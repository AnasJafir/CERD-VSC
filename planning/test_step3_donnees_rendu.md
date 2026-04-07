# Test Step 3 - Donnees et rendu editorial

Date: 2026-04-03
Scope: Validation GO/NO-GO de la troisieme marche (sources lisibles, masquage codes techniques, Chiffres Stars, fallback)
Prototype: prova_step1_app.py

## Objectif

Valider la qualite de lecture en E5/E6:

1. aucune fuite de codes techniques cote lecteur,
2. sources toujours affichees avec un libelle humain,
3. bloc Chiffres cles stylise en 3 niveaux (primary/secondary/context),
4. fallback robuste si donnees partielles.

## Preconditions

1. Environnement Python actif.
2. Dependances installees (streamlit).
3. Fichier config/parsed_data.json present.

## Lancement

Commande:

streamlit run prova_step1_app.py

## Cas de test (obligatoires)

### TC1 - Sources lisibles

1. Ouvrir un article via parcours nominal (E2 -> secteur -> theme -> article).
2. Verifier le sous-titre de E6.
3. Refaire via E7 recherche, puis ouvrir un article.

Resultat attendu:

- Le champ source est lisible pour un lecteur (pas de prefixe technique).
- Aucune valeur technique de type fld/tbl/rec/source_ref n'est visible.

### TC2 - Chiffres Stars hierarchises

1. Ouvrir l'article "Tunnel Maroc-Espagne pour 2050 ?".
2. Observer le bloc "Chiffres cles".

Resultat attendu:

- 3 niveaux visibles en priorite decroissante.
- Niveau 1 visuellement le plus fort, niveau 2 intermediaire, niveau 3 contextuel.
- Chaque carte affiche valeur + legende lisible.

### TC3 - Fallback donnees partielles

1. Aller en E2 -> Entrer par serie -> Fichier Entreprises.
2. Ouvrir l'article "Panorama Entreprises - Edition synthese".

Resultat attendu:

- Le detail s'affiche sans erreur meme sans star_records structures.
- Les chiffres cles sont derives du champ brut (pipe/newline) si necessaire.
- Les zones manquantes restent lisibles (pas de crash ni affichage technique).

### TC4 - Non-regression navigation

1. Depuis E6, revenir a E5 puis orientation.
2. Rejouer un second parcours via E7 et ouvrir un autre article.

Resultat attendu:

- Navigation stable, aucune etape bloquante.
- Le breadcrumb reste coherent.

## Critere GO

GO si:

1. TC1, TC2, TC3, TC4 passent.
2. Validation metier explicite de votre part.

NO-GO si:

1. Un code technique est visible cote lecteur.
2. Le bloc Chiffres cles ne respecte pas la hierarchie de priorite.
3. Le fallback partiel casse l'ecran detail.

## Notes de validation

- Decision: GO
- Commentaires: Les 4 tests passent. Validation metier confirmee.
- Date: 2026-04-03
