[🏠 Home](../README.md) · [Labs](README.md) · [Apache Handbook](../servers/apache.md)

# 🪶 Apache HTTP Server — Hands-On Practice Lab

> **Audience:** DevOps / Cloud Engineers & Trainees | **Difficulty:** Beginner → Advanced (progressive)  
> **Time:** 4–6 hours (all exercises) | **Platform:** Linux (RHEL/CentOS or Ubuntu/Debian)  
> **Prerequisites:** Linux CLI basics, a VM or cloud instance with root access  
> **Reference:** [Apache Advanced Configuration Guide](../servers/apache.md)

---

## Table of Contents

1. [Lab Overview](#1-lab-overview)
2. [Lab Environment Setup](#2-lab-environment-setup)
3. [Exercise 1 — Install Apache & Verify (Beginner)](#exercise-1--install-apache--verify-beginner)
4. [Exercise 2 — Name-Based Virtual Hosts (Beginner)](#exercise-2--name-based-virtual-hosts-beginner)
5. [Exercise 3 — Static Site with Caching Headers (Beginner)](#exercise-3--static-site-with-caching-headers-beginner)
6. [Exercise 4 — SPA Hosting with mod_rewrite (Intermediate)](#exercise-4--spa-hosting-with-mod_rewrite-intermediate)
7. [Exercise 5 — Reverse Proxy to Node.js Backend (Intermediate)](#exercise-5--reverse-proxy-to-nodejs-backend-intermediate)
8. [Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)](#exercise-6--ssltls-with-self-signed-certificate-intermediate)
9. [Exercise 7 — PHP-FPM with Event MPM (Intermediate)](#exercise-7--php-fpm-with-event-mpm-intermediate)
10. [Exercise 8 — Load Balancing with mod_proxy_balancer (Advanced)](#exercise-8--load-balancing-with-mod_proxy_balancer-advanced)
11. [Exercise 9 — Security Hardening & Headers (Advanced)](#exercise-9--security-hardening--headers-advanced)
12. [Exercise 10 — Monitoring, Logging & WAF (Advanced)](#exercise-10--monitoring-logging--waf-advanced)
13. [Cleanup](#cleanup)
14. [Troubleshooting Reference](#troubleshooting-reference)

---

## 1. Lab Overview

This lab takes you through **10 progressive exercises** that build on each other, starting from basic Apache installation and ending with production-grade security hardening, load balancing, and WAF configuration.

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                     LAB PROGRESSION                             │
  │                                                                 │
  │  Exercise 1-3:  BEGINNER                                        │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ Install → VirtualHosts → Static Sites + Cache Headers   │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 4-7:  INTERMEDIATE                                    │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ SPA + Rewrite → Reverse Proxy → SSL/TLS → PHP-FPM      │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 8-10: ADVANCED                                        │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ Load Balancing → Security Hardening → Monitoring + WAF  │    │
  │  └──────────────────────────────────────────────────────────┘    │
  └─────────────────────────────────────────────────────────────────┘
```

### What You'll Build

By the end of this lab, your server will look like this:

```
  ┌───────────────────────────────────────────────────────────────────┐
  │                   FINAL LAB ARCHITECTURE                          │
  │                                                                   │
  │  Internet / Clients                                               │
  │       │                                                           │
  │  ┌────▼────────────────────────────────────────────────────┐      │
  │  │  Apache HTTP Server (event MPM)                         │      │
  │  │  :443 (SSL/TLS) + :80 (→ redirect to HTTPS)            │      │
  │  │                                                         │      │
  │  │  ┌─────────────────────────────────────────────────┐    │      │
  │  │  │ VHost: static.lab.local    → Static HTML site   │    │      │
  │  │  │ VHost: app.lab.local       → SPA (React-like)   │    │      │
  │  │  │ VHost: api.lab.local       → Reverse Proxy      │────┼──┐   │
  │  │  │ VHost: php.lab.local       → PHP-FPM            │    │  │   │
  │  │  │ VHost: lb.lab.local        → Load Balancer      │────┼──┤   │
  │  │  └─────────────────────────────────────────────────┘    │  │   │
  │  │                                                         │  │   │
  │  │  mod_security (WAF) + Security Headers                  │  │   │
  │  │  mod_status (Monitoring) + JSON Logging                 │  │   │
  │  └─────────────────────────────────────────────────────────┘  │   │
  │                                                               │   │
  │  ┌────────────────────────────────────────────────────────────┘   │
  │  │  Backend Services                                              │
  │  │  ├── Node.js :3001, :3002, :3003  (load balanced)             │
  │  │  └── PHP-FPM (unix socket)                                     │
  │  └────────────────────────────────────────────────────────────────┘
  └───────────────────────────────────────────────────────────────────┘
```

---

## 2. Lab Environment Setup

### 2.1 Provision a VM

Use any of the following:
- **Cloud:** AWS EC2, DigitalOcean Droplet, Azure VM, GCP Compute
- **Local:** VirtualBox, VMware, Vagrant, Multipass

**Minimum specs:** 1 vCPU, 1 GB RAM, 10 GB disk  
**Recommended OS:** Rocky Linux 9 / AlmaLinux 9 / Ubuntu 22.04 LTS

### 2.2 Set Up Local DNS (hosts file)

On your **local machine** (not the server), add these entries to resolve lab domains:

```bash
# Linux/macOS: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts

# Replace <SERVER_IP> with your VM's IP address
<SERVER_IP>  static.lab.local
<SERVER_IP>  app.lab.local
<SERVER_IP>  api.lab.local
<SERVER_IP>  php.lab.local
<SERVER_IP>  lb.lab.local
```

### 2.3 Initial Server Setup

SSH into the server and prepare the environment:

```bash
# Update system
sudo dnf update -y          # RHEL-family
# sudo apt update && sudo apt upgrade -y   # Debian-family

# Install common tools
sudo dnf install -y curl wget vim tree net-tools bind-utils
# sudo apt install -y curl wget vim tree net-tools dnsutils

# Disable SELinux temporarily for learning (re-enable later in Exercise 9)
# RHEL only:
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
```

> **⚠️ Gotcha:** We disable SELinux initially to avoid permission issues while learning. Exercise 9 will properly configure SELinux for production.

---

## Exercise 1 — Install Apache & Verify (Beginner)

**Objective:** Install Apache, start the service, verify it's running, and understand the file layout.

**Time:** 15 minutes

### Step 1 — Install Apache

```bash
# RHEL/CentOS/Rocky/Alma
sudo dnf install httpd mod_ssl -y

# Ubuntu/Debian
# sudo apt install apache2 -y
```

### Step 2 — Start and Enable

```bash
# RHEL
sudo systemctl enable --now httpd

# Debian
# sudo systemctl enable --now apache2
```

### Step 3 — Open Firewall

```bash
# RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Debian (ufw)
# sudo ufw allow 'Apache Full'
```

### Step 4 — Verify Installation

```bash
# Check version and MPM
httpd -v
httpd -V | grep -i mpm

# Check service status
systemctl status httpd

# Check loaded modules
httpd -M | head -20

# Test from command line
curl -I http://localhost
```

**Expected output:** HTTP/1.1 200 OK with `Server: Apache` header.

### Step 5 — Explore the File Layout

```bash
# RHEL file layout
tree /etc/httpd/ -L 2

# Key files to note:
cat /etc/httpd/conf/httpd.conf | head -30
ls -la /etc/httpd/conf.d/
ls -la /etc/httpd/conf.modules.d/
ls -la /var/www/html/
ls -la /var/log/httpd/
```

### ✅ Verification Checklist

- [ ] `curl -I http://localhost` returns 200
- [ ] `httpd -V | grep mpm` shows `event` (modern default)
- [ ] `systemctl is-enabled httpd` returns `enabled`
- [ ] You can access the default Apache test page from your browser via `http://<SERVER_IP>`

> **⚠️ Gotcha (RHEL):** If you see the default Rocky/Alma test page, that's the welcome.conf in `/etc/httpd/conf.d/`. On Debian, the default page comes from `/var/www/html/index.html`.

---

## Exercise 2 — Name-Based Virtual Hosts (Beginner)

**Objective:** Create two name-based virtual hosts serving different sites on the same IP.

**Time:** 20 minutes

### Architecture

```
  ┌──────────────┐           ┌──────────────────────────────────┐
  │ Browser      │           │ Apache (:80)                     │
  │              │           │                                  │
  │ Host: static │──────────►│ VHost: static.lab.local          │
  │ .lab.local   │           │ → /var/www/static-site/          │
  │              │           │                                  │
  │ Host: app    │──────────►│ VHost: app.lab.local             │
  │ .lab.local   │           │ → /var/www/app-site/             │
  └──────────────┘           └──────────────────────────────────┘
```

### Step 1 — Create Document Roots

```bash
# Create directories
sudo mkdir -p /var/www/static-site
sudo mkdir -p /var/www/app-site

# Create content for static site
sudo tee /var/www/static-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>Static Site</title></head>
<body>
  <h1>🏠 Static Site — static.lab.local</h1>
  <p>This is the static site virtual host.</p>
  <p>Server time: <!--#echo var="DATE_LOCAL" --></p>
</body>
</html>
EOF

# Create content for app site
sudo tee /var/www/app-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>App Site</title></head>
<body>
  <h1>🚀 App Site — app.lab.local</h1>
  <p>This is the application site virtual host.</p>
</body>
</html>
EOF

# Set ownership
sudo chown -R apache:apache /var/www/static-site /var/www/app-site    # RHEL
# sudo chown -R www-data:www-data /var/www/static-site /var/www/app-site  # Debian
```

### Step 2 — Create Virtual Host Configs

```bash
# VHost for static.lab.local
sudo tee /etc/httpd/conf.d/static-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName  static.lab.local
    DocumentRoot /var/www/static-site

    <Directory /var/www/static-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog  /var/log/httpd/static-error.log
    CustomLog /var/log/httpd/static-access.log combined
</VirtualHost>
EOF

# VHost for app.lab.local
sudo tee /etc/httpd/conf.d/app-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName  app.lab.local
    DocumentRoot /var/www/app-site

    <Directory /var/www/app-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    ErrorLog  /var/log/httpd/app-error.log
    CustomLog /var/log/httpd/app-access.log combined
</VirtualHost>
EOF
```

### Step 3 — Test and Reload

```bash
# ALWAYS test config before reload
apachectl configtest

# Check which vhost handles which domain
apachectl -S

# Graceful reload (zero downtime)
sudo apachectl graceful
```

### Step 4 — Verify

```bash
# Test from server using Host header
curl -H "Host: static.lab.local" http://localhost
curl -H "Host: app.lab.local" http://localhost

# The two should return different pages
```

### ✅ Verification Checklist

- [ ] `apachectl configtest` returns `Syntax OK`
- [ ] `apachectl -S` shows both vhosts listed
- [ ] `curl -H "Host: static.lab.local" http://localhost` shows "Static Site"
- [ ] `curl -H "Host: app.lab.local" http://localhost` shows "App Site"
- [ ] Both sites accessible from browser via their domain names

> **⚠️ Gotcha:** If both domains show the same page, check that you don't have a wildcard default vhost taking precedence. The first vhost in load order is the catch-all for unmatched requests.

---

## Exercise 3 — Static Site with Caching Headers (Beginner)

**Objective:** Add proper caching headers, compression, and custom error pages to the static site.

**Time:** 20 minutes

### Step 1 — Enable Required Modules

```bash
# RHEL: Modules are usually loaded by default. Verify:
httpd -M | grep -E "deflate|headers|expires"

# If missing, ensure these lines exist in conf.modules.d/:
# LoadModule deflate_module modules/mod_deflate.so
# LoadModule headers_module modules/mod_headers.so
# LoadModule expires_module modules/mod_expires.so

# Debian:
# sudo a2enmod deflate headers expires
```

### Step 2 — Create Custom Error Pages

```bash
sudo mkdir -p /var/www/static-site/errors

sudo tee /var/www/static-site/errors/404.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>404 — Page Not Found</title></head>
<body>
  <h1>404 — Page Not Found</h1>
  <p>The page you're looking for doesn't exist on static.lab.local.</p>
  <a href="/">Go Home</a>
</body>
</html>
EOF

sudo tee /var/www/static-site/errors/500.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head><title>500 — Server Error</title></head>
<body>
  <h1>500 — Internal Server Error</h1>
  <p>Something went wrong. Please try again later.</p>
</body>
</html>
EOF
```

### Step 3 — Add Caching, Compression & Error Pages to VHost

```bash
sudo tee /etc/httpd/conf.d/static-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName  static.lab.local
    DocumentRoot /var/www/static-site

    <Directory /var/www/static-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    # --- Cache Static Assets ---
    <FilesMatch "\.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$">
        Header set Cache-Control "public, max-age=2592000, immutable"
    </FilesMatch>

    # --- HTML — cache but revalidate ---
    <FilesMatch "\.(html|htm)$">
        Header set Cache-Control "public, max-age=3600, must-revalidate"
    </FilesMatch>

    # --- Compression ---
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/css
        AddOutputFilterByType DEFLATE application/javascript application/json
        AddOutputFilterByType DEFLATE image/svg+xml
    </IfModule>

    # --- Custom Error Pages ---
    ErrorDocument 404 /errors/404.html
    ErrorDocument 500 /errors/500.html

    # --- Deny Hidden Files ---
    <FilesMatch "^\.">
        Require all denied
    </FilesMatch>

    ErrorLog  /var/log/httpd/static-error.log
    CustomLog /var/log/httpd/static-access.log combined
</VirtualHost>
EOF
```

### Step 4 — Test and Verify

```bash
apachectl configtest && sudo apachectl graceful

# Test caching headers
curl -I -H "Host: static.lab.local" http://localhost/
# Should show: Cache-Control: public, max-age=3600, must-revalidate

# Test 404 custom page
curl -H "Host: static.lab.local" http://localhost/nonexistent-page
# Should show your custom 404 page content

# Test compression
curl -H "Host: static.lab.local" -H "Accept-Encoding: gzip" -I http://localhost/
# Should show: Content-Encoding: gzip (if response is large enough)
```

### ✅ Verification Checklist

- [ ] Response headers show `Cache-Control` directives
- [ ] `/nonexistent-page` returns your custom 404 HTML
- [ ] Gzip encoding is present for text content
- [ ] Hidden files (e.g., `.git`) return 403 Forbidden

---

## Exercise 4 — SPA Hosting with mod_rewrite (Intermediate)

**Objective:** Configure Apache to serve a Single Page Application (React/Vue/Angular) with client-side routing.

**Time:** 20 minutes

### Architecture

```
  Client requests /about, /dashboard, /settings
  ┌──────────────────────────────────────────────────────────────┐
  │  Apache checks:                                              │
  │  1. Does /var/www/app-site/about exist as a file? → No      │
  │  2. Does /var/www/app-site/about/ exist as directory? → No  │
  │  3. Fallback: serve /var/www/app-site/index.html            │
  │     (JavaScript router handles the URL on the client side)   │
  └──────────────────────────────────────────────────────────────┘
```

### Step 1 — Enable mod_rewrite

```bash
# RHEL: verify it's loaded
httpd -M | grep rewrite
# If not, ensure LoadModule is present in conf.modules.d/

# Debian:
# sudo a2enmod rewrite
```

### Step 2 — Create SPA Content

```bash
# Simulate a built SPA with multiple "pages"
sudo mkdir -p /var/www/app-site/static/js
sudo mkdir -p /var/www/app-site/static/css

# Main SPA index
sudo tee /var/www/app-site/index.html > /dev/null << 'EOF'
<!DOCTYPE html>
<html>
<head>
  <title>SPA App</title>
  <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
  <nav>
    <a href="/">Home</a> |
    <a href="/about">About</a> |
    <a href="/dashboard">Dashboard</a>
  </nav>
  <div id="app">
    <h1>🚀 SPA Application — app.lab.local</h1>
    <p>Current URL: <span id="url"></span></p>
    <p>This SPA uses client-side routing. All routes serve this index.html.</p>
  </div>
  <script>
    document.getElementById('url').textContent = window.location.pathname;
  </script>
</body>
</html>
EOF

# CSS file
sudo tee /var/www/app-site/static/css/app.css > /dev/null << 'EOF'
body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
nav { background: #333; padding: 10px; }
nav a { color: white; margin: 0 10px; text-decoration: none; }
EOF

sudo chown -R apache:apache /var/www/app-site
```

### Step 3 — Configure SPA VHost with Rewrite

```bash
sudo tee /etc/httpd/conf.d/app-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName  app.lab.local
    DocumentRoot /var/www/app-site

    <Directory /var/www/app-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted

        # SPA fallback — serve index.html for all non-file routes
        RewriteEngine On
        RewriteBase /

        # If the requested file exists, serve it directly
        RewriteCond %{REQUEST_FILENAME} !-f
        # If the requested directory exists, serve it directly
        RewriteCond %{REQUEST_FILENAME} !-d
        # Otherwise, serve index.html (SPA client-side routing)
        RewriteRule . /index.html [L]
    </Directory>

    # Cache static assets aggressively
    <FilesMatch "\.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$">
        Header set Cache-Control "public, max-age=2592000, immutable"
    </FilesMatch>

    ErrorLog  /var/log/httpd/app-error.log
    CustomLog /var/log/httpd/app-access.log combined
</VirtualHost>
EOF
```

### Step 4 — Test SPA Routing

```bash
apachectl configtest && sudo apachectl graceful

# These should ALL return the same index.html content:
curl -H "Host: app.lab.local" http://localhost/
curl -H "Host: app.lab.local" http://localhost/about
curl -H "Host: app.lab.local" http://localhost/dashboard
curl -H "Host: app.lab.local" http://localhost/any/deep/route

# But static files should be served directly:
curl -I -H "Host: app.lab.local" http://localhost/static/css/app.css
# Should return 200 with CSS content-type
```

### ✅ Verification Checklist

- [ ] `/about`, `/dashboard`, `/any/route` all return the SPA index.html
- [ ] `/static/css/app.css` returns the actual CSS file (not index.html)
- [ ] CSS files have `Cache-Control: public, max-age=2592000, immutable` header

> **⚠️ Gotcha:** If rewrite rules don't work, check that `mod_rewrite` is loaded (`httpd -M | grep rewrite`). On RHEL, it's usually pre-loaded. On Debian, you must run `a2enmod rewrite`.

---

## Exercise 5 — Reverse Proxy to Node.js Backend (Intermediate)

**Objective:** Set up Apache as a reverse proxy to a Node.js API backend.

**Time:** 30 minutes

### Architecture

```
  Client → Apache (:80) → Node.js (:3001)
  ┌──────────────┐     ┌─────────────────┐     ┌────────────────┐
  │  Browser     │────►│ Apache          │────►│ Node.js        │
  │              │     │ api.lab.local   │     │ localhost:3001  │
  │              │◄────│ (reverse proxy) │◄────│ (JSON API)     │
  └──────────────┘     └─────────────────┘     └────────────────┘
```

### Step 1 — Install Node.js

```bash
# RHEL/CentOS
sudo dnf install -y nodejs npm

# Verify
node -v
npm -v
```

### Step 2 — Create a Simple API Backend

```bash
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
  console.log(`API server running on http://127.0.0.1:${PORT} (PID: ${process.pid})`);
});
JSEOF

# Start the backend
cd /opt/api-backend
node server.js &

# Verify it's running
curl http://127.0.0.1:3001/
```

### Step 3 — Enable Proxy Modules

```bash
# RHEL: verify proxy modules are loaded
httpd -M | grep proxy

# You need at minimum:
# proxy_module, proxy_http_module
# These are usually loaded by default on RHEL

# Debian:
# sudo a2enmod proxy proxy_http headers
```

### Step 4 — Create Reverse Proxy VHost

```bash
sudo tee /etc/httpd/conf.d/api-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName api.lab.local

    # CRITICAL: Prevent Apache from being used as a forward proxy
    ProxyRequests Off

    # Preserve the original Host header
    ProxyPreserveHost On

    # Proxy all requests to Node.js backend
    ProxyPass        / http://127.0.0.1:3001/
    ProxyPassReverse / http://127.0.0.1:3001/

    # Forward client information to backend
    RequestHeader set X-Real-IP "%{REMOTE_ADDR}e"
    RequestHeader set X-Forwarded-Proto "%{REQUEST_SCHEME}e"

    # Timeouts
    ProxyTimeout 60

    ErrorLog  /var/log/httpd/api-error.log
    CustomLog /var/log/httpd/api-access.log combined
</VirtualHost>
EOF
```

### Step 5 — Test Reverse Proxy

```bash
apachectl configtest && sudo apachectl graceful

# Test through the proxy
curl -s -H "Host: api.lab.local" http://localhost/ | python3 -m json.tool

# You should see:
# - "host": "api.lab.local" (ProxyPreserveHost worked)
# - "x-real-ip": "127.0.0.1" (your IP forwarded)
# - "x-forwarded-proto": "http"

# Test different paths
curl -s -H "Host: api.lab.local" http://localhost/users | python3 -m json.tool
curl -s -H "Host: api.lab.local" http://localhost/api/v1/data | python3 -m json.tool
```

### ✅ Verification Checklist

- [ ] `curl -H "Host: api.lab.local" http://localhost/` returns JSON from Node.js
- [ ] Response shows `x-real-ip` is populated (not "not set")
- [ ] Response shows `host` is `api.lab.local` (not `127.0.0.1:3001`)
- [ ] All URL paths are passed through correctly

> **⚠️ Gotcha (RHEL/SELinux):** If you get a 503 error with SELinux enforcing, run:
> ```bash
> sudo setsebool -P httpd_can_network_connect 1
> ```
> This is the #1 trap for reverse proxy on RHEL/CentOS.

---

## Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)

**Objective:** Generate a self-signed certificate and configure HTTPS with HTTP→HTTPS redirect.

**Time:** 25 minutes

### Architecture

```
  ┌──────────────┐      ┌─────────────────────────────────────────┐
  │  Browser     │      │  Apache                                 │
  │              │      │                                         │
  │ http://      │──────│──► :80 VHost ──► 301 Redirect to HTTPS  │
  │ static.lab   │      │                                         │
  │              │──────│──► :443 VHost ──► Serve static content   │
  │ https://     │      │      (SSL termination)                  │
  └──────────────┘      └─────────────────────────────────────────┘
```

### Step 1 — Generate Self-Signed Certificate

```bash
# Create certificate directory
sudo mkdir -p /etc/httpd/ssl

# Generate private key + self-signed cert (valid 365 days)
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/httpd/ssl/lab.key \
  -out /etc/httpd/ssl/lab.crt \
  -subj "/C=IN/ST=Gujarat/L=Ahmedabad/O=Lab/CN=*.lab.local"

# Verify certificate
openssl x509 -in /etc/httpd/ssl/lab.crt -text -noout | head -15

# Set proper permissions
sudo chmod 600 /etc/httpd/ssl/lab.key
sudo chmod 644 /etc/httpd/ssl/lab.crt
```

### Step 2 — Ensure mod_ssl is Loaded

```bash
# RHEL: mod_ssl was installed in Exercise 1
httpd -M | grep ssl

# If not installed:
# sudo dnf install mod_ssl -y

# Debian:
# sudo a2enmod ssl
```

### Step 3 — Update Static Site VHost for HTTPS

```bash
sudo tee /etc/httpd/conf.d/static-site.conf > /dev/null << 'EOF'
# --- HTTP → HTTPS Redirect ---
<VirtualHost *:80>
    ServerName static.lab.local
    Redirect permanent / https://static.lab.local/
</VirtualHost>

# --- HTTPS VHost ---
<VirtualHost *:443>
    ServerName static.lab.local
    DocumentRoot /var/www/static-site

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile    /etc/httpd/ssl/lab.crt
    SSLCertificateKeyFile /etc/httpd/ssl/lab.key

    # Protocol & Cipher Hardening
    SSLProtocol           all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLHonorCipherOrder   on
    SSLCipherSuite        ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLCompression        off

    # HSTS Header
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains"

    <Directory /var/www/static-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    <FilesMatch "\.(css|js|jpg|jpeg|png|gif|ico|svg|woff2?)$">
        Header set Cache-Control "public, max-age=2592000, immutable"
    </FilesMatch>

    ErrorDocument 404 /errors/404.html
    ErrorDocument 500 /errors/500.html

    <FilesMatch "^\.">
        Require all denied
    </FilesMatch>

    ErrorLog  /var/log/httpd/static-ssl-error.log
    CustomLog /var/log/httpd/static-ssl-access.log combined
</VirtualHost>
EOF
```

### Step 4 — Handle Default ssl.conf Conflict

```bash
# RHEL: The default ssl.conf has a *:443 VHost that may conflict
# Option 1: Rename it
sudo mv /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/ssl.conf.bak

# Option 2: Or comment out the <VirtualHost> block in ssl.conf
# and keep only the global SSL settings
```

### Step 5 — Test

```bash
apachectl configtest && sudo apachectl graceful

# Test HTTP redirect
curl -I -H "Host: static.lab.local" http://localhost/
# Should return: 301 Moved Permanently → https://static.lab.local/

# Test HTTPS (use -k to skip cert verification for self-signed)
curl -k -I https://localhost/ -H "Host: static.lab.local"
# Should return: 200 OK with Strict-Transport-Security header

# Check SSL details
openssl s_client -connect localhost:443 -servername static.lab.local < /dev/null 2>/dev/null | head -20
```

### ✅ Verification Checklist

- [ ] HTTP requests redirect to HTTPS (301)
- [ ] HTTPS serves the static site with 200
- [ ] `Strict-Transport-Security` header is present
- [ ] `openssl s_client` shows TLS 1.2 or 1.3
- [ ] No SSLv3/TLS 1.0/1.1 is offered

> **⚠️ Gotcha:** On RHEL, the default `/etc/httpd/conf.d/ssl.conf` defines a catch-all `*:443` VHost. If you don't rename/edit it, it will conflict with your custom HTTPS VHost. Always check `apachectl -S` to verify vhost routing.

---

## Exercise 7 — PHP-FPM with Event MPM (Intermediate)

**Objective:** Set up PHP processing with PHP-FPM (not mod_php) to maintain the efficient event MPM.

**Time:** 25 minutes

### Architecture

```
  ┌──────────────────────────────────────────────────────────────┐
  │  Apache (event MPM)                                          │
  │                                                              │
  │  Request for *.php ──► mod_proxy_fcgi ──► PHP-FPM (socket)   │
  │  Request for *.html ──► Direct serve from DocumentRoot       │
  │                                                              │
  │  Key: PHP runs in a SEPARATE process pool (not inside Apache)│
  └──────────────────────────────────────────────────────────────┘
```

### Step 1 — Install PHP-FPM

```bash
# RHEL
sudo dnf install php-fpm php-cli php-json php-mbstring -y

# Debian
# sudo apt install php-fpm php-cli php-json php-mbstring -y
```

### Step 2 — Configure PHP-FPM Pool

```bash
# Check the default pool config
cat /etc/php-fpm.d/www.conf | grep -E "^(listen|user|group)" 

# Key settings to verify:
# listen = /run/php-fpm/www.sock  (RHEL)
# listen.owner = apache
# listen.group = apache
# user = apache
# group = apache

# Debian: socket is /run/php/phpX.X-fpm.sock, user/group = www-data
```

### Step 3 — Start PHP-FPM

```bash
sudo systemctl enable --now php-fpm

# Verify
systemctl status php-fpm
ls -la /run/php-fpm/www.sock     # Should exist and be owned by apache
```

### Step 4 — Enable Required Apache Modules

```bash
# RHEL: verify
httpd -M | grep -E "proxy_fcgi|setenvif"

# These should be loaded by default
# If not, ensure LoadModule lines exist

# Debian:
# sudo a2enmod proxy_fcgi setenvif
```

### Step 5 — Create PHP Site Content

```bash
sudo mkdir -p /var/www/php-site

# PHP info page
sudo tee /var/www/php-site/index.php > /dev/null << 'PHPEOF'
<?php
echo "<h1>🐘 PHP Site — php.lab.local</h1>";
echo "<p>PHP Version: " . phpversion() . "</p>";
echo "<p>Server API: " . php_sapi_name() . "</p>";
echo "<p>Server Time: " . date('Y-m-d H:i:s') . "</p>";
echo "<p>Server Software: " . $_SERVER['SERVER_SOFTWARE'] . "</p>";
echo "<hr>";
echo "<h2>Request Headers (from Apache):</h2>";
echo "<pre>";
foreach ($_SERVER as $key => $value) {
    if (strpos($key, 'HTTP_') === 0 || strpos($key, 'SERVER_') === 0) {
        echo htmlspecialchars("$key: $value") . "\n";
    }
}
echo "</pre>";
?>
PHPEOF

# phpinfo page (useful for debugging)
sudo tee /var/www/php-site/info.php > /dev/null << 'PHPEOF'
<?php phpinfo(); ?>
PHPEOF

sudo chown -R apache:apache /var/www/php-site
```

### Step 6 — Create PHP VHost

```bash
sudo tee /etc/httpd/conf.d/php-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName php.lab.local
    DocumentRoot /var/www/php-site

    <Directory /var/www/php-site>
        Options -Indexes +FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    # Route PHP files to FPM via unix socket
    <FilesMatch \.php$>
        SetHandler "proxy:unix:/run/php-fpm/www.sock|fcgi://localhost"
    </FilesMatch>

    DirectoryIndex index.php index.html

    ErrorLog  /var/log/httpd/php-error.log
    CustomLog /var/log/httpd/php-access.log combined
</VirtualHost>
EOF
```

### Step 7 — Test

```bash
apachectl configtest && sudo apachectl graceful

# Test PHP processing
curl -H "Host: php.lab.local" http://localhost/
# Should show PHP version and server info

# Test phpinfo
curl -H "Host: php.lab.local" http://localhost/info.php | head -20
# Should show HTML output from phpinfo()

# Verify event MPM is still active (NOT prefork)
httpd -V | grep -i mpm
# Must show: event
```

### ✅ Verification Checklist

- [ ] PHP pages execute and show PHP version
- [ ] `php_sapi_name()` shows `fpm-fcgi` (NOT `apache2handler`)
- [ ] `httpd -V | grep mpm` still shows `event` (not prefork)
- [ ] `/info.php` shows full phpinfo output
- [ ] PHP-FPM socket exists at `/run/php-fpm/www.sock`

> **⚠️ Gotcha:** If you accidentally install `mod_php` (the `php` package on RHEL without `-fpm`), it will force Apache to switch to prefork MPM. Always use `php-fpm` package and verify MPM after installation.

---

## Exercise 8 — Load Balancing with mod_proxy_balancer (Advanced)

**Objective:** Set up Apache as a load balancer across multiple Node.js backends with health monitoring.

**Time:** 30 minutes

### Architecture

```
  ┌──────────────┐     ┌─────────────────────────┐     ┌────────────┐
  │  Browser     │────►│  Apache (Load Balancer)  │──┬─►│ Node :3001 │
  │              │     │  lb.lab.local            │  │  └────────────┘
  │              │◄────│                          │  │  ┌────────────┐
  └──────────────┘     │  mod_proxy_balancer      │──┼─►│ Node :3002 │
                       │  byrequests (round robin) │  │  └────────────┘
                       │  + balancer-manager       │  │  ┌────────────┐
                       └─────────────────────────┘  └─►│ Node :3003 │
                                                       └────────────┘
```

### Step 1 — Start Multiple Node.js Backends

```bash
# Start 3 backend instances on different ports
cd /opt/api-backend

# Kill any existing instance
pkill -f "node server.js" 2>/dev/null

# Start 3 instances
PORT=3001 node server.js &
PORT=3002 node server.js &
PORT=3003 node server.js &

# Verify all are running
sleep 1
curl -s http://127.0.0.1:3001/ | python3 -c "import sys,json; print('Port 3001: PID', json.load(sys.stdin)['pid'])"
curl -s http://127.0.0.1:3002/ | python3 -c "import sys,json; print('Port 3002: PID', json.load(sys.stdin)['pid'])"
curl -s http://127.0.0.1:3003/ | python3 -c "import sys,json; print('Port 3003: PID', json.load(sys.stdin)['pid'])"
```

### Step 2 — Enable Balancer Modules

```bash
# Verify required modules
httpd -M | grep -E "proxy_balancer|lbmethod|slotmem"

# You need: proxy_balancer_module, lbmethod_byrequests_module, slotmem_shm_module
# These are typically loaded by default on RHEL
```

### Step 3 — Create Load Balancer VHost

```bash
sudo tee /etc/httpd/conf.d/lb-site.conf > /dev/null << 'EOF'
<VirtualHost *:80>
    ServerName lb.lab.local

    ProxyRequests Off
    ProxyPreserveHost On

    # Define backend pool
    <Proxy "balancer://nodepool">
        BalancerMember http://127.0.0.1:3001 route=node1 loadfactor=1
        BalancerMember http://127.0.0.1:3002 route=node2 loadfactor=1
        BalancerMember http://127.0.0.1:3003 route=node3 loadfactor=1

        # Load balancing method (round robin by default)
        ProxySet lbmethod=byrequests

        # Health check: mark failed after 3 errors, retry after 10s
        ProxySet failontimeout=on
    </Proxy>

    # Route all requests to the pool
    ProxyPass        / balancer://nodepool/
    ProxyPassReverse / balancer://nodepool/

    # Forward client info
    RequestHeader set X-Real-IP "%{REMOTE_ADDR}e"
    RequestHeader set X-Forwarded-Proto "%{REQUEST_SCHEME}e"

    # --- Balancer Manager (monitoring dashboard) ---
    <Location "/balancer-manager">
        SetHandler balancer-manager
        Require ip 127.0.0.1
        # In production, restrict to internal IPs only
    </Location>

    ErrorLog  /var/log/httpd/lb-error.log
    CustomLog /var/log/httpd/lb-access.log combined
</VirtualHost>
EOF
```

### Step 4 — Test Load Balancing

```bash
apachectl configtest && sudo apachectl graceful

# Send multiple requests — observe the PID/port changing (round robin)
for i in {1..6}; do
  echo "--- Request $i ---"
  curl -s -H "Host: lb.lab.local" http://localhost/ | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Port: {d[\"port\"]}, PID: {d[\"pid\"]}')"
done

# Expected output: ports cycle through 3001, 3002, 3003, 3001, 3002, 3003
```

### Step 5 — Test Failover

```bash
# Kill one backend
kill $(lsof -ti:3002) 2>/dev/null

# Send requests — should still work (only 3001 and 3003 respond)
for i in {1..4}; do
  curl -s -H "Host: lb.lab.local" http://localhost/ | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Port: {d[\"port\"]}')" 2>/dev/null || echo "Error on request $i"
done

# Restart the killed backend
PORT=3002 node /opt/api-backend/server.js &
```

### Step 6 — Access Balancer Manager

```bash
# View the balancer manager dashboard
curl -s -H "Host: lb.lab.local" http://localhost/balancer-manager | head -50

# In a browser (from the server): http://lb.lab.local/balancer-manager
# Shows: member status, request count, load factor, enable/disable controls
```

### ✅ Verification Checklist

- [ ] Requests are distributed across all 3 backends (ports cycle)
- [ ] When one backend is killed, requests still succeed on remaining backends
- [ ] `/balancer-manager` shows the dashboard with member status
- [ ] After restarting a killed backend, it rejoins the pool

> **⚠️ Gotcha:** `ProxyPass` ordering matters — the `/balancer-manager` Location must be defined or Apache must evaluate it before the catch-all `ProxyPass /`. Since we use `<Location>` blocks, longest-match applies and it works. If you used bare `ProxyPass` directives, `/balancer-manager` would be swallowed by `ProxyPass /`.

---

## Exercise 9 — Security Hardening & Headers (Advanced)

**Objective:** Apply production-level security hardening including server hiding, security headers, SELinux, and path restrictions.

**Time:** 30 minutes

### Step 1 — Hide Server Information

```bash
# Add to main httpd.conf
sudo tee -a /etc/httpd/conf/httpd.conf > /dev/null << 'EOF'

# --- Security Hardening ---
ServerTokens Prod
ServerSignature Off
TraceEnable Off
EOF
```

### Step 2 — Add Global Security Headers

```bash
sudo tee /etc/httpd/conf.d/security-headers.conf > /dev/null << 'EOF'
# Global Security Headers — applied to ALL vhosts
<IfModule mod_headers.c>
    # Prevent clickjacking
    Header always set X-Frame-Options "SAMEORIGIN"

    # Prevent MIME-type sniffing
    Header always set X-Content-Type-Options "nosniff"

    # Referrer policy
    Header always set Referrer-Policy "strict-origin-when-cross-origin"

    # Permissions Policy
    Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"

    # Remove server identity headers
    Header always unset X-Powered-By
    Header unset ETag
</IfModule>

FileETag None
EOF
```

### Step 3 — Block Sensitive Paths

```bash
sudo tee /etc/httpd/conf.d/security-paths.conf > /dev/null << 'EOF'
# Block hidden files and directories (.git, .env, .svn, etc.)
<DirectoryMatch "^\.|\/\.">
    Require all denied
</DirectoryMatch>

# Block backup/temp files
<FilesMatch "\.(bak|old|orig|save|tmp|swp|sql|gz|tar)$">
    Require all denied
</FilesMatch>

# Block common sensitive files
<FilesMatch "^(wp-config\.php|\.env|\.htpasswd|composer\.json|package\.json)$">
    Require all denied
</FilesMatch>
EOF
```

### Step 4 — Configure SELinux (RHEL Only)

```bash
# Re-enable SELinux
sudo setenforce 1
sudo sed -i 's/SELINUX=permissive/SELINUX=enforcing/' /etc/selinux/config

# Set correct file contexts
sudo restorecon -Rv /var/www/
sudo restorecon -Rv /etc/httpd/

# Allow Apache to make network connections (for reverse proxy)
sudo setsebool -P httpd_can_network_connect 1

# Allow Apache to connect to databases (if needed)
# sudo setsebool -P httpd_can_network_connect_db 1

# Verify
getsebool -a | grep httpd | grep "on$"
```

### Step 5 — Test Security

```bash
apachectl configtest && sudo apachectl graceful

# Test server header hiding
curl -I -H "Host: static.lab.local" -k https://localhost/
# Should show: Server: Apache (no version)
# Should NOT show: X-Powered-By

# Test security headers
curl -I -H "Host: static.lab.local" -k https://localhost/ 2>/dev/null | grep -E "X-Frame|X-Content|Referrer|Permissions"

# Test sensitive path blocking
curl -I -H "Host: static.lab.local" -k https://localhost/.git/config
# Should return 403

curl -I -H "Host: static.lab.local" -k https://localhost/.env
# Should return 403

# Test TRACE method is disabled
curl -X TRACE -H "Host: static.lab.local" -k https://localhost/
# Should return 405 Method Not Allowed
```

### ✅ Verification Checklist

- [ ] Server header shows only "Apache" (no version number)
- [ ] X-Frame-Options, X-Content-Type-Options headers present
- [ ] `.git`, `.env`, `.bak` files return 403
- [ ] TRACE method returns 405
- [ ] SELinux is enforcing and Apache still works
- [ ] Reverse proxy still functions with SELinux enabled

---

## Exercise 10 — Monitoring, Logging & WAF (Advanced)

**Objective:** Set up JSON structured logging, mod_status monitoring, and mod_security WAF.

**Time:** 30 minutes

### Step 1 — JSON Structured Logging

```bash
# Add JSON log format to httpd.conf
sudo tee /etc/httpd/conf.d/logging.conf > /dev/null << 'EOF'
# JSON log format for log aggregation (ELK, Loki, Datadog)
LogFormat "{ \"time\":\"%{%Y-%m-%dT%H:%M:%S%z}t\", \"remote_ip\":\"%a\", \"host\":\"%V\", \"request_method\":\"%m\", \"request_uri\":\"%U\", \"query\":\"%q\", \"status\":%>s, \"bytes_sent\":%B, \"duration_us\":%D, \"referer\":\"%{Referer}i\", \"user_agent\":\"%{User-Agent}i\" }" json_combined

# Apply JSON logging to all vhosts (or per-vhost)
# CustomLog /var/log/httpd/access-json.log json_combined
EOF
```

### Step 2 — Enable mod_status

```bash
# Ensure mod_status is loaded
httpd -M | grep status

sudo tee /etc/httpd/conf.d/server-status.conf > /dev/null << 'EOF'
# Server Status Dashboard
ExtendedStatus On

<Location /server-status>
    SetHandler server-status
    # Restrict to localhost and internal IPs only
    Require ip 127.0.0.1
    Require ip 10.0.0.0/8
    Require ip 192.168.0.0/16
</Location>

# Machine-readable endpoint for monitoring tools
# Access: http://localhost/server-status?auto
EOF
```

### Step 3 — Test Monitoring

```bash
apachectl configtest && sudo apachectl graceful

# View server status
curl http://localhost/server-status?auto

# Key metrics to look for:
# BusyWorkers, IdleWorkers, Total Accesses, Total kBytes
# Scoreboard: each character represents a worker slot
```

### Step 4 — Install mod_security (WAF)

```bash
# RHEL
sudo dnf install mod_security mod_security_crs -y

# Debian
# sudo apt install libapache2-mod-security2 modsecurity-crs -y
```

### Step 5 — Configure mod_security

```bash
# RHEL: mod_security config is at /etc/httpd/conf.d/mod_security.conf
# The CRS rules are at /etc/httpd/modsecurity.d/

# Verify it's loaded
httpd -M | grep security

# Test with a SQL injection attempt
apachectl configtest && sudo apachectl graceful

curl -H "Host: static.lab.local" "http://localhost/?id=1%20OR%201=1"
# With mod_security active, this should return 403 Forbidden

curl -H "Host: static.lab.local" "http://localhost/?param=<script>alert(1)</script>"
# XSS attempt — should also be blocked
```

### Step 6 — Check WAF Audit Logs

```bash
# mod_security audit log
sudo tail -20 /var/log/httpd/modsec_audit.log

# Look for lines like:
# [id "941100"] [msg "XSS Attack Detected via libinjection"]
# [id "942100"] [msg "SQL Injection Attack Detected via libinjection"]
```

### ✅ Verification Checklist

- [ ] `/server-status?auto` returns Apache metrics
- [ ] JSON logging format produces valid JSON in log file
- [ ] mod_security blocks SQL injection attempts (403)
- [ ] mod_security blocks XSS attempts (403)
- [ ] Audit log shows blocked attack details
- [ ] Legitimate requests still pass through normally

---

## Cleanup

When you're done with the lab, clean up:

```bash
# Stop Node.js backends
pkill -f "node server.js"

# Stop services
sudo systemctl stop httpd
sudo systemctl stop php-fpm

# Remove lab configs (optional)
sudo rm -f /etc/httpd/conf.d/{static-site,app-site,api-site,php-site,lb-site}.conf
sudo rm -f /etc/httpd/conf.d/{security-headers,security-paths,logging,server-status}.conf
sudo rm -rf /var/www/{static-site,app-site,php-site}
sudo rm -rf /opt/api-backend
sudo rm -rf /etc/httpd/ssl
```

---

## Troubleshooting Reference

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  COMMON ISSUES & FIXES                                           │
  │                                                                  │
  │  Problem                        Fix                              │
  │  ─────────────────────────────  ───────────────────────────────  │
  │  403 Forbidden                  Check: permissions, <Directory>, │
  │                                 SELinux (restorecon), Require    │
  │                                                                  │
  │  503 Service Unavailable        SELinux: setsebool -P            │
  │  (reverse proxy)               httpd_can_network_connect 1       │
  │                                                                  │
  │  500 Internal Server Error      Check: error_log, config syntax  │
  │                                 apachectl configtest             │
  │                                                                  │
  │  Wrong site served              apachectl -S to see vhost map    │
  │                                 Check ServerName + load order    │
  │                                                                  │
  │  PHP not executing              Check: php-fpm running,          │
  │                                 socket permissions, SetHandler   │
  │                                                                  │
  │  SSL handshake failure          Check: cert paths, ssl.conf      │
  │                                 conflict, port 443 open          │
  │                                                                  │
  │  Rewrite rules not working      Check: mod_rewrite loaded,       │
  │                                 RewriteEngine On, log rewrite:   │
  │                                 trace3                           │
  └──────────────────────────────────────────────────────────────────┘
```

### Debug Commands Cheat Sheet

```bash
# Config verification
apachectl configtest                   # Syntax check
apachectl -S                           # VHost mapping
apachectl -M                           # Loaded modules

# Log viewing
sudo tail -f /var/log/httpd/error_log  # Live error log
sudo tail -f /var/log/httpd/*-error.log # Per-vhost errors

# Process info
ps aux | grep httpd | head -10         # Running processes
ss -tlnp | grep -E ":80|:443"         # Listening ports

# SELinux debugging (RHEL)
sudo ausearch -m avc -ts recent        # Recent SELinux denials
sudo sealert -a /var/log/audit/audit.log # Human-readable explanations

# Rewrite debugging
# Add to vhost: LogLevel warn rewrite:trace3
sudo tail -f /var/log/httpd/error_log | grep rewrite
```

---

> **Lab Complete!** You now have hands-on experience with Apache from basic installation through production-grade security.  
> **Next:** Try the [Nginx Practice Lab](nginx_practice_lab.md) or [IIS Practice Lab](iis_practice_lab.md).

[🏠 Home](../README.md) · [Labs](README.md) · [Apache Handbook](../servers/apache.md)
