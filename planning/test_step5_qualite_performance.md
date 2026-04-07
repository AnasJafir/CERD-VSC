# Test Step 5 - Qualite et performance percue

Date: 2026-04-06
Scope: Validation GO/NO-GO de la cinquieme marche (placeholders, retry, mode performance mobile, fluidite E5/E7)
Prototype: prova_step1_app.py

## Objectif

Valider que l'experience lecteur reste fluide et robuste:

1. chargement percu guide (placeholders),
2. reprise simple en cas de chargement partiel (retry),
3. mode performance mobile fonctionnel,
4. navigation sans blocage sur les vues E5/E7.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Placeholders de chargement

1. Ouvrir E5 (liste articles) puis E7 (recherche).
2. Observer les cartes de chargement au moment du rendu.

Resultat attendu:

- Des placeholders sont visibles avant l'affichage final.
- Le rendu final remplace proprement les placeholders.

### TC2 - Mode performance mobile

1. Ouvrir le panneau lateral "Mode Qualite".
2. Activer puis desactiver "Mode performance mobile".
3. Revenir sur E4 et E7.

Resultat attendu:

- Le nombre d'elements affiches par ecran s'adapte au mode.
- La pagination/revelation progressive reste stable.

### TC3 - Robustesse retry et mode degrade

1. Dans le panneau lateral, cliquer "Rafraichir les donnees".
2. Verifier l'absence de blocage global de l'interface.
3. En cas d'avertissement de chargement partiel, utiliser "Reessayer le chargement".

Resultat attendu:

- L'application reste navigable.
- Le mecanisme de retry est disponible et fonctionnel.

### TC4 - Fluidite navigation E5/E7

1. Faire 2 parcours complets:
   - E2 -> secteur -> theme -> E5 -> E6
   - E2 -> E7 -> filtres -> detail article
2. Observer les mesures runtime affichees dans la sidebar (Rendu E5 / Rendu E7).
3. Faire un parcours via E2 -> Entrer par serie -> Combien ca coute ? -> ouvrir un article.

Resultat attendu:

- Pas de gel d'ecran ni erreur bloquante.
- Les mesures runtime se mettent a jour apres rendu des vues.
- Dans E5, le libelle affiche "Serie" (et non "Theme") pour cette entree.
- Dans E6, les chips parents de l'article (secteur + theme) restent visibles.
- Dans E6, l'arborescence visuelle commence par le Domaine puis descend vers Secteur/Sous-secteur/Theme selon le cas.
- Les chips parents sont affiches sans prefixes textuels (pas de "Domaine:", "Secteur:", etc.).
- Le volume visuel decroit du Domaine (le plus fort) vers le Theme (le plus discret).

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Le chargement devient bloquant sans feedback utilisateur.
2. Le mode performance degrade la navigation.
3. Le retry ne permet pas de recuperer un chargement partiel.

## Notes de validation

- Decision: GO
- Commentaires: Tous les tests passent. Ajustement valide: arborescence parent domaine-first, sans prefixes, avec volumes differencies.
- Date: 2026-04-06
