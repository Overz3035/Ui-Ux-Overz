# Anime.js SVG + Text

Free and built-in — no paid plugins needed.

## Line drawing — createDrawable

```js
import { animate, createDrawable, stagger } from "animejs";

const [drawable] = createDrawable(".circuit"); // selector | line | path | polyline | rect
animate(drawable, {
  draw: ["0 0", "0 1", "1 1"], // "start end": 0 hidden → 1 fully drawn
  ease: "inOutCirc",
  delay: stagger(40),
});
```

`draw: "0 1"` = fully drawn. Animate between draw states for draw-on effects.

## Motion path — createMotionPath

```js
import { animate, createMotionPath } from "animejs";

animate(".car", {
  ...createMotionPath(".circuit"), // spreads { translateX, translateY, rotate }
  ease: "linear",                  // constant speed along the path
  duration: 5000,
  loop: true,
});
```

Second argument is path offset `0–1`: `createMotionPath(".circuit", 0.5)` starts halfway.

## Shape morphing — morphTo

```js
import { animate, morphTo } from "animejs";

animate(".shape-a", { d: morphTo(".shape-b"), ease: "inOutCirc", duration: 800 });
```

Works on `path`/`polygon`/`polyline` (`d` or `points`). Keep point counts close for clean morphs; same fill/box helps.

## Combined SVG scene

```js
animate(createDrawable(".circuit"), { draw: ["0 0", "0 1"], ease: "inOutCirc", duration: 1200 });
animate(".car", { ...createMotionPath(".circuit"), ease: "linear", duration: 5000, loop: true });
animate(".stop-a", { d: morphTo(".stop-b"), ease: "inOutCirc" });
```

## Text splitting — splitText

```js
import { animate, splitText, stagger } from "animejs";

const { chars, words, lines } = splitText("h2", { chars: true, words: true });
// settings: { lines, words, chars, debug, includeSpaces, accessible }

animate(chars, {
  y: ["1em", 0],
  opacity: [0, 1],
  rotate: { from: "-0.125turn" },
  delay: stagger(30, { from: "first" }),
  ease: "outExpo",
  duration: 700,
});
```

Split first, animate the returned collections. `accessible: true` keeps screen-reader text intact. Always `revert()` the splitter on unmount (`split.revert()` or scope revert).

## scrambleText (decoding effect)

```js
import { animate, scrambleText } from "animejs";

animate(".code", scrambleText({ text: "ACCESS GRANTED", chars: "01", duration: 1200 }));
```

Tune with `revealRate revealDelay settleRate cursor ease from reversed seed`. Reserve for rare/first-time moments — never on body copy.
