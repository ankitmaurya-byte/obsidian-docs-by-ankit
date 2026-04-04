# CSS

## Box Model
```
box_model:
  what: Every HTML element is a rectangular box with four layers
  layers_inside_out:
    content: "The actual content (text, image) - set with width/height"
    padding: "Space between content and border (inside the element)"
    border: "Edge of the element"
    margin: "Space outside the border (between elements)"

  box_sizing:
    content-box: "Default - width/height = content only, padding and border are extra"
    border-box: "width/height = content + padding + border (what you usually want)"

  margin_collapsing:
    what: "Adjacent vertical margins collapse to the larger value"
    when: "Between sibling block elements, between parent and first/last child"
    does_not_apply: "Horizontal margins, flex/grid items, floated elements"
```

```css
/* Always use border-box globally */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Box model example */
.card {
  width: 300px;      /* with border-box: total width stays 300px */
  padding: 20px;
  border: 1px solid #ccc;
  margin: 16px;
}
```

## Flexbox
```
flexbox:
  what: One-dimensional layout system (row OR column)
  terminology:
    flex_container: "Parent element with display:flex"
    flex_items: "Direct children of flex container"
    main_axis: "Primary direction (row = horizontal, column = vertical)"
    cross_axis: "Perpendicular to main axis"

  container_properties:
    display: "flex | inline-flex"
    flex-direction: "row (default) | row-reverse | column | column-reverse"
    flex-wrap: "nowrap (default) | wrap | wrap-reverse"
    justify-content: "Main axis alignment: flex-start | flex-end | center | space-between | space-around | space-evenly"
    align-items: "Cross axis alignment: stretch (default) | flex-start | flex-end | center | baseline"
    align-content: "Multi-line cross axis: stretch | flex-start | flex-end | center | space-between | space-around"
    gap: "row-gap column-gap (space between items)"

  item_properties:
    flex-grow: "0 (default) - how much item grows to fill space"
    flex-shrink: "1 (default) - how much item shrinks when space is tight"
    flex-basis: "auto (default) - initial size before grow/shrink"
    flex: "shorthand: grow shrink basis (e.g., flex: 1 = flex: 1 1 0)"
    align-self: "Override align-items for this item"
    order: "0 (default) - visual order (lower = first)"
```

```css
/* Centering (the classic) */
.center {
  display: flex;
  justify-content: center; /* main axis */
  align-items: center;     /* cross axis */
  height: 100vh;
}

/* Navbar layout */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

/* Equal-width columns */
.columns {
  display: flex;
  gap: 16px;
}
.columns > * {
  flex: 1; /* all items grow equally */
}

/* Sidebar + main content */
.layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  flex: 0 0 250px; /* don't grow, don't shrink, 250px wide */
}
.main {
  flex: 1; /* take remaining space */
}

/* Wrap items like a tag cloud */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Push last item to the right */
.nav-items {
  display: flex;
  gap: 16px;
}
.nav-items > :last-child {
  margin-left: auto; /* pushes to the far right */
}
```

## CSS Grid
```
css_grid:
  what: Two-dimensional layout system (rows AND columns simultaneously)
  terminology:
    grid_container: "Parent with display:grid"
    grid_items: "Direct children"
    grid_lines: "Dividers between columns/rows (numbered from 1)"
    grid_track: "A row or column"
    grid_cell: "Single unit (intersection of row and column)"
    grid_area: "Rectangular area spanning one or more cells"

  container_properties:
    display: "grid | inline-grid"
    grid-template-columns: "Defines column sizes (e.g., 1fr 2fr 1fr, repeat(3, 1fr))"
    grid-template-rows: "Defines row sizes"
    grid-template-areas: "Name grid areas for visual layout"
    gap: "row-gap column-gap"
    justify-items: "Align items horizontally in their cell"
    align-items: "Align items vertically in their cell"
    justify-content: "Align entire grid horizontally in container"
    align-content: "Align entire grid vertically in container"

  item_properties:
    grid-column: "start / end (e.g., 1 / 3 spans 2 columns)"
    grid-row: "start / end"
    grid-area: "name or row-start / col-start / row-end / col-end"
    justify-self: "Override justify-items for this item"
    align-self: "Override align-items for this item"

  key_units:
    fr: "Fraction of available space"
    minmax: "minmax(200px, 1fr) - responsive sizing"
    auto-fill: "repeat(auto-fill, minmax(200px, 1fr)) - as many as fit"
    auto-fit: "Like auto-fill but collapses empty tracks"
```

```css
/* Basic 3-column layout */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* Holy grail layout with named areas */
.page {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar main aside"
    "footer footer footer";
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}
.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.aside   { grid-area: aside; }
.footer  { grid-area: footer; }

/* Responsive card grid (no media queries needed) */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

/* Spanning multiple cells */
.featured {
  grid-column: 1 / 3; /* spans 2 columns */
  grid-row: 1 / 3;    /* spans 2 rows */
}

/* Centering with grid (simplest method) */
.center-grid {
  display: grid;
  place-items: center; /* shorthand for align-items + justify-items */
  height: 100vh;
}
```

## Positioning
```
positioning:
  static:
    what: "Default - element in normal document flow"
    top_right_bottom_left: "Have no effect"

  relative:
    what: "Positioned relative to its normal position"
    effect: "Element still takes up original space in flow"
    use: "Offset element slightly, or create positioning context for absolute children"

  absolute:
    what: "Removed from normal flow, positioned relative to nearest positioned ancestor"
    effect: "Does not take up space, other elements behave as if it doesn't exist"
    positioned_ancestor: "Nearest ancestor with position other than static"
    fallback: "If no positioned ancestor, positions relative to <html>"

  fixed:
    what: "Positioned relative to the viewport"
    effect: "Stays in place when scrolling"
    use: "Fixed headers, floating buttons, modals"

  sticky:
    what: "Hybrid of relative and fixed"
    behavior: "Acts relative until scroll threshold, then acts fixed"
    requires: "At least one of top/right/bottom/left to define stick point"
    use: "Sticky headers, table headers, sidebar navigation"
```

```css
/* Relative + Absolute (dropdown, badges, tooltips) */
.card {
  position: relative; /* creates positioning context */
}
.card .badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: red;
  border-radius: 50%;
  padding: 4px 8px;
}

/* Fixed header */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  z-index: 100;
  background: white;
}
body {
  padding-top: 60px; /* compensate for fixed header */
}

/* Sticky table header */
thead th {
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
}

/* Sticky sidebar */
.sidebar {
  position: sticky;
  top: 80px; /* sticks 80px from top */
  height: fit-content;
}
```

## Media Queries and Responsive Design
```
responsive_design:
  approach: Mobile-first (start with smallest screen, add complexity for larger)
  common_breakpoints:
    mobile: "< 640px"
    tablet: "640px - 1024px"
    desktop: "> 1024px"
  techniques:
    media_queries: "@media (min-width: 768px) { ... }"
    fluid_typography: "clamp(1rem, 2.5vw, 2rem)"
    fluid_layout: "Use %, vw, fr, auto-fit/auto-fill"
    container_queries: "@container (min-width: 400px) { ... }"
  units:
    rem: "Relative to root font-size (scalable, accessible)"
    em: "Relative to parent font-size"
    vw_vh: "Viewport width/height percentage"
    dvh: "Dynamic viewport height (accounts for mobile browser chrome)"
```

```css
/* Mobile-first approach */
.container {
  padding: 16px;
  width: 100%;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 24px;
    max-width: 720px;
    margin: 0 auto;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    max-width: 960px;
  }
}

/* Fluid typography - scales between 1rem and 2.5rem */
h1 {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
}

/* Responsive images */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* Container queries (modern CSS) */
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: flex;
    flex-direction: row;
  }
}

/* Prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a1a;
    --text: #e0e0e0;
  }
}
```

## CSS Variables (Custom Properties)
```
css_variables:
  what: "Custom properties that can be reused throughout a stylesheet"
  syntax:
    define: "--variable-name: value"
    use: "var(--variable-name, fallback)"
  scope: "Inherited - defined on :root for global, on element for local"
  features:
    - Cascade and inherit like normal properties
    - Can be changed at runtime with JS
    - Can be scoped to components
    - Support fallback values
```

```css
/* Global variables */
:root {
  --color-primary: #3b82f6;
  --color-secondary: #10b981;
  --color-text: #1f2937;
  --color-bg: #ffffff;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 32px;
  --radius: 8px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --font-sans: system-ui, -apple-system, sans-serif;
}

/* Dark theme override */
[data-theme="dark"] {
  --color-text: #e0e0e0;
  --color-bg: #1a1a1a;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

/* Usage */
.button {
  background: var(--color-primary);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius);
  color: white;
}

.card {
  background: var(--color-bg);
  color: var(--color-text);
  box-shadow: var(--shadow);
  border-radius: var(--radius);
  padding: var(--spacing-lg);
}

/* Fallback value */
.special {
  color: var(--color-accent, #ff6600);
}

/* Component-scoped variables */
.alert {
  --alert-bg: #fef3cd;
  --alert-color: #856404;
  --alert-border: #ffc107;

  background: var(--alert-bg);
  color: var(--alert-color);
  border: 1px solid var(--alert-border);
  padding: var(--spacing-md);
}

.alert.danger {
  --alert-bg: #f8d7da;
  --alert-color: #721c24;
  --alert-border: #f5c6cb;
}
```

## Animations
```
animations:
  transitions:
    what: "Animate property changes smoothly"
    syntax: "transition: property duration timing-function delay"
    timing_functions: "ease, ease-in, ease-out, ease-in-out, linear, cubic-bezier()"

  keyframe_animations:
    what: "Multi-step animations with full control"
    syntax: "@keyframes name { from {} to {} } or { 0% {} 50% {} 100% {} }"

  performant_properties:
    transform: "translate, scale, rotate (GPU accelerated)"
    opacity: "GPU accelerated"
    avoid_animating: "width, height, top, left, margin, padding (cause layout recalculation)"
```

```css
/* Transition - hover effect */
.button {
  background: #3b82f6;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  transition: background 0.2s ease, transform 0.2s ease;
}

.button:hover {
  background: #2563eb;
  transform: translateY(-2px);
}

.button:active {
  transform: translateY(0);
}

/* Keyframe animation - fade in and slide up */
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

.card {
  animation: fadeInUp 0.3s ease-out;
}

/* Loading spinner */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Skeleton loading pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton {
  background: #e5e7eb;
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}

/* Staggered animation using custom property */
.list-item {
  animation: fadeInUp 0.4s ease-out backwards;
  animation-delay: calc(var(--i) * 0.1s);
}
```

```html
<!-- Usage of staggered animation -->
<ul>
  <li class="list-item" style="--i: 0">First</li>
  <li class="list-item" style="--i: 1">Second</li>
  <li class="list-item" style="--i: 2">Third</li>
</ul>
```

## Pseudo-classes and Pseudo-elements
```
pseudo:
  pseudo_classes:
    what: "Select elements based on state or position (single colon)"
    state:
      ":hover": "Mouse over"
      ":focus": "Element has focus"
      ":focus-visible": "Focus from keyboard (not mouse click)"
      ":active": "Being clicked"
      ":visited": "Visited link"
      ":disabled": "Disabled form element"
      ":checked": "Checked checkbox/radio"
    structural:
      ":first-child": "First child of parent"
      ":last-child": "Last child of parent"
      ":nth-child(n)": "nth child (2n = even, 2n+1 = odd, 3n = every 3rd)"
      ":not(selector)": "Negation"
      ":is(selector)": "Matches any of the selectors (forgiving)"
      ":has(selector)": "Parent selector (contains matching child)"
      ":where(selector)": "Like :is() but with zero specificity"

  pseudo_elements:
    what: "Create/style sub-parts of elements (double colon)"
    "::before": "Insert content before element"
    "::after": "Insert content after element"
    "::placeholder": "Style input placeholder text"
    "::selection": "Style highlighted/selected text"
    "::first-line": "Style first line of text"
    "::first-letter": "Style first letter (drop caps)"
```

```css
/* :has() - parent selector (modern CSS) */
.card:has(img) {
  padding: 0; /* remove padding if card contains an image */
}

/* :is() - grouping */
:is(h1, h2, h3, h4) {
  font-family: var(--font-sans);
  line-height: 1.2;
}

/* Focus visible (keyboard only) */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Pseudo-elements for decorative content */
.required-label::after {
  content: " *";
  color: red;
}

.blockquote::before {
  content: "\201C"; /* opening curly quote */
  font-size: 3rem;
  color: #ccc;
}

/* Custom checkbox */
.checkbox:checked + label::before {
  background: #3b82f6;
  content: "\2714";
  color: white;
}

/* Zebra-striped table */
tr:nth-child(even) {
  background: #f9fafb;
}

/* Tooltip with pseudo-element */
.tooltip {
  position: relative;
}
.tooltip::after {
  content: attr(data-tip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}
.tooltip:hover::after {
  opacity: 1;
}
```

## Specificity
```
specificity:
  what: "Algorithm that determines which CSS rule applies when multiple rules target the same element"
  calculation: "(inline, id, class, element)"
  values:
    inline_styles: "1,0,0,0 (highest, avoid)"
    id_selectors: "0,1,0,0 (#header)"
    class_selectors: "0,0,1,0 (.card, [type=text], :hover)"
    element_selectors: "0,0,0,1 (div, p, ::before)"
    universal: "0,0,0,0 (* has no specificity)"
    !important: "Overrides everything (avoid, breaks cascade)"

  rules:
    - Higher specificity wins
    - Equal specificity = last rule wins (source order)
    - Inline styles beat everything except !important
    - :is() and :not() take specificity of their argument
    - :where() always has 0 specificity
```

```css
/* Specificity examples (lowest to highest) */
p { color: black; }                    /* 0,0,0,1 */
.text { color: blue; }                /* 0,0,1,0 */
p.text { color: green; }              /* 0,0,1,1 */
#main .text { color: red; }           /* 0,1,1,0 */
#main p.text { color: purple; }       /* 0,1,1,1 */

/* :where() has zero specificity - easy to override */
:where(.card, .panel, .box) {
  padding: 16px;
  border-radius: 8px;
}

/* :is() takes highest specificity of its arguments */
:is(#main, .sidebar) p {
  /* specificity = 0,1,0,1 (because of #main) */
  color: red;
}
```

## BEM Naming Convention
```
bem:
  what: "Block Element Modifier - naming convention for CSS classes"
  structure:
    block: "Standalone component (card, header, menu)"
    element: "Part of a block (card__title, menu__item)"
    modifier: "Variation of block or element (card--featured, menu__item--active)"
  syntax:
    block: ".block"
    element: ".block__element"
    modifier: ".block--modifier or .block__element--modifier"
  benefits:
    - Flat specificity (only single class selectors)
    - Self-documenting class names
    - No naming collisions
    - Easy to understand component structure
```

```css
/* BEM example: card component */
.card { }
.card__header { }
.card__title { }
.card__body { }
.card__footer { }
.card--featured { border: 2px solid gold; }
.card--compact { padding: 8px; }
.card__title--large { font-size: 1.5rem; }
```

```html
<div class="card card--featured">
  <div class="card__header">
    <h2 class="card__title card__title--large">Title</h2>
  </div>
  <div class="card__body">Content here</div>
  <div class="card__footer">Footer</div>
</div>
```

## Modern CSS Features
```
modern_css:
  nesting:
    what: "Native CSS nesting (like Sass) - supported in modern browsers"
    syntax: ".parent { .child { ... } &:hover { ... } }"

  cascade_layers:
    what: "@layer - control cascade ordering explicitly"
    syntax: "@layer base, components, utilities"

  color_functions:
    - "oklch(0.7 0.15 200) - perceptually uniform"
    - "color-mix(in srgb, #ff0000 50%, #0000ff)"

  subgrid:
    what: "Grid children can inherit parent grid tracks"
    syntax: "grid-template-columns: subgrid"

  logical_properties:
    what: "Direction-agnostic properties (work with RTL/LTR)"
    examples:
      margin-inline: "replaces margin-left/margin-right"
      padding-block: "replaces padding-top/padding-bottom"
      inset: "shorthand for top/right/bottom/left"

  scroll_snap:
    what: "Native scroll snapping (carousels without JS)"
    container: "scroll-snap-type: x mandatory"
    children: "scroll-snap-align: start"
```

```css
/* Native CSS nesting */
.card {
  padding: 16px;
  background: white;

  .card__title {
    font-size: 1.25rem;
    margin-bottom: 8px;
  }

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &.card--dark {
    background: #1a1a1a;
    color: white;
  }
}

/* Cascade layers */
@layer base, components, utilities;

@layer base {
  h1 { font-size: 2rem; }
}
@layer components {
  .card { padding: 16px; }
}
@layer utilities {
  .mt-4 { margin-top: 1rem; }
}

/* Scroll snap carousel */
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 16px;
}
.carousel > * {
  scroll-snap-align: start;
  flex: 0 0 80%;
}

/* Logical properties */
.element {
  margin-inline: auto;     /* horizontal centering (LTR and RTL) */
  padding-block: 16px;     /* top and bottom */
  border-inline-start: 3px solid blue; /* left in LTR, right in RTL */
  inset: 0;                /* top:0 right:0 bottom:0 left:0 */
}

/* View transitions API */
::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}
```

## Practical Layout Examples
```
practical_layouts:
  common_patterns:
    - Sticky footer
    - Full-height sidebar layout
    - Responsive card grid
    - Centered content with max-width
```

```css
/* Sticky footer (content pushes footer down) */
body {
  display: flex;
  flex-direction: column;
  min-height: 100dvh; /* dynamic viewport height */
}
main {
  flex: 1;
}
footer {
  /* always at bottom, pushed down by content */
}

/* Full app layout */
.app {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr;
  height: 100dvh;
}
.app-header {
  grid-column: 1 / -1; /* full width */
}
.app-sidebar {
  overflow-y: auto;
}
.app-main {
  overflow-y: auto;
  padding: 24px;
}

/* Responsive: stack on mobile */
@media (max-width: 768px) {
  .app {
    grid-template-columns: 1fr;
  }
  .app-sidebar {
    display: none; /* or use a drawer */
  }
}

/* Aspect ratio box (16:9 video container) */
.video-wrapper {
  aspect-ratio: 16 / 9;
  width: 100%;
  background: black;
}

/* Truncate text with ellipsis */
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Multi-line truncate */
.line-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```
