const fs = require('fs');

let pwa_p = 'prova-pwa/app/e6-article.tsx';
let pwa_code = fs.readFileSync(pwa_p, 'utf8');

let breadcrumbBlockRegex = /<View style=\{\{flexDirection: 'row'[\s\S]*?<\/View>/;

let newBreadcrumb = `        <View style={{flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', marginBottom: 16, paddingHorizontal: 8}}>
          <Pressable onPress={() => router.push('/')}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>Accueil</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          
          {sector.description ? sector.description.split(' > ').map((crumb, i) => (
             <View key={'crumb'+i} style={{flexDirection: 'row', alignItems: 'center'}}>
               <Text style={{fontFamily: typography.body, color: palette.textMuted}}>{crumb.replace(/Domaine[:\\s]*/, '')}</Text>
               <Text style={{color: palette.textMuted}}> > </Text>
             </View>
          )) : null}
          
          <Pressable onPress={() => router.push({ pathname: '/e3-thematiques', params: { sectorId: sector.id } })}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>{sector.label}</Text>
          </Pressable>
          <Text style={{color: palette.textMuted}}> > </Text>
          
          <Pressable onPress={() => router.push({ pathname: '/e5-articles', params: { themeId: theme.id } })}>
            <Text style={{fontFamily: typography.body, color: palette.brand, fontWeight: 'bold'}}>{theme.label}</Text>
          </Pressable>
        </View>`;

pwa_code = pwa_code.replace(breadcrumbBlockRegex, newBreadcrumb);

fs.writeFileSync(pwa_p, pwa_code);
console.log('Breadcrumb updated in React Native');
