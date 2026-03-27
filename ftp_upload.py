"""
Загрузка на Beget через FTP
"""

import ftplib
import os

FTP_HOST = 'ftp.beget.com'
FTP_USER = 'ahilesor'
FTP_PASS = r'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'

# Путь к файлу
local_file = r'C:\Users\MSI\Desktop\Клауд\Курсор\Автосайты\Парсеры\che168_beget_final.php'
remote_file = '/public_html/che168_parse.php'

print("=" * 60)
print("ЗАГРУЗКА НА BEGET ЧЕРЕЗ FTP")
print("=" * 60)

try:
    print("\n[1] Подключение к FTP...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("    УСПЕШНО!")

    print("\n[2] Переход в public_html...")
    ftp.cwd('/public_html')
    print("    Текущая папка:", ftp.pwd())

    print("\n[3] Загрузка файла...")
    with open(local_file, 'rb') as f:
        ftp.storbinary(f'STOR {os.path.basename(remote_file)}', f)
    print("    УСПЕШНО!")

    print("\n[4] Проверка...")
    files = ftp.nlst()
    if 'che168_parse.php' in files:
        print("    Файл на сервере!")
    else:
        print("    Файл не найден в списке")

    ftp.quit()

    print("\n=== ГОТОВО! ===")
    print("URL: https://ahilesor.beget.ru/che168_parse.php")

except Exception as e:
    print(f"\nОШИБКА: {e}")
    print("\nFTP не доступен — загрузи вручную через https://sprutio.beget.com/")
