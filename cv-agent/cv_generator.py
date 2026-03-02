"""
cv_generator.py
Generates an ATS-compliant PDF CV from structured data,
following the NXSTEP template structure.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# ─── COLOUR PALETTE (ATS-safe: No images, no decorative columns) ──────────────
C_BLACK = colors.HexColor("#0D0D0D")
C_DARK  = colors.HexColor("#1A1A2E")
C_ACCENT = colors.HexColor("#2E4057")
C_MID   = colors.HexColor("#4A5568")
C_LIGHT = colors.HexColor("#718096")
C_LINE  = colors.HexColor("#CBD5E0")
C_WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN_LEFT   = 2.0 * cm
MARGIN_RIGHT  = 2.0 * cm
MARGIN_TOP    = 1.8 * cm
MARGIN_BOTTOM = 1.8 * cm
CONTENT_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT


def _styles():
    """Build and return all paragraph styles used in the document."""
    s = getSampleStyleSheet()

    styles = {
        # ── Name (hero) ──────────────────────────────────────────────
        "Name": ParagraphStyle(
            "Name",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=C_BLACK,
            spaceAfter=2,
            spaceBefore=0,
            leading=26,
        ),
        # ── Job Title ────────────────────────────────────────────────
        "Title": ParagraphStyle(
            "Title",
            fontName="Helvetica",
            fontSize=12,
            textColor=C_ACCENT,
            spaceAfter=4,
            leading=16,
        ),
        # ── Contact line ─────────────────────────────────────────────
        "Contact": ParagraphStyle(
            "Contact",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MID,
            spaceAfter=2,
            leading=12,
        ),
        # ── Section header ───────────────────────────────────────────
        "Section": ParagraphStyle(
            "Section",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=C_DARK,
            spaceBefore=14,
            spaceAfter=3,
            leading=14,
        ),
        # ── Sub-header inside section (e.g. skill category, job role) ─
        "SubHeader": ParagraphStyle(
            "SubHeader",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=C_ACCENT,
            spaceBefore=7,
            spaceAfter=2,
            leading=13,
        ),
        # ── Company / Institution ─────────────────────────────────────
        "Company": ParagraphStyle(
            "Company",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=C_MID,
            spaceAfter=2,
            leading=13,
        ),
        # ── Plain body text ─────────────────────────────────────────
        "Body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=9,
            textColor=C_BLACK,
            spaceAfter=2,
            leading=13,
        ),
        # ── Bullet item ─────────────────────────────────────────────
        "Bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=9,
            textColor=C_BLACK,
            leftIndent=10,
            firstLineIndent=-10,
            spaceAfter=1,
            leading=13,
            bulletIndent=0,
        ),
        # ── Tag / keyword (for outils, env. technique, interests) ───
        "Tag": ParagraphStyle(
            "Tag",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=C_MID,
            spaceAfter=2,
            leading=12,
        ),
        # ── Label for metadata fields (Langues, etc.) ────────────────
        "Label": ParagraphStyle(
            "Label",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=C_BLACK,
        ),
    }
    return styles


def _hr(color=C_LINE, thickness=0.5):
    return HRFlowable(
        width="100%",
        thickness=thickness,
        color=color,
        spaceAfter=4,
        spaceBefore=1,
    )


def _section(title: str, st: dict):
    """Return a section header + rule."""
    return [
        Paragraph(title.upper(), st["Section"]),
        _hr(C_ACCENT, 1),
    ]


def _bullets(items: list, st: dict):
    """Convert a list of strings to bullet Paragraphs."""
    result = []
    for item in items:
        if item and item.strip():
            result.append(Paragraph(f"• {item.strip()}", st["Bullet"]))
    return result


def generate_cv_pdf(data: dict) -> bytes:
    """
    Generate an ATS-compliant PDF from structured CV data dict.
    Returns the PDF as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=f"CV – {data.get('nom_complet', 'Candidat')}",
        author="NXSTEP ATS CV Generator",
        subject="CV ATS",
        creator="NXSTEP",
    )

    st = _styles()
    story = []

    # ══════════════════════════════════════════════════════════════════
    # HEADER – Name + Title + Contact
    # ══════════════════════════════════════════════════════════════════
    nom = data.get("nom_complet") or "Candidat"
    titre = data.get("titre_poste") or ""
    contact = data.get("contact") or {}

    story.append(Paragraph(nom, st["Name"]))
    if titre:
        story.append(Paragraph(titre, st["Title"]))

    # Build contact line
    contact_parts = []
    if contact.get("email"):
        contact_parts.append(contact["email"])
    if contact.get("telephone"):
        contact_parts.append(contact["telephone"])
    if contact.get("localisation"):
        contact_parts.append(contact["localisation"])
    if contact.get("linkedin"):
        contact_parts.append(contact["linkedin"])
    if contact.get("github"):
        contact_parts.append(contact["github"])
    if contact_parts:
        story.append(Paragraph("  |  ".join(contact_parts), st["Contact"]))

    story.append(_hr(C_BLACK, 1.5))

    # ══════════════════════════════════════════════════════════════════
    # PROFIL PROFESSIONNEL
    # ══════════════════════════════════════════════════════════════════
    profil = data.get("profil")
    if profil:
        story += _section("Profil Professionnel", st)
        story.append(Paragraph(profil, st["Body"]))

    # ══════════════════════════════════════════════════════════════════
    # COMPÉTENCES / SAVOIR-FAIRE
    # ══════════════════════════════════════════════════════════════════
    competences = data.get("competences") or []
    if competences:
        story += _section("Compétences & Savoir-Faire", st)
        for cat in competences:
            cat_name = cat.get("categorie") or ""
            items = cat.get("items") or []
            if cat_name:
                story.append(Paragraph(cat_name, st["SubHeader"]))
            story += _bullets(items, st)

    # ══════════════════════════════════════════════════════════════════
    # OUTILS TECHNIQUES
    # ══════════════════════════════════════════════════════════════════
    outils = data.get("outils_techniques") or []
    if outils:
        story += _section("Outils & Technologies", st)
        story.append(Paragraph(", ".join(o for o in outils if o), st["Tag"]))

    # ══════════════════════════════════════════════════════════════════
    # EXPÉRIENCES PROFESSIONNELLES
    # ══════════════════════════════════════════════════════════════════
    experiences = data.get("experiences") or []
    if experiences:
        story += _section("Expériences Professionnelles", st)
        for exp in experiences:
            poste = exp.get("poste") or ""
            entreprise = exp.get("entreprise") or ""
            periode = exp.get("periode") or ""
            contexte = exp.get("contexte") or ""
            mission = exp.get("mission") or ""
            activites = exp.get("activites") or []
            env_tech = exp.get("environnement_technique") or []

            # Role line: Poste – Entreprise · Période
            role_parts = []
            if poste:
                role_parts.append(f"<b>{poste}</b>")
            if entreprise:
                role_parts.append(entreprise)
            if periode:
                role_parts.append(f"<font color='#718096'>{periode}</font>")
            story.append(Paragraph("  –  ".join(role_parts), st["SubHeader"]))

            if contexte:
                story.append(Paragraph(f"<b>Contexte :</b> {contexte}", st["Body"]))
            if mission:
                story.append(Paragraph(f"<b>Mission :</b> {mission}", st["Body"]))
            if activites:
                story.append(Paragraph("Activités :", st["Body"]))
                story += _bullets(activites, st)
            if env_tech:
                env_line = ", ".join(e for e in env_tech if e)
                story.append(
                    Paragraph(
                        f"<b>Environnement technique :</b> {env_line}",
                        st["Tag"]
                    )
                )
            story.append(Spacer(1, 4))

    # ══════════════════════════════════════════════════════════════════
    # FORMATIONS
    # ══════════════════════════════════════════════════════════════════
    formations = data.get("formations") or []
    if formations:
        story += _section("Formation", st)
        for f in formations:
            diplome = f.get("diplome") or ""
            etab = f.get("etablissement") or ""
            annee = f.get("annee") or ""
            parts = []
            if diplome:
                parts.append(f"<b>{diplome}</b>")
            if etab:
                parts.append(etab)
            if annee:
                parts.append(annee)
            story.append(Paragraph("  –  ".join(parts), st["Body"]))

    # ══════════════════════════════════════════════════════════════════
    # CERTIFICATIONS
    # ══════════════════════════════════════════════════════════════════
    certifs = data.get("certifications") or []
    if certifs:
        story += _section("Certifications", st)
        story += _bullets(certifs, st)

    # ══════════════════════════════════════════════════════════════════
    # LANGUES
    # ══════════════════════════════════════════════════════════════════
    langues = data.get("langues") or []
    if langues:
        story += _section("Langues", st)
        for lang in langues:
            l_name = lang.get("langue") or ""
            l_niv = lang.get("niveau") or ""
            if l_name:
                text = f"<b>{l_name}</b>"
                if l_niv:
                    text += f" : {l_niv}"
                story.append(Paragraph(text, st["Body"]))

    # ══════════════════════════════════════════════════════════════════
    # CENTRES D'INTÉRÊT
    # ══════════════════════════════════════════════════════════════════
    centres = data.get("centres_interet") or []
    if centres:
        story += _section("Centres d'Intérêt", st)
        story.append(Paragraph("  |  ".join(c for c in centres if c), st["Tag"]))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.read()
