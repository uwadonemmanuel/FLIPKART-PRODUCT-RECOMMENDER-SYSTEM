#!/usr/bin/env python3
"""
Retry script for failed package downloads.
Reads failed_packages.txt and retries downloading those packages.
"""

import sys
import json
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl

# Import functions from main download script
from download_packages import (
    DOWNLOAD_DIR,
    MAX_RETRIES,
    RETRY_DELAY,
    CHUNK_SIZE,
    CP_TAG,
    PLATFORM_TAG,
    ALT_PLATFORM_TAGS,
    create_ssl_context,
    get_package_info,
    find_best_wheel,
    download_file
)

def parse_failed_packages_file(failed_file):
    """Parse failed_packages.txt to get list of packages to retry."""
    packages = []
    if not failed_file.exists():
        print(f"❌ Failed packages file not found: {failed_file}")
        return packages
    
    with open(failed_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Extract package name and version
            if '==' in line:
                # Remove inline comments
                package_line = line.split('#')[0].strip()
                if '==' in package_line:
                    name, version = package_line.split('==', 1)
                    version = version.strip().rstrip('.')  # Remove trailing dots
                    packages.append((name.strip(), version))
            else:
                # No version specified
                package_line = line.split('#')[0].strip()
                packages.append((package_line, None))
    
    return packages

def retry_package(package_name, version=None):
    """Retry downloading a single package."""
    print(f"🔄 Retrying: {package_name}" + (f"=={version}" if version else ""))
    
    # Get package info from PyPI
    package_info = get_package_info(package_name)
    if not package_info:
        print(f"  ❌ Could not fetch package information")
        return False, "Could not fetch package information"
    
    # Determine version - try exact first, then normalized
    original_version = version
    if version is None:
        version = package_info['info']['version']
    else:
        # Normalize version (remove trailing dots/spaces)
        version = version.strip().rstrip('.')
        
        # Check if exact version exists, if not try normalized
        releases = package_info.get('releases', {})
        if version not in releases:
            # Try without post-release suffix
            if '.post' in version:
                base_version = version.split('.post')[0]
                if base_version in releases:
                    version = base_version
            # Try with .post0 format
            elif not version.endswith('.post0'):
                post_version = f"{version}.post0"
                if post_version in releases:
                    version = post_version
            # Try fuzzy matching
            if version not in releases:
                version_base = version.split('.post')[0] if '.post' in version else version
                for release_version in sorted(releases.keys(), reverse=True):
                    if release_version.startswith(version_base):
                        version = release_version
                        break
    
    # Find best wheel file
    wheel = find_best_wheel(package_info, version)
    if not wheel:
        # Try with latest version as fallback
        latest_version = package_info['info']['version']
        if latest_version != version:
            print(f"  ⚠️  Version {original_version or version} not found, trying latest: {latest_version}")
            wheel = find_best_wheel(package_info, latest_version)
            if wheel:
                version = latest_version
        
        if not wheel:
            print(f"  ❌ No suitable wheel file found for {package_name} {original_version or version}")
            # List available versions for debugging
            releases = package_info.get('releases', {})
            if releases:
                available_versions = sorted(releases.keys(), reverse=True)[:5]
                print(f"  💡 Available versions: {', '.join(available_versions)}")
            return False, "No suitable wheel file found"
    
    filename = wheel['filename']
    url = wheel['url']
    filepath = DOWNLOAD_DIR / filename
    
    # Note if it's a source distribution
    if filename.endswith('.tar.gz'):
        print(f"  ℹ️  Note: Downloading source distribution (no wheel available)")
    
    # Check if already downloaded
    if filepath.exists():
        file_size = filepath.stat().st_size
        expected_size = wheel.get('size', 0)
        if expected_size > 0 and file_size == expected_size:
            print(f"  ✅ Already downloaded: {filename}")
            return True, "already downloaded"
        else:
            print(f"  ⚠️  Incomplete file found, will resume: {filename}")
    
    # Download the file
    print(f"  📥 Downloading: {filename}")
    success, message = download_file(url, filepath, resume=True)
    
    if success:
        print(f"  ✅ {message.capitalize()}")
        return True, message
    else:
        print(f"  ❌ {message}")
        return False, message

def main():
    """Main retry function."""
    print("=" * 70)
    print("🔄 Retry Failed Package Downloads")
    print("=" * 70)
    print()
    
    failed_file = Path("failed_packages.txt")
    
    if not failed_file.exists():
        print(f"❌ Failed packages file not found: {failed_file}")
        print("   Run download_packages.py first to generate this file.")
        return 1
    
    # Parse failed packages
    packages = parse_failed_packages_file(failed_file)
    
    if not packages:
        print("✅ No failed packages found in failed_packages.txt")
        print("   All packages may have been successfully downloaded!")
        return 0
    
    print(f"📦 Found {len(packages)} failed package(s) to retry\n")
    
    # Track statistics
    stats = {
        'total': len(packages),
        'success': 0,
        'failed': 0,
        'already_downloaded': 0
    }
    
    # Retry each package
    for idx, (package_name, version) in enumerate(packages, 1):
        print(f"[{idx}/{stats['total']}] ", end='')
        success, message = retry_package(package_name, version)
        
        if success:
            if "already downloaded" in message.lower():
                stats['already_downloaded'] += 1
            else:
                stats['success'] += 1
        else:
            stats['failed'] += 1
        
        print()
    
    # Print summary
    print("=" * 70)
    print("📊 Retry Summary")
    print("=" * 70)
    print(f"Total packages:     {stats['total']}")
    print(f"✅ Success:          {stats['success']}")
    print(f"✅ Already exists:   {stats['already_downloaded']}")
    print(f"❌ Still failed:     {stats['failed']}")
    print("=" * 70)
    
    if stats['failed'] == 0:
        print("\n🎉 All packages downloaded successfully!")
        print(f"\nTo install all packages, run:")
        print(f"  pip install {DOWNLOAD_DIR}/*.whl")
        
        # Optionally remove failed_packages.txt
        try:
            failed_file.unlink()
            print(f"\n✅ Removed {failed_file} (all packages downloaded)")
        except:
            pass
        
        return 0
    else:
        print(f"\n⚠️  {stats['failed']} package(s) still failed.")
        print("   You can run this script again to retry.")
        print("   Or check the error messages above for details.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Retry interrupted by user.")
        print("You can re-run this script to continue.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

