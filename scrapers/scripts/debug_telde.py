import asyncio
from playwright.async_api import async_playwright
from app.scrapers.telde_cultura import scrape_telde_cultura
from app.scrapers._enrichment import extraer_datos_duros, enriquecer_evento

async def debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        url = "https://teldecultura.org/events/broadway-jazz-45"
        await page.goto(url)
        
        # Log JSON-LD
        import json
        import re
        html = await page.content()
        matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        for m in matches:
            print("JSON-LD found:", m[:200])
            try:
                data = json.loads(m)
                if isinstance(data, list):
                    for d in data:
                        if "offers" in d:
                            print("OFFERS:", d["offers"])
                elif "offers" in data:
                    print("OFFERS:", data["offers"])
            except:
                pass
                
        # Also print what selectors return for price
        sel_prices = await page.locator(".em-item-meta-line, .em-event-price, .precio, .price, .fee").all_inner_texts()
        print("CSS SELECTORS FOR PRICE:", sel_prices)        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug())
