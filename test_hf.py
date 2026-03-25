import os
import json
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement (si le .env existe)
load_dotenv(dotenv_path='config/.env')

# Clé API : essayez d'abord de la prendre dans le .env, sinon remplacez ici.
HF_API_KEY = "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"
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"

def test_huggingface_model():
    print("🚀 Test de connexion à HuggingFace API (Qwen2.5-7B-Instruct)...")
    if not HF_API_KEY or "VOTRE_CLE" in HF_API_KEY:
        print("⚠️ Attention : Aucune clé API HuggingFace définie.")
        print("❌ HuggingFace exige désormais une clé API (même gratuite) sur ses nouveaux serveurs (router).")
    
    # 1. Simuler un petit texte de document
    texte_test = """
    Rapport annuel 2023 de la Banque Centrale. 
    L'économie a connu une croissance de 3% cette année. Le taux d'inflation s'est stabilisé autour de 2.5%.
    Les investissements dans les énergies renouvelables ont doublé.
    Ce document est une note interne destinée au Ministère des Finances.
    Date de diffusion : 14 Février 2024.
    """
    
    # 2. Simuler quelques codes thématiques (normalement tirés de parsed_data.json)
    context_str = """
    - 10.1: Croissance économique
    - 10.2: Inflation et taux d'intérêt
    - 20.1: Energies renouvelables
    - 32.2: Finances publiques
    """

    # 3. Le prompt EXACT utilisé dans l'application Streamlit
    prompt = f'''[INST] Tu es un expert archiviste pour le Centre d'Études (CERD). Analyse le document et extrais les métadonnées en FORMAT JSON VALIDE STRICT.

Champs requis :
1. "Titre" (String): Titre explicite.
2. "Extrait" (String): Résumé de 3 lignes max.
3. "Mots_Cles" (String): Mots-clés séparés par des virgules. Si aucun, laisser vide.
4. "Source" (String): Entité productrice.
5. "Date_Publication" (String): Format YYYY-MM-DD.
6. "Code_Theme_Ref" (String): Code pertinent de la liste ci-dessous.
7. "Série" (String): Classification "c1", "c2", "c3", "c4" (minuscule).
8. "Contenu_Principal" (String): Le TEXTE INTÉGRAL du corps de l'article, reformaté pour la lisibilité.

Liste des Codes Thématiques :
{context_str}

Texte Complet :
{texte_test}

RÉPONDS UNIQUEMENT ET STRICTEMENT AVEC LE JSON (commence par {{ et termine par }}), RIEN D'AUTRE. [/INST]'''

    headers = {}
    if HF_API_KEY and "VOTRE_CLE" not in HF_API_KEY:
        headers["Authorization"] = f"Bearer {HF_API_KEY}"
        
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"❌ Erreur API ({response.status_code}): {response.text}")
            return
            
        print("✅ Réponse reçue avec succès ! Analyse en cours...\n")
        result_text = response.json()[0]['generated_text'].strip()
        
        # Nettoyage Markdown
        if result_text.startswith("```json"): result_text = result_text[7:]
        if result_text.startswith("```"): result_text = result_text[3:]
        if result_text.endswith("```"): result_text = result_text[:-3]
        
        # Validation JSON
        try:
            data = json.loads(result_text.strip())
            print("🟢 JSON PARSÉ AVEC SUCCÈS :")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"🔴 ERREUR DE PARSING JSON : {e}")
            print(f"Texte retourné : {result_text}")
            
    except requests.exceptions.Timeout:
         print("🔴 Timeout : L'API a mis trop de temps à répondre.")
    except Exception as e:
        print(f"🔴 Erreur inconnue : {e}")

if __name__ == "__main__":
    test_huggingface_model()
