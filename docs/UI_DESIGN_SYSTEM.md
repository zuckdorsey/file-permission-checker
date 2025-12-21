# UI Design System

Design specifications for the File Permission Checker application interface.

## Color Palette

### Base Colors

| Name | Hex | Usage |
|------|-----|-------|
| Background | #0d0d0d | Main window, tables |
| Card | #141414 | Panels, cards, dialogs |
| Surface | #1a1a1a | Input fields, group boxes |
| Border Light | #1f1f1f | Primary borders |
| Border Medium | #262626 | Secondary borders |
| Border Accent | #333333 | Button borders |

### Text Colors

| Name | Hex | Usage |
|------|-----|-------|
| Primary | #e5e5e5 | Main text, headings |
| Secondary | #d4d4d4 | Body text |
| Muted | #a3a3a3 | Labels, placeholders |
| Disabled | #737373 | Disabled text |
| Subtle | #525252 | Hints, version info |

### Interactive Colors

| Name | Hex | Usage |
|------|-----|-------|
| Button BG | #333333 | Default button |
| Button Hover | #404040 | Hovered button |
| Button Pressed | #4a4a4a | Pressed button |

### Status Colors

| Status | Background | Border | Text |
|--------|------------|--------|------|
| Success | rgba(74, 222, 128, 0.15) | rgba(74, 222, 128, 0.3) | #86efac |
| Warning | rgba(251, 191, 36, 0.15) | rgba(251, 191, 36, 0.3) | #fcd34d |
| Danger | rgba(239, 68, 68, 0.15) | rgba(239, 68, 68, 0.3) | #fca5a5 |

## Typography

### Font Stack

```
'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif
```

### Font Sizes

| Size | Usage |
|------|-------|
| 22px | Splash screen title |
| 16px | Dialog headers |
| 14px | Section titles |
| 13px | Body text, buttons |
| 12px | Labels, secondary text |
| 11px | Badges, table headers |

### Font Weights

| Weight | Usage |
|--------|-------|
| 600 | Headings |
| 500 | Buttons, labels |
| 400 | Body text |

## Components

### Cards

```css
background: #141414;
border: 1px solid #1f1f1f;
border-radius: 8px;
```

### Buttons

Primary:
```css
background: #333333;
border: 1px solid #404040;
border-radius: 6px;
padding: 10px 20px;
color: #e5e5e5;
```

Secondary:
```css
background: #1f1f1f;
border: 1px solid #333333;
color: #a3a3a3;
```

### Inputs

```css
background: #0d0d0d;
border: 1px solid #262626;
border-radius: 6px;
padding: 10px 14px;
color: #e5e5e5;
```

### Tables

Header:
```css
background: #141414;
color: #a3a3a3;
text-transform: uppercase;
letter-spacing: 0.5px;
```

Rows:
```css
background: #0d0d0d;
color: #d4d4d4;
border-bottom: 1px solid #1a1a1a;
```

### Toast Notifications

| Type | Background | Border |
|------|------------|--------|
| Success | #166534 | #15803d |
| Error | #991b1b | #b91c1c |
| Warning | #854d0e | #a16207 |
| Info | #1e3a5f | #2563eb |

## Spacing

| Size | Pixels | Usage |
|------|--------|-------|
| xs | 4px | Inline spacing |
| sm | 8px | Component padding |
| md | 12px | Section spacing |
| lg | 16px | Group spacing |
| xl | 20px | Dialog margins |
| 2xl | 24px | Major sections |

## Border Radius

| Size | Pixels | Usage |
|------|--------|-------|
| sm | 4px | Badges |
| md | 6px | Buttons, inputs |
| lg | 8px | Cards, dialogs |
| xl | 12px | Splash screen |

## Shadows

```css
/* Card shadow */
box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);

/* Toast shadow */
box-shadow: 0 3px 12px rgba(0, 0, 0, 0.8);
```

## Transitions

```css
transition: all 0.15s ease;
```

## Design Principles

1. Minimalism: No unnecessary decorations
2. Contrast: Readable text on dark backgrounds
3. Consistency: Same patterns throughout
4. Subtlety: Avoid bright colors
5. Professionalism: Clean appearance
