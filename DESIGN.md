---
name: Warm Industrial Drafting
colors:
  surface: '#fdf8f5'
  surface-dim: '#ddd9d6'
  surface-bright: '#fdf8f5'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f7f3ef'
  surface-container: '#f1ede9'
  surface-container-high: '#ece7e4'
  surface-container-highest: '#e6e2de'
  on-surface: '#1c1b1a'
  on-surface-variant: '#4d4639'
  inverse-surface: '#31302e'
  inverse-on-surface: '#f4f0ec'
  outline: '#7f7668'
  outline-variant: '#d0c5b5'
  surface-tint: '#745a23'
  primary: '#725821'
  on-primary: '#ffffff'
  primary-container: '#8d7037'
  on-primary-container: '#fffbff'
  inverse-primary: '#e4c280'
  secondary: '#44664e'
  on-secondary: '#ffffff'
  secondary-container: '#c6ecce'
  on-secondary-container: '#4a6c54'
  tertiary: '#9b3f2c'
  on-tertiary: '#ffffff'
  tertiary-container: '#ba5642'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdea2'
  primary-fixed-dim: '#e4c280'
  on-primary-fixed: '#261900'
  on-primary-fixed-variant: '#5a430c'
  secondary-fixed: '#c6ecce'
  secondary-fixed-dim: '#aacfb3'
  on-secondary-fixed: '#00210f'
  on-secondary-fixed-variant: '#2d4e38'
  tertiary-fixed: '#ffdad3'
  tertiary-fixed-dim: '#ffb4a4'
  on-tertiary-fixed: '#3e0500'
  on-tertiary-fixed-variant: '#7f2a19'
  background: '#fdf8f5'
  on-background: '#1c1b1a'
  surface-variant: '#e6e2de'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 3.25rem
    fontWeight: '600'
    lineHeight: 3.75rem
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 2.25rem
    fontWeight: '600'
    lineHeight: 2.75rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 1.5rem
    fontWeight: '500'
    lineHeight: 2rem
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 1.25rem
    fontWeight: '500'
    lineHeight: 1.75rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: JetBrains Mono
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.625rem
    letterSpacing: -0.005em
  body-md:
    fontFamily: JetBrains Mono
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: 0em
  body-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: 0.01em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.125rem
    letterSpacing: 0.04em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.08em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 3rem
  margin-tablet: 2rem
  margin-mobile: 1.25rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a Warm Industrial aesthetic, blending the precision of bespoke technical hardware documentation with the tactile warmth of a master drafting studio. Tailored for analytical PC builders who prioritize transparency, engineering rigour, and digital privacy, the interface deliberately rejects aggressive gaming RGB glows, dark-mode cyberpunk tropes, and sterilised corporate templates.

The visual language draws inspiration from precision callipers, archival blueprint manuals, and bench-tested hardware schematics. It projects quiet competence, tactile physical materiality, and calibrated accuracy through:
- Warm, non-fatiguing light surfaces resembling archival draft paper and muted sand.
- Structural hairline drafting lines, registration markers, and corner brackets that anchor information grids.
- A functional taxonomy where restrained amber ochre, dusty sage, and muted terracotta provide immediate diagnostic status without sensory overload.

## Colors

The palette is strictly calibrated for light mode, emphasizing warmth, tactile distinction, and optical clarity.

### Functional Palette Logic
- **Primary (`#987B40`)**: Restrained Amber Ochre. Signifies indeterminate states, pending validation, warnings, active focus rings, and primary interactive hardware actions.
- **Secondary (`#4E7058`)**: Dusty Sage Green. Represents clearance, confirmed dimensional clearance, verified electrical compatibility, and authoritative confirmation.
- **Tertiary (`#BF5A45`)**: Muted Terracotta. Designates mechanical clashes, thermal envelope overages, pinout mismatches, and critical incompatibilities.
- **Neutral Surface Hierarchy**:
  - `Canvas Background`: Warm Ivory (`#F9F8F5`) transitioning to Soft Beige (`#F3EFEA`) for inset structural sections.
  - `Card / Component Fill`: Technical Pure White (`#FFFFFF`) or Soft Cream (`#FAF8F5`).
  - `Muted Shelf Surface`: Muted Sand (`#EAE4DC`) for spec summary plates and recessed trays.
  - `Hairline Borders`: Soft Sandstone (`#DCD5CB`).
- **Typography Neutrals**:
  - `Primary Text`: Deep Charcoal (`#232220`), delivering 13.5:1 contrast against Ivory canvas.
  - `Secondary Text`: Warm Slate (`#696660`), maintaining WCAG AAA compliance for auxiliary hardware specifications and labels.

## Typography

Typography balances architectural proportions with explicit engineering precision.

### Hierarchy & Pairing
- **Headlines & Section Titles (`Space Grotesk`)**: Provides geometric structure with distinct structural quirks (such as angular terminals and deliberate crossbars). Headings communicate functional authority without feeling clinical.
- **Specifications, Data, & Body (`JetBrains Mono`)**: Monospaced rendering ensures exact horizontal and vertical tabular alignment across dimensional tolerances (e.g., clearance limits, socket pinouts, wattages, thermal boundaries).
- **Labels & Tags**: Monospaced all-caps treatment with expanded letter tracking (`0.04em` to `0.08em`) to emulate punched metal spec tags and architectural drafting blueprints.

## Layout & Spacing

The layout operates on a 12-column modular drafting grid governed by structural rhythm and clear dimensional spacing.

### Drafting Canvas Model
- **Outer Margins**: Desktop relies on generous `3rem` margins to emulate expansive workbench margins. Tablet transitions to `2rem`, while mobile tightens to `1.25rem`.
- **Gutters**: Desktop and tablet preserve `1.5rem` (`24px`) gutters; mobile condenses to `1rem` (`16px`).
- **Drafting Guides**: Key structural groupings are intersected by 1px hairline divider rules in `#DCD5CB`. Components align to strict horizontal and vertical bounding lines without ambiguous drifting margins.
- **Reflow & Responsiveness**:
  - Desktop (>1024px): 12 columns. Dual-pane inspection modes (parts tray left, schematic validation canvas right).
  - Tablet (768px - 1023px): 8 columns. Vertically stacked validation reports with sticky diagnostic summary headers.
  - Mobile (<768px): 4 columns. Single-column data streams with full-bleed technical cards.

## Elevation & Depth

Visual hierarchy does not use diffuse, dark dropshadows. Depth is derived from tangible material tiers, tonal stacking, and tactile micro-borders.

### Stacking Tiers
1. **Base Layer (Canvas)**: `#F9F8F5` (Warm Ivory). Unraised background workspace.
2. **Structural Trays (Recessed Tier)**: Inset `#F3EFEA` or `#EAE4DC` with an interior 1px boundary stroke of `#DCD5CB`. Used for spec summaries and peripheral telemetry panels.
3. **Drafting Cards (Raised Tier 1)**: Solid `#FFFFFF` or `#FAF8F5` surface enclosed in a 1px solid `#DCD5CB` border, stabilized by a crisp, high-spread, low-opacity ambient drop: `0px 2px 4px rgba(35, 34, 32, 0.04), 0px 1px 2px rgba(35, 34, 32, 0.02)`.
4. **Active & Floating Drawers (Raised Tier 2)**: Elevated modals, component picker flyouts, and active compatibility overlays sit on `#FFFFFF` with a 1px `#C8C0B5` border accompanied by an anchor drop: `0px 8px 24px rgba(35, 34, 32, 0.08), 0px 2px 6px rgba(35, 34, 32, 0.04)`.

### Technical Registration Accents
High-order inspection panels feature discrete corner tick marks or 4px corner brackets printed in `#987B40` (at 40% opacity) positioned on the outer perimeter to evoke architectural drafting frames.

## Shapes

The design system enforces a pill-shaped and highly curved profile (`roundedness: 3`), blending technical precision with softer, tactile handling edges.

### Corner Rules
- **Base Surfaces & Interactive Units**: Components (buttons, input fields, tags, and small badges) utilize fully rounded radii.
- **Containers & Modules (`rounded-lg`)**: Structural cards and telemetry containers scale to pronounced curved radii.
- **Overlay Sheets (`rounded-xl`)**: Modals and slide-in panels utilize maximum smooth corner curves.
- **Forbidden Shapes**: Completely unfilleted blunt intersections (`0px`) are strictly avoided for actionable controls to preserve a machined yet ergonomically approachable feel.

## Components

### Buttons
- **Primary Action**: Solid `#987B40` fill with white `#FFFFFF` text (`JetBrains Mono`, `0.8125rem`, Medium). Fully rounded pill-like radius. Hover state transitions to `#866C36` with a crisp 1px outline offset.
- **Secondary Action**: Warm cream `#FAF8F5` background, 1px solid `#DCD5CB` border, `#232220` text. Hover transitions to `#F3EFEA` background and `#696660` border.
- **Ghost Action**: Transparent fill, `#696660` text, 1px dashed `#DCD5CB` border for secondary slot additions (e.g., `+ ADD SECONDARY M.2 DRIVE`).

### Chips & Compatibility Badges
- Built with monospaced typography (`0.6875rem`, Semi-Bold, uppercase). Radii: fully rounded. Padding: `0.25rem 0.5rem`.
- **Pass (Verified Clearance)**: `#4E7058` text over a 12% tint background (`#EEF3EF`) with a 1px `#4E7058` (30% opacity) stroke.
- **Warning / Review Needed**: `#987B40` text over `#F7F4EC` background with a 1px `#987B40` (30% opacity) stroke.
- **Fail / Incompatible**: `#BF5A45` text over `#F9EFEF` background with a 1px `#BF5A45` (30% opacity) stroke.

### Input Fields
- Background: `#FAF8F5`. 1px solid border in `#DCD5CB`. Typography: `JetBrains Mono` (`0.875rem`) in `#232220`.
- Placeholder: `#8F8A80`. Focus state: Border turns to `#987B40` with an outer, zero-blur focus ring `box-shadow: 0 0 0 1px #987B40`.
- Affixes: Monospaced units (e.g., `[mm]`, `[W]`, `[V]`) rendered in `#696660` inside the right margin.

### Checkboxes & Radio Buttons
- 16px × 16px squares with fully rounded corners for checkboxes; 16px round for radios.
- Unchecked: `#FAF8F5` surface with 1px `#DCD5CB` perimeter.
- Checked: `#987B40` solid fill with sharp `#FFFFFF` check mark icon.

### Cards & Hardware Slot Containers
- Structured with `#FFFFFF` or `#FAF8F5` surface, 1px `#DCD5CB` perimeter, and prominent rounded curvature.
- Header contains component identifier and serial spec in muted `JetBrains Mono` (`label-sm`).
- Internal divider lines use hairline 1px `#EAE4DC`.
- Clearance graphs inside cards use segmented progress lines instead of curved gradients.

### Hardware-Specific Components
- **Tolerance Clearance Bar**: Multi-segment visual ruler indicating millimeter margins (e.g., GPU length vs. Chassis radiator clearance) using muted ticks and color-coded status sections.
- **Socket Grid Matrix**: Pinout verification matrix featuring monospaced pin configurations encased in subtle geometric corner brackets.
- **Privacy Assurance Seal**: Cryptographic verification badge utilizing low-contrast hairline borders, confirming all part validation calculations are performed strictly locally in-browser.