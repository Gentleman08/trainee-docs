[🏠 Home](../README.md) · [Labs](README.md) · [Nginx Handbook](../servers/nginx.md)

# ⚡ Nginx — Hands-On Practice Lab

> **Audience:** DevOps / Cloud Engineers & Trainees | **Difficulty:** Beginner → Advanced (progressive)  
> **Time:** 4–6 hours (all exercises) | **Platform:** Linux (RHEL/CentOS or Ubuntu/Debian)  
> **Prerequisites:** Linux CLI basics, a VM or cloud instance with root access  
> **Reference:** [Nginx Advanced Configuration Guide](../servers/nginx.md)

---

## Table of Contents

1. [Lab Overview](#1-lab-overview)
2. [Lab Environment Setup](#2-lab-environment-setup)
3. [Exercise 1 — Install Nginx & Verify (Beginner)](#exercise-1--install-nginx--verify-beginner)
4. [Exercise 2 — Server Blocks (Virtual Hosts) (Beginner)](#exercise-2--server-blocks-virtual-hosts-beginner)
5. [Exercise 3 — Static Site with Caching & Compression (Beginner)](#exercise-3--static-site-with-caching--compression-beginner)
6. [Exercise 4 — SPA Hosting with try_files (Intermediate)](#exercise-4--spa-hosting-with-try_files-intermediate)
7. [Exercise 5 — Reverse Proxy to Node.js Backend (Intermediate)](#exercise-5--reverse-proxy-to-nodejs-backend-intermediate)
8. [Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)](#exercise-6--ssltls-with-self-signed-certificate-intermediate)
9. [Exercise 7 — PHP-FPM Integration (Intermediate)](#exercise-7--php-fpm-integration-intermediate)
10. [Exercise 8 — Load Balancing with Upstream (Advanced)](#exercise-8--load-balancing-with-upstream-advanced)
11. [Exercise 9 — Security Hardening & Rate Limiting (Advanced)](#exercise-9--security-hardening--rate-limiting-advanced)
12. [Exercise 10 — Proxy Cache, Monitoring & Docker (Advanced)](#exercise-10--proxy-cache-monitoring--docker-advanced)
13. [Cleanup](#cleanup)
14. [Troubleshooting Reference](#troubleshooting-reference)

---

## 1. Lab Overview

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                     LAB PROGRESSION                             │
  │                                                                 │
  │  Exercise 1-3:  BEGINNER                                        │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ Install → Server Blocks → Static Sites + Cache + Gzip   │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 4-7:  INTERMEDIATE                                    │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ SPA + try_files → Reverse Proxy → SSL/TLS → PHP-FPM    │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 8-10: ADVANCED                                        │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ Load Balancing → Security + Rate Limit → Cache + Docker │    │
  │  └──────────────────────────────────────────────────────────┘    │
  └─────────────────────────────────────────────────────────────────┘
```

### Final Architecture

```
  ┌───────────────────────────────────────────────────────────────────┐
  │                   FINAL LAB ARCHITECTURE                          │
  │                                                                   │
  │  Internet / Clients                                               │
  │       │                                                           │
  │  ┌────▼────────────────────────────────────────────────────┐      │
  │  │  Nginx                                                  │      │
  │  │  :443 (SSL/TLS) + :80 (→ redirect to HTTPS)            │      │
  │  │                                                         │      │
  │  │  ┌─────────────────────────────────────────────────┐    │      │
  │  │  │ server: static.lab.local  → Static HTML site    │    │      │
  │  │  │ server: app.lab.local     → SPA (try_files)     │    │      │
  │  │  │ server: api.lab.local     → Reverse Proxy       │────┼──┐   │
  │  │  │ server: php.lab.local     → PHP-FPM (FastCGI)   │    │  │   │
  │  │  │ server: lb.lab.local      → Load Balancer       │────┼──┤   │
  │  │  └─────────────────────────────────────────────────┘    │  │   │
  │  │                                                         │  │   │
  │  │  Rate Limiting + Security Headers + Proxy Cache         │  │   │
  │  │  stub_status (Monitoring) + JSON Logging                │  │   │
  │  └─────────────────────────────────────────────────────────┘  │   │
  │                                                               │   │
  │  ┌────────────────────────────────────────────────────────────┘   │
  │  │  Backend Services                                              │
  │  │  ├── Node.js :3001, :3002, :3003  (upstream load balanced)    │
  │  │  └── PHP-FPM (unix socket)                                     │
  │  └────────────────────────────────────────────────────────────────┘
  └───────────────────────────────────────────────────────────────────┘
```

---

## 2. Lab Environment Setup

### 2.1 Provision a VM

- **Cloud:** AWS EC2, DigitalOcean Droplet, Azure VM, GCP Compute
- **Local:** VirtualBox, VMware, Vagrant, Multipass

**Minimum specs:** 1 vCPU, 1 GB RAM, 10 GB disk  
**Recommended OS:** Rocky Linux 9 / AlmaLinux 9 / Ubuntu 22.04 LTS

### 2.2 Set Up Local DNS

On your **local machine** (not the server):

```bash
# Linux/macOS: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts

<SERVER_IP>  static.lab.local
<SERVER_IP>  app.lab.local
<SERVER_IP>  api.lab.local
<SERVER_IP>  php.lab.local
<SERVER_IP>  lb.lab.local
```

### 2.3 Initial Server Setup

```bash
# Update
sudo dnf update -y          # RHEL-family
# sudo apt update && sudo apt upgrade -y   # Debian-family

# Install tools
sudo dnf install -y curl wget vim tree net-tools bind-utils
# sudo apt install -y curl wget vim tree net-tools dnsutils

# Disable SELinux temporarily for learning (re-enable in Exercise 9)
# RHEL only:
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
```

---

## Exercise 1 — Install Nginx & Verify (Beginner)

**Objective:** Install Nginx, understand the process model, explore config file layout.

**Time:** 15 minutes

### Step 1 — Install Nginx

```bash
# RHEL/CentOS/Rocky/Alma
sudo dnf install epel-release -y
sudo dnf install nginx -y

# Ubuntu/Debian
# sudo apt install nginx -y
```

### Step 2 — Start and Enable

```bash
sudo systemctl enable --now nginx
```

### Step 3 — Open Firewall

```bash
# RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Debian (ufw)
# sudo ufw allow 'Nginx Full'
```

### Step 4 — Verify Installation

```bash
# Check version
nginx -v

# Check process model
ps aux | grep nginx
# You should see: 1 master process + N worker processes (N = CPU cores)

# Test config syntax
nginx -t

# Dump full merged config
nginx -T | head -50

# Test HTTP response
curl -I http://localhost
```

### Step 5 — Explore File Layout

```bash
# RHEL layout
tree /etc/nginx/ -L 2

# Key files:
head -30 /etc/nginx/nginx.conf
ls -la /etc/nginx/conf.d/
ls -la /usr/share/nginx/html/
ls -la /var/log/nginx/

# Debian also has:
# ls -la /etc/nginx/sites-available/
# ls -la /etc/nginx/sites-enabled/
```

### ✅ Verification Checklist

- [ ] `curl -I http://localhost` returns 200
- [ ] `ps aux | grep nginx` shows master + worker processes
- [ ] Worker count matches CPU cores (`nproc`)
- [ ] Default welcome page visible in browser at `http://<SERVER_IP>`

> **⚠️ Gotcha (RHEL):** RHEL uses `/etc/nginx/conf.d/` for server blocks (drop-in `*.conf`). Debian uses `sites-available/` + `sites-enabled/` (symlink pattern). Don't mix conventions.

---

## Exercise 2 — Server Blocks (Virtual Hosts) (Beginner)

**Objective:** Create multiple server blocks routing different domains to different sites.

**Time:** 20 minutes

### Architecture

```
  ┌──────────────┐           ┌──────────────────────────────────┐
  │ Browser      │           │ Nginx (:80)                      │
  │              │           │                                  │
  │ Host: static │──────────►│ server: static.lab.local         │
  │ .lab.local   │           │ → /var/www/static-site/          │
  │              │           │                                  │
  │ Host: app    │──────────►│ server: app.lab.local            │
  │ .lab.local   │           │ → /var/www/app-site/             │
  └──────────────┘           └──────────────────────────────────┘
```

### Step 1 — Create Document Roots

```bash
sudo mkdir -p /var/www/static-site
sudo mkdir -p /var/www/app-site

# Static site content
sudo tee /var/www/static-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Static Site</title></head>
<body>
  <h1>🏠 Static Site — static.lab.local</h1>
  <p>This is the static site server block.</p>
</body>
</html>
EOF

# App site content
sudo tee /var/www/app-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>App Site</title></head>
<body>
  <h1>🚀 App Site — app.lab.local</h1>
  <p>This is the application site server block.</p>
</body>
</html>
EOF

sudo chown -R nginx:nginx /var/www/static-site /var/www/app-site    # RHEL
# sudo chown -R www-data:www-data /var/www/static-site /var/www/app-site  # Debian
```

### Step 2 — Create Server Block Configs

```bash
# Remove default config (RHEL)
sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak

# Debian: sudo rm /etc/nginx/sites-enabled/default

# Static site server block
sudo tee /etc/nginx/conf.d/static-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  static.lab.local;

    root         /var/www/static-site;
    index        index.html;

    access_log   /var/log/nginx/static-access.log;
    error_log    /var/log/nginx/static-error.log;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# App site server block
sudo tee /etc/nginx/conf.d/app-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  app.lab.local;

    root         /var/www/app-site;
    index        index.html;

    access_log   /var/log/nginx/app-access.log;
    error_log    /var/log/nginx/app-error.log;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

# Catch-all for unmatched hostnames
sudo tee /etc/nginx/conf.d/00-default.conf > /dev/null << 'EOF'
server {
    listen       80 default_server;
    server_name  _;

    return 444;    # Drop connection — Nginx-specific "reject"
}
EOF
```

### Step 3 — Test and Reload

```bash
# ALWAYS test before reload
nginx -t

# Graceful reload (zero-downtime)
sudo systemctl reload nginx
```

### Step 4 — Verify

```bash
# Test each server block
curl -H "Host: static.lab.local" http://localhost
curl -H "Host: app.lab.local" http://localhost

# Test catch-all (should get empty response / connection reset)
curl -H "Host: unknown.domain" http://localhost
# curl: (52) Empty reply from server  ← that's the 444 response
```

### ✅ Verification Checklist

- [ ] `static.lab.local` shows "Static Site"
- [ ] `app.lab.local` shows "App Site"
- [ ] Unknown hostnames get dropped (empty reply / 444)
- [ ] `nginx -t` returns "syntax is ok"

> **⚠️ Gotcha:** The `default_server` flag on `listen` determines the catch-all. Without it, Nginx uses the **first server block** in load order as default. Name your catch-all `00-default.conf` to ensure it loads first.

---

## Exercise 3 — Static Site with Caching & Compression (Beginner)

**Objective:** Add browser caching headers, gzip compression, and custom error pages.

**Time:** 20 minutes

### Step 1 — Create Error Pages and Test Assets

```bash
sudo mkdir -p /var/www/static-site/errors
sudo mkdir -p /var/www/static-site/images

# Custom 404
sudo tee /var/www/static-site/errors/404.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html><head><title>404</title></head>
<body><h1>404 — Not Found</h1><p>This page doesn't exist on static.lab.local.</p><a href="/">Home</a></body>
</html>
EOF

# Custom 50x
sudo tee /var/www/static-site/errors/50x.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html><head><title>Server Error</title></head>
<body><h1>500 — Server Error</h1><p>Something went wrong. Try again later.</p></body>
</html>
EOF

# A CSS file for testing cache headers
sudo tee /var/www/static-site/style.css > /dev/null << 'EOF'
body { font-family: sans-serif; max-width: 800px; margin: 50px auto; background: #f5f5f5; }
h1 { color: #333; }
EOF

sudo chown -R nginx:nginx /var/www/static-site
```

### Step 2 — Update Server Block with Full Features

```bash
sudo tee /etc/nginx/conf.d/static-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  static.lab.local;

    root         /var/www/static-site;
    index        index.html;

    access_log   /var/log/nginx/static-access.log;
    error_log    /var/log/nginx/static-error.log;

    # --- Static file serving ---
    location / {
        try_files $uri $uri/ =404;
    }

    # --- Cache static assets aggressively ---
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;    # Don't log static asset hits
    }

    # --- Custom error pages ---
    error_page 404 /errors/404.html;
    error_page 500 502 503 504 /errors/50x.html;

    location = /errors/404.html {
        internal;    # Only served on actual errors, not direct requests
    }
    location = /errors/50x.html {
        internal;
    }

    # --- Block hidden files ---
    location ~ /\. {
        deny all;
        return 404;
    }

    # --- Block backup files ---
    location ~* \.(bak|old|swp|sql|tar\.gz)$ {
        deny all;
        return 404;
    }
}
EOF
```

### Step 3 — Enable Gzip Globally

```bash
# Check if gzip is already in nginx.conf
grep -n "gzip" /etc/nginx/nginx.conf

# Add/update gzip settings in the http block
# If not present, create a gzip snippet:
sudo tee /etc/nginx/conf.d/gzip.conf > /dev/null << 'EOF'
# Gzip Compression — applied globally
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_min_length 256;
gzip_types
    text/plain
    text/css
    application/json
    application/javascript
    text/xml
    application/xml
    application/xml+rss
    text/javascript
    image/svg+xml;
EOF
```

### Step 4 — Test

```bash
nginx -t && sudo systemctl reload nginx

# Test caching headers on CSS
curl -I -H "Host: static.lab.local" http://localhost/style.css
# Should show: Cache-Control: public, immutable + Expires header

# Test gzip compression
curl -H "Host: static.lab.local" -H "Accept-Encoding: gzip" -I http://localhost/
# Should show: Content-Encoding: gzip

# Test custom 404
curl -H "Host: static.lab.local" http://localhost/nonexistent
# Should show your custom 404 page

# Test hidden file blocking
curl -I -H "Host: static.lab.local" http://localhost/.env
# Should return 404 (denied)
```

### ✅ Verification Checklist

- [ ] CSS files return `Cache-Control: public, immutable` and `Expires` header
- [ ] HTML responses are gzip-compressed
- [ ] Custom 404 page appears for missing paths
- [ ] `.env`, `.git` requests are blocked

---

## Exercise 4 — SPA Hosting with try_files (Intermediate)

**Objective:** Configure Nginx to serve a Single Page Application where all routes fallback to `index.html`.

**Time:** 15 minutes

### The Key Concept

```
  ┌──────────────────────────────────────────────────────────────┐
  │  try_files $uri $uri/ /index.html;                           │
  │                                                              │
  │  Request: /dashboard                                         │
  │  Step 1: Does /var/www/app-site/dashboard exist? → No       │
  │  Step 2: Does /var/www/app-site/dashboard/ exist? → No      │
  │  Step 3: Serve /var/www/app-site/index.html ← SPA fallback  │
  │          (JavaScript router handles /dashboard client-side)  │
  └──────────────────────────────────────────────────────────────┘
```

### Step 1 — Create SPA Content

```bash
sudo mkdir -p /var/www/app-site/assets/css
sudo mkdir -p /var/www/app-site/assets/js

sudo tee /var/www/app-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>SPA App</title>
  <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
  <nav>
    <a href="/">Home</a> |
    <a href="/about">About</a> |
    <a href="/dashboard">Dashboard</a> |
    <a href="/settings">Settings</a>
  </nav>
  <div id="app">
    <h1>🚀 SPA Application</h1>
    <p>Current route: <strong id="route"></strong></p>
    <p>All routes serve this index.html — the JS router handles navigation.</p>
  </div>
  <script>document.getElementById('route').textContent = window.location.pathname;</script>
</body>
</html>
EOF

sudo tee /var/www/app-site/assets/css/app.css > /dev/null << 'EOF'
body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
nav { background: #2196F3; padding: 12px; border-radius: 4px; }
nav a { color: white; margin: 0 15px; text-decoration: none; font-weight: bold; }
EOF

sudo chown -R nginx:nginx /var/www/app-site
```

### Step 2 — Configure SPA Server Block

```bash
sudo tee /etc/nginx/conf.d/app-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  app.lab.local;

    root         /var/www/app-site;
    index        index.html;

    access_log   /var/log/nginx/app-access.log;
    error_log    /var/log/nginx/app-error.log;

    # SPA fallback — the key directive
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API calls go to backend (we'll set this up in Exercise 5)
    # location /api/ {
    #     proxy_pass http://localhost:3001;
    # }

    # Cache static assets
    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

### Step 3 — Test SPA Routing

```bash
nginx -t && sudo systemctl reload nginx

# All these should return the SAME index.html content:
curl -s -H "Host: app.lab.local" http://localhost/ | grep "<h1>"
curl -s -H "Host: app.lab.local" http://localhost/about | grep "<h1>"
curl -s -H "Host: app.lab.local" http://localhost/dashboard | grep "<h1>"
curl -s -H "Host: app.lab.local" http://localhost/any/deep/nested/route | grep "<h1>"

# But real files should be served directly:
curl -I -H "Host: app.lab.local" http://localhost/assets/css/app.css
# Should return 200 with text/css content type
```

### ✅ Verification Checklist

- [ ] `/`, `/about`, `/dashboard`, `/any/route` all return the SPA index.html
- [ ] `/assets/css/app.css` returns the actual CSS file
- [ ] CSS files have cache headers (expires 30d)

---

## Exercise 5 — Reverse Proxy to Node.js Backend (Intermediate)

**Objective:** Set up Nginx as a reverse proxy forwarding to a Node.js API.

**Time:** 30 minutes

### Architecture

```
  Client → Nginx (:80) → Node.js (:3001)

  ┌──────────────┐     ┌─────────────────┐     ┌────────────────┐
  │  Browser     │────►│ Nginx           │────►│ Node.js        │
  │              │     │ api.lab.local   │     │ 127.0.0.1:3001 │
  │              │◄────│                 │◄────│ (JSON API)     │
  └──────────────┘     └─────────────────┘     └────────────────┘

  Nginx adds headers:
  ├── Host: api.lab.local (original)
  ├── X-Real-IP: <client IP>
  ├── X-Forwarded-For: <client IP>
  └── X-Forwarded-Proto: http/https
```

### Step 1 — Install Node.js & Create Backend

```bash
sudo dnf install -y nodejs npm
# sudo apt install -y nodejs npm

sudo mkdir -p /opt/api-backend

sudo tee /opt/api-backend/server.js > /dev/null << 'JSEOF'
const http = require('http');
const PORT = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  const response = {
    message: 'Hello from Node.js backend!',
    path: req.url,
    method: req.method,
    headers: {
      host: req.headers.host,
      'x-real-ip': req.headers['x-real-ip'] || 'not set',
      'x-forwarded-for': req.headers['x-forwarded-for'] || 'not set',
      'x-forwarded-proto': req.headers['x-forwarded-proto'] || 'not set'
    },
    timestamp: new Date().toISOString(),
    pid: process.pid,
    port: PORT
  };
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(response, null, 2));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`API running on http://127.0.0.1:${PORT} (PID: ${process.pid})`);
});
JSEOF

cd /opt/api-backend && node server.js &
sleep 1
curl -s http://127.0.0.1:3001/ | head -5
```

### Step 2 — Create Reverse Proxy Server Block

```bash
sudo tee /etc/nginx/conf.d/api-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  api.lab.local;

    access_log   /var/log/nginx/api-access.log;
    error_log    /var/log/nginx/api-error.log;

    location / {
        proxy_pass http://127.0.0.1:3001;

        # --- Essential proxy headers ---
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # --- Timeouts ---
        proxy_connect_timeout 60s;
        proxy_send_timeout    60s;
        proxy_read_timeout    60s;

        # --- Buffering ---
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
EOF
```

### Step 3 — Test

```bash
nginx -t && sudo systemctl reload nginx

# Test through proxy
curl -s -H "Host: api.lab.local" http://localhost/ | python3 -m json.tool

# Verify headers are passed:
# "host" should be "api.lab.local"
# "x-real-ip" should show an IP
# "x-forwarded-proto" should show "http"

# Test different paths
curl -s -H "Host: api.lab.local" http://localhost/users | python3 -m json.tool
curl -s -H "Host: api.lab.local" http://localhost/api/v1/data | python3 -m json.tool
```

### ✅ Verification Checklist

- [ ] API responses show `host: api.lab.local`
- [ ] `x-real-ip` is populated (not "not set")
- [ ] All URL paths passed through correctly
- [ ] Responses are valid JSON

> **⚠️ Gotcha (RHEL/SELinux):** If you get 502 Bad Gateway, SELinux is likely blocking the proxy connection. Fix:
> ```bash
> sudo setsebool -P httpd_can_network_connect 1
> ```

---

## Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)

**Objective:** Generate a wildcard self-signed cert, configure HTTPS, and set up HTTP→HTTPS redirect.

**Time:** 25 minutes

### Step 1 — Generate Certificate

```bash
sudo mkdir -p /etc/nginx/ssl

sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/lab.key \
  -out /etc/nginx/ssl/lab.crt \
  -subj "/C=IN/ST=Gujarat/L=Ahmedabad/O=Lab/CN=*.lab.local"

openssl x509 -in /etc/nginx/ssl/lab.crt -text -noout | head -15

sudo chmod 600 /etc/nginx/ssl/lab.key
sudo chmod 644 /etc/nginx/ssl/lab.crt
```

### Step 2 — Create SSL Snippet (Reusable)

```bash
sudo tee /etc/nginx/conf.d/ssl-params.conf > /dev/null << 'EOF'
# Reusable SSL parameters — include in HTTPS server blocks
# Usage: include /etc/nginx/conf.d/ssl-params.conf;
# Note: This file has no server{} block — it's a snippet.

# These are directives to be included inside server{} blocks.
# They are NOT standalone — they'll cause errors if loaded as a standalone conf.
# Rename to .inc to prevent auto-loading, or keep and include manually.
EOF

# Actually, let's make it a proper snippet file:
sudo mkdir -p /etc/nginx/snippets

sudo tee /etc/nginx/snippets/ssl-params.conf > /dev/null << 'EOF'
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';

ssl_session_cache   shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;

add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
EOF

# Remove the conf.d file (it would be auto-loaded and cause errors)
sudo rm -f /etc/nginx/conf.d/ssl-params.conf
```

### Step 3 — Update Static Site for HTTPS

```bash
sudo tee /etc/nginx/conf.d/static-site.conf > /dev/null << 'EOF'
# HTTP → HTTPS redirect
server {
    listen       80;
    server_name  static.lab.local;
    return 301   https://$host$request_uri;
}

# HTTPS server block
server {
    listen       443 ssl;
    server_name  static.lab.local;

    ssl_certificate     /etc/nginx/ssl/lab.crt;
    ssl_certificate_key /etc/nginx/ssl/lab.key;
    include             /etc/nginx/snippets/ssl-params.conf;

    root         /var/www/static-site;
    index        index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~* \.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        # Re-add HSTS since add_header in child block kills parent headers
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    }

    error_page 404 /errors/404.html;
    error_page 500 502 503 504 /errors/50x.html;
    location = /errors/404.html { internal; }
    location = /errors/50x.html { internal; }

    location ~ /\. { deny all; return 404; }

    access_log /var/log/nginx/static-ssl-access.log;
    error_log  /var/log/nginx/static-ssl-error.log;
}
EOF
```

### Step 4 — Test

```bash
nginx -t && sudo systemctl reload nginx

# Test HTTP redirect
curl -I -H "Host: static.lab.local" http://localhost/
# Should: 301 → https://static.lab.local/

# Test HTTPS (-k = skip cert verification for self-signed)
curl -k -I -H "Host: static.lab.local" https://localhost/
# Should: 200 OK + Strict-Transport-Security header

# Check TLS version
openssl s_client -connect localhost:443 -servername static.lab.local < /dev/null 2>/dev/null | grep "Protocol\|Cipher"
```

### ✅ Verification Checklist

- [ ] HTTP port 80 redirects to HTTPS (301)
- [ ] HTTPS returns 200 with the static site
- [ ] `Strict-Transport-Security` header present
- [ ] TLS 1.2 or 1.3 negotiated (no older protocols)

> **⚠️ Gotcha (add_header inheritance):** If a `location {}` block has its own `add_header`, ALL parent `add_header` directives are dropped for that block — including HSTS! Always repeat critical headers or use `include` snippets in every location block.

---

## Exercise 7 — PHP-FPM Integration (Intermediate)

**Objective:** Serve PHP pages via FastCGI to PHP-FPM.

**Time:** 25 minutes

### Step 1 — Install PHP-FPM

```bash
# RHEL
sudo dnf install php-fpm php-cli php-json php-mbstring -y

# Debian
# sudo apt install php-fpm php-cli php-json php-mbstring -y

sudo systemctl enable --now php-fpm
```

### Step 2 — Verify PHP-FPM Socket

```bash
# RHEL: default socket
ls -la /run/php-fpm/www.sock
# Should be owned by nginx:nginx (or apache:apache — needs adjusting)

# Check and fix socket ownership
sudo grep -E "^(listen|user|group)" /etc/php-fpm.d/www.conf

# If user/group is apache, change to nginx:
sudo sed -i 's/^user = apache/user = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/^group = apache/group = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/^listen.owner = apache/listen.owner = nginx/' /etc/php-fpm.d/www.conf
sudo sed -i 's/^listen.group = apache/listen.group = nginx/' /etc/php-fpm.d/www.conf

sudo systemctl restart php-fpm
ls -la /run/php-fpm/www.sock
```

### Step 3 — Create PHP Site

```bash
sudo mkdir -p /var/www/php-site

sudo tee /var/www/php-site/index.php > /dev/null << 'PHPEOF'
<?php
echo "<h1>🐘 PHP Site — php.lab.local</h1>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>SAPI: " . php_sapi_name() . "</p>";
echo "<p>Time: " . date('Y-m-d H:i:s') . "</p>";
echo "<hr><h2>Server Variables</h2><pre>";
foreach (['SERVER_SOFTWARE','REMOTE_ADDR','HTTP_HOST','HTTP_X_REAL_IP'] as $k) {
    echo "$k: " . ($_SERVER[$k] ?? 'N/A') . "\n";
}
echo "</pre>";
PHPEOF

sudo tee /var/www/php-site/info.php > /dev/null << 'PHPEOF'
<?php phpinfo(); ?>
PHPEOF

sudo chown -R nginx:nginx /var/www/php-site
```

### Step 4 — Create PHP Server Block

```bash
sudo tee /etc/nginx/conf.d/php-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  php.lab.local;

    root         /var/www/php-site;
    index        index.php index.html;

    access_log   /var/log/nginx/php-access.log;
    error_log    /var/log/nginx/php-error.log;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    # Pass PHP to FPM
    location ~ \.php$ {
        # Security: only process existing files
        try_files $uri =404;

        fastcgi_pass  unix:/run/php-fpm/www.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include       fastcgi_params;

        fastcgi_read_timeout 300s;
    }

    # Block PHP execution in uploads
    location ~* /uploads/.*\.php$ {
        deny all;
    }

    # Block hidden files
    location ~ /\. {
        deny all;
        return 404;
    }
}
EOF
```

### Step 5 — Test

```bash
nginx -t && sudo systemctl reload nginx

curl -H "Host: php.lab.local" http://localhost/
# Should show PHP version and "SAPI: fpm-fcgi"

curl -H "Host: php.lab.local" http://localhost/info.php | head -30
# Should show phpinfo HTML output
```

### ✅ Verification Checklist

- [ ] PHP pages execute and show version info
- [ ] SAPI shows `fpm-fcgi` (FastCGI, not Apache module)
- [ ] `/info.php` returns phpinfo output
- [ ] Non-existent `.php` files return 404 (not passed to FPM)

> **⚠️ Gotcha:** Without `try_files $uri =404;` in the PHP location block, an attacker could exploit `cgi.fix_pathinfo` to execute uploaded images as PHP. Always validate the file exists before passing to FPM.

---

## Exercise 8 — Load Balancing with Upstream (Advanced)

**Objective:** Configure Nginx as a load balancer across multiple Node.js instances.

**Time:** 30 minutes

### Architecture

```
  ┌──────────────┐     ┌─────────────────────────┐     ┌────────────┐
  │  Browser     │────►│  Nginx (Load Balancer)  │──┬─►│ Node :3001 │
  │              │     │  lb.lab.local            │  │  └────────────┘
  │              │◄────│                          │  │  ┌────────────┐
  └──────────────┘     │  upstream node_pool {}   │──┼─►│ Node :3002 │
                       │  (round robin + health)  │  │  └────────────┘
                       └─────────────────────────┘  │  ┌────────────┐
                                                    └─►│ Node :3003 │
                                                       └────────────┘
```

### Step 1 — Start Multiple Backends

```bash
cd /opt/api-backend
pkill -f "node server.js" 2>/dev/null
sleep 1

PORT=3001 node server.js &
PORT=3002 node server.js &
PORT=3003 node server.js &
sleep 1

# Verify all running
for port in 3001 3002 3003; do
  echo "Port $port: $(curl -s http://127.0.0.1:$port/ | python3 -c "import sys,json; print('PID', json.load(sys.stdin)['pid'])")"
done
```

### Step 2 — Create Load Balancer Config

```bash
sudo tee /etc/nginx/conf.d/lb-site.conf > /dev/null << 'EOF'
# Define backend pool
upstream node_pool {
    # Round Robin (default) — requests cycle through backends
    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3003 max_fails=3 fail_timeout=30s;

    # Keep connections alive to backends (performance optimization)
    keepalive 32;
}

server {
    listen       80;
    server_name  lb.lab.local;

    access_log   /var/log/nginx/lb-access.log;
    error_log    /var/log/nginx/lb-error.log;

    location / {
        proxy_pass http://node_pool;

        # Required for keepalive to upstream
        proxy_http_version 1.1;
        proxy_set_header Connection "";

        # Forward client info
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_read_timeout    60s;
        proxy_send_timeout    60s;

        # On error, try next backend
        proxy_next_upstream error timeout http_502 http_503;
    }
}
EOF
```

### Step 3 — Test Load Balancing

```bash
nginx -t && sudo systemctl reload nginx

# Send 9 requests — should cycle through 3 backends (round robin)
for i in {1..9}; do
  port=$(curl -s -H "Host: lb.lab.local" http://localhost/ | python3 -c "import sys,json; print(json.load(sys.stdin)['port'])")
  echo "Request $i → Port $port"
done

# Expected: 3001, 3002, 3003, 3001, 3002, 3003, 3001, 3002, 3003
```

### Step 4 — Test Failover

```bash
# Kill one backend
kill $(lsof -ti:3002) 2>/dev/null
sleep 2

# Requests should still work (only 3001 and 3003)
for i in {1..6}; do
  port=$(curl -s -H "Host: lb.lab.local" http://localhost/ | python3 -c "import sys,json; print(json.load(sys.stdin)['port'])" 2>/dev/null)
  echo "Request $i → Port ${port:-FAILED}"
done

# Restart the killed backend
PORT=3002 node /opt/api-backend/server.js &
sleep 2

# Verify it rejoined (after fail_timeout=30s expires)
```

### Step 5 — Test Different Algorithms

```bash
# Uncomment and test different methods in the upstream block:

# Least connections (best for varying response times):
# upstream node_pool {
#     least_conn;
#     server 127.0.0.1:3001;
#     server 127.0.0.1:3002;
#     server 127.0.0.1:3003;
# }

# IP Hash (sticky sessions — same client always hits same backend):
# upstream node_pool {
#     ip_hash;
#     server 127.0.0.1:3001;
#     server 127.0.0.1:3002;
#     server 127.0.0.1:3003;
# }

# Weighted (send more traffic to faster servers):
# upstream node_pool {
#     server 127.0.0.1:3001 weight=5;
#     server 127.0.0.1:3002 weight=3;
#     server 127.0.0.1:3003 weight=1;
# }
```

### ✅ Verification Checklist

- [ ] Requests cycle through all 3 backends (round robin)
- [ ] When one backend is killed, remaining backends handle traffic
- [ ] Killed backend rejoins after restart + fail_timeout
- [ ] `proxy_next_upstream` ensures seamless failover

> **⚠️ Gotcha:** `ip_hash` breaks when clients come through a CDN or NAT — thousands of users share one IP, overloading a single backend. Use cookie-based sticky sessions or externalize state to Redis instead.

---

## Exercise 9 — Security Hardening & Rate Limiting (Advanced)

**Objective:** Apply production security: hide server info, add headers, configure rate limiting, and re-enable SELinux.

**Time:** 30 minutes

### Step 1 — Hide Nginx Version

```bash
# Add to the http block in nginx.conf (if not already there)
# Check first:
grep "server_tokens" /etc/nginx/nginx.conf

# If not present, add it:
sudo sed -i '/http {/a\    server_tokens off;' /etc/nginx/nginx.conf
```

### Step 2 — Create Security Headers Snippet

```bash
sudo tee /etc/nginx/snippets/security-headers.conf > /dev/null << 'EOF'
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
EOF
```

### Step 3 — Configure Rate Limiting

```bash
sudo tee /etc/nginx/conf.d/rate-limiting.conf > /dev/null << 'EOF'
# Rate limit zones (define in http context)
# 10 requests/second per client IP for general API
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 1 request/second for login endpoints (brute-force protection)
limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/s;

# Connection limit (max concurrent connections per IP)
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;
EOF
```

### Step 4 — Apply Rate Limiting to API Site

```bash
sudo tee /etc/nginx/conf.d/api-site.conf > /dev/null << 'EOF'
server {
    listen       80;
    server_name  api.lab.local;

    access_log   /var/log/nginx/api-access.log;
    error_log    /var/log/nginx/api-error.log;

    # Include security headers
    include /etc/nginx/snippets/security-headers.conf;

    # Connection limit
    limit_conn conn_limit 50;

    location / {
        # Rate limit: 10 req/s, burst up to 20, no delay for first 10
        limit_req zone=api_limit burst=20 nodelay;
        limit_req_status 429;

        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Strict rate limit on login
    location /login {
        limit_req zone=login_limit burst=5;
        limit_req_status 429;

        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Block sensitive paths
    location ~ /\.(git|svn|env|htpasswd) {
        deny all;
        return 404;
    }

    # Disable unused HTTP methods
    if ($request_method !~ ^(GET|HEAD|POST|PUT|PATCH|DELETE)$) {
        return 405;
    }
}
EOF
```

### Step 5 — Re-enable SELinux (RHEL)

```bash
sudo setenforce 1
sudo sed -i 's/SELINUX=permissive/SELINUX=enforcing/' /etc/selinux/config

# Allow Nginx to proxy
sudo setsebool -P httpd_can_network_connect 1

# Verify
getenforce
getsebool httpd_can_network_connect
```

### Step 6 — Test

```bash
nginx -t && sudo systemctl reload nginx

# Test server header hiding
curl -I -H "Host: api.lab.local" http://localhost/
# Should show: Server: nginx (no version number)

# Test security headers
curl -I -H "Host: api.lab.local" http://localhost/ 2>/dev/null | grep -E "X-Frame|X-Content|Referrer|Permissions|Content-Security"

# Test rate limiting (send 30 rapid requests)
for i in {1..30}; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -H "Host: api.lab.local" http://localhost/)
  echo "Request $i: HTTP $code"
done
# First ~20 should be 200, then 429 (Too Many Requests)

# Test hidden path blocking
curl -I -H "Host: api.lab.local" http://localhost/.env
# Should return 404
```

### ✅ Verification Checklist

- [ ] Server header shows `nginx` (no version)
- [ ] Security headers present (X-Frame-Options, CSP, etc.)
- [ ] Rate limiting returns 429 when exceeded
- [ ] `.env`, `.git` paths are blocked
- [ ] SELinux enforcing and Nginx still works

---

## Exercise 10 — Proxy Cache, Monitoring & Docker (Advanced)

**Objective:** Configure Nginx proxy caching, stub_status monitoring, structured JSON logging, and understand Docker deployment.

**Time:** 30 minutes

### Step 1 — Set Up Proxy Cache

```bash
# Create cache directory
sudo mkdir -p /var/cache/nginx/proxy
sudo chown nginx:nginx /var/cache/nginx/proxy

# Add proxy cache zone to main config
# First, check if proxy_cache_path already exists:
grep "proxy_cache_path" /etc/nginx/nginx.conf

# Add it to the http block:
sudo sed -i '/http {/a\    proxy_cache_path /var/cache/nginx/proxy levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m use_temp_path=off;' /etc/nginx/nginx.conf
```

### Step 2 — Apply Caching to Load Balancer

```bash
sudo tee /etc/nginx/conf.d/lb-site.conf > /dev/null << 'EOF'
upstream node_pool {
    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3002 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3003 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen       80;
    server_name  lb.lab.local;

    access_log   /var/log/nginx/lb-access.log;
    error_log    /var/log/nginx/lb-error.log;

    location / {
        proxy_pass http://node_pool;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Proxy Cache
        proxy_cache api_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503;
        proxy_cache_lock on;

        # Show cache status in response header
        add_header X-Cache-Status $upstream_cache_status always;
    }
}
EOF
```

### Step 3 — Enable stub_status Monitoring

```bash
sudo tee /etc/nginx/conf.d/monitoring.conf > /dev/null << 'EOF'
server {
    listen       8080;
    server_name  localhost;

    # Nginx status endpoint (for Prometheus/Nagios/Zabbix)
    location /nginx_status {
        stub_status;
        allow 127.0.0.1;
        allow 10.0.0.0/8;
        allow 192.168.0.0/16;
        deny all;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF
```

### Step 4 — JSON Structured Logging

```bash
# Add JSON log format to nginx.conf http block
sudo tee /etc/nginx/conf.d/json-logging.conf > /dev/null << 'EOF'
# JSON log format — use with: access_log /path/file.log json_combined;
log_format json_combined escape=json
    '{'
        '"time": "$time_iso8601",'
        '"remote_addr": "$remote_addr",'
        '"request_method": "$request_method",'
        '"request_uri": "$request_uri",'
        '"status": $status,'
        '"body_bytes_sent": $body_bytes_sent,'
        '"request_time": $request_time,'
        '"upstream_response_time": "$upstream_response_time",'
        '"http_user_agent": "$http_user_agent",'
        '"http_referer": "$http_referer",'
        '"upstream_cache_status": "$upstream_cache_status"'
    '}';
EOF
```

### Step 5 — Test Everything

```bash
nginx -t && sudo systemctl reload nginx

# Test proxy cache
curl -I -H "Host: lb.lab.local" http://localhost/
# First request: X-Cache-Status: MISS
curl -I -H "Host: lb.lab.local" http://localhost/
# Second request: X-Cache-Status: HIT ← served from cache!

# Test monitoring
curl http://localhost:8080/nginx_status
# Shows: Active connections, accepts, handled, requests, reading, writing, waiting

# Test health endpoint
curl http://localhost:8080/health
# Returns: OK

# Test JSON logging
sudo tail -1 /var/log/nginx/lb-access.log
# Shows JSON-formatted log entries (if json_combined format is applied)
```

### Step 6 — Docker Deployment (Conceptual + Config)

If Docker is available on your VM, test containerized Nginx:

```bash
# Create a Docker-ready config
mkdir -p /tmp/nginx-docker

cat > /tmp/nginx-docker/nginx.conf << 'DOCKEREOF'
worker_processes auto;
error_log /dev/stderr;
pid /tmp/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    access_log    /dev/stdout;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
DOCKEREOF

cat > /tmp/nginx-docker/index.html << 'DOCKEREOF'
<h1>Hello from Dockerized Nginx!</h1>
DOCKEREOF

# If Docker is installed:
# docker run -d --name nginx-lab \
#   -p 8081:80 \
#   -v /tmp/nginx-docker/nginx.conf:/etc/nginx/nginx.conf:ro \
#   -v /tmp/nginx-docker/index.html:/usr/share/nginx/html/index.html:ro \
#   nginx:alpine

# curl http://localhost:8081/
```

> **Key Docker gotchas:**
> 1. `daemon off;` or `-g 'daemon off;'` — Nginx must run in foreground
> 2. Logs to `/dev/stdout` and `/dev/stderr` for `docker logs`
> 3. Docker internal DNS resolver: `resolver 127.0.0.11` (for compose)

### ✅ Verification Checklist

- [ ] Proxy cache works (MISS → HIT on second request)
- [ ] `X-Cache-Status` header visible in responses
- [ ] `/nginx_status` returns active connection metrics
- [ ] `/health` endpoint returns 200 OK
- [ ] JSON log format produces valid JSON

---

## Cleanup

```bash
# Stop backends
pkill -f "node server.js"

# Stop services
sudo systemctl stop nginx
sudo systemctl stop php-fpm

# Remove configs
sudo rm -f /etc/nginx/conf.d/{static-site,app-site,api-site,php-site,lb-site,00-default,gzip,rate-limiting,monitoring,json-logging}.conf
sudo rm -rf /var/www/{static-site,app-site,php-site}
sudo rm -rf /opt/api-backend
sudo rm -rf /etc/nginx/ssl /etc/nginx/snippets
sudo rm -rf /var/cache/nginx/proxy
```

---

## Troubleshooting Reference

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  COMMON ISSUES & FIXES                                           │
  │                                                                  │
  │  Problem                        Fix                              │
  │  ─────────────────────────────  ───────────────────────────────  │
  │  502 Bad Gateway                Backend down, SELinux blocking,  │
  │                                 wrong socket path, permissions   │
  │                                                                  │
  │  504 Gateway Timeout            Backend slow, increase           │
  │                                 proxy_read_timeout               │
  │                                                                  │
  │  403 Forbidden                  File permissions, missing root,  │
  │                                 SELinux context                  │
  │                                                                  │
  │  "no resolver defined"          Add: resolver 127.0.0.53;       │
  │  (dynamic proxy_pass)           when using variables in proxy    │
  │                                                                  │
  │  PHP not executing              php-fpm not running, socket     │
  │                                 permissions, wrong socket path  │
  │                                                                  │
  │  Config test fails              Check: include paths exist,     │
  │                                 brackets matched, semicolons    │
  │                                                                  │
  │  SSL handshake failure          Cert path wrong, key mismatch,  │
  │                                 port 443 not open               │
  └──────────────────────────────────────────────────────────────────┘
```

### Debug Commands

```bash
nginx -t                                # Syntax check
nginx -T                                # Dump full merged config
sudo tail -f /var/log/nginx/error.log   # Live error log
ss -tlnp | grep nginx                   # Listening ports
ps aux | grep nginx                     # Process status

# SELinux (RHEL)
sudo ausearch -m avc -ts recent         # Recent denials
sudo setsebool -P httpd_can_network_connect 1  # Allow proxy
```

---

> **Lab Complete!** You now have hands-on experience with Nginx from basic setup through production configuration.  
> **Next:** Try the [Apache Practice Lab](apache_practice_lab.md) or [IIS Practice Lab](iis_practice_lab.md).

[🏠 Home](../README.md) · [Labs](README.md) · [Nginx Handbook](../servers/nginx.md)
