@echo off
chcp 65001 >nul
echo ============================================================
echo НАСТРОЙКА GITHUB ACTIONS - АВТОМАТИЧЕСКИЙ ПАРСИНГ
echo ============================================================
echo.
echo ШАГ 1: Создать токен GitHub (2 минуты)
echo ----------------------------------------------
echo 1. Откройте: https://github.com/settings/tokens
echo 2. Login: kudryashov20091991@gmail.com
echo 3. Password: !1Vbkkbfhl _4
echo 4. Generate new token (classic)
echo 5. Name: che168-parser
echo 6. Permissions: repo (все), workflow
echo 7. Generate token -> СКОПИРУЙТЕ токен (ghp_...)
echo.
set /p GITHUB_TOKEN="Вставьте токен (ghp_...): "

echo.
echo ШАГ 2: Настройка репозитория
echo ----------------------------------------------

cd /d "%~dp0"

echo Инициализация Git...
git init >nul 2>&1
git config user.email "kudryashov20091991@gmail.com"
git config user.name "kudryashov20091991-lang"

echo Создание репозитория...
curl -s -u "kudryashov20091991-lang:%GITHUB_TOKEN%" -X POST https://api.github.com/user/repos ^
  -H "Accept: application/vnd.github.v3+json" ^
  -d "{\"name\":\"che168-parser\",\"private\":false,\"auto_init\":true}" >nul 2>&1
echo Репозиторий создан!

echo Загрузка файлов...
git add che168_parser.py .github/workflows/che168_parse.yml 2>nul
git commit -m "Che168 parser for GitHub Actions" >nul 2>&1
git branch -M main >nul 2>&1

git remote remove origin >nul 2>&1
git remote add origin https://github.com/kudryashov20091991-lang/che168-parser.git

git push -u origin main >nul 2>&1
echo Файлы загружены!

echo.
echo ============================================================
echo ГОТОВО!
echo ============================================================
echo.
echo Откройте: https://github.com/kudryashov20091991-lang/che168-parser/actions
echo Нажмите: Che168 Parser -> Run workflow
echo.
echo Парсер будет запускаться автоматически каждые 6 часов!
echo Результат скачивается из артефактов (che168_result.json)
echo.
pause
