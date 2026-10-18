# 🧰 Tools & Websites Worth Knowing in IT — What They're For & When to Use Them

> A curated map of **~200 tools and websites** every IT / DevOps / cloud person should recognise.
> For each one: **what it does** and **when to reach for it**, plus head-to-head guides for the
> common "which one should I pick?" questions (Firebase vs Supabase, Vercel vs Netlify vs Render…).
>
> 📝 **Free tiers and pricing change often.** Several popular services have removed or cut
> free plans over the years. Check the current pricing page before you build on one.
> Last reviewed: **October 2026**.

[🏠 Back to Home](../README.md)

---

## 📑 Table of Contents

1. [Backend-as-a-Service (Firebase, Supabase…)](#1--backend-as-a-service-baas)
2. [Managed Databases, Caches & Search](#2--managed-databases-caches--search)
3. [App Hosting & Deployment Platforms](#3--app-hosting--deployment-platforms)
4. [Cloud Providers & VPS Hosts](#4--cloud-providers--vps-hosts)
5. [Authentication & Identity](#5--authentication--identity)
6. [Code Hosting, CI/CD & Package Registries](#6--code-hosting-cicd--package-registries)
7. [Containers & Kubernetes Tools](#7--containers--kubernetes-tools)
8. [Infrastructure as Code & Configuration](#8--infrastructure-as-code--configuration)
9. [Monitoring, Logging & Incident Response](#9--monitoring-logging--incident-response)
10. [Security Tools & Sites](#10--security-tools--sites)
11. [API, Webhook & Developer Utilities](#11--api-webhook--developer-utilities)
12. [Networking & DNS Tools](#12--networking--dns-tools)
13. [Building-Block SaaS (payments, email, files, analytics…)](#13--building-block-saas)
14. [Low-Code, No-Code & Automation](#14--low-code-no-code--automation)
15. [AI Tools](#15--ai-tools)
16. [Local Dev Environment & Terminal](#16--local-dev-environment--terminal)
17. [Diagrams, Docs & Team Productivity](#17--diagrams-docs--team-productivity)
18. [Learning Platforms & Hands-On Labs](#18--learning-platforms--hands-on-labs)
19. [Reference Sites & Communities](#19--reference-sites--communities)
20. [Decision Cheat Sheet: "I want to… → use…"](#20--decision-cheat-sheet)

---

# 1 — Backend-as-a-Service (BaaS)

> **What BaaS means:** instead of building and hosting your own backend (server, database, login
> system, file storage, APIs), you use a ready-made one and talk to it from your frontend or
> mobile app. Great for **prototypes, MVPs, hackathons, mobile apps and small teams**.

| Tool | What it is | Use it when | Think twice when |
|------|-----------|------------|------------------|
| **Firebase** (Google) | BaaS with a NoSQL document DB (**Firestore**), Realtime Database, Auth, Cloud Storage, Hosting, Cloud Functions, push notifications (FCM), Analytics, Crashlytics, Remote Config | **Mobile apps** (Android/iOS/Flutter), real-time features (chat, live updates), you want Google's ecosystem, push notifications, crash reporting | You need complex relational queries/joins and reporting, want to avoid lock-in, or need SQL |
| **Supabase** | Open-source "Firebase alternative" built on **PostgreSQL**: database + auto-generated REST/GraphQL APIs, Auth, Storage, Realtime, Edge Functions, vector search (pgvector), Row-Level Security | You want **SQL/relational data**, joins, standard Postgres you can migrate away from, open source/self-hosting option, AI apps with vector search | Your team doesn't know SQL and won't learn it; you need deep mobile-specific services (push, crash reporting) out of the box |
| **Appwrite** | Open-source BaaS (databases, auth, storage, functions, messaging) that's **easy to self-host** with Docker; cloud version too | You want a Firebase-like experience you can **run on your own server** (data residency, cost control) | You don't want to operate infrastructure (use their cloud then) |
| **PocketBase** | A **single Go binary** with an embedded SQLite DB, auth, file storage, realtime and an admin UI | Small projects, internal tools, side projects; you want the simplest possible backend on a $5 VPS | High scale or multi-server setups (it's single-node by design) |
| **Convex** | Reactive backend: TypeScript functions + a database with automatic real-time sync to the frontend | TypeScript/React apps where everything must update live; you like writing backend logic as code | You need standard SQL access or non-JS stacks |
| **AWS Amplify** | AWS's framework + hosting for full-stack web/mobile apps on top of AWS services (Cognito, AppSync, DynamoDB, S3) | You're already on AWS and want BaaS-style speed with a path into the full AWS world | You want simplicity outside AWS |
| **Nhost** | Open-source BaaS on Postgres + Hasura GraphQL | You want GraphQL-first on Postgres | You prefer REST-first or broader community/ecosystem |

### 🥊 Firebase vs Supabase: the 30-second decision

```
 Is your data naturally RELATIONAL (users ↔ orders ↔ products, reports, joins)?
     YES ─► Supabase (Postgres)
     NO  ─► Is it a MOBILE app needing push notifications / crash reports / analytics?
               YES ─► Firebase
               NO  ─► Need to self-host?  YES ─► Supabase / Appwrite / PocketBase
                                          NO  ─► Either works; pick the one your team knows
```

| | Firebase | Supabase |
|---|---|---|
| Database | NoSQL documents (Firestore) | PostgreSQL (SQL) |
| Queries | Simple queries, limited joins | Full SQL, joins, views, functions |
| Security model | Security Rules language | Postgres Row-Level Security (RLS) policies |
| Open source / self-host | No | Yes |
| Lock-in | Higher (proprietary APIs) | Lower (it's Postgres, so `pg_dump` and move) |
| Mobile extras | Excellent (FCM, Crashlytics, Remote Config) | Fewer built-in |
| Pricing model | Pay per reads/writes/storage, so costs can surprise with chatty apps | Mostly per project size/compute + usage |

> ⚠️ **The #1 BaaS security mistake:** because the frontend talks to the database directly,
> **security rules / RLS policies ARE your backend security**. Leaving Firestore rules open
> (`allow read, write: if true`) or tables without RLS exposes all data to anyone. Never put
> admin/service keys in frontend code.

---

# 2 — Managed Databases, Caches & Search

| Tool | What it is | Use it when |
|------|-----------|------------|
| **Neon** | Serverless **Postgres** with branching (copy a DB like a Git branch) and scale-to-zero | Postgres for side projects/serverless apps; per-PR preview databases |
| **Supabase (DB only)** | Managed Postgres (you can ignore the BaaS features) | You just want hosted Postgres with a nice UI |
| **PlanetScale** | Managed **MySQL** (Vitess) and Postgres with branching and non-blocking schema changes | Large-scale MySQL; teams wanting safe online schema changes (note: free hobby tier was removed in 2024) |
| **MongoDB Atlas** | Managed **MongoDB** (document DB) on any major cloud, with search and vector search | Document-shaped data, teams already using MongoDB |
| **Turso** | Hosted **SQLite/libSQL**, replicated to the edge | Read-heavy apps wanting low latency globally; SQLite fans |
| **CockroachDB** | Distributed SQL (Postgres-compatible) that survives node/region failures | Multi-region apps needing strong consistency |
| **Upstash** | Serverless **Redis** and Kafka-style messaging, pay-per-request | Caching/rate-limiting/queues from serverless/edge functions |
| **Redis Cloud / Valkey** | Managed Redis (in-memory cache, sessions, queues); Valkey = open-source Redis fork | Caching, sessions, leaderboards, pub/sub |
| **Azure SQL / Amazon RDS / Aurora / Cloud SQL** | The big clouds' managed relational databases | Production workloads inside that cloud: backups, HA and compliance handled |
| **Cosmos DB / DynamoDB / Firestore** | Cloud-native NoSQL at massive scale | Huge scale with predictable access patterns |
| **Elastic Cloud / OpenSearch** | Search engine and log analytics | Full-text search, log analytics |
| **Algolia** | Hosted search-as-you-type for websites/apps | Instant product/site search without running servers |
| **Meilisearch / Typesense** | Open-source, easy search engines (self-host or cloud) | Algolia-like search with lower cost/self-hosting |
| **Pinecone / Qdrant / Weaviate / pgvector** | **Vector databases** for AI similarity search (RAG) | Building AI apps that search documents by meaning |
| **DBeaver / pgAdmin / Azure Data Studio / TablePlus** | Desktop database clients | Querying, browsing and managing databases visually |

> 🧭 **Default advice:** for most apps, **PostgreSQL** is the safe default database. Pick
> something else when you have a specific reason (document model, massive scale, edge latency).

---

# 3 — App Hosting & Deployment Platforms

> These platforms take your code (or container) and run it on the internet, handling servers,
> HTTPS, scaling and deploys. They're perfect for learning, side projects and many production apps.

| Platform | Best at | Use it when | Watch out for |
|----------|--------|------------|---------------|
| **Vercel** | **Next.js** and frontend frameworks; preview deploys per PR; edge/serverless functions | React/Next.js sites and apps; frontend teams wanting zero-config deploys | Costs at high traffic/bandwidth; long-running backends don't fit serverless limits |
| **Netlify** | Static sites & Jamstack, forms, serverless functions, preview deploys | Static/marketing sites, docs, Hugo/Astro/Gatsby sites | Same serverless limits as Vercel |
| **Cloudflare Pages / Workers** | Static sites + code running at Cloudflare's **edge** worldwide; very cheap; KV/D1 (SQLite)/R2 storage | Fast global sites, APIs at the edge, cost-sensitive projects; you already use Cloudflare DNS | Workers runtime isn't full Node.js; some libraries won't work |
| **GitHub Pages** | Free static site hosting from a repo | Personal sites, project docs, portfolios | Static only (no backend) |
| **Render** | Heroku-like PaaS: web services, workers, cron jobs, Postgres, Redis | Full-stack apps (Node/Python/Go/Docker) with a database, without cloud complexity | Free instances sleep when idle (slow first request) |
| **Railway** | Very fast "deploy anything" PaaS with databases and a nice UI | Prototypes, side projects, small services, hackathons | Usage-based pricing; keep an eye on bills |
| **Fly.io** | Run Docker containers/VMs close to users in many regions | Globally distributed apps, low-latency APIs, running containers without Kubernetes | More hands-on (CLI, config) than Render/Railway |
| **Heroku** | The original developer-friendly PaaS (`git push heroku main`) | Legacy apps already there; teams valuing its maturity/add-ons | No free dynos since 2022; often pricier than newer options |
| **DigitalOcean App Platform** | Simple PaaS on DigitalOcean | Simple apps when you also use DO droplets/databases | Fewer advanced features than big clouds |
| **Azure App Service / Container Apps** | Azure's PaaS for web apps / serverless containers | Company is on Azure; need VNet integration, Entra ID, compliance | Learning curve of Azure itself |
| **AWS App Runner / Elastic Beanstalk / Amplify Hosting** | AWS's simpler hosting options | Company is on AWS | Same as above for AWS |
| **Google Cloud Run** | Serverless containers that scale to zero | Containerised APIs with spiky traffic; pay-per-use | Cold starts on scale-from-zero |
| **Coolify / Dokku / CapRover** | **Self-hosted** Heroku/Vercel-like PaaS on your own VPS | You want PaaS convenience on a cheap VPS and full control | You operate and patch the server yourself |

### 🥊 Which hosting platform?

```
 Static site / docs / portfolio ............ GitHub Pages, Cloudflare Pages, Netlify
 Next.js / React app ....................... Vercel (or Cloudflare / Netlify)
 Full-stack app + Postgres, minimal ops .... Render, Railway
 Containers in many regions ................ Fly.io, Google Cloud Run
 Company runs on Azure / AWS / GCP ......... that cloud's PaaS (App Service/Container Apps, App Runner, Cloud Run)
 Cheapest at small scale, you like Linux ... VPS (Hetzner/DO) + Coolify or Docker Compose
```

---

# 4 — Cloud Providers & VPS Hosts

| Provider | What it is | Use it when |
|----------|-----------|------------|
| **Microsoft Azure** | Big-three cloud; strongest Microsoft/enterprise integration (Entra ID, Windows, .NET, M365) | Enterprises on Microsoft stack; hybrid with on-prem AD; most Indian IT service companies' enterprise clients |
| **Amazon Web Services (AWS)** | Largest cloud by market share; widest service catalogue | Default choice for many startups and enterprises; huge job market |
| **Google Cloud (GCP)** | Big-three cloud; strong in data/analytics (BigQuery), Kubernetes (GKE), AI | Data/ML-heavy workloads, Kubernetes-first teams |
| **Oracle Cloud (OCI)** | Enterprise cloud, strong for Oracle DBs; notably generous "Always Free" tier | Oracle workloads; free small VMs for learning |
| **DigitalOcean** | Developer-friendly cloud: droplets (VMs), managed DBs, Kubernetes, simple pricing | Small/medium apps, learning, predictable bills |
| **Hetzner** | Low-cost European VPS and dedicated servers | Cheapest reliable VMs for self-hosting, labs, side projects |
| **Linode (Akamai) / Vultr** | Developer VPS clouds | Simple VMs worldwide at low cost |
| **Cloudflare** | Edge network: DNS, CDN, WAF, DDoS, Zero Trust, Workers, R2 storage (no egress fees) | Put in front of almost any website; free DNS/CDN tier is excellent |

> 🧭 **Career tip:** learn **one** big cloud deeply (Azure or AWS), know the equivalents in
> the others, and use a cheap VPS for hands-on Linux practice. See the
> [Cloud Handbook](../cloud/cloud_handbook.md) and [Azure notes](../azure/README.md).
>
> ⚠️ **Set budget alerts on day one** in any cloud account. Forgotten resources and leaked
> keys used for crypto-mining are how students get surprise bills.

---

# 5 — Authentication & Identity

| Tool | What it is | Use it when |
|------|-----------|------------|
| **Auth0** (Okta) | Hosted login/identity platform: social logins, MFA, enterprise SSO | B2C/B2B apps needing rich login features fast |
| **Clerk** | Drop-in auth with pre-built UI components, user management, organisations | React/Next.js apps wanting beautiful login UI in minutes |
| **Firebase Auth / Supabase Auth** | Auth bundled with those BaaS platforms | You already use Firebase/Supabase |
| **Keycloak** | Open-source identity & access management server (OIDC/SAML) you host | Self-hosted SSO for internal apps; avoid per-user SaaS costs |
| **Okta / Microsoft Entra ID** | Enterprise workforce identity: employee SSO, MFA, lifecycle | Company employee logins across SaaS apps |
| **Microsoft Entra External ID / Amazon Cognito** | Cloud-native customer identity on Azure / AWS | Customer-facing apps on that cloud |
| **Authentik / Authelia** | Open-source SSO/2FA in front of self-hosted apps | Homelab and small-company self-hosting |

> ⚠️ **Don't write your own authentication** (password hashing, sessions, MFA, reset flows)
> for real products. Use a proven provider or library.

---

# 6 — Code Hosting, CI/CD & Package Registries

| Tool | What it is | Use it when |
|------|-----------|------------|
| **GitHub** | Most popular Git hosting; PRs, Issues, **Actions** CI/CD, Packages/GHCR, Codespaces, security scanning | Default for open source and most companies; build your public portfolio here |
| **GitLab** | All-in-one DevOps platform (repos, CI/CD, registry, security), SaaS or self-hosted | Companies wanting a single integrated platform or self-hosting |
| **Azure DevOps** | Repos, Boards, Pipelines, Artifacts, Test Plans | Microsoft-centric enterprises (see [Azure DevOps guide](../azure-devops/index.md)) |
| **Bitbucket** | Atlassian's Git hosting with Pipelines; integrates with Jira | Teams deep in Jira/Confluence |
| **Jenkins** | Open-source, self-hosted, plugin-based automation server | Legacy/complex enterprise pipelines; full control |
| **CircleCI / Buildkite / TeamCity** | Dedicated CI/CD services | Specific performance/self-hosted-runner needs |
| **Argo CD / Flux** | GitOps continuous delivery for Kubernetes | Deploying to Kubernetes from Git |
| **JFrog Artifactory / Sonatype Nexus** | Universal artifact repositories & proxies | Enterprises storing/proxying packages and images |
| **npm / PyPI / Maven Central / NuGet / crates.io** | Public package registries for each language | Publishing/consuming open-source libraries |
| **Docker Hub / GHCR / ACR / ECR / Artifact Registry / Quay** | Container image registries | Storing and pulling container images |
| **Renovate / Dependabot** | Bots that open PRs to update dependencies | Keeping dependencies patched automatically |

See also: [CI/CD Pipeline Scenarios](../cicd-pipelines/README.md).

---

# 7 — Containers & Kubernetes Tools

| Tool | What it is | Use it when |
|------|-----------|------------|
| **Docker Desktop** | Docker + GUI + local Kubernetes on Windows/macOS | Building/running containers on your laptop (check licensing for large companies) |
| **Podman / Podman Desktop** | Daemonless, rootless Docker alternative (Red Hat) | Docker-compatible workflow without Docker Desktop licensing |
| **Rancher Desktop / OrbStack / Colima** | Alternatives to Docker Desktop (OrbStack is macOS-only) | Lightweight local containers/Kubernetes |
| **kind / minikube / k3d / k3s** | Run Kubernetes locally (kind/k3d in Docker) or lightweight K8s (k3s) on small servers | Learning Kubernetes, CI testing, homelabs |
| **kubectl / Helm / Kustomize** | Core K8s CLI, package manager, YAML customisation | Every Kubernetes job |
| **k9s** | Terminal UI for Kubernetes | Fast day-to-day cluster navigation and debugging |
| **Lens / Headlamp / Freelens** | Desktop/web GUIs for Kubernetes | Visual cluster exploration |
| **kubectx / kubens** | Switch clusters/namespaces quickly | Working with many clusters (avoid prod mistakes!) |
| **Stern** | Tail logs from many pods at once | Debugging multi-pod apps |
| **dive** | Explore image layers and wasted space | Shrinking container images |
| **Trivy / Grype** | Scan images, filesystems and IaC for vulnerabilities | Security checks locally and in CI |
| **hadolint** | Dockerfile linter | Catch Dockerfile mistakes early |
| **Play with Docker / Killercoda** | Free browser-based Docker/K8s playgrounds | Practise without installing anything |
| **Artifact Hub** | Search engine for Helm charts, operators, plugins | Finding a Helm chart to install software |
| **CNCF Landscape** (landscape.cncf.io) | Map of the whole cloud-native ecosystem | Discovering what tools exist for a category |

See also: [Docker notes](../docker/README.md) · [Kubernetes Handbook](../kubernetes/kubernetes_handbook.md).

---

# 8 — Infrastructure as Code & Configuration

| Tool | What it is | Use it when |
|------|-----------|------------|
| **Terraform** | The most widely used multi-cloud IaC tool (HCL); BSL licence since 2023 | Infrastructure on any cloud; huge module ecosystem |
| **OpenTofu** | Open-source (MPL) fork of Terraform, community/Linux Foundation | You want Terraform compatibility with an open-source licence |
| **Bicep** | Azure-native IaC language (compiles to ARM) | Azure-only infrastructure |
| **AWS CloudFormation / CDK** | AWS-native IaC; CDK lets you write it in TypeScript/Python | AWS-only infrastructure |
| **Pulumi** | IaC in real programming languages (TS, Python, Go, C#) | Teams preferring code over HCL/YAML |
| **Ansible** | Agentless config management/automation over SSH/WinRM | Configuring servers, patching, app installs, network devices |
| **Packer** | Build VM/machine images from code | Golden images for VMs |
| **Crossplane** | Manage cloud resources via Kubernetes APIs | Platform teams offering self-service infra in K8s |
| **Terraform Registry / Ansible Galaxy** | Public module/role libraries | Reusing community modules (review before use!) |
| **Checkov / tfsec (Trivy) / TFLint / Infracost** | IaC security scan / lint / cost estimates in PRs | Quality, security and cost checks for IaC |
| **Atlantis / Spacelift / HCP Terraform / env0** | Run Terraform from PRs with approvals and state management | Team Terraform workflows |

See also: [Terraform architecture notes](../terraform-arch/) · [IaC pipelines](../cicd-pipelines/04-iac.md).

---

# 9 — Monitoring, Logging & Incident Response

| Tool | What it is | Use it when |
|------|-----------|------------|
| **Prometheus** | Open-source metrics collection and alerting | Kubernetes/cloud-native metrics, the industry standard |
| **Grafana** (+ **Grafana Cloud**) | Dashboards for any data source; Grafana Cloud bundles hosted Prometheus/Loki/Tempo | Visualising metrics/logs/traces; a free cloud tier is good for learning |
| **Loki / Elasticsearch / OpenSearch** | Log aggregation & search | Centralised logs |
| **Jaeger / Tempo / Zipkin** | Distributed tracing backends | Following requests across microservices |
| **OpenTelemetry** | Vendor-neutral standard + SDKs/collector for telemetry | Instrument once, send to any backend |
| **Datadog / New Relic / Dynatrace / Splunk** | Commercial all-in-one observability platforms | Companies wanting one managed platform (watch costs) |
| **Azure Monitor / CloudWatch / Google Cloud Observability** | Cloud-native monitoring | Workloads in that cloud |
| **Sentry** | Error tracking & performance for apps (stack traces, releases) | Know immediately when users hit exceptions |
| **UptimeRobot / Better Stack / Uptime Kuma** | Uptime monitoring & status pages (Uptime Kuma is self-hosted) | "Is my website up?" checks and public status pages |
| **PagerDuty / incident.io / Grafana OnCall** | On-call scheduling, paging and incident management | Running on-call rotations and incidents |
| **Statuspage / Instatus** | Hosted public status pages | Communicating outages to customers |
| **Netdata / Glances / btop** | Real-time system monitoring for single servers | Quick look at a Linux server's health |

---

# 10 — Security Tools & Sites

| Tool / Site | What it does | Use it when |
|-------------|-------------|------------|
| **Have I Been Pwned** (haveibeenpwned.com) | Check if your email/password appeared in data breaches | Personal and company breach awareness |
| **VirusTotal** | Scan files/URLs with dozens of antivirus engines | Checking a suspicious file or link |
| **SSL Labs Server Test** (ssllabs.com) | Grades a site's TLS/HTTPS configuration | Verifying your HTTPS setup |
| **securityheaders.com** | Checks HTTP security headers | Hardening web apps |
| **crt.sh** | Search Certificate Transparency logs | Finding certificates issued for your domains (and subdomains) |
| **Let's Encrypt** | Free, automated TLS certificates | HTTPS for any site (via certbot, cert-manager, Caddy) |
| **Shodan / Censys** | Search engines for internet-exposed devices | Checking what your org exposes publicly (authorised use only) |
| **OWASP** (owasp.org) | Open security community: Top 10, ZAP, cheat sheets, ASVS | Learning web security; secure-coding references |
| **OWASP ZAP / Burp Suite** | Web vulnerability scanners / proxies | Testing your own apps (with permission) |
| **Snyk / Socket / Dependabot** | Dependency vulnerability and malicious-package detection | Securing open-source dependencies |
| **SonarQube / SonarCloud / Semgrep / CodeQL** | Static code analysis for bugs and vulnerabilities | Code quality and security gates |
| **gitleaks / TruffleHog** | Find secrets committed to Git | Prevent and detect leaked keys |
| **Bitwarden / 1Password / KeePassXC** | Password managers | Everyone, for unique strong passwords and shared team vaults |
| **HashiCorp Vault / Infisical / Doppler** | Secrets management for apps and teams | Centralising application secrets |
| **CyberChef** (gchq.github.io/CyberChef) | "Swiss army knife" for encoding/decoding/data transforms | Base64, JWT decode, hashing, format conversions (safer than random online decoders) |
| **TryHackMe / Hack The Box / OverTheWire** | Legal hacking practice labs | Learning security hands-on |
| **CISA KEV catalog / NVD** | Known exploited vulnerabilities list / CVE database | Prioritising patches |

> ⚠️ **Never paste secrets, tokens, customer data or private keys into random online tools**
> (JWT decoders, JSON formatters, AI chats). Use local tools or trusted offline ones like CyberChef run locally.

See also: [Cybersecurity notes](../cybersecurity-notes/) · [Web VAPT notes](../web-vapt-notes/).

---

# 11 — API, Webhook & Developer Utilities

| Tool / Site | What it does | Use it when |
|-------------|-------------|------------|
| **Postman** | API client: send requests, collections, environments, tests, mock servers | Testing and documenting APIs; team API collections |
| **Insomnia / Bruno / Hoppscotch** | Postman alternatives (Bruno stores collections as files in Git; Hoppscotch is web/open source) | Lightweight or Git-friendly API testing |
| **curl / HTTPie** | Command-line HTTP clients | Quick API calls, scripts, debugging |
| **webhook.site / RequestBin** | Instantly get a URL that shows every request sent to it | Debugging webhooks (what is GitHub/Stripe actually sending?) |
| **ngrok / Cloudflare Tunnel / Tailscale Funnel** | Expose a local server to the internet via a secure tunnel | Testing webhooks or demos against your laptop |
| **httpbin.org** | Test endpoints that echo requests, return status codes, delays | Testing HTTP clients, proxies, retries |
| **Swagger Editor / Redoc / Stoplight** | Design and document APIs with OpenAPI specs | API-first design and docs |
| **jq / jqplay / yq** | Query and transform JSON/YAML on the command line | Parsing API/CLI output in scripts |
| **regex101** | Build and test regular expressions with explanations | Writing regex for logs, validation, grep |
| **crontab.guru** | Explains and builds cron expressions | Scheduling jobs (`0 2 * * 1-5` = 2 a.m. weekdays) |
| **explainshell.com** | Explains each part of a shell command | Understanding a scary command before running it |
| **ShellCheck** (shellcheck.net) | Finds bugs in shell scripts | Every Bash script you write |
| **JSON Crack / JSON Formatter** | Visualise/format JSON | Exploring big JSON payloads (don't paste secrets) |
| **Mockaroo / Faker** | Generate realistic fake test data | Seeding test databases |
| **DevDocs.io** | Fast offline-capable docs for hundreds of languages/tools | Looking up reference docs quickly |
| **Carbon / ray.so** | Beautiful code screenshots | Slides, blog posts, social media |

---

# 12 — Networking & DNS Tools

| Tool / Site | What it does | Use it when |
|-------------|-------------|------------|
| **dig / nslookup / dog** | Command-line DNS lookups | Checking what a name resolves to |
| **DNSChecker / whatsmydns.net** | Check DNS propagation worldwide | After changing DNS records |
| **MXToolbox** | DNS, email (MX/SPF/DKIM/DMARC) and blacklist checks | Debugging email delivery and domain setup |
| **Cloudflare DNS / Route 53 / Azure DNS** | Managed authoritative DNS | Hosting your domain's DNS reliably |
| **ipinfo.io / ifconfig.me** | Show your public IP and IP details | "What IP am I coming from?" (e.g. for firewall allow-lists) |
| **Subnet calculators** (e.g. cidr.xyz, jodies.de/ipcalc) | Visualise CIDR ranges | Planning VNets/subnets |
| **Wireshark / tcpdump** | Capture and inspect network packets | Deep network debugging |
| **mtr / traceroute / tracert** | Show the path and latency to a host | Finding where packets are dropped or slow |
| **nmap** | Network/port scanner | Auditing open ports on **your own** systems |
| **Tailscale / ZeroTier / WireGuard** | Easy mesh VPNs / modern VPN protocol | Securely reaching home labs and servers without open ports |
| **Speedtest / fast.com** | Bandwidth tests | Checking connection speed |
| **Downdetector / cloud status pages** | User-reported outages / official provider status (status.azure.com, health.aws.amazon.com, githubstatus.com) | "Is it me or is it them?" during incidents |

See also: [Networking Handbook](../networking/networking_handbook.md) · [DNS notes](../quick-reference/dns_notes.md).

---

# 13 — Building-Block SaaS

> Services you plug into apps instead of building yourself.

| Need | Tools | When to use |
|------|-------|------------|
| **Payments** | **Stripe**, Razorpay (India), PayPal, Paddle/Lemon Squeezy (merchant-of-record, handles global tax) | Accepting payments/subscriptions. Never handle raw card data yourself |
| **Transactional email** | **Resend**, SendGrid, Mailgun, Amazon SES, Postmark | Password resets, receipts, notifications (configure SPF/DKIM/DMARC) |
| **SMS / voice / WhatsApp** | **Twilio**, MessageBird (Bird), Vonage | OTPs, notifications, phone verification |
| **File/image storage & CDN** | **Cloudinary**, ImageKit, Uploadthing, S3/R2/Blob Storage | User uploads, image resizing/optimisation |
| **Real-time messaging** | Pusher, Ably, Socket.IO, Supabase Realtime | Live chat, notifications, collaborative features |
| **Product analytics** | **PostHog** (open source, feature flags, session replay), Mixpanel, Amplitude | Understanding how users use your product |
| **Web analytics** | Google Analytics, **Plausible**, Umami (privacy-friendly) | Site traffic stats |
| **Feature flags** | LaunchDarkly, Unleash, Flagsmith, PostHog, OpenFeature | Gradual rollouts, kill switches |
| **Headless CMS** | Strapi, Sanity, Contentful, Payload | Letting non-developers edit website content |
| **Customer support/chat** | Intercom, Crisp, Zendesk, Freshdesk | Support widgets and ticketing |
| **Maps/geo** | Google Maps Platform, Mapbox, OpenStreetMap/Leaflet | Maps, geocoding, routing |

---

# 14 — Low-Code, No-Code & Automation

| Tool | What it is | Use it when |
|------|-----------|------------|
| **n8n** | Workflow automation (open source, self-hostable), with AI/agent nodes | Automating between apps/APIs with full control, e.g. alert → ticket → Slack |
| **Zapier / Make** | Hosted no-code automation between thousands of apps | Quick business automations without servers |
| **Power Automate / Power Apps** | Microsoft's automation and low-code app platform | Microsoft 365 organisations (approvals, SharePoint/Teams flows) |
| **Retool / Appsmith / Budibase / ToolJet** | Build internal tools/admin panels on top of databases and APIs | Admin dashboards and ops tools in hours, not weeks |
| **Airtable / NocoDB / Baserow** | Spreadsheet-database hybrids (NocoDB/Baserow are open source) | Lightweight data apps, trackers, inventories |
| **Google Apps Script** | JavaScript automation for Google Workspace | Automating Sheets/Gmail/Drive |
| **IFTTT** | Simple consumer automations | Personal/home automations |

> 🧭 Low-code is great for **internal tools and glue**. For core customer-facing products,
> consider maintainability, versioning, testing and vendor lock-in.

---

# 15 — AI Tools

| Tool | What it is | Use it when |
|------|-----------|------------|
| **ChatGPT / Claude / Gemini / Microsoft Copilot** | General AI assistants | Explaining concepts, drafting docs/emails, brainstorming, reviewing configs (no secrets!) |
| **Claude Code / Google Antigravity / OpenAI Codex / GitHub Copilot agent** | AI coding agents that edit code and run commands | Coding tasks with review and safety settings. See [AI Coding Agents](../ai-coding-agents/README.md) |
| **GitHub Copilot / Cursor / Windsurf / JetBrains AI** | AI inside the editor (autocomplete, chat, agents) | Day-to-day coding assistance |
| **Perplexity** | AI search with cited sources | Researching with links you can verify |
| **NotebookLM** | AI over your own documents (Google) | Studying/summarising notes, PDFs, docs |
| **Hugging Face** | Hub for open models, datasets, demos (Spaces) | Finding/trying open-source AI models |
| **Ollama / LM Studio** | Run open AI models locally on your computer | Private/offline AI, experimenting without sending data out |
| **OpenRouter** | One API to many AI models | Comparing/using multiple model providers |
| **Azure AI Foundry / Amazon Bedrock / Google Vertex AI** | Enterprise AI model platforms in the big clouds | Building AI features inside company cloud governance |
| **LangChain / LlamaIndex / Claude Agent SDK** | Frameworks/SDKs for building AI apps and agents | Building RAG and agent applications |

> ⚠️ Follow your company's AI policy. Don't paste confidential code, customer data, or
> credentials into consumer AI tools. Verify AI answers, because models can be confidently wrong.

---

# 16 — Local Dev Environment & Terminal

| Tool | What it is | Use it when |
|------|-----------|------------|
| **VS Code** | Free, extensible code editor | Default editor for most DevOps work (YAML, Terraform, Docker extensions) |
| **JetBrains IDEs** (IntelliJ, PyCharm, Rider…) | Powerful language-specific IDEs | Heavy Java/Python/.NET development |
| **WSL2** (Windows Subsystem for Linux) | Real Linux inside Windows | Essential on Windows for DevOps: Bash, Docker, Linux tools |
| **Windows Terminal / iTerm2 / WezTerm / Warp** | Modern terminal apps | Better tabs, splits, themes |
| **winget / Chocolatey / Scoop · Homebrew · apt** | Package managers (Windows · macOS · Linux) | Installing tools with one command (`winget install Git.Git`) |
| **Oh My Zsh / Starship / Oh My Posh** | Shell prompt frameworks | Show Git branch, Kubernetes context, cloud account in your prompt (prevents prod mistakes!) |
| **tmux / Zellij** | Terminal multiplexers (sessions survive disconnects) | Long-running SSH work on servers |
| **Dev Containers / GitHub Codespaces / Gitpod** | Reproducible dev environments in containers, locally or in the cloud | Onboarding in minutes; same tools for everyone |
| **asdf / mise / nvm / pyenv / sdkman** | Manage multiple versions of languages/tools | Different projects needing different Node/Python/Terraform versions |
| **direnv** | Auto-load env vars per folder | Per-project config without polluting your shell |
| **Git GUI clients** (GitHub Desktop, GitKraken, Fork, Sourcetree) | Visual Git | Learning Git, complex merges/history visualisation |
| **Learn Git Branching** (learngitbranching.js.org) | Interactive Git visual tutorial | Understanding branches/rebase visually |

---

# 17 — Diagrams, Docs & Team Productivity

| Tool | What it is | Use it when |
|------|-----------|------------|
| **draw.io / diagrams.net** | Free diagramming with cloud icon sets (Azure/AWS/GCP) | Architecture diagrams |
| **Excalidraw** | Hand-drawn-style whiteboard diagrams | Quick sketches, design discussions |
| **Mermaid** (mermaid.live) | Diagrams written as text, rendered in Markdown/GitHub | Diagrams versioned alongside docs |
| **Lucidchart / Miro / FigJam** | Collaborative diagramming/whiteboards | Team workshops, planning |
| **Notion / Confluence / Obsidian** | Docs & wikis (Obsidian = local Markdown notes) | Team docs (Notion/Confluence), personal knowledge base (Obsidian) |
| **Jira / Linear / Azure Boards / Trello / GitHub Projects** | Work tracking | Tickets, sprints, kanban boards |
| **Slack / Microsoft Teams / Discord** | Team chat (with integrations/ChatOps) | Team communication, alerts, deployment notifications |
| **Loom** | Quick screen-recorded videos | Async walkthroughs, bug reports, KT sessions |
| **MkDocs (Material) / Docusaurus** | Turn Markdown into documentation websites | Internal docs portals, project docs |

---

# 18 — Learning Platforms & Hands-On Labs

| Platform | What it offers | Use it when |
|----------|---------------|------------|
| **roadmap.sh** | Visual learning roadmaps (DevOps, Linux, Docker, K8s, cloud…) | Planning what to learn next, in order |
| **Microsoft Learn** | Free official Azure/Microsoft training paths and sandboxes | Azure certifications (AZ-900, AZ-104, AZ-400…) |
| **AWS Skill Builder** | Official AWS training & labs | AWS certifications |
| **Google Cloud Skills Boost** | Official GCP labs and courses | GCP learning |
| **KodeKloud** | Hands-on DevOps courses with browser labs (Linux, Docker, K8s, Terraform, Ansible) | Learning by doing; CKA/CKAD prep |
| **Killercoda / iximiuz Labs** | Free/low-cost interactive Linux/Docker/K8s scenarios in the browser | Practising without setting anything up |
| **A Cloud Guru / Pluralsight / Udemy / Coursera** | Video courses (Udemy: buy on sale) | Structured courses and certification prep |
| **freeCodeCamp / The Odin Project** | Free coding curricula (web development) | Learning programming fundamentals |
| **Exercism / Codewars / LeetCode / HackerRank** | Coding practice problems | Improving programming/scripting; interview prep |
| **Linux Journey / OverTheWire Bandit** | Learn Linux basics / command-line wargames | Getting comfortable in the terminal |
| **TryHackMe / Hack The Box** | Security labs | Security/DevSecOps skills |
| **CNCF & Linux Foundation training** | Kubernetes/cloud-native courses & certs (CKA, CKAD, CKS, KCNA) | Kubernetes certifications |
| **Exam/practice sites** (e.g. official practice assessments) | Practice tests | Final certification prep (prefer official ones) |

> 🧭 **Learning loop that works:** pick a roadmap.sh topic → do a hands-on lab → build a small
> project → write notes (like this repo) → teach/explain it → repeat.

---

# 19 — Reference Sites & Communities

| Site | Why visit |
|------|----------|
| **Official docs** (learn.microsoft.com, docs.aws.amazon.com, cloud.google.com/docs, kubernetes.io/docs, docs.docker.com, developer.hashicorp.com) | Always the source of truth. Check here before trusting blogs or AI |
| **MDN Web Docs** | The best reference for HTTP, web, JavaScript, CSS |
| **Stack Overflow / Server Fault / Super User** | Q&A for programming / sysadmin / power-user questions |
| **GitHub** (Trending, Discussions, Issues) | Discover tools; search issues for your exact error message |
| **Reddit** (r/devops, r/sysadmin, r/kubernetes, r/AZURE, r/aws, r/selfhosted, r/homelab) | Real-world discussions and war stories |
| **Hacker News** (news.ycombinator.com) | Tech news and in-depth discussions |
| **dev.to / Hashnode / Medium** | Community blog posts and tutorials |
| **CNCF Blog & KubeCon talks (YouTube)** | Cloud-native trends and deep dives |
| **Google SRE books** (sre.google/books) | Free, foundational SRE books |
| **The Twelve-Factor App** (12factor.net) | Cloud-native app principles |
| **Martin Fowler's site** (martinfowler.com) | Architecture, CI/CD, refactoring patterns |
| **Newsletters**: DevOps Weekly, SRE Weekly, KubeWeekly, Last Week in AWS, TLDR DevOps | Stay current with 10 minutes a week |
| **Podcasts/YouTube**: TechWorld with Nana, NetworkChuck, Fireship, John Savill (Azure), Kubernetes Podcast | Learning on the go |
| **Downdetector & provider status pages** | Check for outages during incidents |
| **endoflife.date** | End-of-support dates for languages, OSes, databases, frameworks | Planning upgrades; spotting unsupported versions |
| **Can I use** (caniuse.com) | Browser support for web features |

---

# 20 — Decision Cheat Sheet

| I want to… | Reach for |
|------------|-----------|
| Build an app backend fast with login + DB + storage | **Supabase** (SQL) or **Firebase** (NoSQL/mobile) |
| Self-host a simple backend cheaply | **PocketBase** or **Appwrite** on a VPS |
| Host a static site/portfolio for free | **GitHub Pages**, **Cloudflare Pages**, **Netlify** |
| Deploy a Next.js app | **Vercel** |
| Deploy a full-stack app + Postgres with no ops | **Render** or **Railway** |
| Run containers globally without Kubernetes | **Fly.io**, **Cloud Run**, **Azure Container Apps** |
| Get a cheap Linux server to practise | **Hetzner**, **DigitalOcean**, Oracle free tier, or WSL2 locally |
| Free managed Postgres for a side project | **Neon** or **Supabase** |
| Add caching/rate-limiting to serverless functions | **Upstash Redis** |
| Add login to an app | **Clerk**, **Auth0**, or your BaaS's auth; **Keycloak** to self-host |
| Accept payments | **Stripe** / **Razorpay** |
| Send transactional emails | **Resend**, **SES**, **SendGrid** |
| Test an API | **Postman**, **Bruno**, `curl` |
| Debug a webhook | **webhook.site**, **ngrok** |
| Understand a cron expression / shell command / regex | **crontab.guru**, **explainshell**, **regex101** |
| Check DNS changes worldwide | **DNSChecker**, **whatsmydns** |
| Check a site's HTTPS config | **SSL Labs**, **securityheaders.com** |
| Monitor if a site is up | **UptimeRobot**, **Better Stack**, **Uptime Kuma** |
| Track app errors | **Sentry** |
| Draw an architecture diagram | **draw.io**, **Excalidraw**, **Mermaid** |
| Automate tasks between apps | **n8n**, **Zapier**, **Power Automate** |
| Build an internal admin tool | **Retool**, **Appsmith** |
| Learn Kubernetes hands-on | **Killercoda**, **KodeKloud**, **kind/minikube** |
| Plan my learning path | **roadmap.sh** |
| Check whether a version is still supported | **endoflife.date** |
| Run AI models privately on my laptop | **Ollama**, **LM Studio** |

---

## 🔗 Related notes in this repo

- [DevOps Glossary](../devops-glossary/README.md) defines the terms used on this page
- [DevOps Toolkit](../devops_toolkit.md) lists the software installed for the training environment
- [AI Coding Agents](../ai-coding-agents/README.md) · [CI/CD Pipelines](../cicd-pipelines/README.md) · [Dockerfile Handbook](../docker/dockerfile_handbook/README.md)

---

[🏠 Back to Home](../README.md)
