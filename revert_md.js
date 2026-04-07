const fs = require('fs');
let p = 'prova-pwa/app/e6-article.tsx';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/    strong: \{\s*fontFamily: typography\.display,\s*fontSize: 24,\s*fontWeight: '800',\s*color: palette\.brandDark,\s*\}/, `    strong: {
      fontFamily: typography.body,
      fontWeight: '800',
      color: palette.textStrong,
    }`);

c = c.replace(/    heading1/, `    heading1`); // Just verify it doesn't crash

fs.writeFileSync(p, c, 'utf8');
console.log('e6-article.tsx reverted');
