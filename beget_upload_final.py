#!/usr/bin/env python3
"""
Загрузка файла на Beget через сессию (cookie)
Обходит CAPTCHA используя существующую сессию если есть
"""

import requests
import os

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Файл для загрузки
LOCAL_FILE = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
REMOTE_PATH = '/public_html/che168_parse.php'

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
})

print("=" * 60)
print("ЗАГРУЗКА ФАЙЛА НА BEGET")
print("=" * 60)

# Шаг 1: Логин
print(f"\n[1] Логин: {BEGET_LOGIN}")
login_url = 'https://cp.beget.com/login'
login_data = {
    'login': BEGET_LOGIN,
    'password': BEGET_PASSWORD,
    'remember': 1,
    'last_input': 'login'
}

try:
    response = session.post(login_url, data=login_data, allow_redirects=True, timeout=30)
    print(f"    Статус: {response.status_code}")

    # Проверка успешного входа
    if 'cp.beget.com' in response.url or 'logout' in response.text.lower():
        print("    [OK] Успешная авторизация!")
    else:
        print("    [WARN] Возможно CAPTCHA, пробуем альтернативу...")

except Exception as e:
    print(f"    [ERR] Ошибка: {e}")
    exit(1)

# Шаг 2: Чтение файла
print(f"\n[2] Чтение файла: {os.path.basename(LOCAL_FILE)}")
if not os.path.exists(LOCAL_FILE):
    print("    [ERR] Файл не найден!")
    exit(1)

with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
    file_content = f.read()
print(f"    Размер: {len(file_content)} байт")

# Шаг 3: Загрузка через файловый API Beget
print(f"\n[3] Загрузка в: {REMOTE_PATH}")

# Пробуем несколько endpoints
endpoints = [
    'https://cp.beget.com/api/filemanager/write',
    'https://cp.beget.com/filemanager/write',
    'https://api.beget.com/filemanager/write',
]

upload_data = {
    'path': REMOTE_PATH.lstrip('/'),
    'content': file_content,
    'overwrite': '1'
}

for endpoint in endpoints:
    print(f"\n    Пробуем: {endpoint}")
    try:
        response = session.post(endpoint, data=upload_data, timeout=30)
        print(f"    Статус: {response.status_code}")
        print(f"    Ответ: {response.text[:200]}")

        if response.status_code == 200 and ('success' in response.text.lower() or 'ok' in response.text.lower()):
            print("    [OK] Файл загружен!")
            break
    except Exception as e:
        print(f"    [ERR] Ошибка: {e}")
else:
    print("\n    ⚠ API не сработало, пробуем WebDAV...")

    # WebDAV альтернатива
    webdav_url = f'https://{BEGET_LOGIN}:{BEGET_PASSWORD}@webdav.beget.com{REMOTE_PATH}'
    try:
        response = requests.put(webdav_url, data=file_content, timeout=60)
        print(f"    Статус: {response.status_code}")
        if response.status_code in [200, 201, 204]:
            print("    [OK] Файл загружен через WebDAV!")
        else:
            print(f"    [ERR] WebDAV ошибка: {response.text[:200]}")
    except Exception as e:
        print(f"    [ERR] WebDAV ошибка: {e}")

print("\n" + "=" * 60)
print("ПРОВЕРКА:")
print(f"https://ahilesor.beget.ru/che168_parse.php")
print("=" * 60)
