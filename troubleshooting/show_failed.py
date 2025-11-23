#!/usr/bin/env python3
"""
Quick script to show which packages failed to download.
"""

import sys
from pathlib import Path

failed_file = Path("failed_packages.txt")

if not failed_file.exists():
    print("✅ No failed packages file found.")
    print("   All packages may have been successfully downloaded!")
    sys.exit(0)

print("=" * 70)
print("❌ Failed Packages")
print("=" * 70)
print()

with open(failed_file, 'r') as f:
    lines = f.readlines()
    failed_count = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            failed_count += 1
            print(f"  {failed_count}. {line}")

print()
print("=" * 70)
print(f"Total failed packages: {failed_count}")
print("=" * 70)
print()
print("To retry these packages, run:")
print("  python retry_failed.py")
print()

