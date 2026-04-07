import argparse
import hashlib
import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from pyairtable import Api

ROOT_DIR = Path(__file__).resolve().parents[1]
PARSED_DATA_PATH = ROOT_DIR / 'config' / 'parsed_data.json'
DEFAULT_OUTPUT_DIR = 'prova-pwa'

ALLOWED_SERIES = {'c1', 'c2', 'c3', 'c4'}
TEST_MARKERS = ('test', 'mock', 'e2e', 'demo', 'sandbox', 'sample')
KEY_FIGURE_UNIT_PATTERN = re.compile(
    r'(?i)(%|\b(?:dh|mad|eur|usd|mrd|md|million|milliard|milliards|millions|km|m2|m3|kg|tonnes?|heures?|jours?|ans?)\b)'
)
KEY_FIGURE_MONEY_PATTERN = re.compile(r'(?i)(?:€|\$|\b(?:dh|mad|eur|usd|mrd|md|million|milliard|milliards|millions)\b)')
KEY_FIGURE_TAIL_UNIT_PATTERN = re.compile(
    r"^\s*(?:d['’]\s*)?(%|dh|mad|eur|usd|mrd|md|km|m2|m3|kg|tonnes?|heures?|jours?|ans?|m)\b",
    flags=re.IGNORECASE,
)


def resolve_output_path(output_dir):
    base_path = Path(str(output_dir or '').strip() or DEFAULT_OUTPUT_DIR)
    if not base_path.is_absolute():
        base_path = ROOT_DIR / base_path

    return base_path / 'src' / 'data' / 'publicCatalog.generated.ts'


def normalize_text(value):
    text = str(value or '').strip().lower()
    if not text:
        return ''
    normalized = unicodedata.normalize('NFD', text)
    cleaned = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def slugify_value(value, fallback='item'):
    text = normalize_text(value)
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text or fallback


def normalize_ocr_artifacts(value):
    text = str(value or '')
    replacements = {
        'ÆÇ': '€',
        'Æ€': '€',
        'Â€': '€',
        'dÆ€': "d'€",
        'dÆÇ': "d'€",
        'Ç': '€',
        'ç': '€',
        '¢': '€',
        'co¹t': 'cout',
        'Co¹t': 'Cout',
        'durÚe': 'duree',
        'DurÚe': 'Duree',
        'pÚriode': 'periode',
        'PÚriode': 'Periode',
        'Úvolution': 'evolution',
        'Évolution': 'Evolution',
        'Ú': 'e',
        'Þ': 'e',
        'Ó': 'a',
        'Æ': "'",
    }
    for old_value, new_value in replacements.items():
        text = text.replace(old_value, new_value)

    text = re.sub(r'(?i)\beuros?\b', '€', text)
    text = re.sub(r"(?i)\bd['’]\s*€\b", '€', text)
    return text


def split_pipe_values(value):
    raw = str(value or '').strip()
    if not raw:
        return []

    parts = re.split(r'\s*\|\s*|[\r\n]+', raw)
    output = []
    seen = set()
    for part in parts:
        clean_part = re.sub(r'\s+', ' ', str(part)).strip()
        if clean_part and clean_part not in seen:
            seen.add(clean_part)
            output.append(clean_part)
    return output


def split_keywords(value):
    raw = str(value or '').strip()
    if not raw:
        return []

    parts = re.split(r'\s*\|\s*|[\r\n,;]+', raw)
    output = []
    seen = set()
    for part in parts:
        clean_part = re.sub(r'\s+', ' ', str(part)).strip()
        if clean_part:
            key = clean_part.lower()
            if key not in seen:
                seen.add(key)
                output.append(clean_part)
    return output


def strip_internal_tokens(value):
    text = str(value or '')
    if not text.strip():
        return ''

    patterns = [
        r'\b(?:fld|tbl|rec)[A-Za-z0-9]{10,}\b',
        r'\b(?:source_ref|id|code)\s*[:=]\s*[A-Za-z0-9_\-]+\b',
        r'\bSRC[_\-]?[0-9]+\b',
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' |,;-')
    return cleaned


def human_source_label(raw_source):
    source = strip_internal_tokens(raw_source)
    source = re.sub(r'(?i)^source\s*lisible\s*:\s*', '', source)
    source = source.strip()
    return source or 'Source non precisee'


def safe_date(value):
    text = str(value or '').strip()
    if not text:
        return ''
    if len(text) >= 10:
        return text[:10]
    return text


def first_attachment_url(value):
    if not isinstance(value, list):
        return ''

    for item in value:
        if not isinstance(item, dict):
            continue
        url = str(item.get('url', '')).strip()
        if url:
            return url

    return ''


def clean_visual_title(filename):
    raw = str(filename or '').strip()
    if not raw:
        return 'Visuel article'

    base_name, _ = os.path.splitext(raw)
    title = re.sub(r'[_\-]+', ' ', base_name)
    title = re.sub(r'\s+', ' ', title).strip()
    return title or 'Visuel article'


def extract_visual_attachments(value):
    if not isinstance(value, list):
        return []

    visuals = []
    seen = set()

    for item in value:
        if not isinstance(item, dict):
            continue

        url = str(item.get('url', '')).strip()
        if not url:
            continue

        filename = str(item.get('filename', '')).strip()
        mime_type = str(item.get('type', '')).strip().lower()
        extension = os.path.splitext(filename.lower())[1]

        is_image = extension in {'.png', '.jpg', '.jpeg', '.webp', '.gif'} or mime_type.startswith('image/')
        if not is_image:
            continue

        if url in seen:
            continue
        seen.add(url)

        visuals.append(
            {
                'url': url,
                'filename': filename,
                'title': clean_visual_title(filename),
            }
        )

    return visuals


def looks_like_test_payload(fields):
    text_parts = [
        str(fields.get('Titre', '')).lower(),
        str(fields.get('Extrait', '')).lower(),
        str(fields.get('Source', '')).lower(),
        str(fields.get('Mots_Cles', '')).lower(),
    ]
    compact_text = ' '.join(text_parts)

    return any(marker in compact_text for marker in TEST_MARKERS)


def is_plain_year(value):
    return bool(re.fullmatch(r'(?:18|19|20)\d{2}', str(value or '').strip()))


def normalize_candidate_key(value):
    return re.sub(r'[^a-z0-9]+', '', str(value or '').lower())


def extract_tail_unit(tail_text):
    clean_tail = re.sub(r'\s+', ' ', str(tail_text or '')).strip()
    if not clean_tail:
        return ''

    if clean_tail.startswith('%'):
        return '%'

    if clean_tail.startswith('€'):
        return '€'

    if clean_tail.startswith('$'):
        return '$'

    money_scale_match = re.match(
        r"(?i)^(?:d['’]\s*)?(milliards?|millions?)\b\s*(?:d['’]\s*)?(€|\$|dh|mad|eur|usd)?",
        clean_tail,
    )
    if money_scale_match:
        scale = str(money_scale_match.group(1) or '').lower()
        currency = str(money_scale_match.group(2) or '').lower()
        if currency:
            return f'{scale} {currency}'
        return scale

    match = KEY_FIGURE_TAIL_UNIT_PATTERN.search(clean_tail)
    if not match:
        return ''
    return str(match.group(1) or '').strip()


def enrich_value_with_tail_unit(value, tail_text):
    clean_value = normalize_ocr_artifacts(value)
    clean_value = re.sub(r'\s+', ' ', clean_value).strip('.,;:- ')
    if not clean_value:
        return ''

    if KEY_FIGURE_UNIT_PATTERN.search(clean_value) or KEY_FIGURE_MONEY_PATTERN.search(clean_value):
        return clean_value

    tail_unit = extract_tail_unit(tail_text)
    if not tail_unit:
        return clean_value

    if tail_unit == '%':
        return f'{clean_value}%'

    return f'{clean_value} {tail_unit}'


def extract_time_hint(context_text):
    context = str(context_text or '')
    patterns = [
        r'(?i)\bfin\s+\d{4}\b',
        r'(?i)\bhorizon\s+\d{4}\b',
        r"(?i)\bd['’]ici\s+\d{4}\b",
        r'(?i)\b\d+\s+ans?\s+plus\s+tard\b',
        r'(?i)\b(?:18|19|20)\d{2}\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, context)
        if match:
            return re.sub(r'\s+', ' ', match.group(0)).strip()
    return ''


def extract_route_hint(context_text):
    context = str(context_text or '')
    route_match = re.search(r'([A-Z][A-Za-zÀ-ÿ\-]+)\s*[-–]\s*([A-Z][A-Za-zÀ-ÿ\-]+)', context)
    if not route_match:
        return ''
    return f"{route_match.group(1).strip()}-{route_match.group(2).strip()}"


def infer_metric_axis(context_text, value_text):
    context_lower = str(context_text or '').lower()
    value_lower = str(value_text or '').lower()

    if any(token in context_lower for token in ['comparaison', 'vs', 'benchmark', 'plus que', 'moins que']):
        return 'comparaison'
    if any(token in context_lower for token in ['cout', 'coût', 'co¹t', 'budget', 'invest', 'prix', 'montant']) or KEY_FIGURE_MONEY_PATTERN.search(value_lower):
        return 'financier'
    if any(token in context_lower for token in ['trajet', 'duree', 'durée', 'delai', 'délai', 'temps']) or 'heure' in value_lower:
        return 'duree'
    if any(token in context_lower for token in ['longueur', 'distance', 'km']) or 'km' in value_lower:
        return 'dimension_longueur'
    if any(token in context_lower for token in ['profondeur', 'hauteur', 'largeur', 'diametre']) or re.search(r'\b\d+(?:[.,]\d+)?\s*m\b', value_lower):
        return 'dimension_mesure'
    if '%' in value_lower or any(token in context_lower for token in ['taux', 'part', 'variation', 'evolution', 'évolution']):
        return 'variation'
    if re.fullmatch(r'(?:18|19|20)\d{2}', str(value_text or '').strip()):
        return 'date'
    return 'quantite'


def extract_subject_hint(context_text):
    context_lower = str(context_text or '').lower()
    if 'section sous-marine' in context_lower or 'section sous marine' in context_lower:
        return 'de la section sous-marine'
    if 'ouvrage' in context_lower:
        return "de l'ouvrage"
    if 'projet' in context_lower:
        return 'du projet'
    if 'tunnel' in context_lower:
        return 'du tunnel'
    if 'article' in context_lower:
        return "de l'article"
    return ''


def infer_key_figure_legend(context_text, value):
    context = normalize_ocr_artifacts(context_text)
    context = re.sub(r'\s+', ' ', str(context or '')).strip()
    if not context:
        return ''

    value_text = enrich_value_with_tail_unit(value, '')
    axis = infer_metric_axis(context, value_text)
    time_hint = extract_time_hint(context)
    route_hint = extract_route_hint(context)
    subject_hint = extract_subject_hint(context)
    context_lower = context.lower()

    if axis == 'duree' and route_hint:
        legend = f'Temps de trajet {route_hint}'
    elif axis == 'financier':
        if any(token in context_lower for token in ['budget', 'investissement', 'investi', 'investis']):
            legend = f'Budget ou investissement cle {subject_hint}'.strip()
        elif any(token in context_lower for token in ['cout', 'coût', 'co¹t', 'prix', 'montant']):
            legend = f'Cout estime {subject_hint}'.strip()
        else:
            legend = f'Montant financier cle {subject_hint}'.strip()
    elif axis == 'dimension_longueur':
        if 'section sous-marine' in context_lower or 'section sous marine' in context_lower:
            legend = 'Longueur de la section sous-marine'
        elif any(token in context_lower for token in ['total', 'entier', 'mesurerait']):
            legend = f'Longueur totale {subject_hint}'.strip()
        else:
            legend = f'Longueur cle {subject_hint}'.strip()
    elif axis == 'dimension_mesure':
        if 'profondeur' in context_lower:
            legend = f'Profondeur cle {subject_hint}'.strip()
        elif 'hauteur' in context_lower:
            legend = f'Hauteur cle {subject_hint}'.strip()
        else:
            legend = f'Dimension cle {subject_hint}'.strip()
    elif axis == 'comparaison':
        legend = 'Comparaison chiffrée'
    elif axis == 'variation':
        legend = 'Variation ou part cle'
    elif axis == 'date':
        legend = 'Jalon temporel'
    else:
        legend = f'Indicateur quantitatif cle {subject_hint}'.strip()

    legend = re.sub(r'\s+', ' ', legend).strip(' .;:-')
    if time_hint and time_hint.lower() not in legend.lower():
        legend = f'{legend} ({time_hint})'

    if len(legend.split()) < 3:
        context_without_value = context
        clean_value = re.sub(r'\s+', ' ', str(value or '')).strip()
        if clean_value:
            context_without_value = re.sub(re.escape(clean_value), '', context_without_value, flags=re.IGNORECASE)
        context_without_value = re.sub(r'\s+', ' ', context_without_value).strip(' .;:-')
        if context_without_value:
            legend = context_without_value[:140]

    return normalize_ocr_artifacts(legend)


def first_numeric_value(value):
    match = re.search(r'\d+(?:[.,]\d+)?', str(value or ''))
    if not match:
        return None

    numeric_text = match.group(0).replace(',', '.')
    try:
        return float(numeric_text)
    except Exception:
        return None


def score_key_figure_candidate(value, legend):
    clean_value = re.sub(r'\s+', ' ', str(value or '')).strip('.,;:- ')
    clean_legend = re.sub(r'\s+', ' ', str(legend or '')).strip()

    if not clean_value or not re.search(r'\d', clean_value):
        return -10

    score = 0
    if KEY_FIGURE_MONEY_PATTERN.search(clean_value):
        score += 4
    if KEY_FIGURE_UNIT_PATTERN.search(clean_value):
        score += 3
    if re.search(r'[<>+=]', clean_value):
        score += 1
    if re.search(r'(?i)(cout|budget|invest|volume|production|longueur|profondeur|taux|part)', clean_legend):
        score += 2
    if len(re.sub(r'\D', '', clean_value)) >= 5:
        score += 1
    if is_plain_year(clean_value):
        score -= 6

    if not KEY_FIGURE_UNIT_PATTERN.search(clean_value) and not KEY_FIGURE_MONEY_PATTERN.search(clean_value):
        numeric_value = first_numeric_value(clean_value)
        if numeric_value is not None and numeric_value < 50:
            score -= 2

    return score


def extract_markdown_highlight_candidates(content):
    text = str(content or '')
    if not text:
        return []

    values = []
    seen = set()
    for match in re.finditer(r'\*\*([^*]+)\*\*', text):
        raw_value = match.group(1)
        tail_text = text[match.end():match.end() + 28]
        clean_value = enrich_value_with_tail_unit(strip_internal_tokens(raw_value), tail_text)
        if not clean_value or not re.search(r'\d', clean_value):
            continue

        key = normalize_candidate_key(clean_value)
        if key and key not in seen:
            seen.add(key)

            context_start = max(0, match.start() - 120)
            context_end = min(len(text), match.end() + 120)
            context_text = text[context_start:context_end]
            values.append(
                {
                    'value': clean_value,
                    'legend': infer_key_figure_legend(context_text, clean_value),
                }
            )

    return values


def sanitize_key_figures(key_figures, content_text, excerpt_text):
    base = key_figures if isinstance(key_figures, list) else []
    fallback_legend = strip_internal_tokens(excerpt_text) or 'Information cle mise en evidence.'

    candidates = []
    seen = set()

    for idx, figure in enumerate(base):
        value = strip_internal_tokens(figure.get('value', ''))
        legend = strip_internal_tokens(figure.get('legend', '')) or fallback_legend
        key = normalize_candidate_key(value)
        if not key or key in seen:
            continue

        score = score_key_figure_candidate(value, legend)
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': value,
                'legend': legend,
                'score': score,
                'order': idx,
            }
        )

    highlighted_candidates = extract_markdown_highlight_candidates(content_text)
    for idx, highlighted in enumerate(highlighted_candidates):
        highlighted_value = str(highlighted.get('value', '')).strip()
        highlighted_legend = str(highlighted.get('legend', '')).strip() or fallback_legend

        key = normalize_candidate_key(highlighted_value)
        if not key or key in seen:
            continue

        score = score_key_figure_candidate(highlighted_value, highlighted_legend)
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': highlighted_value,
                'legend': highlighted_legend,
                'score': score + 1,
                'order': len(base) + idx,
            }
        )

    candidates.sort(key=lambda row: (-row.get('score', 0), row.get('order', 999)))

    if not candidates:
        for idx, figure in enumerate(base):
            value = strip_internal_tokens(figure.get('value', ''))
            if not value or not re.search(r'\d', value):
                continue
            legend = strip_internal_tokens(figure.get('legend', '')) or fallback_legend
            candidates.append(
                {
                    'value': value,
                    'legend': legend,
                    'score': 0,
                    'order': idx,
                }
            )
            if len(candidates) >= 3:
                break

    sanitized = []
    for idx, candidate in enumerate(candidates[:3]):
        sanitized.append(
            {
                'level': safe_level('', idx + 1),
                'value': candidate.get('value', ''),
                'legend': candidate.get('legend', '') or fallback_legend,
            }
        )

    return sanitized


def normalize_series(value):
    series = str(value or '').strip().lower()
    return series if series in ALLOWED_SERIES else 'c1'


def safe_level(value, fallback_level):
    level_text = str(value or '').strip()
    if level_text in {'1', '2', '3'}:
        return int(level_text)
    if fallback_level in {1, 2, 3}:
        return fallback_level
    return 3


def build_catalog_metadata(record_id, title, theme_code, date_publication, source):
    export_timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    title_slug = slugify_value(title, fallback='article')
    theme_slug = slugify_value(theme_code, fallback='theme')
    catalog_slug = f'{theme_slug}-{title_slug}' if theme_slug and theme_slug != 'theme' else title_slug

    signature = f"{record_id}|{title}|{date_publication}|{source}"
    catalog_fingerprint = hashlib.sha1(signature.encode('utf-8')).hexdigest()[:12]
    catalog_id = f"CAT-{catalog_fingerprint.upper()}"

    return {
        'catalogId': catalog_id,
        'catalogSlug': catalog_slug,
        'catalogTimestampUTC': export_timestamp,
        'catalogFingerprint': catalog_fingerprint,
    }


def load_taxonomy(path):
    if not path.exists():
        return {
            'domains_by_code': {},
            'sectors_by_code': {},
            'subsectors_by_code': {},
            'themes_by_code': {},
        }

    with path.open('r', encoding='utf-8') as file:
        data = json.load(file)

    return {
        'domains_by_code': {
            str(item.get('code', '')).strip(): item
            for item in data.get('domaines', [])
            if str(item.get('code', '')).strip()
        },
        'sectors_by_code': {
            str(item.get('code', '')).strip(): item
            for item in data.get('secteurs', [])
            if str(item.get('code', '')).strip()
        },
        'subsectors_by_code': {
            str(item.get('code', '')).strip(): item
            for item in data.get('sous_secteurs', [])
            if str(item.get('code', '')).strip()
        },
        'themes_by_code': {
            str(item.get('code', '')).strip(): item
            for item in data.get('themes', [])
            if str(item.get('code', '')).strip()
        },
    }


def resolve_theme_context(theme_code, taxonomy):
    if not theme_code:
        return {
            'theme_label': '',
            'sector_code': '',
            'sector_label': '',
            'domain_label': '',
        }

    themes_by_code = taxonomy.get('themes_by_code', {})
    sectors_by_code = taxonomy.get('sectors_by_code', {})
    subsectors_by_code = taxonomy.get('subsectors_by_code', {})
    domains_by_code = taxonomy.get('domains_by_code', {})

    theme = themes_by_code.get(theme_code)
    if not theme:
        return {
            'theme_label': '',
            'sector_code': '',
            'sector_label': '',
            'domain_label': '',
        }

    theme_label = str(theme.get('nom', '')).strip()
    parent_type = str(theme.get('type_parent', '')).strip().lower()
    parent_ref = str(theme.get('parent_ref', '')).strip()

    sector = None
    domain = None

    if parent_type == 'secteur':
        sector = sectors_by_code.get(parent_ref)
        if sector:
            domain_code = str(sector.get('parent_domaine', '')).strip()
            domain = domains_by_code.get(domain_code)

    elif parent_type == 'sous_secteur':
        subsector = subsectors_by_code.get(parent_ref)
        if subsector:
            sector_code = str(subsector.get('parent_secteur', '')).strip()
            sector = sectors_by_code.get(sector_code)
            domain_code = str(subsector.get('parent_domaine', '')).strip()
            if not domain_code and sector:
                domain_code = str(sector.get('parent_domaine', '')).strip()
            domain = domains_by_code.get(domain_code)

    elif parent_type == 'domaine':
        domain = domains_by_code.get(parent_ref)

    sector_code = str(sector.get('code', '')).strip() if sector else ''
    sector_label = str(sector.get('nom', '')).strip() if sector else ''
    subsector_label = str(subsector.get('nom', '')).strip() if 'subsector' in locals() and subsector else ''
    domain_label = str(domain.get('nom', '')).strip() if domain else ''

    return {
        'theme_label': theme_label,
        'sector_code': sector_code,
        'sector_label': sector_label,
        'domain_label': domain_label,
        'subsector_label': subsector_label,
    }


def build_star_map(star_records):
    star_map = {}

    for star_record in star_records:
        fields = star_record.get('fields', {})
        linked_articles = fields.get('Article_Ref') or []
        if not linked_articles:
            continue

        order_text = str(fields.get('Ordre_Affichage', '')).strip()
        order_value = int(order_text) if order_text.isdigit() else 999

        star_payload = {
            'value': strip_internal_tokens(fields.get('Valeur', '')),
            'legend': strip_internal_tokens(fields.get('Legende', '')),
            'level': str(fields.get('Niveau_Importance', '')).strip(),
            'order': order_value,
        }

        if not star_payload['value']:
            continue

        for article_id in linked_articles:
            key = str(article_id).strip()
            if not key:
                continue
            star_map.setdefault(key, []).append(star_payload.copy())

    for article_id, star_values in star_map.items():
        star_values.sort(key=lambda item: item.get('order', 999))
        normalized = []
        for idx, star_value in enumerate(star_values[:3]):
            normalized.append(
                {
                    'level': safe_level(star_value.get('level'), idx + 1),
                    'value': star_value.get('value', ''),
                    'legend': star_value.get('legend', '') or 'Contexte non precise.',
                }
            )
        star_map[article_id] = normalized

    return star_map


def fallback_key_figures(article_fields, excerpt_text):
    stars = split_pipe_values(article_fields.get('Chiffre_Star', ''))
    legends = split_pipe_values(article_fields.get('Legende_Chiffre', ''))

    key_figures = []
    for idx, star in enumerate(stars[:3]):
        legend = legends[idx] if idx < len(legends) else ''
        if not legend and legends:
            legend = legends[-1]
        if not legend:
            legend = excerpt_text or 'Contexte non precise.'

        key_figures.append(
            {
                'level': safe_level('', idx + 1),
                'value': strip_internal_tokens(star),
                'legend': strip_internal_tokens(legend) or 'Contexte non precise.',
            }
        )

    return [figure for figure in key_figures if figure.get('value')]


def build_live_catalog(api, base_id, taxonomy):
    articles_table = api.table(base_id, 'Articles')
    stars_table = api.table(base_id, 'Chiffres_Stars')

    article_records = articles_table.all()
    star_records = stars_table.all()

    star_map = build_star_map(star_records)
    sector_index = {}
    theme_index = {}
    articles = []

    for article_record in article_records:
        fields = article_record.get('fields', {})

        if looks_like_test_payload(fields):
            continue

        article_id = str(article_record.get('id', '')).strip()
        if not article_id:
            continue

        title = strip_internal_tokens(fields.get('Titre', ''))
        if not title:
            continue

        series = normalize_series(fields.get('Série', 'c1'))
        theme_code = str(fields.get('Code_Theme_Ref', '')).strip()

        context = resolve_theme_context(theme_code, taxonomy)
        theme_label = context['theme_label'] or (f'Theme {theme_code}' if theme_code else 'Theme non classe')
        sector_code = context['sector_code'] or '00'
        sector_label = context['sector_label'] or 'Secteur non classe'
        domain_label = context['domain_label'] or 'Classement temporaire'
        subsector_label = context.get('subsector_label', '')

        # Smart hierarchy assignment
        if subsector_label:
            final_sector_label = subsector_label
            final_description = f"{domain_label} > {sector_label}"
        elif context['domain_label'] and not context['sector_label']:
            final_sector_label = context['domain_label']
            final_description = f"{context['domain_label']}"
            sector_code = f"dom-{slugify_value(context['domain_label'])}"
        else:
            final_sector_label = sector_label
            final_description = f"{domain_label}"

        sector_id = f"sec-{slugify_value(sector_code, fallback='00')}"
        theme_key = theme_code or f"sans-code-{theme_label}"
        theme_id = f"th-{slugify_value(theme_key, fallback='theme')}"

        if sector_id not in sector_index:
            sector_index[sector_id] = {
                'id': sector_id,
                'label': final_sector_label,
                'description': final_description,
            }

        if theme_id not in theme_index:
            theme_index[theme_id] = {
                'id': theme_id,
                'sectorId': sector_id,
                'code': theme_code,
                'label': theme_label,
            }

        source = human_source_label(fields.get('Source', ''))
        document_url = first_attachment_url(fields.get('Fichier'))
        visuals = extract_visual_attachments(fields.get('Contenu_Visuel'))

        excerpt = strip_internal_tokens(fields.get('Extrait', ''))
        content = strip_internal_tokens(fields.get('Contenu_Nettoye', ''))
        if not content:
            content = strip_internal_tokens(fields.get('Contenu_Texte', ''))

        keywords = split_keywords(fields.get('Mots_Cles', ''))
        key_figures = star_map.get(article_id, [])
        if not key_figures:
            key_figures = fallback_key_figures(fields, excerpt)
        key_figures = sanitize_key_figures(key_figures, content, excerpt)

        date_publication = safe_date(fields.get('Date_Publication', ''))
        catalog_meta = build_catalog_metadata(
            article_id,
            title,
            theme_code,
            date_publication,
            source,
        )

        article_payload = {
            'id': article_id,
            'sectorId': sector_id,
            'themeId': theme_id,
            'series': series,
            'title': title,
            'source': source,
            'date': date_publication,
            'excerpt': excerpt,
            'content': content,
            'keywords': keywords,
            'keyFigures': key_figures,
            'catalogId': catalog_meta['catalogId'],
            'catalogSlug': catalog_meta['catalogSlug'],
            'catalogTimestampUTC': catalog_meta['catalogTimestampUTC'],
            'catalogFingerprint': catalog_meta['catalogFingerprint'],
        }

        if document_url:
            article_payload['documentUrl'] = document_url

        if visuals:
            article_payload['visuals'] = visuals

        articles.append(article_payload)

    articles.sort(key=lambda row: (row.get('date', ''), row.get('title', '')), reverse=True)
    sectors = sorted(sector_index.values(), key=lambda row: row.get('id', ''))
    themes = sorted(theme_index.values(), key=lambda row: (row.get('code', ''), row.get('label', '')))

    return {
        'generatedAt': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'sectors': sectors,
        'themes': themes,
        'articles': articles,
    }


def write_catalog_ts(payload, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_payload = json.dumps(payload, indent=2, ensure_ascii=True)
    content = (
        '// Auto-generated from Airtable public catalog dataset.\n'
        '// Run scripts/export_public_catalog_for_pwa.py to refresh.\n\n'
        f'export const PUBLIC_CATALOG = {json_payload} as const;\n'
    )
    output_path.write_text(content, encoding='utf-8')


def main():
    load_dotenv(ROOT_DIR / '.env')
    load_dotenv(ROOT_DIR / 'config' / '.env')

    parser = argparse.ArgumentParser(description='Export Airtable public catalog for Prova clients.')
    parser.add_argument(
        '--output-dir',
        default=os.getenv('PROVA_PWA_OUTPUT_DIR', DEFAULT_OUTPUT_DIR),
        help='Target app directory containing src/data (default: prova-pwa).',
    )
    args = parser.parse_args()
    output_path = resolve_output_path(args.output_dir)

    api_token = os.getenv('AIRTABLE_ACCESS_TOKEN')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not api_token or not base_id:
        print('ERROR: AIRTABLE_ACCESS_TOKEN or AIRTABLE_BASE_ID missing in environment.')
        raise SystemExit(1)

    taxonomy = load_taxonomy(PARSED_DATA_PATH)
    api = Api(api_token)

    payload = build_live_catalog(api, base_id, taxonomy)
    write_catalog_ts(payload, output_path)

    print('OK: PWA public catalog generated.')
    print(f"- Output: {output_path}")
    print(f"- Sectors: {len(payload.get('sectors', []))}")
    print(f"- Themes: {len(payload.get('themes', []))}")
    print(f"- Articles exported: {len(payload.get('articles', []))}")


if __name__ == '__main__':
    main()
