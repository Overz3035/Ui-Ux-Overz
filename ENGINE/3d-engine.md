# ENGINE — 3D Engine

3D is a content decision, not a style decision. Ship WebGL only when spatial
understanding, product inspection, or generative depth **adds information**
the DOM cannot deliver (§22). A website is not better because it is 3D.

## 1. Decision gate (run in order)

1. Does the content have a spatial/z-axis story the user benefits from
   manipulating? If no → CSS gradient, still render, or SVG.
2. Is there a graceful fallback (poster image / static render) that keeps
   all information? If no → design that first.
3. Budget check: scene ≤ ~100k triangles for hero props, DPR clamped
   (min(devicePixelRatio, 2)), no per-frame allocation, pause off-screen.
4. Battery/low-power audience? Then 3D only on explicit user opt-in.

## 2. Stack routing

| Need | Tool |
|---|---|
| React tree, declarative scene | React Three Fiber (+ drei helpers) |
| Vanilla scene, maximum control | Three.js |
| Animated gradient/ambient surfaces without scene mgmt | Shadergradient |
| Custom surface effects (noise, displacement, refraction) | custom GLSL shaders |
| Glass/refraction styling on DOM | CSS backdrop-filter first; LiquidGlass.js only when true refraction is required |

Never introduce WebGL for a single hover tilt — CSS `transform: perspective`
is enough.

## 3. Scene hygiene

- One `<Canvas>` per page; lazy-load below the fold.
- Text stays in DOM. Never render body copy in WebGL (a11y + SEO).
- Respect `prefers-reduced-motion`: freeze camera/loop, keep interactivity.
- Poster + `<noscript>` fallbacks; loading state ≤ the duration of the
  largest texture.
- Dispose geometries/materials; R3F handles this, vanilla must not leak.

## 4. Shader quick guidance

Technique knowledge: `KNOWLEDGE/three-d/shader-techniques.md` (recipes,
guards, vocabulary). Registry concept entry: `shaders`.

- Ambient backgrounds: fragment shader on a fullscreen quad or
  Shadergradient; keep contrast low behind text (a11y 4.5:1 still applies).
- Animate `u_time` with delta; clamp dt ≤ 50 ms after tab switches.
- Provide a static SVG/CSS gradient fallback when WebGL context fails.

## 5. Performance contract

| Metric | Budget |
|---|---|
| Time to interactive | 3D must not delay it (defer init) |
| Frame rate | 60 fps desktop / 30 fps mobile floor; adaptive DPR |
| Bundle | `three` ≈ 150 kB gzip — justify per page, code-split it |
| GPU memory | dispose on route change |

## 6. When NOT to use 3D (frequent cases)

- Hero decoration that a gradient + parallax layers achieve.
- Data visualization that is fundamentally 2D (charts, tables).
- Sites whose audience is task-driven (see `industrial-control` DNA).
- Any project where the fallback is "user stares at a black rectangle".
