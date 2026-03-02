import time
from playwright.sync_api import sync_playwright

class ScraperManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def search_google_maps(self, query: str, max_results: int = 10) -> int:
        """
        Recherche des entreprises sur Google Maps via Playwright,
        puis insère les résultats dans la BDD.
        Retourne le nombre de nouveaux leads ajoutés.
        """
        print(f"Demarrage du scraper Google Maps pour '{query}' (Max: {max_results} resultats)...")
        added_count = 0
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_default_timeout(10000)
                
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
                print(f"Navigation vers {search_url}...")
                page.goto(search_url)
                
                # Gérer le consentement cookie Google si présent
                try:
                    accept_btn = page.locator("button:has-text('Tout accepter'), button:has-text('Accept all')").first
                    accept_btn.click(timeout=5000)
                    time.sleep(2)
                except Exception:
                    pass

                # Attendre le chargement des résultats
                try:
                    page.wait_for_selector("div[role='feed']", timeout=15000)
                except Exception:
                    print("Aucun resultat trouve ou timeout.")
                    browser.close()
                    return 0

                # Scroll simple pour charger plus de résultats
                feed = page.locator("div[role='feed']")
                for _ in range(max_results // 5 + 1):
                    feed.hover()
                    page.mouse.wheel(0, 5000)
                    time.sleep(2)
                
                # Extraction des informations
                items = page.locator("div[role='feed'] > div > div > a").all()
                for i, item in enumerate(items[:max_results]):
                    try:
                        company_name = item.get_attribute("aria-label")
                        if not company_name:
                            continue
                        
                        # Clic pour ouvrir le détail
                        item.click()
                        time.sleep(2)
                        
                        # Récupérer le site web si présent
                        website = None
                        try:
                            website_el = page.locator("a[data-item-id='authority']").first
                            if website_el.is_visible():
                                website = website_el.get_attribute("href")
                        except Exception:
                            pass
                            
                        # Ajouter le lead en base
                        if self.db.add_lead(company_name=company_name, website=website):
                            print(f"Trouve : {company_name} | Web: {website or 'N/A'}")
                            added_count += 1
                            
                    except Exception as e:
                        print(f"Erreur d'extraction sur un item : {e}")
                
                browser.close()
                return added_count
                
        except Exception as e:
            print(f"Erreur fatale du scraper: {e}")
            return added_count

    def import_from_csv(self, file_path: str) -> int:
        """Imports leads from a CSV file into the database."""
        import pandas as pd
        print(f"Importation des leads depuis {file_path}...")
        try:
            df = pd.read_csv(file_path)
            added = 0
            for _, row in df.iterrows():
                # Map CSV columns to BDD fields
                if self.db.add_lead(
                    company_name=row.get('company_name', row.get('name')),
                    website=row.get('website')
                ):
                    added += 1
            print(f"{added} leads importés avec succès.")
            return added
        except Exception as e:
            print(f"Erreur import CSV: {e}")
            return 0
