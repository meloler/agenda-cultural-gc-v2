"""
Scraper para LocalGuideGranCanaria.com - Agenda de Fin de Semana.

URL: https://localguidegrancanaria.com/planes-en-gran-canaria/

Estructura DOM:
  - Post semanal en WordPress (se actualiza el mismo post en vez de crear nuevos).
  - Los eventos NO están en contenedores individuales (.card).
  - Son siblings directos dentro de `.entry-content`.
  - El patrón es secuencial:
      1. <h3>Título del evento</h3>
      2. <ul class="wp-block-list">
         <li>📍 Lugar</li>
         <li>🗓️ Fecha (texto libre: "Del 14 al 16 de marzo")</li>
         <li>⏰ Hora</li>
      3. <figure><img></figure> o <div class="wp-block-image"><img></div>
      4. Links (a veces)
"""

import asyncio
import re
from playwright.async_api import Page
from app.models import Evento
from app.utils.text_processing import categorizar_pro, limpiar_texto
from app.utils.parsers import _parsear_fecha, _parsear_hora, _parsear_precio, _validar_imagen


async def scrape_localguide_gc(page: Page) -> list[Evento]:
    """Extrae eventos del artículo de agenda recorriendo el DOM secuencialmente."""
    print("🌴 LocalGuideGranCanaria.com...")
    eventos: list[Evento] = []
    
    url_base = "https://localguidegrancanaria.com/planes-en-gran-canaria/"

    try:
        await page.goto(
            url_base,
            wait_until="domcontentloaded",
            timeout=25000,
        )
        await asyncio.sleep(2)

        # Hacer algo de scroll para lazy load images si las hubiera
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(0.5)

        # Extraer mediante iteración secuencial de DOM
        # Recogemos bloques entre H3s
        items_raw = await page.evaluate("""
            () => {
                const results = [];
                const container = document.querySelector('.entry-content');
                if (!container) return results;

                const nodes = Array.from(container.children);
                let currentEvent = null;

                for (const node of nodes) {
                    // Si encontramos un H3, abrimos un NUEVO evento
                    if (node.tagName === 'H3') {
                        // Limpiar el 1. 2. 3. que suelen poner en los H3
                        let titulo = node.textContent.trim();
                        titulo = titulo.replace(/^\\d+\\.\\s*/, '').trim();
                        
                        // Si el h3 es "Conclusión" o cosas similares, lo ignoramos y dejamos de guardar en currentEvent
                        if (titulo.toLowerCase().includes('suscríbete') || 
                            titulo.toLowerCase().includes('conclusión') ||
                            titulo.length < 4) {
                            currentEvent = null;
                            continue;
                        }

                        currentEvent = {
                            titulo: titulo,
                            luga_raw: "",
                            fecha_raw: "",
                            hora_raw: "",
                            precio_raw: "",
                            imagen_url: null,
                            links: []
                        };
                        results.push(currentEvent);
                        continue;
                    }

                    // Si estamos acumulando datos para un evento (después de un H3)
                    if (currentEvent) {
                        // Extraer de listas con emojis
                        if (node.tagName === 'UL' || node.classList.contains('wp-block-list')) {
                            const lis = node.querySelectorAll('li');
                            for (const li of lis) {
                                const text = li.textContent.trim();
                                const html = li.innerHTML;
                                
                                const hasEmoji = (char) => html.includes(char) || (li.querySelector(`img[alt*="${char}"]`) !== null);

                                if (hasEmoji('📍')) {
                                    currentEvent.luga_raw = text.replace(/^[:\\s]+|[:\\s]+$/g, '');
                                }
                                else if (hasEmoji('🗓') || hasEmoji('📆')) {
                                    currentEvent.fecha_raw = text.replace(/^[:\\s]+|[:\\s]+$/g, '');
                                }
                                else if (hasEmoji('⏰') || hasEmoji('⏱')) {
                                    currentEvent.hora_raw = text.replace(/^[:\\s]+|[:\\s]+$/g, '');
                                }
                                else if (hasEmoji('💶') || text.toLowerCase().includes('precio')) {
                                    currentEvent.precio_raw = text.replace(/^[:\\s]+|[:\\s]+$/g, '');
                                }
                                else {
                                    // Comprobar si hay precio oculto en otros items
                                    const lower = text.toLowerCase();
                                    if (lower.includes('gratuita') || lower.includes('gratis') || lower.includes('entrada libre') || text.includes('€')) {
                                        currentEvent.precio_raw = text;
                                    }
                                }
                            }
                        }
                        
                        // Extraer imagen
                        if (node.tagName === 'FIGURE' || node.classList.contains('wp-block-image')) {
                            const img = node.querySelector('img');
                            if (img && !currentEvent.imagen_url) {
                                currentEvent.imagen_url = img.src || img.dataset.src;
                            }
                        }
                        // Específico para sus links que a veces están sueltos en un P
                        if (node.tagName === 'P') {
                            const img = node.querySelector('img');
                            if (img && !currentEvent.imagen_url) {
                                currentEvent.imagen_url = img.src || img.dataset.src;
                            }
                        }

                        // Extraer links sueltos (botones de comprar o info)
                        const links = node.querySelectorAll('a');
                        for (const a of links) {
                            const href = a.href;
                            if (href && href !== '#' && href.includes('http')) {
                                currentEvent.links.push({t: a.textContent.trim().substring(0,20), u: href});
                            }
                        }
                    }
                }
                
                return results;
            }
        """)

        print(f"   -> {len(items_raw)} bloques de eventos detectados.")

        for item in items_raw:
            titulo = limpiar_texto(item.get("titulo", ""))
            if not titulo or len(titulo) < 3:
                continue

            # Fechas en español tipo "Del 23 al 25 de mayo"
            fecha_raw = limpiar_texto(item.get("fecha_raw", ""))
            fecha_iso = _parsear_fecha(fecha_raw)

            # Si la fecha no se parsea bien con _parsear_fecha (porque tiene "Del ... al ...")
            # Extraemos el úlitmo día y mes. Ej: "Del 20 al 23 de marzo" -> 23 de marzo
            if not fecha_iso and fecha_raw:
                try:
                    # Intento de extracción de último día del rango
                    m = re.search(r'(?:al|y)\s+(\d{1,2})\s+de\s+([a-zA-Z]+)', fecha_raw.lower())
                    if m:
                        art_fake = f"{m.group(1)} de {m.group(2)}"
                        fecha_iso = _parsear_fecha(art_fake)
                except:
                    pass

            hora = _parsear_hora(item.get("hora_raw", ""))
            precio_num = _parsear_precio(item.get("precio_raw", ""))
            
            # Lugar (a veces dicen "Varios lugares")
            lugar = limpiar_texto(item.get("luga_raw", ""))
            if not lugar:
                lugar = "Gran Canaria"

            # URL de Venta/Info (priorizar ticketing)
            url_evento = url_base
            links = item.get("links", [])
            for link in links:
                u = link.get("u", "").lower()
                if any(tk in u for tk in ["tickety", "tomaticket", "entrees", "entradas.com", "ticketmaster", "compra", "tureservaonline"]):
                    url_evento = link.get("u")
                    break
            # Si no hay de ticketing, agarramos el primero que no sea el propio blog
            if url_evento == url_base and links:
                for link in links:
                    if "localguidegrancanaria.com" not in link.get("u"):
                        url_evento = link.get("u")
                        break

            # Limpiar img
            imagen_final = _validar_imagen(item.get("imagen_url"))

            eventos.append(
                Evento(
                    nombre=titulo,
                    lugar=lugar[:200],
                    fecha_raw=fecha_raw[:100] if fecha_raw else "Sin fecha",
                    fecha_iso=fecha_iso,
                    precio_num=precio_num,
                    hora=hora,
                    organiza="LocalGuideGC",
                    url_venta=url_evento,
                    imagen_url=imagen_final,
                    estilo=categorizar_pro(titulo, "LocalGuideGC")
                )
            )

            # Log
            if fecha_iso:
                print(f"      ✅ {titulo[:50]}: {fecha_iso} {hora or '?'} | {lugar[:30]}...")
            else:
                print(f"      ⚠️ {titulo[:50]}: sin fecha parseable ({fecha_raw})")

        con_precio = sum(1 for e in eventos if e.precio_num is not None)
        con_fecha = sum(1 for e in eventos if e.fecha_iso)
        print(f"   -> LocalGuideGC: {len(eventos)} eventos extraídos (precio:{con_precio} fecha:{con_fecha})")

    except Exception as e:
        print(f"   ❌ Error LocalGuideGC: {e}")

    return eventos
