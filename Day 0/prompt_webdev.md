# PROMPT — Web Development Notes

Write me new notes on Web Development in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world development example
- ASCII diagram if applicable
- Add gotchas and developer-related context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with architecture, code snippets, deployment steps, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete Web Development Glossary

### Batch 1 — Internet & Web Fundamentals
How the Internet Works
Client-Server Model
HTTP / HTTPS
HTTP Methods (GET, POST, PUT, PATCH, DELETE)
HTTP Status Codes (1xx–5xx)
HTTP Headers (Content-Type, Authorization, Cache-Control, CORS)
Request / Response Cycle
URL Structure (Protocol, Domain, Path, Query, Fragment)
DNS Resolution
TCP/IP
WebSockets
Server-Sent Events (SSE)
REST API
GraphQL
gRPC
API Versioning
Rate Limiting & Throttling
Idempotency
Webhooks
CORS (Cross-Origin Resource Sharing)

### Batch 2 — HTML & Semantic Web
HTML5
Semantic HTML (header, main, section, article, aside, footer, nav)
Forms & Input Types
Form Validation (HTML5 + Custom)
Accessibility (a11y) — ARIA Roles, Labels, Landmarks
SEO Basics (Title, Meta, OG Tags, Structured Data)
Responsive Meta Tag (Viewport)
HTML Entities
iframes
Shadow DOM
Web Components
Custom Elements
Template & Slot
Canvas & SVG
Lazy Loading (Images, iframes)
Preload / Prefetch / Preconnect

### Batch 3 — CSS Fundamentals & Layout
CSS Selectors (Element, Class, ID, Attribute, Pseudo)
Specificity & Cascade
Box Model (Content, Padding, Border, Margin)
Display (Block, Inline, Inline-Block, None, Contents)
Position (Static, Relative, Absolute, Fixed, Sticky)
Flexbox (Container & Items Properties)
CSS Grid (Template, Areas, Auto-fit, Minmax)
Responsive Design (Media Queries, Breakpoints)
Mobile-First vs Desktop-First
CSS Variables (Custom Properties)
Units (px, em, rem, vh, vw, %, ch)
Typography (font-family, line-height, letter-spacing)
Colors (Hex, RGB, HSL, oklch)
Gradients (Linear, Radial, Conic)
Transitions & Animations (@keyframes)
Transform (Translate, Rotate, Scale)
Z-Index & Stacking Context
Overflow & Scrolling
CSS Reset / Normalize
Container Queries

### Batch 4 — CSS Frameworks & Architecture
Tailwind CSS
Bootstrap
CSS Modules
CSS-in-JS (Styled Components, Emotion)
BEM Methodology
Utility-First CSS
Design Tokens
Theme System (Light/Dark Mode)
CSS Architecture (ITCSS, SMACSS)
PostCSS & Autoprefixer
Sass / SCSS
CSS Logical Properties
clamp() / min() / max()
Aspect Ratio
Scroll Snap
View Transitions API
@layer (Cascade Layers)

### Batch 5 — JavaScript Core
Variables (var, let, const)
Data Types (Primitive vs Reference)
Functions (Declaration, Expression, Arrow)
Scope (Global, Function, Block)
Hoisting
Closures
this Keyword
Prototypal Inheritance
Classes (ES6+)
Destructuring
Spread / Rest Operator
Template Literals
Modules (import / export, CommonJS vs ESM)
Array Methods (map, filter, reduce, forEach, find, some, every)
Object Methods (keys, values, entries, assign, spread)
Promises
Async / Await
Event Loop (Call Stack, Callback Queue, Microtask Queue)
Error Handling (try/catch, custom errors)
Generators & Iterators

### Batch 6 — JavaScript Advanced & DOM
DOM (Document Object Model)
DOM Manipulation (querySelector, createElement, append)
Event Handling (addEventListener, Event Delegation, Bubbling, Capturing)
Event.preventDefault() vs Event.stopPropagation()
Local Storage / Session Storage / Cookies
IndexedDB
Fetch API
AbortController
Intersection Observer
Mutation Observer
Resize Observer
Web Workers
Service Workers
Web APIs (Geolocation, Notification, Clipboard, File)
Debounce & Throttle
Proxy & Reflect
WeakMap & WeakSet
Symbol
Regular Expressions
Date Handling (Intl, date-fns, Day.js)

### Batch 7 — TypeScript
TypeScript Overview
Type Annotations (string, number, boolean, any, unknown, never, void)
Interfaces vs Types
Union & Intersection Types
Generics
Enums
Type Guards / Narrowing
Utility Types (Partial, Required, Pick, Omit, Record, Readonly)
Mapped Types
Conditional Types
Template Literal Types
Declaration Files (.d.ts)
tsconfig.json (strict, paths, baseUrl)
Type Inference
Discriminated Unions
Zod / Valibot (Runtime Validation)

### Batch 8 — React Fundamentals
React Overview
JSX
Components (Functional vs Class)
Props
State (useState)
useEffect (Side Effects, Cleanup, Dependencies)
useRef
useContext
useReducer
useMemo / useCallback
Custom Hooks
Component Lifecycle (Mount, Update, Unmount)
Conditional Rendering
Lists & Keys
Controlled vs Uncontrolled Components
Forms in React (React Hook Form, Formik)
Error Boundaries
Suspense & Lazy Loading
Portals
StrictMode

### Batch 9 — React Ecosystem & State Management
React Router (v6+)
Client-Side Routing vs Server-Side Routing
Nested Routes / Layouts
State Management Overview
Context API (Pros & Limitations)
Redux Toolkit (RTK)
Zustand
Jotai / Recoil
TanStack Query (React Query) — Caching, Mutations, Invalidation
SWR
Data Fetching Patterns (SSR, SSG, CSR, ISR)
React Server Components (RSC)
Server Actions
Streaming SSR
React Suspense for Data Fetching

### Batch 10 — Next.js & Full-Stack React
Next.js Overview
App Router vs Pages Router
File-Based Routing
Server Components vs Client Components
Server Actions (Form Handling)
API Routes / Route Handlers
Middleware
Static Site Generation (SSG) / getStaticProps
Server-Side Rendering (SSR) / getServerSideProps
Incremental Static Regeneration (ISR)
Image Optimization (next/image)
Font Optimization (next/font)
Metadata API (SEO)
Caching (Data Cache, Full Route Cache, Router Cache)
Parallel Routes / Intercepting Routes
Edge Runtime vs Node.js Runtime
Deployment (Vercel, Docker, Self-Hosted)

### Batch 11 — Backend & Databases
Node.js & Express
Middleware Pattern
Authentication (JWT, Session, OAuth2, Passport.js)
Authorization (RBAC, ABAC)
Password Hashing (bcrypt, Argon2)
SQL vs NoSQL
PostgreSQL
MongoDB
Prisma ORM / Drizzle ORM
Database Migrations
Connection Pooling
Transactions
Indexing
N+1 Query Problem
Redis (Caching, Sessions, Pub/Sub)
Message Queues (BullMQ, RabbitMQ)
File Upload (Multer, S3, Presigned URLs)
Email (Nodemailer, Resend, SendGrid)
Pagination (Offset, Cursor-Based)
Full-Text Search (PostgreSQL, Elasticsearch, Meilisearch)

### Batch 12 — Testing
Unit Testing (Jest, Vitest)
Integration Testing
End-to-End Testing (Playwright, Cypress)
Component Testing (React Testing Library)
Mocking (Functions, APIs, Modules)
Test Doubles (Stub, Mock, Spy, Fake)
Snapshot Testing
Code Coverage
TDD (Test-Driven Development)
BDD (Behavior-Driven Development)
Testing Pyramid
Flaky Tests
CI Testing Pipeline
Visual Regression Testing
Accessibility Testing (axe-core)
Load Testing (k6, Artillery)

### Batch 13 — DevOps & Deployment
Git & GitHub (Branching, PRs, Merge Strategies)
CI/CD (GitHub Actions, GitLab CI)
Docker (Dockerfile, Images, Containers, Compose)
Environment Variables (.env, Secrets)
Hosting (Vercel, Netlify, Railway, Fly.io, AWS, Azure)
Domain & DNS Setup
SSL / TLS Certificates (Let's Encrypt)
CDN (Cloudflare, AWS CloudFront)
Reverse Proxy (Nginx, Caddy)
Load Balancing
Logging (Winston, Pino, Structured Logs)
Monitoring (Sentry, Datadog, Grafana)
Performance Budgets
Lighthouse / Core Web Vitals (LCP, FID, CLS, INP)
Bundle Analysis (Webpack Bundle Analyzer)
Tree Shaking / Code Splitting
Edge Functions / Serverless Functions
Feature Flags (LaunchDarkly, Unleash)

### Batch 14 — Security
OWASP Top 10
XSS (Cross-Site Scripting) — Stored, Reflected, DOM
CSRF (Cross-Site Request Forgery)
SQL Injection
Content Security Policy (CSP)
HTTPS Everywhere
Secure Headers (Helmet.js)
Input Validation & Sanitization
Authentication Best Practices
Token Storage (HttpOnly Cookies vs localStorage)
Rate Limiting & Brute Force Protection
Dependency Vulnerabilities (npm audit, Snyk)
CORS Misconfiguration
Clickjacking
Subresource Integrity (SRI)
Secrets Management

---

## PART 2 — Project Case Studies

### Case Study 1: Full-Stack SaaS Dashboard (MetricFlow)

Build a multi-tenant analytics dashboard where:
- Users sign up, create organizations, invite team members
- Connect data sources (API keys) and view real-time metrics
- Dashboard with charts (line, bar, pie), filterable by date range
- Role-based access: Admin, Editor, Viewer
- Stripe integration for subscription billing
- Email notifications for threshold alerts

**Cover in the case study:**
- Architecture diagram (ASCII): Frontend → API → DB → Queue → Workers
- Tech stack: Next.js (App Router), TypeScript, Prisma, PostgreSQL, Redis, BullMQ, Stripe, Resend
- Code snippets: auth middleware, RBAC decorator, Stripe webhook handler, real-time chart component
- Database schema design (multi-tenant: shared DB, tenant column)
- Testing strategy: unit (Vitest), integration (Supertest), E2E (Playwright)
- CI/CD pipeline (GitHub Actions → Docker → Railway/AWS)
- Performance: caching strategy, pagination, query optimization
- Security: CSRF, XSS, rate limiting, secure headers
- Lessons learned & production gotchas

### Case Study 2: Real-Time Collaborative Document Editor (CollabDocs)

Build a Google Docs-like collaborative editor where:
- Users create and share documents with live collaboration
- Real-time cursors, text editing, and presence indicators
- Rich text editor with formatting (bold, italic, headings, lists, code blocks)
- Version history with diff viewer
- Comments and mentions
- Offline support with sync on reconnect

**Cover in the case study:**
- Architecture diagram (ASCII): Client → WebSocket Server → CRDT/OT Engine → DB
- Tech stack: Next.js, TypeScript, Tiptap/ProseMirror, Yjs (CRDT), WebSocket (Hocuspocus), PostgreSQL, S3
- Code snippets: Yjs provider setup, awareness protocol (cursors), WebSocket server, version snapshot
- Conflict resolution: CRDT vs OT comparison, why Yjs
- Offline mode: IndexedDB persistence, sync protocol
- Testing: collaborative editing tests, WebSocket mocking
- Deployment: WebSocket scaling (sticky sessions, Redis pub/sub)
- Security: document permissions, input sanitization in rich text
- Lessons learned & production gotchas
