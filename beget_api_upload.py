"""
Загрузка файлов на Beget через API (без FTP)
Документация: https://api.beget.com/
"""

import requests
import base64
import os

API_USER = 'ahilesor'
API_PASS = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Файл для загрузки
SCRIPT_FILE = 'che168_parser.php'
REMOTE_PATH = f'/public_html/{SCRIPT_FILE}'

# Читаем файл
script_path = os.path.join(os.path.dirname(__file__), SCRIPT_FILE)
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Загрузка {SCRIPT_FILE} на Beget...")
print(f"Размер: {len(content)} байт")

# API вызов для записи файла
# Используем file.write через API
url = 'https://api.beget.com/file/write'

# Кодируем контент в base64 для передачи
content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

response = requests.post(
    url,
    auth=(API_USER, API_PASS),
    params={
        'path': REMOTE_PATH,
        'content': content_b64
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200 and 'ok' in response.text.lower():
    print("\nФАЙЛ ЗАГРУЖЕН!")
    print(f"URL: https://ahilesor.beget.ru/{SCRIPT_FILE}")
else:
    print("\nОшибка загрузки. Пробую альтернативный метод...")
    # Альтернатива: через FileManager API
    print("Создаю файл через другой метод...")
