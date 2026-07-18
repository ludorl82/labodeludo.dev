export type InventoryKey =
  | "proxy-inverse"
  | "site-web"
  | "surveillance"
  | "pare-feu"
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
      "Tourne sur la VM cloud, seul point d'entrée public du réseau. Termine le TLS et relaie chaque hôte public vers le bon service à l'intérieur du réseau domicile via le tunnel chiffré — rien n'est exposé directement sur le pare-feu maison.",
    articles: [
      "retirer-pare-feu-tunnel-cloudflare",
      "le-move-qui-echouait-une-histoire-de-proxy-de-schema-http-et-dun-coffre-fort-presque-corrompu",
    ],
  },
  "site-web": {
    name: "Site web statique",
    description:
      "Ce blogue lui-même : contenu statique généré et déployé automatiquement, servi via le proxy inverse de la VM cloud.",
    articles: ["deployer-un-site-web-statique-avec-wordpress-et-s3"],
  },
  surveillance: {
    name: "Surveillance + alertes",
    description:
      "Tableau de bord de monitoring centralisé et notifications push, hébergé sur la VM cloud pour ne pas partager le sort de ce qu'il surveille en cas de panne à la maison.",
    articles: [
      "construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence",
    ],
  },
  "pare-feu": {
    name: "Pare-feu domicile",
    description:
      "Routeur/pare-feu du réseau maison. Sépare les VLANs (serveurs, réseau local), et maintient le tunnel chiffré site-à-site vers la VM cloud — aucun port n'est ouvert directement sur l'Internet résidentiel.",
    articles: ["ftp-prive-wireguard", "convention-ipv6-vlan-serveurs"],
  },
  bastion: {
    name: "Bastion / console",
    description:
      "Point d'entrée SSH du VLAN serveurs. Exécute les outils de développement et les sessions d'agent dans des conteneurs compartimentés plutôt que directement sur l'hôte. Orchestre aussi les sauvegardes chiffrées hebdomadaires, la nuit, de tous les nœuds de la grappe conteneurs.",
    articles: [
      "compartimentalisation-des-outils-de-console",
      "deployer-un-cluster-k3s-avec-claude-code",
    ],
  },
  stockage: {
    name: "Stockage (NAS)",
    description: "Stockage de fichiers centralisé pour le réseau serveurs.",
    articles: ["convention-ipv6-vlan-serveurs"],
  },
  "pipeline-media": {
    name: "Pipeline média",
    description:
      "Ripping et encodage vidéo, plus vidéosurveillance (enregistreur réseau) des caméras de la maison.",
    articles: [
      "convention-ipv6-vlan-serveurs",
      "construire-un-vrai-reseau-dalarme-pour-son-homelab-et-toutes-les-manieres-dont-ca-peut-foirer-en-silence",
      "mon-encodeur-faisait-du-bruit-le-detecteur-video-tournait-sur-le-cpu-au-lieu-du-gpu",
    ],
  },
  "calcul-gpu": {
    name: "Calcul GPU",
    description:
      "Inférence de modèles de langage locaux (LLM), notamment pour l'assistant vocal domotique.",
    articles: [
      "ce-que-peut-faire-un-llm-local-sur-une-carte-a-300-mon-assistant-vocal-maison-avec-qwen3",
      "convention-ipv6-vlan-serveurs",
      "mon-encodeur-faisait-du-bruit-le-detecteur-video-tournait-sur-le-cpu-au-lieu-du-gpu",
    ],
  },
  "hote-conteneurs": {
    name: "Grappe conteneurs (k3s)",
    description:
      "Petite grappe Kubernetes (k3s) répartie entre un plan de contrôle dans le nuage et des nœuds à la maison, qui a remplacé l'ancien hôte Docker unique. Fait tourner les conteneurs du réseau serveurs, dont le pipeline de déploiement de ce site.",
    articles: [
      "deployer-un-site-web-statique-avec-wordpress-et-s3",
      "convention-ipv6-vlan-serveurs",
      "deployer-un-cluster-k3s-avec-claude-code",
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
    articles: ["ftp-prive-wireguard"],
  },
};

/** Inventory items that list the given blog post id among their articles. */
export function inventoryForArticle(id: string): InventoryKey[] {
  return (Object.keys(INVENTORY) as InventoryKey[]).filter((key) =>
    INVENTORY[key].articles.includes(id),
  );
}
