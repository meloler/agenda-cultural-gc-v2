"""
Feeds & SEO endpoints — RSS, Sitemap, All Events (for map/calendar).
"""

from __future__ import annotations

import html
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from api.database import get_session
from api.models import Evento

router = APIRouter(tags=["Feeds & SEO"])

SITE_URL = "https://agendaculturalgc.com"


# ---------------------------------------------------------------------------
# GET /api/eventos/all  — All confirmed events (no pagination) for map/calendar
# ---------------------------------------------------------------------------

@router.get("/api/all-eventos", summary="All events (no pagination)")
async def all_eventos(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    """Returns all confirmed future events without pagination.
    Used by map and calendar views."""
    hoy = str(date.today())
    stmt = (
        select(Evento)
        .where(col(Evento.fecha_iso).is_not(None))
        .where(col(Evento.fecha_iso) >= hoy)
        .order_by(col(Evento.fecha_iso).asc())
    )
    result = await session.execute(stmt)
    eventos = result.scalars().all()

    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "lugar": e.lugar,
            "fecha_iso": e.fecha_iso,
            "hora": e.hora,
            "precio_num": e.precio_num,
            "estilo": e.estilo,
            "imagen_url": e.imagen_url,
            "organiza": e.organiza,
            "latitud": e.latitud,
            "longitud": e.longitud,
            "descripcion": e.descripcion,
            "url_venta": e.url_venta,
        }
        for e in eventos
    ]


# ---------------------------------------------------------------------------
# GET /rss.xml  — RSS 2.0 Feed
# ---------------------------------------------------------------------------

def _esc(text: str | None) -> str:
    """Escape XML entities."""
    if not text:
        return ""
    return html.escape(str(text), quote=True)


@router.get("/rss.xml", summary="RSS 2.0 feed")
async def rss_feed(
    session: AsyncSession = Depends(get_session),
) -> Response:
    hoy = str(date.today())
    stmt = (
        select(Evento)
        .where(col(Evento.fecha_iso).is_not(None))
        .where(col(Evento.fecha_iso) >= hoy)
        .order_by(col(Evento.fecha_iso).asc())
        .limit(50)
    )
    result = await session.execute(stmt)
    eventos = result.scalars().all()

    items_xml = ""
    for e in eventos:
        desc = e.descripcion or f"Evento de {e.estilo} en {e.lugar}"
        pub_date = ""
        if e.fecha_iso:
            try:
                dt = datetime.strptime(e.fecha_iso, "%Y-%m-%d")
                pub_date = dt.strftime("%a, %d %b %Y 00:00:00 GMT")
            except ValueError:
                pass

        items_xml += f"""
    <item>
      <title>{_esc(e.nombre)}</title>
      <link>{_esc(e.url_venta)}</link>
      <description>{_esc(desc)}</description>
      <category>{_esc(e.estilo)}</category>
      {f'<pubDate>{pub_date}</pubDate>' if pub_date else ''}
      <guid isPermaLink="false">agcgc-{e.id}</guid>
    </item>"""

    now_rfc = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Agenda Cultural Gran Canaria</title>
    <link>{SITE_URL}</link>
    <description>Todos los eventos culturales de Gran Canaria: conciertos, teatro, cine, humor, danza y mucho más.</description>
    <language>es</language>
    <lastBuildDate>{now_rfc}</lastBuildDate>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    {items_xml}
  </channel>
</rss>"""

    return Response(content=xml, media_type="application/rss+xml; charset=utf-8")


# ---------------------------------------------------------------------------
# GET /sitemap.xml  — Google Sitemap
# ---------------------------------------------------------------------------

@router.get("/sitemap.xml", summary="XML Sitemap for SEO")
async def sitemap(
    session: AsyncSession = Depends(get_session),
) -> Response:
    hoy = str(date.today())
    stmt = (
        select(Evento.id, Evento.nombre, Evento.fecha_iso)
        .where(col(Evento.fecha_iso).is_not(None))
        .where(col(Evento.fecha_iso) >= hoy)
        .order_by(col(Evento.fecha_iso).asc())
    )
    result = await session.execute(stmt)
    rows = result.all()

    urls_xml = f"""
  <url>
    <loc>{SITE_URL}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>{SITE_URL}/#/semana</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{SITE_URL}/#/mapa</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{SITE_URL}/#/calendario</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>"""

    for row in rows:
        urls_xml += f"""
  <url>
    <loc>{SITE_URL}/#/evento/{row.id}</loc>
    <lastmod>{row.fecha_iso}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>"""

    return Response(content=xml, media_type="application/xml; charset=utf-8")


# ---------------------------------------------------------------------------
# GET /robots.txt
# ---------------------------------------------------------------------------

@router.get("/robots.txt", summary="Robots.txt")
async def robots_txt() -> Response:
    content = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
