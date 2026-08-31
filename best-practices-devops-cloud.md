# Best Practices for Cloud & DevOps Technologies

A comprehensive reference of best practices with reasoning for each.

---

## Table of Contents

1. [Azure](#1-microsoft-azure)
2. [AWS](#2-amazon-web-services-aws)
3. [GCP](#3-google-cloud-platform-gcp)
4. [Git](#4-git)
5. [GitHub](#5-github)
6. [Docker](#6-docker)
7. [Terraform](#7-terraform)
8. [Kubernetes](#8-kubernetes)
9. [CI/CD General](#9-cicd-general)
10. [Security (Cross-Platform)](#10-security-cross-platform)

---

## 1. Microsoft Azure

### 1.1 Resource Organization

| Best Practice | Reason |
|---|---|
| **Use Management Groups, Subscriptions, and Resource Groups hierarchically** | Provides a structured governance model; policies and RBAC applied at higher levels are inherited, reducing repetitive configuration and ensuring consistent compliance. |
| **Adopt a consistent naming convention** (e.g., `<env>-<region>-<app>-<resource>`) | Makes resources instantly identifiable, simplifies searching, scripting, billing analysis, and onboarding new team members. |
| **Tag every resource** with `environment`, `owner`, `cost-center`, `project` | Enables accurate cost allocation, automated lifecycle management (e.g., auto-shutdown dev VMs), and compliance auditing. |
| **Use separate subscriptions for Dev / Staging / Production** | Provides hard blast-radius boundaries — a misconfigured policy or quota exhaustion in Dev cannot impact Production. |

### 1.2 Identity & Access

| Best Practice | Reason |
|---|---|
| **Use Azure AD (Entra ID) for centralized identity** | Single source of truth for authentication; avoids scattered local accounts that are hard to audit and revoke. |
| **Enforce MFA for all users, especially admins** | Compromised passwords alone won't grant access; prevents the #1 attack vector (credential theft). |
| **Apply least-privilege RBAC** — prefer built-in roles before custom | Minimizes the attack surface; built-in roles are maintained by Microsoft with appropriate scope. |
| **Use Managed Identities instead of service principal secrets** | Eliminates the need to store and rotate credentials; Azure handles the token lifecycle automatically. |
| **Enable Privileged Identity Management (PIM) for admin roles** | Provides just-in-time access; admins only get elevated privileges when needed, with time-bound activation and audit trails. |

### 1.3 Networking

| Best Practice | Reason |
|---|---|
| **Use Hub-and-Spoke VNet topology** | Centralizes shared services (firewall, DNS, VPN gateways) while isolating workloads; reduces cost and complexity vs. full mesh. |
| **Deploy Azure Firewall or NVA in the hub** | All traffic flows through a single inspection point for logging, threat detection, and policy enforcement. |
| **Use Private Endpoints for PaaS services** | Keeps traffic on the Microsoft backbone; prevents data exposure over the public internet. |
| **Enable NSG Flow Logs and send to Log Analytics** | Provides network-level visibility for troubleshooting, security investigations, and compliance audits. |

### 1.4 Compute & Storage

| Best Practice | Reason |
|---|---|
| **Use Availability Zones for production workloads** | Protects against datacenter-level failures; Azure guarantees 99.99% VM SLA with AZs. |
| **Enable Azure Backup and test restores periodically** | Backups are useless if they can't be restored; periodic testing ensures RTO/RPO targets are actually achievable. |
| **Use Managed Disks over unmanaged disks** | Azure handles storage account management, replication, and availability automatically; simpler and more reliable. |
| **Enable soft delete on storage accounts and Key Vaults** | Protects against accidental or malicious deletion; allows recovery within the retention period. |

### 1.5 Monitoring & Cost

| Best Practice | Reason |
|---|---|
| **Enable Azure Monitor, Application Insights, and Log Analytics** | Provides end-to-end observability (metrics, logs, traces); critical for detecting issues before users report them. |
| **Set budget alerts at the subscription and resource group level** | Prevents bill shock; alerts the team before spending exceeds expectations, allowing corrective action. |
| **Use Azure Advisor recommendations** | Free, automated analysis of your resources for cost, performance, reliability, and security improvements. |
| **Right-size VMs using Azure Monitor metrics** | Many VMs are over-provisioned; right-sizing can cut compute costs by 30–60% without performance impact. |

---

## 2. Amazon Web Services (AWS)

### 2.1 Account & Organization

| Best Practice | Reason |
|---|---|
| **Use AWS Organizations with Service Control Policies (SCPs)** | Enforces guardrails across all accounts; prevents individual accounts from performing dangerous actions (e.g., disabling CloudTrail). |
| **Separate accounts per environment and workload** | Provides strong isolation; blast radius is limited to a single account. Billing and IAM boundaries are clear. |
| **Enable AWS CloudTrail in all regions** | Every API call is recorded; essential for security investigation, compliance (SOC2, HIPAA), and troubleshooting. |
| **Set up a centralized logging account** | Prevents an attacker from deleting logs in a compromised account; ensures immutable audit trail. |

### 2.2 IAM

| Best Practice | Reason |
|---|---|
| **Never use the root account for daily tasks** | Root has unrestricted access and cannot be limited by IAM policies; compromise of root = total account takeover. |
| **Use IAM Roles instead of long-lived access keys** | Roles provide temporary credentials that auto-rotate; access keys are static and frequently leaked in code repos. |
| **Apply least-privilege policies using IAM Access Analyzer** | Access Analyzer reviews actual usage and recommends tighter policies; reduces over-permissioned identities. |
| **Enforce MFA on all human IAM users** | Adds a second authentication factor; critical since passwords alone are frequently compromised. |
| **Use Permission Boundaries for delegated admin** | Limits the maximum permissions a delegated admin can grant; prevents privilege escalation. |

### 2.3 Networking

| Best Practice | Reason |
|---|---|
| **Use VPC for all resources; avoid EC2-Classic** | VPCs provide network isolation, subnets, security groups, and NACLs; EC2-Classic is a shared flat network (deprecated). |
| **Place databases and internal services in private subnets** | Prevents direct internet exposure; access is only possible through bastion hosts, VPN, or internal load balancers. |
| **Use VPC Endpoints for AWS services (S3, DynamoDB, etc.)** | Traffic stays on the AWS network; avoids NAT Gateway costs and reduces exposure to internet-based attacks. |
| **Enable VPC Flow Logs** | Network-level audit trail for security analysis, troubleshooting connectivity issues, and detecting anomalies. |

### 2.4 Compute & Storage

| Best Practice | Reason |
|---|---|
| **Use Auto Scaling Groups with launch templates** | Automatically adjusts capacity to demand; maintains availability during spikes and reduces cost during low usage. |
| **Enable S3 bucket versioning and block public access by default** | Versioning protects against accidental deletion/overwrite; blocking public access prevents the #1 cause of S3 data breaches. |
| **Encrypt data at rest using KMS (CMKs) and in transit using TLS** | Meets compliance requirements; protects data even if physical media or network traffic is intercepted. |
| **Use Reserved Instances or Savings Plans for steady-state workloads** | Can reduce compute costs by 40–72% compared to On-Demand pricing. |

### 2.5 Monitoring

| Best Practice | Reason |
|---|---|
| **Use CloudWatch Alarms, Logs, and Dashboards** | Centralized observability; alarms enable automated response (e.g., scaling, SNS notifications) before issues impact users. |
| **Enable AWS Config for resource configuration tracking** | Records configuration changes over time; essential for compliance audits and identifying when drift occurred. |
| **Use AWS Trusted Advisor** | Automated checks for cost optimization, security, fault tolerance, and service limits. |

---

## 3. Google Cloud Platform (GCP)

### 3.1 Organization & Projects

| Best Practice | Reason |
|---|---|
| **Use GCP Organization node with folders for departments/environments** | Provides hierarchical policy inheritance (IAM, org policies); ensures consistent governance across hundreds of projects. |
| **One project per application per environment** | Projects are the billing and IAM boundary in GCP; separation prevents accidental cross-environment access and simplifies cost tracking. |
| **Enable Organization Policy Constraints** (e.g., restrict VM external IPs) | Prevents misconfigurations at the org level; individual projects cannot override these constraints. |
| **Use labels on all resources** (`env`, `team`, `app`) | Labels are GCP's primary mechanism for cost allocation, filtering, and automation scripting. |

### 3.2 IAM

| Best Practice | Reason |
|---|---|
| **Follow the principle of least privilege; use predefined roles** | Predefined roles are granularly scoped; custom roles require ongoing maintenance and can drift. |
| **Use Service Accounts with Workload Identity (for GKE)** | Avoids storing service account keys; GKE pods get GCP credentials via Kubernetes-native identity federation. |
| **Avoid exporting service account keys** | Keys are long-lived credentials that can be leaked; prefer Workload Identity Federation for external systems. |
| **Enable IAM Recommender** | Analyzes actual permission usage and suggests removing unused permissions; automates least-privilege enforcement. |

### 3.3 Networking

| Best Practice | Reason |
|---|---|
| **Use Shared VPC for multi-project networking** | Centralizes network administration in a host project; spoke projects consume subnets without managing routes, firewalls, or VPNs. |
| **Use Private Google Access and Private Service Connect** | Allows VMs without external IPs to reach Google APIs; keeps all traffic private and reduces attack surface. |
| **Implement Cloud Armor for public-facing services** | Provides DDoS protection and WAF capabilities; essential for internet-facing applications. |

### 3.4 Compute & Data

| Best Practice | Reason |
|---|---|
| **Use Managed Instance Groups (MIGs) with autoscaling** | Automatic healing (replaces unhealthy instances), rolling updates, and cost optimization through scale-in. |
| **Enable Customer-Managed Encryption Keys (CMEK) for sensitive data** | Gives you control over key rotation and revocation; meets regulatory requirements beyond Google-managed keys. |
| **Use Cloud Storage lifecycle policies** | Automatically transitions objects to cheaper storage classes or deletes them; prevents unbounded storage cost growth. |
| **Enable Committed Use Discounts for steady-state workloads** | 1- or 3-year commitments can save up to 57% on compute and memory costs. |

### 3.5 Monitoring

| Best Practice | Reason |
|---|---|
| **Use Cloud Monitoring, Cloud Logging, and Cloud Trace** | GCP's native observability stack; provides metrics, logs, and distributed tracing in one integrated platform. |
| **Enable Audit Logs (Admin Activity + Data Access)** | Records who did what, when, and where; Admin Activity logs are always on; Data Access logs must be explicitly enabled. |
| **Set up log sinks to a separate project for security** | Prevents an attacker with project-level access from deleting forensic evidence. |

---

## 4. Git

### 4.1 Branching & Workflow

| Best Practice | Reason |
|---|---|
| **Adopt a branching strategy** (Git Flow, GitHub Flow, or Trunk-Based) | Provides a shared team convention for when and how to branch, merge, and release; avoids chaos. |
| **Use short-lived feature branches** | Long-lived branches diverge significantly from `main`, leading to painful merge conflicts and integration risk. |
| **Merge via Pull/Merge Requests, not direct pushes to main** | Enables code review, CI checks, and audit trail before code reaches the main branch. |
| **Rebase or squash before merging to main** | Keeps the main branch history linear and readable; each commit represents a logical change. |
| **Delete branches after merging** | Prevents branch clutter; stale branches confuse the team about what's active. |

### 4.2 Commits

| Best Practice | Reason |
|---|---|
| **Write meaningful commit messages** (imperative mood, `<type>: <description>`) | Good messages act as documentation; `git log` and `git blame` become powerful debugging tools. |
| **Make small, atomic commits** (one logical change per commit) | Easier to review, revert, cherry-pick, and bisect; large commits hide bugs and make rollbacks risky. |
| **Never commit secrets, credentials, or API keys** | Once committed, secrets are in the history forever (even after deletion); automated scanners constantly harvest exposed keys. |
| **Use `.gitignore` to exclude build artifacts, IDE files, and OS files** | Keeps the repo clean; prevents platform-specific or generated files from polluting diffs and causing merge conflicts. |

### 4.3 Repository Hygiene

| Best Practice | Reason |
|---|---|
| **Use signed commits (GPG/SSH)** | Verifies the identity of the committer; prevents impersonation in the commit history. |
| **Don't store large binary files in Git; use Git LFS** | Git stores every version of every file; large binaries bloat the repo, slow clones, and waste disk/network. |
| **Tag releases with semantic versioning** (`v1.2.3`) | Provides an immutable reference point; tools and CI can trigger on tags for builds and deployments. |
| **Protect the `main` / `master` branch** | Prevents force pushes and accidental deletion; enforces that all changes go through the review process. |

---

## 5. GitHub

### 5.1 Repository Settings

| Best Practice | Reason |
|---|---|
| **Enable branch protection rules on `main`** (require PR, status checks, reviews) | Prevents direct pushes; ensures every change is reviewed and passes CI before merging. |
| **Require at least 1–2 approving reviews** | Catches bugs, knowledge silos, and security issues; spreads understanding of the codebase across the team. |
| **Enable CODEOWNERS file** | Automatically assigns the right reviewers based on file paths; ensures domain experts review their area of the code. |
| **Use issue and PR templates** | Standardizes information provided (steps to reproduce, testing done, screenshots); reduces back-and-forth. |

### 5.2 Security

| Best Practice | Reason |
|---|---|
| **Enable Dependabot for dependency vulnerability alerts and auto-updates** | Keeps dependencies patched; known vulnerabilities in dependencies are a top attack vector. |
| **Enable secret scanning and push protection** | Blocks commits containing secrets before they reach the repo; retroactively scanning is too late. |
| **Use GitHub Actions OIDC for cloud deployments (no stored secrets)** | Eliminates long-lived cloud credentials in GitHub; uses short-lived tokens via federated identity. |
| **Set repositories to private by default** | Prevents accidental exposure of proprietary code; make repos public only when intentional. |

### 5.3 GitHub Actions

| Best Practice | Reason |
|---|---|
| **Pin action versions to a specific SHA, not a tag** (`actions/checkout@<sha>`) | Tags are mutable and can be hijacked; SHA pinning guarantees you run exactly the code you audited. |
| **Use reusable workflows and composite actions for DRY CI** | Reduces duplication across repos; changes to shared logic propagate automatically. |
| **Limit `GITHUB_TOKEN` permissions with `permissions:` block** | Default token has broad permissions; restricting them follows least-privilege and limits damage from compromised workflows. |
| **Use environments with required reviewers for production deployments** | Adds a manual approval gate; prevents accidental production deployments from a mis-merged PR. |
| **Cache dependencies** (`actions/cache`) | Dramatically speeds up CI builds; avoids re-downloading the same packages on every run. |

---

## 6. Docker

### 6.1 Image Building

| Best Practice | Reason |
|---|---|
| **Use official, minimal base images** (e.g., `alpine`, `distroless`, `slim`) | Smaller attack surface, fewer vulnerabilities, faster pulls and deployments. |
| **Use multi-stage builds** | Final image contains only the runtime and compiled artifacts; build tools, source code, and dev dependencies are discarded. |
| **Pin base image versions** (`python:3.12-slim`, NOT `python:latest`) | `latest` is a moving target; your build may break unexpectedly when the base image updates. Reproducibility is critical. |
| **Order Dockerfile instructions by change frequency** (least → most) | Docker caches layers; putting frequently changed steps (e.g., `COPY . .`) last maximizes cache hits and speeds up builds. |
| **Use `.dockerignore`** | Prevents sending unnecessary files (`.git`, `node_modules`, docs) to the build context; speeds up builds and reduces image size. |
| **Don't install unnecessary packages** | Every package is a potential vulnerability; keep images lean and purpose-built. |

### 6.2 Security

| Best Practice | Reason |
|---|---|
| **Run containers as a non-root user** (`USER appuser`) | Root inside the container can escalate to root on the host in misconfigured setups; non-root limits blast radius. |
| **Scan images for vulnerabilities** (Trivy, Snyk, Docker Scout) | Catches known CVEs in OS packages and language libraries before deployment; shift security left. |
| **Never store secrets in images or Dockerfiles** | Images are distributable artifacts; anyone with pull access can extract secrets from layers. Use runtime secret injection. |
| **Use read-only filesystem where possible** (`--read-only`) | Prevents malware from writing to the container filesystem; forces explicit declaration of writable volumes. |
| **Sign images and verify signatures** (Docker Content Trust / cosign) | Ensures the image hasn't been tampered with between build and deployment. |

### 6.3 Runtime & Operations

| Best Practice | Reason |
|---|---|
| **Set resource limits** (`--memory`, `--cpus`) | Prevents a single container from consuming all host resources (noisy neighbor problem); essential for multi-tenant hosts. |
| **Use health checks** (`HEALTHCHECK` instruction) | Enables orchestrators (Docker Compose, Kubernetes) to detect and restart unhealthy containers automatically. |
| **Log to stdout/stderr, not to files inside the container** | Enables log aggregation by Docker, Kubernetes, and centralized logging systems; container filesystem is ephemeral. |
| **Use Docker Compose for local multi-container development** | Defines the full stack (app, DB, cache, queue) in one file; `docker compose up` reproduces the environment consistently. |
| **Use named volumes for persistent data** | Data survives container restarts and recreation; bind mounts are platform-dependent and harder to manage. |

---

## 7. Terraform

### 7.1 Project Structure

| Best Practice | Reason |
|---|---|
| **Organize code into modules** (one per logical component) | Promotes reusability, encapsulation, and separation of concerns; large monolithic configs are unmaintainable. |
| **Separate environments using workspaces or directory structure** | Prevents accidental changes to Production when you intended to modify Dev; clear boundary enforcement. |
| **Use a consistent file layout**: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf` | Team members know exactly where to find resources, variables, and outputs; reduces onboarding time. |
| **Store modules in a separate repo or registry** | Enables versioning and reuse across teams; consumers pin to a specific module version for stability. |

### 7.2 State Management

| Best Practice | Reason |
|---|---|
| **Use remote backend** (S3 + DynamoDB, Azure Blob, GCS) | Local state files are easily lost, can't be shared, and don't support locking; remote backends solve all three. |
| **Enable state locking** | Prevents concurrent `terraform apply` from corrupting state; DynamoDB (AWS) or native locking (Azure/GCS) provides this. |
| **Encrypt state at rest and in transit** | State contains sensitive data (resource IDs, connection strings, sometimes passwords); encryption is mandatory. |
| **Never commit `terraform.tfstate` to version control** | State files contain secrets and are frequently updated; they belong in a remote backend, not Git. |
| **Use `terraform state` commands carefully; back up before modifications** | Direct state manipulation can orphan or destroy resources; always back up first. |

### 7.3 Code Quality

| Best Practice | Reason |
|---|---|
| **Use `terraform fmt` and `terraform validate` in CI** | Enforces consistent formatting and catches syntax/type errors before `plan`; fast feedback loop. |
| **Use `terraform plan` before every `apply`; review the plan** | Shows exactly what will change; prevents surprises like accidental resource destruction. |
| **Pin provider versions** (`required_providers` with `~>` constraint) | Uncontrolled provider upgrades can introduce breaking changes; pinning ensures reproducible builds. |
| **Pin module versions** | Same reasoning as providers; a module update could change behavior or destroy resources. |
| **Use variables with types, descriptions, and validations** | Self-documenting code; validation blocks catch invalid input early rather than failing mid-apply. |
| **Use `terraform-docs` to auto-generate module documentation** | Keeps documentation in sync with code; reduces manual documentation effort. |

### 7.4 Security

| Best Practice | Reason |
|---|---|
| **Never hardcode secrets in `.tf` files** | Terraform files are committed to Git; secrets in code = secrets in history forever. |
| **Use `sensitive = true` for secret outputs** | Prevents Terraform from displaying secret values in CLI output and logs. |
| **Inject secrets via environment variables or secret managers** (Vault, AWS SSM, Azure Key Vault) | Secrets are resolved at runtime; no static credentials in code or state. |
| **Run policy-as-code** (OPA/Sentinel/Checkov) in CI | Catches security violations (e.g., public S3 buckets, unencrypted disks) before `apply`; automated guardrails. |

---

## 8. Kubernetes

### 8.1 Cluster Configuration

| Best Practice | Reason |
|---|---|
| **Use managed Kubernetes** (AKS, EKS, GKE) | Offloads control plane management, patching, and scaling to the cloud provider; reduces operational burden. |
| **Enable RBAC and disable anonymous auth** | Prevents unauthorized access to the API server; RBAC provides granular, auditable access control. |
| **Use namespaces to isolate workloads** | Provides logical separation, resource quotas, and RBAC scoping; prevents teams from interfering with each other. |
| **Keep clusters and nodes updated** | Older versions have known CVEs and miss performance improvements; stay within N-2 of the latest version. |

### 8.2 Workload Best Practices

| Best Practice | Reason |
|---|---|
| **Set resource requests and limits on all containers** | Requests ensure scheduling on nodes with capacity; limits prevent a single pod from starving others (OOMKill, CPU throttle). |
| **Use liveness, readiness, and startup probes** | Kubernetes uses probes to route traffic (readiness), restart unhealthy pods (liveness), and handle slow-starting apps (startup). |
| **Run containers as non-root with read-only root filesystem** | Reduces the impact of container breakout vulnerabilities; defense-in-depth. |
| **Use Deployments (not bare Pods) for stateless workloads** | Deployments provide rolling updates, rollbacks, replica management, and self-healing; bare Pods don't restart if the node fails. |
| **Use Pod Disruption Budgets (PDBs)** | Ensures a minimum number of pods remain available during voluntary disruptions (node upgrades, scaling). |

### 8.3 Security

| Best Practice | Reason |
|---|---|
| **Use Network Policies to restrict pod-to-pod traffic** | By default, all pods can talk to all pods; Network Policies enforce micro-segmentation (zero-trust networking). |
| **Use Secrets management** (external-secrets, Sealed Secrets, or CSI Secret Store Driver) | Kubernetes Secrets are base64-encoded, not encrypted; external secret managers provide encryption, rotation, and auditing. |
| **Scan container images in CI and enforce admission policies** | Prevents deploying images with known vulnerabilities or without signatures; use OPA Gatekeeper or Kyverno. |
| **Enable audit logging on the API server** | Records all API calls; essential for incident response and compliance. |

---

## 9. CI/CD General

| Best Practice | Reason |
|---|---|
| **Automate everything: build, test, scan, deploy** | Manual steps are slow, error-prone, and not auditable; automation ensures consistency and speed. |
| **Run tests in CI on every PR** (unit, integration, linting) | Catches regressions early; developers get fast feedback before merge, not after deployment. |
| **Use trunk-based development with feature flags** | Short-lived branches reduce merge conflicts; feature flags decouple deployment from release. |
| **Implement progressive delivery** (canary, blue-green, rolling) | Reduces blast radius of bad deployments; only a fraction of traffic hits the new version initially. |
| **Make builds reproducible** (pin dependencies, use lock files) | Ensures the same source code always produces the same artifact; eliminates "it worked on my machine." |
| **Store build artifacts in a registry** (container registry, artifact repo) | Provides a single source of truth for deployable artifacts; enables traceability from commit to deployment. |
| **Separate CI (build & test) from CD (deploy)** | CI runs on every commit; CD may require manual approval or environment-specific gates. Separation provides control. |
| **Use Infrastructure as Code for CI/CD pipeline configuration** | Pipeline-as-code is versioned, reviewable, and reproducible; clicking through a UI is not. |

---

## 10. Security (Cross-Platform)

| Best Practice | Reason |
|---|---|
| **Shift security left** — integrate scanning in CI, not just production | Finding a vulnerability in CI costs minutes to fix; finding it in production costs an incident. |
| **Rotate credentials and keys regularly** | Limits the window of exposure if a credential is compromised; automation (Vault, cloud-native rotation) makes this painless. |
| **Encrypt data at rest and in transit** | Protects data from interception (TLS) and theft of physical media or snapshots (at-rest encryption). |
| **Apply the principle of least privilege everywhere** | Every identity (human or machine) should have only the permissions required for its function — nothing more. |
| **Enable centralized logging and monitoring** | A single pane of glass for security events across all platforms; essential for correlation and incident response. |
| **Conduct regular security reviews and penetration tests** | Automated scans catch known issues; human testers find logic flaws, misconfigurations, and novel attack paths. |
| **Maintain an incident response plan and practice it** | When a breach occurs, time is critical; a rehearsed plan reduces mean-time-to-respond (MTTR). |
| **Use a secrets manager** (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) | Centralizes secret storage, provides access auditing, automatic rotation, and encryption; eliminates secrets in code/config. |

---

## Quick Reference Cheat Sheet

```
┌──────────────┬────────────────────────────────────┐
│ Technology   │ Top 3 Takeaways                    │
├──────────────┼────────────────────────────────────┤
│ Azure        │ Managed Identity, RBAC, Hub-Spoke  │
│ AWS          │ No root usage, IAM Roles, SCPs     │
│ GCP          │ Org Policies, Workload Identity,   │
│              │ Shared VPC                         │
│ Git          │ Small commits, no secrets, protect  │
│              │ main branch                        │
│ GitHub       │ Branch protection, Dependabot,     │
│              │ OIDC deployments                   │
│ Docker       │ Multi-stage builds, non-root,      │
│              │ scan images                        │
│ Terraform    │ Remote state, pin versions,        │
│              │ plan before apply                  │
│ Kubernetes   │ RBAC, resource limits, Network     │
│              │ Policies                           │
│ CI/CD        │ Automate all, test in CI,          │
│              │ progressive delivery               │
│ Security     │ Shift left, least privilege,       │
│              │ secrets manager                    │
└──────────────┴────────────────────────────────────┘
```
