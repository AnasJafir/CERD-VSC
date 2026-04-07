const fs = require('fs');
let code = fs.readFileSync('app/index.tsx', 'utf8');

// Change background color to palette.bg to match theme
code = code.replace(/backgroundColor: '#ffffff'/g, 'backgroundColor: palette.bg');

// Update primary button style to use brand colors
code = code.replace(/backgroundColor: palette\.textStrong,/g, 'backgroundColor: palette.brandDark,');

// Update secondary button style to match Theme
code = code.replace(/backgroundColor: '#f5f5f5',/g, 'backgroundColor: palette.surfaceAlt,');
code = code.replace(/borderColor: '#e0e0e0',/g, 'borderColor: palette.border,');
code = code.replace(/backgroundColor: '#ebebeb',/g, 'backgroundColor: palette.surfaceStrong,');

// Adjust hero title color to brand
code = code.replace(/color: palette\.textStrong,\s*marginBottom: 8,/g, 'color: palette.brandDark,\n    marginBottom: 8,');

// Modify logo box
code = code.replace(/backgroundColor: '#fff',/g, "backgroundColor: palette.surface,");

fs.writeFileSync('app/index.tsx', code, 'utf8');
console.log('Fixed index.tsx');
