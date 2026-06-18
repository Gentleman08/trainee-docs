# Batch 12 — Testing
> Building confidence that your code does what it's supposed to — at every level.

Testing turns "I think it works" into "I know it works." This batch covers every layer of the testing stack — from tiny unit tests to full browser automation — so you can ship with confidence.

---

## 1. Unit Testing (Jest, Vitest)

**One-line definition:** Testing a single function or module in complete isolation from everything else.

### Real-World Dev Example
```js
// math.js
export function add(a, b) { return a + b; }

// math.test.js (Jest or Vitest — syntax is identical)
import { add } from './math';

test('adds two numbers correctly', () => {
  expect(add(2, 3)).toBe(5);
  expect(add(-1, 1)).toBe(0);
});
```
Run with `npx jest` or `npx vitest`.

### Gotchas & Dev Context
- **Jest** ships with Create React App; **Vitest** is the Vite-native choice — faster, ESM-first.
- Each `test()` block should test one behaviour, not a laundry list.
- Use `describe()` to group related tests: `describe('add()', () => { … })`.
- Avoid testing implementation details (internal variable names). Test behaviour.
- `toBe` uses `===`; use `toEqual` for objects/arrays (deep equality).

### Production FAQ
**Q: Jest or Vitest for a new project?**
A: Vitest if you're on Vite; Jest otherwise. Both share the same API so switching is low effort.

**Q: Should every function have a unit test?**
A: Test logic that could break — pure functions, edge cases, business rules. Skip trivial getters/setters.

**Q: How do I run only one test file?**
A: `npx jest path/to/file.test.js` or `npx vitest path/to/file.test.js`.

---

## 2. Integration Testing

**One-line definition:** Testing how multiple units work together — without spinning up a real browser or server.

### Real-World Dev Example
```js
// Tests a service that calls a repository — both real, DB is mocked
import { getUserById } from './userService';
import { db } from './db'; // mocked module

jest.mock('./db');
db.findUser.mockResolvedValue({ id: 1, name: 'Alice' });

test('getUserById returns formatted user', async () => {
  const user = await getUserById(1);
  expect(user.name).toBe('Alice');
  expect(db.findUser).toHaveBeenCalledWith(1);
});
```

### ASCII Diagram
```
[ Unit A ]──┐
            ├──► [ Integration Test ] ──► checks combined output
[ Unit B ]──┘
```

### Gotchas & Dev Context
- Integration tests sit between unit and E2E — they catch wiring bugs that unit tests miss.
- It's fine to use a real database if you spin up a test DB (e.g., SQLite in memory).
- Slower than unit tests; keep the suite focused on critical paths.
- React Testing Library tests are often called "integration tests" — they render components with real hooks.

### Production FAQ
**Q: My unit tests all pass but the feature is broken. Why?**
A: Units were tested in isolation. Integration tests catch the gaps *between* units — how they pass data to each other.

**Q: Should I hit a real API in integration tests?**
A: No — mock external HTTP calls (use MSW or `jest.mock`). You own the test environment; third-party APIs are unpredictable.

---

## 3. End-to-End Testing (Playwright, Cypress)

**One-line definition:** Driving a real browser through your app like a real user — click, type, assert.

### Real-World Dev Example
```js
// Playwright — tests/login.spec.ts
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.fill('[name="email"]', 'alice@example.com');
  await page.fill('[name="password"]', 'secret');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('h1')).toHaveText('Welcome, Alice');
});
```

### Gotchas & Dev Context
- **Playwright** — cross-browser (Chromium, Firefox, WebKit), faster, better async support, Microsoft-backed.
- **Cypress** — Chrome-first, great DX, real-time interactive runner.
- E2E tests are the slowest — run them in CI, not on every keystroke.
- Always use `data-testid` attributes for selectors; CSS classes can change.
- Flakiness is common (see §12). Use `waitFor` / `expect().toBeVisible()` over arbitrary `sleep()`.

### Production FAQ
**Q: Playwright or Cypress?**
A: Playwright for multi-browser coverage and speed; Cypress for teams who love its interactive GUI.

**Q: Should E2E tests cover every page?**
A: No — cover critical user journeys (login, checkout, signup). Unit/integration cover the rest.

**Q: My E2E tests fail in CI but pass locally. What now?**
A: Check viewport size, timing, and environment variables. Add `--headed` locally to mirror CI rendering.

---

## 4. Component Testing (React Testing Library)

**One-line definition:** Rendering a UI component in isolation and asserting on what the user sees and can interact with.

### Real-World Dev Example
```jsx
// Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

test('calls onClick when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Submit</Button>);

  fireEvent.click(screen.getByRole('button', { name: /submit/i }));

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

### Gotchas & Dev Context
- RTL philosophy: query by **role, label, text** — not class names or IDs. This mirrors how users interact.
- Use `screen.getByRole('button')` over `container.querySelector('button')`.
- `userEvent` (from `@testing-library/user-event`) is more realistic than `fireEvent` — prefer it.
- Avoid testing internal state. If you can't see it in the DOM, neither can the user.
- Works with Jest or Vitest — install `@testing-library/react` and `@testing-library/jest-dom`.

### Production FAQ
**Q: Is RTL a replacement for E2E tests?**
A: No — RTL doesn't test routing, real network calls, or multi-page flows. It's one level below E2E.

**Q: How do I test a component that fetches data?**
A: Wrap it in a mock provider or use MSW (Mock Service Worker) to intercept fetch/axios calls.

**Q: `getBy` vs `queryBy` vs `findBy` — which to use?**
A: `getBy` — throws if missing (good for expected elements). `queryBy` — returns null (good for asserting absence). `findBy` — async, awaits appearance.

---

## 5. Mocking (Functions, APIs, Modules)

**One-line definition:** Replacing real dependencies with fake, controlled versions so tests stay fast and predictable.

### Real-World Dev Example
```js
// Mock a module
jest.mock('./analytics', () => ({ track: jest.fn() }));

// Mock an API call
import axios from 'axios';
jest.mock('axios');
axios.get.mockResolvedValue({ data: { user: 'Alice' } });

// Mock a function
const fetchUser = jest.fn().mockReturnValue({ id: 1, name: 'Alice' });
expect(fetchUser()).toEqual({ id: 1, name: 'Alice' });
expect(fetchUser).toHaveBeenCalled();
```

### ASCII Diagram
```
Real Code              Test Environment
─────────────────────────────────────────
calls → stripe.charge()   →  jest.fn() returns { success: true }
calls → sendEmail()       →  jest.fn() (no-op, just recorded)
```

### Gotchas & Dev Context
- `jest.fn()` — tracks calls. `jest.spyOn()` — wraps an existing method. `jest.mock()` — replaces a whole module.
- Reset mocks between tests: `afterEach(() => jest.clearAllMocks())`.
- Over-mocking creates brittle tests that pass even when real code is broken.
- For HTTP, prefer **MSW (Mock Service Worker)** — it intercepts at the network layer, works in browser and Node.

### Production FAQ
**Q: When should I use MSW instead of `jest.mock`?**
A: When you want to mock HTTP across components/hooks without coupling to the fetch implementation.

**Q: My mock isn't resetting between tests. Why?**
A: Use `jest.clearAllMocks()` in `afterEach`, or set `clearMocks: true` in `jest.config.js`.

---

## 6. Test Doubles (Stub, Mock, Spy, Fake)

**One-line definition:** The four flavours of "stand-in" objects used to replace real dependencies in tests.

### Real-World Dev Example
```js
// STUB — returns canned data, no behaviour tracking
const stubDb = { findUser: () => ({ id: 1, name: 'Alice' }) };

// MOCK — tracks calls, can assert on them
const mockEmail = jest.fn();
mockEmail('alice@example.com');
expect(mockEmail).toHaveBeenCalledWith('alice@example.com');

// SPY — wraps real implementation, lets you observe it
const spy = jest.spyOn(console, 'log').mockImplementation(() => {});

// FAKE — working lightweight implementation (e.g., in-memory DB)
const fakeDb = new Map(); // real insert/lookup, no persistence
```

### ASCII Diagram
```
Double Type │ Has logic? │ Tracks calls? │ Use when…
────────────┼────────────┼───────────────┼──────────────────────────
Stub        │ No         │ No            │ just need a return value
Mock        │ No         │ Yes           │ need to verify interactions
Spy         │ Yes (real) │ Yes           │ observe without replacing
Fake        │ Yes (lite) │ No            │ replace DB/cache in tests
```

### Gotchas & Dev Context
- The terms are often used interchangeably in everyday speech, but knowing the distinctions helps in code reviews.
- In Jest: `jest.fn()` = mock/stub hybrid; `jest.spyOn()` = spy.
- Fakes are expensive to write but make integration tests much more realistic.

### Production FAQ
**Q: Is a Jest mock the same as a mock in the classic sense?**
A: Kind of — `jest.fn()` is actually a mock-stub hybrid: it can return canned values AND track calls.

**Q: When is a Fake better than a Mock?**
A: When you're testing complex interactions (like multiple DB reads/writes) — a full fake is more reliable than stitching together many `mockReturnValue` calls.

---

## 7. Snapshot Testing

**One-line definition:** Serializing a component's rendered output to a file, then failing if it changes unexpectedly.

### Real-World Dev Example
```jsx
// Badge.test.jsx
import { render } from '@testing-library/react';
import Badge from './Badge';

test('Badge renders correctly', () => {
  const { asFragment } = render(<Badge label="New" color="green" />);
  expect(asFragment()).toMatchSnapshot();
});
```
First run: creates `__snapshots__/Badge.test.jsx.snap`.
Later runs: diffs against that snapshot — fails on unintended changes.

Update snapshots intentionally: `npx jest --updateSnapshot`.

### Gotchas & Dev Context
- Great for catching accidental UI regressions; terrible as a substitute for real assertions.
- Snapshots break on trivial changes (whitespace, className order) — can train devs to blindly update them.
- Keep snapshots small — snapshot a sub-component, not a whole page.
- Commit `.snap` files to version control so CI can diff them.
- Consider **inline snapshots** (`toMatchInlineSnapshot`) for small outputs — keeps test + snapshot in one file.

### Production FAQ
**Q: Should I delete all my snapshots and use RTL assertions instead?**
A: Mostly yes for behaviour. Keep snapshots for pure presentational components where the rendered HTML *is* the contract.

**Q: A snapshot failed — should I just run `--updateSnapshot`?**
A: Only after reviewing the diff. A snapshot failure is a signal — investigate before accepting.

---

## 8. Code Coverage

**One-line definition:** A metric showing what percentage of your source code is executed when your tests run.

### Real-World Dev Example
```bash
# Jest — generate coverage report
npx jest --coverage

# Output:
# File       | % Stmts | % Branch | % Funcs | % Lines
# Button.jsx |    92   |    75    |   100   |   91
```
Coverage report is in `./coverage/lcov-report/index.html` — open it in a browser for a visual line-by-line view.

### ASCII Diagram
```
Source Lines      Tests Hit?    Coverage
───────────────────────────────────────
line 1: if (x)   ✓ true path   │
line 2:   doA()  ✓             │ 75% branch
line 3: else      ✗ false path  │   coverage
line 4:   doB()  ✗             │
```

### Gotchas & Dev Context
- 100% coverage does not mean bug-free — it means every line ran, not that every edge case is correct.
- Track **branch coverage** (both `if` and `else` paths) — more meaningful than line coverage.
- Set thresholds in `jest.config.js`: `coverageThreshold: { global: { lines: 80 } }`.
- Exclude generated files, config, and type definitions from coverage.
- Coverage is a team health metric, not a target to game.

### Production FAQ
**Q: What's a good coverage target?**
A: 70–85% is healthy for most apps. Anything above 90% often means you're testing trivial code to hit a number.

**Q: Why does Istanbul (Jest's coverage tool) show 100% but my feature still broke?**
A: Your tests executed the line but didn't assert the correct output. Coverage ≠ correctness.

---

## 9. TDD (Test-Driven Development)

**One-line definition:** Write the failing test first, then write only enough code to make it pass, then refactor.

### Real-World Dev Example
```js
// Step 1: Write failing test
test('slugify converts spaces to hyphens', () => {
  expect(slugify('Hello World')).toBe('hello-world'); // FAILS — function doesn't exist yet
});

// Step 2: Write minimal code
export function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-');
}
// Test now passes ✓

// Step 3: Refactor — handle special characters, etc.
```

### ASCII Diagram
```
  ┌──────────┐
  │  RED     │ ← Write failing test
  └────┬─────┘
       ▼
  ┌──────────┐
  │  GREEN   │ ← Write minimum code to pass
  └────┬─────┘
       ▼
  ┌──────────┐
  │ REFACTOR │ ← Clean up, tests still green
  └────┬─────┘
       │ repeat
       ▼
```

### Gotchas & Dev Context
- TDD is a **design technique**, not just a testing technique — it forces you to think about the API before implementation.
- Hard to apply to UI or exploratory features — use it for business logic and utilities.
- Don't write more code than needed to make the test green (YAGNI principle).
- TDD doesn't eliminate integration bugs — you still need higher-level tests.

### Production FAQ
**Q: Is TDD always slower?**
A: Initially yes — but it pays off by reducing debugging time and rework later.

**Q: Do I need 100% TDD on a real project?**
A: No. Apply it selectively — complex algorithms, bug fixes (write a test that reproduces the bug first), and critical business logic.

---

## 10. BDD (Behavior-Driven Development)

**One-line definition:** Writing tests in plain English (Given/When/Then) so that non-developers can read and validate them.

### Real-World Dev Example
```js
// Using Jest with a BDD-style describe block
describe('Shopping Cart', () => {
  describe('when a user adds an item', () => {
    it('should increase the item count by 1', () => {
      const cart = new Cart();
      cart.addItem({ id: 1, name: 'Book', price: 12 });
      expect(cart.itemCount).toBe(1);
    });

    it('should update the total price', () => {
      const cart = new Cart();
      cart.addItem({ id: 1, name: 'Book', price: 12 });
      expect(cart.total).toBe(12);
    });
  });
});
```
Full BDD tools like **Cucumber.js** use `.feature` files with Gherkin syntax (`Given/When/Then`).

### ASCII Diagram
```
Feature: User Login
  Scenario: Valid credentials
    Given a registered user "alice@example.com"
    When  they submit the login form with correct password
    Then  they should be redirected to /dashboard
```

### Gotchas & Dev Context
- BDD's value is in the **conversation** it forces between devs, QA, and product — not just the syntax.
- Plain Jest/Vitest with descriptive `describe`/`it` strings is "soft BDD" — sufficient for most teams.
- Full Cucumber/Gherkin adds complexity; only adopt if non-dev stakeholders actively write scenarios.
- `it('should…')` is idiomatic BDD-style naming.

### Production FAQ
**Q: Is BDD the same as TDD?**
A: Related but different — TDD is about the development cycle; BDD is about the language and collaboration model.

**Q: Do we need Cucumber to do BDD?**
A: No. Descriptive `describe/it` blocks in Jest capture most of BDD's value without the tooling overhead.

---

## 11. Testing Pyramid

**One-line definition:** A model prescribing that you should have many unit tests, fewer integration tests, and very few E2E tests.

### ASCII Diagram
```
        ▲
       /E2E\          ← Few, slow, expensive
      /──────\
     /  Integ \       ← Some, medium speed
    /────────────\
   /   Unit Tests  \  ← Many, fast, cheap
  /──────────────────\
```

### Real-World Dev Example
A typical React app might have:
- **500 unit tests** (utilities, hooks, reducers) — run in ~5s
- **80 integration tests** (component + API mock) — run in ~30s
- **20 E2E tests** (critical paths in browser) — run in ~3 min

### Gotchas & Dev Context
- The pyramid is a **guideline**, not a law — some teams use a "testing trophy" (more integration, fewer unit).
- The higher up the pyramid = slower CI, harder to debug failures.
- If you have more E2E tests than unit tests, your CI will be painfully slow.
- The "ice cream cone" anti-pattern is the pyramid flipped — mostly E2E, no unit tests. Avoid it.
- Mike Cohn coined the original pyramid; Kent Dodds popularised the "trophy" variant for UI apps.

### Production FAQ
**Q: Should I always follow the pyramid exactly?**
A: Use it as a starting heuristic. Heavy UI apps often benefit from more integration/component tests (the trophy shape).

**Q: What if my unit tests are passing but E2E keeps failing?**
A: You have integration gaps — missing tests for how units connect. Add integration coverage on failing paths.

---

## 12. Flaky Tests

**One-line definition:** Tests that pass or fail unpredictably without any code changes — the bane of CI pipelines.

### Real-World Dev Example
```js
// FLAKY — relies on timing
test('loads data', async () => {
  render(<UserProfile />);
  await new Promise(r => setTimeout(r, 500)); // ← fragile!
  expect(screen.getByText('Alice')).toBeInTheDocument();
});

// FIXED — waits for actual DOM update
test('loads data', async () => {
  render(<UserProfile />);
  expect(await screen.findByText('Alice')).toBeInTheDocument(); // ← waits intelligently
});
```

### Gotchas & Dev Context
- Common causes: hardcoded timeouts, shared test state, animation timing, network calls, random data, date/time dependencies.
- Fix strategy: isolate, retry 3x to confirm flakiness, then eliminate the root cause.
- Playwright has `--retries` and a built-in flakiness report.
- Never merge flaky tests — they erode trust in the entire test suite ("the boy who cried wolf").
- Track flaky tests in a dedicated issue label so they don't get ignored.

### Production FAQ
**Q: A test fails 1 in 10 runs. Can I just add a retry?**
A: Retries mask the problem temporarily. Investigate and fix the root cause — retries should be a last resort for genuinely non-deterministic environments.

**Q: How do I find which tests are flaky?**
A: Run the full suite 5–10 times in CI and compare results. Playwright and Jest have plugins for flakiness detection.

---

## 13. CI Testing Pipeline

**One-line definition:** Automatically running your test suite on every push or pull request using a server — catching regressions before they merge.

### Real-World Dev Example
```yaml
# .github/workflows/test.yml (GitHub Actions)
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm test -- --coverage
      - run: npx playwright install --with-deps
      - run: npx playwright test
```

### ASCII Diagram
```
Push to PR
    │
    ▼
GitHub Actions triggered
    │
    ├── npm test (unit + integration)  ──► ✓ / ✗
    ├── playwright test (E2E)           ──► ✓ / ✗
    └── coverage threshold check        ──► ✓ / ✗
    │
    ▼
Merge allowed only if all ✓
```

### Gotchas & Dev Context
- Use `npm ci` (not `npm install`) in CI — reproducible installs from `package-lock.json`.
- Cache `node_modules` between runs to cut pipeline time.
- Parallelise slow test suites with Jest `--maxWorkers` or Playwright sharding.
- Set required status checks in GitHub so PRs can't merge without green tests.
- Store test artifacts (coverage HTML, Playwright traces) as CI artifacts for debugging.

### Production FAQ
**Q: CI passes but my local tests fail. What gives?**
A: Environment differences — Node version, OS path separators, missing env vars. Always test locally with `npm ci` too.

**Q: My CI pipeline takes 20 minutes. How do I speed it up?**
A: Cache dependencies, parallelise test files, split unit and E2E into separate jobs, only run E2E on `main`.

---

## 14. Visual Regression Testing

**One-line definition:** Automatically comparing screenshots of your UI before and after a change to catch unintended visual differences.

### Real-World Dev Example
```js
// Playwright visual comparison
import { test, expect } from '@playwright/test';

test('homepage looks correct', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100, // allow minor anti-aliasing differences
  });
});
```
First run: creates baseline screenshots.
Later runs: pixel-diffs against baseline — fails if difference exceeds threshold.

### Gotchas & Dev Context
- Tools: **Playwright** (built-in), **Percy**, **Chromatic** (Storybook-native), **reg-suit**.
- Screenshots differ across OS/GPU — always generate baselines in CI (not locally on Mac vs Linux).
- Mask dynamic content (timestamps, ads) with `page.locator('.ad').fill('')` before screenshotting.
- Visual regression tests are expensive to maintain — apply to core layouts, not every component.
- Chromatic integrates with Storybook and shows visual diffs in PRs as UI reviews.

### Production FAQ
**Q: How is this different from snapshot testing?**
A: Snapshot testing serialises HTML/JSX to text. Visual regression captures actual rendered pixels — catches CSS, font, and layout bugs that HTML snapshots miss.

**Q: Should I run visual tests on every PR?**
A: Yes, but gate them separately from unit tests. Use a tool like Chromatic that runs them in the background and flags only meaningful diffs.

---

## 15. Accessibility Testing (axe-core)

**One-line definition:** Automatically checking your UI against WCAG accessibility rules — missing labels, poor contrast, broken ARIA — so everyone can use your app.

### Real-World Dev Example
```jsx
// Using jest-axe
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import LoginForm from './LoginForm';

expect.extend(toHaveNoViolations);

test('LoginForm has no accessibility violations', async () => {
  const { container } = render(<LoginForm />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

Install: `npm install --save-dev jest-axe axe-core`.

### Gotchas & Dev Context
- **axe-core** catches ~57% of WCAG issues automatically — manual testing still required for the rest.
- Common violations: missing `alt` text, unlabelled form inputs, insufficient colour contrast, missing landmark roles.
- Use **Playwright + axe** for full-page checks: `@axe-core/playwright`.
- Also test keyboard navigation manually — axe can't fully catch focus order issues.
- Accessibility is a legal requirement in many countries (ADA, EU EAA). Failing audits can have consequences.

### Production FAQ
**Q: Does axe passing mean my site is fully accessible?**
A: No — automated tools catch structural issues. Real screen-reader testing (NVDA, VoiceOver) is still essential.

**Q: What are the most common axe violations in React apps?**
A: Missing form labels, images without `alt`, buttons without accessible names, and insufficient colour contrast.

---

## 16. Load Testing (k6, Artillery)

**One-line definition:** Simulating many concurrent users hitting your API or app to find performance bottlenecks before real traffic does.

### Real-World Dev Example
```js
// k6 script — k6.io
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,          // 100 virtual users
  duration: '30s',   // for 30 seconds
};

export default function () {
  const res = http.get('https://api.example.com/products');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```
Run: `k6 run script.js` — outputs p95 response time, RPS, error rate.

### ASCII Diagram
```
k6 Engine
   │
   ├── Virtual User 1 ──► GET /api/products
   ├── Virtual User 2 ──► GET /api/products
   ├── ...
   └── Virtual User 100 ► GET /api/products
              │
              ▼
        Your API Server
        (watch: CPU, memory, DB connections, response time)
```

### Gotchas & Dev Context
- **k6** — scriptable in JS, great CLI output, cloud mode available. Best for API load testing.
- **Artillery** — YAML config + JS hooks, good for complex scenarios with multiple steps.
- Never run load tests against production without a maintenance window and rate-limit safeguards.
- Key metrics: **p95/p99 latency**, **error rate**, **throughput (RPS)**, **time to first byte**.
- Load test in a staging environment that mirrors production infrastructure.

### Production FAQ
**Q: What's the difference between load testing and stress testing?**
A: Load testing checks performance under expected traffic. Stress testing pushes beyond limits to find the breaking point.

**Q: k6 or Artillery?**
A: k6 for pure API/HTTP testing with rich metrics. Artillery if you need complex multi-step user journeys or WebSocket testing.

---

*End of Batch 12 — Testing*
