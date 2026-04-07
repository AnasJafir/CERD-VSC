const fs = require('fs');

let ui_p = 'prova-pwa/components/pwa/Ui.tsx';
let ui_code = fs.readFileSync(ui_p, 'utf8');

// Inject imports for icons and router
if (!ui_code.includes('@expo/vector-icons')) {     
    ui_code = ui_code.replace(
        "import { Animated",
        "import { useRouter } from 'expo-router';\nimport { Ionicons } from '@expo/vector-icons';\nimport { Animated"
    );
}

let navBar = `
      <View style={{flexDirection: 'row', justifyContent: 'flex-end', padding: 16, position: 'absolute', top: 40, right: 0, zIndex: 1000}}>
        <Pressable onPress={() => router.push('/')} style={{marginRight: 16, backgroundColor: palette.surface, padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.1, shadowOffset: {width: 0, height: 2}, shadowRadius: 8}}>
          <Ionicons name="home-outline" size={24} color={palette.brand} />
        </Pressable>
        <Pressable onPress={() => router.push('/')} style={{backgroundColor: palette.surface, padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.1, shadowOffset: {width: 0, height: 2}, shadowRadius: 8}}>
          <Ionicons name="search-outline" size={24} color={palette.brand} />
        </Pressable>
      </View>
`;

// Insert nav bar into AppScreen right before the ScrollView
let appScreenRegex = /export function AppScreen\(\{[^\}]*\}\:\s*AppScreenProps\)\s*\{\s*return\s*\(\s*<SafeAreaView style=\{styles\.safe\}>\s*(<View style=\{styles\.backgroundLayer\}[\s\S]*?<\/View>)/;

// Oh wait, inside AppScreen we need `const router = useRouter();`
let appScreenDefRegex = /export function AppScreen\(\{ title, subtitle, kicker, children \}: AppScreenProps\) \{/;

ui_code = ui_code.replace(appScreenDefRegex, `export function AppScreen({ title, subtitle, kicker, children }: AppScreenProps) {\n  const router = useRouter();`);

ui_code = ui_code.replace(appScreenRegex, `export function AppScreen({ title, subtitle, kicker, children }: AppScreenProps) {\n  const router = useRouter();\n    return (\n      <SafeAreaView style={styles.safe}>\n        ${navBar}\n        $1`);

fs.writeFileSync(ui_p, ui_code);
console.log('UI updated with floating nav bar');
