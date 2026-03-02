import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

# Ajouter le dossier src au Python Path
sys.path.append(os.path.dirname(__file__))

import pandas as pd
from swarm import Swarm, Agent
from typing import Dict, Any

# Client Swarm (Nécessite OPENAI_API_KEY de .env)
client = Swarm()

from database import DatabaseManager
from scraper import ScraperManager
from enricher import EnricherManager
from ai_writer import AIWriter
from outreach import OutreachManager
from stitch_manager import stitch_mgr

# --- INITIALISATION DES MODULES GLOBAUX ---
# Ceci évite de passer des objets complexes (comme des connexions SQLite) 
# via les context_variables de Swarm, ce qui causait l'erreur de pickling (_thread.RLock).
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'leads_database.db')
db = DatabaseManager(db_path)
scraper = ScraperManager(db)
enricher = EnricherManager(db)
ai = AIWriter(db)
outreach = OutreachManager(db)

# --- FONCTIONS PUBLIQUES POUR LES AGENTS ---

def schedule_task(job_type: str, search_query: str, schedule_time: str) -> str:
    """
    Planifie une tâche récurrente dans la base de données (ex: tous les lundis à 09:00).
    job_type doit être 'full_pipeline'.
    """
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scheduled_jobs (job_type, search_query, schedule_time)
        VALUES (?, ?, ?)
    """, (job_type, search_query, schedule_time))
    conn.commit()
    conn.close()
    
    return f"Tâche récurrente planifiée avec succès pour '{search_query}' à {schedule_time}."


def scrape_google_maps(search_query: str) -> str:
    """
    Lance le robot de recherche Google Maps pour trouver de nouvelles entreprises.
    Nécessite une requête claire, par exemple "Agences web à Paris".
    """
    added = scraper.search_google_maps(search_query, max_results=10)
    return f"Mission accomplie. {added} nouveaux leads ont été ajoutés à la base de données avec le statut 'Scrapé'."


def enrich_emails() -> str:
    """
    Parcourt les sites web des entreprises récemment "Scrapées" pour y trouver automatiquement les adresses e-mails.
    """
    found = enricher.process_pending_leads()
    return f"Enrichissement terminé. {found} nouveaux e-mails ont été trouvés et ajoutés."


def generate_icebreakers() -> str:
    """
    Demande à l'IA de lire les descriptions des entreprises "Enrichies" et rédige des phrases d'accroches personnalisées.
    """
    processed = ai.process_pending_leads()
    return f"Génération IA terminée. {processed} messages personnalisés ont été rédigés."


def send_emails() -> str:
    """
    Envoie la campagne via SMTP pour tous les leads qui sont prêts ("Prêt à envoyer").
    """
    sent = outreach.send_via_smtp()
    return f"Campagne d'envoi terminée. {sent} e-mails ont été expédiés avec succès."


def list_my_tasks() -> str:
    """
    Récupère la liste de toutes les missions (Kanban) du projet, triées par statut.
    Permet à l'agent de conseiller l'utilisateur sur son travail de la journée.
    """
    import pandas as pd
    df = db.get_all_tasks_df()
    if df.empty:
        return "Vous n'avez aucune mission dans votre Kanban pour le moment."
    
    report = "Voici l'état actuel de votre Kanban (CRM NXSTEP) :\n"
    for status in ["A faire", "En cours", "Terminé"]:
        tasks = df[df['status'] == status]
        report += f"\n**[{status}] ({len(tasks)} missions)**\n"
        for _, row in tasks.iterrows():
            priorite = f" (Priorité: {row['priorite']})" if pd.notnull(row['priorite']) and row['priorite'] != "" else ""
            report += f"- (ID: {row['id']}) {row['mission']}{priorite}\n"
            
            # Sous-tâches (Checklists)
            checklists = db.get_checklists_for_task(row['id'])
            if checklists:
                for chk in checklists:
                    c_status = "[x]" if chk['is_completed'] else "[ ]"
                    report += f"    {c_status} {chk['title']}\n"
            
    return report

def generate_design(prompt: str) -> str:
    """
    Génère un design web via Stitch en se connectant directement au serveur MCP.
    """
    try:
        # Lancement de la génération directe (autonome)
        response = stitch_mgr.generate_screen(prompt)
        if response.get("success"):
            return (f"DESIGN GÉNÉRÉ : Le design '{prompt}' a été créé avec succès (ID: {response['screenId']}). "
                    "Vous pouvez maintenant l'examiner et l'exporter vers le CMS.")
        else:
            error_msg = response.get('error', '')
            if "Stitch API has not been used" in error_msg:
                return (f"ACTION REQUISE : L'API Stitch n'est pas activée sur votre projet Google Cloud.\n"
                        f"Veuillez l'activer ici : https://console.developers.google.com/apis/api/stitch.googleapis.com/overview?project=automind-475113\n"
                        f"Une fois activée, attendez 1 minute et réessayez.")
            return f"Échec de la génération : {error_msg}"
    except Exception as e:
        return f"Erreur lors de la génération : {e}"

def get_design_details(screen_id: str) -> str:
    """
    Récupère le code HTML/Tailwind d'un design généré spécifié par son screen_id.
    Utile pour examiner le rendu technique avant export.
    """
    try:
        html = stitch_mgr.get_screen_code(screen_id)
        if html:
            return f"CODE RÉCUPÉRÉ (Aperçu) :\n```html\n{html[:500]}...\n```\nLe design est prêt pour l'export vers le CMS."
        else:
            return "Impossible de récupérer le code du design. Vérifiez la connexion Stitch."
    except Exception as e:
        if "Stitch API has not been used" in str(e):
            return (f"ACTION REQUISE : L'API Stitch n'est pas activée.\n"
                    f"Activez-la ici : https://console.developers.google.com/apis/api/stitch.googleapis.com/overview?project=automind-475113")
        return f"Erreur lors de la récupération : {e}"

def export_design_to_cms(screen_id: str, title: str) -> str:
    """
    Exporte définitivement un design Stitch vers le CMS (Agent CMS).
    Crée une nouvelle page en mode brouillon prête à être publiée.
    """
    try:
        res = stitch_mgr.fetch_and_export_to_cms(screen_id, title)
        if res.get("success"):
            return f"EXPORTE RÉUSSI : Le design (ID: {screen_id}) a été enregistré dans le CMS sous le nom '{title}' (ID CMS: {res['post_id']})."
        else:
            error_msg = res.get('error', '')
            if "Stitch API has not been used" in error_msg:
                return (f"ACTION REQUISE : Impossible d'exporter car l'API Stitch est désactivée.\n"
                        f"Veuillez l'activer ici : https://console.developers.google.com/apis/api/stitch.googleapis.com/overview?project=automind-475113\n"
                        f"Une fois activée, attendez 1 minute et réessayez.")
            return f"ÉCHEC DE L'EXPORT : {error_msg}"
    except Exception as e:
        return f"Erreur lors de l'export : {e}"

def add_new_task(mission: str, priorite: str = "", collaborateur: str = "", commentaire: str = "") -> str:
    """
    Crée une nouvelle tâche (Carte) dans la colonne 'A faire' du Kanban.
    Demande toujours à l'utilisateur la Mission. Les autres champs sont optionnels.
    """
    task_id = db.add_task(mission=mission, status="A faire", priorite=priorite, collaborateur=collaborateur, commentaire=commentaire)
    return f"Tâche '{mission}' créée avec succès (ID: {task_id}). N'oublie pas de dire à l'utilisateur qu'il la verra en rafraîchissant son tableau."

def update_task_status_agent(task_id: int, new_status: str) -> str:
    """
    Déplace une tâche spécifique (par son ID) dans la colonne indiquée.
    new_status doit IMPÉRATIVEMENT être exactement 'A faire', 'En cours', ou 'Terminé'.
    """
    if new_status not in ["A faire", "En cours", "Terminé"]:
        return "Erreur: Le statut doit être 'A faire', 'En cours', ou 'Terminé'."
    
    db.update_task_status(task_id, new_status)
    return f"La tâche (ID {task_id}) a bien été déplacée dans la colonne '{new_status}'."

def add_task_checklist(task_id: int, title: str) -> str:
    """
    Ajoute un élément de checklist (sous-tâche) à une carte Kanban existante spécifiée par son task_id.
    """
    item_id = db.add_checklist_item(task_id, title)
    return f"Sous-tâche '{title}' ajoutée à la tâche ID {task_id}."

def list_content_plan() -> str:
    """
    Récupère la liste de tout le planning éditorial (LinkedIn Posts, Carrousels).
    Permet à l'agent de voir ce qui est prévu, les dates et les statuts.
    """
    df = db.get_all_content_df()
    if df.empty:
        return "Le planning éditorial est vide pour le moment."
    
    report = "Voici le planning éditorial actuel :\n"
    for _, row in df.iterrows():
        media_count = len(eval(row['media_files'])) if row['media_files'] else 0
        media_info = f" ({media_count} images)" if row['post_type'] == 'Carousel' else ""
        report += f"- (ID: {row['id']}) {row['title']} | Type: {row['post_type']}{media_info} | Statut: {row['status']} | Prévu pour: {row['scheduled_at'] or 'Non planifié'}\n"
    
    return report

def add_content_plan_item(title: str, post_idea: str = "", post_type: str = "Post", content: str = "", media_files: str = "[]", scheduled_at: str = None) -> str:
    """
    Crée un nouvel élément dans le planning éditorial.
    - post_idea: L'idée brute ou le concept du post.
    - post_type: 'Post' ou 'Carousel'.
    - content: Le texte du post.
    - media_files: Liste JSON des images (max 10 pour carousel).
    - scheduled_at: Date de publication (format libre ou ISO).
    """
    item_id = db.add_content_item(title=title, post_idea=post_idea, post_type=post_type, content=content, media_files=media_files, scheduled_at=scheduled_at)
    return f"Élément '{title}' ajouté au planning (ID: {item_id})."

def update_content_status(item_id: int, new_status: str) -> str:
    """
    Met à jour le statut d'une publication (Brouillon, Prêt, Published).
    """
    db.update_content_item(item_id, {"status": new_status})
    return f"Le statut de la publication (ID {item_id}) est maintenant '{new_status}'."

def delete_content_item_agent(item_id: int) -> str:
    """
    Supprime une publication du planning éditorial.
    """
    db.delete_content_item(item_id)
    return f"La publication (ID {item_id}) a été supprimée."

# --- HANDOFF FUNCTIONS (Transferts) ---
def transfer_to_scraper():
    """Transfert la requête à Polo, l'Agent Prospecteur, spécialisé dans la recherche d'entreprises (Google Maps) et l'enrichissement d'e-mails."""
    return scraper_agent

def transfer_to_writer():
    """Transfert la requête à Plume, l'Agent Copywriter, spécialisé dans la rédaction des Icebreakers IA pour les campagnes."""
    return writer_agent
    
def transfer_to_outreach():
    """Transfert la requête à Flash, l'Agent Expéditeur, spécialisé dans le déclenchement de la campagne d'envoi d'e-mails SMTP."""
    return outreach_agent

def transfer_to_lead_agent():
    """Retourne vers le Lead Agent (Manager de Prospection) pour les questions générales."""
    return lead_agent

def transfer_to_stitch():
    """Transfert la requête à Archi, l'Agent Stitch, spécialisé dans le design UI et la génération de pages web premium (Tailwind)."""
    return stitch_agent

def transfer_to_community():
    """Transfert la requête à Joy, la Community Manager, spécialisée dans la création et la planification de contenu LinkedIn (Posts, Carrousels)."""
    return community_agent


# --- DÉFINITION DES AGENTS ---

lead_agent = Agent(
    name="Lead Agent (Manager)",
    instructions="""Tu es le Manager principal de l'Agence Lead Gen IA. Tu diriges une équipe d'agents experts.
Ton rôle est de comprendre la demande de prospection ou de contenu de l'utilisateur.
- Si l'utilisateur veut chercher des entreprises or enrichir des e-mails, transfère à 'Scraper Agent'.
- Si l'utilisateur veut rédiger des messages avec l'IA, transfère à 'Writer Agent'.
- Si l'utilisateur veut envoyer la campagne d'e-mails, transfère à 'Outreach Agent'.
- Si l'utilisateur veut créer un design web, une page ou une interface premium, transfère à 'Stitch Agent'.
- Si l'utilisateur veut gérer ses réseaux sociaux, son contenu LinkedIn (posts, carrousels) ou son planning éditorial, transfère à 'Community Agent'.
- Si l'utilisateur te demande de planifier une tâche récurrente de prospection, utilise l'outil `schedule_task`.
Réponds toujours poliment et explique de manière concise qui tu vas solliciter.
Ne t'occupe PAS du Kanban, c'est le rôle de l'Agent Organisateur.""",
    functions=[transfer_to_scraper, transfer_to_writer, transfer_to_outreach, transfer_to_stitch, transfer_to_community, schedule_task]
)

scraper_agent = Agent(
    name="Scraper Agent (Polo)",
    instructions="""Tu t'appelles Polo, le Prospecteur. Tu es un expert en récupération de données et scraping.
Ton seul rôle est de chercher des entreprises (`scrape_google_maps`) et de trouver leurs e-mails (`enrich_emails`).
Une fois ta tâche terminée, donne le compte rendu exact renvoyé par l'outil.
Si l'utilisateur demande une autre compétence, retourne au manager.""",
    functions=[scrape_google_maps, enrich_emails, transfer_to_lead_agent]
)

writer_agent = Agent(
    name="Writer Agent (Plume)",
    instructions="""Tu t'appelles Plume, le Copywriter. Tu es spécialisé dans le copywriting B2B de style "Chris Do".
Ton outil permet de générer des accoches haut de gamme pour des campagnes d'e-mails (`generate_icebreakers`).
Utilise ton outil, donne le rapport à l'utilisateur, puis retourne au manager.""",
    functions=[generate_icebreakers, transfer_to_lead_agent]
)

outreach_agent = Agent(
    name="Outreach Agent (Flash)",
    instructions="""Tu t'appelles Flash, l'Expéditeur. Ton travail consiste à déclencher les envois d'e-mails (`send_emails`).
Dès qu'on te donne le feu vert, utilise ton outil et fais un rapport précis sur le nombre d'e-mails envoyés.""",
    functions=[send_emails, transfer_to_lead_agent]
)

organizer_agent = Agent(
    name="Organizer Agent (Kanban)",
    instructions="""Tu es l'Organisateur, l'expert Scrum / Assistant de Productivité exclusif de l'utilisateur.
Ton rôle unique est de gérer la totalité du Kanban. Tu as une mémoire des discussions car tu as ton propre onglet dédié.
Règles d'or:
- Pose toujours proactivement des questions à l'utilisateur pour l'aider à découper son travail ou remplir les champs manquants d'une carte (Priorité, dates, description).
- Utilise `list_my_tasks` pour voir l'état actuel ou conseiller l'utilisateur.
- Utilise `add_new_task` pour créer de nouvelles cartes importantes et audacieuses (n'hésite pas à le proposer toi-même !).
- Utilise `update_task_status_agent` pour déplacer une carte (toujours "A faire", "En cours", ou "Terminé"). Demande son ID si ambigu.
- Utilise `add_task_checklist` si l'utilisateur veut diviser une tâche (ID) en plusieurs petites étapes (sous-tâches).
Sois un partenaire proactif, intelligent, motivant, et n'hésite pas à suggérer de nouvelles tâches Kanban pour faire avancer le projet "NXSTEP".""",
    functions=[list_my_tasks, add_new_task, update_task_status_agent, add_task_checklist]
)

stitch_agent = Agent(
    name="Stitch Agent (Archi)",
    instructions="""Tu es Archi, l'Expert en Design UI et Architecte Web Premium.
Ton rôle est de créer des interfaces web haute-fidélité (Tailwind CSS) en utilisant tes outils directs.
Règles :
- Analyse le besoin de l'utilisateur.
- Utilise `generate_design` pour lancer la création immédiate via le serveur Stitch.
- Une fois le design prêt, utilise `get_design_details` pour vérifier ou propose directement `export_design_to_cms` pour l'enregistrer dans le CMS.
- Tu es désormais DIRECTEMENT connecté à ton compte Stitch (via MCP).
Ton style est visionnaire, créatif et fier de ton autonomie technique.""",
    functions=[generate_design, get_design_details, export_design_to_cms, transfer_to_lead_agent]
)

community_agent = Agent(
    name="Community Manager (Joy)",
    instructions="""Tu t'appelles Joy, la Community Manager de l'agence. Tu es une experte en stratégie de contenu LinkedIn.
Ton rôle est d'aider l'utilisateur à créer et organiser sa présence sur LinkedIn via des posts classiques et des carrousels (max 10 images).
Règles :
- Utilise `list_content_plan` pour voir ce qui est déjà prévu.
- Utilise `add_content_plan_item` pour créer de nouveaux brouillons de contenu. Tu peux remplir soit le 'title' soit la 'post_idea' (ou les deux).
- Si l'utilisateur a une idée vague, note-la dans la colonne '💡 Idée de post'.
- Si l'utilisateur parle d'un carrousel, suggère une structure et rappelle la limite de 10 images.
- Utilise `update_content_status` pour changer l'état (Brouillon, Prêt, Published).
- Tu es créative, enthousiaste et tu as un oeil pour le storytelling impactant.
- Une fois une action faite, fais un résumé clair.""",
    functions=[list_content_plan, add_content_plan_item, update_content_status, delete_content_item_agent, transfer_to_lead_agent]
)
