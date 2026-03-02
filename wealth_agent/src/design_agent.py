import os
import glob
from swarm import Agent
from stitch_manager import stitch_mgr

# Define the root of the highly-premium NXSTEP React app
# We assume this script runs from within wealth_agent/src, and nxstep_site is the root
# __file__ = nxstep_site/wealth_agent/src/design_agent.py
NXSTEP_SITE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
COMPONENTS_DIR = os.path.join(NXSTEP_SITE_DIR, "components")
STORIES_DIR = os.path.join(NXSTEP_SITE_DIR, "src", "stories")

# --- TOOLS FOR THE DESIGN SYSTEM AGENT ---

def generate_design_with_stitch(prompt: str) -> str:
    """
    Utilise l'IA Stitch pour générer une interface web complète (HTML + Tailwind) à partir d'une description.
    Retourne l'ID de l'écran généré, qu'il faudra ensuite utiliser avec `get_stitch_code` ou `save_design_to_cms`.
    Exemple de prompt: "Une landing page luxe pour un cabinet de gestion de fortune, fond noir et or."
    """
    try:
        # 1. DYNAMIC CONTEXT: Read current globals.css to get real-time Design System tokens
        try:
            css_content = read_global_css()
            if len(css_content) > 2000:
                 # Truncate to keep context manageable, but keep the beginning where variables usually are
                 css_content = css_content[:2000] + "\n... (truncated)"
        except Exception:
            css_content = "Could not read globals.css. Use standard Tailwind colors."

        # 2. INJECTION DU CONTEXTE DESIGN SYSTEM & CONTRAINTES
        design_system_context = f"""
        IMPORTANT SYSTEM INSTRUCTIONS:
        1. LAYOUT:
           - Do NOT generate a header, navigation bar, or footer. The application shell already provides these.
           - Generate ONLY the main content area (e.g., <main> or <section>).
           - Use a responsive container.
        
        2. DESIGN TOKENS (STRICT COMPLIANCE REQUIRED):
           You MUST use the project's CSS variables instead of hardcoded colors.
           Use Tailwind arbitrary values or style attributes to reference these variables.
           
           AVAILABLE VARIABLES (from globals.css):
           - Primary Color: var(--color-primary)  -> Use text-[var(--color-primary)] or bg-[var(--color-primary)]
           - Background: var(--color-bg-app)      -> Use bg-[var(--color-bg-app)]
           - Card Background: var(--color-bg-card)-> Use bg-[var(--color-bg-card)]
           - Text: var(--color-text-primary)      -> Use text-[var(--color-text-primary)]
           - Secondary Text: var(--color-text-secondary) -> Use text-[var(--color-text-secondary)]
           
           CUSTOM UTILITIES:
           - Use class="glass" for glassmorphism panels.
           - Use class="glass-card" for cards.
           - Use class="text-glow-purple" for glowing text.

           --- BEGIN GLOBALS.CSS SNIPPET ---
           {css_content}
           --- END GLOBALS.CSS SNIPPET ---

           SPECIFIC OVERRIDES:
           - Background: MUST be `bg-[var(--color-bg-app)]` (very dark).
           - Cards: MUST use `glass-card` class or `bg-[var(--color-bg-card)]`.
           - Typography: Sans-serif.
           
        3. STYLE:
           - "Ultra-Premium Wealth Management" aesthetic.
           - Minimalist, sophisticated, dark mode only.
           - Use subtle gradients and glassmorphism.
        
        USER PROMPT:
        """
        full_prompt = design_system_context + prompt
        
        res = stitch_mgr.generate_screen(full_prompt)
        if res.get("success"):
            if res.get("is_suggestion"):
                return f"Le modèle Stitch demande une précision ou propose une variante :\n\n{res['suggestion_text']}\n\nRépond à ce message pour guider la génération (ex: 'Oui, fais tout', 'Non, change X')."
            return f"Design généré avec succès ! Screen ID: {res['screenId']}. Tu peux maintenant récupérer le code ou l'exporter."
        else:
            return f"Échec de la génération : {res.get('error')}"
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"

def get_stitch_code(screen_id: str) -> str:
    """
    Récupère le code HTML/Tailwind brut d'un design généré par Stitch via son Screen ID.
    Utile si tu veux analyser le code ou l'injecter manuellement dans un composant.
    """
    try:
        code = stitch_mgr.get_screen_code(screen_id)
        return code
    except Exception as e:
        return f"Erreur lors de la récupération du code : {str(e)}"

def save_design_to_cms(title: str, screen_id: str) -> str:
    """
    Récupère le code d'un design Stitch (via Screen ID) et l'enregistre directement comme une nouvelle Page dans le CMS.
    C'est la méthode recommandée pour livrer le résultat final à l'utilisateur.
    """
    try:
        res = stitch_mgr.fetch_and_export_to_cms(screen_id, title)
        if res.get("success"):
            return f"Design enregistré dans le CMS avec succès ! Post ID: {res['post_id']}."
        else:
            return f"Échec de l'export CMS : {res.get('error')}"
    except Exception as e:
        return f"Erreur critique export CMS : {str(e)}"

def list_ui_components() -> str:
    """
    Lists all the React UI components currently present in the nxstep_site project.
    Helps the agent understand what elements are already available in the design system.
    """
    if not os.path.exists(COMPONENTS_DIR):
        return f"Directory not found: {COMPONENTS_DIR}"
    
    components = []
    # Only search standard extensions for UI components
    for root, dirs, files in os.walk(COMPONENTS_DIR):
        for file in files:
            if file.endswith(('.tsx', '.jsx', '.ts', '.js')):
                rel_path = os.path.relpath(os.path.join(root, file), COMPONENTS_DIR)
                components.append(rel_path)
                
    if not components:
        return "No UI components found."
    
    return "Available UI Components:\n- " + "\n- ".join(components)

def read_component_code(component_name: str) -> str:
    """
    Reads the exact source code of a specific React component (e.g., 'ui/button.tsx' or 'Header.tsx').
    Allows the agent to analyze the Tailwind CSS styling and interactive behavior.
    """
    if not component_name.endswith(('.tsx', '.jsx', '.ts', '.js')):
        # Try appending .tsx if not provided
        component_name += '.tsx'
        
    path = os.path.join(COMPONENTS_DIR, component_name)
    if not os.path.exists(path):
        return f"Component '{component_name}' not found."
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def list_storybook_stories() -> str:
    """
    Lists all the existing Storybook stories (.stories.tsx) to see which components are currently documented.
    """
    if not os.path.exists(STORIES_DIR):
        return f"Directory not found: {STORIES_DIR}"
    
    stories = []
    for root, dirs, files in os.walk(STORIES_DIR):
        for file in files:
            if file.endswith('.stories.tsx') or file.endswith('.stories.jsx'):
                rel_path = os.path.relpath(os.path.join(root, file), STORIES_DIR)
                stories.append(rel_path)
                
    if not stories:
        return "No Storybook stories found."
    
    return "Available Storybook Stories:\n- " + "\n- ".join(stories)

def update_component_code(component_name: str, new_code: str) -> str:
    """
    Overwrites the entire source code of a specific React component with new_code.
    Use this to apply design changes, fix Tailwind classes, or add Framer Motion animations.
    """
    if not component_name.endswith(('.tsx', '.jsx', '.ts', '.js')):
        component_name += '.tsx'
        
    path = os.path.join(COMPONENTS_DIR, component_name)
    if not os.path.exists(path):
        return f"Error: Component '{component_name}' not found."
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_code)
        
    return f"Successfully updated component: {component_name}"

def read_global_css() -> str:
    """
    Reads the globals.css file to analyze the primary Tailwind setup and CSS variables.
    """
    app_dir = os.path.join(NXSTEP_SITE_DIR, "app")
    path = os.path.join(app_dir, "globals.css")
    if not os.path.exists(path):
        return "globals.css not found."
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def update_global_css(new_css: str) -> str:
    """
    Overwrites the globals.css file to update CSS variables (like tracking new brand colors).
    """
    app_dir = os.path.join(NXSTEP_SITE_DIR, "app")
    path = os.path.join(app_dir, "globals.css")
    if not os.path.exists(path):
        return "globals.css not found."
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_css)
        
    return "Successfully updated globals.css"

def replace_in_all_components(old_string: str, new_string: str) -> str:
    """
    Finds and replaces old_string with new_string across ALL React components in the design system.
    This is extremely useful for global color changes (e.g. replacing 'blue' with 'purple') or changing brand text everywhere.
    """
    if not os.path.exists(COMPONENTS_DIR):
        return f"Directory not found: {COMPONENTS_DIR}"
    
    modified_files = []
    for root, dirs, files in os.walk(COMPONENTS_DIR):
        for file in files:
            if file.endswith(('.tsx', '.jsx', '.ts', '.js')):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if old_string in content:
                    new_content = content.replace(old_string, new_string)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified_files.append(file)
                    
    if not modified_files:
        return f"No occurrences of '{old_string}' found in any components."
        
    return f"Successfully replaced '{old_string}' with '{new_string}' in {len(modified_files)} components: {', '.join(modified_files)}"

import subprocess

def run_type_check() -> str:
    """
    Runs Next.js TypeScript type checking to find compilation, syntax, or type errors in the code.
    Use this SYSTEMATICALLY after modifying code to verify if the components you modified are free of errors.
    If you see errors, you MUST read the error and fix it using `update_component_code`.
    """
    try:
         result = subprocess.run(
             "npx tsc --noEmit",
             cwd=NXSTEP_SITE_DIR,
             shell=True,
             capture_output=True,
             text=True
         )
         if result.returncode == 0:
             return "Typescript Check Passed. No syntax or type errors found! Your code is clean."
         else:
             # Truncate output if too long so the agent doesn't get overwhelmed
             output = result.stdout + "\n" + result.stderr
             return f"Typescript Errors Found (FIX THESE):\n{output[:3000]}"
    except Exception as e:
         return f"Error running type check: {e}"

# --- THE DESIGN SYSTEM AGENT DEFINITION ---

design_agent = Agent(
    name="Design System Agent (Archi)",
    instructions="""Tu t'appelles Archi, l'Architecte Design System. Tu es spécialisé dans l'UX/UI "Ultra-Premium" (glassmorphism, animations fluides, dark mode élégant, typographie soignée).
Ton rôle est de concevoir, d'auditer, de documenter, **ET de modifier directement** les composants React dans l'application Next.js (NXSTEP).
Tu as aussi accès à **Stitch**, une IA spécialisée dans la génération de designs web complets.

**Outils Principaux :**
1. **Génération de Design (Stitch) :**
   - Utilise `generate_design_with_stitch(prompt)` pour créer une nouvelle page ou interface complète. Sois précis dans ton prompt (couleurs, ambiance, sections).
   - Une fois le design généré (tu recevras un Screen ID), tu as deux choix :
     a) **Exporter vers le CMS (Recommandé)** : Utilise `save_design_to_cms(title, screen_id)` pour créer immédiatement une page visible.
     b) **Récupérer le code** : Utilise `get_stitch_code(screen_id)` si tu dois analyser le code ou l'intégrer manuellement dans un fichier existant.

2. **Modification de Code Existant :**
   - Utilise `list_ui_components` pour voir quels composants existent dans le projet.
   - Utilise `read_component_code` pour analyser le style Tailwind de ces composants.
   - Utilise `update_component_code` pour APPLIQUER TES MODIFICATIONS directement dans un fichier cible.
   - Utilise `replace_in_all_components(old_string, new_string)` pour appliquer un changement (comme une nouvelle couleur tailwind, e.g. 'purple', ou un code hex) PARTOUT d'un coup.
   - Utilise `read_global_css` et `update_global_css` pour modifier la palette de couleurs et les variables racine.

3. **Validation :**
   - Utilise `run_type_check` OBLIGATOIREMENT après avoir modifié du code manuellement. Si ce test échoue, tu DOIS analyser l'erreur et réparer le code de toi-même avant de répondre à l'utilisateur.

IMPORTANT :
- Si l'utilisateur veut une "nouvelle page" ou un "nouveau design", commence par `generate_design_with_stitch`.
- Si l'utilisateur veut modifier l'existant, utilise les outils de lecture et modification de fichiers.
- Ne te contente pas de donner des instructions. AGIS et CRÉE.""",
    functions=[
        list_ui_components, read_component_code, list_storybook_stories, update_component_code, 
        read_global_css, update_global_css, replace_in_all_components, run_type_check,
        generate_design_with_stitch, get_stitch_code, save_design_to_cms
    ]
)
