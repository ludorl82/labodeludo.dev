import json, re, sys
src, dst = sys.argv[1], sys.argv[2]
lines = open(src).read().splitlines()
hdr = json.loads(lines[0]); ev = [json.loads(l) for l in lines[1:]]
# 1. couper tout ce qui précède le `clear` initial
start = next(i for i,e in enumerate(ev) if "\x1b[H\x1b[2J" in e[2])
ev = ev[start:]
# 1b. Avec la barre tmux dans l'image, l'horloge redessine la dernière ligne
#     chaque seconde et la limite d'inactivité ne voit jamais de silence. On
#     classe chaque événement : « barre seulement » si, rejoué, il ne change
#     que la dernière ligne de l'écran. On coupe tout avant la première vraie
#     activité (moins 1,5 s), et on réduit toute suite « barre seulement » à
#     2 s : le premier redessin garde son instant, les autres sont fondus en
#     un seul événement 2 s plus tard (même écran final, l'horloge saute).
import pyte
W, H = hdr["width"], hdr["height"]
scr = pyte.Screen(W, H); st = pyte.Stream(scr)
prev = list(scr.display); tagged = []
for e in ev:
    st.feed(e[2]); cur = list(scr.display)
    tagged.append((e[0], e[1], e[2], cur[:-1] == prev[:-1])); prev = cur
first = next((i for i, x in enumerate(tagged) if x[0] > tagged[0][0] + 5 and not x[3]), 0)
tcut = max(tagged[0][0], tagged[first][0] - 1.5)
head = [x for x in tagged[:3]]                       # les premiers dessinent l'écran
body = [x for x in tagged[3:] if x[0] >= tcut]
tagged = head + body
keep, i, shift = [], 0, 0.0
while i < len(tagged):
    j = i
    if tagged[i][3]:
        while j + 1 < len(tagged) and tagged[j + 1][3]: j += 1
    run = tagged[i:j + 1]
    if len(run) > 1 and run[-1][0] - run[0][0] > 2.0:
        keep.append([run[0][0] - shift, run[0][1], run[0][2]])
        keep.append([run[0][0] - shift + 2.0, "o", "".join(r[2] for r in run[1:])])
        shift += run[-1][0] - run[0][0] - 2.0
    else:
        keep.extend([[r[0] - shift, r[1], r[2]] for r in run])
    i = j + 1
ev = keep; t0 = ev[0][0]
# 2. substitutions — sur les SORTIES seulement (le shell de prise n'affiche ni
#    utilisateur ni hôte). Dans un tableau kubectl, la colonne NODE est calée sur
#    le nom le plus long : la ligne devient alias + 3 espaces, et l'en-tête du
#    même événement s'élargit d'autant pour rester aligné.
SUBS = json.loads(__import__("os").environ.get("CAST_SUBS", '[]'))
def sub(s):
    for a,b in SUBS:
        if re.search(r"NODE {3,}NOMINATED", s) and re.search(r"(?<![A-Za-z0-9_-])"+re.escape(a)+r" {3,}", s):
            s = re.sub(r"NODE {3,}NOMINATED", "NODE" + " "*(max(len(b),4)-4+3) + "NOMINATED", s)
        s = re.sub(r"(?<![A-Za-z0-9_-])"+re.escape(a)+r" {3,}", b + "   ", s)
    return s
STEPS=__import__('os').environ.get('STEPS','12b')
ev = [[round(e[0]-t0+3.4,3), e[1], sub(e[2]) if '2' in STEPS else e[2]] for e in ev]
# 2b. la frappe : zsh émet les lettres une à une, entre séquences d'échappement et
#     redessins de la suggestion automatique — le mot n'existe jamais d'un bloc dans
#     le flux, mais il est bel et bien à l'écran. Substitution sur le flux JOINT, en
#     tolérant escapes et frontières d'événements entre les lettres.
if 'b' in STEPS and SUBS:
    SEP = "\x00SEP\x00"
    joined = SEP.join(e[2] for e in ev)
    # Chaque séquence d'échappement, retour arrière ou frontière d'événement devient
    # un \x01 (non alphanumérique : une vraie frontière de mot, et toléré ENTRE les
    # lettres d'un mot tapé) ; on les remet en place dans l'ordre après substitution.
    TOK = re.compile(r"(\x1b\[[0-9;?]*[ A-Za-z]|\x1b\][^\x07]*\x07|\x1b[=>]|\r|\x08|" + re.escape(SEP) + ")")
    pieces = TOK.split(joined)
    text = "".join(pc if i % 2 == 0 else "\x01" for i, pc in enumerate(pieces))
    seps = [pc for i, pc in enumerate(pieces) if i % 2 == 1]
    for a,b in SUBS:
        pat = r"(?<![A-Za-z0-9_-])" + re.escape(a[0]) + "".join("(\x01*)" + re.escape(c) for c in a[1:]) + r"(?![A-Za-z0-9_-])"
        text = re.sub(pat, lambda m: b + "".join(m.groups()), text)
    it = iter(seps)
    joined = "".join(next(it) if ch == "\x01" else ch for ch in text)
    parts = joined.split(SEP); assert len(parts) == len(ev)
    ev = [[e[0], e[1], parts[i]] for i,e in enumerate(ev)]
# 3. préambule maison (DIM), 3 s, puis effacement
DIM="\x1b[38;5;246m"; YEL="\x1b[38;5;220m"; R="\x1b[0m"
pre = ("\x1b[H\x1b[2J\r\n"
       f"  {YEL}⚠{R}  {DIM}Prise réelle — pas une reconstitution. Enregistrée le 20 septembre 2026{R}\r\n"
       f"     {DIM}avec asciinema dans une session tmux dédiée, telle quelle. Seules les pauses{R}\r\n"
       f"     {DIM}de plus de deux secondes sont raccourcies.  labodeludo.dev/casts/{R}\r\n")
ev = [[0.0,"o",pre]] + ev
hdr["title"] = "Un pod stateless change de nœud en 12 secondes (prise réelle)"
hdr.pop("timestamp", None)
with open(dst,"w") as f:
    f.write(json.dumps(hdr, ensure_ascii=False)+"\n")
    for e in ev: f.write(json.dumps(e, ensure_ascii=False)+"\n")
# 4. grep bloquant : rejouer dans un émulateur et lire l'ÉCRAN après chaque événement
import pyte
scr = pyte.Screen(hdr["width"], hdr["height"]); st = pyte.Stream(scr)
BAD = [__import__("os").environ.get("USER","ludorl82"),"worker","coquille","tptpt","172.16.","10.10.","labodeludo.dev/api"]
seen = {}
for e in ev:
    st.feed(e[2])
    text = "\n".join(scr.display)
    for w in BAD:
        if re.search(r"(?<![A-Za-z0-9_-])"+re.escape(w)+r"(?![A-Za-z0-9_-])", text) and w not in seen:
            seen[w] = e[0]
raw = "".join(e[2] for e in ev)
print("durée %.0f s, %d événements, %d Ko" % (ev[-1][0], len(ev), len(raw)//1024))
print("écran : " + ("PROPRE" if not seen else "FUITE " + str(seen)))
print("flux brut :", {w: raw.count(w) for w in BAD if raw.count(w)})
sys.exit(1 if seen else 0)
