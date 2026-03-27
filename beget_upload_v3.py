"""
Загрузка на Beget через правильный формат авторизации
"""
import requests

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем файл
script_path = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Origin': 'https://cp.beget.com',
    'Referer': 'https://cp.beget.com/',
})

# 1. Авторизация через основную форму
print("Шаг 1: Авторизация...")
auth_url = 'https://cp.beget.com/auth'
auth_data = {'login': API_USER, 'passwd': API_PASS, 'remember': '1'}

resp = session.post(auth_url, data=auth_data, allow_redirects=True, timeout=30)
print(f"  Status: {resp.status_code}")
print(f"  URL после: {resp.url}")
print(f"  Cookies: {list(session.cookies.keys())}")

# 2. Проверка авторизации
print("\nШаг 2: Проверка...")
check = session.get('https://cp.beget.com/bulk/isalive', timeout=10)
print(f"  Status: {check.status_code}")
print(f"  Content: {check.text[:100]}")

# 3. Загрузка файла через FileManager
print("\nШаг 3: Загрузка файла...")

# Сначала получаем токен/список файлов
list_resp = session.get('https://cp.beget.com/filemanager/list', params={'path': '/public_html'}, timeout=15)
print(f"  List status: {list_resp.status_code}")

# Запись файла
write_url = 'https://cp.beget.com/filemanager/edit'
write_data = {
    'path': '/public_html/che168_parse.php',
    'content': content,
    'charset': 'utf-8',
    'action': 'edit'
}

write_resp = session.post(write_url, data=write_data, timeout=30)
print(f"  Write status: {write_resp.status_code}")
print(f"  Response: {write_resp.text[:300]}")

if write_resp.status_code == 200 or 'ok' in write_resp.text.lower():
    print("\n=== УСПЕШНО! ===")
    print("URL: https://ahilesor.beget.ru/che168_parse.php")
else:
    print("\n=== ОШИБКА ===")
    print("Нужно загрузить вручную через https://cp.beget.com")
