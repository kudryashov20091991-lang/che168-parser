# Парсер Che168 через GitHub Actions

## Преимущества
- ✅ Работает БЕЗ VPN (GitHub сервера не блокируются)
- ✅ Прокси работают 100%
- ✅ Автоматический запуск по расписанию
- ✅ Результаты в JSON файле
- ✅ Не зависит от локального ПК

## Настройка (5 минут)

### 1. Создать репозиторий на GitHub
```bash
cd "C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры"
git init
git add .
git commit -m "Che168 parser for GitHub Actions"
```

### 2. Подключить удаленный репозиторий
```bash
git remote add origin https://github.com/ВАШ_НИК/che168-parser.git
git branch -M main
git push -u origin main
```

### 3. Запустить парсер
1. Зайти на https://github.com/ВАШ_НИК/che168-parser
2. Перейти в Actions → Che168 Parser
3. Нажать "Run workflow"
4. Через 1-2 минуты результат в артефактах

## Результат
- Файл: `che168_result.json` (скачать из артефактов)
- Или смотреть прямо в логе запуска

## Автоматизация
Парсер запускается каждые 6 часов (расписание в `.github/workflows/che168_parse.yml`)

Чтобы изменить расписание, отредактировать строку:
```yaml
- cron: '0 */6 * * *'  # Каждые 6 часов
```

## Альтернативы

### Если GitHub не подходит:
1. **PythonAnywhere** - бесплатный хостинг Python, нет VPN
2. **Replit** - облачная IDE, запуск скриптов
3. **Hugging Face Spaces** - бесплатный CPU, Python скрипты
