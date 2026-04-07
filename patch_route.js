const fs = require('fs');

let ui_p = 'prova-pwa/components/pwa/Ui.tsx';
let ui_code = fs.readFileSync(ui_p, 'utf8');

ui_code = ui_code.replace('/e2-recherche', '/e7-recherche');
fs.writeFileSync(ui_p, ui_code);
console.log('Route fixed');
