[🏠 Home](../README.md) · [Quick Reference](batch_state.md)

# 🔐 Azure RBAC — DevOps Quick Reference

> **Read time:** ~12 min | **Audience:** DevOps Engineers
> Who can do what, where. Least privilege in practice.

---

## Table of Contents
1. [The RBAC Formula](#1-the-rbac-formula)
2. [Scope Hierarchy](#2-scope-hierarchy)
3. [Generic Built-in Roles](#3-generic-built-in-roles)
4. [Key Vault Roles](#4-key-vault-roles)
5. [Storage Account Roles](#5-storage-account-roles)
6. [AKS Roles](#6-aks-roles)
7. [Networking Roles](#7-networking-roles)
8. [Azure DevOps — Pipeline Permissions](#8-azure-devops--pipeline-permissions)
9. [Identity Types](#9-identity-types)
10. [Least Privilege Decision Guide](#10-least-privilege-decision-guide)
11. [DevOps Gotchas ⚠️](#11-devops-gotchas)

---

## 1. The RBAC Formula

Every RBAC assignment is exactly 3 things:

```
  WHO  +  WHAT  +  WHERE  =  Access

  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐
  │  Principal   │  │     Role       │  │     Scope        │
  │  (Identity)  │+ │  (Permissions) │+ │  (Resource)      │= Role Assignment
  └──────────────┘  └────────────────┘  └──────────────────┘

  Example:
  "devops-team"  +  "Contributor"  +  "rg-myapp-prod"
  → DevOps team can create/modify/delete anything in rg-myapp-prod
```

**Principals** = users, groups, service principals, managed identities
**Roles** = a named set of allowed actions (e.g., `Microsoft.KeyVault/vaults/secrets/read`)
**Scope** = where the role applies — inherits downward in the hierarchy

---

## 2. Scope Hierarchy

Roles assigned at a higher scope automatically apply to everything below it.

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  Management Group  (e.g., "Enterprise Root")                        │
  │  │  ← Broadest scope. Assign here = applies to all subscriptions   │
  │  │                                                                  │
  │  ├── Subscription  (e.g., "Production Subscription")               │
  │  │   │  ← Assign here = applies to all RGs in this subscription    │
  │  │   │                                                              │
  │  │   ├── Resource Group  (e.g., "rg-myapp-prod")                  │
  │  │   │   │  ← Assign here = applies to all resources in this RG    │
  │  │   │   │                                                          │
  │  │   │   ├── Resource (e.g., "kv-myapp-prod")                     │
  │  │   │   │      ← Narrowest scope. Assign here = ONE resource only │
  │  │   │   │                                                          │
  │  │   │   └── Resource (e.g., "st-myappprod")                      │
  │  │   │                                                              │
  │  │   └── Resource Group  (e.g., "rg-myapp-dev")                   │
  │  │                                                                  │
  └─────────────────────────────────────────────────────────────────────┘

  Golden rule: assign at the NARROWEST scope possible.
```

```bash
# Assign a role via CLI
az role assignment create \
    --assignee "user@company.com" \
    --role "Contributor" \
    --resource-group "rg-myapp-prod"

# Assign at a specific resource (Key Vault)
az role assignment create \
    --assignee "user@company.com" \
    --role "Key Vault Secrets User" \
    --scope "/subscriptions/<sub-id>/resourceGroups/rg-prod/providers/Microsoft.KeyVault/vaults/kv-prod"

# List all role assignments on a resource group
az role assignment list --resource-group rg-prod --output table
```

---

## 3. Generic Built-in Roles

These 4 roles work on almost every Azure resource.

| Role | Can Do | Cannot Do | Use For |
|------|--------|-----------|---------|
| **Owner** | Everything — create, delete, modify, AND assign roles to others | Nothing | Subscription admins only. Never hand this out casually |
| **Contributor** | Create, modify, delete resources | Cannot assign roles (no IAM access) | DevOps teams, CI/CD pipelines |
| **Reader** | Read/view everything — configs, settings, logs | Cannot make any changes | Auditors, finance teams, junior devs who need visibility |
| **User Access Administrator** | Manage role assignments ONLY | Cannot touch actual resources | IAM admins, when someone else sets up resources |

```
  ┌──────────────────────────────────────────────────┐
  │  WHEN TO PICK WHICH ROLE                         │
  │                                                  │
  │  Need to browse/read configs?          → Reader  │
  │  Need to deploy/manage infra?          → Contributor │
  │  Need to assign roles to others?       → User Access Admin │
  │  Need full control of the subscription?→ Owner   │
  │                                                  │
  │  Default assumption: Reader            ← start here │
  │  Escalate only when needed                       │
  └──────────────────────────────────────────────────┘
```

---

## 4. Key Vault Roles

Key Vault has TWO planes — understand this or you'll be confused:

```
  Control Plane (ARM)                 Data Plane
  ──────────────────                  ──────────
  Manage the vault itself             Access secrets/keys/certs INSIDE the vault
  Create/delete vaults                Read a secret value
  Manage networking, firewalls        Write a new secret
  View vault properties               Rotate a key

  Roles like "Contributor" give       Roles like "Key Vault Secrets User"
  control plane access only           give data plane access
  (can see vault exists, NOT          (can actually read secrets)
   read any secrets!)
```

| Role | Can Do | Cannot Do | Use For |
|------|--------|-----------|---------|
| **Key Vault Administrator** | Full control — manage secrets, keys, certs, AND vault config + access policies | Cannot assign Azure RBAC roles | Security admins, vault owners |
| **Key Vault Secrets Officer** | Create, update, delete, list secrets (full CRUD on secrets only) | Cannot manage keys or certificates | App teams that need to write secrets |
| **Key Vault Secrets User** | **Read (get) secret values** | Cannot list, create, delete, or modify secrets | Apps reading secrets at runtime, CI/CD pipelines pulling secrets |
| **Key Vault Reader** | View vault metadata, list secret names | Cannot read secret VALUES | Auditors who need to see what secrets exist but not their values |
| **Key Vault Crypto Officer** | Manage encryption keys (create, rotate, delete) | Cannot manage secrets or certs | Encryption/PKI teams |
| **Key Vault Certificate Officer** | Manage SSL certificates | Cannot manage secrets or keys | Certificate management teams |

### Minimum role to read a secret in Azure DevOps pipeline:
```
  Pipeline Service Connection Identity → "Key Vault Secrets User" on the vault
  (OIDC service connection, not client secret preferred)
```

```bash
# Grant a managed identity read access to secrets
az role assignment create \
    --assignee "<managed-identity-client-id>" \
    --role "Key Vault Secrets User" \
    --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.KeyVault/vaults/<kv-name>"

# Enable RBAC on Key Vault (instead of legacy access policies)
az keyvault update \
    --name kv-prod \
    --resource-group rg-prod \
    --enable-rbac-authorization true
```

> **Always enable RBAC authorization on Key Vault** (`--enable-rbac-authorization true`). The old "Access Policies" model is being deprecated and is harder to audit.

---

## 5. Storage Account Roles

Storage also has control plane vs data plane split.

```
  Control Plane                         Data Plane
  ─────────────                         ──────────
  "Storage Account Contributor"         "Storage Blob Data Reader"
  Can create/delete storage accounts    Can actually READ blob content
  Can view keys (!) — dangerous         Cannot manage the account itself
```

| Role | Can Do | Cannot Do | Use For |
|------|--------|-----------|---------|
| **Storage Account Contributor** | Create/delete accounts, view access keys (full key access!) | Cannot read blob/file data via Entra ID auth | Infrastructure provisioning only. Very powerful — avoid in prod |
| **Storage Blob Data Owner** | Full CRUD on blobs + manage POSIX ACLs | Cannot manage account settings | Data lake admins |
| **Storage Blob Data Contributor** | Read, write, delete blobs (CRUD) | Cannot delete containers, cannot view keys | Apps that upload/download blobs |
| **Storage Blob Data Reader** | Read blob content only | Cannot write, delete, or list all containers | Apps/users that only need to download |
| **Storage Queue Data Contributor** | Send and receive messages from queues | Cannot access blobs | Queue consumers/producers |
| **Storage File Data SMB Share Contributor** | Read/write Azure File shares | Cannot delete the share itself | File share users |
| **Storage Blob Delegator** | Generate user delegation SAS tokens | Cannot access blobs directly | Apps that need to generate time-limited URLs |

```bash
# Grant an app read access to blobs
az role assignment create \
    --assignee "<managed-identity-id>" \
    --role "Storage Blob Data Reader" \
    --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<st-name>"

# Grant at container level (even more restrictive)
az role assignment create \
    --assignee "<managed-identity-id>" \
    --role "Storage Blob Data Contributor" \
    --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<st-name>/blobServices/default/containers/<container-name>"
```

---

## 6. AKS Roles

| Role | Can Do | Cannot Do | Use For |
|------|--------|-----------|---------|
| **AKS Cluster Admin** | Full kubectl access — any namespace, any resource | Nothing | Cluster admins / break-glass access |
| **AKS Cluster User** | Download kubeconfig only (can connect to cluster) | Cannot deploy or view resources until Kubernetes RBAC grants it | All developers (then K8s RBAC controls what they can do) |
| **AKS RBAC Admin** | Manage Kubernetes RBAC roles within a namespace | Cannot access other namespaces | Namespace owners |
| **AKS RBAC Cluster Admin** | Full Kubernetes RBAC admin across all namespaces | Nothing | Platform admins |
| **AKS RBAC Reader** | Read-only kubectl (get/list/describe, all namespaces) | Cannot modify anything | Developers with read-only cluster access |
| **AKS RBAC Writer** | Read + write resources in a namespace | Cannot manage roles | Developers deploying to their namespace |

```
  Azure RBAC                 Kubernetes RBAC
  ──────────────             ────────────────
  Controls who can           Controls what they can do
  connect to the cluster     INSIDE the cluster

  AKS Cluster User           ClusterRole: developer
  → Can get kubeconfig   +   → Can deploy to namespace X
```

---

## 7. Networking Roles

| Role | Can Do | Cannot Do | Use For |
|------|--------|-----------|---------|
| **Network Contributor** | Create/manage VNets, NSGs, public IPs, load balancers, VPN gateways | Cannot manage DNS zones or Private Endpoints separately | NetOps teams |
| **DNS Zone Contributor** | Create/update/delete records in DNS zones | Cannot create new DNS zones (need Contributor for that) | Teams that manage DNS records but not infra |
| **Private DNS Zone Contributor** | Manage private DNS zones and links | Cannot manage public DNS zones | Teams managing internal service discovery |

---

## 8. Azure DevOps — Pipeline Permissions

This is what you need to allow a pipeline to READ secrets from Azure Key Vault.

### The full chain

```
  Azure DevOps Pipeline
       │
       │ uses Service Connection
       ▼
  Service Principal / Managed Identity (in Entra ID)
       │
       │ needs Azure RBAC role
       ▼
  Key Vault (Azure Resource)
       │
       │ "Key Vault Secrets User" role at vault scope
       ▼
  Secret value returned to pipeline ✅
```

### Roles needed per DevOps persona

| Persona | Azure DevOps Role | Azure RBAC Role | Purpose |
|---------|-----------------|-----------------|---------|
| **Platform Admin** | Project Collection Admin | Owner (subscription) | Full control |
| **DevOps Engineer** | Project Administrator | Contributor (resource group) | Deploy infra, manage pipelines |
| **Developer** | Contributor (repo) | None (Reader max) | Push code, create PRs |
| **Pipeline identity** | — | Key Vault Secrets User | Read secrets at pipeline runtime |
| **Pipeline identity** | — | Storage Blob Data Contributor | Upload artifacts to blob |
| **Pipeline identity** | — | AKS Cluster User + AKS RBAC Writer | Deploy to AKS |
| **Auditor** | Reader | Reader | View-only access everywhere |

### How the pipeline reads secrets

```yaml
# azure-pipelines.yml

variables:
  - name: azureServiceConnection
    value: 'sc-azure-prod'        # Service connection (OIDC preferred)
  - name: keyVaultName
    value: 'kv-myapp-prod'

stages:
  - stage: Deploy
    jobs:
      - job: FetchSecrets
        steps:
          - task: AzureKeyVault@2
            inputs:
              azureSubscription: '$(azureServiceConnection)'
              KeyVaultName: '$(keyVaultName)'
              SecretsFilter: 'DB-PASSWORD,API-KEY'
            displayName: 'Fetch secrets from Key Vault'

          - script: |
              echo "Connecting to DB: $(DB-PASSWORD)"   # ← prints *** in logs
            displayName: 'Use secret (auto-masked)'
```

**Requirement:** The service connection identity must have `Key Vault Secrets User` on the vault.

### What permissions each persona has in Azure DevOps

| Persona | Can Do | Cannot Do |
|---------|--------|-----------|
| **Project Collection Admin** | Create orgs, billing, install extensions, manage all projects | Nothing within scope |
| **Project Administrator** | Create repos, pipelines, service connections, manage environments | Cannot manage billing or org-wide settings |
| **Contributors (Developers)** | Push to feature branches, create PRs, trigger pipelines | Cannot merge to main/dev, cannot create service connections |
| **Readers** | View repos, pipelines, build results | Cannot push code or trigger pipelines |
| **Build Administrator** | Create and edit pipelines, manage variable groups | Cannot manage service connections or environments |

---

## 9. Identity Types

| Identity Type | What it is | Credential managed by | Use for |
|---------------|-----------|----------------------|---------|
| **User** | Human person (`alice@company.com`) | User (password + MFA) | Human access to portal, CLI |
| **Group** | Collection of users | N/A (group membership) | Assign roles to teams at once |
| **Service Principal** | App identity for EXTERNAL tools | YOU (client secret/cert — must rotate!) | GitHub Actions, Terraform from outside Azure |
| **System-assigned Managed Identity** | Azure-managed identity tied to ONE resource | Azure (zero secrets!) | VM, App Service, Function accessing Azure services |
| **User-assigned Managed Identity** | Azure-managed identity you create independently | Azure (zero secrets!) | Shared identity across multiple resources |

```
  Rule: If it runs INSIDE Azure → use Managed Identity
        If it runs OUTSIDE Azure → use Service Principal

  Service Principal secrets expire.
  Managed Identity credentials never expire.
  Use Managed Identity whenever possible.
```

---

## 10. Least Privilege Decision Guide

```
  QUESTION: What does this person/system need to do?
                    │
      ┌─────────────┼──────────────┐
      ▼             ▼              ▼
  View only     Deploy infra    Full control
      │             │              │
      ▼             ▼              ▼
  Reader      Contributor     Owner (avoid!)
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
  Whole sub?           Specific RG/resource?
      │                       │
  Contributor            Contributor
  at sub level           at RG level ✅ (prefer this)

  SPECIFIC SERVICES:
  Read KV secrets?        → Key Vault Secrets User
  Write to blob storage?  → Storage Blob Data Contributor
  Read blob storage?      → Storage Blob Data Reader
  Deploy to AKS?          → AKS Cluster User + AKS RBAC Writer
  Manage DNS records?     → DNS Zone Contributor
```

---

## 11. DevOps Gotchas ⚠️

### 1. Contributor cannot assign roles
```
  Contributor gives: create, update, delete resources ✅
  Contributor gives: assign RBAC to others          ❌
  Need "User Access Administrator" for that
```

### 2. Control plane ≠ data plane for Key Vault and Storage
```
  Contributor on a Key Vault = can see the vault in portal
  Contributor on a Key Vault = CANNOT read any secrets
  You need "Key Vault Secrets User" for that (separate data-plane role)

  Same for Storage:
  "Storage Account Contributor" ≠ ability to read blob data
  Need "Storage Blob Data Reader" for that
```

### 3. Service Principal secrets expire — and will break your pipeline
Default SP secret lifetime = 1 year. They expire silently. Pipeline breaks at 2am on a Friday. Set calendar reminders 30 days before expiry. Better: switch to **OIDC/Workload Identity Federation** — no secrets at all.

### 4. Check expiry dates of all service principals
```bash
# Find all service principals and their secret expiry
az ad app list --all --query "[].{Name:displayName, AppId:appId}" -o table
az ad sp credential list --id <app-id> --query "[].endDateTime" -o table
```

### 5. Role assignments are additive — there's no "deny" in standard RBAC
If someone has Reader at subscription level and Contributor at resource group level, they get Contributor on that RG. You can't take away Reader from a specific resource without removing the subscription-level assignment. Use **Azure RBAC deny assignments** or **Azure Policy** for explicit denials.

### 6. "Owner" does NOT mean they can do everything without being Owner themselves
A user with Owner can assign any role to anyone — including Owner to themselves. Never give Owner to automated processes or junior engineers.

### 7. Scope matters — don't assign Contributor at subscription level
If your CI/CD pipeline needs Contributor on `rg-myapp-prod` only, scope it to the resource group. Subscription-level Contributor means the pipeline can delete any resource in any RG.

---

*Source: [Azure Handbook §8](../azure/azure_handbook.md) · [Azure Services Handbook §3.2, §5.7, §6.1](../azure-services/azure_services_handbook.md) · [DevOps Phase 12](../azure-devops/phase-12-security-compliance.md)*
