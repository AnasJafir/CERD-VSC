#!/usr/bin/env python3
"""
Script 02 — Création de l'infrastructure des tables Airtable
=============================================================
Crée (ou vérifie) les 4 tables du projet CERD dans la base Airtable cible,
puis sauvegarde les IDs techniques dans config/tables_config.json.

Idempotence :
  - Si une table existe déjà, son ID est récupéré sans re-création.
  - Si un champ existe déjà, il n'est pas re-créé.
  → Le script peut être relancé sans effet de bord.

Ordre de création imposé par les dépendances de liens :
  1. Domaines
  2. Secteurs_SousSecteurs  (lien → Domaines, auto-lien interne)
  3. Themes                 (lien → Secteurs_SousSecteurs)
  4. Articles               (lien → Themes + champ formule ID_Article)
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# ─── Chemins ──────────────────────────────────────────────────────────────────
ROOT_DIR        = Path(__file__).resolve().parent.parent
CONFIG_OUT_PATH = ROOT_DIR / "config" / "tables_config.json"

# ─── Environnement ────────────────────────────────────────────────────────────
load_dotenv(ROOT_DIR / ".env")
TOKEN   = os.getenv("AIRTABLE_ACCESS_TOKEN", "")
BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")

META_URL = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}"
HEADERS  = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type":  "application/json",
}

# Airtable autorise 5 req/sec ; on reste conservatif
RATE_LIMIT_DELAY = 0.25


# ══════════════════════════════════════════════════════════════════════════════
# Couche réseau
# ══════════════════════════════════════════════════════════════════════════════

def _call(method: str, url: str, **kwargs) -> dict:
    """Appel HTTP avec rate-limiting et levée d'erreur explicite."""
    time.sleep(RATE_LIMIT_DELAY)
    resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
    if not resp.ok:
        raise RuntimeError(
            f"[{resp.status_code}] {method} {url}\n{resp.text[:400]}"
        )
    return resp.json()


def get_all_tables() -> dict[str, dict]:
    """Retourne {nom_table: table_object} pour toutes les tables de la base."""
    data = _call("GET", f"{META_URL}/tables")
    return {t['name']: t for t in data.get('tables', [])}


def create_table(name: str, fields: list[dict]) -> dict:
    """Crée une nouvelle table et retourne l'objet table Airtable."""
    print(f"    → Création de la table '{name}' …")
    data = _call("POST", f"{META_URL}/tables",
                 json={"name": name, "fields": fields})
    print(f"    [OK] '{name}' créée (id={data['id']})")
    return data


def add_field(table_id: str, field_def: dict) -> dict:
    """Ajoute un champ à une table existante et retourne l'objet champ."""
    fname = field_def.get('name', '?')
    print(f"       + Champ '{fname}' …")
    data = _call("POST", f"{META_URL}/tables/{table_id}/fields", json=field_def)
    print(f"       [OK] '{fname}' ajouté (id={data['id']})")
    return data


# ══════════════════════════════════════════════════════════════════════════════
# Définitions des tables (champs sans liens d'abord)
# ══════════════════════════════════════════════════════════════════════════════

# Couleurs disponibles pour singleSelect : blueLight2, cyanLight2, tealLight2,
# greenLight2, yellowLight2, orangeLight2, redLight2, pinkLight2, purpleLight2

TABLE_SCHEMAS: dict[str, list[dict]] = {

    # ── Table 1 : Domaines ────────────────────────────────────────────────
    "Domaines": [
        {"name": "Code_Domaine", "type": "singleLineText"},  # primaire
        {"name": "Nom_Domaine",  "type": "singleLineText"},
    ],

    # ── Table 2 : Secteurs & Sous-Secteurs ────────────────────────────────
    "Secteurs_SousSecteurs": [
        {"name": "Code", "type": "singleLineText"},          # primaire
        {"name": "Nom",  "type": "singleLineText"},
        {
            "name": "Type",
            "type": "singleSelect",
            "options": {"choices": [
                {"name": "Secteur",      "color": "blueLight2"},
                {"name": "Sous_Secteur", "color": "cyanLight2"},
            ]},
        },
        {
            "name": "Est_Aussi_Theme",
            "type": "checkbox",
            "options": {"icon": "check", "color": "greenBright"},
        },
        # Texte de référence pour faciliter les lookups / formules
        {"name": "Code_Parent_Domaine", "type": "singleLineText"},
        {"name": "Code_Parent_Secteur", "type": "singleLineText"},
    ],

    # ── Table 3 : Thèmes ──────────────────────────────────────────────────
    "Themes": [
        {"name": "Code_Theme", "type": "singleLineText"},    # primaire
        {"name": "Nom_Theme",  "type": "singleLineText"},
        {
            "name": "Type_Parent",
            "type": "singleSelect",
            "options": {"choices": [
                {"name": "Secteur",      "color": "blueLight2"},
                {"name": "Sous_Secteur", "color": "cyanLight2"},
                {"name": "Domaine",      "color": "yellowLight2"},
            ]},
        },
        # Référence textuelle du parent (utile pour les formules Airtable)
        {"name": "Code_Parent_Ref", "type": "singleLineText"},
    ],

    # ── Table 4 : Articles ────────────────────────────────────────────────
    "Articles": [
        {"name": "Titre", "type": "singleLineText"},         # primaire
        {
            "name": "Série",
            "type": "singleSelect",
            "options": {"choices": [
                {"name": "c1", "color": "blueLight2"},
                {"name": "c2", "color": "greenLight2"},
                {"name": "c3", "color": "orangeLight2"},
                {"name": "c4", "color": "purpleLight2"},
            ]},
        },
        # Copie textuelle du code thème pour la formule ID_Article
        {"name": "Code_Theme_Ref", "type": "singleLineText"},
        {"name": "Index", "type": "number", "options": {"precision": 0}},
        {"name": "Extrait",          "type": "multilineText"},
        {"name": "Mots_Cles",        "type": "multilineText"},
        {"name": "Source",           "type": "singleLineText"},
        {
            "name": "Date_Publication",
            "type": "date",
            "options": {"dateFormat": {"name": "iso"}},
        },
        {"name": "Contenu_Texte",    "type": "multilineText"},
        {"name": "Fichier",          "type": "multipleAttachments"},
        {"name": "Contenu_Visuel",   "type": "multipleAttachments"},
        # ID_Article : champ texte calculé par les scripts d'ingestion
        # (format : {Série}-{Code_Theme_Ref}-{Index})
        # Note : l'API Airtable ne supporte pas la création de champs formule.
        # Pour un calcul auto dans l'interface, ajouter manuellement une formule :
        #   CONCATENATE({Série}, "-", {Code_Theme_Ref}, "-", {Index})
        {"name": "ID_Article",        "type": "singleLineText"},
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
# Champs de liaison (ajoutés après création de toutes les tables)
# ══════════════════════════════════════════════════════════════════════════════
# Clé = (table_cible, nom_du_champ)
# Valeur = fonction lambda(ids) → dict de définition du champ
# 'ids' reçoit le dict {nom_table: table_id}

LINKED_FIELDS: list[tuple[str, str, callable]] = [
    # SSS ← Domaines
    (
        "Secteurs_SousSecteurs",
        "Parent_Domaine",
        lambda ids: {
            "name": "Parent_Domaine",
            "type": "multipleRecordLinks",
            "options": {"linkedTableId": ids["Domaines"]},
        },
    ),
    # SSS ← SSS (auto-lien : Sous-Secteur → Secteur parent)
    (
        "Secteurs_SousSecteurs",
        "Parent_Secteur",
        lambda ids: {
            "name": "Parent_Secteur",
            "type": "multipleRecordLinks",
            "options": {"linkedTableId": ids["Secteurs_SousSecteurs"]},
        },
    ),
    # Themes ← SSS
    (
        "Themes",
        "Parent_SSS",
        lambda ids: {
            "name": "Parent_SSS",
            "type": "multipleRecordLinks",
            "options": {"linkedTableId": ids["Secteurs_SousSecteurs"]},
        },
    ),
    # Articles ← Themes
    (
        "Articles",
        "Theme",
        lambda ids: {
            "name": "Theme",
            "type": "multipleRecordLinks",
            "options": {"linkedTableId": ids["Themes"]},
        },
    ),
    # Themes ← Domaines
    (
        "Themes",
        "Parent_Domaine",
        lambda ids: {
            "name": "Parent_Domaine",
            "type": "multipleRecordLinks",
            "options": {"linkedTableId": ids["Domaines"]},
        },
    ),
]



# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires de configuration
# ══════════════════════════════════════════════════════════════════════════════

def table_id_map(tables_config: dict) -> dict[str, str]:
    """Retourne {nom_table: airtable_table_id}."""
    return {name: cfg['id'] for name, cfg in tables_config.items()}


def field_names_for(table_obj: dict) -> set[str]:
    """Retourne l'ensemble des noms de champs d'un objet table Airtable."""
    return {f['name'] for f in table_obj.get('fields', [])}


def fields_index(table_obj: dict) -> dict[str, str]:
    """Retourne {nom_champ: id_champ} pour un objet table."""
    return {f['name']: f['id'] for f in table_obj.get('fields', [])}


# ══════════════════════════════════════════════════════════════════════════════
# Orchestration principale
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 60)
    print("  SPRINT 1 — Script 02 : Création des Tables Airtable")
    print("═" * 60)

    if not TOKEN or not BASE_ID:
        raise SystemExit(
            "[ERREUR] Variables AIRTABLE_ACCESS_TOKEN ou AIRTABLE_BASE_ID manquantes."
        )

    print(f"\n  Base ID : {BASE_ID}")

    # ── Étape 1 : Inventaire des tables existantes ─────────────────────────
    print("\n[1] Récupération des tables existantes …")
    existing = get_all_tables()
    print(f"    Tables déjà présentes : {list(existing.keys()) or 'aucune'}")

    tables_config: dict[str, dict] = {}

    # ── Étape 2 : Création ou récupération des tables ─────────────────────
    print("\n[2] Création / vérification des tables …")
    order = ["Domaines", "Secteurs_SousSecteurs", "Themes", "Articles"]

    for tname in order:
        if tname in existing:
            print(f"    [SKIP] '{tname}' existe déjà (id={existing[tname]['id']})")
            tobj = existing[tname]
        else:
            tobj = create_table(tname, TABLE_SCHEMAS[tname])

        tables_config[tname] = {
            "id":     tobj['id'],
            "fields": fields_index(tobj),
        }

    # ── Étape 3 : Rafraîchir l'état réel des tables ───────────────────────
    print("\n[3] Rafraîchissement de l'inventaire …")
    existing = get_all_tables()
    ids = table_id_map(tables_config)

    # ── Étape 4 : Ajout des champs de liaison (idempotent) ─────────────────
    print("\n[4] Ajout des champs de liaison (Linked Records) …")

    for tname, fname, field_builder in LINKED_FIELDS:
        tobj         = existing.get(tname, {})
        current_flds = field_names_for(tobj)
        tid          = tables_config[tname]['id']

        if fname in current_flds:
            print(f"    [SKIP] '{tname}'.'{fname}' déjà présent")
            continue

        fdef = field_builder(ids)
        fdata = add_field(tid, fdef)
        tables_config[tname]['fields'][fname] = fdata['id']

    # ── Étape 5 : Note sur ID_Article ────────────────────────────────────
    print("\n[5] Champ ID_Article …")
    print("    [INFO] ID_Article est un champ texte (singleLineText) créé")
    print("           dans le schéma initial de la table Articles.")
    print("           Sa valeur sera calculée et injectée par les scripts d'ingestion.")
    print("           Pour un calcul automatique dans l'interface Airtable, vous pouvez")
    print("           manuellement le convertir en formule :")
    print("           CONCATENATE({Série}, \"-\", {Code_Theme_Ref}, \"-\", {Index})")

    # ── Étape 6 : Sauvegarde de la configuration ──────────────────────────
    print("\n[6] Sauvegarde de la configuration …")
    CONFIG_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(tables_config, f, ensure_ascii=False, indent=2)
    print(f"    [OK] {CONFIG_OUT_PATH.relative_to(ROOT_DIR)}")

    # ── Résumé ────────────────────────────────────────────────────────────
    print("\n" + "═" * 60)
    print("  RÉSUMÉ — Tables configurées")
    print("═" * 60)
    for tname, cfg in tables_config.items():
        nb_fields = len(cfg['fields'])
        print(f"  {tname:<28} id={cfg['id']}  ({nb_fields} champs)")
    print("\n  [OK] Script 02 terminé. Lancez maintenant 03_populate_hierarchy.py")
    print("═" * 60)


if __name__ == '__main__':
    main()
