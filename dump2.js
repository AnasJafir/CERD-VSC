const fs = require('fs');

let file_path = 'scripts/export_public_catalog_for_pwa.py';
let script_content = fs.readFileSync(file_path, 'utf8');

console.log(script_content.substring(script_content.indexOf('def load_taxonomy'), script_content.indexOf('def build_live_catalog') + 2000));
