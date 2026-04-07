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
- [x] Verifier les champs de liaison (Theme, Article_Ref) ; Source_Ref conserve mais non-operatoire pour le flux courant
- [x] Retirer la dependance au statut de publication dans le flux non-tech

### 2.2 Vues operationnelles

- [x] Vue Ingestion (controle champs obligatoires)
- [x] Vue Qualite (incoherences et manques)
- [x] Vue Disponibilite App + synchronisation catalogue PWA
- [x] Vue tri Source brute (usage phase test)

### 2.3 Automations et scripts

- [x] Mode source extraite uniquement active (Source_Ref mis en veille operationnelle)
- [x] Conservation source brute pour tri/recherche
- [x] Generation du catalogue public PWA sans filtre de statut
- [x] Verification script de backfill Chiffres_Stars

### 2.4 Qualite et validation

- [x] Controle permissions Airtable (token + tables)
- [x] Controle coherence Articles <-> Chiffres_Stars
- [x] Controle presence Source extraite (sans dependance Source_Ref)
- [x] Jalon Airtable stable valide - date: 2026-04-06

## 3) Suivi des blocages

- [x] Aucun blocage critique actif
- [x] Blocage #1 resolu: Champ statut publication configure dans Articles (Brouillon, Valide, Publie)
- [x] Blocage #2 clos: aucun blocage residuel sur le scope Prova + Airtable stabilise

## 4) Journal court

- 2026-04-07: Bascule versionnee PWA executee: snapshot historique conserve en dossier `prova-pwa-0`, nouvelle branche produit active en `prova-pwa-1`. Refonte UX/UI V1 livree avec palette pro sombre (orange/teal), onboarding 3 etapes (Porte -> Maison -> Cuisine), navigation E1->E7 modernisee, accordon secteurs, recherche filtree (secteur/theme/serie + tri), page article numbers-first (STAR PRIMARY/SECONDARY/CONTEXT) et pages Series/A propos/Mode d'emploi harmonisees. Validation: `npx tsc --noEmit` OK sur `prova-pwa-1`.
- 2026-04-07: Export catalogue PWA rendu multi-cible via `scripts/export_public_catalog_for_pwa.py --output-dir <app-dir>` pour synchroniser independamment `prova-pwa` et `prova-pwa-1`. Script `sync:airtable` de `prova-pwa-1` aligne sur cette option.
- 2026-04-07: Ajustement demande metier chiffres cles: validation legende assouplie sur principe QUOI obligatoire / QUAND optionnel, renforcement priorite des indices de mise en forme (gras, element saillant), et passe de normalisation OCR supplementaire pour nettoyer les artefacts monetaire/accents dans ingestion + export.
- 2026-04-06: Correctif qualite chiffres cles contextuels: extraction renforcee pour lier strictement valeur + legende autonome (quoi/ou/quand), ajout support JSON structure `chiffres_cles` dans le prompt Gemini, comprehension article explicite (sujet + chronologie + evolutions multi-dates) pour tous les sujets, priorisation des paires structurees dans la normalisation, fallback base sur contenu markdown (equivalences monetaires, fusion duree `5 heure 30`, reduction des fragments decontexualises), et ajustement export avec inférence de legendes generalisee (non dependante du cas Tunnel).
- 2026-04-06: Durcissement ingestion IA en Gemini-only: suppression du fallback Groq (app.py + scripts/04_article_ingestion_gemini.py), passage modele principal sur gemini-2.5-flash avec secours gemini-2.5-flash-lite, retry progressif 503/429, matching source aligne sur modele Gemini configure, et ingest_app.py harmonise sur les memes modeles/retry. Validation: py_compile OK, diagnostics VS Code OK.
- 2026-04-06: Ajustement visuel cible client finalise: transformation de l'ecran d'entree en vraie landing de presentation (logo anime, bloc mission/proprietaire CERD, integration de l'image Visuels/Chiffres cles, CTA directs vers Mode d'emploi et App), harmonisation navigation retour accueil vers la landing, et renforcement mise en evidence E6 (chiffres cles plus contrastes/tailles plus fortes).
- 2026-04-06: Correctif extraction Chiffres Stars renforce (ingestion + export): meilleure capture des unites monetaires depuis le contexte gras, filtrage des valeurs non essentielles (annees seules), inferer legendes contextuelles, limitation a 3 valeurs saillantes. Verification sur Tunnel: valeurs monetaires prioritaires avec legendes coherentes.
- 2026-04-06: Correctifs UX + qualite extraction finalises avant reset des tables: logo officiel transparent integre sur accueil (fin du placeholder texte), ecran accueil recentre sur presentation projet/owner + acces Mode d emploi et App, suppression du fallback mock dans la PWA + filtrage des enregistrements test/mock/e2e a l export public, integration des visuels Cloudinary dans E6 (image + titre), et durcissement du pipeline Chiffres Stars (max 3 valeurs saillantes uniquement, exclusion des chiffres de contexte non mis en evidence). Validations: export catalogue OK, TypeScript OK, py_compile OK.
- 2026-04-06: Lot refonte UX PWA livre (style editorial 2026, onboarding logo anime + sequence A propos -> Mode d emploi -> Base, navigation sector-first modernisee E1->E7, detail article renforce avec chiffres cles hierarchises sans labels techniques de niveau, et CTA "Voir l article" branche sur URL document source quand disponible).
- 2026-04-06: Recommandation delivery communiquee: conserver Streamlit pour l ingestion cet apres-midi (time-to-value immediat), et planifier ensuite une migration progressive vers le stack Expo uniquement si besoin de demo unifiee front + back-office.
- 2026-04-06: Simplification interface ingestion app.py: cockpit operateur conserve (suivi ingestion + disponibilite app + synchro), diagnostics techniques de qualite/source deplaces dans un panneau replie "Diagnostics internes (avance)".
- 2026-04-06: Validation technique post-refonte OK: export catalogue PWA regenere avec champ documentUrl, TypeScript `npx tsc --noEmit` OK, `py_compile` OK sur app.py et scripts/export_public_catalog_for_pwa.py.
- 2026-04-06: Audit + correctif workflow source finalises: app.py aligne en "source extraite uniquement" (retrait des controles et ecrans operationnels Source_Ref/codes source, suppression du mapping 1 clic Source_Ref, controles qualite bases sur presence de source extraite), et scripts/export_public_catalog_for_pwa.py force l'usage de la source extraite texte pour le dataset PWA.
- 2026-04-06: Simplification du flux ingestion non-tech validee: suppression de la logique statut de publication dans le pont PWA (export sans filtre de statut), suppression de l'ecriture forcee Statut_Publication en ingestion, remplacement de la zone "Vue Publication" par "Disponibilite App" + bouton de synchro PWA, et synchro automatique apres creation d'article.
- 2026-04-06: Point 1 finalise: pont de donnees PWA live Airtable en place (script scripts/export_public_catalog_for_pwa.py), generation automatique prova-pwa/src/data/publicCatalog.generated.ts, catalog PWA branche sur dataset 'Publie' avec fallback mock, validation compile TypeScript OK.
- 2026-04-06: Demarrage du projet PWA Expo Router (prova-pwa): routes E0->E7 + pages Series/A propos/Mode d emploi creees, dataset mock catalogue ajoute, navigation sector-first implementee (Secteur -> Theme -> Article), verification TypeScript `npx tsc --noEmit` OK.
- 2026-04-06: Nettoyage du tracking: placeholder Blocage #2 clos pour refléter 100% de realisation checklist scope actuel.
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
