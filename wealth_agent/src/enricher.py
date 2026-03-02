import requests
from bs4 import BeautifulSoup
import re

class EnricherManager:
    def __init__(self, db_manager):
        self.db = db_manager
        
    def find_email_on_website(self, url):
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            # Simple RegEx pour trouver les emails
            emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text))
            
            # Filtrer les faux positifs (comme les formats d'image .png@2x)
            valid_emails = [e for e in emails if e.endswith(('.com', '.fr', '.net', '.org', '.io', '.co'))
                            and not e.startswith('sentry') and not 'wixpress' in e]
            
            if valid_emails:
                return valid_emails[0]
                
            # Pas trouve sur la page d'accueil ? Chercher la page contact
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if 'contact' in href or 'about' in href:
                    if href.startswith('/'):
                        href = url.rstrip('/') + href
                    elif not href.startswith('http'):
                        continue
                    
                    try:
                        contact_resp = requests.get(href, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                        contact_emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", contact_resp.text))
                        valid_contact_emails = [e for e in contact_emails if e.endswith(('.com', '.fr', '.net', '.org', '.io', '.co'))]
                        if valid_contact_emails:
                            return valid_contact_emails[0]
                    except:
                        pass
                        
            return None
        except Exception as e:
            return None

    def process_pending_leads(self) -> int:
        print("Lancement de l'enrichissement (Email Web Scraping)...")
        df = self.db.get_leads_by_status('Scrapé')
        
        if df.empty:
            print("Aucun lead a enrichir.")
            return 0
            
        found_count = 0
        for index, row in df.iterrows():
            lead_id = row['id']
            company = row['company_name']
            website = row['website']
            
            if not website or website == 'N/A':
                self.db.update_lead(lead_id, {'status': 'Email Introuvable'})
                continue
                
            print(f"Recherche pour : {company} ({website})")
            email = self.find_email_on_website(website)
            
            if email:
                print(f"  -> Email trouve: {email}")
                self.db.update_lead(lead_id, {'email': email, 'status': 'Enrichi'})
                found_count += 1
            else:
                self.db.update_lead(lead_id, {'status': 'Email Introuvable'})
                
        return found_count
