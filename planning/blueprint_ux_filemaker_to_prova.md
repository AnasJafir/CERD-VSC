# Blueprint UX FileMaker -> Prova + Airtable

## Objectif
Transformer la vision historique FileMaker du client en parcours moderne, mobile-first, tout en gardant:
- guidance forte
- navigation accordéon
- recherche métier sectorielle
- mots-clés en mode secondaire

## Principes directeurs
1. La porte: l'utilisateur arrive sur un écran d'accueil qui explique l'identité et les parcours.
2. La maison: l'utilisateur voit immédiatement la structure de navigation avant de chercher.
3. La cuisine: il dispose d'outils de navigation/recherche sans complexité technique.

## Parcours Prova (lecteur)
## E0 - Splash
- Logo
- Nom projet
- Chargement court

## E1 - Home Identité
- Bloc projet
- Bloc owner
- Bloc promesse valeur
- CTA: Entrer dans la base

## E2 - Home Orientation
- Entrée A: Commencer par un secteur
- Entrée B: Explorer par série (c3, Entreprise, etc.)
- Entrée C: Recherche mots-clés/index (secondaire)
- Aide courte: "Comment trouver un document"

## E3 - Secteurs (accordéon)
- Liste secteurs en cartes repliables
- État ouvert/fermé mémorisé
- Compteur d'articles par secteur

## E4 - Thématiques
- Sous-listes thématiques du secteur sélectionné
- Tri par pertinence ou alphabétique

## E5 - Liste documents/articles
- Carte article: titre, source lisible, date, extrait
- Badges: série, thématique
- Accès rapide au détail

## E6 - Détail article
- En-tête éditorial propre
- Bloc Chiffres clés stylé (importance 1/2/3)
- Corps article lisible
- Sources en libellés humains (pas de codes)

## E7 - Recherche index/mots-clés (secondaire)
- Champ recherche
- Suggestions index
- Résultats groupés par secteur/thématique

## Parcours Airtable (admin)
## A1 - Vue Ingestion
- Contrôle champs obligatoires
- Suggestion source(s) et thème(s)
- Prévisualisation article

## A2 - Vue Chiffres clés
- Table Chiffres_Stars liée à Articles
- Ordre d'affichage
- Tokens de style

## A3 - Vue Qualité
- Incohérences et manques
- Alertes publication

## A4 - Vue Publication
- Dataset public filtré
- Codes internes masqués côté export Prova

## Spécification de comportement
- Le parcours nominal ne dépend pas du clavier.
- Les mots-clés servent d'accélérateur, pas de point d'entrée principal.
- L'utilisateur doit comprendre "où je suis" à tout moment (fil d'ariane visible).

## UX Writing recommandée
- Boutons d'action explicites: "Commencer par un secteur", "Voir les thèmes", "Lire le document".
- Micro-copies pédagogiques courtes sous les titres.
- Terminologie stable (éviter changements entre secteur/thème/document).

## Données nécessaires minimum
- Secteur
- Thématique
- Série
- Titre
- Source(s) lisible(s)
- Date publication
- Extrait
- Chiffres clés structurés

## Definition of Done
- Un lecteur trouve un article sans saisir un mot-clé.
- Le bloc chiffres clés est visuellement priorisé et lisible.
- Les codes internes ne sont jamais visibles sur Prova.
- Le parcours E1 -> E6 est validé par test utilisateur.
