const fs = require('fs');

let home_p = 'prova-pwa/app/e1-home.tsx';
let home_code = fs.readFileSync(home_p, 'utf8');

let newAppScreen = `    <AppScreen
      title="Base Documentaire"
      subtitle="L'Essentiel en Chiffres, au bout du Smartphone."
    >
      <Reveal>
        <InfoCard
          tone="highlight"
          title="De quoi s'agit-il d'abord ?"
          subtitle="Un projet eG initié par M. Sadek ARIF"    
        >
          <View style={styles.logoWrap}>
            <Image source={CERD_LOGO} style={styles.logoImage} resizeMode="contain" />
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
    </AppScreen>`;

home_code = home_code.replace(/<AppScreen[\s\S]*<\/AppScreen>/, newAppScreen);

fs.writeFileSync(home_p, home_code);
console.log('e1-home.tsx patched');


let mode_p = 'prova-pwa/app/mode-emploi.tsx';
let mode_code = fs.readFileSync(mode_p, 'utf8');

let newSteps = `const STEPS = [
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
];`;

mode_code = mode_code.replace(/const STEPS = \[\s*\{[\s\S]*?\}\s*\];/, newSteps);

mode_code = mode_code.replace(
`<Text style={styles.text}>La consultation s'effectue pas à pas pour vous garantir la meilleure pertinence des informations.</Text>`,
`<Text style={styles.text}>Comment se présente notre Base documentaire ? La consultation s'effectue par une structure arborescente allant du Domaine au Thème (allant de 1 à 3 niveaux de parents) pour produire l'information pertinente menant à la décision.</Text>`
);

mode_code = mode_code.replace(
`subtitle="Mise en main rapide et navigation guidée."`,
`subtitle="Une présentation basée sur la nomenclature des activités"`
);

// Eliminate terms like "optionnel" if any exist
fs.writeFileSync(mode_p, mode_code);
console.log('mode-emploi.tsx patched');

