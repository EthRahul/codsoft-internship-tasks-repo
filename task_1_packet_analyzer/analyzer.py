"""
Packet Analyzer Module
----------------------
Handles live network packet capturing, layer extraction, payload parsing,
color-coded formatting, and packet analysis statistics using Scapy and Colorama.
"""

import os
import sys
import datetime
from typing import Optional, Dict, Tuple

from colorama import Fore, Style, init
from scapy.all import sniff, IP, IPv6, TCP, UDP, ICMP, ARP, Raw, Packet

# Initialize Colorama for auto-reset after each print statement
init(autoreset=True)


def check_privileges() -> bool:
    """
    Verifies if the script is executing with administrator/root privileges required for raw socket access.
    
    Returns:
        bool: True if executing as root/admin, False otherwise.
    """
    if os.name == 'posix':
        return os.geteuid() == 0
    elif os.name == 'nt':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return False


class PacketAnalyzer:
    """
    Monitors live network traffic, extracts packet headers and payloads,
    and displays color-coded logs on the terminal.
    """

    # Protocol Color Mapping
    # TCP -> RED (as per requirements), UDP -> GREEN, ICMP -> YELLOW, ARP -> MAGENTA
    COLOR_MAP = {
        "TCP": Fore.RED + Style.BRIGHT,
        "UDP": Fore.GREEN + Style.BRIGHT,
        "ICMP": Fore.YELLOW + Style.BRIGHT,
        "ARP": Fore.MAGENTA + Style.BRIGHT,
        "OTHER": Fore.CYAN + Style.BRIGHT,
    }

    def __init__(self, max_payload_len: int = 64):
        """
        Initializes the PacketAnalyzer.

        Args:
            max_payload_len (int): Maximum bytes of payload snippet to display per packet.
        """
        self.max_payload_len = max_payload_len
        self.packet_count = 0
        self.protocol_stats: Dict[str, int] = {
            "TCP": 0,
            "UDP": 0,
            "ICMP": 0,
            "ARP": 0,
            "OTHER": 0,
        }

    def extract_payload(self, packet: Packet) -> str:
        """
        Safely extracts and formats the packet payload into printable ASCII characters.

        Args:
            packet (Packet): Scapy packet object.

        Returns:
            str: Human-readable payload snippet or length indicator.
        """
        if packet.haslayer(Raw):
            try:
                payload_bytes = packet[Raw].load
                # Extract printable ASCII bytes
                snippet = payload_bytes[:self.max_payload_len]
                printable = "".join(
                    chr(b) if 32 <= b <= 126 else "." for b in snippet
                )
                if len(payload_bytes) > self.max_payload_len:
                    printable += "..."
                return f'"{printable}" ({len(payload_bytes)} bytes)'
            except Exception:
                return "<Error decoding raw payload>"
        return "No Raw Payload"

    def determine_protocol(self, packet: Packet) -> Tuple[str, str]:
        """
        Determines the protocol name and associated color styling.

        Args:
            packet (Packet): Scapy packet object.

        Returns:
            Tuple[str, str]: (Protocol Name, Colorama Style String)
        """
        if packet.haslayer(TCP):
            proto_name = "TCP"
        elif packet.haslayer(UDP):
            proto_name = "UDP"
        elif packet.haslayer(ICMP):
            proto_name = "ICMP"
        elif packet.haslayer(ARP):
            proto_name = "ARP"
        else:
            proto_name = "OTHER"

        color = self.COLOR_MAP.get(proto_name, self.COLOR_MAP["OTHER"])
        return proto_name, color

    def process_packet(self, packet: Packet) -> None:
        """
        Callback function invoked by Scapy for every sniffed packet.
        Parses headers, colorizes details, and outputs packet information.

        Args:
            packet (Packet): Captured network packet.
        """
        self.packet_count += 1
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]

        src_ip = "Unknown"
        dst_ip = "Unknown"
        src_port = ""
        dst_port = ""

        # Extract Network Layer details (IP / IPv6 / ARP)
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
        elif packet.haslayer(IPv6):
            src_ip = packet[IPv6].src
            dst_ip = packet[IPv6].dst
        elif packet.haslayer(ARP):
            src_ip = packet[ARP].psrc
            dst_ip = packet[ARP].pdst

        # Extract Transport Layer ports
        if packet.haslayer(TCP):
            src_port = f":{packet[TCP].sport}"
            dst_port = f":{packet[TCP].dport}"
        elif packet.haslayer(UDP):
            src_port = f":{packet[UDP].sport}"
            dst_port = f":{packet[UDP].dport}"

        proto_name, color = self.determine_protocol(packet)
        self.protocol_stats[proto_name] = self.protocol_stats.get(proto_name, 0) + 1

        payload_snippet = self.extract_payload(packet)
        pkt_len = len(packet)

        # Print color-coded header and details
        divider = Fore.LIGHTBLACK_EX + "─" * 78
        print(divider)
        print(
            f"{Fore.WHITE}[#{self.packet_count:04d}]{Style.RESET_ALL} "
            f"{Fore.BLUE}[{timestamp}]{Style.RESET_ALL} "
            f"Protocol: {color}{proto_name:<6}{Style.RESET_ALL} "
            f"Length: {Fore.CYAN}{pkt_len} B{Style.RESET_ALL}"
        )
        print(
            f"  {Fore.WHITE}Source:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{src_ip}{src_port:<6}{Style.RESET_ALL}  ➜  "
            f"{Fore.WHITE}Destination:{Style.RESET_ALL} {Fore.LIGHTRED_EX}{dst_ip}{dst_port:<6}{Style.RESET_ALL}"
        )
        print(f"  {Fore.WHITE}Payload Snippet:{Style.RESET_ALL} {Fore.LIGHTWHITE_EX}{payload_snippet}{Style.RESET_ALL}")

    def start_sniffing(
        self,
        interface: Optional[str] = None,
        count: int = 0,
        bpf_filter: Optional[str] = None,
    ) -> None:
        """
        Starts the Scapy packet sniffer on the specified interface.

        Args:
            interface (str, optional): Network interface name (e.g. eth0, wlan0).
            count (int): Number of packets to capture before stopping (0 for infinite).
            bpf_filter (str, optional): Berkeley Packet Filter string (e.g., 'tcp', 'udp', 'port 80').
        """
        print(f"\n{Fore.GREEN}{Style.BRIGHT}[+] Starting Network Packet Sniffer...{Style.RESET_ALL}")
        if interface:
            print(f"    {Fore.WHITE}Interface:{Style.RESET_ALL} {Fore.CYAN}{interface}{Style.RESET_ALL}")
        else:
            print(f"    {Fore.WHITE}Interface:{Style.RESET_ALL} {Fore.CYAN}Default System Interface{Style.RESET_ALL}")

        if bpf_filter:
            print(f"    {Fore.WHITE}BPF Filter:{Style.RESET_ALL} {Fore.YELLOW}{bpf_filter}{Style.RESET_ALL}")
        print(f"    {Fore.WHITE}Packet Count Target:{Style.RESET_ALL} {Fore.CYAN}{'Continuous (Ctrl+C to stop)' if count == 0 else count}{Style.RESET_ALL}")
        print(f"    {Fore.LIGHTBLACK_EX}Press Ctrl+C to halt capture at any time.{Style.RESET_ALL}\n")

        try:
            sniff(
                iface=interface,
                count=count,
                filter=bpf_filter,
                prn=self.process_packet,
                store=False,
            )
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Packet capture interrupted by user.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Error during packet sniffing: {e}{Style.RESET_ALL}")
            if "permission" in str(e).lower() or "operation not permitted" in str(e).lower():
                print(f"{Fore.RED}[!] Please ensure you run this script with sudo/administrator privileges.{Style.RESET_ALL}")
        finally:
            self.display_summary()

    def display_summary(self) -> None:
        """
        Displays a summary table of captured traffic upon termination.
        """
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*40}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}       TRAFFIC CAPTURE SUMMARY       {Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*40}{Style.RESET_ALL}")
        print(f"Total Packets Captured: {Fore.WHITE}{Style.BRIGHT}{self.packet_count}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTBLACK_EX}{'-'*40}{Style.RESET_ALL}")

        for proto, count in self.protocol_stats.items():
            color = self.COLOR_MAP.get(proto, self.COLOR_MAP["OTHER"])
            pct = (count / self.packet_count * 100) if self.packet_count > 0 else 0
            print(f"  {color}{proto:<8}{Style.RESET_ALL}: {count:>5} packets ({pct:>5.1f}%)")

        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*40}{Style.RESET_ALL}\n")
