const fs = require('fs');

let ui_p = 'prova-pwa/components/pwa/Ui.tsx';
let ui_code = fs.readFileSync(ui_p, 'utf8');

let navBar = `      <View style={{flexDirection: 'row', justifyContent: 'flex-end', paddingHorizontal: 24, paddingTop: 12, paddingBottom: 0, zIndex: 1000}}>
        <Pressable onPress={() => router.push('/')} style={{marginRight: 10, backgroundColor: '#fff', padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.05, shadowOffset: {width: 0, height: 2}, shadowRadius: 4}}>
          <Ionicons name="home" size={20} color={palette.brand} />
        </Pressable>
        <Pressable onPress={() => router.push('/e2-recherche')} style={{backgroundColor: '#fff', padding: 10, borderRadius: 20, shadowColor: '#000', shadowOpacity: 0.05, shadowOffset: {width: 0, height: 2}, shadowRadius: 4}}>
          <Ionicons name="search" size={20} color={palette.brand} />
        </Pressable>
      </View>`;

if(!ui_code.includes('Ionicons name="home"')) {
    ui_code = ui_code.replace(
        '<SafeAreaView style={styles.safe}>',
        '<SafeAreaView style={styles.safe}>\n' + navBar
    );
    
    fs.writeFileSync(ui_p, ui_code);
    console.log('navbar injected');
} else {
    console.log('navbar already there');
}


// we also need to add @expo/vector-icons / useRouter to top if missing
if(!ui_code.includes("import { useRouter } from 'expo-router';")) {
   ui_code = ui_code.replace("import { Animated", "import { useRouter } from 'expo-router';\nimport { Ionicons } from '@expo/vector-icons';\nimport { Animated");
   fs.writeFileSync(ui_p, ui_code);
} else if (!ui_code.includes("@expo/vector-icons")) {
   ui_code = ui_code.replace("import { Animated", "import { Ionicons } from '@expo/vector-icons';\nimport { Animated");
   fs.writeFileSync(ui_p, ui_code);
}
