export type Author = "ludo" | "bob";

export function authorFromTags(tags: string[]): Author {
  return tags.includes("bob") ? "bob" : "ludo";
}
