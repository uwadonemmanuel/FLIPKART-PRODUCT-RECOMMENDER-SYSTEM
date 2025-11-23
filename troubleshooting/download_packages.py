#!/usr/bin/env python3
"""
Automated package downloader with resume capability.
Downloads all .whl files from requirements.txt, skipping already downloaded files.
"""

import os
import sys
import json
import time
import subprocess
import platform
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
CHUNK_SIZE = 8192  # 8KB chunks for download

# Platform detection
PYTHON_VERSION = f"{sys.version_info.major}{sys.version_info.minor}"
SYSTEM = platform.system().lower()
MACHINE = platform.machine().lower()

# Determine platform tag
if SYSTEM == "darwin":  # macOS
    if MACHINE == "arm64" or MACHINE == "aarch64":
        PLATFORM_TAG = "macosx_11_0_arm64"
        ALT_PLATFORM_TAGS = ["macosx_10_15_universal2", "macosx_11_0_universal2"]
    else:  # x86_64
        PLATFORM_TAG = "macosx_10_13_x86_64"
        ALT_PLATFORM_TAGS = ["macosx_10_12_x86_64", "macosx_10_13_universal2"]
elif SYSTEM == "linux":
    PLATFORM_TAG = f"linux_{MACHINE}"
    ALT_PLATFORM_TAGS = []
elif SYSTEM == "windows":
    PLATFORM_TAG = f"win_amd64" if MACHINE == "amd64" else f"win_{MACHINE}"
    ALT_PLATFORM_TAGS = []
else:
    PLATFORM_TAG = "any"
    ALT_PLATFORM_TAGS = []

CP_TAG = f"cp{PYTHON_VERSION}"


def create_ssl_context():
    """Create SSL context that's more permissive for problematic certificates."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def get_package_info(package_name):
    """Get package information from PyPI JSON API."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url)
            req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
            with urlopen(req, timeout=30, context=create_ssl_context()) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data
        except (URLError, HTTPError, TimeoutError) as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️  Retrying ({attempt + 1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  ❌ Failed to fetch package info: {e}")
                return None
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            return None
    
    return None


def find_best_wheel(package_info, version=None):
    """Find the best wheel file for the current platform."""
    if not package_info:
        return None
    
    # Get latest version if not specified
    if version is None:
        version = package_info['info']['version']
    
    # Get all files for this version
    releases = package_info.get('releases', {})
    files = releases.get(version, [])
    
    # If exact version not found, try normalized versions
    # (e.g., 2.9.0.post0 might be stored as 2.9.0 or vice versa)
    if not files:
        # Try without post-release suffix
        if '.post' in version:
            base_version = version.split('.post')[0]
            files = releases.get(base_version, [])
            if files:
                version = base_version  # Update to actual version found
        
        # Try with different post-release formats
        if not files:
            if version.endswith('.post0'):
                alt_version = version.replace('.post0', '')
                files = releases.get(alt_version, [])
                if files:
                    version = alt_version
            elif not version.endswith('.post0') and '.post' not in version:
                # Try adding .post0
                post_version = f"{version}.post0"
                files = releases.get(post_version, [])
                if files:
                    version = post_version
        
        # Try finding closest version match (fuzzy matching)
        if not files:
            # Look for versions that start with our version base
            version_base = version.split('.post')[0] if '.post' in version else version
            for release_version in sorted(releases.keys(), reverse=True):
                if release_version.startswith(version_base):
                    files = releases.get(release_version, [])
                    if files:
                        version = release_version  # Update to actual version found
                        break
    
    if not files:
        return None
    
    # Priority order:
    # 1. Platform-specific wheel (cp312-macosx_10_13_x86_64)
    # 2. Alternative platform tags
    # 3. Universal wheel (py3-none-any)
    # 4. Source distribution as last resort
    
    wheel_files = [f for f in files if f['packagetype'] == 'bdist_wheel']
    
    # Try exact platform match
    for wheel in wheel_files:
        filename = wheel['filename']
        if CP_TAG in filename and PLATFORM_TAG in filename:
            return wheel
    
    # Try alternative platform tags
    for alt_tag in ALT_PLATFORM_TAGS:
        for wheel in wheel_files:
            filename = wheel['filename']
            if CP_TAG in filename and alt_tag in filename:
                return wheel
    
    # Try universal wheel (py3-none-any or py2.py3-none-any)
    for wheel in wheel_files:
        filename = wheel['filename']
        if 'none-any' in filename and ('py3' in filename or 'py2.py3' in filename):
            return wheel
    
    # Try any wheel with correct Python version (strict check)
    # Filter out wheels for other Python versions
    compatible_wheels = []
    import re
    
    for wheel in wheel_files:
        filename = wheel['filename']
        # Extract Python version tags from filename
        # Match patterns like cp312, cp313, cp37-abi3, py3, py2.py3
        py_tags = re.findall(r'(cp\d+(?:-abi\d+)?|py\d+|py\d+\.py\d+)', filename)
        
        if py_tags:
            # Check for stable ABI wheels (cp37-abi3, cp38-abi3, etc.) - compatible with Python 3.7+
            stable_abi_tags = [t for t in py_tags if '-abi' in t]
            if stable_abi_tags:
                # Stable ABI wheels are compatible with Python 3.7 and later
                # Extract the base version (e.g., cp37 from cp37-abi3 means Python 3.7)
                python_major = sys.version_info.major
                python_minor = sys.version_info.minor
                for tag in stable_abi_tags:
                    match = re.search(r'cp(\d)(\d)', tag)  # Match cp37, cp38, etc.
                    if match:
                        wheel_major = int(match.group(1))
                        wheel_minor = int(match.group(2))
                        # Stable ABI wheels work if wheel version <= current Python version
                        # e.g., cp37-abi3 works with Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, etc.
                        if (wheel_major < python_major) or (wheel_major == python_major and wheel_minor <= python_minor):
                            compatible_wheels.append(wheel)
                            break
                continue
            
            # Check if any tag matches our Python version exactly
            if any(CP_TAG in tag for tag in py_tags):
                # Make sure it's not for a different Python version
                other_cp_tags = [t for t in py_tags if t.startswith('cp') and CP_TAG not in t and '-abi' not in t]
                if not other_cp_tags:  # No conflicting CP tags
                    compatible_wheels.append(wheel)
                    continue
            
            # Check for universal Python tags (py3, py2.py3)
            if any('py3' in tag or 'py2.py3' in tag for tag in py_tags):
                compatible_wheels.append(wheel)
                continue
        else:
            # No Python version tag, assume compatible
            compatible_wheels.append(wheel)
    
    if compatible_wheels:
        return compatible_wheels[0]
    
    # Last resort: any wheel (but warn)
    if wheel_files:
        print(f"    ⚠️  Warning: No exact Python version match, using: {wheel_files[0]['filename']}")
        return wheel_files[0]
    
    # If no wheel found, try source distribution as last resort
    source_files = [f for f in files if f['packagetype'] == 'sdist']
    if source_files:
        print(f"    ⚠️  No wheel found, will download source distribution")
        return source_files[0]
    
    return None


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
            # Resume download
            resume_pos = file_size
        else:
            # Start fresh
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
                        print(f"    ↻ Resuming from {resume_pos} bytes...")
                    
                    downloaded = resume_pos
                    total_size = resume_pos + int(response.headers.get('Content-Length', 0))
                    
                    while True:
                        chunk = response.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indicator
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r    ⬇️  {downloaded:,}/{total_size:,} bytes ({percent:.1f}%)", end='', flush=True)
                    
                    print()  # New line after progress
                    
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


def get_all_dependencies():
    """Get all dependencies using pip."""
    print("📋 Resolving dependencies from requirements.txt...")
    
    # Try multiple methods to get dependencies
    methods = [
        get_dependencies_pip_report,
        get_dependencies_pip_freeze,
        parse_requirements_direct
    ]
    
    for method in methods:
        try:
            packages = method()
            if packages:
                return packages
        except Exception as e:
            print(f"⚠️  Method {method.__name__} failed: {e}")
            continue
    
    print("❌ All methods failed, using basic requirements.txt parsing")
    return parse_requirements_direct()


def get_dependencies_pip_report():
    """Get dependencies using pip install --dry-run --report (pip 22.2+)."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--dry-run", "--report", "-", "-r", str(REQUIREMENTS_FILE)],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    if result.returncode != 0:
        raise Exception("pip dry-run failed")
    
    report = json.loads(result.stdout)
    packages = {}
    for item in report.get('install', []):
        name = item['metadata']['name']
        version = item['metadata']['version']
        packages[name] = version
    return packages


def get_dependencies_pip_freeze():
    """Get dependencies by using pip install --dry-run and parsing output."""
    # Use pip install --dry-run to see what would be installed
    # This is more reliable than pip show
    packages = {}
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--dry-run", "-r", str(REQUIREMENTS_FILE)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Parse the output to extract package names and versions
        # pip output format: "Would install package-name-version"
        for line in result.stdout.split('\n'):
            if 'Would install' in line or 'Would download' in line:
                # Extract package info
                parts = line.strip().split()
                for part in parts:
                    if '-' in part and (part.endswith('.whl') or part.count('-') >= 2):
                        # Try to parse package name and version
                        if part.endswith('.whl'):
                            part = part.replace('.whl', '')
                        
                        # Split by version pattern
                        import re
                        match = re.match(r'^([a-zA-Z0-9_-]+)-([0-9.]+)', part)
                        if match:
                            name = match.group(1).replace('_', '-')
                            version = match.group(2)
                            packages[name] = version
        
        if packages:
            return packages
        else:
            raise Exception("No packages parsed from pip output")
            
    except Exception as e:
        raise Exception(f"pip install --dry-run failed: {e}")


def parse_requirements_direct():
    """Parse requirements.txt directly (fallback method)."""
    packages = {}
    if REQUIREMENTS_FILE.exists():
        with open(REQUIREMENTS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package name and version
                    if '==' in line:
                        name, version = line.split('==', 1)
                        packages[name.strip()] = version.strip()
                    elif '>=' in line:
                        name = line.split('>=')[0].strip()
                        packages[name] = None  # Will get latest
                    elif '~=' in line:
                        name = line.split('~=')[0].strip()
                        packages[name] = None  # Will get latest
                    elif '<' in line or '>' in line:
                        # Handle version constraints like "<2.0.0,>=1.0.0"
                        name = line.split()[0].strip() if ' ' in line else line.split('<')[0].split('>')[0].strip()
                        packages[name] = None  # Will get latest
                    else:
                        packages[line] = None  # Will get latest
    return packages


def main():
    """Main download function."""
    print("=" * 70)
    print("📦 Python Package Downloader with Resume Capability")
    print("=" * 70)
    print(f"Platform: {SYSTEM} {MACHINE}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Target: {CP_TAG} on {PLATFORM_TAG}")
    print(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    print("=" * 70)
    print()
    
    # Create download directory
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get all packages to download
    print(f"📄 Reading requirements from: {REQUIREMENTS_FILE}")
    packages = get_all_dependencies()
    
    if not packages:
        print("❌ No packages found in requirements file")
        return 1
    
    print(f"📦 Found {len(packages)} packages to process\n")
    
    # Track statistics
    stats = {
        'total': len(packages),
        'skipped': 0,
        'downloaded': 0,
        'failed': 0,
        'already_exists': 0
    }
    
    # Track failed packages for retry
    failed_packages = []
    
    # Process each package
    for idx, (package_name, version) in enumerate(packages.items(), 1):
        print(f"[{idx}/{stats['total']}] Processing {package_name}" + (f"=={version}" if version else ""))
        
        # Get package info from PyPI
        package_info = get_package_info(package_name)
        if not package_info:
            print(f"  ❌ Could not fetch package information")
            stats['failed'] += 1
            failed_packages.append((package_name, version, "Could not fetch package information"))
            continue
        
        # Determine version
        if version is None:
            version = package_info['info']['version']
        
        # Find best wheel file
        wheel = find_best_wheel(package_info, version)
        if not wheel:
            print(f"  ❌ No suitable wheel file found for {package_name} {version}")
            stats['failed'] += 1
            failed_packages.append((package_name, version, "No suitable wheel file found"))
            continue
        
        filename = wheel['filename']
        url = wheel['url']
        filepath = DOWNLOAD_DIR / filename
        
        # Check if already downloaded
        if filepath.exists():
            file_size = filepath.stat().st_size
            expected_size = wheel.get('size', 0)
            if expected_size > 0 and file_size == expected_size:
                print(f"  ✅ Already downloaded: {filename}")
                stats['already_exists'] += 1
                continue
            else:
                print(f"  ⚠️  Incomplete file found, will resume: {filename}")
        
        # Download the file
        print(f"  📥 Downloading: {filename}")
        success, message = download_file(url, filepath, resume=True)
        
        if success:
            if "already complete" in message:
                stats['already_exists'] += 1
            else:
                stats['downloaded'] += 1
            print(f"  ✅ {message.capitalize()}")
        else:
            stats['failed'] += 1
            failed_packages.append((package_name, version, message))
            print(f"  ❌ {message}")
        
        print()
    
    # Print summary
    print("=" * 70)
    print("📊 Download Summary")
    print("=" * 70)
    print(f"Total packages:     {stats['total']}")
    print(f"✅ Downloaded:      {stats['downloaded']}")
    print(f"✅ Already exists:  {stats['already_exists']}")
    print(f"❌ Failed:          {stats['failed']}")
    print(f"⏭️  Skipped:         {stats['skipped']}")
    print("=" * 70)
    
    if stats['failed'] == 0:
        print("\n🎉 All packages downloaded successfully!")
        print(f"\nTo install all packages, run:")
        print(f"  pip install {DOWNLOAD_DIR}/*.whl")
        return 0
    else:
        print(f"\n⚠️  {stats['failed']} package(s) failed to download.")
        
        # Save failed packages to a file for retry
        failed_file = Path("failed_packages.txt")
        if failed_packages:
            with open(failed_file, 'w') as f:
                f.write("# Failed packages - run retry_failed.py to retry these\n")
                for name, version, error in failed_packages:
                    if version:
                        f.write(f"{name}=={version}  # {error}\n")
                    else:
                        f.write(f"{name}  # {error}\n")
            print(f"\n📝 Failed packages saved to: {failed_file}")
            print("   Run: python retry_failed.py")
        
        print("\nYou can also re-run this script to retry failed downloads.")
        return 1


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

