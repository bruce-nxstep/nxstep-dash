import sqlite3
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='data/leads_database.db'):
        # S'assurer que le dossier data existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialise toutes les tables nécessaires si elles n'existent pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des leads
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT UNIQUE NOT NULL,
                website TEXT,
                linkedin_url TEXT,
                description TEXT,
                email TEXT,
                first_name TEXT,
                last_name TEXT,
                icebreaker TEXT,
                status TEXT DEFAULT 'Scrapé',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Plateforme Cron / Jobs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL,
                search_query TEXT,
                schedule_time TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kanban (Missions CRM)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission TEXT NOT NULL,
                status TEXT DEFAULT 'A faire',
                priorite TEXT,
                agentic TEXT,
                collaborateur TEXT,
                date_debut TEXT,
                date_fin TEXT,
                commentaire TEXT,
                next_step TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Checklists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        ''')
        
        # Planning Editorial (Community Manager)
        cursor.execute('''
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
            )
        ''')

        # Table des logs de publication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publication_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                title TEXT,
                status TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des comptes LinkedIn
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS linkedin_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                person_urn TEXT UNIQUE NOT NULL,
                access_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Migration
        columns_to_add = ["post_idea", "img1", "img2", "img3", "img4", "img5", "img6", "img7", "img8", "img9", "img10", "linkedin_account_id"]
        for col in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE content_plan ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass 
        
        conn.commit()
        conn.close()

    # --- CONTENT PLAN METHODS (Community Manager) ---

    def add_content_item(self, title, post_idea="", post_type="Post", content="", media_files="[]", 
                         img1="", img2="", img3="", img4="", img5="", 
                         img6="", img7="", img8="", img9="", img10="",
                         scheduled_at=None, status="Brouillon", linkedin_account_id=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO content_plan (
                title, post_idea, post_type, content, media_files, 
                img1, img2, img3, img4, img5, img6, img7, img8, img9, img10,
                scheduled_at, status, linkedin_account_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, post_idea, post_type, content, media_files, 
              img1, img2, img3, img4, img5, img6, img7, img8, img9, img10,
              scheduled_at, status, linkedin_account_id))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id

    def update_content_item(self, item_id, updates):
        if not updates: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates['updated_at'] = datetime.now().isoformat()
        columns = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(item_id)
        query = f"UPDATE content_plan SET {columns} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_content_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM content_plan WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

    # --- LINKEDIN ACCOUNTS METHODS ---

    def add_or_update_linkedin_account(self, name, person_urn, access_token):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # On essaie de mettre à jour si le URN existe déjà, sinon on insère
        cursor.execute("SELECT id FROM linkedin_accounts WHERE person_urn = ?", (person_urn,))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE linkedin_accounts 
                SET name = ?, access_token = ?, updated_at = ? 
                WHERE person_urn = ?
            ''', (name, access_token, now, person_urn))
        else:
            cursor.execute('''
                INSERT INTO linkedin_accounts (name, person_urn, access_token, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, person_urn, access_token, now, now))
        
        conn.commit()
        conn.close()

    def get_linkedin_accounts(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM linkedin_accounts ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_linkedin_account(self, account_id):
        if not account_id or account_id == 'None': return None
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM linkedin_accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_linkedin_account(self, account_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM linkedin_accounts WHERE id = ?", (account_id,))
        conn.commit()
        conn.close()

    def get_pending_content(self):
        """Récupère les posts dont le statut est 'Prêt' et dont la date est passée ou actuelle."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # On récupère tous les 'Prêt' et on filtre en Python pour la robustesse des formats de date
        cursor.execute("SELECT * FROM content_plan WHERE status = 'Prêt' AND scheduled_at IS NOT NULL AND scheduled_at != ''")
        rows = cursor.fetchall()
        conn.close()
        
        pending = []
        now = datetime.now()
        
        for row in rows:
            try:
                # Nettoyage de la date (gestion du 'Z' et des millisecondes)
                date_str = row['scheduled_at'].replace('Z', '')
                if '.' in date_str:
                    date_str = date_str.split('.')[0] # On ignore les microsecondes pour simplifier
                
                # Essai de plusieurs formats courants
                formats = ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
                dt = None
                for fmt in formats:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        break
                    except:
                        continue
                
                if dt and dt <= now:
                    pending.append(dict(row))
            except Exception as e:
                print(f"Erreur de parsing date pour post {row['id']}: {e}")
                
        return pending

    def add_publication_log(self, post_id, title, status, message):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO publication_logs (post_id, title, status, message)
            VALUES (?, ?, ?, ?)
        ''', (post_id, title, status, message))
        conn.commit()
        conn.close()

    def get_publication_logs(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(f'SELECT * FROM publication_logs ORDER BY timestamp DESC LIMIT {limit}', conn)
        conn.close()
        return df

    def get_all_content_df(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM content_plan ORDER BY scheduled_at ASC', conn)
        conn.close()
        return df

    # --- LEADS METHODS ---

    def add_lead(self, company_name, website=None, linkedin_url=None, description=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO leads (company_name, website, linkedin_url, description)
                VALUES (?, ?, ?, ?)
            ''', (company_name, website, linkedin_url, description))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def delete_lead(self, lead_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        conn.close()

    def update_lead(self, lead_id, updates):
        if not updates: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates['updated_at'] = datetime.now().isoformat()
        columns = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(lead_id)
        query = f"UPDATE leads SET {columns} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def get_all_leads_as_df(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM leads', conn)
        conn.close()
        return df

    # --- KANBAN / TASKS METHODS ---

    def add_task(self, mission, status="A faire", priorite="", agentic="", collaborateur="", date_debut="", date_fin="", commentaire="", next_step=""):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (mission, status, priorite, agentic, collaborateur, date_debut, date_fin, commentaire, next_step)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (mission, status, priorite, agentic, collaborateur, date_debut, date_fin, commentaire, next_step))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def update_task(self, task_id, updates):
        if not updates: return
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates['updated_at'] = datetime.now().isoformat()
        columns = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(task_id)
        query = f"UPDATE tasks SET {columns} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def update_task_status(self, task_id, new_status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (new_status, task_id))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    def clear_all_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        conn.commit()
        conn.close()

    def get_all_tasks_df(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM tasks', conn)
        conn.close()
        return df

    # --- CHECKLISTS METHODS ---

    def add_checklist_item(self, task_id, title):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON") 
        cursor.execute('INSERT INTO checklists (task_id, title) VALUES (?, ?)', (task_id, title))
        conn.commit()
        item_id = cursor.lastrowid
        conn.close()
        return item_id

    def get_checklists_for_task(self, task_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, is_completed FROM checklists WHERE task_id = ? ORDER BY id ASC', (task_id,))
        items = [{"id": row[0], "title": row[1], "is_completed": bool(row[2])} for row in cursor.fetchall()]
        conn.close()
        return items

    def toggle_checklist_item(self, item_id, is_completed):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE checklists SET is_completed = ? WHERE id = ?', (int(is_completed), item_id))
        conn.commit()
        conn.close()

    def delete_checklist_item(self, item_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checklists WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    db = DatabaseManager('data/test_db.db')
    print("Database initialized.")
