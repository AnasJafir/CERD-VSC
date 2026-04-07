const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/'contenu_nettoye':\s*'Contenu_Nettoye'\n\s*\}/, `'contenu_nettoye': 'Contenu_Nettoye',\n            'titre_visuel': 'Titre_Visuel'\n        }`);

fs.writeFileSync(p, c, 'utf8');
