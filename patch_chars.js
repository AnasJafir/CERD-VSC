const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let code = fs.readFileSync(p, 'utf8');

code = code.replace(/Cout estime/g, 'Coût estimé');
code = code.replace(/montant financier cle/ig, 'Montant financier clé');
code = code.replace(/investissement cle/ig, 'investissement clé');
code = code.replace(/information cle/ig, 'information clé');
code = code.replace(/valeur cle/ig, 'valeur clé');
code = code.replace(/donnee cle/ig, 'donnée clé');

// Make sure the inline code instructions are working and replacing the old ones
code = code.replace(
`- Ne modifie pas la taille de la police pour les chiffres. Contente-toi simplement d'entourer les chiffres clés (et UNIQUEMENT les chiffres) avec des astérisques pour les mettre en gras (\`**chiffre**\`). N'utilise JAMAIS de titres Markdown (\`###\`) pour eux.`,
`- Ne mets PAS le texte normal en gras. Par contre, pour les CHIFFRES CLÉS extraits (et UNIQUEMENT eux), affiche les "en ligne" mais entoure-les avec des accents graves (backticks) pour les marquer comme du code (\`chiffre\`). N'entoure AUCUN autre mot de la sorte.`
);

code = code.replace(
`- EXEMPLE ATTENDU (dans le texte) : le projet évalué à **5,3** milliards d'euros en **2008**.`,
`- EXEMPLE ATTENDU (dans le texte) : le projet évalué à \`5,3 milliards d'euros\` en 2008.`
);

fs.writeFileSync(p, code);
console.log('chars patched');
