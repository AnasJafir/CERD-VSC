import { useLocalSearchParams, useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';
import { ScrollView, Pressable } from 'react-native';
import { getArticlesByTheme, getSectorById, getThemesBySector, getFullBreadcrumbsForTheme } from '@/src/data/catalog';
import { palette, typography } from '@/src/theme';

function oneParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default function E4ThemesScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ sectorId?: string | string[] }>();
  const sectorId = oneParam(params.sectorId);

  const sector = sectorId ? getSectorById(sectorId) : undefined;
  const themes = sectorId ? getThemesBySector(sectorId) : [];

  if (!sectorId || !sector || themes.length === 0) {
    return (
      <AppScreen  title="Themes" subtitle="Aucun secteur valide detecte">
        <InfoCard title="Chemin incomplet" subtitle="Reprenez la selection du secteur.">
          <Text style={styles.text}>Cette etape depend du secteur choisi precedemment.</Text>
          <ActionButton label="Choisir un secteur" onPress={() => router.push('/e3-secteurs')} />
        </InfoCard>
      </AppScreen>
    );
  }

  return (
    <AppScreen
      
      title={sector.label}
      subtitle="Selectionnez un theme pour afficher la liste des articles."
    >
            <Reveal delay={50}>
        <Breadcrumbs items={[
          { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
          ...getFullBreadcrumbsForTheme(themes[0].id).slice(0, -1).map((crumb, idx, arr) => ({
            label: crumb.label,
            onPress: idx < arr.length - 1 ? () => router.push('/e3-secteurs') : undefined
          }))
        ]} />
      </Reveal>

      {themes.map((theme, index) => {
        const articleCount = getArticlesByTheme(theme.id).length;

        return (
          <Reveal key={theme.id} delay={70 + index * 40}>
            <InfoCard title={theme.label} subtitle="Un sujet unique par article pour une lecture nette.">
              <View style={styles.badgesRow}>
                <Badge text={`${articleCount} article(s)`}  />
              </View>
              <ActionButton
                label="Voir les articles"
                onPress={() =>
                  router.push({
                    pathname: '/e5-articles',
                    params: { themeId: theme.id },
                  })
                }
              />
            </InfoCard>
          </Reveal>
        );
      })}

      <ActionButton label="Retour à l'orientation" onPress={() => router.push('/e2-orientation')} />
      <ActionButton label="Retour secteurs" onPress={() => router.push('/e3-secteurs')} />
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
    color: palette.textMuted,
  },
});
