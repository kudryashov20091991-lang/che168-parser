"""
Загрузка файла на Beget - финальная версия
"""
import requests
import http.cookiejar

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем файл
script_path = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Файл: {len(content)} байт")

# Создаем сессию с cookie
class NoRedirect(requests.Session):
    def get_redirect_target(self, resp):
        return None

session = NoRedirect()
session.auth = (API_USER, API_PASS)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://cp.beget.com/',
})

# 1. Получаем cookie авторизации
print("Шаг 1: Авторизация...")
auth_url = 'https://cp.beget.com/api/auth/login'
auth_data = f'login={API_USER}&passwd={API_PASS}&remember=1'

try:
    resp = session.post(auth_url, data=auth_data, allow_redirects=False, timeout=30)
    print(f"  Status: {resp.status_code}")
    print(f"  Cookies: {session.cookies.get_dict()}")

    # 2. Проверка
    print("\nШаг 2: Проверка авторизации...")
    check = session.get('https://cp.beget.com/api/bulk/isalive', timeout=10)
    print(f"  Status: {check.status_code}")

    # 3. Загрузка файла
    print("\nШаг 3: Загрузка файла...")
    write_url = 'https://cp.beget.com/api/filemanager/write'
    write_data = f'path=/public_html/che168_parse.php&content={requests.utils.quote(content)}&charset=utf-8'

    write_resp = session.post(write_url, data=write_data, timeout=30)
    print(f"  Status: {write_resp.status_code}")
    print(f"  Response: {write_resp.text[:500]}")

    if write_resp.status_code == 200:
        print("\n=== УСПЕШНО! ===")
        print("Файл загружен: https://ahilesor.beget.ru/che168_parse.php")
        print("Запусти в браузере для парсинга!")
    else:
        print("\n=== ОШИБКА ===")
        print("Попробуй вручную: https://cp.beget.com -> Файловый менеджер")

except Exception as e:
    print(f"Ошибка: {e}")
