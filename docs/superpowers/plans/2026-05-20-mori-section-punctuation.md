# Mori Section Punctuation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three chibi-style Mori illustrations as small decorative medallions between sections of a static portfolio site, with float animation, dark-mode-safe rendering, and reduced-motion support.

**Architecture:** Pure HTML + CSS additions to a vanilla static site (no frameworks, no build step). One reusable CSS pattern (`.mori-break` / `.mori-medallion`) drives all three placements; HTML inserts three `<div>` blocks between specific `<section>` elements in `index.html`. A small optional JS addition wires up subtle scroll parallax via the existing `IntersectionObserver` pattern already used in `script.js`.

**Tech Stack:** Vanilla HTML, Tailwind utility classes (loaded via CDN — `tailwind.config` is defined inline in `index.html`), plain CSS in `styles.css`, vanilla JS in `script.js`. No package manager, no test framework. Verification is visual (open `index.html` in a browser) and via `git status` / `git log`.

**Verification Note:** This codebase has no automated tests. "Test" steps below are visual browser checks. After each task, open `index.html` in a browser (file:// is fine), scroll to the affected section, and confirm the described visual outcome in both light and dark mode (use the floating moon/sun toggle in the bottom-right corner).

**Spec:** `docs/superpowers/specs/2026-05-20-mori-section-punctuation-design.md`

**Files touched:**
- `styles.css` — append Mori CSS block (Task 1)
- `index.html` — insert three medallion blocks (Tasks 2, 3, 4)
- `script.js` — append parallax IntersectionObserver (Task 5, optional)

---

### Task 1: Add base CSS for Mori medallion pattern

**Files:**
- Modify: `styles.css` (append at end, before the `@media (prefers-reduced-motion: reduce)` block already at the bottom — we will merge our reduced-motion overrides INTO that existing block)

- [ ] **Step 1: Open `styles.css` and locate the existing `@media (prefers-reduced-motion: reduce)` block**

It starts around line 302 and contains entries like `.reveal { ... }`, `.typewriter-cursor { ... }`, etc. We will insert new Mori CSS BEFORE this block and add one entry INSIDE it for the float animation.

- [ ] **Step 2: Insert the Mori CSS block immediately before the existing `@media (prefers-reduced-motion: reduce)` block**

Paste the following block right after the `.theme-transitioning` block (around line 300) and before the `@media (prefers-reduced-motion: reduce)` line:

```css
/* ── Mori medallions (section punctuation) ─────────────── */
.mori-break {
    position: relative;
    width: 100%;
    pointer-events: none;
    margin-top: -3.5rem;
    margin-bottom: -1rem;
    display: flex;
    z-index: 2;
}

.mori-break.is-center  { justify-content: center; }
.mori-break.is-right   { justify-content: flex-end;   padding-right: 12%; }
.mori-break.is-left    { justify-content: flex-start; padding-left: 12%; }

.mori-medallion {
    position: relative;
    width: 5.5rem;
    height: 5.5rem;
    border-radius: 9999px;
    background: #ffffff;
    border: 1px solid rgba(34, 34, 34, 0.08);
    box-shadow:
        0 4px 12px rgba(34, 34, 34, 0.06),
        0 16px 36px rgba(34, 34, 34, 0.06);
    overflow: hidden;
    animation: mori-float 5.5s ease-in-out infinite;
    will-change: transform;
}

.mori-break.is-right  .mori-medallion { animation-delay: -1.8s; }
.mori-break.is-left   .mori-medallion { animation-delay: -3.4s; }

.mori-medallion::before {
    content: '';
    position: absolute;
    inset: -1.5rem;
    background: radial-gradient(circle, rgba(34, 34, 34, 0.05), transparent 70%);
    z-index: -1;
    border-radius: 9999px;
    pointer-events: none;
}

.dark .mori-medallion {
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow:
        0 4px 12px rgba(0, 0, 0, 0.45),
        0 18px 40px rgba(0, 0, 0, 0.5);
}

.dark .mori-medallion::before {
    background: radial-gradient(circle, rgba(236, 236, 236, 0.07), transparent 70%);
}

.mori-image {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center 35%;
    mix-blend-mode: multiply;
}

.dark .mori-image {
    mix-blend-mode: multiply;
}

@media (min-width: 768px) {
    .mori-medallion { width: 6.5rem; height: 6.5rem; }
    .mori-break { margin-top: -4rem; }
}

@media (min-width: 1024px) {
    .mori-medallion { width: 7.5rem; height: 7.5rem; }
    .mori-break.is-right { padding-right: 15%; }
    .mori-break.is-left  { padding-left: 15%; }
}

@keyframes mori-float {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
}
```

Notes:
- `mix-blend-multiply` is set on `.mori-image` AND repeated under `.dark .mori-image` to defeat the existing global rule at line 251 (`.dark .mix-blend-multiply { mix-blend-mode: normal; }`). That global rule applies via the Tailwind class `mix-blend-multiply`; our element uses a custom class `.mori-image` so it's safe, but we keep both selectors explicit for clarity.
- `object-position: center 35%` shifts the framing so Mori's face/upper body shows inside the circular crop (the source images have lots of headroom).

- [ ] **Step 3: Add the float-disable rule into the existing reduced-motion block**

Inside the existing `@media (prefers-reduced-motion: reduce) { ... }` block at the bottom of `styles.css`, add this entry (anywhere inside the block — alphabetical or logical grouping is fine):

```css
    .mori-medallion {
        animation: none;
    }
```

The resulting reduced-motion block should now contain `.reveal`, `.typewriter-cursor`, `#projectModal`, `#projectModalPanel`, `.timeline-item`, `.timeline-item.is-inactive`/`.is-active`, `.timeline-dot`, AND `.mori-medallion`.

- [ ] **Step 4: Visually verify (no HTML yet, so no visible change)**

Open `index.html` in a browser. Confirm the page still loads with no console errors and no visual regressions on existing sections.

- [ ] **Step 5: Commit**

```bash
git add styles.css
git commit -m "feat: add Mori medallion CSS pattern for section punctuation"
```

---

### Task 2: Insert Mori-1 between About and Journey (centered)

**Files:**
- Modify: `index.html` — insert between the closing `</section>` of `#about` (currently line 179) and the opening `<section id="journey">` (currently line 181)

- [ ] **Step 1: Locate the join between `#about` and `#journey`**

In `index.html`, find this region (currently ~line 179–181):

```html
                </div>
            </div>
        </section>

        <section id="journey" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 2: Insert the Mori-1 medallion between the two sections**

Replace the region above with:

```html
                </div>
            </div>
        </section>

        <div class="mori-break is-center" aria-hidden="true">
            <div class="mori-medallion">
                <img src="img/Mori/Mori-1.jpg" alt="" class="mori-image" loading="lazy" />
            </div>
        </div>

        <section id="journey" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 3: Visually verify in light mode**

Open `index.html` in a browser. Scroll to the bottom of the About section. Confirm:
- A small circular medallion containing Mori-1 (curious chibi, looking up) sits centered between About and Journey.
- The medallion overlaps the section divider line vertically.
- The medallion gently bobs up and down (~8px range, ~5.5s loop).
- A faint soft halo is visible around the medallion.
- No source-image white edges leak past the circular crop.

- [ ] **Step 4: Visually verify in dark mode**

Toggle dark mode using the moon/sun button in the bottom-right corner. Confirm:
- The medallion remains a white circle (intentional — reads as a "polaroid" against the dark bg).
- Mori-1 still renders cleanly (no inverted colors, no halo around the character).
- Shadow looks correct (deeper than light mode).

- [ ] **Step 5: Verify reduced-motion behavior (optional spot check)**

In DevTools, open Rendering panel → "Emulate CSS media feature `prefers-reduced-motion`" → set to `reduce`. Confirm the medallion stops bobbing and sits still.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: add Mori-1 medallion between about and journey sections"
```

---

### Task 3: Insert Mori-3 between Services and Experience (offset right)

**Files:**
- Modify: `index.html` — insert between the closing `</section>` of `#services` (currently line 502) and the opening `<section id="experience">` (currently line 504)

- [ ] **Step 1: Locate the join between `#services` and `#experience`**

In `index.html`, find this region (currently ~line 502–504):

```html
            </ul>
        </section>

        <section id="experience" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 2: Insert the Mori-3 medallion offset to the right**

Replace the region above with:

```html
            </ul>
        </section>

        <div class="mori-break is-right" aria-hidden="true">
            <div class="mori-medallion">
                <img src="img/Mori/Mori-3.jpg" alt="" class="mori-image" loading="lazy" />
            </div>
        </div>

        <section id="experience" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 3: Visually verify in light mode**

Reload `index.html`. Scroll to the bottom of the Services section. Confirm:
- A medallion with Mori-3 (confident smirk chibi) sits positioned toward the right side (offset ~15% from the right edge on desktop, ~12% on tablet).
- It overlaps the section divider line.
- It bobs with a slightly different timing than Mori-1 (because of the `animation-delay: -1.8s` rule).

- [ ] **Step 4: Visually verify on mobile width**

Resize browser to <768px (or use DevTools device emulation). Confirm:
- The medallion shrinks to ~5.5rem diameter.
- It still sits at the right side (the `padding-right: 12%` rule applies on mobile too — confirm it doesn't push off-screen).
- If it looks cramped on very narrow screens (<400px), that's a known acceptable compromise.

- [ ] **Step 5: Verify in dark mode**

Toggle dark mode. Confirm clean rendering as in Task 2 Step 4.

- [ ] **Step 6: Commit**

```bash
git add index.html
git commit -m "feat: add Mori-3 medallion between services and experience sections"
```

---

### Task 4: Insert Mori-2 between Experience and Contact (offset left)

**Files:**
- Modify: `index.html` — insert between the closing `</section>` of `#experience` (currently line 552) and the opening `<section id="contact">` (currently line 554)

- [ ] **Step 1: Locate the join between `#experience` and `#contact`**

In `index.html`, find this region (currently ~line 552–554):

```html
            </ol>
        </section>

        <section id="contact" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 2: Insert the Mori-2 medallion offset to the left**

Replace the region above with:

```html
            </ol>
        </section>

        <div class="mori-break is-left" aria-hidden="true">
            <div class="mori-medallion">
                <img src="img/Mori/Mori-2.jpg" alt="" class="mori-image" loading="lazy" />
            </div>
        </div>

        <section id="contact" class="px-6 md:px-20 lg:px-28 py-24 md:py-32 border-t border-primary/5">
```

- [ ] **Step 3: Visually verify in light mode**

Reload `index.html`. Scroll to the bottom of the Experience section. Confirm:
- A medallion with Mori-2 (sincere/focused chibi with cape) sits positioned toward the left side.
- It overlaps the section divider line.
- The three medallions now form a varied rhythm down the page: center (about/journey), right (services/experience), left (experience/contact).

- [ ] **Step 4: Verify the overall page rhythm**

Scroll the whole portfolio from top to bottom in both light and dark mode. Confirm:
- Three Mori medallions appear at the specified locations.
- The asymmetric horizontal positioning feels intentional, not random.
- None of the medallions overlap text or buttons.
- Section content is unmodified.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: add Mori-2 medallion between experience and contact sections"
```

---

### Task 5: (Optional, recommended) Add scroll parallax for medallions

**Files:**
- Modify: `script.js` — append a new block at the bottom of the IIFE, just before the closing `})();` line (currently line 421)

This is small and self-contained. Skip this task if you want a CSS-only solution — the medallions will still float via the keyframe animation.

- [ ] **Step 1: Locate the bottom of the IIFE in `script.js`**

The file ends with `})();` on line 421 (the contact form `if (form && status) { ... }` block closes just before it).

- [ ] **Step 2: Insert the parallax block immediately before the closing `})();`**

Add this code as a new block (after the contact form block, before the final `})();`):

```javascript
    // Mori medallion parallax (subtle vertical drift on scroll)
    const moriBreaks = document.querySelectorAll('.mori-break');

    if (moriBreaks.length && !reduceMotion && 'IntersectionObserver' in window) {
        const isMobile = window.matchMedia('(max-width: 767px)').matches;

        if (!isMobile) {
            const moriState = new Map();
            let moriRafId = null;

            const updateMori = () => {
                moriState.forEach((entry, el) => {
                    const rect = el.getBoundingClientRect();
                    const viewportH = window.innerHeight || 1;
                    // Progress: 0 when the element enters the viewport bottom, 1 when it exits the top
                    const progress = 1 - (rect.top + rect.height / 2) / viewportH;
                    // Clamp + scale: ±10px range
                    const clamped = Math.max(0, Math.min(1, progress));
                    const offset = (clamped - 0.5) * 20; // -10 to +10
                    const medallion = el.querySelector('.mori-medallion');
                    if (medallion) {
                        medallion.style.setProperty('--mori-parallax', `${offset.toFixed(2)}px`);
                    }
                });
                moriRafId = null;
            };

            const moriObserver = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            moriState.set(entry.target, entry);
                        } else {
                            moriState.delete(entry.target);
                            const medallion = entry.target.querySelector('.mori-medallion');
                            if (medallion) {
                                medallion.style.removeProperty('--mori-parallax');
                            }
                        }
                    });
                },
                { rootMargin: '20% 0px 20% 0px' }
            );

            moriBreaks.forEach((el) => moriObserver.observe(el));

            window.addEventListener('scroll', () => {
                if (moriRafId) return;
                moriRafId = requestAnimationFrame(updateMori);
            }, { passive: true });
        }
    }
```

- [ ] **Step 3: Update the CSS to consume the `--mori-parallax` custom property**

In `styles.css`, find the `.mori-medallion` block (added in Task 1). Change its `animation` declaration so the parallax offset is additive to the float animation. Replace:

```css
.mori-medallion {
    position: relative;
    width: 5.5rem;
    height: 5.5rem;
    border-radius: 9999px;
    background: #ffffff;
    border: 1px solid rgba(34, 34, 34, 0.08);
    box-shadow:
        0 4px 12px rgba(34, 34, 34, 0.06),
        0 16px 36px rgba(34, 34, 34, 0.06);
    overflow: hidden;
    animation: mori-float 5.5s ease-in-out infinite;
    will-change: transform;
}
```

With:

```css
.mori-medallion {
    position: relative;
    width: 5.5rem;
    height: 5.5rem;
    border-radius: 9999px;
    background: #ffffff;
    border: 1px solid rgba(34, 34, 34, 0.08);
    box-shadow:
        0 4px 12px rgba(34, 34, 34, 0.06),
        0 16px 36px rgba(34, 34, 34, 0.06);
    overflow: hidden;
    will-change: transform;
    --mori-parallax: 0px;
    transform: translateY(var(--mori-parallax));
    transition: transform 0.18s linear;
}

.mori-medallion::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    animation: mori-float 5.5s ease-in-out infinite;
    pointer-events: none;
}
```

Wait — that approach uses pseudo-element for animation which breaks the float. Use this simpler approach instead: have the keyframe animate a separate inner wrapper. To avoid restructuring HTML, use a CSS-only solution by making the medallion's float animation update a CSS variable via custom properties (not widely supported) — easier: just nest transforms by wrapping in another element.

REVISED STEP 3 (use this instead): Modify HTML to wrap the `<img>` and instead animate the inner wrapper, OR use a simpler approach where parallax slightly modifies the `animation-play-state` or offset. Simplest: change the keyframe to use a CSS custom property for its base position:

Replace the original `.mori-medallion` and `@keyframes mori-float` blocks with:

```css
.mori-medallion {
    position: relative;
    width: 5.5rem;
    height: 5.5rem;
    border-radius: 9999px;
    background: #ffffff;
    border: 1px solid rgba(34, 34, 34, 0.08);
    box-shadow:
        0 4px 12px rgba(34, 34, 34, 0.06),
        0 16px 36px rgba(34, 34, 34, 0.06);
    overflow: hidden;
    will-change: transform;
    --mori-parallax: 0px;
    animation: mori-float 5.5s ease-in-out infinite;
}

@keyframes mori-float {
    0%, 100% { transform: translateY(var(--mori-parallax)); }
    50%      { transform: translateY(calc(var(--mori-parallax) - 8px)); }
}
```

This way, the float keyframe reads `--mori-parallax` directly, and updating the property in JS shifts the float baseline smoothly. Modern browsers (Chrome 99+, Safari 16+, Firefox 128+) animate calc() within keyframes correctly.

- [ ] **Step 4: Visually verify parallax**

Reload `index.html` in a browser at desktop width. Scroll through the page slowly. Confirm:
- Each medallion shows a subtle additional vertical drift on scroll (in addition to the natural float).
- The drift is small (~±10px range, not jarring).
- The float animation still plays.
- No jitter or layout shift.

- [ ] **Step 5: Verify mobile and reduced-motion**

- Resize to <768px: parallax should NOT activate (the JS short-circuits via the `isMobile` check). Float still works.
- Toggle reduced-motion in DevTools: both parallax AND float should stop.

- [ ] **Step 6: Commit**

```bash
git add script.js styles.css
git commit -m "feat: add subtle scroll parallax to Mori medallions"
```

---

## Self-Review Checklist (already run)

**Spec coverage:**
- ✅ 3 Mori placements between specified section pairs → Tasks 2, 3, 4
- ✅ Polaroid medallion pattern with white bg in both modes → Task 1 (`.mori-medallion`)
- ✅ Float animation + halo + thin border + shadow → Task 1
- ✅ `mix-blend-multiply` for clean source-bg rendering → Task 1 (`.mori-image`)
- ✅ `prefers-reduced-motion` guard → Task 1 Step 3, Task 5 (via `reduceMotion` flag)
- ✅ Asymmetric horizontal positioning (center/right/left) → Task 1 (`.is-center`/`.is-right`/`.is-left`), Tasks 2/3/4
- ✅ Mobile responsiveness (smaller medallion, no parallax) → Task 1 (responsive breakpoints), Task 5 (`isMobile` guard)
- ✅ Accessibility (`aria-hidden`, empty alt) → Tasks 2, 3, 4
- ✅ Optional parallax via IntersectionObserver matching existing patterns → Task 5
- ✅ No portfolio color changes outside Mori images → Confirmed (only grayscale halo, white medallion)

**Placeholder scan:** None found. All code blocks are concrete and complete.

**Type consistency:** Class names `.mori-break`, `.mori-medallion`, `.mori-image`, `.is-center`, `.is-right`, `.is-left`, custom property `--mori-parallax` used consistently across CSS and JS.

**One nuance to flag:** Task 5 Step 3 supersedes Task 1's `.mori-medallion` and `@keyframes mori-float` blocks. If skipping Task 5, leave Task 1's blocks as written. If doing Task 5, the Step 3 replacement is the final form.
