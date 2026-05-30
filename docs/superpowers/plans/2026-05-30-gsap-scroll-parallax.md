# GSAP Scroll Parallax Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add expressive, accessible GSAP + ScrollTrigger scroll motion to the portfolio, replacing the hand-rolled scroll code with one consistent system and adding new effects to Journey, About/Skills, and Projects.

**Architecture:** Load GSAP core + ScrollTrigger from CDN before `script.js`. All scroll animation lives in `script.js` inside a single `gsap.context()`, gated by `gsap.matchMedia()` for reduced-motion + desktop breakpoint. Existing non-scroll logic (theme, menu, typewriter, modal, form) is untouched. The IntersectionObserver reveals, RAF Mori parallax, and RAF timeline focus are removed and reimplemented via ScrollTrigger; their CSS rules are retained as the reduced-motion / no-JS fallback.

**Tech Stack:** Vanilla HTML, Tailwind (CDN), `styles.css`, `script.js` (IIFE), GSAP 3.13 + ScrollTrigger (CDN). No build step. No automated test framework — each task is verified manually in the browser.

**Reference:** Spec at `docs/superpowers/specs/2026-05-30-gsap-scroll-parallax-design.md`.

---

## Conventions for this plan

- **"Verify" steps** mean: open `index.html` in a browser (or via a local static server such as `npx serve` / VS Code Live Server), open DevTools console, and observe the described behavior. "No console errors" is part of every verify step.
- **Commits** use the project's existing style (`feat:` / `refactor:` / `chore:`). End every commit message with the trailer:
  ```
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```
- On Windows PowerShell, `git commit` with a multi-line message is unreliable inline. Prefer a single `-m` per line:
  ```
  git commit -m "subject line" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
  ```
- All new scroll code goes **inside the IIFE** in `script.js`, after the existing `reduceMotion` constant (line ~75) and before the closing `})();`.
- Keep effects **transform/opacity only**. Never animate layout properties.

---

## File Structure

- **Modify `index.html`** — add two GSAP CDN `<script>` tags before `<script src="script.js"></script>` (line ~676).
- **Modify `script.js`** — add the GSAP bootstrap block; remove the three RAF/IO blocks (section reveal, Mori parallax, timeline focus); add `initHero`, `initAboutSkills`, `initJourney`, `initProjects`, `initMori`, `initTimeline`, `initSectionReveals`.
- **Modify `styles.css`** — ensure `.reveal` / `.is-visible`, `.timeline-item`, and Mori base rules remain valid as fallbacks; add any helper classes the JS targets (e.g. a hero portrait wrapper hook if needed). No visual redesign.

No new files. One IIFE, one stylesheet, one HTML file — matches the existing structure.

---

## Task 1: Load GSAP + ScrollTrigger from CDN and bootstrap

**Files:**
- Modify: `index.html` (before `<script src="script.js"></script>`, ~line 676)
- Modify: `script.js` (after the `reduceMotion` const, ~line 75)

- [ ] **Step 1: Add CDN script tags**

In `index.html`, immediately before the existing `<script src="script.js"></script>`:

```html
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/gsap.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.13.0/ScrollTrigger.min.js" defer></script>
    <script src="script.js" defer></script>
```

Note: add `defer` to the existing `script.js` tag so load order is guaranteed and parsing isn't blocked.

- [ ] **Step 2: Add the GSAP bootstrap scaffold in `script.js`**

Find the line `const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;` (~line 75). Leave it. At the **end of the IIFE**, just before the final `})();`, add:

```javascript
    // ---- GSAP scroll system ----
    const hasGsap = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

    if (hasGsap && !reduceMotion) {
        gsap.registerPlugin(ScrollTrigger);
        ScrollTrigger.config({ ignoreMobileResize: true });

        gsap.context(() => {
            const mm = gsap.matchMedia();

            mm.add(
                {
                    isDesktop: '(min-width: 768px)',
                    isMobile: '(max-width: 767px)',
                },
                (ctx) => {
                    const { isDesktop } = ctx.conditions;
                    initSectionReveals();
                    initHero(isDesktop);
                    initAboutSkills(isDesktop);
                    initProjects(isDesktop);
                    initMori(isDesktop);
                    initTimeline(isDesktop);
                    // initJourney is wired in Task 6 (depends on the marquee animation handle)
                }
            );
        });
    }

    // Stub functions — filled in by later tasks. Defined as no-ops so the
    // bootstrap runs cleanly before each effect is implemented.
    function initSectionReveals() {}
    function initHero() {}
    function initAboutSkills() {}
    function initProjects() {}
    function initMori() {}
    function initTimeline() {}
```

- [ ] **Step 3: Verify bootstrap loads**

Open `index.html` in a browser with DevTools console open.
Expected: page renders normally, no console errors, `window.gsap` and `window.ScrollTrigger` are defined (type `gsap` in console → returns the GSAP object). The stub functions run with no effect.

- [ ] **Step 4: Verify reduced-motion + CDN-blocked paths**

- Enable OS "reduce motion", reload → no errors, content fully visible (the `if (hasGsap && !reduceMotion)` block is skipped).
- In DevTools Network tab, block `*gsap*`, reload → no errors, content fully visible (`hasGsap` is false).

- [ ] **Step 5: Commit**

```bash
git add index.html script.js
git commit -m "feat: load GSAP + ScrollTrigger and add scroll-system bootstrap" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Migrate section reveals to ScrollTrigger

Replaces the existing IntersectionObserver reveal block.

**Files:**
- Modify: `script.js` — remove the IO reveal block (~lines 53–72); implement `initSectionReveals`.
- Verify: `styles.css` `.reveal` / `.is-visible` rules remain (used as reduced-motion / no-JS fallback).

- [ ] **Step 1: Remove the old IntersectionObserver reveal block**

Delete this block (currently ~lines 53–72):

```javascript
    const sectionsToReveal = document.querySelectorAll('main section, footer');
    sectionsToReveal.forEach((el) => el.classList.add('reveal'));

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver( /* ... */ );
        sectionsToReveal.forEach((el) => observer.observe(el));
    } else {
        sectionsToReveal.forEach((el) => el.classList.add('is-visible'));
    }
```

**Replace it** with a reduced-motion / no-GSAP fallback that still reveals everything, so content is never stuck hidden:

```javascript
    const sectionsToReveal = document.querySelectorAll('main section, footer');

    // When GSAP scroll motion is active, initSectionReveals() handles these.
    // Otherwise (reduced motion or GSAP unavailable) reveal immediately.
    const gsapActive =
        typeof window.gsap !== 'undefined' &&
        typeof window.ScrollTrigger !== 'undefined' &&
        !reduceMotion;

    if (!gsapActive) {
        sectionsToReveal.forEach((el) => el.classList.add('reveal', 'is-visible'));
    }
```

- [ ] **Step 2: Implement `initSectionReveals`**

Replace the `function initSectionReveals() {}` stub with:

```javascript
    function initSectionReveals() {
        const els = document.querySelectorAll('main section, footer');
        els.forEach((el) => el.classList.add('reveal'));

        ScrollTrigger.batch(els, {
            start: 'top 88%',
            onEnter: (batch) =>
                gsap.to(batch, {
                    autoAlpha: 1,
                    y: 0,
                    duration: 0.7,
                    ease: 'power2.out',
                    stagger: 0.08,
                    overwrite: true,
                }),
            once: true,
        });

        // Set the pre-animation state GSAP will tween FROM.
        gsap.set(els, { autoAlpha: 0, y: 24 });
    }
```

- [ ] **Step 3: Verify**

Reload (full motion, desktop). Expected: each section fades + rises in as it enters the viewport; sections already in view on load animate in once; no console errors. Scroll up then down — sections do not re-hide (`once: true`).

- [ ] **Step 4: Verify fallbacks**

- Reduced motion on → all sections visible immediately, no transforms.
- Block GSAP CDN → all sections visible immediately.

- [ ] **Step 5: Commit**

```bash
git add script.js
git commit -m "refactor: migrate section reveals from IntersectionObserver to ScrollTrigger" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Migrate Mori parallax to ScrollTrigger

Replaces the RAF Mori parallax block.

**Files:**
- Modify: `script.js` — remove the RAF Mori block (`moriBreaks` … scroll listener, ~lines 426–474); implement `initMori`.

- [ ] **Step 1: Remove the old RAF Mori block**

Delete the entire `const moriBreaks = document.querySelectorAll('.mori-break'); ... });` block (~lines 426–474). Note: the current code targets `.mori-break` / `.mori-medallion`, but the live markup uses `#moriExperience` and `#moriContact` (see `index.html:505,556`). The new implementation targets the real elements.

- [ ] **Step 2: Implement `initMori`**

Replace the `function initMori() {}` stub with:

```javascript
    function initMori(isDesktop) {
        if (!isDesktop) return; // heavy parallax is desktop-only
        const moris = [
            { el: document.getElementById('moriExperience'), section: document.getElementById('experience') },
            { el: document.getElementById('moriContact'), section: document.getElementById('contact') },
        ];

        moris.forEach(({ el, section }) => {
            if (!el || !section) return;
            gsap.fromTo(
                el,
                { yPercent: -8 },
                {
                    yPercent: 8,
                    ease: 'none',
                    scrollTrigger: {
                        trigger: section,
                        start: 'top bottom',
                        end: 'bottom top',
                        scrub: true,
                        invalidateOnRefresh: true,
                    },
                }
            );
        });
    }
```

- [ ] **Step 3: Verify**

Reload, scroll to Experience and Contact. Expected: each Mori illustration drifts vertically as its section scrolls through the viewport (smooth, scrubbed); no jank; no console errors. Toggle light/dark mid-scroll → the Mori `src` still swaps (existing `syncIcons`) and parallax continues.

- [ ] **Step 4: Verify fallbacks**

- Reduced motion → Mori images static, in default position.
- Mobile (<768px) → `initMori` returns early; images static.

- [ ] **Step 5: Commit**

```bash
git add script.js
git commit -m "refactor: migrate Mori parallax to ScrollTrigger scrub" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Migrate timeline focus to ScrollTrigger

Replaces the RAF timeline-focus block.

**Files:**
- Modify: `script.js` — remove the timeline RAF block (~lines 335–393); implement `initTimeline`.
- Verify: `styles.css` `.timeline-item`, `.timeline-dot`, `.is-active`, `.is-inactive` rules exist (the RAF code added these classes; reuse them).

- [ ] **Step 1: Confirm the timeline CSS classes exist**

In `styles.css`, confirm rules for `.timeline-item`, `.is-active`, `.is-inactive`, `.timeline-dot` are present (the previous RAF implementation relied on them). If absent, add minimal versions:

```css
.timeline-item { transition: opacity .4s ease, transform .4s ease; }
.timeline-item.is-inactive { opacity: .45; }
.timeline-item.is-active { opacity: 1; }
```

- [ ] **Step 2: Remove the old timeline RAF block**

Delete the block starting at `// Timeline scroll zoom` / `const timelineOl = document.querySelector('#experience ol');` through its closing `})();`-adjacent `updateTimelineActive();` call (~lines 335–393).

- [ ] **Step 3: Implement `initTimeline`**

Replace the `function initTimeline() {}` stub with:

```javascript
    function initTimeline() {
        const ol = document.querySelector('#experience ol');
        if (!ol) return;
        const items = Array.from(ol.querySelectorAll('li'));
        if (!items.length) return;

        items.forEach((item) => {
            item.classList.add('timeline-item');
            const dot = item.querySelector('span');
            if (dot) dot.classList.add('timeline-dot');
        });

        // Animate the left border line drawing in as the list scrolls.
        gsap.fromTo(
            ol,
            { '--tl-scale': 0 },
            {
                '--tl-scale': 1,
                ease: 'none',
                scrollTrigger: {
                    trigger: ol,
                    start: 'top 80%',
                    end: 'bottom 60%',
                    scrub: true,
                },
            }
        );

        // Highlight the item nearest the focus line.
        items.forEach((item) => {
            ScrollTrigger.create({
                trigger: item,
                start: 'top 55%',
                end: 'bottom 45%',
                onToggle: (self) => {
                    item.classList.toggle('is-active', self.isActive);
                    item.classList.toggle('is-inactive', !self.isActive);
                },
            });
        });
    }
```

- [ ] **Step 4: Add the drawing-line CSS**

In `styles.css`, make the timeline's left border use the `--tl-scale` variable. The list is `<ol class="... border-l ...">`. Add:

```css
#experience ol {
    position: relative;
}
#experience ol::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 1px;
    background: rgb(var(--rgb-primary) / 0.25);
    transform: scaleY(var(--tl-scale, 1));
    transform-origin: top;
}
```

If the Tailwind `border-l` on the `<ol>` visually conflicts with the `::before` line, remove `border-l` from the `<ol>` class list in `index.html:515` so only the animated line shows.

- [ ] **Step 5: Verify**

Reload, scroll through Experience. Expected: the vertical line draws from top to bottom as you scroll; the entry nearest the focus line is highlighted (`is-active`) while others dim (`is-inactive`); transitions are smooth; no console errors.

- [ ] **Step 6: Verify fallbacks**

- Reduced motion → line fully drawn (`--tl-scale` default 1), all items at full opacity, no highlight cycling.
- Mobile → still functions (timeline highlight is not desktop-gated); confirm no layout break.

- [ ] **Step 7: Commit**

```bash
git add script.js styles.css index.html
git commit -m "refactor: migrate experience timeline to ScrollTrigger with line draw" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Hero parallax (light touch)

**Files:**
- Modify: `script.js` — implement `initHero`.

- [ ] **Step 1: Implement `initHero`**

Replace the `function initHero() {}` stub with:

```javascript
    function initHero(isDesktop) {
        if (!isDesktop) return;
        const hero = document.querySelector('main > section.relative');
        if (!hero) return;

        const portrait = document.getElementById('profileImg');
        const portraitWrap = portrait ? portrait.closest('.group') : null;
        const sideRail = hero.querySelector('.\\[writing-mode\\:vertical-rl\\]')
            ? hero.querySelector('div.hidden.md\\:flex')
            : hero.querySelector('div.hidden');
        const stats = hero.querySelector('.flex.flex-wrap.gap-12');

        // Portrait drifts up slightly slower than the page.
        if (portraitWrap) {
            gsap.to(portraitWrap, {
                yPercent: -10,
                ease: 'none',
                scrollTrigger: {
                    trigger: hero,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: true,
                },
            });
        }

        // Side rail gentle parallax.
        if (sideRail) {
            gsap.to(sideRail, {
                yPercent: 12,
                ease: 'none',
                scrollTrigger: {
                    trigger: hero,
                    start: 'top top',
                    end: 'bottom top',
                    scrub: true,
                },
            });
        }

        // Stats fade out as the hero leaves.
        if (stats) {
            gsap.to(stats, {
                autoAlpha: 0,
                y: -20,
                ease: 'none',
                scrollTrigger: {
                    trigger: hero,
                    start: 'center top',
                    end: 'bottom top',
                    scrub: true,
                },
            });
        }
    }
```

Note on selectors: the hero is the first `<section class="relative">` (no `id`) in `<main>` (`index.html:84`). The side rail is the `div.hidden.md:flex` at `index.html:86`. The stats row is `div.flex.flex-wrap.gap-12` at `index.html:101`. If a selector returns null in the console, adjust to match the live class list rather than guessing — the guard clauses keep it safe either way.

- [ ] **Step 2: Verify**

Reload (desktop). Expected: as you scroll out of the hero, the portrait drifts up slightly slower than surrounding content (depth), the side rail shifts gently, and the stats fade out. Motion is subtle, not distracting. No console errors. The typewriter and hover image-swap still work.

- [ ] **Step 3: Verify fallbacks**

- Reduced motion → hero static, stats fully visible.
- Mobile → `initHero` returns early; hero static.

- [ ] **Step 4: Commit**

```bash
git add script.js
git commit -m "feat: add subtle hero scroll parallax" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Journey — scroll-velocity-reactive marquee + intra-frame image parallax

**Files:**
- Modify: `script.js` — keep the existing marquee, expose its animation handle, add `initJourney`, wire it into the `mm.add` callback.

- [ ] **Step 1: Expose the marquee animation handle**

In the existing Journey marquee block (`if (journeySlider && journeyTrack && journeySection && !reduceMotion) { ... }`, ~lines 297–333), the `initMarquee` function creates a local `anim`. Lift it to a higher scope so `initJourney` can read it. At the top of the IIFE scope (near the other element consts), add:

```javascript
    let journeyMarqueeAnim = null;
```

Inside `initMarquee`, change `const anim = journeyTrack.animate(` to `journeyMarqueeAnim = journeyTrack.animate(` and update the two `anim.pause()` / `anim.play()` references to `journeyMarqueeAnim.pause()` / `journeyMarqueeAnim.play()`.

- [ ] **Step 2: Implement `initJourney`**

Replace the (to-be-added) `function initJourney() {}` — add this stub next to the others first, then fill it:

```javascript
    function initJourney(isDesktop) {
        const section = document.getElementById('journey');
        if (!section) return;

        // 2a. Scroll-velocity reactivity: speed the marquee with scroll velocity.
        if (journeyMarqueeAnim) {
            let resetTimer = null;
            ScrollTrigger.create({
                trigger: section,
                start: 'top bottom',
                end: 'bottom top',
                onUpdate: (self) => {
                    const v = self.getVelocity();              // px/sec, signed
                    const boost = 1 + Math.min(Math.abs(v) / 1500, 3); // 1..4
                    journeyMarqueeAnim.playbackRate = boost;
                    clearTimeout(resetTimer);
                    resetTimer = setTimeout(() => {
                        journeyMarqueeAnim.playbackRate = 1;
                    }, 180);
                },
            });
        }

        // 2b. Intra-frame parallax on each slide image (desktop only).
        if (isDesktop) {
            section.querySelectorAll('.journey-slide img').forEach((img) => {
                gsap.fromTo(
                    img,
                    { yPercent: -6 },
                    {
                        yPercent: 6,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: section,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true,
                        },
                    }
                );
            });
        }

        // 2c. Heading + intro reveal.
        const heads = section.querySelectorAll('h2, p');
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

- [ ] **Step 3: Add the intra-frame parallax CSS guard**

So the image can shift inside its frame without revealing gaps, ensure the slide image is slightly oversized and the slide clips it. In `styles.css`, confirm `.journey-slide` has `overflow: hidden;` (add if missing) and bump the image scale:

```css
.journey-slide { overflow: hidden; }
.journey-slide img { transform: scale(1.06); }
```

(GSAP animates `yPercent` on top of this base scale.)

- [ ] **Step 4: Wire `initJourney` into the matchMedia callback**

In the `mm.add(...)` callback from Task 1, add the call (and remove the "wired in Task 6" comment):

```javascript
                    initJourney(isDesktop);
```

- [ ] **Step 5: Verify**

Reload (desktop). Expected:
- The marquee auto-scrolls as before; scrolling the page speeds it up and it eases back to normal speed ~0.2s after you stop.
- Each slide's image shifts subtly within its frame as the section scrolls (no white gaps at edges).
- The Journey heading + intro reveal once on enter.
- Hover still pauses the marquee. No console errors.

- [ ] **Step 6: Verify fallbacks**

- Reduced motion → the existing marquee block already self-disables under `!reduceMotion`; `initJourney` is not called (whole GSAP block skipped). Slides static.
- Mobile → marquee velocity reactivity still applies; intra-frame image parallax is skipped (`isDesktop` guard).

- [ ] **Step 7: Commit**

```bash
git add script.js styles.css
git commit -m "feat: scroll-velocity marquee and intra-frame image parallax for Journey" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: About / Skills reveals

**Files:**
- Modify: `script.js` — implement `initAboutSkills`.

- [ ] **Step 1: Implement `initAboutSkills`**

Replace the `function initAboutSkills() {}` stub with:

```javascript
    function initAboutSkills() {
        // About: stagger the heading and paragraphs.
        const about = document.getElementById('about');
        if (about) {
            const heading = about.querySelector('h2');
            const paras = about.querySelectorAll('p.text-base, .grid p.text-base, .leading-relaxed');
            if (heading) {
                gsap.from(heading, {
                    autoAlpha: 0,
                    y: 28,
                    duration: 0.7,
                    ease: 'power3.out',
                    scrollTrigger: { trigger: about, start: 'top 78%', once: true },
                });
            }
            if (paras.length) {
                gsap.from(paras, {
                    autoAlpha: 0,
                    y: 18,
                    duration: 0.6,
                    ease: 'power2.out',
                    stagger: 0.1,
                    scrollTrigger: { trigger: about, start: 'top 72%', once: true },
                });
            }
        }

        // Skills: stagger the grid cells assembling in.
        const skills = document.getElementById('skills');
        if (skills) {
            const cells = skills.querySelectorAll('.grid > .bg-tertiary');
            if (cells.length) {
                gsap.from(cells, {
                    autoAlpha: 0,
                    scale: 0.98,
                    y: 16,
                    duration: 0.5,
                    ease: 'power2.out',
                    stagger: { each: 0.06, from: 'start' },
                    scrollTrigger: { trigger: skills, start: 'top 75%', once: true },
                });
            }
        }
    }
```

Note: the skills cells are the `div.bg-tertiary` children inside the `grid ... gap-px` container (`index.html:331–360`). The `autoAlpha`/`scale` `from` tween animates toward the elements' natural state, so nothing is permanently hidden if a selector misses.

- [ ] **Step 2: Verify**

Reload (desktop). Expected: entering About, the "Student. / Project lead. / Builder." heading rises in, then paragraphs stagger in. Entering Skills, the bordered cells pop in one after another (subtle scale + rise). Each fires once. No console errors. Confirm the hairline grid (`gap-px` background) still reads correctly after animation settles.

- [ ] **Step 3: Verify fallbacks**

- Reduced motion → About + Skills fully visible, no transforms.
- Confirm on mobile the reveals still work (not desktop-gated) and there's no horizontal overflow from the `y`/`scale` from-state.

- [ ] **Step 4: Commit**

```bash
git add script.js
git commit -m "feat: add About and Skills scroll reveals" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8: Projects — card stagger + in-frame image parallax

**Files:**
- Modify: `script.js` — implement `initProjects`.
- Modify: `index.html` — optionally dial back the hover zoom on project images (~lines 401,416,431,446).

- [ ] **Step 1: Implement `initProjects`**

Replace the `function initProjects() {}` stub with:

```javascript
    function initProjects(isDesktop) {
        const section = document.getElementById('projects');
        if (!section) return;

        // Heading + intro reveal.
        const intro = section.querySelectorAll(':scope > .grid h2, :scope > .grid p');
        if (intro.length) {
            gsap.from(intro, {
                autoAlpha: 0,
                y: 20,
                duration: 0.6,
                ease: 'power2.out',
                stagger: 0.06,
                scrollTrigger: { trigger: section, start: 'top 80%', once: true },
            });
        }

        // Cards rise + fade with stagger.
        const cards = section.querySelectorAll('article.group');
        if (cards.length) {
            gsap.from(cards, {
                autoAlpha: 0,
                y: 40,
                duration: 0.7,
                ease: 'power3.out',
                stagger: 0.12,
                scrollTrigger: { trigger: section, start: 'top 72%', once: true },
            });
        }

        // In-frame image parallax (desktop only).
        if (isDesktop) {
            cards.forEach((card) => {
                const img = card.querySelector('img');
                if (!img) return;
                gsap.fromTo(
                    img,
                    { yPercent: -6 },
                    {
                        yPercent: 6,
                        ease: 'none',
                        scrollTrigger: {
                            trigger: card,
                            start: 'top bottom',
                            end: 'bottom top',
                            scrub: true,
                        },
                    }
                );
            });
        }
    }
```

- [ ] **Step 2: Ensure the image frame clips the parallax**

The project image wrappers already use `overflow-hidden` and the image is `object-cover` absolutely positioned (`index.html:400–401`). Add a base scale so the `yPercent` shift never reveals an edge. In `styles.css`:

```css
#projects article .relative.overflow-hidden img { transform: scale(1.08); }
```

- [ ] **Step 3: (Optional) reconcile the hover zoom**

The cards currently have `group-hover:scale-105` on the image (`index.html:401` etc.). With scroll parallax driving `yPercent`, the hover `scale` still composes fine, but if it visually fights, reduce to `group-hover:scale-[1.02]` on each of the four project `<img>` tags. Leave as-is if it looks good.

- [ ] **Step 4: Verify**

Reload (desktop). Expected: entering Projects, the heading/intro reveal, then the four cards rise + fade in with stagger. As you continue scrolling, each project image drifts within its frame (no edge gaps). Hover zoom still works. Clicking "View ↗" still opens the modal correctly. No console errors.

- [ ] **Step 5: Verify fallbacks**

- Reduced motion → all cards + images visible, static.
- Mobile → cards still reveal; in-frame image parallax skipped.

- [ ] **Step 6: Commit**

```bash
git add script.js styles.css index.html
git commit -m "feat: add Projects card stagger and in-frame image parallax" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9: Full regression + ScrollTrigger refresh pass

**Files:**
- Modify: `script.js` — add a refresh-on-load-complete safeguard.

- [ ] **Step 1: Refresh ScrollTrigger after images/fonts load**

Late-loading images (the Journey photos, project images, Mori) change layout and can mis-place triggers. Inside the `if (hasGsap && !reduceMotion)` block, after the `gsap.context(...)` call, add:

```javascript
        window.addEventListener('load', () => ScrollTrigger.refresh());
```

- [ ] **Step 2: Full desktop walkthrough**

Hard-reload (disable cache) at desktop width. Scroll top → bottom slowly, then fast, then jump via each nav anchor (About, Projects, Skills, Services, Experience, Contact). Expected:
- All effects fire at the correct scroll positions (no early/late triggers after the load refresh).
- Anchor links land at the correct offset under the fixed header.
- No console errors, no layout jumps, no horizontal scrollbar.

- [ ] **Step 3: Cross-cutting regression**

- Project modal: open each, close via `Esc`, backdrop click, and the X — focus returns to the trigger.
- Theme toggle: switch light/dark while scrolled into Experience and Contact — Mori `src` swaps and parallax continues; profile images swap in hero.
- Contact form: submit empty (error), bad email (error), valid (success message). 
- Mobile menu: open/close, anchor click closes it.

- [ ] **Step 4: Reduced-motion full pass**

OS reduce-motion on, reload. Expected: every section visible, no transforms, marquee static, timeline fully drawn, no console errors.

- [ ] **Step 5: Mobile pass (<768px)**

Resize / device emulation. Expected: reveals work, no heavy parallax, no horizontal overflow, marquee + velocity reaction OK, timeline OK.

- [ ] **Step 6: CDN-blocked pass**

Block `*gsap*` in Network, reload. Expected: full content visible (CSS fallback), site fully usable, no errors.

- [ ] **Step 7: Commit**

```bash
git add script.js
git commit -m "chore: refresh ScrollTrigger on load for accurate trigger positions" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Self-Review (completed by plan author)

**Spec coverage:**
- Foundation A (CDN, native scroll, matchMedia, context) → Task 1 ✓
- Replace IO reveals → Task 2 ✓
- Replace Mori RAF → Task 3 ✓
- Replace timeline RAF → Task 4 ✓
- Hero light touch → Task 5 ✓
- Journey velocity + intra-frame parallax → Task 6 ✓
- About/Skills reveals → Task 7 ✓
- Projects stagger + in-frame parallax → Task 8 ✓
- Accessibility (reduced-motion appear-only, transforms-only), perf (refresh, invalidateOnRefresh, ignoreMobileResize), CDN-blocked fallback → gated throughout + Task 9 ✓
- Manual verification checklist → per-task verify steps + Task 9 ✓

**Type/name consistency:** Function names (`initSectionReveals`, `initHero`, `initAboutSkills`, `initJourney`, `initProjects`, `initMori`, `initTimeline`) are defined as stubs in Task 1 and filled consistently in later tasks. `journeyMarqueeAnim` is declared in Task 6 Step 1 and used in the same task. `--tl-scale` is defined in Task 4 JS and consumed in Task 4 CSS.

**Placeholder scan:** No TBD/TODO; every code step shows full code; the one "optional" step (Task 8 Step 3) is genuinely optional and fully specified.

**Open risk flagged for the implementer:** Several effects rely on Tailwind utility-class selectors (hero side rail, stats, skills cells). Each has a null-guard, so a missed selector degrades to "no effect" rather than an error — but the implementer should confirm in the console that each `querySelector` resolves and adjust to the live class list if not.
