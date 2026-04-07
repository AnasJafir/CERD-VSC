import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, Badge, InfoCard, Reveal } from '@/components/pwa/Ui';
import { palette, typography } from '@/src/theme';

export default function AProposScreen() {
  const router = useRouter();

  return (
    <AppScreen  title="A propos" subtitle="Ce que propose la base documentaire CERD, et pour qui.">
      <Reveal>
        <InfoCard
          tone="highlight"
          
          title="De quoi s agit-il ?"
          subtitle="Une base documentaire economique orientee decision, d abord sur le Maroc."
        >
          <Text style={styles.text}>
            Avec un smartphone et l application mobile, l utilisateur accede en 2 ou 3 clics a des informations sectorielles utiles, structurees et lisibles.
          </Text>
          <View style={styles.badgesRow}>
            <Badge text="2-3 clics" />
            <Badge text="Un sujet par document" variant="neutral" />
            <Badge text="Une page utile" variant="neutral" />
          </View>
        </InfoCard>
      </Reveal>

      <Reveal delay={80}>
        <InfoCard title="Public vise" subtitle="Cadres, dirigeants, analystes, journalistes, chercheurs">
          <Text style={styles.text}>
            La promesse est simple: reduire le temps de recherche, mettre en avant les chiffres cles, et guider vers le bon document sans jargon technique.
          </Text>
        </InfoCard>
      </Reveal>

      <Reveal delay={130}>
        <InfoCard title="Qualite editoriale" subtitle="Sources lisibles, droits d auteur respectes">
          <Text style={styles.text}>
            Les informations sont extraites de rapports et publications, puis synthetisees. Les documents sources restent consultables quand ils sont disponibles.
          </Text>
        </InfoCard>
      </Reveal>

      <ActionButton label="Continuer vers le mode d emploi" onPress={() => router.push('/mode-emploi')} />
      <ActionButton label="Entrer directement dans la base" variant="secondary" onPress={() => router.push('/e2-orientation')} />
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  text: {
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
    color: palette.textBody,
  },
  badgesRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 4,
  },
});
