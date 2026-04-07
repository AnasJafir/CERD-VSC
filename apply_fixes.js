const fs = require('fs');

// Fix e6-article.tsx
let pwa_p = 'prova-pwa/app/e6-article.tsx';
let pwa_code = fs.readFileSync(pwa_p, 'utf8');

// The new breadcrumb should look like:
// Domaine: Constructions. BTP & Immobilier | Grands travaux & Réalisations. | Ponts et Tunnels
// We'll replace the simple text headers with interactive breadcrumbs

let interactiveBreadcrumb = `
        <View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>
          <Pressable onPress={() => router.push('/')}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>Accueil</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          {sector.description ? (
             <Text style={{fontFamily: typography.body, color: palette.textMuted}}>{sector.description.replace('Domaine: ', '')}</Text>
          ) : null}
          {sector.description ? <Text style={{color: palette.textMuted}}> > </Text> : null}
          <Pressable onPress={() => router.push('/e3-thematiques?sectorId=' + sector.id)}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>{sector.label}</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          <Pressable onPress={() => router.push('/e5-articles?themeId=' + theme.id)}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>{theme.label}</Text>
          </Pressable>
        </View>
`;

pwa_code = pwa_code.replace(/<View style=\{styles\.headerContainer\}>[\s\S]*?<\/View>/, interactiveBreadcrumb);

// Remove the keyFigures section
let keyFigRegex = /\{\s*article\.keyFigures[\s\S]*?\}\s*\):\s*null\s*\}/;
pwa_code = pwa_code.replace(keyFigRegex, '');

// Preprocess excerpt to style numbers correctly if it has inline code backticks, or just use same markdown styles
pwa_code = pwa_code.replace(
`<Markdown style={markdownStyles}>
                {article.excerpt}`,
`<Markdown style={markdownStyles}>
                {article.excerpt.replace(/(\d+(?:,\d+)?\s*(?:milliards?|millions?)?\s*(?:d['’]\s*)?(?:€|\$|dh|mad|eur|usd|h|heure|heures|%)(?:\s*\d+)?)/gi, '\`$1\`')}`
);

// Fix bullet points (replace inline dashes with proper newline and bullet for markdown)
pwa_code = pwa_code.replace(
`{String(article.content).replace(/\\\\r\\\\n/g, '\\n')}`,
`{String(article.content).replace(/\\\\r\\\\n/g, '\\n').replace(/(?<=^|\\n)\\s*-\\s/g, '\\n- ')}`
);

fs.writeFileSync(pwa_p, pwa_code);
console.log('e6-article.tsx updated');

// Build _layout.tsx fix for Home/Search buttons
let layout_p = 'prova-pwa/app/_layout.tsx';
let layout_code = fs.readFileSync(layout_p, 'utf8');

// I need to add global buttons to the header or the screen wrapper. Wait, let's see how _layout is structured.
