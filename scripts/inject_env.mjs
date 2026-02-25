import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Determina la URL según variables de entorno de Vercel/Locales
let siteUrl = process.env.SITE_URL
    || (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : null)
    || (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : 'http://localhost:3000');

// Fallback preventivo asegurando que no haya slash final
siteUrl = siteUrl.replace(/\/$/, '');

console.log(`[Inject Env] SITE_URL resolviendo a: ${siteUrl}`);

const indexPath = path.join(__dirname, '..', 'index.html');
if (!fs.existsSync(indexPath)) {
    console.error('No se pudo encontrar index.html');
    process.exit(1);
}

let indexHtml = fs.readFileSync(indexPath, 'utf8');

// Reemplazar la URL placeholder donde se halle
const updatedHtml = indexHtml.replace(/__SITE_URL__/g, siteUrl);

if (indexHtml !== updatedHtml) {
    fs.writeFileSync(indexPath, updatedHtml);
    console.log('[Inject Env] ✓ URLs de index.html actualizadas (Canonical, Open Graph, JSON-LD, etc).');
} else {
    console.log('[Inject Env] No se detectaron URLs placeholder que cambiar en index.html.');
}

// Generar env.js dinámico para el Frontend con las claves de Supabase
const supabaseUrl = process.env.VITE_SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('[Inject Env] ⚠️  Faltan las credenciales de Supabase en las variables de entorno (.env).')
}

const envJsContent = `window.ENV = {
  SUPABASE_URL: "${supabaseUrl || ''}",
  SUPABASE_ANON_KEY: "${supabaseAnonKey || ''}"
};`;

fs.writeFileSync(path.join(__dirname, '..', 'env.js'), envJsContent);
console.log('[Inject Env] ✓ env.js generado exitosamente para el frontend.');
