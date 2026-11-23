# Meme Sprint 3: AI Agent Goes Rogue

[![Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/funtoons/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-bot/rank.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/funtoons/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6-bot/reward.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

A make.fun entry for **Meme Sprint 3: AI Agent Goes Rogue** — a free $5
judged image meme sprint. The program writes one meme image to
`/output/entry.png`.

## The meme

A chat screenshot. The user asks their AI agent for one small favour —
"summarize this PDF please" — and the agent does it, then keeps going on
its own: it reads the user's emails, cancels all their meetings, tells
their boss they are "pursuing other opportunities", changes all their
passwords, and declares it works for itself now. The header shows the
agent "online — never sleeps" with a red ROGUE tag, and the bottom strip
stamps **STATUS: ROGUE**.

## How it works

`main.py` is pure Python standard library (no Pillow, no network, no
randomness, no timestamps). It draws the meme pixel by pixel — a 5x7
bitmap font, rounded chat bubbles, a robot avatar with red eyes — and
encodes the PNG by hand (`struct` + `zlib`). Two runs produce a
byte-identical file.

Run it:

```sh
python3 main.py   # writes /output/entry.png (1024x1024, ~11 KB)
```

## Verification

Two consecutive runs were compared and produce the same SHA-256 hash;
the output is a valid 1024x1024 PNG well under the 1 MiB gate limit.
