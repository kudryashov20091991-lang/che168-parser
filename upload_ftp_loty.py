"""
Загрузка файлов на FTP Beget в раздел /glavnaya-2/loty
"""
import ftplib
import os

FTP_HOST = "luchshie-yaponskie-avto.ru"
FTP_USER = "ahilesor"
FTP_PASS = r"TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:`"
REMOTE_DIR = "/luchshie-yaponskie-avto.ru/public_html/glavnaya-2/loty"

LOCAL_FILES = [
    "che168_30_cars.html",
    "che168_30_cars.json",
]

print("Подключение к FTP...")
ftp = ftplib.FTP(FTP_HOST)
ftp.login(FTP_USER, FTP_PASS)
print("Успешно!")

# Создаем директорию
try:
    ftp.cwd(REMOTE_DIR)
    print(f"Директория существует: {REMOTE_DIR}")
except:
    print(f"Создание директории {REMOTE_DIR}...")
    parts = []
    for part in REMOTE_DIR.split('/'):
        if part:
            parts.append(part)
            path = '/' + '/'.join(parts)
            try:
                ftp.cwd(path)
            except:
                ftp.mkd(path)
                print(f"  Создано: {path}")
    ftp.cwd(REMOTE_DIR)

# Загружаем файлы
for filename in LOCAL_FILES:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        print(f"Загрузка {filename}...")
        with open(filepath, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        print(f"  Успешно!")
    else:
        print(f"  Файл не найден: {filepath}")

ftp.quit()
print("\nГотово!")
print(f"URL: https://luchshie-yaponskie-avto.ru/glavnaya-2/loty/che168_30_cars.html")
