"""
Script 04 — Ingestion Streamlit App (Gemini Powered)
====================================================
V4.0 - Extraction Intelligente via Google Gemini 1.5 Flash
"""

import streamlit as st
import pandas as pd
import os
import requests
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import datetime

# Extractors
import pdfplumber
from docx import Document

# ─── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CERD Ingestion IA",
    page_icon="🤖",
    layout="wide"
)

# Load Environment
ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

# Airtable Config
AIRTABLE_TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

# ─── Helper Functions ─────────────────────────────────────────────────────────

def clean_text(text):
    """Normalize text."""
    if not text: return ""
    return re.sub(r'\s+', ' ', text).strip()

@st.cache_data(ttl=3600)
def load_themes_from_airtable():
    """Fetches Theme IDs, Codes and Names for context."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/Themes"
    themes = []
    params = {"fields[]": ["Code_Theme", "Nom_Theme"], "view": "Grid view"}
    
    try:
        offset = None
        while True:
            if offset: params["offset"] = offset
            resp = requests.get(url, headers=HEADERS, params=params)
            if resp.status_code != 200: break
            data = resp.json()
            for record in data.get('records', []):
                fields = record.get('fields', {})
                code = fields.get('Code_Theme')
                nom = fields.get('Nom_Theme')
                if code and nom:
                    themes.append({
                        "label": f"{code} - {nom}",
                        "id": record['id'],
                        "code": code,
                        "name": nom
                    })
            offset = data.get('offset')
            if not offset: break
        return themes
    except Exception as e:
        st.error(f"Erreur chargement thèmes: {e}")
        return []

def extract_text_from_file(uploaded_file):
    """Raw text extraction from PDF/Docx/Txt."""
    full_text = ""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract: full_text += extract + "\n"
        
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                full_text += para.text + "\n"
        
        elif uploaded_file.type == "text/plain":
            full_text = str(uploaded_file.read(), "utf-8")
            
    except Exception as e:
        return f"Error: {e}"
        
    return clean_text(full_text)

def gemini_extract(text, api_key, theme_context_str):
    """Uses Gemini 1.5 Flash to structured JSON extraction."""
    if not api_key:
        return {"Error": "Clé API manquante", "Titre": "Erreur", "Theme_Code_Suggested": ""}
    
    client = genai.Client(api_key=api_key)
    
    # Model Configuration
    generation_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        top_k=64,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )
    
    # Construct Promopt
    prompt = f"""
    You are an expert archivist. Analyze the following document text and extract metadata into JSON format.
    
    Fields required in JSON:
    - "Titre" (String): The main title of the document.
    - "Extrait" (String): A concise summary or abstract (approx 300-500 characters).
    - "Mots_Cles" (String): Comma-separated keywords relevant to the content.
    - "Source" (String): The organization, author, or publication source.
    - "Série" (String): Series name or Report number if applicable.
    - "Date_Publication" (String): Format YYYY-MM-DD. If fuzzy or year only, use YYYY-01-01.
    - "Contenu_Visuel" (String): Brief description of any tables, charts, or images mentioned in text (e.g., "Contains statistical tables on page 4").
    - "Theme_Code_Suggested" (String): Choose the MOST relevant 'Code_Theme' from the provided list. Return ONLY the code (e.g., "A.1").

    Context - Available Themes (Code - Name):
    {theme_context_str}

    Document Text (First 30k chars):
    {text[:30000]}
    """

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=generation_config,
        )
        return json.loads(response.text)
    except Exception as e:
        return {"Error": str(e), "Titre": "Erreur IA", "Theme_Code_Suggested": ""}

def push_to_airtable(data, theme_id):
    url = f"https://api.airtable.com/v0/{BASE_ID}/Articles"
    fields = {
        "Titre": data.get("Titre"),
        "Statut_Publication": "Brouillon",
        "Theme": [theme_id] if theme_id else []
    }
    
    # Optional fields mapping
    mapping = ["Extrait", "Mots_Cles", "Source", "Série", "Date_Publication", "Contenu_Texte", "Contenu_Visuel"]
    for k in mapping:
        val = data.get(k)
        if val: 
            # Slice safely for text fields
            fields[k] = str(val)[:100000] 
            
    return requests.post(url, headers=HEADERS, json={"fields": fields})

# ─── UI Layout ────────────────────────────────────────────────────────────────

st.sidebar.header("Configuration IA")
gemini_key = st.sidebar.text_input("Clé API Gemini", type="password", help="Générer sur aistudio.google.com")
st.sidebar.info("Modèle utilisé : **Gemini 1.5 Flash** (Rapide & Gratuit)\n\nClé requise pour l'analyse.")

st.title("🤖 CERD — Ingestion Assistée par IA")
st.markdown("Analyse sémantique complète : Titre, Résumé, Mots-clés, Dates et **Classification Automatique**.")

# Load Context
themes_list = load_themes_from_airtable()
themes_context_str = ""
if themes_list:
    themes_map = {t["label"]: t["id"] for t in themes_list}
    themes_code_map = {t["code"]: t["id"] for t in themes_list}
    # Limit context to avoid overflow if list is massive (though 1.5 Flash is 1M tokens)
    # We take top 500 or just all if small enough
    themes_context_str = "\n".join([f"{t['code']} - {t['name']}" for t in themes_list[:1000]])
else:
    st.warning("Aucun thème chargé depuis Airtable.")
    themes_code_map = {}

uploaded_files = st.file_uploader("Documents (PDF, DOCX)", accept_multiple_files=True)

if uploaded_files and gemini_key:
    if st.button("Lancer l'analyse IA ⚡", type="primary"):
        st.session_state["ia_results"] = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, f in enumerate(uploaded_files):
            status_text.text(f"Traitement : {f.name}")
            
            # 1. Extract Text
            raw_text = extract_text_from_file(f)
            
            # 2. Call Gemini
            extracted = gemini_extract(raw_text, gemini_key, themes_context_str)
            
            # 3. Add Raw Text for Airtable
            extracted["Contenu_Texte"] = raw_text
            extracted["Fichier_Source"] = f.name
            
            # 4. Resolve Theme ID from Suggestion
            suggested_code = extracted.get("Theme_Code_Suggested")
            theme_id = themes_code_map.get(suggested_code) # Map Code -> ID
            extracted["Theme_ID"] = theme_id
            
            # 5. Handle Date for DataFrame compatibility
            d = extracted.get("Date_Publication")
            # If d is valid string YYYY-MM-DD
            if d and re.match(r'^\d{4}-\d{2}-\d{2}$', str(d)):
                extracted["Date_Publication"] = pd.to_datetime(d).date()
            else:
                extracted["Date_Publication"] = None

            st.session_state["ia_results"].append(extracted)
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        status_text.text("Analyse terminée !")
        st.success("Extraction terminée !")

if "ia_results" in st.session_state and st.session_state["ia_results"]:
    st.subheader("Validation et Import")
    
    df = pd.DataFrame(st.session_state["ia_results"])
    
    # Configure Columns
    column_config = {
        "Fichier_Source": st.column_config.TextColumn("Fichier", disabled=True),
        "Titre": st.column_config.TextColumn("Titre", required=True),
        "Extrait": st.column_config.TextColumn("Résumé IA", width="medium"),
        "Theme_Code_Suggested": st.column_config.TextColumn("Thème Suggéré", disabled=True),
        "Theme_ID": st.column_config.TextColumn("ID Thème (Caché)", disabled=True),
        "Date_Publication": st.column_config.DateColumn("Date Pub.", format="Ys-MM-DD"),
        "Contenu_Visuel": st.column_config.TextColumn("Visuels"),
        "Contenu_Texte": st.column_config.TextColumn("Texte", disabled=True),
        "Error": st.column_config.TextColumn("Erreur API", disabled=True)
    }

    # Prepare Display DataFrame
    display_cols = ["Fichier_Source", "Titre", "Theme_Code_Suggested", "Date_Publication", "Extrait", "Mots_Cles", "Source", "Série", "Contenu_Visuel", "Contenu_Texte", "Theme_ID"]
    # Filter only columns present
    display_cols = [c for c in display_cols if c in df.columns]

    # Editor
    edited_df = st.data_editor(
        df[display_cols],
        column_config=column_config,
        width="stretch",
        num_rows="dynamic", 
        key="editor_ia"
    )

    if st.button("Confirmer l'import vers Airtable 🚀", type="primary"):
        success = 0
        errors = []
        
        records = edited_df.to_dict(orient="records")
        bar_import = st.progress(0)

        for i, row in enumerate(records):
            # Ensure Date is string for JSON
            date_val = row.get("Date_Publication")
            if isinstance(date_val, (pd.Timestamp, datetime.date, datetime.datetime)):
                row["Date_Publication"] = str(date_val)
            elif pd.isna(date_val):
                row["Date_Publication"] = None

            tid = row.get("Theme_ID")
            
            try:
                resp = push_to_airtable(row, tid)
                if resp.status_code == 200:
                    success += 1
                else:
                    errors.append(f"{row.get('Titre')} (Code {resp.status_code}): {resp.text}")
            except Exception as e:
                errors.append(f"Err: {e}")
            
            bar_import.progress((i+1)/len(records))
            
        if success:
            st.balloons()
            st.success(f"✅ {success} articles importés avec succès !")
        if errors:
            st.error(f"❌ {len(errors)} erreurs survenues.")
            st.expander("Détails des erreurs").write(errors)

elif uploaded_files and not gemini_key:
    st.warning("👈 Veuillez entrer une clé API Gemini dans la barre latérale pour activer l'analyse.")
