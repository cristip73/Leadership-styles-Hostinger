# SQLite with Dokploy - Quick Setup Guide

## Core Problem
Volume mounts in Dokploy **override** Docker image contents. If your SQLite database is at `/app/data/app.db` and you mount a volume there, your database becomes invisible.

## Solution

### 1. Environment Variables
```bash
DATABASE_PATH=/app/data/app.db
NIXPACKS_START_CMD=gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
NIXPACKS_PYTHON_VERSION=3.11
```

### 2. Volume Configuration
- **Type**: Volume Mount
- **Mount Name**: `app-sqlite`
- **Mount Path**: `/app/data`

### 3. Database Initialization

#### Option A: Simple (New Projects)
Let SQLite create the database automatically via your app's `CREATE TABLE IF NOT EXISTS` statements.

#### Option B: With Seed Data (Existing Data)
```bash
# Structure
/seed/app.db     # Seed database (different path!)
/data/app.db     # Runtime database (volume mount)
```

Create `seed_db.sh`:
```bash
#!/bin/sh
TARGET_DB="${DATABASE_PATH:-/app/data/app.db}"
SEED_DB="/app/seed/app.db"

mkdir -p $(dirname "$TARGET_DB")
if [ ! -f "$TARGET_DB" ]; then
    cp "$SEED_DB" "$TARGET_DB"
    echo "Database seeded"
fi
```

Update start command:
```bash
NIXPACKS_START_CMD=sh seed_db.sh && gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

### 4. Python Code Example
```python
import os

class Database:
    def __init__(self):
        # Use env var in production, local path in development
        self.db_path = os.environ.get('DATABASE_PATH', 'data/app.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
```

## Key Learnings

### ✅ DO:
- Keep seed databases in `/app/seed/` (not masked by volume)
- Use environment variables for database paths
- Use `CREATE TABLE IF NOT EXISTS` for schema
- Check file size, not just existence (empty DB ≠ no file)

### ❌ DON'T:
- Put database in same path as volume mount
- Use `$PORT` variable (use fixed port like 8000)
- Run DROP TABLE in production
- Keep production data in Git

## Adding New Tables (Migrations)
```python
def init_db(self):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY,
            data TEXT
        )
    ''')
```
Safe to run multiple times - won't affect existing data.

## Debugging
```bash
# Check database in container (Python method)
docker exec [container-id] python -c "
import sqlite3
conn = sqlite3.connect('/app/data/app.db')
print('Tables:', conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall())
"
```

## TL;DR
1. Mount volume at `/app/data`
2. Set `DATABASE_PATH=/app/data/app.db`
3. Keep seed files at `/app/seed/` if needed
4. Deploy

---

*Volume mounts hide Docker image files - always use different paths for seeds!*