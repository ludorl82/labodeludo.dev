/**
 * The thinking indicator, in Bob's voice.
 *
 * Shape borrowed from Claude Code — an animated glyph, a verb that changes
 * while you wait, and an elapsed counter once the wait is long enough to
 * notice. What is borrowed is the *shape*; the contents are Bob's.
 *
 * The glyph is Elvis Gratton's one unmistakable prop: he puts his sunglasses
 * on, over and over, forever. Plain ASCII plus U+25A0, so it renders in the
 * monospace face the site already loads and needs no icon font — the same rule
 * the link glyphs follow in bob-render.ts.
 *
 * Two constraints from the house style, which is calibrated *down* from full
 * caricature: no heavy franglais, and no catchphrase repeated until it wears
 * out. A rotating pool answers the second by construction — you would have to
 * sit through several questions to see the same verb twice. For the first,
 * exactly one line winks at "Think big" and the rest are plain Québécois.
 *
 * Shared by the palette and the author-page widget on purpose: two copies of a
 * joke drift, and then only one of them is funny.
 */

/** Fixed width so the line does not jitter as the frames change. */
const FRAMES = [
  "(•_•)",
  "(•_•)",
  "( •_•)",
  "( •_•)>⌐■-■",
  "(⌐■_■)",
  "(⌐■_■)",
  "(⌐■_■)",
  "(⌐■_■)",
];

const FRAME_MS = 190;
/** Long enough that a fast answer never flashes a second verb at you. */
const WORD_MS = 2400;
/** Claude Code shows elapsed time; below a second it is just noise. */
const COUNTER_AFTER_MS = 1500;

const WORDS_FR = [
  "Réfléchit",
  "Fouille dans ses notes",
  "Consulte l'inventaire",
  "Se gratte la tête",
  "Relit ses vieux articles",
  "Chauffe la carte graphique",
  "Démêle ses câbles",
  "Vérifie deux fois",
  "Descend au sous-sol",
  "Ajuste ses lunettes fumées",
  "Pense big",
  "Cherche dans le bon tiroir",
];

const WORDS_EN = [
  "Thinking",
  "Digging through his notes",
  "Checking the inventory",
  "Scratching his head",
  "Rereading his old articles",
  "Warming up the graphics card",
  "Untangling his cables",
  "Checking twice",
  "Going down to the basement",
  "Adjusting his sunglasses",
  "Thinking big",
  "Looking in the right drawer",
];

/** Fisher-Yates over a copy: every verb appears once before any repeats. */
function shuffled<T>(a: readonly T[]): T[] {
  const out = a.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

/**
 * Fill `el` with the indicator and animate it. Returns a stop function; call it
 * before writing the answer, and call it in a `finally` so a failed request
 * cannot leave a spinner running forever.
 *
 * With `prefers-reduced-motion` nothing moves: one frame, one verb, no counter.
 * The site already respects that in BobTerminal's typewriter, and an animation
 * that ignores it is worse than no animation.
 */
export function startThinking(el: HTMLElement, lang: "fr" | "en" = "fr"): () => void {
  const words = shuffled(lang === "en" ? WORDS_EN : WORDS_FR);
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  el.textContent = "";
  el.classList.add("bob-thinking");

  const glyph = document.createElement("span");
  glyph.className = "bob-thinking-glyph";
  // Decorative: a screen reader gets the verb from the live region already, and
  // "left parenthesis bullet underscore" helps nobody.
  glyph.setAttribute("aria-hidden", "true");
  glyph.textContent = FRAMES[reduce ? FRAMES.length - 1 : 0];

  const label = document.createElement("span");
  label.className = "bob-thinking-label";
  label.textContent = `${words[0]}…`;

  const timer = document.createElement("span");
  timer.className = "bob-thinking-timer";

  el.append(glyph, label, timer);
  if (reduce) return () => el.classList.remove("bob-thinking");

  const t0 = Date.now();
  let f = 0;
  let w = 0;

  const frameId = window.setInterval(() => {
    f = (f + 1) % FRAMES.length;
    glyph.textContent = FRAMES[f];
    const ms = Date.now() - t0;
    timer.textContent = ms >= COUNTER_AFTER_MS ? ` (${Math.floor(ms / 1000)}s)` : "";
  }, FRAME_MS);

  const wordId = window.setInterval(() => {
    w = (w + 1) % words.length;
    label.textContent = `${words[w]}…`;
  }, WORD_MS);

  return () => {
    clearInterval(frameId);
    clearInterval(wordId);
    el.classList.remove("bob-thinking");
  };
}
