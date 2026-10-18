# 05 — .NET, PHP, Ruby & Elixir (Examples 51–62)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Go, Rust, C/C++](04-go-rust-c.md)

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 51 | [ASP.NET Core Web API](#example-51--aspnet-core-web-api) | The baseline .NET Dockerfile |
| 52 | [ASP.NET Core on chiseled images](#example-52--aspnet-core-on-chiseled-images) | Hardened .NET |
| 53 | [.NET Worker Service](#example-53--net-worker-service) | Background service, no web |
| 54 | [.NET Native AOT](#example-54--net-native-aot) | Native binary, tiny image |
| 55 | [Blazor WebAssembly → nginx](#example-55--blazor-webassembly--nginx) | .NET frontend as static files |
| 56 | [PHP + Apache](#example-56--php--apache) | Classic PHP site |
| 57 | [PHP-FPM + nginx (two containers)](#example-57--php-fpm--nginx) | Production PHP layout |
| 58 | [Laravel (Composer + Vite assets)](#example-58--laravel) | Modern PHP framework |
| 59 | [WordPress with baked-in plugins/themes](#example-59--wordpress-with-baked-in-pluginsthemes) | CMS |
| 60 | [Ruby on Rails](#example-60--ruby-on-rails) | Full Ruby framework |
| 61 | [Sinatra / Rack (small Ruby service)](#example-61--sinatra--rack) | Lightweight Ruby |
| 62 | [Elixir Phoenix release](#example-62--elixir-phoenix-release) | BEAM / Erlang VM |

---

# Part A — .NET (C#)

## 🧾 What is .NET? (for non-developers)

- **.NET** is Microsoft's platform; **C#** is its main language. **ASP.NET Core** is the
  web framework. Modern .NET (6, 8, 10…) is **cross-platform** and runs great on Linux containers.
- Old **.NET Framework 4.x** is **Windows-only** → needs Windows containers (see Chapter 10).
- The project file is **`*.csproj`**. A **solution** (`*.sln`) groups several projects.
- **`dotnet restore`** downloads dependencies (from **NuGet**). **`dotnet publish`** compiles
  and produces a folder of `.dll` files ready to run.

### Microsoft's official images (from `mcr.microsoft.com`)

| Image | Contains | Use |
|-------|----------|-----|
| `dotnet/sdk:10.0` | Full SDK (~800 MB) | **Build** stage |
| `dotnet/aspnet:10.0` | ASP.NET Core runtime | Runtime for web apps |
| `dotnet/runtime:10.0` | .NET runtime (no ASP.NET) | Runtime for console/worker apps |
| `dotnet/runtime-deps:10.0` | Only OS libs, no .NET | Self-contained / Native AOT apps |
| `...:10.0-noble-chiseled` | Ultra-minimal Ubuntu, no shell, non-root | Hardened production |

> 📝 Use an **LTS** release in production (8.0, 10.0 — even numbers). Check
> [the .NET support policy](https://dotnet.microsoft.com/platform/support/policy) for end dates.

### .NET 8+ container defaults you should know

- Apps listen on port **8080** (not 80) by default — set by `ASPNETCORE_HTTP_PORTS=8080`.
- Images include a non-root user **`app`** with UID **1654**, exposed as env var `$APP_UID`.

### Starter `.dockerignore` for .NET

```gitignore
**/bin/
**/obj/
**/.vs/
**/*.user
**/appsettings.Development.json
.git
.env*
Dockerfile*
.dockerignore
```

> ⚠️ **.NET gotcha:** Local `bin/` and `obj/` folders (from Windows builds) copied into the
> image cause weird restore/build errors. The `**/` prefix excludes them in every subfolder.

---

## Example 51 — ASP.NET Core Web API

**📁 Developer gives you:** `MyApi.sln`, `src/MyApi/MyApi.csproj`, source `.cs` files.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# 1) Copy only project files and restore (cached until dependencies change)
COPY MyApi.sln .
COPY src/MyApi/MyApi.csproj src/MyApi/
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet restore src/MyApi/MyApi.csproj

# 2) Copy everything else and publish
COPY . .
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet publish src/MyApi/MyApi.csproj \
      -c Release \
      -o /app/publish \
      --no-restore \
      /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
# Built-in non-root user (UID 1654)
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApi.dll"]
```

**🔍 Explained:**

- Copying the `.csproj` (dependency list) before source code = the same cache trick as
  `package.json` in Node.
- `-c Release` — optimised build configuration (vs `Debug`).
- `--no-restore` — restore already happened in the cached step.
- `/p:UseAppHost=false` — don't generate a native launcher executable; we run with `dotnet MyApi.dll`.
- `MyApi.dll` — the main output, usually named after the project.

**⚠️ DevOps Gotchas:**

- Projects referencing **other projects** (`<ProjectReference>`) need **all** those
  `.csproj` files copied before restore, preserving folder structure.
- Private NuGet feeds (Azure Artifacts) need a `nuget.config` and a token → use a
  **build secret** (see Chapter 10, Example 104), never commit the token.
- `appsettings.Development.json` is for local dev — make sure the runtime sets
  `ASPNETCORE_ENVIRONMENT=Production` (it's the default when unset).

---

## Example 52 — ASP.NET Core on chiseled images

**🧾 What is this?** **Chiseled** images are Ubuntu images with everything removed except
what .NET needs: **no shell, no package manager, non-root by default**. ~100 MB, very few CVEs.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY src/MyApi/MyApi.csproj src/MyApi/
RUN dotnet restore src/MyApi/MyApi.csproj
COPY . .
RUN dotnet publish src/MyApi/MyApi.csproj -c Release -o /app/publish --no-restore /p:UseAppHost=false

# "-extra" variant includes ICU (culture/globalization) and tzdata (time zones)
FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble-chiseled-extra AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApi.dll"]
```

**🔍 Explained:**

- No `USER` line needed — chiseled images already run as the non-root `app` user.
- Plain `-chiseled` lacks ICU and time-zone data. If the app formats dates/currency for
  different cultures or converts time zones, use `-chiseled-extra` (or set
  `InvariantGlobalization=true` in the csproj if the app doesn't need cultures).

**⚠️ DevOps Gotchas:**

- No shell → `HEALTHCHECK CMD curl ...` impossible. Use Kubernetes probes against
  ASP.NET Core health checks (`app.MapHealthChecks("/healthz")`).
- Missing ICU error looks like:
  `Couldn't find a valid ICU package installed on the system` → switch to `-extra`.

---

## Example 53 — .NET Worker Service

**🧾 What is this?** A long-running background process with no web server (e.g. reads
messages from Azure Service Bus and processes them). Uses the plain **runtime** image.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY src/OrderWorker/OrderWorker.csproj src/OrderWorker/
RUN dotnet restore src/OrderWorker/OrderWorker.csproj
COPY . .
RUN dotnet publish src/OrderWorker/OrderWorker.csproj -c Release -o /app/publish --no-restore /p:UseAppHost=false

# runtime (not aspnet) — no web framework needed
FROM mcr.microsoft.com/dotnet/runtime:10.0-noble-chiseled AS runtime
WORKDIR /app
COPY --from=build /app/publish .
ENV DOTNET_ENVIRONMENT=Production
ENTRYPOINT ["dotnet", "OrderWorker.dll"]
```

**🔍 Explained:**

- `dotnet/runtime` is smaller than `dotnet/aspnet` because it lacks ASP.NET Core.
- `DOTNET_ENVIRONMENT` — the environment name for non-web .NET hosts
  (`ASPNETCORE_ENVIRONMENT` is for web apps).
- No `EXPOSE` — it doesn't listen for traffic.

**⚠️ DevOps Gotchas:**

- On `SIGTERM`, .NET's host waits **30 s** (default `ShutdownTimeout`) for workers to stop.
  Docker's default stop timeout is **10 s** → work gets killed mid-message. Align the
  timeouts (`docker stop -t 45`, Kubernetes `terminationGracePeriodSeconds: 45`).

---

## Example 54 — .NET Native AOT

**🧾 What is this?** **Native AOT** (Ahead-Of-Time) compiles .NET into a native binary —
no .NET runtime needed at all. Very fast startup, small images (~20–40 MB). The dev must
enable `<PublishAot>true</PublishAot>` and the app must be AOT-compatible.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
# The native toolchain (clang + linker libs) is needed for AOT compilation
RUN apt-get update \
 && apt-get install -y --no-install-recommends clang zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY src/MyApi/MyApi.csproj src/MyApi/
RUN dotnet restore src/MyApi/MyApi.csproj -r linux-x64
COPY . .
RUN dotnet publish src/MyApi/MyApi.csproj -c Release -r linux-x64 -o /app/publish --no-restore

# runtime-deps = just the OS libraries; no .NET inside
FROM mcr.microsoft.com/dotnet/runtime-deps:10.0-noble-chiseled AS runtime
WORKDIR /app
COPY --from=build /app/publish/MyApi .
EXPOSE 8080
ENTRYPOINT ["./MyApi"]
```

**🔍 Explained:**

- `-r linux-x64` — "runtime identifier": compile for Linux on x64 CPUs.
- Output is a single native executable `MyApi` (no `.dll`).
- `runtime-deps` — contains only the system libraries a native .NET app needs.

**⚠️ DevOps Gotchas:**

- AOT builds for **arm64** need `-r linux-arm64` and an arm64 toolchain — cross-compiling
  AOT is limited. Easiest: build on an arm64 agent, or use Microsoft's `-aot` SDK image tags.
- Libraries using reflection heavily (some ORMs, serializers) may not work. This is a
  developer decision, not a DevOps flag to flip.

---

## Example 55 — Blazor WebAssembly → nginx

**🧾 What is this?** **Blazor WebAssembly** runs C# **in the browser**. After publishing,
it's just **static files** (HTML, JS, `.wasm`, `.dll`) — served by any web server.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY src/WebClient/WebClient.csproj src/WebClient/
RUN dotnet restore src/WebClient/WebClient.csproj
COPY . .
RUN dotnet publish src/WebClient/WebClient.csproj -c Release -o /app/publish --no-restore

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/publish/wwwroot /usr/share/nginx/html
EXPOSE 8080
```

`nginx.conf`:

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;

    location / {
        # Single-page app: unknown paths fall back to index.html
        try_files $uri $uri/ /index.html;
    }
}
```

**🔍 Explained:**

- The publish output has a `wwwroot/` folder — that's all the browser needs.
- `nginx-unprivileged` — nginx variant that runs as non-root on port 8080 (see Chapter 6).
- `try_files ... /index.html` — lets in-app routes like `/orders/42` work on page refresh.

**⚠️ DevOps Gotchas:**

- Very old nginx versions lacked the `application/wasm` MIME type → browser refuses to load
  `.wasm`. Current official images include it.

---

# Part B — PHP

## 🧾 What is PHP? (for non-developers)

- **PHP** is an interpreted language powering a huge part of the web (WordPress, Laravel,
  Drupal, Magento).
- PHP code is executed by a web server in one of two ways:
  - **mod_php** — PHP runs *inside* Apache. Simple, one container. (`php:8.3-apache`)
  - **PHP-FPM** — a separate PHP process pool; a web server (nginx) forwards requests to it
    over the **FastCGI** protocol on port **9000**. More scalable. (`php:8.3-fpm`)
- **Composer** is PHP's package manager (`composer.json` / `composer.lock`), installing into `vendor/`.
- **PHP extensions** (`pdo_mysql`, `gd`, `intl`, `opcache`) add features. Official images
  provide helper scripts: `docker-php-ext-install`, `docker-php-ext-configure`, `docker-php-ext-enable`.
- **OPcache** caches compiled PHP in memory — **always enable it in production** (big speed-up).

### Starter `.dockerignore` for PHP

```gitignore
vendor/
node_modules/
storage/logs/*
storage/framework/cache/*
.env*
.git
tests/
Dockerfile*
.dockerignore
```

---

## Example 56 — PHP + Apache

```dockerfile
# syntax=docker/dockerfile:1
FROM php:8.3-apache

# Install system libraries + compile PHP extensions in one layer
RUN apt-get update \
 && apt-get install -y --no-install-recommends libzip-dev libicu-dev \
 && docker-php-ext-install pdo_mysql zip intl opcache \
 && rm -rf /var/lib/apt/lists/*

# Use the production php.ini shipped with the image
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# Run Apache on 8080 so it doesn't need root to bind port 80
RUN sed -i 's/Listen 80/Listen 8080/' /etc/apache2/ports.conf \
 && sed -i 's/:80>/:8080>/' /etc/apache2/sites-available/000-default.conf \
 && a2enmod rewrite

# Composer: grab the binary from the official composer image
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist --no-interaction

COPY --chown=www-data:www-data . .
RUN composer dump-autoload --optimize --no-dev

USER www-data
EXPOSE 8080
# Default CMD from the base image is apache2-foreground — keep it
```

**🔍 Explained:**

- `docker-php-ext-install pdo_mysql zip intl opcache` — compiles and enables extensions.
  The `-dev` libraries (`libzip-dev`, `libicu-dev`) are needed to compile `zip` and `intl`.
- `php.ini-production` — safer defaults (errors hidden from users, logged instead).
- `sed` lines — change Apache's port from 80 to 8080. Ports below 1024 need root.
- `a2enmod rewrite` — enables URL rewriting (most PHP frameworks need it for pretty URLs).
- `composer install --no-dev --no-scripts --no-autoloader` — install dependencies only,
  without the project code (cache layer). Then `dump-autoload --optimize` after code is copied.
- `www-data` — the standard Debian web-server user, already present in the image.

**⚠️ DevOps Gotchas:**

- The `-dev` packages stay in this image (single stage). For leaner images, see Example 58's
  multi-stage approach, or remove them after compiling.
- `docker-php-ext-install` compiles C code → slow (minutes). The community tool
  `mlocati/php-extension-installer` (`install-php-extensions gd intl ...`) is faster and
  handles dependencies automatically.

---

## Example 57 — PHP-FPM + nginx

**🧾 What is this?** The production PHP setup: **two containers** — nginx (serves static
files, forwards `.php` requests) and PHP-FPM (runs PHP).

```
Browser ──► nginx :8080 ──(static files: served directly)
                │
                └──(.php requests, FastCGI)──► php-fpm :9000 ──► your PHP code
```

`Dockerfile` (PHP-FPM):

```dockerfile
# syntax=docker/dockerfile:1
FROM php:8.3-fpm-alpine AS base
# install-php-extensions: fast helper that installs build deps, compiles, and cleans up
COPY --from=mlocati/php-extension-installer:2 /usr/bin/install-php-extensions /usr/local/bin/
RUN install-php-extensions pdo_pgsql intl opcache
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

FROM composer:2 AS vendor
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --prefer-dist --no-interaction --optimize-autoloader --ignore-platform-reqs

FROM base AS runtime
WORKDIR /var/www/html
COPY --from=vendor --chown=www-data:www-data /app/vendor ./vendor
COPY --chown=www-data:www-data . .
USER www-data
EXPOSE 9000
CMD ["php-fpm"]
```

`nginx.Dockerfile`:

```dockerfile
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
# nginx needs the static files (CSS/JS/images) too!
COPY public /var/www/html/public
```

`docker/nginx.conf`:

```nginx
server {
    listen 8080;
    root /var/www/html/public;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass app:9000;                 # "app" = the php-fpm service name
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }
}
```

**🔍 Explained:**

- `composer:2` as a full **stage** — install dependencies with Composer, copy only `vendor/` out.
- `--ignore-platform-reqs` — the composer image lacks our PHP extensions; skip that check
  (they exist in the runtime stage). Use carefully.
- `fastcgi_pass app:9000` — nginx forwards PHP requests to the container named `app`.
- `SCRIPT_FILENAME` — tells PHP-FPM which file to execute. The path must exist **inside the
  PHP container**, which is why both containers use `/var/www/html`.

**⚠️ DevOps Gotchas:**

- **nginx can't see files inside the PHP container.** Static assets must be copied into the
  nginx image too (or shared via a volume). Classic symptom: PHP pages work, CSS/images 404.
- PHP-FPM's `pm.max_children` (number of PHP workers) defaults to **5** → under load,
  requests queue and time out. Tune it in a `zz-custom.conf` pool file based on memory.

---

## Example 58 — Laravel

**🧾 What is this?** **Laravel** is the most popular modern PHP framework. It usually has
**frontend assets** built with **Vite** (a Node.js tool) → we need a Node stage too.

```dockerfile
# syntax=docker/dockerfile:1

#### PHP dependencies ####
FROM composer:2 AS vendor
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist --no-interaction --ignore-platform-reqs
COPY . .
RUN composer dump-autoload --optimize --classmap-authoritative --no-dev

#### Frontend assets (CSS/JS) ####
FROM node:22-alpine AS assets
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY vite.config.* ./
COPY resources ./resources
COPY public ./public
RUN npm run build            # outputs to public/build

#### Runtime ####
FROM php:8.3-fpm-alpine AS runtime
COPY --from=mlocati/php-extension-installer:2 /usr/bin/install-php-extensions /usr/local/bin/
RUN install-php-extensions pdo_mysql bcmath intl opcache redis pcntl \
 && mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

WORKDIR /var/www/html
COPY --chown=www-data:www-data . .
COPY --from=vendor --chown=www-data:www-data /app/vendor        ./vendor
COPY --from=assets --chown=www-data:www-data /app/public/build  ./public/build

USER www-data
EXPOSE 9000
CMD ["php-fpm"]
```

**🔍 Explained:**

- Three independent build stages (BuildKit runs them in parallel): Composer, Node, PHP.
- `--classmap-authoritative` — fastest autoloader mode for production.
- `public/build` — where Vite writes compiled CSS/JS.
- Same image can run Laravel's queue worker: `command: ["php", "artisan", "queue:work"]`.

**⚠️ DevOps Gotchas:**

- **Don't run `php artisan config:cache` at build time** — it freezes the build
  environment's `.env` values into the image. Run it at container **start** (entrypoint
  script) so it picks up runtime env vars.
- `storage/` and `bootstrap/cache/` must be **writable** by `www-data`.
- Laravel's `APP_KEY` is a secret — inject at runtime, never bake in.

---

## Example 59 — WordPress with baked-in plugins/themes

**🧾 What is this?** **WordPress** is the world's most popular CMS (website builder). The
official image contains WordPress itself; we add our **custom theme and plugins** so every
environment is identical.

```dockerfile
# syntax=docker/dockerfile:1
FROM wordpress:6.6-php8.3-apache

# Production PHP settings + larger upload limit
RUN mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini" \
 && { \
      echo 'upload_max_filesize = 64M'; \
      echo 'post_max_size = 64M'; \
      echo 'memory_limit = 256M'; \
    } > "$PHP_INI_DIR/conf.d/uploads.ini"

# Custom theme and plugins committed to the repo
COPY --chown=www-data:www-data wp-content/themes/acme-theme   /usr/src/wordpress/wp-content/themes/acme-theme
COPY --chown=www-data:www-data wp-content/plugins/acme-plugin /usr/src/wordpress/wp-content/plugins/acme-plugin
```

**🔍 Explained:**

- The official image keeps WordPress in `/usr/src/wordpress` and copies it into
  `/var/www/html` on **first start** (if empty). That's why we add our files to
  `/usr/src/wordpress`.
- `{ echo ...; echo ...; } > file` — shell trick to write several lines to a file in one RUN.
- Database settings come from env vars at runtime: `WORDPRESS_DB_HOST`, `WORDPRESS_DB_USER`,
  `WORDPRESS_DB_PASSWORD`, `WORDPRESS_DB_NAME`.

**⚠️ DevOps Gotchas:**

- **Uploads** (`wp-content/uploads`) are user data → must be on a **persistent volume** or
  object storage plugin (Azure Blob / S3). Otherwise images vanish on redeploy.
- If `/var/www/html` is already a persistent volume from an older deploy, the entrypoint
  **won't** overwrite it — your new theme won't appear. Mount only `wp-content/uploads` instead.
- WordPress auto-updates and plugin installs via the admin UI modify files inside the
  container → lost on restart. Disable them (`DISALLOW_FILE_MODS`) and update via the image.

---

# Part C — Ruby

## 🧾 What is Ruby? (for non-developers)

- **Ruby** is an interpreted language. **Ruby on Rails** is its famous web framework
  (GitHub, Shopify, Basecamp were built with it).
- **Bundler** manages dependencies ("gems"): `Gemfile` + `Gemfile.lock`, command `bundle install`.
- Production web server: **Puma**.

---

## Example 60 — Ruby on Rails

```dockerfile
# syntax=docker/dockerfile:1
ARG RUBY_VERSION=3.3

FROM ruby:${RUBY_VERSION}-slim-bookworm AS base
WORKDIR /rails
ENV RAILS_ENV=production \
    BUNDLE_DEPLOYMENT=1 \
    BUNDLE_PATH=/usr/local/bundle \
    BUNDLE_WITHOUT="development:test"
# Runtime libraries only
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl libjemalloc2 libpq5 \
 && rm -rf /var/lib/apt/lists/*

FROM base AS build
# Compilers + headers to build native gems (pg, nokogiri…)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git libpq-dev libyaml-dev pkg-config \
 && rm -rf /var/lib/apt/lists/*
COPY Gemfile Gemfile.lock ./
RUN bundle install \
 && rm -rf ~/.bundle "${BUNDLE_PATH}"/ruby/*/cache
COPY . .
# Precompile boot cache and assets; a dummy secret is enough for asset compilation
RUN bundle exec bootsnap precompile app/ lib/ \
 && SECRET_KEY_BASE_DUMMY=1 ./bin/rails assets:precompile

FROM base AS runtime
COPY --from=build "${BUNDLE_PATH}" "${BUNDLE_PATH}"
COPY --from=build /rails /rails
RUN groupadd --system --gid 1000 rails \
 && useradd rails --uid 1000 --gid 1000 --create-home --shell /bin/bash \
 && chown -R rails:rails db log storage tmp
USER 1000:1000
# jemalloc reduces Ruby memory fragmentation
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libjemalloc.so.2
EXPOSE 3000
CMD ["./bin/rails", "server", "-b", "0.0.0.0"]
```

**🔍 Explained:**

- `BUNDLE_DEPLOYMENT=1` — strict mode: uses `Gemfile.lock` exactly (like `npm ci`).
- `BUNDLE_WITHOUT="development:test"` — skip dev/test gems.
- `bootsnap precompile` — caches Ruby file loading → faster boot.
- `SECRET_KEY_BASE_DUMMY=1` — lets asset compilation run without the real secret.
- `chown -R rails:rails db log storage tmp` — only folders Rails writes to are owned by the
  app user; code stays read-only.

**⚠️ DevOps Gotchas:**

- **Rails 7.1+ generates a production Dockerfile** (`rails new` creates one). Start from
  it rather than writing from scratch — this example is modelled on it.
- The `LD_PRELOAD` path is **amd64-specific**. On arm64 it's
  `/usr/lib/aarch64-linux-gnu/libjemalloc.so.2` — a wrong path prints a warning on every
  command. For multi-arch, set it via an entrypoint script or a symlink.
- `RAILS_MASTER_KEY` (decrypts credentials) is a runtime secret.

---

## Example 61 — Sinatra / Rack

**🧾 What is this?** **Sinatra** is a tiny Ruby web framework (Ruby's "Flask"). Runs with
Puma via a `config.ru` file.

```dockerfile
# syntax=docker/dockerfile:1
FROM ruby:3.3-alpine AS build
RUN apk add --no-cache build-base
WORKDIR /app
ENV BUNDLE_DEPLOYMENT=1 BUNDLE_WITHOUT="development:test"
COPY Gemfile Gemfile.lock ./
RUN bundle install --jobs 4

FROM ruby:3.3-alpine
WORKDIR /app
ENV BUNDLE_DEPLOYMENT=1 BUNDLE_WITHOUT="development:test" RACK_ENV=production
COPY --from=build /usr/local/bundle /usr/local/bundle
RUN adduser -D -u 1001 app
COPY --chown=1001 . .
USER 1001
EXPOSE 9292
CMD ["bundle", "exec", "puma", "-b", "tcp://0.0.0.0:9292", "config.ru"]
```

**🔍 Explained:**

- `build-base` — Alpine's compiler bundle (only in the build stage).
- `/usr/local/bundle` — where gems are installed in official Ruby images; copied to runtime.
- `RACK_ENV=production` — Rack/Sinatra's production switch.

**⚠️ DevOps Gotchas:**

- Gems with native extensions compiled on Alpine (musl) must run on Alpine — don't mix
  Alpine build with Debian runtime.

---

# Part D — Elixir

## 🧾 What is Elixir? (for non-developers)

- **Elixir** runs on the **Erlang VM (BEAM)** — famous for massive concurrency and
  fault-tolerance (WhatsApp, Discord). **Phoenix** is its web framework.
- `mix` is the build tool. **`mix release`** produces a self-contained folder with the app
  **and** the Erlang runtime — so the final image doesn't need Elixir installed.

---

## Example 62 — Elixir Phoenix release

```dockerfile
# syntax=docker/dockerfile:1
FROM elixir:1.17-slim AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV MIX_ENV=prod
RUN mix local.hex --force && mix local.rebar --force

COPY mix.exs mix.lock ./
RUN mix deps.get --only prod
COPY config/config.exs config/prod.exs config/
RUN mix deps.compile

COPY priv priv
COPY lib lib
COPY assets assets
RUN mix assets.deploy && mix compile

COPY config/runtime.exs config/
COPY rel rel
RUN mix release

FROM debian:bookworm-slim AS runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends libstdc++6 openssl libncurses6 locales ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && sed -i '/en_US.UTF-8/s/^# //' /etc/locale.gen && locale-gen
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 MIX_ENV=prod
WORKDIR /app
RUN useradd --system --uid 1001 --no-create-home app
COPY --from=build --chown=1001:1001 /app/_build/prod/rel/my_app ./
USER 1001
EXPOSE 4000
# bin/server is generated by "mix phx.gen.release"
CMD ["/app/bin/server"]
```

**🔍 Explained:**

- `mix local.hex/rebar --force` — install Elixir/Erlang package tools non-interactively.
- `config/runtime.exs` is copied **late** — it's read at **runtime** (env vars), so
  changes to it don't need a full recompile.
- `mix assets.deploy` — builds and fingerprints CSS/JS.
- `mix release` → `_build/prod/rel/my_app/` contains the app + Erlang runtime.
- Runtime image is plain Debian + a few C libraries the BEAM needs + UTF-8 locale.

**⚠️ DevOps Gotchas:**

- The Erlang version in the build image must match the runtime OS (same Debian release),
  because the release includes compiled native code.
- Phoenix needs `SECRET_KEY_BASE`, `DATABASE_URL` and `PHX_HOST` at runtime.
- **Clustering** (BEAM nodes talking to each other) needs extra ports and DNS-based
  discovery (`libcluster`) — design this with the team for Kubernetes.

---

**Next:** [06 — Frontend & Static Sites ➡️](06-frontend-static.md)
