const fs = require('fs');
let c = fs.readFileSync('prova-pwa/src/data/catalog.ts', 'utf8');

c = c.replace(/import \{ TAXONOMY \} from '\.\/fullTaxonomy';\n/g, '');
c = c.replace(/import \{ TAXONOMY \} from '\.\/fullTaxonomy';\r\n/g, '');
c = "import { TAXONOMY } from './fullTaxonomy';\n" + c;

fs.writeFileSync('prova-pwa/src/data/catalog.ts', c);
console.log("Updated catalog.ts successfully.");