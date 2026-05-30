---
name: ClauseGuard
colors:
  surface: '#121317'
  surface-dim: '#121317'
  surface-bright: '#38393e'
  surface-container-lowest: '#0d0e12'
  surface-container-low: '#1a1b20'
  surface-container: '#1f1f24'
  surface-container-high: '#292a2e'
  surface-container-highest: '#343439'
  on-surface: '#e3e2e8'
  on-surface-variant: '#c3c6d7'
  inverse-surface: '#e3e2e8'
  inverse-on-surface: '#2f3035'
  outline: '#8d90a0'
  outline-variant: '#434655'
  surface-tint: '#b4c5ff'
  primary: '#b4c5ff'
  on-primary: '#002a78'
  primary-container: '#2563eb'
  on-primary-container: '#eeefff'
  inverse-primary: '#0053db'
  secondary: '#c6c6cd'
  on-secondary: '#2e3036'
  secondary-container: '#47494f'
  on-secondary-container: '#b7b8bf'
  tertiary: '#ffb596'
  on-tertiary: '#581e00'
  tertiary-container: '#bc4800'
  on-tertiary-container: '#ffede6'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b4c5ff'
  on-primary-fixed: '#00174b'
  on-primary-fixed-variant: '#003ea8'
  secondary-fixed: '#e2e2e9'
  secondary-fixed-dim: '#c6c6cd'
  on-secondary-fixed: '#1a1b21'
  on-secondary-fixed-variant: '#45474c'
  tertiary-fixed: '#ffdbcd'
  tertiary-fixed-dim: '#ffb596'
  on-tertiary-fixed: '#360f00'
  on-tertiary-fixed-variant: '#7d2d00'
  background: '#121317'
  on-background: '#e3e2e8'
  surface-variant: '#343439'
typography:
  headline-xl:
    fontFamily: IBM Plex Mono
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: IBM Plex Mono
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: IBM Plex Mono
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  headline-sm:
    fontFamily: IBM Plex Mono
    fontSize: 18px
    fontWeight: '500'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28.8px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 25.6px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22.4px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 2rem
  card-gap: 1.5rem
  section-margin: 4rem
  gutter: 1rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style
The brand personality is authoritative yet approachable, tailored for legal and technical precision. The design system follows a **Modern Corporate** aesthetic with a strong emphasis on **Minimalism** and "Breathable High-Density." The interface prioritizes clarity over decoration, using expansive whitespace to reduce cognitive load during complex document analysis. 

The emotional response should be one of calm confidence and absolute reliability. By stripping away unnecessary shadows and heavy dividers, the UI directs all focus toward the content. The style utilizes a dark, sophisticated palette with sharp, functional typography to evoke a "premium tool" feel for professionals.

## Colors
This design system utilizes a deep, layered dark theme to provide visual depth without relying on traditional shadows. 

- **Primary (Electric Cobalt):** Reserved strictly for primary actions, focus states, and critical status indicators. Use sparingly to maintain its impact.
- **Background:** The base layer uses a deep charcoal (#0B0C10) to ground the interface.
- **Surface & Surface-Bright:** Cards and containers use #16181D, while elevated elements like tooltips or active toggles use #21242C.
- **Borders:** All structural separation is handled by a low-contrast #262932 border. This replaces shadows to maintain a flat, architectural feel.

## Typography
The typographic system creates a clear distinction between "System Data" and "User Content." 

- **Headlines:** IBM Plex Mono is used for all headings to reflect the technical and precise nature of legal clauses. It should be used with tight letter-spacing in larger sizes.
- **Body:** Inter is the workhorse for all prose and document text. A generous line-height of 1.6 (160%) is mandatory to ensure readability in dense legal documents.
- **Labels:** Use Inter Bold in uppercase for small metadata labels to ensure they are distinct from body text.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy for document viewing areas and a **Fluid** model for dashboard views. 

- **Global Padding:** Standardize on 32px (2rem) for internal card padding and main container margins to create "breathable" space.
- **Vertical Rhythm:** Use a strict 8px-based scale. For high-density data, use `stack-sm` (8px). For standard content blocks, use `stack-lg` (32px).
- **Desktop:** 12-column grid with 24px gutters.
- **Mobile:** 4-column grid with 16px margins. Headings should scale down significantly (e.g., Headline-XL becomes 28px).

## Elevation & Depth
This design system avoids traditional box shadows in favor of **Tonal Layers** and **Subtle Outlines**. 

Depth is communicated through color stepping:
1. **Level 0 (Base):** #0B0C10 (App background).
2. **Level 1 (Cards):** #16181D with a 1px solid border of #262932.
3. **Level 2 (Modals/Popovers):** #21242C with a 1px solid border of #262932.

By removing shadows, the interface feels faster, cleaner, and more intentional. Focus states for inputs should use the primary cobalt as a 1px ring rather than a glow.

## Shapes
The shape language is "Rounded" and approachable while maintaining a professional edge. Components use a baseline 8px (0.5rem) radius to soften the technical nature of the interface.

- **Small Components:** 8px radius (Checkboxes, Tags).
- **Standard Components:** 16px radius (Buttons, Input fields).
- **Large Components:** 24px radius (Main content cards).

## Components
- **Buttons:** Primary buttons use a solid #2563EB fill with white text. Secondary buttons use a transparent fill with a #262932 border.
- **Input Fields:** Use #16181D background with a #262932 border. On focus, the border changes to #2563EB.
- **Cards:** Cards are the primary container. Use 32px (2rem) padding for content-heavy cards and 24px for simple data cards. No shadows; use the defined border tokens and the increased corner radius.
- **Lists:** Use subtle horizontal dividers (#262932) only. Remove all outer borders for list items to keep the view "open."
- **Chips/Tags:** Use IBM Plex Mono at 12px for tags to differentiate them from body text. Use a #21242C background.
- **Legal Clauses:** Specialized component with a left-accent border (2px cobalt) when selected or flagged, ensuring high-density information remains scannable.