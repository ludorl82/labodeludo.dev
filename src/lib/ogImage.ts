// Link-preview card resolution. Every article points at a generated
// "<hero>-og.png" rather than at its hero directly, so og:image is always
// exactly OG_IMAGE_WIDTH x OG_IMAGE_HEIGHT and we can declare those
// dimensions honestly in the head.
//
// Before this (until 2026-08-08) og:image was the hero itself: banners are
// 1200x375, a 3.2:1 strip, and posts with no hero fell back to a 512x512
// square. LinkedIn renders its large card only near 1.91:1, so both cases
// were being demoted to the small thumbnail layout.
//
// scripts/generate-og-images.mjs builds the cards and must agree with these
// constants.

export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 627;

const OG_SUFFIX = "-og.png";
const KNOWN_EXTENSIONS = [".svg", ".png", ".jpg", ".jpeg", ".webp"];
const DEFAULT_OG_IMAGE = "/og-default.png";

export function resolveOgImage(heroImage: string | undefined): string {
  if (!heroImage) return DEFAULT_OG_IMAGE;
  const lower = heroImage.toLowerCase();
  const ext = KNOWN_EXTENSIONS.find((e) => lower.endsWith(e));
  if (!ext) return DEFAULT_OG_IMAGE;
  return heroImage.slice(0, -ext.length) + OG_SUFFIX;
}
