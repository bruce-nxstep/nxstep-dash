import os
import sys
from dotenv import load_dotenv

# Ajoute le chemin d'accès au dossier src
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database import DatabaseManager
from scraper import ScraperManager
from enricher import EnricherManager
from ai_writer import AIWriter
from outreach import OutreachManager

def main():
    print("="*50)
    print("🤖 Bienvenue dans l'Agent de Génération de Leads (Wealth Agent) 🤖")
    print("="*50)
    
    # Vérification de l'environnement
    if not os.path.exists(".env"):
        print("⚠️ Le fichier .env est manquant. Créez-le à partir de .env.example")
        
    # Initialisation
    db = DatabaseManager('data/leads_database.db')
    scraper = ScraperManager(db)
    enricher = EnricherManager(db)
    ai_writer = AIWriter(db)
    outreach = OutreachManager(db)
    
    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Importer des leads depuis un CSV (Scraping Manuel)")
        print("2. Scraper Google Maps (Scraping Automatique)")
        print("3. Chercher les E-mails sur les sites Web (Enrichissement Gratuit)")
        print("4. Générer des Icebreakers (IA)")
        print("5. Exporter les leads 'Prêt à envoyer' en CSV")
        print("6. Envoyer les emails via SMTP (Automatique)")
        print("7. Statut de la Base de Données")
        print("0. Quitter")
        
        choix = input("\n👉 Votre choix : ")
        
        if choix == "1":
            fichier = input("Chemin du fichier CSV (ex: data/import.csv) : ")
            added = scraper.import_from_csv(fichier)
            print(f"[{added}] nouveaux leads ajoutés.")
            
        elif choix == "2":
            requete = input("Recherche ciblée (ex: Agences web à Bordeaux) : ")
            max_res = input("Nombre maximum de résultats (ex: 20) : ")
            try:
                max_res = int(max_res)
            except ValueError:
                max_res = 10
            
            print("\n🚀 Lancement du robot LinkedIn/Maps. Veuillez patienter...")
            added = scraper.search_google_maps(requete, max_res)
            print(f"[{added}] nouveaux leads ajoutés.")
            
        elif choix == "3":
            print("\n🔍 Aspiration automatique des adresses E-mail sur les sites web...")
            added = enricher.process_pending_leads()
            print(f"[{added}] e-mails trouvés et ajoutés à la base !")
            
        elif choix == "4":
            print("\nLancement de la génération d'Icebreakers via OpenAI...")
            processed = ai_writer.process_pending_leads()
            print(f"[{processed}] Icebreakers générés avec succès.")
            
        elif choix == "5":
            print("\nCréation du fichier d'export de campagne...")
            exported = outreach.export_to_csv()
            print(f"[{exported}] leads exportés.")
            
        elif choix == "6":
            print("\n🚀 Lancement de la campagne d'envoi d'emails (SMTP)...")
            sent = outreach.send_via_smtp()
            print(f"[{sent}] emails envoyés avec succès.")
            
        elif choix == "7":
            print("\n--- STATUT BDD ---")
            df = db.get_all_leads_as_df()
            if df.empty:
                print("La base de données est vide.")
            else:
                print(f"Total des leads : {len(df)}")
                print(df['status'].value_counts())
                
        elif choix == "0":
            print("À bientôt ! 👋")
            break
            
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()
