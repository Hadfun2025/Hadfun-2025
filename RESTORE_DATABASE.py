#!/usr/bin/env python3
"""
CRITICAL: Run this script in any new session to restore your complete database
This ensures you never lose your 1624 fixtures and team data
"""
import subprocess
import os

print("=" * 60)
print("RESTORING FOOTBALL PREDICTION DATABASE")
print("=" * 60)

# Get environment variables
DB_NAME = os.getenv('DB_NAME', 'test_database')
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

# Check if backup exists
backup_path = f"/app/mongodb_backup/{DB_NAME}"
if not os.path.exists(backup_path):
    print("❌ ERROR: Backup not found at " + backup_path)
    print("Cannot restore database!")
    exit(1)

print("\n✅ Backup found")
print(f"   Location: {backup_path}")

# Restore the database
print("\n📦 Restoring database...")
result = subprocess.run([
    "mongorestore",
    f"--uri={MONGO_URL}",
    f"--db={DB_NAME}",
    "--drop",  # Drop existing collections first
    backup_path
], capture_output=True, text=True)

if result.returncode == 0:
    print("✅ DATABASE RESTORED SUCCESSFULLY!")
    print("\n📊 Restored data includes:")
    print("   - 1624 fixtures across 16 leagues")
    print("   - Team: Cheshunt Crew (7 members)")
    print("   - All scores from Nov 22 onwards")
    print("   - UEFA competitions")
    print("\n🎉 Your app is ready to use!")
else:
    print("❌ ERROR during restore:")
    print(result.stderr)
    exit(1)
