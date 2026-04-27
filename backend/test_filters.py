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
        
        await page.wait_for_selector("#habit-filter option")
        
        print("Selecting second option in the Habit Filter")
        dropdown = page.locator("#habit-filter")
        
        options = await dropdown.locator("option").all_inner_texts()
        print("Available habits:", options)
        
        if len(options) > 1:
            await dropdown.select_option(label=options[1])
            await page.wait_for_timeout(1000)
            print("Filter selected:", options[1])
        else:
            print("No habits to filter test against.")
            
        print("Done")
        await browser.close()

asyncio.run(main())
