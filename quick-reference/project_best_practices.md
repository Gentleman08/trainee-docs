[🏠 Home](../README.md) · [Quick Reference](batch_state.md)

# 🚀 Starting a Project from Scratch — DevOps Best Practices

> **Read time:** ~15 min | **Audience:** DevOps Engineers starting a new project
> Decisions made on Day 1 are hard to undo on Day 100.

---

## Table of Contents
1. [Azure Resource Naming Convention](#1-azure-resource-naming-convention)
2. [GitHub / Azure DevOps Naming Convention](#2-github--azure-devops-naming-convention)
3. [Repository Structure](#3-repository-structure)
4. [Branch Model & Naming](#4-branch-model--naming)
5. [Branch Protection Policies](#5-branch-protection-policies)
6. [RBAC — Day 1 Access Setup](#6-rbac--day-1-access-setup)
7. [Secrets Management from Day 1](#7-secrets-management-from-day-1)
8. [Environment Strategy](#8-environment-strategy)
9. [Tagging Strategy](#9-tagging-strategy)
10. [Cost Management](#10-cost-management)
11. [Security from Day 1](#11-security-from-day-1)
12. [Service Connections — Use OIDC, Not Secrets](#12-service-connections--use-oidc-not-secrets)
13. [DevOps Gotchas ⚠️](#13-devops-gotchas)

---

## 1. Azure Resource Naming Convention

**Pattern:** `{type}-{app}-{env}-{region}`

Consistent naming prevents confusion, aids searching, and makes RBAC scoping easier.

| Resource | Pattern | Example |
|----------|---------|---------|
| Resource Group | `rg-{app}-{env}-{region}` | `rg-myapp-prod-eastus` |
| Virtual Machine | `vm-{role}-{env}-{region}` | `vm-web01-prod-eastus` |
| VM Scale Set | `vmss-{role}-{env}` | `vmss-web-prod` |
| App Service | `app-{name}-{env}` | `app-myapi-prod` |
| App Service Plan | `asp-{name}-{env}` | `asp-myapp-prod` |
| AKS Cluster | `aks-{name}-{env}-{region}` | `aks-main-prod-eastus` |
| Storage Account | `st{app}{env}{region}` ← **no hyphens!** | `stmyappprodeus` |
| Key Vault | `kv-{app}-{env}` | `kv-myapp-prod` |
| Virtual Network | `vnet-{name}-{env}-{region}` | `vnet-main-prod-eastus` |
| Subnet | `snet-{tier}-{env}` | `snet-web-prod` |
| NSG | `nsg-{tier}-{env}` | `nsg-web-prod` |
| Public IP | `pip-{resource}-{env}` | `pip-lb-prod` |
| Load Balancer | `lb-{app}-{env}` | `lb-myapp-prod` |
| Container Registry | `acr{app}{env}` ← **no hyphens!** | `acrmyappprod` |
| Log Analytics | `log-{app}-{env}` | `log-myapp-prod` |
| Application Insights | `appi-{app}-{env}` | `appi-myapp-prod` |
| Service Principal | `sp-{tool}-{env}` | `sp-github-prod` |
| Managed Identity | `id-{app}-{purpose}` | `id-myapp-kv-reader` |

```
  Short regions for naming:
  eastus   → eus    westus  → wus
  eastus2  → eus2   westus2 → wus2
  northeurope → neu  westeurope → weu
  centralindia → cin  southeastasia → sea
```

---

## 2. GitHub / Azure DevOps Naming Convention

Consistency across project artifacts prevents confusion and simplifies automation.

### Azure DevOps

| Resource | Pattern | Example |
|----------|---------|---------|
| Organization | `org-{company}` | `org-acme-corp` |
| Project | `prj-{business-unit}-{app}` | `prj-fin-paymentgateway` |
| Git Repository | `repo-{app-name}` | `repo-payment-api` |
| Pipeline | `pipe-{app}-{purpose}` | `pipe-payment-api-ci` |
| Variable Group | `vg-{env}-{purpose}` | `vg-prod-dbcredentials` |
| Service Connection | `sc-{target}-{env}` | `sc-azure-sub-prod` |
| Agent Pool | `pool-{os}-{purpose}` | `pool-ubuntu-build` |
| Environment | `env-{name}` | `env-prod` |
| Secure File | `sf-{name}-{purpose}` | `sf-sonar-cert` |

### GitHub

| Resource | Pattern | Example |
|----------|---------|---------|
| Organization | `{company-name}` | `acme-corp` |
| Repository | `{app-name}` or `{component}` | `payment-api`, `infra-terraform` |
| GitHub Actions workflow file | `{purpose}.yml` | `ci.yml`, `cd-prod.yml` |
| Environment | `{env-name}` | `production`, `staging` |
| Secret | `{SCOPE}_{RESOURCE}_{PROPERTY}` (SCREAMING_SNAKE) | `PROD_DB_PASSWORD`, `AZURE_CLIENT_ID` |

---

## 3. Repository Structure

### Single Application Repo

```
  repo-payment-api/
  ├── src/                          # Application source code
  │   ├── app.js
  │   └── tests/
  ├── pipelines/                    # CI/CD pipeline definitions
  │   ├── pr-validation.yml         # Runs on every PR
  │   ├── build.yml                 # CI — build + test
  │   ├── cd-release.yml            # CD — multi-stage deploy
  │   └── templates/                # Reusable pipeline templates
  │       ├── security-scans.yml
  │       ├── docker-build.yml
  │       └── deploy-stage.yml
  ├── infra/                        # Infrastructure as Code (Terraform/Bicep)
  │   ├── main.tf
  │   ├── variables.tf
  │   └── environments/
  │       ├── dev.tfvars
  │       ├── staging.tfvars
  │       └── prod.tfvars
  ├── docs/                         # Architecture, runbooks, ADRs
  │   ├── architecture.md
  │   └── runbooks/
  ├── Dockerfile
  ├── .gitignore
  ├── .gitleaks.toml               # Secrets scanning config
  └── README.md
```

### Multi-Repo Strategy (Monorepo vs Polyrepo)

```
  MONOREPO                          POLYREPO
  ────────                          ────────
  One repo for everything           One repo per service

  ✅ Easy cross-service refactor    ✅ Independent deployments
  ✅ Single PR spans multiple svc   ✅ Clear ownership per team
  ❌ Slower CI (larger checkout)    ❌ Harder cross-service changes
  ❌ Complex pipeline triggers      ❌ Config duplication

  Rule of thumb:
  < 3 services → monorepo is fine
  > 3 services with separate teams → polyrepo
```

---

## 4. Branch Model & Naming

Use **GitFlow** for structured releases. Simpler projects can use **Trunk-Based** (main + feature branches only).

### GitFlow (recommended for enterprise)

```
  main ─────────────────────────────────────────── (production state)
   │                                    ▲
   │              ┌─── release/v1.2 ───┤ merge commit
   │              │     (QA+UAT fixes) │
  dev ────────────────────────────────────────────── (latest dev)
   │         ▲             ▲
   │    feature/JIRA-123   feature/JIRA-456     (squash merge → dev)
   │
  hotfix/critical-fix ──────────────────────────── (emergency fix)
      └──► merged to main AND dev
```

| Branch | Created from | Merge to | Purpose | Merge strategy |
|--------|-------------|----------|---------|----------------|
| `main` | — | — | Production-ready state. No direct commits | — |
| `dev` | `main` | — | Integration branch, latest development | — |
| `feature/{ticket-id}-short-desc` | `dev` | `dev` | Build a feature | Squash merge |
| `release/{version}` | `dev` | `main` + `dev` | Prepare a release, QA/UAT fixes | Merge commit |
| `hotfix/{ticket-id}-short-desc` | `main` | `main` + `dev` | Emergency production fix | Merge commit |

### Branch naming examples

```
  feature/JIRA-123-add-payment-method
  feature/GH-456-fix-login-timeout
  release/v1.2.0
  release/2026-07-sprint3
  hotfix/JIRA-789-fix-null-pointer-prod
  hotfix/critical-db-conn-leak
```

---

## 5. Branch Protection Policies

Apply these policies to `main` and `dev` before the first commit.

### For `main` (production branch — strictest)

- [ ] **Require pull request** — no direct pushes allowed
- [ ] **Minimum 2 reviewers** — at least 1 must be a tech lead
- [ ] **Prohibit self-approval** — reviewer ≠ author
- [ ] **Require linked work item** — every PR traced to a ticket
- [ ] **Require all comments resolved** before merge
- [ ] **Require build validation** — CI pipeline must pass
- [ ] **Merge strategy: Merge Commit (No-Fast-Forward)** — preserves history
- [ ] **Require stale review dismissal** — new commits reset approvals

### For `dev` (integration branch)

- [ ] **Require pull request** — no direct pushes
- [ ] **Minimum 1 reviewer**
- [ ] **Prohibit self-approval**
- [ ] **Require build validation** — PR pipeline must pass
- [ ] **Merge strategy: Squash** — keeps history clean

### For `release/*` and `hotfix/*`

- [ ] Created by tech lead or release manager only
- [ ] Only the release manager can merge to `main`

---

## 6. RBAC — Day 1 Access Setup

Set this up before anyone starts working. Changing RBAC retroactively is messy.

```
  ┌─────────────────────────────────────────────────────────────────────────┐
  │  DAY 1 RBAC SETUP                                                       │
  │                                                                         │
  │  Subscription Level:                                                    │
  │  ├── Sub Owners (1-2 people only!)  → Owner                            │
  │  └── Everyone else                 → Reader (at subscription level)    │
  │                                                                         │
  │  Resource Group: rg-{app}-prod                                          │
  │  ├── DevOps Engineers → Contributor                                     │
  │  ├── Developers       → Reader (can view, not deploy)                   │
  │  └── Auditors         → Reader                                          │
  │                                                                         │
  │  Resource Group: rg-{app}-dev                                           │
  │  ├── DevOps Engineers → Contributor                                     │
  │  └── Developers       → Contributor (can deploy to dev)                 │
  │                                                                         │
  │  Key Vault:                                                              │
  │  ├── Pipeline identity   → Key Vault Secrets User                      │
  │  ├── App Managed Identity→ Key Vault Secrets User                      │
  │  ├── DevOps Engineers    → Key Vault Secrets Officer                   │
  │  └── Everyone else       → No access                                   │
  │                                                                         │
  │  Storage Account:                                                        │
  │  ├── Pipeline identity   → Storage Blob Data Contributor                │
  │  ├── Apps reading data   → Storage Blob Data Reader                    │
  │  └── Everyone else       → No access                                   │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Azure DevOps access setup

| Scope | Who | Role |
|-------|-----|------|
| Organization | CTO / Platform Architect | Project Collection Admin |
| Project | DevOps Engineers | Project Administrator |
| Repositories | All developers | Contributors |
| `main` branch merge | Tech Leads only | (via branch policy) |
| Pipelines | DevOps Engineers | Build Administrator |
| Service Connections | DevOps Engineers | Administrator |
| Environments (prod/UAT) | DevOps Leads | Approvers |

---

## 7. Secrets Management from Day 1

Set up Key Vault **before** writing a single line of app code. The cost of retrofitting is always higher.

```
  WRONG (don't do this):
  ┌────────────────────────────┐
  │ app.config                  │
  │ DB_PASSWORD = "abc123"     │ ← hardcoded secret in code
  │ API_KEY = "sk-xxxxx"       │ ← committed to git
  └────────────────────────────┘

  RIGHT:
  ┌───────────────────────────────────────────────────────┐
  │  Key Vault: kv-myapp-prod                             │
  │  ├── Secret: db-password (set once, app reads at     │
  │  │           runtime via managed identity)            │
  │  └── Secret: api-key                                 │
  │                                                       │
  │  App (Managed Identity) ─► Key Vault ─► secret value │
  │  App code contains NO credentials                    │
  └───────────────────────────────────────────────────────┘
```

### Secrets setup checklist for Day 1

- [ ] Create Key Vault per environment (dev/staging/prod)
- [ ] Enable RBAC mode (not legacy Access Policies)
- [ ] Enable soft delete + purge protection on prod vault
- [ ] Enable private endpoint for prod vault (no public access)
- [ ] Assign `Key Vault Secrets User` to all app managed identities
- [ ] Link Key Vault to Azure DevOps variable group
- [ ] Document which secret names exist in the vault (not their values)
- [ ] Never store secrets in pipeline YAML files — use variable groups

---

## 8. Environment Strategy

Define your environments before writing pipelines. Each env should be isolated.

```
  ┌────────┬───────────┬────────────────────────────────────────────────────┐
  │  Env   │  Purpose  │  Rules                                              │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  Dev   │  Active   │  Developers can deploy freely. Broken is OK.        │
  │        │  dev work │  No approval needed. Cheap SKU (Free/Basic tier)   │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  QA    │  Test by  │  Automated test suite must pass before deploy.      │
  │        │  QA team  │  QA lead sign-off. Matches prod infra config        │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  UAT   │  Customer │  Stakeholder / product owner approval.              │
  │        │  testing  │  No auto-deploy — manual trigger after QA pass     │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  Staging│ Pre-prod │  Mirrors production exactly (same SKU, same data   │
  │        │ validation│  anonymized). Multi-approval (lead + DevOps lead)  │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  Prod  │  Live     │  Multi-approval: CAB + DevOps Lead + PM.           │
  │        │  users    │  Blue-Green deployment. 7-day post-deploy monitor  │
  ├────────┼───────────┼────────────────────────────────────────────────────┤
  │  DR    │  Disaster │  Sync from prod after each prod deployment.        │
  │        │  recovery │  Enterprise Release Manager approval only.         │
  └────────┴───────────┴────────────────────────────────────────────────────┘
```

**Key rule:** Prod and Staging must use the same SKU (same tier, same settings). Testing on a Free tier, then deploying to Premium and hoping it works = wrong.

---

## 9. Tagging Strategy

Tags are how you slice costs, track ownership, and enforce governance. Define them day 1 or you'll spend months backfilling.

### Mandatory tags (enforce via Azure Policy)

| Tag Key | Example Values | Purpose |
|---------|---------------|---------|
| `environment` | `dev`, `staging`, `prod`, `dr` | Filter costs by env |
| `project` | `payment-gateway`, `auth-service` | Group resources by project |
| `owner` | `alice@company.com` | Who to contact when something breaks |
| `team` | `backend`, `platform`, `devops` | Team ownership |
| `cost-center` | `CC-1234` | Finance billing allocation |
| `created-by` | `terraform`, `az-cli`, `portal` | Track how resource was provisioned |
| `managed-by` | `terraform`, `manual` | Know what's IaC vs manual |

```bash
# Apply tags to a resource group
az group update \
    --name rg-myapp-prod-eastus \
    --tags environment=prod project=payment-gateway \
           owner=alice@company.com team=backend cost-center=CC-1234

# Enforce mandatory tags via Azure Policy
az policy assignment create \
    --name "require-tags" \
    --policy "Require-Specified-Tag" \
    --params '{"tagName": {"value": "environment"}}'
```

---

## 10. Cost Management

Set up budgets and alerts **before** engineers start deploying. Surprise bills are avoidable.

```
  ┌───────────────────────────────────────────────────────────┐
  │  Cost Management Checklist — Day 1                        │
  │                                                           │
  │  1. Set a budget for each environment                     │
  │     dev: $100/month, staging: $200/month, prod: $500     │
  │                                                           │
  │  2. Set budget alerts at 50% / 80% / 100%                │
  │     Alert email: devops-team@company.com                  │
  │                                                           │
  │  3. Enable lifecycle management on storage                │
  │     → Move blobs > 30 days to Cool tier                  │
  │     → Move blobs > 90 days to Archive tier               │
  │     → Delete blobs > 365 days                            │
  │                                                           │
  │  4. Use spot/low-priority VMs for dev/build agents        │
  │                                                           │
  │  5. Tag everything → filter cost reports by tag           │
  │                                                           │
  │  6. Set up weekly cost report email from Azure            │
  │     Cost Management → Budgets → Add alert                │
  └───────────────────────────────────────────────────────────┘
```

```bash
# Create a budget alert
az consumption budget create \
    --budget-name "budget-prod" \
    --amount 500 \
    --time-grain Monthly \
    --start-date 2026-08-01 \
    --end-date 2027-07-31 \
    --resource-group rg-myapp-prod-eastus \
    --notifications '[{
        "enabled": true,
        "operator": "GreaterThan",
        "threshold": 80,
        "contactEmails": ["devops@company.com"]
    }]'
```

---

## 11. Security from Day 1

Security decisions made later cost 10x more than making them upfront.

### Security checklist — before first deployment

- [ ] **MFA enabled** for ALL users — no exceptions, not even admins
- [ ] **Microsoft Defender for Cloud** enabled on subscription (free tier at minimum)
- [ ] **Azure Policy** — enforce no public IPs on VMs, require HTTPS on App Services
- [ ] **Resource locks** on production — `CanNotDelete` on prod resource group
- [ ] **Enable audit logs** — Azure Activity Log, Key Vault audit logs, AKS audit logs
- [ ] **No storage account public blob access** — disable at subscription level via Policy
- [ ] **Enable soft delete** on Key Vault and Storage (7-90 day recovery window)
- [ ] **Container image scanning** — enable ACR image scanning (Microsoft Defender)
- [ ] **Branch protection** — configured before first dev pushes (see §5)
- [ ] **Secrets scanning** — gitleaks or similar configured in pre-commit hook + PR pipeline
- [ ] **DAST/SAST** — at least one static analysis tool in the CI pipeline

### Network security from day 1

```
  ┌──────────────────────────────────────────────────────┐
  │  NETWORK SECURITY BASELINE                           │
  │                                                      │
  │  ✅ NSGs on all subnets (deny-all inbound default)   │
  │  ✅ No SSH/RDP (22/3389) open to internet            │
  │     → Use Azure Bastion instead                     │
  │  ✅ Databases in private subnet only                 │
  │  ✅ Key Vault via private endpoint                   │
  │  ✅ Storage via private endpoint for prod            │
  │  ✅ All public IPs use Standard SKU                  │
  │  ✅ Enable DDoS protection for prod (if budget allows)│
  └──────────────────────────────────────────────────────┘
```

---

## 12. Service Connections — Use OIDC, Not Secrets

This is the #1 security improvement most teams skip.

### Old way (service principal with secret) — AVOID

```
  Azure DevOps Pipeline
      → authenticates to Azure using CLIENT_ID + CLIENT_SECRET
      → secret stored in variable group
      → secret EXPIRES after 1-2 years (breaks pipeline silently)
      → secret can be stolen from logs if masked incorrectly
```

### New way (OIDC / Workload Identity Federation) — PREFERRED

```
  Azure DevOps Pipeline
      → requests a short-lived OIDC token from Entra ID
      → no secret stored anywhere
      → token valid for minutes only
      → no rotation needed, no expiry risk

  Setup:
  1. Create service connection in Azure DevOps
     → Select "Workload Identity Federation (automatic)"
  2. Azure DevOps creates the App Registration + Federated Credential
  3. Assign the app registration "Contributor" on the resource group
  Done. No secret. No expiry. ✅
```

```bash
# Verify OIDC service connection works
az login --service-principal \
    --username <client-id> \
    --federated-token <oidc-token> \
    --tenant <tenant-id>
```

---

## 13. DevOps Gotchas ⚠️

### 1. Storage account names cannot have hyphens
```
  WRONG: st-myapp-prod-eastus  → invalid!
  RIGHT: stmyappprodeus        → valid (3-24 chars, lowercase + digits only)
```
Also: storage account names are **globally unique** across all of Azure. Add random suffix if needed.

### 2. Plan your VNet IP address space on Day 1
```
  Once resources are deployed, you CANNOT resize a VNet's address space
  without downtime. Plan generously from the start.

  Bad: 10.0.0.0/24  → only 254 usable IPs → runs out with AKS
  Good: 10.0.0.0/16 → 65,534 usable IPs → room to grow
```
Also: peered VNets CANNOT have overlapping address spaces.

### 3. Branch policies are off by default — turn them on before Day 1 coding
If you wait until after engineers start pushing, you'll have to clean up a messy commit history.

### 4. Contributor role at subscription level gives pipeline access to everything
Scope service connection permissions to the **resource group**, not the subscription.

### 5. Key Vault names are globally unique AND soft-deleted names are reserved
If you delete a Key Vault and try to create a new one with the same name, it fails — the soft-deleted vault holds the name. Purge it first: `az keyvault purge --name kv-myapp-prod`.

### 6. AKS node pool subnet needs to be large — plan for pods
With Azure CNI, every pod gets a VNet IP. A 10-node cluster with 30 pods per node = 300 IPs minimum. Use /21 (2048 IPs) for production AKS subnets.

### 7. Lower TTL before ANY DNS migration
If you're pointing a domain to a new IP:
1. Lower TTL to 60 seconds → wait 24 hours
2. Change the A/CNAME record
3. Raise TTL back after confirming it works
Skipping step 1 = users stuck on old IP for up to 24 hours.

### 8. Resource locks on prod resource group — or someone will delete something accidentally
```bash
# Prevent deletion of prod resource group
az lock create \
    --name "lock-prod-nodelete" \
    --resource-group rg-myapp-prod-eastus \
    --lock-type CanNotDelete
```

### 9. Never use App Service Free/Shared tier for anything that matters
- No custom domain support
- No TLS (HTTPS)
- No deployment slots
- No auto-scale
- No VNet integration
Use Basic (B1) minimum for dev, Standard (S1+) for anything customer-facing.

### 10. Set up monitoring before prod launch — not after the first incident
You want dashboards and alerts ready before traffic arrives. Setting up monitoring after an incident is how you discover you've lost hours of logs.

---

*Source: [Azure DevOps Index](../azure-devops/index.md) · [Phase 1: Fundamentals](../azure-devops/phase-01-fundamentals.md) · [Phase 2: GitFlow](../azure-devops/phase-02-gitflow.md) · [Phase 12: Security](../azure-devops/phase-12-security-compliance.md) · [Azure Handbook](../azure/azure_handbook.md)*
