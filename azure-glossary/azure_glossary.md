# ☁️ Azure Complete Glossary — DevOps & Infrastructure Terms

> **500+ terms** explained in beginner-friendly language with real-world DevOps examples, ASCII diagrams, gotchas, and production FAQs.
> **Last updated:** 2026-05-12

---

## 📑 Table of Contents

1. [Azure Foundations & IaC](#1--azure-foundations--iac)
2. [Identity & Access Management](#2--identity--access-management)
3. [Networking Core](#3--networking-core)
4. [DNS, VPN & ExpressRoute](#4--dns-vpn--expressroute)
5. [Network Security](#5--network-security)
6. [Load Balancing & Traffic](#6--load-balancing--traffic-management)
7. [Private Connectivity & Network Tools](#7--private-connectivity--network-tools)
8. [Compute](#8--compute)
9. [Containers & Kubernetes](#9--containers--kubernetes)
10. [Storage & Databases](#10--storage--databases)
11. [Azure Virtual Desktop (AVD)](#11--azure-virtual-desktop-avd)
12. [Monitoring & KQL](#12--monitoring--kql)
13. [Security](#13--security)
14. [DevOps & Deployment](#14--devops--deployment-strategies)
15. [Governance, Cost & DR](#15--governance-cost--disaster-recovery)
16. [Advanced Networking & Protocols](#16--advanced-networking--protocols)
17. [Advanced Compute, Patterns & Caching](#17--advanced-compute-patterns--caching)
18. [AD DS Fundamentals](#18--active-directory-domain-services-fundamentals)
19. [AD Authentication, GPO & Replication](#19--ad-authentication-gpo--replication)
20. [Hybrid Identity & Federation](#20--hybrid-identity--federation)
21. [AD Security, Attacks & Operations](#21--ad-security-attacks--operations)

---

# 1 — Azure Foundations & IaC

---

### Azure Regions

**What:** A region is a set of datacenters in a geographic area (e.g., East US, West Europe). Each region has 1-3 availability zones.

**DevOps example:** You deploy your production app to `East US` because most users are in North America. Your DR copy goes to `West US` (paired region).

```
  ┌─────────────┐  300+ miles  ┌─────────────┐
  │  East US    │◄════════════►│  West US    │
  │  (primary)  │  region pair  │  (DR)       │
  │  3 zones    │              │  3 zones    │
  └─────────────┘              └─────────────┘
```

> ⚠️ **Gotcha:** Not all services are available in all regions. Check `az account list-locations` before choosing.

---

### Region Pairs

**What:** Microsoft pairs two regions 300+ miles apart. If one fails, the other gets priority recovery. Updates are rolled to one region at a time (never both simultaneously).

**Example pairs:** East US ↔ West US, North Europe ↔ West Europe, Southeast Asia ↔ East Asia.

> **FAQ:** *Can I choose my own pair?* No. Microsoft assigns pairs. You can deploy to any two regions, but only official pairs get priority recovery and sequential updates.

---

### Availability Zones

**What:** Physically separate datacenters WITHIN one region. Each zone has its own power, cooling, and network. There are typically 3 zones per region.

```
  Region: East US
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │  Zone 1  │ │  Zone 2  │ │  Zone 3  │
  │  DC-A    │ │  DC-B    │ │  DC-C    │
  │  VM-1    │ │  VM-2    │ │  VM-3    │
  └──────────┘ └──────────┘ └──────────┘
  Each zone = separate building, separate power grid
  SLA: 99.99% when spread across zones
```

**DevOps example:** Deploy 3 replicas of your API, one in each zone. If an entire datacenter catches fire, 2/3 replicas survive.

> ⚠️ **Gotcha:** Zone numbers (1,2,3) are logical — Zone 1 for subscription A might be a different physical building than Zone 1 for subscription B.

---

### Availability Sets

**What:** Spread VMs across fault domains (racks) and update domains within ONE datacenter. Older than Availability Zones.

```
  ┌─────────────────────────────────────────┐
  │  Availability Set                       │
  │  FD 0 (Rack A)  │  FD 1 (Rack B)      │
  │  UD 0: VM-1     │  UD 1: VM-2          │
  │  UD 2: VM-3     │  UD 3: VM-4          │
  └─────────────────────────────────────────┘
  SLA: 99.95%
```

> **FAQ:** *Should I use Availability Sets or Zones?* **Zones** whenever possible (99.99% vs 99.95%). Sets are for regions without zone support.

---

### Fault Domains

**What:** A physical rack with shared power and network switch. VMs in different fault domains survive rack failures.

**Plain English:** If Rack A's power supply blows up, VMs on Rack B keep running.

---

### Update Domains

**What:** Logical groups for planned maintenance. Azure reboots one update domain at a time during patches. Default: 5 UDs per availability set.

**Plain English:** Azure never reboots ALL your VMs at once during Windows Updates — it does one group at a time.

---

### SLA (Service Level Agreement)

**What:** Microsoft's uptime promise. If they miss it, you get billing credits.

```
  ┌───────────┬────────────────────┬──────────────────┐
  │ SLA       │ Allowed downtime   │ Example          │
  ├───────────┼────────────────────┼──────────────────┤
  │ 99.9%     │ 8.76 hours/year    │ Single VM        │
  │ 99.95%    │ 4.38 hours/year    │ Availability Set │
  │ 99.99%    │ 52.6 minutes/year  │ Availability Zone│
  │ 99.999%   │ 5.26 minutes/year  │ Cosmos DB multi  │
  └───────────┴────────────────────┴──────────────────┘
```

> ⚠️ **Gotcha:** SLA only applies if you meet configuration requirements. A single VM with Standard HDD has NO SLA.

---

### Resource Groups

**What:** Logical container for related Azure resources. Like a folder — organizes resources that share the same lifecycle.

**DevOps example:** `rg-myapp-prod` holds the App Service, SQL DB, Key Vault, and Storage for one app's production environment.

> ⚠️ **Gotcha:** A resource group has a region, but resources inside can be in ANY region. The RG region only stores metadata.

> **FAQ:** *One RG per app or per environment?* Per app+environment: `rg-myapp-prod`, `rg-myapp-dev`. Delete the RG = delete everything in it.

---

### Management Groups

**What:** Containers ABOVE subscriptions for organizing at enterprise scale. Apply policies and RBAC to 100s of subscriptions at once.

```
  Root Management Group
  ├── MG: Production
  │   ├── Sub: Prod-App1
  │   └── Sub: Prod-App2
  ├── MG: Development
  │   └── Sub: Dev-All
  └── MG: Sandbox
      └── Sub: Sandbox-Free
```

**DevOps example:** Apply "deny public IPs" policy at the Production management group → ALL prod subscriptions inherit it automatically.

---

### Subscriptions

**What:** A billing and access boundary. Each subscription gets its own bill and has resource quotas (e.g., max 250 storage accounts).

**DevOps example:** Most companies use separate subscriptions for prod/dev to isolate blast radius and billing.

> ⚠️ **Gotcha:** Resources in different subscriptions CAN communicate via VNet peering, but RBAC doesn't cross subscription boundaries by default.

---

### Tags

**What:** Key-value labels on resources for organizing, cost tracking, and automation. Example: `environment=production`, `team=backend`, `cost-center=CC-1234`.

> ⚠️ **Gotcha:** Tags are NOT inherited from resource groups. Use Azure Policy to auto-apply tags from the RG. Max 50 tags per resource.

---

### Resource Locks

**What:** Prevent accidental deletion or modification of critical resources.

| Lock type | Effect |
|-----------|--------|
| **ReadOnly** | Can read but can't modify or delete |
| **Delete** | Can modify but can't delete |

**DevOps example:** Put a Delete lock on your production SQL server. Even an Owner-role user can't accidentally delete it.

> ⚠️ **Gotcha:** Locks are inherited — a lock on a resource group applies to ALL resources inside.

---

### ARM Templates

**What:** JSON files that define Azure infrastructure declaratively. Azure Resource Manager (ARM) reads the template and creates/updates resources.

```json
{
  "resources": [{
    "type": "Microsoft.Web/sites",
    "name": "myapp-prod",
    "location": "eastus",
    "properties": { "httpsOnly": true }
  }]
}
```

> ⚠️ **Gotcha:** ARM templates are verbose JSON — a simple VM can be 200+ lines. Most teams prefer Bicep (compiles to ARM JSON).

---

### Bicep

**What:** Azure's DSL (Domain-Specific Language) that compiles to ARM JSON. Much cleaner and shorter syntax.

```bicep
resource web 'Microsoft.Web/sites@2023-01-01' = {
  name: 'myapp-prod'
  location: 'eastus'
  properties: { httpsOnly: true }
}
```

**DevOps example:** Your CI/CD pipeline runs `az deployment group create --template-file main.bicep` to deploy infrastructure.

---

### Terraform

**What:** HashiCorp's multi-cloud IaC tool. Uses HCL (HashiCorp Configuration Language). Works with Azure, AWS, GCP, and 1000s of providers.

```hcl
resource "azurerm_resource_group" "rg" {
  name     = "rg-myapp-prod"
  location = "eastus"
}
```

> **FAQ:** *Bicep or Terraform?* Bicep = Azure-only, tighter integration, no state file. Terraform = multi-cloud, larger ecosystem, requires state management. Both are industry-standard.

---

### Infrastructure as Code (IaC)

**What:** Define infrastructure in code files (not clicking in portal). Store in Git, review via PR, deploy via CI/CD. Reproducible, auditable, version-controlled.

```
  Without IaC:                    With IaC:
  Click portal → create VM        Push code → PR → CI/CD → VM created
  No record of what changed       Git history shows every change
  Can't reproduce reliably         Deploy exact same infra in 5 min
```

---

### Idempotency

**What:** Running the same operation multiple times produces the SAME result. If a resource already exists, IaC doesn't create a duplicate — it skips or updates.

**DevOps example:** Run `terraform apply` 5 times → same infrastructure every time. No duplicates.

> ⚠️ **Gotcha:** Imperative scripts (bash `az` commands) are NOT idempotent by default — `az vm create` will fail if the VM already exists unless you add `--if-exists` checks.

---

### Declarative Deployments

**What:** You describe the DESIRED STATE ("I want 3 VMs"), and the tool figures out how to get there.

**Tools:** ARM, Bicep, Terraform, Kubernetes YAML.

---

### Imperative Deployments

**What:** You give STEP-BY-STEP commands ("create VM, then attach disk, then set NSG").

**Tools:** Azure CLI (`az`), PowerShell, bash scripts.

```
  Declarative: "I want a pizza"      → chef figures out steps
  Imperative:  "Make dough, add      → you give each step
               sauce, add cheese,
               bake at 400°F"
```

> **FAQ:** *Which is better?* Declarative for infrastructure (reproducible). Imperative for one-off operations (quick fixes, debugging).

---

# 2 — Identity & Access Management

---

### Entra ID (formerly Azure AD)

**What:** Microsoft's cloud identity service. Authenticates users, apps, and services. Every Azure tenant has one. Think of it as the "login system" for all Microsoft cloud services.

```
  User types "username@company.com" + password
       │
       ▼
  Entra ID validates credentials
       │
       ├── Issues OAuth2 token (access_token)
       ▼
  Token used to access Azure, M365, custom apps
```

> ⚠️ **Gotcha:** Entra ID is NOT Active Directory Domain Services (AD DS). Entra ID = cloud identity (REST/OAuth2). AD DS = on-prem (Kerberos/LDAP). They can sync via Entra Connect.

---

### Tenant

**What:** A dedicated instance of Entra ID for your organization. Created automatically when you sign up for Azure. Has a unique ID and a domain (e.g., `company.onmicrosoft.com`).

**Plain English:** Your company's own private identity database in the cloud. One company = one tenant.

> **FAQ:** *Can I have multiple tenants?* Yes, but it complicates management. Most orgs use one tenant with multiple subscriptions.

---

### Users

**What:** Identity objects in Entra ID. Can be cloud-only (created in portal) or synced from on-prem AD via Entra Connect.

**Types:** Member users (employees), Guest users (external — B2B collaboration).

---

### Groups

**What:** Containers for users. Assign RBAC roles to a group → all members get that role. Two types: Security groups (for access control) and Microsoft 365 groups (for collaboration).

**Dynamic groups** = membership auto-managed by rules (e.g., "all users in Engineering department").

> ⚠️ **Gotcha:** Dynamic group membership can take up to 24 hours to update. Don't rely on it for time-sensitive access changes.

---

### Enterprise Applications

**What:** A record in your tenant for an app your org USES (e.g., Salesforce, GitHub, ServiceNow). Controls who can access the app and how they authenticate (SSO, MFA, etc.).

**Plain English:** "These are the apps our company has approved and connected to our login system."

---

### App Registrations

**What:** A record for an app your org BUILDS. Defines the app's identity (client ID, redirect URIs, API permissions). Creates a corresponding Service Principal.

```
  App Registration = app's "birth certificate" (global definition)
  Enterprise App   = app's "employee badge" (per-tenant access control)
```

---

### Service Principals

**What:** The identity object that an application uses to authenticate to Azure. When you register an app, a service principal is created in your tenant.

**DevOps example:** Your CI/CD pipeline uses a service principal to deploy resources: `az login --service-principal -u $CLIENT_ID -p $SECRET --tenant $TENANT`.

> ⚠️ **Gotcha:** Service principal secrets expire (default: 1-2 years). Set calendar reminders or use certificate-based auth. Expired secrets = broken pipelines at 2 AM.

---

### Managed Identity

**What:** Azure automatically manages credentials for your app — no secrets to store, rotate, or leak. The identity exists only while the resource exists.

```
  WITHOUT managed identity:
  App → reads secret from Key Vault → uses secret to auth to SQL
  (How does the app authenticate to Key Vault? More secrets!)

  WITH managed identity:
  App → Azure auto-injects token → uses token to auth to SQL
  (No secrets anywhere. Azure handles everything.)
```

---

### System-Assigned Managed Identity

**What:** Tied to ONE resource. Created when you enable it, deleted when the resource is deleted. 1:1 relationship.

**Example:** Enable on App Service → that specific app gets its own identity → delete the app → identity gone.

---

### User-Assigned Managed Identity

**What:** Standalone identity resource. Can be shared across MULTIPLE resources. Survives if one resource is deleted.

**Example:** Create `id-shared-prod` → assign to App Service, Function App, and AKS. All three use the same identity to access Key Vault.

> **FAQ:** *System or User assigned?* System = simple, single-resource. User = shared across resources, survives redeployment.

---

### OAuth2

**What:** Authorization framework. App requests permission to access resources ON BEHALF of a user. Returns an access_token.

```
  User → Login → Entra ID → access_token → App uses token to call API
  
  The token says: "User John authorized App X to read his email"
  The API checks the token, not a password.
```

**Plain English:** OAuth2 is like giving a hotel front desk your ID (you prove who you are), and they give you a room key (token) that only opens your room (scoped access).

---

### OpenID Connect (OIDC)

**What:** Layer on TOP of OAuth2 that adds identity (who the user IS). Returns an `id_token` (JWT with user info) plus the OAuth2 `access_token`.

**Plain English:** OAuth2 = "what are you allowed to do?" OIDC = "who ARE you?" + "what are you allowed to do?"

---

### SAML

**What:** Older XML-based SSO protocol. Enterprise apps (Salesforce, SAP) still use it. Entra ID supports SAML for SSO with these legacy apps.

> **FAQ:** *SAML vs OIDC?* New apps → OIDC. Legacy enterprise apps → SAML. Both do SSO, OIDC is simpler and JSON-based.

---

### Kerberos

**What:** On-prem authentication protocol used by AD DS. Ticket-based — user gets a TGT (Ticket Granting Ticket) from the Domain Controller, then uses it to access services without re-entering passwords.

```
  User login → DC issues TGT → User presents TGT → DC issues Service Ticket → Access granted
```

> ⚠️ **Gotcha:** Kerberos doesn't work over the internet (requires line-of-sight to DC). That's why Entra ID uses OAuth2/OIDC instead.

---

### MFA (Multi-Factor Authentication)

**What:** Require two or more proofs of identity: something you KNOW (password), something you HAVE (phone/authenticator), something you ARE (biometrics).

**DevOps example:** Enforce MFA for all users accessing Azure portal and CI/CD pipelines via Conditional Access policies.

> ⚠️ **Gotcha:** MFA alone doesn't protect against token theft. Combine with Conditional Access (device compliance, location restrictions).

---

### Conditional Access

**What:** "If-then" policies for access decisions. IF user is logging in FROM an untrusted network, THEN require MFA. IF device is non-compliant, THEN block access.

```
  ┌─────────────────────────────────────────────────┐
  │  Conditional Access Policy                      │
  │                                                 │
  │  IF:   User is in "All Employees" group         │
  │  AND:  Accessing Azure Portal                   │
  │  AND:  From outside corporate network           │
  │  THEN: Require MFA + compliant device           │
  │                                                 │
  │  IF:   User is in "Admins" group                │
  │  THEN: ALWAYS require MFA + managed device      │
  └─────────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Conditional Access requires Entra ID P1 or P2 license. Not available on free tier.

---

### PIM (Privileged Identity Management)

**What:** Just-in-time privileged access. Admins don't have permanent Owner/Contributor roles — they "activate" the role for a limited time (e.g., 4 hours) with approval + MFA.

```
  Without PIM:  User has Owner role 24/7 (dangerous)
  With PIM:     User requests Owner → approver approves → 4-hour window → auto-revoked
```

**DevOps example:** SRE needs to restart a production SQL server. They activate "Contributor" via PIM for 2 hours, do the work, and the role auto-expires.

---

### RBAC (Role-Based Access Control)

**What:** Assign permissions to users/groups/SPs at a specific scope. Role + Principal + Scope = Role Assignment.

```
  ┌──────────────┬─────────────────────┬───────────────────┐
  │ Role         │ What it allows      │ When to use       │
  ├──────────────┼─────────────────────┼───────────────────┤
  │ Reader       │ View everything     │ Auditors, devs    │
  │ Contributor  │ Create/manage all   │ DevOps, developers│
  │              │ but can't assign    │                   │
  │              │ roles               │                   │
  │ Owner        │ Everything +        │ Team leads only   │
  │              │ assign roles        │                   │
  │ User Access  │ Only manage role    │ Identity admins   │
  │ Administrator│ assignments         │                   │
  └──────────────┴─────────────────────┴───────────────────┘

  Scope hierarchy: Management Group → Subscription → RG → Resource
  Roles INHERIT downward.
```

> ⚠️ **Gotcha:** RBAC changes can take up to 5 minutes to propagate. Don't panic if permissions don't work immediately.

---

### Custom Roles

**What:** When built-in roles don't fit, create your own. Define exactly which actions are allowed/denied.

**DevOps example:** Create "VM Operator" role that can start/stop/restart VMs but NOT delete them or modify networking.

---

### Least Privilege Principle

**What:** Give users the MINIMUM permissions needed to do their job. Never give Owner when Contributor works. Never give Contributor when a custom role with fewer permissions works.

---

### Azure AD Connect (Entra Connect)

**What:** Syncs on-prem AD users/groups to Entra ID. Enables hybrid identity — one username + password for both on-prem and cloud.

```
  On-Prem AD DS ═══ Entra Connect ═══► Entra ID (cloud)
  john@corp.com      (sync every       john@corp.com
  (Kerberos/LDAP)     30 minutes)      (OAuth2/OIDC)
```

---

### Pass-through Authentication (PTA)

**What:** Cloud auth requests are forwarded to on-prem AD for validation. Passwords NEVER stored in the cloud. Requires an on-prem agent.

---

### Federation (AD FS)

**What:** An on-prem federation server (AD FS) handles all authentication. Entra ID redirects login to your AD FS server. Most complex setup — being replaced by PHS + Seamless SSO.

> **FAQ:** *PHS vs PTA vs Federation?* PHS = simplest, password hashes in cloud. PTA = passwords stay on-prem. Federation = full control but complex. Most new deployments → PHS + Seamless SSO.

---

### Seamless SSO

**What:** Users on domain-joined devices inside the corporate network are automatically signed into Entra ID — no password prompt. Uses Kerberos tickets behind the scenes.

**Plain English:** Open your browser at work → go to Azure Portal → you're already logged in. No password needed.

---

# 3 — Networking Core

---

### VNet (Virtual Network)

**What:** Your private network in Azure. An isolated IP address space where you deploy resources. Resources inside a VNet can talk to each other by default. Resources in DIFFERENT VNets cannot (unless you peer them).

```
  ┌──────────────────────────────────────────┐
  │  VNet: vnet-prod (10.0.0.0/16)          │
  │  = 65,536 IP addresses                  │
  │                                          │
  │  ┌──────────────┐ ┌──────────────┐      │
  │  │ snet-web     │ │ snet-db      │      │
  │  │ 10.0.1.0/24  │ │ 10.0.2.0/24  │      │
  │  │ (256 IPs)    │ │ (256 IPs)    │      │
  │  │ VM-web       │ │ VM-sql       │      │
  │  └──────────────┘ └──────────────┘      │
  │                                          │
  │  Subnets can talk to each other (default)│
  └──────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** VNet CIDR ranges cannot overlap with other VNets you want to peer. Plan your IP scheme BEFORE deploying anything.

---

### Subnets

**What:** Segments within a VNet. Each subnet gets a chunk of the VNet's address space. Use subnets to isolate tiers (web, app, DB) and apply different security rules (NSGs).

**Azure reserves 5 IPs per subnet:** `.0` (network), `.1` (gateway), `.2-.3` (DNS), `.255` (broadcast). A /24 gives 251 usable IPs, not 256.

> ⚠️ **Gotcha:** Some services require dedicated subnets (AKS needs /23, Container Apps needs /23, Azure Firewall needs a subnet named `AzureFirewallSubnet`).

---

### CIDR (Classless Inter-Domain Routing)

**What:** Notation for IP ranges. `10.0.0.0/16` means "10.0.x.x" = 65,536 IPs. The `/16` = first 16 bits are fixed (the network), remaining 16 bits are hosts.

```
  ┌────────┬──────────┬────────────────────┐
  │ CIDR   │ IPs      │ Common use         │
  ├────────┼──────────┼────────────────────┤
  │ /8     │ 16.7M    │ Huge enterprise    │
  │ /16    │ 65,536   │ VNet               │
  │ /24    │ 256      │ Subnet             │
  │ /27    │ 32       │ Small subnet       │
  │ /28    │ 16       │ Gateway subnet     │
  │ /32    │ 1        │ Single host        │
  └────────┴──────────┴────────────────────┘
  
  Private ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
```

---

### IP Addressing

**What:** Azure resources get Private IPs (within VNet, like 10.0.1.5) and optionally Public IPs (internet-reachable). Public IPs can be Static (stays same) or Dynamic (changes on restart).

> ⚠️ **Gotcha:** Dynamic public IPs change when you stop/deallocate a VM. Use Static IPs for DNS records or firewall allowlists.

---

### DHCP

**What:** Azure manages DHCP internally. When a VM boots, Azure automatically assigns it an IP from the subnet range. You don't run a DHCP server — Azure IS the DHCP server.

---

### VNet Peering

**What:** Connect two VNets so resources can communicate across them. Traffic stays on Microsoft's backbone (never hits the public internet). Low latency, high bandwidth.

```
  ┌─────────────┐         ┌─────────────┐
  │ vnet-prod   │◄═══════►│ vnet-shared │
  │ 10.0.0.0/16 │ peering │ 10.1.0.0/16 │
  │ App VMs     │         │ DNS, AD DS  │
  └─────────────┘         └─────────────┘
  
  ⚠️ Peering is NOT transitive:
  A ↔ B and B ↔ C does NOT mean A ↔ C
```

> ⚠️ **Gotcha:** VNet address spaces CANNOT overlap. `10.0.0.0/16` can't peer with `10.0.0.0/16`. Plan CIDR ranges upfront.

---

### Global VNet Peering

**What:** Same as VNet peering but across DIFFERENT regions (e.g., East US ↔ West Europe). Works identically but adds cross-region latency (~1-5ms).

---

### Gateway Transit

**What:** When VNet A has a VPN/ExpressRoute gateway, peered VNet B can USE that gateway to reach on-prem. VNet B doesn't need its own gateway — saves money.

```
  On-Prem ═══ VPN GW ═══ vnet-hub ◄══► vnet-spoke
                          (has GW)       (uses hub's GW
                                          via transit)
```

---

### Route Tables

**What:** A set of routing rules attached to a subnet. Tells Azure WHERE to send traffic matching a given destination.

---

### UDR (User Defined Routes)

**What:** Custom routes you add to override Azure's default (system) routes. Typically used to force traffic through a firewall or NVA.

```
  Default:  Subnet → Internet  (direct)
  With UDR: Subnet → 0.0.0.0/0 → next hop: Firewall (10.0.4.4)
```

**DevOps example:** Force all outbound traffic from your app subnet through Azure Firewall for logging and inspection.

---

### System Routes

**What:** Azure's built-in routes that handle VNet-to-VNet, subnet-to-subnet, and internet traffic automatically. You never create these — Azure manages them.

---

### BGP (Border Gateway Protocol)

**What:** Protocol for exchanging routes between your on-prem network and Azure (via VPN Gateway or ExpressRoute). On-prem routers "advertise" their networks, Azure "learns" them automatically.

> ⚠️ **Gotcha:** If you disable BGP route propagation on a route table, Azure won't learn on-prem routes for that subnet — traffic to on-prem will fail.

---

### Route Propagation

**What:** When a VPN/ExpressRoute gateway learns routes via BGP, it "propagates" (shares) those routes to subnet route tables. Can be enabled/disabled per route table.

---

### Route Advertisement

**What:** The act of a router telling its neighbors "I can reach these networks." Your on-prem router advertises `192.168.0.0/16` → Azure VPN Gateway learns it → traffic from Azure to `192.168.x.x` goes through the VPN.

---

### Blackhole Route

**What:** A route that drops all matching traffic. Next hop = `None`. Packets going to that destination are silently discarded.

**DevOps example:** Add `0.0.0.0/0 → None` on a database subnet to guarantee it can NEVER reach the internet.

---

### Asymmetric Routing

**What:** Traffic takes a different path going OUT than coming BACK. This breaks stateful firewalls because the return packet doesn't match the tracked session.

```
  Request:  Client → LB → Firewall → VM
  Response: VM → direct → Client   (skipped firewall!)
  
  Firewall sees the response without seeing the original request → DROPS it
```

> ⚠️ **Gotcha:** Common when mixing UDRs and load balancers. Always ensure return traffic follows the same path.

---

### Forced Tunneling

**What:** Force ALL internet-bound traffic from Azure back to on-prem through a VPN, so it exits through your corporate firewall instead of Azure's internet gateway.

```
  Without forced tunneling:
  Azure VM → Internet (direct via Azure)

  With forced tunneling:
  Azure VM → VPN → On-Prem Firewall → Internet
```

> ⚠️ **Gotcha:** Breaks Azure services that need outbound internet access (App Service, Azure Monitor). Use split tunneling or service tag routes.

---

### Hairpinning

**What:** Traffic goes out an interface and comes right back in the same interface. Example: two VMs behind the same load balancer trying to talk to each other via the LB's public IP.

---

### Transit Routing / Transit VNet

**What:** Using one VNet (the hub) to route traffic between two other VNets (spokes) that don't directly peer with each other. Traffic transits through the hub's NVA or firewall.

---

### Shared Services VNet

**What:** A VNet containing services used by all other VNets: DNS servers, AD domain controllers, monitoring agents, jump boxes. All spoke VNets peer to this hub.

---

### Hub-Spoke Architecture

**What:** The standard enterprise Azure network design. One central "hub" VNet with shared services (firewall, VPN, DNS), and multiple "spoke" VNets for workloads.

```
  ┌──────────────────────────────────────────────────┐
  │                                                  │
  │              ┌──────────────┐                    │
  │    ┌────────►│  Hub VNet    │◄────────┐          │
  │    │         │  Firewall    │         │          │
  │    │         │  VPN Gateway │         │          │
  │    │         │  DNS, AD     │         │          │
  │    │         └──────────────┘         │          │
  │    │peering       │peering           │peering   │
  │    ▼              ▼                   ▼          │
  │ ┌────────┐  ┌────────┐         ┌────────┐      │
  │ │Spoke 1 │  │Spoke 2 │         │Spoke 3 │      │
  │ │Web App │  │API     │         │Data    │      │
  │ └────────┘  └────────┘         └────────┘      │
  │                                                  │
  │  Spokes talk to each other via Hub Firewall     │
  │  All internet traffic exits via Hub Firewall    │
  └──────────────────────────────────────────────────┘
```

> **FAQ:** *Why not peer all spokes directly?* Hub-spoke centralizes security (one firewall), reduces peering count, and enforces traffic inspection.

---

### Mesh Architecture

**What:** Every VNet peers with every other VNet directly. No hub. Simpler for small setups but doesn't scale (N VNets = N×(N-1)/2 peerings).

---

### East-West Traffic

**What:** Traffic BETWEEN workloads within your network (e.g., web tier → API tier, spoke-to-spoke). Lateral/horizontal movement.

---

### North-South Traffic

**What:** Traffic entering or leaving your network (e.g., internet user → your app, your app → external API). Vertical movement through the network boundary.

```
  ┌────── North-South ──────┐
  │   Internet / Users      │
  │          ↕               │
  │   ┌─── Firewall ───┐    │
  │   │                 │    │
  │   │  Web ←→ API     │    │ ← East-West
  │   │  API ←→ DB      │    │ ← East-West
  │   └─────────────────┘    │
  └──────────────────────────┘
```

---

### DMZ (Demilitarized Zone)

**What:** A network segment between the internet and your internal network. Hosts public-facing services (reverse proxy, WAF) that inspect traffic before it reaches internal servers.

---

### NVA (Network Virtual Appliance)

**What:** A VM running third-party firewall/routing software (Palo Alto, Fortinet, Barracuda). Sits in a subnet and inspects traffic forwarded to it via UDRs.

**DevOps example:** All east-west traffic between spokes is routed through a Palo Alto NVA in the hub for deep packet inspection.

> ⚠️ **Gotcha:** Must enable "IP Forwarding" on the NVA's NIC in Azure, otherwise Azure drops forwarded packets.

---

### Spoke Isolation

**What:** Spokes cannot communicate with each other unless explicitly routed through the hub firewall. This is the default in hub-spoke — peering is only hub↔spoke, not spoke↔spoke.

---

# 4 — DNS, VPN & ExpressRoute

---

### Azure DNS

**What:** Microsoft-managed DNS hosting. You create a DNS zone (e.g., `myapp.com`) and add records (A, CNAME, MX, TXT). Uses Azure's global anycast network — ultra-fast resolution worldwide.

**DevOps example:** Point `api.myapp.com` (CNAME) → your App Service `myapp-prod.azurewebsites.net`.

> ⚠️ **Gotcha:** Azure DNS hosts YOUR zones but is NOT a domain registrar. Buy domain from GoDaddy/Namecheap → point nameservers to Azure DNS.

---

### Private DNS Zones

**What:** DNS resolution that works ONLY inside your VNets. Resources resolve private hostnames without exposing them to the public internet.

```
  Public DNS:
  myapp.azurewebsites.net → 52.146.x.x (public IP)

  Private DNS Zone (privatelink.azurewebsites.net):
  myapp.azurewebsites.net → 10.0.5.4 (private IP)
  
  Only works from VNets linked to the private zone.
  Internet users still get the public IP.
```

**DevOps example:** Create a Private Endpoint for Azure SQL → auto-registers in `privatelink.database.windows.net` Private DNS Zone → all VNet VMs resolve the SQL FQDN to its private IP.

---

### DNS Resolution

**What:** The process of translating a hostname (e.g., `myapp.com`) to an IP (e.g., `10.0.1.5`). Azure VNets use Azure-provided DNS (168.63.129.16) by default, or you can point to custom DNS servers.

---

### DNS Forwarding

**What:** A DNS server that forwards queries it can't answer to another DNS server. Used in hybrid scenarios: Azure DNS server forwards `corp.local` queries → on-prem DNS server.

```
  Azure VM asks: "What is fileserver.corp.local?"
       │
       ▼
  Azure DNS Forwarder (10.0.1.10)
       │ "I don't know corp.local, let me ask on-prem"
       ▼
  On-Prem DNS (192.168.1.10)
       │ "fileserver.corp.local = 192.168.1.50"
       ▼
  Answer returned to Azure VM
```

---

### Conditional Forwarders

**What:** Forward DNS queries for SPECIFIC domains to specific DNS servers. Unlike regular forwarding (which forwards everything), conditional forwarders are domain-targeted.

**Example:** Forward `corp.local` → on-prem DNS. Forward `partner.com` → partner's DNS. Everything else → Azure DNS.

---

### Split-Horizon DNS

**What:** Same domain name resolves to DIFFERENT IPs depending on where the query comes from. Internal users get the private IP, external users get the public IP.

```
  External user asks for myapp.com → 52.146.x.x (public LB)
  Internal user asks for myapp.com → 10.0.1.5 (private IP)
```

**DevOps example:** Employees in the VNet access the app directly (fast, no hairpinning). Internet users go through the WAF/CDN.

---

### Recursive Resolver

**What:** A DNS server that chases the full resolution chain on your behalf: root servers → TLD servers → authoritative servers → answer. Azure's built-in DNS (168.63.129.16) is a recursive resolver.

---

### Authoritative DNS

**What:** The DNS server that has the OFFICIAL answer for a domain. When you host `myapp.com` in Azure DNS, Azure DNS is the authoritative server for that zone.

---

### Azure DNS Private Resolver

**What:** A managed service that provides DNS forwarding between Azure VNets and on-prem networks. Replaces the need to deploy custom DNS VMs in your hub.

```
  ┌──────────────────────────────────────────────┐
  │  VNet Hub                                    │
  │                                              │
  │  DNS Private Resolver                        │
  │  ├── Inbound Endpoint (10.0.0.4)            │
  │  │   On-prem forwards HERE for Azure zones   │
  │  └── Outbound Endpoint (10.0.0.5)           │
  │      Azure forwards HERE for on-prem zones   │
  └──────────────────────────────────────────────┘
```

> **FAQ:** *Why not just use a VM as DNS forwarder?* Private Resolver is managed, HA, auto-scaled. DNS VMs need patching, monitoring, and failover config.

---

### DNS Forwarding Chain

**What:** Multiple DNS servers chained: VM → Azure DNS → Forwarder → On-prem DNS. Each server forwards to the next for domains it doesn't own. Keep chains short to avoid latency.

---

### VPN Gateway

**What:** A managed gateway in your VNet that creates encrypted tunnels to other networks (on-prem, other VNets, remote users). Uses IPSec/IKE protocols.

```
  ┌──────────┐   IPSec tunnel    ┌──────────┐
  │ Azure    │═══════════════════│ On-Prem  │
  │ VPN GW   │ (over internet)  │ Firewall │
  │ 10.0.0.0 │                  │ 192.168.0│
  └──────────┘                  └──────────┘
```

> ⚠️ **Gotcha:** VPN Gateway requires a dedicated subnet named `GatewaySubnet` (recommended /27). Deploying a VPN GW takes 30-45 minutes.

---

### Site-to-Site VPN (S2S)

**What:** Permanent encrypted tunnel between your on-prem network and Azure VNet. Always-on connection. Requires a VPN device on-prem (firewall/router with public IP).

**DevOps example:** Your office network (192.168.0.0/16) connects to Azure VNet (10.0.0.0/16) via S2S VPN. All developers can access Azure VMs from their desks.

---

### Point-to-Site VPN (P2S)

**What:** Individual user's laptop connects to Azure VNet via VPN client. No VPN device needed — just install the Azure VPN client.

**DevOps example:** Remote developers connect to the dev VNet from their homes to access internal resources.

---

### VNet-to-VNet VPN

**What:** Encrypted tunnel between two Azure VNets (even in different regions/subscriptions). Alternative to peering when you need encryption in transit or cross-tenant connectivity.

> **FAQ:** *VPN vs Peering?* Peering = faster, cheaper, no encryption. VPN = encrypted, works cross-tenant, but has bandwidth limits (~1.25 Gbps max).

---

### ExpressRoute

**What:** Private, dedicated connection between your on-prem and Azure that does NOT go over the public internet. Uses a connectivity provider (Equinix, Megaport, AT&T). Much faster and more reliable than VPN.

```
  ┌──────────┐  Private fiber  ┌──────────┐   ┌──────────┐
  │ On-Prem  │════════════════│ Provider │═══│ Azure    │
  │ DC       │ (NOT internet) │ Edge     │   │ ER GW   │
  └──────────┘                └──────────┘   └──────────┘
  
  Bandwidth: 50 Mbps to 100 Gbps
  Latency: Predictable (no internet congestion)
  Cost: $$$ (monthly circuit fee + provider fee)
```

> ⚠️ **Gotcha:** ExpressRoute does NOT encrypt traffic by default (it's private but not encrypted). Add IPSec VPN over ER for encryption if needed.

---

### ExpressRoute Direct

**What:** Connect directly to Microsoft's edge routers (skip the provider). Get 10 Gbps or 100 Gbps port pairs. For ultra-high bandwidth needs.

---

### ExpressRoute Global Reach

**What:** Connect two on-prem sites to each other THROUGH Azure's backbone. Site A (Tokyo) → Azure backbone → Site B (London), without needing your own WAN.

---

### Microsoft Peering

**What:** ExpressRoute peering type for accessing Microsoft 365 and Azure PaaS services (Storage, SQL) over the private connection. Uses public IP ranges advertised by Microsoft.

---

### Private Peering

**What:** ExpressRoute peering type for accessing your Azure VNet resources (VMs, private endpoints). Uses your private IP ranges (10.x.x.x). This is the most common peering type.

```
  ExpressRoute Circuit
  ├── Private Peering → Your VNet resources (10.0.0.0/16)
  └── Microsoft Peering → Microsoft 365, Azure PaaS (public IPs)
```

---

### FastPath

**What:** Bypasses the ExpressRoute gateway for data traffic, sending packets directly to VMs. Reduces latency by eliminating one hop. Only available on Ultra Performance / ErGw3AZ SKU gateways.

> ⚠️ **Gotcha:** FastPath doesn't work with Private Link/Private Endpoints. Traffic to PEs still goes through the gateway.

---

# 5 — Network Security

---

### NSG (Network Security Group)

**What:** A stateful firewall that filters traffic to/from Azure resources using rules based on source/destination IP, port, and protocol. Attached to subnets or individual NICs.

```
  ┌─────────────────────────────────────────────────────┐
  │  NSG Rule (simplified)                              │
  │                                                     │
  │  Priority │ Direction │ Src      │ Dst Port │ Action│
  │  ─────────┼───────────┼──────────┼──────────┼───────│
  │  100      │ Inbound   │ Internet │ 443      │ Allow │
  │  110      │ Inbound   │ Internet │ 80       │ Allow │
  │  200      │ Inbound   │ 10.0.2.0 │ 5432     │ Allow │
  │  65500    │ Inbound   │ Any      │ Any      │ Deny  │
  │  (default, always last)                             │
  └─────────────────────────────────────────────────────┘

  Rules processed in PRIORITY ORDER (lowest number = first).
  First matching rule wins. Default deny at the end.
```

> ⚠️ **Gotcha:** NSGs are stateful — if you allow inbound on port 443, the return traffic is auto-allowed. But NSG on BOTH subnet AND NIC are evaluated (most restrictive wins).

> **FAQ:** *Attach to subnet or NIC?* Subnet-level for broad rules (entire tier). NIC-level for per-VM exceptions. Both are evaluated if both exist.

---

### ASG (Application Security Group)

**What:** Group VMs by role (web servers, DB servers) instead of by IP. Use ASGs in NSG rules to avoid hardcoding IPs.

```
  Instead of: Source 10.0.1.4, 10.0.1.5 → Dest 10.0.2.10 Port 5432
  Use:        Source asg-web-servers    → Dest asg-db-servers Port 5432

  Add a new web VM to asg-web-servers → it automatically gets access.
  No NSG rule changes needed.
```

---

### Effective NSG

**What:** The combined result of ALL NSG rules applied to a NIC (from both subnet NSG and NIC NSG). Use `az network nic show-effective-nsg` or the portal's "Effective security rules" to see what actually applies.

**DevOps example:** "Why can't my VM reach the database?" → Check effective NSG — the subnet NSG allows it but the NIC-level NSG denies it.

---

### Effective Routes

**What:** The combined result of system routes + UDRs + BGP routes for a specific NIC. Shows exactly where traffic to any destination will go.

```bash
az network nic show-effective-route-table --resource-group rg-myapp \
    --name vm-web-nic -o table
```

> ⚠️ **Gotcha:** Always check effective routes before and after adding UDRs. One wrong route can blackhole all traffic.

---

### Azure Firewall

**What:** Managed, stateful firewall-as-a-service. Central point for all network traffic filtering. Supports application rules (FQDN-based), network rules (IP-based), NAT rules, and threat intelligence.

```
  ┌──────────────────────────────────────────────────┐
  │  Azure Firewall                                  │
  │                                                  │
  │  Rule types:                                     │
  │  ├── NAT Rules: DNAT inbound traffic             │
  │  ├── Network Rules: IP + port based (L3/L4)      │
  │  └── Application Rules: FQDN based (L7)          │
  │      e.g., Allow *.github.com on port 443        │
  │                                                  │
  │  Features:                                       │
  │  • Threat intelligence (block known bad IPs)     │
  │  • FQDN tags (e.g., WindowsUpdate, AzureBackup) │
  │  • TLS inspection (Premium SKU)                  │
  │  • IDPS (Intrusion Detection, Premium SKU)       │
  └──────────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Azure Firewall requires a dedicated subnet named `AzureFirewallSubnet` (/26 minimum). Costs ~$912/month (Standard) even with zero traffic.

---

### Firewall Policies

**What:** A reusable collection of firewall rules that can be shared across multiple Azure Firewalls. Supports inheritance — child policy inherits parent rules.

**DevOps example:** Parent policy = company-wide rules (block malware IPs). Child policy per team = team-specific FQDN allowlists.

---

### DNAT (Destination NAT)

**What:** Translates the DESTINATION IP of incoming traffic. Used to expose internal servers via the firewall's public IP.

```
  Internet user connects to Firewall public IP (20.30.40.50:443)
       │
       ▼ DNAT rule translates destination
       │
  Traffic arrives at internal VM (10.0.1.5:443)
```

**Plain English:** "When someone knocks on the front door (public IP), redirect them to the right room (internal IP)."

---

### SNAT (Source NAT)

**What:** Translates the SOURCE IP of outgoing traffic. When a VM accesses the internet, Azure replaces the VM's private IP with a public IP so the response can find its way back.

```
  VM (10.0.1.5) → sends request to google.com
  Azure SNAT: source IP changed to 20.30.40.50 (public)
  Google responds to 20.30.40.50
  Azure translates back to 10.0.1.5
```

---

### SNAT Port Exhaustion

**What:** Each outbound connection uses a unique source port. Azure gives limited SNAT ports per VM (often 1024). Under heavy load (many outbound connections), you run out of ports → connections fail.

```
  Symptoms: Intermittent connection timeouts to external APIs
  
  Fixes:
  1. NAT Gateway (64,000 ports per IP, up to 16 IPs = 1M ports)
  2. Azure Firewall (centralizes SNAT)
  3. Reduce outbound connections (connection pooling, keep-alive)
```

> ⚠️ **Gotcha:** This is a TOP production issue. Monitor SNAT port usage in Azure Monitor. Alert at 80% utilization.

---

### Azure Bastion

**What:** Managed jump box service. RDP/SSH into VMs directly from the Azure portal over TLS — no public IP on the VM needed, no NSG rules for RDP/SSH.

```
  Without Bastion:
  Developer → RDP (port 3389) → Public IP on VM  ← DANGEROUS

  With Bastion:
  Developer → Azure Portal (HTTPS/443) → Bastion → Private IP of VM
  (VM has NO public IP, port 3389 is NOT exposed to internet)
```

> ⚠️ **Gotcha:** Bastion requires a dedicated subnet named `AzureBastionSubnet` (/26 minimum). Basic SKU = ~$140/month per instance.

---

### DDoS Protection

**What:** Defends against volumetric attacks (flooding your public IPs with traffic). Two tiers:

| Tier | What it does | Cost |
|------|-------------|------|
| **DDoS Infrastructure** | Free, default on all Azure services. Basic L3/L4 protection | Free |
| **DDoS Network Protection** | Advanced, per-VNet. Adaptive tuning, real-time metrics, cost guarantee | ~$2,944/month |

> **FAQ:** *Do I need DDoS Network Protection?* Only if you have public-facing services with SLA requirements. The free tier handles most attacks. Premium is for large enterprises.

---

### WAF (Web Application Firewall)

**What:** Protects web apps from OWASP Top 10 attacks (SQL injection, XSS, etc.). Applied at Layer 7 (HTTP/HTTPS). Deployed on Application Gateway, Front Door, or CDN.

```
  Internet → WAF → Application Gateway → App Service
  
  WAF blocks:
  • SQL injection: ' OR 1=1 --
  • XSS: <script>alert('hack')</script>
  • Path traversal: ../../etc/passwd
  • Bot traffic
```

---

### JIT Access (Just-In-Time)

**What:** Temporarily opens VM management ports (RDP/SSH) ONLY when needed, for a limited time, from a specific IP. Part of Microsoft Defender for Cloud.

```
  Normal state: Port 3389 is BLOCKED by NSG
  
  Admin requests JIT access:
  → Approved for 3 hours from IP 203.0.113.5
  → NSG rule auto-added: Allow 203.0.113.5 → port 3389
  → After 3 hours: rule auto-removed
```

**DevOps example:** Instead of leaving RDP open 24/7, developers request JIT access for 2 hours when they need to troubleshoot a VM.

---

# 6 — Load Balancing & Traffic Management

---

### Azure Load Balancer

**What:** Layer 4 (TCP/UDP) load balancer. Distributes traffic across VMs using hash-based algorithm (source IP, port, protocol). Ultra-low latency, millions of flows.

```
  ┌───────────────────────────────────────────┐
  │  Azure Load Balancer (Layer 4)            │
  │                                           │
  │  Frontend IP: 20.30.40.50 (public)        │
  │       │                                   │
  │       ├── VM-1 (10.0.1.5) ← healthy ✓    │
  │       ├── VM-2 (10.0.1.6) ← healthy ✓    │
  │       └── VM-3 (10.0.1.7) ← unhealthy ✗  │
  │                                           │
  │  Health probe removes VM-3 from rotation  │
  └───────────────────────────────────────────┘
```

---

### Application Gateway

**What:** Layer 7 (HTTP/HTTPS) load balancer. Understands URLs, headers, cookies. Can route `/api/*` to backend A and `/web/*` to backend B. Includes WAF.

```
  Internet → App Gateway (L7)
       │
       ├── /api/*    → Backend Pool: API VMs
       ├── /images/* → Backend Pool: CDN/Storage
       └── /*        → Backend Pool: Web VMs
```

---

### Front Door

**What:** Global Layer 7 load balancer + CDN + WAF. Routes users to the CLOSEST healthy backend worldwide. Uses anycast for instant failover.

**DevOps example:** Users in Europe hit your West Europe backend. Users in Asia hit your Southeast Asia backend. If one region goes down, traffic auto-shifts.

> **FAQ:** *App Gateway vs Front Door?* App Gateway = regional (one region). Front Door = global (multi-region). Use Front Door for multi-region apps.

---

### Traffic Manager

**What:** DNS-based traffic distributor. Returns different DNS answers based on routing method (performance, priority, weighted, geographic). Not a proxy — it only resolves DNS.

```
  ┌───────────┬────────────────────────────────────────┐
  │ Method    │ How it works                           │
  ├───────────┼────────────────────────────────────────┤
  │ Priority  │ Primary first, failover to secondary   │
  │ Weighted  │ 80% to backend A, 20% to backend B     │
  │ Performance│ Closest (lowest latency) backend      │
  │ Geographic│ Europe users → EU backend              │
  └───────────┴────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Traffic Manager is DNS-only. It doesn't see or proxy actual traffic. Failover depends on DNS TTL (default 60 seconds = 60s to detect + failover).

---

### Internal Load Balancer

**What:** Load balancer with a PRIVATE frontend IP (10.x.x.x). Only accessible from within your VNet. Used for internal tiers (API, database pools).

---

### Public Load Balancer

**What:** Load balancer with a PUBLIC frontend IP. Internet-facing. Used for web frontends.

---

### Layer 4 Load Balancing

**What:** Routes based on IP address and TCP/UDP port. Cannot read HTTP headers, URLs, or cookies. Fast but dumb. Azure Load Balancer does this.

---

### Layer 7 Load Balancing

**What:** Routes based on HTTP content — URL path, hostname, headers, cookies. Slower but smarter. Application Gateway and Front Door do this.

```
  Layer 4: "Send TCP port 443 traffic to these VMs"
  Layer 7: "Send /api/* to API pool AND /admin/* to Admin pool"
```

---

### Backend Pool

**What:** The group of VMs, VMSS instances, IPs, or App Services that receive traffic from the load balancer. Health probes determine which members are active.

---

### Health Probe

**What:** Periodic checks (HTTP, HTTPS, or TCP) that the load balancer sends to backend pool members. If a member fails the probe, it's removed from rotation until it recovers.

```
  Health probe: GET /health every 15 seconds
  
  VM responds 200 OK → stays in pool
  VM responds 503 or no response → removed from pool
  VM recovers later → automatically re-added
```

> ⚠️ **Gotcha:** Always create a dedicated `/health` endpoint that checks DB connectivity, not just returns 200. A VM that returns 200 but can't reach the DB is useless.

---

### Listener

**What:** An Application Gateway component that listens for incoming connections on a specific IP, port, and protocol. Multi-site listeners handle multiple domains on the same gateway.

**Example:** Listener 1 = `api.myapp.com:443`, Listener 2 = `admin.myapp.com:443`.

---

### Routing Rule

**What:** Connects a listener to a backend pool. "When traffic arrives on THIS listener, send it to THIS backend pool using THIS HTTP settings."

---

### URL Path Routing

**What:** Route traffic to different backend pools based on the URL path (Application Gateway feature).

```
  myapp.com/api/*     → Backend: API servers
  myapp.com/images/*  → Backend: Storage account
  myapp.com/*         → Backend: Web servers (default)
```

---

### Sticky Sessions / Session Affinity

**What:** All requests from the same user go to the SAME backend server. Achieved via cookies. Useful for apps that store session state in server memory.

> ⚠️ **Gotcha:** Sticky sessions break horizontal scaling — if the "sticky" server dies, the user loses their session. Better approach: store sessions in Redis or a database (stateless backends).

---

### Floating IP

**What:** A load balancer setting where the backend VM receives traffic with the load balancer's frontend IP as the destination (not the VM's own IP). Required for SQL AlwaysOn, HA cluster setups.

---

### Direct Server Return (DSR)

**What:** Backend server responds directly to the client, bypassing the load balancer on the return path. Reduces load balancer traffic. Azure's Floating IP enables this.

```
  Request:  Client → LB → VM
  Response: VM → Client (direct, skips LB)
```

---

### SSL Offloading

**What:** The load balancer/gateway terminates TLS (decrypts HTTPS), then forwards plain HTTP to backend servers. Backend servers don't need certificates or TLS processing.

```
  Client ──HTTPS──► App Gateway (decrypts) ──HTTP──► Backend VM
  
  Pro: Backend VMs are simpler (no cert management)
  Con: Traffic between gateway and VMs is unencrypted
```

---

### End-to-End SSL

**What:** TLS encryption ALL the way. The gateway re-encrypts traffic before sending to the backend. Backend servers need their own certificates.

```
  Client ──HTTPS──► App Gateway (decrypts + re-encrypts) ──HTTPS──► Backend VM
  
  Pro: Encrypted everywhere (compliance requirement)
  Con: Backend VMs need certificate management
```

---

### WAF Detection Mode vs Prevention Mode

| Mode | What it does |
|------|-------------|
| **Detection** | Logs malicious requests but ALLOWS them through. Use for testing |
| **Prevention** | Blocks and logs malicious requests. Use for production |

**DevOps example:** Deploy WAF in Detection mode first → review logs for false positives → tune rules → switch to Prevention mode.

---

### NAT Gateway

**What:** Provides a static outbound public IP for all resources in a subnet. Solves SNAT port exhaustion by providing 64,000 ports per public IP.

```
  Without NAT GW:
  VM-1 → Internet (random Azure IP, limited SNAT ports)
  VM-2 → Internet (different random IP, limited ports)

  With NAT GW (assigned to subnet):
  VM-1 → Internet (always 20.30.40.50, 64K ports)
  VM-2 → Internet (always 20.30.40.50, 64K ports)
```

**DevOps example:** Your app calls a third-party API that allowlists IPs. Attach NAT Gateway → all outbound traffic uses the same static IP → give that IP to the vendor.

---

### Static Outbound IP

**What:** A fixed public IP for outbound traffic that doesn't change. Achieved via NAT Gateway, Azure Firewall, or a Public IP on a Load Balancer outbound rule.

---

### Outbound Rules

**What:** Load Balancer rules that define how backend pool members access the internet. Specify which public IP to use and how many SNAT ports each VM gets.

---

### Port Exhaustion

**What:** Running out of available source ports for outbound connections. Happens when too many connections are opened to the same destination without reusing ports.

> ⚠️ **Gotcha:** Common with microservices making many HTTP calls. Fix: connection pooling, `HttpClient` reuse, NAT Gateway, or increase SNAT port allocation.

---

# 7 — Private Connectivity & Network Tools

---

### Service Endpoints

**What:** Extend your VNet identity to Azure PaaS services (Storage, SQL, Key Vault). Traffic stays on Azure backbone instead of going through the public internet. The service STILL has a public IP — you're just optimizing the route.

```
  Without Service Endpoint:
  VM (10.0.1.5) → Internet → Storage (public IP)

  With Service Endpoint:
  VM (10.0.1.5) → Azure backbone → Storage (same public IP, faster path)
```

> ⚠️ **Gotcha:** Service endpoints don't REMOVE public access. Anyone on the internet can still reach the service unless you also add firewall rules ("Allow only from this VNet").

---

### Service Endpoint Policies

**What:** Restrict which specific Azure resources a service endpoint can access. Without policies, a VM with Storage endpoint can reach ANY storage account. With policies, only YOUR storage accounts.

**DevOps example:** Prevent data exfiltration — a compromised VM can only reach `stmyappprod`, not an attacker's storage account.

---

### Private Link

**What:** The underlying technology that enables Private Endpoints. Also lets you expose YOUR OWN services privately to other VNets, subscriptions, or tenants.

```
  Private Link = the platform/framework
  Private Endpoint = a specific instance created using Private Link
```

---

### Private Endpoints

**What:** A NIC with a private IP (10.x.x.x) in YOUR subnet that represents an Azure PaaS service. Traffic goes through the private IP — you can disable all public access.

```
  ┌──────────────────────────────────────────────┐
  │  VNet (10.0.0.0/16)                          │
  │                                              │
  │  snet-app (10.0.1.0/24)                     │
  │  └── App Service (uses managed identity)     │
  │                                              │
  │  snet-pe (10.0.5.0/24)                      │
  │  ├── PE for SQL (10.0.5.4)                  │
  │  ├── PE for Key Vault (10.0.5.5)            │
  │  └── PE for Storage (10.0.5.6)              │
  │                                              │
  │  App → 10.0.5.4 (SQL, never leaves VNet)    │
  │  Public access to SQL: DISABLED              │
  └──────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Private Endpoints require Private DNS Zones for name resolution. Without them, the FQDN still resolves to the public IP and traffic fails.

---

### Private Endpoint NIC

**What:** The actual virtual network interface card created for a Private Endpoint. Has a private IP from your subnet. You can see it in the portal under the PE resource.

---

### Private Link Service

**What:** Expose YOUR application behind a Standard Load Balancer as a Private Link. Consumers in other VNets/tenants create Private Endpoints to YOUR service — traffic stays private.

```
  Provider VNet:                    Consumer VNet:
  ┌──────────────────┐              ┌──────────────────┐
  │ Standard LB      │              │                  │
  │ ├── VM-1         │              │ Private Endpoint │
  │ └── VM-2         │◄═════════════│ (10.1.5.4)       │
  │ Private Link Svc │  Private Link│                  │
  └──────────────────┘              └──────────────────┘
  
  Consumer never sees provider's VNet. Fully isolated.
```

---

### Network Watcher

**What:** Azure's network diagnostic and monitoring toolkit. A collection of tools for troubleshooting connectivity, inspecting routes, capturing packets, and analyzing flow logs.

---

### IP Flow Verify

**What:** Tests whether a specific packet (source IP, dest IP, port, protocol) would be ALLOWED or DENIED by NSG rules. Tells you WHICH rule blocked/allowed it.

```bash
az network watcher test-ip-flow --vm vm-web \
    --direction Inbound --protocol TCP \
    --local 10.0.1.5:80 --remote 203.0.113.10:50000
# Output: "Access allowed" or "Access denied by rule: DenyAllInbound"
```

**DevOps example:** "Why can't my app reach the database?" → Run IP Flow Verify → "Denied by NSG rule Priority 200: DenySQL".

---

### Next Hop

**What:** Shows where traffic from a VM to a specific destination will be routed. Reveals if traffic goes to the Internet, VPN Gateway, NVA, or is blackholed.

```bash
az network watcher show-next-hop --vm vm-web \
    --dest-ip 8.8.8.8 --source-ip 10.0.1.5
# Output: "Next hop: 10.0.4.4 (VirtualAppliance)" ← through firewall
```

---

### Connection Troubleshoot

**What:** Tests end-to-end connectivity from a VM to a destination (IP or FQDN). Checks NSGs, routing, DNS, and port availability in one shot.

---

### NSG Flow Logs

**What:** Records all traffic that passes through an NSG — source/dest IP, port, protocol, allowed/denied. Stored in a Storage Account. Essential for security auditing and troubleshooting.

```
  Flow log entry:
  Timestamp: 2026-05-12T10:30:15Z
  Source: 203.0.113.10:54321
  Dest: 10.0.1.5:443
  Protocol: TCP
  Action: ALLOWED
  Direction: Inbound
```

> ⚠️ **Gotcha:** Flow logs generate significant data. Enable only on critical NSGs and set retention policies. Use Traffic Analytics to summarize instead of reading raw logs.

---

### Traffic Analytics

**What:** Processes NSG flow logs and provides visual dashboards — top talkers, blocked traffic patterns, geo-distribution of connections, anomaly detection. Built on Log Analytics.

**DevOps example:** Dashboard shows 10,000 blocked connection attempts from a suspicious IP range → investigate potential attack.

---

### Packet Capture

**What:** Captures actual network packets on a VM for deep analysis. Like running `tcpdump` but managed through Azure. Download the capture file and analyze in Wireshark.

**DevOps example:** App intermittently times out. Packet capture reveals TCP retransmissions due to MTU mismatch between VM and NVA.

---

# 8 — Compute

---

### Virtual Machines (VMs)

**What:** IaaS — you get a full virtual server (OS, CPU, RAM, disk). You manage patching, security, and runtime. Most control, most responsibility.

```
  ┌─────────────────────────────────────────┐
  │ VM Responsibility Model                 │
  │                                         │
  │ You manage:   OS, patches, runtime,     │
  │               app, security, scaling    │
  │ Azure manages: hardware, hypervisor,    │
  │               network, datacenter       │
  └─────────────────────────────────────────┘
```

---

### VMSS (Virtual Machine Scale Sets)

**What:** A group of identical VMs that auto-scales based on demand. All VMs use the same image and configuration. The load balancer distributes traffic.

```
  Low traffic:  2 VMs running
  Spike:        VMSS scales to 10 VMs (auto)
  Traffic drops: VMSS scales back to 2 VMs

  All VMs are identical (same image, same config).
  You never manually create individual VMs.
```

**DevOps example:** Your web tier uses VMSS. CPU > 70% → scale out. CPU < 30% → scale in.

---

### Availability Set (compute context)

**What:** Group VMs across fault domains (racks) and update domains. Ensures not all VMs go down during a rack failure or planned maintenance. Configured at VM creation time — can't add later.

---

### Ephemeral OS Disk

**What:** Uses the VM's local/temporary SSD for the OS disk instead of managed disk. Faster boot, no storage cost, but ALL data is lost on VM redeployment/resize.

**Best for:** Stateless workloads (web servers, VMSS) where the OS disk is rebuilt from an image every time.

> ⚠️ **Gotcha:** No data persistence. If you stop/deallocate or resize the VM, the OS disk is wiped. Only use for stateless VMs.

---

### Managed Disks

**What:** Azure-managed virtual hard drives. You don't manage storage accounts — Azure handles replication, encryption, and availability.

```
  ┌────────────┬──────────┬──────────┬─────────────┐
  │ Disk type  │ IOPS     │ $/month  │ Use case    │
  ├────────────┼──────────┼──────────┼─────────────┤
  │ Standard HDD│ 500     │ ~$2      │ Dev/test    │
  │ Standard SSD│ 500     │ ~$4      │ Light prod  │
  │ Premium SSD │ 5,000   │ ~$20     │ Production  │
  │ Ultra Disk  │ 160,000 │ ~$100+   │ SAP, DB, HPC│
  └────────────┴──────────┴──────────┴─────────────┘
```

> ⚠️ **Gotcha:** VM SLA (99.9%) requires Premium SSD or Ultra Disk. Standard HDD gives NO SLA.

---

### Boot Diagnostics

**What:** Captures VM console output and screenshots during boot. Helps debug VMs that won't start (stuck on GRUB, blue screen, etc.). Stored in a storage account.

---

### Autoscaling

**What:** Automatically add/remove VM instances based on metrics (CPU, memory, queue depth, schedule). Available for VMSS, App Service, AKS, Container Apps.

```
  Autoscale rule:
  IF average CPU > 70% for 5 minutes → add 2 instances
  IF average CPU < 30% for 10 minutes → remove 1 instance
  Min: 2 instances, Max: 20 instances
```

> ⚠️ **Gotcha:** Always set a MIN instance count ≥ 2 for production. Set a MAX to prevent cost explosions. Add cooldown periods to avoid rapid scale flapping.

---

### Rolling Upgrades

**What:** Update VMSS instances one batch at a time. While batch 1 is being updated, batches 2-5 continue serving traffic. If an update fails, it stops and rolls back.

---

### Hotpatching

**What:** Apply security patches to VMs WITHOUT rebooting. The VM stays online and serving traffic. Available for Windows Server 2022 Azure Edition.

---

### Azure Compute Gallery (formerly Shared Image Gallery)

**What:** Store and share custom VM images across subscriptions and regions. Version images, set replication targets, and manage lifecycle.

---

### Golden Images

**What:** A pre-configured, hardened, fully-baked VM image used as a base for all deployments. Includes OS, patches, agents, security configs, and runtime dependencies.

```
  Golden Image Pipeline:
  Base OS → Install patches → Install agents (monitoring, AV)
  → Harden (disable unused services, CIS benchmarks)
  → Bake with Packer → Store in Compute Gallery
  → VMSS uses this image for all new instances
```

---

### Image Versioning

**What:** Each golden image gets a version (1.0.0, 1.1.0, 2.0.0). VMSS can pin to a specific version or auto-update to the latest. Roll back by pointing to a previous version.

---

### Packer

**What:** HashiCorp tool that automates VM image creation. Define a template → Packer spins up a temporary VM → runs your provisioning scripts → captures the disk as an image → deletes the VM.

```bash
# Packer builds a golden image:
packer build azure-image.pkr.hcl

# Result: Managed image in Azure Compute Gallery
# VMSS uses this image for all new instances
```

---

### Azure Bastion (compute context)

**What:** Secure RDP/SSH access to VMs through the Azure portal. No public IP needed on VMs. See Batch 5 for full details.

---

### Azure Update Manager

**What:** Centralized patch management for VMs at scale. Assess, schedule, and deploy OS updates across Windows and Linux VMs. Replaces the older Update Management solution.

---

### Maintenance Configurations

**What:** Define maintenance windows for Azure to apply platform updates (host OS patches, hardware updates). Prevent unplanned reboots during business hours.

---

### Patch Management

**What:** The process of keeping VMs up to date with security patches. Azure Update Manager automates this — assess what's missing, schedule install windows, report compliance.

---

### App Service

**What:** PaaS for web apps and APIs. Deploy code (or containers) without managing VMs. Azure handles OS patching, scaling, load balancing, and TLS.

```
  IaaS (VM):      You manage EVERYTHING above hardware
  PaaS (App Svc): You manage code only. Azure manages the rest.
  
  Supports: .NET, Java, Node.js, Python, PHP, Ruby, Go, containers
```

---

### App Service Plan

**What:** The underlying VM(s) that host your App Services. Defines CPU, RAM, and pricing tier. Multiple apps can share one plan (but share resources).

```
  ┌──────────┬──────┬──────┬──────────────────────────┐
  │ Tier     │ CPU  │ RAM  │ Features                 │
  ├──────────┼──────┼──────┼──────────────────────────┤
  │ Free/F1  │ Shared│ 1GB │ Dev only, no SLA         │
  │ Basic/B1 │ 1    │ 1.75│ Custom domain, no scale  │
  │ Std/S1   │ 1    │ 1.75│ Auto-scale, slots, VNet  │
  │ Prem/P1v3│ 2    │ 8   │ Zone-redundant, more perf│
  └──────────┴──────┴──────┴──────────────────────────┘
```

---

### ARR Affinity

**What:** Application Request Routing — sticky sessions for App Service. A cookie pins a user to a specific instance. Disable for stateless apps (recommended).

---

### Deployment Slots

**What:** Separate environments (staging, QA) within the same App Service. Deploy to staging → test → swap staging ↔ production (instant, zero downtime). Swap back if problems occur.

---

### Function Apps

**What:** Serverless compute — run small pieces of code (functions) triggered by events (HTTP, timer, queue, blob). Pay per execution on Consumption plan. Scale to zero.

```
  Event happens → Function runs → Pay for that execution → Done
  No event = no cost (scale to zero)
```

---

### Logic Apps

**What:** Visual workflow automation. Drag-and-drop connectors to integrate services (receive email → create Jira ticket → notify Teams). Low-code/no-code. 400+ connectors.

**DevOps example:** When Azure Monitor fires an alert → Logic App creates a PagerDuty incident → posts to Slack → assigns on-call engineer.

---

# 9 — Containers & Kubernetes

---

### Container Apps

**What:** Serverless container platform. Run containers with built-in auto-scaling (including scale-to-zero), traffic splitting, and Dapr. No K8s knowledge needed.

```
  ACI       = single container, no orchestration
  Cont Apps = managed microservices platform (K8s underneath)
  AKS       = full Kubernetes, you manage it
```

---

### Azure Container Registry (ACR)

**What:** Private Docker registry in Azure. Store, build, scan, and distribute container images. Use managed identity to pull (never admin credentials).

---

### Azure Container Instances (ACI)

**What:** Run a container without managing any infrastructure. Spin up in seconds, pay per second. No scaling, no load balancing — for simple, one-off tasks.

**DevOps example:** Run a nightly data migration script in ACI with `--restart-policy Never`. Container runs, exits, costs $0.03.

---

### AKS (Azure Kubernetes Service)

**What:** Managed Kubernetes. Azure manages the control plane (API server, etcd, scheduler) for free. You manage and pay for the worker nodes.

```
  ┌──────────────────────────────────────────────┐
  │  AKS Cluster                                 │
  │                                              │
  │  Control Plane (FREE, Azure-managed):        │
  │  ├── API Server                              │
  │  ├── etcd (cluster state DB)                 │
  │  ├── Scheduler                               │
  │  └── Controller Manager                      │
  │                                              │
  │  Worker Nodes (YOU pay):                     │
  │  ├── Node Pool "system" (3× Standard_D2s)   │
  │  └── Node Pool "user"   (5× Standard_D4s)   │
  │      └── Your Pods run here                  │
  └──────────────────────────────────────────────┘
```

---

### Kubernetes Control Plane

**What:** The brain of Kubernetes. API Server handles all requests. Scheduler places pods on nodes. etcd stores all cluster state. In AKS, Microsoft manages this — you never SSH into it.

---

### Node Pools

**What:** Groups of VMs (nodes) with the same size and config. System node pool runs K8s services (CoreDNS, metrics). User node pools run your apps. Can have different VM sizes per pool.

**DevOps example:** Node pool "gpu" with GPU VMs for ML workloads. Node pool "general" with standard VMs for APIs.

---

### Pods

**What:** The smallest deployable unit in K8s. One or more containers sharing network (localhost) and storage. Usually 1 container per pod. Pods are ephemeral — they come and go.

---

### Services (K8s)

**What:** A stable network endpoint for a group of pods. Pods get random IPs that change on restart. A Service provides a fixed IP/DNS name that load-balances across healthy pods.

```
  ┌──────────────────────────┐
  │ Service: myapi-svc       │
  │ ClusterIP: 10.96.0.15   │
  │    │                     │
  │    ├── Pod-1 (10.244.0.5)│
  │    ├── Pod-2 (10.244.1.3)│
  │    └── Pod-3 (10.244.2.7)│
  └──────────────────────────┘
  
  Types:
  ClusterIP  = internal only (default)
  NodePort   = exposes on each node's IP
  LoadBalancer = creates Azure LB with public IP
```

---

### Ingress

**What:** Layer 7 routing for K8s. Maps external URLs to internal Services. One entry point for multiple services.

```
  myapp.com/api/*    → Service: api-svc
  myapp.com/web/*    → Service: web-svc
  myapp.com/admin/*  → Service: admin-svc
```

---

### Ingress Controller

**What:** The actual software that implements Ingress rules. NGINX Ingress Controller is most common. It runs as pods inside your cluster and acts as a reverse proxy.

---

### AGIC (Application Gateway Ingress Controller)

**What:** Uses Azure Application Gateway as the ingress controller for AKS. The App Gateway lives OUTSIDE the cluster, providing WAF + SSL + L7 routing.

> **FAQ:** *NGINX vs AGIC?* NGINX = runs inside cluster, more flexible. AGIC = Azure-native, includes WAF, better for compliance.

---

### Kubenet

**What:** Basic K8s networking. Pods get IPs from a separate CIDR (not from VNet). Requires UDRs for pod-to-pod traffic across nodes. Simpler but limited.

---

### Azure CNI

**What:** Each pod gets an IP directly from the VNet subnet. Pods are first-class VNet citizens — reachable by VMs, other VNets, and on-prem. Uses more IPs.

```
  Kubenet:    Node gets VNet IP, pods get separate IPs (NAT'd)
  Azure CNI:  Every pod gets a VNet IP directly (10.0.x.x)
```

> ⚠️ **Gotcha:** Azure CNI consumes IPs fast. A node with 30 pods needs 31 IPs (1 node + 30 pods). Plan subnet sizes carefully (/21 or larger).

---

### Overlay Networking

**What:** Azure CNI Overlay — pods get IPs from a private overlay network, not the VNet. Saves VNet IPs while keeping CNI benefits. Best of both worlds.

---

### HPA (Horizontal Pod Autoscaler)

**What:** Auto-scales the NUMBER of pods based on CPU, memory, or custom metrics. More traffic → more pods. Less traffic → fewer pods.

```yaml
# Scale between 2-20 replicas based on CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

---

### Cluster Autoscaler

**What:** Auto-scales the NUMBER of NODES (VMs). If pods can't be scheduled because nodes are full, Cluster Autoscaler adds nodes. If nodes are underutilized, it removes them.

```
  HPA scales PODS:     2 pods → 20 pods (needs more node capacity)
  Cluster Autoscaler:  3 nodes → 8 nodes (to fit the 20 pods)
```

---

### Taints & Tolerations

**What:** Taints on nodes REPEL pods. Only pods with matching Tolerations can be scheduled there. Used to reserve nodes for specific workloads.

**DevOps example:** Taint GPU nodes → only ML pods with the right toleration land there. Regular API pods go to standard nodes.

---

### CSI Driver (Container Storage Interface)

**What:** Standard plugin interface for attaching storage to pods. Azure provides CSI drivers for Managed Disks, Azure Files, and Blob Storage.

---

### Network Policies

**What:** Firewall rules for pod-to-pod traffic INSIDE the cluster. By default, all pods can talk to all pods. Network policies restrict this.

```yaml
# Only allow traffic from frontend pods to api pods
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
spec:
  podSelector:
    matchLabels: { app: api }
  ingress:
  - from:
    - podSelector:
        matchLabels: { app: frontend }
```

---

### Service Mesh

**What:** Infrastructure layer for service-to-service communication. Handles mTLS, retries, circuit breaking, observability. Istio and Linkerd are common. Implemented via sidecar proxies.

---

### Sidecar Pattern

**What:** A helper container running alongside your main container in the same pod. Handles cross-cutting concerns (logging, proxying, TLS) without modifying your app code.

```
  Pod:
  ├── Main Container (your API)
  └── Sidecar Container (Envoy proxy — handles mTLS, retries)
```

---

### Workload Identity

**What:** Maps a K8s ServiceAccount to an Entra ID managed identity. Pods authenticate to Azure services (Key Vault, SQL) using federated tokens — no secrets.

> Replaces deprecated "Pod Identity". Use Workload Identity for all new AKS deployments.

---

### Secrets Store CSI (+ Pod Identity)

**What:** Mounts Key Vault secrets directly into pods as files or env vars. Pods read secrets from `/mnt/secrets/db-password` — no code changes needed.

---

### Helm Charts

**What:** Package manager for Kubernetes. A Helm chart bundles all K8s manifests (Deployment, Service, ConfigMap) into a versioned, parameterized package.

```bash
helm install myapp ./myapp-chart --set image.tag=v2.0.0
helm upgrade myapp ./myapp-chart --set replicas=5
helm rollback myapp 1  # rollback to previous version
```

---

### GitOps (FluxCD / ArgoCD)

**What:** Git is the single source of truth for cluster state. Push changes to Git → GitOps agent (Flux/Argo) auto-applies them to the cluster. No `kubectl apply` needed.

```
  Developer pushes YAML → Git repo
       │
       ▼
  FluxCD/ArgoCD watches repo
       │
       ▼
  Auto-applies changes to AKS cluster
  
  Drift detected? Agent auto-reconciles to match Git.
```

> **FAQ:** *Helm vs GitOps?* Not either/or. Use Helm to package charts. Use GitOps to deploy them from Git automatically.

---

# 10 — Storage & Databases

---

### Storage Accounts

**What:** Top-level container for all Azure storage services (Blob, Files, Queue, Table). Each account has a unique name (globally), a redundancy setting, and access tier.

---

### GPv2 (General Purpose v2)

**What:** The recommended storage account type. Supports all storage services and all access tiers. GPv1 is legacy — always choose GPv2 for new deployments.

---

### Blob Storage

**What:** Object storage for unstructured data — files, images, videos, backups, logs. Organized in containers (like folders). Three blob types:

| Type | Use case |
|------|----------|
| **Block blob** | Files, images, backups (most common) |
| **Append blob** | Log files (append-only, no overwrites) |
| **Page blob** | VM disks (random read/write) |

---

### Azure Files

**What:** Fully managed SMB/NFS file shares in the cloud. Mount as a network drive on Windows (`Z:\`) or Linux (`/mnt/share`). Replaces on-prem file servers.

**DevOps example:** Legacy app requires a shared file system → mount Azure Files share to all App Service instances.

---

### Azure File Sync

**What:** Syncs on-prem file servers with Azure Files. Frequently used files cached locally, rarely used files tiered to cloud. Access all files as if they're local.

---

### Queue Storage

**What:** Simple message queue for decoupling components. Producer adds messages, consumer reads and deletes them. Max message size: 64 KB. For simple scenarios — use Service Bus for advanced features.

---

### Table Storage

**What:** NoSQL key-value store. Cheap, fast, simple. Good for logs, user settings, device telemetry. Schema-less — each row can have different columns.

---

### SMB (Server Message Block)

**What:** Windows file sharing protocol. Azure Files supports SMB 2.1 and 3.0. SMB 3.0 supports encryption in transit.

---

### NFS (Network File System)

**What:** Linux file sharing protocol. Azure Files supports NFS 4.1 for Premium tier. Requires VNet — no public access for NFS.

> ⚠️ **Gotcha:** NFS shares are Premium tier only and require a VNet. SMB is available on all tiers.

---

### SMB Multichannel

**What:** Uses multiple network connections in parallel for higher throughput to Azure Files. Available on Premium SMB shares. Can 3-4× throughput.

---

### Redundancy (LRS / ZRS / GRS / RA-GRS / GZRS)

```
  ┌────────┬──────────────────────────────────┬────────────┐
  │ Type   │ How it works                     │ Copies     │
  ├────────┼──────────────────────────────────┼────────────┤
  │ LRS    │ 3 copies in 1 datacenter         │ 3          │
  │ ZRS    │ 3 copies across 3 zones          │ 3          │
  │ GRS    │ LRS + async copy to paired region│ 6 (3+3)    │
  │ RA-GRS │ GRS + read from secondary        │ 6 (3+3)    │
  │ GZRS   │ ZRS + async copy to paired region│ 6 (3+3)    │
  └────────┴──────────────────────────────────┴────────────┘
  
  Cost:  LRS < ZRS < GRS < RA-GRS < GZRS
  Safety: LRS < ZRS < GRS < RA-GRS < GZRS
```

---

### Access Tiers (Hot / Cool / Cold / Archive)

```
  ┌──────────┬─────────────────┬───────────┬──────────────┐
  │ Tier     │ Access cost     │ Storage $ │ Retrieval    │
  ├──────────┼─────────────────┼───────────┼──────────────┤
  │ Hot      │ Cheapest access │ Highest   │ Instant      │
  │ Cool     │ Higher access   │ 44% lower │ Instant      │
  │ Cold     │ Higher access   │ 75% lower │ Instant      │
  │ Archive  │ Very expensive  │ 95% lower │ Hours (rehydrate)│
  └──────────┴─────────────────┴───────────┴──────────────┘
```

> ⚠️ **Gotcha:** Archive tier data takes HOURS to read (must rehydrate first). Cool has 30-day minimum hold, Cold has 90-day, Archive has 180-day — early deletion fees apply.

---

### SAS Tokens (Shared Access Signatures)

**What:** Signed URLs that grant scoped, time-limited access to storage resources. No need to share account keys.

```
  https://stmyapp.blob.core.windows.net/uploads/file.pdf
    ?sv=2023-01-01
    &st=2026-05-14T08:00:00Z     ← start time
    &se=2026-05-14T09:00:00Z     ← expiry (1 hour)
    &sp=r                         ← permissions (read only)
    &sig=abc123...                ← signature (tamper-proof)
```

> ⚠️ **Gotcha:** SAS tokens can't be revoked individually. If leaked, rotate the storage account key that signed it (breaks ALL SAS signed with that key). Use stored access policies for revocability.

---

### Access Keys

**What:** Two master keys per storage account. Full access to everything. Never share them — use managed identity or SAS instead. Rotate regularly.

---

### Immutable Blob (WORM)

**What:** Write Once, Read Many. Once data is written, it cannot be modified or deleted for a retention period. For legal/compliance requirements (SEC, HIPAA).

---

### Soft Delete

**What:** Deleted blobs/containers are recoverable for a retention period (1-365 days). Protects against accidental deletion. Enable for all production accounts.

---

### CMK / PMK / Double Encryption

| Term | What |
|------|------|
| **PMK** (Platform Managed Key) | Microsoft manages the encryption key. Default. Zero effort |
| **CMK** (Customer Managed Key) | You bring your own key (stored in Key Vault). More control |
| **Double Encryption** | Two layers: infrastructure encryption (PMK) + service encryption (CMK) |

---

### Disk Encryption Sets

**What:** Link a CMK from Key Vault to managed disks. All VMs using that disk encryption set have their OS/data disks encrypted with your key.

---

### Lifecycle Management Policy

**What:** Automate tier transitions and deletion based on age. Set rules like "move to Cool after 30 days, Archive after 90, delete after 365."

---

### Azure SQL Database

**What:** Managed relational database (SQL Server engine). Azure handles patching, backups (auto every 5-min), HA, and replication. You manage schema and queries.

```
  ┌──────────────┬──────────────────────────────────────┐
  │ Model        │ Details                              │
  ├──────────────┼──────────────────────────────────────┤
  │ DTU          │ Bundled CPU+IO+memory. Simple pricing│
  │ vCore        │ Choose cores, memory independently.  │
  │              │ Supports serverless + Hyperscale     │
  │ Serverless   │ Auto-pause when idle (saves $$$)     │
  │ Hyperscale   │ Up to 100 TB, fast scaling           │
  └──────────────┴──────────────────────────────────────┘
```

---

### DTU vs vCore

**What:** DTU = simple, bundled. vCore = flexible, independent scaling of CPU/memory. vCore supports reserved instances (up to 55% savings).

> **FAQ:** *Which to choose?* DTU for small/simple workloads. vCore for production (more flexibility, better cost optimization).

---

### Managed Instance

**What:** Near 100% SQL Server compatibility in a managed service. Supports features missing from Azure SQL Database: SQL Agent, cross-database queries, CLR. Deployed in YOUR VNet.

---

### Elastic Pool

**What:** Multiple databases sharing a pool of DTUs/vCores. Databases with varying usage patterns share resources — when DB-A is idle, DB-B can use those resources.

**DevOps example:** SaaS app with 50 tenant databases. Each tenant is small but spikes at different times. One elastic pool serves all 50 cheaply.

---

### Cosmos DB

**What:** Globally distributed, multi-model NoSQL database. Single-digit millisecond latency worldwide. Supports document (JSON), key-value, graph, column-family APIs.

---

### Consistency Levels

**What:** Cosmos DB offers 5 levels — trade consistency for latency/throughput:

```
  Strong ← Bounded Staleness ← Session ← Consistent Prefix ← Eventual
  (slowest, safest)                                    (fastest, weakest)
  
  Session = default. Reads within a session always see your own writes.
  Strong  = all regions see same data at same time (expensive).
  Eventual = fastest, but you might read stale data briefly.
```

---

### RU/s (Request Units)

**What:** Cosmos DB's throughput currency. A single 1KB point read = 1 RU. Complex queries cost more. Provision RU/s per container or use autoscale.

> ⚠️ **Gotcha:** If you exceed provisioned RU/s, requests get 429 (throttled). Monitor RU consumption and set autoscale.

---

### Partitioning (Cosmos DB)

**What:** Data is distributed across partitions based on a partition key. Good key = even distribution. Bad key = hot partitions (all traffic hits one partition).

```
  Good keys:  userId, tenantId, deviceId  (high cardinality)
  Bad keys:   status, country, category   (few distinct values)
  
  ⚠️ Partition key CANNOT be changed after creation!
```

---

### PostgreSQL Flexible Server

**What:** Managed PostgreSQL with zone-redundant HA, configurable maintenance windows, and burstable/general/memory-optimized tiers. Recommended for all new PostgreSQL workloads.

---

### MySQL Flexible Server

**What:** Same concept as PostgreSQL Flexible Server but for MySQL. Zone-redundant, configurable, supports stop/start to save costs in dev environments.

---

# 11 — Azure Virtual Desktop (AVD)

---

### Azure Virtual Desktop (AVD)

**What:** Cloud-based desktop and app virtualization. Users access a full Windows desktop or individual apps from any device (laptop, tablet, thin client). Microsoft manages the broker, gateway, and web access — you manage the VMs (session hosts).

```
  ┌──────────────────────────────────────────────────────┐
  │  AVD Architecture                                    │
  │                                                      │
  │  User → AVD Gateway (Microsoft-managed) → Reverse    │
  │         Connect → Session Host VM (your VNet)        │
  │                                                      │
  │  Microsoft manages:  Gateway, Broker, Web Access,    │
  │                      Diagnostics, Feed              │
  │  You manage:         Session Host VMs, Networking,   │
  │                      Image, FSLogix, Identity       │
  └──────────────────────────────────────────────────────┘
```

---

### Host Pools

**What:** A collection of session host VMs that serve the same purpose. Two types:

| Type | How it works |
|------|-------------|
| **Pooled** | Multiple users share VMs. Cheaper. Users get a random VM each session |
| **Personal** | Each user is assigned their OWN dedicated VM. Persistent desktop. More expensive |

**DevOps example:** Call center agents → Pooled (100 agents, 30 VMs). Developers → Personal (each gets their own VM with custom tools).

---

### Session Hosts

**What:** The actual VMs that users connect to. Run Windows 10/11 multi-session or Windows Server. You choose the VM size, image, and how many to deploy.

> ⚠️ **Gotcha:** Windows 10/11 multi-session is ONLY available in Azure (not on-prem). It allows multiple users on a single Windows client OS — unique to AVD.

---

### App Groups

**What:** Define what users can access from a host pool. Two types:

| Type | What user sees |
|------|---------------|
| **Desktop** | Full Windows desktop (Start menu, taskbar, everything) |
| **RemoteApp** | Individual apps appear as local windows (no desktop visible) |

A host pool can have ONE Desktop app group and MANY RemoteApp app groups.

---

### Workspaces

**What:** A logical grouping of app groups shown to users in their AVD feed. Users see "Work Apps" workspace containing Excel, Outlook, SAP RemoteApps.

---

### Feed Discovery

**What:** The process by which a user's AVD client discovers available desktops and apps. User signs in → client queries `https://rdweb.wvd.microsoft.com/api/arm/feeddiscovery` → gets list of workspaces and apps.

---

### AVD Broker

**What:** Microsoft-managed service that handles user connections. Decides WHICH session host a user connects to based on load balancing settings. You never manage this.

---

### AVD Gateway

**What:** Microsoft-managed reverse proxy that tunnels RDP traffic over HTTPS (port 443). Users don't need direct network access to session hosts — all traffic goes through the gateway.

---

### Reverse Connect

**What:** Session hosts make OUTBOUND connections to the AVD Gateway. No inbound ports need to be opened on your VMs/NSGs. This is the key security feature of AVD.

```
  Traditional RDP: User → port 3389 → VM  (inbound, risky!)
  AVD Reverse Connect: VM → outbound HTTPS → Gateway ← User
  (No inbound ports. Firewall-friendly.)
```

---

### RemoteApps

**What:** Individual applications streamed to the user's device. The app looks like a local window — users don't see the full remote desktop. Ideal for specific LOB apps.

**DevOps example:** Accounting team needs SAP. Publish SAP as a RemoteApp → it appears in their Start menu alongside local apps.

---

### Desktop App Group

**What:** Gives users a full Windows desktop experience. They see a full screen with Start menu, taskbar, desktop icons. Only ONE desktop app group per host pool.

---

### FSLogix

**What:** Microsoft's profile management solution for AVD. Stores user profiles (Desktop, Documents, AppData, browser cache) in VHD containers on Azure Files. Profiles follow users across session hosts.

```
  Without FSLogix:
  User logs into VM-A → customizes desktop → logs out
  User logs into VM-B next day → clean desktop (no profile!)

  With FSLogix:
  User logs into ANY VM → FSLogix mounts their profile VHD
  → Same desktop, same files, same settings. Seamless.
```

---

### Profile Containers

**What:** FSLogix VHD(x) files that contain the user's ENTIRE profile (Desktop, Documents, AppData, registry). Mounted at login, detached at logout. Stored on Azure Files or NetApp Files.

---

### Office Containers

**What:** Separate FSLogix container specifically for Microsoft 365 cache data (Outlook OST, Teams cache, OneDrive). Keeps Office data separate from the main profile for better performance.

> **FAQ:** *Profile Container vs Office Container?* Use both. Profile = user settings. Office = M365 cache. Separating them means you can manage sizes independently.

---

### Breadth-First Load Balancing

**What:** Spreads users evenly across ALL available session hosts. VM-1 gets user 1, VM-2 gets user 2, VM-3 gets user 3, then back to VM-1.

**Best for:** Consistent performance. No single VM gets overloaded.

---

### Depth-First Load Balancing

**What:** Fills one session host to its max user limit before moving to the next. VM-1 gets 10 users, then VM-2 gets next 10.

**Best for:** Cost savings. Fewer VMs running at any time — unused VMs can be deallocated.

```
  Breadth-first: VM-1(3) VM-2(3) VM-3(3) → all used equally
  Depth-first:   VM-1(9) VM-2(0) VM-3(0) → VM-2,3 can be shut down
```

---

### Drain Mode

**What:** Prevents NEW user sessions from connecting to a session host. Existing sessions continue until users log off. Used for maintenance — drain users before patching/rebooting.

**DevOps example:** Enable drain mode on VM-1 → wait for all users to log off → patch VM-1 → disable drain mode → VM-1 accepts new users again.

---

### Start VM on Connect

**What:** Deallocated VMs automatically start when a user tries to connect. Saves costs by keeping VMs off during non-business hours. User waits ~1-2 minutes for VM to boot.

> ⚠️ **Gotcha:** Only works with Personal host pools or Pooled with depth-first. Users experience a cold-start delay.

---

### Entra Join (AVD context)

**What:** Session hosts joined directly to Entra ID (cloud-only). No on-prem AD needed. Simplest setup for cloud-native organizations.

---

### Hybrid Join (AVD context)

**What:** Session hosts joined to BOTH on-prem AD DS and Entra ID. Required when users need access to on-prem file shares, printers, or Kerberos-authenticated apps.

```
  Cloud-only org → Entra Join
  Hybrid org (on-prem AD + cloud) → Hybrid Join
  Need Kerberos for Azure Files → Cloud Kerberos Trust
```

---

# 12 — Monitoring & KQL

---

### Azure Monitor

**What:** The umbrella platform for ALL monitoring in Azure. Collects metrics and logs from every Azure resource. Feeds into Log Analytics, App Insights, Alerts, and dashboards.

```
  ┌──────────────────────────────────────────────────┐
  │  Azure Monitor                                   │
  │                                                  │
  │  Sources:  VMs, App Service, AKS, SQL, custom    │
  │     │                                            │
  │     ├── Metrics → real-time numbers (CPU, RAM)   │
  │     │             stored 93 days, 1-min granular │
  │     │                                            │
  │     └── Logs → text records (events, traces)     │
  │               sent to Log Analytics Workspace    │
  │               queried with KQL                   │
  │                                                  │
  │  Outputs: Alerts, Dashboards, Workbooks, Grafana │
  └──────────────────────────────────────────────────┘
```

---

### Metrics

**What:** Numerical time-series data. CPU %, memory %, disk IOPS, request count. Lightweight, near real-time (~1 min). Stored for 93 days automatically. Best for dashboards and quick alerts.

---

### Logs

**What:** Rich, structured text records. Application traces, audit logs, diagnostic events. Sent to Log Analytics Workspace. Queried with KQL. Can retain for years.

---

### Alerts

**What:** Automated notifications when a condition is met. "If CPU > 90% for 5 minutes, fire an alert." Triggers an Action Group.

```
  Alert types:
  • Metric alert: CPU > 80% (checks every 1 min)
  • Log alert: KQL query returns > 0 results
  • Activity Log alert: someone deleted a resource
  • Smart Detection: App Insights detects anomaly
```

---

### Action Groups

**What:** Define WHO gets notified and HOW when an alert fires. Can email, SMS, call a webhook, trigger a Logic App, create an ITSM ticket, or run an Azure Function.

---

### Dynamic Threshold Alerts

**What:** Azure Monitor uses ML to learn your resource's normal baseline. Alerts fire when values deviate from the LEARNED pattern instead of a static number.

**DevOps example:** CPU normally runs at 60% on weekdays, 20% on weekends. A static alert at 80% would miss weekday spikes. Dynamic threshold learns the pattern and alerts on anomalies.

---

### Log Analytics Workspace

**What:** The central data store for logs. All Azure resources send diagnostic logs here. Query logs with KQL. One workspace per environment (or one shared workspace for smaller orgs).

> ⚠️ **Gotcha:** Log ingestion costs money (~$2.76/GB). Send only what you need. Set data retention policies (default 30 days, max 2 years in basic tier, 12 years in archive).

---

### Application Insights

**What:** APM (Application Performance Monitoring) for your code. Tracks request rates, response times, failure rates, exceptions, dependencies, and user behavior. Auto-instruments .NET, Java, Node.js, Python.

---

### Distributed Tracing

**What:** Tracks a single request across multiple microservices. Request enters Service A → calls Service B → calls Service C. Distributed tracing correlates ALL three into one end-to-end trace.

```
  Request ID: abc-123
  ├── Service A: 200ms (API Gateway)
  │   └── Service B: 150ms (Order Service)
  │       └── Service C: 800ms (Payment Service) ← bottleneck!
  Total: 1150ms
```

---

### Dependency Mapping

**What:** App Insights auto-discovers which services your app calls (SQL, Redis, external APIs). Shows a visual map of dependencies with success rates and latency.

---

### Live Metrics

**What:** Real-time stream of your app's performance — requests, failures, CPU, memory — with zero delay. Use during deployments or incident investigations.

---

### OpenTelemetry

**What:** Open-source, vendor-neutral observability framework. Standardized APIs for traces, metrics, and logs. Send telemetry to App Insights, Jaeger, Datadog, or any backend.

**DevOps example:** Instrument your app with OpenTelemetry once → switch between App Insights and Datadog without code changes.

---

### Prometheus

**What:** Open-source metrics collection system. Scrapes /metrics endpoints from your apps. AKS has managed Prometheus — collects K8s cluster metrics automatically.

---

### Grafana

**What:** Open-source dashboarding tool. Azure Managed Grafana connects to Azure Monitor, Prometheus, and Log Analytics. Beautiful dashboards without managing Grafana servers.

```
  Data Pipeline:
  AKS → Prometheus (collects metrics) → Grafana (visualizes dashboards)
  App → App Insights (collects traces) → Grafana (unified view)
```

---

### SLO (Service Level Objective)

**What:** YOUR internal target. "99.95% of requests will complete in <500ms." Stricter than SLA. If you miss your SLO, you take action before it becomes an SLA breach.

---

### SLI (Service Level Indicator)

**What:** The actual measurement. "This week, 99.92% of requests completed in <500ms." SLI is the metric, SLO is the target, SLA is the contract.

```
  SLI = what you measure    (99.92% success rate this week)
  SLO = what you aim for    (99.95% target)
  SLA = what you promise    (99.9% to customers — contractual)
```

---

### Log Retention

**What:** How long logs are kept. Default 30 days in Log Analytics. Interactive retention up to 2 years. Archive up to 12 years. Longer retention = higher cost.

---

### KQL (Kusto Query Language)

**What:** The query language for Log Analytics. SQL-like but pipe-based. Data flows left to right through operators.

```kql
// Find slow requests in the last hour
requests
| where timestamp > ago(1h)
| where duration > 5000
| summarize count() by name
| order by count_ desc
```

---

### KQL Operators Reference

**`where`** — Filter rows matching a condition:
```kql
requests | where resultCode == "500"
```

**`summarize`** — Aggregate data (like GROUP BY):
```kql
requests | summarize count() by resultCode
```

**`extend`** — Add a calculated column:
```kql
requests | extend durationSec = duration / 1000
```

**`project`** — Select specific columns (like SELECT):
```kql
requests | project name, duration, resultCode
```

**`join`** — Combine two tables:
```kql
requests | join dependencies on operation_Id
```

**`union`** — Merge rows from multiple tables:
```kql
union requests, exceptions
```

**`distinct`** — Unique values:
```kql
requests | distinct name
```

**`count`** — Count rows:
```kql
requests | where resultCode == "500" | count
```

**`bin()`** — Bucket time into intervals:
```kql
requests | summarize count() by bin(timestamp, 5m)
```

**`mv-expand`** — Expand arrays into rows:
```kql
datatable(tags: dynamic) [dynamic(["prod","web"])]
| mv-expand tags
```

**`parse_json`** — Parse JSON strings:
```kql
traces | extend parsed = parse_json(message)
```

> ⚠️ **Gotcha:** KQL is case-SENSITIVE for string comparisons. Use `=~` for case-insensitive matching: `where name =~ "MyApp"`.

---

# 13 — Security

---

### Microsoft Defender for Cloud

**What:** Cloud Security Posture Management (CSPM) + workload protection. Continuously assesses your Azure resources for security misconfigurations and provides recommendations.

```
  ┌──────────────────────────────────────────────┐
  │  Defender for Cloud                          │
  │                                              │
  │  CSPM (free):                                │
  │  • Secure Score                              │
  │  • Security recommendations                  │
  │  • Regulatory compliance dashboard           │
  │                                              │
  │  Workload Protection (paid plans):           │
  │  • Defender for Servers (VM threat detection)│
  │  • Defender for SQL (injection detection)    │
  │  • Defender for Containers (image scanning)  │
  │  • Defender for Key Vault (anomaly alerts)   │
  └──────────────────────────────────────────────┘
```

---

### Secure Score

**What:** A percentage (0-100%) showing your security posture. Higher = more secure. Each recommendation has points. Fix issues → score goes up.

**DevOps example:** Secure Score is 72%. Top recommendation: "Enable MFA for all privileged accounts" (+8 points). Fix it → score becomes 80%.

---

### Vulnerability Assessment

**What:** Scans VMs, containers, and SQL databases for known CVEs (Common Vulnerabilities and Exposures). Reports which patches are missing and severity.

---

### Adaptive Application Controls

**What:** ML-based allowlisting. Defender learns which applications normally run on your VMs, then alerts if an unknown executable runs (possible malware).

---

### Regulatory Compliance Dashboard

**What:** Maps your Azure configuration against compliance frameworks (CIS, NIST, PCI-DSS, HIPAA, ISO 27001). Shows pass/fail per control.

---

### Microsoft Sentinel

**What:** Cloud-native SIEM + SOAR. Collects security logs from Azure, M365, on-prem, and third-party sources. Detects threats with analytics rules, investigates with hunting queries, and auto-responds with playbooks.

```
  ┌──────────────────────────────────────────────┐
  │  Sentinel Pipeline                           │
  │                                              │
  │  Collect: Data connectors (Azure AD, M365,   │
  │           Firewall, Syslog, AWS, etc.)       │
  │     │                                        │
  │  Detect: Analytics rules (scheduled KQL      │
  │          queries that create incidents)      │
  │     │                                        │
  │  Investigate: Incidents, entity mapping,     │
  │               hunting queries, UEBA          │
  │     │                                        │
  │  Respond: Playbooks (Logic Apps) auto-run    │
  │           on incident creation               │
  └──────────────────────────────────────────────┘
```

---

### SIEM (Security Information and Event Management)

**What:** Centralized log collection + correlation + alerting. Sentinel IS Azure's SIEM. Collects logs from everywhere, correlates events, and detects attack patterns.

---

### SOAR (Security Orchestration, Automation, and Response)

**What:** Automates incident response. When Sentinel detects a threat, a playbook (Logic App) runs automatically — blocks an IP, disables an account, creates a ticket.

---

### Analytics Rules

**What:** KQL queries that run on a schedule in Sentinel. When results match, an incident is created. "If more than 5 failed logins from same IP in 10 minutes → create incident."

---

### Hunting Queries

**What:** Proactive KQL queries to find threats BEFORE they trigger rules. Security analysts write custom queries to look for suspicious patterns. "Find all PowerShell executions from non-admin accounts."

---

### Workbooks (Sentinel)

**What:** Interactive dashboards in Sentinel. Visualize security data — failed logins by country, top attacked resources, threat trends over time.

---

### UEBA (User and Entity Behavior Analytics)

**What:** Builds behavioral profiles for users and entities. Detects anomalies — "User John normally logs in from NYC. Today he logged in from Russia AND downloaded 10GB of data."

---

### Incident Management

**What:** Sentinel groups related alerts into incidents. An incident = a potential security breach. Analysts triage (true positive vs false positive), investigate, and respond.

---

### Threat Hunting

**What:** Proactively searching for threats that haven't triggered any alerts. Uses hunting queries, threat intelligence, and hypothesis-driven investigation.

---

### Key Vault

**What:** Secure store for secrets (passwords, connection strings), certificates, and encryption keys. RBAC-controlled, audited, and integrated with managed identities.

---

### Secrets / Certificates / Keys

| Type | What it stores | Example |
|------|---------------|---------|
| **Secrets** | Passwords, API keys, connection strings | `DB-ConnectionString` |
| **Certificates** | TLS/SSL certificates with auto-renewal | `*.myapp.com` wildcard cert |
| **Keys** | Encryption keys (RSA, EC) | Disk encryption key |

---

### RBAC vs Access Policies (Key Vault)

| Method | Details |
|--------|---------|
| **RBAC** (recommended) | Uses standard Azure RBAC roles. Visible in IAM blade. Auditable. Supports Conditional Access |
| **Access Policies** (legacy) | Per-vault policies. Not visible in IAM. Harder to audit across many vaults |

---

### HSM (Hardware Security Module)

**What:** Dedicated hardware for cryptographic operations. Keys never leave the HSM chip. FIPS 140-2 Level 3 certified. Managed HSM = dedicated HSM pool in Key Vault.

---

### Confidential Computing

**What:** Data is encrypted WHILE BEING PROCESSED (in-use), not just at rest and in transit. Uses hardware enclaves (Intel SGX, AMD SEV). Even Azure admins can't see your data.

```
  Traditional:     At-rest ✓ (encrypted disk)
                   In-transit ✓ (TLS)
                   In-use ✗ (data in RAM is plaintext)

  Confidential:    At-rest ✓
                   In-transit ✓
                   In-use ✓ (hardware enclave protects RAM)
```

---

### Trusted Launch

**What:** Security features for VMs: Secure Boot + vTPM. Protects against boot-level attacks (rootkits, bootkits). Enable at VM creation.

---

### Secure Boot

**What:** Ensures only signed, trusted software loads during VM boot. Blocks malware that tries to inject itself into the boot process.

---

### vTPM (Virtual Trusted Platform Module)

**What:** Virtual security chip that stores encryption keys, measures boot integrity, and supports BitLocker. Required for Trusted Launch and Windows 11.

---

### Zero Trust

**What:** Security model: "never trust, always verify." Every request is authenticated and authorized, regardless of where it comes from. No implicit trust for internal network traffic.

```
  Traditional:  Inside the firewall = trusted
  Zero Trust:   Nothing is trusted. Every request must prove:
                1. WHO you are (identity)
                2. WHAT device (compliance)
                3. WHERE from (location)
                4. WHAT you're accessing (least privilege)
```

**DevOps implementation:** Managed identities (no passwords), Private Endpoints (no public access), Conditional Access (verify every login), Network segmentation (NSGs on every subnet).

---

# 14 — DevOps & Deployment Strategies

---

### Azure DevOps

**What:** Microsoft's all-in-one DevOps platform. Five services: Repos (Git), Pipelines (CI/CD), Boards (project tracking), Artifacts (package feeds), Test Plans (testing).

---

### Azure Repos

**What:** Git repositories hosted in Azure DevOps. Supports unlimited private repos, branch policies, pull request reviews, and integration with Pipelines.

---

### Azure Pipelines

**What:** CI/CD automation. Build code, run tests, deploy to any cloud. Supports YAML pipelines (code-defined) and classic (GUI-defined). Free tier: 1 parallel job, 1800 min/month.

---

### Azure Boards

**What:** Work item tracking — Epics, Features, User Stories, Tasks, Bugs. Kanban boards, sprint planning, and burndown charts. Integrates with Repos (link commits to work items).

---

### Azure Artifacts

**What:** Package feed hosting. Store and share NuGet, npm, Maven, Python, and universal packages. Private feeds for your organization.

---

### YAML Pipelines

**What:** Define your CI/CD pipeline as code in a YAML file (`azure-pipelines.yml`). Stored in Git alongside your app code. Version-controlled, reviewable via PRs.

```yaml
trigger:
  branches: [main]

stages:
- stage: Build
  jobs:
  - job: BuildApp
    pool: { vmImage: 'ubuntu-latest' }
    steps:
    - script: npm install && npm test
    - task: Docker@2
      inputs: { command: buildAndPush }

- stage: Deploy
  dependsOn: Build
  jobs:
  - deployment: Production
    environment: 'prod'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
```

---

### CI/CD

**What:** Continuous Integration (automatically build + test on every commit) + Continuous Delivery/Deployment (automatically deploy to staging/production).

```
  CI:  Push code → Build → Run tests → ✓ or ✗
  CD:  Build passes → Deploy to staging → Approval → Deploy to prod

  CI catches bugs early. CD delivers value fast.
```

---

### Git

**What:** Distributed version control system. Every developer has a full copy of the repository. Changes are tracked as commits. Branches enable parallel work.

---

### Branching Strategies

```
  ┌─────────────────┬──────────────────────────────────────┐
  │ Strategy        │ How it works                         │
  ├─────────────────┼──────────────────────────────────────┤
  │ Trunk-based     │ All devs commit to main. Short-lived │
  │                 │ feature branches. Deploy from main.  │
  │ GitFlow         │ develop, feature/*, release/*, main. │
  │                 │ Complex but structured.              │
  │ GitHub Flow     │ main + feature branches. PR to main. │
  │                 │ Simple. Most popular.                │
  └─────────────────┴──────────────────────────────────────┘
```

---

### Merge Strategies

| Strategy | What it does |
|----------|-------------|
| **Merge commit** | Creates a merge commit preserving full branch history |
| **Squash merge** | Combines all branch commits into one clean commit on main |
| **Rebase** | Replays your commits on top of the latest main. Linear history |

---

### Rebase

**What:** Moves your branch's commits to the tip of main. Creates linear history (no merge commits). Cleaner but rewrites history — never rebase shared/public branches.

---

### Cherry-pick

**What:** Copy a specific commit from one branch to another without merging the whole branch. Used for hotfixes — pick the fix from dev, apply to main.

---

### Blue-Green Deployment

**What:** Two identical environments: Blue (current production) and Green (new version). Deploy to Green → test → switch traffic from Blue to Green. Instant rollback = switch back to Blue.

```
  ┌─────────┐    traffic    ┌─────────┐
  │ Blue    │◄══════════════│ Users   │
  │ v1.0    │    (current)  └─────────┘
  └─────────┘
  ┌─────────┐
  │ Green   │  ← deploy v2.0 here, test
  │ v2.0    │  ← switch traffic when ready
  └─────────┘
```

---

### Canary Deployment

**What:** Route a small percentage of traffic (e.g., 5%) to the new version. Monitor for errors. Gradually increase (5% → 25% → 50% → 100%). Rollback if issues appear.

```
  v1.0: 95% of traffic ──────────►
  v2.0:  5% of traffic ──► (monitor errors, latency)
  
  If healthy: 5% → 25% → 50% → 100%
  If broken:  shift back to 0% instantly
```

---

### Rolling Deployment

**What:** Update instances one at a time (or in batches). Instance 1 gets v2.0 while instances 2-5 still run v1.0. Then instance 2, then 3... No extra infrastructure needed.

---

### Immutable Infrastructure

**What:** Never patch or modify running servers. Instead, build a NEW image with the changes and replace the old instances entirely. If something breaks, deploy the previous image.

```
  Mutable:   SSH into server → apt update → pip install → hope it works
  Immutable: Build new image → deploy fresh instances → kill old ones
```

---

### Drift Detection

**What:** Detecting when actual infrastructure differs from the IaC definition. A VM was manually resized, a port was opened by hand — these changes "drift" from the declared state.

**DevOps example:** Terraform plan shows "3 resources changed" but nobody committed any Terraform changes → someone made manual portal changes (drift!).

---

### Artifact Feeds

**What:** Private package repositories in Azure Artifacts. Publish internal libraries (npm, NuGet) and consume them across teams. Upstream sources proxy public registries (npmjs.org).

---

### Pipeline Agent

**What:** The machine that actually executes pipeline jobs. Can be Microsoft-hosted (managed VMs) or self-hosted (your own VMs/containers).

---

### Self-Hosted Agent vs Microsoft-Hosted Agent

| Type | Pros | Cons |
|------|------|------|
| **Microsoft-hosted** | Zero maintenance, fresh VM each job | Limited software, can't access private VNets |
| **Self-hosted** | Full control, VNet access, cached dependencies | You manage patching, scaling, availability |

---

### Agent Pool

**What:** A group of agents. Jobs are dispatched to any available agent in the pool. Organize by purpose: "linux-pool", "windows-pool", "gpu-pool".

---

### Secure Files / Variable Groups

**What:** Secure Files = store certificates, SSH keys, mobile provisioning profiles in Pipelines. Variable Groups = shared sets of variables (like connection strings) used across multiple pipelines.

---

### Environment Approvals / Release Gates

**What:** Manual or automated checks before deploying to a stage. Approvals = a person clicks "approve." Gates = automated checks (query Azure Monitor for zero errors, check work item count).

---

### Branch Policies

**What:** Rules enforced on Git branches. Require PR reviews before merge, require passing CI build, require linked work items, enforce merge strategy.

**DevOps example:** `main` branch policy: minimum 2 reviewers, build must pass, squash merge only, no direct pushes.

---

### Protected Branch / Required Reviewers

**What:** `main` and `release/*` branches are protected — no one can push directly. All changes go through PRs with required reviewers. Prevents "oops I pushed to production."

---

# 15 — Governance, Cost & Disaster Recovery

---

### Azure Policy

**What:** Enforce organizational rules on Azure resources. "All storage accounts must use HTTPS." "VMs must be in approved regions." Policies evaluate at resource creation and on existing resources.

```
  Policy effects:
  • Audit     → logs non-compliance (doesn't block)
  • Deny      → blocks non-compliant resource creation
  • Modify    → auto-fixes resources (e.g., add missing tags)
  • DeployIfNotExists → deploys a resource if missing
  • Append    → adds fields to requests
```

---

### Initiative Definitions

**What:** A BUNDLE of related policies. Instead of assigning 20 policies individually, assign one initiative. Example: "CIS Benchmark" initiative contains 200+ security policies.

---

### Remediation Tasks

**What:** Fix existing non-compliant resources. A `DeployIfNotExists` policy only applies to NEW resources. Remediation task retroactively applies it to EXISTING resources.

---

### Policy Exemptions

**What:** Temporarily exclude a resource from a policy. "This dev VM can have a public IP until March 31st." Exemptions have expiry dates.

---

### Guest Configuration

**What:** Audit settings INSIDE a VM (not just Azure resource properties). Check if Windows Defender is enabled, if password policies are set, if specific software is installed.

---

### Azure Blueprints (Deprecated)

**What:** Bundled ARM templates + policies + RBAC + resource groups into a deployable package. Being replaced by **Deployment Stacks** and **Template Specs**. Don't use for new projects.

---

### Azure Landing Zones

**What:** A pre-configured, best-practice Azure environment. Includes management groups, subscriptions, networking (hub-spoke), policies, and identity. The "foundation" before you deploy workloads.

```
  ┌─────────────────────────────────────────────────┐
  │  Azure Landing Zone                             │
  │                                                 │
  │  Root MG                                        │
  │  ├── Platform                                   │
  │  │   ├── Identity Sub (Entra Connect, AD DS)   │
  │  │   ├── Connectivity Sub (Hub VNet, Firewall) │
  │  │   └── Management Sub (Log Analytics, ASR)   │
  │  └── Workloads                                  │
  │      ├── Prod Sub (spoke VNet, apps)           │
  │      └── Dev Sub (spoke VNet, dev apps)        │
  └─────────────────────────────────────────────────┘
```

---

### CAF (Cloud Adoption Framework)

**What:** Microsoft's guidance for cloud adoption. Covers strategy, planning, readiness, migration, governance, and management. Landing Zones are the "implement" step.

---

### Azure Cost Management

**What:** Track, analyze, and optimize Azure spending. Cost analysis by resource, tag, subscription. Set budgets with alerts. Identify waste (unused VMs, oversized disks).

---

### Budgets

**What:** Set spending limits with alerts. "Alert me at 80% of $5,000/month. Alert the team at 100%." Budgets don't stop spending — they only alert. Use resource locks or policies to prevent overspend.

---

### Reservations / Savings Plans

| Type | Savings | Commitment |
|------|---------|-----------|
| **Reservations** | Up to 72% | Specific VM size + region for 1-3 years |
| **Savings Plans** | Up to 65% | $/hour commitment for any VM size/region for 1-3 years |

> **FAQ:** *Which to choose?* Reservations = maximum savings if you know exact VM sizes. Savings Plans = flexibility if workloads change.

---

### Spot VMs

**What:** Use Azure's unused capacity at up to 90% discount. Azure can EVICT your VM with 30-second notice when it needs the capacity back. For batch jobs, CI runners, fault-tolerant workloads.

> ⚠️ **Gotcha:** Never run production workloads on Spot VMs. They WILL be evicted. Design for interruption.

---

### Rightsizing

**What:** Match VM sizes to actual usage. A D4s_v3 (4 CPU) running at 10% CPU → downgrade to D2s_v3 (2 CPU). Azure Advisor provides rightsizing recommendations.

---

### FinOps

**What:** Financial Operations — the practice of bringing financial accountability to cloud spending. Combines engineering, finance, and business to optimize cost.

---

### Azure Arc

**What:** Extend Azure management (policies, monitoring, RBAC) to resources OUTSIDE Azure — on-prem servers, other clouds (AWS/GCP), edge devices. Manage everything from one pane.

---

### Azure Migrate

**What:** Hub for migrating on-prem workloads to Azure. Discovery (find servers), assessment (size, cost estimate), migration (replicate and cutover).

---

### Recovery Services Vault

**What:** Container for backup data and ASR replication data. Stores VM backups, SQL backups, file backups. Supports cross-region restore and immutable backups.

---

### Azure Backup

**What:** Managed backup service. Backs up VMs, SQL, Files, Blobs. Scheduled, automated, encrypted. Restore full VM, individual files, or specific DBs.

---

### Azure Site Recovery (ASR)

**What:** Disaster recovery as a service. Continuously replicates VMs to a secondary region. When disaster strikes, failover to the secondary in minutes.

```
  Normal:    VM runs in East US → replicates to West US (async)
  Disaster:  East US down → Failover → VM now runs in West US
  Recovery:  East US back → Failback → VM returns to East US
```

---

### RPO / RTO

```
  RPO (Recovery Point Objective) = How much data can you lose?
  RPO = 15 min → you need backups every 15 min

  RTO (Recovery Time Objective) = How long can you be down?
  RTO = 1 hour → must be back online within 1 hour
```

---

### Active-Active / Active-Passive

| Pattern | How it works | RTO |
|---------|-------------|-----|
| **Active-Active** | Both regions serve traffic simultaneously. LB distributes. If one fails, the other absorbs all traffic | Near zero |
| **Active-Passive** | Primary serves traffic. Secondary is standby. On failure, DNS/LB switches to secondary | Minutes |

---

### Event Grid

**What:** Event routing service. When something HAPPENS (blob created, resource changed), Event Grid delivers the event to subscribers (Function, Logic App, webhook) within seconds.

---

### Event Hub

**What:** Big data streaming ingestion. Millions of events/second. For telemetry, IoT, clickstream data. Like Apache Kafka in Azure.

---

### Service Bus

**What:** Enterprise message broker. Queues (point-to-point) and Topics (pub-sub). Supports ordering, deduplication, sessions, dead-letter queues. More features than Queue Storage.

```
  Queue Storage:  Simple, cheap, 64KB messages
  Service Bus:    Enterprise, sessions, ordering, 256KB-100MB messages
  Event Grid:     Event notification (react to things that happened)
  Event Hub:      Streaming ingestion (millions of events/sec)
```

---

### Azure Service Health / Resource Health

| Service | What it shows |
|---------|--------------|
| **Service Health** | Azure-wide outages, planned maintenance, health advisories affecting your resources |
| **Resource Health** | Status of YOUR specific resources — is this VM running? Is this SQL DB available? |

---

### Activity Logs

**What:** Audit log of ALL control-plane operations in your subscription. Who created what, who deleted what, who changed RBAC. Retained for 90 days. Send to Log Analytics for longer retention.

---

### Azure Resource Graph

**What:** Query engine for ALL your Azure resources across ALL subscriptions. Instantly answer "How many VMs are running?" or "Which storage accounts allow public access?" using KQL-like queries.

---

# 16 — Advanced Networking & Protocols

---

### TCP 3-Way Handshake

**What:** How two machines establish a TCP connection before exchanging data. Three packets: SYN → SYN-ACK → ACK.

```
  Client                  Server
    │  SYN (seq=100)        │
    │──────────────────────►│
    │                       │
    │  SYN-ACK (seq=200,    │
    │  ack=101)             │
    │◄──────────────────────│
    │                       │
    │  ACK (ack=201)        │
    │──────────────────────►│
    │                       │
    │  Connection established│
```

> ⚠️ **Gotcha:** SYN flood attack = attacker sends thousands of SYNs without completing the handshake, exhausting server resources. Azure DDoS Protection mitigates this.

---

### TCP Window Size / Flow Control

**What:** The receiver advertises how much data it can accept before the sender must wait for an ACK. Larger window = higher throughput. TCP window scaling enables windows up to 1 GB.

---

### TCP Keep-Alive

**What:** Periodic packets sent on idle connections to confirm the other side is still alive. Azure Load Balancer has a 4-minute idle timeout by default — enable TCP keep-alive or increase timeout to prevent dropped connections.

> ⚠️ **Gotcha:** Azure LB kills idle TCP connections after 4 minutes. For long-running connections (WebSockets, database pools), set `IdleTimeoutInMinutes: 30` or enable keep-alives.

---

### TLS Handshake

**What:** Establishes an encrypted HTTPS connection. Happens AFTER the TCP handshake. Negotiates cipher suite, exchanges certificates, generates session keys.

```
  Client                           Server
    │  ClientHello (TLS versions,   │
    │  cipher suites)               │
    │──────────────────────────────►│
    │                               │
    │  ServerHello + Certificate    │
    │  + server key exchange        │
    │◄──────────────────────────────│
    │                               │
    │  Client verifies certificate  │
    │  Client key exchange          │
    │──────────────────────────────►│
    │                               │
    │  Both derive session keys     │
    │  Encrypted communication ✓    │
```

---

### TLS Versions

| Version | Status |
|---------|--------|
| TLS 1.0 / 1.1 | Deprecated. Disable everywhere |
| **TLS 1.2** | Current standard. Minimum for Azure services |
| **TLS 1.3** | Latest. Faster handshake (1 round trip). Most secure |

---

### mTLS (Mutual TLS)

**What:** BOTH sides present certificates. Normal TLS = only server proves identity. mTLS = client AND server prove identity. Used for service-to-service communication in zero-trust environments.

```
  Normal TLS:  Client verifies server certificate  (one-way)
  mTLS:        Client verifies server certificate
               Server verifies client certificate   (two-way)
```

**DevOps example:** Service mesh (Istio) uses mTLS between all pods. Each pod has a certificate. Any unauthorized service is rejected.

---

### SNI (Server Name Indication)

**What:** TLS extension that tells the server WHICH hostname the client wants to connect to. Allows multiple HTTPS sites on one IP address.

**Plain English:** Without SNI, one IP = one certificate. With SNI, one IP can serve `api.myapp.com`, `admin.myapp.com`, and `docs.myapp.com` each with their own cert.

---

### Certificates

**What:** Digital documents that bind a public key to an identity (domain name, organization). Used for TLS/HTTPS, code signing, and client authentication.

---

### Certificate Authority (CA)

**What:** A trusted organization that issues certificates. Browsers trust CAs → CAs sign your certificate → browsers trust your site.

```
  Public CAs:   DigiCert, Let's Encrypt, GlobalSign
  Private CAs:  Your org's internal CA (AD CS) for internal services
```

---

### CSR (Certificate Signing Request)

**What:** A file you generate containing your public key and domain name. You send the CSR to a CA → CA verifies you own the domain → CA returns a signed certificate.

---

### SAN (Subject Alternative Name)

**What:** A certificate field listing all domain names the cert is valid for. One cert for multiple domains: `myapp.com`, `api.myapp.com`, `www.myapp.com`.

---

### Wildcard Certificate

**What:** One cert valid for all subdomains: `*.myapp.com` covers `api.myapp.com`, `www.myapp.com`, `admin.myapp.com`. Does NOT cover `myapp.com` itself (add it as a SAN).

> ⚠️ **Gotcha:** Wildcard certs only cover ONE level. `*.myapp.com` covers `api.myapp.com` but NOT `v2.api.myapp.com`.

---

### Certificate Pinning

**What:** Your app only trusts a SPECIFIC certificate (not any cert from any CA). Prevents man-in-the-middle attacks even if a CA is compromised. Hard to manage — rotate carefully.

---

### OCSP (Online Certificate Status Protocol)

**What:** Real-time check: "Is this certificate still valid or has it been revoked?" Browser asks the CA's OCSP responder before trusting a certificate.

---

### HSTS (HTTP Strict Transport Security)

**What:** HTTP header that tells browsers to ONLY use HTTPS for this domain. Prevents downgrade attacks (user types http:// → browser auto-upgrades to https://).

---

### IPSec

**What:** Protocol suite for encrypting IP traffic. Used by VPN Gateway for S2S and VNet-to-VNet tunnels. Two modes:

| Mode | What it encrypts |
|------|-----------------|
| **Transport** | Only the payload (data). IP header is visible |
| **Tunnel** | Entire original packet (header + data). Wrapped in new IP header |

---

### IKE (Internet Key Exchange)

**What:** Protocol that negotiates the encryption keys for IPSec tunnels. IKEv2 is faster and more reliable than IKEv1. Azure VPN Gateway supports both.

---

### NAT-T (NAT Traversal)

**What:** Wraps IPSec packets in UDP (port 4500) so they can pass through NAT devices. Without NAT-T, IPSec packets get dropped by firewalls doing NAT.

---

### VXLAN (Virtual Extensible LAN)

**What:** Network overlay protocol that encapsulates Layer 2 frames inside UDP packets. Enables millions of virtual networks (16M IDs vs VLAN's 4096). Used by Azure's SDN fabric under the hood.

```
  Original frame → VXLAN header (VNI) → UDP → Outer IP → Wire
  
  VM-A (VNet-1) sends frame → Azure SDN encapsulates in VXLAN
  → travels across physical network → decapsulated at destination host
  → delivered to VM-B (VNet-1)
```

---

### Overlay Networking (Protocol Context)

**What:** A virtual network built on top of the physical network using encapsulation (VXLAN, GENEVE, GRE). Azure VNets, K8s pod networks, and NVAs all use overlays.

---

### MTU (Maximum Transmission Unit)

**What:** Maximum packet size (in bytes) that a network link can carry. Standard = 1500 bytes. VPN/VXLAN overhead reduces effective MTU. Mismatched MTU = dropped/fragmented packets.

> ⚠️ **Gotcha:** VPN tunnels reduce MTU to ~1400 bytes. If your app sends 1500-byte packets through a VPN, they get fragmented or dropped. Set MSS clamping or reduce app MTU.

---

### Fragmentation

**What:** Breaking a large packet into smaller pieces when it exceeds the MTU. The receiver reassembles fragments. Fragmentation hurts performance — avoid it by setting correct MTU.

---

### Jumbo Frames

**What:** Frames with MTU > 1500 bytes (typically 9000 bytes). Higher throughput for large data transfers. Azure VMs support up to 9000-byte MTU within the same VNet.

---

# 17 — Advanced Compute, Patterns & Caching

---

### Circuit Breaker Pattern

**What:** Prevents cascading failures. If a downstream service fails repeatedly, the circuit breaker "opens" and immediately returns errors WITHOUT calling the failing service. After a timeout, it "half-opens" to test recovery.

```
  States:
  CLOSED → calls flow normally
     │ (failures exceed threshold)
     ▼
  OPEN → all calls fail immediately (fast fail)
     │ (timeout expires)
     ▼
  HALF-OPEN → allow one test call
     │ success → CLOSED
     │ failure → OPEN again
```

**DevOps example:** Your API calls a payment service. Payment service goes down. Without circuit breaker → all API threads hang waiting → your API dies too. With circuit breaker → fast fail, users see "try later."

---

### Retry Pattern

**What:** Automatically retry failed operations with increasing delays. Handles transient faults (network blip, throttling).

```
  Attempt 1: fail → wait 1s
  Attempt 2: fail → wait 2s
  Attempt 3: fail → wait 4s  (exponential backoff)
  Attempt 4: fail → give up, return error
```

> ⚠️ **Gotcha:** Always use exponential backoff with jitter (random delay). Without jitter, all clients retry at the same time → thundering herd → service crashes again.

---

### Bulkhead Pattern

**What:** Isolate components into separate pools so a failure in one doesn't exhaust resources for all. Like watertight compartments in a ship — one floods, the others stay dry.

**DevOps example:** Separate thread pools for critical API (payment) and non-critical API (recommendations). If recommendations hangs, payment still works.

---

### Saga Pattern

**What:** Manage distributed transactions across microservices using a sequence of local transactions. Each step has a compensating action (undo) if a later step fails.

```
  Order Service → Payment Service → Inventory Service
       │                │                │
  If Inventory fails:   │                │
       │                │       compensate: refund payment
       │           compensate: cancel order
```

---

### CQRS (Command Query Responsibility Segregation)

**What:** Separate read and write models. Write operations go to a write-optimized store. Read operations go to a read-optimized store (denormalized, cached).

```
  Commands (writes) → Write DB (normalized, ACID)
                          │ (sync/async)
                          ▼
  Queries (reads) ← Read DB (denormalized, fast)
```

---

### Strangler Fig Pattern

**What:** Gradually replace a legacy monolith by routing traffic to new microservices, one feature at a time. The new system "strangles" the old one until nothing is left.

```
  Phase 1: 100% → Monolith
  Phase 2: /api/orders → New Service, everything else → Monolith
  Phase 3: /api/users → New Service, /api/orders → New Service
  Phase N: 0% → Monolith (decommissioned)
```

---

### Ambassador Pattern

**What:** A proxy sidecar that handles cross-cutting network concerns (retries, circuit breaking, TLS) on behalf of the main service. The app code stays simple.

---

### Throttling / Rate Limiting

**What:** Limit how many requests a client can make in a time window. "Max 100 requests per minute per API key." Prevents abuse and protects backend resources.

```
  Client sends request #101 in 1 minute:
  → HTTP 429 Too Many Requests
  → Retry-After: 30 (seconds)
```

---

### Cache-Aside Pattern

**What:** App checks cache first. If miss → read from DB → store in cache → return. Next request hits cache (fast). The app manages the cache, not the DB.

```
  Request → Cache hit?
            ├── YES → return cached data (fast)
            └── NO → read from DB → store in cache → return
```

---

### Azure Cache for Redis

**What:** Managed Redis instance. In-memory key-value store for caching, session state, pub/sub, and leaderboards. Sub-millisecond response times.

**DevOps example:** Cache database query results in Redis. First request = 200ms (DB). Subsequent requests = 2ms (Redis). 100× faster.

> ⚠️ **Gotcha:** Redis is in-memory — data is lost if the node restarts (unless using Premium tier with persistence). Design for cache invalidation.

---

### CDN (Content Delivery Network)

**What:** Cache static content (images, JS, CSS) at edge locations worldwide. Users download from the nearest edge server, not your origin server.

```
  Without CDN: User in Tokyo → downloads from US origin (200ms)
  With CDN:    User in Tokyo → downloads from Tokyo edge (20ms)
```

---

### Horizontal Scaling (Scale Out)

**What:** Add MORE machines to handle increased load. 2 VMs → 10 VMs. Requires stateless application design. Preferred for cloud-native apps.

---

### Vertical Scaling (Scale Up)

**What:** Make the EXISTING machine bigger. 2 CPU → 8 CPU. Limited by the largest available VM size. Requires downtime to resize. Hits a ceiling.

```
  Scale Out:  ■ ■ → ■ ■ ■ ■ ■ ■  (more machines)
  Scale Up:   ■ → ■■■■           (bigger machine)
```

---

### Scale Unit Architecture

**What:** Design your system as repeatable "units" that can be stamped out. Each unit contains a complete set of resources (VMs, DB, storage). Scale by deploying more units.

---

### Geo-Replication (Database)

**What:** Replicate your database to other Azure regions. Active geo-replication (Azure SQL) creates readable secondaries. Failover in seconds.

---

### Connection Pooling

**What:** Reuse existing database connections instead of creating a new one for each request. A pool of pre-opened connections is shared across requests.

> ⚠️ **Gotcha:** Creating a new SQL connection takes ~50ms. Connection pooling reduces this to ~0ms. Always enable pooling. Common issue: .NET apps NOT disposing SqlConnection properly → pool exhaustion.

---

### Backpressure

**What:** When a system is overloaded, it signals upstream to SLOW DOWN instead of accepting everything and crashing. Queues filling up → producer is told to wait.

---

### Idempotency (Patterns Context)

**What:** An operation that produces the same result even if executed multiple times. Critical for retries — if a payment request is retried, it should charge ONCE, not twice.

**Implementation:** Use idempotency keys. Client sends `Idempotency-Key: abc123`. Server checks if `abc123` was already processed → returns cached result instead of processing again.

---

### Eventual Consistency

**What:** After a write, all replicas will EVENTUALLY have the same data, but not immediately. Reads might return stale data briefly. Most distributed systems use this.

```
  Write to primary → primary returns success
  → async replication to replicas (1-5 seconds)
  → during those seconds, reads from replicas return OLD data
  → eventually, all replicas have the new data
```

---

### Distributed Locking

**What:** Ensure only ONE instance of an application performs a critical operation at a time, across multiple servers. Use Redis SETNX, Azure Blob leases, or Cosmos DB stored procedures.

> ⚠️ **Gotcha:** Distributed locks are hard to get right. Watch for lock expiry (process takes longer than lock TTL → two processes run simultaneously). Use fencing tokens.

---

# 18 — AD DS Fundamentals

---

### Active Directory Domain Services (AD DS)

**What:** Microsoft's on-prem directory service. Stores user accounts, computer objects, groups, and policies. Provides authentication (Kerberos/NTLM) and authorization for Windows environments. The foundation of enterprise identity since Windows 2000.

```
  ┌──────────────────────────────────────────────┐
  │  AD DS                                       │
  │                                              │
  │  What it stores:                             │
  │  • Users (john.doe@corp.local)               │
  │  • Computers (WS-JOHN, SRV-SQL01)           │
  │  • Groups (IT-Admins, HR-Users)              │
  │  • GPOs (Password Policy, Desktop Lockdown)  │
  │                                              │
  │  What it does:                               │
  │  • Authenticates users (Kerberos/NTLM)       │
  │  • Authorizes access (ACLs, group membership)│
  │  • Distributes policies (GPO)                │
  └──────────────────────────────────────────────┘
```

---

### Domain Controller (DC)

**What:** A server running AD DS that stores a writable copy of the directory database (NTDS.dit). Handles authentication requests. Every domain needs at least 2 DCs for redundancy.

> ⚠️ **Gotcha:** DCs should NEVER run other workloads (no SQL Server, no IIS). They should be dedicated, hardened servers. Losing all DCs = entire domain is dead.

---

### Forest

**What:** The top-level container in AD DS. The ULTIMATE security boundary. A forest contains one or more domains that share a common schema and Global Catalog. Trusts between forests are explicit.

```
  Forest: corp.com
  ├── Domain: corp.com (root domain)
  ├── Domain: us.corp.com (child domain)
  └── Domain: eu.corp.com (child domain)
  
  Forest: partner.com (separate forest, separate security)
```

---

### Domain

**What:** A logical boundary for administration, authentication, and policy. All objects (users, computers, groups) belong to a domain. Domains share a common namespace (corp.com, us.corp.com).

---

### Tree

**What:** A hierarchy of domains sharing a contiguous namespace. `corp.com` → `us.corp.com` → `ny.us.corp.com`. Parent-child trust is automatically created between tree domains.

---

### Organizational Unit (OU)

**What:** A container inside a domain to organize objects (users, computers, groups). OUs are used for delegating administration and applying GPOs.

```
  corp.com (domain)
  ├── OU: IT Department
  │   ├── OU: Servers
  │   │   ├── SRV-SQL01
  │   │   └── SRV-WEB01
  │   └── OU: Admins
  │       ├── john.admin
  │       └── jane.admin
  ├── OU: HR Department
  │   └── OU: Users
  │       ├── bob.hr
  │       └── alice.hr
  └── OU: Workstations
      ├── WS-BOB
      └── WS-ALICE
```

> **FAQ:** *OU vs Group?* OUs organize objects for MANAGEMENT (GPOs, delegation). Groups organize objects for ACCESS (permissions, email).

---

### FSMO Roles (Flexible Single Master Operations)

**What:** Five special roles that only ONE DC holds at a time. Most AD operations are multi-master (any DC can handle them), but these five require a single authoritative source.

| Role | Scope | What it does |
|------|-------|-------------|
| **Schema Master** | 1 per forest | Controls schema changes (adding attributes) |
| **Domain Naming Master** | 1 per forest | Controls adding/removing domains |
| **PDC Emulator** | 1 per domain | Password changes, time sync, GPO, lockout |
| **RID Master** | 1 per domain | Allocates unique ID pools to DCs |
| **Infrastructure Master** | 1 per domain | Resolves cross-domain object references |

> ⚠️ **Gotcha:** PDC Emulator is the most critical. If it's down: password changes fail, account lockouts don't process, time drifts. Monitor it closely.

---

### Domain Join

**What:** Adding a computer to an Active Directory domain. The computer creates an account in AD (computer object), gets a machine password, and can authenticate users via Kerberos.

```
  Before domain join: Standalone PC. Local accounts only.
  After domain join:  PC is managed by AD. Domain users can log in.
                      GPOs apply. Kerberos works. Centralized management.
```

---

### Computer Objects

**What:** AD objects representing machines joined to the domain. Each has a machine account (SRV-SQL01$) and a password that auto-rotates every 30 days. Used for machine-to-machine authentication.

---

### AD Sites

**What:** Represent physical network locations (offices, data centers). AD uses sites to optimize replication traffic and help clients find the nearest DC.

```
  Site: New York Office (subnet 10.0.1.0/24)
  ├── DC: DC-NY01
  └── DC: DC-NY02

  Site: London Office (subnet 10.0.2.0/24)
  ├── DC: DC-LDN01
  └── DC: DC-LDN02

  Users in 10.0.1.0/24 → authenticate to DC-NY01/02 (local)
  NOT DC-LDN01 (across the WAN)
```

---

### AD Subnets

**What:** Map IP subnets to AD Sites. When a computer starts, it checks its IP → matches to a subnet → finds its site → finds the nearest DCs. Without subnet mappings, clients pick random DCs.

---

### Site Links

**What:** Define replication paths between AD Sites. Control replication schedule (e.g., every 180 minutes) and cost (prefer cheaper links). ISTG (Inter-Site Topology Generator) uses site links to build replication topology.

---

### AD Schema

**What:** The blueprint defining what object types (user, computer, group) and attributes (firstName, email, phoneNumber) exist in AD. Schema is forest-wide — one change affects ALL domains.

> ⚠️ **Gotcha:** Schema changes are IRREVERSIBLE. You can deactivate attributes but never delete them. Test schema changes in a lab forest first.

---

### Global Catalog (GC)

**What:** A DC that stores a PARTIAL, read-only copy of ALL objects in ALL domains in the forest. Enables cross-domain searches (find a user in any domain) and Universal Group membership resolution.

---

### Forest / Domain Functional Level

**What:** Determines which AD DS features are available. Higher levels enable newer features but require ALL DCs to run a minimum Windows Server version. Cannot be downgraded.

```
  Functional Level → Minimum DC OS required:
  2016 → Windows Server 2016+
  2019 → Windows Server 2019+ (adds Entra hybrid features)
  2025 → Windows Server 2025+ (latest)
```

---

### AD Recycle Bin

**What:** Recover accidentally deleted AD objects (users, OUs, groups) with ALL attributes intact. Must be enabled (off by default). Requires Forest Functional Level 2008 R2+.

**DevOps example:** Someone deletes the "IT-Admins" group. Without Recycle Bin: recreate from scratch, re-add all members, re-apply permissions. With Recycle Bin: restore in 30 seconds, everything intact.

---

### Distinguished Name (DN) / RDN

**What:** The full path to an object in AD. Like a file path but in LDAP format.

```
  DN:  CN=John Doe,OU=Users,OU=IT,DC=corp,DC=com
  RDN: CN=John Doe (just the object's own name)

  CN = Common Name
  OU = Organizational Unit
  DC = Domain Component
```

---

### AD DS on Azure VMs

**What:** Run Domain Controllers as Azure VMs for hybrid or cloud-only AD DS. Place DCs in an Availability Set or across Availability Zones. Use Managed Disks with write caching disabled for NTDS.dit.

> ⚠️ **Gotcha:** NEVER snapshot or restore AD DS VMs from backup without proper procedures — it causes USN rollback (replication corruption). Use Windows Server Backup, not Azure VM snapshots.

---

### Entra Domain Services (Managed AD DS)

**What:** Microsoft-managed AD DS in Azure. Provides domain join, LDAP, Kerberos, NTLM WITHOUT managing DCs yourself. Objects sync FROM Entra ID (one-way). For legacy apps that need AD protocols.

```
  Entra ID → syncs users/groups → Entra Domain Services
  Legacy app authenticates via LDAP/Kerberos ✓
  No DCs to manage ✓
  Can't extend schema or create trusts ✗
```

---

# 19 — AD Auth, GPO & Replication

---

### Kerberos Authentication

**What:** The PRIMARY authentication protocol in AD. Ticket-based — user proves identity once, gets tickets to access services without re-entering passwords. Uses symmetric key encryption.

```
  ┌────────────────────────────────────────────────┐
  │  Kerberos Flow (simplified)                    │
  │                                                │
  │  1. User logs in → sends credentials to DC     │
  │                                                │
  │  2. DC returns TGT (Ticket Granting Ticket)    │
  │     (proof: "you ARE john.doe")                │
  │                                                │
  │  3. User wants to access file server           │
  │     → sends TGT to DC, asks for service ticket │
  │                                                │
  │  4. DC returns Service Ticket for file server   │
  │                                                │
  │  5. User presents Service Ticket to file server │
  │     → file server validates → access granted   │
  │                                                │
  │  No password sent to file server! Just tickets. │
  └────────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Kerberos requires TIME SYNC (max 5-minute skew between client and DC). If time drifts, Kerberos fails and falls back to NTLM. PDC Emulator is the time authority.

---

### TGT (Ticket Granting Ticket)

**What:** Your "master ticket" after logging in. Valid for 10 hours by default. Used to REQUEST service tickets without re-entering your password. Cached locally on your machine.

---

### Service Ticket (TGS)

**What:** A ticket for a SPECIFIC service (file share, SQL, web app). Obtained by presenting your TGT to the DC. Contains your identity and permissions. Valid for 10 hours.

---

### SPN (Service Principal Name)

**What:** A unique identifier for a service instance in AD. Kerberos uses SPNs to find which account runs a service. Format: `service/hostname:port`.

```
  Examples:
  MSSQLSvc/SQL01.corp.com:1433     (SQL Server)
  HTTP/webapp.corp.com              (IIS web app)
  HOST/DC01.corp.com               (domain controller)
```

> ⚠️ **Gotcha:** Duplicate SPNs break Kerberos authentication. Use `setspn -X` to check for duplicates. Missing SPNs force NTLM fallback.

---

### Kerberos Delegation

**What:** Allows a service to impersonate a user and access another service on their behalf. Web server accesses SQL "as" the logged-in user.

| Type | Risk level |
|------|-----------|
| **Unconstrained** | Service can impersonate user to ANY service. DANGEROUS |
| **Constrained** | Service can only impersonate to SPECIFIC services |
| **Resource-Based** | The TARGET resource controls who can delegate to it (preferred) |

---

### NTLM Authentication

**What:** Older, challenge-response authentication. No tickets. Server sends a challenge → client encrypts it with password hash → server verifies. Slower and less secure than Kerberos.

```
  NTLM is used when:
  • Kerberos is unavailable (no DC contact, time skew)
  • Connecting by IP address instead of hostname
  • Legacy applications that don't support Kerberos
  • Cross-forest without proper trust configuration
```

> ⚠️ **Gotcha:** NTLM is vulnerable to relay attacks and pass-the-hash. Disable NTLMv1 everywhere. Audit NTLMv2 usage and work toward eliminating NTLM entirely.

---

### LDAP (Lightweight Directory Access Protocol)

**What:** The protocol for QUERYING and MODIFYING AD. Applications use LDAP to search for users, read attributes, reset passwords. Port 389 (unencrypted) or 636 (LDAPS = LDAP over TLS).

```
  LDAP query: "Find all users in the IT OU"
  (&(objectClass=user)(memberOf=CN=IT-Users,OU=Groups,DC=corp,DC=com))
```

---

### LDAPS (LDAP Secure)

**What:** LDAP encrypted with TLS (port 636). Requires a certificate on the DC. Microsoft is deprecating unencrypted LDAP (port 389) — migrate to LDAPS or LDAP channel binding.

---

### SAML (Security Assertion Markup Language)

**What:** XML-based protocol for SSO between identity providers and applications. ADFS issues SAML tokens. Being replaced by OAuth2/OIDC in modern apps, but still used by many enterprise SaaS apps.

---

### GPO (Group Policy Object)

**What:** A set of rules/settings applied to users and computers in an OU. Controls everything: password policies, desktop wallpaper, software installation, firewall rules, drive mappings.

```
  ┌──────────────────────────────────────────────┐
  │  GPO: "Workstation Security"                 │
  │                                              │
  │  Computer Settings:                          │
  │  • Disable USB storage                       │
  │  • Enable Windows Firewall                   │
  │  • Set screen lock to 5 minutes              │
  │                                              │
  │  User Settings:                              │
  │  • Map H: drive to \\fileserver\home$        │
  │  • Set default browser to Edge               │
  │  • Remove Control Panel access               │
  │                                              │
  │  Linked to: OU=Workstations,DC=corp,DC=com  │
  └──────────────────────────────────────────────┘
```

---

### GPO Processing Order

**What:** GPOs are applied in a specific order. Last applied wins (most specific overrides).

```
  L → S → D → OU  (order of application)
  
  Local policy (on the machine itself)
  → Site policy (AD Site)
  → Domain policy (corp.com)
  → OU policy (OU=Workstations)
  → Child OU policy (OU=IT under Workstations)
  
  The LAST policy applied WINS for conflicting settings.
```

---

### GPO Inheritance / Blocking / Enforcement

| Feature | What it does |
|---------|-------------|
| **Inheritance** | Child OUs automatically inherit parent OU's GPOs |
| **Block Inheritance** | Child OU blocks ALL GPOs from parent (nuclear option) |
| **Enforced** | Parent GPO CANNOT be blocked — overrides block inheritance |

---

### WMI Filters

**What:** Apply a GPO only to machines matching a WMI query. "Apply this GPO only to laptops" or "only to machines with >8GB RAM."

```
  SELECT * FROM Win32_Battery  → filters to laptops only
  SELECT * FROM Win32_OperatingSystem WHERE Version LIKE "10.%" → Win10 only
```

---

### Loopback Processing

**What:** Apply USER settings based on the COMPUTER's OU instead of the user's OU. Used for kiosk/terminal servers where you want all users to get the same experience.

---

### SYSVOL

**What:** A shared folder on every DC that stores GPO files, logon scripts, and policies. Replicated between all DCs using DFS-R. Path: `\\corp.com\SYSVOL\corp.com\`.

> ⚠️ **Gotcha:** If SYSVOL replication breaks, GPOs stop updating across DCs. Run `dcdiag /test:sysvolcheck` and check DFS-R event logs.

---

### DFS-R (Distributed File System Replication)

**What:** Replicates SYSVOL and other shared folders between DCs. Uses delta compression (only sends changed blocks, not entire files). Replaced FRS (File Replication Service).

---

### AD Replication

**What:** The process of synchronizing directory changes between DCs. Multi-master — any DC can accept writes and replicate to others. Uses USN (Update Sequence Numbers) to track changes.

```
  DC-01: User john.doe password changed (USN 5001)
     │
     ▼ replication
  DC-02: Receives change, updates local copy (USN 5001)
     │
     ▼ replication
  DC-03: Receives change, updates local copy (USN 5001)
```

---

### USN (Update Sequence Number)

**What:** A counter on each DC that increments with every change. Used to track which changes have been replicated. USN rollback (counter goes backwards) = CRITICAL error that corrupts replication.

---

### KCC (Knowledge Consistency Checker)

**What:** An AD process that automatically builds the replication topology. Creates connection objects between DCs to ensure efficient replication. Runs every 15 minutes.

---

### AD-Integrated DNS

**What:** DNS zones stored IN Active Directory instead of in flat files. Benefits: automatic replication to all DCs, secure dynamic updates, no separate DNS replication to manage.

```
  Standard DNS:  Zone stored in file → replicated separately
  AD-Integrated: Zone stored in AD → replicated with AD replication
                 Secure dynamic updates (only domain members can register)
```

---

### SRV Records (AD DNS)

**What:** DNS records that tell clients WHERE to find AD services. Clients query DNS to find DCs, Kerberos, LDAP, and Global Catalog servers.

```
  _ldap._tcp.corp.com       → DC01.corp.com, DC02.corp.com
  _kerberos._tcp.corp.com   → DC01.corp.com, DC02.corp.com
  _gc._tcp.corp.com         → DC01.corp.com (Global Catalog)
  
  Without these SRV records, clients can't find DCs → login fails.
```

---

# 20 — Hybrid Identity & Federation

---

### Entra Connect (formerly Azure AD Connect)

**What:** Syncs on-prem AD DS users, groups, and passwords to Entra ID. Runs on a Windows Server in your on-prem environment. The bridge between on-prem AD and cloud identity.

```
  ┌──────────────┐    sync every    ┌──────────────┐
  │ On-Prem AD   │ ═══30 minutes═══►│ Entra ID     │
  │              │                   │              │
  │ john.doe     │    ──────────►   │ john.doe     │
  │ jane.admin   │    ──────────►   │ jane.admin   │
  │ IT-Admins    │    ──────────►   │ IT-Admins    │
  └──────────────┘    (one-way)     └──────────────┘
```

---

### Entra Cloud Sync

**What:** Lightweight alternative to Entra Connect. Uses a small agent (no full server). Supports multi-forest scenarios. Less features than Entra Connect but simpler to deploy.

| Feature | Entra Connect | Cloud Sync |
|---------|--------------|------------|
| Agent | Full server install | Lightweight agent |
| Multi-forest | Manual config | Native support |
| Writeback | Password, group, device | Password only |
| Exchange hybrid | Full support | Limited |

---

### Password Hash Sync (PHS)

**What:** Hashes of on-prem password hashes are synced to Entra ID. Users log in to cloud services using the same password. Authentication happens IN THE CLOUD — no dependency on on-prem infrastructure.

```
  User logs into M365:
  → Entra ID checks password hash locally
  → No call to on-prem needed
  → Works even if on-prem is down ✓
```

> **FAQ:** *Is PHS secure?* Yes. The hash is re-hashed (hash of a hash). Microsoft can't reverse it. PHS also enables leaked credential detection.

---

### Pass-Through Authentication (PTA)

**What:** Authentication requests are forwarded to on-prem AD in real-time. Password is NEVER stored in the cloud. On-prem AD validates the password and returns the result.

```
  User logs into M365:
  → Entra ID forwards auth request → PTA Agent (on-prem)
  → PTA Agent validates against AD DS
  → Returns success/fail to Entra ID
  
  ⚠️ If on-prem is down → authentication FAILS
```

---

### Federation (ADFS)

**What:** On-prem ADFS (Active Directory Federation Services) handles ALL authentication. Entra ID redirects login requests to your ADFS server. Most complex option — requires ADFS infrastructure (servers, certs, WAP).

```
  PHS:        Cloud validates password (simplest, recommended)
  PTA:        On-prem validates password (real-time, no cloud storage)
  Federation: On-prem ADFS handles everything (most complex)
```

> ⚠️ **Gotcha:** Microsoft recommends PHS as PRIMARY method. It's the most resilient (works when on-prem is down) and enables leaked credential detection.

---

### Seamless SSO

**What:** Users on domain-joined machines signed into AD are automatically signed into Entra ID without entering credentials again. Works with PHS and PTA. Uses Kerberos tickets.

**User experience:** Open browser → navigate to M365 → automatically logged in. No username/password prompt.

---

### Hybrid Entra Join

**What:** Devices registered in BOTH on-prem AD and Entra ID. The device has a computer object in AD AND a device object in Entra ID. Required for Conditional Access policies that check device compliance.

```
  Device identity options:
  ┌────────────────────┬─────────────────────────────────┐
  │ Type               │ Registered in                   │
  ├────────────────────┼─────────────────────────────────┤
  │ Entra Registered   │ Entra ID only (BYOD)           │
  │ Entra Joined       │ Entra ID only (cloud-native)   │
  │ Hybrid Entra Joined│ AD DS + Entra ID (hybrid orgs) │
  └────────────────────┴─────────────────────────────────┘
```

---

### Device Registration

**What:** The process of adding a device to Entra ID. Registered devices get a device identity (certificate), enabling Conditional Access policies to verify device health and compliance.

---

### Cloud Kerberos Trust

**What:** Enables passwordless sign-in (WHfB) for Hybrid Entra Joined devices WITHOUT deploying PKI or key trust infrastructure. Uses Entra ID as the Kerberos trust anchor.

---

### Entra B2B (Business-to-Business)

**What:** Invite external users (partners, vendors) to access your Azure resources and apps. They use THEIR OWN identity (their company's Entra ID, Google, etc.). You control what they can access.

**DevOps example:** A contractor needs access to your Azure DevOps project. Invite them as a B2B guest → they log in with their company email → access only the repos you assign.

---

### Entra B2C (Business-to-Consumer)

**What:** Identity platform for YOUR customers. Build custom sign-up/sign-in flows for your app. Supports social logins (Google, Facebook, Apple), local accounts, and custom policies.

```
  B2B = invite external BUSINESS users (partners, vendors)
  B2C = build login for your app's END USERS (customers)
```

---

### Passwordless Authentication

**What:** Sign in without a password. Uses something you HAVE (phone, security key) + something you ARE (biometric) or KNOW (PIN). More secure than passwords — nothing to phish.

| Method | How it works |
|--------|-------------|
| **FIDO2 Security Key** | Physical USB/NFC key. Tap to authenticate |
| **Windows Hello for Business** | PIN or biometric tied to device TPM |
| **Microsoft Authenticator** | Phone notification → approve + biometric |

---

### FIDO2 Security Keys

**What:** Physical hardware keys (YubiKey, Feitian) for passwordless authentication. Plug in USB or tap NFC → no password needed. Phishing-resistant — the key verifies the website's domain.

---

### Windows Hello for Business (WHfB)

**What:** Replace passwords with PIN or biometric (fingerprint, face) tied to the device's TPM chip. The PIN never leaves the device — it's local, not a network credential.

> **FAQ:** *How is a PIN more secure than a password?* The PIN is tied to ONE device. Even if stolen, it can't be used from another machine. A password works from anywhere.

---

### Microsoft Authenticator (Passwordless)

**What:** Push notification to your phone. Approve the sign-in + provide biometric. No password typed. Number matching prevents accidental approvals (user must type the number shown on screen).

---

### Continuous Access Evaluation (CAE)

**What:** Real-time token revocation. Normally, access tokens are valid for 1 hour — if you disable an account, the user can still access resources until the token expires. CAE revokes tokens within minutes.

```
  Without CAE: User disabled → waits up to 1 hour → access revoked
  With CAE:    User disabled → access revoked in ~2 minutes
```

---

### Token Lifetime

**What:** How long authentication tokens are valid before requiring re-authentication.

| Token | Default lifetime |
|-------|-----------------|
| Access token | 60-90 minutes |
| Refresh token | 90 days (revoked on password change) |
| SAML token | 1 hour |
| ID token | 1 hour |

---

### Verified ID (Entra Verified ID)

**What:** Decentralized identity — issue and verify digital credentials (employment proof, education certificates) using open standards. Users control their own credentials in a digital wallet.

---

# 21 — AD Security, Attacks & Operations

---

### Kerberoasting

**What:** Attack that extracts service account password hashes from Kerberos service tickets. Any domain user can request a TGS for any SPN → crack the hash offline.

```
  Attack flow:
  1. Attacker (any domain user) requests TGS for SPN MSSQLSvc/SQL01
  2. DC returns TGS encrypted with the service account's hash
  3. Attacker extracts the hash from the ticket
  4. Attacker cracks the hash offline (hashcat, john)
  5. Attacker now has the service account password
```

**Defenses:** Use gMSAs (Group Managed Service Accounts) with 120+ character auto-rotating passwords. Set long complex passwords for legacy service accounts. Monitor for mass TGS requests.

---

### AS-REP Roasting

**What:** Attack targeting accounts with "Do not require Kerberos pre-authentication" enabled. Attacker requests AS-REP for the account → gets an encrypted blob → cracks offline.

**Defense:** Ensure ALL accounts have Kerberos pre-authentication ENABLED (it's on by default — someone disabled it).

---

### Golden Ticket

**What:** A forged TGT created using the KRBTGT account's password hash. Grants UNRESTRICTED access to EVERYTHING in the domain. Valid for 10 years by default. The ultimate AD compromise.

```
  How attacker gets KRBTGT hash:
  1. Compromises a Domain Controller
  2. Runs DCSync to extract KRBTGT hash
  
  Defense:
  • Reset KRBTGT password TWICE (old hash stays valid for one rotation)
  • Protect DCs — physical and network isolation
  • Monitor for anomalous TGT usage
```

> ⚠️ **Gotcha:** Resetting KRBTGT once leaves the old hash valid (AD keeps N-1 hash). You must reset TWICE with a gap of at least 10 hours.

---

### Silver Ticket

**What:** A forged service ticket for a SPECIFIC service. Uses the service account's hash (not KRBTGT). More targeted than Golden Ticket — access to one service, not the entire domain.

---

### Pass-the-Hash (PtH)

**What:** Attacker steals the NTLM hash from a compromised machine's memory (using Mimikatz) and uses it to authenticate as that user WITHOUT knowing the password.

```
  Attacker on Workstation-A:
  1. Extracts NTLM hash of admin from memory (Mimikatz)
  2. Uses hash to authenticate to Server-B as admin
  3. No password needed — the hash IS the credential
```

**Defenses:** Disable NTLM where possible. Use Credential Guard. Don't log into workstations with Domain Admin accounts.

---

### Pass-the-Ticket (PtT)

**What:** Attacker steals Kerberos tickets (TGT or TGS) from memory and injects them into their own session. Similar to PtH but for Kerberos.

---

### DCSync

**What:** Attacker with "Replicating Directory Changes" permission mimics a DC and requests password hashes for ANY account via the replication protocol. Doesn't require access to a DC.

**Defense:** Only Domain Controllers should have replication permissions. Audit these permissions regularly. Alert on non-DC replication requests.

---

### LAPS (Local Administrator Password Solution)

**What:** Automatically manages and rotates the local administrator password on domain-joined machines. Each machine gets a UNIQUE, random password stored in AD (encrypted in Windows LAPS v2).

```
  Without LAPS:
  All 500 workstations have the same local admin password "P@ssw0rd!"
  → Attacker compromises one → has admin on ALL 500

  With LAPS:
  WS-001: local admin = "j8#kL2@mN!9pQ"
  WS-002: local admin = "xR5$vB7&cF3nY"
  Each unique, auto-rotated every 30 days.
```

---

### gMSA (Group Managed Service Account)

**What:** Service accounts with auto-managed 120-character passwords that rotate every 30 days. No human knows the password. Used for services, scheduled tasks, IIS app pools.

> ⚠️ **Gotcha:** gMSAs require Windows Server 2012+ DCs and the KDS root key. Run `Add-KdsRootKey` before creating gMSAs.

---

### Tiered Administration Model

**What:** Separate admin accounts into tiers to prevent credential theft escalation. Tier 0 credentials NEVER touch Tier 1/2 machines.

```
  Tier 0: Domain Controllers, Entra Connect, AD DS
          (highest privilege — most protected)
  Tier 1: Member servers (SQL, file, app servers)
  Tier 2: Workstations, end-user devices

  Rules:
  • Tier 0 admins ONLY log into Tier 0 machines
  • Tier 1 admins NEVER log into Tier 2 workstations
  • If attacker compromises Tier 2, they can't reach Tier 0
```

---

### PAW (Privileged Access Workstation)

**What:** A hardened, dedicated machine used ONLY for administrative tasks. No email, no web browsing, no USB. Physically or logically isolated from regular workstations.

**DevOps example:** Sysadmin uses their regular laptop for email/Teams. For AD admin tasks, they switch to a locked-down PAW that can only reach DCs.

---

### Credential Guard

**What:** Windows security feature that isolates credential hashes in a hardware-backed virtual container. Mimikatz can't extract NTLM hashes or Kerberos tickets from memory.

---

### AD CS (Active Directory Certificate Services)

**What:** On-prem Certificate Authority for issuing certificates (user auth, code signing, TLS). If misconfigured, AD CS templates can be exploited for domain takeover (ESC1-ESC8 attacks).

> ⚠️ **Gotcha:** AD CS misconfigurations are one of the TOP attack vectors in modern AD environments. Audit certificate templates for overly permissive enrollment permissions.

---

### Trusts

**What:** A relationship between two AD domains/forests that allows users in one to access resources in the other. The TRUSTING domain allows access. The TRUSTED domain's users get access.

```
  Domain A ───trusts──► Domain B
  
  Users in Domain B CAN access resources in Domain A
  Users in Domain A CANNOT access resources in Domain B
  (unless B also trusts A = two-way trust)
```

---

### Trust Types

| Type | Direction | Scope |
|------|----------|-------|
| **Parent-Child** | Two-way, transitive | Automatic between parent/child domains |
| **Tree-Root** | Two-way, transitive | Automatic between trees in same forest |
| **Forest** | One or two-way | Cross-forest. Manual. Non-transitive |
| **External** | One or two-way | To a single domain in another forest |
| **Shortcut** | One or two-way | Speeds up auth between distant child domains |
| **Realm** | One or two-way | To non-Windows Kerberos realm (Linux/MIT) |

---

### SID Filtering

**What:** Security mechanism that removes foreign SIDs from authentication tokens when crossing trust boundaries. Prevents an attacker in Forest B from injecting Domain Admin SID of Forest A into their token.

---

### Selective Authentication

**What:** When creating a forest trust, you can limit WHICH users in the trusted forest can access WHICH resources in the trusting forest. More secure than allowing blanket access.

---

### dcdiag

**What:** THE diagnostic tool for AD health. Tests DNS, replication, FSMO, SYSVOL, connectivity, and more.

```powershell
# Run all tests
dcdiag /v

# Common tests
dcdiag /test:dns          # DNS health
dcdiag /test:replications # Replication status
dcdiag /test:sysvolcheck  # SYSVOL/DFS-R health
dcdiag /test:fsmocheck    # FSMO role holder status
```

---

### repadmin

**What:** AD replication monitoring and management tool. Check replication status, force sync, view replication partners.

```powershell
repadmin /replsummary          # Replication health summary
repadmin /showrepl DC01        # Show replication partners for DC01
repadmin /syncall /APed        # Force sync all partitions, all DCs
repadmin /queue DC01           # Check replication queue
```

---

### ntdsutil

**What:** AD database management tool. Metadata cleanup (remove dead DCs), FSMO role seizure, authoritative restore, AD snapshot management.

```powershell
# Seize FSMO role (when original holder is permanently offline)
ntdsutil → roles → connections → connect to server DC02
→ seize PDC

# Metadata cleanup (remove a decommissioned DC)
ntdsutil → metadata cleanup → select operation target
→ remove selected server
```

---

### AD Hardening Checklist

```
  ✅ Enable LAPS for local admin passwords
  ✅ Use gMSAs for service accounts
  ✅ Implement tiered administration (Tier 0/1/2)
  ✅ Disable NTLM where possible, enforce NTLMv2 minimum
  ✅ Enable Credential Guard on all admin machines
  ✅ Protect Domain Controllers (dedicated, no other workloads)
  ✅ Reset KRBTGT password twice per year
  ✅ Audit AD CS templates for misconfigurations
  ✅ Enable AD Recycle Bin
  ✅ Monitor for Kerberoasting (mass TGS requests)
  ✅ Use PAWs for privileged administration
  ✅ Enable SID Filtering on all trusts
  ✅ Run dcdiag and repadmin regularly
  ✅ Backup AD DS (System State) daily
```

---

> **🎉 Glossary Complete! 21/21 batches. ~4,850+ lines. 500+ terms covered.**

