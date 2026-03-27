#!/usr/bin/env python3
"""
Запуск парсера на Beget через curl
"""

import requests
import time

print("=" * 60)
print("ЗАПУСК ПАРСЕРА CHE168 НА BEGET")
print("=" * 60)

# URL парсера на Beget
parse_url = 'https://ahilesor.beget.ru/che168_parse.php'

print(f"\nURL: {parse_url}")
print("Ожидание запуска PHP (может занять до 2 минут)...")

# Пробуем открыть страницу парсера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

try:
    response = requests.get(parse_url, headers=headers, timeout=120)
    print(f"\nСтатус HTTP: {response.status_code}")
    print(f"Размер ответа: {len(response.text)} байт")

    # Сохраняем результат
    with open('parse_result.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("\n[OK] Результат сохранен в parse_result.html")

    # Показываем первые 2000 символов
    print("\n" + "=" * 60)
    print("ОТЧЕТ (первые 2000 символов):")
    print("=" * 60)
    print(response.text[:2000])

except requests.exceptions.Timeout:
    print("\n[WARN] Таймаут - парсер работает (ждём результат)")
    print("Откройте вручную: https://ahilesor.beget.ru/che168_parse.php")
except Exception as e:
    print(f"\n[ERR] Ошибка: {e}")
    print("\nПопробуйте открыть вручную:")
    print("https://ahilesor.beget.ru/che168_parse.php")
