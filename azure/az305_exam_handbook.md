[🏠 Home](../README.md) · [Azure](README.md)

# 📐 AZ-305 Exam — Question & Answer Handbook

> **Audience:** Candidates preparing for AZ-305: Designing Microsoft Azure Infrastructure Solutions
> **Level:** Architect-level. Questions test DESIGN DECISIONS and TRADE-OFFS, not implementation steps.
> **Format:** Scenario → Options → ✅ Correct Answer → Full explanation per option

---

## Exam Domain Weights

| Domain | Weight | Questions |
|--------|--------|-----------|
| **1. Design Identity, Governance & Monitoring Solutions** | 25–30% | Q1–Q22 |
| **2. Design Data Storage Solutions** | 25–30% | Q23–Q45 |
| **3. Design Business Continuity Solutions** | 10–15% | Q46–Q60 |
| **4. Design Infrastructure Solutions** | 25–30% | Q61–Q85 |

---

## Key difference from AZ-104

```
  AZ-104 (Administrator): "HOW do you do X?"
     → Configure a VNet, set up RBAC, deploy a VM

  AZ-305 (Architect): "WHICH approach best meets these requirements?"
     → Given cost, RTO, RPO, compliance constraints — what should you choose and why?

  The correct answer is almost always the one that meets ALL stated requirements
  with the LEAST complexity, cost, or risk.
```

---

# Domain 1: Identity, Governance & Monitoring

---

## Q1 ⭐ Entra ID B2C vs B2B

**Scenario:** Your company is building a consumer-facing e-commerce portal. Customers from any email provider (Gmail, Outlook, Facebook) need to self-register and log in. Internal employees do NOT use this portal.

**Which identity solution should you use?**

A) Azure AD B2B (Business to Business)
B) Azure AD B2C (Business to Consumer)
C) Entra ID External Identities with guest users
D) Federate with a third-party identity provider directly

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — B2B | ❌ Wrong | B2B is for **partner/guest users** who already have a work or Microsoft account. It's NOT designed for self-service registration from Gmail/Facebook. |
| **B — B2C** | ✅ Correct | B2C is purpose-built for **consumer-facing apps**: self-service sign-up, social identity providers (Google, Facebook, Apple), custom branding, and millions of external users. |
| C — Guest users | ❌ Wrong | Guest users via External Identities are B2B — they require an existing Microsoft or organizational account. Not suitable for anonymous Gmail/Facebook consumers. |
| D — Direct federation | ❌ Wrong | You'd have to build and maintain the federation yourself. B2C already handles social logins, user flows, MFA, and token issuance. |

> **Gotcha:** B2C and B2B share the "External Identities" branding but serve completely different purposes. B2C = consumers. B2B = partner organizations.

---

## Q2 ⭐ Conditional Access Design

**Scenario:** Your organization requires that:
- All users accessing Microsoft 365 from unmanaged devices must use MFA
- Users on compliant corporate devices should NOT be prompted for MFA
- Privileged admins (Global Admin, User Admin) must always use MFA regardless of device

**What is the MINIMUM number of Conditional Access policies needed?**

A) 1 policy
B) 2 policies
C) 3 policies
D) 4 policies

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — 1 policy | ❌ Wrong | A single policy cannot express "require MFA UNLESS compliant device" AND "always require MFA for admins." The conditions would conflict. |
| **B — 2 policies** | ✅ Correct | **Policy 1:** Require MFA for all users on non-compliant devices (grant access with MFA if device compliance check fails). **Policy 2:** Require MFA for privileged admin roles regardless of device. These two policies cover all scenarios cleanly. |
| C — 3 policies | ❌ Wrong | You could write 3, but 2 is the minimum that correctly covers all scenarios without redundancy. |
| D — 4 policies | ❌ Wrong | Over-engineered. More policies = more complex management and risk of policy gaps. |

> **Architect principle:** Conditional Access policies should be as few as possible while covering all requirements. Each extra policy adds management overhead and potential for misconfiguration.

---

## Q3 ⭐ Privileged Identity Management (PIM)

**Scenario:** Your security policy states: "No user should hold the Global Administrator role permanently. Admin access must be time-bound, require justification, and trigger approval from a second admin."

**Which feature implements this requirement?**

A) Azure RBAC with custom roles
B) Privileged Identity Management (PIM) with eligible assignments
C) Conditional Access with session controls
D) Azure Policy with deny effect

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Custom RBAC | ❌ Wrong | RBAC roles are always-on. There's no built-in time-bounding, approval workflow, or justification mechanism in standard RBAC. |
| **B — PIM eligible assignments** | ✅ Correct | PIM is exactly this: users get "eligible" (not active) assignments. To use the role, they must activate it with: justification text, optional MFA re-auth, and optionally a second approver. Activations are time-limited (e.g., 1–8 hours). All activations are audited. |
| C — Conditional Access | ❌ Wrong | Conditional Access controls how you authenticate, not what roles you can hold. It can enforce MFA during activation but doesn't provide the eligibility/approval workflow. |
| D — Azure Policy | ❌ Wrong | Azure Policy governs resource configurations, not identity role assignments. |

> **Gotcha:** PIM requires Entra ID P2 licensing. Without P2, you can't use eligible assignments.

---

## Q4 Management Group Hierarchy Design

**Scenario:** A company has:
- 3 business units (BU-A, BU-B, BU-C) each with Dev and Prod environments
- A central IT team that manages shared services (networking, security tools)
- A legal requirement that Production workloads in all BUs must follow the same compliance policy
- BUs should have autonomy over their Dev environments

**Design the management group hierarchy.**

A) Flat structure: All subscriptions directly under Root MG
B) Root → [BU-A MG, BU-B MG, BU-C MG, Shared-IT MG] — subscriptions inside each BU MG
C) Root → [Corp MG] → [BU MGs with Dev/Prod sub-MGs, Shared-IT MG] — compliance policy at Corp level, Dev policies at BU level
D) One management group per subscription

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Flat | ❌ Wrong | You lose the ability to apply policies at different scopes. Every compliance policy must be applied to every subscription individually — unmanageable at scale. |
| B — BU-level MGs only | ❌ Wrong | If compliance policy applies at the BU level, you can't apply a SINGLE policy to ALL production subscriptions across BUs without repeating it per BU MG. |
| **C — Hierarchical with Corp level** | ✅ Correct | Apply compliance policy at Corp MG → inherits to ALL subscriptions. Apply BU-specific policies at BU MGs. Dev environments can have relaxed policies at the BU Dev sub-MG. This is the Microsoft Cloud Adoption Framework recommended structure. |
| D — 1 MG per subscription | ❌ Wrong | Defeats the purpose of management groups — they're meant to group subscriptions. One MG per subscription is just a flat structure with extra complexity. |

---

## Q5 ⭐ Azure Policy vs Azure Blueprint

**Scenario:** You need to ensure that:
1. Every new subscription gets: a VNet, Log Analytics workspace, and specific RBAC role assignments — deployed automatically
2. Certain resource types (classic VMs) are permanently blocked
3. Required tags on all resources are enforced

**Which combination is MOST appropriate?**

A) Azure Policy for all three
B) Azure Blueprint for all three
C) Azure Blueprint for item 1 (resource deployment), Azure Policy for items 2 and 3
D) ARM templates for item 1, Azure Policy for items 2 and 3

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Policy only | ❌ Wrong | Azure Policy can deploy resources via DeployIfNotExists effects, but it's cumbersome for deploying a full set of resources (VNet + workspace + RBAC) as a versioned package. |
| B — Blueprint only | ❌ Wrong | Blueprints can contain Policy assignments, so this technically works, but Blueprints are being deprecated in favour of Template Specs + Policy. Additionally, using Blueprints for simple deny rules is overkill. |
| **C — Blueprint + Policy** | ✅ Correct | Blueprints package multiple artifacts (ARM templates, Policy assignments, RBAC) into a versioned, assignable package — perfect for "subscription bootstrap." Azure Policy with Deny effect is the clean way to block resource types and enforce tagging. |
| D — ARM + Policy | ❌ Wrong | ARM templates alone don't provide repeatable subscription-level assignment with versioning. You'd need to orchestrate deployment manually. |

> **Note (2024+):** Microsoft is deprecating Azure Blueprints in favour of Deployment Stacks + Template Specs. For the exam, Blueprint is still the expected answer. In real projects, evaluate the newer approach.

---

## Q6 Centralized vs Distributed Logging Architecture

**Scenario:** You have 15 Azure subscriptions across 3 business units. Security team needs a single view of all logs for threat detection. Individual teams need logs only for their own resources. Retention must be 90 days for operational logs, 1 year for security audit logs.

**Which architecture BEST meets these requirements?**

A) One Log Analytics workspace per subscription
B) One centralized Log Analytics workspace for all subscriptions
C) One Log Analytics workspace per BU for operational logs + one centralized workspace for security logs (Microsoft Sentinel)
D) Azure Monitor alerts per subscription with no centralized logging

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Per subscription | ❌ Wrong | Security team cannot get a unified view without cross-workspace queries, which add complexity. No single place for threat detection. |
| B — Fully centralized | ❌ Wrong | Individual teams see ALL logs from all subscriptions. Data access control is complex. One workspace for 15 subscriptions creates ingestion cost concerns. |
| **C — Hybrid (BU workspaces + security workspace)** | ✅ Correct | Individual BU workspaces with RBAC give teams their own view. A centralized Security workspace (connected to Sentinel) receives security events from all subscriptions via Diagnostic Settings. Different retention per workspace satisfies the dual retention requirement. |
| D — No centralized logging | ❌ Wrong | Doesn't meet the security team's requirement. Alerts without logs = no investigation capability. |

---

## Q7 ⭐ Custom RBAC Role Design

**Scenario:** Developers need to be able to:
- View and list all resources in their resource group
- Start, stop, and restart VMs
- NOT be able to delete any resources
- NOT be able to change networking or RBAC settings

**What should you assign?**

A) Reader + Virtual Machine Contributor
B) Contributor with a deny assignment for delete operations
C) A custom role with specific allowed actions: Microsoft.Compute/virtualMachines/start, stop, restart, and */read
D) Owner with limited scope

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Reader + VM Contributor** | ✅ Correct | Reader grants */read across all resources (view everything). VM Contributor grants start/stop/restart VMs but does NOT include delete, network changes, or RBAC changes. This combination of two built-in roles meets all requirements without custom role complexity. |
| B — Contributor + deny | ❌ Wrong | Deny assignments require Azure Blueprints or specific PIM configurations — you cannot create ad-hoc deny assignments in standard RBAC. Also, Contributor already allows networking and RBAC changes. |
| C — Custom role | ❌ Wrong | Would work, but violates the "least complexity" principle. Reader + VM Contributor achieves the same result using built-in roles. Custom roles are for gaps that built-in roles can't fill. |
| D — Owner limited scope | ❌ Wrong | Owner includes full delete and RBAC assignment permissions — violates the requirement. |

---

## Q8 Multi-Tenant Identity Design

**Scenario:** Your company (Tenant A) has acquired another company (Tenant B). Users from Tenant B need access to SharePoint and some Azure resources in Tenant A. The acquisition is complete — Tenant B users should gradually be migrated but IT wants minimal disruption now.

**What is the recommended approach?**

A) Merge Tenant B into Tenant A immediately (delete Tenant B)
B) Configure Azure AD Connect between both tenants
C) Invite Tenant B users as B2B guests into Tenant A
D) Create duplicate accounts for each Tenant B user in Tenant A

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Merge tenants | ❌ Wrong | Azure AD doesn't support merging tenants directly. This would require provisioning all users manually, reconfiguring all app registrations, updating all role assignments — weeks of work with high risk of disruption. |
| B — Azure AD Connect | ❌ Wrong | Azure AD Connect syncs from on-premises Active Directory to Azure AD. It doesn't federate between two Azure AD tenants. |
| **C — B2B guests** | ✅ Correct | B2B allows Tenant B users to sign in with their existing Tenant B credentials and be granted access to resources in Tenant A. Minimal disruption, no password changes, existing SSO preserved. Gradual migration can happen in parallel. This is exactly the use case B2B was designed for. |
| D — Duplicate accounts | ❌ Wrong | Users get two sets of credentials, double licensing costs, and two identities to maintain. Security nightmare — if a Tenant B user leaves, their Tenant A account may be forgotten. |

---

## Q9 Azure Monitor Architecture

**Scenario:** You need to monitor a 3-tier web application: Azure Front Door → Application Gateway → AKS → Azure SQL. You need: real-time performance metrics, end-to-end transaction tracing, anomaly detection, and automated alerting.

**Which combination covers all requirements?**

A) Azure Monitor Metrics only
B) Log Analytics + Azure Monitor Alerts
C) Application Insights (for app tracing) + Azure Monitor Metrics + Log Analytics + Azure Monitor Alerts
D) Grafana + Prometheus only

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Metrics only | ❌ Wrong | Metrics give numbers (CPU, latency) but no end-to-end transaction tracing. You can't correlate a slow SQL query with a specific frontend request. |
| B — Log Analytics + Alerts | ❌ Wrong | Covers logging and alerting but missing application-level distributed tracing and anomaly detection (Smart Detection). |
| **C — App Insights + Monitor + Log Analytics + Alerts** | ✅ Correct | **Application Insights:** end-to-end distributed tracing, dependency mapping, Smart Detection (anomaly detection), user behaviour. **Azure Monitor Metrics:** real-time infra metrics (CPU, memory, latency). **Log Analytics:** log aggregation and query. **Alerts:** automated notifications. Each tool fills a specific gap. |
| D — Grafana + Prometheus | ❌ Wrong | Valid for open-source monitoring but doesn't cover Azure PaaS services natively. Azure Monitor data can be sent to Grafana, but not "only Grafana + Prometheus" — you'd still need Azure Monitor as the data source. |

---

## Q10 ⭐ Defender for Cloud vs Azure Monitor

**Scenario:** A security architect asks: "We need to detect misconfigurations in our Azure resources (e.g., storage accounts open to internet, SQL databases without encryption) and also detect threats like suspicious logins and malware on VMs."

**Which service(s) should they use?**

A) Azure Monitor only
B) Microsoft Defender for Cloud only
C) Azure Sentinel only
D) Defender for Cloud (for posture management + threat detection) + Microsoft Sentinel (for SIEM/SOAR and long-term investigation)

**✅ Answer: D**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Azure Monitor | ❌ Wrong | Azure Monitor is an observability platform, not a security tool. It doesn't evaluate security posture or detect threats. |
| B — Defender for Cloud only | ❌ Wrong | Defender for Cloud has CSPM (Cloud Security Posture Management) and workload threat detection. But it lacks full SIEM capabilities — it doesn't retain logs long-term for investigation, doesn't do cross-platform correlation, and doesn't have SOAR playbooks. |
| C — Sentinel only | ❌ Wrong | Sentinel is a SIEM — it ingests and correlates logs. But it doesn't natively evaluate resource configurations (that's Defender for Cloud's CSPM). |
| **D — Defender for Cloud + Sentinel** | ✅ Correct | **Defender for Cloud:** Secure Score, configuration recommendations, real-time threat alerts per workload. **Microsoft Sentinel:** Ingests Defender alerts + other data sources, long-term log retention, KQL investigation, automation playbooks (Logic Apps). They complement each other — Defender detects, Sentinel investigates and responds. |

---

## Q11 Identity: Choosing Authentication Method

**Scenario:** Your company has 5,000 users in on-premises Active Directory. The requirement is:
- All users sign in to Microsoft 365 using corporate AD credentials
- Users must NOT be forced to change their AD password when it expires in the cloud — AD is still the authoritative password store
- No additional on-premises infrastructure should be required for authentication

**Which hybrid identity authentication method should you choose?**

A) Password Hash Synchronization (PHS)
B) Pass-through Authentication (PTA)
C) Active Directory Federation Services (AD FS)
D) Azure AD Connect Cloud Sync with SAML

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — PHS** | ✅ Correct | PHS syncs a hash of the password hash to Azure AD. Authentication happens in the cloud — no on-prem dependency at sign-in time. Password expiry policies can be configured so cloud doesn't force resets. No extra on-prem infrastructure needed beyond Azure AD Connect (which is the sync tool, not an auth server). |
| B — PTA | ❌ Wrong | PTA authenticates against on-prem AD at sign-in time (real-time), which requires PTA Agent running on-premises. Any on-prem outage = users can't log in to M365. Also the "no additional on-prem infrastructure" requirement — PTA needs at least 3 agents for HA. |
| C — AD FS | ❌ Wrong | Requires deploying and managing AD FS servers on-premises. Highly complex infrastructure. Violates "no additional on-prem infrastructure" requirement. |
| D — Cloud Sync + SAML | ❌ Wrong | Cloud Sync is an agent-based alternative to Azure AD Connect for synchronization, not for authentication. SAML federation would still require a federation service on-premises. |

> **Gotcha:** PHS is Microsoft's recommended method for most organizations because it has the best availability (no on-prem auth dependency) and security (works even if on-prem is compromised — cloud passwords can still be forced reset).

---

## Q12 Governance: Cost Management Design

**Scenario:** Your organization wants to:
- Get automated alerts when a subscription reaches 80% and 100% of its monthly budget
- Force teams to add required tags on all resources at creation time
- See a unified cost breakdown by department

**Which combination of features addresses ALL three requirements?**

A) Azure Cost Management + Azure Policy + Management Groups
B) Azure Budgets + Azure Policy (Deny effect for tags) + Cost Analysis with tags
C) Azure Advisor + Azure Policy + Resource Groups
D) Microsoft Cost Management (external) + manual tagging

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Cost Management + Policy + MGs | ❌ Partially right | Missing the specific "Budgets" feature for alerts. "Azure Cost Management" is the broader service — you need **Azure Budgets** specifically for threshold alerts. MGs add scope but aren't required for these three requirements. |
| **B — Budgets + Policy + Cost Analysis** | ✅ Correct | **Azure Budgets:** Set budget thresholds with automated email alerts at 80% and 100%. **Azure Policy (Deny for tags):** Block resource creation if required tags are missing. **Cost Analysis with tag filters:** Break down costs by department tag for unified view. Each requirement maps to exactly one feature. |
| C — Advisor + Policy + RGs | ❌ Wrong | Azure Advisor provides recommendations but NOT budget alerts. Resource groups don't solve the cross-department view. |
| D — External + manual | ❌ Wrong | Manual tagging isn't enforced — teams will skip it. External tooling adds complexity without using native features. |

---

## Q13 ⭐ Entra ID Licensing Requirements

**Scenario:** A DevOps architect is designing an identity solution. Which features require Entra ID P2 licensing? (Select all that apply.)

A) Multi-Factor Authentication (MFA)
B) Privileged Identity Management (PIM)
C) Conditional Access
D) Identity Protection (risk-based sign-in policies)
E) B2B guest user access
F) Self-Service Password Reset (SSPR)

**✅ Answer: B and D**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — MFA | ❌ P2 not required | MFA per-user is available in all paid Entra ID tiers. Security Defaults (free tier) enforce MFA. Per-user MFA = included in M365. |
| **B — PIM** | ✅ Requires P2 | PIM (eligible assignments, activation workflows, access reviews) requires Entra ID P2 or Microsoft Entra ID Governance. |
| C — Conditional Access | ❌ P2 not required | Conditional Access requires Entra ID P1 or higher. P2 adds risk-based conditions, but basic CA is P1. |
| **D — Identity Protection** | ✅ Requires P2 | Risk-based sign-in policies (sign-in risk, user risk, risky users report) require Entra ID P2. |
| E — B2B guest | ❌ P2 not required | B2B guest access is available in free tier (up to 5 guests per licensed user for free). |
| F — SSPR | ❌ P2 not required | SSPR requires Entra ID P1. Combined registration for SSPR+MFA requires P1. |

---

## Q14 Zero Trust Architecture

**Scenario:** An architect is designing a Zero Trust network model. Which statement BEST describes the core principle?

A) Trust all traffic inside the corporate network perimeter
B) Verify every user and device, apply least privilege, and assume breach
C) Use a firewall to block all external traffic and allow all internal traffic
D) Deploy VPN for all remote workers and trust authenticated VPN sessions

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Trust the perimeter | ❌ Wrong | This is the old "castle and moat" model that Zero Trust explicitly replaces. Lateral movement by attackers who breach the perimeter is a major risk. |
| **B — Verify, least privilege, assume breach** | ✅ Correct | The three Zero Trust pillars: (1) Verify explicitly — always authenticate and authorize based on all data points. (2) Least privilege — limit access with JIT/JEA. (3) Assume breach — design as if breaches are inevitable, limit blast radius. |
| C — Firewall model | ❌ Wrong | Traditional perimeter security, not Zero Trust. Doesn't address insider threats or compromised internal accounts. |
| D — VPN trust | ❌ Wrong | VPN establishes connectivity but doesn't verify device compliance or enforce per-resource access control. A compromised VPN session gets broad access. |

---

## Q15 Azure AD Application Registration vs Enterprise Application

**Scenario:** A developer registers an internal HR app in Azure AD. What is the difference between the "App Registration" and the "Enterprise Application" that gets created?

A) App Registration is for internal apps; Enterprise Applications are for SaaS apps from the Gallery
B) App Registration defines WHAT the app is (identity, permissions, redirect URIs); Enterprise Application is the service principal — the local instance of the app in your tenant that controls WHO can access it
C) They are the same thing — just two views of the same object
D) App Registration is for OAuth; Enterprise Application is for SAML

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Internal vs SaaS | ❌ Wrong | Both App Registrations and Enterprise Applications exist for internal apps AND gallery apps. The distinction isn't about where the app comes from. |
| **B — Definition vs Instance** | ✅ Correct | App Registration = the application definition: app ID, client secrets, API permissions requested, redirect URIs. Enterprise Application (Service Principal) = the local representation of that app in your tenant: who is assigned access, whether assignment is required, consent grants, sign-in logs. When you add a SaaS app from the Gallery, an Enterprise Application is created without a corresponding App Registration (since the registration is in the vendor's tenant). |
| C — Same object | ❌ Wrong | They are related but distinct objects. App Registration → global; Enterprise Application → tenant-specific. |
| D — OAuth vs SAML | ❌ Wrong | Both protocols can be configured in either App Registration or Enterprise Application depending on the integration type. |

---

## Q16 ⭐ Managed Identity vs Service Principal

**Scenario:** An Azure Function needs to read secrets from Key Vault. The solution must minimize credential management overhead.

**What is the BEST approach?**

A) Create a service principal with a client secret, store the secret in app settings
B) Create a service principal with a certificate stored in Key Vault
C) Assign a System-Assigned Managed Identity to the Function App, grant Key Vault Secret User role
D) Use connection string authentication with Key Vault

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Service principal + client secret | ❌ Wrong | Client secrets expire and must be rotated manually. The secret is stored in app settings (plaintext). Circular problem: you need credentials to access Key Vault, and those credentials need to be managed somewhere. |
| B — Service principal + certificate | ❌ Wrong | More secure than a secret, but the certificate still needs to be managed, stored, and rotated. The function code needs to load the certificate to authenticate. |
| **C — Managed Identity** | ✅ Correct | Managed Identity (system-assigned) means Azure manages the credential entirely. No secrets, no certificates, no rotation. The Function App gets a token from the IMDS endpoint automatically. Granting Key Vault Secret User role on the Key Vault lets it read secrets. Zero credential management overhead — exactly what the question requires. |
| D — Connection string auth | ❌ Wrong | Key Vault doesn't use connection strings. This isn't a valid authentication method for Key Vault. |

> **Gotcha:** Key Vault Secret User role = read secrets (data plane). Key Vault Contributor role = manage Key Vault (control plane) but does NOT allow reading secrets. Must grant the right data plane role.

---

## Q17 Azure Policy Effects — Correct Order of Evaluation

**Scenario:** An Azure Policy with `Deny` effect and another with `Audit` effect both apply to the same resource type. Which statement is correct?

A) Audit effect takes precedence over Deny
B) Deny effect takes precedence — the resource creation is blocked
C) Both effects are applied simultaneously
D) The policy with the higher priority number takes precedence

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Audit > Deny | ❌ Wrong | The evaluation order is: Disabled → Append → Deny → Audit → AuditIfNotExists → DeployIfNotExists. Deny is evaluated before Audit. |
| **B — Deny takes precedence** | ✅ Correct | If any applicable policy has the `Deny` effect and the resource is non-compliant, the resource creation is blocked. The `Audit` policy doesn't override the `Deny`. The resource is denied and would have been audited if allowed, but it's never created. |
| C — Both simultaneously | ❌ Wrong | Deny stops resource creation. Audit cannot apply to a resource that was never created. |
| D — Priority number | ❌ Wrong | Azure Policy doesn't have a "priority number" like Conditional Access. All applicable policies are evaluated; Deny wins. |

---

## Q18 Monitoring: Alert Rule Design

**Scenario:** You want to alert when the average CPU of a VM Scale Set exceeds 90% for more than 5 consecutive minutes. Cost must be minimized.

**What type of alert rule should you create?**

A) Log Alert querying the Log Analytics workspace every minute
B) Metric Alert with aggregation type Average, threshold 90%, evaluation frequency 1 min, window size 5 min
C) Activity Log Alert for CPU threshold
D) Smart Detection in Application Insights

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Log Alert | ❌ Wrong | Log Alerts query Log Analytics and have minimum 1-minute granularity but incur query costs per evaluation. CPU is a native metric — using a Metric Alert is more efficient and near real-time (1-minute granularity natively). |
| **B — Metric Alert** | ✅ Correct | Metric Alerts evaluate platform metrics (like CPU) directly without needing Log Analytics queries. Aggregation=Average, threshold=90%, frequency=1 min, window=5 min means: "average CPU over the last 5 minutes, checked every 1 minute — alert if >90%." This satisfies "5 consecutive minutes" semantics. Cheaper than Log Alerts and near real-time. |
| C — Activity Log Alert | ❌ Wrong | Activity Log Alerts trigger on management operations (e.g., VM stopped, policy changed) — not on performance metrics. |
| D — Smart Detection | ❌ Wrong | Application Insights Smart Detection finds anomalies in application telemetry (latency, failure rate). It doesn't monitor VM CPU. |

---

## Q19 Log Retention and Archival

**Scenario:** Compliance requires audit logs to be retained for 7 years. Log Analytics workspace interactive retention is limited to 2 years (730 days). How do you meet the 7-year requirement?

A) Create multiple Log Analytics workspaces to chain retention
B) Use Log Analytics long-term retention (archive tier) to extend retention to 12 years
C) Export logs to Azure Storage with immutable storage policy
D) Both B and C are valid approaches

**✅ Answer: D**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Chain workspaces | ❌ Wrong | You can't chain workspaces to extend retention. Each workspace's retention is independent. |
| B — Archive tier | ✅ Partially correct | Log Analytics has an Archive Tier that extends to 12 years. Archive data is not interactively queryable (you must restore it first) but it satisfies the retention requirement. This is a valid approach. |
| C — Azure Storage with WORM | ✅ Partially correct | Exporting to Azure Blob Storage with immutable storage policies (WORM — Write Once Read Many) satisfies compliance requirements for long-term retention. Cheaper for very large volumes. |
| **D — Both B and C** | ✅ Correct | Both approaches meet the 7-year requirement. The choice depends on: budget, whether you need to query archived data, and compliance team preferences. In practice, many organizations use both: Archive tier for hot compliance data, Storage for cold compliance archives. |

---

## Q20 Identity Governance: Access Reviews

**Scenario:** Quarterly, you need to verify that only the right people still have access to sensitive Azure resources and Microsoft 365 groups. Access should be automatically removed if reviewers don't respond within 2 weeks.

**What feature should you use?**

A) Conditional Access with sign-in risk policies
B) Azure AD Access Reviews with auto-apply results
C) PIM role activation expiry settings
D) Azure RBAC assignment expiry dates

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Conditional Access | ❌ Wrong | Conditional Access controls authentication conditions, not periodic review of who has access. It doesn't have a "quarterly review" workflow. |
| **B — Access Reviews** | ✅ Correct | Access Reviews (part of Entra ID Governance, requires P2) allow you to: schedule quarterly reviews, assign reviewers (managers, group owners, or the users themselves), and configure auto-apply results (remove access if no response within the review window). Exactly the scenario described. |
| C — PIM expiry settings | ❌ Wrong | PIM role activations are time-limited but that's for active role periods (hours/days), not quarterly compliance reviews. |
| D — RBAC assignment expiry | ❌ Wrong | RBAC role assignments in Azure don't have built-in expiry dates. PIM eligible assignments can have expiry, but standard RBAC assignments don't automatically expire. |

---

## Q21 Entra External ID Architecture

**Scenario:** You're designing a partner portal where employees from 50 partner organizations need to access your Azure-hosted web app. Partners use their own corporate Azure AD tenants. What is the simplest architecture?

A) Create user accounts in your tenant for all 50 partner organizations' users
B) Set up AD FS federation with each partner organization
C) Configure Azure AD B2B cross-tenant access settings and invite users, or configure cross-tenant synchronization
D) Deploy a separate Azure AD B2C tenant for partner users

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Create accounts in your tenant | ❌ Wrong | Creates a second identity for every partner user. They must manage two sets of credentials. When they leave their company, you must manually deprovision them in your tenant — a security risk. |
| B — AD FS with each partner | ❌ Wrong | AD FS requires federation trust with each of 50 tenants — enormous infrastructure and maintenance overhead. |
| **C — B2B or cross-tenant sync** | ✅ Correct | **B2B invitation:** Partners authenticate with their own Azure AD tenant credentials. You grant access by inviting them as guests. **Cross-tenant synchronization (ENTRA ID new feature):** Automatically syncs users from partner tenants into yours for deeper integration. Both approaches use each organization's existing identity — no second password, no federation servers. |
| D — B2C | ❌ Wrong | B2C is for consumers (self-service registration, social logins). Partners are corporate users with corporate identities — B2B is the right tool. |

---

## Q22 Azure Monitor Workbooks vs Dashboards

**Scenario:** Your operations team wants an interactive report that shows: live metrics charts, log query results tables, and allows filtering by environment (dev/staging/prod) via a dropdown. The report should be shareable across the team.

**Which Azure Monitor feature should you use?**

A) Azure Dashboard
B) Azure Monitor Workbooks
C) Power BI with Azure Monitor connector
D) Log Analytics query results

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Azure Dashboard | ❌ Partially | Dashboards can show pinned charts and tiles but don't support interactive parameters (dropdowns) or mixing metrics with log query tables in a single interactive document. |
| **B — Azure Monitor Workbooks** | ✅ Correct | Workbooks are interactive documents combining: metrics charts, log query tables, text, parameters (dropdowns, date pickers), and links. They support sharing via Azure RBAC. Designed exactly for this scenario. |
| C — Power BI | ❌ Wrong | Power BI works but adds licensing complexity and a separate tool. For Azure-native teams, Workbooks serve this purpose without extra cost or tooling. |
| D — Log Analytics queries | ❌ Wrong | Raw query results are not interactive, not shareable as a formatted report, and don't include metrics charts. |

---

# Domain 2: Design Data Storage Solutions

---

## Q23 ⭐ Choosing the Right Database

**Scenario:** You are designing storage for the following data:
- **App 1:** Social network — user profiles with variable schema, global users needing <10ms reads, must scale horizontally
- **App 2:** Financial transactions — ACID compliance, complex joins, 99.99% SLA
- **App 3:** Sensor data — 100,000 events/second, time-series analysis

**Match each app to the BEST Azure database service.**

A) App1=Cosmos DB, App2=Azure SQL DB, App3=Azure Table Storage
B) App1=Cosmos DB, App2=Azure SQL Managed Instance, App3=Azure Data Explorer (ADX)
C) App1=Azure SQL DB, App2=Cosmos DB, App3=Event Hub
D) App1=Azure Table Storage, App2=Azure SQL DB, App3=Cosmos DB

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — App3=Table Storage | ❌ Wrong | Azure Table Storage is a simple key-value store, not optimized for time-series analysis or 100K events/sec ingestion and querying. |
| **B — Cosmos/SQL MI/ADX** | ✅ Correct | **Cosmos DB:** Global distribution, <10ms reads globally, schema-flexible (document model), horizontal scale. Perfect for social profiles. **Azure SQL Managed Instance:** Full SQL Engine compatibility (ACID, stored procs, complex joins), 99.99% SLA. Perfect for financial transactions needing relational features. **Azure Data Explorer (ADX):** Purpose-built for time-series and telemetry at massive scale (ingests millions of events/sec, optimized for time-range queries, built-in anomaly detection). |
| C — Wrong assignment | ❌ Wrong | Azure SQL DB doesn't handle variable schemas well. Cosmos DB for ACID financial transactions works but adds unnecessary complexity vs SQL MI. Event Hub is a streaming platform, not a database. |
| D — Wrong assignment | ❌ Wrong | Table Storage for social profiles: no global distribution, no sub-10ms global reads. Cosmos DB for time-series: possible but not optimal vs ADX. |

---

## Q24 ⭐ Cosmos DB Consistency Levels

**Scenario:** A global e-commerce app uses Cosmos DB in 3 regions. Which consistency level should you choose for each requirement?

- Shopping cart: Must show user's own writes immediately
- Product catalog: Reads can be slightly stale (seconds) — lowest latency is priority
- Order records: Must guarantee reads reflect all previous writes globally

**Match requirements to consistency levels.**

A) Cart=Bounded Staleness, Catalog=Session, Orders=Strong
B) Cart=Session, Catalog=Eventual, Orders=Strong
C) Cart=Strong, Catalog=Eventual, Orders=Consistent Prefix
D) Cart=Session, Catalog=Consistent Prefix, Orders=Bounded Staleness

**✅ Answer: B**

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │  COSMOS DB CONSISTENCY LEVELS (strongest → weakest)                 │
  │                                                                     │
  │  Strong           → Global linearizability. Reads always return     │
  │                     latest committed write. Highest latency.        │
  │  Bounded          → Reads lag behind by at most K versions or T    │
  │  Staleness          seconds. Good for near-real-time global reads.  │
  │  Session          → Within a session, monotonic reads, monotonic   │
  │                     writes, read-your-writes. DEFAULT. Balanced.   │
  │  Consistent       → No out-of-order reads. Never see rollbacks.    │
  │  Prefix             Global order guaranteed.                        │
  │  Eventual         → Lowest latency, highest availability. Reads    │
  │                     may be stale. Order not guaranteed.            │
  └─────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Cart=Bounded Staleness | ❌ Wrong | Bounded Staleness guarantees a lag bound but doesn't guarantee a user sees their OWN writes in the same session. Session consistency is the right choice for per-user read-your-writes. |
| **B — Cart=Session, Catalog=Eventual, Orders=Strong** | ✅ Correct | **Session:** User always sees their own cart writes (read-your-writes guarantee within the session). **Eventual:** Product catalog can be slightly stale — acceptable, lowest latency for read-heavy global traffic. **Strong:** Orders must reflect all prior writes — linearizability required for financial/inventory consistency. |
| C — Cart=Strong | ❌ Wrong | Strong for shopping cart is overkill — expensive, high latency. Session provides read-your-writes which is all the cart needs. |
| D — Orders=Bounded Staleness | ❌ Wrong | Bounded Staleness still allows stale reads (within the bound). Order records need Strong to guarantee no stale data ever. |

---

## Q25 ⭐ Storage Account Redundancy Selection

**Scenario:** Choose the correct redundancy option for each requirement:

- **File A:** VM disk OS data — can tolerate VM restart, must survive datacenter failure in same region
- **File B:** Backup archives — must survive complete regional failure, reads from secondary are acceptable when primary fails  
- **File C:** Critical database backups — must survive regional failure AND secondary region must always be readable (not just on failover)

A) A=LRS, B=GRS, C=RA-GRS
B) A=ZRS, B=GRS, C=RA-GRS
C) A=LRS, B=RA-GRS, C=GZRS
D) A=ZRS, B=GZRS, C=RA-GZRS

**✅ Answer: B**

```
  ┌────────────────────────────────────────────────────────────────────┐
  │  STORAGE REDUNDANCY DECISION TREE                                  │
  │                                                                    │
  │  LRS: 3 copies, 1 datacenter. Cheapest.                           │
  │       ✅ Dev/test, non-critical data                               │
  │       ❌ Datacenter fire = data loss                               │
  │                                                                    │
  │  ZRS: 3 copies, 3 availability zones in 1 region.                 │
  │       ✅ Datacenter failure survival within region                 │
  │       ❌ Regional failure = data loss                              │
  │                                                                    │
  │  GRS: Primary region (LRS) + secondary region (LRS).              │
  │       Secondary is NOT readable unless you initiate failover.     │
  │       ✅ Regional disaster recovery                                │
  │                                                                    │
  │  RA-GRS: Same as GRS but secondary IS always readable.            │
  │          ✅ Regional DR + always read from secondary               │
  │                                                                    │
  │  GZRS: Primary region (ZRS) + secondary region (LRS).            │
  │  RA-GZRS: Same + readable secondary.                              │
  │           ✅ Highest durability + zone resilience                  │
  └────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — A=LRS | ❌ Wrong | LRS survives hardware failure within one datacenter, NOT datacenter failure. File A requires surviving datacenter failure within same region → ZRS. |
| **B — A=ZRS, B=GRS, C=RA-GRS** | ✅ Correct | **A=ZRS:** 3 copies across 3 zones — survives full datacenter outage in same region. **B=GRS:** Survives regional failure, secondary readable on manual failover — acceptable for backups. **C=RA-GRS:** Secondary always readable without failover — matches "must always be readable." |
| C — A=LRS | ❌ Wrong | Same issue as A above. |
| D — All GZRS | ❌ Wrong | GZRS is correct for File C (even better than RA-GRS). But for File A, ZRS is sufficient and cheaper than GZRS. Over-engineering and unnecessary cost for File A. |

---

## Q26 Azure SQL Database vs SQL Managed Instance

**Scenario:** A company is migrating a large on-premises SQL Server 2019 database. The application uses:
- Linked Servers to another SQL Server
- SQL Server Agent jobs
- CLR assemblies
- Cross-database queries

**Which Azure SQL option should they choose?**

A) Azure SQL Database (Single Database)
B) Azure SQL Database (Elastic Pool)
C) Azure SQL Managed Instance
D) SQL Server on Azure VM (IaaS)

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  SQL FEATURE COMPATIBILITY                                            │
  │                                                                       │
  │  Feature                    SQL DB    SQL MI    SQL on VM            │
  │  ─────────────────────────────────────────────────────────────────   │
  │  Linked Servers              ❌        ✅        ✅                   │
  │  SQL Agent jobs              ❌        ✅        ✅                   │
  │  CLR assemblies              Limited   ✅        ✅                   │
  │  Cross-database queries      ❌        ✅        ✅                   │
  │  Full SQL Agent              ❌        ✅        ✅                   │
  │  Service Broker              ❌        ✅        ✅                   │
  │  Database Mail               ❌        ✅        ✅                   │
  │  Managed backups             ✅        ✅        Manual              │
  │  Built-in HA                 ✅        ✅        Manual (WSFC)       │
  │  OS access                   ❌        ❌        ✅                   │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — SQL DB Single | ❌ Wrong | SQL Database doesn't support Linked Servers, SQL Agent, or cross-database queries. App would require significant refactoring. |
| B — SQL DB Elastic Pool | ❌ Wrong | Same limitations as Single Database — Elastic Pool is about cost optimization for multiple databases, not feature expansion. |
| **C — SQL Managed Instance** | ✅ Correct | SQL MI provides near 100% SQL Server compatibility including all the features the app requires: Linked Servers, SQL Agent, CLR, cross-database queries. It's PaaS (fully managed), unlike IaaS. The "Lift and Shift" option. |
| D — SQL on VM | ❌ Wrong | SQL on VM also supports all features, but requires OS management, patching, backup configuration — higher operational overhead. SQL MI is preferred when MI supports the required features. |

---

## Q27 ⭐ Messaging Service Selection

**Scenario:** Match each requirement to the right Azure messaging service:

- **A:** Decouple a web app from a payment processing service. Each order must be processed exactly once. Messages must survive if the payment service is down for hours.
- **B:** Broadcast a "new product published" event to 50 different subscriber services simultaneously  
- **C:** Ingest 1 million IoT sensor telemetry events per second for real-time analytics

A) A=Queue Storage, B=Service Bus Topics, C=Event Hub
B) A=Service Bus Queue, B=Event Grid, C=Event Hub
C) A=Service Bus Queue, B=Service Bus Topics, C=Event Hub
D) A=Event Hub, B=Event Grid, C=Kafka

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  AZURE MESSAGING SERVICES                                             │
  │                                                                       │
  │  Azure Queue Storage:                                                 │
  │  ├── Simple message queue, at-least-once delivery                    │
  │  ├── Max message: 64KB, max queue: 500TB                             │
  │  ├── No topics/subscriptions, no dead-letter queue natively          │
  │  └── Good for: simple task queues, basic decoupling                  │
  │                                                                       │
  │  Azure Service Bus Queue:                                             │
  │  ├── Enterprise messaging: FIFO, dead-letter, sessions, batching     │
  │  ├── At-most-once (peek-lock) + exactly-once-processing patterns     │
  │  ├── Max message: 256KB (Standard), 100MB (Premium)                  │
  │  └── Good for: order processing, financial transactions, decoupling  │
  │                                                                       │
  │  Azure Service Bus Topics:                                            │
  │  ├── Service Bus + pub/sub (one message → multiple subscriptions)    │
  │  └── Good for: fan-out to related services                           │
  │                                                                       │
  │  Azure Event Grid:                                                    │
  │  ├── Event routing: source → multiple handlers                       │
  │  ├── Push-based, HTTP webhooks, near-zero latency                    │
  │  ├── Integrates natively with Azure resource events                  │
  │  └── Good for: reactive automation, serverless triggers              │
  │                                                                       │
  │  Azure Event Hub:                                                     │
  │  ├── Big data streaming pipeline                                      │
  │  ├── Millions of events/sec, partitioned, consumer groups            │
  │  ├── Kafka-compatible surface                                         │
  │  └── Good for: telemetry, log streaming, real-time analytics        │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — A=Queue Storage | ❌ Wrong | Queue Storage has at-least-once delivery but lacks enterprise features like dead-letter queues, sessions, and peek-lock for exactly-once processing patterns. |
| **B — A=Service Bus, B=Event Grid, C=Event Hub** | ✅ Correct | **Service Bus Queue:** Exactly-once processing via peek-lock, dead-letter queue for failures, durable message storage. Perfect for orders. **Event Grid:** Event routing to multiple subscribers simultaneously, push-based, sub-second delivery — perfect for "new product published" fan-out. **Event Hub:** Designed for high-throughput telemetry (millions/sec), partitioned for parallel processing. |
| C — A=SB, B=SB Topics, C=Event Hub | ❌ Partially | Event Hub is correct. But for "broadcast to 50 different subscriber services" that may be in different systems (not related), Event Grid is better than SB Topics. SB Topics work within the SB ecosystem; Event Grid natively fans out to HTTP webhooks, Azure Functions, Logic Apps, etc. |
| D — A=Event Hub | ❌ Wrong | Event Hub is for high-throughput streaming, not durable order processing queues with exactly-once semantics. |

---

## Q28 Azure Data Lake vs Blob Storage

**Scenario:** A data engineering team needs to store:
- Raw log files (CSV, JSON) from 100 systems
- These files will be analyzed by Azure Databricks and Azure Synapse
- Data must be organized with hierarchical folder structure and fine-grained access control at the folder level

**Which service should they use?**

A) Azure Blob Storage (general purpose v2)
B) Azure Data Lake Storage Gen2 (ADLS Gen2)
C) Azure Files
D) Azure Table Storage

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Blob Storage | ❌ Partially | Blob Storage can store the files and Databricks/Synapse can read from it. But Blob Storage doesn't have a true hierarchical namespace — "folders" are simulated by path prefixes. You can't set ACLs at the folder level (only at the container or blob level). |
| **B — ADLS Gen2** | ✅ Correct | ADLS Gen2 = Azure Blob Storage with Hierarchical Namespace (HNS) enabled. It provides true directory structure with POSIX-compatible ACLs at the folder level. Native integration with Databricks, Synapse, and all Azure analytics services. This is the standard for analytics workloads. |
| C — Azure Files | ❌ Wrong | Azure Files is an SMB/NFS file share — designed for lift-and-shift applications that need a file system, not for analytics pipelines. |
| D — Azure Table Storage | ❌ Wrong | Table Storage is a key-value store for structured data — not for raw log files and analytics. |

---

## Q29 ⭐ Storage Account Access Tiers

**Scenario:** A company stores documents in Azure Blob Storage:
- Active documents: accessed multiple times daily
- Archive: documents from last year, accessed maybe once per quarter
- Cold archive: documents older than 3 years, must be retained for compliance but almost never accessed

**Which storage tiers should they use?**

A) All documents in Hot tier
B) Active=Hot, Archive=Cool, Cold archive=Archive
C) Active=Hot, Archive=Archive, Cold archive=Archive
D) Active=Premium, Archive=Cool, Cold archive=Archive

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  BLOB STORAGE ACCESS TIERS                                            │
  │                                                                       │
  │  Tier      Storage Cost  Access Cost  Retrieval  Use Case            │
  │  ────────────────────────────────────────────────────────────────    │
  │  Premium   Highest       Lowest       Instant    Latency-sensitive  │
  │  Hot       High          Low          Instant    Frequent access    │
  │  Cool      Medium        Medium       Instant    Infrequent (30d+) │
  │  Cold      Lower         Higher       Instant    Rare (90d+)       │
  │  Archive   Lowest        Highest      Hours      Compliance/rarely │
  │            storage cost              (rehydrate) accessed          │
  │                                                                       │
  │  IMPORTANT: Archive tier requires "rehydration" before you can     │
  │  read the blob — takes hours. Not suitable for anything that might  │
  │  need to be accessed quickly.                                        │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — All Hot | ❌ Wrong | Paying hot tier prices for compliance-only data stored for years is extremely expensive. |
| **B — Hot/Cool/Archive** | ✅ Correct | **Hot:** Daily access — optimized for frequent reads, low access cost. **Cool:** Quarterly access — lower storage cost, acceptable access cost at that frequency. **Archive:** Compliance-only, almost never accessed — lowest storage cost, hours to retrieve is acceptable for compliance archives. |
| C — Active=Hot, rest=Archive | ❌ Wrong | Last year's documents accessed quarterly would have high retrieval cost in Archive tier plus hours of wait. Cool is the right middle ground. |
| D — Active=Premium | ❌ Wrong | Premium Blob Storage is for latency-sensitive workloads (databases, high-frequency trading). Standard Hot tier is sufficient for documents accessed multiple times daily. |

---

## Q30 Cosmos DB Multi-Region Write

**Scenario:** A global gaming app uses Cosmos DB. Players are in 3 regions (US, EU, Asia). Each player's session data is frequently updated from the player's location. Latency must be <50ms globally.

**Which Cosmos DB configuration is MOST appropriate?**

A) Single-region write with read replicas in EU and Asia
B) Multi-region writes with Session consistency
C) Multi-region writes with Strong consistency
D) Single-region write with Bounded Staleness consistency

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Single-region write | ❌ Wrong | Players in EU and Asia updating session data must route writes to US → round-trip latency easily >100ms. Violates <50ms requirement for writes. |
| **B — Multi-region writes + Session** | ✅ Correct | **Multi-region write:** Each player writes to their nearest region (<50ms). **Session consistency:** Each player's session sees their own writes immediately (read-your-writes). Other players' sessions may see slight staleness — acceptable for game session data. This is the standard pattern for globally distributed apps. |
| C — Multi-region writes + Strong | ❌ Wrong | Strong consistency with multi-region writes means every write must be acknowledged by all regions before returning — defeats the purpose. Latency would be dominated by cross-region network RTT (~100-200ms). Cannot achieve <50ms. |
| D — Single-region write + Bounded Staleness | ❌ Wrong | Still single-region writes — Asia and EU players have high write latency. Bounded Staleness doesn't fix the write path. |

---

## Q31 Azure Cache for Redis — Design Scenarios

**Scenario:** An API returns product recommendations computed from a machine learning model. The computation takes 3 seconds. The result is the same for 5 minutes. The API handles 500 requests/second.

**What is the MOST effective caching strategy?**

A) Enable HTTP response caching on the load balancer
B) Cache the ML recommendation results in Azure Cache for Redis with 5-minute TTL
C) Cache at the database query level
D) Use Azure CDN to cache API responses

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Load balancer caching | ❌ Wrong | Azure Load Balancers don't have HTTP response caching. Application Gateway has some capabilities, but it's designed for path routing/WAF, not API response caching with TTL control. |
| **B — Azure Cache for Redis** | ✅ Correct | Redis is purpose-built for this: cache the 3-second ML computation result with 5-minute TTL. Subsequent 500 requests/sec get sub-millisecond responses from Redis instead of triggering the 3-second ML computation. Redis supports complex data structures, expiry, eviction policies, and pub/sub. |
| C — Database query caching | ❌ Wrong | The bottleneck is the ML computation, not a database query. Database query caching (e.g., MySQL query cache) doesn't cache ML model outputs. |
| D — CDN | ❌ Wrong | Azure CDN caches static content and HTTP responses at the edge, but it requires `Cache-Control` headers and works best for static/semi-static content. API responses with per-user data or dynamic parameters don't cache well in CDN. Also, CDN doesn't give you programmatic TTL control or data structure flexibility. |

---

## Q32 Data Migration Strategy

**Scenario:** A company needs to migrate 500 TB of on-premises data to Azure Blob Storage. They have a 1 Gbps internet connection to Azure. Time is critical — must complete within 2 weeks.

**What is the MOST appropriate migration approach?**

A) AzCopy over the internet connection
B) Azure Data Box (physical device)
C) Azure Migrate with agent-based discovery
D) ExpressRoute with AzCopy

**✅ Answer: B**

```
  Network capacity check:
  1 Gbps = 125 MB/s = ~10.8 TB/day
  500 TB ÷ 10.8 TB/day = ~46 days minimum (100% utilization, no overhead)
  2-week deadline = 14 days → NOT POSSIBLE over 1 Gbps
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — AzCopy over internet | ❌ Wrong | Math: 500TB over 1 Gbps = ~46 days minimum. Cannot meet 2-week deadline. Network is the bottleneck. |
| **B — Azure Data Box** | ✅ Correct | Data Box is a ruggedized appliance (80-100 TB usable). Microsoft ships it to you. You copy data locally at disk speeds (much faster than internet). Then ship back to Microsoft who uploads to Azure datacenter. For 500 TB: 5-6 Data Boxes in parallel → easily within 2 weeks. The "offline transfer" approach when network is the bottleneck. |
| C — Azure Migrate | ❌ Wrong | Azure Migrate discovers and assesses workloads for migration — it's a planning/assessment tool, not a bulk data transfer tool. |
| D — ExpressRoute + AzCopy | ❌ Wrong | Even if you provisioned ExpressRoute in time (weeks of provisioning), 1 Gbps ExpressRoute has the same bandwidth limitation as internet. You'd need 10 Gbps ExpressRoute (very expensive, and still ~4-5 days at 100% utilization). Data Box remains the correct answer for 500TB in 2 weeks. |

---

## Q33 Azure SQL: Service Tier Selection

**Scenario:** An OLTP application has:
- Unpredictable traffic: sometimes 10 DTUs, sometimes 1000 DTUs
- SLA requirement: 99.99% uptime
- Development cost sensitivity: want to minimize cost during low-traffic periods

**Which Azure SQL Database service tier should you choose?**

A) Standard tier with fixed DTU
B) Serverless (General Purpose) with auto-pause
C) Business Critical tier
D) Hyperscale tier

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Standard fixed DTU | ❌ Wrong | Fixed DTU means you pay for the peak (1000 DTUs) even during low traffic periods. Wastes money on idle capacity. |
| **B — Serverless** | ✅ Correct | Serverless tier scales compute automatically between a configured min and max vCore. When idle, it auto-pauses (billing stops for compute). Perfect for unpredictable workloads where cost optimization during low traffic is required. General Purpose tier provides 99.99% SLA. |
| C — Business Critical | ❌ Wrong | Business Critical (formerly Premium) provides the highest performance and local SSD storage — it's for latency-sensitive, high-throughput workloads. Not suitable when cost minimization is a requirement (it's the most expensive tier). |
| D — Hyperscale | ❌ Wrong | Hyperscale is for databases that need to scale beyond the 4TB limit of other tiers or need extremely fast backups. Overkill for standard OLTP with variable load. |

---

## Q34 Encryption Design

**Scenario:** A company processes healthcare data (HIPAA). Requirement: encryption keys must be controlled by the company (not Microsoft), and they must be able to revoke Azure's access to data at any time.

**Which encryption approach meets this requirement?**

A) Azure-managed keys (default storage encryption)
B) Customer-Managed Keys (CMK) stored in Azure Key Vault
C) Customer-Managed Keys with Key Vault and BYOK (Bring Your Own Key) from on-premises HSM
D) Application-level encryption before storing in Azure

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Azure-managed keys | ❌ Wrong | Microsoft controls the keys. Company cannot revoke Azure's access — violates the requirement. |
| B — CMK in Key Vault | ❌ Partially | CMK means the company controls the key, but the key is stored in Azure Key Vault (Microsoft infrastructure). If Microsoft has access to Key Vault, they technically have access to the key. However, Key Vault HSM provides cryptographic isolation. |
| **C — CMK + BYOK from on-premises HSM** | ✅ Correct | BYOK (Bring Your Own Key): The encryption key is generated in the company's own on-premises HSM (Hardware Security Module), and the key material is imported into Azure Key Vault Managed HSM. The company retains the root of trust on-premises. They can revoke Azure's access by disabling or deleting the key in Key Vault. This meets the strictest interpretation of "company controls the key" for HIPAA. |
| D — Application-level encryption | ❌ Wrong | Valid technically, but adds enormous application complexity. Every read/write requires the application to handle encryption/decryption. Key management, rotation, and access control must all be coded. Native CMK is far more practical. |

---

## Q35 Azure Cognitive Search vs Azure AI Search Integration

**Scenario:** A legal firm has 10 million PDF and Word documents in Azure Blob Storage. Lawyers need to search documents by full-text content, filter by date range, case type, and attorney name. Results must be returned in <2 seconds.

**What is the BEST storage + search architecture?**

A) Azure SQL Database with LIKE queries
B) Azure Blob Storage + Azure AI Search (Cognitive Search) with blob indexer
C) Cosmos DB with SQL API
D) Azure Synapse Analytics for full-text search

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — SQL with LIKE | ❌ Wrong | LIKE queries don't scale to 10 million documents and are extremely slow without full-text indexes. SQL full-text search exists but is not optimized for unstructured document content. |
| **B — Blob Storage + Azure AI Search** | ✅ Correct | Keep original documents in Blob Storage. Azure AI Search (formerly Cognitive Search) indexes them via blob indexer: extracts text from PDFs/Word, creates searchable index, supports filters (date, case type, attorney) and full-text queries with relevance scoring. Sub-second queries at scale. This is the standard Azure document search architecture. |
| C — Cosmos DB | ❌ Wrong | Cosmos DB stores structured/semi-structured JSON — not optimized for storing PDF/Word files. You'd still need a search layer. |
| D — Synapse Analytics | ❌ Wrong | Synapse is a data warehouse for analytics (aggregations, joins, OLAP). It's not a document search engine. |

---

## Q36 Storage Account Networking Design

**Scenario:** An application running in an Azure Virtual Network needs to access an Azure Storage Account. The storage account must NOT be accessible from the internet. The solution must use Azure's backbone network (not the internet).

**Which approach should you use?**

A) Configure storage firewall to allow the VNet subnet
B) Private Endpoint for the storage account
C) Service Endpoint for the storage account
D) Both B and C achieve the same result — choose either

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  SERVICE ENDPOINT vs PRIVATE ENDPOINT                                 │
  │                                                                       │
  │  Service Endpoint:                                                    │
  │  ├── Adds VNet route to Azure service's PUBLIC IP                   │
  │  ├── Traffic stays on Azure backbone (not internet)                  │
  │  ├── Storage account still has a public endpoint                     │
  │  ├── Storage public endpoint can be restricted to specific VNets    │
  │  └── The service's IP is still public — just routing is optimized  │
  │                                                                       │
  │  Private Endpoint:                                                    │
  │  ├── Creates a PRIVATE IP in your VNet for the service              │
  │  ├── The service is accessible ONLY via private IP                  │
  │  ├── Public endpoint can be disabled entirely                        │
  │  ├── DNS resolves storage.blob.core.windows.net → private IP        │
  │  └── Most secure — service is truly private                         │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Storage firewall | ❌ Wrong | Firewall rules restrict access but the storage account still has a public endpoint. A misconfigured firewall or a bypass could expose it. |
| **B — Private Endpoint** | ✅ Correct | Private Endpoint places the storage account in your VNet with a private IP. Public endpoint can be disabled entirely. The storage account is completely inaccessible from the internet — only reachable via private IP in the VNet or connected networks (VPN/ExpressRoute). This is the strongest "not accessible from internet" guarantee. |
| C — Service Endpoint | ❌ Wrong | Service Endpoint keeps the storage account's public endpoint — it just restricts which VNets can reach it and routes traffic over Azure backbone. The account is still publicly addressed. If the requirement is "must NOT be accessible from internet," Service Endpoint doesn't fully satisfy it. |
| D — Same result | ❌ Wrong | They are not the same. Private Endpoint = fully private. Service Endpoint = optimized routing but still public endpoint. |

---

## Q37 Choosing Between Azure SQL DB Pricing Models

**Scenario:** You have 20 small databases each used by different clients. Each DB is small (5-10 GB) but the usage patterns are completely different — some spike at 09:00, others at 14:00.

**What is the MOST cost-effective SQL Database option?**

A) 20 × SQL Database Single Database, General Purpose
B) SQL Database Elastic Pool with shared DTUs/vCores
C) SQL Managed Instance
D) 20 × SQL Database Serverless

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — 20 × Single DB | ❌ Wrong | Each DB must have enough capacity for its own peak. If they peak at different times, you're paying for peak capacity that's idle most of the time across 20 databases. |
| **B — Elastic Pool** | ✅ Correct | Elastic Pool shares a pool of DTUs/vCores across multiple databases. Since peaks occur at different times, the pool's shared resources cover spikes without each database needing dedicated peak capacity. Perfect for multi-tenant SaaS where databases have complementary usage patterns. |
| C — SQL MI | ❌ Wrong | SQL Managed Instance is overkill for 20 small databases. MI has a minimum cost equivalent to many vCores. The compute cost would be dramatically higher than an Elastic Pool for small databases. |
| D — 20 × Serverless | ❌ Wrong | Serverless auto-scales and auto-pauses, which is good. But each Serverless database has its own compute budget. You lose the shared-pool benefit. For databases with complementary peaks, Elastic Pool is more cost-effective. |

---

## Q38 Cosmos DB Partition Key Selection

**Scenario:** A Cosmos DB container stores orders. Expected data: 10 million orders. Common queries:
- Get all orders for a specific customer (customerId)
- Get orders by status (pending/shipped/delivered)
- Get order by orderId

**Which partition key should you choose?**

A) `status` (pending/shipped/delivered)
B) `orderId`
C) `customerId`
D) A compound key: `customerId + orderId`

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  COSMOS DB PARTITION KEY RULES                                        │
  │                                                                       │
  │  ✅ Good partition key:                                               │
  │     - High cardinality (many unique values)                          │
  │     - Evenly distributes data across partitions                      │
  │     - Matches your most common query pattern                         │
  │     - Doesn't create "hot partitions" (one partition >> others)      │
  │                                                                       │
  │  ❌ Bad partition key:                                                │
  │     - Low cardinality (e.g., status: only 3 values = 3 partitions)  │
  │     - All data goes to one partition (hot partition)                 │
  │     - Requires cross-partition queries for most lookups              │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — `status` | ❌ Wrong | Only 3 values (pending/shipped/delivered). Creates 3 partitions with massive data skew — most orders are "delivered" = massive hot partition. Low cardinality = poor distribution. |
| B — `orderId` | ❌ Partially | High cardinality (good distribution). But "get all orders for a customer" becomes a cross-partition query — expensive and slow. Doesn't match the most common query pattern. |
| **C — `customerId`** | ✅ Correct | High cardinality (many customers = good distribution). Most common query (orders by customer) is a single-partition query — fast and cheap. Occasional cross-partition queries (by status, by orderId) are acceptable for rare operations. |
| D — Compound key | ❌ Wrong | Creating a synthetic compound key makes orderId lookups efficient but forces all customer queries to be cross-partition (you don't know the full compound key without orderId). Adds complexity without improving the key query pattern. |

---

## Q39 Immutable Blob Storage for Compliance

**Scenario:** A financial company must store transaction records so they cannot be deleted or modified for 7 years (SEC compliance). Even storage account administrators must not be able to delete or overwrite data during the retention period.

**Which feature should you use?**

A) Azure Storage soft delete with 7-year retention
B) Azure Blob Storage immutable storage with time-based retention policies (WORM)
C) Azure Backup with 7-year retention
D) Azure Site Recovery

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Soft delete | ❌ Wrong | Soft delete prevents accidental deletion and allows recovery, but admins CAN permanently delete data. Doesn't satisfy "even admins cannot delete." |
| **B — Immutable WORM** | ✅ Correct | WORM (Write Once Read Many) policies lock data. During the retention period, nobody — including storage account owners or subscription admins — can delete or overwrite blobs. The policy can be locked (irrevocable) to satisfy regulatory requirements like SEC 17a-4. This is exactly what SEC/FINRA/HIPAA compliance requires. |
| C — Azure Backup | ❌ Wrong | Azure Backup retains backup data, but it's designed for recovery, not compliance immutability of original records. Backup admins can delete backups. |
| D — Azure Site Recovery | ❌ Wrong | ASR is a disaster recovery service for replicating VMs — not a compliance data retention tool. |

---

## Q40 ⭐ Data Redundancy for PostgreSQL

**Scenario:** An Azure Database for PostgreSQL Flexible Server hosts a critical application. Requirements:
- Automatic failover with <30 second RTO
- Data must survive zone failure
- Minimum 99.99% uptime SLA

**Which configuration should you choose?**

A) Single server, locally redundant backup
B) Flexible Server with Zone-Redundant HA
C) Flexible Server with Same-Zone HA
D) Read replica in secondary region

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Single server | ❌ Wrong | Single server has no automatic failover and doesn't survive zone failures. Maximum SLA is lower than 99.99%. |
| **B — Zone-Redundant HA** | ✅ Correct | Zone-Redundant HA deploys primary and standby in different availability zones. Automatic failover in <30 seconds on zone failure or server failure. Provides 99.99% SLA — matches requirement. Data is synchronously replicated to the standby. |
| C — Same-Zone HA | ❌ Wrong | Same-Zone HA has primary and standby in the same availability zone. Provides protection against server failure but NOT zone failure. Doesn't meet the zone-failure survival requirement. |
| D — Read replica | ❌ Wrong | Read replicas are for read scaling and manual disaster recovery. They use asynchronous replication and don't provide automatic failover. Not suitable for <30s RTO. |

---

## Q41 Azure Search: Skillsets and Cognitive Enrichment

**Scenario:** A company wants to index scanned handwritten forms stored in PDF format in Blob Storage. They need to extract form fields, understand the handwritten text, and make it searchable.

**What Azure AI Search feature enables this?**

A) Standard blob indexer
B) Custom analyzer in the search index
C) AI enrichment pipeline with built-in cognitive skills (OCR + Form Recognizer)
D) Azure Synapse Link with AI Search

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Standard blob indexer | ❌ Wrong | Standard indexer extracts text from typed PDFs via text extraction. It cannot handle scanned images or handwritten content — no OCR capability. |
| B — Custom analyzer | ❌ Wrong | Analyzers control how text is tokenized for the search index. They don't extract text from images. |
| **C — AI enrichment with cognitive skills** | ✅ Correct | Azure AI Search skillsets allow a pipeline of cognitive skills to run during indexing: OCR skill extracts text from scanned images, Form Recognizer skill (Document Intelligence) extracts structured form fields, and the results are mapped to the search index. This is the complete solution for handwritten scanned forms. |
| D — Synapse Link | ❌ Wrong | Synapse Link provides analytics integration with Cosmos DB/SQL — not related to document OCR and search indexing. |

---

## Q42 Azure Files vs Azure Blob for Lift-and-Shift

**Scenario:** A company is migrating an on-premises application that uses a shared network drive (SMB) for storing user-uploaded files. 10 users access the same files simultaneously. The migration must require ZERO code changes in the application.

**What should they use?**

A) Azure Blob Storage with custom REST API integration
B) Azure Files (SMB share) mounted as a drive
C) Azure Data Lake Storage Gen2
D) Azure NetApp Files

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Blob Storage + REST API | ❌ Wrong | Requires code changes — application must use Azure Storage SDK/REST instead of file system operations. Violates "zero code changes." |
| **B — Azure Files SMB** | ✅ Correct | Azure Files provides a fully managed SMB file share. It can be mounted as a drive on Windows/Linux VMs using the same UNC path format as on-premises. The application continues to read/write files via SMB with ZERO code changes. Supports concurrent access from multiple clients. |
| C — ADLS Gen2 | ❌ Wrong | ADLS is accessed via REST/HDFS APIs — not SMB. Code changes required. Designed for analytics, not lift-and-shift applications. |
| D — Azure NetApp Files | ❌ Wrong | NetApp Files provides enterprise NFS/SMB at very high performance — valid, but significantly more expensive than Azure Files. For a standard file share migration, Azure Files is the appropriate choice. NetApp is for HPC, databases, and high-performance workloads. |

---

## Q43 Azure Table Storage: When to Use

**Scenario:** Which use case is BEST suited for Azure Table Storage?

A) Storing 1 billion rows of structured IoT sensor data requiring complex SQL queries
B) Storing user session state as key-value pairs — 10 million users, accessed by session ID
C) Storing hierarchical JSON documents with cross-document transactions
D) Full-text search across product descriptions

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Complex SQL queries | ❌ Wrong | Table Storage doesn't support SQL queries, joins, or complex filtering. For 1 billion rows with complex queries, use Azure Data Explorer or Synapse. |
| **B — Session state by key** | ✅ Correct | Table Storage is a simple key-value + attribute store. Storing session data accessed by session ID (the key) is exactly its sweet spot: extremely cheap, massive scale, simple lookups by PartitionKey+RowKey. No complex query requirements = Table Storage wins on cost. |
| C — JSON documents + transactions | ❌ Wrong | Table Storage doesn't support cross-entity transactions (except within a single partition). For JSON documents with ACID transactions, use Cosmos DB. |
| D — Full-text search | ❌ Wrong | Table Storage has no full-text search capability. Use Azure AI Search for this. |

---

## Q44 Azure Database Migration Service

**Scenario:** You need to migrate a 500 GB SQL Server 2016 database from on-premises to Azure SQL Managed Instance with MINIMAL downtime (production system).

**Which migration mode should you use with Azure Database Migration Service?**

A) Offline migration — backup and restore
B) Online migration (continuous sync) with cutover window
C) Azure Data Factory pipeline
D) BACPAC export/import

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Offline migration | ❌ Wrong | Offline migration takes the source database offline during migration. For a 500 GB database, this could mean many hours of downtime. |
| **B — Online migration with cutover** | ✅ Correct | Online migration with DMS: (1) Full backup restores to MI while source stays online. (2) Continuous transaction log backup and replay keeps MI in sync. (3) When ready, you cut over with a small window (minutes) during which the final logs are applied. Minimizes production downtime. |
| C — Azure Data Factory | ❌ Wrong | ADF is designed for data movement/ETL pipelines. While it can move data, it doesn't handle SQL Server-specific migration concerns (schema, stored procs, indexes, log-based sync). DMS is the right tool. |
| D — BACPAC export/import | ❌ Wrong | BACPAC export takes a logical backup of the database. For 500 GB, export + import takes many hours and the source must essentially be static during export. Very high downtime. |

---

## Q45 Data Residency and Sovereignty

**Scenario:** A European company must ensure that ALL customer data stays within the EU. They use Azure SQL Database, Blob Storage, and Cosmos DB.

**What must they configure to guarantee data residency?**

A) Select EU regions and enable Azure Policy to deny deployments outside EU
B) Enable GDPR compliance setting in Azure portal
C) Select EU regions only — Azure automatically handles data residency
D) Use private endpoints — they prevent data from leaving the region

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — EU regions + Azure Policy** | ✅ Correct | Choosing EU regions ensures data is stored in EU datacenters. But someone could accidentally deploy resources in US East! Azure Policy with `Deny` effect on `allowedLocations` (restricted to EU region list) prevents any resource from being created outside approved EU regions. This combination technically enforces data residency. |
| B — GDPR setting | ❌ Wrong | There's no single "enable GDPR compliance" toggle in Azure. GDPR compliance is achieved through technical controls (data residency, encryption, access controls, audit logs) — not a checkbox. |
| C — Regions + auto-handling | ❌ Wrong | Azure doesn't automatically prevent cross-region replication or data movement. GRS (geo-redundant storage) replicates to a paired region outside EU unless you specifically choose ZRS or LRS. RA-GRS for European storage often pairs with non-EU regions. |
| D — Private endpoints | ❌ Wrong | Private endpoints control network access to services from your VNet — they don't prevent data from being stored or replicated to another region. |

---

# Domain 3: Design Business Continuity Solutions

---

## Q46 ⭐ RTO vs RPO: Definition

**Scenario:** A company's SLA states: "In a disaster, we must restore the system within 4 hours. We can accept losing up to 1 hour of data."

**Identify the correct mapping.**

A) RTO = 1 hour, RPO = 4 hours
B) RTO = 4 hours, RPO = 1 hour
C) RTO = 4 hours, RPO = 0 hours
D) RTO = 0 hours, RPO = 1 hour

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  RTO vs RPO                                                           │
  │                                                                       │
  │  RPO (Recovery Point Objective):                                      │
  │  "How much DATA can we afford to lose?"                              │
  │  = Maximum age of data to restore                                    │
  │  = Frequency of backups needed                                       │
  │  RPO = 1 hour → must backup every 1 hour                            │
  │                                                                       │
  │  RTO (Recovery Time Objective):                                       │
  │  "How long can the system be DOWN?"                                  │
  │  = Maximum acceptable downtime duration                              │
  │  = How fast the system must be restored                              │
  │  RTO = 4 hours → system must be running within 4 hours of disaster  │
  │                                                                       │
  │  Timeline:                                                            │
  │  [last backup] ←─── RPO ───→ [disaster] ←─── RTO ───→ [restored]  │
  │       ↑                                                     ↑        │
  │  Data from here                                    System is        │
  │  may be lost                                       back online      │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — RTO=1h, RPO=4h | ❌ Wrong | RTO and RPO are swapped. |
| **B — RTO=4h, RPO=1h** | ✅ Correct | **RTO=4 hours:** system can be down for up to 4 hours. **RPO=1 hour:** can lose up to 1 hour of data → must have backups at least every hour. |
| C — RPO=0 | ❌ Wrong | RPO=0 means ZERO data loss — requires synchronous replication, not just "lose up to 1 hour." |
| D — RTO=0 | ❌ Wrong | RTO=0 means instant failover with zero downtime — requires active-active configuration. The scenario states 4 hours is acceptable. |

---

## Q47 ⭐ Azure Backup vs Azure Site Recovery

**Scenario:** Match each requirement to the correct service:

- **A:** Virtual Machines must be recoverable if a file is accidentally deleted from inside the VM
- **B:** If the entire Azure region fails, the application must be recovered in another region within 1 hour

A) A=Azure Backup, B=Azure Site Recovery
B) A=Azure Site Recovery, B=Azure Backup
C) A=Azure Backup, B=Azure Backup (geo-redundant)
D) A=ASR, B=ASR

**✅ Answer: A**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  AZURE BACKUP vs AZURE SITE RECOVERY                                  │
  │                                                                       │
  │  Azure Backup:                                                        │
  │  ├── Point-in-time recovery                                          │
  │  ├── Recover files, folders, or entire VMs/databases                 │
  │  ├── Backup retention (days to years)                                │
  │  ├── Use for: accidental deletion, corruption, ransomware recovery   │
  │  └── RPO: hours to days (backup frequency)                          │
  │                                                                       │
  │  Azure Site Recovery (ASR):                                           │
  │  ├── Continuous replication of VMs to another region                │
  │  ├── Orchestrated failover (test failover + actual failover)         │
  │  ├── Use for: regional disaster, datacenter failure                  │
  │  ├── RPO: seconds to minutes (continuous replication)               │
  │  └── RTO: minutes to hours (depending on complexity)                │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Backup for accidental delete, ASR for regional DR** | ✅ Correct | **Azure Backup:** Restores files from within a VM — exactly what you need for accidental deletion. Provides point-in-time recovery of VM data. **ASR:** Continuously replicates VMs to a secondary region. When region fails, orchestrated failover brings VMs up in secondary region within minutes-to-hour (1-hour RTO is achievable). |
| B — Swapped | ❌ Wrong | ASR doesn't help with accidental file deletion inside a VM — it replicates the VM state, including the deletion. Backup doesn't help with regional DR — it's not a live replication tool. |
| C — Both Backup | ❌ Wrong | GRS backups can be used for regional DR in a basic sense, but recovery from backup in another region takes much longer than 1 hour for a complex application. |
| D — Both ASR | ❌ Wrong | ASR replicates continuously — if a file is accidentally deleted, the deletion is replicated instantly. ASR can't restore to "before the deletion" without backup. |

---

## Q48 Availability Sets vs Availability Zones vs Region Pairs

**Scenario:** Which architecture protects against each failure type?

| Failure Type | Protection |
|---|---|
| Single server hardware failure | ? |
| Single datacenter failure | ? |
| Entire Azure region failure | ? |

A) All three: Availability Zone → Zone → Region Pair
B) Availability Set → Availability Zone → Region Pair
C) Availability Zone → Availability Set → Region Pair
D) Availability Set → Region Pair → Availability Zone

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  REDUNDANCY LEVELS                                                    │
  │                                                                       │
  │  Availability Set:                                                    │
  │  ├── 2+ VMs in same datacenter, different fault/update domains      │
  │  ├── If one rack fails → other VMs on different racks stay up       │
  │  ├── Protects against: single server, rack, switch failure          │
  │  └── Does NOT protect: whole datacenter/zone failure                │
  │                                                                       │
  │  Availability Zone:                                                   │
  │  ├── 2+ VMs across 2+ physically separate datacenters in a region   │
  │  ├── If one datacenter fails → other zones stay up                  │
  │  ├── Protects against: single datacenter failure                    │
  │  └── Does NOT protect: entire region failure                        │
  │                                                                       │
  │  Region Pair (with ASR/GRS):                                         │
  │  ├── Replication to a second region hundreds of miles away          │
  │  ├── If one region fails → failover to pair region                  │
  │  └── Protects against: entire Azure region failure                  │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — All Zone → Zone → Region | ❌ Wrong | AZ does not protect against a single server hardware failure specifically (it protects against datacenter-level failures). |
| **B — AS → AZ → Region Pair** | ✅ Correct | **Availability Set** → rack/server-level fault tolerance within one datacenter. **Availability Zone** → datacenter-level resilience within one region. **Region Pair** → region-level disaster recovery. |
| C — Zone → Set → Region | ❌ Wrong | Swapped AS and AZ. |
| D — Set → Pair → Zone | ❌ Wrong | Region Pair is for regional-level DR, not datacenter-level. |

---

## Q49 SQL Database Business Continuity

**Scenario:** Azure SQL Database (Business Critical tier) is your primary database. Requirements:
- RPO: ≤5 seconds
- RTO: ≤30 seconds
- Must survive a zone failure
- MUST remain readable during a zone failure

**What combination achieves all requirements?**

A) Zone-redundant Business Critical + geo-replication
B) Zone-redundant Business Critical — built-in features are sufficient
C) Business Critical + active geo-replication to secondary region
D) Standard tier + automatic failover group

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Zone-redundant + geo-replication | ❌ Wrong | Overkill for zone failure. Geo-replication adds cost and complexity. The zone failure scenario doesn't require cross-region capability. |
| **B — Zone-redundant Business Critical** | ✅ Correct | Business Critical tier ALREADY includes: built-in read replicas (HA replicas) that are always-on and readable, synchronous replication with RPO ~0 (actually ≤5 sec), automatic failover in ~30 seconds, and built-in zone redundancy when you enable it. All requirements are met by the built-in BC features — no additional geo-replication needed. |
| C — Geo-replication to secondary | ❌ Wrong | Cross-region geo-replication is for regional DR (region-level failure), not zone failure. Adds cost and latency. Doesn't improve zone-level RTO/RPO. |
| D — Standard + failover group | ❌ Wrong | Standard tier doesn't have Business Critical's built-in HA replicas. Failover groups use asynchronous replication — RPO could be minutes, not ≤5 seconds. |

---

## Q50 Active-Active vs Active-Passive

**Scenario:** Which deployment model is CORRECT for each requirement?

- **A:** Must handle 2× load at all times. Can survive a full region failure with ZERO degradation.
- **B:** Must survive a full region failure. During normal operation, secondary region is unused (cost savings). Brief downtime during failover is acceptable.

A) A=Active-Passive, B=Active-Active
B) A=Active-Active, B=Active-Passive
C) Both Active-Active
D) Both Active-Passive with warm standby

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Active-Passive first | ❌ Wrong | "Zero degradation during region failure" requires both regions to be active simultaneously. Active-Passive would mean the entire load shifts to the secondary during failover — if both together handle 2× load, then either alone must handle 1× load. |
| **B — Active-Active first, Active-Passive second** | ✅ Correct | **Active-Active:** Both regions serve live traffic. If one fails, the other already handles traffic — no failover lag, no degradation. Must have capacity in each region to handle full load (or load balancer redistributes traffic). **Active-Passive:** Secondary is warm standby, not serving traffic. Lower cost during normal operation. Brief downtime during failover (DNS cutover, connection pool refresh). Matches "brief downtime is acceptable, cost savings." |
| C/D | ❌ Wrong | Don't match both requirements appropriately. |

---

## Q51 Azure Front Door for Global HA

**Scenario:** A web application is deployed in East US and West Europe. You need:
- Automatic failover if one region's application fails
- Latency-based routing so users go to the nearest region
- DDoS protection and WAF at the edge

**Which Azure service provides ALL three?**

A) Azure Traffic Manager
B) Azure Load Balancer
C) Azure Front Door (Standard or Premium)
D) Azure Application Gateway

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Traffic Manager | ❌ Wrong | Traffic Manager does DNS-based global routing and failover. But it works at DNS level only: no WAF, no DDoS protection, no caching, no SSL offload. |
| B — Load Balancer | ❌ Wrong | Azure Load Balancer is regional (within one region), not global. No WAF, no multi-region routing. |
| **C — Azure Front Door** | ✅ Correct | Front Door is a global HTTP load balancer with: **Latency-based routing** (Anycast — directs users to nearest PoP), **Health probes + automatic failover** between origins, **WAF** (Web Application Firewall at the edge), **DDoS protection** (through integration with Azure DDoS). All three requirements met by one service. |
| D — Application Gateway | ❌ Wrong | App Gateway is regional. It has WAF, but no global routing, no latency-based multi-region failover. Use App Gateway behind Front Door for regional routing + WAF (layer 2 approach). |

---

## Q52 Azure Backup: Retention and Vault Design

**Scenario:** You must back up 50 VMs across 3 subscriptions. Recovery points must be retained:
- Daily: 30 days
- Weekly: 12 weeks
- Monthly: 12 months
- Yearly: 5 years

**What is the BEST Recovery Services Vault design?**

A) One Recovery Services Vault per VM (50 vaults)
B) One Recovery Services Vault per subscription (3 vaults)
C) One centralized Recovery Services Vault in a hub subscription
D) One Recovery Services Vault per region where VMs are deployed

**✅ Answer: D**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Per VM | ❌ Wrong | 50 vaults is unmanageable and adds significant administrative overhead. No benefit over fewer vaults. |
| B — Per subscription | ❌ Wrong | Recovery Services Vaults are regional — if a subscription has VMs in multiple regions, one vault per subscription can still be too coarse. |
| C — One centralized vault | ❌ Wrong | Recovery Services Vaults are regional — you cannot use a vault in East US to back up VMs in West Europe. You MUST have a vault in each region where VMs reside. |
| **D — Per region** | ✅ Correct | Recovery Services Vaults are regional resources. Best practice: one vault per region (per subscription or shared across subscriptions via Azure Lighthouse). The retention policy (GFS: Grandfather-Father-Son — daily/weekly/monthly/yearly) is configured as a Backup Policy within each vault. This meets all the retention requirements. |

---

## Q53 Cosmos DB Backup

**Scenario:** Cosmos DB hosts your application's primary database. You need to be able to restore to any point in time within the last 7 days (continuous backup).

**What Cosmos DB backup mode should you enable?**

A) Periodic backup with 24-hour interval
B) Continuous backup mode (7-day retention)
C) Export to Azure Storage with Logic App trigger every hour
D) Geo-replication to secondary region

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Periodic backup | ❌ Wrong | Periodic backup takes snapshots every 1–24 hours. If you need to restore to "any point in time within 7 days," the periodic backup can only restore to the snapshots taken — you'd lose data between snapshots. |
| **B — Continuous backup** | ✅ Correct | Continuous backup mode (an option when creating Cosmos DB) stores every transaction change feed continuously. You can restore to ANY second within the last 7 or 30 days (tier dependent). Perfect for point-in-time recovery (PITR). |
| C — Logic App export | ❌ Wrong | Exporting data hourly to Storage is not a proper backup — it requires custom code, doesn't capture deletes, and restoring requires custom import logic. |
| D — Geo-replication | ❌ Wrong | Geo-replication is for disaster recovery and read scaling — it replicates changes in near-real-time, including accidental deletes and corruption. It's NOT a backup — it doesn't protect against data corruption or accidental deletion. |

---

## Q54 VM Scale Set Autoscale Design

**Scenario:** A web app runs on a VM Scale Set. Traffic is predictable: high 08:00–18:00, very low overnight. Sudden spikes can occur during sales events. 

**What autoscale configuration should you use?**

A) Only metric-based autoscale (CPU > 80% = scale out)
B) Only schedule-based autoscale (scale to 10 at 08:00, scale to 2 at 18:00)
C) Schedule-based autoscale for predictable traffic + metric-based for spike handling
D) Fixed instance count with the maximum needed for peak traffic

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Metrics only | ❌ Wrong | If traffic spikes suddenly, metric-based scale-out takes time (VMs take minutes to provision and warm up). By the time VMs are ready, the spike may have already caused errors. |
| B — Schedule only | ❌ Wrong | Schedule handles predictable patterns but can't react to sudden unexpected spikes during business hours or outside the scheduled window. |
| **C — Schedule + Metrics** | ✅ Correct | **Schedule-based:** Pre-scale to known capacity before 08:00 (avoiding cold starts). **Metric-based:** On top of the scheduled baseline, if CPU/requests spike, scale out further automatically. This is the recommended autoscale pattern — schedule for predictable load, metrics for unexpected spikes. |
| D — Fixed max count | ❌ Wrong | Pay for maximum capacity 24/7 even during overnight low traffic. Extremely cost-inefficient. |

---

## Q55 Multi-Region AKS Design

**Scenario:** You need a globally available Kubernetes-based application across East US and West Europe. Requirements:
- Users should always reach the nearest region
- If one region's AKS cluster fails, traffic must automatically route to the other
- Deployment must be consistent across both clusters

**What is the recommended architecture?**

A) One large AKS cluster with nodes across both regions
B) Two separate AKS clusters + Azure Front Door for routing + GitOps for consistent deployment
C) One AKS cluster with Azure Traffic Manager
D) AKS with Availability Zones in one region only

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — One cluster, cross-region nodes | ❌ Wrong | AKS clusters are regional — you cannot have nodes from different regions in one cluster (too much latency for etcd/control plane communication). |
| **B — Two AKS clusters + Front Door + GitOps** | ✅ Correct | **Two clusters:** One in each region — independent failure domains. **Azure Front Door:** Global load balancing with latency-based routing and automatic health-probe-based failover. **GitOps (e.g., Flux/ArgoCD):** Ensures both clusters always have identical configuration from the same Git source. This is the standard multi-region AKS architecture. |
| C — One cluster + Traffic Manager | ❌ Wrong | AKS is regional — one cluster can't span regions. Traffic Manager routes DNS, but with one cluster, there's no second region to fail over to. |
| D — One region with AZs | ❌ Wrong | AZs protect against datacenter failure within a region but not full region failure. Doesn't meet "global availability" requirement. |

---

## Q56 SQL Auto-Failover Groups

**Scenario:** Azure SQL Database needs to automatically failover to a secondary region with NO manual intervention if the primary region becomes unavailable. Application connection strings must NOT change after failover.

**Which feature should you use?**

A) Active geo-replication with manual failover
B) Auto-failover groups
C) Azure Site Recovery for SQL Database
D) Azure Database Migration Service

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Geo-replication + manual failover | ❌ Wrong | Active geo-replication provides a readable secondary in another region, but failover requires a manual `az sql db replica set-primary` command. Not automatic. Also, connection strings change after failover (you must point to the secondary server endpoint). |
| **B — Auto-failover groups** | ✅ Correct | Auto-failover groups add two features on top of geo-replication: (1) **Automatic failover** — if the primary region is unreachable, failover happens automatically based on the failover policy. (2) **Listener endpoints** — the group provides a read-write listener and read-only listener endpoint that DON'T change after failover. Application connection strings remain the same. |
| C — Azure Site Recovery for SQL | ❌ Wrong | ASR replicates VMs — if SQL is on Azure SQL Database (PaaS), ASR doesn't apply. ASR is for IaaS SQL Server on VMs. |
| D — DMS | ❌ Wrong | DMS is a one-time migration tool, not a continuous replication and failover solution. |

---

## Q57 Backup Strategy for Blob Storage

**Scenario:** A company stores customer uploaded images in Azure Blob Storage. Images may be accidentally deleted by a bug or malicious action. You need to be able to recover any accidentally deleted image from the last 30 days.

**What is the SIMPLEST solution?**

A) Daily Azure Backup for Azure Blob Storage
B) Enable Blob soft delete with 30-day retention
C) Copy blobs to a secondary storage account every night
D) Enable Azure Storage versioning

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Azure Backup for Blobs | ❌ Wrong | Azure Backup for Blob Storage is a valid solution but adds complexity (backup vault, policies). For the scenario of recovering accidentally deleted blobs, soft delete is simpler and achieves the same goal. |
| **B — Soft delete** | ✅ Correct | Blob soft delete retains deleted blobs as "soft-deleted" for the configured retention period (up to 365 days). When a blob is deleted, it's not immediately removed — you can undelete it within 30 days. Simplest setting — one toggle in the storage account. No additional infrastructure. |
| C — Nightly copy | ❌ Wrong | If a blob is deleted at 10:00 and you need it at 15:00, you'd have to wait until the next night's copy ran. You'd lose up to 24 hours of data. More complex to implement. |
| D — Storage versioning | ❌ Wrong | Versioning is good but doesn't directly recover deleted blobs (it keeps previous versions on overwrite). For deletions, versioning creates a "delete marker" — you must also manage version lifecycle. Soft delete is simpler for the exact scenario described. |

---

## Q58 Azure Storage — Geo-Redundant vs Zone-Redundant Backup

**Scenario:** A company needs their Azure SQL Database backups to survive a complete regional failure. Which backup redundancy option should they configure?

A) Locally Redundant (LRS) backups
B) Zone-Redundant (ZRS) backups  
C) Geo-Redundant (GRS) backups
D) Standard backups (default option)

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — LRS | ❌ Wrong | LRS keeps 3 copies within a single datacenter. Zone failure or region failure = backup data also lost. |
| B — ZRS | ❌ Wrong | ZRS keeps copies across availability zones in a single region. Survives zone failure, but NOT a full regional failure — all zones in the same region fail simultaneously in a regional disaster. |
| **C — GRS** | ✅ Correct | GRS replicates backup data to a paired Azure region. If the primary region fails completely, backups exist in the secondary region. Azure SQL Database automated backups support LRS, ZRS, and GRS — select GRS for regional DR protection. |
| D — Default | ❌ Wrong | Default backup redundancy has changed over time and varies by region. Never rely on "default" for critical compliance requirements — explicitly configure GRS. |

---

## Q59 Recovery Time for Different Workloads

**Scenario:** Rank the following approaches by RTO from FASTEST to SLOWEST:

1. Active-Active multi-region (always on)
2. Active-Passive with hot standby (warm ready)
3. Restore from Azure Backup in secondary region
4. Azure Site Recovery with orchestrated failover

A) 1 → 2 → 4 → 3
B) 1 → 4 → 2 → 3
C) 2 → 1 → 4 → 3
D) 1 → 2 → 3 → 4

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Active-Active → Hot Standby → ASR → Backup Restore** | ✅ Correct | **Active-Active (~0 RTO):** Traffic already flowing to both regions — no failover needed, DNS change at most. **Hot Standby (~minutes):** Standby is running and synced. DNS change or load balancer update routes traffic. **ASR failover (~minutes to ~1 hour):** Orchestrated failover, VM boot time, application startup, DNS propagation. **Backup restore (hours):** Download backup, provision infrastructure, restore data, configure, test. Longest possible RTO. |
| B — Swap ASR and hot standby | ❌ Wrong | Hot standby (already running, just redirect traffic) is faster than ASR (must boot VMs and wait for replication cutover). |
| C/D — Wrong order | ❌ Wrong | Various incorrect orderings. |

---

## Q60 Azure Traffic Manager vs Front Door: HA Routing

**Scenario:** A global application serves both HTTP/HTTPS web traffic AND TCP-based custom protocol traffic. You need health-based global failover for both.

**What should you use?**

A) Azure Front Door for both
B) Azure Traffic Manager for both
C) Azure Front Door for HTTP/HTTPS, Azure Traffic Manager for TCP
D) Azure Application Gateway for both

**✅ Answer: C**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Front Door for both | ❌ Wrong | Azure Front Door only supports HTTP/HTTPS traffic. It cannot route or health-check TCP or non-HTTP protocols. |
| B — Traffic Manager for both | ❌ Partially | Traffic Manager uses DNS-based routing — it works for ANY protocol (including TCP custom protocols) because it doesn't handle the actual traffic — it just resolves DNS. But Front Door is better for HTTP/HTTPS (edge caching, WAF, lower latency via Anycast). |
| **C — Front Door (HTTP) + Traffic Manager (TCP)** | ✅ Correct | **Front Door:** HTTP/HTTPS with WAF, caching, latency-based routing, health probes at Layer 7. **Traffic Manager:** DNS-based global routing with health probes for the TCP custom protocol — Traffic Manager's health probes support TCP port checks and HTTP endpoint checks. Best tool for each protocol. |
| D — App Gateway for both | ❌ Wrong | App Gateway is regional (not global) and handles HTTP/HTTPS only. Cannot do multi-region failover or TCP custom protocol routing. |

---

# Domain 4: Design Infrastructure Solutions

---

## Q61 ⭐ Compute Decision: When to Use Each Service

**Scenario:** Match each workload to the BEST compute option:

- **A:** 10,000 identical stateless batch image-processing jobs, each runs 5 seconds, needed once per day
- **B:** A legacy monolithic ASP.NET application requiring Windows Server 2019
- **C:** A microservices application with 20 services requiring independent scaling and container isolation

A) A=Azure Functions, B=Azure App Service, C=AKS
B) A=Azure Container Instances (ACI), B=Azure VM, C=AKS
C) A=Azure Batch, B=Azure VM, C=Azure Container Apps
D) A=Azure Functions, B=Azure VM, C=Azure Container Apps

**✅ Answer: A**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  COMPUTE DECISION TREE                                                │
  │                                                                       │
  │  Serverless event-driven?     → Azure Functions                     │
  │  Stateless web/API?           → App Service (PaaS)                  │
  │  Long-running parallel batch? → Azure Batch                         │
  │  Short-lived containers?      → Azure Container Instances (ACI)     │
  │  Microservices, full K8s?     → AKS                                 │
  │  Microservices, simplified?   → Azure Container Apps               │
  │  Need OS access/custom config?→ Azure VMs (IaaS)                   │
  │  Legacy app, no code changes? → Azure VMs or App Service            │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Functions, App Service, AKS** | ✅ Correct | **Functions:** 10,000 short-lived event-driven jobs (5 seconds each, no persistent state) = perfect serverless Functions use case. **App Service:** ASP.NET is natively supported by Windows App Service — PaaS, no OS management, auto-scale, built-in Windows Server support. **AKS:** 20 microservices with container isolation, independent scaling = Kubernetes is the right orchestrator. |
| B — ACI for batch | ❌ Wrong | ACI can run individual containers but doesn't manage 10,000 parallel jobs natively. Azure Functions or Batch is better for coordinating parallel job execution at scale. |
| C — Batch for batch | ❌ Partially | Azure Batch is excellent for parallel batch processing, but for simple 5-second independent jobs triggered once daily, Functions is simpler and equally capable. Container Apps for 20 microservices is valid but AKS is preferred when full Kubernetes control is needed. |
| D — Functions + VM | ❌ Wrong | Using VMs for a legacy ASP.NET app works but App Service (PaaS) is better — less management overhead, built-in load balancing, and staging slots. |

---

## Q62 ⭐ AKS Networking: kubenet vs Azure CNI

**Scenario:** Your AKS cluster will run 500 pods. Pods must be directly accessible from other Azure resources (Azure SQL, on-premises via ExpressRoute) using pod IP addresses. There's no room for IP waste.

**Which AKS networking plugin should you choose?**

A) kubenet (basic networking)
B) Azure CNI (Container Network Interface)
C) Calico plugin
D) NGINX Ingress Controller

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  kubenet vs Azure CNI                                                 │
  │                                                                       │
  │  kubenet:                                                             │
  │  ├── Pods get IPs from a private pod CIDR (not your VNet)          │
  │  ├── Pods NOT directly accessible from VNet without NAT             │
  │  ├── NAT occurs when pod traffic leaves the node                    │
  │  ├── Fewer VNet IPs consumed (only node IPs from VNet)             │
  │  └── Good for: simple workloads not needing direct pod access      │
  │                                                                       │
  │  Azure CNI:                                                           │
  │  ├── Pods get REAL VNet IP addresses                                │
  │  ├── Pods directly accessible from VNet (SQL, on-premises, etc.)   │
  │  ├── Requires pre-allocating VNet IPs for all pods                 │
  │  ├── Uses more VNet IP space                                        │
  │  └── Good for: direct pod connectivity requirements                │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — kubenet | ❌ Wrong | kubenet uses NAT for pod outbound traffic — pods don't have VNet IPs. Azure SQL or on-premises resources cannot initiate connections to specific pods. "Directly accessible by pod IP" requirement cannot be met with kubenet. |
| **B — Azure CNI** | ✅ Correct | Azure CNI assigns VNet IPs to pods. Pod IPs are routable within the VNet, to peered VNets, and over ExpressRoute to on-premises. Azure SQL can be configured to allow connections from pod IP ranges. Meets the "direct pod IP access" requirement. The "no room for IP waste" concern is noted — you must plan the subnet carefully (pre-allocate IPs for max pod count). |
| C — Calico | ❌ Wrong | Calico is a network policy plugin (controls pod-to-pod traffic rules). It doesn't determine whether pods get VNet IPs — that's Azure CNI or kubenet. Calico is often USED WITH Azure CNI for network policies. |
| D — NGINX Ingress | ❌ Wrong | NGINX Ingress Controller handles HTTP/HTTPS routing into the cluster — it's a Layer 7 load balancer, not a networking plugin that affects pod IP assignment. |

---

## Q63 Hub-Spoke Network Topology

**Scenario:** A company has:
- 10 application spoke VNets (one per team)
- Shared services (DNS, firewall, VPN Gateway to on-premises, Active Directory)
- Each spoke must be able to communicate with on-premises
- Spokes should NOT communicate directly with each other

**What network topology should you implement?**

A) Flat: All VNets peered to each other (full mesh)
B) Hub-Spoke: Hub VNet contains shared services, all spokes peer only to hub
C) Virtual WAN: All VNets connected via Azure Virtual WAN
D) Each spoke connects directly to on-premises via separate VPN Gateways

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  HUB-SPOKE TOPOLOGY                                                   │
  │                                                                       │
  │  On-Premises ────── VPN/ExpressRoute ──── HUB VNet                  │
  │                                          ├── Firewall               │
  │                                          ├── DNS                    │
  │                                          ├── Bastion                │
  │                                          ├── Shared Services        │
  │                                          │                          │
  │                          ┌──────── VNet Peering ────────┐            │
  │                          │                              │            │
  │                     Spoke VNet 1              Spoke VNet 2          │
  │                     (Team A app)              (Team B app)          │
  │                                                                       │
  │  ✅ Spokes access on-prem via Hub VPN Gateway                        │
  │  ✅ Spokes access shared services via Hub                            │
  │  ✅ Spokes do NOT peer with each other (traffic control via Firewall)│
  │  ✅ Single VPN Gateway in Hub (not one per spoke = cost saving)      │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Full mesh | ❌ Wrong | With 10 spokes, full mesh = 45 peering connections. Every spoke can reach every other spoke (violates "spokes should not communicate"). No centralized firewall or shared services management. |
| **B — Hub-Spoke** | ✅ Correct | Hub contains shared services (firewall, VPN Gateway, DNS). Spokes peer only with hub. Spoke-to-spoke traffic goes through hub firewall (which can block it). On-premises access via hub's VPN/ExpressRoute Gateway. One VPN gateway shared by all spokes. This is the Microsoft Cloud Adoption Framework recommended topology. |
| C — Virtual WAN | ❌ Wrong | Virtual WAN is also valid and could work, but it's more expensive and designed for large-scale or complex connectivity (SD-WAN, multiple regions). For standard enterprise hub-spoke, VNet peering hub-spoke is simpler and cheaper. |
| D — Per-spoke VPN | ❌ Wrong | Each spoke having its own VPN Gateway to on-premises = 10 VPN Gateways. Extremely expensive, complex, and doesn't provide centralized shared services. |

---

## Q64 ⭐ Hybrid Connectivity: ExpressRoute vs VPN Gateway

**Scenario:** A company needs to connect their on-premises datacenter to Azure. Requirements:
- Bandwidth: 2 Gbps sustained
- Latency: must be predictable and low (financial trading system)
- Uptime: 99.95% or better for the connectivity
- Data must NOT traverse the public internet

**Which connectivity option should you choose?**

A) Site-to-Site VPN Gateway (policy-based)
B) Site-to-Site VPN Gateway (route-based)
C) Azure ExpressRoute
D) Azure Virtual WAN with S2S VPN

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  VPN GATEWAY vs EXPRESSROUTE                                          │
  │                                                                       │
  │  VPN Gateway:                                                         │
  │  ├── Encrypted tunnel OVER the public internet                      │
  │  ├── Max bandwidth: up to 10 Gbps (VpnGw5AZ)                       │
  │  ├── Latency: variable (internet routing)                            │
  │  ├── Uptime: 99.9% SLA                                              │
  │  └── Best for: dev/test, remote offices, lower cost                 │
  │                                                                       │
  │  ExpressRoute:                                                        │
  │  ├── Private connection via connectivity provider (NOT internet)    │
  │  ├── Bandwidth: 50 Mbps to 100 Gbps                                │
  │  ├── Latency: consistent, low (private network, not internet)       │
  │  ├── Uptime: 99.95% SLA (higher with ExpressRoute Global Reach)    │
  │  └── Best for: production, financial systems, data-intensive        │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Policy-based VPN | ❌ Wrong | Policy-based VPN is a legacy type limited to 1 Gbps max and fewer features. Doesn't meet 2 Gbps. Also uses public internet — violates "not traverse internet." |
| B — Route-based VPN | ❌ Wrong | Route-based VPN supports up to 10 Gbps (highest SKU) and 99.9% SLA. BUT: traffic traverses the public internet — violates the data-must-not-traverse-internet requirement. Also, latency is unpredictable over internet. |
| **C — ExpressRoute** | ✅ Correct | ExpressRoute provides: private connection (not internet), 2 Gbps bandwidth (choose 2 Gbps circuit), predictable low latency (private MPLS network), 99.95% SLA (higher with redundant circuits). All requirements met. Financial trading systems consistently choose ExpressRoute. |
| D — Virtual WAN S2S VPN | ❌ Wrong | S2S VPN still traverses the internet regardless of Virtual WAN. Same limitation as option B. |

---

## Q65 Azure Firewall vs NSG vs NVA

**Scenario:** Determine the RIGHT security control for each requirement:

- **A:** Block all inbound internet traffic to a subnet EXCEPT port 443
- **B:** Filter outbound internet traffic from the entire hub VNet, with URL filtering and threat intelligence
- **C:** Deep packet inspection, next-gen IDS/IPS, custom routing for partner traffic

A) A=NSG, B=Azure Firewall, C=Azure Firewall Premium
B) A=Azure Firewall, B=NSG, C=NVA
C) A=NSG, B=NVA, C=Azure Firewall Premium
D) A=NSG, B=Azure Firewall Standard, C=Azure Firewall Premium or NVA

**✅ Answer: D**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  NETWORK SECURITY LAYERS                                              │
  │                                                                       │
  │  NSG (Network Security Group):                                        │
  │  ├── Layer 3/4 (IP/Port) filtering                                   │
  │  ├── Applied to subnet or NIC level                                  │
  │  ├── Allow/Deny rules based on IP, port, protocol                   │
  │  └── No URL filtering, no FQDN, no threat intelligence              │
  │                                                                       │
  │  Azure Firewall Standard:                                             │
  │  ├── Layer 3-7, fully stateful                                       │
  │  ├── FQDN filtering (allow *.microsoft.com)                         │
  │  ├── Threat intelligence (Microsoft TI feed)                        │
  │  ├── Network rules + Application rules                               │
  │  └── Managed service, no patching required                          │
  │                                                                       │
  │  Azure Firewall Premium:                                              │
  │  ├── All Standard features +                                         │
  │  ├── IDPS (Intrusion Detection & Prevention)                        │
  │  ├── TLS inspection (decrypt → inspect → re-encrypt)                │
  │  ├── URL filtering (full URL, not just domain)                      │
  │  └── Web categories                                                  │
  │                                                                       │
  │  NVA (Network Virtual Appliance):                                    │
  │  ├── Third-party firewall (Palo Alto, Fortinet, Checkpoint, etc.)  │
  │  ├── Full control — custom routing, advanced IPS/IDS               │
  │  ├── Requires VM management (patching, scaling, HA)                │
  │  └── Use when Azure Firewall lacks required specific features       │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — NSG for all 3 | ❌ Wrong | NSG can't do URL filtering or threat intelligence. Wrong tool for B and C. |
| **D — NSG + Firewall Standard + Firewall Premium or NVA** | ✅ Correct | **A=NSG:** Port 443 allow, block everything else — simple L3/4 rule, perfect for NSG. **B=Azure Firewall Standard:** Hub-level outbound with URL filtering (FQDN rules) and threat intel — Standard tier covers this. **C=NVA or Firewall Premium:** Deep packet inspection + IDS/IPS + custom routing for partner traffic requires either Firewall Premium (IDPS + TLS inspection) or a dedicated NVA. |
| B — Firewall for A | ❌ Wrong | Azure Firewall works but is overkill for a simple port-allow rule on a subnet. NSG is simpler and cheaper for L3/4 rules. |
| C — NVA for B | ❌ Partially | NVA would work for B, but Azure Firewall Standard is simpler (managed service, no VM patching). Use NVA only when needed. |

---

## Q66 Private Link vs Service Endpoint (Design Decision)

**Scenario:** A developer says: "Our app in VNet A needs to access Azure Key Vault. I configured a Service Endpoint — is this sufficient?"

The security team says: "Key Vault must be completely private — not accessible from ANY public IP or other VNets."

**Is a Service Endpoint sufficient? If not, what should be used?**

A) Yes, Service Endpoint makes Key Vault private
B) No — Service Endpoint still allows public access; use a Private Endpoint
C) No — use Azure Firewall to block public access to Key Vault
D) Service Endpoint + network rules are sufficient to block all public access

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Service Endpoint is sufficient | ❌ Wrong | Service Endpoint allows your VNet traffic to take an optimized route to Key Vault's public IP. The Key Vault STILL has a public endpoint. Other people on the internet could potentially reach it (though Key Vault's own firewall can restrict this). |
| **B — Private Endpoint** | ✅ Correct | Private Endpoint creates a private NIC in your VNet with a private IP mapped to Key Vault. You can then disable Key Vault's public endpoint entirely. DNS resolves `vault.azure.net` to the private IP within your VNet. No public access is possible — the public endpoint is disabled. This satisfies "completely private — not accessible from ANY public IP." |
| C — Azure Firewall | ❌ Wrong | Azure Firewall sits in front of your VNet traffic. It doesn't control access to Azure PaaS services (like Key Vault) from the internet — those are controlled by Key Vault's own network settings. |
| D — Service Endpoint + network rules | ❌ Wrong | Key Vault network rules with Service Endpoint restrict to specified VNets, but the public endpoint still exists. Someone with a matching VNet or if Microsoft's support bypasses could potentially access. Private Endpoint + disabled public endpoint = truly private. |

---

## Q67 ⭐ Azure Front Door vs Application Gateway vs Load Balancer

**Scenario:** Match the correct Azure load-balancing service:

- **A:** Global HTTP(S) routing + WAF + automatic failover across regions + edge caching
- **B:** Regional HTTP(S) routing + WAF + SSL termination + cookie-based session affinity
- **C:** Regional layer-4 (TCP/UDP) load balancing for non-HTTP internal traffic

A) A=Front Door, B=App Gateway, C=Azure Load Balancer
B) A=App Gateway, B=Front Door, C=Traffic Manager
C) A=Traffic Manager, B=App Gateway, C=Azure Load Balancer
D) A=Front Door, B=Traffic Manager, C=App Gateway

**✅ Answer: A**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  LOAD BALANCING SERVICE SELECTION                                     │
  │                                                                       │
  │                         Global?                                       │
  │                        /       \                                      │
  │                      Yes        No                                    │
  │                       │          │                                    │
  │                 HTTP/HTTPS?   HTTP/HTTPS?                             │
  │                 /       \    /          \                             │
  │               Yes        No            Yes    No                     │
  │                │          │             │      │                     │
  │          Front Door  Traffic      App Gateway  Load                  │
  │          (L7 global) Manager      (L7 regional) Balancer             │
  │                      (DNS-based)               (L4 regional)         │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Front Door, App Gateway, Load Balancer** | ✅ Correct | **Front Door:** Global HTTP(S) with WAF at edge, Anycast routing, origin health probes + automatic failover, edge caching. **Application Gateway:** Regional HTTP(S) with WAF, URL-based routing, SSL termination, session affinity (sticky sessions). **Azure Load Balancer:** Layer 4 (TCP/UDP) — backend pools, health probes, no HTTP understanding. |
| B — Swapped | ❌ Wrong | App Gateway is not global. Traffic Manager doesn't handle TCP/UDP traffic (it's DNS-only). |
| C — Traffic Manager first | ❌ Wrong | Traffic Manager is DNS-based, not HTTP-aware routing. Doesn't support WAF or edge caching. |
| D — Mixed up | ❌ Wrong | Traffic Manager is not a regional L7 load balancer. App Gateway is not for TCP/UDP non-HTTP. |

---

## Q68 Azure API Management (APIM) — Design Scenarios

**Scenario:** Multiple internal development teams expose REST APIs. The company needs:
- A single external endpoint for all APIs
- Rate limiting per API consumer
- Authentication via API key or OAuth
- API documentation portal for developers

**What should you deploy?**

A) Azure Application Gateway in front of all API servers
B) Azure API Management
C) Azure Front Door with custom routing rules
D) Azure Service Bus to mediate API calls

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Application Gateway | ❌ Wrong | App Gateway is a Layer 7 load balancer. It doesn't provide rate limiting, API key management, OAuth integration, or developer portals. It's traffic routing, not API management. |
| **B — Azure API Management** | ✅ Correct | APIM is purpose-built for all four requirements: **Single endpoint:** APIM acts as the API gateway — all APIs published through one external URL. **Rate limiting:** Built-in `rate-limit` and `quota` policies per consumer. **Authentication:** Built-in API key validation, OAuth 2.0, JWT validation policies. **Developer portal:** Auto-generated interactive documentation portal for API consumers. |
| C — Azure Front Door | ❌ Wrong | Front Door handles global routing and WAF, but has no API-specific features (rate limiting by API key, OAuth policies, developer portal). |
| D — Azure Service Bus | ❌ Wrong | Service Bus is a messaging queue/topic system — not an API gateway. It doesn't expose REST endpoints for external consumers or provide API management features. |

---

## Q69 Container Apps vs AKS

**Scenario:** A team wants to deploy 5 microservices as containers. They want:
- Auto-scale to zero when idle
- No Kubernetes cluster management overhead
- KEDA-based scaling (scale on queue depth, HTTP requests)
- Simple networking between services

**AKS or Azure Container Apps?**

A) AKS — more control is always better
B) Azure Container Apps — simplified container hosting with built-in KEDA scaling
C) ACI (Azure Container Instances) — simplest option
D) Azure App Service with Docker containers

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CONTAINER APPS vs AKS                                                │
  │                                                                       │
  │  Azure Container Apps:                                                │
  │  ├── Managed Kubernetes under the hood (no cluster to manage)       │
  │  ├── Built-in KEDA scaling (HTTP, queues, CPU, custom metrics)      │
  │  ├── Scale to zero (pay nothing when idle)                          │
  │  ├── Built-in service discovery and Dapr support                    │
  │  ├── Good for: microservices, event-driven, API workloads           │
  │  └── Limitation: less Kubernetes control (no raw kubectl access)    │
  │                                                                       │
  │  AKS:                                                                 │
  │  ├── Full Kubernetes — you manage node pools, upgrades, RBAC        │
  │  ├── Full control: any K8s operator, CRD, storage class            │
  │  ├── Higher operational overhead                                     │
  │  └── Good for: complex stateful workloads, full K8s ecosystem      │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — AKS | ❌ Wrong | "No Kubernetes management overhead" explicitly rules out AKS — you own the cluster, node upgrades, scaling configuration, networking, etc. |
| **B — Container Apps** | ✅ Correct | Container Apps is built on Kubernetes (AKS under the hood) but abstracts all management. KEDA is built-in. Scale-to-zero is native. Service-to-service communication via built-in service discovery. Exactly matches all stated requirements. |
| C — ACI | ❌ Wrong | ACI runs individual containers — not designed for multiple inter-connected microservices with KEDA scaling. No built-in service mesh or networking between services. |
| D — App Service | ❌ Wrong | App Service for containers works, but KEDA-based scaling (queue depth, HTTP, custom metrics) isn't natively available in App Service — it has its own autoscale rules. Also no "scale to zero" for App Service (unless Consumption plan, which is for Functions). |

---

## Q70 Landing Zone Architecture

**Scenario:** A large enterprise is adopting Azure for the first time. 20 teams will deploy workloads over the next 6 months. The CTO wants: governance from day one, centralized networking, subscription vending, and no tribal knowledge dependency.

**What is the recommended starting framework?**

A) Create one subscription and share it across all teams
B) Implement the Microsoft Cloud Adoption Framework (CAF) Landing Zone — Enterprise Scale
C) Use Azure Blueprints to deploy each team's environment manually
D) Let each team create their own subscriptions independently with no central governance

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — One shared subscription | ❌ Wrong | One subscription creates resource naming conflicts, no cost separation, no isolation of blast radius, no team-level RBAC. Unmanageable at scale. |
| **B — CAF Enterprise Scale Landing Zone** | ✅ Correct | The Microsoft CAF Landing Zone is an opinionated, reference architecture for enterprise Azure adoption: **Management Group hierarchy** (with policy inheritance), **Hub network** (VPN, firewall, ExpressRoute), **Identity subscription** (Active Directory, PIM), **Management subscription** (monitoring, security), **Subscription vending** process for new teams, **Policy-as-code** (Azure Policy for governance). Designed for exactly this scenario — large enterprise, multiple teams, governed from day one. |
| C — Manual Blueprints per team | ❌ Wrong | Manual per-team deployment doesn't scale to 20 teams. No repeatable subscription vending process. Governance is applied inconsistently. |
| D — No central governance | ❌ Wrong | Shadow IT, inconsistent naming, security gaps, no cost visibility, no network control. This is the problem CAF is designed to prevent. |

---

## Q71 Migration Strategy: 6Rs

**Scenario:** Match each application to its migration strategy:

- **A:** A 10-year-old tightly-coupled monolith on Windows Server 2003 — moving to Azure quickly with minimal changes
- **B:** An on-premises Oracle database being replaced by Cosmos DB with a complete data model redesign
- **C:** A custom COTS application where the vendor provides a SaaS version

A) A=Rehost, B=Rearchitect, C=Replace
B) A=Refactor, B=Rebuild, C=Replatform
C) A=Rehost, B=Rebuild, C=Replace
D) A=Retire, B=Rearchitect, C=Retain

**✅ Answer: A**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  THE 6 Rs OF MIGRATION                                                │
  │                                                                       │
  │  Rehost (Lift & Shift):  Move as-is to IaaS. Zero code change.     │
  │  Replatform (Lift-Tinker-Shift): Minor changes to use PaaS.        │
  │  Refactor: Significantly change architecture to use cloud features. │
  │  Rearchitect: Major redesign of the application/data model.        │
  │  Rebuild: Rewrite from scratch using cloud-native services.        │
  │  Replace: Replace with SaaS (drop the custom app entirely).        │
  │  Retain: Keep on-premises (not ready or too risky to migrate).     │
  │  Retire: Decommission (app no longer needed).                      │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Rehost, Rearchitect, Replace** | ✅ Correct | **Rehost (lift and shift):** Old monolith → Azure VM with minimal changes. "Quickly with minimal changes" = Rehost. **Rearchitect:** Oracle → Cosmos DB with complete data model redesign = fundamental architectural change to the storage layer. **Replace:** Vendor provides SaaS version → stop running your own and switch to their SaaS. |
| B — Wrong labels | ❌ Wrong | Refactor implies code changes. Rebuild implies rewriting from scratch. Replace is correct for C but the others don't match. |
| C — A=Rehost is right, B=Rebuild wrong | ❌ Wrong | Oracle → Cosmos DB with data model redesign is Rearchitect, not Rebuild (which would mean starting the application code from scratch). |
| D — A=Retire | ❌ Wrong | Retire means decommission, not move quickly. The scenario says they ARE moving it. |

---

## Q72 Cost Optimization: Reserved Instances vs Spot vs Pay-as-you-go

**Scenario:** Match each workload to the cost-optimal pricing model:

- **A:** Database VM running 24/7 for the next 3 years
- **B:** Video rendering job — runs for 2 hours, can restart from checkpoint if interrupted
- **C:** Dev/test environment, used only 8 hours a day on weekdays

A) A=Reserved (3yr), B=Spot, C=Pay-as-you-go with auto-shutdown
B) A=Pay-as-you-go, B=Reserved, C=Spot
C) A=Reserved, B=Pay-as-you-go, C=Spot
D) A=Spot, B=Reserved, C=Pay-as-you-go

**✅ Answer: A**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  PRICING MODEL COMPARISON                                             │
  │                                                                       │
  │  Pay-as-you-go (PAYG):                                               │
  │  ├── No commitment, full price                                       │
  │  ├── Good for: unpredictable, short-term, variable workloads        │
  │                                                                       │
  │  Reserved Instances (1 or 3 year):                                   │
  │  ├── Up to 72% savings vs PAYG                                       │
  │  ├── Commitment: you pay whether you use it or not                  │
  │  ├── Good for: steady-state, 24/7, predictable workloads           │
  │                                                                       │
  │  Spot VMs:                                                            │
  │  ├── Up to 90% savings — use Azure's spare capacity                 │
  │  ├── Can be evicted with 30-second notice when capacity needed      │
  │  ├── Good for: fault-tolerant, interruptible, batch workloads      │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Reserved/Spot/PAYG+shutdown** | ✅ Correct | **Reserved (3yr):** Database is 24/7, predictable, long-term. 3-year Reserved saves ~72% vs PAYG — maximum savings. **Spot:** Video rendering can restart from checkpoint if evicted — fault-tolerant batch = perfect Spot use case. Up to 90% savings. **PAYG + auto-shutdown:** Dev environment not needed evenings/weekends. PAYG with auto-shutdown at 17:00 + start at 09:00 = pay only for ~40 hours/week instead of 168. Or Dev/Test pricing if available. |
| B — PAYG for database | ❌ Wrong | PAYG for a 3-year database workload wastes huge savings from Reserved pricing. |
| C — PAYG for video rendering | ❌ Wrong | Pay-as-you-go for interruptible batch work wastes money. Spot is 90% cheaper and the job can restart. |
| D — Spot for database | ❌ Wrong | Spot VMs can be evicted with 30-second notice — a database cannot tolerate that. |

---

## Q73 Azure Virtual WAN

**Scenario:** A company has 50 branch offices globally, each with a local internet connection and SD-WAN device. They also have 10 Azure regions with VNets. All branches must connect to all Azure regions, and branch-to-branch communication must be possible.

**What is the recommended Azure networking solution?**

A) 50 Site-to-Site VPN Gateways in a hub VNet, manually peer to 10 regions
B) Azure Virtual WAN with hub-and-spoke connections
C) Azure ExpressRoute for all 50 branches
D) Full mesh VNet peering across all 10 regions with individual VPN connections per branch

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — 50 VPN Gateways | ❌ Wrong | 50 VPN Gateway deployments to manage + manual peering to 10 regions + no native branch-to-branch routing. Operationally impossible to manage. |
| **B — Azure Virtual WAN** | ✅ Correct | Virtual WAN is specifically designed for this: **Automated hub creation** in each Azure region, **BGP-based branch connectivity** (any SD-WAN-compatible device connects via S2S VPN or ExpressRoute), **Any-to-any routing**: branches ↔ Azure, branches ↔ branches (via Virtual WAN hub routing), **10 regional hubs** managed centrally. The exact use case Virtual WAN was built for. |
| C — ExpressRoute for 50 branches | ❌ Wrong | ExpressRoute requires dedicated circuits from connectivity providers — expensive, slow to provision, and overkill for small branch offices with internet connections. |
| D — Full mesh | ❌ Wrong | With 10 regions: full mesh = 45 VNet peerings. Plus 50 branches × 10 regions = 500 VPN connections. Unmanageable. No native branch-to-branch routing. |

---

## Q74 Azure CDN vs Front Door for Content Delivery

**Scenario:** A company serves static files (images, CSS, JS) globally. They need content cached at edge locations worldwide for the lowest possible latency. The application backend is in West US.

**What should they use for STATIC CONTENT delivery?**

A) Azure Front Door (Standard/Premium)
B) Azure CDN from Microsoft (Classic) or Azure CDN from Akamai/Verizon
C) Azure Application Gateway
D) Azure Traffic Manager

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Azure Front Door** | ✅ Correct | In 2023, Microsoft integrated Azure CDN capabilities into Azure Front Door. Front Door Standard/Premium includes CDN caching at edge PoPs globally, plus the added benefits of: dynamic site acceleration, WAF, global load balancing, and health-probe-based failover. For new deployments, Front Door Standard/Premium is the recommended approach for both static CDN and dynamic app delivery. |
| B — Azure CDN Classic | ❌ Partially | Azure CDN (Classic) is still available and works for pure static content delivery. However, Microsoft is converging CDN into Front Door. Front Door is the current recommended solution and includes all CDN capabilities plus more. For the exam, both may be valid but Front Door is the recommended modern answer. |
| C — Application Gateway | ❌ Wrong | App Gateway is a regional Layer 7 load balancer. It doesn't cache content globally at edge PoPs. |
| D — Traffic Manager | ❌ Wrong | Traffic Manager does DNS-based routing but has zero caching or edge delivery capabilities. |

---

## Q75 Azure Functions: Hosting Plan Selection

**Scenario:** An Azure Function processes webhook events from GitHub. It runs infrequently — maybe 50 times per day. Each execution takes 30 seconds. Cost must be minimized.

**Which hosting plan should you choose?**

A) Premium Plan
B) Dedicated (App Service) Plan
C) Consumption Plan
D) Kubernetes-based hosting

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  AZURE FUNCTIONS HOSTING PLANS                                        │
  │                                                                       │
  │  Consumption Plan:                                                    │
  │  ├── Pay per execution + per GB-second                               │
  │  ├── Scale to zero (no charge when idle)                            │
  │  ├── Cold starts (first execution after idle period takes longer)   │
  │  ├── Max timeout: 10 minutes                                         │
  │  └── Best for: infrequent, unpredictable, budget-sensitive          │
  │                                                                       │
  │  Premium Plan:                                                        │
  │  ├── Always-warm instances (no cold starts)                         │
  │  ├── VNet integration                                                │
  │  ├── Unlimited execution duration                                    │
  │  └── Best for: always-on, VNet needed, cold start intolerance      │
  │                                                                       │
  │  Dedicated (App Service) Plan:                                        │
  │  ├── Functions run on dedicated VMs (same as web apps)             │
  │  ├── Pay always (no scale-to-zero)                                  │
  │  └── Best for: predictable, steady traffic, using existing ASP     │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Premium | ❌ Wrong | Premium has always-on instances — you pay even when no webhooks are received. For 50 executions per day, you're paying for idle capacity. |
| B — Dedicated | ❌ Wrong | Even worse — always-on dedicated VMs for 50 executions/day. |
| **C — Consumption** | ✅ Correct | 50 executions/day × 30 seconds each = 25 minutes of execution time per day. Consumption plan charges only for actual execution time + memory. Scale-to-zero means zero cost during the other 23+ hours. Cold starts (if any) are acceptable since webhooks are asynchronous. |
| D — Kubernetes | ❌ Wrong | K8s hosting (KEDA-based) makes sense for custom scaling requirements or enterprise K8s integration — massive overkill for 50 simple webhook functions. |

---

## Q76 Network Security Design: DMZ Architecture

**Scenario:** A web application must be accessible from the internet. The backend database must NEVER be directly accessible from the internet. The application tier communicates with the database tier.

**Which network design is CORRECT?**

A) All resources in one subnet with NSG allowing internet on port 80/443
B) Web tier in public subnet with public IP, DB in private subnet with no public IP, NSG allows web→DB on DB port only
C) Web tier behind Application Gateway in a dedicated subnet, app servers in private subnet, DB in private subnet with Private Endpoint
D) Everything in private subnets, use Azure Bastion for external access

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  CORRECT DMZ ARCHITECTURE                                             │
  │                                                                       │
  │  Internet                                                             │
  │     │                                                                 │
  │     ▼                                                                 │
  │  [Application Gateway Subnet] — WAF, SSL termination                 │
  │     │ (private traffic only)                                          │
  │     ▼                                                                 │
  │  [App Tier Subnet] — No public IP, NSG blocks internet              │
  │     │ (app port only, e.g. 5432 for PostgreSQL)                      │
  │     ▼                                                                 │
  │  [DB Subnet] — Private Endpoint, no public IP                        │
  │  Azure SQL / PostgreSQL — public endpoint DISABLED                   │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — All in one subnet | ❌ Wrong | No isolation. NSG alone doesn't provide real separation. DB is reachable from the internet if web tier is compromised (lateral movement). |
| B — Web in public subnet | ❌ Wrong | App servers having public IPs is a security risk — an attacker who compromises an app server can then try to reach the DB. Also, NSG alone for web→DB without WAF misses application-layer attacks. |
| **C — App Gateway + private subnets + Private Endpoint** | ✅ Correct | **App Gateway** with WAF terminates internet traffic, inspects Layer 7. **App servers** in private subnet — no public IPs, NSG restricts traffic. **DB** with Private Endpoint — completely private, public endpoint disabled, only accessible via private IP from app tier subnet. Defence in depth: WAF → App layer → DB private. |
| D — Everything private, Bastion for external | ❌ Wrong | Bastion is for admin SSH/RDP access — it's not for serving the web application to external users. The app still needs to be externally accessible on port 443. |

---

## Q77 AKS: Ingress Controller Design

**Scenario:** Your AKS cluster hosts 20 microservices. External clients access different services via paths: `/api/users` → user service, `/api/orders` → orders service, `/api/payments` → payments service. You also need TLS termination at the cluster edge.

**What should you deploy?**

A) One Azure Load Balancer per service
B) An Ingress Controller (NGINX or Application Gateway Ingress Controller) with Ingress rules
C) External DNS records pointing directly to each service's ClusterIP
D) Azure Traffic Manager with 20 endpoints

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Load Balancer per service | ❌ Wrong | 20 services = 20 public IPs = expensive and unmanageable. Each LoadBalancer service has its own IP — clients can't use path-based routing. |
| **B — Ingress Controller** | ✅ Correct | Ingress Controller is the Kubernetes-native solution: **One public IP** (load balancer service for the ingress controller). **Path-based routing** configured via Kubernetes Ingress resources (`/api/users` → user service, etc.). **TLS termination** at the ingress controller using Kubernetes Secrets (cert-manager can auto-provision Let's Encrypt certs). NGINX Ingress or AGIC (Application Gateway Ingress Controller) are common choices. |
| C — ClusterIP external DNS | ❌ Wrong | ClusterIPs are internal-only — they're not externally accessible. DNS records can't point to ClusterIPs from outside the cluster. |
| D — Traffic Manager | ❌ Wrong | Traffic Manager does DNS-based global routing — not path-based routing within a cluster. 20 endpoints is not how Traffic Manager is used for microservices. |

---

## Q78 Azure AD App Registration: Authorization Design

**Scenario:** An API needs to:
- Allow Microsoft 365 users to sign in and access their own data
- Allow a backend service to call the API without a user present (daemon/service-to-service)

**Which OAuth 2.0 flows should be used for each scenario?**

A) Both use Authorization Code flow
B) User sign-in = Authorization Code flow with PKCE; Service = Client Credentials flow
C) User sign-in = Implicit flow; Service = Device Code flow
D) Both use Client Credentials flow

**✅ Answer: B**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  OAUTH 2.0 FLOWS                                                      │
  │                                                                       │
  │  Authorization Code + PKCE:                                           │
  │  ├── For interactive user sign-in (web apps, SPAs, mobile)          │
  │  ├── User signs in → consent → auth code → access token            │
  │  └── PKCE (Proof Key for Code Exchange) protects public clients    │
  │                                                                       │
  │  Client Credentials:                                                  │
  │  ├── No user involved — service-to-service                          │
  │  ├── App authenticates with client_id + client_secret (or cert)    │
  │  └── Used for daemons, background services, automation             │
  │                                                                       │
  │  Implicit flow: DEPRECATED — use Auth Code + PKCE for SPAs        │
  │  Device Code: For devices with no browser (IoT, CLI tools)         │
  │  On-behalf-of: API calling another API on behalf of a signed-in user│
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Both Auth Code | ❌ Wrong | Client Credentials (no user present) cannot use Auth Code flow — there's no user to sign in and provide consent. |
| **B — Auth Code + PKCE for user, Client Credentials for service** | ✅ Correct | **Auth Code + PKCE:** User signs in to M365, redirected to sign-in, authenticates, consents, gets token. PKCE is required for SPAs and recommended for all clients now. **Client Credentials:** Background service has its own app registration with a secret or certificate. Gets a token without any user interaction. |
| C — Implicit flow | ❌ Wrong | Implicit flow is deprecated (tokens exposed in URL). Use Auth Code + PKCE instead. Device Code is for no-browser devices (not applicable here). |
| D — Both Client Credentials | ❌ Wrong | User sign-in requires a user to interact — Client Credentials bypasses user interaction entirely. A user's data wouldn't be properly scoped to that user without user authentication. |

---

## Q79 Azure Dedicated Hosts vs Isolated VMs

**Scenario:** A financial company has compliance requirements that state: "Virtual machines must run on hardware not shared with any other organization." Normal Azure multi-tenant VMs are not compliant.

**Which option satisfies this requirement?**

A) Azure Spot VMs
B) Azure Reserved Instances
C) Azure Dedicated Hosts
D) Isolated VM sizes (e.g., Standard_E80ids_v4)

**✅ Answer: D (or C — both are valid, but context matters)**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Spot VMs | ❌ Wrong | Spot VMs use spare multi-tenant capacity — absolutely not isolated. They run on whatever hardware Azure has available. |
| B — Reserved Instances | ❌ Wrong | Reserved Instances are a billing commitment — they don't change the physical isolation of the VM. Still runs on shared multi-tenant hardware. |
| **C — Dedicated Hosts** | ✅ Correct | Azure Dedicated Host provides a dedicated physical server for your Azure VMs. Only your organization's VMs run on this server. Full control over VM placement, hardware isolation, compliance. Can host multiple VM families on one dedicated server. |
| **D — Isolated VM sizes** | ✅ Also Correct | Certain VM sizes (like Standard_E80ids_v4, Standard_M128s) guarantee that the VMs are the ONLY customer workload running on that physical server due to their size. No other customers share the host. Less expensive than Dedicated Hosts for specific workloads. |

> For the exam, if both C and D appear together, the question will give more context. **Dedicated Hosts** give MORE control (maintenance window control, VM placement across sockets). **Isolated VMs** are simpler — just pick a specific VM size that guarantees isolation.

---

## Q80 ⭐ Azure Monitor: Application Insights Sampling

**Scenario:** An Application Insights instance is ingesting 100 GB of telemetry per day — costs are very high. The development team needs to reduce costs but still catch all exceptions and slow requests.

**What should you configure?**

A) Disable Application Insights in production
B) Configure adaptive sampling to reduce telemetry volume while retaining all exception and failed request data
C) Set a fixed sampling rate of 1% for all telemetry
D) Move to a separate Log Analytics workspace with cheaper pricing tier

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Disable | ❌ Wrong | Disabling removes all observability from production — not acceptable. |
| **B — Adaptive sampling** | ✅ Correct | Adaptive sampling automatically adjusts the sampling rate based on traffic volume to stay within a target telemetry volume. Critically, it has built-in **exception and failure preservation** — all exceptions, failed requests, and dependency failures are NEVER sampled out (they're always captured). High-volume normal traffic is sampled, but critical errors are always captured. Perfect for cost control without sacrificing error detection. |
| C — Fixed 1% sampling | ❌ Wrong | A fixed 1% rate means 99% of all data (including exceptions) is discarded. You'd miss the vast majority of errors. This could lead to blind spots in production issues. |
| D — Different workspace | ❌ Wrong | Moving to another workspace doesn't reduce the telemetry VOLUME — you're still ingesting 100 GB, just somewhere else. The cost is driven by data ingestion volume, not the workspace. |

---

## Q81 AKS Node Pool Design

**Scenario:** An AKS cluster runs:
- **System workloads:** Kubernetes system pods (CoreDNS, metrics-server) — must always be available
- **CPU-intensive ML inference:** requires GPU VMs (NC-series)
- **General microservices:** Standard compute, auto-scale 2–50 nodes

**How should the node pools be structured?**

A) One node pool with mixed VM sizes
B) Three separate node pools: System pool (standard VMs), GPU pool (NC-series), User pool (standard VMs with autoscale)
C) One system pool + one large user pool
D) Separate clusters for each workload type

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Mixed pool | ❌ Wrong | AKS node pools are homogeneous — all nodes must be the same VM size. Can't mix standard and GPU VMs in one pool. |
| **B — Three pools** | ✅ Correct | **System pool (required):** Dedicated to Kubernetes system pods — standard VMs, taints prevent user workloads from running here (stability for system components). **GPU pool:** NC-series VMs for ML inference — node selector/taints route GPU workloads here. Scale to zero when no ML jobs running. **User pool:** Standard VMs with autoscale (2–50) for general microservices. Each pool has independent VM size, scale settings, and availability zone configuration. |
| C — Two pools | ❌ Wrong | Combining GPU and general workloads in one pool wastes expensive GPU VMs for non-GPU workloads. |
| D — Separate clusters | ❌ Wrong | Separate clusters for each workload type is expensive (multiple control planes, multiple ingress controllers, complex service-to-service networking). Multiple node pools within one cluster is the right approach. |

---

## Q82 Azure Migrate: Assessment and Migration

**Scenario:** A company wants to migrate 200 VMs from VMware on-premises to Azure. Before migrating, they need to: discover all VMs, assess their Azure readiness, estimate monthly costs in Azure, and then replicate VMs.

**Which Azure Migrate tools cover the complete workflow?**

A) Azure Migrate: Server Assessment + Azure Migrate: Server Migration
B) Azure Site Recovery only
C) Azure Database Migration Service + Azure Migrate
D) Azure Backup + Azure Migrate

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Server Assessment + Server Migration** | ✅ Correct | **Azure Migrate: Discovery and Assessment** (formerly "Server Assessment"): Deploy an appliance on-premises → discovers VMs → assesses Azure readiness → recommends right-sized Azure VMs → estimates monthly Azure cost. **Azure Migrate: Server Migration**: Replicates VMware VMs to Azure (agentless or agent-based), with test migration capability, then cutover. Complete end-to-end workflow for VM migration. |
| B — ASR only | ❌ Wrong | ASR is designed for disaster recovery — it can migrate VMs, but it lacks the discovery, assessment, and right-sizing features. Also ASR has ongoing replication costs vs Azure Migrate's migration-focused pricing. |
| C — DMS + Migrate | ❌ Wrong | DMS is for database migration (SQL Server, MySQL, PostgreSQL) — not VM migration. You'd use DMS for the database layer of the migration, but it doesn't handle VM migration. |
| D — Backup + Migrate | ❌ Wrong | Azure Backup isn't a migration tool. It can be used to "backup and restore in Azure" as a crude migration but lacks the assessment, right-sizing, test migration, and orchestration features of Azure Migrate. |

---

## Q83 Azure Policy: Built-in vs Custom Policies

**Scenario:** You need to enforce that all VMs in production must use managed disks (no unmanaged disks). Is this covered by a built-in policy?

**What is the recommended approach?**

A) Write a custom policy with Deny effect
B) Use the built-in policy "Audit VMs that do not use managed disks" with Deny effect
C) Use Azure Advisor recommendations
D) Configure it via ARM template restrictions

**✅ Answer: B**

| Option | Verdict | Reason |
|--------|---------|--------|
| A — Custom policy | ❌ Wrong | Writing custom policies adds maintenance overhead. Always check built-in policies first — Azure has hundreds covering common scenarios. |
| **B — Built-in policy with Deny** | ✅ Correct | Azure has a built-in policy: "Audit VMs that do not use managed disks." The built-in policy's effect can be changed to `Deny` when assigning it, which blocks creation of VMs with unmanaged disks. No custom policy needed. **Always check built-in policies before writing custom ones.** |
| C — Azure Advisor | ❌ Wrong | Advisor makes recommendations but doesn't enforce or block. Teams can ignore Advisor recommendations. |
| D — ARM template restrictions | ❌ Wrong | ARM templates don't have a "restriction" mechanism. You'd need to control what templates teams can deploy — that's governance, not a template feature. |

---

## Q84 Azure Automation vs Logic Apps vs Azure Functions

**Scenario:** Match each automation requirement to the best tool:

- **A:** Run a PowerShell script to resize VMs every Sunday at midnight — no coding expertise available
- **B:** Process webhook from GitHub, transform the payload, and write to an Azure SQL table — event-driven, low code
- **C:** Real-time data transformation pipeline processing 10,000 events/second

A) A=Azure Automation, B=Logic Apps, C=Azure Functions
B) A=Logic Apps, B=Azure Functions, C=Azure Automation
C) A=Azure Automation, B=Azure Functions, C=Logic Apps
D) A=Azure Functions, B=Logic Apps, C=Azure Functions

**✅ Answer: A**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A — Automation, Logic Apps, Functions** | ✅ Correct | **Azure Automation:** Runbook (PowerShell/Python), scheduled execution, no coding expertise needed for Ops teams. Perfect for VM management scripts on a schedule. **Logic Apps:** Low-code/no-code visual workflow designer. GitHub webhook connector + SQL connector available off the shelf — event-driven transformation with no custom code. **Azure Functions:** High-performance code execution for 10,000 events/second — Functions can handle millions of executions with sub-second latency. Logic Apps is too slow and expensive for this throughput. |
| B — Logic Apps for C | ❌ Wrong | Logic Apps is not designed for high-throughput event processing at 10K/sec. Each Logic App run has overhead for workflow orchestration. Functions is far more efficient at this scale. |
| C — Functions for B | ❌ Wrong | Functions would work but requires coding. Logic Apps provides GitHub and SQL connectors natively — no code needed for the described scenario. |
| D — Functions for scheduling | ❌ Wrong | Functions can run on a schedule (Timer trigger), but if "no coding expertise" is a constraint, Azure Automation with UI-based runbook authoring is more appropriate. |

---

## Q85 ⭐ Architecture: Choosing Between Microservices and Monolith

**Scenario:** A startup is building a new application from scratch. The team has 5 developers, limited DevOps expertise, and must ship MVP in 3 months. Which architecture approach is recommended?

A) Microservices with AKS from day one
B) Serverless microservices with 15 Azure Functions
C) Monolith on Azure App Service with a plan to refactor later
D) Event-driven architecture with Event Hub + Azure Stream Analytics

**✅ Answer: C**

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  ARCHITECTURE MATURITY PRINCIPLE                                      │
  │                                                                       │
  │  Microservices solve SCALE problems.                                  │
  │  They introduce OPERATIONAL complexity.                               │
  │                                                                       │
  │  A 5-person team with 3-month deadline should NOT start with:       │
  │  - Service mesh, distributed tracing, K8s, multiple CI/CD pipelines │
  │  - 15 separate deployable units                                      │
  │  - Distributed transactions across services                          │
  │                                                                       │
  │  Start simple. Refactor when you have:                               │
  │  - Proven product-market fit                                         │
  │  - Specific scaling bottlenecks in the monolith                      │
  │  - A larger team to manage the complexity                            │
  │                                                                       │
  │  "Monolith first" — Martin Fowler's recommendation                   │
  └──────────────────────────────────────────────────────────────────────┘
```

| Option | Verdict | Reason |
|--------|---------|--------|
| A — AKS microservices | ❌ Wrong | AKS requires Kubernetes expertise, cluster management, separate CI/CD per service, distributed tracing, service mesh. A 5-person team would spend 60% of their time on infrastructure, not product. |
| B — 15 Azure Functions | ❌ Wrong | 15 separate Functions = 15 deployment units, 15 sets of connection strings, complex distributed tracing, cold starts, distributed transaction challenges. Operational overhead far exceeds the benefit at this stage. |
| **C — Monolith on App Service** | ✅ Correct | App Service is managed PaaS — no infrastructure management. Single codebase = simpler development, testing, debugging. Deploy from Git in minutes. When specific services need to scale independently or team grows, extract them to microservices strategically. Ship MVP in 3 months is achievable. This is the exam's expected answer when the scenario specifies small team + time constraint + limited DevOps expertise. |
| D — Event-driven with Stream Analytics | ❌ Wrong | Event-driven architecture adds async complexity, eventual consistency challenges, and requires expertise in Event Hub and stream processing. Significantly increases complexity for a startup MVP. |

---

## Quick Reference Cheatsheet

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  AZ-305 KEY DESIGN PRINCIPLES                                         │
  │                                                                       │
  │  1. MEET ALL REQUIREMENTS — Identify every constraint in the        │
  │     scenario: cost, RTO, RPO, compliance, latency, scale, ops.     │
  │     The correct answer satisfies ALL constraints, not just some.    │
  │                                                                       │
  │  2. SIMPLEST SOLUTION WINS — If two options meet requirements,      │
  │     the one with less complexity is usually correct.                 │
  │                                                                       │
  │  3. CONTROL PLANE ≠ DATA PLANE — Key Vault Contributor can't       │
  │     read secrets. Contributor can't assign roles.                   │
  │                                                                       │
  │  4. PRIVATE ENDPOINT > SERVICE ENDPOINT — When "not accessible     │
  │     from internet" is required.                                      │
  │                                                                       │
  │  5. MANAGED IDENTITY > SERVICE PRINCIPAL — When "minimize          │
  │     credential management" is a requirement.                         │
  │                                                                       │
  │  6. BUILT-IN POLICY FIRST — Always check built-in policies         │
  │     before writing custom ones.                                      │
  │                                                                       │
  │  7. FRONT DOOR vs APP GATEWAY — Global=Front Door, Regional=AppGW   │
  │                                                                       │
  │  8. COSMOS DB STRONG ≠ MULTI-REGION WRITE — Strong consistency     │
  │     with multi-region write defeats the purpose.                    │
  │                                                                       │
  │  9. DATA BOX THRESHOLD: >40TB to migrate in <2 weeks → Data Box    │
  │                                                                       │
  │  10. SQL MI for LIFT-AND-SHIFT — If the app uses Linked Servers,  │
  │      SQL Agent, CLR, cross-DB queries → SQL MI, not SQL Database.  │
  └──────────────────────────────────────────────────────────────────────┘
```

---

*Source: [AZ-104 Exam Handbook](az104_exam_handbook.md) · [Azure Handbook](azure_handbook.md) · [Azure Services Handbook](../azure-services/azure_services_handbook.md)*
