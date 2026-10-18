# 07 — Databases, Caches, Queues & Proxies (Examples 73–82)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Frontend & Static](06-frontend-static.md)

---

## 🧾 What's different about these images? (for non-developers)

Until now we containerised **our own code**. This chapter is about **off-the-shelf
infrastructure software** — databases, caches, message queues, proxies. You rarely write
these from scratch; you **extend the official image** by adding:

- configuration files,
- initialisation scripts (create users/tables on first start),
- plugins/extensions.

| Software | What it does (plain English) | Default port |
|----------|------------------------------|--------------|
| **PostgreSQL** | Relational database — stores data in tables (like Excel sheets with rules) | 5432 |
| **MySQL / MariaDB** | Relational database (very common with PHP/WordPress) | 3306 |
| **MongoDB** | Document database — stores JSON-like documents | 27017 |
| **Redis** / **Valkey** | In-memory key/value store — caching, sessions, queues | 6379 |
| **RabbitMQ** | Message broker — apps send each other messages via queues | 5672 (15672 UI) |
| **Elasticsearch / OpenSearch** | Search engine & log storage | 9200 |
| **nginx / HAProxy** | Reverse proxy / load balancer — sits in front of apps | 80/443 |

### ⚠️ Should you run databases in containers at all?

| Environment | Recommendation |
|-------------|----------------|
| Local dev, CI tests | ✅ **Yes** — perfect use case (fresh DB in seconds) |
| Production | ⚠️ Prefer **managed services** (Azure Database for PostgreSQL, AWS RDS, Azure Cache for Redis). Backups, HA, patching, failover handled for you. |
| Production in Kubernetes | Possible with **operators** (CloudNativePG, Strimzi, etc.) and persistent volumes — requires real expertise. |

### Golden rules for stateful containers

1. **Data must live on a volume** (`-v pgdata:/var/lib/postgresql/data`). Without it, deleting
   the container deletes the database.
2. **Passwords come from runtime env vars or secret files** — never baked into the image.
3. **Pin major versions.** A DB image jumping from Postgres 16 → 17 **cannot read the old data
   files** — the container crash-loops. Major upgrades need `pg_upgrade` / dump & restore.

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 73 | [PostgreSQL with init scripts](#example-73--postgresql-with-init-scripts) | `/docker-entrypoint-initdb.d` |
| 74 | [MySQL with custom config](#example-74--mysql-with-custom-config) | `conf.d` overrides |
| 75 | [MongoDB with init script](#example-75--mongodb-with-init-script) | JS init |
| 76 | [Redis with config file](#example-76--redis-with-config-file) | Persistence & memory policy |
| 77 | [RabbitMQ with plugins + definitions](#example-77--rabbitmq-with-plugins-and-definitions) | Pre-created queues |
| 78 | [Elasticsearch with plugins](#example-78--elasticsearch-with-plugins) | Plugin install |
| 79 | [Database migrations image (Flyway)](#example-79--database-migrations-image-flyway) | Schema changes as a job |
| 80 | [nginx reverse proxy / load balancer](#example-80--nginx-reverse-proxy) | Upstreams |
| 81 | [HAProxy load balancer](#example-81--haproxy-load-balancer) | Validated config |
| 82 | [PostgreSQL + compiled extension (pgvector)](#example-82--postgresql-with-a-compiled-extension) | Multi-stage on an infra image |

---

## Example 73 — PostgreSQL with init scripts

**🧾 What is this?** A Postgres image that, **on first start**, creates the app's database
schema and a read-only user.

`init/01-schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS customers (
    id         SERIAL PRIMARY KEY,
    email      TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

`init/02-readonly-user.sh`:

```bash
#!/bin/bash
set -euo pipefail
# READONLY_PASSWORD comes from a runtime environment variable
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE ROLE reporting LOGIN PASSWORD '${READONLY_PASSWORD}';
  GRANT CONNECT ON DATABASE "${POSTGRES_DB}" TO reporting;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO reporting;
EOSQL
```

`Dockerfile`:

```dockerfile
FROM postgres:16-bookworm

# Scripts here run in alphabetical order, ONLY when the data directory is empty
COPY --chmod=755 init/ /docker-entrypoint-initdb.d/

# Health check using Postgres's own readiness tool
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
```

**▶️ Run:**

```bash
docker run -d --name db \
  -e POSTGRES_USER=app -e POSTGRES_PASSWORD=changeme -e POSTGRES_DB=shop \
  -e READONLY_PASSWORD=alsochangeme \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 mydb:16
```

**🔍 Explained:**

- `/docker-entrypoint-initdb.d/` — the official image's hook: `.sql`, `.sql.gz` and `.sh`
  files run on **first initialisation**.
- `POSTGRES_USER/PASSWORD/DB` — read by the entrypoint to create the superuser and database.
- `pg_isready` — returns success only when Postgres accepts connections (not just "process
  running").
- No `USER` line: the image's entrypoint starts as root, fixes data-folder permissions,
  then **drops to the `postgres` user** itself.

**⚠️ DevOps Gotchas:**

- **Init scripts run ONLY when the volume is empty.** Changing `01-schema.sql` and
  redeploying does **nothing** if the volume already has data. Schema changes belong in a
  migration tool (Example 79). This confuses almost everyone once.
- If an init script fails halfway, the data folder is left partially initialised → next
  start skips init. Delete the volume and retry (in dev only!).
- `POSTGRES_PASSWORD_FILE=/run/secrets/pg_pw` reads the password from a file (Docker/K8s
  secrets) — better than a plain env var.

---

## Example 74 — MySQL with custom config

`conf/my-custom.cnf`:

```ini
[mysqld]
character-set-server = utf8mb4
collation-server     = utf8mb4_0900_ai_ci
max_connections      = 300
innodb_buffer_pool_size = 512M
slow_query_log       = 1
long_query_time      = 1
```

`Dockerfile`:

```dockerfile
FROM mysql:8.4

# Files in conf.d are loaded after the main my.cnf (overrides)
COPY conf/my-custom.cnf /etc/mysql/conf.d/my-custom.cnf
COPY init/ /docker-entrypoint-initdb.d/

HEALTHCHECK --interval=10s --timeout=5s --retries=10 \
  CMD mysqladmin ping -h 127.0.0.1 --silent || exit 1
```

**🔍 Explained:**

- `utf8mb4` — full Unicode (including emoji 😀). Old `utf8` in MySQL is a broken 3-byte subset.
- `innodb_buffer_pool_size` — the main memory cache; typically 50–70% of the container's memory limit.
- `mysqladmin ping` — health probe.
- Runtime env vars: `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`.

**⚠️ DevOps Gotchas:**

- MySQL **ignores config files that are world-writable** (`Warning: World-writable config
  file ... is ignored`). Files copied from Windows sometimes get `777`. Use `COPY --chmod=644`.
- `mysql:8.4` is the LTS line; `mysql:latest` follows "innovation" releases — don't use it in prod.

---

## Example 75 — MongoDB with init script

`init/01-create-user.js`:

```javascript
// Runs with the root user against MONGO_INITDB_DATABASE on first start
db = db.getSiblingDB('shop');
db.createUser({
  user: 'shop_app',
  pwd: process.env.SHOP_APP_PASSWORD,
  roles: [{ role: 'readWrite', db: 'shop' }]
});
db.createCollection('orders');
db.orders.createIndex({ customerId: 1, createdAt: -1 });
```

`Dockerfile`:

```dockerfile
FROM mongo:7.0
COPY init/ /docker-entrypoint-initdb.d/
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD mongosh --quiet --eval "db.adminCommand('ping').ok" | grep -q 1 || exit 1
```

**🔍 Explained:**

- Same init-folder convention as Postgres/MySQL; supports `.js` and `.sh`.
- `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` — runtime vars creating the admin.
- `createIndex` — indexes make queries fast; creating them at init is a common pattern.

**⚠️ DevOps Gotchas:**

- Without `MONGO_INITDB_ROOT_*` set, MongoDB starts **without authentication** — anyone who
  can reach port 27017 has full access. Thousands of databases have been ransomed this way.
- MongoDB 5.0+ requires a CPU with **AVX** instructions. Some older hypervisors/CPU
  settings don't expose AVX → container crashes immediately with "Illegal instruction".

---

## Example 76 — Redis with config file

`redis.conf`:

```conf
# Listen on all interfaces inside the container
bind 0.0.0.0
protected-mode yes
port 6379

# Memory: cap usage and evict least-recently-used keys (cache behaviour)
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence: append-only file (survives restarts)
appendonly yes
appendfsync everysec
dir /data
```

`Dockerfile`:

```dockerfile
FROM redis:7.4-alpine
COPY --chown=redis:redis redis.conf /usr/local/etc/redis/redis.conf
HEALTHCHECK --interval=10s --timeout=3s CMD redis-cli ping | grep -q PONG || exit 1
# Password is passed at runtime so it's not in the image
CMD ["sh", "-c", "exec redis-server /usr/local/etc/redis/redis.conf --requirepass \"$REDIS_PASSWORD\""]
```

**🔍 Explained:**

- `maxmemory` + `allkeys-lru` — when full, Redis evicts least-recently-used keys instead of
  crashing/erroring. Right for a **cache**; wrong for a **queue** (you'd lose jobs) → use
  `noeviction` there.
- `appendonly yes` — write every change to a log file in `/data` (mount a volume).
- `sh -c "exec redis-server ..."` — we need a shell to expand `$REDIS_PASSWORD`, and `exec`
  replaces the shell so redis-server is PID 1 (gets signals).

**⚠️ DevOps Gotchas:**

- `maxmemory` must be **below** the container memory limit (leave ~25% headroom for
  fragmentation and forks during persistence), or the kernel OOM-kills Redis.
- **Licensing:** Redis changed its license in 2024 (7.4+ is not OSI open-source; Redis 8
  added AGPL as an option). Many orgs moved to **Valkey** (`valkey/valkey:8-alpine`), a
  drop-in fork. Check your company policy.
- The healthcheck with `--requirepass` needs `redis-cli -a "$REDIS_PASSWORD" ping`.

---

## Example 77 — RabbitMQ with plugins and definitions

**🧾 What is this?** Pre-load RabbitMQ with plugins and a set of exchanges/queues
("definitions") so every environment starts with the same topology.

`enabled_plugins`:

```erlang
[rabbitmq_management,rabbitmq_prometheus,rabbitmq_shovel].
```

`rabbitmq.conf`:

```ini
load_definitions = /etc/rabbitmq/definitions.json
management.load_definitions = /etc/rabbitmq/definitions.json
vm_memory_high_watermark.relative = 0.6
```

`definitions.json` (topology only — no users/passwords):

```json
{
  "vhosts": [{ "name": "/" }],
  "exchanges": [
    { "name": "orders", "vhost": "/", "type": "topic", "durable": true, "auto_delete": false }
  ],
  "queues": [
    { "name": "orders.created", "vhost": "/", "durable": true, "auto_delete": false,
      "arguments": { "x-queue-type": "quorum" } }
  ],
  "bindings": [
    { "source": "orders", "vhost": "/", "destination": "orders.created",
      "destination_type": "queue", "routing_key": "order.created" }
  ]
}
```

`Dockerfile`:

```dockerfile
FROM rabbitmq:3.13-management-alpine
COPY --chown=rabbitmq:rabbitmq enabled_plugins  /etc/rabbitmq/enabled_plugins
COPY --chown=rabbitmq:rabbitmq rabbitmq.conf    /etc/rabbitmq/conf.d/20-custom.conf
COPY --chown=rabbitmq:rabbitmq definitions.json /etc/rabbitmq/definitions.json
EXPOSE 5672 15672 15692
HEALTHCHECK --interval=30s --timeout=10s --retries=5 \
  CMD rabbitmq-diagnostics -q ping || exit 1
```

**🔍 Explained:**

- `-management` tag — includes the web UI on port 15672.
- `enabled_plugins` — Erlang list syntax; note the trailing **dot**.
- `rabbitmq_prometheus` — exposes metrics on 15692 for Prometheus.
- `quorum` queues — replicated, safe queues (recommended over classic mirrored queues).

**⚠️ DevOps Gotchas:**

- If `definitions.json` contains **no users**, and you load definitions, the default
  `guest` user may not be created. Create users via `RABBITMQ_DEFAULT_USER/PASS` env vars or
  a secret-mounted definitions file.
- RabbitMQ's node name depends on the **hostname**. If the hostname changes on restart
  (plain containers do by default), the node can't find its old data. Set `hostname:` in
  Compose or use a StatefulSet in Kubernetes.

---

## Example 78 — Elasticsearch with plugins

```dockerfile
FROM docker.elastic.co/elasticsearch/elasticsearch:8.15.3

# --batch: don't ask for confirmation of extra permissions
RUN bin/elasticsearch-plugin install --batch analysis-icu analysis-phonetic

COPY --chown=elasticsearch:root config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
```

`config/elasticsearch.yml` (single-node dev example):

```yaml
cluster.name: "dev-cluster"
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: true
```

**🔍 Explained:**

- Elastic publishes its own registry (`docker.elastic.co`).
- `elasticsearch-plugin install` — plugins are version-locked to the ES version (another reason to pin tags).
- `discovery.type: single-node` — don't look for other cluster members (dev/test only).

**⚠️ DevOps Gotchas:**

- **`vm.max_map_count`** — Elasticsearch needs the **host** kernel setting
  `vm.max_map_count=262144`. It can't be set from the Dockerfile. Symptom: container exits
  with `max virtual memory areas vm.max_map_count [65530] is too low`. Fix on the host:
  `sysctl -w vm.max_map_count=262144` (on Docker Desktop/WSL: inside the WSL VM).
- Heap: set `ES_JAVA_OPTS="-Xms1g -Xmx1g"` (same min/max), and give the container ~2× that memory.
- **OpenSearch** (`opensearchproject/opensearch`) is the open-source fork — same ideas, its
  plugin tool is `bin/opensearch-plugin`.

---

## Example 79 — Database migrations image (Flyway)

**🧾 What is this?** **Migrations** are versioned SQL scripts (`V1__create_customers.sql`,
`V2__add_phone_column.sql`) that evolve the database schema safely. **Flyway** applies the
ones not yet applied and records them in a history table. We package them as an image and
run it as a **one-off job** before deploying the new app version.

`sql/V1__create_customers.sql`, `sql/V2__add_phone.sql`, …

```dockerfile
FROM flyway/flyway:10-alpine
COPY sql/ /flyway/sql/
# Connection details come from env vars at runtime:
#   FLYWAY_URL=jdbc:postgresql://db:5432/shop  FLYWAY_USER=...  FLYWAY_PASSWORD=...
ENV FLYWAY_CONNECT_RETRIES=10 \
    FLYWAY_VALIDATE_MIGRATION_NAMING=true
CMD ["migrate"]
```

**▶️ Run (e.g. as a pipeline step or Kubernetes Job):**

```bash
docker run --rm \
  -e FLYWAY_URL=jdbc:postgresql://db.example.internal:5432/shop \
  -e FLYWAY_USER=migrator -e FLYWAY_PASSWORD="$DB_PASSWORD" \
  shop-migrations:1.4.2
```

**🔍 Explained:**

- The base image's `ENTRYPOINT` is `flyway`, so `CMD ["migrate"]` runs `flyway migrate`.
  Override to `info`, `validate`, etc.
- `FLYWAY_CONNECT_RETRIES=10` — wait for the DB to come up instead of failing immediately.
- Tag the migrations image with the **same version** as the app it belongs to.

**⚠️ DevOps Gotchas:**

- **Never edit an already-applied migration file** — Flyway's checksum check fails
  (`Migration checksum mismatch`). Always add a new `V<n>__...sql`.
- Make migrations **backward-compatible** (add columns, don't rename/drop in the same
  release). During rolling deploys, old and new app versions run side by side.
- Alternatives: **Liquibase** (Java), **Alembic** (Python), **EF Core migrations** (.NET),
  **golang-migrate** — same "migrations as a job" pattern.

---

## Example 80 — nginx reverse proxy

**🧾 What is this?** A **reverse proxy** receives all traffic and forwards it to the right
backend: `/api/*` → API containers, `/` → frontend. It can also load-balance across
several copies of the API.

`nginx.conf`:

```nginx
upstream api_backend {
    # Docker DNS names of the API containers; nginx load-balances between them
    server api-1:8080;
    server api-2:8080;
    keepalive 32;
}

server {
    listen 8080;
    server_tokens off;
    client_max_body_size 20m;

    location /api/ {
        proxy_pass http://api_backend/;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    location / {
        proxy_pass http://frontend:8080;
        proxy_set_header Host $host;
    }

    location = /healthz { return 200 "ok\n"; access_log off; }
}
```

`Dockerfile`:

```dockerfile
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Fail the BUILD if the config has syntax errors (instead of failing at deploy time)
RUN nginx -t
EXPOSE 8080
```

**🔍 Explained:**

- `upstream` — a named group of backend servers.
- `proxy_pass http://api_backend/;` — the **trailing slash** strips the `/api/` prefix:
  `/api/users` → backend receives `/users`. Without the slash, the backend receives `/api/users`.
- `X-Forwarded-*` headers — tell the backend the real client IP and original protocol.
- `RUN nginx -t` — validates configuration during the build. Cheap and catches typos early.

**⚠️ DevOps Gotchas:**

- `nginx -t` may fail at build time if upstream hostnames (`api-1`) can't be resolved
  (nginx resolves them at startup). In that case drop the `RUN nginx -t` line or validate
  in a Compose-based CI test instead.
- nginx resolves upstream DNS **once at startup**. If backend container IPs change (they
  do, on restart/scale), nginx keeps sending to dead IPs. Use the `resolver 127.0.0.11`
  directive with variables, or a Kubernetes Service (stable IP).
- The trailing slash on `proxy_pass` is the #1 nginx proxy mistake.

---

## Example 81 — HAProxy load balancer

`haproxy.cfg`:

```haproxy
global
    log stdout format raw local0

defaults
    mode http
    log global
    option httplog
    timeout connect 5s
    timeout client  30s
    timeout server  30s

frontend http_in
    bind *:8080
    default_backend api

backend api
    balance roundrobin
    option httpchk GET /health
    http-check expect status 200
    server api1 api-1:8080 check
    server api2 api-2:8080 check

# Built-in stats dashboard
frontend stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 10s
```

`Dockerfile`:

```dockerfile
FROM haproxy:3.0-alpine
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
# Validate configuration at build time (-c = check only)
RUN haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg
EXPOSE 8080 8404
```

**🔍 Explained:**

- `log stdout format raw` — logs go to stdout → `docker logs` works.
- `option httpchk GET /health` — HAProxy actively checks each backend and removes unhealthy ones.
- The official image already runs as the non-root `haproxy` user (hence ports > 1024).

**⚠️ DevOps Gotchas:**

- Same DNS-at-startup issue as nginx: use a `resolvers` section with
  `nameserver dns 127.0.0.11:53` for dynamic container IPs.

---

## Example 82 — PostgreSQL with a compiled extension

**🧾 What is this?** **pgvector** is a Postgres extension for AI "vector" search. When an
extension isn't packaged for your Postgres version, you compile it in a build stage and copy
just the compiled files into the official image.

```dockerfile
# syntax=docker/dockerfile:1
ARG PG_MAJOR=16

FROM postgres:${PG_MAJOR}-bookworm AS build
ARG PG_MAJOR
ARG PGVECTOR_VERSION=v0.7.4
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git ca-certificates postgresql-server-dev-${PG_MAJOR} \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/pgvector
RUN git clone --depth 1 --branch ${PGVECTOR_VERSION} https://github.com/pgvector/pgvector.git . \
 && make OPTFLAGS="" \
 && make install DESTDIR=/out

FROM postgres:${PG_MAJOR}-bookworm
ARG PG_MAJOR
# Copy only the compiled library and extension SQL/control files
COPY --from=build /out/usr/lib/postgresql/${PG_MAJOR}/lib/        /usr/lib/postgresql/${PG_MAJOR}/lib/
COPY --from=build /out/usr/share/postgresql/${PG_MAJOR}/extension/ /usr/share/postgresql/${PG_MAJOR}/extension/
# Enable it automatically in new databases
RUN echo "CREATE EXTENSION IF NOT EXISTS vector;" > /docker-entrypoint-initdb.d/00-vector.sql
```

**🔍 Explained:**

- `postgresql-server-dev-16` — headers needed to compile Postgres extensions.
- `git clone --depth 1 --branch v0.7.4` — fetch only that tagged version (pinned, reproducible).
- `make install DESTDIR=/out` — install into `/out/...` instead of the real system paths,
  so we can copy exactly those files.
- `OPTFLAGS=""` — disables CPU-specific optimisations (`-march=native`), so the binary
  runs on any CPU, not just the build machine's.
- `ARG PG_MAJOR` repeated after each `FROM` — ARGs before `FROM` must be re-declared inside
  a stage to be used there.

**⚠️ DevOps Gotchas:**

- Many popular extensions have ready-made images (`pgvector/pgvector:pg16`,
  `postgis/postgis:16-3.4`). Prefer those — less to maintain.
- Without `OPTFLAGS=""`, an extension compiled on a modern CI CPU can crash with
  "Illegal instruction" on older production hardware.

---

**Next:** [08 — DevOps Tooling, CI/CD & Monitoring ➡️](08-devops-tooling.md)
