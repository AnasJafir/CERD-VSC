const fs = require('fs');

let file_path = 'prova-pwa/app/e3-secteurs.tsx';
let newCode = `import { useRouter } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, Text, View, Pressable, ScrollView, LayoutAnimation, UIManager, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { AppScreen, Badge, Breadcrumbs, Reveal } from '@/components/pwa/Ui';
import { ARTICLES } from '@/src/data/catalog';      
import { TAXONOMY } from '@/src/data/fullTaxonomy';
import { palette, typography } from '@/src/theme';

if (Platform.OS === 'android') {
  if (UIManager.setLayoutAnimationEnabledExperimental) {
    UIManager.setLayoutAnimationEnabledExperimental(true);
  }
}

export default function E3SecteursScreen() {
  const router = useRouter();
  
  // States for accordions
  const [expandedDomains, setExpandedDomains] = useState<Record<string, boolean>>({});
  const [expandedSectors, setExpandedSectors] = useState<Record<string, boolean>>({});
  const [expandedSubSectors, setExpandedSubSectors] = useState<Record<string, boolean>>({});

  const toggleDomain = (code: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedDomains(prev => ({ ...prev, [code]: !prev[code] }));
  };

  const toggleSector = (code: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedSectors(prev => ({ ...prev, [code]: !prev[code] }));
  };

  const toggleSubSector = (code: string) => {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setExpandedSubSectors(prev => ({ ...prev, [code]: !prev[code] }));
  };

  // Safe slugify helper for TS IDs equivalent to Python's slugify
  const slugify = (text: string) => {
    return text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  };

  const renderTheme = (theme: typeof TAXONOMY.themes[0], level: number) => {
    // Only count articles for this theme
    const themeId = \`th-\${slugify(theme.code || 'theme')}\`;
    const count = ARTICLES.filter(a => a.themeId === themeId).length;

    return (
      <View key={'th-'+theme.code} style={[styles.accordionItem, { paddingLeft: level * 16 }]}>
        <Pressable 
          style={({ pressed }) => [styles.accordionHeader, styles.themeHeader, pressed && { opacity: 0.7 }]}
          onPress={() => router.push({ pathname: '/e5-articles', params: { themeId } })}
        >
          <View style={{flex: 1, flexDirection: 'row', alignItems: 'center'}}>
           <Ionicons name="document-text-outline" size={18} color={palette.textBody} style={{marginRight: 8}} />
           <Text style={styles.themeLabel}>{theme.nom}</Text>
          </View>
          <Badge text={\`\${count} article(s)\`} variant={count > 0 ? "warm" : "neutral"} />
        </Pressable>
      </View>
    );
  };

  return (
    <AppScreen  title="Explorateur de Domaines" subtitle="Naviguez au travers de l'arborescence complète de la Base B3D.">
      <Reveal>
        <Breadcrumbs
          items={[
            { label: 'Accueil', onPress: () => router.push('/e1-home') },       
            { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
            { label: 'Domaines' },
          ]}
        />
      </Reveal>

      <View style={{ marginTop: 8, paddingBottom: 40 }}>
        {TAXONOMY.domaines.map((domain, dIndex) => {
          const isDomainExpanded = !!expandedDomains[domain.code];
          const sectors = TAXONOMY.secteurs.filter(s => s.parent_domaine === domain.code);
          
          return (
            <Reveal key={'dom-'+domain.code} delay={80 + dIndex * 30}>
              <View style={styles.accordionContainer}>
                <Pressable 
                  style={styles.accordionHeader} 
                  onPress={() => toggleDomain(domain.code)}
                >
                  <Text style={styles.domainLabel}>{domain.nom}</Text>
                  <Ionicons name={isDomainExpanded ? "chevron-up" : "chevron-down"} size={20} color={palette.brand} />
                </Pressable>
                
                {isDomainExpanded && (
                  <View style={styles.accordionContent}>
                    {sectors.length === 0 && <Text style={styles.emptyText}>Aucun secteur défini.</Text>}
                    {sectors.map((sector) => {
                      const isSectorExpanded = !!expandedSectors[sector.code];
                      const subSectors = TAXONOMY.sous_secteurs.filter(ss => ss.parent_secteur === sector.code);
                      const sectorThemes = TAXONOMY.themes.filter(t => t.type_parent.toLowerCase() === 'secteur' && t.parent_ref === sector.code);
                      
                      return (
                        <View key={'sec-'+sector.code} style={styles.accordionItem}>
                          <Pressable 
                            style={[styles.accordionHeader, { paddingLeft: 16, backgroundColor: '#fdfbf2' }]} 
                            onPress={() => toggleSector(sector.code)}
                          >
                            <Text style={styles.sectorLabel}>{sector.nom}</Text>
                            <Ionicons name={isSectorExpanded ? "chevron-up" : "chevron-down"} size={18} color={palette.textBody} />
                          </Pressable>

                          {isSectorExpanded && (
                           <View style={styles.accordionContent}>
                             {subSectors.map(subSector => {
                               const isSubExpanded = !!expandedSubSectors[subSector.code];
                               const subThemes = TAXONOMY.themes.filter(t => t.type_parent.toLowerCase() === 'sous_secteur' && t.parent_ref === subSector.code);
                               return (
                                 <View key={'ss-'+subSector.code} style={styles.accordionItem}>
                                    <Pressable 
                                      style={[styles.accordionHeader, { paddingLeft: 32, backgroundColor: '#fafafa' }]} 
                                      onPress={() => toggleSubSector(subSector.code)}
                                    >
                                      <Text style={styles.subSectorLabel}>{subSector.nom}</Text>
                                      <Ionicons name={isSubExpanded ? "chevron-up" : "chevron-down"} size={16} color={palette.textMuted} />
                                    </Pressable>
                                    
                                    {isSubExpanded && (
                                      <View style={styles.accordionContent}>
                                        {subThemes.length === 0 && <Text style={[styles.emptyText, {paddingLeft: 48}]}>Aucun thème.</Text>}
                                        {subThemes.map(theme => renderTheme(theme, 3))}
                                      </View>
                                    )}
                                 </View>
                               );
                             })}
                             
                             {/* Themes directly under sector */}
                             {sectorThemes.map(theme => renderTheme(theme, 2))}
                             
                             {subSectors.length === 0 && sectorThemes.length === 0 && 
                                <Text style={[styles.emptyText, {paddingLeft: 32}]}>Aucun sous-secteur ni thème.</Text>
                             }
                           </View>
                          )}
                        </View>
                      );
                    })}
                  </View>
                )}
              </View>
            </Reveal>
          );
        })}
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  accordionContainer: {
    backgroundColor: '#fff',
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#eee',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  accordionItem: {
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  accordionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
  },
  domainLabel: {
    fontFamily: typography.display,
    fontSize: 16,
    fontWeight: '700',
    color: palette.brand,
    flex: 1,
    paddingRight: 16,
  },
  sectorLabel: {
    fontFamily: typography.body,
    fontSize: 15,
    fontWeight: '600',
    color: palette.textStrong,
    flex: 1,
    paddingRight: 16,
  },
  subSectorLabel: {
    fontFamily: typography.body,
    fontSize: 14,
    fontWeight: '500',
    color: palette.textBody,
    flex: 1,
    paddingRight: 16,
  },
  themeHeader: {
    backgroundColor: '#fff',
    paddingVertical: 12,
  },
  themeLabel: {
    fontFamily: typography.body,
    fontSize: 14,
    color: palette.textBody,
    flex: 1,
  },
  accordionContent: {
    backgroundColor: '#fafafa',
  },
  emptyText: {
    fontFamily: typography.body,
    fontSize: 13,
    color: palette.textMuted,
    fontStyle: 'italic',
    padding: 16,
  }
});
`;

fs.writeFileSync(file_path, newCode);
console.log('e3-secteurs.tsx completely rewritten as Full Accordion');
