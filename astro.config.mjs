// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://labodeludo.dev',
  integrations: [mdx(), sitemap()],
  redirects: {
    '/blog': '/',
    // The inventory index is now the "rôles" section of the architecture
    // hub. The per-role permalinks stay: articles link to them, and so do
    // the boxes on both diagrams.
    '/inventaire': '/architecture/#roles',
  },
});
