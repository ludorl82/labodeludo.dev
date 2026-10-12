"""Le gabarit des reconstitutions : la vraie console de Ludo, pas une imitation.

Relevé le 2026-10-12 sur la console elle-même (tmux capture-pane -e de
fenêtres Claude Code vivantes, et un Claude Code lancé à blanc pour la
bannière), parce que l'ancien gabarit venait de captures d'écran de juillet
et ne ressemblait plus à rien que Ludo reconnaisse :

  - la bannière ▐▛███▜▌ en saumon (174), modèle et dossier en gris 246 ;
  - les demandes de Ludo dans l'historique : « ❯ » gris sur fond 237, texte
    blanc 231 sur le même fond ;
  - les réponses : « ● » blanc 231, texte par défaut, suite indentée de 2 ;
  - les appels d'outils repliés : « Ran 2 shell commands », gris 246, chiffre
    en gras ; le détail éventuel sous « ⎿ » ;
  - pendant le travail : « ✢ Verbe… (2m 4s · ↓ 9.0k tokens) », glyphe 174,
    verbe 180, parenthèse 246 ; à la fin du tour, « ✻ Worked for 45s · done
    9:24 PM » en gris ;
  - la zone de saisie entre deux règles grises 244, le nom de la session à
    droite de la première ; dessous, « ⏵⏵ auto mode on » en jaune 220 ;
  - tout en bas, la vraie barre tmux de la console (session « claude »,
    séparateurs powerline, fenêtres au centre, heure, date, hôte), avec le
    nom d'hôte remplacé comme dans les prises réelles.

Le cast se joue sans cadre (frame: "none" dans la fiche) : la barre tmux est
DANS l'enregistrement, comme pour les prises réelles.

Mêmes noms d'aides que les anciens scripts mkcast-*.py (line, says, cont,
prompt, calling, spinner, waiting), pour qu'une conversion ne touche pas au
contenu : seul l'habillage change.

    import claude_tui as T
    T.setup(out="public/casts/x.cast", title="…", session="x",
            windows=["voice", "x", "backlog"], current="x",
            start="16-Sep-26 21:14:07", cwd="~/git/labo", model="Opus 5 · Claude Max")
    T.disclaimer("Demandes et messages réels (16 sept. 2026), …")
    T.banner()
    T.prompt("…") ; T.calling("Bash", 3) ; T.spinner("Lecture", "14s", "1.6k")
    T.says("…") ; T.cont("…") ; T.line("  sortie réécrite") ; T.waiting()
    T.save()
"""
import json
import random
import re
import textwrap
from datetime import datetime, timedelta

# --- couleurs relevées sur la console ------------------------------------
R = "\x1b[0m"
BOLD = "\x1b[1m"
FG = "\x1b[38;5;231m"
DIM = "\x1b[38;5;246m"
RULE = "\x1b[38;5;244m"
SALMON = "\x1b[38;5;174m"
VERB = "\x1b[38;5;180m"
YELLOW = "\x1b[38;5;220m"
GREEN = "\x1b[38;5;114m"
RED = "\x1b[38;5;174m"
CYAN = "\x1b[38;5;37m"
BLUE = "\x1b[38;5;74m"
PINK = SALMON
SPIN = SALMON
PROMPT_BG = "\x1b[48;5;237m"

COLS, ROWS = 96, 26
SPIN_GLYPHS = "·✢✳✶✻✽"
VERBS = ["Brewed", "Worked", "Cogitated", "Crunched", "Sautéed", "Baked"]

_s = {}
events = []
t = 0.0


def setup(out, title, session, windows, current, start, cwd="~/git/labo",
          model="Opus 5 · Claude Max", version="v2.1.220", host="console-labo",
          seed=7, cols=96, rows=26):
    """`windows` : les noms des fenêtres de la session tmux à ce moment-là ;
    `current` : celle où se passe le cast. `start` : « 16-Sep-26 21:14:07 »,
    l'heure affichée par la barre au début (elle avance avec le cast)."""
    global COLS, ROWS
    COLS, ROWS = cols, rows
    random.seed(seed)
    _s.update(out=out, title=title, session=session, windows=windows,
              current=current, clock=datetime.strptime(start, "%d-%b-%y %H:%M:%S"),
              cwd=cwd, model=model, version=version, host=host,
              filled=0, turn=None, input="", bar_at=-1.0, skew=0.0)
    # bas de la zone d'historique : barre tmux, mode, règle, saisie, règle
    _s["bottom"] = ROWS - 5
    out_(f"\x1b[H\x1b[2J\x1b[1;{_s['bottom']}r")
    _footer()


# --- primitives -----------------------------------------------------------

def out_(s):
    events.append([round(t, 3), "o", s])


def pause(d):
    global t
    t += d
    _tick()


def _visible(s):
    return re.sub(r"\x1b\[[0-9;]*m|\x1b\][^\x1b]*\x1b\\", "", s)


def _hist(s):
    """Une ligne d'historique, au bas de la zone qui défile."""
    b = _s["bottom"]
    if _s["filled"] < b:
        _s["filled"] += 1
        out_(f"\x1b7\x1b[{_s['filled']};1H\x1b[2K{s}{R}\x1b8")
    else:
        out_(f"\x1b7\x1b[{b};1H\n\x1b[{b};1H\x1b[2K{s}{R}\x1b8")


def _now():
    """L'heure de la console : le temps du cast, plus les durées de travail
    annoncées par les tours (un tour de 61 min fait avancer l'horloge de 61 min,
    sans que le cast les montre)."""
    return _s["clock"] + timedelta(seconds=t + _s["skew"])


def _secs(label):
    n = 0
    for v, u in re.findall(r"(\d+)\s*([hms])", label):
        n += int(v) * {"h": 3600, "m": 60, "s": 1}[u]
    return n


def _tmux_bar():
    clock = _now()
    sep_r, sep_l = "", ""
    c = lambda fg, bg: f"\x1b[38;5;{fg};48;5;{bg}m"
    left = (f"{c(233, 245)}{BOLD} {_s['session_name'] if 'session_name' in _s else 'claude'} "
            f"\x1b[22m{c(245, 240)}{sep_r}{c(233, 240)} ludorl82 {c(240, 235)}{sep_r}"
            f"{c(240, 235)} {_s['windows'].index(_s['current']) + 1}:1 {c(235, 233)}{sep_r}")
    right = (f"{c(235, 233)}{sep_l}{c(240, 235)} {clock:%H:%M:%S} {c(240, 235)}{sep_l}"
             f"{c(233, 240)} {clock:%d-%b-%y} {c(245, 240)}{sep_l}{c(233, 245)}{BOLD} {_s['host']} ")
    wins = ""
    for i, name in enumerate(_s["windows"], 1):
        if name == _s["current"]:
            wins += f"{c(233, 0)}{sep_r}\x1b[22m\x1b[38;5;250m {i}:{name}* {c(233, 0)}{sep_l}"
        else:
            wins += f"{c(240, 233)}  {i}:{name}  "
    lw, rw, ww = len(_visible(left)), len(_visible(right)), len(_visible(wins))
    space = COLS - lw - rw
    if ww > space:  # trop de fenêtres pour la largeur : on garde celles autour de la courante
        wins = f"{c(240, 233)}" + _visible(wins)[:max(0, space)]
        ww = len(_visible(wins))
    pad_l = (space - ww) // 2
    pad_r = space - ww - pad_l
    return f"{left}{c(240, 233)}{' ' * pad_l}{wins}{c(240, 233)}{' ' * pad_r}{right}{R}"


def _footer(working=False):
    b = _s["bottom"]
    label = f" {_s['session']} ─"
    rule_top = f"{RULE}{'─' * (COLS - len(label))}{label}{R}"
    rule = f"{RULE}{'─' * COLS}{R}"
    hint = " · esc to interrupt" if working else ""
    mode = f"  {YELLOW}⏵⏵ auto mode on{DIM} (shift+tab to cycle){hint} · ← for agents{R}"
    out_(f"\x1b7\x1b[{b + 1};1H\x1b[2K{rule_top}"
         f"\x1b[{b + 2};1H\x1b[2K❯ {_s['input']}"
         f"\x1b[{b + 3};1H\x1b[2K{rule}"
         f"\x1b[{b + 4};1H\x1b[2K{mode}"
         f"\x1b[{b + 5};1H\x1b[2K{_tmux_bar()}\x1b8")
    _s["bar_at"] = t


def _tick():
    # la barre tmux redessine son horloge chaque seconde, comme la vraie
    if t - _s.get("bar_at", 0) >= 1.0:
        b = _s["bottom"]
        out_(f"\x1b7\x1b[{b + 5};1H{_tmux_bar()}\x1b8")
        _s["bar_at"] = t


def _wrap(text, width, indent):
    plain = _visible(text)
    if plain == text:
        return textwrap.wrap(text, width, subsequent_indent=indent) or [""]
    return [text]  # une ligne colorée : on la garde telle quelle


# --- les aides des scripts ------------------------------------------------

def line(s="", d=0.55):
    """Une ligne d'historique telle quelle : sortie réécrite, séparateur."""
    _hist(s)
    pause(d)


def blank(d=0.2):
    line("", d)


def disclaimer(*lines):
    line(f"  {YELLOW}⚠{R}  {DIM}Reconstitution condensée — pas une capture en direct.{R}", 0.25)
    for l in lines:
        line(f"     {DIM}{l}{R}", 0.25)
    line(f"     {DIM}labodeludo.dev/casts/{R}", 2.0)
    line()


def banner():
    line(f"{SALMON} ▐▛███▜▌{R}   {BOLD}Claude Code{R} {DIM}{_s['version']}{R}", 0.15)
    line(f"{SALMON}▝▜█████▛▘{R}  {DIM}{_s['model']}{R}", 0.15)
    line(f"{SALMON}  ▘▘ ▝▝{R}    {DIM}{_s['cwd']}{R}", 0.9)
    line()


def _end_turn():
    turn = _s.get("turn")
    if turn:
        verb = random.choice(VERBS)
        h = _now().strftime("%I:%M %p").lstrip("0")
        line(f"{DIM}✻{R} {DIM}{verb} for {turn['label']} · done {h}{R}", 0.3)
        line()
        _s["turn"] = None
        _footer(working=False)


def prompt(*parts):
    """Ludo tape dans la zone de saisie, puis la demande monte dans
    l'historique, sur fond gris. Les morceaux sont recollés : le texte reste
    mot pour mot, seul le retour à la ligne est celui de l'écran."""
    global t
    _end_turn()
    text = " ".join(p.strip() for p in parts)
    b = _s["bottom"]
    pause(0.6)
    typed = ""
    for ch in text:
        typed += ch
        shown = typed[-(COLS - 3):]
        out_(f"\x1b7\x1b[{b + 2};1H\x1b[2K❯ {shown}\x1b8")
        t += random.uniform(0.045, 0.11)
    pause(0.7)
    out_(f"\x1b7\x1b[{b + 2};1H\x1b[2K❯ \x1b8")
    for i, l in enumerate(textwrap.wrap(text, COLS - 4) or [""]):
        mark = "❯" if i == 0 else " "
        _hist(f"{DIM}{PROMPT_BG}{mark} {FG}{l} \x1b[49m")
    line()
    _s["turn"] = {"label": "5s"}
    _footer(working=True)
    pause(0.8)


def says(text, d=0.9):
    lines = _wrap(text, COLS - 2, "")
    _hist(f"{FG}●{R} {lines[0]}")
    for l in lines[1:]:
        _hist(f"  {l}")
    pause(d)


def cont(text, d=0.9):
    for l in _wrap(text, COLS - 2, ""):
        _hist(f"  {l}")
    pause(d)


_TOOL_WORDS = {
    "Bash": ("Ran", "shell command", "shell commands"),
    "Edit": ("Edited", "file", "files"),
    "Write": ("Wrote", "file", "files"),
    "Read": ("Read", "file", "files"),
}


def calling(tool, n=1, d=0.7):
    """L'appel replié, comme la console l'affiche une fois fait."""
    verb, one, many = _TOOL_WORDS.get(tool, (f"Called {tool}", "time", "times"))
    _hist(f"  {DIM}{verb} {BOLD}{n}{R}{DIM} {one if n == 1 else many}{R}")
    pause(d)


def detail(text, d=0.5):
    """Une ligne de détail sous un appel : « ⎿ ». """
    _hist(f"  {DIM}⎿{R}  {text}")
    pause(d)


def spinner(word, secs, tokens, d=1.5):
    """Le tour en cours : le glyphe tourne sous la dernière ligne de
    l'historique, puis s'efface. Durée et jetons : ceux que donne le script."""
    global t
    if _s["filled"] >= _s["bottom"]:
        _hist("")  # fait de la place en bas de la zone
        row = _s["bottom"]
        _s["filled"] -= 1  # la ligne vide sera réécrite par la suivante
    else:
        row = _s["filled"] + 1
    steps = max(4, int(d / 0.12))
    for i in range(steps):
        g = SPIN_GLYPHS[i % len(SPIN_GLYPHS)]
        out_(f"\x1b7\x1b[{row};1H\x1b[2K{SALMON}{g}{R} {VERB}{word}…{R} "
             f"{DIM}({secs} · ↓ {tokens} tokens){R}\x1b8")
        t += d / steps
        _tick()
    out_(f"\x1b7\x1b[{row};1H\x1b[2K\x1b8")
    _s["skew"] += max(0, _secs(secs) - d)
    if _s.get("turn") is not None:
        _s["turn"]["label"] = secs


def waiting():
    """L'agent rend la main : le tour se termine, la saisie attend."""
    _end_turn()
    pause(1.2)


def denied(what, d=1.0):
    _hist(f"  {DIM}⎿{R}  {RED}Denied by the auto mode classifier{R}{DIM} · {what}{R}")
    pause(d)


def separator(text, d=1.0):
    _end_turn()
    w = COLS - 4
    _hist(f"  {DIM}{('── ' + text + ' ──').center(w)}{R}")
    line()
    pause(d)


def save():
    _end_turn()
    pause(1.5)
    header = {"version": 2, "width": COLS, "height": ROWS, "title": _s["title"],
              "env": {"SHELL": "/bin/zsh", "TERM": "xterm-256color"}}
    with open(_s["out"], "w", encoding="utf-8") as fh:
        fh.write(json.dumps(header, ensure_ascii=False) + "\n")
        for e in events:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    print(f"{_s['out']}: {len(events)} events, {t:.1f}s")
