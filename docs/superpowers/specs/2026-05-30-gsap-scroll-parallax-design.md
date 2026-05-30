# GSAP Scroll Parallax — Design Spec

**Date:** 2026-05-30
**Author:** Kyle Anthony Magalona (with Claude)
**Status:** Approved for planning

## Goal

Add expressive, tasteful scroll-driven motion to the portfolio using GSAP +
ScrollTrigger. Motion should deepen the existing minimal editorial look (hairline
borders, light weights, large display type, generous whitespace) — felt as depth
and rhythm, not as decoration. Target intensity: **medium / expressive**.

Two streams of work:

1. **Replace** the existing hand-rolled scroll code (Mori parallax, timeline
   focus, and the IntersectionObserver section reveals) with one consistent
   GSAP/ScrollTrigger system.
2. **Add** new scroll effects, prioritising **Journey**, **About/Skills**, and
   **Projects**, with a light touch on the Hero.

## Constraints

- **No build step.** Site is vanilla HTML + Tailwind (CDN) + `styles.css` +
  a single `script.js` IIFE. GSAP must load from CDN via `<script>` tags.
- **Accessibility first.** `prefers-reduced-motion: reduce` currently disables
  all motion; this must be preserved. Reduced motion = content appears in final
  state with no transforms.
- **Don't break what works.** Fixed header, anchor navigation, the project modal
  (focus trap + `Esc`), theme toggle, and the contact form must remain
  unaffected.
- **Light/dark themes** both supported; animations must not depend on a specific
  theme.
- **Mobile.** Effects must degrade gracefully; heavy parallax is desktop-first,
  matching the existing `max-width: 767px` opt-outs.

## Foundation: Approach A — GSAP core + ScrollTrigger, native scroll

Chosen over Lenis smooth-scroll (extra dependency, momentum-scroll/focus risk)
and ScrollSmoother (wrapper transform conflicts with the fixed header).

- Load from CDN **before** `script.js`:
  - `gsap` (3.13+)
  - `ScrollTrigger`
- Register once: `gsap.registerPlugin(ScrollTrigger)`.
- All animation authored inside `script.js`, wrapped in `gsap.context()` for
  clean scoping/teardown.
- Responsive + reduced-motion handled with `gsap.matchMedia()`:
  - `(prefers-reduced-motion: no-preference)` and a desktop breakpoint
    (`min-width: 768px`) gate the parallax-heavy effects.
  - The reduced-motion / mobile branches set final states immediately (no
    tweens), so nothing is left hidden.
- The "smooth" feel comes from **scrub** (`scrub: true` / a small numeric value),
  not from a smooth-scroll library.

## Architecture

`script.js` stays a single IIFE. Introduce a clear internal structure:

```
(() => {
  // 1. existing non-scroll logic: theme, menu, typewriter, modal, form, year
  // 2. const reduceMotion = ...   (already present)
  // 3. if (window.gsap && window.ScrollTrigger && !reduceMotion) {
  //      gsap.registerPlugin(ScrollTrigger);
  //      const ctx = gsap.context(() => {
  //        const mm = gsap.matchMedia();
  //        mm.add({ desktop: "(min-width: 768px)", reduced: "(prefers-reduced-motion: reduce)" }, (c) => {
  //          const { desktop, reduced } = c.conditions;
  //          if (reduced) return;       // appear-only, no tweens
  //          initHero(desktop);
  //          initAboutSkills(desktop);
  //          initJourney(desktop);
  //          initProjects(desktop);
  //          initMori(desktop);
  //          initTimeline(desktop);
  //          initSectionReveals();
  //        });
  //      });
  //    } else {
  //      // no GSAP or reduced motion: ensure everything visible (current fallback)
  //    }
})();
```

Each `initX` is a small named function with one responsibility. The existing
IntersectionObserver-based section reveal, the RAF Mori parallax, and the RAF
timeline-focus code are **removed** and reimplemented as `initSectionReveals`,
`initMori`, and `initTimeline`.

### Removed / migrated existing code

| Current code | Fate |
|---|---|
| `IntersectionObserver` section reveal (`.reveal` / `.is-visible`) | Reimplemented as `initSectionReveals` (ScrollTrigger batch). CSS `.reveal`/`.is-visible` rules retained as the reduced-motion/no-JS fallback. |
| Mori RAF parallax (`updateMori`, `moriObserver`, scroll listener) | Reimplemented as `initMori` (ScrollTrigger scrub on `#moriExperience`, `#moriContact`). |
| Timeline focus RAF (`updateTimelineActive`, scroll listener) | Reimplemented as `initTimeline` (ScrollTrigger). |
| Journey marquee (Web Animations API) | **Kept**, but `initJourney` adds scroll-velocity reactivity to its `timeScale`. |
| Typewriter, modal, form, theme, menu | **Untouched.** |

## Per-section animation design

### Hero (light touch)
- Portrait (`#profileImg` / `#profileImg2` wrapper) drifts up slightly slower
  than scroll — small `yPercent` scrub for depth.
- Side rail ("Information Systems / 2026") parallaxes gently.
- Stats row fades/translates out as the hero leaves the viewport (scrub).
- Typewriter untouched. Hover image-swap untouched.

### About / Skills (`#about`, `#skills`)
- About heading lines ("Student." / "Project lead." / "Builder.") reveal line by
  line — `y` + opacity + clip, staggered, triggered on enter.
- About paragraphs fade/translate in on enter.
- Skills grid cells stagger in (opacity + small scale, e.g. 0.98 → 1) so the
  hairline grid reads as "assembling."
- Optional: tiny scrub speed difference between the two skills text columns for
  depth.

### Journey (`#journey`)
- Keep the auto-marquee and hover-pause.
- Make the belt **scroll-velocity reactive**: map `ScrollTrigger` scroll velocity
  to the animation's `timeScale` so it speeds up while scrolling and eases back
  to idle (target ~1) when scrolling stops.
- Light intra-frame parallax on each slide's `<img>` (image slightly oversized,
  small `y`/`scale` shift) so slides have internal depth.
- Heading + intro copy reveal on enter.

### Projects (`#projects`)
- Project cards rise + fade with stagger as the grid enters
  (ScrollTrigger batch).
- Each project image gets scale/translate parallax **inside its frame** on scroll
  (image sized > frame, `y`/`scale` scrub). This becomes the primary image
  motion; the existing hover `group-hover:scale-105` is kept or dialed back to
  avoid fighting the scroll motion.
- Heading + intro copy reveal on enter.

### Experience + Contact — Mori illustrations (`#moriExperience`, `#moriContact`)
- Replace RAF parallax with ScrollTrigger scrub (`yPercent` over the section's
  scroll range). Same visual intent, smoother, less code.
- Theme-swap of the Mori `src` (existing `syncIcons` logic) stays as-is.

### Experience — Timeline (`#experience ol`)
- Replace the RAF focus logic with ScrollTrigger.
- The left border line "draws" (scaleY 0 → 1) as the section scrolls.
- The entry nearest the focus line highlights (`is-active`) and others dim
  (`is-inactive`) — same classes/intent as today, driven by ScrollTrigger so it
  scrubs smoothly. Dots animate on activation.

## Accessibility & performance

- All scroll motion gated behind `gsap.matchMedia()` reduced-motion + breakpoint
  branches. Reduced-motion branch sets final state only.
- Transforms/opacity only (GPU-friendly); avoid animating layout properties.
- `ScrollTrigger.config({ ignoreMobileResize: true })` and
  `invalidateOnRefresh` where dimensions matter (Journey offset, Mori range).
- `gsap.context()` scopes selectors and enables teardown if ever needed.
- No change to initial paint / LCP: GSAP loads `defer`-style after content; final
  states are reachable without JS via retained CSS fallback rules.

## Testing / verification

Manual verification (no test framework in repo):

1. **Reduced motion:** OS "reduce motion" on → load site → every section fully
   visible, no transforms, no console errors. Marquee idles or is static.
2. **Desktop full motion:** scroll top→bottom → hero depth, About/Skills reveals,
   Journey velocity reaction, Projects card stagger + image parallax, Mori drift,
   timeline draw + active highlight all fire smoothly; no jank.
3. **Mobile (<768px):** heavy parallax off; reveals still work or content simply
   appears; no horizontal overflow.
4. **Light + dark:** run both; Mori/profile theme swaps still work mid-scroll.
5. **Regression:** anchor nav jumps to correct offsets under the fixed header;
   project modal opens/closes with `Esc` and focus return; contact form
   validates; theme toggle works.
6. **No-JS / CDN-blocked:** if GSAP fails to load, content is fully visible
   (CSS fallback) — verify by blocking the CDN.

## Out of scope

- Lenis / ScrollSmoother smooth-scrolling (noted as a possible future upgrade).
- Horizontal pinned scroll, cursor-reactive effects, animated counters.
- Any redesign of layout, content, or color.
- Build tooling / bundling GSAP locally.
