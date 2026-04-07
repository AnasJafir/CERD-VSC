const fs = require('fs');

let file_path = 'app/e6-article.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replaceAll(
  '<Text style={{color: palette.textMuted}}> > </Text>',
  "<Text style={{color: palette.textMuted}}>{' > '}</Text>"
);

fs.writeFileSync(file_path, file_code);
console.log('e6-article.tsx arrows fixed');
