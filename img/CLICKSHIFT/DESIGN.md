---
name: Systematic Professional
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#44474e'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#75777f'
  outline-variant: '#c5c6cf'
  surface-tint: '#4e5e81'
  primary: '#031635'
  on-primary: '#ffffff'
  primary-container: '#1a2b4b'
  on-primary-container: '#8293b8'
  inverse-primary: '#b6c6ef'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#2c0e00'
  on-tertiary: '#ffffff'
  tertiary-container: '#4d1d00'
  on-tertiary-container: '#ef6c0a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#b6c6ef'
  on-primary-fixed: '#081b3a'
  on-primary-fixed-variant: '#364768'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb690'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#783200'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style
The design system is engineered for high-density utility and professional reliability. The brand personality is authoritative yet frictionless, positioning the product as a silent partner in complex logistics. 

The aesthetic leans into **Modern Corporate Minimalism** with a focus on systematic order. It utilizes a logic-driven interface where every visual element serves a functional purpose. The goal is to reduce cognitive load during data-heavy scheduling tasks through rigorous alignment, clear information hierarchy, and a restrained but meaningful use of color and depth.

## Colors
The palette is anchored by "Shift Blue" (#1A2B4B), a deep navy that communicates stability and institutional trust. "Success Teal" (#0D9488) is used strictly for positive outcomes, confirmed states, and conflict-free resolutions. 

"Alert Orange" (#F97316) serves as the primary system disruptor, used sparingly to highlight scheduling overlaps or required actions. The neutral scale is cool-toned, providing a clean scaffolding for data grids without competing with functional status indicators.

## Typography
This design system utilizes **Inter** for all primary UI interactions due to its exceptional legibility in dense interfaces. Weights are used to reinforce hierarchy: Semi-bold for structural headers and Regular for data entry.

**JetBrains Mono** is introduced as a secondary functional font for timestamps, IDs, and tabular numerical data, ensuring that "8s", "0s", and "Bs" are instantly distinguishable in high-speed scheduling environments. For mobile views, `headline-lg` scales down to 24px to maintain readability within constrained widths.

## Layout & Spacing
The layout follows a **Strict 4px Grid System**. Efficiency is prioritized through a 12-column fluid grid for main dashboards, while specific scheduling views (Gantt charts or calendars) utilize fixed-width time-slots to maintain logic.

- **Desktop:** 32px external margins; 16px gutters between data cards.
- **Tablet:** 24px margins; 12px gutters. Content reflows from 12 columns to 6.
- **Mobile:** 16px margins; 8px gutters. Sidebar navigation collapses into a bottom bar or "hamburger" menu.

## Elevation & Depth
Depth is signaled through **Tonal Layering** rather than heavy shadows. The background uses a slight off-white (#F8FAFC), while active work surfaces are pure white. 

Low-contrast outlines (1px solid #E2E8F0) define data cells and sections. Ambient shadows are reserved for floating elements like dropdowns or "Smart Logic" popovers, using a very soft, multi-layered blur: `0 4px 12px rgba(26, 43, 75, 0.08)`. This creates a subtle lift without breaking the "flat" professional aesthetic.

## Shapes
The shape language is **Soft-Square**. A standard radius of 4px (`rounded-sm`) is applied to inputs, buttons, and data cards to provide a modern feel while maintaining a disciplined, architectural structure. 

Large containers (like the main schedule view) use 8px (`rounded-lg`) to differentiate them from smaller interactive units. This minimal rounding ensures that screen real estate is used efficiently, as overly rounded corners can waste valuable pixel space in dense grids.

## Components
- **Buttons:** Primary buttons use Shift Blue with white text. Secondary buttons use a Ghost style with a 1px Shift Blue border.
- **Status Chips:** Use Success Teal for "Confirmed," Alert Orange for "Conflict," and Neutral Gray for "Draft." Labels should be in `label-caps`.
- **Input Fields:** Crisp 1px borders. On focus, the border transitions to Shift Blue with a soft 2px outer glow of the same color.
- **Data Grids:** Alternating row stripes (Zebra striping) using a 2% opacity Shift Blue for high readability in long lists.
- **Smart Logic Icons:** Small, 16px icons that appear next to scheduled items. Use Teal for "Optimized" and Orange for "Needs Attention."
- **Cards:** White background, 1px neutral-200 border, no shadow unless hovered.