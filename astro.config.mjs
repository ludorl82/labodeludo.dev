// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://labodeludo.dev',
  integrations: [
    mdx(),
    sitemap({
      // AMP twins are found through the canonical page's rel="amphtml", not
      // through the sitemap. Listing one here asks Search Console to index it
      // as a page in its own right, which is the opposite of what it is.
      filter: (page) => !page.endsWith('/amp/'),
    }),
  ],
  redirects: {
    '/blog': '/',
    // /architecture/details is gone: every one of its eleven diagrams
    // already lives inside the article it came from, so the page was pure
    // duplication.
    '/architecture/details': '/architecture/',
  },
});
