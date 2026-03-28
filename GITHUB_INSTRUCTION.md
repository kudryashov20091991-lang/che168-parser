# GitHub Actions - Автозапуск парсера

## Шаг 1: Создать токен (2 мин)

1. Войти: https://github.com/login (kudryashov20091991@gmail.com / !1Vbkkbfhl _4)
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Name: `che168-parser`
5. Permissions: **repo** (все галочки), **workflow**
6. Click "Generate token"
7. **Скопировать токен** (начинается с `ghp_...`)

## Шаг 2: Создать репозиторий (1 мин)

1. https://github.com/new
2. Repository name: `che168-parser`
3. Public
4. Click "Create repository"

## Шаг 3: Загрузить файлы (2 мин)

В терминале:
```powershell
cd "C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры"
git init
git config user.email "kudryashov20091991@gmail.com"
git config user.name "kudryashov20091991-lang"
git remote add origin https://github.com/kudryashov20091991-lang/che168-parser.git
git add che168_parser.py .github/workflows/che168_parse.yml
git branch -M main
git push -u origin main
```

Если запросит пароль - вставить **токен** (не пароль от почты!)

## Шаг 4: Запустить (1 мин)

1. Открыть https://github.com/kudryashov20091991-lang/che168-parser/actions
2. Click "Che168 Parser"
3. Click "Run workflow" → "Run workflow"
4. Через 2 мин: скачать `che168_result.json` из артефактов

---

## Автозапуск

Парсер запускается автоматически каждые 6 часов.
Результат: https://github.com/kudryashov20091991-lang/che168-parser/actions
