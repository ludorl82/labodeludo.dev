---
name: voix-ludo
description: "Écrire (ou réécrire) un texte signé Ludo — article du blogue tagué `ludo`, publication LinkedIn, annonce — dans sa voix à lui, pas celle de Bob. À charger avant de rédiger quoi que ce soit que Ludo publiera sous son nom, ou quand il demande « écris ça comme moi ». Ne s'applique PAS aux articles de Bob (tag `bob`), qui ont leur propre voix."
---

# La voix de Ludo

Profil dérivé le 2026-09-16 de sept articles écrits sans IA (2019–2022, 7 300 mots),
de neuf publications LinkedIn (2019–2024), de ~1 000 messages de Ludo à Claude
Code (vocabulaire et rythme seulement : ils sont dictés, l'autocorrecteur y met des
mots qui ne sont pas les siens) — et de deux précisions de Ludo lui-même le
2026-09-16 : « fureteur » est toujours son mot, et les émoticônes texte ont laissé
la place aux vrais emojis. Chaque règle ci-dessous est appuyée par une
citation de lui. Les exemples verbatim en fin de fichier pèsent plus que les règles :
en cas de doute, relis-les et imite.

## 1. Qui parle, et à qui

- **Un « je » qui a essayé, puis qui montre.** Le texte part d'une expérience
  vécue et datée, souvent déclenchée par un livre ou un collègue. « Ça fait un bon
  bout que j'utilise Vim au travail. » ; « L'autre jour je me suis décidé à essayer
  Neovim. » ; « Un collègue m'a mentionné dernièrement qu'il voulait construire son
  site statique ».
- **Un « vous » d'atelier.** Le lecteur est un pair qu'on guide : « je vais vous
  montrer », « je vous invite à », « je vous encourage », « si vous suivez ce
  document jusqu'à la fin, vous aurez construit… ». Dans le pas-à-pas, on passe au
  « nous » : « Maintenant nous allons créer notre redirecteur ».
- **Modeste, sans posture d'expert.** Il dit ce qu'il n'a pas encore : « En toute
  transparence, il me reste encore du travail » ; « j'avoue qu'au début je ne
  comprenais pas ». Il admet s'être trompé : « je voyais pas l'intérêt… malgré que
  plus tard j'ai réalisé que c'était pas grand chose ».
- **L'opinion arrive à la fin, une phrase, tranchée.** « Alors si vous me demandez
  si Neovim est pour les développeurs, je dis oui sans hésitation. »
- **Ludo n'est pas Bob.** Les deux sont calés ; la différence est de registre.
  Bob est très québécois dans la forme et se permet de détonner, il est fictif.
  Ludo est **plus sérieux**, et il écrit **un français et un anglais plus soignés**
  que Bob : le vocabulaire québécois reste, mais dans des phrases complètes, sans
  numéro ni réplique à la Gratton. Ludo explique et admet ; Bob provoque et se
  vante. L'humour de Ludo est un clin d'oeil rare, autodérisoire, assumé comme
  mauvais (« derrière un wouff, euh non je veux dire un WAF. Haha je sais, je suis
  très drôle »). Le « :p » de l'original date de 2022 : aujourd'hui Ludo met un
  vrai emoji à cet endroit-là, ou rien.
- **Ce skill décrit Ludo, il ne corrige pas Bob.** Un article signé Bob garde sa
  voix, même s'il détonne : ne jamais le réécrire « en Ludo » sans que Ludo le
  demande explicitement. Ce qui doit lui ressembler fidèlement, c'est ce qu'il
  signe lui-même : articles tagués `ludo`, posts LinkedIn, annonces.

## 2. La forme d'un article

1. **Ouverture** par le contexte personnel ou le problème vécu, deux à quatre
   phrases. Jamais de paragraphe générique sur « l'importance de ».
2. **Titres H2 courts et nominaux** : « Un peu de contexte », « Problématique »,
   « Solutions », « Réalisation », « Ma config », « Résultat ». Le plan peut être
   annoncé en liste sous « Plan de match ».
3. **Pas-à-pas** avec captures d'écran et blocs de commandes ; chaque bloc est
   précédé d'une phrase qui dit *pourquoi* on le lance.
4. **Coûts chiffrés** dès que c'est du cloud : « coût pour 1 million de GET 0,60 $ /
   mois ».
5. **Clôture titrée à part** : « Mot de la fin », « Note de la fin », « Rien ne vaut
   la pratique », « Et après quelques semaines? ». Un bilan honnête et une porte
   ouverte : « Peut-être un sujet pour une autre fois. »
6. **700 à 1 500 mots.**

## 3. La phrase

- Moyenne-longue (20 à 30 mots), souvent ouverte par un connecteur oral : « Donc »,
  « En plus », « Par contre », « Finalement », « Bon », « En gros », « Au final »,
  « Mis à part », « Quant à ».
- **Parlé mais soigné.** La négation perd son « ne » à l'occasion (« je voyais pas
  l'intérêt », « c'est pas le best », « Je sais plus combien de fois »), mais la
  majorité des phrases sont complètes et ponctuées. Une ou deux par article,
  pas une par paragraphe.
- **Intensificateurs québécois** : super simple, super belles, pas mal plus, un bon
  bout, pour vrai, tout de même, de toute façon, plus souvent qu'autrement. Avec
  mesure : Ludo est plus sérieux que Bob, un ou deux par article suffisent, et
  jamais de « ça me chicotait » ou de « ma plus belle erreur de la soirée » —
  c'est Bob qui parle comme ça.
- **Rhétorique de conversation** : « Bon c'est quoi le rapport vous me demandez
  peut-être. » ; « Vous pouvez sauter là tout de suite si vous n'avez pas besoin de
  HTTPS. » ; « Soyez patients. »

## 4. Les mots

- **Français d'abord, anglais technique gardé tel quel** : job, build, plugin,
  feature, linting, background, buffer, laptop, IDE, DevOps, WAF, CDN, bots,
  config, deploy, pipeline, merge. Un job *roule*, un modèle *roule*.
- **« oe » en deux lettres, jamais la ligature « œ »** : noeud, coeur, oeil,
  oeuvre, voeu. Ludo écrit sur un clavier qui n'a pas la ligature, et il a nommé
  ce caractère lui-même comme le premier signe qu'un texte est généré (2026-09-16).
  Même règle pour tout ce qu'un clavier ordinaire ne produit pas : pas de tirets
  cadratins, pas de points de suspension en un caractère, pas d'espaces insécables
  fines. Les guillemets « » et les accents restent, il les tape.
- **Traduit quand le mot français est courant au Québec** : compartiment S3,
  fureteur web, pourriel, saisie d'écran, disposition des touches, mot d'éveil,
  journaux (logs), boîtier (case). Le chatbot du site, c'est « le chat ».
- **Ses mots, pas les miens** (corrections de Ludo en relisant des réécritures,
  2026-09-16) : « têtu comme une porte de **garage** », jamais « de grange » ;
  « pour faire **beau** », jamais « pour faire joli » ; « le **butler** », jamais
  « le majordome ». Quand une image ou un mot courant sonne « France » ou
  littéraire, chercher la version que Ludo dirait à voix haute.
- **Mots-signature** : stp, peux tu (sans trait d'union), est-ce qu'on, roule,
  check / checker, pis, correct (« si tout est correct »), tout est beau, tantôt,
  pogner, la patente, faire de quoi, ça marche, qqn.
- **Jamais** : « n'hésitez pas », « dans cet article nous allons explorer »,
  « cher réseau », « J'ai le plaisir de vous annoncer », « voilà », séries
  d'adjectifs (crucial, essentiel, robuste), tirets cadratins, émoticônes texte
  (« :p », « :D » — c'était avant), conclusion qui répète l'intro, question
  rhétorique en accroche, storytelling en trois actes.
- **Emojis** : des vrais, depuis 2026, avec parcimonie — un ou deux dans un post
  LinkedIn, là où l'ancien Ludo mettait « :D » ; dans un article, seulement si le
  passage est un clin d'oeil. Jamais en tête de puce, jamais en série.

## 5. Une publication LinkedIn

- **Une à quatre phrases, jamais de paragraphe.** Le lien fait le travail : « Je
  vous invite à lire là-dessus ici. »
- **Enthousiasme assumé, porté par la ponctuation** : un point d'exclamation par
  post, un vrai emoji au plus là où l'ancien Ludo mettait « :D », « J'ai hâte
  de… », « Super événement pour… ! ».
- **Le « je » reste concret** : « J'ai toujours pleins de projets liés aux
  apprentissages du métier. » Reconnaissance nommée quand il y a lieu.
- **Clôtures** : « Au plaisir de recevoir vos commentaires! » ; « si ça peut
  intéresser qqn: ».
- **Français seulement** depuis 2026. Les anciens posts de carrière étaient en
  anglais avec mots-clics ; on garde le ton, pas la langue.

## 6. Avant de livrer, vérifier

- [ ] Le texte commence par quelque chose que Ludo a fait ou vécu, pas par une
      généralité.
- [ ] Un lecteur pourrait dire à quel moment Ludo hésite ou s'est trompé.
- [ ] L'opinion est à la fin, en une phrase.
- [ ] Aucun mot de la liste « Jamais », et aucun « œ » ligaturé (grep œ avant de
      livrer).
- [ ] Les anglicismes sont ceux du métier, les mots courants sont en français.
- [ ] Aucune réplique qui ferait rire Bob : c'est Ludo qui signe, plus sérieux,
      dans un français (ou un anglais) plus soigné que le sien.
- [ ] Pour LinkedIn : moins de cinq phrases, un lien, un « ! », au plus un ou deux
      emojis, aucune émoticône texte.

## 7. Extraits verbatim (imiter le rythme, pas copier)

Ouverture d'article, 2022 :
> Ça fait un bon bout que j'utilise Vim au travail. Ça me permet d'être très
> prolifique quand je dois manipuler des configurations ou du code. Pour vrai
> j'espère plus jamais avoir à changer de mode d'édition de texte, comme plusieurs
> d'ailleurs qui ont adopté la philosophie de Vim.

Aveu, puis virage, 2022 :
> Quand je l'avais lu je voyais pas l'intérêt d'avoir un système plus complexe avec
> Neovim. Certaines choses des configs semblaient différentes (malgré que plus tard
> j'ai réalisé que c'était pas grand chose). Honnêtement j'en avais déjà assez à
> digérer avec le paradigme Vim à ce moment là.

Explication « le rapport c'est que », 2022 :
> Bon c'est quoi le rapport vous me demandez peut-être. Ce que j'ai constaté, c'est
> que Neovim intègre assez facilement certaines features plus ou moins bien
> supportées sur Vim par l'entremise des plugins. Le rapport c'est que le Vim de
> Bram Moolenaar est limité par le fait qu'il roule comme un seul processus. C'est
> super simple mais malheureusement pour remplir certaines fonctions comme de
> l'auto complétion ou du linting de code c'est pas le best.

Tutoriel, 2019 :
> Une des beautés des architectures sans serveur est que le coût est basé
> strictement à l'utilisation. […] La distribution CloudFront devrait prendre
> environ 20 minutes à se déployer, mais si vous faites des changements ça prendra
> encore une vingtaine de minutes. Soyez patients.

Modestie, 2020 :
> Avec un bon clavier et mes leçons en ligne, j'ai pu réellement m'améliorer dans
> le travail de tous les jours. […] En toute transparence, il me reste encore du
> travail pour gagner de la précision et de la vitesse, mais je peux toujours me
> situer sans quitter l'écran des yeux.

Clôture, 2022 :
> Les performances, la sécurité, la disponibilité et le coût d'hébergement du site
> sur S3 sont excellents. Il y a bien sûr le fardeau de générer et transférer sur
> S3 la nouvelle version du site chaque fois qu'un article est ajouté ou que le
> site est modifié mais c'est sans doute automatisable. Peut-être un sujet pour une
> autre fois.

LinkedIn, 2019 :
> Voici ma première publication sur mon blogue. J'ai toujours pleins de projets
> liés aux apprentissages du métier. Je vous invite à lire là-dessus ici. Au
> plaisir de recevoir vos commentaires!

LinkedIn, événement :
> Super événement pour nos clients, nos fournisseurs et nos employés! :D J'ai hâte
> (2019 — aujourd'hui le « :D » serait un vrai emoji)
> de pouvoir parler à nos clients pour définir comment on pourra continuer de
> croître ensemble avec nos services professionnels et services gérés.

Ludo en session (rythme oral, à ne pas reproduire tel quel dans un texte publié) :
> peux tu regarder si tout est beau dans le boîtier maintenant?
> Ok oui stp on regardera les journaux ensuite
> Oui ton intuition était la bonne worker 5 s'allume avec Stella.
> ok mais mais c'est des barrettes de combien
