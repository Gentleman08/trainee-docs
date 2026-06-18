# 🔷 Batch 2: Security, Identity & Advanced Networking

> **Level:** Beginner–Intermediate | **Estimated Total Time:** 12–18 days | **Scenarios:** 5 (numbered 6–10)
>
> Security and networking are where real-world Azure projects succeed or fail. This batch covers identity management (Entra ID), secrets management (Key Vault), network security (Firewall, WAF), traffic distribution (Load Balancer, App Gateway, Front Door), and hybrid connectivity (VPN, ExpressRoute).

---

## 📑 Table of Contents

- [Scenario 6: Azure Active Directory (Entra ID) Deep Dive](#scenario-6-azure-active-directory-entra-id-deep-dive)
- [Scenario 7: Azure Key Vault Mastery](#scenario-7-azure-key-vault-mastery)
- [Scenario 8: Azure Firewall & Network Security](#scenario-8-azure-firewall--network-security)
- [Scenario 9: Load Balancing & Traffic Management](#scenario-9-load-balancing--traffic-management)
- [Scenario 10: VPN Gateway & ExpressRoute](#scenario-10-vpn-gateway--expressroute)

---

## Scenario 6: Azure Active Directory (Entra ID) Deep Dive

### 🎯 Objective

Understand Azure's identity platform end-to-end. Configure authentication and authorization for applications using OAuth 2.0 / OIDC, manage users and groups at scale, implement Conditional Access, and integrate Managed Identities so your code never stores credentials.

### 📦 App Description

**A multi-tenant SaaS application (Node.js or .NET)** with social login (Google, GitHub), role-based dashboards (Admin, Editor, Viewer), and an admin panel for tenant management. This tests every auth flow — client credentials for service-to-service, authorization code for users, on-behalf-of for downstream APIs.

### 🏗️ Architecture Diagram

```
                     ┌──────────────────────┐
                     │     USERS            │
                     │  (Tenant A & B)      │
                     └──────────┬───────────┘
                                │ Login (OIDC)
                     ┌──────────▼───────────┐
                     │    MICROSOFT         │
                     │    ENTRA ID          │
                     │                      │
                     │  ┌────────────────┐  │
                     │  │ App Registration│  │
                     │  │ "SaaS App"     │  │
                     │  │                │  │
                     │  │ Redirect URIs  │  │
                     │  │ App Roles:     │  │
                     │  │  • Admin       │  │
                     │  │  • Editor      │  │
                     │  │  • Viewer      │  │
                     │  │                │  │
                     │  │ API Permissions│  │
                     │  │  • User.Read   │  │
                     │  │  • Graph API   │  │
                     │  └────────────────┘  │
                     │                      │
                     │  Conditional Access: │
                     │  • MFA for Admins   │
                     │  • Block legacy auth│
                     │  • Named locations  │
                     └──────────┬───────────┘
                                │ Token (JWT)
                     ┌──────────▼───────────┐
                     │    WEB APP           │
                     │  (App Service)       │
                     │                      │
                     │  Validates token     │
                     │  Checks app roles    │
                     │  Routes to dashboard │
                     │                      │
                     │  ┌────────────────┐  │
                     │  │ System-Assigned │  │
                     │  │ Managed Identity│ │──►  Key Vault
                     │  └────────────────┘  │──►  SQL Database
                     └──────────────────────┘──►  Storage
```

### 📋 Pre-requisites

- Azure AD tenant (comes with every Azure subscription)
- Global Administrator or Application Administrator role
- A web app ready to integrate with MSAL (Microsoft Authentication Library)
- Understanding of OAuth 2.0 basics

### ✅ Hands-on Tasks

#### Part A: Tenant & User Management

- [ ] Verify your Azure AD tenant and note the tenant ID
- [ ] Add a custom domain to your tenant (or use the default `.onmicrosoft.com`)
- [ ] Create test users: `admin@`, `editor@`, `viewer@`
- [ ] Create security groups: `grp-admins`, `grp-editors`, `grp-viewers`
- [ ] Create a dynamic group with rule: `user.department -eq "Engineering"`
- [ ] Invite a guest user (B2B collaboration)

```bash
# Create a user
az ad user create \
  --display-name "Test Admin" \
  --user-principal-name admin@yourtenant.onmicrosoft.com \
  --password "P@$$w0rd1234!" \
  --force-change-password-next-sign-in false

# Create a group
az ad group create --display-name "grp-admins" --mail-nickname "grp-admins"

# Add user to group
az ad group member add --group "grp-admins" --member-id <user-object-id>
```

> ⚠️ **DevOps Gotcha:** Dynamic groups can take up to **24 hours** to fully evaluate their membership rules, especially in large tenants. Don't rely on dynamic group membership being immediate in CI/CD pipelines. If you need instant group membership, use assigned (static) groups.

#### Part B: App Registrations & OAuth Flows

- [ ] Register an application in Azure AD (App Registration)
- [ ] Configure redirect URIs for your web app
- [ ] Set up **Authorization Code Flow** (for user sign-in):
  - Configure web platform with redirect URI
  - Add API permissions: `User.Read`, `openid`, `profile`
  - Grant admin consent
- [ ] Set up **Client Credentials Flow** (for service-to-service):
  - Create a client secret (or certificate)
  - Request token via `POST /oauth2/v2.0/token` with `grant_type=client_credentials`
- [ ] Set up **On-Behalf-Of Flow** (API calling another API as the user):
  - Expose an API scope
  - Configure downstream API permissions

```bash
# Register app
az ad app create \
  --display-name "SaaS App" \
  --web-redirect-uris "https://myapp.azurewebsites.net/auth/callback" \
  --sign-in-audience "AzureADMultipleOrgs"

# Create client secret
az ad app credential reset --id <app-id> --append
```

> ⚠️ **DevOps Gotcha:** Client secrets have a maximum lifetime (Azure AD recommends 6 months, max 2 years). When a secret expires, your app SILENTLY STOPS WORKING. Set calendar reminders or use certificates instead (which also expire but can be auto-rotated). Better yet, use **Managed Identity** to avoid secrets entirely.

#### Part C: App Roles & Claims

- [ ] Define app roles in the app manifest: `Admin`, `Editor`, `Viewer`
- [ ] Assign users/groups to app roles via Enterprise Applications
- [ ] Configure your app to read the `roles` claim from the JWT token
- [ ] Implement role-based access control in your app's middleware
- [ ] Configure groups claim to include group memberships in tokens

```json
// App manifest - appRoles section
"appRoles": [
  {
    "id": "unique-guid-1",
    "allowedMemberTypes": ["User"],
    "displayName": "Admin",
    "description": "Full administrative access",
    "value": "Admin",
    "isEnabled": true
  },
  {
    "id": "unique-guid-2",
    "allowedMemberTypes": ["User"],
    "displayName": "Editor",
    "value": "Editor",
    "isEnabled": true
  }
]
```

> ⚠️ **DevOps Gotcha:** If a user belongs to more than **200 groups**, Azure AD stops including groups in the token and instead includes a `_claim_names` field with a URL to fetch groups via Graph API. This "groups overage claim" breaks apps that expect groups directly in the token. Always code defensively — check for overage and call Graph API as fallback.

#### Part D: Service Principals vs Managed Identities

- [ ] Understand the relationship: App Registration → Service Principal (in each tenant)
- [ ] Create a service principal for automation: `az ad sp create-for-rbac`
- [ ] Enable **System-Assigned Managed Identity** on an App Service
- [ ] Enable **User-Assigned Managed Identity** and attach it to multiple resources
- [ ] Use Managed Identity to access Key Vault from code (no secrets needed!)

```bash
# System-Assigned MI
az webapp identity assign --name myapp --resource-group myrg

# User-Assigned MI
az identity create --name mi-shared-dev --resource-group myrg
az webapp identity assign --name myapp --resource-group myrg \
  --identities /subscriptions/<sub>/resourceGroups/myrg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/mi-shared-dev
```

```
┌───────────────────────────────────────────────────────────┐
│ SERVICE PRINCIPAL vs MANAGED IDENTITY                     │
│                                                           │
│ Service Principal:                                        │
│   • You manage the credential (secret/cert)              │
│   • Can be used from anywhere (on-prem, other clouds)    │
│   • Credential rotation is YOUR responsibility           │
│   • Use for: CI/CD pipelines, external integrations      │
│                                                           │
│ Managed Identity:                                         │
│   • Azure manages the credential (auto-rotated)          │
│   • Only works from Azure resources                      │
│   • No secrets to leak or rotate                         │
│   • System-Assigned: tied to ONE resource lifecycle      │
│   • User-Assigned: shared across resources, YOU manage   │
│   • Use for: App-to-Azure-service communication          │
└───────────────────────────────────────────────────────────┘
```

#### Part E: Conditional Access Policies

- [ ] Create a policy: Require MFA for all Admin role users
- [ ] Create a policy: Block legacy authentication protocols
- [ ] Create a policy: Require compliant devices for production apps
- [ ] Configure Named Locations (trusted IPs for your office)
- [ ] Test policies using "What If" tool
- [ ] Configure sign-in risk policies (requires P2 license or trial)

> ⚠️ **DevOps Gotcha:** Conditional Access policies can lock out your service principals! If you create a policy like "Require MFA for all users" without excluding service principals, your CI/CD pipelines, background jobs, and API integrations will BREAK because service principals can't do MFA. Always exclude service principals and Managed Identities from user-facing CA policies.

#### Part F: Azure AD B2C (Customer Identity)

- [ ] Create a B2C tenant (separate from your main tenant)
- [ ] Configure a sign-up/sign-in user flow
- [ ] Add identity providers: local accounts, Google, GitHub
- [ ] Customize the login page branding
- [ ] Configure custom attributes on user profiles
- [ ] Understand B2C vs B2B: B2C = customer-facing, B2B = partner/employee

#### Part G: Privileged Identity Management (PIM)

- [ ] Enable PIM for Azure AD roles (requires P2 license or trial)
- [ ] Make the Global Admin role "eligible" instead of "permanent"
- [ ] Activate the role just-in-time with justification and approval
- [ ] Set maximum activation duration (e.g., 4 hours)
- [ ] Configure access reviews for stale permissions

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `AADSTS65001`: User consent required | Admin consent not granted | Grant admin consent in portal or via `az ad app permission admin-consent` |
| `AADSTS700016`: App not found in tenant | Multi-tenant app, SP not provisioned | User must consent first, or admin pre-provisions SP |
| Token expired / `401 Unauthorized` | Token lifetime exceeded (default: 1 hour for access tokens) | Implement token refresh; use MSAL's silent acquisition |
| Groups claim missing from token | Groups overage (>200 groups) | Handle overage claim; call Graph API for group list |
| Managed Identity returns `403` | RBAC role not assigned to the MI | Assign appropriate role: `az role assignment create --assignee <mi-principal-id>` |
| B2C login page shows default Microsoft branding | Custom branding not configured | Configure company branding in B2C tenant settings |
| CA policy blocks service principal | Policy applies to "All users" including SPs | Exclude service principals from the CA policy |

### 💰 Cost Tips

- Azure AD Free: basic user/group management, app registrations — **FREE**
- Azure AD P1 (~$6/user/month): Conditional Access, dynamic groups, self-service password reset
- Azure AD P2 (~$9/user/month): PIM, Identity Protection, access reviews
- B2C: first 50,000 authentications/month FREE, then $0.00325/auth
- Use trial P2 licenses for learning PIM/Identity Protection
- Managed Identities: **completely FREE**

### ✔️ Verification Checklist

- [ ] Users can sign in to your app using Azure AD
- [ ] Token contains correct app roles (`Admin`, `Editor`, `Viewer`)
- [ ] Role-based dashboards show different content per role
- [ ] MFA is enforced for Admin users (CA policy)
- [ ] Managed Identity can access Key Vault without any secrets in code
- [ ] Guest user can sign in via B2B collaboration
- [ ] PIM activation works with justification + time limit
- [ ] Client credentials flow works for service-to-service API calls

### 🔍 Behind the Scenes

- **Azure AD** is a globally distributed identity service running across 30+ regions. Token issuance happens at the nearest Azure AD datacenter.
- **JWT tokens** are self-contained — the resource (API) validates the token's signature using Azure AD's public keys (from the OIDC metadata endpoint), without calling back to Azure AD. This is why token revocation isn't instant.
- **Managed Identity** works via the Azure Instance Metadata Service (IMDS). Your code calls `http://169.254.169.254/metadata/identity/oauth2/token`, and Azure's fabric controller injects a token. The private key never leaves Azure's infrastructure.
- **Conditional Access** is evaluated at token issuance time. If a policy requires MFA, the user must complete MFA before Azure AD issues the token. The policy is NOT checked when the token is used — only when issued (or refreshed).
- **App Registrations** are global (exist in your home tenant), but **Service Principals** are local to each tenant. When a user in Tenant B consents to your multi-tenant app, a Service Principal is created in Tenant B.

---

## Scenario 7: Azure Key Vault Mastery

### 🎯 Objective

Centralize all secrets, keys, and certificates in Key Vault. Implement zero-credential applications using Managed Identity. Master access control, rotation, backup, and Private Endpoint integration.

### 📦 App Description

**A secrets-heavy microservices application** that connects to Azure SQL, Cosmos DB, Storage Account, and a third-party API. Every single credential must come from Key Vault — no connection strings in code or config files. The app uses Managed Identity to access Key Vault.

### 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    KEY VAULT                              │
│              "kv-myapp-prod-001"                          │
│                                                          │
│  Access: RBAC (recommended)                              │
│  Firewall: VNet rules + Private Endpoint                 │
│  Soft Delete: Enabled (90 days)                          │
│  Purge Protection: Enabled                               │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐           │
│  │ SECRETS  │  │  KEYS    │  │ CERTIFICATES │           │
│  │          │  │          │  │              │           │
│  │ db-conn  │  │ encrypt- │  │ wildcard-    │           │
│  │ api-key  │  │ key-rsa  │  │ cert.pfx     │           │
│  │ redis-pw │  │          │  │ (auto-renew) │           │
│  │ cosmos-  │  │ signing- │  │              │           │
│  │ key      │  │ key-ec   │  │ api-cert     │           │
│  └──────────┘  └──────────┘  └──────────────┘           │
│                                                          │
│  EVENT GRID ──► Logic App (rotation alert)               │
└──────────────────┬───────────────────────────────────────┘
                   │ Private Endpoint (10.1.3.10)
                   │
    ┌──────────────┴──────────────────────────────┐
    │                 CONSUMERS                    │
    │                                              │
    │  App Service ──► Managed Identity ──► KV    │
    │  Azure Function ──► Managed Identity ──► KV │
    │  AKS Pod ──► Workload Identity ──► KV       │
    │  DevOps Pipeline ──► Service Principal ──► KV│
    └──────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Resource group and VNet from Batch 1
- Azure AD understanding from Scenario 6
- An app with database and API dependencies

### ✅ Hands-on Tasks

#### Part A: Key Vault Creation & Access Model

- [ ] Create a Key Vault with RBAC authorization (recommended over access policies)
- [ ] Understand Access Policies vs Azure RBAC:

```
┌───────────────────────────────────────────────────────────┐
│ ACCESS POLICIES vs RBAC                                    │
│                                                           │
│ Access Policies (legacy):                                 │
│   • All-or-nothing per identity                          │
│   • Max 1024 policies per vault                           │
│   • No fine-grained audit of WHO accessed WHAT            │
│   • Simpler for small teams                              │
│                                                           │
│ Azure RBAC (recommended):                                 │
│   • Granular roles: Secret Reader, Key Operator, etc.    │
│   • Consistent with all other Azure RBAC                  │
│   • Supports Conditional Access                          │
│   • Full audit trail with Azure Activity Log             │
│   • Can scope to individual secrets/keys                  │
└───────────────────────────────────────────────────────────┘
```

```bash
az keyvault create \
  --name kv-myapp-prod-001 \
  --resource-group rg-portfolio-dev-eastus \
  --location eastus \
  --enable-rbac-authorization true \
  --enable-soft-delete true \
  --retention-days 90 \
  --enable-purge-protection true
```

- [ ] Assign yourself "Key Vault Administrator" role
- [ ] Assign your app's Managed Identity "Key Vault Secrets User" role
- [ ] Understand the built-in KV roles: Administrator, Secrets Officer, Secrets User, Crypto Officer, Certificates Officer

> ⚠️ **DevOps Gotcha:** When you switch from Access Policies to RBAC, all existing access policies are IGNORED — not deleted, just ignored. This means anyone who had access via policies immediately loses access until RBAC roles are assigned. Plan the migration carefully and assign RBAC roles BEFORE switching.

#### Part B: Secrets Management

- [ ] Create secrets for all app dependencies: DB connection strings, API keys, Redis passwords
- [ ] Create a new version of a secret (rotate a password)
- [ ] Reference a specific secret version vs latest version
- [ ] Enable secret expiration dates and set alerts
- [ ] List all versions of a secret
- [ ] Implement automated secret rotation using Azure Functions + Event Grid

```bash
# Create a secret
az keyvault secret set --vault-name kv-myapp-prod-001 --name "db-connection" \
  --value "Server=mydb.database.windows.net;Database=myapp;..."

# Set expiration
az keyvault secret set-attributes --vault-name kv-myapp-prod-001 --name "db-connection" \
  --expires "2025-06-01T00:00:00Z"

# Get latest version
az keyvault secret show --vault-name kv-myapp-prod-001 --name "db-connection"

# List all versions
az keyvault secret list-versions --vault-name kv-myapp-prod-001 --name "db-connection"
```

> ⚠️ **DevOps Gotcha:** Key Vault has a **throttling limit of 4000 transactions per vault per 10 seconds** (for standard vaults). If your app makes too many calls to Key Vault (e.g., fetching a secret on every HTTP request), you'll get `429 Too Many Requests`. Cache secrets locally with a short TTL (5-15 minutes) and implement retry with exponential backoff.

#### Part C: Keys & Certificates

- [ ] Create an RSA-2048 key for data encryption
- [ ] Create an EC key for digital signing
- [ ] Perform encrypt/decrypt and sign/verify operations using the API
- [ ] Create a self-signed certificate for testing
- [ ] Import a CA-signed certificate
- [ ] Configure auto-renewal for certificates (with DigiCert or Let's Encrypt)

#### Part D: Key Vault References in App Service

- [ ] Configure App Service to use Key Vault references for app settings:
  - `@Microsoft.KeyVault(VaultName=kv-myapp-prod-001;SecretName=db-connection)`
- [ ] Enable System-Assigned Managed Identity on App Service
- [ ] Grant the MI "Key Vault Secrets User" role
- [ ] Verify the reference resolves correctly in Kudu Environment tab

> ⚠️ **DevOps Gotcha:** Key Vault references in App Service resolve at **app startup** and when settings are refreshed (can take up to 24 hours for automatic refresh). If you rotate a secret in Key Vault, your app won't pick up the new value until it restarts or the reference refreshes. To force immediate pickup: restart the app or touch any app setting to trigger a refresh.

#### Part E: Key Vault Networking & Security

- [ ] Configure Key Vault firewall: allow access from specific VNets only
- [ ] Create a Private Endpoint for Key Vault
- [ ] Set up the Private DNS Zone: `privatelink.vaultcore.azure.net`
- [ ] Disable public access entirely
- [ ] Test: verify KV is accessible from VNet but NOT from public internet

#### Part F: Soft Delete & Purge Protection

- [ ] Delete a secret — observe it goes to "soft-deleted" state
- [ ] Recover the soft-deleted secret
- [ ] Purge a soft-deleted secret (permanently delete — only if purge protection allows)
- [ ] Try to create a new Key Vault with the same name as a soft-deleted vault — watch it fail!

> ⚠️ **DevOps Gotcha:** Soft delete is enabled by default and CANNOT be disabled on new vaults. Purge protection, once enabled, CANNOT be disabled. If you soft-delete a Key Vault, its name is globally reserved for the retention period (default 90 days). Your Terraform/Bicep deployments will FAIL with "VaultAlreadyExists" if you try to recreate a vault with the same name. Either purge the deleted vault or use a different name.

#### Part G: Backup & Disaster Recovery

- [ ] Backup individual secrets/keys/certificates to a local file
- [ ] Restore a backed-up secret to a different Key Vault (must be same subscription + geography)
- [ ] Understand: there's no built-in vault-level backup — you must backup items individually

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `AccessDenied` from Managed Identity | RBAC role not assigned or wrong scope | Verify role assignment with `az role assignment list` |
| `SecretNotFound` | Secret name typo or wrong vault | Double-check vault name and secret name (case-sensitive!) |
| `429 Too Many Requests` | Throttling — too many KV calls | Cache secrets locally; implement retry with backoff |
| Vault name conflict after deletion | Soft-deleted vault holding the name | Purge: `az keyvault purge --name <vault>` |
| Private Endpoint not resolving | Missing Private DNS Zone or VNet link | Create `privatelink.vaultcore.azure.net` zone and link |
| Key Vault reference shows raw `@Microsoft.KeyVault(...)` | MI not configured or permission missing | Check MI exists and has `Key Vault Secrets User` role |
| Certificate auto-renewal failed | CA integration misconfigured | Check CA settings; verify DNS validation records |

### 💰 Cost Tips

- Secrets operations: $0.03 per 10,000 operations (very cheap)
- Software-protected keys: $0.03 per 10,000 operations
- HSM-protected keys: $1–5 per key per month + $0.03 per operation
- Certificates: free to store, operations charged per call
- Private Endpoint: ~$7.50/month
- **Total for learning:** <$5/month

### ✔️ Verification Checklist

- [ ] All application secrets are in Key Vault (none in code or config)
- [ ] App Service successfully resolves KV references
- [ ] Managed Identity has correct RBAC roles
- [ ] Key Vault firewall blocks public access
- [ ] Private Endpoint resolves from within VNet
- [ ] Soft delete recovery works
- [ ] Secret rotation updates the app (after restart)

### 🔍 Behind the Scenes

- **Key Vault** runs as a dedicated Azure service backed by FIPS 140-2 validated HSMs. Even "software-protected" keys are stored in HSMs at rest — the difference is whether crypto operations happen in the HSM (premium) or in software.
- **Managed Identity tokens** are issued by Azure AD's token service. When your app calls Key Vault with an MI token, KV validates the token with Azure AD and checks RBAC roles before returning the secret.
- **Soft delete** works by moving items to a hidden "deleted" state within the vault. They're not actually destroyed until either: (a) the retention period expires, or (b) you explicitly purge them (if purge protection is off).
- **Private Endpoints** for Key Vault create a NIC in your subnet with a private IP. All Key Vault traffic from your VNet goes to this private IP, bypassing the public endpoint entirely.

---

## Scenario 8: Azure Firewall & Network Security

### 🎯 Objective

Implement defense-in-depth network security: Azure Firewall for network-level control, WAF for application-level protection, DDoS protection, and Private Link to eliminate public internet exposure for backend services.

### 📦 App Description

**A public-facing web application with an API backend and database**, where the API and database are completely private — ZERO public internet exposure. Only the Azure Firewall and Application Gateway face the internet. All internal traffic is inspected and logged.

### 🏗️ Architecture Diagram

```
                         INTERNET
                             │
                ┌────────────┴────────────┐
                │    Azure Front Door     │
                │    (Global WAF + CDN)   │
                └────────────┬────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────┐
│                    HUB VNet (10.0.0.0/16)                      │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              AZURE FIREWALL                           │      │
│  │         "fw-hub-prod-eastus"                          │      │
│  │                                                       │      │
│  │  RULE PROCESSING ORDER:                               │      │
│  │  1. DNAT Rules (inbound NAT)                          │      │
│  │  2. Network Rules (L3/L4)                             │      │
│  │  3. Application Rules (L7 FQDN-based)                 │      │
│  │                                                       │      │
│  │  DNAT: Internet:443 → App Gateway Private IP          │      │
│  │  Network: Allow spoke-to-spoke on specific ports      │      │
│  │  Application: Allow *.microsoft.com, *.ubuntu.com     │      │
│  │                                                       │      │
│  │  Threat Intelligence: Alert & Deny                    │      │
│  └──────────────────────────────────────────────────────┘      │
│                                                                │
│  ┌──────────────────────────────────────┐                      │
│  │  APPLICATION GATEWAY + WAF v2        │                      │
│  │  "agw-prod-eastus"                   │                      │
│  │                                      │                      │
│  │  WAF Mode: Prevention                │                      │
│  │  Rule Set: OWASP 3.2                 │                      │
│  │  Custom Rules: Block SQL injection   │                      │
│  │  Backend Pool: App Service (Private)  │                      │
│  └──────────────────────────────────────┘                      │
└────────────────────────────────┬───────────────────────────────┘
                                 │ VNet Peering
┌────────────────────────────────┴───────────────────────────────┐
│                    SPOKE VNet (10.1.0.0/16)                     │
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ snet-app       │  │ snet-pe        │  │ snet-data      │    │
│  │ App Service    │  │ Private        │  │ SQL DB         │    │
│  │ (VNet Int.)    │  │ Endpoints      │  │ (Private EP)   │    │
│  │ NO public IP   │  │ for PaaS       │  │ NO public IP   │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                │
│  UDR: 0.0.0.0/0 → Azure Firewall (forced tunneling)          │
└────────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Azure Firewall Deployment

- [ ] Create Azure Firewall (Standard SKU) in the hub VNet
- [ ] Understand rule types and processing order (DNAT → Network → Application)
- [ ] Create DNAT rule: NAT inbound HTTPS to App Gateway
- [ ] Create Network rules: Allow spoke-to-spoke on port 1433 (SQL)
- [ ] Create Application rules: Allow outbound to `*.microsoft.com`, `*.ubuntu.com`
- [ ] Enable Threat Intelligence filtering (Alert & Deny mode)
- [ ] Create a Firewall Policy for centralized management

```bash
# Create Firewall
az network firewall create \
  --name fw-hub-prod-eastus \
  --resource-group rg-hub-prod-eastus \
  --location eastus \
  --vnet-name vnet-hub-eastus \
  --sku AZFW_VNet --tier Standard

# Create DNAT rule
az network firewall nat-rule create \
  --firewall-name fw-hub-prod-eastus \
  --resource-group rg-hub-prod-eastus \
  --collection-name "dnat-inbound" \
  --priority 100 --action Dnat \
  --name "allow-https" \
  --protocols TCP \
  --source-addresses "*" \
  --destination-addresses <firewall-public-ip> \
  --destination-ports 443 \
  --translated-address 10.0.4.10 \
  --translated-port 443
```

> ⚠️ **DevOps Gotcha:** Azure Firewall costs **~$912/month minimum** (Standard SKU = $1.25/hour + data processing). This is often the biggest surprise on Azure bills. For learning, deploy it, practice, then DELETE it when done. For production, consider Azure Firewall Basic (~$456/month) if you don't need threat intelligence or TLS inspection.

#### Part B: WAF on Application Gateway

- [ ] Deploy Application Gateway v2 with WAF enabled
- [ ] Set WAF mode to "Detection" first (logs without blocking)
- [ ] Switch to "Prevention" mode (actively blocks attacks)
- [ ] Configure OWASP 3.2 managed rule set
- [ ] Create custom WAF rules (e.g., block requests from specific countries)
- [ ] Create WAF exclusions for legitimate requests that trigger false positives
- [ ] Review WAF logs in Log Analytics

> ⚠️ **DevOps Gotcha:** When you first enable WAF in Prevention mode, be prepared for legitimate traffic to get blocked. APIs that accept JSON with HTML content, file upload endpoints, and health check probes often trigger OWASP rules. ALWAYS start in Detection mode, analyze the logs for false positives, create exclusions, THEN switch to Prevention. Going straight to Prevention in production will cause an outage.

#### Part C: Private Link & Private Endpoints

- [ ] Create Private Endpoints for: Azure SQL, Storage Account, Key Vault
- [ ] Create Private DNS Zones for each:
  - `privatelink.database.windows.net`
  - `privatelink.blob.core.windows.net`
  - `privatelink.vaultcore.azure.net`
- [ ] Link DNS zones to both hub and spoke VNets
- [ ] Disable public access on all PaaS services
- [ ] Verify DNS resolution from a VM: `nslookup mydb.database.windows.net`

```
┌───────────────────────────────────────────────────────────┐
│ PRIVATE ENDPOINT DNS FLOW                                  │
│                                                           │
│  App → nslookup mydb.database.windows.net                │
│    │                                                      │
│    ├──► Azure DNS → CNAME → mydb.privatelink.database... │
│    │                                                      │
│    ├──► Private DNS Zone "privatelink.database..."        │
│    │    A record: mydb → 10.1.3.5 (Private IP)           │
│    │                                                      │
│    └──► Connection to 10.1.3.5 (stays in VNet)           │
│                                                           │
│  Without Private DNS Zone:                                │
│    nslookup resolves to PUBLIC IP → blocked by firewall! │
└───────────────────────────────────────────────────────────┘
```

> ⚠️ **DevOps Gotcha:** The biggest Private Endpoint mistake: forgetting the Private DNS Zone. Without it, your app resolves the PaaS service FQDN to its PUBLIC IP, which gets blocked by the storage/SQL firewall. The app gets a connection timeout with no obvious error message. Always create the DNS zone, link it to ALL VNets that need access, and verify with `nslookup` from INSIDE a VM in the VNet.

#### Part D: DDoS Protection

- [ ] Understand DDoS Protection Basic (free, automatic) vs Standard (paid, advanced)
- [ ] If budget allows, enable DDoS Protection Standard on the VNet
- [ ] Configure DDoS diagnostic logs
- [ ] Review the DDoS protection metrics

#### Part E: Forced Tunneling

- [ ] Create a Route Table with `0.0.0.0/0` → Azure Firewall
- [ ] Associate it with spoke subnets to force ALL outbound traffic through the firewall
- [ ] Test: from a spoke VM, `curl https://example.com` — verify it appears in firewall logs
- [ ] Understand what BREAKS with forced tunneling (Azure services that need direct internet)

> ⚠️ **DevOps Gotcha:** Forced tunneling breaks several Azure services! App Service VNet Integration, Azure Monitor agent, Key Vault access, and AKS all require direct internet routes for certain Azure endpoints. You must create UDR exceptions for Azure service tags (like `AzureMonitor`, `AzureKeyVault`, `AzureActiveDirectory`) or use Service Endpoints. This is the #1 cause of "everything worked until we added the firewall" situations.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| WAF blocks legitimate API requests | OWASP rule false positive | Add exclusion for the specific rule + request field |
| Private Endpoint DNS not resolving | DNS zone not linked to VNet | Link zone with `az network private-dns link vnet create` |
| App can't reach internet through firewall | Missing application rule for the FQDN | Add FQDN to firewall application rules |
| Split-brain DNS: public IP from outside, private from inside | This is EXPECTED behavior | Use conditional forwarders if needed for hybrid scenarios |
| Azure service broken after forced tunneling | Service needs direct internet route | Add UDR exception for Azure service tags |
| Firewall logs show "Deny" but rule exists | Rule priority wrong or rule type wrong | Check: DNAT for inbound, Network for L4, Application for FQDN |
| 502 from App Gateway | Backend health probe failing | Check backend pool health; verify probe path returns 200 |

### 💰 Cost Tips

- **Azure Firewall Standard:** ~$912/month — DELETE when not learning
- **Azure Firewall Basic:** ~$456/month — cheaper alternative
- **Application Gateway v2 WAF:** ~$328/month — DELETE when not learning
- **Private Endpoints:** ~$7.50/month each + data processing
- **DDoS Standard:** ~$2,944/month — use Basic (free) for learning
- **Cost-saving for learning:** Deploy, practice for 2-3 days, then delete all

### ✔️ Verification Checklist

- [ ] Azure Firewall processes inbound and outbound traffic (check logs)
- [ ] WAF blocks known attack patterns (test with OWASP ZAP)
- [ ] All PaaS services accessible ONLY via Private Endpoints
- [ ] Private DNS zones resolve to private IPs from VNet
- [ ] Public access disabled on SQL, Storage, Key Vault
- [ ] Forced tunneling sends all outbound through firewall
- [ ] Firewall diagnostic logs visible in Log Analytics

### 🔍 Behind the Scenes

- **Azure Firewall** runs as a highly available, fully managed service. Behind the scenes, it's a cluster of firewall VMs that auto-scale. It uses Azure's SDN to intercept traffic routed through it via UDRs.
- **WAF** uses the ModSecurity engine (OWASP Core Rule Set) to inspect HTTP requests. Each rule evaluates the request against patterns — SQL injection, XSS, path traversal, etc. Rules have anomaly scores; if the cumulative score exceeds the threshold, the request is blocked.
- **Private Link** works by creating a cross-tenant ARM NIC that maps your private IP to the PaaS service's internal IP. Azure's backbone network handles the routing — traffic never touches the public internet.
- **DNAT rules** modify the destination IP/port of incoming packets. The firewall rewrites the packet header to point to your internal resource and routes it through the VNet fabric.

---

## Scenario 9: Load Balancing & Traffic Management

### 🎯 Objective

Understand all Azure load balancing options, when to use each, and how to combine them. Deploy a globally distributed application with intelligent traffic routing, failover, and caching.

### 📦 App Description

**A globally distributed web application serving users in multiple regions.** Deploy the same app in East US and West Europe, configure intelligent routing so users hit the nearest region, and implement automatic failover when a region goes down.

### 🏗️ Architecture Diagram

```
                         GLOBAL USERS
                    US  │  Europe  │  Asia
                        │          │
              ┌─────────▼──────────▼─────────┐
              │      AZURE FRONT DOOR         │
              │   (Global L7 Load Balancer)   │
              │                               │
              │  • WAF Policy (OWASP 3.2)     │
              │  • Caching (static assets)    │
              │  • SSL offloading             │
              │  • Health probes              │
              │  • Routing: Latency-based     │
              └──────┬────────────────┬───────┘
                     │                │
         ┌───────────▼──┐    ┌───────▼───────────┐
         │  EAST US      │    │  WEST EUROPE      │
         │               │    │                   │
         │  App Gateway  │    │  App Gateway      │
         │  + WAF (Reg.) │    │  + WAF (Reg.)     │
         │       │       │    │       │           │
         │  App Service  │    │  App Service      │
         │  "app-eastus" │    │  "app-westeu"     │
         │       │       │    │       │           │
         │  Azure SQL    │    │  Azure SQL        │
         │  (Primary)    │──► │  (Geo-replica)    │
         │               │    │  (Read-only)      │
         └───────────────┘    └───────────────────┘

┌───────────────────────────────────────────────────────────┐
│ WHEN TO USE WHAT:                                          │
│                                                           │
│ Azure Load Balancer (L4):                                 │
│   TCP/UDP, ultra-fast, VMs/VMSS, internal or public       │
│   Use for: Non-HTTP workloads, database HA, VMSS          │
│                                                           │
│ Application Gateway (L7, regional):                       │
│   HTTP/HTTPS, URL routing, WAF, SSL offload              │
│   Use for: Regional web apps, path-based routing          │
│                                                           │
│ Azure Front Door (L7, global):                            │
│   Global HTTP/HTTPS, caching, WAF, latency routing        │
│   Use for: Global web apps, multi-region                  │
│                                                           │
│ Traffic Manager (DNS, global):                            │
│   DNS-level routing, any protocol, any endpoint           │
│   Use for: Non-HTTP global routing, hybrid scenarios      │
└───────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Azure Load Balancer

- [ ] Create a Standard Public Load Balancer
- [ ] Configure frontend IP, backend pool (2 VMs), health probe (HTTP /health)
- [ ] Create load balancing rules (port 80, port 443)
- [ ] Create inbound NAT rules for SSH to individual VMs
- [ ] Create an Internal Load Balancer for database tier
- [ ] Test: stop one VM, verify traffic fails over to the other

```bash
az network lb create \
  --name lb-web-prod-eastus \
  --resource-group rg-portfolio-dev-eastus \
  --sku Standard \
  --frontend-ip-name lb-frontend \
  --backend-pool-name lb-backend \
  --public-ip-address lb-public-ip
```

> ⚠️ **DevOps Gotcha:** Standard Load Balancer has NO default outbound connectivity. VMs behind a Standard LB cannot reach the internet unless you configure outbound rules, a NAT Gateway, or public IPs on the VMs. This is different from Basic LB, which has implicit outbound. Migrating from Basic to Standard will break outbound connectivity if you don't add explicit outbound rules.

#### Part B: Application Gateway

- [ ] Deploy Application Gateway v2 with WAF
- [ ] Configure URL path-based routing:
  - `/api/*` → API backend pool
  - `/static/*` → Storage Account backend
  - `/*` → Web app backend
- [ ] Configure multi-site hosting (multiple domains on one gateway)
- [ ] Enable SSL termination (offload SSL at the gateway)
- [ ] Configure end-to-end SSL (re-encrypt to backend)
- [ ] Set up connection draining for graceful shutdowns

> ⚠️ **DevOps Gotcha:** Application Gateway health probes are CRITICAL. If your backend app returns anything other than 200-399 on the probe path, the gateway marks it as unhealthy and stops routing traffic to it. The default probe path is `/` — make sure your app returns 200 on `/` or configure a custom probe path like `/health`. A common production outage: app returns a 302 redirect on `/` (to `/login`), gateway sees 302 as unhealthy, all traffic goes to `502 Bad Gateway`.

#### Part C: Azure Front Door

- [ ] Create an Azure Front Door Premium profile
- [ ] Add origins in two regions (East US and West Europe)
- [ ] Configure latency-based routing (route to nearest origin)
- [ ] Enable caching for static content
- [ ] Attach a WAF policy with managed rules
- [ ] Configure custom domain and SSL certificate
- [ ] Test failover: disable one origin, verify traffic routes to the other

#### Part D: Traffic Manager

- [ ] Create a Traffic Manager profile with "Performance" routing
- [ ] Add endpoints in two regions
- [ ] Test with `nslookup <profile>.trafficmanager.net` from different locations
- [ ] Switch to "Priority" routing (active-passive failover)
- [ ] Switch to "Weighted" routing (A/B testing with 80/20 split)
- [ ] Switch to "Geographic" routing (EU users → EU endpoint)

> ⚠️ **DevOps Gotcha:** Traffic Manager works at the DNS level — it returns the IP of the best endpoint. This means DNS TTL affects failover speed. Default TTL is 60 seconds, so failover takes at least 60 seconds. For faster failover, reduce TTL (min 0 seconds) but this increases DNS query volume. Also, client-side DNS caching can extend failover time beyond the TTL.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| 502 Bad Gateway from App Gateway | Backend unhealthy (probe failing) | Check backend health; verify probe path returns 200 |
| No outbound internet from VMs behind Standard LB | Standard LB has no default outbound | Add outbound rules or NAT Gateway |
| Session affinity not working | Sticky sessions not configured | Enable cookie-based affinity on App Gateway |
| Front Door shows old cached content | Cache not purged | Purge cache: `az afd endpoint purge` |
| Traffic Manager failover slow | DNS TTL too high | Reduce TTL; check client DNS caching |
| SSL cert error after App Gateway deployment | Cert not bound to listener | Upload PFX cert and bind to HTTPS listener |
| Health probe causing auth errors (401) | Probe hits authenticated endpoint | Configure probe to hit an unauthenticated `/health` path |

### 💰 Cost Tips

- **Load Balancer Standard:** ~$18/month + rules + data (cheapest)
- **Application Gateway v2:** ~$175/month minimum — DELETE when not using
- **Application Gateway WAF v2:** ~$328/month — DELETE when done
- **Front Door:** ~$35/month base + per-request charges
- **Traffic Manager:** ~$0.54/million queries (very cheap)
- For learning: deploy, test for 1-2 days, delete expensive resources

### ✔️ Verification Checklist

- [ ] Load Balancer distributes traffic evenly across backend VMs
- [ ] App Gateway routes `/api/*` and `/*` to correct backends
- [ ] WAF blocks OWASP test attacks (use an OWASP test scanner)
- [ ] Front Door routes users to nearest region
- [ ] Front Door fails over when a region is unhealthy
- [ ] Traffic Manager resolves to correct endpoint based on routing method
- [ ] Health probes correctly detect unhealthy backends

### 🔍 Behind the Scenes

- **Azure Load Balancer** operates in Azure's SDN fabric. It uses 5-tuple hash (src IP, src port, dst IP, dst port, protocol) for traffic distribution. It's implemented at the hypervisor level — no VM or appliance processes the traffic, making it ultra-fast (~4 million packets/second).
- **Application Gateway** is a Layer 7 proxy — actual VMs (managed by Microsoft) accept connections, terminate SSL, inspect HTTP headers, and proxy to backends. This is why it's slower but more feature-rich than Load Balancer.
- **Front Door** uses Microsoft's global edge network (190+ PoPs worldwide). Your traffic enters the nearest PoP and travels the Microsoft backbone to the origin — faster than public internet routing.
- **Traffic Manager** is purely DNS-based — it never touches the actual data traffic. It simply resolves DNS queries to the best endpoint's IP. This makes it protocol-agnostic (works with any TCP/UDP traffic).

---

## Scenario 10: VPN Gateway & ExpressRoute

### 🎯 Objective

Connect Azure to on-premises networks (or simulated on-prem) using VPN Gateway and understand ExpressRoute for enterprise connectivity. Master hybrid networking scenarios.

### 📦 App Description

**A hybrid application** where the web frontend runs in Azure (App Service) but connects to a simulated on-premises database (PostgreSQL on a VM in a separate VNet acting as "on-prem"). This forces you to deal with VPN tunnels, routing, DNS resolution across networks, and the complexities of hybrid connectivity.

### 🏗️ Architecture Diagram

```
┌──────────────────────────┐         ┌──────────────────────────┐
│    "ON-PREMISES"          │         │    AZURE CLOUD           │
│  (Simulated VNet)         │         │                          │
│                           │         │                          │
│  VNet: 172.16.0.0/16      │  S2S    │  VNet: 10.0.0.0/16      │
│                           │  VPN    │                          │
│  ┌─────────────────┐     │  Tunnel │  ┌─────────────────┐     │
│  │ snet-onprem     │     │◄──────►│  │ GatewaySubnet   │     │
│  │ 172.16.1.0/24   │     │  IPSec │  │ 10.0.255.0/27   │     │
│  │                 │     │  IKEv2 │  │                 │     │
│  │ ┌─────────────┐ │     │         │  │ VPN Gateway    │     │
│  │ │ VM: db-onprem│ │     │         │  │ "vpngw-hub"    │     │
│  │ │ PostgreSQL   │ │     │         │  │ VpnGw2 SKU     │     │
│  │ │ 172.16.1.4   │ │     │         │  └─────────────────┘     │
│  │ └─────────────┘ │     │         │                          │
│  │                 │     │         │  ┌─────────────────┐     │
│  │ ┌─────────────┐ │     │         │  │ snet-app        │     │
│  │ │ VM: vpn-gw   │ │     │         │  │ 10.0.1.0/24    │     │
│  │ │ (or another  │ │     │         │  │                 │     │
│  │ │  VPN Gateway)│ │     │         │  │ App Service     │     │
│  │ └─────────────┘ │     │         │  │ (VNet Int.)     │     │
│  └─────────────────┘     │         │  │ → 172.16.1.4    │     │
│                           │         │  └─────────────────┘     │
│  Local DNS:               │         │                          │
│  db.onprem.local          │         │  Azure DNS:              │
│  → 172.16.1.4             │         │  Forwarder → on-prem DNS │
└──────────────────────────┘         └──────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Simulate On-Premises

- [ ] Create a separate VNet to simulate on-prem (`172.16.0.0/16`)
- [ ] Deploy a VM with PostgreSQL in the "on-prem" VNet
- [ ] Create a VPN Gateway in the "on-prem" VNet
- [ ] Verify the two VNets CANNOT communicate (no peering, no VPN yet)

#### Part B: Site-to-Site VPN

- [ ] Create a VPN Gateway in the Azure hub VNet (`GatewaySubnet` must be /27 or larger)
- [ ] Create a Local Network Gateway representing the "on-prem" network
- [ ] Create a VPN Connection (IPSec/IKEv2 tunnel)
- [ ] Verify connectivity: ping from Azure VM to on-prem VM
- [ ] Check VPN connection status and throughput

```bash
# Create VPN Gateway (takes 30-45 minutes!)
az network vnet-gateway create \
  --name vpngw-hub-eastus \
  --resource-group rg-hub-prod-eastus \
  --vnet vnet-hub-eastus \
  --gateway-type Vpn \
  --vpn-type RouteBased \
  --sku VpnGw2 \
  --generation Generation2

# Create Local Network Gateway (represents on-prem)
az network local-gateway create \
  --name lgw-onprem \
  --resource-group rg-hub-prod-eastus \
  --gateway-ip-address <onprem-vpn-public-ip> \
  --local-address-prefixes 172.16.0.0/16

# Create Connection
az network vpn-connection create \
  --name conn-to-onprem \
  --resource-group rg-hub-prod-eastus \
  --vnet-gateway1 vpngw-hub-eastus \
  --local-gateway2 lgw-onprem \
  --shared-key "YourPreSharedKey123!"
```

> ⚠️ **DevOps Gotcha:** VPN Gateway deployment takes **30-45 minutes**. Don't stare at the screen — go grab coffee. Also, the `GatewaySubnet` MUST be named exactly `GatewaySubnet` (just like `AzureBastionSubnet`). Any other name will fail. Microsoft recommends /27 for the gateway subnet. And VPN Gateways cost ~$140-400/month even when idle — DELETE when done practicing.

#### Part C: Point-to-Site VPN

- [ ] Configure P2S VPN for developer laptop access
- [ ] Try certificate-based authentication (generate root + client certs)
- [ ] Try Azure AD authentication (SSO for P2S VPN)
- [ ] Download and install the VPN client
- [ ] Verify: from your laptop, access resources in the Azure VNet via private IP

> ⚠️ **DevOps Gotcha:** P2S VPN with Azure AD auth only works with OpenVPN protocol and the Azure VPN Client app. IKEv2 native clients (Windows built-in, macOS built-in) don't support Azure AD auth — they only work with certificate auth. Many teams plan for Azure AD P2S auth and then discover their users' OS VPN clients don't support it.

#### Part D: VPN Gateway Advanced

- [ ] Configure Active-Active VPN Gateways for high availability
- [ ] Understand VPN Gateway SKUs and throughput:
  - VpnGw1: 650 Mbps, 30 tunnels
  - VpnGw2: 1 Gbps, 30 tunnels
  - VpnGw3: 1.25 Gbps, 30 tunnels
  - VpnGw5: 10 Gbps, 100 tunnels
- [ ] Compare VNet-to-VNet VPN connection vs VNet Peering
- [ ] Configure BGP for dynamic route exchange

#### Part E: ExpressRoute Concepts

- [ ] Understand ExpressRoute vs VPN:

```
┌───────────────────────────────────────────────────────────┐
│ VPN GATEWAY vs EXPRESSROUTE                                │
│                                                           │
│ VPN Gateway:                                              │
│   • Over public internet (encrypted IPSec tunnel)         │
│   • Up to 10 Gbps                                         │
│   • Minutes to set up                                     │
│   • ~$140-400/month                                       │
│   • Good for: dev/test, small workloads, quick setup      │
│                                                           │
│ ExpressRoute:                                             │
│   • Private dedicated connection (NOT over internet)      │
│   • Up to 100 Gbps                                        │
│   • Weeks to provision (involves ISP/partner)             │
│   • ~$300-15,000/month + circuit provider fees            │
│   • Good for: production, compliance, high throughput     │
│   • Peering types: Private (VNets), Microsoft (M365/PaaS)│
└───────────────────────────────────────────────────────────┘
```

- [ ] Review ExpressRoute peering types: Private Peering and Microsoft Peering
- [ ] Understand ExpressRoute Global Reach (connect on-prem sites through Azure backbone)
- [ ] Understand Virtual WAN for large-scale hub-spoke with ExpressRoute + VPN

#### Part F: Hybrid DNS

- [ ] Configure Azure Private DNS Resolver (or DNS forwarder VM)
- [ ] Set up conditional forwarding: Azure DNS forwards `*.onprem.local` to on-prem DNS
- [ ] Set up conditional forwarding: On-prem DNS forwards `*.database.windows.net` to Azure DNS
- [ ] Verify cross-network DNS resolution works

> ⚠️ **DevOps Gotcha:** Hybrid DNS is the most painful part of hybrid networking. Private Endpoints break if DNS isn't correctly configured across both networks. The on-prem DNS server must forward Azure Private Link domains (like `privatelink.database.windows.net`) to Azure DNS (168.63.129.16) for Private Endpoints to resolve correctly from on-prem. Without this, on-prem apps will resolve to the PUBLIC IP and get blocked.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| VPN tunnel won't connect | Pre-shared key mismatch, IKE version mismatch | Verify PSK on both sides; ensure both use IKEv2 |
| VPN tunnel flapping (up/down) | Unstable internet, MTU issues | Check ISP stability; reduce MTU to 1350-1400 |
| Asymmetric routing | Routes exist in one direction only | Ensure routes are symmetric; check UDRs on both sides |
| Can't resolve on-prem DNS from Azure | DNS forwarding not configured | Set up Azure Private DNS Resolver or forwarder VM |
| VPN throughput lower than expected | Gateway SKU too small or single tunnel | Upgrade SKU; use Active-Active for two tunnels |
| Forced tunneling breaks Azure services | All traffic going through on-prem | Add UDR exceptions for Azure service tags |
| BGP routes not propagating | BGP not enabled on gateway or wrong ASN | Enable BGP; check ASN configuration (Azure uses 65515) |

### 💰 Cost Tips

- **VPN Gateway VpnGw1:** ~$140/month — cheapest production-capable
- **VPN Gateway VpnGw2:** ~$280/month
- **ExpressRoute:** ~$300/month minimum + provider fees — NOT for learning
- For learning: use VNet-to-VNet VPN to simulate S2S (cheaper than two VPN gateways)
- **DELETE VPN Gateways when done** — they cost even when no tunnels are active
- Gateway deployment takes 30-45 min — factor this into your practice time

### ✔️ Verification Checklist

- [ ] S2S VPN tunnel shows "Connected" status
- [ ] Ping succeeds from Azure VM to on-prem VM (and vice versa)
- [ ] App Service (via VNet Integration) can reach on-prem database
- [ ] P2S VPN allows laptop access to Azure private resources
- [ ] DNS resolution works across both networks
- [ ] VPN throughput meets expectations for the SKU
- [ ] BGP routes are visible (if BGP is configured)

### 🔍 Behind the Scenes

- **VPN Gateway** is a pair of Azure VMs (for redundancy) running in the `GatewaySubnet`. They handle IPSec tunnel establishment, IKE key exchange, and packet encryption/decryption. Active-Active mode runs both VMs simultaneously with two tunnels.
- **IPSec tunnels** use IKEv2 for key negotiation and ESP (Encapsulating Security Payload) for data encryption. Packets are encapsulated, encrypted, and sent over the public internet. The receiving gateway decrypts and routes to the VNet.
- **ExpressRoute** uses MPLS (Multi-Protocol Label Switching) circuits provided by connectivity partners (like AT&T, Equinix). Traffic travels over the partner's private network to a Microsoft Edge router, then to the Azure backbone. It NEVER touches the public internet.
- **BGP (Border Gateway Protocol)** enables dynamic route exchange between your on-prem router and Azure VPN Gateway. Without BGP, you must manually specify on-prem address prefixes. With BGP, changes propagate automatically.

---

## 🎯 What's Next?

After completing Batch 2, you should have solid skills in:
- ✅ Identity management and authentication flows
- ✅ Secrets and certificate management
- ✅ Network security and WAF configuration
- ✅ Global and regional load balancing
- ✅ Hybrid connectivity with VPN/ExpressRoute

**Proceed to → Batch 3: Containers, Databases & Messaging** where you'll tackle ACR, AKS, Azure SQL, Cosmos DB, Service Bus, Event Hubs, and Redis Cache.
