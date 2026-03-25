import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='config/.env')

GROQ_API_KEY = os.getenv('GROQ_API_KEY') or "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

def test_groq_model():
    print("🚀 Test de connexion à GROQ API (Llama-3.1-8B)...")
    if not GROQ_API_KEY or "VOTRE_CLE" in GROQ_API_KEY:
        print("⚠️ Attention : Aucune clé API Groq définie.")
        print("Obtenez-la gratuitement sur console.groq.com")
        return
    
    texte_test = """
    Rapport annuel 2023 de la Banque Centrale. 
    L'économie a connu une croissance de 3% cette année. Le taux d'inflation s'est stabilisé autour de 2.5%.
    Les investissements dans les énergies renouvelables ont doublé.
    Ce document est une note interne destinée au Ministère des Finances.
    Date de diffusion : 14 Février 2024.
    """
    
    context_str = """
    - 10.1: Croissance économique
    - 10.2: Inflation et taux d'intérêt
    - 20.1: Energies renouvelables
    - 32.2: Finances publiques
    """

    prompt = f'''Tu es un expert archiviste pour le Centre d'Études (CERD). Analyse le document et extrais les métadonnées EN FORMAT JSON STRICTEMENT VALIDE.

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
'''

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
        
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            print(f"❌ Erreur API ({response.status_code}): {response.text}")
            return
            
        print("✅ Réponse reçue avec succès ! Analyse en cours...\n")
        result_text = response.json()['choices'][0]['message']['content']
        
        try:
            data = json.loads(result_text.strip())
            print("🟢 JSON PARSÉ AVEC SUCCÈS :")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"🔴 ERREUR DE PARSING JSON : {e}")
            print(f"Brut : {result_text}")
            
    except Exception as e:
        print(f"🔴 Erreur inconnue : {e}")

if __name__ == "__main__":
    test_groq_model()
