# Cybersecurity Internship Repository - CodSoft

Welcome to my **CodSoft Cybersecurity Internship** project repository! This repository contains Python-based cybersecurity tools and practical tasks developed during the internship program. Each task demonstrates core security concepts, network analysis, packet inspection, and secure coding practices.

---

## 📁 Repository Structure

```text
codsoft-internship-tasks-repo/
│
├── README.md                           # Main repository documentation
└── task_1_packet_analyzer/             # Task 1: Network Packet Analyzer
    ├── analyzer.py                     # Packet capture, parsing & colorizing logic
    ├── main.py                         # CLI entry point & privilege verification
    ├── requirements.txt                # Python dependencies (scapy, colorama)
    └── README.md                       # Detailed task documentation & usage guide
```

---

## 🛠️ Tasks Overview

| Task # | Project Name | Description | Tech Stack | Status |
| :---: | :--- | :--- | :--- | :---: |
| **Task 1** | [Network Packet Analyzer](./task_1_packet_analyzer/README.md) | Captures live network traffic, extracts packet headers (IP, Protocol, Ports, Payload), and color-codes output. | `Python 3`, `Scapy`, `Colorama` | ✅ Completed |

---

## 🚀 Quick Start & Installation

### Prerequisites
- **Python 3.8+** installed
- Administrative / `sudo` privileges (required for raw socket network sniffing)
- Linux / macOS / Windows with Npcap (if using Windows)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/codsoft-internship-tasks-repo.git
cd codsoft-internship-tasks-repo
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows (CMD)
# venv\Scripts\activate.bat
```

### 3. Install Dependencies for Task 1
```bash
cd task_1_packet_analyzer
pip install -r requirements.txt
```

### 4. Run Task 1 (Network Packet Analyzer)
> **Note:** Raw socket packet capture requires elevated privileges (`sudo` on Linux/macOS or Administrator prompt on Windows).

```bash
# Run with default settings (captures packets across default interface)
sudo python3 main.py

# Or run with optional arguments (e.g., capture 20 packets on specific interface)
sudo python3 main.py -i eth0 -c 20 -f "tcp"
```

---

## ⚖️ Legal & Ethical Disclaimer

This software is developed strictly for **educational and defensive cybersecurity research purposes** in accordance with internship training guidelines. 
- Network packet sniffing must **only** be conducted on networks and devices that you own or have explicit, written permission to monitor.
- Unauthorized packet capture on third-party networks may violate local, national, or international computer crime laws (such as the CFAA, Computer Misuse Act, or GDPR).
- The author assumes no liability for misuse or damage caused by this utility.

---

## 🧑‍💻 Author
- **Internship Program:** CodSoft Cybersecurity Internship
- **Repository Maintainer:** Cybersecurity Intern
