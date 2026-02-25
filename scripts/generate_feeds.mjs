import fs from 'fs';
import path from 'path';
import { createClient } from '@supabase/supabase-js';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

// Helpers para rutas absolutas en modules ES6
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Conexión Supabase (usamos rol anon explícito para lectura pública sin exponer write keys aquí, 
// o la key del entorno si se provee)
const SUPABASE_URL = process.env.VITE_SUPABASE_URL || 'https://jjballixujlppsfeuhad.supabase.co';
// Si tuviéramos SERVICE_ROLE_KEY podemos usarla para bypass RLS, pero la anon suele valer para leer
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpqYmFsbGl4dWpscHBzZmV1aGFkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIwMTMzMDksImV4cCI6MjA4NzU4OTMwOX0.XwVgi8rnHEUcc-q0FeCi7UgYrkMdx_v2fEutRWYZYbQ';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

const SITE_URL = process.env.SITE_URL
    || (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : null)
    || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000');

/**
 * Escapa strings especiales para XML
 */
function escapeXml(unsafe) {
    if (!unsafe) return '';
    return unsafe.replace(/[<>&'"]/g, function (c) {
        switch (c) {
            case '<': return '&lt;';
            case '>': return '&gt;';
            case '&': return '&amp;';
            case '\'': return '&apos;';
            case '"': return '&quot;';
        }
    });
}

function generateSitemap(events) {
    console.log('Generando sitemap.xml...');
    const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
      <loc>${SITE_URL}/</loc>
      <changefreq>daily</changefreq>
      <priority>1.0</priority>
  </url>
  <url>
      <loc>${SITE_URL}/mapa</loc>
      <changefreq>daily</changefreq>
      <priority>0.8</priority>
  </url>
  <url>
      <loc>${SITE_URL}/calendario</loc>
      <changefreq>daily</changefreq>
      <priority>0.8</priority>
  </url>
  <url>
      <loc>${SITE_URL}/semana</loc>
      <changefreq>daily</changefreq>
      <priority>0.8</priority>
  </url>
${events.map(ev => `  <url>
      <loc>${SITE_URL}/evento/${ev.id}</loc>
      <changefreq>weekly</changefreq>
      <priority>0.6</priority>
  </url>`).join('\n')}
</urlset>`;

    fs.writeFileSync(path.join(__dirname, '..', 'sitemap.xml'), sitemapXml);
    console.log('✓ sitemap.xml guardado exitosamente.');
}

function generateRss(events) {
    console.log('Generando rss.xml...');
    const pubDate = new Date().toUTCString();

    // Solo mostramos los próximos 50 eventos en el feed para evitar pesarlo
    const topEvents = events.slice(0, 50);

    const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Agenda Cultural Gran Canaria</title>
    <link>${SITE_URL}</link>
    <description>Los mejores eventos culturales, conciertos y espectáculos en Gran Canaria.</description>
    <language>es-es</language>
    <pubDate>${pubDate}</pubDate>
    <atom:link href="${SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
${topEvents.map(ev => {
        // Calcular pubDate formato RFC-822
        let itemDate = '';
        try {
            itemDate = new Date(ev.fecha_iso + (ev.hora ? `T${ev.hora}:00` : 'T00:00:00')).toUTCString();
        } catch (e) {
            itemDate = pubDate;
        }

        const desc = `
      <p><strong>Fecha:</strong> ${escapeXml(ev.fecha_iso)} ${escapeXml(ev.hora || '')}</p>
      <p><strong>Lugar:</strong> ${escapeXml(ev.lugar)}</p>
      <p>${escapeXml(ev.descripcion || 'Evento cultural')}</p>
      ${ev.imagen_url ? `<img src="${ev.imagen_url}" alt="Imagen del evento" />` : ''}
    `.trim();

        return `
    <item>
      <title>${escapeXml(ev.nombre)}</title>
      <link>${SITE_URL}/evento/${ev.id}</link>
      <guid isPermaLink="true">${SITE_URL}/evento/${ev.id}</guid>
      <description><![CDATA[${desc}]]></description>
      <pubDate>${itemDate}</pubDate>
    </item>`;
    }).join('\n')}
  </channel>
</rss>`;

    fs.writeFileSync(path.join(__dirname, '..', 'rss.xml'), rssXml);
    console.log('✓ rss.xml guardado exitosamente.');
}

function generateRobots() {
    console.log('Generando robots.txt...');
    const robotsTxt = `User-agent: *
Allow: /

Sitemap: ${SITE_URL}/sitemap.xml
`;
    fs.writeFileSync(path.join(__dirname, '..', 'robots.txt'), robotsTxt);
    console.log('✓ robots.txt guardado exitosamente.');
}

async function run() {
    console.log('Extrayendo eventos futuros desde Supabase...');
    const today = new Date().toISOString().slice(0, 10);

    const { data: events, error } = await supabase
        .from('evento')
        .select('id, nombre, lugar, fecha_iso, hora, descripcion, estilo, imagen_url')
        .not('fecha_iso', 'is', null)
        .gte('fecha_iso', today)
        .order('fecha_iso', { ascending: true });

    if (error) {
        console.error('Error al obtener eventos de Supabase:', error);
        process.exit(1);
    }

    console.log(`Se recuperaron ${events.length} eventos futuros.`);

    generateSitemap(events);
    generateRss(events);
    generateRobots();

    console.log('Todos los feeds han sido generados localmente para servir en estático.');
}

run().catch(console.error);
