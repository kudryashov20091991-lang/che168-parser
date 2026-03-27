"""
Загрузка на Beget через сессию API
"""
import requests
import base64
import os

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем файл
script_path = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

session = requests.Session()

# 1. Авторизация
print("Авторизация...")
login_url = 'https://cp.beget.com/auth'
login_data = {
    'login': API_USER,
    'passwd': API_PASS,
    'remember': '1'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://cp.beget.com/',
}

try:
    login_resp = session.post(login_url, data=login_data, headers=headers, timeout=30, allow_redirects=True)
    print(f"Login status: {login_resp.status_code}")
    print(f"Cookies: {session.cookies.get_dict()}")

    # 2. Проверка авторизации
    check_resp = session.get('https://cp.beget.com/bulk/isalive', headers=headers, timeout=10)
    print(f"Auth check: {check_resp.status_code}")

    # 3. Загрузка через FileManager
    # Получаем список файлов сначала
    file_list_url = 'https://cp.beget.com/filemanager/list'
    params = {'path': '/public_html', '_': '1711555000'}

    list_resp = session.get(file_list_url, headers=headers, params=params, timeout=30)
    print(f"File list status: {list_resp.status_code}")
    print(f"Response: {list_resp.text[:500]}")

    # 4. Запись файла
    if list_resp.status_code == 200:
        write_url = 'https://cp.beget.com/filemanager/edit'
        write_data = {
            'path': '/public_html/che168_parse.php',
            'content': content,
            'charset': 'utf-8'
        }

        write_resp = session.post(write_url, data=write_data, headers=headers, timeout=30)
        print(f"Write status: {write_resp.status_code}")
        print(f"Response: {write_resp.text[:300]}")

        if write_resp.status_code == 200:
            print("\nУСПЕШНО ЗАГРУЖЕНО!")
            print("URL: https://ahilesor.beget.ru/che168_parse.php")
        else:
            print("\nОшибка записи. Попробуй вручную через https://cp.beget.com")

except Exception as e:
    print(f"Ошибка: {e}")
