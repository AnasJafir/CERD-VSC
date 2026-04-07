const fs = require('fs');

let mode_p = 'app/mode-emploi.tsx';
let mode_code = fs.readFileSync(mode_p, 'utf8');

let top_part = mode_code.substring(0, mode_code.indexOf('const STEPS '));
let bottom_part = mode_code.substring(mode_code.indexOf('export default function'));

let newSteps = `const STEPS = [
  {
    title: '1. Identifier les Domaines / Secteurs',
    text: "La Base documentaire est organisée selon une Structure arborescente et une Nomenclature précise des activités.",
  },
  {
    title: '2. Atteindre le Thème',
    text: "Passez par le Domaine d'intérêt économique et naviguez à travers le Secteur, parfois même un Sous-secteur pour atterrir sur le Thème exact (ex : Transport > Transport terrestre).",
  },
  {
    title: '3. Consulter les articles / documents',
    text: "Trouvez l'information pertinente. Chaque Thème comporte plusieurs Articles classés pour produire une Connaissance.",
  },
  {
    title: '4. Lire la Fiche Article',
    text: "Le Document qui couvre un seul sujet se présente d'abord avec un Extrait, suivi du texte de synthèse résumé en ciblant l'Essentiel et mettant en évidence les Chiffres clés.",
  },
];\n\n`;

fs.writeFileSync(mode_p, top_part + newSteps + bottom_part);
console.log('mode-emploi.tsx successfully patched!!');

