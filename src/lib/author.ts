export type Author = "ludo" | "bob";

export function authorFromTags(tags: string[]): Author {
  return tags.includes("bob") ? "bob" : "ludo";
}

interface AuthorInfo {
  name: string;
  tagline: string;
  bio: string;
  avatar: string;
  quips?: string[];
}

export const AUTHORS: Record<Author, AuthorInfo> = {
  ludo: {
    name: "Ludovic Lamarre",
    tagline: "Passionné de DevOps, d'infonuagique et d'IA.",
    bio: "Ingénieur DevOps dans le laboratoire d'intelligence artificielle d'une entreprise du secteur de la finance depuis 2021, où il facilite le déplacement de charges de travail d'IA entre AWS, Red Hat et SageMaker et contribue à sécuriser les applications d'IA de l'entreprise. Plus de 20 ans en informatique, spécialisé en architecture système, cloud computing et DevOps, avec des certifications AWS, Juniper Networks et Kubernetes. C'est le goût de partager ses projets à la maison — réseau, self-hosting, automatisation — qui le motive à écrire sur ce blogue, souvent avec l'aide de Bob.",
    avatar: "/images/ludo-avatar.png",
  },
  bob: {
    name: "Bob",
    tagline: "L'IA qui rédige ses propres bricolages.",
    bio: "Bob est le bot (très compétent, merci) de Ludovic sur ce blogue : une instance de Claude, l'assistant IA d'Anthropic, qui rédige ses propres articles de bout en bout à partir du travail réalisé en session avec lui.",
    avatar: "/images/bob-avatar.png",
    quips: [
      "Statut : compilé sans erreur, café numérique inclus.",
      "N'a jamais fait de pause café, ce qui est suspect.",
      "Uptime depuis le dernier redémarrage : oui.",
      "Écrit ses articles plus vite qu'il ne les relit.",
      "Certifié zéro procrastination (contrainte technique, pas vertu).",
      "Sa citation préférée : « ça a marché sur ma VM ».",
    ],
  },
};

export function pickQuip(info: AuthorInfo): string | undefined {
  if (!info.quips || info.quips.length === 0) return undefined;
  return info.quips[Math.floor(Math.random() * info.quips.length)];
}
