const fs = require('fs');
let file_path = 'prova-pwa/app/index.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "const CERD_LOGO = require('../assets/images/logo-cerd.png');",
  "const CHIFFRES_CLES = require('../assets/images/chiffres-cles.png');"
);

// We need to change the content of LandingScreen
file_code = file_code.replace(/<View style=\{styles\.centerStage\}>[\s\S]*?<\/View><\/Reveal>/, `<View style={styles.centerStage}>
        <View style={styles.logoStage}>
          <Animated.View
            style={[
              styles.logoAura,
              {
                opacity: glowOpacity,
                transform: [{ scale: glowScale }],
              },
            ]}
          />
          <Animated.View style={[styles.logoPlate, { transform: [{ translateY: logoDriftY }] }]}>
            <Image source={CHIFFRES_CLES} style={styles.logoImage} resizeMode="contain" />
          </Animated.View>
        </View>

        <Text style={styles.heroTitle}>Base Documentaire eG</Text>
        <Text style={styles.heroSubtitle}>Un projet initié par M. Sadek ARIF</Text>
        <Text style={styles.heroText}>
          "eG" est une Base documentaire à caractère économique qui s'intéresse d'abord au Maroc et vise spécialement les Cadres et Dirigeants.
        </Text>
        <Text style={styles.heroText}>
          Muni de votre Smartphone, accédez directement à tout un ensemble d'informations couvrant tous les Secteurs d'activité économique. Un seul sujet par Document présenté dans une seule page couvrant l'Essentiel, toujours avec des Chiffres clés faciles à mémoriser.
        </Text>
      </View></Reveal>`);

file_code = file_code.replace(
  "width: 240,",
  "width: '100%',"
);

file_code = file_code.replace(
  "height: 120,",
  "height: 200,"
);
file_code = file_code.replace(
  "height: 96,",
  "height: '100%', borderRadius: 20,"
);

fs.writeFileSync(file_path, file_code);
console.log('index.tsx patched');
