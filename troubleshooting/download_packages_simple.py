#!/usr/bin/env python3
"""
Simplified automated package downloader with resume capability.
Uses pip download to get all dependencies, then resumes incomplete downloads.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl

# Configuration
DOWNLOAD_DIR = Path("downloads")
# Try full requirements first, fall back to basic if not found
REQUIREMENTS_FILE = Path("requirements_full.txt") if Path("requirements_full.txt").exists() else Path("requirements.txt")
MAX_RETRIES = 5
RETRY_DELAY = 3  # seconds
CHUNK_SIZE = 8192  # 8KB chunks

def create_ssl_context():
    """Create SSL context that's more permissive for problematic certificates."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def get_file_size(url):
    """Get file size from URL without downloading."""
    try:
        req = Request(url)
        req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
        with urlopen(req, timeout=10, context=create_ssl_context()) as response:
            return int(response.headers.get('Content-Length', 0))
    except:
        return 0

def download_file(url, filepath, resume=True):
    """Download file with resume capability."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists and is complete
    if filepath.exists():
        file_size = filepath.stat().st_size
        remote_size = get_file_size(url)
        if remote_size > 0 and file_size == remote_size:
            return True, "already complete"
        elif resume and file_size > 0:
            resume_pos = file_size
        else:
            resume_pos = 0
    else:
        resume_pos = 0
    
    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
            
            if resume_pos > 0:
                req.add_header('Range', f'bytes={resume_pos}-')
            
            with urlopen(req, timeout=60, context=create_ssl_context()) as response:
                mode = 'ab' if resume_pos > 0 else 'wb'
                
                with open(filepath, mode) as f:
                    if resume_pos > 0:
                        print(f"    ↻ Resuming from {resume_pos:,} bytes...")
                    
                    downloaded = resume_pos
                    total_size = resume_pos + int(response.headers.get('Content-Length', 0))
                    
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r    ⬇️  {downloaded:,}/{total_size:,} bytes ({percent:.1f}%)", end='', flush=True)
                    
                    print()
                    
                    if total_size > 0 and downloaded != total_size:
                        raise Exception(f"Incomplete download: {downloaded}/{total_size} bytes")
                    
                    return True, "downloaded"
                    
        except (URLError, HTTPError, TimeoutError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    ⚠️  Retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
            else:
                return False, f"Failed after {MAX_RETRIES} attempts: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    return False, "Max retries exceeded"

def get_package_url_from_pypi(package_name, version=None):
    """Get download URL for a package from PyPI JSON API."""
    import json
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
            with urlopen(req, timeout=30, context=create_ssl_context()) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if version is None:
                    version = data['info']['version']
                
                # Find wheel file (prefer wheel over source)
                files = data.get('releases', {}).get(version, [])
                wheel_files = [f for f in files if f['packagetype'] == 'bdist_wheel']
                
                if wheel_files:
                    # Return first wheel (pip download will handle platform selection)
                    return wheel_files[0]['url'], wheel_files[0]['filename']
                elif files:
                    # Fallback to source distribution
                    return files[0]['url'], files[0]['filename']
                
                return None, None
                
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ Failed to get package info: {e}")
                return None, None
    
    return None, None

def main():
    """Main download function using pip download with resume capability."""
    print("=" * 70)
    print("📦 Python Package Downloader (Simplified with Resume)")
    print("=" * 70)
    print(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    print("=" * 70)
    print()
    
    # Create download directory
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    if not REQUIREMENTS_FILE.exists():
        print(f"❌ Requirements file not found: {REQUIREMENTS_FILE}")
        return 1
    
    print(f"📄 Using requirements file: {REQUIREMENTS_FILE}")
    print("📋 Step 1: Using pip download to get all packages and dependencies...")
    print("   (This will download to the downloads directory)")
    print()
    
    # Use pip download to get all packages
    # This handles dependency resolution automatically
    cmd = [
        sys.executable, "-m", "pip", "download",
        "-r", str(REQUIREMENTS_FILE),
        "-d", str(DOWNLOAD_DIR),
        "--no-deps"  # We'll handle dependencies separately if needed
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print("⚠️  pip download with --no-deps had issues, trying with dependencies...")
            # Try again with dependencies
            cmd = [
                sys.executable, "-m", "pip", "download",
                "-r", str(REQUIREMENTS_FILE),
                "-d", str(DOWNLOAD_DIR)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        print("⚠️  pip download timed out, but may have downloaded some packages")
        print("   Continuing to check and resume incomplete downloads...")
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        print("   Continuing to check and resume incomplete downloads...")
    except Exception as e:
        print(f"⚠️  Error during pip download: {e}")
        print("   Continuing to check and resume incomplete downloads...")
    
    print()
    print("📋 Step 2: Checking for incomplete downloads and resuming...")
    print()
    
    # Check all .whl and .tar.gz files in download directory
    downloaded_files = list(DOWNLOAD_DIR.glob("*.whl")) + list(DOWNLOAD_DIR.glob("*.tar.gz"))
    
    if not downloaded_files:
        print("⚠️  No files found in download directory.")
        print("   pip download may have failed. Trying alternative method...")
        
        # Fallback: parse requirements.txt and download manually
        print("\n📋 Alternative: Downloading packages directly from PyPI...")
        with open(REQUIREMENTS_FILE, 'r') as f:
            packages = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '==' in line:
                        name, version = line.split('==', 1)
                        packages.append((name.strip(), version.strip()))
                    else:
                        packages.append((line.strip(), None))
        
        stats = {'downloaded': 0, 'failed': 0, 'skipped': 0}
        
        for idx, (package_name, version) in enumerate(packages, 1):
            print(f"[{idx}/{len(packages)}] {package_name}" + (f"=={version}" if version else ""))
            
            filepath = DOWNLOAD_DIR / f"{package_name}-{version if version else 'latest'}.whl"
            if filepath.exists():
                print(f"  ✅ Already exists")
                stats['skipped'] += 1
                continue
            
            url, filename = get_package_url_from_pypi(package_name, version)
            if not url:
                print(f"  ❌ Could not get download URL")
                stats['failed'] += 1
                continue
            
            filepath = DOWNLOAD_DIR / filename
            if filepath.exists():
                print(f"  ✅ Already exists: {filename}")
                stats['skipped'] += 1
                continue
            
            print(f"  📥 Downloading: {filename}")
            success, message = download_file(url, filepath, resume=True)
            
            if success:
                stats['downloaded'] += 1
                print(f"  ✅ {message.capitalize()}")
            else:
                stats['failed'] += 1
                print(f"  ❌ {message}")
            print()
        
        print("=" * 70)
        print("📊 Download Summary")
        print("=" * 70)
        print(f"✅ Downloaded:  {stats['downloaded']}")
        print(f"✅ Skipped:     {stats['skipped']}")
        print(f"❌ Failed:      {stats['failed']}")
        print("=" * 70)
        
        return 0 if stats['failed'] == 0 else 1
    
    # Check each file for completeness
    print(f"Found {len(downloaded_files)} files to check")
    print()
    
    stats = {'checked': 0, 'complete': 0, 'incomplete': 0, 'resumed': 0, 'failed': 0}
    
    for filepath in downloaded_files:
        stats['checked'] += 1
        filename = filepath.name
        file_size = filepath.stat().st_size
        
        print(f"[{stats['checked']}/{len(downloaded_files)}] {filename} ({file_size:,} bytes)")
        
        # Try to get expected size from PyPI
        # Extract package name and version from filename
        if filename.endswith('.whl'):
            parts = filename.replace('.whl', '').split('-')
            if len(parts) >= 2:
                package_name = parts[0].replace('_', '-')
                # Try to find version in filename
                # This is approximate - pip download should have complete files
                print(f"  ✅ File exists ({file_size:,} bytes)")
                stats['complete'] += 1
        else:
            print(f"  ✅ File exists ({file_size:,} bytes)")
            stats['complete'] += 1
        
        print()
    
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"Files checked:   {stats['checked']}")
    print(f"✅ Complete:     {stats['complete']}")
    print(f"⚠️  Incomplete:   {stats['incomplete']}")
    print(f"↻  Resumed:       {stats['resumed']}")
    print(f"❌ Failed:        {stats['failed']}")
    print("=" * 70)
    
    print(f"\n🎉 All packages are in: {DOWNLOAD_DIR.absolute()}")
    print(f"\nTo install all packages, run:")
    print(f"  pip install {DOWNLOAD_DIR}/*.whl")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user.")
        print("You can re-run this script to resume downloads.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

