const fs = require('fs');

// Fix e6-article.tsx
let pwa_p = 'prova-pwa/app/e6-article.tsx';
let pwa_code = fs.readFileSync(pwa_p, 'utf8');

// The regex might have missed the keyFigures. Let's do string replacement.
let keyFigBlock = `          {article.keyFigures && article.keyFigures.length > 0 ? (
            <View style={styles.metricsContainer}>
              {article.keyFigures.map((fig, idx) => (
                <View key={\`fig-\${idx}\`} style={styles.metricRow}>
                  <Markdown style={metricMarkdownStyles}>{fig.value}</Markdown> 
                  <Markdown style={legendMarkdownStyles}>{fig.legend}</Markdown>
                </View>
              ))}
            </View>
          ) : null}`;

pwa_code = pwa_code.replace(keyFigBlock, '');

// Fix interactive breadcrumb since it failed earlier too
let oldHeader = `<View style={styles.headerContainer}>
          <Text style={styles.headerSector}>{sector.label}</Text>
          <Text style={styles.headerTheme}>{theme.label}</Text>
        </View>`;

let nb = `<View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>
          <Pressable onPress={() => router.push('/')}>
            <Text style={{fontFamily: typography.body, fontSize: 16, color: palette.brand, fontWeight: 'bold'}}>Accueil</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          {sector.description ? (
             <Text style={{fontFamily: typography.body, fontSize: 16, color: palette.textMuted}}>{sector.description.replace(/Domaine[:\\s]*/, '')}</Text>
          ) : null}
          {sector.description ? <Text style={{color: palette.textMuted}}> > </Text> : null}
          <Pressable onPress={() => router.push({ pathname: '/e3-thematiques', params: { sectorId: sector.id } })}>
            <Text style={{fontFamily: typography.body, fontSize: 16, color: palette.brand, fontWeight: 'bold'}}>{sector.label}</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          <Pressable onPress={() => router.push({ pathname: '/e5-articles', params: { themeId: theme.id } })}>
            <Text style={{fontFamily: typography.body, fontSize: 16, color: palette.brand, fontWeight: 'bold'}}>{theme.label}</Text>
          </Pressable>
        </View>`;

pwa_code = pwa_code.replace(oldHeader, nb);

// Add missing backticks to numbers in the excerpt (just wrap them in code tags so they get the markdown style)
let oldExcerpt = `<Markdown style={markdownStyles}>
                {article.excerpt}
              </Markdown>`;
let newExcerpt = `<Markdown style={markdownStyles}>
                {article.excerpt.replace(/(\\d+(?:[,.]\\d+)?\\s*(?:milliards?|millions?)\\s*(?:d['’]\\s*)?(?:€|\\$|DH|MAD|EUR|USD|heure|heures|%)(?:\\s*\\d+)?)/gi, '\\`$1\\`')}
              </Markdown>`;
pwa_code = pwa_code.replace(oldExcerpt, newExcerpt);

// Fix bullet points with inline dashes (- ) in content not breaking visually
// We force newline before dashes that aren't at the start of a string or already after a newline
let oldContent = `{String(article.content).replace(/\\\\r\\\\n/g, '\\n')}`;
let newContent = `{String(article.content).replace(/\\\\r\\\\n/g, '\\n').replace(/(?<!^)(?<!\\n)\\s+- /g, '\\n\\n- ')}`;
pwa_code = pwa_code.replace(oldContent, newContent);

fs.writeFileSync(pwa_p, pwa_code);
console.log('e6-article.tsx cleaned up');
