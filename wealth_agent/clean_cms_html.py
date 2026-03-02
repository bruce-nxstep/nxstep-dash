import sqlite3
import os
import re

def clean_html(html):
    if not html:
        return html
    # Extract body content if present
    body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if body_match:
        return body_match.group(1).strip()
    return html.strip()

def main():
    db_path = os.path.join("wealth_agent", "data", "cms.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find all AI generated posts/pages
    cursor.execute("SELECT id, title, content FROM posts WHERE ai_generated = 1")
    rows = cursor.fetchall()

    print(f"Found {len(rows)} AI generated entries to clean.")

    for row_id, title, content in rows:
        cleaned = clean_html(content)
        if cleaned != content:
            print(f"Cleaning '{title}' (ID: {row_id})...")
            cursor.execute("UPDATE posts SET content = ? WHERE id = ?", (cleaned, row_id))
        else:
            print(f"'{title}' is already clean.")

    conn.commit()
    conn.close()
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
