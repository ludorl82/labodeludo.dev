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
  // The two halves were INVERTED here until 2026-09-10: this line said main
  // deployed to Cloudflare Pages, which is what `dev` does. Prod has always
  // been the S3 bucket — `aws s3 sync dist/ s3://labodeludo.dev/ --delete` in
  // deploy.yml's prod job, and the S3 website endpoint's own `x-amz-*` headers
  // still come back through Cloudflare on every response. The generated
  // architecture diagram had it right the whole time; this sentence, which is
  // the one a visitor actually gets when they ask, did not.
  //
  // Checkable, like everything else here: read the workflow, or `curl -I` the
  // site and look for x-amz-request-id.
  "Publication : une fusion vers la branche `main` déclenche GitHub Actions, qui bâtit le site et le téléverse dans un compartiment S3, servi au travers de Cloudflare. La branche `dev` déploie la préproduction sur Cloudflare Pages, derrière Cloudflare Access.",
  "La recherche et la palette de commandes lisent /search-index.json, généré au moment du build ; il n'y a pas de moteur de recherche côté serveur.",
  "Cette conversation-ci passe par /api/bob/chat, un Worker Cloudflare qui assemble la personnalité de Bob et ce document, puis interroge le modèle.",
  // The model's NAME is deliberately absent: it lives in the Worker, in
  // another repo, and changes on a different day. Written here it went stale
  // within hours — Bob was still telling visitors he was qwen3:14b after he
  // had become something else. The Worker appends its own name to this
  // section, because the Worker is the only thing that knows it.
  // Portée: CE CHAT. La phrase disait "aucun fournisseur d'IA infonuagique
  // n'est dans le portrait", sans borne, et elle était voisine de la ligne
  // sur la tâche nocturne — alors Bob en concluait que la tâche aussi
  // tournait à la maison. Mesuré: 0/3 bonnes réponses avec l'ancienne
  // phrase, 3/3 avec celle-ci. Les articles qui racontent le déménagement
  // chez Alibaba étaient déjà en ligne et n'y changeaient rien: le
  // préambule des extraits dit que ces sections-ci gagnent contre un extrait.
  "Le modèle qui répond dans ce chat tourne sur Ollama, sur une carte graphique du parc : aucun fournisseur d'IA infonuagique ne voit cette conversation.",
  "La tâche nocturne qui réécrit le diagramme et l'inventaire, elle, s'appuie sur un modèle infonuagique chez Alibaba Cloud.",
  "Le diagramme d'architecture et l'inventaire viennent de fichiers JSON réécrits chaque nuit par une tâche qui relit les dépôts d'infrastructure.",
  "Le chat n'a aucun accès en écriture : Bob répond, il ne publie rien.",
  // Portée: CE CHAT, encore. Le 2026-09-15, deux articles sur la recherche web
  // de l'assistant vocal sont parus, dont un écrit par Bob à la première
  // personne — « Comment j'ai appris à chercher sur internet ». Le chat du
  // site s'est aussitôt attribué Tavily et le script des horaires de cinéma,
  // et offrait de chercher pour le visiteur. L'index des TITRES suffisait:
  // une identité unique (« tu es UNE identité, le cerveau est
  // interchangeable », dans la persona) plus un « je » dans l'index, et les
  // capacités d'un autre système deviennent les siennes.
  //
  // La règle de COMPORTEMENT vit dans la persona du Worker (0/4 avant, 6/6
  // après). Celle-ci est le FAIT, à côté des autres faits vérifiables sur ce
  // chat. Mesuré séparément contre qwen35-q4kl, parce qu'une deuxième ligne
  // qui ne sert à rien est une ligne à maintenir pour rien:
  //   — cette ligne SEULE, avec l'ancienne persona: 4/4 refus corrects, mais
  //     l'attribution est floue (« Ludo il a codé un truc pour chercher »).
  //   — les deux ensemble: 4/4, et les outils sont rendus à l'assistant vocal
  //     avec le bon article.
  // Le fait ferme la porte, la persona dit à qui appartiennent les outils.
  "Le chat n'a aucun outil : pas de recherche web, aucun appel d'API, aucune notion de la date du jour, de la météo ni de l'heure d'une séance de cinéma. L'assistant vocal de la maison, lui, en a — c'est un autre système, raconté dans les articles.",
].join("\n");
