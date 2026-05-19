const form = document.querySelector("#search-form");
const tabButtons = document.querySelectorAll("[data-tab-target]");
const tabPanels = document.querySelectorAll(".tab-panel");
const resultsNode = document.querySelector("#results");
const filterResultsNode = document.querySelector("#filter-results");
const favoritesNode = document.querySelector("#favorites-list");
const statusNode = document.querySelector("#status-text");
const filterStatusNode = document.querySelector("#filter-status");
const favoritesStatusNode = document.querySelector("#favorites-status");
const favoritesSyncStatusNode = document.querySelector("#favorites-sync-status");
const resultsSection = document.querySelector("#results-section");
const summaryCard = document.querySelector("#summary-card");
const summaryContentNode = document.querySelector("#summary-content");
const adviceCard = document.querySelector("#advice-card");
const filterControlsNode = document.querySelector("#filter-controls");
const favoritesCountNode = document.querySelector("#favorites-count");
const comparisonCountNode = document.querySelector("#comparison-count");
const comparisonCounterNode = document.querySelector("#comparison-counter");
const comparisonStatusNode = document.querySelector("#comparison-status");
const comparisonSelectedNode = document.querySelector("#comparison-selected");
const comparisonTableNode = document.querySelector("#comparison-table");
const clearFavoritesButton = document.querySelector("#clear-favorites");
const clearComparisonButton = document.querySelector("#clear-comparison");
const themeToggleButton = document.querySelector("#theme-toggle");

const SAFE_MARGIN = 25;
const AMBITIOUS_MARGIN = 20;
const FAVORITES_KEY = "aisha_favorites";
const LEGACY_FAVORITES_KEY = "aishaMiniAppFavorites";
const THEME_KEY = "aisha_theme";
const COMPARISON_KEY = "aisha_compare";
const MAX_COMPARISON_ITEMS = 3;

let lastResults = [];
let displayedResults = [];
let activeFilter = "all";
let currentSearch = null;
let favorites = loadFavorites();
let comparisonItems = loadComparisonItems();
let comparisonNotice = "";
let favoritesSyncNotice = "";

const categoryMeta = {
  safe: {
    className: "safe",
    shortLabel: "Безопасный",
    label: "🟢 Безопасный вариант",
  },
  realistic: {
    className: "realistic",
    shortLabel: "Реалистичный",
    label: "🟡 Реалистичный вариант",
  },
  ambitious: {
    className: "ambitious",
    shortLabel: "Амбициозный",
    label: "🔴 Амбициозный вариант",
  },
};

const filterLabels = {
  all: "Все",
  safe: "Безопасные",
  realistic: "Реалистичные",
  ambitious: "Амбициозные",
  budget: "Бюджет",
  paid: "Платное",
};

const telegramWebApp = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
const telegramInitData = telegramWebApp?.initData || "";

initTheme();

if (telegramWebApp) {
  telegramWebApp.ready();
  telegramWebApp.expand();
}

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activateTab(button.dataset.tabTarget);
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const scoreValue = String(formData.get("score") || "").trim();
  const score = Number(scoreValue);
  const type = formData.get("education-type") === "paid" ? "paid" : "budget";
  const typeLabel = type === "paid" ? "Платное" : "Бюджет";

  const validationError = validateScore(scoreValue, score);
  if (validationError) {
    currentSearch = null;
    lastResults = [];
    displayedResults = [];
    renderAll();
    showStatus(validationError, true);
    scrollToResults();
    return;
  }

  currentSearch = {
    region: formData.get("region"),
    score,
    direction: formData.get("direction"),
    type,
    typeLabel,
  };

  const params = new URLSearchParams({
    region: currentSearch.region,
    score: String(score),
    direction: currentSearch.direction,
    type,
    limit: "5",
  });

  showStatus("Ищу варианты...");
  resultsNode.innerHTML = "";
  filterResultsNode.innerHTML = "";

  try {
    const response = await fetch(`/api/universities?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const payload = await response.json();
    if (!Array.isArray(payload)) {
      throw new Error("Unexpected backend response");
    }

    lastResults = payload
      .filter((item) => classifyUniversity(score, item) !== "unavailable")
      .map((item) => ({
        ...item,
        category: classifyUniversity(score, item),
        saved_score: score,
      }));
    activeFilter = "all";
    renderAll();

    if (!lastResults.length) {
      showStatus("По таким параметрам вариантов не найдено. Проверь регион, направление или тип обучения. Небольшие опечатки я стараюсь исправлять автоматически.");
    } else {
      showStatus(`Нашла вариантов: ${lastResults.length}. Сейчас используются демонстрационные данные.`);
    }

    scrollToResults();
  } catch (error) {
    lastResults = [];
    displayedResults = [];
    renderAll();
    showStatus("Backend-заглушка недоступна. Запусти python -m backend_stub.main.", true);
    scrollToResults();
  }
});

document.addEventListener("click", (event) => {
  const filterButton = event.target.closest("[data-filter]");
  if (filterButton) {
    applyFilter(filterButton.dataset.filter);
    return;
  }

  const favoriteButton = event.target.closest("[data-add-favorite]");
  if (favoriteButton) {
    const item = findResultByKey(favoriteButton.dataset.favoriteKey);
    addToFavorites(item);
    return;
  }

  const removeButton = event.target.closest("[data-remove-favorite]");
  if (removeButton) {
    removeFromFavorites(removeButton.dataset.favoriteKey);
    return;
  }

  const compareButton = event.target.closest("[data-compare-key]");
  if (compareButton) {
    toggleCompare(compareButton.dataset.compareKey);
    return;
  }

  const removeCompareButton = event.target.closest("[data-remove-compare]");
  if (removeCompareButton) {
    removeFromComparison(removeCompareButton.dataset.compareKey);
  }
});

clearFavoritesButton.addEventListener("click", () => {
  clearFavorites();
});

clearComparisonButton.addEventListener("click", () => {
  clearComparison();
});

themeToggleButton?.addEventListener("click", () => {
  toggleTheme();
});

renderAll();
initFavoritesSync();

function initTheme() {
  applyTheme(getPreferredTheme());
}

function getPreferredTheme() {
  const savedTheme = getSavedTheme();
  if (savedTheme) {
    return savedTheme;
  }
  return telegramWebApp?.colorScheme === "dark" ? "dark" : "light";
}

function getSavedTheme() {
  try {
    const savedTheme = window.localStorage.getItem(THEME_KEY);
    return ["light", "dark"].includes(savedTheme) ? savedTheme : "";
  } catch (error) {
    return "";
  }
}

function saveTheme(theme) {
  try {
    window.localStorage.setItem(THEME_KEY, theme);
  } catch (error) {
    return;
  }
}

function applyTheme(theme) {
  const safeTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = safeTheme;

  if (themeToggleButton) {
    const isDark = safeTheme === "dark";
    themeToggleButton.textContent = isDark ? "☀️ Светлая" : "🌙 Тёмная";
    themeToggleButton.setAttribute("aria-pressed", String(isDark));
    themeToggleButton.setAttribute("title", isDark ? "Включить светлую тему" : "Включить тёмную тему");
  }
}

function toggleTheme() {
  const currentTheme = document.documentElement.dataset.theme === "dark" ? "dark" : "light";
  const nextTheme = currentTheme === "dark" ? "light" : "dark";
  applyTheme(nextTheme);
  saveTheme(nextTheme);

  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.selectionChanged();
  }
}

function activateTab(tabName) {
  const safeTabName = tabName || "home";
  tabPanels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === safeTabName);
  });
  tabButtons.forEach((button) => {
    const isActive = button.dataset.tabTarget === safeTabName;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function validateScore(rawValue, score) {
  if (!rawValue) {
    return "Введи баллы ЕГЭ.";
  }
  if (/^-\d+$/.test(rawValue)) {
    return "Баллы не могут быть отрицательными.";
  }
  if (!/^\d+$/.test(rawValue)) {
    return "Баллы нужно ввести числом, например: 230.";
  }
  if (score < 0) {
    return "Баллы не могут быть отрицательными.";
  }
  if (score > 400) {
    return "Проверь сумму баллов. Обычно сумма ЕГЭ указывается в пределах 0–400.";
  }
  return "";
}

function renderAll() {
  renderSearchResults();
  renderSummary();
  renderAdvice();
  renderFilterControls();
  renderFilteredResults();
  renderFavorites();
  renderComparison();
}

function renderSearchResults() {
  if (!lastResults.length) {
    resultsNode.innerHTML = "";
    return;
  }
  resultsNode.innerHTML = renderCards(lastResults, currentSearch?.score || 0);
}

function renderSummary() {
  if (!currentSearch) {
    summaryCard.classList.add("is-hidden");
    summaryContentNode.innerHTML = "";
    return;
  }

  const counts = getFilterCounts(lastResults);
  summaryCard.classList.remove("is-hidden");
  summaryContentNode.innerHTML = `
    <div><b>Регион:</b> ${escapeHtml(currentSearch.region)}</div>
    <div><b>Направление:</b> ${escapeHtml(currentSearch.direction)}</div>
    <div><b>Тип:</b> ${escapeHtml(currentSearch.typeLabel)}</div>
    <div><b>Баллы:</b> ${currentSearch.score}</div>
    <div><b>Найдено:</b> ${lastResults.length}</div>
    <div><b>Безопасные:</b> ${counts.safe} · <b>Реалистичные:</b> ${counts.realistic} · <b>Амбициозные:</b> ${counts.ambitious}</div>
    <div><b>Избранное:</b> ${favorites.length}</div>
  `;
}

function renderAdvice() {
  if (!currentSearch) {
    adviceCard.classList.add("is-hidden");
    adviceCard.innerHTML = "";
    return;
  }

  const counts = getFilterCounts(lastResults);
  let text = "Попробуй изменить регион, направление или тип обучения.";

  if (lastResults.length && counts.safe >= Math.max(1, counts.realistic + counts.ambitious)) {
    text = "У тебя есть варианты с запасом. Сохрани 1–2 подходящих и проверь сайты вузов.";
  } else if (lastResults.length && counts.ambitious > 0 && counts.safe + counts.realistic === 0) {
    text = "Варианты есть, но запас небольшой. Попробуй другой регион или платное обучение как запасной сценарий.";
  } else if (lastResults.length) {
    text = "Есть несколько вариантов для сравнения. Сохрани интересные программы и посмотри фильтры по уровню поступления.";
  }

  adviceCard.classList.remove("is-hidden");
  adviceCard.innerHTML = `
    <h3>Совет</h3>
    <p>${escapeHtml(text)}</p>
    <p>Проходные баллы могут меняться, поэтому перед подачей документов проверь информацию на сайте вуза.</p>
  `;
}

function renderFilterControls() {
  const counts = getFilterCounts(lastResults);
  const filters = ["all", "safe", "realistic", "ambitious", "budget", "paid"];
  filterControlsNode.innerHTML = filters.map((filterName) => {
    const count = counts[filterName] ?? lastResults.length;
    const isActive = activeFilter === filterName;
    return `
      <button class="filter-chip ${isActive ? "is-active" : ""}" type="button" data-filter="${filterName}">
        ${escapeHtml(filterLabels[filterName])} <span>${count}</span>
      </button>
    `;
  }).join("");
}

function applyFilter(filterName) {
  activeFilter = filterLabels[filterName] ? filterName : "all";
  renderFilterControls();
  renderFilteredResults();
  activateTab("filters");
  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.selectionChanged();
  }
}

function renderFilteredResults() {
  displayedResults = filterResults(lastResults, activeFilter);

  if (!currentSearch) {
    filterStatusNode.textContent = "Сначала сделай подбор, чтобы включить фильтры.";
    filterResultsNode.innerHTML = "";
    return;
  }

  if (!displayedResults.length) {
    filterStatusNode.textContent = `По фильтру “${filterLabels[activeFilter]}” вариантов нет. Попробуй другой фильтр или измени параметры подбора.`;
    filterResultsNode.innerHTML = "";
    return;
  }

  filterStatusNode.textContent = `Фильтр: ${filterLabels[activeFilter]}. Показано ${displayedResults.length} из ${lastResults.length}.`;
  filterResultsNode.innerHTML = renderCards(displayedResults, currentSearch.score);
}

function filterResults(results, filterName) {
  if (!Array.isArray(results) || filterName === "all") {
    return Array.isArray(results) ? [...results] : [];
  }

  if (["safe", "realistic", "ambitious"].includes(filterName)) {
    return results.filter((item) => getItemCategory(item) === filterName);
  }

  if (filterName === "budget") {
    return results.filter((item) => normalizeType(item.type) === "budget");
  }

  if (filterName === "paid") {
    return results.filter((item) => normalizeType(item.type) === "paid");
  }

  return [...results];
}

function getFilterCounts(results) {
  const items = Array.isArray(results) ? results : [];
  return {
    all: items.length,
    safe: items.filter((item) => getItemCategory(item) === "safe").length,
    realistic: items.filter((item) => getItemCategory(item) === "realistic").length,
    ambitious: items.filter((item) => getItemCategory(item) === "ambitious").length,
    budget: items.filter((item) => normalizeType(item.type) === "budget").length,
    paid: items.filter((item) => normalizeType(item.type) === "paid").length,
  };
}

function renderCards(items, score) {
  return items.map((item, index) => renderCard(item, score, index + 1)).join("");
}

function renderCard(item, score, index) {
  const category = getItemCategory(item, score);
  const meta = categoryMeta[category] || categoryMeta.ambitious;
  const subjects = Array.isArray(item.subjects) && item.subjects.length
    ? item.subjects.join(", ")
    : "не указаны";
  const minScore = getMinScore(item);
  const delta = minScore === null ? null : score - minScore;
  const key = makeFavoriteKey(item);
  const compareKey = getUniversityKey(item);
  const alreadyFavorite = isFavorite(item);
  const alreadyCompared = isCompared(item);

  return `
    <article class="result-card">
      <div class="result-card__top">
        <h3>${index}. ${escapeHtml(textValue(item.university, "Вуз"))} — ${escapeHtml(textValue(item.program, "программа не указана"))}</h3>
        <span class="badge ${meta.className}">${meta.label}</span>
      </div>
      <div class="result-meta">
        <div><b>Город:</b> ${escapeHtml(textValue(item.city, "не указан"))}</div>
        <div><b>Предметы:</b> ${escapeHtml(subjects)}</div>
        <div><b>Мин. балл:</b> ${escapeHtml(formatValue(minScore))}</div>
        <div><b>Твои баллы:</b> ${score}</div>
        <div><b>${delta === null ? "Запас" : delta >= 0 ? "Запас" : "Не хватает"}:</b> ${escapeHtml(formatDelta(delta))}</div>
        <div><b>Тип:</b> ${escapeHtml(textValue(item.type, "не указан"))}</div>
        <div><b>Стоимость:</b> ${escapeHtml(formatPrice(item.price))}</div>
        ${item.study_form ? `<div><b>Форма:</b> ${escapeHtml(item.study_form)}</div>` : ""}
        ${item.duration ? `<div><b>Срок:</b> ${escapeHtml(item.duration)}</div>` : ""}
        ${item.url ? `<div><b>Сайт:</b> <a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a></div>` : ""}
        <div><b>Пометка:</b> демонстрационные данные</div>
      </div>
      <div class="card-actions">
        <button class="favorite-button ${alreadyFavorite ? "is-added" : ""}" type="button" data-add-favorite data-favorite-key="${escapeAttribute(key)}">
          ${alreadyFavorite ? "В избранном" : "В избранное"}
        </button>
        <button class="favorite-button compare-button ${alreadyCompared ? "is-added" : ""}" type="button" data-compare-key="${escapeAttribute(compareKey)}">
          ${alreadyCompared ? "В сравнении" : "Добавить к сравнению"}
        </button>
      </div>
    </article>
  `;
}

function renderFavorites() {
  favoritesCountNode.textContent = String(favorites.length);
  renderFavoritesSyncStatus();

  if (!favorites.length) {
    favoritesStatusNode.textContent = "Избранное пока пустое. Добавь подходящий вариант из результатов подбора.";
    favoritesNode.innerHTML = "";
    clearFavoritesButton.disabled = true;
    return;
  }

  favoritesStatusNode.textContent = `Сохранено вариантов: ${favorites.length}.`;
  clearFavoritesButton.disabled = false;
  favoritesNode.innerHTML = favorites.map((item, index) => renderFavoriteCard(item, index + 1)).join("");
}

function renderFavoritesSyncStatus() {
  if (!favoritesSyncStatusNode) {
    return;
  }
  if (favoritesSyncNotice) {
    favoritesSyncStatusNode.textContent = favoritesSyncNotice;
    return;
  }
  favoritesSyncStatusNode.textContent = hasTelegramAuth()
    ? "Избранное синхронизируется с Telegram-ботом."
    : "Локальный режим: избранное хранится только в этом браузере.";
}

function renderFavoriteCard(item, index) {
  const score = Number(item.saved_score) || currentSearch?.score || getMinScore(item) || 0;
  const card = renderCard(item, score, index);
  const key = makeFavoriteKey(item);
  return card.replace(
    /<button class="favorite-button[\s\S]*?<\/button>/,
    `<button class="favorite-button favorite-button--remove" type="button" data-remove-favorite data-favorite-key="${escapeAttribute(key)}">Удалить из избранного</button>`
  );
}

function loadFavorites() {
  try {
    const raw = window.localStorage.getItem(FAVORITES_KEY) || window.localStorage.getItem(LEGACY_FAVORITES_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
}

function saveFavorites() {
  try {
    window.localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites));
  } catch (error) {
    favoritesStatusNode.textContent = "Не удалось сохранить избранное в браузере, но приложение продолжит работать.";
  }
}

async function initFavoritesSync() {
  if (!hasTelegramAuth()) {
    favoritesSyncNotice = "Локальный режим: избранное хранится только в этом браузере.";
    renderFavoritesSyncStatus();
    return;
  }

  try {
    const payload = await requestFavoritesApi("/api/favorites/sync", {
      local_favorites: favorites,
    });
    updateFavoritesFromServer(payload.favorites);
    favoritesSyncNotice = "Избранное синхронизировано с Telegram.";
    renderAll();
  } catch (error) {
    favoritesSyncNotice = "Сейчас избранное сохранено локально. Синхронизация будет доступна при открытии через Telegram.";
    renderFavoritesSyncStatus();
  }
}

function hasTelegramAuth() {
  return Boolean(telegramInitData);
}

async function requestFavoritesApi(path, body = null) {
  const options = {
    method: body ? "POST" : "GET",
    headers: {
      "X-Telegram-Init-Data": telegramInitData,
    },
  };
  if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.status === "error") {
    throw new Error(payload.error || `Favorites API returned ${response.status}`);
  }
  return payload;
}

function updateFavoritesFromServer(serverFavorites) {
  favorites = Array.isArray(serverFavorites) ? serverFavorites.filter((item) => item && typeof item === "object") : [];
  saveFavorites();
}

async function addToFavorites(item) {
  if (!item) {
    return;
  }
  if (!isFavorite(item)) {
    favorites = [
      ...favorites,
      {
        ...item,
        saved_score: currentSearch?.score || item.saved_score || getMinScore(item) || 0,
      },
    ];
    saveFavorites();
  }
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/add", { item });
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное синхронизировано с Telegram.";
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать с Telegram. Избранное сохранено локально.";
      renderFavoritesSyncStatus();
    }
  }

  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.impactOccurred("light");
  }
}

async function removeFromFavorites(key) {
  favorites = favorites.filter((item) => makeFavoriteKey(item) !== key);
  saveFavorites();
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/remove", { key });
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное синхронизировано с Telegram.";
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать удаление. Локальная копия обновлена.";
      renderFavoritesSyncStatus();
    }
  }
}

async function clearFavorites() {
  favorites = [];
  saveFavorites();
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/clear", {});
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное очищено и синхронизировано с Telegram.";
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать очистку. Локальная копия очищена.";
      renderFavoritesSyncStatus();
    }
  }
}

function renderComparison() {
  const count = comparisonItems.length;
  comparisonCountNode.textContent = String(count);
  comparisonCounterNode.textContent = `Выбрано: ${count}/${MAX_COMPARISON_ITEMS}`;
  clearComparisonButton.disabled = count === 0;
  comparisonSelectedNode.innerHTML = renderComparisonSelected();

  if (!count) {
    comparisonStatusNode.textContent = comparisonNotice || "Пока нечего сравнивать. Выполни подбор и добавь 2–3 варианта.";
    comparisonTableNode.innerHTML = "";
    return;
  }

  if (count === 1) {
    comparisonStatusNode.textContent = comparisonNotice || "Выбран 1 вариант. Добавь ещё один, чтобы увидеть таблицу сравнения.";
    comparisonTableNode.innerHTML = "";
    return;
  }

  comparisonStatusNode.textContent = comparisonNotice || "Сравни параметры и выбери наиболее подходящий вариант.";
  comparisonTableNode.innerHTML = renderComparisonTable(comparisonItems);
}

function renderComparisonSelected() {
  if (!comparisonItems.length) {
    return "";
  }

  return comparisonItems.map((item, index) => {
    const key = getUniversityKey(item);
    return `
      <article class="comparison-selected-card">
        <div>
          <b>${index + 1}. ${escapeHtml(textValue(item.university, "Вуз"))}</b>
          <span>${escapeHtml(textValue(item.program, "программа не указана"))}</span>
        </div>
        <button class="secondary-button danger-button" type="button" data-remove-compare="${escapeAttribute(key)}">Удалить</button>
      </article>
    `;
  }).join("");
}

function renderComparisonTable(items) {
  const highlights = getComparisonHighlights(items);
  const rows = [
    { label: "Вуз", value: (item) => textValue(item.university, "не указано") },
    { label: "Программа", value: (item) => textValue(item.program, "не указано") },
    { label: "Город", value: (item) => textValue(item.city, "не указано") },
    { label: "Регион", value: (item) => textValue(item.region, "не указано") },
    { label: "Направление", value: (item) => textValue(item.direction, "не указано") },
    { label: "Категория", highlight: "category", value: (item) => getCategoryLabel(item) },
    { label: "Мин. балл", highlight: "minScore", value: (item) => formatValue(getMinScore(item)) },
    { label: "Твои баллы", value: (item) => formatValue(getUserScore(item)) },
    { label: "Запас/не хватает", highlight: "margin", value: (item) => formatDelta(getScoreMargin(item)) },
    { label: "Тип обучения", highlight: "type", value: (item) => textValue(item.type, "не указано") },
    { label: "Стоимость", highlight: "price", value: (item) => formatPrice(item.price) },
    { label: "Форма", value: (item) => textValue(item.study_form, "не указано") },
    { label: "Срок", value: (item) => textValue(item.duration, "не указано") },
    { label: "Предметы", value: (item) => Array.isArray(item.subjects) && item.subjects.length ? item.subjects.join(", ") : "не указаны" },
    { label: "Сайт", html: (item) => item.url ? `<a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noopener noreferrer">Открыть сайт</a>` : "не указано" },
  ];

  return `
    <div class="comparison-table-scroll">
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Параметр</th>
            ${items.map((item, index) => `<th>${index + 1}. ${escapeHtml(textValue(item.university, "Вуз"))}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${rows.map((row) => `
            <tr>
              <th>${escapeHtml(row.label)}</th>
              ${items.map((item) => `
                <td class="${getComparisonCellClass(row.highlight, item, highlights)}">
                  ${row.html ? row.html(item) : escapeHtml(row.value(item))}
                </td>
              `).join("")}
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
    <p class="comparison-note">Сравнение носит справочный характер. Перед подачей документов проверь данные на официальных сайтах вузов.</p>
  `;
}

function getComparisonHighlights(items) {
  return {
    category: getBestKeys(items, (item) => getCategoryRank(getItemCategory(item)), "max"),
    minScore: getBestKeys(items, (item) => getMinScore(item), "min"),
    margin: getBestKeys(items, (item) => getScoreMargin(item), "max"),
    type: new Set(items.filter((item) => normalizeType(item.type) === "budget").map(getUniversityKey)),
    price: getBestKeys(items, (item) => getNumericPrice(item.price), "min"),
  };
}

function getBestKeys(items, extractor, mode) {
  const values = items
    .map((item) => ({ key: getUniversityKey(item), value: extractor(item) }))
    .filter((entry) => Number.isFinite(entry.value));

  if (!values.length) {
    return new Set();
  }

  const target = mode === "max"
    ? Math.max(...values.map((entry) => entry.value))
    : Math.min(...values.map((entry) => entry.value));

  return new Set(values.filter((entry) => entry.value === target).map((entry) => entry.key));
}

function getComparisonCellClass(highlightName, item, highlights) {
  if (!highlightName) {
    return "";
  }

  const key = getUniversityKey(item);
  if (highlights[highlightName]?.has(key)) {
    return highlightName === "category" || highlightName === "type" ? "compare-good" : "compare-best";
  }

  if (highlightName === "category" && getItemCategory(item) === "ambitious") {
    return "compare-warning";
  }

  if (highlightName === "margin" && Number(getScoreMargin(item)) < 0) {
    return "compare-warning";
  }

  return "";
}

function loadComparisonItems() {
  try {
    const raw = window.localStorage.getItem(COMPARISON_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed)
      ? parsed.filter((item) => item && typeof item === "object").slice(0, MAX_COMPARISON_ITEMS)
      : [];
  } catch (error) {
    return [];
  }
}

function saveComparisonItems() {
  try {
    window.localStorage.setItem(COMPARISON_KEY, JSON.stringify(comparisonItems.slice(0, MAX_COMPARISON_ITEMS)));
  } catch (error) {
    comparisonNotice = "Не удалось сохранить сравнение в браузере, но текущая таблица продолжит работать.";
  }
}

function toggleCompare(key) {
  const item = findItemByCompareKey(key);
  if (!item) {
    return;
  }

  if (isCompared(item)) {
    removeFromComparison(key);
    return;
  }

  if (comparisonItems.length >= MAX_COMPARISON_ITEMS) {
    comparisonNotice = "Можно сравнить до 3 вариантов одновременно.";
    renderAll();
    activateTab("comparison");
    return;
  }

  comparisonNotice = "";
  comparisonItems = [
    ...comparisonItems,
    {
      ...item,
      saved_score: currentSearch?.score || item.saved_score || getMinScore(item) || 0,
      category: getItemCategory(item),
    },
  ];
  saveComparisonItems();
  renderAll();

  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.impactOccurred("light");
  }
}

function removeFromComparison(key) {
  comparisonNotice = "";
  comparisonItems = comparisonItems.filter((item) => getUniversityKey(item) !== key);
  saveComparisonItems();
  renderAll();
}

function clearComparison() {
  comparisonNotice = "";
  comparisonItems = [];
  saveComparisonItems();
  renderAll();
}

function findResultByKey(key) {
  return lastResults.find((item) => makeFavoriteKey(item) === key)
    || displayedResults.find((item) => makeFavoriteKey(item) === key)
    || favorites.find((item) => makeFavoriteKey(item) === key);
}

function findItemByCompareKey(key) {
  return lastResults.find((item) => getUniversityKey(item) === key)
    || displayedResults.find((item) => getUniversityKey(item) === key)
    || favorites.find((item) => getUniversityKey(item) === key)
    || comparisonItems.find((item) => getUniversityKey(item) === key);
}

function isFavorite(item) {
  const key = makeFavoriteKey(item);
  return favorites.some((favorite) => makeFavoriteKey(favorite) === key);
}

function isCompared(item) {
  const key = getUniversityKey(item);
  return comparisonItems.some((comparedItem) => getUniversityKey(comparedItem) === key);
}

function makeFavoriteKey(item) {
  return getUniversityKey(item);
}

function getUniversityKey(item) {
  return [
    item.university,
    item.program,
    item.city,
    item.min_score,
    item.type,
  ].map((value) => textValue(value, "")).join("|");
}

function classifyUniversity(score, item) {
  const minScore = getMinScore(item);
  if (minScore === null) {
    return "unavailable";
  }
  if (minScore <= score - SAFE_MARGIN) {
    return "safe";
  }
  if (minScore <= score) {
    return "realistic";
  }
  if (minScore <= score + AMBITIOUS_MARGIN) {
    return "ambitious";
  }
  return "unavailable";
}

function getItemCategory(item, fallbackScore = currentSearch?.score || item.saved_score || 0) {
  if (item.category && categoryMeta[item.category]) {
    return item.category;
  }
  return classifyUniversity(Number(fallbackScore) || 0, item);
}

function getCategoryLabel(item) {
  const category = getItemCategory(item);
  return categoryMeta[category]?.shortLabel || "не указано";
}

function getCategoryRank(category) {
  const ranks = {
    safe: 3,
    realistic: 2,
    ambitious: 1,
  };
  return ranks[category] || 0;
}

function getUserScore(item) {
  const score = Number(item.saved_score || currentSearch?.score || 0);
  return Number.isFinite(score) && score > 0 ? score : null;
}

function getScoreMargin(item) {
  const score = getUserScore(item);
  const minScore = getMinScore(item);
  if (score === null || minScore === null) {
    return null;
  }
  return score - minScore;
}

function getMinScore(item) {
  const value = Number(item.min_score);
  return Number.isFinite(value) ? value : null;
}

function getNumericPrice(price) {
  if (price === null || price === undefined || price === "") {
    return null;
  }
  if (typeof price === "number") {
    return Number.isFinite(price) ? price : null;
  }

  const cleaned = String(price).replace(/[^\d.,]/g, "").replace(",", ".");
  const value = Number(cleaned);
  return Number.isFinite(value) ? value : null;
}

function normalizeType(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (["budget", "бюджет", "бюджетное", "бюджетный"].includes(normalized)) {
    return "budget";
  }
  if (["paid", "платное", "платный", "контракт"].includes(normalized)) {
    return "paid";
  }
  return normalized;
}

function formatDelta(delta) {
  if (delta === null) {
    return "недостаточно данных";
  }
  if (delta >= 0) {
    return `+${delta}`;
  }
  return `${Math.abs(delta)} баллов`;
}

function formatPrice(price) {
  if (price === null || price === undefined || price === "") {
    return "не указана";
  }
  const numericPrice = Number(price);
  if (Number.isFinite(numericPrice)) {
    return `${numericPrice.toLocaleString("ru-RU")} руб./год`;
  }
  return String(price);
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") {
    return "не указано";
  }
  return String(value);
}

function textValue(value, fallback) {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}

function showStatus(text, isError = false) {
  statusNode.textContent = text;
  statusNode.classList.toggle("status-error", isError);
}

function scrollToResults() {
  resultsSection?.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}
