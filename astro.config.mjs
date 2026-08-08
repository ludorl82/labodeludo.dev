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
    // /architecture/details is gone: every one of its eleven diagrams
    // already lives inside the article it came from, so the page was pure
    // duplication.
    '/architecture/details': '/architecture/',
  },
});
