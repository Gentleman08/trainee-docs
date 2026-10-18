# 06 — Frontend & Static Sites (Examples 63–72)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: .NET, PHP, Ruby, Elixir](05-dotnet-php-ruby-elixir.md)

---

## 🧾 What is a "frontend"? (for non-developers)

- The **frontend** is what runs in the user's **browser**: HTML (structure), CSS (style),
  JavaScript (behaviour).
- Modern frontends are written with frameworks — **React**, **Vue**, **Angular**, **Svelte** —
  and then **built** (compiled, bundled, minified) by tools like **Vite** or **webpack**.
- After building you get a folder (`dist/` or `build/`) of **plain static files**.
  No Node.js needed to serve them — just a web server like **nginx** or **Caddy**.

```
 Source (React/Vue/Angular + node_modules, ~500 MB)
        │  npm run build   (needs Node.js)
        ▼
 dist/  (index.html + a few JS/CSS files, ~2 MB)
        │  copy into nginx image
        ▼
 Final image: nginx (~45 MB) + 2 MB of files
```

- **SPA (Single-Page Application)** — one `index.html`; JavaScript handles routes like
  `/products/42` **inside the browser**. The web server must return `index.html` for unknown
  paths, or refreshing `/products/42` gives a **404**. (The `try_files` line below fixes it.)
- **SSG (Static Site Generator)** — tools like **Hugo**, **Jekyll**, **Docusaurus**, **Astro**
  turn Markdown into a full website of HTML pages at build time.

### Why `nginx-unprivileged`?

The official `nginx` image starts as **root** to listen on port 80. The
**`nginxinc/nginx-unprivileged`** image is maintained by the nginx team and runs as user
`nginx` (UID 101) on port **8080** — works out-of-the-box with Kubernetes `runAsNonRoot`
and OpenShift.

### ⚠️ The #1 frontend gotcha: build-time environment variables

Frontend env vars (`VITE_API_URL`, `REACT_APP_API_URL`, `NEXT_PUBLIC_*`) are **replaced
with literal text during `npm run build`**. They are **not** read at runtime — the browser
can't read the container's environment!

Consequence: an image built with `VITE_API_URL=https://dev-api` will **always** call
dev-api — even in production. Solutions: build one image per environment (passing build
args), or use **runtime config injection** (Example 69). Also: **never put secrets** in
frontend env vars — every user can read them in the browser's dev tools.

### Starter `.dockerignore` for frontends

```gitignore
node_modules
dist
build
.angular
.svelte-kit
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
| 63 | [Plain HTML/CSS site on nginx](#example-63--plain-htmlcss-site-on-nginx) | Simplest possible image |
| 64 | [React (Vite) → nginx-unprivileged](#example-64--react-vite--nginx-unprivileged) | SPA multi-stage |
| 65 | [Production nginx config for SPAs](#example-65--production-nginx-config-for-spas) | Caching, gzip, security headers |
| 66 | [Angular → nginx](#example-66--angular--nginx) | Angular's output path |
| 67 | [Vue (Vite) with build-time API URL](#example-67--vue-with-build-time-api-url) | Build args |
| 68 | [SvelteKit / Nuxt (Node SSR)](#example-68--sveltekit-node-ssr) | Server-side rendering |
| 69 | [Runtime config injection](#example-69--runtime-config-injection) | One image, many environments |
| 70 | [Hugo static site](#example-70--hugo-static-site) | Go-based SSG |
| 71 | [Docusaurus documentation site](#example-71--docusaurus-documentation-site) | Docs portal |
| 72 | [Caddy static server with automatic HTTPS](#example-72--caddy-static-server) | Alternative to nginx |

---

## Example 63 — Plain HTML/CSS site on nginx

**🧾 What is this?** Hand-written HTML files. No build step.

```dockerfile
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --chown=101:101 ./site /usr/share/nginx/html
EXPOSE 8080
```

**🔍 Explained:**

- `/usr/share/nginx/html` — nginx's default "web root"; files here are served at `/`.
- No `CMD` — the base image already starts nginx in the foreground.
- That's the whole Dockerfile. 3 lines. ~45 MB image.

**⚠️ DevOps Gotchas:**

- The `site/` folder must contain an `index.html`, or `/` returns 403 Forbidden.

---

## Example 64 — React (Vite) → nginx-unprivileged

**📁 Developer gives you:** `package.json`, `package-lock.json`, `vite.config.js`,
`index.html`, `src/`. `npm run build` outputs to `dist/`.

```dockerfile
# syntax=docker/dockerfile:1

############ Stage 1: build the static files with Node ############
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

############ Stage 2: serve them with nginx ############
FROM nginxinc/nginx-unprivileged:1.27-alpine
# Our nginx config (SPA routing) replaces the default site
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
```

`nginx.conf` (minimal):

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**🔍 Explained:**

- `npm ci` installs **all** dependencies (including dev ones) — the build tools *are*
  devDependencies here. That's fine: they stay in the build stage.
- `try_files $uri $uri/ /index.html` — "serve the file if it exists, else the folder,
  else fall back to `index.html`" → SPA routing works on refresh.
- The final image contains **zero** Node.js and **zero** `node_modules`.

**⚠️ DevOps Gotchas:**

- **Create React App** (older projects) outputs to `build/`, not `dist/`. Check
  `package.json` / the build log for the output folder.

---

## Example 65 — Production nginx config for SPAs

**🧾 What is this?** Same Dockerfile as Example 64, but with a production-grade nginx config:
caching, compression, security headers, and a health endpoint.

`nginx.conf`:

```nginx
server {
    listen 8080;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Don't reveal the nginx version in headers / error pages
    server_tokens off;

    # Compress text responses (smaller downloads)
    gzip on;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;
    gzip_min_length 1024;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Health endpoint for load balancers / Kubernetes probes
    location = /healthz {
        access_log off;
        return 200 "ok\n";
    }

    # Fingerprinted assets (e.g. index-a1b2c3.js) never change → cache for 1 year
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # index.html must NEVER be cached, or users get stale app versions after deploys
    location = /index.html {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**🔍 Explained:**

- `/assets/` — Vite puts hashed files here; the filename changes whenever content changes,
  so they can be cached "forever".
- `index.html` no-cache — it's the file that points to the newest hashed assets.
- `try_files $uri =404` in `/assets/` — a missing asset returns a real 404 instead of
  `index.html` (prevents confusing "Unexpected token <" JavaScript errors).

**⚠️ DevOps Gotchas:**

- **`add_header` inheritance trap:** if a `location` block has *any* `add_header`, it
  **drops all** `add_header` lines from the parent `server` block. Above, `/index.html` and
  `/assets/` lose the security headers. Fix by repeating them in those blocks or by putting
  them in a snippet file and `include`-ing it in each location.

---

## Example 66 — Angular → nginx

**🧾 What is this?** **Angular** is Google's frontend framework. Build command:
`ng build` (usually via `npm run build`). Angular 17+ outputs to `dist/<project-name>/browser/`.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npx ng build --configuration production

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Replace "my-app" with the project name from angular.json
COPY --from=build /app/dist/my-app/browser /usr/share/nginx/html
EXPOSE 8080
```

**🔍 Explained:**

- `npx ng build` — `npx` runs a tool from the project's `node_modules` (here the Angular CLI).
- `--configuration production` — enables optimisation, minification, and swaps in
  `environment.prod.ts`.

**⚠️ DevOps Gotchas:**

- **Output path changed** across Angular versions: older → `dist/my-app/`; 17+ (new
  "application" builder) → `dist/my-app/browser/`. Wrong path → nginx serves its default
  welcome page or 403.
- Angular builds are **memory-hungry**: large apps fail with
  `JavaScript heap out of memory`. Fix: `ENV NODE_OPTIONS=--max-old-space-size=4096` in the
  build stage (and enough RAM on the CI agent).
- If the app is served under a sub-path (`/portal/`), it needs `--base-href /portal/`.

---

## Example 67 — Vue with build-time API URL

**🧾 What is this?** A **Vue** app (built with Vite) that needs to know the backend API URL.
Because it's a build-time value, we pass it as a **build arg**.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .

# Build-time value: docker build --build-arg VITE_API_URL=https://api.example.com .
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}
RUN test -n "$VITE_API_URL" || (echo "ERROR: VITE_API_URL build arg is required" && exit 1) \
 && npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
```

**🔍 Explained:**

- `ARG VITE_API_URL` → `ENV VITE_API_URL=...` — Vite only reads environment variables
  starting with `VITE_` during the build.
- `test -n "$VITE_API_URL" || (... exit 1)` — **fail fast** if someone forgets the build arg,
  instead of shipping a broken frontend that calls `undefined/api/...`.
- `ARG` is placed **after** `npm ci` so changing the URL doesn't bust the dependency cache.

**⚠️ DevOps Gotchas:**

- This bakes the URL into the image → **separate images for dev/staging/prod**, which
  breaks the "build once, promote everywhere" principle. Example 69 fixes that.
- A **relative URL** (`/api`) + a reverse proxy/ingress routing `/api` to the backend
  avoids the problem entirely. Often the cleanest solution — suggest it to the team.

---

## Example 68 — SvelteKit (Node SSR)

**🧾 What is this?** Some frameworks do **Server-Side Rendering (SSR)** — they render pages
on a Node.js server for speed/SEO. **SvelteKit** (with `adapter-node`), **Nuxt** (Vue),
**Remix**, and **Next.js** (Chapter 1) work this way. These need **Node at runtime**, not nginx.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build \
 && npm prune --omit=dev

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOST=0.0.0.0
COPY --from=build --chown=node:node /app/build        ./build
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/package.json ./
USER node
EXPOSE 3000
CMD ["node", "build"]
```

**🔍 Explained:**

- SvelteKit's `adapter-node` outputs a runnable server in `build/` → `node build` runs `build/index.js`.
- `HOST` / `PORT` — env vars the adapter reads.
- **Nuxt** equivalent: output is `.output/`, run with `node .output/server/index.mjs`
  (and Nuxt bundles its own deps, so no `node_modules` copy needed).

**⚠️ DevOps Gotchas:**

- SvelteKit behind a proxy needs `ORIGIN=https://www.example.com` (or `PROTOCOL_HEADER` /
  `HOST_HEADER`), otherwise form submissions fail with "Cross-site POST form submissions are forbidden".

---

## Example 69 — Runtime config injection

**🧾 What is this?** Build the SPA **once**; at container start, write a small
`config.js` from environment variables. The app reads `window.APP_CONFIG` instead of
build-time vars. **One image → dev, staging, prod.**

`index.html` (dev adds this line **before** the main script):

```html
<script src="/config.js"></script>
```

`docker/40-runtime-config.sh`:

```sh
#!/bin/sh
set -eu
# Write runtime config from environment variables (no secrets here — it's public!)
cat > /usr/share/nginx/html/config.js <<EOF
window.APP_CONFIG = {
  API_URL: "${API_URL:-/api}",
  ENVIRONMENT: "${ENVIRONMENT:-production}",
  FEATURE_NEW_CHECKOUT: "${FEATURE_NEW_CHECKOUT:-false}"
};
EOF
echo "runtime config written for ENVIRONMENT=${ENVIRONMENT:-production}"
```

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=101:101 /app/dist /usr/share/nginx/html
# The html folder itself is root-owned in the base image; let nginx (UID 101) create files in it
USER root
RUN chown 101:101 /usr/share/nginx/html
USER 101
# Scripts in /docker-entrypoint.d/ run automatically before nginx starts
COPY --chmod=755 docker/40-runtime-config.sh /docker-entrypoint.d/40-runtime-config.sh
EXPOSE 8080
```

**▶️ Run:**

```bash
docker run -p 8080:8080 -e API_URL=https://api.prod.example.com -e ENVIRONMENT=prod spa:1.0.0
```

**🔍 Explained:**

- The official nginx images run every executable script in **`/docker-entrypoint.d/`**
  before starting nginx — a built-in hook. No custom entrypoint needed.
- `${API_URL:-/api}` — shell syntax for "use `$API_URL`, or `/api` if it's unset/empty".
- `--chown=101:101` + `chown` of the folder — the script runs as nginx (UID 101) and must be
  able to **create** `config.js` there. `COPY --chown` only changes the copied files, not an
  already-existing destination folder, hence the short `USER root` → `chown` → `USER 101` dance.

**⚠️ DevOps Gotchas:**

- Doesn't work with `readOnlyRootFilesystem: true` in Kubernetes (can't write the file).
  Alternative: mount `config.js` from a **ConfigMap** at `/usr/share/nginx/html/config.js`.
- `config.js` must be **no-cache** in nginx, like `index.html`.
- Everything in `config.js` is **public**. Never put API keys or secrets there.

---

## Example 70 — Hugo static site

**🧾 What is this?** **Hugo** is a very fast static site generator (written in Go). It turns
Markdown + templates into HTML. Output: `public/`.

```dockerfile
# syntax=docker/dockerfile:1
FROM hugomods/hugo:exts-0.136.5 AS build
WORKDIR /src
COPY . .
# --minify: smaller HTML/CSS/JS; --gc: clean unused cache files
RUN hugo --minify --gc --environment production

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /src/public /usr/share/nginx/html
EXPOSE 8080
```

**🔍 Explained:**

- `hugomods/hugo:exts-*` — a community image with Hugo "extended" (needed for SCSS themes)
  plus Git and Node. Pin the exact Hugo version the site was developed with.
- No SPA `try_files` needed — Hugo generates a real HTML file for every page.

**⚠️ DevOps Gotchas:**

- Themes are often **Git submodules**. If CI clones without submodules, the build fails
  with "template not found". Use `git clone --recurse-submodules` / `submodules: true` in
  the pipeline checkout step.
- Set `baseURL` correctly per environment (`hugo --baseURL https://docs.example.com/`), or
  links/CSS point to the wrong domain.

---

## Example 71 — Docusaurus documentation site

**🧾 What is this?** **Docusaurus** (by Meta) is a React-based docs site generator. Output: `build/`.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
```

**🔍 Explained:**

- Same two-stage pattern as React. Docusaurus pre-renders each page to HTML, so the default
  nginx config works.
- `wget` exists in the Alpine-based nginx image (busybox), so the healthcheck works.

**⚠️ DevOps Gotchas:**

- Docusaurus fails the build on **broken links** by default (`onBrokenLinks: 'throw'`). A
  docs PR with a typo'd link breaks the pipeline — that's intentional and good.

---

## Example 72 — Caddy static server

**🧾 What is this?** **Caddy** is a modern web server that obtains and renews **HTTPS
certificates automatically** (from Let's Encrypt). Great for small deployments on a single VM
without a separate load balancer.

`Caddyfile`:

```caddyfile
# Replace with your real domain; Caddy will fetch a TLS certificate automatically.
# For local testing use  :8080  instead of a domain.
www.example.com {
    root * /srv
    encode gzip zstd
    try_files {path} /index.html
    file_server
    header {
        X-Content-Type-Options nosniff
        Referrer-Policy strict-origin-when-cross-origin
        -Server
    }
}
```

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM caddy:2.8-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
EXPOSE 80 443
```

**🔍 Explained:**

- `try_files {path} /index.html` — Caddy's SPA fallback (same idea as nginx).
- `encode gzip zstd` — compression.
- `-Server` — removes the `Server` header.
- Ports 80 and 443 are needed for automatic HTTPS (Let's Encrypt validates over them).

**⚠️ DevOps Gotchas:**

- Caddy stores certificates in `/data`. **Mount a volume there** — otherwise every restart
  requests new certificates and you'll hit Let's Encrypt **rate limits** (blocked for a week).
- The domain's DNS must point at the server, and ports 80/443 must be open, before Caddy can
  get a certificate.
- Behind a cloud load balancer / ingress that already terminates TLS, use plain `:8080`
  in the Caddyfile — no automatic HTTPS needed.

---

**Next:** [07 — Databases, Caches, Queues & Proxies ➡️](07-databases-infra.md)
