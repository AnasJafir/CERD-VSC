import os

app_path = r"C:\Users\user\Desktop\CERD-VSC\app.py"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """        # Navigation
        col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])"""

injection = """        # 🚀 BULK IMPORT BUTTON
        pending_items = [i for i, entry in enumerate(queue) if entry['status'] != 'Imported' and entry['status'] != 'Error']
        if len(pending_items) > 0:
            st.divider()
            if st.button(f"🚀 Importer TOUT le lot ({len(pending_items)} articles) automatiquement", type="primary", use_container_width=True):
                with st.spinner(f"Importation automatique de {len(pending_items)} articles en cours..."):
                    c_mgr = CloudinaryManager(c_name, c_key, c_secret) if "Complet" in import_scope else None
                    success_count = 0
                    errors = []

                    bar_import = st.progress(0)
                    for idx_iter, queue_idx in enumerate(pending_items):
                        entry = queue[queue_idx]
                        data = entry['data']

                        titre = data.get('Titre', 'Sans titre')
                        theme_raw = str(data.get('Code_Theme_Ref', data.get('Theme_ID', ''))).split(' - ')[0].strip()
                        theme_code = theme_raw if theme_raw else "0.0"
                        serie = str(data.get('Série', 'c1')).lower().strip()
                        if serie not in ['c1', 'c2', 'c3', 'c4']:
                            serie = 'c1'

                        source = data.get('Source', '')
                        date_pub = data.get('Date_Publication', '')
                        extrait = data.get('Extrait', '')
                        mots_cles = data.get('Mots_Cles', '')
                        contenu_texte = data.get('Contenu_Nettoye', data.get('Contenu_Principal', entry.get('text', '')))
                        chiffre_star = data.get('Chiffres_Cles', data.get('Chiffre_Star', ''))
                        legende_chiffre = data.get('Legende_Chiffre', data.get('Legende', ''))

                        doc_url = None
                        img_urls = []
                        final_content = ""

                        if "Complet" in import_scope:
                            if entry.get('file_bytes'):
                                file_stream = io.BytesIO(entry['file_bytes'])
                                file_stream.name = entry['filename']
                                rtype = 'raw' if entry['filename'].lower().endswith(('.pdf','.docx','.zip')) else 'auto'
                                doc_url = c_mgr.upload_file(file_stream, entry['filename'], resource_type=rtype)

                            for i_name, i_bytes in entry.get('images', []):
                                i_io = io.BytesIO(i_bytes)
                                url = c_mgr.upload_file(i_io, i_name, resource_type="image")
                                if url:
                                    ext = os.path.splitext(i_name)[1]
                                    safe_name = titre.replace('/', '-').replace('\\\\', '-') if titre else i_name
                                    if not safe_name.lower().endswith(ext.lower()):
                                        safe_name += ext
                                    img_urls.append({"url": url, "filename": safe_name})

                            final_content = contenu_texte

                        theme_rec_id = at_manager.get_theme_record_id(theme_code)
                        theme_link = [theme_rec_id] if theme_rec_id else []

                        new_index, id_article_str = at_manager.get_next_index(serie if serie else "c1", theme_code)

                        doc_attachment = []
                        if doc_url:
                            doc_attachment.append({"url": doc_url, "filename": entry['filename']})

                        # Formatting Chiffres Cles like the individual form logic
                        stars_dict = dict(zip(['Chiffre_Star', 'Legende_Chiffre'], normalize_filtered_star_pair(chiffre_star, legende_chiffre, contenu_texte, extrait)))

                        payload = {
                            **stars_dict,
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

                        try:
                            # 1. Create article
                            created_article = at_manager.create_article(payload)
                            article_record_id = created_article.get('id') if isinstance(created_article, dict) else None
                            
                            # 2. Create stars records using AirtableManager logic
                            at_manager.create_star_records(article_record_id, stars_dict.get('Chiffre_Star', ''), stars_dict.get('Legende_Chiffre', ''))

                            if created_article:
                                st.session_state.batch_queue[queue_idx]['status'] = 'Imported'
                                success_count += 1
                            else:
                                errors.append(entry['filename'])
                        except Exception as e:
                            errors.append(f"{entry['filename']}: {str(e)}")

                        bar_import.progress((idx_iter + 1) / len(pending_items))

                    if success_count > 0:
                        st.success(f"✅ {success_count} articles importés avec succès (incluant fichiers sur Cloudinary) !")
                        st.balloons()
                        
                        # Sync PWA automatically
                        sync_ok, sync_feedback = sync_pwa_catalog_after_ingestion()
                        if sync_ok:
                            st.info("🔄 Catalogue PWA synchronisé après import massif.")
                        else:
                            st.warning("Import terminé, mais la synchro PWA a échoué. Pensez à faire 'npm run sync:airtable'.")

                    if errors:
                        st.error(f"❌ Échec pour {len(errors)} articles : {', '.join(errors)}")

                    # Auto clear queue if all imported
                    if all(item.get('status') == 'Imported' for item in st.session_state.batch_queue):
                        st.session_state.batch_queue = []
                        st.success("🎉 Tous les articles ont été importés. La file est vidée.")

                    import time
                    time.sleep(2)
                    st.experimental_rerun() if hasattr(st, 'experimental_rerun') else st.rerun()

        # Navigation
        col_nav1, col_nav2, col_nav3 = st.columns([1, 4, 1])"""

if target in content:
    content = content.replace(target, injection)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PATCH SUCCESSFUL!")
else:
    print("TARGET NOT FOUND!")
