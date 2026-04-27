import asyncio
from playwright.async_api import async_playwright
import os, subprocess, time, signal

async def main():
    # Start Backend
    print("Starting backend...")
    os.chdir("../backend")
    proc = subprocess.Popen(["../venv/bin/uvicorn", "main:app", "--port", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2) # Give it a second to start
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
            page.on("pageerror", lambda err: print(f"JS ERROR: {err}"))
            
            url = f"file://{os.path.abspath('../frontend/index.html')}"
            print("Navigating to", url)
            await page.goto(url)
            
            await page.wait_for_selector("#habits-list .habit-item")
            
            print("Changing habit filter...")
            await page.select_option("#habit-filter", index=1)
            await page.wait_for_timeout(1000)
            
            print("Clicking Logbook button...")
            await page.click("button:has-text('Logbook')")
            
            await page.wait_for_timeout(2000)
            logbook_html = await page.evaluate("() => document.querySelector('[id^=logbook-body-]').innerHTML")
            print(f"Logbook body: {logbook_html}")
            
            await browser.close()
    finally:
        os.kill(proc.pid, signal.SIGTERM)
        print("Backend killed")

asyncio.run(main())
