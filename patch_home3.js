const fs = require('fs');

let file_path = 'prova-pwa/app/e1-home.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  'resizeMode="cover"',
  'resizeMode="contain"'
);

file_code = file_code.replace(
  'height: 180, // Ajustez la hauteur',
  'height: 200, // Ajustez la hauteur'
);

fs.writeFileSync(file_path, file_code);
console.log('e1-home.tsx resizeMode patched');

