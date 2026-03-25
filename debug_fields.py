import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_ID = "tblBo99UNx1L68IlF" # Secteurs_SousSecteurs ID from config

url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
headers = {"Authorization": f"Bearer {TOKEN}"}

resp = requests.get(url, headers=headers)
if resp.ok:
    tables = resp.json()['tables']
    for t in tables:
        print(f"Fields for table {t['name']} ({t['id']}):")
        for f in t['fields']:
            print(f"  - {f['name']} ({f['id']}) Type: {f.get('type')} Options: {f.get('options')}")

else:
    print(resp.text)
