# Batch 9 — React Ecosystem & State Management
> Routing, data fetching, and managing state at scale in React apps.

---

## 1. React Router (v6+)

**One-line definition:** A library that lets React apps switch between "pages" without reloading the browser.

### Real-World Dev Example
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/users/:id" element={<UserProfile />} />
      </Routes>
    </BrowserRouter>
  );
}
```
`:id` is a URL param — `useParams()` reads it inside `UserProfile`.

### ASCII Diagram
```
URL: /users/42
        |
   React Router
        |
   <Route path="/users/:id">
        |
   <UserProfile id="42" />
```

### Gotchas & Dev Context
- v6 replaced `<Switch>` with `<Routes>` — old tutorials using `<Switch>` are outdated.
- Use `<Link>` instead of `<a>` tags to avoid full page reloads.
- `useNavigate()` replaces `useHistory()` from v5.
- `<NavLink>` auto-applies an `active` class — great for nav menus.

### Production FAQ
**Q: How do I protect a route (auth guard)?**  
A: Wrap `<Route>` with a component that checks auth state and redirects with `<Navigate to="/login" />` if unauthenticated.

**Q: My routes work locally but 404 on deploy. Why?**  
A: Your server doesn't know about client-side routes. Configure it to serve `index.html` for all routes (e.g., `nginx try_files $uri /index.html`).

---

## 2. Client-Side Routing vs Server-Side Routing

**One-line definition:** CSR handles navigation in the browser via JS; SSR fetches a new HTML page from the server on every navigation.

### ASCII Diagram
```
CLIENT-SIDE ROUTING            SERVER-SIDE ROUTING
─────────────────────          ────────────────────
User clicks link               User clicks link
       │                              │
JS intercepts click            Browser sends GET /about
       │                              │
Swaps components in-place      Server renders HTML
       │                              │
URL updates (no reload)        Browser loads new page
```

### Real-World Dev Example
- **CSR:** React SPA — clicking "About" swaps the component, no network round-trip.
- **SSR:** Traditional Rails/Django app — every click fetches a new HTML document.

### Gotchas & Dev Context
- CSR = faster navigation after initial load, but poor SEO out of the box.
- SSR = better SEO, slower navigations (network round-trip each time).
- Modern frameworks (Next.js) **blend both** — SSR the first page, CSR the rest.
- CSR apps need a spinner/skeleton for slow networks since JS must load first.

### Production FAQ
**Q: Which should I pick for an e-commerce site?**  
A: SSR or hybrid (Next.js). Product pages need SEO and fast first load.

**Q: Does CSR hurt Core Web Vitals?**  
A: Yes — LCP suffers because content renders after JS loads. Use SSR/SSG for critical pages.

---

## 3. Nested Routes / Layouts

**One-line definition:** Child routes rendered *inside* a parent route's component — perfect for shared layouts (nav + sidebar).

### Real-World Dev Example
```jsx
<Routes>
  <Route path="/app" element={<AppLayout />}>   {/* shared shell */}
    <Route index element={<Dashboard />} />
    <Route path="settings" element={<Settings />} />
    <Route path="profile" element={<Profile />} />
  </Route>
</Routes>

// AppLayout.jsx
function AppLayout() {
  return (
    <div>
      <Sidebar />
      <Outlet />   {/* child route renders here */}
    </div>
  );
}
```

### ASCII Diagram
```
/app/settings
│
├── AppLayout (Sidebar + Navbar always visible)
│       └── <Outlet />
│               └── <Settings />  ← swapped per route
```

### Gotchas & Dev Context
- `<Outlet />` is the slot where child routes render — forget it and child pages are blank.
- Index routes (`index` prop) render when the parent path matches exactly.
- Nesting can go many levels deep — keep it readable, 2-3 levels max.
- Great pattern: one layout for public pages, one for authenticated dashboard.

### Production FAQ
**Q: Can I have different layouts for auth vs public routes?**  
A: Yes — create two parent routes each with their own layout component wrapping an `<Outlet />`.

**Q: How do I pass data from a layout to its child routes?**  
A: Use React Context, or in v6.4+ use route `loader` functions with `useOutletContext()`.

---

## 4. State Management Overview

**One-line definition:** "State management" means deciding *where* data lives and *how* it flows across your component tree.

### ASCII Diagram
```
         Component Tree
         ─────────────
              App
             /   \
          NavBar  Dashboard
                  /      \
              Chart     UserList
                            │
                         UserCard

Local state → only one component needs it (useState)
Lifted state → 2-3 sibling components share it
Global state → many distant components need it (Context / Redux / Zustand)
```

### Real-World Dev Example
| Data | Best fit |
|---|---|
| Form input value | `useState` (local) |
| Auth user / theme | Context API or Zustand |
| Complex server cache | TanStack Query |
| Large app with many slices | Redux Toolkit |

### Gotchas & Dev Context
- **Don't over-engineer.** Start with `useState`, lift state, then reach for global tools only when needed.
- Server state (API data) ≠ UI state (modal open/closed) — treat them differently.
- Mixing server cache in Redux leads to duplication & staleness bugs. Use React Query for server state.

### Production FAQ
**Q: What's the most common state management mistake?**  
A: Putting everything in Redux/Context, including server data that TanStack Query handles better.

**Q: Can I use multiple state libraries together?**  
A: Yes — Zustand for UI state + TanStack Query for server state is a popular, lean combo.

---

## 5. Context API (Pros & Limitations)

**One-line definition:** React's built-in way to share state across components without prop-drilling.

### Real-World Dev Example
```jsx
const ThemeContext = createContext('light');

function App() {
  const [theme, setTheme] = useState('dark');
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Navbar />
      <Main />
    </ThemeContext.Provider>
  );
}

// anywhere in the tree:
function Navbar() {
  const { theme } = useContext(ThemeContext);
  return <nav className={theme}>...</nav>;
}
```

### Gotchas & Dev Context
- **Re-render problem:** Every consumer re-renders when *any* part of the context value changes. Split contexts by concern (e.g., `AuthContext`, `ThemeContext`).
- Not a state manager — it's a transport mechanism. It still needs `useState`/`useReducer` behind it.
- For high-frequency updates (mouse position, animations) Context is too slow — use Zustand or refs.
- `memo()` + context splitting helps but gets complex fast.

### Production FAQ
**Q: When should I stop using Context and switch to Zustand/Redux?**  
A: When you have frequent updates causing widespread re-renders, complex update logic, or need devtools for debugging.

**Q: Can I have multiple contexts?**  
A: Yes, and you *should* — one per domain (auth, cart, theme) to minimize unnecessary re-renders.

---

## 6. Redux Toolkit (RTK)

**One-line definition:** The modern, official way to write Redux — removes boilerplate and adds useful utilities out of the box.

### Real-World Dev Example
```js
// cartSlice.js
import { createSlice } from '@reduxjs/toolkit';

const cartSlice = createSlice({
  name: 'cart',
  initialState: { items: [] },
  reducers: {
    addItem: (state, action) => { state.items.push(action.payload); },
    removeItem: (state, action) => {
      state.items = state.items.filter(i => i.id !== action.payload);
    },
  },
});

export const { addItem, removeItem } = cartSlice.actions;
export default cartSlice.reducer;

// In component:
const dispatch = useDispatch();
dispatch(addItem({ id: 1, name: 'Shirt' }));
```

### ASCII Diagram
```
Component → dispatch(action) → Reducer → New State → Component re-renders
```

### Gotchas & Dev Context
- RTK uses Immer under the hood — you can "mutate" state directly in reducers (it's actually immutable).
- `createAsyncThunk` handles API calls with `pending/fulfilled/rejected` states automatically.
- **RTK Query** (bundled) is RTK's own data-fetching layer — a direct competitor to React Query.
- Redux DevTools extension is incredibly useful for time-travel debugging.

### Production FAQ
**Q: Is Redux overkill for small apps?**  
A: Yes. Use `useState` + Context for small apps. Redux shines with large teams, complex update logic, and audit trails.

**Q: RTK Query vs TanStack Query?**  
A: RTK Query integrates seamlessly with existing Redux stores; TanStack Query is framework-agnostic and more feature-rich for complex caching.

---

## 7. Zustand

**One-line definition:** A tiny, fast global state library — like Redux but with almost zero boilerplate.

### Real-World Dev Example
```js
import { create } from 'zustand';

const useCartStore = create((set) => ({
  items: [],
  addItem: (item) => set((state) => ({ items: [...state.items, item] })),
  clearCart: () => set({ items: [] }),
}));

// In any component — no Provider needed!
function Cart() {
  const { items, clearCart } = useCartStore();
  return <button onClick={clearCart}>Clear ({items.length})</button>;
}
```

### Gotchas & Dev Context
- **No Provider required** — the store lives outside React's tree. This is Zustand's killer feature.
- Components only re-render when the slice of state they *subscribe to* changes — very efficient.
- Supports middleware: `persist` (localStorage), `devtools` (Redux DevTools), `immer`.
- Works great alongside TanStack Query: Zustand for UI state, RQ for server state.
- Bundle size ~1KB — negligible.

### Production FAQ
**Q: Can Zustand replace Redux entirely?**  
A: For most apps, yes. You lose some structure and strict patterns, which can be a trade-off in very large teams.

**Q: How do I persist state across refreshes?**  
A: Wrap the store with `persist` middleware: `create(persist(fn, { name: 'cart-storage' }))`.

---

## 8. Jotai / Recoil

**One-line definition:** Atom-based state libraries — state is split into tiny independent units (atoms) instead of one big store.

### Real-World Dev Example (Jotai)
```js
import { atom, useAtom } from 'jotai';

const countAtom = atom(0);
const doubleAtom = atom((get) => get(countAtom) * 2); // derived atom

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const [double] = useAtom(doubleAtom);
  return <button onClick={() => setCount(c => c + 1)}>{count} (×2 = {double})</button>;
}
```

### ASCII Diagram
```
Atom A ──► Derived Atom C ──► Component X
Atom B ──►
```

### Gotchas & Dev Context
- **Jotai** is simpler, has no boilerplate, works with React Suspense natively.
- **Recoil** (Meta, less actively maintained) has a similar model but heavier API.
- Atoms are created outside components — they're globally shared but lazily initialized.
- Perfect for: per-item state (e.g., each row in a table has its own atom).
- Not ideal for: complex async flows or large normalized datasets.

### Production FAQ
**Q: Jotai vs Zustand — which to pick?**  
A: Jotai = granular per-atom subscriptions, great for complex derived state. Zustand = simpler mental model for whole-store subscriptions.

**Q: Is Recoil production-ready?**  
A: It's used at Meta but the community has largely shifted to Jotai. New projects should prefer Jotai.

---

## 9. TanStack Query (React Query) — Caching, Mutations, Invalidation

**One-line definition:** A server-state library that fetches, caches, syncs, and updates async data — so you don't manage loading/error states manually.

### Real-World Dev Example
```jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch & cache
function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 60_000, // cache fresh for 60s
  });
  if (isLoading) return <Spinner />;
  return data.map(u => <div key={u.id}>{u.name}</div>);
}

// Mutate + invalidate
function AddUser() {
  const qc = useQueryClient();
  const mutation = useMutation({
    mutationFn: (user) => fetch('/api/users', { method:'POST', body: JSON.stringify(user) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] }), // refetch list
  });
}
```

### Gotchas & Dev Context
- **`staleTime`** = how long data is "fresh" (no refetch). Default is 0 (always stale).
- **`gcTime`** (formerly `cacheTime`) = how long unused cache is kept in memory.
- Invalidation triggers a background refetch — the UI shows stale data until fresh data arrives.
- Window focus refetch is enabled by default — disable with `refetchOnWindowFocus: false` if too aggressive.
- Don't store server data in Zustand/Redux when React Query already caches it.

### Production FAQ
**Q: What's the difference between `invalidateQueries` and `refetchQueries`?**  
A: `invalidateQueries` marks data stale and refetches if a component is observing it. `refetchQueries` forces a refetch unconditionally.

**Q: How do I handle optimistic updates?**  
A: Use `onMutate` to update the cache immediately, then roll back in `onError` if the request fails.

---

## 10. SWR

**One-line definition:** Vercel's lightweight data-fetching hook — "stale-while-revalidate" means show cached data instantly, then update in background.

### Real-World Dev Example
```jsx
import useSWR from 'swr';

const fetcher = (url) => fetch(url).then(r => r.json());

function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher);

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error!</p>;
  return <p>Hello, {data.name}</p>;
}
```

### Gotchas & Dev Context
- SWR = **S**tale-**W**hile-**R**evalidate: serve cached data instantly, revalidate in background, update UI when fresh data arrives.
- Much simpler API than TanStack Query — good for apps with straightforward fetching needs.
- Less powerful: fewer options for mutation handling, optimistic updates, and query invalidation vs TanStack Query.
- Built-in deduplication: multiple components calling `useSWR('/api/user')` share one request.
- Default: auto-refetch on window focus, network reconnect.

### Production FAQ
**Q: SWR vs TanStack Query — which to use?**  
A: SWR for simpler apps or Next.js projects (same team, great integration). TanStack Query for complex caching, pagination, infinite scroll, and mutations.

**Q: Does SWR support mutations?**  
A: Yes via `useSWRMutation`, but it's less ergonomic than TanStack Query's `useMutation`.

---

## 11. Data Fetching Patterns (SSR, SSG, CSR, ISR)

**One-line definition:** Four strategies for *when* and *where* HTML + data is generated — each with different performance and freshness trade-offs.

### ASCII Diagram
```
CSR  → Browser fetches data at runtime           (slowest first load, freshest)
SSR  → Server fetches + renders on every request (fresh, slower TTFB)
SSG  → Pre-rendered at build time, served as HTML (fastest, stale until rebuild)
ISR  → SSG + background regeneration after N secs (balance of speed + freshness)
```

### Real-World Dev Example (Next.js App Router)
```jsx
// SSG — built once
export const revalidate = false;

// ISR — rebuild every 60 seconds
export const revalidate = 60;

// SSR — fetch on every request
export const dynamic = 'force-dynamic';

async function Page() {
  const data = await fetch('https://api.example.com/posts').then(r => r.json());
  return <PostList posts={data} />;
}
```

### Gotchas & Dev Context
- SSG is best for content that rarely changes (docs, blogs, marketing pages).
- SSR adds server load — every visit = one server render.
- ISR is Next.js-specific and is the sweet spot for most content sites.
- CSR is fine for dashboards behind login where SEO doesn't matter.

### Production FAQ
**Q: Which pattern should a news site use?**  
A: ISR — generate articles at build, revalidate every few minutes for updates.

**Q: Can I mix patterns in one Next.js app?**  
A: Yes — each page/route can independently declare its own revalidation strategy.

---

## 12. React Server Components (RSC)

**One-line definition:** React components that run *only on the server* — they fetch data, render HTML, and send it to the client with zero JS bundle cost.

### Real-World Dev Example
```jsx
// app/users/page.jsx — Server Component (no 'use client')
async function UsersPage() {
  const users = await db.query('SELECT * FROM users'); // direct DB access!
  return (
    <ul>
      {users.map(u => <li key={u.id}>{u.name}</li>)}
    </ul>
  );
}
```

### ASCII Diagram
```
Server                          Client
──────                          ──────
RSC renders → serializes → sends HTML/RSC payload → hydrates Client Components
                                        (RSC code never ships to browser)
```

### Gotchas & Dev Context
- RSC can't use `useState`, `useEffect`, or browser APIs — they have no client lifecycle.
- Mark interactive parts with `'use client'` at the top of the file.
- RSC reduces JS bundle size significantly — ideal for data-heavy, read-only UI.
- RSC and Client Components can be **composed** — RSC wraps Client Components.
- Currently best supported in Next.js App Router.

### Production FAQ
**Q: Do RSC replace API routes?**  
A: For reads, often yes — RSC fetches directly from DB/service. For writes, use Server Actions or API routes.

**Q: Can a Server Component import a Client Component?**  
A: Yes. You can pass Server-fetched data as props to `'use client'` components.

---

## 13. Server Actions

**One-line definition:** Async functions that run on the server, callable directly from client components — replacing the need for manual API route wiring for mutations.

### Real-World Dev Example
```jsx
// actions.js
'use server';
export async function createPost(formData) {
  const title = formData.get('title');
  await db.insert({ title });
  revalidatePath('/posts');
}

// PostForm.jsx (Client Component)
'use client';
import { createPost } from './actions';

export function PostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Post title" />
      <button type="submit">Create</button>
    </form>
  );
}
```

### Gotchas & Dev Context
- `'use server'` marks a function — not a file (though files can be all-server).
- Server Actions work progressively — they work even without JS loaded (plain HTML form submit).
- Always validate/sanitize inputs — these run on your server with DB access.
- Use `revalidatePath()` or `revalidateTag()` to bust the cache after mutations.
- Available in Next.js 14+ App Router.

### Production FAQ
**Q: Are Server Actions secure?**  
A: They're exposed as POST endpoints internally — treat them like API routes: authenticate, authorize, validate inputs.

**Q: Can Server Actions replace REST APIs entirely?**  
A: For same-app mutations, yes. If third-party clients need to call your API, keep REST/GraphQL endpoints.

---

## 14. Streaming SSR

**One-line definition:** Send HTML to the browser in chunks as it's ready — the user sees content progressively instead of waiting for the entire page.

### ASCII Diagram
```
Traditional SSR:
Server ──── (wait for all data) ──── send full HTML ──── Browser renders

Streaming SSR:
Server ── shell HTML ──► Browser (shows layout instantly)
       ── chunk 1   ──► Browser (shows fast sections)
       ── chunk 2   ──► Browser (shows slow sections)
```

### Real-World Dev Example
```jsx
// Next.js App Router — Suspense enables streaming
import { Suspense } from 'react';

export default function Page() {
  return (
    <div>
      <Header />                          {/* renders immediately */}
      <Suspense fallback={<Spinner />}>
        <SlowDataComponent />             {/* streams in when ready */}
      </Suspense>
    </div>
  );
}
```

### Gotchas & Dev Context
- Streaming requires HTTP/1.1 chunked transfer or HTTP/2 — most modern hosts support it.
- Improves **Time to First Byte (TTFB)** and **Largest Contentful Paint (LCP)**.
- Not supported in all deployment targets — serverless functions may buffer responses.
- `<Suspense>` boundaries control *what* streams and *when*.

### Production FAQ
**Q: Does streaming SSR work on Vercel/Netlify?**  
A: Yes on Vercel with Next.js. Netlify supports it via Edge Functions. Avoid platforms that buffer the full response.

**Q: Can I stream multiple independent sections simultaneously?**  
A: Yes — wrap each slow section in its own `<Suspense>` boundary; they stream in parallel.

---

## 15. React Suspense for Data Fetching

**One-line definition:** A React mechanism that "pauses" a component's render until its async data is ready, showing a fallback in the meantime.

### Real-World Dev Example
```jsx
import { Suspense } from 'react';

function UserProfile({ userId }) {
  // Framework/library throws a Promise if data isn't ready yet
  const user = use(fetchUser(userId)); // React 19 `use()` hook
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<p>Loading profile...</p>}>
      <UserProfile userId={42} />
    </Suspense>
  );
}
```

### ASCII Diagram
```
React renders <UserProfile>
       │
  Data ready? ──No──► throw Promise ──► <Suspense> shows fallback
       │                                      │
      Yes                              Promise resolves
       │                                      │
  Render user data  ◄───────────────── React retries render
```

### Gotchas & Dev Context
- Suspense for data fetching requires framework/library support — TanStack Query, Relay, and Next.js wire this up for you.
- Don't start fetches *inside* a component during render — waterfall problem. Hoist fetches or use parallel routes.
- Error boundaries (`<ErrorBoundary>`) catch thrown errors from Suspense children.
- React 19's `use(promise)` hook is the official low-level API — replaces most custom Suspense wrappers.
- Works seamlessly with Streaming SSR — each `<Suspense>` boundary is a stream chunk boundary.

### Production FAQ
**Q: Does Suspense create a network waterfall?**  
A: It can — if a parent suspends before a child fetch starts. Fix: use `Promise.all`, parallel routes, or framework-level prefetching.

**Q: Can I use Suspense without a framework?**  
A: Yes, but you must handle the "throw a Promise" contract yourself or use a library like SWR/TanStack Query in Suspense mode.

---

*End of Batch 9 — React Ecosystem & State Management*
