import os
import sys
import json
import time
import importlib.util
from dotenv import load_dotenv
from pyairtable import Api
from pyairtable.formulas import match
from requests.exceptions import HTTPError

load_dotenv()
load_dotenv('config/.env')
api_token = os.environ.get('AIRTABLE_ACCESS_TOKEN')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_token or not base_id:
    print("❌ ERREUR : Airtable Access Token ou Base ID introuvable dans config/.env")
    sys.exit(1)

# Importer SourceMatcher depuis le script d'ingestion (nom de fichier commençant par 04)
spec = importlib.util.spec_from_file_location('article_matcher', os.path.join(os.path.dirname(__file__), '04_article_ingestion_gemini.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SourceMatcher = mod.SourceMatcher

def migrate_sources_and_link_articles():
    api = Api(api_token)
    sources_table = api.table(base_id, 'Sources')
    articles_table = api.table(base_id, 'Articles')
    
    print("🚀 Démarrage du script de migration Airtable...")
    
    # ÉTAPE 1: VÉRIFIER L'ACCÈS À LA TABLE SOURCES
    try:
        # Test simple pour voir si la table existe
        sources_table.first(max_records=1)
    except HTTPError as e:
        if e.response.status_code in [403, 404]:
            print("\n❌ ERREUR 403/404 : La table 'Sources' n'existe pas encore sur votre Airtable.")
            print("\n🚨 ACTION REQUISE AVANT DE CONTINUER 🚨")
            print("1. Allez sur votre base Airtable et ajoutez une Table vide nommée 'Sources'.")
            print("2. Ajoutez ces champs exacts :")
            print("   - Code_Source (Texte court / Champ principal obligatoirement !)")
            print("   - Nom_Source (Texte court)")
            print("   - Categorie (Texte court ou Sélection unique)")
            print("   - Aliases (Texte long)")
            print("3. Dans votre table 'Articles', ajoutez un champ 'Source_Ref' de type 'Link to another record' pointant vers 'Sources'.")
            print("4. Relancez ce script.\n")
            sys.exit(1)
        else:
            raise e

    # ÉTAPE 2: PEUPLER LA TABLE SOURCES
    print("\n--- ÉTAPE 1 : Peuplement de la table 'Sources' ---")
    matcher = SourceMatcher('config/sources_data.json')
    if not matcher.sources:
        print("❌ Aucune source trouvée dans config/sources_data.json. Avez-vous exécuté parse_sources.py ?")
        sys.exit(1)
        
    source_record_ids = {} # mapping code -> record_id
    
    for s in matcher.sources:
        # Check if code already exists
        records = sources_table.all(formula=match({'Code_Source': s['code']}), max_records=1)
        if not records:
            time.sleep(0.2)
            try:
                new_record = sources_table.create({
                    'Code_Source': s['code'],
                    'Nom_Source': s['nom'],
                    'Categorie': s['categorie'],
                    'Aliases': ', '.join(s.get('aliases', []))
                })
                source_record_ids[s['code']] = new_record['id']
                print(f"➕ Source créée : {s['code']} - {s['nom']}")
            except HTTPError as e:
                # Si erreur sur le modèle des colonnes
                if e.response.status_code == 422:
                    print(f"\n❌ Erreur 422 : Airtable a rejeté les colonnes. Vérifiez que la table 'Sources' a bien les colonnes : Code_Source, Nom_Source, Categorie, Aliases.")
                    sys.exit(1)
                raise e
        else:
            source_record_ids[s['code']] = records[0]['id']
            print(f"⬇️ Source existante : {s['code']}")

    # ÉTAPE 3: METTRE À JOUR LES ARTICLES EXISTANTS
    print(f"\n--- ÉTAPE 2 : Mise à jour des articles ('Source_Ref') ---")
    try:
        all_articles = articles_table.all(fields=['Source', 'Source_Ref', 'Titre'])
    except HTTPError as e:
         if e.response.status_code == 422:
             print("\n❌ Erreur 422 : Airtable a rejeté la demande sur 'Articles'. Vérifiez que le champ 'Source_Ref' a bien été créé en mode 'Link to another record'.")
             sys.exit(1)
         raise e
         
    updated_count = 0
    missed_count = 0
    
    for a in all_articles:
        fields = a.get('fields', {})
        raw_source = fields.get('Source')
        source_ref = fields.get('Source_Ref')
        titre = fields.get('Titre', 'Sans titre')
        
        if raw_source:
            source_matches = matcher.match_many(raw_source)
            matched_codes = [m['code'] for m in source_matches if m.get('code') != '999']

            target_ids = []
            seen_ids = set()
            for code in matched_codes:
                rec_id = source_record_ids.get(code)
                if rec_id and rec_id not in seen_ids:
                    seen_ids.add(rec_id)
                    target_ids.append(rec_id)

            if target_ids:
                existing_ids = list(source_ref) if isinstance(source_ref, list) else []
                if set(existing_ids) != set(target_ids):
                    print(
                        f"🔗 Match pour l'article '{titre[:50]}...' : '{raw_source}' -> Codes {', '.join(matched_codes)}"
                    )
                    # Mise à jour sur Airtable
                    time.sleep(0.25) # Rate limiting safe
                    articles_table.update(a['id'], {'Source_Ref': target_ids})
                    updated_count += 1
            else:
                missed_count += 1
                
    print(f"\n✅ MIGRATION RÉUSSIE !")
    print(f"   - {len(matcher.sources)} sources vérifiées/créées")
    print(f"   - {updated_count} articles mis à jour avec la nouvelle liaison relationnelle")
    if missed_count > 0:
        print(f"   - {missed_count} articles non reconnus ignorés (code 999)")

if __name__ == "__main__":
    migrate_sources_and_link_articles()
