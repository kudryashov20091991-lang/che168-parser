/**
 * Загрузка на Beget через Puppeteer (Node.js)
 */

const puppeteer = require('puppeteer-core');

const BEGET_LOGIN = 'ahilesor';
const BEGET_PASS = 'TezCl3fcQ3$]bfsIV_DHRVDJBJO[&;XRKT49-_3*e#:';

const fs = require('fs');
const path = require('path');

const phpFile = path.join(__dirname, 'che168_beget_final.php');
const phpContent = fs.readFileSync(phpFile, 'utf-8');

console.log(`PHP файл: ${phpContent.length} байт`);
console.log('='.repeat(60));
console.log('ЗАГРУЗКА НА BEGET ЧЕРЕZ PUPPETEER');
console.log('='.repeat(60));

(async () => {
    let browser;

    try {
        // Подключение к существующему Chrome или запуск нового
        console.log('\n[1] Запуск браузера...');

        try {
            // Пробуем подключиться к существующему
            browser = await puppeteer.connect({
                browserURL: 'http://localhost:9222',
                defaultViewport: null
            });
            console.log('    Подключено к существующему Chrome');
        } catch (e) {
            // Запускаем новый
            browser = await puppeteer.launch({
                headless: false,
                args: ['--start-maximized', '--disable-notifications', '--disable-web-security']
            });
            console.log('    Запущен новый Chrome');
        }

        const pages = await browser.pages();
        const page = pages[0];

        await page.setViewport({ width: 1920, height: 1080 });

        // 2. Авторизация
        console.log('[2] Авторизация...');
        await page.goto('https://cp.beget.com/', { waitUntil: 'networkidle0', timeout: 120000 });
        await page.waitForTimeout(10000);

        console.log(`    URL: ${page.url}`);

        // Проверка на страницу логина
        const loginInput = await page.$('input[name="login"]');
        if (loginInput) {
            console.log('    Страница входа, ввожу данные...');
            await page.type('input[name="login"]', BEGET_LOGIN, { delay: 50 });
            await page.type('input[name="passwd"]', BEGET_PASS, { delay: 50 });
            await page.click('button[type="submit"]');
            await page.waitForTimeout(15000);
            console.log(`    URL после входа: ${page.url}`);
        } else {
            console.log('    Уже авторизован!');
        }

        // 3. Файловый менеджер
        console.log('[3] Файловый менеджер...');
        await page.goto('https://cp.beget.com/filemanager', { waitUntil: 'networkidle0', timeout: 120000 });
        await page.waitForTimeout(10000);

        // 4. public_html
        console.log('[4] public_html...');
        try {
            await page.click('[data-name="public_html"]');
            await page.waitForTimeout(3000);
            console.log('    Открыта public_html');
        } catch (e) {
            console.log('    Клик не сработал, пробую URL...');
            await page.goto('https://cp.beget.com/filemanager/public_html', { waitUntil: 'networkidle0', timeout: 120000 });
            await page.waitForTimeout(5000);
        }

        // 5. Создание файла
        console.log('[5] Создание файла che168_parse.php...');
        try {
            // Кнопка создать
            await page.click('button[title="Создать"], .btn-create');
            await page.waitForTimeout(2000);

            // Выбрать файл
            await page.click('text=Файл');
            await page.waitForTimeout(2000);

            // Имя файла
            await page.type('input[placeholder*="имя"], input[name="name"]', 'che168_parse.php');
            await page.waitForTimeout(1000);

            // ОК
            await page.click('button:has-text("OK"), button:has-text("Создать")');
            await page.waitForTimeout(5000);

            console.log('    Файл создан!');
        } catch (e) {
            console.log(`    Ошибка создания: ${e.message}`);
        }

        // 6. Редактирование
        console.log('[6] Редактирование...');
        try {
            await page.click('text=che168_parse.php');
            await page.waitForTimeout(3000);

            // Вставка кода
            console.log('[7] Вставка PHP кода...');
            await page.evaluate((content) => {
                const textarea = document.querySelector('textarea');
                if (textarea) {
                    textarea.value = content;
                    textarea.dispatchEvent(new Event('input', { bubbles: true }));
                    textarea.dispatchEvent(new Event('change', { bubbles: true }));
                }
            }, phpContent);
            await page.waitForTimeout(3000);

            // Сохранение
            console.log('[8] Сохранение...');
            await page.click('button:has-text("Сохранить"), .btn-save');
            await page.waitForTimeout(5000);

            console.log('\n=== УСПЕШНО! ===');
            console.log('URL: https://ahilesor.beget.ru/che168_parse.php');
        } catch (e) {
            console.log(`    Ошибка: ${e.message}`);
            console.log('\nБраузер открыт — загрузи вручную');
        }

        console.log('\nБраузер открыт. Закроется через 30 сек...');
        await page.waitForTimeout(30000);

    } catch (e) {
        console.error(`\nОШИБКА: ${e.message}`);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
})();
