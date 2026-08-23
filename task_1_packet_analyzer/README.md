# Task 1: Network Packet Analyzer

A powerful, light-weight Python-based **Network Packet Analyzer** developed for the **CodSoft Cybersecurity Internship**. This tool captures live network traffic, extracts essential header information and data payloads, and displays color-coded console logs for efficient network analysis and packet inspection.

---

## 🎯 Objectives & Specifications

- **Live Traffic Capture:** Capture network packets on specified or default network interfaces using `Scapy`.
- **Header Field Extraction:**
  - Source IP Address & Port
  - Destination IP Address & Port
  - Protocol Type (TCP, UDP, ICMP, ARP, etc.)
  - Packet Length (bytes) & Timestamp
- **Payload Inspection:** Safely extracts raw packet payload snippets and decodes printable ASCII characters.
- **Color-Coded Console Output:** Built with `Colorama` to provide distinct color highlights:
  - 🔴 **TCP Traffic:** Red
  - 🟢 **UDP Traffic:** Green
  - 🟡 **ICMP Traffic:** Yellow
  - 🟣 **ARP Traffic:** Magenta
  - 🔵 **Other/System:** Cyan / Blue
- **Traffic Summary:** Generates a breakdown of protocol statistics upon capture termination.

---

## 📦 Requirements & Dependencies

- **Python:** `Python 3.8+`
- **Privileges:** Administrative/`sudo` access (required for socket network capture)
- **Python Packages:**
  - `scapy >= 2.5.0`
  - `colorama >= 0.4.6`

Install all required packages via `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run

### 1. Basic Sniffing (Default Interface)
Run the packet analyzer with default settings. Press `Ctrl+C` to stop capturing and view the summary.

```bash
sudo python3 main.py
```

### 2. Capture a Specific Number of Packets
Limit packet capture to a set number of packets (e.g., 20 packets):

```bash
sudo python3 main.py -c 20
```

### 3. Filter Traffic using BPF (Berkeley Packet Filter)
Sniff only specific protocols or ports using filters:

```bash
# Capture only TCP traffic
sudo python3 main.py -f "tcp"

# Capture HTTP/HTTPS traffic
sudo python3 main.py -f "tcp port 80 or tcp port 443"

# Capture ICMP (Ping) packets
sudo python3 main.py -f "icmp"
```

### 4. Specify Target Interface
List and select a specific network interface (e.g., `eth0`, `wlan0`, `lo`):

```bash
sudo python3 main.py -i eth0 -f "udp"
```

---

## ⚙️ Command-Line Arguments Reference

| Option | Short | Type | Default | Description |
| :--- | :---: | :---: | :---: | :--- |
| `--interface` | `-i` | `str` | `None` | Network interface to sniff on (e.g., `eth0`, `wlan0`, `lo`). |
| `--count` | `-c` | `int` | `0` | Number of packets to capture (`0` for continuous capture). |
| `--filter` | `-f` | `str` | `None` | Berkeley Packet Filter (BPF) string (e.g. `'tcp'`, `'port 80'`). |
| `--max-payload` | | `int` | `64` | Maximum payload snippet byte length to format and display. |

---

## 🖥️ Sample Console Output

```text
========================================================================
             CodSoft Cybersecurity Internship - Task 1          
                   NETWORK PACKET ANALYZER TOOL                 
========================================================================

[+] Starting Network Packet Sniffer...
    Interface: Default System Interface
    BPF Filter: None
    Packet Count Target: Continuous (Ctrl+C to stop)
    Press Ctrl+C to halt capture at any time.

──────────────────────────────────────────────────────────────────────────────
[#0001] [11:42:01.204] Protocol: TCP    Length: 74 B
  Source: 192.168.1.45:54322  ➜  Destination: 142.250.190.46:443  
  Payload Snippet: ".....G..@...k....p...#" (32 bytes)
──────────────────────────────────────────────────────────────────────────────
[#0002] [11:42:01.215] Protocol: UDP    Length: 68 B
  Source: 192.168.1.1:53     ➜  Destination: 192.168.1.45:53211 
  Payload Snippet: "...g...google.com..." (26 bytes)
──────────────────────────────────────────────────────────────────────────────
[#0003] [11:42:02.001] Protocol: ICMP   Length: 98 B
  Source: 192.168.1.45       ➜  Destination: 8.8.8.8           
  Payload Snippet: "!"#$%&'()*+,-./01234567" (56 bytes)

========================================
       TRAFFIC CAPTURE SUMMARY       
========================================
Total Packets Captured: 3
----------------------------------------
  TCP     :     1 packets ( 33.3%)
  UDP     :     1 packets ( 33.3%)
  ICMP    :     1 packets ( 33.3%)
  ARP     :     0 packets (  0.0%)
  OTHER   :     0 packets (  0.0%)
========================================
```

---

## 📂 Code Architecture

- **`analyzer.py`**:
  - `check_privileges()`: Verifies root/admin runtime environment.
  - `PacketAnalyzer`: Core logic class containing Scapy callback (`process_packet`), payload extractor (`extract_payload`), color mapping (`COLOR_MAP`), and summary visualizer (`display_summary`).
- **`main.py`**:
  - Entry point handling CLI argument parsing (`argparse`), privilege verification alerts, ASCII banner rendering, and starting the analyzer daemon.

---

## ⚠️ Ethical & Educational Disclaimer

This packet analyzer is created exclusively for **educational, defensive cybersecurity, and software testing purposes** as part of the CodSoft internship curriculum. 

1. **Consent Required:** Always ensure you have explicit authorization from the network owner before monitoring or analyzing network traffic.
2. **Privacy Notice:** Intercepting sensitive packet data without consent is illegal under cyber law frameworks worldwide.
