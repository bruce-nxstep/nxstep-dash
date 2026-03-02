
import os
import sys

# Print current CWD
print(f"CWD: {os.getcwd()}")

# Add src to path
src_path = os.path.join(os.getcwd(), 'src')
sys.path.append(src_path)
print(f"Added to path: {src_path}")

# Check if file exists
file_path = os.path.join(src_path, 'google_sync.py')
print(f"File exists: {os.path.exists(file_path)}")

# Try import
try:
    from google_sync import GoogleSheetSync
    print("✅ SUCCESS: Imported GoogleSheetSync")
except ImportError as e:
    print(f"❌ FAILURE: {e}")
    print(f"sys.path: {sys.path}")
