#!/usr/bin/env python3
"""
Script 99 — Cleanup Duplicates
=============================================================
Identifies codes that are rightfully Themes (according to parsed_data.json)
but incorrectly exist in the 'Secteurs_SousSecteurs' table due to previous runs.
Deletes strictly the records that are now Themes.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# ─── Configuration ────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
PARSED_DATA_PATH = ROOT_DIR / "config" / "parsed_data.json"
TABLES_CONFIG_PATH = ROOT_DIR / "config" / "tables_config.json"

load_dotenv(ROOT_DIR / ".env")
TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
DATA_URL = f"https://api.airtable.com/v0/{BASE_ID}"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
RATE_LIMIT_DELAY = 0.25

def _call(method: str, url: str, **kwargs) -> dict:
    time.sleep(RATE_LIMIT_DELAY)
    resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
    if not resp.ok:
        raise RuntimeError(f"[{resp.status_code}] {method} {url}\n{resp.text[:400]}")
    return resp.json()

def main():
    print("  Script 99 : Cleanup Duplicates\n")

    with open(PARSED_DATA_PATH, 'r', encoding='utf-8') as f:
        parsed = json.load(f)
    with open(TABLES_CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    tid_sss = cfg['Secteurs_SousSecteurs']['id']
    
    # 1. Identify valid Themes
    valid_themes_codes = {item['code'] for item in parsed['themes']}
    print(f"  Target: Ensure {len(valid_themes_codes)} Theme codes aren't in Secteurs table.")

    # 2. Scan Secteurs_SousSecteurs table
    # We need to list all records to find duplicates
    print(f"  Scanning table Secteurs_SousSecteurs ({tid_sss})...")
    
    records_to_delete = []
    
    offset = None
    while True:
        params = {"fields[]": ["Code"]}
        if offset: params["offset"] = offset
        
        data = _call("GET", f"{DATA_URL}/{tid_sss}", params=params)
        records = data.get('records', [])
        
        for r in records:
            code = r['fields'].get('Code')
            rid  = r['id']
            if code in valid_themes_codes:
                records_to_delete.append((rid, code))
        
        offset = data.get('offset')
        if not offset: break
    
    print(f"  Found {len(records_to_delete)} records to delete in Secteurs table.")

    if not records_to_delete:
        print("  Clean!")
        return

    # 3. Delete duplicates
    print("  Deleting...")
    # Airtable allows batch delete of 10
    
    batch = []
    for rid, code in records_to_delete:
        batch.append(rid)
        if len(batch) == 10:
            params = {}
            for i, r in enumerate(batch):
                params[f"records[{i}]"] = r
            
            _call("DELETE", f"{DATA_URL}/{tid_sss}", params=params)
            print(f"  Deleted batch of {len(batch)}")
            batch = []
            
    if batch:
        params = {}
        for i, r in enumerate(batch):
            params[f"records[{i}]"] = r
        _call("DELETE", f"{DATA_URL}/{tid_sss}", params=params)
        print(f"  Deleted batch of {len(batch)}")

    print("\n  Cleanup complete.")

if __name__ == '__main__':
    main()
