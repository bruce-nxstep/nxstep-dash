"""
test_generator.py
Quick validation: generates a sample PDF + DOCX + ZIP from dummy CV data
without needing an OpenAI key.
"""
import sys, os, zipfile, io
sys.path.insert(0, os.path.dirname(__file__))

from cv_generator import generate_cv_pdf
from docx_generator import generate_cv_docx

SAMPLE_DATA = {
    "nom_complet": "Jean Martin",
    "titre_poste": "Ingénieur IAM / Cybersécurité",
    "contact": {
        "email": "jean.martin@email.com",
        "telephone": "+33 6 12 34 56 78",
        "localisation": "Paris, France",
        "linkedin": "linkedin.com/in/jeanmartin",
        "github": None
    },
    "profil": "Ingénieur en sécurité informatique avec 5 ans d'expérience dans la gestion des identités et des accès (IAM/PAM). Expert en déploiement de solutions CyberArk, One Identity et Microsoft Active Directory dans des environnements critiques et multisites. Certifié ISO 27001, passionné par l'architecture Zero Trust et la conformité RGPD.",
    "competences": [
        {
            "categorie": "Gestion des Identités et des Accès (IAM/PAM)",
            "items": [
                "Administration centralisée des identités via One Identity | Active Roles",
                "Sécurisation et gestion des comptes à privilèges avec CyberArk",
                "Implémentation du modèle Zero Trust et principe du moindre privilège"
            ]
        },
        {
            "categorie": "Authentification et Sécurité des Accès",
            "items": [
                "Déploiement et gestion de l'authentification multi-facteurs (MFA)",
                "Configuration d'Okta Verify et Microsoft Authenticator"
            ]
        }
    ],
    "outils_techniques": ["One Identity", "CyberArk", "Active Directory", "ServiceNow", "MFA", "Intune", "AWS", "Azure", "Citrix", "ISO 27001"],
    "experiences": [
        {
            "poste": "Ingénieur IAM / Support N1-N2",
            "entreprise": "Hait Tech (mission grands comptes)",
            "periode": "Jan 2022 – Présent",
            "contexte": "Missions pour trois grands comptes internationaux dans des environnements critiques.",
            "mission": "Assurer le support N1/N2, la gestion des identités et la sécurisation des accès.",
            "activites": [
                "Administration des comptes via One Identity | Active Roles",
                "Sécurisation des accès à privilèges via CyberArk",
                "Déploiement et gestion du MFA (Okta Verify, Microsoft Authenticator)"
            ],
            "environnement_technique": ["One Identity", "CyberArk", "Active Directory", "ServiceNow", "AWS", "Azure"]
        }
    ],
    "formations": [{"diplome": "Master en Cybersécurité", "etablissement": "Université Paris-Saclay", "annee": "2021"}],
    "certifications": ["ISO 27001 Lead Implementer", "AWS Cloud Practitioner"],
    "langues": [
        {"langue": "Français", "niveau": "Courant"},
        {"langue": "Anglais", "niveau": "Intermédiaire (B2)"}
    ],
    "centres_interet": ["Karaté", "Football", "Cinéma", "Documentaires Tech"]
}

if __name__ == "__main__":
    print("Generating PDF...")
    pdf_bytes = generate_cv_pdf(SAMPLE_DATA)
    print(f"  ✅ PDF: {len(pdf_bytes):,} bytes")

    print("Generating DOCX...")
    docx_bytes = generate_cv_docx(SAMPLE_DATA)
    print(f"  ✅ DOCX: {len(docx_bytes):,} bytes")

    print("Packing ZIP...")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("CV_ATS_Jean_Martin.pdf",  pdf_bytes)
        zf.writestr("CV_ATS_Jean_Martin.docx", docx_bytes)
    zip_bytes = zip_buffer.getvalue()
    with open("test_cv_output.zip", "wb") as f:
        f.write(zip_bytes)
    print(f"  ✅ ZIP: {len(zip_bytes):,} bytes → test_cv_output.zip")
    print("\n🎉 All formats generated successfully!")
