# Anime.js Core API (`animate()`)

> v4. Targets are the FIRST argument: `animate(targets, params)`. All times in **milliseconds**.

## Targets

```js
animate(".box", { x: 100 });                    // CSS selector
animate(document.querySelector(".box"), { ... }); // DOM element(s), NodeList, Array
animate([el1, el2], { ... });                   // array of targets
animate(jsObject, { value: 100 });              // plain JS object (JS engine only)
```

## Animatable properties

| Group | Examples |
| ----- | -------- |
| Transforms (prefer) | `x`, `y`, `z`, `rotate`, `rotateX/Y/Z`, `scale`, `scaleX/Y`, `skewX/Y` |
| CSS | `opacity`, `color`, `backgroundColor`, `borderRadius`, `boxShadow`, `filter`, `clipPath` |
| CSS variables | `{ "--my-var": 100 }` |
| SVG attributes | `attr: { cx: 200, r: 50 }`, `d` (with `morphTo`), `points` |
| JS object props | any numeric key on the target object |

Units: numbers get sensible defaults (`x: 100` → `px`); strings keep theirs (`x: "12rem"`, `rotate: "-1turn"`).

## Tween value types

```js
animate(".box", {
  x: 200,                    // to — animate TO this
  y: { from: 50 },           // from — start here, go to current
  opacity: [0, 1],           // [from, to]
  rotate: "-=90",            // relative (JS engine only)
  backgroundColor: "#ff0000",// colors interpolate
  x: (el, i) => i * 50,      // function-based per target
});
```

## Tween parameters (per property or global)

```js
animate(".box", {
  y: [
    { to: "-2.75rem", ease: "outExpo", duration: 600 },  // keyframes
    { to: 0, ease: "outBounce", duration: 800, delay: 100 },
  ],
  rotate: { from: "-1turn", delay: 0 },  // property-specific params
  duration: 800,          // default per tween
  delay: stagger(50),     // ms | stagger() | function
  ease: "inOutCirc",      // default ease
  composition: "blend",   // "replace" (default) | "none" | "blend" — JS only
  modifier: (v) => Math.round(v), // transform the interpolated value — JS only
});
```

### composition (JS engine only)

```js
animate(".shape", { x: random(-100, 100), composition: "blend" });
// or globally: import { engine } from "animejs"; engine.defaults.composition = "blend";
```

- `"replace"` — new tween kills conflicting running tweens (default under ~1000 targets).
- `"none"` — running tweens finish; new one waits (best perf at scale).
- `"blend"` — additive; overlapping transforms sum instead of fighting. Best for drift/mouse-follow layers.
- `blend` is INCOMPATIBLE with keyframes, colors, `loop`, `alternate`, `reversed`, `reverse()`.

## Easings

String names: `linear`, `inQuad`/`outQuad`/`inOutQuad`/`outInQuad` (same ×4 for `Cubic Quart Quint Sine Expo Circ Bounce`), `inBack`/`outBack`/… (overshoot 1.70158), `inElastic`/`outElastic`/… (`outElastic(.8, 1.2)` tunable), `inOut(power)` e.g. `inOut(3)`.

```js
import { animate, createSpring, cubicBezier, steps } from "animejs";

animate(".a", { x: 200, ease: "outExpo" });
animate(".b", { x: 200, ease: "outElastic(.8, 1.2)" });
animate(".c", { x: 200, ease: cubicBezier(0, 0, 0.58, 1) }); // custom bezier
animate(".d", { x: 200, ease: steps(5) });                   // stepped
animate(".e", { x: 200, ease: createSpring({ stiffness: 95, damping: 13 }) }); // spring (overrides duration)
animate(".f", { x: 200, ease: createSpring({ bounce: 0.5, duration: 350 }) }); // perceived spring
```

UI mapping: entrances → `outExpo`/`outQuad`; on-screen moves → `inOutCirc`/`inOutQuad`; constant (marquee, motion-path) → `linear`; playful → spring `bounce 0.1–0.3`.

## Playback settings

```js
animate(".box", {
  x: 200,
  duration: 800,
  delay: 100,
  loop: true,        // true | iteration count
  loopDelay: 500,    // ms between loops — JS only
  alternate: true,   // ping-pong
  reversed: true,    // start reversed
  autoplay: true,    // false = create paused; or onScroll({...}) to bind scroll
  playbackRate: 2,   // 2x speed
  frameRate: 30,     // throttle — JS only
});
```

## Callbacks

```js
animate(".box", {
  x: 200,
  onBegin: (anim) => {},       // JS only
  onUpdate: (anim) => {},      // every tick — NEVER setState here, write to ref/DOM
  onRender: (anim) => {},      // JS only, after render
  onLoop: (anim) => {},        // JS only
  onComplete: (anim) => {},
  onPause: (anim) => {},
});
// Promise style:
await animate(".box", { x: 200 }).then(() => console.log("done"));
```

## Methods & properties

```js
const anim = animate(".box", { x: 200, autoplay: false });
anim.play(); anim.pause(); anim.restart(); anim.reverse();
anim.complete(); anim.cancel(); anim.revert(); // revert restores pre-animation inline styles
anim.seek(400);      // jump to ms
anim.stretch(2);     // scale total duration — JS only
anim.refresh();      // re-read targets/values — JS only
anim.progress;       // 0–1 getter/setter
```

## Lightweight WAAPI build (~3kb)

```js
import { waapi } from "animejs";
waapi.animate(".box", { x: 200 }); // basic tweens only; no JS-only flags (marked above)
```

## React — scoped, always

```jsx
import { useEffect, useRef } from "react";
import { animate, createScope, stagger } from "animejs";

useEffect(() => {
  const scope = createScope({ root: ref.current }).add((self) => {
    animate(".card", { opacity: [0, 1], y: [24, 0], delay: stagger(60) });
    self.add("nudge", (n) => animate(".card", { x: n * 10 })); // callable later
  });
  return () => scope.revert();
}, []);
// scope.methods.nudge(5);
```

`createScope({ mediaQueries: { portrait: "(orientation: portrait)" } })` gives responsive branches via `matches`.
