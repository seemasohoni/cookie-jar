import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Start server
        import subprocess
        import time
        server = subprocess.Popen(["venv/bin/uvicorn", "main:app", "--port", "8000"])
        time.sleep(2)
        
        try:
            # File URL
            url = f"file://{os.path.abspath('../frontend/index.html')}"
            print("Navigating to", url)
            await page.goto(url)
            
            # Wait for initial load
            await page.wait_for_selector("#habits-list .habit-item")
            print("Initial habits loaded.")
            
            # Create a new habit
            await page.fill("#new-habit-name", "Drink Water")
            await page.select_option("#new-habit-category", "GOOD")
            
            # Intercept request
            async with page.expect_response("**/habits") as response_info:
                await page.click("button[type='submit']")
            
            response = await response_info.value
            print("POST /habits response:", response.status)
            
            await page.wait_for_timeout(1000)
            
            # Check if it rendered
            content = await page.content()
            if "Drink Water" in content:
                print("SUCCESS: Drink Water rendered on dashboard")
            else:
                print("FAIL: Drink Water not found on dashboard")
                
            # Log any console messages
            messages = []
            page.on("console", lambda msg: messages.append(msg.text))
            
        finally:
            server.terminate()
            await browser.close()

asyncio.run(main())
