# Pattern Library (auto-generated)

Extracted from the indexed reference library. Each pattern carries
its principle, when to use it, and when to avoid it. Evidence =
number of indexed references that demonstrate the pattern.

## Reduced Motion Fallback

- **Evidence:** 51 reference(s)
- **Principle:** Every choreographed effect needs a static, equally complete state.
- **Use when:** Always, without exception.
- **Avoid when:** Never.
- **Examples:** `motion-three-d-map-canvas-minimal-spacious-001.mp4`, `motion-three-d-map-canvas-minimal-spacious-002.mp4`, `motion-three-d-map-canvas-dark-ui-003.mp4`, `motion-three-d-map-canvas-minimal-spacious-004.mp4`

## Scroll Choreography

- **Evidence:** 41 reference(s)
- **Principle:** Tie motion to scroll position, never to elapsed time, so users stay in control.
- **Use when:** Narrative marketing pages.
- **Avoid when:** Task surfaces, long-form reading, low-power devices.
- **Examples:** `motion-misc-map-canvas-minimal-spacious-003.mp4`, `motion-misc-map-canvas-data-dense-004.mp4`, `motion-misc-map-canvas-light-ui-011.mp4`, `motion-misc-bottom-nav-dark-ui-016.mp4`

## Bento Composition

- **Evidence:** 29 reference(s)
- **Principle:** Vary tile weight to encode importance while keeping a single grid rhythm.
- **Use when:** Feature overviews, capability summaries.
- **Avoid when:** Ordered/sequential content, or when tiles have equal weight.
- **Examples:** `landing-bento-grid-dark-ui-muted-neutral-card-grid-001.jpg`, `dashboard-bento-grid-dark-ui-card-grid-015.jpeg`, `motion-three-d-map-canvas-minimal-spacious-004.mp4`, `motion-three-d-map-canvas-dark-ui-005.mp4`

## Persistent Sidebar

- **Evidence:** 15 reference(s)
- **Principle:** Keep global navigation always reachable when users pivot between many peer sections.
- **Use when:** 5+ top-level destinations, repeat-visit tooling, desktop-first workflow.
- **Avoid when:** Marketing pages, <=4 destinations, mobile-primary audiences.
- **Examples:** `editorial-sidebar-content-dark-ui-001.jpg`, `editorial-sidebar-content-dark-ui-002.jpg`, `ui-sidebar-content-dark-ui-015.png`, `motion-three-d-map-canvas-minimal-spacious-002.mp4`

## Three D Product Focus

- **Evidence:** 10 reference(s)
- **Principle:** 3D earns its cost only when rotation/inspection is the message.
- **Use when:** Physical products, spatial data, configurators.
- **Avoid when:** Decorating a page that could ship as an image.
- **Examples:** `motion-three-d-map-canvas-minimal-spacious-001.mp4`, `motion-three-d-map-canvas-minimal-spacious-002.mp4`, `motion-three-d-map-canvas-dark-ui-003.mp4`, `motion-three-d-map-canvas-minimal-spacious-004.mp4`

## Dense Data Table

- **Evidence:** 4 reference(s)
- **Principle:** Maximise scannable rows per viewport; align numerals right, use tabular figures.
- **Use when:** Comparison and scanning across many records is the primary job.
- **Avoid when:** Fewer than ~8 records, or the record itself is the destination.
- **Examples:** `data-dense-dark-ui-004.png`, `data-dense-dark-ui-005.jpg`, `data-dense-card-grid-dark-ui-001.jpg`, `motion-scroll-sidebar-card-grid-data-dense-008.webm`

## Ambient Shader Background

- **Evidence:** 0 reference(s)
- **Principle:** Keep ambient motion below conscious attention: low contrast, low velocity, pausable.
- **Use when:** Brand surfaces needing depth without content competition.
- **Avoid when:** Text-heavy or data-heavy regions; battery-constrained contexts.

## Bottom Tab Navigation

- **Evidence:** 0 reference(s)
- **Principle:** Put 3-5 primary destinations inside thumb reach.
- **Use when:** Mobile app-like surfaces with flat IA.
- **Avoid when:** Deep hierarchies, desktop layouts.

## Hero Value Proposition

- **Evidence:** 0 reference(s)
- **Principle:** One claim, one proof, one action; everything else is below the fold.
- **Use when:** First-touch marketing surfaces.
- **Avoid when:** Authenticated product surfaces.

## Kpi Summary Row

- **Evidence:** 0 reference(s)
- **Principle:** Answer 'is anything wrong?' above the fold before offering detail.
- **Use when:** Monitoring and operational dashboards.
- **Avoid when:** Exploratory analytics where no single metric is canonical.

## Progressive Disclosure

- **Evidence:** 0 reference(s)
- **Principle:** Reveal depth on demand so the default view stays legible.
- **Use when:** Complex records with rarely-needed fields.
- **Avoid when:** Users need side-by-side comparison of the hidden fields.

## Subtle Hover Elevation

- **Evidence:** 0 reference(s)
- **Principle:** Confirm affordance with the smallest perceivable change (<=4px, <=150ms).
- **Use when:** Any pointer-driven interactive surface.
- **Avoid when:** Touch-only contexts, where hover never fires.
