"""
app.py - NXSTEP ATS CV Generator
Flask web application that:
 1. Accepts an uploaded CV (PDF or DOCX)
 2. Extracts text with cv_parser
 3. Sends text to GPT-4o via openai_client
 4. Generates both an ATS PDF and an ATS DOCX
 5. Returns a ZIP archive containing both files for download
"""
import os
import uuid
import zipfile
import io
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from cv_parser import extract_text_from_file
from openai_client import extract_cv_data
from cv_generator import generate_cv_pdf
from docx_generator import generate_cv_docx

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nxstep-cv-secret-2024")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """
    POST /generate
    Form fields:
      - file: uploaded CV (PDF or DOCX)
      - api_key: OpenAI API key
    Returns: ZIP file containing CV_ATS_<Nom>.pdf + CV_ATS_<Nom>.docx
    """
    api_key = request.form.get("api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return jsonify({"error": "Clé API OpenAI manquante."}), 400

    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier fourni."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Aucun fichier sélectionné."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format non supporté. Utilisez PDF ou DOCX."}), 400

    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Step 1: Extract text
        raw_text = extract_text_from_file(filepath)
        if not raw_text.strip():
            return jsonify({"error": "Impossible d'extraire du texte du fichier fourni."}), 400

        # Step 2: GPT-4o → structured JSON
        cv_data = extract_cv_data(raw_text, api_key)

        # Step 3: Generate both formats
        pdf_bytes  = generate_cv_pdf(cv_data)
        docx_bytes = generate_cv_docx(cv_data)

        os.remove(filepath)

        nom       = cv_data.get("nom_complet", "CV").replace(" ", "_")
        pdf_name  = f"CV_ATS_{nom}.pdf"
        docx_name = f"CV_ATS_{nom}.docx"
        zip_name  = f"CV_ATS_{nom}.zip"

        # Step 4: Pack into ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(pdf_name,  pdf_bytes)
            zf.writestr(docx_name, docx_bytes)
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name=zip_name,
        )

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


@app.route("/preview", methods=["POST"])
def preview():
    """POST /preview — returns the extracted JSON for debugging."""
    api_key = request.form.get("api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return jsonify({"error": "Clé API OpenAI manquante."}), 400

    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier fourni."}), 400

    file = request.files["file"]
    if not allowed_file(file.filename):
        return jsonify({"error": "Format non supporté. Utilisez PDF ou DOCX."}), 400

    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        raw_text = extract_text_from_file(filepath)
        cv_data  = extract_cv_data(raw_text, api_key)
        os.remove(filepath)
        return jsonify(cv_data)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"\n🚀 NXSTEP ATS CV Generator running at http://localhost:{port}\n")
    app.run(debug=True, port=port)
