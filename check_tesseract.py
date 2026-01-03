#!/usr/bin/env python
"""
Script to check if Tesseract is properly installed and accessible
Run this to debug Tesseract installation issues
"""
import sys
import os
import subprocess
import shutil

def check_tesseract():
    """Check if Tesseract is installed and accessible"""
    print("=" * 60)
    print("TESSERACT INSTALLATION CHECK")
    print("=" * 60)
    
    # Check 1: Is tesseract in PATH?
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        print(f"✅ Tesseract found in PATH: {tesseract_path}")
    else:
        print("❌ Tesseract NOT found in PATH")
    
    # Check 2: Check common installation paths
    common_paths = [
        '/usr/bin/tesseract',
        '/usr/local/bin/tesseract',
        '/bin/tesseract',
        '/opt/homebrew/bin/tesseract',  # macOS Homebrew
    ]
    
    print("\nChecking common installation paths:")
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Found: {path}")
        else:
            print(f"❌ Not found: {path}")
    
    # Check 3: Try to run tesseract
    print("\nTrying to run tesseract --version:")
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"✅ Tesseract version:\n{result.stdout}")
    except FileNotFoundError:
        print("❌ Tesseract command not found")
    except subprocess.TimeoutExpired:
        print("❌ Tesseract command timed out")
    except Exception as e:
        print(f"❌ Error running tesseract: {e}")
    
    # Check 4: Try pytesseract
    print("\nChecking pytesseract:")
    try:
        import pytesseract
        print(f"✅ pytesseract imported successfully")
        print(f"   Default cmd: {pytesseract.pytesseract.tesseract_cmd}")
        
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version via pytesseract: {version}")
        except Exception as e:
            print(f"❌ Error getting version via pytesseract: {e}")
            
    except ImportError:
        print("❌ pytesseract not installed")
    except Exception as e:
        print(f"❌ Error with pytesseract: {e}")
    
    # Check 5: List installed language packs
    print("\nChecking for tessdata (language data):")
    tessdata_paths = [
        '/usr/share/tesseract-ocr/4.00/tessdata',
        '/usr/share/tesseract-ocr/5/tessdata',
        '/usr/share/tessdata',
        '/usr/local/share/tessdata',
    ]
    
    for path in tessdata_paths:
        if os.path.exists(path):
            print(f"✅ Found tessdata directory: {path}")
            try:
                files = os.listdir(path)
                lang_files = [f for f in files if f.endswith('.traineddata')]
                if lang_files:
                    print(f"   Languages: {', '.join([f.replace('.traineddata', '') for f in lang_files[:10]])}")
                    if len(lang_files) > 10:
                        print(f"   ... and {len(lang_files) - 10} more")
            except Exception as e:
                print(f"   Error listing files: {e}")
        else:
            print(f"❌ Not found: {path}")
    
    print("\n" + "=" * 60)
    print("END OF CHECK")
    print("=" * 60)

if __name__ == '__main__':
    check_tesseract()
