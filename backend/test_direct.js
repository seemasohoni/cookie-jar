const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.new_page();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err));
  await page.goto('file://' + __dirname + '/../frontend/index.html');
  await page.waitForSelector('.habit-item');
  await page.click('button:has-text("Logbook")');
  await page.waitForTimeout(2000);
  await browser.close();
})();
