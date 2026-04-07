# Test Step 7 - Campagne interne 20 articles

Date: 2026-04-06
Scope: Validation GO/NO-GO de la septieme marche (corpus de test interne >= 20 articles)
Prototype: prova_step1_app.py

## Objectif

Valider la disponibilite d'un corpus QA suffisant pour la campagne interne:

1. corpus recherche >= 20 articles,
2. couverture multi-secteurs/multi-themes,
3. navigation detail stable sur un echantillon de 20,
4. suivi runtime cohérent pendant la campagne.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Taille du corpus QA

1. Ouvrir l'application.
2. Observer la sidebar section "Suivi Runtime".
3. Verifier la metrique "Corpus QA".

Resultat attendu:

- La metrique Corpus QA affiche une valeur >= 20.
- Le statut "Corpus 20+ articles pret" est visible.

### TC2 - Couverture de navigation

1. Ouvrir E7 recherche sans mot-cle.
2. Parcourir plusieurs pages de resultats.
3. Verifier la presence de secteurs/themes differents.

Resultat attendu:

- Le corpus n'est pas mono-theme.
- Les resultats couvrent plusieurs contextes de navigation.

### TC3 - Echantillon 20 articles

1. Ouvrir 20 articles (via E5 ou E7) et consulter le detail E6.
2. Verifier a chaque fois: source lisible, chips parents, bloc chiffres cles.

Resultat attendu:

- Aucun crash sur les 20 ouvertures.
- Les elements editoriaux restent affiches de facon stable.

### TC4 - Runtime et fluidite campagne

1. Pendant les ouvertures successives, observer "Rendu E5" et "Rendu E7".
2. Alterner mode performance mobile ON/OFF puis continuer la navigation.

Resultat attendu:

- Les mesures runtime se mettent a jour normalement.
- Aucun gel ou blocage critique lors de la campagne.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Corpus QA < 20.
2. Navigation instable dans la campagne des 20 articles.
3. Degradation notable de fluidite sans feedback utilisateur.

## Notes de validation

- Decision: GO
- Commentaires: Validation metier explicite recue. TC1 OK (Corpus QA = 46, statut 20+ visible). TC2 OK (couverture observee sur 7 secteurs et 12 themes, pages 1 a 5). TC3 OK (20 ouvertures E7->E6 realisees, aucun crash, source/chips/chiffres cles visibles a chaque ouverture). TC4 OK (bascule mode performance mobile OFF puis ON, navigation continue sans gel critique, metriques runtime E5/E7 actives).
- Date: 2026-04-06
