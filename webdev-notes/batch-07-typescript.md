# Batch 7 — TypeScript
> Adding a safety net to JavaScript — without slowing you down.

TypeScript is JavaScript with types bolted on. It catches bugs at compile-time instead of runtime, makes your editor smarter, and scales gracefully as your codebase grows. Every valid `.js` file is also valid `.ts` — you adopt it at your own pace.

---

## 1. TypeScript Overview

**TypeScript is a statically-typed superset of JavaScript that compiles down to plain JS.**

### Real-World Dev Example
You're building a REST API. Without TypeScript, `user.adress` typos only blow up in production. With TypeScript, your editor underlines the mistake instantly.

```ts
// JS — silent bug
function greet(user) { return user.name.toUpperCase(); }

// TS — caught at compile time
function greet(user: { name: string }): string {
  return user.name.toUpperCase();
}
```

### ASCII Diagram
```
.ts file → [tsc / esbuild] → .js file → Node / Browser
              ↑
         Type checking
         (errors here,
          not in prod)
```

### Gotchas & Dev Context
- TypeScript **does not run** in browsers — it always compiles to JS first.
- Types are erased at runtime; they're purely a dev-time tool.
- `tsc` is the official compiler, but most projects use `esbuild` or `swc` for speed (they skip type-checking).
- Use `tsc --noEmit` in CI to type-check without producing output files.

### Production FAQ
**Q: Does TypeScript slow down my app?**
No. Types are stripped at build time. Your shipped JS is identical in size and speed.

**Q: Do I need 100% coverage on day one?**
No. Set `"strict": false` and add types incrementally. Use `// @ts-ignore` as a temporary escape hatch.

---

## 2. Type Annotations

**Explicit labels that tell TypeScript what kind of value a variable or function deals with.**

| Type      | Meaning                                      |
|-----------|----------------------------------------------|
| `string`  | Text                                         |
| `number`  | Integers and floats                          |
| `boolean` | `true` / `false`                             |
| `any`     | Opt-out of type checking (escape hatch)      |
| `unknown` | Like `any`, but forces you to narrow first   |
| `never`   | A value that can never exist                 |
| `void`    | Function returns nothing meaningful          |

### Real-World Dev Example
```ts
let username: string = "Ada";
let age: number = 30;
let isAdmin: boolean = false;

function logError(msg: string): void {
  console.error(msg);
}

function crash(msg: string): never {
  throw new Error(msg); // never returns
}

function parseInput(input: unknown): string {
  if (typeof input === "string") return input; // narrowed ✓
  return String(input);
}
```

### Gotchas & Dev Context
- **Avoid `any`** — it silently defeats type-checking. Prefer `unknown`.
- `never` is useful for exhaustive checks in `switch` statements.
- `void` ≠ `undefined`. A `void` return type means the caller shouldn't use the return value.
- TypeScript infers types automatically; you don't need to annotate everything.

### Production FAQ
**Q: When is `unknown` better than `any`?**
Always, when handling external data (API responses, `JSON.parse`). `unknown` forces you to validate before using the value, preventing silent crashes.

**Q: What does a `never` type actually protect against?**
It ensures your `switch`/`if` chains are exhaustive. If you add a new union member but forget to handle it, TypeScript errors on the `never` branch.

---

## 3. Interfaces vs Types

**Both describe the shape of an object — the difference is in extensibility and flexibility.**

### Real-World Dev Example
```ts
// Interface — extendable, mergeable
interface User {
  id: number;
  name: string;
}
interface User { email: string } // declaration merging ✓

// Type alias — more flexible
type ID = string | number;          // unions ✓
type Point = { x: number; y: number };

// Extending
interface AdminUser extends User { role: string }
type AdminUser2 = User & { role: string };
```

### ASCII Diagram
```
interface          type alias
─────────────      ──────────────
✓ extend           ✓ unions
✓ merge            ✓ tuples
✓ implement        ✓ mapped types
✗ unions           ✓ computed keys
```

### Gotchas & Dev Context
- **Declaration merging** only works with `interface` — this is how libraries like Express add types to `Request`.
- Use `interface` for public API shapes; use `type` for unions, tuples, and utility compositions.
- They are interchangeable for simple object shapes — pick a convention and stick to it.
- Classes can `implement` an interface, not a type alias (though it works similarly).

### Production FAQ
**Q: Which should I default to?**
TypeScript's own style guide recommends `interface` for object shapes and `type` for everything else. Most teams agree on this split.

**Q: Can I mix them?**
Yes. `type AdminUser = User & { role: string }` extends an interface with a type alias — perfectly valid.

---

## 4. Union & Intersection Types

**Union (`|`) means "one of these"; Intersection (`&`) means "all of these combined."**

### Real-World Dev Example
```ts
// Union — input can be string or number
type ID = string | number;
function printId(id: ID) {
  if (typeof id === "string") console.log(id.toUpperCase());
  else console.log(id.toFixed(2));
}

// Intersection — merge two shapes
type WithTimestamps = { createdAt: Date; updatedAt: Date };
type Post = { title: string; body: string };
type FullPost = Post & WithTimestamps;

const post: FullPost = {
  title: "Hello",
  body: "World",
  createdAt: new Date(),
  updatedAt: new Date(),
};
```

### ASCII Diagram
```
Union A | B            Intersection A & B
┌───────────────┐      ┌─────────────────┐
│  A  │  B  │  │      │   A   ∩   B      │
│  ●  │  ●  │  │      │   must have ALL  │
└───────────────┘      └─────────────────┘
value is A OR B        value is A AND B
```

### Gotchas & Dev Context
- Intersecting two primitive types gives `never` — `string & number` is impossible.
- Union types require narrowing before you can use type-specific methods.
- Intersections are great for "mixin" patterns — add `WithAuth`, `WithPagination` etc. to base types.

### Production FAQ
**Q: When do I use a union vs an optional property?**
Union when the shape changes entirely (e.g., `Success | Error`). Optional (`?`) when the property simply may or may not be present on the same shape.

**Q: Can I union more than two types?**
Yes: `type Status = "idle" | "loading" | "success" | "error"` — string literal unions are extremely common in React state management.

---

## 5. Generics

**A placeholder type that gets filled in when you actually use a function or class — think reusable templates.**

### Real-World Dev Example
```ts
// Without generics — loses type info
function identity(value: any): any { return value; }

// With generics — type-safe and reusable
function identity<T>(value: T): T { return value; }

const str = identity("hello");  // T = string
const num = identity(42);       // T = number

// Real use case: typed API fetcher
async function fetchData<T>(url: string): Promise<T> {
  const res = await fetch(url);
  return res.json() as T;
}

const user = await fetchData<{ name: string }>("/api/user");
console.log(user.name); // ✓ autocomplete works
```

### ASCII Diagram
```
function box<T>(val: T): T
                ↑
         Fill T at call site:
         box<string>("hi")  → T = string
         box<number>(42)    → T = number
```

### Gotchas & Dev Context
- TypeScript can often **infer** `T` — you don't always need to write `<string>` explicitly.
- Use `extends` to constrain generics: `<T extends object>` prevents primitives.
- Generic components in React require `<T,>` (trailing comma) in `.tsx` files to avoid JSX parsing conflicts.

### Production FAQ
**Q: When do I actually need generics vs just using `any`?**
Use generics when the input type and output type are linked. `any` breaks that link; generics preserve it.

**Q: How do I constrain a generic to only objects with a specific key?**
`<T extends { id: number }>` — T must have at least an `id: number` property.

---

## 6. Enums

**A named set of related constants — avoids magic strings and numbers scattered through your code.**

### Real-World Dev Example
```ts
// Numeric enum (auto-increments from 0)
enum Direction { Up, Down, Left, Right }
console.log(Direction.Up); // 0

// String enum (preferred — readable in logs/DBs)
enum Role {
  Admin = "ADMIN",
  Editor = "EDITOR",
  Viewer = "VIEWER",
}

function checkAccess(role: Role) {
  if (role === Role.Admin) grantFullAccess();
}
checkAccess(Role.Admin); // ✓
checkAccess("ADMIN");    // ✗ Type error
```

### Gotchas & Dev Context
- **Prefer string enums** — numeric enum values are meaningless in logs and API payloads.
- Enums are one of TypeScript's few features that emit runtime JS code (an IIFE object).
- Many teams replace enums with `const` objects + `as const` for zero runtime overhead:
```ts
const Role = { Admin: "ADMIN", Editor: "EDITOR" } as const;
type Role = typeof Role[keyof typeof Role]; // "ADMIN" | "EDITOR"
```
- Enums **can't** be used as index types directly.

### Production FAQ
**Q: Should I use `enum` or `as const` objects?**
`as const` objects are increasingly preferred — they're tree-shakeable, have no runtime overhead, and work better with Zod/Valibot schemas.

**Q: Can enum values be computed?**
String enum members must be literal strings. Numeric enums can use simple computed values, but this gets messy fast — avoid it.

---

## 7. Type Guards / Narrowing

**Code patterns that help TypeScript figure out which specific type is active inside a union.**

### Real-World Dev Example
```ts
type Cat = { meow(): void };
type Dog = { bark(): void };
type Pet = Cat | Dog;

// typeof guard
function handle(input: string | number) {
  if (typeof input === "string") input.toUpperCase(); // string here
}

// instanceof guard
function formatDate(d: Date | string) {
  if (d instanceof Date) return d.toISOString();
  return d;
}

// Custom type guard (type predicate)
function isCat(pet: Pet): pet is Cat {
  return "meow" in pet;
}

function makeSounds(pet: Pet) {
  if (isCat(pet)) pet.meow(); // ✓ narrowed to Cat
  else pet.bark();             // ✓ narrowed to Dog
}
```

### Gotchas & Dev Context
- `typeof` only works reliably for primitives. Use `instanceof` for class instances.
- The `in` operator is great for discriminating between object shapes.
- Type predicates (`pet is Cat`) tell TypeScript what the type is when the function returns `true`.
- Narrowing works in `if`, `switch`, ternary, and after null checks (`??`, `?.`).

### Production FAQ
**Q: Why does TypeScript still show an error after I checked `if (user !== null)`?**
Likely a reassignment inside an async callback. TypeScript can't track mutations across closures. Store in a `const` first.

**Q: What's the difference between a type guard and an assertion?**
A type guard is conditional and safe. An assertion (`as Cat`) is a forceful override with no runtime check — use assertions only when you're certain.

---

## 8. Utility Types

**Built-in generic types that transform existing types — no need to rewrite shapes from scratch.**

### Real-World Dev Example
```ts
interface User { id: number; name: string; email: string; age: number }

type PartialUser   = Partial<User>;        // all fields optional
type RequiredUser  = Required<PartialUser>; // all fields required
type UserPreview   = Pick<User, "id" | "name">;   // only id & name
type WithoutAge    = Omit<User, "age">;            // everything except age
type UserMap       = Record<string, User>;          // { [key: string]: User }
type FrozenUser    = Readonly<User>;                // no mutations allowed

// Real use — PATCH endpoint body
async function updateUser(id: number, data: Partial<User>) { /* ... */ }
```

### ASCII Diagram
```
User { id, name, email, age }
 ├─ Partial<User>     → { id?, name?, email?, age? }
 ├─ Pick<User,"id">   → { id }
 ├─ Omit<User,"age">  → { id, name, email }
 └─ Readonly<User>    → { readonly id, name, ... }
```

### Gotchas & Dev Context
- `Partial` is only one level deep — nested objects remain required.
- `Record<K, V>` is cleaner than `{ [key: string]: V }` — prefer it.
- `Readonly` doesn't deep-freeze at runtime; it only prevents reassignment at the type level.
- Combine utilities: `Readonly<Pick<User, "id" | "name">>` is perfectly valid.

### Production FAQ
**Q: How do I make a deeply partial type?**
Use a recursive type: `type DeepPartial<T> = { [K in keyof T]?: DeepPartial<T[K]> }`.

**Q: Is `Required` the opposite of `Partial`?**
Yes — `Required<T>` removes all `?` modifiers from every property, making them all mandatory.

---

## 9. Mapped Types

**Programmatically transform every key of a type using `in keyof` — like `.map()` but for types.**

### Real-World Dev Example
```ts
type Flags<T> = {
  [K in keyof T]: boolean;
};

interface Features { darkMode: string; betaAccess: string }
type FeatureFlags = Flags<Features>;
// → { darkMode: boolean; betaAccess: boolean }

// Add readonly + optional modifiers
type ReadonlyPartial<T> = {
  readonly [K in keyof T]?: T[K];
};

// Remove readonly with -readonly
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};
```

### ASCII Diagram
```
type Flags<T> = { [K in keyof T]: boolean }
                         ↑
              Loops over every key in T
              and assigns a new type (boolean)
```

### Gotchas & Dev Context
- Use `+` / `-` modifiers to add or remove `readonly` and `?` from mapped properties.
- `as` clause remaps keys: `[K in keyof T as \`get${Capitalize<string & K>}\`]` produces getter names.
- Mapped types are the backbone of all built-in utility types like `Partial`, `Readonly`, etc.
- Homomorphic mapped types (using `keyof T`) preserve optionality of the source type.

### Production FAQ
**Q: Can mapped types rename keys?**
Yes, with the `as` re-mapping clause in TypeScript 4.1+: `[K in keyof T as NewKey]: T[K]`.

**Q: Mapped type vs Record — which to use?**
`Record<K, V>` is a shorthand for uniform mappings. Use a mapped type when each key needs a different or derived value type.

---

## 10. Conditional Types

**Type-level `if/else` — resolve to different types based on a condition.**

### Real-World Dev Example
```ts
// Basic form: T extends U ? TrueType : FalseType
type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<string>; // "yes"
type B = IsString<number>; // "no"

// Unwrap a Promise
type Awaited<T> = T extends Promise<infer U> ? U : T;
type Data = Awaited<Promise<{ id: number }>>; // { id: number }

// Exclude from a union
type WithoutNull<T> = T extends null | undefined ? never : T;
type SafeString = WithoutNull<string | null>; // string
```

### ASCII Diagram
```
T extends Condition ?
    ┌──── TrueType   (T matches)
    └──── FalseType  (T doesn't match)

Distributes over unions automatically:
  IsString<string | number>
  → IsString<string> | IsString<number>
  → "yes" | "no"
```

### Gotchas & Dev Context
- Conditional types **distribute** over naked union types automatically — often what you want, occasionally surprising.
- Use `infer` to capture and name a type within the condition: `T extends Array<infer Item> ? Item : never`.
- TypeScript's built-in `Awaited`, `NonNullable`, `ReturnType`, `Parameters` are all conditional types.

### Production FAQ
**Q: What is `infer` doing exactly?**
It's a type variable that TypeScript fills in during the conditional check. Think of it as pattern matching — "if T looks like `Promise<X>`, call that X `U`."

**Q: When do conditional types get deferred?**
When `T` is still a generic (not yet resolved), TypeScript can't evaluate the condition yet and keeps it pending — this can cause unexpected `type is circular` errors in complex chains.

---

## 11. Template Literal Types

**String literal types composed using backtick syntax — build new string types programmatically.**

### Real-World Dev Example
```ts
type EventName = "click" | "focus" | "blur";
type Handler = `on${Capitalize<EventName>}`;
// → "onClick" | "onFocus" | "onBlur"

type CSSUnit = "px" | "rem" | "em" | "%";
type CSSValue = `${number}${CSSUnit}`;
// → "16px" | "1.5rem" | ... (wide but usable)

// Typed event emitter keys
type Route = "/users" | "/posts";
type Method = "GET" | "POST";
type Endpoint = `${Method} ${Route}`;
// → "GET /users" | "GET /posts" | "POST /users" | "POST /posts"
```

### Gotchas & Dev Context
- Combining large unions explodes combinatorially — `5 methods × 20 routes = 100 types`. Keep unions small.
- Works with `Uppercase<T>`, `Lowercase<T>`, `Capitalize<T>`, `Uncapitalize<T>` intrinsic helpers.
- Extremely useful for generating typed object keys (e.g., `get${FieldName}`, `on${EventName}`).
- Template literal types are purely compile-time — no regex or parsing happens at runtime.

### Production FAQ
**Q: Can I use template literal types with `keyof`?**
Yes — `[K in keyof T as \`data-${string & K}\`]` produces `data-*` attribute keys from an object's keys.

**Q: Are these the same as JavaScript template literals?**
Same syntax, different purpose. JS template literals produce runtime strings. TS template literal types produce compile-time type constraints.

---

## 12. Declaration Files (.d.ts)

**Type-only files that describe the shape of existing JS code — no runtime output, pure type information.**

### Real-World Dev Example
```ts
// math.js (plain JS, no types)
export function add(a, b) { return a + b; }

// math.d.ts (declaration file)
export declare function add(a: number, b: number): number;

// Consumer gets full type safety without touching the JS
import { add } from "./math";
add(1, 2);        // ✓
add("a", "b");    // ✗ Type error
```

### ASCII Diagram
```
your-library/
 ├── dist/
 │    ├── index.js      ← runtime code
 │    └── index.d.ts    ← type declarations
 └── package.json
          "types": "dist/index.d.ts"
```

### Gotchas & Dev Context
- When you install `@types/lodash`, you're installing `.d.ts` files — Lodash itself is plain JS.
- Running `tsc --declaration` auto-generates `.d.ts` files from your TypeScript source.
- `declare module "some-lib" { }` in a `.d.ts` file lets you add types to untyped packages.
- Never import from `.d.ts` files in runtime code — they don't exist after compilation.

### Production FAQ
**Q: When do I need to write `.d.ts` files manually?**
When consuming a third-party JS library that has no `@types/*` package and no bundled types. Also when publishing your own library.

**Q: What's the difference between `declare const` and `const`?**
`declare const` tells TypeScript "this exists in the environment, trust me" — no JS is emitted. Plain `const` emits actual JS.

---

## 13. tsconfig.json (strict, paths, baseUrl)

**The project configuration file that controls how TypeScript compiles and type-checks your code.**

### Real-World Dev Example
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@utils/*": ["src/utils/*"],
      "@components/*": ["src/components/*"]
    },
    "outDir": "dist",
    "noEmit": false,
    "skipLibCheck": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### Key Options Explained
| Option       | What it does                                                  |
|--------------|---------------------------------------------------------------|
| `strict`     | Enables all strict checks (null checks, implicit any, etc.)  |
| `baseUrl`    | Root for non-relative imports                                 |
| `paths`      | Alias mappings — `@utils/format` → `src/utils/format`        |
| `noEmit`     | Type-check only, don't produce JS                            |
| `skipLibCheck` | Skip checking `.d.ts` files in `node_modules` (faster)     |

### Gotchas & Dev Context
- `paths` in `tsconfig.json` is type-only — your bundler (Vite, webpack) needs its own alias config to resolve them at runtime.
- `"strict": true` is shorthand for ~8 individual flags. Enable it from day one.
- `target` affects what JS syntax is emitted; `lib` affects what browser APIs TypeScript knows about.

### Production FAQ
**Q: Why does my `@utils` import work in TS but fail at runtime?**
Because `paths` is only for the TypeScript compiler. Configure the same aliases in `vite.config.ts` or `webpack.config.js`.

**Q: Can I extend a base tsconfig?**
Yes: `"extends": "@tsconfig/node22/tsconfig.json"` — the `@tsconfig/*` npm packages provide well-maintained base configs.

---

## 14. Type Inference

**TypeScript automatically figures out types from context — you don't have to annotate everything.**

### Real-World Dev Example
```ts
// All inferred — no annotations needed
const name = "Ada";              // string
const count = 42;                // number
const active = true;             // boolean
const nums = [1, 2, 3];          // number[]

function add(a: number, b: number) {
  return a + b; // return type inferred as number
}

// Object inference
const config = { host: "localhost", port: 3000 };
// { host: string; port: number }

// Best common type — inferred from array members
const mixed = [1, "two", true]; // (string | number | boolean)[]
```

### ASCII Diagram
```
const x = "hello"
          ↑
     TypeScript sees a string literal
     → infers type as string
     → x: string (widened) or "hello" (literal, with as const)
```

### Gotchas & Dev Context
- Inference **widens** by default: `"hello"` becomes `string`, not `"hello"`. Use `as const` for literal types.
- Functions with complex return types benefit from explicit annotations for readability, even if inference works.
- `typeof` in type position captures the inferred type of a value: `type Config = typeof config`.
- Inference doesn't work well across async boundaries without explicit return types.

### Production FAQ
**Q: Should I annotate everything even if TypeScript can infer it?**
No — over-annotating is noise. Annotate function parameters, public API boundaries, and complex return types. Let inference do the rest.

**Q: What is `as const` and when do I need it?**
`as const` freezes a value's type to its literal form: `{ role: "admin" as const }` gives `role: "admin"` instead of `role: string`. Essential for discriminated unions and enums-as-objects patterns.

---

## 15. Discriminated Unions

**A union of types that each share a common literal field (the "discriminant") — makes exhaustive handling safe and clean.**

### Real-World Dev Example
```ts
type Success = { status: "success"; data: string };
type Loading = { status: "loading" };
type Failure = { status: "error"; message: string };

type State = Success | Loading | Failure;

function render(state: State) {
  switch (state.status) {
    case "success": return state.data;       // ✓ data available
    case "loading": return "Loading...";
    case "error":   return state.message;   // ✓ message available
    default:
      const _exhaustive: never = state;     // compile error if case missed
      return _exhaustive;
  }
}
```

### ASCII Diagram
```
State = Success | Loading | Failure
          ↑         ↑        ↑
       status:   status:  status:
      "success" "loading" "error"
          ↑
     Discriminant field — same key, different literal values
```

### Gotchas & Dev Context
- The discriminant field must be a **literal type** (`"success"`, not `string`).
- The `never` trick in the `default` branch gives compile-time exhaustiveness checking.
- This pattern is the TypeScript-idiomatic way to model state machines (loading/error/success).
- Works beautifully with React's `useReducer` — each action type becomes a union member.

### Production FAQ
**Q: What makes it "discriminated"?**
TypeScript uses the shared literal key to narrow the union. Once it sees `state.status === "success"`, it knows the full shape of that branch without you asserting anything.

**Q: Can I use a field other than `status` as the discriminant?**
Yes — any literal property works: `type`, `kind`, `tag`, `__typename`. Pick one convention and stick to it.

---

## 16. Zod / Valibot (Runtime Validation)

**Libraries that validate data at runtime AND generate TypeScript types — your single source of truth for data shapes.**

### Real-World Dev Example
```ts
// Zod
import { z } from "zod";

const UserSchema = z.object({
  id: z.number(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(["admin", "editor", "viewer"]),
});

type User = z.infer<typeof UserSchema>; // Type derived from schema!

// Validate API response
const raw = await fetch("/api/user").then(r => r.json());
const user = UserSchema.parse(raw); // throws if invalid
// or safe version:
const result = UserSchema.safeParse(raw);
if (result.success) console.log(result.data.name);
else console.error(result.error.issues);
```

```ts
// Valibot — same idea, tree-shakeable & lighter
import * as v from "valibot";

const UserSchema = v.object({
  id: v.number(),
  name: v.string(),
});
type User = v.InferOutput<typeof UserSchema>;
```

### ASCII Diagram
```
Zod Schema ──→ Runtime validation (throws on bad data)
     └──────→ TypeScript type (via z.infer<>)
     
One definition → two guarantees
```

### Gotchas & Dev Context
- TypeScript types **cannot** validate at runtime — they're erased. Zod/Valibot fill this gap.
- Zod is heavier (~13 kB gzipped); Valibot is designed for tree-shaking (much smaller bundles).
- Use at API boundaries, form inputs, and environment variable parsing (`zod` + `dotenv`).
- `safeParse` is production-preferred — it never throws, returns `{ success, data | error }`.

### Production FAQ
**Q: Do I need Zod if I already have TypeScript types?**
Yes, if you're consuming external data. TypeScript types don't exist at runtime — Zod ensures the actual data matches what your types expect.

**Q: Should I use Zod or Valibot?**
Zod has a larger ecosystem (React Hook Form, tRPC, drizzle). Valibot is the better choice for bundle-sensitive apps (edge functions, small client bundles). Both are excellent.

---

*End of Batch 7 — TypeScript*
