const fs = require('fs');
let content = fs.readFileSync('scripts/04_article_ingestion_gemini.py', 'utf8');

const oldArtifacts = `    replacements = {
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
    }`;

const newArtifacts = `    replacements = {
        'ÆÇ': '€',
        'Æ€': '€',
        'Â€': '€',
        'dÆ€': "d'€",
        'dÆÇ': "d'€",
        '¢': '€',
        'co¹t': 'coût',
        'Co¹t': 'Coût',
        'durÚe': 'durée',
        'DurÚe': 'Durée',
        'pÚriode': 'période',
        'PÚriode': 'Période',
        'Úvolution': 'évolution',
        'Ú': 'é',
        'Þ': 'è',
        'Ó': 'à',
        'Æ': "'",
    }`;

content = content.replace(oldArtifacts, newArtifacts);
fs.writeFileSync('scripts/04_article_ingestion_gemini.py', content);
