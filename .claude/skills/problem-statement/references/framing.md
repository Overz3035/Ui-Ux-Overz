# Framing Reference

Load only when `/problem-statement` is becoming ambiguous, exhaustive, or example-driven.

## X-Y Pattern

A request may name Y (attempted solution) while the real need is X.

Signs:
- The request is oddly specific for a simple goal.
- The solution feels like a workaround.
- The user asks for a technique without explaining why.
- The proposed path has many steps for a simple outcome.

Response shape:
> "You're asking for [Y], but the underlying need seems to be [X]. Is that right?"

## WHAT vs HOW

A problem statement names what must change, not how to change it.

| Solution-shaped | Problem-shaped |
|---|---|
| Add a caching layer | Page loads take 3+ seconds; users abandon before content appears |
| Refactor auth | Adding a provider takes 2 weeks and touches 6 files |
| We need microservices | Deploying a fix requires coordinating 4 owners and takes 2 weeks |

## Constraints

- **Hard:** physics, regulation, signed commitments, externally binding contracts.
- **Soft:** technical debt, maintainer preference, time pressure, habits.
- **Assumed:** constraints nobody can trace to an owner or reason.

Question soft/assumed constraints by asking:
- What would we do if this constraint did not exist?
- Who decided it was fixed?
- What is the cost of violating it vs. preserving it?

## Frame Pressure Test

Use this when the first frame feels too easy:
- What does this frame reveal or make easier?
- What does it hide or make harder?
- What plausible alternate story would change the solution space?
- Who would disagree, and what alternate story would they tell?
- What evidence would show this is only a symptom?
