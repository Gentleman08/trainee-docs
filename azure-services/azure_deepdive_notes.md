# ☁️ Azure Services Deep Dive — Configuration & Scenarios Guide

> **Purpose:** Field-by-field configuration guide for key Azure services, with operational tasks, real-world scenarios, and interview prep.
> **Companion to:** `azure_services_handbook.md` (conceptual reference)
> **Last updated:** 2026-05-04

---

## 📑 Table of Contents

1. [App Service Deep Dive](#chapter-1--azure-app-service-deep-dive)
2. [Azure Key Vault Deep Dive](#chapter-2--azure-key-vault-deep-dive)
3. [Storage Accounts Deep Dive](#chapter-3--azure-storage-accounts-deep-dive)
4. [Azure Databases Deep Dive](#chapter-4--azure-databases-deep-dive)
5. [Azure Functions Deep Dive](#chapter-5--azure-functions-deep-dive)
6. [Azure Container Registry Deep Dive](#chapter-6--azure-container-registry-deep-dive)
7. [ACI, Container Apps & Container Groups](#chapter-7--aci-container-apps--container-groups)
8. [HA, DR & Reliability on Azure](#chapter-8--ha-dr--reliability-on-azure)
9. [User Defined Routes & Other Topics](#chapter-9--user-defined-routes--other-important-topics)
10. [Interview Questions — All Services](#chapter-10--interview-questions--all-services)

---

# Chapter 1 — Azure App Service Deep Dive

> App Service is Azure's PaaS web hosting platform. This chapter explains **every field** you encounter when creating, configuring, and operating an App Service.

---

## 1.1 Creating an App Service — Every Field Explained

When you click "Create Web App" in the Azure Portal, you see these tabs: **Basics, Docker, Networking, Monitoring, Tags, Review+Create.**

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Subscription** | Which Azure billing account to use | `Pay-As-You-Go` | All costs go here |
| **Resource Group** | Logical container for related resources | `rg-myapp-prod` | Group app + DB + KV together |
| **Name** | Your app's URL: `<name>.azurewebsites.net` | `myapp-prod` | Globally unique, 2-60 chars, alphanumeric + hyphens |
| **Publish** | Code or Docker Container | `Code` | Code = deploy source directly. Container = deploy Docker image |
| **Runtime stack** | Language + version | `.NET 8`, `Python 3.12`, `Node 20 LTS` | Must match your app's language |
| **Operating System** | Linux or Windows | `Linux` | Linux is cheaper (~30% less), supports more stacks. Windows needed for .NET Framework |
| **Region** | Azure datacenter location | `East US` | Pick closest to your users. Must match VNet region if using VNet integration |

### App Service Plan (created on Basics tab)

The plan is the **underlying VM(s)** your app runs on. Multiple apps can share one plan.

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Plan name** | Name of the hosting plan | `asp-myapp-prod` | Convention: `asp-<app>-<env>` |
| **SKU / Pricing tier** | Size and features of the VM | See table below | This is your biggest cost decision |

**Pricing tiers explained:**

```
  ┌────────┬──────────┬────────┬───────┬────────────────────────────────────────┐
  │ Tier   │ CPU/RAM  │ $/mo   │ Scale │ Key features                           │
  ├────────┼──────────┼────────┼───────┼────────────────────────────────────────┤
  │ F1     │ Shared   │ Free   │ No    │ 60 min/day compute. Dev/test only      │
  │ B1     │ 1C/1.75G │ ~$13   │ No    │ Always on, custom domain. Dev/test     │
  │ B2     │ 2C/3.5G  │ ~$26   │ No    │ More CPU/RAM                           │
  │ B3     │ 4C/7G    │ ~$52   │ No    │ Largest Basic                          │
  ├────────┼──────────┼────────┼───────┼────────────────────────────────────────┤
  │ S1     │ 1C/1.75G │ ~$73   │ 10    │ Slots, auto-scale, VNet, backups      │
  │ S2     │ 2C/3.5G  │ ~$146  │ 10    │ Same features, more power             │
  │ S3     │ 4C/7G    │ ~$292  │ 10    │ Largest Standard                       │
  ├────────┼──────────┼────────┼───────┼────────────────────────────────────────┤
  │ P1v3   │ 2C/8G    │ ~$138  │ 30    │ Premium: faster CPU, more RAM, 250GB  │
  │ P2v3   │ 4C/16G   │ ~$276  │ 30    │ storage, zone redundancy, private     │
  │ P3v3   │ 8C/32G   │ ~$550  │ 30    │ endpoint support                      │
  └────────┴──────────┴────────┴───────┴────────────────────────────────────────┘

  Scale = max instances for auto-scale
  Recommendation: B1 for dev, S1 for small prod, P1v3 for production
```

### Docker Tab (if Publish = Container)

| Field | What it means | Example value |
|-------|--------------|---------------|
| **Image Source** | Where to pull image from | ACR, Docker Hub, Private Registry |
| **Registry** | Registry URL | `myacr.azurecr.io` |
| **Image** | Image name | `myapi` |
| **Tag** | Image version | `v1.2.3` or `latest` |
| **Startup Command** | Override container CMD | `gunicorn app:app --bind 0.0.0.0:8000` |

### Networking Tab

| Field | What it means | Example value |
|-------|--------------|---------------|
| **Enable public access** | Can the internet reach your app? | `On` (default) |
| **VNet integration** | App can reach resources in a VNet | Select VNet + subnet |
| **Private endpoint** | App accessible only via private IP | Creates a PE in your VNet |

### Monitoring Tab

| Field | What it means | Example value |
|-------|--------------|---------------|
| **Application Insights** | Enable APM (performance monitoring) | `Yes` (always enable for prod) |
| **App Insights resource** | Existing or new | `appi-myapp-prod` |

### Tags Tab

| Field | What it means | Example value |
|-------|--------------|---------------|
| **Name** | Tag key | `environment` |
| **Value** | Tag value | `production` |

**Recommended tags for every resource:**

```
  environment = production / staging / dev
  team        = devops / backend / frontend
  cost-center = CC-1234
  project     = myapp
  created-by  = terraform / manual / bicep
```

> ⚠️ **Gotcha:** Tags are NOT inherited from resource group. Tag each resource individually, or use Azure Policy to auto-inherit.

---

## 1.2 App Service Configuration — Settings Tab

After creation, the **Configuration** blade has these sections:

### Application Settings (Environment Variables)

```
  These are environment variables injected into your app at runtime.

  ┌────────────────────────────┬──────────────────────────────────────┐
  │ Name                       │ Value                                │
  ├────────────────────────────┼──────────────────────────────────────┤
  │ DATABASE_URL               │ @Microsoft.KeyVault(SecretUri=...)  │
  │ REDIS_HOST                 │ redis-prod.redis.cache.windows.net  │
  │ APP_ENV                    │ production                           │
  │ WEBSITES_PORT              │ 8000 (for containers)                │
  └────────────────────────────┴──────────────────────────────────────┘

  The @Microsoft.KeyVault() syntax pulls secrets from Key Vault
  at runtime — no secrets in config!
```

```bash
# Set app settings via CLI
az webapp config appsettings set \
    --resource-group rg-myapp --name myapp-prod \
    --settings APP_ENV=production REDIS_HOST=redis-prod.redis.cache.windows.net

# Set Key Vault reference
az webapp config appsettings set \
    --resource-group rg-myapp --name myapp-prod \
    --settings "DATABASE_URL=@Microsoft.KeyVault(SecretUri=https://kv-prod.vault.azure.net/secrets/db-url/)"
```

### Connection Strings

```
  Legacy way to pass DB connections. Prefer App Settings instead.
  Supported types: SQLAzure, SQLServer, MySQL, PostgreSQL, Custom
```

### General Settings

| Setting | What it means | Values |
|---------|--------------|--------|
| **Stack** | Runtime | `.NET 8`, `Python 3.12`, `Node 20` |
| **Platform** | Architecture | `32-bit` or `64-bit` (use 64-bit for prod) |
| **Always On** | Keep app warm (no cold starts) | `On` for prod (requires B1+) |
| **HTTP version** | Protocol version | `2.0` (use HTTP/2 for performance) |
| **ARR affinity** | Sticky sessions (same user → same instance) | `Off` unless stateful |
| **HTTPS Only** | Redirect HTTP → HTTPS | `On` (always!) |
| **Minimum TLS** | Minimum TLS version | `1.2` (never use 1.0/1.1) |
| **FTP state** | FTP deployment access | `Disabled` (security risk) |
| **Remote debugging** | Attach VS debugger | `Off` in production |

```bash
# Enable Always On and HTTPS only
az webapp update --resource-group rg-myapp --name myapp-prod \
    --always-on true --https-only true

# Set minimum TLS version
az webapp config set --resource-group rg-myapp --name myapp-prod \
    --min-tls-version 1.2 --ftps-state Disabled
```

### Path Mappings

```
  Map URL paths to physical directories or Azure Storage.
  Example: /uploads → Azure File Share mount
```

---

## 1.3 Deployment Slots

**What are they?** Separate "copies" of your app running on the same App Service Plan. You deploy to a slot, test it, then **swap** it to production with zero downtime.

**How it works:**

```
  Production slot:   myapp-prod.azurewebsites.net     ← users hit this
  Staging slot:      myapp-prod-staging.azurewebsites.net

  Deploy flow:
  1. Push new code → staging slot
  2. Test staging URL (warm up the app)
  3. Swap staging ↔ production (instant, zero downtime)
  4. If broken → swap back (instant rollback)

  What happens during swap:
  ┌──────────┐                    ┌──────────┐
  │ Staging  │ ◄════ SWAP ═════► │Production│
  │ (v2 new) │                    │ (v1 old) │
  └──────────┘                    └──────────┘
  After swap:
  Production = v2 (new code, live traffic)
  Staging    = v1 (old code, available for rollback)
```

**Slot-specific vs slot-swappable settings:**

```
  ┌──────────────────────┬──────────────────────────────────┐
  │ SWAPPED (move with   │ STICKY (stay with slot)          │
  │ the code)            │                                  │
  ├──────────────────────┼──────────────────────────────────┤
  │ App code/binaries    │ Custom domain bindings            │
  │ App settings (unless │ SSL certificates                  │
  │   marked sticky)     │ Scale settings                    │
  │ Connection strings   │ Diagnostic settings               │
  │ Handler mappings     │ Settings marked as "slot setting" │
  └──────────────────────┴──────────────────────────────────┘
```

```bash
# Create a deployment slot
az webapp deployment slot create \
    --resource-group rg-myapp --name myapp-prod \
    --slot staging

# Deploy to staging slot
az webapp deploy --resource-group rg-myapp --name myapp-prod \
    --slot staging --src-path ./app.zip

# Swap staging → production
az webapp deployment slot swap \
    --resource-group rg-myapp --name myapp-prod \
    --slot staging --target-slot production

# Rollback (swap back)
az webapp deployment slot swap \
    --resource-group rg-myapp --name myapp-prod \
    --slot staging --target-slot production

# Mark a setting as slot-specific (sticky)
az webapp config appsettings set \
    --resource-group rg-myapp --name myapp-prod \
    --slot staging --slot-settings APP_ENV=staging
```

> ⚠️ **Gotcha:** Deployment slots require **S1 tier or higher**. Free and Basic tiers don't support slots. S1 = 5 slots, P1v3 = 20 slots.

---

## 1.4 Custom Domains & SSL

**Adding a custom domain:**

```
  1. Buy domain (e.g., myapp.com) from any registrar
  2. In DNS, add CNAME: www → myapp-prod.azurewebsites.net
     OR A record → App Service IP + TXT verification record
  3. In App Service → Custom domains → Add domain
  4. Azure validates DNS ownership
  5. Bind SSL certificate
```

```bash
# Add custom domain
az webapp config hostname add \
    --resource-group rg-myapp --webapp-name myapp-prod \
    --hostname www.myapp.com

# Create free managed SSL (Azure auto-renews)
az webapp config ssl bind \
    --resource-group rg-myapp --name myapp-prod \
    --certificate-thumbprint <thumbprint> --ssl-type SNI
```

> ⚠️ **Gotcha:** Free managed certificates only work for standard domains, not wildcard (*.myapp.com). For wildcards, use App Service Certificates or bring your own.

---

## 1.5 Networking & VNet Integration

**Outbound: VNet Integration (app → Azure resources)**

```
  Your App Service CAN'T reach resources in a VNet by default.
  VNet Integration creates a tunnel from App Service → your VNet.

  ┌──────────────┐                    ┌──────────────────┐
  │ App Service  │ ──VNet Integration──► VNet             │
  │ (public PaaS)│                    │  ├── SQL (PE)    │
  │              │                    │  ├── Redis (PE)  │
  │              │                    │  └── VM          │
  └──────────────┘                    └──────────────────┘

  Requires: S1+ tier, a dedicated /26 subnet (minimum)
```

**Inbound: Private Endpoint (users → app privately)**

```
  By default, App Service is accessible from the internet.
  A Private Endpoint makes it accessible ONLY from your VNet.

  Internet ──✗──► App Service (public access disabled)
  VNet     ──✓──► Private Endpoint (10.0.5.4) ──► App Service
```

```bash
# Enable VNet integration (outbound)
az webapp vnet-integration add \
    --resource-group rg-myapp --name myapp-prod \
    --vnet vnet-prod --subnet snet-app-integration

# Create private endpoint (inbound)
az network private-endpoint create \
    --resource-group rg-myapp --name pe-myapp \
    --vnet-name vnet-prod --subnet snet-pe \
    --private-connection-resource-id $APP_ID \
    --group-ids sites --connection-name conn-myapp
```

---

## 1.6 Scaling

**Scale Up (vertical) — change plan tier:**

```bash
az appservice plan update --resource-group rg-myapp \
    --name asp-myapp-prod --sku P1v3
```

**Scale Out (horizontal) — add instances:**

```bash
# Manual scale to 3 instances
az appservice plan update --resource-group rg-myapp \
    --name asp-myapp-prod --number-of-workers 3

# Auto-scale rule (CPU > 70% → add instance, < 30% → remove)
az monitor autoscale create \
    --resource-group rg-myapp --name autoscale-myapp \
    --resource asp-myapp-prod \
    --resource-type Microsoft.Web/serverfarms \
    --min-count 2 --max-count 10 --count 2

az monitor autoscale rule create \
    --resource-group rg-myapp --autoscale-name autoscale-myapp \
    --condition "CpuPercentage > 70 avg 5m" \
    --scale out 1

az monitor autoscale rule create \
    --resource-group rg-myapp --autoscale-name autoscale-myapp \
    --condition "CpuPercentage < 30 avg 5m" \
    --scale in 1
```

---

## 1.7 Backups & Diagnostics

**App Service Backup (S1+ required):**

```bash
# Configure backup (daily, keep 30 days)
az webapp config backup create \
    --resource-group rg-myapp --webapp-name myapp-prod \
    --backup-name daily-backup \
    --container-url "https://stdemo.blob.core.windows.net/backups?sv=..." \
    --frequency 1d --retain-one true --retention 30
```

**Diagnostics & Logging:**

```bash
# Enable all logs
az webapp log config --resource-group rg-myapp --name myapp-prod \
    --application-logging filesystem --level verbose \
    --web-server-logging filesystem \
    --detailed-error-messages true --failed-request-tracing true

# Stream logs live
az webapp log tail --resource-group rg-myapp --name myapp-prod
```

---

## 1.8 App Service — Example Scenarios

### Scenario 1: Zero-downtime deployment for e-commerce site

```
  PROBLEM: Deploying new code causes 30-second downtime.

  SOLUTION: Deployment slots + swap.

  ┌────────────────────────────────────────────────────┐
  │  1. Deploy v2 → staging slot                       │
  │  2. Run smoke tests against staging URL            │
  │  3. Warm up staging (App Insights: 0 errors)       │
  │  4. Swap staging ↔ production                      │
  │  5. Monitor production for 15 minutes              │
  │  6. If errors spike → swap back (instant rollback) │
  └────────────────────────────────────────────────────┘

  Result: Zero downtime, instant rollback capability.
  Tier required: S1 or higher.
```

### Scenario 2: Secure internal API (no internet access)

```
  PROBLEM: API should only be accessible from internal apps.

  ┌──────────────────────────────────────────────────────┐
  │  VNet (10.0.0.0/16)                                 │
  │                                                      │
  │  snet-pe (10.0.5.0/26)                              │
  │  └── Private Endpoint ──► API App Service            │
  │       (10.0.5.4)          (public access: OFF)       │
  │                                                      │
  │  snet-app (10.0.1.0/24)                             │
  │  └── Frontend App ──► calls 10.0.5.4:443 ──► API   │
  │      (VNet integrated)                               │
  │                                                      │
  │  Internet ──✗──► API (blocked, no public access)    │
  └──────────────────────────────────────────────────────┘

  Components: VNet, Private Endpoint, VNet Integration, Private DNS Zone.
```

### Scenario 3: Multi-region app with auto-failover

```
  PROBLEM: App must survive a full region outage (99.99% uptime).

  ┌─────────────────────────────────────────────────────┐
  │  Azure Front Door (global)                          │
  │       │                                             │
  │       ├── East US (primary, weight: 80%)            │
  │       │   └── App Service (P1v3, 2 instances)      │
  │       │       └── Azure SQL (failover group, primary)│
  │       │                                             │
  │       └── West US (secondary, weight: 20%)          │
  │           └── App Service (P1v3, 2 instances)      │
  │               └── Azure SQL (failover, secondary)  │
  │                                                     │
  │  Failover: Front Door detects East US down →        │
  │  routes 100% to West US. SQL auto-failover.         │
  └─────────────────────────────────────────────────────┘
```

---

# Chapter 2 — Azure Key Vault Deep Dive

> Key Vault is Azure's centralized secrets, keys, and certificates manager. This chapter covers every creation field, operational tasks, and real-world scenarios.

---

## 2.1 Creating a Key Vault — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Subscription** | Billing account | `Pay-As-You-Go` | — |
| **Resource Group** | Logical container | `rg-myapp-prod` | Same RG as the app that consumes it |
| **Vault name** | Globally unique name | `kv-myapp-prod` | 3-24 chars, alphanumeric + hyphens. Globally unique |
| **Region** | Datacenter location | `East US` | Same region as consumers for latency |
| **Pricing tier** | Standard or Premium | `Standard` | Premium adds HSM-backed keys ($1/key/month) |

### Access Configuration Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Permission model** | How to control access | `Azure RBAC` (recommended) or `Vault access policy` (legacy) |
| **Resource access** | Enable for specific services | Enable for: Azure VMs, ARM templates, Azure Disk Encryption |

**RBAC vs Access Policies:**

```
  ┌──────────────────────┬────────────────────────────────────────┐
  │ RBAC (recommended)   │ Access Policies (legacy)               │
  ├──────────────────────┼────────────────────────────────────────┤
  │ Uses Azure roles     │ Per-vault policy (not visible in IAM) │
  │ Consistent with all  │ Separate permission model              │
  │ Azure resources      │ Hard to audit at scale                 │
  │ Supports Conditional │ No Conditional Access support          │
  │ Access               │                                        │
  │ Auditable in IAM     │ Must check vault-level settings       │
  └──────────────────────┴────────────────────────────────────────┘

  Always use RBAC for new Key Vaults.
```

**Key RBAC roles:**

```
  ┌──────────────────────────────┬────────────────────────────────┐
  │ Role                         │ What it allows                 │
  ├──────────────────────────────┼────────────────────────────────┤
  │ Key Vault Administrator      │ Full manage (secrets+keys+certs)│
  │ Key Vault Secrets User       │ Read secrets only              │
  │ Key Vault Secrets Officer    │ Read + write secrets           │
  │ Key Vault Crypto User        │ Use keys for encrypt/decrypt   │
  │ Key Vault Certificates Officer│ Manage certificates           │
  │ Key Vault Reader             │ Read metadata only (not values)│
  └──────────────────────────────┴────────────────────────────────┘
```

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Public access** | Can internet reach the vault? | `All networks`, `Selected networks`, `Disabled` |
| **Virtual networks** | Allow from specific VNets/subnets | Select VNet + subnet |
| **Private endpoint** | Access via private IP in VNet | Creates PE — use for production |

```
  Development:  Public access = All networks (easier testing)
  Production:   Public access = Disabled + Private Endpoint only
```

### Tags Tab

Same as all resources — add `environment`, `team`, `cost-center`, etc.

---

## 2.2 Key Vault Operations & Configuration

### Secrets — CRUD Operations

```bash
# Create/Update a secret
az keyvault secret set --vault-name kv-myapp-prod \
    --name "db-password" --value "P@ssw0rd123!"

# Read a secret
az keyvault secret show --vault-name kv-myapp-prod \
    --name "db-password" --query value -o tsv

# List all secrets (names only, not values)
az keyvault secret list --vault-name kv-myapp-prod -o table

# Delete a secret (soft-deleted, recoverable)
az keyvault secret delete --vault-name kv-myapp-prod --name "db-password"

# Recover a soft-deleted secret
az keyvault secret recover --vault-name kv-myapp-prod --name "db-password"

# Permanently delete (purge)
az keyvault secret purge --vault-name kv-myapp-prod --name "db-password"

# List deleted secrets
az keyvault secret list-deleted --vault-name kv-myapp-prod -o table

# Set secret with expiration date
az keyvault secret set --vault-name kv-myapp-prod \
    --name "api-key" --value "abc123" \
    --expires "2025-12-31T23:59:59Z"

# Set secret with specific content type
az keyvault secret set --vault-name kv-myapp-prod \
    --name "cert-pem" --file ./cert.pem \
    --content-type "application/x-pem-file"
```

### Soft Delete & Purge Protection

```
  ┌──────────────────────┬───────────────────────────────────────┐
  │ Feature              │ What it does                          │
  ├──────────────────────┼───────────────────────────────────────┤
  │ Soft delete           │ Deleted items recoverable for 7-90   │
  │ (default: ON)        │ days. CANNOT be disabled once enabled │
  │                      │                                       │
  │ Purge protection     │ Even admins can't permanently delete  │
  │ (default: OFF)       │ during retention period. Enable for   │
  │                      │ production!                           │
  └──────────────────────┴───────────────────────────────────────┘
```

```bash
# Enable purge protection (irreversible!)
az keyvault update --name kv-myapp-prod \
    --enable-purge-protection true

# Set soft-delete retention (days)
az keyvault update --name kv-myapp-prod \
    --retention-days 90
```

### Key Vault References in App Service

```
  Instead of storing secrets in App Service config:
  ✗ DATABASE_URL = "Server=sql.database.windows.net;Password=P@ss123"

  Use Key Vault references:
  ✓ DATABASE_URL = @Microsoft.KeyVault(SecretUri=https://kv-myapp-prod.vault.azure.net/secrets/db-url/)

  Prerequisites:
  1. App Service has system-assigned managed identity
  2. Managed identity has "Key Vault Secrets User" role on the vault
  3. App setting value uses the @Microsoft.KeyVault() syntax
```

---

## 2.3 Key Vault — Scenarios

### Scenario 1: Centralized secret management for microservices

```
  ┌─────────────────────────────────────────────────────┐
  │  Key Vault (kv-myapp-prod)                         │
  │  ├── db-password                                    │
  │  ├── redis-connection                               │
  │  ├── api-key-stripe                                 │
  │  └── jwt-signing-key                                │
  │       │           │           │                     │
  │       ▼           ▼           ▼                     │
  │  App Service   Function   AKS Pod                   │
  │  (MI: id-web)  (MI: id-fn) (MI: id-aks)            │
  │                                                     │
  │  Each service uses its own managed identity         │
  │  Each identity has ONLY the secrets it needs        │
  │  (least privilege via RBAC)                         │
  └─────────────────────────────────────────────────────┘
```

### Scenario 2: Automated secret rotation

```
  PROBLEM: API key expires every 90 days.

  SOLUTION:
  1. Key Vault raises "SecretNearExpiry" event (Event Grid)
  2. Event Grid triggers an Azure Function
  3. Function calls the external API to generate a new key
  4. Function updates the secret in Key Vault
  5. App Service auto-reloads the new secret value

  Key Vault ──► Event Grid ──► Function ──► New API key ──► Key Vault
      └── "SecretNearExpiry"                                    │
                                                        App Service reads
                                                        updated secret
```

> ⚠️ **Gotcha:** Key Vault has a rate limit of **1,000 operations per 10 seconds** per vault. If you have high-volume reads, cache secrets in your app (refresh every 5-15 min).

---

# Chapter 3 — Azure Storage Accounts Deep Dive

> Storage Accounts hold blobs, files, tables, and queues. This chapter covers every configuration field and operational task.

---

## 3.1 Creating a Storage Account — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Subscription** | Billing account | `Pay-As-You-Go` | — |
| **Resource Group** | Container | `rg-myapp-prod` | — |
| **Storage account name** | Globally unique | `stmyappprod2024` | 3-24 chars, lowercase + numbers ONLY. No dashes/uppercase |
| **Region** | Datacenter | `East US` | Same region as consumers |
| **Performance** | Standard or Premium | `Standard` | Standard=HDD, Premium=SSD (for low latency) |
| **Redundancy** | Replication level | `LRS` / `ZRS` / `GRS` / `GZRS` | See replication table below |

**Performance comparison:**

```
  Standard (HDD):              Premium (SSD):
  ─────────────────            ──────────────────
  General purpose              Block blobs, Files, or Page blobs
  Blobs, Files, Tables, Queues Block blobs ONLY (or Files/Pages)
  ~60 IOPS per blob            ~10,000+ IOPS
  ~$0.018/GB/month             ~$0.15/GB/month
  Use for: most workloads      Use for: high-IOPS, low-latency
```

### Advanced Tab

| Field | What it means | Default | Recommended |
|-------|--------------|---------|-------------|
| **Require secure transfer** | HTTPS only (no HTTP) | `Enabled` | Keep enabled (security) |
| **Allow blob public access** | Anonymous read on containers | `Disabled` | Keep disabled unless hosting static site |
| **Enable storage account key access** | Allow key-based auth | `Enabled` | Disable for strict RBAC-only environments |
| **Default access tier** | Hot or Cool | `Hot` | Hot for frequently accessed, Cool for backups |
| **Enable hierarchical namespace** | Data Lake Storage Gen2 | `Disabled` | Enable ONLY for big data / analytics |
| **Minimum TLS version** | Minimum accepted TLS | `1.2` | Always 1.2 |
| **Permitted scope for copy operations** | Limit copy sources | `From any storage account` | Restrict for compliance |

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Network access** | Who can access | `Enable from all networks`, `Enable from selected VNets`, `Disable public access` |
| **Virtual networks** | Allowed VNets/subnets | Add service endpoint or private endpoint |
| **Private endpoints** | Access via private IP | Create PE for production |
| **Network routing** | Microsoft or Internet routing | `Microsoft routing` (default, faster) |

```
  Development:  All networks (easier testing)
  Production:   Selected VNets + Private Endpoint
                + Disable public access
```

### Data Protection Tab

| Field | What it means | Default | Notes |
|-------|--------------|---------|-------|
| **Enable soft delete for blobs** | Recover deleted blobs | 7 days | Production: set to 30-90 days |
| **Enable soft delete for containers** | Recover deleted containers | 7 days | Production: 30+ days |
| **Enable soft delete for file shares** | Recover deleted shares | 7 days | — |
| **Enable versioning for blobs** | Keep previous versions | `Disabled` | Enable for important data |
| **Enable change feed** | Log all blob changes | `Disabled` | Enable for audit/replication |
| **Enable point-in-time restore** | Restore blobs to any time | `Disabled` | Requires versioning + change feed |

### Encryption Tab

| Field | What it means | Default |
|-------|--------------|---------|
| **Encryption type** | Microsoft-managed or customer-managed keys | `Microsoft-managed` |
| **Infrastructure encryption** | Double encryption | `Disabled` |

```
  Microsoft-managed keys = Azure handles encryption (recommended for most)
  Customer-managed keys (CMK) = You provide the key from Key Vault
                                Required for some compliance (HIPAA, PCI)
```

### Tags Tab

Standard tags: `environment`, `team`, `cost-center`, `project`

---

## 3.2 Storage Account — Operations

### Container Operations (Blob Storage)

```bash
# Create storage account
az storage account create --name stmyappprod --resource-group rg-myapp \
    --location eastus --sku Standard_ZRS --kind StorageV2 \
    --access-tier Hot --min-tls-version TLS1_2 \
    --allow-blob-public-access false

# Create a container (private access)
az storage container create --name uploads --account-name stmyappprod \
    --auth-mode login

# Upload blob
az storage blob upload --account-name stmyappprod \
    --container-name uploads --name report.pdf --file ./report.pdf \
    --auth-mode login

# Download blob
az storage blob download --account-name stmyappprod \
    --container-name uploads --name report.pdf --file ./downloaded.pdf

# List blobs
az storage blob list --account-name stmyappprod \
    --container-name uploads -o table --auth-mode login

# Set blob access tier
az storage blob set-tier --account-name stmyappprod \
    --container-name uploads --name old-report.pdf --tier Cool

# Delete blob (soft delete keeps it recoverable)
az storage blob delete --account-name stmyappprod \
    --container-name uploads --name report.pdf

# Restore soft-deleted blob
az storage blob undelete --account-name stmyappprod \
    --container-name uploads --name report.pdf
```

### Storage Firewall & Network Rules

```bash
# Restrict to specific VNet/subnet
az storage account network-rule add --account-name stmyappprod \
    --resource-group rg-myapp --vnet-name vnet-prod --subnet snet-app

# Set default action to deny
az storage account update --name stmyappprod --resource-group rg-myapp \
    --default-action Deny

# Allow specific IP
az storage account network-rule add --account-name stmyappprod \
    --resource-group rg-myapp --ip-address 203.0.113.1

# Check network rules
az storage account network-rule list --account-name stmyappprod -o table
```

### Static Website Hosting

```bash
# Enable static website
az storage blob service-properties update --account-name stmyappprod \
    --static-website --index-document index.html --404-document 404.html

# Upload website files to $web container
az storage blob upload-batch --account-name stmyappprod \
    --destination '$web' --source ./build/

# Get the website URL
az storage account show --name stmyappprod \
    --query "primaryEndpoints.web" -o tsv
# Output: https://stmyappprod.z13.web.core.windows.net/
```

---

## 3.3 Storage Account — Scenarios

### Scenario 1: Secure file upload with SAS tokens

```
  PROBLEM: External users need to upload files but shouldn't
  have full storage access.

  ┌──────────────────────────────────────────────────────┐
  │  User's browser                                      │
  │       │                                              │
  │       │ 1. Request upload URL from API                │
  │       ▼                                              │
  │  API (App Service)                                   │
  │       │ 2. Generate SAS token (write-only, 15 min)   │
  │       │    Container: uploads                         │
  │       │    Permissions: Create only                   │
  │       │    Expiry: 15 minutes                         │
  │       ▼                                              │
  │  Returns: https://st.blob.../uploads/file?sv=...     │
  │       │                                              │
  │  User │ 3. Upload directly to Blob Storage            │
  │       └──────────► Blob Storage                      │
  │                    (API never handles the file!)      │
  └──────────────────────────────────────────────────────┘

  Benefits: API doesn't need to handle large files.
  User gets a short-lived, scoped token.
```

### Scenario 2: Data lifecycle for cost optimization

```
  ┌────────────────────────────────────────────────────┐
  │  Lifecycle Policy                                  │
  │                                                    │
  │  Day 0-30:   HOT tier    ($0.018/GB)              │
  │  Day 30-90:  COOL tier   ($0.010/GB)  ← 44% less │
  │  Day 90-180: COLD tier   ($0.0045/GB) ← 75% less │
  │  Day 180+:   ARCHIVE     ($0.00099/GB)← 95% less │
  │  Day 365:    DELETE                                │
  │                                                    │
  │  For 1TB of data:                                  │
  │  All Hot = $18.43/month                            │
  │  With lifecycle = ~$5/month (73% savings!)         │
  └────────────────────────────────────────────────────┘
```

### Scenario 3: Cross-region backup with GRS

```
  ┌──────────────────┐         ┌──────────────────┐
  │  East US          │         │  West US (paired) │
  │  (primary)        │════════►│  (secondary)      │
  │                  │  auto    │                  │
  │  stmyappprod     │  sync    │  stmyappprod     │
  │  ├── uploads/    │         │  ├── uploads/     │
  │  ├── backups/    │         │  ├── backups/     │
  │  └── logs/       │         │  └── logs/        │
  └──────────────────┘         └──────────────────┘

  GRS = 6 copies total (3 local + 3 paired region)
  RA-GRS = same + READ access from secondary region

  If East US goes down entirely:
  - RA-GRS: apps can read from West US immediately
  - GRS: must wait for Microsoft to initiate failover
```

> ⚠️ **Gotcha:** Storage account names are limited to 24 chars, lowercase + digits only. Plan naming carefully — you can't rename later, only recreate.

---

# Chapter 4 — Azure Databases Deep Dive

> Managed databases — Azure handles patching, backups, HA. You manage schema and data.

---

## 4.1 Azure SQL Database — Every Field Explained

### Creating a SQL Server (logical server)

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Server name** | Globally unique hostname | `sql-myapp-prod` | Becomes `sql-myapp-prod.database.windows.net` |
| **Location** | Datacenter | `East US` | Must match apps for latency |
| **Authentication** | How to log in | `Use both SQL and Microsoft Entra authentication` | Prefer Entra-only for production |
| **Server admin login** | SQL admin username | `sqladmin` | Used for initial setup only |
| **Password** | SQL admin password | `P@ssw0rd123!` | 8+ chars, mix of upper/lower/digit/special |
| **Microsoft Entra admin** | Entra ID admin account | `dba-group@company.com` | Set a group, not individual user |

### Creating a Database (on the server)

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Database name** | Name of this database | `db-myapp` | Not globally unique, just unique per server |
| **Compute + Storage** | How much power | See purchasing models below | Biggest cost decision |
| **Backup storage redundancy** | Where backups go | `Geo-redundant` | LRS (cheapest), ZRS, GRS (safest) |
| **Collation** | String sorting rules | `SQL_Latin1_General_CP1_CI_AS` | Default is fine for most apps |

**Purchasing models compared:**

```
  ┌───────────────────┬───────────────────────────────────────────────┐
  │ DTU MODEL         │ VCORE MODEL                                  │
  ├───────────────────┼───────────────────────────────────────────────┤
  │ Bundled CPU+IO+   │ Choose CPU cores + RAM separately            │
  │ memory            │                                               │
  │                   │ Tiers:                                        │
  │ Basic: 5 DTUs     │ General Purpose (remote storage, S3 equiv)   │
  │   ~$5/mo          │ Business Critical (local SSD, 99.995% SLA)   │
  │ Standard: 10-3000 │ Hyperscale (up to 100TB, on-demand scaling)  │
  │   ~$15-$2,500/mo  │                                               │
  │ Premium: 125-4000 │ Compute:                                      │
  │   ~$465-$14K/mo   │ Provisioned (always running, predictable)     │
  │                   │ Serverless (auto-pause, pay only when active) │
  │                   │                                               │
  │ Simple pricing    │ More control, reserved instance discounts     │
  │ Best for: small   │ Best for: production, cost optimization      │
  └───────────────────┴───────────────────────────────────────────────┘

  Recommendation: vCore Serverless for dev/test, vCore GP Provisioned for prod
```

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Connectivity method** | How apps connect | `Public endpoint` or `Private endpoint` |
| **Allow Azure services** | Let other Azure services connect | `Yes` for dev, `No` for secure prod |
| **Add current client IP** | Whitelist your IP for testing | `Yes` (add your IP to firewall) |

### Security Tab

| Field | What it means | Default |
|-------|--------------|---------|
| **Microsoft Defender for SQL** | Threat detection + vulnerability assessment | Free trial then $15/server/mo |
| **Transparent Data Encryption (TDE)** | Encrypt data at rest | `Enabled` (always on, can't disable) |
| **Ledger** | Tamper-proof table (blockchain-like audit) | `Disabled` |

---

## 4.2 Azure SQL — Operations

### Firewall & Networking

```bash
# Create SQL server
az sql server create --name sql-myapp-prod --resource-group rg-myapp \
    --location eastus --admin-user sqladmin \
    --admin-password "P@ssw0rd123!"

# Set Entra admin
az sql server ad-admin create --resource-group rg-myapp \
    --server-name sql-myapp-prod \
    --display-name "DBA Team" --object-id $ENTRA_GROUP_ID

# Add firewall rule (your IP)
az sql server firewall-rule create --resource-group rg-myapp \
    --server sql-myapp-prod --name AllowMyIP \
    --start-ip-address 203.0.113.1 --end-ip-address 203.0.113.1

# Allow Azure services (for App Service without VNet integration)
az sql server firewall-rule create --resource-group rg-myapp \
    --server sql-myapp-prod --name AllowAzure \
    --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Create private endpoint (production)
az network private-endpoint create --resource-group rg-myapp \
    --name pe-sql-myapp --vnet-name vnet-prod --subnet snet-pe \
    --private-connection-resource-id $SQL_SERVER_ID \
    --group-ids sqlServer --connection-name conn-sql
```

### Database CRUD & Management

```bash
# Create database (serverless, auto-pause after 1 hour)
az sql db create --resource-group rg-myapp --server sql-myapp-prod \
    --name db-myapp --edition GeneralPurpose \
    --compute-model Serverless --auto-pause-delay 60 \
    --min-capacity 0.5 --capacity 2 --family Gen5 \
    --backup-storage-redundancy Geo

# Scale up a database
az sql db update --resource-group rg-myapp --server sql-myapp-prod \
    --name db-myapp --capacity 4

# Point-in-time restore (restore to 30 minutes ago)
az sql db restore --resource-group rg-myapp --server sql-myapp-prod \
    --dest-name db-myapp-restored \
    --name db-myapp --time "2024-06-15T10:30:00Z"

# Copy a database (for testing)
az sql db copy --resource-group rg-myapp --server sql-myapp-prod \
    --name db-myapp --dest-name db-myapp-copy

# Enable auditing (send to Log Analytics)
az sql server audit-policy update --resource-group rg-myapp \
    --name sql-myapp-prod --state Enabled \
    --lats Enabled --lawri $LOG_ANALYTICS_ID

# List databases
az sql db list --resource-group rg-myapp --server sql-myapp-prod -o table
```

### Failover Groups (Geo-Replication)

```
  Primary (East US)              Secondary (West US)
  ─────────────────              ──────────────────
  sql-myapp-prod     ═══════►   sql-myapp-dr
  └── db-myapp       auto-sync  └── db-myapp (read-only)

  Failover Group DNS:
  Read-write: fog-myapp.database.windows.net → always points to primary
  Read-only:  fog-myapp.secondary.database.windows.net → secondary

  On failover: DNS auto-switches. App connection string never changes!
```

```bash
# Create failover group
az sql failover-group create --resource-group rg-myapp \
    --name fog-myapp --server sql-myapp-prod \
    --partner-server sql-myapp-dr --partner-resource-group rg-myapp-dr \
    --add-db db-myapp --failover-policy Automatic \
    --grace-period 1

# Manual failover (planned)
az sql failover-group set-primary --resource-group rg-myapp-dr \
    --server sql-myapp-dr --name fog-myapp
```

> ⚠️ **Gotcha:** Serverless auto-pause causes ~60 seconds cold start. Don't use for production APIs with strict latency requirements. Use `--auto-pause-delay -1` to disable auto-pause.

---

## 4.2 Azure SQL — Scenarios

### Scenario 1: Secure app-to-database connection

```
  ┌───────────────────────────────────────────────────────────┐
  │  VNet (10.0.0.0/16)                                      │
  │                                                           │
  │  snet-app (10.0.1.0/24)                                  │
  │  └── App Service ──VNet Integration──┐                   │
  │      (Managed Identity: id-web)      │                   │
  │                                       │                   │
  │  snet-pe (10.0.5.0/26)              │                   │
  │  └── Private Endpoint ◄──────────────┘                   │
  │       (10.0.5.5)                                          │
  │       │                                                   │
  │       └── Azure SQL (sql-myapp-prod)                     │
  │           (public access: DISABLED)                       │
  │                                                           │
  │  Auth flow:                                               │
  │  App → DefaultAzureCredential → Entra ID → token → SQL  │
  │  (No password stored anywhere!)                           │
  └───────────────────────────────────────────────────────────┘
```

---

## 4.3 Azure Cosmos DB — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Account Name** | Globally unique | `cosmos-myapp-prod` | 3-44 chars, lowercase + hyphens |
| **API** | Data model type | See table below | Choose at creation, CANNOT change later |
| **Capacity mode** | Provisioned or Serverless | `Serverless` for dev, `Provisioned` for prod | Serverless = pay per request, max 1M RU/s |
| **Global distribution** | Multi-region writes | Add regions after creation | Each region adds cost |

**API options (choose at creation — cannot change later!):**

```
  ┌────────────────────┬──────────────────────────────────────────┐
  │ API                │ Use when                                 │
  ├────────────────────┼──────────────────────────────────────────┤
  │ NoSQL (document)   │ Default choice. JSON documents, SQL-like │
  │                    │ queries. Most flexible                   │
  │ MongoDB            │ Migrating from MongoDB. Wire compatible  │
  │ Cassandra          │ Migrating from Apache Cassandra          │
  │ Gremlin (graph)    │ Graph relationships (social networks)    │
  │ Table              │ Migrating from Azure Table Storage       │
  │ PostgreSQL         │ Distributed PostgreSQL (Citus)           │
  └────────────────────┴──────────────────────────────────────────┘

  95% of new projects → use NoSQL API.
```

### Consistency Tab

```
  ┌────────────────────┬─────────────────────────────────────────┐
  │ Level              │ What it means (plain English)            │
  ├────────────────────┼─────────────────────────────────────────┤
  │ Strong             │ Everyone sees the same data at all times │
  │                    │ (slowest, highest RU cost)               │
  │ Bounded Staleness  │ Data can be up to N seconds/versions old │
  │                    │ (predictable lag)                         │
  │ Session (default)  │ YOUR reads see YOUR writes immediately   │
  │                    │ Others may be slightly behind (best 80%) │
  │ Consistent Prefix  │ You see writes in order, but may be late │
  │ Eventual           │ Eventually everyone sees everything      │
  │                    │ (fastest, cheapest RU cost)              │
  └────────────────────┴─────────────────────────────────────────┘

  Default (Session) is correct for 80% of use cases.
  Strong consistency doubles RU cost.
```

### Networking, Backup & Encryption tabs

Same patterns as other services: public/private endpoint, continuous backups, Microsoft-managed or CMK encryption.

---

## 4.4 Cosmos DB — Operations & Partition Keys

### Choosing the Right Partition Key

```
  The MOST important decision in Cosmos DB.

  ┌─────────────────────┬──────────────────────────────────────┐
  │ Good partition keys  │ Bad partition keys                   │
  ├─────────────────────┼──────────────────────────────────────┤
  │ userId (many users) │ status ("active"/"inactive" = 2 vals)│
  │ tenantId            │ country (few values = hot partitions) │
  │ deviceId            │ date (all today's data = 1 partition) │
  │ orderId             │ id (unique but kills cross-partition) │
  └─────────────────────┴──────────────────────────────────────┘

  Rule: Pick a key with HIGH cardinality (many distinct values)
  that is used in MOST queries as a filter.
```

```bash
# Create Cosmos account
az cosmosdb create --name cosmos-myapp-prod --resource-group rg-myapp \
    --locations regionName=eastus failoverPriority=0 \
    --default-consistency-level Session \
    --enable-automatic-failover true

# Create database + container with partition key
az cosmosdb sql database create \
    --account-name cosmos-myapp-prod --resource-group rg-myapp \
    --name appdb

az cosmosdb sql container create \
    --account-name cosmos-myapp-prod --resource-group rg-myapp \
    --database-name appdb --name users \
    --partition-key-path "/userId" \
    --throughput 400

# Enable autoscale (100-4000 RU/s)
az cosmosdb sql container throughput update \
    --account-name cosmos-myapp-prod --resource-group rg-myapp \
    --database-name appdb --name users \
    --max-throughput 4000
```

> ⚠️ **Gotcha:** Cross-partition queries are expensive. If you query without the partition key, Cosmos fans out to ALL partitions. Always include the partition key in your WHERE clause.

---

## 4.5 PostgreSQL Flexible Server — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Server name** | Unique in region | `pg-myapp-prod` | Becomes `pg-myapp-prod.postgres.database.azure.com` |
| **Region** | Datacenter | `East US` | — |
| **PostgreSQL version** | Engine version | `16` | Use latest stable |
| **Workload type** | Sizing preset | `Development` / `Production (Small/Medium)` / `Production (Large)` | Sets default SKU |
| **Compute + storage** | VM size | See tiers below | — |
| **Admin username** | Postgres admin | `pgadmin` | — |
| **Password** | Admin password | `P@ssw0rd123!` | — |

**Compute tiers:**

```
  ┌──────────────┬───────────┬──────────┬────────────────────────┐
  │ Tier         │ CPU       │ $/month  │ Use case               │
  ├──────────────┼───────────┼──────────┼────────────────────────┤
  │ Burstable    │ 1-20 vCores│ $13-$370│ Dev/test, low traffic  │
  │ (B-series)   │           │          │ CPU bursts as needed   │
  ├──────────────┼───────────┼──────────┤                        │
  │ General Purp │ 2-96 vCores│$125-$6K │ Production, balanced   │
  │ (D-series)   │           │          │ workloads              │
  ├──────────────┼───────────┼──────────┤                        │
  │ Memory Opt   │ 2-96 vCores│$150-$7K │ Large datasets,        │
  │ (E-series)   │           │          │ in-memory analytics    │
  └──────────────┴───────────┴──────────┴────────────────────────┘
```

### High Availability Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **HA mode** | Standby replica | `Disabled`, `Same zone`, `Zone redundant` |

```
  Zone-redundant HA:
  ┌──────────────────┐         ┌──────────────────┐
  │  Zone 1 (primary) │         │  Zone 2 (standby) │
  │  pg-myapp-prod    │══sync══►│  pg-myapp-prod    │
  │  (read/write)     │         │  (auto-failover)  │
  └──────────────────┘         └──────────────────┘
  Automatic failover: ~60-120 seconds.
```

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Connectivity** | `Public access` or `Private access (VNet)` | Private for production |
| **Private DNS zone** | Resolves server name to private IP | `privatelink.postgres.database.azure.com` |

```bash
# Create PostgreSQL Flexible Server (private access)
az postgres flexible-server create \
    --resource-group rg-myapp --name pg-myapp-prod \
    --location eastus --admin-user pgadmin \
    --admin-password "P@ssw0rd123!" \
    --sku-name Standard_D2ds_v4 --tier GeneralPurpose \
    --storage-size 128 --version 16 \
    --vnet vnet-prod --subnet snet-db \
    --private-dns-zone $DNS_ZONE_ID

# Enable HA
az postgres flexible-server update --resource-group rg-myapp \
    --name pg-myapp-prod --high-availability ZoneRedundant

# Create a database
az postgres flexible-server db create --resource-group rg-myapp \
    --server-name pg-myapp-prod --database-name myappdb

# Enable Entra ID authentication
az postgres flexible-server parameter set \
    --resource-group rg-myapp --server-name pg-myapp-prod \
    --name azure.extensions --value "pgcrypto,uuid-ossp"

# Backup: configure retention (default 7 days, max 35)
az postgres flexible-server update --resource-group rg-myapp \
    --name pg-myapp-prod --backup-retention 35

# Point-in-time restore
az postgres flexible-server restore --resource-group rg-myapp \
    --name pg-myapp-restored --source-server pg-myapp-prod \
    --restore-time "2024-06-15T10:30:00Z"
```

---

## 4.6 Database Decision Guide

```
  ┌─────────────────┬──────────────┬──────────────┬─────────────────┐
  │                 │ Azure SQL    │ Cosmos DB    │ PostgreSQL Flex │
  ├─────────────────┼──────────────┼──────────────┼─────────────────┤
  │ Type            │ Relational   │ NoSQL (multi)│ Relational      │
  │ Query language  │ T-SQL        │ SQL-like/API │ SQL (Postgres)  │
  │ Global distrib  │ Failover grp │ Built-in     │ Read replicas   │
  │ Latency         │ ~5-10ms      │ <10ms global │ ~5-10ms         │
  │ Max size        │ 4TB (100TB*) │ Unlimited    │ 16TB            │
  │ Serverless      │ Yes          │ Yes          │ No (Burstable)  │
  │ Open source     │ No           │ No           │ Yes             │
  │ Best for        │ .NET apps,   │ Global apps, │ Open-source     │
  │                 │ ACID, joins  │ high scale   │ apps, JSON+SQL  │
  │ Starting cost   │ ~$5/mo       │ ~$24/mo      │ ~$13/mo         │
  └─────────────────┴──────────────┴──────────────┴─────────────────┘

  * Hyperscale tier
```

---

# Chapter 5 — Azure Functions Deep Dive

> Functions = serverless compute. Run code on demand without managing servers. Pay only when code runs.

---

## 5.1 Creating a Function App — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Subscription** | Billing account | `Pay-As-You-Go` | — |
| **Resource Group** | Container | `rg-myapp-prod` | — |
| **Function App name** | Globally unique | `func-myapp-prod` | Becomes `func-myapp-prod.azurewebsites.net` |
| **Runtime stack** | Language | `.NET 8`, `Python 3.11`, `Node.js 20`, `Java 17` | Must match your code |
| **Version** | Runtime version | `~4` (v4) | Use latest |
| **Region** | Datacenter | `East US` | Same as related services |
| **Operating System** | Linux or Windows | `Linux` | Linux = cheaper, recommended for Python/Node |

### Hosting Tab

| Field | What it means | Values | Notes |
|-------|--------------|--------|-------|
| **Plan type** | How you pay and scale | See table below | Biggest decision |
| **Storage account** | Required for triggers/state | `stfuncmyapp` | Auto-created or select existing |

**Hosting plans compared:**

```
  ┌──────────────────┬────────────────────────────────────────────────┐
  │ CONSUMPTION      │ Pay per execution. Scale 0 → 200 instances.   │
  │ (Serverless)     │ Cold start: 1-3 seconds.                      │
  │                  │ Cost: $0.20 per million executions + compute   │
  │                  │ Free grant: 1M executions + 400K GB-s/month   │
  │                  │ Best for: event-driven, sporadic workloads     │
  ├──────────────────┼────────────────────────────────────────────────┤
  │ FLEX CONSUMPTION │ Pay per execution but with reserved instances. │
  │                  │ Always-ready instances eliminate cold starts.  │
  │                  │ VNet integration supported.                    │
  │                  │ Best for: production serverless with VNet      │
  ├──────────────────┼────────────────────────────────────────────────┤
  │ PREMIUM (EP1-3)  │ Pre-warmed instances (no cold starts).        │
  │                  │ VNet integration, unlimited execution time.    │
  │                  │ Scale: 1 → 100 instances.                     │
  │                  │ Cost: ~$160+/month (always running)           │
  │                  │ Best for: enterprise, latency-sensitive        │
  ├──────────────────┼────────────────────────────────────────────────┤
  │ APP SERVICE PLAN │ Runs on an existing App Service Plan.         │
  │ (Dedicated)      │ No additional cost if plan has spare capacity.│
  │                  │ Predictable cost, no scale to zero.           │
  │                  │ Best for: existing plans with spare resources  │
  └──────────────────┴────────────────────────────────────────────────┘
```

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Enable public access** | Internet can trigger HTTP functions | `On` (default) |
| **VNet integration** | Functions can reach VNet resources | Premium/Flex plan only |
| **Private endpoint** | Functions accessible only from VNet | Premium plan only |

### Monitoring Tab

| Field | What it means | Example value |
|-------|--------------|---------------|
| **Application Insights** | Enable monitoring | `Yes` (always enable) |
| **App Insights resource** | Existing or new | `appi-func-myapp` |

### Tags Tab

Standard: `environment`, `team`, `cost-center`, `project`

---

## 5.2 Function App Configuration

### Application Settings (critical ones)

```
  ┌──────────────────────────────┬──────────────────────────────────────┐
  │ Setting                      │ What it does                         │
  ├──────────────────────────────┼──────────────────────────────────────┤
  │ AzureWebJobsStorage          │ Storage connection for triggers/state│
  │ FUNCTIONS_WORKER_RUNTIME     │ Language runtime (python, node, etc) │
  │ WEBSITE_RUN_FROM_PACKAGE     │ Run from ZIP deployment (=1)         │
  │ FUNCTIONS_EXTENSION_VERSION  │ Runtime version (~4)                 │
  │ APPINSIGHTS_INSTRUMENTATIONKEY│ App Insights key                    │
  │ WEBSITE_CONTENTAZUREFILECONN │ File share for Consumption plan      │
  └──────────────────────────────┴──────────────────────────────────────┘
```

### Triggers & Bindings (how Functions are invoked)

```
  TRIGGER = what starts the function (exactly ONE per function)
  BINDING = input/output data connections (zero or many)

  ┌─────────────────┬────────────────────────────────────────────┐
  │ Trigger          │ When it fires                              │
  ├─────────────────┼────────────────────────────────────────────┤
  │ HTTP             │ REST API call (GET/POST/PUT/DELETE)        │
  │ Timer            │ Cron schedule ("0 */5 * * * *" = every 5m) │
  │ Blob Storage     │ New blob uploaded to container              │
  │ Queue Storage    │ New message in queue                        │
  │ Service Bus      │ New message in queue/topic                  │
  │ Event Grid       │ Azure event (blob created, resource change) │
  │ Event Hub        │ Streaming event                             │
  │ Cosmos DB        │ Document created/updated (change feed)      │
  └─────────────────┴────────────────────────────────────────────┘
```

### Example: HTTP Trigger (Python)

```python
# function_app.py
import azure.functions as func
import json

app = func.FunctionApp()

@app.route(route="users/{id}", methods=["GET"], auth_level=func.AuthLevel.FUNCTION)
def get_user(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.route_params.get('id')
    # fetch user from DB...
    return func.HttpResponse(
        json.dumps({"id": user_id, "name": "John"}),
        mimetype="application/json", status_code=200
    )

@app.route(route="users", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    # save to DB...
    return func.HttpResponse(status_code=201)
```

### Example: Blob Trigger (Python)

```python
@app.blob_trigger(arg_name="blob", path="raw-images/{name}",
                   connection="AzureWebJobsStorage")
def process_image(blob: func.InputStream):
    logging.info(f"Processing blob: {blob.name}, Size: {blob.length} bytes")
    # Resize, convert, save to "processed" container...
```

### Example: Timer Trigger

```python
@app.timer_trigger(schedule="0 0 2 * * *",  # Daily at 2 AM UTC
                    arg_name="timer", run_on_startup=False)
def daily_cleanup(timer: func.TimerRequest):
    logging.info("Running daily cleanup task...")
    # Delete old records, send reports, etc.
```

---

## 5.3 Function App — Operations

```bash
# Create a Function App (Consumption plan, Python)
az functionapp create --resource-group rg-myapp \
    --name func-myapp-prod --consumption-plan-location eastus \
    --runtime python --runtime-version 3.11 \
    --storage-account stfuncmyapp --os-type Linux \
    --functions-version 4

# Deploy code (ZIP deployment)
func azure functionapp publish func-myapp-prod

# List functions in the app
az functionapp function list --resource-group rg-myapp \
    --name func-myapp-prod -o table

# Get function URL (with key)
az functionapp function show --resource-group rg-myapp \
    --name func-myapp-prod --function-name get_user \
    --query invokeUrlTemplate -o tsv

# View logs (live stream)
func azure functionapp logstream func-myapp-prod

# Scale settings (Premium plan only)
az functionapp plan update --resource-group rg-myapp \
    --name asp-func-premium --max-burst 20 --min-instances 1

# Stop/Start
az functionapp stop --resource-group rg-myapp --name func-myapp-prod
az functionapp start --resource-group rg-myapp --name func-myapp-prod
```

---

## 5.4 Function App — Scenarios

### Scenario 1: Event-driven image processing pipeline

```
  ┌───────────────────────────────────────────────────────────┐
  │                                                           │
  │  User uploads image                                       │
  │       │                                                   │
  │       ▼                                                   │
  │  Blob Storage ("raw-images" container)                    │
  │       │                                                   │
  │       │ Blob trigger fires                                │
  │       ▼                                                   │
  │  Azure Function (process_image)                           │
  │       │                                                   │
  │       ├── 1. Validate file type (jpg/png only)            │
  │       ├── 2. Resize to thumbnail (200x200)                │
  │       ├── 3. Save to "thumbnails" container               │
  │       ├── 4. Save metadata to Cosmos DB                   │
  │       └── 5. Send notification via Service Bus            │
  │                                                           │
  │  Cost: $0.00 for first 1M invocations (free tier)         │
  └───────────────────────────────────────────────────────────┘
```

### Scenario 2: Scheduled data sync

```
  Timer Trigger ("0 0 */6 * * *" = every 6 hours)
       │
       ▼
  Azure Function
       │
       ├── 1. Fetch data from external API
       ├── 2. Transform / clean data
       ├── 3. Upsert into Azure SQL
       └── 4. Log results to App Insights

  No server to manage. Runs every 6 hours. Costs pennies.
```

> ⚠️ **Gotcha:** Consumption plan has a 5-minute default timeout (max 10 min). For long-running tasks, use Premium plan (unlimited) or Durable Functions with orchestration.

---

# Chapter 6 — Azure Container Registry (ACR) Deep Dive

> ACR = your private Docker registry in Azure. Build, store, scan, and distribute container images.

---

## 6.1 Creating an ACR — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Registry name** | Globally unique | `myacr2024` | 5-50 chars, alphanumeric only. Becomes `myacr2024.azurecr.io` |
| **Resource Group** | Container | `rg-myapp-prod` | — |
| **Location** | Datacenter | `East US` | Same region as AKS/App Service for fast pulls |
| **SKU** | Feature tier | See table below | Biggest cost/feature decision |

**SKU comparison:**

```
  ┌──────────┬──────────┬───────────┬────────────────────────────────┐
  │ SKU      │ Storage  │ $/month   │ Features                       │
  ├──────────┼──────────┼───────────┼────────────────────────────────┤
  │ Basic    │ 10 GB    │ ~$5       │ Dev/test only. Low throughput  │
  │ Standard │ 100 GB   │ ~$20      │ Most production workloads     │
  │ Premium  │ 500 GB   │ ~$50      │ Geo-replication, private      │
  │          │          │           │ endpoint, content trust,       │
  │          │          │           │ customer-managed keys          │
  └──────────┴──────────┴───────────┴────────────────────────────────┘

  Dev: Basic.  Small team prod: Standard.  Enterprise: Premium.
```

### Networking Tab (Premium only for PE)

| Field | What it means | Values |
|-------|--------------|--------|
| **Public access** | Registry reachable from internet | `All networks`, `Selected networks`, `Disabled` |
| **Private endpoint** | Pull images via private IP | Premium SKU only |

### Encryption Tab (Premium only)

| Field | What it means | Default |
|-------|--------------|---------|
| **Customer-managed key** | Encrypt images with your Key Vault key | `Disabled` (Microsoft-managed) |

### Tags Tab

Standard: `environment`, `team`, `cost-center`

---

## 6.2 ACR — Operations

### Build, Push & Pull Images

```bash
# Create ACR
az acr create --name myacr2024 --resource-group rg-myapp \
    --sku Standard --admin-enabled false --location eastus

# Login to ACR
az acr login --name myacr2024

# Build image in cloud (ACR Tasks — no local Docker needed!)
az acr build --registry myacr2024 \
    --image myapi:v1.0.0 --file Dockerfile .

# Tag and push a local image
docker tag myapi:latest myacr2024.azurecr.io/myapi:v1.0.0
docker push myacr2024.azurecr.io/myapi:v1.0.0

# Pull an image
docker pull myacr2024.azurecr.io/myapi:v1.0.0

# List repositories
az acr repository list --name myacr2024 -o table

# List tags for a repository
az acr repository show-tags --name myacr2024 --repository myapi \
    -o table --orderby time_desc

# Show image manifest (size, digest, etc.)
az acr repository show-manifests --name myacr2024 --repository myapi \
    -o table
```

### Image Cleanup & Retention

```bash
# Delete a specific tag
az acr repository delete --name myacr2024 --image myapi:v0.1.0 --yes

# Delete untagged manifests (dangling images)
az acr run --cmd "acr purge --filter 'myapi:.*' --untagged --ago 7d" \
    --registry myacr2024 /dev/null

# Keep only last 10 tags, delete rest older than 30 days
az acr run --cmd "acr purge --filter 'myapi:.*' --ago 30d --keep 10" \
    --registry myacr2024 /dev/null

# Schedule automatic cleanup (ACR Task)
az acr task create --name purge-old-images --registry myacr2024 \
    --cmd "acr purge --filter 'myapi:.*' --ago 30d --keep 10" \
    --schedule "0 0 * * *" --context /dev/null
```

### Connecting ACR to Compute Services

```bash
# Attach ACR to AKS (managed identity — recommended)
az aks update --resource-group rg-myapp --name aks-prod \
    --attach-acr myacr2024

# Attach ACR to App Service (managed identity)
az webapp config container set --resource-group rg-myapp \
    --name myapp-prod \
    --container-image-name myacr2024.azurecr.io/myapi:v1.0.0 \
    --container-registry-url https://myacr2024.azurecr.io

# Grant ACI pull access
az role assignment create --assignee $ACI_IDENTITY_ID \
    --role AcrPull --scope $ACR_ID
```

### Geo-Replication (Premium SKU)

```
  ┌──────────────────┐         ┌──────────────────┐
  │  East US          │         │  West Europe      │
  │  myacr2024        │════════►│  myacr2024        │
  │  (primary)        │  sync   │  (replica)        │
  │                  │         │                  │
  │  AKS pulls here  │         │  AKS pulls here  │
  │  (fast, local)   │         │  (fast, local)   │
  └──────────────────┘         └──────────────────┘

  Push once → replicated to all regions automatically.
  Each region's AKS pulls from its local replica (fast).
```

```bash
# Add geo-replication
az acr replication create --registry myacr2024 \
    --location westeurope

# List replications
az acr replication list --registry myacr2024 -o table
```

---

## 6.3 ACR — Scenarios

### Scenario 1: CI/CD pipeline with ACR Tasks

```
  ┌───────────────────────────────────────────────────────────┐
  │                                                           │
  │  Developer pushes code → GitHub                           │
  │       │                                                   │
  │       │ GitHub Actions triggers                           │
  │       ▼                                                   │
  │  az acr build --registry myacr2024 --image myapi:$SHA    │
  │  (builds in Azure — no Docker on CI runner!)              │
  │       │                                                   │
  │       │ Image pushed to ACR automatically                 │
  │       ▼                                                   │
  │  ACR webhook notifies AKS                                 │
  │       │                                                   │
  │       ▼                                                   │
  │  AKS pulls new image → rolling update (zero downtime)     │
  │                                                           │
  │  Benefits:                                                │
  │  • No Docker-in-Docker on CI runner                       │
  │  • Build happens in Azure (fast, close to ACR)            │
  │  • Image never leaves Azure network                       │
  └───────────────────────────────────────────────────────────┘
```

### Scenario 2: Multi-region deployment with geo-replication

```
  Push image once to East US ACR
       │
       ├── Auto-replicated → West Europe ACR
       └── Auto-replicated → Southeast Asia ACR
            │                    │
            ▼                    ▼
       AKS (Europe)         AKS (Asia)
       pulls locally         pulls locally
       (~2ms pull)            (~2ms pull)
```

> ⚠️ **Gotcha:** Never use `admin-enabled true` in production. Use managed identities (`az aks update --attach-acr`) or service principals. Admin credentials are shared passwords — a security risk.

---

# Chapter 7 — ACI, Container Apps & Container Groups Deep Dive

> Run containers without managing VMs or Kubernetes. From single containers (ACI) to full microservice platforms (Container Apps).

---

## 7.1 Azure Container Instances (ACI) — Every Field Explained

### Basics Tab

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Container name** | Name of this container | `myapi` | Lowercase, hyphens allowed |
| **Region** | Datacenter | `East US` | — |
| **SKU** | Standard or Confidential | `Standard` | Confidential = hardware-encrypted memory (TEE) |
| **Image source** | Where to pull image | `Azure Container Registry`, `Docker Hub`, `Other registry` | — |
| **Image** | Full image path | `myacr2024.azurecr.io/myapi:v1` | Include tag |
| **OS type** | Linux or Windows | `Linux` | Linux is cheaper and starts faster |
| **Size (vCPUs)** | CPU cores | `1` | 1-4 cores per container |
| **Size (Memory GiB)** | RAM | `1.5` | 0.5-16 GB per container |

### Networking Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Networking type** | `Public`, `Private`, `None` | Public = gets public IP. Private = VNet integrated |
| **DNS name label** | Custom DNS | `myapi-demo` | Becomes `myapi-demo.eastus.azurecontainer.io` |
| **Ports** | Exposed ports | `80`, `443`, `8080` | TCP or UDP |

**VNet deployment:**

```
  Public ACI:
  Internet ──► myapi-demo.eastus.azurecontainer.io:80 ──► Container

  Private ACI (VNet):
  ┌──────────────────────────────────────────────────┐
  │  VNet (10.0.0.0/16)                              │
  │                                                    │
  │  snet-aci (10.0.3.0/24) — delegated to ACI       │
  │  └── Container Instance (10.0.3.4:80)            │
  │                                                    │
  │  Other subnets can reach 10.0.3.4 directly       │
  │  Internet CANNOT reach the container              │
  └──────────────────────────────────────────────────┘
```

### Advanced Tab

| Field | What it means | Values |
|-------|--------------|--------|
| **Restart policy** | What happens when container exits | `Always` (keep running), `OnFailure` (restart on crash), `Never` (run once and stop) |
| **Environment variables** | Env vars injected into container | `DB_HOST=sql.database.windows.net` |
| **Secure env variables** | Same but hidden (for secrets) | `DB_PASS=P@ssw0rd` (not visible in portal after set) |
| **Command override** | Override container ENTRYPOINT | `["python", "app.py", "--port", "8080"]` |

### Volume Mounts

| Volume type | What it does | Use case |
|-------------|-------------|----------|
| **Azure File Share** | Mount SMB share into container | Persistent storage (logs, uploads) |
| **emptyDir** | Temp shared storage between containers in same group | Sidecar pattern (shared cache) |
| **Secret** | Mount secrets as files | Certificates, config files |
| **gitRepo** | Clone a Git repo into container | Pull config/code at startup |

```bash
# Create ACI with public IP
az container create --resource-group rg-myapp \
    --name myapi --image myacr2024.azurecr.io/myapi:v1 \
    --cpu 1 --memory 1.5 --ports 80 \
    --dns-name-label myapi-demo \
    --registry-login-server myacr2024.azurecr.io \
    --registry-username $ACR_USER --registry-password $ACR_PASS \
    --restart-policy Always \
    --environment-variables APP_ENV=production \
    --secure-environment-variables DB_PASS=P@ssw0rd

# Create ACI in VNet (private)
az container create --resource-group rg-myapp \
    --name myapi-private --image myacr2024.azurecr.io/myapi:v1 \
    --cpu 1 --memory 1.5 --ports 80 \
    --vnet vnet-prod --subnet snet-aci \
    --restart-policy Always

# View container logs
az container logs --resource-group rg-myapp --name myapi

# Exec into container (interactive shell)
az container exec --resource-group rg-myapp --name myapi \
    --exec-command "/bin/bash"

# Show container status
az container show --resource-group rg-myapp --name myapi -o table

# Delete container
az container delete --resource-group rg-myapp --name myapi --yes
```

> ⚠️ **Gotcha:** ACI has no built-in auto-scaling, load balancing, or health checks. For those features, use Container Apps or AKS. ACI is for simple, single-purpose containers.

---

## 7.2 Container Groups (Multi-Container ACI)

**What is it?** A container group runs multiple containers on the **same host** — they share network (localhost), storage volumes, and lifecycle. Like a Kubernetes Pod but simpler.

### Why use container groups?

```
  ┌───────────────────────────────────────────────────────┐
  │  Container Group (shared network + storage)           │
  │                                                       │
  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
  │  │ Main App    │  │ Log Shipper  │  │ Auth Proxy  │ │
  │  │ (port 8080) │  │ (fluentd)    │  │ (port 80)   │ │
  │  │             │  │ reads app    │  │ forwards to │ │
  │  │             │  │ logs from    │  │ port 8080   │ │
  │  │             │  │ shared vol   │  │             │ │
  │  └─────────────┘  └──────────────┘  └─────────────┘ │
  │                                                       │
  │  All containers share:                                │
  │  • localhost network (app:8080, proxy:80)             │
  │  • Azure File Share volume (/var/log/app)            │
  │  • Lifecycle (start/stop together)                    │
  │  • Public IP (one IP for the group)                  │
  └───────────────────────────────────────────────────────┘
```

### YAML definition (recommended for multi-container)

```yaml
# deploy-group.yaml
apiVersion: 2021-10-01
type: Microsoft.ContainerInstance/containerGroups
name: myapp-group
location: eastus
properties:
  containers:
    - name: web-app
      properties:
        image: myacr2024.azurecr.io/myapi:v1
        ports:
          - port: 8080
        resources:
          requests:
            cpu: 1.0
            memoryInGB: 1.5
        environmentVariables:
          - name: APP_ENV
            value: production
          - name: DB_PASS
            secureValue: "P@ssw0rd123"
        volumeMounts:
          - name: app-logs
            mountPath: /var/log/app

    - name: log-shipper
      properties:
        image: fluent/fluentd:latest
        resources:
          requests:
            cpu: 0.5
            memoryInGB: 0.5
        volumeMounts:
          - name: app-logs
            mountPath: /var/log/app
            readOnly: true

  osType: Linux
  restartPolicy: Always

  ipAddress:
    type: Public
    dnsNameLabel: myapp-group-demo
    ports:
      - port: 8080
        protocol: TCP

  volumes:
    - name: app-logs
      azureFile:
        shareName: applogs
        storageAccountName: stmyappprod
        storageAccountKey: "<key>"

  imageRegistryCredentials:
    - server: myacr2024.azurecr.io
      username: "<sp-client-id>"
      password: "<sp-client-secret>"
```

```bash
# Deploy container group from YAML
az container create --resource-group rg-myapp \
    --file deploy-group.yaml

# Check group status
az container show --resource-group rg-myapp --name myapp-group -o table

# View logs for a specific container in the group
az container logs --resource-group rg-myapp --name myapp-group \
    --container-name web-app

az container logs --resource-group rg-myapp --name myapp-group \
    --container-name log-shipper
```

---

## 7.3 Azure Container Apps — Every Field Explained

**What is it?** A serverless container platform built on Kubernetes (but you never manage K8s). Supports auto-scaling (including scale-to-zero), Dapr, service discovery, and traffic splitting. Think of it as "AKS without the complexity."

### Creating a Container Apps Environment

The **Environment** is the shared boundary — all Container Apps in the same environment share the same VNet and Log Analytics workspace.

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **Environment name** | Name of the shared environment | `cae-myapp-prod` | Convention: `cae-<project>-<env>` |
| **Region** | Datacenter | `East US` | — |
| **Environment type** | `Workload profiles` or `Consumption only` | `Consumption only` | Consumption = serverless. Profiles = dedicated VMs |
| **Zone redundancy** | Spread across AZs | `Enabled` | For production HA |
| **VNet** | Network boundary | Select existing VNet | Requires dedicated subnet (/23 minimum) |
| **Log Analytics** | Where logs go | `law-myapp-prod` | Required for diagnostics |

```bash
# Create Container Apps Environment
az containerapp env create \
    --name cae-myapp-prod --resource-group rg-myapp \
    --location eastus \
    --logs-workspace-id $LAW_CUSTOMER_ID \
    --logs-workspace-key $LAW_KEY
```

### Creating a Container App

| Field | What it means | Example value | Notes |
|-------|--------------|---------------|-------|
| **App name** | Name of this app | `ca-myapi` | Convention: `ca-<service>` |
| **Environment** | Which CAE to deploy in | `cae-myapp-prod` | — |
| **Image** | Container image | `myacr2024.azurecr.io/myapi:v1` | — |
| **CPU / Memory** | Resources per replica | `0.5 / 1.0Gi` | Min: 0.25 CPU, 0.5 Gi |
| **Min replicas** | Minimum instances | `0` (scale to zero!) or `1` | 0 = serverless |
| **Max replicas** | Maximum instances | `10` | Auto-scale up to this |

### Ingress Configuration

| Field | What it means | Values |
|-------|--------------|--------|
| **Ingress** | Enable HTTP access | `Enabled` / `Disabled` |
| **Traffic** | Who can access | `Accept from anywhere` or `Limited to environment` |
| **Target port** | Port your container listens on | `8080` |
| **Transport** | Protocol | `HTTP`, `HTTP2`, `TCP` |

### Scaling Rules

```
  ┌───────────────────┬──────────────────────────────────────┐
  │ Scale trigger      │ What it does                         │
  ├───────────────────┼──────────────────────────────────────┤
  │ HTTP               │ Scale by concurrent requests          │
  │ Azure Queue        │ Scale by queue length                 │
  │ Service Bus        │ Scale by message count                │
  │ Custom             │ Scale by custom metric (KEDA)         │
  │ TCP                │ Scale by TCP connections               │
  └───────────────────┴──────────────────────────────────────┘
```

```bash
# Create Container App
az containerapp create \
    --name ca-myapi --resource-group rg-myapp \
    --environment cae-myapp-prod \
    --image myacr2024.azurecr.io/myapi:v1 \
    --target-port 8080 --ingress external \
    --cpu 0.5 --memory 1.0Gi \
    --min-replicas 1 --max-replicas 10 \
    --registry-server myacr2024.azurecr.io \
    --registry-identity system \
    --env-vars APP_ENV=production

# Create revision (new version)
az containerapp update --name ca-myapi --resource-group rg-myapp \
    --image myacr2024.azurecr.io/myapi:v2

# Traffic splitting (canary deployment)
az containerapp ingress traffic set --name ca-myapi \
    --resource-group rg-myapp \
    --revision-weight ca-myapi--v1=80 ca-myapi--v2=20

# Scale rule (HTTP-based)
az containerapp update --name ca-myapi --resource-group rg-myapp \
    --scale-rule-name http-scale \
    --scale-rule-type http \
    --scale-rule-http-concurrency 50

# View app URL
az containerapp show --name ca-myapi --resource-group rg-myapp \
    --query properties.configuration.ingress.fqdn -o tsv
```

---

## 7.4 Container Service Decision Guide

```
  ┌──────────────────┬────────────┬───────────────┬──────────────┐
  │                  │ ACI        │ Container Apps│ AKS          │
  ├──────────────────┼────────────┼───────────────┼──────────────┤
  │ Complexity       │ Simplest   │ Medium        │ Most complex │
  │ Scale to zero    │ N/A (pay   │ Yes           │ Yes (KEDA)   │
  │                  │ while run) │               │              │
  │ Auto-scale       │ No         │ Yes (built-in)│ Yes (HPA)    │
  │ Load balancer    │ No         │ Yes (built-in)│ Yes (config) │
  │ Service mesh     │ No         │ Dapr built-in │ Yes (Istio)  │
  │ Multi-container  │ Groups     │ Sidecars      │ Pods         │
  │ VNet support     │ Yes        │ Yes           │ Yes          │
  │ CI/CD revisions  │ No         │ Yes (traffic) │ Yes (manual) │
  │ K8s knowledge    │ None       │ None          │ Required     │
  │ Best for         │ Quick jobs │ Microservices │ Full control │
  │                  │ batch tasks│ APIs, workers │ enterprise   │
  │ Cost model       │ Per-second │ Per-second    │ Per-node     │
  └──────────────────┴────────────┴───────────────┴──────────────┘
```

---

## 7.5 Container Services — Scenarios

### Scenario 1: Microservices with Container Apps

```
  ┌───────────────────────────────────────────────────────────┐
  │  Container Apps Environment (cae-myapp-prod)              │
  │  VNet: 10.0.0.0/16, Subnet: 10.0.8.0/23                 │
  │                                                           │
  │  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐│
  │  │ ca-frontend│  │ ca-api     │  │ ca-worker           ││
  │  │ React SPA  │  │ REST API   │  │ Background processor││
  │  │ ingress:   │  │ ingress:   │  │ ingress: disabled    ││
  │  │ external   │  │ internal   │  │ scales by queue msgs ││
  │  │ port: 3000 │  │ port: 8080 │  │                     ││
  │  │ 1-5 replicas│  │ 2-10 repls │  │ 0-20 replicas       ││
  │  └─────┬──────┘  └─────┬──────┘  └──────┬──────────────┘│
  │        │               │                 │               │
  │        └──► calls ─────┘     Service Bus ┘               │
  │            internal URL       queue trigger               │
  │            ca-api.internal                                │
  │                                                           │
  │  Shared: Log Analytics, Managed Identity, Dapr            │
  └───────────────────────────────────────────────────────────┘
```

### Scenario 2: Batch job with ACI (run once and stop)

```
  ┌───────────────────────────────────────────────┐
  │  Nightly data processing                      │
  │                                                │
  │  Timer (Logic App) ──► Creates ACI             │
  │       at 2 AM           │                      │
  │                         ▼                      │
  │                    ACI container               │
  │                    --restart-policy Never       │
  │                         │                      │
  │                    1. Pull data from API        │
  │                    2. Process & transform       │
  │                    3. Load into Azure SQL       │
  │                    4. Container exits (code 0)  │
  │                         │                      │
  │                    ACI auto-deleted (no cost)   │
  │                                                │
  │  Cost: ~$0.03 for 10 min of processing         │
  └───────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Container Apps require a /23 subnet minimum (510 IPs). Plan your VNet CIDR carefully — this is a large allocation.

---

# Chapter 8 — HA, DR & Reliability on Azure

> **HA** = stays running when things break. **DR** = recovers when everything fails. **Reliability** = consistently meets SLA promises.

---

## 8.1 Key Concepts

```
  ┌──────────────────┬─────────────────────────────────────────────┐
  │ Term             │ Plain English                               │
  ├──────────────────┼─────────────────────────────────────────────┤
  │ Availability     │ % of time the service is UP and responding  │
  │ SLA              │ Microsoft's promise: "99.9% uptime"         │
  │ RPO              │ Recovery Point Objective — how much data    │
  │                  │ you can afford to LOSE (e.g., 15 min)       │
  │ RTO              │ Recovery Time Objective — how long you can  │
  │                  │ be DOWN (e.g., 1 hour)                      │
  │ Fault Domain     │ Physical rack sharing power/network. VMs on │
  │                  │ different FDs survive rack failure           │
  │ Update Domain    │ Logical group for maintenance. Azure updates │
  │                  │ one UD at a time (rolling patches)           │
  │ Availability Set │ Spread VMs across FDs + UDs in ONE datacenter│
  │ Availability Zone│ Physically separate datacenter IN SAME region│
  │                  │ (own power, cooling, network)                │
  │ Region Pair      │ Two regions 300+ miles apart for DR          │
  │                  │ (East US ↔ West US)                         │
  └──────────────────┴─────────────────────────────────────────────┘
```

---

## 8.2 Availability Levels

```
  LEVEL 1: Single VM (no redundancy)
  ────────────────────────────────────
  SLA: 99.9% (with Premium SSD)
  Downtime: ~8.76 hours/year
  Survives: Nothing — single point of failure

  LEVEL 2: Availability Set (same datacenter)
  ────────────────────────────────────────────
  SLA: 99.95%
  Downtime: ~4.38 hours/year
  Survives: Rack failure, planned maintenance
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ FD 0     │ │ FD 1     │ │ FD 2     │
  │ VM-1     │ │ VM-2     │ │ VM-3     │
  │ (Rack A) │ │ (Rack B) │ │ (Rack C) │
  └──────────┘ └──────────┘ └──────────┘

  LEVEL 3: Availability Zones (cross-datacenter)
  ───────────────────────────────────────────────
  SLA: 99.99%
  Downtime: ~52 minutes/year
  Survives: Entire datacenter failure
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ Zone 1   │ │ Zone 2   │ │ Zone 3   │
  │ DC-East  │ │ DC-North │ │ DC-South │
  │ VM-1     │ │ VM-2     │ │ VM-3     │
  └──────────┘ └──────────┘ └──────────┘

  LEVEL 4: Multi-Region (cross-region)
  ─────────────────────────────────────
  SLA: 99.99%+ (composite)
  Downtime: ~minutes/year
  Survives: Entire region failure (natural disaster)
  ┌──────────────┐         ┌──────────────┐
  │ East US      │         │ West US      │
  │ (primary)    │════════►│ (secondary)  │
  │ Active       │         │ Standby/Active│
  └──────────────┘         └──────────────┘
```

---

## 8.3 HA per Service — How Each Service Achieves High Availability

| Service | HA mechanism | SLA |
|---------|-------------|-----|
| **App Service** | Zone-redundant plan (P1v3+), multiple instances | 99.95% |
| **Azure SQL** | Zone-redundant Business Critical, Failover Groups | 99.995% |
| **Cosmos DB** | Multi-region writes, automatic failover | 99.999% |
| **Storage Account** | ZRS (3 zones), GRS (2 regions) | 99.99% (RA-GRS) |
| **Key Vault** | Auto-replicated within region, paired region backup | 99.99% |
| **Azure Functions** | Zone-redundant Premium plan | 99.95% |
| **AKS** | Zone-redundant node pools, pod anti-affinity | 99.95% |
| **Container Apps** | Zone-redundant environment | 99.95% |
| **Load Balancer** | Zone-redundant (Standard SKU) | 99.99% |
| **PostgreSQL Flex** | Zone-redundant HA (sync standby) | 99.99% |

---

## 8.4 Disaster Recovery Patterns

### Active-Passive (Hot Standby)

```
  Normal operation:
  ┌──────────────┐         ┌──────────────┐
  │ East US      │         │ West US      │
  │ ACTIVE       │════════►│ PASSIVE      │
  │ 100% traffic │  sync   │ 0% traffic   │
  │ App + DB     │         │ App (scaled  │
  │ (full scale) │         │ down) + DB   │
  └──────────────┘         │ (read-only)  │
                           └──────────────┘

  During disaster (East US down):
  ┌──────────────┐         ┌──────────────┐
  │ East US      │         │ West US      │
  │ DOWN ✗       │         │ ACTIVE       │
  │              │         │ 100% traffic │
  │              │         │ (scaled up)  │
  └──────────────┘         └──────────────┘

  RTO: 5-30 minutes (scale up standby + DNS switch)
  RPO: ~0 (sync replication) or ~seconds (async)
  Cost: ~60-70% of active-active (standby runs smaller)
```

### Active-Active (Both Live)

```
  Normal operation:
  ┌──────────────────────────────────────────────┐
  │  Azure Front Door (global load balancer)     │
  │       │                                       │
  │       ├── East US (50% traffic)               │
  │       │   App + DB (read-write)              │
  │       │                                       │
  │       └── West US (50% traffic)               │
  │           App + DB (read-write)              │
  └──────────────────────────────────────────────┘

  During disaster:
  Front Door detects East US unhealthy → routes 100% to West US.
  No manual intervention. Automatic failover.

  RTO: ~seconds (automatic)
  RPO: ~0 (multi-region write with Cosmos DB)
  Cost: 2× (both regions fully active)
```

### Backup & Restore (Cold DR)

```
  Normal: Backups taken daily → stored in paired region (GRS)
  Disaster: Restore from backup in paired region

  RTO: Hours (restore takes time)
  RPO: Hours (since last backup)
  Cost: Cheapest ($$ for storage only)
  Best for: Non-critical workloads, dev/test environments
```

---

## 8.5 SLA Calculation (Composite SLA)

```
  Your app uses:
  - App Service:     99.95%
  - Azure SQL:       99.99%
  - Key Vault:       99.99%
  - Storage Account: 99.9%

  Composite SLA (serial dependency = multiply):
  99.95% × 99.99% × 99.99% × 99.9% = 99.83%

  ≈ 14.9 hours of downtime per year

  To improve:
  1. Add redundancy (zones, regions)
  2. Remove single points of failure
  3. Add caching (reduce dependency on DB)
  4. Use async patterns (queues instead of direct calls)
```

> ⚠️ **Gotcha:** Microsoft SLAs only apply when you meet their configuration requirements. A single VM with Standard HDD has NO SLA. Add Premium SSD or use Availability Zones.

---

# Chapter 9 — User Defined Routes & Other Important Topics

---

## 9.1 User Defined Routes (UDRs)

**What are they?** Azure automatically routes traffic between subnets, VNets, and the internet using system routes. UDRs let you **override** these defaults — force traffic through a firewall, NVA, or VPN.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Route Table** | A collection of UDRs, attached to a subnet |
| **Next hop** | Where to send matching traffic (NVA IP, Firewall, VNet Gateway, Internet, None) |
| **NVA** | Network Virtual Appliance — a VM running firewall/routing software |
| **0.0.0.0/0** | Default route — matches ALL internet-bound traffic |

### Default (System) Routes vs UDRs

```
  SYSTEM ROUTES (automatic):
  ────────────────────────
  Subnet A → Subnet B (same VNet):    direct, via VNet
  Subnet A → Internet:                 via Azure internet gateway
  Subnet A → Peered VNet:              via VNet peering

  USER DEFINED ROUTES (override):
  ────────────────────────────────
  Subnet A → Internet:  force through Azure Firewall (10.0.4.4)
  Subnet A → 10.1.0.0/16:  force through VPN Gateway
  Subnet A → 0.0.0.0/0:  drop all internet traffic (next hop = None)
```

### Example: Force all traffic through Azure Firewall

```
  ┌────────────────────────────────────────────────────────┐
  │  VNet (10.0.0.0/16)                                   │
  │                                                        │
  │  snet-web (10.0.1.0/24)                               │
  │  ├── Route Table: rt-force-firewall                    │
  │  │   └── 0.0.0.0/0 → next hop: 10.0.4.4 (Firewall)  │
  │  └── VM-web (wants to reach internet)                  │
  │       │                                                │
  │       │ Traffic forced to Firewall (not direct internet)│
  │       ▼                                                │
  │  snet-fw (10.0.4.0/24)                                │
  │  └── Azure Firewall (10.0.4.4)                        │
  │       │                                                │
  │       │ Inspects, logs, allows/denies                   │
  │       ▼                                                │
  │  Internet (if allowed by firewall rules)               │
  └────────────────────────────────────────────────────────┘
```

```bash
# Create a route table
az network route-table create --resource-group rg-myapp \
    --name rt-force-firewall --location eastus \
    --disable-bgp-route-propagation true

# Add route: all internet traffic → Firewall
az network route-table route create \
    --resource-group rg-myapp --route-table-name rt-force-firewall \
    --name route-to-firewall \
    --address-prefix 0.0.0.0/0 \
    --next-hop-type VirtualAppliance \
    --next-hop-ip-address 10.0.4.4

# Associate route table with a subnet
az network vnet subnet update --resource-group rg-myapp \
    --vnet-name vnet-prod --name snet-web \
    --route-table rt-force-firewall

# List routes in a table
az network route-table route list --resource-group rg-myapp \
    --route-table-name rt-force-firewall -o table
```

### Next Hop Types Explained

```
  ┌──────────────────────┬──────────────────────────────────────┐
  │ Next Hop Type        │ Traffic goes to...                   │
  ├──────────────────────┼──────────────────────────────────────┤
  │ VirtualAppliance     │ Specific IP (firewall, NVA)          │
  │ VirtualNetworkGateway│ VPN or ExpressRoute gateway          │
  │ VnetLocal            │ Within the VNet (default behavior)   │
  │ Internet             │ Azure's internet gateway             │
  │ None                 │ DROP the packet (black hole)          │
  └──────────────────────┴──────────────────────────────────────┘
```

### Common UDR Patterns

```
  1. FORCE TO FIREWALL: 0.0.0.0/0 → Azure Firewall IP
     (inspect all outbound traffic)

  2. BLOCK INTERNET: 0.0.0.0/0 → None
     (database subnet should never reach internet)

  3. ROUTE TO ON-PREM: 10.0.0.0/8 → VPN Gateway
     (traffic to on-prem network via VPN)

  4. ROUTE BETWEEN SPOKES: 10.1.0.0/16 → Hub Firewall
     (spoke-to-spoke via hub firewall for inspection)
```

> ⚠️ **Gotcha:** When you attach a UDR with `0.0.0.0/0 → Firewall`, Azure services that need outbound access (like App Service VNet integration) may break. Add specific routes for Azure service IPs or use service tags.

---

## 9.2 Azure Service Tags & ASGs

### Service Tags

Pre-defined IP ranges for Azure services — use in NSGs and UDRs instead of hardcoding IPs.

```
  ┌──────────────────────┬──────────────────────────────────────┐
  │ Service Tag          │ What it covers                       │
  ├──────────────────────┼──────────────────────────────────────┤
  │ Internet             │ All public internet IPs              │
  │ AzureCloud           │ All Azure datacenter IPs             │
  │ AzureCloud.EastUS    │ Azure IPs in East US only            │
  │ Sql                  │ Azure SQL Database endpoints         │
  │ Storage              │ Azure Storage endpoints              │
  │ AzureKeyVault        │ Key Vault endpoints                  │
  │ AzureContainerRegistry│ ACR endpoints                      │
  │ AzureActiveDirectory │ Entra ID endpoints                   │
  │ GatewayManager       │ Azure Gateway Manager (for VPN/ER)   │
  └──────────────────────┴──────────────────────────────────────┘

  Example NSG rule: Allow outbound to Azure SQL
  Source: VNet  Destination: Sql  Port: 1433  Action: Allow
  (No need to know SQL server's IP — Service Tag handles it!)
```

### Application Security Groups (ASGs)

```
  Group VMs by function, not by IP/subnet.

  ┌─────────────────────────────────────────────────────┐
  │  ASG: asg-web-servers                               │
  │  Members: VM-web-1, VM-web-2, VM-web-3             │
  │                                                     │
  │  ASG: asg-db-servers                                │
  │  Members: VM-db-1, VM-db-2                          │
  │                                                     │
  │  NSG Rule:                                          │
  │  Source: asg-web-servers                            │
  │  Destination: asg-db-servers                        │
  │  Port: 5432  Action: Allow                          │
  │                                                     │
  │  = Web servers can reach DB servers on port 5432    │
  │  = No hardcoded IPs, works across subnets           │
  └─────────────────────────────────────────────────────┘
```

---

## 9.3 Azure DNS & Private DNS Zones

### Azure DNS (Public)

```bash
# Create DNS zone
az network dns zone create --resource-group rg-myapp \
    --name myapp.com

# Add A record
az network dns record-set a add-record --resource-group rg-myapp \
    --zone-name myapp.com --record-set-name www \
    --ipv4-address 20.30.40.50

# Add CNAME record
az network dns record-set cname set-record --resource-group rg-myapp \
    --zone-name myapp.com --record-set-name api \
    --cname myapp-api.azurewebsites.net
```

### Private DNS Zones (for Private Endpoints)

```
  When you create a Private Endpoint for Azure SQL:
  sql-myapp-prod.database.windows.net normally resolves to → public IP

  With Private DNS Zone (privatelink.database.windows.net):
  sql-myapp-prod.database.windows.net resolves to → 10.0.5.5 (private IP)

  Traffic stays in VNet, never goes to internet!
```

```bash
# Create private DNS zone
az network private-dns zone create --resource-group rg-myapp \
    --name privatelink.database.windows.net

# Link to VNet
az network private-dns zone-group create --resource-group rg-myapp \
    --endpoint-name pe-sql-myapp --name default \
    --private-dns-zone privatelink.database.windows.net \
    --zone-name privatelink.database.windows.net
```

---

## 9.4 Azure Resource Naming Conventions

```
  ┌────────────────┬───────────────────────────────────────┐
  │ Resource Type  │ Naming Convention                     │
  ├────────────────┼───────────────────────────────────────┤
  │ Resource Group │ rg-<project>-<env>                    │
  │ VNet           │ vnet-<project>-<env>                  │
  │ Subnet         │ snet-<purpose>                        │
  │ NSG            │ nsg-<subnet-or-purpose>               │
  │ VM             │ vm-<role>-<number>                    │
  │ App Service    │ app-<project>-<env>                   │
  │ App Svc Plan   │ asp-<project>-<env>                   │
  │ Function App   │ func-<project>-<env>                  │
  │ Storage Acct   │ st<project><env> (no dashes!)         │
  │ Key Vault      │ kv-<project>-<env>                    │
  │ SQL Server     │ sql-<project>-<env>                   │
  │ SQL Database   │ db-<name>                             │
  │ Cosmos DB      │ cosmos-<project>-<env>                │
  │ Container Reg  │ cr<project><env> (no dashes!)         │
  │ Container App  │ ca-<service>                          │
  │ AKS Cluster    │ aks-<project>-<env>                   │
  │ Log Analytics  │ law-<project>-<env>                   │
  │ App Insights   │ appi-<project>-<env>                  │
  │ Load Balancer  │ lb-<purpose>-<env>                    │
  │ Public IP      │ pip-<resource>-<env>                  │
  │ Route Table    │ rt-<purpose>                          │
  │ Private Endpt  │ pe-<target-resource>                  │
  └────────────────┴───────────────────────────────────────┘

  Rules: lowercase, hyphens (except storage/ACR), max length varies.
```

---

## 9.5 Azure Well-Architected Framework (WAF)

```
  The 5 pillars of a well-architected Azure solution:

  ┌─────────────────────────────────────────────────────────┐
  │  1. RELIABILITY                                        │
  │     Design for failure. Use zones, regions, health     │
  │     probes, auto-failover.                             │
  │                                                        │
  │  2. SECURITY                                           │
  │     Zero-trust. Managed identities, Key Vault,         │
  │     private endpoints, NSGs, encryption everywhere.    │
  │                                                        │
  │  3. COST OPTIMIZATION                                  │
  │     Right-size resources, reserved instances,           │
  │     auto-scale, lifecycle policies, spot VMs.           │
  │                                                        │
  │  4. OPERATIONAL EXCELLENCE                             │
  │     IaC (Bicep/Terraform), CI/CD, monitoring,          │
  │     alerts, runbooks, documentation.                   │
  │                                                        │
  │  5. PERFORMANCE EFFICIENCY                             │
  │     Caching (Redis), CDN, async patterns (queues),     │
  │     auto-scale, right compute choice.                  │
  └─────────────────────────────────────────────────────────┘
```

---

# Chapter 10 — Interview Questions — All Services

---

## 10.1 App Service Interview Questions

**Q1: What is the difference between Scale Up and Scale Out in App Service?**

> **Scale Up** (vertical) = Change to a bigger VM (more CPU/RAM). E.g., B1 → P1v3. Requires brief restart.
> **Scale Out** (horizontal) = Add more instances of the same VM size. E.g., 2 → 5 instances. No downtime. Load balancer distributes traffic. Always prefer Scale Out for HA.

**Q2: How do deployment slots enable zero-downtime deployments?**

> Deploy new code to a staging slot → test it → swap staging ↔ production. The swap is instant (DNS pointer change, not code copy). If the new version fails, swap back (instant rollback). Settings marked as "slot sticky" stay with the slot and don't swap.

**Q3: An App Service returns 503 errors under heavy load. How do you troubleshoot?**

> 1. Check App Insights for request rates and response times.
> 2. Check if the App Service Plan is at CPU/memory limits → Scale Up or Scale Out.
> 3. Check "Always On" is enabled (cold starts on free/basic tiers).
> 4. Check if the app has connection pool exhaustion (DB/Redis connections not disposed).
> 5. Check if auto-scale rules are configured and triggering properly.
> 6. Review "Diagnose and solve problems" blade in the portal.

**Q4: What is the difference between VNet Integration and Private Endpoints?**

> **VNet Integration** = outbound. Your app can reach resources inside a VNet (e.g., SQL via Private Endpoint, VMs). The app itself is still publicly accessible.
> **Private Endpoint** = inbound. The app gets a private IP in your VNet. The internet can't reach it. Used for internal APIs. You can use both together.

**Q5: You have 3 App Services running on the same App Service Plan. What happens if one app gets a traffic spike?**

> All 3 apps share the same underlying VM(s). A spike in one app can starve the others (noisy neighbor). Solutions: move the busy app to its own plan, enable auto-scale, or use per-app scaling (Premium).

---

## 10.2 Key Vault Interview Questions

**Q6: Access Policies vs RBAC — which should you use and why?**

> RBAC (recommended). It's consistent with all other Azure resources, supports Conditional Access, and is auditable via the IAM blade. Access Policies are legacy — they're per-vault and not visible in IAM, making them hard to audit across many vaults.

**Q7: What is the difference between Soft Delete and Purge Protection?**

> **Soft Delete** = When you delete a secret/key/cert, it's recoverable for 7-90 days (configurable). Enabled by default, cannot be disabled once turned on.
> **Purge Protection** = Even an admin with full access cannot permanently delete during the retention period. Must be explicitly enabled. Use for production to prevent accidental or malicious permanent deletion.

**Q8: How do you access Key Vault secrets from an App Service without storing any credentials?**

> 1. Enable system-assigned managed identity on the App Service.
> 2. Assign "Key Vault Secrets User" RBAC role to that identity on the vault.
> 3. In App Settings, use `@Microsoft.KeyVault(SecretUri=https://kv-name.vault.azure.net/secrets/secret-name/)`.
> The app gets a token from Entra ID automatically — no passwords stored anywhere.

**Q9: Key Vault has a 1000 ops/10sec rate limit. Your app does 5000 secret reads/second. How do you solve this?**

> Cache secrets in-app memory with a refresh interval (e.g., 5-15 min). Use the Azure SDK's `SecretClient` with caching. For config, use Key Vault references in App Service (auto-cached). Never call Key Vault on every request.

---

## 10.3 Storage Account Interview Questions

**Q10: Explain the storage redundancy options (LRS, ZRS, GRS, RA-GRS, GZRS).**

> - **LRS** (Locally Redundant) = 3 copies in 1 datacenter. Cheapest. Survives: disk failure.
> - **ZRS** (Zone Redundant) = 3 copies across 3 availability zones. Survives: datacenter failure.
> - **GRS** (Geo Redundant) = LRS + async copy to paired region (3+3=6 copies). Survives: region failure, but secondary is read-only after failover.
> - **RA-GRS** (Read-Access GRS) = GRS + read access from secondary region anytime.
> - **GZRS** = ZRS + GRS combined. Best protection: 3 zones locally + 3 in paired region.

**Q11: What is a SAS token and when should you use one?**

> Shared Access Signature — a signed URL that grants time-limited, scoped access to a specific blob/container. Use for: letting users upload files directly to storage without going through your API, or giving partners read-only access to specific containers. Always set short expiry, limit permissions (read-only/write-only), and restrict by IP if possible.

**Q12: How do you optimize storage costs for a compliance system that keeps data for 7 years?**

> Use lifecycle management policies:
> - Days 0-30: Hot tier (frequently accessed).
> - Days 30-90: Cool tier (44% cheaper).
> - Days 90-365: Cold tier (75% cheaper).
> - Days 365+: Archive tier (95% cheaper).
> - Day 2555 (7 years): Delete.
> This can save 70%+ vs keeping everything in Hot.

**Q13: What's the difference between Service Endpoints and Private Endpoints for Storage?**

> **Service Endpoint** = Traffic from your VNet to storage stays on Azure backbone (never goes to public internet). But the storage account still has a public IP. Free.
> **Private Endpoint** = Storage gets a private IP (10.x.x.x) in your VNet. You can disable all public access entirely. More secure but costs ~$7.30/month.

---

## 10.4 Database Interview Questions

**Q14: DTU vs vCore — when do you use each?**

> **DTU** = Bundled unit (CPU+IO+memory combined). Simple pricing, good for small workloads where you don't need fine-grained control. Can't independently scale CPU vs memory.
> **vCore** = Choose CPU cores, memory, and storage independently. Supports reserved instances (up to 55% discount), serverless compute, and Hyperscale (up to 100TB). Use vCore for production — more flexibility and better cost optimization.

**Q15: How do Failover Groups work in Azure SQL?**

> A failover group creates a read-write listener (DNS) that always points to the primary server. When failover happens (automatic or manual), the DNS switches to the secondary. Your app's connection string uses the failover group DNS (e.g., `fog-myapp.database.windows.net`) — it never changes, so the app doesn't need reconfiguration during failover.

**Q16: What is a partition key in Cosmos DB and why is it critical?**

> The partition key determines how data is distributed across physical partitions. A good key has high cardinality (many distinct values) and is used in most queries as a filter. Bad keys (like "status" or "country") create hot partitions where all traffic hits one partition, causing throttling. You CANNOT change the partition key after creation without recreating the container.

**Q17: Your Azure SQL Serverless DB has ~60 second cold starts. Users complain about slow first requests. What do you do?**

> Options:
> 1. Set `--auto-pause-delay -1` to disable auto-pause (always running, costs more).
> 2. Switch to Provisioned compute for predictable performance.
> 3. Add a health check that pings the DB every 30 minutes to prevent auto-pause.
> 4. Use connection retry logic in your app (exponential backoff).

---

## 10.5 Azure Functions Interview Questions

**Q18: Consumption vs Premium vs App Service Plan — how do you choose?**

> - **Consumption**: Event-driven, low-traffic, cost-sensitive. Free tier available. Cold starts 1-3s. 5-minute default timeout.
> - **Premium**: No cold starts (pre-warmed), VNet integration, unlimited timeout. For production with latency requirements.
> - **App Service Plan**: If you already have an App Service Plan with spare capacity. Predictable cost. No scale-to-zero.

**Q19: What are triggers vs bindings?**

> **Trigger** = what starts the function. Every function has exactly ONE trigger (HTTP request, timer, blob upload, queue message, etc.).
> **Binding** = input/output data connections. Zero or many per function. Input binding reads data (e.g., read from Cosmos DB). Output binding writes data (e.g., send to Queue). Bindings eliminate boilerplate code for connecting to Azure services.

**Q20: A Blob-triggered function processes 10,000 images daily. Occasionally images are processed twice. Why and how do you fix it?**

> Blob triggers use a scan-based approach (not event-driven). If the function app restarts or scales, it may re-scan and reprocess. Solutions:
> 1. Switch to **Event Grid trigger** (event-driven, guaranteed once delivery).
> 2. Add idempotency — check if the image was already processed (e.g., flag in DB).
> 3. Use a queue-based pattern: blob upload → Event Grid → Queue → Function.

---

## 10.6 Container Services Interview Questions

**Q21: ACI vs Container Apps vs AKS — when do you use each?**

> - **ACI**: Simple, single-purpose containers. Batch jobs, sidecar groups, quick demos. No orchestration, no auto-scaling, no load balancing.
> - **Container Apps**: Microservices, APIs, background workers. Built-in auto-scaling (including scale-to-zero), traffic splitting, Dapr integration. No Kubernetes knowledge required.
> - **AKS**: Full Kubernetes. When you need custom networking, service mesh (Istio), custom operators, or have a team with K8s expertise. Most complex but most flexible.

**Q22: What is a Container Group in ACI and how is it like a Kubernetes Pod?**

> A container group runs multiple containers on the same host. They share: localhost network (can communicate via 127.0.0.1), storage volumes, lifecycle (start/stop together), and a single public IP. This is the same concept as a K8s Pod. Use cases: sidecar logging (app + fluentd), reverse proxy (app + nginx), init containers.

**Q23: How does traffic splitting work in Container Apps?**

> Container Apps creates a new **revision** for each deployment. You can split traffic by percentage:
> - `revision-v1: 90%` and `revision-v2: 10%` (canary deployment).
> - Test v2 with real traffic. If metrics look good, shift to 100%.
> - If v2 has errors, shift back to v1 (instant rollback).

**Q24: What is the minimum subnet size for Container Apps and why?**

> **/23 minimum** (510 usable IPs). Container Apps runs on managed Kubernetes under the hood. It needs IP space for: node pools, internal load balancers, KEDA scalers, and Envoy proxies. A /23 supports ~100 app replicas. Plan your VNet CIDR carefully — this is a large allocation.

---

## 10.7 ACR Interview Questions

**Q25: How do you secure ACR in production?**

> 1. Disable admin account (`--admin-enabled false`).
> 2. Use managed identities for pulling images (AKS: `az aks update --attach-acr`).
> 3. Enable Private Endpoint (Premium SKU) — disable public access.
> 4. Enable content trust (image signing) for verified images.
> 5. Schedule automated image cleanup (purge untagged/old images).
> 6. Use vulnerability scanning (Microsoft Defender for Containers).

**Q26: What are ACR Tasks and why use them instead of building locally?**

> ACR Tasks build container images in Azure's cloud. Benefits:
> - No Docker daemon needed on your CI runner (no Docker-in-Docker).
> - Build happens close to the registry (fast push, no network transfer).
> - Image never leaves Azure (stays within Microsoft's network).
> - Supports automated builds on Git commit or base image update.

---

## 10.8 HA, DR & Reliability Interview Questions

**Q27: Explain RPO and RTO with an example.**

> **RPO** (Recovery Point Objective) = How much data loss is acceptable.
> Example: RPO = 15 minutes means you can lose up to 15 minutes of data. Requires backups every 15 minutes.
> **RTO** (Recovery Time Objective) = How long the system can be down.
> Example: RTO = 1 hour means the system must be back online within 1 hour of failure. Requires hot standby or fast restore.
> A banking app might need RPO=0 (no data loss) + RTO=5 min. A blog might accept RPO=24h + RTO=4h.

**Q28: What is the difference between Availability Sets and Availability Zones?**

> **Availability Sets** = Spread VMs across fault domains (racks) and update domains within ONE datacenter. SLA: 99.95%. Protects against: rack failure, planned maintenance.
> **Availability Zones** = Spread VMs across physically separate datacenters within one region (each zone has own power/cooling/network). SLA: 99.99%. Protects against: entire datacenter failure.
> Always prefer Availability Zones where supported.

**Q29: How do you calculate composite SLA?**

> Multiply individual SLAs for serial (dependent) components:
> App Service (99.95%) × SQL (99.99%) × Storage (99.9%) = 99.84%
> To improve: add redundancy (parallel paths), use async patterns (queues), add caching to reduce dependencies.

---

## 10.9 UDR & Networking Interview Questions

**Q30: What are User Defined Routes and when do you need them?**

> UDRs override Azure's default system routes. Use when you need to:
> 1. Force all outbound traffic through Azure Firewall for inspection.
> 2. Block internet access from a database subnet (next hop = None).
> 3. Route traffic to on-premises via VPN Gateway.
> 4. Route spoke-to-spoke traffic through a hub firewall.
> Without UDRs, subnets route directly to the internet and each other.

**Q31: What happens if you set 0.0.0.0/0 → Azure Firewall as a UDR on a subnet with App Service VNet integration?**

> All outbound traffic from that subnet goes through the firewall, including Azure service traffic. This can break App Service VNet integration because the app needs direct access to Azure management endpoints. Fix: add specific routes for Azure service tags (e.g., `AzureCloud` → Internet) or use NSGs with service tags instead of UDRs for fine-grained control.

**Q32: Explain the difference between Service Endpoints, Private Endpoints, and Private Link.**

> - **Service Endpoint**: Extends VNet identity to Azure services. Traffic stays on Azure backbone but service keeps its public IP. Free. Simple to configure. Less secure (public IP still exists).
> - **Private Endpoint**: Creates a private NIC with a private IP (10.x.x.x) in your subnet for the Azure service. You can disable all public access. Most secure. Costs ~$7.30/month.
> - **Private Link**: The underlying technology that enables Private Endpoints. Also lets you expose YOUR OWN services privately to other VNets/subscriptions.

---

## 10.10 Scenario-Based Design Questions

**Q33: Design a secure 3-tier web application on Azure.**

> ```
>   Internet → Azure Front Door (WAF + CDN + SSL)
>       │
>   VNet (10.0.0.0/16)
>       │
>   snet-web: App Service (VNet integrated, P1v3)
>       │ private endpoint
>   snet-api: Container App (internal ingress only)
>       │ managed identity
>   snet-db: Azure SQL (private endpoint, Entra auth)
>       │
>   Key Vault (private endpoint, RBAC)
>   Storage (private endpoint, lifecycle policies)
>   Log Analytics + App Insights (monitoring)
>
>   Security: Zero secrets (managed identities + KV references)
>   HA: Zone-redundant App Service + SQL Business Critical
>   DR: SQL Failover Group to paired region
> ```

**Q34: Your application has 10,000 file uploads per day. How do you architect the upload pipeline?**

> ```
>   1. API generates SAS token (write-only, 15-min expiry) → returns to client
>   2. Client uploads directly to Blob Storage (bypasses API)
>   3. Event Grid detects new blob → triggers Azure Function
>   4. Function validates, processes (resize/scan), moves to "processed" container
>   5. Function writes metadata to Cosmos DB (partition key: userId)
>   6. Function sends notification via Service Bus
>
>   Why: API never handles large files. Storage handles upload bandwidth.
>   Cost: ~$0 for Function (Consumption free tier for 1M/month).
>   Scale: Handles 10K-1M uploads/day without architecture changes.
> ```

---

*End of Azure Deep Dive Notes*
