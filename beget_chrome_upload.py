"""
Загрузка PHP парсера на Beget через Chrome (Selenium)
Обходит проблему с JavaScript авторизацией
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Данные
BEGET_LOGIN = 'ahilesor'
BEGET_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Читаем PHP файл
with open(r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php', 'r', encoding='utf-8') as f:
    php_content = f.read()

print(f"PHP файл: {len(php_content)} байт")
print("=" * 60)
print("ЗАГРУЗКА НА BEGET ЧЕРЕЗ CHROME")
print("=" * 60)

# Настройка Chrome
options = Options()
options.add_argument('--start-maximized')
options.add_argument('--disable-notifications')

print("\n[1] Запуск Chrome...")
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)

try:
    # 2. Авторизация
    print("[2] Авторизация на Beget...")
    driver.get('https://cp.beget.com/login')
    time.sleep(3)

    # Ищем поле логина
    login_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'login'))
    )
    login_input.clear()
    login_input.send_keys(BEGET_LOGIN)

    # Поле пароля
    pass_input = driver.find_element(By.NAME, 'passwd')
    pass_input.clear()
    pass_input.send_keys(BEGET_PASS)

    # Кнопка входа
    submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit_btn.click()

    print("    Ввел логин/пароль, жду перехода...")
    time.sleep(5)

    # 3. Переход в файловый менеджер
    print("[3] Переход в Файловый менеджер...")
    driver.get('https://cp.beget.com/filemanager')
    time.sleep(4)

    # 4. Переход в public_html
    print("[4] Открытие public_html...")
    try:
        # Ищем папку public_html в списке
        folders = driver.find_elements(By.CSS_SELECTOR, '[data-name="public_html"], .file-manager-item[data-name="public_html"]')
        if folders:
            folders[0].click()
            time.sleep(2)
            print("    public_html открыта")
        else:
            print("    Папка не найдена, пробую напрямую...")
            driver.get('https://cp.beget.com/filemanager/public_html')
            time.sleep(3)
    except Exception as e:
        print(f"    Ошибка: {e}")
        driver.get('https://cp.beget.com/filemanager/public_html')
        time.sleep(3)

    # 5. Создание файла
    print("[5] Создание файла che168_parse.php...")

    # Пробуем найти кнопку "Создать" или "+"
    try:
        create_btn = driver.find_element(By.CSS_SELECTOR, 'button[title="Создать"], .btn-create, [data-action="create"]')
        create_btn.click()
        time.sleep(1)

        # Выбираем "Файл"
        file_option = driver.find_element(By.XPATH, "//span[contains(text(), 'Файл')]")
        file_option.click()
        time.sleep(2)
    except:
        print("    Кнопка создания не найдена, пробую альтернативу...")

    # 6. Ввод имени файла
    print("[6] Ввод имени файла...")
    try:
        name_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="имя"], input[name="name"]')
        name_input.clear()
        name_input.send_keys('che168_parse.php')
        time.sleep(1)

        # OK
        ok_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Создать')]")
        ok_btn.click()
        time.sleep(3)
    except Exception as e:
        print(f"    Ошибка создания: {e}")

    print("\n" + "=" * 60)
    print("ДАЛЬШЕ ВРУЧНУЮ (2 клика):")
    print("1. Дважды кликни на che168_parse.php в списке")
    print("2. Вставь содержимое и нажми Сохранить")
    print(f"\nФайл для копирования: che168_beget_final.php")
    print("=" * 60)

except Exception as e:
    print(f"\nОШИБКА: {e}")

finally:
    print("\nChrome открыт. Не закрывай браузер!")
    input("Нажми Enter когда загрузишь файл...")
    driver.quit()
