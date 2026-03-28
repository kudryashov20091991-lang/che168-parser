# Парсер Che168 на GitHub Actions - ПОЛНАЯ ИНСТРУКЦИЯ

## Почему GitHub Actions?

| Проблема | Решение |
|----------|---------|
| VPN блокирует прокси | GitHub сервера в США, нет VPN |
| VPN блокирует Beget | Не нужен Beget |
| Логи на ПК | Логи в GitHub Actions |
| Зависит от ПК | Работает 24/7 в облаке |

## Шаг 1: Создать репозиторий (1 мин)

1. Открыть https://github.com/new
2. Repository name: `che168-parser`
3. Public (бесплатно, достаточно для парсера)
4. **НЕ** инициализировать с README/.gitignore
5. Click "Create repository"

## Шаг 2: Запушить код (2 мин)

Открыть PowerShell и выполнить:

```powershell
cd "C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры"

# Заменить YOUR_USERNAME на ваш логин GitHub
git remote add origin https://github.com/YOUR_USERNAME/che168-parser.git

git branch -M main
git push -u origin main
```

Если спросит пароль - использовать Personal Access Token:
https://github.com/settings/tokens (создать с permission "repo")

## Шаг 3: Включить Actions (30 сек)

1. Открыть https://github.com/YOUR_USERNAME/che168-parser/actions
2. Если видно "Actions have been disabled" - click "Enable"
3. Это требуется только первый раз

## Шаг 4: Запустить парсер (1 мин)

1. На странице Actions выбрать "Che168 Parser"
2. Click "Run workflow"
3. Выбрать ветку "main"
4. Click "Run workflow" еще раз
5. Ждать 1-2 минуты (зеленая галочка = готово)

## Результат

1. Click на зеленый запуск в списке Actions
2. Внизу секция "Artifacts"
3. Скачать `che168_result.json`
4. Открыть в блокноте - там 10 авто с ценами

## Автоматизация (опционально)

Файл `.github/workflows/che168_parse.yml` содержит:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Каждые 6 часов
```

Чтобы отключить автозапуск - удалить эти строки.

## Лимиты GitHub Actions

- ✅ 2000 минут/месяц бесплатно (парсер = 2 мин → 1000 запусков)
- ✅ 500 MB хранилище
- ✅ Public репозитории бесплатно

## Если что-то не так

### Ошибка при пуше
```
remote: Support for password authentication was removed
```
→ Использовать Personal Access Token вместо пароля:
https://github.com/settings/tokens/new (permissions: repo, workflow)

### Actions не запускаются
→ Проверить Settings → Actions → General → Allow all actions

### Парсер выдает 0 авто
→ Прокси могут быть временно недоступны, запустить еще раз

---

**Итого:** 3-4 минуты настройки → парсер работает в облаке 24/7
