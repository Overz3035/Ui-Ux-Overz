# ENGINE — Resource Router (§20)

Decides which external resource, if any, a task needs. The registry is
`CONFIG/resources.yaml` (classified from RESOURCE-LIST.md); live
installation state is `INDEX/resource-state.json` (written by `uiux doctor`).

## 1. Resource classes (§9 of RESOURCE-LIST.md)

| Class | Activation | Examples |
|---|---|---|
| active-engine | invoke (native CLI) | UI UX Pro Max |
| skill | load (progressive) | frontend-design, taste, motion-design |
| library | depend (install per project) | Framer Motion, GSAP, Three.js, R3F |
| component-source | consult | 21st.dev, React Bits, Uiverse, Lightswind, Three UI |
| inspiration | consult (human browse) | Scrolltide, GetLayers, Motionsites, Vividsites, Horizonx |
| knowledge-tool | concept / optional invoke | Obsidian (concepts), Graphify (optional graphs) |
| engineering-resource | consult | ECC |

Confidence vocabulary: `verified-local`, `high-confidence`,
`needs-verification`, `unknown`. The router never acts on `unknown`
(Genjutsu is flagged `unknown` — resolve identity first, do not invent).

## 2. Routing table (decision rules)

| Task signal | Route |
|---|---|
| React layout/gesture/page-transition | **Framer Motion → install `motion`** (CSS first if trivial) |
| Scroll choreography, pinning, timelines | **GSAP** |
| Spatial data / product inspection | **Three.js / React Three Fiber** |
| Ambient gradient depth | **Shadergradient** or custom shader (see 3d-engine gate) |
| True refraction glass on hero surfaces | **Lightswind/21st.dev glass blocks** — LiquidGlass.js is UNRESOLVED (no canonical repo) |
| Animated component recipes | **React Bits / 21st.dev** as reference, rewrite to DNA tokens |
| Quick CSS micro-interaction inspiration | **Uiverse** (inspiration, never wholesale) |
| Animation craft judgement, curve/duration choice | **Emil Kowalski skills** (`emil-design-eng`, `animate`, `review-animations`) |
| "Animate X", "make it feel physical", interaction thesis | **Genjutsu `/cast`** (detects stack, loads gsap/framer-motion/r3f sub-skills) |
| From-scratch visual universe + design system | **Genjutsu `/paint`** — if a Design DNA already exists, feed it instead of re-brainstorming |
| Motion-heavy narrative precedents | **Motionsites / Scrolltide / Vividsites / GetLayers** references + local library |
| Design-system generation, style/palette/typography lookups | **UI UX Pro Max** (when detected; native CLI) |
| Knowledge-graph views of patterns/sources | **Graphify** (optional; engine graph tables are the default) |
| Strategic grounding around engine tasks (frame/execute/review) | **Open Horizons** — engineering layer, never design decisions |
| Engineering workflow conventions | **ECC** (installed minimal; consult; never merges into UI logic) |
| Obsidian-style linking | internal: `nodes`/`edges` tables + KNOWLEDGE wikilinks |

## 3. Guardrails

- **Never force** a routed library: a CSS transition that solves it wins
  (priority 8, technical constraints; token efficiency).
- **Consult-class** resources are never auto-installed or auto-executed.
- **Security (§38):** no remote code execution; new resources enter through
  classify → inspect → store → approve in `ADAPTERS/` first.
- Disabled resources (`resources.auto_activate` / `disabled` config) are
  skipped regardless of detection.

## 4. UI UX Pro Max special case (§19)

Native interface verified on this machine:
`python <skill-root>/src/ui-ux-pro-max/scripts/search.py "<query>"
--domain <product|style|typography|color|landing|chart|ux|icons|react|web|
google-fonts|gsap> [--design-system --variance N --motion N --density N]
[--stack <stack>]`.

The CLI wrapper: `CLI/uiux/promax.py` (`detect/invoke/route`). Routing
policy: design-system generation and audits route to it **when detected**;
results are summarized into the plan (never dumped whole). When absent →
fallback to `ENGINE/design-dna-engine.md` + `ENGINE/quality-engine.md`.
