[🏠 Home](../README.md) · [☁️ AWS](README.md)

# 🧰 AWS Services — What Each Does & When to Use It

> **~170 AWS services** grouped by category. For each one: **what it is**, **use it when**, and
> **think twice / notes**. Each category ends with a "pick this when…" summary.
>
> Terms like *VPC, IAM role, AZ* are explained in [01 — AWS Terms](01-aws-terms.md). End-to-end
> architectures are in [03 — Scenarios & Decision Guides](03-aws-scenarios.md).
>
> 📝 AWS adds, renames and retires services regularly. Status notes reflect **October 2026**;
> check the AWS docs before starting something new on a niche service.

---

## 📑 Table of Contents

1. [Compute](#1--compute)
2. [Containers](#2--containers)
3. [Serverless Compute & Edge](#3--serverless-compute--edge)
4. [Storage](#4--storage)
5. [Databases](#5--databases)
6. [Networking & Content Delivery](#6--networking--content-delivery)
7. [Security, Identity & Compliance](#7--security-identity--compliance)
8. [Management & Governance](#8--management--governance)
9. [Monitoring & Observability](#9--monitoring--observability)
10. [Developer Tools & CI/CD](#10--developer-tools--cicd)
11. [Application Integration & Messaging](#11--application-integration--messaging)
12. [Analytics & Data](#12--analytics--data)
13. [AI & Machine Learning](#13--ai--machine-learning)
14. [Migration & Transfer](#14--migration--transfer)
15. [Frontend, Mobile & APIs](#15--frontend-mobile--apis)
16. [IoT, Media & Other Specialised Services](#16--iot-media--other-specialised-services)
17. [Cost Management](#17--cost-management)
18. [Retired / Closed-to-New-Customers Services](#18--retired--closed-to-new-customers-services)

---

# 1 — Compute

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon EC2** | Virtual servers with full OS control | Lift-and-shift apps, custom software, legacy apps, licensed software, GPU workloads, anything needing OS access | You patch and manage the OS. Prefer managed services where they fit |
| **EC2 Auto Scaling** | Automatically adds/removes EC2 instances | Stateless web/app tiers with variable load; self-healing fleets | Apps must be stateless (store sessions in ElastiCache/DynamoDB) |
| **EC2 Image Builder** | Automated pipelines that build and patch AMIs/container images | Golden images with monthly patching | — |
| **Amazon Lightsail** | Simple VPS bundles (VM + storage + IP + DNS) at a flat monthly price | Simple websites, WordPress, dev/test, learning; predictable cost | Limited networking/scaling. Graduate to EC2/ECS for serious workloads |
| **AWS Elastic Beanstalk** | PaaS: upload code, Beanstalk provisions EC2 + ASG + ELB | Quick deploys of classic web apps (Java, .NET, Node, Python, PHP, Go, Docker) without designing infra | Less popular for new builds. Teams often choose ECS/Fargate or App Runner |
| **AWS App Runner** | Fully managed container/web app service from source or image, with HTTPS and autoscaling | Simple web APIs/sites from a container with zero infrastructure | Fewer knobs than ECS. Check current feature/region availability |
| **AWS Batch** | Managed batch job scheduling on EC2/Spot/Fargate | Large batch/HPC jobs, simulations, rendering, genomics, queues of compute jobs | For event-driven short tasks, Lambda/Step Functions may be simpler |
| **AWS ParallelCluster** | Open-source tool to build HPC clusters (Slurm) on AWS | Traditional HPC workloads | — |
| **AWS Outposts** | AWS racks/servers in your data centre | Low-latency local processing, data residency, consistent hybrid ops | Expensive. For real on-prem requirements only |
| **VMware Cloud on AWS / Elastic VMware Service** | Run VMware workloads on AWS infrastructure | Data-centre exit for VMware estates without re-platforming | Check current offering/licensing (Broadcom changes) |
| **AWS Local Zones / Wavelength** | AWS compute close to cities / inside 5G networks | Single-digit-ms latency apps (gaming, media, AR) | Limited services per zone |

**🧭 Pick this when…** Full control or legacy → **EC2**. Simple VPS → **Lightsail**. Container without infra → **App Runner/Fargate**. Batch jobs → **AWS Batch**. Event-driven code → **Lambda** (§3).

---

# 2 — Containers

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon ECS** | AWS-native container orchestrator (simpler than Kubernetes) | You want containers on AWS with minimal complexity; deep AWS integration (IAM per task, ALB, CloudWatch) | Not portable to other clouds like Kubernetes is |
| **AWS Fargate** | Serverless compute engine for ECS/EKS: no servers to manage | Most ECS workloads; spiky or small services; teams without ops capacity | Higher per-vCPU price than well-utilised EC2; limited GPU/daemon support |
| **Amazon EKS** | Managed Kubernetes control plane | You need Kubernetes (portability, ecosystem, Helm/operators, existing K8s skills) | Kubernetes is complex. Upgrades every ~year, add-ons, networking (IP planning) |
| **EKS Auto Mode** | EKS where AWS also manages nodes, scaling (Karpenter), networking and storage add-ons | You want Kubernetes with much less node operations work | Less low-level control |
| **EKS Anywhere / ECS Anywhere** | Run EKS/ECS-managed workloads on your own hardware | Hybrid/on-prem container estates | — |
| **Amazon ECR** | Private/public container image registry with scanning and replication | Storing images for ECS/EKS/Lambda | Add **lifecycle policies** to delete old images |
| **AWS App2Container** | Tool to containerise existing .NET/Java apps | Modernising legacy apps into containers | — |
| **Red Hat OpenShift Service on AWS (ROSA)** | Managed OpenShift jointly supported by Red Hat and AWS | Organisations standardised on OpenShift | Licensing cost |
| **AWS Copilot CLI** | Opinionated CLI to deploy containers to ECS quickly | Fast ECS bootstrapping | Check current recommendations. AWS tooling in this space evolves |

**🧭 ECS vs EKS:** default to **ECS + Fargate** for AWS-only teams wanting simplicity. Choose **EKS** if you need Kubernetes portability, the CNCF ecosystem, or already have Kubernetes expertise.

---

# 3 — Serverless Compute & Edge

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS Lambda** | Run functions in response to events; pay per request + duration | APIs (with API Gateway), file processing (S3 events), stream/queue processing, cron jobs, glue between services | 15-minute max; cold starts; long-running/steady high load may be cheaper on containers |
| **Lambda@Edge** | Lambda functions running at CloudFront regional edges | Request/response manipulation needing network calls/larger compute at the edge | Higher cost/latency than CloudFront Functions |
| **CloudFront Functions** | Ultra-lightweight JavaScript at CloudFront edge locations | Header rewrites, redirects, URL normalisation, simple auth token checks | Very limited runtime (no network calls) |
| **AWS Step Functions** | Visual state-machine orchestration of services/Lambdas with retries and error handling | Multi-step workflows (order processing, ETL, human approval), sagas, long-running processes | **Standard** (long, exactly-once, audit history) vs **Express** (high-volume, short, cheaper) |
| **Amazon EventBridge Scheduler** | Serverless scheduler for one-time/recurring invocations | Cron jobs, reminders, delayed tasks at scale | — |
| **AWS SAM** | Framework/CLI for serverless apps (CloudFormation extension) | Building/deploying Lambda apps; local testing | CDK or Terraform are alternatives |

**🧭 Lambda vs containers:** event-driven, spiky, short tasks → **Lambda**. Long-running, steady high traffic, or custom runtimes → **Fargate/ECS**.

---

# 4 — Storage

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon S3** | Object storage for any amount of data | Backups, static websites, data lakes, media, logs, artifacts, user uploads | Not a file system. Choose the storage class wisely; keep Block Public Access on |
| **S3 Glacier (storage classes)** | Low-cost archive tiers within S3 | Compliance archives, long-term backups | Retrieval time and fees; minimum storage duration |
| **S3 Tables / S3 Vectors** | Managed Apache Iceberg tables / vector storage built into S3 | Analytics lakehouse tables; cost-effective vector storage for AI | Newer features. Check region availability |
| **Amazon EBS** | Block storage (virtual disks) for EC2 | OS disks, databases on EC2, any app needing a local-like disk | Single AZ; one instance at a time (except io2 Multi-Attach) |
| **Amazon EFS** | Managed NFS shared file system (Linux), elastic | Shared files across many Linux instances/containers/Lambdas (CMS, home dirs, ML datasets) | Higher cost per GB than S3; NFS latency |
| **FSx for Windows File Server** | Managed Windows SMB file shares with AD integration | Windows apps needing shared drives, home folders, lift-and-shift file servers | — |
| **FSx for Lustre** | High-performance parallel file system linked to S3 | HPC, ML training, video rendering | Short-term "scratch" vs "persistent" options |
| **FSx for NetApp ONTAP / OpenZFS** | Managed NetApp / ZFS file systems | Migrating NetApp/ZFS workloads with familiar features (snapshots, clones, multi-protocol) | — |
| **AWS Storage Gateway** | Hybrid gateway exposing cloud storage on-prem (file, volume, tape) | Extending on-prem storage to S3, replacing tape backups | — |
| **AWS Backup** | Central, policy-based backup across EC2, EBS, RDS, DynamoDB, EFS, FSx, S3… with cross-account/region copies and vault lock | Organisation-wide backup compliance and ransomware protection (immutable vaults) | Test restores regularly |
| **AWS Elastic Disaster Recovery (DRS)** | Continuous block-level replication of servers to AWS for fast failover | DR for on-prem or cloud servers with low RPO/RTO | Ongoing replication costs |

**🧭 Which storage?** Objects/files via API → **S3**. A disk for one EC2 → **EBS**. Shared Linux files → **EFS**. Windows shares → **FSx for Windows**. HPC → **FSx for Lustre**. Backups → **AWS Backup**.

---

# 5 — Databases

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon RDS** | Managed MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2 | Traditional relational apps; lift-and-shift databases; need a specific engine | Scale is mostly vertical + read replicas |
| **Amazon Aurora** | Cloud-native MySQL/PostgreSQL-compatible DB with distributed storage | Production relational workloads needing high performance, fast failover, many replicas, global DR | Costs more than RDS for small/simple DBs |
| **Aurora Serverless v2** | Aurora that scales capacity automatically | Variable/unpredictable workloads, dev/test, multi-tenant SaaS | Check minimum capacity costs and scale-to-zero support for your engine version |
| **Aurora DSQL** | Serverless, distributed SQL (PostgreSQL-compatible) with active-active multi-region | Globally distributed apps needing strong consistency and high availability | PostgreSQL compatibility isn't 100% (feature differences) |
| **Amazon DynamoDB** | Serverless NoSQL key-value/document DB, single-digit-ms at any scale | High-scale apps with known access patterns (sessions, carts, IoT, gaming, user profiles), serverless backends | Ad-hoc queries/joins are hard; data modelling up front |
| **Amazon ElastiCache** | Managed in-memory cache (Valkey, Redis OSS, Memcached), including serverless | Caching DB queries, sessions, leaderboards, rate limiting, pub/sub | Cache ≠ source of truth (unless using MemoryDB) |
| **Amazon MemoryDB** | Durable, Redis/Valkey-compatible in-memory **database** | Microsecond reads with durability as a primary database | More expensive than a cache |
| **Amazon DocumentDB** | MongoDB-compatible document database | JSON document workloads, migrating from MongoDB | Not every MongoDB feature is supported. Check compatibility |
| **Amazon Keyspaces** | Serverless Apache Cassandra-compatible DB | Cassandra workloads without managing clusters | — |
| **Amazon Neptune** | Graph database (property graph + RDF), plus Neptune Analytics | Relationships: social graphs, fraud detection, knowledge graphs, recommendations, GraphRAG | — |
| **Amazon Timestream** | Time-series databases (LiveAnalytics and InfluxDB-compatible options) | IoT telemetry, metrics, DevOps monitoring data | Check which Timestream variant is recommended for new workloads |
| **Amazon Redshift** | Petabyte-scale data warehouse (provisioned or serverless) | BI/analytics over large structured datasets, reporting | Not for OLTP (transactional) workloads |
| **Amazon OpenSearch Service** | Managed OpenSearch/Elasticsearch, including serverless | Full-text search, log analytics, vector search | Cluster sizing/shard design matters for cost/performance |
| **AWS Database Migration Service (DMS)** | Migrate/replicate databases (homogeneous or heterogeneous) with CDC | Moving databases to AWS with minimal downtime | Heterogeneous moves need the schema conversion tool |

**🧭 Which database?**

```
 Relational, transactions, joins ───────────────► Aurora (production) / RDS (specific engine or small)
 Key-value at massive scale, serverless ────────► DynamoDB
 Microsecond caching ───────────────────────────► ElastiCache (Valkey/Redis)
 Documents (MongoDB API) ───────────────────────► DocumentDB
 Graph relationships ───────────────────────────► Neptune
 Time-series ───────────────────────────────────► Timestream
 Analytics / warehouse ─────────────────────────► Redshift (or Athena over S3)
 Search ─────────────────────────────────────────► OpenSearch
 Global active-active SQL ──────────────────────► Aurora DSQL
```

---

# 6 — Networking & Content Delivery

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon VPC** | Your private network (subnets, route tables, gateways, SGs) | Every non-serverless workload | Plan CIDRs; NAT and IPv4 costs |
| **Elastic Load Balancing** (ALB/NLB/GWLB) | Managed load balancers | ALB: HTTP apps/microservices. NLB: TCP/UDP, static IPs, extreme performance, PrivateLink. GWLB: inline firewalls | CLB is legacy |
| **Amazon Route 53** | DNS hosting, domain registration, health checks, routing policies, Resolver | Domain DNS, failover, latency/weighted routing, hybrid DNS (Resolver endpoints) | — |
| **Route 53 Application Recovery Controller (ARC)** | Readiness checks and routing controls for multi-region failover | Mission-critical DR with controlled, reliable failover | — |
| **Amazon CloudFront** | Global CDN with edge caching, TLS, WAF integration, Origin Access Control | Static sites (S3), accelerating APIs/dynamic content, video, protecting origins | Cache invalidation strategy; costs at high bandwidth |
| **AWS Global Accelerator** | Anycast static IPs routing users over the AWS backbone to the nearest healthy endpoint | Non-HTTP (TCP/UDP) global apps, gaming, fast regional failover, static IP needs | CloudFront is better for cacheable HTTP content |
| **AWS Transit Gateway** | Regional hub connecting VPCs and on-prem | Many VPCs/accounts; centralised egress/inspection | Per-attachment and per-GB charges |
| **AWS Cloud WAN** | Managed global network built from policies, spanning regions and on-prem | Global enterprises with many regions/branches | Overkill for small estates |
| **AWS PrivateLink / VPC Endpoints** | Private access to AWS services and partner/your services | Keeping traffic off the internet; exposing services across accounts without peering | Interface endpoints cost per hour per AZ |
| **AWS Direct Connect** | Dedicated private connectivity to AWS | Steady high bandwidth hybrid traffic, predictable latency, compliance | Lead time; needs redundancy |
| **AWS Site-to-Site VPN / Client VPN** | IPsec tunnels for sites / OpenVPN remote access for users | Quick hybrid connectivity; backup for Direct Connect; remote admin access | Internet-dependent performance |
| **AWS Verified Access** | Zero-trust access to internal apps without VPN, based on identity and device posture | Replacing VPN for corporate web apps | — |
| **Amazon VPC Lattice** | Service-to-service networking across VPCs/accounts with auth policies | Microservices spread across many accounts/VPCs | — |
| **AWS Cloud Map** | Service discovery (DNS/API) for dynamic resources | Microservices finding each other (ECS service discovery) | — |
| **AWS Network Firewall** | Managed stateful network firewall/IPS for VPCs | Centralised traffic inspection, domain filtering for egress | Cost; needs routing design |
| **Amazon API Gateway** | Managed APIs (REST, HTTP, WebSocket) with auth, throttling, usage plans | Front door for Lambda/HTTP backends, API keys/usage plans, WebSockets | **HTTP API** is cheaper/simpler; **REST API** has more features (WAF, usage plans, request validation) |

**🧭 Load balancer choice:** HTTP(S) → **ALB**. TCP/UDP, static IP, ultra-performance → **NLB**. Third-party firewall appliances → **GWLB**. Global static anycast IPs → **Global Accelerator**. Cacheable content → **CloudFront**.

---

# 7 — Security, Identity & Compliance

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS IAM** | Users, groups, roles, policies | Every account. Roles for workloads, policies for least privilege | Avoid long-lived access keys |
| **AWS IAM Identity Center** | Workforce SSO across all accounts and business apps | Human access to AWS accounts (integrate with Entra ID/Okta/Google) | Recommended over IAM users |
| **Amazon Cognito** | Customer identity: user pools (sign-up/sign-in, MFA, social/SAML) and identity pools (temporary AWS credentials) | Login for your web/mobile app's end users | UI customisation and migration need planning. Compare with Auth0/Clerk |
| **Amazon Verified Permissions** | Fine-grained authorisation service using the Cedar policy language | App-level permissions (who can view/edit which record) outside your code | — |
| **AWS Directory Service** | Managed Microsoft AD, AD Connector, Simple AD | Windows workloads needing AD in AWS; joining EC2 to a domain | — |
| **AWS KMS** | Create and control encryption keys; envelope encryption | Encrypting data in nearly every service; key control and audit | Key deletion = data loss; request quotas |
| **AWS CloudHSM** | Dedicated hardware security modules (FIPS 140-3 Level 3) | Regulatory need for single-tenant HSMs, custom crypto | KMS is simpler for most needs |
| **AWS Secrets Manager** | Store and automatically rotate secrets | DB credentials, API keys needing rotation | Per-secret cost. Parameter Store for simple config |
| **AWS Certificate Manager (ACM)** | Free public TLS certificates, auto-renewed; private CA | HTTPS on ALB/CloudFront/API Gateway | CloudFront certs must be in us-east-1 |
| **AWS WAF** | Web application firewall rules, rate limiting, bot control | Protecting public web apps/APIs from OWASP attacks and abuse | Tune rules (count mode first) |
| **AWS Shield** | DDoS protection: Standard (free), Advanced (paid, response team, cost protection) | Advanced for high-value public apps | — |
| **AWS Firewall Manager** | Central management of WAF/Shield/SG/Network Firewall policies across accounts | Organisations enforcing security policies at scale | Requires Organizations + Config |
| **Amazon GuardDuty** | Threat detection from logs and runtime signals | Turn on in **all** accounts/regions via delegated admin | — |
| **Amazon Inspector** | Automated vulnerability scanning for EC2, ECR images, Lambda; code scanning | Continuous CVE management | — |
| **Amazon Macie** | Discovers and protects sensitive data (PII) in S3 | Data classification, GDPR/PCI compliance | Cost scales with data scanned |
| **AWS Security Hub** | Central security findings + posture checks (CIS, AWS FSBP, PCI) | Single pane of glass for security across accounts | — |
| **Amazon Detective** | Investigate findings with visual graphs of activity | Root-cause analysis of GuardDuty/Security Hub findings | — |
| **Amazon Security Lake** | Centralises security logs in OCSF format in S3 | SIEM/analytics integration across accounts | — |
| **IAM Access Analyzer** | Finds external/unused access, validates and generates policies | Least-privilege reviews; detecting public/cross-account exposure | — |
| **AWS Config** | Resource configuration history and compliance rules | Auditing and compliance; detecting drift/misconfiguration | Cost per configuration item recorded |
| **AWS CloudTrail** | API activity logging (plus CloudTrail Lake for queries) | Always on: audit, security investigation | Organisation trail to a central log account |
| **AWS Audit Manager** | Collects evidence for audits mapped to frameworks | Preparing for SOC 2/ISO/PCI audits | — |
| **AWS Artifact** | Download AWS compliance reports and agreements | Auditors asking for AWS's SOC/ISO reports | — |
| **AWS Private CA** | Managed private certificate authority | Internal mTLS, device certificates | Cost per CA |
| **AWS Payment Cryptography** | Managed payment HSM functions | Payment processing apps (PCI PIN) | Niche |

**🧭 Minimum security baseline for every account:** Identity Center (no IAM users), MFA on root, CloudTrail org trail, GuardDuty, Security Hub, Config, IAM Access Analyzer, Block Public Access for S3, default EBS encryption, budget alerts.

---

# 8 — Management & Governance

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS Organizations** | Multi-account management, consolidated billing, SCPs/RCPs, tag and backup policies | Any organisation with more than one account | Keep the management account empty of workloads |
| **AWS Control Tower** | Automated landing zone, guard-rails (controls) and Account Factory | Setting up and governing a new multi-account environment | Customisations via CfCT/AFT for advanced needs |
| **AWS CloudFormation** | Native IaC (YAML/JSON templates, stacks, StackSets) | AWS-only IaC, StackSets across accounts | Verbose. CDK generates it for you |
| **AWS CDK** | IaC in programming languages → CloudFormation | Developers preferring TypeScript/Python over YAML | Requires bootstrap per account/region |
| **AWS Service Catalog** | Approved IaC "products" users can self-provision | Governed self-service (e.g. "standard RDS database") | — |
| **AWS Systems Manager** | Ops hub: Session Manager, Patch Manager, Run Command, Parameter Store, Automation, Inventory, Fleet Manager | Managing fleets of EC2/on-prem servers without SSH; patching; runbooks | Needs SSM agent + role + network path |
| **AWS Resource Groups & Tag Editor** | Group and bulk-tag resources | Organising and tagging resources | — |
| **AWS License Manager** | Track and enforce software licences (BYOL) | Oracle/Microsoft licence compliance | — |
| **AWS Trusted Advisor** | Best-practice checks (cost, security, resilience, performance, limits) | Regular account health reviews | Full checks need Business+ support |
| **AWS Compute Optimizer** | Rightsizing recommendations | Reducing over-provisioned EC2/EBS/Lambda/ECS costs | — |
| **AWS Health** | Your personalised service health events | Alerting on AWS issues affecting your resources | — |
| **AWS Well-Architected Tool** | Guided architecture reviews against the 6 pillars | Design reviews, before go-live | — |
| **AWS Resilience Hub** | Assess and validate app resilience vs RTO/RPO targets | Proving DR readiness | — |
| **AWS Proton** | Templates for platform teams to offer standard infra/app stacks | — | AWS has announced availability changes. Check before adopting; see §18 |
| **AWS CloudShell** | Browser-based shell with AWS CLI pre-authenticated | Quick CLI tasks without local setup | Not for long-running work |
| **AWS Console Mobile App / Chatbot (Amazon Q Developer in chat applications)** | Manage/monitor from phone; AWS notifications and commands in Slack/Teams | ChatOps alerts and quick actions | — |

---

# 9 — Monitoring & Observability

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon CloudWatch** | Metrics, logs, alarms, dashboards, Logs Insights, anomaly detection | Default monitoring for everything on AWS | Custom metrics, log ingestion and retention drive cost |
| **CloudWatch Synthetics / RUM** | Scripted canaries / real-user browser monitoring | Uptime and user-journey checks; front-end performance | — |
| **CloudWatch Application Signals / Container Insights / Lambda Insights** | APM-style service views (SLOs), container and Lambda metrics | Service health dashboards and SLOs without third-party tools | — |
| **AWS X-Ray** | Distributed tracing | Tracing requests through Lambda/API Gateway/microservices | AWS now steers towards **OpenTelemetry (ADOT)** instrumentation sending to X-Ray/CloudWatch |
| **AWS Distro for OpenTelemetry (ADOT)** | AWS-supported OpenTelemetry collector/SDKs | Vendor-neutral instrumentation | — |
| **Amazon Managed Service for Prometheus** | Managed Prometheus-compatible metrics | Kubernetes/EKS metrics with PromQL, at scale | — |
| **Amazon Managed Grafana** | Managed Grafana with AWS data source integration | Dashboards over Prometheus/CloudWatch/OpenSearch | — |
| **AWS CloudTrail Lake** | Query audit events with SQL | Security/audit investigations | — |
| **Amazon DevOps Guru** | ML-driven operational anomaly detection | Detecting operational anomalies automatically | Check current status/recommendations |

---

# 10 — Developer Tools & CI/CD

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS CodeBuild** | Managed build/test containers (`buildspec.yml`); can also host GitHub Actions runners | CI builds inside AWS; builds needing VPC access | See [CI/CD guide](../cicd-pipelines/README.md) |
| **AWS CodePipeline** | Orchestrates release stages (source → build → approve → deploy) | AWS-native delivery pipelines | Many teams use GitHub Actions/GitLab instead |
| **AWS CodeDeploy** | Automated deployments to EC2/on-prem, Lambda (traffic shifting), ECS (blue/green) | Blue/green and canary deployments with auto-rollback | — |
| **AWS CodeArtifact** | Managed package repository (npm, PyPI, Maven, NuGet…) proxying public registries | Private packages; caching/approving open-source dependencies | — |
| **Amazon CodeGuru (Reviewer/Profiler)** | Automated code review and profiling | Check status. Amazon Q Developer and Inspector code scanning cover much of this now | — |
| **Amazon Q Developer** | AI coding assistant for IDEs/CLI and AWS console help | AI help with AWS code, upgrades, troubleshooting | Review all suggestions |
| **AWS Infrastructure Composer** | Visual designer generating IaC (CloudFormation/SAM) | Visualising and sketching serverless architectures | — |
| **AWS Fault Injection Service (FIS)** | Managed chaos-engineering experiments | Testing resilience (stop instances, inject latency, AZ power interruption scenarios) | Use stop conditions (alarms) |
| **AWS Device Farm** | Test mobile/web apps on real devices/browsers | Mobile app testing across devices | — |
| **AWS CLI / SDKs / Tools for PowerShell** | Command line and language SDKs | All automation | Use SSO/roles, not static keys |

---

# 11 — Application Integration & Messaging

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon SQS** | Fully managed message **queue** (Standard: at-least-once, best-effort order; FIFO: ordered, exactly-once processing) | Decoupling producers/consumers, buffering spikes, background jobs, work queues | Consumers must be idempotent (Standard); set visibility timeout and DLQ |
| **Amazon SNS** | Pub/sub **topics** pushing to many subscribers (SQS, Lambda, HTTP, email, SMS, mobile push) | Fan-out: one event → many consumers; notifications/alerts | Combine **SNS → SQS** for durable fan-out |
| **Amazon EventBridge** | Serverless **event bus** with content-based routing, schema registry, archive/replay, SaaS integrations, Pipes, Scheduler | Event-driven architectures, reacting to AWS/SaaS events, routing by event content | Throughput/latency differ from SNS/Kinesis. Check the use case |
| **EventBridge Pipes** | Point-to-point integration from a source (SQS, Kinesis, DynamoDB Streams…) to a target with filtering/enrichment | Replacing "glue Lambdas" that just move data | — |
| **AWS Step Functions** | Workflow orchestration | Multi-step business processes with retries/compensation | See §3 |
| **Amazon MQ** | Managed ActiveMQ and RabbitMQ brokers | Migrating apps using JMS/AMQP/MQTT/STOMP protocols without code changes | For new cloud-native apps, prefer SQS/SNS/EventBridge |
| **Amazon MSK** | Managed Apache Kafka (provisioned or serverless) + MSK Connect | Kafka-based streaming, existing Kafka ecosystems | Kafka expertise needed |
| **Amazon Kinesis Data Streams** | Real-time data streaming with shards and replay | Clickstreams, IoT telemetry, real-time analytics with multiple consumers | Shard/capacity management (or on-demand mode) |
| **Amazon Data Firehose** (formerly Kinesis Data Firehose) | Load streaming data into S3/Redshift/OpenSearch/Splunk/HTTP, with transformation | Simplest way to land streams/logs in a data lake | Near-real-time (buffering), not sub-second |
| **Amazon AppFlow** | No-code data flows between SaaS (Salesforce, SAP, Slack…) and AWS | Syncing SaaS data into S3/Redshift | — |
| **Amazon MWAA** | Managed Apache Airflow | Orchestrating data pipelines with Airflow DAGs | Step Functions may be simpler for AWS-only workflows |
| **AWS AppSync** | Managed GraphQL and real-time pub/sub APIs | GraphQL APIs over DynamoDB/Lambda/HTTP; real-time subscriptions | — |
| **Amazon SES** | Email sending/receiving service | Transactional and bulk email from your apps | Start in sandbox; set up SPF/DKIM/DMARC |
| **Amazon Pinpoint / End User Messaging** | SMS, push and voice messaging APIs | Sending SMS/push notifications | Pinpoint engagement features are being retired. Check AWS End User Messaging |

**🧭 SQS vs SNS vs EventBridge vs Kinesis:**

| Need | Use |
|------|-----|
| One consumer group processes each job (work queue) | **SQS** |
| Broadcast one message to many subscribers | **SNS** (often SNS → SQS) |
| Route events by content to different targets; AWS/SaaS events | **EventBridge** |
| Ordered, replayable high-throughput stream with multiple readers | **Kinesis Data Streams** / **MSK** |
| Just land streaming data in S3/Redshift | **Data Firehose** |

---

# 12 — Analytics & Data

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon Athena** | Serverless SQL queries directly on S3 data (pay per TB scanned) | Ad-hoc analysis of logs/data lakes (CloudTrail, ALB logs), lightweight BI | Partition and use columnar formats (Parquet) to cut cost |
| **AWS Glue** | Serverless ETL (Spark), Data Catalog, crawlers, data quality | Building data pipelines; cataloguing data lake tables | Spark knowledge helps |
| **AWS Glue DataBrew** | Visual data preparation (no code) | Analysts cleaning data | — |
| **AWS Lake Formation** | Build and govern data lakes with fine-grained (row/column) permissions | Secure, governed data lakes shared across teams/accounts | — |
| **Amazon EMR** | Managed Hadoop/Spark/Hive/Presto clusters (EC2, EKS, serverless) | Large-scale big-data processing with open-source frameworks | Cluster tuning |
| **Amazon Redshift** | Data warehouse (provisioned/serverless, Spectrum queries on S3) | Enterprise BI and reporting | — |
| **Amazon QuickSight** | Serverless BI dashboards and natural-language Q&A | Business dashboards embedded or for internal users | Licensing per user/session. Check the current packaging |
| **Amazon OpenSearch Service** | Search and log analytics | Log analytics dashboards, search | — |
| **Amazon Managed Service for Apache Flink** | Real-time stream processing with Flink | Streaming analytics/ETL on Kinesis/MSK | — |
| **Amazon DataZone / SageMaker Unified Studio** | Data catalogue, governance and sharing portal / unified data + AI workspace | Data mesh / self-service data access across teams | Newer, evolving offering |
| **AWS Clean Rooms** | Collaborate on combined datasets without sharing raw data | Joint analysis with partners (advertising, healthcare) | — |
| **AWS Data Exchange** | Find and subscribe to third-party datasets | Buying external data | — |

**🧭 Typical data lake on AWS:** ingest (Firehose/DMS/AppFlow) → **S3** (raw/curated zones, Iceberg/S3 Tables) → catalogue (**Glue Data Catalog**) → govern (**Lake Formation**) → query (**Athena**, **Redshift**, **EMR**) → visualise (**QuickSight**).

---

# 13 — AI & Machine Learning

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **Amazon Bedrock** | Fully managed access to foundation models (Anthropic Claude, Amazon Nova, Meta Llama, Mistral, and others) via one API, plus Knowledge Bases (RAG), Agents, Guardrails, evaluation, fine-tuning | Building generative AI apps (chatbots, RAG, summarisation, agents) inside AWS governance | Model availability varies by region; manage token costs and quotas |
| **Amazon Bedrock AgentCore** | Runtime, memory, identity, gateway and observability for deploying AI agents at scale | Running production AI agents securely | Newer service. Check region support |
| **Amazon SageMaker AI** | Full ML platform: notebooks, training, tuning, deployment endpoints, pipelines, model registry, monitoring | Custom ML models, MLOps, training/hosting your own models | Endpoint costs accrue while running. Shut down idle resources |
| **Amazon Q Business** | Generative AI assistant over company data (connectors to SharePoint, Confluence, S3…) | Internal enterprise Q&A with permissions-aware answers | Per-user pricing |
| **Amazon Q Developer** | AI coding/AWS assistant | Developers working on AWS | — |
| **Amazon Rekognition** | Image/video analysis (objects, faces, text, moderation) | Content moderation, image tagging, identity verification | Face analysis has legal/ethical constraints |
| **Amazon Textract** | Extract text, forms, tables from documents | Invoice/form processing, document automation | — |
| **Amazon Comprehend** | NLP: sentiment, entities, key phrases, PII detection, classification | Analysing reviews/tickets; PII redaction | LLMs via Bedrock may be more flexible |
| **Amazon Transcribe** | Speech-to-text | Call-centre transcription, subtitles, meeting notes | — |
| **Amazon Polly** | Text-to-speech | Voice apps, accessibility, IVR | — |
| **Amazon Translate** | Neural machine translation | Translating content/apps | — |
| **Amazon Lex** | Conversational chatbots (voice and text) | Contact-centre bots, chat interfaces (with Amazon Connect) | — |
| **Amazon Kendra** | Intelligent enterprise search | Search across documents with ML ranking; RAG retriever | Cost. Bedrock Knowledge Bases may suffice |
| **Amazon Personalize** | Recommendation engine as a service | Product/content recommendations | — |
| **Amazon Fraud Detector** | Managed fraud detection models | Online fraud scoring | Check availability for new customers before adopting; alternatives are custom models on SageMaker AI |
| **AWS Trainium / Inferentia (EC2 Trn/Inf)** | AWS custom ML training and inference chips | Cost-efficient large-scale training/inference | Requires the Neuron SDK |

**🧭 AI choice:** Use a ready AI capability (OCR, speech, translation) → **task-specific AI service**. Generative AI app/RAG/agents → **Bedrock**. Train/host your own models → **SageMaker AI**. Employees asking questions of company docs → **Q Business**.

---

# 14 — Migration & Transfer

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS Migration Hub / AWS Transform** | Track migrations; AI-assisted migration & modernisation (VMware, mainframe, .NET) | Planning and running large migrations | Evolving tooling. Check current names |
| **AWS Application Discovery Service** | Discover on-prem servers, dependencies and utilisation | Migration assessment | — |
| **AWS Application Migration Service (MGN)** | Lift-and-shift server replication to EC2 | Rehosting VMs/physical servers with minimal downtime | The primary rehost tool |
| **AWS DMS + Schema Conversion** | Database migration with continuous replication | Moving databases, including engine changes (Oracle → Aurora PostgreSQL) | Test the cutover |
| **AWS DataSync** | Fast online data transfer (NFS/SMB/HDFS/object → S3/EFS/FSx) | Moving large file datasets, recurring syncs | — |
| **AWS Transfer Family** | Managed SFTP/FTPS/FTP/AS2 endpoints backed by S3/EFS | Partners exchanging files via SFTP | Hourly endpoint cost |
| **AWS Snowball Edge** | Physical device for offline data transfer and edge compute | Moving many TBs where network is too slow; disconnected edge sites | Check current device availability/ordering |
| **AWS Mainframe Modernization** | Tools/runtime for migrating mainframe workloads | Mainframe exit programmes | — |

**🧭 The 7 Rs of migration:** Retire, Retain, **Rehost** (lift-and-shift with MGN), **Relocate** (VMware), **Replatform** (e.g. to RDS), **Repurchase** (move to SaaS), **Refactor** (re-architect to cloud-native).

---

# 15 — Frontend, Mobile & APIs

| Service | What it is | Use it when | Think twice / notes |
|---------|-----------|-------------|---------------------|
| **AWS Amplify** | Full-stack framework + hosting (CI/CD, SSR for Next.js) for web/mobile apps on AWS | Frontend teams wanting fast full-stack apps on AWS; hosting React/Next.js | Abstracts AWS. Advanced needs may outgrow it |
| **Amazon API Gateway** | Managed APIs | Front door for serverless backends | See §6 |
| **AWS AppSync** | Managed GraphQL | GraphQL and real-time apps | See §11 |
| **Amazon Location Service** | Maps, geocoding, routing, geofencing | Location features in apps | — |
| **Amazon Cognito** | End-user authentication | App sign-up/sign-in | See §7 |

---

# 16 — IoT, Media & Other Specialised Services

| Service | What it is | Use it when |
|---------|-----------|-------------|
| **AWS IoT Core** | Connect devices securely (MQTT), rules engine, device shadows | Fleets of connected devices sending telemetry |
| **AWS IoT Greengrass** | Run Lambda/containers/ML on edge devices | Local processing on gateways/devices |
| **AWS IoT SiteWise / IoT Device Management / IoT Device Defender** | Industrial data / fleet management / device security | Factories, large device fleets |
| **AWS Elemental MediaConvert / MediaLive / MediaPackage** | File-based transcoding / live encoding / packaging | Video streaming platforms |
| **Amazon IVS** | Managed low-latency live streaming | Interactive live video in apps |
| **Amazon Connect** | Cloud contact centre | Call centres with IVR, chat, AI agents |
| **Amazon WorkSpaces / AppStream 2.0** | Virtual desktops / application streaming | Remote desktops (like Azure Virtual Desktop) |
| **Amazon WorkMail / Chime SDK** | Business email / real-time communications SDK | Specific collaboration needs |
| **Amazon GameLift** | Game server hosting and matchmaking | Multiplayer games |
| **AWS Ground Station** | Satellite ground stations as a service | Satellite data downlink |
| **Amazon Braket** | Quantum computing access | Quantum research/experiments |
| **AWS HealthLake / HealthOmics** | Healthcare data (FHIR) / genomics workflows | Healthcare and life sciences |
| **AWS Marketplace** | Buy third-party software/SaaS billed through AWS | Procuring tools via the AWS bill |

---

# 17 — Cost Management

| Service | What it is | Use it when |
|---------|-----------|-------------|
| **AWS Billing & Cost Management console** | Bills, payments, credits | Every month |
| **AWS Budgets** | Spend/usage alerts and budget actions | **Day one** of every account |
| **AWS Cost Explorer** | Analyse and forecast spend by service/account/tag | Understanding where money goes |
| **Cost Anomaly Detection** | ML alerts for unusual spend | Catching runaway costs or compromised keys early |
| **Cost and Usage Report / Data Exports** | Line-item billing data to S3 | Detailed FinOps analysis with Athena/QuickSight |
| **Savings Plans / Reserved Instances** | Commitment discounts | Steady-state workloads |
| **AWS Pricing Calculator** | Estimate architecture costs | Before building; for proposals |
| **Compute Optimizer / Trusted Advisor** | Rightsizing and idle-resource findings | Monthly optimisation reviews |
| **AWS Cost Optimization Hub** | Consolidated cost-saving recommendations | Prioritising savings across accounts |

---

# 18 — Retired / Closed-to-New-Customers Services

> Don't start new projects on these. Older tutorials still mention them.

| Service | Status (as of late 2026) | Use instead |
|---------|--------------------------|-------------|
| **AWS CodeCommit** | Closed to new customers since July 2024 (existing customers can continue) | GitHub, GitLab, Bitbucket |
| **AWS Cloud9** | Closed to new customers since July 2024 | Local IDE + AWS Toolkit, CloudShell, cloud dev environments |
| **AWS OpsWorks** (Chef/Puppet) | End of life (2024) | Systems Manager, Ansible |
| **AWS App Mesh** | End of support 30 Sept 2026 | Amazon VPC Lattice, ECS Service Connect, Istio on EKS |
| **Amazon QLDB** | End of support (July 2025) | Aurora PostgreSQL with audit/history tables |
| **AWS Snowmobile** | Retired | Snowball Edge / DataSync / Direct Connect |
| **Classic Load Balancer / EC2-Classic** | Legacy / retired | ALB/NLB in a VPC |
| **AWS CodeStar** | Discontinued (2024) | CodePipeline/CodeBuild, GitHub Actions, project templates |
| **Others** (e.g. Amazon Pinpoint engagement features, and several smaller services) | Retiring or closed to new customers | Check AWS's "service availability updates" page before adopting any niche service |

---

**Next:** [03 — Scenarios, Architectures & Decision Guides ➡️](03-aws-scenarios.md)

[⬅️ Back to AWS Index](README.md)
