# Cybersecurity Internship Repository - CodSoft

Welcome to my **CodSoft Cybersecurity Internship** project repository! This repository contains cybersecurity tools and practical tasks developed during the internship program. Each task demonstrates core security concepts — from network packet inspection to intrusion detection and secure code assessment.

---

## 📁 Repository Structure

    codsoft-internship-tasks-repo/
    │
    ├── README.md                                    # Main repository documentation
    ├── task_1_packet_analyzer/                      # Task 1: Network Packet Analyzer
    │   ├── analyzer.py                               # Packet capture, parsing & colorizing logic
    │   ├── main.py                                   # CLI entry point & privilege verification
    │   ├── requirements.txt                          # Python dependencies (scapy, colorama)
    │   └── README.md                                 # Detailed task documentation & usage guide
    ├── task_2_Network-Intrusion-Detection-System/    # Task 2: Network Intrusion Detection System
    │   ├── README.md                                 # Detailed task documentation & usage guide
    │   ├── rules/local.rules                         # Custom Suricata detection rule
    │   ├── scripts/alert_responder.sh                # Automated alert response script
    │   └── images/                                   # Setup, attack, and dashboard screenshots
    └── task_3_Secure-Code-Assessment/                # Task 3: Secure Code Assessment
        ├── README.md                                 # Detailed task documentation & usage guide
        ├── report/                                   # Findings report & recon notes
        ├── scans/                                    # Raw Bandit scan output
        ├── fixes/                                    # Remediated code for critical findings
        └── images/                                   # Scan proof screenshots

---

## 🛠️ Tasks Overview

| Task #     | Project Name                                                                                                                                                  | Description                                                                                                                                                                                             | Tech Stack                                 | Status      |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | ----------- |
| **Task 1** | [Network Packet Analyzer](https://github.com/EthRahul/codsoft-internship-tasks-repo/blob/main/task_1_packet_analyzer/README.md)                               | Captures live network traffic, extracts packet headers (IP, Protocol, Ports, Payload), and color-codes output.                                                                                          | `Python 3`, `Scapy`, `Colorama`            | ✅ Completed |
| **Task 2** | [Network Intrusion Detection System](https://github.com/EthRahul/codsoft-internship-tasks-repo/blob/main/task_2_Network-Intrusion-Detection-System/README.md) | Configures Suricata as a NIDS on an isolated VirtualBox lab network, with a custom SSH brute-force detection rule, live traffic monitoring, automated alert response, and a graphical EveBox dashboard. | `Suricata`, `Bash`, `EveBox`, `VirtualBox` | ✅ Completed |
| **Task 3** | [Secure Code Assessment](https://github.com/EthRahul/codsoft-internship-tasks-repo/blob/main/task_3_Secure-Code-Assessment/README.md)                        | Manual + automated (Bandit) security audit of a Flask web app, mapped to OWASP Top 10 (2025). 12 vulnerabilities identified across auth, sessions, and API layers; 4 critical findings remediated and verified. | `Python 3`, `Flask`, `Bandit`, `itsdangerous` | ✅ Completed |

---

## 🚀 Quick Start & Installation

### Prerequisites

- **Python 3.8+** installed (for Tasks 1 and 3)
- Administrative / `sudo` privileges (required for raw socket sniffing and Suricata)
- Linux / macOS / Windows with Npcap (if using Windows)
- **VirtualBox** and a Suricata install (for Task 2)

### 1. Clone the Repository

git clone https://github.com/EthRahul/codsoft-internship-tasks-repo.git
cd codsoft-internship-tasks-repo


### 2. Set Up Virtual Environment (Recommended, for Tasks 1 and 3)
Create virtual environment

python3 -m venv venv

Activate on Linux/macOS

source venv/bin/activate

Activate on Windows (CMD)
venv\Scripts\activate.bat

### 3. Install Dependencies for Task 1

cd task_1_packet_analyzer
pip install -r requirements.txt


### 4. Run Task 1 (Network Packet Analyzer)
> **Note:** Raw socket packet capture requires elevated privileges (`sudo` on Linux/macOS or Administrator prompt on Windows).
Run with default settings (captures packets across default interface)

sudo python3 main.py

Or run with optional arguments (e.g., capture 20 packets on specific interface)

sudo python3 main.py -i eth0 -c 20 -f "tcp"


### 5. Run Task 2 (Network Intrusion Detection System)
> **Note:** Requires an isolated lab (VirtualBox host-only network + a target VM) and Suricata installed. Full lab setup steps are in the [task README](https://github.com/EthRahul/codsoft-internship-tasks-repo/blob/main/task_2_Network-Intrusion-Detection-System/README.md).

cd task_2_Network-Intrusion-Detection-System

Start the IDS, pointed at your lab interface

sudo suricata -c /etc/suricata/suricata.yaml -i <your-interface>

In another terminal, run the automated alert responder

./scripts/alert_responder.sh

View alerts in a browser dashboard

evebox oneshot /var/log/suricata/eve.json

then open http://127.0.0.1:5636

### 6. Run Task 3 (Secure Code Assessment)
> **Note:** This task audits Vulpy, an intentionally vulnerable Flask app (not included in this repo). Clone it separately per the [task README](https://github.com/EthRahul/codsoft-internship-tasks-repo/blob/main/task_3_Secure-Code-Assessment/README.md) to reproduce the full scan.

cd task_3_Secure-Code-Assessment

Re-run static analysis on the remediated code

bandit -r fixes/ -f txt


---

## ⚖️ Legal & Ethical Disclaimer

This software is developed strictly for **educational and defensive cybersecurity research purposes** in accordance with internship training guidelines.

- Network packet sniffing, intrusion detection testing, and code security assessments must **only** be conducted on networks, devices, and codebases that you own or have explicit, written permission to test.
- Unauthorized packet capture, attack simulation, or code auditing on third-party systems may violate local, national, or international computer crime laws (such as the CFAA, Computer Misuse Act, or GDPR).
- The author assumes no liability for misuse or damage caused by this repository's tools.

---

## 🧑‍💻 Author

- **Internship Program:** CodSoft Cybersecurity Internship
- **Repository Maintainer:** Rahul Sunouri ([@EthRahul](https://github.com/EthRahul))
