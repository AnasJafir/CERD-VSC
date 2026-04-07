const fs = require('fs');
let p = 'scripts/04_article_ingestion_gemini.py';
let c = fs.readFileSync(p, 'utf8');

c = c.replace(/REGLES POUR LES VISUELS \(OBLIGATOIRE\) :\n- Lors de l'analyse de l'article, il faut détecter le nom ou titre exact de la figure, image, graphe ou tableau s'il y en a de mentionné dans le texte. Tu dois l'associer comme titre du visuel./, `REGLES POUR LES VISUELS (OBLIGATOIRE) :\n- Lors de l'analyse de l'article, repère TOUTE légende, description, titre de galerie, graphe, carte ou illustration (ex: 'Une galerie sur le rocher de Gibraltar...', source 'Wikipédia', etc.) présente dans le texte.\n- Extrais EXACTEMENT ce texte pour remplir le champ "titre_visuel".`);

c = c.replace(/"titre_visuel": "Nom exact de la figure, image, graphe ou tableau\. Sinon, laisse vide",/g, `"titre_visuel": "Texte exact de la légende, description, titre de galerie ou d'illustration (ex. avec mentions de source comme Wikipédia). Sinon laisse vide",`);

fs.writeFileSync(p, c, 'utf8');
