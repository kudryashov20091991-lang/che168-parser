# Парсер на Google Cloud Run — БЕСПЛАТНО 24/7

## Преимущества

- ✅ **2 млн запросов/месяц бесплатно** (хватит на круглосуточный парсинг)
- ✅ Нет VPN блокировок (сервера Google по всему миру)
- ✅ Прокси работают 100%
- ✅ Запуск по HTTP запросу
- ✅ Автоматическое масштабирование

## Настройка (5 минут)

### 1. Войти в Google Cloud

Открыть: https://console.cloud.google.com

Войти через почту: `kudryashov20091991@gmail.com`

### 2. Создать проект

1. Click на селектор проектов (сверху)
2. "NEW PROJECT"
3. Name: `che168-parser`
4. Click "CREATE"

### 3. Включить Cloud Run API

1. Открыть: https://console.cloud.google.com/apis/library/run.googleapis.com
2. Click "ENABLE"

### 4. Развернуть парсер

Открыть Cloud Shell (иконка `>_` сверху справа) и выполнить:

```bash
# Клонировать репо с парсером
git clone https://github.com/your-user/che168-parser.git
cd che168-parser/cloud_run

# Собрать и развернуть
gcloud run deploy che168-parser \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 120s
```

### 5. Получить URL

После деплоя будет выдан URL вида:
```
https://che168-parser-xxx.run.app
```

### 6. Запустить парсинг

Открыть в браузере:
```
https://che168-parser-xxx.run.app/parse
```

Или через curl:
```bash
curl https://che168-parser-xxx.run.app/parse
```

## Автоматизация

### Вариант 1: Cloud Scheduler (каждые 5 минут)

```bash
gcloud scheduler jobs create http che168-every-5min \
  --schedule "*/5 * * * *" \
  --uri "https://che168-parser-xxx.run.app/parse" \
  --http-method GET \
  --time-zone "Europe/Moscow"
```

### Вариант 2: GitHub Actions → Cloud Run

Создать workflow который вызывает Cloud Run URL.

## Лимиты

- 2 млн запросов/месяц бесплатно
- 512 MB память (достаточно для парсера)
- 120 сек таймаут (парсер укладывается)

## Стоимость

При парсинге каждые 5 минут:
- ~8600 запросов/месяц
- **Бесплатно** (входит в 2 млн)

При парсинге каждую минуту:
- ~43000 запросов/месяц
- **Бесплатно**

## Результат

JSON ответ:
```json
{
  "timestamp": "2026-03-27T12:00:00",
  "source": "che168.com",
  "cars_found": 10,
  "cars": [
    {"price_cny": 120000, "price_rub": 1560000, "proxy": "45.32.56.105:13851"}
  ]
}
```

---

**Итого:** Полностью бесплатно для круглосуточного парсинга!
