# 🗄️ SQLite Database Persistence in Dokploy - Complete Guide

**Based on real-world deployment experience with Flask/Gunicorn/SQLite**  
**Last Updated**: August 27, 2025

---

## 🚨 The Problem

When deploying SQLite-based applications to Dokploy, your database file gets **overwritten by an empty volume mount**, resulting in 0 records in production despite having data in your repository.

### Why This Happens:
1. Docker image contains your database at `/app/data/assessment.db`
2. Dokploy mounts persistent volume at `/app/data`
3. **Volume mount masks the image files** - your DB becomes invisible
4. SQLite creates a new empty database in the mounted volume

---

## ✅ The Solution: Database Seeding Strategy

### Project Structure:
```
your-app/
├── seed/
│   └── assessment.db      # Seed database (in Git)
├── data/
│   └── assessment.db      # Runtime database (ignored in Git)
├── database.py             # Database connection with auto-seeding
├── seed_db.sh             # Production seeding script
└── .gitignore             # Excludes data/ and *.db
```

---

## 📋 Step-by-Step Setup Guide

### 1. **Prepare Your Code**

#### database.py - Add auto-seeding for development:
```python
import os
import shutil

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.environ.get('DATABASE_PATH', 'data/assessment.db')
            
            # Auto-seed for dev environment
            if not os.path.exists(db_path) and os.path.exists('seed/assessment.db'):
                os.makedirs('data', exist_ok=True)
                shutil.copy2('seed/assessment.db', db_path)
                print(f"Database initialized from seed")
        
        self.db_path = db_path
        # ... rest of your database code
```

#### seed_db.sh - Production seeding script:
```bash
#!/bin/sh
TARGET_DB="${DATABASE_PATH:-/app/data/assessment.db}"
SEED_DB="/app/seed/assessment.db"
MIN_SIZE=40000  # Empty DB ~20KB, populated ~50KB+

echo "Database seeding check..."
mkdir -p $(dirname "$TARGET_DB")

if [ ! -f "$TARGET_DB" ] || [ $(stat -c%s "$TARGET_DB" 2>/dev/null || echo 0) -lt "$MIN_SIZE" ]; then
    echo "Seeding database..."
    cp "$SEED_DB" "$TARGET_DB"
    echo "Database seeded successfully!"
else
    echo "Database exists, skipping seed"
fi
```

#### .gitignore:
```gitignore
# Database files
data/
*.db
!seed/*.db  # Keep seed database in Git
```

### 2. **Dokploy Configuration**

#### Environment Variables:
```bash
# Database path
DATABASE_PATH=/app/data/assessment.db

# Start command with seeding
NIXPACKS_START_CMD=sh seed_db.sh && gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app

# Other settings
NIXPACKS_PYTHON_VERSION=3.11
SECRET_KEY=your-secret-key
```

#### Volume Configuration:
- **Type**: Volume Mount
- **Mount Name**: `your-app-sqlite` 
- **Mount Path**: `/app/data`
- **Purpose**: Persistent database storage

#### Domain Settings:
- **Container Port**: `8000` (must match gunicorn bind port)

### 3. **Initial Deployment**

```bash
# 1. Create seed database with initial data
mkdir seed
cp data/assessment.db seed/assessment.db  # Or create new one

# 2. Temporarily include in Git
git add seed/assessment.db seed_db.sh
git commit -m "Add database seeding infrastructure"
git push

# 3. Deploy in Dokploy
# The seed script will copy database on first run
```

### 4. **After Successful Deployment**

```bash
# Restore .gitignore to exclude runtime databases
echo "*.db" >> .gitignore
echo "data/" >> .gitignore
git add .gitignore
git commit -m "Exclude runtime databases from Git"
git push
```

---

## 🎓 Key Lessons Learned

### 1. **Volume Mounts Override Image Contents**
- ❌ Files in Docker image at `/app/data` get hidden by volume mount
- ✅ Solution: Keep seed files in different path (`/app/seed`)

### 2. **File Existence != Has Data**
- ❌ Checking `-f` or `-s` isn't enough - empty SQLite DB with schema has size > 0
- ✅ Solution: Check file size threshold (empty ~20KB, populated 50KB+)

### 3. **Development vs Production Paths**
- ✅ Dev: Auto-copy from `seed/` to `data/` on first run
- ✅ Prod: Use `DATABASE_PATH` env var pointing to volume mount

### 4. **Safe Schema Migrations**
- ✅ Use `CREATE TABLE IF NOT EXISTS` - safe to run multiple times
- ✅ New tables can be added without data loss
- ❌ Never use DROP TABLE in production

### 5. **Debugging in Containers**
- SQLite CLI often not available in containers
- Use Python to inspect: `python -c "import sqlite3; ..."`
- Or install: `apt-get update && apt-get install sqlite3`

---

## 🔧 Common Issues & Solutions

### Issue: "Database already exists, skipping seed" but still 0 records
**Cause**: Empty database from previous failed deployment  
**Fix**: Check file size, not just existence

### Issue: "Bad Gateway" after deployment
**Cause**: Wrong port configuration  
**Fix**: Use fixed port `8000`, not `$PORT` variable

### Issue: Can't verify database in container
**Cause**: No sqlite3 installed  
**Fix**: Use Python to check:
```python
docker exec [container-id] python -c "
import sqlite3
conn = sqlite3.connect('/app/data/assessment.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print('Users:', cursor.fetchone()[0])
"
```

---

## 📚 Quick Reference

### File Locations:
- **Seed DB**: `/app/seed/assessment.db` (in image)
- **Runtime DB**: `/app/data/assessment.db` (in volume)
- **Dev DB**: `data/assessment.db` (local)

### Environment Variables:
```bash
DATABASE_PATH=/app/data/assessment.db
NIXPACKS_START_CMD=sh seed_db.sh && gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:app
```

### Volume Mount:
- **Path in Container**: `/app/data`
- **Persistent**: Yes
- **Survives Redeploy**: Yes

---

## ✨ Best Practices

1. **Always backup before migrations**: `cp database.db backup-$(date +%Y%m%d).db`
2. **Test migrations locally first**
3. **Keep seed database small** (only essential data)
4. **Version your schema changes** (consider migration system for complex apps)
5. **Monitor first deployment** - check logs for seeding confirmation

---

## 🚀 TL;DR - Quick Setup

1. Move your DB to `seed/` folder
2. Create `seed_db.sh` script that copies DB if missing
3. Configure Dokploy:
   - Volume: `/app/data`
   - Env: `DATABASE_PATH=/app/data/assessment.db`
   - Start: `sh seed_db.sh && gunicorn ...`
4. Deploy and verify data exists

**Remember**: Volume mounts hide image files - always seed from a different path!

---

**Created from real deployment experience** | **Tested and working in production**