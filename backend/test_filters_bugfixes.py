import asyncio
from playwright.async_api import async_playwright
import os, subprocess, time, signal

async def main():
    print("Starting backend...")
    os.chdir("../backend")
    proc = subprocess.Popen(["../venv/bin/uvicorn", "main:app", "--port", "8000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            url = f"file://{os.path.abspath('../frontend/index.html')}"
            print("Navigating to", url)
            await page.goto(url)
            
            await page.wait_for_selector("#habits-list .habit-item")
            
            # Step 1: Open Logbook
            print("Verify Logbook Opens...")
            await page.click("button:has-text('Logbook')")
            await page.wait_for_timeout(1000)
            
            # Note down if it's visible
            is_visible = await page.is_visible("[id^=logbook-body-]")
            print(f"Logbook Visible: {is_visible}")
            
            # Step 2: Trigger a re-render by changing the filter (which was causing logbook to vanish)
            print("Changing main filter to trigger fetchHabits (which previously collapsed the logbook)")
            await page.select_option("#habit-filter", index=1)
            await page.wait_for_timeout(1000)
            
            # Check if logbook is STILL visible
            is_visible_after = await page.is_visible("[id^=logbook-body-]")
            print(f"Logbook Visible After Filter Change (Bug Fix Test): {is_visible_after}")
            
            # Step 3: Test Timescale select
            print("Testing timescale select filter")
            await page.select_option("#timescale-filter", value="day")
            print("Successfully updated timescale to 'day'")
            
            await browser.close()
    finally:
        os.kill(proc.pid, signal.SIGTERM)
        print("Backend killed")

asyncio.run(main())
