const RASTER_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"];

const DEFAULT_OG_IMAGE = "/og-favicon.png";

export function resolveOgImage(heroImage: string | undefined): string {
  if (!heroImage) {
    return DEFAULT_OG_IMAGE;
  }
  if (RASTER_EXTENSIONS.some((ext) => heroImage.toLowerCase().endsWith(ext))) {
    return heroImage;
  }
  if (heroImage.toLowerCase().endsWith(".svg")) {
    // Social crawlers don't reliably render SVG; scripts/generate-og-images.mjs
    // rasterizes a PNG sibling for every SVG heroImage before each build.
    return heroImage.replace(/\.svg$/i, ".png");
  }
  return DEFAULT_OG_IMAGE;
}
