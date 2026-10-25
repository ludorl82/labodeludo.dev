import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const prerender = true;

/**
 * The short links, code → article path, from each article's `court` field.
 *
 * The only source for both hosts: scripts/emit-short-links.mjs turns it into
 * dist/_redirects for Cloudflare Pages (staging), and
 * scripts/redirect-short-links.sh into S3 redirect objects (prod). Duplicates
 * and collisions with real pages are refused there, after the build, because
 * only the built tree knows every top-level path.
 */
export const GET: APIRoute = async () => {
  const [posts, postsEn] = await Promise.all([
    getCollection("blog"),
    getCollection("blogEn"),
  ]);

  const links = [
    ...posts.map((p) => ({ code: p.data.court, target: `/blog/${p.id}/` })),
    ...postsEn.map((p) => ({ code: p.data.court, target: `/en/blog/${p.id}/` })),
  ]
    .filter((l): l is { code: string; target: string } => !!l.code)
    .sort((a, b) => a.code.localeCompare(b.code));

  return new Response(JSON.stringify({ schema: 1, links }), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
