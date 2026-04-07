const fs = require('fs');

let file_path = 'app/index.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "logoImage: {",
  "logoImage: { flex: 1, width: '100%',"
);

fs.writeFileSync(file_path, file_code);
console.log('patched index.tsx image flex');
