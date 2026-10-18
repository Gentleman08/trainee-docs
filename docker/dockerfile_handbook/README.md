# 🐳 Dockerfile Handbook — 115 Examples Across Tech Stacks

> A beginner-friendly guide to writing **production-grade, maintainable Dockerfiles**
> for almost any tech stack. No development background needed: every stack starts with a
> plain-English explanation of what it is, and every example explains each line and ends
> with **DevOps gotchas** from real projects.

[🏠 Back to Docker](../README.md) · [🏠 Back to Home](../../README.md)

---

## 🧭 How to use this handbook

1. **Read [Chapter 00 — Fundamentals](00-fundamentals.md) first.** It explains images,
   layers, caching, every Dockerfile instruction, base-image choices, and has the
   **best-practices checklist** and **master gotcha table**.
2. Then jump to the chapter for the stack you're working with.
3. Each example uses the same layout:

| Section | What you get |
|---------|--------------|
| 🧾 **What is this?** | The technology explained in plain English |
| 📁 **Developer gives you** | The files to expect in the repo |
| 📄 **Dockerfile** | A complete, commented, best-practice Dockerfile |
| 🔍 **Explained** | What each important line does and why |
| ⚠️ **DevOps Gotchas** | Real-world traps, error messages, and fixes |
| ▶️ **Build & run** | Commands to try it (where useful) |

> 📝 Image tags (e.g. `node:22`, `python:3.12`) were current when written. Check Docker Hub
> or the vendor registry for the latest **supported** version before you copy an example.

---

## 📚 Chapters

| # | Chapter | Examples | Stacks covered |
|---|---------|----------|----------------|
| 00 | [Fundamentals](00-fundamentals.md) | 1–5 | Concepts, instructions, layers, cache, base images, `.dockerignore`, multi-stage, checklist |
| 01 | [Node.js / JavaScript / TypeScript](01-nodejs.md) | 6–17 | Express, TypeScript, pnpm, Yarn, Next.js, NestJS, distroless, monorepos, Bun, dev containers |
| 02 | [Python](02-python.md) | 18–30 | Scripts, Flask, Django, FastAPI, Poetry, uv, Celery, Streamlit, distroless, private indexes |
| 03 | [Java & JVM](03-java-jvm.md) | 31–40 | Spring Boot (Maven/Gradle/layered), jlink, Quarkus (JVM & native), Tomcat, Kotlin, distroless |
| 04 | [Go, Rust, C & C++](04-go-rust-c.md) | 41–50 | Go (alpine/scratch/distroless/multi-arch), Rust (cargo-chef/musl), C with make, C++ with CMake |
| 05 | [.NET, PHP, Ruby & Elixir](05-dotnet-php-ruby-elixir.md) | 51–62 | ASP.NET Core, chiseled, Native AOT, Blazor, PHP-Apache, PHP-FPM, Laravel, WordPress, Rails, Sinatra, Phoenix |
| 06 | [Frontend & Static Sites](06-frontend-static.md) | 63–72 | HTML, React, Angular, Vue, SvelteKit, runtime config, Hugo, Docusaurus, Caddy |
| 07 | [Databases, Caches, Queues & Proxies](07-databases-infra.md) | 73–82 | PostgreSQL, MySQL, MongoDB, Redis, RabbitMQ, Elasticsearch, Flyway, nginx, HAProxy, pgvector |
| 08 | [DevOps Tooling, CI/CD & Monitoring](08-devops-tooling.md) | 83–94 | Terraform, Ansible, kubectl/helm, Azure CLI, AWS CLI, Jenkins, Azure DevOps & GitHub agents, Prometheus, Grafana, backups |
| 09 | [Data Science, ML & AI](09-data-ml-ai.md) | 95–103 | Jupyter, PyTorch CPU/GPU, TF Serving, Hugging Face, Ollama, Spark, Airflow, R Shiny |
| 10 | [Advanced Patterns & Hardening](10-advanced-patterns.md) | 104–115 | Build secrets, SSH mounts, cache mounts, targets, test stages, Compose, labels, signals, read-only FS, heredocs, golden images, Windows containers, CI pipelines |

---

## 🔎 Quick lookup — "I need a Dockerfile for…"

| I have… | Go to |
|---------|-------|
| A Node/Express API | [Ex 6](01-nodejs.md#example-6--simple-express-api), [Ex 7](01-nodejs.md#example-7--express-with-tini-and-healthcheck) |
| A TypeScript backend | [Ex 8](01-nodejs.md#example-8--typescript-api-multi-stage), [Ex 13](01-nodejs.md#example-13--nestjs-api) |
| A Next.js site | [Ex 12](01-nodejs.md#example-12--nextjs-standalone) |
| A Flask / Django / FastAPI app | [Ex 19](02-python.md#example-19--flask--gunicorn), [Ex 20](02-python.md#example-20--django--gunicorn--static-files), [Ex 21](02-python.md#example-21--fastapi--uvicorn) |
| A Spring Boot service | [Ex 31](03-java-jvm.md#example-31--spring-boot--maven-multi-stage), [Ex 33](03-java-jvm.md#example-33--spring-boot-layered-jar) |
| A Go microservice | [Ex 43](04-go-rust-c.md#example-43--go--distroless-with-cache-mounts-and-version-stamping) |
| An ASP.NET Core API | [Ex 51](05-dotnet-php-ruby-elixir.md#example-51--aspnet-core-web-api), [Ex 52](05-dotnet-php-ruby-elixir.md#example-52--aspnet-core-on-chiseled-images) |
| A PHP / Laravel app | [Ex 57](05-dotnet-php-ruby-elixir.md#example-57--php-fpm--nginx), [Ex 58](05-dotnet-php-ruby-elixir.md#example-58--laravel) |
| A React / Angular / Vue SPA | [Ex 64](06-frontend-static.md#example-64--react-vite--nginx-unprivileged), [Ex 66](06-frontend-static.md#example-66--angular--nginx), [Ex 69](06-frontend-static.md#example-69--runtime-config-injection) |
| A database for local dev | [Ex 73](07-databases-infra.md#example-73--postgresql-with-init-scripts), [Ex 109](10-advanced-patterns.md#example-109--docker-compose-full-stack) |
| A CI agent image | [Ex 90](08-devops-tooling.md#example-90--azure-devops-self-hosted-agent), [Ex 91](08-devops-tooling.md#example-91--github-actions-self-hosted-runner) |
| An ML model to serve | [Ex 96](09-data-ml-ai.md#example-96--ml-model-api-cpu-only-pytorch), [Ex 97](09-data-ml-ai.md#example-97--gpu-inference-with-cuda) |
| A legacy Windows/.NET Framework app | [Ex 115](10-advanced-patterns.md#example-115--windows-container-iis--net-framework) |

---

## ✅ The 10 commandments (the short version of everything)

1. **Pin your base image** (`python:3.12-slim-bookworm`, not `python:latest`).
2. **Use a `.dockerignore`** — keep out `.git`, `.env`, `node_modules`, build output.
3. **Copy dependency files first, install, then copy source** — cache is everything.
4. **Use multi-stage builds** — build tools stay in the kitchen, not on the plate.
5. **Run as a non-root, numeric `USER`.**
6. **Never put secrets in `ARG`, `ENV`, or copied files** — use `--mount=type=secret` and runtime secrets.
7. **Use exec-form `CMD`/`ENTRYPOINT`** (`["app", "arg"]`) so shutdown signals work.
8. **Listen on `0.0.0.0`** and log to **stdout/stderr**.
9. **Same image everywhere** — configure with environment variables at runtime.
10. **Lint (hadolint) and scan (Trivy/Scout) in CI** — and rebuild regularly for patches.

---

[🏠 Back to Docker](../README.md) · [🏠 Back to Home](../../README.md)
