const fs = require('fs');
let p = 'prova-pwa/app/e6-article.tsx';
let txt = fs.readFileSync(p, 'utf8');

// I'm replacing the bad regex with a simpler backtick wrapper that dynamically captures any numbers with units
let oldExcerpt = `<Markdown style={markdownStyles}>
                {article.excerpt.replace(/(d+(?:,d+)?s*(?:milliards?|millions?)?s*(?:d['’]s*)?(?:€|$|dh|mad|eur|usd|h|heure|heures|%)(?:s*d+)?)/gi, '\`$1\`')}    
              </Markdown>`;
              
let newExcerpt = `<Markdown style={markdownStyles}>
                {article.excerpt.replace(/(\\d+(?:[,.]\\d+)?\\s*(?:milliards?|millions?)\\s*(?:d['’]\\s*)?(?:€|\\$|DH|MAD|EUR|USD|heure|heures|%)(?:\\s*\\d+)?)/gi, '\\`$1\\`')}
              </Markdown>`;

if(txt.includes(oldExcerpt)) {
    txt = txt.replace(oldExcerpt, newExcerpt);
    fs.writeFileSync(p, txt, 'utf8');
    console.log('Excerpt fixed');
} else {
    console.log('Old excerpt not found');
}
