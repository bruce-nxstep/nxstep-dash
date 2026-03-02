import os
import sys
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from mcp_client import get_stitch_client
from stitch_manager import stitch_mgr

def debug_screen():
    api_key = stitch_mgr.get_config("stitch_api_key")
    client = get_stitch_client(api_key=api_key)
    pid = stitch_mgr.get_config("last_project_id")
    sid = stitch_mgr.get_config("current_screen_id")
    
    print(f"DEBUG: pid={pid}, sid={sid}")
    res = client.call_tool("get_screen", {"name": f"projects/{pid}/screens/{sid}", "projectId": pid, "screenId": sid})
    print("\n--- FULL RESPONSE OBJECT ---")
    print(res)
    print("\n--- STRING REPRESENTATION ---")
    print(str(res))

if __name__ == "__main__":
    debug_screen()
