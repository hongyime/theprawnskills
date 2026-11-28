---
name: database-schema-designer
description: >-
  When to read: designing a database schema, normalizing tables, or planning indexes/migrations.
  Use for: designing robust, scalable database schemas for SQL and NoSQL. Does: covers
  normalization, indexing, migration patterns, constraints, and performance for Postgres, MySQL,
  and MongoDB.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Database Schema Designer

Design production-ready database schemas with best practices built-in.

---

## Quick Start

Just describe your data model:

```
design a schema for an e-commerce platform with users, products, orders
```

You'll get a complete SQL schema like:

```sql
CREATE TABLE users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  total DECIMAL(10,2) NOT NULL,
  INDEX idx_orders_user (user_id)
);
```

**What to include in your request:**
- Entities (users, products, orders)
- Key relationships (users have orders, orders have items)
- Scale hints (high-traffic, millions of records)
- Database preference (SQL/NoSQL) - defaults to SQL if not specified

---

## Triggers

`design schema`, `database design`, `create tables`, `schema for`, `model data`, `I need a database`, `design NoSQL`.

---

---

---

## Process Overview

1. **ANALYSIS** — entities, relationships, access patterns; SQL vs NoSQL
2. **DESIGN** — normalize to 3NF (SQL) / embed-reference (NoSQL); PKs, FKs, types, constraints
3. **OPTIMIZE** — indexing, denormalization for read-heavy queries, timestamps
4. **MIGRATE** — reversible up/down scripts, backward compatible, zero-downtime

---

## Commands

| Command | When to Use | Action |
|---------|-------------|--------|
| `design schema for {domain}` | Starting fresh | Full schema generation |
| `normalize {table}` | Fixing existing table | Apply normalization rules |
| `add indexes for {table}` | Performance issues | Generate index strategy |
| `migration for {change}` | Schema evolution | Create reversible migration |
| `review schema` | Code review | Audit existing schema |

**Workflow:** Start with `design schema` → iterate with `normalize` → optimize with `add indexes` → evolve with `migration`

---

## Core Principles

| Principle | WHY | Implementation |
|-----------|-----|----------------|
| Model the Domain | UI changes, domain doesn't | Entity names reflect business concepts |
| Data Integrity First | Corruption is costly to fix | Constraints at database level |
| Optimize for Access Pattern | Can't optimize for both | OLTP: normalized, OLAP: denormalized |
| Plan for Scale | Retrofitting is painful | Index strategy + partitioning plan |

---

## Anti-Patterns

| Avoid | Why | Instead |
|-------|-----|---------|
| VARCHAR(255) everywhere | Wastes storage, hides intent | Size appropriately per field |
| Storing dates as strings | Can't compare/sort | DATE, TIMESTAMP types |
| SELECT * in queries | Fetches unnecessary data | Explicit column lists |
| Non-reversible migrations | Can't rollback | Always write DOWN migration |
| Adding NOT NULL without default | Breaks existing rows | Add nullable, backfill, then constrain |

---

## Verification Checklist

After designing a schema:

- [ ] Every table has a primary key
- [ ] All relationships have foreign key constraints
- [ ] ON DELETE strategy defined for each FK
- [ ] Indexes exist on all foreign keys
- [ ] Indexes exist on frequently queried columns
- [ ] Appropriate data types (DECIMAL for money, etc.)
- [ ] NOT NULL on required fields
- [ ] UNIQUE constraints where needed
- [ ] CHECK constraints for validation
- [ ] created_at and updated_at timestamps
- [ ] Migration scripts are reversible
- [ ] Tested on staging with production data

---

<details>
<summary><strong>Deep Dive: Normalization (SQL)</strong></summary>

### 1st Normal Form (1NF)

```sql
-- BAD: Multiple values in column
CREATE TABLE orders (
  id INT PRIMARY KEY,
  product_ids VARCHAR(255)  -- '101,102,103'
);

-- GOOD: Separate table for items
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT REFERENCES orders(id),
  product_id INT
);
```

### 2nd Normal Form (2NF)

```sql
-- BAD: customer_name depends only on customer_id
CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  customer_name VARCHAR(100),  -- Partial dependency!
  PRIMARY KEY (order_id, product_id)
);

-- GOOD: Customer data in separate table
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name VARCHAR(100)
);
```

### 3rd Normal Form (3NF)

```sql
-- BAD: country depends on postal_code
CREATE TABLE customers (
  id INT PRIMARY KEY,
  postal_code VARCHAR(10),
  country VARCHAR(50)  -- Transitive dependency!
);

-- GOOD: Separate postal_codes table
CREATE TABLE postal_codes (
  code VARCHAR(10) PRIMARY KEY,
  country VARCHAR(50)
);
```

```sql
-- Denormalized for performance
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT,
  total_amount DECIMAL(10,2),  -- Calculated
  item_count INT               -- Calculated
);
```
</details>
<details>
<summary><strong>Deep Dive: Data Types</strong></summary>

```sql
-- Good sizing
email VARCHAR(255)
phone VARCHAR(20)
country_code CHAR(2)
```

```sql
-- ALWAYS use DECIMAL for money
price DECIMAL(10, 2)  -- $99,999,999.99

-- NEVER use FLOAT for money
price FLOAT  -- Rounding errors!
```

### Date/Time Types

```sql
DATE        -- 2025-10-31
TIME        -- 14:30:00
DATETIME    -- 2025-10-31 14:30:00
TIMESTAMP   -- Auto timezone conversion

-- Always store in UTC
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### Boolean

```sql
-- PostgreSQL
is_active BOOLEAN DEFAULT TRUE

-- MySQL
is_active TINYINT(1) DEFAULT 1
```
</details>
<details>
<summary><strong>Deep Dive: Indexing Strategy</strong></summary>

```sql
-- Foreign key index
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Query pattern index
CREATE INDEX idx_orders_status_date ON orders(status, created_at);
```

### Composite Index Order

```sql
CREATE INDEX idx_customer_status ON orders(customer_id, status);

-- Uses index (customer_id first)
SELECT * FROM orders WHERE customer_id = 123;
SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';

-- Does NOT use index (status alone)
SELECT * FROM orders WHERE status = 'pending';
```

**Rule:** Most selective column first, or column most queried alone.
</details>
<details>
<summary><strong>Deep Dive: Constraints</strong></summary>

### Primary Keys

```sql
-- Auto-increment (simple)
id INT AUTO_INCREMENT PRIMARY KEY

-- UUID (distributed systems)
id CHAR(36) PRIMARY KEY DEFAULT (UUID())

-- Composite (junction tables)
PRIMARY KEY (student_id, course_id)
```

### Foreign Keys

```sql
FOREIGN KEY (customer_id) REFERENCES customers(id)
  ON DELETE CASCADE     -- Delete children with parent
  ON DELETE RESTRICT    -- Prevent deletion if referenced
  ON DELETE SET NULL    -- Set to NULL when parent deleted
  ON UPDATE CASCADE     -- Update children when parent changes
```

### Other Constraints

```sql
-- Unique
email VARCHAR(255) UNIQUE NOT NULL

-- Composite unique
UNIQUE (student_id, course_id)

-- Check
price DECIMAL(10,2) CHECK (price >= 0)
discount INT CHECK (discount BETWEEN 0 AND 100)

-- Not null
name VARCHAR(100) NOT NULL
```

</details>
<details>
<summary><strong>Deep Dive: Relationship Patterns</strong></summary>

### One-to-Many

```sql
CREATE TABLE orders (
  id INT PRIMARY KEY,
  customer_id INT NOT NULL REFERENCES customers(id)
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id INT NOT NULL,
  quantity INT NOT NULL
);
```

### Many-to-Many

```sql
-- Junction table
CREATE TABLE enrollments (
  student_id INT REFERENCES students(id) ON DELETE CASCADE,
  course_id INT REFERENCES courses(id) ON DELETE CASCADE,
  enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (student_id, course_id)
);
```

### Self-Referencing

```sql
CREATE TABLE employees (
  id INT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  manager_id INT REFERENCES employees(id)
);
```

### Polymorphic

```sql
-- Approach 1: Separate FKs (stronger integrity)
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  post_id INT REFERENCES posts(id),
  photo_id INT REFERENCES photos(id),
  CHECK (
    (post_id IS NOT NULL AND photo_id IS NULL) OR
    (post_id IS NULL AND photo_id IS NOT NULL)
  )
);

-- Approach 2: Type + ID (flexible, weaker integrity)
CREATE TABLE comments (
  id INT PRIMARY KEY,
  content TEXT NOT NULL,
  commentable_type VARCHAR(50) NOT NULL,
  commentable_id INT NOT NULL
);
```

</details>
<details>
<summary><strong>Deep Dive: NoSQL Design (MongoDB)</strong></summary>

### Embedding vs Referencing

| Factor | Embed | Reference |
|--------|-------|-----------|
| Access pattern | Read together | Read separately |
| Relationship | 1:few | 1:many |
| Document size | Small | Approaching 16MB |
| Update frequency | Rarely | Frequently |

### Embedded Document

```json
{
  "_id": "order_123",
  "customer": {
    "id": "cust_456",
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "items": [
    { "product_id": "prod_789", "quantity": 2, "price": 29.99 }
  ],
  "total": 109.97
}
```

### Referenced Document

```json
{
  "_id": "order_123",
  "customer_id": "cust_456",
  "item_ids": ["item_1", "item_2"],
  "total": 109.97
}
```

### MongoDB Indexes

```javascript
// Single field
db.users.createIndex({ email: 1 }, { unique: true });

// Composite
db.orders.createIndex({ customer_id: 1, created_at: -1 });

// Text search
db.articles.createIndex({ title: "text", content: "text" });

// Geospatial
db.stores.createIndex({ location: "2dsphere" });
```

</details>
<details>
<summary><strong>Deep Dive: Migrations</strong></summary>

### Adding a Column (Zero-Downtime)

```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Step 2: Deploy code that writes to new column

-- Step 3: Backfill existing rows
UPDATE users SET phone = '' WHERE phone IS NULL;

-- Step 4: Make required (if needed)
ALTER TABLE users MODIFY phone VARCHAR(20) NOT NULL;
```

### Renaming a Column (Zero-Downtime)

```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Copy data
UPDATE users SET email_address = email;

-- Step 3: Deploy code reading from new column
-- Step 4: Deploy code writing to new column

-- Step 5: Drop old column
ALTER TABLE users DROP COLUMN email;
```

### Migration Template

```sql
-- Migration: YYYYMMDDHHMMSS_description.sql

-- UP
BEGIN;
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
CREATE INDEX idx_users_phone ON users(phone);
COMMIT;

-- DOWN
BEGIN;
DROP INDEX idx_users_phone ON users;
ALTER TABLE users DROP COLUMN phone;
COMMIT;
```

</details>
<details>
<summary><strong>Deep Dive: Performance Optimization</strong></summary>

### Query Analysis

```sql
EXPLAIN SELECT * FROM orders
WHERE customer_id = 123 AND status = 'pending';
```

### N+1 Query Problem

```python
# BAD: N+1 queries
orders = db.query("SELECT * FROM orders")
for order in orders:
    customer = db.query(f"SELECT * FROM customers WHERE id = {order.customer_id}")

# GOOD: Single JOIN
results = db.query("""
    SELECT orders.*, customers.name
    FROM orders
    JOIN customers ON orders.customer_id = customers.id
""")
```

</details>

