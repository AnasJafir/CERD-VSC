const fs = require('fs');
let p = 'scripts/export_public_catalog_for_pwa.py';
let code = fs.readFileSync(p, 'utf8');

// We will overwrite the `def resolve_theme_hierarchy` or wherever out_sectors is populated
let t_regex = /domain_label = str\(domain\.get\('nom', ''\)\)\.strip\(\) if domain else 'Domaine non classifié'\s*sector_label = str\(sector\.get\('nom', ''\)\)\.strip\(\) if sector else 'Secteur non classifié'\s*out_sectors\[sector_id\] = \{\s*'id': sector_id,\s*'label': sector_label,\s*'description': f"Domaine: \{domain_label\}",\s*\}/;

let repl = `domain_label = str(domain.get('nom', '')).strip() if domain else ''
            sector_label = str(sector.get('nom', '')).strip() if sector else ''
            subsector_label = str(subsector.get('nom', '')).strip() if 'subsector' in locals() and subsector else ''
            
            parents = []
            if domain_label:
                parents.append(domain_label)
            
            final_label = 'Général'
            
            if parent_type == 'secteur' and sector_label:
                final_label = sector_label
            elif parent_type == 'sous_secteur' and subsector_label:
                if sector_label:
                    parents.append(sector_label)
                final_label = subsector_label
            elif parent_type == 'domaine' and domain_label:
                final_label = domain_label
                parents = []

            out_sectors[sector_id] = {
                'id': sector_id,
                'label': final_label,
                'description': " > ".join(parents)
            }`;

if (code.match(t_regex)) {
    code = code.replace(t_regex, repl);
    fs.writeFileSync(p, code);
    console.log('Python script updated for hierarchy');
} else {
    console.log('Regex not matched');
}
