---
title: "Déployer sa table à dessiner"
pubDate: 2019-09-20
description: "[![](/images/blog/2019/09/16184601/2019-09-16-184507-tmuxinator-ide-1024x580.png)](/images/blog/2019/09/16184601/2019-09-16-184507-tmuxinator-ide.png)"
tags: ["Cloud", "Labo", "ludo"]
heroImage: "/images/blog/2019/09/2019-09-16-18_45_07-tmuxinator-ide.png"
---
[![](/images/blog/2019/09/16184601/2019-09-16-18_45_07-tmuxinator-ide-1024x580.png)](/images/blog/2019/09/16184601/2019-09-16-18_45_07-tmuxinator-ide.png)

Dans cette publication, je vous partagerai ce que j'en suis venu à préconiser comme environnement de travail comme DevOps. Ces dernières semaines, je me suis fait un malin plaisir à lire plusieurs livres sur les logiciels que nous utilisons à mon travail, mais un de ceux qui m'a procuré le plus de plaisir est un livre sur l'éditeur de texte Vim intitulé _Practical Vim: Edit Text at the Speed of Thought_. Dans la même collection, j'ai aussi dévoré un autre petit livre, _tmux 2: Productive Mouse-Free Development_. C'est surtout avec ces deux ouvrages que j'ai défini mon environnement de travail.

## Développer avec Vi IMproved

**Vim** est un éditeur de texte à la fois très connu et méconnu. Ça faisait plusieurs années que je l'utilisais dans le cadre de mes fonctions d'architecte de systèmes lorsque je devais éditer des configurations dans la console, mais ce n'est que dans ces derniers mois que j'en ai vraiment compris l'essence et le plein potentiel. Vim permet d'éditer des fichiers de texte sans environnement graphique comme tous les éditeurs de texte en console, mais Vim est en réalité plus que cela. C'est un véritable outil de production de code.

Le premier mystère de Vim, contrairement à d'autres éditeurs de texte en console est le mode _normal_ qui ne permet pas l'édition de texte. Ce que l'auteur Drew Neil nous explique c'est que Vim traite les fichiers de code que nous créons comme des peintures. Plutôt que de rentrer directement dans l'ajout de texte, qui est peut-être la fonction principale de quelqu'un qui écrit de longs textes, Vim dans le mode normal offre à son utilisateur une interface axée sur les actions répétitives.

Le mode normal permet en fait d'effectuer des opérations que l'on combine à des mouvements. Par exemple, on fait du copier/couper coller, avec les nombreux registres à cet effet, on crée et on utilise des macros que l'on utilise sur différents fichiers. Lorsqu'on combine une opération avec un mouvement, on peut alors répéter facilement l'action avec une touche réservée à cet effet. Si vous connaissez déjà tous les raccourcis clavier de votre système actuel, peut-être que Vim est le défi que vous cherchez pour amener votre productivité au prochain niveau.

Une des forces de Vim est la fondation de toutes les touches permettant à l'utiliser avec le clavier. On dit que Vim est un outil conçu pour ceux qui sont familiers avec la dactylographie. Bien que toutes les touches de Vim sont configurables, par défaut le logiciel est fait pour augmenter la productivité de ceux qui sont habitués à taper sans regarder le clavier suivant la technique de dactylographie enseignée sur les applications telles que Tap'Touche. Vim et tmux peuvent être utilisés avec l'aide de la souris, mais par défaut cette dernière est désactivée.

## Gérer ses fenêtres avec tmux 2

Bien que Vim permette de gérer lui-même plusieurs onglets et plusieurs panneaux dans une même session d'édition, nous avons parfois besoin de retourner dans la console pour lancer nos travaux d'automatisation ou bien nous voulons temporairement suspendre le travail dans notre outil pour ouvrir un autre projet. **tmux 2** permet de faire cela et bien plus. tmux qui veut dire _terminal multiplexer_ est une solution regorgeant d'avantages pour le travail dans la console. Lorsqu'exécuté sur un environnement de serveur, il permet de faire tourner ses travaux de build et d'automatisation en arrière-plan alors que le client de console SSH peut être déconnecté du serveur. Donc, si on lance une lourde tâche et que la connexion SSH est interrompue, on peut revenir s'attacher sur notre session qui roule encore en arrière-plan. Par exemple, quand on a un laptop et qu'on veut le fermer pour se déplacer, mais qu'on a une job qui roule, c'est très pratique.

Une autre facette intéressante de tmux, qui est liée directement au but de cet article, est la capacité de configurer la disposition de notre environnement de travail ainsi que les applications qui vont être démarrées au lancement de l'environnement. Bien que tout cela se fasse avec tmux nativement, il existe un script qui permette de profiter de tmux simplement sans avoir à gérer trop de configurations. Il s'agit là de **tmuxinator**. Ce script rend possible la gestion de ses environnements de travail de manière déclarative dans des fichiers YAML.

Une fois dans une session tmux, il est essentiel de connaître les raccourcis clavier du logiciel. Un simple aide-mémoire pour trouver les raccourcis peut suffire, mais je vous invite à lire l'ouvrage de Brian P. Hogan _tmux 2: Productive Mouse-Free Development_ dans lequel il explique les commandes essentielles. Le livre est très succinct et va droit au but. Il décrit tmux 2 et il parle aussi de tmuxinator.

## Installer les outils

Tout d'abord, pour installer les outils sur Ubuntu 18.04 nous commencerons comme toujours par mettre à jour le système.

```
sudo apt update
sudo apt upgrade
```

Vim est normalement installé de base sur Ubuntu, mais vous pouvez utiliser cette commande pour vous en assurer.

```
sudo apt install vim
```

Ensuite pour installer tmux et tmuxinator, il vous faudra installer le gestionnaire de scripts gem qui vous permettra d'installer ce dernier. Des instructions complètes sur l'installation sont disponibles ici:  
https://github.com/tmuxinator/tmuxinator#installation

Quand au binaire de tmux, il est disponible dans le gestionnaire de paquets de base de Ubuntu.

```
sudo apt install tmux
sudo apt install ruby-full
gem install tmuxinator
export EDITOR='vim'
source ~/.bin/tmuxinator.zsh
```

En plus de profiter des outils précédemment décrits, j'utilise depuis longtemps la console **ZSH** notamment pour la facilité qu'elle offre pour parcourir les différentes commandes que nous sommes appelées à utiliser au jour le jour. Par dessus ZSH, j'ai aussi ajouté une configuration déjà codée par Robby Russell: **Oh My ZSH**.

```
sudo apt install git-core zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```

Oh My ZSH offre plusieurs thèmes que je vous invite à explorer sur la page de son développeur.  
[https://github.com/robbyrussell/oh-my-zsh/wiki/Themes](https://github.com/robbyrussell/oh-my-zsh/wiki/Themes)

### Vim et tmux à la Ludo

Si vous êtes un DevOps, vous aurez sans doute le réflexe louable de mettre ces outils à votre main. Je vous encourage à le faire en consultant les nombreuses ressources du web, mais à titre d'exemple je vous partage ma configuration personnelle très sommaire avec les instructions qui m'intéressent le plus.

```
cd ~
wget https://labodeludo.dev/wp-content/uploads/2019/09/20110651/zshrc.tar
wget https://labodeludo.dev/wp-content/uploads/2019/09/20110208/tmux.tar
wget https://labodeludo.dev/wp-content/uploads/2019/09/20111717/vim.tar
for f in {zshrc.tar,tmux.tar,vim.tar}; do tar zxvf $f; done
ln -s .vim/vimrc .vimrc
rm -f {zshrc.tar,tmux.tar,vim.tar}
```

Maintenant que vous avez changé la console et que vous avez inclus toutes vos configurations, vous pouvez simplement sortir de votre session avec `Ctrl-d` et ouvrir de nouveau le terminal. Vous aurez alors une console semblable à la suivante. Il vous restera probablement à changer les polices de votre terminal. Personnellement, j'utilise **wsl-terminal** à la maison sous Windows 10 et **iterm2** au travail sur Mac OS. Voici une référence qui m'a été utile pour avoir des polices plus agréables à lire sur Windows avec WSL et Ubuntu.  
[https://medium.com/@Andreas\_cmj/how-to-setup-a-nice-looking-terminal-with-wsl-in-windows-10-creators-update-2b468ed7c326](https://medium.com/@Andreas_cmj/how-to-setup-a-nice-looking-terminal-with-wsl-in-windows-10-creators-update-2b468ed7c326)

![](/images/blog/2019/09/20115141/2019-09-20-11_50_38-ludorl82@DESKTOP-6M4PVL6_-.png)

Console à l'ouverture

Une fois rentré dans la console de base, on peut lancer son environnement de choix avec tmuxinator avec la commande `mux ide`. Pour faciliter l'utilisation de tmux et Vim, je vous recommande aussi de réassigner votre touche de verrouillage de majuscule avec `Ctrl`. J'ai utilisé ce guide pour le faire.  
[https://vim.fandom.com/wiki/Map\_caps\_lock\_to\_escape\_in\_Windows](https://vim.fandom.com/wiki/Map_caps_lock_to_escape_in_Windows)

![](/images/blog/2019/09/20120658/2019-09-20-12_06_05-tmuxinator-ide.png)

Console tmux avec deux fenêtres

Pour basculer d'une fenêtre à l'autre vous pouvez faire `Ctrl-a` `2` et `Ctrl-a` `1`.

Dans ma configuration j'ai activé le mode Vim pour parcourir l'historique de la sortie de la console dans tmux en mode copie. Je trouve que ça permet de profiter plus pleinement de l'apprentissage de Vim. J'ai aussi constaté que les différents raccourcis dans Vim pour parcourir le texte sont utilisés dans **less**. Avec cet apprentissage vous pouvez donc avancer avec la conviction que vous apprenez une méthode de travail qui est au cœur des systèmes avec lesquels vous serez appelé à travailler.

### Un petit Cloud9 en passant

Finalement, si comme moi vous aimez parfois pouvoir utiliser du graphique, je vous conseille d'utiliser l'IDE de cloud de AWS. Il s'installe facilement sur un serveur Linux avec la configuration que je vous ai partagée et, en plus, vous aurez un outil graphique pour le copier coller par exemple ou si vous n'avez accès qu'à un fureteur web.

[![](/images/blog/2019/09/20124213/2019-09-20-12_40_57-telepitpit-AWS-Cloud9-1024x576.png)](/images/blog/2019/09/20124213/2019-09-20-12_40_57-telepitpit-AWS-Cloud9.png)

## Rien ne vaut la pratique

Je vous encourage encore à vous renseigner sur l'utilisation des différents outils que je vous ai présentés. Dans ma configuration de tmux j'ai modifié la touche de commande avec `Ctrl-a`. Mis à part ce changement vous pourrez utiliser toutes les références du web sur le sujet. Et à vrai dire, il semble que cette modification soit plus commune que le `Ctrl-b` affecté par défaut.

Et pour ce qui est de Vim, c'est un sujet très vaste qui pourrait être traité beaucoup plus longtemps, mais dans la réalité c'est en l'utilisant et en pratiquant les différents raccourcis et commandes que vous viendrez à l'adopter.
