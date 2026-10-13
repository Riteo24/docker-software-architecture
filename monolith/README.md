# Layered Monolith — каталог товарів

## Мета та архітектура

Реалізовано багатошаровий моноліт із напрямком виконання запиту:
**presentation → application → domain → infrastructure через порт репозиторію**.
Домен і сценарії залежать від інтерфейсу `ProductRepository`, а не від PostgreSQL.
Зовнішня infrastructure реалізує цей порт. `app/bootstrap.py` є composition root: він створює адаптери та передає їх сценаріям.

| Шар | Файли | Відповідальність |
|---|---|---|
| Presentation | `app/presentation/http.py` | HTTP, DTO, відповіді та мапінг |
| Application | `app/application/usecases.py` | CreateProduct, ListProducts, CheckHealth |
| Domain | `app/domain/product.py`, `ports.py` | Product, валідація, помилка та порт |
| Infrastructure | `app/infrastructure/` | SQL, PostgreSQL, Alembic, необов'язковий Redis |

Контролери не імпортують infrastructure і не виконують SQL. Перевірка цього правила автоматизована в `../scripts/check_structure.py`.

## Контракти

| Метод і шлях | Успішна відповідь |
|---|---|
| GET /health | 200 `{"status":"ok"}`; 503, якщо таблиця/БД недоступна |
| GET /products | 200 `[{"id":1,"name":"Desk","price":199.9}]` |
| POST /products | Тіло `{"name":"Desk","price":199.9}` → 201 `{"id":1}` |

Ім'я після обрізання пробілів повинно містити 1–100 символів. Ціна повинна бути додатним скінченним числом.
Невалідний ввід повертає 422. Усередині домену ціна зберігається як Decimal, у PostgreSQL — NUMERIC, у JSON — число.

## Запуск та перевірка

```bash
cp .env.example .env
docker compose up --build -d --wait
curl http://localhost:8080/health
curl -X POST http://localhost:8080/products -H 'Content-Type: application/json' -d '{"name":"Desk","price":199.9}'
curl http://localhost:8080/products
python3 tests/smoke.py
docker compose down
```

Compose піднімає `api` і `db` (`postgres:16`). Обидва мають healthcheck, БД має volume `products-data`.
API чекає готовності БД та перед початком приймання HTTP запускає `alembic upgrade head`.
Міграція створює `products(id PRIMARY KEY, name TEXT NOT NULL, price NUMERIC CHECK > 0)` з додатковими перевірками імені та скінченності ціни.
Версія міграції зберігається у `alembic_version`, тому повторний старт безпечний.

ENV: DB_HOST=db, DB_PORT=5432, DB_NAME=shop, DB_USER=shop, DB_PASS=shop, PORT=8080.
Compose також працює без `.env`, використовуючи навчальні значення за замовчуванням.
При зміні PORT змініть адресу curl/BASE_URL.

## Docker і тести

Dockerfile має builder, slim runtime, окремий test-stage та користувача `app` із UID 10001.
У runtime є HEALTHCHECK, що виконує GET /health. Тести запускаються з test-stage:

```bash
docker build --target test -t architecture-monolith-tests .
docker run --rm architecture-monolith-tests
```

Локально: встановіть `requirements.txt` і `requirements-dev.txt`, потім `python -m pytest -q`.
Перевіряються порожнє/занадто довге ім'я, від'ємна/нульова/нескінченна ціна, сценарії з мок-репозиторієм і HTTP-контракти.
Smoke-тест звертається до справжнього запущеного API та перевіряє health/create/list/відмову невалідному вводу.

## Ускладнення, які також реалізовано

**Redis:** кеш для GET /products, TTL 30 секунд. Після створення товару змінюється версія ключа кешу; наступний список читає актуальні дані.
У разі недоступності Redis читання переходить до PostgreSQL. Якщо Redis був недоступний під час запису, старий кеш може існувати до завершення TTL.

```bash
docker compose -f docker-compose.yml -f docker-compose.cache.yml up --build -d --wait
docker compose -f docker-compose.yml -f docker-compose.cache.yml down
```

**Alembic:** стартові міграції та ручна команда `make migrate`.
Makefile також містить `make test`, `make up`, `make smoke`.

Демонстраційні облікові дані `shop/shop` використовуються тільки для локального навчального запуску.
