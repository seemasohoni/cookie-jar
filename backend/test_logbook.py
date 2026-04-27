import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page Error: {err}"))
        
        url = f"file://{os.path.abspath('../frontend/index.html')}"
        print("Navigating to", url)
        await page.goto(url)
        
        await page.wait_for_selector("#habits-list .habit-item")
        
        # Click the Logbook button
        print("Clicking Logbook button")
        await page.click("button:has-text('Logbook')")
        
        # Wait a bit
        await page.wait_for_timeout(2000)
        
        log_text = await page.locator("[id^=logbook-body-]").first.inner_text()
        print(f"Logbook Text: {log_text}")
        
        await browser.close()

asyncio.run(main())
