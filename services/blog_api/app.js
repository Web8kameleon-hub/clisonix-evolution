const API_BASE_URL = window.location.origin;

const state = {
  allArticles: [],
  articles: [],
  categories: [],
  selectedCategory: "all",
  selectedAuthor: "all",
  sortBy: "date_desc",
  query: "",
  page: 1,
  pageSize: 12,
  autoRefreshMs: 10000,
  refreshTimer: null,
  refreshInFlight: false,
};

const serviceCatalog = [
  { name: "Dr. Albana", port: "8040", kind: "Medical Engine" },
  { name: "Blerina", port: "8035", kind: "Content Engine" },
  { name: "Blog Publisher", port: "8041", kind: "Publishing" },
  { name: "Content Factory", port: "8006", kind: "Orchestration" },
  { name: "Blog API", port: "8050", kind: "Industrial UI" },
];

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function titleCase(value) {
  return String(value || "")
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function fetchArticleDetail(articleId) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/articles/${encodeURIComponent(articleId)}`,
  );
  if (!response.ok) {
    let detail = "";
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || "";
    } catch {
      detail = "";
    }
    const error = new Error(detail || `Request failed: ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

function debounce(fn, wait = 250) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), wait);
  };
}

function readStateFromUrl() {
  const params = new URLSearchParams(window.location.search);
  state.query = params.get("q") || "";
  state.selectedCategory = params.get("cat") || "all";
  state.selectedAuthor = params.get("author") || "all";
  state.sortBy = params.get("sort") || "date_desc";

  const parsedPage = Number(params.get("page") || 1);
  state.page = Number.isFinite(parsedPage) && parsedPage > 0 ? parsedPage : 1;
}

function syncInputsFromState() {
  const categorySelect = document.getElementById("categorySelect");
  const authorSelect = document.getElementById("authorSelect");
  const sortSelect = document.getElementById("sortSelect");
  const searchInput = document.getElementById("searchInput");
  const advancedSearchInput = document.getElementById("advancedSearchInput");

  if (
    [...categorySelect.options].some((o) => o.value === state.selectedCategory)
  ) {
    categorySelect.value = state.selectedCategory;
  } else {
    state.selectedCategory = "all";
    categorySelect.value = "all";
  }

  if ([...authorSelect.options].some((o) => o.value === state.selectedAuthor)) {
    authorSelect.value = state.selectedAuthor;
  } else {
    state.selectedAuthor = "all";
    authorSelect.value = "all";
  }

  if ([...sortSelect.options].some((o) => o.value === state.sortBy)) {
    sortSelect.value = state.sortBy;
  } else {
    state.sortBy = "date_desc";
    sortSelect.value = "date_desc";
  }

  searchInput.value = state.query;
  advancedSearchInput.value = state.query;
}

function updateUrlFromState() {
  const params = new URLSearchParams();
  if (state.query.trim()) {
    params.set("q", state.query.trim());
  }
  if (state.selectedCategory !== "all") {
    params.set("cat", state.selectedCategory);
  }
  if (state.selectedAuthor !== "all") {
    params.set("author", state.selectedAuthor);
  }
  if (state.sortBy !== "date_desc") {
    params.set("sort", state.sortBy);
  }
  if (state.page > 1) {
    params.set("page", String(state.page));
  }

  const query = params.toString();
  const nextUrl = query
    ? `${window.location.pathname}?${query}`
    : window.location.pathname;
  window.history.replaceState(null, "", nextUrl);
}

async function copyCurrentViewLink() {
  const fullUrl = `${window.location.origin}${window.location.pathname}${window.location.search}`;
  const button = document.getElementById("copyLinkBtn");
  const originalText = button.textContent;

  try {
    await navigator.clipboard.writeText(fullUrl);
    button.textContent = "Copied ✓";
    button.classList.remove("btn-outline-primary");
    button.classList.add("btn-success");
  } catch {
    button.textContent = "Copy failed";
    button.classList.remove("btn-outline-primary");
    button.classList.add("btn-danger");
  }

  setTimeout(() => {
    button.textContent = originalText;
    button.classList.remove("btn-success", "btn-danger");
    button.classList.add("btn-outline-primary");
  }, 1200);
}

function renderServices() {
  const root = document.getElementById("servicesList");
  root.innerHTML = serviceCatalog
    .map(
      (service) => `
    <div class="d-flex justify-content-between align-items-center border rounded p-2">
      <div>
        <div class="fw-semibold">${escapeHtml(service.name)}</div>
        <small class="text-muted">${escapeHtml(service.kind)}</small>
      </div>
      <span class="badge text-bg-light service-pill">:${escapeHtml(service.port)}</span>
    </div>
  `,
    )
    .join("");
}

async function loadCategories() {
  const payload = await fetchJson(`${API_BASE_URL}/api/v1/articles/categories`);
  state.categories = payload.categories || [];

  const select = document.getElementById("categorySelect");
  const options = ['<option value="all">Të gjitha kategoritë</option>'];
  for (const cat of state.categories) {
    options.push(
      `<option value="${escapeHtml(cat.key)}">${titleCase(cat.key)} (${cat.count})</option>`,
    );
  }
  select.innerHTML = options.join("");

  renderCategoriesBoard();
}

function renderAuthors() {
  const authors = [
    ...new Set(state.allArticles.map((a) => a.author).filter(Boolean)),
  ].sort((a, b) => a.localeCompare(b));
  const select = document.getElementById("authorSelect");
  const options = ['<option value="all">Të gjithë autorët</option>'];
  for (const author of authors) {
    options.push(
      `<option value="${escapeHtml(author)}">${escapeHtml(author)}</option>`,
    );
  }
  select.innerHTML = options.join("");
}

function createDocCard(article) {
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
            <button class="btn btn-sm btn-outline-primary" data-open-id="${escapeHtml(article.id)}">Hap</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function applyFiltersAndSort() {
  const q = state.query.trim().toLowerCase();

  let filtered = state.allArticles.filter((article) => {
    if (
      state.selectedCategory !== "all" &&
      article.category !== state.selectedCategory
    ) {
      return false;
    }
    if (
      state.selectedAuthor !== "all" &&
      article.author !== state.selectedAuthor
    ) {
      return false;
    }
    if (!q) {
      return true;
    }

    const haystack = [
      article.title,
      article.preview,
      article.category,
      article.author,
    ]
      .join(" ")
      .toLowerCase();

    return haystack.includes(q);
  });

  filtered.sort((a, b) => {
    if (state.sortBy === "title_asc") {
      return String(a.title || "").localeCompare(String(b.title || ""));
    }
    if (state.sortBy === "read_desc") {
      return Number(b.read_time || 0) - Number(a.read_time || 0);
    }

    const aDate = new Date(a.date || 0).getTime();
    const bDate = new Date(b.date || 0).getTime();
    if (state.sortBy === "date_asc") {
      return aDate - bDate;
    }
    return bDate - aDate;
  });

  state.articles = filtered;
}

function getPageStats() {
  const total = state.articles.length;
  const totalPages = Math.max(1, Math.ceil(total / state.pageSize));
  if (state.page > totalPages) {
    state.page = totalPages;
  }
  const start = (state.page - 1) * state.pageSize;
  const end = start + state.pageSize;
  return { total, totalPages, start, end };
}

function bindArticleOpenEvents() {
  document.querySelectorAll("[data-open-id]").forEach((btn) => {
    btn.addEventListener("click", async (event) => {
      event.preventDefault();
      const id = btn.getAttribute("data-open-id");
      const article = state.articles.find((a) => a.id === id);
      if (article) {
        await openDocumentModal(article);
      }
    });
  });
}

async function openDocumentModal(article) {
  const modalEl = document.getElementById("docModal");
  const modal = new bootstrap.Modal(modalEl);
  document.getElementById("docModalTitle").textContent = article.title;
  document.getElementById("docModalBody").innerHTML = `
    <div class="text-muted small">Duke ngarkuar përmbajtjen...</div>
  `;
  modal.show();

  try {
    const detail = await fetchArticleDetail(article.id);
    const contentHtml = escapeHtml(detail.content || "").replace(/\n/g, "<br>");
    document.getElementById("docModalBody").innerHTML = `
      <div class="mb-3">
        <span class="badge text-bg-primary me-2">${escapeHtml(titleCase(detail.category || article.category))}</span>
        <span class="text-muted small me-2">${escapeHtml(detail.author || article.author)}</span>
        <span class="text-muted small">${escapeHtml((detail.date || "").slice(0, 10))}</span>
      </div>
      <article style="line-height:1.7">${contentHtml || escapeHtml(article.preview)}</article>
    `;
    return;
  } catch (error) {
    const denied = error && (error.status === 401 || error.status === 403);
    const infoText = denied
      ? "Artikulli i plotë kërkon pagesë/subscription. Po shfaqet preview."
      : "Nuk u ngarkua dot artikulli i plotë. Po shfaqet preview.";

    document.getElementById("docModalBody").innerHTML = `
    <div class="mb-3">
      <span class="badge text-bg-primary me-2">${escapeHtml(titleCase(article.category))}</span>
      <span class="text-muted small">${escapeHtml(article.author)}</span>
    </div>
    <div class="alert alert-info mb-3">
      ${escapeHtml(infoText)}
    </div>
    <article>${escapeHtml(article.preview)}</article>
  `;
  }
}

function applyAndRender(shouldUpdateUrl = true) {
  applyFiltersAndSort();
  renderArticles();
  renderAdvancedResults();
  if (shouldUpdateUrl) {
    updateUrlFromState();
  }
}

function renderArticles() {
  const grid = document.getElementById("documentsGrid");
  const { total, totalPages, start, end } = getPageStats();
  const pageItems = state.articles.slice(start, end);

  if (!pageItems.length) {
    grid.innerHTML =
      '<div class="col-12"><div class="alert alert-warning mb-0">Nuk u gjet asnjë dokument. Provo kategori tjetër ose fjalë kyçe më të gjera.</div></div>';
  } else {
    grid.innerHTML = pageItems.map(createDocCard).join("");
  }

  document.getElementById("resultCount").textContent = `${total} rezultate`;
  document.getElementById("pageInfo").textContent =
    `Faqe ${state.page} / ${totalPages}`;
  document.getElementById("prevPageBtn").disabled = state.page <= 1;
  document.getElementById("nextPageBtn").disabled = state.page >= totalPages;
  bindArticleOpenEvents();
}

function renderAdvancedResults() {
  const root = document.getElementById("advancedSearchResults");
  if (
    !state.query.trim() &&
    state.selectedCategory === "all" &&
    state.selectedAuthor === "all"
  ) {
    root.innerHTML =
      '<div class="col-12 text-muted">Shkruaj një kërkim për të parë rezultatet.</div>';
    return;
  }
  if (!state.articles.length) {
    root.innerHTML =
      '<div class="col-12"><div class="alert alert-warning mb-0">Nuk u gjet asnjë dokument për këtë kërkim.</div></div>';
    return;
  }

  const { start, end } = getPageStats();
  root.innerHTML = state.articles.slice(start, end).map(createDocCard).join("");
  bindArticleOpenEvents();
}

function renderCategoriesBoard() {
  const root = document.getElementById("categoriesBoard");
  if (!state.categories.length) {
    root.innerHTML =
      '<div class="col-12 text-muted">Nuk ka kategori të disponueshme.</div>';
    return;
  }
  root.innerHTML = state.categories
    .map(
      (c) => `
    <div class="col-md-4">
      <div class="card card-soft h-100">
        <div class="card-body">
          <h6 class="fw-bold mb-1">${escapeHtml(titleCase(c.key))}</h6>
          <p class="text-muted mb-2">Dokumente sipas natyrës funksionale.</p>
          <span class="badge text-bg-light">${escapeHtml(c.count)} dokumente</span>
        </div>
      </div>
    </div>
  `,
    )
    .join("");
}

async function loadArticles() {
  state.allArticles = await fetchJson(
    `${API_BASE_URL}/api/v1/articles?skip=0&limit=5000`,
  );
  renderAuthors();
  syncInputsFromState();
  applyAndRender(false);
}

async function refreshLiveData() {
  if (state.refreshInFlight) {
    return;
  }

  state.refreshInFlight = true;
  try {
    await loadCategories();
    await loadArticles();
  } catch (error) {
    console.error("Auto-refresh failed:", error);
  } finally {
    state.refreshInFlight = false;
  }
}

function startAutoRefresh() {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
  }
  state.refreshTimer = setInterval(() => {
    refreshLiveData().catch(console.error);
  }, state.autoRefreshMs);
}

async function handleSearch() {
  state.query = document.getElementById("searchInput").value || "";
  document.getElementById("advancedSearchInput").value = state.query;
  state.page = 1;
  applyAndRender();
}

async function handleAdvancedSearch() {
  state.query = document.getElementById("advancedSearchInput").value || "";
  document.getElementById("searchInput").value = state.query;
  state.page = 1;
  applyAndRender();
}

function goToPrevPage() {
  if (state.page > 1) {
    state.page -= 1;
    applyAndRender();
  }
}

function goToNextPage() {
  const { totalPages } = getPageStats();
  if (state.page < totalPages) {
    state.page += 1;
    applyAndRender();
  }
}

function bindEvents() {
  document.getElementById("searchBtn").addEventListener("click", handleSearch);
  document
    .getElementById("advancedSearchBtn")
    .addEventListener("click", handleAdvancedSearch);
  document
    .getElementById("prevPageBtn")
    .addEventListener("click", goToPrevPage);
  document
    .getElementById("nextPageBtn")
    .addEventListener("click", goToNextPage);
  document
    .getElementById("copyLinkBtn")
    .addEventListener("click", copyCurrentViewLink);
  document.getElementById("sortSelect").addEventListener("change", (e) => {
    state.sortBy = e.target.value;
    state.page = 1;
    applyAndRender();
  });
  document.getElementById("authorSelect").addEventListener("change", (e) => {
    state.selectedAuthor = e.target.value;
    state.page = 1;
    applyAndRender();
  });

  const debouncedMainSearch = debounce(() => {
    handleSearch().catch(console.error);
  }, 280);

  document
    .getElementById("searchInput")
    .addEventListener("input", debouncedMainSearch);
  document
    .getElementById("searchInput")
    .addEventListener("keydown", async (e) => {
      if (e.key === "Enter") {
        await handleSearch();
      }
    });
  document
    .getElementById("advancedSearchInput")
    .addEventListener("keydown", async (e) => {
      if (e.key === "Enter") {
        await handleAdvancedSearch();
      }
    });
  document
    .getElementById("categorySelect")
    .addEventListener("change", async (e) => {
      state.selectedCategory = e.target.value;
      state.page = 1;
      applyAndRender();
    });
}

async function bootstrap() {
  readStateFromUrl();
  renderServices();
  bindEvents();
  await loadCategories();
  await loadArticles();
  startAutoRefresh();
  updateUrlFromState();
}

document.addEventListener("DOMContentLoaded", () => {
  bootstrap().catch((err) => {
    console.error(err);
    const grid = document.getElementById("documentsGrid");
    if (grid) {
      grid.innerHTML =
        '<div class="col-12"><div class="alert alert-danger">Gabim në ngarkimin e UI/API.</div></div>';
    }
  });
});

window.addEventListener("beforeunload", () => {
  if (state.refreshTimer) {
    clearInterval(state.refreshTimer);
    state.refreshTimer = null;
  }
});
