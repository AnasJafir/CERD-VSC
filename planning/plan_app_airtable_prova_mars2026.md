# Plan Directeur App/Airtable + Interface Externe Prova (Mars 2026)

## 1) Cadrage et filtre de travail
Ce plan traite uniquement les deux volets demandés:
- Interface Airtable
- Interface externe mobile Prova

Sujet explicitement exclu de ce document:
- Organisation conteneur/dossiers/fiches en tant que process de collaboration interne non produit

Règle de priorisation:
- Lisibilité éditoriale et apparence professionnelle d'abord
- Navigation et recherche métier ensuite
- Automatisation IA et performance ensuite

## 2) Constats consolidés (transcriptions + visuels)
### 2.1 Exigences fonctionnelles fortes
- Le lecteur ne doit pas voir les codes internes (codes source, codes techniques).
- Les variations de source doivent être normalisées en backend, puis affichées en nom lisible.
- La navigation attendue est hiérarchique et progressive (du macro vers le détail).
- La recherche doit être guidée par le secteur/thématique et non uniquement par saisie brute.

### 2.1.b Détail validé depuis l'échange écrit client
- L'expérience doit commencer par une adresse précise et une porte d'entrée claire (home d'accueil explicite).
- Après ouverture, l'application doit présenter la maison: où aller, comment y aller, ce que l'on y trouve.
- Le lecteur arrive ensuite dans un espace recherche/navigation (métaphore cuisine) avec des outils immédiatement compréhensibles.
- Dans la B3D Chiffres clés de l'Entreprise, l'utilisateur ne saisit des mots-clés qu'à titre exceptionnel.
- Le parcours nominal démarre d'un besoin sectoriel (industrie, agriculture, etc.) puis descend vers le thème et le document.
- Le défilement accordéon est une exigence centrale pour guider la progression du lecteur.
- La page d'accueil (ou seconde page de démarrage) doit rendre visible les entrées de série (ex: c3 Combien ça coûte, Série Entreprise).

### 2.2 Exigences UX/Design fortes
- La qualité visuelle est critique (client éditeur/publieur).
- Les chiffres clés sont centraux et doivent ressortir visuellement.
- Les distinctions de poids, taille et couleur doivent être conservées dans l'interface externe.
- Le premier écran doit poser l'identité: projet, marque, owner, mission.

### 2.3 Indices visuels fournis
- Identité dominante jaune/noir/gris (logo principal + déclinaisons icône).
- Maquette historique orientée recherche en deux axes:
  - Recherche par secteur d'activité
  - Recherche dans la thématique
- Structure type arborescente avec descente jusqu'au document/article.

## 3) Vision produit cible
### 3.1 Airtable = back-office éditorial
- Ingestion et validation
- Contrôle qualité des métadonnées
- Gouvernance des sources
- Préparation de la diffusion vers Prova

### 3.2 Prova = front-office lecteur
- Expérience de consultation claire et premium
- Navigation arborescente intuitive
- Moteur de recherche métier
- Rendu éditorial riche des chiffres clés

### 3.3 Traduction produit de la vision FileMaker (non négociable)
- Porte d'entrée: écran d'accueil institutionnel avec orientation utilisateur.
- Présentation de la maison: écran qui expose les chemins de navigation avant toute recherche libre.
- Recherche/navigation outillée: interface accordéon avec priorité au parcours secteur -> thème -> document.
- Mots-clés et index: mode complémentaire, jamais mode principal.
- Objectif final: réduire la saisie utilisateur et maximiser le guidage visuel.

## 4) Architecture cible (haut niveau)
## 4.1 Couche données
- Airtable comme source opérationnelle principale
- Tables de référence: Themes, Sources, Articles
- Extension nécessaire pour les chiffres clés stylés (voir section 6)

## 4.2 Couche service (bridge Prova)
- API d'agrégation (lecture seule côté Prova au départ)
- Filtrage des champs sensibles (codes internes masqués)
- Caching des listes et des articles publiés

## 4.3 Couche présentation Prova
- Home identité
- Exploration par secteur -> thématique -> liste documents -> détail article
- Recherche contextualisée

### 4.4 Flux utilisateur cible (inspiré FileMaker)
- Étape 1: Arrivée sur Home (identité, mission, owner, CTA entrer).
- Étape 2: Écran orientation (cartographie des parcours disponibles).
- Étape 3: Navigation accordéon par secteur d'activité.
- Étape 4: Descente vers thématique puis liste de documents/articles.
- Étape 5: Consultation article avec mise en avant des chiffres clés.
- Étape 6: Option secondaire recherche par mots-clés / index.

## 5) Plan par volets
## 5.1 Volet A - Interface Airtable (admin)
### Objectifs
- Fiabiliser la chaîne éditoriale
- Standardiser les données publiées
- Préparer un export propre pour Prova

### Livrables
1. Vue Ingestion
- Contrôle des champs obligatoires
- Multi-sources liées
- Validation éditoriale avant publication

2. Vue Qualité
- Détection champs manquants
- Incohérences source/date/thème
- Statut publication (Brouillon, Validé, Publié)

3. Vue Publication
- Dataset filtré public
- Champs techniques cachés
- Horodatage publication

4. Automations minimales
- Mapping source texte -> Source_Ref
- Conservation de la source brute (champ Source) pour tri/recherche tel que saisi
- Tolérance de mapping: ne pas bloquer l'import si la normalisation Source n'est pas parfaite
- Génération slug titre
- Mise à jour index de recherche

## 5.2 Volet B - Interface externe Prova (mobile)
### Objectifs
- Donner une expérience de lecture professionnelle
- Rendre la recherche rapide et naturelle
- Valoriser les chiffres clés visuellement

### Livrables
1. Home/Branding
- Logo principal
- Baseline projet
- Owner/identité institutionnelle
- CTA Entrer dans la base

1.b Home Orientation (obligatoire)
- Bloc "Commencer par un secteur"
- Bloc "Accéder à l'index des mots-clés"
- Bloc "Entrer par série" (c3 Combien ça coûte, Série Entreprise)
- Micro-guides expliquant le parcours attendu

2. Navigation
- Secteurs (niveau 1)
- Thématiques (niveau 2)
- Résultats documents/articles (niveau 3)
- Détail article (niveau 4)
- Comportement accordéon (défilement progressif, ouvertures/fermetures)

3. Recherche
- Onglet A (primaire): Recherche par secteur
- Onglet B (primaire): Recherche dans la thématique
- Onglet C (secondaire): Mots-clés / index général
- Suggestions contextuelles

4. Détail article
- Titre, source lisible, date, extrait
- Bloc Chiffres clés mis en avant
- Corps texte structuré

## 6) Spécification cruciale: Chiffres clés et apparence
Pour reproduire l'intention éditoriale, le modèle doit passer de texte simple à modèle structuré.

### 6.1 Modèle de données recommandé
Créer une table liée Chiffres_Stars (ou champ JSON versionné) avec:
- article_id
- ordre_affichage
- valeur
- unite
- legende
- niveau_importance (1..3)
- style_token (STAR_PRIMARY, STAR_SECONDARY, STAR_CONTEXT)
- color_token
- weight_token
- size_token

### 6.2 Règles de rendu Prova
- STAR_PRIMARY: taille haute, contraste fort
- STAR_SECONDARY: taille moyenne, accent couleur
- STAR_CONTEXT: taille normale, lisible, non agressive
- Garantir lisibilité mobile (pas de style décoratif non lisible)
- Respecter la logique éditoriale historique observée dans les captures FileMaker (hiérarchie visuelle explicite).

### 6.3 Compatibilité avec l'existant
- Garder les champs Chiffre_Star et Legende_Chiffre en fallback
- Mapper progressivement vers le modèle structuré

## 7) Design system proposé (pro, simple, fidèle)
### Direction visuelle
- Fond neutre clair ou gris doux
- Accent jaune de marque
- Texte principal sombre à haut contraste
- Style sobre, éditorial, sans surcharge

### Typographie
- Priorité lisibilité (sans-serif)
- Hiérarchie claire des tailles
- Éviter styles fantaisie

### Composants clés
- Cartes article
- Chips secteur/thématique
- Bloc chiffres clés
- Barre de recherche
- Fil d'ariane

## 8) Feuille de route d'exécution (6 semaines)
## Semaine 1 - Cadrage final produit
- Valider parcours utilisateur Prova
- Valider structure de publication Airtable
- Figer design tokens initiaux
- Valider officiellement la métaphore produit "Porte -> Maison -> Cuisine" avec écrans correspondants

## Semaine 2 - Data model + gouvernance Airtable
- Ajouter modèle Chiffres_Stars
- Ajouter statuts de publication
- Vues Ingestion/Qualité/Publication

## Semaine 3 - API bridge Prova
- Endpoints lecture (secteurs, thèmes, articles)
- Filtrage champs privés
- Cache + pagination

## Semaine 4 - Prova shell + navigation
- Home branding
- Home orientation
- Parcours arborescent
- Liste résultats + détail article

## Semaine 5 - Recherche + rendu STAR
- Recherche par secteur/thématique
- Recherche index/mots-clés (secondaire)
- Bloc chiffres clés stylé
- Ajustements typographiques

## Semaine 6 - QA, performance, livraison
- Tests UX mobile
- Tests données (cohérence Airtable -> Prova)
- Hardening et préparation release

## 9) Critères d'acceptation
### Airtable
- Un article validé possède toutes les métadonnées requises
- Les sources sont liées en multi-référence et affichées en libellé lisible
- Le tri/recherche par désignation source brute reste possible (ex: LVE, La Vie Economique)
- Les données publiées sont filtrées des codes internes

### Prova
- Temps d'accès au détail article <= 2 interactions depuis une liste
- Recherche retourne des résultats pertinents dans le bon contexte
- Chiffres clés ressortent visuellement sans nuire à la lisibilité
- Écran d'accueil transmet clairement identité + objectif du projet
- Parcours principal sans saisie clavier possible (secteur -> thème -> document)
- Mode mots-clés présent mais secondaire dans l'architecture de navigation

## 10) Démarrage immédiat (ordre d'action)
1. Figer le schéma Airtable de publication + table Chiffres_Stars
2. Produire les wireframes Prova: Home identité + Home orientation + accordéon secteur
3. Définir les design tokens (couleur, typo, tailles, styles STAR)
4. Construire parcours nominal complet sans saisie clavier
5. Brancher recherche métier + index secondaire + bloc chiffres clés stylé
6. QA conjointe avec un jeu de 20 articles réels

## 11) Addendum échanges client (30/03/2026 -> 01/04/2026)
### 11.1 Décisions UX/Navigation confirmées
- Le parcours principal reste sector-first: Domaine/Secteur -> Thème -> Article.
- La recherche par mots-clés/index est maintenue mais en mode secondaire.
- La page d'accueil (ou 2eme écran) doit exposer explicitement les séries c1/c2/c3/c4.
- La catégorie "Autres grands thèmes" (code domaine 9) est confirmée dans le périmètre navigation.

### 11.2 Décisions éditoriales de présentation
- Intégrer le contenu de la diapo 4 ("de quoi s'agit-il") dans une page "A propos".
- Intégrer le mode d'emploi (diapos 14-15) sous forme de guide visuel aligné sur l'interface réelle.
- Rappel validé: Airtable accepte pièces jointes PDF/images, mais ne permet pas une mise en page éditoriale riche inline dans le corps d'article.
- Contournement produit validé: rendu éditorial avancé dans l'interface mobile Prova (POC), Airtable restant le back-office.

### 11.3 Stratégie Source (mode test puis montée en puissance)
- Approche duale retenue:
  - normalisation intelligente conservée (Source_Ref pour robustesse et futur scaling),
  - désignation brute conservée (champ Source) pour tri/recherche immédiat selon la réalité des articles.
- En phase test, la perfection de normalisation n'est pas un prérequis bloquant.
- Cas d'usage explicitement accepté: obtenir des listes par source brute même avec variantes d'écriture.
- Côté lecteur final, privilégier l'affichage lisible; masquer les codes techniques.

### 11.4 Ingestion volumique et logistique fichiers
- Pour lots volumineux (au-dela des limites mail), transfert via Google Drive validé.
- Les archives WinRAR servent de base de test pour démarrer sur un premier grand lot.
- Objectif cible confirmé: trajectoire vers 20.000+ documents avec supervision humaine (controle/validation) au-dessus du flux IA.

### 11.5 Gouvernance de la connaissance projet
- Les échanges WhatsApp/audio/email doivent etre centralises, structures par sujet et verses dans le conteneur documentaire.
- Ces echanges sont consideres comme actifs de cadrage produit, non comme historique passif.

### 11.6 Impacts planning immediats
- Sprint test: prioriser livraison rapide d'un flux robuste plutot que normalisation parfaite des sources.
- Ajouter une vue Airtable de tri par Source brute en parallele des liens Source_Ref.
- POC Prova: prioriser ecrans "A propos" + "Mode d'emploi" pour contextualiser la valeur B3D des l'entree.

---
Plan prêt pour passage en exécution. Ce document restera la base de pilotage projet App/Airtable + Prova.
