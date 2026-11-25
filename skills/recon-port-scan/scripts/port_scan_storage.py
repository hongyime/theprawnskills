#!/usr/bin/env python3
"""
Port Scan Results Storage Script
Parse nmap XML output and store to database
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Add results-storage to path (StorageAPI was removed; use ResultsDatabase)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase


def get_or_create_subsystem(conn, name):
    """Get subsystem id, creating it if needed. Returns None if name is None."""
    if name is None:
        return None
    conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)", (name,))
    return conn.execute(
        "SELECT id FROM subsystems WHERE name = ?", (name,)).fetchone()[0]


def get_or_create_host(conn, ip, subsystem_id=None, hostname=None,
                       os_fingerprint=None):
    """Get host id, creating it if needed."""
    conn.execute(
        "INSERT OR IGNORE INTO hosts "
        "(subsystem_id, ip_address, hostname, os_fingerprint) "
        "VALUES (?, ?, ?, ?)", (subsystem_id, ip, hostname, os_fingerprint))
    return conn.execute(
        "SELECT id FROM hosts WHERE ip_address = ? "
        "AND (subsystem_id IS ? OR subsystem_id = ?)",
        (ip, subsystem_id, subsystem_id)).fetchone()[0]


def store_port_scan(db, host_result, scan_tool, subsystem=None):
    """Store one host's parsed port rows. Returns number of ports stored."""
    with db.get_connection() as conn:
        subsystem_id = get_or_create_subsystem(conn, subsystem)
        host_id = get_or_create_host(
            conn, host_result["ip"], subsystem_id,
            hostname=host_result.get("hostname"),
            os_fingerprint=host_result.get("os_fingerprint"))
        rows = [
            (host_id, p["port"], p.get("protocol"), p.get("state"),
             p.get("service"), p.get("version"), p.get("product"),
             p.get("extra_info"), scan_tool)
            for p in host_result["ports"]
        ]
        conn.executemany(
            "INSERT OR REPLACE INTO port_scan_results "
            "(host_id, port, protocol, state, service, version, "
            " product, extra_info, scan_tool) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
        conn.commit()
    return len(rows)


def parse_nmap_xml(xml_content):
    """Parse nmap XML output and extract port information."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"[-] Error parsing XML: {e}")
        return []

    results = []

    for host in root.findall(".//host"):
        # Skip hosts that are down
        status = host.find("./status")
        if status is not None and status.get("state") != "up":
            continue

        # Get IP address
        ip_elem = host.find("./address[@addrtype='ipv4']")
        if ip_elem is None:
            continue

        ip = ip_elem.get("addr")

        # Get hostname if available
        hostname = None
        hostname_elem = host.find("./hostnames/hostname")
        if hostname_elem is not None:
            hostname = hostname_elem.get("name")

        # Get OS fingerprint if available
        os_fingerprint = None
        os_elem = host.find("./os/osmatch")
        if os_elem is not None:
            os_fingerprint = os_elem.get("name", "")

        # Extract ports
        ports_data = []
        for port in host.findall(".//port"):
            port_info = {
                "port": int(port.get("portid")),
                "protocol": port.get("protocol"),
                "state": port.find("./state").get("state"),
            }

            # Add service information if available
            service = port.find("./service")
            if service is not None:
                port_info.update({
                    "service": service.get("name"),
                    "version": service.get("version"),
                    "product": service.get("product"),
                    "extra_info": service.get("extrainfo")
                })

            ports_data.append(port_info)

        if ports_data:
            results.append({
                "ip": ip,
                "hostname": hostname,
                "os_fingerprint": os_fingerprint,
                "ports": ports_data
            })

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Store port scan results to database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Store from XML file
  %(prog)s --xml-file scan.xml

  # Store from XML file with subsystem
  %(prog)s --xml-file scan.xml --subsystem "External Network"

  # Store from stdin
  nmap -sV -p- target.com -oX - | %(prog)s
        """
    )

    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--scan-tool", default="nmap",
                       help="Scan tool (default: nmap)")
    parser.add_argument("--xml-file", help="Nmap XML file path")

    args = parser.parse_args()

    # Read XML (from file or stdin)
    if args.xml_file:
        try:
            with open(args.xml_file, 'r') as f:
                xml_content = f.read()
        except FileNotFoundError:
            print(f"[-] File not found: {args.xml_file}")
            sys.exit(1)
    else:
        xml_content = sys.stdin.read()

    # Parse scan results
    scan_results = parse_nmap_xml(xml_content)

    if not scan_results:
        print("[-] No host results found in XML")
        sys.exit(0)

    # Store to database
    db = ResultsDatabase()
    total_ports = 0

    for host_result in scan_results:
        try:
            stored = store_port_scan(
                db, host_result, scan_tool=args.scan_tool,
                subsystem=args.subsystem)

            total_ports += stored

            hostname_str = f" ({host_result['hostname']})" if host_result['hostname'] else ""
            print(f"[+] Stored {len(host_result['ports'])} ports for {host_result['ip']}{hostname_str}")

        except Exception as e:
            print(f"[-] Error storing results for {host_result['ip']}: {e}")

    print(f"[+] Total: {total_ports} ports stored for {len(scan_results)} hosts")


if __name__ == "__main__":
    main()
