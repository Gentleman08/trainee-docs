# 🧩 Intermediate DevOps Terms — Explained

> **~120 terms** you meet once you start building pipelines, containers, Kubernetes, cloud
> networks and monitoring. Each entry has **What**, an **Example**, and a **⚠️** gotcha.
>
> Shaky on basics? Start with [Beginner Terms](beginner-terms.md). Ready for more? Go to [Advanced Terms](advanced-terms.md).

[⬅️ Back to Glossary Index](README.md)

---

## 📑 Table of Contents

1. [CI/CD & Release Practices](#1--cicd--release-practices)
2. [Source Control Workflows](#2--source-control-workflows)
3. [Testing & Code Quality](#3--testing--code-quality)
4. [Containers & Images](#4--containers--images)
5. [Kubernetes Core Objects](#5--kubernetes-core-objects)
6. [Infrastructure as Code & Configuration Management](#6--infrastructure-as-code--configuration-management)
7. [Cloud Networking](#7--cloud-networking)
8. [Web Traffic, Proxies & Certificates](#8--web-traffic-proxies--certificates)
9. [Architecture & Scalability](#9--architecture--scalability)
10. [Messaging & Data](#10--messaging--data)
11. [Monitoring, Logging & Incident Response](#11--monitoring-logging--incident-response)
12. [Security & Identity](#12--security--identity)
13. [Ways of Working](#13--ways-of-working)

---

# 1 — CI/CD & Release Practices

### Pipeline as Code
**What:** Defining CI/CD pipelines in version-controlled files (YAML) instead of clicking in a UI.
**Example:** `.github/workflows/ci.yml`, `azure-pipelines.yml`, `buildspec.yml`, `Jenkinsfile`.
**⚠️** Pipeline changes then go through PR review like any code. See [CI/CD Pipelines guide](../cicd-pipelines/README.md).

### Build Agent / Runner
**What:** The machine (VM/container) that executes pipeline jobs. Either **hosted** by the platform or **self-hosted** by you.
**Example:** `runs-on: ubuntu-latest` (GitHub-hosted); a VM in your VNet as a self-hosted Azure DevOps agent.
**⚠️** Each job usually starts on a fresh machine, so files don't carry over between jobs. Use artifacts.

### Artifact Repository
**What:** A store for build outputs and packages (jars, npm packages, container images, Helm charts).
**Example:** JFrog Artifactory, Sonatype Nexus, Azure Artifacts, AWS CodeArtifact, GitHub Packages, ACR/ECR.
**⚠️** Also use it as a **proxy/cache** for public registries: faster builds, protection against outages and removed packages.

### Build Once, Deploy Many
**What:** Build an artifact one time and promote **that exact artifact** through dev → staging → prod.
**Example:** Image `orders:3f2c1ab` tested in staging is the same digest deployed to prod.
**⚠️** Rebuilding per environment can pull newer dependencies, so you'd ship something untested.

### Environment Promotion
**What:** Moving a release from one environment to the next after checks/approvals.
**Example:** Auto-deploy to dev → automated tests → staging → manual approval → production.
**⚠️** Environment-specific config should come from variables/secrets, not different builds.

### Approval Gate / Manual Intervention
**What:** A pipeline pause that requires a human (or automated check) before continuing.
**Example:** GitHub environment "production" with required reviewers; Azure DevOps environment approvals.
**⚠️** Approvers must actually review. Rubber-stamping makes gates pure delay.

### Semantic Versioning (SemVer)
**What:** `MAJOR.MINOR.PATCH`: breaking change → MAJOR, new feature → MINOR, bug fix → PATCH.
**Example:** `2.4.1 → 2.5.0` (new feature), `2.5.0 → 3.0.0` (breaking API change).
**⚠️** Version ranges like `^2.4.0` accept any 2.x, so a lock file is what keeps builds reproducible.

### Lock File
**What:** A file recording the **exact** versions of every dependency installed.
**Example:** `package-lock.json`, `poetry.lock`, `go.sum`, `Cargo.lock`, `.terraform.lock.hcl`.
**⚠️** Commit it, and use strict install commands in CI (`npm ci`).

### Blue/Green Deployment
**What:** Two identical environments; deploy to the idle one (green), test it, then switch traffic from blue to green.
**Example:** Azure App Service deployment slots swap; ECS + CodeDeploy blue/green.
**⚠️** Instant rollback (switch back), but database changes must work for both versions.

### Canary Deployment
**What:** Send a small percentage of traffic to the new version first, watch metrics, then increase.
**Example:** 5% → 25% → 100% over an hour, aborting if the error rate rises.
**⚠️** Needs good metrics, or you won't notice the canary is sick.

### Rolling Deployment
**What:** Replace instances gradually, a few at a time.
**Example:** Kubernetes Deployment default: `maxSurge: 25%`, `maxUnavailable: 25%`.
**⚠️** Old and new versions run side by side during the rollout, so APIs and schemas must be backward compatible.

### Feature Flag (Feature Toggle)
**What:** A runtime switch that turns functionality on/off without redeploying.
**Example:** LaunchDarkly, Unleash, Azure App Configuration, OpenFeature SDKs: `if flags.isEnabled("new-checkout", user)`.
**⚠️** Clean up flags after rollout, or they become technical debt.

### Rollback vs Roll-Forward
**What:** **Rollback** = return to the previous version. **Roll-forward** = quickly ship a fix on top.
**Example:** `helm rollback orders 0`; or hotfix commit and redeploy in 10 minutes.
**⚠️** Database migrations often make rollback impossible. Plan backward-compatible migrations.

### Smoke Test
**What:** A quick check right after deployment that the most critical paths work.
**Example:** `curl -f https://app/health` and log in with a test account.
**⚠️** Fail the pipeline (and roll back) if smoke tests fail. Don't just log the result.

### Webhook
**What:** An HTTP callback: system A calls a URL on system B when an event happens.
**Example:** GitHub sends a webhook to Jenkins on every push; Stripe calls your API on a payment.
**⚠️** Verify webhook signatures. Anyone can POST to a public URL.

---

# 2 — Source Control Workflows

### Trunk-Based Development
**What:** Everyone integrates small changes into the main branch (trunk) frequently, at least daily, with short-lived branches.
**Example:** PRs live less than a day; incomplete features hide behind flags.
**⚠️** DORA research associates it with higher delivery performance. It requires good automated tests.

### GitFlow
**What:** A branching model with `main`, `develop`, `feature/*`, `release/*` and `hotfix/*` branches.
**Example:** Features merge into `develop`; a `release/1.4` branch stabilises; tags on `main`.
**⚠️** Heavyweight for continuously deployed web apps. Better suited to versioned products with scheduled releases.

### Pull Request (PR) / Merge Request (MR)
**What:** A proposal to merge a branch, with code review, discussion and automated checks.
**Example:** PR must pass CI and get 1 approval before merging to `main`.
**⚠️** Keep PRs small (< ~400 lines). Big PRs get superficial reviews.

### Branch Protection / Rulesets
**What:** Repository rules preventing direct pushes, requiring reviews and passing checks.
**Example:** `main`: no force pushes, require PR + green CI + CODEOWNERS approval.
**⚠️** Configured in repo settings, not in pipeline YAML.

### CODEOWNERS
**What:** A file mapping paths to owners who are automatically requested (or required) as reviewers.
**Example:** `/infra/ @acme/platform-team`.
**⚠️** Protect sensitive paths (`.github/workflows/`, `infra/`) this way.

### Merge vs Rebase vs Squash
**What:** Ways to integrate branches. **Merge** keeps history with a merge commit. **Rebase** replays commits on top for a linear history. **Squash** combines a PR into one commit.
**Example:** Many teams use "squash and merge" for clean `main` history.
**⚠️** Never rebase/force-push branches others are working on.

### Tag / Release
**What:** A **tag** is a named pointer to a specific commit (usually a version). A **release** adds notes and artifacts.
**Example:** `git tag v1.4.2 && git push origin v1.4.2` triggers the release pipeline.
**⚠️** Protect release tags so not everyone can trigger production releases.

### Conventional Commits
**What:** A commit message format: `type(scope): description` (`feat`, `fix`, `docs`, `chore`…).
**Example:** `fix(auth): handle expired refresh tokens`.
**⚠️** Enables automatic changelogs and version bumps (semantic-release, release-please).

### Git Hooks / pre-commit
**What:** Scripts that run at Git events (before commit, before push).
**Example:** The `pre-commit` framework runs formatters, linters and secret scanning before each commit.
**⚠️** Local hooks can be skipped (`--no-verify`). CI must still enforce the same checks.

---

# 3 — Testing & Code Quality

### Test Pyramid
**What:** Lots of fast **unit** tests, fewer **integration** tests, very few slow **end-to-end (e2e)** tests.
**Example:** 2,000 unit (2 min), 200 integration (5 min), 20 e2e (10 min).
**⚠️** An "ice-cream cone" (mostly e2e) gives slow, flaky pipelines.

### Unit / Integration / End-to-End Tests
**What:** **Unit**: one function in isolation. **Integration**: components together (app + real DB). **E2E**: the whole system like a user (browser automation).
**Example:** Jest/pytest (unit), Testcontainers (integration), Playwright/Cypress (e2e).
**⚠️** Integration tests catch what mocks hide, e.g. a SQL query that only fails on real Postgres.

### Flaky Test
**What:** A test that sometimes passes and sometimes fails without code changes.
**Example:** Timing-dependent assertions, shared test data, test-order dependence, timezone assumptions.
**⚠️** Flaky tests teach people to ignore red builds. Quarantine and fix them quickly.

### Code Coverage
**What:** Percentage of code executed by tests (lines/branches).
**Example:** JaCoCo, coverage.py, Istanbul/nyc report 78% line coverage.
**⚠️** High coverage ≠ good tests (tests without assertions count too). Use it as a signal, not a target.

### Linting / Static Analysis
**What:** Automatically checking code for errors, style issues and suspicious patterns without running it.
**Example:** ESLint, Pylint/Ruff, golangci-lint, hadolint (Dockerfiles), tflint, yamllint.
**⚠️** Run linters in CI and pre-commit. Fix or explicitly suppress, never silently ignore.

### SAST / DAST / SCA
**What:** **SAST**: scans source code for vulnerabilities. **DAST**: tests the running app from outside. **SCA**: finds vulnerable dependencies.
**Example:** CodeQL/Semgrep (SAST), OWASP ZAP (DAST), Dependabot/Trivy/Snyk (SCA).
**⚠️** Each finds different issues. Mature pipelines use all three.

### Quality Gate
**What:** A pass/fail threshold a build must meet (coverage, no critical bugs, no new vulnerabilities).
**Example:** SonarQube quality gate fails PRs with new critical issues.
**⚠️** Gate on **new code** to avoid blocking everything on legacy debt.

### Technical Debt
**What:** The future cost of shortcuts taken now (quick hacks, missing tests, outdated dependencies).
**Example:** Framework three major versions behind, so upgrades are now a multi-month project.
**⚠️** Budget regular time to pay it down, or "interest" slows all future work.

---

# 4 — Containers & Images

### Container vs Virtual Machine
**What:** A **VM** virtualises hardware and runs a full guest OS. A **container** shares the host kernel and isolates processes, so it's lighter and starts in seconds.
**Example:** One VM might host 20 containers.
**⚠️** Containers are less isolated than VMs. Untrusted code may need VM-level isolation. See [Docker notes](../docker/README.md).

### Image Layers & Build Cache
**What:** Images are stacks of read-only layers, one per Dockerfile instruction. Unchanged layers are reused from cache.
**Example:** Copy `package.json` and install deps **before** copying source, so code changes don't reinstall deps.
**⚠️** Files deleted in a later layer still take up space in the image.

### Multi-Stage Build
**What:** A Dockerfile with several `FROM` stages: build in a big image, copy only the output into a small runtime image.
**Example:** Go build in `golang:1.23`, copy binary to `distroless/static` (~10 MB).
**⚠️** Smaller images = faster deploys and fewer vulnerabilities. See [Dockerfile Handbook](../docker/dockerfile_handbook/README.md).

### Base Image (slim / alpine / distroless / scratch)
**What:** The starting image in `FROM`. Variants trade size, compatibility and attack surface.
**Example:** `python:3.12-slim` (safe default), `alpine` (tiny, musl), `distroless` (no shell), `scratch` (empty).
**⚠️** Alpine's musl libc breaks some prebuilt packages. Pin versions, never rely on `latest`.

### Container Registry
**What:** A server storing container images.
**Example:** Docker Hub, GHCR, ACR, ECR, Google Artifact Registry, Harbor.
**⚠️** Docker Hub rate-limits anonymous pulls. Authenticate or mirror images.

### Image Tag vs Digest
**What:** A **tag** (`:1.4.2`, `:latest`) is a movable label. A **digest** (`@sha256:…`) identifies exact content.
**Example:** Deploy `orders@sha256:9b1e…` to guarantee the tested image.
**⚠️** Tags can be overwritten. Use immutable tags or digests for production.

### Docker Compose
**What:** A YAML file to define and run multi-container apps locally.
**Example:** `compose.yaml` with api + postgres + redis; `docker compose up`.
**⚠️** Great for dev/CI. Production orchestration is usually Kubernetes or a managed container service.

### Container Runtime (containerd / CRI-O)
**What:** The low-level software that actually runs containers on a node.
**Example:** Kubernetes uses containerd via the CRI (Container Runtime Interface).
**⚠️** Kubernetes removed "dockershim" (1.24), but Docker-built images still run fine. They're standard OCI images.

### OCI (Open Container Initiative)
**What:** Open standards for container image formats, runtimes and registries.
**Example:** Images built by Docker, Buildah or Kaniko all run on containerd because they're OCI images.
**⚠️** OCI registries can also store Helm charts, SBOMs and signatures as "OCI artifacts".

### Rootless / Non-Root Containers
**What:** Running the container process as a non-root user (and optionally the container engine itself without root).
**Example:** `USER 1001` in the Dockerfile; Kubernetes `runAsNonRoot: true`.
**⚠️** Root in a container plus a kernel bug can mean root on the host.

---

# 5 — Kubernetes Core Objects

> Full guide: [Kubernetes Handbook](../kubernetes/kubernetes_handbook.md).

### Cluster / Node / Pod
**What:** A **cluster** is a set of machines (**nodes**) managed by Kubernetes. A **pod** is the smallest deployable unit: one or more containers sharing network and storage.
**Example:** 3-node AKS cluster running 40 pods.
**⚠️** Pods are disposable. Never rely on a specific pod or its IP staying around.

### Deployment / ReplicaSet
**What:** A **Deployment** declares the desired state for stateless pods (image, replicas, update strategy). It manages **ReplicaSets**, which keep N pods running.
**Example:** `replicas: 3`, rolling update when the image changes.
**⚠️** Use Deployments, not bare pods. Bare pods aren't recreated if a node dies.

### Service (ClusterIP / NodePort / LoadBalancer)
**What:** A stable network name/IP in front of a changing set of pods. **ClusterIP** is internal; **NodePort** opens a port on every node; **LoadBalancer** provisions a cloud load balancer.
**Example:** `orders` Service → DNS `orders.prod.svc.cluster.local` → any healthy orders pod.
**⚠️** Services select pods by **labels**. A label typo gives "no endpoints".

### Ingress / Ingress Controller
**What:** HTTP(S) routing rules (host/path → Service). An **ingress controller** (NGINX, Traefik, cloud gateways) implements them.
**Example:** `api.acme.com/orders` → `orders` Service; TLS via cert-manager.
**⚠️** An Ingress object does nothing without a controller installed. Gateway API is the newer successor.

### Namespace
**What:** A virtual partition inside a cluster for organising and isolating resources.
**Example:** `dev`, `staging` namespaces or one per team; quotas and RBAC per namespace.
**⚠️** Namespaces aren't a hard security boundary by themselves. Add network policies and RBAC.

### ConfigMap / Secret
**What:** **ConfigMap** holds non-sensitive config. **Secret** holds sensitive data (base64-encoded, optionally encrypted at rest).
**Example:** Mounted as env vars or files into pods.
**⚠️** base64 is **not** encryption. Use etcd encryption, RBAC, and external secret stores (CSI driver / External Secrets Operator).

### Volume / PersistentVolume (PV) / PersistentVolumeClaim (PVC) / StorageClass
**What:** **PVC** = a pod's request for storage. **PV** = the actual storage. **StorageClass** = how to provision it dynamically (disk type).
**Example:** PVC `10Gi`, `storageClassName: managed-csi-premium` → Azure Disk created automatically.
**⚠️** Zonal disks bind pods to one zone. Check the reclaim policy (`Delete` removes data when the PVC is deleted).

### StatefulSet
**What:** Manages stateful pods with **stable names** (`db-0`, `db-1`), stable storage per pod and ordered rollout.
**Example:** Kafka, Elasticsearch or Postgres clusters in Kubernetes.
**⚠️** Running databases in Kubernetes needs operators and expertise. Managed DBs are often simpler.

### DaemonSet
**What:** Runs one pod on **every** (or selected) node.
**Example:** Log collectors (Fluent Bit), monitoring agents, CNI plugins.
**⚠️** DaemonSet resource requests multiply by node count. Size them carefully.

### Job / CronJob
**What:** A **Job** runs pods to completion (batch task). A **CronJob** runs Jobs on a schedule.
**Example:** Nightly backup CronJob `0 2 * * *`.
**⚠️** Set `concurrencyPolicy: Forbid` to avoid overlapping runs, and `backoffLimit` to cap retries.

### Liveness / Readiness / Startup Probes
**What:** Health checks: **readiness** = ready for traffic? **liveness** = should it be restarted? **startup** = still booting, don't check liveness yet.
**Example:** `readinessProbe: httpGet /ready`; `livenessProbe: httpGet /healthz`.
**⚠️** A liveness probe that checks the database causes mass restarts during a DB blip. Keep liveness shallow.

### Resource Requests & Limits
**What:** **Requests** = guaranteed amount used for scheduling. **Limits** = the maximum allowed.
**Example:** `requests: {cpu: 250m, memory: 256Mi}`, `limits: {memory: 512Mi}`.
**⚠️** No requests → poor scheduling and first to be evicted. Exceeding memory limits → OOMKilled.

### Labels & Selectors
**What:** Key/value tags on objects, and queries that match them.
**Example:** `app: orders, env: prod`; Service selector `app: orders`.
**⚠️** Labels connect everything (Services, Deployments, policies). Consistent labelling conventions matter.

### Helm / Chart / Release
**What:** **Helm** is Kubernetes' package manager. A **chart** is a templated package. A **release** is an installed instance of a chart.
**Example:** `helm upgrade --install orders ./chart -f values-prod.yaml`.
**⚠️** Helm templating can get complex. Keep values files per environment, and use `--atomic` for auto-rollback.

### Kustomize
**What:** Template-free customisation of Kubernetes YAML using a base + overlays (patches).
**Example:** `base/` deployment; `overlays/prod` sets replicas 5 and the prod image tag. Built into `kubectl apply -k`.
**⚠️** Simpler than Helm for in-house apps. Helm is better for distributing reusable packages.

### kubectl
**What:** The command-line tool to talk to Kubernetes.
**Example:** `kubectl get pods -n prod`, `kubectl logs`, `kubectl describe`, `kubectl rollout status`.
**⚠️** Always check your current context (`kubectl config current-context`) before running commands, so you don't hit prod by accident.

### Managed Kubernetes (AKS / EKS / GKE)
**What:** Cloud services that run the Kubernetes control plane for you.
**Example:** AKS on Azure, EKS on AWS, GKE on Google Cloud.
**⚠️** You still own node upgrades, add-ons, networking design and security configuration.

---

# 6 — Infrastructure as Code & Configuration Management

### Infrastructure as Code (IaC)
**What:** Defining infrastructure in code files that are versioned, reviewed and applied automatically.
**Example:** Terraform/OpenTofu, Bicep, CloudFormation, Pulumi, CDK.
**⚠️** Mixing manual portal changes with IaC causes drift. See [CI/CD IaC chapter](../cicd-pipelines/04-iac.md).

### Terraform Provider / Resource / Module
**What:** A **provider** talks to an API (azurerm, aws). A **resource** is one managed object. A **module** is a reusable group of resources.
**Example:** `module "aks" { source = "./modules/aks" … }`.
**⚠️** Pin provider and module versions.

### Plan / Apply
**What:** **Plan** shows what would change. **Apply** makes the changes.
**Example:** Plan on PR (posted as a comment), apply after merge and approval.
**⚠️** Read plans for `destroy` / `must be replaced`. That's how databases get recreated accidentally.

### Remote State / Backend
**What:** Storing Terraform state in shared, locked storage instead of on a laptop.
**Example:** Azure Storage container, S3 bucket, HCP Terraform.
**⚠️** Local state on one person's laptop = lost state and conflicts.

### Workspaces / Environments in IaC
**What:** Ways to manage several copies of infrastructure (dev/stage/prod): separate directories, workspaces, or stacks.
**Example:** `envs/dev`, `envs/prod` folders calling the same modules with different tfvars.
**⚠️** Keep separate state (and ideally separate credentials) per environment.

### Configuration Management
**What:** Tools that install software and configure servers into a desired state, repeatedly.
**Example:** Ansible (agentless, SSH), Chef, Puppet, SaltStack, PowerShell DSC.
**⚠️** IaC creates the servers; config management configures what's inside. In container-heavy setups, images replace much of it.

### Ansible Playbook / Inventory / Role
**What:** **Playbook** = YAML list of tasks. **Inventory** = which hosts. **Role** = reusable bundle of tasks/templates.
**Example:** `ansible-playbook -i inventory.ini site.yml --check` (dry run).
**⚠️** Use idempotent modules (`apt`, `template`) instead of raw `shell` commands so re-runs are safe.

### Idempotence
**What:** Running the same operation multiple times gives the same result as running it once.
**Example:** `terraform apply` twice → second run makes no changes; Ansible reports `changed=0`.
**⚠️** Non-idempotent scripts ("append this line to the config") break on re-runs.

### Golden Image / Packer
**What:** A pre-baked VM image with OS, patches and software. **Packer** builds them from code.
**Example:** Monthly Packer pipeline builds a hardened Ubuntu image used by all scale sets.
**⚠️** Rebuild images regularly to include security patches.

### GitOps
**What:** Git is the single source of truth for desired state. An agent in the cluster (Argo CD, Flux) continuously syncs the cluster to Git.
**Example:** Merge a PR changing the image tag → Argo CD deploys it; `git revert` = rollback.
**⚠️** CI no longer needs cluster credentials. But secrets need special handling (Sealed Secrets, SOPS, External Secrets).

---

# 7 — Cloud Networking

### VPC / VNet
**What:** Your private, isolated network in the cloud (AWS **VPC**, Azure **VNet**, GCP VPC).
**Example:** `10.0.0.0/16` VNet with subnets for web, app and data tiers.
**⚠️** Plan address ranges up front. Overlapping CIDRs block peering/VPN later.

### CIDR / Subnet
**What:** **CIDR** notation describes an IP range: `10.0.1.0/24` = 256 addresses. A **subnet** is a slice of a VNet/VPC.
**Example:** `/16` = 65,536 addresses; `/24` = 256 (clouds reserve ~5 per subnet).
**⚠️** Kubernetes with VPC-native CNIs consumes many IPs. Size subnets generously.

### Public vs Private Subnet
**What:** A **public** subnet has a route to the internet gateway. A **private** subnet doesn't (outbound goes via NAT).
**Example:** Load balancers in public subnets; app servers and databases in private ones.
**⚠️** Databases should never sit in public subnets with public IPs.

### NAT Gateway
**What:** Lets private resources make **outbound** internet connections without being reachable from the internet.
**Example:** Private VMs download updates via a NAT gateway with a static public IP (useful for partner allow-lists).
**⚠️** NAT data processing charges and SNAT port exhaustion are common surprises.

### Security Group / NSG / Firewall Rules
**What:** Stateful allow/deny rules for traffic to resources (AWS Security Groups, Azure NSGs).
**Example:** Allow 443 from the load balancer to the app tier; deny everything else.
**⚠️** "Temporary" `0.0.0.0/0` rules on SSH/RDP are a classic breach vector.

### Bastion / Jump Host
**What:** A hardened entry point for administrative access to private machines.
**Example:** Azure Bastion, AWS Systems Manager Session Manager (no open SSH ports at all).
**⚠️** Prefer managed, audited access over self-managed jump boxes with shared keys.

### VPC Peering / Transit / Hub-and-Spoke
**What:** Connecting networks. **Peering** links two networks directly. **Hub-and-spoke** routes many spokes through a central hub (firewall, shared services).
**Example:** Azure hub VNet with firewall + VPN gateway; app VNets peer to it. AWS Transit Gateway.
**⚠️** Peering isn't transitive (A↔B and B↔C doesn't mean A↔C).

### VPN / Direct Connect / ExpressRoute
**What:** Ways to connect on-prem to the cloud. **VPN** goes over the internet (encrypted). **Direct Connect** (AWS) / **ExpressRoute** (Azure) are private dedicated links.
**Example:** Site-to-site VPN as backup for ExpressRoute.
**⚠️** Plan redundancy. A single tunnel or circuit is a single point of failure.

### Private Endpoint / PrivateLink
**What:** Accessing a cloud PaaS service (storage, database) through a **private IP in your network** instead of its public endpoint.
**Example:** Storage account reachable only via `10.0.5.4`; public access disabled.
**⚠️** Requires correct **private DNS** zones, which is the #1 private-endpoint troubleshooting issue.

### DNS Records (A, AAAA, CNAME, MX, TXT, NS)
**What:** **A** = name → IPv4; **AAAA** = name → IPv6; **CNAME** = alias to another name; **MX** = mail server; **TXT** = text (verification, SPF); **NS** = delegates a zone.
**Example:** `api.acme.com CNAME acme-api.azurewebsites.net`.
**⚠️** You can't put a CNAME at the zone apex (`acme.com`). Use ALIAS/ANAME records. See [DNS notes](../quick-reference/dns_notes.md).

### TTL (Time To Live)
**What:** How long DNS answers (or cached data) may be cached.
**Example:** Lower TTL to 60 s a day **before** a planned migration.
**⚠️** Changing TTL only takes effect after the old TTL expires.

---

# 8 — Web Traffic, Proxies & Certificates

### Load Balancer (Layer 4 vs Layer 7)
**What:** Distributes traffic across servers. **L4** works with IPs/ports (TCP/UDP). **L7** understands HTTP (paths, headers, cookies).
**Example:** Azure Load Balancer / AWS NLB (L4); Application Gateway / ALB (L7).
**⚠️** Health checks decide which backends get traffic. Make them meaningful but cheap.

### Reverse Proxy
**What:** A server in front of applications that receives client requests and forwards them (TLS termination, routing, caching, compression).
**Example:** NGINX, HAProxy, Envoy, Traefik, Caddy. See [Servers notes](../servers/README.md).
**⚠️** Pass the real client IP via `X-Forwarded-For` and configure the app to trust only your proxy.

### API Gateway
**What:** A managed entry point for APIs: routing, auth, rate limiting, quotas, transformations, analytics.
**Example:** Azure API Management, AWS API Gateway, Kong, Apigee.
**⚠️** Don't put business logic in the gateway. It becomes a hidden monolith.

### CDN (Content Delivery Network)
**What:** A global network of edge servers caching content close to users.
**Example:** Cloudflare, Azure Front Door, CloudFront, Akamai serving images/JS/CSS.
**⚠️** Cache invalidation is hard. Use versioned/fingerprinted filenames for static assets.

### WAF (Web Application Firewall)
**What:** Filters HTTP traffic for attacks (SQL injection, XSS, bots) using rule sets like the OWASP CRS.
**Example:** WAF policy on Front Door/Application Gateway/CloudFront.
**⚠️** Start in detection mode, tune false positives, then switch to prevention.

### TLS / SSL Certificate
**What:** **TLS** encrypts traffic (HTTPS). A **certificate** proves a server's identity, signed by a trusted Certificate Authority (CA).
**Example:** Let's Encrypt via cert-manager; managed certificates on cloud load balancers.
**⚠️** **Expired certificates** cause regular, embarrassing outages. Automate renewal and alert 30 days before expiry.

### TLS Termination / Offloading
**What:** Decrypting HTTPS at a proxy/load balancer and forwarding to backends (plain or re-encrypted).
**Example:** Application Gateway terminates TLS, then re-encrypts to backends (end-to-end TLS).
**⚠️** Compliance often requires re-encryption to the backend, not plain HTTP inside the network.

### Sticky Sessions (Session Affinity)
**What:** The load balancer sends a user's requests to the same backend.
**Example:** Needed for apps storing session state in server memory, and for WebSockets.
**⚠️** Hurts load distribution and failover. Prefer stateless apps with shared session stores (Redis).

### CORS (Cross-Origin Resource Sharing)
**What:** Browser security rules controlling whether a web page from one domain may call an API on another.
**Example:** API returns `Access-Control-Allow-Origin: https://app.acme.com`.
**⚠️** `Access-Control-Allow-Origin: *` with credentials is a security hole (and browsers reject it anyway).

### HTTP Status Codes (essential set)
**What:** 2xx success (200 OK, 201 Created, 204 No Content); 3xx redirect (301, 302, 304); 4xx client error (400, 401 Unauthenticated, 403 Forbidden, 404, 409, 429 Too Many Requests); 5xx server error (500, 502 Bad Gateway, 503 Unavailable, 504 Gateway Timeout).
**Example:** 502 from a load balancer usually means the backend crashed or refused the connection.
**⚠️** 502/504 point at the backend or proxy timeouts. 401 vs 403 = "who are you?" vs "you can't".

---

# 9 — Architecture & Scalability

### Monolith vs Microservices
**What:** A **monolith** is one deployable application. **Microservices** are many small, independently deployable services.
**Example:** Start as a modular monolith; split out services where teams or scaling needs diverge.
**⚠️** Microservices trade code complexity for operational complexity (networking, observability, data consistency).

### Stateless vs Stateful
**What:** **Stateless** services keep no client data between requests (any instance can serve any request). **Stateful** services keep data (DBs, sessions).
**Example:** Web API stateless (sessions in Redis); Postgres stateful.
**⚠️** Stateless services scale and recover easily. Push state into managed data services.

### Horizontal vs Vertical Scaling
**What:** **Horizontal** (scale out) adds more instances. **Vertical** (scale up) makes an instance bigger.
**Example:** HPA adds pods; resize a DB from 4 to 16 vCPU.
**⚠️** Vertical scaling hits limits and often needs a restart. Horizontal needs stateless design.

### Autoscaling
**What:** Automatically adjusting capacity based on metrics or schedules.
**Example:** VM scale sets on CPU; Kubernetes HPA on requests per second; scheduled scale-up before 9 a.m.
**⚠️** Scaling takes time (minutes for VMs). Keep headroom and use predictive or scheduled scaling for known peaks.

### High Availability (HA)
**What:** Designing systems to stay up despite component failures, usually through redundancy across zones.
**Example:** 3 replicas across 3 availability zones behind a zone-redundant load balancer.
**⚠️** HA ≠ backup. Replicas faithfully replicate deletions and corruption too.

### Fault Tolerance vs Resilience
**What:** **Fault tolerance**: continues working with no interruption when parts fail. **Resilience**: recovers quickly and degrades gracefully.
**Example:** RAID disk mirror (fault tolerant); service that serves cached data when the DB is down (resilient).
**⚠️** Full fault tolerance is expensive. Choose per component based on business impact.

### Single Point of Failure (SPOF)
**What:** A component whose failure takes down the whole system.
**Example:** One NAT gateway, one DNS provider, one database without a replica, one person who knows the system.
**⚠️** Look for SPOFs in people and processes too, not just infrastructure.

### Caching
**What:** Storing frequently used data in fast storage to reduce latency and load.
**Example:** Redis/Memcached in front of the DB; HTTP caching; CDN edge caching.
**⚠️** "There are only two hard things in computer science: cache invalidation and naming things." Define TTLs and invalidation.

### Twelve-Factor App
**What:** A methodology for cloud-native apps: config in env vars, stateless processes, logs to stdout, dev/prod parity, disposability, and more.
**Example:** Same image across environments; config injected at runtime.
**⚠️** Still a great checklist for "is this app container/cloud friendly?".

### Serverless
**What:** Running code without managing servers. The platform scales automatically and bills per use.
**Example:** AWS Lambda, Azure Functions, Cloud Run, Azure Container Apps.
**⚠️** Watch cold starts, execution time limits, vendor lock-in, and costs at sustained high volume.

---

# 10 — Messaging & Data

### Message Queue
**What:** A buffer where producers put messages and consumers process them asynchronously; each message goes to one consumer.
**Example:** SQS, Azure Service Bus queues, RabbitMQ.
**⚠️** Design consumers to be idempotent. Messages can be delivered more than once.

### Publish/Subscribe (Pub/Sub)
**What:** Publishers send messages to a **topic**; every subscriber gets a copy.
**Example:** SNS, Service Bus topics, Google Pub/Sub, Kafka topics with consumer groups.
**⚠️** Adding subscribers is easy. Tracking who depends on an event is hard, so document event contracts.

### Event Streaming (Kafka)
**What:** A durable, ordered, replayable log of events, partitioned for scale.
**Example:** Kafka/Event Hubs/Kinesis; consumers track their own offsets and can replay history.
**⚠️** Ordering is only guaranteed **within a partition**. Choose partition keys carefully.

### SQL vs NoSQL
**What:** **SQL** (relational) databases use tables, schemas and joins with strong consistency. **NoSQL** (document, key-value, wide-column, graph) trades some of that for flexibility and scale.
**Example:** Postgres/MySQL/Azure SQL vs MongoDB/Cosmos DB/DynamoDB/Redis/Cassandra.
**⚠️** Choose by access patterns. Relational is a great default for most business data.

### Read Replica
**What:** A copy of a database that serves read queries, kept in sync (usually asynchronously) with the primary.
**Example:** Reports run on the replica so they don't slow down the primary.
**⚠️** Replication lag means replicas may return slightly stale data.

### Database Migration (Schema Migration)
**What:** Versioned scripts that change a database schema in a controlled order.
**Example:** Flyway, Liquibase, Alembic, EF Core migrations, run as a pipeline step.
**⚠️** Never edit an applied migration. Make migrations backward compatible for zero-downtime deploys.

### Connection Pooling
**What:** Reusing a set of open database connections instead of opening a new one per request.
**Example:** PgBouncer for Postgres; HikariCP in Java apps.
**⚠️** 50 pods × 20 connections each = 1,000 connections, which can exceed the database's max. Size pools against DB limits.

### Backup Strategies (Full / Incremental / Differential, 3-2-1)
**What:** **Full** = everything; **incremental** = changes since the last backup; **differential** = changes since the last full. The **3-2-1 rule** = 3 copies, 2 different media, 1 offsite (plus 1 immutable/offline, 0 errors in restore tests).
**Example:** Daily incremental + weekly full + cross-region copy + immutable vault.
**⚠️** A backup that has never been restore-tested isn't a backup.

---

# 11 — Monitoring, Logging & Incident Response

### Metrics / Logs / Traces (the "three pillars")
**What:** **Metrics**: numbers over time (CPU, request rate). **Logs**: timestamped event records. **Traces**: the path of a request across services.
**Example:** Prometheus (metrics), Loki/Elasticsearch/Log Analytics (logs), Jaeger/Tempo/App Insights (traces).
**⚠️** Correlate them with shared IDs (trace ID in logs). See [Advanced: Observability](advanced-terms.md#3--observability-advanced).

### Prometheus / PromQL
**What:** A popular open-source metrics system that **scrapes** `/metrics` endpoints. **PromQL** is its query language.
**Example:** `rate(http_requests_total{status=~"5.."}[5m])`.
**⚠️** Avoid high-cardinality labels (user IDs) in metrics.

### Grafana / Dashboards
**What:** **Grafana** visualises data from Prometheus, Loki, cloud monitors and more.
**Example:** Service dashboard: requests, errors, latency (p50/p95/p99), saturation.
**⚠️** Dashboards are for investigating. Alerts, not people staring at screens, should detect problems.

### Log Aggregation / Centralised Logging
**What:** Collecting logs from all servers/containers into one searchable system.
**Example:** Fluent Bit → Elasticsearch/OpenSearch, Loki, Azure Log Analytics, CloudWatch Logs.
**⚠️** Containers should log to stdout/stderr. Set retention to control costs. Never log secrets or personal data.

### Alerting / Alert Rules
**What:** Conditions on metrics/logs that notify humans or systems.
**Example:** "Error rate > 2% for 5 min → page on-call"; "disk > 85% → ticket".
**⚠️** Page only for urgent, actionable, user-impacting problems.

### On-Call / Rotation / Escalation Policy
**What:** Engineers take turns being reachable to respond to alerts. Escalation policies route unacknowledged alerts onward.
**Example:** PagerDuty/Opsgenie: primary → secondary after 10 minutes → manager after 30.
**⚠️** Sustainable on-call needs low alert noise, good runbooks and compensation/time off.

### Runbook / Playbook
**What:** Step-by-step instructions for handling a known situation.
**Example:** "Disk full on DB server: 1) check largest tables, 2) …".
**⚠️** Link runbooks directly from alerts, and update them after every incident.

### RTO / RPO (intro)
**What:** **RTO** = maximum acceptable downtime. **RPO** = maximum acceptable data loss (as time).
**Example:** RTO 4 h, RPO 15 min for the order system.
**⚠️** These drive backup frequency and DR design. See [Advanced: DR](advanced-terms.md#11--multi-region-dr--data).

### Incident Management Lifecycle
**What:** Detect → triage (severity) → mitigate → resolve → postmortem → follow-up actions.
**Example:** Mitigate first (roll back) and investigate root cause later.
**⚠️** "Restore service first" beats "find the perfect fix while users wait".

### Health Check Endpoint
**What:** A URL (e.g. `/health`, `/ready`) that reports whether the app is working.
**Example:** Load balancers and Kubernetes probes call it every few seconds.
**⚠️** Separate "alive" from "ready". Don't make health checks expensive or dependent on every downstream.

---

# 12 — Security & Identity

### IAM (Identity and Access Management)
**What:** The systems and policies that control **who** (identity) can do **what** (permissions) on **which** resources.
**Example:** Microsoft Entra ID + Azure RBAC; AWS IAM users/roles/policies.
**⚠️** Prefer roles and groups over permissions assigned to individuals.

### RBAC (Role-Based Access Control)
**What:** Permissions are grouped into roles, and roles are assigned to users/groups/identities at a scope.
**Example:** "Reader" on the subscription, "Contributor" on one resource group; Kubernetes `Role` + `RoleBinding`.
**⚠️** Assign at the **narrowest scope** needed. See [Azure RBAC notes](../quick-reference/azure_rbac_notes.md).

### Service Account / Service Principal / Managed Identity
**What:** Non-human identities for apps and automation. **Managed identities** (Azure) / **IAM roles** (AWS) have credentials managed by the cloud, with no secrets to store.
**Example:** App Service uses its managed identity to read Key Vault.
**⚠️** Prefer managed identities/roles over service principals with client secrets.

### Secrets Management
**What:** Storing, accessing, rotating and auditing secrets centrally.
**Example:** Azure Key Vault, AWS Secrets Manager, HashiCorp Vault, Kubernetes External Secrets Operator.
**⚠️** Never put secrets in Git, images or plain pipeline variables.

### Authentication vs Authorization (AuthN vs AuthZ)
**What:** **AuthN** = proving who you are. **AuthZ** = what you're allowed to do.
**Example:** Log in with SSO + MFA (AuthN); RBAC decides you can only read (AuthZ).
**⚠️** HTTP 401 = not authenticated; 403 = authenticated but not authorised.

### OAuth 2.0 / OpenID Connect (OIDC)
**What:** **OAuth 2.0** is a framework for delegated authorization (access tokens). **OIDC** adds identity (ID tokens) on top, for login.
**Example:** "Sign in with Google/Microsoft"; CI pipelines using OIDC tokens to access clouds without secrets.
**⚠️** Validate token audience, issuer and expiry. Never accept unsigned tokens.

### JWT (JSON Web Token)
**What:** A compact, signed token format carrying claims (user, roles, expiry).
**Example:** `Authorization: Bearer eyJhbGciOi…`.
**⚠️** JWTs are signed, **not encrypted** by default. Anyone can read the contents, so don't put secrets in them.

### Encryption at Rest / in Transit
**What:** **At rest**: data encrypted on disk. **In transit**: data encrypted while moving over networks (TLS).
**Example:** Storage service encryption + customer-managed keys; HTTPS + TLS to databases.
**⚠️** Encryption at rest doesn't protect against someone with valid access. Access control still matters.

### Vulnerability / CVE / CVSS
**What:** A **vulnerability** is a security weakness. A **CVE** is its public ID (e.g. CVE-2021-44228, "Log4Shell"). **CVSS** is a 0–10 severity score.
**Example:** Trivy reports `CVE-2024-xxxx (HIGH, fixed in 1.2.3)`.
**⚠️** Prioritise by exploitability and exposure (internet-facing? exploit in the wild?), not just CVSS.

### Patch Management
**What:** Regularly applying security updates to OS, runtimes, images and dependencies.
**Example:** Automated node image upgrades in AKS/EKS; weekly base-image rebuilds; Dependabot PRs.
**⚠️** Containers don't patch themselves. You must rebuild and redeploy images.

### Audit Log
**What:** A tamper-resistant record of who did what, when (logins, permission changes, resource changes).
**Example:** Azure Activity Log, AWS CloudTrail, Kubernetes audit logs, Git history.
**⚠️** Ship audit logs to a separate, protected location with sufficient retention.

---

# 13 — Ways of Working

### Shift Left
**What:** Moving testing, security and quality checks **earlier** in the development process.
**Example:** Linting in the IDE, unit tests on commit, security scans on PR instead of before release.
**⚠️** Earlier detection is cheaper, but don't drown developers in noisy tools.

### DevSecOps
**What:** Integrating security into every DevOps stage as a shared responsibility.
**Example:** Secret scanning, SAST, SCA, IaC and image scans in pipelines; security champions in teams.
**⚠️** Security tools need owners and triage processes, or findings just pile up.

### SRE (Site Reliability Engineering) (intro)
**What:** An engineering approach to operations using SLOs, error budgets, automation and blameless postmortems.
**Example:** Release pace is governed by how much error budget remains.
**⚠️** See [Advanced: SRE](advanced-terms.md#1--sre--reliability-engineering).

### Toil (intro)
**What:** Repetitive manual operational work that could be automated.
**Example:** Manually rotating certificates every quarter.
**⚠️** Track and automate it, or it consumes the team.

### ITIL / Change Management / CAB
**What:** **ITIL** is a framework of IT service management practices. **Change management** governs production changes. A **CAB** (Change Advisory Board) reviews risky changes.
**Example:** Standard (pre-approved), normal (reviewed) and emergency changes.
**⚠️** Modern practice: automate approvals for low-risk changes with good pipelines and evidence, and keep CABs for genuinely risky changes.

### Postmortem (intro)
**What:** A written review after an incident covering what happened, impact, causes and follow-up actions.
**Example:** Published within 5 business days with owners and due dates for actions.
**⚠️** Keep it blameless and track action items to completion.

### KT (Knowledge Transfer)
**What:** Structured handover of knowledge about systems between people or teams.
**Example:** Architecture walkthrough, runbook review, shadowing on-call. See [KT checklist](../quick-reference/kt_checklist.md).
**⚠️** If only one person can fix it, you have a people single point of failure.

---

**See also:** [Beginner Terms](beginner-terms.md) · [Advanced Terms](advanced-terms.md) · [Azure Glossary](../azure-glossary/azure_glossary.md)

[⬅️ Back to Glossary Index](README.md)
