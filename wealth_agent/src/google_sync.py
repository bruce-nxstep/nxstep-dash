import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any

class GoogleSheetSync:
    def __init__(self, sheet_url: str):
        self.sheet_url = sheet_url
        self.credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'google_credentials.json')
        self.client = None
        self.sheet = None
        
        self.try_connect()

    def is_enabled(self) -> bool:
        """Indique si la connexion Google est active."""
        return self.sheet is not None

    def try_connect(self):
        """Tente de se connecter au Google Sheet si le fichier credentials existe."""
        if not os.path.exists(self.credentials_path):
            print("Google Sync: 'google_credentials.json' introuvable. Mode hors-ligne activé.")
            return

        try:
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
            self.client = gspread.authorize(creds)
            doc = self.client.open_by_url(self.sheet_url)
            
            # Recherche de l'onglet contenant la colonne 'Mission'
            target_sheet = None
            for ws in doc.worksheets():
                try:
                    first_row = ws.row_values(1)
                    if 'Mission' in first_row:
                        target_sheet = ws
                        break
                except Exception:
                    continue
            
            if target_sheet:
                self.sheet = target_sheet
                print(f"Google Sync: Onglet trouvé '{target_sheet.title}'.")
            else:
                self.sheet = doc.sheet1
                print("Google Sync: Onglet 'Mission' non trouvé, utilisation du premier onglet par défaut.")
        except Exception as e:
            print(f"Google Sync Erreur de connexion : {e}")
            self.sheet = None

    def export_all_to_sheet(self, df_tasks):
        """Écrase le Google Sheet avec la base de données SQLite actuelle."""
        if not self.is_enabled():
            return
            
        try:
            # Vider la feuille en gardant les entêtes ? Ou on réécrit tout.
            self.sheet.clear()
            
            # Préparer les données
            headers = ['Mission', 'Statut', 'Priorité', 'Agentic', 'Collaborateur', 'Date de début', 'Date de Fin', 'Commentaire', 'Next Step']
            
            rows = [headers]
            for _, row in df_tasks.iterrows():
                rows.append([
                    str(row['mission']),
                    str(row['status']),
                    str(row['priorite'] if row['priorite'] else ''),
                    str(row['agentic'] if row['agentic'] else ''),
                    str(row['collaborateur'] if row['collaborateur'] else ''),
                    str(row['date_debut'] if row['date_debut'] else ''),
                    str(row['date_fin'] if row['date_fin'] else ''),
                    str(row['commentaire'] if row['commentaire'] else ''),
                    str(row['next_step'] if row['next_step'] else '')
                ])
            
            # Mise à jour massive de la feuille
            self.sheet.update(rows)
            print("Google Sync: Sheet mis à jour depuis la BDD.")
        except Exception as e:
            print(f"Google Sync Erreur d'export : {e}")

    def import_all_from_sheet(self):
        """Lit le Google Sheet depuis zéro. Retourne les lignes sous forme de dicts pour mettre à jour la BDD SQLite."""
        if not self.is_enabled():
            return []
            
        try:
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            print(f"Google Sync Erreur d'import : {e}")
            return []
