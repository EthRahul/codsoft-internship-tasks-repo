#!/usr/bin/env python3
"""
Task 1: Network Packet Analyzer
--------------------------------
Main entry point for running live packet capture and analysis.
Created for CodSoft Cybersecurity Internship.

Usage:
    sudo python3 main.py [-i INTERFACE] [-c COUNT] [-f FILTER]
"""

import argparse
import sys
from colorama import Fore, Style, init

from analyzer import PacketAnalyzer, check_privileges

# Initialize Colorama
init(autoreset=True)


def print_banner() -> None:
    """Prints styled header banner for the CLI tool."""
    banner = fr'''
{Fore.CYAN}{Style.BRIGHT}========================================================================
   __  __ _____ _______        _____  _____  _  ________ _____ 
  |  \/  |  ___|  __ \ \      / / _ \|  __ \| |/ /  ____|  __ \ 
  | \  / | |__ | |__) \ \    / / | | | |__) | ' /| |__  | |__) |
  | |\/| |  __||  _  / \ \  / /| | | |  _  /|  < |  __| |  _  / 
  | |  | | |___| | \ \  \ \/ / | |_| | | \ \| . \| |____| | \ \ 
  |_|  |_|_____|_|  \_\  \__/   \___/|_|  \_\_|\_\______|_|  \_\
                                                               
             CodSoft Cybersecurity Internship - Task 1          
                   NETWORK PACKET ANALYZER TOOL                 
========================================================================{Style.RESET_ALL}
'''
    print(banner)


def main() -> None:
    """Parses command-line arguments and launches the packet analyzer."""
    # Step 1: Configure Argument Parser
    parser = argparse.ArgumentParser(
        description="CodSoft Task 1: Network Packet Analyzer - Capture & inspect live packet traffic.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python3 main.py
  sudo python3 main.py -i eth0 -c 50
  sudo python3 main.py -f "tcp port 80 or tcp port 443"
  sudo python3 main.py -f "icmp" -c 10
        """
    )
    parser.add_argument(
        "-i", "--interface",
        type=str,
        default=None,
        help="Target network interface (e.g. eth0, wlan0, lo). Default: System default."
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=0,
        help="Number of packets to capture before stopping (0 for continuous). Default: 0."
    )
    parser.add_argument(
        "-f", "--filter",
        type=str,
        default=None,
        help="Berkeley Packet Filter (BPF) string (e.g. 'tcp', 'udp', 'icmp', 'port 80')."
    )
    parser.add_argument(
        "--max-payload",
        type=int,
        default=64,
        help="Maximum payload snippet length in bytes to display. Default: 64."
    )

    args = parser.parse_args()

    # Step 2: Print Banner
    print_banner()

    # Step 3: Check for root/administrator privileges
    is_admin = check_privileges()
    if not is_admin:
        print(f"{Fore.YELLOW}{Style.BRIGHT}[!] WARNING: ELEVATED PRIVILEGES RECOMMENDED{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Network packet sniffing on raw sockets generally requires root/administrator rights.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}If packet sniffing fails or no packets are captured, please execute with:{Style.RESET_ALL}")
        print(f"\n    {Fore.GREEN}{Style.BRIGHT}sudo python3 main.py{Style.RESET_ALL}\n")
        
        try:
            response = input(f"{Fore.CYAN}Do you wish to proceed anyway? (y/N): {Style.RESET_ALL}").strip().lower()
            if response != 'y':
                print(f"{Fore.RED}[*] Exiting. Re-run with sudo privileges.{Style.RESET_ALL}")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.RED}[*] Exiting.{Style.RESET_ALL}")
            sys.exit(0)

    # Step 4: Instantiate and run packet analyzer
    analyzer = PacketAnalyzer(max_payload_len=args.max_payload)
    analyzer.start_sniffing(
        interface=args.interface,
        count=args.count,
        bpf_filter=args.filter
    )


if __name__ == "__main__":
    main()
