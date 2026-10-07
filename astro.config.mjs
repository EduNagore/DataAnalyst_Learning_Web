// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
//
// Despliegue en GitHub Pages (ver PLAN.md §3):
// - site/base asumen el repo "DataAnalyst_Learning_Web" bajo el usuario "EduNagore".
// - Todas las rutas internas y assets deben construirse con el helper `url()`
//   de `src/lib/url.ts` (basado en import.meta.env.BASE_URL), nunca con "/..." a mano.
export default defineConfig({
  site: 'https://edunagore.github.io',
  base: '/DataAnalyst_Learning_Web',
  trailingSlash: 'always',
  integrations: [react(), mdx(), sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
});
