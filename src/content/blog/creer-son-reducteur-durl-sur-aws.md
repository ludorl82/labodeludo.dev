---
title: "Créer son réducteur d'URL sur AWS"
pubDate: 2019-08-27
description: "Dans cette publication, je vais vous montrer comment on peut créer simplement un réducteur d'URL hébergé dans S3. Pour ce faire, nous aurons besoin d'un petit nom de domaine et d'un compte AWS."
tags: ["Cloud", "ludo"]
heroImage: "/images/blog/2019/08/reducteur-d-url-sans-serveur-compresse.jpg"
---
Dans cette publication, je vais vous montrer comment on peut créer simplement un réducteur d'URL hébergé dans **S3**. Pour ce faire, nous aurons besoin d'un petit nom de domaine et d'un compte **AWS**.

\*\*\* MAJ 2019-10-24 Si vous souhaitez simplement déployer le réducteur d'URL vous pouvez sauter au [prochain article](https://labodeludo.dev/cloud/automatiser-le-deploiement-de-son-reducteur-durl-avec-terraform/#deploiement).

### Plan de match

-   Enregistrer le domaine court et le configurer dans **Route 53**
-   Créer le compartiment **S3** et le configurer en site web statique
-   Placer et configurer le **CloudFront** devant le compartiment
-   Créer nos URLs courtes dans **S3**

\*\*\* MAJ 2019-10-23: L'origine Cloudfront a été modifiée pour pointer sur l'URL de site web statique du compartiment S3 et non sur son URL d'API REST. Nous avons maintenant bien une redirection 301 en analysant les entêtes tel qu'en fait foie la dernière saisie d'écran.

## Un peu de contexte

Les réducteurs d'URL sont très populaires dans le domaine du marketing et du web parce qu'ils permettent de communiquer des adresses faciles à se souvenir pointant sur des ressources précises sur le NET. Par exemple, les réseaux sociaux ont tous leur propre réducteur d'URL, _lnkd.in_, _t.co_, _g.co_ et _fb.me_ pour ne nommer qu'eux. Lorsqu'on «post» un lien vers une page externe sur le web, une petite URL est créée automatiquement et elle pointe vers la page en question.

Vous pouvez aussi recourir aux [bitly](https://bitly.com) de ce monde pour réduire vos URLs, mais sans rentrer trop dans les détails des différentes facettes de chacun des services, vous devrez sacrifier certaines libertés et certaines possibilités si vous ne payez pas des sommes importantes.

Des fois avec un peu de savoir-faire on peut faire plus. Faire son propre réducteur d'URL c'est un beau projet qui nous permet de survoler les technologies sans serveur du cloud. Si vous suivez ce document jusqu'à la fin, vous aurez construit un petit réducteur d'URL très performant, hautement disponible et demandant peu de maintenance.

## Architecture et coûts

Maintenant nous allons créer notre redirecteur d'URL à l'aide d'objets **S3** attribués de la métadonnée _Website Redirect Location_. Devant **S3** nous placerons une distribution **CloudFront** pour maximiser les performances et pour ajouter un certificat SSL à notre outil. Une fois le labo complété, nous aurons donc un redirecteur d'URL sur un point de distribution **CloudFront** avec HTTPS.

[![](/images/blog/2019/08/23094958/Réducteur-dURL-1ere-partie-2-1024x450.jpeg)](/images/blog/2019/08/26193935/Réducteur-dURL-1ere-partie-1.jpeg)

Diagramme créé avec Lucidchart

Une des beautés des architectures sans serveur est que le coût est basé strictement à l'utilisation. Donc dans notre cas (Canada Central):  
\- S3: stockage négligeable, coût pour 1 million de GET 0,60$ / mois  
\- Amazon CloudFront: bande passante négligeable, coût pour 1 million de GET: 1$ / mois

Quant à l'enregistrement du nom de domaine, ça peut aller de quelques dollars pas année à plusieurs centaines. Les _.io_ sont à 39$ / année sur AWS. Vous pouvez aussi choisir d'utiliser un sous-domaine d'un domaine que vous possédez déjà si vous voulez simplement expérimenter.

## Déployer le réducteur d'URL

### Enregistrer son domaine court

En premier, vous allez devoir vous trouver un nom de domaine pas trop long qui répond au besoin. Avec toutes les TLD qui sont maintenant disponibles, ce n'est pas trop difficile de trouver un nom de domaine court. En moyenne, les noms de domaines sont d'environ [13 caractères](http://datagenetics.com/blog/march22012/) avec l'extension _.com_ ; moins que ça, c'est bien. Si vous voulez un coup de pouce pour trouver le bon nom de domaine, vous pouvez faire vos recherches notamment dans [Domainr](https://domainr.com) qui parcourt toutes les extensions TLD du NET.

Une fois que vous aurez trouvé votre nom de domaine court, vous pouvez l'enregistrer auprès de votre registraire de choix. Ces [instructions](https://docs.aws.amazon.com/fr_fr/Route53/latest/DeveloperGuide/registrar.html) vous montreront comment enregistrer le domaine avec Amazon. Si vous utilisez un autre registraire que Amazon, vous devrez créer une zone hébergée dans Route 53 et la désigner comme serveur DNS pour votre domaine. Voir ces [instructions](https://docs.aws.amazon.com/fr_fr/Route53/latest/DeveloperGuide/migrate-dns-domain-in-use.html).

Maintenant que nous avons enregistré notre nom de domaine et que nous avons désigné Route 53 comme serveur DNS pour ce dernier, nous allons voir les entrées telles que celles-ci. Le nom de domaine que je vais utiliser est _lrl.io_.

[![](/images/blog/2019/08/2019-08-15-15_50_44-Route-53-Management-Console-1024x652.png)](/images/blog/2019/08/2019-08-15-15_50_44-Route-53-Management-Console.png)

Pour être sûr que les changements de DNS auprès de votre registraire se sont bien propagés sur le NET, vous devriez faire une requête DIG sur les serveurs de nom de Google par exemple et vérifier que vos entrées NS correspondent.

[![](/images/blog/2019/08/2019-08-15-15_28_22-Dig-résolution-DNS-1024x649.png)](/images/blog/2019/08/2019-08-15-15_28_22-Dig-résolution-DNS.png)

### Créer son compartiment S3

Vous devez ensuite créer un compartiment S3 qui servira de site web statique en suivant ces [instructions](https://docs.aws.amazon.com/fr_fr/AmazonS3/latest/dev/website-hosting-custom-domain-walkthrough.html). Prenez bien note que le compartiment devra avoir le même nom que votre domaine.

Comme page d'index et comme page d'erreur, nous spécifions un objet que nous appelons _web_. Il fera une redirection sur la page d'accueil de notre domaine. Assurez-vous ensuite que vos fenêtres correspondent à celles-ci.

-   [![](/images/blog/2019/08/2019-08-14-20_32_21-Window-1024x745.png)](/images/blog/2019/08/2019-08-14-20_32_21-Window-1024x745.png)
    
-   [![](/images/blog/2019/08/2019-08-15-15_37_15-S3-Management-Console-1024x577.png)](/images/blog/2019/08/2019-08-15-15_37_15-S3-Management-Console-1024x577.png)
    
-   [![](/images/blog/2019/08/2019-08-15-15_41_11-S3-Management-Console-1024x577.png)](/images/blog/2019/08/2019-08-15-15_41_11-S3-Management-Console-1024x577.png)
    
-   [![](/images/blog/2019/08/2019-08-15-16_48_18-S3-Management-Console-1024x719.png)](/images/blog/2019/08/2019-08-15-16_48_18-S3-Management-Console-1024x719.png)
    
-   [![](/images/blog/2019/08/2019-08-15-16_21_38-S3-Management-Console-1-1024x698.png)](/images/blog/2019/08/2019-08-15-16_21_38-S3-Management-Console-1-1024x698.png)
    
-   [![](/images/blog/2019/08/2019-08-15-16_28_28-Route-53-Management-Console-1-1024x548.png)](/images/blog/2019/08/2019-08-15-16_28_28-Route-53-Management-Console-1-1024x548.png)
    

Maintenant que votre compartiment S3 est configuré en hébergement statique et que Route 53 fait pointer le domaine sur ce dernier, vous pouvez déjà créer des objets dedans et les voir avec votre nom de domaine. Si par exemple vous créez l'objet _web_ dans votre compartiment avec le code suivant à l'intérieur `<html><body>Vous avez bien rejoint votre compartiment S3</body></html>`, vous devriez être en mesure de voir votre page html s'afficher en naviguant à l'adresse: _http://lrl.io/web_. Plus loin dans le post nous allons voir comment ajouter des objets dans S3. Vous pouvez sauter là tout de suite si vous n'avez pas besoin de HTTPS.

### Configurer Cloudfront comme point de terminaison SSL

Pour utiliser le CDN de Amazon comme point de terminaison SSL, nous allons d'abord créer notre certificat dans **AWS Certificate Manager**, dans la région de Virginie du Nord. Pour ce faire, nous allons dans la console de ACM et nous allons demander un certificat public tel que décrit dans la [documentation](https://docs.aws.amazon.com/fr_fr/acm/latest/userguide/gs-acm-request-public.html). Comme nous hébergeons les services DNS du domaine dans Route 53, nous pourrons procéder à la validation par DNS en cliquant simplement sur le bouton `Créer un enregistrement dans Route 53`. Suite à la validation du certificat par entrée DNS ou par email, nous devrions avoir le résultat comme suit.

-   [![](/images/blog/2019/08/27154531/2019-08-27-15_44_52-AWS-Certificate-Manager-1024x659.png)](/images/blog/2019/08/27154531/2019-08-27-15_44_52-AWS-Certificate-Manager-1024x659.png)
    
-   [![](/images/blog/2019/08/27153336/2019-08-26-20_17_34-AWS-Certificate-Manager-1024x555.png)](/images/blog/2019/08/27153336/2019-08-26-20_17_34-AWS-Certificate-Manager-1024x555.png)
    
-   [![](/images/blog/2019/08/27153337/2019-08-26-20_18_38-AWS-Certificate-Manager-1024x555.png)](/images/blog/2019/08/27153337/2019-08-26-20_18_38-AWS-Certificate-Manager-1024x555.png)
    

Maintenant que nous avons créé notre certificat SSL, nous sommes prêts à créer la distribution. Dans **AWS CloudFront**, nous allons faire `Créer Distribution`. Nous choisirons de faire une distribution web avec les paramètres tels qu'illustrés ci-bas.

-   [![](/images/blog/2019/10/23094225/2019-10-23-09_35_44-AWS-CloudFront-Management-Console-1024x598.png)](/images/blog/2019/10/23094225/2019-10-23-09_35_44-AWS-CloudFront-Management-Console-1024x598.png)
    
-   [![](/images/blog/2019/08/27153412/2019-08-27-15_08_52-AWS-CloudFront-Management-Console-1024x630.png)](/images/blog/2019/08/27153412/2019-08-27-15_08_52-AWS-CloudFront-Management-Console-1024x630.png)
    
-   [![](/images/blog/2019/08/27153414/2019-08-27-15_09_04-AWS-CloudFront-Management-Console-1024x630.png)](/images/blog/2019/08/27153414/2019-08-27-15_09_04-AWS-CloudFront-Management-Console-1024x630.png)
    
-   [![](/images/blog/2019/08/27153416/2019-08-27-15_09_36-AWS-CloudFront-Management-Console-1024x630.png)](/images/blog/2019/08/27153416/2019-08-27-15_09_36-AWS-CloudFront-Management-Console-1024x630.png)
    
-   [![](/images/blog/2019/08/27153417/2019-08-27-15_09_52-AWS-CloudFront-Management-Console-1024x630.png)](/images/blog/2019/08/27153417/2019-08-27-15_09_52-AWS-CloudFront-Management-Console-1024x630.png)
    

La distribution CloudFront devrait prendre environ 20 minutes à se déployer, mais si vous faites des changements ça prendra encore une vingtaine de minutes. Soyez patients. Une fois que c'est fini de se créer, nous devrions voir le résultat comme suit.

[![](/images/blog/2019/08/26205809/2019-08-26-20_56_27-AWS-CloudFront-Management-Console-1024x585.png)](/images/blog/2019/08/26205809/2019-08-26-20_56_27-AWS-CloudFront-Management-Console.png)

Finalement, nous devons configurer Route 53 pour pointer sur la distribution **CloudFront**, car elle est maintenant le point de contact pour nos clients du web. Dans votre zone hébergée de Route 53, vous devez mettre à jour l'entrée comme suit. Vous devrez toutefois patienter que la distribution **CloudFront** ait terminé de se déployer. Voici ce que devrait avoir l'air la zone hébergée de Route 53.

[![](/images/blog/2019/08/26205820/2019-08-26-20_57_30-Route-53-Management-Console-1024x585.png)](/images/blog/2019/08/26205820/2019-08-26-20_57_30-Route-53-Management-Console.png)

## Créer ses URLs courtes

Maintenant, nous pouvons commencer à ajouter les objets qui serviront de point de redirection pour nos URLs courtes. Nous commencerons par créer l'objet web qui sert à rediriger les requêtes sur le domaine racine.

Il reste donc seulement à créer les objets qui vont nous servir d'URL courtes. Pour commencer, on va créer un objet qu'on va appeler _web_. L'objet ne doit pas avoir d'extension et il peut être complètement vide. Une fois que le fichier est créé, on le charge dans le compartiment.

[![](/images/blog/2019/08/2019-08-15-17_18_18-S3-Management-Console-1024x650.png)](/images/blog/2019/08/2019-08-15-17_18_18-S3-Management-Console.png)

Ensuite, dans les propriétés de l'objet, nous allons créer une redirection vers notre long nom de domaine.

[![](/images/blog/2019/08/2019-08-15-17_22_45-S3-Management-Console-1024x580.png)](/images/blog/2019/08/2019-08-15-17_22_45-S3-Management-Console.png)

Nous pouvons confirmer que le domaine court est bien redirigé vers notre longue URL en naviguant sur l'URL courte ou bien en analysant les entêtes de la réponse HTTP telle que ci-dessous avec [webconfs](https://www.webconfs.com/http-header-check.php).

[![](/images/blog/2019/08/23094344/2019-10-23-09_38_55-HTTP-_-HTTPS-Header-Check-1024x565.png)](/images/blog/2019/08/27155151/2019-08-27-15_51_15-HTTP-_-HTTPS-Header-Check.png)

Maintenant que nous avons redirigé le domaine court sur sa racine, nous pouvons suivre le même processus pour ajouter autant d'URLs courtes qu'il nous plaît.

## Mot de la fin

Dans cette publication nous avons donc créé un redirecteur d'URL sans serveur qui se met à jour en téléchargeant des objets dans notre compartiment S3. Dans un prochain post, je vous montrerai comment gérer vos URLs courtes avec le AWS Systems Manager et des fonctions Lambda.
