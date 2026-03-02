import os
import sys

# Mimic chat_app.py path logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from database import DatabaseManager
    print(f"Imported DatabaseManager from: {sys.modules['database'].__file__}")
    db = DatabaseManager()
    if hasattr(db, 'get_all_content_df'):
        print("✅ Method get_all_content_df FOUND")
    else:
        print("❌ Method get_all_content_df NOT FOUND")
        print(f"Available attributes: {[attr for attr in dir(db) if not attr.startswith('__')]}")
except Exception as e:
    print(f"Error: {e}")
