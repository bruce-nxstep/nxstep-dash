import os
import sys
import time
import schedule
import sqlite3
import pandas as pd
from datetime import datetime

# Ajouter le dossier src au Python Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from scraper import ScraperManager
from enricher import EnricherManager
from ai_writer import AIWriter
from outreach import OutreachManager

# Initialisation
db_path = os.path.join(os.path.dirname(__file__), 'data', 'leads_database.db')
db = DatabaseManager(db_path)
scraper = ScraperManager(db)
enricher = EnricherManager(db)
ai_writer = AIWriter(db)
outreach = OutreachManager(db)

def execute_full_pipeline(search_query=None):
    """
    Exécute toute la chaîne d'action de l'agent : Scraping > Enrichissement > IA > Envoi.
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🤖 Lancement de la routine d'automatisation complète...")
    
    # 1. Scraping (Optionnel, seulement si une requête est fournie)
    if search_query:
        print(f"Étape 1: Scraping pour '{search_query}'...")
        added = scraper.search_google_maps(search_query, max_results=5) # 5 leads à la fois en auto pour rester sous les radars
        print(f"-> {added} leads générés.")
    else:
        print("Étape 1: Scraping ignoré (pas de requête spécifiée).")

    # 2. Enrichissement (Cherche des e-mails pour les nouveaux leads 'Scrapés')
    print("Étape 2: Enrichissement...")
    emails_found = enricher.process_pending_leads()
    print(f"-> {emails_found} emails trouvés.")

    # 3. Rédaction IA (Scrapé ou Enrichi -> Icebreaker généré)
    print("Étape 3: Rédaction IA...")
    icebreakers = ai_writer.process_pending_leads()
    print(f"-> {icebreakers} messages rédigés.")

    # 4. Envoi SMTP
    print("Étape 4: Envoi SMTP...")
    sent = outreach.send_via_smtp()
    print(f"-> {sent} emails envoyés.")
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Routine terminée.")

def run_scheduled_jobs():
    """Vérifie la base de données et exécute les tâches planifiées si nécessaire"""
    try:
        conn = sqlite3.connect(db_path)
        # On lit les jobs
        jobs = pd.read_sql_query("SELECT * FROM scheduled_jobs WHERE is_active = 1", conn)
        conn.close()
        
        if jobs.empty:
            return
            
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for index, job in jobs.iterrows():
            # Si c'est l'heure (à la minute près)
            if job['schedule_time'] == current_time:
                print(f"⏰ Execution du job #{job['id']} : {job['job_type']}")
                
                if job['job_type'] == "full_pipeline":
                    execute_full_pipeline(search_query=job.get('search_query'))
                    
                # Mettre à jour last_run
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE scheduled_jobs SET last_run = ? WHERE id = ?", (now.isoformat(), job['id']))
                conn.commit()
                conn.close()
                
    except Exception as e:
        print(f"⚠️ Erreur lors de la vérification des tâches cron : {e}")

# Option de test rapide avec l'argument `--test` dans le terminal
if len(sys.argv) > 1 and sys.argv[1] == "--test":
    print("Mode Test: Execution immédiate du pipeline.")
    execute_full_pipeline("Agences SEO à Toulouse")
    sys.exit()

print("="*50)
print("⚙️ NXSTEP WEALTH AGENT - CRON WORKER ⚙️")
print("Le worker est en écoute des tâches planifiées... (Ctrl+C pour quitter)")
print("="*50)

# Le Worker vérifie chaque minute si une tâche doit être exécutée
schedule.every(1).minutes.do(run_scheduled_jobs)

while True:
    schedule.run_pending()
    time.sleep(1)
