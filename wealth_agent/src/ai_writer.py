import os
from openai import OpenAI
import sqlite3
import pandas as pd
from dotenv import load_dotenv

class AIWriter:
    def __init__(self, db_manager):
        load_dotenv()
        self.db = db_manager
        self.client = OpenAI()
        
    def generate_icebreaker(self, company_name: str, website: str) -> str:
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'generate_icebreaker.txt')
        
        system_prompt = "Tu es un expert en Cold Email"
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                
        user_message = f"Entreprise: {company_name}\nSite web: {website}\nRedige une accroche B2B personnalisee et breve."
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Erreur OpenAI: {e}")
            return None

    def process_pending_leads(self) -> int:
        print("Demarrage de la generation par l'IA...")
        df = self.db.get_leads_by_status('Enrichi')
        
        if df.empty:
            print("Aucun lead a rediger.")
            return 0
            
        processed_count = 0
        for index, row in df.iterrows():
            lead_id = row['id']
            company = row['company_name']
            
            print(f"Redaction pour : {company}...")
            # row can be a Series or a dict, accessing via brackets
            website = row['website'] if 'website' in row else ''
            icebreaker = self.generate_icebreaker(company, website)
            
            if icebreaker:
                self.db.update_lead(lead_id, {'icebreaker': icebreaker, 'status': 'Prêt à envoyer'})
                processed_count += 1
                
        return processed_count
