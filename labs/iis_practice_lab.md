[🏠 Home](../README.md) · [Labs](README.md) · [IIS Handbook](../servers/iis.md)

# 🪟 IIS — Hands-On Practice Lab

> **Audience:** DevOps / Cloud Engineers & Trainees | **Difficulty:** Beginner → Advanced (progressive)  
> **Time:** 4–6 hours (all exercises) | **Platform:** Windows Server 2019/2022  
> **Prerequisites:** Windows Server basics, PowerShell familiarity, Remote Desktop or local console access  
> **Reference:** [IIS Advanced Configuration Guide](../servers/iis.md)

---

## Table of Contents

1. [Lab Overview](#1-lab-overview)
2. [Lab Environment Setup](#2-lab-environment-setup)
3. [Exercise 1 — Install IIS & Verify (Beginner)](#exercise-1--install-iis--verify-beginner)
4. [Exercise 2 — Sites, Bindings & Host Headers (Beginner)](#exercise-2--sites-bindings--host-headers-beginner)
5. [Exercise 3 — Static Site with Compression & Caching (Beginner)](#exercise-3--static-site-with-compression--caching-beginner)
6. [Exercise 4 — Application Pools Deep Dive (Intermediate)](#exercise-4--application-pools-deep-dive-intermediate)
7. [Exercise 5 — URL Rewrite & SPA Hosting (Intermediate)](#exercise-5--url-rewrite--spa-hosting-intermediate)
8. [Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)](#exercise-6--ssltls-with-self-signed-certificate-intermediate)
9. [Exercise 7 — Reverse Proxy with ARR (Intermediate)](#exercise-7--reverse-proxy-with-arr-intermediate)
10. [Exercise 8 — Load Balancing with ARR Server Farms (Advanced)](#exercise-8--load-balancing-with-arr-server-farms-advanced)
11. [Exercise 9 — Security Hardening & Request Filtering (Advanced)](#exercise-9--security-hardening--request-filtering-advanced)
12. [Exercise 10 — FREB Diagnostics, Monitoring & Docker (Advanced)](#exercise-10--freb-diagnostics-monitoring--docker-advanced)
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
  │  │ Install → Sites/Bindings → Static + Compression + Cache │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 4-7:  INTERMEDIATE                                    │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ App Pools → URL Rewrite/SPA → SSL/TLS → ARR Proxy      │    │
  │  └──────────────────────────────────────────────────────────┘    │
  │                          │                                      │
  │  Exercise 8-10: ADVANCED                                        │
  │  ┌──────────────────────────────────────────────────────────┐    │
  │  │ ARR Load Balancing → Security Hardening → FREB + Docker │    │
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
  │  │  HTTP.sys  (Kernel-mode listener)                       │      │
  │  │  :80 / :443 (TLS termination in kernel)                 │      │
  │  └────┬────────────────────────────────────────────────────┘      │
  │       │                                                           │
  │  ┌────▼────────────────────────────────────────────────────┐      │
  │  │  IIS  (W3SVC → Application Pools → Worker Processes)    │      │
  │  │                                                         │      │
  │  │  ┌─────────────────────────────────────────────────┐    │      │
  │  │  │ Site: static.lab.local  → Static HTML site      │    │      │
  │  │  │ Site: app.lab.local     → SPA (URL Rewrite)     │    │      │
  │  │  │ Site: api.lab.local     → ARR Reverse Proxy     │────┼──┐   │
  │  │  │ Site: lb.lab.local      → ARR Load Balancer     │────┼──┤   │
  │  │  └─────────────────────────────────────────────────┘    │  │   │
  │  │                                                         │  │   │
  │  │  Compression + Output Caching + Request Filtering       │  │   │
  │  │  FREB Tracing + Custom Logging + Health Check           │  │   │
  │  └─────────────────────────────────────────────────────────┘  │   │
  │                                                               │   │
  │  ┌────────────────────────────────────────────────────────────┘   │
  │  │  Backend Services                                              │
  │  │  ├── Node.js :3001, :3002, :3003  (ARR server farm)           │
  │  │  └── ASP.NET Core / PHP (managed by separate App Pools)       │
  │  └────────────────────────────────────────────────────────────────┘
  └───────────────────────────────────────────────────────────────────┘
```

---

## 2. Lab Environment Setup

### 2.1 Provision a VM

- **Cloud:** AWS EC2 (Windows Server 2022 AMI), Azure VM, GCP
- **Local:** VirtualBox, VMware, Hyper-V
- **Image:** Windows Server 2022 Standard (Desktop Experience recommended for learning)

**Minimum specs:** 2 vCPU, 4 GB RAM, 40 GB disk

### 2.2 Set Up Local DNS

On your **local machine** (not the server):

```
# Windows: C:\Windows\System32\drivers\etc\hosts  (edit as Administrator)
# Linux/macOS: /etc/hosts

<SERVER_IP>  static.lab.local
<SERVER_IP>  app.lab.local
<SERVER_IP>  api.lab.local
<SERVER_IP>  lb.lab.local
```

On the **server itself** (for `curl` testing):

```powershell
# Run PowerShell as Administrator
Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value @"
127.0.0.1  static.lab.local
127.0.0.1  app.lab.local
127.0.0.1  api.lab.local
127.0.0.1  lb.lab.local
"@
```

### 2.3 Open Firewall

```powershell
# Allow HTTP and HTTPS
New-NetFirewallRule -DisplayName "HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

---

## Exercise 1 — Install IIS & Verify (Beginner)

**Objective:** Install IIS with required role services, understand the architecture, explore config files.

**Time:** 20 minutes

### Step 1 — Install IIS via PowerShell

```powershell
# Run PowerShell as Administrator

# Core IIS + common modules
Install-WindowsFeature -Name `
    Web-Server, `
    Web-Common-Http, `
    Web-Default-Doc, `
    Web-Dir-Browsing, `
    Web-Http-Errors, `
    Web-Static-Content, `
    Web-Http-Logging, `
    Web-Stat-Compression, `
    Web-Dyn-Compression, `
    Web-Filtering, `
    Web-Mgmt-Tools, `
    Web-Mgmt-Console `
    -IncludeManagementTools

# Verify
Get-WindowsFeature Web-* | Where-Object Installed | Format-Table Name, InstallState
```

### Step 2 — Explore Architecture

```powershell
# IIS Services
Get-Service W3SVC, WAS | Format-Table Name, Status, StartType

# Worker processes
Get-Process w3wp -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU, WorkingSet64

# Application Pools
Import-Module WebAdministration
Get-IISAppPool | Format-Table Name, State, ManagedRuntimeVersion

# Sites
Get-IISSite | Format-Table Name, State, Bindings
```

### Step 3 — Explore Config Files

```powershell
# The master config (equivalent to nginx.conf / httpd.conf)
$appHostConfig = "$env:SystemRoot\System32\inetsrv\config\applicationHost.config"
Test-Path $appHostConfig
# View first 50 lines
Get-Content $appHostConfig | Select-Object -First 50

# web.config (per-site override)
$defaultSite = "$env:SystemDrive\inetpub\wwwroot\web.config"
if (Test-Path $defaultSite) { Get-Content $defaultSite }

# Config schema reference
Test-Path "$env:SystemRoot\System32\inetsrv\config\schema"

# IIS Manager (GUI)
Start-Process inetmgr
```

### Step 4 — Verify Default Site

```powershell
# Test locally
Invoke-WebRequest -Uri http://localhost -UseBasicParsing | Select-Object StatusCode, StatusDescription
# Should: 200 OK

# Check what's being served
Get-Content "$env:SystemDrive\inetpub\wwwroot\iisstart.htm" | Select-Object -First 5
```

### ✅ Verification Checklist

- [ ] `Get-Service W3SVC` shows Running
- [ ] `http://localhost` returns 200 with IIS welcome page
- [ ] IIS Manager (`inetmgr`) opens successfully
- [ ] DefaultAppPool is running

> **⚠️ Gotcha:** Always use `Import-Module WebAdministration` or `Import-Module IISAdministration` before IIS cmdlets. The older `WebAdministration` module uses the `IIS:\` PSDrive. The newer `IISAdministration` module (Server 2016+) provides `Get-IISSite`, `Get-IISAppPool`, etc.

---

## Exercise 2 — Sites, Bindings & Host Headers (Beginner)

**Objective:** Create multiple IIS sites with host header routing (like Apache VHosts / Nginx server blocks).

**Time:** 20 minutes

### Architecture

```
  ┌──────────────┐           ┌──────────────────────────────────┐
  │ Browser      │           │ IIS (:80)                        │
  │              │           │                                  │
  │ Host: static │──────────►│ Site: StaticSite                 │
  │ .lab.local   │           │ → C:\Sites\StaticSite\           │
  │              │           │                                  │
  │ Host: app    │──────────►│ Site: AppSite                    │
  │ .lab.local   │           │ → C:\Sites\AppSite\              │
  └──────────────┘           └──────────────────────────────────┘
```

### Step 1 — Create Site Directories & Content

```powershell
# Create site roots
New-Item -Path "C:\Sites\StaticSite" -ItemType Directory -Force
New-Item -Path "C:\Sites\AppSite" -ItemType Directory -Force

# Static site content
@"
<!DOCTYPE html>
<html>
<head><title>Static Site</title></head>
<body>
  <h1>🏠 Static Site — static.lab.local</h1>
  <p>This is the IIS static site.</p>
</body>
</html>
"@ | Set-Content -Path "C:\Sites\StaticSite\index.html"

# App site content
@"
<!DOCTYPE html>
<html>
<head><title>App Site</title></head>
<body>
  <h1>🚀 App Site — app.lab.local</h1>
  <p>This is the IIS application site.</p>
</body>
</html>
"@ | Set-Content -Path "C:\Sites\AppSite\index.html"
```

### Step 2 — Remove Default Site & Create New Sites

```powershell
Import-Module WebAdministration

# Stop and remove default site
Stop-Website -Name "Default Web Site"
Remove-Website -Name "Default Web Site"

# Create Application Pools (one per site — isolation)
New-WebAppPool -Name "StaticSitePool"
New-WebAppPool -Name "AppSitePool"

# Set App Pool to No Managed Code (static sites don't need .NET)
Set-ItemProperty "IIS:\AppPools\StaticSitePool" -Name managedRuntimeVersion -Value ""
Set-ItemProperty "IIS:\AppPools\AppSitePool" -Name managedRuntimeVersion -Value ""

# Create sites with host header bindings
New-Website -Name "StaticSite" -PhysicalPath "C:\Sites\StaticSite" `
    -HostHeader "static.lab.local" -Port 80 -ApplicationPool "StaticSitePool"

New-Website -Name "AppSite" -PhysicalPath "C:\Sites\AppSite" `
    -HostHeader "app.lab.local" -Port 80 -ApplicationPool "AppSitePool"

# Start sites
Start-Website -Name "StaticSite"
Start-Website -Name "AppSite"
```

### Step 3 — Verify

```powershell
# List all sites
Get-IISSite | Format-Table Name, State, Bindings, PhysicalPath

# Test each site
(Invoke-WebRequest -Uri http://static.lab.local -UseBasicParsing).Content | Select-String "Static Site"
(Invoke-WebRequest -Uri http://app.lab.local -UseBasicParsing).Content | Select-String "App Site"

# Test with explicit headers (alternative)
$headers = @{ Host = "static.lab.local" }
Invoke-WebRequest -Uri http://localhost -Headers $headers -UseBasicParsing | Select-Object StatusCode
```

### ✅ Verification Checklist

- [ ] `static.lab.local` shows "Static Site"
- [ ] `app.lab.local` shows "App Site"
- [ ] Each site has its own Application Pool
- [ ] Default Web Site removed

> **⚠️ Gotcha:** IIS uses Host Header in bindings to differentiate sites on the same IP:port. Without a host header, requests fall through to the first site. Always set explicit host headers in production.

---

## Exercise 3 — Static Site with Compression & Caching (Beginner)

**Objective:** Enable static and dynamic compression, configure output caching, and add custom error pages.

**Time:** 20 minutes

### Step 1 — Create Error Pages

```powershell
New-Item -Path "C:\Sites\StaticSite\errors" -ItemType Directory -Force

@"
<!DOCTYPE html>
<html><head><title>404</title></head>
<body><h1>404 — Not Found</h1><p>This page doesn't exist.</p><a href="/">Home</a></body>
</html>
"@ | Set-Content -Path "C:\Sites\StaticSite\errors\404.html"

@"
<!DOCTYPE html>
<html><head><title>500</title></head>
<body><h1>500 — Server Error</h1><p>Something went wrong. Try again later.</p></body>
</html>
"@ | Set-Content -Path "C:\Sites\StaticSite\errors\500.html"

# Create a CSS file for testing
@"
body { font-family: sans-serif; max-width: 800px; margin: 50px auto; background: #f5f5f5; }
h1 { color: #333; }
"@ | Set-Content -Path "C:\Sites\StaticSite\style.css"
```

### Step 2 — Configure via web.config

```powershell
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>

    <!-- Static compression -->
    <urlCompression doStaticCompression="true" doDynamicCompression="true" />

    <!-- Client-side caching for static assets -->
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="30.00:00:00" />
    </staticContent>

    <!-- Custom error pages -->
    <httpErrors errorMode="Custom" existingResponse="Replace">
      <remove statusCode="404" />
      <error statusCode="404" path="/errors/404.html" responseMode="ExecuteURL" />
      <remove statusCode="500" />
      <error statusCode="500" path="/errors/500.html" responseMode="ExecuteURL" />
    </httpErrors>

    <!-- Default document -->
    <defaultDocument>
      <files>
        <clear />
        <add value="index.html" />
      </files>
    </defaultDocument>

  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\StaticSite\web.config"
```

### Step 3 — Verify

```powershell
# Test compression
$response = Invoke-WebRequest -Uri http://static.lab.local -UseBasicParsing `
    -Headers @{ "Accept-Encoding" = "gzip" }
$response.Headers["Content-Encoding"]
# Should show: gzip

# Test cache header
$response = Invoke-WebRequest -Uri http://static.lab.local/style.css -UseBasicParsing
$response.Headers["Cache-Control"]
# Should show: max-age=2592000

# Test 404
try {
    Invoke-WebRequest -Uri http://static.lab.local/nonexistent -UseBasicParsing
} catch {
    $_.Exception.Response.StatusCode  # Should be 404
    # The body will be your custom error page
}
```

### ✅ Verification Checklist

- [ ] Response contains `Content-Encoding: gzip`
- [ ] CSS files return `Cache-Control: max-age=2592000`
- [ ] Missing pages show custom 404 page
- [ ] `web.config` is valid XML

> **⚠️ Gotcha:** IIS compression requires the `Web-Stat-Compression` and `Web-Dyn-Compression` features to be installed. If `Content-Encoding` doesn't appear, verify:
> ```powershell
> Get-WindowsFeature Web-Stat-Compression, Web-Dyn-Compression | Format-Table Name, Installed
> ```

---

## Exercise 4 — Application Pools Deep Dive (Intermediate)

**Objective:** Understand App Pool isolation, recycling, identity, and pipeline modes.

**Time:** 25 minutes

### The Key Concept

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                  IIS APPLICATION POOL MODEL                      │
  │                                                                  │
  │  Site A ──► AppPool A ──► w3wp.exe (PID 1234)                   │
  │                           ├── Pipeline: Integrated               │
  │                           ├── Identity: ApplicationPoolIdentity  │
  │                           ├── .NET CLR: v4.0                     │
  │                           └── Recycle: every 29h, 4GB max       │
  │                                                                  │
  │  Site B ──► AppPool B ──► w3wp.exe (PID 5678)  ← ISOLATED      │
  │                           ├── Pipeline: Integrated               │
  │                           ├── Identity: ApplicationPoolIdentity  │
  │                           └── Recycle: custom schedule           │
  │                                                                  │
  │  If AppPool A crashes → Site B is UNAFFECTED                    │
  │  Each w3wp.exe is a separate process with its own memory space  │
  └──────────────────────────────────────────────────────────────────┘
```

### Step 1 — Create a Test App Pool with Custom Settings

```powershell
Import-Module WebAdministration

# Create pool
New-WebAppPool -Name "TestPool"

# Configure recycling (avoid peak-hour restarts)
Set-ItemProperty "IIS:\AppPools\TestPool" -Name recycling.periodicRestart.time -Value "00:00:00"  # Disable time-based
Set-ItemProperty "IIS:\AppPools\TestPool" -Name recycling.periodicRestart.privateMemory -Value 4194304  # 4GB max

# Schedule recycling at 3 AM
Clear-ItemProperty "IIS:\AppPools\TestPool" -Name recycling.periodicRestart.schedule
Set-ItemProperty "IIS:\AppPools\TestPool" -Name recycling.periodicRestart.schedule -Value @{value="03:00:00"}

# Set pipeline mode
Set-ItemProperty "IIS:\AppPools\TestPool" -Name managedPipelineMode -Value "Integrated"

# Set .NET CLR version (empty string = No Managed Code)
Set-ItemProperty "IIS:\AppPools\TestPool" -Name managedRuntimeVersion -Value ""

# Set idle timeout (20 minutes default, 0 = never)
Set-ItemProperty "IIS:\AppPools\TestPool" -Name processModel.idleTimeout -Value "00:20:00"

# Set start mode (AlwaysRunning = no cold start)
Set-ItemProperty "IIS:\AppPools\TestPool" -Name startMode -Value "AlwaysRunning"
```

### Step 2 — Explore App Pool Properties

```powershell
# View all properties
Get-ItemProperty "IIS:\AppPools\TestPool" | Format-List *

# Key settings to know
$pool = Get-Item "IIS:\AppPools\TestPool"
[PSCustomObject]@{
    Name = $pool.Name
    State = $pool.State
    Pipeline = $pool.managedPipelineMode
    CLR = $pool.managedRuntimeVersion
    Identity = $pool.processModel.identityType
    IdleTimeout = $pool.processModel.idleTimeout
    StartMode = $pool.startMode
    RecycleTime = $pool.recycling.periodicRestart.time
    RecycleMemory = "$($pool.recycling.periodicRestart.privateMemory / 1KB)KB"
}

# View worker processes
Get-ChildItem "IIS:\AppPools\StaticSitePool\WorkerProcesses" | Format-Table processId, state
```

### Step 3 — Monitor Worker Processes

```powershell
# Force a request to start the worker process
Invoke-WebRequest -Uri http://static.lab.local -UseBasicParsing | Out-Null

# See worker processes
Get-Process w3wp | Format-Table Id, ProcessName, WorkingSet64, CPU

# Map PID to App Pool
Get-ChildItem "IIS:\AppPools\*\WorkerProcesses\*" | Format-Table @{
    Label = "AppPool"
    Expression = { $_.GetParent().Name }
}, processId, state
```

### Step 4 — Test App Pool Recycling

```powershell
# Manual recycle
$poolName = "StaticSitePool"
(Get-Item "IIS:\AppPools\$poolName").Recycle()

# Verify new PID
Start-Sleep 2
Invoke-WebRequest -Uri http://static.lab.local -UseBasicParsing | Out-Null
Get-ChildItem "IIS:\AppPools\$poolName\WorkerProcesses\*" | Format-Table processId
```

### ✅ Verification Checklist

- [ ] Each site has its own dedicated App Pool
- [ ] `managedRuntimeVersion` is empty for static sites
- [ ] Recycling schedule set (avoid time-based, use scheduled)
- [ ] Worker processes visible per App Pool

> **⚠️ Gotcha:** Default IIS recycling is every 1740 minutes (29 hours). This causes a cold-start penalty on the first request after recycle. In production: disable time-based recycling, set a specific 3 AM schedule, and use `startMode=AlwaysRunning` with Application Initialization for zero-downtime recycling.

---

## Exercise 5 — URL Rewrite & SPA Hosting (Intermediate)

**Objective:** Install URL Rewrite module and configure SPA client-side routing fallback.

**Time:** 20 minutes

### Step 1 — Install URL Rewrite Module

```powershell
# Download and install URL Rewrite
# Option 1: Web Platform Installer
# Option 2: Direct download from Microsoft

# Download URL Rewrite 2.1 (x64)
$url = "https://download.microsoft.com/download/1/2/8/128E2E22-C1B9-44A4-BE2A-5859ED1D4592/rewrite_amd64_en-US.msi"
$output = "$env:TEMP\urlrewrite2.msi"
Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing

# Install silently
Start-Process msiexec.exe -ArgumentList "/i $output /quiet /norestart" -Wait -NoNewWindow

# Verify (restart IIS after install)
iisreset /restart
Get-WebGlobalModule | Where-Object Name -like "*rewrite*" | Format-Table Name
```

### Step 2 — Create SPA Content

```powershell
# Ensure AppSite directory exists
New-Item -Path "C:\Sites\AppSite\assets\css" -ItemType Directory -Force
New-Item -Path "C:\Sites\AppSite\assets\js" -ItemType Directory -Force

@"
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
    <a href="/dashboard">Dashboard</a>
  </nav>
  <div id="app">
    <h1>🚀 SPA Application on IIS</h1>
    <p>Current route: <strong id="route"></strong></p>
    <p>All routes serve this index.html — URL Rewrite handles fallback.</p>
  </div>
  <script>document.getElementById('route').textContent = window.location.pathname;</script>
</body>
</html>
"@ | Set-Content -Path "C:\Sites\AppSite\index.html"

@"
body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
nav { background: #2196F3; padding: 12px; border-radius: 4px; }
nav a { color: white; margin: 0 15px; text-decoration: none; font-weight: bold; }
"@ | Set-Content -Path "C:\Sites\AppSite\assets\css\app.css"
```

### Step 3 — Configure URL Rewrite via web.config

```powershell
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="SPA Fallback" stopProcessing="true">
          <match url=".*" />
          <conditions logicalGrouping="MatchAll">
            <!-- Don't rewrite actual files -->
            <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
            <!-- Don't rewrite actual directories -->
            <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
            <!-- Don't rewrite API calls (if applicable) -->
            <add input="{REQUEST_URI}" pattern="^/api/" negate="true" />
          </conditions>
          <action type="Rewrite" url="/index.html" />
        </rule>
      </rules>
    </rewrite>

    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="30.00:00:00" />
    </staticContent>
  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\AppSite\web.config"
```

### Step 4 — Test SPA Routing

```powershell
# All these should return the same SPA index.html:
(Invoke-WebRequest -Uri http://app.lab.local/ -UseBasicParsing).Content | Select-String "SPA Application"
(Invoke-WebRequest -Uri http://app.lab.local/about -UseBasicParsing).Content | Select-String "SPA Application"
(Invoke-WebRequest -Uri http://app.lab.local/dashboard -UseBasicParsing).Content | Select-String "SPA Application"
(Invoke-WebRequest -Uri http://app.lab.local/any/deep/route -UseBasicParsing).Content | Select-String "SPA Application"

# But actual files should be served directly:
(Invoke-WebRequest -Uri http://app.lab.local/assets/css/app.css -UseBasicParsing).Headers["Content-Type"]
# Should return: text/css
```

### ✅ Verification Checklist

- [ ] `/about`, `/dashboard`, `/any/route` all return the SPA index.html
- [ ] `/assets/css/app.css` returns the actual CSS file
- [ ] URL Rewrite module is installed and working
- [ ] `web.config` is valid

> **⚠️ Gotcha:** The IIS equivalent of Nginx `try_files` is URL Rewrite with `IsFile`/`IsDirectory` conditions. Without URL Rewrite installed, you get 404 for all SPA routes.

---

## Exercise 6 — SSL/TLS with Self-Signed Certificate (Intermediate)

**Objective:** Generate a self-signed certificate, bind to HTTPS, configure HTTP→HTTPS redirect.

**Time:** 25 minutes

### Step 1 — Generate Self-Signed Certificate

```powershell
# Create a wildcard self-signed certificate
$cert = New-SelfSignedCertificate `
    -DnsName "*.lab.local", "lab.local" `
    -CertStoreLocation "Cert:\LocalMachine\My" `
    -NotAfter (Get-Date).AddYears(1) `
    -FriendlyName "Lab Wildcard" `
    -KeyAlgorithm RSA `
    -KeyLength 2048

# View the certificate
$cert | Format-List Subject, DnsNameList, Thumbprint, NotBefore, NotAfter

# Store thumbprint for later use
$thumbprint = $cert.Thumbprint
Write-Host "Thumbprint: $thumbprint"
```

### Step 2 — Add HTTPS Binding to Static Site

```powershell
Import-Module WebAdministration

# Add HTTPS binding with SNI (Server Name Indication)
New-WebBinding -Name "StaticSite" -Protocol "https" `
    -Port 443 -HostHeader "static.lab.local" -SslFlags 1

# Bind certificate to the HTTPS binding
$binding = Get-WebBinding -Name "StaticSite" -Protocol "https"
$binding.AddSslCertificate($thumbprint, "My")

# Verify bindings
Get-WebBinding -Name "StaticSite" | Format-Table protocol, bindingInformation
```

### Step 3 — Configure HTTP→HTTPS Redirect

Add to the static site's web.config:

```powershell
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>

    <!-- URL Rewrite: HTTP → HTTPS redirect -->
    <rewrite>
      <rules>
        <rule name="HTTP to HTTPS" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="off" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>

    <!-- Compression -->
    <urlCompression doStaticCompression="true" doDynamicCompression="true" />

    <!-- Cache -->
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="30.00:00:00" />
    </staticContent>

    <!-- Custom error pages -->
    <httpErrors errorMode="Custom" existingResponse="Replace">
      <remove statusCode="404" />
      <error statusCode="404" path="/errors/404.html" responseMode="ExecuteURL" />
    </httpErrors>

    <!-- HSTS -->
    <httpProtocol>
      <customHeaders>
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains" />
      </customHeaders>
    </httpProtocol>

  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\StaticSite\web.config"
```

### Step 4 — Test

```powershell
# Test HTTP redirect (should 301 → HTTPS)
try {
    Invoke-WebRequest -Uri http://static.lab.local -UseBasicParsing -MaximumRedirection 0
} catch {
    $_.Exception.Response.StatusCode       # 301
    $_.Exception.Response.Headers.Location # https://static.lab.local/
}

# Test HTTPS (skip cert validation for self-signed)
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
$response = Invoke-WebRequest -Uri https://static.lab.local -UseBasicParsing
$response.StatusCode
$response.Headers["Strict-Transport-Security"]

# Check TLS version
[Net.ServicePointManager]::SecurityProtocol
```

### ✅ Verification Checklist

- [ ] HTTP redirects to HTTPS (301)
- [ ] HTTPS returns 200 with static site content
- [ ] `Strict-Transport-Security` header present
- [ ] Certificate shows `*.lab.local` subject

> **⚠️ Gotcha (SNI):** The `-SslFlags 1` parameter enables SNI (Server Name Indication), allowing multiple HTTPS sites on the same IP:443. Without SNI, only one certificate per IP:port is possible. SNI requires IE 7+ / all modern browsers.

---

## Exercise 7 — Reverse Proxy with ARR (Intermediate)

**Objective:** Install Application Request Routing (ARR) and configure IIS as a reverse proxy.

**Time:** 30 minutes

### Architecture

```
  Client → IIS (:80) → Node.js (:3001)

  ┌──────────────┐     ┌─────────────────┐     ┌────────────────┐
  │  Browser     │────►│ IIS             │────►│ Node.js        │
  │              │     │ api.lab.local   │     │ 127.0.0.1:3001 │
  │              │◄────│ (ARR Proxy)     │◄────│ (JSON API)     │
  └──────────────┘     └─────────────────┘     └────────────────┘
```

### Step 1 — Install ARR & URL Rewrite

```powershell
# Download ARR 3.0
$arrUrl = "https://download.microsoft.com/download/E/9/8/E9849D6A-020E-47E4-9FD0-A023E99B54EB/requestRouter_amd64.msi"
$arrOutput = "$env:TEMP\arr3.msi"
Invoke-WebRequest -Uri $arrUrl -OutFile $arrOutput -UseBasicParsing

# Install ARR
Start-Process msiexec.exe -ArgumentList "/i $arrOutput /quiet /norestart" -Wait -NoNewWindow

# Restart IIS
iisreset /restart
```

### Step 2 — Enable Proxy Mode

```powershell
# Enable ARR proxy at the server level
Import-Module WebAdministration

# Method 1: PowerShell
Set-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' `
    -filter "system.webServer/proxy" -name "enabled" -value "True"

# Optionally preserve host header
Set-WebConfigurationProperty -pspath 'MACHINE/WEBROOT/APPHOST' `
    -filter "system.webServer/proxy" -name "preserveHostHeader" -value "True"
```

### Step 3 — Install Node.js & Start Backend

```powershell
# Download Node.js LTS
$nodeUrl = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
$nodeOutput = "$env:TEMP\nodejs.msi"
Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeOutput -UseBasicParsing
Start-Process msiexec.exe -ArgumentList "/i $nodeOutput /quiet /norestart" -Wait

# Refresh PATH
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + $env:PATH

# Create backend
New-Item -Path "C:\NodeApps\api" -ItemType Directory -Force

@"
const http = require('http');
const PORT = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  const response = {
    message: 'Hello from Node.js backend!',
    path: req.url,
    method: req.method,
    headers: {
      host: req.headers.host,
      'x-forwarded-for': req.headers['x-forwarded-for'] || 'not set',
      'x-arr-ssl': req.headers['x-arr-ssl'] || 'not set'
    },
    pid: process.pid,
    port: PORT
  };
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(response, null, 2));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`API on http://127.0.0.1:${PORT}`);
});
"@ | Set-Content -Path "C:\NodeApps\api\server.js"

# Start Node.js backend (in a separate PowerShell window or as service)
Start-Process node -ArgumentList "C:\NodeApps\api\server.js" -NoNewWindow

# Verify backend is running
Start-Sleep 2
Invoke-WebRequest -Uri http://127.0.0.1:3001 -UseBasicParsing | Select-Object Content
```

### Step 4 — Create API Site with Reverse Proxy Rules

```powershell
# Create site directory and App Pool
New-Item -Path "C:\Sites\ApiSite" -ItemType Directory -Force
New-WebAppPool -Name "ApiSitePool"
Set-ItemProperty "IIS:\AppPools\ApiSitePool" -Name managedRuntimeVersion -Value ""

New-Website -Name "ApiSite" -PhysicalPath "C:\Sites\ApiSite" `
    -HostHeader "api.lab.local" -Port 80 -ApplicationPool "ApiSitePool"

# Create web.config with reverse proxy rule
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Reverse Proxy to Node.js" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\ApiSite\web.config"

Start-Website -Name "ApiSite"
```

### Step 5 — Test

```powershell
# Test through IIS proxy
$response = Invoke-WebRequest -Uri http://api.lab.local -UseBasicParsing
$response.Content | ConvertFrom-Json | Format-List

# Verify host header preserved
($response.Content | ConvertFrom-Json).headers.host
# Should show: api.lab.local (because preserveHostHeader = true)

# Test different paths
(Invoke-WebRequest -Uri http://api.lab.local/users -UseBasicParsing).Content | ConvertFrom-Json
```

### ✅ Verification Checklist

- [ ] API proxy returns JSON from Node.js backend
- [ ] `host` header shows `api.lab.local` (preserved)
- [ ] Different URL paths are passed through correctly
- [ ] ARR proxy enabled at server level

> **⚠️ Gotcha:** Enabling ARR proxy at the server level (`system.webServer/proxy enabled=true`) is a **global** setting. It applies to ALL sites. Per-site proxy rules in `web.config` control which sites actually proxy. Without URL Rewrite rules, sites serve content normally.

---

## Exercise 8 — Load Balancing with ARR Server Farms (Advanced)

**Objective:** Configure IIS ARR as a load balancer across multiple backends.

**Time:** 30 minutes

### Architecture

```
  ┌──────────────┐     ┌─────────────────────────┐     ┌────────────┐
  │  Browser     │────►│  IIS (ARR Server Farm)  │──┬─►│ Node :3001 │
  │              │     │  lb.lab.local            │  │  └────────────┘
  │              │◄────│                          │  │  ┌────────────┐
  └──────────────┘     │  Health checks active    │──┼─►│ Node :3002 │
                       │                          │  │  └────────────┘
                       └─────────────────────────┘  │  ┌────────────┐
                                                    └─►│ Node :3003 │
                                                       └────────────┘
```

### Step 1 — Start Multiple Backends

```powershell
# Start 3 Node.js instances on different ports
Stop-Process -Name node -ErrorAction SilentlyContinue
Start-Sleep 1

$env:PORT = "3001"; Start-Process node -ArgumentList "C:\NodeApps\api\server.js" -NoNewWindow
$env:PORT = "3002"; Start-Process node -ArgumentList "C:\NodeApps\api\server.js" -NoNewWindow
$env:PORT = "3003"; Start-Process node -ArgumentList "C:\NodeApps\api\server.js" -NoNewWindow
Start-Sleep 2

# Verify all running
1..3 | ForEach-Object {
    $port = 3000 + $_
    $resp = (Invoke-WebRequest -Uri "http://127.0.0.1:$port" -UseBasicParsing).Content | ConvertFrom-Json
    "Port $port — PID $($resp.pid)"
}
```

### Step 2 — Create Server Farm via IIS Manager

The easiest way to create a server farm is via IIS Manager GUI:

1. Open IIS Manager → Click server name → **Server Farms** (in features view)
2. Click **Create Server Farm** → Name: `NodeFarm`
3. Add servers: `127.0.0.1` with ports 3001, 3002, 3003
4. Set health check URL: `http://127.0.0.1:{port}/`
5. When prompted "Create URL Rewrite rules?", click **Yes**

### Alternative: Manual Config via appcmd

```powershell
# Add server farm using appcmd
$appcmd = "$env:SystemRoot\System32\inetsrv\appcmd.exe"

& $appcmd set config -section:webFarms /+"[name='NodeFarm']" /commit:apphost

& $appcmd set config -section:webFarms `
    /+"[name='NodeFarm'].[address='127.0.0.1',enabled='True']" `
    /commit:apphost

# Note: For multiple ports on the same IP, you need to configure
# the ARR settings through web.config or IIS Manager.
# The appcmd approach works best for different server IPs.
```

### Step 3 — Create Load Balancer Site

```powershell
# Create site
New-Item -Path "C:\Sites\LbSite" -ItemType Directory -Force
New-WebAppPool -Name "LbSitePool"
Set-ItemProperty "IIS:\AppPools\LbSitePool" -Name managedRuntimeVersion -Value ""

New-Website -Name "LbSite" -PhysicalPath "C:\Sites\LbSite" `
    -HostHeader "lb.lab.local" -Port 80 -ApplicationPool "LbSitePool"

# Create web.config with load balancing rule
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Load Balance to NodeFarm" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://NodeFarm/{R:1}" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\LbSite\web.config"

Start-Website -Name "LbSite"
```

### Step 4 — Test Load Balancing

```powershell
# Send multiple requests — should distribute across backends
1..9 | ForEach-Object {
    $resp = (Invoke-WebRequest -Uri http://lb.lab.local -UseBasicParsing).Content | ConvertFrom-Json
    "Request $_ → Port $($resp.port) (PID $($resp.pid))"
}
```

### Step 5 — Configure Health Checks (via IIS Manager)

In IIS Manager:

1. Click **Server Farms** → **NodeFarm**
2. Open **Health Test**
3. Set URL: `http://lb.lab.local/`
4. Response match: (empty or specific pattern)
5. Interval: 30 seconds
6. Timeout: 10 seconds

### ✅ Verification Checklist

- [ ] Requests distribute across 3 backends
- [ ] Killing one backend doesn't affect availability
- [ ] Server Farm visible in IIS Manager
- [ ] Health checks configured

> **⚠️ Gotcha:** ARR uses weighted round-robin by default. For session affinity (sticky sessions), enable **Client Affinity** in the Server Farm → Routing Rules. This uses an `ARRAffinity` cookie.

---

## Exercise 9 — Security Hardening & Request Filtering (Advanced)

**Objective:** Apply production security: remove server header, configure request filtering, block patterns.

**Time:** 30 minutes

### Step 1 — Remove Server Header

```powershell
# Method 1: Registry (removes IIS version from Server header)
# Changes "Server: Microsoft-IIS/10.0" to "Server: Microsoft-IIS"
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\HTTP\Parameters" `
    -Name "DisableServerHeader" -Value 0 -Type DWord

# Method 2: Remove header entirely via URL Rewrite (outbound rule)
# This requires the URL Rewrite module
```

### Step 2 — Configure Request Filtering

Create a comprehensive security web.config for the API site:

```powershell
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>

    <!-- Request Filtering (IIS built-in WAF) -->
    <security>
      <requestFiltering removeServerHeader="true">
        <!-- Limit request size -->
        <requestLimits maxAllowedContentLength="30000000" maxUrl="4096" maxQueryString="2048" />

        <!-- Block dangerous file extensions -->
        <fileExtensions allowUnlisted="true">
          <add fileExtension=".bak" allowed="false" />
          <add fileExtension=".config" allowed="false" />
          <add fileExtension=".sql" allowed="false" />
          <add fileExtension=".mdf" allowed="false" />
          <add fileExtension=".ldf" allowed="false" />
          <add fileExtension=".cs" allowed="false" />
          <add fileExtension=".csproj" allowed="false" />
        </fileExtensions>

        <!-- Block URL sequences -->
        <denyUrlSequences>
          <add sequence=".." />
          <add sequence="//" />
          <add sequence="\\"/>
          <add sequence="web.config" />
          <add sequence=".git" />
          <add sequence=".env" />
          <add sequence=".svn" />
        </denyUrlSequences>

        <!-- Block dangerous HTTP verbs -->
        <verbs allowUnlisted="false">
          <add verb="GET" allowed="true" />
          <add verb="HEAD" allowed="true" />
          <add verb="POST" allowed="true" />
          <add verb="PUT" allowed="true" />
          <add verb="PATCH" allowed="true" />
          <add verb="DELETE" allowed="true" />
          <add verb="OPTIONS" allowed="true" />
        </verbs>
      </requestFiltering>
    </security>

    <!-- Security headers -->
    <httpProtocol>
      <customHeaders>
        <remove name="X-Powered-By" />
        <remove name="Server" />
        <add name="X-Frame-Options" value="SAMEORIGIN" />
        <add name="X-Content-Type-Options" value="nosniff" />
        <add name="X-XSS-Protection" value="1; mode=block" />
        <add name="Referrer-Policy" value="strict-origin-when-cross-origin" />
        <add name="Permissions-Policy" value="camera=(), microphone=(), geolocation=()" />
        <add name="Content-Security-Policy" value="default-src 'self'; script-src 'self' 'unsafe-inline';" />
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains" />
      </customHeaders>
    </httpProtocol>

    <!-- Reverse proxy rule -->
    <rewrite>
      <rules>
        <rule name="Reverse Proxy to Node.js" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:3001/{R:1}" />
        </rule>
      </rules>

      <!-- Remove Server header via outbound rule -->
      <outboundRules>
        <rule name="Remove Server Header">
          <match serverVariable="RESPONSE_Server" pattern=".*" />
          <action type="Rewrite" value="" />
        </rule>
      </outboundRules>
    </rewrite>

  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\ApiSite\web.config"
```

### Step 3 — Test Security

```powershell
# Test server header removed
$response = Invoke-WebRequest -Uri http://api.lab.local -UseBasicParsing
$response.Headers["Server"]       # Should be empty or absent
$response.Headers["X-Powered-By"] # Should be absent

# Test security headers
$response.Headers["X-Frame-Options"]           # SAMEORIGIN
$response.Headers["X-Content-Type-Options"]    # nosniff
$response.Headers["Content-Security-Policy"]   # default-src 'self'...

# Test blocked sequences
try {
    Invoke-WebRequest -Uri "http://api.lab.local/.env" -UseBasicParsing
} catch {
    $_.Exception.Response.StatusCode  # 404 or 403
}

try {
    Invoke-WebRequest -Uri "http://api.lab.local/web.config" -UseBasicParsing
} catch {
    $_.Exception.Response.StatusCode  # 404
}

# Test blocked verb (TRACE)
try {
    Invoke-WebRequest -Uri http://api.lab.local -Method TRACE -UseBasicParsing
} catch {
    $_.Exception.Response.StatusCode  # 404 (verb not allowed)
}
```

### Step 4 — IP Address Restrictions (Optional)

```powershell
# Install IP Security feature
Install-WindowsFeature Web-IP-Security

# Configure via appcmd or web.config
# Example: Allow only specific IP range
# <security>
#   <ipSecurity allowUnlisted="false" denyAction="NotFound">
#     <add ipAddress="10.0.0.0" subnetMask="255.0.0.0" allowed="true" />
#     <add ipAddress="192.168.0.0" subnetMask="255.255.0.0" allowed="true" />
#     <add ipAddress="127.0.0.1" allowed="true" />
#   </ipSecurity>
# </security>
```

### ✅ Verification Checklist

- [ ] Server header removed (empty or absent)
- [ ] X-Powered-By header removed
- [ ] Security headers present (X-Frame-Options, CSP, HSTS, etc.)
- [ ] `.env`, `.git`, `web.config` paths are blocked
- [ ] Blocked HTTP verbs return error

> **⚠️ Gotcha:** `removeServerHeader="true"` in `<requestFiltering>` only works on IIS 10.0+ (Server 2016+). On older versions, use the outbound rewrite rule to blank the Server header.

---

## Exercise 10 — FREB Diagnostics, Monitoring & Docker (Advanced)

**Objective:** Configure Failed Request Event Buffering (FREB) tracing, set up monitoring, understand Docker deployment.

**Time:** 30 minutes

### Step 1 — Install FREB Tracing Feature

```powershell
Install-WindowsFeature Web-Http-Tracing
iisreset /restart
```

### Step 2 — Enable FREB for a Site

```powershell
Import-Module WebAdministration

# Enable FREB for StaticSite
Set-ItemProperty "IIS:\Sites\StaticSite" -Name traceFailedRequestsLogging.enabled -Value $true
Set-ItemProperty "IIS:\Sites\StaticSite" -Name traceFailedRequestsLogging.directory -Value "C:\inetpub\logs\FailedReqLogFiles\StaticSite"
Set-ItemProperty "IIS:\Sites\StaticSite" -Name traceFailedRequestsLogging.maxLogFiles -Value 50

# Create logging directory
New-Item -Path "C:\inetpub\logs\FailedReqLogFiles\StaticSite" -ItemType Directory -Force
```

### Step 3 — Configure FREB Rules via web.config

```powershell
# Add FREB tracing rule — capture 404s and slow requests (> 5 seconds)
@"
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <tracing>
      <traceFailedRequests>
        <!-- Trace 404 errors -->
        <add path="*">
          <traceAreas>
            <add provider="WWW Server" areas="Authentication,Security,Filter,StaticFile,CGI,Compression,Cache,RequestNotifications" verbosity="Verbose" />
          </traceAreas>
          <failureDefinitions statusCodes="404-404" />
        </add>
        <!-- Trace slow requests (> 5 seconds) -->
        <add path="*">
          <traceAreas>
            <add provider="WWW Server" areas="RequestNotifications" verbosity="Verbose" />
          </traceAreas>
          <failureDefinitions timeTaken="00:00:05" />
        </add>
      </traceFailedRequests>
    </tracing>

    <!-- Keep existing settings -->
    <urlCompression doStaticCompression="true" doDynamicCompression="true" />
    <staticContent>
      <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="30.00:00:00" />
    </staticContent>
    <httpErrors errorMode="Custom" existingResponse="Replace">
      <remove statusCode="404" />
      <error statusCode="404" path="/errors/404.html" responseMode="ExecuteURL" />
    </httpErrors>
    <rewrite>
      <rules>
        <rule name="HTTP to HTTPS" stopProcessing="true">
          <match url="(.*)" />
          <conditions>
            <add input="{HTTPS}" pattern="off" />
          </conditions>
          <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>
    <httpProtocol>
      <customHeaders>
        <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains" />
      </customHeaders>
    </httpProtocol>
  </system.webServer>
</configuration>
"@ | Set-Content -Path "C:\Sites\StaticSite\web.config"
```

### Step 4 — Trigger and View FREB Trace

```powershell
# Trigger a 404
try {
    Invoke-WebRequest -Uri "http://static.lab.local/this-does-not-exist.html" -UseBasicParsing
} catch {}

# View FREB logs
Get-ChildItem "C:\inetpub\logs\FailedReqLogFiles\StaticSite" -Recurse | Format-Table Name, Length, LastWriteTime

# FREB produces XML files with an XSL stylesheet
# Open in browser for visual trace:
$frebFiles = Get-ChildItem "C:\inetpub\logs\FailedReqLogFiles\StaticSite\*.xml" | Sort-Object LastWriteTime -Descending
if ($frebFiles) {
    Write-Host "Open in browser: $($frebFiles[0].FullName)"
    # Uncomment to open:
    # Start-Process $frebFiles[0].FullName
}
```

### Step 5 — IIS Monitoring with Performance Counters

```powershell
# Key IIS performance counters
$counters = @(
    "\Web Service(_Total)\Current Connections",
    "\Web Service(_Total)\Bytes Sent/sec",
    "\Web Service(_Total)\Bytes Received/sec",
    "\Web Service(_Total)\Total Method Requests/sec",
    "\ASP.NET\Requests Current",
    "\HTTP Service Request Queues(*)\CurrentQueueSize"
)

# Sample counters
Get-Counter -Counter $counters -SampleInterval 1 -MaxSamples 3 | ForEach-Object {
    $_.CounterSamples | Format-Table Path, CookedValue
}

# Quick health check
[PSCustomObject]@{
    W3SVC = (Get-Service W3SVC).Status
    WAS = (Get-Service WAS).Status
    AppPools = (Get-IISAppPool | Where-Object State -eq "Started").Count
    Sites = (Get-IISSite | Where-Object State -eq "Started").Count
    WorkerProcesses = @(Get-Process w3wp -ErrorAction SilentlyContinue).Count
}
```

### Step 6 — Docker Deployment (Conceptual + Config)

IIS runs natively in Windows containers. Here's a conceptual Docker deployment:

```powershell
# Dockerfile (for Windows containers)
@"
# IIS base image
FROM mcr.microsoft.com/windows/servercore/iis:windowsservercore-ltsc2022

# Remove default site
RUN powershell -Command Remove-Website -Name 'Default Web Site'

# Copy site content
COPY ./site /inetpub/wwwroot

# Create site
RUN powershell -Command `
    New-Website -Name 'MySite' -PhysicalPath 'C:\inetpub\wwwroot' -Port 80 -Force

# IIS runs as ServiceMonitor (foreground process for containers)
ENTRYPOINT ["C:\\ServiceMonitor.exe", "w3svc"]
"@ | Set-Content -Path "C:\DockerLab\Dockerfile"

# Build and run (if Docker Desktop with Windows containers is installed)
# docker build -t iis-lab C:\DockerLab
# docker run -d -p 8080:80 --name iis-container iis-lab
# Invoke-WebRequest -Uri http://localhost:8080 -UseBasicParsing
```

> **Key Docker gotchas for IIS:**
> 1. `ServiceMonitor.exe` is the entrypoint — it keeps the container alive and monitors W3SVC
> 2. Windows containers are **much larger** (~5GB vs ~50MB for Alpine Linux containers)
> 3. Process isolation (default) vs Hyper-V isolation — host OS build must match container OS build with process isolation
> 4. `LogMonitor.exe` pipes IIS logs to stdout for `docker logs` to capture

### ✅ Verification Checklist

- [ ] FREB trace generated for 404 requests
- [ ] FREB XML files viewable in browser with timeline visualization
- [ ] Performance counters return IIS metrics
- [ ] Understanding of IIS Docker deployment model

---

## Cleanup

```powershell
# Stop backends
Stop-Process -Name node -ErrorAction SilentlyContinue

# Remove sites
Get-Website | Where-Object Name -ne "Default Web Site" | Remove-Website

# Remove app pools (custom ones only)
"StaticSitePool", "AppSitePool", "ApiSitePool", "LbSitePool", "TestPool" | ForEach-Object {
    Remove-WebAppPool -Name $_ -ErrorAction SilentlyContinue
}

# Remove site directories
Remove-Item -Path "C:\Sites" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "C:\NodeApps" -Recurse -Force -ErrorAction SilentlyContinue

# Remove SSL cert
Get-ChildItem Cert:\LocalMachine\My | Where-Object FriendlyName -eq "Lab Wildcard" | Remove-Item

# Optionally remove IIS entirely
# Uninstall-WindowsFeature Web-Server -IncludeManagementTools
```

---

## Troubleshooting Reference

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  COMMON ISSUES & FIXES                                           │
  │                                                                  │
  │  Problem                        Fix                              │
  │  ─────────────────────────────  ───────────────────────────────  │
  │  500.19 — Config error          web.config XML syntax error,     │
  │                                 missing module/feature           │
  │                                                                  │
  │  502.3 — Bad Gateway            Backend down, ARR not enabled,   │
  │                                 timeout too short                │
  │                                                                  │
  │  503 — Service Unavailable      App Pool crashed / stopped,      │
  │                                 check Event Viewer               │
  │                                                                  │
  │  403.14 — Dir listing denied    No default document, add         │
  │                                 index.html to defaultDocument    │
  │                                                                  │
  │  404.3 — MIME type missing      Add MIME type for the file ext   │
  │                                 in <staticContent><mimeMap>      │
  │                                                                  │
  │  URL Rewrite not working        Module not installed, check      │
  │                                 web.config rules + conditions    │
  │                                                                  │
  │  Slow first request             App Pool cold start: set         │
  │                                 startMode=AlwaysRunning          │
  └──────────────────────────────────────────────────────────────────┘
```

### Debug Commands

```powershell
# IIS config test
$appcmd = "$env:SystemRoot\System32\inetsrv\appcmd.exe"
& $appcmd list site
& $appcmd list apppool
& $appcmd list wp               # Worker processes

# Event logs
Get-EventLog -LogName System -Source "IIS*" -Newest 10 | Format-Table TimeGenerated, Message -Wrap
Get-WinEvent -LogName "Microsoft-IIS-Configuration/Operational" -MaxEvents 10 -ErrorAction SilentlyContinue

# IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC*\*.log" -Tail 20

# Netstat — check listening ports
netstat -an | Select-String ":80 |:443 |:3001|:3002|:3003"

# Test URL from server
Invoke-WebRequest -Uri http://localhost -UseBasicParsing | Select-Object StatusCode
```

### Sub-Status Code Quick Reference

```
  ┌────────────────────────────────────────────────────────────────┐
  │  Status.Sub   Meaning                                          │
  │  ──────────   ───────────────────────────────────────────────  │
  │  400.0        Bad Request (generic)                            │
  │  401.1        Logon failed                                     │
  │  401.2        Logon failed (server config)                     │
  │  403.14       Directory listing denied                         │
  │  403.18       Cannot execute in App Pool (.NET version issue)  │
  │  404.0        File not found                                   │
  │  404.3        MIME type restriction                            │
  │  404.13       Content too large                                │
  │  500.0        Internal server error                            │
  │  500.19       Configuration data invalid (web.config error)    │
  │  500.21       Module not recognized                            │
  │  502.3        Bad gateway / Forwarder connection failure (ARR) │
  │  503.0        Application pool unavailable                     │
  └────────────────────────────────────────────────────────────────┘
```

---

> **Lab Complete!** You now have hands-on experience with IIS from basic setup through production configuration.  
> **Next:** Try the [Apache Practice Lab](apache_practice_lab.md) or [Nginx Practice Lab](nginx_practice_lab.md).

[🏠 Home](../README.md) · [Labs](README.md) · [IIS Handbook](../servers/iis.md)
