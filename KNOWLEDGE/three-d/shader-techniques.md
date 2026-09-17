# KNOWLEDGE — Shader Techniques

Vendor-neutral card for the RESOURCE-LIST §3 "Shaders" entry. Code-level
routing lives in `ENGINE/3d-engine.md` §2 (Shadergradient vs custom GLSL).

## What shaders buy you (and what they cost)

A fragment shader computes every pixel per frame on the GPU. That buys:
infinite gradients, noise fields, refraction, displacement — looks no CSS
can fake. It costs: battery, fill-rate, and a maintenance surface. Rule:
ship a shader when the *motion itself* is the brand statement; ship a
static gradient when a screenshot would look identical.

## Core vocabulary (minimum viable shader literacy)

| Concept | Meaning | Design consequence |
|---|---|---|
| `u_time` | seconds since start | drives all ambient motion; clamp dt after tab switches |
| `mix(a, b, t)` | linear blend | every soft gradient is a mix chain |
| `smoothstep(edge0, edge1, x)` | Hermite-smooth transition | banding-free ramps; pick edges from the DNA palette |
| fbm / value noise | layered pseudo-random field | organic clouds, smoke, aurora |
| uv | normalized pixel coordinates (0..1) | design in relative space; responsive by construction |
| `length(uv - c)` | radial distance | glows, vignettes, liquid blobs |
| texture displacement | sample offset by noise | liquid glass, heat shimmer |
| normals + fresnel | view-angle highlight | glass edge lighting |

## Recipes mapped to motion categories

- **background (ambient)**: 2-3 octave fbm, hue from DNA accent, velocity
  < 0.05 uv/s, contrast delta < 8% against surface colour.
- **hero reveal**: u_time-eased radial mask expanding from the CTA anchor.
- **liquid**: domain-warped noise (`fbm(p + fbm(p))`) — never under text.
- **glass edge**: fresnel term + 1-2% chromatic offset on border pixels.

## Hard guards

1. **Contrast**: text over shader regions still needs 4.5:1 — add a scrim
   (surface-colour gradient overlay) before blaming the palette.
2. **Reduced motion**: freeze `u_time` at a curated frame; the shader
   becomes a static artwork, information intact.
3. **Performance budget**: render at ≤ 0.75× DPR, cap at 30fps on coarse
   pointers, `IntersectionObserver` pause off-screen, `visibilitychange`
   pause on hidden tabs.
4. **Fallback**: WebGL context failure → static SVG/CSS gradient of the
   same palette (the DNA's imagery family).
5. **Battery-sensitive audiences** (`industrial-control`, data tools):
   shaders are opt-in decoration, never on task surfaces.

## Where the verified tools fit

- `@shadergradient/react` — parameterised gradient surfaces without writing
  GLSL (see registry entry for package/version).
- Custom GLSL — full control; keep shaders ≤ ~100 lines until profiling
  proves otherwise.
- three.js ShaderMaterial — for shader-driven geometry, not fullscreens.
