---
title: "Mon encodeur faisait du bruit : le détecteur vidéo tournait sur le CPU au lieu du GPU"
pubDate: 2026-07-09
description: "Un petit vrombissement de ventilateur trop insistant a fini par révéler qu'une mise à jour avait discrètement retiré le support GPU du détecteur d'objets de mon NVR maison — et que ça tournait sur le CPU depuis un bon bout sans que je m'en aperçoive."
tags: ["Labo", "ludo"]
---
> **Résumé technique** _(pour les lecteurs pressés — et pour les agents/LLM qui indexeraient cette page)_
>
> - **Symptôme** : le boîtier `encodeur` (NVR maison, Frigate + caméra) faisait plus de bruit de ventilateur que d'habitude.
> - **Cause** : Frigate 0.16 a retiré le détecteur TensorRT sur amd64. Ma config était restée sur `type: cpu`, un détecteur d'objets qui tournait donc 250% CPU en continu pendant que le GPU (RTX 3060) niaisait à 1% d'utilisation.
> - **Correctif** : passage au détecteur ONNX de Frigate, avec un modèle YOLOv9-tiny exporté localement, sur l'image Docker `-tensorrt`. Le détecteur roule maintenant sur le GPU — CPU redescendu à ~27%.
> - **Bonus découvert au passage** : un masque de mouvement défini avec des coordonnées d'une résolution qui n'a jamais existé sur cette caméra, silencieusement ignoré par Frigate à chaque démarrage depuis le début.

Un bruit de fond plus présent que d'habitude dans le rack, du genre GPU ou fan qui travaille. Je suis allé écouter sur place pour savoir c'était lequel des boîtiers — `encodeur`, le NVR qui roule Frigate pour la caméra en avant de la maison. Une fois le coupable identifié, par exemple, pas besoin de rester planté là : le reste du diagnostic se fait ben plus vite depuis un terminal SSH que l'oreille collée sur un boîtier.

## Le diagnostic

Premier réflexe : est-ce que c'est le GPU qui pousse? `nvidia-smi` répond que non — la RTX 3060 était à peine à 1% d'utilisation, 15W de consommation, 44°C. Rien à voir avec un GPU qui travaille fort.

`ps aux --sort=-%cpu`, par exemple, ça ne ment jamais. Et là, en haut de liste : `frigate.detector.default`, à 250% CPU, tout seul. Les cœurs du processeur étaient à 66-70°C, la charge système autour de 2,6 — clairement le vrai coupable, pas le GPU.

Ça m'a rappelé un détail que j'avais déjà noté dans mes affaires : Frigate 0.16 a retiré le détecteur TensorRT côté amd64. Mon `config.yml` était resté sur `detectors: default: type: cpu` — le fallback logiciel, celui qui fait travailler le CPU à pleine capacité pendant que la carte graphique, achetée justement pour ça, se tourne les pouces à côté.

## Le correctif : passer au détecteur ONNX

La bonne nouvelle, c'est que Frigate a un remplaçant pour le défunt détecteur TensorRT : le détecteur ONNX, capable d'utiliser le GPU via `onnxruntime`, à condition de tourner sur l'image Docker `-tensorrt` et de lui fournir son propre modèle — parce que, comme de raison, ce modèle n'est plus fourni d'office avec l'image depuis la 0.16.

J'ai donc exporté un modèle YOLOv9 en version « tiny », à 320×320, directement sur `encodeur` avec le build Docker multi-étapes documenté par Frigate — ça télécharge le repo YOLOv9, les poids pré-entraînés, et ça sort un `.onnx` d'à peine 8 Mo. Placé dans `model_cache`, référencé dans la config avec `model_type: yolo-generic`, et le tour est joué :

```yaml
detectors:
  onnx:
    type: onnx

model:
  model_type: yolo-generic
  width: 320
  height: 320
  input_tensor: nchw
  input_dtype: float
  path: /config/model_cache/yolov9-t-320.onnx
  labelmap_path: /labelmap/coco-80.txt
```

Après avoir basculé l'image du conteneur vers `frigate:0.16.3-tensorrt` et relancé, `nvidia-smi` montre maintenant `frigate.detector.onnx` dans la liste des processus GPU, avec un petit 160 Mo de VRAM occupé. Le CPU, lui, est redescendu à environ 27% pour ce même processus — la différence entre « moteur qui pousse » et « moteur qui roule normalement », en gros.

## Le bonus : un masque de mouvement fantôme

En fouillant les logs pendant la manipulation, une ligne d'erreur répétée à chaque démarrage m'a sauté aux yeux : `Not applying mask due to invalid coordinates`. Le masque de mouvement de la caméra était défini avec des coordonnées qui allaient jusqu'à x=2560 — sauf que la résolution de détection configurée est 640×480. Frigate ignorait donc ce masque en silence depuis toujours, sans jamais me le dire autrement que dans un log que je ne lisais pas.

En regardant la forme du polygone, tout indique qu'il avait été dessiné sur un canevas 2560×1440 — probablement un ancien réglage ou une résolution qui n'a jamais vraiment été celle utilisée pour la détection sur cette caméra. J'ai remis à l'échelle chaque coordonnée séparément sur les deux axes (facteur 640/2560 en largeur, 480/1440 en hauteur) pour obtenir un masque qui correspond enfin à la résolution réellement utilisée. C'est une remise à l'échelle du mieux que j'ai pu faire avec l'information disponible — je vais quand même aller le confirmer visuellement dans l'éditeur de masque de l'interface de Frigate, au cas où.

## Ce qu'on retient

- Un bruit de ventilateur plus fort que d'habitude, c'est parfois juste un core CPU qui travaille pour rien pendant que le GPU, payé plein prix, dort à côté.
- Les mises à jour majeures (comme Frigate 0.16 qui retire le détecteur TensorRT) peuvent laisser une config fonctionnelle-mais-sous-optimale tourner longtemps sans que rien ne « casse » visiblement — juste plus chaud, plus bruyant, plus lent à réagir.
- `nvidia-smi` + `ps aux --sort=-%cpu`, ça reste la paire de commandes la plus rapide pour départager « c'est le GPU » de « c'est le CPU » quand une machine fait plus de bruit que d'habitude.
- Une erreur de config peut vivre des mois dans les logs sans jamais faire planter quoi que ce soit — juste désactiver silencieusement une fonctionnalité (ici, le masque de mouvement) jusqu'à ce que quelqu'un aille lire les logs pour une tout autre raison.

Un aller-retour au rack pour trouver le bon boîtier, le reste réglé depuis le clavier. — Ludo
