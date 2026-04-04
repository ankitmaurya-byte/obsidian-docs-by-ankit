# Web Performance

## Core Web Vitals
```
core_web_vitals:
  what: Google's set of metrics measuring real-world user experience
  metrics:
    LCP:
      full_name: Largest Contentful Paint
      what: "Time until the largest visible content element is rendered"
      target: "< 2.5 seconds (good)"
      measures: "Loading performance"
      common_culprits:
        - Slow server response (TTFB)
        - Render-blocking CSS/JS
        - Unoptimized hero images
        - Client-side rendering (no SSR)
      fixes:
        - Optimize server response time
        - Preload critical resources (preload hero image)
        - Use CDN for static assets
        - Inline critical CSS
        - Use SSR or SSG

    FID:
      full_name: First Input Delay
      what: "Time from first user interaction to browser response"
      target: "< 100ms (good)"
      measures: "Interactivity"
      replaced_by: "INP (Interaction to Next Paint) as of March 2024"
      fixes:
        - Break up long tasks (> 50ms)
        - Defer non-critical JavaScript
        - Use web workers for heavy computation
        - Reduce main thread work

    INP:
      full_name: Interaction to Next Paint
      what: "Latency of all interactions throughout the page lifecycle (worst case)"
      target: "< 200ms (good)"
      measures: "Overall responsiveness"

    CLS:
      full_name: Cumulative Layout Shift
      what: "Total of all unexpected layout shifts during page lifetime"
      target: "< 0.1 (good)"
      measures: "Visual stability"
      common_culprits:
        - Images without dimensions
        - Ads/embeds without reserved space
        - Dynamically injected content
        - Web fonts causing text reflow (FOUT)
      fixes:
        - Always set width/height or aspect-ratio on images/videos
        - Reserve space for ads and embeds
        - Use font-display swap with size-adjust
        - Avoid inserting content above existing content
```

## Lazy Loading
```
lazy_loading:
  what: "Defer loading of non-critical resources until they are needed"
  types:
    images:
      native: 'loading="lazy" attribute on <img> and <iframe>'
      intersection_observer: "JS-based for more control"
    components: "React.lazy() + Suspense for code splitting"
    routes: "Load route components on navigation"
    data: "Fetch data only when section is visible"

  best_practices:
    - Never lazy load above-the-fold content
    - Set dimensions on lazy images to prevent CLS
    - Use placeholder/skeleton while loading
    - Preload resources you know will be needed soon
```

```html
<!-- Native lazy loading -->
<img src="photo.jpg" loading="lazy" width="800" height="600" alt="Photo" />

<!-- Eager load above-the-fold hero image -->
<img src="hero.jpg" loading="eager" fetchpriority="high" alt="Hero" />

<!-- Lazy load iframe -->
<iframe src="https://youtube.com/embed/xxx" loading="lazy"></iframe>
```

```javascript
// Intersection Observer for custom lazy loading
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src; // move data-src to src
        img.removeAttribute("data-src");
        observer.unobserve(img);
      }
    });
  },
  { rootMargin: "200px" } // start loading 200px before visible
);

document.querySelectorAll("img[data-src]").forEach((img) => {
  observer.observe(img);
});

// React lazy loading
const HeavyChart = React.lazy(() => import("./HeavyChart"));

function Dashboard() {
  return (
    <Suspense fallback={<div className="skeleton" />}>
      <HeavyChart />
    </Suspense>
  );
}
```

## Code Splitting
```
code_splitting:
  what: "Breaking your JS bundle into smaller chunks loaded on demand"
  why: "Users don't need all code upfront - load only what's needed for current page"
  methods:
    route_based: "Split by page/route (most common)"
    component_based: "Split heavy components (modals, charts, editors)"
    dynamic_import: "import() returns a Promise, bundler creates separate chunk"
  tools:
    webpack: "Built-in support via dynamic import()"
    vite: "Built-in, uses Rollup for production"
    next_js: "Automatic per-page splitting + next/dynamic"
```

```javascript
// Dynamic import (works with any bundler)
button.addEventListener("click", async () => {
  const { PDFViewer } = await import("./PDFViewer.js");
  const viewer = new PDFViewer();
  viewer.render(document.getElementById("container"));
});

// React route-based splitting
import { lazy, Suspense } from "react";
import { Routes, Route } from "react-router-dom";

const Home = lazy(() => import("./pages/Home"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}

// Next.js dynamic import
import dynamic from "next/dynamic";

const Chart = dynamic(() => import("../components/Chart"), {
  loading: () => <p>Loading chart...</p>,
  ssr: false, // disable server-side rendering for this component
});

// Prefetch on hover (load before user clicks)
function NavLink({ to, children }) {
  const prefetch = () => {
    import(`./pages/${to}.js`); // starts loading on hover
  };

  return (
    <a href={`/${to}`} onMouseEnter={prefetch}>
      {children}
    </a>
  );
}
```

## Tree Shaking
```
tree_shaking:
  what: "Dead code elimination - remove unused exports from the final bundle"
  how_it_works:
    - Bundler analyzes static import/export statements (ESM only)
    - Marks unused exports as dead code
    - Removes them during minification
  requirements:
    - Use ES modules (import/export), NOT CommonJS (require)
    - Bundler must support it (Webpack, Rollup, Vite, esbuild)
    - Package must declare sideEffects in package.json
  tips:
    - Import specific functions, not entire libraries
    - Avoid side effects in module scope
    - Use sideEffects field in package.json
    - Check bundle with webpack-bundle-analyzer
```

```javascript
// BAD - imports entire library (no tree shaking possible with some libs)
import _ from "lodash";
_.get(obj, "path");

// GOOD - import only what you need
import get from "lodash/get";
get(obj, "path");

// GOOD - named imports (tree-shakeable if library uses ESM)
import { get, debounce } from "lodash-es";
```

```json
// package.json - declare side-effect-free for better tree shaking
{
  "name": "my-library",
  "sideEffects": false
}

// Or specify files with side effects
{
  "sideEffects": ["*.css", "./src/polyfills.js"]
}
```

## Image Optimization
```
image_optimization:
  formats:
    WebP: "25-35% smaller than JPEG, supports transparency, good browser support"
    AVIF: "50% smaller than JPEG, best quality, growing browser support"
    SVG: "Vector graphics, infinite scaling, tiny for icons/logos"
    JPEG: "Photos, no transparency"
    PNG: "Lossless, transparency, larger files"

  techniques:
    responsive_images: "srcset + sizes for different screen sizes"
    art_direction: "<picture> element for different crops per breakpoint"
    lazy_loading: 'loading="lazy" on below-fold images'
    dimensions: "Always set width + height to prevent CLS"
    compression: "Squoosh, Sharp, ImageOptim"
    modern_formats: "Serve AVIF/WebP with JPEG fallback"
    CDN_transforms: "On-the-fly resizing via Cloudinary, imgix, Vercel"
    fetchpriority: '"high" for hero image, "low" for below-fold'
```

```html
<!-- Responsive images with modern formats -->
<picture>
  <source srcset="hero.avif" type="image/avif" />
  <source srcset="hero.webp" type="image/webp" />
  <img
    src="hero.jpg"
    alt="Hero image"
    width="1200"
    height="600"
    loading="eager"
    fetchpriority="high"
    decoding="async"
  />
</picture>

<!-- Responsive srcset - browser picks best size -->
<img
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  src="photo-800.jpg"
  alt="Responsive photo"
  loading="lazy"
  width="800"
  height="600"
/>
```

```javascript
// Sharp - server-side image optimization (Node.js)
import sharp from "sharp";

await sharp("input.jpg")
  .resize(800, 600, { fit: "cover" })
  .webp({ quality: 80 })
  .toFile("output.webp");

// Generate multiple sizes
const sizes = [400, 800, 1200];
for (const width of sizes) {
  await sharp("input.jpg")
    .resize(width)
    .avif({ quality: 65 })
    .toFile(`output-${width}.avif`);
}
```

## CDN (Content Delivery Network)
```
cdn:
  what: "Geographically distributed network of servers that cache and serve content from locations closest to users"
  how_it_works:
    1: "User requests a resource"
    2: "DNS resolves to nearest CDN edge server"
    3: "Edge server checks its cache"
    4: "Cache hit: serves immediately, Cache miss: fetches from origin, caches, serves"
  benefits:
    - Reduced latency (served from nearby edge)
    - Reduced origin server load
    - DDoS protection
    - Automatic SSL/TLS
    - Global availability
  what_to_put_on_cdn:
    - Static assets (JS, CSS, images, fonts)
    - Pre-rendered HTML pages (SSG)
    - API responses (with proper cache headers)
  popular_cdns:
    - Cloudflare
    - AWS CloudFront
    - Vercel Edge Network
    - Fastly
    - Akamai
```

## Compression
```
compression:
  what: "Reduce file size of text-based resources (HTML, CSS, JS, JSON, SVG)"
  algorithms:
    gzip:
      compression_ratio: "~60-80% reduction"
      browser_support: "Universal"
      speed: "Fast compression and decompression"

    brotli:
      compression_ratio: "~15-25% better than gzip"
      browser_support: "All modern browsers (over HTTPS)"
      speed: "Slower compression, similar decompression"
      note: "Pre-compress static assets at build time for best ratio"

  how_it_works:
    1: "Browser sends Accept-Encoding: gzip, br header"
    2: "Server compresses response with best supported algorithm"
    3: "Server sends Content-Encoding: br (or gzip) header"
    4: "Browser decompresses automatically"

  implementation:
    nginx: "gzip on; brotli on;"
    express: "compression middleware"
    build_time: "Pre-compress with gzip + brotli (vite-plugin-compression)"
```

```javascript
// Express.js compression middleware
import compression from "compression";
import express from "express";

const app = express();
app.use(compression()); // automatically gzip responses

// Vite config - pre-compress at build time
// vite.config.js
import viteCompression from "vite-plugin-compression";

export default {
  plugins: [
    viteCompression({ algorithm: "gzip" }),
    viteCompression({ algorithm: "brotliCompress" }),
  ],
};
```

```nginx
# Nginx configuration
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml;
gzip_min_length 1000;

# Brotli (requires ngx_brotli module)
brotli on;
brotli_types text/plain text/css application/json application/javascript;
```

## Caching Strategies
```
caching_strategies:
  http_cache_headers:
    Cache-Control:
      "no-store": "Never cache (sensitive data)"
      "no-cache": "Cache but revalidate every time"
      "max-age=31536000": "Cache for 1 year (immutable assets)"
      "public": "Any cache can store (CDN, browser)"
      "private": "Only browser can cache (user-specific data)"
      "stale-while-revalidate=60": "Serve stale while fetching fresh in background"
    ETag: "Hash of content - server checks if changed (304 Not Modified)"
    Last-Modified: "Timestamp - less precise than ETag"

  strategies:
    cache_first: "Check cache, fallback to network (static assets)"
    network_first: "Try network, fallback to cache (API data)"
    stale_while_revalidate: "Serve cached, update cache in background"
    cache_only: "Only serve from cache (offline mode)"
    network_only: "Never cache (real-time data, analytics)"

  file_naming:
    content_hash: "bundle.a1b2c3.js - changes on content change, cache forever"
    versioned: "styles.v2.css - manual version bump"
    pattern: "Use content hash + Cache-Control: max-age=31536000, immutable"
```

```nginx
# Nginx caching configuration

# HTML - always revalidate (content may change)
location / {
  add_header Cache-Control "no-cache";
}

# Hashed static assets - cache forever
location /assets/ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}

# API responses - short cache with revalidation
location /api/ {
  add_header Cache-Control "private, max-age=0, must-revalidate";
  add_header Vary "Authorization";
}
```

```javascript
// Service Worker - stale-while-revalidate
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.open("dynamic-v1").then(async (cache) => {
      const cached = await cache.match(event.request);

      // Fetch fresh in background
      const fetchPromise = fetch(event.request).then((response) => {
        cache.put(event.request, response.clone());
        return response;
      });

      // Return cached immediately, update cache in background
      return cached || fetchPromise;
    })
  );
});
```

## Critical Rendering Path
```
critical_rendering_path:
  what: "The sequence of steps the browser takes to convert HTML, CSS, and JS into pixels on screen"
  steps:
    1_parse_html: "Build DOM tree from HTML"
    2_parse_css: "Build CSSOM from CSS (render-blocking)"
    3_javascript: "Execute JS (parser-blocking unless async/defer)"
    4_render_tree: "Combine DOM + CSSOM (only visible elements)"
    5_layout: "Calculate position and size of each element"
    6_paint: "Fill in pixels (colors, borders, shadows)"
    7_composite: "Combine layers and display"

  optimization:
    reduce_critical_resources:
      - "Inline critical CSS (above-the-fold styles)"
      - "Defer non-critical CSS"
      - "async/defer JS scripts"
      - "Preload critical fonts"
    reduce_critical_bytes:
      - "Minify HTML, CSS, JS"
      - "Compress with gzip/brotli"
      - "Remove unused CSS (PurgeCSS)"
    reduce_critical_path_length:
      - "Reduce number of round trips"
      - "Use HTTP/2 for multiplexing"
      - "Preconnect to required origins"
```

```html
<head>
  <!-- Preconnect to external origins -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://cdn.example.com" crossorigin />

  <!-- Preload critical resources -->
  <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/hero.avif" as="image" />

  <!-- Critical CSS inlined -->
  <style>
    /* Only above-the-fold styles here */
    body { margin: 0; font-family: system-ui; }
    .hero { min-height: 100vh; display: flex; align-items: center; }
  </style>

  <!-- Non-critical CSS loaded async -->
  <link rel="preload" href="/styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
  <noscript><link rel="stylesheet" href="/styles.css" /></noscript>

  <!-- JS loading strategies -->
  <script src="critical.js"></script>                <!-- blocks parsing -->
  <script src="analytics.js" async></script>          <!-- downloads in parallel, executes ASAP -->
  <script src="app.js" defer></script>                <!-- downloads in parallel, executes after HTML parsed -->
  <script type="module" src="module.js"></script>     <!-- deferred by default -->
</head>
```

## Lighthouse and Bundle Analysis
```
lighthouse:
  what: "Google's automated tool for auditing web page quality"
  categories:
    Performance: "Loading speed, interactivity, visual stability"
    Accessibility: "Screen readers, color contrast, ARIA"
    Best_Practices: "HTTPS, no deprecated APIs, error-free console"
    SEO: "Meta tags, crawlability, mobile-friendly"
  how_to_run:
    - "Chrome DevTools > Lighthouse tab"
    - "npx lighthouse https://example.com --view"
    - "PageSpeed Insights (web-based)"
    - "CI: lighthouse-ci (automated in pipeline)"

bundle_analysis:
  tools:
    webpack_bundle_analyzer: "Visual treemap of bundle contents"
    source_map_explorer: "Analyze from source maps"
    bundlephobia: "Check npm package sizes before installing"
    vite: "npx vite-bundle-visualizer"
  what_to_look_for:
    - Unexpectedly large dependencies
    - Duplicate packages (different versions)
    - Unused code that wasn't tree-shaken
    - Moment.js locale files (use date-fns or dayjs instead)
```

```bash
# Lighthouse CLI
npx lighthouse https://example.com --output=html --output-path=report.html

# Bundle analysis
npx webpack-bundle-analyzer dist/stats.json
npx source-map-explorer dist/main.js

# Check package size before installing
npx bundlephobia lodash        # full lodash: ~70KB
npx bundlephobia lodash-es     # tree-shakeable: only what you use

# Vite bundle visualization
npx vite-bundle-visualizer
```

```javascript
// Webpack config for bundle analysis
const BundleAnalyzerPlugin = require("webpack-bundle-analyzer").BundleAnalyzerPlugin;

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: "static",
      openAnalyzer: false,
      reportFilename: "bundle-report.html",
    }),
  ],
};
```

## SSR vs CSR vs SSG
```
rendering_strategies:
  CSR:
    full_name: Client-Side Rendering
    how: "Browser downloads empty HTML + JS bundle, JS renders everything"
    flow: "HTML shell -> download JS -> execute JS -> fetch data -> render"
    pros:
      - Rich interactivity
      - Great for dashboards/apps behind auth
      - Simple deployment (static files)
    cons:
      - Slow initial load (blank page until JS loads)
      - Poor SEO (crawlers may not execute JS)
      - Bad LCP (content not visible until JS runs)
    use_when: "Internal tools, dashboards, SPAs behind login"

  SSR:
    full_name: Server-Side Rendering
    how: "Server renders full HTML on each request, sends to browser, then hydrates with JS"
    flow: "Request -> server renders HTML -> send to browser -> download JS -> hydrate"
    pros:
      - Fast initial paint (full HTML immediately)
      - Great SEO (crawlers see full content)
      - Good for dynamic/personalized content
    cons:
      - Server load (renders on every request)
      - Slower TTFB than static
      - Hydration cost (JS still needs to download and run)
    use_when: "Dynamic pages, personalized content, e-commerce product pages"

  SSG:
    full_name: Static Site Generation
    how: "Pages pre-rendered at build time, served as static HTML"
    flow: "Build time: render all pages -> Deploy to CDN -> Serve static HTML"
    pros:
      - Fastest possible load (pre-built, CDN-served)
      - Best SEO
      - Cheapest to host (just static files)
      - Most secure (no server)
    cons:
      - Build time grows with page count
      - Not suitable for frequently changing data
      - Requires rebuild for content updates
    use_when: "Blogs, docs, marketing pages, content that rarely changes"

  ISR:
    full_name: Incremental Static Regeneration
    how: "SSG + background regeneration after a time interval"
    pros: "Best of SSG + SSR - fast static pages that update themselves"
    framework: "Next.js revalidate option"
    use_when: "Content that changes periodically (product catalog, blog)"

  streaming_ssr:
    what: "Server streams HTML in chunks as it's rendered"
    benefit: "User sees content progressively, not all at once"
    framework: "React 18 renderToPipeableStream, Next.js App Router"
```

## Practical Optimization Checklist
```
optimization_checklist:

  loading:
    - "[ ] Enable gzip/brotli compression"
    - "[ ] Use CDN for static assets"
    - "[ ] Implement code splitting (route-based at minimum)"
    - "[ ] Tree shake unused code (use ESM imports)"
    - "[ ] Minify HTML, CSS, JavaScript"
    - "[ ] Preload critical resources (fonts, hero image, key CSS)"
    - "[ ] Preconnect to required third-party origins"
    - "[ ] Use HTTP/2 or HTTP/3"

  images:
    - "[ ] Use modern formats (WebP/AVIF with fallbacks)"
    - "[ ] Serve responsive images (srcset + sizes)"
    - "[ ] Lazy load below-fold images"
    - "[ ] Set explicit width/height to prevent CLS"
    - "[ ] Compress images (Sharp, Squoosh)"
    - "[ ] Use fetchpriority=high for hero image"

  css:
    - "[ ] Inline critical CSS for above-the-fold content"
    - "[ ] Defer non-critical CSS loading"
    - "[ ] Remove unused CSS (PurgeCSS)"
    - "[ ] Avoid @import (use <link> instead)"
    - "[ ] Use content-visibility: auto for off-screen sections"

  javascript:
    - "[ ] Defer non-critical JS with defer/async"
    - "[ ] Avoid large synchronous tasks (break into chunks)"
    - "[ ] Remove unused dependencies"
    - "[ ] Audit bundle size regularly"
    - "[ ] Use dynamic import() for heavy features"

  fonts:
    - "[ ] Use font-display: swap (prevent invisible text)"
    - "[ ] Preload critical fonts"
    - "[ ] Subset fonts (only include needed characters)"
    - "[ ] Self-host fonts instead of Google Fonts (one less origin)"
    - "[ ] Use variable fonts to reduce file count"

  caching:
    - "[ ] Cache static assets with long max-age + content hash"
    - "[ ] Use stale-while-revalidate for API responses"
    - "[ ] Implement Service Worker for offline support"
    - "[ ] Set proper Cache-Control headers per resource type"

  monitoring:
    - "[ ] Run Lighthouse CI in deployment pipeline"
    - "[ ] Monitor Core Web Vitals with web-vitals library"
    - "[ ] Set performance budgets (max bundle size, max LCP)"
    - "[ ] Analyze bundle regularly with webpack-bundle-analyzer"
    - "[ ] Use Chrome DevTools Performance tab for runtime profiling"
```

```javascript
// Monitor Core Web Vitals in production
import { onLCP, onINP, onCLS } from "web-vitals";

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating, // "good", "needs-improvement", "poor"
    id: metric.id,
    page: window.location.pathname,
  });

  // Use sendBeacon for reliable delivery on page unload
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/analytics/vitals", body);
  } else {
    fetch("/api/analytics/vitals", { method: "POST", body, keepalive: true });
  }
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);

// Performance budget check in CI
// package.json
// "scripts": {
//   "build": "vite build",
//   "postbuild": "bundlesize"
// }
// "bundlesize": [
//   { "path": "dist/assets/*.js", "maxSize": "150 kB" },
//   { "path": "dist/assets/*.css", "maxSize": "20 kB" }
// ]
```
