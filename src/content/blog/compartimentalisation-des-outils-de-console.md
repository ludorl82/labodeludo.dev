---
title: "Compartimentalisation des outils de console"
pubDate: 2026-07-05
description: "Dans les dernières décennies, nous avons observé une compartimentalisation croissante dans la gestion des charges de travail. Alors qu'on hébergeait nos serveurs sur des machines physiques il y a 30 ans, aujourd'hui on…"
tags: ["DevOps", "ludo"]
heroImage: "/images/blog/docker-cover-1-e1655335176221.png"
---
Dans les dernières décennies, nous avons observé une compartimentalisation croissante dans la gestion des charges de travail. Alors qu'on hébergeait nos serveurs sur des machines physiques il y a 30 ans, aujourd'hui on définit des bribes de code dans des environnements sans serveur qui s'exécutent sans égard aux couches sous-jacentes, facturées en Go-secondes d'exécution[1](https://aws.amazon.com/fr/lambda/pricing/).

La boite à outils du bon DevOps contient principalement des outils de console. Les outils graphiques dans notre domaine ne sont bien souvent qu'une version diluée des outils de CLI. En tant que tel, il est très concevable de développer et d'opérer nos logiciels directement à partir de conteneurs. Je vous présenterai ici ma propre implémentation dont le code est disponible dans ces dépôts :  
[ludorl82/console](https://github.com/ludorl82/console) (image de base) | [ludorl82/.shell-scripts/console](https://github.com/ludorl82/.shell-scripts/tree/main/console) (couche de personnalisation) | [ludorl82/.shell-configs](https://github.com/ludorl82/.shell-configs)

_Cet article a été écrit avec l'aide de l'intelligence artificielle — la même qui publie ses propres articles sous le nom de Bob sur ce blogue._

## Motivation et objectif

En isolant les outils que nous utilisons dans des conteneurs, nous procédons à une définition exacte et précise de toutes les configurations et des étapes de construction de notre environnement de travail sous forme de code. Ceci rend notre console et notre environnement de travail très portables.

Comme DevOps nous sommes souvent confrontés à diagnostiquer des problèmes réseaux dans des environnements très hermétiques et dans lesquels nous devons opérer avec rien de plus qu'une console. Ou bien bien souvent les développeurs auront à travailler avec des jeux de données qu'on doit exploiter de l'intérieur de segmentations réseaux à l'intérieur desquelles un environnement graphique n'est pas disponible.

Finalement le rôle de DevOps est très lié à l'automatisation. On est doublement gagnant de baigner sur une base régulière dans un environnement de travail dans lequel on travaille avec des commandes d'interpréteur que l'on pourra aisément transposer dans des pipelines de CICD.

Pour toutes ces raisons, je me suis décidé à bâtir cette console dans des conteneurs.

## Limitations d'une console sous docker

Avant de commencer je vais tout de suite énoncer que cette solution n'est pas pour tout le monde. Travailler dans un conteneur n'a plus rien d'exotique en soi — JupyterLab, GitHub Codespaces et les devcontainers eux-mêmes ont rendu ça courant. La vraie limite ici, c'est que ce setup est auto-géré plutôt que sur une plateforme managée : c'est moi qui maintiens le Dockerfile, les Features et le script de bootstrap, et c'est moi qui dois comprendre Docker assez en profondeur pour déboguer quand ça casse (une collision de GID, un entrypoint mal chaîné, etc.). La courbe d'apprentissage est donc abrupte.

## Design et architecture

Pour mon projet de console sous docker, j'ai d'abord dû choisir comment j'allais grouper les outils dont je me sers sur une base régulière. Il m'apparaissait évident qu'une base commune avec les outils que j'utilise toujours devrait être faite. Par contre d'autres outils me servent seulement qu'à l'occasion et ceux-ci devraient être inclus strictement dans des couches docker au-dessus de celles qui définissent l'image de base. Et c'est là que pour moi l'utilisation des conteneurs trouve beaucoup de son sens. En construisant des images spécialisées de la console par dessus la base, j'évite la duplication de l'espace disque et de la consommation de mémoire des charges de travail.

La vraie motivation derrière cette approche, en pratique, c'est que mes besoins varient beaucoup selon la machine où je travaille. Au bureau, j'ai une longue liste d'outils et de configurations propres à mon employeur à ajouter par-dessus la base ; à la maison, la couche de personnalisation reste beaucoup plus légère. Plutôt que de maintenir deux consoles complètement distinctes qui dupliqueraient tout ce qui est commun aux deux, je n'ai qu'à faire varier la couche du dessus — la base, elle, ne change pas.

Concrètement, cela s'est traduit par deux dépôts distincts. Le dépôt [ludorl82/console](https://github.com/ludorl82/console) définit l'image de base : un Ubuntu 24.04 avec les outils que j'utilise partout (zsh, tmux, Neovim, Node.js, un serveur SSH pour m'y connecter) et rien de spécifique à une machine ou à un compte utilisateur. Le dépôt [ludorl82/.shell-scripts/console](https://github.com/ludorl82/.shell-scripts/tree/main/console) définit une couche de personnalisation qui part de `FROM ludorl82/console:latest`, renomme le compte générique `ubuntu` pour mon propre compte (UID/GID, shell, répertoire personnel) et ajoute les outils que je n'utilise que sur certaines machines, comme `gh` et `aws`. La même base sert donc autant sur mon serveur bastion que sur mon poste de travail professionnel, chacun n'ajoutant par-dessus que ce qui lui est propre.

Pour faire une solution plus complète, j'ai créé un bootstrap script pour pouvoir déployer la console sur une machine Ubuntu ou Debian, physique (un Raspberry Pi 5 sous Raspberry Pi OS dans mon cas) ou virtuelle.

## Conteneurisation des configs pour une meilleure portabilité

Le fichier qui définit l'ensemble d'instructions pour bâtir une image Docker est le Dockerfile[2](https://docs.docker.com/engine/reference/builder/). Aussi il existe plusieurs engins pour rouler des conteneurs, dont docker, containerd, lxd, podman, etc. Par contre le Dockerfile est un standard universel pour décrire une image docker. Le projet Docker met de l'avant aussi sa propre solution pour bâtir et déployer plusieurs conteneurs à l'aide de docker compose[3](https://docs.docker.com/compose/). C'est ceci que j'ai utilisé pour bâtir la demo pour cet article.

Le montage de `$HOME` au complet dans le conteneur (plutôt qu'une copie des fichiers de configuration dans l'image) est ce qui permet de garder `.shell-configs` et `.shell-scripts` comme de simples dépôts git sur l'hôte, modifiables sans reconstruire quoi que ce soit :

```
services:
  console:
    build:
      context: .
      dockerfile: Dockerfile
    image: ludorl82/console:latest
    environment:
      - PASS=${PASS:-}
    ports:
      - "2222:22"
    volumes:
      # Le socket est monté sous un nom différent (docker-host.sock) plutôt
      # que d'écraser /var/run/docker.sock directement -- la section
      # suivante explique pourquoi.
      - "/var/run/docker.sock:/var/run/docker-host.sock"
      - "${HOME}:${HOME}"
    restart: always
```

## Devcontainers : la spec derrière les Features

Écrire des Dockerfile à la main pour chaque outil optionnel finit par produire un fichier long, redondant d'une image à l'autre, et qui refait son propre bricolage pour des problèmes déjà résolus ailleurs : installer le CLI Docker proprement, créer un utilisateur non-root avec le bon UID, etc. Pour reconstruire ces deux images, j'ai plutôt adopté la spécification [Development Containers](https://containers.dev/) (« devcontainers »), portée notamment par Microsoft et Docker autour de VS Code mais utilisable indépendamment de tout éditeur via son [CLI officiel](https://github.com/devcontainers/cli) (`@devcontainers/cli` sur npm).

Le fichier `devcontainer.json`[4](https://containers.dev/implementors/json_reference/) décrit comment construire et démarrer un environnement de développement à partir d'un Dockerfile ou d'une image existante. Son apport principal pour ce projet est le concept de Feature[5](https://containers.dev/implementors/features/) : un module autonome, versionné et publié sur un registre OCI (ghcr.io dans mon cas), qui ajoute un outil ou une capacité à une image de façon déclarative plutôt que par un bloc `RUN` maison. Le catalogue officiel [devcontainers/features](https://github.com/devcontainers/features) couvre déjà la plupart des outils courants d'une console DevOps.

Pour l'image de base, deux Features suffisent :

```
{
  "name": "console",
  "build": {
    "dockerfile": "../Dockerfile",
    "context": ".."
  },
  "features": {
    "ghcr.io/devcontainers/features/common-utils:2": {
      "username": "automatic",
      "userUid": "automatic",
      "userGid": "automatic",
      "installZsh": true,
      "installOhMyZsh": false,
      "installOhMyZshConfig": false,
      "upgradePackages": false,
      "configureZshAsDefaultShell": true
    },
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  }
}
```

`common-utils` crée l'utilisateur non-root — ici laissé en `"automatic"` pour ne pas entrer en collision avec le compte `ubuntu` déjà présent dans l'image `ubuntu:24.04`, la personnalisation par compte réel se faisant dans l'autre couche. `docker-outside-of-docker`[6](https://github.com/devcontainers/features/tree/main/src/docker-outside-of-docker) donne accès au démon Docker de l'hôte depuis l'intérieur du conteneur sans faire tourner un second démon imbriqué (docker-in-docker) : elle installe un script `docker-init.sh` qui, au démarrage, aligne le GID du groupe `docker` du conteneur sur celui du socket monté, puis s'efface via `exec "$@"`. C'est exactement le problème que je réglais auparavant à la main en montant directement `/var/run/docker.sock`[7](https://stackoverflow.com/questions/23439126/how-to-mount-a-host-directory-in-a-docker-container)[8](https://medium.com/@andreacolangelo/sibling-docker-container-2e664858f87a) pour lancer des « conteneurs frères » depuis la console, avec le risque de collision de GID entre l'hôte et le conteneur que ça implique — la Feature encapsule maintenant cette solution. C'est ce script que mon `entrypoint.sh` chaîne avant de lancer `sshd` :

```
#!/bin/bash
set -euo pipefail

if [ -n "${PASS:-}" ]; then
    echo "${CONSOLE_USER}:${PASS}" | chpasswd
fi

# docker-init.sh (installé par la Feature docker-outside-of-docker) réconcilie
# le GID du groupe docker du conteneur avec celui du socket monté, avant de
# s'exec dans "$@" lui-même. Présent seulement quand l'image a été construite
# via le CLI devcontainer.
if [ -x /usr/local/share/docker-init.sh ]; then
    exec /usr/local/share/docker-init.sh "$@"
else
    exec "$@"
fi
```

Deux pièges à connaître avec ce modèle. D'abord, les Features s'appliquent toujours _après_ que le Dockerfile ait fini de construire ses propres couches — toute étape qui dépend du résultat d'une Feature (ici, le groupe `docker` créé par `docker-outside-of-docker`) doit donc être un hook de cycle de vie (`postCreateCommand`, etc.) ou, comme je l'ai fait, une étape de l'entrypoint exécutée au démarrage — pas une instruction `RUN` dans le Dockerfile. Ensuite, ces hooks de cycle de vie ne s'exécutent que sous `devcontainer up` ; comme ce service tourne en production via un simple `docker compose up -d`, aucun hook ne se déclencherait de toute façon, d'où le choix de tout régler dans l'entrypoint plutôt que de dépendre d'un mécanisme qui ne s'active qu'en développement.

Autre conséquence pratique : construire l'image avec un simple `docker build` ou `docker compose build` ignore complètement les Features et produit une image sans utilisateur non-root ni CLI Docker. La construction complète passe par le CLI : `npx @devcontainers/cli build --workspace-folder . --image-name ludorl82/console:local`. C'est cette même invocation, via l'action [devcontainers/ci](https://github.com/devcontainers/ci), que la CI GitHub utilise pour publier l'image sur Docker Hub à chaque release.

La couche de personnalisation ajoute deux autres Features officielles, `github-cli`[9](https://github.com/devcontainers/features/tree/main/src/github-cli) et `aws-cli`[10](https://github.com/devcontainers/features/tree/main/src/aws-cli), en plus de son propre bloc de renommage d'utilisateur :

```
{
  "name": "console-personal",
  "build": {
    "dockerfile": "../Dockerfile",
    "context": "..",
    "args": {
      "USER": "${localEnv:USER}",
      "UID": "${localEnv:UID:1000}",
      "GID": "${localEnv:GID:1000}"
    }
  },
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/aws-cli:1": {}
  }
}
```

![Capture d'écran du fichier devcontainer.json de la couche de personnalisation, ouvert dans Neovim sous Windows](/images/blog/console-devcontainer-screenshot-1024x608.png)

Le devcontainer.json de la couche de personnalisation, avec ses Features github-cli et aws-cli

Notez l'usage de `${localEnv:USER}` dans les arguments de build : cette syntaxe du CLI devcontainer va chercher la variable d'environnement du même nom sur la machine hôte au moment de la construction, ce qui évite de coder en dur mon nom d'utilisateur dans le dépôt.

## Bootstrap de machine

Dans un premier temps, ce script [bootstrap\_shell.sh](https://github.com/ludorl82/.shell-scripts/blob/main/bootstrap-shell/bootstrap_shell.sh) clone (ou met à jour) mes deux dépôts de configuration, installe Docker via un script dédié, fixe le fuseau horaire, puis installe les paquets système nécessaires — dont `nodejs` et `npm`, qui n'y étaient pas requis avant et qui servent uniquement à exécuter le CLI devcontainer via `npx` sans avoir à l'installer globalement. Il termine en construisant la couche de personnalisation avec ce même CLI plutôt qu'un simple `docker compose build`, pour que ses Features (`github-cli`, `aws-cli`) soient bien appliquées, puis démarre le conteneur avec `docker compose up -d` (`$COMPOSE_CMD` ci-dessous, choisi un peu plus haut dans le script selon que `docker-compose` ou le plugin `docker compose` est disponible) :

```
# Un simple `docker compose build` ignore les Features devcontainer de cette
# image (github-cli, aws-cli) -- on construit plutôt via le CLI devcontainer,
# qui les applique et re-télécharge la base ludorl82/console:latest à chaque
# fois depuis Docker Hub ; on laisse ensuite compose démarrer l'image déjà
# taguée.
export GID="$(id -g)"
/usr/bin/newgrp docker <<EONG
npx --yes @devcontainers/cli build --workspace-folder . --image-name ludorl82/console-personal:latest
$COMPOSE_CMD up -d
EONG
```

## Émulateurs de terminal sur Windows et macOS

Pour unifier ma façon de travailler entre mes machines Windows et macOS, j’utilise le même émulateur de terminal sur les deux : Alacritty[11](https://alacritty.org/). Une seule configuration, les mêmes raccourcis, peu importe l’OS de la machine que j’ai sous la main pour me connecter à la console.

## En conclusion

Cette console conteneurisée reste un chantier permanent, mais le passage à la spécification devcontainers a réglé le problème qui m’agaçait le plus : maintenir deux Dockerfile qui dérivaient tranquillement l’un de l’autre. Aujourd’hui, la base et la personnalisation évoluent chacune de leur côté sans dupliquer ce qui est commun, et le tout reste aussi portable qu’un simple `docker compose up -d` — sur mon bastion, mon poste de travail, ou un Raspberry Pi 5 fraîchement sorti de sa boîte.
