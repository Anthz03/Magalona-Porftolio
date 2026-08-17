---
name: VerifAI Core
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#454652'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#767683'
  outline-variant: '#c6c5d4'
  surface-tint: '#4c56af'
  primary: '#000666'
  on-primary: '#ffffff'
  primary-container: '#1a237e'
  on-primary-container: '#8690ee'
  inverse-primary: '#bdc2ff'
  secondary: '#006875'
  on-secondary: '#ffffff'
  secondary-container: '#00e3fd'
  on-secondary-container: '#00616d'
  tertiary: '#002108'
  on-tertiary: '#ffffff'
  tertiary-container: '#003912'
  on-tertiary-container: '#00b048'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e0e0ff'
  primary-fixed-dim: '#bdc2ff'
  on-primary-fixed: '#000767'
  on-primary-fixed-variant: '#343d96'
  secondary-fixed: '#9cf0ff'
  secondary-fixed-dim: '#00daf3'
  on-secondary-fixed: '#001f24'
  on-secondary-fixed-variant: '#004f58'
  tertiary-fixed: '#69ff87'
  tertiary-fixed-dim: '#3ce36a'
  on-tertiary-fixed: '#002108'
  on-tertiary-fixed-variant: '#00531e'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1280px
  gutter: 24px
  margin-desktop: 48px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
---

## Brand & Style

The design system is engineered for **VerifAI**, an AI-powered credibility engine. The brand personality is rooted in **Academic Authority** blended with **Modern Technical Precision**. It must evoke a sense of absolute reliability, akin to a peer-reviewed journal, but delivered with the speed and efficiency of a modern SaaS tool.

The visual style follows a **Modern Corporate** aesthetic with a **Tactile Tech** twist. It utilizes clean borders, high-contrast typography, and a "browser extension" logic—meaning information is compartmentalized into clear, functional modules. The interface prioritizes data density without sacrificing clarity, using subtle depth to separate layers of analysis.

## Colors

The palette is designed to communicate stability and success.
- **Primary (Deep Indigo):** Used for structural elements, headers, and primary actions to establish an "Academic Blue" foundation of trust.
- **Secondary (Vibrant Cyan):** Represents the "AI" layer—used for scanning animations, highlights, and active states.
- **Tertiary (Emerald Green):** Reserved exclusively for "Verified" states, high credibility scores, and success feedback.
- **Neutral:** A range of cool grays (from #F8F9FA to #212121) facilitates a clean, "paper-like" background with professional depth.

## Typography

This design system uses a triple-font approach to balance personality and utility:
- **Plus Jakarta Sans** is used for headlines to provide a modern, approachable, and slightly soft technical feel.
- **Inter** handles all body copy and UI labels, ensuring maximum readability across high-density data views.
- **JetBrains Mono** (monospaced) is used sparingly for metadata, confidence scores, and timestamps to emphasize the "calculated" and "precise" nature of the tool.

All headlines use tighter letter spacing for a more "designed" editorial appearance, while body text maintains standard tracking for accessibility.

## Layout & Spacing

The layout utilizes a **12-column Fixed Grid** for desktop dashboards and a **4-column Fluid Grid** for the browser extension and mobile views.

The rhythm is based on a **4px baseline grid**. 
- **Dashboards:** Use a "sidebar-main" pattern with a fixed 280px navigation rail.
- **Browser Extension:** Uses compact 16px internal padding to maximize the limited real estate.
- **Spacing Logic:** Components are spaced using a "Stack" philosophy—related elements use `stack-sm`, while unrelated sections use `stack-lg`.

## Elevation & Depth

To maintain a professional, academic feel, the design system avoids heavy shadows. Instead, it uses **Tonal Layering** and **Micro-Borders**:
- **Level 0 (Background):** Light gray (#F8F9FA) surface.
- **Level 1 (Cards/Modules):** White surface with a 1px solid border (#E0E0E0).
- **Level 2 (Dropdowns/Popovers):** White surface with a "Precision Shadow"—an ultra-thin 1px border combined with a soft 8px blur, 4% opacity black shadow.
- **Interaction:** Hovering over interactive cards slightly deepens the border color rather than increasing shadow depth, maintaining a "flat-but-tactile" feel.

## Shapes

The shape language is **Soft**. It avoids the playfulness of fully rounded "pill" shapes to maintain its academic seriousness.
- **Standard UI elements** (Buttons, Inputs) use a 4px (0.25rem) radius.
- **Container elements** (Cards, Sidebars) use an 8px (0.5rem) radius.
- **Status Indicators** (Credibility Chips) use a 2px radius for a sharper, more clinical look.

## Components

### Buttons
- **Primary:** Deep Indigo background, white text, 4px radius.
- **Secondary:** Transparent background, Deep Indigo 1px border.
- **Ghost:** No border or background; used for low-priority actions in high-density areas.

### Credibility Chips
Small badges used to indicate truth scores. They should feature a small icon (Check, Warning, or Info) followed by a percentage. Use Tertiary Green for scores > 80% and Primary Indigo for neutral data points.

### Input Fields
Strict, rectangular fields with 1px light gray borders. On focus, the border transitions to Vibrant Cyan. Labels should always be visible above the field using `label-sm`.

### Credibility Cards
The core unit of the UI. Features a header with the source name, a body section for the AI analysis snippet, and a footer containing "Confidence Level" metadata in JetBrains Mono.

### Data Visualizations
Charts should use a "Thin-Line" aesthetic. Use Vibrant Cyan for trends and Primary Indigo for axes and grids. Ensure all data points have a "Precision" tooltip that appears on hover.