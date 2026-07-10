#!/usr/bin/env node
//
// Rasterizes every SVG heroImage referenced by a blog post into a PNG
// sibling, since Open Graph/Twitter card crawlers don't reliably render
// SVG. Also renders a larger PNG version of the site favicon for posts
// with no heroImage at all, since the 64x64 favicon.png is too small to
// use as a link-preview thumbnail. Runs before every build so newly
// added SVG banners get a matching PNG without a manual step.
//
import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const PUBLIC_DIR = join(ROOT, "public");
const CONTENT_DIRS = ["src/content/blog", "src/content/blog-en"].map((d) => join(ROOT, d));

const OG_WIDTH = 1200;
const FAVICON_OG_SIZE = 512;

function findSvgHeroImages() {
  const found = new Set();
  for (const dir of CONTENT_DIRS) {
    for (const file of readdirSync(dir)) {
      if (!file.endsWith(".md") && !file.endsWith(".mdx")) continue;
      const text = readFileSync(join(dir, file), "utf8");
      const match = text.match(/heroImage:\s*"([^"]+\.svg)"/);
      if (match) found.add(match[1]);
    }
  }
  return [...found];
}

async function rasterizeHeroImages() {
  for (const heroImage of findSvgHeroImages()) {
    const svgPath = join(PUBLIC_DIR, heroImage);
    const pngPath = svgPath.replace(/\.svg$/, ".png");
    if (existsSync(pngPath)) continue;
    if (!existsSync(svgPath)) {
      console.warn(`generate-og-images: missing source SVG for ${heroImage}, skipping`);
      continue;
    }
    await sharp(svgPath).resize({ width: OG_WIDTH }).png().toFile(pngPath);
    console.log(`generate-og-images: rendered ${heroImage} -> ${pngPath.replace(ROOT, "")}`);
  }
}

async function rasterizeFavicon() {
  const svgPath = join(PUBLIC_DIR, "favicon.svg");
  const pngPath = join(PUBLIC_DIR, "og-favicon.png");
  if (existsSync(pngPath)) return;
  await sharp(svgPath).resize(FAVICON_OG_SIZE, FAVICON_OG_SIZE).png().toFile(pngPath);
  console.log(`generate-og-images: rendered favicon.svg -> og-favicon.png (${FAVICON_OG_SIZE}x${FAVICON_OG_SIZE})`);
}

await rasterizeFavicon();
await rasterizeHeroImages();
