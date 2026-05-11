CRISIS_RESPONSE = (
    "Мне важно, чтобы ты сейчас был в безопасности. Пожалуйста, обратись к взрослому рядом, "
    "родственнику, учителю или в экстренную службу. Если есть риск, что ты навредишь себе, позвони 112."
)

CRISIS_PATTERNS = (
    "суицид",
    "самоуб",
    "покончить с собой",
    "не хочу жить",
    "не хочется жить",
    "хочу умереть",
    "лучше умереть",
    "навредить себе",
    "причинить себе вред",
    "убить себя",
    "режу себя",
    "порезать себя",
    "вскрыть вены",
    "спрыгнуть",
    "выброшусь",
)

SUPPORT_PATTERNS = (
    "устал",
    "устала",
    "выгорел",
    "выгорела",
    "боюсь",
    "страшно",
    "тревож",
    "паник",
    "не знаю куда",
    "не знаю, куда",
    "не поступ",
    "переживаю",
    "нет сил",
)


def _normalize(text: str) -> str:
    return text.lower().replace("ё", "е")


def is_crisis_message(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern in normalized for pattern in CRISIS_PATTERNS)


def is_support_message(text: str) -> bool:
    normalized = _normalize(text)
    return any(pattern in normalized for pattern in SUPPORT_PATTERNS)
