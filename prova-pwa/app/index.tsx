import { useRouter } from 'expo-router';
import { useEffect, useRef } from 'react';
import { Animated, Easing, Image, StyleSheet, Text, View, Pressable, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

import { Reveal } from '@/components/pwa/Ui';
import { palette, typography } from '@/src/theme';

const CHIFFRES_CLES = require('../assets/images/chiffres-cles-new.png');

export default function LandingScreen() {
  const router = useRouter();
  const glow = useRef(new Animated.Value(0)).current;
  const floatLogo = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    const glowLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(glow, {
          toValue: 1,
          duration: 2500,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
        Animated.timing(glow, {
          toValue: 0,
          duration: 2500,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: true,
        }),
      ]),
    );

    const logoFloatLoop = Animated.loop(
      Animated.sequence([
        Animated.timing(floatLogo, {
          toValue: 1,
          duration: 3000,
          easing: Easing.inOut(Easing.cubic),
          useNativeDriver: true,
        }),
        Animated.timing(floatLogo, {
          toValue: 0,
          duration: 3000,
          easing: Easing.inOut(Easing.cubic),
          useNativeDriver: true,
        }),
      ]),
    );

    glowLoop.start();
    logoFloatLoop.start();

    return () => {
      glowLoop.stop();
      logoFloatLoop.stop();
    };
  }, [floatLogo, glow]);

  const glowScale = glow.interpolate({
    inputRange: [0, 1],
    outputRange: [0.95, 1.05],
  });

  const glowOpacity = glow.interpolate({
    inputRange: [0, 1],
    outputRange: [0.1, 0.3],
  });

  const logoDriftY = floatLogo.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -10],
  });

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer} showsVerticalScrollIndicator={false}>
      <View style={styles.container}>
        <Reveal delay={100}><View style={styles.centerStage}>
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

        <Reveal delay={250}>
          <View style={styles.authorCard}>
            <View style={styles.authorHeader}>
              <Ionicons name="person-circle-outline" size={48} color={palette.brandDark} />
              <View style={styles.authorTitleWrap}>
                <Text style={styles.authorName}>Qui est M. ARIF Sadek ?</Text>
                <Text style={styles.authorRole}>Directeur & Fondateur</Text>
              </View>
            </View>
            <View style={styles.authorContent}>
              <Text style={styles.authorBio}>
                Ingénieur principal Hc ONCF à la retraite. Ancien Directeur administratif et financier puis Directeur général de la SCIF. DECS. Expert-comptable.
              </Text>
              <Text style={styles.authorBio}>
                <Text style={{fontWeight: '700'}}>Consultant / Éditeur :</Text>
                {"\n"}Directeur de publication (Revue "Entreprise & Gestion").
                {"\n"}Auteur d'ouvrages de référence liés au Maroc (L'ONCF de l'an 2000, Les Retraites: Crise, enjeux & perspectives). Enseignant-formateur en Économie et Gestion.
              </Text>
              <Text style={styles.authorContact}>
                Contact : 061.78.80.00 | arifsadek42@gmail.com
              </Text>
            </View>
          </View>
        </Reveal>
      </View></Reveal>

      <Reveal delay={400}><View style={styles.footerStage}>
        <Pressable 
          style={({ pressed }) => [styles.primaryButton, pressed && styles.primaryButtonPressed]}
          onPress={() => router.push('/e2-orientation')}
        >
          <Text style={styles.primaryButtonText}>Accéder à la base</Text>
          <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginLeft: 8 }} />
        </Pressable>



        <Pressable
          style={({ pressed }) => [styles.secondaryButton, pressed && styles.secondaryButtonPressed]}
          onPress={() => router.push('/mode-emploi')}
        >
          <Text style={styles.secondaryButtonText}>Mode d'emploi</Text>
        </Pressable>
      </View></Reveal>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
    backgroundColor: palette.bg,
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  centerStage: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    maxWidth: 500,
    width: '100%',
  },
  logoStage: { width: '100%', 
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 160,
    marginBottom: 32,
  },
  logoAura: {
    position: 'absolute',
    width: 220,
    height: 160,
    borderRadius: 110,
    backgroundColor: palette.brandSoft,
  },
  logoPlate: {
    width: '100%',
    height: 200,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: 'rgba(0,0,0,0.05)',
    backgroundColor: palette.surface,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 16,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowOffset: { width: 0, height: 12 },
    shadowRadius: 24,
    elevation: 8,
  },
  logoImage: {
    flex: 1,
    width: '100%',
    height: '100%',
    borderRadius: 20,
    resizeMode: 'contain',
  },
  heroTitle: {
    fontFamily: typography.display,
    fontSize: 42,
    fontWeight: '800',
    color: palette.brandDark,
    marginBottom: 8,
    textAlign: 'center',
    letterSpacing: -0.5,
  },
  heroSubtitle: {
    fontFamily: typography.display,
    fontSize: 20,
    fontWeight: '600',
    color: palette.textBody,
    marginBottom: 16,
    textAlign: 'center',
  },
  heroText: {
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 24,
    color: palette.textMuted,
    textAlign: 'center',
    marginTop: 8,
    paddingHorizontal: 20,
  },
  authorCard: {
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
  footerStage: {
    width: '100%',
    maxWidth: 400,
    paddingBottom: 40,
  },
  primaryButton: {
    backgroundColor: palette.brandDark,
    paddingVertical: 18,
    borderRadius: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 16,
    elevation: 4,
    marginBottom: 16,
  },
  primaryButtonPressed: {
    opacity: 0.9,
    transform: [{ scale: 0.98 }],
  },
  primaryButtonText: {
    color: '#ffffff',
    fontFamily: typography.body,
    fontWeight: '700',
    fontSize: 18,
    letterSpacing: 0.5,
  },
  secondaryButton: {
    backgroundColor: palette.surfaceAlt,
    paddingVertical: 16,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: palette.border,
  },
  secondaryButtonPressed: {
    backgroundColor: palette.surfaceStrong,
    transform: [{ scale: 0.98 }],
  },
  secondaryButtonText: {
    color: palette.textMuted,
    fontFamily: typography.body,
    fontWeight: '600',
    fontSize: 16,
  },
});


