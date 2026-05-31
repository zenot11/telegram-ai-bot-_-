const form = document.querySelector("#search-form");
const tabButtons = document.querySelectorAll("[data-tab-target]");
const tabPanels = document.querySelectorAll(".tab-panel");
const resultsNode = document.querySelector("#results");
const filterResultsNode = document.querySelector("#filter-results");
const favoritesNode = document.querySelector("#favorites-list");
const statusNode = document.querySelector("#status-text");
const resultsActionsNode = document.querySelector("#results-actions");
const filterStatusNode = document.querySelector("#filter-status");
const favoritesStatusNode = document.querySelector("#favorites-status");
const favoritesSyncStatusNode = document.querySelector("#favorites-sync-status");
const sessionBadgeNode = document.querySelector("#session-badge");
const sessionCardNode = document.querySelector("#session-card");
const sessionDescriptionNode = document.querySelector("#session-description");
const sessionUserNode = document.querySelector("#session-user");
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
const planContentNode = document.querySelector("#plan-content");
const planCopyFallbackNode = document.querySelector("#plan-copy-fallback");
const exportContentNode = document.querySelector("#export-content");
const exportCopyFallbackNode = document.querySelector("#export-copy-fallback");
const feedbackForm = document.querySelector("#feedback-form");
const feedbackCategoryNode = document.querySelector("#feedback-category");
const feedbackMessageNode = document.querySelector("#feedback-message");
const feedbackStatusNode = document.querySelector("#feedback-status");
const feedbackResultNode = document.querySelector("#feedback-result");
const feedbackHistoryStatusNode = document.querySelector("#feedback-history-status");
const feedbackListNode = document.querySelector("#feedback-list");
const aishaHintNode = document.querySelector("#aisha-hint");
const aishaHintTextNode = document.querySelector("#aisha-hint-text");
const aishaHintActionButton = document.querySelector("#aisha-hint-action");
const aishaHintRefreshButton = document.querySelector("#aisha-hint-refresh");
const aishaHintHideButton = document.querySelector("#aisha-hint-hide");
const aishaHintShowButton = document.querySelector("#aisha-hint-show");
const clearFavoritesButton = document.querySelector("#clear-favorites");
const clearComparisonButton = document.querySelector("#clear-comparison");
const themeToggleButton = document.querySelector("#theme-toggle");
const clearFormButton = document.querySelector("#clear-form");
const clearFeedbackButton = document.querySelector("#feedback-clear");
const refreshFeedbackButton = document.querySelector("#feedback-refresh");
const quickScenarioButtons = document.querySelectorAll("[data-quick-scenario]");
const toastContainerNode = document.querySelector("#toast-container");

const SAFE_MARGIN = 25;
const AMBITIOUS_MARGIN = 20;
const FAVORITES_KEY = "aisha_favorites";
const LEGACY_FAVORITES_KEY = "aishaMiniAppFavorites";
const THEME_KEY = "aisha_theme";
const COMPARISON_KEY = "aisha_compare";
const HINTS_HIDDEN_KEY = "aisha_hints_hidden";
const MAX_COMPARISON_ITEMS = 3;

let lastResults = [];
let displayedResults = [];
let activeFilter = "all";
let activeTab = "home";
let isSearchLoading = false;
let currentSearch = null;
let favorites = loadFavorites();
let comparisonItems = loadComparisonItems();
let aishaHintsHidden = loadAishaHintsHidden();
let comparisonNotice = "";
let favoritesSyncNotice = "";
let feedbackTickets = [];
let latestLocalFeedbackTicket = null;
let sessionState = {
  status: "checking",
  mode: "checking",
  authenticated: false,
  user: null,
  message: "Проверяю режим открытия Mini App.",
};

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

const quickScenarios = {
  "adygea-it": {
    region: "Адыгея",
    score: 230,
    direction: "IT",
    type: "budget",
    label: "Адыгея · 230 · IT · Бюджет",
  },
  "moscow-economy": {
    region: "Москва",
    score: 260,
    direction: "экономика",
    type: "budget",
    label: "Москва · 260 · экономика · Бюджет",
  },
  "tatarstan-medicine": {
    region: "Татарстан",
    score: 250,
    direction: "медицина",
    type: "budget",
    label: "Татарстан · 250 · медицина · Бюджет",
  },
};

const feedbackCategoryLabels = {
  admission_question: "Вопрос по поступлению",
  search_problem: "Проблема с подбором вузов",
  mini_app_problem: "Проблема с Mini App",
  data_error: "Ошибка в данных",
  improvement: "Предложить улучшение",
  other: "Другое",
};

const telegramWebApp = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
const telegramInitData = getTelegramInitData();

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

form.addEventListener("submit", (event) => {
  event.preventDefault();
  performSearch();
});

quickScenarioButtons.forEach((button) => {
  button.addEventListener("click", () => {
    applyQuickScenario(button.dataset.quickScenario);
  });
});

clearFormButton?.addEventListener("click", () => {
  clearSearchForm();
});

feedbackForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  submitFeedback();
});

clearFeedbackButton?.addEventListener("click", () => {
  resetFeedbackForm();
});

refreshFeedbackButton?.addEventListener("click", () => {
  loadMyFeedback();
});

aishaHintActionButton?.addEventListener("click", () => {
  const actionTab = aishaHintActionButton.dataset.actionTab;
  if (actionTab) {
    activateTab(actionTab);
  }
});

aishaHintRefreshButton?.addEventListener("click", () => {
  updateAishaHint();
  showToast("Совет обновлён.", "info");
});

aishaHintHideButton?.addEventListener("click", () => {
  hideAishaHints();
});

aishaHintShowButton?.addEventListener("click", () => {
  showAishaHints();
});

async function performSearch() {
  const formData = new FormData(form);
  const scoreValue = String(formData.get("score") || "").trim();
  const score = Number(scoreValue);
  const type = formData.get("education-type") === "paid" ? "paid" : "budget";
  const typeLabel = type === "paid" ? "Платное" : "Бюджет";
  const region = String(formData.get("region") || "").trim();
  const direction = String(formData.get("direction") || "").trim();

  if (!region) {
    showStatus("Выбери регион для подбора.", true);
    showToast("Выбери регион.", "warning");
    activateTab("search");
    return;
  }
  if (!direction) {
    showStatus("Выбери направление для подбора.", true);
    showToast("Выбери направление.", "warning");
    activateTab("search");
    return;
  }
  const validationError = validateScore(scoreValue, score);
  if (validationError) {
    currentSearch = null;
    lastResults = [];
    displayedResults = [];
    renderAll();
    showStatus(validationError, true);
    showToast(validationError, "warning");
    scrollToResults();
    return;
  }

  currentSearch = {
    region,
    score,
    direction,
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
  isSearchLoading = true;
  updateAishaHint();

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
    isSearchLoading = false;
    renderAll();

    if (!lastResults.length) {
      showStatus("По этим параметрам вариантов не нашлось. Попробуй увеличить диапазон баллов, выбрать соседний регион или поменять тип обучения.");
      showToast("По этим параметрам вариантов не нашлось.", "warning");
    } else {
      showStatus(`Найдено: ${lastResults.length} вариантов. Можно сохранить, отфильтровать или сравнить.`);
      showToast(`Найдено: ${lastResults.length} вариантов.`, "success");
    }

    scrollToResults();
  } catch (error) {
    isSearchLoading = false;
    lastResults = [];
    displayedResults = [];
    renderAll();
    showStatus("Не удалось получить данные. Проверь подключение или попробуй позже.", true);
    showToast("Не удалось получить данные. Попробуй позже.", "error");
    scrollToResults();
  }
}

function applyQuickScenario(scenarioId) {
  const scenario = quickScenarios[scenarioId];
  if (!scenario) {
    return;
  }

  setFormValues(scenario);
  activateTab("search");
  showToast(`Сценарий применён: ${scenario.label}`, "success");
  performSearch();
}

function setFormValues({ region, score, direction, type }) {
  const regionInput = form.elements.region;
  const scoreInput = form.elements.score;
  const directionInput = form.elements.direction;
  const typeInput = form.querySelector(`input[name="education-type"][value="${type}"]`);

  if (regionInput) {
    ensureSelectOption(regionInput, region);
    regionInput.value = region;
  }
  if (scoreInput) {
    scoreInput.value = String(score);
  }
  if (directionInput) {
    ensureSelectOption(directionInput, direction);
    directionInput.value = direction;
  }
  if (typeInput) {
    typeInput.checked = true;
  }
}

function clearSearchForm() {
  form.reset();
  if (form.elements.region) {
    form.elements.region.value = "";
  }
  if (form.elements.direction) {
    form.elements.direction.value = "";
  }
  if (form.elements.score) {
    form.elements.score.value = "";
  }
  showStatus("Форма очищена. Последние результаты остались ниже.");
  showToast("Форма очищена.", "info");
}

async function loadBackendDirectories() {
  const [regions, directions] = await Promise.all([
    fetchDirectoryItems("/api/regions"),
    fetchDirectoryItems("/api/directions"),
  ]);

  if (regions.length) {
    replaceSelectOptions(form.elements.region, regions, "Выбери регион");
  }
  if (directions.length) {
    replaceSelectOptions(form.elements.direction, directions, "Выбери направление");
  }
}

async function fetchDirectoryItems(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return [];
    }
    const payload = await response.json();
    if (!Array.isArray(payload.items)) {
      return [];
    }
    return payload.items
      .map((item) => String(item || "").trim())
      .filter(Boolean)
      .slice(0, 200);
  } catch (error) {
    return [];
  }
}

function replaceSelectOptions(select, items, placeholder) {
  if (!select) {
    return;
  }
  const currentValue = select.value;
  const uniqueItems = [...new Set(items)];
  const placeholderOption = document.createElement("option");
  placeholderOption.value = "";
  placeholderOption.disabled = true;
  placeholderOption.textContent = placeholder;

  select.replaceChildren(placeholderOption);
  uniqueItems.forEach((item) => {
    const option = document.createElement("option");
    option.value = item;
    option.textContent = item;
    select.appendChild(option);
  });

  if (currentValue) {
    ensureSelectOption(select, currentValue);
    select.value = currentValue;
  } else {
    placeholderOption.selected = true;
  }
}

function ensureSelectOption(select, value) {
  if (!select || !value) {
    return;
  }
  const exists = Array.from(select.options).some((option) => option.value === value);
  if (exists) {
    return;
  }
  const option = document.createElement("option");
  option.value = value;
  option.textContent = value;
  select.appendChild(option);
}

document.addEventListener("click", (event) => {
  const tabTargetButton = event.target.closest("[data-tab-target]");
  if (tabTargetButton && !Array.from(tabButtons).includes(tabTargetButton)) {
    activateTab(tabTargetButton.dataset.tabTarget);
    return;
  }

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
    return;
  }

  const copyPlanButton = event.target.closest("[data-plan-copy]");
  if (copyPlanButton) {
    copyAdmissionPlan();
    return;
  }

  const refreshPlanButton = event.target.closest("[data-plan-refresh]");
  if (refreshPlanButton) {
    renderAdmissionPlan();
    showToast("План обновлён.", "success");
    return;
  }

  const copyExportButton = event.target.closest("[data-export-copy]");
  if (copyExportButton) {
    copyExportReport();
    return;
  }

  const printExportButton = event.target.closest("[data-export-print]");
  if (printExportButton) {
    printExportReport();
    return;
  }

  const refreshExportButton = event.target.closest("[data-export-refresh]");
  if (refreshExportButton) {
    refreshExportReport();
    return;
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
checkWebAppSession();
loadBackendDirectories();

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
  updateAishaHint();
  showToast(nextTheme === "dark" ? "Тёмная тема включена." : "Светлая тема включена.", "info");

  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.selectionChanged();
  }
}

function activateTab(tabName) {
  const safeTabName = tabName || "home";
  activeTab = safeTabName;
  tabPanels.forEach((panel) => {
    panel.classList.toggle("is-active", panel.id === safeTabName);
  });
  tabButtons.forEach((button) => {
    const isActive = button.dataset.tabTarget === safeTabName;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });
  updateAishaHint();
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
  renderSessionStatus();
  renderSearchResults();
  renderSummary();
  renderAdvice();
  renderFilterControls();
  renderFilteredResults();
  renderFavorites();
  renderComparison();
  renderAdmissionPlan();
  renderExportPreview();
  renderFeedbackStatus();
  renderMyFeedback();
  renderAishaHint();
}

function getAishaHintContext() {
  return {
    activeTab,
    isSearchLoading,
    hasSearch: Boolean(currentSearch),
    hasResults: lastResults.length > 0,
    resultsCount: lastResults.length,
    counts: getFilterCounts(lastResults),
    favoritesCount: favorites.length,
    comparisonCount: comparisonItems.length,
  };
}

function buildAishaHint() {
  const context = getAishaHintContext();

  if (context.isSearchLoading) {
    return {
      title: "Aisha советует",
      text: "Я ищу подходящие варианты. После выдачи лучше сначала посмотреть безопасные и реалистичные варианты.",
      actionLabel: "К результатам",
      actionTab: "search",
      tone: "search",
    };
  }

  if (context.activeTab === "plan") {
    return {
      title: "Aisha советует",
      text: "План помогает не потеряться: сначала запасные варианты, потом реалистичные, затем амбициозные.",
      actionLabel: context.hasResults ? "К экспорту" : "К подбору",
      actionTab: context.hasResults ? "export" : "search",
      tone: "plan",
    };
  }

  if (context.activeTab === "export") {
    return {
      title: "Aisha советует",
      text: context.hasResults
        ? "Когда определишься, сохрани отчёт или распечатай его через системное окно печати."
        : "Сначала выполни подбор, и здесь появится отчёт для копирования или печати.",
      actionLabel: context.hasResults ? "Открыть план" : "К подбору",
      actionTab: context.hasResults ? "plan" : "search",
      tone: "export",
    };
  }

  if (context.activeTab === "feedback") {
    return {
      title: "Aisha советует",
      text: "Если заметил ошибку в данных или Mini App, отправь обращение — я сохраню его с номером заявки.",
      actionLabel: "К форме",
      actionTab: "feedback",
      tone: "support",
    };
  }

  if (context.activeTab === "comparison") {
    if (context.comparisonCount >= 2) {
      return {
        title: "Aisha советует",
        text: "Проверь баллы, стоимость, город и сайт в таблице сравнения.",
        actionLabel: "К плану",
        actionTab: "plan",
        tone: "compare",
      };
    }
    return {
      title: "Aisha советует",
      text: context.comparisonCount === 1
        ? "Для сравнения нужно минимум 2 вуза. Добавь ещё один вариант."
        : "Добавь 2–3 вуза к сравнению, чтобы быстрее увидеть различия между программами.",
      actionLabel: context.hasResults ? "К подбору" : "Начать подбор",
      actionTab: "search",
      tone: "compare",
    };
  }

  if (context.activeTab === "favorites") {
    if (!context.favoritesCount) {
      return {
        title: "Aisha советует",
        text: "Пока избранное пустое. Сохрани 2–3 варианта из результатов, чтобы не потерять их.",
        actionLabel: context.hasResults ? "К результатам" : "К подбору",
        actionTab: "search",
        tone: "favorite",
      };
    }
    return {
      title: "Aisha советует",
      text: "Теперь добавь 2–3 вуза в сравнение: так легче выбрать между программами.",
      actionLabel: "К сравнению",
      actionTab: "comparison",
      tone: "favorite",
    };
  }

  if (!context.hasSearch) {
    return {
      title: "Aisha советует",
      text: "Начни с подбора: выбери регион, баллы, направление и тип обучения.",
      actionLabel: "К подбору",
      actionTab: "search",
      tone: "idle",
    };
  }

  if (!context.hasResults) {
    return {
      title: "Aisha советует",
      text: "По текущим параметрам ничего не найдено. Попробуй соседний регион, платное обучение или более широкое направление.",
      actionLabel: "Изменить поиск",
      actionTab: "search",
      tone: "empty",
    };
  }

  if (!context.favoritesCount) {
    const categoryPart = context.counts.safe || context.counts.realistic
      ? `В выдаче: безопасные — ${context.counts.safe}, реалистичные — ${context.counts.realistic}. `
      : "";
    return {
      title: "Aisha советует",
      text: `${categoryPart}Сохрани 2–3 варианта в избранное, чтобы не потерять их и потом сравнить.`,
      actionLabel: "К результатам",
      actionTab: "search",
      tone: "success",
    };
  }

  if (context.comparisonCount < 2) {
    return {
      title: "Aisha советует",
      text: "У тебя уже есть избранное. Добавь минимум 2 вуза в сравнение, чтобы увидеть различия в таблице.",
      actionLabel: "К сравнению",
      actionTab: "comparison",
      tone: "compare",
    };
  }

  return {
    title: "Aisha советует",
    text: "Проверь таблицу сравнения, план поступления и официальные сайты вузов перед подачей документов.",
    actionLabel: "Открыть план",
    actionTab: "plan",
    tone: "plan",
  };
}

function renderAishaHint() {
  if (!aishaHintNode || !aishaHintTextNode) {
    return;
  }

  if (aishaHintsHidden) {
    aishaHintNode.classList.add("is-hidden");
    aishaHintShowButton?.classList.remove("is-hidden");
    return;
  }

  const hint = buildAishaHint();
  aishaHintNode.classList.remove("is-hidden");
  aishaHintNode.dataset.hintTone = hint.tone || "idle";
  aishaHintTextNode.textContent = hint.text;
  aishaHintShowButton?.classList.add("is-hidden");

  if (aishaHintActionButton && hint.actionLabel && hint.actionTab) {
    aishaHintActionButton.textContent = hint.actionLabel;
    aishaHintActionButton.dataset.actionTab = hint.actionTab;
    aishaHintActionButton.classList.remove("is-hidden");
  } else {
    aishaHintActionButton?.classList.add("is-hidden");
  }
}

function updateAishaHint() {
  renderAishaHint();
}

function hideAishaHints() {
  aishaHintsHidden = true;
  saveAishaHintsHidden(true);
  renderAishaHint();
  showToast("Подсказки скрыты.", "info");
}

function showAishaHints() {
  aishaHintsHidden = false;
  saveAishaHintsHidden(false);
  renderAishaHint();
  showToast("Подсказки снова включены.", "info");
}

function loadAishaHintsHidden() {
  try {
    return window.localStorage.getItem(HINTS_HIDDEN_KEY) === "true";
  } catch (error) {
    return false;
  }
}

function saveAishaHintsHidden(value) {
  try {
    if (value) {
      window.localStorage.setItem(HINTS_HIDDEN_KEY, "true");
    } else {
      window.localStorage.removeItem(HINTS_HIDDEN_KEY);
    }
  } catch (error) {
    // The current in-memory setting is enough when localStorage is unavailable.
  }
}

function getTelegramInitData() {
  return telegramWebApp?.initData || "";
}

function hasTelegramInitData() {
  return Boolean(telegramInitData);
}

function isTelegramSessionVerified() {
  return sessionState.mode === "telegram" && sessionState.authenticated === true;
}

async function checkWebAppSession() {
  sessionState = {
    status: "checking",
    mode: hasTelegramInitData() ? "telegram" : "local",
    authenticated: false,
    user: null,
    message: hasTelegramInitData()
      ? "Проверяю Telegram-сессию."
      : "Проверяю локальный режим Mini App.",
  };
  renderSessionStatus();

  try {
    const response = await fetch("/api/webapp/session", {
      headers: hasTelegramInitData() ? { "X-Telegram-Init-Data": telegramInitData } : {},
    });
    const payload = await response.json().catch(() => ({}));

    if (response.ok && payload.mode === "telegram" && payload.authenticated) {
      sessionState = {
        status: "telegram_verified",
        mode: "telegram",
        authenticated: true,
        user: payload.user || null,
        message: "Mini App открыт через Telegram. Сессия проверена, избранное может синхронизироваться с ботом.",
      };
      renderSessionStatus();
      await initFavoritesSync();
      await loadMyFeedback();
      return;
    }

    if (response.ok && payload.mode === "local") {
      sessionState = {
        status: "local",
        mode: "local",
        authenticated: false,
        user: null,
        message: "Локальный режим. Mini App открыт не через Telegram, поэтому избранное хранится только в этом браузере.",
      };
      favoritesSyncNotice = "Локальный режим: избранное хранится только в этом браузере.";
      feedbackTickets = latestLocalFeedbackTicket ? [latestLocalFeedbackTicket] : [];
      renderAll();
      return;
    }

    sessionState = {
      status: payload.error === "bot_token_not_configured" ? "service_unavailable" : "invalid",
      mode: "telegram",
      authenticated: false,
      user: null,
      message: payload.error === "bot_token_not_configured"
        ? "Проверка Telegram-сессии сейчас недоступна. Избранное сохранится локально."
        : "Telegram-сессия не прошла проверку. Синхронизация отключена, избранное сохранится локально.",
    };
    favoritesSyncNotice = "Синхронизация отключена, избранное сохранится локально.";
    feedbackTickets = [];
    renderAll();
  } catch (error) {
    sessionState = {
      status: "service_unavailable",
      mode: hasTelegramInitData() ? "telegram" : "local",
      authenticated: false,
      user: null,
      message: "Сервис сейчас недоступен. Mini App работает в локальном режиме.",
    };
    favoritesSyncNotice = "Сервис сейчас недоступен. Избранное сохранится локально.";
    feedbackTickets = latestLocalFeedbackTicket ? [latestLocalFeedbackTicket] : [];
    renderAll();
  }
}

function renderSessionStatus() {
  const meta = getSessionMeta(sessionState.status);

  if (sessionBadgeNode) {
    sessionBadgeNode.textContent = meta.badge;
    sessionBadgeNode.className = `session-badge session-badge--${meta.className}`;
  }

  if (sessionCardNode) {
    sessionCardNode.className = `session-card session-card--${meta.className}`;
  }

  if (sessionDescriptionNode) {
    sessionDescriptionNode.textContent = sessionState.message;
  }

  if (sessionUserNode) {
    sessionUserNode.textContent = formatSessionUser(sessionState.user);
  }
}

function getSessionMeta(status) {
  const statuses = {
    checking: { className: "checking", badge: "Проверка…" },
    telegram_verified: { className: "success", badge: "Telegram ✓" },
    local: { className: "local", badge: "Локальный режим" },
    invalid: { className: "error", badge: "Сессия не проверена" },
    service_unavailable: { className: "warning", badge: "Сервис недоступен" },
  };
  return statuses[status] || statuses.checking;
}

function formatSessionUser(user) {
  if (!user || typeof user !== "object") {
    return "";
  }

  const name = [user.first_name, user.last_name].filter(Boolean).join(" ").trim();
  if (name) {
    return `Пользователь Telegram: ${name}`;
  }
  if (user.username) {
    return `Пользователь Telegram: @${user.username}`;
  }
  return "Пользователь Telegram подтверждён.";
}

function renderFeedbackStatus() {
  if (!feedbackStatusNode) {
    return;
  }

  if (sessionState.status === "checking") {
    feedbackStatusNode.textContent = "Проверяю режим Mini App.";
    feedbackStatusNode.className = "feedback-status-card";
    return;
  }

  if (isTelegramSessionVerified()) {
    feedbackStatusNode.textContent = "Telegram-сессия проверена: обращение сохранится с привязкой к боту.";
    feedbackStatusNode.className = "feedback-status-card feedback-status-card--success";
    return;
  }

  if (hasTelegramInitData() && !isTelegramSessionVerified()) {
    feedbackStatusNode.textContent = "Telegram-сессия не прошла проверку. Обращение можно отправить только после повторного открытия Mini App через Telegram.";
    feedbackStatusNode.className = "feedback-status-card feedback-status-card--warning";
    return;
  }

  feedbackStatusNode.textContent = "Локальный режим: обращение сохранится без привязки к Telegram.";
  feedbackStatusNode.className = "feedback-status-card feedback-status-card--local";
}

async function submitFeedback() {
  const category = String(feedbackCategoryNode?.value || "other").trim();
  const message = String(feedbackMessageNode?.value || "").trim();
  const validationError = validateFeedbackForm(category, message);
  if (validationError) {
    setFeedbackResult(validationError, true);
    showToast(validationError, "warning");
    return;
  }

  if (hasTelegramInitData() && !isTelegramSessionVerified()) {
    const text = "Telegram-сессия не прошла проверку. Открой Mini App через /webapp и попробуй снова.";
    setFeedbackResult(text, true);
    showToast("Сессия Telegram не проверена.", "error");
    return;
  }

  try {
    const payload = await requestFeedbackApi("/api/feedback", {
      category,
      message,
      context: buildFeedbackContext(),
    });
    const ticket = payload.ticket || {};
    latestLocalFeedbackTicket = payload.mode === "local" ? ticket : latestLocalFeedbackTicket;
    setFeedbackResult(`Заявка ${ticket.ticket_id || ""} создана. Спасибо за обратную связь.`);
    if (feedbackMessageNode) {
      feedbackMessageNode.value = "";
    }
    showToast("Заявка создана.", "success");

    if (isTelegramSessionVerified()) {
      await loadMyFeedback();
    } else {
      feedbackTickets = ticket.ticket_id ? [ticket] : [];
      renderMyFeedback();
    }
  } catch (error) {
    const text = feedbackErrorMessage(error);
    setFeedbackResult(text, true);
    showToast(text, "error");
  }
}

async function loadMyFeedback() {
  if (!feedbackHistoryStatusNode || !feedbackListNode) {
    return;
  }

  if (hasTelegramInitData() && !isTelegramSessionVerified()) {
    feedbackTickets = [];
    renderMyFeedback();
    return;
  }

  try {
    const payload = await requestFeedbackApi("/api/feedback/my", null);
    feedbackTickets = Array.isArray(payload.tickets) ? payload.tickets : [];
    renderMyFeedback();
    if (payload.mode === "telegram") {
      showToast("Обращения обновлены.", "info");
    }
  } catch (error) {
    if (!hasTelegramInitData()) {
      feedbackTickets = latestLocalFeedbackTicket ? [latestLocalFeedbackTicket] : [];
      renderMyFeedback();
      return;
    }
    feedbackHistoryStatusNode.textContent = "Не удалось обновить обращения. Проверь подключение или открой Mini App через Telegram.";
    showToast("Не удалось обновить обращения.", "warning");
  }
}

function renderMyFeedback() {
  if (!feedbackHistoryStatusNode || !feedbackListNode) {
    return;
  }

  if (!feedbackTickets.length) {
    feedbackHistoryStatusNode.textContent = isTelegramSessionVerified()
      ? "Пока обращений нет."
      : "Пока обращений нет. В локальном режиме показывается только последняя заявка текущей страницы.";
    feedbackListNode.innerHTML = "";
    return;
  }

  feedbackHistoryStatusNode.textContent = `Показано обращений: ${feedbackTickets.length}.`;
  feedbackListNode.innerHTML = feedbackTickets.map((ticket) => `
    <article class="feedback-ticket">
      <div>
        <strong>${escapeHtml(textValue(ticket.ticket_id, "Заявка"))}</strong>
        <span>${escapeHtml(textValue(ticket.category_label, "Другое"))}</span>
      </div>
      <p>${escapeHtml(textValue(ticket.message, "Сообщение сохранено"))}</p>
      <small>Статус: ${escapeHtml(textValue(ticket.status, "new"))} · ${escapeHtml(textValue(ticket.created_at, "дата не указана"))}</small>
    </article>
  `).join("");
}

function validateFeedbackForm(category, message) {
  if (!feedbackCategoryLabels[category]) {
    return "Выбери тип обращения.";
  }
  if (!message) {
    return "Напиши обращение чуть подробнее.";
  }
  if (message.length < 5) {
    return "Опиши проблему чуть подробнее.";
  }
  if (message.length > 1000) {
    return "Сообщение слишком длинное. Сократи его до 1000 символов.";
  }
  return "";
}

function resetFeedbackForm() {
  if (feedbackForm) {
    feedbackForm.reset();
  }
  setFeedbackResult("Форма обращения очищена.");
  showToast("Форма обращения очищена.", "info");
}

function setFeedbackResult(text, isError = false) {
  if (!feedbackResultNode) {
    return;
  }
  feedbackResultNode.textContent = text;
  feedbackResultNode.className = `panel-status ${isError ? "feedback-error" : "feedback-success"}`;
}

async function requestFeedbackApi(path, body = null) {
  const options = {
    method: body ? "POST" : "GET",
    headers: {},
  };
  if (isTelegramSessionVerified()) {
    options.headers["X-Telegram-Init-Data"] = telegramInitData;
  }
  if (body) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  const response = await fetch(path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.status === "error") {
    throw new Error(payload.error || `Feedback API returned ${response.status}`);
  }
  return payload;
}

function buildFeedbackContext() {
  return {
    last_search: currentSearch
      ? {
          region: currentSearch.region,
          score: currentSearch.score,
          direction: currentSearch.direction,
          type: currentSearch.type,
          results_count: lastResults.length,
        }
      : null,
    active_tab: document.querySelector(".tab-button.is-active")?.dataset.tabTarget || "unknown",
    session_mode: sessionState.mode,
    theme: document.documentElement.dataset.theme || "light",
  };
}

function feedbackErrorMessage(error) {
  const message = String(error?.message || "");
  if (message.includes("message_too_short")) {
    return "Опиши проблему чуть подробнее.";
  }
  if (message.includes("message_too_long")) {
    return "Сообщение слишком длинное. Сократи его до 1000 символов.";
  }
  if (message.includes("invalid_category")) {
    return "Выбери тип обращения.";
  }
  if (message.includes("invalid_init_data")) {
    return "Telegram-сессия не прошла проверку. Открой Mini App через /webapp и попробуй снова.";
  }
  return "Не удалось отправить обращение. Проверь подключение или попробуй позже.";
}

function renderSearchResults() {
  if (!lastResults.length) {
    resultsNode.innerHTML = "";
    resultsActionsNode?.classList.add("is-hidden");
    return;
  }
  resultsActionsNode?.classList.remove("is-hidden");
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
  showToast(`Фильтр: ${filterLabels[activeFilter]}`, "info");
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
    filterStatusNode.textContent = "В этом фильтре вариантов нет. Попробуй выбрать другой фильтр или вернуться ко всем результатам.";
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
  const subjects = formatSubjects(item.subjects);
  const admissionType = shouldShowAdmissionType(item) ? formatAdmissionType(item.admission_type) : "";
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
        ${subjects ? `<div><b>Предметы:</b> ${escapeHtml(subjects)}</div>` : ""}
        <div><b>Мин. балл:</b> ${escapeHtml(formatValue(minScore))}</div>
        <div><b>Твои баллы:</b> ${score}</div>
        <div><b>${delta === null ? "Запас" : delta >= 0 ? "Запас" : "Не хватает"}:</b> ${escapeHtml(formatDelta(delta))}</div>
        <div><b>Тип:</b> ${escapeHtml(textValue(item.type, "не указан"))}</div>
        ${admissionType ? `<div><b>Конкурс:</b> ${escapeHtml(admissionType)}</div>` : ""}
        ${hasValue(item.price) ? `<div><b>Стоимость:</b> ${escapeHtml(formatPrice(item.price))}</div>` : ""}
        ${hasValue(item.study_form) ? `<div><b>Форма:</b> ${escapeHtml(item.study_form)}</div>` : ""}
        ${hasValue(item.duration) ? `<div><b>Срок:</b> ${escapeHtml(item.duration)}</div>` : ""}
        ${hasValue(item.faculty) ? `<div><b>Факультет:</b> ${escapeHtml(item.faculty)}</div>` : ""}
        ${hasValue(item.year) ? `<div><b>Год данных:</b> ${escapeHtml(item.year)}</div>` : ""}
        ${hasValue(item.url) ? `<div><b>Сайт:</b> <a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a></div>` : ""}
        ${hasValue(item.note) ? `<div><b>Пометка:</b> ${escapeHtml(item.note)}</div>` : ""}
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
    favoritesStatusNode.textContent = "Пока здесь пусто. Добавь вуз из результатов, чтобы быстро вернуться к нему позже.";
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
    showToast("Не удалось сохранить избранное в браузере.", "warning");
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
    showToast("Избранное синхронизировано с Telegram.", "success");
    renderAll();
  } catch (error) {
    favoritesSyncNotice = "Сейчас избранное сохранено локально. Синхронизация будет доступна при открытии через Telegram.";
    showToast("Избранное сохранено локально.", "warning");
    renderFavoritesSyncStatus();
  }
}

function hasTelegramAuth() {
  return isTelegramSessionVerified();
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
  if (isFavorite(item)) {
    showToast("Уже в избранном.", "info");
  } else {
    favorites = [
      ...favorites,
      {
        ...item,
        saved_score: currentSearch?.score || item.saved_score || getMinScore(item) || 0,
      },
    ];
    saveFavorites();
    showToast("Добавлено в избранное.", "success");
  }
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/add", { item });
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное синхронизировано с Telegram.";
      showToast("Избранное синхронизировано с Telegram.", "success");
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать с Telegram. Избранное сохранено локально.";
      showToast("Не удалось синхронизировать с Telegram. Сохранено локально.", "warning");
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
  showToast("Удалено из избранного.", "info");
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/remove", { key });
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное синхронизировано с Telegram.";
      showToast("Избранное синхронизировано с Telegram.", "success");
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать удаление. Локальная копия обновлена.";
      showToast("Удаление сохранено локально.", "warning");
      renderFavoritesSyncStatus();
    }
  }
}

async function clearFavorites() {
  favorites = [];
  saveFavorites();
  showToast("Избранное очищено.", "info");
  renderAll();

  if (hasTelegramAuth()) {
    try {
      const payload = await requestFavoritesApi("/api/favorites/clear", {});
      updateFavoritesFromServer(payload.favorites);
      favoritesSyncNotice = "Избранное очищено и синхронизировано с Telegram.";
      showToast("Избранное очищено и синхронизировано.", "success");
      renderAll();
    } catch (error) {
      favoritesSyncNotice = "Не удалось синхронизировать очистку. Локальная копия очищена.";
      showToast("Очистка сохранена локально.", "warning");
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
    comparisonStatusNode.textContent = comparisonNotice || "Добавь 2–3 вуза к сравнению, чтобы увидеть таблицу различий.";
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

function renderAdmissionPlan() {
  if (!planContentNode) {
    return;
  }

  if (!currentSearch) {
    planCopyFallbackNode?.classList.add("is-hidden");
    planContentNode.innerHTML = `
      <article class="plan-empty empty-state">
        <h3>Пока нет плана поступления</h3>
        <p>Сначала выполни подбор вузов, а я соберу персональные шаги.</p>
        <button class="primary-button" type="button" data-tab-target="search">Перейти к подбору</button>
      </article>
    `;
    return;
  }

  const plan = buildAdmissionPlan();
  planCopyFallbackNode?.classList.add("is-hidden");
  planContentNode.innerHTML = `
    <article class="plan-hero">
      <div>
        <p class="eyebrow">Персональный маршрут</p>
        <h3>Твой план поступления</h3>
        <p>${escapeHtml(plan.overview)}</p>
      </div>
      <div class="plan-progress">
        <span>Готовность плана</span>
        <strong>${plan.completedSteps}/${plan.checklist.length}</strong>
      </div>
    </article>

    <div class="plan-grid">
      <article class="plan-card">
        <span class="plan-badge plan-badge--next">Краткий итог</span>
        <div class="plan-summary">
          <div><b>Регион:</b> ${escapeHtml(currentSearch.region)}</div>
          <div><b>Направление:</b> ${escapeHtml(currentSearch.direction)}</div>
          <div><b>Тип:</b> ${escapeHtml(currentSearch.typeLabel)}</div>
          <div><b>Баллы:</b> ${currentSearch.score}</div>
          <div><b>Найдено:</b> ${lastResults.length}</div>
          <div><b>Избранное:</b> ${favorites.length}</div>
        </div>
      </article>

      <article class="plan-card">
        <span class="plan-badge plan-badge--important">Что сделать сначала</span>
        ${renderPlanList(plan.firstSteps)}
      </article>

      <article class="plan-card plan-card--wide">
        <span class="plan-badge plan-badge--next">Чеклист</span>
        <div class="plan-checklist">
          ${plan.checklist.map((item) => renderChecklistItem(item)).join("")}
        </div>
      </article>
    </div>

    <div class="plan-category-grid">
      ${renderPlanCategoryBlock("Безопасные варианты", "safe", plan.safeItems, plan.categoryMessages.safe)}
      ${renderPlanCategoryBlock("Реалистичные варианты", "realistic", plan.realisticItems, plan.categoryMessages.realistic)}
      ${renderPlanCategoryBlock("Амбициозные варианты", "ambitious", plan.ambitiousItems, plan.categoryMessages.ambitious)}
    </div>

    <article class="plan-card">
      <span class="plan-badge plan-badge--important">Что проверить перед подачей</span>
      ${renderPlanList(plan.checkBeforeSubmit)}
    </article>

    <article class="plan-card">
      <span class="plan-badge plan-badge--next">Следующие действия</span>
      ${renderPlanList(plan.nextActions)}
      <p class="plan-note">Это не гарантия поступления, а помощник для планирования. Проверь официальные сайты вузов перед подачей документов.</p>
    </article>

    <div class="plan-actions">
      <button class="secondary-button" type="button" data-tab-target="search">Открыть подбор</button>
      <button class="secondary-button" type="button" data-tab-target="filters">Открыть фильтры</button>
      <button class="secondary-button" type="button" data-tab-target="favorites">Открыть избранное</button>
      <button class="secondary-button" type="button" data-tab-target="comparison">Открыть сравнение</button>
      <button class="secondary-button" type="button" data-tab-target="export">Экспортировать план</button>
      <button class="secondary-button" type="button" data-plan-copy>Скопировать план</button>
      <button class="secondary-button" type="button" data-plan-refresh>Обновить план</button>
    </div>
  `;
}

function buildAdmissionPlan() {
  const counts = getFilterCounts(lastResults);
  const safeItems = lastResults.filter((item) => getItemCategory(item) === "safe");
  const realisticItems = lastResults.filter((item) => getItemCategory(item) === "realistic");
  const ambitiousItems = lastResults.filter((item) => getItemCategory(item) === "ambitious");
  const checklist = [
    { label: "Подбор выполнен", done: lastResults.length > 0 },
    { label: "Сохранены избранные варианты", done: favorites.length > 0 },
    { label: "Добавлены вузы к сравнению", done: comparisonItems.length >= 2 },
    { label: "Проверены официальные сайты", done: false },
    { label: "Подготовлен итоговый список", done: false },
  ];

  const firstSteps = [];
  if (!lastResults.length) {
    firstSteps.push("Измени параметры поиска: регион, направление, тип обучения или баллы.");
  } else if (safeItems.length >= 2) {
    firstSteps.push("Начни с безопасных вариантов: они дают самый спокойный запасной список.");
  } else if (safeItems.length === 0 && realisticItems.length > 0) {
    firstSteps.push("Сохрани 2–3 реалистичных варианта и проверь проходные баллы на сайтах вузов.");
  } else {
    firstSteps.push("Выбери 2–3 наиболее понятных варианта и сравни их по программе, баллам и стоимости.");
  }

  if (ambitiousItems.length) {
    firstSteps.push("Амбициозные варианты оставь как цель, но не делай их единственной стратегией.");
  }
  if (!favorites.length) {
    firstSteps.push("Сохрани 2–3 вуза в избранное, чтобы не потерять их.");
  } else {
    firstSteps.push("У тебя уже есть избранные вузы. Следующий шаг — сравнить их по баллам, стоимости и программе.");
  }
  if (comparisonItems.length < 2) {
    firstSteps.push("Добавь минимум 2 вуза в сравнение, чтобы увидеть различия в таблице.");
  } else {
    firstSteps.push("Ты уже начал сравнение. Проверь таблицу и выбери наиболее подходящие варианты.");
  }

  const nextActions = [
    "Открой фильтры и посмотри безопасные, реалистичные и амбициозные варианты отдельно.",
    "Добавь основные варианты в избранное.",
    "Сравни 2–3 вуза в таблице.",
    "Перейди на сайты вузов и проверь актуальные условия.",
  ];

  const checkBeforeSubmit = [
    "Актуальные проходные баллы и сроки приёма.",
    "Стоимость, если рассматриваешь платное обучение.",
    "Предметы, форма обучения и длительность программы.",
    "Официальные страницы выбранных вузов.",
  ];

  return {
    counts,
    safeItems,
    realisticItems,
    ambitiousItems,
    checklist,
    completedSteps: checklist.filter((item) => item.done).length,
    overview: buildAdmissionOverview(counts),
    firstSteps,
    nextActions,
    checkBeforeSubmit,
    categoryMessages: {
      safe: safeItems.length
        ? "У тебя есть варианты с запасом. Начни с них как со спокойного списка."
        : "Безопасных вариантов пока нет. Попробуй расширить регион или тип обучения.",
      realistic: realisticItems.length
        ? "Эти варианты близки к твоим баллам. Их стоит сохранить и проверить на сайтах вузов."
        : "Реалистичных вариантов сейчас нет. Проверь соседние параметры поиска.",
      ambitious: ambitiousItems.length
        ? "Эти варианты можно оставить как цель, но лучше дополнить их более спокойными."
        : "Амбициозных вариантов нет. Текущий список выглядит более спокойным.",
    },
  };
}

function buildAdmissionOverview(counts) {
  if (!lastResults.length) {
    return "По текущим параметрам варианты не найдены. Попробуй соседний регион, другой тип обучения или более широкое направление.";
  }
  if (counts.safe >= 2) {
    return `Подбор выглядит спокойным: найдено ${counts.safe} безопасных вариантов из ${lastResults.length}.`;
  }
  if (counts.safe === 0 && counts.realistic > 0) {
    return "Безопасных вариантов пока нет, но есть реалистичные. Стоит добавить запасные варианты.";
  }
  if (counts.ambitious > 0 && counts.safe + counts.realistic === 0) {
    return "Сейчас подбор в основном амбициозный. Добавь более спокойные варианты.";
  }
  return `Найдено ${lastResults.length} вариантов. Используй избранное и сравнение, чтобы сузить список.`;
}

function renderPlanList(items) {
  return `
    <ul class="plan-list">
      ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;
}

function renderChecklistItem(item) {
  return `
    <div class="plan-checkitem ${item.done ? "is-done" : ""}">
      <span>${item.done ? "✓" : "•"}</span>
      <strong>${escapeHtml(item.label)}</strong>
    </div>
  `;
}

function renderPlanCategoryBlock(title, category, items, message) {
  const meta = categoryMeta[category];
  const topItems = items.slice(0, 3);
  return `
    <article class="plan-card">
      <span class="plan-badge plan-badge--${meta.className}">${escapeHtml(title)}</span>
      <p>${escapeHtml(message)}</p>
      ${
        topItems.length
          ? `<ol class="plan-program-list">${topItems.map((item) => `
              <li>
                <b>${escapeHtml(textValue(item.university, "Вуз"))}</b>
                <span>${escapeHtml(textValue(item.program, "программа не указана"))}</span>
              </li>
            `).join("")}</ol>`
          : `<p class="plan-muted">В этой категории пока нет вариантов.</p>`
      }
    </article>
  `;
}

async function copyAdmissionPlan() {
  if (!currentSearch) {
    showToast("Сначала выполни подбор.", "warning");
    return;
  }

  const text = buildAdmissionPlanText(buildAdmissionPlan());
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error("Clipboard is unavailable");
    }
    await navigator.clipboard.writeText(text);
    planCopyFallbackNode?.classList.add("is-hidden");
    showToast("План скопирован.", "success");
  } catch (error) {
    if (planCopyFallbackNode) {
      planCopyFallbackNode.value = text;
      planCopyFallbackNode.classList.remove("is-hidden");
      planCopyFallbackNode.focus();
      planCopyFallbackNode.select();
    }
    showToast("Не удалось скопировать автоматически. Скопируй текст вручную.", "warning");
  }
}

function buildAdmissionPlanText(plan) {
  const lines = [
    "Аиша — персональный план поступления",
    "",
    "Краткий итог:",
    `Регион: ${currentSearch.region}`,
    `Направление: ${currentSearch.direction}`,
    `Тип обучения: ${currentSearch.typeLabel}`,
    `Баллы: ${currentSearch.score}`,
    `Найдено вариантов: ${lastResults.length}`,
    `Безопасные: ${plan.counts.safe}`,
    `Реалистичные: ${plan.counts.realistic}`,
    `Амбициозные: ${plan.counts.ambitious}`,
    `Избранное: ${favorites.length}`,
    `В сравнении: ${comparisonItems.length}`,
    "",
    "Что сделать сначала:",
    ...plan.firstSteps.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Что проверить перед подачей:",
    ...plan.checkBeforeSubmit.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Следующие действия:",
    ...plan.nextActions.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Важно: это не гарантия поступления, а помощник для планирования. Проверь официальные сайты вузов перед подачей документов.",
  ];
  return lines.join("\n");
}

function renderExportPreview() {
  if (!exportContentNode) {
    return;
  }

  exportCopyFallbackNode?.classList.add("is-hidden");

  if (!currentSearch) {
    exportContentNode.innerHTML = `
      <article class="export-empty empty-state">
        <h3>Пока нечего экспортировать</h3>
        <p>Сначала выполни подбор вузов, а затем здесь появится отчёт.</p>
        <button class="primary-button" type="button" data-tab-target="search">Перейти к подбору</button>
      </article>
    `;
    return;
  }

  const reportData = buildExportReportData();
  exportContentNode.innerHTML = `
    <article id="export-report-print" class="export-report">
      <header class="export-report__header">
        <div>
          <p class="eyebrow">Отчёт</p>
          <h3>Аиша — отчёт по подбору вузов</h3>
        </div>
        <span>Сформировано: ${escapeHtml(reportData.generatedAtText)}</span>
      </header>

      <section class="export-section-block">
        <h4>Параметры подбора</h4>
        <div class="export-grid">
          <div><b>Регион:</b> ${escapeHtml(reportData.search.region)}</div>
          <div><b>Баллы:</b> ${escapeHtml(formatValue(reportData.search.score))}</div>
          <div><b>Направление:</b> ${escapeHtml(reportData.search.direction)}</div>
          <div><b>Тип обучения:</b> ${escapeHtml(reportData.search.typeLabel)}</div>
        </div>
      </section>

      <section class="export-section-block">
        <h4>Краткий итог</h4>
        ${renderExportSummaryGrid(reportData)}
      </section>

      ${renderExportItems("Найденные варианты", reportData.topResults, "По текущему подбору варианты не найдены.", 5)}
      ${renderExportItems("Избранные вузы", reportData.favorites, "Избранные варианты пока не добавлены.")}
      ${renderExportItems("Сравнение", reportData.comparisonItems, "Вузы для сравнения пока не выбраны.")}
      ${renderExportPlan(reportData)}

      <section class="export-section-block export-disclaimer">
        <h4>Важно</h4>
        <p>Данные используются для предварительного подбора. Проходные баллы и условия поступления нужно проверять на официальных сайтах вузов.</p>
      </section>
    </article>
  `;
}

function buildExportReportData() {
  if (!currentSearch) {
    return null;
  }

  return {
    generatedAt: new Date(),
    generatedAtText: formatExportDate(new Date()),
    search: currentSearch,
    counts: getFilterCounts(lastResults),
    totalResults: lastResults.length,
    topResults: lastResults.slice(0, 5),
    favorites: Array.isArray(favorites) ? [...favorites] : [],
    comparisonItems: Array.isArray(comparisonItems) ? [...comparisonItems] : [],
    plan: buildAdmissionPlan(),
  };
}

function renderExportSummaryGrid(reportData) {
  return `
    <div class="export-grid export-grid--summary">
      <div><b>Найдено вариантов:</b> ${reportData.totalResults}</div>
      <div><b>Безопасные:</b> ${reportData.counts.safe}</div>
      <div><b>Реалистичные:</b> ${reportData.counts.realistic}</div>
      <div><b>Амбициозные:</b> ${reportData.counts.ambitious}</div>
      <div><b>Избранные:</b> ${reportData.favorites.length}</div>
      <div><b>В сравнении:</b> ${reportData.comparisonItems.length}</div>
    </div>
  `;
}

function renderExportItems(title, items, emptyText, limit = null) {
  const visibleItems = Array.isArray(items)
    ? items.slice(0, Number.isFinite(limit) ? limit : items.length)
    : [];
  const hiddenCount = Array.isArray(items) ? Math.max(0, items.length - visibleItems.length) : 0;

  return `
    <section class="export-section-block">
      <h4>${escapeHtml(title)}</h4>
      ${
        visibleItems.length
          ? `<div class="export-item-list">
              ${visibleItems.map((item, index) => renderExportItem(item, index + 1)).join("")}
            </div>
            ${hiddenCount ? `<p class="export-muted">Ещё вариантов: ${hiddenCount}.</p>` : ""}`
          : `<p class="export-muted">${escapeHtml(emptyText)}</p>`
      }
    </section>
  `;
}

function renderExportItem(item, index) {
  const category = getItemCategory(item);
  const meta = categoryMeta[category] || categoryMeta.ambitious;
  const subjects = formatSubjects(item.subjects);
  const admissionType = shouldShowAdmissionType(item) ? formatAdmissionType(item.admission_type) : "";
  const margin = getScoreMargin(item);

  return `
    <article class="export-item">
      <div class="export-item__title">
        <strong>${index}. ${escapeHtml(textValue(item.university, "Вуз"))} — ${escapeHtml(textValue(item.program, "программа не указана"))}</strong>
        <span class="badge ${meta.className}">${escapeHtml(meta.shortLabel)}</span>
      </div>
      <div class="export-item__meta">
        <span><b>Город:</b> ${escapeHtml(textValue(item.city, "не указано"))}</span>
        <span><b>Мин. балл:</b> ${escapeHtml(formatValue(getMinScore(item)))}</span>
        <span><b>Твои баллы:</b> ${escapeHtml(formatValue(getUserScore(item) || currentSearch?.score))}</span>
        <span><b>Запас/не хватает:</b> ${escapeHtml(formatDelta(margin))}</span>
        <span><b>Тип:</b> ${escapeHtml(textValue(item.type, "не указано"))}</span>
        ${admissionType ? `<span><b>Конкурс:</b> ${escapeHtml(admissionType)}</span>` : ""}
        ${hasValue(item.price) ? `<span><b>Стоимость:</b> ${escapeHtml(formatPrice(item.price))}</span>` : ""}
        ${subjects ? `<span><b>Предметы:</b> ${escapeHtml(subjects)}</span>` : ""}
        ${hasValue(item.study_form) ? `<span><b>Форма:</b> ${escapeHtml(item.study_form)}</span>` : ""}
        ${hasValue(item.duration) ? `<span><b>Срок:</b> ${escapeHtml(item.duration)}</span>` : ""}
        ${hasValue(item.faculty) ? `<span><b>Факультет:</b> ${escapeHtml(item.faculty)}</span>` : ""}
        ${hasValue(item.year) ? `<span><b>Год данных:</b> ${escapeHtml(item.year)}</span>` : ""}
        ${hasValue(item.url) ? `<span><b>Сайт:</b> <a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.url)}</a></span>` : ""}
      </div>
    </article>
  `;
}

function renderExportPlan(reportData) {
  const plan = reportData.plan;
  if (!plan) {
    return `
      <section class="export-section-block">
        <h4>План поступления</h4>
        <p class="export-muted">План появится после подбора.</p>
      </section>
    `;
  }

  return `
    <section class="export-section-block">
      <h4>План поступления</h4>
      <p>${escapeHtml(plan.overview)}</p>
      <p><b>Готовность:</b> ${plan.completedSteps}/${plan.checklist.length}</p>
      <div class="export-plan-columns">
        <div>
          <b>Что сделать сначала</b>
          ${renderPlanList(plan.firstSteps.slice(0, 4))}
        </div>
        <div>
          <b>Что проверить</b>
          ${renderPlanList(plan.checkBeforeSubmit)}
        </div>
      </div>
    </section>
  `;
}

function buildExportPlainText(reportData = buildExportReportData()) {
  if (!reportData) {
    return "Пока нечего экспортировать. Сначала выполни подбор вузов.";
  }

  const lines = [
    "Аиша — отчёт по подбору вузов",
    "",
    `Сформировано: ${reportData.generatedAtText}`,
    "",
    "Параметры подбора:",
    `Регион: ${reportData.search.region}`,
    `Баллы: ${reportData.search.score}`,
    `Направление: ${reportData.search.direction}`,
    `Тип обучения: ${reportData.search.typeLabel}`,
    "",
    "Краткий итог:",
    `Найдено вариантов: ${reportData.totalResults}`,
    `Безопасные: ${reportData.counts.safe}`,
    `Реалистичные: ${reportData.counts.realistic}`,
    `Амбициозные: ${reportData.counts.ambitious}`,
    `Избранные: ${reportData.favorites.length}`,
    `В сравнении: ${reportData.comparisonItems.length}`,
    "",
    "Найденные варианты:",
    ...formatExportItemsForText(reportData.topResults, "По текущему подбору варианты не найдены."),
    "",
    "Избранные вузы:",
    ...formatExportItemsForText(reportData.favorites, "Избранные варианты пока не добавлены."),
    "",
    "Сравнение:",
    ...formatExportItemsForText(reportData.comparisonItems, "Вузы для сравнения пока не выбраны."),
    "",
    "План поступления:",
    ...formatExportPlanForText(reportData.plan),
    "",
    "Важно: данные используются для предварительного подбора. Проходные баллы и условия поступления нужно проверять на официальных сайтах вузов.",
  ];

  return lines.join("\n");
}

function formatExportItemsForText(items, emptyText) {
  if (!Array.isArray(items) || !items.length) {
    return [emptyText];
  }

  return items.map((item, index) => {
    const subjects = formatSubjects(item.subjects);
    const admissionType = shouldShowAdmissionType(item) ? formatAdmissionType(item.admission_type) : "";
    const parts = [
      `${index + 1}. ${textValue(item.university, "Вуз")} — ${textValue(item.program, "программа не указана")}`,
      `Город: ${textValue(item.city, "не указано")}`,
      `Категория: ${getCategoryLabel(item)}`,
      `Мин. балл: ${formatValue(getMinScore(item))}`,
      `Твои баллы: ${formatValue(getUserScore(item) || currentSearch?.score)}`,
      `Запас/не хватает: ${formatDelta(getScoreMargin(item))}`,
      `Тип: ${textValue(item.type, "не указано")}`,
    ];
    if (admissionType) {
      parts.push(`Конкурс: ${admissionType}`);
    }
    if (hasValue(item.price)) {
      parts.push(`Стоимость: ${formatPrice(item.price)}`);
    }
    if (subjects) {
      parts.push(`Предметы: ${subjects}`);
    }
    if (hasValue(item.study_form)) {
      parts.push(`Форма: ${item.study_form}`);
    }
    if (hasValue(item.duration)) {
      parts.push(`Срок: ${item.duration}`);
    }
    if (hasValue(item.faculty)) {
      parts.push(`Факультет: ${item.faculty}`);
    }
    if (hasValue(item.year)) {
      parts.push(`Год данных: ${item.year}`);
    }
    if (hasValue(item.url)) {
      parts.push(`Сайт: ${item.url}`);
    }
    return parts.join("\n");
  });
}

function formatExportPlanForText(plan) {
  if (!plan) {
    return ["План появится после подбора."];
  }

  return [
    plan.overview,
    `Готовность: ${plan.completedSteps}/${plan.checklist.length}`,
    "",
    "Что сделать сначала:",
    ...plan.firstSteps.map((item, index) => `${index + 1}. ${item}`),
    "",
    "Что проверить перед подачей:",
    ...plan.checkBeforeSubmit.map((item, index) => `${index + 1}. ${item}`),
  ];
}

async function copyExportReport() {
  const reportData = buildExportReportData();
  if (!reportData) {
    showToast("Сначала выполни подбор.", "warning");
    return;
  }

  const text = buildExportPlainText(reportData);
  try {
    if (!navigator.clipboard?.writeText) {
      throw new Error("Clipboard is unavailable");
    }
    await navigator.clipboard.writeText(text);
    exportCopyFallbackNode?.classList.add("is-hidden");
    showToast("Отчёт скопирован.", "success");
  } catch (error) {
    if (exportCopyFallbackNode) {
      exportCopyFallbackNode.value = text;
      exportCopyFallbackNode.classList.remove("is-hidden");
      exportCopyFallbackNode.focus();
      exportCopyFallbackNode.select();
    }
    showToast("Не удалось скопировать автоматически. Скопируй текст вручную.", "warning");
  }
}

function printExportReport() {
  if (!currentSearch) {
    showToast("Сначала выполни подбор.", "warning");
    return;
  }

  renderExportPreview();
  showToast("Откроется системное окно печати. Там можно сохранить отчёт как PDF.", "info");
  window.setTimeout(() => {
    window.print();
  }, 120);
}

function refreshExportReport() {
  renderExportPreview();
  showToast(currentSearch ? "Отчёт обновлён." : "Сначала выполни подбор.", currentSearch ? "success" : "warning");
}

function formatExportDate(date) {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
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
  ];
  if (items.some((item) => shouldShowAdmissionType(item))) {
    rows.push({
      label: "Конкурс",
      value: (item) => shouldShowAdmissionType(item) ? formatAdmissionType(item.admission_type) : "не указано",
    });
  }
  if (items.some((item) => hasValue(item.price))) {
    rows.push({ label: "Стоимость", highlight: "price", value: (item) => hasValue(item.price) ? formatPrice(item.price) : "не указано" });
  }
  if (items.some((item) => hasValue(item.study_form))) {
    rows.push({ label: "Форма", value: (item) => textValue(item.study_form, "не указано") });
  }
  if (items.some((item) => hasValue(item.duration))) {
    rows.push({ label: "Срок", value: (item) => textValue(item.duration, "не указано") });
  }
  if (items.some((item) => hasValue(item.faculty))) {
    rows.push({ label: "Факультет", value: (item) => textValue(item.faculty, "не указано") });
  }
  if (items.some((item) => hasValue(item.year))) {
    rows.push({ label: "Год данных", value: (item) => textValue(item.year, "не указано") });
  }
  if (items.some((item) => formatSubjects(item.subjects))) {
    rows.push({ label: "Предметы", value: (item) => formatSubjects(item.subjects) || "не указано" });
  }
  if (items.some((item) => hasValue(item.url))) {
    rows.push({
      label: "Сайт",
      html: (item) => hasValue(item.url) ? `<a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noopener noreferrer">Открыть сайт</a>` : "не указано",
    });
  }

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
    showToast("Можно сравнить до 3 вариантов.", "warning");
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
  showToast("Добавлено к сравнению.", "success");
  renderAll();

  if (telegramWebApp?.HapticFeedback) {
    telegramWebApp.HapticFeedback.impactOccurred("light");
  }
}

function removeFromComparison(key) {
  comparisonNotice = "";
  comparisonItems = comparisonItems.filter((item) => getUniversityKey(item) !== key);
  saveComparisonItems();
  showToast("Убрано из сравнения.", "info");
  renderAll();
}

function clearComparison() {
  comparisonNotice = "";
  comparisonItems = [];
  saveComparisonItems();
  showToast("Сравнение очищено.", "info");
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

function hasValue(value) {
  if (value === null || value === undefined) {
    return false;
  }
  if (Array.isArray(value)) {
    return value.some((item) => hasValue(item));
  }
  if (typeof value === "string") {
    return value.trim() !== "";
  }
  return true;
}

function formatSubjects(subjects) {
  if (Array.isArray(subjects)) {
    return subjects
      .map((subject) => String(subject).trim())
      .filter(Boolean)
      .join(", ");
  }
  if (typeof subjects === "string" && subjects.trim()) {
    return subjects.trim();
  }
  return "";
}

function formatAdmissionType(value) {
  const normalized = String(value || "").trim().toLowerCase().replaceAll(" ", "_").replaceAll("-", "_");
  const labels = {
    budget: "бюджет",
    paid: "платное",
    target: "целевая квота",
    special_quota: "особая квота",
    separate_quota: "отдельная квота",
    additional: "дополнительный набор",
  };
  return labels[normalized] || (hasValue(value) ? String(value).trim() : "");
}

function shouldShowAdmissionType(item) {
  const label = formatAdmissionType(item?.admission_type);
  return Boolean(label) && !["бюджет", "платное"].includes(label);
}

function formatPrice(price) {
  if (!hasValue(price)) {
    return "не указана";
  }
  const numericPrice = Number(price);
  if (Number.isFinite(numericPrice)) {
    return `${numericPrice.toLocaleString("ru-RU")} руб./год`;
  }
  return String(price);
}

function formatValue(value) {
  if (!hasValue(value)) {
    return "не указано";
  }
  return String(value);
}

function textValue(value, fallback) {
  if (!hasValue(value)) {
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

function showToast(message, type = "info") {
  if (!toastContainerNode || !message) {
    return;
  }

  const safeType = ["success", "info", "warning", "error"].includes(type) ? type : "info";
  const toast = document.createElement("div");
  toast.className = `toast toast--${safeType}`;
  toast.textContent = message;
  toastContainerNode.appendChild(toast);

  while (toastContainerNode.children.length > 3) {
    toastContainerNode.removeChild(toastContainerNode.firstElementChild);
  }

  window.setTimeout(() => {
    toast.classList.add("toast--leaving");
    window.setTimeout(() => {
      toast.remove();
    }, 180);
  }, 3200);
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
