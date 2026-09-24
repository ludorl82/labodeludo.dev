---
title: "Politique de confidentialité"
---

Le labo de Ludo est un blogue personnel. Cette page couvre ce qui touche à la vie privée sur ce site : la lecture du blogue, le robot conversationnel « Parler à Bob », les outils d'intelligence artificielle qui font tourner le labo, et l'intégration LinkedIn utilisée pour publier du contenu.

Dernière mise à jour : 24 septembre 2026.

## Le blogue

Ce site est statique (Astro, hébergé sur S3) et ne fait tourner aucun système de compte, de commentaire ou de tracking publicitaire.

Le site utilise Google Analytics 4 pour mesurer la fréquentation (pages vues, provenance, type d'appareil, pays). Ces données sont agrégées et ne servent qu'à savoir quels articles sont lus. Aucune donnée n'est revendue ni utilisée à des fins publicitaires.

## Le robot « Parler à Bob »

Le site propose un robot conversationnel qui répond aux questions sur le labo à partir des articles publiés ici.

- **Les questions sont traitées par un modèle qui roule sur mon propre matériel**, dans le labo. Elles ne sont envoyées à aucun fournisseur d'intelligence artificielle externe. Le service qui reçoit la question (un Worker Cloudflare) la relaie au labo par un tunnel chiffré et retourne la réponse.
- **Les questions sont comptées, pas conservées telles quelles avec leur auteur.** Le texte de chaque question est gardé pendant 35 jours, avec un compteur, sans adresse IP, sans identifiant de session et sans la réponse. Cette liste sert à choisir les questions suggérées sous la boîte de dialogue. Une question qui ressemble à une adresse (courriel, URL, numéro de téléphone) est refusée à l'entrée et n'est jamais enregistrée.
- **La sélection des questions suggérées est faite au labo, elle aussi.** Elle a été confiée à un modèle hébergé (Alibaba Cloud Model Studio, région de Singapour) du 13 au 15 septembre 2026 : la liste comptée des questions lui était transmise une fois par jour. **Ce n'est plus le cas depuis le 15 septembre 2026** — la sélection est revenue sur mon propre matériel. **Aucune donnée provenant des visiteurs ne sort du labo.**
- **La conversation elle-même n'est pas enregistrée** au-delà de la session en cours dans le navigateur.

## Les outils d'intelligence artificielle du labo

Ce blogue documente un labo maison dont la configuration est décrite en code et entretenue avec des assistants d'intelligence artificielle. Pour que ce soit clair :

- **Des fournisseurs externes voient la configuration du labo, pas les données des visiteurs.** Les tâches automatisées qui relisent la documentation du labo et redessinent les pages [/architecture](/architecture/) et [/inventaire](/inventaire/) tournent sur des modèles hébergés : ceux d'Anthropic (Claude), et, depuis septembre 2026, ceux d'Alibaba Cloud Model Studio (région de Singapour). Ce qui leur est transmis, ce sont mes propres dépôts de configuration et mes notes techniques. Aucune donnée provenant des visiteurs du site n'y transite.
- **Les questions posées au robot sont traitées au labo, du début à la fin.** Ni les conversations, ni la liste comptée des questions ne sont transmises à un fournisseur externe. Ça a été le cas pour la liste comptée pendant deux jours en septembre 2026 ; c'est écrit plus haut.
- **Chaque article dit en tête comment il a été écrit.** Ceux signés « Bob » sont rédigés par un assistant d'intelligence artificielle. Les miens, depuis 2026, sont rédigés avec l'aide de l'intelligence artificielle (surtout Claude Code), puis relus et validés par moi. Ceux de 2019 à 2022 ont été écrits sans. Les pages générées qui le disent le sont réellement.
- **Je relis scrupuleusement les articles que je signe, mais pas nécessairement ceux de Bob.** Les textes de Bob sont à prendre avec un grain de sel. C'est pourquoi il doit appuyer ses affirmations sur des références officielles autant que possible : les RFC, la documentation des éditeurs et des projets, les pages de manuel, avec un lien directement dans le texte. Ce qu'aucune source officielle ne confirme, il le présente comme une simple observation.

## Intégration LinkedIn

L'application LinkedIn associée à ce site sert uniquement à publier, sous mon propre nom, du contenu que j'ai moi-même rédigé (des billets de ce blogue, entre autres). Elle n'est utilisée que par moi, à titre personnel — ce n'est pas une application destinée à d'autres utilisateurs.

Concrètement :

- L'application détient un jeton d'accès OAuth qui lui permet de publier en mon nom sur mon propre profil LinkedIn.
- Aucune donnée appartenant à d'autres utilisateurs LinkedIn n'est collectée, stockée ou partagée.
- Le jeton n'est utilisé par aucun tiers et n'est jamais revendu ou partagé.

## Contact

Des questions sur cette page ou sur le site : [github.com/ludorl82](https://github.com/ludorl82).
