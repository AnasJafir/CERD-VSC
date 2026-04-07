const fs = require('fs');

let file_path = 'prova-pwa/app/e3-secteurs.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  '<AppScreen  title="Secteurs" subtitle="Choisissez le domaine de depart pour reduire le bruit informationnel.">',
  '<AppScreen  title="Domaines et Secteurs" subtitle="Choisissez le domaine de départ pour réduire le bruit informationnel.">'
);

// We need to group by Domain. The current map is:
// {SECTORS.map((sector, index) => { ...
// We can change the mapping to group them by `sector.description` (which holds the Domain).

let newMapCode = `
      {Object.entries(
        SECTORS.reduce((acc, sector) => {
          // In publicCatalog.generated.ts, sector.description is often "Domaine > Secteur" or just "Domaine"
          // Let's use the first part before ' > ' as the Domain name
          const domain = (sector.description || 'Domaine').split(' > ')[0];
          if (!acc[domain]) acc[domain] = [];
          acc[domain].push(sector);
          return acc;
        }, {} as Record<string, typeof SECTORS>)
      ).map(([domain, domainSectors], dIndex) => (
        <View key={domain} style={{ marginBottom: 24 }}>
          <Reveal delay={80 + dIndex * 45}>
            <View style={{ backgroundColor: '#f0f0f0', padding: 12, borderRadius: 8, marginBottom: 12 }}>
              <Text style={{ fontFamily: typography.display, fontSize: 20, color: palette.brand, fontWeight: 'bold' }}>
                {domain}
              </Text>
            </View>
          </Reveal>
          
          {domainSectors.map((sector, sIndex) => {
            const themes = getThemesBySector(sector.id);
            const articles = ARTICLES.filter((article) => article.sectorId === sector.id);
            
            // Extract the sector part from description, or use sector.label
            const sectorName = sector.label;

            return (
              <Reveal key={sector.id} delay={100 + dIndex * 45 + sIndex * 20}>
                <InfoCard title={sectorName}>       
                  <View style={styles.metaRow}>
                    <Badge text={\`\${themes.length} thématique(s)\`} variant="neutral" />  
                    <Badge text={\`\${articles.length} article(s)\`} />
                  </View>
                  <Text style={styles.text}>Accès direct aux thèmes reliés à ce secteur.</Text>
                  <ActionButton
                    label="Explorer ce secteur"
                    onPress={() =>
                      router.push({
                        pathname: '/e4-themes',
                        params: { sectorId: sector.id },
                      })
                    }
                  />
                </InfoCard>
              </Reveal>
            );
          })}
        </View>
      ))}
`;

file_code = file_code.replace(
  /\{SECTORS\.map\(\(sector, index\) => \{[\s\S]*?(?=\s*<\/AppScreen>)/,
  newMapCode
);

fs.writeFileSync(file_path, file_code);
console.log('e3-secteurs.tsx patched with domains');
