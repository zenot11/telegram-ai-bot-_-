# Database usage audit

Этап 45 фиксирует, как проект “Аиша” использует PostgreSQL-базу команды. Изучены SQL-файлы из `finalproj.zip`: `01_schema.sql`, `02_seed_universities.sql`, `03_seed_directions_and_scores.sql`, `04_seed_achievements.sql`, `05_example_queries.sql`, `06_seed_supplement_universities.sql`. SQL-файлы и архив не добавляются в Git.

PostgreSQL остаётся основным пользовательским источником при `USE_POSTGRES=true`; JSON остаётся fallback для запуска и тестов без live-базы. Пользовательские данные Telegram-бота, избранное Mini App и feedback не переносятся в PostgreSQL, потому что проект уже использует локальные JSON-хранилища бота и проверенную Telegram WebApp-сессию.

## Итог

- Основной пользовательский JOIN: `passing_scores -> directions -> universities`, плюс `LEFT JOIN faculties`.
- `passing_scores` используется как факт наличия конкурсной записи. Направления без проходных баллов не попадают в обычную выдачу подбора, чтобы не выглядеть как полноценный вариант поступления.
- `faculties` используется через `LEFT JOIN`, чтобы отсутствие факультета не выбрасывало направление.
- `achievements` используется как общий справочник индивидуальных достижений. В схеме нет связи `university_id/direction_id`, поэтому карточки вузов не показывают достижения как вуз-специфичные правила.
- Таблицы `users`, `user_ege_scores`, `user_achievements`, `user_favorites` не используются текущим Python backend: они относятся к исходной командной схеме пользовательского кабинета, а не к Telegram storage проекта.
- View `v_directions_with_latest_budget` изучена, но основной backend строит запросы напрямую, потому что ему нужны все `admission_type`, `paid`, квоты, score-фильтр и exact-code fallback.

## Таблицы и поля

| Таблица | Поле | Смысл | Используется сейчас? | Где используется | Можно показывать пользователю? | Комментарий / причина неиспользования |
| --- | --- | --- | --- | --- | --- | --- |
| `universities` | `id` | Primary key вуза | Да | JOIN `directions.university_id` | Нет | Служебный идентификатор. |
| `universities` | `name` | Полное название вуза | Да | API `university`, `university_full_name`; карточки, сравнение, поиск `q` | Да | Основное пользовательское название. |
| `universities` | `short_name` | Аббревиатура | Да | API `university_short_name`; поиск `q`; карточки | Да, условно | Показывается только если это полезная аббревиатура. Технические `РЦТИ-26` скрываются. |
| `universities` | `city` | Город | Да | API `city`; `/api/cities`; фильтр `city`; location | Да | Если `city=region`, UI не дублирует значение. |
| `universities` | `region` | Субъект РФ | Да | API `region`; `/api/regions`; фильтр `region`; location | Да | Алиасы `Крым`, `Адыгея` раскрываются в республику. |
| `universities` | `website` | Сайт вуза | Да | API `url`; карточки при наличии | Да | Пустые значения скрываются. |
| `universities` | `description` | Описание вуза | Нет | Не используется | Потенциально | В seed это не основной источник для карточек; можно использовать в будущем detail-view. |
| `universities` | `created_at`, `updated_at` | Служебные даты | Нет | Не используется | Нет | Не нужны пользователю в подборе. |
| `faculties` | `id` | Primary key факультета | Да | JOIN `directions.faculty_id` | Нет | Служебный идентификатор. |
| `faculties` | `university_id` | Связь с вузом | Да | FK integrity; JOIN через `directions` | Нет | Служебная связь. |
| `faculties` | `name` | Факультет / институт | Да | API `faculty`; поиск `q`; карточки при наличии | Да | `LEFT JOIN`, чтобы не терять направления без факультета. |
| `directions` | `id` | Primary key направления | Да | JOIN `passing_scores.direction_id`; view | Нет | Служебный идентификатор. |
| `directions` | `university_id` | Связь направления с вузом | Да | JOIN `universities` | Нет | Обязательная связь. |
| `directions` | `faculty_id` | Связь с факультетом | Да | `LEFT JOIN faculties` | Нет | Может быть `NULL`; поэтому не `INNER JOIN`. |
| `directions` | `name` | Название направления | Да | API `program`, `direction`; `/api/directions`; карточки; q-search | Да | Основное название программы. |
| `directions` | `code` | Код направления, например `09.03.04` | Да | API `direction_code`; exact-code first search; `/api/directions?q=...` | Да, как часть направления | При запросе с кодом backend сначала ищет точный `directions.code`. |
| `directions` | `profile` | Профиль / специализация | Да | API `profile`; fallback matching; q-search | Да, если полезно | Не показывается как обязательное поле и не должен дублировать `name`. |
| `directions` | `study_form` | Форма обучения enum | Да | API `study_form`, `study_form_label`; `/api/study-forms`; фильтр | Да | UI label: `Форма обучения`. |
| `directions` | `level` | Уровень образования | Нет | Не используется | Потенциально | В текущем UI нет фильтра бакалавриат/специалитет/магистратура; можно добавить без изменения API. |
| `directions` | `created_at` | Служебная дата | Нет | Не используется | Нет | Не нужна пользователю. |
| `passing_scores` | `id` | Primary key записи балла | Нет | Не используется напрямую | Нет | Служебный идентификатор. |
| `passing_scores` | `direction_id` | Связь с направлением | Да | Основной JOIN | Нет | Обязательная связь для результата подбора. |
| `passing_scores` | `year` | Год данных | Да | API `year`; карточки; сортировка `year_desc`; audit | Да | Помогает не смешивать годы без контекста. |
| `passing_scores` | `admission_type` | Тип конкурса / финансирования | Да | API `admission_type`, `type`, `financing_label`, `contest_label`; фильтры | Да, нормализованно | `budget/paid` идут в `Финансирование`, квоты идут в `Конкурс`. |
| `passing_scores` | `min_score` | Минимальный / проходной балл | Да | API `min_score`, `score_display`, `score_is_valid`, `score_is_suspicious`; ranking | Да, аккуратно | `<40` считается suspicious и не даёт safe/gap. |
| `passing_scores` | `note` | Пометка источника | Да | API `note`; карточки при наличии | Да | Полезно для квот, БВИ и неполных значений. |
| `achievements` | `id` | Primary key достижения | Нет | Не отдаётся в UI | Нет | Служебный идентификатор. |
| `achievements` | `code` | Стабильный код достижения | Да | `/api/achievements` item code | Нет для обычного текста | Полезно для машинной обработки, не как основная подпись. |
| `achievements` | `name` | Название достижения | Да | `/api/achievements`; Mini App block | Да | Показывается как общий справочник. |
| `achievements` | `max_points` | Ориентировочный потолок баллов | Да | `/api/achievements` | Да, с пояснением | Не является гарантией конкретного вуза. |
| `achievements` | `description` | Пояснение | Да | `/api/achievements`; Mini App block | Да | Точные правила зависят от вуза. |
| `users` | `id`, `email`, `password_hash`, `full_name`, `graduation_year`, `created_at`, `updated_at` | Пользовательский кабинет исходной схемы | Нет | Не используется | Нет | Проект не переносит Telegram user storage в PostgreSQL; `.env`/токены не связаны с этой таблицей. |
| `user_ege_scores` | `id`, `user_id`, `subject`, `score` | ЕГЭ пользователя в исходной схеме | Нет | Не используется | Нет | Telegram-бот хранит пользовательские сценарии в локальном JSON storage. |
| `user_achievements` | `user_id`, `achievement_id`, `points`, `awarded_at` | Достижения конкретного пользователя | Нет | Не используется | Нет | Нет текущего PostgreSQL user session layer; Mini App не принимает user_id из клиента. |
| `user_favorites` | `user_id`, `direction_id`, `added_at` | Избранные направления исходной схемы | Нет | Не используется | Нет | Избранное синхронизируется с Telegram-ботом через `telegram_bot/storage/user_data.py`. |
| `v_directions_with_latest_budget` | все поля view | Денормализованный справочник последнего бюджетного балла | Нет | Не используется | Потенциально | Не подходит как основной источник, потому что не содержит paid/квоты и не покрывает текущие filters. |

## Безопасные будущие улучшения

- Добавить фильтр `level`, если защите нужно разделять бакалавриат, специалитет и магистратуру.
- Сделать detail-view в Mini App, где `universities.description`, `directions.profile`, `faculties.name` и `passing_scores.note` показываются подробнее.
- Использовать `v_directions_with_latest_budget` только как вспомогательный быстрый каталог, не как основной источник `/api/universities`.
- Добавить вуз-специфичные достижения только если появится таблица связи `university_achievement_points` или аналогичная.
