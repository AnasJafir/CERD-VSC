const fs = require('fs');

let file_path = 'app/index.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "height: '100%', borderRadius: 20,",
  "height: '100%', borderRadius: 20, resizeMode: 'contain',"
);

fs.writeFileSync(file_path, file_code);
console.log('patched index.tsx image style');
