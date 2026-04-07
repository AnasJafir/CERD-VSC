const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

const regex = /"chiffres_stars": "Optionnel: liste \[\{"chiffre":"\.\.\.", "legende":"Avec accents !"\}\], triée chrono\.", "legende":"Avec accents !"\}\], triée chrono\.", \\"legende\\":\\"\.\.\.\\"\}\}\], liee 1-1 et limitee a 3\.",/;

c = c.replace(regex, `"chiffres_stars": "Optionnel: liste [{{\\"chiffre\\":\\"...\\", \\"legende\\":\\"Avec accents !\\"}}], triée chrono.",`);

fs.writeFileSync(p, c, 'utf8');
