# Retry Failed Downloads Guide

## Overview

If some packages fail to download, the script now automatically saves them to `failed_packages.txt` for easy retry.

## Quick Commands

### 1. Check which packages failed:
```bash
python show_failed.py
```

### 2. Retry failed packages:
```bash
python retry_failed.py
```

### 3. Re-run the main download script (will retry failed ones):
```bash
python download_packages.py
```

## How It Works

1. **During Download**: When `download_packages.py` runs, it tracks any failed packages
2. **Save Failed List**: Failed packages are saved to `failed_packages.txt` with error messages
3. **Retry**: Run `retry_failed.py` to retry only the failed packages (faster than re-running everything)

## Example Output

When packages fail, you'll see:
```
⚠️  7 package(s) failed to download.

📝 Failed packages saved to: failed_packages.txt
   Run: python retry_failed.py
```

## Failed Packages File Format

The `failed_packages.txt` file looks like:
```
# Failed packages - run retry_failed.py to retry these
package-name==1.0.0  # Error message here
another-package==2.0.0  # Different error
```

## Benefits

✅ **Faster Retries**: Only retries failed packages, not all packages  
✅ **Error Tracking**: See why each package failed  
✅ **Automatic Cleanup**: `failed_packages.txt` is removed when all packages succeed  
✅ **Resume Support**: Incomplete downloads are automatically resumed  

## Troubleshooting

### If retry still fails:
1. Check the error message in `failed_packages.txt`
2. Common issues:
   - **SSL errors**: Script handles these automatically with retries
   - **Network timeouts**: Script retries up to 5 times
   - **Missing wheel files**: Package may not have a wheel for your platform
   - **Version not found**: Check if the version exists on PyPI

### Manual Download:
If a package consistently fails, you can:
1. Check the package on PyPI: `https://pypi.org/project/PACKAGE_NAME/`
2. Download manually from the browser
3. Place the `.whl` file in the `downloads/` directory

## Tips

- Run `retry_failed.py` multiple times if needed - it's safe to re-run
- Check your internet connection if many packages fail
- Some packages may need to be downloaded as source distributions (`.tar.gz`) if wheels aren't available

