const fs = require('fs');
let code = fs.readFileSync('app/e6-article.tsx', 'utf8');

const regex = /<Breadcrumbs items=\{\[\s*\{\s*label:\s*'Orientation'.*?\]\}\s*\/>\s*<Text style=\{styles\.sourceHeader\}>/s;

const replacement = \<Breadcrumbs items={[
            { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
            ...getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => ({ 
              label: crumb.label,
              onPress: idx < arr.length - 1
                ? () => router.push('/e3-secteurs')
                : () => router.push({ pathname: '/e5-articles', params: { themeId: theme.id } })
            }))
          ]} />
        </ScrollView>
      </Reveal>

      <Reveal delay={80}>
        <InfoCard title="Corps du document" style={styles.articleCard}>

          {article.source && (
            <Text style={styles.sourceHeader}>\;

if (regex.test(code)) {
    code = code.replace(regex, replacement);
    fs.writeFileSync('app/e6-article.tsx', code, 'utf8');
    console.log('Fixed e6');
} else {
    console.log('Target string not found in e6-article.tsx!');
}
