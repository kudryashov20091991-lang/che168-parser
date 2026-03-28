#!/usr/bin/env python3
"""
Получение данных VPS через сессию Beget
"""

import requests
from requests.auth import HTTPBasicAuth
import re

BEGET_LOGIN = 'ahilesor'
BEGET_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print("=" * 60)
print("ПОЛУЧЕНИЕ ДАННЫХ VPS")
print("=" * 60)

# Шаг 1: Логин
login_url = 'https://cp.beget.com/login'
login_data = {
    'login': BEGET_LOGIN,
    'password': BEGET_PASSWORD,
    'remember': 1,
    'last_input': 'login'
}

response = session.post(login_url, data=login_data, allow_redirects=True, timeout=30)
print(f"Логин: статус {response.status_code}")

# Шаг 2: Переход на страницу VPS
vps_url = 'https://cp.beget.com/vps'
response = session.get(vps_url, timeout=30)
print(f"VPS страница: статус {response.status_code}")

# Ищем IP адрес в HTML
ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
if ips:
    print(f"\nНайдены IP адреса: {set(ips)}")

# Сохраняем HTML для анализа
with open('vps_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("\nHTML сохранен в vps_page.html")
