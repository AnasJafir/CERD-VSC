const fs = require('fs');

// 1. Fix e4-themes.tsx
let contentE4 = fs.readFileSync('app/e4-themes.tsx', 'utf8');
const searchE4 = /<Reveal>[\s\n]*<ScrollView horizontal showsHorizontalScrollIndicator={false}.*?<\/ScrollView>[\s\n]*<\/Reveal>/s;
contentE4 = contentE4.replace(searchE4, `<Reveal delay={50}>
        <Breadcrumbs items={[
          { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
          ...getFullBreadcrumbsForTheme(themes[0].id).slice(0, -1).map((crumb, idx, arr) => ({
            label: crumb.label,
            onPress: idx < arr.length - 1 ? () => router.push('/e3-secteurs') : undefined
          }))
        ]} />
      </Reveal>`);
fs.writeFileSync('app/e4-themes.tsx', contentE4, 'utf8');

// 2. Fix e5-articles.tsx
let contentE5 = fs.readFileSync('app/e5-articles.tsx', 'utf8');
const searchE5 = /<Reveal>[\s\n]*<ScrollView horizontal showsHorizontalScrollIndicator={false}.*?<\/ScrollView>[\s\n]*<\/Reveal>/s;
contentE5 = contentE5.replace(searchE5, `<Reveal delay={50}>
        <Breadcrumbs items={[
          { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
          ...getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => ({
            label: crumb.label,
            onPress: idx < arr.length - 1 ? () => router.push('/e3-secteurs') : undefined
          }))
        ]} />
      </Reveal>`);
fs.writeFileSync('app/e5-articles.tsx', contentE5, 'utf8');

// 3. Fix e6-article.tsx
let contentE6 = fs.readFileSync('app/e6-article.tsx', 'utf8');
const searchE6 = /<View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>(.*?)<\/View>/s;
contentE6 = contentE6.replace(searchE6, `<Breadcrumbs items={[
            { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
            ...getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => ({
              label: crumb.label,
              onPress: idx < arr.length - 1 
                ? () => router.push('/e3-secteurs') 
                : () => router.push({ pathname: '/e5-articles', params: { themeId: theme.id } })
            })),
            { label: 'Article', onPress: undefined }
          ]} />`);
fs.writeFileSync('app/e6-article.tsx', contentE6, 'utf8');

console.log('Finished');