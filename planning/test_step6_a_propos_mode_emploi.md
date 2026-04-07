# Test Step 6 - A propos et Mode d'emploi

Date: 2026-04-06
Scope: Validation GO/NO-GO de la sixieme marche (contextualisation lecteur + guidage)
Prototype: prova_step1_app.py

## Objectif

Valider l'integration des pages de contextualisation demandees:

1. page A propos accessible et coherent avec la vision produit,
2. page Mode d'emploi exploitable et actionnable,
3. series c1/c2/c3/c4 visibles depuis l'orientation,
4. absence de regression sur les parcours principaux.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Acces A propos

1. Ouvrir E2 (Home Orientation).
2. Cliquer "A propos du projet".
3. Lire le contenu puis revenir orientation.

Resultat attendu:

- Le contenu A propos est present et lisible.
- Le retour vers l'orientation fonctionne sans blocage.

### TC2 - Acces Mode d'emploi

1. Depuis E2, cliquer "Mode d'emploi".
2. Verifier les etapes du parcours recommande.
3. Verifier les entrees alternatives mentionnees.

Resultat attendu:

- La page Mode d'emploi expose clairement le flux secteur -> theme -> article.
- Les options series/recherche sont explicites.

### TC3 - Series visibles en orientation

1. Sur E2, verifier le bloc series.
2. Confirmer la presence de c1, c2, c3, c4.

Resultat attendu:

- Les series sont visibles et identifiables sans navigation supplementaire.

### TC4 - Actions depuis Mode d'emploi

1. Depuis Mode d'emploi, cliquer:
   - Commencer par un secteur,
   - Entrer par serie,
   - Retour orientation.

Resultat attendu:

- Les 3 actions routent vers la bonne vue.
- Aucun impact negatif sur les parcours E3/E5/E6/E7.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Les pages info ne sont pas accessibles depuis l'orientation.
2. Le contenu n'est pas coherent avec la vision (parcours guide principal).
3. Les actions depuis Mode d'emploi cassent la navigation.

## Notes de validation

- Decision: GO
- Commentaires: Tous les tests passent. Pages A propos et Mode d'emploi valides.
- Date: 2026-04-06
