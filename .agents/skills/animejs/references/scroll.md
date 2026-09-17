# Anime.js onScroll (Scroll Observer)

Binds an animation's autoplay to scroll. **No pin support** — if the design needs pinning, use GSAP ScrollTrigger instead.

## Basic usage

```js
import { animate, onScroll } from "animejs";

animate(".panel", {
  x: "-20rem",
  ease: "linear", // scroll-mapped motion is always linear-ish at the mapping layer
  autoplay: onScroll({
    target: ".section",  // trigger element (default: first animation target)
    enter: "bottom top", // when mapping starts
    leave: "top bottom", // when mapping ends
    sync: true,          // hard-lock progress to scroll
  }),
});
```

## Settings

| Setting | Type | Default | Notes |
| ------- | ---- | ------- | ----- |
| `container` | selector \| element | viewport | the scrolled element |
| `target` | selector \| element | first anim target | what the thresholds measure against |
| `axis` | `"x" \| "y"` | `"y"` | scroll direction |
| `repeat` | boolean | `true` | re-arm after complete; `false` reverts the observer |
| `debug` | boolean | `false` | visual markers — remove in production |

### Thresholds — `enter` / `leave`

Format: `"triggerPoint viewportPoint"`. Points: `top center bottom`, `%`, `px`, or relative (`bottom-=50`).

```js
enter: "bottom top",       // trigger bottom hits viewport top
enter: "bottom-=50 top",   // 50px early
leave: "top+=60 bottom",
```

## Sync modes

```js
sync: "play pause", // DEFAULT — play on enter, pause on leave
sync: "play",       // play on enter, ignore the rest
sync: "play pause reverse reset",

sync: true,   // or 1 — hard-lock animation progress to scroll position
sync: 0.25,   // 0..1 — smoothed follow (closer to 0 = lazier catch-up)
sync: "inOutCirc", // ease the scroll-mapped progress
```

Method-name strings accept the space-separated observer methods (`enter leave enterForward leaveBackward …`).

## Play vs scrub — decision

```js
// Reveal on entry (fire-and-forget) — method sync
animate(".card", {
  opacity: [0, 1], y: [32, 0], duration: 700, ease: "outExpo",
  autoplay: onScroll({ target: ".card", enter: "bottom 85%", sync: "play" }),
});

// Progress mapped to scroll (parallax/scrub feel) — progress sync
animate(".hero-bg", {
  y: ["-4rem", "4rem"], ease: "linear",
  autoplay: onScroll({ target: ".hero", enter: "top bottom", leave: "bottom top", sync: 0.5 }),
});
```

Scrub-mapped tweens: keep `ease: "linear"`, animate `transform`/`opacity` only.

## Callbacks

`onEnter onLeave onEnterForward onEnterBackward onLeaveForward onLeaveBackward onUpdate onSyncComplete onResize`. Never `setState` inside `onUpdate` — write to a ref or the DOM.

## Cleanup (React)

```jsx
useEffect(() => {
  const scope = createScope({ root }).add(() => {
    animate(".card", { opacity: [0, 1], autoplay: onScroll({ target: ".card", sync: "play" }) });
  });
  return () => scope.revert(); // reverts observers too
}, []);
```
