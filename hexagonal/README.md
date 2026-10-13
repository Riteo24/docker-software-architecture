# Hexagonal — замовлення з двома адаптерами

## Архітектура

Ядро `core/` містить Order, валідацію, порт OrderRepository та сценарії CreateOrder/GetOrder.
Воно не імпортує `adapters/` і не залежить від FastAPI, PostgreSQL або CSV.
Порт має `create(order) -> OrderId`, `get_by_id(id) -> Order | None` (Python-еквівалент getById) та службову перевірку ping.

Вхідний HTTP-адаптер викликає сценарії ядра. Вихідні адаптери PostgreSQL та CSV реалізують один порт.
Фабрика у `config/wiring.py` обирає реалізацію за ENV `REPO_ADAPTER=db|file` і виконує DI.

## Контракти

- POST /orders із `{"sku":"ABC","qty":2}` → 201 `{"id":"UUID"}`.
- GET /orders/UUID → 200 `{"id":"UUID","sku":"ABC","qty":2}`.
- GET /orders/невідомий-id → 404.
- Порожній sku, qty ≤ 0 або неціла qty → 422.
- GET /health → 200 або 503 за недоступного сховища.

## Запуск PostgreSQL

```bash
cp .env.example .env
docker compose up --build -d --wait
curl -X POST http://localhost:8081/orders -H 'Content-Type: application/json' -d '{"sku":"ABC","qty":2}'
# Підставте UUID, отриманий у відповіді POST:
curl http://localhost:8081/orders/UUID
python3 tests/smoke.py
```

На старті DB-варіанту виконується `adapters/db/001_orders.sql`. SQL параметризований.
PostgreSQL 16 має healthcheck та іменований volume `orders-db`.

## Перемикання на CSV лише через ENV

```bash
REPO_ADAPTER=file docker compose up -d --force-recreate --wait api
python3 tests/smoke.py
```

Також можна змінити `REPO_ADAPTER=file` у `.env` та повторити запуск.
CSV має заголовок `id,sku,qty`, а шлях задається через `CSV_PATH=/data/orders.csv`.
Volume `orders-csv:/data` зберігає дані після перезапуску API.
Записи CSV екрануються стандартною бібліотекою csv, а блокування fcntl захищає одночасні читання/записи.
Зміна адаптера змінює сховище: раніше створені DB-замовлення автоматично не копіюються в CSV.
БД залишається у базовому Compose і може працювати невикористаною для file-варіанту; це дозволяє перемикати конфігурацію одним ENV.

Повернення до БД:

```bash
REPO_ADAPTER=db docker compose up -d --force-recreate --wait api
python3 tests/smoke.py
docker compose down
```

## Тести

Core-тести перевіряють валідацію та сценарії з мок-репозиторієм.
Додаткові тести перевіряють HTTP з CSV, відновлення даних новим екземпляром адаптера та одночасні записи.

```bash
docker build --target test -t architecture-hexagonal-tests .
docker run --rm architecture-hexagonal-tests
```

Локально: `pip install -r requirements.txt -r requirements-dev.txt`, потім `python -m pytest -q`.
Повна Docker-перевірка з обома сховищами: із головної папки `bash scripts/docker_check.sh hexagonal`.
ENV і всі навчальні значення наведені в `.env.example`.
