const fs = require('fs');

let pwa_p = 'prova-pwa/app/e6-article.tsx';
let pwa_code = fs.readFileSync(pwa_p, 'utf8');

pwa_code = pwa_code.replace(
`  bullet_list: {
    marginLeft: 0,
  }`,
`  bullet_list: {
    marginLeft: 0,
  },
  code_inline: {
    fontFamily: typography.display,
    fontSize: 24,
    fontWeight: '800',
    color: palette.brandDark,
    backgroundColor: 'transparent',
    borderWidth: 0,
    padding: 0,
  }`
);

fs.writeFileSync(pwa_p, pwa_code);
console.log('e6-article.tsx code_inline added');

let p = 'scripts/04_article_ingestion_gemini.py';
let code = fs.readFileSync(p, 'utf8');

code = code.replace(
/- Ne modifie pas la taille de la police pour .* N'utilise JAMAIS de titres Markdown .*/g,
`- Ne mets PAS le texte normal en gras. Par contre, pour les CHIFFRES CLÉS extraits (et UNIQUEMENT eux), affiche les "en ligne" mais entoure-les avec des accents graves (backticks) pour les marquer comme du code (\`chiffre\`). N'entoure AUCUN autre mot de la sorte.`
);

code = code.replace(
/- EXEMPLE INTERDIT .* Ne mets AUCUN texte classique en gras .*/g,
`- EXEMPLE ATTENDU (dans le texte) : le projet évalué à \`5,3 milliards d'euros\` en 2008.\n- INTERDIT : utiliser de grands titres Markdown (###) pour les chiffres dans le corps du texte. Interdit de mettre du texte normal en backticks.`
);

fs.writeFileSync(p, code);
console.log('04_article_ingestion_gemini.py Markdown instructions patched');
