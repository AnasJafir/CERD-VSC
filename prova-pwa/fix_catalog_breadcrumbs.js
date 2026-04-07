const fs = require('fs');

function fixCatalog() {
    let code = fs.readFileSync('src/data/catalog.ts', 'utf8');
    const regex = /export function getFullBreadcrumbsForTheme\(themeId: string\) \{\s*const theme = TAXONOMY\.themes\.find\(t => t\.code === themeId\);\s*if \(\!theme\) return \[\];/s;
    
    if (regex.test(code)) {
        code = code.replace(regex, `export function getFullBreadcrumbsForTheme(themeId: string) {
  const appTheme = THEMES.find(t => t.id === themeId);
  const themeMatch = appTheme ? TAXONOMY.themes.find(t => t.nom === appTheme.label || t.code === appTheme.code) : null;
  if (!appTheme || !themeMatch) return [];
  const theme = themeMatch;`);
        fs.writeFileSync('src/data/catalog.ts', code, 'utf8');
        console.log('Fixed catalog.ts');
    } else {
        console.log('Target string not found in catalog.ts');
    }
}

fixCatalog();
