# Запуск парсера на GitHub Actions

## Ваш аккаунт
Почта: `kudryashov20091991@gmail.com`

## Шаг 1: Создать репозиторий (1 мин)

1. Открыть https://github.com/new
2. Repository name: `che168-parser`
3. Public
4. Click **"Create repository"**

## Шаг 2: Запушить код (1 мин)

Открыть PowerShell и выполнить:

```powershell
cd "C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры"

git remote add origin https://github.com/kudryashov20091991/che168-parser.git

git branch -M main

git push -u origin main
```

**Если запросит пароль:**
1. Открыть https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Name: `che168-parser`
4. Permissions: ✅ `repo`, ✅ `workflow`
5. Click "Generate token"
6. Скопировать токен (вида `ghp_...`)
7. Вставить вместо пароля в терминале

## Шаг 3: Включить Actions (30 сек)

1. Открыть https://github.com/kudryashov20091991/che168-parser/actions
2. Если видно сообщение — click **"Enable"**

## Шаг 4: Запустить парсер (2 мин)

1. На странице Actions выбрать **"Che168 Parser"**
2. Click **"Run workflow"**
3. Ветка: `main`
4. Click **"Run workflow"**
5. Через 1-2 минуты появится зеленый запуск

## Результат

1. Click на зеленый запуск ✓
2. Внизу секция **"Artifacts"**
3. Скачать `che168_result.json`
4. Открыть — там 10 авто с ценами в CNY и RUB

---

## Про лимиты (ответ на вопрос)

**2000 минут/месяц** — это время выполнения workflow.

Один запуск парсера = **2 минуты**.

Итого: **1000 запусков в месяц** бесплатно.

### Для круглосуточного парсинга:

| Интервал | Запусков/мес | Минут/мес | Статус |
|----------|--------------|-----------|--------|
| Каждые 5 мин | 8640 | 17280 | ❌ Не входит |
| Каждые 15 мин | 2880 | 5760 | ❌ Не входит |
| Каждые 30 мин | 1440 | 2880 | ❌ Не входит |
| Каждые 6 часов | 120 | 240 | ✅ Входит |

**Вывод:** GitHub Actions подходит для периодического парсинга (каждые 6 часов).

### Для круглосуточного парсинга (каждые 5-15 мин):

1. **Google Cloud Run** — 2 млн запросов бесплатно
   - Папка: `cloud_run/INSTRUCTION.md`
   - Запуск по HTTP запросу

2. **VPS на Beget** — 210 руб/мес
   - https://www.beget.com/ru/vps
   - От 7 руб/день
   - Без лимитов

---

**Рекомендация:** Начните с GitHub Actions (бесплатно, быстро).
Если нужно чаще — Google Cloud Run (без лимитов).
