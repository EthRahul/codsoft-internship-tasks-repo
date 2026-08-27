# Secure Code Assessment Report — Vulpy (Flask Web Application)

**Assessed by:** Rahul Sunouri
**Target:** Vulpy (`bad/` variant) — https://github.com/fportantier/vulpy
**Date:** August 2026
**Scope:** Manual source code review + automated static analysis (Bandit)

---

## 1. Executive Summary

This assessment identified **12 confirmed vulnerabilities** in Vulpy's `bad/` codebase, spanning authentication, session management, multi-factor authentication, and the REST API layer. Of these, **4 are rated Critical**, **5 High**, **2 Medium**, and **1 Low**.

The most severe issues allow complete authentication bypass through SQL injection, trivial session forgery with no cryptographic protection, and cross-account content spoofing via the API. Combined, these findings mean an unauthenticated attacker can access any account, read or write data as any user, and in some configurations achieve remote code execution via Flask's exposed debug mode.

The codebase shows inconsistent security maturity — some modules (`libmfa.py`, `libposts.py`) use safe parameterized SQL queries correctly, while others (`libuser.py`) construct queries via unsafe string formatting. This indicates the vulnerabilities are addressable without a full rewrite; the safe pattern already exists elsewhere in the same codebase.

## 2. Scope & Methodology

**Files manually reviewed:** `vulpy.py`, `mod_user.py`, `libuser.py`, `libsession.py`, `libmfa.py`, `mod_mfa.py`, `libapi.py`, `mod_api.py`, `libposts.py`

**Files covered only via automated scan (not manually reviewed line-by-line):** `db.py`, `db_init.py`, `mod_posts.py`, `mod_csp.py`, `mod_hello.py`, `brute.py`, `vulpy-ssl.py`, `templates/` — flagged as **Further Work** in Section 5.

**Methodology:**
1. Manual attack-surface mapping from the application entry point (`vulpy.py`) outward through each Flask blueprint.
2. Manual code review of authentication, session, and authorization logic, tracing each request path end-to-end rather than reviewing files in isolation.
3. Automated static analysis via **Bandit v1.9.4** across the full `bad/` directory, cross-referenced against manual findings for validation.
4. Severity ratings reflect **exploit impact and reachability**, determined through manual analysis — not raw tool output. Bandit's default severity (e.g. rating the hardcoded `SECRET_KEY` as "Low") was overridden where contextual impact analysis justified a different rating, and is noted explicitly where this occurs.

## 3. Findings Summary

| ID | Finding | OWASP 2025 | CWE | Severity |
|----|---------|------------|-----|----------|
| F04 | SQL Injection in login/create/password_change | A05 Injection | CWE-89 | **Critical** |
| F06 | Unsigned session cookie (trivial forgery) | A08 Software/Data Integrity Failures | CWE-353 | **Critical** |
| F12 | Identity spoofing via JSON body override | A01 Broken Access Control | CWE-863 | **Critical** |
| F02 | Flask debug mode enabled | A02 Security Misconfiguration | CWE-215, CWE-489 | **Critical** |
| F05 | Plaintext password storage | A04 Cryptographic Failures | CWE-256 | High |
| F07 | No brute-force/rate-limiting protection | A07 Authentication Failures | CWE-307 | High |
| F08 | CSRF on /mfa/disable via unprotected GET | A01 Broken Access Control | CWE-352 | High |
| F10 | API keys stored insecurely, no expiry | A04 Cryptographic Failures | CWE-377, CWE-522 | High |
| F11 | Unauthenticated post listing (IDOR) | A01 Broken Access Control | CWE-862 | High |
| F01 | Hardcoded SECRET_KEY | A07 Authentication Failures | CWE-798, CWE-347 | Medium |
| F09 | Weak randomness for API key generation | A04 Cryptographic Failures | CWE-330 | Medium |
| F03 | Dev config shipped in entrypoint | A06 Insecure Design | CWE-1188 | Low |

## 4. Detailed Findings

### F04 — SQL Injection (Critical)
**Location:** `libuser.py` — `login()`, `create()`, `password_change()`
**Description:** All three functions build SQL queries via Python string formatting with unsanitized user input directly interpolated.
**Impact:** Submitting `' OR '1'='1' --` as the username with any password bypasses authentication entirely. The query's `WHERE` clause becomes always-true; `fetchone()` returns the first row in the table (often the earliest-created/admin account), and the application logs the attacker in as that user with no valid password ever checked.
**Remediation:** Replace all string-formatted queries with parameterized queries using `?` placeholders — the pattern already used correctly in `libmfa.py` and `libposts.py` in this same codebase.

### F06 — Unsigned Session Cookie (Critical)
**Location:** `libsession.py` — `create()`, `load()`
**Description:** Sessions are implemented as `base64.b64encode(json.dumps(...))` with no HMAC or signature of any kind. Base64 is encoding, not cryptographic protection — it is trivially reversible and forgeable with no secret knowledge required.
**Impact:** Anyone can construct a valid-looking session (e.g. `{"username": "admin"}`), base64-encode it, and set it as their `vulpy_session` cookie to be treated as a fully authenticated session — no login, password, or key required.
**Remediation:** Use Flask's built-in signed session (`itsdangerous`, tied to a properly randomized `SECRET_KEY`), or explicitly HMAC-sign the cookie payload and verify the signature before trusting any field in `load()`.

### F12 — Identity Spoofing via JSON Body Override (Critical)
**Location:** `mod_api.py` — `do_post_create()`
**Description:** The authenticated username is set first (`data = {'username': libapi.authenticate(request)}`), but `data.update(request.get_json())` then merges the raw, attacker-controlled request body on top of it, silently overwriting the authenticated identity if the body includes a `username` field.
**Impact:** A valid API key for account A can be used to create posts under any arbitrary username B, since `post_schema` does not forbid extra fields.
**Remediation:** Never merge trusted and untrusted dictionaries in a way that lets the untrusted one win. Set `data['username']` **after** merging the request body, or strip `username` from the incoming JSON before merging.

### F02 — Flask Debug Mode Enabled (Critical)
**Location:** `vulpy.py`, `vulpy-ssl.py` — `app.run(debug=True, ...)`
**Description:** Debug mode exposes full stack traces (source code, local variables, file paths) on any unhandled exception, and activates the Werkzeug interactive debugger, which allows arbitrary Python code execution and is protected only by a PIN with documented bypass techniques.
**Impact:** If reachable from outside localhost, this is a direct path to remote code execution.
**Remediation:** Never set `debug=True` outside local development. Use environment-variable-driven configuration (e.g. `debug=os.environ.get('FLASK_DEBUG') == '1'`) so production deployments default to `False`.

### F05 — Plaintext Password Storage (High)
**Location:** `libuser.py` — `create()`, `password_change()`
**Description:** Passwords are written to the database exactly as submitted, with no hashing algorithm applied.
**Impact:** Any database compromise (including via F04) immediately exposes every user's real password in cleartext — a risk that extends to any other service where users reuse that password.
**Remediation:** Hash passwords with a modern algorithm (bcrypt, argon2, or scrypt) before storage; never store or compare plaintext passwords.

### F07 — No Brute-Force Protection (High)
**Location:** `libuser.py`, `libmfa.py`
**Description:** The `users` table includes a `failures` column, initialized to 0, but it is never read or incremented anywhere in the codebase. There is no attempt counter or lockout on password or OTP validation.
**Impact:** Unlimited guesses are permitted against both passwords and 6-digit OTP codes, with no delay, lockout, or CAPTCHA.
**Remediation:** Increment `failures` on each failed attempt, lock the account or add exponential backoff after a threshold, and reset on success.

### F08 — CSRF on MFA Disable (High)
**Location:** `mod_mfa.py` — `do_mfa_disable()`
**Description:** MFA is disabled via a GET request with no CSRF token and no confirmation step.
**Impact:** An attacker can disable a victim's MFA simply by getting them to load a link or image pointing at `/mfa/disable` while authenticated — no interaction beyond a page load is required.
**Remediation:** Require CSRF tokens (e.g. Flask-WTF) on all state-changing routes, and never perform state changes on GET requests.

### F10 — Insecure API Key Storage (High)
**Location:** `libapi.py` — `keygen()`, `authenticate()`
**Description:** API keys are embedded directly in filenames under `/tmp/` (e.g. `vulpy.apikey.<username>.<key>`), which is world-readable by default on most Linux systems. Keys never expire.
**Impact:** Any local user can enumerate all valid username/key pairs with a simple `ls /tmp/`, no file-read permission needed since the secret is the filename itself.
**Remediation:** Store API keys hashed in the database (not the filesystem), associate an expiration timestamp, and provide a revocation mechanism.

### F11 — Unauthenticated Post Listing / IDOR (High)
**Location:** `mod_api.py` — `do_post_list()`
**Description:** `GET /api/post/<username>` performs no authentication or authorization check before returning that user's posts.
**Impact:** Any unauthenticated party can enumerate and read any user's posts by guessing or iterating usernames.
**Remediation:** Require authentication on this route, and verify the requester is authorized to view the requested user's posts (or make the endpoint explicitly public-by-design if that is intended, with that decision documented).

### F01 — Hardcoded SECRET_KEY (Medium — corrected from initial Critical rating)
**Location:** `vulpy.py`, `vulpy-ssl.py` — `app.config['SECRET_KEY'] = 'aaaaaaa'`
**Description:** The Flask signing key is hardcoded to a trivial, guessable value.
**Impact:** Currently, this key only protects Flask's built-in session (used here solely for `flash()` messages) — the application's actual authentication state is carried by the separate, unsigned cookie in F06. Real-world impact today is limited to flash-message tampering. However, this is still a critical latent risk: if the app later adopts Flask's native session for auth, or Flask-WTF's CSRF protection (which also relies on `SECRET_KEY`), this hardcoded key becomes immediately exploitable for full session forgery or CSRF bypass.
**Remediation:** Generate a cryptographically random key (`secrets.token_hex(32)`) and load it from an environment variable, never hardcoded in source.

### F09 — Weak Randomness for API Keys (Medium)
**Location:** `libapi.py` — `keygen()`
**Description:** API keys are derived from `random.getrandbits(2048)`, then hashed with SHA-256. `random` uses a non-cryptographic PRNG (Mersenne Twister); hashing weak-entropy input does not restore security.
**Impact:** Under specific conditions, predictable PRNG state could make key generation more guessable than intended.
**Remediation:** Use Python's `secrets` module (`secrets.token_hex()`), which is designed for security-sensitive token generation.

### F03 — Dev Configuration Shipped in Entrypoint (Low)
**Location:** `vulpy.py` — `extra_files='csp.txt'` alongside `debug=True`
**Description:** Development-only convenience configuration (auto-reload watching) is hardcoded directly into the application entrypoint, with no environment-based separation between development and production settings.
**Impact:** Supporting evidence that this codebase has no dev/prod configuration boundary at all — reinforces the severity of F02.
**Remediation:** Introduce environment-based configuration (e.g. `.env` + `python-dotenv`, or Flask's config classes) so debug/dev settings never ship by default.

## 5. Further Work (Out of Scope for This Assessment)

The following files were flagged by automated scanning but not manually reviewed line-by-line in this assessment round: `db.py`, `db_init.py` (both show the same SQL string-formatting pattern as F04 per Bandit), `mod_posts.py`, `mod_csp.py`, `mod_hello.py`, `brute.py` (a companion brute-force script, ironically unrelated to app defenses), `vulpy-ssl.py` (confirmed via Bandit to duplicate F01 and F02), and the `templates/` directory (not yet checked for unescaped Jinja2 output / XSS). A follow-up review pass is recommended before considering this assessment fully exhaustive.

## 6. Remediation Priority Roadmap

1. **Immediate:** Fix F04 (SQLi) and F06 (unsigned sessions) — these two alone account for full authentication bypass.
2. **Immediate:** Disable F02 (debug mode) before any deployment beyond local development.
3. **Short-term:** F12 (identity spoofing), F11 (IDOR), F05 (plaintext passwords), F08 (CSRF), F10 (API key storage).
4. **Short-term:** F07 (brute-force protection) — straightforward to add given the `failures` column already exists in schema.
5. **Housekeeping:** F01, F09, F03 — lower immediate impact but should be fixed as part of the same remediation pass since they share root causes with items above.

## 7. Conclusion

Vulpy's `bad/` variant demonstrates a broad, realistic cross-section of web application security failures concentrated in authentication and authorization logic. Critically, the vulnerabilities are not uniform across the codebase — modules that use parameterized SQL and proper session logic exist alongside modules that don't, suggesting the fixes are a matter of applying existing safe patterns consistently rather than a full architectural rewrite.
