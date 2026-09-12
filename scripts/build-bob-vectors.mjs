/**
 * Builds the semantic-search index Bob answers from.
 *
 * WHY: the chat grounding (src/pages/bob-grounding.json.ts) carries an INDEX of
 * the corpus — one line per article, title plus a description truncated to 80
 * characters. Bob can therefore name an article and link to it, but cannot
 * answer FROM it. The corpus itself is ~937 KB, about 354k tokens at the 2.65
 * chars/token this site measures, so it will never fit in a prompt. Retrieval
 * is the only way to put article *content* in front of the model.
 *
 * WHY A COMMITTED ARTIFACT, not a build step: embedding happens here and the
 * result is committed, so `npm run build` never touches the homelab. Generating
 * vectors during the build would make a public site's deploy fail whenever
 * `bob` is down for maintenance — a coupling nobody would choose deliberately,
 * and one that would be discovered at the worst moment. Run this when content
 * changes; the build just serves what is in public/.
 *
 * It is INCREMENTAL: chunks are keyed by a hash of their text, and unchanged
 * chunks keep their existing vector. Adding one article re-embeds that article
 * and nothing else.
 *
 * Usage:  node scripts/build-bob-vectors.mjs [--host http://bob.tptpt.in:11434]
 */
import { createHash } from "node:crypto";
import { readFile, readdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

const HOST = process.argv.includes("--host")
  ? process.argv[process.argv.indexOf("--host") + 1]
  : "http://bob.tptpt.in:11434";
const MODEL = "bge-m3";
const OUT = "public/bob-vectors.json";

/** Chunk size in characters. ~1200 keeps a whole argument together — a section
 *  with its example — while staying small enough that four of them fit in the
 *  prompt budget without crowding out the grounding. */
const TARGET_CHARS = 1200;
/** A code block is never split: a half-shown command is worse than none. */
const MAX_CHARS = 2600;

const COLLECTIONS = [
  { dir: "src/content/blog", lang: "fr", url: (slug) => `/blog/${slug}/` },
  { dir: "src/content/blog-en", lang: "en", url: (slug) => `/en/blog/${slug}/` },
];

/** Frontmatter, for the four fields this needs. Deliberately not a YAML
 *  dependency: the shapes here are `key: "quoted"`, `key: bare` and
 *  `key: ["a", "b"]`, and a parser for exactly that is easier to trust than a
 *  general one that might reinterpret a title full of colons. */
function frontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return { data: {}, body: raw };
  const data = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2].trim();
    if (v.startsWith('"') && v.endsWith('"')) v = v.slice(1, -1);
    else if (v.startsWith("[")) {
      try { v = JSON.parse(v.replace(/'/g, '"')); } catch { /* leave as text */ }
    }
    data[kv[1]] = v;
  }
  return { data, body: raw.slice(m[0].length) };
}

/** MDX noise that means nothing to a reader and nothing to retrieval. */
function stripMdx(body) {
  return body
    .replace(/^import\s+.*$/gm, "")
    .replace(/^export\s+const\s+.*$/gm, "")
    .replace(/<\/?[A-Z][\w.]*(\s[^>]*)?\/?>/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** Split into blocks, never inside a fenced code block. */
function blocks(body) {
  const out = [];
  let buf = [];
  let fence = null;
  for (const line of body.split(/\r?\n/)) {
    const f = line.match(/^\s*(```+|~~~+)/);
    if (f && !fence) fence = f[1];
    else if (f && fence && line.trim().startsWith(fence)) fence = null;
    if (!fence && line.trim() === "") {
      if (buf.length) out.push(buf.join("\n").trim());
      buf = [];
    } else {
      buf.push(line);
    }
  }
  if (buf.length) out.push(buf.join("\n").trim());
  return out.filter(Boolean);
}

function chunk(body) {
  const out = [];
  let cur = "";
  for (const b of blocks(body)) {
    if (b.length > MAX_CHARS) {
      // A single oversized block (a long cast transcript, a big table) goes out
      // on its own rather than dragging a neighbour over the limit with it.
      if (cur) { out.push(cur); cur = ""; }
      out.push(b.slice(0, MAX_CHARS));
      continue;
    }
    if (cur && cur.length + b.length + 2 > TARGET_CHARS) {
      out.push(cur);
      // Overlap: carry the last paragraph so an idea split across the seam is
      // still retrievable from both sides.
      const tail = cur.split("\n\n").pop();
      cur = tail && tail.length < 400 ? `${tail}\n\n${b}` : b;
    } else {
      cur = cur ? `${cur}\n\n${b}` : b;
    }
  }
  if (cur) out.push(cur);
  return out;
}

const hash = (s) => createHash("sha256").update(s).digest("hex").slice(0, 16);

/** Unit-normalise, then quantise to int8. Cosine similarity between two
 *  normalised vectors is their dot product, and the dot product of the
 *  quantised pair ranks identically — so the Worker never needs floats. */
function quantise(vec) {
  let norm = Math.sqrt(vec.reduce((a, x) => a + x * x, 0)) || 1;
  const q = Buffer.alloc(vec.length);
  for (let i = 0; i < vec.length; i++) {
    const v = Math.round((vec[i] / norm) * 127);
    q[i] = Math.max(-127, Math.min(127, v)) & 0xff;
  }
  return q.toString("base64");
}

async function embed(texts) {
  const res = await fetch(`${HOST}/api/embed`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ model: MODEL, input: texts }),
  });
  if (!res.ok) throw new Error(`embed ${res.status}: ${(await res.text()).slice(0, 200)}`);
  const body = await res.json();
  if (!body.embeddings?.length) throw new Error("embed returned no vectors");
  return body.embeddings;
}

const previous = existsSync(OUT)
  ? JSON.parse(await readFile(OUT, "utf8"))
  : { chunks: [] };
const known = new Map(previous.chunks.map((c) => [c.h, c.v]));

const pending = [];
const chunks = [];
for (const col of COLLECTIONS) {
  for (const file of (await readdir(col.dir)).filter((f) => /\.mdx?$/.test(f))) {
    const raw = await readFile(path.join(col.dir, file), "utf8");
    const { data, body } = frontmatter(raw);
    const slug = file.replace(/\.mdx?$/, "");
    const title = data.title ?? slug;
    const pieces = chunk(stripMdx(body));
    pieces.forEach((text, i) => {
      // The title rides along in the embedded text: a chunk deep inside an
      // article rarely repeats what the article is about, and without it the
      // vector drifts away from the question that names the subject.
      const embedded = `${title}\n\n${text}`;
      const h = hash(embedded);
      const entry = {
        h,
        slug,
        lang: col.lang,
        title,
        url: col.url(slug),
        date: String(data.pubDate ?? "").slice(0, 10),
        i,
        text,
      };
      chunks.push(entry);
      if (!known.has(h)) pending.push({ entry, embedded });
    });
  }
}

console.log(`${chunks.length} tronçons, ${pending.length} à vectoriser`);
const BATCH = 16;
for (let i = 0; i < pending.length; i += BATCH) {
  const slice = pending.slice(i, i + BATCH);
  const vectors = await embed(slice.map((p) => p.embedded));
  slice.forEach((p, j) => known.set(p.entry.h, quantise(vectors[j])));
  process.stdout.write(`\r  ${Math.min(i + BATCH, pending.length)}/${pending.length}`);
}
if (pending.length) process.stdout.write("\n");

const dim = Buffer.from(known.values().next().value, "base64").length;
const artifact = {
  model: MODEL,
  dim,
  generated: new Date().toISOString(),
  chunks: chunks.map((c) => ({ ...c, v: known.get(c.h) })),
};
await writeFile(OUT, JSON.stringify(artifact));
const bytes = Buffer.byteLength(JSON.stringify(artifact));
console.log(`écrit ${OUT} — ${chunks.length} tronçons, ${dim} dimensions, ${(bytes / 1e6).toFixed(2)} Mo`);
