#!/usr/bin/env python3
"""Quick script to download the correct hf-xet wheel for Python 3.12"""

import sys
import json
from pathlib import Path
from urllib.request import urlopen, Request
import ssl

def create_ssl_context():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def download_hf_xet():
    """Download correct hf-xet wheel for Python 3.12"""
    package_name = "hf-xet"
    version = "1.2.0"
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    
    print(f"Fetching {package_name} {version} from PyPI...")
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    req = Request(url)
    req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
    
    try:
        with urlopen(req, timeout=30, context=create_ssl_context()) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        files = data.get('releases', {}).get(version, [])
        wheel_files = [f for f in files if f['packagetype'] == 'bdist_wheel']
        
        print(f"\nFound {len(wheel_files)} wheel files:")
        for wheel in wheel_files:
            print(f"  - {wheel['filename']}")
        
        # Look for Python 3.12 compatible wheel
        cp312_wheels = [w for w in wheel_files if 'cp312' in w['filename']]
        stable_abi_wheels = [w for w in wheel_files if 'cp37-abi3' in w['filename'] or 'cp38-abi3' in w['filename']]
        universal_wheels = [w for w in wheel_files if 'none-any' in w['filename'] and 'py3' in w['filename']]
        
        selected_wheel = None
        
        if cp312_wheels:
            # Prefer cp312 wheels
            selected_wheel = cp312_wheels[0]
            print(f"\n✅ Found Python 3.12 wheel: {selected_wheel['filename']}")
        elif stable_abi_wheels:
            # Stable ABI wheels (cp37-abi3) are compatible with Python 3.7+
            # Prefer macOS x86_64 if available
            macos_wheels = [w for w in stable_abi_wheels if 'macosx' in w['filename'] and 'x86_64' in w['filename']]
            if macos_wheels:
                selected_wheel = macos_wheels[0]
            else:
                selected_wheel = stable_abi_wheels[0]
            print(f"\n✅ Found stable ABI wheel (compatible with Python 3.12): {selected_wheel['filename']}")
        elif universal_wheels:
            # Fall back to universal wheel
            selected_wheel = universal_wheels[0]
            print(f"\n✅ Found universal wheel: {selected_wheel['filename']}")
        else:
            print("\n❌ No compatible wheel found for Python 3.12")
            print("Available wheels:")
            for wheel in wheel_files:
                print(f"  - {wheel['filename']}")
            return False
        
        # Download the wheel
        filepath = download_dir / selected_wheel['filename']
        if filepath.exists():
            print(f"\n✅ File already exists: {filepath}")
            return True
        
        print(f"\n📥 Downloading: {selected_wheel['filename']}")
        print(f"   URL: {selected_wheel['url']}")
        
        download_url = selected_wheel['url']
        req = Request(download_url)
        req.add_header('User-Agent', 'Python-Package-Downloader/1.0')
        
        with urlopen(req, timeout=60, context=create_ssl_context()) as response:
            with open(filepath, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
        
        print(f"✅ Downloaded: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = download_hf_xet()
    sys.exit(0 if success else 1)

