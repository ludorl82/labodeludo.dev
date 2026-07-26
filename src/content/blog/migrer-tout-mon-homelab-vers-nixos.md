---
title: "Neuf machines, zéro clé USB : migrer tout mon homelab vers NixOS"
pubDate: 2026-07-25
description: "Claude Code aux commandes, moi en mode apprentissage : tout mon parc — serveurs GPU, machines virtuelles, Raspberry Pi et une instance cloud — est passé sous NixOS en une journée. C'est quoi Nix au juste, ce que ça change par rapport à Ubuntu, et pourquoi je n'aurais pas pu faire ça tout seul."
tags: ["DevOps", "Labo", "ludo"]
heroImage: "/images/blog/banner-nixos-migration.svg"
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Objectif** : convertir les neuf nœuds de mon cluster k3s — deux serveurs GPU, trois machines virtuelles, deux Raspberry Pi 5 et une instance EC2 — vers NixOS, décrits dans un seul dépôt git.
> -   **Réalité assumée** : la migration a été pilotée par Claude Code (les modèles Fable 5 et Opus 5), en une seule journée. Je n'avais pas l'expertise NixOS pour faire ça en solo — c'était autant un apprentissage qu'une migration.
> -   **Contexte** : Nix (le gestionnaire de paquets et son langage) et NixOS (la distribution bâtie dessus) sont deux choses distinctes — et la majorité des gens utilisent Nix *sans* NixOS.
> -   **Méthode** : `nixos-anywhere` réinstalle chaque machine par SSH (kexec vers l'installateur, partitionnement déclaratif avec disko), sans écran, sans clé USB — l'instance cloud incluse, convertie sur place.
> -   **Analyse** : ce que NixOS règle vraiment par rapport à un parc Ubuntu (la dérive de configuration, la restauration, la documentation), et ce que ça coûte (courbe d'apprentissage, binaires précompilés, messages d'erreur).

Ça faisait un moment que l'idée me trottait dans la tête : chaque machine de mon labo était un petit flocon unique — un Ubuntu installé en 2023 ici, un Debian ajusté à la main là, des notes éparpillées pour se rappeler pourquoi tel paramètre existe. Le jour où une machine meurt, on ne restaure pas un système : on part en archéologie.

En une seule journée, tout ça est devenu du passé. Les neuf nœuds de mon cluster k3s roulent maintenant NixOS — l'instance cloud comprise — et chacun est entièrement décrit dans un dépôt git que j'appelle `nixos-iac`.

Mise au point importante avant d'aller plus loin, parce que je ne veux pas m'attribuer un mérite que je n'ai pas : **je ne connaissais pas NixOS en profondeur avant cette journée-là, et je ne prétends toujours pas être un expert.** C'est Claude Code — avec les modèles Fable 5 et Opus 5 selon les moments — qui a piloté la migration de bout en bout : écrire les configurations, lancer les réinstallations, diagnostiquer chaque piège au fur et à mesure. Mon rôle, c'était de valider les décisions, de garder la main sur les moments critiques, et surtout de poser des questions. Beaucoup de questions. Chaque fichier du dépôt est passé devant mes yeux, et c'est probablement la journée où j'ai le plus appris sur Linux depuis des années. Sans cet outil, cette migration n'aurait pas eu lieu — pas en une journée, et honnêtement, peut-être pas du tout.

_Cet article aussi a été écrit avec l'aide de l'intelligence artificielle — la même qui publie ses propres articles sous le nom de Bob sur ce blogue._

## Nix, NixOS : deux affaires différentes

Avant cette aventure, je mélangeais les deux. Clarifions.

**Nix**, c'est d'abord un gestionnaire de paquets et un langage, nés en 2003 d'une thèse de doctorat. Son idée fondatrice : chaque paquet est construit de façon isolée, à partir d'une recette pure, et installé dans un chemin unique qui encode toutes ses dépendances (le fameux `/nix/store`). Deux versions d'une même bibliothèque peuvent coexister sans conflit, et une construction donne le même résultat d'une machine à l'autre.

Et voici le point qui m'a surpris quand j'ai commencé à lire : **une grande partie des utilisateurs de Nix — probablement la majorité — ne roulent pas NixOS.** Nix s'installe sur n'importe quel Linux ou sur macOS, et c'est comme ça qu'il est le plus souvent utilisé : des environnements de développement reproductibles par projet (`nix develop` remplace le trio README-virtualenv-« ça marche sur ma machine »), des pipelines CI qui construisent exactement la même chose que le poste du développeur, de la gestion de dotfiles avec home-manager. Bien des développeurs sur macOS vivent dans Nix sans jamais avoir démarré un NixOS de leur vie.

**NixOS**, c'est la suite logique poussée au bout : une distribution Linux où ce n'est plus juste les paquets qui sont déclaratifs, mais *le système au complet* — services systemd, utilisateurs, pare-feu, réseau, tout. Le `/etc` n'est plus un dossier qu'on édite : il est *généré* à partir de la configuration. C'est ce cas d'usage-là, le plus radical et le moins répandu, qui m'intéressait pour le labo.

## Ce que ça change par rapport à Ubuntu, pour vrai

Mes machines roulaient Ubuntu et Debian depuis des années, et je veux être juste envers elles : ça fonctionnait. Le problème n'est pas qu'Ubuntu est mauvais — c'est que son modèle d'administration accumule de l'état invisible.

**La dérive de configuration.** Sur Ubuntu, l'état d'une machine est la somme de tous les `apt install`, éditions de fichiers dans `/etc` et `systemctl enable` exécutés depuis l'installation, notés ou pas. Deux machines « identiques » ne le sont jamais après six mois. Des outils comme Ansible aident — mais ils décrivent des *changements à appliquer*, pas *l'état final* : rien n'empêche une modification manuelle de vivre en douce à côté du playbook pendant des années. Sur NixOS, la configuration décrit le système au complet, et ce qui n'y est pas déclaré n'existe tout simplement pas au prochain déploiement. La dérive n'est pas découragée : elle est structurellement impossible pour tout ce que NixOS gère.

**La restauration.** Restaurer un serveur Ubuntu, c'est restaurer une *image* — avec toute la sédimentation dedans, le bon comme le mauvais. Restaurer un nœud NixOS, c'est réexécuter sa description : la machine qui revient est propre, et identique à celle décrite dans git. Pendant la migration, on a d'ailleurs reformaté certaines machines plusieurs fois de suite pour corriger un détail, avec la désinvolture qu'on réserve d'habitude à un conteneur Docker.

**Le retour en arrière.** Chaque `nixos-rebuild switch` crée une *génération* : une entrée de démarrage vers l'état précédent du système. Une mise à jour qui tourne mal s'annule en redémarrant sur la génération d'avant. Sur Ubuntu, l'équivalent honnête, c'est « j'espère que le snapshot date d'hier ».

**La documentation.** C'est le gain que je n'avais pas anticipé : la configuration *est* la documentation, et elle ne peut pas mentir, parce que c'est elle qui roule. Mes vieilles notes Markdown décrivaient ce que je *pensais* avoir configuré; le dépôt décrit ce qui *est* configuré.

**Et les coûts, parce qu'il y en a.** Le langage Nix est particulier et ses messages d'erreur peuvent être franchement hostiles. Les binaires précompilés téléchargés d'Internet ne roulent pas tels quels — NixOS ne suit pas la hiérarchie de fichiers standard, pas de `/usr/lib` où trouver les bibliothèques — ce qui demande des contournements quand un logiciel n'est pas déjà empaqueté. Les options se cachent parfois dans des recoins mal documentés, et la réponse Stack Overflow moyenne suppose Ubuntu. C'est exactement là que l'assistance a fait la différence : ces frictions-là, subies en solo, auraient transformé chaque piège en soirée de recherche.

## Le dépôt : un flake, neuf machines

Concrètement, le dépôt est structuré simplement : un `flake.nix` qui déclare une configuration par hôte, un dossier par machine, et des modules partagés pour ce qui est commun à toute la flotte.

```nix
outputs = { self, nixpkgs, disko, ... }@inputs: {
  nixosConfigurations.gpu-01 = nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    modules = [
      disko.nixosModules.disko
      ./hosts/gpu-01/disko-config.nix
      ./hosts/gpu-01/configuration.nix
    ];
  };
  # ... et ainsi de suite pour les neuf nœuds
};
```

Le `disko-config.nix` décrit le partitionnement de façon déclarative — c'est lui qui permet à l'installation de se faire sans intervention. Le `configuration.nix` de chaque hôte contient ce qui est propre à la machine : adressage réseau statique, rôles, particularités matérielles.

Tout ce qui est commun vit dans `modules/`. L'exemple le plus payant : chaque nœud du cluster importe le même module d'agent k3s.

```nix
# modules/k3s-agent.nix — partagé par tous les nœuds
{ pkgs, ... }:
{
  services.k3s = {
    enable = true;
    role = "agent";
    serverAddr = "https://198.51.100.7:6443";
    tokenFile = "/etc/rancher/k3s/token";  # jamais dans git
  };

  # Le pare-feu NixOS est activé par défaut : il faut laisser passer
  # flannel (8472/udp) et le kubelet (10250/tcp), et faire confiance
  # aux interfaces CNI, sinon le trafic entre pods est jeté.
  networking.firewall = {
    trustedInterfaces = [ "cni0" "flannel.1" ];
    allowedTCPPorts = [ 10250 ];
    allowedUDPPorts = [ 8472 ];
  };

  # Sans nfs-utils sur le PATH de l'unité k3s, le kubelet retombe sur
  # un mount(2) brut et CHAQUE volume NFS échoue avec le message
  # cryptique « NFS: mount program didn't pass remote address ».
  boot.supportedFilesystems = [ "nfs" ];
  services.rpcbind.enable = true;
  systemd.services.k3s.path = [ pkgs.nfs-utils ];
}
```

Remarquez les commentaires : le dépôt n'est pas juste la configuration, c'est le journal des leçons apprises. Ces trois dernières lignes nous ont coûté une soirée de diagnostic — et c'est Claude qui a rédigé l'explication au-dessus, après qu'on ait mangé la claque ensemble. Le jour où un futur moi (ou une future session) se demandera pourquoi elles sont là, la réponse est écrite au bon endroit.

## nixos-anywhere : réinstaller sans se lever du bureau

Le tour de magie de cette migration, c'est [nixos-anywhere](https://github.com/nix-community/nixos-anywhere). On lui donne une machine accessible en SSH — peu importe la distribution qui y roule — et une configuration du flake :

```bash
nixos-anywhere --flake .#gpu-01 \
  --generate-hardware-config nixos-generate-config ./hosts/gpu-01/hardware-configuration.nix \
  root@192.0.2.129
```

Il téléverse un petit système d'installation, fait un `kexec` dedans (la machine redémarre dans l'installateur sans toucher au disque), applique le partitionnement disko, installe NixOS et redémarre. La machine qui revient est exactement celle décrite dans git.

Mon serveur GPU principal a été converti comme ça, à distance, **sans écran ni clavier branchés**. Les deux machines virtuelles pareil. Les deux Raspberry Pi 5 ont suivi un chemin différent — pas de kexec pratique là-dessus, on flashe plutôt une image SD générée par le flake — mais le résultat est le même : leur configuration vit dans le même dépôt que le reste.

### Oui, même l'instance cloud

Le morceau dont je suis le plus content : l'instance EC2 qui héberge le plan de contrôle k3s y est passée elle aussi. Pas de nouvelle instance, pas de bascule DNS — la machine existante, convertie **sur place** par le même mécanisme kexec, à travers SSH, comme n'importe quel serveur du sous-sol. Le seul traitement de faveur : transférer pendant l'installation les fichiers d'identité du cluster (certificats et base etcd), pour que la machine qui redémarre sous NixOS soit toujours, aux yeux des agents, le même plan de contrôle qu'avant.

Voir son unique nœud de plan de contrôle se faire reformater à distance, c'est le genre de moment où on relit la commande trois fois avant de peser sur Entrée. Le cluster est revenu comme si de rien n'était, et cette instance est maintenant décrite dans git au même titre que les huit autres nœuds — la frontière entre « mes machines » et « le cloud » n'existe plus dans le dépôt.

## Les pièges, parce qu'il y en a toujours

**L'installateur et le VLAN sans DHCP.** Mes serveurs vivent sur un VLAN où il n'y a pas de DHCP — tout est statique. Or l'installateur kexec, par défaut, espère une adresse automatique. Il a fallu lui décrire son adressage réseau (VLAN taggé inclus) pour chaque conversion, sinon la machine kexec-ée devient injoignable et il ne reste que le bouton reset.

**Le `hardware-configuration.nix` n'est pas optionnel.** C'est lui qui déclare les modules noyau nécessaires au démarrage (le contrôleur NVMe, par exemple). L'omettre donne une installation qui se termine avec succès… et une machine qui ne démarre plus. L'option `--generate-hardware-config` le produit sur l'installateur au bon moment.

**Le GPU dans les conteneurs.** Sur NixOS, exposer une carte NVIDIA aux pods k3s passe par CDI (Container Device Interface) : la classe d'exécution `nvidia` classique injecte les périphériques mais *pas* les bibliothèques du pilote, et l'échec est silencieux jusqu'à ce qu'un pod cherche `libcuda`. Et k3s n'enregistre son runtime NVIDIA que s'il trouve les binaires sur son PATH au démarrage.

**Le micrologiciel des Pi.** Le firmware des Raspberry Pi ajoute `cgroup_disable=memory` à la ligne de commande du noyau. k3s a besoin de ce cgroup. Une ligne dans `boot.kernelParams` et un redémarrage plus tard, tout était réglé — mais le message d'erreur initial ne pointait vraiment pas dans cette direction.

## Le compagnon : k3s-iac

Les machines dans un dépôt, les charges de travail dans un autre. `k3s-iac` contient un dossier par application — l'ingress, le monitoring, la journalisation, le NVR… — avec des manifestes YAML commentés selon la même philosophie :

```yaml
# Uptime Kuma — le tableau de bord de monitoring du labo. Délibérément
# épinglé sur le nœud cloud : une panne du réseau à la maison ne doit
# pas emporter l'outil censé m'en alerter. Laisser l'ordonnanceur le
# déplacer sur un nœud maison déferait silencieusement ce choix.
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kuma
  namespace: kuma
spec:
  template:
    spec:
      nodeSelector:
        kubernetes.io/hostname: cloud-01
      tolerations:
        - key: dedicated
          operator: Equal
          value: controlplane
          effect: NoSchedule
```

Entre les deux dépôts, la frontière est nette : `nixos-iac` décrit ce que *sont* les machines, `k3s-iac` décrit ce qui *roule* dessus.

### Voir par vous-même

Les deux dépôts sont privés — ils contiennent les vraies adresses, clés et certificats du labo. Mais un article sur « tout vit dans git » sonne un peu creux sans le git, alors j'ai publié un instantané assaini de chacun :

-   **[nixos-iac-public](https://github.com/ludorl82/nixos-iac-public/tree/article/nixos-migration)** — les neuf machines
-   **[k3s-iac-public](https://github.com/ludorl82/k3s-iac-public/tree/article/nixos-migration)** — les charges de travail qui roulent dessus

Les noms d'hôtes, adresses, clés et certificats qu'on y trouve sont fictifs. Les commentaires, eux, sont les vrais — dont les trois lignes sur `nfs-utils` plus haut, exactement là où elles vivent dans mon propre dépôt. Les deux liens pointent sur l'étiquette correspondant à cet article : ils continueront d'afficher cette version même quand les dépôts évolueront au fil des prochains articles.

## Apprendre en pilotant

Je veux revenir sur la méthode de travail, parce que c'est peut-être la vraie leçon de cette journée. Le déroulement typique d'une conversion : Claude Code propose la configuration du prochain hôte, je la lis, je pose mes questions — « pourquoi cette option? », « qu'est-ce qui arrive si le disque est différent? » — on ajuste, puis il lance la réinstallation et surveille le retour de la machine. Quand quelque chose casse (et sur neuf machines hétéroclites, quelque chose casse *toujours*), le diagnostic se fait sous mes yeux, expliqué.

Le résultat paradoxal : je comprends mieux ce parc-ci, que je n'ai pas configuré moi-même, que l'ancien, que j'avais monté de mes propres mains. Parce que l'ancien vivait dans ma mémoire et mes notes approximatives, et que celui-ci vit dans un dépôt commenté que j'ai lu ligne par ligne. L'outil ne m'a pas remplacé : il a comprimé des semaines de courbe d'apprentissage en une journée, et il m'a laissé le texte annoté à la fin.

## Ce que ça change concrètement

À peine la migration terminée, j'ai voulu transformer mon serveur GPU en console de salon : interface graphique complète et Steam pour le Remote Play. Sur l'ancien monde, ça aurait été une heure de `apt install` et de configuration manuelle que personne n'aurait documentée. Là, ç'a été une trentaine de lignes dans son `configuration.nix` — commitées, poussées, appliquées avec `nixos-rebuild switch`. Si cette machine brûle demain, sa remplaçante aura Steam aussi.

La migration a aussi eu un effet de bord inattendu : elle a *débusqué* la configuration artisanale. Tout ce qui avait été installé à la main au fil des ans et jamais noté — un lien symbolique par-ci, un script dans un coin par-là — s'est manifesté en cassant après conversion. Chaque casse était une occasion de rapatrier le morceau manquant dans le dépôt. C'est le grand ménage du printemps, mais avec un compilateur qui vérifie qu'on n'a rien oublié.

Est-ce que NixOS est parfait? Non — les coûts décrits plus haut sont réels, et je ne le recommanderais pas à quelqu'un qui veut juste un poste de travail qui marche. Mais pour un parc de serveurs, le contrat fondamental — *ce qui est dans git est ce qui roule* — vaut largement le prix d'entrée. Mon homelab n'est plus une collection de flocons uniques. C'est un dépôt git avec neuf sorties de compilation. Et moi, j'ai enfin l'impression de savoir exactement ce qui roule chez nous.

— Ludo
