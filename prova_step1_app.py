import json
import os
import re
import unicodedata
from datetime import date, datetime
from html import escape
from time import perf_counter

import streamlit as st


st.set_page_config(page_title="CERD Prova - MVP", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARSED_DATA_PATH = os.path.join(BASE_DIR, "config", "parsed_data.json")
BANNER_PATH = os.path.join(BASE_DIR, "Visuels", "Chiffres clés.png")
ICON_PATH = os.path.join(BASE_DIR, "Visuels", "Capture d'écran 2026-03-30 184442.png")

DEFAULT_PARSED_DATA = {
    "domaines": [],
    "secteurs": [],
    "sous_secteurs": [],
    "themes": [],
}

SERIES_LABELS = {
        "c1": "Serie C1",
        "c2": "Fichier Entreprises",
        "c3": "Combien ca coute ?",
    "c4": "Publications eG",
}

STAR_TOKENS = {
        "1": {
                "Style_Token": "STAR_PRIMARY",
                "Color_Token": "brand.yellow.600",
                "Weight_Token": "700",
                "Size_Token": "xl",
                "css_class": "star-primary",
        },
        "2": {
                "Style_Token": "STAR_SECONDARY",
                "Color_Token": "brand.gray.900",
                "Weight_Token": "600",
                "Size_Token": "lg",
                "css_class": "star-secondary",
        },
        "3": {
                "Style_Token": "STAR_CONTEXT",
                "Color_Token": "brand.gray.700",
                "Weight_Token": "500",
                "Size_Token": "md",
                "css_class": "star-context",
        },
}

LEVEL_LABELS = {
        "1": "Priorite 1",
        "2": "Priorite 2",
        "3": "Contexte",
}


st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');

    :root {
        --cerd-brand-yellow: #d4b106;
        --cerd-brand-yellow-soft: #f6e8a5;
        --cerd-text-strong: #0f172a;
        --cerd-text-main: #1e293b;
        --cerd-text-soft: #475569;
        --cerd-border: rgba(15, 23, 42, 0.16);
        --cerd-surface: #ffffff;
        --cerd-surface-soft: #f8fafc;
        --cerd-radius: 12px;
        --cerd-shadow-soft: 0 8px 24px rgba(15, 23, 42, 0.06);
        --cerd-font-display: 'Fraunces', Georgia, serif;
        --cerd-font-body: 'Source Sans 3', 'Trebuchet MS', sans-serif;
        --cerd-size-display: 2.1rem;
        --cerd-size-h2: 1.45rem;
        --cerd-size-h3: 1.15rem;
        --cerd-size-body: 1rem;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1200px 420px at 0% 0%, rgba(246,232,165,0.36) 0%, rgba(246,232,165,0) 60%),
            linear-gradient(180deg, #f9fafb 0%, #ffffff 44%, #f7fafc 100%);
    }

    .main * {
        font-family: var(--cerd-font-body);
        color: var(--cerd-text-main);
    }

    h1, h2, h3 {
        font-family: var(--cerd-font-display) !important;
        color: var(--cerd-text-strong) !important;
        letter-spacing: 0.01em;
    }

    h1 {
        font-size: var(--cerd-size-display) !important;
        line-height: 1.08;
    }

    h2 {
        font-size: var(--cerd-size-h2) !important;
    }

    h3 {
        font-size: var(--cerd-size-h3) !important;
    }

    p, li, label, .stCaption {
        font-size: var(--cerd-size-body) !important;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid rgba(15, 23, 42, 0.12);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, var(--cerd-brand-yellow) 0%, #bf9b00 100%);
        color: #111827;
        border: none;
        font-weight: 700;
    }

    .star-card {
        border: 1px solid var(--cerd-border);
        border-radius: var(--cerd-radius);
        padding: 12px;
        min-height: 120px;
        background: linear-gradient(180deg, var(--cerd-surface) 0%, var(--cerd-surface-soft) 100%);
        box-shadow: var(--cerd-shadow-soft);
    }

    .star-kicker {
        font-size: 0.78rem;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        color: var(--cerd-text-soft);
        margin-bottom: 8px;
    }

    .star-value {
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .star-legend {
        font-size: 0.88rem;
        color: var(--cerd-text-soft);
    }

    .star-primary .star-value {
        font-size: 2rem;
        font-weight: 700;
        color: #8a5a00;
    }

    .star-secondary .star-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--cerd-text-strong);
    }

    .star-context .star-value {
        font-size: 1.25rem;
        font-weight: 500;
        color: #334155;
    }

    .meta-chip {
        display: inline-block;
        border: 1px solid rgba(51, 65, 85, 0.28);
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 0.78rem;
        color: var(--cerd-text-main);
        background: rgba(246, 232, 165, 0.35);
        margin-right: 6px;
    }

    .parent-line {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: flex-end;
        margin: 6px 0 8px;
    }

    .parent-chip {
        display: inline-block;
        border-radius: 999px;
        border: 1px solid rgba(51, 65, 85, 0.26);
        background: #ffffff;
        color: var(--cerd-text-main);
        line-height: 1.15;
        padding: 5px 12px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .parent-domain {
        font-size: 1.03rem;
        font-weight: 700;
        background: rgba(246, 232, 165, 0.52);
        color: #5b4700;
    }

    .parent-sector {
        font-size: 0.96rem;
        font-weight: 650;
        background: rgba(246, 232, 165, 0.32);
    }

    .parent-subsector {
        font-size: 0.89rem;
        font-weight: 600;
        background: rgba(248, 250, 252, 0.95);
    }

    .parent-theme {
        font-size: 0.83rem;
        font-weight: 560;
        background: rgba(241, 245, 249, 0.95);
        color: #334155;
    }

    .parent-series {
        font-size: 0.77rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.9);
        border-style: dashed;
        color: #475569;
    }

    .token-card {
        border: 1px dashed rgba(51, 65, 85, 0.35);
        border-radius: 10px;
        padding: 8px 10px;
        background: #ffffff;
        margin-bottom: 8px;
    }

    .skeleton-card {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 8px;
        background: #ffffff;
    }

    .skeleton-bar {
        height: 10px;
        border-radius: 8px;
        margin-bottom: 6px;
        background: linear-gradient(90deg, rgba(226,232,240,0.8) 25%, rgba(248,250,252,0.95) 50%, rgba(226,232,240,0.8) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.2s infinite;
    }

    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    @media (max-width: 900px) {
        h1 {
            font-size: 1.7rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
        }
        .star-card {
            min-height: 106px;
            padding: 10px;
        }
        .star-primary .star-value {
            font-size: 1.55rem;
        }
        .star-secondary .star-value {
            font-size: 1.3rem;
        }
        .star-context .star-value {
            font-size: 1.1rem;
        }
        .parent-domain {
            font-size: 0.95rem;
        }
        .parent-sector {
            font-size: 0.9rem;
        }
        .parent-subsector {
            font-size: 0.84rem;
        }
        .parent-theme {
            font-size: 0.8rem;
        }
        .parent-series {
            font-size: 0.74rem;
        }
    }
</style>
""",
        unsafe_allow_html=True,
)


@st.cache_data
def load_parsed_data(path):
    if not os.path.exists(path):
        return DEFAULT_PARSED_DATA.copy()
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_parsed_data_safe(path):
    try:
        return load_parsed_data(path), None
    except Exception as exc:
        return DEFAULT_PARSED_DATA.copy(), str(exc)


def to_date(value):
    try:
        return datetime.strptime(str(value), "%Y-%m-%d")
    except Exception:
        return datetime.min


def split_pipe_or_lines(value):
    if value is None:
        return []
    if isinstance(value, list):
        items = []
        for item in value:
            items.extend(split_pipe_or_lines(item))
        return items
    parts = re.split(r"\s*\|\s*|[\r\n]+", str(value))
    return [part.strip() for part in parts if str(part).strip()]


def strip_technical_tokens(text):
    if text is None:
        return ""
    clean = str(text)
    patterns = [
        r"\b(?:fld|tbl|rec)[A-Za-z0-9]{10,}\b",
        r"\b(?:id|code|source_ref)\s*[:=]\s*[A-Za-z0-9_\-]+\b",
        r"\bSRC[_\-]?[0-9]+\b",
    ]
    for pattern in patterns:
        clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\s{2,}", " ", clean)
    return clean.strip(" |,;-")


def human_source_label(raw_source):
    source = strip_technical_tokens(raw_source)
    source = re.sub(r"(?i)^source\s*lisible\s*:\s*", "", source)
    return source if source else "Source non precisee"


def series_label(series_code):
    return SERIES_LABELS.get(str(series_code or "").strip().lower(), "Serie document")


def level_label(level):
    return LEVEL_LABELS.get(str(level), "Contexte")


def star_profile_for_index(index):
    if index == 0:
        return STAR_TOKENS["1"].copy() | {"Niveau_Importance": "1"}
    if index == 1:
        return STAR_TOKENS["2"].copy() | {"Niveau_Importance": "2"}
    return STAR_TOKENS["3"].copy() | {"Niveau_Importance": "3"}


def normalize_star_records(article):
    structured = article.get("star_records")
    output = []

    if isinstance(structured, list) and structured:
        ordered = sorted(
            structured,
            key=lambda row: int(row.get("Ordre_Affichage", 999)) if str(row.get("Ordre_Affichage", "")).isdigit() else 999,
        )
        for idx, row in enumerate(ordered):
            value = row.get("Valeur") or row.get("value") or row.get("chiffre")
            if not str(value or "").strip():
                continue

            default_profile = star_profile_for_index(idx)
            level = str(row.get("Niveau_Importance") or default_profile["Niveau_Importance"])
            level = level if level in {"1", "2", "3"} else "3"
            token_profile = STAR_TOKENS[level]

            output.append(
                {
                    "Valeur": str(value).strip(),
                    "Unite": str(row.get("Unite", "")).strip(),
                    "Legende": str(row.get("Legende", "")).strip(),
                    "Ordre_Affichage": idx + 1,
                    "Niveau_Importance": level,
                    "Style_Token": row.get("Style_Token") or token_profile["Style_Token"],
                    "Color_Token": row.get("Color_Token") or token_profile["Color_Token"],
                    "Weight_Token": row.get("Weight_Token") or token_profile["Weight_Token"],
                    "Size_Token": row.get("Size_Token") or token_profile["Size_Token"],
                    "css_class": token_profile["css_class"],
                }
            )
        if output:
            return output

    stars = split_pipe_or_lines(article.get("Chiffre_Star"))
    if not stars:
        stars = [str(value).strip() for value in article.get("key_figures", []) if str(value).strip()]

    legends = split_pipe_or_lines(article.get("Legende_Chiffre"))
    for idx, star in enumerate(stars):
        profile = star_profile_for_index(idx)
        legend = ""
        if legends:
            legend = legends[idx] if idx < len(legends) else legends[-1]
        if not legend:
            legend = str(article.get("excerpt", "")).strip()

        output.append(
            {
                "Valeur": star,
                "Unite": "",
                "Legende": legend,
                "Ordre_Affichage": idx + 1,
                "Niveau_Importance": profile["Niveau_Importance"],
                "Style_Token": profile["Style_Token"],
                "Color_Token": profile["Color_Token"],
                "Weight_Token": profile["Weight_Token"],
                "Size_Token": profile["Size_Token"],
                "css_class": profile["css_class"],
            }
        )

    return output


def render_star_cards(article):
    stars = normalize_star_records(article)
    if not stars:
        st.info("Aucun chiffre cle structure disponible pour cet article.")
        return

    cols = st.columns(min(3, len(stars)))
    for idx, star in enumerate(stars[:3]):
        col = cols[idx % len(cols)]
        level = star.get("Niveau_Importance", "3")
        level_text = level_label(level)
        value = strip_technical_tokens(star.get("Valeur", "-")) or "-"
        unit = strip_technical_tokens(star.get("Unite", ""))
        legend = strip_technical_tokens(star.get("Legende", ""))
        if not legend:
            legend = "Contexte non precise."
        display_value = f"{value} {unit}".strip()
        css_class = STAR_TOKENS.get(level, STAR_TOKENS["3"])["css_class"]

        with col:
            st.markdown(
                f"""
<div class="star-card {css_class}">
  <div class="star-kicker">{escape(level_text)}</div>
  <div class="star-value">{escape(display_value)}</div>
  <div class="star-legend">{escape(legend)}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_visual_token_guide():
    with st.expander("Guide visuel (tokens actifs)"):
        st.markdown(
            """
<div class="token-card"><strong>Typographie</strong><br>Display: Fraunces (titres) | Body: Source Sans 3 (lecture)</div>
<div class="token-card"><strong>Palette</strong><br>Brand: jaune CERD | Texte: noir/gris fort contraste | Surface: blanc + gris doux</div>
<div class="token-card"><strong>Hierarchie Chiffres</strong><br>Priorite 1 (xl/700) -> Priorite 2 (lg/600) -> Contexte (md/500)</div>
""",
            unsafe_allow_html=True,
        )


def render_series_overview():
    chips = [
        "c1 - Serie C1",
        "c2 - Fichier Entreprises",
        "c3 - Combien ca coute ?",
        "c4 - Publications eG",
    ]
    html = ""
    for chip in chips:
        html += f"<span class='meta-chip'>{escape(chip)}</span>"
    st.markdown(html, unsafe_allow_html=True)


def render_loading_placeholders(target, count=2):
    if not st.session_state.show_placeholders:
        return
    with target.container():
        for _ in range(count):
            st.markdown(
                """
<div class="skeleton-card">
  <div class="skeleton-bar" style="width: 74%;"></div>
  <div class="skeleton-bar" style="width: 58%;"></div>
  <div class="skeleton-bar" style="width: 92%;"></div>
</div>
""",
                unsafe_allow_html=True,
            )


def normalize_text(value):
    text = strip_technical_tokens(value)
    lowered = str(text).lower()
    deaccented = "".join(
        char
        for char in unicodedata.normalize("NFD", lowered)
        if unicodedata.category(char) != "Mn"
    )
    deaccented = re.sub(r"\s+", " ", deaccented)
    return deaccented.strip()


@st.cache_data
def build_taxonomy_index(data):
    domains_by_code = {
        str(item.get("code", "")).strip(): item
        for item in data.get("domaines", [])
        if str(item.get("code", "")).strip()
    }
    sectors_by_code = {
        str(item.get("code", "")).strip(): item
        for item in data.get("secteurs", [])
        if str(item.get("code", "")).strip()
    }
    subsectors_by_code = {
        str(item.get("code", "")).strip(): item
        for item in data.get("sous_secteurs", [])
        if str(item.get("code", "")).strip()
    }
    themes_by_code = {
        str(item.get("code", "")).strip(): item
        for item in data.get("themes", [])
        if str(item.get("code", "")).strip()
    }

    themes_by_name = {}
    for theme in data.get("themes", []):
        key = normalize_text(theme.get("nom", ""))
        if not key:
            continue
        themes_by_name.setdefault(key, []).append(theme)

    return {
        "domains_by_code": domains_by_code,
        "sectors_by_code": sectors_by_code,
        "subsectors_by_code": subsectors_by_code,
        "themes_by_code": themes_by_code,
        "themes_by_name": themes_by_name,
    }


def get_chain_from_theme(theme, taxonomy):
    parent_type = str(theme.get("type_parent", "")).strip().lower()
    parent_ref = str(theme.get("parent_ref", "")).strip()

    domain = None
    sector = None
    subsector = None

    if parent_type == "sous_secteur":
        subsector = taxonomy["subsectors_by_code"].get(parent_ref)
        if subsector:
            sector_code = str(subsector.get("parent_secteur", "")).strip()
            sector = taxonomy["sectors_by_code"].get(sector_code)
            domain_code = str(subsector.get("parent_domaine", "")).strip()
            if not domain_code and sector:
                domain_code = str(sector.get("parent_domaine", "")).strip()
            domain = taxonomy["domains_by_code"].get(domain_code)

    elif parent_type == "secteur":
        sector = taxonomy["sectors_by_code"].get(parent_ref)
        if sector:
            domain_code = str(sector.get("parent_domaine", "")).strip()
            domain = taxonomy["domains_by_code"].get(domain_code)

    elif parent_type == "domaine":
        domain = taxonomy["domains_by_code"].get(parent_ref)

    else:
        if parent_ref in taxonomy["subsectors_by_code"]:
            subsector = taxonomy["subsectors_by_code"].get(parent_ref)
            sector_code = str(subsector.get("parent_secteur", "")).strip()
            sector = taxonomy["sectors_by_code"].get(sector_code)
            domain_code = str(subsector.get("parent_domaine", "")).strip()
            if not domain_code and sector:
                domain_code = str(sector.get("parent_domaine", "")).strip()
            domain = taxonomy["domains_by_code"].get(domain_code)
        elif parent_ref in taxonomy["sectors_by_code"]:
            sector = taxonomy["sectors_by_code"].get(parent_ref)
            domain_code = str(sector.get("parent_domaine", "")).strip()
            domain = taxonomy["domains_by_code"].get(domain_code)
        elif parent_ref in taxonomy["domains_by_code"]:
            domain = taxonomy["domains_by_code"].get(parent_ref)

    return {
        "theme": theme,
        "subsector": subsector,
        "sector": sector,
        "domain": domain,
    }


def resolve_article_hierarchy(article, taxonomy):
    if not taxonomy:
        return {
            "theme": None,
            "subsector": None,
            "sector": None,
            "domain": None,
            "case": 0,
        }

    theme = None
    theme_code = str(article.get("theme_code", "")).strip()
    if theme_code:
        theme = taxonomy["themes_by_code"].get(theme_code)

    if not theme:
        key = normalize_text(article.get("theme", ""))
        candidates = taxonomy["themes_by_name"].get(key, [])
        if len(candidates) == 1:
            theme = candidates[0]
        elif candidates:
            article_sector = normalize_text(article.get("sector", ""))
            for candidate in candidates:
                chain = get_chain_from_theme(candidate, taxonomy)
                sector = chain.get("sector")
                if article_sector and sector and normalize_text(sector.get("nom", "")) == article_sector:
                    theme = candidate
                    break
            if not theme:
                theme = candidates[0]

    if theme:
        chain = get_chain_from_theme(theme, taxonomy)
    else:
        chain = {
            "theme": None,
            "subsector": None,
            "sector": None,
            "domain": None,
        }

    if not chain.get("theme"):
        fallback_theme = str(article.get("theme", "")).strip()
        if fallback_theme:
            chain["theme"] = {"nom": fallback_theme}

    if not chain.get("sector"):
        fallback_sector = str(article.get("sector", "")).strip()
        if fallback_sector and fallback_sector.lower() != "secteur":
            chain["sector"] = {"nom": fallback_sector}

    case_id = 0
    if chain.get("theme") and chain.get("subsector") and chain.get("sector") and chain.get("domain"):
        case_id = 1
    elif chain.get("theme") and chain.get("sector") and chain.get("domain"):
        case_id = 2
    elif chain.get("theme") and chain.get("domain") and not chain.get("sector"):
        case_id = 3

    chain["case"] = case_id
    return chain


def format_parent_labels(hierarchy):
    labels = []
    if hierarchy.get("domain"):
        labels.append(("domain", strip_technical_tokens(hierarchy["domain"].get("nom", ""))))
    if hierarchy.get("sector"):
        labels.append(("sector", strip_technical_tokens(hierarchy["sector"].get("nom", ""))))
    if hierarchy.get("subsector"):
        labels.append(("subsector", strip_technical_tokens(hierarchy["subsector"].get("nom", ""))))
    if hierarchy.get("theme"):
        labels.append(("theme", strip_technical_tokens(hierarchy["theme"].get("nom", ""))))

    return [(label, value) for label, value in labels if value]


def get_themes_for_sector(data, sector_code):
    sector_code = str(sector_code)
    ss_codes = {
        str(item.get("code"))
        for item in data.get("sous_secteurs", [])
        if str(item.get("parent_secteur")) == sector_code
    }

    themes = []
    for theme in data.get("themes", []):
        parent_ref = str(theme.get("parent_ref", ""))
        if parent_ref == sector_code or parent_ref in ss_codes:
            themes.append(theme)

    return sorted(themes, key=lambda row: str(row.get("nom", "")).lower())


def build_demo_articles(theme_name, series=None, sector_name=None, theme_code=None):
    theme_name_lower = str(theme_name or "").lower()
    articles = []

    if series == "c3" or "cout" in theme_name_lower or "transport" in theme_name_lower:
        articles.append(
            {
                "title": "Tunnel Maroc-Espagne pour 2050 ?",
                "source": "Source lisible: CERD / Publications eG",
                "sector": sector_name or "Transport",
                "theme": theme_name or "Ponts et Tunnels",
                "theme_code": theme_code or "42.1",
                "series": series or "c3",
                "date": "2025-12-28",
                "excerpt": "Le projet de liaison fixe, estime a 5,3 Md EUR en 2008, depasse aujourd'hui 25 Md EUR.",
                "body": "Un projet historique relance avec une trajectoire de cout en forte hausse. Le dossier compare les estimations 2008-2025.",
                "key_figures": ["5,3 Md EUR", ">25 Md EUR", "38,7 km"],
                "Legende_Chiffre": "Estimation 2008 | Estimation 2025 | Longueur",
            }
        )

    if "construction" in theme_name_lower or "materiaux" in theme_name_lower or series == "c3":
        articles.append(
            {
                "title": "Structure des prix de revient de la Briqueterie",
                "source": "Source lisible: Rapport MEDA 2006",
                "sector": sector_name or "Constructions",
                "theme": theme_name or "Materiaux de construction",
                "theme_code": theme_code or "38.3",
                "series": series or "c3",
                "date": "2006-12-31",
                "excerpt": "L'energie peut atteindre 40 % du cout de revient total.",
                "body": "Synthese de l'etude sur la filiere briques et tuiles en terre cuite au Maroc sur un echantillon d'unites.",
                "key_figures": ["40 %", "15 unites", "86 unites"],
                "Legende_Chiffre": "Poids energie | Unitees etudiees | Nombre d'unites sectorielles",
            }
        )

    if "construction" in theme_name_lower or "btp" in theme_name_lower:
        articles.append(
            {
                "title": "La consommation du ciment 2020-2024",
                "source": "Source lisible: Office des changes / publications sectorielles",
                "sector": sector_name or "Constructions",
                "theme": theme_name or "Ciment et Cimenteries",
                "theme_code": theme_code or "38.2",
                "series": series or "c1",
                "date": "2022-12-31",
                "excerpt": "La consommation se redresse en 2021 a 14,0 Mt apres le choc 2020.",
                "body": "Le document met en perspective la consommation nationale, les evolutions annuelles et un repere international.",
                "key_figures": ["14,0 Mt", "13,8 %", "386 kg/hab"],
                "Legende_Chiffre": "Volume annuel | Variation annuelle | Niveau par habitant",
            }
        )

    if "entreprise" in theme_name_lower:
        articles.append(
            {
                "title": "Panorama Entreprises - Edition synthese",
                "source": "Source lisible: CERD / Base Entreprises fldm3TzZimUMuKxuA",
                "sector": sector_name or "Services",
                "theme": theme_name or "Fichier Entreprises",
                "theme_code": theme_code,
                "series": series or "c2",
                "date": "2026-01-15",
                "excerpt": "Exemple de donnees partielles pour valider le fallback de rendu.",
                "body": "Certaines fiches disposent d'un champ Chiffre_Star brut sans structure complete. Le rendu doit rester lisible.",
                "Chiffre_Star": "12 540 entreprises | 1,8 M emplois",
            }
        )

    if not articles:
        articles.append(
            {
                "title": "Fiche de synthese: " + (theme_name or "Theme"),
                "source": "Source lisible: CERD",
                "sector": sector_name or "Secteur",
                "theme": theme_name or "Theme",
                "theme_code": theme_code,
                "series": series or "c1",
                "date": str(date.today()),
                "excerpt": "Exemple de fiche article pour valider le parcours sans clavier.",
                "body": "Cette fiche est un contenu de demonstration pour tester la navigation secteur -> theme -> article.",
                "key_figures": ["1 page", "2 clics", "secteur-first"],
                "Legende_Chiffre": "Format | Effort d'acces | Logique d'entree",
            }
        )

    return articles


def build_theme_snapshot_article(theme, sector_name, series_code="c1"):
    theme_name = str(theme.get("nom", "Theme"))
    theme_code = str(theme.get("code", "")).strip() or None
    sector_label = str(sector_name or "Secteur")
    normalized_series = str(series_code or "c1").strip().lower()

    return {
        "title": f"Repere {theme_name}",
        "source": "Source lisible: CERD / Base thematique",
        "sector": sector_label,
        "theme": theme_name,
        "theme_code": theme_code,
        "series": normalized_series,
        "date": str(date.today()),
        "excerpt": f"Lecture rapide du theme {theme_name} pour la campagne de test utilisateur.",
        "body": f"Cette fiche sert de point d'entree pour valider la navigation sur le theme {theme_name} ({theme_code or 'sans code'}).",
        "key_figures": [
            theme_code or "N/A",
            sector_label,
            series_label(normalized_series),
        ],
        "Legende_Chiffre": "Code theme | Secteur parent | Serie de navigation",
    }


@st.cache_data
def build_search_catalog(data):
    catalog = [
        {
            "title": "Tunnel Maroc-Espagne pour 2050 ?",
            "source": "Source lisible: CERD / Publications eG",
            "sector": "Transport",
            "theme": "Ponts et Tunnels",
            "theme_code": "42.1",
            "series": "c3",
            "date": "2025-12-28",
            "excerpt": "Le projet de liaison fixe passe de 5,3 Md EUR a plus de 25 Md EUR.",
            "body": "Comparatif historique des estimations et enjeux economiques.",
            "key_figures": ["5,3 Md EUR", ">25 Md EUR", "38,7 km"],
            "Legende_Chiffre": "Estimation 2008 | Estimation 2025 | Longueur",
        },
        {
            "title": "Structure des prix de revient de la Briqueterie",
            "source": "Source lisible: Rapport MEDA 2006",
            "sector": "Constructions",
            "theme": "Materiaux de construction",
            "theme_code": "38.3",
            "series": "c3",
            "date": "2006-12-31",
            "excerpt": "L'energie atteint 40 % du cout de revient dans l'echantillon observe.",
            "body": "Synthese de la filiere briques et tuiles avec structure de couts.",
            "key_figures": ["40 %", "15 unites", "86 unites"],
            "Legende_Chiffre": "Poids energie | Unitees etudiees | Nombre d'unites sectorielles",
        },
        {
            "title": "La consommation du ciment 2020-2024",
            "source": "Source lisible: Publications sectorielles",
            "sector": "Constructions",
            "theme": "Ciment et Cimenteries",
            "theme_code": "38.2",
            "series": "c1",
            "date": "2022-12-31",
            "excerpt": "Apres la baisse 2020, la consommation se redresse a 14,0 Mt.",
            "body": "Lecture rapide des volumes, rythme de reprise et repere international.",
            "key_figures": ["14,0 Mt", "13,8 %", "386 kg/hab"],
            "Legende_Chiffre": "Volume annuel | Variation annuelle | Niveau par habitant",
        },
        {
            "title": "La Louisiane vendue aux USA en 1803",
            "source": "Source lisible: CERD / reference historique",
            "sector": "Autres grands themes",
            "theme": "Insolite",
            "theme_code": "90.1",
            "series": "c3",
            "date": "2025-10-14",
            "excerpt": "Transaction historique: 15 millions de dollars pour un tiers du territoire actuel des USA.",
            "body": "Article de contextualisation economique et comparaison des ordres de grandeur.",
            "key_figures": ["15 M$", "1803", "12 Etats"],
            "Legende_Chiffre": "Montant | Annee | Etats concernes",
        },
        {
            "title": "Panorama Entreprises - Edition synthese",
            "source": "Source lisible: CERD / Base Entreprises fldm3TzZimUMuKxuA",
            "sector": "Services",
            "theme": "Fichier Entreprises",
            "theme_code": None,
            "series": "c2",
            "date": "2026-01-15",
            "excerpt": "Exemple de donnees partielles pour valider le fallback de rendu.",
            "body": "Certaines fiches disposent d'un champ Chiffre_Star brut sans structure complete. Le rendu doit rester lisible.",
            "Chiffre_Star": "12 540 entreprises | 1,8 M emplois",
        },
    ]

    series_cycle = ["c1", "c3", "c2"]
    secteurs = data.get("secteurs", [])
    for sector in secteurs:
        sector_name = str(sector.get("nom", "Secteur"))
        sector_code = str(sector.get("code", ""))
        themes = get_themes_for_sector(data, sector_code)
        for idx, theme in enumerate(themes[:3]):
            theme_name = str(theme.get("nom", "Theme"))
            theme_code = str(theme.get("code", "")).strip()
            series_code = series_cycle[idx % len(series_cycle)]

            catalog.extend(build_demo_articles(theme_name, series_code, sector_name, theme_code))
            catalog.append(build_theme_snapshot_article(theme, sector_name, series_code))

        if len(catalog) >= 40:
            break

    unique_catalog = []
    seen = set()
    for row in catalog:
        key = (
            str(row.get("title", "")).strip().lower(),
            str(row.get("theme_code", "")).strip(),
            str(row.get("date", "")).strip(),
            str(row.get("series", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_catalog.append(row)

    if len(unique_catalog) < 20:
        all_themes = data.get("themes", [])
        for theme in all_themes:
            parent_ref = str(theme.get("parent_ref", "")).strip()
            sector = next(
                (row for row in secteurs if str(row.get("code", "")).strip() == parent_ref),
                None,
            )
            sector_name = str(sector.get("nom", "Secteur")) if sector else "Secteur"
            candidate = build_theme_snapshot_article(theme, sector_name, "c1")
            key = (
                str(candidate.get("title", "")).strip().lower(),
                str(candidate.get("theme_code", "")).strip(),
                str(candidate.get("date", "")).strip(),
                str(candidate.get("series", "")).strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            unique_catalog.append(candidate)
            if len(unique_catalog) >= 20:
                break

    return unique_catalog


def score_article(article, query):
    if not query:
        return 0
    q = str(query).strip().lower()
    if not q:
        return 0

    title = str(article.get("title", "")).lower()
    blob = " ".join(
        [
            str(article.get("title", "")),
            str(article.get("theme", "")),
            str(article.get("sector", "")),
            str(article.get("source", "")),
            str(article.get("excerpt", "")),
            str(article.get("body", "")),
        ]
    ).lower()

    score = blob.count(q)
    if q in title:
        score += 3
    return score


def filter_and_sort_catalog(catalog, query, selected_sector, selected_theme, selected_series, sort_mode):
    rows = []
    q = str(query or "").strip().lower()

    for article in catalog:
        if selected_sector != "Tous" and str(article.get("sector", "")) != selected_sector:
            continue
        if selected_theme != "Tous" and str(article.get("theme", "")) != selected_theme:
            continue
        if selected_series and str(article.get("series", "")) not in selected_series:
            continue
        if q:
            if score_article(article, q) <= 0:
                continue
        rows.append(article)

    if sort_mode == "Date la plus recente":
        rows.sort(key=lambda row: to_date(row.get("date", "")), reverse=True)
    elif sort_mode == "Date la plus ancienne":
        rows.sort(key=lambda row: to_date(row.get("date", "")))
    elif sort_mode == "Alphabetique":
        rows.sort(key=lambda row: str(row.get("title", "")).lower())
    else:
        rows.sort(key=lambda row: score_article(row, q), reverse=True)

    return rows


def get_series_articles(series_code, catalog):
    code = str(series_code or "").strip().lower()
    if not code:
        return []

    rows = [
        row for row in catalog
        if str(row.get("series", "")).strip().lower() == code
    ]
    rows.sort(key=lambda row: to_date(row.get("date", "")), reverse=True)

    unique_rows = []
    seen = set()
    for row in rows:
        key = (
            str(row.get("title", "")).strip().lower(),
            str(row.get("date", "")).strip(),
            human_source_label(row.get("source", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append(dict(row))

    return unique_rows


def resolve_article_context(article, catalog):
    title = str(article.get("title", "")).strip().lower()
    date_label = str(article.get("date", "")).strip()
    series_code = str(article.get("series", "")).strip().lower()
    source_label = human_source_label(article.get("source", "")).strip().lower()

    if not title:
        return None

    for row in catalog:
        if str(row.get("title", "")).strip().lower() != title:
            continue
        if date_label and str(row.get("date", "")).strip() and str(row.get("date", "")).strip() != date_label:
            continue
        if series_code and str(row.get("series", "")).strip().lower() != series_code:
            continue
        candidate_source = human_source_label(row.get("source", "")).strip().lower()
        if source_label and candidate_source and source_label != candidate_source:
            continue
        return {
            "sector": row.get("sector"),
            "theme": row.get("theme"),
            "theme_code": row.get("theme_code"),
        }

    for row in catalog:
        if str(row.get("title", "")).strip().lower() == title and (
            not series_code or str(row.get("series", "")).strip().lower() == series_code
        ):
            return {
                "sector": row.get("sector"),
                "theme": row.get("theme"),
                "theme_code": row.get("theme_code"),
            }

    return None


def reset_to_orientation():
    st.session_state.view = "orientation"
    st.session_state.selected_domain = None
    st.session_state.selected_sector = None
    st.session_state.selected_theme = None
    st.session_state.selected_theme_code = None
    st.session_state.selected_article = None
    st.session_state.selected_series = None
    st.session_state.themes_visible_count = 12


def set_view(next_view):
    st.session_state.view = next_view


def init_state():
    defaults = {
        "view": "splash",
        "entry_mode": None,
        "selected_domain": None,
        "selected_sector": None,
        "selected_theme": None,
        "selected_theme_code": None,
        "selected_article": None,
        "selected_series": None,
        "search_query": "",
        "search_sector": "Tous",
        "search_theme": "Tous",
        "search_series": [],
        "search_sort": "Pertinence",
        "search_page": 1,
        "perf_mode": True,
        "show_placeholders": True,
        "last_articles_ms": None,
        "last_search_ms": None,
        "themes_visible_count": 12,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

with st.sidebar:
    st.markdown("### Mode Qualite")
    st.session_state.perf_mode = st.checkbox(
        "Mode performance mobile",
        value=st.session_state.perf_mode,
        help="Reduit le volume rendu par ecran pour garder une navigation fluide.",
    )
    st.session_state.show_placeholders = st.checkbox(
        "Afficher placeholders de chargement",
        value=st.session_state.show_placeholders,
    )
    if st.button("Rafraichir les donnees"):
        st.cache_data.clear()
        st.rerun()

data, data_error = load_parsed_data_safe(PARSED_DATA_PATH)
try:
    search_catalog = build_search_catalog(data)
    catalog_error = None
except Exception as exc:
    search_catalog = []
    catalog_error = str(exc)

try:
    taxonomy_index = build_taxonomy_index(data)
    taxonomy_error = None
except Exception as exc:
    taxonomy_index = {
        "domains_by_code": {},
        "sectors_by_code": {},
        "subsectors_by_code": {},
        "themes_by_code": {},
        "themes_by_name": {},
    }
    taxonomy_error = str(exc)

with st.sidebar:
    st.markdown("### Suivi Runtime")
    e5_value = f"{st.session_state.last_articles_ms} ms" if st.session_state.last_articles_ms is not None else "-"
    e7_value = f"{st.session_state.last_search_ms} ms" if st.session_state.last_search_ms is not None else "-"
    corpus_count = len(search_catalog)
    st.metric("Rendu E5", e5_value)
    st.metric("Rendu E7", e7_value)
    st.metric("Corpus QA", corpus_count)
    if corpus_count >= 20:
        st.success("Corpus 20+ articles pret")
    else:
        st.warning("Corpus inferieur a 20 articles")
    if data_error:
        st.warning("Chargement de donnees partiel. Mode fallback actif.")
    if catalog_error:
        st.warning("Catalogue recherche indisponible, reessayez un rafraichissement.")
    if taxonomy_error:
        st.warning("Index de hierarchie parent indisponible, fallback actif.")

# Header
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists(ICON_PATH):
        st.image(ICON_PATH, width=70)
with col_title:
    st.title("CERD Prova - MVP Prova")
    st.caption("Parcours nominal + recherche + contextualisation lecteur")

# Breadcrumb
breadcrumb = []
if st.session_state.view in ["splash", "home", "orientation", "about", "help", "sector", "themes", "articles", "detail", "series", "search"]:
    breadcrumb.append("E0 Splash")
if st.session_state.view in ["home", "orientation", "about", "help", "sector", "themes", "articles", "detail", "series", "search"]:
    breadcrumb.append("E1 Home")
if st.session_state.view in ["orientation", "about", "help", "sector", "themes", "articles", "detail", "series", "search"]:
    breadcrumb.append("E2 Orientation")
if st.session_state.view in ["sector", "themes", "articles", "detail"]:
    breadcrumb.append("E3 Secteurs")
if st.session_state.view in ["themes", "articles", "detail"]:
    breadcrumb.append("E4 Themes")
if st.session_state.view in ["articles", "detail"]:
    breadcrumb.append("E5 Articles")
if st.session_state.view == "detail":
    breadcrumb.append("E6 Detail")
if st.session_state.view == "search":
    breadcrumb.append("E7 Recherche")
if st.session_state.view == "about":
    breadcrumb.append("A propos")
if st.session_state.view == "help":
    breadcrumb.append("Mode d'emploi")

st.markdown("**Chemin:** " + " > ".join(breadcrumb))

if data_error:
    st.warning("Les donnees principales n'ont pas pu etre chargees completement. Affichage en mode securise.")
    if st.button("Reessayer le chargement", key="retry_data_top"):
        st.cache_data.clear()
        st.rerun()

if catalog_error:
    st.info("Le moteur de recherche est temporairement en mode degrade.")

if st.session_state.view == "splash":
    st.subheader("E0 - Splash")
    if os.path.exists(ICON_PATH):
        st.image(ICON_PATH, width=110)
    st.markdown("### CERD - Chiffres cles de l'Entreprise")
    st.caption("Chargement court puis entree dans l'espace lecteur")
    if st.button("Continuer", type="primary"):
        set_view("home")
        st.rerun()

elif st.session_state.view == "home":
    st.subheader("E1 - Home Identite")
    if os.path.exists(BANNER_PATH):
        st.image(BANNER_PATH, width="stretch")

    st.markdown("### Base documentaire economique et sociale")
    st.write("Objectif: acces en 2-3 clics a des informations structurees, lisibles et utiles.")
    if st.button("Entrer dans la base", type="primary"):
        set_view("orientation")
        st.rerun()

elif st.session_state.view == "orientation":
    st.subheader("E2 - Home Orientation")
    st.info("Choisissez un mode d'acces. Le parcours nominal est sans clavier.")
    render_visual_token_guide()
    st.caption("Series accessibles")
    render_series_overview()

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Commencer par un secteur", type="primary", width="stretch"):
            st.session_state.entry_mode = "sector"
            set_view("sector")
            st.rerun()
    with col_b:
        if st.button("Entrer par serie", width="stretch"):
            st.session_state.entry_mode = "series"
            st.session_state.selected_theme_code = None
            set_view("series")
            st.rerun()
    with col_c:
        if st.button("Recherche index/mots-cles (secondaire)", width="stretch"):
            st.session_state.entry_mode = "search"
            set_view("search")
            st.rerun()
        st.caption("Mode secondaire")

    st.markdown("### Informations lecteur")
    info_col_1, info_col_2 = st.columns(2)
    with info_col_1:
        if st.button("A propos du projet", width="stretch"):
            set_view("about")
            st.rerun()
    with info_col_2:
        if st.button("Mode d'emploi", width="stretch"):
            set_view("help")
            st.rerun()

elif st.session_state.view == "about":
    st.subheader("A propos du projet")
    st.markdown(
        """
### Base documentaire B3D
La base B3D Chiffres cles de l'Entreprise est un dispositif de lecture economique mobile-first.

- Objectif d'usage: acceder a une information utile en 2 a 3 clics.
- Methode: un sujet par document, en format editorial court.
- Valeur: transformer l'abondance d'information en lecture claire pour la decision.
"""
    )

    st.markdown("### Principes de navigation")
    st.markdown(
        """
- Parcours principal: secteur -> theme -> article.
- Recherche mots-cles: presente mais secondaire.
- Sources: toujours en libelles lisibles, jamais en codes techniques.
"""
    )

    about_c1, about_c2 = st.columns(2)
    with about_c1:
        if st.button("Retour orientation", width="stretch", key="about_back_orientation"):
            reset_to_orientation()
            st.rerun()
    with about_c2:
        if st.button("Aller au mode d'emploi", width="stretch", key="about_to_help"):
            set_view("help")
            st.rerun()

elif st.session_state.view == "help":
    st.subheader("Mode d'emploi")
    st.markdown(
        """
### Parcours recommande
1. Commencer par un secteur.
2. Choisir un theme.
3. Ouvrir l'article.
4. Lire l'extrait, les chiffres cles et la source.
"""
    )

    st.markdown("### Entrees alternatives")
    st.markdown(
        """
- Entrer par serie (c1, c2, c3, c4).
- Recherche index/mots-cles (mode secondaire).
"""
    )
    render_series_overview()

    help_c1, help_c2, help_c3 = st.columns(3)
    with help_c1:
        if st.button("Commencer par un secteur", width="stretch", key="help_to_sector"):
            reset_to_orientation()
            st.session_state.entry_mode = "sector"
            set_view("sector")
            st.rerun()
    with help_c2:
        if st.button("Entrer par serie", width="stretch", key="help_to_series"):
            reset_to_orientation()
            st.session_state.entry_mode = "series"
            set_view("series")
            st.rerun()
    with help_c3:
        if st.button("Retour orientation", width="stretch", key="help_back_orientation"):
            reset_to_orientation()
            st.rerun()

elif st.session_state.view == "sector":
    st.subheader("E3 - Secteurs (accordeon)")
    st.write("Cliquez sur une section, puis choisissez un secteur.")

    domaines = sorted(data.get("domaines", []), key=lambda row: str(row.get("code", "")))
    secteurs = data.get("secteurs", [])

    for domaine in domaines:
        d_code = str(domaine.get("code", ""))
        d_nom = strip_technical_tokens(domaine.get("nom", ""))
        secteur_rows = [
            row for row in secteurs if str(row.get("parent_domaine", "")) == d_code
        ]
        with st.expander(f"{d_nom} ({len(secteur_rows)} secteurs)"):
            secteur_rows = sorted(secteur_rows, key=lambda row: str(row.get("code", "")))
            if not secteur_rows:
                st.caption("Aucun secteur disponible.")

            for secteur in secteur_rows:
                s_code = str(secteur.get("code", ""))
                s_nom = strip_technical_tokens(secteur.get("nom", ""))
                button_label = f"Choisir: {s_nom}"
                if st.button(button_label, key=f"sector_{s_code}"):
                    st.session_state.selected_domain = d_nom
                    st.session_state.selected_sector = {"code": s_code, "nom": s_nom}
                    st.session_state.themes_visible_count = 10 if st.session_state.perf_mode else 20
                    set_view("themes")
                    st.rerun()

    if st.button("Retour orientation"):
        reset_to_orientation()
        st.rerun()

elif st.session_state.view == "themes":
    st.subheader("E4 - Themes")
    sector = st.session_state.selected_sector
    if not sector:
        reset_to_orientation()
        st.rerun()

    st.write(f"Secteur selectionne: **{sector['nom']}**")
    themes = get_themes_for_sector(data, sector["code"])
    theme_batch = 10 if st.session_state.perf_mode else 20

    if not themes:
        st.warning("Aucun theme trouve pour ce secteur.")
    else:
        visible_count = max(theme_batch, st.session_state.themes_visible_count)
        for theme in themes[:visible_count]:
            t_name = strip_technical_tokens(theme.get("nom", ""))
            if st.button(f"Choisir theme: {t_name}", key=f"theme_{t_name}"):
                st.session_state.selected_theme = t_name
                st.session_state.selected_theme_code = str(theme.get("code", "")).strip() or None
                set_view("articles")
                st.rerun()

        if visible_count < len(themes):
            st.caption(f"{visible_count}/{len(themes)} themes affiches")
            if st.button(f"Afficher {theme_batch} themes de plus"):
                st.session_state.themes_visible_count = min(len(themes), visible_count + theme_batch)
                st.rerun()

    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("Retour secteurs"):
            set_view("sector")
            st.rerun()
    with col_reset:
        if st.button("Retour orientation"):
            reset_to_orientation()
            st.rerun()

elif st.session_state.view == "series":
    st.subheader("Entree par serie")
    st.write("Entrees visibles conformes a la vision client.")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Combien ca coute ?", type="primary", width="stretch"):
            st.session_state.selected_series = "c3"
            st.session_state.selected_theme = None
            st.session_state.selected_theme_code = None
            set_view("articles")
            st.rerun()
    with col_s2:
        if st.button("Fichier Entreprises", width="stretch"):
            st.session_state.selected_series = "c2"
            st.session_state.selected_theme = None
            st.session_state.selected_theme_code = None
            set_view("articles")
            st.rerun()

    if st.button("Retour orientation"):
        reset_to_orientation()
        st.rerun()

elif st.session_state.view == "articles":
    st.subheader("E5 - Liste Articles")
    selected_theme = st.session_state.selected_theme
    selected_series = st.session_state.selected_series
    is_series_entry = st.session_state.entry_mode == "series" and bool(selected_series)

    if is_series_entry:
        st.write(f"Serie: **{series_label(selected_series)}**")
    else:
        st.write(f"Theme: **{selected_theme or 'Theme'}**")

    loading_slot = st.empty()
    render_loading_placeholders(loading_slot, count=2)
    articles_start = perf_counter()
    if is_series_entry:
        articles = get_series_articles(selected_series, search_catalog)
        if not articles:
            fallback_theme = "Combien ca coute" if selected_series == "c3" else "Fichier Entreprises"
            articles = build_demo_articles(fallback_theme, selected_series)
    else:
        articles = build_demo_articles(
            selected_theme,
            selected_series,
            st.session_state.selected_sector["nom"] if st.session_state.selected_sector else None,
            st.session_state.selected_theme_code,
        )
    st.session_state.last_articles_ms = int((perf_counter() - articles_start) * 1000)
    loading_slot.empty()

    st.caption(
        f"Temps rendu E5: {st.session_state.last_articles_ms} ms | Mode: {'performance mobile' if st.session_state.perf_mode else 'standard'}"
    )

    for index, article in enumerate(articles):
        with st.container(border=True):
            st.markdown(f"### {article['title']}")
            source_label = human_source_label(article.get("source", ""))
            st.caption(f"Source: {source_label} | Date: {article.get('date', '-')}")
            st.markdown(f"<span class='meta-chip'>{escape(series_label(article.get('series')))}</span>", unsafe_allow_html=True)
            st.write(strip_technical_tokens(article.get("excerpt", "")) or "Extrait non disponible.")
            if st.button("Lire le document", key=f"article_{index}"):
                st.session_state.selected_article = article
                set_view("detail")
                st.rerun()

    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("Retour series" if is_series_entry else "Retour themes"):
            if st.session_state.entry_mode == "series":
                set_view("series")
            else:
                set_view("themes")
            st.rerun()
    with col_reset:
        if st.button("Retour orientation"):
            reset_to_orientation()
            st.rerun()

elif st.session_state.view == "detail":
    st.subheader("E6 - Detail Article")
    article = st.session_state.selected_article

    if not article:
        set_view("articles")
        st.rerun()

    needs_context_resolve = (
        st.session_state.entry_mode == "series"
        or not str(article.get("theme_code", "")).strip()
        or not str(article.get("sector", "")).strip()
        or str(article.get("sector", "")).strip().lower() == "secteur"
        or not str(article.get("theme", "")).strip()
        or str(article.get("theme", "")).strip().lower() == "theme"
    )
    if needs_context_resolve:
        resolved = resolve_article_context(article, search_catalog)
        if resolved:
            enriched = dict(article)
            if resolved.get("sector"):
                enriched["sector"] = resolved.get("sector")
            if resolved.get("theme"):
                enriched["theme"] = resolved.get("theme")
            if resolved.get("theme_code"):
                enriched["theme_code"] = resolved.get("theme_code")
            article = enriched
            st.session_state.selected_article = enriched

    title = strip_technical_tokens(article.get("title", "Document")) or "Document"
    source_label = human_source_label(article.get("source", ""))
    date_label = strip_technical_tokens(article.get("date", "-")) or "-"

    hierarchy = resolve_article_hierarchy(article, taxonomy_index)
    parent_labels = format_parent_labels(hierarchy)
    if not parent_labels:
        fallback_sector = strip_technical_tokens(article.get("sector", ""))
        fallback_theme = strip_technical_tokens(article.get("theme", ""))
        if fallback_sector:
            parent_labels.append(("sector", fallback_sector))
        if fallback_theme:
            parent_labels.append(("theme", fallback_theme))

    st.markdown(f"## {title}")
    st.caption(f"Source: {source_label} | Date: {date_label}")

    chips_html = "<div class='parent-line'>"
    for level, value in parent_labels:
        chips_html += f"<span class='parent-chip parent-{escape(level)}'>{escape(value)}</span>"
    chips_html += f"<span class='parent-chip parent-series'>{escape(series_label(article.get('series')))}</span>"
    chips_html += "</div>"
    st.markdown(
        chips_html,
        unsafe_allow_html=True,
    )

    st.markdown("### Extrait")
    st.write(strip_technical_tokens(article.get("excerpt", "")) or "Extrait non disponible.")

    st.markdown("### Chiffres cles")
    render_star_cards(article)

    st.markdown("### Corps")
    st.write(strip_technical_tokens(article.get("body", "")) or "Contenu non disponible.")

    back_to_search = st.session_state.entry_mode == "search"
    back_label = "Retour recherche" if back_to_search else "Retour articles"

    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button(back_label):
            set_view("search" if back_to_search else "articles")
            st.rerun()
    with col_reset:
        if st.button("Retour orientation"):
            reset_to_orientation()
            st.rerun()

elif st.session_state.view == "search":
    st.subheader("E7 - Recherche index / mots-cles (secondaire)")

    col_q, col_sort = st.columns([3, 1])
    with col_q:
        query = st.text_input(
            "Mot-cle",
            value=st.session_state.search_query,
            placeholder="Ex: tunnel, ciment, cout, entreprise",
        )
        st.session_state.search_query = query
    with col_sort:
        sort_mode = st.selectbox(
            "Tri",
            ["Pertinence", "Date la plus recente", "Date la plus ancienne", "Alphabetique"],
            index=["Pertinence", "Date la plus recente", "Date la plus ancienne", "Alphabetique"].index(
                st.session_state.search_sort
            ),
        )
        st.session_state.search_sort = sort_mode

    all_sectors = ["Tous"] + sorted({str(row.get("sector", "")) for row in search_catalog if row.get("sector")})
    all_themes = ["Tous"] + sorted({str(row.get("theme", "")) for row in search_catalog if row.get("theme")})
    all_series = sorted({str(row.get("series", "")) for row in search_catalog if row.get("series")})

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        selected_sector = st.selectbox(
            "Filtre secteur",
            all_sectors,
            index=all_sectors.index(st.session_state.search_sector)
            if st.session_state.search_sector in all_sectors
            else 0,
        )
        st.session_state.search_sector = selected_sector
    with col_f2:
        selected_theme = st.selectbox(
            "Filtre theme",
            all_themes,
            index=all_themes.index(st.session_state.search_theme)
            if st.session_state.search_theme in all_themes
            else 0,
        )
        st.session_state.search_theme = selected_theme
    with col_f3:
        selected_series = st.multiselect(
            "Filtre serie",
            all_series,
            default=[
                row
                for row in st.session_state.search_series
                if row in all_series
            ],
        )
        st.session_state.search_series = selected_series

    loading_slot = st.empty()
    render_loading_placeholders(loading_slot, count=2)
    search_start = perf_counter()
    results = filter_and_sort_catalog(
        search_catalog,
        st.session_state.search_query,
        st.session_state.search_sector,
        st.session_state.search_theme,
        st.session_state.search_series,
        st.session_state.search_sort,
    )
    st.session_state.last_search_ms = int((perf_counter() - search_start) * 1000)
    loading_slot.empty()

    st.caption(
        f"{len(results)} resultat(s) | Temps rendu E7: {st.session_state.last_search_ms} ms"
    )

    page_size = 4 if st.session_state.perf_mode else 6
    max_page = max(1, (len(results) + page_size - 1) // page_size)
    if st.session_state.search_page > max_page:
        st.session_state.search_page = 1

    page = st.number_input("Page", min_value=1, max_value=max_page, value=st.session_state.search_page, step=1)
    st.session_state.search_page = int(page)

    start = (st.session_state.search_page - 1) * page_size
    end = start + page_size
    paged_results = results[start:end]

    if not paged_results:
        st.info("Aucun resultat. Ajustez le mot-cle ou les filtres.")
    else:
        for index, article in enumerate(paged_results):
            with st.container(border=True):
                st.markdown(f"### {strip_technical_tokens(article.get('title', 'Document'))}")
                source_label = human_source_label(article.get("source", ""))
                st.caption(
                    f"Source: {source_label} | {strip_technical_tokens(article.get('sector', 'Secteur'))} | {strip_technical_tokens(article.get('theme', 'Theme'))} | {series_label(article.get('series', 'c1'))} | Date: {strip_technical_tokens(article.get('date', '-'))}"
                )
                st.write(strip_technical_tokens(article.get("excerpt", "")) or "Extrait non disponible.")
                if st.button("Lire le document", key=f"search_article_{index}_{start}"):
                    st.session_state.selected_article = article
                    set_view("detail")
                    st.rerun()

    if st.button("Retour orientation"):
        reset_to_orientation()
        st.rerun()
