# KNOWLEDGE — Typography Pairings

Curated families the DNA generator selects from (Google Fonts, with system
fallbacks). Organized by radius family. Pairing = display + body.

## Sharp (precision, editorial, luxury, brutalist)

| Display | Body | Reads as |
|---|---|---|
| Space Grotesk | Inter | technical-modern |
| Archivo | IBM Plex Sans | institutional-strong |
| Fraunces | Public Sans | editorial-warm serif |
| Sora | Manrope | geometric-calm |
| Bricolage Grotesque | Inter | expressive-contemporary |
| Instrument Serif | Geist | fashion-editorial |

## Soft (humanist, playful, wellness)

| Display | Body | Reads as |
|---|---|---|
| Outfit | Nunito Sans | friendly-round |
| Plus Jakarta Sans | Figtree | modern-approachable |
| Quicksand | Source Sans 3 | gentle-casual |
| DM Serif Display | DM Sans | warm-elegant |
| Gabarito | Onest | soft-confident |

## Mixed (industrial, technical, dashboard)

| Display | Body | Reads as |
|---|---|---|
| IBM Plex Sans | IBM Plex Sans | engineering-unified |
| Barlow | Barlow | utilitarian-compact |
| Chivo | Inter | neutral-operational |
| Saira | Roboto Flex | instrument-panel |
| Rubik | Inter | rounded-practical |

## Rules that outrank any pairing

- Body line-height ≥ 1.5; display ≤ 1.1.
- 45–75 characters per line.
- Tabular numerals (`font-variant-numeric: tabular-nums`) in tables, KPIs,
  timers, and any column that must scan.
- Weight range: pick 2–3 weights per family; ship less.
- `font-display: swap`; subset; two families max (mono counts as utility,
  not a third voice — JetBrains Mono default).
- Scale ratio from DNA (1.2 / 1.25 / 1.333 / 1.414); fluid via clamp().
