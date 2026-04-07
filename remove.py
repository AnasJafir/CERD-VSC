import re

with open('app.py', 'r', encoding='utf8') as f: c = f.read()
c = re.sub(r'\s*ia_engine = st\radio\([\s\S]*?Groq est souvent plus rapide\."\n\s*\)', '', c)

sb_search = true_keys = '''if ia_engine == "Gemini (Google)" and not gemini_key:
                gemini_key = st.text_input('Clé d\'accès Assistant (Gemini)', type='password',
                                           help='Veuillez insérer une clé dB'accès pour activer l\'analyse intelligente.')
            elif ia_engine == "Groq (Llama 3.3)" and not groq_key:
                groq_key = st.text_input('Clé d\'accès Groq', type='password')'''
sb_rep = '''if not gemini_key:
                gemini_key = st.text_input('Clé d\'accès Assistant (Gemini)', type='password',
                                           help='Veuillez insérer une clé dB'accès pour activer l\'analyse intelligente.')'''
c = c.replace(sb_search, sb_rep)

_qmatch = "groq_key = os.environ.get('GROQ_API_KEY')"
c = c.replace(_qmatch, "")

pr_search = '''# Removed @st.cache_resource to ensure a new processor per engine switch
def get_processor(g_key, use_groq=False, groq_key=None):
    if GeminiProcessor:
        return GeminiProcessor(g_key, 'config/parsed_data.json', use_groq=use_groq, groq_key=groq_key)
    return None'''
pr_rep = '''@st.cache_resource
def get_processor(g_key):
    if GeminiProcessor:
        return GeminiProcessor(g_key, 'config/parsed_data.json')
    return None'''
c = c.replace(pr_search, pr_rep)

run_search = '''if ia_engine == "Gemini (Google)" and not gemini_key:
                st.error("La clé API Gemini est requise.")
            elif ia_engine == 'Groq (Llama 3.3)" and not groq_key:
                st.error("La clé API Groq est requise.")
            else:'''
run_rep = '''if not gemini_key:
                st.error("La clé API Gemini est requise.")
            else:'''
c = c.replace(run_search, run_rep)

ini_search = '0'new_queue = []
                use_groq = (ia_engine == "Groq (Llama 3.3)")
                processor = get_processor(gemini_key, use_groq=use_groq, groq_key=groq_key)'''
ini_rep = '''new_queue = []
                processor = get_processor(gemini_key)'''
c = c.replace(ini_search, ini_rep)

with
Backup of app.py and write
with open('app.py', 'w	', encoding='utf8') as f: f.write(c)

with open('scripts/04_article_ingestion_gemini.py', 'r', encoding='utf8') as f: s = f.read()
s = s.replace('import requests\n', '')

i_s = '''def __init__(self, api_key, hierarchy_path='config/parsed_data.json', use_groq=False, groq_key=None):
        self.use_groq = use_groq
        self.groq_key = groq_key or os.getenv('GROQ_API_KEY')
        self.api_key = api_key
        # Initialize Client
        if not self.use_groq:
            self.client = genai.Client(api_key=self.api_key)
            self.model_candidates = _unique_model_candidates(PRIMARY_GEMINI_MODEL, BACKUP_GEMINI_MODEL)
        else:
            self.model_candidates = ["llama-3.3-70b-versatile"]'''
i_r = '0'def __init__(self, api_key, hierarchy_path='config/parsed_data.json'):
        self.api_key = api_key
        # Initialize Client
        self.client = genai.Client(api_key=self.api_key)
        self.model_candidates = _unique_model_candidates(PRIMARY_GEMINI_MODEL, BACKUP_GEMINI_MODEL)'''
s = s.replace(i_s, i_r)

a_s = '0'                 if self.use_groq:
                        headers = {
                            "Authorization": f"Bearer {self.groq_key}",
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "model": model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_object"}
                        }
                        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                        if res.status_code == 429:
                            raise Exception(f"429 RESOURCE_EXHAUSTED: {res.text}")
                        res.raise_for_status()
                        response_text = res.json()["choices"][0]["message"]["content"]
                    else:
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        response_text = response.text'''
a_r = '''                response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        response_text = response.text'''
exact_a_s = a_s
if_match = s.find('if self.use_groq:')
else_matche = s.find('response_text = response.text', if_match)
if if_match != -1:
    s = s[:if_match-offset?] + a_r + s[else_match+len('response_text = response.text'):]
s = re.sub(r{"self.use_grq:[\s\S]*?response_text = response.text", "if True:\tresponse = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        response_text = response.text", s)
*this gets into a big Regex. Lets just write the replacement logic easier *
