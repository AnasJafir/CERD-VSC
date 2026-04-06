# Tracking d'avancement - Prova puis Airtable

Date de creation: 2026-04-01
Proprietaire du suivi: Equipe projet CERD
Cadence conseillee: mise a jour quotidienne

## Mode d'emploi

- Cocher `[x]` quand la tache est terminee.
- Ajouter une note courte si blocage.
- Mettre la date de fin sur les jalons principaux.

## Etat global

- [x] Checklist initiale creee (2026-04-01)
- [x] MVP Prova pret pour test utilisateur
- [x] Interface Airtable admin stabilisee
- [x] Passage en recette complete

## 1) Interface externe / App mobile Prova (priorite 1)

### 1.1 Fondations UX

- [x] Valider le parcours nominal sans clavier (secteur -> theme -> article)
- [x] Valider la structure des ecrans E0 a E7
- [x] Valider les tokens visuels (couleurs, typo, tailles)

### 1.2 Ecrans coeur

- [x] E0 Splash (logo + chargement court)
- [x] E1 Home identite (projet + owner + promesse)
- [x] E2 Home orientation (3 entrees: secteur, serie, index)
- [x] E3 Accordeon secteurs (ouvert/ferme + compteur)
- [x] E4 Liste thematiques par secteur
- [x] E5 Liste articles avec badges
- [x] E6 Detail article (source lisible + extrait + contenu)
- [x] E7 Recherche index/mots-cles (secondaire)

### 1.3 Donnees et rendu

- [x] Masquer tous les codes techniques cote lecteur
- [x] Afficher les sources en libelles lisibles
- [x] Integrer le rendu Chiffres Stars (primary/secondary/context)
- [x] Verifier le fallback si donnees partielles

### 1.4 Qualite et validation

- [x] Test mobile (navigation + lisibilite)
- [x] Test performance (chargement listes/articles)
- [x] Test utilisateur interne sur 20 articles reels
- [x] Jalon Prova MVP valide - date: 2026-04-06

## 2) Interface Airtable (priorite 2)

### 2.1 Structure et gouvernance

- [x] Verifier la structure des tables (Articles, Themes, Sources, Chiffres_Stars)
- [x] Verifier les champs de liaison (Theme, Source_Ref, Article_Ref)
- [x] Verifier les statuts de publication (Brouillon, Valide, Publie)

### 2.2 Vues operationnelles

- [x] Vue Ingestion (controle champs obligatoires)
- [x] Vue Qualite (incoherences et manques)
- [x] Vue Publication (dataset public filtre)
- [x] Vue tri Source brute (usage phase test)

### 2.3 Automations et scripts

- [x] Mapping Source texte -> Source_Ref (tolerant)
- [x] Conservation source brute pour tri/recherche
- [x] Generation/metadonnees techniques de publication
- [x] Verification script de backfill Chiffres_Stars

### 2.4 Qualite et validation

- [x] Controle permissions Airtable (token + tables)
- [x] Controle coherence Articles <-> Chiffres_Stars
- [x] Controle coherence Source brute <-> Source_Ref
- [x] Jalon Airtable stable valide - date: 2026-04-06

## 3) Suivi des blocages

- [x] Aucun blocage critique actif
- [x] Blocage #1 resolu: Champ statut publication configure dans Articles (Brouillon, Valide, Publie)
- [ ] Blocage #2: ____

## 4) Journal court

- 2026-04-06: Verification UI finale export public enrichi: clic bouton "Telecharger dataset public enrichi CSV (Publie)" valide en runtime apres reduction sidebar Streamlit.
- 2026-04-06: Passage en recette complete valide (modes Assistant IA + Saisie manuelle verifies en runtime, publication enrichie et anti-diffusion confirms en etat nominal et en cas non publie).
- 2026-04-06: Recette runtime E2E Airtable validee sur app.py: transition workflow Valide -> Publie, apparition section publiee + export enrichi, et blocage anti-diffusion confirme quand statut non publie selectionne.
- 2026-04-06: Verification script 05_backfill_chiffres_stars.py executee (OK) : 0 creation, 1 article deja couvert, aucun article sans Chiffre_Star.
- 2026-04-06: Export publication enrichi dans app.py avec metadonnees techniques (Publication_ID, Slug_Publication, Publication_Timestamp_UTC, Publication_Fingerprint).
- 2026-04-06: Automatisation mapping tolerant Source texte -> Source_Ref ajoutee dans app.py (analyse + application 1 clic, sans ecraser la Source brute).
- 2026-04-06: Vue tri Source brute (phase test) ajoutee dans app.py avec regroupement des designations Source, tri par volume et filtre de detail, plus suivi couverture Source_Ref.
- 2026-04-06: Vue Ingestion + Vue Qualite ajoutees dans app.py (controle champs obligatoires + incoherences Source brute/Source_Ref + coherence Articles/Chiffres_Stars + detection Chiffres_Stars orphelins), smoke test runtime OK.
- 2026-04-06: Validation post-correctifs executee: py_compile + diagnostics OK sur app.py et ingest_app.py, smoke tests Streamlit OK (app admin + app ingestion).
- 2026-04-06: ingest_app.py aligne sur le SDK google-genai (import + appel generate_content) pour corriger l'erreur runtime ModuleNotFoundError sur google.generativeai.
- 2026-04-06: Warnings Streamlit deprecation traites (remplacement use_container_width par width='stretch' dans app.py et ingest_app.py).
- 2026-04-06: Test runtime workflow 1 clic execute dans app.py: article "Tunnel Maroc-Espagne pour 2050 ?" passe de Brouillon a Valide en base Airtable.
- 2026-04-06: Workflow statut publication ajoute dans app.py (transition 1 clic Brouillon -> Valide -> Publie).
- 2026-04-06: Vue Publication activee dans app.py avec filtre strict 'Publie' + controle bloquant anti-diffusion pour statuts Brouillon/Valide.
- 2026-04-06: Champ Airtable 'Statut_Publication' cree dans Articles (single select: Brouillon/Valide/Publie) + initialisation des enregistrements existants en Brouillon.
- 2026-04-06: Audit Airtable read-only execute: tables Articles/Themes/Sources/Chiffres_Stars presentes, liaisons Theme/Source_Ref/Article_Ref confirmees, permissions token+base OK. Gap restant: champ statut publication a configurer dans Articles.
- 2026-04-06: Jalon Prova MVP valide (GO utilisateur confirme). Passage vers stream Airtable priorite 2.
- 2026-04-06: Step 7 valide GO (validation metier explicite). Campagne interne 20 articles reels marquee complete + correction retour contextuel E6 vers E7 pour l'entree recherche.
- 2026-04-06: Step 7 pre-validation technique executee (TC1-TC4 OK sur app en run: corpus=46, 20 ouvertures E7->E6 sans crash, couverture multi-secteurs/themes, runtime stable). En attente GO metier explicite.
- 2026-04-06: Step 6 valide GO (tests passes). Pages A propos + Mode d'emploi validees.
- 2026-04-06: Etape 7 prototype livre (corpus QA 20+ articles, suivi runtime corpus en sidebar) dans prova_step1_app.py. En attente de validation GO/NO-GO Step 7.
- 2026-04-06: Etape 6 prototype livre (pages A propos + Mode d'emploi + series c1/c2/c3/c4 visibles depuis orientation) dans prova_step1_app.py. En attente de validation GO/NO-GO Step 6.
- 2026-04-06: Step 5 valide GO (tests passes). Qualite/performance percue validee + ajustement parent domaine-first sans prefixes.
- 2026-04-06: Step 4 valide GO (tests passes). Tokens visuels et lisibilite mobile valides.
- 2026-04-06: Etape 5 prototype livre (qualite/performance percue: placeholders, retry, mode performance mobile, mesures de rendu E5/E7) dans prova_step1_app.py. En attente de validation GO/NO-GO Step 5.
- 2026-04-03: Step 3 valide GO (tests passes). Donnees et rendu editorial valides.
- 2026-04-03: Etape 4 prototype livre (tokens visuels: couleurs/typo/tailles + lisibilite mobile) dans prova_step1_app.py. En attente de validation GO/NO-GO Step 4.
- 2026-04-03: Step 2 valide GO (tests passes). Structure E0 a E7 validee.
- 2026-04-03: Etape 1 prototype livre (prova_step1_app.py) + protocole de test GO/NO-GO cree.
- 2026-04-01: checklist creee, ordre de travail valide (Prova puis Airtable).
