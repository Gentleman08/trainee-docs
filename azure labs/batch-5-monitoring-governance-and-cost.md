# 🔷 Batch 5: Monitoring, Governance & Cost Management

> **Level:** Intermediate–Advanced | **Estimated Total Time:** 12–15 days | **Scenarios:** 5 (numbered 23–27)
>
> This batch covers the operational skills that keep Azure environments healthy, compliant, and cost-effective. These are the skills that matter most in production — and the ones most often neglected until something goes wrong.

---

## 📑 Table of Contents

- [Scenario 23: Azure Monitor & Application Insights](#scenario-23-azure-monitor--application-insights)
- [Scenario 24: Azure Governance at Scale](#scenario-24-azure-governance-at-scale)
- [Scenario 25: Cost Management & Optimization](#scenario-25-cost-management--optimization)
- [Scenario 26: Logging, Auditing & Compliance](#scenario-26-logging-auditing--compliance)
- [Scenario 27: Azure Backup & Site Recovery](#scenario-27-azure-backup--site-recovery)

---

## Scenario 23: Azure Monitor & Application Insights

### 🎯 Objective
Implement comprehensive observability: metrics, logs, traces, alerts, and dashboards. Master KQL (Kusto Query Language) for log analysis and troubleshooting. Set up intelligent alerting that reduces noise and catches real issues.

### 📦 App Description
**A microservices-based order processing system** (from previous batches) where you need to trace requests across services, identify bottlenecks, measure latency percentiles, and set up alerting that pages you for real problems, not noise.

### 🏗️ Architecture Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                    AZURE MONITOR                              │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐     │
│  │           LOG ANALYTICS WORKSPACE                    │     │
│  │         "law-prod-eastus-001"                        │     │
│  │                                                      │     │
│  │  Tables:                                             │     │
│  │  • AppRequests (HTTP requests)                       │     │
│  │  • AppDependencies (outbound calls)                  │     │
│  │  • AppExceptions (errors)                            │     │
│  │  • AppTraces (custom logs)                           │     │
│  │  • AppMetrics (custom metrics)                       │     │
│  │  • AzureActivity (control plane operations)          │     │
│  │  • AzureDiagnostics (resource logs)                  │     │
│  │  • Perf (VM performance counters)                    │     │
│  │  • Heartbeat (agent health)                          │     │
│  └─────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐   │
│  │ APP INSIGHTS   │  │ METRICS        │  │ ALERTS        │   │
│  │ (per service)  │  │ EXPLORER       │  │               │   │
│  │                │  │                │  │ • CPU > 80%   │   │
│  │ • App Map      │  │ • CPU/Memory   │  │ • Errors > 5% │   │
│  │ • Live Metrics │  │ • Requests/sec │  │ • Latency P99 │   │
│  │ • Failures     │  │ • Custom       │  │   > 2 sec     │   │
│  │ • Performance  │  │   metrics      │  │ • DLQ depth   │   │
│  │ • Availability │  │                │  │   > 100       │   │
│  └────────────────┘  └────────────────┘  └───────┬───────┘   │
│                                                   │           │
│                                          ┌────────▼────────┐  │
│                                          │  ACTION GROUPS  │  │
│                                          │                 │  │
│                                          │ • Email team    │  │
│                                          │ • SMS on-call   │  │
│                                          │ • Teams webhook │  │
│                                          │ • PagerDuty     │  │
│                                          │ • Auto-scale    │  │
│                                          │ • Logic App     │  │
│                                          └─────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Application Insights Setup
- [ ] Add Application Insights SDK to your application (or use auto-instrumentation)
- [ ] Use **connection string** (not instrumentation key — IK is deprecated)
- [ ] View the Application Map — see all dependencies visualized
- [ ] Use Live Metrics Stream for real-time debugging
- [ ] Configure availability tests (URL ping test from 5+ locations)
- [ ] Set up custom events and metrics in your code
- [ ] Enable distributed tracing across microservices (W3C Trace Context)

> ⚠️ **DevOps Gotcha:** Application Insights uses **sampling** by default to control costs. Adaptive sampling may DROP telemetry during high-volume periods. If you're debugging a specific issue and can't find the traces, sampling might be hiding them. Temporarily set `MaxTelemetryItemsPerSecond` to a high value, or use `TelemetryClient.TrackEvent()` with sampling excluded for critical events.

#### Part B: KQL (Kusto Query Language) — The Power Tool
- [ ] Learn KQL fundamentals — this is THE skill for Azure operations:

```kusto
// 1. Top 10 slowest requests in the last 24 hours
requests
| where timestamp > ago(24h)
| top 10 by duration desc
| project timestamp, name, duration, resultCode, cloud_RoleInstance

// 2. Error rate by endpoint
requests
| where timestamp > ago(1h)
| summarize totalRequests = count(), failedRequests = countif(success == false) by name
| extend errorRate = round(failedRequests * 100.0 / totalRequests, 2)
| order by errorRate desc

// 3. P50, P95, P99 latency per endpoint
requests
| where timestamp > ago(1h)
| summarize percentiles(duration, 50, 95, 99) by name
| order by percentile_duration_99 desc

// 4. Dependency failures (database, API calls)
dependencies
| where timestamp > ago(1h) and success == false
| summarize count() by target, type, resultCode
| order by count_ desc

// 5. Exceptions with stack traces
exceptions
| where timestamp > ago(24h)
| summarize count() by type, outerMessage
| order by count_ desc

// 6. Trace end-to-end request across services
union requests, dependencies, traces
| where operation_Id == "specific-operation-id"
| order by timestamp asc
| project timestamp, itemType, name, duration, success

// 7. Active users by hour
customEvents
| where timestamp > ago(7d) and name == "PageView"
| summarize dcount(user_Id) by bin(timestamp, 1h)
| render timechart

// 8. Resource utilization from VM performance counters
Perf
| where CounterName == "% Processor Time" and InstanceName == "_Total"
| summarize avg(CounterValue) by Computer, bin(TimeGenerated, 5m)
| render timechart

// 9. Azure Activity Log - who deleted resources?
AzureActivity
| where OperationNameValue endswith "DELETE" and ActivityStatusValue == "Success"
| project TimeGenerated, Caller, OperationNameValue, ResourceGroup, _ResourceId

// 10. Cross-service correlation - find slow downstream calls
requests
| where duration > 5000  // requests over 5 seconds
| join kind=inner (
    dependencies
    | where duration > 2000
) on operation_Id
| project requestName = name, requestDuration = duration, 
          depTarget = target1, depDuration = duration1, depType = type1
```

> ⚠️ **DevOps Gotcha:** KQL queries in Log Analytics have a **30-second timeout** for interactive queries and scan limits. Queries over large time ranges (months) or with heavy joins can timeout. Use `| where timestamp > ago(...)` to narrow the time range FIRST, then filter further. Also, `take` is faster than `top` for quick sampling.

#### Part C: Alerts & Action Groups
- [ ] Create **metric alerts**: CPU > 80% for 5 minutes
- [ ] Create **log alerts**: error rate > 5% in 15-minute window
- [ ] Create **activity log alerts**: resource deleted in production RG
- [ ] Configure **dynamic threshold** alerts (AI-based baseline detection)
- [ ] Set up Action Groups: email, SMS, Teams webhook, PagerDuty
- [ ] Create an auto-scale action triggered by metric alert

> ⚠️ **DevOps Gotcha:** Alert fatigue is REAL. If you alert on everything (CPU > 50%, any 4xx error, any slow request), your team will start ignoring alerts. Only alert on **actionable conditions**: 5xx error rate spike, P99 latency above SLA, disk space < 10%, DLQ depth growing. Use dynamic thresholds to reduce false positives from normal traffic patterns.

#### Part D: Workbooks & Dashboards
- [ ] Create a Workbook with KQL queries for operational dashboard
- [ ] Pin key metrics to an Azure Dashboard
- [ ] Create a shared dashboard for the team
- [ ] Set up automatic reports via scheduled Logic App + KQL query

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Telemetry missing for some requests | Adaptive sampling dropping data | Increase sampling rate; exclude critical events |
| KQL query timeout | Too broad time range or heavy joins | Narrow time range; use `summarize` to reduce data first |
| Alert firing too often (flapping) | Threshold too sensitive | Add evaluation window (5 min); use dynamic thresholds |
| Log Analytics costs exploding | Verbose logging from all resources | Set diagnostic settings to specific categories; use Basic logs tier |
| Distributed traces missing | SDK not configured for W3C trace propagation | Verify all services use compatible App Insights SDK |
| Connection string vs IK confusion | Using deprecated instrumentation key | Migrate to connection string (`APPLICATIONINSIGHTS_CONNECTION_STRING`) |

### 💰 Cost Tips
- App Insights: first 5GB/month FREE, then ~$2.30/GB
- Log Analytics: first 5GB/month FREE, then ~$2.30/GB
- **The #1 cost trap**: verbose diagnostic logging can cost $100s/month — configure selectively
- Use **Basic logs tier** for high-volume tables (70% cheaper, limited query capabilities)
- Metric alerts: ~$0.10/month each (cheap)
- Log alerts: ~$1.50/month each (slightly more)
- Archive old logs to cheaper storage after 30 days

---

## Scenario 24: Azure Governance at Scale

### 🎯 Objective
Implement enterprise-grade governance using Management Groups, Azure Policy, Resource Graph, and Microsoft Defender for Cloud. Enforce compliance at scale without slowing down development teams.

### 📦 App Description
**A simulated enterprise environment** with multiple resource groups (simulating subscriptions) for different teams: Platform, App-Team-A, App-Team-B. Enforce naming conventions, required tags, allowed regions, security baselines, and cost controls via policy.

### ✅ Hands-on Tasks

#### Part A: Management Group Hierarchy
- [ ] Design a hierarchy:
```
Root Management Group
├── Platform
│   ├── Connectivity (hub VNet, Firewall, DNS)
│   ├── Identity (Azure AD DS, domain controllers)
│   └── Management (Log Analytics, Automation, Backup)
├── Landing Zones
│   ├── Corp (internal apps)
│   │   ├── App-Team-A subscription
│   │   └── App-Team-B subscription
│   └── Online (internet-facing apps)
├── Sandbox (dev/experiment, relaxed policies)
└── Decommissioned (locked down)
```
- [ ] Create this hierarchy using `az account management-group`

#### Part B: Azure Policy Deep Dive
- [ ] Understand and implement ALL policy effects:

```
┌───────────────────────────────────────────────────────────┐
│ POLICY EFFECTS:                                            │
│                                                           │
│ Deny:              Block non-compliant create/update      │
│ Audit:             Allow but log non-compliance           │
│ Append:            Add fields (e.g., add tags)            │
│ Modify:            Change resource properties             │
│ DeployIfNotExists: Auto-deploy related resources          │
│                    (e.g., deploy diagnostic settings)      │
│ AuditIfNotExists:  Audit if related resource missing      │
│ Disabled:          Turn off policy without removing        │
│ Manual:            Requires manual compliance attestation  │
└───────────────────────────────────────────────────────────┘
```

- [ ] Assign built-in policies: required tags, allowed regions, allowed VM SKUs
- [ ] Create a custom policy: "Deny storage accounts without HTTPS-only"
- [ ] Create a policy initiative (policy set) combining 5+ related policies
- [ ] Set up remediation tasks for non-compliant resources
- [ ] Create policy exemptions with expiry dates
- [ ] Use `DeployIfNotExists` to auto-deploy diagnostic settings on all new resources

> ⚠️ **DevOps Gotcha:** `DeployIfNotExists` requires a **Managed Identity** to perform the deployment. When you assign a DINE policy, Azure creates an MI, but you must grant it the necessary RBAC roles at the correct scope. If the MI doesn't have permission, the remediation silently fails. Check the policy assignment's MI and its role assignments.

#### Part C: Azure Resource Graph
- [ ] Write Resource Graph queries to audit compliance:
```kusto
// Find all VMs without the 'env' tag
Resources
| where type =~ 'Microsoft.Compute/virtualMachines'
| where tags !has 'env'
| project name, resourceGroup, location, subscriptionId

// Find public IP addresses (security audit)
Resources
| where type =~ 'Microsoft.Network/publicIPAddresses'
| project name, resourceGroup, properties.ipAddress, properties.publicIPAllocationMethod

// Count resources by type across all subscriptions
Resources
| summarize count() by type
| order by count_ desc
| take 20

// Find storage accounts with public access enabled
Resources
| where type =~ 'Microsoft.Storage/storageAccounts'
| where properties.allowBlobPublicAccess == true
| project name, resourceGroup, location
```

#### Part D: Microsoft Defender for Cloud
- [ ] Review Secure Score and recommendations
- [ ] Enable Defender plans for: App Service, SQL, Storage, Key Vault, Containers
- [ ] Implement top 5 security recommendations
- [ ] Configure regulatory compliance dashboards (PCI-DSS, ISO 27001)
- [ ] Set up adaptive application controls and just-in-time VM access

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Policy evaluation delay | New policy takes up to 30 min to evaluate | Trigger manual scan: `az policy state trigger-scan` |
| DINE remediation fails | MI lacks RBAC permissions | Grant MI the required role at the policy scope |
| Policy blocks legitimate deployments | Policy too restrictive | Create exemption (with expiry!) or adjust policy parameters |
| Policy conflicts between MG levels | Child policy contradicts parent | Lower-scope policies take precedence; review hierarchy |
| Resource Graph query returns stale data | Data freshness depends on resource type | RG is near-real-time for most resources but not instant |

### 💰 Cost Tips
- Azure Policy: **FREE** — no cost for policy assignments and evaluations
- Resource Graph: **FREE** — no cost for queries
- Defender for Cloud: Free tier (Secure Score, recommendations), paid per workload plan
- Management Groups: **FREE**

---

## Scenario 25: Cost Management & Optimization

### 🎯 Objective
Implement FinOps practices: understand your Azure bill, set budgets, optimize costs with reservations and savings plans, eliminate waste, and build a cost-conscious culture.

### 📦 App Description
**Take any previous scenario's infrastructure** and optimize it for cost. Document before/after costs, implement all applicable savings, and set up ongoing cost governance.

### ✅ Hands-on Tasks

#### Part A: Understand Your Bill
- [ ] Open Cost Management → Cost Analysis
- [ ] View costs by: resource group, resource type, tag, location
- [ ] Create custom cost views and pin to dashboards
- [ ] Export cost data to Storage Account for analysis
- [ ] Review Azure Advisor cost recommendations

#### Part B: Budgets & Alerts
- [ ] Create budgets at subscription and resource group level
- [ ] Set alerts at 50%, 80%, 100%, 120% of budget
- [ ] Configure alert actions: email, webhook, Logic App
- [ ] Set up anomaly detection alerts (unusual spending patterns)

#### Part C: Savings Mechanisms
```
┌───────────────────────────────────────────────────────────┐
│ SAVINGS COMPARISON:                                        │
│                                                           │
│ Pay-as-you-go:     Full price, no commitment              │
│ Reservations:      1yr (20-40% off) or 3yr (40-60% off)  │
│                    Locked to specific resource type/size   │
│ Savings Plans:     1yr or 3yr, $/hr commitment            │
│                    Flexible across regions and sizes       │
│ Spot VMs:          Up to 90% off, can be evicted          │
│                    Good for: batch, dev/test, fault-tolerant│
│ Hybrid Benefit:    Bring existing Windows/SQL licenses     │
│                    Save 40-55% on VMs and SQL              │
│ Dev/Test Pricing:  Discounted rates for dev/test subs     │
│                    No Windows license charges on VMs       │
└───────────────────────────────────────────────────────────┘
```

- [ ] Calculate potential savings from Reservations for your most-used VMs
- [ ] Evaluate Savings Plans vs Reservations for your workload
- [ ] Enable Azure Hybrid Benefit on eligible VMs and SQL databases
- [ ] Identify and shut down/resize underutilized resources (right-sizing)

#### Part D: Eliminate Waste
- [ ] Find orphaned resources: unattached disks, unused public IPs, empty NSGs
- [ ] Set up auto-shutdown for dev/test VMs
- [ ] Use AKS stop/start for non-production clusters
- [ ] Configure SQL and Cosmos DB serverless auto-pause
- [ ] Optimize storage with lifecycle policies (Hot → Cool → Archive)
- [ ] Review and optimize data egress (cross-region, internet)

```kusto
// Resource Graph query: Find orphaned disks
Resources
| where type =~ 'Microsoft.Compute/disks'
| where managedBy == ""
| project name, resourceGroup, properties.diskSizeGB, properties.diskState
```

> ⚠️ **DevOps Gotcha:** The sneakiest Azure cost: **data egress**. Data leaving Azure (to internet or between regions) is charged at $0.087/GB for the first 10TB. An application serving 10TB/month of content (images, videos, API responses) would cost $870/month JUST in egress. Use CDN, compress responses, and cache aggressively to reduce egress.

### 💰 Quick Wins Checklist
- [ ] Auto-shutdown on all dev/test VMs (save 60%)
- [ ] Right-size VMs based on CPU/memory utilization (save 20-40%)
- [ ] Delete orphaned disks and unused public IPs
- [ ] Reservations for 24/7 production VMs (save 30-60%)
- [ ] Azure Hybrid Benefit for Windows/SQL workloads (save 40-55%)
- [ ] Storage lifecycle policies (save 60-90% on old data)
- [ ] Spot VMs for fault-tolerant batch workloads (save 60-90%)
- [ ] AKS stop/start for non-production (save 60%)

---

## Scenario 26: Logging, Auditing & Compliance

### 🎯 Objective
Implement enterprise-grade logging, security monitoring with Sentinel (SIEM), and regulatory compliance dashboards. Every action should be auditable.

### 📦 App Description
**A healthcare or financial application** with strict compliance requirements (HIPAA, PCI-DSS). Implement full audit trail, access logging, data classification, and compliance reporting.

### ✅ Hands-on Tasks

#### Part A: Logging Architecture
- [ ] Design Log Analytics workspace architecture:
  - Single workspace for small environments
  - Hub workspace + satellite workspaces for large enterprises
- [ ] Configure diagnostic settings for ALL Azure services → Log Analytics
- [ ] Deploy Azure Monitor Agent (AMA) to VMs (replaces legacy MMA/OMS agent)
- [ ] Configure Data Collection Rules (DCRs) for selective log collection
- [ ] Set up Activity Log forwarding to Log Analytics

> ⚠️ **DevOps Gotcha:** Log ingestion costs can EXPLODE if you enable verbose logging on everything. A single busy App Gateway can generate 10+ GB/day of logs. Azure SQL Audit logs at maximum verbosity can be enormous. ALWAYS: (1) select only the log categories you need, (2) use Basic logs tier for high-volume tables, (3) set retention policies, (4) monitor workspace ingestion with Cost Analysis.

#### Part B: Microsoft Sentinel (SIEM)
- [ ] Enable Sentinel on your Log Analytics workspace
- [ ] Configure data connectors: Azure Activity, Azure AD Sign-in, Security Events
- [ ] Create analytics rules to detect suspicious behavior:
  - Multiple failed sign-ins from the same IP
  - Resource deletion in production outside business hours
  - New user added to admin group
- [ ] Investigate incidents using the Sentinel investigation graph
- [ ] Create automated response playbooks (Logic Apps)

#### Part C: Compliance
- [ ] Configure regulatory compliance in Defender for Cloud (PCI-DSS, HIPAA)
- [ ] Review compliance score and failing controls
- [ ] Implement fixes for top failing controls
- [ ] Create Azure Policy for enforcing diagnostic settings on all resources
- [ ] Set up Microsoft Purview for data discovery and classification

### 💰 Cost Tips
- Sentinel: ~$2.46/GB ingested (on top of Log Analytics costs)
- First 5GB/day to Log Analytics is FREE
- Use Basic logs tier for high-volume, rarely-queried data (70% cheaper)
- Archive to Storage Account after 90 days (cheapest long-term)
- Sentinel 400GB/day commitment tier: significant discount for large environments

---

## Scenario 27: Azure Backup & Site Recovery

### 🎯 Objective
Implement comprehensive backup and disaster recovery. Meet RPO and RTO targets. Test failover procedures before you need them.

### 📦 App Description
**A production web application with database**, deployed in East US (primary). Set up complete backup and disaster recovery to West Europe (secondary) with automated failover.

### 🏗️ Architecture Diagram
```
┌────────────────────────────────┐     ┌────────────────────────────────┐
│     PRIMARY: East US            │     │    SECONDARY: West Europe      │
│                                │     │    (DR Site)                   │
│  App Service ────────────────────────►  App Service (replica)        │
│  (production)                  │ ASR │  (standby)                    │
│                                │     │                                │
│  Azure SQL ──────────────────────────►  Azure SQL                    │
│  (primary, read-write)         │ Geo │  (secondary, read-only)       │
│                                │ Rep │                                │
│  Storage Account ────────────────────►  Storage Account              │
│  (RA-GRS auto-replicates)      │     │  (read-only secondary)        │
│                                │     │                                │
│  Recovery Services Vault       │     │  Recovery Services Vault       │
│  • VM Backup: Daily, 30 day    │     │  • ASR Replication target      │
│  • SQL Backup: 15 min RPO      │     │  • Cross-region restore        │
│  • File Backup: Daily          │     │                                │
│                                │     │                                │
│  RPO: 15 minutes               │     │  RTO: < 1 hour (auto-failover)│
└────────────────────────────────┘     └────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│ RPO vs RTO:                                                │
│                                                           │
│ RPO (Recovery Point Objective):                            │
│   How much DATA can you afford to lose?                   │
│   15 min RPO = maximum 15 min of data loss                │
│                                                           │
│ RTO (Recovery Time Objective):                             │
│   How much DOWNTIME can you afford?                       │
│   1 hour RTO = system must be back in 1 hour              │
│                                                           │
│ Lower RPO/RTO = more expensive (more frequent backups,    │
│ active-active replication, automated failover)             │
└───────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Azure Backup
- [ ] Create a Recovery Services Vault
- [ ] Configure backup for:
  - VMs: Daily backup, 30-day retention, GFS policy (weekly/monthly/yearly)
  - Azure SQL: Automated backup (PITR up to 35 days) + Long-term retention
  - Azure Files: Daily snapshot
  - Blob Storage: Operational backup (continuous)
- [ ] Perform a file-level restore from VM backup
- [ ] Perform a full VM restore to new VM
- [ ] Cross-region restore from GRS vault
- [ ] Enable soft delete for backup items (prevent accidental deletion)

> ⚠️ **DevOps Gotcha:** VM backup takes a **snapshot first** (for instant restore), then transfers data to the vault. The snapshot phase is fast (minutes), but the data transfer can take hours for large disks. If you need a restore, use the snapshot (instant) rather than waiting for the full vault copy. Also, backup of running VMs captures a **crash-consistent** snapshot (not application-consistent) unless you use the VSS agent (Windows) or pre/post scripts (Linux).

#### Part B: Azure Site Recovery (ASR)
- [ ] Enable Azure-to-Azure replication for VMs
- [ ] Configure replication policy: 15-minute RPO, 24 recovery points
- [ ] Create a Recovery Plan with custom steps (scripts, manual actions)
- [ ] Run a **Test Failover** (creates VMs in secondary region in isolated network)
- [ ] Run a **Planned Failover** (graceful, no data loss)
- [ ] Understand **Unplanned Failover** (forced, potential data loss up to RPO)
- [ ] Re-protect and failback after failover

> ⚠️ **DevOps Gotcha:** ASR test failover creates ACTUAL VMs in the target region — they cost money! Always clean up test failover resources after testing. Also, ASR does NOT replicate NSG rules, UDRs, or public IPs by default. Configure these in the Recovery Plan's pre/post steps, or your failover VMs might be unreachable or have wrong network security.

#### Part C: SQL Database DR
- [ ] Set up SQL Geo-Replication (async read-only replica in secondary region)
- [ ] Create a Failover Group (auto-failover with DNS alias)
- [ ] Test failover: initiate manual failover, verify app reconnects
- [ ] Understand: the failover group DNS alias (`<name>.database.windows.net`) auto-switches — your app's connection string doesn't change

#### Part D: DR Testing & Documentation
- [ ] Create a DR runbook documenting all failover steps
- [ ] Schedule quarterly DR drills
- [ ] Document RPO and RTO targets and actual achieved times
- [ ] Test application functionality after failover (not just connectivity)

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Backup job fails | VM agent not running or disk locked | Reinstall VM agent; check for disk locks |
| ASR replication lag > RPO | High churn rate on disk or network throttling | Check replication health; increase bandwidth |
| Failover VM has wrong IP | IP not mapped in recovery plan | Configure static IP mapping in ASR settings |
| SQL failover group DNS not switching | DNS propagation delay | Wait 5-10 min; use the failover group DNS alias (not server name) |
| Backup vault can't be deleted | Backup items still present (including soft-deleted) | Remove all items; disable soft delete; purge; then delete vault |
| NSG rules missing after failover | ASR doesn't replicate NSGs by default | Pre-create NSGs in DR region; add to recovery plan |

### 💰 Cost Tips
- Recovery Services Vault: FREE (you pay per protected instance)
- VM Backup: ~$5/month per VM (first 500GB), snapshot storage extra
- ASR replication: ~$25/month per VM + compute during failover
- SQL Geo-replication: you pay for the secondary database (same tier as primary)
- **DR testing**: budget for temporary compute during test failovers
- Use LRS vaults for dev/test, GRS for production

---

## 🎯 What's Next?

After completing Batch 5, you should have solid skills in:
- ✅ Comprehensive observability and KQL mastery
- ✅ Enterprise governance with Policy, Resource Graph, and Defender
- ✅ Cost optimization and FinOps practices
- ✅ Compliance and audit logging
- ✅ Backup and disaster recovery strategies

**Proceed to → Batch 6: Advanced Architecture Patterns & Real-World Projects** where you'll tackle multi-region active-active, microservices architecture, event-driven CQRS, zero-trust security, cloud migration, landing zones, and chaos engineering.
