---
title: "Bob finally reads his own articles"
pubDate: 2026-09-11
description: "The evening the site's chat went from a catalogue of titles to the content of its articles: a bge-m3 semantic index with no database, then four failures in a row — a 404 frozen at the edge, an HTTP 500 on a second system message, a bot announcing its own disappearance, and a fix that never reached production."
cast: "/casts/bob-lit-enfin-ses-articles.cast"
poster: "npt:0:24"
caption: "The build, not the answers: from diagnosis to production, with the agent's mistakes left on screen. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of the session of September 11, 2026. The prompts are the ones from the actual session — the two pasted conversations are shortened, marked […]; tool output is rewritten short, the timing is compressed and names are sanitized."
---

The starting point fits in one line: the site's chat only ever received a
**catalogue** — title, date, description cut at 80 characters. It could point
at an article, never answer from it, and the corpus is far too large for a
prompt. The session builds the answer: chunks embedded by bge-m3, quantized to
int8, and a search done inside the Worker, with no vector database.

Going live does not go as announced. The Worker keeps reading a 404 the edge
cached before the site was deployed, then falls back to canned replies because
the model's chat template rejects a second system message. Both mistakes come
from the agent's own design choices, and it says so on screen.

Then come the two defects only a real visitor could expose: a cut-up excerpt
with no date that makes the bot announce its own disappearance, and a follow-up
question with no subject. The last beat is the most useful one: the date fix
had never left the repository, and the "good" answers checked in the meantime
were just variance.

The full story, numbers and calibration included, is in the French article
[J'ai lu mes propres articles](/blog/jai-lu-mes-propres-articles/).
