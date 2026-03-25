import streamlit as st
import pandas as pd
import json
import os
import re
import sys
import io
import importlib.util
from datetime import datetime
from dotenv import load_dotenv


# PAGE CONFIG
st.set_page_config(page_title='CERD - Import Intelligent', layout='wide')

# LOAD CONFIG
load_dotenv()
if not os.getenv('GEMINI_API_KEY'):
    load_dotenv(dotenv_path='config/.env')

# DYNAMIC IMPORT
module_name = 'article_ingestion_gemini'
file_path = os.path.join('scripts', '04_article_ingestion_gemini.py')

if os.path.exists(file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    # Aliases
    TextExtractor = module.TextExtractor
    GeminiProcessor = module.GeminiProcessor
    HuggingFaceProcessor = getattr(module, 'HuggingFaceProcessor', None)
    AutoProcessor = getattr(module, 'AutoProcessor', None)
    AirtableManager = module.AirtableManager
    ImageExtractor = module.ImageExtractor
    CloudinaryManager = module.CloudinaryManager
else:
    st.error('Script introuvable.')
    st.stop()

# UI HEADER
st.title('🚀 CERD - Assistant d\'Ingestion (Test Isolé Groq)')
st.caption('Centre d\'Études et Recherche Documentaire — Outil d\'Ingestion Documentaire')

# SIDEBAR CONFIG
with st.sidebar:
    st.header('⚙️ Configuration')
    mode = st.radio(
        "Mode de Saisie",
        ["Assistant IA 🤖 (Batch)", "Saisie Manuelle ✍️"],
        help="Batch : Uploadez plusieurs fichiers, l'IA les analyse automatiquement. Manuel : Remplissez vous-même les champs."
    )
    
    # Import Scope
    import_scope = st.radio(
        "Type d'Import",
        ["Complet (Méta + Fichiers + Texte)", "Métadonnées Uniquement"],
        help="Complet : stocke aussi le fichier PDF, les images et le texte intégral sur Cloudinary. Métadonnées : importe seulement Titre, Thème, Résumé, Mots-clés, Source et Date."
    )
    
    gemini_key = None # FORCER L'UTILISATION DE GROQ
    groq_key = os.getenv('GROQ_API_KEY')
    
    if "Assistant" in mode:
        if not gemini_key:
            gemini_key = st.text_input('Clé d\'accès Assistant', type='password',
                                       help='Veuillez insérer la clé d\'accès pour activer l\'analyse intelligente.')
    
    airtable_token = os.getenv('AIRTABLE_ACCESS_TOKEN')
    airtable_base = os.getenv('AIRTABLE_BASE_ID')

    if not airtable_token:
        st.error('Manque de configuration Airtable.')
        st.stop()
        
    st.divider()
    st.subheader("☁️ Hébergement (Cloudinary)")
    cloudinary_url = os.getenv('CLOUDINARY_URL')
    if not cloudinary_url:
        st.info("Ajoutez CLOUDINARY_URL dans .env pour activer l'hébergement.")
        c_name = st.text_input("Cloud Name")
        c_key = st.text_input("API Key")
        c_secret = st.text_input("API Secret", type="password")
    else:
        st.success("✅ Cloudinary Configuré")
        c_name, c_key, c_secret = None, None, None

    # ── GUIDE UTILISATEUR ────────────────────────────────────────────────
    st.divider()
    
    with st.expander("📖 Comment utiliser cet outil ?"):
        st.markdown("""
**Mode Assistant IA (recommandé)**
1. Choisissez *Assistant IA 🤖 (Batch)*
2. Uploadez vos fichiers PDF ou DOCX
3. Cliquez **Lancer l'analyse** — l'IA pré-remplit tous les champs
4. Vérifiez et corrigez si nécessaire
5. Cliquez **Valider et Importer** pour envoyer vers Airtable

**Mode Saisie Manuelle**
1. Choisissez *Saisie Manuelle ✍️*
2. Remplissez les champs vous-même
3. Cliquez **Créer l'article 💾**

> 💡 L'IA gère automatiquement les délais réseau. Laissez l'opération se terminer sans fermer la page.
        """)

    with st.expander("🏷️ Légende des Séries (c1 → c4)"):
        st.markdown("""
| Série | Signification |
|---|---|
| **c1** | 📄 Général |
| **c2** | 🏢 Entreprise |
| **c3** | 💰 Combien ça coûte |
| **c4** | 📋 Documentation professionnelle |

> La série est pré-remplie automatiquement par l'IA. Vérifiez qu'elle correspond au contenu du document.
        """)

    with st.expander("🗂️ Parcourir les Thèmes"):
        try:
            if os.path.exists('config/parsed_data.json'):
                with open('config/parsed_data.json', 'r', encoding='utf-8') as _f:
                    _hier = json.load(_f)
                for _dom in _hier.get('domaines', []):
                    st.markdown(f"**{_dom['code']} — {_dom['nom']}**")
                    _dom_themes = [
                        t for t in _hier.get('themes', [])
                        if str(t.get('parent_ref', '')).startswith(_dom['code'])
                        or str(t.get('code', '')).startswith(_dom['code'])
                    ]
                    for _t in _dom_themes[:8]:  # Limit to avoid overflow
                        st.markdown(f"&nbsp;&nbsp;&nbsp;`{_t['code']}` {_t['nom']}")
                    if len(_dom_themes) > 8:
                        st.caption(f"  ... et {len(_dom_themes)-8} autres thèmes")
        except Exception:
            st.info("Chargement des thèmes indisponible.")

# INITIALIZE UTILS
@st.cache_data
def get_theme_options():
    try:
        if os.path.exists('config/parsed_data.json'):
            with open('config/parsed_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'themes' in data:
                    return [f"{t['code']} - {t['nom']}" for t in data['themes']]
    except Exception as e:
        pass
    return []

@st.cache_resource
def get_processor(g_key, gr_key, mode_choice):
    if AutoProcessor:
        return AutoProcessor(g_key, gr_key, mode_choice, 'config/parsed_data.json')
    return None

at_manager = AirtableManager(airtable_token, airtable_base)

# STATE MANAGEMENT
if 'batch_queue' not in st.session_state:
    st.session_state.batch_queue = [] # List of dicts {file, text, data, images, status}
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

theme_options = get_theme_options()

if 'manual_data' not in st.session_state:
    st.session_state.manual_data = {}
if 'manual_images' not in st.session_state:
    st.session_state.manual_images = []

# LOGIC
if mode == "Assistant IA 🤖 (Batch)":
    uploaded_files = st.file_uploader('Documents à analyser (PDF, DOCX)', type=['pdf', 'docx'], accept_multiple_files=True)

    # PROCESS BUTTON
    if uploaded_files and len(uploaded_files) > 0:
        if st.button(f'Lancer l\'analyse de {len(uploaded_files)} fichiers 🧠', type='primary'):
            if not gemini_key and not groq_key:
                st.error("Au moins une clé API (Gemini ou Groq) est requise.")
            else:
                progress_text = "Opération en cours..."
                my_bar = st.progress(0, text=progress_text)
                
                new_queue = []
                processor = get_processor(gemini_key, groq_key, "Auto (Gemini → Groq)")
                
                for i, uploaded_file in enumerate(uploaded_files):
                    # Progress Update
                    progress_percent = int(((i) / len(uploaded_files)) * 100)
                    my_bar.progress(progress_percent, text=f"Analyse {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
                    
                    try:
                        # 1. Extract Text
                        text = TextExtractor.extract(uploaded_file, uploaded_file.name)
                        if not text:
                            raise ValueError("Impossible d'extraire le texte.")
                            
                        # 1.b Introduce minimal delay between API calls to avoid 429 bursts if looping quickly
                        if i > 0:
                             import time
                             time.sleep(2)
                             
                        # 2. Extract Images (Only if Scope is Complet)
                        images = []
                        if "Complet" in import_scope:
                             images = ImageExtractor.extract_images(uploaded_file, uploaded_file.name)
                        
                        # 3. Analyze with AI (AutoProcessor handles fallback)
                        data = processor.analyze_document(text)
                        
                        # Read bytes safely before the file gets closed
                        file_bytes = uploaded_file.getvalue() if "Complet" in import_scope else None
                        
                        entry = {
                            'filename': uploaded_file.name,
                            'file_bytes': file_bytes, # Store robust bytes
                            'text': text,
                            'data': data,
                            'images': images,
                            'status': 'Pending',
                            'error_msg': None
                        }
                        new_queue.append(entry)
                        
                    except Exception as e:
                        new_queue.append({
                            'filename': uploaded_file.name,
                            'status': 'Error',
                            'error_msg': str(e),
                            'data': {},
                            'text': '',
                            'images': []
                        })
                
                my_bar.progress(100, text="Analyse Terminée !")
                st.session_state.batch_queue = new_queue
                st.session_state.current_idx = 0
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()

    # REVIEW INTERFACE
    if st.session_state.batch_queue:
        queue = st.session_state.batch_queue
        total = len(queue)
        current = st.session_state.current_idx
        
        # Navigation
        col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])
        with col_nav1:
            if st.button("⬅️ Précédent", disabled=(current == 0)):
                st.session_state.current_idx -= 1
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
        with col_nav3:
            if st.button("Suivant ➡️", disabled=(current == total - 1)):
                st.session_state.current_idx += 1
                st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
        with col_nav2:
             st.markdown(f"<h3 style='text-align: center'>Document {current + 1} / {total} : {queue[current]['filename']}</h3>", unsafe_allow_html=True)
        
        entry = queue[current]
        data = entry['data']
        
        if entry['status'] == 'Error':
            st.error(f"Erreur lors de l'analyse : {entry['error_msg']}")
        elif entry['status'] == 'Imported':
             st.success("✅ Document déjà importé dans Airtable.")
        else:
            # FORM
            st.divider()
            with st.form(f'validation_form_{current}'):
                col1, col2 = st.columns(2)
                
                with col1:
                    titre = st.text_input(
                        'Titre',
                        value=data.get('Titre', ''),
                        help="Titre principal du document tel qu'il apparaît en première page."
                    )
                    
                    # Force valid series from Airtable config (lowercase c1, c2, c3, c4)
                    extracted_serie = str(data.get('Série', 'c1')).lower().strip()
                    allowed_series = ['c1', 'c2', 'c3', 'c4']
                    series_labels = {
                        'c1': 'c1 — Général',
                        'c2': 'c2 — Entreprise',
                        'c3': 'c3 — Combien ça coûte',
                        'c4': 'c4 — Documentation professionnelle'
                    }
                    default_idx = 0
                    if extracted_serie in allowed_series:
                        default_idx = allowed_series.index(extracted_serie)
                    
                    serie_label = st.selectbox(
                        'Série',
                        options=list(series_labels.values()),
                        index=default_idx,
                        help="Classification du document. c1=Général, c2=Entreprise, c3=Coûts, c4=Documentation pro."
                    )
                    serie = serie_label.split(' — ')[0]  # Extract 'c1', 'c2', etc.
                    theme_code = st.text_input(
                        'Code Thème',
                        value=data.get('Code_Theme_Ref', ''),
                        help="Code thématique (ex: 10.1, 32.2). Consultez la liste 🗂️ dans la barre latérale."
                    )
                    
                with col2:
                    date_pub = st.text_input(
                        'Date Publication',
                        value=data.get('Date_Publication', ''),
                        help="Format AAAA-MM-JJ. Si seule l'année est connue, utilisez AAAA-01-01."
                    )
                    source = st.text_input(
                        'Source',
                        value=data.get('Source', ''),
                        help="Organisme ou auteur éditeur (ex: HCP, BAM, Ministère de l'Économie...)."
                    )
                    mots_cles = st.text_area(
                        'Mots Clés',
                        value=str(data.get('Mots_Cles', '')),
                        help="Mots-clés extraits du document, séparés par des virgules. L'IA les copie exactement depuis le document."
                    )

                extrait = st.text_area('Extrait', value=data.get('Extrait', ''), height=100)
                
                # Content
                content_val = data.get('Contenu_Principal', entry['text'])
                if not content_val or len(content_val) < 50:
                     content_val = entry['text']
                st.markdown('**Contenu Reformulé**')
                with st.expander("Voir/Modifier le Contenu", expanded=False):
                    contenu_texte = st.text_area('Contenu', value=content_val, height=300)

                # Images Selection
                selected_images = []
                if entry['images']:
                    st.write(f"**Images ({len(entry['images'])})** - Cochez pour importer")
                    cols = st.columns(4)
                    for idx, (img_name, img_bytes) in enumerate(entry['images']):
                        with cols[idx % 4]:
                            st.image(img_bytes, width=150)
                            if st.checkbox(f"Importer {img_name}", value=True, key=f"img_{current}_{idx}"):
                                selected_images.append((img_name, img_bytes))

                # Submit
                button_label = 'Valider et Importer (Métadonnées)' if "Métadonnées" in import_scope else 'Valider et Importer Complet ☁️'
                submitted = st.form_submit_button(button_label, type='primary')

                if submitted:
                    with st.spinner('Traitement en cours...'):
                        try:
                            # 1. Setup Variables
                            doc_url = None
                            img_urls = []
                            final_content = ""
                            c_mgr = CloudinaryManager(c_name, c_key, c_secret) if "Complet" in import_scope else None

                            if "Complet" in import_scope:
                                # 2. Upload Document
                                if entry.get('file_bytes'):
                                    file_stream = io.BytesIO(entry['file_bytes'])
                                    file_stream.name = entry['filename']
                                    rtype = 'raw' if entry['filename'].lower().endswith(('.pdf','.docx','.zip')) else 'auto'
                                    doc_url = c_mgr.upload_file(file_stream, entry['filename'], resource_type=rtype)
                                    if doc_url:
                                        st.info(f"📎 Fichier source uploadé : {doc_url[:80]}...")
                                    else:
                                        st.error("⚠️ Échec upload document source sur Cloudinary")
                                
                                # 3. Upload Images
                                for i_name, i_bytes in selected_images:
                                    i_io = io.BytesIO(i_bytes)
                                    url = c_mgr.upload_file(i_io, i_name, resource_type="image")
                                    if url:
                                        img_urls.append({"url": url, "filename": i_name}) # Airtable format
                                
                                final_content = contenu_texte
                            
                            # 4. Prepare Payload
                            theme_rec_id = at_manager.get_theme_record_id(theme_code)
                            theme_link = [theme_rec_id] if theme_rec_id else []
                            
                            new_index, id_article_str = at_manager.get_next_index(serie if serie else "c1", theme_code)
                            
                            doc_attachment = []
                            if doc_url:
                                doc_attachment.append({"url": doc_url, "filename": entry['filename']})
                            
                            payload = {
                                'Titre': titre,
                                'Série': serie,
                                'Code_Theme_Ref': theme_code,
                                'Theme': theme_link, 
                                'Index': new_index,
                                'Extrait': extrait,
                                'Mots_Cles': mots_cles,
                                'Source': source,
                                'Date_Publication': date_pub if date_pub else None,
                                'Contenu_Texte': final_content,
                                'Fichier': doc_attachment,
                                'Contenu_Visuel': img_urls
                            }
                            
                            # 5. Create
                            at_manager.create_article(payload)
                            
                            st.success(f"✅ Article '{titre}' importé avec succès !")
                            st.session_state.batch_queue[current]['status'] = 'Imported'
                            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()
                            
                        except Exception as e:
                            st.error(f"Erreur Import: {e}")


if mode == "Saisie Manuelle ✍️":
    # 0. Check for Success Message from previous run
    if 'success_msg' in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg
        
    st.header('Saisie Manuelle de Nouvel Article')
    
    # 1. OPTIONAL: DOCUMENT LOADING (Extraire Images only)
    uploaded_manual_file = None
    
    if "Complet" in import_scope:
        with st.expander("📂 Charger le Document Source & Extraire Visuels (Optionnel)", expanded=True):
            uploaded_manual_file = st.file_uploader("Fichier pour extraction d'images & Archivage", type=['pdf', 'docx'], key='manual_upload')
            
            if uploaded_manual_file is not None:
                if st.button("🖼️ Extraire les Visuels", type="secondary"):
                    with st.spinner("Extraction en cours..."):
                        try:
                            # Extract Images ONLY (Text is manually entered)
                            # Uses generic extract_images which supports PDF & DOCX
                            images = ImageExtractor.extract_images(uploaded_manual_file, uploaded_manual_file.name)
                            
                            # Update Session State
                            st.session_state.manual_data = {} # Reset data
                            # Ensure no text is pre-filled
                            if 'Contenu_Texte' in st.session_state.manual_data:
                                del st.session_state.manual_data['Contenu_Texte']
                            
                            st.session_state.manual_images = images
                            
                            nb = len(images)
                            st.success(f"{nb} image(s) extraite(s) ! Cochez celles à conserver ci-dessous.")
                        except Exception as e:
                            st.error(f"Erreur d'extraction : {e}")

    # 2. FORM
    with st.form("manual_entry_form", clear_on_submit=True):
        # Manual Mode: No auto-fill from AI
        # Note: clear_on_submit=True resets the form fields after successful submit (and rerun)
        
        col1, col2 = st.columns(2)
        
        with col1:
            titre = st.text_input(
                'Titre *',
                help="Titre principal du document. Champ obligatoire."
            )
            
            series_labels_manual = [
                'c1 — Général',
                'c2 — Entreprise',
                'c3 — Combien ça coûte',
                'c4 — Documentation professionnelle'
            ]
            serie_label_manual = st.selectbox(
                'Série',
                options=series_labels_manual,
                index=0,
                help="Classification du document. c1=Général, c2=Entreprise, c3=Coûts, c4=Documentation pro."
            )
            serie = serie_label_manual.split(' — ')[0]
            
            # Theme with Search
            theme_selection = st.selectbox(
                'Thème (Rechercher par Code ou Nom)',
                options=theme_options,
                index=None,
                placeholder="Choisir un thème...",
                help="Tapez un code (ex: 32.2) ou un mot-clé pour filtrer. Consultez 🗂️ dans la barre latérale."
            )
            theme_code = theme_selection.split(' - ')[0].strip() if theme_selection else ""
            
        with col2:
            date_pub = st.text_input(
                'Date Publication (AAAA-MM-JJ)',
                help="Format AAAA-MM-JJ. Si seule l'année est connue, utilisez AAAA-01-01."
            )
            source = st.text_input(
                'Source',
                help="Organisme ou auteur éditeur (ex: HCP, BAM, Ministère...)."
            )
            mots_cles = st.text_area(
                'Mots Clés',
                help="Mots-clés pertinents séparés par des virgules."
            )

        extrait = st.text_area('Extrait', height=100)
        
        # Extended fields
        final_content = ""
        manual_img_file = None
        selected_extracted_indices = []
        
        if "Complet" in import_scope:
            st.divider()
            st.subheader("Contenu Complet & Images")
            
            # Text Content (Raw text available if doc loaded)
            # Use distinct key or default empty since clear_on_submit is True
            final_content = st.text_area('Contenu Intégral', height=300)
            
            # MULTI-IMAGE SELECTION (Extracted)
            st.write("---")
            st.write("📸 **Gestion des Images**")

            # A. Extracted Images Section
            if st.session_state.manual_images:
                st.markdown(f"**Images Extraites ({len(st.session_state.manual_images)})** - Sélectionnez celles à importer :")
                cols_img = st.columns(4)
                for idx, (img_name, img_bytes) in enumerate(st.session_state.manual_images):
                    with cols_img[idx % 4]:
                        st.image(img_bytes, width=150)
                        # Ensure unique key for checkbox
                        if st.checkbox(f"Importer {idx+1}", value=False, key=f"extract_img_{idx}"):
                             selected_extracted_indices.append(idx)
            
            # B. Manual Upload Section
            st.markdown("**Ajouter une image supplémentaire :**")
            manual_img_file = st.file_uploader("Image Illustrative (JPG/PNG)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
        
        submitted = st.form_submit_button('Créer l\'article 💾', type='primary')
        
        if submitted:
            if not titre:
                st.error("Le Titre est obligatoire.")
            else:
                with st.spinner('Enregistrement sur Airtable...'):
                    try:
                        # 1. Cloudinary Uploads
                        doc_url = None
                        img_urls = []
                        target_file = None
                        c_mgr = CloudinaryManager(c_name, c_key, c_secret) if "Complet" in import_scope else None

                        if "Complet" in import_scope:
                            # Explicitly check session state first for stability inside submit callback
                            target_file = None
                            if 'manual_upload' in st.session_state and st.session_state.manual_upload:
                                target_file = st.session_state.manual_upload
                            elif uploaded_manual_file: # Fallback to local var
                                target_file = uploaded_manual_file

                            if target_file is not None:
                                try:
                                    # Create pure BytesIO copy to avoid closed file issues
                                    file_bytes = target_file.getvalue()
                                    file_stream = io.BytesIO(file_bytes)
                                    file_stream.name = target_file.name
                                    
                                    # Use 'raw' strictly for docs, CloudinaryManager handles extension but explicit is safer
                                    rtype = 'raw' if target_file.name.lower().endswith(('.pdf','.docx','.zip')) else 'auto'
                                    
                                    # st.info(f"DEBUG: Taille du fichier = {len(file_bytes)} bytes")
                                    
                                    doc_url = c_mgr.upload_file(file_stream, target_file.name, resource_type=rtype)
                                    
                                    if doc_url:
                                        st.info(f"📎 Fichier source uploadé : {doc_url[:80]}...")
                                    else:
                                        st.error("⚠️ Échec upload document sur Cloudinary (URL vide)")
                                        
                                except Exception as upload_err:
                                    st.error(f"Erreur upload fichier: {upload_err}")
                            else:
                                st.warning("⚠️ Aucun fichier source détecté pour l'upload.")
                            
                            # Process Extracted Images (Selected)
                            if selected_extracted_indices and st.session_state.manual_images:
                                for idx in selected_extracted_indices:
                                    i_name, i_bytes = st.session_state.manual_images[idx]
                                    i_io = io.BytesIO(i_bytes)
                                    url = c_mgr.upload_file(i_io, i_name, resource_type="image")
                                    if url:
                                        img_urls.append({"url": url, "filename": i_name})
                                        
                            # Process Manual Image
                            if manual_img_file:
                                i_bytes = manual_img_file.getvalue()
                                i_io = io.BytesIO(i_bytes)
                                url = c_mgr.upload_file(i_io, manual_img_file.name, resource_type="image")
                                if url:
                                    img_urls.append({"url": url, "filename": manual_img_file.name})

                        # 2. Airtable Logic
                        theme_rec_id = at_manager.get_theme_record_id(theme_code)
                        theme_link = [theme_rec_id] if theme_rec_id else []
                        
                        final_serie = serie if serie else "c1"
                        new_index, id_article_str = at_manager.get_next_index(final_serie, theme_code)
                        
                        doc_attachment = []
                        if doc_url and target_file:
                             doc_attachment.append({"url": doc_url, "filename": target_file.name})
                        elif doc_url:
                             doc_attachment.append({"url": doc_url})
                        
                        # 2. Airtable Logic
                        theme_rec_id = at_manager.get_theme_record_id(theme_code)
                        theme_link = [theme_rec_id] if theme_rec_id else []
                        
                        final_serie = serie if serie else "c1"
                        new_index, id_article_str = at_manager.get_next_index(final_serie, theme_code)
                        
                        doc_attachment = []
                        if doc_url and target_file:
                             doc_attachment.append({"url": doc_url, "filename": target_file.name})
                        elif doc_url:
                             doc_attachment.append({"url": doc_url})
                        
                        payload = {
                            'Titre': titre,
                            'Série': final_serie,
                            'Code_Theme_Ref': theme_code,
                            'Theme': theme_link, 
                            'Index': new_index,
                            'Extrait': extrait,
                            'Mots_Cles': mots_cles,
                            'Source': source,
                            'Date_Publication': date_pub if date_pub else None,
                            'Contenu_Texte': final_content,
                            'Fichier': doc_attachment,
                            'Contenu_Visuel': img_urls
                        }
                        
                        at_manager.create_article(payload)
                        
                        # Set Success Message in Session State for persistence after rerun
                        st.session_state.success_msg = f"✅ Article '{titre}' créé avec succès ! (Code: {id_article_str})"
                        
                        # Reset Data
                        st.session_state.manual_data = {}
                        st.session_state.manual_images = []
                        
                        # Rerun to clear form and show success message
                        if hasattr(st, 'rerun'): st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la création : {e}")
