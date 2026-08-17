# React Migration Plan — Portfolio (Static → Vite + React + TypeScript)

> **How to use this file:** When you're ready to start, tell me *"read REACT_MIGRATION_PLAN.md and begin the React migration"* (optionally name a phase, e.g. "do Phase 2"). I'll execute it phase by phase with verification checkpoints. **No code is written until then.**

---

## 0. Verdict — Is it possible?

**Yes, and it's a clean fit.** The current site is already component-shaped:

- Clear, self-contained `<section>` blocks (hero, about, journey, skills, projects, services, experience, philosophy/quote, contact) → each becomes a React component.
- Animations already live in isolated `init*()` functions inside one IIFE in `script.js` → each maps to a `useGSAP`/`useEffect` hook in its component.
- Styling is Tailwind utility classes + a `styles.css` of custom properties → Tailwind moves to a build step, `styles.css` ports over almost unchanged.

The only real *work* (not risk) is rewriting DOM lookups (`getElementById`/`querySelector`) as React refs, and wiring GSAP/Lenis cleanup so they behave under React's lifecycle.

**Chosen stack (from planning):**
- **Vite + React** (client-rendered SPA — closest 1:1 to today's static site)
- **TypeScript**
- **Faithful 1:1 port** — identical visuals & behavior; no redesign

---

## 1. Target Tech Stack

| Concern | Today | After migration |
|---|---|---|
| Build/dev | None (static files) | **Vite** (`npm run dev` / `build`) |
| Framework | Vanilla JS | **React 18** + **TypeScript** |
| Styling | Tailwind **CDN** + inline `tailwind.config` | **Tailwind via PostCSS** (`tailwind.config.ts`, `@tailwind` directives) |
| Custom CSS | `styles.css` (CSS vars, keyframes) | `src/styles/globals.css` (same content) |
| Animation | GSAP 3.13 + ScrollTrigger (CDN) | **`gsap`** npm + **`@gsap/react`** (`useGSAP`) |
| Smooth scroll | Lenis 1.1.20 (CDN) | **`lenis`** npm + **`lenis/react`** (`<ReactLenis>`) |
| Icons | `iconify-icon` web component (CDN) | **`@iconify/react`** `<Icon />` (no web component) |
| Fonts | Google Fonts `<link>` (Inter) + `Aronik TRIAL` | Same `<link>` in `index.html` (verify Aronik asset) |
| Theme | Inline no-flash script + class on `<html>` | Same inline script in `index.html` + React `ThemeProvider` |
| Hosting | Static host | **Vercel** (static build output) |

**New dependencies:**
```
react react-dom
gsap @gsap/react
lenis
@iconify/react
-D vite @vitejs/plugin-react typescript @types/react @types/react-dom
-D tailwindcss postcss autoprefixer
```

---

## 2. Proposed Project Structure

```
portfolio/
├─ index.html                 # Vite entry; keep no-flash theme script + font links in <head>
├─ package.json
├─ tsconfig.json
├─ vite.config.ts
├─ tailwind.config.ts         # ports the current inline tailwind.config
├─ postcss.config.js
├─ public/
│  └─ img/                    # move ALL current img/ assets here (served at /img/...)
└─ src/
   ├─ main.tsx                # ReactDOM root, imports globals.css
   ├─ App.tsx                 # <ReactLenis root> + ThemeProvider + page layout
   ├─ styles/
   │  └─ globals.css          # = current styles.css (CSS vars, keyframes, component classes)
   ├─ lib/
   │  ├─ gsap.ts              # registerPlugin(ScrollTrigger) once; export gsap, ScrollTrigger
   │  └─ useReducedMotion.ts  # matchMedia('(prefers-reduced-motion)')
   ├─ context/
   │  └─ ThemeContext.tsx     # dark/light state synced to <html class> + localStorage
   ├─ data/                   # extracted content (typed)
   │  ├─ projects.ts          # project cards + modal detail (currently in script.js)
   │  ├─ experience.ts        # timeline entries
   │  ├─ skills.ts            # skill groups + icon names
   │  ├─ services.ts          # services list
   │  └─ journey.ts           # journey slides
   ├─ components/
   │  ├─ Header.tsx           # nav, theme toggle, mobile menu, "Book A Call"
   │  ├─ MobileMenu.tsx
   │  ├─ Footer.tsx
   │  ├─ ProjectModal.tsx     # modal driven by React state (no getElementById)
   │  └─ ui/Icon.tsx          # thin wrapper around @iconify/react
   └─ sections/
      ├─ Hero.tsx             # typewriter, profile image hover, stats, "View CV" link
      ├─ About.tsx
      ├─ Journey.tsx          # pinned horizontal scrub / marquee
      ├─ Skills.tsx
      ├─ Projects.tsx         # grid → opens ProjectModal
      ├─ Services.tsx
      ├─ Experience.tsx       # timeline + Mori parallax image
      ├─ QuoteInterlude.tsx   # the "Creating Efficient Systems…" reveal
      └─ Contact.tsx          # contact form + status
```

---

## 3. The Core Pattern: Porting GSAP/ScrollTrigger to React

This is the heart of the migration. Today every animation queries the DOM globally and runs once on `DOMContentLoaded`. In React, each animation is **scoped to its component's ref and cleaned up on unmount.**

**Before (`script.js`):**
```js
function initQuote(isDesktop) {
  const section = document.getElementById('philosophy');
  const words = section.querySelectorAll('.quote-word');
  ScrollTrigger.create({ trigger: section, /* … */ });
}
```

**After (`QuoteInterlude.tsx`):**
```tsx
import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import { gsap, ScrollTrigger } from '../lib/gsap';

export function QuoteInterlude() {
  const root = useRef<HTMLElement>(null);

  useGSAP(() => {
    const words = gsap.utils.toArray<HTMLElement>('.quote-word', root.current!);
    const mm = gsap.matchMedia();
    mm.add({ isDesktop: '(min-width: 768px)', isMobile: '(max-width: 767px)' }, (ctx) => {
      // … same reveal logic as initQuote, using `words` and root.current …
    });
  }, { scope: root });   // useGSAP auto-reverts/cleans up on unmount

  return <section id="philosophy" ref={root} className="quote-interlude …"> … </section>;
}
```

**Why `@gsap/react`'s `useGSAP`:** it runs the animation inside a `gsap.context` scoped to `root`, and **auto-reverts all tweens/ScrollTriggers on unmount and on dependency change** — which also makes it safe under React 18 StrictMode double-invoke (the #1 GSAP-in-React footgun).

**Rules for every ported animation:**
1. One `useGSAP(() => {…}, { scope: rootRef })` per section component.
2. Replace all `document.getElementById/querySelector` with refs or scoped `gsap.utils.toArray`.
3. Keep the existing `gsap.matchMedia()` desktop/mobile split exactly as-is.
4. Call `ScrollTrigger.refresh()` after images load (see §5 Journey/Mori).
5. Preserve `history.scrollRestoration = 'manual'` (set once in `App`/`main`).

---

## 4. Smooth Scroll (Lenis) in React

Today: `new Lenis()` + `gsap.ticker.add(time => lenis.raf(time*1000))` + anchor-link interception.

After: wrap the app once and let GSAP drive the RAF loop.
```tsx
// App.tsx
import { ReactLenis, useLenis } from 'lenis/react';

<ReactLenis root options={{ lerp: 0.1, smoothWheel: true, autoRaf: false }}>
  {/* set up gsap.ticker -> lenis.raf in a small effect, and
      ScrollTrigger.update on lenis 'scroll' (same as today) */}
  <Page />
</ReactLenis>
```
- Anchor `href="#section"` smooth scroll → a `useLenis` helper or keep the header offset logic in a click handler.
- Reduced-motion / no-GSAP fallback: skip Lenis and the GSAP reveals; render sections in their final visible state (matches today's `.reveal.is-visible` fallback).

---

## 5. Section-by-Section Notes (gotchas)

- **Hero** — typewriter is a `setInterval`/timeout effect (`useEffect` + cleanup); profile image crossfade is pure CSS `group-hover` (keep as-is); "View CV" link → `<a href="/img/Magalona_Resume (1)-1.png">` (asset in `public/img`).
- **Journey** — pinned horizontal scrub + marquee; **most animation-heavy**. Port carefully; needs `ScrollTrigger.refresh()` after slide images load. Marquee pause-on-hover → React handlers on the slider ref. Keep `refreshPriority` ordering note from the current code.
- **Projects** — grid of cards open a **modal**. Today the modal is one hidden DOM block populated via `getElementById`. **Rewrite as React:** `useState<Project | null>(selected)`; `<ProjectModal project={selected} onClose={…} />`. Project content moves to `src/data/projects.ts`. Handle `Escape` key + backdrop click + body scroll lock in the modal component.
- **Experience** — timeline reveal synced to a rail line; plus the "Mori" image parallax popping from the right. Both are ScrollTriggers → standard port. Mori images go in `public/img`.
- **QuoteInterlude** — already designed data-driven (`N = words.length`); trivial port (see §3). CSS-sticky desktop pin needs no JS pin, so no downstream-trigger surprises.
- **Contact** — form currently does client-side `submit` handling + status message. Port to controlled inputs + `onSubmit`. (If you later want real submissions, wire an action/endpoint — out of scope for the faithful port.)
- **Theme toggle** — keep the inline no-flash script in `index.html <head>` verbatim (it must run before paint). The React toggle reads/writes `localStorage.theme` and toggles `document.documentElement.classList`.
- **Mobile menu** — `useState(open)` + the same markup; close on link click.
- **Footer** — has its own reveal trigger ("show on first Contact arrival"); preserve that trigger.
- **Icons** — replace every `<iconify-icon icon="lucide:database" />` with `<Icon icon="lucide:database" />` from `@iconify/react`. Same icon names (`lucide:*`, `simple-icons:*`, `devicon-plain:*`) work. Remove the web-component CDN script and the FOUC CSS rule for it.

---

## 6. Migration Phases (execution order)

Each phase is independently verifiable in the browser. We migrate into a **new `portfolio/` subfolder (or new branch)** so the current site keeps working until cutover.

- [ ] **Phase 0 — Scaffold.** `npm create vite@latest` (React + TS). Add deps (§1). Configure Tailwind (PostCSS), port inline `tailwind.config` → `tailwind.config.ts`, move `styles.css` → `src/styles/globals.css`, copy no-flash theme script + font links into `index.html`. Move `img/` → `public/img/`. *Verify: blank styled page, dark/light toggle of `<html>` class works, fonts load.*
- [ ] **Phase 1 — App shell.** `main.tsx`, `App.tsx` with `ThemeProvider` + `ReactLenis` + `lib/gsap.ts` (registerPlugin, manual scrollRestoration). Header + Footer + empty section placeholders. *Verify: nav renders, theme toggle works via React, smooth scroll active, no console errors.*
- [ ] **Phase 2 — Static sections (no heavy animation).** Port Hero (incl. typewriter, View CV), About, Skills, Services, QuoteInterlude. Extract their data to `src/data/*`. *Verify: visuals match current site; quote reveal scrubs.*
- [ ] **Phase 3 — Projects + modal.** `Projects.tsx` + `ProjectModal.tsx` (React state) + `data/projects.ts`. *Verify: cards open modal, Escape/backdrop close, scroll lock, content correct.*
- [ ] **Phase 4 — Animation-heavy sections.** Journey (pinned scrub/marquee) and Experience (timeline + Mori parallax), incl. `ScrollTrigger.refresh()` on image load and refresh-priority ordering. *Verify: pinning, scrub, parallax, and downstream sections fire at correct positions; reload mid-page behaves.*
- [ ] **Phase 5 — Fallbacks & a11y.** Reduced-motion path (final-state render, no Lenis), `prefers-reduced-motion`, focus/ARIA on modal & mobile menu, `sr-only` text. *Verify: with reduce-motion on, everything is legible and static.*
- [ ] **Phase 6 — Build & deploy.** `npm run build`, preview, fix any SSR-free build issues; deploy to Vercel (framework preset: Vite). *Verify: production build matches dev; CV link & images resolve.*
- [ ] **Phase 7 — Cutover.** Replace repo root with the React app (or merge the branch), update README, archive the old static files. (Tag the last static commit first.)

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| React 18 **StrictMode** double-mounts effects → duplicate ScrollTriggers | Use `useGSAP({ scope })` (auto-cleanup). Optionally disable StrictMode during initial port, re-enable after. |
| ScrollTrigger positions wrong because images load late | `ScrollTrigger.refresh()` on `window` load + per-image `onload`; `invalidateOnRefresh: true` on pinned triggers (already used today). |
| Lenis + ScrollTrigger fighting over RAF | Single ticker: `gsap.ticker.add(t => lenis.raf(t*1000))`, `autoRaf:false`, `ScrollTrigger.update` on lenis scroll (mirror current code). |
| `Aronik TRIAL` font not actually bundled | Confirm whether a font file exists; if not, it already falls back to Inter — document and keep fallback. |
| Tailwind **CDN → build** purges classes built dynamically | Ensure `content` globs in `tailwind.config.ts` cover `index.html` + `src/**/*.{ts,tsx}`; avoid constructing class names from runtime strings. |
| Filename with spaces (`Magalona_Resume (1)-1.png`) | Works URL-encoded; consider renaming to `magalona-cv.png` during the move for cleaner URLs. |

---

## 8. What stays effectively unchanged
- All Tailwind utility classes in markup (copy into JSX; `class` → `className`, `for` → `htmlFor`, self-close tags).
- `styles.css` contents (CSS variables, `@keyframes`, `.journey-*`, `.quote-*`, `.skill-*`, Mori clip rules).
- The animation **logic** (math, easings, scrub mappings, matchMedia breakpoints) — only the *DOM access* and *lifecycle wiring* change.
- Theme behavior, color tokens, dark mode.

---

## 9. Rough effort estimate
- Phase 0–1: ~1 sitting (scaffold + shell).
- Phase 2–3: ~1–2 sittings (most sections + modal).
- Phase 4: ~1 sitting (the tricky animations).
- Phase 5–7: ~1 sitting (polish + deploy + cutover).

Estimates assume faithful port with browser verification between phases (no automated tests in this project).

---

### To begin
Tell me: **"Read REACT_MIGRATION_PLAN.md and start Phase 0"** (or "start the React migration"). I'll work in a new folder/branch so the live static site stays intact until Phase 7 cutover.
