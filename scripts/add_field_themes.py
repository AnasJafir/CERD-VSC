#!/usr/bin/env python3
"""
Add missing fields to Themes table for Strict Hierarchy v2.
"""
import os
import sys
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# ─── Configuration ────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
TABLES_CONFIG_PATH = ROOT_DIR / "config" / "tables_config.json"

load_dotenv(ROOT_DIR / ".env")
TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
META_URL = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
RATE_LIMIT_DELAY = 0.25

def _call(method: str, url: str, **kwargs) -> dict:
    time.sleep(RATE_LIMIT_DELAY)
    resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
    if not resp.ok:
        # If field already exists error... Airtable returns 422 if duplicate name
        if resp.status_code == 422 and "already exists" in resp.text:
             print("  [INFO] Field seems to exist (422).")
             return {}
        raise RuntimeError(f"[{resp.status_code}] {method} {url}\n{resp.text[:400]}")
    return resp.json()

def main():
    if not TABLES_CONFIG_PATH.exists():
        print(f"Error: {TABLES_CONFIG_PATH} not found.")
        return

    with open(TABLES_CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    cfg_themes = cfg.get('Themes')
    if not cfg_themes:
        print("Themes table not found in config.")
        return
        
    tid_themes = cfg_themes['id']
    
    cfg_dom = cfg.get('Domaines')
    if not cfg_dom:
         print("Domaines table not found in config.")
         return
         
    tid_domaines = cfg_dom['id']

    print(f"Adding 'Parent_Domaine' field to Themes table ({tid_themes})...")
    
    url = f"{META_URL}/tables/{tid_themes}/fields"
    
    payload = {
        "name": "Parent_Domaine",
        "type": "multipleRecordLinks",
        "options": {
            "linkedTableId": tid_domaines
        }
    }
    
    try:
        _call("POST", url, json=payload)
        print("  [OK] Field 'Parent_Domaine' created.")
    except Exception as e:
        print(f"  [WARN] {e}")

if __name__ == '__main__':
    main()
