"""
Загрузка файлов на Beget через FTP
"""
import ftplib
import os

FTP_HOST = 'ftp.beget.com'
FTP_USER = 'ahilesor'
FTP_PASS = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Файлы для загрузки
files_to_upload = [
    'che168_parser.php',
]

try:
    print("Подключение к FTP Beget...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("Успешно!")

    # Список файлов
    ftp.retrlines('LIST')

    # Загрузка
    for filename in files_to_upload:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            print(f"\nЗагрузка {filename}...")
            with open(filepath, 'rb') as f:
                ftp.storbinary(f'STOR {filename}', f)
            print(f"  Готово!")
        else:
            print(f"  Файл не найден: {filepath}")

    ftp.quit()
    print("\nВсе файлы загружены!")

except Exception as e:
    print(f"Ошибка: {e}")
