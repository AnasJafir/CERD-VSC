const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

const regex = /candidates\.sort\(key=lambda item: \(-item\['score'\], item\['order'\]\)\)\s+return candidates\[:max_items\]/;
const replacement = `candidates.sort(key=lambda item: (-item['score'], item['order']))
    selected = candidates[:max_items]
    selected.sort(key=lambda item: item['order'])
    return selected`;

c = c.replace(regex, replacement);

fs.writeFileSync(p, c, 'utf8');
