const fs = require('fs');
const path = require('path');

const targetPath = path.join(__dirname, 'prova-pwa/app/e7-recherche.tsx');

let content = fs.readFileSync(targetPath, 'utf-8');

// Update availableThemes to support Domaine direct
content = content.replace(
  `  const availableThemes = useMemo(() => {
    if (selectedSousSecteur) {
      return TAXONOMY.themes.filter(t => t.type_parent === 'Sous_Secteur' && t.parent_ref === selectedSousSecteur);
    }
    if (selectedSecteur) {
      return TAXONOMY.themes.filter(t => t.type_parent === 'Secteur' && t.parent_ref === selectedSecteur);
    }
    return [];
  }, [selectedSecteur, selectedSousSecteur]);`,
  `  const availableThemes = useMemo(() => {
    if (selectedSousSecteur) {
      return TAXONOMY.themes.filter(t => t.type_parent === 'Sous_Secteur' && t.parent_ref === selectedSousSecteur);
    }
    if (selectedSecteur) {
      return TAXONOMY.themes.filter(t => t.type_parent === 'Secteur' && t.parent_ref === selectedSecteur);
    }
    if (selectedDomaine) {
      return TAXONOMY.themes.filter(t => t.type_parent === 'Domaine' && t.parent_ref === selectedDomaine);
    }
    return [];
  }, [selectedDomaine, selectedSecteur, selectedSousSecteur]);`
);

// Update render logic in JSX for Secteur
content = content.replace(
  `          {/* SECTEURS */}
          {selectedDomaine && (
            <>
              <Text style={styles.filterTitle}>Secteur</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
                <FilterChip label="Tous" active={!selectedSecteur} onPress={() => handleSecteurChange(undefined)} />
                {availableSecteurs.map(s => (
                  <FilterChip key={s.code} label={s.nom} active={selectedSecteur === s.code} onPress={() => handleSecteurChange(s.code)} />
                ))}
              </ScrollView>
            </>
          )}`,
  `          {/* SECTEURS */}
          {selectedDomaine && availableSecteurs.length > 0 && (
            <>
              <Text style={styles.filterTitle}>Secteur</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
                <FilterChip label="Tous" active={!selectedSecteur} onPress={() => handleSecteurChange(undefined)} />
                {availableSecteurs.map(s => (
                  <FilterChip key={s.code} label={s.nom} active={selectedSecteur === s.code} onPress={() => handleSecteurChange(s.code)} />
                ))}
              </ScrollView>
            </>
          )}`
);

// Update render logic for Themes
content = content.replace(
  `          {/* THEMES */}
          {selectedSecteur && availableThemes.length > 0 && (
            <>
              <Text style={styles.filterTitle}>Thème</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>`,
  `          {/* THEMES */}
          {((selectedDomaine && availableThemes.length > 0) || (selectedSecteur && availableThemes.length > 0) || (selectedSousSecteur && availableThemes.length > 0)) && (
            <>
              <Text style={styles.filterTitle}>Thème</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>`
);

fs.writeFileSync(targetPath, content, 'utf-8');
console.log('e7 patched for dynamic visibility');
