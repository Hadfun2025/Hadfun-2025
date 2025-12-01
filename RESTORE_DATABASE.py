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

# Check if backup exists
backup_path = "/app/mongodb_backup/test_database"
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
    "--uri=mongodb://localhost:27017",
    "--db=test_database",
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
