# KNOWLEDGE — Layout & Composition

Patterns for arranging content. The taxonomy extracts evidence for these
from references; this card supplies the judgment layer.

## Canonical scaffolds

| Scaffold | Anatomy | Choose when |
|---|---|---|
| persistent sidebar | rail (200–280 px) + content, sticky global nav | 5+ peer sections, repeat-visit tools |
| top-nav centered | slim header + centered column | marketing, editorial, focused tasks |
| split hero | 1:1 or 2:1 text/media, proof below | products needing immediate demonstration |
| bento grid | varied-weight tiles on one grid rhythm | capability summaries, feature overviews |
| dense data table | toolbar + sticky header + tabular numerals | comparison across many records |
| full-bleed media | edge-to-edge visual, overlaid type | atmospheric brands, cinematic direction |
| stacked mobile | single column, priority-ordered | ≤ 767 px always; apps |

## Grid discipline

- One base grid per view (12-col desktop, 4-col tablet, 1-col mobile).
- Break the grid for emphasis only: one element, intentionally offset.
- Gutter = DNA grid_gap; container max-width prevents line-length drift
  (1440+ px is for margins, not wider content).

## Spacing logic

- Space scale from DNA (4 or 8 base). Adjacent elements: pick the step that
  communicates relationship — related = smaller step, grouped = larger gap.
- Inside padding < outside padding (groups read as objects).
- Section rhythm: repeat a consistent vertical step (e.g. 96 px) so the
  page breathes in a pattern.

## Density decisions

- data_heavy → compact class: 36 px rows, 12 px card padding, 12–13 px
  table font, tabular numerals, sticky headers, zebra optional.
- narrative → spacious: 56 px rows equivalent, 24 px padding, generous
  section steps.
- Never mix density classes in one view except dashboard+detail splits.

## Responsive adaptation (summary)

Navigation model, grid columns, and interaction mode change per breakpoint
class — see `ENGINE/responsive-engine.md` §2. Tables become stacked cards
on mobile; heroes become typographic; ambient motion drops out.

## Composition heuristics

- Above the fold: claim + proof + action (landing) or status + action
  (dashboard). Everything else can scroll.
- Diagonals create motion; horizontals create calm; verticals create
  procession — match to content meaning.
- Odd counts of items (3, 5) read better in rows than even, unless a grid
  symmetry is intended.
- The eye enters top-left (LTR) — earn its path with scale, then guide with
  alignment, then reward with accent.
