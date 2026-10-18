[🏠 Home](../README.md) · [☁️ AWS](README.md)

# 🏗️ AWS Scenarios, Reference Architectures & Decision Guides

> **"Which AWS services should I use for this?"** This chapter answers it with decision
> guides and **20 real-world scenarios**. Each shows the services involved, an ASCII
> architecture, why each piece was chosen, and the gotchas.
>
> New to the vocabulary? Read [01 — Terms](01-aws-terms.md) and [02 — Services](02-aws-services.md) first.

---

## 📑 Table of Contents

**Part A — Decision guides**
- [A1. Which compute?](#a1-which-compute)
- [A2. Which database?](#a2-which-database)
- [A3. Which storage?](#a3-which-storage)
- [A4. Which messaging/integration service?](#a4-which-messagingintegration-service)
- [A5. Which way to connect networks?](#a5-which-way-to-connect-networks)
- [A6. Which load balancer / edge service?](#a6-which-load-balancer--edge-service)
- [A7. Which way to give access?](#a7-which-way-to-give-access)
- [A8. Which IaC / deployment tool?](#a8-which-iac--deployment-tool)

**Part B — 20 scenarios**

| # | Scenario | # | Scenario |
|---|----------|---|----------|
| 1 | [Static website / SPA](#scenario-1--static-website-or-spa) | 11 | [Real-time streaming analytics](#scenario-11--real-time-streaming-analytics) |
| 2 | [Classic 3-tier web app](#scenario-2--classic-3-tier-web-application) | 12 | [Generative AI chatbot over company docs (RAG)](#scenario-12--generative-ai-chatbot-over-company-documents-rag) |
| 3 | [Serverless REST API](#scenario-3--serverless-rest-api) | 13 | [Multi-account landing zone](#scenario-13--multi-account-landing-zone) |
| 4 | [Containerised microservices](#scenario-4--containerised-microservices) | 14 | [Hybrid connectivity to on-prem](#scenario-14--hybrid-connectivity-to-on-premises) |
| 5 | [Event-driven order processing](#scenario-5--event-driven-order-processing) | 15 | [Disaster recovery across regions](#scenario-15--disaster-recovery-across-regions) |
| 6 | [File upload & image processing](#scenario-6--file-upload-and-image-processing) | 16 | [Migrating a data centre](#scenario-16--migrating-a-data-centre-to-aws) |
| 7 | [Scheduled jobs & batch processing](#scenario-7--scheduled-jobs-and-batch-processing) | 17 | [Centralised logging & security monitoring](#scenario-17--centralised-logging-and-security-monitoring) |
| 8 | [CI/CD for an AWS app](#scenario-8--cicd-for-an-aws-application) | 18 | [Secure private access to AWS services](#scenario-18--secure-private-access-without-internet) |
| 9 | [Data lake & analytics](#scenario-9--data-lake-and-analytics) | 19 | [Multi-tenant SaaS](#scenario-19--multi-tenant-saas) |
| 10 | [Mobile app backend](#scenario-10--mobile-app-backend) | 20 | [Cost-optimised dev/test environments](#scenario-20--cost-optimised-devtest-environments) |

**Part C — Reference**
- [C1. Azure ↔ AWS service mapping](#c1-azure--aws-service-mapping)
- [C2. Top 20 AWS mistakes beginners make](#c2-top-20-aws-mistakes-beginners-make)
- [C3. AWS certification path](#c3-aws-certification-path)

---

# Part A — Decision Guides

## A1. Which compute?

```
 Do you need full OS control, special software, or lift-and-shift a VM?
   └─ YES ─► EC2 (+ Auto Scaling + ALB)             simple single server? ─► Lightsail
   └─ NO ─► Is it event-driven, short (<15 min), spiky?
              └─ YES ─► Lambda
              └─ NO ─► Is it a container?
                         └─ YES ─► Need Kubernetes (portability/ecosystem)?
                                     └─ YES ─► EKS (Auto Mode for less ops)
                                     └─ NO  ─► ECS on Fargate   (simplest: App Runner)
                         └─ NO ─► Classic web app, want PaaS? ─► Elastic Beanstalk
                                  Large batch/HPC jobs?      ─► AWS Batch
```

| Workload | Best fit | Why |
|----------|----------|-----|
| Legacy Windows/.NET Framework app | EC2 (Windows) or Elastic Beanstalk | Needs Windows OS/IIS |
| Spring Boot / Node API in containers | ECS on Fargate | No servers, simple, AWS-integrated |
| Company standard is Kubernetes | EKS | Same tooling as other clusters (Helm, Argo CD) |
| Resize images when uploaded | Lambda | Event-driven, pay per use |
| Nightly 3-hour report job | ECS Fargate task via EventBridge Scheduler, or AWS Batch | Exceeds Lambda's 15 min |
| ML training on GPUs | SageMaker AI or EC2 GPU instances | Managed training vs full control |
| Simple WordPress blog | Lightsail | Flat cheap price |

---

## A2. Which database?

| Requirement | Choose | Avoid |
|-------------|--------|-------|
| Relational, transactions, joins, reporting | **Aurora** (PostgreSQL/MySQL) or **RDS** | DynamoDB (joins are painful) |
| Specific engine: Oracle, SQL Server, Db2 | **RDS** for that engine | — |
| Massive scale, simple key lookups, serverless | **DynamoDB** | RDS (connection limits at extreme scale) |
| Unpredictable load, dev/test, SaaS tenants | **Aurora Serverless v2** or **DynamoDB on-demand** | Over-provisioned instances |
| Sub-millisecond cache | **ElastiCache** (Valkey/Redis) | Hitting the DB for every read |
| MongoDB-style documents | **DocumentDB** (or MongoDB Atlas on AWS) | — |
| Relationships/graph queries | **Neptune** | Recursive SQL joins |
| Time-series metrics/IoT | **Timestream** | — |
| Data warehouse / BI | **Redshift**, or **Athena** over S3 | Running analytics on the production OLTP DB |
| Full-text search | **OpenSearch** | `LIKE '%term%'` queries |
| Multi-region active-active with strong consistency | **Aurora DSQL** or **DynamoDB Global Tables** (eventual) | Single-region DB with manual failover |

---

## A3. Which storage?

| Need | Choose |
|------|--------|
| Store files/objects accessed via API or HTTP | **S3** |
| Archive for years at the lowest cost | **S3 Glacier Deep Archive** |
| Disk for an EC2 instance/database | **EBS gp3** (io2 for high IOPS) |
| Shared Linux file system across instances/containers | **EFS** |
| Windows file shares (SMB) with AD | **FSx for Windows File Server** |
| High-performance computing / ML training data | **FSx for Lustre** (linked to S3) |
| On-prem servers needing cloud-backed storage | **Storage Gateway** |
| Central backups and compliance | **AWS Backup** (with vault lock) |
| Move 100 TB from a data centre | **DataSync** (online) or **Snowball Edge** (offline) |

---

## A4. Which messaging/integration service?

| Pattern | Service | Example |
|---------|---------|---------|
| Work queue: one worker handles each job | **SQS** | Resize jobs, email sending |
| Strict ordering per key / no duplicates | **SQS FIFO** | Bank transactions per account |
| Fan-out: one event → many subscribers | **SNS → SQS** | `OrderPlaced` → billing, shipping, analytics |
| Route events by content; react to AWS/SaaS events | **EventBridge** | "S3 object created in bucket X with prefix Y" → Lambda |
| Multi-step workflow with retries and state | **Step Functions** | Order saga, document approval |
| Real-time stream, multiple readers, replay | **Kinesis Data Streams** / **MSK** | Clickstream, IoT telemetry |
| Land streaming data into S3/Redshift | **Data Firehose** | Logs → S3 data lake |
| Existing JMS/AMQP app | **Amazon MQ** | Migrating ActiveMQ/RabbitMQ apps |
| Scheduled tasks | **EventBridge Scheduler** | Nightly reports, reminders |

---

## A5. Which way to connect networks?

| Situation | Choose |
|-----------|--------|
| 2–3 VPCs need to talk | **VPC Peering** |
| Many VPCs and accounts, plus on-prem | **Transit Gateway** (Cloud WAN for global) |
| Expose one service to other VPCs/accounts/customers privately | **PrivateLink** |
| Service-to-service app traffic across accounts with auth | **VPC Lattice** |
| Private access to S3/DynamoDB from private subnets | **Gateway VPC endpoints** (free) |
| Private access to other AWS APIs | **Interface VPC endpoints** |
| Office/data centre to AWS, quick and cheap | **Site-to-Site VPN** |
| Steady high-bandwidth, predictable latency hybrid | **Direct Connect** (+ VPN backup) |
| Remote employees to private apps | **Verified Access** (zero trust) or **Client VPN** |

---

## A6. Which load balancer / edge service?

| Need | Choose |
|------|--------|
| HTTP/HTTPS routing by path/host, microservices | **ALB** |
| TCP/UDP, static IPs, millions of rps, PrivateLink | **NLB** |
| Insert third-party firewall appliances | **GWLB** |
| Cache static content globally, protect origin | **CloudFront** (+ WAF) |
| Global static anycast IPs, fast regional failover, non-HTTP | **Global Accelerator** |
| DNS-based routing (latency, weighted, failover, geo) | **Route 53** |
| Managed API front door with throttling/auth/keys | **API Gateway** |

---

## A7. Which way to give access?

| Who/what needs access | Use |
|-----------------------|-----|
| Employees → AWS console/CLI | **IAM Identity Center** (SSO) with your IdP |
| App on EC2 → AWS APIs | **IAM role** via instance profile |
| ECS task → AWS APIs | **ECS task role** |
| EKS pod → AWS APIs | **EKS Pod Identity** / IRSA |
| Lambda → AWS APIs | **Lambda execution role** |
| GitHub Actions / external CI → AWS | **OIDC federation** to an IAM role |
| Another AWS account | **Cross-account IAM role** (with ExternalId for third parties) |
| Your app's end users (sign-up/sign-in) | **Cognito** user pools |
| Temporary access to one private S3 file | **Pre-signed URL** |
| On-prem servers → AWS APIs | **IAM Roles Anywhere** (certificates) or SSM hybrid activation |

> ⚠️ Long-lived **IAM user access keys** are almost never the right answer in modern setups.

---

## A8. Which IaC / deployment tool?

| Situation | Choose |
|-----------|--------|
| Multi-cloud or Terraform-skilled team | **Terraform / OpenTofu** |
| AWS-only, prefer YAML, native support | **CloudFormation** |
| AWS-only, developers prefer TypeScript/Python | **AWS CDK** |
| Serverless apps (Lambda + API Gateway) | **AWS SAM** (or CDK/Serverless Framework) |
| Deploy to many accounts/regions at once | **CloudFormation StackSets** / Terraform with pipelines |
| Blue/green or canary deployments | **CodeDeploy**, ECS blue/green, Lambda aliases |
| CI/CD pipelines | **GitHub Actions + OIDC**, **CodePipeline + CodeBuild**, GitLab CI. See [CI/CD guide](../cicd-pipelines/README.md) |

---

# Part B — 20 Real-World Scenarios

## Scenario 1 — Static Website or SPA

**🎯 Situation:** Company marketing site or React/Vue/Angular SPA. Global users, cheap, HTTPS, no servers.

```
 User ──► Route 53 (example.com, Alias) ──► CloudFront (ACM cert in us-east-1, WAF)
                                               │  Origin Access Control (OAC)
                                               ▼
                                         S3 bucket (private, Block Public Access ON)
```

| Service | Why |
|---------|-----|
| **S3** | Stores the built files cheaply |
| **CloudFront** | HTTPS, global caching, hides the bucket via OAC |
| **ACM** | Free auto-renewing certificate (**must be in us-east-1** for CloudFront) |
| **Route 53** | Alias record at the zone apex |
| **WAF** (optional) | Bot/rate protection |

**⚠️ Gotchas:** SPA deep links return 403/404 from S3 unless CloudFront maps errors to `/index.html`. Invalidate only `index.html` on deploy. Don't use the public "S3 static website hosting" endpoint, because it can't use OAC. Alternative: **Amplify Hosting** (with Git CI/CD and SSR).

---

## Scenario 2 — Classic 3-Tier Web Application

**🎯 Situation:** A Java/.NET/Node web app with a relational database, needing high availability.

```
                     Route 53
                        │
                  CloudFront + WAF (optional)
                        │
   ┌──────────── VPC (3 AZs) ───────────────────────────────────────┐
   │ Public subnets:   ALB (multi-AZ)            NAT GW (per AZ)    │
   │                    │                                           │
   │ Private app:      Auto Scaling group of EC2  (or ECS Fargate)  │
   │                    │            │                              │
   │                    │         ElastiCache (sessions/cache)      │
   │ Private data:     Aurora (writer + reader, Multi-AZ)           │
   └────────────────────────────────────────────────────────────────┘
   Secrets Manager (DB creds) · CloudWatch (metrics/logs/alarms) · AWS Backup
```

| Tier | Services | Why |
|------|----------|-----|
| Web/edge | Route 53, CloudFront, WAF, ALB | DNS, caching, protection, health-checked load balancing |
| App | EC2 ASG across 3 AZs (or ECS Fargate) | Self-healing, scales with load |
| Session/cache | ElastiCache | Makes app servers stateless |
| Data | Aurora Multi-AZ + read replicas | HA, fast failover, read scaling |
| Ops | Secrets Manager, CloudWatch, Systems Manager, AWS Backup | Secrets rotation, monitoring, patching without SSH, backups |

**⚠️ Gotchas:** Sessions stored on instances break scaling (use ElastiCache/DynamoDB). Use SG referencing (DB SG allows only the app SG). NAT per AZ for resilience, and watch NAT data costs.

---

## Scenario 3 — Serverless REST API

**🎯 Situation:** A new API with unpredictable traffic, a small team, and pay-per-use pricing.

```
 Client ──► API Gateway (HTTP API, JWT authorizer ◄── Cognito)
                 │
                 ▼
             Lambda functions ──► DynamoDB (on-demand)
                 │                    │
                 │               DynamoDB Streams ──► Lambda (side effects)
                 └──► Secrets Manager / Parameter Store
 Observability: CloudWatch Logs + X-Ray/ADOT · Deploy: SAM/CDK via CI/CD
```

| Service | Why |
|---------|-----|
| **API Gateway HTTP API** | Cheap, fast front door with JWT auth (REST API if you need usage plans/WAF/request validation) |
| **Lambda** | No servers, scales to zero |
| **DynamoDB on-demand** | Serverless DB, no connection limits, pay per request |
| **Cognito** | User sign-up/sign-in, JWTs |

**⚠️ Gotchas:** Lambda + relational DB → use **RDS Proxy** (connection exhaustion). Set reserved concurrency to protect downstream systems. Cold starts matter for Java (use SnapStart). Design DynamoDB keys around access patterns.

---

## Scenario 4 — Containerised Microservices

**🎯 Situation:** 10–30 services built as Docker images, independent deployments per team.

```
 Users ──► Route 53 ──► ALB (host/path routing) ──► ECS services on Fargate (or EKS)
                                                     │  service-to-service: Service Connect / VPC Lattice
                                                     ├─► Aurora / DynamoDB per service
                                                     └─► SQS/SNS/EventBridge for async events
 ECR (images, scanning) · CodePipeline/GitHub Actions · CloudWatch Container Insights · X-Ray/ADOT
```

| Choice | When |
|--------|------|
| **ECS + Fargate** | AWS-only, want simplicity, small platform team |
| **EKS (Auto Mode)** | Kubernetes skills, multi-cloud consistency, Helm/operators ecosystem |
| **ALB** | One load balancer routing many services by path/host |
| **ECS Service Connect / Cloud Map / VPC Lattice** | Service discovery and service-to-service traffic |
| **Database per service** | Teams own their data independently |

**⚠️ Gotchas:** Microservices multiply operational overhead (tracing, versioning, network costs). ECS task role vs execution role confusion. EKS subnets run out of IPs (VPC CNI). Plan CIDRs or prefix delegation.

---

## Scenario 5 — Event-Driven Order Processing

**🎯 Situation:** E-commerce checkout must stay fast, while payment, inventory, email and analytics happen reliably in the background.

```
 Checkout API ──► EventBridge bus  ──rule: OrderPlaced──►  Step Functions (order saga)
      (Lambda)        │                                     ├─ reserve inventory (Lambda/DynamoDB)
                      │                                     ├─ charge payment (Lambda → payment API)
                      │                                     └─ on failure: compensate (release stock, refund)
                      ├──rule──► SQS ──► Lambda: send confirmation email (SES)
                      └──rule──► Data Firehose ──► S3 data lake (analytics)
 Each queue/target: DLQ + alarms on DLQ depth
```

| Service | Why |
|---------|-----|
| **EventBridge** | Decouples producers from consumers; content-based routing; archive and replay |
| **Step Functions** | Orchestrates the multi-step saga with retries and compensation |
| **SQS + DLQ** | Buffers work; failed messages are kept, not lost |
| **SES** | Transactional email |
| **Firehose → S3** | Analytics without touching the transactional path |

**⚠️ Gotchas:** At-least-once delivery means **idempotent consumers** (idempotency keys). Alarm on DLQ depth. Use the **transactional outbox** pattern if the DB write and event publish must both happen.

---

## Scenario 6 — File Upload and Image Processing

**🎯 Situation:** Users upload photos/documents. Generate thumbnails, scan for malware, extract text.

```
 Browser ──(1) request upload URL──► API Gateway → Lambda (generates pre-signed PUT URL)
    │
    └─(2) PUT file directly ──► S3 "uploads" bucket
                                  │ S3 Event / EventBridge
                                  ▼
                       SQS (buffer) ──► Lambda: thumbnail (Sharp/Pillow) ──► S3 "processed"
                                  ├──► Textract (documents → text) ──► DynamoDB (metadata)
                                  └──► GuardDuty Malware Protection for S3 (scan uploads)
 Delivery: CloudFront in front of "processed" bucket
```

**Why:** Pre-signed URLs keep big files off your servers. SQS between S3 and Lambda smooths spikes and retries failures. CloudFront serves results fast.

**⚠️ Gotchas:** Never write output to the same bucket/prefix that triggers the function (an **infinite loop** that runs up a bill). Validate file type/size. Lifecycle-delete abandoned uploads (and incomplete multipart uploads).

---

## Scenario 7 — Scheduled Jobs and Batch Processing

**🎯 Situation:** Nightly reports, data cleanup, invoice generation, ML batch scoring.

| Job length / type | Service |
|-------------------|---------|
| < 15 min, light | **EventBridge Scheduler → Lambda** |
| Minutes–hours, container | **EventBridge Scheduler → ECS Fargate task** |
| Many parallel compute jobs, queues, Spot savings | **AWS Batch** |
| Multi-step with dependencies, retries, branching | **Step Functions** (scheduled) |
| Big data transformation | **Glue jobs** / **EMR Serverless** |
| Run commands/patches on servers on a schedule | **Systems Manager** (Maintenance Windows, State Manager) |

**⚠️ Gotchas:** Make jobs **idempotent** (they may run twice). Alarm on failures. Schedules are UTC by default unless you set a time zone (EventBridge Scheduler supports time zones).

---

## Scenario 8 — CI/CD for an AWS Application

**🎯 Situation:** Build, test and deploy containers/serverless apps to dev → staging → prod accounts.

```
 GitHub ──► GitHub Actions ──OIDC──► IAM role (tooling account)
                │ build, test, scan (Trivy), push ──► ECR
                ▼
        deploy dev ──► approve ──► deploy staging ──► approve ──► deploy prod
        (cross-account roles; ECS/CodeDeploy blue-green or Lambda alias canary)
 Alternative AWS-native: CodePipeline + CodeBuild + CodeDeploy
```

**Key choices:** **OIDC** instead of access keys. **Separate accounts** per environment. **Build once, promote the same image digest**. **Blue/green or canary** via CodeDeploy, with CloudWatch-alarm rollback. Full examples: [CI/CD Pipelines guide](../cicd-pipelines/README.md).

---

## Scenario 9 — Data Lake and Analytics

**🎯 Situation:** Combine app databases, clickstream and SaaS data for BI dashboards and ad-hoc analysis.

```
 Sources                    Ingest                  Store (S3 zones)           Process/Query        Consume
 RDS/Aurora ──► DMS (CDC) ─┐                       raw/  ──► Glue ETL ──► curated/ (Parquet/Iceberg)
 Clickstream ─► Firehose ──┼──────────────────────►        Glue Data Catalog       Athena · Redshift ─► QuickSight
 SaaS ────────► AppFlow ───┘                        Lake Formation permissions     EMR / SageMaker AI
```

| Service | Role |
|---------|------|
| **S3** | Cheap, durable lake storage in zones (raw → curated) |
| **Glue** | ETL + Data Catalog (table definitions) |
| **Lake Formation** | Fine-grained access (row/column) and cross-account sharing |
| **Athena** | Serverless SQL for ad-hoc queries |
| **Redshift** | High-performance warehouse for heavy BI |
| **QuickSight** | Dashboards |

**⚠️ Gotchas:** Store as **Parquet/Iceberg, partitioned** (Athena charges per TB scanned). Govern PII early (Macie, Lake Formation). Avoid a "data swamp" with no catalogue or owners.

---

## Scenario 10 — Mobile App Backend

**🎯 Situation:** iOS/Android app needing login, user data sync, push notifications, file storage.

| Need | Service |
|------|---------|
| Sign-up/sign-in, social login, MFA | **Cognito** |
| API with real-time updates/offline sync | **AppSync** (GraphQL) or **API Gateway + Lambda** |
| Data | **DynamoDB** |
| Files/images | **S3** + **CloudFront** (pre-signed URLs) |
| Push notifications/SMS | **SNS mobile push** / **AWS End User Messaging** |
| Full-stack scaffolding | **Amplify** |
| Analytics | **Pinpoint alternatives** / third-party (Firebase Analytics, PostHog) |

**⚠️ Gotchas:** Never ship AWS access keys in the app. Use Cognito identity pools for scoped temporary credentials. Compare with Firebase/Supabase for speed of development (see [IT Tools guide](../it-tools-and-websites/README.md#1--backend-as-a-service-baas)).

---

## Scenario 11 — Real-Time Streaming Analytics

**🎯 Situation:** Process IoT sensor data / clickstreams in seconds: detect anomalies, update dashboards.

```
 Devices ──► IoT Core (MQTT) ──rule──► Kinesis Data Streams ──► Managed Service for Apache Flink
 Web apps ─────────────────────────────►        │                  (windowed aggregations, anomaly detection)
                                                ├──► Lambda (alerts → SNS)
                                                └──► Data Firehose ──► S3 (history) / OpenSearch (dashboards)
```

**Choose:** **Kinesis Data Streams** (AWS-native) or **MSK** (Kafka ecosystem). **Flink** for stateful stream processing. **Firehose** to land data. **Timestream/OpenSearch** for time-series dashboards.

**⚠️ Gotchas:** Partition key choice affects ordering and hot shards. Plan retention/replay. Size consumers to keep up (monitor iterator age).

---

## Scenario 12 — Generative AI Chatbot over Company Documents (RAG)

**🎯 Situation:** Employees ask questions; answers must cite internal docs and respect permissions.

```
 Docs (S3/SharePoint/Confluence) ──► Bedrock Knowledge Base (chunk + embed)
                                         └─► Vector store (OpenSearch Serverless / Aurora pgvector / S3 Vectors)
 User ──► Web app (Cognito auth) ──► API Gateway ──► Lambda / Bedrock Agent
                                                       ├─► Retrieve relevant chunks
                                                       ├─► Foundation model on Bedrock (e.g. Claude) generates answer + citations
                                                       └─► Bedrock Guardrails (PII, topics, prompt-attack filters)
 Alternative turnkey option: Amazon Q Business with connectors
```

**Why:** **Bedrock** keeps data inside your AWS account/governance and offers many models. **Knowledge Bases** handle ingestion and retrieval. **Guardrails** add safety. **Q Business** is the no-code alternative.

**⚠️ Gotchas:** Retrieval quality (chunking, metadata, freshness) matters more than model choice. Enforce document-level permissions. Watch token costs and model quotas per region. Treat retrieved content as untrusted (prompt injection).

---

## Scenario 13 — Multi-Account Landing Zone

**🎯 Situation:** A company is starting on AWS, or cleaning up a single messy account, and needs security, governance and billing done right.

```
 Management account (Organizations, billing, Control Tower) — NO workloads
 ├── OU: Security
 │     ├── Log Archive account   (org CloudTrail, Config, VPC Flow Logs → locked S3)
 │     └── Audit/Security Tooling (GuardDuty, Security Hub, Inspector delegated admin)
 ├── OU: Infrastructure
 │     ├── Network account (Transit Gateway, central egress/inspection, Route 53 Resolver)
 │     └── Shared Services (CI/CD tooling, ECR, directory)
 ├── OU: Workloads
 │     ├── Prod  OU → app-prod accounts
 │     └── NonProd OU → app-dev, app-staging accounts
 └── OU: Sandbox (experiments, budget-capped)
 Access: IAM Identity Center + Entra ID/Okta groups → permission sets per account
 Guard-rails: SCPs (deny region use, deny disabling CloudTrail/GuardDuty, deny root use), RCPs (data perimeter)
```

**Tools:** **Control Tower** (or Landing Zone Accelerator), **Organizations**, **Identity Center**, **SCPs/RCPs**, **Config conformance packs**, **Account Factory (AFT)** for account vending via Terraform.

**⚠️ Gotchas:** Don't put workloads in the management account (SCPs don't apply there). Plan the IP address strategy for all accounts up front. Set budgets per account.

---

## Scenario 14 — Hybrid Connectivity to On-Premises

**🎯 Situation:** Apps in AWS must reach an on-prem database/AD and vice versa, securely and reliably.

```
 On-prem DC ──(Direct Connect, 2 locations)──► DX Gateway ──► Transit Gateway ──► VPCs (many accounts)
            └─(Site-to-Site VPN backup)─────────────────────┘
 DNS: Route 53 Resolver inbound/outbound endpoints ↔ on-prem DNS (conditional forwarding)
 Identity: AD Connector / AWS Managed Microsoft AD (trust with on-prem AD)
```

**Choices:** Start with **VPN** (hours to set up). Add **Direct Connect** for bandwidth/latency/cost at scale. Use **Transit Gateway** for many VPCs. **Route 53 Resolver endpoints** for hybrid DNS.

**⚠️ Gotchas:** Overlapping CIDRs between on-prem and VPCs. Single DX = SPOF. Forgetting DNS makes everything "connected but not resolving".

---

## Scenario 15 — Disaster Recovery Across Regions

**🎯 Situation:** The business needs to survive a full region outage. Pick a strategy by RTO/RPO and budget.

| Strategy | AWS implementation | RTO / RPO | Cost |
|----------|--------------------|-----------|------|
| **Backup & restore** | AWS Backup cross-region copies + IaC to rebuild | Hours / hours | $ |
| **Pilot light** | Aurora Global Database / DynamoDB Global Tables / S3 CRR running; compute defined in IaC, scaled to zero | ~10s of min / seconds–minutes | $$ |
| **Warm standby** | Full stack running small in region B; scale up on failover | Minutes / seconds | $$$ |
| **Active-active** | Both regions serve traffic: Route 53 latency/failover, Global Tables / Aurora DSQL | ~0 / ~0 | $$$$ |

**Supporting services:** **Route 53 health checks / ARC** (routing control), **Elastic Disaster Recovery** (server replication), **AWS Backup vault lock** (ransomware-proof copies), **CloudFormation/Terraform** (rebuild).

**⚠️ Gotchas:** DR plans fail without **regular failover tests**. Replicate secrets, AMIs, container images (ECR replication), certificates and quotas to the DR region too. Avoid control-plane dependencies during failover.

---

## Scenario 16 — Migrating a Data Centre to AWS

**🎯 Situation:** 200 VMs, several databases and file shares move to AWS within a year.

| Phase | Services |
|-------|----------|
| **Assess** | Migration Evaluator, Application Discovery Service, AWS Transform/Migration Hub |
| **Mobilise** | Landing zone (Scenario 13), Direct Connect/VPN (Scenario 14), training |
| **Migrate servers** (rehost) | **Application Migration Service (MGN)** |
| **Migrate databases** | **DMS** + Schema Conversion (e.g. Oracle → Aurora PostgreSQL) |
| **Migrate files** | **DataSync**, **FSx**, **Snowball Edge** for huge offline transfers |
| **Optimise** | Rightsize (Compute Optimizer), Savings Plans, replatform to RDS/ECS, modernise over time |

**⚠️ Gotchas:** Map application dependencies before moving (move app + DB together to avoid latency). Rehost first, modernise later. Test cutover and rollback plans.

---

## Scenario 17 — Centralised Logging and Security Monitoring

**🎯 Situation:** Auditors and the security team need all logs in one tamper-resistant place, plus threat detection.

```
 All accounts: CloudTrail (org trail) · Config · VPC Flow Logs · ALB/CloudFront/WAF logs
                     │
                     ▼
 Log Archive account: S3 (Object Lock, KMS, lifecycle to Glacier) ──► Athena / Security Lake / SIEM
 Security account: GuardDuty + Security Hub + Inspector + Macie (delegated admin, all regions)
                     └──► EventBridge ──► SNS / Chatbot / ticketing (high-severity findings)
```

**⚠️ Gotchas:** Enable services in **all regions** (attackers use regions you don't watch). Restrict who can modify the log bucket (SCP + bucket policy). Set retention to meet compliance needs (e.g. 1 year hot, 7 years archive).

---

## Scenario 18 — Secure Private Access Without Internet

**🎯 Situation:** Regulated workloads in private subnets must not use the internet, but need S3, ECR, Secrets Manager, CloudWatch, SSM.

```
 Private subnet (no NAT, no IGW)
   ├── S3, DynamoDB ──────────► Gateway endpoints (free, via route table)
   ├── ECR api/dkr, Logs, SSM, ssmmessages, Secrets Manager, KMS, STS ──► Interface endpoints (PrivateLink)
   └── Admin access ──────────► Session Manager (no bastion, no SSH)
 Endpoint policies restrict to your org's buckets/resources (data perimeter)
```

**⚠️ Gotchas:** Interface endpoints cost per AZ per hour, so centralise them in a shared VPC for many accounts. Enable **private DNS** on endpoints. ECR also needs the **S3 gateway endpoint** (image layers live in S3).

---

## Scenario 19 — Multi-Tenant SaaS

**🎯 Situation:** A B2B SaaS serving hundreds of customers with tenant isolation, per-tenant metering and noisy-neighbour protection.

| Isolation model | Implementation | Trade-off |
|-----------------|----------------|-----------|
| **Silo** (account/stack per tenant) | Separate AWS account or stack per enterprise tenant | Strongest isolation, highest cost/ops |
| **Bridge** | Shared app tier, database/schema per tenant | Balance |
| **Pool** | Shared everything, `tenant_id` on every row/item | Cheapest, needs strict access controls |

**Services:** **Cognito** (tenant claims in JWT), **API Gateway usage plans** (per-tenant throttling), **DynamoDB** with tenant-prefixed keys + IAM conditions (`dynamodb:LeadingKeys`), **Aurora PostgreSQL Row-Level Security**, **cell-based architecture** for scale, **CUR + tags** for cost-per-tenant, **AWS Marketplace** for selling.

**⚠️ Gotchas:** Cross-tenant data leaks are existential. Enforce isolation in the data layer, not just app code. Plan tenant onboarding automation from day one.

---

## Scenario 20 — Cost-Optimised Dev/Test Environments

**🎯 Situation:** Dev/test spend is 40% of the bill, and environments run 24/7 though they're used ~50 hours a week.

| Action | Service | Typical saving |
|--------|---------|----------------|
| Stop instances/RDS outside office hours | **Instance Scheduler on AWS**, EventBridge Scheduler + Lambda | ~65% on those resources |
| Use Spot for CI runners and test workers | **EC2 Spot**, Fargate Spot | Up to ~70–90% |
| Serverless/scale-to-zero databases | **Aurora Serverless v2**, **DynamoDB on-demand** | Pay only when used |
| Graviton instances | `t4g`, `m7g`, `c7g`… | Better price-performance |
| Ephemeral per-PR environments torn down automatically | IaC + CI/CD | No forgotten stacks |
| Budgets per team account + anomaly detection | **Budgets**, **Cost Anomaly Detection** | Early warning |
| Clean up idle resources | **Trusted Advisor**, **Compute Optimizer**, Config rules | Remove waste |
| Lifecycle policies (S3, ECR, snapshots, log retention) | S3 Lifecycle, ECR lifecycle, DLM, CloudWatch retention | Storage creep eliminated |

**⚠️ Gotchas:** NAT Gateways, idle load balancers, unattached EBS volumes, old snapshots and public IPv4 addresses keep charging even when "nothing is running".

---

# Part C — Reference

## C1. Azure ↔ AWS Service Mapping

> Handy since most of this repo is Azure-focused. Equivalents are approximate: features differ.

| Category | Azure | AWS |
|----------|-------|-----|
| Accounts & governance | Management groups / Subscriptions / Resource groups | Organizations OUs / Accounts / (tags, Resource Groups) |
| Governance guard-rails | Azure Policy | SCPs, RCPs, AWS Config rules, Control Tower controls |
| Landing zone | Azure Landing Zones (CAF) | Control Tower / Landing Zone Accelerator |
| Identity (workforce) | Microsoft Entra ID | IAM Identity Center (+ external IdP) |
| Customer identity | Entra External ID (B2C) | Cognito |
| Access control | Azure RBAC role assignments | IAM policies & roles |
| Workload identity | Managed Identity | IAM roles (instance profile, task role, Pod Identity) |
| VMs | Virtual Machines / VM Scale Sets | EC2 / Auto Scaling groups |
| PaaS web apps | App Service | Elastic Beanstalk / App Runner / Amplify Hosting |
| Serverless functions | Azure Functions | Lambda |
| Serverless containers | Container Apps / Container Instances | Fargate (ECS/EKS) / App Runner |
| Kubernetes | AKS | EKS |
| Container registry | ACR | ECR |
| Batch | Azure Batch | AWS Batch |
| Object storage | Blob Storage | S3 |
| Archive | Blob Archive tier | S3 Glacier classes |
| Disks | Managed Disks | EBS |
| File shares | Azure Files / NetApp Files | EFS / FSx |
| Relational DB | Azure SQL / Database for PostgreSQL/MySQL | RDS / Aurora |
| NoSQL | Cosmos DB | DynamoDB (+ DocumentDB, Keyspaces, Neptune) |
| Cache | Azure Cache for Redis / Managed Redis | ElastiCache / MemoryDB |
| Data warehouse | Synapse / Fabric Warehouse | Redshift |
| Ad-hoc SQL on lake | Synapse serverless SQL / Fabric | Athena |
| ETL | Data Factory | Glue (+ AppFlow, DMS) |
| BI | Power BI | QuickSight |
| Search | Azure AI Search | OpenSearch Service / Kendra |
| Virtual network | VNet | VPC |
| Network security | NSG / ASG | Security Groups / NACLs |
| Firewall | Azure Firewall | AWS Network Firewall |
| Hub networking | Virtual WAN / hub VNet | Transit Gateway / Cloud WAN |
| Private service access | Private Endpoint / Private Link | Interface VPC endpoints / PrivateLink |
| Dedicated connectivity | ExpressRoute | Direct Connect |
| VPN | VPN Gateway | Site-to-Site VPN / Client VPN |
| L4 load balancer | Azure Load Balancer | NLB |
| L7 load balancer | Application Gateway (+ WAF) | ALB (+ WAF) |
| Global entry / CDN | Front Door / Azure CDN | CloudFront (+ Global Accelerator) |
| DNS | Azure DNS / Traffic Manager | Route 53 |
| Bastion | Azure Bastion | Systems Manager Session Manager / EC2 Instance Connect |
| Secrets & keys | Key Vault | Secrets Manager + KMS (+ Parameter Store, ACM) |
| Security posture | Defender for Cloud | Security Hub + GuardDuty + Inspector |
| SIEM | Microsoft Sentinel | Security Lake + OpenSearch / partner SIEM |
| Monitoring | Azure Monitor / Log Analytics / App Insights | CloudWatch / CloudWatch Logs / X-Ray & Application Signals |
| Audit logs | Activity Log | CloudTrail |
| IaC (native) | ARM / Bicep | CloudFormation / CDK |
| CI/CD | Azure DevOps / GitHub Actions | CodePipeline + CodeBuild + CodeDeploy / GitHub Actions |
| Artifact feeds | Azure Artifacts | CodeArtifact |
| Messaging queue | Service Bus queues / Storage Queues | SQS |
| Pub/sub | Service Bus topics / Event Grid | SNS / EventBridge |
| Event streaming | Event Hubs | Kinesis Data Streams / MSK |
| Workflows | Logic Apps / Durable Functions | Step Functions |
| API management | API Management | API Gateway |
| Generative AI | Azure AI Foundry / Azure OpenAI | Bedrock |
| ML platform | Azure Machine Learning | SageMaker AI |
| Backup / DR | Azure Backup / Site Recovery | AWS Backup / Elastic Disaster Recovery |
| Migration | Azure Migrate | Application Migration Service / DMS / Migration Hub |
| Virtual desktops | Azure Virtual Desktop | WorkSpaces / AppStream 2.0 |
| Cost tools | Cost Management + Budgets / Advisor | Cost Explorer + Budgets / Trusted Advisor / Compute Optimizer |

---

## C2. Top 20 AWS Mistakes Beginners Make

| # | Mistake | Fix |
|---|---------|-----|
| 1 | Using the root user daily / no MFA on root | Lock root away with MFA; use Identity Center |
| 2 | Access keys committed to GitHub | Roles + OIDC; secret scanning; rotate immediately if leaked |
| 3 | No budget alert → surprise bill | AWS Budgets + Cost Anomaly Detection on day one |
| 4 | Public S3 buckets | Account-level Block Public Access; CloudFront OAC for websites |
| 5 | `0.0.0.0/0` on SSH/RDP security groups | Session Manager; no inbound admin ports |
| 6 | Everything in one account | Multi-account with Organizations/Control Tower |
| 7 | Single-AZ production | Multi-AZ for ALB, compute and databases |
| 8 | No backups / never tested restores | AWS Backup with tested restores, cross-region copies |
| 9 | Forgetting NAT Gateway & data transfer costs | VPC endpoints; watch cross-AZ traffic; NAT per AZ only where needed |
| 10 | CloudWatch logs kept forever | Set log retention |
| 11 | Hard-coded config/secrets in code or AMIs | Parameter Store / Secrets Manager |
| 12 | Lambda writing to the bucket that triggers it | Separate buckets/prefixes; recursion detection |
| 13 | Over-sized instances "just in case" | Compute Optimizer; autoscaling; Graviton |
| 14 | No tags → can't attribute cost | Tagging standard + cost allocation tags |
| 15 | Manual console changes in prod | IaC + drift detection |
| 16 | Ignoring service quotas before launch | Check/request increases early |
| 17 | IMDSv1 left enabled | Require IMDSv2 |
| 18 | Unencrypted EBS/RDS/S3 | Default encryption settings; KMS |
| 19 | CloudTrail/GuardDuty not enabled in all regions | Org-wide trail and delegated-admin GuardDuty |
| 20 | Deleting a KMS key or a stack with data | Deletion protection, `DeletionPolicy: Retain`, KMS waiting period |

---

## C3. AWS Certification Path

| Level | Certification | Good for |
|-------|---------------|----------|
| Foundational | **Cloud Practitioner (CLF)** | Anyone new to AWS; business/tech basics |
| Foundational | **AI Practitioner (AIF)** | AI/GenAI concepts on AWS |
| Associate | **Solutions Architect – Associate (SAA)** | Most popular; designing on AWS. Great first technical cert |
| Associate | **Developer – Associate (DVA)** | Building/deploying apps (Lambda, DynamoDB, CI/CD) |
| Associate | **CloudOps Engineer – Associate** (formerly SysOps Administrator) | Operations, monitoring, troubleshooting |
| Associate | **Data Engineer – Associate** / **Machine Learning Engineer – Associate** | Data pipelines / ML engineering |
| Professional | **Solutions Architect – Professional (SAP)** | Complex multi-account, hybrid, migration architectures |
| Professional | **DevOps Engineer – Professional (DOP)** | CI/CD, automation, monitoring, governance at scale |
| Specialty | **Security**, **Advanced Networking**, **Machine Learning** (check current specialty list) | Deep domain expertise |

> 🧭 **Suggested DevOps path:** Cloud Practitioner (optional) → **Solutions Architect – Associate** →
> **CloudOps** or **Developer – Associate** → **DevOps Engineer – Professional**. Use **AWS Skill
> Builder** labs and build the scenarios above in a sandbox account (with a budget alert!).
> Certification names and versions change. Confirm on aws.amazon.com/certification.

---

[⬅️ Back to AWS Index](README.md) · [01 — Terms](01-aws-terms.md) · [02 — Services](02-aws-services.md)
