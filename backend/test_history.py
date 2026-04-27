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
        
        # Click the History button
        print("Clicking History button")
        await page.click("button:has-text('History')")
        
        await page.wait_for_selector("#history-modal")
        
        # Verify History Table headers
        table_headers = await page.locator("#history-modal th").all_inner_texts()
        print(f"Table Headers: {table_headers}")
        
        # Close the modal
        await page.click("button:has-text('Close History')")
        
        print("Done")
        
        await browser.close()

asyncio.run(main())
