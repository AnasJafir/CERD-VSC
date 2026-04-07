import { useLocalSearchParams, useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';
import { ScrollView, Pressable } from 'react-native';
import {
  getArticlesByTheme,
  getSectorById,
  getThemeById,
  SERIES,
  getFullBreadcrumbsForTheme,
} from '@/src/data/catalog';
import { palette, typography } from '@/src/theme';

function oneParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

function getSeriesLabel(seriesCode: string) {
  const series = SERIES.find((item) => item.code === seriesCode);
  return series ? series.label : seriesCode;
}

export default function E5ArticlesScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ themeId?: string | string[] }>();
  const themeId = oneParam(params.themeId);

  const theme = themeId ? getThemeById(themeId) : undefined;
  const sector = theme ? getSectorById(theme.sectorId) : undefined;
  const articles = themeId ? getArticlesByTheme(themeId) : [];

  if (!themeId || !theme || !sector || articles.length === 0) {
    return (
      <AppScreen  title="Articles" subtitle="Aucun theme valide detecte">
        <InfoCard title="Chemin incomplet" subtitle="Selectionnez d abord un theme.">
          <ActionButton label="Retour themes" onPress={() => router.push('/e3-secteurs')} />
        </InfoCard>
      </AppScreen>
    );
  }

  return (
    <AppScreen
      
      title={theme.label}
      subtitle={`Articles disponibles dans ${sector.label}`}
    >
      <Reveal delay={50}>
        <Breadcrumbs items={[
          { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
          ...getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => ({
            label: crumb.label,
            onPress: idx < arr.length - 1 ? () => router.push('/e3-secteurs') : undefined
          }))
        ]} />
      </Reveal>

      {articles.map((article, index) => (
        <Reveal key={article.id} delay={70 + index * 40}>
          <InfoCard title={article.title} subtitle={`${article.source} | ${article.date || 'Date non renseignee'}`}>
            <View style={styles.badgesRow}>
              <Badge text={getSeriesLabel(article.series)} />
            </View>
            <Text style={styles.excerpt}>{article.excerpt || 'Extrait en cours de preparation.'}</Text>
            <ActionButton
              label="Lire l article"
              onPress={() =>
                router.push({
                  pathname: '/e6-article',
                  params: { articleId: article.id },
                })
              }
            />
          </InfoCard>
        </Reveal>
      ))}

      <ActionButton
        label="Retour à l'orientation"
        onPress={() => router.push('/e2-orientation')}
      />
      <ActionButton
        label="Retour themes"
        onPress={() =>
          router.push({
            pathname: '/e4-themes',
            params: { sectorId: sector.id },
          })
        }
      />
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  badgesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  excerpt: {
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
    color: palette.textBody,
    marginBottom: 5,
  },
});
