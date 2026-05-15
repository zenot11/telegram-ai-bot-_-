const form = document.querySelector("#search-form");
const resultsNode = document.querySelector("#results");
const statusNode = document.querySelector("#status-text");

const SAFE_MARGIN = 25;
const AMBITIOUS_MARGIN = 20;

const categoryMeta = {
  safe: {
    className: "safe",
    label: "🟢 Безопасный вариант",
  },
  realistic: {
    className: "realistic",
    label: "🟡 Реалистичный вариант",
  },
  ambitious: {
    className: "ambitious",
    label: "🔴 Амбициозный вариант",
  },
};

if (window.Telegram?.WebApp) {
  window.Telegram.WebApp.ready();
  window.Telegram.WebApp.expand();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const scoreValue = String(formData.get("score") || "").trim();
  const score = Number(scoreValue);
  const type = formData.get("education-type") === "paid" ? "paid" : "budget";

  const validationError = validateScore(scoreValue, score);
  if (validationError) {
    showStatus(validationError, true);
    resultsNode.innerHTML = "";
    return;
  }

  const params = new URLSearchParams({
    region: formData.get("region"),
    score: String(score),
    direction: formData.get("direction"),
    type,
    limit: "5",
  });

  showStatus("Ищу варианты...");
  resultsNode.innerHTML = "";

  try {
    const response = await fetch(`/api/universities?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const payload = await response.json();
    if (!Array.isArray(payload)) {
      throw new Error("Unexpected backend response");
    }

    const visibleResults = payload.filter((item) => classifyUniversity(score, item) !== "unavailable");
    renderResults(visibleResults, score);
  } catch (error) {
    showStatus("Backend-заглушка недоступна. Запусти python -m backend_stub.main.", true);
  }
});

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

function renderResults(items, score) {
  if (!items.length) {
    showStatus("По таким параметрам вариантов не найдено. Попробуй другой регион, направление или тип обучения.");
    resultsNode.innerHTML = "";
    return;
  }

  showStatus(`Нашла вариантов: ${items.length}. Сейчас используются демонстрационные данные.`);
  resultsNode.innerHTML = items.map((item, index) => renderCard(item, score, index + 1)).join("");
}

function renderCard(item, score, index) {
  const category = classifyUniversity(score, item);
  const meta = categoryMeta[category] || categoryMeta.ambitious;
  const subjects = Array.isArray(item.subjects) && item.subjects.length
    ? item.subjects.join(", ")
    : "не указаны";
  const minScore = getMinScore(item);
  const delta = minScore === null ? null : score - minScore;

  return `
    <article class="result-card">
      <h3>${index}. ${escapeHtml(item.university || "Вуз")}</h3>
      <span class="badge ${meta.className}">${meta.label}</span>
      <div class="result-meta">
        <div><b>Город:</b> ${escapeHtml(item.city || "не указан")}</div>
        <div><b>Программа:</b> ${escapeHtml(item.program || "не указана")}</div>
        <div><b>Предметы:</b> ${escapeHtml(subjects)}</div>
        <div><b>Мин. балл:</b> ${escapeHtml(formatValue(minScore))}</div>
        <div><b>Твои баллы:</b> ${score}</div>
        <div><b>${delta === null ? "Запас" : delta >= 0 ? "Запас" : "Не хватает"}:</b> ${escapeHtml(formatDelta(delta))}</div>
        <div><b>Тип:</b> ${escapeHtml(item.type || "не указан")}</div>
        <div><b>Стоимость:</b> ${escapeHtml(formatPrice(item.price))}</div>
        ${item.study_form ? `<div><b>Форма:</b> ${escapeHtml(item.study_form)}</div>` : ""}
        ${item.duration ? `<div><b>Срок:</b> ${escapeHtml(item.duration)}</div>` : ""}
        ${item.url ? `<div><b>Сайт:</b> <a class="site-link" href="${escapeAttribute(item.url)}" target="_blank" rel="noreferrer">${escapeHtml(item.url)}</a></div>` : ""}
        <div><b>Пометка:</b> ${escapeHtml(item.note || "демонстрационные данные")}</div>
      </div>
    </article>
  `;
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

function getMinScore(item) {
  const value = Number(item.min_score);
  return Number.isFinite(value) ? value : null;
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

function showStatus(text, isError = false) {
  statusNode.textContent = text;
  statusNode.classList.toggle("status-error", isError);
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
