import { TAXONOMY } from './fullTaxonomy';
import { PUBLIC_CATALOG } from './publicCatalog.generated';

export type SeriesCode = 'c1' | 'c2' | 'c3' | 'c4';

export type Sector = {
  id: string;
  label: string;
  description: string;
};

export type Theme = {
  id: string;
  sectorId: string;
  code: string;
  label: string;
};

export type KeyFigure = {
  level: 1 | 2 | 3;
  value: string;
  legend: string;
};

export type ArticleVisual = {
  url: string;
  filename?: string;
  title?: string;
};

export type Article = {
  id: string;
  sectorId: string;
  themeId: string;
  series: SeriesCode;
  title: string;
  source: string;
  date: string;
  excerpt: string;
  content: string;
  keywords: string[];
  keyFigures: KeyFigure[];
  visuals?: ArticleVisual[];
  documentUrl?: string;
  catalogId?: string;
  catalogSlug?: string;
  catalogTimestampUTC?: string;
  catalogFingerprint?: string;
};

export const SERIES = [
  { code: 'c1' as const, label: 'Général' },
  { code: 'c2' as const, label: 'Fichier Entreprises' },
  { code: 'c3' as const, label: 'Combien ça coûte ?' },
  { code: 'c4' as const, label: 'Publications eG' },
];


type LiveCatalogPayload = {
  sectors?: unknown;
  themes?: unknown;
  articles?: unknown;
};

const TEST_MARKERS = ['test', 'mock', 'demo', 'sandbox', 'sample', 'e2e'];

function normalizeSeries(value: unknown): SeriesCode {
  const series = String(value ?? '').trim().toLowerCase();
  if (series === 'c2') {
    return 'c2';
  }
  if (series === 'c3') {
    return 'c3';
  }
  if (series === 'c4') {
    return 'c4';
  }
  return 'c1';
}

function normalizeLevel(level: unknown, fallback: 1 | 2 | 3): 1 | 2 | 3 {
  const levelText = String(level ?? '').trim();
  if (levelText === '1') {
    return 1;
  }
  if (levelText === '2') {
    return 2;
  }
  if (levelText === '3') {
    return 3;
  }
  return fallback;
}

function normalizeLiveSectors(value: unknown): Sector[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const output: Sector[] = [];
  for (const row of value) {
    const raw = row as Partial<Sector>;
    const id = String(raw.id ?? '').trim();
    const label = String(raw.label ?? '').trim();
    if (!id || !label) {
      continue;
    }

    output.push({
      id,
      label,
      description: String(raw.description ?? '').trim(),
    });
  }

  return output;
}

function normalizeLiveThemes(value: unknown): Theme[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const output: Theme[] = [];
  for (const row of value) {
    const raw = row as Partial<Theme>;
    const id = String(raw.id ?? '').trim();
    const sectorId = String(raw.sectorId ?? '').trim();
    const label = String(raw.label ?? '').trim();
    if (!id || !sectorId || !label) {
      continue;
    }

    output.push({
      id,
      sectorId,
      label,
      code: String(raw.code ?? '').trim(),
    });
  }

  return output;
}

function normalizeKeyFigures(value: unknown): KeyFigure[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const keyFigures: KeyFigure[] = [];
  for (let index = 0; index < value.length; index += 1) {
    const row = value[index] as Partial<KeyFigure> | undefined;
    if (!row) {
      continue;
    }

    const figureValue = String(row.value ?? '').trim();
    if (!figureValue) {
      continue;
    }

    keyFigures.push({
      level: normalizeLevel(row.level, index === 0 ? 1 : index === 1 ? 2 : 3),
      value: figureValue,
      legend: String(row.legend ?? 'Contexte non precise.').trim() || 'Contexte non precise.',
    });

    if (keyFigures.length >= 3) {
      break;
    }
  }

  return keyFigures;
}

function normalizeVisuals(value: unknown): ArticleVisual[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const visuals: ArticleVisual[] = [];
  for (const row of value) {
    const raw = row as Record<string, unknown>;
    const url = String(raw.url ?? '').trim();
    if (!url) {
      continue;
    }

    visuals.push({
      url,
      filename: String(raw.filename ?? '').trim() || undefined,
      title: String(raw.title ?? '').trim() || undefined,
    });
  }

  return visuals;
}

function isLikelyTestArticle(title: string, excerpt: string, source: string, keywords: string[]) {
  const haystack = `${title} ${excerpt} ${source} ${keywords.join(' ')}`.toLowerCase();
  return TEST_MARKERS.some((marker) => haystack.includes(marker));
}

function normalizeLiveArticles(value: unknown): Article[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const articles: Article[] = [];
  for (const row of value) {
    const raw = row as Record<string, unknown>;
    const article = raw as Partial<Article>;
    const id = String(article.id ?? '').trim();
    const sectorId = String(article.sectorId ?? '').trim();
    const themeId = String(article.themeId ?? '').trim();
    const title = String(article.title ?? '').trim();

    if (!id || !sectorId || !themeId || !title) {
      continue;
    }

    const keywords = Array.isArray(article.keywords)
      ? article.keywords
          .map((keyword) => String(keyword ?? '').trim())
          .filter((keyword) => keyword.length > 0)
      : [];

    const source = String(article.source ?? 'Source non precisee').trim() || 'Source non precisee';
    const excerpt = String(article.excerpt ?? '').trim();
    if (isLikelyTestArticle(title, excerpt, source, keywords)) {
      continue;
    }

    const visuals = normalizeVisuals(raw.visuals);

    articles.push({
      id,
      sectorId,
      themeId,
      series: normalizeSeries(article.series),
      title,
      source,
      date: String(article.date ?? '').trim(),
      excerpt,
      content: String(article.content ?? '').trim(),
      keywords,
      keyFigures: normalizeKeyFigures(article.keyFigures),
      visuals: visuals.length > 0 ? visuals : undefined,
      documentUrl: String(raw.documentUrl ?? '').trim() || undefined,
      catalogId: String(raw.catalogId ?? '').trim() || undefined,
      catalogSlug: String(raw.catalogSlug ?? '').trim() || undefined,
      catalogTimestampUTC: String(raw.catalogTimestampUTC ?? '').trim() || undefined,
      catalogFingerprint: String(raw.catalogFingerprint ?? '').trim() || undefined,
    });
  }

  return articles;
}

const rawLiveCatalog = PUBLIC_CATALOG as unknown as LiveCatalogPayload;
const liveSectors = normalizeLiveSectors(rawLiveCatalog.sectors);
const liveThemes = normalizeLiveThemes(rawLiveCatalog.themes);
const liveArticles = normalizeLiveArticles(rawLiveCatalog.articles);

export const SECTORS: Sector[] = liveSectors;
export const THEMES: Theme[] = liveThemes;
export const ARTICLES: Article[] = liveArticles;

export function getSectorById(sectorId: string) {
  return SECTORS.find((sector) => sector.id === sectorId);
}

export function getThemeById(themeId: string) {
  return THEMES.find((theme) => theme.id === themeId);
}

export function getThemesBySector(sectorId: string) {
  return THEMES.filter((theme) => theme.sectorId === sectorId);
}

export function getArticleById(articleId: string) {
  return ARTICLES.find((article) => article.id === articleId);
}

export function getArticlesByTheme(themeId: string) {
  return ARTICLES.filter((article) => article.themeId === themeId);
}

export function getArticlesBySeries(series: SeriesCode) {
  return ARTICLES.filter((article) => article.series === series);
}

export type SearchFilters = {
  domaineCode?: string;
  secteurCode?: string;
  sousSecteurCode?: string;
  themeCode?: string;
  series?: SeriesCode;
};

export function searchArticles(query: string, filters?: SearchFilters) {
  const q = query.trim().toLowerCase();
  return ARTICLES.filter((article) => {
    if (filters) {
      if (filters.series && article.series !== filters.series) {
        return false;
      }
      if (filters.themeCode) {
        const appTheme = THEMES.find(t => t.id === article.themeId);
        if (!appTheme || appTheme.code !== filters.themeCode) {
          return false;
        }
      }

      // Check hierarchy if higher-level filters are specified
      if (filters.domaineCode || filters.secteurCode || filters.sousSecteurCode) {
        const appTheme = THEMES.find(t => t.id === article.themeId);
        const themeMatch = appTheme ? TAXONOMY.themes.find(t => t.nom === appTheme.label || t.code === appTheme.code) : null;
        
        let matchesDomaine = true;
        let matchesSecteur = true;
        let matchesSousSecteur = true;

        if (themeMatch) {
          let domaineCode: string | undefined;
          let secteurCode: string | undefined;
          let sousSecteurCode: string | undefined;

          if (themeMatch.type_parent === 'Sous_Secteur') {
            sousSecteurCode = themeMatch.parent_ref;
            const ss = TAXONOMY.sous_secteurs.find(s => s.code === sousSecteurCode);
            if (ss) {
              secteurCode = ss.parent_secteur;
              domaineCode = ss.parent_domaine;
            }
          } else if (themeMatch.type_parent === 'Secteur') {
            secteurCode = themeMatch.parent_ref;
            const s = TAXONOMY.secteurs.find(sec => sec.code === secteurCode);
            if (s) {
              domaineCode = s.parent_domaine;
            }
          } else if (themeMatch.type_parent === 'Domaine') {
            domaineCode = themeMatch.parent_ref;
          }

          if (filters.domaineCode && domaineCode !== filters.domaineCode) matchesDomaine = false;
          if (filters.secteurCode && secteurCode !== filters.secteurCode) matchesSecteur = false;
          if (filters.sousSecteurCode && sousSecteurCode !== filters.sousSecteurCode) matchesSousSecteur = false;
        } else {
          // Fallback if no taxonomy mapping
          if (filters.secteurCode && article.sectorId !== filters.secteurCode) matchesSecteur = false;
          if (filters.domaineCode) matchesDomaine = false;
          if (filters.sousSecteurCode) matchesSousSecteur = false;
        }

        if (!matchesDomaine || !matchesSecteur || !matchesSousSecteur) {
          return false;
        }
      }
    }

    if (!q) {
      return true;
    }

    const inTitle = article.title.toLowerCase().includes(q);
    const inExcerpt = article.excerpt.toLowerCase().includes(q);
    const inContent = article.content.toLowerCase().includes(q);
    const inSource = article.source.toLowerCase().includes(q);
    const inKeywords = article.keywords.some((keyword) => keyword.toLowerCase().includes(q));
    return inTitle || inExcerpt || inContent || inSource || inKeywords;
  });
}

export function getFullBreadcrumbsForTheme(themeId: string) {
  const appTheme = THEMES.find(t => t.id === themeId);
  const themeMatch = appTheme ? TAXONOMY.themes.find(t => t.nom === appTheme.label || t.code === appTheme.code) : null;
  if (!appTheme || !themeMatch) return [];
  const theme = themeMatch;

  let domaine: any;
  let secteur: any;
  let sousSecteur: any;

  if (theme.type_parent === 'Sous_Secteur') {
    sousSecteur = TAXONOMY.sous_secteurs.find(ss => ss.code === theme.parent_ref);
    if (sousSecteur) {
      secteur = TAXONOMY.secteurs.find(s => s.code === sousSecteur.parent_secteur);
      if (secteur) {
        domaine = TAXONOMY.domaines.find(d => d.code === secteur.parent_domaine);
      }
    }
  } else if (theme.type_parent === 'Secteur') {
    secteur = TAXONOMY.secteurs.find(s => s.code === theme.parent_ref);
    if (secteur) {
      domaine = TAXONOMY.domaines.find(d => d.code === secteur.parent_domaine);
    }
    } else if (theme.type_parent === 'Domaine') {
      domaine = TAXONOMY.domaines.find(d => d.code === theme.parent_ref);
    }

    const breadcrumbs = [];
    if (domaine) breadcrumbs.push({ type: 'domaine', label: domaine.nom, id: domaine.code });
    if (secteur) breadcrumbs.push({ type: 'secteur', label: secteur.nom, id: secteur.code });
    if (sousSecteur) breadcrumbs.push({ type: 'sousSecteur', label: sousSecteur.nom, id: sousSecteur.code });
    breadcrumbs.push({ type: 'theme', label: theme.nom, id: theme.code });

    return breadcrumbs;
  }