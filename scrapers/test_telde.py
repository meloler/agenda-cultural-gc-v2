import asyncio
from playwright.async_api import async_playwright
from app.scrapers.telde_cultura import scrape_telde_cultura

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        res = await scrape_telde_cultura(page)
        print("TELDE:", len(res))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
