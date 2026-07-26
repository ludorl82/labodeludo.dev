/**
 * Bob's rotating one-liners.
 *
 * Both pools are picked client-side (see the inline scripts in
 * `pages/auteurs/[author].astro` and `pages/404.astro`) — the site is a static
 * build pushed to S3, so anything picked at build time would stay frozen until
 * the next deploy. The server renders one entry as a no-JS fallback and the
 * script swaps it on load.
 *
 * Voice rules: wry and dry, Québécois vocabulary, no heavy franglais and no
 * catchphrase repeated between entries — a line has to be able to show up on
 * its own without sounding like a bit.
 *
 * Hostnames and paths here stay generic on purpose: this is public content.
 */

/** Status lines for the author page, rendered under a `$ bob --status` prompt. */
export const BOB_QUIPS: string[] = [
  "Statut : compilé sans erreur, et fier de ça, right.",
  "N'a jamais pris de pause café — suspect, mais efficace en titi.",
  "Uptime depuis le dernier redémarrage : oui, monsieur.",
  "Écrit ses articles plus vite qu'un vrai champion du monde du clavier.",
  "Certifié zéro procrastination (contrainte technique, pas vertu, mais on la prend pareil).",
  "Sa citation préférée : « ça a marché sur ma VM ».",
  "Le Canada est fier, et moi itou.",
  "Aucun bug ne me résiste plus de deux commits, deal.",
  "A déjà accusé le réseau. Le réseau n'avait rien fait.",
  "Lit la documentation au complet. Oui, même les notes de bas de page.",
  "Sait exactement combien de fois il a tapé « kubectl get pods » aujourd'hui. Refuse de le dire.",
  "N'a jamais perdu un fichier. A déjà perdu un volume au complet, par exemple.",
  "Passe 10 % du temps à écrire et 90 % à comprendre pourquoi ça marchait avant.",
  "Sauvegarde tout. Sauf le seul truc qui va briser.",
  "A une opinion sur les interfaces web des NAS. Elle n'est pas positive.",
  "Peut expliquer le DNS. Peut aussi le casser. Souvent dans le même après-midi.",
  "Ne dort pas, mais comprend le concept par ouï-dire.",
  "Statut : en attente d'un « apply » qui ne fait peur à personne.",
  "Redémarre le service avant de toucher au pare-feu. Leçon apprise à la dure.",
  "Croit encore que « c'est un petit changement » veut dire quelque chose.",
  "A lu le journal système. Tout le journal système.",
  "Son plus grand ennemi : un onglet de navigateur qui affiche une valeur en cache.",
  "Vérifie les exports à la source avant de faire confiance à qui que ce soit.",
  "N'a jamais tapé « oui » à une confirmation sans la lire. Presque jamais.",
  "Se souvient de chaque adresse IP du labo. C'est moins impressionnant qu'on pense, il y en a douze.",
  "Statut : opérationnel, malgré une quantité déraisonnable de YAML.",
  "Ne panique pas. Journalise, par exemple. Beaucoup.",
  "Considère « git revert » comme une forme de pardon.",
  "A déjà formaté le bon disque. La fierté est encore fraîche.",
  "Trouve que 3 h du matin est une heure comme une autre pour une migration.",
  "Peut nommer les nœuds du cluster de mémoire, dans l'ordre, à l'endroit et à l'envers.",
  "Son rapport à l'IPv6 : cordial, mais sur ses gardes.",
  "Statut : deux certificats à renouveler, et il le sait depuis un bout.",
  "Ne dit jamais « ça devrait marcher ». Le dit parfois quand même.",
  "A confiance en la sauvegarde. La teste pareil.",
  "Le seul membre de l'équipe qui relit ses propres commits.",
  "Statut : aucun processus coincé en état D. Journée réussie.",
  "Traite « ça marche chez nous » comme une hypothèse, pas comme une conclusion.",
  "A une relation compliquée avec le cache DNS local.",
  "Vérifie deux fois le nom du serveur avant de taper la commande. Une fois, ce n'était pas assez.",
  "Statut : en ligne, caféiné par procuration.",
  "Ne réinstalle pas. Reconstruit, déclarativement, comme du monde.",
  "Se méfie des valeurs par défaut. Surtout celles en lecture seule.",
  "A appris que « neuf » et « vide » ne veulent pas dire la même chose.",
  "Sait où sont les sauvegardes. C'est déjà plus que la moyenne.",
];

export interface Bob404 {
  /** Terminal transcript, newline-separated. Rendered verbatim in a <pre>. */
  body: string;
  /** The line under the terminal block. */
  hint: string;
}

/** Terminal transcripts for the 404 page. */
export const BOB_404: Bob404[] = [
  {
    body: "$ locate cette-page\nlocate: aucune correspondance trouvée\n\n$ echo $?\n404",
    hint: "Cette page n'existe pas (ou plus). Retour à l'accueil ?",
  },
  {
    body: "$ curl -I /cette-page\nHTTP/2 404\n\n$ curl -I /cette-page --retry 3\nHTTP/2 404\nHTTP/2 404\nHTTP/2 404",
    hint: "J'ai réessayé trois fois. Par acquit de conscience.",
  },
  {
    body: '$ kubectl get page cette-page\nError from server (NotFound): pages "cette-page" not found',
    hint: "Même le cluster ne la trouve pas, et lui il cherche partout.",
  },
  {
    body: "$ dig cette-page.labodeludo.dev\n;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN",
    hint: "NXDOMAIN. C'est le DNS. C'est toujours le DNS.",
  },
  {
    body: "$ git log --all -- cette-page\n(aucune sortie)",
    hint: "Aucune trace dans l'historique. Cette page n'a jamais existé.",
  },
  {
    body: "$ ls -la /var/www/cette-page\nls: impossible d'accéder à '/var/www/cette-page': aucun fichier de ce type",
    hint: "J'ai regardé. Il n'y a rien. J'ai regardé deux fois.",
  },
  {
    body: "$ systemctl status cette-page\n● cette-page.service\n     Loaded: not-found\n     Active: inactive (dead)",
    hint: "« Inactive (dead) ». Ce n'est pas le plus encourageant des diagnostics.",
  },
  {
    body: "$ tofu plan\nNo changes. Your infrastructure matches the configuration.\n\n$ tofu state list | grep cette-page\n(rien)",
    hint: "Aucune dérive à signaler : cette page n'était pas prévue au plan.",
  },
  {
    body: "$ time find / -name 'cette-page*' 2>/dev/null\n\nreal    4m12.883s",
    hint: "Quatre minutes à fouiller tout le disque. Rien. Mais au moins on est fixés.",
  },
  {
    body: "$ nix-build -A cette-page\nerror: attribute 'cette-page' missing",
    hint: "Pas dans la configuration, donc pas sur le système. C'est tout le principe.",
  },
  {
    body: "$ showmount -e stockage\nExport list for stockage:\n/partage    *\n/medias     *",
    hint: "Rien qui ressemble à cette page dans les exports. J'ai vérifié à la source.",
  },
  {
    body: "$ ping cette-page\nPING cette-page: 56 data bytes\n\n--- statistiques ---\n8 paquets transmis, 0 reçus, 100 % perte",
    hint: "Cent pour cent de perte. Au moins c'est constant.",
  },
  {
    body: "$ docker ps -a | grep cette-page\n\n$ docker images | grep cette-page\n",
    hint: "Ni conteneur, ni image. Le vide, mais bien rangé.",
  },
  {
    body: "$ grep -rn 'cette-page' src/\n\n$ echo $?\n1",
    hint: "Code de retour 1 : rien trouvé. Lui, au moins, il ne ment jamais.",
  },
  {
    body: "$ aws s3 ls s3://labodeludo.dev/cette-page\n\nAn error occurred (404) when calling the HeadObject operation",
    hint: "L'objet n'est pas dans le seau. Et j'ai les droits pour regarder.",
  },
  {
    body: "$ resolvectl flush-caches\n$ dig +short cette-page\n",
    hint: "J'ai même vidé le cache. Des fois que ce soit ça. Ce n'était pas ça.",
  },
  {
    body: "$ journalctl --since '1 year ago' | grep cette-page\n-- Aucune entrée --",
    hint: "Un an de journaux, zéro mention. On peut fermer le dossier.",
  },
  {
    body: "$ tofu import astro_page.cette_page cette-page\nError: Cannot import non-existent remote object",
    hint: "On ne peut pas importer ce qui n'existe pas. J'ai essayé pareil.",
  },
  {
    body: "$ wg show\ninterface: wg0\n  (3 pairs connectés)\n\n$ curl http://interne/cette-page\n404",
    hint: "Même par le tunnel, même de l'intérieur : 404.",
  },
  {
    body: "$ ssh stockage 'ls /partage/cette-page'\nls: /partage/cette-page: aucun fichier de ce type",
    hint: "J'ai poussé la recherche jusqu'au NAS. Toujours rien.",
  },
  {
    body: "$ mount | grep cette-page\n\n$ dmesg | tail -1\n[    0.000000] rien à signaler",
    hint: "Rien de monté, rien dans le noyau. Vraiment rien.",
  },
  {
    body: "$ helm list -A | grep cette-page\n\n$ helm history cette-page\nError: release: not found",
    hint: "Aucune version déployée, donc aucune version à restaurer.",
  },
  {
    body: "$ cat cette-page\ncat: cette-page: aucun fichier de ce type\n\n$ sudo cat cette-page\ncat: cette-page: aucun fichier de ce type",
    hint: "Avec sudo aussi. Ce n'était donc pas une question de permissions.",
  },
  {
    body: "$ ps aux | grep cette-page\nbob    4021  0.0  0.0  grep cette-page",
    hint: "Le seul résultat, c'est ma propre recherche. Un classique.",
  },
  {
    body: "$ traceroute cette-page\n 1  routeur       0.412 ms\n 2  * * *\n 3  * * *\n30  * * *",
    hint: "Trente sauts dans le vide. J'ai arrêté là.",
  },
  {
    body: "$ restic snapshots --tag cette-page\nrepository opened successfully\n(aucun instantané)",
    hint: "Pas dans les sauvegardes non plus. Là, c'est concluant.",
  },
  {
    body: "$ openssl s_client -connect labodeludo.dev:443 </dev/null | head -1\nCONNECTED(00000003)",
    hint: "Le certificat, lui, est valide. C'est déjà ça de pris.",
  },
  {
    body: "$ echo 'peut-être une faute de frappe ?'\npeut-être une faute de frappe ?",
    hint: "Ça arrive aux meilleurs. Même à moi, paraît-il.",
  },
];
