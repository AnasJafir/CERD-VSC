const fs = require('fs');

// 1. Update catalog.ts
let catalog = fs.readFileSync('prova-pwa/src/data/catalog.ts', 'utf8');
if (!catalog.includes('getFullBreadcrumbsForTheme')) {
  catalog += `
import { TAXONOMY } from './fullTaxonomy';
export function getFullBreadcrumbsForTheme(themeId: string) {
  const theme = TAXONOMY.themes.find(t => t.code === themeId);
  if (!theme) return [];

  let domaine;
  let secteur;
  let sousSecteur;

  if (theme.type_parent === 'Sous_Secteur') {
    sousSecteur = TAXONOMY.sous_secteurs.find(ss => ss.code === theme.parent_ref);
    if (sousSecteur) {
      secteur = TAXONOMY.secteurs.find(s => s.code === sousSecteur.parent_secteur);
      if (secteur) {
        domaine = TAXONOMY.domaines.find(d => d.code === secteur.parent_domaine);
      }
    }
  } else if (theme.type_parent === 'Secteur') {
    secteur = TAXONOMY.secteurs.find(s => s.code === theme.parent_ref);
    if (secteur) {
      domaine = TAXONOMY.domaines.find(d => d.code === secteur.parent_domaine);
    }
  }

  const breadcrumbs = [];
  if (domaine) breadcrumbs.push({ type: 'domaine', label: domaine.nom, id: domaine.code });
  if (secteur) breadcrumbs.push({ type: 'secteur', label: secteur.nom, id: secteur.code });
  if (sousSecteur) breadcrumbs.push({ type: 'sousSecteur', label: sousSecteur.nom, id: sousSecteur.code });
  breadcrumbs.push({ type: 'theme', label: theme.nom, id: theme.code });

  return breadcrumbs;
}
`;
  fs.writeFileSync('prova-pwa/src/data/catalog.ts', catalog);
}

// 2. Update e6-article.tsx
let content = fs.readFileSync('prova-pwa/app/e6-article.tsx', 'utf8');
content = content.replace(
  "import { getArticleById, getSectorById, getThemeById } from '@/src/data/catalog';",
  "import { getArticleById, getSectorById, getThemeById, getFullBreadcrumbsForTheme } from '@/src/data/catalog';"
);

const oldBreadcrumbMatch = content.match(/<View style=\{\{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8\}\}>[\s\S]*?<\/Text>\n\s*<\/View>\n\s*\)\) : null\}[\s\S]*?<\/Text>\n\s*<\/View>/);

if (oldBreadcrumbMatch) {
  content = content.replace(oldBreadcrumbMatch[0], 
`<View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>
            <Pressable onPress={() => router.push('/e2-orientation')}>
              <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>Orientation</Text>
            </Pressable>
            <Text style={{color: palette.textMuted}}>{' > '}</Text>
            
            {getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => (
              <View key={'crumb'+idx} style={{flexDirection: 'row', alignItems: 'center'}}>
                 <Pressable onPress={() => router.push('/e3-secteurs')}>
                   <Text style={{fontFamily: typography.body, color: idx === arr.length - 1 ? palette.textStrong : palette.brand, fontWeight: idx === arr.length - 1 ? 'normal' : 'bold'}}>{crumb.label}</Text>
                 </Pressable>
                 {idx < arr.length - 1 && <Text style={{color: palette.textMuted}}>{' > '}</Text>}
              </View>
            ))}
          </View>`);
}

content = content.replace(
  /<ActionButton label="Retour accueil" onPress=\{\(\) => router\.push\('\/'\)\} \/>/,
  `<ActionButton label="Retour à l'orientation" onPress={() => router.push('/e2-orientation')} />\n            <ActionButton label="Retour accueil" onPress={() => router.push('/')} />`
);
fs.writeFileSync('prova-pwa/app/e6-article.tsx', content);

// 3. Update e5-articles.tsx
let articlesContent = fs.readFileSync('prova-pwa/app/e5-articles.tsx', 'utf8');

articlesContent = articlesContent.replace(
  "import {\n  getArticlesByTheme,\n  getSectorById,\n  getThemeById,\n  SERIES,\n} from '@/src/data/catalog';",
  "import {\n  getArticlesByTheme,\n  getSectorById,\n  getThemeById,\n  SERIES,\n  getFullBreadcrumbsForTheme\n} from '@/src/data/catalog';"
);

articlesContent = articlesContent.replace(
  "import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';",
  "import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';\nimport { ScrollView, Pressable } from 'react-native';"
);

// We replace Breadcrumbs inside E5ArticlesScreen
const newBreadcrumbsCode = `<Reveal>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{marginBottom: 16, paddingHorizontal: 8}}>
          <View style={{flexDirection: 'row', alignItems: 'center'}}>
            <Pressable onPress={() => router.push('/e2-orientation')}>
              <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>Orientation</Text>
            </Pressable>
            <Text style={{color: palette.textMuted}}>{' > '}</Text>
            {getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => (
              <View key={'crumb'+idx} style={{flexDirection: 'row', alignItems: 'center'}}>
                 <Pressable onPress={() => router.push('/e3-secteurs')}>
                   <Text style={{fontFamily: typography.body, color: idx === arr.length - 1 ? palette.textStrong : palette.brand, fontWeight: idx === arr.length - 1 ? 'normal' : 'bold'}}>{crumb.label}</Text>
                 </Pressable>
                 {idx < arr.length - 1 && <Text style={{color: palette.textMuted}}>{' > '}</Text>}
              </View>
            ))}
          </View>
        </ScrollView>
      </Reveal>`;

articlesContent = articlesContent.replace(
  /<Reveal>\s*<Breadcrumbs[\s\S]*?\]\}\s*\/>\s*<\/Reveal>/,
  newBreadcrumbsCode
);

fs.writeFileSync('prova-pwa/app/e5-articles.tsx', articlesContent);

console.log("Files updated successfully");
