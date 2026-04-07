import { useRouter } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { ActionButton, AppScreen, Badge, InfoCard, Reveal } from '@/components/pwa/Ui';
import { palette, typography } from '@/src/theme';

const STEPS = [
  {
    title: '1. Identifier les Domaines / Secteurs',
    text: "La Base documentaire est organisée selon une Structure arborescente et une Nomenclature précise des activités.",
  },
  {
    title: '2. Atteindre le Thème',
    text: "Passez par le Domaine d'intérêt économique et naviguez à travers le Secteur, parfois même un Sous-secteur pour atterrir sur le Thème exact (ex : Transport > Transport terrestre).",
  },
  {
    title: '3. Consulter les articles / documents',
    text: "Trouvez l'information pertinente. Chaque Thème comporte plusieurs Articles classés pour produire une Connaissance.",
  },
  {
    title: '4. Lire la Fiche Article',
    text: "Le Document qui couvre un seul sujet se présente d'abord avec un Extrait, suivi du texte de synthèse résumé en ciblant l'Essentiel et mettant en évidence les Chiffres clés.",
  },
];

export default function ModeEmploiScreen() {
  const router = useRouter();

  return (
    <AppScreen title="Mode d'emploi" subtitle="Une présentation basée sur la nomenclature des activités">
      <Reveal>
        <InfoCard tone="highlight" title="Notre démarche" subtitle="Simplicité et efficacité">
          <View style={styles.badges}>
            <Badge text="Guidé" />
            <Badge text="Centré métier" />
            <Badge text="Immédiat" />
          </View>
          <Text style={styles.text}>Comment se présente notre Base documentaire ? La consultation s'effectue par une structure arborescente allant du Domaine au Thème (allant de 1 à 3 niveaux de parents) pour produire l'information pertinente menant à la décision.</Text>
        </InfoCard>
      </Reveal>

      {STEPS.map((step, index) => (
        <Reveal key={step.title} delay={70 + index * 40}>
          <InfoCard key={step.title} title={step.title}>
            <Text style={styles.text}>{step.text}</Text>
          </InfoCard>
        </Reveal>
      ))}

      <Reveal delay={250}>
        <InfoCard title="Autres modes d'accès">
          <Text style={styles.text}>
            <Text style={{ fontWeight: '700' }}>Naviguer par Recherche : </Text>
            Utilisez la barre de recherche globale pour retrouver rapidement des documents par mots-clés, titres, ou critères spécifiques.{'\n\n'}
            <Text style={{ fontWeight: '700' }}>Naviguer par Séries : </Text>
            Regroupez vos lectures en consultant les documents transverses d'une même série ou collection éditoriale (ex. Fichier Entreprises, Combien ça coûte).
          </Text>
        </InfoCard>
      </Reveal>

      <ActionButton label="Accéder à la base" onPress={() => router.push('/e2-orientation')} />
      <ActionButton label="Directement vers les secteurs" variant="secondary" onPress={() => router.push('/e3-secteurs')} />
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
  badges: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
});
