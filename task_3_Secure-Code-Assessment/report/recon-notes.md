# Recon Notes — Vulpy (bad/)

## Flagged in vulpy.py
- [ ] SECRET_KEY hardcoded as 'aaaaaaa'
- [ ] debug=True in app.run()
- [ ] extra_files='csp.txt' in debug mode


### Finding 1: Hardcoded SECRET_KEY
- Location: vulpy.py, `app.config['SECRET_KEY'] = 'aaaaaaa'`
- Mechanism: Flask signs (not encrypts) session cookies with this key. A known/weak
  key lets an attacker forge arbitrary session content (e.g. set is_admin=True)
  and sign it correctly themselves — bypassing login entirely.
- Vulnerability type: Session/Cookie Forgery
- OWASP 2025: A07 Authentication Failures
- CWE: CWE-798 (Use of Hard-coded Credentials) / CWE-347 (Improper Verification of Cryptographic Signature)
- Severity: Critical (full auth bypass if session contains privilege flags — confirm once we read mod_user.py/libuser.py)


### Finding 2: debug=True in production entrypoint
- Location: vulpy.py, app.run(debug=True, ...)
- Mechanism: Debug mode leaks full stack traces (source, local vars, paths) on error,
  and exposes the Werkzeug interactive debugger — a known path to RCE via PIN bypass
  techniques if reachable.
- Vulnerability type: Security Misconfiguration (Debug Mode Enabled)
- OWASP 2025: A02 Security Misconfiguration
- CWE: CWE-215, CWE-489
- Severity: Critical (RCE potential if externally reachable)

### Finding 3: extra_files='csp.txt' alongside debug mode
- Location: vulpy.py, app.run(..., extra_files='csp.txt')
- Mechanism: Dev-only auto-reload convenience hardcoded into entrypoint — no
  environment-based config separation between dev and prod.
- Vulnerability type: Insecure Design (Config Management)
- OWASP 2025: A06 Insecure Design
- CWE: CWE-1188
- Severity: Low (supporting evidence for Finding 2)


### Finding 4: SQL Injection in login/create/password_change
- Location: libuser.py — login(), create(), password_change() all build SQL via
  string formatting (.format()/%), user input concatenated directly into query.
- Mechanism (login): payload username=' OR '1'='1' -- makes WHERE always-true;
  fetchone() returns first row in table; do_login() logs attacker in as that
  user with no valid password. Full auth bypass, not data dump (fetchone limits
  to 1 row — UNION injection would be needed for data exfil).
- Vulnerability type: SQL Injection
- OWASP 2025: A05 Injection
- CWE: CWE-89
- Severity: Critical

### Finding 5: Plaintext password storage
- Location: libuser.py — create() and password_change(), password written to
  DB with no hashing applied.
- Mechanism: Any DB compromise (including via Finding 4) exposes every user's
  real password directly, no cracking needed.
- Vulnerability type: Cryptographic Failure (Plaintext Storage)
- OWASP 2025: A04 Cryptographic Failures
- CWE: CWE-256
- Severity: High


### Finding 6: Unsigned session cookie (trivial forgery)
- Location: libsession.py — create() uses base64.b64encode(json.dumps(...)) with
  no HMAC/signature; load() just base64-decodes with no verification.
- Mechanism: Base64 is encoding, not cryptographic protection. Anyone can forge a
  session for any username with a one-line script, no secret/key required at all.
  This is separate from and worse than the SECRET_KEY issue (Finding 1) — Flask's
  signed-session mechanism isn't even in use here for auth state.
- Vulnerability type: Missing Integrity Check on Session Token
- OWASP 2025: A08 Software/Data Integrity Failures
- CWE: CWE-353 (Missing Support for Integrity Check)
- Severity: Critical


### Finding 7: No brute-force/rate-limiting protection on login or OTP
- Location: libuser.py + libmfa.py — 'failures' column exists in schema
  (set to 0 on user creation) but is never read or incremented anywhere in
  the codebase. mfa_validate() has no attempt counter or lockout either.
- Mechanism: Unlimited password and OTP guesses permitted — no delay, no
  lockout, no CAPTCHA. Makes SQLi (Finding 4) and MFA brute-forcing both
  easier with no defensive friction.
- Vulnerability type: Missing Brute-Force Protection
- OWASP 2025: A07 Authentication Failures
- CWE: CWE-307
- Severity: High

### Observation (not a finding): Inconsistent SQL query practices
- libmfa.py uses parameterized queries (?) correctly throughout.
- libuser.py uses string formatting for the same kind of queries.
- Shows the vulnerable patterns are localized, not systemic — useful context
  for the report's "root cause" narrative.


### Correction: MFA enrollment is NOT broken
- mfa_reset_secret() in mod_mfa.py's do_mfa_view() (GET) properly generates a
  real secret via pyotp.random_base32() before QR/enrollment is shown. The
  earlier hypothesis (empty secret) is refuted after checking mod_mfa.py.

### Finding 8: CSRF on /mfa/disable via unprotected GET
- Location: mod_mfa.py, do_mfa_disable() — state-changing action (disables MFA)
  on a GET route, no CSRF token, no confirmation step.
- Mechanism: Victim loading any attacker-controlled link/image pointing at
  /mfa/disable while authenticated silently disables their MFA.
- Vulnerability type: CSRF
- OWASP 2025: A01 Broken Access Control
- CWE: CWE-352
- Severity: High


### Finding 9: Weak randomness for API key generation
- Location: libapi.py, keygen() — hashlib.sha256(str(random.getrandbits(2048))...)
- Mechanism: random module uses Mersenne Twister, a predictable non-cryptographic
  PRNG. Wrapping weak-entropy input in SHA-256 does not add entropy back.
  Python's `secrets` module exists specifically for security tokens.
- Vulnerability type: Insufficient Randomness
- OWASP 2025: A04 Cryptographic Failures
- CWE: CWE-330
- Severity: Medium

### Finding 10: API keys stored as world-readable filenames in /tmp, no expiry
- Location: libapi.py, keygen()/authenticate() — key embedded directly in
  filename under /tmp/, e.g. vulpy.apikey.<username>.<key>
- Mechanism: /tmp is world-readable by default on most Linux systems. The
  secret itself is the filename, not file content — `ls /tmp/` alone leaks
  every valid username+key pair with no read permission needed. No expiration
  or revocation mechanism beyond overwrite-on-next-keygen for that same user.
- Vulnerability type: Insecure Storage of Sensitive Data / Missing Expiration
- OWASP 2025: A04 Cryptographic Failures
- CWE: CWE-377, CWE-522 (Insufficiently Protected Credentials)
- Severity: High


### Verified (not vulnerable): keygen() password=None default
- Location: libapi.py, keygen(username, password=None)
- The only caller (mod_api.py do_key_create) enforces a JSON schema requiring
  both username and password before keygen() is invoked, so the unauthenticated
  branch is unreachable via the current API surface. Dead defensive code, not
  a live vulnerability — noted as a latent risk if reused elsewhere later.

### Finding 11: Unauthenticated post listing (Broken Access Control)
- Location: mod_api.py, do_post_list() — GET /api/post/<username>
- Mechanism: No session/API-key check at all. Any unauthenticated party can
  enumerate and read any user's posts by username, directly from the URL.
- Vulnerability type: Broken Access Control / IDOR
- OWASP 2025: A01 Broken Access Control
- CWE: CWE-862 (Missing Authorization)
- Severity: High

### Finding 12: Identity spoofing via JSON body override
- Location: mod_api.py, do_post_create() — POST /api/post
- Mechanism: data = {'username': authenticate(request)} sets the correct
  authenticated identity, but data.update(request.get_json()) merges the
  raw request body on top of it. An attacker with a valid API key for their
  own account can include "username":"victim" in the POST body and post
  content as another user entirely. post_schema doesn't forbid extra fields,
  so this passes validation.
- Vulnerability type: Improper Authorization / Parameter Pollution
- OWASP 2025: A01 Broken Access Control
- CWE: CWE-863 (Incorrect Authorization)
- Severity: Critical

