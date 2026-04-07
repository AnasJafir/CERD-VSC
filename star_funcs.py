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