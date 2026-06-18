# 🔷 Batch 6: Advanced Architecture Patterns & Real-World Projects

> **Level:** Advanced | **Estimated Total Time:** 18–25 days | **Scenarios:** 7 (numbered 28–34)
>
> This is the capstone batch. These scenarios represent real-world architecture challenges you'll face in enterprise Azure projects. Each one combines multiple services and skills from all previous batches.

---

## 📑 Table of Contents

- [Scenario 28: Multi-Region Active-Active Deployment](#scenario-28-multi-region-active-active-deployment)
- [Scenario 29: Microservices Architecture on Azure](#scenario-29-microservices-architecture-on-azure)
- [Scenario 30: Event-Driven Architecture & CQRS](#scenario-30-event-driven-architecture--cqrs)
- [Scenario 31: Zero-Trust Security Architecture](#scenario-31-zero-trust-security-architecture)
- [Scenario 32: Migration to Azure](#scenario-32-migration-to-azure)
- [Scenario 33: Azure Landing Zone & Enterprise-Scale](#scenario-33-azure-landing-zone--enterprise-scale)
- [Scenario 34: Performance Testing & Chaos Engineering](#scenario-34-performance-testing--chaos-engineering)
- [Learning Path Summary](#-learning-path-summary)
- [Recommended Certification Path](#-recommended-certification-path)

---

## Scenario 28: Multi-Region Active-Active Deployment

### 🎯 Objective
Design and deploy a globally distributed application where multiple regions actively serve traffic simultaneously. Handle data replication, conflict resolution, and automated regional failover.

### 📦 App Description
**A global SaaS platform (project management tool like Jira/Asana)** with users in US, Europe, and Asia. Each region must have <100ms latency. Data must be consistent across regions with real-time collaboration features.

### 🏗️ Architecture Diagram
```
                         GLOBAL USERS
              US   │    Europe   │    Asia
                   │             │
          ┌────────▼─────────────▼────────▼────────┐
          │           AZURE FRONT DOOR              │
          │    (Global L7 + WAF + Caching)          │
          │    Routing: Latency-based               │
          └──────┬──────────────┬──────────────┬────┘
                 │              │              │
    ┌────────────▼──┐  ┌───────▼───────┐  ┌───▼──────────┐
    │   EAST US      │  │ WEST EUROPE   │  │ SE ASIA      │
    │                │  │               │  │              │
    │  AKS/App Svc   │  │  AKS/App Svc  │  │ AKS/App Svc  │
    │  (Active)      │  │  (Active)     │  │ (Active)     │
    │       │        │  │       │       │  │      │       │
    │  Cosmos DB     │  │  Cosmos DB    │  │ Cosmos DB    │
    │  (Write Region)│  │  (Write)      │  │ (Write)      │
    │       │        │  │       │       │  │      │       │
    │  Redis Cache   │  │  Redis Cache  │  │ Redis Cache  │
    │  (Local)       │  │  (Local)      │  │ (Local)      │
    └────────────────┘  └───────────────┘  └──────────────┘
           │                    │                   │
           └────────────────────┴───────────────────┘
                    Cosmos DB Multi-Region Writes
                    (Automatic conflict resolution)
```

### ✅ Hands-on Tasks

#### Part A: Global Entry Point
- [ ] Deploy Azure Front Door Premium as the global entry point
- [ ] Configure latency-based routing to 2+ regions
- [ ] Attach WAF policy with OWASP 3.2 managed rules
- [ ] Configure caching for static assets
- [ ] Set up health probes with automatic failover (if a region goes unhealthy)
- [ ] Configure custom domain with managed SSL certificate

#### Part B: Multi-Region Compute
- [ ] Deploy identical application stacks in 2+ regions
- [ ] Use IaC (Bicep/Terraform) to ensure consistency across regions
- [ ] Configure App Configuration service for centralized config
- [ ] Implement health check endpoints that verify all dependencies

#### Part C: Multi-Region Data
- [ ] Configure Cosmos DB with multi-region writes (all regions can accept writes)
- [ ] Choose conflict resolution policy:
  - Last Writer Wins (default, based on `_ts` timestamp)
  - Custom conflict resolution with stored procedure
- [ ] Set up Azure SQL failover group (one write region + read replicas)
- [ ] Configure local Redis Cache in each region for session/cache data
- [ ] Handle session affinity: user's session should be accessible from any region

> ⚠️ **DevOps Gotcha:** Multi-region writes in Cosmos DB can cause **data conflicts** when two regions update the same document simultaneously. The default "Last Writer Wins" strategy silently drops the losing write. For critical data (financial transactions, inventory counts), you MUST implement custom conflict resolution or use an architectural pattern that avoids concurrent writes to the same document (e.g., partition ownership).

#### Part D: Failover Testing
- [ ] Disable one origin in Front Door and verify traffic routes to remaining regions
- [ ] Simulate a Cosmos DB regional outage (change failover priority)
- [ ] Test SQL failover group: initiate manual failover, verify app reconnects
- [ ] Measure actual failover time (should be <60 seconds for Front Door)
- [ ] Document the failover procedure in a runbook

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Split-brain: both regions think they're primary | Network partition between regions | Cosmos DB handles this with conflict resolution; SQL uses quorum |
| Data conflicts in Cosmos DB | Concurrent writes to same document in different regions | Use LWW or custom merge procedure; design to avoid conflicts |
| DNS propagation delay during failover | Front Door DNS TTL | Front Door handles this at the edge; DNS caching minimal |
| Session lost after region failover | Session stored in local Redis only | Use centralized session store or replicate sessions |
| Cost doubling with multi-region | Running everything twice | Optimize: smaller SKUs in secondary; use reserved capacity |

### 💰 Cost Tips
- Multi-region roughly **doubles** compute and data costs
- Use smaller SKUs in secondary regions if they only handle overflow
- Cosmos DB multi-region write costs 2x the RU/s per additional region
- Front Door: ~$35/month base + per-request
- Redis per region: ~$80/month each (Standard C1)
- **Only deploy multi-region for workloads that truly need it** — most apps are fine with single-region + DR

---

## Scenario 29: Microservices Architecture on Azure

### 🎯 Objective
Design and deploy a microservices application following Domain-Driven Design principles. Implement API gateway, inter-service communication, distributed transactions (Saga), circuit breakers, and service mesh.

### 📦 App Description
**A ride-sharing/food-delivery platform with 6+ microservices**: user management, driver/rider matching, order management, payment processing, notification service, and analytics service. Each service has its own database.

### 🏗️ Architecture Diagram
```
                    ┌──────────────────┐
                    │     CLIENTS      │
                    │  (Web + Mobile)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  API MANAGEMENT  │
                    │  (Gateway)       │
                    │  Rate limiting   │
                    │  JWT validation  │
                    │  API versioning  │
                    └────────┬─────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                    AKS CLUSTER / CONTAINER APPS             │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  User    │  │  Order   │  │ Payment  │  │  Driver  │   │
│  │  Service │  │  Service │  │ Service  │  │ Matching │   │
│  │          │  │          │  │          │  │ Service  │   │
│  │ SQL DB   │  │ Cosmos   │  │ SQL DB   │  │ Redis    │   │
│  │ (Users)  │  │ (Orders) │  │ (Txns)   │  │ (Geo)    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │              │         │
│       └──────┬───────┴──────┬───────┴──────┬───────┘         │
│              │              │              │                  │
│       ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐          │
│       │ Service Bus │ │ Event    │ │ Notification│          │
│       │ (Commands)  │ │ Grid     │ │ Service     │          │
│       └─────────────┘ │ (Events) │ │ (Email/SMS) │          │
│                       └──────────┘ └─────────────┘          │
│                                                             │
│  Cross-cutting: Dapr sidecar for service invocation,        │
│  state management, pub/sub, secrets management              │
└─────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Service Design
- [ ] Apply Domain-Driven Design: identify bounded contexts
- [ ] Define API contracts (OpenAPI) between services
- [ ] Choose communication patterns:
  - **Synchronous**: HTTP/gRPC for real-time queries (user lookup, driver availability)
  - **Asynchronous**: Service Bus for commands (place order, process payment)
  - **Events**: Event Grid for notifications (order completed, payment received)
- [ ] Implement database-per-service pattern

#### Part B: Distributed Transactions (Saga Pattern)
- [ ] Implement an Order Saga:
  1. Create order (Order Service)
  2. Reserve inventory (Inventory Service)
  3. Process payment (Payment Service)
  4. Confirm order (Order Service)
  5. Compensating transactions if any step fails (refund, release inventory)
- [ ] Use choreography (event-driven) vs orchestration (central coordinator) approach
- [ ] Implement idempotency for all service operations

```
┌───────────────────────────────────────────────────────────┐
│ SAGA PATTERN (CHOREOGRAPHY):                               │
│                                                           │
│  Order Svc ──► "OrderCreated" event                       │
│       │                                                   │
│       ├──► Inventory Svc listens, reserves stock          │
│       │    Publishes "InventoryReserved"                   │
│       │                                                   │
│       ├──► Payment Svc listens, charges payment           │
│       │    Publishes "PaymentProcessed"                    │
│       │                                                   │
│       └──► Order Svc listens, confirms order              │
│            Publishes "OrderConfirmed"                      │
│                                                           │
│  IF Payment fails:                                        │
│    Payment Svc publishes "PaymentFailed"                   │
│    Inventory Svc listens, releases stock (compensation)    │
│    Order Svc listens, marks order as failed                │
└───────────────────────────────────────────────────────────┘
```

#### Part C: Resilience Patterns
- [ ] Implement circuit breaker (stop calling a failing service)
- [ ] Implement retry with exponential backoff
- [ ] Implement bulkhead (isolate failures to prevent cascading)
- [ ] Implement timeout policies
- [ ] Use Dapr for automatic retry, circuit breaker, and service invocation

#### Part D: Azure Container Apps vs AKS
- [ ] Compare Container Apps (simpler, managed) vs AKS (full control):

```
┌───────────────────────────────────────────────────────────┐
│ CONTAINER APPS vs AKS:                                     │
│                                                           │
│ Container Apps:                                           │
│   ✅ No cluster management                                │
│   ✅ Built-in Dapr, KEDA, Envoy                          │
│   ✅ Scale to zero (pay nothing when idle)               │
│   ✅ Simpler networking and ingress                       │
│   ❌ Less control over infrastructure                     │
│   ❌ Limited to HTTP/TCP ingress                          │
│                                                           │
│ AKS:                                                      │
│   ✅ Full Kubernetes flexibility                          │
│   ✅ Custom networking, storage, GPU workloads            │
│   ✅ Service mesh (Istio, Linkerd)                        │
│   ✅ Windows containers, multi-cluster                    │
│   ❌ Cluster management overhead                          │
│   ❌ Can't scale to zero (minimum 1 node)                │
└───────────────────────────────────────────────────────────┘
```

#### Part E: Service Mesh & Observability
- [ ] Deploy Istio or Linkerd on AKS (if using AKS)
- [ ] Configure mTLS between services (zero-trust within cluster)
- [ ] Implement distributed tracing with Application Insights
- [ ] Use Application Map to visualize service dependencies
- [ ] Set up Azure App Configuration with feature flags for canary deployments

> ⚠️ **DevOps Gotcha:** Service meshes add significant complexity and resource overhead (~100MB RAM per sidecar proxy per pod). If you have 50 pods, that's 5GB of RAM just for sidecars. Only use a service mesh if you actually need mTLS, traffic splitting, or advanced observability. For simpler needs, Dapr or native Azure SDKs are lighter alternatives.

---

## Scenario 30: Event-Driven Architecture & CQRS

### 🎯 Objective
Implement Event Sourcing and CQRS (Command Query Responsibility Segregation). Every state change is an immutable event. Read models are projections built from the event stream.

### 📦 App Description
**A banking/financial ledger application**: every transaction (deposit, withdrawal, transfer) is recorded as an immutable event. Account balances are calculated projections. The audit trail is the event stream itself — it can never be modified or deleted.

### ✅ Hands-on Tasks

#### Part A: Event Sourcing
- [ ] Design events: `AccountCreated`, `MoneyDeposited`, `MoneyWithdrawn`, `TransferInitiated`
- [ ] Store events in Cosmos DB (append-only, partitioned by account ID)
- [ ] Rebuild account balance by replaying events from the event stream
- [ ] Implement snapshots (periodic checkpoints to avoid replaying entire history)

#### Part B: CQRS Implementation
- [ ] Separate Command side (writes to event store) from Query side (reads from projections)
- [ ] Use Cosmos DB Change Feed to project events into read-optimized views
- [ ] Build materialized views:
  - Account balance (projected from all deposit/withdrawal events)
  - Transaction history (last 100 transactions per account)
  - Daily summary (aggregated by day)
- [ ] Use Azure Functions as Change Feed processors

#### Part C: Event Processing Guarantees
- [ ] Implement idempotent event handlers (processing same event twice is safe)
- [ ] Handle out-of-order events (use event timestamps and sequence numbers)
- [ ] Implement the Outbox Pattern for reliable event publishing:
  - Write event to database AND outbox table in same transaction
  - Separate process reads outbox and publishes to Event Grid/Service Bus
  - Mark as published after successful publish
- [ ] Build event replay capability (rebuild any projection from scratch)

#### Part D: Schema Evolution
- [ ] Handle event schema changes (v1 → v2 of an event)
- [ ] Use event upcasting (transform old events to new schema on read)
- [ ] Design events to be forward-compatible (consumers ignore unknown fields)

> ⚠️ **DevOps Gotcha:** Event stores grow FOREVER (that's the point — immutable history). A busy system can generate millions of events per day. Plan for: (1) archiving old events to cheaper storage, (2) snapshot strategy to avoid replaying from the beginning, (3) partitioning strategy that prevents hot partitions. Monitor Cosmos DB RU consumption on the event store container closely.

---

## Scenario 31: Zero-Trust Security Architecture

### 🎯 Objective
Implement a zero-trust architecture where NO component is trusted by default. Every request is authenticated, authorized, and encrypted. No public internet exposure for any backend service.

### 📦 App Description
**A government or defense-grade secure application**: every component (compute, data, networking) is locked down with zero public internet exposure. Access is through Bastion only. All PaaS services use Private Endpoints.

### 🏗️ Architecture Diagram
```
                    ┌──────────────┐
                    │   INTERNET   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Front Door  │
                    │  (WAF + DDoS)│
                    └──────┬───────┘
                           │ Only HTTPS
                    ┌──────▼───────┐
                    │  App Gateway │
                    │  (End-to-End │
                    │   SSL/mTLS)  │
                    └──────┬───────┘
                           │
┌──────────────────────────┴───────────────────────────────┐
│            FULLY PRIVATE VNet (No Public IPs)             │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │ App Service (Private Endpoint + VNet Integration)│     │
│  │ Managed Identity → Key Vault, SQL, Storage       │     │
│  │ No secrets in code. No public IP.                │     │
│  └──────────────────────┬──────────────────────────┘     │
│                         │ Private Endpoints only          │
│  ┌──────────┐  ┌────────┴───┐  ┌──────────┐             │
│  │ Key Vault│  │  Azure SQL │  │ Storage  │             │
│  │ (Private)│  │  (Private) │  │ (Private)│             │
│  │ RBAC only│  │ Always Enc.│  │ CMK Enc. │             │
│  │ Firewall │  │ Auditing   │  │ WORM     │             │
│  └──────────┘  └────────────┘  └──────────┘             │
│                                                          │
│  Azure Bastion ──► Jump Box (only way to access VMs)     │
│  JIT VM Access (Defender for Cloud)                      │
│  NSG: Default deny all, explicit allow per service       │
│                                                          │
│  Sentinel: SIEM monitoring all activity                   │
│  Defender for Cloud: Secure Score > 90%                  │
└──────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Network Zero Trust
- [ ] Deploy ALL PaaS services with Private Endpoints (SQL, Storage, Key Vault, ACR, Service Bus)
- [ ] Disable ALL public access on PaaS services
- [ ] Create Private DNS Zones for every Private Endpoint service
- [ ] Configure centralized DNS forwarding for hub-spoke topology
- [ ] Set NSG default: deny all inbound + outbound, then whitelist specific flows
- [ ] Deploy Azure Firewall for outbound traffic inspection

#### Part B: Identity Zero Trust
- [ ] Use Managed Identity for ALL service-to-service communication (zero secrets)
- [ ] Enable Azure AD Conditional Access with continuous access evaluation (CAE)
- [ ] Configure PIM for just-in-time admin access
- [ ] Set up JIT VM access (approve VM SSH/RDP access, auto-expire after 3 hours)
- [ ] Implement MFA for all users (no exceptions)

#### Part C: Data Zero Trust
- [ ] Enable Always Encrypted on SQL columns containing PII
- [ ] Configure Customer Managed Keys (CMK) for Storage encryption
- [ ] Enable immutable storage (WORM) for audit logs
- [ ] Set up Microsoft Purview for data classification and sensitivity labels
- [ ] Configure TLS 1.2+ everywhere, mTLS between services

#### Part D: Monitoring Zero Trust
- [ ] Enable Defender for Cloud on all services, achieve Secure Score > 90%
- [ ] Deploy Microsoft Sentinel for SIEM
- [ ] Create analytics rules for detecting anomalous behavior
- [ ] Set up automated response playbooks (auto-block compromised accounts)
- [ ] Configure Azure AD sign-in risk policies

> ⚠️ **DevOps Gotcha:** Zero-trust networking is complex to debug. When everything is private + firewalled + NSG'd, troubleshooting connectivity issues becomes a multi-layer investigation. Build a debugging checklist: (1) NSG flow logs, (2) DNS resolution (`nslookup`), (3) Firewall logs, (4) Private DNS zone records, (5) VNet integration status, (6) Managed Identity permissions. Without this systematic approach, you'll spend hours guessing.

---

## Scenario 32: Migration to Azure

### 🎯 Objective
Migrate a legacy on-premises application to Azure using a structured approach: assess, plan, migrate, optimize. Practice different migration strategies.

### 📦 App Description
**A legacy monolithic application (3-tier: IIS + .NET Framework + SQL Server)** running "on-premises" (simulated with VMs). Migrate it to Azure using multiple strategies: lift-and-shift, re-platform, and re-architect.

### ✅ Hands-on Tasks

#### Part A: Assessment
- [ ] Deploy Azure Migrate appliance (or use agentless discovery)
- [ ] Discover and assess on-premises workloads
- [ ] Review assessment report: VM sizing, cost estimates, compatibility issues
- [ ] Identify migration strategy per component:

```
┌───────────────────────────────────────────────────────────┐
│ MIGRATION STRATEGIES (5 R's):                              │
│                                                           │
│ Rehost (Lift-and-Shift):                                  │
│   Move VMs as-is to Azure. Fastest, minimal changes.     │
│   Tools: Azure Migrate, ASR                               │
│                                                           │
│ Replatform (Lift-Tinker-Shift):                            │
│   Move with minor optimizations (VM → App Service,       │
│   SQL Server → Azure SQL). Moderate effort, good gains.   │
│                                                           │
│ Refactor (Re-architect):                                   │
│   Redesign for cloud-native (containers, serverless,      │
│   microservices). Most effort, best long-term outcome.    │
│                                                           │
│ Rebuild:                                                   │
│   Rewrite from scratch on cloud-native. Nuclear option.   │
│                                                           │
│ Replace:                                                   │
│   Use SaaS instead of custom software.                    │
└───────────────────────────────────────────────────────────┘
```

#### Part B: Database Migration
- [ ] Use Azure Database Migration Service (DMS) to migrate SQL Server → Azure SQL
- [ ] Perform online migration (minimal downtime)
- [ ] Validate data integrity after migration
- [ ] Handle schema compatibility issues (deprecated features, CLR types)

#### Part C: Application Migration
- [ ] Lift-and-shift: Use ASR to replicate VMs to Azure
- [ ] Re-platform: Move the .NET app to Azure App Service
- [ ] Containerize: Use Azure Migrate App Containerization to create Docker images
- [ ] Configure DNS cutover plan with minimal downtime

#### Part D: Post-Migration
- [ ] Right-size VMs based on actual usage (Azure Advisor)
- [ ] Implement monitoring (App Insights, Azure Monitor)
- [ ] Set up backup and DR in Azure
- [ ] Optimize costs (reservations, right-sizing, PaaS migration)
- [ ] Document lessons learned and create migration playbook

> ⚠️ **DevOps Gotcha:** The #1 migration risk is **DNS cutover**. When you switch DNS from on-prem to Azure, there's a propagation period where some users hit the old system and some hit the new one. If the old and new systems have separate databases, you can get data inconsistency. Use database replication (DMS online mode) to keep both in sync until cutover is complete, then disable the old system.

---

## Scenario 33: Azure Landing Zone & Enterprise-Scale

### 🎯 Objective
Set up a complete enterprise Azure environment following the Cloud Adoption Framework (CAF). Design management group hierarchy, connectivity, identity, management, and landing zone subscriptions with policy-driven governance.

### 📦 App Description
**A complete enterprise Azure environment** from scratch — multiple "teams" deploying different applications into their landing zones. Platform team manages shared infrastructure; application teams have autonomy within guardrails.

### 🏗️ Architecture Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                    MANAGEMENT GROUPS                           │
│                                                              │
│  Root                                                         │
│  ├── Platform                                                 │
│  │   ├── Connectivity                                         │
│  │   │   └── Hub VNet, Azure Firewall, DNS, VPN Gateway      │
│  │   ├── Identity                                             │
│  │   │   └── Azure AD DS, Domain Controllers                 │
│  │   └── Management                                           │
│  │       └── Log Analytics, Automation, Backup               │
│  │                                                            │
│  ├── Landing Zones                                            │
│  │   ├── Corp (Internal Apps)                                 │
│  │   │   ├── App-Team-A (their subscription)                 │
│  │   │   │   └── Spoke VNet peered to Hub                    │
│  │   │   │   └── App Service, SQL, Storage                   │
│  │   │   └── App-Team-B (their subscription)                 │
│  │   │       └── Spoke VNet peered to Hub                    │
│  │   │       └── AKS, Cosmos DB, Redis                       │
│  │   └── Online (Internet-facing)                            │
│  │       └── Public-facing apps with Front Door              │
│  │                                                            │
│  ├── Sandbox                                                  │
│  │   └── Relaxed policies, dev/experiment                    │
│  │                                                            │
│  └── Decommissioned                                           │
│      └── Locked down, read-only                              │
│                                                              │
│  POLICIES APPLIED AT EACH LEVEL:                              │
│  Root:        Require tags, audit logging                     │
│  Platform:    Specific allowed resources                      │
│  Landing Zones: Deny public IPs, require encryption          │
│  Sandbox:     Allowed regions only                            │
└──────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

- [ ] Design management group hierarchy following CAF
- [ ] Deploy connectivity subscription (hub VNet, Azure Firewall, DNS, VPN)
- [ ] Deploy management subscription (Log Analytics, Automation)
- [ ] Create landing zone subscriptions with policy guardrails
- [ ] Implement subscription vending (automated new subscription provisioning)
- [ ] Set up hub-spoke network with centralized DNS
- [ ] Configure policy initiatives at each management group level
- [ ] Implement monitoring baseline (all resources → central Log Analytics)
- [ ] Document platform team vs application team responsibilities

> ⚠️ **DevOps Gotcha:** Landing Zones are complex — don't build from scratch. Use the **Azure Landing Zone Accelerator** (terraform-azurerm-caf-enterprise-scale module or Bicep module) as a starting point. It implements CAF best practices. Customize from there rather than reinventing the wheel.

---

## Scenario 34: Performance Testing & Chaos Engineering

### 🎯 Objective
Validate application resilience through load testing and chaos experiments. Establish performance baselines, identify bottlenecks, and verify auto-scale and failover mechanisms.

### 📦 App Description
**Take any previous scenario's deployed application** and subject it to load testing (are you fast enough?) and chaos engineering (do you survive failures?).

### ✅ Hands-on Tasks

#### Part A: Azure Load Testing
- [ ] Create an Azure Load Testing resource
- [ ] Upload a JMeter test plan (or create a URL-based test)
- [ ] Establish performance baselines: P50, P95, P99 latency, throughput
- [ ] Ramp test: gradually increase load from 10 to 1000 concurrent users
- [ ] Identify bottlenecks: CPU, memory, database, network
- [ ] Validate auto-scale: verify AKS/App Service scales under load
- [ ] Compare performance before and after caching (Redis)
- [ ] Integrate load tests into CI/CD pipeline (fail deployment if P99 > threshold)

> ⚠️ **DevOps Gotcha:** Load testing can accidentally DDoS your own infrastructure and downstream dependencies. Start with low load and gradually increase. If you're testing against production, use a separate backend or test database. Also, Azure Load Testing generates traffic FROM Azure — your app's NSG/firewall must allow the load testing IP ranges.

#### Part B: Azure Chaos Studio
- [ ] Create Chaos Studio experiments:
  - **VM Shutdown**: Kill a VM and verify the app continues serving traffic
  - **Network Delay**: Add 200ms latency to a VM's network and verify degraded but functional performance
  - **DNS Failure**: Disrupt DNS resolution and verify the app handles it gracefully
  - **AKS Pod Failure**: Kill pods and verify Kubernetes restarts them quickly
  - **Disk I/O Pressure**: Saturate disk I/O and verify the app remains responsive
- [ ] Define steady-state hypothesis: "During the experiment, error rate stays below 1% and P99 < 3 seconds"
- [ ] Monitor Application Insights during chaos experiments
- [ ] Document findings: which failures did the app handle? Which caused outages?
- [ ] Fix identified resilience gaps and re-test

#### Part C: Game Days
- [ ] Plan a team Game Day: scheduled 2-hour chaos event
- [ ] Run experiments while monitoring dashboards
- [ ] Practice incident response procedures
- [ ] Document: what broke, why, how to fix, how to prevent
- [ ] Create improvement backlog from Game Day findings

```
┌───────────────────────────────────────────────────────────┐
│ CHAOS ENGINEERING PRINCIPLES:                              │
│                                                           │
│ 1. Define steady state: what does "healthy" look like?    │
│ 2. Hypothesize: "the system will handle X failure"        │
│ 3. Run experiment: inject the failure                     │
│ 4. Observe: did the hypothesis hold?                      │
│ 5. Learn: fix gaps and improve resilience                 │
│                                                           │
│ RULES:                                                    │
│ • Start in non-production environments                    │
│ • Minimize blast radius (affect one component at a time)  │
│ • Have a rollback plan (abort button)                     │
│ • Run during business hours (people available to respond) │
│ • Document everything                                     │
└───────────────────────────────────────────────────────────┘
```

> ⚠️ **DevOps Gotcha:** Chaos experiments in production require buy-in from management and the team. Never run chaos experiments without: (1) a rollback plan, (2) monitoring dashboards visible, (3) team members on standby, (4) blast radius limited to one component. Start in dev/test and only graduate to production after proving the app handles failures correctly in lower environments.

### 💰 Cost Tips
- Azure Load Testing: ~$10 per test hour per engine (use 1-2 engines for learning)
- Chaos Studio: Free for the service; you pay for target resources
- Run tests during off-peak hours on dev/test environments
- Delete load testing resources when not actively testing

---

## 🎓 Learning Path Summary

| # | Scenario | Difficulty | Est. Time | Key Azure Services | Certification |
|---|----------|------------|-----------|--------------------|-|
| 1 | Subscription & Resource Group Strategy | Beginner | 2-3 days | Resource Groups, RBAC, Policy, Tags | AZ-900, AZ-104 |
| 2 | Virtual Machine Deep Dive | Beginner | 2-3 days | VMs, Disks, Bastion, Backup | AZ-104 |
| 3 | Azure Networking Fundamentals | Beginner | 3-4 days | VNet, NSG, Peering, DNS, Private EP | AZ-104, AZ-700 |
| 4 | Azure Storage Deep Dive | Beginner | 2-3 days | Blob, Files, SAS, Lifecycle | AZ-104, AZ-204 |
| 5 | Azure App Service Fundamentals | Beginner | 2-3 days | App Service, Slots, Scaling | AZ-104, AZ-204 |
| 6 | Azure AD (Entra ID) Deep Dive | Intermediate | 3-4 days | Entra ID, OAuth, Managed Identity | AZ-104, SC-300 |
| 7 | Azure Key Vault Mastery | Intermediate | 2-3 days | Key Vault, Managed Identity | AZ-204, AZ-305 |
| 8 | Azure Firewall & Network Security | Intermediate | 3-4 days | Firewall, WAF, Private Link, DDoS | AZ-700, AZ-305 |
| 9 | Load Balancing & Traffic Management | Intermediate | 2-3 days | LB, App GW, Front Door, Traffic Mgr | AZ-700, AZ-305 |
| 10 | VPN Gateway & ExpressRoute | Intermediate | 2-3 days | VPN GW, ExpressRoute, Virtual WAN | AZ-700 |
| 11 | ACR & ACI | Intermediate | 2-3 days | ACR, ACI, Defender for Containers | AZ-204 |
| 12 | AKS Fundamentals | Intermediate | 3-4 days | AKS, kubectl, Ingress, Storage | AZ-204, AZ-305 |
| 13 | AKS Advanced | Advanced | 3-4 days | AKS, Workload ID, GitOps, Policy | AZ-305, AZ-400 |
| 14 | Azure SQL & Cosmos DB | Intermediate | 3-4 days | SQL, Cosmos DB, Failover Groups | AZ-204, AZ-305 |
| 15 | Messaging & Event-Driven | Intermediate | 2-3 days | Service Bus, Event Hubs, Event Grid | AZ-204, AZ-305 |
| 16 | Redis Cache & CDN | Intermediate | 2 days | Redis, CDN | AZ-204 |
| 17 | Azure Functions Deep Dive | Intermediate | 3-4 days | Functions, Durable Functions | AZ-204 |
| 18 | Logic Apps & Integration | Intermediate | 2-3 days | Logic Apps, APIM | AZ-204, AZ-305 |
| 19 | Azure DevOps CI/CD | Intermediate | 3-4 days | Azure DevOps, Pipelines, Repos | AZ-400 |
| 20 | GitHub Actions for Azure | Intermediate | 2-3 days | GitHub Actions, OIDC | AZ-400 |
| 21 | Bicep IaC | Intermediate | 2-3 days | Bicep, ARM, Deployment Stacks | AZ-104, AZ-400 |
| 22 | Terraform on Azure | Intermediate | 2-3 days | Terraform, AzureRM | AZ-400 |
| 23 | Azure Monitor & App Insights | Intermediate | 3-4 days | Monitor, App Insights, KQL, Alerts | AZ-104, AZ-204 |
| 24 | Azure Governance at Scale | Advanced | 2-3 days | Policy, Resource Graph, Defender | AZ-104, AZ-305 |
| 25 | Cost Management & Optimization | Intermediate | 2 days | Cost Management, Advisor, Reservations | AZ-104, AZ-305 |
| 26 | Logging, Auditing & Compliance | Advanced | 3-4 days | Sentinel, Log Analytics, Purview | AZ-305, SC-200 |
| 27 | Azure Backup & Site Recovery | Intermediate | 2-3 days | Backup, ASR, Failover Groups | AZ-104, AZ-305 |
| 28 | Multi-Region Active-Active | Advanced | 3-4 days | Front Door, Cosmos DB, SQL FG | AZ-305 |
| 29 | Microservices on Azure | Advanced | 4-5 days | AKS/Container Apps, APIM, Service Bus | AZ-204, AZ-305 |
| 30 | Event-Driven & CQRS | Advanced | 3-4 days | Event Hubs, Cosmos DB, Functions | AZ-204, AZ-305 |
| 31 | Zero-Trust Security | Advanced | 3-4 days | Private Link, MI, Defender, Sentinel | AZ-305, SC-100 |
| 32 | Migration to Azure | Advanced | 3-4 days | Azure Migrate, DMS, ASR | AZ-104, AZ-305 |
| 33 | Azure Landing Zone | Advanced | 3-4 days | MGs, Policy, CAF, Hub-Spoke | AZ-305 |
| 34 | Perf Testing & Chaos Engineering | Advanced | 2-3 days | Load Testing, Chaos Studio | AZ-305, AZ-400 |

**Total Estimated Time: 85–115 days** (working through all 34 scenarios at a thorough pace)

---

## 📚 Recommended Certification Path

### Path 1: Cloud Fundamentals
```
AZ-900 (Azure Fundamentals)
  └── Scenarios: 1, 2, 3, 4, 5 (Batch 1)
  └── Study: 1-2 weeks
  └── Cost: $165 exam fee
```

### Path 2: Azure Administrator
```
AZ-104 (Azure Administrator Associate)
  └── Scenarios: 1-5, 6, 7, 21, 23, 24, 25, 27, 32
  └── Study: 4-8 weeks
  └── Prerequisites: AZ-900 recommended
  └── Key skills: VMs, networking, storage, identity, monitoring, governance
```

### Path 3: Azure Developer
```
AZ-204 (Azure Developer Associate)
  └── Scenarios: 4, 5, 7, 11, 12, 14, 15, 16, 17, 18, 23, 29, 30
  └── Study: 4-8 weeks
  └── Key skills: App Service, Functions, Cosmos DB, messaging, caching, containers
```

### Path 4: Azure Solutions Architect
```
AZ-305 (Azure Solutions Architect Expert)
  └── Scenarios: 7, 8, 9, 12, 14, 15, 18, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33
  └── Study: 6-10 weeks
  └── Prerequisites: AZ-104 or AZ-204
  └── Key skills: Architecture design, trade-offs, multi-region, security, governance
```

### Path 5: DevOps Engineer
```
AZ-400 (Azure DevOps Engineer Expert)
  └── Scenarios: 13, 19, 20, 21, 22, 34
  └── Study: 4-8 weeks
  └── Prerequisites: AZ-104 or AZ-204
  └── Key skills: CI/CD, IaC, monitoring, testing, release management
```

### Path 6: Azure Network Engineer
```
AZ-700 (Azure Network Engineer Associate)
  └── Scenarios: 3, 8, 9, 10
  └── Study: 4-6 weeks
  └── Key skills: VNets, load balancing, firewalls, VPN, ExpressRoute
```

### Recommended Order
```
AZ-900 → AZ-104 → AZ-204 → AZ-305 → AZ-400
  │         │         │         │         │
  └─ 2wk ──└─ 2mo ──└─ 2mo ──└─ 2mo ──└─ 2mo
  
  Total: ~10 months for all 5 certifications
```

---

## 🏆 Final Notes

Completing all 34 scenarios will give you hands-on experience with virtually every Azure service used in production. Remember:

1. **Practice manually first** — understand what the portal does before automating
2. **Break things intentionally** — the best learning happens when things fail
3. **Document everything** — create your own runbooks and troubleshooting guides
4. **Delete resources after each scenario** — Azure bills add up fast
5. **Join the community** — Azure subreddit, Microsoft Q&A, and local user groups

**You've got this. Now go build something amazing on Azure.** 🚀
