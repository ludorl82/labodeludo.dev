import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

export const prerender = true;

function truncate(text: string, words: number): string {
  const plain = text
    .replace(/<[^>]+>/g, " ")
    .replace(/[#*_>`]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const parts = plain.split(" ");
  return parts.length <= words ? plain : parts.slice(0, words).join(" ") + "…";
}

export const GET: APIRoute = async ({ site }) => {
  const base = site?.toString().replace(/\/$/, "") ?? "https://labodeludo.dev";

  const [fr, en] = await Promise.all([
    getCollection("blog"),
    getCollection("blogEn"),
  ]);

  const byDateDesc = (a: (typeof fr)[number], b: (typeof fr)[number]) =>
    b.data.pubDate.valueOf() - a.data.pubDate.valueOf();

  const frSorted = [...fr].sort(byDateDesc);
  const enIds = new Set(en.map((p) => p.id));

  const lines: string[] = [
    "# Le labo de Ludo",
    "",
    "> Journal d'incidents et de bricolages d'un homelab réel — réseau, self-hosting, automatisation. La plupart des articles sont en français ; ceux qui ont une version anglaise sont notés ci-dessous.",
    "",
    "## Articles",
    "",
  ];

  for (const post of frSorted) {
    const description = post.data.description || truncate(post.body ?? "", 60);
    const url = `${base}/blog/${post.id}/`;
    lines.push(`- [${post.data.title}](${url}): ${description}`);
    if (enIds.has(post.id)) {
      lines.push(`  - English version: ${base}/en/blog/${post.id}/`);
    }
  }

  lines.push("");

  return new Response(lines.join("\n"), {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
