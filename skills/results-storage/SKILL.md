---
name: results-storage
description: >-
  When to read: storing scan results, querying vulnerabilities, or managing pentest data across
  sessions. Use for: SQLite-based persistent storage and reporting for penetration testing
  results. Does: enables cross-session persistence, structured vulnerability tracking, and
  professional report generation.
license: Apache-2.0
metadata:
  author: "Local setup"
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Pentest Results Storage & Reporting

## Overview

SQLite-based persistent storage for penetration testing: cross-session persistence, structured vulnerability tracking, Markdown/JSON reports. Database at `./data/results.db`, organized as optional Subsystem > Host > port scans / vulnerabilities / web findings (no subsystem = flat Host hierarchy, `subsystem_id` NULL).

> **Note:** the upstream `storage_api.py` wrapper (`StorageAPI`) shipped broken (newlines stripped, tokens fused) and was removed. All storage/querying goes through `ResultsDatabase` (`scripts/db_manager.py`) with plain SQL, plus `QueryBuilder` / `PredefinedQueries` (`scripts/query_builder.py`) for reads.

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

# With subsystem: same pattern — get subsystem id first, then pass it to
# get_or_create_host (see "Storing findings" for the subsystem insert).
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

db = ResultsDatabase(db_path="./data/results.db")  # default "./data/results.db"
```

Database and data directory are auto-created (dir 700, file 600).

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
```

Port-scan batch insert is shown under Methods (`execute_many`) above.

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

markdown_path = gen.generate_markdown_report(
    output_path="report.md",      # optional: auto-generates if None
    subsystem="Web Application"    # optional: includes all if None
)
json_path = gen.generate_json_report(
    output_path="report.json", subsystem="Web Application")
summary = gen.generate_executive_summary(subsystem="Web Application")
risk_info = gen.calculate_risk_score(vulnerabilities)
# -> {"score": 8.5, "level": "High"}
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

Multi-day test, state kept across sessions via `--subsystem "Customer A"` on the storage scripts (see Integration above), report on day 3:

```bash
nmap -sV -p- 192.168.1.0/24 -oX day1_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py --xml-file day1_scan.xml --subsystem "Customer A"
sqlmap -u "https://customer-a.com/login?id=1" --batch
python ../exploit-sqli/scripts/sqli_storage.py --host-ip 192.168.1.100 \
  --url "https://customer-a.com/login?id=1" --parameter id --subsystem "Customer A"
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
gen.generate_markdown_report('customer_a_report.md', 'Customer A')
"
```

### Scenario 2: Multi-Subsystem Organization

Same storage-script pattern with a different `--subsystem` per network segment (`DMZ`, `Internal`, `Cloud`), then one report per subsystem — or one comprehensive report with no `subsystem` argument:

```bash
nmap -sV -p- 10.0.0.0/24 -oX dmz_scan.xml
python ../recon-port-scan/scripts/port_scan_storage.py --xml-file dmz_scan.xml --subsystem "DMZ"
# repeat for 192.168.1.0/24 ("Internal") and 10.1.0.0/24 ("Cloud")
python -c "
from scripts.report_generator import ReportGenerator
gen = ReportGenerator()
for s in ('DMZ', 'Internal', 'Cloud'):
    gen.generate_markdown_report(f'{s.lower()}_report.md', s)
gen.generate_markdown_report('full_report.md')
"
```

### Scenario 3: Vulnerability Querying

Find all Critical vulnerabilities across all hosts with the first query in "Querying findings" above, then print each result's id, title, host, type, CVSS, and discovery date.

### Scenario 4: Flat Hierarchy Usage

No subsystem — storage scripts run without `--subsystem`, and inserts use the Quick Start pattern with `subsystem_id` NULL (host insert + vulnerability + web-finding rows as in Quick Start).

### Scenario 5: Host-Based Investigation

Deep dive into one host: fetch its host row (LEFT JOIN subsystems for the name), its open ports ordered by port, and its vulnerabilities with web-finding details ordered by CVSS desc (SQL in "Querying findings" / `execute_query` above), then print IP, hostname, OS fingerprint, open-port count, vulnerability count, and each finding's severity + title, then list open ports as `port/protocol: service (state)`.

### Scenario 6: Custom Queries

Query for specific vulnerability patterns by composing the builders from "Querying findings": web vulns in one subsystem (`.by_subsystem(...).by_type("xss", "sqli", "lfi", "ssrf", "xxe")`), high-severity SQLi across all subsystems (`.by_type("sqli").by_severity("High", "Critical")`), or vulnerabilities for one host (`.by_host("192.168.1.100")`).

## Report Customization

Markdown reports include: Executive Summary, Methodology, Detailed Findings (by severity), Host Inventory, Recommendations, Appendices. JSON reports carry `metadata` (report_date, test_period, testers), `executive_summary` (risk_score, total_vulnerabilities, severity_breakdown), `subsystems`, `hosts`, `vulnerabilities`, `recommendations`.

## Data Management

- **Location**: `./data/results.db`
- **Backup**: `cp ./data/results.db ./data/results_backup_$(date +%Y%m%d).db`; encrypted: `gpg --cipher-algo AES256 --compress-algo 1 --symmetric ./data/results.db`
- **Export/Import**: `sqlite3 ./data/results.db .dump > results_backup.sql` / `sqlite3 ./data/results.db < results_backup.sql`
- **Reset** (CAUTION: deletes all data): `rm ./data/results.db` — recreated on next use.

## Performance Considerations

Tested with 10,000+ vulnerabilities; filtered queries < 1s; full report with 1,000+ vulnerabilities < 10s. Indexes auto-created for common query patterns.

## Security Considerations

- Database created 600 (owner read/write only); data dir 700. PoC code lives in the DB — encrypt for production.
- Best practices: back up after each session, keep filesystem permissions restrictive, encrypt backups in shared locations, follow retention policies (delete when no longer needed). All timestamps UTC. Supports OWASP Testing Guide v4.2, PTES, OSSTMM.

## Troubleshooting

- **Database locked**: `lsof ./data/results.db`, then `kill -9 <PID>` if needed.
- **Import errors**: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`; verify with `python -c "from scripts.db_manager import ResultsDatabase; print(ResultsDatabase().get_schema_version())"`.
- **Report errors**: `pip install jinja2`; verify `ls -lh ./data/results.db`.

## Related Skills

`recon-port-scan`, `recon-subdomain`, `exploit-sqli`, `exploit-xss`, `exploit-lfi` — all with storage integration.

## Advanced Usage

### Programmatic Access

```python
import sqlite3

conn = sqlite3.connect('./data/results.db')
cursor = conn.cursor()
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

Batch-insert vulnerabilities: resolve each `host_id` first (`INSERT OR IGNORE INTO hosts`, then `SELECT id`), collect rows, and insert with one `conn.executemany` + `conn.commit()` — same shape as the port-scan `execute_many` in Methods above, with columns `(host_id, vulnerability_type, severity, title, cwe_id, discovered_by_skill)`.

---

*Foundation for persistent, organized penetration testing data management across all pentest-skills capabilities.*
