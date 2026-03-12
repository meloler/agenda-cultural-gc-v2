import asyncio
from playwright.async_api import async_playwright
from app.scrapers.salan_producciones import scrape_salan_producciones

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        eventos = await scrape_salan_producciones(page)
        for ev in eventos:
            print(f"- {ev.nombre}")
            if ev.url_venta:
                print(f"  URL: {ev.url_venta}")
            print(f"  Desc length: {len(ev.descripcion) if ev.descripcion else 0}")
            print(f"  Desc preview: {ev.descripcion[:150] if ev.descripcion else 'NONE'}")
            print(f"  Organiza: {ev.organiza}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
