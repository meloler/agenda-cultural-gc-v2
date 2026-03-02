import asyncio
from playwright.async_api import async_playwright
from app.scrapers.cultura_canaria import scrape_cultura_canaria

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Solo una página para no tardar
        results = await scrape_cultura_canaria(page, "https://teatroperezgaldos.es", "Teatro Pérez Galdós")
        for e in results[:3]:
            print(f"EVENTO: {e.nombre} | FECHA: {e.fecha_iso} | PRECIO: {e.precio_num} | HORA: {e.hora}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test())
