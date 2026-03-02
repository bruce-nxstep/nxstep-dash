import os
import sqlite3
import json
import requests
from typing import Optional, List, Dict, Any
import time
from datetime import datetime
from src.mcp_client import get_stitch_client

# Database path for local state
DB_PATH = "stitch_state.db"


class StitchManager:
    """
    Manager for interfacing with the Stitch MCP server and handling design projects.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.progress = 0
        self.status_text = ""
        self._init_db()

    def update_progress(self, value: int, text: str):
        """Met à jour la progression pour l'interface utilisateur."""
        self.progress = value
        self.status_text = text
        # Essayer de mettre à jour Streamlit si disponible
        try:
            import streamlit as st
            if 'stitch_progress' in st.session_state:
                st.session_state.stitch_progress = value
                st.session_state.stitch_status = text
        except:
            pass

    def _init_db(self):
        """Ensures the Stitch-specific state table exists."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stitch_config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_designs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def set_config(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO stitch_config (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get_config(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM stitch_config WHERE key = ?", (key,)).fetchone()
            return row[0] if row else None

    def _slugify(self, s: str) -> str:
        """Robust slugification matching the CMS Dashboard."""
        import unicodedata
        import re
        s = unicodedata.normalize("NFD", s).encode(
            "ascii", "ignore").decode("ascii")
        return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

    def save_screen_to_cms(self, title: str, html: str, slug: str = None) -> int:
        """
        Saves generated HTML/Tailwind content as a new page in the CMS.
        Extracts only the <body> content as the template will provide the frame.
        """
        import re
        from cms_database import CMSDatabase
        
        # Extract body content if present
        body_match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
        content = body_match.group(1).strip() if body_match else html.strip()
        
        # We need the CMS db path. Assuming it's in data/cms.db relative to root
        cms_db_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'data', 'cms.db')
        cms_db = CMSDatabase(cms_db_path)

        # Determine excerpt and SEO
        excerpt = f"Design généré via Stitch Agent : {title}"
        meta_title = f"{title} | Design Premium"
        meta_description = f"Page web haute fidélité générée par l'IA Stitch pour {title}."

        # Generated slug if not provided
        if not slug:
            slug = self._slugify(title)

        # Add post as 'page' and 'published'
        post_id = cms_db.add_post(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            post_type="page",
            status="published",
            meta_title=meta_title,
            meta_description=meta_description,
            author="Stitch Agent",
            ai_generated=True
        )
        return post_id

    def fetch_html_from_url(self, url: str) -> str:
        # ... (existing code)
        pass

    def get_screen_code(self, screen_id: str, project_id: Optional[str] = None) -> str:
        """
        Récupère le code HTML/Tailwind réel d'un écran.
        Lève une exception si le code ne peut pas être récupéré.
        """
        try:
            api_key = self.get_config("stitch_api_key") or os.environ.get("STITCH_API_KEY")
            client = get_stitch_client(api_key=api_key)
            # Prioritize: argument > stored mapping > current context
            pid = project_id or self.get_config(f"project_of_{screen_id}") or self.ensure_project_context()
            self.set_config("current_screen_id", screen_id)

            # 1. Essayer l'outil virtuel s'il existe (get_screen_code)
            try:
                # Log usage for debugging
                client._log(f"Attempting get_screen_code for projects/{pid}/screens/{screen_id}")
                response = client.call_tool("get_screen_code", {"projectId": pid, "screenId": screen_id})
                if response:
                    text = "".join([getattr(i, 'text', str(i)) for i in response])
                    # Try extracting JSON content
                    try:
                        data = json.loads(text)
                        if "htmlContent" in data: return data["htmlContent"]
                        if "code" in data: return data["code"]
                    except:
                        if "<html" in text.lower() or "<div" in text.lower():
                            return text
            except Exception as e:
                client._log(f"Virtual tool get_screen_code failed: {e}")

            # 2. Fallback : Utiliser get_screen et extraire l'URL de téléchargement
            client._log(f"Falling back to get_screen for projects/{pid}/screens/{screen_id}")
            res = client.call_tool("get_screen", {
                "name": f"projects/{pid}/screens/{screen_id}", 
                "projectId": pid, 
                "screenId": screen_id
            })

            if not res:
                raise Exception("Réponse vide de get_screen")

            res_text = "".join([getattr(i, 'text', str(i)) for i in res])
            client._log(f"DEBUG: get_screen raw result: {res_text[:200]}...")

            if "entity was not found" in res_text.lower():
                raise Exception(f"L'écran '{screen_id}' n'a pas été trouvé dans le projet '{pid}'. Il a peut-être été supprimé ou l'ID est incorrect.")

            if "Stitch API has not been used" in res_text or "API keys not supported" in res_text:
                raise Exception(f"Erreur API Stitch : {res_text}")

            # Parsing JSON for downloadUrl
            download_url = None
            try:
                data = json.loads(res_text)
                if "htmlCode" in data and "downloadUrl" in data["htmlCode"]:
                    download_url = data["htmlCode"]["downloadUrl"]
                elif "downloadUrl" in data:
                    download_url = data["downloadUrl"]
                elif "screenshot" in data and "downloadUrl" in data["screenshot"]:
                    # Sometimes only screenshot is available? Check
                    pass
            except: pass

            # Fallback Regex
            if not download_url:
                import re
                url_match = re.search(r'downloadUrl:\s*"([^"]+)"', res_text)
                if not url_match:
                    url_match = re.search(r'downloadUrl"\s*:\s*"([^"]+)"', res_text)
                if url_match:
                    download_url = url_match.group(1)

            if download_url:
                client._log(f"Downloading HTML from: {download_url}")
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        resp = requests.get(download_url, headers=headers)
                        if resp.status_code == 200: return resp.text
                        elif resp.status_code == 429:
                            time.sleep((attempt + 1) * 2)
                            continue
                        else:
                            time.sleep(1)
                    except: time.sleep(1)

                # Final attempt
                resp = requests.get(download_url, headers=headers)
                if resp.status_code == 200: return resp.text
                else: raise Exception(f"Download failed after retries with status {resp.status_code}")

            raise Exception("URL de téléchargement introuvable dans la réponse Stitch. Le code n'est peut-être pas encore prêt.")

        except Exception as e:
            client._log(f"ERROR: Stitch code retrieval failed: {e}")
            raise e

    def fetch_and_export_to_cms(self, screen_id: str, title: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Récupère le code et l'enregistre dans le CMS."""
        try:
            html = self.get_screen_code(screen_id, project_id)

            # --- ADAPTATION DESIGN SYSTEM (NEW) ---
            try:
                from src.design_adapter import design_adapter
                print(f"Adapting code for '{title}' to Design System...")
                html = design_adapter.adapt_html(html)
                print("Code adapted successfully.")
            except Exception as e:
                print(
                    f"WARNING: Design Adapter failed: {e}. Using original code.")
            # --------------------------------------

            post_id = self.save_screen_to_cms(title, html)
            return {"success": True, "post_id": post_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def ensure_project_context(self) -> str:
        """Vérifie qu'un projet existe ou en crée un nouveau par défaut. Retourne le projectId valide."""
        import re
        api_key = self.get_config("stitch_api_key") or os.environ.get("STITCH_API_KEY")
        client = get_stitch_client(api_key=api_key)

        def extract_pid(obj_text):
            match = re.search(r'projects/([0-9]+)', str(obj_text))
            return match.group(1) if match else None

        stored_pid = self.get_config("last_project_id")
        if stored_pid and stored_pid != "default" and len(stored_pid) > 5:
            try:
                # Try to get the project. If it fails due to network, DON'T clear it immediately.
                res = client.call_tool("get_project", {"name": f"projects/{stored_pid}"})
                res_text = "".join([getattr(i, 'text', str(i)) for i in res]) if res else ""
                
                # Only clear if it's a definitive "NOT FOUND" or "PERMISSION DENIED" from the API
                unrecoverable = ["not found", "permission denied", "entity was not found"]
                if any(err in res_text.lower() for err in unrecoverable):
                    client._log(f"Project ID {stored_pid} definitively invalid: {res_text[:100]}")
                    stored_pid = None
                else:
                    return stored_pid # Still good (or transient error we ignore for now)
            except Exception as e:
                client._log(f"Transient error verifying project {stored_pid}: {e}. Keeping it.")
                return stored_pid

        # Fallback to listing or creating
        try:
            res = client.call_tool("list_projects", {})
            res_text = "".join([getattr(i, 'text', str(i)) for i in res]) if res else ""
            pid = extract_pid(res_text)
            if pid:
                self.set_config("last_project_id", pid)
                return pid
        except: pass

        try:
            client._log("Creating a new project: Wealth Agent Designs")
            res = client.call_tool("create_project", {"title": "Wealth Agent Designs"})
            res_text = "".join([getattr(i, 'text', str(i)) for i in res]) if res else ""
            pid = extract_pid(res_text)
            if pid:
                self.set_config("last_project_id", pid)
                return pid
        except Exception as e:
            client._log(f"CRITICAL: Failed to create project: {e}")

        return "default"

    def generate_screen(self, prompt: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Appelle l'outil de génération du serveur Stitch MCP."""
        import re
        self.update_progress(10, "Initialisation de la connexion Stitch...")
        try:
            api_key = self.get_config("stitch_api_key") or os.environ.get("STITCH_API_KEY")
            client = get_stitch_client(api_key=api_key)
            self.update_progress(30, "Vérification du contexte projet...")
            pid = project_id or self.ensure_project_context()

            self.update_progress(50, "Génération du design en cours (IA)...")
            response = client.call_tool("generate_screen_from_text", {
                "projectId": pid,
                "prompt": prompt,
                "deviceType": "DESKTOP",
                "modelId": "GEMINI_3_PRO"
            })

            self.update_progress(80, "Design reçu ! Traitement de la réponse...")
            if not response:
                raise Exception("Réponse vide de generate_screen_from_text")

            # Combine all text parts safely
            text_result = "".join([getattr(i, 'text', str(i)) for i in response])
            client._log(f"DEBUG: Combined Stitch result: {text_result[:500]}...")

            if "entity was not found" in text_result.lower():
                # Project ID probably invalid or session expired
                client._log(f"Project ID {pid} reported as not found during generation.")
                self.set_config("last_project_id", "") # Clear it for next time
                return {"success": False, "error": "Le projet Stitch n'a pas été trouvé. Réessayez."}

            # --- DETECT SUGGESTIONS ---
            suggestion_patterns = ["Yes, make them all", "Would you like to", "Do you want me to", "Est-ce que vous voulez"]
            is_suggestion = any(pattern.lower() in text_result.lower() for pattern in suggestion_patterns)
            if is_suggestion and "screens/" not in text_result:
                self.update_progress(100, "Le modèle demande une précision.")
                return {"success": True, "is_suggestion": True, "suggestion_text": text_result, "screenId": None}

            screen_id = None
            # 1. Try parsing JSON
            try:
                data = json.loads(text_result)
                if isinstance(data, dict):
                    if "screens" in data and len(data["screens"]) > 0:
                        screen_id = data["screens"][0].get("name", "").split("/")[-1]
                    elif "name" in data:
                        screen_id = data.get("name", "").split("/")[-1]
            except: pass

            # 2. Fallback Regex
            if not screen_id:
                screen_match = re.search(r'screens/([a-fA-F0-9]{32}|[a-zA-Z0-9_-]+)', text_result)
                if screen_match:
                    screen_id = screen_match.group(1)

            if screen_id:
                self.set_config("last_project_id", pid)
                self.set_config("current_screen_id", screen_id)
                # Associate this screen with this project for future exports
                self.set_config(f"project_of_{screen_id}", pid)
                self.update_progress(100, "Génération terminée !")
                return {"success": True, "screenId": screen_id, "is_suggestion": False}

            client._log(f"DEBUG: Parsing failed. Raw result snippet: {text_result[:500]}")
            return {"success": False, "error": f"ID de l'écran introuvable dans la réponse: {text_result[:100]}..."}

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.update_progress(0, f"Erreur: {str(e)}")
            return {"success": False, "error": str(e)}

    # Legacy Bridge Methods (Compatibility)
    def add_pending_design(self, prompt: str) -> int: return 0
    def get_pending_designs(self) -> list: return []
    def complete_design(self, job_id: int): pass


# Global instance
stitch_mgr = StitchManager(os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'data', 'stitch_state.db'))
