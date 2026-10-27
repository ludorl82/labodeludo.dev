import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const prerender = true;

/**
 * The short links, code → article path, from each article's `court` field.
 *
 * The only source for every host: scripts/emit-short-links.mjs turns it into
 * dist/_redirects for Cloudflare Pages (staging),
 * scripts/redirect-short-links.sh into S3 redirect objects (prod), and the
 * `lbdl` Worker in cloudflare-iac reads the published file to serve lbdl.dev.
 * Renaming or reshaping it breaks the short domain. Duplicates
 * and collisions with real pages are refused there, after the build, because
 * only the built tree knows every top-level path.
 */
export const GET: APIRoute = async () => {
  const [posts, postsEn, casts, castsEn] = await Promise.all([
    getCollection("blog"),
    getCollection("blogEn"),
    getCollection("casts"),
    getCollection("castsEn"),
  ]);

  // Casts live under their own prefix, cast/<code> (11 characters at most):
  // the code is a path to both hosts, so nothing else needs to know.
  const cast = (court: string | undefined) => (court ? `cast/${court}` : undefined);
  const links = [
    ...posts.map((p) => ({ code: p.data.court, target: `/blog/${p.id}/` })),
    ...postsEn.map((p) => ({ code: p.data.court, target: `/en/blog/${p.id}/` })),
    ...casts.map((c) => ({ code: cast(c.data.court), target: `/casts/${c.id}/` })),
    ...castsEn.map((c) => ({ code: cast(c.data.court), target: `/en/casts/${c.id}/` })),
  ]
    .filter((l): l is { code: string; target: string } => !!l.code)
    .sort((a, b) => a.code.localeCompare(b.code));

  return new Response(JSON.stringify({ schema: 1, links }), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};
