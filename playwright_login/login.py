import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"

async def main():
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(f"Credentials file {CREDENTIALS_FILE} not found")
    creds = json.loads(CREDENTIALS_FILE.read_text())
    username = creds.get("username")
    password = creds.get("password")
    if not username or not password:
        raise ValueError("username and password must be provided in credentials.json")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://serviceteam-witt.kilanka.de")
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')
        print(await page.title())
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
