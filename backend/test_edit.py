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
        
        # Click the edit button
        print("Clicking Edit button")
        await page.click("button:has-text('Edit')")
        
        await page.wait_for_selector("#edit-habit-modal")
        
        # Ensure modal inputs populated
        name = await page.input_value("#edit-habit-name")
        print(f"Modal populated with habit name: {name}")
        
        # Close the modal
        await page.click("button:has-text('Cancel')")
        
        print("Done")
        
        await browser.close()

asyncio.run(main())
