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
  },
  "site-web": {
    name: "Site web statique",
    description:
      "Ce blogue lui-même : contenu statique généré et déployé automatiquement par la grappe conteneurs, servi via le proxy inverse de la VM cloud. Le pipeline qui le construit est décrit en git comme le reste, pas configuré à la main.",
    articles: ["deployer-un-site-web-statique-avec-wordpress-et-s3"],
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
    ],
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
