const KNOWN_CATEGORIES = new Set(["DevOps", "Cloud", "Maison", "Labo"]);

const VAR_BY_CATEGORY: Record<string, string> = {
  DevOps: "--accent-devops",
  Cloud: "--accent-cloud",
  Maison: "--accent-maison",
  Labo: "--accent-labo",
};

export function primaryCategory(tags: string[]): string | undefined {
  return tags.find((t) => KNOWN_CATEGORIES.has(t));
}

export function categoryColorVar(category: string | undefined): string {
  return category ? VAR_BY_CATEGORY[category] ?? "--accent-default" : "--accent-default";
}
