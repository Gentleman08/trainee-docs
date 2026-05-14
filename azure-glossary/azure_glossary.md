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

<!-- BATCH 13 STARTS HERE -->
