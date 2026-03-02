import asyncio
from playwright.async_api import async_playwright
from app.scrapers.cultura_canaria import scrape_cultura_canaria

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        res = await scrape_cultura_canaria(page, "https://teatroperezgaldos.es", "Teatro Pérez Galdós")
        print("GALDOS:", len(res))
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
