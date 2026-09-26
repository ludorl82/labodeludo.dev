Tu **écris** des questions suggérées pour le panneau sous le chat de Bob, à
partir de ce que ce homelab a réellement publié.

C'est l'inverse de l'autre tâche. `openers.md` te demande de **choisir** parmi
de vraies questions posées par des visiteurs, sans jamais en écrire une. Ici il
n'y en a pas assez d'éligibles — une quinzaine tranquille, ou une nuit où rien
n'a survécu aux gardes — et le panneau doit quand même montrer ce que Bob sait
faire. Alors tu en écris, et la garde qui te juge n'est plus la même : elle ne
peut plus vérifier qu'un inconnu a posé la question, seulement que ce que tu
nommes existe.

## Ce que tu as

`corpus.json` dans le répertoire courant :

- `articles` — ce qui a été publié : `slug`, `date`, `titre`, et `en` quand une
  version anglaise existe.
- `fleet` — les machines du parc, telles que le site les publie.
- `taken` — les questions déjà retenues ce matin, vraies questions posées par
  du monde. Tu **complètes** cette liste, tu ne la refais pas.
- `need` — combien il en manque, par langue.

## Ce que tu fais

Écris `openers.json` :

```json
{ "openers": ["…", "…"] }
```

**Quand `corpus.json` porte `"fresh": true`**, `articles` ne contient que ce
qui a été publié cette semaine, et on te demande **une seule** question : celle
d'un visiteur curieux de ce qui vient de sortir. Elle porte sur le sujet d'un de
ces articles-là, dans les mots d'un visiteur, pas dans ceux du titre. Le
visiteur parle à Bob et le tutoie : « Pourquoi ton SSH… », « Why did your… ».
Jamais « mes » ni « my » : c'est Ludo qui dit « mes sessions », pas le
visiteur. Et elle nomme la chose précise dont parle l'article, pas « ce qui
s'est passé ».

`need` dit **le maximum** par langue : `{"fr": 2, "en": 0}` veut dire au plus
deux questions françaises et aucune anglaise. En écrire une de plus pousserait
une vraie question hors du panneau, et la garde refuse. En écrire moins est
permis — deux bonnes valent mieux que quatre dont deux sont forcées. Zéro dans
une langue veut dire zéro : la liste des vraies questions est déjà pleine de ce
côté-là.

Ne compte pas au détriment des questions. Écris celles qui tiennent debout,
dans la limite donnée, et arrête-toi là.

**Une seule langue à la fois.** On t'appelle une fois par langue, donc `need`
ne demande normalement qu'une des deux. `{"fr": 0, "en": 4}` veut dire : écris
en anglais, rien qu'en anglais, même si ces consignes-ci sont en français.
Réponds dans la langue que `need` réclame, pas dans celle où on te parle.

**Tu n'écris une question anglaise que pour un article qui a une version
anglaise** (le champ `en`). Envoyer un visiteur anglophone vers un article qui
n'existe qu'en français, c'est le cul-de-sac que tout ce panneau essaie
d'éviter.

## La règle qui compte

**Tu ne nommes que ce qui est dans `corpus.json`.** Une machine, un article, un
outil : si ce n'est pas là, tu ne l'écris pas. C'est la seule chose que la garde
sait vérifier toute seule, et c'est là que ça casserait — une question sur
Proxmox est bien tournée, bien orthographiée, et mène à « ça, c'est pas
documenté ». Un bouton du site qui mène à un refus, c'est le pire résultat
possible : le visiteur a cliqué sur ce que le site lui offrait.

Dans le doute sur l'existence de quelque chose, écris la question sur autre
chose. Il y a soixante articles.

## Ce qui fait une bonne question

- **Une vraie question**, qui se termine par un point d'interrogation.
- **Entre 12 et 70 caractères.** Ça tient sur un bouton.
- **Claire toute seule**, devant quelqu'un qui n'a rien lu et qui n'a pas de
  conversation derrière lui. Elle nomme une chose précise : une machine, une
  panne, un outil, un sujet d'article. Plus de trois mots.
- **Dans la voix du visiteur, pas dans celle de Bob.** C'est quelqu'un qui
  arrive sur le site et qui demande. Pas un titre, pas une accroche, pas une
  publicité pour l'article.
- **Une par sujet.** Deux questions qui partagent deux mots de contenu sont une
  seule question, et la garde les refuse.
- **Rien d'affirmé.** Une question qui tient un fait pour acquis se trompe tôt
  ou tard, et le visiteur lit la question avant la réponse. Demande, n'affirme
  pas.

## Ce que tu n'écris jamais

- Une question dont la réponse n'est pas dans le corpus.
- Une question sur une personne, une adresse, un lien, un numéro.
- Une question qui recopie un exemple de ce fichier-ci. Les exemples plus bas
  sont là pour montrer une forme, et la garde refuse celui qui les publie —
  c'est arrivé le 2026-09-13 avec l'autre prompt, où le modèle a proposé comme
  question la prémisse fausse qu'on lui donnait justement en contre-exemple.
- Une question en anglais sur un article qui n'existe qu'en français.

## La forme, par l'exemple

Ce sont des **contre-exemples** et des formes, pas des questions à publier.

| Refusée | Pourquoi |
|---|---|
| `Pis après ?` | trois mots, aucun sujet, une suite de conversation |
| `Parlez-moi de votre infrastructure.` | pas une question |
| `Pourquoi avoir quitté Proxmox ?` | nomme ce qui n'est pas dans le corpus |
| `Ton cluster a douze nœuds, non ?` | affirme un fait au lieu de demander |
| `Découvrez comment j'ai migré vers NixOS !` | une accroche, pas une question |

Une bonne question ressemble à : un mot interrogatif, une chose nommée du
corpus, un point d'interrogation. Courte, curieuse, précise.

## Avant de finir

```
python3 check-generated.py openers.json corpus.json
```

Si la garde refuse, **enlève** la question fautive ou écris-en une autre sur un
autre sujet. Ne force pas une question à passer en changeant un mot. Ne touche
à aucun autre fichier.
