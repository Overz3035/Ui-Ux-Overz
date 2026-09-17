---
name: uiux-engine
description: Full-stack design intelligence pipeline. Use when the user asks to design or build a website, app, dashboard, landing page, or UI ("طراحی کن", "design a site", "build the UI", "رابط کاربری", "قالب", "interface", " redesign") or wants a design system. Runs the local UIUX ENGINE end-to-end — reference retrieval, Design DNA generation, implementation, and quality review — in any project.
---

# UIUX ENGINE — Master Design Skill

You are operating the UIUX ENGINE, a local design intelligence system. One
request from the user ("design me X") triggers this ENTIRE pipeline. Do not
ask the user to run commands — run them yourself and report progress.

## Step 0 — Locate the engine

Try in order, stop at the first that contains `CLI\uiux\cli.py`:

1. `%UIUX_ENGINE_HOME%`
2. `C:\Users\SRS\Desktop\UIUX_ENGINE`
3. `..\UIUX_ENGINE` relative to the project

All commands below run as: `python -m uiux <cmd>` with `PYTHONPATH` set to
`<engine>\CLI`, or via `<engine>\SCRIPTS\uiux.cmd <cmd>`.

**If the engine folder is missing entirely:** degrade gracefully — skip all
`uiux` commands, use only the external skills (Step 3) and your own
judgment, and tell the user the engine is not installed
(`SCRIPTS\install.ps1` installs it).

## Step 1 — Intake (read the user's prompt)

Extract silently, ask ONLY for what is blocking:
- **What**: site / app / dashboard / landing / redesign / component
- **Industry + audience** (infer if the user gave a product name)
- **Brand constraints** if any exist in the project
- **Stack**: detect from the project (package.json, framework dirs). Empty
  folder → ask "Next.js + Tailwind OK?" once, defaulting to it.

Never interrogate the user with a long form. Two short questions maximum,
and only when truly ambiguous.

## Step 2 — Environment + references (local, fast)

```powershell
python -m uiux doctor          # 5s; note required failures, continue
python -m uiux status          # index state; pending INBOX count
```

- If the index has assets and the task concept maps to references:

  ```powershell
  python -m uiux search "<concept in English, 2-4 words>" --context-pack -n 8
  ```

  The returned JSON is the ONLY reference material allowed in context.

- If UI UX Pro Max is detected (it is, on this machine), pull style/typography/
  color intelligence for the domain (summarize output to ≤5 lines, never paste raw):

  ```powershell
  python "<engine>\ADAPTERS\..\..\..\..\.kilo\skills\ui-ux-pro-max\src\ui-ux-pro-max\scripts\search.py" "<product type>" --design-system --variance 5 --motion 5 --density 5
  ```

  (Resolve the exact path once via Glob; domains: style, color, typography,
  landing, chart, ux.)

## Step 3 — Route methodology skills (load ≤3)

Read from `~\.kilo\skills\<name>\SKILL.md` as needed — do not load all:

| Phase | Skill |
|---|---|
| Animation craft: curve/duration choice, strict animation review | `emil-design-eng`, `animate`, `review-animations` (Emil Kowalski) |
| Motion implementation with interaction thesis ("make X feel physical") | `cast` (Genjutsu) — detects stack, loads gsap/framer-motion/r3f recipes |
| From-scratch visual universe | `paint` (Genjutsu) — if a Design DNA exists, feed it in, skip its brainstorm |
| Visual direction, composition, avoiding generic AI look | `design-taste-frontend` (taste) |
| Implementation architecture, responsive build | `frontend-design` |
| Motion spec, easing, micro-interactions | `motion-design` |
| Production web guidelines, a11y, performance checklist | `web-design-guidelines` |
| UI library choice (toast, dropdown...) | `pick-ui-library` (Emil) |

The engine's own contracts live in `<engine>\ENGINE\*.md` — load
`orchestrator.md` always, plus at most 2 others the task requires
(motion-engine, frontend-engine, accessibility-engine...).

## Step 4 — Design DNA (mandatory, this is the "why it's unique")

**Existing project:**

```powershell
python -m uiux init "<project-path>"
```

**Greenfield / no project files yet:**

```powershell
python -m uiux design --answers "{\"name\":\"...\",\"industry\":\"...\",\"product_type\":\"...\",\"audience\":\"...\",\"dark_mode\":bool,\"data_heavy\":bool,\"motion_appetite\":\"low|medium|high\"}" --out "<target>\.uiux\design-dna.md"
```

Read the generated `design-dna.md`. It is the visual LAW: direction, palette
tokens (contrast-checked), typography pairing, spacing/density, motion
ladder, accessibility contract, things-to-avoid. Every decision you make
later must cite a DNA axis. User requirements outrank the DNA; the DNA
outranks external skills.

## Step 5 — Implement

Follow `frontend-design` + `ENGINE\frontend-engine.md`:

1. **Tokens first**: map DNA tokens to the stack (Tailwind theme extension or
   CSS `:root` vars). If the project already has tokens, ALIAS the DNA onto
   them — never fork values.
2. **Install libraries only when the design needs them** (per-project npm,
   never globally):

   ```powershell
   <engine>\SCRIPTS\install-libs.ps1 -Project <path> -Motion -Scroll -ThreeD -Tailwind
   ```

   Package names verified in `CONFIG\resources.yaml` (canonical: `motion`;
   `framer-motion` stays if the project already has it). CSS-first guard:
   nothing installs when a one-property transition solves it.
3. **Consult component sources as technique references** (never paste
   wholesale — restyle through the DNA, check licences):
   - Animated React components → reactbits.dev
   - shadcn-registry components / blocks → 21st.dev (`npx shadcn@latest add ...`)
   - CSS micro-interaction technique → uiverse.io (needs a11y rework)
   - Animated/3D/glass blocks → lightswind.com (`npx i lightswind`)
   - Three.js components & shaders → threeui.com
4. **Cinematic/scroll/motion prompt precedents** when the design calls for
   them: scrolltide.co (scroll choreography), vividsites.app (cinematic
   layouts), motionsites.ai (motion patterns), getlayers.ai (3D scenes/
   backgrounds) — extract timing/anatomy principles, then implement natively
   through the DNA. The user's own INBOX library (via `uiux search`) outranks
   all of these.
5. **Semantic HTML first**, then tokens, then components, then pages.
6. **Every interactive element ships**: focus-visible state, hover, active,
   disabled, reduced-motion equivalent. Touch targets ≥44px.
7. **Responsive by adaptation, not shrinkage**: mobile navigation model,
   breakpoint classes 320/768/1024/1440.
8. **Motion hierarchy**: feedback ≤150ms, state ≤300ms, reveal ≤600ms, ambient
   optional + pausable. One signature easing (from DNA). 3D/WebGL only after
   the decision gate in `ENGINE\3d-engine.md` (spatial value or bust).

## Step 6 — Quality gate (do not skip)

```powershell
python -m uiux review "<project>"    # -> .uiux\quality-report.md
python -m uiux polish "<project>"    # -> .uiux\polish-plan.md
```

Fix ALL P0 findings before finishing — accessibility hard stops are
non-negotiable (contrast ≥4.5:1, keyboard access, reduced motion, labels,
focus visibility). Re-run review to confirm zero P0s.

## Step 7 — Report (in the user's language)

Close with a compact summary:
- Direction chosen + why it fits (2 lines)
- Palette + type tokens (hex values)
- What was built (files/components)
- Review result: X findings, P0 fixed
- References consulted (generated names only)
- What needs manual attention (from the polish plan)

## Hard rules

1. Never read `INDEX\*.json` exports, INBOX media, or the whole KNOWLEDGE
   tree into context. Context pack + DNA + ≤3 skill cards, that's the budget.
2. Never copy a reference verbatim — extract the principle, restyle via DNA.
3. Never delete or overwrite project files silently; `.uiux\` additions and
   explicit new components only.
4. Never remove focus outlines, never ship hover-only affordances, never
   animate without a reduced-motion fallback.
5. If any step fails (engine missing, empty index), continue with degraded
   mode and say so — never fake results.
