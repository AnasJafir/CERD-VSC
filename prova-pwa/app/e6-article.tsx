import { useLocalSearchParams, useRouter } from 'expo-router';
import { Image, Linking, Pressable, StyleSheet, Text, View, ScrollView } from 'react-native';
import Markdown, { ASTNode } from 'react-native-markdown-display';

import { ActionButton, AppScreen, Badge, Breadcrumbs, InfoCard, Reveal } from '@/components/pwa/Ui';
import { getArticleById, getSectorById, getThemeById, getFullBreadcrumbsForTheme } from '@/src/data/catalog';
import { palette, typography } from '@/src/theme';

function oneParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

function formatDateToJJMMAAAA(dateStr: string | undefined): string {
  if (!dateStr) return 'Date non renseignée';
  const parts = dateStr.split(/[-/]/);
  if (parts.length === 3) {
    if (parts[0].length === 4) {
      const aaaa = parts[0];
      const mm = parts[1].padStart(2, '0');
      const jj = parts[2].padStart(2, '0');
      return `${jj}-${mm}-${aaaa}`;
    } else {
      const jj = parts[0].padStart(2, '0');
      const mm = parts[1].padStart(2, '0');
      const aaaa = parts[2].length === 2 ? `20${parts[2]}` : parts[2];
      return `${jj}-${mm}-${aaaa}`;
    }
  }
  return dateStr;
}

export default function E6ArticleScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ articleId?: string | string[] }>();
  const articleId = oneParam(params.articleId);

  const article = articleId ? getArticleById(articleId) : undefined;
  const theme = article ? getThemeById(article.themeId) : undefined;
  const sector = theme ? getSectorById(theme.sectorId) : undefined;

  const openSourceDocument = async () => {
    if (!article?.documentUrl) return;
    try {
      await Linking.openURL(article.documentUrl);
    } catch {
      // Ignore
    }
  };

  if (!article || !theme || !sector) {
    return (
      <AppScreen title="Article" subtitle="Introuvable">
        <InfoCard title="Erreur" subtitle="L'article sélectionné n'existe pas.">
          <ActionButton label="Retour à l'orientation" onPress={() => router.push('/e2-orientation')} />
            <ActionButton label="Retour accueil" onPress={() => router.push('/')} />
        </InfoCard>
      </AppScreen>
    );
  }

  return (
    <AppScreen title={article.title} subtitle={`${sector.label} | ${theme.label}`}>
      <Reveal>
        
        <Breadcrumbs items={[
            { label: 'Orientation', onPress: () => router.push('/e2-orientation') },
            ...getFullBreadcrumbsForTheme(theme.id).map((crumb, idx, arr) => ({ 
              label: crumb.label,
              onPress: idx < arr.length - 1
                ? () => router.push('/e3-secteurs')
                : () => router.push({ pathname: '/e5-articles', params: { themeId: theme.id } })
            })),
            { label: 'Document', onPress: undefined }
          ]} />
      </Reveal>

      <Reveal delay={80}>
        <InfoCard title={formatDateToJJMMAAAA(article.date)} style={styles.articleCard}>

          {article.source && (
            <Text style={styles.sourceHeader}>
              Source : {article.source}
            </Text>
          )}

          {article.excerpt ? (
            <View style={styles.excerptContainer}>
              <Markdown style={markdownStyles}>
                {article.excerpt.replace(/(\d+(?:[,.]\d+)?(?:\s*(?:milliards?|millions?))?\s*(?:d['’]\s*)?(?:€|\$|dh|mad|eur|usd|h|heure|heures|%)(?:\s*\d+)?)/gi, String.fromCharCode(96) + '$1' + String.fromCharCode(96))}
              </Markdown>
            </View>
          ) : null}



          {article.visuals && article.visuals.length > 0 ? (
            <View style={styles.visualsContainer}>
              {article.visuals.map((vis, idx) => (
                <Pressable
                  key={`vis-${idx}`} 
                  onPress={() => Linking.openURL(vis.url).catch(() => undefined)}
                  style={styles.visualBlock}
                >
                  <Image style={styles.visualImage} resizeMode="contain" source={{ uri: vis.url }} />
                  {vis.title ? <Text style={styles.visualCaption}>{vis.title}</Text> : null}
                </Pressable>
              ))}
            </View>
          ) : null}

          {article.content ? (
            <View style={styles.contentContainer}>
              <Markdown style={markdownStyles}>
                {String(article.content).replace(/\\r\\n/g, '\n').replace(/ - /g, '\n\n- ')}
              </Markdown>
            </View>
          ) : null}

          {article.documentUrl && (
            <ActionButton 
              label="Consulter le document source d'origine" 
              
              onPress={openSourceDocument}
            />
          )}

        </InfoCard>
      </Reveal>
      
      <ActionButton
        label="Retour aux articles"
        
        onPress={() =>
          router.push({
            pathname: '/e5-articles',
            params: { themeId: theme.id },
          })
        }
      />
    </AppScreen>
  );
}

const markdownStyles = StyleSheet.create({
  body: {
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 25,
    color: palette.textBody,
  },
  // Removed huge strong style
  strong: {
    fontWeight: 'bold',
  },
  heading1: {
    fontFamily: typography.display,
    fontSize: 26,
    fontWeight: '800',
    color: palette.textStrong,
    marginTop: 20,
    marginBottom: 10,
  },
  heading2: {
    fontFamily: typography.display,
    fontSize: 22,
    fontWeight: '700',
    color: palette.textStrong,
    marginTop: 18,
    marginBottom: 8,
  },
  heading3: {
    fontFamily: typography.display,
    fontSize: 28,
    fontWeight: '900',
    color: palette.brand,
    marginTop: 24,
    marginBottom: 6,
  },
  list_item: {
    marginTop: 4,
    marginBottom: 4,
  },
  bullet_list: {
    marginLeft: 0,
  },
  code_inline: {
    fontFamily: typography.display,
    fontSize: 24,
    fontWeight: '800',
    color: palette.brandDark,
    backgroundColor: 'transparent',
    borderWidth: 0,
    padding: 0,
  }
});

const metricMarkdownStyles = StyleSheet.create({
  body: {
    fontFamily: typography.display,
    fontSize: 34,
    fontWeight: '800',
    color: palette.brand,
    lineHeight: 40,
    marginBottom: 4,
  },
  strong: {
    fontWeight: '900',
  }
});

const legendMarkdownStyles = StyleSheet.create({
  body: {
    fontFamily: typography.body,
    fontSize: 16,
    color: palette.textMuted,
    fontWeight: '600',
  },
});

const styles = StyleSheet.create({
  articleCard: {
    padding: 24,
    backgroundColor: '#fff',
  },
  excerptContainer: {
    marginBottom: 20,
    paddingBottom: 20,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
  },
  metricsContainer: {
    marginBottom: 24,
  },
  metricRow: {
    marginBottom: 20,
    paddingLeft: 12,
    borderLeftWidth: 4,
    borderColor: palette.brandSoft,
  },
  visualsContainer: {
    marginBottom: 24,
  },
  visualBlock: {
    marginBottom: 16,
    borderRadius: 8,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: palette.border,
    padding: 8,
    backgroundColor: palette.surfaceAlt,
  },
  visualImage: {
    width: '100%',
    height: 220,
    borderRadius: 4,
  },
  visualCaption: {
    fontFamily: typography.body,
    fontSize: 14,
    color: palette.textMuted,
    marginTop: 8,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  contentContainer: {
    marginBottom: 32,
  },
  headerContainer: {
    marginBottom: 16,
    paddingHorizontal: 8,
  },
  headerSector: {
    fontFamily: typography.display,
    fontSize: 24,
    fontWeight: '800',
    color: palette.brand,
    marginBottom: 4,
  },
  headerTheme: {
    fontFamily: typography.body,
    fontSize: 16,
    fontWeight: '600',
    color: palette.textMuted,
  },
  sourceHeader: {
    fontFamily: typography.body,
    fontSize: 14,
    color: palette.textMuted,
    marginBottom: 16,
    fontStyle: 'italic',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: palette.border,
    paddingBottom: 16,
  },
});


