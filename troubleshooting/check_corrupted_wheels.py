#!/usr/bin/env python3
"""Check for corrupted wheel files and remove them."""

import zipfile
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")

def main():
    print("=" * 70)
    print("🔍 Checking for Corrupted Wheel Files")
    print("=" * 70)
    print()
    
    if not DOWNLOAD_DIR.exists():
        print(f"❌ Download directory not found: {DOWNLOAD_DIR}")
        return 1
    
    wheel_files = list(DOWNLOAD_DIR.glob("*.whl"))
    
    if not wheel_files:
        print("✅ No wheel files found")
        return 0
    
    print(f"📦 Checking {len(wheel_files)} wheel file(s)...\n")
    
    corrupted = []
    valid = []
    
    for wheel_file in wheel_files:
        try:
            if zipfile.is_zipfile(wheel_file):
                # Try to open it to verify it's not corrupted
                with zipfile.ZipFile(wheel_file, 'r') as zf:
                    zf.testzip()  # This will raise an exception if corrupted
                valid.append(wheel_file)
            else:
                corrupted.append(wheel_file)
        except Exception as e:
            corrupted.append(wheel_file)
            print(f"  ❌ {wheel_file.name}: {e}")
    
    print(f"\n✅ Valid wheels: {len(valid)}")
    print(f"❌ Corrupted wheels: {len(corrupted)}")
    
    if corrupted:
        print("\nRemoving corrupted wheels...")
        for wheel_file in corrupted:
            try:
                wheel_file.unlink()
                print(f"  🗑️  Removed: {wheel_file.name}")
            except Exception as e:
                print(f"  ⚠️  Failed to remove {wheel_file.name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Summary")
    print("=" * 70)
    print(f"Total wheels:        {len(wheel_files)}")
    print(f"✅ Valid:             {len(valid)}")
    print(f"❌ Removed:            {len(corrupted)}")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

