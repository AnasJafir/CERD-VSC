const fs = require('fs');
const path = require('path');

const targetPath = path.join(__dirname, 'prova-pwa/app/index.tsx');
let content = fs.readFileSync(targetPath, 'utf8');

// 1. Remove the "À propos de l'Auteur" button safely
const btnToRemove = `        <Pressable
          style={({ pressed }) => [styles.secondaryButton, pressed && styles.secondaryButtonPressed]}
          onPress={() => router.push('/a-propos')}
        >
          <Text style={styles.secondaryButtonText}>À propos de l'Auteur</Text>
        </Pressable>`;
if (content.includes(btnToRemove)) {
  content = content.replace(btnToRemove, '');
}

// 2. Add the author Card after the project definition text
const hookString = `        <Text style={styles.heroText}>
          Muni de votre Smartphone, accédez directement à tout un ensemble d'informations couvrant tous les Secteurs d'activité économique. Un seul sujet par Document présenté dans une seule page couvrant l'Essentiel, toujours avec des Chiffres clés faciles à mémoriser.
        </Text>`;

const authorBlock = `        <Text style={styles.heroText}>
          Muni de votre Smartphone, accédez directement à tout un ensemble d'informations couvrant tous les Secteurs d'activité économique. Un seul sujet par Document présenté dans une seule page couvrant l'Essentiel, toujours avec des Chiffres clés faciles à mémoriser.
        </Text>

        <Reveal delay={250}>
          <View style={styles.authorCard}>
            <View style={styles.authorHeader}>
              <Ionicons name="person-circle-outline" size={48} color={palette.brandDark} />
              <View style={styles.authorTitleWrap}>
                <Text style={styles.authorName}>M. ARIF Sadek</Text>
                <Text style={styles.authorRole}>Directeur & Fondateur</Text>
              </View>
            </View>
            <View style={styles.authorContent}>
              <Text style={styles.authorBio}>
                Ingénieur principal Hc ONCF à la retraite. Ancien Directeur administratif et financier puis Directeur général de la SCIF. DECS. Expert-comptable.
              </Text>
              <Text style={styles.authorBio}>
                <Text style={{fontWeight: '700'}}>Expérience :</Text> Public-Privé / Finance-Industrie / Édition.
                {"\\n"}• 1964-1980 : ONCF Direction financière (Ing. principal)
                {"\\n"}• 1980-1997 : SCIF (DAF puis DG, 650 personnes)
                {"\\n"}• Partenariats internationaux : Gec-Alsthom, De Dietrich, Fauvet Girel, Ganz...
              </Text>
              <Text style={styles.authorBio}>
                <Text style={{fontWeight: '700'}}>Consultant / Éditeur :</Text>
                {"\\n"}Directeur de publication (Revue "Entreprise & Gestion").
                {"\\n"}Auteur d'ouvrages de référence liés au Maroc (L'ONCF de l'an 2000, Les Retraites: Crise, enjeux & perspectives). Enseignant-formateur en Économie et Gestion.
              </Text>
              <Text style={styles.authorContact}>
                Contact : 061.78.80.00 | arifsadek42@gmail.com
              </Text>
            </View>
          </View>
        </Reveal>`;

if (content.includes(hookString) && !content.includes('M. ARIF Sadek</Text>')) {
  content = content.replace(hookString, authorBlock);
}

fs.writeFileSync(targetPath, content, 'utf8');
console.log('index.tsx patched with Author block!');