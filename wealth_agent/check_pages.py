import sqlite3
import os

db_path = os.path.join('data', 'cms.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Pages in Database ---")
cursor.execute("SELECT id, title, slug, status, post_type FROM posts WHERE post_type='page'")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))

conn.close()
