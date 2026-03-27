"""
Выгрузка спарсенных автомобилей с che168.com на сайт luchshie-yaponskie-avto.ru
"""

import ftplib
import json
from pathlib import Path
from datetime import datetime

# FTP доступ
FTP_HOST = 'luchshie-yaponskie-avto.ru'
FTP_USER = 'ahilesor'
FTP_PASS = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`'
FTP_PATH = '/luchshie-yaponskie-avto.ru/public_html/wp-content/themes/autoimport-theme/'

# Файлы для выгрузки
PARSER_DIR = Path(__file__).parent
JSON_FILE = PARSER_DIR / 'che168_cars_15.json'
HTML_FILE = PARSER_DIR / 'che168_cars_15.html'

def generate_php_array(cars):
    """Генерирует PHP массив с данными для импорта"""
    php_code = "<?php\n// Автомобили из Китая (che168.com)\n// Выгружено: " + datetime.now().strftime("%d.%m.%Y %H:%M") + "\n\n$che168_cars = [\n"

    for car in cars:
        php_code += f"""    [
        'id' => {car['id']},
        'title' => "{car['title_ru'].replace('"', '\\"')}",
        'title_original' => "{car['title_original'].replace('"', '\\"')}",
        'price_cny' => {car['price_cny']},
        'price_rub' => {car['price_rub']},
        'mileage_km' => {car['mileage_km']},
        'year' => {car['year']},
        'image' => "{car['image']}",
        'location' => "{car['location']}",
    ],
"""

    php_code += "];\n"
    return php_code

def upload_to_ftp():
    """Загружает файлы на сайт"""
    print("=" * 60)
    print("ВЫГРУЗКА CHE168.COM НА САЙТ")
    print("=" * 60)

    # Проверяем наличие файлов
    if not JSON_FILE.exists():
        print(f"Ошибка: Файл {JSON_FILE} не найден!")
        return False

    # Читаем JSON
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cars = data.get('cars', [])
    print(f"\nЗагружено автомобилей из JSON: {len(cars)}")

    # Генерируем PHP файл
    php_content = generate_php_array(cars)
    php_file = PARSER_DIR / 'che168_cars_data.php'
    with open(php_file, 'w', encoding='utf-8') as f:
        f.write(php_content)
    print(f"Сгенерирован PHP файл: {php_file}")

    # Подключаемся к FTP
    try:
        print(f"\nПодключение к FTP: {FTP_HOST}...")
        ftp = ftplib.FTP(FTP_HOST)
        ftp.set_pasv(True)
        ftp.login(FTP_USER, FTP_PASS)
        print("Успешно подключено!")

        # Переходим в директорию темы
        ftp.cwd('/luchshie-yaponskie-avto.ru/public_html/wp-content/themes/autoimport-theme/')

        # Загружаем PHP файл с данными
        print(f"\nЗагрузка che168_cars_data.php...")
        with open(php_file, 'rb') as f:
            ftp.storbinary('STOR che168_cars_data.php', f)
        print("Загружено!")

        # Загружаем HTML файл (для просмотра)
        print(f"Загрузка che168_cars_15.html...")
        with open(HTML_FILE, 'rb') as f:
            ftp.storbinary('STOR che168_cars_15.html', f)
        print("Загружено!")

        # Загружаем JSON файл (для резервной копии)
        print(f"Загрузка che168_cars_15.json...")
        with open(JSON_FILE, 'rb') as f:
            ftp.storbinary('STOR che168_cars_15.json', f)
        print("Загружено!")

        ftp.quit()

        print("\n" + "=" * 60)
        print("ВЫГРУЗКА ЗАВЕРШЕНА!")
        print("=" * 60)
        print("\nФайлы на сайте:")
        print("  - /wp-content/themes/autoimport-theme/che168_cars_data.php")
        print("  - /wp-content/themes/autoimport-theme/che168_cars_15.html")
        print("  - /wp-content/themes/autoimport-theme/che168_cars_15.json")
        print("\nДля отображения на сайте добавьте в functions.php:")
        print("  include get_template_directory() . '/che168_cars_data.php';")

        return True

    except Exception as e:
        print(f"\nОшибка FTP: {e}")
        return False

if __name__ == "__main__":
    upload_to_ftp()
