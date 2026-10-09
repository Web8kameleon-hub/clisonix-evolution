const API_BASE_URL = window.location.origin;

const state = {
  articles: [],
  fallbackArticles: [],
  categories: [],
  selectedCategory: 'all',
  query: '',
  source: 'api'
};

const serviceCatalog = [
  { name: 'Dr. Albana', port: '8040', kind: 'Medical Engine' },
  { name: 'Blerina', port: '8035', kind: 'Content Engine' },
  { name: 'Blog Publisher', port: '8041', kind: 'Publishing' },
  { name: 'Content Factory', port: '8006', kind: 'Orchestration' },
  { name: 'Blog API', port: '8050', kind: 'Industrial UI' }
];

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function titleCase(value) {
  return String(value || '').replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function normalizeCategory(value) {
  return String(value || 'general')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'general';
}

function inferCategoryFromTitle(title) {
  const text = String(title || '').toLowerCase();
  if (text.includes('clinical') || text.includes('medical') || text.includes('patient')) return 'clinical-study';
  if (text.includes('diagnostic') || text.includes('diagnosis') || text.includes('fda')) return 'diagnostic';
  if (text.includes('privacy') || text.includes('gdpr') || text.includes('hipaa') || text.includes('compliance')) return 'compliance';
  if (text.includes('eeg') || text.includes('brain')) return 'neuroscience';
  if (text.includes('audio') || text.includes('speech') || text.includes('sound')) return 'audio-intelligence';
  return 'general';
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderServices() {
  const root = document.getElementById('servicesList');
  root.innerHTML = serviceCatalog.map(service => `
    <div class="d-flex justify-content-between align-items-center border rounded p-2">
      <div>
        <div class="fw-semibold">${escapeHtml(service.name)}</div>
        <small class="text-muted">${escapeHtml(service.kind)}</small>
      </div>
      <span class="badge text-bg-light service-pill">:${escapeHtml(service.port)}</span>
    </div>
  `).join('');
}

function buildQuery() {
  const params = new URLSearchParams({ limit: '60' });
  if (state.selectedCategory && state.selectedCategory !== 'all') {
    params.set('category', state.selectedCategory);
  }
  if (state.query.trim()) {
    params.set('q', state.query.trim());
  }
  return params.toString();
}

async function loadPublicationsFallback() {
  let publications;
  try {
    publications = await fetchJson('publications.json');
  } catch (_err) {
    publications = await fetchJson('./publications.json');
  }

  state.fallbackArticles = (publications || []).map((item, index) => {
    const tags = Array.isArray(item.tags) ? item.tags : [];
    const category = normalizeCategory(tags[0] || 'general');
    const filename = String(item.filename || '');
    const staticName = filename.endsWith('.md') ? filename.replace(/\.md$/i, '.html') : filename;
    return {
      id: item.filename || `publication-${index}`,
      title: item.title || item.filename || `Publication ${index + 1}`,
      preview: tags.length ? `Tags: ${tags.join(', ')}` : 'Publication synced from repository.',
      author: 'Clisonix AI',
      read_time: 4,
      category,
      url: staticName ? `static/${staticName}` : null,
      date: item.published || ''
    };
  });

  if (state.fallbackArticles.length < 10) {
    try {
      const backupHtml = await fetch('index.html.bak').then((r) => {
        if (!r.ok) throw new Error(`backup index failed: ${r.status}`);
        return r.text();
      });
      const entries = [];
      // Extract ARTICLES array from JavaScript in index.html.bak
      const arrayMatch = backupHtml.match(/const\s+ARTICLES\s*=\s*\[([\s\S]*?)\];/);
      if (arrayMatch) {
        try {
          // Parse the JavaScript array as JSON by wrapping it
          const jsonStr = '[' + arrayMatch[1] + ']';
          const articles = JSON.parse(jsonStr);
          articles.forEach((article, idx) => {
            entries.push({
              id: article.filename || `article-${idx}`,
              title: article.title || 'Untitled',
              preview: `Published: ${article.date || 'Unknown'}`,
              author: article.author || 'Clisonix AI',
              read_time: 4,
              category: inferCategoryFromTitle(article.title || ''),
              url: article.filename ? `static/${article.filename}` : null,
              date: article.date || ''
            });
          });
        } catch (parseErr) {
          // If direct JSON parse fails, try regex extraction
          const regex = /"filename":\s*"([^"]+)"[\s\S]*?"title":\s*"([^"]+)"[\s\S]*?"date":\s*"([^"]+)"/g;
          let match;
          while ((match = regex.exec(arrayMatch[1])) !== null) {
            entries.push({
              id: match[1],
              title: match[2],
              preview: `Published: ${match[3]}`,
              author: 'Clisonix AI',
              read_time: 4,
              category: inferCategoryFromTitle(match[2]),
              url: `static/${match[1]}`,
              date: match[3]
            });
          }
        }
      }
      if (entries.length) {
        state.fallbackArticles = entries;
      }
    } catch (_err) {
    }
  }

  const counts = new Map();
  for (const article of state.fallbackArticles) {
    counts.set(article.category, (counts.get(article.category) || 0) + 1);
  }
  state.categories = Array.from(counts.entries()).map(([key, count]) => ({ key, count }));
}

function getFilteredFallbackArticles() {
  const query = state.query.trim().toLowerCase();
  return state.fallbackArticles.filter((article) => {
    const categoryOk = state.selectedCategory === 'all' || article.category === state.selectedCategory;
    if (!categoryOk) {
      return false;
    }
    if (!query) {
      return true;
    }
    const haystack = `${article.title} ${article.preview} ${article.category}`.toLowerCase();
    return haystack.includes(query);
  });
}

async function loadCategories() {
  try {
    const payload = await fetchJson(`${API_BASE_URL}/api/v1/articles/categories`);
    state.categories = payload.categories || [];
    state.source = 'api';
  } catch (_err) {
    await loadPublicationsFallback();
    state.source = 'publications';
  }

  const select = document.getElementById('categorySelect');
  const options = ['<option value="all">All categories</option>'];
  for (const cat of state.categories) {
    options.push(`<option value="${escapeHtml(cat.key)}">${titleCase(cat.key)} (${cat.count})</option>`);
  }
  select.innerHTML = options.join('');

  renderCategoriesBoard();
}

function createDocCard(article) {
  const openLabel = article.url ? 'Read' : 'Open';
  return `
    <div class="col-md-6">
      <div class="card card-soft doc-card h-100" data-id="${escapeHtml(article.id)}">
        <div class="card-body d-flex flex-column">
          <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
            <span class="badge text-bg-primary badge-category">${escapeHtml(titleCase(article.category))}</span>
            <small class="text-muted">${escapeHtml(article.read_time)} min</small>
          </div>
          <h6 class="fw-bold">${escapeHtml(article.title)}</h6>
          <p class="preview mb-3">${escapeHtml(article.preview)}</p>
          <div class="mt-auto d-flex justify-content-between align-items-center">
            <small class="text-muted">${escapeHtml(article.author)}</small>
            <button class="btn btn-sm btn-outline-primary" data-open-id="${escapeHtml(article.id)}">${openLabel}</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function bindArticleOpenEvents() {
  document.querySelectorAll('[data-open-id]').forEach(btn => {
    btn.addEventListener('click', (event) => {
      event.preventDefault();
      const id = btn.getAttribute('data-open-id');
      const article = state.articles.find(a => a.id === id);
      if (article) {
        if (article.url) {
          const target = article.url.startsWith('http') ? article.url : `${window.location.origin}/${article.url.replace(/^\//, '')}`;
          window.open(target, '_blank', 'noopener,noreferrer');
          return;
        }
        openDocumentModal(article);
      }
    });
  });
}

function openDocumentModal(article) {
  document.getElementById('docModalTitle').textContent = article.title;
  document.getElementById('docModalBody').innerHTML = `
    <div class="mb-3">
      <span class="badge text-bg-primary me-2">${escapeHtml(titleCase(article.category))}</span>
      <span class="text-muted small">${escapeHtml(article.author)}</span>
    </div>
    <div class="alert alert-info mb-3">
      This is a classified preview. Use your full-access endpoint for complete content.
    </div>
    <article>${escapeHtml(article.preview)}</article>
  `;
  const modal = new bootstrap.Modal(document.getElementById('docModal'));
  modal.show();
}

function renderArticles() {
  const grid = document.getElementById('documentsGrid');
  grid.innerHTML = state.articles.map(createDocCard).join('');
  document.getElementById('resultCount').textContent = `${state.articles.length} results`;
  bindArticleOpenEvents();
}

function renderAdvancedResults() {
  const root = document.getElementById('advancedSearchResults');
  if (!state.query.trim()) {
    root.innerHTML = '<div class="col-12 text-muted">Type a search query to see results.</div>';
    return;
  }
  if (!state.articles.length) {
    root.innerHTML = '<div class="col-12"><div class="alert alert-warning mb-0">No documents matched this query.</div></div>';
    return;
  }
  root.innerHTML = state.articles.map(createDocCard).join('');
  bindArticleOpenEvents();
}

function renderCategoriesBoard() {
  const root = document.getElementById('categoriesBoard');
  if (!state.categories.length) {
    root.innerHTML = '<div class="col-12 text-muted">No categories are currently available.</div>';
    return;
  }
  root.innerHTML = state.categories.map(c => `
    <div class="col-md-4">
      <div class="card card-soft h-100">
        <div class="card-body">
          <h6 class="fw-bold mb-1">${escapeHtml(titleCase(c.key))}</h6>
          <p class="text-muted mb-2">Documents grouped by functional nature.</p>
          <span class="badge text-bg-light">${escapeHtml(c.count)} documents</span>
        </div>
      </div>
    </div>
  `).join('');
}

async function loadArticles() {
  if (state.source === 'api') {
    try {
      const query = buildQuery();
      state.articles = await fetchJson(`${API_BASE_URL}/api/v1/articles?${query}`);
    } catch (_err) {
      await loadPublicationsFallback();
      state.source = 'publications';
      state.articles = getFilteredFallbackArticles();
    }
  } else {
    state.articles = getFilteredFallbackArticles();
  }

  renderArticles();
  renderAdvancedResults();
}

async function handleSearch() {
  state.query = document.getElementById('searchInput').value || '';
  await loadArticles();
}

async function handleAdvancedSearch() {
  state.query = document.getElementById('advancedSearchInput').value || '';
  document.getElementById('searchInput').value = state.query;
  await loadArticles();
}

function bindEvents() {
  document.getElementById('searchBtn').addEventListener('click', handleSearch);
  document.getElementById('advancedSearchBtn').addEventListener('click', handleAdvancedSearch);
  document.getElementById('searchInput').addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      await handleSearch();
    }
  });
  document.getElementById('advancedSearchInput').addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      await handleAdvancedSearch();
    }
  });
  document.getElementById('categorySelect').addEventListener('change', async (e) => {
    state.selectedCategory = e.target.value;
    await loadArticles();
  });
}

async function bootstrap() {
  renderServices();
  bindEvents();
  await loadCategories();
  await loadArticles();
}

document.addEventListener('DOMContentLoaded', () => {
  bootstrap().catch((err) => {
    console.error(err);
    const grid = document.getElementById('documentsGrid');
    if (grid) {
      grid.innerHTML = '<div class="col-12"><div class="alert alert-danger">Failed to load UI data.</div></div>';
    }
  });
});
