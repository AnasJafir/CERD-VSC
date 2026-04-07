const fs = require('fs');
let app = fs.readFileSync('app.py', 'utf8');

// remove ia_engine block
let i1 = app.indexOf('ia_engine = st.radio(');
let i2 = app.indexOf(')', i1) + 1;
if(i1 > -1 && i2 > i1) {
    app = app.substring(0, i1) + app.substring(i2);
}

// remove groq_key
let i3 = app.indexOf("groq_key = os.environ.get('GROQ_API_KEY')");
if(i3 > -1) {
    app = app.substring(0, i3) + app.substring(i3 + 42); // approx
}

// replace keys block
let searchKeys = 'if ia_engine == "Gemini (Google)" and not gemini_key:\\r\\n                gemini_key = st.text_input(\\\'Clé d\\\\\\\'accès Assistant (Gemini)\\\', type=\\\'password\\\',\\r\\n                                           help=\\\'Veuillez insérer une clé d\\\\\\\'accès pour activer l\\\\\\\'analyse intelligente.\\\')\\r\\n            elif ia_engine == "Groq (Llama 3.3)" and not groq_key:\\r\\n                groq_key = st.text_input(\\\'Clé d\\\\\\\'accès Groq\\\', type=\\\'password\\\')';
let replaceKeys = 'if not gemini_key:\\n                gemini_key = st.text_input(\\\'Clé d\\\\\\\'accès Assistant (Gemini)\\\', type=\\\'password\\\',\\n                                           help=\\\'Veuillez insérer une clé d\\\\\\\'accès pour activer l\\\\\\\'analyse intelligente.\\\')';
if(app.indexOf(searchKeys) > -1) { app = app.split(searchKeys).join(replaceKeys); }

// Revert process button logic
let searchRun = 'if ia_engine == "Gemini (Google)" and not gemini_key:\\r\\n                st.error("La clé API Gemini est requise.")\\r\\n            elif ia_engine == "Groq (Llama 3.3)" and not groq_key:\\r\\n                st.error("La clé API Groq est requise.")\\r\\n            else:';
let replaceRun = 'if not gemini_key:\\n                st.error("La clé API Gemini est requise.")\\n            else:';
if(app.indexOf(searchRun) > -1) { app = app.split(searchRun).join(replaceRun); }

// Revert get_processor call 
let searchInit = '                use_groq = (ia_engine == "Groq (Llama 3.3)")\\r\\n                processor = get_processor(gemini_key, use_groq=use_groq, groq_key=groq_key)';
let replaceInit = '                processor = get_processor(gemini_key)';
if(app.indexOf(searchInit) > -1) { app = app.split(searchInit).join(replaceInit); }

// Revert get_processor definition
let searchProc = 'def get_processor(g_key, use_groq=False, groq_key=None):\\r\\n    if GeminiProcessor:\\n        return GeminiProcessor(g_key, \\\'config/parsed_data.json\\\', use_groq=use_groq, groq_key=groq_key)\\r\\n    return None';
let replaceProc = 'def get_processor(g_key):\\n    if GeminiProcessor:\\n        return GeminiProcessor(g_key, \\\'config/parsed_data.json\\\')\\n    return None';
if(app.indexOf(searchProc) > -1) { app = app.split(searchProc).join(replaceProc); }

fs.writeFileSync('app.py', app);
console.log("App.py fixed");
