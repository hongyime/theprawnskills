# ResultsDatabase API Reference

Complete API reference for the pentest-skills results-storage system, built
on `ResultsDatabase` (`scripts/db_manager.py`).

> **Note:** the upstream `storage_api.py` wrapper (`StorageAPI`) shipped broken
> (newlines stripped, tokens fused) and could not be imported, so it was
> removed. There are no `store_*` convenience methods. Writes are plain SQL
> through `ResultsDatabase`; reads use `QueryBuilder` / `PredefinedQueries`
> (`scripts/query_builder.py`) or SQL.

## Overview

`ResultsDatabase` is the storage interface. It supports:

- **Database setup** - Creates the schema and manages the connection
- **SQL execution** - `execute_query()` / `execute_many()` / `get_connection()`
- **Maintenance** - Schema version, database info, vacuum, analyze
- **Query builders** - `QueryBuilder`, `VulnerabilityQueryBuilder`,
  `PortScanQueryBuilder`, `PredefinedQueries` (see "Querying")

## Initialization

```python
from scripts.db_manager import ResultsDatabase

db = ResultsDatabase(db_path="./data/results.db")
```

### Parameters

- `db_path` (str, optional) - Path to SQLite database file. Default: `"./data/results.db"`

### Notes

- Database is automatically created if it doesn't exist
- Data directory is created with restrictive permissions (700)
- Database file is created with permissions 600 (owner read/write only)

---

## ResultsDatabase methods

### get_connection()

Get the (cached) SQLite connection. Use as a context manager; it commits
on clean exit and rolls back on exception. Foreign keys are ON, journal
mode is WAL, busy timeout is 5 seconds.

```python
with db.get_connection() as conn:
    conn.execute("INSERT INTO hosts (ip_address) VALUES (?)", ("192.168.1.100",))
    conn.commit()
```

**Returns:**
- `sqlite3.Connection`

### execute_query()

Run one SQL statement.

```python
row = db.execute_query(
    "SELECT id FROM hosts WHERE ip_address = ?", ("192.168.1.100",),
    fetch='one')
rows = db.execute_query(
    "SELECT * FROM vulnerabilities WHERE severity = ?", ("Critical",),
    fetch='all')
cursor = db.execute_query("INSERT INTO hosts (ip_address) VALUES (?)",
                          ("192.168.1.100",))
```

**Parameters:**
- `query` (str, required) - SQL statement
- `params` (tuple, optional) - Query parameters
- `fetch` (str, optional) - `'one'` | `'all'` | `None` (returns cursor)

**Returns:**
- Fetched row(s) when `fetch` is given, else the cursor

**Raises:**
- `sqlite3.Error` - On database errors

### execute_many()

Run one statement many times (batch insert/update). Commits automatically.

```python
count = db.execute_many(
    "INSERT OR REPLACE INTO port_scan_results "
    "(host_id, port, protocol, state, service) VALUES (?, ?, ?, ?, ?)",
    [(host_id, 80, "tcp", "open", "http"),
     (host_id, 443, "tcp", "open", "https")])
```

**Parameters:**
- `query` (str, required) - SQL statement
- `params_list` (list, required) - List of parameter tuples

**Returns:**
- `int` - Row count

### get_schema_version()

```python
db.get_schema_version()  # -> "1.0.0"
```

### get_database_info()

```python
info = db.get_database_info()
# {"path": ..., "schema_version": "1.0.0", "size_bytes": ...,
#  "tables": {"subsystems": n, "hosts": n, ...},
#  "indexes": [{"name": ..., "table": ...}, ...]}
```

### vacuum() / analyze()

```python
db.vacuum()    # reclaim space
db.analyze()   # update query planner statistics
```

### close()

```python
db.close()  # close the connection
```

### Context manager

```python
with ResultsDatabase() as db:
    db.execute_query("SELECT COUNT(*) FROM vulnerabilities", fetch='one')
# Connection automatically closed
```

---

## Storing findings

Writes are SQL against the schema in `scripts/db_manager.py`
(`TABLES_SQL`). Use these get-or-create helpers (copy-pasteable):

```python
def get_or_create_subsystem(conn, name, description="", subnet_range=""):
    conn.execute(
        "INSERT OR IGNORE INTO subsystems (name, description, subnet_range) "
        "VALUES (?, ?, ?)", (name, description, subnet_range))
    return conn.execute(
        "SELECT id FROM subsystems WHERE name = ?", (name,)).fetchone()[0]

def get_or_create_host(conn, ip, subsystem_id=None, hostname=None,
                       os_fingerprint=None):
    conn.execute(
        "INSERT OR IGNORE INTO hosts "
        "(subsystem_id, ip_address, hostname, os_fingerprint) "
        "VALUES (?, ?, ?, ?)", (subsystem_id, ip, hostname, os_fingerprint))
    return conn.execute(
        "SELECT id FROM hosts WHERE ip_address = ? "
        "AND (subsystem_id IS ? OR subsystem_id = ?)",
        (ip, subsystem_id, subsystem_id)).fetchone()[0]
```

### Subsystems

```python
with db.get_connection() as conn:
    subsystem_id = get_or_create_subsystem(
        conn, "Web Application",
        description="Customer A web infrastructure",
        subnet_range="192.168.1.0/24")
    conn.commit()

# List subsystems with host/vuln counts
rows = db.execute_query(
    "SELECT s.id, s.name, s.description, s.subnet_range, s.created_at, "
    "COUNT(DISTINCT h.id) as host_count, COUNT(DISTINCT v.id) as vuln_count "
    "FROM subsystems s "
    "LEFT JOIN hosts h ON s.id = h.subsystem_id "
    "LEFT JOIN vulnerabilities v ON h.id = v.host_id "
    "GROUP BY s.id ORDER BY s.name", fetch='all')
```

### Vulnerabilities

Valid `severity` values: `Critical`, `High`, `Medium`, `Low`, `Info`.
Valid `vulnerability_type` values: `sqli`, `xss`, `lfi`, `rfi`, `ssrf`,
`xxe`, `file_download`, `command_injection`, `csrf`, `open_redirect`,
`path_traversal`, `insecure_deserialization`, `weak_auth`,
`info_disclosure`, `other`.

```python
# Generic vulnerability + web-finding row
with db.get_connection() as conn:
    host_id = get_or_create_host(conn, "192.168.1.100", subsystem_id)
    cur = conn.execute(
        "INSERT INTO vulnerabilities "
        "(host_id, vulnerability_type, severity, title, description, "
        " affected_component, proof_of_concept, cvss_score, cwe_id, cve_id, "
        " discovered_by_skill) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (host_id, "sqli", "Critical", "SQL Injection in Login Page",
         "Authentication bypass via SQL injection in id parameter",
         "/login", "id=1' OR '1'='1", 9.8, "CWE-89", None, "exploit-sqli"))
    vuln_id = cur.lastrowid
    conn.execute(
        "INSERT INTO web_findings "
        "(vulnerability_id, url, parameter, http_method, payload, "
        " response_evidence, context, request_headers) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (vuln_id, "https://example.com/login?id=1", "id", "GET",
         "1' OR '1'='1", None, None, None))
    conn.commit()
```

Type-specific defaults used by the old convenience methods (apply them
when inserting):

| Type | `vulnerability_type` | `cwe_id` | `discovered_by_skill` | Default severity |
|------|----------------------|----------|-----------------------|------------------|
| SQLi | `sqli` | `CWE-89` | `exploit-sqli` | High |
| XSS | `xss` | `CWE-79` | `exploit-xss` | Medium |
| LFI | `lfi` | `CWE-98` | `exploit-lfi` | High |

For XSS, store the `xss_type` (reflected/stored/dom) in the vulnerability
`title` or `description` (for example `"Reflected XSS in Search"`), and the
`context` (`html_body`, `html_attribute`, `javascript`, `dom`, `url`) in the
`web_findings.context` column. For LFI, store the read file content as
`proof_of_concept` and/or `web_findings.response_evidence`.

### Port scan results

```python
db.execute_many(
    "INSERT OR REPLACE INTO port_scan_results "
    "(host_id, port, protocol, state, service, version, product, extra_info, scan_tool) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    [(host_id, 22, "tcp", "open", "ssh", None, None, None, "nmap"),
     (host_id, 80, "tcp", "open", "http", "Apache httpd 2.4.41", "Apache", None, "nmap"),
     (host_id, 443, "tcp", "open", "https", None, None, None, "nmap")])
```

---

## Querying findings

Use the query builders in `scripts/query_builder.py`. All take a
`ResultsDatabase` and return lists of dicts.

### VulnerabilityQueryBuilder

```python
from scripts.query_builder import VulnerabilityQueryBuilder

# All Critical vulnerabilities, critical first
vulns = (VulnerabilityQueryBuilder(db)
    .select("v.id", "v.title", "v.severity", "v.cvss_score",
            "v.vulnerability_type", "v.discovered_at",
            "h.ip_address", "h.hostname")
    .with_host_info()
    .by_severity("Critical")
    .critical_first()
    .execute())
```

**Methods:**
- `.select(*columns)` - Columns to return (required)
- `.with_host_info()` - Join `hosts`
- `.with_subsystem()` - Join `hosts` + `subsystems`
- `.with_web_finding()` - Join `web_findings`
- `.by_severity(*severities)` - Filter by severity level(s)
- `.by_type(*types)` - Filter by vulnerability type(s)
- `.by_host(host_ip)` - Filter by host IP
- `.by_subsystem(name)` - Filter by subsystem name
- `.critical_first()` / `.recent_first()` / `.high_value_first()` - Ordering
- `.where(condition, *params)` / `.where_in(column, values)` /
  `.where_between(column, start, end)` / `.group_by(*cols)` /
  `.having(condition, *params)` / `.order_by(column, direction)` /
  `.limit(n)` / `.offset(n)` - Generic builder methods
- `.execute(fetch="all")` - Run; `fetch` is `'all'` | `'one'`

### PortScanQueryBuilder

```python
from scripts.query_builder import PortScanQueryBuilder

ports = (PortScanQueryBuilder(db)
    .select("psr.port", "psr.protocol", "psr.state", "psr.service")
    .with_host_info()
    .by_host("192.168.1.100")
    .open_ports_only()
    .execute())
```

**Methods:** `.select()`, `.with_host_info()`, `.with_subsystem()`,
`.by_host(ip)`, `.by_state(*states)`, `.by_service(*services)`,
`.by_scan_tool(tool)`, `.open_ports_only()`, plus the generic builder
methods above, `.execute()`.

### PredefinedQueries

```python
from scripts.query_builder import PredefinedQueries

q = PredefinedQueries(db)
q.get_critical_vulnerabilities(limit=10)   # critical vulns, CVSS desc
q.get_vulnerability_by_host()              # vuln counts grouped by host
q.get_exposed_services()                   # open services across hosts
q.get_most_vulnerable_subsystems(limit=10)
q.get_vulnerability_type_trend()
q.get_scan_coverage()
```

---

## Statistics

```python
# Totals + severity breakdown + average CVSS
row = db.execute_query(
    "SELECT COUNT(*) as total, "
    "COUNT(CASE WHEN severity='Critical' THEN 1 END) as critical, "
    "COUNT(CASE WHEN severity='High' THEN 1 END) as high, "
    "COUNT(CASE WHEN severity='Medium' THEN 1 END) as medium, "
    "COUNT(CASE WHEN severity='Low' THEN 1 END) as low, "
    "COUNT(CASE WHEN severity='Info' THEN 1 END) as info, "
    "AVG(cvss_score) as avg_cvss FROM vulnerabilities",
    fetch='one')

# Counts by vulnerability type
rows = db.execute_query(
    "SELECT vulnerability_type, COUNT(*) as count FROM vulnerabilities "
    "GROUP BY vulnerability_type ORDER BY count DESC", fetch='all')
```

`ReportGenerator` (`scripts/report_generator.py`) computes these
statistics internally via `ResultsDatabase` when generating reports.

---

## ReportGenerator

```python
from scripts.report_generator import ReportGenerator

gen = ReportGenerator(db_path="./data/results.db")
gen.generate_markdown_report(output_path="report.md", subsystem="Web Application")
gen.generate_json_report(output_path="report.json", subsystem="Web Application")
summary = gen.generate_executive_summary(subsystem="Web Application")
risk = gen.calculate_risk_score(vulnerabilities)  # {"score": 8.5, "level": "High"}
gen.close()
```

---

## Error Handling

Common exceptions:

- `sqlite3.IntegrityError` - Constraint violation (duplicate subsystem name, etc.)
- `sqlite3.Error` - General database error
- `ValueError` - `QueryBuilder` with no columns (`select()`) or no table

---

For database schema, see `database_schema.md`.

For integration examples, see `integration_examples.md`.
