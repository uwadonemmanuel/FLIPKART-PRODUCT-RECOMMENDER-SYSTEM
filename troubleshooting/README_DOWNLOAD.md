# Package Download Scripts

Two scripts are available to download all Python packages with resume capability:

## Scripts

### 1. `download_packages.py` (Advanced)
- Queries PyPI API directly for each package
- Automatically selects the correct wheel file for your platform
- Handles dependency resolution
- Full resume capability for interrupted downloads
- More control but slower

### 2. `download_packages_simple.py` (Recommended)
- Uses `pip download` to handle dependency resolution automatically
- Faster and more reliable
- Checks and resumes incomplete downloads
- Simpler approach

## Usage

### Recommended: Simple Script
```bash
python download_packages_simple.py
```

### Advanced: Full Control Script
```bash
python download_packages.py
```

## Features

✅ **Resume Capability**: If download is interrupted, re-run the script to resume  
✅ **Skip Existing**: Already downloaded files are skipped  
✅ **Platform Detection**: Automatically selects correct wheel files for your system  
✅ **SSL Error Handling**: Works around SSL certificate issues  
✅ **Progress Tracking**: Shows download progress for each file  
✅ **Retry Logic**: Automatically retries failed downloads  

## Download Directory

All packages are downloaded to: `downloads/`

The script will:
- Skip files that are already completely downloaded
- Resume incomplete downloads
- Retry failed downloads up to 5 times

## After Download

Install all downloaded packages:
```bash
pip install downloads/*.whl
```

Or install from the directory:
```bash
pip install --find-links downloads -r requirements.txt
```

## Platform Information

The scripts automatically detect:
- Python version (e.g., 3.12)
- Operating system (macOS, Linux, Windows)
- Architecture (x86_64, arm64, etc.)

And download the appropriate wheel files for your platform.

## Troubleshooting

### SSL Errors
The scripts use a more permissive SSL context to work around certificate issues.

### Incomplete Downloads
If a download fails, simply re-run the script. It will automatically resume from where it left off.

### Missing Dependencies
The simple script uses `pip download` which automatically resolves all dependencies. The advanced script queries PyPI for each package individually.

## Notes

- The scripts check file sizes to determine if downloads are complete
- Partial downloads are automatically resumed
- Universal wheels (py3-none-any) are preferred if platform-specific wheels aren't available
- Source distributions (.tar.gz) are downloaded as a last resort

