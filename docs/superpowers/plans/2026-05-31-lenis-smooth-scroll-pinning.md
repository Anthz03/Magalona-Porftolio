# Lenis Smooth Scroll + Pinning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the portfolio a "Tenity-class" scroll experience — smooth/inertia scrolling (Lenis), stronger parallax depth, a pinned Experience heading, and a scroll-driven horizontal Journey belt — building on the existing GSAP + ScrollTrigger system.

**Architecture:** Add Lenis (CDN) for smooth scrolling and bridge it to ScrollTrigger so all scroll effects stay in sync. Push existing parallax magnitudes up. Restructure Experience into a 2-column layout with a CSS-`sticky` heading. Replace the desktop Journey auto-marquee with a ScrollTrigger pin + horizontal scrub (8 unique slides), keeping the auto-marquee for mobile only. Everything stays gated behind `gsap.matchMedia()` reduced-motion + desktop branches; reduced-motion/CDN-blocked paths fall back to native scroll with all content visible.

**Tech Stack:** Vanilla HTML, Tailwind (CDN), `styles.css`, `script.js` (IIFE), GSAP 3.13 + ScrollTrigger (CDN), **Lenis 1.x (CDN)**. No build step. No automated test framework — each task is verified with `node --check script.js` plus manual browser checks.

**Reference:** Spec at `docs/superpowers/specs/2026-05-31-lenis-smooth-scroll-pinning-design.md`.

---

## Conventions for this plan

- **"Verify" steps** mean: serve the site (`npx serve` in the project root so the CDNs load), open `http://localhost:3000` with DevTools console open, and observe the described behavior. "No console errors" is part of every verify step.
- **Cache discipline:** before every visual verify, in DevTools → Network tick **"Disable cache"** and hard-reload (Ctrl+Shift+R). (This avoids the earlier "looks the same" stale-bundle confusion.)
- **Commits** use the project style. On Windows PowerShell use one `-m` per line:
  ```
  git commit -m "subject" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
  ```
- All new JS goes **inside the IIFE** in `script.js`. Transform/opacity only.
- After each task: `node --check script.js` must pass before committing.

---

## File Structure

- **Modify `index.html`** — add the Lenis CDN `<script>` before `script.js` (~line 676); restructure the `#experience` section into a 2-column grid (~lines 504–553).
- **Modify `script.js`** — add Lenis bootstrap + ScrollTrigger bridge in the `hasGsap && !reduceMotion` block; add anchor-nav interception; bump parallax magnitudes in `initHero`/`initMori`/`initProjects`/`initSectionReveals`; rework Journey (`initJourney` + the top-level marquee block) into desktop-pinned-horizontal vs mobile-marquee.
- **Modify `styles.css`** — add the recommended Lenis classes; add `#experience` sticky-column rules; hide Journey duplicate slides on desktop; ensure `.journey-slider { overflow: hidden }`.

No new files.

---

## Task 1: Load Lenis and bootstrap smooth scroll

**Files:**
- Modify: `index.html` (before the GSAP tags / `script.js`, ~line 676)
- Modify: `script.js` (inside `if (hasGsap && !reduceMotion) {`, ~line 365, before `gsap.context`)
- Modify: `styles.css` (append the Lenis recommended CSS)

- [ ] **Step 1: Add the Lenis CDN tag**

In `index.html`, immediately before the existing GSAP script tags (currently at ~line 676), add Lenis first so it is defined before `script.js` runs:

```html
    <script src="https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js" defer></script>
    <script src="script.js" defer></script>
```

(Only the Lenis line is new; the three existing lines stay in this order.)

- [ ] **Step 2: Add the Lenis recommended CSS**

Append to the end of `styles.css`:

```css
/* ── Lenis smooth scroll ─────────────────────────────── */
html.lenis,
html.lenis body {
    height: auto;
}

.lenis.lenis-smooth {
    scroll-behavior: auto !important;
}

.lenis.lenis-smooth [data-lenis-prevent] {
    overscroll-behavior: contain;
}

.lenis.lenis-stopped {
    overflow: hidden;
}

.lenis.lenis-smooth iframe {
    pointer-events: none;
}
```

- [ ] **Step 3: Bootstrap Lenis and bridge it to ScrollTrigger**

In `script.js`, find the block `if (hasGsap && !reduceMotion) {` (~line 365). Immediately after `ScrollTrigger.config({ ignoreMobileResize: true });` and **before** `gsap.context(() => {`, insert:

```javascript
        // ---- Lenis smooth scroll (progressive enhancement) ----
        // Drives the real page scroll (no wrapper transform), so the fixed
        // header and ScrollTrigger pinning keep working. Bridged to GSAP.
        const hasLenis = typeof window.Lenis !== 'undefined';
        let lenis = null;
        if (hasLenis) {
            lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
            lenis.on('scroll', ScrollTrigger.update);
            gsap.ticker.add((time) => lenis.raf(time * 1000));
            gsap.ticker.lagSmoothing(0);
        }
```

Note: `lenis` is declared in the `if (hasGsap && !reduceMotion)` scope so Task 2's anchor handler (added in the same scope) can read it.

- [ ] **Step 4: `node --check`**

Run: `node --check script.js`
Expected: no output (exit 0).

- [ ] **Step 5: Verify smooth scroll**

Serve + hard-reload (cache disabled). Expected: scrolling has a weighted, glides-to-a-stop momentum feel; the fixed header stays put; existing reveals/parallax still fire; no console errors. In console, `typeof Lenis` → `"function"` and `ScrollTrigger.getAll().length` → a non-zero number.

- [ ] **Step 6: Verify fallbacks**

- OS reduce-motion on → no smooth scroll (block skipped), native scroll, all content visible, no errors.
- DevTools Network → block `*lenis*`, reload → GSAP effects still run on native scroll, no errors (`hasLenis` false).

- [ ] **Step 7: Commit**

```bash
git add index.html script.js styles.css
git commit -m "feat: add Lenis smooth scroll bridged to ScrollTrigger" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Route anchor navigation through Lenis

Lenis intercepts wheel/scroll, so in-page anchor jumps must go through `lenis.scrollTo` with an offset for the fixed header, or they land at the wrong position.

**Files:**
- Modify: `script.js` (inside `if (hasGsap && !reduceMotion) {`, after the Lenis bootstrap from Task 1)

- [ ] **Step 1: Add the anchor interception**

In `script.js`, directly after the Lenis bootstrap block (Task 1 Step 3), still inside `if (hasGsap && !reduceMotion)` and before `gsap.context`, add:

```javascript
        // Route in-page anchor links through Lenis so they land under the
        // fixed header. The header is the fixed top nav; read its height live.
        if (lenis) {
            const header = document.querySelector('header');
            document.querySelectorAll('a[href^="#"]').forEach((link) => {
                link.addEventListener('click', (event) => {
                    const id = link.getAttribute('href');
                    if (!id || id === '#') return;
                    const target = document.querySelector(id);
                    if (!target) return;
                    event.preventDefault();
                    const offset = header ? -header.offsetHeight : 0;
                    lenis.scrollTo(target, { offset });
                });
            });
        }
```

Note: confirmed — the fixed nav is `<header class="fixed top-0 left-0 right-0 z-50 …">` at `index.html:41`, so `document.querySelector('header')` resolves to it. The guard leaves native behavior intact if it were ever null.

- [ ] **Step 2: `node --check`**

Run: `node --check script.js`
Expected: no output (exit 0).

- [ ] **Step 3: Verify anchor nav**

Serve + hard-reload. Click each top-nav link, each mobile-menu link, and the hero "Scroll down" link. Expected: each smoothly scrolls (with momentum) to its section and lands with the section heading visible **below** the fixed header (not hidden under it). No console errors.

- [ ] **Step 4: Verify fallback**

OS reduce-motion on → links use native jump (Lenis not initialized), still land correctly. No errors.

- [ ] **Step 5: Commit**

```bash
git add script.js
git commit -m "feat: route anchor navigation through Lenis with header offset" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Stronger parallax depth

Push the magnitudes of the existing effects and add `scrub` smoothing so scrubbed tweens glide with the momentum.

**Files:**
- Modify: `script.js` (`initSectionReveals`, `initHero`, `initMori`, `initProjects`)
- Modify: `styles.css` (`#projects … img` base scale)

- [ ] **Step 1: Increase the section-reveal offset**

In `script.js` `initSectionReveals`, change the pre-set and the tween target offset from `24` to `40`:

Find:
```javascript
        gsap.set(els, { autoAlpha: 0, y: 24 });
```
Change to:
```javascript
        gsap.set(els, { autoAlpha: 0, y: 40 });
```

(The `onEnter` tween already animates `y: 0`, so only the from-state changes.)

- [ ] **Step 2: Increase hero magnitudes and add scrub smoothing**

In `initHero`, change the portrait `yPercent: -10` → `-22`, the side-rail `yPercent: 12` → `26`, and the three hero `scrub: true` → `scrub: 1`:

Find the portrait tween's `yPercent: -10,` → `yPercent: -22,`.
Find the side-rail tween's `yPercent: 12,` → `yPercent: 26,`.
In all three hero `scrollTrigger` objects, change `scrub: true` → `scrub: 1`.

- [ ] **Step 3: Increase Mori magnitude and scrub smoothing**

In `initMori`, change `{ yPercent: -8 }` → `{ yPercent: -18 }`, `yPercent: 8,` → `yPercent: 18,`, and `scrub: true,` → `scrub: 1,`.

- [ ] **Step 4: Increase project-image magnitude, scrub smoothing, and base scale**

In `initProjects`, the per-card image `gsap.fromTo`: change `{ yPercent: -5 }` → `{ yPercent: -9 }`, `yPercent: 5,` → `yPercent: 9,`, and `scrub: true,` → `scrub: 1,`.

In `styles.css`, change the project-image base scale to keep ≥9% overflow headroom each side:

Find:
```css
#projects article .relative.overflow-hidden img {
    transform: scale(1.12);
    transition: none;
}
```
Change `scale(1.12)` → `scale(1.20)`.

- [ ] **Step 5: `node --check`**

Run: `node --check script.js`
Expected: no output (exit 0).

- [ ] **Step 6: Verify stronger depth**

Serve + hard-reload (desktop, wide window). Expected: hero portrait/side-rail drift is clearly more pronounced; Mori illustrations drift further; project images shift more within their frames **with no edge gaps**; scrubbed motion glides (≈1s catch-up) rather than tracking instantly. No console errors.

- [ ] **Step 7: Verify fallbacks**

Reduced motion → static, all visible. Mobile → desktop-only parallax still skipped, no horizontal overflow.

- [ ] **Step 8: Commit**

```bash
git add script.js styles.css
git commit -m "feat: increase parallax depth and add scrub smoothing" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Pin the Experience heading (2-column sticky layout)

Restructure `#experience` into a desktop 2-column grid: a left column holding the heading (which becomes `sticky`) and a right column holding the timeline `<ol>`. On `<lg` it stacks as today. This implements the spec's "pin the heading" via CSS `sticky` — robust with Lenis and consistent with the site's existing `grid-cols-12` sections.

**Files:**
- Modify: `index.html` (`#experience`, ~lines 506–552)

- [ ] **Step 1: Restructure the Experience markup**

In `index.html`, replace the heading `<div>` + `<ol>` (currently the block starting `<div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 mb-16">` through the `</ol>`) with a 2-column grid. Replace:

```html
            <div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16 mb-16">
                <div class="lg:col-span-7">
                    <p class="text-xs uppercase tracking-[0.3em] text-secondary">05 — Experience</p>
                    <h2 class="mt-4 text-4xl md:text-5xl lg:text-6xl font-light leading-[0.95] tracking-tight">
                        A short timeline.
                    </h2>
                </div>
            </div>

            <ol class="relative z-10 ml-2 md:ml-4">
```

with:

```html
            <div class="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-16">
                <div class="lg:col-span-4">
                    <div class="lg:sticky lg:top-28">
                        <p class="text-xs uppercase tracking-[0.3em] text-secondary">05 — Experience</p>
                        <h2 class="mt-4 text-4xl md:text-5xl lg:text-6xl font-light leading-[0.95] tracking-tight">
                            A short timeline.
                        </h2>
                    </div>
                </div>

                <ol class="lg:col-span-7 relative z-10 ml-2 md:ml-4">
```

Then move the existing `</ol>` so it closes this grid: after the last `</li>` (the Letrán entry), the structure must be `</ol>` then a new `</div>` closing the grid, then `</section>`. Concretely, replace the existing:

```html
                </li>
            </ol>
        </section>
```

with:

```html
                </li>
            </ol>
            </div>
        </section>
```

- [ ] **Step 2: Verify the pin (sticky heading)**

Serve + hard-reload (desktop, wide window). Expected: as you scroll through Experience, the "05 — Experience / A short timeline." heading **holds in place** (sticky, just below the fixed header at `top-28` ≈ 7rem) while the six timeline entries scroll past on the right and the line draws + active item highlights. The heading releases when the section ends. No layout jump; `#moriExperience` still sits in the section.

- [ ] **Step 3: Verify fallbacks / regression**

- `<lg` (mobile/tablet): the columns stack — heading on top, timeline below (no sticky). No horizontal overflow.
- Reduced motion: layout intact, line fully drawn, no errors.
- Confirm the timeline `<ol>` still has its `--tl-scale` line (`#experience ol::before`) and `is-active` highlight working after the restructure.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "feat: pin Experience heading via 2-column sticky layout" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Journey — pinned scroll-driven horizontal (desktop), marquee on mobile

Replace the desktop auto-marquee with a ScrollTrigger pin + horizontal scrub across the 8 unique slides. Keep the auto-marquee for mobile only.

**Files:**
- Modify: `styles.css` (hide duplicate slides on desktop; ensure `.journey-slider { overflow: hidden }`)
- Modify: `script.js` (gate the top-level marquee block to mobile; rewrite `initJourney`'s desktop path)

- [ ] **Step 1: CSS — hide the duplicate slides on desktop and confirm overflow**

The belt has 8 unique slides followed by 8 duplicates (the duplicates exist only for the infinite mobile marquee loop). On desktop the pinned scrub uses the 8 unique slides, so hide the rest. Append to `styles.css`:

```css
/* Desktop Journey runs as a pinned horizontal scrub over the 8 unique
   slides; the duplicate loop set (used only by the mobile auto-marquee)
   is hidden at >=768px. */
@media (min-width: 768px) {
    .journey-slide:nth-child(n + 9) {
        display: none;
    }
}
```

`.journey-slider` already clips horizontally (confirmed: `styles.css:103` has `overflow: hidden;` plus an edge `mask-image` fade), so no change is needed there — the horizontal scrub belt will fade nicely at both edges.

- [ ] **Step 2: Gate the existing auto-marquee block to mobile**

In `script.js`, find the top-level marquee guard:

```javascript
    if (journeySlider && journeyTrack && journeySection && !reduceMotion) {
```

Change it to only run below the desktop breakpoint:

```javascript
    const journeyIsMobile = window.matchMedia('(max-width: 767px)').matches;
    if (journeySlider && journeyTrack && journeySection && !reduceMotion && journeyIsMobile) {
```

(Leave the rest of that block — `initMarquee`, the `journeyObserver`, hover pause/play — unchanged. It now only powers mobile.)

- [ ] **Step 3: Rewrite `initJourney` for the desktop pinned horizontal**

Replace the current `initJourney` function body's effects **2a (velocity)** and **2b (intra-frame img parallax)** with a desktop pinned horizontal scrub; keep **2c (heading reveal)**. Replace the whole `function initJourney(isDesktop) { ... }` with:

```javascript
    function initJourney(isDesktop) {
        const section = document.getElementById('journey');
        if (!section) return;

        // Desktop: pin the section and scrub the belt horizontally with scroll.
        if (isDesktop) {
            const slider = section.querySelector('.journey-slider');
            const track = section.querySelector('.journey-track');
            if (slider && track) {
                const distance = () => Math.max(0, track.scrollWidth - slider.clientWidth);
                gsap.to(track, {
                    x: () => -distance(),
                    ease: 'none',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top top',
                        end: () => '+=' + distance(),
                        pin: true,
                        scrub: 1,
                        anticipatePin: 1,
                        invalidateOnRefresh: true,
                    },
                });
            }
        }

        // Heading + intro reveal — scoped to the header div so it doesn't
        // grab the slide caption <p>s inside the belt. (Both branches.)
        const header = section.querySelector(':scope > div');
        const heads = header ? header.querySelectorAll('h2, p') : [];
        if (heads.length) {
            gsap.from(heads, {
                autoAlpha: 0,
                y: 20,
                duration: 0.6,
                ease: 'power2.out',
                stagger: 0.06,
                scrollTrigger: { trigger: section, start: 'top 80%', once: true },
            });
        }
    }
```

Note: the `journeyMarqueeAnim` variable is now only used by the mobile marquee block; leave its `let journeyMarqueeAnim = null;` declaration in place (harmless on desktop). The velocity-reactivity code is intentionally removed (it depended on the marquee that no longer runs on desktop).

- [ ] **Step 4: `node --check`**

Run: `node --check script.js`
Expected: no output (exit 0).

- [ ] **Step 5: Verify desktop pinned horizontal**

Serve + hard-reload (desktop, wide window). Expected: reaching Journey, the section **pins** and scrolling down drags the photo belt **leftwards** from the first to the last of the 8 photos; the belt only moves while you scroll (you drive the pace); each photo appears once (no duplicates); the section releases to Skills/Projects when the belt finishes; the heading reveals on enter. No console errors, no vertical jump on pin (`anticipatePin` helps).

- [ ] **Step 6: Verify mobile + fallbacks**

- `<768px` (device emulation): the auto-marquee runs as before (loops, hover/touch behavior), no pin, all slides visible. No horizontal page overflow.
- Reduced motion: no marquee, no pin; the belt is static. All content reachable. No errors.
- Confirm anchor nav to `#skills`/`#projects`/`#contact` (which sit after the pinned Journey) still lands correctly — the pin adds scroll length, so re-verify offsets.

- [ ] **Step 7: Commit**

```bash
git add script.js styles.css
git commit -m "feat: pinned scroll-driven horizontal Journey on desktop, marquee on mobile" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Full regression + refresh pass

**Files:**
- Verify only (the `window load → ScrollTrigger.refresh()` is already present from the prior plan; confirm it covers the new pins).

- [ ] **Step 1: Confirm refresh covers pins**

In `script.js`, confirm the line `window.addEventListener('load', () => ScrollTrigger.refresh());` exists inside the `if (hasGsap && !reduceMotion)` block (added by the prior plan's Task 9). The new pins (Journey) and `invalidateOnRefresh` tweens (Mori, Journey distance) rely on it for accurate positions after images load. No code change expected; if it is missing, add it after the `gsap.context(...)` call.

- [ ] **Step 2: Prove the new bundle is running (cache-proof)**

DevTools → Network → "Disable cache" ON → hard-reload. In console:
- `typeof Lenis` → `"function"`
- `ScrollTrigger.getAll().length` → a non-zero number that now includes the Journey pin (e.g., noticeably higher than before Task 5).

- [ ] **Step 3: Desktop full walkthrough**

Hard-reload at desktop width. Scroll top→bottom slowly then quickly, then jump via every nav anchor (About, Journey, Skills, Services, Experience, Contact). Expected:
- Smooth momentum throughout; fixed header stable.
- All effects fire at correct positions after the load refresh; the Experience heading pins (sticky) and the Journey belt pins + scrubs horizontally.
- Anchor links land under the fixed header at the correct offset, including sections after the pinned Journey.
- No console errors, no layout jumps, no horizontal scrollbar.

- [ ] **Step 4: Cross-cutting regression**

- Project modal: open each, close via `Esc`, backdrop, and X — focus returns to the trigger.
- Theme toggle mid-scroll (in Experience and Contact): Mori/profile `src` swaps; effects continue.
- Contact form: empty (error), bad email (error), valid (success).
- Mobile menu: open/close; anchor click closes it and scrolls correctly.
- Typewriter still cycles.

- [ ] **Step 5: Reduced-motion full pass**

OS reduce-motion on, reload. Expected: no Lenis, no pins, no horizontal hijack; every section visible; Experience heading not sticky-trapping content; Journey belt static; native scroll; no console errors.

- [ ] **Step 6: Mobile pass (<768px)**

Device emulation. Expected: smooth scroll may apply (Lenis is not desktop-gated, only reduced-motion-gated) but **no pins / no horizontal hijack**; Journey auto-marquee runs; reveals work; no horizontal overflow.

- [ ] **Step 7: CDN-blocked pass**

Block `*lenis*` then (separately) `*gsap*` in Network, reload each time. Expected: with Lenis blocked → effects run on native scroll; with GSAP blocked → full static content, native scroll, all visible; no errors either way.

- [ ] **Step 8: Commit (if any fixes were needed)**

```bash
git add -A
git commit -m "chore: verify Lenis + pinning regression and refresh coverage" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

(If Step 1 found nothing to change and no fixes were needed, skip the commit.)

---

## Self-Review (completed by plan author)

**Spec coverage:**
- Smooth/inertia scroll (Lenis + ScrollTrigger bridge) → Task 1 ✓
- Anchor nav under Lenis with header offset → Task 2 ✓
- Stronger parallax depth (magnitudes + scrub smoothing) → Task 3 ✓
- Pinned Experience heading → Task 4 ✓ (CSS sticky 2-col; satisfies spec intent — chosen over ScrollTrigger pin for robustness with Lenis)
- Pinned Journey → scroll-driven horizontal, marquee on mobile → Task 5 ✓
- Accessibility / reduced-motion / mobile / CDN-blocked fallbacks → gated throughout + Task 6 ✓
- "Prove the new bundle runs" cache check → Task 1 Step 5, Task 6 Step 2 ✓
- Refresh coverage for late images / pins → Task 6 Step 1 ✓

**Placeholder scan:** No TBD/TODO; each code step shows the exact change. The one conditional (Task 6 Step 8 commit) is genuinely conditional and explained.

**Type/name consistency:** `lenis` (declared Task 1 Step 3, used Task 2 Step 1), `hasLenis`, `journeyMarqueeAnim` (kept, mobile-only), `initJourney(isDesktop)`, the `#projects … img` scale rule (1.12 → 1.20), `--tl-scale` line untouched. Journey desktop selectors (`.journey-slider`, `.journey-track`, `.journey-slide`) match `index.html` and `styles.css`.

**Open risks flagged for the implementer:**
- Pin + fixed header: `start: 'top top'` pins the Journey section at the viewport top, partially under the fixed header; the section's `py-24` padding keeps content clear, but verify no important content hides under the header during the pin (Task 5 Step 5). If it does, change `start` to `'top top+=96'` (header height).
- Resizing across the 768px breakpoint mid-session is not fully reconciled (the top-level mobile marquee block reads the viewport once at load); a reload is the supported path. Acceptable for a portfolio.
- (Resolved) `header` selector in Task 2 — confirmed `<header>` at `index.html:41`; `.journey-slider` overflow — confirmed at `styles.css:103`.
