MAX_TOTAL_SCORE = 400

AVAILABLE_DIRECTIONS = (
    "IT",
    "психология",
    "медицина",
    "экономика",
    "педагогика",
    "юриспруденция",
    "инженерия",
    "дизайн",
    "строительство",
    "туризм",
)

AVAILABLE_REGIONS = (
    "Адыгея",
    "Москва",
    "Краснодарский край",
    "Санкт-Петербург",
    "Татарстан",
    "Крым",
    "Ростовская область",
    "Свердловская область",
)

REGION_ALIASES = {
    "адыгея": "Адыгея",
    "адыгея республика": "Адыгея",
    "республика адыгея": "Адыгея",
    "адыгеая": "Адыгея",
    "адыгеяа": "Адыгея",
    "москва": "Москва",
    "москве": "Москва",
    "мск": "Москва",
    "moscow": "Москва",
    "краснодарский край": "Краснодарский край",
    "краснодар": "Краснодарский край",
    "краснодарский": "Краснодарский край",
    "краснодарский кр": "Краснодарский край",
    "санкт-петербург": "Санкт-Петербург",
    "санкт петербург": "Санкт-Петербург",
    "спб": "Санкт-Петербург",
    "питер": "Санкт-Петербург",
    "петербург": "Санкт-Петербург",
    "татарстан": "Татарстан",
    "республика татарстан": "Татарстан",
    "казань": "Татарстан",
    "казан": "Татарстан",
    "крым": "Крым",
    "республика крым": "Крым",
    "симферополь": "Крым",
    "севастополь": "Крым",
    "ростовская область": "Ростовская область",
    "ростов": "Ростовская область",
    "ростов-на-дону": "Ростовская область",
    "ростов на дону": "Ростовская область",
    "свердловская область": "Свердловская область",
    "екатеринбург": "Свердловская область",
    "свердловск": "Свердловская область",
}

DIRECTION_SYNONYMS = {
    "IT": (
        "it",
        "айти",
        "айт",
        "информатика",
        "программирование",
        "разработка",
        "программист",
        "кодинг",
        "информационные технологии",
        "компьютерные науки",
    ),
    "психология": ("психолог", "психология", "псих", "психфак"),
    "медицина": ("медицина", "мед", "лечебное", "лечебное дело", "врач"),
    "экономика": ("экономика", "эконом", "бизнес", "финансы", "менеджмент"),
    "педагогика": ("педагогика", "педагог", "учитель", "образование"),
    "юриспруденция": ("юриспруденция", "юрист", "право", "законы", "юридический"),
    "инженерия": ("инженерия", "инженер", "техника", "машиностроение", "техническое"),
    "дизайн": ("дизайн", "графика", "визуальные", "дизайнер"),
    "строительство": ("строительство", "архитектура", "строительный", "стройка"),
    "туризм": ("туризм", "гостиницы", "гостиничное", "сервис"),
}

EDUCATION_TYPE_LABELS = {
    "budget": "бюджет",
    "paid": "платное",
}


def parse_score(text: str) -> tuple[int | None, str | None]:
    value = text.strip().lower().replace("ё", "е").strip(".,;:!?")
    for suffix in ("баллов", "балла", "балл"):
        if value.endswith(suffix):
            value = value.removesuffix(suffix).strip()
            break
    value = value.replace(" ", "")
    if not value:
        return None, "Баллы нужно ввести числом, например: 230."

    if value.startswith("-") and value[1:].isdigit():
        return None, "Баллы не могут быть отрицательными. Введи сумму баллов ЕГЭ числом."

    if not value.isdigit():
        return None, "Баллы нужно ввести числом, например: 230."

    score = int(value)
    if score > MAX_TOTAL_SCORE:
        return None, "Проверь сумму баллов. Обычно сумма ЕГЭ указывается в пределах 0–400."

    return score, None


def normalize_text(text: str) -> str:
    cleaned = text.strip().lower().replace("ё", "е")
    cleaned = cleaned.strip(".,;:!?")
    return " ".join(cleaned.split())


def normalize_region(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    normalized = normalize_text(cleaned)
    if normalized in REGION_ALIASES:
        return REGION_ALIASES[normalized]
    return cleaned[:1].upper() + cleaned[1:] if cleaned else cleaned


def normalize_direction(text: str) -> str:
    cleaned = " ".join(text.strip().split())
    normalized = normalize_text(cleaned)

    for direction, synonyms in DIRECTION_SYNONYMS.items():
        if normalized == normalize_text(direction):
            return direction
        if any(synonym in normalized for synonym in synonyms):
            return direction

    return cleaned


def normalize_education_type(text: str) -> str | None:
    value = normalize_text(text)
    if value in {
        "budget",
        "бюджет",
        "бюджетное",
        "бюджетный",
        "бесплатно",
        "бесплатное",
        "гос",
        "государственное",
    } or "бюдж" in value:
        return "budget"
    if value in {
        "paid",
        "платное",
        "платно",
        "платный",
        "контракт",
        "контрактное",
        "договор",
        "коммерция",
        "коммерческое",
    } or "плат" in value:
        return "paid"
    return None


def normalize_study_type(text: str) -> str | None:
    return normalize_education_type(text)


def education_type_label(value: str) -> str:
    return EDUCATION_TYPE_LABELS.get(value, "не указан")
