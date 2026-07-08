---
title: "Intégration de plugins asynchrones avec Neovim"
pubDate: 2022-06-02
description: "Ça fait un bon bout que j'utilise Vim au travail. Ça me permet d'être très prolifique quand je dois manipuler des configurations ou du code. Pour vrai j'espère plus jamais avoir à changer de mode d'édition de texte,…"
tags: ["DevOps", "ludo"]
heroImage: "/images/blog/Screenshot_20220418-162737_Termux.jpg"
---
Ça fait un bon bout que j'utilise Vim au travail. Ça me permet d'être très prolifique quand je dois manipuler des configurations ou du code. Pour vrai j'espère plus jamais avoir à changer de mode d'édition de texte, comme plusieurs d'ailleurs qui ont adopté la philosophie de Vim. J'ai intégré le mode Vim dans tous mes outils qui demandent de manipuler du texte. Le plugin zsh-vi-mode de oh-my-zsh fait mon bonheur quand je dois éditer des commandes. J'utilise le mode vi dans tmux pour parcourir le buffer de ma console et pour copier du texte.

Par contre j'ai commencé à me questionner à force de côtoyer des devs qui utilisent des IDE graphiques. Je sais plus combien de fois on m'a demandé pourquoi je reste sur ma console alors que les outils graphiques permettent de visualiser le code facilement. J'ai considéré en prendre un avec un plugin qui permettrait de reproduire les raccourcis de clavier de Vim. Mais malheureusement l'essence même des IDE graphiques semble les empêcher de fonctionner dans le paradigme Vim. Les différents modes de Vim (Normal, Visual, Insert, etc.) ne sont pas disponibles autrement qu'en utilisant Vim (et gVim). C'est pour ça que j'ai continué longtemps avec Vim.

## Neovim

L'autre jour je me suis décidé à essayer Neovim. J'en avais entendu parler dans le livre de Drew Neil « Modern Vim: Craft Your Development Environment with Vim 8 and Neovim ». Quand je l'avais lu je voyais pas l'intérêt d'avoir un système plus complexe avec Neovim. Certaines choses des configs semblaient différentes (malgré que plus tard j'ai réalisé que c'était pas grand chose). Honnêtement j'en avais déjà assez à digérer avec le paradigme Vim à ce moment là.

Mais maintenant je fais pas mal plus de développement que j'en faisais à mes débuts comme DevOps. Et pour faire du développement, c'est toujours plus facile de pouvoir compter sur des retours visuels pour savoir quand on fait des fautes de frappe, de syntaxe ou avoir des aides d'autocomplétions.

Bon c'est quoi le rapport vous me demandez peut-être. Ce que j'ai constaté, c'est que Neovim intègre assez facilement certaines features plus ou moins bien supportées sur Vim par l'entremise des plugins. Le rapport c'est que le Vim de Bram Moolenaar est limité par le fait qu'il roule comme un seul processus. C'est super simple mais malheureusement pour remplir certaines fonctions comme de l'auto complétion ou du linting de code c'est pas le best. Donc depuis 2014 la communauté a fait une fourche de son projet et développe Neovim en parallèle de Vim.

En gros, Nvim fonctionne avec tous les plugins de Vim, mais il permet d'utiliser d'autres plugins en plus qui demandent des traitements asynchrones en background. Certains plugins qui fonctionnent dans Vim sont plus performants dans Neovim. Comme de fournir des suggestions d'auto-complétions selon le langage de programmation utilisé ou bien d'offrir des suggestions de correction de syntaxe de code. Un plugin bien reconnu qui brille dans Nvim est [Conquer of Completion](https://github.com/neoclide/coc.nvim).

Si vous voulez l'essayer, voici un vidéo que j'ai utilisé pour l'adopter. Il y a aussi des instructions pour avoir des super belles personnalisations de l'apparence de Neovim. Relativement facile a compléter aussi IMHO:

https://youtu.be/JWReY93Vl6g

### Ma config

Si vous voulez aussi j'ai publié ma propre config fortement inspirée de ce vidéo ici:  
[.shell-configs/init.vim at nvim-article · ludorl82/.shell-configs (github.com)](https://github.com/ludorl82/.shell-configs/blob/nvim-article/configs/.console.config/nvim/init.vim)

Une autre fonction qui est super intéressante c'est la nouvelle organisation des plugins dans Nvim (et Vim 8). Nvim permet de simplement cloner les plugins de Github directement dans un dossier qui est pris en charge par le nouveau gestionnaire de plugins natif. Pour mettre à jour mes plugins je lance un find qui fait exactement ça à partir de la console.

PLUGINS\_DIR="$HOME/.config/nvim/pack/bundle/start"
find $PLUGINS\_DIR -mindepth 1 -maxdepth 1 -type d -exec git --git-dir={}/.git --work-tree={} pull \\;

Pour faire quelque chose plus complet, je l'ai inclus dans un script que je roule de temps en temps:  
[.shell-configs/upgrade\_console.sh at nvim-article · ludorl82/.shell-configs (github.com)](https://github.com/ludorl82/.shell-configs/blob/nvim-article/scripts/upgrade_console.sh#L19)

### Résultat

Au final, le résultat est très intéressant pour un logiciel qui permet de garder les gains de productivité de Vim, mais en incluant toutes les fonctions et plus d'un IDE graphique. Pour donner une idée, voici une saisie de ma console si j'édite un script bash dans mon dépôt de code.

[![](/images/blog/2022-04-20-18_14_01-Greenshot.png)](/images/blog/2022-04-20-18_14_01-Greenshot.png)

Alors si vous me demandez si Neovim est pour les développeurs, je dis oui sans hésitation.
