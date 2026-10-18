# 10 — Advanced Patterns & Production Hardening (Examples 104–115)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Data, ML & AI](09-data-ml-ai.md)

---

> These patterns aren't tied to one language. They're the techniques that separate a
> "works on my laptop" Dockerfile from one a platform team is happy to run in production.

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 104 | [Build secrets (private npm / NuGet feeds)](#example-104--build-secrets) | Tokens never touch a layer |
| 105 | [SSH mount for private Git repos](#example-105--ssh-mount-for-private-git-repos) | Use your SSH agent during build |
| 106 | [Cache mounts for OS packages + cheat sheet](#example-106--cache-mounts) | Faster rebuilds everywhere |
| 107 | [One Dockerfile, dev and prod targets](#example-107--one-dockerfile-dev-and-prod-targets) | `--target` |
| 108 | [Test & lint stage + exporting results](#example-108--test-and-lint-stage-with-exported-results) | CI inside the build |
| 109 | [Docker Compose full stack with health-gated startup](#example-109--docker-compose-full-stack) | Local environment |
| 110 | [OCI labels & build metadata](#example-110--oci-labels-and-build-metadata) | Traceability |
| 111 | [Signals & graceful shutdown deep dive](#example-111--signals-and-graceful-shutdown) | tini, `exec`, `trap`, `STOPSIGNAL` |
| 112 | [Read-only root filesystem](#example-112--read-only-root-filesystem) | Kubernetes hardening |
| 113 | [Heredocs in Dockerfiles](#example-113--heredocs) | Readable multi-line RUN/COPY |
| 114 | [Company "golden" base image + corporate CA](#example-114--company-golden-base-image) | Platform-team pattern |
| 115 | [Windows container: IIS + .NET Framework](#example-115--windows-container-iis--net-framework) | Legacy Windows apps |
| — | [Putting it together: CI pipelines](#putting-it-together-ci-pipelines) | GitHub Actions & Azure DevOps |
| — | [Final decision cheat sheet](#final-decision-cheat-sheet) | Which pattern when |

---

## Example 104 — Build secrets

**🧾 What is this?** Private package feeds (npm, NuGet, PyPI, Maven) need a token **during
the build**. BuildKit's `--mount=type=secret` makes the token available to one `RUN` as a
file, and **never stores it** in the image or its history.

### Node.js — private npm registry

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
# Mount the .npmrc (which contains the auth token) only for this command
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm ci
COPY . .
RUN npm run build
# ... runtime stage as usual (no .npmrc anywhere)
```

```bash
docker build --secret id=npmrc,src=$HOME/.npmrc -t app .
```

### .NET — private NuGet feed (Azure Artifacts)

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY nuget.config .
COPY src/MyApi/MyApi.csproj src/MyApi/
# The secret holds the feed token; the Azure Artifacts credential provider reads this env var
RUN --mount=type=secret,id=feed_token \
    export VSS_NUGET_EXTERNAL_FEED_ENDPOINTS="{\"endpointCredentials\":[{\"endpoint\":\"https://pkgs.dev.azure.com/acme/_packaging/internal/nuget/v3/index.json\",\"password\":\"$(cat /run/secrets/feed_token)\"}]}" \
 && dotnet restore src/MyApi/MyApi.csproj
COPY . .
RUN dotnet publish src/MyApi/MyApi.csproj -c Release -o /app/publish --no-restore
```

```bash
docker build --secret id=feed_token,env=SYSTEM_ACCESSTOKEN -t api .
```

**🔍 Explained:**

- `--mount=type=secret,id=X` — default location `/run/secrets/X`; `target=` places it
  elsewhere (e.g. where the tool expects a config file).
- `src=` reads from a file, `env=` reads from an environment variable on the build machine.
- `export VAR=... && command` — the variable lives only inside this `RUN`'s shell.

**⚠️ DevOps Gotchas — what NOT to do:**

| ❌ Anti-pattern | Why it leaks |
|----------------|--------------|
| `ARG NPM_TOKEN` | Visible in `docker history --no-trunc` |
| `ENV NPM_TOKEN=...` | Baked into image config, visible in `docker inspect` |
| `COPY .npmrc .` then `RUN rm .npmrc` | File is still in the earlier layer — extractable |
| Multi-stage with `COPY .npmrc` in build stage | Safer (not in final image) but stays in **build cache** and CI logs — still discouraged |

- The NuGet credential provider must be installed in the SDK image for
  `VSS_NUGET_EXTERNAL_FEED_ENDPOINTS` to work (Microsoft provides an install script);
  alternatively put the token into a `nuget.config` mounted as a secret.

---

## Example 105 — SSH mount for private Git repos

**🧾 What is this?** Some dependencies come straight from private Git repositories via SSH.
BuildKit can **forward your SSH agent** into one `RUN` — the private key never enters the build.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
RUN apt-get update \
 && apt-get install -y --no-install-recommends git openssh-client \
 && rm -rf /var/lib/apt/lists/*

# Trust GitHub's host key (avoids the interactive "are you sure?" prompt)
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

WORKDIR /app
COPY requirements.txt .
# requirements.txt contains e.g.:  git+ssh://git@github.com/acme/internal-lib.git@v1.2.0
RUN --mount=type=ssh \
    pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

```bash
# Start an agent and add your key (on your machine / CI agent)
eval "$(ssh-agent)" && ssh-add ~/.ssh/id_ed25519
docker build --ssh default -t app .
```

**🔍 Explained:**

- `--mount=type=ssh` — exposes the build machine's SSH agent socket to this one command.
- `--ssh default` — use the default agent (`$SSH_AUTH_SOCK`).
- `ssh-keyscan` — records GitHub's public host key so SSH doesn't stop and ask.

**⚠️ DevOps Gotchas:**

- `ssh-keyscan` trusts whatever key it receives at build time. For strict security, commit
  GitHub's published host keys to the repo and `COPY` them as `known_hosts`.
- In CI, use a **deploy key** (read-only, single repo) rather than a personal key.

---

## Example 106 — Cache mounts

**🧾 What is this?** We've used cache mounts for npm, pip, Maven, Go, Cargo. Here's the same
trick for **apt** (Debian/Ubuntu packages), plus a cheat sheet.

```dockerfile
# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

# Debian images auto-delete downloaded .deb files; disable that so the cache mount is useful
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
 && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates jq
```

**🔍 Explained:**

- `sharing=locked` — apt can't handle two builds using the same cache at once; this makes
  parallel builds wait their turn instead of corrupting the cache.
- No `rm -rf /var/lib/apt/lists/*` needed — those folders are cache mounts, not layers.

### Cache mount cheat sheet

| Tool | `target=` |
|------|-----------|
| npm | `/root/.npm` |
| pnpm | `/pnpm/store` (with `PNPM_HOME=/pnpm`) |
| yarn (classic) | `/usr/local/share/.cache/yarn` |
| pip | `/root/.cache/pip` |
| uv | `/root/.cache/uv` |
| Poetry | value of `POETRY_CACHE_DIR` |
| Maven | `/root/.m2` |
| Gradle | `/root/.gradle` (or `/home/gradle/.gradle` in gradle images) |
| Go modules / build | `/go/pkg/mod` and `/root/.cache/go-build` |
| Cargo | `/usr/local/cargo/registry` (+ `target/`) |
| NuGet | `/root/.nuget/packages` |
| Composer | `/tmp/cache` (composer image) or `~/.composer/cache` |
| Bundler | `/usr/local/bundle/cache` |
| apt | `/var/cache/apt` + `/var/lib/apt` |
| apk | `/var/cache/apk` (then drop `--no-cache`) |

**⚠️ DevOps Gotchas:**

- If the `RUN` runs as a **non-root user**, the cache path is that user's home, and the
  mount needs `uid=`/`gid=` options so the user can write to it.
- Cache mounts live on the **builder**. Ephemeral CI runners start empty — use registry
  or GHA cache backends (see CI section) for layer caching.

---

## Example 107 — One Dockerfile, dev and prod targets

**🧾 What is this?** Instead of `Dockerfile.dev` and `Dockerfile.prod` drifting apart, use
**one** file with named stages. Pick one with `--target`.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

############ dev: extra tools, auto-reload, source mounted ############
FROM base AS dev
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
# Source is bind-mounted by docker compose; --reload restarts on file changes
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

############ prod: lean, non-root (LAST stage = default target) ############
FROM base AS prod
RUN useradd --system --uid 1001 --no-create-home app
COPY --chown=1001:1001 app ./app
USER 1001
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build --target dev  -t app:dev .    # local development
docker build               -t app:1.0.0 .  # no --target → last stage (prod)
```

**🔍 Explained:**

- Both targets share the `base` stage → dependencies are identical in dev and prod.
- **Put `prod` last** — the default when someone forgets `--target` should be the safe one.
- BuildKit **skips stages not needed** for the chosen target (building `prod` never builds `dev`).

---

## Example 108 — Test and lint stage with exported results

**🧾 What is this?** Run linting and unit tests **inside** the Docker build, so CI uses
exactly the same environment as production. Then **export** test reports to the CI machine.

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM deps AS build
COPY . .
RUN npm run build

############ test: lint + unit tests ############
FROM build AS test
# Lint failures stop the build immediately. Test failures don't: we record them in a
# marker file so the reports can still be exported, and fail later in the "verify" stage
RUN npm run lint \
 && (npm test -- --ci --reporters=default --reporters=jest-junit || touch /app/TESTS_FAILED)

############ export: only the reports, written to the host ############
FROM scratch AS test-results
COPY --from=test /app/junit.xml /
COPY --from=test /app/coverage /coverage

############ verify: fail the build if tests failed ############
FROM test AS verify
RUN test ! -f /app/TESTS_FAILED

############ runtime ############
FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build --chown=node:node /app/dist ./dist
USER node
CMD ["node", "dist/index.js"]
```

**▶️ In CI:**

```bash
# 1) Write test reports to ./reports on the CI machine (even if tests failed)
docker build --target test-results --output type=local,dest=./reports .
# 2) Fail the pipeline if tests failed
docker build --target verify .
# 3) Build the real image (cached layers make this fast)
docker build -t app:1.0.0 .
```

**🔍 Explained:**

- `FROM scratch AS test-results` + `--output type=local,dest=./reports` — instead of making
  an image, BuildKit writes that stage's **files** to a local folder. CI can then publish
  JUnit results and coverage.
- The `TESTS_FAILED` marker lets us export reports **and** still fail the pipeline afterwards.
- The `runtime` stage doesn't depend on `test`, so `docker build -t app .` alone skips tests.
  That's why the pipeline builds `verify` explicitly.

**⚠️ DevOps Gotchas:**

- Tests that need a database/Redis can't easily run in `docker build` (no service
  containers). Run those **integration tests** with Docker Compose after building.

---

## Example 109 — Docker Compose full stack

**🧾 What is this?** **Docker Compose** starts several containers together from one YAML file
— perfect for running the whole app locally (API + database + cache). This example uses
**healthchecks** so the API only starts once the database is really ready.

`compose.yaml`:

```yaml
services:
  db:
    image: postgres:16-bookworm
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: localdevonly
      POSTGRES_DB: shop
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d shop"]
      interval: 5s
      timeout: 3s
      retries: 10

  redis:
    image: redis:7.4-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      retries: 10

  migrate:
    build: ./migrations              # Flyway image from Example 79
    environment:
      FLYWAY_URL: jdbc:postgresql://db:5432/shop
      FLYWAY_USER: app
      FLYWAY_PASSWORD: localdevonly
    depends_on:
      db: { condition: service_healthy }

  api:
    build:
      context: .
      target: prod
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://app:localdevonly@db:5432/shop
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:      { condition: service_healthy }
      redis:   { condition: service_healthy }
      migrate: { condition: service_completed_successfully }
    restart: unless-stopped

volumes:
  pgdata:
```

```bash
docker compose up --build        # build images and start everything
docker compose logs -f api       # follow API logs
docker compose down              # stop (keeps the pgdata volume)
docker compose down -v           # stop AND delete volumes (fresh database next time)
```

**🔍 Explained:**

- Services reach each other by **service name** (`db`, `redis`) — Compose creates a private
  network with built-in DNS. That's why `DATABASE_URL` uses host `db`, not `localhost`.
- `condition: service_healthy` — wait for the healthcheck to pass, not just for the container
  to start.
- `service_completed_successfully` — run migrations to completion before the API starts.
- `CMD-SHELL` vs `CMD` — `CMD-SHELL` runs through `/bin/sh` (needed for pipes, env vars).

**⚠️ DevOps Gotchas:**

- Plain `depends_on: [db]` only waits for the **container to start**, not for Postgres to
  accept connections → "connection refused" on first boot. Use healthcheck conditions.
- `localhost` inside a container is the container itself. The #1 Compose beginner error.
- Compose is great for **local/dev/CI**; production orchestration is Kubernetes, ECS,
  Azure Container Apps, etc.

---

## Example 110 — OCI labels and build metadata

**🧾 What is this?** During an incident you'll ask: *"What code is actually running?"*
Labels stamped at build time answer that from the image itself.

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/app .

FROM gcr.io/distroless/static-debian12:nonroot

# Supplied by CI
ARG VERSION=0.0.0-dev
ARG GIT_SHA=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.title="orders-api" \
      org.opencontainers.image.description="Order management REST API" \
      org.opencontainers.image.vendor="Acme Corp" \
      org.opencontainers.image.source="https://github.com/acme/orders-api" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.licenses="Proprietary" \
      com.acme.team="payments" \
      com.acme.oncall="#payments-oncall"

COPY --from=build /out/app /app
ENTRYPOINT ["/app"]
```

```bash
docker build \
  --build-arg VERSION=1.4.2 \
  --build-arg GIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  -t orders-api:1.4.2 .

# Read it back later
docker inspect orders-api:1.4.2 --format '{{json .Config.Labels}}'
```

**🔍 Explained:**

- `org.opencontainers.image.*` — standard label names understood by registries and scanners.
  GitHub links a GHCR package to its repo via `...image.source`.
- Custom `com.<company>.*` labels — ownership/on-call info.
- Labels are placed **late** in the final stage: changing them (every build) doesn't
  invalidate earlier cached layers.

**⚠️ DevOps Gotchas:**

- Tag images with **immutable** tags (`1.4.2`, `git-<sha>`), not just `latest`. Kubernetes
  won't re-pull a changed `latest` if `imagePullPolicy: IfNotPresent` — nodes run different
  code under the same tag.
- In GitHub Actions, `docker/metadata-action` generates these labels and tags automatically.

---

## Example 111 — Signals and graceful shutdown

**🧾 What is this?** When Kubernetes/Docker stops a container:

```
1. SIGTERM sent to PID 1   → "please finish what you're doing and exit"
2. Wait grace period       → Docker: 10s, Kubernetes: 30s (terminationGracePeriodSeconds)
3. SIGKILL                 → forced kill, no cleanup possible
```

If PID 1 doesn't handle SIGTERM, **every deploy drops in-flight requests**, and every stop
takes the full grace period.

### The three rules

| Rule | How |
|------|-----|
| 1. Your app must be PID 1 (or a proper init must be) | Exec-form `CMD`/`ENTRYPOINT`; `exec "$@"` in scripts |
| 2. Zombie processes must be reaped (apps that spawn children) | `tini` / `dumb-init` / `docker run --init` |
| 3. The app must react to the signal it receives | App code, or `STOPSIGNAL` for apps expecting another signal |

### Example: wrapper script that needs cleanup on shutdown

```bash
#!/bin/sh
# entrypoint.sh — starts the app, forwards SIGTERM, runs cleanup
set -eu

term_handler() {
  echo "SIGTERM received — draining..."
  kill -TERM "$child" 2>/dev/null
  wait "$child"
  echo "deregistering from service registry"
  # ... cleanup commands ...
  exit 143   # 128 + 15 (SIGTERM) — conventional exit code
}
trap term_handler TERM INT

"$@" &          # start the app in the background
child=$!
wait "$child"   # wait returns early when a trapped signal arrives
```

```dockerfile
FROM debian:bookworm-slim
# dumb-init: minimal init that forwards signals to the whole process group and reaps zombies
RUN apt-get update \
 && apt-get install -y --no-install-recommends dumb-init \
 && rm -rf /var/lib/apt/lists/*
COPY --chmod=755 entrypoint.sh /entrypoint.sh
COPY --chmod=755 myworker /usr/local/bin/myworker
USER 65532
ENTRYPOINT ["/usr/bin/dumb-init", "--", "/entrypoint.sh"]
CMD ["myworker", "--queue", "orders"]
```

### `STOPSIGNAL` — when the app expects a different signal

```dockerfile
FROM nginx:1.27-alpine
# nginx: SIGQUIT = graceful shutdown (finish requests), SIGTERM = fast shutdown
STOPSIGNAL SIGQUIT
```

**🔍 Explained:**

- **Use `exec "$@"`** (Example 29) when the script has nothing to do on shutdown.
- **Use `trap` + background child** (above) only when you need cleanup steps.
- Official nginx images already set `STOPSIGNAL SIGQUIT` — shown here for illustration.

**⚠️ DevOps Gotchas:**

- **Test it:** `docker run -d --name t img && time docker stop t`. If it takes ~10 s, signals
  aren't handled.
- In Kubernetes, also add a short `preStop: sleep 5` hook — it gives load balancers time to
  stop sending traffic to the pod **before** SIGTERM arrives.

---

## Example 112 — Read-only root filesystem

**🧾 What is this?** A strong hardening control: the container's filesystem is **read-only**.
Attackers can't drop malware or modify binaries. The app may only write to explicitly
mounted folders (like `/tmp`).

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    TMPDIR=/tmp
WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=root:root . .
USER 1001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/tmp", "app:app"]
```

Kubernetes pod spec snippet:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
volumeMounts:
  - name: tmp
    mountPath: /tmp
volumes:
  - name: tmp
    emptyDir:
      medium: Memory
      sizeLimit: 64Mi
```

Test locally:

```bash
docker run --read-only --tmpfs /tmp:rw,size=64m -p 8000:8000 app:1.0.0
```

**🔍 Explained:**

- `COPY --chown=root:root` + `USER 1001` — the app user can **read** code but not modify it,
  even without a read-only filesystem. Defence in depth.
- `PYTHONDONTWRITEBYTECODE=1` — otherwise Python tries to write `.pyc` files and logs errors.
- `--worker-tmp-dir /tmp` — gunicorn writes heartbeat files; point it at the writable mount.
- `capabilities: drop: ["ALL"]` — removes Linux kernel privileges the app doesn't need.

**⚠️ DevOps Gotchas:**

- Common write locations to mount when going read-only: `/tmp`, nginx's `/var/cache/nginx`
  and `/var/run`, Java's temp dir, app upload/cache folders. Run with `--read-only` locally
  and read the errors to find them all.

---

## Example 113 — Heredocs

**🧾 What is this?** Modern Dockerfile syntax lets you write multi-line scripts and inline
files with **heredocs** (`<<EOF ... EOF`) — no more `&& \` on every line.

```dockerfile
# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

# Multi-line RUN — each line runs in order; "set -e" stops on the first error
RUN <<EOF
set -eux
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl
rm -rf /var/lib/apt/lists/*
useradd --system --uid 1001 --no-create-home app
EOF

# Create a file inline — no need to keep a separate config file in the repo
COPY <<EOF /etc/app/config.ini
[server]
port = 8080
log_format = json
EOF

# Feed a heredoc to another interpreter via stdin (needs python3 in the image)
# RUN python3 <<EOF
# print("heredocs can feed any interpreter")
# EOF

USER 1001
```

**🔍 Explained:**

- `RUN <<EOF ... EOF` — the lines between are executed as one shell script in **one layer**.
- `set -eux` — `-e` exit on error, `-u` error on unset variables, `-x` print each command
  (great for debugging build logs). **Always include `set -e`** — without it, a failing line
  in the middle is ignored.
- `COPY <<EOF /path` — writes the text into a file in the image.
- Requires `# syntax=docker/dockerfile:1` (BuildKit).

**⚠️ DevOps Gotchas:**

- `$VARIABLES` inside an unquoted `<<EOF` are expanded by the **Dockerfile** at build time
  (from ARG/ENV). Use `<<"EOF"` (quoted) to keep `$` literal for the shell/file.
- Older tools that parse Dockerfiles (some linters/scanners) may not understand heredocs yet.

---

## Example 114 — Company "golden" base image

**🧾 What is this?** Platform teams often publish an internal **base image** every team must
use. It bakes in company standards once: **corporate CA certificates**, a standard non-root
user, an init process, timezone data, security patches. App teams then `FROM` it.

### Why corporate CA certificates matter

Many companies inspect HTTPS traffic with a **TLS-intercepting proxy** (Zscaler, Palo Alto,
Netskope). The proxy re-signs traffic with the **company's own root certificate**. Containers
don't trust it by default → every `pip install`, `npm ci`, `curl` fails with
`SSL: CERTIFICATE_VERIFY_FAILED` / `self-signed certificate in certificate chain`.

```dockerfile
# golden-base/Dockerfile  →  published as acr.acme.io/base/debian:12-2024.11
# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

# Company root CA(s) — public certificates, safe to include
COPY certs/acme-root-ca.crt /usr/local/share/ca-certificates/acme-root-ca.crt

RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends ca-certificates tini tzdata \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --home-dir /home/app --create-home app

# Make language runtimes use the system trust store (they each have their own by default!)
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/acme-root-ca.crt \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    TZ=UTC

LABEL org.opencontainers.image.vendor="Acme Corp" \
      com.acme.base-image="true"

ENTRYPOINT ["/usr/bin/tini", "--"]
USER 10001
```

App team's Dockerfile:

```dockerfile
FROM acr.acme.io/base/debian:12-2024.11
WORKDIR /home/app
COPY --chown=app:app myservice .
CMD ["./myservice"]
```

**🔍 Explained:**

- `/usr/local/share/ca-certificates/*.crt` + `update-ca-certificates` — Debian's way of adding
  trusted CAs (Alpine is the same; RHEL uses `/etc/pki/ca-trust/source/anchors/` +
  `update-ca-trust`).
- **Each runtime has its own trust store:**
  - Python `requests` → `REQUESTS_CA_BUNDLE`; pip → `PIP_CERT`
  - Node.js → `NODE_EXTRA_CA_CERTS`
  - Java → its own `cacerts` keystore: `keytool -importcert -cacerts -storepass changeit -noprompt -alias acme -file acme-root-ca.crt`
  - Go / curl / OpenSSL → system store / `SSL_CERT_FILE`
- `apt-get upgrade -y` — in a **base** image that's rebuilt regularly, this pulls OS
  security fixes. (In app images, prefer rebuilding on an updated base instead.)
- `ENTRYPOINT tini` — every child image gets proper signal handling for free.

**⚠️ DevOps Gotchas:**

- **Rebuild the golden image on a schedule** (weekly) and when upstream publishes CVE fixes,
  then trigger rebuilds of all app images (Renovate/Dependabot can bump the `FROM` tag).
- Child images inherit `USER 10001`. If a child needs to install packages, it must
  `USER root` … `USER 10001` again.
- Never put the CA's **private key** anywhere near an image — only the public certificate.

---

## Example 115 — Windows container: IIS + .NET Framework

**🧾 What is this?** Legacy **ASP.NET (.NET Framework 4.x)** apps only run on **Windows**.
Windows containers let you containerise them without rewriting. They run on **Windows
hosts** (Windows Server, AKS Windows node pools) — not on Linux.

```dockerfile
# escape=`
# ↑ Changes the escape character to backtick so Windows paths (C:\...) work naturally

########## Build ##########
FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2022 AS build
WORKDIR C:\src

# Restore NuGet packages first (cache-friendly)
COPY *.sln .
COPY LegacyWeb\*.csproj LegacyWeb\
COPY LegacyWeb\packages.config LegacyWeb\
RUN nuget restore

COPY . .
RUN msbuild LegacyWeb\LegacyWeb.csproj `
      /p:Configuration=Release `
      /p:DeployOnBuild=true `
      /p:WebPublishMethod=FileSystem `
      /p:PublishUrl=C:\publish

########## Runtime ##########
FROM mcr.microsoft.com/dotnet/framework/aspnet:4.8-windowsservercore-ltsc2022
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue';"]

# Remove the default IIS start page
RUN Remove-Item -Recurse -Force C:\inetpub\wwwroot\*

WORKDIR C:\inetpub\wwwroot
COPY --from=build C:\publish .

EXPOSE 80
# The base image's ENTRYPOINT (ServiceMonitor.exe w3svc) keeps IIS running and
# forwards environment variables to the app pool
```

**🔍 Explained:**

- `` # escape=` `` — parser directive (must be the first line): use backtick as the line
  continuation/escape character, so `C:\src` isn't mangled.
- `windowsservercore-ltsc2022` — Windows Server 2022 Core base. (`nanoserver` is smaller but
  can't run .NET Framework or IIS.)
- `msbuild ... /p:DeployOnBuild=true /p:PublishUrl=C:\publish` — builds and publishes the web
  app to a folder.
- `SHELL ["powershell", ...]` — `RUN` commands now use PowerShell. `$ErrorActionPreference =
  'Stop'` makes failures stop the build (like `set -e` in bash).
- `ServiceMonitor.exe` — Microsoft's tool that watches the IIS service (`w3svc`) and exits
  if it stops, so the container's lifecycle follows IIS.

**⚠️ DevOps Gotchas:**

- **Host/OS version matching:** a container built on `ltsc2022` needs a Windows Server 2022
  host (with process isolation). Version mismatch → "The container operating system does not
  match the host operating system". Hyper-V isolation relaxes this at a performance cost.
- **Huge images:** Windows Server Core images are **~2–5 GB**. First pulls on new nodes take
  minutes — pre-pull or use image caching on node pools.
- **Docker Desktop** must be switched to "Windows containers" mode to build these; Linux and
  Windows images can't be built in the same mode.
- In AKS, use a **Windows node pool** and `nodeSelector: kubernetes.io/os: windows`.
- `web.config` connection strings: move them to environment variables / Key Vault — Microsoft's
  `ServiceMonitor` can push env vars into the app pool.

---

## Putting it together: CI pipelines

### GitHub Actions — lint, build (multi-arch, cached), scan, push

```yaml
name: container
on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:

permissions:
  contents: read
  packages: write

jobs:
  image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Tags & labels
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha
            type=semver,pattern={{version}}

      - name: Build (and push on main/tags)
        uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan image
        if: github.event_name != 'pull_request'
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: "1"
          ignore-unfixed: true
```

> 📝 `type=sha` produces a short-SHA tag (`sha-1a2b3c4`); adjust the Trivy `image-ref` to
> match your tag format. Pin actions to commit SHAs in high-security repos.

### Azure DevOps — build & push to ACR

```yaml
trigger:
  branches: { include: [main] }

pool:
  vmImage: ubuntu-latest

variables:
  imageRepository: orders-api
  containerRegistry: acme-acr-connection   # service connection name
  tag: $(Build.BuildId)

steps:
  - script: docker run --rm -i hadolint/hadolint < Dockerfile
    displayName: Lint Dockerfile

  - task: Docker@2
    displayName: Build and push
    inputs:
      command: buildAndPush
      containerRegistry: $(containerRegistry)
      repository: $(imageRepository)
      dockerfile: Dockerfile
      tags: |
        $(tag)
        $(Build.SourceVersion)
    env:
      DOCKER_BUILDKIT: 1
```

---

## Final decision cheat sheet

| Situation | Pattern / Example |
|-----------|-------------------|
| Interpreted language (Python/Node/Ruby/PHP) | `-slim` base, deps before code, non-root — Ex 5, 6, 19 |
| Compiled to a static binary (Go/Rust) | Multi-stage → `distroless/static` or `scratch` — Ex 42, 43, 48 |
| JVM app | Maven/Gradle build stage → JRE runtime, `MaxRAMPercentage` — Ex 31, 33 |
| .NET app | SDK build stage → `aspnet` / chiseled — Ex 51, 52 |
| Frontend SPA | Node build stage → `nginx-unprivileged` — Ex 64, 65, 69 |
| Need a token to install deps | `--mount=type=secret` — Ex 28, 104 |
| Slow rebuilds | Layer ordering + cache mounts — Ex 9, 43, 106 |
| One app, many roles (web/worker/scheduler) | Same image, different `command` — Ex 24 |
| Same image for dev/stage/prod | Config via env at runtime — Ex 69 |
| Must run on Graviton/ARM + Intel | `buildx --platform` + `TARGETARCH` — Ex 45 |
| Corporate proxy breaks HTTPS | Golden base image with CA — Ex 114 |
| Startup steps before the app | Entrypoint script with `exec "$@"` — Ex 29 |
| Container takes 10 s to stop | Exec form, tini, signal handling — Ex 7, 111 |
| Security review asks for hardening | Non-root, distroless, read-only FS, drop caps — Ex 14, 40, 112 |
| Legacy .NET Framework app | Windows container — Ex 115 |

---

🎉 **That's all 115 examples.** Go back to the [Handbook Index](README.md) for the full list.
