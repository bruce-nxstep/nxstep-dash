"""
openai_client.py
Uses OpenAI GPT-4o to extract structured CV data from raw text,
returning a JSON object that matches the NXSTEP ATS template schema.
"""
import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """Tu es un expert en rédaction de CV ATS (Applicant Tracking System).
Ta mission est d'analyser le CV fourni et d'en extraire les informations structurées
selon le format JSON exact ci-dessous. Le CV de sortie doit être:
- Optimisé pour les ATS (pas de tableaux, colonnes, graphiques)
- Clair, professionnel et en adéquation avec la langue du CV original
- Les bullets doivent être concis et orientés résultats/compétences

Retourne UNIQUEMENT un objet JSON valide, sans commentaires, sans markdown, sans backticks.
Respecte exactement ce schéma:

{
  "nom_complet": "string",
  "titre_poste": "string (poste / rôle visé ou actuel)",
  "contact": {
    "email": "string ou null",
    "telephone": "string ou null",
    "localisation": "string ou null",
    "linkedin": "string ou null",
    "github": "string ou null"
  },
  "profil": "string (résumé professionnel de 3-5 lignes, narratif, orienté valeur apportée)",
  "competences": [
    {
      "categorie": "string (ex: Gestion des Identités et des Accès)",
      "items": ["string", "string", "..."]
    }
  ],
  "outils_techniques": ["string", "string", "..."],
  "experiences": [
    {
      "poste": "string",
      "entreprise": "string",
      "periode": "string (ex: Jan 2022 – Déc 2023)",
      "contexte": "string (description courte du contexte)",
      "mission": "string (objectif principal de la mission)",
      "activites": ["string", "string", "..."],
      "environnement_technique": ["string", "string", "..."]
    }
  ],
  "formations": [
    {
      "diplome": "string",
      "etablissement": "string",
      "annee": "string ou null"
    }
  ],
  "certifications": ["string", "string"],
  "langues": [
    {
      "langue": "string",
      "niveau": "string (ex: Courant, Intermédiaire, Notions)"
    }
  ],
  "centres_interet": ["string", "string"]
}

Si une information est absente du CV fourni, utilise null ou une liste vide [].
N'invente aucune information. Extrait uniquement ce qui est présent dans le CV.
"""


def extract_cv_data(raw_text: str, api_key: str) -> dict:
    """
    Send raw CV text to GPT-4o and return structured JSON data.
    
    Args:
        raw_text: The extracted CV text
        api_key: OpenAI API key
    
    Returns:
        Parsed dict matching the NXSTEP ATS schema
    """
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Voici le CV à analyser et reformater:\n\n{raw_text}"
            }
        ],
        temperature=0.2,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    return json.loads(content)
