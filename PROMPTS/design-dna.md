# PROMPTS — Design DNA generation

Generate the Design DNA for a project.

Inputs (ask only for what is missing; never invent a brand):
- name, product_type, industry, audience
- brand constraints (or none)
- dark_mode preference, motion_appetite (low|medium|high)
- data_heavy (bool), accessibility_first (bool, default true)

Procedure:
1. If a project is attached and lacks .uiux/, run `uiux init <project>`.
2. Else run `uiux design --answers '<json>' --out <path>`.
3. Read the result. Present: direction name + one-line rationale, palette
   table, typography, spacing/density, motion ladder, accessibility
   contract, things-to-avoid.
4. Note rejected alternatives (one line) — the full scoring stays internal.

Constraints:
- Principles from references/knowledge; decisions from the DNA.
- If the user's explicit requirements conflict with the generated direction,
  the user wins (priority 1) and the DNA is regenerated with updated answers.
