# Mori as Section Punctuation — Design Spec

**Date:** 2026-05-20
**Author:** Kyle Anthony Magalona (with Claude)
**Status:** Approved (design only, pending implementation plan)

## Goal

Integrate the three chibi-style illustrations from `img/Mori/` into the portfolio as small decorative characters that sit **between sections**, on the existing section divider lines. The result should feel like Mori is "placed everywhere" — a recurring personality motif — without disturbing section content or the portfolio's overall minimalist editorial tone.

## Non-Goals

- No restructuring of section grids or layouts.
- No color changes to the portfolio palette. The portfolio remains strictly monochrome (`#222222` / `#7B7B7B` / `#F8F8F8` light, inverted dark). Mori's rust/orange appears only inside its own illustration.
- No new pages, components, or routes.
- No changes to existing journey carousel, project modals, or theme toggle behavior.

## Placements

Mori illustrations sit at the section-border whitespace between these section pairs:

| Position | Image | Between | Reason |
|---|---|---|---|
| 1 | `Mori-1.jpg` (curious, looking up, holding orb) | `#about` → `#journey` | "Who I am" → "what I've done"; curious pose mirrors the student/learner identity above |
| 2 | `Mori-3.jpg` (confident, determined smirk) | `#services` → `#experience` | "What I offer" → "track record"; confident pose punctuates the services pitch |
| 3 | `Mori-2.jpg` (sincere/focused, with cape) | `#experience` → `#contact` | "Track record" → "let's connect"; focused expression reads as ready to listen |

Section order in the existing markup (for reference):
`hero → about → journey → skills → projects → services → experience → contact`

## Visual Treatment

Each placement uses the same component pattern: a centered (or slightly offset) decorative break that sits visually on the section divider.

### The "Mori Medallion" pattern

- **Container**: A small circular/pill-shaped white card (`bg-white` in both light and dark mode), `rounded-full`, with thin border (`border-primary/10`) and soft drop shadow.
  - White-in-dark is intentional — reads as a printed-photo or portal/badge, and sidesteps the source image's near-white background clashing with dark mode.
- **Image**: The Mori illustration inside the medallion, sized so character fits with breathing room. `mix-blend-multiply` cleans up any residual near-white pixels against the white medallion bg.
- **Size**: ~96–128px diameter (`w-24 md:w-28 lg:w-32`).
- **Halo**: A soft monochrome radial gradient pseudo-element behind the medallion (`rgba(34,34,34,0.04)` light / `rgba(236,236,236,0.06)` dark) — the only "gradient" touch, kept strictly grayscale.

### Positioning on the divider

- Each Mori sits vertically centered on the section's top border (so half overlaps the section above, half below). Implemented by placing the medallion in a container that uses negative top margin (`-mt-12` / `-mt-16`) to pull it up over the section's `border-t`.
- Horizontal positioning varies for natural variety (anti-rigidity):
  - Position 1 (about→journey): centered (`mx-auto`)
  - Position 2 (services→experience): slightly right (`ml-auto mr-[12%] md:mr-[15%]`)
  - Position 3 (experience→contact): slightly left (`mr-auto ml-[12%] md:ml-[15%]`)

### Animation

- **Float**: vertical drift `±6px` on a 5s ease-in-out infinite loop. Each Mori gets a small `animation-delay` offset so they don't all bob in sync.
- **Parallax-lite (optional, recommended)**: A small additional vertical translate (~10px range) driven by an `IntersectionObserver` or scroll listener, applied only when the element is in view. Skip on mobile to keep performance simple.
- **Reduced motion**: All animations and parallax are disabled under `prefers-reduced-motion: reduce`.

## Responsive Behavior

- **Desktop (md+)**: Mori sits on the divider with the offset described above.
- **Mobile (<md)**: All three Mori medallions are centered (`mx-auto`) regardless of desktop offset. Slightly smaller diameter (`w-20`). Float animation only (no parallax) to keep scroll performance clean.

## Accessibility

- Mori medallions are decorative. They are wrapped in `role="presentation"` containers with empty `alt=""` on the `img` tag so screen readers skip them.
- No interactive behavior — they are not clickable, not focusable.
- `prefers-reduced-motion` disables all motion as noted above.

## Files Touched

- `index.html`
  - Insert one `<div class="mori-break">…</div>` between `#about` and `#journey`
  - Insert one between `#services` and `#experience`
  - Insert one between `#experience` and `#contact`
  - No changes to section internals or grid layouts.
- `styles.css`
  - Add `.mori-break`, `.mori-medallion`, `.mori-image`, halo pseudo-element, float keyframe.
  - Add `.dark` overrides where needed (kept minimal — medallion bg stays white).
  - Add `prefers-reduced-motion` guard.
- `script.js`
  - Optional small addition: parallax IntersectionObserver for the three medallions. If skipped for simplicity, only CSS float remains — design still works.

## Out-of-Scope Considerations Acknowledged

- Could later: add a fourth Mori in the hero or as a cursor companion. Not in this spec.
- Could later: introduce a single accent color tied to Mori's rust palette. Explicitly rejected for now per user direction (strict monochrome).
- Could later: clickable Mori easter eggs / interactions. Not in this spec.

## Acceptance Criteria

1. Three Mori images appear, one each between the three specified section pairs.
2. Each sits visually on the section divider line, not inside section content.
3. Each renders cleanly in both light and dark mode without ugly white edges.
4. Each has a gentle floating animation that respects reduced-motion preferences.
5. No portfolio color changes outside the Mori images themselves.
6. Existing section content, grids, and interactions are unmodified.
7. Mobile layout remains clean and uncluttered.
