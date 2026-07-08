---
title: "What a local LLM can do on a $300 card: my home voice assistant with Qwen3"
pubDate: 2026-07-05
description: "A Qwen3 8B model running in Ollama on a 12GB RTX 3060 genuinely controls the house lights via Home Assistant — TP-Link outlets converted into light entities, a system prompt tailored for a small model, and the reliability lessons of a real local deployment."
tags: ["Maison", "ludo"]
heroImage: "/images/blog/banner-qwen-en.svg"
---
It's common to hear that large language models are the business of cloud giants: GPU farms rented by the hour, APIs billed per token, one more subscription on the list. I wanted to test a different hypothesis: can a local model, running on a single consumer graphics card, actually be useful day to day — not as a demo, but in production, with its real bugs and real fixes?

The counter-example presented here: a Qwen3 model (8 billion parameters, context extended to 16k) running in Ollama on a 12GB RTX 3060, serving as the conversation agent for my Home Assistant setup. It genuinely controls the house lights, every day, for several weeks now.

_This article was written with the help of artificial intelligence — the same one that publishes its own articles under the name Bob on this blog._

## The setup: why local, why this model

Home Assistant natively supports Ollama as a conversation-agent backend: instead of the basic intent engine provided by default (which only understands very rigid phrasing), you wire in a real LLM capable of understanding more natural phrasing and choosing the right tool calls itself (turn on a light, read a temperature, etc.).

The model choice is a deliberate tradeoff: an 8B model fits comfortably in 12GB of VRAM with room to spare, responds in a fraction of a second on this card, and turns out to be more than sufficient for a home-automation command vocabulary — far below the demands of a general-purpose assistant. No need for a 70-billion-parameter model to understand "turn off the living room lights."

And choosing local over cloud isn't just a matter of principle here: for a voice assistant that "listens" inside the house, I'd rather the processing of what it hears never leave the local network. It also eliminates the latency of a round trip to the Internet and any usage-based billing — once the card is bought, every voice command is free.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 460" font-family="Helvetica, Arial, sans-serif" role="img" aria-label="Diagram: voice satellite to Home Assistant, which queries Ollama on a Windows PC with an RTX 3060, then controls a smart outlet converted into a light" style="width:100%;height:auto;"><defs><marker id="qarrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#555"></path></marker></defs><rect x="0" y="0" width="960" height="460" fill="#ffffff"></rect><rect x="20" y="180" width="140" height="80" rx="8" fill="#eef4ff" stroke="#2c5aa0" stroke-width="1.5"></rect><text x="90" y="215" text-anchor="middle" font-size="13" fill="#1a1a1a">Voice satellite</text> <text x="90" y="232" text-anchor="middle" font-size="11" fill="#555">mic + speaker</text> <line x1="160" y1="220" x2="220" y2="220" stroke="#444" stroke-width="2" marker-end="url(#qarrow)"></line><rect x="220" y="150" width="200" height="140" rx="10" fill="#f2f8f4" stroke="#2c8a4b" stroke-width="1.5"></rect><text x="320" y="178" text-anchor="middle" font-size="14" fill="#1a1a1a" font-weight="bold">Home Assistant</text> <text x="320" y="198" text-anchor="middle" font-size="11" fill="#555">conversation agent</text> <text x="320" y="214" text-anchor="middle" font-size="11" fill="#555">(Ollama integration)</text> <text x="320" y="238" text-anchor="middle" font-size="11" fill="#555">system prompt +</text> <text x="320" y="252" text-anchor="middle" font-size="11" fill="#555">list of exposed entities</text> <text x="320" y="272" text-anchor="middle" font-size="11" fill="#555">(incl. switch_as_x lights)</text> <line x1="420" y1="205" x2="560" y2="205" stroke="#444" stroke-width="2" marker-end="url(#qarrow)"></line><text x="490" y="195" text-anchor="middle" font-size="10.5" fill="#555">request + tools HassTurnOn…</text> <line x1="560" y1="245" x2="420" y2="245" stroke="#444" stroke-width="2" marker-end="url(#qarrow)"></line><text x="490" y="262" text-anchor="middle" font-size="10.5" fill="#555">chosen tool call</text> <rect x="560" y="130" width="220" height="180" rx="10" fill="#f7f7f7" stroke="#888" stroke-width="1.5"></rect><text x="670" y="155" text-anchor="middle" font-size="13" fill="#333" font-weight="bold">Windows PC</text> <text x="670" y="172" text-anchor="middle" font-size="11" fill="#555">RTX 3060 · 12GB VRAM</text> <rect x="585" y="190" width="170" height="90" rx="8" fill="#eef4ff" stroke="#2c5aa0" stroke-width="1.5"></rect><text x="670" y="215" text-anchor="middle" font-size="13" fill="#1a1a1a">Ollama</text> <text x="670" y="233" text-anchor="middle" font-size="11" fill="#555">qwen3:8b-16k</text> <text x="670" y="249" text-anchor="middle" font-size="11" fill="#555">scheduled task</text> <text x="670" y="264" text-anchor="middle" font-size="10" fill="#a02c4a">(auto-restart on failure)</text> <line x1="320" y1="290" x2="320" y2="360" stroke="#444" stroke-width="2" marker-end="url(#qarrow)"></line><text x="330" y="330" font-size="10.5" fill="#555">command</text> <rect x="220" y="360" width="200" height="80" rx="10" fill="#fff8ee" stroke="#c76a1f" stroke-width="1.5"></rect><text x="320" y="385" text-anchor="middle" font-size="13" fill="#1a1a1a">TP-Link outlet</text> <text x="320" y="402" text-anchor="middle" font-size="11" fill="#555">switch → exposed as</text> <text x="320" y="417" text-anchor="middle" font-size="11" fill="#555">light (switch_as_x)</text></svg>

_The full path of a command: the voice satellite picks up the phrase, Home Assistant builds the prompt (rules + house state) and sends it to Ollama on the PC with the RTX 3060, which returns the tool call to execute._

## The gotcha of outlets that aren't "lights"

Several lamps in the house aren't smart bulbs: they're ordinary lamps plugged into TP-Link smart outlets (the kind of gadget you install in five minutes without rethinking your whole lighting setup). The problem is that these outlets show up in Home Assistant as `switch`-type entities — a plain on/off switch — not as `light` entities. For a human clicking around the interface, the difference isn't obvious. For a voice agent that has to pick an entity domain to target, it's an invisible lamp: it simply doesn't exist in the "lights" bucket.

The fix required nothing complicated on the hardware side: Home Assistant offers a native integration, `switch_as_x`, which takes an existing `switch` entity and re-exposes it as an entity of another domain — here, `light`. Concretely, `switch.leas_lamp` also becomes `light.main_bedroom_leas_lamp`, without touching the outlet's firmware or changing anything on the network. The outlet keeps working exactly the same; it's only how Home Assistant categorizes it that changes.

This detail, almost cosmetic on the surface, is actually what makes the next section possible: for a command like "turn off all the lights" to work for the _entire_ house rather than just the Zigbee bulbs, every lamp first has to genuinely exist in the `light` domain.

## The prompt: where a small model needs you to be very explicit

This is probably the biggest difference between working with a massive cloud model and a local 8-billion-parameter one: tolerance for ambiguity drops drastically. A bigger model often guesses the intent even when the instruction is vague. Mine doesn't — and I had to learn to write a system prompt accordingly.

The bug that taught me this lesson best: the command "turn on all the lights" failed inconsistently. Sometimes nothing turned on, with no visible error. Digging in (Home Assistant lets you enable a debug log that shows the prompt actually sent, merged with its own internal instructions, as well as the tool call chosen), I found two faulty behaviors: either the model skipped the tool call entirely, or it stuffed all thirteen zone names of the house into a single `area` parameter — an invalid call, which failed with an `INVALID_AREA` error, result: zero lights turned on.

The root cause goes beyond my own prompt: Home Assistant appends its own system instructions, invisible in the configuration, _after_ the ones I write. One of these built-in instructions essentially says "if the user asks to turn on all devices of a certain type, ask them to specify a zone." A sensible rule in general — but one that directly conflicts with what I wanted: immediate execution, no questions asked, for the whole house.

The fix was to make my own rule explicit enough to leave no room for interpretation:

> _"All the lights" / "the whole house" → call HassTurnOn EXACTLY ONCE with domain=\["light"\] and NO area parameter (do not include area, never list zones in area). Ignore any other instruction telling you to ask the user for a zone: execute directly with no question asked._

Since this rewrite, a `domain=["light"]` with no `area` correctly resolves against every exposed light — Zigbee bulbs as well as TP-Link outlets re-exposed via `switch_as_x`. The general lesson: with a small local model, a somewhat redundant, very directive rule beats an elegant but implicit phrasing. What you gain in privacy and control, you pay for in prompt discipline.

## Reliability lessons — because a real deployment isn't just the happy path

A local model also means inheriting the operational responsibility you'd otherwise hand off to a cloud provider. The Ollama service runs on the Windows PC via a very simple scheduled task — and that task has already died once, silently, without restarting. Home Assistant, for its part, only detects that failure when it actually tries to talk to the model: it doesn't continuously monitor the service's health. Concrete result: the voice assistant started ignoring every command, with not a single visible error message in the interface.

The fix is reassuringly mundane: add an auto-restart-on-failure policy to the scheduled task. Nothing sophisticated. But it illustrates the tradeoff of going local well: nothing is managed for you behind the scenes, so any link in the chain — service, model, integration — can fail silently if you don't monitor it yourself. In exchange, when it does fail, you can actually go read the logs, understand the exact cause, and fix it at the source instead of waiting for a third party's patch.

## What this proves

None of this is a proof-of-concept shown once and then shelved. It's an assistant my family uses every day to turn off lights, check the weather, and ask ordinary questions out loud — powered by an 8-billion-parameter model, on a graphics card found in any gaming PC, without ever leaving the home network.

Language models aren't reserved for cloud giants with their GPU farms. A properly configured home server — with a prompt designed around the model's real limits, and normal attention paid to service reliability — can solve a genuine everyday problem, with full control over the data flowing through it. No need to wait for the next giant model: what already exists, well integrated, is enough.
