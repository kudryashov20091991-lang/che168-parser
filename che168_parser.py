#!/usr/bin/env python3
"""
Che168 parser for GitHub Actions
Uses Playwright to execute JavaScript and bypass anti-bot
"""
import json, os, time
from datetime import datetime

PROXIES = [
    {"server": "http://45.32.56.105:13851", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13852", "username": "Ek0G8F", "password": "GR0Fhj"},
    {"server": "http://45.32.56.105:13853", "username": "Ek0G8F", "password": "GR0Fhj"},
]

def parse_with_playwright():
    """Use Playwright to render the page with JavaScript"""
    cars = []
    results = []
    debug_html = ""

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ])

            for proxy_cfg in PROXIES:
                if len(cars) >= 10:
                    break

                result = {"proxy": proxy_cfg["server"], "url": "https://www.che168.com/beijing/", "status": "error", "error": ""}

                try:
                    context = browser.new_context(
                        proxy=proxy_cfg,
                        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        locale='zh-CN',
                        viewport={'width': 1920, 'height': 1080},
                    )
                    page = context.new_page()
                    page.goto("https://www.che168.com/beijing/", wait_until="networkidle", timeout=60000)
                    time.sleep(5)

                    html = page.content()
                    debug_html = html[:50000]

                    prices = page.evaluate('''() => {
                        const prices = [];
                        const selectors = [
                            '[class*="price"]',
                            '[data-price]',
                            '.price',
                            '.car-price'
                        ];
                        selectors.forEach(sel => {
                            document.querySelectorAll(sel).forEach(el => {
                                const text = el.textContent;
                                const match = text.match(/(\\d+\\.?\\d*)\\s*万/);
                                if (match && prices.length < 10) {
                                    prices.push(parseFloat(match[1]));
                                }
                            });
                        });
                        return prices;
                    }''')

                    for p in prices[:10]:
                        cars.append({"price_cny": p * 10000, "price_rub": round(p * 10000 * 13, 2)})

                    result["status"] = "success"
                    context.close()

                except Exception as e:
                    result["error"] = str(e)[:100]

                results.append(result)

                if len(cars) >= 10:
                    break

            browser.close()

    except ImportError:
        result = {"proxy": "playwright", "status": "error", "error": "Playwright not installed"}
        results.append(result)
    except Exception as e:
        result = {"proxy": "playwright", "status": "error", "error": str(e)[:100]}
        results.append(result)

    return cars, results, debug_html

def parse():
    """Main parse function"""
    cars, results, debug_html = parse_with_playwright()
    return cars, results, debug_html

if __name__ == "__main__":
    cars, results, debug_html = parse()
    print(f"Found: {len(cars)} cars")
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "che168.com",
        "proxies_tested": 1,
        "cars_found": len(cars),
        "results": results,
        "cars": cars
    }
    with open("che168_result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Сохраняем debug HTML как артефакт
    if debug_html:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(debug_html)
