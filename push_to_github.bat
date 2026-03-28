@echo off
chcp 65001 >nul
echo ============================================================
echo ПУШ ПАРСЕРА НА GITHUB
echo ============================================================
echo.
echo Введите ваш логин GitHub (например: ahilesor):
set /p GITHUB_LOGIN=

echo.
echo Введите имя репозитория (например: che168-parser):
set /p REPO_NAME=

echo.
echo Настройка Git...
cd /d "%~dp0"
git config user.email "kudryashov20091991@gmail.com"
git config user.name "ahilesor"

echo.
echo Подключение удаленного репозитория...
git remote remove origin 2>nul
git remote add origin https://github.com/%GITHUB_LOGIN%/%REPO_NAME%.git

echo.
echo Переименование ветки в main...
git branch -M main

echo.
echo Пуш на GitHub...
echo Если запросит пароль - используйте Personal Access Token:
echo https://github.com/settings/tokens
echo.
git push -u origin main

echo.
echo ============================================================
echo ГОТОВО!
echo ============================================================
echo.
echo Теперь откройте:
echo https://github.com/%GITHUB_LOGIN%/%REPO_NAME%/actions
echo.
echo Нажмите Enter для выхода...
pause >nul
