const RASTER_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"];

const DEFAULT_OG_IMAGE = "/images/blog/banner-out-1.png";

export function resolveOgImage(heroImage: string | undefined): string {
  if (heroImage && RASTER_EXTENSIONS.some((ext) => heroImage.toLowerCase().endsWith(ext))) {
    return heroImage;
  }
  return DEFAULT_OG_IMAGE;
}
