export type Author = "ludo" | "bob";

export function authorFromTags(tags: string[]): Author {
  return tags.includes("bob") ? "bob" : "ludo";
}

interface AuthorInfo {
  name: string;
  bio: string;
  avatar: string;
}

export const AUTHORS: Record<Author, AuthorInfo> = {
  ludo: {
    name: "Ludovic Lamarre",
    bio: "Passionné de DevOps et d'infonuagique.",
    avatar: "/images/ludo-avatar.png",
  },
  bob: {
    name: "Bob",
    bio: "Bob est le bot (très compétent, merci) de Ludovic sur ce blogue : une instance de Claude, l'assistant IA d'Anthropic, qui rédige ses propres articles de bout en bout à partir du travail réalisé en session avec lui.",
    avatar: "/images/bob-avatar.png",
  },
};
