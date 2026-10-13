# Event-Driven — асинхронна обробка замовлення

## Архітектура

Сервіси обмінюються подіями через Kafka topic **orders.events**:

1. orders отримує POST /orders і публікує OrderCreated.
2. billing читає OrderCreated, моделює платіж і публікує PaymentCaptured.
3. notifications читає PaymentCaptured, записує повідомлення про email у лог і публікує EmailSent.

Усі події знаходяться в одному topic, їхній тип розрізняється полем `type`.
Billing та notifications мають різні consumer groups і фільтрують події потрібного типу.
Ключ повідомлення — orderId. У навчальному topic одна partition, тому порядок для замовлення зберігається.
Ініціалізатор `init-topics` створює topic до запуску прикладних сервісів.

## Формати подій

| Тип | Поля payload |
|---|---|
| OrderCreated | orderId, userId, itemId, qty, ts |
| PaymentCaptured | orderId, amount, ts |
| EmailSent | orderId, to, ts |

Кожна подія також містить `type` та UUID `eventId` для маршрутизації й ідемпотентності.
`orderId` — UUID, `ts` — ISO 8601 із часовим поясом.
JSON Schema з прикладами обмежень зберігаються у [schemas](schemas/); видавець та обробники перевіряють повідомлення за цими схемами.

Платіж навчальний: amount = qty × 100.00. Реального списання коштів немає.
Email у цій реалізації відправляється як дозволений умовою лог, адреса — `customer@example.com`.
SMTP-сервіс і пошук email користувача не входять до цієї демонстрації.

## Запуск

```bash
cp .env.example .env
docker compose up --build -d --wait --wait-timeout 600
curl -X POST http://localhost:5002/orders -H 'Content-Type: application/json' -d '{"userId":1,"itemId":2,"qty":1}'
docker compose logs -f billing notifications
```

Ctrl+C зупиняє перегляд логів. Контейнери залишаються працювати; для їх зупинки виконайте `docker compose down`.
У логах будуть PROCESSED type=OrderCreated, PROCESSED type=PaymentCaptured та EMAIL_LOG з тим самим orderId.

Compose використовує Kafka і ZooKeeper Confluent 7.7.12, healthchecks та volumes для журналів.
Kafka має внутрішню адресу kafka:9092; порт брокера не публікується на комп'ютер, тому команди Kafka виконуються в контейнері.
Orders відповідає 201 тільки після підтвердження публікації брокером; за помилки публікації відповідає 503.

## Повторна подія й ідемпотентність

Billing тримає `processed_event_ids` і `processed_order_ids` у пам'яті.
Повтор тієї самої події або інша OrderCreated для вже обробленого orderId не створюють другого платежу.
Notifications також запобігає повторному логуванню email для orderId.
Після успішної обробки consumer вручну підтверджує offset. Якщо обробка не вдалася, offset не підтверджується, а процес завершується для повторного запуску.

```bash
# Створює нове навчальне замовлення й надсилає одну OrderCreated двічі:
docker compose exec orders python -m scripts.replay_order
docker compose logs billing notifications
```

Множини у пам'яті дозволені умовою завдання. Вони очищуються після перезапуску worker, тому гарантія усунення дублікатів обмежена життям процесу.
Для виробничої системи потрібні стійке сховище оброблених подій, outbox/транзакційна публікація та ідемпотентний платіжний провайдер.
Цей приклад не заявляє exactly-once доставку.

## Тести

Unit-тести перевіряють OrderCreated → PaymentCaptured → EmailSent, дублікати, повтор після тимчасової помилки публікації, JSON Schema та HTTP.

```bash
docker build --target test -t architecture-event-driven-tests .
docker run --rm architecture-event-driven-tests
docker compose exec orders python -m tests.smoke
```

Smoke звертається до працюючого orders, читає справжній Kafka topic, перевіряє ланцюжок, публікує вихідну подію ще двічі й перевіряє, що платіж та email залишаються одиничними.
З головної папки повний запуск перевірки: `bash scripts/docker_check.sh event-driven`.
