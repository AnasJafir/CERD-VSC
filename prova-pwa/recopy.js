const fs = require('fs');
fs.copyFileSync('../Visuels/Chiffres clés.png', 'assets/images/chiffres-cles.png');
console.log('Re-copied image successfully via NodeJS to be fully binary safe.');
