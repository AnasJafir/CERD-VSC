# Test Step 2 - Structure E0 a E7

Date: 2026-04-03
Scope: Validation GO/NO-GO de la deuxieme marche (activation E0 Splash + E7 Recherche)
Prototype: prova_step1_app.py

## Objectif

Valider que la structure E0 a E7 est exploitable en demonstration:

1. entree via Splash,
2. parcours nominal secteur-first intact,
3. recherche secondaire active avec filtres, tri et ouverture de detail.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - E0 Splash

1. Ouvrir l'app.
2. Verifier l'ecran E0 (logo + titre + bouton Continuer).
3. Cliquer Continuer.

Resultat attendu:

- E0 visible au demarrage.
- Transition vers E1 fonctionnelle.

### TC2 - Parcours nominal preserve

1. Depuis E1, cliquer Entrer dans la base.
2. E2 -> Commencer par un secteur.
3. E3 -> E4 -> E5 -> E6 sur un article.

Resultat attendu:

- Le parcours sans clavier reste operationnel.
- Le fil d'orientation affiche les etapes de facon lisible.

### TC3 - Recherche secondaire (E7)

1. Depuis E2, cliquer Recherche index/mots-cles (secondaire).
2. Saisir un mot-cle (ex: tunnel ou ciment).
3. Appliquer au moins un filtre (secteur, theme ou serie).
4. Changer le tri (Date la plus recente ou Alphabetique).
5. Ouvrir un resultat avec Lire le document.

Resultat attendu:

- Resultats affiches et comptabilises.
- Filtres et tri influencent la liste.
- Le detail article s'ouvre depuis E7.

### TC4 - Robustesse de navigation

1. Depuis detail ouvert via E7, cliquer Retour orientation.
2. Revenir en recherche et changer page de resultats.
3. Verifier message propre quand aucun resultat.

Resultat attendu:

- Aucune navigation bloquante.
- Pagination et etat vide stables.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. E0 absent au demarrage.
2. Recherche E7 inutilisable (filtres/tri non fonctionnels).
3. Rupture du parcours nominal secteur-first.

## Notes de validation

- Decision: GO
- Commentaires: Tests passes, feu vert utilisateur pour continuer.
- Date: 2026-04-03
