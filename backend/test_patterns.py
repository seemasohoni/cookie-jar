import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        url = f"file://{os.path.abspath('../frontend/index.html')}"
        print("Navigating to", url)
        await page.goto(url)
        
        await page.wait_for_selector("#habits-list .habit-item")
        
        # Log a habit to generate pattern data
        print("Clicking Log button")
        await page.click("button.btn-sm")
        
        await page.wait_for_selector("#log-modal")
        
        print("Setting trigger to CUSTOM and value to 'Listening to Song'")
        await page.select_option("#log-trigger", "CUSTOM")
        await page.fill("#log-trigger-custom", "Listening to Song")
        
        await page.click("button:has-text('Save Log')")
        await page.wait_for_timeout(2000)
        
        print("Done")
        
        await browser.close()

asyncio.run(main())
