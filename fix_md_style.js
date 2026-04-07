const fs = require('fs');
let p = 'prova-pwa/app/e6-article.tsx';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/    strong: \{\s*fontFamily: typography\.body,\s*fontWeight: '700',\s*color: palette\.textStrong,\s*\}/, `    strong: {
      fontFamily: typography.display,
      fontSize: 24,
      fontWeight: '800',
      color: palette.brandDark,
    }`);

c = c.replace(/    heading3: \{.*?\}/s, `    heading3: {
      fontFamily: typography.display,
      fontSize: 32,
      fontWeight: '900',
      color: palette.brand,
      marginTop: 24,
      marginBottom: 8,
    }`);

fs.writeFileSync(p, c, 'utf8');
