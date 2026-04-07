const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let code = fs.readFileSync(p, 'utf8');

// Disable the score-based sorting for structured candidates, 
// or at least extract year for sorting.
code = code.replace(
    /candidates\.sort\(key=lambda item: \(-item\['score'\], item\['order'\]\)\)/g,
    `
    def get_year(txt):
        import re
        m = re.search(r'\\b(19|20)\\d{2}\\b', str(txt))
        return int(m.group(0)) if m else 9999

    candidates.sort(key=lambda item: (get_year(item['legend'] + " " + item['value']), item['order']))
    `
);

// Add accents to the hardcoded Python labels
code = code.replace(/'Cout estime \{subject_hint\}'/g, "'Coût estimé {subject_hint}'");
code = code.replace(/'Montant financier cle \{subject_hint\}'/g, "'Montant financier clé {subject_hint}'");
code = code.replace(/'Budget ou investissement cle'/g, "'Budget ou investissement clé'");
code = code.replace(/'Temps de trajet'/g, "'Temps de trajet'");
code = code.replace(/'co¹t'/g, "'coût'");

// In e6-article.tsx, revert the markdown strong and add a specific key figure style
fs.writeFileSync(p, code);
console.log('04_article_ingestion_gemini.py patched');

// Fix the styling in e6-article.tsx
let pwa_p = 'prova-pwa/app/e6-article.tsx';
let pwa_code = fs.readFileSync(pwa_p, 'utf8');

pwa_code = pwa_code.replace(
`  strong: {
    fontFamily: typography.display,
    fontSize: 24,
    fontWeight: '800',
    color: palette.brandDark,
  },`,
`  // Removed huge strong style
  strong: {
    fontWeight: 'bold',
  },`
);

fs.writeFileSync(pwa_p, pwa_code);
console.log('e6-article.tsx patched');
