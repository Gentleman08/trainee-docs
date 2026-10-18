# 02 — Python (Examples 18–30)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Node.js](01-nodejs.md)

---

## 🧾 What is Python? (for non-developers)

- **Python** is an interpreted language (no compile step) used for web APIs, automation
  scripts, data science, and machine learning.
- **pip** is Python's package installer. Dependencies are listed in `requirements.txt`
  or `pyproject.toml`.
- A **virtual environment ("venv")** is a folder holding a project's own copy of Python
  packages, isolated from the system. Great for multi-stage copying.
- Python web apps need an **application server** in production:
  - **gunicorn** — for "WSGI" (traditional, synchronous) apps: Flask, Django.
  - **uvicorn** — for "ASGI" (async) apps: FastAPI, Starlette, modern Django.
  - Framework built-in servers (`flask run`, `manage.py runserver`) are **for development only**.

### Files you'll see in a Python project

| File | Meaning |
|------|---------|
| `requirements.txt` | Plain list of packages (`flask==3.0.3`) — the classic approach |
| `pyproject.toml` | Modern project file (dependencies + tool config) |
| `poetry.lock` | Lock file if the team uses **Poetry** |
| `uv.lock` | Lock file if the team uses **uv** (fast modern tool) |
| `Pipfile` / `Pipfile.lock` | If the team uses **Pipenv** |
| `manage.py` | Means it's a **Django** project |
| `wsgi.py` / `asgi.py` | Entry point for gunicorn / uvicorn |

### Python environment variables you'll use in every Dockerfile

| Variable | Why |
|----------|-----|
| `PYTHONUNBUFFERED=1` | Print logs immediately (otherwise `docker logs` shows nothing for a while) |
| `PYTHONDONTWRITEBYTECODE=1` | Don't create `.pyc` files at runtime |
| `PIP_NO_CACHE_DIR=1` | Don't keep pip's download cache in the image |
| `PIP_DISABLE_PIP_VERSION_CHECK=1` | Stop pip from phoning home to check for updates |

> ⚠️ **Python gotcha — Alpine:** Most Python packages ship pre-compiled "wheels" for
> **glibc** (Debian). Alpine uses musl, so packages like `numpy`, `pandas`, `psycopg2`,
> `cryptography` may have to **compile from source** — 10× slower builds and often
> *bigger* images. **Use `python:3.x-slim` by default.** (Example 26 shows the pain.)

### Starter `.dockerignore` for Python

```gitignore
__pycache__/
*.py[cod]
.venv/
venv/
.env*
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.git
Dockerfile*
.dockerignore
```

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 18 | [Python script / batch job](#example-18--python-script--batch-job) | ENTRYPOINT + arguments |
| 19 | [Flask + gunicorn](#example-19--flask--gunicorn) | WSGI web app |
| 20 | [Django + gunicorn + static files](#example-20--django--gunicorn--static-files) | collectstatic at build time |
| 21 | [FastAPI + uvicorn](#example-21--fastapi--uvicorn) | Async API |
| 22 | [Poetry, multi-stage](#example-22--poetry-multi-stage) | Export deps into a venv |
| 23 | [uv, multi-stage](#example-23--uv-multi-stage) | Modern fast installer |
| 24 | [Celery worker (same image, different command)](#example-24--celery-worker) | One image, many roles |
| 25 | [Streamlit dashboard](#example-25--streamlit-dashboard) | Data app |
| 26 | [Alpine vs slim — the compiled-deps trap](#example-26--alpine-vs-slim--the-compiled-deps-trap) | musl gotcha |
| 27 | [Distroless Python](#example-27--distroless-python) | Hardened runtime |
| 28 | [Private package index with a build secret](#example-28--private-package-index-with-a-build-secret) | No tokens in layers |
| 29 | [Entrypoint script pattern (Django migrations)](#example-29--entrypoint-script-pattern) | `docker-entrypoint.sh` + `exec` |
| 30 | [Pre-built wheels multi-stage](#example-30--pre-built-wheels-multi-stage) | `pip wheel` |

---

## Example 18 — Python script / batch job

**🧾 What is this?** Not a website — a script that runs, does a job (e.g. clean old files,
generate a report), and **exits**. Typical for cron jobs / Kubernetes CronJobs.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --system --uid 1001 --no-create-home appuser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=1001:1001 report.py .

USER 1001

# The container behaves like the program itself
ENTRYPOINT ["python", "report.py"]
# Default arguments (overridable)
CMD ["--days", "7"]
```

**🔍 Explained:**

- `ENTRYPOINT` = the fixed program. `CMD` = default arguments.
- `docker run report-job` → runs `python report.py --days 7`
- `docker run report-job --days 30` → runs `python report.py --days 30`
- No `EXPOSE` — a batch job doesn't listen on any port.

**⚠️ DevOps Gotchas:**

- The **exit code** matters: `0` = success, anything else = failure. Kubernetes Jobs and
  CI pipelines use it to decide retry/alert. Make sure the script exits non-zero on errors.
- Don't use `cron` *inside* a container for scheduling — use the orchestrator's scheduler
  (Kubernetes CronJob, Azure Container Apps Jobs, ECS scheduled tasks).

---

## Example 19 — Flask + gunicorn

**🧾 What is this?** **Flask** is a lightweight Python web framework. In production it
runs behind **gunicorn**.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
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

# Config via env so ops can tune without rebuilding
ENV GUNICORN_CMD_ARGS="--workers=3 --threads=2 --timeout=60 --access-logfile=-"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

**🔍 Explained:**

- `wsgi:app` — "import `wsgi.py`, use the object named `app`". Ask the developer for
  this — it's often `app:app`, `main:app`, or `myproject.wsgi:application`.
- `GUNICORN_CMD_ARGS` — gunicorn reads extra flags from this env var. Ops can override
  with `docker run -e GUNICORN_CMD_ARGS="--workers=8" ...`.
- `--access-logfile=-` — the `-` means **stdout**, so access logs show in `docker logs`.

**⚠️ DevOps Gotchas:**

- **Worker count:** the classic formula is `(2 × CPU cores) + 1`. But in Kubernetes the
  container sees the **node's** CPU count, not its CPU *limit*. A pod limited to 1 CPU on a
  64-core node would start 129 workers and get OOM-killed. **Set workers explicitly.**
- `--timeout=60` — gunicorn kills a worker if a request takes longer. Long reports →
  "WORKER TIMEOUT" errors in logs.

---

## Example 20 — Django + gunicorn + static files

**🧾 What is this?** **Django** is a full-featured Python web framework (admin panel,
database ORM, etc.). It has **static files** (CSS, JS, images) that must be "collected"
into one folder with `python manage.py collectstatic`.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=mysite.settings

RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --no-create-home app

WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=app:app . .

# Collect static files at BUILD time (needs a dummy secret key just to load settings)
RUN SECRET_KEY=build-only-not-secret python manage.py collectstatic --noinput

USER 1001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "mysite.wsgi:application"]
```

**🔍 Explained:**

- `DJANGO_SETTINGS_MODULE` — tells Django which settings file to use.
- `SECRET_KEY=build-only-not-secret python manage.py ...` — sets an env var **only for
  that one command**. Django refuses to start without a secret key, but collectstatic
  doesn't actually need the real one.
- `collectstatic --noinput` — gathers CSS/JS into `STATIC_ROOT` without asking questions.

**⚠️ DevOps Gotchas:**

- gunicorn doesn't serve static files. Either use the **WhiteNoise** library (dev adds it
  to Django), or serve them from nginx / a CDN / Azure Blob.
- **Don't run `migrate` (database schema changes) in the Dockerfile** — the database isn't
  available at build time, and it should run **once** per deploy, not once per replica.
  See Example 29 and Chapter 10.
- The real `SECRET_KEY` must come from runtime env/secret store, never the image.

---

## Example 21 — FastAPI + uvicorn

**🧾 What is this?** **FastAPI** is a modern, high-performance Python framework for APIs,
using async code. Runs on **uvicorn**.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=1001:1001 ./app ./app

USER 1001
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

# --proxy-headers: trust X-Forwarded-* headers when behind a load balancer / ingress
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
```

**🔍 Explained:**

- `COPY ./app ./app` — copies only the `app/` package folder, not tests/docs.
- `app.main:app` — "in `app/main.py`, the object named `app`".
- `--proxy-headers` — when behind nginx/an ingress, the app sees the real client IP and
  `https` scheme instead of the proxy's.

**⚠️ DevOps Gotchas:**

- One uvicorn process = one CPU core. In Kubernetes, prefer **1 process per container** and
  scale with replicas. On a single VM, use `--workers N` (or gunicorn with the uvicorn worker).
- If FastAPI is served under a path prefix (e.g. `/api`) by an ingress, add `--root-path /api`
  or the auto-generated docs page breaks.

---

## Example 22 — Poetry, multi-stage

**🧾 What is this?** **Poetry** is a popular tool to manage Python dependencies with
`pyproject.toml` + `poetry.lock`. We don't want Poetry itself in the final image — just
the installed packages.

```dockerfile
# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim-bookworm AS build
ENV POETRY_VERSION=1.8.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"
WORKDIR /app

COPY pyproject.toml poetry.lock ./
# Install only main (non-dev) deps into /app/.venv; skip installing the project itself
RUN --mount=type=cache,target=/tmp/poetry_cache \
    poetry install --only main --no-root

FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY --chown=1001:1001 src ./src
USER 1001
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**🔍 Explained:**

- `POETRY_VIRTUALENVS_IN_PROJECT=1` — Poetry creates the venv at `/app/.venv` (a
  predictable path we can copy).
- `--only main` — skip dev groups (tests, linters).
- `--no-root` — don't install the project's own code yet (it hasn't been copied); this
  keeps the dependency layer cacheable.
- Pinning `POETRY_VERSION` — different Poetry versions can resolve differently.

**⚠️ DevOps Gotchas:**

- If `poetry.lock` is out of date with `pyproject.toml`, the build fails with
  "pyproject.toml changed significantly". Ask the dev to run `poetry lock` and commit.
- The venv contains **absolute paths**. It must be at the **same path** in both stages
  (`/app/.venv` here) or scripts like `uvicorn` break.

---

## Example 23 — uv, multi-stage

**🧾 What is this?** **uv** (by Astral) is a very fast Rust-based replacement for pip/Poetry.
Projects using it have a `uv.lock` file.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS build

# Copy the uv binary from its official image (no pip install needed)
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies only (not the project) — cached layer
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Now copy the project and install it
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
RUN useradd --system --uid 1001 --no-create-home app
WORKDIR /app
COPY --from=build --chown=1001:1001 /app /app
USER 1001
EXPOSE 8000
CMD ["uvicorn", "myapp.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**🔍 Explained:**

- `COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/` — `--from` can point at **any
  image**, not just a stage. A neat trick to grab a single binary.
- `--mount=type=bind,source=uv.lock,...` — makes the file visible to this one `RUN`
  without creating a `COPY` layer.
- `--frozen` — use the lock file exactly; don't update it.
- `UV_COMPILE_BYTECODE=1` — pre-compiles `.pyc` files at build time → faster container startup.
- `UV_LINK_MODE=copy` — needed because the cache mount and the target are different filesystems.

**⚠️ DevOps Gotchas:**

- Pin the uv image tag (`:0.5`, or a full version). `:latest` changes behaviour over time.

---

## Example 24 — Celery worker

**🧾 What is this?** **Celery** runs **background jobs** (send emails, resize images)
outside the web request. It reads tasks from a queue (Redis/RabbitMQ). It uses the **same
code** as the web app — so we use **the same image** with a different command.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=1001:1001 . .

USER 1001
EXPOSE 8000

# Default role: web server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysite.wsgi:application"]
```

Run the **same image** in three roles (docker-compose):

```yaml
services:
  web:
    image: myapp:1.0.0
    ports: ["8000:8000"]
  worker:
    image: myapp:1.0.0
    command: ["celery", "-A", "mysite", "worker", "--loglevel=INFO", "--concurrency=2"]
  beat:
    image: myapp:1.0.0
    command: ["celery", "-A", "mysite", "beat", "--loglevel=INFO"]
```

**🔍 Explained:**

- **Build once, run many roles.** Overriding `command` replaces the image's `CMD`.
- `worker` = processes jobs. `beat` = the scheduler that enqueues periodic jobs.

**⚠️ DevOps Gotchas:**

- **Run exactly ONE `beat`** replica. Two beats = every scheduled job runs twice
  (double emails, double billing!).
- Workers need graceful shutdown time to finish tasks — set Kubernetes
  `terminationGracePeriodSeconds` higher than your longest task.

---

## Example 25 — Streamlit dashboard

**🧾 What is this?** **Streamlit** turns a Python data script into an interactive web
dashboard. Popular with data teams.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app
RUN useradd --uid 1001 --create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=1001:1001 . .

USER 1001
EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**🔍 Explained:**

- `STREAMLIT_SERVER_HEADLESS=true` — don't try to open a browser (there's no screen).
- `--create-home` — Streamlit writes config to the user's home folder, so the user needs one.
- `/_stcore/health` — Streamlit's built-in health endpoint.

**⚠️ DevOps Gotchas:**

- Streamlit uses **WebSockets**. Behind nginx/an ingress/Azure App Gateway, WebSocket
  upgrade must be enabled, and sticky sessions are needed with multiple replicas —
  otherwise the page keeps reconnecting.

---

## Example 26 — Alpine vs slim — the compiled-deps trap

**🧾 What is this?** A demonstration of *why* we prefer slim for Python.

```dockerfile
# ❌ Alpine version — requirements include pandas, psycopg2, cryptography
FROM python:3.12-alpine
WORKDIR /app
# Need a whole compiler toolchain because wheels for musl may not exist
RUN apk add --no-cache gcc g++ musl-dev libffi-dev postgresql-dev cargo rust
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt     # may take 15+ minutes
COPY . .
CMD ["python", "app.py"]
# Result: often 600 MB+ and slow builds
```

```dockerfile
# ✅ slim version — pre-built glibc wheels just download
FROM python:3.12-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt     # ~30 seconds
COPY . .
RUN useradd --system --uid 1001 app
USER 1001
CMD ["python", "app.py"]
# Result: typically ~300 MB, fast builds
```

**🔍 Explained:** "Wheels" are pre-compiled packages. PyPI has many `manylinux` (glibc)
wheels and fewer `musllinux` (Alpine) ones. No wheel → pip compiles from source → needs
compilers → huge and slow.

**⚠️ DevOps Gotchas:**

- This situation improves over time (more `musllinux` wheels exist each year), so test —
  but **slim is the safe default**.
- If you must use Alpine, put compilers in a **build stage only** (like Example 30).

---

## Example 27 — Distroless Python

**🧾 What is this?** Python runtime with no shell or package manager.

```dockerfile
# syntax=docker/dockerfile:1
# Build stage must use the SAME Python minor version as distroless (Debian 12 = Python 3.11)
FROM python:3.11-slim-bookworm AS build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=65532:65532 . .
ENV PYTHONPATH=/opt/venv/lib/python3.11/site-packages \
    PYTHONUNBUFFERED=1
EXPOSE 8000
# ENTRYPOINT of this image is already "python3"
CMD ["-m", "gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

**🔍 Explained:**

- Distroless Python's version is tied to Debian 12's Python (**3.11**). The build stage must
  match, or compiled packages won't load.
- We can't use the venv's `python` (it's a symlink to the build image's interpreter path), so we
  point `PYTHONPATH` at its `site-packages` and use distroless's own `python3`.
- `-m gunicorn` — run gunicorn as a module (the `gunicorn` script expects a shell-path shebang).

**⚠️ DevOps Gotchas:**

- This is the most fragile Python pattern — version mismatches fail at **runtime**, not
  build time. Add a smoke test in CI (`docker run --rm image -c "import app"`).

---

## Example 28 — Private package index with a build secret

**🧾 What is this?** Companies host internal Python packages on a private index (Azure
Artifacts, JFrog Artifactory, AWS CodeArtifact). Installing needs a **token**. The token
must **not** end up in the image.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app

COPY requirements.txt .
# The secret is mounted as a file ONLY during this RUN; never written to a layer
RUN --mount=type=secret,id=pip_index_url \
    PIP_EXTRA_INDEX_URL="$(cat /run/secrets/pip_index_url)" \
    pip install -r requirements.txt

COPY --chown=1001:1001 . .
USER 1001
CMD ["python", "app.py"]
```

**▶️ Build:**

```bash
# The file contains e.g. https://user:TOKEN@pkgs.dev.azure.com/org/_packaging/feed/pypi/simple/
docker build --secret id=pip_index_url,src=./pip_index_url.txt -t myapp .

# Or from an environment variable (common in CI)
docker build --secret id=pip_index_url,env=PIP_INDEX_URL -t myapp .
```

**🔍 Explained:**

- `--mount=type=secret,id=pip_index_url` — the secret appears at `/run/secrets/pip_index_url`
  only while this command runs.
- `PIP_EXTRA_INDEX_URL="$(cat ...)" pip install` — sets the variable for that one command only.

**⚠️ DevOps Gotchas:**

- ❌ `ARG PIP_TOKEN` + `RUN pip install ... $PIP_TOKEN` → the token is visible in
  `docker history`. This is one of the most common security findings in audits.
- Add `pip_index_url.txt` to `.gitignore` **and** `.dockerignore`.

---

## Example 29 — Entrypoint script pattern

**🧾 What is this?** Sometimes the app needs a few steps at **container start** (wait
for config, run migrations in dev, then start the server). We use a small shell script.

`docker-entrypoint.sh`:

```bash
#!/bin/sh
# Stop on any error
set -e

# Optional: only run migrations when explicitly asked (e.g. in a one-off job)
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Running database migrations..."
  python manage.py migrate --noinput
fi

# Replace this shell with the real command so it becomes PID 1 and gets signals
exec "$@"
```

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=1001:1001 . .
# --chmod sets execute permission during COPY (no extra layer)
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

USER 1001
EXPOSE 8000
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mysite.wsgi:application"]
```

**🔍 Explained:**

- `exec "$@"` — **the most important line.** `"$@"` = "all arguments passed to the script"
  (here: the `CMD`). `exec` *replaces* the shell process with gunicorn, so gunicorn becomes
  PID 1 and receives `SIGTERM`. Without `exec`, the shell stays PID 1 → slow, ugly shutdowns.
- `set -e` — if any command fails, the script stops (instead of starting a broken app).
- `COPY --chmod=755` — makes the script executable.

**⚠️ DevOps Gotchas:**

- **Windows line endings:** if the script was saved on Windows (CRLF), the container fails
  with `exec /usr/local/bin/docker-entrypoint.sh: no such file or directory` — a very
  misleading error. Fix with `.gitattributes`: `*.sh text eol=lf`.
- Running migrations on **every** replica start causes races with 10 replicas. Prefer a
  separate Kubernetes Job / pipeline step with `RUN_MIGRATIONS=true`.

---

## Example 30 — Pre-built wheels multi-stage

**🧾 What is this?** An alternative to copying a venv: build **wheel files** in a stage
with compilers, then install those wheels in a clean stage.

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS builder
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
COPY requirements.txt .
# Build (or download) a wheel for every dependency into /wheels
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app
# Bind-mount the wheels for the install — they never become a layer in this stage
RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl
COPY --chown=1001:1001 . .
USER 1001
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

**🔍 Explained:**

- `pip wheel` — produces `.whl` files instead of installing.
- `--mount=type=bind,from=builder,...` — temporarily mounts the builder's `/wheels` folder.
  A plain `COPY --from` would leave the wheel files in a layer (wasted MBs).
- `--no-index --find-links=/wheels` — "install only from this folder, never the internet".
  Guarantees what you built is what you install.

---

**Next:** [03 — Java & JVM ➡️](03-java-jvm.md)
