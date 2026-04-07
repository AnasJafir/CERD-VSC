# Test Step 4 - Tokens visuels et lisibilite mobile

Date: 2026-04-03
Scope: Validation GO/NO-GO de la quatrieme marche (couleurs, typo, tailles, robustesse mobile)
Prototype: prova_step1_app.py

## Objectif

Valider la coherence visuelle de l'interface lecteur:

1. hierarchy typographique claire,
2. palette conforme (jaune/noir/gris) avec bon contraste,
3. tailles et niveaux visuels stables sur les Chiffres cles,
4. rendu mobile lisible sans chevauchement.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Hierarchie typographique

1. Ouvrir E1 puis E2 puis E6.
2. Observer titres, sous-titres, textes courants.

Resultat attendu:

- Les titres ressortent clairement par rapport au texte.
- La lecture des paragraphes reste confortable (sans effet visuel parasite).

### TC2 - Tokens de couleur et contraste

1. Ouvrir E2 et afficher "Guide visuel (tokens actifs)".
2. Ouvrir un article en E6.

Resultat attendu:

- La palette jaune/noir/gris est perceptible et coherente.
- Les contenus restent lisibles (contraste suffisant sur texte et cartes).

### TC3 - Hierarchie des Chiffres cles

1. Ouvrir l'article "Tunnel Maroc-Espagne pour 2050 ?".
2. Observer les 3 cartes du bloc Chiffres cles.

Resultat attendu:

- Priorite 1 > Priorite 2 > Contexte en impact visuel.
- Aucune mention technique de token interne n'est affichee au lecteur.

### TC4 - Lisibilite mobile

1. Reduire la largeur de fenetre a un format mobile.
2. Rejouer un parcours E2 -> E5 -> E6 puis E7.

Resultat attendu:

- Pas de texte coupe ou superpose.
- Les cartes Chiffres cles restent lisibles.
- Navigation exploitable sans friction majeure.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Contraste insuffisant sur les textes principaux.
2. Perte de hierarchy visuelle entre titres et corps.
3. Degradation nette de lisibilite en largeur mobile.

## Notes de validation

- Decision: GO
- Commentaires: Les 4 tests passent. Validation metier confirmee.
- Date: 2026-04-06
