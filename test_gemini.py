import os
import json
from dotenv import load_dotenv

import importlib.util

module_name = 'article_ingestion_gemini'
file_path = os.path.join('scripts', '04_article_ingestion_gemini.py')
spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
GeminiProcessor = module.GeminiProcessor

def test_gemini():
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY') or "votre_cle_gemini_ici"
    
    if not gemini_key or "votre" in gemini_key.lower():
        print("Clé Gemini invalide ou introuvable.")
        return

    print("🚀 Test de connexion à Gemini avec Clean Split JSON...")
    
    processor = GeminiProcessor(gemini_key)
    
    texte_test = """Un projet né en 1979 (mais l’idée remonte à plus d’un siècle) à l'occasion d'une rencontre entre
les rois Juan Carlos et Hassan II. Le projet de relier le Maroc et l'Espagne est resté dans les tiroirs
plus de quatre décennies, il refait surface en février 2023.
- En 2008, le projet de liaison fixe pour relier Malabata près de Tanger à la ville
espagnole Tarifa était évalué en 2008 à 5,3 milliards d’€, soit 60 milliards DH
- Les travaux d’étude ont été confiés à la Société marocaine d’études du détroit de
Gibraltar (Sned) et la Société espagnole d’études (Seceg),
- L’ouvrage sera long de 28 mètres sous-marine. C'est plus court, mais beaucoup
plus profond que le tunnel sous la Manche, qui parcourt 38 kilomètres en moyenne à
100 mètres au-dessous du niveau de la mer. L'ouvrage hispano-marocain dans son
entier mesurerait 38,7 km de long et sa profondeur atteindrait les 475 m.
- 17 ans plus tard, " Le mythe devient tangible", titrait le quotidien espagnol El Pais, le
coût devrait atteindre les 15 milliards d’€.
- Fin 2025, plus de 25 milliards d’€ seront nécessaires.
- Casablanca - Madrid : 5 heure 30, selon le site marocain Bladi.net"""
    
    print("Envoi du texte pour analyse...")
    result = processor.analyze_document(texte_test)
    
    print("\n🟢 RÉSULTAT DE L'EXTRACTION JSON :")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_gemini()
