const fs = require('fs');
const path = require('path');

const parsedDataPath = path.join(__dirname, '..', 'config', 'parsed_data.json');
const outPath = path.join(__dirname, '..', 'prova-pwa', 'src', 'data', 'fullTaxonomy.ts');

const data = JSON.parse(fs.readFileSync(parsedDataPath, 'utf8'));

let tsContent = `// Auto-generated full taxonomy from parsed_data.json

export interface TaxonomyTheme {
  code: string;
  nom: string;
  type_parent: string;
  parent_ref: string;
}

export interface TaxonomySubSector {
  code: string;
  nom: string;
  parent_secteur: string;
  parent_domaine: string;
}

export interface TaxonomySector {
  code: string;
  nom: string;
  parent_domaine: string;
}

export interface TaxonomyDomain {
  code: string;
  nom: string;
}

export const TAXONOMY = {
  domaines: ${JSON.stringify(data.domaines, null, 2)} as TaxonomyDomain[],
  secteurs: ${JSON.stringify(data.secteurs, null, 2)} as TaxonomySector[],
  sous_secteurs: ${JSON.stringify(data.sous_secteurs, null, 2)} as TaxonomySubSector[],
  themes: ${JSON.stringify(data.themes, null, 2)} as TaxonomyTheme[],
};
`;

fs.writeFileSync(outPath, tsContent);
console.log('Full taxonomy generated at ' + outPath);
