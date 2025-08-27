#!/bin/sh

# Database seeding script for Dokploy deployment
# Copies seed database to volume mount location on first run

TARGET_DB="${DATABASE_PATH:-/app/data/assessment.db}"
SEED_DB="/app/seed/assessment.db"
MIN_SIZE=40000  # 40KB threshold - empty DB with schema is ~20KB, populated is ~53KB

echo "Database seeding check..."
echo "Target: $TARGET_DB"
echo "Seed: $SEED_DB"

# Create target directory if it doesn't exist
TARGET_DIR=$(dirname "$TARGET_DB")
mkdir -p "$TARGET_DIR"

# Check if seed database exists
if [ ! -f "$SEED_DB" ]; then
    echo "ERROR: Seed database not found at $SEED_DB"
    echo "Application will create new empty database"
    exit 0
fi

# Get seed database size for reference
SEED_SIZE=$(stat -c%s "$SEED_DB" 2>/dev/null || stat -f%z "$SEED_DB" 2>/dev/null || echo 0)
echo "Seed database size: $SEED_SIZE bytes"

# Check if target database needs seeding
if [ ! -f "$TARGET_DB" ]; then
    echo "Target database not found, will seed"
    NEEDS_SEED=1
else
    # Get target database size
    TARGET_SIZE=$(stat -c%s "$TARGET_DB" 2>/dev/null || stat -f%z "$TARGET_DB" 2>/dev/null || echo 0)
    echo "Existing database size: $TARGET_SIZE bytes"
    
    if [ "$TARGET_SIZE" -lt "$MIN_SIZE" ]; then
        echo "Existing database is too small (< $MIN_SIZE bytes), likely empty"
        NEEDS_SEED=1
    else
        echo "Database appears to have data, skipping seed"
        NEEDS_SEED=0
    fi
fi

# Perform seeding if needed
if [ "$NEEDS_SEED" = "1" ]; then
    echo "Copying seed database..."
    cp "$SEED_DB" "$TARGET_DB"
    echo "Database seeded successfully!"
    
    # Verify copy
    NEW_SIZE=$(stat -c%s "$TARGET_DB" 2>/dev/null || stat -f%z "$TARGET_DB" 2>/dev/null || echo 0)
    echo "New database size: $NEW_SIZE bytes"
else
    echo "Database seeding not needed"
fi

echo "Database seeding check complete"