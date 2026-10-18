# 04 — Go, Rust, C & C++ (Examples 41–50)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Java & JVM](03-java-jvm.md)

---

## 🧾 What are these languages? (for non-developers)

These are **compiled** languages that produce a **native binary** — a single executable
file that the CPU runs directly. No interpreter, no runtime (like Python/Node/JVM) needed.

| Language | Used for | Build tool | Manifest / lock |
|----------|----------|-----------|-----------------|
| **Go** (Golang) | Cloud tools & APIs. Docker, Kubernetes, Terraform are written in Go. | `go build` | `go.mod` / `go.sum` |
| **Rust** | High-performance, memory-safe systems & services | `cargo build` | `Cargo.toml` / `Cargo.lock` |
| **C** | Operating systems, embedded, legacy | `gcc`, `make` | `Makefile` |
| **C++** | Games, trading systems, databases, browsers | `g++`, `cmake` | `CMakeLists.txt` |

### Static vs dynamic binaries — this decides your final image

```
STATIC binary                                DYNAMIC binary
 ┌──────────────────────┐                     ┌──────────────────┐
 │ your code            │                     │ your code        │──► needs libc.so,
 │ + all libraries      │                     └──────────────────┘    libssl.so … from the OS
 │ + C library baked in │
 └──────────────────────┘
 Runs on ANY Linux — even "scratch"           Needs an OS with matching libraries
 (an empty image)                             (debian-slim / distroless/base / alpine)
```

- **Go** produces static binaries easily (`CGO_ENABLED=0`).
- **Rust** produces static binaries when targeting **musl** (`x86_64-unknown-linux-musl`).
- **C/C++** are dynamic by default; static needs `-static` and static versions of libraries.

### What does a `scratch` image lack? (you must add these yourself)

| Missing thing | Symptom if forgotten | Fix |
|---------------|---------------------|-----|
| **CA certificates** (`/etc/ssl/certs/ca-certificates.crt`) | `x509: certificate signed by unknown authority` on every HTTPS call | Copy from a build stage |
| **Timezone data** (`/usr/share/zoneinfo`) | `unknown time zone Asia/Kolkata` | Copy, or Go: `import _ "time/tzdata"` |
| **A user** (`/etc/passwd`) | Runs as root (UID 0) | `USER 65532:65532` (numbers work without passwd) |
| **A shell** | Can't `docker exec sh`; `HEALTHCHECK CMD` with shell fails | Use exec-form healthchecks that call the binary itself |
| **`/tmp`** | App crashes writing temp files | Create it in build stage and copy |

> 💡 **Easier option:** `gcr.io/distroless/static-debian12` = "scratch + CA certs + tzdata +
> `/etc/passwd` with a `nonroot` user". For Go, it's usually the best choice.

### Starter `.dockerignore`

```gitignore
# Go
bin/
vendor/      # remove this line if the team commits vendor/ intentionally
# Rust
target/
# C/C++
build/
*.o
*.a
*.so
# Common
.git
.env*
Dockerfile*
.dockerignore
```

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 41 | [Go API → Alpine](#example-41--go-api--alpine) | Basic multi-stage |
| 42 | [Go → scratch (the minimal image)](#example-42--go--scratch) | CA certs, tzdata, non-root |
| 43 | [Go → distroless, cache mounts, version stamping](#example-43--go--distroless-with-cache-mounts-and-version-stamping) | Production Go |
| 44 | [Go with private modules](#example-44--go-with-private-modules) | Git auth via secret |
| 45 | [Go multi-architecture (amd64 + arm64)](#example-45--go-multi-architecture-build) | Cross-compile with buildx |
| 46 | [Rust → debian-slim](#example-46--rust--debian-slim) | Basic Rust |
| 47 | [Rust with cargo-chef caching](#example-47--rust-with-cargo-chef-caching) | Cache Rust deps |
| 48 | [Rust static musl → scratch](#example-48--rust-static-musl--scratch) | Tiny Rust image |
| 49 | [C program with make → static](#example-49--c-program-with-make) | Classic C |
| 50 | [C++ with CMake + shared libraries](#example-50--c-with-cmake-and-shared-libraries) | Runtime libs |

---

## Example 41 — Go API → Alpine

**📁 Developer gives you:** `go.mod`, `go.sum`, `main.go` (and maybe `cmd/`, `internal/` folders).

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
WORKDIR /src

# Download modules first (cached until go.mod/go.sum change)
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# CGO_ENABLED=0 → pure-Go static binary. -o sets the output path.
RUN CGO_ENABLED=0 go build -o /out/server .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates tzdata \
 && adduser -D -u 1001 app
COPY --from=build /out/server /usr/local/bin/server
USER 1001
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/server"]
```

**🔍 Explained:**

- `go mod download` — fetches dependencies listed in `go.mod`/`go.sum`.
- `CGO_ENABLED=0` — disables "cgo" (Go calling C code). Result: a fully static binary that
  doesn't need any C library.
- `go build -o /out/server .` — compile the package in the current folder (`.`) into `/out/server`.
- Runtime: Alpine (~8 MB) + `ca-certificates` (for HTTPS) + `tzdata` (timezones).
- `adduser -D` — Alpine: create user with no password.

**⚠️ DevOps Gotchas:**

- If `main.go` is in `cmd/api/`, build with `go build -o /out/server ./cmd/api`.
- Alpine runtime is handy when you need a shell for debugging. For maximum hardening,
  see Examples 42–43.

---

## Example 42 — Go → scratch

**🧾 What is this?** `scratch` is a completely **empty** image. The final image contains
**only** your binary (+ the few files we add). Often **5–15 MB total**.

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23-alpine AS build
RUN apk add --no-cache ca-certificates tzdata
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
# -ldflags="-s -w" strips debug info → smaller binary
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /out/server ./cmd/server \
 && mkdir -p /out/tmp && chmod 1777 /out/tmp

FROM scratch
# HTTPS trust store + timezone database
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /usr/share/zoneinfo /usr/share/zoneinfo
# A writable /tmp
COPY --from=build /out/tmp /tmp
COPY --from=build /out/server /server
# Numeric UID/GID — works without /etc/passwd
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**🔍 Explained:**

- `-ldflags="-s -w"` — `-s` removes the symbol table, `-w` removes DWARF debug info.
  Typically shrinks the binary by ~25%.
- `chmod 1777` — world-writable with the "sticky bit" (standard `/tmp` permissions).
- `USER 65532:65532` — an unprivileged UID/GID. scratch has no `/etc/passwd`, but the
  kernel only cares about the number.

**⚠️ DevOps Gotchas:**

- **No shell, no tools.** `docker exec -it ... sh` → "executable file not found". Debug with
  `kubectl debug -it pod --image=busybox --target=container`.
- If the binary isn't truly static (cgo slipped in), the container fails with the
  misleading error `exec /server: no such file or directory`. The file exists — it's the
  **dynamic loader** that's missing. Check with `file server` or `ldd server` in the build stage.

---

## Example 43 — Go → distroless with cache mounts and version stamping

**🧾 What is this?** The production-grade Go Dockerfile: fast rebuilds via cache mounts,
version info embedded into the binary, distroless runtime.

```dockerfile
# syntax=docker/dockerfile:1
ARG GO_VERSION=1.23

FROM golang:${GO_VERSION}-bookworm AS build
WORKDIR /src

# Values injected by CI: docker build --build-arg VERSION=1.4.2 --build-arg COMMIT=$(git rev-parse --short HEAD)
ARG VERSION=dev
ARG COMMIT=none

# Bind-mount go.mod/go.sum and cache the module download directory
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=bind,source=go.mod,target=go.mod \
    --mount=type=bind,source=go.sum,target=go.sum \
    go mod download -x

# Cache both downloaded modules and the compiler's build cache
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=bind,target=. \
    CGO_ENABLED=0 go build \
      -trimpath \
      -ldflags="-s -w -X main.version=${VERSION} -X main.commit=${COMMIT}" \
      -o /out/server ./cmd/server

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

**🔍 Explained:**

- `--mount=type=bind,target=.` — mounts the whole build context read-only for this RUN
  instead of `COPY . .`. No source code layer is created at all.
- `/root/.cache/go-build` — Go's compile cache. Unchanged packages aren't recompiled.
- `-trimpath` — removes your machine's file paths from the binary (reproducible builds, no leaked paths).
- `-X main.version=${VERSION}` — sets a Go variable at link time, so the app can print
  `version 1.4.2 (abc1234)` on `/version` or at startup. Hugely useful during incidents.
- `distroless/static-debian12:nonroot` — scratch + CA certs + tzdata + nonroot user.

**⚠️ DevOps Gotchas:**

- `ARG`s declared *after* `FROM` are only visible in that stage. `GO_VERSION` (before
  `FROM`) works in `FROM` lines but **not** inside RUN unless re-declared.
- Changing `COMMIT` on every build invalidates the cache of the build step — acceptable,
  since that step needs to run anyway when code changes.

---

## Example 44 — Go with private modules

**🧾 What is this?** Companies keep shared Go libraries in **private Git repos**. `go mod
download` must authenticate. We pass a Git token as a **build secret**.

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.23-bookworm AS build

# Tell Go these module paths are private (don't use the public proxy/checksum DB)
ENV GOPRIVATE=github.com/acme-corp/*

WORKDIR /src
COPY go.mod go.sum ./

# Use the token only during this RUN; it never lands in an image layer
RUN --mount=type=secret,id=gh_token \
    --mount=type=cache,target=/go/pkg/mod \
    git config --global url."https://x-access-token:$(cat /run/secrets/gh_token)@github.com/".insteadOf "https://github.com/" \
 && go mod download \
 && git config --global --unset-all url."https://x-access-token:$(cat /run/secrets/gh_token)@github.com/".insteadOf

COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/server /server
ENTRYPOINT ["/server"]
```

**▶️ Build:**

```bash
docker build --secret id=gh_token,env=GITHUB_TOKEN -t svc .
```

**🔍 Explained:**

- `GOPRIVATE` — skips Go's public proxy for matching paths (it can't see private repos anyway).
- `git config ... insteadOf` — rewrites every `https://github.com/` URL to include the token.
- The config is removed again in the same RUN, so `~/.gitconfig` in the layer has no token.

**⚠️ DevOps Gotchas:**

- **Alternative: SSH agent forwarding** — `RUN --mount=type=ssh go mod download` with
  `docker build --ssh default .` (needs `git config url."git@github.com:".insteadOf ...`).
- Another common approach is `go mod vendor` in CI before the build, so no auth is needed
  inside Docker at all.

---

## Example 45 — Go multi-architecture build

**🧾 What is this?** Servers come in two CPU architectures: **amd64** (Intel/AMD — most
cloud VMs) and **arm64** (AWS Graviton, Azure Cobalt/Ampere, Apple M-series Macs, Raspberry Pi).
One **multi-arch image** works on both — Docker pulls the right variant automatically.

```dockerfile
# syntax=docker/dockerfile:1
# Run the build stage on the BUILD machine's native architecture (fast — no emulation)
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS build

# Provided automatically by buildx, e.g. TARGETOS=linux TARGETARCH=arm64
ARG TARGETOS
ARG TARGETARCH

WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
# Cross-compile for the TARGET architecture
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -ldflags="-s -w" -o /out/server .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/server /server
ENTRYPOINT ["/server"]
```

**▶️ Build & push for both architectures:**

```bash
docker buildx create --use            # once: create a builder that supports multi-platform
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t myregistry.azurecr.io/svc:1.0.0 \
  --push .
```

**🔍 Explained:**

- `--platform=$BUILDPLATFORM` — the build stage runs natively (e.g. amd64 CI agent).
- `GOARCH=$TARGETARCH` — Go **cross-compiles** for arm64 without emulation (very fast).
- The final stage has no `--platform`, so buildx produces one per target platform.
- `--push` — multi-arch images must be pushed to a registry (local Docker can't store a
  multi-platform image in the classic image store).

**⚠️ DevOps Gotchas:**

- **"exec format error"** = an image built for the wrong CPU. Classic case: a dev on an
  M-series Mac builds and pushes an arm64-only image; the amd64 AKS/EKS nodes can't run it.
- For languages that can't cross-compile easily, buildx falls back to **QEMU emulation** —
  works, but can be 5–20× slower.

---

## Example 46 — Rust → debian-slim

**📁 Developer gives you:** `Cargo.toml`, `Cargo.lock`, `src/main.rs`. Binary name = the
`name` in `Cargo.toml` (here: `myapp`).

```dockerfile
# syntax=docker/dockerfile:1
FROM rust:1-slim-bookworm AS build
WORKDIR /src
COPY . .
# Cache cargo's registry and the target dir; copy the binary out in the SAME RUN
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/src/target \
    cargo build --release --locked \
 && cp target/release/myapp /usr/local/bin/myapp

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 1001 --no-create-home app
COPY --from=build /usr/local/bin/myapp /usr/local/bin/myapp
USER 1001
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/myapp"]
```

**🔍 Explained:**

- `cargo build --release` — optimised production build (debug builds are 10–100× slower at runtime).
- `--locked` — fail if `Cargo.lock` would need changing (like `npm ci`).
- `--mount=type=cache,target=/src/target` — keeps compiled dependencies between builds.
  Because a cache mount is **not** part of the image, we must `cp` the binary out **in the
  same RUN**.
- Runtime is Debian slim because the binary is dynamically linked against glibc (and
  often OpenSSL).

**⚠️ DevOps Gotchas:**

- If the app uses OpenSSL (`openssl-sys` crate), the build needs `pkg-config libssl-dev`
  and the runtime needs `libssl3`. Many teams switch to `rustls` to avoid this.
- Rust compiles are **slow and RAM-hungry** — release builds of big projects can need
  4+ GB RAM and 10+ minutes. Cache properly (Example 47).

---

## Example 47 — Rust with cargo-chef caching

**🧾 What is this?** Rust compiles every dependency from source. Without caching, every
code change recompiles **everything**. **cargo-chef** creates a "recipe" of only the
dependencies, so they can be built in a cached layer — works even on CI without cache mounts.

```dockerfile
# syntax=docker/dockerfile:1
FROM lukemathwalker/cargo-chef:latest-rust-1-slim-bookworm AS chef
WORKDIR /app

# Stage: compute the dependency "recipe" (changes only when deps change)
FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# Stage: build dependencies, then the app
FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
# This layer is cached as long as recipe.json is unchanged
RUN cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN cargo build --release --locked --bin myapp

FROM debian:bookworm-slim AS runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --system --uid 1001 --no-create-home app
COPY --from=builder /app/target/release/myapp /usr/local/bin/myapp
USER 1001
ENTRYPOINT ["/usr/local/bin/myapp"]
```

**🔍 Explained:**

- `planner` — `cargo chef prepare` reads `Cargo.toml`/`Cargo.lock` and writes `recipe.json`.
  Even though we `COPY . .`, the output (`recipe.json`) only changes when deps change.
- `builder` — `cargo chef cook` compiles **only dependencies** from the recipe → cached layer.
  Then the real source is copied and only your crate is compiled (seconds, not minutes).

**⚠️ DevOps Gotchas:**

- Pin the cargo-chef image to a specific tag in real projects — `latest-*` moves.

---

## Example 48 — Rust static musl → scratch

**🧾 What is this?** Compile Rust against **musl** (instead of glibc) to get a fully static
binary that runs on `scratch`.

```dockerfile
# syntax=docker/dockerfile:1
FROM rust:1-alpine AS build
# musl-dev provides the musl C library headers for linking
RUN apk add --no-cache musl-dev ca-certificates
WORKDIR /src
COPY . .
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/src/target \
    cargo build --release --locked \
 && cp target/release/myapp /myapp

FROM scratch
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /myapp /myapp
USER 65532:65532
EXPOSE 8080
ENTRYPOINT ["/myapp"]
```

**🔍 Explained:**

- On Alpine, the Rust toolchain targets musl by default, and links statically.
- Final image = binary + CA certs. Often **< 10 MB**.

**⚠️ DevOps Gotchas:**

- musl's default memory allocator is slower than glibc's for heavily multi-threaded apps.
  Teams often add the `mimalloc` or `jemalloc` crate. If you see a performance drop after
  switching to musl, this is why.

---

## Example 49 — C program with make

**🧾 What is this?** A classic C program built with a `Makefile` (a file listing build
commands; you run `make`).

```dockerfile
# syntax=docker/dockerfile:1
FROM debian:bookworm-slim AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
# Build a statically-linked binary so it runs on a minimal image
RUN make CFLAGS="-O2 -Wall" LDFLAGS="-static" \
 && strip myprog

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /src/myprog /usr/local/bin/myprog
ENTRYPOINT ["/usr/local/bin/myprog"]
```

**🔍 Explained:**

- `build-essential` — gcc, g++, make, and C library headers.
- `CFLAGS="-O2 -Wall"` — optimise (`-O2`) and warn about suspicious code (`-Wall`).
- `LDFLAGS="-static"` — link everything statically.
- `strip` — removes debug symbols to reduce size.

**⚠️ DevOps Gotchas:**

- The `Makefile` must actually use `$(CFLAGS)` / `$(LDFLAGS)`; hand-written Makefiles
  sometimes ignore them. Check with `ldd myprog` (should say "not a dynamic executable").
- Static glibc binaries can misbehave with DNS lookups (NSS). If the program resolves
  hostnames, prefer a dynamic build on `distroless/base-debian12` or build static on Alpine/musl.

---

## Example 50 — C++ with CMake and shared libraries

**🧾 What is this?** **CMake** is the most common C++ build system. Here the app uses
shared libraries (Boost, OpenSSL), so the runtime image needs the **runtime** versions of
those libraries (not the `-dev` packages).

```dockerfile
# syntax=docker/dockerfile:1
FROM ubuntu:24.04 AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential cmake ninja-build \
      libboost-program-options-dev libssl-dev \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
RUN cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
 && cmake --build build --parallel \
 && cmake --install build --prefix /out

FROM ubuntu:24.04 AS runtime
# Only the runtime shared libraries (no compilers, no headers)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libboost-program-options1.83.0 libssl3t64 ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=build /out/bin/myserver /usr/local/bin/myserver
# Ubuntu 24.04 images include a non-root "ubuntu" user (UID 1000)
USER ubuntu
EXPOSE 9000
ENTRYPOINT ["/usr/local/bin/myserver"]
```

**🔍 Explained:**

- `cmake -S . -B build` — source in `.`, build files in `build/`.
- `-G Ninja` — use the Ninja build tool (faster than make).
- `-DCMAKE_BUILD_TYPE=Release` — optimised build.
- `cmake --install build --prefix /out` — puts the finished binary in `/out/bin/`.
- `-dev` packages (headers) in build, plain runtime library packages in runtime. The
  runtime package names include version numbers (`1.83.0`, `libssl3t64`), which differ per
  Ubuntu release.

**⚠️ DevOps Gotchas:**

- Missing runtime library → container fails with
  `error while loading shared libraries: libboost_xxx.so.1.83.0: cannot open shared object file`.
  Run `ldd /out/bin/myserver` in the build stage to list everything it needs.
- Build and runtime must use the **same distro release** — a binary built on Ubuntu 24.04
  may not run on Debian 11 (older glibc).

---

**Next:** [05 — .NET, PHP, Ruby, Elixir ➡️](05-dotnet-php-ruby-elixir.md)
