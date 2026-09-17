---
name: animejs
description: "Anime.js v4 animation engine sub-skill - core, timeline, stagger, scroll, SVG, text."
---

# Anime.js — Sub-skill

> Package: `animejs` (v4 only). Import: `import { animate, createTimeline, stagger, onScroll } from "animejs"`
> Docs: https://animejs.com/documentation — v4 syntax is NOT backwards compatible with v3.

## When to use Anime.js vs alternatives

| Criteria              | CSS Native | Anime.js            | GSAP                | Framer Motion       |
| --------------------- | ---------- | ------------------- | ------------------- | ------------------- |
| Hover / simple toggle | **Yes**    | Overkill            | Overkill            | Overkill            |
| Scroll reveal (basic) | view()     | **onScroll sync**   | ScrollTrigger       | useScroll           |
| Pinned / scrubbed scroll cinema | No | Limited (no pin) | **ScrollTrigger** | No |
| Grid stagger / text split | No    | **stagger + splitText** | Distribution + SplitText | Variants |
| SVG draw / morph / motion path | No | **Built-in**     | MorphSVG (paid*)    | No                  |
| Timeline orchestration | No      | **Yes**             | **Yes (richer)**    | Variants (basic)    |
| Drag with physics     | No         | **createDraggable** | Draggable plugin    | drag prop           |
| Layout / shared element | No       | createLayout (basic) | Manual             | **layoutId**        |
| Bundle size           | 0kb        | **~24kb full, ~3kb WAAPI** | ~30kb + plugins | ~50kb |

\* MorphSVG/DrawSVG are Club GreenSock; Anime.js ships morph/draw/motion-path free.

**Rule**: if it needs pin, scrubbed cinema, or containerAnimation — GSAP. If it needs React layoutId/exit — Framer Motion. If it needs stagger grids, SVG draw/morph, split-text, or scroll-synced tweens at minimal weight — Anime.js. Otherwise CSS first.

## Setup

```js
// Full API from the main module
import { animate, createTimeline, stagger, onScroll, createSpring, splitText } from "animejs";

// Tree-shaken subpaths (only what you import ships)
import { animate } from "animejs/animation";
import { createTimeline } from "animejs/timeline";
import { stagger, random } from "animejs/utils";
import { onScroll } from "animejs/events";
import { splitText } from "animejs/text";
import { svg } from "animejs/svg";
```

```html
<!-- No bundler: ESM via CDN -->
<script type="importmap">
{ "imports": { "animejs": "https://esm.sh/animejs" } }
</script>
```

React: run inside `createScope({ root })` and `revert()` on unmount — never bare `animate()` in `useEffect`.

```jsx
useEffect(() => {
  const scope = createScope({ root: ref.current }).add(() => {
    animate(".card", { opacity: [0, 1], y: [24, 0], delay: stagger(60) });
  });
  return () => scope.revert(); // kills everything, prevents double-run in StrictMode
}, []);
```

## Core Patterns

### animate() — milliseconds, not seconds

```js
import { animate } from "animejs";

animate(".square", {
  rotate: 90,            // x/y/scale/rotate/opacity = transforms, GPU-friendly
  duration: 600,         // MS (GSAP uses seconds — do not mix up)
  delay: 100,            // MS
  ease: "outExpo",       // built-ins: inOutQuad, outBounce, inOutCirc, inOut(3) ...
  loop: true,            // true | number of iterations
  alternate: true,       // ping-pong each loop
});
```

Per-property parameters override the globals:

```js
animate(".el", {
  y: [
    { to: "-2.75rem", ease: "outExpo", duration: 600 },
    { to: 0, ease: "outBounce", duration: 800, delay: 100 },
  ],
  rotate: { from: "-1turn" }, // starts here, animates to current
  ease: "inOutCirc",
});
```

### Overlapping tweens — composition

```js
// Random drift that blends with other running tweens instead of killing them
animate(".shape", {
  x: random(-100, 100),
  rotate: random(-180, 180),
  composition: "blend", // "replace" (default) | "none" | "blend"
});
```

`blend` is additive — best for translate/scale/rotation. It is incompatible with keyframes, colors, `loop`, `alternate`, and `reverse()`.

### Stagger

```js
animate(".dot", { scale: [1, 0.75], delay: stagger(50) });                       // time
animate(".dot", { scale: stagger([1.1, 0.75], { grid: [13, 13], from: "center" }) }); // values
animate(".dot", { y: ["-2rem", "2rem"], delay: stagger(100, { from: "random" }) });
```

`from`: `"first" | "center" | "last" | "random" | index | [x, y]`. Keep it `"first"` unless the design calls for a radial/random wave.

### Timeline

```js
createTimeline({ defaults: { ease: "outExpo", duration: 500 } })
  .add(".title", { y: [40, 0], opacity: [0, 1] })       // sequential
  .add(".sub", { y: [30, 0], opacity: [0, 1] }, "<0.15") // 0.15s after prev START
  .add(".cta", { scale: [0.9, 1], opacity: [0, 1] }, "-=0.2"); // overlap prev end
```

Position cheatsheet: `500` (absolute ms) · `"+=100"` / `"-=100"` (vs timeline end) · `"<"` (prev end) · `"<<"` (prev start) · `"<<+=250"` / `"<-=250"` (offset) · `"label"` · `stagger(10)`. See `references/timeline.md`.

### Scroll — autoplay: onScroll()

```js
animate(".panel", {
  x: "-20rem",
  ease: "linear",
  autoplay: onScroll({
    target: ".section",   // what triggers; default = first animation target
    enter: "bottom top",  // "triggerPoint viewportPoint"
    leave: "top bottom",
    sync: true,           // hard-lock progress to scroll (true | 0..1 smooth | "easeName")
  }),
});
```

`sync: "play pause"` (default) just plays/pauses on enter/leave. No pin support — if the design needs pinning, switch to GSAP ScrollTrigger.

### SVG + text (free, no plugins)

```js
import { animate, createDrawable, createMotionPath, splitText, stagger } from "animejs";

animate(createDrawable(".circuit"), { draw: ["0 0", "0 1", "1 1"], delay: stagger(40) });
animate(".car", { ...createMotionPath(".circuit"), ease: "linear", duration: 5000, loop: true });
animate(".a", { d: morphTo(".b") }); // needs `import { morphTo } from "animejs"`

const { chars } = splitText("h2", { words: false, chars: true });
animate(chars, { y: ["1em", 0], opacity: [0, 1], delay: stagger(30) });
```

## DO NOT — Critical mistakes

### 1. Seconds instead of milliseconds

```js
// BAD — 0.8ms, effectively instant
animate(".box", { x: 200, duration: 0.8 });

// GOOD
animate(".box", { x: "12rem", duration: 800, ease: "outExpo" });
```

### 2. v3 syntax in a v4 project

```js
// BAD (v3) — targets inside params, anime() factory
anime({ targets: ".box", translateX: 200 });

// GOOD (v4) — targets are the first argument, x not translateX
animate(".box", { x: "12rem" });
```

### 3. blend where it is unsupported

```js
// BAD — blend + loop/keyframes/colors silently misbehaves
animate(".box", { scale: [0.5, 1, 1.5], loop: true, composition: "blend" });

// GOOD — blend only for single-shot additive transform tweens
animate(".box", { x: random(-100, 100), composition: "blend" });
```

### 4. setState in onUpdate

```js
// BAD — re-renders 60x/s
animate(obj, { x: 100, onUpdate: (anim) => setProgress(anim.progress) });

// GOOD — write to a ref or the DOM directly
animate(obj, { x: 100, onUpdate: (anim) => { barRef.current.style.transform = `scaleX(${anim.progress})`; } });
```

### 5. Animating layout properties

```js
// BAD — width/height/top/left force reflow every frame
animate(".box", { width: "12rem", height: "12rem" });

// GOOD — composited only
animate(".box", { scale: 1.5, opacity: 0.5 });
```

### 6. Unscoped animation in React

```js
// BAD — leaks + double-fires under StrictMode
useEffect(() => { animate(".box", { x: 100 }); }, []);

// GOOD — scoped + reverted
useEffect(() => {
  const scope = createScope({ root }).add(() => animate(".box", { x: 100 }));
  return () => scope.revert();
}, []);
```

## Refs

- `references/core.md` — Full `animate()` API: targets, animatable props, tweens, easings, springs, playback, callbacks, methods, React scope
- `references/timeline.md` — Timeline creation, position parameter, labels, nesting, control
- `references/scroll.md` — onScroll settings, thresholds, sync modes, callbacks
- `references/svg-text.md` — morphTo, createDrawable, createMotionPath, splitText
