// The rules the drawing prompts STATE and nothing used to CHECK.
//
// Both generated drawings are rewritten by the weekly job. Until now the
// author was a hosted model that followed "keep the viewBox under 800", "never
// hardcode a count", "theme tokens only", "a complete French aria-label" on its
// own, and the only mechanical guards were scan-public, a build, and
// check-diagram-highlight. Moving the author to the lab's own model is what
// makes those sentences worth enforcing: a rule a strong model happened to keep
// is not a rule, and the weaker the author, the more of the contract has to
// live in a program instead of in a prompt.
//
// Every rule compares against the BASE revision (default HEAD — the driver
// runs this before committing, so HEAD is what the site had last week). That
// is deliberate: the drawing today already contains "0 port ouvert" and
// English code comments, and a rule that refused the drawing as it stands
// would be relaxed the first night it fired. What is refused is what the
// session ADDED.
//
//   node scripts/check-diagram-lint.mjs B|D [--dist dist] [--base HEAD]
//
// --dist enables the checks that need the rendered SVG (geometry, the
// aria-label as a reader gets it). The driver always passes it, after the
// SHOW_LIVE_ARCH=1 build.
import { readFileSync, existsSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

const COMPONENTS = {
  B: {
    file: "src/components/LiveArchDiagram.astro",
    page: "architecture/index.html",
    figure: 'class="live-arch"',
    maxWidth: 800,
  },
  D: {
    file: "src/components/RackDiagram.astro",
    page: "inventaire/index.html",
    figure: 'class="racks"',
    maxWidth: 900,
  },
};

const args = process.argv.slice(2);
const which = args[0];
const opt = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 ? args[i + 1] : dflt;
};
const C = COMPONENTS[which];
if (!C) {
  console.error("usage: check-diagram-lint.mjs B|D [--dist dist] [--base HEAD]");
  process.exit(2);
}
const dist = opt("--dist", null);
const base = opt("--base", "HEAD");

const git = (...a) => execFileSync("git", a, { encoding: "utf8" });
const cur = readFileSync(C.file, "utf8");
let prev;
try {
  prev = git("show", `${base}:${C.file}`);
} catch {
  // a component with no history has nothing to be compared against; the
  // absolute rules below still run
  prev = "";
}

const problems = [];
const refuse = (rule, msg) => problems.push(`${rule} ${msg}`);

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------
const split = (src) => {
  const m = src.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  return m ? { front: m[1], markup: m[2] } : { front: "", markup: src };
};

// the words a reader sees in the markup: no comments, no style/script, no
// {expressions}, no tags — so a number here is a number somebody TYPED
const markupText = (markup) => {
  let s = markup
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<style[\s\S]*?<\/style>/g, " ")
    .replace(/<script[\s\S]*?<\/script>/g, " ");
  let before;
  do {
    before = s;
    s = s.replace(/\{[^{}]*\}/g, " ");
  } while (s !== before);
  return s.replace(/<[^>]*>/g, " ");
};

// string literals of the frontmatter, with their ${…} holes removed
const frontStrings = (front) => {
  const code = front.replace(/^\s*\/\/.*$/gm, "");
  const out = [];
  for (const m of code.matchAll(/`((?:[^`\\]|\\.)*)`|"((?:[^"\\\n]|\\.)*)"|'((?:[^'\\\n]|\\.)*)'/g)) {
    out.push((m[1] ?? m[2] ?? m[3] ?? "").replace(/\$\{[^}]*\}/g, " "));
  }
  return out.join("\n");
};

const tally = (items) => {
  const t = new Map();
  for (const x of items) t.set(x, (t.get(x) ?? 0) + 1);
  return t;
};
// what `now` has more of than `then`
const grown = (now, then) =>
  [...tally(now)].filter(([k, n]) => n > (tally(then).get(k) ?? 0)).map(([k]) => k);

const P = split(prev);
const N = split(cur);

// ---------------------------------------------------------------------------
// G1 — the data imports stay, and clickable boxes do not quietly disappear
// ---------------------------------------------------------------------------
for (const imp of prev.match(/^import \w+ from "\.\.\/data\/[\w.-]+";$/gm) ?? []) {
  if (!cur.includes(imp)) refuse("G1", `import removed: ${imp}`);
}
// Whether a box went missing is judged on the RENDERED drawing, below: a
// count of attributes in the source cannot tell a lost box from three
// hand-placed boxes folded into one `.map()` — which is exactly what the
// 2026-09-09 refactor did, and a source count refused it.

// ---------------------------------------------------------------------------
// G3 — no count typed by hand. 0 and 1 are words ("0 port ouvert", "l'unique"),
// anything else the data can provide and must.
// ---------------------------------------------------------------------------
const NUM = /(?<![\p{L}\d.,:#-])(\d+)(?![\p{L}\d.,%])/gu;
const bigNums = (s) => [...s.matchAll(NUM)].map((m) => m[1]).filter((n) => Number(n) >= 2);
for (const n of grown(bigNums(markupText(N.markup)), bigNums(markupText(P.markup)))) {
  refuse("G3", `a number typed into the drawing's text: "${n}" — derive it from the data`);
}
const COUNTISH = /(?<![\p{L}\d.,:#-])(\d+)\s+\p{Ll}/gu;
const countish = (s) => [...s.matchAll(COUNTISH)].map((m) => m[1]).filter((n) => Number(n) >= 2);
for (const n of grown(countish(frontStrings(N.front)), countish(frontStrings(P.front)))) {
  refuse("G3", `a count typed into a string: "${n} …" — derive it from the data`);
}

// ---------------------------------------------------------------------------
// G4 — monochrome by design: theme tokens only
// ---------------------------------------------------------------------------
const OK_PAINT = /^(none|transparent|currentColor|var\(--[\w-]+\)|url\(#[\w-]+\))$/;
const colours = (s) => [
  ...[...s.matchAll(/\b(?:fill|stroke|stop-color|color)="([^"{]*)"/g)]
    .map((m) => m[1].trim())
    .filter((v) => !OK_PAINT.test(v)),
  ...(s.match(/#[0-9a-fA-F]{3,8}\b(?=["';\s)])|\b(?:rgba?|hsla?|oklch)\(/g) ?? []),
];
for (const c of grown(colours(cur), colours(prev))) {
  refuse("G4", `colour outside the theme: ${c}`);
}

// ---------------------------------------------------------------------------
// G5 (source) — the author's reasoning does not belong in the file
// ---------------------------------------------------------------------------
let added = "";
try {
  added = git("diff", "-U0", base, "--", C.file)
    .split("\n")
    .filter((l) => l.startsWith("+") && !l.startsWith("+++"))
    .join("\n");
} catch {
  added = cur;
}
const REASONING = /<\/?think>|\b(Let me|Let's|The user|I will|I'll|I need to|Okay, so|Wait,)\b/;
for (const line of added.split("\n")) {
  if (REASONING.test(line)) {
    refuse("G5", `reasoning left in the file: ${line.slice(0, 100).trim()}`);
  }
}

// ---------------------------------------------------------------------------
// G6 — a redraw is an edit, not a rewrite. The largest real nightly redraw
// deleted 57 of ~500 lines; 40 % is a session that started over.
// ---------------------------------------------------------------------------
if (prev) {
  const [, del] = (git("diff", "--numstat", base, "--", C.file).trim().split(/\s+/) ?? []).map(Number);
  const baseLines = prev.split("\n").length;
  if (del > baseLines * 0.4) {
    refuse("G6", `${del} of ${baseLines} lines deleted — that is a rewrite, not the smallest change`);
  }
}

// ---------------------------------------------------------------------------
// G7 (source, racks) — no device typed in by hand
// ---------------------------------------------------------------------------
if (which === "D" && existsSync("src/data/fleet.json")) {
  const fleet = JSON.parse(readFileSync("src/data/fleet.json", "utf8"));
  const literals = new Set(
    (fleet.devices ?? [])
      .flatMap((d) => [d.name, d.model])
      .filter((s) => typeof s === "string" && s.length >= 4),
  );
  for (const lit of literals) {
    const count = (s) => s.split(lit).length - 1;
    if (count(cur) > count(prev)) {
      refuse("G7", `fleet value typed into the component: "${lit}" — read it from fleet.json`);
    }
  }
}

// ---------------------------------------------------------------------------
// rendered checks
// ---------------------------------------------------------------------------
const decode = (s) =>
  s
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&");
const attr = (tag, name) => {
  const m = tag.match(new RegExp(`\\s${name}="([^"]*)"`));
  return m ? decode(m[1]) : null;
};

if (dist) {
  const pagePath = join(dist, C.page);
  const html = existsSync(pagePath) ? readFileSync(pagePath, "utf8") : "";
  const at = html.indexOf(C.figure);
  const start = at >= 0 ? html.indexOf("<svg", at) : -1;
  const end = start >= 0 ? html.indexOf("</svg>", start) : -1;
  if (start < 0 || end < 0) {
    // an empty fleet legitimately renders no racks; the architecture drawing
    // is only absent when SHOW_LIVE_ARCH is off, which the driver never does
    if (which === "B") refuse("G2", `no drawing found in ${pagePath} — was it built with SHOW_LIVE_ARCH=1?`);
  } else {
    const svg = html.slice(start, end);
    const open = svg.slice(0, svg.indexOf(">") + 1);

    // G2 — the canvas
    const vb = (attr(open, "viewBox") ?? "").split(/\s+/).map(Number);
    const [W, H] = [vb[2], vb[3]];
    if (!(W > 0 && H > 0)) refuse("G2", `unreadable viewBox: ${attr(open, "viewBox")}`);
    else if (W > C.maxWidth) refuse("G2", `viewBox is ${W} wide — the column caps it at ${C.maxWidth}`);

    // G5 — the aria-label a screen reader gets, in the page's language
    const label = attr(open, "aria-label") ?? "";
    if (attr(open, "role") !== "img" || label.length < 60) {
      refuse("G5", `role="img" with a complete aria-label is required (got ${label.length} chars)`);
    } else {
      const words = label.toLowerCase().match(/\p{L}+/gu) ?? [];
      const FR = new Set(["le", "la", "les", "des", "du", "et", "est", "un", "une", "qui", "par", "dans", "sur", "pas", "sont", "au", "aux", "ne"]);
      const EN = new Set(["the", "and", "is", "are", "of", "to", "which", "not", "in", "on", "with", "by", "from", "this"]);
      const fr = words.filter((w) => FR.has(w)).length;
      const en = words.filter((w) => EN.has(w)).length;
      if (fr <= en) refuse("G5", `aria-label does not read as French (${fr} French vs ${en} English function words)`);
    }

    // G2 — boxes: inside the canvas, and (architecture) never on top of another
    const body = svg.replace(/<defs[\s\S]*?<\/defs>/g, "");
    const num = (t, n) => Number(attr(t, n) ?? "0");
    if (W > 0 && H > 0) {
      for (const m of body.matchAll(/<rect\b[^>]*>/g)) {
        const [x, y, w, h] = ["x", "y", "width", "height"].map((n) => num(m[0], n));
        if (x < -1 || y < -1 || x + w > W + 1 || y + h > H + 1) {
          refuse("G2", `a box leaves the canvas: x=${x} y=${y} ${w}×${h} in ${W}×${H}`);
        }
      }
    }
    if (which === "B") {
      const boxes = [];
      for (const m of body.matchAll(/<(a|g)\b[^>]*\bdata-nodes?="([^"]*)"[^>]*>/g)) {
        const rest = body.slice(m.index + m[0].length);
        const stop = rest.search(new RegExp(`</${m[1]}>`));
        const rect = rest.slice(0, stop < 0 ? undefined : stop).match(/<rect\b[^>]*>/);
        if (!rect) continue; // text-only aggregates (λ, s3) have no box
        const [x, y, w, h] = ["x", "y", "width", "height"].map((n) => num(rect[0], n));
        boxes.push({ id: m[2].split(/\s+/)[0] || "(aggregate)", x, y, w, h });
      }
      for (let i = 0; i < boxes.length; i++) {
        for (let j = i + 1; j < boxes.length; j++) {
          const a = boxes[i], b = boxes[j];
          const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
          const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
          if (ox > 1 && oy > 1) refuse("G2", `boxes overlap: ${a.id} and ${b.id}`);
        }
      }
    }

    // G1 (rendered) — every machine, every hors-IaC box and the tunnel is a
    // box of its own, and every app sits in an aggregate. That is the drawing's
    // contract with the page's click; losing one is losing an entrance.
    if (which === "B" && existsSync("src/data/architecture.json")) {
      const arch = JSON.parse(readFileSync("src/data/architecture.json", "utf8"));
      const singles = new Set([...body.matchAll(/\bdata-node="([^"]+)"/g)].map((m) => m[1]));
      const members = new Set([...body.matchAll(/\bdata-nodes="([^"]*)"/g)].flatMap((m) => m[1].split(/\s+/)));
      for (const n of arch.nodes) {
        if (["host", "external", "tunnel"].includes(n.kind) && !singles.has(n.id)) {
          refuse("G1", `${n.id} has no box of its own in the drawing`);
        }
        if (n.kind === "app" && !members.has(n.id) && !singles.has(n.id)) {
          refuse("G1", `${n.id} is in no box or aggregate`);
        }
      }
    }

    // G7 (rendered, racks) — no U scale: rackOrder is a stacking order
    if (which === "D") {
      const lone = [...body.matchAll(/>\s*(U\s?\d+|\d+\s?U)\s*</g)];
      if (lone.length >= 3) refuse("G7", `${lone.length} bare U labels — that is a U scale, and the data has no U positions`);
    }
  }
}

if (problems.length) {
  console.error(`check-diagram-lint ${which}: refused`);
  for (const p of problems) console.error("  - " + p);
  process.exit(1);
}
console.log(`check-diagram-lint ${which}: ok${dist ? " (source + rendered)" : " (source only)"}`);
