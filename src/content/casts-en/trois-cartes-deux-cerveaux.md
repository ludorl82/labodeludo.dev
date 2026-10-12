---
title: "Three cards, two brains"
pubDate: 2026-09-25
description: "Two sessions around Bob's voice: the evening it moves to the 27-billion-parameter dense model, set up from a phone, then the prefix measurement that showed where a clock belongs in a cached prompt, and what the agent had misunderstood the first time."
cast: "/casts/trois-cartes-deux-cerveaux.cast"
poster: "npt:1:48"
caption: "The thread of two sessions: the voice re-reading its whole prompt, the dense model's bench, three lines at the top of the prompt, the processing slot that cannot be doubled, then the October 4 measurement and the cache warm for the wrong prompt. The agent stops twice and corrects itself three times. The recording is in French."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcripts of two sessions, on September 25 and from October 4 to 6, 2026. Ludo's prompts are quoted word for word, typos included; tool output is rewritten and shortened, the timing is compressed and names are sanitized."
article: ["trois-cartes-deux-cerveaux-une-horloge", "un-cerveau-plus-lent-pour-bob"]
---

One September evening, from a phone, a simple question: what takes time when
you talk to the house's voice assistant? Ollama's log answers that every
question re-reads its whole prompt, more than 5,000 tokens. The agent first
blames the model's hybrid architecture, "probable cause, not proven". The
dense model's bench contradicts it: the cache works, and what changes at every
question is three lines at the top of the voice prompt (the temperature, the
time to the minute, the forecast).

The weather becomes a tool, the re-read drops to about twenty tokens, and the
dense model replaces the mixture-of-experts model everywhere. Then the site's
chat is suspected of emptying the voice's cache; the proposed remedy, two
processing slots, runs into a warning in the log: this model only gets one.

Nine days later, while the articles are being written, the measurement script
shows what `prompt_eval_count` was hiding: the time at the end of the system
prompt is not enough, because a hybrid model can only resume at a checkpoint.
The agent corrects two things it had stated on September 25, then a third: the
cache was not emptying, it was warm for the wrong prompt, and the site's chat
had evicted nothing.

The short version is in
[A Slower Brain for Bob](/en/blog/un-cerveau-plus-lent-pour-bob/); the theory,
the logs and the confessions, in
[Three Cards, Two Brains and a Clock in the Wrong Place](/en/blog/trois-cartes-deux-cerveaux-une-horloge/).
The measurement itself is shown for real in
[The clock in the prompt, for real](/en/casts/l-heure-dans-le-prompt-prise-reelle/).
