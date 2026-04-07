# Prompts Frontend - CERD Prova (PWA d'abord, natif ensuite)

Date: 2026-04-01
Contexte: Basé sur les echanges client + plan directeur + blueprint UX.

## 0) Outil recommande pour ce stack

Decision recommande:
- Outil principal de generation UI/UX: v0 (meilleur point de depart)
- Cible implementation: Expo (React Native) + React Native Web pour PWA

Pourquoi:
- v0 est tres bon pour sortir vite des ecrans, la structure, et les variantes UX.
- Expo est le meilleur socle pour garder un seul codebase Android/iOS + web.
- La combinaison permet: prototype rapide puis migration propre vers rendu natif.

## 1) Mode d'utilisation des prompts

Ordre conseille:
1. Prompt A (Vision + IA design global)
2. Prompt B (Navigation + parcours)
3. Prompt C (Recherche / filtres / tri)
4. Prompt D (Detail article + chiffres stars)
5. Prompt E (Design system + tokens)
6. Prompt F (Handoff vers stack Expo)

Recommandations d'usage:
- Joindre les captures de design et references visuelles au Prompt A.
- Rejouer le prompt suivant en demandant "iterate without breaking previous constraints".
- Conserver le meme vocabulaire d'ecrans E0 a E7.

---

## Prompt A - Vision produit et apparence globale (a coller dans v0)

```text
Act as a senior mobile product designer and frontend architect.

Project name:
CERD - B3D Chiffres Cles de l'Entreprise

Primary objective:
Design a premium, readable, mobile-first knowledge app experience with guided navigation.

Business constraints:
- Reader must never see internal technical codes.
- Sources must be displayed in human-readable labels.
- Main journey is guided (sector -> theme -> article), not keyword-first.
- Keyword search remains secondary.

UX metaphor to preserve:
1) Door: clear identity entry
2) House: clear map of where to go
3) Kitchen: practical tools for search/navigation

Visual direction:
- Editorial, professional, high readability
- Dominant brand style inspired by attached references (yellow/black/neutral gray)
- No generic dashboard look, no clutter
- Strong hierarchy for key figures

Required output:
1. A complete mobile-first app concept
2. Route map and screen hierarchy
3. Component inventory
4. Initial design tokens (color/typography/spacing)
5. French UI copy examples for key actions

Important:
Use attached screenshots as visual inspiration while modernizing interaction quality.
```

---

## Prompt B - Parcours utilisateur et navigation (a coller dans v0)

```text
Generate a detailed UX flow for this app with screens E0 to E7.

Non-negotiable flows:
- E0 Splash
- E1 Home Identite
- E2 Home Orientation with 3 entries:
  A) Commencer par un secteur
  B) Entrer par serie (c1, c2, c3, c4)
  C) Recherche index/mots-cles (secondary)
- E3 Secteurs as accordion cards (expand/collapse + article counters)
- E4 Thematiques under selected sector
- E5 Article list cards
- E6 Article detail
- E7 Search/index view

Behavior rules:
- Main journey must work without typing.
- Breadcrumb must show where the user is.
- Access to article detail should be <= 2 taps from a list.
- Maintain coherent labels in French across all screens.

Deliverables:
- User flow diagram (text + screen transitions)
- State variants (loading/empty/error/success)
- Interaction notes for mobile gestures and tap targets
- UX copy for helper text and CTA labels
```

---

## Prompt C - Recherche, filtres, tri, modes d'acces (a coller dans v0)

```text
Design all search and discovery modes for the app.

Priority order:
1) Sector-first exploration (primary)
2) Theme exploration (primary)
3) Keyword/index search (secondary)

Define and implement UX for:
- Search bar behavior and suggestions
- Filter chips (sector, theme, serie, date, source label)
- Sort options (pertinence, date desc, date asc, alphabetic)
- Grouped results by sector/theme
- Empty and no-result states with recovery actions

Critical constraints:
- Keep user oriented in hierarchy
- Do not expose technical source codes
- Source display must stay human-readable

Output required:
- UI screens for search/filter/sort
- Clear interaction specs (when filters combine, reset, persist)
- Mobile-first components and spacing guidance
```

---

## Prompt D - Detail article et bloc "Chiffres Stars" (a coller dans v0)

```text
Create the full article detail experience focused on readability and key figures.

Article detail sections:
1) Header: title, source label(s), publication date, badges (serie/theme)
2) Excerpt block
3) Key figures block (Chiffres Stars)
4) Body content
5) Related navigation actions

Key figures model to support:
- valeur
- unite
- legende
- ordre_affichage
- niveau_importance (1..3)
- style_token (STAR_PRIMARY, STAR_SECONDARY, STAR_CONTEXT)

Rendering rules:
- STAR_PRIMARY: highest emphasis
- STAR_SECONDARY: medium emphasis
- STAR_CONTEXT: supporting emphasis
- Keep readability and avoid decorative overload

Fallback rule:
If only legacy fields exist (single text blocks), still render cleanly.

Output required:
- Article detail UI with variants
- Key figures component system
- Content formatting recommendations for long reading on mobile
```

---

## Prompt E - Design system, style guide, composants (a coller dans v0)

```text
Generate a compact design system for this product.

Need:
- Colors (brand + neutral + semantic)
- Typography scale for mobile readability
- Spacing and radius tokens
- Component styles: cards, chips, accordions, search, breadcrumbs, article blocks
- Key-figure typography rules by importance level

Constraints:
- Professional editorial tone
- Strong contrast and accessibility
- Consistency between orientation/search/detail screens

Output required:
- Token table
- Component guideline table
- Do and don't examples
- French microcopy style rules
```

---

## Prompt F - Handoff technique vers stack Expo (a coller dans v0 ou IA code)

```text
Now produce a technical handoff package for implementation in:
- Expo React Native + Expo Router
- React Native Web (PWA first)
- TypeScript

Deliver:
1) Recommended folder architecture
2) Route structure mapping E0..E7
3) Shared component map
4) Data contracts for sector/theme/article/source/chiffres stars
5) State management recommendation
6) Platform notes: web PWA vs iOS/Android native adjustments

Important:
- Maximize shared code across web and native.
- Preserve visual/UX constraints previously defined.
- Keep technical codes hidden from reader-facing UI.
```

---

## 2) Prompt "consolidation finale" (apres iterations)

```text
Consolidate all previous outputs into one final spec:
- Product vision summary
- Final route map
- Final screen list E0..E7
- Search/filter/sort behavior matrix
- Component inventory
- Design token table
- Accessibility checklist
- Handoff checklist for Expo implementation

Do not remove any approved constraints from earlier iterations.
```

## 3) Ressources utiles a joindre (si disponibles)

Priorite haute:
- Captures d'ecrans de reference visuelle (historique + preferences)
- Logos et variantes
- Exemples d'articles reels (5 a 10)
- Exemples de "Chiffres Stars" bien formes

Priorite moyenne:
- Charte typo/couleur si existante
- Exemples de resultats de recherche souhaites

## 4) Note operationnelle

Si v0 genere trop "web dashboard", ajouter cette phrase:
"Rework the UI as an editorial mobile reading app, not a SaaS dashboard."

---

## 5) Prompt V2 - ancre sur tes visuels reels (a coller dans v0)

```text
Use the attached branding and legacy reference screens as hard visual anchors.

Brand assets observed:
- eD icon logo in black + lime-yellow
- Main banner text: "chiffres cles de l'entreprise" with "Arif M. Sadek"
- Signature background motif with subtle binary digits

Legacy UI patterns to preserve (modernized):
1) Three-column search orientation at entry:
  - Left: brand block
  - Middle: "RECHERCHE Par" (sector path)
  - Right: "RECHERCHE Dans" (thematic path)
2) Guided click bars with instructional copy ("Cliquez sur ...")
3) Tree-style hierarchical exploration from macro category to final article
4) Editorial reading destination (not analytics dashboard)

Mandatory modernized interpretation:
- Keep visual memory of the old product, but improve clarity, spacing, typography, and touch ergonomics.
- Keep the sector-first navigation as the default discovery mode.
- Keep thematic and series entry points visible from orientation screen.
- Keep keyword search as secondary.

Style directions extracted from references:
- Brand yellow + black as identity anchors
- Neutral grayscale for text hierarchy
- Optional soft binary texture only as subtle background accent
- Strong readability on mobile first

Generate:
- Final mobile-first UI concept preserving these references
- E0..E7 screens
- A dedicated "A propos" and "Mode d'emploi" section
- Search/filter/sort states
- Tree-navigation interaction pattern adapted for touch
```

## 6) Ressources integrees (extraction effectuee)

Ressources traitees depuis [Visuels](Visuels):
- Modele de Page d'accueil Appli. Mobile.docx
- Quelques Diapos pour projet Presentation PPT_ Mars 2026.pptx
- 4 PDF exemples d'articles:
  - La consommation du ciment. 2020-2024.pdf
  - Structure des prix de revient de la Briqueterie .pdf
  - Tunnel Maroc-Espagne .pdf
  - La Louisiane, vendue par la France aux USA en 1803, pour 15 millions de dollars..pdf

Sortie d'analyse complete:
- [planning/analysis_visuels_assets.txt](planning/analysis_visuels_assets.txt)

Constats majeurs integres dans la V3:
1. Promesse produit: acces a l'information en 2-3 clics sur smartphone.
2. Structure: 10 secteurs, plus de 250 themes, parcours arborescent.
3. Principe editorial: un sujet par document, une page, l'essentiel + chiffres cles.
4. Series explicites a exposer: "Combien ca coute ?" et "Entreprises".
5. Fiche article cible: Theme, Titre, Numero, Date, Extrait, Mots cles, Source, Corps.

## 7) Prompt V3 - version ultra-fidele aux contenus clients (a coller dans v0)

```text
Design a mobile-first editorial app based on the attached real project documents and legacy screens.

Project:
CERD - Chiffres cles de l'Entreprise

Core mission to preserve:
- Give decision-makers fast access to economic information in 2 to 3 taps.
- Convert information overload into structured, useful knowledge.
- Keep one precise topic per document, in one-page editorial format.

Audience:
- Cadres, dirigeants, analysts, journalists, researchers, finance/admin leaders.

Information architecture to implement:
- 10 sectors
- 250+ themes
- Articles grouped by thematic tree navigation
- Main discovery path must be:
  Sector -> Theme -> Article
- Secondary paths visible from home orientation:
  - "Combien ca coute ?"
  - "Fichier Entreprises"
  - keyword/index access (secondary)

Mandatory legacy labels to reinterpret cleanly:
- "RECHERCHE Par"
- "RECHERCHE Dans"
- "Cliquez sur ..." guidance style
- "Publications eG"

Required screen model:
- E0 Splash
- E1 Home Identite
- E2 Home Orientation (3 entries minimum)
- E3 Sector accordion / tree navigation
- E4 Theme list
- E5 Article list
- E6 Article detail
- E7 Search/index (secondary)

Article detail structure (must be explicit):
1) Theme / serie / date / source label(s)
2) Title
3) Excerpt
4) Key figures block with hierarchy (primary/secondary/context)
5) Body content with optional bullet points
6) Source mention and related actions

Data semantics to respect:
- Never expose internal technical codes in reader UI.
- Show human-readable source labels.
- Keep fallback rendering if only legacy text fields are available.

Visual identity constraints:
- Brand anchors: lime-yellow + black + neutral grays
- Editorial readability first, no SaaS dashboard style
- Optional subtle binary texture as a background accent

UX quality constraints:
- Main journey should not require typing.
- Clear hierarchy and orientation at every step.
- Max 2 interactions from list to article detail.
- Strong touch ergonomics and accessibility.

Generate output as:
1) Final UX flow and route map
2) High-fidelity screen set E0..E7
3) Search/filter/sort behavior matrix
4) Reusable component inventory
5) French microcopy suggestions
6) Implementation-ready handoff for Expo + React Native Web
```
