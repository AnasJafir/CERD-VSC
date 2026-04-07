import React, { useEffect, useRef } from 'react';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import {
  Animated,
  Easing,
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  ViewStyle,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { palette, typography } from '@/src/theme';

type AppScreenProps = {
  title: string;
  subtitle?: string;
  kicker?: string;
  children: React.ReactNode;
};

type ButtonProps = {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  fullWidth?: boolean;
  disabled?: boolean;
};

type InfoCardProps = {
  title: string;
  subtitle?: string;
  kicker?: string;
  children?: React.ReactNode;
  style?: ViewStyle;
  tone?: 'default' | 'warm' | 'highlight';
};

export type BreadcrumbItem = {
  label: string;
  onPress?: () => void;
};

type RevealProps = {
  children: React.ReactNode;
  delay?: number;
};

type BadgeProps = {
  text: string;
  variant?: 'warm' | 'neutral' | 'dark';
};

type StatPillProps = {
  label: string;
  value: string;
};

export function AppScreen({ title, subtitle, kicker, children }: AppScreenProps) {
  const router = useRouter();
  return (
    <SafeAreaView style={styles.safe}>
      <View style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 24, paddingTop: 12, paddingBottom: 0, zIndex: 1000}}>
        <Pressable onPress={() => router.push('/')}>
            <Image source={require('../../assets/images/logo-transparent.png')} style={{width: 140, height: 65}} resizeMode="contain" />
        </Pressable>
        <View style={{flexDirection: 'row'}}>
          <Pressable onPress={() => router.push('/')} style={{marginRight: 10, backgroundColor: '#fff', padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.05, shadowOffset: {width: 0, height: 2}, shadowRadius: 4}}>
            <Ionicons name="home" size={20} color={palette.brand} />
          </Pressable>
          <Pressable onPress={() => router.push('/e7-recherche')} style={{backgroundColor: '#fff', padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.05, shadowOffset: {width: 0, height: 2}, shadowRadius: 4}}>
            <Ionicons name="search" size={20} color={palette.brand} />
          </Pressable>
        </View>
      </View>
      <View style={styles.backgroundLayer} pointerEvents="none">
        <View style={styles.bgOrbTop} />
        <View style={styles.bgOrbBottom} />
      </View>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {kicker ? <Text style={styles.kicker}>{kicker}</Text> : null}
        <Reveal>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </Reveal>
        <View style={styles.section}>{children}</View>
      </ScrollView>
    </SafeAreaView>
  );
}

export function Reveal({ children, delay = 0 }: RevealProps) {
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(14)).current;

  useEffect(() => {
    const animation = Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 460,
        delay,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 520,
        delay,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]);

    animation.start();
    return () => animation.stop();
  }, [delay, opacity, translateY]);

  return (
    <Animated.View style={{ opacity, transform: [{ translateY }] }}>
      {children}
    </Animated.View>
  );
}

export function ActionButton({
  label,
  onPress,
  variant = 'primary',
  fullWidth = true,
  disabled = false,
}: ButtonProps) {
  const isSecondary = variant === 'secondary';
  const isGhost = variant === 'ghost';

  return (
    <Pressable
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        isGhost ? styles.buttonGhost : isSecondary ? styles.buttonSecondary : styles.buttonPrimary,
        fullWidth ? styles.buttonFullWidth : null,
        disabled ? styles.buttonDisabled : null,
        pressed ? styles.buttonPressed : null,
      ]}
    >
      <Text
        style={[
          styles.buttonText,
          isSecondary || isGhost ? styles.buttonTextSecondary : null,
          disabled ? styles.buttonTextDisabled : null,
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

export function InfoCard({ title, subtitle, kicker, children, style, tone = 'default' }: InfoCardProps) {
  const toneStyle = tone === 'highlight' ? styles.cardHighlight : tone === 'warm' ? styles.cardWarm : styles.cardDefault;

  return (
    <View style={[styles.card, toneStyle, style]}>
      {kicker ? <Text style={styles.cardKicker}>{kicker}</Text> : null}
      <Text style={styles.cardTitle}>{title}</Text>
      {subtitle ? <Text style={styles.cardSubtitle}>{subtitle}</Text> : null}
      {children}
    </View>
  );
}

export function Badge({ text, variant = 'warm' }: BadgeProps) {
  const badgeStyle = variant === 'dark' ? styles.badgeDark : variant === 'neutral' ? styles.badgeNeutral : styles.badgeWarm;
  const badgeTextStyle = variant === 'dark' ? styles.badgeTextDark : styles.badgeText;

  return (
    <View style={[styles.badge, badgeStyle]}>
      <Text style={[styles.badgeText, badgeTextStyle]}>{text}</Text>
    </View>
  );
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  if (!items.length) {
    return null;
  }

  return (
    <View style={styles.breadcrumbRow}>
      {items.map((item, index) => {
        const isLast = index === items.length - 1;
        return (
          <View key={`${item.label}-${index}`} style={styles.breadcrumbItemRow}>
            <Pressable
              onPress={item.onPress}
              disabled={!item.onPress || isLast}
              style={[styles.breadcrumbItem, isLast ? styles.breadcrumbItemCurrent : null]}
            >
              <Text style={[styles.breadcrumbText, isLast ? styles.breadcrumbTextCurrent : null]}>{item.label}</Text>
            </Pressable>
            {!isLast ? <Text style={styles.breadcrumbSeparator}>/</Text> : null}
          </View>
        );
      })}
    </View>
  );
}

export function StatPill({ label, value }: StatPillProps) {
  return (
    <View style={styles.statPill}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: palette.bg,
  },
  backgroundLayer: {
    ...StyleSheet.absoluteFillObject,
  },
  bgOrbTop: {
    position: 'absolute',
    top: -140,
    right: -100,
    width: 320,
    height: 320,
    borderRadius: 180,
    backgroundColor: 'rgba(246, 220, 136, 0.42)',
  },
  bgOrbBottom: {
    position: 'absolute',
    left: -120,
    bottom: -150,
    width: 320,
    height: 320,
    borderRadius: 180,
    backgroundColor: 'rgba(122, 90, 0, 0.14)',
  },
  scrollContent: {
    paddingHorizontal: 18,
    paddingTop: 14,
    paddingBottom: 40,
  },
  section: {
    marginTop: 16,
  },
  kicker: {
    fontFamily: typography.accent,
    fontSize: 11,
    letterSpacing: 0.7,
    textTransform: 'uppercase',
    color: palette.textMuted,
    marginBottom: 8,
  },
  title: {
    fontFamily: typography.display,
    fontSize: 34,
    lineHeight: 39,
    color: palette.textStrong,
    marginBottom: 6,
  },
  subtitle: {
    fontFamily: typography.body,
    fontSize: 16,
    lineHeight: 24,
    color: palette.textBody,
  },
  card: {
    borderColor: palette.border,
    borderWidth: 1,
    borderRadius: 18,
    padding: 15,
    marginBottom: 13,
    shadowColor: '#1a1a1a',
    shadowOpacity: 0.08,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 5 },
    elevation: 3,
  },
  cardDefault: {
    backgroundColor: palette.surface,
  },
  cardWarm: {
    backgroundColor: palette.surfaceAlt,
  },
  cardHighlight: {
    backgroundColor: palette.surfaceStrong,
  },
  cardKicker: {
    fontFamily: typography.accent,
    fontSize: 11,
    letterSpacing: 0.6,
    textTransform: 'uppercase',
    color: palette.brandDark,
    marginBottom: 6,
  },
  cardTitle: {
    fontFamily: typography.display,
    fontSize: 21,
    lineHeight: 27,
    color: palette.textStrong,
    marginBottom: 2,
  },
  cardSubtitle: {
    fontFamily: typography.body,
    fontSize: 14,
    lineHeight: 21,
    color: palette.textMuted,
    marginBottom: 10,
  },
  button: {
    minHeight: 46,
    borderRadius: 13,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
    marginTop: 8,
  },
  buttonPrimary: {
    backgroundColor: palette.brand,
    borderWidth: 1,
    borderColor: '#9d7d00',
  },
  buttonSecondary: {
    backgroundColor: palette.surface,
    borderWidth: 1,
    borderColor: palette.border,
  },
  buttonGhost: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    alignSelf: 'flex-start',
    minHeight: 34,
    paddingHorizontal: 0,
    marginTop: 4,
  },
  buttonFullWidth: {
    width: '100%',
  },
  buttonPressed: {
    opacity: 0.82,
  },
  buttonDisabled: {
    opacity: 0.45,
  },
  buttonText: {
    fontFamily: typography.accent,
    fontSize: 13,
    letterSpacing: 0.35,
    textTransform: 'uppercase',
    color: '#221b00',
  },
  buttonTextSecondary: {
    color: palette.textStrong,
  },
  buttonTextDisabled: {
    color: palette.textMuted,
  },
  badge: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderRadius: 999,
    paddingHorizontal: 11,
    paddingVertical: 5,
    marginRight: 7,
    marginTop: 7,
  },
  badgeWarm: {
    backgroundColor: '#f7e1a0',
    borderColor: '#d4b36a',
  },
  badgeNeutral: {
    backgroundColor: '#f4f0e1',
    borderColor: '#d1c8a8',
  },
  badgeDark: {
    backgroundColor: '#1f2127',
    borderColor: '#1f2127',
  },
  badgeText: {
    fontFamily: typography.accent,
    fontSize: 11,
    letterSpacing: 0.2,
    color: '#5f4700',
  },
  badgeTextDark: {
    color: '#f2ebd4',
  },
  breadcrumbRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  breadcrumbItemRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 4,
    marginBottom: 4,
  },
  breadcrumbItem: {
    backgroundColor: 'rgba(255, 255, 255, 0.72)',
    borderWidth: 1,
    borderColor: palette.border,
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  breadcrumbItemCurrent: {
    backgroundColor: '#f7e3a8',
    borderColor: '#d8b66f',
  },
  breadcrumbText: {
    fontFamily: typography.body,
    fontSize: 12,
    color: palette.textBody,
  },
  breadcrumbTextCurrent: {
    color: '#503d00',
    fontWeight: '600',
  },
  breadcrumbSeparator: {
    marginHorizontal: 6,
    color: palette.textMuted,
    fontFamily: typography.accent,
    fontSize: 11,
  },
  statPill: {
    borderRadius: 14,
    borderWidth: 1,
    borderColor: palette.border,
    backgroundColor: 'rgba(255, 255, 255, 0.75)',
    paddingHorizontal: 11,
    paddingVertical: 8,
    marginRight: 8,
    marginTop: 6,
    minWidth: 110,
  },
  statLabel: {
    fontFamily: typography.accent,
    fontSize: 10,
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    color: palette.textMuted,
    marginBottom: 2,
  },
  statValue: {
    fontFamily: typography.display,
    fontSize: 17,
    lineHeight: 22,
    color: palette.textStrong,
  },
});
