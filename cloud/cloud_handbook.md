[🏠 Home](../README.md) · [Cloud](README.md)

# ☁️ Data Centers & Cloud Computing — Comprehensive DevOps/Cloud Handbook

> **Audience:** DevOps / Cloud Engineers & Trainees | **Focus:** Architecture, Services, Production Readiness  
> **Covers:** DC Architecture, Virtualization, IaaS/PaaS/SaaS, AWS/Azure/GCP, IaC, Containers, Serverless, HA/DR, FinOps  
> **Tip:** Sections build on each other — read sequentially first, then use TOC for reference.

---

## Table of Contents

1. [Why Cloud Computing Matters for DevOps](#1-why-cloud-computing-matters-for-devops)
2. [Data Center Architecture & Components](#2-data-center-architecture--components)
3. [Virtualization Fundamentals](#3-virtualization-fundamentals)
4. [Cloud Computing Models — IaaS, PaaS, SaaS](#4-cloud-computing-models--iaas-paas-saas)
5. [AWS / Azure / GCP — Core Services Comparison](#5-aws--azure--gcp--core-services-comparison)
6. [Compute Services](#6-compute-services)
7. [Storage Services](#7-storage-services)
8. [Cloud Networking](#8-cloud-networking)
9. [Identity & Access Management (IAM)](#9-identity--access-management-iam)
10. [Serverless Computing](#10-serverless-computing)
11. [Containers & Orchestration in the Cloud](#11-containers--orchestration-in-the-cloud)
12. [Infrastructure as Code (IaC)](#12-infrastructure-as-code-iac)
13. [CI/CD in the Cloud](#13-cicd-in-the-cloud)
14. [Monitoring & Observability](#14-monitoring--observability)
15. [High Availability & Disaster Recovery](#15-high-availability--disaster-recovery)
16. [Cost Optimization & FinOps](#16-cost-optimization--finops)
17. [Security & Compliance](#17-security--compliance)
18. [Production Gotchas & Scenario-Based FAQ](#18-production-gotchas--scenario-based-faq)

---

## 1. Why Cloud Computing Matters for DevOps

### 1.1 The Shift from Data Centers to Cloud

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  EVOLUTION OF INFRASTRUCTURE                                    │
  │                                                                 │
  │  Era 1: Physical Servers (1990s-2000s)                         │
  │  ├── Buy servers, rack & stack in colo                         │
  │  ├── Weeks to provision new capacity                           │
  │  └── 10-20% average utilization                                │
  │                                                                 │
  │  Era 2: Virtualization (2000s-2010s)                           │
  │  ├── VMware, Hyper-V, KVM                                     │
  │  ├── Multiple VMs per physical host                            │
  │  ├── Hours to provision, 40-60% utilization                    │
  │  └── Private cloud (OpenStack, vSphere)                        │
  │                                                                 │
  │  Era 3: Public Cloud (2006-present)                            │
  │  ├── AWS EC2 launched 2006, Azure 2010, GCP 2011              │
  │  ├── Minutes to provision, pay-per-use                         │
  │  ├── Global infrastructure as an API                           │
  │  └── 60-80% utilization with auto-scaling                      │
  │                                                                 │
  │  Era 4: Cloud-Native (2014-present)                            │
  │  ├── Containers (Docker), orchestration (Kubernetes)           │
  │  ├── Serverless (Lambda), managed services                     │
  │  ├── Seconds to provision, extreme elasticity                  │
  │  └── Infrastructure as Code, GitOps                            │
  └─────────────────────────────────────────────────────────────────┘
```

### 1.2 What You'll Be Able to Do

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  CLOUD COMPETENCY PROGRESSION                                   │
  │                                                                 │
  │  BEGINNER (Sections 1–5)                                        │
  │  ├── Explain DC architecture and tier classifications           │
  │  ├── Understand hypervisor types and VM lifecycle               │
  │  ├── Differentiate IaaS / PaaS / SaaS with examples            │
  │  └── Map equivalent services across AWS / Azure / GCP          │
  │                                                                 │
  │  INTERMEDIATE (Sections 6–11)                                   │
  │  ├── Provision and manage cloud compute, storage, networking    │
  │  ├── Design IAM policies with least privilege                   │
  │  ├── Deploy serverless functions and understand cold starts     │
  │  ├── Run containers on ECS/EKS/AKS/GKE                        │
  │  └── Understand cloud networking (VPC, subnets, peering)       │
  │                                                                 │
  │  ADVANCED (Sections 12–18)                                      │
  │  ├── Write IaC with Terraform / CloudFormation                  │
  │  ├── Build CI/CD pipelines on cloud-native services             │
  │  ├── Design HA / DR architectures with RTO/RPO targets         │
  │  ├── Optimize cloud costs and implement FinOps practices       │
  │  └── Handle production scenarios with confidence               │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Center Architecture & Components

### 2.1 Physical Layout — From Building to Rack

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  DATA CENTER — PHYSICAL HIERARCHY                                    │
  │                                                                      │
  │  Building / Facility                                                 │
  │  ├── Floor / Data Hall                                               │
  │  │   ├── Row (Hot Aisle / Cold Aisle arrangement)                    │
  │  │   │   ├── Cabinet / Rack (42U standard)                           │
  │  │   │   │   ├── Server (1U, 2U, 4U)                                │
  │  │   │   │   │   ├── CPU, RAM, NIC, HBA                             │
  │  │   │   │   │   └── Local storage (SSD/NVMe)                       │
  │  │   │   │   ├── Network switch (Top-of-Rack / ToR)                 │
  │  │   │   │   ├── Storage array (SAN/NAS)                            │
  │  │   │   │   └── Patch panels, cable management                     │
  │  │   │   └── PDU (Power Distribution Unit)                          │
  │  │   └── Core/Aggregation switches                                  │
  │  ├── UPS (Uninterruptible Power Supply) Room                        │
  │  ├── Generator Room (diesel/gas backup)                             │
  │  ├── Cooling Plant (CRAC/CRAH units, chillers)                      │
  │  ├── Meet-Me Room (ISP connections, cross-connects)                 │
  │  └── NOC (Network Operations Center)                                │
  └──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Hot Aisle / Cold Aisle Cooling

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  COOLING — HOT AISLE / COLD AISLE LAYOUT                        │
  │                                                                  │
  │  Cold air from under raised floor → through server → hot exhaust │
  │                                                                  │
  │         COLD AISLE          HOT AISLE         COLD AISLE        │
  │  ┌─────┐  ↑  ┌─────┐  ┌─────┐  ↑  ┌─────┐  ┌─────┐  ↑       │
  │  │     │  │  │     │  │     │  │  │     │  │     │  │        │
  │  │ Rack│←─┤  │ Rack│  │ Rack│──┤  │ Rack│  │ Rack│←─┤        │
  │  │  A  │  │  │  B  │  │  C  │  │  │  D  │  │  E  │  │        │
  │  │     │  │  │     │  │     │  │  │     │  │     │  │        │
  │  │front│  │  │front│  │back │  │  │back │  │front│  │        │
  │  └─────┘  │  └─────┘  └─────┘  │  └─────┘  └─────┘  │        │
  │           │                     │                     │        │
  │     Cold air rises         Hot air rises         Cold air      │
  │     from floor             to ceiling            from floor    │
  │     (perforated tiles)     (return to CRAC)      (perf tiles)  │
  │                                                                  │
  │  Temperature targets:                                            │
  │  Cold aisle inlet: 18-27°C (64-80°F) — ASHRAE recommended      │
  │  Hot aisle exhaust: 35-45°C (95-113°F)                          │
  └──────────────────────────────────────────────────────────────────┘
```

### 2.3 Data Center Tiers (Uptime Institute)

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DC TIER CLASSIFICATION                                          │
  │                                                                  │
  │  Tier │ Uptime    │ Downtime/yr │ Redundancy        │ Cost      │
  │  ─────┼───────────┼─────────────┼───────────────────┼────────   │
  │  I    │ 99.671%   │ 28.8 hrs    │ None (N)          │ $         │
  │       │           │             │ Single path        │           │
  │  ─────┼───────────┼─────────────┼───────────────────┼────────   │
  │  II   │ 99.741%   │ 22.7 hrs    │ Partial (N+1)     │ $$        │
  │       │           │             │ Redundant cooling  │           │
  │  ─────┼───────────┼─────────────┼───────────────────┼────────   │
  │  III  │ 99.982%   │ 1.6 hrs     │ Full (N+1)        │ $$$       │
  │       │           │             │ Dual power paths   │           │
  │       │           │             │ Concurrently       │           │
  │       │           │             │ maintainable       │           │
  │  ─────┼───────────┼─────────────┼───────────────────┼────────   │
  │  IV   │ 99.995%   │ 0.4 hrs     │ Full (2N or 2N+1) │ $$$$      │
  │       │           │             │ Fault tolerant     │           │
  │       │           │             │ Dual everything    │           │
  └──────────────────────────────────────────────────────────────────┘
  
  Cloud providers operate Tier III-IV equivalent facilities.
  AWS has 100+ data centers across 30+ regions.
```

### 2.4 Power & Redundancy

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  POWER DELIVERY CHAIN                                            │
  │                                                                  │
  │  Utility Power (Grid)                                            │
  │       │                                                          │
  │       ▼                                                          │
  │  Transformer (step down voltage)                                 │
  │       │                                                          │
  │       ▼                                                          │
  │  Automatic Transfer Switch (ATS) ←── Generator (backup)         │
  │       │                              (starts in 10-15 seconds)  │
  │       ▼                                                          │
  │  UPS (Uninterruptible Power Supply)                              │
  │  (battery bridge — covers the 10-15s gap)                       │
  │       │                                                          │
  │       ▼                                                          │
  │  PDU (Power Distribution Unit)                                   │
  │       │                                                          │
  │       ▼                                                          │
  │  Server PSU (often dual — A+B feeds)                             │
  │                                                                  │
  │  PUE (Power Usage Effectiveness):                                │
  │  = Total Facility Power / IT Equipment Power                     │
  │  • Ideal: 1.0 (impossible)                                      │
  │  • Good:  1.2-1.4                                                │
  │  • Average: 1.5-2.0                                              │
  │  • Google: ~1.10  |  AWS: ~1.20                                  │
  └──────────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** Understanding DC architecture helps you appreciate why cloud regions have multiple Availability Zones (AZs) — each AZ is one or more physically separate data centers with independent power, cooling, and networking.

---

## 3. Virtualization Fundamentals

### 3.1 What Is Virtualization?

Virtualization creates **virtual versions of physical resources** (servers, storage, networks) using software called a **hypervisor**.

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  BARE METAL vs VIRTUALIZED                                       │
  │                                                                  │
  │  Without Virtualization:         With Virtualization:            │
  │  ┌──────────────────┐           ┌──────────────────────────┐    │
  │  │    Application    │           │  VM1    VM2    VM3       │    │
  │  │    Operating      │           │  ┌───┐  ┌───┐  ┌───┐    │    │
  │  │    System         │           │  │App│  │App│  │App│    │    │
  │  │                   │           │  │OS │  │OS │  │OS │    │    │
  │  │                   │           │  └───┘  └───┘  └───┘    │    │
  │  │                   │           │  ┌──────────────────┐    │    │
  │  │                   │           │  │   Hypervisor     │    │    │
  │  ├──────────────────┤           ├──┴──────────────────┴──┤    │
  │  │   Physical HW     │           │   Physical Hardware    │    │
  │  └──────────────────┘           └────────────────────────┘    │
  │                                                                  │
  │  1 OS per server                 Multiple VMs per server        │
  │  10-20% utilization              60-80% utilization             │
  └──────────────────────────────────────────────────────────────────┘
```

### 3.2 Hypervisor Types

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  TYPE 1 (Bare Metal):              TYPE 2 (Hosted):             │
  │  Runs directly on hardware          Runs on top of an OS        │
  │                                                                  │
  │  ┌───────────────────────┐         ┌───────────────────────┐    │
  │  │  VM1    VM2    VM3    │         │  VM1    VM2           │    │
  │  │  ┌──┐  ┌──┐  ┌──┐    │         │  ┌──┐  ┌──┐          │    │
  │  │  │OS│  │OS│  │OS│    │         │  │OS│  │OS│          │    │
  │  │  └──┘  └──┘  └──┘    │         │  └──┘  └──┘          │    │
  │  ├───────────────────────┤         ├──────────────────────┤    │
  │  │  Hypervisor (Type 1)  │         │  Hypervisor (Type 2) │    │
  │  ├───────────────────────┤         ├──────────────────────┤    │
  │  │  Hardware             │         │  Host OS (Windows/   │    │
  │  └───────────────────────┘         │   macOS/Linux)       │    │
  │                                    ├──────────────────────┤    │
  │  Examples:                          │  Hardware             │    │
  │  • VMware ESXi                     └──────────────────────┘    │
  │  • Microsoft Hyper-V                                            │
  │  • KVM (Linux)                     Examples:                    │
  │  • Xen (AWS uses Nitro/Xen)       • VirtualBox                 │
  │  • Citrix Hypervisor               • VMware Workstation         │
  │                                    • Parallels (Mac)            │
  │  ✅ Better performance             ❌ More overhead             │
  │  ✅ Production workloads           ✅ Development/testing       │
  └──────────────────────────────────────────────────────────────────┘
```

### 3.3 VMs vs Containers

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VIRTUAL MACHINES vs CONTAINERS                                  │
  │                                                                  │
  │  Virtual Machine:                   Container:                   │
  │  ┌───────────────────────┐         ┌───────────────────────┐    │
  │  │ App A  │ App B  │ App C│         │ App A │ App B │ App C │    │
  │  ├────────┼────────┼──────┤         │ Libs  │ Libs  │ Libs  │    │
  │  │ Guest  │ Guest  │Guest │         ├───────┴───────┴───────┤    │
  │  │ OS     │ OS     │OS    │         │  Container Runtime     │    │
  │  │(Ubuntu)│(CentOS)│(Win) │         │  (Docker/containerd)   │    │
  │  ├────────┴────────┴──────┤         ├───────────────────────┤    │
  │  │ Hypervisor              │         │  Host OS (Linux)       │    │
  │  ├─────────────────────────┤         ├───────────────────────┤    │
  │  │ Host Hardware            │         │  Host Hardware         │    │
  │  └─────────────────────────┘         └───────────────────────┘    │
  │                                                                  │
  │  ┌────────────────┬──────────────────┬──────────────────┐        │
  │  │ Feature        │ VM                │ Container        │        │
  │  ├────────────────┼──────────────────┼──────────────────┤        │
  │  │ Isolation      │ Strong (HW-level) │ Process-level    │        │
  │  │ Boot time      │ Minutes           │ Seconds          │        │
  │  │ Size           │ GBs               │ MBs              │        │
  │  │ OS             │ Any (Linux/Win)   │ Shares host OS   │        │
  │  │ Density        │ 10s per host      │ 100s per host    │        │
  │  │ Overhead       │ High (full OS)    │ Minimal          │        │
  │  │ Use case       │ Legacy apps,      │ Microservices,   │        │
  │  │                │ multi-OS,         │ CI/CD, modern    │        │
  │  │                │ strong isolation   │ cloud-native     │        │
  │  └────────────────┴──────────────────┴──────────────────┘        │
  └──────────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** Cloud EC2/Azure VM instances are VMs running on Type 1 hypervisors. When you "launch an instance," you're creating a VM. Containers (ECS, EKS, AKS) run inside those VMs. Understanding this stack matters for performance tuning and troubleshooting.

---

## 4. Cloud Computing Models — IaaS, PaaS, SaaS

### 4.1 The Cloud Service Models

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CLOUD SERVICE MODELS — WHO MANAGES WHAT                             │
  │                                                                      │
  │                On-Prem    IaaS       PaaS       SaaS                 │
  │  ┌──────────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
  │  │Application│  │ YOU  │  │ YOU  │  │ YOU  │  │VENDOR│              │
  │  │Data       │  │ YOU  │  │ YOU  │  │ YOU  │  │VENDOR│              │
  │  │Runtime    │  │ YOU  │  │ YOU  │  │VENDOR│  │VENDOR│              │
  │  │Middleware │  │ YOU  │  │ YOU  │  │VENDOR│  │VENDOR│              │
  │  │OS         │  │ YOU  │  │ YOU  │  │VENDOR│  │VENDOR│              │
  │  │Virtualizn │  │ YOU  │  │VENDOR│  │VENDOR│  │VENDOR│              │
  │  │Servers    │  │ YOU  │  │VENDOR│  │VENDOR│  │VENDOR│              │
  │  │Storage    │  │ YOU  │  │VENDOR│  │VENDOR│  │VENDOR│              │
  │  │Networking │  │ YOU  │  │VENDOR│  │VENDOR│  │VENDOR│              │
  │  └──────────┘  └──────┘  └──────┘  └──────┘  └──────┘              │
  │                                                                      │
  │  IaaS Examples:      PaaS Examples:       SaaS Examples:            │
  │  • EC2, Azure VM     • AWS Elastic        • Gmail, Office 365      │
  │  • GCE               •   Beanstalk        • Salesforce             │
  │  • DigitalOcean      • Azure App Service  • Slack, Zoom            │
  │  • S3, EBS           • Google App Engine  • Datadog (SaaS)        │
  │  • VPC, VNet         • Heroku             • GitHub, GitLab        │
  └──────────────────────────────────────────────────────────────────────┘
```

### 4.2 Beyond the Big Three: XaaS

| Model | Description | Examples |
|-------|-------------|---------|
| **FaaS** | Functions as a Service (serverless) | Lambda, Azure Functions, Cloud Run |
| **CaaS** | Containers as a Service | ECS, AKS, GKE, Fargate |
| **DBaaS** | Database as a Service | RDS, CosmosDB, Cloud SQL |
| **BaaS** | Backend as a Service | Firebase, AWS Amplify |
| **DaaS** | Desktop as a Service | Amazon WorkSpaces, Azure Virtual Desktop |

### 4.3 Cloud Deployment Models

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DEPLOYMENT MODELS                                               │
  │                                                                  │
  │  Public Cloud:        Private Cloud:       Hybrid Cloud:         │
  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐     │
  │  │ AWS / Azure /  │  │ On-premises    │  │  On-prem  +    │     │
  │  │ GCP            │  │ OpenStack,     │  │  Public Cloud  │     │
  │  │                │  │ VMware vCloud  │  │  connected via │     │
  │  │ Shared infra,  │  │                │  │  VPN / Direct  │     │
  │  │ multi-tenant   │  │ Dedicated,     │  │  Connect       │     │
  │  │                │  │ single-tenant  │  │                │     │
  │  │ ✅ Scalable    │  │ ✅ Full control│  │ ✅ Flexibility │     │
  │  │ ✅ Pay-per-use │  │ ✅ Compliance  │  │ ✅ Keep        │     │
  │  │ ❌ Less control│  │ ❌ High CapEx  │  │   sensitive    │     │
  │  │               │  │ ❌ Slower scale│  │   data on-prem │     │
  │  └────────────────┘  └────────────────┘  └────────────────┘     │
  │                                                                  │
  │  Multi-Cloud: Using 2+ public clouds (AWS + Azure) to avoid    │
  │  vendor lock-in. Complex but increasingly common.              │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 5. AWS / Azure / GCP — Core Services Comparison

### 5.1 The Rosetta Stone — Service Mapping

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │  CLOUD SERVICES COMPARISON — "Rosetta Stone"                          │
  │                                                                        │
  │  Category        │ AWS               │ Azure              │ GCP        │
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  COMPUTE                                                               │
  │  VMs             │ EC2               │ Virtual Machines   │ Compute    │
  │                  │                   │                    │ Engine     │
  │  Containers      │ ECS / EKS         │ AKS / ACI          │ GKE / CR   │
  │  Serverless      │ Lambda            │ Functions          │ Cloud      │
  │                  │                   │                    │ Functions  │
  │  Serverless      │ Fargate           │ Container Apps     │ Cloud Run  │
  │  Containers      │                   │                    │            │
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  STORAGE                                                               │
  │  Object          │ S3                │ Blob Storage       │ Cloud      │
  │                  │                   │                    │ Storage    │
  │  Block           │ EBS               │ Managed Disks      │ Persistent │
  │                  │                   │                    │ Disk       │
  │  File            │ EFS               │ Azure Files        │ Filestore  │
  │  Archive         │ S3 Glacier        │ Archive Storage    │ Archive    │
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  DATABASE                                                              │
  │  Relational      │ RDS / Aurora      │ Azure SQL / MySQL  │ Cloud SQL  │
  │                  │                   │   / PostgreSQL     │ / AlloyDB  │
  │  NoSQL (Doc)     │ DynamoDB          │ Cosmos DB          │ Firestore  │
  │  NoSQL (KV)      │ ElastiCache       │ Azure Cache        │ Memorystore│
  │  Data Warehouse  │ Redshift          │ Synapse Analytics  │ BigQuery   │
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  NETWORKING                                                            │
  │  VPC             │ VPC               │ VNet               │ VPC        │
  │  CDN             │ CloudFront        │ Azure CDN / FD     │ Cloud CDN  │
  │  DNS             │ Route 53          │ Azure DNS          │ Cloud DNS  │
  │  LB (L7)        │ ALB               │ App Gateway        │ HTTP(S) LB │
  │  LB (L4)        │ NLB               │ Azure Load Bal.    │ TCP/UDP LB │
  │  Private Link    │ PrivateLink       │ Private Link       │ Private    │
  │                  │                   │                    │ Service Con│
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  SECURITY                                                              │
  │  IAM             │ IAM               │ Entra ID (AAD)     │ Cloud IAM  │
  │  Secrets         │ Secrets Manager   │ Key Vault          │ Secret Mgr │
  │  Firewall (host) │ Security Groups   │ NSGs               │ Firewall   │
  │                  │                   │                    │ Rules      │
  │  WAF             │ AWS WAF           │ Azure WAF          │ Cloud Armor│
  │  ────────────────┼───────────────────┼────────────────────┼──────────  │
  │  DEVOPS                                                                │
  │  CI/CD           │ CodePipeline      │ Azure DevOps       │ Cloud Build│
  │  IaC             │ CloudFormation    │ ARM / Bicep        │ Deployment │
  │                  │                   │                    │ Manager    │
  │  Monitoring      │ CloudWatch        │ Azure Monitor      │ Cloud      │
  │                  │                   │                    │ Monitoring │
  │  Logging         │ CloudWatch Logs   │ Log Analytics      │ Cloud      │
  │                  │                   │                    │ Logging    │
  │  Container Reg.  │ ECR               │ ACR                │ Artifact   │
  │                  │                   │                    │ Registry   │
  └────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Regions & Availability Zones

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  REGIONS & AVAILABILITY ZONES                                    │
  │                                                                  │
  │  Region = Geographic location (e.g., us-east-1, westeurope)     │
  │  AZ = Isolated data center(s) within a region                   │
  │                                                                  │
  │  ┌─ Region: us-east-1 (N. Virginia) ────────────────────────┐   │
  │  │                                                           │   │
  │  │  ┌── AZ: us-east-1a ──┐  ┌── AZ: us-east-1b ──┐        │   │
  │  │  │ Data Center(s)     │  │ Data Center(s)     │        │   │
  │  │  │ Independent power  │  │ Independent power  │        │   │
  │  │  │ Independent cooling│  │ Independent cooling│        │   │
  │  │  │ Independent network│  │ Independent network│        │   │
  │  │  └────────────────────┘  └────────────────────┘        │   │
  │  │           │                        │                    │   │
  │  │           └── Low-latency link ────┘                    │   │
  │  │               (< 2ms between AZs)                       │   │
  │  │                                                           │   │
  │  │  ┌── AZ: us-east-1c ──┐  ┌── AZ: us-east-1d ──┐        │   │
  │  │  │ Data Center(s)     │  │ Data Center(s)     │        │   │
  │  │  └────────────────────┘  └────────────────────┘        │   │
  │  └───────────────────────────────────────────────────────────┘   │
  │                                                                  │
  │  AWS:   30+ regions, 90+ AZs                                    │
  │  Azure: 60+ regions, paired regions for DR                      │
  │  GCP:   35+ regions, zones (similar to AZs)                     │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha:** AZ names are **randomized per account**. Your `us-east-1a` might be different physical DC than another account's `us-east-1a`. Use AZ IDs (e.g., `use1-az1`) for cross-account coordination.

---

## 6. Compute Services

### 6.1 EC2 / Azure VM / GCE — Instance Types

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  AWS EC2 INSTANCE FAMILIES (applies conceptually to all clouds)  │
  │                                                                  │
  │  Family │ Optimized For       │ Example Type  │ Use Case         │
  │  ───────┼─────────────────────┼───────────────┼────────────────  │
  │  t3/t4g │ General (burstable) │ t3.medium     │ Dev, small apps  │
  │  m6i/m7g│ General (steady)    │ m6i.xlarge    │ Web servers, app │
  │  c6i/c7g│ Compute optimized   │ c6i.2xlarge   │ Batch, HPC, CI   │
  │  r6i/r7g│ Memory optimized    │ r6i.4xlarge   │ Databases, cache │
  │  i3/i4i │ Storage optimized   │ i3.2xlarge    │ NoSQL, data lake │
  │  p4/p5  │ GPU (accelerated)   │ p4d.24xlarge  │ ML training      │
  │  g5     │ GPU (graphics)      │ g5.xlarge     │ ML inference     │
  │                                                                  │
  │  Naming: m6i.xlarge                                              │
  │          │││ └── Size (nano → metal)                             │
  │          ││└──── Processor (i=Intel, g=Graviton/ARM, a=AMD)     │
  │          │└───── Generation (6th gen)                            │
  │          └────── Family (m=general)                              │
  │                                                                  │
  │  ARM (Graviton) instances: ~20% cheaper, ~20% better perf      │
  │  for most workloads. Use unless you need x86 compatibility.    │
  └──────────────────────────────────────────────────────────────────┘
```

### 6.2 Pricing Models

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD COMPUTE PRICING — LOWEST TO HIGHEST                      │
  │                                                                  │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ Spot Instances (AWS) / Preemptible (GCP)                │    │
  │  │ 60-90% discount  |  Can be terminated with 2-min notice │    │
  │  │ Use for: Batch jobs, CI/CD runners, fault-tolerant work │    │
  │  └─────────────────────────────────────────────────────────┘    │
  │                       ▲                                         │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ Reserved Instances / Savings Plans / Committed Use      │    │
  │  │ 30-72% discount  |  1 or 3 year commitment              │    │
  │  │ Use for: Steady-state production workloads              │    │
  │  └─────────────────────────────────────────────────────────┘    │
  │                       ▲                                         │
  │  ┌─────────────────────────────────────────────────────────┐    │
  │  │ On-Demand                                                │    │
  │  │ Full price  |  No commitment  |  Pay by the second      │    │
  │  │ Use for: Unpredictable workloads, short-term spikes     │    │
  │  └─────────────────────────────────────────────────────────┘    │
  │                                                                  │
  │  Cost optimization strategy:                                    │
  │  Reserved (base load) + On-Demand (spikes) + Spot (batch)     │
  └──────────────────────────────────────────────────────────────────┘
```

### 6.3 Auto Scaling

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  AUTO SCALING — DYNAMIC CAPACITY MANAGEMENT                      │
  │                                                                  │
  │  Capacity                                                        │
  │  ▲                                                               │
  │  │     ┌──────┐                                                  │
  │  │     │      │  ← Max capacity (e.g., 10 instances)            │
  │  │  ┌──┘      │                                                  │
  │  │  │   Auto  └──┐                                               │
  │  │  │  Scaled    │    ← Actual demand                           │
  │  │  │  Capacity  └──┐                                            │
  │  ├──┘               └──┐                                         │
  │  │                     └──┐                                      │
  │  │  ← Min capacity (e.g., 2 instances)                          │
  │  └──────────────────────────────────────────────────────────────►│
  │                       Time                                       │
  │                                                                  │
  │  Scaling Policies:                                               │
  │  ├── Target Tracking: "Keep CPU at 70%"                         │
  │  ├── Step Scaling: "Add 2 if CPU > 80%, add 4 if > 90%"       │
  │  ├── Scheduled: "Scale to 10 at 9am, 2 at midnight"           │
  │  └── Predictive: ML-based, pre-scales before demand spikes     │
  │                                                                  │
  │  AWS: Auto Scaling Groups (ASG)                                 │
  │  Azure: Virtual Machine Scale Sets (VMSS)                       │
  │  GCP: Managed Instance Groups (MIG)                             │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha (Auto Scaling):** Scale-out is fast (minutes), but scale-in should be slow. If you scale in too aggressively, you'll thrash (scale out, scale in, scale out...). Set a cooldown period (300s minimum) and scale in conservatively.

---

## 7. Storage Services

### 7.1 Storage Types

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD STORAGE TYPES                                             │
  │                                                                  │
  │  Object Storage (S3 / Blob / GCS):                              │
  │  ┌─────────────────────────────────────────────────────┐        │
  │  │  key: "images/photo.jpg"                             │        │
  │  │  value: <binary data>                                │        │
  │  │  metadata: {content-type, custom-headers}            │        │
  │  │                                                      │        │
  │  │  Flat namespace (no directories — just key prefixes)│        │
  │  │  Unlimited storage, 11 nines durability (S3)        │        │
  │  │  Access: REST API (PUT/GET/DELETE)                   │        │
  │  │  Use for: Backups, static assets, data lake, logs   │        │
  │  └─────────────────────────────────────────────────────┘        │
  │                                                                  │
  │  Block Storage (EBS / Managed Disk / Persistent Disk):          │
  │  ┌─────────────────────────────────────────────────────┐        │
  │  │  Like a raw disk — attach to ONE instance                    │
  │  │  ┌────┬────┬────┬────┬────┬────┐                    │        │
  │  │  │Blk │Blk │Blk │Blk │Blk │Blk │   Fixed blocks   │        │
  │  │  │ 0  │ 1  │ 2  │ 3  │ 4  │ 5  │                   │        │
  │  │  └────┴────┴────┴────┴────┴────┘                    │        │
  │  │  Formatted with filesystem (ext4, xfs)              │        │
  │  │  Use for: OS root volumes, databases                │        │
  │  └─────────────────────────────────────────────────────┘        │
  │                                                                  │
  │  File Storage (EFS / Azure Files / Filestore):                  │
  │  ┌─────────────────────────────────────────────────────┐        │
  │  │  NFS/SMB share — mount on MANY instances            │        │
  │  │  /shared/                                            │        │
  │  │  ├── config/                                         │        │
  │  │  ├── logs/                                           │        │
  │  │  └── data/                                           │        │
  │  │  Use for: Shared data, CMS content, home dirs       │        │
  │  └─────────────────────────────────────────────────────┘        │
  └──────────────────────────────────────────────────────────────────┘
```

### 7.2 S3 Storage Classes

| Class | Retrieval | Cost | Use Case |
|-------|-----------|------|----------|
| **S3 Standard** | Instant | $$$ | Frequently accessed data |
| **S3 Intelligent-Tiering** | Instant | $-$$$ | Unknown access patterns |
| **S3 Standard-IA** | Instant | $$ | Infrequent but needs fast access |
| **S3 One Zone-IA** | Instant | $ | Recreatable infrequent data |
| **S3 Glacier Instant** | Instant | $ | Archival with instant access |
| **S3 Glacier Flexible** | Minutes-hours | ¢ | Archival (5-12 hr retrieval) |
| **S3 Glacier Deep Archive** | 12-48 hours | ¢¢ | Long-term archive |

### 7.3 Choosing Storage — Decision Tree

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  STORAGE SELECTION DECISION TREE                                 │
  │                                                                  │
  │  What kind of data?                                              │
  │  │                                                               │
  │  ├── Unstructured (images, videos, backups, logs)?              │
  │  │   └── Object Storage (S3, Blob, GCS)                         │
  │  │                                                               │
  │  ├── Database / high IOPS / single instance?                    │
  │  │   └── Block Storage (EBS, Managed Disk)                      │
  │  │       ├── gp3 / Standard SSD: General purpose               │
  │  │       ├── io2 / Premium SSD: High IOPS (databases)          │
  │  │       └── st1 / Standard HDD: Throughput (big data)         │
  │  │                                                               │
  │  ├── Shared filesystem across multiple instances?               │
  │  │   └── File Storage (EFS, Azure Files)                        │
  │  │                                                               │
  │  └── Archival / compliance (rarely accessed)?                   │
  │      └── Glacier / Archive tier                                  │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 8. Cloud Networking

### 8.1 VPC Deep Dive

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  VPC BUILDING BLOCKS                                                 │
  │                                                                      │
  │  1. VPC (10.0.0.0/16) — Your isolated virtual network              │
  │  2. Subnets — Subdivisions within AZs                               │
  │  3. Route Tables — Traffic routing rules                            │
  │  4. Internet Gateway (IGW) — VPC-to-internet bridge                │
  │  5. NAT Gateway — Private subnet → internet (outbound only)        │
  │  6. Security Groups — Instance-level firewall (stateful)           │
  │  7. NACLs — Subnet-level firewall (stateless)                     │
  │  8. VPC Endpoints — Private access to AWS services                 │
  │  9. Peering / Transit Gateway — VPC-to-VPC connectivity            │
  │                                                                      │
  │  TRAFFIC FLOW — Private instance reaching S3:                       │
  │                                                                      │
  │  EC2 (10.0.3.5) → Route Table → VPC Endpoint (Gateway)             │
  │       │                              │                               │
  │       └──── stays within AWS ────────┘                               │
  │            (never touches internet)                                  │
  │                                                                      │
  │  Without endpoint:                                                   │
  │  EC2 → NAT Gateway → IGW → Internet → S3 (public endpoint)        │
  │  (slower, costs more in data transfer)                              │
  └──────────────────────────────────────────────────────────────────────┘
```

### 8.2 VPC Design Patterns

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  PATTERN 1: Single VPC (Small Teams)                             │
  │                                                                  │
  │  VPC: 10.0.0.0/16                                               │
  │  ├── Public:  10.0.1.0/24, 10.0.2.0/24  (AZ-a, AZ-b)         │
  │  ├── Private: 10.0.3.0/24, 10.0.4.0/24  (apps)                │
  │  └── Data:    10.0.5.0/24, 10.0.6.0/24  (databases)           │
  │                                                                  │
  │  PATTERN 2: Hub-and-Spoke (Enterprise)                          │
  │                                                                  │
  │  ┌──────────┐                                                    │
  │  │ Shared   │ (DNS, monitoring, bastion)                        │
  │  │ Services │                                                    │
  │  └────┬─────┘                                                    │
  │       │ Transit Gateway                                          │
  │  ┌────┼────────────┐                                             │
  │  │    │            │                                             │
  │  ▼    ▼            ▼                                             │
  │  Prod  Staging     Dev                                           │
  │  VPC   VPC         VPC                                           │
  │                                                                  │
  │  PATTERN 3: Multi-Account (AWS Organizations)                   │
  │                                                                  │
  │  Account per environment (dev, staging, prod)                   │
  │  + Shared networking account with Transit Gateway               │
  │  + Security account with centralized logging                    │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha (CIDR Planning):** Plan your CIDR ranges BEFORE creating VPCs. Overlapping CIDRs cannot be peered. Use a CIDR allocation spreadsheet. Typical: 10.{env}.0.0/16 where env = 0 (prod), 1 (staging), 2 (dev).

---

## 9. Identity & Access Management (IAM)

### 9.1 IAM Core Concepts

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  IAM — WHO CAN DO WHAT ON WHICH RESOURCES                       │
  │                                                                  │
  │  Principal (WHO)  +  Action (WHAT)  +  Resource (WHERE)          │
  │       │                  │                  │                     │
  │  ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────────────┐      │
  │  │ User     │      │ s3:Get   │      │ arn:aws:s3:::    │      │
  │  │ Role     │      │ Object   │      │ my-bucket/*      │      │
  │  │ Group    │      │          │      │                   │      │
  │  │ Service  │      │ ec2:Run  │      │ arn:aws:ec2:     │      │
  │  └──────────┘      │ Instances│      │ us-east-1:*      │      │
  │                     └──────────┘      └─────────────────┘      │
  │                                                                  │
  │  Policy Example (JSON):                                         │
  │  {                                                               │
  │    "Effect": "Allow",                                            │
  │    "Action": ["s3:GetObject", "s3:PutObject"],                  │
  │    "Resource": "arn:aws:s3:::my-bucket/*",                      │
  │    "Condition": {                                                │
  │      "IpAddress": {"aws:SourceIp": "10.0.0.0/8"}               │
  │    }                                                             │
  │  }                                                               │
  └──────────────────────────────────────────────────────────────────┘
```

### 9.2 IAM Best Practices

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  IAM SECURITY CHECKLIST                                          │
  │                                                                  │
  │  ✅ PRINCIPLE OF LEAST PRIVILEGE                                 │
  │     Grant only the permissions needed, nothing more              │
  │                                                                  │
  │  ✅ USE ROLES, NOT LONG-LIVED CREDENTIALS                       │
  │     EC2 → Instance role (not access keys in code!)              │
  │     Lambda → Execution role                                     │
  │     EKS pods → IRSA (IAM Roles for Service Accounts)           │
  │                                                                  │
  │  ✅ ENABLE MFA EVERYWHERE                                       │
  │     Root account: hardware MFA                                  │
  │     IAM users: virtual MFA (Authenticator app)                  │
  │     Require MFA for sensitive actions (Condition: MFA)          │
  │                                                                  │
  │  ✅ DON'T USE ROOT ACCOUNT                                      │
  │     Create IAM users/roles for all operations                   │
  │     Lock root away, only for billing/account ops                │
  │                                                                  │
  │  ✅ ROTATE CREDENTIALS                                          │
  │     Access keys: rotate every 90 days (or eliminate)            │
  │     Use temporary credentials (STS AssumeRole)                  │
  │                                                                  │
  │  ✅ USE PERMISSION BOUNDARIES                                   │
  │     Set maximum permission level for delegated admins           │
  │                                                                  │
  │  ❌ NEVER hardcode credentials in source code                   │
  │  ❌ NEVER use wildcard (*) on actions AND resources             │
  │  ❌ NEVER share accounts between people                        │
  └──────────────────────────────────────────────────────────────────┘
```

> **DevOps Relevance:** In CI/CD pipelines, use OIDC federation (GitHub Actions → AWS) instead of storing access keys as secrets. This eliminates long-lived credentials entirely.

---

## 10. Serverless Computing

### 10.1 What Is Serverless?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  SERVERLESS ≠ "No servers" — it means "not YOUR servers"        │
  │                                                                  │
  │  Traditional:              Serverless:                           │
  │  ┌────────────────────┐   ┌────────────────────┐                │
  │  │ You manage:        │   │ You manage:        │                │
  │  │ • Server OS        │   │ • Code/function    │                │
  │  │ • Patching         │   │ • Configuration    │                │
  │  │ • Scaling          │   │                    │                │
  │  │ • Availability     │   │ Cloud manages:     │                │
  │  │ • Capacity         │   │ • Everything else  │                │
  │  │ • Code             │   │ • Auto-scaling     │                │
  │  └────────────────────┘   │ • HA               │                │
  │                           │ • Patching         │                │
  │  Pay: 24/7 (even idle)   │ • Pay-per-request  │                │
  │                           └────────────────────┘                │
  └──────────────────────────────────────────────────────────────────┘
```

### 10.2 AWS Lambda Architecture

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  LAMBDA EXECUTION MODEL                                          │
  │                                                                  │
  │  Event Source                     Lambda Function                │
  │  ┌──────────────┐               ┌──────────────────────────────┐│
  │  │ API Gateway   │──── trigger ──►│ handler(event, context):    ││
  │  │ S3 event     │               │   # your code here          ││
  │  │ SQS message  │               │   return {"statusCode": 200}││
  │  │ EventBridge  │               └──────────────────────────────┘│
  │  │ DynamoDB     │                                               │
  │  │ CloudWatch   │               Execution Environment:          │
  │  └──────────────┘               ┌──────────────────────────────┐│
  │                                 │ Memory: 128 MB – 10 GB      ││
  │                                 │ Timeout: 1s – 15 min        ││
  │                                 │ Ephemeral storage: /tmp 10GB ││
  │                                 │ Concurrent: 1000 default     ││
  │                                 └──────────────────────────────┘│
  │                                                                  │
  │  Cold Start vs Warm:                                            │
  │  ┌──────────────────────────────────────────────────┐            │
  │  │ COLD START (first invocation / scaled out):      │            │
  │  │ Download code → Start runtime → Init function    │            │
  │  │ → Execute handler                                │            │
  │  │ Time: 100ms (Python) to 3-10s (Java, .NET)      │            │
  │  │                                                  │            │
  │  │ WARM START (reused container):                   │            │
  │  │ Execute handler directly                         │            │
  │  │ Time: 1-10ms                                     │            │
  │  └──────────────────────────────────────────────────┘            │
  └──────────────────────────────────────────────────────────────────┘
```

### 10.3 Serverless Services Beyond Functions

| Category | AWS | Azure | GCP |
|----------|-----|-------|-----|
| **Functions** | Lambda | Azure Functions | Cloud Functions |
| **Containers** | Fargate | Container Apps | Cloud Run |
| **API Gateway** | API Gateway | API Management | API Gateway |
| **Event Bus** | EventBridge | Event Grid | Eventarc |
| **Queue** | SQS | Service Bus | Cloud Tasks |
| **Step Functions** | Step Functions | Logic Apps | Workflows |
| **Database** | DynamoDB | Cosmos DB (serverless) | Firestore |

> **⚠️ Gotcha (Cold Starts):** Cold starts kill latency-sensitive APIs. Mitigations: Provisioned Concurrency (Lambda), keep-warm pings, use smaller runtimes (Python/Node over Java), minimize dependencies, reduce package size.

---

## 11. Containers & Orchestration in the Cloud

### 11.1 Container Services Landscape

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CONTAINER SERVICES — FROM SIMPLE TO COMPLEX                     │
  │                                                                  │
  │  Complexity ──────────────────────────────────────────►          │
  │  Control    ──────────────────────────────────────────►          │
  │                                                                  │
  │  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐       │
  │  │ Cloud Run /  │  │ ECS / ACI /    │  │ EKS / AKS /   │       │
  │  │ Fargate      │  │ Cloud Run Jobs │  │ GKE            │       │
  │  │              │  │                │  │                │       │
  │  │ • Serverless │  │ • Managed      │  │ • Full K8s    │       │
  │  │ • No infra   │  │   container    │  │ • Maximum     │       │
  │  │   management │  │   orchestration│  │   control     │       │
  │  │ • Per-request │  │ • Task defs   │  │ • Complex     │       │
  │  │   billing    │  │ • Service mesh │  │ • Large teams │       │
  │  │ • Simple     │  │   optional     │  │ • Multi-cloud │       │
  │  │   services   │  │ • Medium teams │  │   portable    │       │
  │  └──────────────┘  └────────────────┘  └────────────────┘       │
  │                                                                  │
  │  Decision: "How much control do you need?"                      │
  │  • Just run containers? → Fargate / Cloud Run                  │
  │  • Need task scheduling? → ECS                                 │
  │  • Need K8s ecosystem? → EKS / AKS / GKE                     │
  └──────────────────────────────────────────────────────────────────┘
```

### 11.2 EKS / AKS / GKE Architecture

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  MANAGED KUBERNETES — WHAT THE CLOUD MANAGES                     │
  │                                                                  │
  │  ┌──────────────────── Control Plane (Managed) ──────────────┐  │
  │  │  API Server │ etcd │ Scheduler │ Controller Manager       │  │
  │  │  (The cloud provider manages HA, patching, scaling)       │  │
  │  └───────────────────────────┬───────────────────────────────┘  │
  │                              │                                   │
  │  ┌───────────────────────────┼─── Data Plane (You manage) ──┐   │
  │  │                           │                              │   │
  │  │  ┌─── Node Group / Pool ──┼───────────────────────┐      │   │
  │  │  │                        │                       │      │   │
  │  │  │  Worker Node 1         │   Worker Node 2       │      │   │
  │  │  │  ┌──────┐ ┌──────┐    │   ┌──────┐ ┌──────┐   │      │   │
  │  │  │  │Pod A │ │Pod B │    │   │Pod C │ │Pod D │   │      │   │
  │  │  │  └──────┘ └──────┘    │   └──────┘ └──────┘   │      │   │
  │  │  │  kubelet, kube-proxy  │   kubelet, kube-proxy  │      │   │
  │  │  └───────────────────────┴────────────────────────┘      │   │
  │  │                                                          │   │
  │  │  OR: Fargate / Virtual Nodes (serverless nodes)         │   │
  │  │  → No EC2 management at all                              │   │
  │  └──────────────────────────────────────────────────────────┘   │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 12. Infrastructure as Code (IaC)

### 12.1 Why IaC?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  MANUAL vs IaC                                                   │
  │                                                                  │
  │  Manual (ClickOps):            Infrastructure as Code:           │
  │  ┌──────────────────────┐     ┌──────────────────────────┐      │
  │  │ Click through console │     │ resource "aws_instance" {│      │
  │  │ Screenshot as docs    │     │   ami = "ami-12345"      │      │
  │  │ "Works on my account"│     │   instance_type = "t3.m" │      │
  │  │ No audit trail       │     │ }                        │      │
  │  │ Can't reproduce      │     │                          │      │
  │  │ Drift happens        │     │ Version controlled (Git) │      │
  │  └──────────────────────┘     │ Reviewable (PR process)  │      │
  │                                │ Reproducible (any env)   │      │
  │  ❌ Error-prone                │ Auditable (who changed?) │      │
  │  ❌ Not scalable               └──────────────────────────┘      │
  │  ❌ Knowledge in heads          ✅ Infrastructure = Code         │
  └──────────────────────────────────────────────────────────────────┘
```

### 12.2 IaC Tools Comparison

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  IAC TOOLS — CHOOSING THE RIGHT ONE                                  │
  │                                                                      │
  │  Tool            │ Language    │ State     │ Cloud    │ Best For      │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  Terraform       │ HCL        │ State file│ Multi    │ Multi-cloud   │
  │  (HashiCorp)     │            │ (remote)  │          │ standard IaC  │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  OpenTofu        │ HCL        │ State file│ Multi    │ Open-source   │
  │  (fork)          │            │ (remote)  │          │ Terraform alt │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  CloudFormation  │ YAML/JSON  │ AWS-      │ AWS only │ AWS-native    │
  │  (AWS)           │            │ managed   │          │ tight integr. │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  Bicep           │ Bicep DSL  │ Azure-    │ Azure    │ Azure-native  │
  │  (Microsoft)     │            │ managed   │ only     │               │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  Pulumi          │ Python,    │ State file│ Multi    │ General-      │
  │                  │ TS, Go, C# │ or cloud  │          │ purpose langs │
  │  ────────────────┼────────────┼───────────┼──────────┼─────────────  │
  │  Ansible         │ YAML       │ Stateless │ Multi    │ Config mgmt   │
  │  (Red Hat)       │            │           │          │ + some IaC    │
  └──────────────────────────────────────────────────────────────────────┘
```

### 12.3 Terraform Workflow

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  TERRAFORM WORKFLOW                                              │
  │                                                                  │
  │  1. Write (.tf files):                                          │
  │     main.tf, variables.tf, outputs.tf, providers.tf             │
  │         │                                                        │
  │         ▼                                                        │
  │  2. terraform init                                               │
  │     Download providers, initialize backend                      │
  │         │                                                        │
  │         ▼                                                        │
  │  3. terraform plan                                               │
  │     Show what WILL change (diff)  ← review this carefully!     │
  │         │                                                        │
  │         ▼                                                        │
  │  4. terraform apply                                              │
  │     Execute the plan, create/update/delete resources            │
  │         │                                                        │
  │         ▼                                                        │
  │  5. State file updated (terraform.tfstate)                      │
  │     Records what Terraform manages                              │
  │                                                                  │
  │  State file MUST be:                                            │
  │  • Stored remotely (S3 + DynamoDB lock, Terraform Cloud)       │
  │  • NEVER committed to Git                                       │
  │  • Locked during apply (prevent concurrent modifications)      │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha (State File):** If you lose the state file, Terraform loses track of all managed resources. They still exist in the cloud but Terraform can't manage them. Always use remote state with versioning and locking. Treat the state file like a database — back it up.

---

## 13. CI/CD in the Cloud

### 13.1 CI/CD Pipeline — Cloud-Native

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CLOUD CI/CD PIPELINE                                                │
  │                                                                      │
  │  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐   │
  │  │  Code    │    │  Build   │    │  Test    │    │   Deploy      │   │
  │  │  Push    │───►│  & Lint  │───►│  & Scan  │───►│   (staging)   │   │
  │  │  (Git)   │    │          │    │          │    │               │   │
  │  └─────────┘    └──────────┘    └──────────┘    └───────┬───────┘   │
  │                                                         │           │
  │                                                  ┌──────▼───────┐   │
  │                                                  │  Approval    │   │
  │                                                  │  Gate        │   │
  │                                                  │  (manual/    │   │
  │                                                  │   automated) │   │
  │                                                  └──────┬───────┘   │
  │                                                         │           │
  │                                                  ┌──────▼───────┐   │
  │                                                  │  Deploy      │   │
  │                                                  │  (production)│   │
  │                                                  └──────────────┘   │
  │                                                                      │
  │  Cloud-native CI/CD services:                                       │
  │  AWS:   CodePipeline + CodeBuild + CodeDeploy                       │
  │  Azure: Azure DevOps Pipelines                                      │
  │  GCP:   Cloud Build + Cloud Deploy                                  │
  │  Also:  GitHub Actions, GitLab CI, Jenkins                          │
  └──────────────────────────────────────────────────────────────────────┘
```

### 13.2 Deployment Strategies

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DEPLOYMENT STRATEGIES                                           │
  │                                                                  │
  │  1. Rolling Update (gradual replacement):                       │
  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                              │
  │  │v1   │ │v1   │ │v1   │ │v1   │  Start                       │
  │  │v2 ← │ │v1   │ │v1   │ │v1   │  Step 1: replace 1          │
  │  │v2   │ │v2 ← │ │v1   │ │v1   │  Step 2: replace 2          │
  │  │v2   │ │v2   │ │v2 ← │ │v2 ← │  Done: all v2               │
  │  └─────┘ └─────┘ └─────┘ └─────┘                              │
  │  ✅ Zero downtime  ❌ Mixed versions during deploy             │
  │                                                                  │
  │  2. Blue/Green (instant switch):                                │
  │  ┌──────────┐  ┌──────────┐    ┌──────────┐  ┌──────────┐     │
  │  │ Blue (v1)│  │Green(v2) │    │ Blue (v1)│  │Green(v2) │     │
  │  │ ACTIVE ← │  │ (staging)│    │ (standby)│  │ ACTIVE ← │     │
  │  └──────────┘  └──────────┘    └──────────┘  └──────────┘     │
  │  ✅ Instant rollback  ❌ 2× resources during transition       │
  │                                                                  │
  │  3. Canary (gradual traffic shift):                             │
  │  ┌────────────────────────────────────────────────┐             │
  │  │ 95% → v1 (stable)     │  5% → v2 (canary)    │             │
  │  │                        │  Monitor errors/latency│             │
  │  │ If OK: 90/10 → 70/30 → 50/50 → 0/100         │             │
  │  │ If bad: route 100% back to v1                  │             │
  │  └────────────────────────────────────────────────┘             │
  │  ✅ Lowest risk  ❌ Complex to set up                          │
  │                                                                  │
  │  4. Recreate (downtime deploy):                                 │
  │  Kill all v1 → Deploy v2 → Start v2                             │
  │  ❌ Downtime  ✅ Simple, clean cut                             │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 14. Monitoring & Observability

### 14.1 The Three Pillars

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  THREE PILLARS OF OBSERVABILITY                                  │
  │                                                                  │
  │  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐│
  │  │    METRICS        │  │    LOGS           │  │   TRACES       ││
  │  │                   │  │                   │  │                ││
  │  │ Numeric data over │  │ Text records of   │  │ End-to-end    ││
  │  │ time              │  │ events            │  │ request flow  ││
  │  │                   │  │                   │  │ across svc's  ││
  │  │ • CPU usage: 73%  │  │ • Error: DB conn  │  │ • Request     ││
  │  │ • Request rate:   │  │   failed at 12:05 │  │   started at  ││
  │  │   500 req/s       │  │ • Auth failed for │  │   API GW →    ││
  │  │ • Error rate: 2%  │  │   user X          │  │   Auth svc →  ││
  │  │ • Latency p99:    │  │ • Deployment      │  │   DB query →  ││
  │  │   200ms           │  │   started v2.3    │  │   Cache hit   ││
  │  │                   │  │                   │  │   → Response   ││
  │  │ Tools:            │  │ Tools:            │  │ Tools:         ││
  │  │ • Prometheus      │  │ • CloudWatch Logs │  │ • Jaeger       ││
  │  │ • CloudWatch      │  │ • ELK Stack       │  │ • Zipkin       ││
  │  │ • Datadog         │  │ • Loki            │  │ • X-Ray        ││
  │  │ • Grafana         │  │ • Splunk          │  │ • Tempo        ││
  │  └──────────────────┘  └──────────────────┘  └────────────────┘│
  │                                                                  │
  │  Together they answer:                                          │
  │  Metrics: "Something is wrong" (alert!)                         │
  │  Logs:    "What happened?" (context)                            │
  │  Traces:  "Where in the chain?" (root cause)                    │
  └──────────────────────────────────────────────────────────────────┘
```

### 14.2 Key Metrics to Monitor

| Category | Metric | Alert Threshold | Tool |
|----------|--------|----------------|------|
| **Compute** | CPU utilization | > 80% sustained | CloudWatch |
| **Compute** | Memory usage | > 85% | Prometheus node_exporter |
| **Compute** | Disk usage | > 80% | CloudWatch / Prometheus |
| **Application** | Error rate (5xx) | > 1% | ALB metrics / Prometheus |
| **Application** | Latency (p99) | > 500ms (varies) | X-Ray / Jaeger |
| **Application** | Request rate | Sudden drop > 50% | Prometheus |
| **Database** | Connection count | > 80% max | RDS enhanced monitoring |
| **Database** | Replication lag | > 5s | RDS metrics |
| **Queue** | Queue depth | Growing over time | SQS metrics |
| **Cost** | Daily spend | > 120% of baseline | AWS Cost Explorer |

### 14.3 Alerting Strategy

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ALERTING — DON'T OVER-ALERT (Alert Fatigue = Ignoring Alerts) │
  │                                                                  │
  │  Severity     Condition                  Action                  │
  │  ──────────   ───────────────────────    ──────────────────────  │
  │  P1 Critical  Service down, data loss    Page on-call (2 min)   │
  │               5xx > 10%, complete outage  Wake up at 3am        │
  │                                                                  │
  │  P2 High      Degraded performance       Page on-call (15 min)  │
  │               p99 latency > 2s           Business hours         │
  │               Error rate > 5%                                    │
  │                                                                  │
  │  P3 Warning   Approaching limits         Slack notification     │
  │               Disk > 80%, CPU > 70%      Review next business   │
  │               Cert expiring in 14 days   day                    │
  │                                                                  │
  │  P4 Info      Deployment completed       Log only               │
  │               Auto-scaling event         Dashboard              │
  │               Routine maintenance                                │
  │                                                                  │
  │  Rule: If you can't take action on an alert, don't page for it.│
  └──────────────────────────────────────────────────────────────────┘
```

---

## 15. High Availability & Disaster Recovery

### 15.1 HA Concepts — RTO & RPO

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  RTO & RPO — THE TWO CRITICAL METRICS                           │
  │                                                                  │
  │  Time ────────────────────────────────────────────────────►      │
  │                                                                  │
  │       Last          Disaster         Service                     │
  │       Backup        Strikes!         Restored                    │
  │         │              │                │                         │
  │  ───────┼──────────────┼────────────────┼──────────────────      │
  │         │              │                │                         │
  │         ├──── RPO ─────┤                │                         │
  │         │ (data loss   │                │                         │
  │         │  tolerance)  ├────── RTO ─────┤                         │
  │                        │ (downtime       │                         │
  │                        │  tolerance)     │                         │
  │                                                                  │
  │  RPO (Recovery Point Objective):                                │
  │  "How much data can we afford to lose?"                         │
  │  RPO = 0   → real-time replication (synchronous)               │
  │  RPO = 1h  → hourly backups (lose max 1 hour of data)         │
  │  RPO = 24h → daily backups                                     │
  │                                                                  │
  │  RTO (Recovery Time Objective):                                 │
  │  "How long can we be down?"                                     │
  │  RTO = 0     → hot standby, auto-failover                      │
  │  RTO = 4h    → warm standby, scripted recovery                 │
  │  RTO = 24h   → cold standby, manual recovery                   │
  └──────────────────────────────────────────────────────────────────┘
```

### 15.2 DR Strategies — Cost vs Recovery Time

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DR STRATEGIES (cheapest → most expensive)                       │
  │                                                                  │
  │  1. BACKUP & RESTORE                                            │
  │     ├── RTO: hours | RPO: hours                                 │
  │     ├── Cost: $ (just storage)                                  │
  │     └── How: Regular backups to another region                  │
  │         Restore from backup when disaster hits                  │
  │                                                                  │
  │  2. PILOT LIGHT                                                 │
  │     ├── RTO: 10s of minutes | RPO: minutes                     │
  │     ├── Cost: $$ (minimal infra running)                        │
  │     └── How: Core services running (DB replication)             │
  │         Scale up other services during recovery                 │
  │                                                                  │
  │  3. WARM STANDBY                                                │
  │     ├── RTO: minutes | RPO: seconds-minutes                    │
  │     ├── Cost: $$$ (scaled-down clone running)                   │
  │     └── How: Smaller version of full environment                │
  │         Scale up to production size during recovery             │
  │                                                                  │
  │  4. MULTI-SITE ACTIVE/ACTIVE                                   │
  │     ├── RTO: ~0 | RPO: ~0                                      │
  │     ├── Cost: $$$$ (2× full environments)                       │
  │     └── How: Full production in 2+ regions                      │
  │         Traffic routed to both (Route 53 failover)             │
  └──────────────────────────────────────────────────────────────────┘
```

### 15.3 Multi-AZ vs Multi-Region

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  Multi-AZ (High Availability)     Multi-Region (Disaster Recovery)│
  │                                                                  │
  │  ┌─ Region ─────────────┐        ┌─ Region A ──┐  ┌─ Region B ─┐│
  │  │  ┌─AZ-a─┐  ┌─AZ-b─┐ │        │  Full env   │  │  Full env  ││
  │  │  │ App  │  │ App  │ │        │  ┌──────┐   │  │  ┌──────┐  ││
  │  │  │ DB   │  │ DB   │ │        │  │Active│   │  │  │Standby│  ││
  │  │  │ (pri)│  │(repl)│ │        │  └──────┘   │  │  └──────┘  ││
  │  │  └──────┘  └──────┘ │        └─────────────┘  └────────────┘│
  │  └──────────────────────┘                                        │
  │                                                                  │
  │  Protects against:              Protects against:                │
  │  • Single DC failure            • Region-wide outage            │
  │  • Hardware failure             • Natural disaster              │
  │  • Rack failure                 • Major network partition       │
  │                                                                  │
  │  Cost: Low (small premium)      Cost: High (2× infrastructure) │
  │  Complexity: Low                Complexity: High                │
  │  Latency: < 2ms between AZs    Latency: 50-200ms between      │
  │                                  regions                        │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 16. Cost Optimization & FinOps

### 16.1 Cloud Cost Breakdown

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  WHERE CLOUD MONEY GOES (typical breakdown)                      │
  │                                                                  │
  │  Compute:  55%  ████████████████████████████                     │
  │  Storage:  15%  ████████                                         │
  │  Network:  15%  ████████  (data transfer OUT is costly!)        │
  │  Database: 10%  █████                                            │
  │  Other:     5%  ███  (support, marketplace, etc.)               │
  │                                                                  │
  │  The #1 cost optimization: RIGHT-SIZE YOUR COMPUTE              │
  │  Most EC2 instances run at 10-30% CPU utilization               │
  └──────────────────────────────────────────────────────────────────┘
```

### 16.2 Cost Optimization Strategies

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD COST OPTIMIZATION CHECKLIST                               │
  │                                                                  │
  │  QUICK WINS (do these first):                                   │
  │  ├── ✅ Delete unused resources (EBS volumes, old snapshots,    │
  │  │      unattached EIPs, stopped instances)                     │
  │  ├── ✅ Right-size instances (use AWS Compute Optimizer)        │
  │  ├── ✅ Use Graviton/ARM instances (~20% cheaper)               │
  │  ├── ✅ Schedule dev/test environments off outside hours        │
  │  └── ✅ Use S3 lifecycle policies (move to IA/Glacier)         │
  │                                                                  │
  │  MEDIUM EFFORT:                                                 │
  │  ├── 💰 Buy Reserved Instances / Savings Plans (30-72% off)   │
  │  ├── 💰 Use Spot Instances for fault-tolerant workloads        │
  │  ├── 💰 Implement auto-scaling (don't over-provision)          │
  │  ├── 💰 Use VPC endpoints (avoid NAT Gateway data charges)    │
  │  └── 💰 Containerize for better density (Fargate vs EC2)      │
  │                                                                  │
  │  ARCHITECTURAL:                                                 │
  │  ├── 🏗️  Go serverless where possible (pay-per-request)        │
  │  ├── 🏗️  Use CDN to reduce origin data transfer               │
  │  ├── 🏗️  Compress data before storage/transfer                 │
  │  ├── 🏗️  Use multi-tier storage (hot/warm/cold)               │
  │  └── 🏗️  Review data transfer paths (cross-AZ, cross-region)  │
  └──────────────────────────────────────────────────────────────────┘
```

### 16.3 FinOps — Cloud Financial Operations

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  FINOPS FRAMEWORK                                                │
  │                                                                  │
  │  Phase 1: INFORM                                                │
  │  ├── Tag ALL resources (team, project, environment)             │
  │  ├── Enable Cost Explorer / billing alerts                      │
  │  ├── Create cost dashboards per team                            │
  │  └── Identify who owns what spend                               │
  │                                                                  │
  │  Phase 2: OPTIMIZE                                              │
  │  ├── Right-size based on utilization data                       │
  │  ├── Purchase commitments (RI/SP) for baseline                  │
  │  ├── Automate scheduling (dev off at night)                     │
  │  └── Set budgets and anomaly detection alerts                   │
  │                                                                  │
  │  Phase 3: OPERATE                                               │
  │  ├── Teams own their cloud costs                                │
  │  ├── Cost review in sprint planning                             │
  │  ├── Architecture reviews include cost impact                   │
  │  └── Continuous optimization culture                            │
  │                                                                  │
  │  Tools: AWS Cost Explorer, Azure Cost Management,               │
  │         GCP Billing, Kubecost (K8s), Infracost (Terraform)     │
  └──────────────────────────────────────────────────────────────────┘
```

> **⚠️ Gotcha (Data Transfer Costs):** Data transfer IN is usually free. Data transfer OUT to the internet costs $0.09/GB. Cross-region transfer costs money. Cross-AZ transfer costs $0.01/GB each way. A chatty microservice architecture across AZs can rack up surprising bills.

---

## 17. Security & Compliance

### 17.1 Shared Responsibility Model

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  SHARED RESPONSIBILITY MODEL                                         │
  │                                                                      │
  │  ┌──────────────── Customer (YOU) Responsibility ────────────────┐   │
  │  │  Data encryption, IAM policies, OS patching (EC2),            │   │
  │  │  Network config (SGs, NACLs), Application security,           │   │
  │  │  Client-side encryption, MFA, access control                  │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                                                      │
  │  ════════════════════ Shared ═════════════════════════               │
  │  Patch management, configuration management, awareness              │
  │  ════════════════════════════════════════════════════                │
  │                                                                      │
  │  ┌──────────────── Cloud Provider Responsibility ────────────────┐   │
  │  │  Physical security, hardware maintenance, hypervisor          │   │
  │  │  patching, network infrastructure, power/cooling, DDoS       │   │
  │  │  protection (L3/L4), compliance certifications              │   │
  │  └──────────────────────────────────────────────────────────────┘   │
  │                                                                      │
  │  Note: More managed = more provider responsibility                  │
  │  EC2:    You patch OS, secure app                                   │
  │  RDS:    Provider patches OS, you secure access/data               │
  │  Lambda: Provider patches everything, you secure code/IAM          │
  └──────────────────────────────────────────────────────────────────────┘
```

### 17.2 Security Best Practices

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD SECURITY CHECKLIST (Critical 15)                          │
  │                                                                  │
  │  Identity:                                                       │
  │  ├── 1. Enable MFA on all human accounts                        │
  │  ├── 2. Use IAM roles (not access keys) for services            │
  │  ├── 3. Implement least privilege policies                       │
  │  └── 4. Regular access reviews (remove unused)                  │
  │                                                                  │
  │  Network:                                                        │
  │  ├── 5. Use private subnets for workloads                       │
  │  ├── 6. Minimize security group rules (no 0.0.0.0/0 on 22)    │
  │  ├── 7. Enable VPC Flow Logs                                    │
  │  └── 8. Use VPC endpoints for AWS services                      │
  │                                                                  │
  │  Data:                                                           │
  │  ├── 9. Encrypt at rest (EBS, S3, RDS)                          │
  │  ├── 10. Encrypt in transit (TLS everywhere)                    │
  │  ├── 11. Use secrets manager (not env vars / config files)      │
  │  └── 12. Enable S3 Block Public Access (account-wide)          │
  │                                                                  │
  │  Monitoring:                                                     │
  │  ├── 13. Enable CloudTrail (API audit log)                      │
  │  ├── 14. Enable GuardDuty / Security Hub                        │
  │  └── 15. Set up billing alerts (detect compromised account)    │
  └──────────────────────────────────────────────────────────────────┘
```

---

## 18. Production Gotchas & Scenario-Based FAQ

### Q1: Our EC2 instance can't reach the internet. How do we troubleshoot?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  EC2 INTERNET CONNECTIVITY TROUBLESHOOTING                       │
  │                                                                  │
  │  Is it in a public or private subnet?                           │
  │  │                                                               │
  │  ├── PUBLIC subnet:                                             │
  │  │   ├── Does it have a public IP or Elastic IP?               │
  │  │   ├── Route table: 0.0.0.0/0 → igw-xxx?                    │
  │  │   ├── Security Group: allows outbound?                      │
  │  │   ├── NACL: allows outbound + return traffic?               │
  │  │   └── OS-level firewall (iptables)?                         │
  │  │                                                               │
  │  └── PRIVATE subnet:                                            │
  │      ├── Route table: 0.0.0.0/0 → nat-xxx?                    │
  │      ├── NAT Gateway exists and is in a public subnet?         │
  │      ├── NAT Gateway has an Elastic IP?                        │
  │      ├── NAT Gateway's subnet route: 0.0.0.0/0 → igw-xxx?    │
  │      └── Security Group / NACL allows outbound?                │
  │                                                                  │
  │  Quick test from the instance:                                  │
  │  ping 8.8.8.8        ← tests IP connectivity                  │
  │  ping google.com     ← tests DNS + IP connectivity             │
  │  curl -v https://google.com ← tests full HTTP stack            │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q2: Our cloud bill doubled this month. How do we find out what caused it?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  COST SPIKE INVESTIGATION                                        │
  │                                                                  │
  │  1. AWS Cost Explorer → Group by Service → see which spiked    │
  │                                                                  │
  │  2. Common culprits:                                            │
  │     ├── NAT Gateway data transfer (forgotten high-throughput   │
  │     │   workload going through NAT)                             │
  │     ├── Forgotten resources (instance running in region you    │
  │     │   don't normally use)                                     │
  │     ├── Snapshot accumulation (daily snapshots never cleaned)  │
  │     ├── Data transfer between regions (replication)            │
  │     ├── Reserved Instance expiration (fell back to on-demand) │
  │     └── Compromised account (crypto mining!)                   │
  │                                                                  │
  │  3. Prevention:                                                 │
  │     ├── Set AWS Budgets with email alerts                      │
  │     ├── Enable Cost Anomaly Detection                          │
  │     ├── Tag everything (team, project, env)                    │
  │     ├── Monthly cost review ritual                              │
  │     └── Use Infracost in PR reviews (catch cost changes early) │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q3: When should I use multiple AWS accounts vs one account with multiple VPCs?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  MULTI-ACCOUNT STRATEGY (Recommended for organizations)          │
  │                                                                  │
  │  ┌─ Management Account ─┐                                       │
  │  │  AWS Organizations    │                                       │
  │  │  Billing consolidation│                                       │
  │  └──────────┬────────────┘                                       │
  │             │                                                    │
  │  ┌──────────┼──────────────────────────────────────┐             │
  │  │          │                                      │             │
  │  ▼          ▼                                      ▼             │
  │  Security   Shared Services    Production          Development   │
  │  Account    Account            Account             Account       │
  │  (GuardDuty (CI/CD, DNS,       (prod workloads)   (dev/test)   │
  │   CloudTrail shared infra)                                      │
  │   SSO)                                                          │
  │                                                                  │
  │  Why separate accounts?                                         │
  │  ├── 1. Blast radius isolation (prod ≠ dev)                    │
  │  ├── 2. Separate billing (cost allocation)                     │
  │  ├── 3. Service quotas per account (avoid limits)              │
  │  ├── 4. IAM boundaries (devs can't touch prod)                │
  │  └── 5. Compliance (PCI-DSS scope reduction)                   │
  │                                                                  │
  │  Connect via: Transit Gateway, RAM (Resource Access Manager)   │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q4: Our Terraform state is corrupted / lost. What do we do?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  TERRAFORM STATE RECOVERY                                        │
  │                                                                  │
  │  If state is corrupted:                                         │
  │  1. Restore from S3 versioning (always enable versioning!)     │
  │     aws s3api list-object-versions --bucket my-tf-state        │
  │     aws s3api get-object --bucket my-tf-state --key tfstate    │
  │       --version-id <old-version> ./terraform.tfstate            │
  │                                                                  │
  │  If state is completely lost:                                   │
  │  1. terraform import for each resource:                         │
  │     terraform import aws_instance.web i-1234567890              │
  │  2. Or use terraformer to auto-import existing infra            │
  │  3. Painstaking but possible                                    │
  │                                                                  │
  │  Prevention:                                                     │
  │  ├── ALWAYS use remote state with versioning                    │
  │  ├── Enable DynamoDB state locking                              │
  │  ├── Never edit state manually                                  │
  │  ├── Use terraform state commands for state surgery             │
  │  └── Back up state in CI/CD artifacts                           │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q5: How do we handle secrets in cloud deployments without hardcoding them?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  SECRETS MANAGEMENT — WORST TO BEST                              │
  │                                                                  │
  │  ❌ WORST: Hardcoded in source code                             │
  │     password = "admin123"  ← NEVER DO THIS                     │
  │                                                                  │
  │  ❌ BAD: .env files in Git                                      │
  │     DB_PASSWORD=admin123   ← .gitignore WILL be forgotten      │
  │                                                                  │
  │  ⚠️ OK: Environment variables in deployment config              │
  │     Still visible in process listing, ECS task def, etc.       │
  │                                                                  │
  │  ✅ GOOD: Cloud secrets manager                                  │
  │     AWS Secrets Manager / Azure Key Vault / GCP Secret Manager │
  │     Rotation, audit trail, IAM-controlled access               │
  │                                                                  │
  │  ✅ BEST: External secrets + auto-rotation                       │
  │     HashiCorp Vault → dynamic credentials (created on demand,  │
  │     expire automatically)                                       │
  │     External Secrets Operator (K8s → cloud secrets)            │
  │     OIDC federation (GitHub Actions → AWS, no keys at all)     │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q6: Our RDS database is running out of connections during traffic spikes. What do we do?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DATABASE CONNECTION MANAGEMENT                                  │
  │                                                                  │
  │  Problem:                                                        │
  │  Each app instance opens ~20 connections to DB                  │
  │  Auto-scaling adds 10 instances → 200 connections              │
  │  RDS max_connections = 150 (based on instance class) → BOOM    │
  │                                                                  │
  │  Solutions:                                                      │
  │  1. Connection Pooling (application-level):                     │
  │     PgBouncer, ProxySQL, HikariCP                               │
  │     Set pool size = 5-10 per instance                           │
  │                                                                  │
  │  2. RDS Proxy (managed pooling):                                │
  │     AWS-managed connection pooler                                │
  │     Handles multiplexing: 1000 app connections →                │
  │     50 actual DB connections                                    │
  │                                                                  │
  │  3. Scale up DB instance (more memory = more connections):      │
  │     db.r6g.large → db.r6g.xlarge                               │
  │     Quick fix but expensive                                      │
  │                                                                  │
  │  4. Read replicas for read traffic:                             │
  │     Route SELECT queries to read replicas                       │
  │     Primary handles only writes                                 │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q7: We need to migrate a legacy application to the cloud. What's the strategy?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  CLOUD MIGRATION STRATEGIES — THE 7 R's                          │
  │                                                                  │
  │  Strategy        Effort  Description                             │
  │  ──────────────  ──────  ─────────────────────────────────────   │
  │  1. Rehost       Low     "Lift and shift" — move as-is to VM   │
  │  2. Relocate     Low     "Hypervisor lift" — vSphere to VMC   │
  │  3. Replatform   Medium  "Lift and optimize" — move to managed │
  │                           services (MySQL → RDS, NFS → EFS)    │
  │  4. Refactor     High    Rearchitect for cloud-native           │
  │                           (monolith → microservices → K8s)     │
  │  5. Repurchase   Medium  Replace with SaaS (CRM → Salesforce) │
  │  6. Retain       None    Keep on-premises (regulatory, legacy)  │
  │  7. Retire       None    Turn off (unused / duplicate)          │
  │                                                                  │
  │  Typical approach:                                               │
  │  Phase 1: Rehost (get to cloud quickly, ~3 months)             │
  │  Phase 2: Replatform (optimize, use managed services, ~6 months)│
  │  Phase 3: Refactor (cloud-native, ongoing)                      │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q8: How do we handle multi-region deployments with databases?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  MULTI-REGION DATABASE STRATEGIES                                │
  │                                                                  │
  │  1. Read Replicas (async):                                      │
  │     Region A (primary) ──async──► Region B (read replica)      │
  │     Writes: Region A only   Reads: Both regions                │
  │     RPO: seconds (replication lag)                              │
  │                                                                  │
  │  2. Aurora Global Database:                                     │
  │     Region A (primary) ──async──► Region B (secondary)         │
  │     Replication lag: < 1 second                                │
  │     Failover to secondary in < 1 minute                        │
  │     RPO: ~1s, RTO: ~1min                                       │
  │                                                                  │
  │  3. DynamoDB Global Tables:                                     │
  │     Region A ◄──multi-master──► Region B                       │
  │     Active-active: writes to BOTH regions                      │
  │     Conflict resolution: last-writer-wins                      │
  │     RPO: ~0, RTO: ~0                                           │
  │                                                                  │
  │  4. CockroachDB / Spanner (multi-region ACID):                 │
  │     Strong consistency across regions                           │
  │     Higher latency (consensus protocol)                        │
  │     RPO: 0, RTO: ~0                                            │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q9: What's the difference between vertical and horizontal scaling, and when to use each?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  VERTICAL SCALING               HORIZONTAL SCALING               │
  │  (Scale Up)                     (Scale Out)                      │
  │                                                                  │
  │  ┌──────────┐                   ┌─────┐ ┌─────┐ ┌─────┐        │
  │  │          │                   │Small│ │Small│ │Small│        │
  │  │  BIG     │                   │  1  │ │  2  │ │  3  │        │
  │  │  SERVER  │                   └─────┘ └─────┘ └─────┘        │
  │  │          │                                                    │
  │  └──────────┘                   + add more as needed            │
  │                                                                  │
  │  Increase instance size:        Add more instances:              │
  │  t3.micro → t3.xlarge          1 instance → 10 instances       │
  │  → m6i.4xlarge → m6i.24xl     Behind a load balancer           │
  │                                                                  │
  │  ✅ Simple (no code changes)   ✅ Unlimited scale               │
  │  ✅ Good for databases         ✅ Fault tolerant                │
  │  ❌ Has a ceiling              ✅ Cost effective (spot)         │
  │  ❌ Single point of failure    ❌ App must be stateless         │
  │  ❌ Downtime during resize     ❌ More complex (LB, sessions)  │
  │                                                                  │
  │  Best practice: Design for horizontal, use vertical as needed  │
  │  Databases: often vertical | App servers: always horizontal    │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q10: Our container keeps getting OOMKilled in ECS/Kubernetes. Why?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  OOMKilled = Out Of Memory Killed                                │
  │                                                                  │
  │  Container memory limit: 512 MB                                 │
  │  Application uses: 520 MB → OOMKilled!                          │
  │                                                                  │
  │  Diagnosis:                                                      │
  │  kubectl describe pod <name>  → Last State: OOMKilled           │
  │  kubectl top pod <name>       → current memory usage            │
  │  docker stats                 → container memory usage          │
  │                                                                  │
  │  Common causes:                                                  │
  │  1. Memory limit too low (increase it)                          │
  │  2. Memory leak in application (fix the code)                   │
  │  3. JVM heap not matching container limits:                     │
  │     Container: 512 MB, JVM default heap: 1/4 of host memory   │
  │     Fix: -XX:MaxRAMPercentage=75.0 -XX:+UseContainerSupport   │
  │  4. Thread accumulation (each thread uses ~1MB stack)           │
  │                                                                  │
  │  K8s memory settings:                                            │
  │  requests: 256Mi  → scheduling (guaranteed minimum)            │
  │  limits:   512Mi  → OOMKill threshold (hard ceiling)           │
  │  Rule: limits = 1.5-2× requests (allow burst, prevent abuse)   │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q11: How does auto-scaling work in Kubernetes (HPA vs VPA vs KEDA)?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  KUBERNETES AUTOSCALING                                          │
  │                                                                  │
  │  HPA (Horizontal Pod Autoscaler):                               │
  │  Scale number of pod replicas based on CPU/memory/custom        │
  │  metrics. Most common for stateless workloads.                  │
  │  ┌───────┐ ┌───────┐        ┌───────┐ ┌───────┐ ┌───────┐     │
  │  │ Pod 1 │ │ Pod 2 │   →    │ Pod 1 │ │ Pod 2 │ │ Pod 3 │     │
  │  └───────┘ └───────┘        └───────┘ └───────┘ └───────┘     │
  │                                                                  │
  │  VPA (Vertical Pod Autoscaler):                                 │
  │  Adjust CPU/memory requests for existing pods.                  │
  │  ⚠️ Requires pod restart. Don't use with HPA on same metric.  │
  │  ┌─────────┐          ┌──────────────┐                          │
  │  │ 256Mi   │    →     │   512Mi      │                          │
  │  │ 100m CPU│          │   200m CPU   │                          │
  │  └─────────┘          └──────────────┘                          │
  │                                                                  │
  │  KEDA (Kubernetes Event-Driven Autoscaling):                    │
  │  Scale based on external events (SQS depth, Kafka lag,         │
  │  HTTP request rate, Prometheus queries).                        │
  │  Can scale to/from ZERO.                                       │
  │  ┌───────┐ ┌───────┐ ┌───────┐     → 0 pods (idle)            │
  │  └───────┘ └───────┘ └───────┘       (no cost when idle!)      │
  │                                                                  │
  │  Cluster Autoscaler:                                            │
  │  Adds/removes NODES based on pending pods.                     │
  │  Unschedulable pod → add node. Empty node → remove node.      │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q12: What's the best way to handle configuration across environments (dev/staging/prod)?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ENVIRONMENT CONFIGURATION MANAGEMENT                            │
  │                                                                  │
  │  ❌ BAD: Hardcoded per environment in code                      │
  │  ❌ BAD: Manual config changes on servers                       │
  │                                                                  │
  │  ✅ GOOD: External configuration per environment                │
  │                                                                  │
  │  Strategy 1: Environment Variables (12-Factor App)              │
  │  ECS Task Definition / K8s ConfigMap per environment            │
  │  dev:  DB_HOST=dev-db.internal   DB_NAME=myapp_dev             │
  │  prod: DB_HOST=prod-db.internal  DB_NAME=myapp_prod            │
  │                                                                  │
  │  Strategy 2: Secrets Manager (per-environment paths)            │
  │  /dev/myapp/db-password                                         │
  │  /prod/myapp/db-password                                        │
  │                                                                  │
  │  Strategy 3: Terraform workspaces / separate tfvars             │
  │  terraform workspace select prod                                │
  │  terraform apply -var-file=prod.tfvars                          │
  │                                                                  │
  │  Strategy 4: Helm values files (Kubernetes)                     │
  │  helm install myapp -f values-prod.yaml                         │
  │  helm install myapp -f values-dev.yaml                          │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q13: How do we implement zero-downtime database migrations (schema changes)?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ZERO-DOWNTIME DATABASE MIGRATIONS                               │
  │                                                                  │
  │  ❌ DANGEROUS: ALTER TABLE ... ADD COLUMN (locks table!)        │
  │                                                                  │
  │  ✅ SAFE: Expand-and-Contract pattern                           │
  │                                                                  │
  │  Step 1 (Expand): Add new column (nullable, no default)        │
  │  ALTER TABLE users ADD COLUMN email_v2 VARCHAR(255);            │
  │  → No lock, no downtime                                        │
  │                                                                  │
  │  Step 2 (Dual-write): App writes to BOTH old and new columns  │
  │  INSERT INTO users (email, email_v2) VALUES ($1, $1);          │
  │                                                                  │
  │  Step 3 (Backfill): Copy old data to new column               │
  │  UPDATE users SET email_v2 = email WHERE email_v2 IS NULL      │
  │  (do in batches to avoid lock escalation!)                     │
  │                                                                  │
  │  Step 4 (Switch reads): App reads from new column              │
  │                                                                  │
  │  Step 5 (Contract): Remove old column (next release)           │
  │  ALTER TABLE users DROP COLUMN email;                           │
  │                                                                  │
  │  Tools: gh-ost (GitHub), pt-online-schema-change (Percona),    │
  │         Flyway, Liquibase (migration management)                │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q14: What monitoring should we set up on Day 1 of a new cloud project?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  DAY 1 MONITORING CHECKLIST                                      │
  │                                                                  │
  │  Infrastructure:                                                 │
  │  ├── ✅ CloudWatch / monitoring agent on all instances          │
  │  ├── ✅ CPU, memory, disk alerts (>80% warning, >90% critical) │
  │  ├── ✅ VPC Flow Logs enabled                                   │
  │  └── ✅ CloudTrail enabled (API audit log)                      │
  │                                                                  │
  │  Application:                                                    │
  │  ├── ✅ Health check endpoint (/health, /readyz)               │
  │  ├── ✅ Request rate + error rate dashboards                    │
  │  ├── ✅ Latency percentiles (p50, p95, p99)                    │
  │  └── ✅ Centralized logging (CloudWatch Logs / ELK)            │
  │                                                                  │
  │  Costs:                                                          │
  │  ├── ✅ AWS Budgets with email alerts                           │
  │  ├── ✅ Cost anomaly detection enabled                          │
  │  └── ✅ Resource tagging policy enforced                        │
  │                                                                  │
  │  Security:                                                       │
  │  ├── ✅ GuardDuty enabled                                       │
  │  ├── ✅ Billing alerts (detect compromised account)            │
  │  └── ✅ Config rules for compliance                             │
  │                                                                  │
  │  Uptime:                                                         │
  │  └── ✅ External synthetic monitoring (Pingdom, UptimeRobot)   │
  └──────────────────────────────────────────────────────────────────┘
```

---

### Q15: How do we choose between ECS and EKS (or equivalent on Azure/GCP)?

```
  ┌──────────────────────────────────────────────────────────────────┐
  │  ECS vs EKS DECISION MATRIX                                      │
  │                                                                  │
  │  Choose ECS (or Cloud Run / ACI) if:                            │
  │  ├── Small-medium team (< 50 engineers)                         │
  │  ├── AWS-only deployment                                        │
  │  ├── Want simplicity over control                               │
  │  ├── Don't need K8s ecosystem (Helm, operators, CRDs)         │
  │  ├── Mostly stateless services                                  │
  │  └── Want to minimize operational overhead                      │
  │                                                                  │
  │  Choose EKS (or AKS / GKE) if:                                 │
  │  ├── Large team with K8s experience                             │
  │  ├── Multi-cloud or avoid vendor lock-in                       │
  │  ├── Need K8s ecosystem (Istio, Argo, Prometheus)              │
  │  ├── Complex orchestration (stateful sets, operators)          │
  │  ├── Need to run same platform on-prem and cloud              │
  │  └── Already have significant K8s investment                    │
  │                                                                  │
  │  Cost note: EKS control plane = $0.10/hr ($73/month)          │
  │  + worker nodes. ECS control plane is free.                    │
  │  GKE Autopilot: only pay for pods (no node management)         │
  └──────────────────────────────────────────────────────────────────┘
```

---

> **Handbook complete.** This covers data center fundamentals through cloud-native architecture — the full spectrum for DevOps engineers working with cloud infrastructure.  
> **Next:** Try the [Cloud Practice Lab](../labs/cloud_practice_lab.md) or the [Networking Handbook](../networking/networking_handbook.md).

[🏠 Home](../README.md) · [Cloud](README.md)
