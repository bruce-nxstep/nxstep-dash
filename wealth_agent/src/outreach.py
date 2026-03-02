import os
import smtplib
from email.mime.text import MIMEText
import sqlite3
import pandas as pd
from dotenv import load_dotenv

class OutreachManager:
    def __init__(self, db_manager):
        load_dotenv() # Charger les clefs SMTP (server, port, user, etc.)
        self.db = db_manager
        
    def send_via_smtp(self) -> int:
        print("Preparation de la campagne d'envoi SMTP (sans Lemlist)...")
        df = self.db.get_leads_by_status('Prêt à envoyer')
        
        if df.empty:
            print("Aucun lead n'est pret a etre envoye.")
            return 0
            
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port_str = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        
        if not smtp_server or not smtp_user or not smtp_password:
            print("Erreur: Identifiants SMTP manquants dans le fichier .env.")
            return 0
            
        try:
            smtp_port = int(smtp_port_str)
        except (ValueError, TypeError):
            print("Erreur: Port SMTP invalide.")
            return 0
            
        sent_count = 0
        try:
            print(f"Connexion au serveur SMTP {smtp_server}:{smtp_port}...")
            # STARTTLS encryption
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            
            for index, row in df.iterrows():
                if not row['email']:
                    continue
                    
                msg = MIMEText(row['icebreaker'])
                msg['Subject'] = "Une opportunite de collaboration"
                msg['From'] = smtp_user
                msg['To'] = row['email']
                
                print(f"Envoi de l'email a : {row['email']}...")
                try:
                    server.send_message(msg)
                    self.db.update_lead(row['id'], {'status': 'Envoyé SMTP'})
                    sent_count += 1
                except Exception as e:
                    print(f"Erreur lors de l'envoi a {row['email']} : {e}")
                    
            server.quit()
        except smtplib.SMTPAuthenticationError:
            print("Erreur d'authentification SMTP: Verifiez email et mot de passe.")
        except Exception as e:
            print(f"Erreur fatale SMTP: {e}")
            
        return sent_count
