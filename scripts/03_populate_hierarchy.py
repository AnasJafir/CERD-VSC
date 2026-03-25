#!/usr/bin/env python3
"""
Script 03 — Peuplement de l'arborescence (Hiérarchie Stricte v2.3 -- Schema Sync)
=================================================================================
Gestion dynamique des parents pour la table Thèmes.

Updates v2.3:
  - Removed "Type" field (deleted in Airtable).
  - Updated "Parent_Secteur" logic to use Text value (Code) instead of Link (converted in Airtable).
  - Syncs with latest schema changes.
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
CONFIG_DIR = ROOT_DIR / "config"
PARSED_DATA_PATH = CONFIG_DIR / "parsed_data.json"
TABLES_CONFIG_PATH = CONFIG_DIR / "tables_config.json"
ENV_PATH = ROOT_DIR / ".env"

load_dotenv(ENV_PATH)
TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
DATA_URL = f"https://api.airtable.com/v0/{BASE_ID}"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
RATE_LIMIT_DELAY = 0.25

# ─── Utilitaires ──────────────────────────────────────────────────────────────

def _call_api(method: str, url: str, **kwargs) -> dict:
    time.sleep(RATE_LIMIT_DELAY)
    try:
        resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
        if not resp.ok:
            print(f"ERROR: {resp.status_code} {resp.text}")
            return {}
        return resp.json()
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return {}

def find_record_id(table_id: str, field: str, value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
    formula = f"{{{field}}}='{escaped}'"
    data = _call_api("GET", f"{DATA_URL}/{table_id}", params={
        "filterByFormula": formula, "maxRecords": 1, "fields[]": []
    })
    records = data.get('records', [])
    return records[0]['id'] if records else None

def upsert(table_id: str, key_field: str, key_curr: str, fields: dict) -> str:
    rid = find_record_id(table_id, key_field, key_curr)
    if rid:
        _call_api("PATCH", f"{DATA_URL}/{table_id}/{rid}", json={"fields": fields})
        print(f"  [MAJ] {key_curr}")
        return rid
    else:
        fields[key_field] = key_curr
        data = _call_api("POST", f"{DATA_URL}/{table_id}", json={"fields": fields})
        if data and 'id' in data:
            print(f"  [NEW] {key_curr}")
            return data['id']
        return ""

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("  Script 03 : Peuplement (Hiérarchie Stricte v2.3 -- Schema Sync)\n")
    
    with open(PARSED_DATA_PATH, 'r', encoding='utf-8') as f:
        parsed = json.load(f)
    with open(TABLES_CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # 1. Domaines
    print("── [1. DOMAINES] ───────────────────────────────────────────────")
    map_dom = {}
    tid_dom = cfg['Domaines']['id']
    
    for item in parsed['domaines']:
        code = item['code']
        rid = upsert(tid_dom, "Code_Domaine", code, {"Nom_Domaine": item['nom']})
        if rid: map_dom[code] = rid

    # 2. Secteurs & Sous-Secteurs
    print("\n── [2. STRUCTURES] ─────────────────────────────────────────────")
    map_sss = {}
    tid_sss = cfg['Secteurs_SousSecteurs']['id']
    
    # A. Secteurs
    for item in parsed['secteurs']:
        code = item['code']
        p_dom = item['parent_domaine']
        fields = {"Nom": item['nom']}
        
        # Link to Domaine
        if p_dom in map_dom:
            fields["Parent_Domaine"] = [map_dom[p_dom]]
            
        rid = upsert(tid_sss, "Code", code, fields)
        if rid: map_sss[code] = rid
        
    # B. Sous-Secteurs
    for item in parsed['sous_secteurs']:
        code = item['code']
        p_sect = item['parent_secteur']
        p_dom = item['parent_domaine']
        
        fields = {"Nom": item['nom']}
        
        # Link to Domaine
        if p_dom in map_dom:
            fields["Parent_Domaine"] = [map_dom[p_dom]]
        
                # Link to Secteur
        if p_sect and p_sect in map_sss:
            fields['Parent_Secteur'] = [map_sss[p_sect]]

            
        rid = upsert(tid_sss, "Code", code, fields)
        if rid: map_sss[code] = rid

    # 3. Thèmes
    print("\n── [3. THÈMES] ─────────────────────────────────────────────────")
    tid_theme = cfg['Themes']['id']
    
    for item in parsed['themes']:
        code = item['code']
        parent_type = item.get('type_parent')
        parent_ref = item.get('parent_ref')
        
        fields = {"Nom_Theme": item['nom']}
        
        # 1. Always link to Domaine
        dom_code = code[0]
        if dom_code in map_dom:
            fields["Parent_Domaine"] = [map_dom[dom_code]]
            
        # 2. Link to SSS parent if applicable
        if parent_type in ('Secteur', 'Sous_Secteur'):
            if parent_ref in map_sss:
                fields["Parent_SSS"] = [map_sss[parent_ref]]
            else:
                 print(f"  [WARN] {code} -> Parent SSS {parent_ref} introuvable")
                
        upsert(tid_theme, "Code_Theme", code, fields)

if __name__ == "__main__":
    main()


