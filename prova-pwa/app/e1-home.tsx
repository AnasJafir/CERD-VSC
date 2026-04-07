import { useRouter } from 'expo-router';
import { Image, StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, InfoCard, Reveal } from '@/components/pwa/Ui';
import { palette, typography } from '@/src/theme';

const CHIFFRES_CLES = require('../assets/images/chiffres-cles-new.png');

export default function E1HomeScreen() {
  const router = useRouter();

  return (
        <AppScreen
      title="Base Documentaire"
      subtitle="L'Essentiel en Chiffres, au bout du Smartphone."
    >
      <Reveal>
        <InfoCard
          tone="highlight"
          title="De quoi s'agit-il d'abord ?"
          subtitle="Un projet eG initié par M. Sadek ARIF"    
        >
          <View style={styles.imageWrap}>
            <Image source={CHIFFRES_CLES} style={styles.chiffresClesImage} resizeMode="contain" />
          </View>
          <Text style={styles.text}>
            "eG" est une Base documentaire à caractère économique qui s'intéresse d'abord au Maroc et vise spécialement les Cadres et Dirigeants.
          </Text>
          <Text style={styles.text}>
            Muni de votre Smartphone, accédez directement à tout un ensemble d'informations couvrant tous les Secteurs d'activité économique.
          </Text>
          <Text style={styles.text}>
            Un seul sujet par Document présenté dans une seule page couvrant l'Essentiel, toujours avec des Chiffres clés faciles à mémoriser.
          </Text>
        </InfoCard>
      </Reveal>

      <Reveal delay={80}>
        <InfoCard title="Démarrage rapide" subtitle="Naviguer et explorer">
          <ActionButton label="Mode d'emploi" onPress={() => router.push('/mode-emploi')} />
          <ActionButton label="Accéder à la Base de données" variant="secondary" onPress={() => router.push('/e2-orientation')} />
          <ActionButton label="À propos du projet" variant="secondary" onPress={() => router.push('/a-propos')} />
        </InfoCard>
      </Reveal>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  imageWrap: { width: '100%', 
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 24, // Bords arrondis
    borderWidth: 2,
    borderColor: '#e0c87b',
    backgroundColor: '#fff',
    padding: 4,
    marginBottom: 16,
    // Ombre
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 6, // Pour Android
    overflow: 'hidden',
  },
  chiffresClesImage: {
    width: '100%', // Prend toute la largeur disponible
    height: 200, // Ajustez la hauteur selon les proportions
    borderRadius: 20, // Arrondi intérieur
  },
  text: {
    fontFamily: typography.body,
    fontSize: 15,
    lineHeight: 22,
    color: palette.textBody,
    marginBottom: 6,
  },
  textMuted: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 20,
    color: palette.textMuted,
  },
});
