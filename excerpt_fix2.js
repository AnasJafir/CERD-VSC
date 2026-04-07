const fs = require('fs');
let txt = fs.readFileSync('prova-pwa/app/e6-article.tsx', 'utf8');

txt = txt.replace(/<Markdown style=\{markdownStyles\}>\s*\{article.excerpt.replace\(\/\(d\+\(\?\:,d\+\)\?s\*\(\?\:milliards\?\|millions\?\)\?s\*\(\?\:d\['’\]s\*\)\?\(\?\:€\|\$\|dh\|mad\|eur\|usd\|h\|heure\|heures\|%\)\(\?\:s\*d\+\)\?\)\/gi, '`\$1`'\)\s*\}\s*<\/Markdown>/,
`<Markdown style={markdownStyles}>
                {article.excerpt.replace(/(\\d+(?:[,.]\\d+)?(?:\\s*(?:milliards?|millions?))?\\s*(?:d['’]\\s*)?(?:€|\\$|dh|mad|eur|usd|h|heure|heures|%)(?:\\s*\\d+)?)/gi, String.fromCharCode(96) + '$1' + String.fromCharCode(96))}
              </Markdown>`);

fs.writeFileSync('prova-pwa/app/e6-article.tsx', txt);
console.log('Fixed excerpt');
