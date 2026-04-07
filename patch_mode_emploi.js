const fs = require('fs');

let p = 'prova-pwa/app/mode-emploi.tsx';
let txt = fs.readFileSync(p, 'utf8');

let newSteps = `const STEPS = [
  {
    title: '1. Repérer son Domaine',
    text: "La base est structurée d'abord par grands Domaines (ex: Infrastructures, Économie).",
  },
  {
    title: '2. Choisir un Secteur (et Sous-secteur)',
    text: "En dessous du Domaine, identifiez le secteur d'activité économique précis.",
  },
  {
    title: '3. Ouvrir un Thème',
    text: "Chaque secteur mène vers des thèmes précis. Sélectionnez celui qui correspond à votre besoin.",
  },
  {
    title: '4. Consulter la liste des articles',
    text: "Chaque thème contient un ensemble d'articles. Ouvrez le titre qui vous intéresse.",
  },
  {
    title: '5. Naviguer et retrouver',
    text: "Vous pouvez utilisez la recherche globale, ou le fil d'Ariane en en-tête d'article pour revenir à n'importe quel niveau parent.",
  },
];`;

txt = txt.replace(/const STEPS = \[\s*\{[\s\S]*?\}\s*\];/g, newSteps);

fs.writeFileSync(p, txt);
console.log('Mode d emploi update complete');
