const fs = require('fs');

let file_path = 'prova-pwa/app/e1-home.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "const CERD_LOGO = require('../assets/images/logo-cerd.png');",
  "const CHIFFRES_CLES = require('../assets/images/chiffres-cles.png');"
);

file_code = file_code.replace(
  '<View style={styles.logoWrap}>\n            <Image source={CERD_LOGO} style={styles.logoImage} resizeMode="contain" />\n          </View>',
  `<View style={styles.imageWrap}>\n            <Image source={CHIFFRES_CLES} style={styles.chiffresClesImage} resizeMode="cover" />\n          </View>`
);

file_code = file_code.replace(
  /logoWrap: \{[\s\S]*?\},/,
  `imageWrap: {
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
  },`
);

file_code = file_code.replace(
  /logoImage: \{[\s\S]*?\},/,
  `chiffresClesImage: {
    width: '100%', // Prend toute la largeur disponible
    height: 180, // Ajustez la hauteur selon les proportions
    borderRadius: 20, // Arrondi intérieur
  },`
);

fs.writeFileSync(file_path, file_code);
console.log('e1-home.tsx part 2 patched');

