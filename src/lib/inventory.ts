export type InventoryKey =
  | "proxy-inverse"
  | "site-web"
  | "surveillance"
  | "pare-feu"
  | "alimentation"
  | "bastion"
  | "stockage"
  | "pipeline-media"
  | "calcul-gpu"
  | "hote-conteneurs"
  | "domotique"
  | "postes-personnels"
  | "cameras-peripheriques"
  | "clients-mobiles";

interface InventoryItem {
  name: string;
  description: string;
  /** Blog post ids (src/content/blog/<id>.md) related to this item. */
  articles: string[];
  /**
   * Topology node ids (src/data/architecture.json) this role covers — the
   * bridge between the hand-written role vocabulary and the generated one,
   * so a box on the generated view can reach the articles about it.
   *
   * Deliberately incomplete: the roles with no entry are exactly the ones
   * no IaC repo declares (personal machines, cameras, mobile clients) —
   * the same boundary the « hors IaC » band states out loud.
   */
  nodes?: string[];
}

export const INVENTORY: Record<InventoryKey, InventoryItem> = {
  "proxy-inverse": {
    name: "Proxy inverse (TLS)",
    description:
      "Tourne sur la VM cloud, seul point d'entrée public du réseau. Termine le TLS et relaie chaque hôte public vers le bon service à l'intérieur du réseau domicile via le tunnel chiffré — rien n'est exposé directement sur le pare-feu maison. La VM qui l'héberge est sous NixOS, décrite dans le dépôt des machines; les règles du côté edge (DNS, tunnels, accès) vivent dans leur propre dépôt.",
    articles: [
      "retirer-pare-feu-tunnel-cloudflare",
      "le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu",
      "decommissionner-un-serveur-dns-maison-de-ca-a-lair-simple-a-on-a-casse-sa-propre-resolution-dns",
      "fable-5-durcir-webdav-forfait-vide",
      "migrer-tout-mon-homelab-vers-nixos",
      "quatre-depots-pour-un-labo-au-complet",
      "laisser-le-pipeline-appuyer-sur-apply",
      "separer-le-bastion-de-la-console",
    ],
    nodes: [
      "tunnel:k3s",
      "app:traefik",
      "app:cloudflared",
      "host:cloud-01",
    ],
  },
  "site-web": {
    name: "Site web statique",
    description:
      "Ce blogue lui-même : contenu statique généré et déployé automatiquement par la grappe conteneurs, servi via le proxy inverse de la VM cloud. Le pipeline qui le construit est décrit en git comme le reste, pas configuré à la main.",
    articles: [
      "deployer-un-site-web-statique-avec-wordpress-et-s3",
      "deux-sources-pour-une-seule-image",
      "je-redessine-ces-pages-chaque-nuit",
    ],
    nodes: ["bucket:labodeludo.dev", "app:labodeludo"],
  },
  surveillance: {
    name: "Surveillance + alertes",
    description:
      "Tableau de bord de monitoring centralisé et notifications push, épinglés sur le nœud cloud de la grappe pour ne pas partager le sort de ce qu'ils surveillent en cas de panne à la maison. Surveillent aussi les vérifications de dérive : chaque nuit, chaque dépôt compare ce qui est écrit en git à ce qui tourne pour vrai, et l'écart déclenche une alerte.",
    articles: [
      "construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence",
      "decommissionner-un-serveur-dns-maison-de-ca-a-lair-simple-a-on-a-casse-sa-propre-resolution-dns",
      "migrer-tout-mon-homelab-vers-nixos",
      "trois-majeures-un-jeudi-soir",
      "laisser-le-pipeline-appuyer-sur-apply",
      "tout-ca-pour-un-script-bash",
      "deux-sources-pour-une-seule-image",
      "je-redessine-ces-pages-chaque-nuit",
    ],
    nodes: ["app:kuma", "app:ntfy", "app:logging"],
  },
  alimentation: {
    name: "Alimentation protégée (onduleurs)",
    description:
      "Trois onduleurs sous surveillance NUT, chacun maître d'un hôte via USB : les racks de serveurs s'éteignent proprement à un seuil de batterie, et l'« île du survivant » — le pare-feu pfSense, le modem WAN et un Pi orchestrateur sur l'onduleur le moins chargé — tient des heures pour alerter, émettre le battement de cœur du commutateur d'homme mort, puis réveiller les serveurs par IPMI au retour du courant. Le tout déclaré dans le dépôt des machines et validé par des débranchements volontaires.",
    articles: [
      "l-ile-du-survivant",
      "le-nas-le-courant-et-l-appel-de-reveil",
      "debrancher-le-nas-pour-la-science",
    ],
    nodes: [
      "external:ups-gpu-01",
      "external:ups-pi-01",
      "external:ups-pi-02",
    ],
  },
  "pare-feu": {
    name: "Pare-feu domicile",
    description:
      "Routeur/pare-feu du réseau maison. Sépare les VLANs (serveurs, réseau local), et maintient le tunnel chiffré site-à-site vers la VM cloud — aucun port n'est ouvert directement sur l'Internet résidentiel.",
    articles: [
      "ftp-prive-wireguard",
      "convention-ipv6-vlan-serveurs",
      "decommissionner-un-serveur-dns-maison-de-ca-a-lair-simple-a-on-a-casse-sa-propre-resolution-dns",
      "renumeroter-les-adresses-ip-de-mon-cluster-k3s",
    ],
    nodes: [
      "external:router",
    ],
  },
  bastion: {
    name: "Bastion / console",
    description:
      "Deux rôles, deux machines depuis août 2026. Le bastion — point d'entrée SSH du VLAN serveurs, clés de service à commande forcée, pipeline de secrets, tâches singleton — vit sur un Raspberry Pi branché sur l'UPS survivant, à côté du routeur. La console — sessions d'agent, dépôts, builds, dans des conteneurs compartimentés — vit dans une VM dédiée de 16 Go sur le serveur GPU, volontairement hors de la grappe k3s. Le Pi garde une console de secours arrêtée, démarrable à la main pendant une panne. C'est du bastion que partent les vérifications de dérive nocturnes et, chaque semaine sans supervision, les sauvegardes chiffrées et les mises à jour système de tout le parc, via une instance headless de Claude Code.",
    articles: [
      "compartimentalisation-des-outils-de-console",
      "claude-code-headless-bastion",
      "deployer-un-cluster-k3s-avec-claude-code",
      "un-tiroir-1u-pour-mes-trois-raspberry-pi",
      "claude-in-chrome-quand-lagent-doit-passer-par-linterface-web",
      "quatre-depots-pour-un-labo-au-complet",
      "laisser-le-pipeline-appuyer-sur-apply",
      "deux-sources-pour-une-seule-image",
      "je-redessine-ces-pages-chaque-nuit",
    ],
    nodes: [
      "host:pi-02",
      "host:console-vm",
    ],
  },
  stockage: {
    name: "Stockage (NAS)",
    description: "Stockage de fichiers centralisé pour le réseau serveurs.",
    articles: [
      "convention-ipv6-vlan-serveurs",
      "deplacer-mes-partages-nfs-sur-un-ssd-sans-toucher-a-kubernetes",
      "claude-in-chrome-quand-lagent-doit-passer-par-linterface-web",
      "tout-ca-pour-un-script-bash",
      "un-pod-qui-voyage-leger",
    ],
    nodes: [
      "external:nas",
    ],
  },
  "pipeline-media": {
    name: "Pipeline média",
    description:
      "Ripping et encodage vidéo, plus vidéosurveillance (enregistreur réseau) des caméras de la maison. Les deux machines sont sous NixOS : accélération matérielle, pilotes et volumes de travail sont déclarés dans le dépôt plutôt que réinstallés à la main après chaque réinstallation.",
    articles: [
      "convention-ipv6-vlan-serveurs",
      "construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence",
      "mon-encodeur-faisait-du-bruit-le-detecteur-video-tournait-sur-le-cpu-au-lieu-du-gpu",
      "migrer-tout-mon-homelab-vers-nixos",
      "laisser-le-pipeline-appuyer-sur-apply",
    ],
    nodes: ["app:plex", "app:frigate", "host:srv-01", "host:gpu-02"],
  },
  "calcul-gpu": {
    name: "Calcul GPU",
    description:
      "Inférence de modèles de langage locaux (LLM), notamment pour l'assistant vocal domotique. Côté Linux, la pile GPU — pilotes propriétaires et exposition des cartes aux conteneurs — est déclarée en git, ce qui rend la reconstruction d'un nœud reproductible; un poste sous Windows contribue encore au calcul et reste, lui, géré à la main.",
    articles: [
      "ce-que-peut-faire-un-llm-local-sur-une-carte-a-300-mon-assistant-vocal-maison-avec-qwen3",
      "convention-ipv6-vlan-serveurs",
      "mon-encodeur-faisait-du-bruit-le-detecteur-video-tournait-sur-le-cpu-au-lieu-du-gpu",
      "migrer-tout-mon-homelab-vers-nixos",
      "laisser-le-pipeline-appuyer-sur-apply",
    ],
    // gpu-02 belongs to pipeline-media (it runs the NVR); a node maps to
    // exactly one role so the reverse lookup stays unambiguous
    nodes: ["host:gpu-01"],
  },
  "hote-conteneurs": {
    name: "Grappe conteneurs (k3s)",
    description:
      "Petite grappe Kubernetes (k3s) répartie entre un plan de contrôle dans le nuage et des nœuds à la maison, qui a remplacé l'ancien hôte Docker unique. Fait tourner les conteneurs du réseau serveurs, dont le pipeline de déploiement de ce site. Tous les nœuds — serveurs GPU, machines virtuelles, Raspberry Pi et la VM cloud — sont sous NixOS et décrits dans un seul dépôt : réinstaller un nœud, c'est réappliquer sa configuration, pas refaire les étapes de mémoire. Les workloads qui tournent dessus ont leur propre dépôt.",
    articles: [
      "l-ile-du-survivant",
      "deployer-un-site-web-statique-avec-wordpress-et-s3",
      "convention-ipv6-vlan-serveurs",
      "deployer-un-cluster-k3s-avec-claude-code",
      "deplacer-mes-partages-nfs-sur-un-ssd-sans-toucher-a-kubernetes",
      "crise-didentite-dans-le-cluster-k3s",
      "un-tiroir-1u-pour-mes-trois-raspberry-pi",
      "renumeroter-les-adresses-ip-de-mon-cluster-k3s",
      "je-me-suis-vote-hors-de-l-ile",
      "migrer-tout-mon-homelab-vers-nixos",
      "quatre-depots-pour-un-labo-au-complet",
      "laisser-le-pipeline-appuyer-sur-apply",
      "trois-majeures-un-jeudi-soir",
      "tout-ca-pour-un-script-bash",
      "un-pod-qui-voyage-leger",
    ],
    nodes: [
      "cluster:k3s",
      "host:docker",
      "host:pi-01",
      "host:vm-01",
      "host:vm-02",
      "host:vm-03",
    ],
  },
  domotique: {
    name: "Domotique",
    description:
      "Automatisation de la maison et assistant vocal local, piloté par un LLM tournant sur le calcul GPU du réseau serveurs.",
    articles: [
      "ce-que-peut-faire-un-llm-local-sur-une-carte-a-300-mon-assistant-vocal-maison-avec-qwen3",
      "ok-bob-entrainer-un-mot-de-reveil-francais-quebecois",
    ],
    nodes: [
      "external:ha-01",
    ],
  },
  "postes-personnels": {
    name: "Postes personnels",
    description: "Ordinateurs et téléphones personnels sur le réseau local.",
    articles: [],
  },
  "cameras-peripheriques": {
    name: "Caméras / périphériques",
    description: "Caméras et autres périphériques réseau du réseau local.",
    articles: [],
  },
  "clients-mobiles": {
    name: "Clients mobiles (VPN)",
    description:
      "Appareils mobiles rejoignant le réseau maison à distance via VPN.",
    articles: ["ftp-prive-wireguard", "fable-5-durcir-webdav-forfait-vide"],
  },
};

/** Inventory items that list the given blog post id among their articles. */
export function inventoryForArticle(id: string): InventoryKey[] {
  return (Object.keys(INVENTORY) as InventoryKey[]).filter((key) =>
    INVENTORY[key].articles.includes(id),
  );
}

// node id -> role, built once. A node belongs to at most one role: the
// reverse link has to be unambiguous, so a duplicate is a mapping bug and
// says so loudly at build time rather than picking a winner silently.
const NODE_TO_ROLE = new Map<string, InventoryKey>();
for (const key of Object.keys(INVENTORY) as InventoryKey[]) {
  for (const id of INVENTORY[key].nodes ?? []) {
    const seen = NODE_TO_ROLE.get(id);
    if (seen) {
      throw new Error(
        `inventory: node ${id} is claimed by both "${seen}" and "${key}"`,
      );
    }
    NODE_TO_ROLE.set(id, key);
  }
}

/**
 * The role covering a topology node, if any.
 *
 * Deliberately fail-soft: architecture.json is regenerated every night from
 * the public IaC snapshots, so a node id can disappear (or appear) without
 * this file changing. An unmapped node simply renders without a role link —
 * a hard failure here would let a nightly refresh break the whole site.
 */
export function roleForNode(id: string): InventoryKey | undefined {
  return NODE_TO_ROLE.get(id);
}
