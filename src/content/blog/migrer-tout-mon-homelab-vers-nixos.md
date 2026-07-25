---
title: "Neuf machines, zéro clé USB : migrer tout mon homelab vers NixOS"
pubDate: 2026-07-25
description: "En deux jours, tout mon parc — serveurs GPU, machines virtuelles, Raspberry Pi et une instance cloud — est passé sous NixOS, réinstallé à distance avec nixos-anywhere. Voici le dépôt qui décrit tout ça, les pièges rencontrés, et pourquoi je ne reviendrais pas en arrière."
tags: ["DevOps", "Labo", "ludo"]
heroImage: "/images/blog/banner-nixos-migration.png"
---

> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> -   **Objectif** : convertir les neuf nœuds de mon cluster k3s — deux serveurs GPU, trois machines virtuelles, deux Raspberry Pi 5 et une instance EC2 — vers NixOS, décrits dans un seul dépôt git.
> -   **Méthode** : `nixos-anywhere` réinstalle chaque machine par SSH (kexec vers l'installateur, partitionnement déclaratif avec disko), sans écran, sans clé USB, même pour l'instance cloud.
> -   **Structure** : un flake, un dossier par hôte, des modules partagés pour ce qui est commun (agent k3s, autorité de certification privée).
> -   **Pièges** : l'installateur qui a besoin d'une IP statique sur un VLAN sans DHCP, le `hardware-configuration.nix` obligatoire sous peine de machine non amorçable, les utilitaires NFS absents du PATH de k3s, le pilote NVIDIA dans les conteneurs, et un micrologiciel de Raspberry Pi qui désactive un cgroup en douce.
> -   **Gain** : la configuration en git *est* la machine. Réinstaller un nœud redonne exactement le même système, et ajouter un rôle complet se fait en quelques lignes versionnées.

Ça faisait un moment que l'idée me trottait dans la tête : chaque machine de mon labo était un petit flocon unique — un Ubuntu installé en 2023 ici, un Debian ajusté à la main là, des notes éparpillées pour se rappeler pourquoi tel paramètre existe. Le jour où une machine meurt, on ne restaure pas un système : on part en archéologie.

En deux jours, tout ça est devenu du passé. Les neuf nœuds de mon cluster k3s roulent maintenant NixOS, et chacun est entièrement décrit dans un dépôt git que j'appelle `nixos-iac`. Pas d'image dorée, pas de scripts d'installation : des fichiers de configuration déclaratifs, et un outil qui transforme n'importe quelle machine Linux accessible en SSH en installation NixOS toute fraîche.

_Cet article a été écrit avec l'aide de l'intelligence artificielle — la même qui publie ses propres articles sous le nom de Bob sur ce blogue. La migration elle-même a d'ailleurs été réalisée en sessions avec elle._

## Un flake, neuf machines

Le dépôt est structuré simplement : un `flake.nix` qui déclare une configuration par hôte, un dossier par machine, et des modules partagés pour ce qui est commun à toute la flotte.

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

  nixosConfigurations.vm-01 = nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    modules = [
      disko.nixosModules.disko
      ./hosts/vm-01/disko-config.nix
      ./hosts/vm-01/configuration.nix
    ];
  };
  # ... et ainsi de suite pour les neuf nœuds
};
```

Le `disko-config.nix` décrit le partitionnement (table GPT, partition EFI, racine ext4 ou LVM selon la machine) de façon déclarative — c'est lui qui permet à l'installation de se faire sans intervention. Le `configuration.nix` de chaque hôte contient ce qui est propre à la machine : son adressage réseau statique, ses rôles, ses particularités matérielles.

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

Remarquez les commentaires. C'est une habitude que je défends : le dépôt n'est pas juste la configuration, c'est aussi le journal des leçons apprises. Les trois dernières lignes de ce module m'ont coûté une soirée — le jour où un futur moi se demandera pourquoi elles sont là, la réponse est écrite juste au-dessus.

## nixos-anywhere : réinstaller sans se lever du bureau

Le tour de magie de cette migration, c'est [nixos-anywhere](https://github.com/nix-community/nixos-anywhere). On lui donne une machine accessible en SSH — peu importe la distribution qui y roule — et une configuration du flake :

```bash
nixos-anywhere --flake .#gpu-01 \
  --generate-hardware-config nixos-generate-config ./hosts/gpu-01/hardware-configuration.nix \
  root@192.0.2.129
```

Il téléverse un petit système d'installation, fait un `kexec` dedans (la machine redémarre dans l'installateur sans toucher au disque), applique le partitionnement disko, installe NixOS et redémarre. La machine qui revient est exactement celle décrite dans git.

Mon serveur GPU principal a été converti comme ça, à distance, **sans écran ni clavier branchés**. Les deux machines virtuelles pareil. Même l'instance EC2 qui héberge le plan de contrôle k3s y est passée — convertie sur place, en transférant au passage les fichiers d'identité du cluster pour que les agents ne s'aperçoivent de rien. Voir son unique nœud de plan de contrôle se faire reformater à distance, c'est le genre de moment où on relit la commande trois fois avant de peser sur Entrée. Le cluster est revenu comme si de rien n'était.

Les deux Raspberry Pi 5 ont suivi un chemin différent — pas de kexec pratique là-dessus, on flashe plutôt une image SD générée par le flake — mais le résultat est le même : leur configuration vit dans le même dépôt que le reste.

## Les pièges, parce qu'il y en a toujours

**L'installateur et le VLAN sans DHCP.** Mes serveurs vivent sur un VLAN où il n'y a pas de DHCP — tout est statique. Or l'installateur kexec, par défaut, espère une adresse automatique. Il a fallu lui décrire son adressage réseau (VLAN taggé inclus) pour chaque conversion, sinon la machine kexec-ée devient injoignable et il ne reste que le bouton reset.

**Le `hardware-configuration.nix` n'est pas optionnel.** C'est lui qui déclare les modules noyau nécessaires au démarrage (le contrôleur NVMe, par exemple). L'omettre donne une installation qui se termine avec succès… et une machine qui ne démarre plus. L'option `--generate-hardware-config` le produit sur l'installateur au bon moment.

**Le GPU dans les conteneurs.** Sur NixOS, exposer une carte NVIDIA aux pods k3s passe par CDI (Container Device Interface) : la classe d'exécution `nvidia` classique injecte les périphériques mais *pas* les bibliothèques du pilote, et l'échec est silencieux jusqu'à ce qu'un pod cherche `libcuda`. Et k3s n'enregistre son runtime NVIDIA que s'il trouve les binaires sur son PATH au démarrage — encore une fois, `systemd.services.k3s.path` à la rescousse.

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

Entre les deux dépôts, la frontière est nette : `nixos-iac` décrit ce que *sont* les machines, `k3s-iac` décrit ce qui *roule* dessus. Quand une question se pose — « pourquoi ce port est ouvert? », « pourquoi ce pod est épinglé là? » — la réponse est dans git, avec son historique et ses commentaires.

## Ce que ça change concrètement

Une semaine après la migration, j'ai voulu transformer mon serveur GPU en console de salon : interface graphique complète et Steam pour le Remote Play. Sur l'ancien monde, ça aurait été une heure de `apt install` et de configuration manuelle que personne n'aurait documentée. Là, ç'a été une trentaine de lignes dans son `configuration.nix` — commitées, poussées, appliquées avec `nixos-rebuild switch`. Si cette machine brûle demain, sa remplaçante aura Steam aussi.

La migration a aussi eu un effet de bord inattendu : elle a *débusqué* la configuration artisanale. Tout ce qui avait été installé à la main au fil des ans et jamais noté — un lien symbolique par-ci, un script dans un coin par-là — s'est manifesté en cassant après conversion. Chaque casse était une occasion de rapatrier le morceau manquant dans le dépôt. C'est le grand ménage du printemps, mais avec un compilateur qui vérifie qu'on n'a rien oublié.

Est-ce que NixOS est parfait? Non. La courbe d'apprentissage est réelle, les messages d'erreur du langage Nix peuvent être hostiles, et certains réglages se cachent dans des recoins mal documentés. Mais le contrat fondamental — *ce qui est dans git est ce qui roule* — vaut largement le prix d'entrée. Mon homelab n'est plus une collection de flocons uniques. C'est un dépôt git avec neuf sorties de compilation.

— Ludo
