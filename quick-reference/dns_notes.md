[🏠 Home](../README.md) · [Quick Reference](batch_state.md)

# 🌐 DNS — DevOps Quick Reference

> **Read time:** ~10 min | **Audience:** DevOps Engineers
> Simple explanations. ASCII diagrams. No fluff.

---

## Table of Contents
1. [What is DNS?](#1-what-is-dns)
2. [Key Terms](#2-key-terms)
3. [DNS Record Types](#3-dns-record-types)
4. [How DNS Works Behind the Scenes](#4-how-dns-works-behind-the-scenes)
5. [DNS Caching & TTL](#5-dns-caching--ttl)
6. [Azure DNS — What You Need to Know](#6-azure-dns--what-you-need-to-know)
7. [DNS Troubleshooting Commands](#7-dns-troubleshooting-commands)
8. [DevOps Gotchas ⚠️](#8-devops-gotchas)

---

## 1. What is DNS?

DNS = **Domain Name System** — the internet's phonebook.

Humans use names. Computers use IPs. DNS bridges them.

```
  You type:   www.myapp.com
       │
       ▼
  DNS resolves: www.myapp.com → 20.50.1.1
       │
       ▼
  Browser connects to: 20.50.1.1:443
```

Without DNS, you'd have to remember `20.50.1.1` instead of `myapp.com`.

---

## 2. Key Terms

| Term | What it means (simple) |
|------|------------------------|
| **Domain** | Human-readable name — `myapp.com` |
| **Zone** | The authoritative data for a domain — like a file containing all DNS records for `myapp.com` |
| **Nameserver (NS)** | The server that holds the zone file. When someone asks "who knows about myapp.com?", the answer is your NS |
| **Resolver** | The DNS client — usually your ISP or `8.8.8.8`. It does the legwork of finding the answer |
| **Recursive Resolver** | A resolver that chases down the full answer on your behalf (asking root → TLD → authoritative) |
| **Authoritative NS** | The final source of truth for a domain. Its answer is definitive |
| **Root Servers** | 13 clusters (`a.root-servers.net` → `m.root-servers.net`) — the starting point of every DNS resolution |
| **TLD** | Top-Level Domain — `.com`, `.org`, `.io`, `.in` — managed by IANA |
| **TTL** | Time To Live — how long (in seconds) a DNS answer is cached before being re-fetched |
| **Propagation** | How long it takes for DNS changes to spread across all resolvers on the internet (depends on TTL) |
| **Delegation** | Pointing a subdomain to a different NS — e.g., `api.myapp.com` NS → ns1.cloudflare.com |
| **FQDN** | Fully Qualified Domain Name — the complete domain: `www.myapp.com.` (note the trailing dot) |

---

## 3. DNS Record Types

| Record | Purpose | Real Example |
|--------|---------|--------------|
| **A** | Domain → IPv4 | `myapp.com → 20.50.1.1` |
| **AAAA** | Domain → IPv6 | `myapp.com → 2001:db8::1` |
| **CNAME** | Alias → another name (NOT an IP) | `www.myapp.com → myapp.com` |
| **MX** | Mail server for the domain | `myapp.com → mail.myapp.com (priority 10)` |
| **NS** | Which nameserver holds the zone | `myapp.com → ns1.azure-dns.com` |
| **TXT** | Free-text record — used for verification & email | `myapp.com → "v=spf1 include:..."` |
| **SOA** | Zone metadata — serial, refresh timers | Generated automatically by DNS provider |
| **SRV** | Service locator — host + port | `_sip._tcp.myapp.com → sip.myapp.com:5060` |
| **PTR** | Reverse DNS — IP → domain | `1.1.50.20.in-addr.arpa → myapp.com` |
| **CAA** | Which Certificate Authority can issue SSL certs | `myapp.com CAA → "letsencrypt.org"` |

### Email-specific TXT records (DevOps must-know)

```
  SPF  → Who is allowed to SEND email on behalf of your domain
         "v=spf1 include:sendgrid.net ~all"
         (prevents spoofing)

  DKIM → Cryptographic signature proving email hasn't been tampered
         "_domainkey.myapp.com TXT → public key"
         (prevents tampering)

  DMARC → Policy: what to do with emails that fail SPF/DKIM
          "v=DMARC1; p=reject; rua=mailto:admin@myapp.com"
          (tells receivers to reject fake emails)
```

> **Rule of thumb:** If you're setting up a new domain for sending emails — SPF + DKIM + DMARC are mandatory, otherwise your emails land in spam.

---

## 4. How DNS Works Behind the Scenes

Step-by-step what happens when you type `www.myapp.com`:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │  DNS RESOLUTION: www.myapp.com                                         │
  │                                                                        │
  │  ┌──────────┐  1. Query "www.myapp.com"   ┌─────────────────────────┐  │
  │  │  Browser │────────────────────────────►│  Recursive Resolver     │  │
  │  │          │                             │  (ISP / 8.8.8.8 / 1.1.1.1) │
  │  │          │  8. Answer: 20.50.1.1       │                         │  │
  │  │          │◄────────────────────────────│  (caches it for TTL)    │  │
  │  └──────────┘                             └────────────┬────────────┘  │
  │                                                        │               │
  │                                   2. "Who handles .com?"               │
  │                                                        ▼               │
  │                                          ┌─────────────────────────┐  │
  │                                          │  Root Servers            │  │
  │                                          │  (a-m.root-servers.net)  │  │
  │                                          │  ". (root zone)"         │  │
  │                                          └────────────┬────────────┘  │
  │                                                        │               │
  │                                   3. "Ask .com TLD servers"           │
  │                                                        ▼               │
  │                                          ┌─────────────────────────┐  │
  │                                          │  .com TLD Servers        │  │
  │                                          │  (Verisign)              │  │
  │                                          └────────────┬────────────┘  │
  │                                                        │               │
  │                           4. "Ask ns1.azure-dns.com (myapp.com NS)"   │
  │                                                        ▼               │
  │                                          ┌─────────────────────────┐  │
  │                                          │  Authoritative NS        │  │
  │                                          │  ns1.azure-dns.com       │  │
  │                                          │  (holds the zone file)   │  │
  │                                          └────────────┬────────────┘  │
  │                                                        │               │
  │                               5. "www.myapp.com A → 20.50.1.1"        │
  │                                                        │               │
  │                            ◄───────────────────────────┘               │
  │                   6. Resolver caches: www.myapp.com=20.50.1.1, TTL=300 │
  │                   7. Returns 20.50.1.1 to browser                      │
  └────────────────────────────────────────────────────────────────────────┘
```

**Key insight:** Steps 2–5 only happen on the **first** request (or after TTL expires). After that, the resolver answers from cache instantly.

### What "authoritative" means

```
  Registrar (GoDaddy / Namecheap)
     → You registered myapp.com here
     → You set NS records here: "ns1.azure-dns.com is authoritative"

  Azure DNS (or Cloudflare, Route 53)
     → You create your A, CNAME, MX records HERE
     → This is where the actual zone lives
```

> **Common confusion:** Changing NS records at the registrar and changing DNS records at Azure DNS are two completely different things. NS change = delegating to Azure. DNS records = what Azure answers with.

---

## 5. DNS Caching & TTL

TTL (seconds) = how long the answer is cached.

```
  ┌─────────────────────────────────────────────────────┐
  │  HIGH TTL (e.g., 86400 = 24 hours)                 │
  │                                                     │
  │  ✅ Less DNS traffic → faster repeat lookups        │
  │  ✅ Resilient (still works even if DNS goes down)   │
  │  ❌ Changes take HOURS to propagate everywhere      │
  │                                                     │
  │  Use for: stable records that rarely change         │
  │           (MX, NS, rarely-changed A records)        │
  ├─────────────────────────────────────────────────────┤
  │  LOW TTL (e.g., 60 = 1 minute)                     │
  │                                                     │
  │  ✅ Changes propagate in ~1 minute                  │
  │  ✅ Perfect for failover / migration                 │
  │  ❌ More DNS lookups → tiny added latency           │
  │                                                     │
  │  Use for: IP migrations, load balancer changes,     │
  │           disaster recovery                         │
  └─────────────────────────────────────────────────────┘
```

### TTL Strategy for Migration / Cutover

```
  Step 1: BEFORE migration
          Lower TTL to 60 seconds → wait 24h (let old TTL expire everywhere)

  Step 2: DURING migration
          Change the DNS record (A/CNAME) to point to new server

  Step 3: AFTER migration (confirmed working)
          Raise TTL back to 3600 or 86400

  Timeline:
  Day -1:  Set TTL = 60  ──► wait for old 86400 TTL to expire
  Day 0:   Switch record  ──► propagates in ~60 seconds
  Day +1:  Raise TTL = 3600 ──► reduce DNS query load
```

---

## 6. Azure DNS — What You Need to Know

### Public vs Private DNS Zones

```
  PUBLIC ZONE (myapp.com)               PRIVATE ZONE (internal.myapp.com)
  ─────────────────────────             ──────────────────────────────────
  Resolves from the internet            Resolves ONLY inside your VNet
  Anyone can query it                   Not visible outside Azure VNet
  Used for: website, API, email         Used for: DB, AKS, microservices

  myapp.com → 20.50.1.1                db.internal.myapp.com → 10.0.2.4
```

### Creating DNS Records (az CLI)

```bash
# Create a public DNS zone
az network dns zone create \
    --resource-group rg-prod \
    --name myapp.com

# Add A record (root domain)
az network dns record-set a add-record \
    --resource-group rg-prod --zone-name myapp.com \
    --record-set-name "@" --ipv4-address 20.50.1.1 --ttl 300

# Add A record (www subdomain)
az network dns record-set a add-record \
    --resource-group rg-prod --zone-name myapp.com \
    --record-set-name "www" --ipv4-address 20.50.1.1 --ttl 300

# Add CNAME (alias)
az network dns record-set cname set-record \
    --resource-group rg-prod --zone-name myapp.com \
    --record-set-name "api" --cname "api-prod.azurewebsites.net"

# Add TXT for domain verification or SPF
az network dns record-set txt add-record \
    --resource-group rg-prod --zone-name myapp.com \
    --record-set-name "@" --value "v=spf1 include:sendgrid.net ~all"

# Create private DNS zone (for internal services)
az network private-dns zone create \
    --resource-group rg-prod --name internal.myapp.com

# ⚠️ CRITICAL: Link private DNS zone to VNet (often forgotten!)
az network private-dns link vnet create \
    --resource-group rg-prod --zone-name internal.myapp.com \
    --name link-to-vnet-main --virtual-network vnet-main \
    --registration-enabled true
```

### Private Endpoints + DNS (the pattern)

When you use a Private Endpoint for Azure services (Key Vault, Storage, SQL), Azure creates a private IP inside your VNet. But your app still uses the public hostname. Fix = Private DNS zone.

```
  WITHOUT private DNS zone:
  App → "kv-prod.vault.azure.net" → resolves to PUBLIC IP → blocked by firewall ❌

  WITH private DNS zone:
  App → "kv-prod.vault.azure.net" → resolves to 10.0.2.5 (private) → works ✅

  The private DNS zone "privatelink.vaultcore.azure.net" maps:
  kv-prod.vault.azure.net → 10.0.2.5 (private endpoint IP)
```

---

## 7. DNS Troubleshooting Commands

```bash
# Basic lookup
dig myapp.com
dig myapp.com +short        # just the IP

# Query specific record types
dig myapp.com A             # IPv4
dig myapp.com AAAA          # IPv6
dig myapp.com MX            # Mail servers
dig myapp.com TXT           # SPF, DKIM, verification
dig myapp.com NS            # Nameservers
dig myapp.com CAA           # SSL cert authority

# Check from a specific resolver (test propagation)
dig @8.8.8.8 myapp.com      # Google
dig @1.1.1.1 myapp.com      # Cloudflare
dig @208.67.222.222 myapp.com  # OpenDNS

# Trace full resolution path (shows every step)
dig +trace myapp.com

# Reverse DNS (IP → hostname)
dig -x 20.50.1.1

# Windows (if dig not available)
nslookup myapp.com
nslookup -type=MX myapp.com

# Check your current resolver
cat /etc/resolv.conf
resolvectl status

# Flush local DNS cache
sudo resolvectl flush-caches          # Linux (systemd)
ipconfig /flushdns                    # Windows
sudo dscacheutil -flushcache          # macOS

# Check if record propagated (run from multiple places)
# Use: https://dnschecker.org or https://mxtoolbox.com
```

---

## 8. DevOps Gotchas ⚠️

### 1. CNAME cannot be used at root/apex
```
  WRONG:  myapp.com  CNAME  myapp.azurewebsites.net  ← DNS spec violation!
  RIGHT:  myapp.com  A      20.50.1.1
          www.myapp.com  CNAME  myapp.com             ← CNAME on subdomain ✅
```
If you need to alias root to another hostname, use Azure Traffic Manager or Front Door, which support "ALIAS/APEX" records.

### 2. TTL is propagation time — reduce BEFORE cutover
Most engineers change the DNS record and then wonder why it takes 24 hours to propagate. Lower TTL to 60 seconds **at least 24 hours before** the planned migration.

### 3. Private DNS zone MUST be linked to VNet
The most common reason Private Endpoints fail: the private DNS zone exists but isn't linked to the VNet. The VMs inside can't use a zone they don't know about.

```bash
# Check if zone is linked
az network private-dns link vnet list \
    --resource-group rg-prod --zone-name privatelink.vaultcore.azure.net
```

### 4. Alpine Linux / musl libc doesn't cache DNS
If you use Alpine-based Docker images, the musl C library **doesn't cache DNS**. Every DNS lookup is a fresh recursive query. In Kubernetes, this can flood CoreDNS.
- Fix: configure ndots properly, or use a full glibc image for DNS-heavy workloads.

### 5. Check NS records FIRST when DNS "doesn't work"
The #1 mistake: you add records in Azure DNS but the registrar (GoDaddy, Namecheap) still points to the old nameserver. Check NS delegation first.

```bash
# Check which NS is actually authoritative for myapp.com
dig myapp.com NS +short
# Should show: ns1.azure-dns.com, ns2.azure-dns.net, etc.
# If it shows your registrar's NS — you forgot to delegate!
```

### 6. DNS-based failover needs LOW TTL
If you use Traffic Manager or Front Door for failover, you need TTL ≤ 60 seconds. With TTL=86400, even if you switch the endpoint, users hit the failed server for up to 24 hours.

### 7. SOA serial number matters for zone transfers
If you're migrating DNS zones between providers, always verify the SOA serial increments correctly. A stale serial = slaves don't pull new records.

---

*Source: [Networking Handbook §7](../networking/networking_handbook.md) · [Azure Services Handbook §2.9](../azure-services/azure_services_handbook.md)*
