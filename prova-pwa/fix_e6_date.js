const fs = require('fs');
let code = fs.readFileSync('app/e6-article.tsx', 'utf8');

code = code.replace(/<ScrollView horizontal showsHorizontalScrollIndicator=\{false\} style=\{\{marginBottom: 16, paddingHorizontal: 8\}\}>\s*(<Breadcrumbs[\s\S]*?\]\}\s*\/>)\s*<\/ScrollView>/g, '$1');

const formatHelper = `function formatDateToJJMM(dateStr: string | undefined): string {
  if (!dateStr) return 'Date non renseignée';
  const parts = dateStr.split(/[-/]/);
  if (parts.length === 3) {
    if (parts[0].length === 4) {
      const yy = parts[0].slice(-2);
      return \`\${parts[2]}-\${parts[1]}-\${yy}\`;
    } else {
      const yy = parts[2].slice(-2);
      return \`\${parts[0]}-\${parts[1]}-\${yy}\`;
    }
  }
  return dateStr;
}

export default function E6ArticleScreen() {`;

code = code.replace('export default function E6ArticleScreen() {', formatHelper);

code = code.replace(/title="Corps du document"/g, 'title={formatDateToJJMM(article.date)}');

code = code.replace(/Source : \{article\.source\}\s*\{article\.date \? `\(\$\{article\.date\}\)` : ''\}/gi, 'Source : {article.source}');

fs.writeFileSync('app/e6-article.tsx', code, 'utf8');
console.log('Fixed e6 styling Date and SV');
