# CERD Project Instructions for AI Agent

## 1) Mission and scope
- This project has 2 product scopes only:
  - Airtable back office interface
  - Prova external mobile interface (PWA first, native after)
- Do not drift into unrelated process tooling unless explicitly requested.
- This project is a high-value strategic asset ("travail en OR").
- When speed conflicts with quality, legal safety, or client vision, prioritize quality and safety.

## 2) Client vision (non-negotiable)
- Preserve the product metaphor: Door -> House -> Kitchen.
- Main journey must be guided and sector-first:
  - Sector -> Theme -> Article
- Keyword search exists but stays secondary.
- Reader-facing UI must never expose technical/internal codes.
- Sources must be shown with human-readable labels.
- Editorial readability is mandatory (not a SaaS dashboard style).
- Home must clearly present identity, purpose, and orientation paths.
- Keep visible series entries such as:
  - Combien ca coute ?
  - Fichier Entreprises

## 3) Information quality rules
- Never invent project facts, metrics, or source data.
- If data is uncertain, state uncertainty clearly and propose validation.
- Keep one-topic-per-article logic in mind.
- Preserve historical and editorial intent from provided visual and text references.
- Prefer concise, structured, decision-useful outputs.

## 4) Security baseline
- Never hardcode secrets, tokens, passwords, or API keys.
- Use environment variables and existing secure config files.
- Avoid exposing sensitive values in logs, terminal output, or generated docs.
- Apply least-privilege principles for integrations and API access.
- Do not run destructive commands unless explicitly requested and confirmed.
- Validate inputs and sanitize external content before processing.

## 5) Copyright and IP protection
- Treat all provided documents, logos, and visual assets as protected IP by default.
- Do not reproduce full third-party copyrighted content unless user confirms rights and need.
- Prefer transformation, summary, synthesis, and structured extraction over raw copying.
- Keep source attribution metadata when transforming article content.
- Preserve brand identity assets exactly as approved by the client.

## 6) Editorial and UX standards
- Mobile-first reading experience.
- High contrast and accessibility by default.
- Strong visual hierarchy for key figures.
- Maintain coherent French UX wording across screens and flows.
- Keep navigation orientation visible (context/breadcrumb/path cues).
- Response time and perceived speed are critical UX requirements.
- Treat slow data fetching as a product risk that can cause user drop-off.
- Prefer progressive loading patterns (skeletons/placeholders), short feedback loops, and graceful retry states.
- Prefer caching, pagination, and incremental fetching over large blocking payloads.
- Consider major performance regressions on reader-facing flows as high-priority defects.

## 7) Data model and publication behavior
- Respect dual source strategy:
  - Keep raw source value for traceability and practical sorting
  - Keep normalized source reference for scaling and data quality
- Keep compatibility with legacy fields when structured fields are missing.
- Do not block ingestion on imperfect source normalization in test phases.

## 8) Work protocol for the agent
- Follow these project files as primary references:
  - planning/plan_app_airtable_prova_mars2026.md
  - planning/blueprint_ux_filemaker_to_prova.md
  - planning/tracking_avancement.md
  - planning/prompts_frontend_v0_expo.md
- Before major changes, align with approved planning constraints.
- After meaningful milestones, update tracking with factual progress.
- Provide clear tradeoffs and risks when presenting options.

## 9) Definition of done mindset
A task is complete only when:
- It matches client vision and scope.
- Security and IP constraints are respected.
- Outputs are implementation-ready and testable.
- Any residual risk or assumption is explicitly documented.
