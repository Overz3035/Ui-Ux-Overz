---
name: uiux-engine
description: UIUX ENGINE is bound to THIS project (vendored via uiux-overz). Use for every UI/UX task in this repo - design work, components, pages, motion, review. Reads .uiux/design-dna.md as the visual law and routes the vendored methodology skills.
---

# UIUX ENGINE (project binding — vendored)

Installed via `npx uiux-overz init`. All methodology skills below are vendored
locally in `.agents/skills/` — no engine CLI, no network, no GitHub needed.

## Non-negotiables

1. `.uiux/design-dna.md` in this project is the visual LAW. On the first
   design task, create it (direction, palette tokens, typography pairing,
   spacing/density, motion ladder, accessibility contract, things-to-avoid).
   Never overwrite it once approved — user requirements outrank it.
2. Methodology skills (local, load at most 3 per task):

   | Phase | Skill |
   |---|---|
   | Animation craft: curve/duration choice, strict review | `animate`, `review-animations`, `emil-design-eng` |
   | Motion implementation ("make X feel physical") | `cast` — detects stack, loads gsap/framer-motion/r3f/animejs |
   | From-scratch visual universe | `paint` — feed the DNA in, skip its brainstorm |
   | Visual direction, avoiding generic AI look | `design-taste-frontend` |
   | Implementation architecture, responsive build | `frontend-design` |
   | Motion spec, easing, micro-interactions | `motion-design` |
   | Production web guidelines, a11y, performance | `web-design-guidelines` |
   | UI library choice (toast, dropdown...) | `pick-ui-library` |

3. Project media lives in `INBOX-OverzStyleUIUX/images/` and `videos/`.
   Never read media binaries into context; reference by filename only.

## Definition of done (UI tasks)

- tokens from the DNA only (alias existing project tokens, never fork values)
- focus-visible + hover + active + disabled + reduced-motion on every
  interactive element; touch targets >= 44px
- responsive by adaptation (320/768/1024/1440), not desktop shrinkage
- zero `design-audit` Critical findings
