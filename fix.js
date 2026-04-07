const fs = require('fs');

let appPath = 'app.py';
let appStr = fs.readFileSync(appPath, 'utf8');

// remove ia_engine
appStr = appStr.replace(/ia_engine = st\.radio\([\s\S]*?Groq est\s*souvent plus rapide\."\n\s*\)/, '');

// revert sidebar keys
appStr = appStr.replace(/gemini_key = os\.environ\.get\('GEMINI_API_KEY'\) or st\.secrets\.get\('GEMINI_API_KEY'\)\n\s*groq_key = os\.environ\.get\('GROQ_API_KEY'\)/, 'gemini_key = os.environ.get(\\\'GEMINI_API_KEY\\\') or st.secrets.get(\\\'GEMINI_API_KEY\\\')');

let searchKeys = 'if ia_engine == "Gemini (Google)" and not gemini_key:\\n                gemini_key = st.text_input(\\\'Cl? d\\\\\\\'acc?s Assistant (Gemini)\\\', type=\\\'password\\\',\\n                                           help=\\\'Veuillez ins?rer une cl? d\\\\\\\'acc?s pour activer l\\\\\\\'analyse intelligente.\\\')\\n            elif ia_engine == "Groq (Llama 3.3)" and not groq_key:\\n                groq_key = st.text_input(\\\'Cl? d\\\\\\\'acc?s Groq\\\', type=\\\'password\\\')';
let replaceKeys = 'if not gemini_key:\\n                gemini_key = st.text_input(\\\'Cl? d\\\\\\\'acc?s Assistant (Gemini)\\\', type=\\\'password\\\',\\n                                           help=\\\'Veuillez ins?rer une cl? d\\\\\\\'acc?s pour activer l\\\\\\\'analyse intelligente.\\\')';
appStr = appStr.split(searchKeys).join(replaceKeys);

// revert get_processor
let searchProc = '# Removed @st.cache_resource to ensure a new processor per engine switch\\ndef get_processor(g_key, use_groq=False, groq_key=None):\\n    if GeminiProcessor:\\n        return GeminiProcessor(g_key, \\\'config/parsed_data.json\\\', use_groq=use_groq, groq_key=groq_key)\\n    return None';
let replaceProc = '@st.cache_resource\\ndef get_processor(g_key):\\n    if GeminiProcessor:\\n        return GeminiProcessor(g_key, \\\'config/parsed_data.json\\\')\\n    return None';
appStr = appStr.split(searchProc).join(replaceProc);

// revert process button logic
let searchRun = 'if ia_engine == "Gemini (Google)" and not gemini_key:\\n                st.error("La cl? API Gemini est requise.")\\n            elif ia_engine == "Groq (Llama 3.3)" and not groq_key:\\n                st.error("La cl? API Groq est requise.")\\n            else:';
let replaceRun = 'if not gemini_key:\\n                st.error("La cl? API Gemini est requise.")\\n            else:';
appStr = appStr.split(searchRun).join(replaceRun);

let searchInit = '                new_queue = []\\n                use_groq = (ia_engine == "Groq (Llama 3.3)")\\n                processor = get_processor(gemini_key, use_groq=use_groq, groq_key=groq_key)';
let replaceInit = '                new_queue = []\\n                processor = get_processor(gemini_key)';
appStr = appStr.split(searchInit).join(replaceInit);

fs.writeFileSync(appPath, appStr);

// Ingestion script
let ingPath = 'scripts/04_article_ingestion_gemini.py';
let ingStr = fs.readFileSync(ingPath, 'utf8');

ingStr = ingStr.replace(/import requests\\n/, '');

let searchClassInit = '    def __init__(self, api_key, hierarchy_path=\\\'config/parsed_data.json\\\', use_groq=False, groq_key=None):\\n        self.use_groq = use_groq\\n        self.groq_key = groq_key or os.getenv(\\\'GROQ_API_KEY\\\')\\n        self.api_key = api_key\\n        # Initialize Client\\n        if not self.use_groq:\\n            self.client = genai.Client(api_key=self.api_key)\\n            self.model_candidates = _unique_model_candidates(PRIMARY_GEMINI_MODEL, BACKUP_GEMINI_MODEL)\\n        else:\\n            self.model_candidates = ["llama-3.3-70b-versatile"]';
let replaceClassInit = '    def __init__(self, api_key, hierarchy_path=\\\'config/parsed_data.json\\\'):\\n        self.api_key = api_key\\n        # Initialize Client\\n        self.client = genai.Client(api_key=self.api_key)\\n        self.model_candidates = _unique_model_candidates(PRIMARY_GEMINI_MODEL, BACKUP_GEMINI_MODEL)';
ingStr = ingStr.split(searchClassInit).join(replaceClassInit);

let searchGen = '                    if self.use_groq:\\n                        headers = {\\n                            "Authorization": f"Bearer {self.groq_key}",\\n                            "Content-Type": "application/json"\\n                        }\\n                        payload = {\\n                            "model": model_name,\\n                            "messages": [{"role": "user", "content": prompt}],\\n                            "response_format": {"type": "json_object"}\\n                        }\\n                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)\\n                        if res.status_code == 429:\\n                            raise Exception(f"429 RESOURCE_EXHAUSTED: {res.text}")\\n                        res.raise_for_status()\\n                        response_text = res.json()["choices"][0]["message"]["content"]\\n                    else:\\n                        response = self.client.models.generate_content(\\n                            model=model_name,\\n                            contents=prompt,\\n                            config={\\\'response_mime_type\\\': \\\'application/json\\\'}\\n                        )\\n                        response_text = response.text';
let replaceGen = '                    response = self.client.models.generate_content(\\n                        model=model_name,\\n                        contents=prompt,\\n                        config={\\\'response_mime_type\\\': \\\'application/json\\\'}\\n                    )\\n                    response_text = response.text';
ingStr = ingStr.split(searchGen).join(replaceGen);

let searchRate = '                            if delay_match1:\\n                                delay = float(delay_match1.group(1)) + 5\\n                            elif delay_match2:\\n                                delay = float(delay_match2.group(1)) + 5\\n                            elif delay_match3:\\n                                delay = float(delay_match3.group(1)) + 2\\n                            else:\\n                                delay = 10 if self.use_groq else 60  # Default long wait for Gemini, shorter for Groq\\n\\n                            api_name = "Groq API" if self.use_groq else "Google API (Gemini)"\\n                            print(f"\\\\n?? Limite de requ?tes {api_name} (429) atteinte.")\\n                            print(f"   D?tail: {error_str}")\\n                            print(f"   -> Pause automatique de {delay:.1f} secondes...")';
let replaceRate = '                            if delay_match1:\\n                                delay = float(delay_match1.group(1)) + 5\\n                            elif delay_match2:\\n                                delay = float(delay_match2.group(1)) + 5\\n                            else:\\n                                delay = 60  # Default long wait for 429\\n                            print(f"\\\\n?? Limite de requ?tes Google API (429) atteinte. Pause automatique de {delay:.1f} secondes...")';
ingStr = ingStr.split(searchRate).join(replaceRate);

ingStr = ingStr.replace(/delay_match3 = re\.search\(r"try again in \(\[0-9\.\]\+\)s", error_str, re\.IGNORECASE\)\n[\s]*/, '');

fs.writeFileSync(ingPath, ingStr);
console.log("Success");
