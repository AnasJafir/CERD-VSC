const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/- Mets en évidence les chiffres clés : entoure-les de gras \(`\*\*chiffre\*\*`\)\. S'ils apparaissent comme particulièrement majeurs ou isolés dans l'article, utilise un très grand titre Markdown \(`### \*\*le chiffre\*\*`\) pour les faire ressortir\./,
`- Ne modifie pas la taille de la police pour les chiffres. Contente-toi simplement d'entourer les chiffres clés (et UNIQUEMENT les chiffres) avec des astérisques pour les mettre en gras (\`**chiffre**\`). N'utilise JAMAIS de titres Markdown (\`###\`) pour eux.`);

c = c.replace(/- EXEMPLE ACCEPTÉ \(chiffre star isolé\) : `\\n### \*\*25 %\*\*\\nDe croissance annuelle\.\.\.\\n`/,
`- EXEMPLE INTERDIT (NE FAIS JAMAIS ÇA) : \`### **25 %**\` (garde la structure d'origine et la taille normale) ! Ne mets AUCUN texte classique en gras s'il ne s'agit pas d'un chiffre clé.`);

c = c.replace(/- Extrais EXACTEMENT ce texte pour remplir le champ "titre_visuel"\./,
`- Extrais EXACTEMENT ce texte pour remplir le champ "titre_visuel".
  - SUPPRIME IMPÉRATIVEMENT intégralement ce texte descriptif / légende / titre de l'illustration du du reste du corps de l'article (\`contenu_nettoye\`) pour éviter un doublon quand on affichera le visuel au-dessus du texte.`);

fs.writeFileSync(p, c, 'utf8');
console.log('Gemini Prompt patched!');
