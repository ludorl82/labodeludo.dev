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
    // Same reasoning one language over: /en/ IS the English post list, so
    // /en/blog/ is a bare directory people reach by trimming an article URL.
    // A redirect rather than a second listing, so there is one canonical
    // index per language instead of two URLs competing for the same page.
    '/en/blog': '/en/',
    // /architecture/details is gone: every one of its eleven diagrams
    // already lives inside the article it came from, so the page was pure
    // duplication.
    '/architecture/details': '/architecture/',
  },
});
