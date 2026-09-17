# Anime.js Timeline

## Creation

```js
import { createTimeline } from "animejs";

const tl = createTimeline({
  defaults: { duration: 800, ease: "outExpo" }, // applies to direct children
  delay: 200,
  loop: true,
  alternate: true,
  autoplay: true, // false | onScroll({...})
});
```

## .add() and the position parameter

Omitted position = appended at the timeline end.

```js
tl.add(".title", { y: [40, 0], opacity: [0, 1] });
tl.add(".sub", { y: [30, 0], opacity: [0, 1] }, "<0.15"); // 0.15s after PREV START
tl.add(".cta", { scale: [0.9, 1] }, "-=0.2");             // overlap: 0.2s before end
```

| Type | Example | Meaning |
| ---- | ------- | ------- |
| Absolute | `500` | at exactly 500ms |
| Addition | `"+=100"` | 100ms after timeline end |
| Subtraction | `"-=100"` | 100ms before timeline end |
| Multiplier | `"*=.5"` | scaled against total duration |
| Prev end | `"<"` | at previous element's end |
| Prev start | `"<<"` | at previous element's start |
| Offset combo | `"<<+=250"`, `"<-=250"` | offset from prev start / end |
| Label | `"intro"` | at `tl.label("intro", 1000)` |
| Stagger | `stagger(10)` | stagger child positions by 10ms |

```js
tl.label("intro", 0)
  .add(".sq", { x: "15rem" }, 500)
  .add(".ci", { x: "15rem" }, "intro")
  .add(".tr", { x: "15rem" }, "<-=250");
```

## Other builders

```js
tl.set(".box", { opacity: 0 }, 0);   // instant values at a position
tl.call(() => console.log("hit"), ">"); // callback at a position
tl.sync(otherTimeline, "<");         // sync another timeline/WAAPI anim
tl.remove(".box");                   // remove children targeting .box
tl.init();                           // force-initialize (measure) without playing
```

Stagger works as a position too: `.add([".a", ".b"], { x: "15rem" }, stagger(500, { start: "intro+=200" }))`.

## Nesting

Timelines nest; each child block is one unit in the parent.

```js
function heroIn() {
  const t = createTimeline();
  t.add(".hero-title", { y: [50, 0], opacity: [0, 1] })
   .add(".hero-sub", { y: [30, 0], opacity: [0, 1] }, "<0.15");
  return t;
}
createTimeline().add(heroIn()).add(cardsIn(), "-=0.2");
```

Advantage: each section is encapsulated and repositionable. `defaults` do NOT cross into nested timelines — set them per timeline.

## Control

```js
tl.play(); tl.pause(); tl.resume(); tl.reverse(); tl.restart();
tl.complete(); tl.cancel(); tl.revert();
tl.seek(1200); tl.seek("intro");  // ms or label
tl.stretch(0.5);                  // 2x faster total
tl.refresh();
tl.progress; // 0–1
```

## Common pattern — hero sequence

```js
createTimeline({ defaults: { ease: "outExpo", duration: 600 } })
  .add(".hero-kicker", { opacity: [0, 1], y: [16, 0] })
  .add(".hero-title", { opacity: [0, 1], y: [40, 0] }, "<0.1")
  .add(".hero-cta", { opacity: [0, 1], scale: [0.96, 1] }, "-=0.3");
```

Keep UI sequences under ~1.2s total; exits at half the entrance duration.
