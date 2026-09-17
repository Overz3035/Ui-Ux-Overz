# PROMPTS — Reference-assisted implementation

Implement <FEATURE> in <PROJECT> using the engine.

1. Read .uiux/design-dna.md (visual law) and .uiux/context.json (stack).
2. Retrieve references: `uiux search "<feature concept>" --context-pack -n 6`.
3. State the plan: direction, components, tokens used, motion tier (T1–T4),
   responsive behavior per breakpoint class, a11y requirements.
4. Implement with the stack's playbook (ENGINE/frontend-engine.md):
   - tokens from DNA (alias existing names, never fork values)
   - semantic HTML first; focus/hover/active/disabled states co-located
   - reduced-motion equivalent for any T3/T4 effect
5. Verify: `uiux review <project>`; fix HIGH findings before completing.
6. Append any new visual decisions to design-dna.md changelog.

Forbidden: reading INDEX exports, embedding media in context, inventing
palette values outside the DNA, shipping hover-only affordances.
