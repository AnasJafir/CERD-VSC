# Test Step 1 - Parcours nominal sans clavier

Date: 2026-04-03
Scope: Validation GO/NO-GO de la premiere marche (E1 -> E5 -> E6)
Prototype: prova_step1_app.py

## Objectif

Valider que l'utilisateur atteint un article en parcours guide sans saisie clavier,
avec orientation claire et sans exposition de codes techniques.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Entree et orientation

1. Ouvrir l'app.
2. Verifier E1 Home Identite (branding + CTA).
3. Cliquer "Entrer dans la base".
4. Verifier E2 avec 3 entrees visibles:
   - Commencer par un secteur
   - Entrer par serie
   - Recherche index/mots-cles (secondaire)

Resultat attendu:

- E1 et E2 affiches correctement.
- Aucune saisie texte necessaire.

### TC2 - Parcours nominal secteur -> theme -> article

1. Depuis E2, cliquer "Commencer par un secteur".
2. Dans E3, choisir une section puis un secteur.
3. Dans E4, choisir un theme.
4. Dans E5, ouvrir un document.
5. Dans E6, verifier detail article.

Resultat attendu:

- Navigation complete sans clavier.
- Chemin visible (breadcrumb).
- Article atteint en parcours guide.

### TC3 - Conformite lecture

1. Sur E5/E6, verifier absence de codes techniques (ID/champs internes).
2. Verifier presence de source lisible.
3. Verifier bloc chiffres cles visible.

Resultat attendu:

- Conformite vision client respectee.

### TC4 - Orientation et retour

1. Depuis E6, retour articles puis retour orientation.
2. Rejouer un second parcours.

Resultat attendu:

- Retours stables.
- Aucune perte de navigation bloquante.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Parcours nominal casse.
2. Codes techniques visibles cote lecteur.
3. Orientation insuffisante pour comprendre "ou je suis".

## Notes de validation

- Decision: GO
- Commentaires: Les 4 tests passent. Feu vert utilisateur pour passer a l'etape suivante.
- Date: 2026-04-03
