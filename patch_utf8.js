const fs = require('fs');

['app/index.tsx', 'app/mode-emploi.tsx', 'app/e6-article.tsx'].forEach(f => {
  let t = fs.readFileSync('prova-pwa/' + f, 'utf8');
  let original = t;
  
  // Known artifacts:
  t = t.replace(/É\xA8/g, 'è');
  t = t.replace(/É\xA0/g, 'à');

  let matches = t.match(/[A-Za-z-']*É(?!c[oO]|t[uU]|s[tT]|t[aA]|l[eE]|v[oO]|l[aA]|r[uU]|q[uU]|g[lL]|d[oO]|r[eE]|p[hH]|q[uU]|p[aA]|t[aA]|p[oO]|n[oO]|m[aA]|s[oO]|t[iI]|r[iI]|c[uU]|c[hH]|d[iI]|p[iI]|c[aA]|v[aA]|p[uU]|t[rR]|s[oO]|c[oO]|m[eE]|b[uU]|p[eE]|l[iI]|d[eE]|r[oO]|t[oO]\b)[^\w\s].{0,3}/gi);
  if (matches) {
    matches.forEach(m => console.log('Found strange É combo in', f, ':', m));
  }
  
  if (t !== original) {
    fs.writeFileSync('prova-pwa/' + f, t, 'utf8');
    console.log('Fixed', f);
  }
});
