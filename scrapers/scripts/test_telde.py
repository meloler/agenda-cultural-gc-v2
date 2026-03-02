import asyncio
from playwright.async_api import async_playwright
from app.scrapers.telde_cultura import scrape_telde_cultura

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Solo una página para no tardar
        results = await scrape_telde_cultura(page)
        for e in results[:5]:
            print(f"EVENTO: {e.nombre} | URL: {e.url_venta} | FECHA: {e.fecha_iso} | PRECIO: {e.precio_num} | HORA: {e.hora}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
