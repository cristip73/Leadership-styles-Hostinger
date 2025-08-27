#!/bin/sh

# Database seeding script for Dokploy deployment
# Copies seed database to volume mount location on first run

TARGET_DB="${DATABASE_PATH:-/app/data/assessment.db}"
SEED_DB="/app/seed/assessment.db"

echo "Database seeding check..."
echo "Target: $TARGET_DB"

# Create target directory if it doesn't exist
TARGET_DIR=$(dirname "$TARGET_DB")
mkdir -p "$TARGET_DIR"

# Check if target database exists and has content
if [ ! -f "$TARGET_DB" ] || [ ! -s "$TARGET_DB" ]; then
    echo "Database not found or empty at $TARGET_DB"
    
    # Check if seed database exists
    if [ -f "$SEED_DB" ]; then
        echo "Copying seed database from $SEED_DB to $TARGET_DB"
        cp "$SEED_DB" "$TARGET_DB"
        echo "Database seeded successfully!"
    else
        echo "Warning: Seed database not found at $SEED_DB"
        echo "Application will create new empty database"
    fi
else
    echo "Database already exists at $TARGET_DB, skipping seed"
fi

echo "Database seeding check complete"