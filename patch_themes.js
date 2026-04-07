const fs = require('fs');

let content = fs.readFileSync('prova-pwa/app/e4-themes.tsx', 'utf8');

// Import getFullBreadcrumbsForTheme
content = content.replace(
  "import { getArticlesByTheme, getSectorById, getThemesBySector } from '@/src/data/catalog';",
  "import { getArticlesByTheme, getSectorById, getThemesBySector, getFullBreadcrumbsForTheme } from '@/src/data/catalog';"
);

content = content.replace(
  "import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';",
  "import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';\nimport { ScrollView, Pressable } from 'react-native';"
);

// Replace Breadcrumbs
const newBreadcrumb = `      <Reveal>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{marginBottom: 16, paddingHorizontal: 8}}>
          <View style={{flexDirection: 'row', alignItems: 'center'}}>
            <Pressable onPress={() => router.push('/e2-orientation')}>
              <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>Orientation</Text>
            </Pressable>
            <Text style={{color: palette.textMuted}}>{' > '}</Text>
            {getFullBreadcrumbsForTheme(themes[0].id).slice(0, -1).map((crumb, idx, arr) => (
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

content = content.replace(
  /<Reveal>\s*<Breadcrumbs[\s\S]*?\]\}\s*\/>\s*<\/Reveal>/,
  newBreadcrumb
);

// Add "Retour à l'orientation"
content = content.replace(
  /<ActionButton label="Retour secteurs" variant="ghost" onPress=\{\(\) => router\.push\('\/e3-secteurs'\)\} \/>/,
  `<ActionButton label="Retour à l'orientation" onPress={() => router.push('/e2-orientation')} />\n      <ActionButton label="Retour secteurs" onPress={() => router.push('/e3-secteurs')} />`
);

fs.writeFileSync('prova-pwa/app/e4-themes.tsx', content);

console.log("Updated e4-themes.tsx successfully");
