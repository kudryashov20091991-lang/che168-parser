"""
Загрузка на Beget с правильным API
"""
import requests
import json

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*',
})

# Авторизация
print("Авторизация...")
session.post('https://cp.beget.com/auth', data={'login': API_USER, 'passwd': API_PASS}, timeout=30)
session.cookies.set('beget', 'begetok', domain='.beget.com', path='/')

# Проверяем
print("Проверка...")
me = session.get('https://api.beget.com/user/info', timeout=10)
print(f"  Status: {me.status_code}")
try:
    print(f"  Response: {me.json()}")
except:
    print(f"  Response: {me.text[:200]}")

# Загрузка через правильный API с session cookie
print("\nЗагрузка файла...")

# Метод 1: Через file.write API
url = 'https://api.beget.com/file/write'
params = {
    'path': f'/beget/ahilesor/public_html/che168_parse.php',
    'content': content
}

resp = session.post(url, params=params, timeout=30)
print(f"  Status: {resp.status_code}")
try:
    print(f"  Response: {resp.json()}")
except:
    print(f"  Response: {resp.text[:300]}")

if resp.status_code == 200:
    print("\n=== УСПЕШНО! ===")
    print("URL: https://ahilesor.beget.ru/che168_parse.php")
else:
    print("\n=== ОШИБКА ===")
    print("Загрузи вручную через https://cp.beget.com -> Файловый менеджер")
    print("Файл готов: che168_beget_final.php")
