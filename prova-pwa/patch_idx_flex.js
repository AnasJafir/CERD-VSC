const fs = require('fs');

let file_path = 'app/index.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "logoImage: { flex: 1, width: '100%',\n    width: '100%',\n    height: '100%', borderRadius: 20, resizeMode: 'contain',\n  },",
  "logoImage: {\n    flex: 1,\n    width: '100%',\n    height: '100%',\n    borderRadius: 20,\n    resizeMode: 'contain',\n  },"
);

fs.writeFileSync(file_path, file_code);
console.log('patched index.tsx image property duplication fixed');
