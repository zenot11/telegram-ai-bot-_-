# PostgreSQL data source

На 37 этапе `backend_stub` получил второй источник данных для вузов, на 38 этапе PostgreSQL-режим расширен справочниками, фильтрами и сортировкой, на 40 этапе пользовательские интерфейсы переведены на PostgreSQL-first поведение, а на 41 этапе отполировано отображение реальных PostgreSQL-карточек:

- при `USE_POSTGRES=true` endpoint `/api/universities` читает данные из PostgreSQL по `DATABASE_URL`;
- JSON fallback `backend_stub/data/universities.json` остаётся для локального запуска и тестов без PostgreSQL;
- справочники `/api/regions`, `/api/cities`, `/api/directions`, `/api/study-forms`, `/api/admission-types` строятся из текущего backend-источника;
- `/api/achievements` отдаёт общий SQL-справочник индивидуальных достижений, если таблица доступна;
- контракт ответа `/api/universities` не меняется для Telegram-бота и Mini App.

На 39 этапе добавлена проверка качества выдачи: PostgreSQL-записи нормализуются к старым JSON-полям, а необязательные пустые поля (`subjects`, `price`, `duration`, `note`) не превращаются в видимые `None`, `null`, `undefined` или `[]` в Telegram-боте и Mini App. Дополнительные поля `year`, `faculty`, `admission_type`, `admission_type_label`, `financing_label`, `contest_label`, `study_form_label`, `profile`, `direction_code`, `university_full_name`, `university_short_name`, `source` описаны в [DATA_COMPATIBILITY.md](DATA_COMPATIBILITY.md); `source` остаётся диагностическим и не выводится в обычном UI.

На 40 этапе добавлены алиасы для данных команды:

- `Крым` ищется как `Республика Крым`;
- `Адыгея` ищется как `Республика Адыгея`;
- старое направление `IT` и синонимы `айти`, `информационные технологии` раскрываются в реальные PostgreSQL-направления (`Прикладная информатика`, `Информационная безопасность`, `Программная инженерия`, `Информатика и вычислительная техника` и близкие профили).

Backend использует полное `universities.name` как основное название. `short_name` выводится отдельно только если он выглядит как полезное короткое название; технические коды вида `РЦТИ-26` не становятся главным названием в карточке.

`passing_scores.min_score` читается напрямую как `min_score`, `passing_scores.admission_type` как `admission_type`, `passing_scores.year` как `year`, `passing_scores.note` как `note`, `directions.study_form` как `study_form`, `faculties.name` как `faculty`. Значения `min_score=0` и `min_score=1` не считаются полноценным проходным баллом: backend добавляет `score_is_valid=false`, `score_display="не указан"` и `score_note="балл требует уточнения"`, а UI не считает от них запас.

На 42 этапе проверена цепочка `passing_scores -> directions -> universities` и `directions.faculty_id -> faculties`: название вуза берётся из `universities.name`, факультет из `faculties.name`, направление из `directions.name`, профиль из `directions.profile`, форма из `directions.study_form`, конкурс и балл из `passing_scores`.

PostgreSQL используется только для базы вузов. Избранное, feedback и локальные пользовательские данные остаются в JSON-хранилищах проекта.

## SQL из `finalproj.zip`

В архиве найдены SQL-файлы:

- `finalproj/backend/db/sql/01_schema.sql` - схема и enum-типы;
- `finalproj/backend/db/sql/02_seed_universities.sql` - вузы;
- `finalproj/backend/db/sql/03_seed_directions_and_scores.sql` - факультеты, направления и проходные баллы;
- `finalproj/backend/db/sql/04_seed_achievements.sql` - справочник достижений;
- `finalproj/backend/db/sql/05_example_queries.sql` - примеры запросов, не миграция;
- `finalproj/backend/db/sql/06_seed_supplement_universities.sql` - дополнительное расширение каталога.

Используемые таблицы для `/api/universities`:

- `universities`: `name`, `short_name`, `city`, `region`, `website`;
- `directions`: `name`, `profile`, `study_form`;
- `passing_scores`: `year`, `admission_type`, `min_score`, `note`;
- `faculties`: `name` для дополнительного поиска по направлению.
- `achievements`: общий справочник индивидуальных достижений для `/api/achievements`.

`admission_type='budget'` отдаётся как `type='бюджет'`, `admission_type='paid'` как `type='платное'`. Форма обучения переводится из `full_time`, `part_time`, `evening` в человекочитаемые значения.

Для бюджетных SQL-конкурсов также поддерживаются `target`, `special_quota`, `separate_quota` и `additional`: в API они остаются бюджетными по полю `type`, а в UI могут отображаться отдельной строкой `Конкурс`.

## Synthetic/demo records from seed data

`06_seed_supplement_universities.sql` содержит технические расширяющие записи, например `Региональный центр технологий и инженерии (Республика Крым)` с `short_name='РЦТИ-12'` и похожие `Институт социальных и цифровых профессий (...)`. Это реальные строки таблицы `universities`, а не ошибка JOIN или mapping.

Такие записи не удаляются из PostgreSQL и seed-файлов, но скрываются из обычной пользовательской выдачи `/api/universities` по умолчанию. Для диагностики доступен query parameter `include_synthetic=true`; alias `include_demo=true` ведёт себя так же. Если после скрытия synthetic rows подходящих обычных вузов нет, UI показывает empty state и предлагает расширить регион, направление, финансирование или конкурс.

## Создание базы

Пример локальной базы:

```bash
createdb tgbot
```

Распакуйте только SQL-файлы во временную папку, не добавляя архив или распаковку в Git:

```bash
mkdir -p /tmp/finalproj-sql
unzip -j /Users/macbook/Downloads/finalproj.zip 'finalproj/backend/db/sql/*.sql' -d /tmp/finalproj-sql
```

Примените файлы в таком порядке:

```bash
psql -d tgbot -f /tmp/finalproj-sql/01_schema.sql
psql -d tgbot -f /tmp/finalproj-sql/02_seed_universities.sql
psql -d tgbot -f /tmp/finalproj-sql/03_seed_directions_and_scores.sql
psql -d tgbot -f /tmp/finalproj-sql/04_seed_achievements.sql
psql -d tgbot -f /tmp/finalproj-sql/06_seed_supplement_universities.sql
```

`05_example_queries.sql` запускать не нужно.

## Запуск backend в PostgreSQL mode

```bash
export USE_POSTGRES=true
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tgbot
bash scripts/run_backend.sh
```

Проверить health:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "service": "backend_stub",
  "storage": "postgresql",
  "data_source": "postgresql",
  "universities_count": 94
}
```

Если применён `06_seed_supplement_universities.sql`, количество будет больше базовых 94 вузов.

Проверить выдачу:

```bash
curl "http://localhost:8000/api/universities?region=Москва&score=260&direction=информатика&type=budget&limit=5"
curl "http://localhost:8000/api/universities?score=230&limit=5&sort=min_score_desc&q=информатика"
curl "http://localhost:8000/api/universities?region=Крым&score=230&direction=IT&type=budget&limit=5"
curl "http://localhost:8000/api/universities?region=Крым&score=230&direction=IT&type=budget&limit=5&include_synthetic=true"
curl "http://localhost:8000/api/regions"
curl "http://localhost:8000/api/directions"
curl "http://localhost:8000/api/achievements"
```

## Проверка PostgreSQL

Опциональная ручная проверка:

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tgbot
python scripts/check_postgres.py
```

Скрипт проверяет таблицы, количество вузов, число synthetic/demo записей, sample suspicious rows, число регионов, число направлений, справочник достижений, display labels и sample-запрос, похожий на `/api/universities`.

Общий проектный чек по умолчанию не требует PostgreSQL. Чтобы включить проверку в `scripts/check_project.sh`:

```bash
export USE_POSTGRES_TESTS=true
bash scripts/check_project.sh
```

## Возврат на JSON fallback

```bash
export USE_POSTGRES=false
bash scripts/run_backend.sh
```

Или просто не задавайте `USE_POSTGRES`: JSON fallback остаётся режимом по умолчанию.
