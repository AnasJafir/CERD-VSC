$code = Get-Content app/e6-article.tsx -Raw
$code = $code -replace 'palette.primaryInteraction', 'palette.brand'
$code = $code -replace 'palette.primaryRefined', 'palette.brandSoft'
$code = $code -replace 'palette.textDetails', 'palette.textMuted'
$code = $code -replace 'palette.borderLight', 'palette.border'
$code = $code -replace 'palette.surfaceHighlight', 'palette.surfaceAlt'
$code = $code -replace 'typography.base', 'typography.body'
$code = $code -replace '<InfoCard style=\{styles.articleCard\}>', '<InfoCard title="Contenu de la fiche" style={styles.articleCard}>'
Set-Content -Path app/e6-article.tsx -Value $code

$code2 = Get-Content app/index.tsx -Raw
$code2 = $code2 -replace 'palette.primaryRefined', 'palette.brandSoft'
$code2 = $code2 -replace 'palette.textDetails', 'palette.textMuted'
$code2 = $code2 -replace 'typography.base', 'typography.body'
$code2 = $code2 -replace '<Reveal delay=\{100\} style=\{styles.centerStage\}>', '<Reveal delay={100}><View style={styles.centerStage}>'
$code2 = $code2 -replace '(?s)(<Text style=\{styles.heroText\}>.*?</Text>\s*)</Reveal>', '$1</View></Reveal>'
$code2 = $code2 -replace '<Reveal delay=\{400\} style=\{styles.footerStage\}>', '<Reveal delay={400}><View style={styles.footerStage}>'
$code2 = $code2 -replace '(?s)(<Text style=\{styles.primaryButtonText\}>.*?</Text>\s*</Pressable>\s*)</Reveal>', '$1</View></Reveal>'
Set-Content -Path app/index.tsx -Value $code2
