const fs = require('fs');

let file_path = 'app/e6-article.tsx';
let file_code = fs.readFileSync(file_path, 'utf8');

file_code = file_code.replace(
  "pathname: '/e3-thematiques'",
  "pathname: '/e4-themes'"
);

file_code = file_code.replace(
  '<InfoCard style={styles.articleCard}>',
  '<InfoCard title="Corps du document" style={styles.articleCard}>'
);

fs.writeFileSync(file_path, file_code);
console.log('e6-article.tsx errors fixed');
