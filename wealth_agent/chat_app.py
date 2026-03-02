import os
import sys

# Ensure src is in path FIRST, before any local imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st
import importlib
import database
importlib.reload(database)
from database import DatabaseManager
from scraper import ScraperManager
from enricher import EnricherManager
from ai_writer import AIWriter
from outreach import OutreachManager
from google_sync import GoogleSheetSync
from cms_database import CMSDatabase as _CMSDB
from site_generator import SiteGenerator as _SiteGen
import pandas as pd
import time
import subprocess
import socket
import threading
import pathlib as _pathlib
import json
import base64
from streamlit_calendar import calendar


# --- WINDOWS DLL FIX FOR pywin32 / pywintypes ---
if os.name == 'nt':
    _venv_root = os.path.join(os.path.dirname(__file__), 'venv')
    _pywin32_dll_path = os.path.join(
        _venv_root, 'Lib', 'site-packages', 'pywin32_system32')
    _win32_path = os.path.join(_venv_root, 'Lib', 'site-packages', 'win32')

    # Force DLL paths
    if os.path.exists(_pywin32_dll_path):
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(_pywin32_dll_path)
        os.environ["PATH"] = _pywin32_dll_path + \
            os.pathsep + os.environ["PATH"]

    # Try bootstrap
    try:
        sys.path.append(_win32_path)
        sys.path.append(os.path.join(_win32_path, 'lib'))
        import pywin32_bootstrap
    except ImportError:
        pass


# Ajouter le dossier src au Python Path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))


# --- HELPERS ---
def get_image_base64(path):
    if not path or not os.path.exists(path):
        return None
    try:
        import base64
        ext = path.split('.')[-1].lower()
        mime = "image/png"
        if ext in ['jpg', 'jpeg']: mime = "image/jpeg"
        elif ext == 'gif': mime = "image/gif"
        
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{encoded}"
    except:
        return None
st.set_page_config(page_title="Wealth Agent (NXSTEP)",
                   page_icon="🤖", layout="wide")


# --- INITIALISATION DES MODULES ---
def init_modules():
    db_path = os.path.join(os.path.dirname(__file__),
                           'data', 'leads_database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = DatabaseManager(db_path)
    return {
        "db": db,
        "scraper": ScraperManager(db),
        "enricher": EnricherManager(db),
        "ai": AIWriter(db),
        "outreach": OutreachManager(db),
        "google_sync": GoogleSheetSync('https://docs.google.com/spreadsheets/d/1t_wqRbUD4KhdGHlwALBKzgBJcFskGV9QJqGHm892NuU')
    }


modules = init_modules()
db = modules["db"]
google_sync = modules["google_sync"]

# --- STORYBOOK AUTO-START ---

# ── Init CMS DB & SSG Trigger ────────────────────────────────────────────────
_cmsdb = _CMSDB(os.path.join(os.path.dirname(__file__), "data", "cms.db"))
_dist_path = _pathlib.Path(os.path.dirname(__file__)) / "dist"


def _trigger_ssg():
    """Helper to run the Static Site Generator and show a toast."""
    try:
        _gen = _SiteGen(_cmsdb.db_path)
        _gen.generate_site()
        st.info("🌐 Design System synchronisé : Site statique mis à jour !", icon="🚀")
    except Exception as _e:
        st.error(f"⚠️ Erreur auto-génération : `{_e}`")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


@st.cache_resource
def start_storybook_server():
    """Starts Storybook in the background if it's not already running."""
    if is_port_in_use(6008):
        print(">>> Storybook is already running on port 6008.")
        return None

    print(">>> Starting Storybook automatically in the background...")
    # Find the nxstep_site root directory
    app_dir = os.path.dirname(os.path.dirname(__file__))

    # Run npx storybook dev -p 6008 in a separated process
    process = subprocess.Popen(
        "npx storybook dev -p 6008",
        cwd=app_dir,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return process


# Ensures this runs exactly once when Streamlit boots
storybook_process = start_storybook_server()

# --- GESTION DE L'ETAT (Chat Histories) ---

HISTORY_FILE = os.path.join(os.path.dirname(
    __file__), 'data', 'chat_history.json')


def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"lead_messages": [], "kanban_messages": [], "design_messages": [], "cms_messages": [], "stitch_messages": [], "community_messages": []}


def save_chat_history(lead_msgs, kanban_msgs, design_msgs, cms_msgs=None, stitch_msgs=None, community_msgs=None):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "lead_messages": lead_msgs,
            "kanban_messages": kanban_msgs,
            "design_messages": design_msgs,
            "cms_messages": cms_msgs or [],
            "stitch_messages": stitch_msgs or [],
            "community_messages": community_msgs or [],
        }, f, ensure_ascii=False, indent=2)


persisted_history = load_chat_history()

if "lead_messages" not in st.session_state:
    if persisted_history["lead_messages"]:
        st.session_state.lead_messages = persisted_history["lead_messages"]
    else:
        st.session_state.lead_messages = [
            {"role": "assistant",
                "content": "Bonjour ! Je suis le Manager de prospection (Lead Agent). Je peux chercher des agences, récupérer leurs emails, ou envoyer votre campagne. Que souhaitez-vous faire ?"}
        ]

if "kanban_messages" not in st.session_state:
    if persisted_history.get("kanban_messages"):
        st.session_state.kanban_messages = persisted_history["kanban_messages"]
    else:
        st.session_state.kanban_messages = [
            {"role": "assistant", "content": "Salut ! Je suis votre Organisateur Kanban 📋🚀. Listons vos tâches de la semaine, ou créez-en de nouvelles ensemble !"}
        ]

if "design_messages" not in st.session_state:
    if persisted_history.get("design_messages"):
        st.session_state.design_messages = persisted_history["design_messages"]
    else:
        st.session_state.design_messages = [
            {"role": "assistant", "content": "Bienvenue ! Je suis Archi, l'Agent Design System 🎨✨. Comment puis-je vous aider avec l'interface aujourd'hui ?"}
        ]

if "cms_messages" not in st.session_state:
    if persisted_history.get("cms_messages"):
        st.session_state.cms_messages = persisted_history["cms_messages"]
    else:
        st.session_state.cms_messages = [
            {"role": "assistant",
                "content": "Bonjour ! Je suis votre **Expert Content Architect** ✍️\n\nJe structure et génère du contenu pour votre CMS Headless en JSON prêt à l'API.\n\n**Que puis-je faire pour vous ?**\n- Créer une nouvelle page ou un article\n- Optimiser le SEO (meta-titres, descriptions, H1-H6)\n- Structurer du contenu existant\n- Générer des slugs propres\n\n*Exemple : \"Crée une page de présentation pour NXSTEP, ton de marque professionnel\"*"}
        ]

if "stitch_messages" not in st.session_state:
    if persisted_history.get("stitch_messages"):
        st.session_state.stitch_messages = persisted_history["stitch_messages"]
    else:
        st.session_state.stitch_messages = [
            {"role": "assistant", "content": "Bonjour ! Je suis Archi, votre **Stitch Agent** 🎨✨\n\nJe suis connecté au serveur Stitch pour générer des designs web haute-fidélité avec Tailwind CSS.\n\n**Que souhaitez-vous créer ?**\n- Une landing page pour un nouveau produit\n- Un dashboard SaaS moderne\n- Une section Hero animée\n\n*Une fois le design généré, vous pourrez l'importer directement dans votre CMS !*"}
        ]

if "community_messages" not in st.session_state:
    if persisted_history.get("community_messages"):
        st.session_state.community_messages = persisted_history["community_messages"]
    else:
        st.session_state.community_messages = [
            {"role": "assistant", "content": "Salut ! Je suis Joy, votre **Community Manager** 📱✨. Je vous aide à planifier vos posts LinkedIn et vos carrousels. Prêt à faire exploser votre visibilité ?"}
        ]

# Un seul appel CSS minimal - uniquement pour masquer le branding Streamlit
st.markdown(
    '<style>#MainMenu,footer,[data-testid="stToolbar"]{visibility:hidden}</style>', unsafe_allow_html=True)

# --- SIDEBAR & NAVIGATION ---
PAGES = [
    "► Prospection Lead",
    "▦ Kanban & Organisation",
    "📱 Community Manager",
    "▤ Base de données",
    "◈ Design System",
    "✍️ Agent CMS",
    "🎨 Stitch Design",
    "❓ FAQ Stitch",
]
PAGE_KEYS = ["lead", "kanban", "community", "database",
             "design", "cms", "stitch", "faq_stitch"]

# Read page from URL query param (survives browser reload)
_url_page = st.query_params.get("page", "lead")
_default_idx = PAGE_KEYS.index(_url_page) if _url_page in PAGE_KEYS else 0

with st.sidebar:
    st.markdown("### ◆ NXSTEP IA")

    current_page = st.radio(
        "Navigation",
        PAGES,
        index=_default_idx,
        label_visibility="collapsed",
        key="current_page",
    )

    # Persist selection in URL so browser reload restores the same tab
    _selected_key = PAGE_KEYS[PAGES.index(current_page)]
    if st.query_params.get("page") != _selected_key:
        st.query_params["page"] = _selected_key

    st.markdown("---")
    st.markdown("**Tableau de Bord**")
    df = db.get_all_leads_as_df()
    if df.empty:
        st.info("La base de données est vide.")
    else:
        st.metric("Total Leads", len(df))
        status_counts = df['status'].value_counts()
        for status, count in status_counts.items():
            st.metric(f"Statut : {status}", count)

    st.markdown("---")
    if st.button("△ Réinitialiser la Base", help="Remet tous les leads au statut initial. Irréversible."):
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        conn.cursor().execute(
            "UPDATE leads SET status='Scrapé', icebreaker=NULL, email=NULL WHERE website IS NOT NULL")
        conn.commit()
        st.success("Base réinitialisée avec succès.")
        st.rerun()

# --- AFFICHAGE DE LA VUE SELECTIONNEE ---

if current_page == "► Prospection Lead":
    st.title("► Prospection Lead")
    st.markdown(
        "Votre expert en scraping B2B, enrichissement et envoi d'e-mails.")
    # Affichage de l'historique Lead Agent
    for message in st.session_state.lead_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- LOGIQUE DU CHATBOT LEAD ---
    if prompt := st.chat_input("Ex: Cherche des agences web tous les lundis à 08:30"):
        # 1. Afficher la question de l'utilisateur
        st.session_state.lead_messages.append(
            {"role": "user", "content": prompt})
        save_chat_history(st.session_state.lead_messages,
                          st.session_state.kanban_messages, st.session_state.design_messages,
                          community_msgs=st.session_state.community_messages)
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Exécuter l'action via l'Orchestrateur Multi-Agents (Swarm)
        from orchestrator import client, lead_agent

        with st.chat_message("assistant"):
            with st.spinner("Le Manager Prospection réfléchit et délègue..."):

                # Formater l'historique pour Swarm
                swarm_messages = [{"role": msg["role"], "content": msg["content"]}
                                  for msg in st.session_state.lead_messages]

                try:
                    # Appel de Swarm
                    response = client.run(
                        agent=lead_agent,
                        messages=swarm_messages,
                        context_variables={}
                    )

                    response_content = response.messages[-1].get("content", "")

                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    response_content = f"Désolé, une erreur technique s'est produite avec mon sous-agent:\n```\n{e}\n```"
                    print(error_trace)  # Affiche aussi dans la console

                # Affichage de la réponse
                st.markdown(response_content)

        # 3. Sauvegarder la réponse dans l'historique
        st.session_state.lead_messages.append(
            {"role": "assistant", "content": response_content})
        save_chat_history(st.session_state.lead_messages,
                          st.session_state.kanban_messages, st.session_state.design_messages,
                          community_msgs=st.session_state.community_messages)

        # 4. Recharger la page pour mettre à jour la Sidebar (BDD)
        time.sleep(1)
        st.rerun()

elif current_page == "▤ Base de données":
    st.title("▤ Base de données Leads")
    st.subheader("Tous les leads prospectés")
    df_all_leads = db.get_all_leads_as_df()

    if not df_all_leads.empty:
        st.markdown("*Double-cliquez sur une cellule pour modifier la valeur. Sélectionnez le bord gauche d'une ligne pour la supprimer avec la touche Retour (Suppr).*")

        # Afficher la data avec Streamlit Data Editor
        edited_df = st.data_editor(
            df_all_leads,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="leads_editor"
        )

        # Actions de sauvegarde
        if st.button("💾 Sauvegarder les modifications"):
            changes = st.session_state.get("leads_editor", {})
            try:
                # 1. Suppressions (utiliser les indices de l'ancien DataFrame)
                for row_idx in changes.get("deleted_rows", []):
                    lead_id_to_delete = int(df_all_leads.iloc[row_idx]["id"])
                    db.delete_lead(lead_id_to_delete)

                # 2. Additions de nouveaux leads vierges
                for new_row in changes.get("added_rows", []):
                    db.add_lead(
                        company_name=new_row.get("company_name", "Sans nom"),
                        website=new_row.get("website"),
                        linkedin_url=new_row.get("linkedin_url"),
                        description=new_row.get("description")
                    )

                # 3. Mises à jour de cellules
                for row_idx_str, cell_updates in changes.get("edited_rows", {}).items():
                    row_idx = int(row_idx_str)
                    lead_id_to_update = int(df_all_leads.iloc[row_idx]["id"])
                    db.update_lead(lead_id_to_update, cell_updates)

                st.success("Modifications synchronisées avec succès ! 🎉")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Erreur technique lors de la sauvegarde : {e}")

        # Bouton d'export CSV rapide
        csv = df_all_leads.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Télécharger en CSV",
            data=csv,
            file_name='leads_export.csv',
            mime='text/csv',
        )
    else:
        st.info(
            "Aucun lead dans la base pour le moment. Demandez au robot d'en chercher !")

elif current_page == "▦ Kanban & Organisation":
    st.title("▦ Kanban & Organisation")
    st.markdown("Pilotez vos chantiers IA et Automatisation au quotidien.")

    # --- GOOGLE SYNC UI ---
    import threading

    def background_export(df_to_export):
        try:
            google_sync.export_all_to_sheet(df_to_export)
            print(">>> Google Sheet mis à jour en arrière-plan avec succès.")
        except Exception as e:
            print(
                f">>> Erreur lors de la mise à jour Google Sheet en arrière-plan : {e}")

    def trigger_google_export():
        if google_sync.is_enabled():
            # Exécuter l'export dans un thread séparé pour ne pas bloquer l'UI Streamlit
            df_export = db.get_all_tasks_df()
            thread = threading.Thread(
                target=background_export, args=(df_export,))
            thread.start()

    if not google_sync.is_enabled():
        st.warning("⚠️ **Mode Hors-Ligne** : Le fichier `google_credentials.json` n'a pas été trouvé. Mettez-le en place pour activer la synchronisation bidirectionnelle Google Sheets.")
    else:
        # --- AUTO-PULL INITIAL ---
        if not st.session_state.get('initial_sync_done', False):
            with st.spinner("🔄 Synchronisation automatique initiale depuis Google Sheets..."):
                records = google_sync.import_all_from_sheet()
                if records:
                    db.clear_all_tasks()
                    for r in records:
                        mission_name = str(r.get('Mission', '')).strip()
                        if not mission_name:
                            continue

                        raw_status = str(r.get('Statut', '')
                                         ).strip().capitalize()
                        final_status = 'A faire'
                        if 'cours' in raw_status.lower():
                            final_status = 'En cours'
                        elif 'termin' in raw_status.lower() or 'done' in raw_status.lower():
                            final_status = 'Terminé'

                        db.add_task(
                            mission=mission_name,
                            status=final_status,
                            priorite=str(r.get('Priorité', '')),
                            agentic=str(r.get('Agentic', '')),
                            collaborateur=str(r.get('Collaborateur', '')),
                            date_debut=str(r.get('Date de début', '')),
                            date_fin=str(r.get('Date de Fin', '')),
                            commentaire=str(r.get('Commentaire', '')),
                            next_step=str(r.get('Next Step', ''))
                        )
                st.session_state.initial_sync_done = True
                print(">>> Auto-sync initial effectué avec succès.")
                st.rerun()

        col_sync1, col_sync2, _ = st.columns([1, 1, 2])
        if col_sync1.button("🔄 Forcer Impo depuis Google", use_container_width=True):
            with st.spinner("Importation depuis Google Sheets (Ceci écrasera les modifications locales)..."):
                records = google_sync.import_all_from_sheet()
                if records:
                    db.clear_all_tasks()
                    for r in records:
                        mission_name = str(r.get('Mission', '')).strip()
                        if not mission_name:
                            continue

                        raw_status = str(r.get('Statut', '')
                                         ).strip().capitalize()
                        final_status = 'A faire'
                        if 'cours' in raw_status.lower():
                            final_status = 'En cours'
                        elif 'termin' in raw_status.lower() or 'done' in raw_status.lower():
                            final_status = 'Terminé'

                        db.add_task(
                            mission=mission_name,
                            status=final_status,
                            priorite=str(r.get('Priorité', '')),
                            agentic=str(r.get('Agentic', '')),
                            collaborateur=str(r.get('Collaborateur', '')),
                            date_debut=str(r.get('Date de début', '')),
                            date_fin=str(r.get('Date de Fin', '')),
                            commentaire=str(r.get('Commentaire', '')),
                            next_step=str(r.get('Next Step', ''))
                        )
                    st.success(
                        "Tâches resynchronisées avec succès depuis Google !")
                    time.sleep(1)
                    st.rerun()
        if col_sync2.button("☁️ Forcer Expo vers Google", use_container_width=True):
            with st.spinner("Sauvegarde vers Google Sheets..."):
                trigger_google_export()
                st.success("Tâches sauvegardées de force sur Google Sheets !")
                time.sleep(1)

    st.markdown("---")

    # Séparation en deux colonnes : Chat Agent VS Kanban Board
    col_chat, col_kanban = st.columns([1, 2.5])

    with col_chat:
        st.markdown("### 🤖 Agent Organisateur")
        st.caption("Votre assistant Kanban pour créer et classer vos tâches.")

        # Affichage du chat Kanban
        chat_container = st.container(height=500, border=False)
        with chat_container:
            for message in st.session_state.kanban_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt_kanban := st.chat_input("Demande d'organiser une mission UX/UI...", key="kanban_chat_input"):
            st.session_state.kanban_messages.append(
                {"role": "user", "content": prompt_kanban})
            save_chat_history(st.session_state.lead_messages,
                              st.session_state.kanban_messages, st.session_state.design_messages,
                              community_msgs=st.session_state.community_messages)
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_kanban)

            # Execution Swarm Kanban
            from orchestrator import client, organizer_agent
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("L'Organisateur réfléchit..."):
                        swarm_messages = [{"role": msg["role"], "content": msg["content"]}
                                          for msg in st.session_state.kanban_messages]
                        try:
                            response = client.run(
                                agent=organizer_agent, messages=swarm_messages, context_variables={})
                            response_content = response.messages[-1].get(
                                "content", "")
                        except Exception as e:
                            response_content = f"Erreur de l'Organisateur: {e}"
                        st.markdown(response_content)

            st.session_state.kanban_messages.append(
                {"role": "assistant", "content": response_content})
            save_chat_history(st.session_state.lead_messages,
                              st.session_state.kanban_messages, st.session_state.design_messages,
                              community_msgs=st.session_state.community_messages)
            time.sleep(0.5)
            st.rerun()

    with col_kanban:
        # Récupérer toutes les tâches actives
        df_tasks = db.get_all_tasks_df()
        if not df_tasks.empty:
            # --- CONFIGURATION DU KANBAN (DRAG & DROP CUSTOM) ---
            import streamlit.components.v1 as components
            import os

            # 1. Préparer les données pour le composant HTML natif
            kanban_tasks = []
            for _, row in df_tasks.iterrows():
                tags = []
                if pd.notnull(row['priorite']) and row['priorite']:
                    tags.append(f"🎯 {row['priorite']}")
                if pd.notnull(row['agentic']) and row['agentic']:
                    tags.append(f"🤖 {row['agentic']}")

                kanban_tasks.append({
                    "id": str(row['id']),
                    "status": str(row['status']),
                    "mission": str(row['mission']),
                    "tags": tags,
                    "collaborateur": str(row['collaborateur']) if pd.notnull(row['collaborateur']) else "",
                    "date_fin": str(row['date_fin']) if pd.notnull(row['date_fin']) else ""
                })

            # 2. Déclaration du composant local
            custom_kanban_path = os.path.join(
                os.path.dirname(__file__), "custom_kanban")
            kanban_component = components.declare_component(
                "custom_kanban", path=custom_kanban_path)

            # 3. Afficher le Kanban interactif
            moved_task = kanban_component(
                tasks=kanban_tasks, key="main_kanban")

            # 4. Écouter les événements du Kanban Custom
            if moved_task and isinstance(moved_task, dict):
                action = moved_task.get("action", "move")
                task_id_event = int(moved_task.get("task_id", 0))

                if action == "edit" and task_id_event != 0:
                    st.session_state.edit_task_id = task_id_event
                    st.session_state.view_task_id = None

                elif action == "view" and task_id_event != 0:
                    st.session_state.view_task_id = task_id_event
                    st.session_state.edit_task_id = None

                elif action == "move" and task_id_event != 0:
                    nouveau_status = moved_task.get("new_status")

                    # Vérifier si l'ancien statut est différent du nouveau
                    matches = df_tasks[df_tasks['id'] == task_id_event]
                    if not matches.empty:
                        current_status = matches.iloc[0]['status']
                        if current_status != nouveau_status:
                            print(
                                f">>> Custom Kanban Mouvement détecté: {task_id_event} vers {nouveau_status}")
                            db.update_task_status(
                                task_id_event, nouveau_status)
                            trigger_google_export()
                            time.sleep(0.3)
                            st.rerun()

            # 5. Interfaces d'Édition et de Visionnage
            @st.dialog("✏️ Édition des Propriétés")
            def edit_task_dialog(t_data, edit_id):
                with st.form("edit_task_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        e_mission = st.text_input(
                            "Mission / Chantier*", value=t_data['mission'])

                        status_opts = ["A faire", "En cours", "Terminé"]
                        cur_status = t_data['status'] if t_data['status'] in status_opts else "A faire"
                        e_status = st.selectbox(
                            "Statut", status_opts, index=status_opts.index(cur_status))

                        priorite_opts = [
                            "", "Critique", "Très Haute", "Haute", "Normale", "Basse"]
                        cur_prio = t_data['priorite'] if t_data['priorite'] in priorite_opts else ""
                        e_priorite = st.selectbox(
                            "Priorité", priorite_opts, index=priorite_opts.index(cur_prio))

                        e_agentic = st.text_input(
                            "État Agentique", value=t_data['agentic'] if t_data['agentic'] else "")

                    with col2:
                        e_collab = st.text_input(
                            "Collaborateur assigné", value=t_data['collaborateur'] if t_data['collaborateur'] else "")
                        e_debut = st.text_input(
                            "Date de début", value=t_data['date_debut'] if t_data['date_debut'] else "")
                        e_fin = st.text_input(
                            "Date de fin", value=t_data['date_fin'] if t_data['date_fin'] else "")
                        e_comment = st.text_area(
                            "Commentaire", value=t_data['commentaire'] if t_data['commentaire'] else "", height=68)

                    e_next = st.text_input(
                        "Next Step", value=t_data['next_step'] if t_data['next_step'] else "")

                    col_s1, col_s2 = st.columns([1, 1])
                    with col_s1:
                        if st.form_submit_button("✅ Enregistrer les infos", use_container_width=True):
                            updates = {
                                "mission": e_mission,
                                "status": e_status,
                                "priorite": e_priorite,
                                "agentic": e_agentic,
                                "collaborateur": e_collab,
                                "date_debut": e_debut,
                                "date_fin": e_fin,
                                "commentaire": e_comment,
                                "next_step": e_next
                            }
                            db.update_task(edit_id, updates)
                            trigger_google_export()
                            st.session_state.edit_task_id = None
                            st.success("Tâche mise à jour avec succès !")
                            time.sleep(0.5)
                            st.rerun()
                    with col_s2:
                        if st.form_submit_button("🗑️ Supprimer définitivement", use_container_width=True):
                            db.delete_task(edit_id)
                            trigger_google_export()
                            st.session_state.edit_task_id = None
                            st.warning("Tâche supprimée.")
                            time.sleep(0.5)
                            st.rerun()

                if st.button("❌ Annuler l'édition", use_container_width=True):
                    st.session_state.edit_task_id = None
                    st.rerun()

            @st.dialog("📄 Détails de la Tâche")
            def view_task_dialog(t_data, view_id):
                st.markdown(f"### {t_data['mission']}")

                # Properties Layout (Notion style)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Statut:** `{t_data['status']}`")
                    st.markdown(
                        f"**Priorité:** {t_data['priorite'] if t_data['priorite'] else 'Aucune'}")
                    if t_data['agentic']:
                        st.markdown(f"**IA:** 🤖 {t_data['agentic']}")
                with col2:
                    st.markdown(
                        f"**Assigné à:** 👤 {t_data['collaborateur'] if t_data['collaborateur'] else '-'}")
                    st.markdown(
                        f"**Échéance:** 📅 {t_data['date_fin'] if t_data['date_fin'] else '-'}")

                st.markdown("---")

                # --- SECTION 2: Checklists (Sous-tâches) ---
                st.markdown("#### ✅ Check-list")

                # Afficher les items existants
                checklist_items = db.get_checklists_for_task(view_id)
                if not checklist_items:
                    st.caption("Aucune sous-tâche pour le moment.")

                for item in checklist_items:
                    col_chk, col_del = st.columns([0.9, 0.1])
                    with col_chk:
                        new_val = st.checkbox(
                            item["title"], value=item["is_completed"], key=f"v_chk_{item['id']}")
                        if new_val != item["is_completed"]:
                            db.toggle_checklist_item(item["id"], new_val)
                            st.rerun()
                    with col_del:
                        if st.button("❌", key=f"v_del_chk_{item['id']}", help="Supprimer", type="tertiary"):
                            db.delete_checklist_item(item["id"])
                            st.rerun()

                # Ajouter un nouvel item
                col_new1, col_new2 = st.columns([0.8, 0.2])
                with col_new1:
                    new_chk_title = st.text_input("Nouvelle sous-tâche", key="v_new_chk_input",
                                                  label_visibility="collapsed", placeholder="Nouvel élément de liste...")
                with col_new2:
                    if st.button("Ajouter", key="v_btn_add", use_container_width=True):
                        if new_chk_title.strip():
                            db.add_checklist_item(
                                view_id, new_chk_title.strip())
                            st.rerun()

                st.markdown("---")
                st.markdown("#### 📝 Commentaire / Description")
                if t_data['commentaire']:
                    st.info(t_data['commentaire'])
                else:
                    st.caption("Aucune description renseignée.")

                if t_data['next_step']:
                    st.markdown("#### ➡️ Prochaine étape")
                    st.success(t_data['next_step'])

                st.markdown("---")
                if st.button("❌ Fermer", use_container_width=True):
                    st.session_state.view_task_id = None
                    st.rerun()

            # Trigger Modals
            if st.session_state.get("edit_task_id") is not None:
                edit_id = st.session_state.edit_task_id
                task_row = df_tasks[df_tasks['id'] == edit_id]
                if not task_row.empty:
                    t_data = task_row.iloc[0].to_dict()
                    edit_task_dialog(t_data, edit_id)

            if st.session_state.get("view_task_id") is not None:
                view_id = st.session_state.view_task_id
                task_row = df_tasks[df_tasks['id'] == view_id]
                if not task_row.empty:
                    t_data = task_row.iloc[0].to_dict()
                    view_task_dialog(t_data, view_id)

            st.markdown("---")
            with st.expander("➕ Ajouter une nouvelle tâche manuellement"):
                with st.form("new_task_form", clear_on_submit=True):
                    new_mission = st.text_input(
                        "Mission / Chantier (Obligatoire)")
                    new_priorite = st.selectbox(
                        "Priorité", ["", "Critique", "Très Haute", "Haute", "Normale", "Basse"])
                    new_collab = st.text_input("Collaborateur")
                    submitted = st.form_submit_button("Créer la tâche")
                    if submitted and new_mission:
                        db.add_task(mission=new_mission, priorite=new_priorite,
                                    collaborateur=new_collab, status="A faire")
                        trigger_google_export()
                        st.success("Tâche ajoutée !")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(
                "Aucune tâche dans le Kanban. Vous pouvez importer le Google Sheet ou créer une tâche.")

elif current_page == "📱 Community Manager":
    st.title("📱 Community Manager & Planning")
    # --- LINKEDIN AUTH FLOW ---
    from linkedin_automator import LinkedInAutomator
    linkedin_auth = LinkedInAutomator(db=db)
    
    # Vérification du code de retour OAuth
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        st.info("🔄 Finalisation de la connexion LinkedIn...")
        success, msg = linkedin_auth.exchange_code_for_token(auth_code)
        if success:
            st.success(msg)
            # Nettoyer l'URL
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

    # Affichage du statut de connexion
    accounts = db.get_linkedin_accounts()
    has_creds = bool(linkedin_auth.client_id and linkedin_auth.client_secret)
    
    with st.expander("🔐 Gestion des Comptes LinkedIn API", expanded=not accounts):
        # 1. Configuration des identifiants API
        if not has_creds or st.checkbox("Modifier les identifiants API (Client ID/Secret)", key="check_mod_creds"):
            with st.form("linkedin_creds_form"):
                st.subheader("⚙️ Identifiants de l'application LinkedIn")
                new_client_id = st.text_input("Client ID", value=linkedin_auth.client_id or "", type="password")
                new_client_secret = st.text_input("Client Secret", value=linkedin_auth.client_secret or "", type="password")
                st.info("💡 Ces identifiants sont globaux pour votre application LinkedIn.")
                
                if st.form_submit_button("💾 Enregistrer la configuration"):
                    from dotenv import set_key, load_dotenv
                    env_path = os.path.join(os.path.dirname(__file__), ".env")
                    set_key(env_path, "LINKEDIN_CLIENT_ID", new_client_id)
                    set_key(env_path, "LINKEDIN_CLIENT_SECRET", new_client_secret)
                    os.environ["LINKEDIN_CLIENT_ID"] = new_client_id
                    os.environ["LINKEDIN_CLIENT_SECRET"] = new_client_secret
                    load_dotenv(env_path, override=True)
                    st.success("Configuration enregistrée !")
                    time.sleep(0.5)
                    st.rerun()
        
        # 2. Liste des comptes connectés
        st.markdown("---")
        if accounts:
            st.subheader("👥 Comptes connectés")
            for acc in accounts:
                col1, col2 = st.columns([0.8, 0.2])
                col1.write(f"✅ **{acc['name']}** (`{acc['person_urn']}`)")
                if col2.button("🗑️", key=f"del_acc_{acc['id']}"):
                    db.delete_linkedin_account(acc['id'])
                    st.rerun()
            st.markdown("---")

        # 3. Bouton d'ajout de compte
        if has_creds:
            auth_url = linkedin_auth.get_authorization_url()
            st.markdown(f'<a href="{auth_url}" target="_self" style="background-color: #0077b5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">+ Ajouter un compte LinkedIn</a>', unsafe_allow_html=True)
            st.caption("Vous pouvez connecter plusieurs comptes en utilisant le même bouton.")
        else:
            st.info("Veuillez d'abord configurer vos identifiants Client ID et Client Secret.")

    tab_chat, tab_plan, tab_calendar, tab_logs = st.tabs(["💬 Conversation", "📅 Planning Table", "🗓️ Calendrier Visuel", "📊 Activité & Logs"])

    with tab_logs:
        st.markdown("### 📊 Historique d'Activité du Worker")
        
        # Affichage des logs
        logs_df = db.get_publication_logs(limit=20)
        
        if not logs_df.empty:
            # Indicateur d'état du worker (basé sur le dernier heartbeat)
            last_heartbeat = logs_df[logs_df['status'] == 'Heartbeat'].iloc[0] if not logs_df[logs_df['status'] == 'Heartbeat'].empty else None
            if last_heartbeat is not None:
                st.success(f"🤖 **Worker Actif** (Dernier signal : `{last_heartbeat['message'].split()[-1]}`)")
            else:
                st.warning("⚠️ **Worker Inactif** ou en attente de démarrage.")
            
            st.dataframe(
                logs_df,
                use_container_width=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Heure", format="HH:mm:ss"),
                    "status": st.column_config.TextColumn("Statut"),
                    "title": st.column_config.TextColumn("Post"),
                    "message": st.column_config.TextColumn("Détails")
                },
                hide_index=True
            )
        else:
            st.info("Aucune activité enregistrée pour le moment. Lancez le fichier `start_all.bat` pour démarrer le worker.")

    with tab_chat:
        st.markdown("### 🤖 Agent Joy")
        st.caption("Votre experte en stratégie de contenu LinkedIn.")

        # Affichage du chat Community
        chat_container = st.container(height=500, border=False)
        with chat_container:
            for message in st.session_state.community_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt_community := st.chat_input("Ex: Prépare un carrousel sur l'automatisation IA...", key="community_chat_input"):
            st.session_state.community_messages.append(
                {"role": "user", "content": prompt_community})
            save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                              st.session_state.design_messages, community_msgs=st.session_state.community_messages)
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_community)

            # Execution Swarm Community
            from orchestrator import client, community_agent
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Joy élabore votre stratégie..."):
                        swarm_messages = [{"role": msg["role"], "content": msg["content"]}
                                          for msg in st.session_state.community_messages]
                        try:
                            response = client.run(
                                agent=community_agent, messages=swarm_messages, context_variables={})
                            response_content = response.messages[-1].get(
                                "content", "")
                        except Exception as e:
                            import traceback
                            print(traceback.format_exc())
                            response_content = f"Erreur de Joy: {e}"
                        st.markdown(response_content)

            st.session_state.community_messages.append(
                {"role": "assistant", "content": response_content})
            save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                              st.session_state.design_messages, community_msgs=st.session_state.community_messages)
            time.sleep(0.5)
            st.rerun()

    with tab_plan:
        st.markdown("### 📅 Planning Éditorial")
        df_content = db.get_all_content_df()
        
        # Convertir en datetime pour la compatibilité avec DateColumn de Streamlit
        if not df_content.empty:
            df_content['scheduled_at'] = pd.to_datetime(df_content['scheduled_at'], errors='coerce')

        if not df_content.empty:
            st.markdown(
                "*Gérez vos idées de posts et carrousels. Ajoutez les liens de vos images pour les carrousels (1 à 10).*")
            
            # Liste des comptes pour le sélecteur
            acc_list = db.get_linkedin_accounts()
            acc_options = {acc['id']: acc['name'] for acc in acc_list}
            acc_names = ["Aucun"] + list(acc_options.values())

            # Configuration des colonnes
            col_config = {
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "linkedin_account_id": st.column_config.SelectboxColumn(
                    "👤 Compte", 
                    options=acc_names,
                    help="Choisissez le compte LinkedIn qui publiera ce post."
                ),
                "title": st.column_config.TextColumn("Titre / Sujet", width="medium"),
                "post_idea": st.column_config.TextColumn("💡 Idée de post", width="medium"),
                "post_type": st.column_config.SelectboxColumn("Type", options=["Post", "Carousel"]),
                "status": st.column_config.SelectboxColumn("Statut", options=["Brouillon", "Prêt", "Published"]),
                "scheduled_at": st.column_config.DatetimeColumn("Date & Heure publication", format="DD/MM/YYYY HH:mm"),
                "content": st.column_config.TextColumn("Contenu (Texte)", width="medium"),
                "media_files": st.column_config.TextColumn("Médias (JSON)", width="small"),
            }
            # Ajouter dynamiquement les 10 colonnes images
            for i in range(1, 11):
                col_config[f"img{i}"] = st.column_config.ImageColumn(f"Image {i}", width="small")

            # Préparer les miniatures pour le tableau (données base64)
            df_display = df_content.copy()
            df_display['linkedin_account_id'] = df_display['linkedin_account_id'].apply(
                lambda x: acc_options.get(int(x)) if x and str(x).isdigit() else "Aucun"
            )
            for i in range(1, 11):
                df_display[f'img{i}'] = df_display[f'img{i}'].apply(get_image_base64)

            # Fonction de sauvegarde automatique
            def auto_save_planning():
                changes = st.session_state.get("content_editor", {})
                if not changes:
                    return
                
                try:
                    # 1. Suppressions
                    for row_idx in changes.get("deleted_rows", []):
                        db.delete_content_item(int(df_content.iloc[row_idx]["id"]))

                    # 2. Ajouts
                    for new_row in changes.get("added_rows", []):
                        acc_name = new_row.get("linkedin_account_id", "Aucun")
                        acc_id = next((k for k, v in acc_options.items() if v == acc_name), None)
                        
                        db.add_content_item(
                            title=new_row.get("title", "Sans titre"),
                            post_idea=new_row.get("post_idea", ""),
                            post_type=new_row.get("post_type", "Post"),
                            content=new_row.get("content", ""),
                            scheduled_at=new_row.get("scheduled_at", None),
                            status=new_row.get("status", "Brouillon"),
                            linkedin_account_id=acc_id,
                            img1=new_row.get("img1", ""), img2=new_row.get("img2", ""),
                            img3=new_row.get("img3", ""), img4=new_row.get("img4", ""),
                            img5=new_row.get("img5", ""), img6=new_row.get("img6", ""),
                            img7=new_row.get("img7", ""), img8=new_row.get("img8", ""),
                            img9=new_row.get("img9", ""), img10=new_row.get("img10", "")
                        )

                    # 3. Mises à jour
                    for row_idx_str, cell_updates in changes.get("edited_rows", {}).items():
                        row_idx = int(row_idx_str)
                        item_id = int(df_content.iloc[row_idx]["id"])
                        
                        if "linkedin_account_id" in cell_updates:
                            acc_name = cell_updates["linkedin_account_id"]
                            cell_updates["linkedin_account_id"] = next((k for k, v in acc_options.items() if v == acc_name), None)
                            
                        db.update_content_item(item_id, cell_updates)
                    
                    st.toast("✅ Planning sauvegardé automatiquement", icon="💾")
                except Exception as e:
                    st.error(f"Erreur lors de l'auto-save : {e}")

            edited_content = st.data_editor(
                df_display,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="content_editor",
                column_config=col_config,
                on_change=auto_save_planning
            )

            # Gestion des médias pour la ligne sélectionnée
            st.markdown("---")
            st.markdown("#### 📸 Gestion des Médias & Aperçu")
            
            # On permet de choisir le post à modifier via un selectbox pour plus de stabilité
            post_titles = df_content['title'].tolist()
            selected_post_title = st.selectbox("Choisir une publication pour gérer ses visuels :", post_titles, key="community_post_selector")
            
            item = df_content[df_content['title'] == selected_post_title].iloc[0]
            selected_item_id = int(item['id'])
            
            st.markdown(f"**Publication sélectionnée :** ID {selected_item_id} - {item['title']}")
            with st.expander("📸 Gestionnaire de Médias (Images Carousel)", expanded=True):
                st.info("Chargez vos images ici. Elles apparaîtront sous forme de miniatures dans le tableau.")
                
                # Dossier d'upload
                upload_dir = os.path.join(os.path.dirname(__file__), 'uploads', 'community')
                os.makedirs(upload_dir, exist_ok=True)
                
                # On crée 10 colonnes pour les 10 uploaders (en grille)
                img_cols = st.columns(5)
                img_cols2 = st.columns(5)
                all_img_cols = img_cols + img_cols2
                
                for i in range(1, 11):
                    with all_img_cols[i-1]:
                        current_img_path = item.get(f'img{i}')
                        if current_img_path and os.path.exists(current_img_path):
                            st.image(current_img_path, width=100)
                            if st.button(f"🗑️ #{i}", key=f"del_img_{selected_item_id}_{i}"):
                                db.update_content_item(selected_item_id, {f"img{i}": ""})
                                st.rerun()
                        else:
                            uploaded_file = st.file_uploader(f"Img {i}", key=f"up_img_{selected_item_id}_{i}", label_visibility="collapsed")
                            if uploaded_file:
                                # Sauvegarde physique
                                file_ext = uploaded_file.name.split('.')[-1]
                                file_name = f"post_{selected_item_id}_img{i}_{int(time.time())}.{file_ext}"
                                file_path = os.path.join(upload_dir, file_name)
                                with open(file_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                # Enregistrement en DB
                                db.update_content_item(selected_item_id, {f"img{i}": file_path})
                                st.success(f"Image {i} chargée !")
                                time.sleep(0.5)
                                st.rerun()

            with st.expander("📝 Contenu détaillé", expanded=True):
                st.write(f"**Titre :** {item['title']} ({item['post_type']})")
                st.write(f"**Idée :** {item['post_idea']}")
                st.write("**Contenu rédigé :**")
                st.code(item['content'], language="markdown")
            if st.button("➕ Préparer 3 emplacements vides"):
                for _ in range(3):
                    db.add_content_item(title="À définir", post_idea="Nouvelle idée...", content="")
                st.rerun()

    with tab_calendar:
        st.markdown("### 🗓️ Vue Calendrier Interactive")
        st.caption("Faites glisser les cartes pour changer la date ou l'heure de publication.")
        
        df_cal = db.get_all_content_df()
        
        if df_cal.empty:
            st.info("Votre planning est vide. Dites à Joy ce que vous voulez publier sur LinkedIn !")
            if st.button("➕ Préparer 3 emplacements vides", key="empty_plan_btn_cal"):
                for _ in range(3):
                    db.add_content_item(title="À définir", post_idea="Nouvelle idée...", content="")
                st.rerun()
        else:
            calendar_events = []
            for _, row in df_cal.iterrows():
                if row['scheduled_at'] and str(row['scheduled_at']).strip():
                    try:
                        # Conversion propre pour FullCalendar
                        dt = pd.to_datetime(row['scheduled_at'])
                        if pd.isna(dt): continue
                        
                        start_iso = dt.isoformat()
                        end_iso = (dt + pd.Timedelta(hours=1)).isoformat()
                        
                        # Couleur selon le statut
                        bg_color = "#3498db" # Blue for Brouillon
                        if row['status'] == 'Prêt': bg_color = "#f1c40f" # Yellow
                        elif row['status'] == 'Published': bg_color = "#27ae60" # Green
                        
                        calendar_events.append({
                            "title": f"{row['title']} ({row['post_type']})",
                            "start": start_iso,
                            "end": end_iso,
                            "id": str(row['id']),
                            "backgroundColor": bg_color,
                            "borderColor": bg_color,
                        })
                    except Exception as e:
                        continue

            calendar_options = {
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
                },
                "initialView": "dayGridMonth",
                "editable": True,
                "navLinks": True,
                "selectable": True,
                "nowIndicator": True,
                "height": "800px",
            }
            
            custom_css="""
                .fc-event-title { font-weight: bold; }
                .fc-event { cursor: pointer; border-radius: 4px; padding: 2px; }
            """
            
            try:
                cal_state = calendar(
                    events=calendar_events,
                    options=calendar_options,
                    custom_css=custom_css,
                    key="community_full_calendar"
                )
            except Exception as e:
                st.error(f"Erreur d'affichage du calendrier : {e}")
                cal_state = {}

            # Gestion des interactions
            if cal_state.get("eventChange"):
                event = cal_state["eventChange"]["event"]
                new_start = event["start"]
                event_id = int(event["id"])
                db.update_content_item(event_id, {"scheduled_at": new_start})
                st.success(f"🚀 Publication ID {event_id} déplacée au {new_start}")
                time.sleep(1)
                st.rerun()

            if cal_state.get("eventClick"):
                ev_data = cal_state["eventClick"]["event"]
                ev_id = int(ev_data["id"])
                item = df_cal[df_cal['id'] == ev_id].iloc[0]
                
                st.markdown("---")
                with st.container(border=True):
                    col_t, col_btn = st.columns([0.9, 0.1])
                    col_t.markdown(f"### 📄 Détails : {item['title']}")
                    if col_btn.button("✖️", key="close_details_cal"):
                        st.rerun()
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.write(f"**Statut :** `{item['status']}`")
                        st.write(f"**Type :** {item['post_type']}")
                        st.write(f"**Planifié le :** {item['scheduled_at']}")
                        st.write(f"**Idée :** {item['post_idea']}")
                    
                    with c2:
                        imgs = [item.get(f'img{i}') for i in range(1, 11) if item.get(f'img{i}')]
                        if imgs:
                            st.markdown("**Images (Carousel) :**")
                            cols_img = st.columns(5)
                            for idx, img_path in enumerate(imgs):
                                if os.path.exists(img_path):
                                    with cols_img[idx % 5]:
                                        st.image(img_path, width=80)

                    st.markdown("**Contenu rédigé :**")
                    st.code(item['content'], language="markdown")

elif current_page == "◈ Design System":
    st.title("◈ Design System")
    st.markdown(
        "Pilotez l'UX/UI Ultra-Premium et gardez un œil sur votre Storybook.")

    chat_tab, design_tokens_tab, storybook_tab = st.tabs(
        ["Chat", "Design Tokens", "Storybook"])

    with chat_tab:
        st.markdown("### 🤖 Chat Archi")
        st.caption("Posez des questions sur vos composants ou demandez un audit.")

        chat_container = st.container(height=500, border=False)
        with chat_container:
            for message in st.session_state.design_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # --- COLOR PICKER CONTEXTUEL ---
        COLOR_KEYWORDS = ["couleur", "hex", "color", "teinte",
                          "code couleur", "quelle couleur", "nouvelle couleur", "choisir"]
        last_assistant_msg = ""
        for msg in reversed(st.session_state.design_messages):
            if msg["role"] == "assistant":
                last_assistant_msg = msg["content"].lower()
                break

        is_waiting_for_color = any(kw in last_assistant_msg for kw in COLOR_KEYWORDS) and \
            st.session_state.design_messages and \
            st.session_state.design_messages[-1]["role"] == "assistant"

        if is_waiting_for_color:
            import re as _re_chat
            _GLOBALS_CSS = os.path.join(os.path.dirname(
                os.path.dirname(__file__)), "app", "globals.css")

            def _write_token_chat(var_name, new_value):
                with open(_GLOBALS_CSS, "r", encoding="utf-8") as f:
                    content = f.read()
                pattern = rf'({_re_chat.escape(var_name)}\s*:\s*)(#[0-9a-fA-F]{{3,8}})'
                new_content = _re_chat.sub(
                    pattern, rf'\g<1>{new_value}', content)
                with open(_GLOBALS_CSS, "w", encoding="utf-8") as f:
                    f.write(new_content)
                _trigger_ssg()

            st.markdown("---")
            st.markdown("### Sélecteur de couleur")
            st.caption(
                "Choisissez la variable et la couleur — elle sera écrite dans `globals.css` immédiatement.")

            # target_var défini EN PREMIER (avant les colonnes qui l'utilisent)
            target_var = st.selectbox(
                "Variable CSS à modifier :",
                ["--color-primary", "--color-primary-light", "--color-primary-dark"],
                key="target_css_var"
            )

            # Lire la valeur actuelle depuis globals.css pour cette variable
            _current_css_value = "#8200db"
            try:
                with open(_GLOBALS_CSS, "r", encoding="utf-8") as _f:
                    _css_content = _f.read()
                _match = _re_chat.search(
                    rf'{_re_chat.escape(target_var)}\s*:\s*(#[0-9a-fA-F]{{3,8}})',
                    _css_content
                )
                if _match:
                    _current_css_value = _match.group(1)
            except Exception:
                pass

            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.markdown(
                    '<span style="font-size:13px;color:#aaa;">◈ cliquez ↓</span>', unsafe_allow_html=True)
                picked_color = st.color_picker(
                    label="Couleur actuelle",
                    value=_current_css_value,
                    key=f"ctx_picker_{target_var}",
                )
                st.markdown(
                    f'<div style="background:{picked_color};height:48px;border-radius:8px;'
                    f'border:2px solid rgba(255,255,255,0.2);margin-top:6px;"></div>',
                    unsafe_allow_html=True
                )
            with col_b:
                st.markdown(f"**Couleur sélectionnée :** `{picked_color}`")
                st.caption("← Cliquez sur le carré pour changer")
                if st.button(
                    f"✅ Appliquer {picked_color} → `{target_var}`",
                    key="send_picked_color",
                    use_container_width=True,
                    type="primary"
                ):
                    _write_token_chat(target_var, picked_color)
                    picker_key = f"ctx_picker_{target_var}"
                    if picker_key in st.session_state:
                        del st.session_state[picker_key]
                    st.success(f"✅ `{target_var}` → `{picked_color}`")
                    st.rerun()
            st.markdown("---")

        # --- BOUTONS DE COMMANDE RAPIDE ---
        st.markdown("**⚡ Commandes rapides**")
        quick_cmds = {
            "🎨 Audit Design": "Fais un audit complet du design system actuel. Liste les composants, les variants disponibles, et signale tout ce qui ne respecte pas le DESIGN_SYSTEM.md.",
            "🔍 /storybook-modification": "Je souhaite utiliser le workflow /storybook-modification. AVANT de faire quoi que ce soit, pose-moi les questions suivantes et ATTENDS mes réponses : 1) Quel composant veux-tu modifier ? 2) Quelle partie précisément (couleur, layout, animation, props) ? 3) Quel est le résultat attendu ? Ne touche aucun fichier avant d'avoir mes réponses.",
            "🖌️ /brand-color-change": "Je souhaite utiliser le workflow /brand-color-change. AVANT de faire quoi que ce soit, pose-moi les questions suivantes et ATTENDS mes réponses : 1) Quelle est la nouvelle couleur principale (code hex exact) ? 2) Quels composants doivent être affectés ? 3) Est-ce un changement permanent ou un test ? Ne touche aucun fichier avant d'avoir mes réponses.",
            "📋 Liste composants": "Liste tous les composants du dashboard Storybook avec leurs variants disponibles.",
            "🛡️ Check intégrité CSS": "Vérifie que globals.css contient bien `@import tailwindcss`, le bloc `@theme`, et les utilitaires `.glass` et `.glass-card`. Signale tout ce qui manque.",
            "📸 Voir Storybook": "Ouvre et décris le rendu actuel du story DashboardOverview/ImperialPurple dans Storybook sur le port 6008.",
        }
        quick_help = {
            "🎨 Audit Design": "Lance un audit complet du design system : composants, variants, et conformité au DESIGN_SYSTEM.md.",
            "🔍 /storybook-modification": "Déclenche le workflow sécurisé pour modifier un composant Storybook sans casser le design.",
            "🖌️ /brand-color-change": "Démarre le processus guidé pour changer la couleur de marque sans effets de bord.",
            "📋 Liste composants": "Affiche tous les composants du dashboard et leurs variants (purple, gold, etc.).",
            "🛡️ Check intégrité CSS": "Vérifie que globals.css est intact : @import tailwindcss, @theme, et les classes glass sont présentes.",
            "📸 Voir Storybook": "Demande à Archi de décrire le rendu visuel actuel dans Storybook (port 6008).",
        }

        if "quick_cmd_trigger" not in st.session_state:
            st.session_state.quick_cmd_trigger = None

        quick_cols = st.columns(3)
        cmd_items = list(quick_cmds.items())
        for i, (label, cmd) in enumerate(cmd_items):
            col = quick_cols[i % 3]
            if col.button(label, key=f"qcmd_{i}", use_container_width=True, help=quick_help[label]):
                st.session_state.quick_cmd_trigger = cmd

        # Traitement du bouton cliqué
        if st.session_state.quick_cmd_trigger:
            prompt_design = st.session_state.quick_cmd_trigger
            st.session_state.quick_cmd_trigger = None
        else:
            prompt_design = None

        if not prompt_design:
            prompt_design = st.chat_input(
                "Ex: Peux-tu lister les composants disponibles ?", key="design_chat_input")

        if prompt_design:
            st.session_state.design_messages.append(
                {"role": "user", "content": prompt_design})
            save_chat_history(st.session_state.lead_messages,
                              st.session_state.kanban_messages, st.session_state.design_messages,
                              community_msgs=st.session_state.community_messages)
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt_design)

            # Exécution Swarm Archi
            try:
                from orchestrator import client
                sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
                from design_agent import design_agent  # Assuming design_agent is defined here

                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Archi analyse le Design System..."):
                            swarm_messages = [{"role": msg["role"], "content": msg["content"]}
                                              for msg in st.session_state.design_messages]
                            response = client.run(
                                agent=design_agent, messages=swarm_messages, context_variables={})
                            response_content = response.messages[-1].get(
                                "content", "")
                            st.markdown(response_content)
            except Exception as e:
                response_content = f"Une erreur technique est survenue avec Archi :\n```\n{e}\n```"
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(response_content)

            st.session_state.design_messages.append(
                {"role": "assistant", "content": response_content})
            save_chat_history(st.session_state.lead_messages,
                              st.session_state.kanban_messages, st.session_state.design_messages,
                              community_msgs=st.session_state.community_messages)
            time.sleep(0.5)
            st.rerun()

    with design_tokens_tab:
        import re as _re

        GLOBALS_CSS_PATH = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), "app", "globals.css")

        def read_all_tokens(css_path):
            """Parse @theme block — returns {var_name: (type, value)} for all tokens.
            Types: 'color' (#hex), 'px' (integer px), 'number' (bare integer), 'pct' (percentage integer)
            """
            tokens = {}
            try:
                with open(css_path, "r", encoding="utf-8") as f:
                    content = f.read()
                theme_match = _re.search(
                    r'@theme\s*\{([^}]+)\}', content, _re.DOTALL)
                if theme_match:
                    for line in theme_match.group(1).splitlines():
                        line = line.strip()
                        if not line or line.startswith("/*") or line.startswith("//"):
                            continue
                        # Hex color
                        m = _re.match(
                            r'(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;', line)
                        if m:
                            tokens[m.group(1)] = ("color", m.group(2))
                            continue
                        # px value
                        m = _re.match(r'(--[\w-]+)\s*:\s*(\d+)px\s*;', line)
                        if m:
                            tokens[m.group(1)] = ("px", int(m.group(2)))
                            continue
                        # Bare integer (font-weight, line-height as %)
                        m = _re.match(r'(--[\w-]+)\s*:\s*(\d+)\s*;', line)
                        if m:
                            var = m.group(1)
                            val = int(m.group(2))
                            if "font-weight" in var:
                                tokens[var] = ("number", val)
                            elif "line-height" in var:
                                tokens[var] = ("pct", val)
                            else:
                                tokens[var] = ("number", val)
            except Exception as e:
                st.error(f"Impossible de lire globals.css : {e}")
            return tokens

        def write_color_token(css_path, var_name, new_hex):
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
            pattern = rf'({_re.escape(var_name)}\s*:\s*)(#[0-9a-fA-F]{{3,8}})'
            new_content = _re.sub(pattern, rf'\g<1>{new_hex}', content)
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            _trigger_ssg()

        def write_px_token(css_path, var_name, new_px):
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
            pattern = rf'({_re.escape(var_name)}\s*:\s*)(\d+)(px)'
            new_content = _re.sub(pattern, rf'\g<1>{new_px}\g<3>', content)
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            _trigger_ssg()

        def write_number_token(css_path, var_name, new_val):
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Match bare integer (not followed by px)
            pattern = rf'({_re.escape(var_name)}\s*:\s*)(\d+)(\s*;)'
            new_content = _re.sub(pattern, rf'\g<1>{new_val}\g<3>', content)
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            _trigger_ssg()

        def auto_group_tokens(tokens: dict) -> dict:
            """Dynamically group all CSS tokens by variable name prefix."""
            from collections import OrderedDict
            SEMANTIC_NAMES = {"--color-success",
                              "--color-warning", "--color-danger", "--color-info"}
            groups = OrderedDict([
                ("🎨 Couleurs de marque",     {}),
                ("✅ Couleurs sémantiques",   {}),
                ("✏️ Couleurs de texte",     {}),
                ("🌑 Fonds",                 {}),
                ("🔲 Bordures",              {}),
                ("📊 Graphiques",            {}),
                ("📐 Tailles de police",     {}),
                ("⚖️ Graisses (weights)",    {}),
                ("↕️ Hauteurs de ligne",     {}),
                ("📏 Espacements",           {}),
                ("🔘 Border Radius",         {}),
                ("🌫️ Flous (blur)",         {}),
                ("⚙️ Autres",               {}),
            ])
            for var_name, token in tokens.items():
                if var_name.startswith("--color-primary"):
                    groups["🎨 Couleurs de marque"][var_name] = token
                elif var_name in SEMANTIC_NAMES:
                    groups["✅ Couleurs sémantiques"][var_name] = token
                elif var_name.startswith("--color-text"):
                    groups["✏️ Couleurs de texte"][var_name] = token
                elif var_name.startswith("--color-bg"):
                    groups["🌑 Fonds"][var_name] = token
                elif var_name.startswith("--color-border") or var_name.startswith("--border"):
                    groups["🔲 Bordures"][var_name] = token
                elif var_name.startswith("--color-chart"):
                    groups["📊 Graphiques"][var_name] = token
                elif var_name.startswith("--font-size"):
                    groups["📐 Tailles de police"][var_name] = token
                elif var_name.startswith("--font-weight"):
                    groups["⚖️ Graisses (weights)"][var_name] = token
                elif var_name.startswith("--line-height"):
                    groups["↕️ Hauteurs de ligne"][var_name] = token
                elif var_name.startswith("--spacing"):
                    groups["📏 Espacements"][var_name] = token
                elif var_name.startswith("--radius"):
                    groups["🔘 Border Radius"][var_name] = token
                elif var_name.startswith("--blur"):
                    groups["🌫️ Flous (blur)"][var_name] = token
                else:
                    groups["⚙️ Autres"][var_name] = token
            return OrderedDict((k, v) for k, v in groups.items() if v)

        # ── Read ALL tokens from globals.css ──────────────────────────────────
        all_tokens = read_all_tokens(GLOBALS_CSS_PATH)
        grouped = auto_group_tokens(all_tokens)

        st.markdown("### Design Tokens")
        n_types = {"color": 0, "px": 0, "number": 0, "pct": 0}
        for _, (t, _) in all_tokens.items():
            n_types[t] = n_types.get(t, 0) + 1
        st.caption(
            f"**{len(all_tokens)} tokens** — "
            f"{n_types['color']} couleurs · {n_types['px']} valeurs px · "
            f"{n_types['number']} graisses · {n_types['pct']} hauteurs de ligne · "
            f"Tout token ajouté à `@theme` apparaît automatiquement."
        )
        st.markdown("---")

        changed_any = False

        # ── Render each group dynamically ─────────────────────────────────────
        for cat_label, cat_tokens in grouped.items():
            is_font_size = cat_label == "📐 Tailles de police"
            first_cat = cat_label == "🎨 Couleurs de marque"

            with st.expander(f"{cat_label} ({len(cat_tokens)})", expanded=first_cat):
                color_vars_in_cat = []

                for var_name, (token_type, current_val) in cat_tokens.items():

                    # ── Color picker ─────────────────────────────────────────
                    if token_type == "color":
                        col_info, col_picker, col_code = st.columns(
                            [3, 1, 1.5])
                        with col_info:
                            st.markdown(f"**`{var_name}`**")
                        with col_picker:
                            new_hex = st.color_picker(
                                label=var_name, value=current_val,
                                key=f"dt_{var_name}", label_visibility="collapsed",
                            )
                        with col_code:
                            st.code(new_hex, language=None)
                        if new_hex.lower() != current_val.lower():
                            write_color_token(
                                GLOBALS_CSS_PATH, var_name, new_hex)
                            changed_any = True
                        color_vars_in_cat.append((var_name, new_hex))

                    # ── px slider ────────────────────────────────────────────
                    elif token_type == "px":
                        min_v = max(0, current_val // 4)
                        max_v = min(
                            256, max(current_val * 4, current_val + 32))
                        col_info, col_slider, col_val = st.columns([3, 3, 1])
                        with col_info:
                            st.markdown(f"**`{var_name}`**")
                        with col_slider:
                            new_px = st.slider(
                                label=var_name, min_value=min_v, max_value=max_v,
                                value=current_val, step=1,
                                key=f"dt_{var_name}", label_visibility="collapsed",
                            )
                        with col_val:
                            st.markdown(f"**{new_px}px**")
                        if new_px != current_val:
                            write_px_token(GLOBALS_CSS_PATH, var_name, new_px)
                            changed_any = True

                    # ── Font weight selectbox ────────────────────────────────
                    elif token_type == "number":
                        WEIGHT_OPTIONS = [100, 200, 300,
                                          400, 500, 600, 700, 800, 900]
                        WEIGHT_LABELS = ["100 Thin", "200 ExtraLight", "300 Light",
                                         "400 Regular", "500 Medium", "600 SemiBold",
                                         "700 Bold", "800 ExtraBold", "900 Black"]
                        safe_val = current_val if current_val in WEIGHT_OPTIONS else 400
                        col_info, col_sel, col_preview = st.columns([2, 2, 2])
                        with col_info:
                            st.markdown(f"**`{var_name}`**")
                        with col_sel:
                            new_num = st.selectbox(
                                label=var_name,
                                options=WEIGHT_OPTIONS,
                                format_func=lambda x: WEIGHT_LABELS[WEIGHT_OPTIONS.index(
                                    x)],
                                index=WEIGHT_OPTIONS.index(safe_val),
                                key=f"dt_{var_name}",
                                label_visibility="collapsed",
                            )
                        with col_preview:
                            st.markdown(
                                f'<p style="font-weight:{new_num};font-size:16px;color:#e8e8e8;margin:0">'
                                f'NXSTEP — {new_num}</p>',
                                unsafe_allow_html=True
                            )
                        if new_num != current_val:
                            write_number_token(
                                GLOBALS_CSS_PATH, var_name, new_num)
                            changed_any = True

                    # ── Line height slider (stored as integer %) ─────────────
                    elif token_type == "pct":
                        col_info, col_slider, col_val = st.columns([3, 3, 1])
                        with col_info:
                            st.markdown(f"**`{var_name}`**")
                        with col_slider:
                            new_pct = st.slider(
                                label=var_name, min_value=100, max_value=250,
                                value=current_val, step=5,
                                key=f"dt_{var_name}", label_visibility="collapsed",
                            )
                        with col_val:
                            st.markdown(f"**{new_pct}%**")
                        if new_pct != current_val:
                            write_number_token(
                                GLOBALS_CSS_PATH, var_name, new_pct)
                            changed_any = True

                # ── Color swatches ───────────────────────────────────────────
                if color_vars_in_cat:
                    swatch_cols = st.columns(len(color_vars_in_cat))
                    for i, (v, hex_val) in enumerate(color_vars_in_cat):
                        short = v.replace("--color-", "").replace("--", "")
                        swatch_cols[i].markdown(
                            f'<div style="background:{hex_val};height:32px;border-radius:6px;'
                            f'border:1px solid rgba(255,255,255,0.1);"></div>'
                            f'<p style="text-align:center;font-size:9px;color:#aaa;margin:2px 0">'
                            f'{short}<br><b>{hex_val}</b></p>',
                            unsafe_allow_html=True
                        )

                # ── Font-size live preview ───────────────────────────────────
                if is_font_size:
                    st.markdown("**Aperçu**")
                    for v, (t, px_v) in cat_tokens.items():
                        if t == "px":
                            label = v.replace("--font-size-", "").upper()
                            st.markdown(
                                f'<p style="font-size:{px_v}px;margin:1px 0;color:#e8e8e8">'
                                f'{label} — {px_v}px</p>',
                                unsafe_allow_html=True
                            )

        if changed_any:
            st.success(
                "✅ `globals.css` mis à jour — Storybook va se recharger.")

        st.markdown("---")
        if st.button("↩️ Restaurer valeurs par défaut (Imperial Purple)", use_container_width=True):
            defaults = {
                "--color-primary": "#8200db",
                "--color-primary-light": "#a346ff",
                "--color-primary-dark": "#5b009d",
                "--color-success": "#22c55e",
                "--color-warning": "#f59e0b",
                "--color-danger": "#ef4444",
                "--color-info": "#3b82f6",
                "--color-text-primary": "#ffffff",
                "--color-text-secondary": "#a1a1aa",
                "--color-text-muted": "#52525b",
                "--color-bg-app": "#080808",
                "--color-bg-card": "#111118",
                "--color-bg-sidebar": "#0d0d12",
                "--color-bg-input": "#1a1a24",
                "--color-border": "#27272a",
                "--color-chart-equities": "#8200db",
                "--color-chart-real-estate": "#3b82f6",
                "--color-chart-fixed-income": "#a346ff",
                "--color-chart-crypto": "#34d399",
                "--color-chart-portfolio-purple": "#8200db",
                "--color-chart-portfolio-gold": "#eab308",
                "--color-text-on-dark": "#ffffff",
                "--color-bg-page": "#0a0a0a",
            }
            for var_name, default_hex in defaults.items():
                write_color_token(GLOBALS_CSS_PATH, var_name, default_hex)
            px_defaults = {
                "--font-size-h1": 48, "--font-size-h2": 36, "--font-size-h3": 24,
                "--font-size-body": 16, "--font-size-sm": 14, "--font-size-xs": 12
            }
            for var_name, default_px in px_defaults.items():
                write_px_token(GLOBALS_CSS_PATH, var_name, default_px)
            st.success("✅ Tous les tokens restaurés !")
            time.sleep(0.3)
            st.rerun()

    with storybook_tab:
        st.markdown("### 🖥️ Live Storybook V2")
        st.caption(
            "Visualisez et interagissez directement avec l'environnement Storybook (port 6008).")

        st.info("Le serveur Storybook démarre en arrière-plan. Cela peut prendre quelques secondes s'il vient d'être lancé.")

        import streamlit.components.v1 as components
        components.iframe("http://localhost:6008", height=700, scrolling=True)

# ██████████████████████████████████████████████████████████████████████████████
# ✍️  CMS AGENT TAB  —  WordPress-like interface
# ██████████████████████████████████████████████████████████████████████████████
elif current_page == "✍️ Agent CMS":
    import json as _json
    import re as _re_cms

    _dist_path = _pathlib.Path(__file__).parent / "dist"

    def _slugify(s: str) -> str:
        import unicodedata
        s = unicodedata.normalize("NFD", s).encode(
            "ascii", "ignore").decode("ascii")
        return _re_cms.sub(r"-+", "-", _re_cms.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")

    def _extract_json(text: str):
        m = _re_cms.search(r'```(?:json)?\s*(\{[\s\S]+?\})\s*```', text)
        if m:
            try:
                return _json.loads(m.group(1))
            except:
                pass
        m2 = _re_cms.search(r'(\{[\s\S]+\})', text)
        if m2:
            try:
                return _json.loads(m2.group(1))
            except:
                pass
        return None

    CMS_SYSTEM_PROMPT = """Tu es un Expert Content Architect spécialisé dans la gestion de CMS Headless ultra-premium.

TES MISSIONS :
1. ANALYSE : Comprendre l'intention (création de page/article, SEO, mise à jour).
2. DESIGN : Générer des structures HTML riches inspirées par Stitch (glassmorphism, typographie moderne).
3. STRUCTURATION : Répondre UNIQUEMENT avec un JSON valide.

RÈGLES DE DESIGN (STITCH-STYLE) :
- Utilise une hiérarchie claire : <h1> pour le titre principal, <h2> pour les sections, <h3> pour les sous-points.
- Introduis chaque article avec une accroche forte dans une <blockquote> pour un aspect premium.
- Utilise des listes à puces (<ul>) pour la scannabilité.
- Ajoute des sections <section> avec des classes sémantiques si nécessaire.
- Le ton doit être visionnaire, inspirant et professionnel.

RÈGLES TECHNIQUES :
- Répondre TOUJOURS en JSON brut.
- status toujours "draft", ai_generated: true.
- Prioriser SEO : meta_title (< 60 chars), meta_description (< 155 chars).

FORMAT JSON :
{
  "title": "...",
  "slug": "...",
  "content": "<h1>...</h1><blockquote>...</blockquote><h2>...</h2><p>...</p>",
  "excerpt": "Résumé premium en 2 phrases.",
  "seo": {"meta_title": "...", "meta_description": "..."},
  "status": "draft",
  "metadata": {"ai_generated": true, "slug_optimized": true}
}"""

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
<span style="font-size:24px">✍️</span>
<h1 style="margin:0;font-size:1.3rem">Agent CMS</h1>
<span style="font-size:11px;background:rgba(219,218,0,0.12);color:#dbda00;border:1px solid rgba(219,218,0,0.3);border-radius:6px;padding:2px 9px">Expert Content Architect</span>
</div>
""", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    _stats = _cmsdb.get_posts_stats()
    _total = sum(_stats.values())
    _cats = len(_cmsdb.get_all_categories())
    _tags_count = len(_cmsdb.get_all_tags())
    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    sc1.metric("📄 Posts total", _total)
    sc2.metric("✅ Publiés", _stats.get("published", 0))
    sc3.metric("🖊️ Brouillons", _stats.get("draft", 0))
    sc4.metric("⏰ Planifiés", _stats.get("scheduled", 0))
    sc5.metric("📂 Catégories", _cats)
    sc6.metric("🏷️ Tags", _tags_count)

    st.markdown("")

    # ── Site Generation ───────────────────────────────────────────────────────
    with st.expander("🚀 Production & Déploiement", expanded=False):
        st.markdown("""
        Convertissez votre contenu en un site web statique HTML/CSS performant.
        Le site sera généré dans le dossier `dist/`.
        """)

        st.markdown("---")
        st.markdown("🏠 **Configuration de la Page d'Accueil**")
        _all_eligible = _cmsdb.get_all_posts()
        _hp = _cmsdb.get_homepage()
        _hp_id = _hp["id"] if _hp else None

        _hp_options = {f"[{p['status'].upper()}] {p['post_type'].upper()} : {p['title']} (/{p['slug']})": p["id"]
                       for p in _all_eligible}
        _hp_labels = list(_hp_options.keys())
        _current_hp_idx = 0
        if _hp_id:
            for i, tid in enumerate(_hp_options.values()):
                if tid == _hp_id:
                    _current_hp_idx = i
                    break

        _col_hp1, _col_hp2 = st.columns([3, 1])
        with _col_hp1:
            _new_hp_label = st.selectbox(
                "Sélectionnez la page d'accueil :",
                _hp_labels,
                index=_current_hp_idx,
                help="Par défaut (si aucune sélection), l'accueil affiche la grille des articles. Note: les brouillons seront publiés s'ils sont choisis."
            )
        with _col_hp2:
            st.markdown("<div style='height:28px'></div>",
                        unsafe_allow_html=True)
            if st.button("Définir", use_container_width=True):
                _new_hp_id = _hp_options[_new_hp_label]
                # If it's a draft, publish it first
                _target_post = _cmsdb.get_post(_new_hp_id)
                if _target_post and _target_post["status"] != "published":
                    _cmsdb.update_post(_new_hp_id, status="published")
                    st.info(
                        f"Page '{_target_post['title']}' publiée automatiquement.")

                _cmsdb.set_homepage(_new_hp_id)
                _trigger_ssg()
                st.success("🏠 Page d'accueil mise à jour !")
                time.sleep(0.5)
                st.rerun()

        st.markdown("---")
        if st.button("Générer le site statique NXSTEP", type="primary", use_container_width=True):
            try:
                _gen = _SiteGen(_cmsdb.db_path)
                with st.spinner("Génération du site en cours..."):
                    _out_path = _gen.generate_site()
                st.success(f"✅ Site généré avec succès !")

                if st.button("📂 Ouvrir la page d'accueil", use_container_width=True):
                    _idx_path = _dist_path / "index.html"
                    if _idx_path.exists():
                        os.startfile(_idx_path)
                    else:
                        st.error(
                            "Site non généré. Veuillez cliquer sur 'Générer le site' ci-dessus.")

                # Show list of generated files
                _files = os.listdir(_out_path)
                st.markdown(f"**Fichiers générés ({len(_files)}) :**")
                st.caption(", ".join(_files))

                st.balloons()
            except Exception as _ge:
                st.error(f"Erreur lors de la génération : `{_ge}`")

    st.markdown("")

    # ── Inner tabs ────────────────────────────────────────────────────────────
    tab_posts, tab_pages, tab_new, tab_cats, tab_tags, tab_agent = st.tabs([
        "📋 Articles",
        "📄 Pages",
        "➕ Nouveau",
        "📂 Catégories",
        "🏷️ Tags",
        "🤖 Agent IA",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : ARTICLES LIST
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_posts:
        st.markdown("### Articles")
        _col_filt1, _col_filt2, _col_filt3 = st.columns([1, 1, 3])
        _status_filter = _col_filt1.selectbox(
            "Statut", ["Tous", "draft", "published", "scheduled"], key="post_status_filter")
        if _col_filt2.button("🔄 Rafraîchir", key="refresh_posts"):
            st.rerun()
        _status_q = None if _status_filter == "Tous" else _status_filter
        _posts = _cmsdb.get_all_posts(post_type="post", status=_status_q)

        if not _posts:
            st.info(
                "Aucun article. Créez votre premier article depuis l'onglet **➕ Nouveau** ou l'**🤖 Agent IA**.")
        else:
            for p in _posts:
                _status_emoji = {"draft": "🖊️", "published": "✅",
                                 "scheduled": "⏰"}.get(p["status"], "❓")
                _is_editing_this = (st.session_state.get(
                    "cms_editing_id") == p["id"])

                with st.expander(
                    f"{_status_emoji} **{p['title']}** — `/{p['slug']}`  ·  {p['updated_at'][:10]}",
                    expanded=_is_editing_this
                ):
                    if _is_editing_this:
                        # ── FULL EDIT FORM ──────────────────────────────────
                        st.markdown("#### ✏️ Modifier l'article")
                        _edit_post = _cmsdb.get_post(p["id"])
                        _all_cats_e = _cmsdb.get_all_categories()
                        _all_tags_e = _cmsdb.get_all_tags()
                        _cat_opt_e = {c["name"]: c["id"] for c in _all_cats_e}
                        _tag_opt_e = {t["name"]: t["id"] for t in _all_tags_e}
                        _cur_cat_names = [c["name"] for c in _all_cats_e if c["id"] in (
                            _edit_post.get("category_ids") or [])]
                        _cur_tag_names = [t["name"] for t in _all_tags_e if t["id"] in (
                            _edit_post.get("tag_ids") or [])]

                        with st.form(f"edit_post_{p['id']}"):
                            _et = st.text_input(
                                "Titre *", value=_edit_post.get("title", ""))
                            _esl = st.text_input(
                                "Slug", value=_edit_post.get("slug", ""))
                            _eex = st.text_area("Extrait", value=_edit_post.get(
                                "excerpt") or "", height=70)
                            _econt = st.text_area("Contenu (HTML)", value=_edit_post.get(
                                "content") or "", height=320)
                            st.markdown("**SEO**")
                            _ems1, _ems2 = st.columns(2)
                            _emt = _ems1.text_input(
                                "Meta Title", value=_edit_post.get("meta_title") or "")
                            _emd = _ems2.text_area("Meta Description", value=_edit_post.get(
                                "meta_description") or "", height=70)
                            st.markdown("**Classification**")
                            _ecat = st.multiselect("Catégories", list(
                                _cat_opt_e.keys()), default=_cur_cat_names, key=f"ecat_{p['id']}")
                            _etag = st.multiselect("Tags", list(
                                _tag_opt_e.keys()), default=_cur_tag_names, key=f"etag_{p['id']}")
                            _est = st.selectbox("Statut", ["draft", "published", "scheduled"],
                                                index=["draft", "published", "scheduled"].index(
                                                    _edit_post.get("status", "draft")),
                                                key=f"est_{p['id']}")
                            _eau = st.text_input(
                                "Auteur", value=_edit_post.get("author") or "Admin")
                            _esub1, _esub2 = st.columns(2)
                            _saved = _esub1.form_submit_button(
                                "💾 Enregistrer", type="primary", use_container_width=True)
                            _cancel = _esub2.form_submit_button(
                                "✖ Annuler", use_container_width=True)

                            if _saved:
                                if not _et.strip():
                                    st.error("Le titre est obligatoire.")
                                else:
                                    _cmsdb.update_post(
                                        p["id"],
                                        title=_et, slug=_esl or _slugify(_et),
                                        content=_econt, excerpt=_eex,
                                        status=_est, meta_title=_emt,
                                        meta_description=_emd, author=_eau,
                                        category_ids=[_cat_opt_e[c]
                                                      for c in _ecat],
                                        tag_ids=[_tag_opt_e[t] for t in _etag],
                                    )
                                    _trigger_ssg()
                                    st.session_state.cms_editing_id = None
                                    st.rerun()
                            if _cancel:
                                st.session_state.cms_editing_id = None
                                st.rerun()
                    else:
                        # ── READ VIEW ──────────────────────────────────────
                        _rv1, _rv2 = st.columns([2, 1])
                        with _rv1:
                            # Rendered HTML preview
                            st.markdown("**📄 Contenu**")
                            _content_html = p.get("content") or ""
                            if _content_html.strip():
                                st.markdown(
                                    f'<div style="background:rgba(255,255,255,0.03);border:1px solid var(--color-border,#27272a);'
                                    f'border-radius:8px;padding:16px 20px;font-size:14px;line-height:1.7;'
                                    f'max-height:400px;overflow-y:auto">'
                                    f'{_content_html}</div>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.caption("Aucun contenu.")
                        with _rv2:
                            st.markdown("**📌 Métadonnées**")
                            st.markdown(
                                f"🏷️ **Catégories :** {p.get('categories') or '—'}")
                            st.markdown(f"🔖 **Tags :** {p.get('tags') or '—'}")
                            st.markdown(
                                f"👤 **Auteur :** {p.get('author') or '—'}")
                            st.markdown(
                                f"📅 **Modifié :** {p.get('updated_at', '')[:16]}")
                            st.markdown("**🔍 SEO**")
                            st.info(
                                f"**{p.get('meta_title') or '—'}**\n\n{p.get('meta_description') or '—'}")
                            _ea, _eb, _ec, _ed = st.columns([1, 1, 1, 1])
                            if _ea.button("✏️ Modifier", key=f"edit_{p['id']}", use_container_width=True, type="primary"):
                                st.session_state.cms_editing_id = p["id"]
                                st.rerun()

                            if _ed.button("🔗 Voir", key=f"view_{p['id']}", use_container_width=True):
                                _fpath = _dist_path / f"{p['slug']}.html"
                                if _fpath.exists():
                                    os.startfile(_fpath)
                                else:
                                    st.warning(
                                        "⚠️ Page non générée. Elle doit être 'Publiée' pour apparaître sur le site.")
                                    if st.button("🚀 Publier maintenant", key=f"pub_quick_{p['id']}"):
                                        _cmsdb.update_post(
                                            p["id"], status="published")
                                        _trigger_ssg()
                                        st.rerun()

                            _new_status = {"draft": "published", "published": "draft"}.get(
                                p["status"], "published")
                            _btn_lbl = {"draft": "✅ Publier", "published": "🖊️ Brouillon",
                                        "scheduled": "✅ Publier"}.get(p["status"], "✅")
                            if _eb.button(_btn_lbl, key=f"toggle_{p['id']}", use_container_width=True):
                                _cmsdb.update_post(p["id"], status=_new_status)
                                _trigger_ssg()
                                st.rerun()
                            if _ec.button("🗑️", key=f"del_{p['id']}", use_container_width=True):
                                _cmsdb.delete_post(p["id"])
                                _trigger_ssg()
                                st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : PAGES LIST
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_pages:
        st.markdown("### Pages")
        _pages = _cmsdb.get_all_posts(post_type="page")
        if not _pages:
            st.info("Aucune page. Créez-en une depuis **➕ Nouveau**.")
        else:
            for p in _pages:
                _status_emoji = {"draft": "🖊️", "published": "✅",
                                 "scheduled": "⏰"}.get(p["status"], "❓")
                _is_editing_page = (st.session_state.get(
                    "cms_editing_id") == p["id"])

                with st.expander(
                    f"{_status_emoji} **{p['title']}** — `/{p['slug']}`",
                    expanded=_is_editing_page
                ):
                    if _is_editing_page:
                        # ── EDIT FORM ───────────────────────────────────────
                        st.markdown("#### ✏️ Modifier la page")
                        _pg = _cmsdb.get_post(p["id"])
                        _all_cats_pg = _cmsdb.get_all_categories()
                        _all_tags_pg = _cmsdb.get_all_tags()
                        _copt_pg = {c["name"]: c["id"] for c in _all_cats_pg}
                        _topt_pg = {t["name"]: t["id"] for t in _all_tags_pg}
                        _ccur_pg = [c["name"] for c in _all_cats_pg if c["id"] in (
                            _pg.get("category_ids") or [])]
                        _tcur_pg = [t["name"] for t in _all_tags_pg if t["id"] in (
                            _pg.get("tag_ids") or [])]

                        with st.form(f"edit_page_{p['id']}"):
                            _pt = st.text_input(
                                "Titre *", value=_pg.get("title", ""))
                            _psl = st.text_input(
                                "Slug", value=_pg.get("slug", ""))
                            _pex = st.text_area("Extrait", value=_pg.get(
                                "excerpt") or "", height=70)
                            _pcont = st.text_area("Contenu (HTML)", value=_pg.get(
                                "content") or "", height=320)
                            st.markdown("**SEO**")
                            _pms1, _pms2 = st.columns(2)
                            _pmt = _pms1.text_input(
                                "Meta Title", value=_pg.get("meta_title") or "")
                            _pmd = _pms2.text_area("Meta Description", value=_pg.get(
                                "meta_description") or "", height=70)
                            _pcat = st.multiselect("Catégories", list(
                                _copt_pg.keys()), default=_ccur_pg, key=f"pcat_{p['id']}")
                            _ptag = st.multiselect("Tags", list(
                                _topt_pg.keys()), default=_tcur_pg, key=f"ptag_{p['id']}")
                            _pst = st.selectbox("Statut", ["draft", "published", "scheduled"],
                                                index=["draft", "published", "scheduled"].index(
                                                    _pg.get("status", "draft")),
                                                key=f"pst_{p['id']}")
                            _pau = st.text_input(
                                "Auteur", value=_pg.get("author") or "Admin")
                            _pb1, _pb2 = st.columns(2)
                            _psaved = _pb1.form_submit_button(
                                "💾 Enregistrer", type="primary", use_container_width=True)
                            _pcancel = _pb2.form_submit_button(
                                "✖ Annuler", use_container_width=True)
                            if _psaved:
                                if not _pt.strip():
                                    st.error("Titre requis.")
                                else:
                                    _cmsdb.update_post(
                                        p["id"],
                                        title=_pt, slug=_psl or _slugify(_pt),
                                        content=_pcont, excerpt=_pex,
                                        status=_pst, meta_title=_pmt,
                                        meta_description=_pmd, author=_pau,
                                        category_ids=[_copt_pg[c]
                                                      for c in _pcat],
                                        tag_ids=[_topt_pg[t] for t in _ptag],
                                    )
                                    _trigger_ssg()
                                    st.session_state.cms_editing_id = None
                                    st.rerun()
                            if _pcancel:
                                st.session_state.cms_editing_id = None
                                st.rerun()
                    else:
                        # Integrated Editor logic
                        if st.session_state.get("visual_editing_slug") == p["slug"]:
                            st.markdown(f"### 🎨 Édition Visuelle : {p['title']}")
                            if st.button("⬅️ Quitter l'éditeur", key=f"quit_vis_{p['id']}"):
                                st.session_state.visual_editing_slug = None
                                st.rerun()
                            
                            import streamlit.components.v1 as components
                            editor_url = f"http://localhost:3000/editor/{p['slug']}"
                            components.iframe(editor_url, height=900, scrolling=True)
                            continue
                        
                        else:
                            # ── READ VIEW ──────────────────────────────────────
                            _pv1, _pv2 = st.columns([2, 1])
                            with _pv1:
                                st.markdown("**📄 Contenu**")
                                _pg_html = p.get("content") or ""
                                if _pg_html.strip():
                                    st.markdown(
                                        f'<div style="background:rgba(255,255,255,0.03);border:1px solid var(--color-border,#27272a);'
                                        f'border-radius:8px;padding:16px 20px;font-size:14px;line-height:1.7;'
                                        f'max-height:400px;overflow-y:auto">{_pg_html}</div>',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    st.caption("Aucun contenu.")
                            with _pv2:
                                st.markdown("**📌 Métadonnées**")
                                st.markdown(
                                    f"👤 **Auteur :** {p.get('author') or '—'}")
                                st.markdown(
                                    f"📅 **Modifié :** {p.get('updated_at', '')[:16]}")
                                st.markdown("**🔍 SEO**")
                                st.info(
                                    f"**{p.get('meta_title') or '—'}**\n\n{p.get('meta_description') or '—'}")
                                _qa, _qb, _qc, _qd, _qe = st.columns([1, 1, 1, 1, 1])
                                if _qa.button("✏️ Modifier", key=f"pedit_{p['id']}", use_container_width=True, type="primary"):
                                    st.session_state.cms_editing_id = p["id"]
                                    st.rerun()

                                if _qb.button("🎨 Visuel", key=f"pvis_{p['id']}", use_container_width=True):
                                    st.session_state.visual_editing_slug = p["slug"]
                                    st.session_state.preview_slug = None
                                    st.rerun()

                                if _qd.button("🔗 Voir", key=f"pview_{p['id']}", use_container_width=True):
                                    import webbrowser
                                    live_url = f"http://localhost:3000/{p['slug']}"
                                    webbrowser.open(live_url)

                                _pnew_s = "published" if p["status"] == "draft" else "draft"
                                _plbl = "✅ Publier" if p["status"] == "draft" else "🖊️ Brouillon"
                                if _qe.button(_plbl, key=f"ptoggle_{p['id']}", use_container_width=True):
                                    _cmsdb.update_post(p["id"], status=_pnew_s)
                                    st.rerun()
                                if _qc.button("🗑️", key=f"pdel_{p['id']}", use_container_width=True):
                                    _cmsdb.delete_post(p["id"])
                                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : NEW POST / PAGE EDITOR
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_new:
        st.markdown("### ✏️ Créer un contenu")
        _ne_type = st.radio(
            "Type", ["Article (post)", "Page"], horizontal=True, key="new_post_type")
        _is_page = "Page" in _ne_type

        with st.form("new_post_form", clear_on_submit=True):
            _f_title = st.text_input(
                "Titre *", placeholder="Mon super article…")
            _f_slug = st.text_input(
                "Slug (auto-généré si vide)", placeholder="mon-super-article")
            _f_excerpt = st.text_area(
                "Extrait / Résumé", height=80, placeholder="Résumé en 2 phrases max.")
            _f_content = st.text_area("Contenu (HTML libre ou Markdown)", height=280,
                                      placeholder="<h2>Introduction</h2>\n<p>Votre contenu…</p>")
            st.markdown("**SEO**")
            _s1, _s2 = st.columns(2)
            _f_meta_title = _s1.text_input(
                "Meta Title", placeholder="Titre SEO ≤ 60 car.")
            _f_meta_desc = _s2.text_area(
                "Meta Description", height=80, placeholder="Description SEO ≤ 155 car.")

            st.markdown("**Classification**")
            _all_cats_fe = _cmsdb.get_all_categories()
            _cat_options = {c["name"]: c["id"] for c in _all_cats_fe}
            _sel_cats = st.multiselect("Catégories", list(
                _cat_options.keys()), key="new_cats")
            _all_tags_fe = _cmsdb.get_all_tags()
            _tag_options = {t["name"]: t["id"] for t in _all_tags_fe}
            _sel_tags = st.multiselect("Tags", list(
                _tag_options.keys()), key="new_tags")

            _f_status = st.selectbox(
                "Statut", ["draft", "published", "scheduled"], key="new_status")
            _f_author = st.text_input("Auteur", value="Admin")

            _submitted = st.form_submit_button(
                "💾 Créer", type="primary", use_container_width=True)
            if _submitted:
                if not _f_title.strip():
                    st.error("Le titre est obligatoire.")
                else:
                    _slug = _f_slug.strip() or _slugify(_f_title)
                    _cat_ids = [_cat_options[c] for c in _sel_cats]
                    _tag_ids = [_tag_options[t] for t in _sel_tags]
                    _new_id = _cmsdb.add_post(
                        title=_f_title, slug=_slug,
                        content=_f_content, excerpt=_f_excerpt,
                        post_type="page" if _is_page else "post",
                        status=_f_status,
                        meta_title=_f_meta_title, meta_description=_f_meta_desc,
                        author=_f_author, ai_generated=False,
                        category_ids=_cat_ids, tag_ids=_tag_ids,
                    )
                    _trigger_ssg()
                    st.success(
                        f"✅ Contenu **{_f_title}** créé (ID {_new_id}) en **{_f_status}** !")
                    time.sleep(0.5)
                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : CATEGORIES
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_cats:
        st.markdown("### 📂 Catégories")
        _cat_col_form, _cat_col_list = st.columns([1, 2])

        with _cat_col_form:
            st.markdown("**Ajouter une catégorie**")
            with st.form("add_cat_form", clear_on_submit=True):
                _cn = st.text_input("Nom *")
                _cs = st.text_input("Slug (auto si vide)")
                _cd = st.text_area("Description", height=80)
                if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                    if _cn.strip():
                        _cmsdb.add_category(
                            _cn.strip(), _cs.strip() or _slugify(_cn), _cd.strip())
                        st.rerun()
                    else:
                        st.warning("Nom requis.")

        with _cat_col_list:
            st.markdown("**Catégories existantes**")
            _all_cats = _cmsdb.get_all_categories()
            if not _all_cats:
                st.info("Aucune catégorie.")
            for cat in _all_cats:
                _npost = _cmsdb.get_category_post_count(cat["id"])
                with st.expander(f"**{cat['name']}** — `/{cat['slug']}`  ({_npost} post{'s' if _npost != 1 else ''})"):
                    with st.form(f"edit_cat_{cat['id']}", clear_on_submit=False):
                        _en = st.text_input(
                            "Nom", value=cat["name"], key=f"cn_{cat['id']}")
                        _es = st.text_input(
                            "Slug", value=cat["slug"], key=f"cs_{cat['id']}")
                        _ed = st.text_area("Description", value=cat.get(
                            "description") or "", key=f"cd_{cat['id']}", height=60)
                        _ec1, _ec2 = st.columns(2)
                        if _ec1.form_submit_button("💾 Enregistrer", use_container_width=True):
                            _cmsdb.update_category(cat["id"], _en, _es, _ed)
                            st.rerun()
                        if _ec2.form_submit_button("🗑️ Supprimer", use_container_width=True):
                            _cmsdb.delete_category(cat["id"])
                            st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : TAGS
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_tags:
        st.markdown("### 🏷️ Tags")
        _tag_form_col, _tag_list_col = st.columns([1, 2])

        with _tag_form_col:
            st.markdown("**Ajouter un tag**")
            with st.form("add_tag_form", clear_on_submit=True):
                _tn = st.text_input("Nom *")
                _ts = st.text_input("Slug (auto si vide)")
                if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
                    if _tn.strip():
                        _cmsdb.add_tag(_tn.strip(), _ts.strip()
                                       or _slugify(_tn))
                        st.rerun()

        with _tag_list_col:
            st.markdown("**Tags existants**")
            _all_tags = _cmsdb.get_all_tags()
            if not _all_tags:
                st.info("Aucun tag.")
            else:
                # Display as chip grid
                _tag_html = ""
                for t in _all_tags:
                    _np = _cmsdb.get_tag_post_count(t["id"])
                    _tag_html += f'<span style="display:inline-flex;align-items:center;gap:6px;background:rgba(219,218,0,0.1);border:1px solid rgba(219,218,0,0.25);border-radius:999px;padding:3px 12px;margin:4px;font-size:12px;color:#dbda00">{t["name"]} <span style="opacity:0.6">({_np})</span></span>'
                st.markdown(
                    f'<div style="margin-bottom:12px">{_tag_html}</div>', unsafe_allow_html=True)

                st.markdown("**Modifier / Supprimer**")
                _sel_tag_name = st.selectbox(
                    "Choisir un tag", [t["name"] for t in _all_tags], key="sel_tag_edit")
                _sel_tag = next(
                    (t for t in _all_tags if t["name"] == _sel_tag_name), None)
                if _sel_tag:
                    with st.form("edit_tag_form", clear_on_submit=False):
                        _etn = st.text_input("Nom", value=_sel_tag["name"])
                        _ets = st.text_input("Slug", value=_sel_tag["slug"])
                        _ta, _tb = st.columns(2)
                        if _ta.form_submit_button("💾 Enregistrer", use_container_width=True):
                            _cmsdb.update_tag(_sel_tag["id"], _etn, _ets)
                            st.rerun()
                        if _tb.form_submit_button("🗑️ Supprimer", use_container_width=True):
                            _cmsdb.delete_tag(_sel_tag["id"])
                            st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # TAB : AI AGENT CHAT
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_agent:
        st.markdown("### 🤖 Agent Content Architect")
        st.caption(
            "Génère du contenu structuré et l'importe automatiquement dans la base CMS.")

        # Quick actions
        _qa1, _qa2, _qa3, _qa4, _qa5 = st.columns(5)
        _cms_quick = None
        if _qa1.button("📄 Article blog", use_container_width=True, key="cms_q1"):
            _cms_quick = "Génère un article de blog complet sur les avantages d'un Design System pour les entreprises SaaS. Ton professionnel, langue française."
        if _qa2.button("🏠 Page Accueil", use_container_width=True, key="cms_q2"):
            _cms_quick = "Crée le contenu de la page d'accueil de NXSTEP : startup spécialisée en IA et automatisation. Ton moderne et premium."
        if _qa3.button("📖 Page À Propos", use_container_width=True, key="cms_q3"):
            _cms_quick = "Génère une page À Propos pour NXSTEP : notre équipe, notre mission, nos valeurs autour de l'IA au service des commerciaux."
        if _qa4.button("🔍 Optimiser SEO", use_container_width=True, key="cms_q4"):
            _cms_quick = "Optimise le SEO du contenu précédent : améliore le meta_title, meta_description, et vérifie la structure H1-H6."
        if _qa5.button("🗑️ Reset", use_container_width=True, key="cms_q5"):
            st.session_state.cms_messages = [st.session_state.cms_messages[0]]
            save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                              st.session_state.design_messages, st.session_state.cms_messages)
            st.rerun()

        st.markdown("")

        # Split: chat | preview
        _ac_chat, _ac_preview = st.columns([1.1, 1], gap="large")

        with _ac_chat:
            _chat_cms = st.container(height=480, border=False)
            with _chat_cms:
                for _m in st.session_state.cms_messages:
                    with st.chat_message(_m["role"]):
                        _pjson = _extract_json(
                            _m["content"]) if _m["role"] == "assistant" else None
                        if _pjson:
                            st.markdown(
                                f"✅ **`{_pjson.get('title', '—')}`** généré")
                            st.code(_json.dumps(
                                _pjson, ensure_ascii=False, indent=2), language="json")
                        else:
                            st.markdown(_m["content"])

            _prompt_cms = _cms_quick or st.chat_input(
                "Ex: Crée un article sur l'IA générative dans le B2B…", key="cms_chat_input")

            if _prompt_cms:
                st.session_state.cms_messages.append(
                    {"role": "user", "content": _prompt_cms})
                save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                                  st.session_state.design_messages, st.session_state.cms_messages)
                with _chat_cms:
                    with st.chat_message("user"):
                        st.markdown(_prompt_cms)
                try:
                    from openai import OpenAI as _OAI
                    _oai = _OAI(api_key=os.environ.get("OPENAI_API_KEY"))
                    _msgs_api = [
                        {"role": "system", "content": CMS_SYSTEM_PROMPT}]
                    for _hm in st.session_state.cms_messages:
                        _msgs_api.append(
                            {"role": _hm["role"], "content": _hm["content"]})
                    with _chat_cms:
                        with st.chat_message("assistant"):
                            with st.spinner("L'Agent structure le contenu…"):
                                _comp = _oai.chat.completions.create(
                                    model="gpt-4o", messages=_msgs_api, temperature=0.7)
                                _cms_resp = _comp.choices[0].message.content or ""
                                _pjson = _extract_json(_cms_resp)
                                if _pjson:
                                    st.markdown(
                                        f"✅ **`{_pjson.get('title', '—')}`** généré")
                                    st.code(_json.dumps(
                                        _pjson, ensure_ascii=False, indent=2), language="json")
                                    # Auto-import into CMS DB
                                    try:
                                        _meta = _pjson.get("metadata", {})
                                        _seo = _pjson.get("seo", {})
                                        _cmsdb.add_post(
                                            title=_pjson.get(
                                                "title", "Sans titre"),
                                            slug=_pjson.get("slug") or _slugify(
                                                _pjson.get("title", "sans-titre")),
                                            content=_pjson.get("content", ""),
                                            excerpt=_pjson.get("excerpt", ""),
                                            post_type="post",
                                            status=_pjson.get(
                                                "status", "draft"),
                                            meta_title=_seo.get(
                                                "meta_title", ""),
                                            meta_description=_seo.get(
                                                "meta_description", ""),
                                            author="AI",
                                            ai_generated=True,
                                            language=_meta.get(
                                                "language", "fr"),
                                        )
                                        _trigger_ssg()
                                        st.success(
                                            "📥 Importé automatiquement dans la liste **Articles** !")
                                    except Exception as _ie:
                                        st.warning(
                                            f"⚠️ Auto-import partiel : `{_ie}`")
                                else:
                                    st.markdown(_cms_resp)
                except Exception as _e:
                    _cms_resp = f"Erreur : `{_e}`"
                    with _chat_cms:
                        with st.chat_message("assistant"):
                            st.error(_cms_resp)
                st.session_state.cms_messages.append(
                    {"role": "assistant", "content": _cms_resp})
                save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                                  st.session_state.design_messages, st.session_state.cms_messages, 
                                  st.session_state.stitch_messages, community_msgs=st.session_state.community_messages)
                time.sleep(0.3)
                st.rerun()

        # ── JSON Preview ───────────────────────────────────────────────────────
        with _ac_preview:
            st.markdown("**📋 Dernier JSON généré**")
            _last_json = None
            for _m in reversed(st.session_state.cms_messages):
                if _m["role"] == "assistant":
                    _last_json = _extract_json(_m["content"])
                    if _last_json:
                        break

            if _last_json:
                _status = _last_json.get("status", "draft")
                _sc = {"draft": "#52525b", "published": "#22c55e",
                       "scheduled": "#f59e0b"}.get(_status, "#52525b")
                _ai = _last_json.get("metadata", {}).get("ai_generated", False)
                st.markdown(
                    f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">'
                    f'<span style="background:{_sc}22;color:{_sc};border:1px solid {_sc}44;border-radius:6px;padding:2px 10px;font-size:11px;font-weight:600">{_status.upper()}</span>'
                    + ('<span style="background:rgba(219,218,0,0.15);color:#dbda00;border:1px solid rgba(219,218,0,0.3);border-radius:6px;padding:2px 10px;font-size:11px">🤖 AI</span>' if _ai else '')
                    + '</div>', unsafe_allow_html=True)
                _seo = _last_json.get("seo", {})
                _mc1, _mc2 = st.columns(2)
                _mc1.markdown(f"**Titre** `{_last_json.get('title', '—')}`")
                _mc1.markdown(f"**Slug** `/{_last_json.get('slug', '—')}`")
                _mc2.markdown(f"**Meta Title** `{_seo.get('meta_title', '—')[:45]}…`" if len(
                    _seo.get('meta_title', '')) > 45 else f"**Meta Title** `{_seo.get('meta_title', '—')}`")
                _mc2.markdown(
                    f"**Langue** `{_last_json.get('metadata', {}).get('language', 'fr')}`")
                st.markdown("**Meta Description**")
                st.info(_seo.get("meta_description", "—"))
                with st.expander("📄 JSON complet"):
                    st.code(_json.dumps(_last_json, ensure_ascii=False,
                            indent=2), language="json")

# ██████████████████████████████████████████████████████████████████████████████
# 🎨 STITCH DESIGN AGENT  —  High-Fidelity UI Generation
# ██████████████████████████████████████████████████████████████████████████████
elif current_page == "🎨 Stitch Design":
    from src.stitch_manager import stitch_mgr

    st.markdown("## 🎨 Stitch Design Studio")
    st.caption(
        "Générez des interfaces premium avec l'IA Stitch et exportez-les vers votre CMS.")

    # Check for API Key (Env or DB)
    if not os.environ.get("STITCH_API_KEY") and not stitch_mgr.get_config("stitch_api_key"):
        st.warning(
            "⚠️ **Clé API Stitch manquante.** Pour utiliser Archi, vous devez configurer votre clé dans la section en bas de page.")
        # But we still show the chat to allow them to configure it
        st.session_state.stitch_project_id = stitch_mgr.get_config(
            "last_project_id")

    _col_chat, _col_preview = st.columns([1, 1])

    with _col_chat:
        st.markdown("### 💬 Conversation avec Archi")
        for m in st.session_state.stitch_messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Décrivez le design que vous voulez générer...", key="stitch_input"):
            st.session_state.stitch_messages.append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.status("Génération du design via Stitch...", expanded=True) as status:
                    from src.orchestrator import client, stitch_agent
                    response = client.run(
                        agent=stitch_agent,
                        messages=st.session_state.stitch_messages,
                    )
                    _resp = response.messages[-1]["content"]
                    st.markdown(_resp)
                    status.update(label="Design généré !", state="complete")

            st.session_state.stitch_messages.append(
                {"role": "assistant", "content": _resp})
            save_chat_history(st.session_state.lead_messages, st.session_state.kanban_messages,
                              st.session_state.design_messages, st.session_state.cms_messages, 
                              st.session_state.stitch_messages, community_msgs=st.session_state.community_messages)
            st.rerun()

    with _col_preview:
        st.markdown("### 🖼️ Aperçu & Actions")

        # Project/Screen Status (Direct Connection)
        st.info("✅ **Connexion Directe Active** (via Stitch MCP Server)")

        # Display latest screen if available
        current_screen_id = st.session_state.get("current_stitch_screen_id")
        if not current_screen_id:
            current_screen_id = stitch_mgr.get_config("current_screen_id")

        if not current_screen_id:
            st.info(
                "Aucun design n'est actuellement affiché. Demandez à Archi d'en créer un !")
        else:
            st.success(f"Design ID: `{current_screen_id}`")
            if st.button("🚀 Exporter vers le CMS NXSTEP", use_container_width=True):
                with st.spinner("Récupération du code et export vers le CMS..."):
                    res = stitch_mgr.fetch_and_export_to_cms(
                        current_screen_id, f"Design Stitch {current_screen_id[:8]}")
                    if res.get("success"):
                        _trigger_ssg()  # Générer les fichiers statiques immédiatement
                        st.balloons()
                        st.success(
                            f"Page exportée et publiée avec succès ! (ID CMS: {res['post_id']}).")
                    else:
                        st.error(
                            f"Erreur lors de l'export : {res.get('error')}")

    st.markdown("---")
    with st.expander("🛠️ Configuration Stitch & Connexion"):
        st.caption(
            "Une **Stitch API Key** est désormais REQUISE pour le fonctionnement d'Archi.")

        # Charger la clé depuis la DB si elle n'est pas déjà dans l'environement
        saved_key = stitch_mgr.get_config("stitch_api_key")
        current_env_key = os.environ.get("STITCH_API_KEY", "")

        _api_key = st.text_input(
            "Stitch API Key (Requis)", value=saved_key or current_env_key, type="password")

        if _api_key:
            os.environ["STITCH_API_KEY"] = _api_key
            if _api_key != saved_key:
                stitch_mgr.set_config("stitch_api_key", _api_key)

            # S'assurer que le client est initialisé avec la bonne clé
            from src.mcp_client import get_stitch_client
            get_stitch_client(api_key=_api_key)

        _mc1, _mc2 = st.columns(2)
        saved_pid = stitch_mgr.get_config("last_project_id") or ""
        saved_sid = stitch_mgr.get_config("current_screen_id") or ""
        new_pid = _mc1.text_input("Project ID Stitch", value=st.session_state.get(
            "stitch_project_id", saved_pid))
        new_sid = _mc2.text_input("Screen ID Actuel", value=st.session_state.get(
            "current_stitch_screen_id", saved_sid))

        if st.button("Sauvegarder la configuration", use_container_width=True):
            stitch_mgr.set_config("last_project_id", new_pid)
            stitch_mgr.set_config("current_screen_id", new_sid)
            st.session_state.stitch_project_id = new_pid
            st.session_state.current_stitch_screen_id = new_sid
            st.success(
                "Paramètres enregistrés. La session Archi est désormais autonome.")
elif current_page == "❓ FAQ Stitch":
    st.title("❓ FAQ : Utilisation de Stitch Agent")
    st.markdown(
        "Suivez ce guide pour configurer Archi et générer vos designs premium.")

    with st.expander("🔑 Comment obtenir ma Stitch API Key ?", expanded=True):
        st.markdown("""
        L'agent Archi nécessite une clé API pour communiquer avec le moteur de design Google Stitch.
        
        **Étapes pour obtenir votre clé :**
        1.  **Google AI Studio** : Rendez-vous sur [Google AI Studio (Gemini)](https://aistudio.google.com/app/apikey).
        2.  **Création** : Cliquez sur **'Create API Key'**.
        3.  **Copie** : Copiez la clé générée (elle commence généralement par `AIza...`).
        4.  **Configuration** : Retournez dans l'onglet **🎨 Stitch Design** de ce dashboard, dépliez la section **Configuration** en bas, et collez votre clé.
        
        > [!NOTE]
        > La clé Stitch est en réalité une clé API Gemini standard qui dispose des permissions pour utiliser les outils de génération d'UI Stitch.
        """)

    with st.expander("🚀 Comment utiliser Archi pour créer un site ?"):
        st.markdown("""
        Une fois votre clé configurée :
        1.  **Chat** : Allez dans **🎨 Stitch Design** et décrivez votre besoin à Archi (ex: *"Crée une landing page sombre pour une agence de cybersécurité"*).
        2.  **Attente** : La génération prend environ 1 à 2 minutes. La connexion est directe et autonome.
        3.  **Export** : Une fois le design ID affiché, cliquez sur **'Exporter vers le CMS'**.
        4.  **Publication** : Allez dans **✍️ Agent CMS**, retrouvez votre design dans l'onglet **Pages**, et publiez-le pour qu'il soit visible sur votre site statique.
        """)

    with st.expander("🛠️ Dépannage : Erreur 'pywintypes'"):
        st.markdown("""
        Si vous voyez une erreur mentionnant `ModuleNotFoundError: No module named 'pywintypes'` :
        - C'est un problème courant sur Windows lié aux environnements virtuels.
        - **Solution** : J'ai intégré un correctif automatique au démarrage de l'application. Si l'erreur persiste, fermez votre terminal et relancez le dashboard avec :
        ```cmd
        .\\\\venv\\\\Scripts\\\\python -m streamlit run chat_app.py
        ```
        """)

    st.info("💡 **Conseil** : Pour des designs optimaux, soyez précis dans vos prompts (couleurs, style, sections souhaitées).")
