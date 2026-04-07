import re

file_path = 'scripts/export_public_catalog_for_pwa.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add subsector_label to resolve_theme_context return
content = re.sub(
    r"sector_label = str\(sector\.get\('nom', ''\)\)\.strip\(\) if sector else ''",
    "sector_label = str(sector.get('nom', '')).strip() if sector else ''\n    subsector_label = str(subsector.get('nom', '')).strip() if 'subsector' in locals() and subsector else ''",
    content
)

content = re.sub(
    r"'domain_label': domain_label,",
    "'domain_label': domain_label,\n        'subsector_label': subsector_label,",
    content
)

# 2. Modify build_public_catalog use of context
content = re.sub(
    r"domain_label = context\['domain_label'\] or 'Classement temporaire'",
    """domain_label = context['domain_label'] or 'Classement temporaire'
        subsector_label = context.get('subsector_label', '')
        
        # Smart hierarchy assignment
        if subsector_label:
            final_sector_label = subsector_label
            final_description = f"{domain_label} > {sector_label}"
        else:
            final_sector_label = sector_label
            final_description = f"{domain_label}"
    """,
    content
)

content = re.sub(
    r"'label': sector_label,\s+'description': f\"Domaine: \{domain_label\}\",",
    "'label': final_sector_label,\n                'description': final_description,",
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Hierarchy fixed in python")
