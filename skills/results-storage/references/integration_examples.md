# Integration Examples

Examples of integrating pentest-skills with the results-storage system.

> **Note:** the upstream `storage_api.py` wrapper (`StorageAPI`) shipped broken
> and was removed. The storage scripts below are written against
> `ResultsDatabase` (`scripts/db_manager.py`) with plain SQL. The copies
> shipped in the sibling skills (`port_scan_storage.py`, `sqli_storage.py`,
> `xss_storage.py`, `lfi_storage.py`, `subdomain_storage.py`) still import
> the removed `StorageAPI` and need the same migration before they run —
> use the scripts below as the working templates.

## Overview

The results-storage system integrates with all pentest-skills through
**storage scripts**. Each skill has an optional storage script that:

1. **Parses tool output** (nmap XML, sqlmap JSON, etc.)
2. **Writes findings to the database** with `ResultsDatabase` SQL
3. **Supports --subsystem flag** for optional grouping

## Integration Pattern

All storage scripts follow a consistent pattern:

```python
#!/usr/bin/env python3
"""
[Vulnerability Type] Storage Script
Parses [tool] output and stores to database
"""

import sys
from pathlib import Path

# Add results-storage to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase

def get_or_create_subsystem(conn, name):
    conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)", (name,))
    return conn.execute(
        "SELECT id FROM subsystems WHERE name = ?", (name,)).fetchone()[0]

def get_or_create_host(conn, ip, subsystem_id=None, hostname=None):
    conn.execute(
        "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address, hostname) "
        "VALUES (?, ?, ?)", (subsystem_id, ip, hostname))
    return conn.execute(
        "SELECT id FROM hosts WHERE ip_address = ? "
        "AND (subsystem_id IS ? OR subsystem_id = ?)",
        (ip, subsystem_id, subsystem_id)).fetchone()[0]

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store [vulnerability type] to database")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--host-ip", required=True, help="Target host IP")
    parser.add_argument("--url", required=True, help="Vulnerable URL")
    # ... other arguments

    args = parser.parse_args()

    # Parse output (from file or stdin)
    data = parse_output(args)

    # Store to database
    db = ResultsDatabase()
    with db.get_connection() as conn:
        subsystem_id = get_or_create_subsystem(conn, args.subsystem) if args.subsystem else None
        host_id = get_or_create_host(conn, args.host_ip, subsystem_id)
        cur = conn.execute(
            "INSERT INTO vulnerabilities "
            "(host_id, vulnerability_type, severity, title, cvss_score, cwe_id, "
            " discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (host_id, data["vuln_type"], data["severity"], data["title"],
             data.get("cvss_score"), data.get("cwe_id"), data.get("discovered_by_skill")))
        vuln_id = cur.lastrowid
        conn.execute(
            "INSERT INTO web_findings "
            "(vulnerability_id, url, parameter, http_method, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (vuln_id, args.url, data.get("parameter"), "GET", data.get("payload")))
        conn.commit()
    db.close()

if __name__ == "__main__":
    main()
```

---

## Example 1: Port Scan Storage

### Script: port_scan_storage.py

```python
#!/usr/bin/env python3
"""
Port Scan Results Storage Script
Parse nmap XML output and store to database
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase

def get_or_create_host(conn, ip, subsystem_id=None):
    conn.execute(
        "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address) VALUES (?, ?)",
        (subsystem_id, ip))
    return conn.execute(
        "SELECT id FROM hosts WHERE ip_address = ? "
        "AND (subsystem_id IS ? OR subsystem_id = ?)",
        (ip, subsystem_id, subsystem_id)).fetchone()[0]

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store port scan results")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--scan-tool", default="nmap", help="Scan tool")
    parser.add_argument("--xml-file", help="Nmap XML file path")

    args = parser.parse_args()

    # Parse XML
    if args.xml_file:
        tree = ET.parse(args.xml_file)
        root = tree.getroot()
    else:
        xml_content = sys.stdin.read()
        root = ET.fromstring(xml_content)

    db = ResultsDatabase()
    for host in root.findall(".//host"):
        ip_elem = host.find("./address[@addrtype='ipv4']")
        if ip_elem is None:
            continue
        ip = ip_elem.get("addr")
        ports_data = []
        for port in host.findall(".//port"):
            port_info = {
                "port": int(port.get("portid")),
                "protocol": port.get("protocol"),
                "state": port.find("./state").get("state"),
            }
            service = port.find("./service")
            if service is not None:
                port_info.update({
                    "service": service.get("name"),
                    "version": service.get("version"),
                    "product": service.get("product"),
                    "extra_info": service.get("extrainfo")
                })
            ports_data.append(port_info)

        # Store to database
        if ports_data:
            with db.get_connection() as conn:
                subsystem_id = None
                if args.subsystem:
                    conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                                 (args.subsystem,))
                    subsystem_id = conn.execute(
                        "SELECT id FROM subsystems WHERE name = ?",
                        (args.subsystem,)).fetchone()[0]
                host_id = get_or_create_host(conn, ip, subsystem_id)
                conn.commit()
            db.execute_many(
                "INSERT OR REPLACE INTO port_scan_results "
                "(host_id, port, protocol, state, service, version, product, "
                " extra_info, scan_tool) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [(host_id, p["port"], p.get("protocol", "tcp"), p["state"],
                  p.get("service"), p.get("version"), p.get("product"),
                  p.get("extra_info"), args.scan_tool) for p in ports_data])
            print(f"[+] Stored {len(ports_data)} ports for {ip}")
    db.close()

if __name__ == "__main__":
    main()
```

### Usage

```bash
# Store nmap scan (flat hierarchy)
nmap -sV -p- 192.168.1.0/24 -oX scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file scan.xml

# Store with subsystem
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file scan.xml \
  --subsystem "External Network"
```

---

## Example 2: SQL Injection Storage

### Script: sqli_storage.py

```python
#!/usr/bin/env python3
"""
SQL Injection Storage Script
Parse sqlmap output and store to database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase

def parse_sqlmap_output(output_file):
    """Parse sqlmap output (simplified example)"""
    # In reality, parse sqlmap's output format
    # This is a simplified example
    return {
        "parameter": "id",
        "payload": "1' OR '1'='1",
        "cvss_score": 9.8
    }

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store SQL injection to database")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--host-ip", required=True, help="Target host IP")
    parser.add_argument("--url", required=True, help="Vulnerable URL")
    parser.add_argument("--parameter", required=True, help="Vulnerable parameter")
    parser.add_argument("--payload", required=True, help="Payload used")
    parser.add_argument("--severity", default="High", help="Severity level")

    args = parser.parse_args()

    # Store to database
    db = ResultsDatabase()
    with db.get_connection() as conn:
        subsystem_id = None
        if args.subsystem:
            conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                         (args.subsystem,))
            subsystem_id = conn.execute(
                "SELECT id FROM subsystems WHERE name = ?",
                (args.subsystem,)).fetchone()[0]
        conn.execute(
            "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address) VALUES (?, ?)",
            (subsystem_id, args.host_ip))
        host_id = conn.execute(
            "SELECT id FROM hosts WHERE ip_address = ? "
            "AND (subsystem_id IS ? OR subsystem_id = ?)",
            (args.host_ip, subsystem_id, subsystem_id)).fetchone()[0]
        cur = conn.execute(
            "INSERT INTO vulnerabilities "
            "(host_id, vulnerability_type, severity, title, description, "
            " cvss_score, cwe_id, discovered_by_skill) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (host_id, "sqli", args.severity,
             f"SQL Injection in {args.parameter}",
             f"SQL injection vulnerability in parameter {args.parameter}",
             9.8, "CWE-89", "exploit-sqli"))
        vuln_id = cur.lastrowid
        conn.execute(
            "INSERT INTO web_findings "
            "(vulnerability_id, url, parameter, http_method, payload) "
            "VALUES (?, ?, ?, ?, ?)",
            (vuln_id, args.url, args.parameter, "GET", args.payload))
        conn.commit()
    db.close()

    print(f"[+] Stored SQL injection vulnerability (ID: {vuln_id})")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# After running sqlmap
sqlmap -u "https://example.com/login?id=1" --batch

# Manually store the finding
python ../exploit-sqli/scripts/sqli_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://example.com/login?id=1" \
  --parameter id \
  --payload "1' OR '1'='1" \
  --subsystem "Web Application" \
  --severity Critical
```

---

## Example 3: XSS Storage

### Script: xss_storage.py

```python
#!/usr/bin/env python3
"""
XSS Storage Script
Parse XSS test output and store to database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store XSS to database")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--host-ip", required=True, help="Target host IP")
    parser.add_argument("--url", required=True, help="Vulnerable URL")
    parser.add_argument("--xss-type", required=True,
                       choices=["reflected", "stored", "dom"],
                       help="XSS type")
    parser.add_argument("--payload", required=True, help="Payload used")
    parser.add_argument("--context", default="html_body", help="XSS context")
    parser.add_argument("--severity", default="Medium", help="Severity level")

    args = parser.parse_args()

    # Store to database
    db = ResultsDatabase()
    with db.get_connection() as conn:
        subsystem_id = None
        if args.subsystem:
            conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                         (args.subsystem,))
            subsystem_id = conn.execute(
                "SELECT id FROM subsystems WHERE name = ?",
                (args.subsystem,)).fetchone()[0]
        conn.execute(
            "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address) VALUES (?, ?)",
            (subsystem_id, args.host_ip))
        host_id = conn.execute(
            "SELECT id FROM hosts WHERE ip_address = ? "
            "AND (subsystem_id IS ? OR subsystem_id = ?)",
            (args.host_ip, subsystem_id, subsystem_id)).fetchone()[0]
        cur = conn.execute(
            "INSERT INTO vulnerabilities "
            "(host_id, vulnerability_type, severity, title, description, "
            " cwe_id, discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (host_id, "xss", args.severity,
             f"{args.xss_type.capitalize()} XSS",
             f"{args.xss_type} cross-site scripting vulnerability",
             "CWE-79", "exploit-xss"))
        vuln_id = cur.lastrowid
        conn.execute(
            "INSERT INTO web_findings "
            "(vulnerability_id, url, http_method, payload, context) "
            "VALUES (?, ?, ?, ?, ?)",
            (vuln_id, args.url, "GET", args.payload, args.context))
        conn.commit()
    db.close()

    print(f"[+] Stored XSS vulnerability (ID: {vuln_id})")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# After testing XSS manually
python ../exploit-xss/scripts/xss_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://example.com/search?q=test" \
  --xss-type reflected \
  --payload "<script>alert(1)</script>" \
  --context html_body \
  --subsystem "Web Application" \
  --severity High
```

---

## Example 4: LFI Storage

### Script: lfi_storage.py

```python
#!/usr/bin/env python3
"""
LFI Storage Script
Parse LFI test output and store to database
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store LFI to database")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--host-ip", required=True, help="Target host IP")
    parser.add_argument("--url", required=True, help="Vulnerable URL")
    parser.add_argument("--payload", required=True, help="Payload used")
    parser.add_argument("--file-read", help="Content of file read")
    parser.add_argument("--severity", default="High", help="Severity level")

    args = parser.parse_args()

    # Store to database (file content goes in proof_of_concept / response_evidence)
    db = ResultsDatabase()
    with db.get_connection() as conn:
        subsystem_id = None
        if args.subsystem:
            conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                         (args.subsystem,))
            subsystem_id = conn.execute(
                "SELECT id FROM subsystems WHERE name = ?",
                (args.subsystem,)).fetchone()[0]
        conn.execute(
            "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address) VALUES (?, ?)",
            (subsystem_id, args.host_ip))
        host_id = conn.execute(
            "SELECT id FROM hosts WHERE ip_address = ? "
            "AND (subsystem_id IS ? OR subsystem_id = ?)",
            (args.host_ip, subsystem_id, subsystem_id)).fetchone()[0]
        cur = conn.execute(
            "INSERT INTO vulnerabilities "
            "(host_id, vulnerability_type, severity, title, description, "
            " proof_of_concept, cwe_id, discovered_by_skill) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (host_id, "lfi", args.severity, "Local File Inclusion",
             "Local file inclusion vulnerability allows reading files from the server",
             args.file_read or args.payload, "CWE-98", "exploit-lfi"))
        vuln_id = cur.lastrowid
        conn.execute(
            "INSERT INTO web_findings "
            "(vulnerability_id, url, http_method, payload, response_evidence) "
            "VALUES (?, ?, ?, ?, ?)",
            (vuln_id, args.url, "GET", args.payload, args.file_read or ""))
        conn.commit()
    db.close()

    print(f"[+] Stored LFI vulnerability (ID: {vuln_id})")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# After successful LFI exploitation
python ../exploit-lfi/scripts/lfi_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://example.com/download?file=../../etc/passwd" \
  --payload "../../etc/passwd" \
  --file-read "root:x:0:0:root:/root:/bin/bash\n..." \
  --subsystem "Web Application" \
  --severity Critical
```

---

## Example 5: Subdomain Storage

### Script: subdomain_storage.py

```python
#!/usr/bin/env python3
"""
Subdomain Storage Script
Parse subdomain enumeration results and store hosts
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'results-storage' / 'scripts'))

from db_manager import ResultsDatabase
import socket

def resolve_ip(hostname):
    """Resolve hostname to IP"""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store subdomains to database")
    parser.add_argument("--subsystem", help="Subsystem name (optional)")
    parser.add_argument("--input-file", help="File containing subdomains (one per line)")

    args = parser.parse_args()

    # Read subdomains
    if args.input_file:
        with open(args.input_file) as f:
            subdomains = [line.strip() for line in f if line.strip()]
    else:
        subdomains = [line.strip() for line in sys.stdin if line.strip()]

    # Store to database (hosts only — no vulnerability rows)
    db = ResultsDatabase()
    stored_count = 0
    with db.get_connection() as conn:
        subsystem_id = None
        if args.subsystem:
            conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                         (args.subsystem,))
            subsystem_id = conn.execute(
                "SELECT id FROM subsystems WHERE name = ?",
                (args.subsystem,)).fetchone()[0]
        for subdomain in subdomains:
            ip = resolve_ip(subdomain)
            if ip:
                conn.execute(
                    "INSERT OR IGNORE INTO hosts "
                    "(subsystem_id, ip_address, hostname) VALUES (?, ?, ?)",
                    (subsystem_id, ip, subdomain))
                stored_count += 1
                print(f"[+] Stored {subdomain} -> {ip}")
        conn.commit()
    db.close()

    print(f"[+] Stored {stored_count} subdomains")

if __name__ == "__main__":
    main()
```

### Usage

```bash
# After running subfinder
subfinder -d example.com > subdomains.txt

# Store subdomains (flat hierarchy)
python ../recon-subdomain/scripts/subdomain_storage.py \
  --input-file subdomains.txt

# Store with subsystem
python ../recon-subdomain/scripts/subdomain_storage.py \
  --input-file subdomains.txt \
  --subsystem "External Infrastructure"
```

---

## Complete Workflow Example

### Multi-Day Penetration Test

```bash
# === Day 1: Initial Reconnaissance ===

# Port scan and store
nmap -sV -p- 192.168.1.0/24 -oX day1_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file day1_scan.xml \
  --subsystem "Customer A"

# Subdomain enumeration and store
subfinder -d customer-a.com > subdomains.txt
python ../recon-subdomain/scripts/subdomain_storage.py \
  --input-file subdomains.txt \
  --subsystem "Customer A"

# === Day 2: Web Application Testing ===

# SQL injection discovery
sqlmap -u "https://customer-a.com/login?id=1" --batch
python ../exploit-sqli/scripts/sqli_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://customer-a.com/login?id=1" \
  --parameter id \
  --payload "1' OR '1'='1" \
  --subsystem "Customer A" \
  --severity Critical

# XSS testing
python ../exploit-xss/scripts/xss_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://example.com/search?q=test" \
  --xss-type reflected \
  --payload "<script>alert(1)</script>" \
  --subsystem "Customer A" \
  --severity High

# === Day 3: Report Generation ===

# Generate comprehensive report
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('customer_a_report.md', 'Customer A')
gen.generate_json_report('customer_a_report.json', 'Customer A')
"

# Or generate all-subsystems report
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('full_report.md')
"
```

---

## Programmatic Usage

### Python API

```python
from scripts.db_manager import ResultsDatabase
from scripts.query_builder import VulnerabilityQueryBuilder, PredefinedQueries
from scripts.report_generator import ReportGenerator

# Initialize
db = ResultsDatabase()

# Create subsystem + host, store an SQLi finding (SQL, see api_reference.md)
with db.get_connection() as conn:
    conn.execute("INSERT OR IGNORE INTO subsystems (name) VALUES (?)",
                 ("Web Application",))
    subsystem_id = conn.execute(
        "SELECT id FROM subsystems WHERE name = ?", ("Web Application",)).fetchone()[0]
    conn.execute(
        "INSERT OR IGNORE INTO hosts (subsystem_id, ip_address) VALUES (?, ?)",
        (subsystem_id, "192.168.1.100"))
    host_id = conn.execute(
        "SELECT id FROM hosts WHERE ip_address = ? "
        "AND (subsystem_id IS ? OR subsystem_id = ?)",
        ("192.168.1.100", subsystem_id, subsystem_id)).fetchone()[0]
    cur = conn.execute(
        "INSERT INTO vulnerabilities "
        "(host_id, vulnerability_type, severity, title, cvss_score, cwe_id, "
        " discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (host_id, "sqli", "Critical", "SQL Injection in id", 9.8, "CWE-89",
         "exploit-sqli"))
    vuln_id = cur.lastrowid
    conn.execute(
        "INSERT INTO web_findings "
        "(vulnerability_id, url, parameter, http_method, payload) "
        "VALUES (?, ?, ?, ?, ?)",
        (vuln_id, "https://example.com/login?id=1", "id", "GET", "1' OR '1'='1"))
    conn.commit()

# Query vulnerabilities
critical_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity")
    .with_subsystem()
    .by_subsystem("Web Application")
    .by_severity("Critical")
    .execute())
for vuln in critical_vulns:
    print(f"[{vuln['id']}] {vuln['title']}")

# Statistics
stats = PredefinedQueries(db).get_most_vulnerable_subsystems(limit=10)
print(f"Most vulnerable: {stats[0]['subsystem_name'] if stats else 'none'}")

# Generate reports
gen = ReportGenerator()
gen.generate_markdown_report(
    output_path="webapp_report.md",
    subsystem="Web Application"
)
db.close()
gen.close()
```

---

## Tips and Best Practices

### 1. Use Consistent Subsystem Names

```bash
# Good - consistent naming
python ... --subsystem "Web Application"
python ... --subsystem "Web Application"

# Bad - inconsistent
python ... --subsystem "Web App"
python ... --subsystem "webapp"
```

### 2. Store After Every Test Session

```bash
# After each tool execution, immediately store results
nmap -sV target.com -oX scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py --xml-file scan.xml

# Don't wait until end of engagement
# Data may be lost if system crashes
```

### 3. Backup Database Regularly

```bash
# After each testing day
cp ./data/results.db ./data/results_backup_$(date +%Y%m%d).db

# Or encrypted backup
gpg --cipher-algo AES256 --symmetric ./data/results.db
```

### 4. Verify Storage

```bash
# Quick check after storing
python -c "
from scripts.db_manager import ResultsDatabase
db = ResultsDatabase()
row = db.execute_query(
    'SELECT COUNT(*) FROM vulnerabilities', fetch='one')
print(f'Vulnerabilities: {row[0]}')
"
```

### 5. Generate Subsystem-Specific Reports

```bash
# For specific teams or stakeholders
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('dmz_report.md', 'DMZ')
gen.generate_markdown_report('internal_report.md', 'Internal Network')
"
```

---

## Troubleshooting

### Import Errors

```bash
# Error: Module not found
# Solution: Add results-storage to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python ../recon-port-scan/scripts/port_scan_storage.py ...
```

### Database Locked

```bash
# Error: database is locked
# Solution: Check for other processes
lsof ./data/results.db
```

### Permission Errors

```bash
# Error: unable to open database file
# Solution: Check data directory permissions
chmod 700 ./data
chmod 600 ./data/results.db
```

---

For database schema, see `database_schema.md`.

For API reference, see `api_reference.md`.
