const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let code = fs.readFileSync(p, 'utf8');

// Remove the `selected.sort(key=lambda item: item['order'])` which completely broke chronological sorting
code = code.replace(/selected\.sort\(key=lambda item: item\['order'\]\)/g, '# Supprimé pour forcer l\'ordre chrono');

fs.writeFileSync(p, code);
console.log('Python sorting patched');
