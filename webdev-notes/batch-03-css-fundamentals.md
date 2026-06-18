# Batch 3 — CSS Fundamentals & Layout
> Making things look exactly right — and understanding why they don't when they don't.

CSS (Cascading Style Sheets) controls how HTML looks and how elements are arranged on screen. This batch covers everything from selectors to animations — the building blocks every front-end developer lives inside daily.

---

## 1. CSS Selectors

**One-line definition:** Patterns that tell the browser *which* HTML elements to style.

### Real-World Dev Example
```css
/* Element — all paragraphs */
p { color: #333; }

/* Class — reusable, multiple elements */
.btn-primary { background: blue; }

/* ID — unique element on the page */
#hero-title { font-size: 3rem; }

/* Attribute — inputs of type email */
input[type="email"] { border-color: green; }

/* Pseudo-class — link on hover */
a:hover { text-decoration: underline; }

/* Pseudo-element — first line of a paragraph */
p::first-line { font-weight: bold; }
```

### ASCII Diagram
```
HTML:  <p class="note" id="intro">Hello</p>

Selectors that match it:
  p             ← element
  .note         ← class
  #intro        ← ID
  p.note        ← combined (element + class)
  p[class]      ← attribute (has a class attr)
  p:first-child ← pseudo-class
  p::before     ← pseudo-element (injected content)
```

### Gotchas & Dev Context
- A single element can be matched by many selectors simultaneously — the most *specific* one wins (see §2).
- `:hover`, `:focus`, `:active`, `:checked` are pseudo-**classes** (state). `::before`, `::after` are pseudo-**elements** (injected content). Double-colon `::` is modern standard for elements.
- Attribute selectors support wildcards: `[href*="github"]` (contains), `[href^="https"]` (starts with), `[href$=".pdf"]` (ends with).
- Avoid over-qualifying selectors (`div.container p.text`) — it raises specificity unnecessarily and makes overrides painful.

### Production FAQ
**Q: When should I use ID selectors vs class selectors?**  
A: Almost always use classes. IDs are extremely high specificity and can only appear once per page — great for JS `getElementById`, but a headache in CSS. Reserve ID selectors for things like skip-navigation links.

**Q: What's the difference between `:nth-child(2)` and `:nth-of-type(2)`?**  
A: `:nth-child(2)` picks the element if it is *literally the 2nd child* of its parent (regardless of tag). `:nth-of-type(2)` picks the 2nd element *of that tag type* within the parent — safer for mixed-content lists.

**Q: Can I chain pseudo-classes?**  
A: Yes. `a:hover:not(.disabled)` applies hover styles only to non-disabled links.

---

## 2. Specificity & Cascade

**One-line definition:** The ruleset browsers use to decide which CSS declaration wins when multiple rules target the same element.

### Real-World Dev Example
```css
/* Specificity score: 0-0-1 (one element) */
p { color: black; }

/* Specificity score: 0-1-0 (one class) */
.intro { color: blue; }

/* Specificity score: 1-0-0 (one ID) */
#main { color: red; }

/* The paragraph below ends up RED — ID wins */
/* <p class="intro" id="main">Text</p> */
```

### ASCII Diagram
```
Specificity scored as  [ID] - [Class/Attr/Pseudo-class] - [Element/Pseudo-element]

Selector               ID   Class  Element   Score
─────────────────────────────────────────────────
p                       0     0      1       0-0-1
.nav                    0     1      0       0-1-0
.nav a                  0     1      1       0-1-1
#header                 1     0      0       1-0-0
#header .nav a          1     1      1       1-1-1
style="" (inline)       1     0      0       wins over all above
!important              ∞     —      —       nuclear option
```

### Gotchas & Dev Context
- **Cascade** = when specificity is equal, the rule declared *last* in the stylesheet wins.
- `!important` overrides everything — including inline styles. Avoid it except for utility classes (`.hidden { display: none !important; }`) or third-party overrides.
- Inherited properties (like `color`, `font-family`) trickle down from parent to child but have lower priority than any explicit rule.
- CSS Layers (`@layer`) (modern) let you control cascade order explicitly without fighting specificity.

### Production FAQ
**Q: My style isn't applying even though my selector looks right. What's happening?**  
A: Open DevTools → Elements → Computed tab. Struck-through rules lost the specificity battle. Find the winning selector and either increase your specificity or move your rule later in the file.

**Q: Is it ever okay to use `!important`?**  
A: Yes — sparingly. Good uses: utility/override classes (`.visually-hidden`), overriding poorly-scoped third-party styles (e.g., widget libraries). Bad use: as a shortcut when you're frustrated debugging specificity.

---

## 3. Box Model

**One-line definition:** Every HTML element is a rectangular box made of four layers — content, padding, border, and margin.

### Real-World Dev Example
```css
.card {
  width: 300px;        /* content width */
  padding: 16px;       /* space inside the border */
  border: 2px solid #ccc;
  margin: 24px auto;   /* space outside the border; auto = center horizontally */
  box-sizing: border-box; /* width now includes padding + border */
}
```

### ASCII Diagram
```
┌─────────────────────────────────┐
│           MARGIN                │  ← transparent, collapses with siblings
│  ┌───────────────────────────┐  │
│  │         BORDER            │  │  ← visible line
│  │  ┌─────────────────────┐  │  │
│  │  │       PADDING       │  │  │  ← background color shows through
│  │  │  ┌───────────────┐  │  │  │
│  │  │  │    CONTENT    │  │  │  │  ← text, images, child elements
│  │  │  └───────────────┘  │  │  │
│  │  └─────────────────────┘  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### Gotchas & Dev Context
- Default `box-sizing: content-box` means `width: 300px` + `padding: 16px` + `border: 2px` = **334px total**. That's a constant surprise.
- Use `box-sizing: border-box` globally — it makes `width` mean the *total visual width*. Add this to every project:
  ```css
  *, *::before, *::after { box-sizing: border-box; }
  ```
- **Margin collapse**: vertical margins between block elements merge — the larger one wins. Horizontal margins never collapse.
- `padding` can't be negative. `margin` can (pulls elements closer or offscreen).

### Production FAQ
**Q: Why is my element wider than I set it?**  
A: You're likely using the default `content-box` sizing. Switch to `border-box` and the padding/border will be absorbed into your declared width.

**Q: Why is there unexpected space between my stacked `<div>`s?**  
A: Margin collapse. Two adjacent vertical margins don't add — they merge to the larger value. Use `padding` on the parent, or add `overflow: hidden` to the parent to prevent collapse.

---

## 4. Display

**One-line definition:** The `display` property controls how an element participates in the page layout flow.

### Real-World Dev Example
```css
/* Block: full width, new line before and after */
div, p, h1 { display: block; }

/* Inline: flows with text, no width/height control */
span, a, strong { display: inline; }

/* Inline-block: flows with text BUT respects width/height */
.badge { display: inline-block; width: 80px; }

/* None: removes from layout entirely (gone, not invisible) */
.modal { display: none; }

/* Contents: element itself is invisible; children render normally */
.wrapper { display: contents; }
```

### ASCII Diagram
```
block:
[────────── full width ──────────]
[────────── next element ────────]

inline:
[span][a][strong] ← flows left-to-right like text

inline-block:
[span 80px][a][strong 80px] ← flows like inline, but respects size

none:
(nothing — removed from document flow)
```

### Gotchas & Dev Context
- `display: none` removes the element from layout (no space taken). `visibility: hidden` hides it but *keeps its space*.
- `inline` elements ignore `width`, `height`, top/bottom `margin` and `padding` (only left/right work).
- `display: contents` is useful when you need a semantic wrapper (e.g., `<ul>`) to not interfere with a Grid or Flexbox layout — but it removes accessibility roles in some browsers; use carefully.
- `display: flex` and `display: grid` are also display values — they make the element a flex/grid *container* (covered in §6–7).

### Production FAQ
**Q: My `<span>` won't take a width. Why?**  
A: `<span>` is `inline` by default. Set `display: inline-block` or `display: block` to control dimensions.

**Q: What's the difference between `display: none` and `opacity: 0`?**  
A: `display: none` — element gone, no space, not interactive. `opacity: 0` — element invisible but still occupies space and captures pointer events. `visibility: hidden` — invisible, keeps space, no pointer events.

---

## 5. Position

**One-line definition:** The `position` property controls how an element is placed in the document — in normal flow or removed from it.

### Real-World Dev Example
```css
.parent { position: relative; }  /* anchor for absolute children */

.tooltip {
  position: absolute;   /* removed from flow, placed vs nearest positioned ancestor */
  top: 100%;
  left: 0;
}

.sticky-header {
  position: sticky;
  top: 0;               /* sticks at top of viewport when scrolling */
}

.modal-overlay {
  position: fixed;      /* always relative to viewport */
  inset: 0;             /* shorthand for top/right/bottom/left: 0 */
}
```

### ASCII Diagram
```
static    → default, top/left/right/bottom have no effect
relative  → offset FROM its normal position; still takes space
absolute  → positioned vs nearest [position: relative/absolute/fixed] ancestor
fixed     → positioned vs the VIEWPORT; stays on screen when scrolling
sticky    → relative until scroll threshold, then acts like fixed
```

### Gotchas & Dev Context
- `absolute` elements look for the nearest *positioned* ancestor (anything other than `static`). If none exists, they position vs the `<html>` element.
- `position: sticky` requires a scrolling container **and** at least one of `top`/`bottom`/`left`/`right` set — otherwise it behaves like `relative`.
- `fixed` elements are excluded from normal flow; they can overlap content. Always test on mobile where viewport behavior differs.
- `z-index` only works on positioned elements (non-`static`).

### Production FAQ
**Q: My absolutely positioned element is not going where I expect.**  
A: Check what its nearest positioned ancestor is. Add `position: relative` to the intended parent if it's missing.

**Q: Sticky header stops sticking halfway down the page. Why?**  
A: The sticky element can only stick within its parent container. Once the parent scrolls out of view, sticking stops. Ensure the parent is tall enough and is the actual scroll container.

---

## 6. Flexbox

**One-line definition:** A one-dimensional layout model for arranging items in a row or column, with powerful alignment and distribution control.

### Real-World Dev Example
```css
/* Container */
.navbar {
  display: flex;
  justify-content: space-between; /* horizontal distribution */
  align-items: center;            /* vertical alignment */
  gap: 16px;
}

/* Item */
.nav-logo {
  flex: 0 0 auto;  /* don't grow, don't shrink, keep natural size */
}

.nav-links {
  flex: 1;         /* take all remaining space */
}
```

### ASCII Diagram
```
Main Axis (row) ───────────────────────────────►
┌─────────────────────────────────────────────┐
│  [Item A]    [Item B]    [Item C]            │ ↕ Cross Axis
└─────────────────────────────────────────────┘

justify-content: controls distribution along main axis
align-items:     controls alignment along cross axis
flex-direction: row | column  ← switches which axis is "main"
```

### Gotchas & Dev Context
- **Container properties**: `flex-direction`, `justify-content`, `align-items`, `align-content`, `flex-wrap`, `gap`.
- **Item properties**: `flex-grow`, `flex-shrink`, `flex-basis`, `align-self`, `order`.
- `flex: 1` is shorthand for `flex: 1 1 0` — grow, shrink, start from 0 basis. Use it for equal-width columns.
- `gap` replaces margin hacks for spacing between flex items (no unwanted outer gap).
- Flexbox is **one-dimensional** — it's best for navbars, toolbars, button groups, and card rows. For two-dimensional layouts, use Grid.

### Production FAQ
**Q: My flex items aren't wrapping to a new line.**  
A: Add `flex-wrap: wrap` to the container. Default is `nowrap`, which squishes all items onto one line.

**Q: How do I center something perfectly horizontally and vertically?**  
A: The classic two-liner:
```css
.parent { display: flex; justify-content: center; align-items: center; }
```

**Q: What does `align-content` do vs `align-items`?**  
A: `align-items` aligns items within a single row. `align-content` aligns the *rows themselves* when `flex-wrap: wrap` creates multiple lines.

---

## 7. CSS Grid

**One-line definition:** A two-dimensional layout system that lets you place elements into rows *and* columns simultaneously.

### Real-World Dev Example
```css
.dashboard {
  display: grid;
  grid-template-columns: 250px 1fr 1fr; /* sidebar + 2 equal columns */
  grid-template-rows: auto 1fr auto;    /* header, main, footer */
  grid-template-areas:
    "sidebar header  header"
    "sidebar content aside"
    "sidebar footer  footer";
  gap: 16px;
}

.site-header { grid-area: header; }
.site-sidebar { grid-area: sidebar; }
.site-content { grid-area: content; }

/* Responsive auto-fit grid of cards */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}
```

### ASCII Diagram
```
grid-template-areas layout:

┌──────────┬───────────────────────┐
│          │       header          │
│          ├────────────┬──────────┤
│ sidebar  │  content   │  aside   │
│          ├────────────┴──────────┤
│          │       footer          │
└──────────┴───────────────────────┘
```

### Gotchas & Dev Context
- `fr` (fractional unit) divides available space *after* fixed sizes are allocated — much smarter than percentages.
- `auto-fit` fills the row with as many columns as fit, collapsing empty ones. `auto-fill` keeps empty column tracks (use `auto-fit` for most card layouts).
- `minmax(250px, 1fr)` = "at least 250px wide, grow to fill remaining space."
- Grid items can overlap! Use `z-index` on grid children to control stacking.

### Production FAQ
**Q: When should I use Grid vs Flexbox?**  
A: Grid = layout (page structure, card grids, overlapping layers). Flex = component internals (navbars, button groups, form rows). They compose well — a Grid cell can contain a Flex container.

**Q: How do I make a grid item span multiple columns?**  
A: `grid-column: span 2;` or precisely: `grid-column: 1 / 3;` (from line 1 to line 3).

---

## 8. Responsive Design (Media Queries & Breakpoints)

**One-line definition:** Techniques that make a layout adapt to different screen sizes using conditional CSS rules.

### Real-World Dev Example
```css
/* Base styles (mobile) */
.container { padding: 16px; }

/* Tablet and up */
@media (min-width: 768px) {
  .container { padding: 32px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; }
}

/* Desktop and up */
@media (min-width: 1280px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Dark mode preference */
@media (prefers-color-scheme: dark) {
  body { background: #0d0d0d; color: #f0f0f0; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
```

### Gotchas & Dev Context
- Common breakpoints (not carved in stone): `480px` (phone), `768px` (tablet), `1024px` (laptop), `1280px` (desktop).
- **Always include the viewport meta tag** in HTML, or media queries won't work on mobile:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1">
  ```
- Media queries can target more than width: `orientation`, `hover`, `pointer`, `prefers-color-scheme`, `prefers-reduced-motion`.
- Tailwind CSS and Bootstrap encapsulate breakpoints as utility classes so you write fewer raw media queries.

### Production FAQ
**Q: My media query isn't triggering on a real phone even though the viewport is correct.**  
A: Check for the `<meta name="viewport">` tag. Without it, mobile browsers render at a fake ~980px width and your `min-width: 768px` query fires even on a small screen.

**Q: Should I use `min-width` or `max-width` in media queries?**  
A: Depends on your approach (see §9). Mobile-first uses `min-width` (add complexity up). Desktop-first uses `max-width` (strip complexity down). Pick one and be consistent.

---

## 9. Mobile-First vs Desktop-First

**One-line definition:** Two opposing strategies for writing responsive CSS — either you start with mobile styles and scale up, or start with desktop styles and scale down.

### Real-World Dev Example
```css
/* ── Mobile-First ── */
.sidebar { display: none; }           /* hidden on mobile */
@media (min-width: 1024px) {
  .sidebar { display: block; }        /* visible on desktop */
}

/* ── Desktop-First ── */
.sidebar { display: block; }          /* visible by default */
@media (max-width: 1023px) {
  .sidebar { display: none; }         /* hidden on mobile */
}
```

### ASCII Diagram
```
Mobile-First:
  base styles → [768px+] → [1024px+] → [1280px+]
  min-width queries ADD features

Desktop-First:
  base styles → [max 1279px] → [max 1023px] → [max 767px]
  max-width queries REMOVE features
```

### Gotchas & Dev Context
- **Mobile-first is the industry standard** for new projects. It aligns with how CSS performance works — mobile devices download and process the base (smallest) styles first.
- Desktop-first is common in legacy projects or when a design only exists as desktop mockups.
- Avoid mixing both strategies in the same codebase — it creates contradictory overrides that are hard to debug.
- Frameworks like Tailwind (`sm:`, `md:`, `lg:`) are mobile-first by design.

### Production FAQ
**Q: My design was built for desktop only in Figma. Do I have to use desktop-first?**  
A: No. You can still write mobile-first CSS — just start by thinking about what the minimal mobile version looks like, even if you have to invent it.

**Q: Which approach gives better performance?**  
A: Mobile-first. On mobile, the browser loads base styles and ignores `min-width` queries it doesn't match. Desktop-first makes mobile load desktop styles and then override them — wasted parsing.

---

## 10. CSS Variables (Custom Properties)

**One-line definition:** Named values declared in CSS that can be reused and updated anywhere in a stylesheet — like variables in code.

### Real-World Dev Example
```css
/* Declare on :root for global scope */
:root {
  --color-primary: #6366f1;
  --color-bg: #ffffff;
  --spacing-md: 16px;
  --radius: 8px;
}

.btn {
  background: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius);
}

/* Dark mode override — one block changes everything */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0d0d0d;
    --color-primary: #818cf8;
  }
}
```

### Gotchas & Dev Context
- Custom properties are **case-sensitive**: `--Color-Primary` ≠ `--color-primary`.
- They **cascade and inherit** like regular properties — a variable set on a parent is available to all its descendants, enabling component-scoped theming:
  ```css
  .card { --color-primary: coral; } /* only affects .card's subtree */
  ```
- Provide a fallback: `var(--gap, 8px)` — if `--gap` is undefined, `8px` is used.
- Unlike Sass variables, CSS variables are live in the browser — you can change them with JavaScript: `document.documentElement.style.setProperty('--color-primary', '#ff0000')`.

### Production FAQ
**Q: How are CSS variables different from Sass/LESS variables?**  
A: Sass variables are compiled away at build time — they're static. CSS variables exist in the browser, cascade, inherit, and can be changed at runtime with JS. Use both: Sass for build-time constants, CSS vars for runtime theming.

**Q: Can CSS variables hold complex values like gradients?**  
A: Yes. `--hero-bg: linear-gradient(to right, #6366f1, #8b5cf6);` then `background: var(--hero-bg);`.

---

## 11. Units (px, em, rem, vh, vw, %, ch)

**One-line definition:** CSS units determine how lengths, sizes, and spacing are measured — relative vs absolute.

### Real-World Dev Example
```css
:root { font-size: 16px; } /* 1rem = 16px sitewide */

h1 { font-size: 2rem; }    /* 32px — scales with root */
p  { font-size: 1rem; }    /* 16px */
.card { padding: 1.5em; }  /* 1.5× the card's own font-size */

.hero { height: 100vh; }   /* full viewport height */
.sidebar { width: 20vw; }  /* 20% of viewport width */

.column { width: 50%; }    /* 50% of parent element */

.input { width: 30ch; }    /* 30 character-widths of the font — great for inputs */
```

### ASCII Diagram
```
Unit   Relative to          Good for
─────────────────────────────────────────────────
px     nothing (absolute)   Borders, shadows, breakpoints
em     current element's    Component-level padding/margin
       font-size
rem    root font-size        Typography, consistent spacing
vh/vw  viewport height/width Full-screen sections
%      parent element        Fluid widths, responsive sizing
ch     width of "0" char     Input field widths
```

### Gotchas & Dev Context
- Avoid `px` for `font-size` — it ignores user browser zoom preferences. Use `rem`.
- `em` compounds: a `1.2em` element inside another `1.2em` element = `1.44em` actual. Use `rem` when you want predictable sizing.
- `vw` includes scrollbar width on some browsers — can cause horizontal scroll. Prefer `%` for widths or use `svw` (small viewport width, modern).
- `ch` is based on the `0` glyph width — approximate, but great for limiting text input width.

### Production FAQ
**Q: When should I use `em` vs `rem`?**  
A: Use `rem` for font sizes and global spacing (predictable). Use `em` for padding/margin *inside* components so they scale proportionally if the component's font size changes.

**Q: `100vh` is causing a scroll on mobile. Why?**  
A: Mobile browsers include the address bar in `100vh`. Use `100svh` (small viewport height) in modern CSS, or the JS workaround: `height: calc(var(--vh, 1vh) * 100)`.

---

## 12. Typography

**One-line definition:** CSS properties that control how text looks — font, size, spacing, and readability.

### Real-World Dev Example
```css
body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-size: 1rem;
  line-height: 1.6;          /* unitless — multiplies element's font-size */
  letter-spacing: 0.01em;
}

h1 {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: clamp(2rem, 5vw, 4rem); /* fluid type: min, preferred, max */
  line-height: 1.2;          /* tighter for headings */
  letter-spacing: -0.02em;   /* negative tracking for large headings */
}

.caption {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.1em;    /* wide tracking for small caps */
}
```

### Gotchas & Dev Context
- **Always** provide font-family fallbacks. If the web font fails to load, the user sees `system-ui` or `sans-serif` — still readable.
- `line-height: 1.6` (unitless) is preferred over `line-height: 1.6em` — unitless avoids inheritance issues with children.
- Use `clamp()` for fluid type instead of hard breakpoint overrides.
- Optimal line length for readability: 45–75 characters (`max-width: 65ch` on a text container).
- `font-display: swap` in `@font-face` prevents invisible text while fonts load.

### Production FAQ
**Q: Web fonts flash as invisible text on load. How do I fix this?**  
A: Add `font-display: swap` to your `@font-face` rule. It shows fallback font immediately, then swaps when the web font loads.

**Q: What's the difference between `letter-spacing` and `word-spacing`?**  
A: `letter-spacing` (tracking) adjusts space between all characters. `word-spacing` adjusts space between words only. Both accept negative values.

---

## 13. Colors (Hex, RGB, HSL, oklch)

**One-line definition:** CSS supports multiple color syntaxes — each with different strengths for specifying and manipulating color.

### Real-World Dev Example
```css
.palette {
  /* Hex — most common, compact */
  color: #6366f1;        /* 6-digit */
  color: #6366f188;      /* 8-digit with alpha */

  /* RGB — readable channels */
  color: rgb(99, 102, 241);
  color: rgb(99 102 241 / 0.5);   /* modern syntax with alpha */

  /* HSL — most intuitive for designers */
  color: hsl(239, 84%, 67%);
  color: hsl(239 84% 67% / 0.5);

  /* oklch — perceptually uniform, best for color manipulation */
  color: oklch(65% 0.18 264);     /* lightness, chroma, hue */
}
```

### ASCII Diagram
```
HSL wheel:
  Hue: 0°=red, 60°=yellow, 120°=green, 180°=cyan, 240°=blue, 300°=magenta
  Saturation: 0%=grey → 100%=vivid
  Lightness: 0%=black → 50%=normal → 100%=white

oklch advantages:
  hsl(240 80% 50%)  vs  hsl(60 80% 50%)
  ← the "same" saturation looks very different visually (not perceptually uniform)
  oklch(60% 0.18 264) vs oklch(60% 0.18 89)
  ← these ACTUALLY have the same perceived brightness ✓
```

### Gotchas & Dev Context
- Hex `#fff` = `#ffffff` (3-digit shorthand). Hex `#fff8` = `#ffffff88` (alpha shorthand).
- `oklch` is the modern choice for design systems — colors at the same `L` value actually *look* the same brightness across hues. HSL doesn't guarantee this.
- Use CSS variables with `oklch` for theming: tweak only lightness to get shades.
- `currentColor` keyword inherits the element's text `color` — great for SVG icons that match surrounding text.

### Production FAQ
**Q: When should I use HSL vs oklch?**  
A: HSL for quick, human-readable colors where visual accuracy between hues isn't critical. `oklch` for design systems, accessible color palettes, or anywhere perceptual uniformity matters (e.g., data visualization).

**Q: How do I add transparency to a color?**  
A: Modern syntax: `rgb(99 102 241 / 0.5)` or `hsl(239 84% 67% / 50%)`. Or use the 8-digit hex: `#6366f180`. Avoid the old `rgba()` form — the space-slash syntax is cleaner.

---

## 14. Gradients (Linear, Radial, Conic)

**One-line definition:** CSS functions that generate smooth color transitions as an image value — no image files needed.

### Real-World Dev Example
```css
/* Linear — angle or direction */
.hero {
  background: linear-gradient(135deg, #6366f1, #8b5cf6 50%, #ec4899);
}

/* Radial — circular or elliptical */
.glow {
  background: radial-gradient(circle at center, #6366f180, transparent 70%);
}

/* Conic — sweeps around a point (pie charts, spinners) */
.pie {
  background: conic-gradient(#6366f1 0% 60%, #e5e7eb 60% 100%);
  border-radius: 50%;
}

/* Multiple gradients layered */
.fancy {
  background:
    linear-gradient(to bottom, transparent 80%, black),
    url('photo.jpg') center / cover;
}
```

### Gotchas & Dev Context
- Gradients are `<image>` values, not `<color>` — use them with `background`, `background-image`, `border-image`, `mask-image`.
- **Hard stops** create sharp lines: `linear-gradient(red 50%, blue 50%)`.
- `repeating-linear-gradient()` tiles the gradient — useful for striped backgrounds.
- Gradient performance is excellent — they're GPU-rendered. Use them freely as decorative backgrounds.
- For smooth gradients, avoid two-stop linear fades through grey in the middle (perceptually muddy). Add a midpoint stop or use `oklch` color space: `linear-gradient(in oklch, ...)` (modern browsers).

### Production FAQ
**Q: My gradient has a grey/muddy area in the middle. How do I fix it?**  
A: Add intermediate stops at the right colors, or use `linear-gradient(in oklch, color1, color2)` which interpolates in perceptual color space.

**Q: Can I animate a gradient?**  
A: CSS `transition` doesn't animate gradients directly. Workarounds: animate `background-position` on a oversized gradient, use `@property` to register a custom property as `<color>` and animate that, or animate with JS/WAAPI.

---

## 15. Transitions & Animations (@keyframes)

**One-line definition:** `transition` smoothly animates a CSS change triggered by a state change; `@keyframes` + `animation` plays a defined sequence on its own.

### Real-World Dev Example
```css
/* Transition — reacts to state change */
.btn {
  background: #6366f1;
  transition: background 200ms ease, transform 150ms ease;
}
.btn:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

/* Keyframe animation — plays automatically */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-text {
  animation: fadeInUp 600ms ease forwards;
  /* name duration timing fill-mode */
}

/* Looping spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.spinner { animation: spin 1s linear infinite; }
```

### Gotchas & Dev Context
- Only **compositable properties** (`transform`, `opacity`) animate on the GPU — smooth at 60fps. Properties like `width`, `height`, `top`, `margin` trigger layout recalculation — use sparingly.
- `transition: all` is a trap — it animates everything including properties you don't expect (color on a link hover suddenly also animates height). Be explicit.
- `animation-fill-mode: forwards` keeps the final keyframe state after the animation ends (otherwise it snaps back).
- Always add `@media (prefers-reduced-motion: reduce)` fallbacks for accessibility.

### Production FAQ
**Q: My animation plays but then snaps back to the original state.**  
A: Add `animation-fill-mode: forwards` to keep the final keyframe applied.

**Q: Why does my transition/animation feel janky (choppy)?**  
A: You're likely animating a layout-triggering property (`height`, `width`). Switch to `transform: scaleY()` for height or `opacity` for fades — these are GPU-accelerated.

---

## 16. Transform

**One-line definition:** `transform` lets you visually move, resize, or rotate an element without affecting the document flow.

### Real-World Dev Example
```css
.card:hover {
  transform: translateY(-8px) scale(1.02);
  /* move up 8px AND scale up 2% — both applied simultaneously */
}

.icon-spin {
  transform: rotate(45deg);
}

.squish {
  transform: scaleX(0.8) scaleY(1.2);
}

.skewed-banner {
  transform: skewY(-3deg);
}

/* 3D */
.flip-card {
  transform: rotateY(180deg);
  transform-style: preserve-3d;
}
```

### ASCII Diagram
```
translate(x, y)  → moves element in 2D space
rotate(deg)      → spins around transform-origin (default: center)
scale(x, y)      → resizes (1 = normal, 0.5 = half, 2 = double)
skew(x, y)       → tilts along axis

transform-origin: top left;  ← changes pivot point for rotate/scale
```

### Gotchas & Dev Context
- Transforms don't affect layout — other elements don't reflow when you translate or scale. This is both a feature and a gotcha (overlap can occur).
- Multiple transforms are applied **right to left** in the value list: `transform: translateX(50px) rotate(45deg)` — first rotates, then moves.
- `will-change: transform` hints the browser to promote the element to its own GPU layer. Use sparingly — only for known animated elements.
- `transform-origin` defaults to `50% 50%` (center). Change it to get fold/flip effects from an edge.

### Production FAQ
**Q: I'm using `transform: translate()` for centering but the element is off. Why?**  
A: `translate(-50%, -50%)` moves 50% of the element's *own* width/height — pair it with `position: absolute; top: 50%; left: 50%;` for classic centering.

**Q: Does `transform` work on inline elements?**  
A: Not reliably. Set `display: inline-block` or `block` first.

---

## 17. Z-Index & Stacking Context

**One-line definition:** `z-index` controls which element appears *on top* when elements overlap — but only within the same stacking context.

### Real-World Dev Example
```css
.modal-overlay { position: fixed; z-index: 1000; }
.modal-dialog  { position: fixed; z-index: 1001; }
.tooltip       { position: absolute; z-index: 500; }
.header        { position: sticky; z-index: 100; }

/* A new stacking context is created by: */
.new-context {
  position: relative; z-index: 1;   /* positioned + z-index */
  /* OR */
  opacity: 0.99;                    /* opacity < 1 */
  /* OR */
  transform: translateZ(0);          /* any transform */
  /* OR */
  isolation: isolate;               /* explicit, cleanest */
}
```

### ASCII Diagram
```
Without stacking context:
  [z:1000 modal] sits above [z:500 tooltip] — makes sense ✓

With stacking context (e.g., parent has transform):
  [parent: transform]
    └─ [z:9999 child]   ← trapped inside parent's context!
  [z:1 sibling]         ← can paint ABOVE the z:9999 child
                           if parent's z-index is lower
```

### Gotchas & Dev Context
- **`z-index` only works on positioned elements** (`position` ≠ `static`).
- Any of these create a new stacking context: `opacity < 1`, `transform`, `filter`, `will-change`, `isolation: isolate`, `position + z-index`.
- A `z-index: 9999` child *cannot escape* its parent's stacking context.
- Use `isolation: isolate` to intentionally create a stacking context without side effects.
- Maintain a z-index scale (e.g., `--z-header: 100`, `--z-modal: 1000`) as CSS variables to avoid magic numbers.

### Production FAQ
**Q: My modal is hidden behind another element even though its `z-index` is huge.**  
A: One of its ancestor elements has created a stacking context with a lower `z-index`. Move the modal to be a direct child of `<body>` (or use a portal in React).

**Q: What's the highest valid `z-index`?**  
A: Theoretically up to 2,147,483,647 (32-bit int max). In practice, keep a scale under 10,000. Escalating z-index is a code smell.

---

## 18. Overflow & Scrolling

**One-line definition:** `overflow` controls what happens when content is larger than its container — clip it, show it, or make it scrollable.

### Real-World Dev Example
```css
/* Clip content, no scroll */
.avatar { width: 48px; height: 48px; border-radius: 50%; overflow: hidden; }

/* Show scrollbar when needed */
.code-block { overflow-x: auto; }

/* Always show scrollbar (prevents layout shift) */
html { overflow-y: scroll; }

/* Smooth scrolling for anchor links */
html { scroll-behavior: smooth; }

/* Custom scrollbar (WebKit only) */
.sidebar::-webkit-scrollbar { width: 6px; }
.sidebar::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }

/* Modern scroll snap */
.carousel {
  overflow-x: scroll;
  scroll-snap-type: x mandatory;
}
.carousel-item { scroll-snap-align: start; }
```

### Gotchas & Dev Context
- `overflow: hidden` on a parent clips child elements visually, including `box-shadow` and elements that extend outside. Check that `border-radius` clipping works as intended.
- `overflow: hidden` also **prevents margin collapse** and creates a new **block formatting context** (BFC) — sometimes used as a float-clearing hack.
- Setting `overflow-x: hidden` implicitly sets `overflow-y: auto` — this can create unexpected vertical scroll on the element.
- `overflow: clip` (modern) is like `hidden` but doesn't create a scroll container — better for clipping without side effects.

### Production FAQ
**Q: My page has horizontal scroll but I can't find the cause.**  
A: Temporarily add `* { outline: 1px solid red; }` to visualize all elements. Alternatively, in DevTools Console: `document.querySelectorAll('*')` and check which element's `scrollWidth > clientWidth`.

**Q: How do I hide scrollbars but keep scrolling functional?**  
A: 
```css
.container { overflow: auto; scrollbar-width: none; } /* Firefox */
.container::-webkit-scrollbar { display: none; }      /* Chrome/Safari */
```

---

## 19. CSS Reset / Normalize

**One-line definition:** CSS files that remove or standardize the inconsistent default styles that different browsers apply to HTML elements.

### Real-World Dev Example
```css
/* ── Minimal Modern Reset (Eric Meyer style) ── */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

img, video, canvas, svg { display: block; max-width: 100%; }

input, button, textarea, select { font: inherit; }

p, h1, h2, h3, h4, h5, h6 { overflow-wrap: break-word; }
```

### Gotchas & Dev Context
- **Reset** (Eric Meyer, Josh Comeau) — strips all browser defaults to zero. You rebuild everything from scratch. Maximum control.
- **Normalize** (necolas/normalize.css) — keeps useful defaults, only fixes inconsistencies across browsers. Less work.
- **Modern preference**: a small, targeted reset (like Josh Comeau's `modern-css-reset`) rather than a full Normalize — browsers are more consistent now.
- Using Tailwind? Its `preflight` is a built-in reset — don't layer another one on top.
- Always load your reset *first* in your stylesheet (or as the first import).

### Production FAQ
**Q: Do I still need a CSS reset in 2025?**  
A: Yes, but a small targeted one. Browsers are more consistent than in 2010, but defaults still differ on margins, font inheritance, and `<button>` styling. A 20-line modern reset covers 95% of what you need.

**Q: Normalize vs Reset — which should I use?**  
A: New projects: modern minimal reset. Retrofitting an old project that relies on browser defaults: Normalize (less disruptive). Never use both simultaneously.

---

## 20. Container Queries

**One-line definition:** Like media queries, but instead of reacting to the *viewport* size, a component's styles react to the size of its *own container*.

### Real-World Dev Example
```css
/* Step 1: Define a containment context on the parent */
.card-wrapper {
  container-type: inline-size;
  container-name: card;   /* optional name */
}

/* Step 2: Query the container's size */
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 120px 1fr;
  }
}

@container card (min-width: 600px) {
  .card-title { font-size: 1.5rem; }
}
```

### ASCII Diagram
```
Media Query world:
  Sidebar (300px wide) → layout based on VIEWPORT (1440px) → desktop layout 😕

Container Query world:
  Sidebar (300px wide) → layout based on SIDEBAR width (300px) → compact layout ✓
  Main area (900px wide) → layout based on MAIN width (900px) → expanded layout ✓
```

### Gotchas & Dev Context
- `container-type: inline-size` is the most common — responds to width only. `size` responds to both width and height.
- The container itself cannot query itself — the rule applies to descendants inside the container.
- **Browser support**: All modern browsers as of 2023. Safe to use in new projects.
- Pairs perfectly with design systems: a `<Card>` component can now adapt to wherever it's placed without media query hacks.
- You cannot yet query by container aspect-ratio or other properties (only `width`, `height`, `inline-size`, `block-size`).

### Production FAQ
**Q: How are container queries different from media queries?**  
A: Media queries look at the *browser viewport*. Container queries look at the *parent element*. The same card component can be compact in a sidebar and expanded in a main area — without any JS or external context.

**Q: Do I need to polyfill container queries?**  
A: No, for modern browsers (Chrome 105+, Firefox 110+, Safari 16+). If you need IE/older browser support, use a polyfill or fall back to media queries.

---

*End of Batch 3 — CSS Fundamentals & Layout*  
*Next up: Batch 4 — JavaScript Core Concepts*
