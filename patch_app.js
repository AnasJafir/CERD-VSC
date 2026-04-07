const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let code = fs.readFileSync(p, 'utf8');

code = code.replace(
`- EXEMPLE ACCEPTÉ (dans le texte) : \`le projet évalué à **5,3** milliards d'euros en **2008**.\`\n`,
``
);

code = code.replace(
`- Ne modifie pas la taille de la police pour les chiffres. Contente-toi simplement d'entourer les chiffres clés (et UNIQUEMENT les chiffres) avec des astérisques pour les mettre en gras (\`**chiffre**\`). N'utilise JAMAIS de titres Markdown (\`###\`) pour eux.`,
``
);

fs.writeFileSync(p, code);
console.log('Final patch complete');
