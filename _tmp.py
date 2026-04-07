import os
import json
import io
import re
import fitz  # PyMuPDF
from docx import Document
from google import genai
import requests
import pandas as pd
from pyairtable import Api, Table
from pyairtable.formulas import match, AND
import pyairtable
from dotenv import load_dotenv
import zipfile
import cloudinary
import cloudinary.uploader
import time
import difflib

# Load params
load_dotenv(dotenv_path='config/.env')

PRIMARY_GEMINI_MODEL = (os.getenv('GEMINI_MODEL') or 'gemini-2.5-flash').strip()
BACKUP_GEMINI_MODEL = (os.getenv('GEMINI_BACKUP_MODEL') or 'gemini-2.5-flash-lite').strip()
SOURCE_MATCH_GEMINI_MODEL = (os.getenv('GEMINI_SOURCE_MATCH_MODEL') or BACKUP_GEMINI_MODEL).strip()


def _unique_model_candidates(*model_names):
    candidates = []
    for model_name in model_names:
        clean_name = str(model_name or '').strip()
        if clean_name and clean_name not in candidates:
            candidates.append(clean_name)
    return candidates


def _is_retryable_gemini_error(error_text):
    normalized_error = str(error_text or '').upper()
    retryable_markers = ['503', '429', 'UNAVAILABLE', 'RESOURCE_EXHAUSTED', 'DEADLINE_EXCEEDED', 'INTERNAL']
    return any(marker in normalized_error for marker in retryable_markers)


def _split_pipe_values(value):
    if value is None:
        return []
    parts = re.split(r'\s*\|\s*|[\r\n]+', str(value))
    return [part.strip() for part in parts if str(part).strip()]


def _join_pipe_unique(values):
    seen = set()
    out = []
    for value in values:
        clean_value = re.sub(r'\s+', ' ', str(value)).strip()
        if clean_value and clean_value not in seen:
            seen.add(clean_value)
            out.append(clean_value)
    return ' | '.join(out)


def _merge_pipe_values(existing_value, incoming_value):
    merged = _split_pipe_values(existing_value) + _split_pipe_values(incoming_value)
    return _join_pipe_unique(merged)


def _collect_star_parts(value):
    if value is None:
        return []

    if isinstance(value, list):
        parts = []
        for item in value:
            parts.extend(_collect_star_parts(item))
        return parts

    if isinstance(value, dict):
        star_keys = [
            'chiffre',
            'chiffre_star',
            'valeur',
            'value',
            'nombre',
            'number',
            'montant',
            'statistique',
        ]
        parts = []
        for key in star_keys:
            if key in value:
                parts.extend(_collect_star_parts(value.get(key)))
        return parts

    text = str(value).strip()
    return [text] if text else []


def _collect_legend_parts(value, allow_scalar=True):
    if value is None:
        return []

    if isinstance(value, list):
        parts = []
        for item in value:
            parts.extend(_collect_legend_parts(item, allow_scalar=allow_scalar))
        return parts

    if isinstance(value, dict):
        legend_keys = [
            'legende',
            'legende_chiffre',
            'contexte',
            'description',
            'detail',
            'explication',
            'texte',
            'text',
        ]
        parts = []
        for key in legend_keys:
            if key in value:
                parts.extend(_collect_legend_parts(value.get(key), allow_scalar=True))
        return parts

    if not allow_scalar:
        return []

    text = str(value).strip()
    return [text] if text else []


KEY_FIGURE_CATEGORY_WEIGHTS = {
    'financier': 7,
    'dimension': 6,
    'duree': 5,
    'comparaison': 5,
    'quantite': 4,
    'date': 3,
}

KEY_FIGURE_CONTEXT_HINTS = (
    'projet',
    'ouvrage',
    'etude',
    'analyse',
    'cout',
    'coût',
    'budget',
    'investissement',
    'longueur',
    'profondeur',
    'trajet',
    'duree',
    'section',
    'comparaison',
    'evolution',
    'horizon',
)

KEY_FIGURE_GENERIC_LEGEND_PATTERN = re.compile(
    r"(?i)^(information\s+cle|indicateur\s+quantitatif\s+cle|montant\s+financier\s+cle|valeur\s+cle|donnee\s+cle|donnée\s+cle)$"
)


def _normalize_ocr_artifacts(value):
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
        'coût': 'cout',
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


def _normalize_context_text(value):
    text = str(value or '')
    text = text.replace('**', '')
    text = _clean_star_candidate(text)
    text = re.sub(r'\s+', ' ', text).strip(' .;:-|')
    return text


def _extract_time_hint(context_text):
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
            return _clean_key_figure_legend(match.group(0))
    return ''


def _extract_route_hint(context_text):
    context = str(context_text or '')
    route_match = re.search(r'([A-Z][A-Za-zÀ-ÿ\-]+)\s*[-–]\s*([A-Z][A-Za-zÀ-ÿ\-]+)', context)
    if not route_match:
        return ''
    origin = route_match.group(1).strip()
    destination = route_match.group(2).strip()
    return f'{origin}-{destination}'


def _infer_metric_axis(context_text, value_text):
    context_lower = str(context_text or '').lower()
    value_lower = str(value_text or '').lower()

    if any(token in context_lower for token in ['comparaison', 'vs', 'benchmark', 'plus que', 'moins que']):
        return 'comparaison'

    if any(token in context_lower for token in ['cout', 'coût', 'coût', 'budget', 'invest', 'prix', 'montant']) or STAR_MONEY_PATTERN.search(value_lower):
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


def _extract_subject_hint(context_text):
    context = str(context_text or '')
    context_lower = context.lower()

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


def _normalize_key_figure_category(value):
    category = str(value or '').strip().lower()
    if not category:
        return ''

    mapping = {
        'finance': 'financier',
        'financial': 'financier',
        'money': 'financier',
        'dimension': 'dimension',
        'size': 'dimension',
        'duree': 'duree',
        'duration': 'duree',
        'time': 'duree',
        'date': 'date',
        'quantite': 'quantite',
        'quantity': 'quantite',
        'comparaison': 'comparaison',
        'comparison': 'comparaison',
        'comparatif': 'comparaison',
    }
    return mapping.get(category, category if category in KEY_FIGURE_CATEGORY_WEIGHTS else '')


def _clean_key_figure_legend(value):
    legend = _normalize_ocr_artifacts(value)
    legend = re.sub(r'\s+', ' ', str(legend or '')).strip(' .;:-|')
    return legend.replace(' :', ':')


def _has_what_context(legend):
    clean_legend = _clean_key_figure_legend(legend)
    if not clean_legend:
        return False

    if KEY_FIGURE_GENERIC_LEGEND_PATTERN.match(clean_legend):
        return False

    legend_lower = clean_legend.lower()
    if len(clean_legend.split()) < 2:
        return False

    has_metric_noun = any(
        token in legend_lower
        for token in [
            'cout',
            'budget',
            'investissement',
            'montant',
            'longueur',
            'profondeur',
            'hauteur',
            'distance',
            'duree',
            'temps',
            'trajet',
            'part',
            'taux',
            'volume',
            'quantite',
            'production',
            'consommation',
            'population',
            'comparaison',
            'evolution',
            'jalon',
            'annee',
        ]
    )

    has_subject_or_scope = any(
        token in legend_lower
        for token in [
            'projet',
            'ouvrage',
            'article',
            'secteur',
            'entreprise',
            'marche',
            'region',
            'ville',
            'pays',
            'ligne',
            'section',
            'service',
            'programme',
            'scenario',
            'horizon',
        ]
    )

    return has_metric_noun or has_subject_or_scope


def _is_contextual_key_figure_legend(legend):
    clean_legend = _clean_key_figure_legend(legend)
    if not clean_legend:
        return False

    if not _has_what_context(clean_legend):
        return False

    legend_lower = clean_legend.lower()
    if re.search(r'\b(?:18|19|20)\d{2}\b', legend_lower):
        return True
    if '(' in clean_legend and ')' in clean_legend:
        return True
    return any(hint in legend_lower for hint in KEY_FIGURE_CONTEXT_HINTS)


def _extract_value_from_dict(payload, keys):
    for key in keys:
        if key in payload:
            value = payload.get(key)
            if isinstance(value, (dict, list)):
                continue
            clean_value = str(value or '').strip()
            if clean_value:
                return clean_value
    return ''


def _collect_structured_key_figures(value):
    if value is None:
        return []

    if isinstance(value, list):
        entries = []
        for item in value:
            entries.extend(_collect_structured_key_figures(item))
        return entries

    if isinstance(value, dict):
        entries = []

        raw_value = _extract_value_from_dict(
            value,
            ['valeur', 'value', 'chiffre', 'chiffre_star', 'nombre', 'number', 'metric'],
        )
        raw_legend = _extract_value_from_dict(
            value,
            ['legende', 'legend', 'label', 'description', 'contexte', 'detail', 'explication'],
        )
        raw_equivalence = _extract_value_from_dict(
            value,
            ['equivalence', 'equivalent', 'equivalent_value', 'conversion'],
        )
        raw_category = _extract_value_from_dict(value, ['categorie', 'category', 'type'])

        clean_value = _clean_star_candidate(raw_value)
        clean_legend = _clean_key_figure_legend(raw_legend)
        clean_equivalence = _clean_star_candidate(raw_equivalence)
        clean_category = _normalize_key_figure_category(raw_category)

        if clean_value and clean_legend:
            if clean_equivalence:
                value_key = _candidate_key(clean_value)
                eq_key = _candidate_key(clean_equivalence)
                if eq_key and eq_key not in value_key:
                    clean_value = f'{clean_value} ({clean_equivalence})'

            entries.append(
                {
                    'value': clean_value,
                    'legend': clean_legend,
                    'category': clean_category,
                }
            )

        for nested_key in ('chiffres_cles', 'chiffres_stars', 'key_figures', 'items', 'data'):
            if nested_key in value:
                entries.extend(_collect_structured_key_figures(value.get(nested_key)))

        return entries

    return []


def _score_structured_key_figure(entry):
    value_text = _clean_star_candidate(entry.get('value', ''))
    legend_text = _clean_key_figure_legend(entry.get('legend', ''))
    category = _normalize_key_figure_category(entry.get('category', ''))

    if not value_text or not legend_text or not re.search(r'\d', value_text):
        return -10

    score = KEY_FIGURE_CATEGORY_WEIGHTS.get(category, 3)

    if STAR_MONEY_PATTERN.search(value_text):
        score += 4
    if STAR_UNIT_PATTERN.search(value_text):
        score += 3
    if _is_plain_year(value_text) and category != 'date':
        score -= 6

    if _is_contextual_key_figure_legend(legend_text):
        score += 3
    elif _has_what_context(legend_text):
        score += 1
    else:
        score -= 2

    if re.search(r'\b(?:18|19|20)\d{2}\b', legend_text):
        score += 1

    if re.search(r'(?i)\bde\b.+\ba\b.+\b\d', legend_text):
        score += 1

    return score


def _select_structured_key_figures(entries, max_items=6):
    candidates = []
    seen = set()

    for idx, entry in enumerate(entries or []):
        value_text = _clean_star_candidate(entry.get('value', ''))
        legend_text = _clean_key_figure_legend(entry.get('legend', ''))
        category = _normalize_key_figure_category(entry.get('category', ''))

        if not value_text or not legend_text or not re.search(r'\d', value_text):
            continue

        key = f"{_candidate_key(value_text)}::{_candidate_key(legend_text)}"
        if not key or key in seen:
            continue

        score = _score_structured_key_figure(
            {
                'value': value_text,
                'legend': legend_text,
                'category': category,
            }
        )
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': value_text,
                'legend': legend_text,
                'category': category,
                'score': score,
                'order': idx,
            }
        )

    
    def get_year(txt):
        import re
        m = re.search(r'\b(19|20)\d{2}\b', str(txt))
        return int(m.group(0)) if m else 9999

    candidates.sort(key=lambda item: (get_year(item['legend'] + " " + item['value']), item['order']))
    
    selected = candidates[:max_items]
    # Supprimé pour forcer l'ordre chrono
    return selected


def _split_value_equivalence(value_text):
    clean_value = _clean_star_candidate(value_text)
    if not clean_value:
        return '', None

    equivalence_match = re.search(
        r'\(([^)]*(?:dh|mad|eur|usd|€|\$)[^)]*)\)\s*$',
        clean_value,
        flags=re.IGNORECASE,
    )
    if not equivalence_match:
        return clean_value, None

    equivalence_text = _clean_star_candidate(equivalence_match.group(1))
    clean_main_value = re.sub(
        r'\s*\([^)]*(?:dh|mad|eur|usd|€|\$)[^)]*\)\s*$',
        '',
        clean_value,
        flags=re.IGNORECASE,
    ).strip()
    return clean_main_value, (equivalence_text or None)


def _infer_key_figure_category(legend_text, value_text, provided_category=''):
    normalized_category = _normalize_key_figure_category(provided_category)
    if normalized_category:
        return normalized_category

    haystack = f"{legend_text} {value_text}".lower()
    if any(token in haystack for token in ['comparaison', 'vs', 'manche']):
        return 'comparaison'
    if any(token in haystack for token in ['cout', 'coût', 'coût', 'budget', 'milliard', 'million', 'dh', 'mad', 'eur', '€', '$']):
        return 'financier'
    if any(token in haystack for token in ['heure', 'heures', 'trajet', 'duree']):
        return 'duree'
    if any(token in haystack for token in ['km', 'm ', 'metre', 'longueur', 'profondeur', 'surface']):
        return 'dimension'
    if re.fullmatch(r'(?:18|19|20)\d{2}', str(value_text or '').strip()):
        return 'date'
    return 'quantite'


STAR_UNIT_PATTERN = re.compile(
    r'(?i)(%|\b(?:dh|mad|eur|usd|mrd|md|million|milliard|milliards|millions|km|m2|m3|kg|tonnes?|heures?|jours?|ans?)\b)'
)
STAR_MONEY_PATTERN = re.compile(r'(?i)(?:€|\$|\b(?:dh|mad|eur|usd|mrd|md|million|milliard|milliards|millions)\b)')
STAR_CONTEXT_PATTERN = re.compile(
    r'(?i)(cout|budget|montant|invest|depense|recette|taux|part|volume|capacite|longueur|profondeur|temps|duree|production)'
)
STAR_TAIL_UNIT_PATTERN = re.compile(
    r"^\s*(?:d['’]\s*)?(%|dh|mad|eur|usd|mrd|md|km|m2|m3|kg|tonnes?|heures?|jours?|ans?|m)\b",
    flags=re.IGNORECASE,
)
STAR_MONEY_VALUE_PATTERN = re.compile(
    r"(?i)(?:plus\s+de\s+)?\d+(?:[.,]\d+)?\s*(?:milliards?|millions?)?\s*(?:d['’]\s*)?(?:€|\$|dh|mad|eur|usd|ç)",
)


def _clean_star_candidate(value):
    text = _normalize_ocr_artifacts(value)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.strip('.,;:-|')


def _is_plain_year(value):
    return bool(re.fullmatch(r'(?:18|19|20)\d{2}', str(value or '').strip()))


def _candidate_key(value):
    return re.sub(r'[^a-z0-9]+', '', str(value or '').lower())


def _extract_tail_unit(tail_text):
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

    match = STAR_TAIL_UNIT_PATTERN.search(clean_tail)
    if not match:
        return ''
    return str(match.group(1) or '').strip()


def _enrich_value_with_tail_unit(value, tail_text):
    clean_value = _clean_star_candidate(value)
    if not clean_value:
        return ''

    if STAR_UNIT_PATTERN.search(clean_value) or STAR_MONEY_PATTERN.search(clean_value):
        return clean_value

    tail_unit = _extract_tail_unit(tail_text)
    if not tail_unit:
        return clean_value

    if tail_unit == '%':
        return f'{clean_value}%'

    return f'{clean_value} {tail_unit}'


def _infer_star_legend_from_context(context_text, value):
    context = _normalize_context_text(context_text)
    if not context:
        return ''

    value_text = _clean_star_candidate(value)
    context_lower = context.lower()
    axis = _infer_metric_axis(context, value_text)
    time_hint = _extract_time_hint(context)
    route_hint = _extract_route_hint(context)
    subject_hint = _extract_subject_hint(context)

    if axis == 'duree' and route_hint:
        legend = f'Temps de trajet {route_hint}'
    elif axis == 'financier':
        if any(token in context_lower for token in ['budget', 'investissement', 'investi', 'investis']):
            legend = f'Budget ou investissement clé {subject_hint}'.strip()
        elif any(token in context_lower for token in ['cout', 'coût', 'coût', 'prix', 'montant']):
            legend = f'Coût estimé {subject_hint}'.strip()
        else:
            legend = f'Montant financier clé {subject_hint}'.strip()
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
    if time_hint and axis in {'financier', 'duree', 'dimension_longueur', 'dimension_mesure', 'comparaison', 'variation', 'date'}:
        if time_hint.lower() not in legend.lower():
            legend = f'{legend} ({time_hint})'

    if len(legend.split()) < 3:
        context_without_value = context
        if value_text:
            context_without_value = re.sub(re.escape(value_text), '', context_without_value, flags=re.IGNORECASE)
        context_without_value = re.sub(r'\s+', ' ', context_without_value).strip(' .;:-')
        if context_without_value:
            legend = context_without_value[:140]

    return _clean_key_figure_legend(legend)


def _first_numeric_value(value):
    match = re.search(r'\d+(?:[.,]\d+)?', str(value or ''))
    if not match:
        return None

    numeric_text = match.group(0).replace(',', '.')
    try:
        return float(numeric_text)
    except Exception:
        return None


def _first_numeric_token(value):
    match = re.search(r'\d+(?:[.,]\d+)?', str(value or ''))
    if not match:
        return ''
    return match.group(0).replace(',', '.')


def _currency_bucket(value):
    value_lower = str(value or '').lower()
    if any(token in value_lower for token in ['dh', 'mad']):
        return 'local'
    if any(token in value_lower for token in ['€', 'eur', '$', 'usd']):
        return 'foreign'
    return ''


def _extract_markdown_highlight_candidates(content):
    text = str(content or '')
    if not text:
        return []

    highlights = []
    seen = set()
    suppressed_keys = set()
    for match in re.finditer(r'\*\*([^*]+)\*\*', text):
        raw_value = match.group(1)
        prefix_text = text[max(0, match.start() - 20):match.start()]
        tail_text = text[match.end():match.end() + 28]
        clean_value = _enrich_value_with_tail_unit(raw_value, tail_text)
        if re.search(r'(?i)plus\s+de\s*$', prefix_text):
            clean_value = f'plus de {clean_value}'

        if not clean_value or not re.search(r'\d', clean_value):
            continue

        value_key_initial = _candidate_key(clean_value)
        raw_key = _candidate_key(_clean_star_candidate(raw_value))
        if value_key_initial in suppressed_keys or raw_key in suppressed_keys:
            continue

        line_start = text.rfind('\n', 0, match.start())
        line_end = text.find('\n', match.end())
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1
        if line_end == -1:
            line_end = len(text)

        context_text = text[line_start:line_end]
        if len(context_text.strip()) < 24:
            context_start = max(0, match.start() - 80)
            context_end = min(len(text), match.end() + 80)
            context_text = text[context_start:context_end]
        context_plain = context_text.replace('**', '')

        # Rebuild time values like "5 heure 30" instead of separate "5" and "30".
        if re.search(r'(?i)\bheure', tail_text):
            minute_match = re.search(r'\*\*(\d{1,2})\*\*', text[match.end():match.end() + 40])
            if minute_match and re.fullmatch(r'\d+(?:[.,]\d+)?', _clean_star_candidate(raw_value)):
                minute_value = minute_match.group(1)
                clean_value = f"{_clean_star_candidate(raw_value)} heure {minute_value}"
                suppressed_keys.add(_candidate_key(minute_value))

        # Ignore intermediate timeline fragments such as "17 ans plus tard" when a monetary value follows.
        if re.search(r'(?i)\bans?\b', clean_value) and 'plus tard' in context_plain.lower() and STAR_MONEY_PATTERN.search(context_plain):
            suppressed_keys.add(_candidate_key(clean_value))
            continue

        # Ignore pure year fragments when the same clause already carries a monetary figure.
        if re.fullmatch(r'(?i)(?:fin\s+)?(?:18|19|20)\d{2}', clean_value) and STAR_MONEY_PATTERN.search(context_plain):
            suppressed_keys.add(_candidate_key(clean_value))
            continue

        if STAR_MONEY_PATTERN.search(clean_value):
            money_values = []
            for money_match in STAR_MONEY_VALUE_PATTERN.finditer(context_plain):
                money_candidate = _clean_star_candidate(money_match.group(0))
                if money_candidate and re.search(r'\d', money_candidate):
                    money_values.append(money_candidate)

            selected_equivalence = ''
            clean_value_number = _first_numeric_token(clean_value)
            clean_value_currency = _currency_bucket(clean_value)

            for money_candidate in money_values:
                money_key = _candidate_key(money_candidate)
                if not money_key or money_key == _candidate_key(clean_value):
                    continue

                candidate_number = _first_numeric_token(money_candidate)
                candidate_currency = _currency_bucket(money_candidate)
                same_number = bool(clean_value_number and candidate_number and clean_value_number == candidate_number)
                different_currency = bool(clean_value_currency and candidate_currency and clean_value_currency != candidate_currency)

                if different_currency and not same_number:
                    selected_equivalence = money_candidate
                    break

                if not selected_equivalence and not same_number:
                    selected_equivalence = money_candidate

            if selected_equivalence:
                selected_equivalence_key = _candidate_key(selected_equivalence)
                clean_value = f'{clean_value} ({selected_equivalence})'

                # Suppress local-currency duplicate when a foreign-currency primary value exists in same clause.
                if clean_value_currency == 'local' and _currency_bucket(selected_equivalence) == 'foreign':
                    suppressed_keys.add(_candidate_key(clean_value))
                    continue

                if selected_equivalence_key:
                    suppressed_keys.add(selected_equivalence_key)

        key = _candidate_key(clean_value)
        if key and key not in seen and key not in suppressed_keys:
            seen.add(key)
            highlights.append(
                {
                    'value': clean_value,
                    'legend': _infer_star_legend_from_context(context_plain, clean_value),
                }
            )

    return highlights


def _score_star_candidate(value, legend, highlighted_keys):
    text = _clean_star_candidate(value)
    legend_text = _clean_star_candidate(legend)

    if not text or not re.search(r'\d', text):
        return -10

    score = 0
    key = _candidate_key(text)
    if key in highlighted_keys:
        # Bold/visually emphasized figures are strong signals in the article structure.
        score += 7

    if STAR_MONEY_PATTERN.search(text):
        score += 4

    if STAR_UNIT_PATTERN.search(text):
        score += 3

    if re.search(r'[<>+=]', text):
        score += 2

    if STAR_CONTEXT_PATTERN.search(legend_text):
        score += 2

    if _has_what_context(legend_text):
        score += 1

    if _is_plain_year(text):
        score -= 6

    if not STAR_UNIT_PATTERN.search(text) and not STAR_MONEY_PATTERN.search(text):
        numeric_value = _first_numeric_value(text)
        if numeric_value is not None and numeric_value < 50:
            score -= 2

    if len(re.sub(r'\D', '', text)) >= 5:
        score += 1

    return score


def _sanitize_star_candidates(stars, legends, highlighted_candidates=None, fallback_legend='', structured_candidates=None):
    fallback = _clean_star_candidate(fallback_legend).replace('|', ' / ')
    if not fallback:
        fallback = 'information clé mise en evidence.'

    highlighted_candidates = highlighted_candidates or []
    structured_candidates = structured_candidates or []
    highlighted_keys = {
        _candidate_key(candidate.get('value', ''))
        for candidate in highlighted_candidates
        if _candidate_key(candidate.get('value', ''))
    }

    candidates = []
    seen = set()

    for idx, star in enumerate(stars):
        clean_star = _clean_star_candidate(star)
        if not clean_star:
            continue

        legend = ''
        if legends:
            legend = legends[idx] if idx < len(legends) else legends[-1]
        clean_legend = _clean_star_candidate(legend)

        key = _candidate_key(clean_star)
        if not key or key in seen:
            continue

        score = _score_star_candidate(clean_star, clean_legend, highlighted_keys)
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': clean_star,
                'legend': clean_legend or fallback,
                'score': score,
                'order': idx,
            }
        )

    # Structured model output (value + legend linked) has priority over loose pairs.
    for idx, structured in enumerate(structured_candidates):
        clean_value = _clean_star_candidate(structured.get('value', ''))
        clean_legend = _clean_key_figure_legend(structured.get('legend', ''))

        key = _candidate_key(clean_value)
        if not clean_value or not key or key in seen:
            continue

        score = _score_star_candidate(clean_value, clean_legend or fallback, highlighted_keys) + 4
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': clean_value,
                'legend': clean_legend or fallback,
                'score': score,
                'order': len(stars) + idx,
            }
        )

    for idx, highlighted in enumerate(highlighted_candidates):
        clean_value = _clean_star_candidate(highlighted.get('value', ''))
        legend_hint = _clean_star_candidate(highlighted.get('legend', ''))
        key = _candidate_key(clean_value)
        if not clean_value or not key or key in seen:
            continue

        score = _score_star_candidate(clean_value, legend_hint or fallback, highlighted_keys)
        if score < 1:
            continue

        seen.add(key)
        candidates.append(
            {
                'value': clean_value,
                'legend': legend_hint or fallback,
                'score': score + 1,
                'order': len(stars) + idx,
            }
        )

    
    def get_year(txt):
        import re
        m = re.search(r'\b(19|20)\d{2}\b', str(txt))
        return int(m.group(0)) if m else 9999

    candidates.sort(key=lambda item: (get_year(item['legend'] + " " + item['value']), item['order']))
    
    selected = candidates[:3]

    if not selected:
        rescue = []
        for idx, star in enumerate(stars):
            clean_value = _clean_star_candidate(star)
            key = _candidate_key(clean_value)
            if not clean_value or not key or key in seen:
                continue
            if not re.search(r'\d', clean_value):
                continue
            legend = ''
            if legends:
                legend = legends[idx] if idx < len(legends) else legends[-1]
            rescue.append(
                {
                    'value': clean_value,
                    'legend': _clean_star_candidate(legend) or fallback,
                }
            )
            if len(rescue) >= 3:
                break

        selected = rescue

    selected_stars = [item['value'] for item in selected]
    selected_legends = [item['legend'] for item in selected]
    return selected_stars, selected_legends


def sanitize_star_values(star_values, legend_values, content_text='', fallback_legend='', structured_candidates=None):
    stars = _split_pipe_values(star_values)
    legends = _split_pipe_values(legend_values)
    highlighted_candidates = _extract_markdown_highlight_candidates(content_text)
    selected_stars, selected_legends = _sanitize_star_candidates(
        stars,
        legends,
        highlighted_candidates=highlighted_candidates,
        fallback_legend=fallback_legend,
        structured_candidates=structured_candidates,
    )

    return _join_pipe_unique(selected_stars), _join_pipe_unique(selected_legends)


def _sanitize_normalized_star_fields(normalized_payload, structured_candidates=None):
    if not isinstance(normalized_payload, dict):
        return normalized_payload

    star_value, legend_value = sanitize_star_values(
        normalized_payload.get('Chiffre_Star', ''),
        normalized_payload.get('Legende_Chiffre', ''),
        content_text=normalized_payload.get('Contenu_Nettoye', ''),
        fallback_legend=normalized_payload.get('Extrait', ''),
        structured_candidates=structured_candidates,
    )

    if star_value:
        normalized_payload['Chiffre_Star'] = star_value
        if legend_value:
            normalized_payload['Legende_Chiffre'] = legend_value
        else:
            normalized_payload.pop('Legende_Chiffre', None)
    else:
        normalized_payload.pop('Chiffre_Star', None)
        normalized_payload.pop('Legende_Chiffre', None)

    return normalized_payload

class TextExtractor:
    @staticmethod
    def extract_docx(file_obj):
        '''Extracts text, table content, and floating text (textboxes) from DOCX using direct XML parsing.'''
        try:
            doc = Document(file_obj)
            text_parts = []
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            def get_para_text(p_element):
                '''Extracts text from a paragraph element considering runs.'''
                return ''.join([node.text for node in p_element.findall('.//w:t', ns) if node.text])

            # 1. Main Body Iteration (Paragraphs and Tables in order)
            for element in doc.element.body:
                if element.tag.endswith('}p'):
                    text = get_para_text(element)
                    if text.strip():
                        text_parts.append(text.strip())     
                elif element.tag.endswith('}tbl'):
                    table_rows = []
                    for tr in element.findall('.//w:tr', ns):
                        row_cells = []
                        for tc in tr.findall('.//w:tc', ns):
                            cell_text_parts = []
                            for p in tc.findall('.//w:p', ns):
                                pt = get_para_text(p)
                                if pt.strip():
                                    cell_text_parts.append(pt.strip())
                            full_cell_text = ' '.join(cell_text_parts)
                            if full_cell_text:
                                row_cells.append(full_cell_text)
                        if row_cells:
                            table_rows.append(' | '.join(row_cells))
                    if table_rows:
                        text_parts.append(f"\n[Tableau]\n" + "\n".join(table_rows) + "\n")

            # 2. Text Boxes / Floating Content
            for txbx in doc.element.body.findall('.//w:txbxContent', ns):
                txbx_texts = []
                for p in txbx.findall('.//w:p', ns):
                    pt = get_para_text(p)
                    if pt.strip():
                        txbx_texts.append(pt.strip())
                if txbx_texts:
                    text_parts.append(f"\n[Encadré/ZoneText]\n" + "\n".join(txbx_texts))

            # 3. Footers
            for section in doc.sections:
                if section.footer:
                    for p in section.footer.paragraphs:
                        if p.text.strip():
                            text_parts.append(f"[Pied_de_page] {p.text.strip()}")
            
            return '\n'.join(text_parts)
        except Exception as e:
            return f'[Erreur lecture DOCX: {e}]'

    @staticmethod
    def extract(file_obj, filename):
        '''Extracts text from PDF or DOCX file object.'''
        text = ''
        try:
            file_obj.seek(0)
            if filename.lower().endswith('.pdf'):
                with fitz.open(stream=file_obj.read(), filetype='pdf') as doc:
                    for page in doc:
                        text += page.get_text() + '\n'
            elif filename.lower().endswith('.docx'):
                text = TextExtractor.extract_docx(file_obj)
            else:
                return None
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception as e:
            return f'Error extracting {filename}: {str(e)}'

class GeminiProcessor:
    def __init__(self, api_key, hierarchy_path='config/parsed_data.json', use_groq=False, groq_key=None):      
        self.use_groq = use_groq
        self.groq_key = groq_key or os.getenv('GROQ_API_KEY')
        self.api_key = api_key
        # Initialize Client
        if not self.use_groq:
            self.client = genai.Client(api_key=self.api_key)
            self.model_candidates = _unique_model_candidates(PRIMARY_GEMINI_MODEL, BACKUP_GEMINI_MODEL)
        else:
            self.model_candidates = ["llama-3.3-70b-versatile"]

        self.valid_codes = self._load_valid_codes(hierarchy_path)
    def _load_valid_codes(self, hierarchy_path):
        codes = {}
        if os.path.exists(hierarchy_path):
            with open(hierarchy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'themes' in data:
                    for t in data['themes']:
                        codes[t['code']] = t['nom']
        return codes

    def analyze_document(self, text):
        '''Sends text to Gemini for classification with structured extractions.'''
        context_str = '\n'.join([f'- {k}: {v}' for k, v in self.valid_codes.items()])
        
        truncated_text = text[:300000]
        
        prompt = f'''Tu es un expert archiviste pour le Centre d'Études (CERD). Analyse le document texte brut fourni et extrais les informations pour renvoyer un objet JSON structuré.

RÈGLES D'EXTRACTION STRICTES ("The Clean Split") :
1. Identifie d'abord toutes les métadonnées de l'article (Titre, Date, Source, etc.).
2. SUPPRIME impérativement ces métadonnées du corps du texte.
3. Le champ "contenu_nettoye" ne DOIT contenir QUE le corps de l'article, exactement tel qu'il apparaît après avoir enlevé les métadonnées de l'en-tête.
4. Tu DOIS faire un COPIER-COLLER EXACT du texte d'origine. Ne change aucun mot, n'ajoute AUCUN titre, n'ajoute pas de "###". Tu ne dois ajouter aucun nouveau mot de ton crû.

COMPREHENSION ARTICLE (OBLIGATOIRE AVANT EXTRACTION) :
- Lis l'article en entier et identifie son sujet principal, les acteurs et la logique narrative.
- Repere les sequences temporelles (dates, periodes, "x ans plus tard", horizons) et les evolutions de valeurs.
- Si une meme metrique change dans le temps, conserve chaque point de mesure avec sa reference temporelle (ex: valeur a t1, valeur a t2, valeur a t3).
- Applique ces regles a tout type de sujet (pas seulement infrastructure): economie, energie, sante, social, etc.

FORMATAGE MARKDOWN REQUIS (OBLIGATOIRE pour `contenu_nettoye`) :
- Ton objectif est de recopier fidèlement le corps de l'article mais de l'organiser et le formater.
- Aère OBLIGATOIREMENT le texte avec des sauts de ligne (\n\n) pour séparer les paragraphes d'origine.
- Ne mets PAS le texte normal en gras. Par contre, pour les CHIFFRES CLÉS extraits (et UNIQUEMENT eux), affiche les "en ligne" mais entoure-les avec des accents graves (backticks) pour les marquer comme du code (`chiffre`). N'entoure AUCUN autre mot de la sorte.
- Si le texte contient des tirets en début de ligne, convertis-les en puces Markdown standard (`- `).
- EXEMPLE ATTENDU (dans le texte) : le projet évalué à `5,3 milliards d'euros` en 2008.
- INTERDIT : utiliser de grands titres Markdown (###) pour les chiffres dans le corps du texte. Interdit de mettre du texte normal en backticks.
- EXEMPLE INTERDIT (NE FAIS JAMAIS ÇA) : `**Juan Carlos**` (ne mets pas en gras les noms, seulement les chiffres clés).

REGLES CHIFFRES CLES CONTEXTUALISES (OBLIGATOIRE) :
- N'extrais JAMAIS un chiffre seul sans contexte. La légende originale de l'article doit être fidèlement respectée avec TOUS SES ACCENTS et sa ponctuation.
- ORDONNE CHRONOLOGIQUEMENT : S'il y a plusieurs valeurs dans le temps, trie TOUJOURS du plus ancien au plus récent (ex: 2008 (ancien), puis "17 ans plus tard", puis 2025 (récent)).
- L'information doit être l'élément "star" actionnable.
- Chaque légende doit répondre explicitement à "QUOI", et idéalement "QUAND" / "OU".
- Conserve les équivalences monétaires exactes.
- Garde l'orthographe française correcte avec les accents (é, è, à, ç, û, etc.). Ne supprime jamais les accents des légendes (ex: écrit "Coût estimé" et non "Coût estimé").

REGLES POUR LES VISUELS (OBLIGATOIRE) :
- Lors de l'analyse de l'article, repère TOUTE légende, description, titre de galerie, graphe, carte ou illustration (ex: 'Une galerie sur le rocher de Gibraltar...', source 'Wikipédia', etc.) présente dans le texte.
- Extrais EXACTEMENT ce texte pour remplir le champ "titre_visuel".
  - SUPPRIME IMPÉRATIVEMENT intégralement ce texte descriptif / légende / titre de l'illustration du du reste du corps de l'article (`contenu_nettoye`) pour éviter un doublon quand on affichera le visuel au-dessus du texte.

CHAMPS JSON ATTENDUS (renvoie UNIQUEMENT un JSON, avec ces clés exactes, en minuscules) :
{{
  "titre": "Titre explicite de l'article.",
  "extrait": "Un petit résumé percutant. Si une section EXTRAIT ou RÉSUMÉ existe, la reprendre.",
  "mots_cles": "Mots-clés séparés par des virgules.",
  "source": "Entité productrice ou auteur. TEXTE EXACT du nom, je m'occupe de trouver le code ensuite.",
  "date_publication": "Format YYYY-MM-DD.",
  "code_theme_ref": "Trouve le nom du thème dans le texte et associe-le avec le code (ex: 90.1) pertinent tiré EXCLUSIVEMENT de la Liste des Codes.",
    "serie": "Classification c1, c2, c3, c4. Par défaut c1.",
    "chiffre_star": "Maximum 3 valeurs. Ordonnées chronologiquement. Garde les accents.",
    "legende_chiffre": "Maximum 3 légendes contextuelles (ex: Coût estimé). GARDE LES ACCENTS.",
    "chiffres_stars": "Optionnel: liste [{{\"chiffre\":\"...\", \"legende\":\"Avec accents !\"}}], triée chrono.",
    "chiffres_cles": [
        {{
            "legende": "Légende complète avec majuscules et accents (é, à, etc.)",
            "valeur": "Valeur exacte avec unité",
            "equivalence": "Valeur équivalente (ou null)",
            "categorie": "financier|dimension|duree|date|quantite|comparaison"
        }}
    ],
    "titre_visuel": "Texte exact de la légende, description, titre de galerie ou d'illustration (ex. avec mentions de source comme Wikipédia). Sinon laisse vide",
    "titre_visuel": "Texte exact de la légende, description, titre de galerie ou d'illustration (ex. avec mentions de source comme Wikipédia). Sinon laisse vide",
    "observations": ["2 à 4 constats exploitables écrits avec de bons accents"],
  "contenu_nettoye": "Le corps de l'article proprement extrait et parsé en Markdown."
}}

Liste des Codes Thématiques :
{context_str}

Texte Complet :
{truncated_text}
'''
        
        max_retries_per_model = 4
        retry_delay = 2
        last_error = ''

        for model_name in self.model_candidates:
            for attempt in range(max_retries_per_model):
                response_text = ""
                try:
                    if self.use_groq:
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
                        response_text = response.text

                    parsed = json.loads(response_text)
                    if isinstance(parsed, list):
                        parsed = parsed[0] if parsed else {}
                    return self._normalize_keys(parsed)
                except Exception as e:
                    error_str = str(e)
                    last_error = f'{model_name}: {error_str}'

                    # Try fallback JSON extraction if parsing failed due to extra data
                    if response_text:
                        try:
                            match = re.search(r'\{.*\}', response_text, re.DOTALL)
                            if match:
                                parsed = json.loads(match.group(0))
                                if isinstance(parsed, list):
                                    parsed = parsed[0] if parsed else {}
                                return self._normalize_keys(parsed)
                        except Exception:
                            pass

                    if _is_retryable_gemini_error(error_str) and attempt < max_retries_per_model - 1:
                        import time
                        import re
                        delay = retry_delay * (attempt + 1)
                        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                            delay_match1 = re.search(r"retryDelay':\s*'([0-9.]+)s'", error_str)
                            delay_match2 = re.search(r"retry in ([0-9.]+)s", error_str, re.IGNORECASE)
                            delay_match3 = re.search(r"try again in ([0-9.]+)s", error_str, re.IGNORECASE)
                            
                            if delay_match1:
                                delay = float(delay_match1.group(1)) + 5
                            elif delay_match2:
                                delay = float(delay_match2.group(1)) + 5
                            elif delay_match3:
                                delay = float(delay_match3.group(1)) + 2
                            else:
                                delay = 10 if self.use_groq else 60  # Default long wait for Gemini, shorter for Groq
                            
                            api_name = "Groq API" if self.use_groq else "Google API (Gemini)"
                            print(f"\n⚠️ Limite de requêtes {api_name} (429) atteinte.")
                            print(f"   Détail: {error_str}")
                            print(f"   -> Pause automatique de {delay:.1f} secondes...")

                        time.sleep(delay)
                        continue

                    if _is_retryable_gemini_error(error_str):
                        break

                    return {'error': last_error}

        return {'error': last_error or 'Gemini indisponible apres plusieurs tentatives.'}

    def _normalize_keys(self, data):
        '''Normalizes JSON keys for compatibility with frontend App.py fields'''
        if not isinstance(data, dict): return data

        mapping = {
            'titre': 'Titre',
            'extrait': 'Extrait',
            'mots_cles': 'Mots_Cles',
            'source': 'Source',
            'date_publication': 'Date_Publication',
            'code_theme_ref': 'Code_Theme_Ref',
            'serie': 'Série',
            'chiffre_star': 'Chiffre_Star',
            'legende_chiffre': 'Legende_Chiffre',
            'contenu_nettoye': 'Contenu_Nettoye'
        }

        star_keys = {
            'chiffre_star',
            'chiffres_stars',
            'chiffres_star',
            'chiffre_cle',
            'chiffres_cle',
        }

        structured_figure_keys = {
            'chiffres_cles',
            'chiffres_cles_structures',
            'key_figures',
            'key_figure_pairs',
        }

        legend_keys = {
            'legende_chiffre',
            'legendes_chiffres',
            'legendes_chiffre',
            'legende_chiffres',
            'contexte_chiffres',
        }

        normalized = {}
        structured_entries = []
        for k, v in data.items():
            normalized_key = str(k).lower().strip()

            if normalized_key in structured_figure_keys:
                structured_entries.extend(_collect_structured_key_figures(v))
                continue

            if normalized_key in star_keys:
                star_value = _join_pipe_unique(_collect_star_parts(v))
                if star_value:
                    normalized['Chiffre_Star'] = _merge_pipe_values(normalized.get('Chiffre_Star', ''), star_value)

                # If model returned paired objects, collect legends from same structure.
                legend_from_star = _join_pipe_unique(_collect_legend_parts(v, allow_scalar=False))
                if legend_from_star:
                    normalized['Legende_Chiffre'] = _merge_pipe_values(normalized.get('Legende_Chiffre', ''), legend_from_star)
                continue

            if normalized_key in legend_keys:
                legend_value = _join_pipe_unique(_collect_legend_parts(v))
                if legend_value:
                    normalized['Legende_Chiffre'] = _merge_pipe_values(normalized.get('Legende_Chiffre', ''), legend_value)
                continue

            mapped_k = mapping.get(normalized_key, k)
            normalized[mapped_k] = v

        selected_structured = _select_structured_key_figures(structured_entries, max_items=10)
        if not selected_structured:
            content_candidates = _extract_markdown_highlight_candidates(normalized.get('Contenu_Nettoye', ''))
            selected_structured = _select_structured_key_figures(content_candidates, max_items=10)

        if selected_structured:
            structured_payload = []
            for entry in selected_structured:
                raw_legend = _clean_key_figure_legend(entry.get('legend', ''))
                raw_value = _clean_star_candidate(entry.get('value', ''))
                value_text, equivalence_text = _split_value_equivalence(raw_value)
                if not value_text or not raw_legend:
                    continue

                structured_payload.append(
                    {
                        'legende': raw_legend,
                        'valeur': value_text,
                        'equivalence': equivalence_text,
                        'categorie': _infer_key_figure_category(raw_legend, value_text, entry.get('category', '')),
                    }
                )

            if structured_payload:
                normalized['chiffres_cles'] = structured_payload[:10]

            merged_structured_values = _join_pipe_unique([item.get('value', '') for item in selected_structured])
            merged_structured_legends = _join_pipe_unique([item.get('legend', '') for item in selected_structured])

            if merged_structured_values:
                normalized['Chiffre_Star'] = _merge_pipe_values(
                    normalized.get('Chiffre_Star', ''),
                    merged_structured_values,
                )
            if merged_structured_legends:
                normalized['Legende_Chiffre'] = _merge_pipe_values(
                    normalized.get('Legende_Chiffre', ''),
                    merged_structured_legends,
                )

        return _sanitize_normalized_star_fields(normalized, structured_candidates=selected_structured)

class ImageExtractor:
    @staticmethod
    def extract_images(file_obj, filename):
        '''Extracts images from PDF or DOCX file object as (name, bytes) tuples.'''
        images = []
        try:
            file_obj.seek(0) # Reset pointer
            if filename.lower().endswith('.pdf'):
                with fitz.open(stream=file_obj.read(), filetype='pdf') as doc:
                    for i, page in enumerate(doc):
                        img_list = page.get_images(full=True)
                        for img_index, img in enumerate(img_list):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            images.append((f'page{i+1}_img{img_index}.{base_image["ext"]}', base_image['image']))    
            elif filename.lower().endswith('.docx'):
                import zipfile
                with zipfile.ZipFile(file_obj) as z:
                    for name in z.namelist():
                        if name.startswith('word/media/'):
                            images.append((os.path.basename(name), z.read(name)))
        except Exception as e:
            print(f'Image extraction error: {e}')
        
        file_obj.seek(0)
        return images

    @staticmethod
    def extract_images_from_docx(file_obj):
        '''Extracts images from DOCX file object as (name, bytes) tuples.'''
        images = []
        try:
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            
            with zipfile.ZipFile(file_obj) as z:
                for name in z.namelist():
                    if name.startswith('word/media/') and not name.endswith('/'):
                         images.append((os.path.basename(name), z.read(name)))
        except Exception as e:
            print(f'DOCX Image extraction error: {e}')
        return images

class CloudinaryManager:
    def __init__(self, cloud_name=None, api_key=None, api_secret=None):
        # Auto-configure if env vars exist, else use passed params
        # Format for env var: CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
        try:
            if cloud_name and api_key and api_secret:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
            else:
                # Explicitly configure from CLOUDINARY_URL env var
                import streamlit as st
                c_url = (os.environ.get('CLOUDINARY_URL') or st.secrets.get('CLOUDINARY_URL', '')).strip()
                if c_url:
                    cloudinary.config(cloudinary_url=c_url)
                    print(f"[Cloudinary] Configuré via CLOUDINARY_URL env var")
                else:
                    print("[Cloudinary] ATTENTION: Aucune configuration trouvée !")
        except Exception as e:
            print(f"[Cloudinary] Erreur config: {e}")

    def upload_file(self, file_content, filename, resource_type="auto"):
        '''Uploads bytes or file-like object to Cloudinary. Returns URL.'''
        try:
            # If it's a file object, ensure we are at start
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
            
            # Determine resource_type based on file extension
            if filename.lower().endswith(('.pdf', '.docx', '.doc', '.zip')):
                resource_type = 'raw'
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                resource_type = 'image'
                
            # Use original filename as base
            base_name, ext = os.path.splitext(filename)
            timestamp = int(time.time())
            
            # Normalize ID (remove spaces/accents)
            safe_name = re.sub(r'[^\w\-]', '_', base_name)
            
            # For RAW files, Cloudinary REQUIRES the extension in the public_id
            if resource_type == 'raw':
                public_id_str = f"{safe_name}_{timestamp}{ext}"
            else:
                public_id_str = f"{safe_name}_{timestamp}"
            
            # Use standard upload for all file types
            # (upload_large is only needed for files > 100 MB and can fail
            #  silently with BytesIO objects for normal-sized documents)
            print(f"[Cloudinary] Upload '{filename}' (type={resource_type}, id={public_id_str})...")
            
            response = cloudinary.uploader.upload(
                file_content, 
                resource_type=resource_type,
                public_id=public_id_str, 
                folder="cerd_imports"
            )
            
            url = response.get('secure_url')
            print(f"[Cloudinary] ✅ Upload OK → {url}")
            return url
            
        except Exception as e:
            print(f"[Cloudinary] ❌ Upload Error pour '{filename}': {e}")
            raise Exception(f"Cloudinary Upload Error: {str(e)}")

class AirtableManager:
    def __init__(self, api_token, base_id):
        self.api = Api(api_token)
        self.base_id = base_id
        self.table = self.api.table(base_id, 'Articles')
        # Updated to match tables_config.json: Table is 'Themes'
        self.theme_table = self.api.table(base_id, 'Themes')
        self.star_table = self.api.table(base_id, 'Chiffres_Stars')

    def check_duplicate_title(self, title):
        matches = self.table.all(formula=match({'Titre': title}), max_records=1)
        return len(matches) > 0

    def get_next_index(self, serie, theme_code):
        formula = f"AND({{Code_Theme_Ref}}='{theme_code}', {{Série}}='{serie}')"
        records = self.table.all(formula=formula, fields=['Index'], sort=['-Index'])
        
        if not records:
            return 1, f'{serie}-{theme_code}-001'
        
        last_index = records[0]['fields'].get('Index', 0)
        new_index = last_index + 1
        return new_index, f'{serie}-{theme_code}-{new_index:03d}'

    def get_theme_record_id(self, code):
        # Updated to match tables_config.json: Field is 'Code_Theme'
        records = self.theme_table.all(formula=match({'Code_Theme': code}), max_records=1)
        if records:
            return records[0]['id']
        return None

    def get_source_record_id(self, code):
        source_table = self.api.table(self.base_id, 'Sources')
        records = source_table.all(formula=match({'Code_Source': str(code)}), max_records=1)
        if records:
            return records[0]['id']
        return None

    def create_article(self, data):
        return self.table.create(data)

    def create_star_records(self, article_record_id, star_values, legend_values):
        if not article_record_id:
            return 0

        cleaned_star_values, cleaned_legend_values = sanitize_star_values(star_values, legend_values)
        stars = _split_pipe_values(cleaned_star_values)
        legends = _split_pipe_values(cleaned_legend_values)
        if not stars:
            return 0

        created_count = 0

        for idx, star in enumerate(stars[:3]):
            legend = ''
            if legends:
                legend = legends[idx] if idx < len(legends) else legends[-1]

            level = '1' if idx == 0 else ('2' if idx == 1 else '3')
            style = 'STAR_PRIMARY' if idx == 0 else ('STAR_SECONDARY' if idx == 1 else 'STAR_CONTEXT')
            color = 'brand.yellow.600' if idx == 0 else ('brand.gray.900' if idx == 1 else 'brand.gray.700')
            weight = '700' if idx == 0 else ('600' if idx == 1 else '500')
            size = 'xl' if idx == 0 else ('lg' if idx == 1 else 'md')

            fields = {
                'Valeur': star,
                'Legende': legend,
                'Ordre_Affichage': idx + 1,
                'Niveau_Importance': level,
                'Style_Token': style,
                'Color_Token': color,
                'Weight_Token': weight,
                'Size_Token': size,
                'Article_Ref': [article_record_id],
            }

            try:
                self.star_table.create(fields)
                created_count += 1
            except Exception as e:
                print(f"Erreur création Chiffre_Star ({star}) : {e}")
                err_str = str(e)
                if 'MODEL_NOT_FOUND' in err_str or '404' in err_str:
                    # Table likely missing on the target base; stop retrying.
                    break

        return created_count

class SourceMatcher:
    def __init__(self, sources_path='config/sources_data.json'):
        self.sources = []
        if os.path.exists(sources_path):
            with open(sources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sources = data.get('sources', [])
                
    def _normalize(self, text, keep_dots=False):
        import unicodedata
        text = str(text or '').lower().strip()
        text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
        if keep_dots:
            text = re.sub(r'[^\w.]+', '', text)
            return text.replace('_', '')
        return re.sub(r'[\W_]+', '', text.strip())

    def _normalized_forms(self, text):
        norm_with_dots = self._normalize(text, keep_dots=True)
        norm_without_dots = norm_with_dots.replace('.', '')
        fallback_norm = self._normalize(text, keep_dots=False)
        return {n for n in [norm_with_dots, norm_without_dots, fallback_norm] if n}

    def _best_similarity(self, left_forms, right_forms):
        best = 0.0
        for left in left_forms:
            for right in right_forms:
                score = difflib.SequenceMatcher(None, left, right).ratio()
                if score > best:
                    best = score
        return best

    def _leading_token_forms(self, text):
        raw_text = str(text or '').strip()
        if not raw_text:
            return set()

        match_token = re.match(r"^([A-Za-z0-9'.-]{2,12})", raw_text)
        if not match_token:
            return set()

        token = match_token.group(1)
        # Only treat all-uppercase-leading tokens as extra exact forms (e.g., MAP, AFP, OCP).
        if token.upper() != token or not re.search(r"[A-Z]", token):
            return set()

        return self._normalized_forms(token)

    def _source_exact_forms(self, source_obj):
        forms = set()
        forms.update(self._normalized_forms(source_obj.get('nom', '')))
        forms.update(self._leading_token_forms(source_obj.get('nom', '')))
        for alias in source_obj.get('aliases', []):
            forms.update(self._normalized_forms(alias))
        return forms

    def _match_exact(self, source_text):
        norm_source_forms = self._normalized_forms(source_text)
        if not norm_source_forms:
            return None

        for s in self.sources:
            source_forms = self._source_exact_forms(s)
            if norm_source_forms & source_forms:
                return s['code'], s['nom']

        return None

    def _protect_domains(self, text):
        domain_pattern = re.compile(r'(?i)\b(?:https?://)?(?:www\.)?[a-z0-9-]+(?:\.[a-z0-9-]+)+\b')

        def repl(match_obj):
            protected = match_obj.group(0)
            protected = protected.replace('://', '<SCHEME>')
            protected = protected.replace('/', '<SLASH>')
            protected = protected.replace('.', '<DOT>')
            return protected

        return domain_pattern.sub(repl, text)

    def _is_noise_fragment(self, fragment):
        norm_fragment = self._normalize(fragment)
        if not norm_fragment:
            return True

        noise_values = {
            'source',
            'sources',
            'autresource',
            'autressources',
            'dautresource',
            'dautressources',
            'etc',
            'etautressources',
            'autres',
            'http',
            'https',
        }
        if norm_fragment in noise_values:
            return True

        return norm_fragment.startswith('dautressource')

    def _split_sources(self, source_text):
        raw_text = str(source_text or '').strip()
        if not raw_text:
            return []

        protected_text = self._protect_domains(raw_text)
        # Split on explicit separators while keeping domain names like bladi.net intact.
        split_pattern = re.compile(r"\s*(?:,|;|/|\||&|\+|\bet\b|\.\s+)\s*", flags=re.IGNORECASE)
        parts = split_pattern.split(protected_text)

        clean_parts = []
        seen = set()

        for part in parts:
            candidate = part
            candidate = candidate.replace('<SCHEME>', '://').replace('<SLASH>', '/').replace('<DOT>', '.')
            candidate = candidate.strip(" \t\r\n-–—:|")
            if self._is_noise_fragment(candidate):
                continue

            candidate_key = self._normalize(candidate)
            if candidate_key and candidate_key not in seen:
                seen.add(candidate_key)
                clean_parts.append(candidate)

        return clean_parts

    def _match_single(self, source_text, gemini_client=None):
        norm_source_forms = self._normalized_forms(source_text)
        if not norm_source_forms:
            return "999", "Source inconnue"

        # 1. Exact Match
        exact_match = self._match_exact(source_text)
        if exact_match:
            return exact_match

        # 2. Fuzzy Match (difflib)
        best_score = 0
        best_match = None
        candidates = []

        for s in self.sources:
            max_score = self._best_similarity(norm_source_forms, self._normalized_forms(s['nom']))
            for alias in s.get('aliases', []):
                score_alias = self._best_similarity(norm_source_forms, self._normalized_forms(alias))
                max_score = max(max_score, score_alias)

            candidates.append((max_score, s))
            if max_score > best_score:
                best_score = max_score
                best_match = s

        if best_score >= 0.70 and best_match:
            return best_match['code'], best_match['nom']

        # 3. Fallback Gemini AI Match
        if gemini_client and best_score >= 0.2:
            candidates.sort(key=lambda x: x[0], reverse=True)
            top_5 = candidates[:5]

            prompt = f"Trouve la source officielle qui correspond le mieux à ce nom extrait d'un article : '{source_text}'.\nVoici les 5 candidats les plus proches trouvés :\n"
            for score, s in top_5:
                prompt += f"- Code {s['code']} : {s['nom']}\n"
            prompt += "Renvoie UNIQUEMENT le code numérique de la source correspondante. Si aucune ne semble correspondre logiquement, renvoie '999'."

            try:
                response = gemini_client.models.generate_content(
                    model=SOURCE_MATCH_GEMINI_MODEL,
                    contents=prompt,
                    config={'temperature': 0.1}
                )
                code_str = response.text.strip().replace('"', '').replace("'", "")
                for score, s in top_5:
                    if s['code'] == code_str:
                        return s['code'], s['nom']
            except Exception as e:
                print(f"Erreur Gemini lors du matching de source : {e}")

        return "999", "Source inconnue"

    def match_many(self, source_text, gemini_client=None):
        if not source_text or not self.sources:
            return []

        # If the complete source string is a known source, keep it as a single source.
        exact_full_match = self._match_exact(source_text)
        if exact_full_match:
            return [{
                'code': exact_full_match[0],
                'nom': exact_full_match[1],
                'source_text': str(source_text).strip(),
            }]

        split_parts = self._split_sources(source_text)
        parts_to_match = split_parts if len(split_parts) > 1 else [str(source_text).strip()]

        matches = []
        seen_codes = set()

        for part in parts_to_match:
            code, nom = self._match_single(part)
            if code == "999" and gemini_client:
                code, nom = self._match_single(part, gemini_client=gemini_client)

            if code != "999" and code not in seen_codes:
                seen_codes.add(code)
                matches.append({
                    'code': code,
                    'nom': nom,
                    'source_text': part,
                })

        if matches:
            return matches

        # If split matching failed entirely, retry once on the full string.
        code, nom = self._match_single(source_text)
        if code == "999" and gemini_client:
            code, nom = self._match_single(source_text, gemini_client=gemini_client)

        if code != "999":
            return [{
                'code': code,
                'nom': nom,
                'source_text': str(source_text).strip(),
            }]

        return []
        
    def match(self, source_text, gemini_client=None):
        matches = self.match_many(source_text, gemini_client=gemini_client)
        if matches:
            first_match = matches[0]
            return first_match['code'], first_match['nom']
        return "999", "Source inconnue"





