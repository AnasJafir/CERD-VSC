import os
import sys
import importlib.util
from dotenv import load_dotenv
from pyairtable import Api

load_dotenv()
load_dotenv('config/.env')

api_token = os.environ.get('AIRTABLE_ACCESS_TOKEN')
base_id = os.environ.get('AIRTABLE_BASE_ID')

if not api_token or not base_id:
    print("❌ ERREUR : Airtable Access Token ou Base ID introuvable dans config/.env")
    sys.exit(1)

# Importer AirtableManager et utilitaires depuis le script principal
spec = importlib.util.spec_from_file_location(
    'article_ingestion',
    os.path.join(os.path.dirname(__file__), '04_article_ingestion_gemini.py')
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
AirtableManager = mod.AirtableManager
_split_pipe_values = mod._split_pipe_values


def backfill_chiffres_stars():
    api = Api(api_token)
    articles_table = api.table(base_id, 'Articles')
    stars_table = api.table(base_id, 'Chiffres_Stars')
    manager = AirtableManager(api_token, base_id)

    print("🚀 Démarrage du backfill Chiffres_Stars...")

    try:
        articles = articles_table.all(fields=['Titre', 'Chiffre_Star', 'Legende_Chiffre'])
    except Exception as e:
        print(f"❌ Impossible de lire la table Articles: {e}")
        sys.exit(1)

    try:
        star_records = stars_table.all(fields=['Article_Ref', 'Valeur'])
    except Exception as e:
        print(f"❌ Impossible de lire la table Chiffres_Stars: {e}")
        print("💡 Vérifiez que la table Chiffres_Stars existe (script 02_create_tables.py).")
        sys.exit(1)

    existing_by_article = {}
    for rec in star_records:
        fields = rec.get('fields', {})
        for article_id in fields.get('Article_Ref', []) or []:
            existing_by_article.setdefault(article_id, set()).add(str(fields.get('Valeur', '')).strip())

    created_articles = 0
    created_stars = 0
    skipped_no_data = 0
    skipped_existing = 0

    for article in articles:
        article_id = article.get('id')
        fields = article.get('fields', {})
        title = fields.get('Titre', 'Sans titre')
        star_values = fields.get('Chiffre_Star', '')
        legend_values = fields.get('Legende_Chiffre', '')

        stars = _split_pipe_values(star_values)
        if not stars:
            skipped_no_data += 1
            continue

        existing_vals = existing_by_article.get(article_id, set())
        if existing_vals and all(star in existing_vals for star in stars):
            skipped_existing += 1
            continue

        created_count = manager.create_star_records(article_id, star_values, legend_values)
        if created_count > 0:
            created_articles += 1
            created_stars += created_count
            print(f"➕ {title[:60]}... -> {created_count} chiffre(s) star créé(s)")

    print("\n✅ Backfill terminé")
    print(f"   Articles traités avec création : {created_articles}")
    print(f"   Chiffres_Stars créés : {created_stars}")
    print(f"   Articles sans Chiffre_Star : {skipped_no_data}")
    print(f"   Articles déjà couverts : {skipped_existing}")


if __name__ == '__main__':
    backfill_chiffres_stars()
