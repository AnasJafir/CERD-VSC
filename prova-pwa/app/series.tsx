import { useState } from 'react';
import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, Badge, InfoCard, Reveal } from '@/components/pwa/Ui';
import { ARTICLES, SERIES, getArticlesBySeries } from '@/src/data/catalog';
import { palette, typography } from '@/src/theme';

export default function SeriesScreen() {
  const router = useRouter();
  const [expandedSeries, setExpandedSeries] = useState<Record<string, boolean>>({});

  const toggleSeries = (code: string) => {
    setExpandedSeries(prev => ({
      ...prev,
      [code]: !prev[code]
    }));
  };

  return (
    <AppScreen

      title="Séries"
      subtitle="Accès direct aux grandes familles éditoriales"
    >
      {SERIES.map((series, index) => {
        const items = getArticlesBySeries(series.code);
        const firstArticle = items[0];
        return (
          <Reveal key={series.code} delay={60 + index * 45}>
            <InfoCard key={series.code} title={series.label} subtitle={`${items.length} article(s)`}>
              <View style={styles.badgesRow}>
                <Badge text={series.code.toUpperCase()}  />
              </View>
              <Text style={styles.text}>Entrée de lecture rapide pour consulter une sélection cohérente d'articles.</Text>
              
              {items.length > 0 ? (
                <View style={{ marginTop: 12 }}>
                  <ActionButton
                    label={expandedSeries[series.code] ? "Masquer les articles" : "Voir les articles"}
                    variant="primary"
                    onPress={() => toggleSeries(series.code)}
                  />
                  {expandedSeries[series.code] && (
                    <View style={{ marginTop: 12, marginLeft: 8, paddingLeft: 8, borderLeftWidth: 2, borderLeftColor: palette.border }}>
                      {items.map((article) => (
                        <ActionButton
                          key={article.id}
                          label={article.title}
                          variant="secondary"
                          onPress={() =>
                            router.push({
                              pathname: '/e6-article',
                              params: { articleId: article.id },
                            })
                          }
                        />
                      ))}
                    </View>
                  )}
                </View>
              ) : (
                <Text style={[styles.text, { marginTop: 8, fontStyle: 'italic' }]}>Aucun article disponible pour cette série.</Text>
              )}
            </InfoCard>
          </Reveal>
        );
      })}

      <InfoCard title="Navigation" subtitle="Options de parcours">
        <ActionButton label="Retour à l'orientation" onPress={() => router.push('/e2-orientation')} />
        <ActionButton label="Retour à l'accueil" onPress={() => router.push('/')} />
      </InfoCard>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  badgesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 4,
  },
  text: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
    color: palette.textBody,
    marginBottom: 6,
  },
});
