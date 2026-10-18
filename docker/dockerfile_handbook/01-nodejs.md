# 01 — Node.js / JavaScript / TypeScript (Examples 6–17)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Fundamentals](00-fundamentals.md)

---

## 🧾 What is Node.js? (for non-developers)

- **JavaScript** started as the language that runs inside web browsers.
- **Node.js** lets JavaScript run on a **server** (outside the browser). It's used for
  web APIs, websites, real-time chat, and tooling.
- **TypeScript** is JavaScript with "types" added. Browsers/Node can't run it directly —
  it must be **compiled** (`tsc`) into plain JavaScript first. → needs a build step.
- **npm** is Node's package manager (downloads dependencies). Alternatives: **yarn**, **pnpm**.
- Dependencies live in a folder called **`node_modules/`** (often 200 MB–1 GB!).

### Files you'll see in a Node project

| File | Meaning |
|------|---------|
| `package.json` | Project name, dependency list, and **scripts** like `"start": "node server.js"` and `"build": "tsc"` |
| `package-lock.json` | Exact versions of every dependency (npm). `yarn.lock` for yarn, `pnpm-lock.yaml` for pnpm |
| `server.js` / `index.js` / `src/` | The source code |
| `tsconfig.json` | TypeScript compiler settings (means there's a build step) |
| `dist/` or `build/` | Compiled output (generated — don't commit, don't copy) |

### Node-specific concepts you need for Dockerfiles

| Concept | Explanation |
|---------|-------------|
| `npm install` vs `npm ci` | `install` may **update** the lock file. `ci` ("clean install") installs **exactly** what's in the lock file and fails if they disagree. **Always use `npm ci` in Docker.** |
| `dependencies` vs `devDependencies` | `devDependencies` are only needed for building/testing (TypeScript compiler, test tools). Production doesn't need them → `npm ci --omit=dev`. |
| `NODE_ENV=production` | Tells many libraries (Express, React) to turn off debug features → faster & safer. |
| The `node` user | Official Node images already contain a non-root user called `node` (UID 1000). Just use `USER node`. |

> ⚠️ **Node gotcha (PID 1):** Node.js doesn't handle being PID 1 well in some cases
> (zombie child processes, signal handling). Either run with `docker run --init`, or add
> `tini`/`dumb-init` in the image. Also, **avoid `CMD ["npm", "start"]`** — npm doesn't
> forward `SIGTERM` to your app reliably. Use `CMD ["node", "server.js"]` directly.

### Starter `.dockerignore` for Node

```gitignore
node_modules
npm-debug.log*
dist
build
.next
coverage
.git
.env*
Dockerfile*
.dockerignore
```

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 6 | [Simple Express API](#example-6--simple-express-api) | The baseline Node Dockerfile |
| 7 | [Express with tini + healthcheck](#example-7--express-with-tini-and-healthcheck) | Proper PID 1 and health |
| 8 | [TypeScript API, multi-stage](#example-8--typescript-api-multi-stage) | Build stage + prod-only deps |
| 9 | [BuildKit npm cache mount](#example-9--buildkit-npm-cache-mount) | Faster rebuilds |
| 10 | [pnpm project](#example-10--pnpm-project) | corepack + pnpm |
| 11 | [Yarn (Berry) project](#example-11--yarn-berry-project) | yarn v4 |
| 12 | [Next.js standalone](#example-12--nextjs-standalone) | Full-stack React framework |
| 13 | [NestJS API](#example-13--nestjs-api) | Enterprise Node framework |
| 14 | [Distroless Node](#example-14--distroless-node) | No shell in production |
| 15 | [Monorepo (npm workspaces)](#example-15--monorepo-npm-workspaces) | Build one app from many |
| 16 | [Bun runtime](#example-16--bun-runtime) | Alternative JS runtime |
| 17 | [Dev container with hot reload](#example-17--development-container-with-hot-reload) | Local development |

---

## Example 6 — Simple Express API

**🧾 What is this?** **Express** is the most popular Node.js web framework — a tiny
web server that answers HTTP requests. Plain JavaScript, no build step.

**📁 Developer gives you:** `package.json`, `package-lock.json`, `server.js`

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine

# Tell libraries we're in production mode
ENV NODE_ENV=production

WORKDIR /app

# 1) Copy only the dependency files first (cache-friendly)
COPY package.json package-lock.json ./

# 2) Install exact versions, skip dev-only packages
RUN npm ci --omit=dev && npm cache clean --force

# 3) Copy the source code, owned by the non-root "node" user
COPY --chown=node:node . .

# 4) Drop root privileges
USER node

EXPOSE 3000
CMD ["node", "server.js"]
```

**🔍 Explained:**

- `node:22-alpine` — Node.js 22 (an LTS = Long-Term Support release) on Alpine Linux (~50 MB base).
- `COPY package.json package-lock.json ./` — the `./` means "into the current WORKDIR".
- `npm ci --omit=dev` — exact install from the lock file, production packages only.
- `npm cache clean --force` — removes npm's download cache (same RUN = actually saves space).
- `--chown=node:node` — the official image ships a user named `node`; files become theirs.

**⚠️ DevOps Gotchas:**

- If `package-lock.json` is missing, `npm ci` fails. That's **good** — ask the dev to commit it.
- Use **even-numbered** Node versions (20, 22, 24) in production — those are LTS. Odd ones
  (21, 23) are short-lived.
- The app must read its port from an env var like `process.env.PORT` and listen on `0.0.0.0`.

**▶️ Build & run:**

```bash
docker build -t express-api:1.0.0 .
docker run -d -p 3000:3000 express-api:1.0.0
```

---

## Example 7 — Express with tini and healthcheck

**🧾 What is this?** Same app, now with a proper "init" process and a health check.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine

# tini: a tiny init process that forwards signals and reaps zombie processes
RUN apk add --no-cache tini

ENV NODE_ENV=production \
    PORT=3000

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --chown=node:node . .

USER node
EXPOSE 3000

# wget is built into Alpine (busybox), so no extra install needed
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1

# tini becomes PID 1 and starts node as its child
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
```

**🔍 Explained:**

- `apk add --no-cache tini` — `apk` is Alpine's package manager. `--no-cache` = don't
  store the package index (no cleanup needed — Alpine's equivalent of the apt cleanup).
- `ENTRYPOINT ["/sbin/tini", "--"]` — tini runs first. The `--` means "everything after
  this is the command to run". Combined with `CMD`, the container runs
  `/sbin/tini -- node server.js`.
- `wget -qO-` — quietly fetch the URL and print it; non-zero exit code if it fails.

**⚠️ DevOps Gotchas:**

- Alternative to installing tini: run with `docker run --init` (Docker injects tini). But
  Kubernetes has no `--init`, so baking tini in the image is more portable.
- Don't make `/health` check the database — if the DB blips, Docker marks **every** app
  container unhealthy at once. Health = "is *this process* OK?"

---

## Example 8 — TypeScript API, multi-stage

**🧾 What is this?** TypeScript must be compiled to JavaScript. The compiler lives in
`devDependencies`. We need it to **build**, but not to **run**.

**📁 Developer gives you:** `package.json` (with `"build": "tsc"`), `package-lock.json`,
`tsconfig.json`, `src/`. Output goes to `dist/`.

```dockerfile
# syntax=docker/dockerfile:1
ARG NODE_VERSION=22

############ Stage 1: install ALL deps and compile ############
FROM node:${NODE_VERSION}-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
# Full install — includes TypeScript and other devDependencies
RUN npm ci

COPY tsconfig.json ./
COPY src ./src
RUN npm run build

############ Stage 2: install ONLY production deps ############
FROM node:${NODE_VERSION}-alpine AS deps
WORKDIR /app
ENV NODE_ENV=production
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

############ Stage 3: final runtime image ############
FROM node:${NODE_VERSION}-alpine AS runtime
RUN apk add --no-cache tini
ENV NODE_ENV=production
WORKDIR /app

COPY --from=deps  --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist         ./dist
COPY --chown=node:node package.json ./

USER node
EXPOSE 3000
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/index.js"]
```

**🔍 Explained:**

- `ARG NODE_VERSION=22` **before** the first `FROM` — a global build variable usable in
  every `FROM` line. Change the version in one place (or with `--build-arg NODE_VERSION=24`).
- **Three stages:**
  1. `build` — full deps + compile `src/` → `dist/`.
  2. `deps` — a clean install of production-only packages.
  3. `runtime` — copies `node_modules` from `deps` and `dist` from `build`. No TypeScript,
     no source `.ts` files, no test tools.
- `COPY src ./src` — copying only what the build needs (not tests, docs) = fewer cache busts.

**⚠️ DevOps Gotchas:**

- Stages `build` and `deps` don't depend on each other, so **BuildKit runs them in
  parallel** — free speed.
- Check the `main`/`start` field in `package.json` to find the real entry file (`dist/index.js`,
  `dist/main.js`, `dist/server.js`…). Wrong path = container exits instantly with
  `Cannot find module`.

---

## Example 9 — BuildKit npm cache mount

**🧾 What is this?** A BuildKit feature that keeps npm's download cache **on the build
machine between builds**, but never puts it in the image. When `package-lock.json`
changes, only new/changed packages are downloaded.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
# The cache mount persists /root/.npm across builds (outside the image)
RUN --mount=type=cache,target=/root/.npm \
    npm ci

COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --omit=dev
COPY --from=build --chown=node:node /app/dist ./dist
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**🔍 Explained:**

- `RUN --mount=type=cache,target=/root/.npm` — mounts a persistent cache folder only for
  this command. `/root/.npm` is where npm stores downloads when running as root.
- No `npm cache clean` needed — the cache never lands in a layer.
- Requires the `# syntax=docker/dockerfile:1` line and BuildKit (default in modern Docker).

**⚠️ DevOps Gotchas:**

- On **ephemeral CI agents** (fresh VM every run), the cache mount starts empty each time.
  Use `docker buildx build --cache-to type=registry,... --cache-from type=registry,...`
  or the GitHub Actions cache backend (`type=gha`) to persist layer cache between runs.

---

## Example 10 — pnpm project

**🧾 What is this?** **pnpm** is a faster, disk-efficient alternative to npm. Lock file:
`pnpm-lock.yaml`. Node ships a tool called **corepack** that installs the right pnpm/yarn
version automatically.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim AS base
# Where pnpm stores its global store; also add it to PATH
ENV PNPM_HOME="/pnpm" \
    PATH="/pnpm:$PATH"
RUN corepack enable
WORKDIR /app

FROM base AS build
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile
COPY . .
RUN pnpm run build

FROM base AS prod-deps
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --prod --frozen-lockfile

FROM base AS runtime
ENV NODE_ENV=production
COPY --from=prod-deps --chown=node:node /app/node_modules ./node_modules
COPY --from=build     --chown=node:node /app/dist         ./dist
COPY --chown=node:node package.json ./
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**🔍 Explained:**

- `FROM base AS build` — a stage built **on top of another stage**. Shared setup
  (corepack, env vars) is written once in `base`.
- `corepack enable` — reads the `"packageManager": "pnpm@9.x.x"` field in `package.json`
  and provides that exact pnpm version.
- `--frozen-lockfile` — pnpm's equivalent of `npm ci`: fail if the lock file is out of date.
- `--prod` — production dependencies only.

**⚠️ DevOps Gotchas:**

- If `package.json` has no `packageManager` field, corepack may prompt or pick a default.
  Ask devs to set it so local and CI versions match.
- Mixing lock files (both `package-lock.json` and `pnpm-lock.yaml`) = confusion. One
  project, one package manager.

---

## Example 11 — Yarn (Berry) project

**🧾 What is this?** **Yarn** is another npm alternative. Modern Yarn (v2+, "Berry")
keeps config in `.yarnrc.yml` and a `.yarn/` folder.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
RUN corepack enable
WORKDIR /app

# Yarn Berry needs its config + release files alongside the lockfile
COPY package.json yarn.lock .yarnrc.yml ./
COPY .yarn ./.yarn
RUN yarn install --immutable

COPY . .
RUN yarn build \
 && yarn workspaces focus --all --production

FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist         ./dist
COPY --chown=node:node package.json ./
USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**🔍 Explained:**

- `--immutable` — Yarn Berry's "don't modify the lock file" flag (like `npm ci`).
- `yarn workspaces focus --all --production` — after building, prunes `node_modules`
  down to production packages (requires the workspace-tools plugin on Yarn 3; built in on Yarn 4).
- **Yarn Classic (v1)** uses a different flag: `yarn install --frozen-lockfile --production`.
  Check `yarn --version` / the `packageManager` field to know which one you have.

**⚠️ DevOps Gotchas:**

- If the project uses **Plug'n'Play** (no `node_modules`, a `.pnp.cjs` file instead), you
  must copy `.pnp.cjs`, `.pnp.loader.mjs` and `.yarn/cache` — the layout is different.
  Ask the team which mode they use (`nodeLinker` in `.yarnrc.yml`).

---

## Example 12 — Next.js standalone

**🧾 What is this?** **Next.js** is a framework for building React websites that render
on the server. It's both a **frontend** (pages) and a **backend** (API routes). It has a
"standalone" output mode that bundles *only* the files needed to run → tiny images.

**📁 Developer must set** in `next.config.js`: `output: 'standalone'`.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS base
WORKDIR /app

########## deps ##########
FROM base AS deps
# libc6-compat: helps some native packages that expect glibc on Alpine
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json ./
RUN npm ci

########## build ##########
FROM base AS build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# Disable anonymous telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

########## runtime ##########
FROM base AS runtime
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
 && adduser  --system --uid 1001 --ingroup nodejs nextjs

# Static assets and the standalone server
COPY --from=build --chown=nextjs:nodejs /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
# server.js is generated by Next.js in standalone mode
CMD ["node", "server.js"]
```

**🔍 Explained:**

- `.next/standalone` contains a minimal `server.js` plus only the `node_modules` actually
  used. Typical result: **~150 MB** instead of **~1 GB**.
- `public/` and `.next/static/` are **not** included in standalone automatically — that's
  why we copy them separately (forgetting this = website with no images/CSS).
- `HOSTNAME=0.0.0.0` — Next's server reads this to bind on all interfaces.
- `addgroup`/`adduser` — Alpine's (busybox) syntax for creating users (Debian uses `groupadd`/`useradd`).

**⚠️ DevOps Gotchas:**

- **`NEXT_PUBLIC_*` variables are baked in at BUILD time**, not runtime. If the frontend
  needs `NEXT_PUBLIC_API_URL`, it must be passed as a build arg — meaning **one image per
  environment**, or a runtime-config workaround. This surprises everyone once.
- If the project has no `public/` folder, the `COPY` fails. Remove that line in that case.

---

## Example 13 — NestJS API

**🧾 What is this?** **NestJS** is a structured, "enterprise-style" Node framework written
in TypeScript (similar in spirit to Java Spring). Builds to `dist/main.js`.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build \
 && npm prune --omit=dev

FROM node:22-alpine AS runtime
RUN apk add --no-cache tini
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/package.json  ./
COPY --from=build --chown=node:node /app/node_modules  ./node_modules
COPY --from=build --chown=node:node /app/dist          ./dist
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s \
  CMD wget -qO- http://127.0.0.1:3000/health || exit 1
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/main.js"]
```

**🔍 Explained:**

- `npm prune --omit=dev` — after building, **removes** dev dependencies from the existing
  `node_modules`. A simpler alternative to the separate `deps` stage in Example 8 (slightly
  less clean, but one fewer install).

**⚠️ DevOps Gotchas:**

- NestJS apps often use **Prisma** (a database tool) which generates code at build time and
  downloads a native "query engine" binary **for the build OS**. If build and runtime OS
  differ (Debian build, Alpine runtime), Prisma fails at startup. Keep both stages on the
  same base, and run `npx prisma generate` in the build stage.

---

## Example 14 — Distroless Node

**🧾 What is this?** **Distroless** images (by Google) contain only Node.js and the bare
minimum OS libraries — **no shell, no package manager**. Attackers who get in can't run
`sh`, `curl`, or install anything.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY . .

# Distroless Node 22, ":nonroot" variant runs as UID 65532 by default
FROM gcr.io/distroless/nodejs22-debian12:nonroot
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build --chown=65532:65532 /app /app
EXPOSE 3000
# The image's ENTRYPOINT is already "node", so CMD is just the script
CMD ["server.js"]
```

**🔍 Explained:**

- Build stage uses `node:22-slim` (Debian) because distroless is also Debian-based (glibc) —
  native modules compiled there will work.
- `:nonroot` tag — preconfigured to run as user `nonroot` (UID 65532).
- `CMD ["server.js"]` — the distroless Node image's `ENTRYPOINT` is `["/nodejs/bin/node"]`,
  so we only pass the filename.

**⚠️ DevOps Gotchas:**

- **No shell = no `docker exec -it ... sh`** for debugging. Use
  `kubectl debug` (ephemeral containers) or the `:debug` tag variant (has busybox) in non-prod.
- `HEALTHCHECK CMD wget ...` won't work (no wget). Rely on Kubernetes HTTP probes instead.
- Don't build on Alpine and run on distroless — musl vs glibc mismatch.

---

## Example 15 — Monorepo (npm workspaces)

**🧾 What is this?** A **monorepo** = one Git repository containing several apps and
shared libraries, e.g.:

```
repo/
├── package.json            ← root, declares "workspaces": ["apps/*", "packages/*"]
├── package-lock.json       ← ONE lock file for everything
├── apps/
│   ├── api/                ← the app we want to containerise
│   └── web/
└── packages/
    └── shared/             ← library used by api and web
```

```dockerfile
# syntax=docker/dockerfile:1
# Build from the REPO ROOT:  docker build -f apps/api/Dockerfile -t api .
FROM node:22-alpine AS build
WORKDIR /repo

# Copy all package.json files first, preserving folder structure, for caching
COPY package.json package-lock.json ./
COPY apps/api/package.json        apps/api/
COPY packages/shared/package.json packages/shared/
RUN npm ci --workspace=apps/api --include-workspace-root

# Now the actual source
COPY packages/shared packages/shared
COPY apps/api        apps/api
RUN npm run build --workspace=packages/shared \
 && npm run build --workspace=apps/api

# Produce a production-only node_modules for just this app
RUN npm ci --omit=dev --workspace=apps/api --include-workspace-root

FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /repo
COPY --from=build --chown=node:node /repo/node_modules            ./node_modules
COPY --from=build --chown=node:node /repo/packages/shared/dist    ./packages/shared/dist
COPY --from=build --chown=node:node /repo/packages/shared/package.json ./packages/shared/
COPY --from=build --chown=node:node /repo/apps/api/dist           ./apps/api/dist
COPY --from=build --chown=node:node /repo/apps/api/package.json   ./apps/api/
USER node
WORKDIR /repo/apps/api
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**🔍 Explained:**

- The **build context is the repo root** (the `.` at the end), but the Dockerfile lives
  in `apps/api/` — hence `-f apps/api/Dockerfile`. This lets the build see `packages/shared`.
- `--workspace=apps/api` — install only what this app (and the root) needs.
- npm workspaces link `packages/shared` into `node_modules` via a symlink; that's why we
  keep the same folder structure in the runtime stage.

**⚠️ DevOps Gotchas:**

- With the repo root as context, `.dockerignore` must live at the **repo root**. Without
  it, every app's `node_modules` gets uploaded — builds become painfully slow.
- For big monorepos, tools like **Turborepo** (`turbo prune api --docker`) generate a
  pruned subset of the repo specifically for Docker builds.

---

## Example 16 — Bun runtime

**🧾 What is this?** **Bun** is a newer, very fast JavaScript runtime + package manager
(alternative to Node.js). Lock file: `bun.lock` (older projects: `bun.lockb`).

```dockerfile
# syntax=docker/dockerfile:1
FROM oven/bun:1-alpine AS build
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

FROM oven/bun:1-alpine AS deps
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production

FROM oven/bun:1-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps  --chown=bun:bun /app/node_modules ./node_modules
COPY --from=build --chown=bun:bun /app/dist         ./dist
COPY --chown=bun:bun package.json ./
# The official Bun image ships a non-root user called "bun"
USER bun
EXPOSE 3000
CMD ["bun", "run", "dist/index.js"]
```

**🔍 Explained:** Same pattern as Node — just `bun install` instead of `npm ci`, and the
non-root user is called `bun`.

**⚠️ DevOps Gotchas:**

- Bun is not 100% compatible with every Node library. Confirm the team actually runs Bun
  in production, not just as a fast installer.

---

## Example 17 — Development container with hot reload

**🧾 What is this?** For **local development**, developers want to edit code on their
laptop and see changes instantly *inside* the container ("hot reload"). This is a
**different goal** from production — we include dev tools and mount source code.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS dev
WORKDIR /app
ENV NODE_ENV=development
COPY package.json package-lock.json ./
RUN npm ci
# Source code is NOT copied — it is mounted at runtime with a volume
USER node
EXPOSE 3000 9229
# "dev" script typically runs nodemon/tsx watch; 9229 = Node debugger port
CMD ["npm", "run", "dev"]
```

`docker-compose.yml` to go with it:

```yaml
services:
  api:
    build:
      context: .
      target: dev
    ports:
      - "3000:3000"
      - "9229:9229"
    volumes:
      - ./:/app                # live-mount laptop source into the container
      - /app/node_modules      # but keep the container's own node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true   # file-watching fix for Windows/WSL mounts
```

**🔍 Explained:**

- `volumes: ./:/app` — the laptop folder *is* `/app` in the container. Edits appear instantly.
- `/app/node_modules` (anonymous volume) — prevents the laptop's (possibly empty or
  Windows-built) `node_modules` from hiding the Linux one installed in the image.
- `npm run dev` is acceptable **here** (signals don't matter in dev).

**⚠️ DevOps Gotchas:**

- **Never deploy the dev target to production.** Use `target: dev` locally and the default
  (last) stage in CI.
- On Windows, file-change notifications don't cross into containers reliably — that's
  what `CHOKIDAR_USEPOLLING=true` works around (for watchers built on chokidar).

---

**Next:** [02 — Python ➡️](02-python.md)
