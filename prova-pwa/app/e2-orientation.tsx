import { useRouter } from 'expo-router';
import { Text, StyleSheet } from 'react-native';

import { ActionButton, AppScreen, InfoCard, Reveal } from '@/components/pwa/Ui';
import { palette, typography } from '@/src/theme';

export default function E2OrientationScreen() {
  const router = useRouter();

  return (
    <AppScreen
      
      title="Orientation"
      subtitle="Choisissez votre porte d acces a l information."
    >
      <Reveal>
        <InfoCard tone="highlight"  title="Commencer par un domaine" subtitle="Parcours hiérarchique : Domaine > Secteur > Sous-Secteur > Thème.">
          <Text style={styles.text}>
            Naviguez à travers l'arborescence de la Base Documentaire selon notre nomenclature (même les domaines sans articles y figurent).
          </Text>
          <ActionButton label="Ouvrir les domaines" onPress={() => router.push('/e3-secteurs')} />
        </InfoCard>
      </Reveal>

      <Reveal delay={90}>
        <InfoCard title="Entrer par serie" subtitle="Acces direct aux corpus editoriaux">
          <Text style={styles.text}>Combien ca coute ?, Fichier Entreprises et Publications eG restent accessibles en un geste.</Text>
          <ActionButton label="Voir les series" onPress={() => router.push('/series')} />
        </InfoCard>
      </Reveal>

      <Reveal delay={140}>
        <InfoCard title="Recherche par mots-cles" subtitle="Mode direct par sujet, source ou expression">
          <Text style={styles.text}>Utilisez les mots-cles avec filtrage par secteur.</Text>
          <ActionButton label="Aller a la recherche" onPress={() => router.push('/e7-recherche')} />
          <ActionButton label="Retour a l accueil" onPress={() => router.push('/')} />
        </InfoCard>
      </Reveal>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  text: {
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
    color: palette.textBody,
    marginBottom: 6,
  },
});
