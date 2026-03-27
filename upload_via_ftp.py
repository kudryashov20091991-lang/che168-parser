"""
Выгрузка на сайт через FTP (Beget)
"""

import json
import ftplib
from pathlib import Path
from datetime import datetime

# FTP доступы (Beget)
FTP_HOST = "luchshie-yaponskie-avto.ru"
FTP_USER = "ahilesor"  # Логин от Beget
FTP_PASSWORD = "TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`"  # Пароль от Beget

# Путь для загрузки на сайте
REMOTE_DIR = ""  # Корневая директория FTP

def upload_via_ftp():
    print("=" * 60)
    print("ВЫГРУЗКА ЧЕРЕЗ FTP НА BEGET")
    print("=" * 60)

    # Читаем JSON
    json_file = Path(__file__).parent / "che168_cars_15.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cars = data["cars"]
    print(f"\nЗагружено {len(cars)} автомобилей")

    # Генерируем HTML
    html_content = generate_html(cars)

    # Создаем PHP файл для вставки на сайт
    php_content = generate_php(cars)

    # Подключаемся к FTP
    print(f"\nПодключение к FTP: {FTP_HOST}...")
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)
        print("[OK] Подключено")

        # Переходим в директорию сайта (если указана)
        if REMOTE_DIR:
            ftp.cwd(REMOTE_DIR)
            print(f"[OK] Переход в {REMOTE_DIR}")

        # Список файлов
        files = ftp.nlst()
        print(f"Файлы на сервере: {files[:10]}")

        # Загружаем HTML
        import io
        html_filename = f"che168_cars_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        print(f"\nЗагрузка {html_filename}...")
        html_file = io.BytesIO(html_content.encode('utf-8'))
        ftp.storbinary(f"STOR {html_filename}", html_file)
        print(f"[OK] Загружено")

        # Загружаем PHP
        php_filename = "china_cars_15.php"
        print(f"\nЗагрузка {php_filename}...")
        php_file = io.BytesIO(php_content.encode('utf-8'))
        ftp.storbinary(f"STOR {php_filename}", php_file)
        print(f"[OK] Загружено")

        ftp.quit()

        print(f"\n{'='*60}")
        print("[OK] ВЫГРУЗКА УСПЕШНА!")
        print(f"{'='*60}")
        print(f"Файлы загружены в корень FTP (домашняя директория ahilesor)")
        print(f"URL для просмотра (через временный домен Beget):")
        print(f"  HTML: https://ahilesor.beget.tech/{html_filename}")
        print(f"  PHP:  https://ahilesor.beget.tech/{php_filename}")
        print(f"\nИЛИ через файловый менеджер Beget:")
        print(f"  1. Зайти на https://cp.beget.com")
        print(f"  2. Файловый менеджер -> корневая директория")
        print(f"  3. Переместить файлы в /luchshie-yaponskie-avto.ru/public_html/")

    except Exception as e:
        print(f"[ERROR] Ошибка FTP: {e}")
        print("\nАльтернатива - ручная загрузка через файловый менеджер Beget:")
        print(f"  1. Зайти на https://cp.beget.com")
        print(f"  2. Файловый менеджер -> luchshie-yaponskie-avto.ru")
        print(f"  3. Загрузить файлы:")
        print(f"     - {json_file.parent / 'che168_cars_15.html'}")
        print(f"     - {json_file.parent / 'che168_cars_15.php'}")

def generate_html(cars):
    html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Автомобили из Китая - che168.com</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .car-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
        .car-card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .car-image { width: 100%; height: 200px; object-fit: cover; }
        .car-info { padding: 15px; }
        .car-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
        .car-price { color: #e74c3c; font-size: 18px; font-weight: bold; }
        .car-details { color: #666; font-size: 14px; margin-top: 10px; }
        .car-details div { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Автомобили из Китая (che168.com)</h1>
    <p>Выгружено: """ + datetime.now().strftime("%d.%m.%Y %H:%M") + """</p>

    <div class="car-grid">
"""
    for car in cars:
        html += f"""
        <div class="car-card">
            <img src="{car['image']}" alt="{car['title_ru']}" class="car-image" onerror="this.style.display='none'">
            <div class="car-info">
                <div class="car-title">{car['title_ru']}</div>
                <div class="car-price">{car['price_rub']:,.0f} ₽</div>
                <div class="car-details">
                    <div><b>Год:</b> {car['year']}</div>
                    <div><b>Пробег:</b> {car['mileage_km']:,.0f} км</div>
                    <div><b>Цена в Китае:</b> {car['price_cny']:,.0f} CNY</div>
                    <div><b>Город:</b> {car['location']}</div>
                </div>
            </div>
        </div>
"""
    html += """
    </div>
</body>
</html>
"""
    return html

def generate_php(cars):
    php = """<?php
/**
 * Автомобили из Китая - 15 лотов
 * Для вставки на WordPress сайт через iframe или include
 */
?>
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        .car-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .car-card { border: 1px solid #ddd; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .car-image { width: 100%; height: 200px; object-fit: cover; }
        .car-info { padding: 15px; }
        .car-title { font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50; }
        .car-price { color: #e74c3c; font-size: 18px; font-weight: bold; }
        .car-details { color: #666; font-size: 14px; margin-top: 10px; }
        .car-details div { margin: 5px 0; }
    </style>
</head>
<body>
    <h2>Автомобили из Китая (che168.com)</h2>
    <p>Актуальные предложения - """ + datetime.now().strftime("%d.%m.%Y") + """</p>
    <div class="car-grid">
"""
    for car in cars:
        php += f"""
        <div class="car-card">
            <img src="{car['image']}" alt="{car['title_ru']}" class="car-image" onerror="this.style.display='none'">
            <div class="car-info">
                <div class="car-title">{car['title_ru']}</div>
                <div class="car-price">{car['price_rub']:,.0f} ₽</div>
                <div class="car-details">
                    <div><b>Год:</b> {car['year']}</div>
                    <div><b>Пробег:</b> {car['mileage_km']:,.0f} км</div>
                    <div><b>Цена в Китае:</b> {car['price_cny']:,.0f} CNY</div>
                    <div><b>Город:</b> {car['location']}</div>
                </div>
            </div>
        </div>
"""
    php += """
    </div>
</body>
</html>
"""
    return php

if __name__ == "__main__":
    upload_via_ftp()
