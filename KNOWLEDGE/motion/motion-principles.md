# KNOWLEDGE — Motion Principles (expanded)

`ENGINE/motion-engine.md` is the contract; this card is the craft layer.

## Choreography patterns

| Pattern | Recipe | Notes |
|---|---|---|
| enter-stagger | children delay = i × stagger, capped at 6 | list/card entrance |
| scroll-reveal | IntersectionObserver + translateY(16→0) + fade | T3; threshold 0.15–0.3 |
| pin-scrub | section pinned, progress scrubs transforms (GSAP ScrollTrigger) | narrative only |
| hover-elevation | translateY(-2 to -4) + shadow step, 120–150 ms | confirm affordance |
| press-squash | scale(0.97) on active, 80–100 ms | tactile confirmation |
| shared-element | Framer Motion layoutId between views | continuity of identity |
| page-transition | exit 150–200 ms → enter 200–300 ms, one shared anchor | route changes |
| ambient-loop | slow transform/gradient drift 20 s+ | T4; pause off-screen |

## Easing judgment

- Decelerate into rest (`ease-out` family) for enters: fast start reads as
  responsive.
- Accelerate out (`ease-in`) for exits: they are leaving, get them gone.
- Springs for interruptible gestures; curves for plays-once reveals.
- Scrubbing is linear (user is the clock).

## Micro-interaction anatomy

A good micro-interaction has: trigger (user act), rule (what changes),
feedback (the change, ≤ 150 ms), and no modal interruption. If it needs an
explanation, it is too clever.

## Performance & restraint

- Compositor-only properties (transform/opacity); measure with devtools
  performance panel on the cheapest target device.
- One ambient loop per page. Two means the page is restless.
- Loading spinners: only beyond 300 ms; skeletons only where shape is
  known; never both.

## Motion as information

- Direction of movement encodes where things came from / went (drawer from
  right, back = previous in nav order).
- Magnitude encodes distance in the IA, not dramatic value.
- Stagger encodes sequence; randomized delays encode nothing.

## Reduced motion (repeat until reflex)

Every pattern above needs its static equivalent: scroll-reveal → visible;
pin-scrub → static composed frame; ambient → first frame; shared-element →
instant swap. The information must survive with animations off.
