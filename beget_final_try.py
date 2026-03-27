"""
Финальная попытка загрузки на Beget
"""
import requests
from http.cookiejar import CookieJar
import re

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем файл
with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

# Создаем сессию
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
})

# 1. Получаем главную страницу для токенов
print("1. Главная страница...")
resp = session.get('https://cp.beget.com/', timeout=15, allow_redirects=True)
print(f"   Status: {resp.status_code}, URL: {resp.url}")

# 2. Авторизация
print("2. Авторизация...")
auth_resp = session.post(
    'https://cp.beget.com/auth',
    data={'login': API_USER, 'passwd': API_PASS, 'remember': '1'},
    timeout=30,
    allow_redirects=False
)
print(f"   Status: {auth_resp.status_code}")
print(f"   Headers: {dict(auth_resp.headers)}")

# Извлекаем cookie из JS
if 'beget=begetok' in auth_resp.text:
    print("   Cookie найден в JS!")
    session.cookies.set('beget', 'begetok', domain='cp.beget.com', path='/')
    session.cookies.set('BegetCp', auth_resp.cookies.get('BegetCp', 'test'), domain='cp.beget.com', path='/')

print(f"   Cookies: {list(session.cookies.keys())}")

# 3. Проверка
print("3. Проверка авторизации...")
check = session.get('https://cp.beget.com/bulk/isalive', timeout=10)
print(f"   Status: {check.status_code}")
print(f"   URL: {check.url}")

# 4. Загрузка файла
print("4. Загрузка файла...")

# Пробуем разные endpoints
endpoints = [
    ('https://cp.beget.com/filemanager/edit', {'path': '/public_html/che168_parse.php', 'content': content, 'charset': 'utf-8'}),
    ('https://cp.beget.com/api/filemanager/write', {'path': '/public_html/che168_parse.php', 'content': content}),
]

for url, data in endpoints:
    print(f"\n   Пробую: {url}")
    resp = session.post(url, data=data, timeout=30)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.text[:200]}")

    if resp.status_code == 200 and ('ok' in resp.text.lower() or 'success' in resp.text.lower()):
        print("\n=== УСПЕШНО! ===")
        print("URL: https://ahilesor.beget.ru/che168_parse.php")
        break
    elif resp.status_code != 404:
        print("   (не 404, возможно успех)")

print("\nГотово!")
