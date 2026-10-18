# 00 — Dockerfile Fundamentals (Start Here)

> **Who this is for:** You have never written code and never built a Docker image.
> By the end of this chapter you will understand every word in a Dockerfile, and
> the later chapters (Node, Python, Java…) will just be "the same ideas, different
> ingredients".

[⬅️ Back to Handbook Index](README.md)

---

## Table of Contents

- [0.1 The 5 words you must know (no dev background needed)](#01-the-5-words-you-must-know)
- [0.2 What is a Dockerfile, really?](#02-what-is-a-dockerfile-really)
- [0.3 Image vs Container vs Registry](#03-image-vs-container-vs-registry)
- [0.4 Layers and the build cache — the most important idea](#04-layers-and-the-build-cache)
- [0.5 Every Dockerfile instruction explained](#05-every-dockerfile-instruction-explained)
- [0.6 Choosing a base image (alpine vs slim vs distroless vs scratch)](#06-choosing-a-base-image)
- [0.7 The `.dockerignore` file](#07-the-dockerignore-file)
- [0.8 Multi-stage builds — explained like a kitchen](#08-multi-stage-builds)
- [0.9 Commands you will type every day](#09-commands-you-will-type-every-day)
- [0.10 Examples 1–5: From a terrible Dockerfile to a great one](#010-examples-15)
- [0.11 The Best-Practices Checklist (print this)](#011-the-best-practices-checklist)
- [0.12 Master list of DevOps gotchas](#012-master-list-of-devops-gotchas)
- [0.13 Tools: linting and scanning your Dockerfiles](#013-tools-linting-and-scanning)

---

## 0.1 The 5 words you must know

Before Docker makes sense, you need five words from the developer world. You don't
need to *write* code, but you need to know what developers hand you.

| Word | Plain-English meaning | Analogy |
|------|----------------------|---------|
| **Source code** | Text files a developer writes (e.g. `app.py`, `index.js`, `Main.java`). | A recipe written on paper. |
| **Dependencies** (a.k.a. packages, libraries, modules) | Code written by *other* people that the app reuses. Listed in a file like `package.json`, `requirements.txt`, `pom.xml`. | Ingredients you buy from the store instead of growing yourself. |
| **Runtime** | The program that *runs* the source code (Node.js, Python, Java JVM, .NET). | The oven. |
| **Build / compile** | Turning source code into something runnable (a binary, a `.jar`, a minified website). Some languages need it, some don't. | Baking the dough into bread. |
| **Port** | A numbered "door" on a computer where an app listens for network traffic (e.g. 80 for web, 5432 for PostgreSQL). | Apartment number in a building. |

### Two families of languages (this decides your Dockerfile shape)

```
INTERPRETED (no compile step, need runtime at run time)
  Python, JavaScript/Node.js, Ruby, PHP
  ──► Image must contain: runtime + dependencies + source code

COMPILED (build step produces an output)
  Go, Rust, C/C++   ──► output = a single native binary  ──► can run on almost nothing (scratch!)
  Java, Kotlin      ──► output = .jar file               ──► still needs a JVM (Java runtime)
  C# / .NET         ──► output = .dll files               ──► needs .NET runtime (or self-contained)
  React/Vue/Angular ──► output = static HTML/CSS/JS        ──► just needs a web server (nginx)
```

> 💡 **Key insight:** For compiled stacks, the tools needed to *build* (compilers, SDKs —
> often 500 MB–1 GB) are NOT needed to *run*. That's why we use **multi-stage builds**
> (section 0.8) — build in a big image, copy only the result into a tiny one.

### What's a "dependency manifest" and a "lock file"?

Every stack has two files that list dependencies:

| Stack | Manifest (what I want) | Lock file (exactly what I got) | Install command |
|-------|------------------------|-------------------------------|-----------------|
| Node.js | `package.json` | `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | `npm ci` |
| Python | `requirements.txt` / `pyproject.toml` | `poetry.lock` / `uv.lock` | `pip install -r` |
| Java | `pom.xml` (Maven) / `build.gradle` | (versions are in the manifest) | `mvn package` |
| Go | `go.mod` | `go.sum` | `go mod download` |
| Rust | `Cargo.toml` | `Cargo.lock` | `cargo build` |
| PHP | `composer.json` | `composer.lock` | `composer install` |
| Ruby | `Gemfile` | `Gemfile.lock` | `bundle install` |
| .NET | `*.csproj` | `packages.lock.json` (optional) | `dotnet restore` |

> ⚠️ **DevOps gotcha:** The **lock file** guarantees the same versions every build. If a
> developer forgets to commit it, your builds become non-reproducible ("worked yesterday,
> broken today" because a library released a new version overnight). Always ask for it.

---

## 0.2 What is a Dockerfile, really?

A **Dockerfile** is a plain text file (literally named `Dockerfile`, no extension) that
contains **step-by-step instructions** to build an **image**.

Think of it as a recipe card:

```
Recipe card (Dockerfile)              What Docker does
─────────────────────────             ───────────────────────────────
1. Start with a clean Linux box  ──►  FROM python:3.12-slim
2. Go into the /app folder       ──►  WORKDIR /app
3. Bring in the ingredients list ──►  COPY requirements.txt .
4. Buy the ingredients           ──►  RUN pip install -r requirements.txt
5. Bring in the recipe           ──►  COPY . .
6. When served, do this          ──►  CMD ["python", "app.py"]
```

The output is an **image** — a frozen, portable snapshot of a tiny Linux filesystem that
contains *everything* the app needs. Anyone with Docker can run it and get the exact same result.

---

## 0.3 Image vs Container vs Registry

```
   Dockerfile ──(docker build)──► IMAGE ──(docker run)──► CONTAINER
   (recipe)                       (frozen meal,           (meal being eaten;
                                   read-only)              running process)
                                     │
                              (docker push / pull)
                                     ▼
                                 REGISTRY
                     (Docker Hub, Azure ACR, AWS ECR, GHCR)
                         = a warehouse of images
```

| Thing | Is it running? | Can it change? | Example |
|-------|----------------|----------------|---------|
| **Image** | No | No — read-only | `myapp:1.4.2` |
| **Container** | Yes | Yes, but changes vanish when it's deleted | `docker run myapp:1.4.2` |
| **Registry** | — | Stores images | `myregistry.azurecr.io/myapp:1.4.2` |

> ⚠️ **DevOps gotcha:** Anything written *inside* a container (uploaded files, logs, DB data)
> is **lost** when the container is removed. Persistent data must go into a **volume**.

### Image naming: `registry/repository:tag`

```
myregistry.azurecr.io / team/payments-api : 1.4.2
└──── registry ─────┘   └── repository ─┘   └tag┘
```

- No registry given → Docker Hub is assumed.
- No tag given → `:latest` is assumed (**never rely on `latest` in production** — it moves).

---

## 0.4 Layers and the build cache

This is **the** concept that separates good Dockerfiles from bad ones.

Each instruction (`FROM`, `COPY`, `RUN`, …) creates a **layer**. A layer is like a
transparent sheet stacked on top of the previous one.

```
  ┌─────────────────────────────┐  Layer 5: COPY . .            (your source code — changes often)
  ├─────────────────────────────┤  Layer 4: RUN pip install     (dependencies — change rarely)
  ├─────────────────────────────┤  Layer 3: COPY requirements   (dependency list — changes rarely)
  ├─────────────────────────────┤  Layer 2: WORKDIR /app
  └─────────────────────────────┘  Layer 1: FROM python:3.12    (base OS + Python)
```

**The cache rule:** When you rebuild, Docker reuses ("caches") each layer **until it hits
the first instruction whose input changed**. From that point **everything below is rebuilt**.

### Why order matters — a real example

```
❌ BAD ORDER                          ✅ GOOD ORDER
COPY . .                              COPY requirements.txt .
RUN pip install -r requirements.txt   RUN pip install -r requirements.txt
                                      COPY . .
```

- Developer changes **one line** of `app.py`.
- **Bad order:** `COPY . .` changed → pip install re-runs → **5 minutes** wasted downloading.
- **Good order:** `requirements.txt` didn't change → pip install layer **reused** → build takes **2 seconds**.

> 🧠 **Golden rule:** Order instructions from **least frequently changed** (top) to
> **most frequently changed** (bottom).

### Layers are additive — deleting later doesn't shrink the image

```dockerfile
RUN curl -o big.tar.gz https://example.com/big.tar.gz   # layer adds 500 MB
RUN rm big.tar.gz                                        # layer "hides" it — image is STILL 500 MB bigger
```

Fix: download, use, and delete **in the same `RUN`**:

```dockerfile
RUN curl -o big.tar.gz https://example.com/big.tar.gz \
 && tar -xzf big.tar.gz \
 && rm big.tar.gz
```

---

## 0.5 Every Dockerfile instruction explained

| Instruction | What it does | Beginner explanation | Example |
|-------------|--------------|---------------------|---------|
| `# syntax=` | Picks the Dockerfile parser version | Must be the very first line. Unlocks modern features (cache mounts, secrets, heredocs). | `# syntax=docker/dockerfile:1` |
| `FROM` | Sets the base image | "Start from this pre-made box". Every Dockerfile starts with it. | `FROM node:22-alpine` |
| `FROM ... AS name` | Names a stage | Used in multi-stage builds so later stages can copy from it. | `FROM golang:1.23 AS build` |
| `ARG` | Build-time variable | Value only exists while **building**. Gone at run time. | `ARG APP_VERSION=1.0.0` |
| `ENV` | Environment variable | Exists at build **and** run time. Apps read config from it. | `ENV PORT=8080` |
| `WORKDIR` | Sets the current folder | Like `cd`, but creates the folder if missing. All later commands run here. | `WORKDIR /app` |
| `COPY` | Copies files from your machine into the image | Source is relative to the **build context** (the folder you build from). | `COPY package.json ./` |
| `COPY --from=` | Copies from another stage/image | The heart of multi-stage builds. | `COPY --from=build /out/app /app` |
| `COPY --chown=` | Copies and sets file owner | Avoids a separate `chown` layer that doubles the size. | `COPY --chown=app:app . .` |
| `ADD` | Like COPY but can extract tars and download URLs | **Prefer `COPY`**. `ADD` has surprising magic. Use only to auto-extract a local `.tar.gz`. | `ADD rootfs.tar.gz /` |
| `RUN` | Runs a command **during build** | Installs software, compiles code. Result is saved as a layer. | `RUN apt-get update && apt-get install -y curl` |
| `USER` | Switches the user | Everything after (and the running app) runs as this user. **Never run as root.** | `USER 1001` |
| `EXPOSE` | Documents the port | **Does NOT open/publish the port.** It's documentation. You still need `-p` at `docker run`. | `EXPOSE 8080` |
| `CMD` | Default command when the container starts | Can be overridden by `docker run image <other command>`. Only the last `CMD` counts. | `CMD ["node", "server.js"]` |
| `ENTRYPOINT` | The fixed executable | Makes the container behave like a program. `CMD` then becomes its default arguments. | `ENTRYPOINT ["terraform"]` |
| `HEALTHCHECK` | Command Docker runs to check if the app is healthy | Lets Docker/Compose/Swarm know the app is truly working, not just "running". (Kubernetes ignores it — it uses probes.) | `HEALTHCHECK CMD curl -f http://localhost:8080/health \|\| exit 1` |
| `LABEL` | Metadata key/values | Who owns it, git commit, version. Shown in `docker inspect`. | `LABEL org.opencontainers.image.source="https://github.com/org/repo"` |
| `VOLUME` | Marks a folder as external storage | Data written here survives container removal. Use sparingly in app images. | `VOLUME /var/lib/data` |
| `STOPSIGNAL` | Signal sent to stop the app | Default `SIGTERM`. Some apps (nginx) prefer others (`SIGQUIT`). | `STOPSIGNAL SIGQUIT` |
| `SHELL` | Changes the shell for `RUN` | Mostly used for `bash -o pipefail` or PowerShell on Windows. | `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` |
| `ONBUILD` | Trigger for child images | Rarely used, confusing. Avoid. | — |

### `CMD` / `ENTRYPOINT`: exec form vs shell form (THE classic gotcha)

```dockerfile
CMD ["node", "server.js"]   # ✅ EXEC form (JSON array) — node is PID 1, receives stop signals
CMD node server.js          # ❌ SHELL form — runs "/bin/sh -c node server.js"; sh is PID 1
```

**Why it matters:** When you run `docker stop` (or Kubernetes deletes a pod), Docker sends
`SIGTERM` ("please shut down gracefully") to **PID 1**. In shell form, PID 1 is `sh`, which
does **not** forward the signal to your app. Docker waits 10 seconds, then **kills** it
(`SIGKILL`). Result: dropped requests, half-written files, slow deployments.

> ✅ **Always use the JSON-array (exec) form for `CMD` and `ENTRYPOINT`.**

### `ENTRYPOINT` + `CMD` together

```dockerfile
ENTRYPOINT ["python", "backup.py"]
CMD ["--help"]
```

| You type | What runs |
|----------|-----------|
| `docker run backup-tool` | `python backup.py --help` |
| `docker run backup-tool --db prod` | `python backup.py --db prod` (CMD replaced) |

### `ARG` vs `ENV` — which one?

```
ARG  ── exists only during `docker build` ──► version numbers, build flags
ENV  ── baked into the image, visible at runtime ──► PORT, NODE_ENV, PATH
```

> ⚠️ **DevOps gotcha:** **Never put secrets (passwords, tokens) in `ARG` or `ENV`.** Both are
> visible to anyone who runs `docker history` or `docker inspect` on the image. Use BuildKit
> secrets at build time (Chapter 10) and runtime secrets (Kubernetes Secrets, Azure Key
> Vault) at run time.

---

## 0.6 Choosing a base image

The `FROM` line is the biggest decision. It controls **size**, **security**, and **compatibility**.

| Variant | Example | Size (approx.) | Has shell? | Package manager | Use when |
|---------|---------|----------------|-----------|-----------------|----------|
| **Full** | `python:3.12` | ~1 GB | ✅ bash | apt | Building/compiling things; never for running in prod |
| **slim** | `python:3.12-slim` | ~130 MB | ✅ bash | apt | **Safe default** for interpreted languages |
| **alpine** | `python:3.12-alpine` | ~50 MB | ✅ sh (busybox) | apk | Small images; careful with Python/native libs (musl) |
| **distroless** | `gcr.io/distroless/python3-debian12` | ~50 MB | ❌ | ❌ | Production hardening; no shell = smaller attack surface |
| **chiseled** (Ubuntu/.NET) | `mcr.microsoft.com/dotnet/aspnet:8.0-noble-chiseled` | ~110 MB | ❌ | ❌ | .NET production |
| **scratch** | `scratch` | 0 MB | ❌ | ❌ | Static binaries only (Go, Rust) |

### Alpine vs Debian-based — the "musl vs glibc" gotcha

- Debian/Ubuntu images use **glibc** (the standard C library).
- Alpine uses **musl** (a smaller C library).
- Many pre-compiled packages (Python "wheels", Node native addons, Oracle drivers, some
  monitoring agents) are built **for glibc**. On Alpine they either fail or must be
  compiled from source → builds become slower and *bigger* than slim.

> 🧠 **Rule of thumb:** Default to **`-slim`** (Debian). Use **alpine** for Go/static stuff
> and Node when you've tested it. Use **distroless/chiseled** for hardened production.

### Pinning versions

```dockerfile
FROM node:latest                 # ❌ changes without warning
FROM node:22                     # ⚠️ OK-ish — major version pinned
FROM node:22.11-alpine3.20       # ✅ minor + OS pinned
FROM node:22.11-alpine3.20@sha256:abc123...   # ✅✅ digest = byte-for-byte identical forever
```

> ⚠️ **DevOps gotcha:** Pinning a digest means you **won't get security patches**
> automatically. Pair pinning with a bot (Dependabot / Renovate) that opens PRs to bump the
> version. Reproducible **and** patched.

> 📝 **About versions in this handbook:** Examples use version tags that were current when
> written (e.g. `node:22`, `python:3.12`). Always check Docker Hub for the latest supported
> version of your stack before copying.

---

## 0.7 The `.dockerignore` file

When you run `docker build .`, the `.` is the **build context** — Docker uploads **that
whole folder** to the builder. A `.dockerignore` file (next to the Dockerfile) lists what
to exclude, exactly like `.gitignore`.

**Why it matters:**

1. **Speed** — not uploading 800 MB of `node_modules` or `.git`.
2. **Security** — not baking `.env` files with passwords into the image via `COPY . .`.
3. **Cache** — irrelevant file changes (README edits) don't bust the `COPY . .` layer.

### Universal starter `.dockerignore`

```gitignore
# Version control
.git
.gitignore

# Secrets — NEVER ship these
.env
.env.*
*.pem
*.key
secrets/

# Dependencies (re-installed inside the image)
node_modules/
vendor/
.venv/
venv/
__pycache__/
*.pyc

# Build outputs (re-built inside the image)
dist/
build/
target/
bin/
obj/

# Editor / OS junk
.vscode/
.idea/
.DS_Store
Thumbs.db

# Docker files themselves
Dockerfile*
docker-compose*.yml
.dockerignore

# CI, docs, tests (optional — keep tests if you run them in the build)
.github/
docs/
*.md
coverage/
```

> ⚠️ **DevOps gotcha:** If you exclude `*.md` but your app reads `README.md` at runtime,
> it breaks. If you exclude tests but have a `test` stage, tests can't run. Tailor it.

> ⚠️ **DevOps gotcha:** Copying a local `node_modules/` built on Windows/macOS into a Linux
> image breaks native modules ("invalid ELF header"). `.dockerignore` it and install inside.

---

## 0.8 Multi-stage builds

**Analogy:** A restaurant kitchen is messy (knives, flour, pans). The customer only gets
the plate. A multi-stage build has a **kitchen stage** and a **plate stage**.

```
 ┌──────────── Stage 1: "build" (kitchen) ─────────────┐
 │ FROM golang:1.23        ← 800 MB of compilers       │
 │ COPY source code                                    │
 │ RUN go build -o app     ← produces one 10 MB file   │
 └──────────────────────────────┬──────────────────────┘
                                │ COPY --from=build /app
 ┌──────────── Stage 2: "runtime" (plate) ─────────────┐
 │ FROM gcr.io/distroless/static                       │
 │ just the 10 MB file     ← final image ~12 MB        │
 └─────────────────────────────────────────────────────┘
       Only the LAST stage becomes your image.
```

Benefits: **smaller** image (faster deploys), **safer** (no compilers for attackers to
use), **no source code** shipped to production.

You can also build a specific stage: `docker build --target build .` (useful for running tests).

---

## 0.9 Commands you will type every day

```bash
# Build an image from the Dockerfile in the current folder (.) and tag it
docker build -t myapp:1.0.0 .

# Build with a Dockerfile that has a different name/location
docker build -f docker/Dockerfile.prod -t myapp:1.0.0 .

# Run it: -d = background, -p HOST:CONTAINER = publish port, --name = friendly name
docker run -d -p 8080:3000 --name myapp myapp:1.0.0

# Pass environment variables at runtime
docker run -e DATABASE_URL="postgres://..." myapp:1.0.0

# See logs / get a shell inside / see running containers
docker logs -f myapp
docker exec -it myapp sh
docker ps

# Inspect the layers and their sizes (find what made the image fat)
docker history myapp:1.0.0
docker image ls myapp

# Stop & remove
docker stop myapp && docker rm myapp

# Tag and push to a registry
docker tag myapp:1.0.0 myregistry.azurecr.io/myapp:1.0.0
docker push myregistry.azurecr.io/myapp:1.0.0

# Clean up disk (dangling images, stopped containers, build cache)
docker system prune
```

> 💡 **`-p 8080:3000` explained:** "traffic arriving at port **8080 on my laptop** → forward
> to port **3000 inside the container**". Left = host, right = container.

> ⚠️ **DevOps gotcha:** Your app must listen on **`0.0.0.0`**, not `127.0.0.1`/`localhost`.
> Inside a container, `localhost` means "only this container" — port publishing can't
> reach it. Symptom: container runs fine, but browser shows "connection reset".

---

## 0.10 Examples 1–5

We'll evolve one tiny Python web app from the worst Dockerfile to a production-grade one.
You don't need to understand Python — focus on the **Dockerfile**.

Project layout the developer gave us:

```
myapp/
├── app.py              ← the application (source code)
├── requirements.txt    ← list of dependencies (Flask, gunicorn)
└── .dockerignore
```

---

### Example 1 — ❌ The "it works" Dockerfile (what NOT to do)

```dockerfile
FROM python
COPY . .
RUN pip install -r requirements.txt
CMD python app.py
```

**What's wrong (line by line):**

| Line | Problem |
|------|---------|
| `FROM python` | No tag → `latest` → 1 GB full image, and the Python version can change any day. |
| `COPY . .` | No `WORKDIR`, so files go to `/` (root of the filesystem) mixed with system files. Copies `.git`, `.env` secrets, everything. Placed **before** install → cache busted on every code change. |
| `RUN pip install` | Keeps pip's download cache inside the image (wasted MBs). |
| `CMD python app.py` | Shell form → app won't get stop signals. Runs Python's **development** server, which is not meant for production. |
| (missing) | Runs as **root**. No `EXPOSE`. No healthcheck. |

---

### Example 2 — Better: pinned image, WORKDIR, cache-friendly order

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
```

**What improved:**

- `python:3.12-slim` — pinned version, ~130 MB instead of ~1 GB.
- `WORKDIR /app` — clean, dedicated folder.
- `COPY requirements.txt` **first**, install, **then** `COPY . .` → code edits don't re-install dependencies.
- `--no-cache-dir` — pip doesn't keep downloaded archives in the image.
- Exec-form `CMD`.

Still missing: non-root user, production server, environment settings.

---

### Example 3 — Good: non-root user + production server

```dockerfile
FROM python:3.12-slim

# Python behaviour tweaks for containers (explained below)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Create an unprivileged user and group
RUN groupadd --system app && useradd --system --gid app --no-create-home app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --chown makes the files owned by our app user (in the same layer)
COPY --chown=app:app . .

USER app

EXPOSE 8000
# gunicorn = a production-grade web server for Python apps
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

**New lines explained:**

- `PYTHONDONTWRITEBYTECODE=1` — stops Python creating `.pyc` cache files (useless in a read-only image).
- `PYTHONUNBUFFERED=1` — makes logs appear **immediately** in `docker logs`. Without it, logs
  get stuck in a buffer and you see nothing while debugging an outage.
- `groupadd/useradd --system` — creates a user with no password and no login.
- `USER app` — from here on, nothing runs as root. If an attacker breaks into the app, they
  can't install tools or modify system files.
- `--bind 0.0.0.0:8000` — listen on all interfaces (see gotcha in 0.9).
- `app:app` — "in file `app.py`, find the object called `app`" (gunicorn syntax).

---

### Example 4 — Great: healthcheck + labels + pinned OS

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

LABEL org.opencontainers.image.title="myapp" \
      org.opencontainers.image.source="https://github.com/acme/myapp" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --no-create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app . .

USER 1001

EXPOSE 8000

# Uses Python itself (no need to install curl) to call the /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

**New lines explained:**

- `# syntax=docker/dockerfile:1` — use the latest stable Dockerfile features.
- `-bookworm` — pins the underlying Debian release (Debian 12 "bookworm"). Prevents a
  surprise OS upgrade when the base tag is updated to a newer Debian.
- `LABEL org.opencontainers.image.*` — standard (OCI) metadata. Registries like GHCR
  show the source repo link from it.
- `PIP_NO_CACHE_DIR=1` — same as `--no-cache-dir`, set once as an environment variable.
- `--uid 1001` + `USER 1001` — a **numeric** user. Kubernetes' `runAsNonRoot` check can
  only verify numeric UIDs, so numbers are more portable than names.
- `HEALTHCHECK` — every 30 s Docker calls `/health`. After 3 failures the container is
  marked `unhealthy`. `--start-period` gives the app 10 s to boot before failures count.

> ⚠️ **DevOps gotcha:** `HEALTHCHECK` requires the developer to actually build a
> `/health` endpoint. Ask for it. Also: **Kubernetes ignores `HEALTHCHECK`** — you
> configure `livenessProbe`/`readinessProbe` in the pod spec instead.

---

### Example 5 — Production: multi-stage with a virtual environment

When dependencies need compiling (e.g. database drivers), you need compilers (`gcc`) at
build time but not at run time. Multi-stage solves this.

```dockerfile
# syntax=docker/dockerfile:1

############################
# Stage 1: build (kitchen) #
############################
FROM python:3.12-slim-bookworm AS build

# Compilers and headers needed to build some Python packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# A "virtual environment" = a self-contained folder holding all Python packages
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

##############################
# Stage 2: runtime (plate)   #
##############################
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Only the runtime library (not the -dev headers or gcc)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --no-create-home app

WORKDIR /app

# Copy ONLY the finished packages from the build stage
COPY --from=build /opt/venv /opt/venv
COPY --chown=app:app . .

USER 1001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

**New lines explained:**

- `apt-get update && apt-get install ... && rm -rf /var/lib/apt/lists/*` — the **standard
  Debian install pattern**, always in **one** `RUN`:
  - `update` refreshes the package list (must be in the same RUN as install, otherwise a
    cached old list is used → "package not found" errors).
  - `-y` answers "yes" automatically (no human to type it during a build).
  - `--no-install-recommends` skips optional extras (saves 100s of MB).
  - `rm -rf /var/lib/apt/lists/*` deletes the package list (~40 MB) in the same layer.
- `build-essential` = gcc + make. `libpq-dev` = PostgreSQL headers for compiling.
- `libpq5` = just the PostgreSQL client library needed at run time.
- `python -m venv /opt/venv` — puts all packages in **one folder**, so we can copy that
  single folder to the next stage.
- `ENV PATH="/opt/venv/bin:$PATH"` — makes `python`, `pip`, `gunicorn` resolve to the venv versions.

Result: final image has no gcc, no headers — typically **40–60% smaller** than doing it in one stage.

> 🎉 Every Dockerfile in the rest of this handbook follows the ideas from Example 5.
> Once this one makes sense, the rest is just different ingredients.

---

## 0.11 The Best-Practices Checklist

Use this as a review checklist for **every** Dockerfile (yours or a developer's).

**Base image**
- [ ] Specific tag pinned (not `latest`); ideally OS release pinned too (`-bookworm`, `-alpine3.20`)
- [ ] Smallest image that works (`slim` / `alpine` / `distroless` / `scratch`)
- [ ] Official or verified-publisher image

**Build efficiency**
- [ ] `# syntax=docker/dockerfile:1` at the top
- [ ] `.dockerignore` present and excludes `.git`, `.env`, dependencies, build output
- [ ] Dependency manifest copied and installed **before** source code
- [ ] Lock file used with the "strict" install command (`npm ci`, `pip install -r`, `composer install --no-dev`, `bundle config deployment`)
- [ ] Multi-stage build for anything that compiles
- [ ] Package installs + cleanup in a **single** `RUN`

**Security**
- [ ] Runs as a non-root, **numeric** `USER`
- [ ] No secrets in `ARG`, `ENV`, or copied files
- [ ] No compilers / build tools in the final image
- [ ] `COPY` instead of `ADD`
- [ ] Image scanned (Trivy / Docker Scout / Defender for Containers)

**Runtime behaviour**
- [ ] Exec-form `CMD`/`ENTRYPOINT` (JSON array)
- [ ] App listens on `0.0.0.0` and the port is `EXPOSE`d
- [ ] Logs go to **stdout/stderr** (not log files inside the container)
- [ ] Config comes from environment variables (same image for dev/test/prod)
- [ ] Graceful shutdown on `SIGTERM` works
- [ ] `HEALTHCHECK` (for Docker/Compose) or probes (for Kubernetes)

**Maintainability**
- [ ] OCI `LABEL`s (source, version, revision)
- [ ] Comments explain *why*, not *what*
- [ ] Versions as `ARG`s at the top when they're reused
- [ ] Passes `hadolint`

---

## 0.12 Master list of DevOps gotchas

| # | Symptom | Cause | Fix |
|---|---------|-------|-----|
| 1 | Every build re-downloads all dependencies | `COPY . .` before dependency install | Copy manifest + lock file first |
| 2 | Image is 1–2 GB | Full base image; build tools in final image | `slim`/`alpine` + multi-stage |
| 3 | Deleting files didn't shrink the image | Files deleted in a later layer | Download+use+delete in the same `RUN` |
| 4 | `docker stop` takes exactly 10 s | Shell-form `CMD` or app ignores `SIGTERM` | Exec form; use `tini`/`--init` if needed |
| 5 | Container runs but browser can't connect | App bound to `127.0.0.1` | Bind to `0.0.0.0` |
| 6 | Port "doesn't work" | `EXPOSE` doesn't publish | Use `docker run -p host:container` |
| 7 | `apt-get install` says package not found | Cached old `apt-get update` layer | `update && install` in one `RUN` |
| 8 | Password visible in `docker history` | Secret passed via `ARG`/`ENV` | BuildKit `--mount=type=secret` |
| 9 | `.env` with prod passwords inside image | `COPY . .` without `.dockerignore` | Add `.env*` to `.dockerignore` |
| 10 | "exec format error" | Image built for `arm64` (Mac M-series) running on `amd64` server, or vice versa | `docker buildx build --platform linux/amd64` |
| 11 | "permission denied" writing files | Running as non-root but folder owned by root | `COPY --chown`, or `chown` the specific folder |
| 12 | Native module crash ("invalid ELF header") | Host `node_modules`/`venv` copied in | `.dockerignore` them; install inside |
| 13 | Python/Node package fails only on Alpine | musl vs glibc | Use `-slim` (Debian) |
| 14 | No logs in `docker logs` | App writes to a file, or Python buffering | Log to stdout; `PYTHONUNBUFFERED=1` |
| 15 | Data lost after restart | Data written inside container | Use volumes |
| 16 | Works on laptop, fails in CI | Different base image pulled (`latest`) | Pin versions / digests |
| 17 | `CRLF` errors: `/bin/sh^M: bad interpreter` | Shell script edited on Windows | Save with LF line endings (`.gitattributes`: `*.sh text eol=lf`) |
| 18 | `COPY failed: file not found` | File outside the build context or excluded by `.dockerignore` | Check build context path & `.dockerignore` |
| 19 | Timezone wrong in logs | Container defaults to UTC | That's usually *good*; set `TZ` env only if needed |
| 20 | Same image works in dev, fails in prod | Config baked into image | Inject config via env vars / mounted files at runtime |

---

## 0.13 Tools: linting and scanning

```bash
# hadolint — a linter that checks your Dockerfile against best practices
docker run --rm -i hadolint/hadolint < Dockerfile

# Trivy — scans the built image for known vulnerabilities (CVEs)
trivy image myapp:1.0.0

# Docker Scout — Docker's built-in scanner
docker scout cves myapp:1.0.0

# dive — interactive explorer to see what's inside each layer (find wasted space)
dive myapp:1.0.0
```

> 💡 In CI pipelines (GitHub Actions / Azure DevOps), run `hadolint` **before** building
> and `trivy` **after** building, and fail the pipeline on HIGH/CRITICAL findings.

---

**Next:** [01 — Node.js / JavaScript ➡️](01-nodejs.md)
