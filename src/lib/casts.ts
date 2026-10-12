import { getCollection, type CollectionEntry } from "astro:content";

export type CastType = CollectionEntry<"casts">["data"]["type"];

/* L'ordre est celui des pastilles du filtre : du plus courant au plus rare. */
export const CAST_TYPES: CastType[] = ["reconstitution", "prise-reelle", "chat", "simulation"];

export const CAST_TYPE_LABELS: Record<"fr" | "en", Record<CastType, string>> = {
  fr: {
    reconstitution: "Reconstitution",
    "prise-reelle": "Prise réelle",
    chat: "Chat du site",
    simulation: "Simulation",
  },
  en: {
    reconstitution: "Reconstruction",
    "prise-reelle": "Real capture",
    chat: "Site chat",
    simulation: "Simulation",
  },
};

/* Une phrase par type, en infobulle de la pastille : ce que le type promet. */
export const CAST_TYPE_HINTS: Record<"fr" | "en", Record<CastType, string>> = {
  fr: {
    reconstitution: "Une session Claude Code remontée après coup à partir de sa transcription réelle",
    "prise-reelle": "La console enregistrée pour vrai avec asciinema",
    chat: "Des réponses du chat du site, capturées mot pour mot",
    simulation: "Un comportement réel, rejoué pour l'enregistrement",
  },
  en: {
    reconstitution: "A Claude Code session rebuilt afterwards from its real transcript",
    "prise-reelle": "The console, recorded for real with asciinema",
    chat: "Answers from the site chat, captured word for word",
    simulation: "A real behaviour, replayed for the recording",
  },
};

/* Un slug d'article mal tapé ne casse rien de visible : le lien disparaît
   simplement des deux côtés. On fait donc échouer le build. */
async function checked(lang: "fr" | "en") {
  const casts = await getCollection(lang === "en" ? "castsEn" : "casts");
  const posts = await getCollection(lang === "en" ? "blogEn" : "blog");
  const known = new Set(posts.map((p) => p.id));
  for (const c of casts) {
    for (const slug of c.data.article) {
      if (!known.has(slug)) {
        throw new Error(`cast ${lang}/${c.id} : article inconnu « ${slug} »`);
      }
    }
  }
  return casts;
}

const byDateAsc = (a: { data: { pubDate: Date } }, b: { data: { pubDate: Date } }) =>
  a.data.pubDate.valueOf() - b.data.pubDate.valueOf();

/** Les enregistrements rattachés à un article, du plus ancien au plus récent :
    l'ordre dans lequel les sessions ont mené au texte. En anglais, un cast qui
    n'existe qu'en français est rendu quand même, marqué `fallback`. */
export async function castsForArticle(slug: string, lang: "fr" | "en" = "fr") {
  const own = (await checked(lang)).filter((c) => c.data.article.includes(slug));
  if (lang === "fr") return own.sort(byDateAsc).map((c) => ({ cast: c, fallback: false }));

  const ownIds = new Set(own.map((c) => c.id));
  const french = (await checked("fr")).filter(
    (c) => c.data.article.includes(slug) && !ownIds.has(c.id),
  );
  return [
    ...own.map((c) => ({ cast: c, fallback: false })),
    ...french.map((c) => ({ cast: c, fallback: true })),
  ].sort((a, b) => byDateAsc(a.cast, b.cast));
}

/** Les articles d'un enregistrement, dans l'ordre de son champ `article`. */
export async function articlesForCast(cast: { data: { article: string[] } }, lang: "fr" | "en" = "fr") {
  await checked(lang);
  const posts = await getCollection(lang === "en" ? "blogEn" : "blog");
  return cast.data.article
    .map((slug) => posts.find((p) => p.id === slug))
    .filter((p): p is NonNullable<typeof p> => !!p);
}
