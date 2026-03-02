import sqlite3
import os
import shutil

db_path = os.path.join('data', 'cms.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- Current Database Pages ---")
cursor.execute("SELECT id, title, slug, status FROM posts WHERE post_type='page'")
pages = cursor.fetchall()
for p in pages:
    print(f"ID: {p['id']} | Title: {p['title']} | Status: {p['status']}")

print("\n--- Cleaning dist directory ---")
dist_path = 'dist'
if os.path.exists(dist_path):
    shutil.rmtree(dist_path)
    os.makedirs(dist_path)
    print("dist/ cleaned.")
else:
    os.makedirs(dist_path)
    print("dist/ created.")

conn.close()
