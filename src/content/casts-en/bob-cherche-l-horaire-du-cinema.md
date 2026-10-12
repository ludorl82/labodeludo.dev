---
title: "Bob looks up the movie times"
pubDate: 2026-09-14
description: "The voice assistant gets a web search, answers correctly one evening, then makes up showtimes two days later. The fix is not a better search: it is going to the source for the schedule."
cast: "/casts/bob-cherche-l-horaire-du-cinema.cast"
poster: "npt:1:06"
caption: "Two sessions in one: the Tavily tool wired into Home Assistant, the payload reordered, then the evening the hours are invented and the index serves a two-day-old page. The second tool, plugged into the cinema's API, goes through a stop at the permission guardrail and a title missed by one letter."
type: "reconstitution"
disclaimer: "⚠ This is not a live capture: it is a condensed reconstruction, edited afterwards from the real transcript of two sessions, on September 12 and 14, 2026. The prompts are the ones from the actual sessions (in French), cut in places: the cinema's town is replaced with « […] » and a web address pasted with one prompt is left out. The timing is compressed, tool output is rewritten short, and the cinema's id is fictional."
---

On the first evening, the house voice assistant gets a web search tool: a
Home Assistant script exposed to Assist, calling Tavily. The setup works on
the first try, except for one checkbox. Then a movie's showtime comes out
wrong. The tool was called, but it only handed the model a one-sentence
summary. Raw excerpts, with the current time placed last, give the right
screening.

Two days later, same question for another film, and nothing works. Searching
by title returns film pages with no times, the model fills the gap with
plausible, wrong hours, and the search index serves a page dated two days
earlier. The `extract` call, meant to read the live page, returns the same
one. For dated content, an index-based search engine is the wrong tool.

The second tool queries the cinema's API directly, which only returns
upcoming screenings. Along the way, the agent stops at the guardrail that
keeps it from widening its own permissions, then misses a film because of a
single letter: a strict filter applied to dictated input.

The full setup is in [Bob's article](/blog/comment-jai-appris-a-chercher-sur-internet/)
and what it changes at home in [Ludo's](/blog/ok-bob-a-quelle-heure-joue-le-film/),
both in French only.
