---
title: "Site web: statique ou dynamique?"
pubDate: 2022-04-23
description: ""
tags: ["Cloud", "Labo", "ludo"]
heroImage: "/images/blog/banner-1544x500-1.jpg"
---
![](/images/blog/banner-1544x500-1-1024x332.jpg)

Il y a plusieurs options pour créer son site web. Plusieurs services offrent de l'hébergement avec leur outil de conception propriétaire. Je pense entre autres à Squarespace ou Wix. Pour ma part j'ai choisi le logiciel WordPress depuis longtemps. Ça me permet d'héberger moi-même mon site mais avec un beau thème de mon choix. [CNET](https://www.cnet.com/tech/services-and-software/best-website-builder/) fait une liste plus exhaustive des plateformes les plus populaires selon les types de sites web.

## Problématique

Un premier défi que j'ai rencontré en hébergeant mes sites WordPress était le fait que mes sites finissaient par tomber. J'avais rencontré ce genre de problèmes dans le passé en hébergeant mon propre serveur Asterisk. Des bots sur internet sont programmés pour attaquer systématiquement les services disponibles publiquement tels que des sites WordPress. Le problème était un peu gênant. Je redémarrerais Apache et MySQL pour ensuite constater quelques semaines plus tard que le site était encore tombé.

En plus je serais routinièrement contraint de nettoyer des pourriels dans les commentaires et de supprimer les comptes d'utilisateurs qui en fait n'étaient que des bots publicitaires.

## Solutions

Une première solution qui m'a dépannée était de placer le serveur derrière un wouff, euh non je veux dire un **WAF** :p. Haha je sais, je suis très drôle :). Personnellement j'ai utilisé le [WAF de AWS](https://aws.amazon.com/fr/waf/). L'attrait qu'avait pour moi cette solution est qu'elle est facilement jumelable au [CDN de AWS](https://aws.amazon.com/fr/cloudfront/) qui me permettait d'avoir des performances intéressantes pour un tarif basé sur l'utilisation. Par contre j'ai appris plus tard que [CloudFlare](https://www.cloudflare.com/it-it/integrations/wordpress/) offre ce service aussi gratuitement avec leur offre de CDN qui est aussi très bien semble-t-il.

### Statique :O

Un collègue m'a mentionné dernièrement qu'il voulait construire son site statique avec [GoHugo](https://gohugo.io/). J'avoue que l'idée d'utiliser un site statique me semblait un peu ordinaire et limitée. Notamment toutes les fonctions de traitement du coté serveur sont inopérantes. Donc plus de formulaire de commentaires et plus de formulaire de recherche dans le blogue. Et plus de publication facile de nouveaux articles ou de mises à jour spontanée.

D'un autre coté mon site web et mon blogue ne sont pas mis a jour si souvent de toute façon et les commentaires se trouvent plus souvent qu'autrement dans les réseaux sociaux. Un point que j'ai trouvé intéressant était l'idée que l'usage d'un site statique généré a partir de Wordpress permet de dédier son serveur local de Wordpress comme d'un environnement de test. Jusqu'à maintenant je desservais tous mes sites à partir de la même machine sur laquelle je développais.

## Réalisation

J'ai donc fait un peu de recherche et j'ai trouvé cette extension de WordPress: [Simply Static](https://en-ca.wordpress.org/plugins/simply-static/). Comme j'utilisais déjà **Cloudfront** je savais que l'hébergement de mon site statique avec **S3** serait relativement simple. J'ai donc suivi un [tutoriel](https://brianshim.com/webtricks/wordpress-static-site-generator/). Ce dernier spécifiait quelques configurations élémentaires a faire:

[![](/images/blog/2022-04-15-21_16_22-Parametres-Simply-Static-‹-Le-labo-de-Ludo-—-WordPress-Personnel-–-Microsoft​-.png)](/images/blog/2022-04-15-21_16_22-Parametres-Simply-Static-‹-Le-labo-de-Ludo-—-WordPress-Personnel-–-Microsoft​-.png)

Pour ce qui est de l'hébergement du site je savais déjà que je voulais l'héberger sur S3 comme la tarification est intéressante et que j'exploite déjà plusieurs services chez Amazon. Voici une documentation expliquant comment héberger un site statique sur S3 avec CloudFront:

[Utiliser CloudFront pour diffuser un site Web statique hébergé sur Amazon S3](https://aws.amazon.com/fr/premiumsupport/knowledge-center/cloudfront-serve-static-website/)

Pour terminer cette description de solution, je veux mentionner que même en mode d'hébergement statique, des plugin s'exécutant du coté client peuvent être utilisés pour remplir certaines fonctions laissées de coté. Par exemple un collègue qui héberge aussi son propre [blogue](https://www.rainmaking.cloud/faqs) utilise [Remarkbox](https://www.remarkbox.com/).

## Et après quelques semaines?

Les performances, la sécurité, la disponibilité et le coût d'hébergement du site sur S3 sont excellents. Il y a bien sûr le fardeau de générer et transférer sur S3 la nouvelle version du site chaque fois qu'un article est ajouté ou que le site est modifié mais c'est sans doute automatisable.  Peut-être un sujet pour une autre fois. En tout et pour tout un site statique c'est tout de même un compromis très intéressant pour ceux qui sont prêts à repenser leurs façons de faire!
