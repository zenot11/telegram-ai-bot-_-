const form = document.querySelector("#search-form");
const tabButtons = document.querySelectorAll("[data-tab-target]");
const tabPanels = document.querySelectorAll(".tab-panel");
const resultsNode = document.querySelector("#results");
const filterResultsNode = document.querySelector("#filter-results");
const favoritesNode = document.querySelector("#favorites-list");
const statusNode = document.querySelector("#status-text");
const filterStatusNode = document.querySelector("#filter-status");
const favoritesStatusNode = document.querySelector("#favorites-status");
const resultsSection = document.querySelector("#results-section");
const summaryCard = document.querySelector("#summary-card");
const summaryContentNode = document.querySelector("#summary-content");
const adviceCard = document.querySelector("#advice-card");
const filterControlsNode = document.querySelector("#filter-controls");
const favoritesCountNode = document.querySelector("#favorites-count");
const clearFavoritesButton = document.querySelector("#clear-favorites");
const themeToggleButton = document.querySelector("#theme-toggle");

const SAFE_MARGIN = 25;
const AMBITIOUS_MARGIN = 20;
const FAVORITES_KEY = "aishaMiniAppFavorites";
const THEME_KEY = "aisha_theme";

let lastResults = [];
let displayedResults = [];
let activeFilter = "all";
let currentSearch = null;
let favorites = loadFavorites();

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
  }
});

clearFavoritesButton.addEventListener("click", () => {
  clearFavorites();
});

themeToggleButton?.addEventListener("click", () => {
  toggleTheme();
});

renderAll();

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
  const alreadyFavorite = isFavorite(item);

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
      <button class="favorite-button ${alreadyFavorite ? "is-added" : ""}" type="button" data-add-favorite data-favorite-key="${escapeAttribute(key)}">
        ${alreadyFavorite ? "В избранном" : "В избранное"}
      </button>
    </article>
  `;
}

function renderFavorites() {
  favoritesCountNode.textContent = String(favorites.length);

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
    const raw = window.localStorage.getItem(FAVORITES_KEY);
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

function addToFavorites(item) {
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
  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.impactOccurred("light");
  }
}

function removeFromFavorites(key) {
  favorites = favorites.filter((item) => makeFavoriteKey(item) !== key);
  saveFavorites();
  renderAll();
}

function clearFavorites() {
  favorites = [];
  saveFavorites();
  renderAll();
}

function findResultByKey(key) {
  return lastResults.find((item) => makeFavoriteKey(item) === key)
    || displayedResults.find((item) => makeFavoriteKey(item) === key)
    || favorites.find((item) => makeFavoriteKey(item) === key);
}

function isFavorite(item) {
  const key = makeFavoriteKey(item);
  return favorites.some((favorite) => makeFavoriteKey(favorite) === key);
}

function makeFavoriteKey(item) {
  return [
    item.university,
    item.program,
    item.city,
    item.min_score,
    item.type,
    item.url,
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

function getMinScore(item) {
  const value = Number(item.min_score);
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
