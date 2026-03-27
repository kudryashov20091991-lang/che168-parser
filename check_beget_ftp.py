"""Проверка FTP доступа к Beget"""
from ftplib import FTP

ftp = FTP('ftp.beget.com')
try:
    ftp.login('ahilesor', 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:')
    print("FTP OK!")
    ftp.retrlines('LIST')
    ftp.quit()
except Exception as e:
    print(f"Error: {e}")
