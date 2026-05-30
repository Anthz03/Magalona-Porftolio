# Lenis Smooth Scroll + Pinning — Design Spec

**Date:** 2026-05-31
**Author:** Kyle Anthony Magalona (with Claude)
**Status:** Approved for planning

## Goal

Upgrade the portfolio's scroll motion to feel like reference site **tenity.com** — a
"Tenity-class" experience built on three qualities the user explicitly chose:

1. **Smooth / inertia scrolling** — a weighted, glides-to-a-stop momentum feel for the
   whole page (the single biggest change to how the site feels).
2. **Stronger parallax depth** — layers visibly moving at different speeds, more
   pronounced than the current subtle drift.
3. **Pinned / sticky sections** — sections that hold on screen while their content
   animates through, then release.

This builds directly on the existing GSAP + ScrollTrigger system (see
`docs/superpowers/specs/2026-05-30-gsap-scroll-parallax-design.md` and its plan, all 9
tasks implemented). It **supersedes** that spec's "Out of scope: Lenis / ScrollSmoother"
decision — the user now wants exactly that smooth-scroll feel.

## Constraints (unchanged from the prior spec unless noted)

- **No build step.** Vanilla HTML + Tailwind (CDN) + `styles.css` + one `script.js`
  IIFE. Lenis loads from CDN via a `<script>` tag, like GSAP.
- **Accessibility first.** `prefers-reduced-motion: reduce` disables ALL motion: no
  Lenis, no pins, no horizontal hijack — content appears in final state, fully
  navigable, native scroll.
- **Don't break what works.** Fixed header, anchor navigation, project modal (focus
  trap + `Esc`), theme toggle, contact form, typewriter must remain unaffected.
- **Light/dark** both supported; effects theme-independent.
- **Mobile.** Heavy effects (pins, horizontal hijack) are desktop-first; mobile and
  reduced-motion degrade gracefully.
- **CDN-blocked fallback.** If GSAP or Lenis fails to load, the site is fully visible
  and usable on native scroll.

## Foundation: Lenis + GSAP ScrollTrigger (Approach A)

Chosen over the two alternatives:

- **GSAP ScrollSmoother** — rejected: it wraps page content in a transformed element,
  which breaks `position: fixed` (the site's header). The prior spec rejected it for the
  same reason.
- **Native CSS scroll-driven animations** — rejected: no inertia/momentum, so it does
  not deliver the Tenity feel.

**Why Lenis works here:** Lenis (v1) smoothly drives the *real* page scroll position
(no wrapper transform), so the fixed header stays fixed and ScrollTrigger pinning (which
relies on native scroll position + spacers) works normally.

Integration pattern (inside the existing `hasGsap && !reduceMotion` block, before the
`gsap.context`):

```
const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((time) => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

- Loaded from CDN (jsDelivr/unpkg), global `Lenis`, after the GSAP tags and before
  `script.js`. A `hasLenis` guard mirrors the existing `hasGsap` guard.
- If Lenis is unavailable, the GSAP effects still run on native scroll (graceful — the
  smooth feel is a progressive enhancement, not a hard dependency).

### Anchor navigation under Lenis

Lenis intercepts scrolling, so in-page anchor links (`a[href^="#"]`, including the mobile
menu and the hero "Scroll down" link) are intercepted and routed through
`lenis.scrollTo(targetId, { offset: -headerHeight })` so they land correctly beneath the
fixed header (currently `main` has `pt-24` ≈ 96px; the offset reads the header's actual
height at click time). When Lenis is not active, the native default anchor jump is left
untouched.

## Per-section design

### Global parallax intensity (stronger depth)

Increase magnitudes on the existing effects; add a small `scrub` smoothing value so
scrubbed tweens glide with the momentum:

| Effect | Current | New |
|---|---|---|
| Hero portrait `yPercent` | -10 | -22 |
| Hero side rail `yPercent` | 12 | 26 |
| Mori `yPercent` | ±8 | ±18 |
| Project image `yPercent` (base `scale`) | ±5 (1.12) | ±9 (1.20) |
| Section reveal `y` | 24 | 40 |
| Scrubbed tweens | `scrub: true` | `scrub: 1` (≈1s catch-up) |

Hero stats fade-out keeps its current behavior. Mori and project-image base `scale`
values grow to keep enough overflow headroom that the larger `yPercent` never reveals an
edge gap (overflow per side ≥ chosen yPercent %).

### Experience — pinned timeline (desktop only)

The Experience section is a two-part layout: a heading block ("06 — Experience" + the
`#moriExperience` illustration) and the `<ol>` timeline. On desktop, **pin the heading
block** (via ScrollTrigger `pin`) so it holds in place while the `<ol>` entries scroll
past and the existing line-draw (`--tl-scale`) + active-item highlight (`is-active` /
`is-inactive`) play out. Pin ends when the timeline's bottom reaches the heading.

- Pin uses a ScrollTrigger spacer so surrounding layout does not jump.
- The existing `initTimeline` line-draw and per-item highlight are retained; only the
  heading-pin is added.
- Mobile / reduced-motion: no pin — current stacked layout, line defaults fully drawn.

### Journey — pinned scroll-driven horizontal (desktop only)

**Replace** the auto-marquee (WAAPI animation + velocity reactivity) on desktop with a
pinned horizontal scrub: pin the Journey section and tween the `.journey-track` from
`x: 0` to `x: -(trackWidth - viewportWidth)` with `scrub`, so scrolling down drags the
photo belt left — the user drives the pace.

- Uses the **9 unique slides**; the duplicated second set (which existed only to loop the
  infinite auto-marquee) is dropped from this pinned mode (hidden in the desktop branch).
- The existing auto-marquee code (`initMarquee` / `journeyMarqueeAnim` / velocity
  reactivity) is **kept but runs only on the mobile branch**; the desktop branch uses the
  pinned horizontal scrub instead. (`matchMedia` already splits desktop vs. mobile, so each
  branch sets up exactly one Journey behavior.)
- Pin length ∝ horizontal distance, recomputed on resize (`invalidateOnRefresh`).
- The Journey heading reveal is retained on both branches.
- **Mobile:** auto-marquee as today (pinned horizontal scrub is janky on touch).
- **Reduced-motion:** static; the belt is a native horizontally-scrollable (swipeable)
  overflow container, no pin, no auto-play.

## Accessibility & performance

- All new behavior gated behind `gsap.matchMedia()` reduced-motion + `min-width: 768px`
  desktop branches. Reduced-motion branch sets final state only and never initializes
  Lenis or pins.
- Lenis disabled under reduced motion (no momentum hijack for users who opted out).
- Transforms/opacity only (GPU-friendly); pins use ScrollTrigger spacers.
- `ScrollTrigger.config({ ignoreMobileResize: true })` retained; pinned/scrub triggers
  use `invalidateOnRefresh` so dimensions recompute on resize. A single
  `window load → ScrollTrigger.refresh()` (already present) covers late-loading images.
- No change to initial paint / LCP: Lenis + GSAP load `defer`-style after content; final
  states reachable without JS via retained CSS fallbacks.

## Testing / verification

Manual (no test framework). Run via a local static server so CDNs load.

0. **Prove the new bundle is running** (carryover from the earlier "looks the same"
   cache issue): DevTools → Network → "Disable cache", hard-reload, then in console
   `ScrollTrigger.getAll().length` should be a large number (pins + scrubs + reveals),
   and `typeof Lenis === 'function'`.
1. **Smooth feel:** scrolling has weighted momentum that glides to a stop; no conflict
   with the fixed header; no scroll "fighting".
2. **Anchor nav:** every nav link + mobile-menu link + hero "Scroll down" smoothly
   scrolls to the section and lands under the fixed header (correct offset).
3. **Stronger parallax:** hero/Mori/project-image depth is clearly more pronounced; no
   edge gaps on parallaxed images.
4. **Experience pin:** heading + Mori hold while the timeline scrolls/highlights and the
   line draws; releases cleanly; no layout jump.
5. **Journey pin:** scrolling down drags the photo belt sideways start→end while pinned;
   releases to the next section; heading reveals.
6. **Regression:** project modal (open/close, Esc, backdrop, focus return), theme toggle
   mid-scroll (Mori/profile swap + effects continue), contact form validation, typewriter.
7. **Reduced motion:** OS reduce-motion on → no Lenis, no pins, no horizontal hijack;
   every section visible, native scroll, no console errors.
8. **Mobile (<768px):** no pins/horizontal hijack; Journey keeps auto-marquee; reveals
   work; no horizontal overflow.
9. **CDN-blocked:** block `*gsap*` and/or `*lenis*` → full content visible, site usable,
   native scroll, no errors.

## Out of scope

- WebGL / Three.js scroll effects, cursor-reactive effects, animated counters.
- Page-transition libraries (Barba) / view transitions.
- Any redesign of layout, content, or color beyond what pinning the Experience/Journey
  sections structurally requires.
- Converting the project image hover-zoom back (scroll parallax remains the primary image
  motion on desktop, per the prior spec).
- Build tooling / bundling GSAP or Lenis locally.
