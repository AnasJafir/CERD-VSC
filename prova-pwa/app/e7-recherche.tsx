import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View, ScrollView } from 'react-native';

import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';
import { searchArticles, SERIES, SearchFilters, SeriesCode } from '@/src/data/catalog';
import { TAXONOMY } from '@/src/data/fullTaxonomy';
import { palette, typography } from '@/src/theme';

function oneParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default function E7RechercheScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ sectorId?: string | string[] }>();
  const sectorFromRoute = oneParam(params.sectorId);

  const [query, setQuery] = useState('');
  
  const [selectedDomaine, setSelectedDomaine] = useState<string | undefined>(undefined);
  const [selectedSecteur, setSelectedSecteur] = useState<string | undefined>(undefined);
  const [selectedSousSecteur, setSelectedSousSecteur] = useState<string | undefined>(undefined);
  const [selectedTheme, setSelectedTheme] = useState<string | undefined>(undefined);
  const [selectedSeries, setSelectedSeries] = useState<SeriesCode | undefined>(undefined);

  useEffect(() => {
    if (sectorFromRoute) {
      setSelectedSecteur(sectorFromRoute);
      const sec = TAXONOMY.secteurs.find(s => s.code === sectorFromRoute);
      if (sec) {
        setSelectedDomaine(sec.parent_domaine);
      }
    }
  }, [sectorFromRoute]);

  // Derived lists
  const availableSecteurs = useMemo(() => {
    if (!selectedDomaine) return [];
    return TAXONOMY.secteurs.filter(s => s.parent_domaine === selectedDomaine);
  }, [selectedDomaine]);

  const availableSousSecteurs = useMemo(() => {
    if (!selectedSecteur) return [];
    return TAXONOMY.sous_secteurs.filter(s => s.parent_secteur === selectedSecteur);
  }, [selectedSecteur]);

  const availableThemes = useMemo(() => {
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
  }, [selectedDomaine, selectedSecteur, selectedSousSecteur]);

  // When changing parents, reset children
  const handleDomaineChange = (val?: string) => {
    setSelectedDomaine(val);
    setSelectedSecteur(undefined);
    setSelectedSousSecteur(undefined);
    setSelectedTheme(undefined);
  };
  
  const handleSecteurChange = (val?: string) => {
    setSelectedSecteur(val);
    setSelectedSousSecteur(undefined);
    setSelectedTheme(undefined);
  };

  const handleSousSecteurChange = (val?: string) => {
    setSelectedSousSecteur(val);
    setSelectedTheme(undefined);
  };

  const results = useMemo(() => {
    const filters: SearchFilters = {
      domaineCode: selectedDomaine,
      secteurCode: selectedSecteur,
      sousSecteurCode: selectedSousSecteur,
      themeCode: selectedTheme,
      series: selectedSeries,
    };
    return searchArticles(query, filters);
  }, [query, selectedDomaine, selectedSecteur, selectedSousSecteur, selectedTheme, selectedSeries]);

  const mapThemeCodeToId = (code: string) => {
    // The new signature takes themeId, but visually we use code. If your themes array in catalog.ts 
    // uses the code as ID, or we let the search filter resolve it. For now, we pass code.
    return code;
  };

  return (
    <AppScreen title="Recherche" subtitle="Recherche globale et filtres en cascade.">
      <Reveal>
        <Breadcrumbs
          items={[
            { label: 'Accueil', onPress: () => router.push('/') },
            { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
            { label: 'Recherche' },
          ]}
        />
      </Reveal>

      <Reveal delay={45}>
        <InfoCard tone="highlight" title="Rechercher" subtitle="Tapez un mot-clé, une source, etc.">
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Ex: tunnel, ciment..."
            placeholderTextColor={palette.textMuted}
            style={styles.input}
          />
        </InfoCard>
      </Reveal>

      <Reveal delay={95}>
        <InfoCard title="Filtres Croisés" subtitle="Séléctionnez dans l'ordre pour réduire le périmètre.">
          
          {/* DOMAINES */}
          <Text style={styles.filterTitle}>Domaine</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
            <FilterChip label="Tous" active={!selectedDomaine} onPress={() => handleDomaineChange(undefined)} />
            {TAXONOMY.domaines.map(d => (
              <FilterChip key={d.code} label={d.nom} active={selectedDomaine === d.code} onPress={() => handleDomaineChange(d.code)} />
            ))}
          </ScrollView>

          {/* SECTEURS */}
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
          )}

          {/* SOUS-SECTEURS */}
          {selectedSecteur && availableSousSecteurs.length > 0 && (
            <>
              <Text style={styles.filterTitle}>Sous-Secteur</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
                <FilterChip label="Tous" active={!selectedSousSecteur} onPress={() => handleSousSecteurChange(undefined)} />
                {availableSousSecteurs.map(ss => (
                  <FilterChip key={ss.code} label={ss.nom} active={selectedSousSecteur === ss.code} onPress={() => handleSousSecteurChange(ss.code)} />
                ))}
              </ScrollView>
            </>
          )}

          {/* THEMES */}
          {((selectedDomaine && availableThemes.length > 0) || (selectedSecteur && availableThemes.length > 0) || (selectedSousSecteur && availableThemes.length > 0)) && (
            <>
              <Text style={styles.filterTitle}>Thème</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
                <FilterChip label="Tous" active={!selectedTheme} onPress={() => setSelectedTheme(undefined)} />
                {availableThemes.map(t => (
                  <FilterChip key={t.code} label={t.nom} active={selectedTheme === t.code} onPress={() => setSelectedTheme(t.code)} />
                ))}
              </ScrollView>
            </>
          )}

          {/* SERIES */}
          <Text style={[styles.filterTitle, { marginTop: 8 }]}>Série</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollWrap}>
            <FilterChip label="Toutes" active={!selectedSeries} onPress={() => setSelectedSeries(undefined)} />
            {SERIES.map((serie) => (
              <FilterChip key={serie.code} label={serie.label} active={selectedSeries === serie.code} onPress={() => setSelectedSeries(serie.code as SeriesCode)} />
            ))}
          </ScrollView>

        </InfoCard>
      </Reveal>

      <Reveal delay={130}>
        <InfoCard title={`Résultats (${results.length})`} subtitle="Articles correspondants.">
          {results.length === 0 ? (
            <Text style={styles.empty}>Aucun résultat pour cette combinaison de recherche et filtres.</Text>
          ) : (
            results.map((article) => (
              <View key={article.id} style={styles.resultRow}>
                <View style={styles.resultBadges}>
                  <Badge text={article.source} />
                </View>
                <Text style={styles.resultTitle}>{article.title}</Text>
                <Text style={styles.resultMeta}>{article.date || 'Date non renseignée'}</Text>
                <Text style={styles.resultExcerpt}>{article.excerpt || '...'}</Text>
                <ActionButton
                  label="Ouvrir l'article"
                  onPress={() =>
                    router.push({
                      pathname: '/e6-article',
                      params: { articleId: article.id },
                    })
                  }
                />
              </View>
            ))
          )}
        </InfoCard>
      </Reveal>
    </AppScreen>
  );
}

type FilterChipProps = {
  label: string;
  active: boolean;
  onPress: () => void;
};

function FilterChip({ label, active, onPress }: FilterChipProps) {
  return (
    <Pressable onPress={onPress} style={[styles.chip, active ? styles.chipActive : null]}>
      <Text style={[styles.chipText, active ? styles.chipTextActive : null]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: palette.border,
    borderRadius: 12,
    minHeight: 46,
    paddingHorizontal: 12,
    fontFamily: typography.body,
    fontSize: 15,
    color: palette.textStrong,
    backgroundColor: '#fffef8',
  },
  scrollWrap: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  filterTitle: {
    fontFamily: typography.display,
    fontSize: 13,
    color: palette.textBody,
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  chip: {
    borderWidth: 1,
    borderColor: palette.border,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 8,
    backgroundColor: '#fffef8',
  },
  chipActive: {
    backgroundColor: '#f6dc88',
    borderColor: '#d3ad47',
  },
  chipText: {
    fontFamily: typography.body,
    fontSize: 13,
    color: palette.textBody,
  },
  chipTextActive: {
    color: '#5f4b00',
    fontWeight: 'bold',
  },
  empty: {
    fontFamily: typography.body,
    fontSize: 14,
    color: palette.textMuted,
  },
  resultRow: {
    borderWidth: 1,
    borderColor: palette.border,
    borderRadius: 14,
    padding: 11,
    marginBottom: 8,
    backgroundColor: '#fffef8',
  },
  resultBadges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 4,
  },
  resultTitle: {
    fontFamily: typography.display,
    fontSize: 18,
    color: palette.textStrong,
  },
  resultMeta: {
    fontFamily: typography.body,
    fontSize: 12,
    color: palette.textMuted,
    marginBottom: 4,
  },
  resultExcerpt: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
    color: palette.textBody,
    marginBottom: 4,
  },
});
