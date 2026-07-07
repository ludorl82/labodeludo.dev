---
title: "Automatiser le déploiement de son réducteur d'URL avec Terraform"
pubDate: 2019-10-24
description: "Dans cette deuxième partie, nous allons automatiser le déploiement de l'infrastructure du réducteur d'URL présenté précédemment, à laquelle nous allons ajouter quelques morceaux. Je vous présenterai l'architecture et…"
tags: ["Cloud", "Labo", "ludo"]
heroImage: "/images/blog/2019/10/og-image-large-e60c82fe1.png"
---
Dans cette deuxième partie, nous allons automatiser le déploiement de l'infrastructure du réducteur d'URL présenté précédemment, à laquelle nous allons ajouter quelques morceaux. Je vous présenterai l'architecture et les coûts totaux et je vous guiderai dans son déploiement avec **Terraform**. Suite à ce laboratoire vous aurez un réducteur d'URL que vous pourrez gérer facilement avec la console de AWS.

## Architecture et coûts

Comme dans le [labo précédent](https://labodeludo.dev/cloud/creer-son-reducteur-durl-sur-aws/), nous allons créer notre redirecteur d'URL à l'aide d'objets **S3** attribués de la métadonnée _Website Redirect Location_. Nous allons aussi profiter de la facilité de gérer nos paramètres du redirecteur d'URL avec le **AWS Systems Manager (SSM)**. Les fonctions **lambda** viendront appliquer les changements du magasin de paramètres dans les objets de redirection du compartiment S3 avec des évènements de **CloudWatch**. Les fonctions lambda seront déclenchées lorsqu'il y aura un ajout, une mise à jour ou une suppression d'un paramètre dans SSM.

![Digramme d'architecture du réducteur d'URL dans AWS](/images/blog/2019/10/23110658/Réducteur-dURL-géré-avec-SSM-4-1024x588.jpeg)

Diagramme créé avec Lucidchart

Les coûts rattachés à cette architecture sont sensiblement les mêmes que ceux du premier laboratoire. Les paramètres standard sont gratuits comme nous ne faisons pas d'appel d'API. Les évènements Cloudwatch standard sont gratuits aussi. L'utilisation des fonctions lambda rattachée à ce projet rentreront sans doute dans la limite de 1M de requêtes gratuites par mois.

Voici donc la liste des coûts:

-   Route 53: l'enregistrement d'un domaine ~17$ / année pour un _.ca_
-   S3: stockage négligeable, coût pour 1M de GET 0,60$ / mois
-   CloudFront: bande passante négligeable, coût pour 1M de GET: 1$ / mois

Une seule limite importante se présente toutefois. Une limite de 1000 paramètres par compte par région existe. Donc si vous voulez créer plus de 1000 URLs courtes, vous devrez demander une augmentation de limite au support de AWS.

## Avant de commencer

Pour compléter ce laboratoire, nous devons avoir un domaine dont les DNS sont configurés dans **Route 53**. Des explications à ce sujet sont fournies dans le [premier billet](https://labodeludo.dev/cloud/creer-son-reducteur-durl-sur-aws/). Vous devrez aussi installer la console en ligne de commande de AWS. Les instructions pour l'installer sont disponibles [ici](https://docs.aws.amazon.com/en_us/cli/latest/userguide/cli-chap-install.html). Finalement vous devez installer Terraform disponible [ici](https://www.terraform.io/downloads.html).

Pour que Terraform puisse déployer l'infrastructure dans votre compte AWS, vous devez configurer le client tel qu'indiqué [ici](https://docs.aws.amazon.com/fr_fr/cli/latest/userguide/cli-chap-configure.html) avec une clé disposant minimalement des permissions décrites dans le fichier [suivant](https://github.com/ludorl82/aws-lambda-short-url/blob/master/terraform-urls-policy.json).

Vous aurez aussi besoin de l'utilitaire [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### Terraform

Dans ce laboratoire, nous allons déployer notre redirecteur d'URL avec Terraform. Il s'agit là d'un outil d'**orchestration d'infrastructure** qui permet de décrire l'infrastructure désirée sous forme de fichiers texte en faisant abstraction de l'ordre dans lequel les éléments d'infrastructure doivent être déployés. C'est pourquoi on réfère communément à cette pratique comme faire de l'infrastructure en code ("infrastructure as code").

Terraform permet donc de déployer l'infrastructure, mais il permet aussi de détruire de l'infrastructure. En fait, il garde une trace du déploiement qu'il a fait dans des fichiers d'état qui peuvent être directement sur la machine du DevOps ou bien dans un endroit centralisé.

Comme nous avons déjà déployé de l'infrastructure pour le réducteur d'URL dans le premier laboratoire, nous commencerons donc par importer ce que nous avons fait dans le plan Terraform. Une fois que ça sera fait, nous pourrons déployer les morceaux manquants en appliquant le plan.

### Importation de l'infrastructure existante

Si vous avez commencé par faire le premier laboratoire nous commencerons par importer ce que vous venez de faire dans le plan Terraform. Sinon, je vous invite à passer tout de suite à l'étape de déploiement.

Dans le laboratoire d'avant, nous avons créé une zone hébergée dans Route 53, un compartiment de site web statique dans S3 et une distribution CloudFront. La documentation de Terraform est très bien faite, alors je vous la fournit pour ces 3 ressources:  
[www.terraform.io/docs/providers/aws/r/s3\_bucket.html#import](https://www.terraform.io/docs/providers/aws/r/s3_bucket.html#import)  
[www.terraform.io/docs/providers/aws/r/cloudfront\_distribution.html#import](https://www.terraform.io/docs/providers/aws/r/cloudfront_distribution.html#import)  
[www.terraform.io/docs/providers/aws/r/route53\_zone.html#import](https://www.terraform.io/docs/providers/aws/r/route53_zone.html#import)

Dans mon cas, voici les trois commandes que je vais devoir lancer:

```
terraform import aws_s3_bucket.short_urls_bucket lrl.io
terraform import aws_cloudfront_distribution.short_urls_cloudfront EOYGSDES71UW4
terraform import aws_route53_zone.short_url_domain Z1D633PJN98FT9
```

Pour appliquer ces commandes à votre cas, vous devrez substituer mon domaine court avec le vôtre. Ensuite il vous faudra trouver l'identifiant de votre distribution CloudFront et celui de votre zone hébergée de Route 53. Les commandes suivantes vous retournerons ces valeurs.

```
aws cloudfront list-distributions | grep Id
aws route53 list-hosted-zones-by-name --dns-name lrl.io
```

Il faut toutefois avoir initialisé le plan avant de pouvoir importer quoique ce soit. Je vous invite donc pour l'instant à simplement recueillir votre identifiant de distribution CloudFront et celui de votre zone hébergée de Route 53.

## Déploiement

### Cloner le dépôt de code

Nous commencerons d'abord par télécharger le code dans lequel se trouve définie l'infrastructure de notre projet.

```
git clone https://github.com/ludorl82/aws-lambda-short-url.git
```

### Initialiser le plan

Ensuite, nous continuerons en initialisant le plan Terraform.

```
cd aws-lambda-short-url
terraform init
```

Pour des fins de simplicité, nous créons ici le plan sur notre propre station de travail, mais il est bon de savoir qu'il est recommandé de sauvegarder le plan dans un espace de stockage sur le nuage tel que dans un [compartiment S3](https://www.terraform.io/docs/backends/types/s3.html). Ceci évite de devoir tout détruire manuellement si nous perdons les fichiers d'état de Terraform et que nous voulons apporter des modifications à l'infra.

Une fois le plan initialisé nous devrions avoir reçu un message de succès comme celui-ci.

```
Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

### Valider le code (au besoin)

Il est possible que le code Terraform doive être mis à jour avec les nouvelles versions du logiciel. Dans le cas qui nous concerne, j'ai utilisé la version suivante de Terraform.

```
$ terraform -version
Terraform v0.12.12
+ provider.archive v1.3.0
+ provider.aws v2.33.0
```

Si vous utilisez une version plus récente et que vous avez des erreurs, vous pouvez soit réparer le code avec la commande `terraform validate` ou bien télécharger la même version que moi de Terraform de leur section d'[archives](https://releases.hashicorp.com/terraform/).

Une fois que vous avez initialisé le projet avec succès, vous pouvez maintenant déployer l'infrastructure. Si vous avez déjà créé votre réducteur d'URL manuellement selon l'architecture décrite dans le billet précédent, alors je vous invite à lire la section sur l'importation de l'infrastructure existante dans le plan et de lancer vos commandes d'importation maintenant.

### Définir les variables (optionnel)

Pour éviter d'être questionné sur les valeurs que vous souhaitez donner à vos variables chaque fois que vous lancez le plan, vous pouvez définir ces dernières dans un fichier de variables comme ci-bas.

```
echo 'region = "ca-central-1"' > short_urls.tfvars
echo 'short_url_domain = "lrl.io"' >> short_urls.tfvars
echo 'base_domain_url = "https://www.ludoviclamarre.ca"' >> short_urls.tfvars
echo 'default_url = "https://www.ludoviclamarre.ca"' >> short_urls.tfvars
```

Si vous avez importé des ressources dans le plan, assurez-vous de choisir la même région dans laquelle se trouvent ces ressources.

### Déployer l'infrastructure

Vous êtes maintenant prêt à déployer votre redirecteur d'URL. Pour ce faire, toujours à partir du répertoire du projet avec vos fichiers Terraform lancez la commande suivante:

```
terraform apply -var-file="short_urls.tfvars"
```

Si vous n'avez pas créé de fichier de variable alors on vous demandera les valeurs suivantes:

-   Le domaine court que vous souhaitez utiliser (ex. exemple.com)
-   L'URL sur laquelle vous souhaitez rediriger la racine du domaine (ex. https://www.monsiteweb.com)
-   L'URL sur laquelle renvoyer en cas d'erreur d'adresse (ex. https://erreur.url.com/pasdurlici)
-   La région dans laquelle déployer (ex. ca-central-1)

On vous présentera alors l'ensemble des choses qui seront déployées. Vous pouvez alors faire `yes`.Vous devrez alors attendre plusieurs minutes le temps du déploiement. Finalement, on vous retournera un message de succès.

```
Outputs:

BaseDomainURL = https://www.monsiteweb.com
DefaultURL = https://erreur.url.com/pasdurlici
ParameterPrefix = exemplecom
Region = ca-central-1
ShortURLDomain = exemple.com
```

## Gérer son réducteur d'URL

Pour cette dernière section, je vous invite à lire le `[README](https://github.com/ludorl82/aws-lambda-short-url/blob/master/README.md)` du dépot de code. C'est dans ce fichier que je tiens à jour cette information étant donné qu'il s'agit d'un projet qui pourra possiblement évoluer dans le temps.

## Mot de la fin

J'espère que vous avez apprécié de découvrir Terraform avec moi. Je vous invite à m'écrire si vous avez des questions.

@++
