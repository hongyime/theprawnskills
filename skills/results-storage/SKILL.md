---
name: results-storage
description: SQLite-based persistent storage and reporting system for penetration testing results. Use this skill when user needs to store scan results, query vulnerabilities, generate reports, or manage pentest data across sessions.
license: Apache-2.0
metadata:
  author: "Local setup"
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Pentest Results Storage & Reporting

## Overview

The `results-storage` skill provides a SQLite-based persistent storage system for all penetration testing activities. It enables cross-session data persistence, structured vulnerability tracking, and professional report generation.

> **Note:** the upstream `storage_api.py` wrapper (`StorageAPI`) shipped broken
> (newlines stripped, tokens fused) and could not be imported, so it was
> removed. All storage and querying now goes through `ResultsDatabase`
> (`scripts/db_manager.py`) with plain SQL, plus `QueryBuilder` /
> `PredefinedQueries` (`scripts/query_builder.py`) for reads.

### Key Features

- **Persistent Storage**: SQLite database at `./data/results.db`
- **Flexible Organization**: Subsystem (optional) > Host hierarchy
- **Multi-Format Reports**: Markdown and JSON report generation
- **Query Capabilities**: Filter by severity, type, host, subsystem
- **Zero Breaking Changes**: Works alongside existing skills without modifications

### Data Organization

```
Subsystem (optional)
    └── Host
        ├── Port Scan Results
        ├── Vulnerabilities (SQLi, XSS, LFI, etc.)
        └── Web Findings (detailed web vulnerability info)
```

**Without Subsystem**: Data is organized in a flat Host hierarchy (subsystem_id is NULL)

## Quick Start

### Initialize Database

Database is automatically created on first use:

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase()
# Database created at ./data/results.db
```

### Store Vulnerability

Findings are stored with plain SQL through `ResultsDatabase`. The pattern is:
get-or-create the subsystem and host, insert the vulnerability row, then
attach the web-finding row. The two helpers below are copy-pasteable; they
use only `ResultsDatabase.get_connection()` and SQL against the schema in
`scripts/db_manager.py`.

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase()

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

# Flat hierarchy (no subsystem): SQLi finding
with db.get_connection() as conn:
    host_id = get_or_create_host(conn, "192.168.1.100")
    cur = conn.execute(
        "INSERT INTO vulnerabilities "
        "(host_id, vulnerability_type, severity, title, description, "
        " proof_of_concept, cvss_score, cwe_id, discovered_by_skill) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (host_id, "sqli", "Critical", "SQL Injection in Login Page",
         "Authentication bypass via SQL injection in id parameter",
         "1' OR '1'='1", 9.8, "CWE-89", "exploit-sqli"))
    vuln_id = cur.lastrowid
    conn.execute(
        "INSERT INTO web_findings "
        "(vulnerability_id, url, parameter, http_method, payload) "
        "VALUES (?, ?, ?, ?, ?)",
        (vuln_id, "https://example.com/login?id=1", "id", "GET",
         "1' OR '1'='1"))
    conn.commit()

# With subsystem: XSS finding
with db.get_connection() as conn:
    subsystem_id = get_or_create_subsystem(conn, "Web Application")
    host_id = get_or_create_host(conn, "192.168.1.100", subsystem_id)
    cur = conn.execute(
        "INSERT INTO vulnerabilities "
        "(host_id, vulnerability_type, severity, title, cvss_score, cwe_id, "
        " discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (host_id, "xss", "High", "Reflected XSS in Search Functionality",
         7.5, "CWE-79", "exploit-xss"))
    vuln_id = cur.lastrowid
    conn.execute(
        "INSERT INTO web_findings "
        "(vulnerability_id, url, parameter, http_method, payload, context) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (vuln_id, "https://example.com/search", "q", "GET",
         "<script>alert(1)</script>", "html_body"))
    conn.commit()
```

### Generate Report

```python
from scripts.report_generator import ReportGenerator

gen = ReportGenerator()

# Markdown report
gen.generate_markdown_report(output_path="pentest_report.md")

# JSON report
gen.generate_json_report(output_path="pentest_report.json")

# Subsystem-specific report
gen.generate_markdown_report(
    output_path="webapp_report.md",
    subsystem="Web Application"
)
```

## Database Schema

### Tables

**subsystems** (optional)
- id, name, description, subnet_range, created_at

**hosts**
- id, subsystem_id (nullable), ip_address, hostname, mac_address, os_fingerprint, status, first_seen, last_seen

**vulnerabilities**
- id, host_id, vulnerability_type, severity, title, description, affected_component, proof_of_concept, cvss_score, cwe_id, cve_id, status, discovered_at, discovered_by_skill

**port_scan_results**
- id, host_id, port, protocol, state, service, version, product, extra_info, scan_tool, scan_date

**web_findings** (detailed web vulnerability info)
- id, vulnerability_id, url, parameter, http_method, payload, response_evidence, context, request_headers

**scan_metadata**
- id, host_id, skill_used, scan_command, scan_date, raw_output_path, notes

### Indexes

Optimized for common queries:
- `idx_vulnerabilities_severity` on vulnerabilities(severity)
- `idx_vulnerabilities_type` on vulnerabilities(vulnerability_type)
- `idx_vulnerabilities_host` on vulnerabilities(host_id)
- `idx_port_scans_host` on port_scan_results(host_id)
- `idx_web_findings_vuln` on web_findings(vulnerability_id)

## API Reference

### ResultsDatabase Class

`ResultsDatabase` (`scripts/db_manager.py`) is the storage interface. It
creates the schema on first use, manages the SQLite connection, and runs
SQL. There are no `store_*` convenience methods — writes are plain SQL
against the schema (see "Storing findings" below); reads use `QueryBuilder`
/ `PredefinedQueries` (`scripts/query_builder.py`) or SQL.

#### Initialization

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase(db_path="./data/results.db")
```

#### Parameters

- `db_path` (str, optional) - Path to SQLite database file. Default: `"./data/results.db"`

#### Notes

- Database is automatically created if it doesn't exist
- Data directory is created with restrictive permissions (700)
- Database file is created with permissions 600 (owner read/write only)

#### Methods

```python
# Connection (use as a context manager; commits on clean exit)
conn = db.get_connection()
with db.get_connection() as conn:
    conn.execute("SELECT ...", (...,))

# Run one query; fetch='one' | 'all' | None (returns cursor)
row = db.execute_query("SELECT id FROM hosts WHERE ip_address = ?",
                       ("192.168.1.100",), fetch='one')
rows = db.execute_query("SELECT * FROM vulnerabilities WHERE severity = ?",
                        ("Critical",), fetch='all')

# Run one statement many times (batch insert); returns row count
db.execute_many(
    "INSERT OR REPLACE INTO port_scan_results "
    "(host_id, port, protocol, state, service) VALUES (?, ?, ?, ?, ?)",
    [(host_id, 80, "tcp", "open", "http"),
     (host_id, 443, "tcp", "open", "https")])

# Schema / maintenance
db.get_schema_version()   # -> "1.0.0"
db.get_database_info()    # -> {"path", "schema_version", "size_bytes",
                          #     "tables": {name: row_count}, "indexes": [...]}
db.vacuum()               # reclaim space
db.analyze()              # update query planner statistics
db.close()                # close the connection
```

`ResultsDatabase` is itself a context manager:

```python
with ResultsDatabase() as db:
    db.execute_query("SELECT COUNT(*) FROM vulnerabilities", fetch='one')
# Connection automatically closed
```

#### Storing findings

Use the get-or-create helpers from Quick Start, then insert rows. Valid
`severity` values: `Critical`, `High`, `Medium`, `Low`, `Info`. Valid
`vulnerability_type` values: `sqli`, `xss`, `lfi`, `rfi`, `ssrf`, `xxe`,
`file_download`, `command_injection`, `csrf`, `open_redirect`,
`path_traversal`, `insecure_deserialization`, `weak_auth`,
`info_disclosure`, `other`.

```python
# Subsystem (optional, idempotent)
with db.get_connection() as conn:
    conn.execute("INSERT OR IGNORE INTO subsystems (name, description, subnet_range) "
                 "VALUES (?, ?, ?)",
                 ("Web Application", "Customer A web infrastructure", "192.168.1.0/24"))
    subsystem_id = conn.execute(
        "SELECT id FROM subsystems WHERE name = ?", ("Web Application",)).fetchone()[0]
    conn.commit()

# List subsystems with host/vuln counts
rows = db.execute_query(
    "SELECT s.id, s.name, s.description, s.subnet_range, s.created_at, "
    "COUNT(DISTINCT h.id) as host_count, COUNT(DISTINCT v.id) as vuln_count "
    "FROM subsystems s "
    "LEFT JOIN hosts h ON s.id = h.subsystem_id "
    "LEFT JOIN vulnerabilities v ON h.id = v.host_id "
    "GROUP BY s.id ORDER BY s.name", fetch='all')

# Port scan results (batch)
db.execute_many(
    "INSERT OR REPLACE INTO port_scan_results "
    "(host_id, port, protocol, state, service, version, product, extra_info, scan_tool) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    [(host_id, 80, "tcp", "open", "http", "Apache httpd 2.4.41", "Apache", None, "nmap"),
     (host_id, 443, "tcp", "open", "https", None, None, None, "nmap")])
```

#### Querying findings

Use the query builders (`scripts/query_builder.py`) — they take a
`ResultsDatabase` and return lists of dicts:

```python
from scripts.query_builder import (
    VulnerabilityQueryBuilder, PortScanQueryBuilder, PredefinedQueries)

# All Critical vulnerabilities, critical first
vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.cvss_score",
            "v.vulnerability_type", "v.discovered_at",
            "h.ip_address", "h.hostname")
    .with_host_info()
    .by_severity("Critical")
    .critical_first()
    .execute())

# Web vulns in one subsystem (multiple types)
web_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.vulnerability_type")
    .with_subsystem()
    .by_subsystem("Web Application")
    .by_type("xss", "sqli", "lfi", "ssrf", "xxe")
    .execute())

# Vulnerabilities for one host
host_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity")
    .with_host_info()
    .by_host("192.168.1.100")
    .execute())

# Open ports for a host
ports = (PortScanQueryBuilder(db)
    .select("psr.port", "psr.protocol", "psr.state", "psr.service")
    .with_host_info()
    .by_host("192.168.1.100")
    .open_ports_only()
    .execute())

# Predefined aggregate queries
q = PredefinedQueries(db)
q.get_critical_vulnerabilities(limit=10)   # critical vulns, CVSS desc
q.get_vulnerability_by_host()              # vuln counts grouped by host
q.get_exposed_services()                   # open services across hosts
q.get_most_vulnerable_subsystems(limit=10)
q.get_vulnerability_type_trend()
q.get_scan_coverage()
```

#### Statistics

```python
# Totals + severity breakdown (SQL aggregate)
row = db.execute_query(
    "SELECT COUNT(*) as total, "
    "COUNT(CASE WHEN severity='Critical' THEN 1 END) as critical, "
    "COUNT(CASE WHEN severity='High' THEN 1 END) as high, "
    "COUNT(CASE WHEN severity='Medium' THEN 1 END) as medium, "
    "COUNT(CASE WHEN severity='Low' THEN 1 END) as low, "
    "COUNT(CASE WHEN severity='Info' THEN 1 END) as info, "
    "AVG(cvss_score) as avg_cvss FROM vulnerabilities",
    fetch='one')
```

### ReportGenerator Class

```python
gen = ReportGenerator(db_path="./data/results.db")

# Markdown report
markdown_path = gen.generate_markdown_report(
    output_path="report.md",      # Optional: auto-generates if None
    subsystem="Web Application"    # Optional: includes all if None
)

# JSON report
json_path = gen.generate_json_report(
    output_path="report.json",
    subsystem="Web Application"
)

# Executive summary only
summary = gen.generate_executive_summary(subsystem="Web Application")

# Risk score calculation
risk_info = gen.calculate_risk_score(vulnerabilities)
# Returns: {"score": 8.5, "level": "High"}
```

## Integration with Existing Skills

All existing skills have optional storage scripts. These scripts:

1. **Parse tool output** (nmap XML, sqlmap JSON, etc.)
2. **Write findings to the database** with `ResultsDatabase` SQL (see API Reference)
3. **Support --subsystem flag** for optional grouping

### Example: Port Scan Storage

```bash
# Flat hierarchy
nmap -sV -p- 192.168.1.0/24 -oX scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file scan.xml

# With subsystem
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file scan.xml \
  --subsystem "External Network"
```

### Example: SQLi Storage

```bash
sqlmap -u "https://example.com/login?id=1" --batch --answers=continuing
python ../exploit-sqli/scripts/sqli_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://example.com/login?id=1" \
  --parameter id \
  --subsystem "Web Application" \
  --severity Critical
```

## Usage Scenarios

### Scenario 1: Multi-Session Penetration Test

**Situation**: You're conducting a penetration test over several days and need to maintain state across sessions.

```bash
# Day 1: Initial reconnaissance
nmap -sV -p- 192.168.1.0/24 -oX day1_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file day1_scan.xml \
  --subsystem "Customer A"

# Day 2: Web application testing
sqlmap -u "https://customer-a.com/login?id=1" --batch
python ../exploit-sqli/scripts/sqli_storage.py \
  --host-ip 192.168.1.100 \
  --url "https://customer-a.com/login?id=1" \
  --parameter id \
  --subsystem "Customer A"

# Day 3: Generate report
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('customer_a_report.md', 'Customer A')
"
```

### Scenario 2: Multi-Subsystem Organization

**Situation**: Testing a large network with distinct subsystems (DMZ, Internal, Cloud).

```bash
# DMZ scanning
nmap -sV -p- 10.0.0.0/24 -oX dmz_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file dmz_scan.xml \
  --subsystem "DMZ"

# Internal network
nmap -sV -p- 192.168.1.0/24 -oX internal_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file internal_scan.xml \
  --subsystem "Internal"

# Cloud infrastructure
nmap -sV -p- 10.1.0.0/24 -oX cloud_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file cloud_scan.xml \
  --subsystem "Cloud"

# Generate subsystem-specific reports
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('dmz_report.md', 'DMZ')
gen.generate_markdown_report('internal_report.md', 'Internal')
gen.generate_markdown_report('cloud_report.md', 'Cloud')
"

# Or generate comprehensive report
python -c "
gen = ReportGenerator()
gen.generate_markdown_report('full_report.md')
"
```

### Scenario 3: Vulnerability Querying

**Situation**: You need to find all Critical vulnerabilities across all hosts.

```python
from scripts.db_manager import ResultsDatabase
from scripts.query_builder import VulnerabilityQueryBuilder

db = ResultsDatabase()

critical_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.cvss_score",
            "v.vulnerability_type", "v.discovered_at",
            "h.ip_address", "h.hostname")
    .with_host_info()
    .by_severity("Critical")
    .critical_first()
    .execute())

for vuln in critical_vulns:
    print(f"[{vuln['id']}] {vuln['title']}")
    print(f"  Host: {vuln['ip_address']}")
    print(f"  Type: {vuln['vulnerability_type']}")
    print(f"  CVSS: {vuln['cvss_score']}")
    print(f"  Discovered: {vuln['discovered_at']}")
    print()
```

### Scenario 4: Flat Hierarchy Usage

**Situation**: Simple test without complex organization.

```bash
# No subsystem specified - uses flat hierarchy
nmap -sV -p- 192.168.1.0/24 -oX scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py \
  --xml-file scan.xml

# Query flat hierarchy (no subsystem) — store an XSS finding with SQL
python -c "
from scripts.db_manager import ResultsDatabase
db = ResultsDatabase()
with db.get_connection() as conn:
    # No subsystem = flat hierarchy (subsystem_id NULL)
    conn.execute(
        'INSERT OR IGNORE INTO hosts (ip_address) VALUES (?)',
        ('192.168.1.100',))
    host_id = conn.execute(
        'SELECT id FROM hosts WHERE ip_address = ?',
        ('192.168.1.100',)).fetchone()[0]
    cur = conn.execute(
        'INSERT INTO vulnerabilities '
        '(host_id, vulnerability_type, severity, title, cvss_score, cwe_id, '
        ' discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (host_id, 'xss', 'High', 'Reflected XSS in Search',
         7.5, 'CWE-79', 'exploit-xss'))
    vuln_id = cur.lastrowid
    conn.execute(
        'INSERT INTO web_findings '
        '(vulnerability_id, url, parameter, http_method, payload, context) '
        'VALUES (?, ?, ?, ?, ?, ?)',
        (vuln_id, 'https://example.com/search', 'q', 'GET',
         '<script>alert(1)</script>', 'html_body'))
    conn.commit()
"
```

### Scenario 5: Host-Based Investigation

**Situation**: Deep dive into a specific host's findings.

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase()

# Host row, open ports, and vulnerabilities, via SQL
with db.get_connection() as conn:
    import sqlite3
    conn.row_factory = sqlite3.Row
    host = dict(conn.execute(
        "SELECT h.*, s.name as subsystem_name FROM hosts h "
        "LEFT JOIN subsystems s ON h.subsystem_id = s.id "
        "WHERE h.ip_address = ?", ("192.168.1.100",)).fetchone())
    ports = [dict(r) for r in conn.execute(
        "SELECT port, protocol, state, service, version, product, extra_info, scan_tool "
        "FROM port_scan_results WHERE host_id = ? ORDER BY port",
        (host['id'],)).fetchall()]
    vulns = [dict(r) for r in conn.execute(
        "SELECT v.id, v.vulnerability_type, v.severity, v.title, v.description, "
        "v.proof_of_concept, v.cvss_score, v.cwe_id, v.cve_id, v.discovered_at, "
        "wf.url, wf.parameter, wf.context "
        "FROM vulnerabilities v "
        "LEFT JOIN web_findings wf ON v.id = wf.vulnerability_id "
        "WHERE v.host_id = ? ORDER BY v.cvss_score DESC",
        (host['id'],)).fetchall()]

print(f"IP: {host['ip_address']}")
print(f"Hostname: {host.get('hostname', 'Unknown')}")
print(f"OS: {host.get('os_fingerprint', 'Unknown')}")
print(f"Open Ports: {len([p for p in ports if p['state'] == 'open'])}")
print(f"Vulnerabilities: {len(vulns)}")

print("\n--- Vulnerabilities ---")
for vuln in vulns:
    print(f"[{vuln['severity']}] {vuln['title']}")

print("\n--- Open Ports ---")
for port in ports:
    print(f"Port {port['port']}/{port['protocol']}: {port.get('service', 'unknown')} ({port['state']})")
```

### Scenario 6: Custom Queries

**Situation**: You need to query for specific vulnerability patterns.

```python
from scripts.db_manager import ResultsDatabase
from scripts.query_builder import VulnerabilityQueryBuilder

db = ResultsDatabase()

# All web vulnerabilities in a subsystem
web_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.vulnerability_type")
    .with_subsystem()
    .by_subsystem("Web Application")
    .by_type("xss", "sqli", "lfi", "ssrf", "xxe")
    .execute())

# High-severity SQLi across all subsystems
sqli_high = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.vulnerability_type")
    .with_host_info()
    .by_type("sqli")
    .by_severity("High", "Critical")
    .execute())

# Vulnerabilities for a specific host
host_vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.vulnerability_type")
    .with_host_info()
    .by_host("192.168.1.100")
    .execute())
```

## Report Customization

### Markdown Report Sections

Generated reports include:
1. **Executive Summary** - High-level overview and risk score
2. **Methodology** - Testing approach and tools used
3. **Detailed Findings** - Vulnerabilities grouped by severity
4. **Host Inventory** - All discovered hosts
5. **Recommendations** - Prioritized remediation steps
6. **Appendices** - Commands, tool outputs, compliance

### JSON Report Schema

```json
{
  "metadata": {
    "report_date": "2025-02-14",
    "test_period": {
      "start": "2025-02-10",
      "end": "2025-02-14"
    },
    "testers": ["pentester"]
  },
  "executive_summary": {
    "risk_score": 8.5,
    "total_vulnerabilities": 47,
    "severity_breakdown": {...}
  },
  "subsystems": [...],
  "hosts": [...],
  "vulnerabilities": [...],
  "recommendations": [...]
}
```

## Data Management

### Database Location

`./data/results.db`

### Backup

```bash
# Simple backup
cp ./data/results.db ./data/results_backup_$(date +%Y%m%d).db

# Encrypted backup (recommended for production)
gpg --cipher-algo AES256 --compress-algo 1 --symmetric ./data/results.db
```

### Export/Import

```bash
# SQLite to SQL
sqlite3 ./data/results.db .dump > results_backup.sql

# SQL to SQLite
sqlite3 ./data/results.db < results_backup.sql
```

### Database Reset

```bash
# CAUTION: Deletes all data
rm ./data/results.db
# Database will be recreated on next use
```

## Performance Considerations

- **Capacity**: Tested with 10,000+ vulnerabilities
- **Query Time**: < 1 second for filtered queries
- **Report Generation**: < 10 seconds for full report with 1,000+ vulnerabilities
- **Indexes**: Automatically created for common query patterns

## Security Considerations

### Data Protection

1. **Database Permissions**: Results.db is created with 600 permissions (owner read/write only)
2. **Sensitive Data**: Database contains PoC code - consider encryption for production environments
3. **Audit Trail**: All findings include timestamps and discovery methods

### Best Practices

- **Regular Backups**: Backup after each testing session
- **Access Control**: Ensure file system permissions are restrictive
- **Encryption**: Encrypt backups before storing in shared locations
- **Retention**: Follow retention policies - delete data when no longer needed

## Troubleshooting

### Database Locked

```bash
# Check for processes using the database
lsof ./data/results.db

# Kill blocking processes if needed
kill -9 <PID>
```

### Import Errors

```bash
# Ensure Python path is correct
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "from scripts.db_manager import ResultsDatabase; print(ResultsDatabase().get_schema_version())"
```

### Report Generation Errors

```bash
# Install Jinja2 if missing
pip install jinja2

# Verify database exists
ls -lh ./data/results.db
```

## Compliance

This storage and reporting system supports compliance with:

- **OWASP Testing Guide** v4.2
- **PTES** (Penetration Testing Execution Standard)
- **OSSTMM** (Open Source Security Testing Methodology)

All timestamps are recorded in UTC for consistency.

## Related Skills

- **recon-port-scan** - Port scanning with storage integration
- **recon-subdomain** - Subdomain enumeration with storage integration
- **exploit-sqli** - SQL injection testing with storage integration
- **exploit-xss** - XSS testing with storage integration
- **exploit-lfi** - LFI testing with storage integration

## Advanced Usage

### Programmatic Access

```python
import sqlite3

conn = sqlite3.connect('./data/results.db')
cursor = conn.cursor()

# Custom SQL queries
cursor.execute("""
    SELECT h.ip_address, COUNT(v.id) as vuln_count
    FROM hosts h
    LEFT JOIN vulnerabilities v ON h.id = v.host_id
    GROUP BY h.ip_address
    ORDER BY vuln_count DESC
""")

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} vulnerabilities")

conn.close()
```

### Batch Operations

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase()

# Batch-insert port scan rows with one call
db.execute_many(
    "INSERT OR REPLACE INTO port_scan_results "
    "(host_id, port, protocol, state, service) VALUES (?, ?, ?, ?, ?)",
    [(host_id, 80, "tcp", "open", "http"),
     (host_id, 443, "tcp", "open", "https"),
     (host_id, 22, "tcp", "open", "ssh")])

# Batch-insert vulnerabilities (resolve each host_id first, then insert)
with db.get_connection() as conn:
    rows = []
    for vuln_data in [
        {"host_ip": "192.168.1.100", "vuln_type": "xss", "severity": "High",
         "title": "Reflected XSS in Search", "cwe_id": "CWE-79",
         "discovered_by_skill": "exploit-xss"},
        {"host_ip": "192.168.1.101", "vuln_type": "sqli", "severity": "Critical",
         "title": "SQL Injection in Login", "cwe_id": "CWE-89",
         "discovered_by_skill": "exploit-sqli"},
    ]:
        conn.execute("INSERT OR IGNORE INTO hosts (ip_address) VALUES (?)",
                     (vuln_data["host_ip"],))
        host_id = conn.execute(
            "SELECT id FROM hosts WHERE ip_address = ?",
            (vuln_data["host_ip"],)).fetchone()[0]
        rows.append((host_id, vuln_data["vuln_type"], vuln_data["severity"],
                     vuln_data["title"], vuln_data["cwe_id"],
                     vuln_data["discovered_by_skill"]))
    conn.executemany(
        "INSERT INTO vulnerabilities "
        "(host_id, vulnerability_type, severity, title, cwe_id, discovered_by_skill) "
        "VALUES (?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
```

---

*This skill provides the foundation for persistent, organized penetration testing data management across all pentest-skills capabilities.*
