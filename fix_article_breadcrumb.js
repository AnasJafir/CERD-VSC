const fs = require('fs');

let content = fs.readFileSync('prova-pwa/app/e6-article.tsx', 'utf8');

const startStr = "<View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>";
const endStr = "<Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>{theme.label}</Text>\n            </Pressable>\n          </View>";

const startIdx = content.indexOf(startStr);
const endIdx = content.indexOf(endStr);

if (startIdx !== -1 && endIdx !== -1) {
  const toReplace = content.substring(startIdx, endIdx + endStr.length);
  
  const newBreadcrumb = `<View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>
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
          </View>`;

  content = content.replace(toReplace, newBreadcrumb);
  
  if (!content.includes('getFullBreadcrumbsForTheme')) {
      content = content.replace(
        "import { getArticleById, getSectorById, getThemeById } from '@/src/data/catalog';",
        "import { getArticleById, getSectorById, getThemeById, getFullBreadcrumbsForTheme } from '@/src/data/catalog';"
      );
  }

  fs.writeFileSync('prova-pwa/app/e6-article.tsx', content);
  console.log("Updated e6-article.tsx successfully");
} else {
  console.log("Could not find start/end", startIdx, endIdx);
}
