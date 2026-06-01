# PostgreSQL data source

На 37 этапе `backend_stub` получил второй источник данных для вузов, на 38 этапе PostgreSQL-режим расширен справочниками, фильтрами и сортировкой, а на 40 этапе пользовательские интерфейсы переведены на PostgreSQL-first поведение:

- при `USE_POSTGRES=true` endpoint `/api/universities` читает данные из PostgreSQL по `DATABASE_URL`;
- JSON fallback `backend_stub/data/universities.json` остаётся для локального запуска и тестов без PostgreSQL;
- справочники `/api/regions`, `/api/cities`, `/api/directions`, `/api/study-forms`, `/api/admission-types` строятся из текущего backend-источника;
- `/api/achievements` отдаёт общий SQL-справочник индивидуальных достижений, если таблица доступна;
- контракт ответа `/api/universities` не меняется для Telegram-бота и Mini App.

На 39 этапе добавлена проверка качества выдачи: PostgreSQL-записи нормализуются к старым JSON-полям, а необязательные пустые поля (`subjects`, `price`, `duration`, `note`) не превращаются в видимые `None`, `null`, `undefined` или `[]` в Telegram-боте и Mini App. Дополнительные поля `year`, `faculty`, `admission_type`, `admission_type_label`, `profile`, `direction_code`, `university_full_name`, `university_short_name`, `source` описаны в [DATA_COMPATIBILITY.md](DATA_COMPATIBILITY.md); `source` остаётся диагностическим и не выводится в обычном UI.

На 40 этапе добавлены алиасы для данных команды:

- `Крым` ищется как `Республика Крым`;
- `Адыгея` ищется как `Республика Адыгея`;
- старое направление `IT` и синонимы `айти`, `информационные технологии` раскрываются в реальные PostgreSQL-направления (`Прикладная информатика`, `Информационная безопасность`, `Программная инженерия`, `Информатика и вычислительная техника` и близкие профили).

Backend использует полное `universities.name` как основное название. `short_name` выводится отдельно только если он выглядит как полезное короткое название; технические коды вида `РЦТИ-26` не становятся главным названием в карточке.

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

Скрипт проверяет таблицы, количество вузов, число регионов, число направлений, справочник достижений и sample-запрос, похожий на `/api/universities`.

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
