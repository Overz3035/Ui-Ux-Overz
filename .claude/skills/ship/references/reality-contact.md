# Reality Contact Reference

Load only when shipping reveals a different target environment, user behavior, ownership failure, or delivery-path tax than expected.

## Delivery-Path Tax

Look for friction in:
- review queue;
- merge conflicts or branch stability;
- CI gate time, serial checks, flaky checks;
- approval bottlenecks;
- deploy duration;
- rollback readiness;
- manual steps.

## Post-Ship Reality Contact

Shipping is complete only when the change is running, reachable, and behaviorally verified in the target environment.

Ask:
- Did users/operators encounter the problem we thought we solved?
- Did the promised characteristics from `/execute` hold?
- Did hidden constraints or ownership failures appear?
- Should failed verification or rollback learning route to `/salvage`? Should broader learning route to `/aim`, `/problem-space`, guardrail, or metis?

Do not reopen shipped work unless verification fails; route failed verification or rollback learning to `/salvage` when extraction is needed, and route other learning to the next appropriate artifact.
