# Microservices + API Gateway

## Архітектура

Реалізовано три незалежні HTTP-сервіси з in-memory даними та шлюз NGINX.
Compose містить рівно чотири сервіси: catalog, users, orders, gateway, які працюють у мережі `ms-net`.
Лише gateway публікує порт на комп'ютер користувача. Каталог, користувачі й замовлення не викликають один одного.
Клієнт звертається до них через gateway.

| Запит клієнта | Внутрішній маршрут |
|---|---|
| GET /catalog/items | catalog:5000/items |
| GET /users/1 | users:5000/users/1 |
| POST /orders | orders:5000/orders |
| GET /orders/1 | orders:5000/orders/1 |

Префікс `/catalog/` видаляється в proxy_pass. `/users/` і `/orders/` є частиною контрактів відповідних сервісів і зберігаються.
Для точного POST /orders є окремий location, тому запит не залежить від перенаправлення на шлях зі слешем.

## Запуск

```bash
cp .env.example .env
docker compose up --build -d --wait
curl http://localhost:8080/catalog/items
curl http://localhost:8080/users/1
curl -X POST http://localhost:8080/orders -H 'Content-Type: application/json' -d '{"userId":1,"itemId":1,"qty":1}'
python3 tests/smoke.py
docker compose down
```

Замовлення повертає 201 `{"id":1}`. Додано GET /orders/id для перевірки створеного запису.
userId, itemId та qty мають бути додатними цілими числами; невалідний ввід повертає 422.
У цьому завданні orders не перевіряє наявність користувача/товару мережевими викликами інших сервісів.
Дані зберігаються у пам'яті та скидаються після перезапуску сервісу, як передбачено умовою.

## Healthchecks і повторні спроби

У кожного сервісу є GET /health і Compose healthcheck.
Gateway очікує service_healthy для трьох API. Політика `restart: on-failure:5` перезапускає завершений із помилкою процес.
У NGINX задано proxy_connect_timeout, proxy_read_timeout та proxy_next_upstream із максимум трьома спробами для безпечних помилок.
NGINX не налаштований повторювати вже надісланий неідемпотентний POST, щоб не створювати повторне замовлення.
Статус unhealthy сам по собі не є завершенням процесу та не активує restart.

## OpenAPI

Кожен сервіс має власний `services/НАЗВА/openapi.yaml` і GET /openapi.json.
Через gateway документація доступна за маршрутами:

- /catalog/openapi.json
- /users/openapi.json
- /orders/openapi.json

## Тести

Кожен сервіс має test-stage і HTTP contract test.
E2E smoke виконується через справжній NGINX та перевіряє каталог, користувача, створення/читання замовлення, валідацію й OpenAPI.
З головної папки: `bash scripts/docker_check.sh microservices`.

Для запуску разом із монолітом задайте `GATEWAY_PORT=8082`; smoke тоді запускайте з `BASE_URL=http://localhost:8082`.
