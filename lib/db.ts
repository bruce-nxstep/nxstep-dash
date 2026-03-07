import Database from 'better-sqlite3';
import path from 'path';

// Connect to the same database used by the Python backend
const dbPath = path.resolve(process.cwd(), 'wealth_agent/data/leads_database.db');

let db: ReturnType<typeof Database> | null = null;

export function getDb() {
    if (!db) {
        db = new Database(dbPath);
        db.pragma('journal_mode = WAL');

        // Initialize Notion-like structures
        db.exec(`
      CREATE TABLE IF NOT EXISTS pages (
          id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          parent_id TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );

      CREATE TABLE IF NOT EXISTS blocks (
          id TEXT PRIMARY KEY,
          page_id TEXT NOT NULL,
          type TEXT NOT NULL, -- 'paragraph', 'heading_1', 'checklist', 'collection_view', etc.
          content TEXT, -- JSON structure for text/marks
          properties TEXT, -- JSON for extra block data (e.g., checked status)
          order_index INTEGER NOT NULL,
          parent_block_id TEXT, -- For nested blocks (like lists)
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (page_id) REFERENCES pages (id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS collections (
          id TEXT PRIMARY KEY,
          page_id TEXT NOT NULL, -- The page where this collection was created
          schema TEXT NOT NULL, -- JSON describing columns/properties
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (page_id) REFERENCES pages (id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS collection_items (
          id TEXT PRIMARY KEY,
          collection_id TEXT NOT NULL,
          properties TEXT NOT NULL, -- JSON holding cell values
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS content_plan (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          linkedin_account_id INTEGER,
          title TEXT NOT NULL,
          post_idea TEXT,
          post_type TEXT DEFAULT 'Post',
          content TEXT,
          media_files TEXT,
          img1 TEXT, img2 TEXT, img3 TEXT, img4 TEXT, img5 TEXT,
          img6 TEXT, img7 TEXT, img8 TEXT, img9 TEXT, img10 TEXT,
          scheduled_at TEXT,
          status TEXT DEFAULT 'Brouillon',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);
    }
    return db;
}
