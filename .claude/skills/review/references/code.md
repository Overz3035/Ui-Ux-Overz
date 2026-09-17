# Code Review Lens

## Check

- **Intent:** Is the engineering goal clear in one sentence?
- **Necessity:** Does this need to exist now, or is it speculative flexibility?
- **Fit:** Does the work still serve the stated aim and Open Horizons outcome?
- **Sufficiency:** Could less code, fewer files, or an existing pattern solve it?
- **Simplicity:** Is this less entangled, not merely easier or more familiar to write?
- **Mechanism:** Can the author explain why this approach prevents the failure or creates the intended behavior?
- **Reasoning:** Can a maintainer reason about failure and change without relying only on tests or CI?
- **Completeness:** Are callers, fixtures, docs, persistence, migrations, install paths, and verification covered where relevant?
- **Scope:** Simple changes should not sprawl across many files without a reason.
- **Artifact:** Does this improve shipped behavior, reliability, or changeability, not just author convenience?
- **Boundaries:** Do modules/components reduce what each part must know, or only rearrange files?

## Response Shape

- Name drift directly: "The aim was X; this now addresses Y."
- Push back on speculative abstraction: "Can we solve only the present problem?"
- Require evidence: "State the mechanism, then verify that exact path."
