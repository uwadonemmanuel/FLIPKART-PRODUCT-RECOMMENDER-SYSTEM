#!/usr/bin/env python3
"""
Remove incompatible wheel files from downloads directory.
Checks Python version compatibility and removes wheels that won't work.
"""

import sys
import os
import re
import platform
from pathlib import Path

DOWNLOAD_DIR = Path("downloads")

# Platform detection
SYSTEM = platform.system().lower()
MACHINE = platform.machine().lower()

# Determine platform tags
if SYSTEM == "darwin":  # macOS
    if MACHINE == "arm64" or MACHINE == "aarch64":
        PLATFORM_TAG = "arm64"
        INCOMPATIBLE_PLATFORMS = ["x86_64", "amd64"]
    else:  # x86_64
        PLATFORM_TAG = "x86_64"
        INCOMPATIBLE_PLATFORMS = ["arm64", "aarch64"]
elif SYSTEM == "linux":
    PLATFORM_TAG = MACHINE
    INCOMPATIBLE_PLATFORMS = ["arm64"] if MACHINE == "x86_64" else ["x86_64", "amd64"]
else:
    PLATFORM_TAG = None
    INCOMPATIBLE_PLATFORMS = []

def is_compatible_wheel(filename, python_major, python_minor):
    """Check if a wheel file is compatible with the current Python version and platform."""
    # Universal wheels are always compatible
    if 'none-any' in filename:
        return True
    
    # Check platform compatibility
    if PLATFORM_TAG:
        # Universal2 wheels (macOS) work on both arm64 and x86_64
        if 'universal2' in filename:
            return True
        
        # Check for incompatible platform tags (but allow if universal2 is also present)
        for incompatible_platform in INCOMPATIBLE_PLATFORMS:
            if incompatible_platform in filename and 'universal2' not in filename:
                return False
    
    # Extract Python version tags from filename
    # Patterns: cp312, cp313, cp37-abi3, py3, py2.py3
    py_tags = re.findall(r'(cp\d+(?:-abi\d+)?|py\d+|py\d+\.py\d+)', filename)
    
    if not py_tags:
        # No Python version tag, assume compatible
        return True
    
    cp_tag = f"cp{python_major}{python_minor}"
    
    for tag in py_tags:
        # Exact match
        if cp_tag in tag:
            return True
        
        # Universal Python tags
        if 'py3' in tag or 'py2.py3' in tag:
            return True
        
        # Stable ABI wheels (cp37-abi3, cp38-abi3, etc.)
        if '-abi' in tag:
            match = re.search(r'cp(\d)(\d)', tag)
            if match:
                wheel_major = int(match.group(1))
                wheel_minor = int(match.group(2))
                # Stable ABI wheels work if wheel version <= current Python version
                if (wheel_major < python_major) or (wheel_major == python_major and wheel_minor <= python_minor):
                    return True
    
    # Check if it's for a different Python version
    for tag in py_tags:
        if tag.startswith('cp'):
            # Extract version
            match = re.search(r'cp(\d)(\d)', tag)
            if match:
                wheel_major = int(match.group(1))
                wheel_minor = int(match.group(2))
                # If it's for a different Python version and not stable ABI, it's incompatible
                if '-abi' not in tag:
                    if wheel_major != python_major or wheel_minor != python_minor:
                        return False
    
    # If we can't determine, assume compatible (better to keep than delete)
    return True

def main():
    """Main function to clean incompatible wheels."""
    print("=" * 70)
    print("🧹 Cleaning Incompatible Wheel Files")
    print("=" * 70)
    
    python_major = sys.version_info.major
    python_minor = sys.version_info.minor
    cp_tag = f"cp{python_major}{python_minor}"
    
    print(f"Python version: {python_major}.{python_minor}")
    print(f"Target tag: {cp_tag}")
    print(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    print()
    
    if not DOWNLOAD_DIR.exists():
        print(f"❌ Download directory not found: {DOWNLOAD_DIR}")
        return 1
    
    # Find all wheel files
    wheel_files = list(DOWNLOAD_DIR.glob("*.whl"))
    
    if not wheel_files:
        print("✅ No wheel files found in downloads directory")
        return 0
    
    print(f"📦 Found {len(wheel_files)} wheel file(s)\n")
    
    incompatible = []
    compatible = []
    
    for wheel_file in wheel_files:
        filename = wheel_file.name
        if is_compatible_wheel(filename, python_major, python_minor):
            compatible.append(wheel_file)
        else:
            incompatible.append(wheel_file)
    
    print(f"✅ Compatible wheels: {len(compatible)}")
    print(f"❌ Incompatible wheels: {len(incompatible)}")
    print()
    
    if incompatible:
        print("Incompatible wheels to be removed:")
        for wheel_file in incompatible:
            print(f"  ❌ {wheel_file.name}")
        print()
        
        # Ask for confirmation (in automated mode, just proceed)
        print("Removing incompatible wheels...")
        removed_count = 0
        for wheel_file in incompatible:
            try:
                wheel_file.unlink()
                print(f"  🗑️  Removed: {wheel_file.name}")
                removed_count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to remove {wheel_file.name}: {e}")
        
        print()
        print(f"✅ Removed {removed_count} incompatible wheel file(s)")
    else:
        print("✅ All wheel files are compatible!")
    
    print()
    print("=" * 70)
    print(f"📊 Summary")
    print("=" * 70)
    print(f"Total wheels:        {len(wheel_files)}")
    print(f"✅ Compatible:        {len(compatible)}")
    print(f"❌ Removed:           {len(incompatible)}")
    print("=" * 70)
    
    if len(compatible) > 0:
        print(f"\n✅ You can now run: pip install downloads/*.whl")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

