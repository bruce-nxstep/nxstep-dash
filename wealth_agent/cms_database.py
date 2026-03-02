"""
CMS Database Manager — WordPress-equivalent data model.
Tables: posts, categories, tags, post_categories, post_tags
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional

class CMSDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data", "cms.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS categories (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL UNIQUE,
                    slug        TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at  TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS tags (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    name       TEXT NOT NULL UNIQUE,
                    slug       TEXT NOT NULL UNIQUE,
                    created_at TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS posts (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    title           TEXT NOT NULL,
                    slug            TEXT NOT NULL UNIQUE,
                    content         TEXT,
                    excerpt         TEXT,
                    post_type       TEXT DEFAULT 'post',   -- 'post' | 'page'
                    status          TEXT DEFAULT 'draft',  -- 'draft' | 'published' | 'scheduled'
                    meta_title      TEXT,
                    meta_description TEXT,
                    featured_image  TEXT,
                    author          TEXT DEFAULT 'AI',
                    ai_generated    INTEGER DEFAULT 1,     -- boolean
                    is_homepage     INTEGER DEFAULT 0,     -- boolean
                    language        TEXT DEFAULT 'fr',
                    scheduled_at    TEXT,
                    created_at      TEXT DEFAULT (datetime('now')),
                    updated_at      TEXT DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS post_categories (
                    post_id     INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
                    PRIMARY KEY (post_id, category_id)
                );

                CREATE TABLE IF NOT EXISTS post_tags (
                    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                    tag_id  INTEGER REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY (post_id, tag_id)
                );
            """)
            # Migration: add is_homepage if missing
            try:
                conn.execute("ALTER TABLE posts ADD COLUMN is_homepage INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass # Already exists

    # ── CATEGORIES ────────────────────────────────────────────────────────────
    def get_all_categories(self):
        with self._conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM categories ORDER BY name").fetchall()]

    def add_category(self, name: str, slug: str, description: str = "") -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO categories (name, slug, description) VALUES (?,?,?)",
                (name.strip(), slug.strip(), description.strip())
            )
            return cur.lastrowid or 0

    def update_category(self, cat_id: int, name: str, slug: str, description: str = ""):
        with self._conn() as conn:
            conn.execute(
                "UPDATE categories SET name=?, slug=?, description=? WHERE id=?",
                (name, slug, description, cat_id)
            )

    def delete_category(self, cat_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))

    def get_category_post_count(self, cat_id: int) -> int:
        with self._conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM post_categories WHERE category_id=?", (cat_id,)
            ).fetchone()[0]

    # ── TAGS ─────────────────────────────────────────────────────────────────
    def get_all_tags(self):
        with self._conn() as conn:
            return [dict(r) for r in conn.execute("SELECT * FROM tags ORDER BY name").fetchall()]

    def add_tag(self, name: str, slug: str) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO tags (name, slug) VALUES (?,?)",
                (name.strip(), slug.strip())
            )
            return cur.lastrowid or 0

    def update_tag(self, tag_id: int, name: str, slug: str):
        with self._conn() as conn:
            conn.execute("UPDATE tags SET name=?, slug=? WHERE id=?", (name, slug, tag_id))

    def delete_tag(self, tag_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM tags WHERE id=?", (tag_id,))

    def get_tag_post_count(self, tag_id: int) -> int:
        with self._conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM post_tags WHERE tag_id=?", (tag_id,)
            ).fetchone()[0]

    # ── POSTS ─────────────────────────────────────────────────────────────────
    def get_all_posts(self, post_type: str = None, status: str = None):
        sql = """
            SELECT p.*,
                GROUP_CONCAT(DISTINCT c.name) AS categories,
                GROUP_CONCAT(DISTINCT t.name) AS tags
            FROM posts p
            LEFT JOIN post_categories pc ON p.id = pc.post_id
            LEFT JOIN categories c ON pc.category_id = c.id
            LEFT JOIN post_tags pt ON p.id = pt.post_id
            LEFT JOIN tags t ON pt.tag_id = t.id
        """
        where, params = [], []
        if post_type:
            where.append("p.post_type = ?"); params.append(post_type)
        if status:
            where.append("p.status = ?"); params.append(status)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " GROUP BY p.id ORDER BY p.updated_at DESC"
        with self._conn() as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def get_post(self, post_id: int) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
            if not row:
                return None
            post = dict(row)
            post["category_ids"] = [r[0] for r in conn.execute(
                "SELECT category_id FROM post_categories WHERE post_id=?", (post_id,)
            ).fetchall()]
            post["tag_ids"] = [r[0] for r in conn.execute(
                "SELECT tag_id FROM post_tags WHERE post_id=?", (post_id,)
            ).fetchall()]
            return post

    def add_post(self, title, slug, content="", excerpt="", post_type="post",
                 status="draft", meta_title="", meta_description="",
                 featured_image="", author="AI", ai_generated=True,
                 language="fr", scheduled_at=None,
                 category_ids=None, tag_ids=None) -> int:
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        with self._conn() as conn:
            cur = conn.execute("""
                INSERT INTO posts
                (title, slug, content, excerpt, post_type, status,
                 meta_title, meta_description, featured_image, author,
                 ai_generated, language, scheduled_at, created_at, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (title, slug, content, excerpt, post_type, status,
                  meta_title, meta_description, featured_image, author,
                  1 if ai_generated else 0, language, scheduled_at, now, now))
            post_id = cur.lastrowid
            self._sync_relations(conn, post_id, category_ids or [], tag_ids or [])
            return post_id

    def update_post(self, post_id: int, **kwargs):
        kwargs["updated_at"] = datetime.now().isoformat(sep=" ", timespec="seconds")
        cat_ids = kwargs.pop("category_ids", None)
        tag_ids = kwargs.pop("tag_ids", None)
        if kwargs:
            sets = ", ".join(f"{k}=?" for k in kwargs)
            with self._conn() as conn:
                conn.execute(f"UPDATE posts SET {sets} WHERE id=?", list(kwargs.values()) + [post_id])
                if cat_ids is not None or tag_ids is not None:
                    self._sync_relations(conn, post_id, cat_ids or [], tag_ids or [])
        elif cat_ids is not None or tag_ids is not None:
            with self._conn() as conn:
                self._sync_relations(conn, post_id, cat_ids or [], tag_ids or [])

    def _sync_relations(self, conn, post_id, cat_ids, tag_ids):
        conn.execute("DELETE FROM post_categories WHERE post_id=?", (post_id,))
        conn.execute("DELETE FROM post_tags WHERE post_id=?", (post_id,))
        for cid in cat_ids:
            conn.execute("INSERT OR IGNORE INTO post_categories VALUES (?,?)", (post_id, cid))
        for tid in tag_ids:
            conn.execute("INSERT OR IGNORE INTO post_tags VALUES (?,?)", (post_id, tid))

    def delete_post(self, post_id: int):
        with self._conn() as conn:
            conn.execute("DELETE FROM posts WHERE id=?", (post_id,))

    def get_posts_stats(self) -> dict:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as n FROM posts GROUP BY status"
            ).fetchall()
        return {r["status"]: r["n"] for r in rows}

    def set_homepage(self, post_id: int):
        with self._conn() as conn:
            # Reset all
            conn.execute("UPDATE posts SET is_homepage = 0")
            # Set target
            conn.execute("UPDATE posts SET is_homepage = 1 WHERE id = ?", (post_id,))

    def get_homepage(self) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM posts WHERE is_homepage = 1 LIMIT 1").fetchone()
            return dict(row) if row else None
