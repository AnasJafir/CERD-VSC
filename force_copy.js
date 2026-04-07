const fs = require('fs');
const path = require('path');

const srcChiffres = path.join(__dirname, 'Visuels', 'Chiffres clés.png');
const dstChiffres = path.join(__dirname, 'prova-pwa', 'assets', 'images', 'chiffres-cles-new.png');

const srcLogo = path.join(__dirname, 'Visuels', 'Logo_optimisé-removebg-preview.png');
const dstLogo = path.join(__dirname, 'prova-pwa', 'assets', 'images', 'logo-transparent.png');

console.log("Copying Chiffres...");
fs.copyFileSync(srcChiffres, dstChiffres);
console.log("Copying Logo...");
fs.copyFileSync(srcLogo, dstLogo);
console.log("Done copying!");
