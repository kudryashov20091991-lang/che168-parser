"""
Загрузка PHP парсера на Beget через API
"""
import requests
import base64
import os

API_USER = 'ahilesor'
API_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Путь к файлу
script_path = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Чтение файла: {len(content)} байт")

# Кодируем в base64
content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

# API Beget для записи файла
url = 'https://api.beget.com/file/write'

print(f"Загрузка на Beget...")
response = requests.post(
    url,
    auth=(API_USER, API_PASS),
    params={
        'path': '/public_html/che168_parse.php',
        'content': content_b64
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\nУСПЕШНО!")
    print("URL для запуска: https://ahilesor.beget.ru/che168_parse.php")
else:
    print("\nОшибка. Пробую через файловый менеджер вручную.")
