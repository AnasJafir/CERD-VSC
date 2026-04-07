const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/REGLES CHIFFRES CLES CONTEXTUALISES \(OBLIGATOIRE\) :.*?(?=\nCHAMPS JSON ATTENDUS)/s, 
`REGLES CHIFFRES CLES CONTEXTUALISES (OBLIGATOIRE) :
- N'extrais jamais un chiffre seul sans contexte. Le contexte de l'article et la légende doivent être IMPERATIVEMENT respectés.
- L'IA doit comprendre l'article, son sujet et son contexte pour bien sélectionner et afficher les chiffres clés.
- Le but exclusif est de mettre en avant l'information "star" que valorise l'article.
- S'il y a un ordre chronologique à respecter entre les chiffres, maintiens-le strictement tout en respectant la légende (ex: 2021 d'abord, puis 2022).
- Chaque chiffre retenu doit avoir une légende autonome qui répond au minimum à ce qu'il a mesuré (QUOI).
- QUAND et OU sont très recommandés, ajoute-les s'ils sont dans l'article. 
- Conserve les equivalences monétaires (ex: 5,3 milliards d'euros + 60 milliards DH).
- Omet les années isolées sans contexte clair.

REGLES POUR LES VISUELS (OBLIGATOIRE) :
- Lors de l'analyse de l'article, il faut détecter le nom ou titre exact de la figure, image, graphe ou tableau s'il y en a de mentionné dans le texte. Tu dois l'associer comme titre du visuel.
`);

c = c.replace(/\"observations\":/g, '"titre_visuel": "Nom exact de la figure, image, graphe ou tableau. Sinon, laisse vide",\n    "observations":');

fs.writeFileSync(p, c, 'utf8');
