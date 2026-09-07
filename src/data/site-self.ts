import pkg from "../../package.json";

/**
 * What Bob knows about the site he lives on.
 *
 * He had the fleet and the corpus and nothing about his own plumbing, so
 * "c'est quoi qui fait rouler le blogue ?" — a question a visitor asks in the
 * first minute — got improvised: a container that restarts on every commit,
 * which is not what this is. That is the one failure his whole value rests on
 * not having, and it happened on the most obvious question in the room.
 *
 * The fix is facts, not a refusal. Everything below is checkable from the
 * repository or from the response headers of the page you are reading it on;
 * the grounding file is public and none of this is anything a visitor could
 * not already see. Keep it that way: this is the site's own description, not
 * the lab's, and the machines belong in fleet.json where the sanitizer looks.
 *
 * The Astro version is read rather than typed, because a hand-copied version
 * number is a fact with an expiry date and no alarm. Anything here that cannot
 * be derived is a line someone has to maintain — so keep the list short, and
 * prefer what changes rarely.
 */
const astro = String(pkg.dependencies.astro ?? "").replace(/^[^\d]*/, "");

export const SITE_SELF = [
  `Le site est bâti avec Astro ${astro} et généré en statique : des fichiers HTML, pas de serveur d'application, pas de base de données.`,
  "Le contenu, ce sont des fichiers Markdown/MDX versionnés dans le dépôt Git du site — une collection française, une anglaise, plus les enregistrements de terminal.",
  "Publication : une fusion vers la branche `main` déclenche GitHub Actions, qui bâtit le site et le déploie sur Cloudflare Pages. La branche `dev` déploie la préproduction, derrière Cloudflare Access.",
  "La recherche et la palette de commandes lisent /search-index.json, généré au moment du build ; il n'y a pas de moteur de recherche côté serveur.",
  "Cette conversation-ci passe par /api/bob/chat, un Worker Cloudflare qui assemble la personnalité de Bob et ce document, puis interroge le modèle.",
  "Le modèle est qwen3:14b, servi par Ollama sur une carte graphique du parc. Aucun fournisseur d'IA infonuagique n'est dans le portrait.",
  "Le diagramme d'architecture et l'inventaire viennent de fichiers JSON réécrits chaque nuit par une tâche qui relit les dépôts d'infrastructure.",
  "Le chat n'a aucun accès en écriture : Bob répond, il ne publie rien.",
].join("\n");
