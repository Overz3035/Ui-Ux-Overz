# Troubleshooting

## Doctor failures

| Symptom | Cause | Fix |
|---|---|---|
| `python` FAIL / not found | missing or PATH | install 3.10+ (`winget install Python.Python.3.12`), reopen terminal |
| pillow/numpy FAIL | packages missing | `python -m pip install Pillow numpy` |
| ffmpeg not found | optional, video off | `winget install Gyan.FFmpeg` or pin `tools.ffmpeg` in CONFIG/config.yaml |
| tesseract not found | optional, OCR off | `winget install UB-Mannheim.TesseractOCR` |
| directories FAIL | partial copy | re-copy the full engine folder (all top-level dirs) |

## Ingestion

| Symptom | Cause | Fix |
|---|---|---|
| 0 discovered | wrong INBOX layout | check INBOX/{sources,images,videos,loose} naming |
| everything cached, 0 analyzed | expected on re-run | change files or bump analyzer (VERSION analyzer=) to force |
| videos have no keyframes | ffmpeg missing | install/pin ffmpeg, `uiux update` |
| sources look wrong | stem inference | rename loose files to share a prefix, re-run update |
| hardlinks failed | cross-volume INBOX | engine falls back to copy automatically |

## Search

| Symptom | Cause | Fix |
|---|---|---|
| no matches | empty index | `uiux ingest` |
| results feel literal | lexical weight dominating | raise `search.weight_concept`, add concepts to CONFIG/concepts.yaml |
| `--context-pack` empty | all scores below cutoff | broaden query; check tags via `uiux analyze` |

## DNA / init

| Symptom | Cause | Fix |
|---|---|---|
| wrote design-dna.proposed.md | existing DNA (never-overwrite) | review + rename deliberately |
| direction feels wrong | answers incomplete | re-run with explicit industry/audience/motion answers |
| palette contrast issues | custom override | the generator nudges; if hand-editing tokens, keep ≥ 4.5:1 |

## Adapters / resources

| Symptom | Cause | Fix |
|---|---|---|
| ui-ux-pro-max shows absent | not installed here | adapter falls back internally; or install the skill into ~/.kilo/skills |
| resource shows `unknown` confidence | identity unresolved (e.g. genjutsu) | resolve canonical source, update registry, never let the router act on it |
| liquidglass-js `unresolvable` | no canonical package exists (rdev/liquid-glass is 404) | use verified alternatives: Lightswind glass blocks, 21st.dev, or CSS backdrop-filter |
| ECC not detected | minimal install state missing | `npx ecc-universal install --profile minimal --target claude` (never stack plugin + manual) |
| `npx skills add ... -g` fails | PromptScript target doesn't support global install | install locally then copy to ~/.kilo/skills + ~/.agents/skills (how the 4 design skills were installed) |
| library shows absent in doctor | libraries are per-project npm deps by design | run `SCRIPTS\install-libs.ps1 -Project <path> -Motion -Scroll -ThreeD` in the project |

## Resource verification status (2026-09, see CONFIG/resources.yaml `verified:` fields)

| Resource | Status |
|---|---|
| UI UX Pro Max | verified-local, native CLI works |
| frontend-design, taste, motion-design, web-design-guidelines | installed globally (skills.sh) |
| ECC | installed (minimal profile, no hooks, into ~/.claude) |
| motion.dev / `motion` package | verified; canonical npm name is `motion` |
| three.js (r185), R3F docs, Shadergradient (`@shadergradient/react`) | verified live |
| 21st.dev, reactbits.dev, lightswind.com, scrolltide.co, getlayers.ai, motionsites.ai, vividsites.app, threeui.com | verified live (details in registry) |
| uiverse.io | domain live (bot-blocked to automated fetch) |
| LiquidGlass.js | UNRESOLVED — no canonical repo exists; use Lightswind/21st.dev instead |
| Genjutsu, Horizonx, Emily/Emil Kowalski, Graphiphy* | UNRESOLVED — router refuses to act on them until the requester identifies the source |

\* A `graphify` skill exists locally and is treated as an optional
knowledge-graph backend; whether it is the intended "Graphiphy" is
unconfirmed.

## Windows quirks

- PowerShell execution policy: run installers with
  `-ExecutionPolicy Bypass`.
- Emoji/UTF-8 in output: the CLI reconfigures stdout to UTF-8; legacy
  consoles may still garble a few glyphs — harmless.
- Long paths: keep the engine folder shallow (< 200 chars).
