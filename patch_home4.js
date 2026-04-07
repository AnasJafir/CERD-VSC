const fs = require('fs');
const path = require('path');

const targetPath = path.join(__dirname, 'prova-pwa/app/index.tsx');

let content = fs.readFileSync(targetPath, 'utf8');

const authorBlock = `
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
                Auteur d'ouvrages de référence liés au Maroc (L'ONCF de l'an 2000, Les Retraites: Crise, enjeux & perspectives). Enseignant-formateur en Économie et Gestion.
              </Text>
              <Text style={styles.authorContact}>
                Contact : 061.78.80.00 | arifsadek42@gmail.com
              </Text>
            </View>
          </View>
        </Reveal>`;

if (content.includes('</View></Reveal>')) {
  content = content.replace(
    `          </Text>
        </View></Reveal>`,
    `          </Text>
        </View></Reveal>
${authorBlock}`
  );
}

const stylesInjection = `  footerStage: {`;

const newStyles = `  authorCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginTop: 24,
    marginBottom: 8,
    width: '100%',
    maxWidth: 500,
    borderWidth: 1,
    borderColor: palette.border,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 10,
    elevation: 2,
  },
  authorHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  authorTitleWrap: {
    marginLeft: 12,
  },
  authorName: {
    fontFamily: typography.display,
    fontSize: 20,
    fontWeight: '700',
    color: palette.brandDark,
  },
  authorRole: {
    fontFamily: typography.body,
    fontSize: 14,
    color: palette.textMuted,
  },
  authorContent: {
    marginTop: 4,
  },
  authorBio: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 22,
    color: palette.textBody,
    marginBottom: 12,
  },
  authorContact: {
    fontFamily: typography.body,
    fontSize: 14,
    fontWeight: '600',
    color: palette.textBody,
    marginTop: 4,
  },
  footerStage: {`;

if (content.includes(stylesInjection)) {
  content = content.replace(stylesInjection, newStyles);
}

fs.writeFileSync(targetPath, content, 'utf-8');
console.log('Author block appended!');
