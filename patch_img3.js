const fs = require('fs');

let file_path = 'prova-pwa/app/index.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  'logoStage: {',
  "logoStage: { width: '100%', "
);

fs.writeFileSync(file_path, file_code);
console.log('patched index.tsx image layout');

let file_path2 = 'prova-pwa/app/e1-home.tsx';
let file_code2 = fs.readFileSync(file_path2, 'utf8');

file_code2 = file_code2.replace(
  'imageWrap: {',
  "imageWrap: { width: '100%', "
);
fs.writeFileSync(file_path2, file_code2);
console.log('patched e1-home.tsx image layout');

