[🏠 Home](../README.md) · [☁️ AWS](README.md)

# 📖 AWS Terms & Concepts — Explained

> **~170 AWS terms** grouped by domain. Each has a plain-English definition, an example, and a
> ⚠️ gotcha or exam tip where useful. Level badges: 🌱 beginner · 🧩 intermediate · 🚀 advanced.
>
> For vendor-neutral terms (CI/CD, Kubernetes, SRE…) see the [DevOps Glossary](../devops-glossary/README.md).
> For the services themselves, see [02 — AWS Services](02-aws-services.md).

---

## 📑 Table of Contents

1. [Global Infrastructure](#1--global-infrastructure)
2. [Accounts, Organizations & Billing](#2--accounts-organizations--billing)
3. [Identity & Access (IAM)](#3--identity--access-iam)
4. [Networking (VPC & Connectivity)](#4--networking-vpc--connectivity)
5. [Compute (EC2 & Scaling)](#5--compute-ec2--scaling)
6. [Storage](#6--storage)
7. [Databases](#7--databases)
8. [Serverless & Containers](#8--serverless--containers)
9. [Security & Encryption](#9--security--encryption)
10. [Monitoring, Management & IaC](#10--monitoring-management--iac)
11. [Reliability, DR & Architecture](#11--reliability-dr--architecture)
12. [Cost & Pricing](#12--cost--pricing)

---

# 1 — Global Infrastructure

### 🌱 Region
**What:** A geographic area containing multiple, isolated data-centre groups (AZs), e.g. `ap-south-1` (Mumbai), `us-east-1` (N. Virginia), `eu-west-1` (Ireland).
**Example:** Deploy in Mumbai for Indian users (low latency, data residency).
**⚠️** Most services are **regional**: resources in one region aren't visible in another. Prices and service availability differ per region. `us-east-1` often gets features first, and it's also where some global services (IAM, CloudFront certificates via ACM, billing) live.

### 🌱 Availability Zone (AZ)
**What:** One or more discrete data centres in a region, with independent power, cooling and networking, connected to the other AZs by low-latency links. Named like `ap-south-1a`.
**Example:** Run EC2 instances in 3 AZs behind a load balancer, so one AZ failing doesn't take you down.
**⚠️** AZ names are **mapped differently per account** (your `1a` may not be another account's `1a`). Use **AZ IDs** (`aps1-az1`) when coordinating across accounts. Cross-AZ data transfer costs money.

### 🌱 Edge Location / Point of Presence (PoP)
**What:** Sites in hundreds of cities where CloudFront (CDN), Route 53 (DNS) and Global Accelerator serve users close to them.
**Example:** A user in Pune gets images from a nearby CloudFront edge instead of a US bucket.

### 🧩 Local Zone
**What:** An extension of a region placed in a large city, bringing compute/storage closer to users for single-digit-millisecond latency.
**Example:** Media rendering or gaming servers in a metro-area Local Zone.

### 🧩 Wavelength Zone
**What:** AWS infrastructure embedded in telecom 5G networks for ultra-low-latency mobile apps.
**Example:** AR/VR or connected-vehicle apps.

### 🚀 AWS Outposts
**What:** AWS-managed racks/servers installed in **your** data centre, running AWS services locally with the same APIs.
**Example:** A factory needing local processing with low latency, but managed like AWS.

### 🧩 Global vs Regional vs Zonal Services
**What:** **Global**: IAM, Route 53, CloudFront, Organizations. **Regional**: S3 (buckets live in a region), Lambda, DynamoDB, VPC. **Zonal**: EC2 instances, EBS volumes, subnets.
**⚠️** An EBS volume can only attach to an instance in the **same AZ**. To move it, snapshot and restore in the other AZ.

---

# 2 — Accounts, Organizations & Billing

### 🌱 AWS Account
**What:** The basic container for AWS resources, with its own billing, security boundary and quotas.
**Example:** Separate accounts for `dev`, `staging`, `prod`, `security`, `logging`.
**⚠️** The account is the **strongest isolation boundary** in AWS. Multi-account setups are best practice.

### 🌱 Root User
**What:** The email-address login that created the account, with unrestricted access.
**Example:** Used only for a few tasks (changing the support plan, closing the account, some billing settings).
**⚠️** Enable **MFA on root**, delete root access keys, and never use root for daily work. A compromised root = a lost account.

### 🧩 AWS Organizations
**What:** A service to centrally manage many accounts: consolidated billing, grouping into OUs, and policy guard-rails.
**Example:** The management account owns the organisation; workload accounts sit in OUs like `Workloads/Prod`.

### 🧩 Organizational Unit (OU)
**What:** A folder of accounts inside an Organization, where policies can be attached.
**Example:** `Security`, `Infrastructure`, `Workloads/Prod`, `Workloads/NonProd`, `Sandbox` OUs.

### 🚀 SCP (Service Control Policy)
**What:** An Organizations policy setting the **maximum permissions** for accounts in an OU. It doesn't grant anything; it only limits.
**Example:** Deny leaving the organisation; deny all regions except `ap-south-1` and `us-east-1`; deny disabling CloudTrail.
**⚠️** SCPs don't affect the **management account**. Keep workloads out of it.

### 🚀 RCP (Resource Control Policy)
**What:** An Organizations policy setting maximum permissions on **resources** (e.g. S3 buckets, KMS keys) across accounts, for "data perimeter" controls.
**Example:** Ensure no S3 bucket in the org can be accessed by principals outside the organisation.

### 🚀 AWS Control Tower / Landing Zone
**What:** **Landing zone** = a well-architected multi-account baseline (accounts, networking, logging, guard-rails). **Control Tower** automates setting one up and governing it (controls, Account Factory).
**Example:** New team gets a pre-configured account with CloudTrail, Config, SSO and guard-rails in minutes.

### 🌱 Consolidated Billing
**What:** One bill for all accounts in an Organization, with combined usage for volume discounts and shared Savings Plans/RIs.

### 🌱 Free Tier
**What:** Free usage allowances for new accounts and some always-free services.
**⚠️** Free Tier terms changed in 2025 (credit-based plans for new accounts). Read the current terms, and **set a budget alert** on day one. Exceeding limits silently creates charges.

### 🌱 Service Quotas (Limits)
**What:** Per-account, per-region caps on resources/API rates (e.g. number of vCPUs for On-Demand instances, VPCs per region).
**Example:** Request a quota increase **weeks before** a big launch.
**⚠️** A common cause of "it worked in dev but fails at scale".

### 🌱 Tags
**What:** Key-value labels on resources (`Environment=prod`, `Owner=payments`, `CostCenter=1234`).
**⚠️** Activate **cost allocation tags** in Billing to see costs per tag. Enforce tagging with tag policies/SCPs/IaC.

### 🧩 Support Plans
**What:** Basic (free), Developer, Business, Enterprise On-Ramp, Enterprise, with increasing response times, Trusted Advisor checks and a TAM at the top.
**⚠️** Production workloads usually need at least **Business** support for 24/7 technical help.

---

# 3 — Identity & Access (IAM)

### 🌱 IAM (Identity and Access Management)
**What:** The global service controlling **who** can do **what** on **which** AWS resources.

### 🌱 IAM User
**What:** A long-lived identity with a password (console) and/or access keys (CLI/API).
**⚠️** Modern best practice: **avoid IAM users for humans**. Use IAM Identity Center (SSO) instead, and roles for workloads. Access keys leak (GitHub!) and must be rotated.

### 🌱 IAM Group
**What:** A collection of IAM users sharing permissions.
**⚠️** Groups can't be nested, and can't be used as a principal in resource policies.

### 🌱 IAM Role
**What:** An identity with permissions but **no long-term credentials**. Trusted entities **assume** it and get temporary credentials.
**Example:** An EC2 instance role reading S3; a CI pipeline assuming a deploy role via OIDC; cross-account access.
**⚠️** Roles + temporary credentials are the default answer for "how should X access AWS?".

### 🧩 Trust Policy vs Permissions Policy
**What:** A role has two policies. The **trust policy** says **who can assume** it. The **permissions policy** says **what it can do**.
**Example:** Trust: `"Principal": {"Service": "ec2.amazonaws.com"}`. Permissions: `s3:GetObject` on one bucket.

### 🌱 Policy (JSON)
**What:** A JSON document with statements: `Effect` (Allow/Deny), `Action`, `Resource`, optional `Condition`, and (in resource policies) `Principal`.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::acme-reports/*",
    "Condition": { "Bool": { "aws:SecureTransport": "true" } }
  }]
}
```

### 🧩 Policy Types
**What:**
- **Identity-based**: attached to users/groups/roles.
- **Resource-based**: attached to resources (S3 bucket policy, KMS key policy, SQS queue policy). They include a `Principal`.
- **AWS managed / customer managed / inline**: reusable AWS-written, reusable self-written, or embedded in one identity.
- **Permissions boundary**: the maximum permissions an identity can have.
- **SCP/RCP**: org-level maximums.
- **Session policy**: further restricts a temporary session.

**⚠️** Effective permission = allowed by identity/resource policies **AND** not exceeded by boundaries/SCPs/session policies **AND** no explicit Deny anywhere.

### 🧩 Explicit Deny / Implicit Deny
**What:** Everything is denied by default (implicit deny). An Allow grants access, but any **explicit Deny always wins**.

### 🌱 ARN (Amazon Resource Name)
**What:** A unique ID for a resource: `arn:partition:service:region:account-id:resource`.
**Example:** `arn:aws:iam::123456789012:role/deploy`, `arn:aws:s3:::my-bucket/*` (S3 ARNs have no region/account).

### 🌱 Principal
**What:** An entity that can make requests: user, role, AWS service, federated user, account.

### 🧩 STS (Security Token Service) / AssumeRole
**What:** Issues **temporary credentials** (access key, secret, session token) when a role is assumed (`AssumeRole`, `AssumeRoleWithWebIdentity`, `AssumeRoleWithSAML`).
**Example:** `aws sts assume-role --role-arn arn:aws:iam::222:role/admin --role-session-name me`.

### 🧩 IAM Identity Center (formerly AWS SSO)
**What:** Central workforce login across all accounts in an Organization, connected to an identity provider (Entra ID, Okta, Google) or its own directory. Users get **permission sets** per account.
**Example:** Engineers log in via Entra ID → choose `prod-readonly` or `dev-admin`. Short-lived CLI credentials via `aws sso login`.

### 🧩 Instance Profile
**What:** The container that attaches an IAM role to an EC2 instance. Apps on the instance get credentials from the **instance metadata service (IMDS)**.
**⚠️** Enforce **IMDSv2** (session tokens). IMDSv1 has been abused via SSRF attacks to steal role credentials.

### 🚀 OIDC Federation / Web Identity
**What:** Trusting an external OpenID Connect provider (GitHub Actions, EKS service accounts, Google) to assume roles **without stored keys**.
**Example:** GitHub Actions → `AssumeRoleWithWebIdentity` with the trust condition `repo:acme/api:environment:prod`. See [CI/CD Ch 05](../cicd-pipelines/05-devsecops.md).

### 🚀 IRSA / EKS Pod Identity
**What:** Giving Kubernetes pods in EKS their own IAM roles (IRSA via OIDC; Pod Identity via an EKS agent, which is simpler).
**⚠️** Never share the node role's broad permissions with every pod.

### 🧩 Least Privilege & IAM Access Analyzer
**What:** Grant only needed permissions. **Access Analyzer** finds resources shared outside your account/org, validates policies, and can generate least-privilege policies from CloudTrail activity.

### 🚀 ABAC (Attribute-Based Access Control)
**What:** Permissions based on **tags** matching between principal and resource, e.g. allow if `aws:PrincipalTag/Team == aws:ResourceTag/Team`.
**Example:** One policy for all teams, scaling without per-team policies.

### 🚀 Confused Deputy
**What:** A service tricked into acting on another account's behalf. Prevented with `aws:SourceArn` / `aws:SourceAccount` conditions and `ExternalId` for third-party role assumption.

---

# 4 — Networking (VPC & Connectivity)

### 🌱 VPC (Virtual Private Cloud)
**What:** Your logically isolated private network in a region, with your chosen IP range (CIDR).
**Example:** `10.20.0.0/16` VPC with public, private-app and private-data subnets in 3 AZs.
**⚠️** Plan non-overlapping CIDRs across VPCs/on-prem, because overlaps block peering/Transit Gateway/VPN routing later.

### 🌱 Subnet (Public / Private)
**What:** A range of IPs in a VPC within **one AZ**. **Public** = its route table has a route to an Internet Gateway. **Private** = no direct internet route.
**⚠️** AWS reserves **5 IPs** per subnet. Size subnets generously (EKS pods consume IPs).

### 🌱 Route Table
**What:** Rules deciding where subnet traffic goes (`0.0.0.0/0 → igw-…`, `10.30.0.0/16 → tgw-…`).

### 🌱 Internet Gateway (IGW)
**What:** Allows internet traffic in/out of a VPC for resources with public IPs in public subnets.

### 🌱 NAT Gateway
**What:** Lets resources in private subnets reach the internet **outbound only**.
**⚠️** NAT Gateways cost per hour **plus per GB processed**, often a surprisingly large line item. Use one per AZ for HA, and **VPC endpoints** for S3/DynamoDB/ECR traffic to avoid NAT charges.

### 🧩 Egress-Only Internet Gateway
**What:** NAT-like outbound-only internet for **IPv6** traffic.

### 🌱 Security Group (SG)
**What:** A **stateful** virtual firewall on ENIs/instances. Allow rules only; return traffic is automatically allowed.
**Example:** App SG allows 8080 **from the ALB's security group** (SG referencing instead of IP ranges).

### 🧩 Network ACL (NACL)
**What:** A **stateless** subnet-level firewall with ordered allow **and** deny rules.
**⚠️** Being stateless, NACLs need rules for return traffic too (ephemeral ports 1024–65535). Most teams rely on SGs and leave NACLs at default.

| | Security Group | NACL |
|---|---|---|
| Level | ENI/instance | Subnet |
| State | Stateful | Stateless |
| Rules | Allow only | Allow + Deny, numbered order |
| Typical use | Primary control | Coarse blocks (e.g. deny a bad IP range) |

### 🌱 Elastic IP (EIP)
**What:** A static public IPv4 address you own until released.
**⚠️** AWS charges for **all public IPv4 addresses** (since 2024), attached or not.

### 🧩 ENI (Elastic Network Interface)
**What:** A virtual network card with private IP(s), SGs and a MAC. It can move between instances.

### 🧩 VPC Endpoint (Gateway / Interface)
**What:** Private access to AWS services without the internet/NAT. **Gateway endpoints** (S3, DynamoDB) are free route-table entries. **Interface endpoints** (most services, via PrivateLink) are ENIs with private IPs, charged per hour/GB.
**Example:** Private ECS tasks pull images from ECR via interface endpoints, and fetch layers from S3 via the gateway endpoint.

### 🚀 AWS PrivateLink
**What:** Exposes a service (yours or AWS's) privately to other VPCs/accounts through interface endpoints, with **no peering and no overlapping-CIDR problems**.
**Example:** A SaaS vendor offers its API to customers via PrivateLink.

### 🧩 VPC Peering
**What:** A private connection between two VPCs (same or different account/region).
**⚠️** **Not transitive** (A↔B, B↔C doesn't give A↔C) and no overlapping CIDRs. Many VPCs → use Transit Gateway.

### 🧩 Transit Gateway (TGW)
**What:** A regional cloud router connecting many VPCs and on-prem networks (hub-and-spoke), with route tables for segmentation.
**Example:** 40 VPCs + Direct Connect + VPN attached to one TGW; prod and non-prod isolated via separate TGW route tables.

### 🧩 Site-to-Site VPN
**What:** An encrypted IPsec tunnel over the internet between on-prem and AWS (2 tunnels per connection for redundancy).

### 🧩 Direct Connect (DX)
**What:** A dedicated private network connection from your data centre/colocation to AWS: consistent latency, high bandwidth, lower data-transfer rates.
**⚠️** Takes weeks to provision. A single DX is a single point of failure, so use VPN backup or redundant DX locations.

### 🧩 Client VPN
**What:** Managed OpenVPN-based remote access for users into VPCs.

### 🚀 VPC Lattice
**What:** An application-layer networking service connecting services across VPCs/accounts with built-in auth policies and traffic management, without managing peering/TGW for app-to-app traffic.

### 🧩 Load Balancer Types (ELB)
**What:**
- **ALB** (Application, L7 HTTP/HTTPS): path/host routing, OIDC auth, WebSockets, Lambda targets.
- **NLB** (Network, L4 TCP/UDP/TLS): ultra-low latency, static IPs, millions of requests per second, PrivateLink.
- **GWLB** (Gateway, L3): inserts third-party firewalls/appliances transparently.
- **CLB** (Classic): legacy, avoid for new work.

### 🧩 Target Group / Health Check / Listener
**What:** A **listener** (port/protocol) routes to **target groups** (instances, IPs, Lambda). **Health checks** decide which targets get traffic.

### 🌱 Route 53 Hosted Zone / Record
**What:** A **public** or **private** (VPC-only) DNS zone holding records (A, AAAA, CNAME, MX, TXT, **Alias**).
**⚠️** **Alias records** can point the zone apex (`example.com`) to ALB/CloudFront/S3 websites, which a CNAME can't. Alias queries to AWS resources are free.

### 🧩 Route 53 Routing Policies
**What:** **Simple**, **Weighted** (canary/A-B), **Latency-based**, **Failover** (active-passive with health checks), **Geolocation**, **Geoproximity**, **Multivalue answer**, **IP-based**.

### 🚀 VPC Flow Logs
**What:** Logs of IP traffic metadata (source/destination, port, accept/reject) for ENIs/subnets/VPCs, sent to CloudWatch Logs or S3.
**Example:** Debugging "connection timed out" (REJECT means SG/NACL blocked it) and security investigations.

---

# 5 — Compute (EC2 & Scaling)

### 🌱 EC2 Instance
**What:** A virtual server in AWS.

### 🌱 AMI (Amazon Machine Image)
**What:** A template (OS + software + config) used to launch instances. AMIs are regional, so copy them to other regions.
**Example:** A "golden AMI" baked with Packer/EC2 Image Builder.

### 🌱 Instance Type & Families
**What:** The instance's CPU/memory/network/storage size, e.g. `m7g.large`. Family letters: **t** burstable, **m** general purpose, **c** compute-optimised, **r/x** memory-optimised, **i/d** storage-optimised, **p/g/inf/trn** accelerated (GPU/ML). Suffix **g** = Graviton (ARM), **a** = AMD, **i** = Intel, **n** = network-enhanced, **d** = local NVMe.
**⚠️** **Graviton** (ARM) instances typically give better price-performance. Images must be built for arm64.

### 🧩 Burstable Instances (T family) & CPU Credits
**What:** `t3/t4g` earn CPU credits while idle and spend them when busy. In **unlimited** mode you pay for extra bursting.
**⚠️** A constantly busy T instance either gets throttled (standard mode) or runs up surprise charges (unlimited mode).

### 🌱 EBS (Elastic Block Store) Volume
**What:** Network-attached block storage (a virtual disk) for EC2. It persists independently of the instance, in **one AZ**.
**Types:** `gp3` general SSD (default; set IOPS/throughput independently), `io2 Block Express` high-IOPS SSD, `st1` throughput HDD, `sc1` cold HDD.

### 🧩 Instance Store
**What:** Physically attached temporary disks (very fast NVMe).
**⚠️** **Data is lost** when the instance stops/terminates or the host fails. Use it for caches/scratch data only.

### 🌱 Key Pair
**What:** SSH key pair for logging into Linux instances (or decrypting the Windows admin password).
**⚠️** Prefer **Session Manager** (no open port 22, no keys to manage, full audit).

### 🌱 User Data
**What:** A script that runs at first boot to configure an instance.

### 🧩 Launch Template
**What:** A versioned blueprint for launching instances (AMI, type, SGs, user data, IAM role), used by Auto Scaling groups.

### 🌱 Auto Scaling Group (ASG)
**What:** Keeps a fleet of EC2 instances at the desired size across AZs, replaces unhealthy ones, and scales on policies.
**Policies:** target tracking (keep CPU at 50%), step scaling, scheduled scaling, predictive scaling.
**⚠️** Use ELB health checks (not just EC2 status checks) so instances with a broken app get replaced.

### 🧩 Placement Groups
**What:** **Cluster** (same rack, lowest latency, HPC), **Spread** (different hardware, max 7 per AZ, critical instances), **Partition** (groups of racks, for Kafka/HDFS/Cassandra).

### 🧩 Purchasing Options
**What:**
- **On-Demand**: pay per second, no commitment.
- **Savings Plans**: commit to $/hour for 1 or 3 years. Compute Savings Plans also cover Fargate and Lambda.
- **Reserved Instances**: commit to a specific instance configuration for 1/3 years.
- **Spot**: spare capacity at up to ~90% off, with 2 minutes' notice before interruption.
- **Dedicated Hosts / Instances**: physical isolation, licensing (BYOL).
- **Capacity Reservations**: guarantee capacity in an AZ.

**⚠️** Typical mix: Savings Plans for the steady baseline + Spot for fault-tolerant work + On-Demand for the rest.

### 🧩 Nitro System
**What:** AWS's hypervisor and offload hardware, the basis of modern EC2: near-bare-metal performance, enhanced security, Nitro Enclaves for isolated processing of sensitive data.

### 🧩 EC2 Status Checks
**What:** **System** status (AWS host problems → stop/start to move hosts) and **instance** status (OS problems → reboot/fix). Plus EBS-attached checks.

---

# 6 — Storage

### 🌱 S3 Bucket / Object / Key
**What:** S3 stores **objects** (files up to 5 TB plus metadata) in **buckets**. The **key** is the object's full name/path (`reports/2026/oct.csv`). Bucket names are globally unique.
**⚠️** "Folders" are just key prefixes. S3 is object storage, not a file system you mount.

### 🌱 Durability vs Availability
**What:** S3 Standard is designed for **99.999999999% (11 nines) durability** (data won't be lost) and 99.99% availability (you can reach it).
**⚠️** Durability doesn't protect against **you** deleting/overwriting data. Use versioning, Object Lock and backups.

### 🧩 S3 Storage Classes

| Class | Use for |
|-------|---------|
| **S3 Standard** | Frequently accessed data |
| **S3 Intelligent-Tiering** | Unknown/changing access patterns (auto-moves objects between tiers) |
| **S3 Standard-IA** | Infrequent access, quick retrieval (retrieval fee) |
| **S3 One Zone-IA** | Re-creatable infrequent data, single AZ |
| **S3 Express One Zone** | Ultra-low-latency, high-request-rate data in one AZ |
| **S3 Glacier Instant Retrieval** | Archive accessed quarterly, millisecond access |
| **S3 Glacier Flexible Retrieval** | Archive, minutes-to-hours retrieval |
| **S3 Glacier Deep Archive** | Long-term compliance archive, ~12-hour retrieval, cheapest |

**⚠️** IA/Glacier classes have **minimum storage durations and retrieval fees**. Tiny objects can cost more there than in Standard.

### 🧩 S3 Lifecycle Rules
**What:** Automatically transition objects to cheaper classes, or delete them after N days.
**Example:** Logs: Standard → Standard-IA at 30 days → Glacier at 90 → delete at 400.

### 🧩 S3 Versioning / Object Lock / MFA Delete
**What:** **Versioning** keeps every version (protects against overwrite/delete). **Object Lock** (WORM) prevents deletion for a retention period (governance/compliance modes). MFA Delete requires MFA to permanently delete versions.
**⚠️** Object Lock compliance mode can't be shortened even by root. It's ideal for ransomware-proof backups.

### 🧩 S3 Block Public Access / Bucket Policy / ACLs
**What:** **Block Public Access** (on by default for new buckets) overrides any public grants. **Bucket policies** control access. **ACLs** are legacy and disabled by default (Object Ownership: bucket owner enforced).
**⚠️** Publicly exposed S3 buckets are among the most common cloud data leaks. Keep BPA on at the account level.

### 🧩 S3 Replication (CRR / SRR)
**What:** Asynchronously copy objects to another bucket in another region (CRR) or the same region (SRR).
**Example:** DR copy in another region; aggregating logs into a central account.

### 🧩 Pre-signed URL
**What:** A time-limited URL granting temporary access to upload/download a private object.
**Example:** A web app lets users upload directly to S3 without passing files through the server.

### 🧩 EFS (Elastic File System)
**What:** Managed **NFS** file system for Linux, shared by many instances/containers across AZs, growing automatically.

### 🧩 FSx
**What:** Managed third-party file systems: **FSx for Windows File Server** (SMB, AD), **FSx for Lustre** (HPC/ML), **FSx for NetApp ONTAP**, **FSx for OpenZFS**.

### 🧩 EBS Snapshot
**What:** Incremental point-in-time backups of EBS volumes, stored in S3 (managed by AWS). They can be copied cross-region/account.
**⚠️** Automate snapshots with **Data Lifecycle Manager** or **AWS Backup**, including retention, or old snapshots pile up costs.

### 🧩 Storage Gateway
**What:** A hybrid appliance giving on-prem apps access to cloud storage: File Gateway (NFS/SMB → S3), Volume Gateway, Tape Gateway (virtual tapes → Glacier).

---

# 7 — Databases

### 🌱 RDS (Relational Database Service)
**What:** Managed relational databases: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2. AWS handles patching, backups and failover.

### 🧩 Multi-AZ Deployment
**What:** A synchronous standby in another AZ with automatic failover (usually 1–2 minutes). The **Multi-AZ DB cluster** option adds two readable standbys.
**⚠️** A Multi-AZ standby (classic) is **not** for reads. It's for HA. Use read replicas for scaling reads.

### 🧩 Read Replica
**What:** Asynchronous copies for read scaling, which can also be cross-region (and promoted for DR).
**⚠️** Replication lag means replicas can return stale data.

### 🧩 Amazon Aurora
**What:** AWS's cloud-native MySQL/PostgreSQL-compatible engine. Storage is replicated 6 ways across 3 AZs, with up to 15 read replicas and fast failover.
**Variants:** **Aurora Serverless v2** (auto-scales capacity in fine increments), **Aurora Global Database** (cross-region, ~1-second replication, DR), **Aurora DSQL** (distributed serverless SQL, active-active).

### 🧩 Automated Backups / Point-in-Time Recovery (PITR)
**What:** Daily snapshots + transaction logs allow restoring to any second within the retention window (up to 35 days).
**⚠️** A restore creates a **new** DB instance/endpoint. Your app config must switch to it.

### 🧩 RDS Proxy
**What:** Managed connection pooling in front of RDS/Aurora.
**Example:** Thousands of Lambda invocations sharing a few DB connections instead of exhausting `max_connections`.

### 🌱 DynamoDB Table / Item / Partition Key / Sort Key
**What:** DynamoDB is a serverless NoSQL key-value/document database. A table holds **items** (up to 400 KB each), identified by a **partition key** (plus optional **sort key**).
**Example:** `PK = CUSTOMER#42`, `SK = ORDER#2026-10-18#A12`.
**⚠️** Design around **access patterns first**. Uneven keys create **hot partitions**.

### 🧩 DynamoDB Capacity Modes
**What:** **On-demand** (pay per request, instant scaling, good default for variable/new workloads) vs **provisioned** (set RCU/WCU, optionally auto-scaled, cheaper for steady load).

### 🧩 GSI / LSI (Secondary Indexes)
**What:** **Global Secondary Index**: alternate partition/sort key, can be added anytime, eventually consistent. **Local Secondary Index**: same partition key with a different sort key, defined at table creation.

### 🚀 DynamoDB Streams / Global Tables / DAX / TTL
**What:** **Streams**: change feed that triggers Lambda. **Global Tables**: multi-region, multi-active replication. **DAX**: in-memory cache with microsecond reads. **TTL**: auto-expire items for free.

### 🧩 Single-Table Design
**What:** A DynamoDB modelling technique storing multiple entity types in one table, with generic keys, to serve many access patterns in single queries.
**⚠️** Powerful, but harder to learn and change. Not mandatory for every app.

### 🧩 ElastiCache / MemoryDB
**What:** **ElastiCache**: managed in-memory cache (Valkey, Redis OSS, Memcached). **MemoryDB**: Redis/Valkey-compatible **durable** primary database.

---

# 8 — Serverless & Containers

### 🌱 Serverless
**What:** Services where AWS manages servers, scaling and availability, and you pay for use: Lambda, Fargate, DynamoDB, S3, SQS, SNS, EventBridge, Step Functions, API Gateway, Aurora Serverless.

### 🌱 Lambda Function / Handler / Runtime
**What:** Code that runs in response to events. The **handler** is the entry function. The **runtime** is the language environment (Python, Node.js, Java, .NET, Go/custom via OS-only runtimes, container images).
**Limits to remember:** max **15-minute** timeout, up to 10,240 MB memory (CPU scales with memory), ephemeral `/tmp` up to 10 GB.

### 🧩 Cold Start
**What:** Extra latency when Lambda creates a new execution environment (download code, start runtime, run init code).
**Mitigation:** smaller packages, lighter frameworks, **Provisioned Concurrency**, **SnapStart** (Java, Python, .NET).

### 🧩 Concurrency (Reserved / Provisioned)
**What:** Number of simultaneous executions. The account has a regional concurrency quota. **Reserved concurrency** guarantees and **caps** a function's concurrency. **Provisioned concurrency** keeps environments pre-warmed.
**⚠️** One runaway function can consume the whole account's concurrency and throttle every other function. Set reserved concurrency on critical or risky functions.

### 🧩 Event Source Mapping
**What:** Lambda polling a stream/queue (SQS, Kinesis, DynamoDB Streams, MSK) and invoking the function with batches.
**⚠️** Configure partial batch failure reporting and DLQs, or one bad message blocks/retries the whole batch.

### 🧩 Synchronous vs Asynchronous Invocation
**What:** **Sync** (API Gateway, SDK `RequestResponse`): the caller waits for the result. **Async** (S3, SNS, EventBridge): Lambda queues the event and retries twice on error, with destinations/DLQ for failures.

### 🧩 Lambda Layer
**What:** A shared package of libraries/dependencies attached to multiple functions.

### 🧩 Function URL
**What:** A built-in HTTPS endpoint for a Lambda function, without API Gateway.
**⚠️** Simple, but lacks API Gateway features (usage plans, request validation, WAF on REST APIs).

### 🌱 ECS (Elastic Container Service) — Cluster / Task Definition / Task / Service
**What:** AWS-native container orchestration. A **task definition** (image, CPU/memory, env, IAM role) runs as **tasks**. A **service** keeps N tasks running behind a load balancer.

### 🧩 Launch Type / Capacity Provider: EC2 vs Fargate
**What:** **Fargate**: serverless containers, no instances to manage. **EC2**: you manage the instances (more control, GPUs, cheaper at scale with Savings Plans/Spot).

### 🧩 Task Role vs Task Execution Role
**What:** **Task role**: permissions for **your app** (read S3). **Execution role**: permissions for **ECS itself** (pull the image from ECR, write logs, fetch secrets).
**⚠️** Mixing them up is the #1 ECS IAM confusion.

### 🌱 EKS (Elastic Kubernetes Service)
**What:** Managed Kubernetes control plane. Workers run as managed node groups, self-managed nodes, Fargate, or **EKS Auto Mode** (AWS manages nodes, autoscaling via Karpenter, and core add-ons).
**⚠️** EKS versions have support windows. Plan upgrades, because extended support costs extra.

### 🌱 ECR (Elastic Container Registry)
**What:** Private (and public) container image registry with scanning, lifecycle policies, replication and pull-through cache.

---

# 9 — Security & Encryption

### 🌱 Shared Responsibility Model
**What:** AWS secures **of** the cloud (hardware, facilities, hypervisor, managed-service infrastructure). You secure what's **in** the cloud (data, IAM, OS patching on EC2, network config, encryption choices).
**⚠️** The line shifts by service: you patch EC2's OS, but AWS patches Lambda's runtime host and RDS's OS.

### 🧩 KMS Key (formerly CMK)
**What:** A key in AWS KMS used to encrypt data or data keys. Types: **AWS owned**, **AWS managed** (`aws/s3`), **customer managed** (you control policy, rotation, deletion).
**⚠️** The **key policy** is the primary access control. Deleting a key (after the 7–30 day wait) makes its data unrecoverable.

### 🚀 Envelope Encryption
**What:** Data is encrypted with a **data key**, which is itself encrypted with a KMS key. Services store the encrypted data key alongside the data.
**Example:** S3 SSE-KMS, EBS encryption, and the KMS `GenerateDataKey` API.

### 🧩 Encryption at Rest Options (S3)
**What:** **SSE-S3** (AWS-managed keys, the default), **SSE-KMS** (KMS keys, audit trail, key policies), **DSSE-KMS** (dual layer), **SSE-C** (customer-provided keys), client-side encryption.
**⚠️** SSE-KMS adds KMS request costs/quotas. Enable **S3 Bucket Keys** to reduce them.

### 🧩 Secrets Manager vs Parameter Store
**What:** **Secrets Manager**: secrets with **automatic rotation** (RDS etc.), cross-account sharing, per-secret cost. **SSM Parameter Store**: config and secrets (SecureString via KMS), cheaper/free standard tier, no built-in rotation.

### 🧩 ACM (AWS Certificate Manager)
**What:** Free public TLS certificates (auto-renewed) for AWS integrated services (ALB, CloudFront, API Gateway), plus private CA.
**⚠️** Certificates for **CloudFront must be in `us-east-1`**.

### 🧩 WAF / Shield
**What:** **WAF**: layer-7 web application firewall rules (SQL injection, XSS, rate limiting, bot control) on CloudFront/ALB/API Gateway/AppSync/Cognito. **Shield Standard**: free DDoS protection. **Shield Advanced**: paid, with a DDoS response team and cost protection.

### 🧩 GuardDuty
**What:** Managed threat detection analysing CloudTrail, VPC Flow Logs, DNS logs, EKS/runtime and S3/malware signals.
**Example:** Alert: "EC2 instance communicating with a known crypto-mining domain".

### 🧩 Security Hub / Inspector / Macie / Detective
**What:** **Security Hub**: central findings + compliance checks (CIS, AWS Foundational Security Best Practices). **Inspector**: vulnerability scanning of EC2, ECR images and Lambda. **Macie**: finds sensitive data (PII) in S3. **Detective**: investigation graphs for security findings.

### 🌱 CloudTrail
**What:** Records **API calls** (who did what, when, from where) across your account.
**⚠️** Create an **organisation trail** to a locked-down central logging account, with log file validation. Attackers try to disable it first.

### 🧩 AWS Config
**What:** Records **resource configuration history** and evaluates compliance rules (e.g. "S3 buckets must block public access"), with auto-remediation.

---

# 10 — Monitoring, Management & IaC

### 🌱 CloudWatch Metrics / Alarms / Dashboards
**What:** **Metrics**: time-series data from AWS services and your apps (custom metrics). **Alarms**: thresholds/anomaly detection → SNS, Auto Scaling, EC2 actions. **Dashboards**: visual summaries.
**⚠️** Default EC2 metrics don't include **memory or disk usage**. Install the **CloudWatch agent**.

### 🌱 CloudWatch Logs / Log Group / Log Stream / Logs Insights
**What:** Central log storage. Log groups contain streams. **Logs Insights** is the query language. Metric filters turn log patterns into metrics.
**⚠️** Set **retention** on log groups. The default "never expire" quietly grows costs.

### 🧩 EventBridge Rule / Event Bus
**What:** Routes events (AWS service events, SaaS, custom) to targets by pattern matching. Also handles scheduled tasks (EventBridge Scheduler).
**Example:** "EC2 instance state → stopped in prod" triggers a Lambda that notifies Slack.

### 🧩 Systems Manager (SSM)
**What:** Operations hub: **Session Manager** (shell without SSH), **Run Command**, **Patch Manager**, **Parameter Store**, **Automation** runbooks, **Inventory**, **State Manager**, Fleet Manager.
**⚠️** Needs the SSM agent plus an instance role with `AmazonSSMManagedInstanceCore`, and network access to the SSM endpoints.

### 🧩 CloudFormation Stack / Template / Change Set / StackSets / Drift
**What:** AWS-native IaC. A **template** (YAML/JSON) is deployed as a **stack**. **Change sets** preview changes. **StackSets** deploy across many accounts/regions. **Drift detection** finds manual changes.
**⚠️** Watch the `Replacement: True` column in change sets: the resource will be **deleted and recreated**. Use `DeletionPolicy: Retain/Snapshot` for data. See [IaC pipelines](../cicd-pipelines/04-iac.md).

### 🧩 AWS CDK / SAM
**What:** **CDK**: write infrastructure in TypeScript/Python/Java/C#/Go, synthesised to CloudFormation. **SAM**: CloudFormation extension + CLI for serverless apps (`sam build/deploy/local invoke`).

### 🧩 Well-Architected Framework
**What:** AWS's best-practice framework with **6 pillars**: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability. The **Well-Architected Tool** runs reviews.

### 🧩 Trusted Advisor / Compute Optimizer
**What:** **Trusted Advisor**: checks for cost, security, fault tolerance, performance and service limits (full checks with Business+ support). **Compute Optimizer**: ML-based rightsizing recommendations for EC2, ASG, EBS, Lambda, ECS.

### 🧩 AWS Health Dashboard
**What:** Personalised view of AWS service events affecting **your** resources (and scheduled maintenance), integrated with EventBridge.

---

# 11 — Reliability, DR & Architecture

### 🌱 High Availability (Multi-AZ)
**What:** Spreading resources across AZs so one AZ failure doesn't cause an outage: ALB + ASG in 3 AZs, RDS Multi-AZ, EFS/S3/DynamoDB are multi-AZ by default.

### 🧩 Fault Isolation Boundaries
**What:** AWS designs failures to stay contained: **AZ** < **Region** < **Account**. Also control-plane vs data-plane separation.
**⚠️** Design for **static stability**: don't depend on control-plane APIs (launching instances) during recovery. Pre-provision capacity instead.

### 🧩 RPO / RTO
**What:** RPO = acceptable data loss (time). RTO = acceptable downtime.

### 🧩 DR Strategies on AWS
**What:**

| Strategy | Example on AWS | RTO / RPO |
|----------|----------------|-----------|
| Backup & Restore | AWS Backup cross-region copies; restore with IaC | Hours / hours |
| Pilot Light | Aurora Global DB replica + AMIs + IaC; compute off | 10s of minutes |
| Warm Standby | Scaled-down full stack running in a second region | Minutes |
| Multi-site Active/Active | Route 53 latency routing, DynamoDB Global Tables / Aurora DSQL | Near zero |

Tools: **AWS Backup**, **Elastic Disaster Recovery (DRS)**, Aurora Global Database, DynamoDB Global Tables, S3 CRR, Route 53 ARC (Application Recovery Controller).

### 🧩 Loose Coupling
**What:** Components communicate via queues/events (SQS, SNS, EventBridge), so failures and load spikes don't cascade.

### 🧩 Decoupled Retries: DLQ (Dead-Letter Queue)
**What:** Messages/events that repeatedly fail go to a DLQ for inspection and redrive (SQS, SNS, EventBridge, Lambda async).

### 🧩 Immutable Deployments / Blue-Green on AWS
**What:** Replace rather than modify: new ASG/AMI, new ECS task set, CodeDeploy blue/green, Lambda aliases with traffic shifting, Elastic Beanstalk immutable/blue-green.

### 🧩 Cell-Based Architecture / Shuffle Sharding
**What:** AWS's own patterns for limiting blast radius: many independent cells; customers assigned to random combinations of resources. See [Advanced DevOps terms](../devops-glossary/advanced-terms.md#cell-based-architecture).

---

# 12 — Cost & Pricing

### 🌱 Pay-as-you-go & Pricing Dimensions
**What:** AWS bills by usage dimensions: compute time, storage GB-month, requests, and **data transfer**.
**⚠️** **Data transfer OUT to the internet, cross-AZ and cross-region traffic** cost money, while inbound is generally free. NAT Gateway processing and public IPv4 addresses are frequent surprises.

### 🌱 AWS Budgets / Cost Explorer / Cost Anomaly Detection
**What:** **Budgets**: alerts when actual/forecast spend crosses thresholds (and budget actions). **Cost Explorer**: analyse spend by service/tag/account. **Anomaly Detection**: ML alerts on unusual spend.
**⚠️** Set a budget alert **the day you create an account**.

### 🧩 Cost and Usage Report (CUR) / Data Exports
**What:** The most detailed billing data, exported to S3 for Athena/QuickSight analysis.

### 🧩 Savings Plans vs Reserved Instances vs Spot
**What:** See [Purchasing Options](#-purchasing-options). Compute Savings Plans are the most flexible commitment. Spot is the cheapest, if interruption is acceptable.

### 🧩 Rightsizing & Graviton
**What:** Match instance sizes to real usage (Compute Optimizer). Move to Graviton for better price-performance.

### 🧩 Pricing Calculator
**What:** calculator.aws estimates the cost of an architecture before you build it.

### 🧩 Unit Cost / FinOps on AWS
**What:** Track cost per customer/transaction using tags + CUR. See [FinOps terms](../devops-glossary/advanced-terms.md#12--finops--cost-engineering).

---

**Next:** [02 — AWS Services: what & when ➡️](02-aws-services.md)

[⬅️ Back to AWS Index](README.md)
