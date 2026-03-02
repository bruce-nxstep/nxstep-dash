import os
import json
import requests
import time
from dotenv import load_dotenv, set_key

load_dotenv(override=True)

class LinkedInAutomator:
    def __init__(self, db=None):
        load_dotenv(override=True)
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.person_urn = os.getenv("LINKEDIN_PERSON_URN")
        self.db = db
        self.api_version = "202602"

    def _get_headers(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": self.api_version,
            "X-Restli-Protocol-Version": "2.0.0"
        }

    def _get_creds(self, account_id):
        token, urn = self.access_token, self.person_urn
        if account_id and self.db:
            acc = self.db.get_linkedin_account(account_id)
            if acc:
                token, urn = acc['access_token'], acc['person_urn']
        return token, urn

    def post_to_linkedin(self, content, account_id=None):
        """Publie un post texte simple."""
        token, urn = self._get_creds(account_id)
        if not token or not urn: return False, "Auth manquante"

        url = "https://api.linkedin.com/rest/posts"
        headers = self._get_headers(token)
        payload = {
            "author": urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED"},
            "lifecycleState": "PUBLISHED"
        }
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code in [201, 200]: return True, "Posté"
            return False, f"Erreur API: {res.text}"
        except Exception as e: return False, str(e)

    def _generate_pdf_from_images(self, image_urls, output_path):
        from fpdf import FPDF
        from PIL import Image
        import io
        pdf = FPDF()
        for url in image_urls:
            if not url: continue
            try:
                img = None
                if str(url).startswith('http'):
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200: img = Image.open(io.BytesIO(res.content))
                elif os.path.exists(url):
                    img = Image.open(url)
                if img:
                    if img.mode != "RGB": img = img.convert("RGB")
                    # On ajuste l'image à la page A4 (210x297mm)
                    pdf.add_page()
                    pdf.image(img, x=0, y=0, w=210, h=297)
                    print(f"Image ajoutée au PDF: {url}")
            except Exception as e: print(f"Erreur image carousel ({url}): {e}")
        if len(pdf.pages) > 0:
            pdf.output(output_path)
            return True
        return False

    def post_carousel_pdf(self, content, pdf_path, title="Mon Carousel", account_id=None):
        """Publie un vrai document carousel via l'API rest/documents."""
        token, urn = self._get_creds(account_id)
        if not token or not urn: return False, "Auth manquante"
        if not os.path.exists(pdf_path): return False, "PDF manquant"

        # 1. Initialize Upload
        url = "https://api.linkedin.com/rest/documents?action=initializeUpload"
        headers = self._get_headers(token)
        payload = {"initializeUploadRequest": {"owner": urn}}
        
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code != 200: return False, f"Init upload fail: {res.text}"
            data = res.json()["value"]
            upload_url = data["uploadUrl"]
            document_urn = data["document"]
        except Exception as e: return False, f"Init Exception: {e}"

        # 2. Upload Binary
        try:
            with open(pdf_path, 'rb') as f:
                # PAS de JSON ici, brut binaire. PAS de LinkedIn-Version sur le PUT.
                upload_res = requests.put(upload_url, data=f.read(), headers={"Authorization": f"Bearer {token}"})
                if upload_res.status_code not in [200, 201]: 
                    return False, f"Upload binaire fail: {upload_res.status_code}"
        except Exception as e: return False, f"Upload Exception: {e}"

        # 3. Wait for processing (LinkedIn requirement)
        time.sleep(5)

        # 4. Create Post
        url = "https://api.linkedin.com/rest/posts"
        headers = self._get_headers(token)
        payload = {
            "author": urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED"},
            "content": {
                "media": {
                    "id": document_urn,
                    "title": title
                }
            },
            "lifecycleState": "PUBLISHED"
        }
        try:
            res = requests.post(url, headers=headers, json=payload)
            if res.status_code in [201, 200]: return True, "Carousel posté avec succès"
            return False, f"Erreur Final Post: {res.text}"
        except Exception as e: return False, f"Final Post Exception: {e}"

    def get_user_info(self, token=None):
        t = token or self.access_token
        if not t: return None
        res = requests.get("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {t}"})
        return res.json() if res.status_code == 200 else None

    def get_authorization_url(self):
        base = "https://www.linkedin.com/oauth/v2/authorization"
        scopes = "w_member_social profile openid email"
        return f"{base}?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&state=foobar&scope={scopes}"

    def exchange_code_for_token(self, code):
        url = "https://api.linkedin.com/oauth/v2/accessToken"
        data = {"grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri, "client_id": self.client_id, "client_secret": self.client_secret}
        res = requests.post(url, data=data)
        if res.status_code == 200:
            d = res.json()
            tk = d["access_token"]
            u = self.get_user_info(tk)
            if u:
                name = f"{u.get('given_name','')} {u.get('family_name','')}".strip() or u.get('name','User')
                urn = f"urn:li:person:{u['sub']}"
                if self.db: self.db.add_or_update_linkedin_account(name, urn, tk)
                return True, f"Connecté : {name}"
        return False, f"Erreur : {res.text}"
