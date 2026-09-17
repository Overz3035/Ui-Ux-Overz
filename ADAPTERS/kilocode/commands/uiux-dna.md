---
description: Generate or update the project Design DNA via UIUX ENGINE.
---
# UIUX Design DNA

Target project: $ARGUMENTS (default: current directory)

Steps:

1. If `.uiux/design-dna.md` exists in the target project: read it, treat it
   as the project's visual law, and report its direction + any conflicts
   with the current request. Do not regenerate silently.
2. If it does not exist: gather what is known about the project (industry,
   audience, product type, brand, motion appetite, data density) from the
   user request and quick repo inspection (package.json, components).
3. Run: `uiux init "<project>"` — it detects the stack and writes `.uiux/`
   context, tokens, and `design-dna.md`. It never overwrites existing files
   (a proposal lands in `design-dna.proposed.md` instead).
4. Read the generated `design-dna.md` and summarize: direction name,
   palette strategy, typography, density/motion posture, and the
   things-to-avoid list.
5. Record any conflict against `ENGINE/priority-hierarchy.md`.

Optional JSON answers (industry/audience/product_type/dark_mode/
data_heavy/motion_appetite/brand) can be supplied inline.
