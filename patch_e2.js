const fs = require('fs');

let file_path = 'prova-pwa/app/e2-orientation.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  'Commencer par un secteur',
  'Commencer par un domaine'
);

file_code = file_code.replace(
  'Parcours sectoriel disponible pour tous les profils.',
  'Parcours hiérarchique : Domaine > Secteur > Sous-Secteur > Thème.'
);

file_code = file_code.replace(
  'Vous descendez ensuite vers un theme, puis vers les articles associes.',
  'Naviguez à travers l\'arborescence de la Base Documentaire selon notre nomenclature (même les domaines sans articles y figurent).'
);

file_code = file_code.replace(
  'Ouvrir les secteurs',
  'Ouvrir les domaines'
);

fs.writeFileSync(file_path, file_code);
console.log('e2-orientation.tsx patched for domains');

