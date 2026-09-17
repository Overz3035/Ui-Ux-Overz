# WORKFLOW — Design Session

A guided session for producing a unique design with the engine.

## Inputs to gather (from the user, not guessed)

1. Product & industry; audience specifics (expertise, devices, context).
2. Brand constraints (palette, type, voice) — or absence of a brand.
3. Motion appetite and any accessibility mandates.
4. Data density expectations (task surface vs narrative surface).

## Steps

1. **Attach or generate DNA**
   - Existing project: `uiux init <project>`.
   - Greenfield: `uiux design --answers '<json>' --out <project>\.uiux\design-dna.md`.
2. **Reference pull (one pack per concept)**
   - `uiux search "<core concept>" --context-pack`
   - optionally one more pack for the motion vocabulary.
3. **Internal direction evaluation (complex projects)**
   - The DNA generator scores directions internally; the DNA records the
     chosen direction + rejected alternatives. Do not re-litigate in the open.
4. **Design the system, not the page**
   - tokens → primitives → sections → pages (ENGINE/frontend-engine.md).
   - Every visual decision cites a DNA axis; anything new gets appended to
     the DNA changelog.
5. **Anti-generic check**
   - Apply `KNOWLEDGE/principles/taste-and-visual-quality.md` §6.
6. **Verify**
   - `uiux review <project>` → fix P0s → manual checklist for taste/UX.
