import os
import json
import io
import re
import fitz  # PyMuPDF
from docx import Document
from google import genai
import pandas as pd
from pyairtable import Api, Table
from pyairtable.formulas import match, AND
from dotenv import load_dotenv
import zipfile
import cloudinary
import cloudinary.uploader
import time
import requests
import time

# Load params
load_dotenv(dotenv_path='config/.env')

class TextExtractor:
    @staticmethod
    def extract_docx(file_obj):
        '''Extracts text, table content, and floating text (textboxes) from DOCX using direct XML parsing.'''
        try:
            doc = Document(file_obj)
            text_parts = []
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            def get_para_text(p_element):
                '''Extracts text from a paragraph element considering runs.'''
                return ''.join([node.text for node in p_element.findall('.//w:t', ns) if node.text])

            # 1. Main Body Iteration (Paragraphs and Tables in order)
            for element in doc.element.body:
                if element.tag.endswith('}p'):
                    text = get_para_text(element)
                    if text.strip():
                        text_parts.append(text.strip())     
                elif element.tag.endswith('}tbl'):
                    table_rows = []
                    for tr in element.findall('.//w:tr', ns):
                        row_cells = []
                        for tc in tr.findall('.//w:tc', ns):
                            cell_text_parts = []
                            for p in tc.findall('.//w:p', ns):
                                pt = get_para_text(p)
                                if pt.strip():
                                    cell_text_parts.append(pt.strip())
                            full_cell_text = ' '.join(cell_text_parts)
                            if full_cell_text:
                                row_cells.append(full_cell_text)
                        if row_cells:
                            table_rows.append(' | '.join(row_cells))
                    if table_rows:
                        text_parts.append(f"\n[Tableau]\n" + "\n".join(table_rows) + "\n")

            # 2. Text Boxes / Floating Content
            for txbx in doc.element.body.findall('.//w:txbxContent', ns):
                txbx_texts = []
                for p in txbx.findall('.//w:p', ns):
                    pt = get_para_text(p)
                    if pt.strip():
                        txbx_texts.append(pt.strip())
                if txbx_texts:
                    text_parts.append(f"\n[Encadré/ZoneText]\n" + "\n".join(txbx_texts))

            # 3. Footers
            for section in doc.sections:
                if section.footer:
                    for p in section.footer.paragraphs:
                        if p.text.strip():
                            text_parts.append(f"[Pied_de_page] {p.text.strip()}")
            
            return '\n'.join(text_parts)
        except Exception as e:
            return f'[Erreur lecture DOCX: {e}]'

    @staticmethod
    def extract(file_obj, filename):
        '''Extracts text from PDF or DOCX file object.'''
        text = ''
        try:
            file_obj.seek(0)
            if filename.lower().endswith('.pdf'):
                with fitz.open(stream=file_obj.read(), filetype='pdf') as doc:
                    for page in doc:
                        text += page.get_text() + '\n'
            elif filename.lower().endswith('.docx'):
                text = TextExtractor.extract_docx(file_obj)
            else:
                return None
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            return f'Error extracting {filename}: {str(e)}'

class GeminiProcessor:
    def __init__(self, api_key, hierarchy_path='config/parsed_data.json'):
        self.api_key = api_key
        # Initialize Client
        self.client = genai.Client(api_key=self.api_key)
        self.valid_codes = self._load_valid_codes(hierarchy_path)

    def _load_valid_codes(self, hierarchy_path):
        codes = {}
        if os.path.exists(hierarchy_path):
            with open(hierarchy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'themes' in data:
                    for t in data['themes']:
                        codes[t['code']] = t['nom']
        return codes

    def analyze_document(self, text):
        '''Sends text to Gemini for classification.'''
        context_str = '\n'.join([f'- {k}: {v}' for k, v in self.valid_codes.items()])
        
        # Optimization: Limit context to ~75k tokens (approx 300k chars) to save quota
        # gemini-1.5-flash is the most generous model for free tier (15 RPM, 1M TPM)
        truncated_text = text[:300000]
        
        prompt = f'''
        Tu es un expert archiviste pour le Centre d'Études (CERD). Analyse le document et extrais les métadonnées JSON.

        Champs requis :
        1. "Titre" (String): Titre explicite de l'article.
        2. "Extrait" (String): Si le document contient une mention explicite 'EXTRAIT :' ou 'RÉSUMÉ :', copie EXACTEMENT le texte associé. Sinon, copie exactement les 2-3 premières phrases du texte. INTERDICTION DE REFORMULER OU D'INVENTER.
        3. "Mots_Cles" (String): Uniquement la liste des mots-clés. Si 'MOTS CLES :' est mentionné, copie STRICTEMENT les mots sur la même ligne et ARRÊTE-TOI. NE JAMAIS inclure de texte supplémentaire, ni le titre, ni des phrases de l'extrait. Formate-les avec des virgules.
        4. "Source" (String): Entité productrice ou mention 'Source :' en bas de page.
        5. "Date_Publication" (String): Format YYYY-MM-DD.
        6. "Code_Theme_Ref" (String): Trouve le nom du thème (souvent après 'THEME :') ou analyse le sujet, et cherche ce NOM dans la "Liste des Codes Thématiques" fournie. Renvoie UNIQUEMENT le code de notre base de données (ex: 90.1) tiré de cette liste. NE REPRENDS JAMAIS les chiffres écrits dans l'article pour le thème (ils sont souvent faux). Seule notre liste fait foi.
        7. "Série" (String): Classification "c1", "c2", "c3", "c4" (minuscule). Extrait-la si mentionnée (ex: 'ARTICLE: c3').
        8. "Contenu_Principal" (String): Le TEXTE INTÉGRAL de l'article.
           IMPORTANT : 
           - GARDE LES SAUTS DE LIGNE ET LES PARAGRAPHES (utilise \\n\\n pour séparer les paragraphes).
           - COPIER-COLLER EXACT DU TEXTE D'ORIGINE en gardant toutes les phrases de l'article intactes, du début à la fin.
           - NE SUPPRIME PAS le début de l'article même s'il correspond au titre ou à l'extrait. L'article doit être complet.
           - Supprime uniquement le BLOC D'EN-TÊTE formel contenant les métadonnées (le tableau avec THEME:, TITRE:, EXTRAIT:, DATE:, etc.) s'il y en a un. Le reste en dessous est le contenu.
           - INTERDICTION TOTALE DE REFORMULER, DE RÉSUMER OU D'INVENTER UN SEUL MOT.


        EXEMPLE DE RÉPONSE JSON ATTENDUE :
        {{
          "Titre": "Rapport sur la Politique Monétaire",
          "Extrait": "Ce rapport analyse l'inflation globale pour l'année courante.",
          "Mots_Cles": "inflation, politique monétaire, finances",
          "Source": "Ministère de l'Économie",
          "Date_Publication": "2023-12-19",
          "Code_Theme_Ref": "10.1",
          "Série": "c1",
          "Contenu_Principal": "L'évolution récente de l'inflation montre que..."
        }}

        Liste des Codes Thématiques :
        {context_str}

        Texte Complet :
        {truncated_text}
        '''
        
        max_retries = 3
        retry_delay = 2  # seconds

        for attempt in range(max_retries):
            try:
                # Using 'gemini-flash-lite-latest' (Gemini 1.5 Flash Lite)
                # Known for being the most cost-effective and generous with quotas
                response = self.client.models.generate_content(
                    model='gemini-flash-lite-latest',
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                parsed = json.loads(response.text)
                if isinstance(parsed, list):
                    return parsed[0] if parsed else {}
                return parsed
            except Exception as e:
                # Check for quota error (429)
                error_str = str(e)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                return {'error': error_str}
        return {'error': 'Max retries exceeded'}

class ImageExtractor:
    @staticmethod
    def extract_images(file_obj, filename):
        '''Extracts images from PDF or DOCX file object as (name, bytes) tuples.'''
        images = []
        try:
            file_obj.seek(0) # Reset pointer
            if filename.lower().endswith('.pdf'):
                with fitz.open(stream=file_obj.read(), filetype='pdf') as doc:
                    for i, page in enumerate(doc):
                        img_list = page.get_images(full=True)
                        for img_index, img in enumerate(img_list):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            images.append((f'page{i+1}_img{img_index}.{base_image["ext"]}', base_image['image']))    
            elif filename.lower().endswith('.docx'):
                import zipfile
                with zipfile.ZipFile(file_obj) as z:
                    for name in z.namelist():
                        if name.startswith('word/media/'):
                            images.append((os.path.basename(name), z.read(name)))
        except Exception as e:
            print(f'Image extraction error: {e}')
        
        file_obj.seek(0)
        return images

    @staticmethod
    def extract_images_from_docx(file_obj):
        '''Extracts images from DOCX file object as (name, bytes) tuples.'''
        images = []
        try:
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            with zipfile.ZipFile(file_obj) as z:
                for name in z.namelist():
                    if name.startswith('word/media/') and not name.endswith('/'):
                         images.append((os.path.basename(name), z.read(name)))
        except Exception as e:
            print(f'DOCX Image extraction error: {e}')
        return images

class CloudinaryManager:
    def __init__(self, cloud_name=None, api_key=None, api_secret=None):
        # Auto-configure if env vars exist, else use passed params
        # Format for env var: CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        try:
            if cloud_name and api_key and api_secret:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
            else:
                # Explicitly configure from CLOUDINARY_URL env var
                import streamlit as st
                c_url = (os.environ.get('CLOUDINARY_URL') or st.secrets.get('CLOUDINARY_URL', '')).strip()
                if c_url:
                    cloudinary.config(cloudinary_url=c_url)
                    print(f"[Cloudinary] Configuré via CLOUDINARY_URL env var")
                else:
                    print("[Cloudinary] ATTENTION: Aucune configuration trouvée !")
        except Exception as e:
            print(f"[Cloudinary] Erreur config: {e}")

    def upload_file(self, file_content, filename, resource_type="auto"):
        '''Uploads bytes or file-like object to Cloudinary. Returns URL.'''
        try:
            # If it's a file object, ensure we are at start
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
            
            # Determine resource_type based on file extension
            if filename.lower().endswith(('.pdf', '.docx', '.doc', '.zip')):
                resource_type = 'raw'
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                resource_type = 'image'
                
            # Use original filename as base
            base_name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            
            # Normalize ID (remove spaces/accents)
            safe_name = re.sub(r'[^\w\-]', '_', base_name)
            
            # For RAW files, Cloudinary REQUIRES the extension in the public_id
            if resource_type == 'raw':
                public_id_str = f"{safe_name}_{timestamp}{ext}"
            else:
                public_id_str = f"{safe_name}_{timestamp}"
            
            # Use standard upload for all file types
            # (upload_large is only needed for files > 100 MB and can fail
            #  silently with BytesIO objects for normal-sized documents)
            print(f"[Cloudinary] Upload '{filename}' (type={resource_type}, id={public_id_str})...")
            
            response = cloudinary.uploader.upload(
                file_content, 
                resource_type=resource_type,
                public_id=public_id_str, 
                folder="cerd_imports"
            )
            
            url = response.get('secure_url')
            print(f"[Cloudinary] ✅ Upload OK → {url}")
            return url
            
        except Exception as e:
            print(f"[Cloudinary] ❌ Upload Error pour '{filename}': {e}")
            raise Exception(f"Cloudinary Upload Error: {str(e)}")

class AirtableManager:
    def __init__(self, api_token, base_id):
        self.api = Api(api_token)
        self.table = self.api.table(base_id, 'Articles')
        # Updated to match tables_config.json: Table is 'Themes'
        self.theme_table = self.api.table(base_id, 'Themes')

    def check_duplicate_title(self, title):
        matches = self.table.all(formula=match({'Titre': title}), max_records=1)
        return len(matches) > 0

    def get_next_index(self, serie, theme_code):
        formula = f"AND({{Code_Theme_Ref}}='{theme_code}', {{Série}}='{serie}')"
        records = self.table.all(formula=formula, fields=['Index'], sort=['-Index'])
        
        if not records:
            return 1, f'{serie}-{theme_code}-001'
        
        last_index = records[0]['fields'].get('Index', 0)
        new_index = last_index + 1
        return new_index, f'{serie}-{theme_code}-{new_index:03d}'

    def get_theme_record_id(self, code):
        # Updated to match tables_config.json: Field is 'Code_Theme'
        records = self.theme_table.all(formula=match({'Code_Theme': code}), max_records=1)
        if records:
            return records[0]['id']
        return None

    def create_article(self, data):
        return self.table.create(data)



