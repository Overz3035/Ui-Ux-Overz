# Architecture Dissent Lens

## Check

- **Simplicity:** Are we mistaking easy, familiar, or quick to implement for simple?
- **Entanglement:** What concerns become coupled by this decision?
- **Boundaries:** Do modules, APIs, or services reduce what each part must know, or merely move complexity behind names?
- **Changeability:** What future change becomes harder if this proceeds?
- **Reasoning:** Can maintainers reason about failure and change without relying only on tests, CI, or conventions?
- **One-way door:** Is this hard enough to reverse that it needs an ADR?

## Response Shape

- Name the entanglement directly: "This couples X to Y, so Z becomes harder."
- Separate simple from easy: "This is familiar, but not simpler because..."
- If proceeding or adjusting on a one-way door, offer an ADR at `docs/adr/NNNN-<decision-slug>.md` with context, options, consequences, and decision.
