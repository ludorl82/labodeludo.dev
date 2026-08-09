#!/usr/bin/env node
//
// Builds the link-preview card for every article: a 1200x627 PNG sibling
// named "<hero>-og.png", plus /og-default.png for the handful of posts with
// no heroImage at all.
//
// Why 1200x627 and not just the banner: LinkedIn (and Facebook) render the
// large card only for images near 1.91:1. Our banners are 1200x375 — a 3.2:1
// strip — and posts without a hero used to fall back to a 512x512 square,
// which forces the small thumbnail layout. Both were the reason previews
// looked wrong (2026-08-08). The hero is contained, never cropped, and
// centred on the site's true black, so the artwork survives intact and the
// card still looks like the site.
//
// The older "<hero>.png" siblings of SVG heroes are deliberately left alone
// and no longer generated: previews already published on LinkedIn and in
// Google's cache point at those URLs, and deleting them would break shares
// that are already out in the world.
//
// Runs before every build, and skips anything already rendered — delete a
// card to force it to be rebuilt.
//
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const PUBLIC_DIR = join(ROOT, "public");
const CONTENT_DIRS = ["src/content/blog", "src/content/blog-en"].map((d) => join(ROOT, d));

// keep in sync with src/lib/ogImage.ts, which emits these as
// og:image:width / og:image:height
const OG_WIDTH = 1200;
const OG_HEIGHT = 627;
const OG_SUFFIX = "-og.png";
const KNOWN_EXT = [".svg", ".png", ".jpg", ".jpeg", ".webp"];
const BLACK = { r: 0, g: 0, b: 0, alpha: 1 };

function ogPathFor(heroImage) {
  const ext = KNOWN_EXT.find((e) => heroImage.toLowerCase().endsWith(e));
  return ext ? heroImage.slice(0, -ext.length) + OG_SUFFIX : null;
}

function findHeroImages() {
  const found = new Set();
  for (const dir of CONTENT_DIRS) {
    for (const file of readdirSync(dir)) {
      if (!file.endsWith(".md") && !file.endsWith(".mdx")) continue;
      const match = readFileSync(join(dir, file), "utf8").match(/heroImage:\s*"([^"]+)"/);
      if (match) found.add(match[1]);
    }
  }
  return [...found];
}

// The colour to pad with. Banners carry their own dark background, and
// padding those with pure black reads as a letterbox bar; sampling the
// source's top-left pixel makes the card look like one continuous image
// instead. Falls back to black, which is also what the site's own page
// background is.
async function padColour(buffer) {
  try {
    const { data } = await sharp(buffer)
      .extract({ left: 0, top: 0, width: 1, height: 1 })
      .raw()
      .toBuffer({ resolveWithObject: true });
    return { r: data[0], g: data[1], b: data[2], alpha: 1 };
  } catch {
    return BLACK;
  }
}

// Contain the source inside the card and centre it. `fit: inside` never
// crops, which matters: these banners carry text, and a cover-crop would cut
// it. SVGs get extra density so the rasterization stays sharp.
async function renderCard(
  srcPath,
  outPath,
  { maxWidth = OG_WIDTH, maxHeight = OG_HEIGHT, background = "auto" } = {},
) {
  const isSvg = srcPath.toLowerCase().endsWith(".svg");
  const inner = await sharp(srcPath, isSvg ? { density: 200 } : {})
    .resize({ width: maxWidth, height: maxHeight, fit: "inside" })
    .png()
    .toBuffer();
  const bg = background === "auto" ? await padColour(inner) : background;
  await sharp({
    create: { width: OG_WIDTH, height: OG_HEIGHT, channels: 4, background: bg },
  })
    .composite([{ input: inner, gravity: "center" }])
    .png()
    .toFile(outPath);
}

async function generateHeroCards() {
  for (const heroImage of findHeroImages()) {
    const rel = ogPathFor(heroImage);
    if (!rel) {
      console.warn(`generate-og-images: unrecognised heroImage extension ${heroImage}, skipping`);
      continue;
    }
    const srcPath = join(PUBLIC_DIR, heroImage);
    const outPath = join(PUBLIC_DIR, rel);
    if (existsSync(outPath)) continue;
    if (!existsSync(srcPath)) {
      console.warn(`generate-og-images: missing source for ${heroImage}, skipping`);
      continue;
    }
    await renderCard(srcPath, outPath);
    console.log(`generate-og-images: card ${rel} (${OG_WIDTH}x${OG_HEIGHT})`);
  }
}

// The no-hero fallback. The mark is deliberately small against a lot of
// black — it reads as the site rather than as a stretched icon.
async function generateDefaultCard() {
  const outPath = join(PUBLIC_DIR, "og-default.png");
  if (existsSync(outPath)) return;
  await renderCard(join(PUBLIC_DIR, "favicon.svg"), outPath, {
    maxWidth: 260,
    maxHeight: 260,
    background: BLACK, // the mark on the site's own black, not on its own edge
  });
  console.log(`generate-og-images: card og-default.png (${OG_WIDTH}x${OG_HEIGHT})`);
}

await generateDefaultCard();
await generateHeroCards();
