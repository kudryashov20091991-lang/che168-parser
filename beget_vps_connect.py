#!/usr/bin/env python3
"""
Подключение к Beget VPS через SFTP
"""

import paramiko
import os

# Данные от VPS Beget
VPS_HOST = 'ahilesor.beget.ru'  # или IP адрес VPS
VPS_USER = 'ahilesor'  # или root
VPS_PASSWORD = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:'
VPS_PORT = 22

print("=" * 60)
print("ПОДКЛЮЧЕНИЕ К BEGET VPS")
print("=" * 60)

try:
    # Создаем SSH клиент
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"\nПодключение к {VPS_HOST}:{VPS_PORT}...")
    client.connect(
        hostname=VPS_HOST,
        port=VPS_PORT,
        username=VPS_USER,
        password=VPS_PASSWORD,
        timeout=10
    )

    print("[OK] Подключено!")

    # Проверка команды
    stdin, stdout, stderr = client.exec_command('hostname && pwd && php -v')

    print("\nРезультат:")
    print(stdout.read().decode())

    if stderr.read().decode():
        print("Ошибки:")
        print(stderr.read().decode())

    client.close()
    print("\n[OK] Отключено")

except FileNotFoundError:
    print("\n[ERR] paramiko не установлен. Выполните: pip install paramiko")
except Exception as e:
    print(f"\n[ERR] Ошибка: {e}")
    print("\nВозможные причины:")
    print("1. Неверный IP/логин/пароль")
    print("2. SSH (порт 22) не доступен на хостинге")
    print("3. Нужен IP адрес VPS (не домен хостинга)")
