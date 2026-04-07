import streamlit as st
import pandas as pd
import json
import os
import re
import sys
import io
import subprocess
import importlib.util
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
    AirtableManager = module.AirtableManager
    ImageExtractor = module.ImageExtractor
    CloudinaryManager = module.CloudinaryManager
    SourceMatcher = module.SourceMatcher
    sanitize_star_values = getattr(module, 'sanitize_star_values', None)
else:
    st.error('Script introuvable.')
    st.stop()

# UI HEADER
st.title('📚 CERD - Assistant d\'Ingestion')
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

    gemini_key = os.environ.get('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY')
    
    if "Assistant" in mode:
        if not gemini_key:
            gemini_key = st.text_input('Clé d\'accès Assistant (Gemini)', type='password',
                                       help='Veuillez insérer une clé d\'accès pour activer l\'analyse intelligente.')

    airtable_token = os.environ.get('AIRTABLE_ACCESS_TOKEN') or st.secrets.get('AIRTABLE_ACCESS_TOKEN')
    airtable_base = os.environ.get('AIRTABLE_BASE_ID') or st.secrets.get('AIRTABLE_BASE_ID')

    if not airtable_token:
        st.error('Manque de configuration Airtable.')
        st.stop()

    st.divider()
    st.subheader("☁️ Hébergement (Cloudinary)")
    cloudinary_url = os.environ.get('CLOUDINARY_URL') or st.secrets.get('CLOUDINARY_URL')
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
def get_processor(g_key):
    if GeminiProcessor:
        return GeminiProcessor(g_key, 'config/parsed_data.json')
    return None

@st.cache_resource
def get_source_matcher():
    if SourceMatcher:
        return SourceMatcher('config/sources_data.json')
    return None


def normalize_multi_value_text(value):
    raw = str(value or '').strip()
    if not raw:
        return ''

    parts = re.split(r'\s*\|\s*|[\r\n]+', raw)
    seen = set()
    normalized_parts = []
    for part in parts:
        clean_part = re.sub(r'\s+', ' ', str(part)).strip()
        if clean_part and clean_part not in seen:
            seen.add(clean_part)
            normalized_parts.append(clean_part)

    return ' | '.join(normalized_parts)


def normalize_filtered_star_pair(star_value, legend_value, content_value='', fallback_legend=''):
    star_text = normalize_multi_value_text(star_value)
    legend_text = normalize_multi_value_text(legend_value)

    if sanitize_star_values:
        return sanitize_star_values(
            star_text,
            legend_text,
            content_text=content_value,
            fallback_legend=fallback_legend,
        )

    return star_text, legend_text


REQUIRED_INGESTION_FIELDS = {
    'Titre': 'Titre',
    'Série': 'Serie',
    'Code_Theme_Ref': 'Code Theme',
    'Theme': 'Lien Theme',
    'Extrait': 'Extrait',
    'Source': 'Source brute',
    'Date_Publication': 'Date publication',
}


def field_is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return len(value) == 0
    return False


def sync_pwa_catalog_after_ingestion():
    script_path = os.path.join('scripts', 'export_public_catalog_for_pwa.py')
    if not os.path.exists(script_path):
        return False, "Script de synchronisation PWA introuvable."

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception as exc:
        return False, f"Erreur de synchronisation PWA: {exc}"

    stdout = (result.stdout or '').strip()
    stderr = (result.stderr or '').strip()

    if result.returncode != 0:
        return False, stderr or stdout or "Synchronisation PWA en echec."

    if stdout:
        lines = [line for line in stdout.splitlines() if line.strip()]
        return True, '\n'.join(lines[-4:])

    return True, "Catalogue PWA synchronise."


def load_articles_for_ingestion_view():
    fields = [
        'Titre',
        'Série',
        'Code_Theme_Ref',
        'Theme',
        'Extrait',
        'Source',
        'Date_Publication',
    ]

    records = at_manager.table.all(fields=fields, sort=['-Date_Publication'])
    rows = []

    for record in records:
        payload = record.get('fields', {})
        missing_fields = []

        for field_key, label in REQUIRED_INGESTION_FIELDS.items():
            if field_is_empty(payload.get(field_key)):
                missing_fields.append(label)

        rows.append(
            {
                'Record_ID': record.get('id', ''),
                'Date_Publication': payload.get('Date_Publication', ''),
                'Titre': payload.get('Titre', ''),
                'Série': payload.get('Série', ''),
                'Code_Theme_Ref': payload.get('Code_Theme_Ref', ''),
                'Source': payload.get('Source', ''),
                'Nb_Champs_Manquants': len(missing_fields),
                'Champs_Manquants': ' | '.join(missing_fields),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                'Record_ID',
                'Date_Publication',
                'Titre',
                'Série',
                'Code_Theme_Ref',
                'Source',
                'Nb_Champs_Manquants',
                'Champs_Manquants',
            ]
        )

    return pd.DataFrame(rows)


def load_quality_control_views():
    article_fields = [
        'Titre',
        'Série',
        'Code_Theme_Ref',
        'Theme',
        'Extrait',
        'Source',
        'Date_Publication',
        'Chiffre_Star',
        'Legende_Chiffre',
    ]

    article_records = at_manager.table.all(fields=article_fields, sort=['-Date_Publication'])
    article_ids = {record.get('id', '') for record in article_records}
    star_records = at_manager.star_table.all(fields=['Article_Ref', 'Valeur', 'Legende'])

    star_count_by_article = {}
    orphan_star_rows = []

    for star_record in star_records:
        star_payload = star_record.get('fields', {})
        linked_articles = star_payload.get('Article_Ref') or []

        if not linked_articles:
            orphan_star_rows.append(
                {
                    'Star_Record_ID': star_record.get('id', ''),
                    'Motif': 'Article_Ref manquant',
                    'Valeur': star_payload.get('Valeur', ''),
                    'Legende': star_payload.get('Legende', ''),
                }
            )
            continue

        unknown_links = [record_id for record_id in linked_articles if record_id not in article_ids]
        if unknown_links:
            orphan_star_rows.append(
                {
                    'Star_Record_ID': star_record.get('id', ''),
                    'Motif': 'Article lie introuvable',
                    'Valeur': star_payload.get('Valeur', ''),
                    'Legende': star_payload.get('Legende', ''),
                }
            )

        for article_id in linked_articles:
            if article_id in article_ids:
                star_count_by_article[article_id] = star_count_by_article.get(article_id, 0) + 1

    source_issue_rows = []
    stars_issue_rows = []

    for article_record in article_records:
        article_payload = article_record.get('fields', {})
        article_id = article_record.get('id', '')

        has_source_text = not field_is_empty(article_payload.get('Source'))
        if not has_source_text:
            source_issue_rows.append(
                {
                    'Titre': article_payload.get('Titre', ''),
                    'Date_Publication': article_payload.get('Date_Publication', ''),
                    'Probleme': 'Source extraite vide',
                }
            )

        has_star_text = not field_is_empty(article_payload.get('Chiffre_Star'))
        star_records_count = star_count_by_article.get(article_id, 0)

        if has_star_text and star_records_count == 0:
            stars_issue_rows.append(
                {
                    'Titre': article_payload.get('Titre', ''),
                    'Date_Publication': article_payload.get('Date_Publication', ''),
                    'Probleme': 'Chiffre_Star present mais aucun enregistrement dans Chiffres_Stars',
                }
            )
        elif (not has_star_text) and star_records_count > 0:
            stars_issue_rows.append(
                {
                    'Titre': article_payload.get('Titre', ''),
                    'Date_Publication': article_payload.get('Date_Publication', ''),
                    'Probleme': 'Chiffres_Stars presents mais champ Chiffre_Star vide',
                }
            )

    source_issues_df = pd.DataFrame(source_issue_rows)
    stars_issues_df = pd.DataFrame(stars_issue_rows)
    orphan_stars_df = pd.DataFrame(orphan_star_rows)

    return {
        'source_issues_df': source_issues_df,
        'stars_issues_df': stars_issues_df,
        'orphan_stars_df': orphan_stars_df,
    }


def load_source_raw_sort_view():
    fields = [
        'Titre',
        'Série',
        'Date_Publication',
        'Source',
    ]

    records = at_manager.table.all(fields=fields, sort=['Source', '-Date_Publication'])
    rows = []

    for record in records:
        payload = record.get('fields', {})
        source_raw = normalize_multi_value_text(payload.get('Source', ''))

        rows.append(
            {
                'Record_ID': record.get('id', ''),
                'Titre': payload.get('Titre', ''),
                'Série': payload.get('Série', ''),
                'Date_Publication': payload.get('Date_Publication', ''),
                'Source_Brute': source_raw,
                'Source_Brute_Norm': str(source_raw).strip().lower(),
                'Source_Extraite_Renseignee': 0 if field_is_empty(source_raw) else 1,
            }
        )

    if not rows:
        empty_summary = pd.DataFrame(
            columns=[
                'Source_Brute',
                'Nb_Articles',
                'Derniere_Date',
            ]
        )
        empty_details = pd.DataFrame(
            columns=[
                'Date_Publication',
                'Titre',
                'Série',
                'Source_Brute',
                'Source_Extraite_Renseignee',
            ]
        )
        return empty_summary, empty_details

    details_df = pd.DataFrame(rows)
    details_non_empty_df = details_df[details_df['Source_Brute_Norm'] != ''].copy()

    if details_non_empty_df.empty:
        empty_summary = pd.DataFrame(
            columns=[
                'Source_Brute',
                'Nb_Articles',
                'Derniere_Date',
            ]
        )
        return empty_summary, details_df

    summary_df = (
        details_non_empty_df.groupby('Source_Brute_Norm', dropna=False)
        .agg(
            Source_Brute=('Source_Brute', 'first'),
            Nb_Articles=('Record_ID', 'count'),
            Derniere_Date=('Date_Publication', 'max'),
        )
        .reset_index(drop=True)
    )

    summary_df = summary_df.sort_values(by=['Nb_Articles', 'Source_Brute'], ascending=[False, True])
    details_df = details_df.sort_values(by=['Source_Brute', 'Date_Publication', 'Titre'], ascending=[True, False, True])

    return summary_df, details_df


def load_articles_for_app_availability_view():
    fields = [
        'Titre',
        'Série',
        'Code_Theme_Ref',
        'Date_Publication',
        'Source',
    ]
    records = at_manager.table.all(fields=fields, sort=['-Date_Publication'])
    rows = []

    for record in records:
        payload = record.get('fields', {})
        rows.append(
            {
                'Record_ID': record.get('id', ''),
                'Titre': payload.get('Titre', ''),
                'Série': payload.get('Série', ''),
                'Code_Theme_Ref': payload.get('Code_Theme_Ref', ''),
                'Date_Publication': payload.get('Date_Publication', ''),
                'Source': payload.get('Source', ''),
            }
        )

    if not rows:
        return pd.DataFrame(columns=['Record_ID'] + fields)

    return pd.DataFrame(rows)

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
            if not gemini_key:
                st.error("La clé API Gemini est requise.")
            else:
                progress_text = "Opération en cours..."
                my_bar = st.progress(0, text=progress_text)

                new_queue = []
                processor = get_processor(gemini_key)

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

                        # 3. Analyze with AI (Gemini uniquement)
                        data = processor.analyze_document(text)
                        if isinstance(data, dict) and 'error' in data:
                            raise ValueError(f"Erreur IA : {data['error']}")
                            
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
                        'Source Brute (Texte)',
                        value=data.get('Source', ''),
                        help="Organisme ou auteur éditeur brut extrait du résumé."
                    )
                    mots_cles = st.text_area(
                        'Mots Clés',
                        value=str(data.get('Mots_Cles', '')),
                        help="Mots-clés extraits du document, séparés par des virgules. L'IA les copie exactement depuis le document."
                    )

                extrait = st.text_area('Extrait', value=data.get('Extrait', ''), height=100)

                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    chiffre_star = st.text_area(
                        'Chiffre(s) Star',
                        value=str(data.get('Chiffre_Star', '')),
                        height=90,
                        help="Un ou plusieurs chiffres clés. Séparez les valeurs par ' | ' ou par des retours à la ligne."
                    )
                with col_c2:
                    legende_chiffre = st.text_area(
                        'Légende(s) Chiffre',
                        value=str(data.get('Legende_Chiffre', '')),
                        height=90,
                        help="Une ou plusieurs légendes/contextes. Séparez les valeurs par ' | ' ou par des retours à la ligne."
                    )

                # Content
                content_val = data.get('Contenu_Nettoye', '')
                if not content_val or len(content_val) < 50:
                     content_val = data.get('Contenu_Principal', entry['text'])
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
                                # Keep only highlighted key figures to avoid noisy stars.
                                **dict(zip(['Chiffre_Star', 'Legende_Chiffre'], normalize_filtered_star_pair(chiffre_star, legende_chiffre, contenu_texte, extrait))),
                                'Titre': titre,
                                'Série': serie,
                                'Code_Theme_Ref': theme_code,
                                'Theme': theme_link, 
                                'Index': new_index,
                                'Extrait': extrait,
                                'Mots_Cles': mots_cles,
                                'Source': source,
                                'Date_Publication': date_pub if date_pub else None,
                                'Contenu_Nettoye': final_content,
                                'Fichier': doc_attachment,
                                'Contenu_Visuel': img_urls
                            }

                            # 5. Create
                            created_article = at_manager.create_article(payload)
                            article_record_id = created_article.get('id') if isinstance(created_article, dict) else None
                            stars_created = at_manager.create_star_records(
                                article_record_id,
                                payload.get('Chiffre_Star', ''),
                                payload.get('Legende_Chiffre', ''),
                            )

                            if stars_created > 0:
                                st.success(f"✅ Article '{titre}' importé avec succès ({stars_created} chiffre(s) star lié(s)) !")
                            else:
                                st.success(f"✅ Article '{titre}' importé avec succès !")

                            sync_ok, sync_feedback = sync_pwa_catalog_after_ingestion()
                            if sync_ok:
                                st.info("🔄 Catalogue PWA synchronisé automatiquement.")
                            else:
                                st.warning("Article importé, mais la synchro PWA a échoué. Lancez 'npm run sync:airtable'.")
                            if sync_feedback:
                                st.caption(sync_feedback)

                            st.session_state.batch_queue[current]['status'] = 'Imported'
                            
                            # Check if all files in queue are imported, if so clear the queue
                            if all(item.get('status') == 'Imported' for item in st.session_state.batch_queue):
                                st.session_state.batch_queue = []
                                st.success("🎉 Tous les articles ont été importés avec succès ! Le formulaire est réinitialisé.")
                                import time
                                time.sleep(2)
                            st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()

                        except Exception as e:
                            st.error(f"Erreur Import: {e}")


if mode == "Saisie Manuelle ✍️":
    # 0. Check for Success Message from previous run
    if 'success_msg' in st.session_state:
        st.success(st.session_state.success_msg)
        del st.session_state.success_msg
    if 'warning_msg' in st.session_state:
        st.warning(st.session_state.warning_msg)
        del st.session_state.warning_msg

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

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            chiffre_star_manual = st.text_area(
                'Chiffre(s) Star',
                height=90,
                help="Un ou plusieurs chiffres clés. Séparez les valeurs par ' | ' ou par des retours à la ligne."
            )
        with col_m2:
            legende_chiffre_manual = st.text_area(
                'Légende(s) Chiffre',
                height=90,
                help="Une ou plusieurs légendes/contextes. Séparez les valeurs par ' | ' ou par des retours à la ligne."
            )

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
                            # Keep only highlighted key figures to avoid noisy stars.
                            **dict(zip(['Chiffre_Star', 'Legende_Chiffre'], normalize_filtered_star_pair(chiffre_star_manual, legende_chiffre_manual, final_content, extrait))),
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

                        created_article = at_manager.create_article(payload)
                        article_record_id = created_article.get('id') if isinstance(created_article, dict) else None
                        at_manager.create_star_records(
                            article_record_id,
                            payload.get('Chiffre_Star', ''),
                            payload.get('Legende_Chiffre', ''),
                        )

                        sync_ok, sync_feedback = sync_pwa_catalog_after_ingestion()

                        # Set Success Message in Session State for persistence after rerun
                        st.session_state.success_msg = f"✅ Article '{titre}' créé avec succès ! (Code: {id_article_str})"
                        if sync_ok:
                            st.session_state.success_msg += " Catalogue PWA synchronisé."
                        else:
                            st.session_state.warning_msg = (
                                "Article créé, mais la synchro PWA a échoué. "
                                "Lancez 'npm run sync:airtable' dans prova-pwa."
                            )

                        if sync_feedback:
                            st.session_state.success_msg += f"\n{sync_feedback}"

                        # Reset Data
                        st.session_state.manual_data = {}
                        st.session_state.manual_images = []

                        # Rerun to clear form and show success message
                        if hasattr(st, 'rerun'): st.rerun() 

                    except Exception as e:
                        st.error(f"Erreur lors de la création : {e}")


st.divider()
st.header("🧩 Suivi rapide ingestion")
st.caption("Vue operateur: verifier que les fiches sont completes avant synchro vers l'app.")

try:
    ingestion_df = load_articles_for_ingestion_view()
except Exception as ingestion_error:
    st.error(f"Impossible de charger la vue Ingestion: {ingestion_error}")
    ingestion_df = pd.DataFrame()

if ingestion_df.empty:
    st.info("Aucun article disponible pour la vue Ingestion.")
else:
    to_review_df = ingestion_df[ingestion_df['Nb_Champs_Manquants'] > 0].copy()
    completed_count = int((ingestion_df['Nb_Champs_Manquants'] == 0).sum())
    completion_rate = int((completed_count / len(ingestion_df)) * 100) if len(ingestion_df) > 0 else 0

    i1, i2, i3 = st.columns(3)
    with i1:
        st.metric('Articles total', int(len(ingestion_df)))
    with i2:
        st.metric('Complets (obligatoires OK)', completed_count)
    with i3:
        st.metric('Taux de completion', f"{completion_rate}%")

    if to_review_df.empty:
        st.success("Tous les articles ont les champs obligatoires complets.")
    else:
        st.warning(f"{len(to_review_df)} article(s) a completer avant disponibilite dans l'app.")
        st.dataframe(
            to_review_df[
                [
                    'Date_Publication',
                    'Titre',
                    'Série',
                    'Source',
                    'Nb_Champs_Manquants',
                    'Champs_Manquants',
                ]
            ],
            width='stretch',
            hide_index=True,
        )

st.divider()
with st.expander("Diagnostics internes (avance)", expanded=False):
    st.caption("Section reservee au controle technique. Le flux operateur principal n en depend pas.")

    try:
        quality_views = load_quality_control_views()
    except Exception as quality_error:
        st.error(f"Impossible de charger les diagnostics qualite: {quality_error}")
        quality_views = {
            'source_issues_df': pd.DataFrame(),
            'stars_issues_df': pd.DataFrame(),
            'orphan_stars_df': pd.DataFrame(),
        }

    source_issues_df = quality_views['source_issues_df']
    stars_issues_df = quality_views['stars_issues_df']
    orphan_stars_df = quality_views['orphan_stars_df']

    q1, q2, q3 = st.columns(3)
    with q1:
        st.metric('Sources extraites manquantes', int(len(source_issues_df)))
    with q2:
        st.metric('Incoherences Chiffres_Stars', int(len(stars_issues_df)))
    with q3:
        st.metric('Chiffres_Stars orphelins', int(len(orphan_stars_df)))

    if not source_issues_df.empty:
        st.subheader("Sources extraites manquantes")
        st.dataframe(source_issues_df, width='stretch', hide_index=True)

    if not stars_issues_df.empty:
        st.subheader("Incoherences Articles ↔ Chiffres_Stars")
        st.dataframe(stars_issues_df, width='stretch', hide_index=True)

    if not orphan_stars_df.empty:
        st.subheader("Enregistrements Chiffres_Stars orphelins")
        st.dataframe(orphan_stars_df, width='stretch', hide_index=True)

    try:
        source_summary_df, source_details_df = load_source_raw_sort_view()
    except Exception as source_view_error:
        st.error(f"Impossible de charger la vue source brute: {source_view_error}")
        source_summary_df = pd.DataFrame()
        source_details_df = pd.DataFrame()

    if not source_summary_df.empty:
        st.subheader("Tri source brute (phase test)")
        st.dataframe(
            source_summary_df[
                [
                    'Source_Brute',
                    'Nb_Articles',
                    'Derniere_Date',
                ]
            ],
            width='stretch',
            hide_index=True,
        )

        source_options = ['Toutes les sources'] + source_summary_df['Source_Brute'].tolist()
        selected_source_raw = st.selectbox(
            "Filtrer le detail par source brute",
            options=source_options,
            help="Tri detaille par designation source extraite.",
        )

        filtered_source_details_df = source_details_df[source_details_df['Source_Brute_Norm'] != ''].copy()
        if selected_source_raw != 'Toutes les sources':
            filtered_source_details_df = filtered_source_details_df[
                filtered_source_details_df['Source_Brute'] == selected_source_raw
            ]

        st.dataframe(
            filtered_source_details_df[
                [
                    'Date_Publication',
                    'Titre',
                    'Série',
                    'Source_Brute',
                ]
            ],
            width='stretch',
            hide_index=True,
        )
    else:
        st.info("Aucune source brute exploitable disponible pour le tri technique.")

st.divider()
st.header("📱 Disponibilite App")
st.caption(
    "Process simplifie: IA extrait, admin valide/corrige, Airtable s'alimente, "
    "puis la synchro met l'article a disposition dans l'app."
)

try:
    app_catalog_df = load_articles_for_app_availability_view()
except Exception as app_catalog_error:
    st.error(f"Impossible de charger la vue Disponibilite App: {app_catalog_error}")
    app_catalog_df = pd.DataFrame()

if app_catalog_df.empty:
    st.info("Aucun article disponible dans Airtable.")
else:
    st.metric('Articles disponibles dans Airtable', int(len(app_catalog_df)))
    st.dataframe(
        app_catalog_df[['Date_Publication', 'Titre', 'Série', 'Source']],
        width='stretch',
        hide_index=True,
    )

sync_col1, sync_col2 = st.columns([1, 2])
with sync_col1:
    if st.button("Synchroniser le catalogue PWA maintenant", type="primary"):
        sync_ok, sync_feedback = sync_pwa_catalog_after_ingestion()
        if sync_ok:
            st.success("Catalogue PWA synchronise avec succes.")
            if sync_feedback:
                st.caption(sync_feedback)
        else:
            st.error("Synchronisation PWA echouee.")
            if sync_feedback:
                st.code(sync_feedback)

with sync_col2:
    st.caption("Commande equivalente: npm run sync:airtable (dans prova-pwa).")


