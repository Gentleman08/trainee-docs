[🏠 Home](../README.md) · [Azure](README.md)

# 📝 AZ-104 Exam — Question & Answer Handbook

> **Audience:** Candidates preparing for the Microsoft Azure Administrator (AZ-104) exam
> **Format:** Scenario-based questions → correct answer(s) → full explanation of why each option is right or wrong
> **Coverage:** All 5 exam domains with weighted focus matching actual exam distribution

---

## Exam Domain Weights

| Domain | Weight | Sections |
|--------|--------|----------|
| **1. Manage Azure Identities & Governance** | 15–20% | Q1–Q20 |
| **2. Implement and Manage Storage** | 15–20% | Q21–Q38 |
| **3. Deploy and Manage Azure Compute Resources** | 20–25% | Q39–Q60 |
| **4. Implement and Manage Virtual Networking** | 20–25% | Q61–Q82 |
| **5. Monitor and Maintain Azure Resources** | 10–15% | Q83–Q100 |

---

## How to Use This Handbook

1. Cover the answer section and attempt the question yourself
2. Read the correct answer(s)
3. Read the full explanation — especially why wrong options are wrong
4. Starred questions ⭐ are high-frequency exam topics

---

# Domain 1 — Manage Azure Identities & Governance

---

## Q1 ⭐ — RBAC Scope Inheritance

**You assign the `Contributor` role to a user at the Subscription level. The subscription contains two resource groups: `rg-prod` and `rg-dev`. What is the effect?**

A. The user gets Contributor access only on `rg-prod` by default  
B. The user gets Contributor access on both `rg-prod` and `rg-dev`, and on all resources within them  
C. The user gets Contributor access only at the subscription level and must be reassigned per resource group  
D. The user gets Owner access because subscription-level assignments grant full control  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure RBAC uses a scope hierarchy: Management Group → Subscription → Resource Group → Resource. When you assign a role at a higher scope, the permissions **inherit downward** to all child scopes automatically. Contributor at subscription level means Contributor on every RG and every resource in that subscription.
- **A is wrong** — There is no default targeting of specific RGs. All child scopes inherit the assignment.
- **C is wrong** — There is no requirement to reassign per resource group if the assignment is at subscription level. Inheritance handles it.
- **D is wrong** — Contributor and Owner are different roles. Contributor cannot assign roles to others; Owner can. Scope level does not promote a role to a higher privilege role.

---

## Q2 ⭐ — Role Difference: Owner vs Contributor

**A DevOps engineer needs to deploy and manage all Azure resources in a resource group but must NOT be able to grant other users access to those resources. Which role should you assign?**

A. Owner at the resource group scope  
B. Contributor at the resource group scope  
C. User Access Administrator at the resource group scope  
D. Contributor at the subscription scope  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — `Contributor` allows creating, modifying, and deleting all resource types in Azure, but explicitly **cannot manage role assignments**. This exactly matches the requirement.
- **A is wrong** — `Owner` includes everything Contributor can do PLUS the ability to assign roles to others. This violates the requirement of not being able to grant access.
- **C is wrong** — `User Access Administrator` is specifically for managing role assignments only — it doesn't grant resource creation rights.
- **D is wrong** — While Contributor scope can be widened to subscription level, the requirement calls for resource group scope to follow least privilege. Subscription scope gives unnecessary access to other resource groups.

---

## Q3 — Custom Roles

**You need to create a custom RBAC role that allows users to restart virtual machines but prevents them from creating or deleting VMs. Which actions should you include in the role definition?**

A. `Microsoft.Compute/virtualMachines/*` (all actions)  
B. `Microsoft.Compute/virtualMachines/restart/action` only  
C. `Microsoft.Compute/virtualMachines/read` and `Microsoft.Compute/virtualMachines/restart/action`  
D. `Microsoft.Compute/virtualMachines/write` and `Microsoft.Compute/virtualMachines/restart/action`  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — To restart a VM you need to be able to READ the VM (to see it) and perform the restart action. The `read` action covers listing and getting VM details. The `restart/action` covers the restart operation specifically. This provides only the minimum required permissions.
- **A is wrong** — `*` wildcard includes create, update, delete, and all other actions on VMs — far more than needed and violates least privilege.
- **B is wrong** — Without the `read` action, the user cannot see the VMs in the portal or CLI, making the restart permission essentially unusable. Also needed for the restart to resolve the VM object.
- **D is wrong** — `write` permission allows creating and updating VMs, which is explicitly not desired. Never include write permissions when only restart is needed.

> **Note:** Custom roles are defined in JSON format and can be created with: `az role definition create --role-definition role.json`

---

## Q4 ⭐ — Management Groups

**Your company has 5 Azure subscriptions across 3 departments. You want to apply a cost management policy to all subscriptions at once without assigning it individually to each subscription. What should you use?**

A. Azure Resource Groups  
B. Azure Management Groups  
C. Azure Policy at each subscription  
D. Azure Blueprints on each subscription  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Management Groups are containers for organizing multiple subscriptions into a hierarchy. Policies, RBAC, and blueprints assigned to a Management Group automatically apply to ALL subscriptions within it. This is exactly the scenario described.
- **A is wrong** — Resource Groups exist WITHIN a subscription — they cannot span subscriptions or group subscriptions together.
- **C is wrong** — Assigning policy at each subscription individually defeats the purpose of centralised management and doesn't scale as subscriptions are added.
- **D is wrong** — While Blueprints can bundle policies and role assignments, they still need to be assigned per subscription individually. Management Groups are the right hierarchy solution.

```
  Management Group: "Company Root"
      │
      ├── Management Group: "Dept A"
      │   ├── Subscription 1
      │   └── Subscription 2
      │
      └── Management Group: "Dept B"
          ├── Subscription 3
          └── Subscription 4

  Assign policy at "Company Root" → applies to ALL 4 subscriptions
```

---

## Q5 — Service Principals vs Managed Identities

**An application running on an Azure Virtual Machine needs to access Azure Key Vault secrets. What is the MOST secure approach?**

A. Create a Service Principal, store the client secret in the VM's environment variables  
B. Create a Service Principal, store the client secret in Azure Key Vault and retrieve it at startup  
C. Enable a system-assigned Managed Identity on the VM and grant it Key Vault access  
D. Use the Azure subscription root credentials in the application configuration  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — A system-assigned Managed Identity is an identity managed entirely by Azure. The VM gets an identity automatically; credentials are never exposed to you and rotate automatically. There is no secret to store, manage, or rotate. This is the Microsoft-recommended approach for Azure resources accessing other Azure services.
- **A is wrong** — Storing a client secret in environment variables is insecure — it can be read by anyone with VM access, appear in process listings, or leak through logs. This is a common security vulnerability.
- **B is wrong** — While better than option A (the secret is in Key Vault), there is still a bootstrapping problem: how does the app authenticate to Key Vault the first time to get the secret? You still need credentials for the initial access.
- **D is wrong** — Using root/owner subscription credentials is a catastrophic security risk — any compromise of those credentials means full control of the entire subscription.

---

## Q6 — Conditional Access

**You want to enforce Multi-Factor Authentication (MFA) only when users sign in from outside the corporate network. Which feature should you configure?**

A. Azure AD Password Protection  
B. Azure AD Identity Protection  
C. Azure AD Conditional Access  
D. Azure AD Privileged Identity Management (PIM)  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Conditional Access allows you to define "if/then" policies: "IF user is outside the named corporate IP range, THEN require MFA." It evaluates conditions like location, device compliance, user risk level, and app being accessed — then applies controls like MFA requirement.
- **A is wrong** — Password Protection detects and blocks known weak passwords and banned password patterns. It has nothing to do with location-based MFA.
- **B is wrong** — Identity Protection uses ML to detect risky sign-ins and risky users, and can trigger MFA, but it acts on risk level signals rather than a specific network location condition.
- **D is wrong** — PIM (Privileged Identity Management) controls just-in-time elevation of privileged roles. It doesn't enforce MFA based on network location for regular sign-ins.

---

## Q7 ⭐ — Azure Policy Effects

**You create an Azure Policy with the effect `Deny`. A developer tries to create a storage account without the required `environment` tag. What happens?**

A. The storage account is created without the tag and a violation is logged  
B. The storage account is created with a default tag value added automatically  
C. The storage account creation is blocked and the developer receives an error  
D. The developer is emailed a policy violation notification  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — The `Deny` effect in Azure Policy **prevents the resource operation from completing** if it doesn't comply with the policy. The ARM API call returns an error and the resource is not created.
- **A is wrong** — That describes the `Audit` effect, which allows the resource to be created but logs a compliance violation.
- **B is wrong** — That describes the `Modify` or `Append` effects, which can automatically add or modify properties (including tags) during resource creation.
- **D is wrong** — Azure Policy does not send emails. Email notifications are part of Azure Monitor alerts or Defender for Cloud recommendations, not Policy enforcement.

> **Policy effects in order of restrictiveness:**
> `Disabled` → `Audit` → `AuditIfNotExists` → `Append` → `Modify` → `DeployIfNotExists` → `Deny`

---

## Q8 — Resource Locks

**A team accidentally deleted a production database. You want to prevent this from happening again but still allow the team to update the database configuration. Which resource lock should you apply?**

A. `ReadOnly` lock on the database  
B. `CanNotDelete` lock on the database  
C. `ReadOnly` lock on the resource group  
D. No lock is needed — use RBAC to restrict the delete permission  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — `CanNotDelete` lock prevents deletion of the resource but allows all other read and write operations including configuration changes. This directly addresses the scenario: prevent accidental deletion while allowing normal management.
- **A is wrong** — `ReadOnly` lock prevents both deletion AND modification. The team would be unable to update configuration, which contradicts the requirement.
- **C is wrong** — A `ReadOnly` lock on the resource group would make all resources in the group read-only, preventing the team from making any changes to any resource in the group.
- **D is wrong** — While RBAC can control who has the delete permission, the scenario shows the team already had it and used it accidentally. Locks provide a safety net above RBAC — even an Owner cannot delete a locked resource without first removing the lock.

> **Key fact:** Resource locks override RBAC. Even if a user has Owner role, they cannot delete a resource with a `CanNotDelete` lock. They must first remove the lock (which is audited).

---

## Q9 — Azure AD User Types

**Your company wants to allow a contractor from a partner company to access Azure resources using their existing corporate identity. What type of account should you create?**

A. A new Microsoft Account (personal account) for the contractor  
B. A new Azure AD user account in your tenant  
C. An Azure AD B2B Guest user invitation  
D. An Azure AD B2C user account  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Azure AD B2B (Business-to-Business) allows you to invite external users as guests. They authenticate using their own organization's credentials (their corporate identity) and access your resources as a guest in your tenant. No new password to manage.
- **A is wrong** — Creating a Microsoft personal account is unnecessary and creates a new identity the contractor must manage separately. It also doesn't leverage their existing corporate identity.
- **B is wrong** — Creating a new Azure AD user in your tenant gives the contractor a completely new identity that you must manage (password resets, lifecycle, etc.) and disconnects them from their existing corporate identity.
- **D is wrong** — Azure AD B2C is for customer-facing applications — it manages identities for app consumers (like an e-commerce site's customer login). It is not for partner/B2B access scenarios.

---

## Q10 — RBAC: Data Plane vs Control Plane

**A developer needs to read blob data from an Azure Storage Account. The developer has been assigned the `Contributor` role on the storage account. The developer reports they cannot read the blob content. What is the most likely cause?**

A. The developer needs the `Owner` role instead of `Contributor`  
B. The `Contributor` role grants control plane access only, not data plane access to blob data  
C. The storage account firewall is blocking the developer's IP  
D. The developer needs to regenerate the storage account access key  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure Storage has a split between the control plane (managing the storage account — creating containers, configuring settings, viewing access keys) and the data plane (actually reading/writing blob content). The `Contributor` role grants control plane access but does NOT include data plane roles like `Storage Blob Data Reader` or `Storage Blob Data Contributor`. To read blob data via Azure AD auth, the developer needs `Storage Blob Data Reader` at minimum.
- **A is wrong** — `Owner` also does not include blob data-plane access. The Owner role manages the storage account itself, not the data inside it. The data-plane roles are separate.
- **C is wrong** — While firewall rules are a valid troubleshooting step, the question points to a permissions issue (role assignment). The most likely cause for a role-related question is always the role itself.
- **D is wrong** — Regenerating access keys would change the credentials used by shared-key auth (connection strings), but the scenario is about RBAC-based access, not key-based access.

---

## Q11 — PIM (Privileged Identity Management)

**Your company requires that admin access to Azure resources be granted only when needed and for a limited time. Which feature provides this capability?**

A. Conditional Access with time-based filters  
B. Azure AD Privileged Identity Management (PIM)  
C. Azure AD Identity Protection  
D. Resource Locks with time-based expiry  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — PIM provides **just-in-time (JIT) privileged access**. Users are assigned as "eligible" for a role. When they need access, they activate it through the PIM portal, specify a reason and duration, and receive the role for that limited period. After the time expires, the role is automatically removed.
- **A is wrong** — Conditional Access does not have a concept of time-based role activation. It controls authentication conditions (require MFA, block access from risky locations) but does not manage role duration.
- **C is wrong** — Identity Protection deals with risky user and sign-in detection based on behavior. It doesn't manage role elevation timing.
- **D is wrong** — Resource Locks don't grant or restrict roles and have no time-based expiry — they are permanent until manually removed.

---

## Q12 — Azure AD Groups

**You need to automatically add all users in your organization with the job title "Software Engineer" to an Azure AD security group. What type of group should you create?**

A. Assigned security group  
B. Dynamic security group  
C. Microsoft 365 group  
D. Distribution group  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — A **dynamic security group** uses membership rules based on user attributes (like `jobTitle`, `department`, `country`). When a user's attributes match the rule, they are automatically added; when attributes change and no longer match, they are removed. No manual management needed.
- **A is wrong** — An **assigned** group requires manually adding and removing members. There is no automatic attribute-based membership.
- **C is wrong** — Microsoft 365 groups are collaboration groups (with shared mailbox, Teams, SharePoint) used for team collaboration, not for RBAC/security group scenarios. They can have dynamic membership but are not the right type for RBAC assignment in Azure.
- **D is wrong** — Distribution groups are email distribution lists used in Exchange/Outlook. They cannot be used for Azure RBAC assignments.

---

## Q13 — Policy Compliance

**You assign an Azure Policy with the `Deny` effect to a subscription, but you notice that several existing resources are already non-compliant. What happens to those existing resources?**

A. They are immediately deleted to enforce compliance  
B. They are marked as non-compliant but are not affected — the policy only applies to new/updated resources  
C. They are automatically remediated to make them compliant  
D. They continue to work but cannot be updated until they are compliant  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — When you assign a policy with the `Deny` effect, it only **prevents future non-compliant resource operations**. Existing resources that were created before the policy assignment are evaluated and marked as non-compliant in the compliance dashboard, but they are **not automatically changed, deleted, or blocked**.
- **A is wrong** — Azure Policy never deletes resources. It is not a cleanup tool — it is a governance guard.
- **C is wrong** — Automatic remediation only happens with the `DeployIfNotExists` or `Modify` effect combined with a remediation task. The `Deny` effect does not auto-remediate.
- **D is wrong** — Existing non-compliant resources can still be updated even with a `Deny` policy — UNLESS the update itself would still make it non-compliant (the update request would be denied). Existing resources are not locked.

---

## Q14 — Subscription and Tenant

**A company has two Azure AD tenants (Tenant A and Tenant B). A subscription currently belongs to Tenant A. The company wants to move the subscription to Tenant B. What is the effect on existing role assignments?**

A. All role assignments are automatically moved to Tenant B  
B. All role assignments are deleted when the subscription is transferred to a new tenant  
C. Only Owner role assignments are preserved  
D. Role assignments cannot be moved — the subscription cannot be transferred  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — When a subscription is transferred to a different Azure AD tenant, **all existing RBAC role assignments are permanently deleted**. This happens because role assignments reference security principals (users, groups, service principals) that exist in the original tenant — those identities don't exist in the new tenant. You must recreate all role assignments in the new tenant after the transfer.
- **A is wrong** — Role assignments reference tenant-specific object IDs. These IDs don't exist in the target tenant, so they cannot be transferred.
- **C is wrong** — No role assignments, including Owner, are preserved. All are deleted.
- **D is wrong** — Subscriptions CAN be transferred between tenants. It is a supported operation, but with the understanding that role assignments must be recreated.

> **Pre-transfer checklist:** Document all role assignments before transfer using `az role assignment list --scope /subscriptions/<sub-id> --all-namespaces`

---

## Q15 — Tags

**You apply the tag `environment: production` to a resource group. A new VM is created inside that resource group. Does the VM automatically inherit the tag?**

A. Yes — child resources automatically inherit all tags from the parent resource group  
B. No — Azure tags do not inherit automatically between resource groups and resources  
C. Yes — but only if the resource group has the `Inherit Tags` policy enabled  
D. Yes — but only for resource types that support tagging  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure tags do **not** inherit automatically. A tag on a resource group is only on the resource group itself. Resources created within it start with no tags unless you explicitly set them or use an Azure Policy with the `Inherit tags from the resource group` definition (a built-in policy).
- **A is wrong** — This is a very common misconception. Tags on resource groups do NOT cascade to resources within them by default.
- **C is wrong** — While you CAN use an Azure Policy to enforce tag inheritance, it is not a native automatic feature — it requires a policy assignment.
- **D is wrong** — Tag inheritance has nothing to do with whether a resource type supports tagging. All resources either inherit or don't — and the answer is they don't by default.

---

## Q16 — Azure AD Connect

**Your company has an on-premises Active Directory. Users should be able to sign into Azure using their on-premises AD credentials. What should you deploy?**

A. Azure AD Domain Services (AADDS)  
B. Azure AD Connect  
C. Azure AD B2C  
D. Active Directory Federation Services (ADFS) — no Azure component needed  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure AD Connect is a tool that **synchronizes on-premises Active Directory identities to Azure AD**. Once set up, users can sign into Azure with the same username and password they use on-premises. It supports password hash sync, pass-through authentication, and federation.
- **A is wrong** — Azure AD Domain Services provides managed domain services (LDAP, Kerberos, Group Policy) in Azure — it does not sync on-premises AD to Azure AD for user sign-in purposes.
- **C is wrong** — Azure AD B2C is for managing customer identities for consumer-facing applications, not for internal employee directory sync.
- **D is wrong** — While ADFS can be used for federation, it is the older and more complex approach. Azure AD Connect is the recommended and simpler Microsoft solution for Azure AD integration.

---

## Q17 — Privileged Roles

**Which Azure AD role should you assign to someone who only needs to reset user passwords and manage user accounts, without giving them access to Azure resources?**

A. Global Administrator  
B. User Administrator  
C. Azure Contributor  
D. Helpdesk Administrator  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — The `User Administrator` Azure AD role allows managing users and groups, including resetting passwords, creating users, and managing group memberships. It is an Azure AD directory role, not an Azure RBAC role, so it doesn't grant access to Azure resources.
- **A is wrong** — `Global Administrator` is the highest Azure AD role — it can manage all aspects of Azure AD and Microsoft 365. Assigning this to a helpdesk person violates least privilege significantly.
- **C is wrong** — `Contributor` is an Azure RBAC role for managing Azure resources (VMs, storage, etc.), not for managing Azure AD users and passwords.
- **D is wrong** — `Helpdesk Administrator` can only reset passwords for non-admin users. It cannot create users or manage groups. If you need full user account management, User Administrator is the right role.

---

## Q18 — Azure Policy Initiative

**You want to apply a group of related policies together — for example, enforce specific tagging, require HTTPS on App Services, and deny public IP addresses on VMs — all as a single assignment. What should you use?**

A. Azure Policy assignment with multiple conditions  
B. Azure Policy Initiative (Policy Set)  
C. Azure Blueprints  
D. ARM Template with policy resources  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — An **Initiative** (also called a Policy Set) is a collection of policy definitions grouped together for a common goal. You assign the initiative once and all the included policies apply together. This is the recommended approach for applying a set of related compliance policies.
- **A is wrong** — A single policy definition contains one specific rule. You cannot bundle multiple distinct policies into one "assignment with multiple conditions" — that's what initiatives are for.
- **C is wrong** — Blueprints can bundle policies, but they are a broader governance artifact (they also include resource groups, ARM templates, and role assignments). For just grouping policies, an initiative is simpler and more appropriate.
- **D is wrong** — While you can deploy policies via ARM templates, it doesn't create the concept of a bundled initiative — it just creates individual policy resources.

---

## Q19 — Azure AD Roles vs Azure RBAC Roles

**A user is assigned the `Global Administrator` role in Azure AD. Can they automatically manage all Azure resources (VMs, storage, etc.) in all subscriptions?**

A. Yes — Global Administrator has full access to all Azure resources  
B. No — Azure AD roles and Azure RBAC roles are separate; Global Administrator only controls Azure AD, not Azure resources  
C. Yes — but only in the default subscription  
D. No — Global Administrator must first be assigned the Owner role in each subscription  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure AD and Azure RBAC are two separate access control systems. **Azure AD roles** control Azure Active Directory objects (users, groups, applications, MFA settings). **Azure RBAC roles** control Azure resources (VMs, storage, networking). Global Administrator in Azure AD does NOT automatically get access to Azure subscriptions or resources.
- **A is wrong** — This is a critical misconception. Many candidates assume Global Admin = all-powerful. It is all-powerful within Azure AD but has no inherent Azure resource permissions.
- **C is wrong** — There is no automatic access to any subscription for a Global Administrator unless they also have Azure RBAC assignments.
- **D is wrong** — While a Global Administrator CAN elevate themselves to User Access Administrator at the root scope (via the Azure AD portal option "Access management for Azure resources"), this is a deliberate action, not automatic. Without this, they have no Azure resource access.

---

## Q20 — Delete Resource Group

**You need to delete a resource group. What happens to all the resources inside it?**

A. The resources become orphaned and must be deleted separately  
B. The resources are moved to the default resource group  
C. All resources inside the resource group are also deleted  
D. Resources with locks are preserved; all others are deleted  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Deleting a resource group is a **cascading delete operation** — all resources contained within it are permanently deleted along with the resource group itself.
- **A is wrong** — Resources cannot exist without a resource group in Azure — they don't become orphaned.
- **B is wrong** — There is no "default resource group" concept in Azure that catches orphaned resources.
- **D is wrong** — Resource locks DO prevent deletion. If any resource in the resource group has a `CanNotDelete` lock, the entire resource group deletion will fail with an error — you must remove the lock first. The group won't partially delete.

---

# Domain 2 — Implement and Manage Storage

---

## Q21 ⭐ — Storage Account Redundancy

**Your company requires that Azure Blob Storage remain available even if an entire Azure region goes down, with automatic failover. Which redundancy option should you choose?**

A. Locally-Redundant Storage (LRS)  
B. Zone-Redundant Storage (ZRS)  
C. Geo-Redundant Storage (GRS)  
D. Geo-Zone-Redundant Storage (GZRS)  

**✅ Correct Answer: D**

**Explanation:**
- **D is correct** — **GZRS** combines zone redundancy within the primary region (3 copies across 3 availability zones) AND geo-replication to a secondary region. If the entire primary region goes down, automatic failover to the secondary region is supported. This is the highest redundancy option Azure offers.
- **A is wrong** — LRS keeps 3 copies within a single datacenter in one region. A single datacenter failure (let alone region failure) would cause data loss.
- **B is wrong** — ZRS replicates across 3 availability zones in one region. It survives datacenter failures but NOT regional failures.
- **C is wrong** — GRS replicates to a secondary region but does NOT use availability zones in the primary region. It survives regional failures but has lower zone-level protection in the primary. Also, GRS secondary access requires Microsoft-initiated failover unless RA-GRS is used.

```
  LRS:  [DC1: 3 copies] — survives: disk failure
  ZRS:  [Zone1][Zone2][Zone3] — survives: datacenter/zone failure
  GRS:  [Primary Region LRS] + [Secondary Region] — survives: regional failure
  GZRS: [Primary ZRS] + [Secondary Region] — survives: zone AND regional failure ✅
```

---

## Q22 — Storage Account Access Tiers

**You have blob data that is accessed frequently for the first 30 days and then rarely accessed for the following year, after which it can be deleted. What is the MOST cost-effective storage configuration?**

A. Store all data in Hot tier for the full year  
B. Store all data in Cool tier from day 1  
C. Start in Hot tier, move to Cool after 30 days, move to Archive after 60 days, delete after 1 year — using lifecycle management  
D. Store all data in Archive tier from day 1  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Azure Blob Storage lifecycle management policies can automatically tier data based on age. Hot tier costs more per GB but less per operation (good for frequent access). Cool tier costs less per GB but more per operation (good for infrequent access). Archive tier has the lowest storage cost but high retrieval cost and delay. Matching the tier to the access pattern is the most cost-effective approach.
- **A is wrong** — Keeping rarely accessed data in Hot tier wastes money — Hot tier has the highest storage cost per GB.
- **B is wrong** — The first 30 days of frequent access in Cool tier means high transaction costs (Cool charges more per read operation). Cool is not optimal for frequently accessed data.
- **D is wrong** — Archive tier makes data inaccessible without a rehydration process (taking hours). Frequently accessed data cannot be in Archive tier without massive operational overhead and cost.

---

## Q23 ⭐ — SAS Token

**You need to give an external partner temporary read-only access to a specific blob container for 48 hours, without sharing your storage account keys. What should you use?**

A. Store the account key in an environment variable and share it  
B. Generate a Shared Access Signature (SAS) token with read permissions expiring after 48 hours  
C. Create a new storage account specifically for the partner  
D. Add the partner as a guest user and assign `Storage Blob Data Reader`  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — A **Shared Access Signature (SAS)** token is a URI that grants limited access (specific permissions, specific resources, for a specific time window) without exposing the account key. It's the designed solution for granting temporary external access.
- **A is wrong** — Sharing an account key gives FULL access to the entire storage account with no time limit. This is a security anti-pattern. If the key leaks, you must rotate it immediately.
- **C is wrong** — Creating a new storage account adds unnecessary complexity, cost, and management overhead just for temporary external access.
- **D is wrong** — While technically valid for an Azure AD user, a B2B guest invitation process is heavyweight for temporary 48-hour partner access. SAS tokens are the standard mechanism for this scenario. Also, a pure external partner may not have an Azure AD account to invite.

---

## Q24 — Storage Firewall

**You configure an Azure Storage Account firewall to allow access only from your virtual network. A developer on the Azure team reports they can no longer access the storage account from the Azure Portal. What should you add to allow portal access?**

A. Add the developer's IP address to the firewall allowlist  
B. Enable the "Allow trusted Microsoft services to access this storage account" exception  
C. Disable the storage firewall entirely  
D. Create a private endpoint for the storage account  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — When you enable storage firewall rules, Azure portal and Azure services (Azure Backup, Azure Data Factory, Azure Monitor diagnostics) may be blocked. The "Allow trusted Microsoft services" exception permits a curated list of Microsoft services (including the Azure Portal ARM operations, Backup, Monitor, etc.) to bypass the firewall. This is the standard configuration when using storage firewalls.
- **A is wrong** — Adding the developer's IP allows them to connect via network, but the portal uses Microsoft's backend services, not the developer's direct IP. The issue is the portal backend services being blocked.
- **C is wrong** — Disabling the firewall removes all security — the opposite of what you want.
- **D is wrong** — A private endpoint would work for VNet-based access but doesn't specifically solve the Azure Portal access issue described, and adds complexity. The exception flag is the right solution.

---

## Q25 — Storage Account Naming

**Which of the following is a valid Azure Storage Account name?**

A. `my-storage-account-prod`  
B. `MyStorageAccountProd`  
C. `mystorageaccountprod`  
D. `msa`  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Storage account names must be: **3–24 characters**, **lowercase letters and numbers only**, **globally unique across all of Azure**. `mystorageaccountprod` satisfies all these constraints.
- **A is wrong** — Hyphens (`-`) are not allowed in storage account names.
- **B is wrong** — Uppercase letters are not allowed in storage account names. Names must be all lowercase.
- **D is wrong** — `msa` is only 3 characters — technically valid in length, but would likely already be taken. More importantly, it's an important naming gotcha: 3 characters is the minimum.

---

## Q26 — Azure Files vs Blob Storage

**Your application needs a shared file system that multiple Azure VMs (running Windows) can mount simultaneously, like a traditional network share. Which storage service should you use?**

A. Azure Blob Storage  
B. Azure Files  
C. Azure Managed Disks  
D. Azure Table Storage  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Files** provides fully managed cloud file shares accessible via the **SMB (Server Message Block)** protocol and NFS. Windows VMs can mount it as a network drive using standard Windows drive mapping. Multiple VMs can mount the same share simultaneously (unlike managed disks).
- **A is wrong** — Blob storage uses a REST API — it cannot be mounted as a file system by multiple VMs simultaneously like a network share. It requires custom code or tools to access.
- **C is wrong** — Managed Disks are VHD-style disks that attach to a single VM (like a physical hard drive). They cannot be shared between multiple VMs simultaneously for read/write (Premium SSD v2 and Ultra Disk support shared disks but require special configuration and are limited).
- **D is wrong** — Table Storage is a NoSQL key-value store for structured data. It has no filesystem semantics and cannot be mounted as a network drive.

---

## Q27 — Storage Replication

**A developer stored critical data in Azure Blob Storage with LRS (Locally Redundant Storage). An entire Azure datacenter failure caused data loss. Which upgrade would have prevented this?**

A. Upgrading to Premium performance tier  
B. Upgrading to ZRS (Zone-Redundant Storage)  
C. Enabling HTTPS-only on the storage account  
D. Enabling soft delete on the storage account  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — ZRS replicates data synchronously across **3 availability zones** in the same region. An entire datacenter failure corresponds to one availability zone going down. ZRS survives this scenario — data is still available in the other 2 zones.
- **A is wrong** — Premium storage is about performance (lower latency, higher IOPS) — it doesn't change the redundancy model. Premium LRS still has the same single-datacenter vulnerability.
- **C is wrong** — HTTPS-only is a security setting for data in transit. It has no effect on data durability or availability during hardware failures.
- **D is wrong** — Soft delete protects against **accidental deletion** by humans — it keeps deleted data recoverable for a retention period. It cannot protect against infrastructure/datacenter failure.

---

## Q28 ⭐ — Access Keys vs RBAC for Storage

**You need to prevent anyone from using storage account access keys to access data and enforce Azure AD-based authentication only. What setting should you configure?**

A. Regenerate both access keys and keep them secret  
B. Disable shared key access on the storage account  
C. Set the minimum TLS version to 1.2  
D. Enable storage firewall rules  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — The **"Disable shared key access"** setting on a storage account (`allowSharedKeyAccess: false`) prevents authentication using storage account keys. All access must then use Azure AD (Entra ID) authentication with RBAC roles. This enforces the modern zero-shared-secret posture.
- **A is wrong** — Regenerating keys just creates new keys — it doesn't prevent key-based access. As long as keys exist and haven't been disabled, they can be used.
- **C is wrong** — Setting minimum TLS version enforces encryption standards for data in transit. It doesn't affect the authentication method (keys vs Azure AD).
- **D is wrong** — Firewall rules control which network addresses can connect to the storage account. They don't control whether key auth or Azure AD auth is used.

---

## Q29 — Blob Access Tiers

**You have archived data in the Archive tier and need to urgently access it within 1 hour. What is the correct process?**

A. Directly download the blob — Archive tier blobs download instantly  
B. Rehydrate the blob by changing its tier to Hot or Cool, which takes 1–15 hours for Standard priority  
C. Rehydrate the blob using High Priority, which can complete within 1 hour for blobs under 10 GB  
D. Copy the blob to a new storage account where it becomes immediately accessible  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — Azure Blob Storage offers two rehydration priority options from Archive: **Standard Priority** (1–15 hours) and **High Priority** (under 1 hour for blobs < 10 GB, higher cost). If urgent access is required within 1 hour, High Priority rehydration is the correct approach.
- **A is wrong** — Archive tier blobs are **offline**. They cannot be directly read or downloaded without first rehydrating them to Hot or Cool tier. Any attempt to read an archived blob returns an error.
- **B is wrong** — Standard priority rehydration can take 1–15 hours. This does not guarantee access within 1 hour.
- **D is wrong** — Copying an archived blob still requires rehydrating it first. You cannot copy a blob that is in the offline Archive state directly.

---

## Q30 — Storage Account Types

**You need a storage account that provides the lowest latency and highest IOPS for an Azure Virtual Machine's OS disk. Which storage account type should you use?**

A. Standard General-Purpose v2 with LRS  
B. Premium Block Blobs  
C. Premium Page Blobs (via Azure Managed Disks Premium SSD)  
D. Standard General-Purpose v1  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — VM OS disks use **page blobs** under the hood (or managed disks, which are page blobs in Microsoft-managed storage accounts). For lowest latency and highest IOPS, **Premium SSD Managed Disks** (backed by Premium Page Blob storage) are the right choice. Premium storage uses SSDs and provides single-millisecond latencies.
- **A is wrong** — Standard storage uses HDDs, which have significantly higher latency (~10ms) and lower IOPS. Not suitable for VM OS disks in production.
- **B is wrong** — Premium Block Blobs are optimized for block blob workloads (large sequential writes like logs, video) — not for page blob / VM disk usage patterns.
- **D is wrong** — General-Purpose v1 is the legacy storage account type. It has fewer features and is not recommended for new deployments. It also uses HDDs for standard tier.

---

## Q31 — Blob Storage Access Levels

**You upload a blob to a container configured with `Private` access level. How can a user access the blob without Azure AD credentials or an account key?**

A. They cannot — Private access means no anonymous or key-less access  
B. They can access it via a direct URL since blob storage is public by default  
C. You must generate a SAS token and share the URL with them  
D. You need to change the container to Public access level  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — With a Private container, anonymous access is blocked. To give someone temporary access without credentials, you generate a **SAS token** — a URL with embedded permissions and expiry. The user accesses the blob via this SAS URL without needing Azure AD or account keys.
- **A is wrong** — While "cannot access without credentials" is essentially true, option C provides the correct mechanism for giving them access without sharing permanent credentials.
- **B is wrong** — Blobs are NOT public by default. Public access must be explicitly configured at both the storage account level (allowBlobPublicAccess) and container level. By default, all containers are Private.
- **D is wrong** — Changing to Public access gives anonymous access to EVERYONE — any person on the internet can read any blob in the container without any credentials. This is a massive security risk for anything other than intentionally public content.

---

## Q32 — Azure File Sync

**You have on-premises file servers with 100 TB of data. You want to move data to Azure Files but keep the most accessed data on-premises for performance. Which solution fits this requirement?**

A. AzCopy all data to Azure Files and access it from the cloud  
B. Azure File Sync with cloud tiering enabled  
C. Azure Backup to protect on-premises file servers  
D. Azure Data Box to transfer data once to Azure  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure File Sync** synchronizes your on-premises file server with Azure Files. When **cloud tiering** is enabled, frequently accessed files are kept locally on the file server (cached), while less frequently accessed files are tiered to Azure (only a stub remains on-premises). Users still see all files in Explorer; accessing a tiered file recalls it transparently. This gives cloud scale with local performance.
- **A is wrong** — Moving all 100 TB to Azure Files and accessing from the cloud would add latency for all on-premises users. Also, AzCopy is a migration tool, not an ongoing sync solution.
- **C is wrong** — Azure Backup protects data from accidental deletion and disaster. It doesn't help with cloud tiering or reducing on-premises storage while maintaining access performance.
- **D is wrong** — Azure Data Box is a physical device for bulk one-time migration — it doesn't provide ongoing sync or cloud tiering.

---

## Q33 — Storage Account Soft Delete

**A developer accidentally deletes a blob from a container. The storage account has blob soft delete enabled with a 7-day retention period and the deletion happened 3 days ago. What can you do?**

A. Nothing — deleted blobs are permanently gone  
B. Restore the blob using the "Undelete Blob" operation  
C. Restore from the most recent backup taken before deletion  
D. Contact Microsoft support to retrieve the blob  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Blob soft delete keeps deleted blobs in a "deleted" state for the configured retention period (7 days in this case). Since only 3 days have passed, the blob is still within the retention window. You can restore it using the `Undelete Blob` REST API operation or through the Azure Portal by showing deleted blobs and clicking Undelete.
- **A is wrong** — Without soft delete, blobs are permanently gone. But with soft delete enabled, they are recoverable within the retention period.
- **C is wrong** — While backups can restore data, using "Undelete Blob" is faster and simpler since the data is still available within the soft delete window. Restoring from backup is the fallback if soft delete wasn't enabled or retention expired.
- **D is wrong** — Microsoft support cannot retrieve customer data — they don't have access to blob data. The recovery capability rests entirely with you via soft delete.

---

## Q34 — Immutable Storage

**Regulatory requirements mandate that audit logs stored in Azure Blob Storage cannot be modified or deleted for 7 years. Which feature should you configure?**

A. Storage Account access keys rotation  
B. Blob versioning  
C. WORM (Write Once, Read Many) policy — immutable blob storage  
D. Blob soft delete with 7-year retention  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Immutable blob storage** (WORM policies) allows configuring blobs so they cannot be modified or deleted for a specified period. Two policy types: **Time-based retention policies** (data is immutable for the specified duration) and **Legal hold policies** (data is immutable until the hold is removed). This meets regulatory compliance requirements (SEC 17a-4, CFTC, FINRA).
- **A is wrong** — Access key rotation is a security practice for changing credentials. It doesn't prevent modification or deletion of data.
- **B is wrong** — Blob versioning keeps previous versions of blobs when they are overwritten, but it doesn't prevent deletion of all versions. It also doesn't enforce a time-based retention period.
- **D is wrong** — Soft delete has a maximum retention of 365 days (1 year), not 7 years. It also doesn't prevent modification. WORM policies are specifically designed for regulatory compliance scenarios.

---

## Q35 — AzCopy

**You need to copy 5 TB of data from an AWS S3 bucket to Azure Blob Storage. Which tool should you use?**

A. Azure Data Box  
B. Azure Storage Explorer (GUI drag and drop)  
C. AzCopy with S3 source support  
D. Azure Import/Export service  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **AzCopy** is a command-line tool designed for bulk data transfer to/from Azure Storage. It supports copying directly from **Amazon S3** as a source: `azcopy copy 'https://s3.amazonaws.com/mybucket/*' 'https://myaccount.blob.core.windows.net/mycontainer/' --recursive`. It handles authentication to both services.
- **A is wrong** — Azure Data Box is a physical device sent to your location. For cloud-to-cloud migration (S3 → Azure Blob), you don't need physical hardware shipment — AzCopy works over the internet.
- **B is wrong** — Azure Storage Explorer is a GUI tool for exploring and managing storage — it doesn't have built-in S3 source support for bulk migration at 5 TB scale.
- **D is wrong** — Azure Import/Export is for shipping physical hard drives to Azure datacenters. For S3 data, the data is already in the cloud — you use AzCopy for direct cloud transfer.

---

## Q36 — Storage Account vs Managed Disk

**What is the key difference between an Azure Managed Disk and an unmanaged disk stored in a storage account?**

A. Managed disks are always encrypted; unmanaged disks are not  
B. With managed disks, Microsoft handles the storage account, capacity planning, and scaling; with unmanaged disks, you manage the storage account  
C. Managed disks support only Windows VMs; unmanaged disks support both Windows and Linux  
D. Unmanaged disks have better performance than managed disks  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — With **unmanaged disks**, you create a storage account, manage capacity (storage account limits), and store the VHD blob yourself. With **managed disks**, Azure fully manages the underlying storage — you just select the disk size/type and Azure handles availability, durability, and scaling. Managed disks are the recommended approach.
- **A is wrong** — Both managed and unmanaged disks support encryption. Managed Disks support Azure Disk Encryption (ADE) and Encryption at rest by default. Unmanaged disks in storage accounts also encrypt at rest via Storage Service Encryption.
- **C is wrong** — Both managed and unmanaged disks support Windows and Linux VMs.
- **D is wrong** — Managed disks do NOT have worse performance. They are backed by the same underlying Azure Storage infrastructure and in many cases have better performance guarantees with Premium and Ultra SSD tiers.

---

## Q37 — Storage Metrics and Diagnostics

**How do you configure Azure Storage to send metrics and logs to a Log Analytics workspace for analysis?**

A. Enable Azure Monitor diagnostic settings on the storage account and route to the Log Analytics workspace  
B. Install a monitoring agent on the storage account VM  
C. Enable storage account diagnostic logs in the Azure Portal and export to an Excel file  
D. Configure the storage account firewall to allow Log Analytics access  

**✅ Correct Answer: A**

**Explanation:**
- **A is correct** — **Azure Monitor Diagnostic Settings** is the standard mechanism for routing platform logs and metrics from Azure resources (including Storage Accounts) to destinations: Log Analytics workspace, Storage Account (archival), or Event Hub (streaming). You enable this per storage service (Blob, Queue, Table, File) within the storage account.
- **B is wrong** — Storage Accounts are not VMs — you can't install monitoring agents on them. Storage is a PaaS service; monitoring is configured via Diagnostic Settings, not agents.
- **C is wrong** — You cannot export live storage logs directly to Excel from the portal. Export to Excel is for portal grid views, not log streaming.
- **D is wrong** — Firewall rules control network access to the storage account, not log routing. Log Analytics integration is configured via Diagnostic Settings regardless of firewall rules.

---

## Q38 — Storage Account Premium vs Standard

**Your application uses Azure Queues for message processing. The messages must be processed with single-digit millisecond latency. Which storage account type supports this?**

A. Standard General-Purpose v2  
B. Premium Block Blobs  
C. Premium File Shares  
D. Standard General-Purpose v1  

**✅ Correct Answer: A**

**Explanation:**
- **A is correct** — Azure Queue Storage is only available in **Standard General-Purpose v2** (and v1) storage accounts — NOT in Premium storage accounts. Standard GPv2 with Queue Storage meets typical queue workload requirements. If single-digit millisecond latency is needed for messaging at scale, **Azure Service Bus Premium** would be a better architectural choice.
- **B is wrong** — Premium Block Blobs storage accounts support only block blobs — they do not support Queue Storage.
- **C is wrong** — Premium File Shares accounts support only Azure Files — they do not support Queue Storage.
- **D is wrong** — Standard v1 is the legacy type and lacks features. New storage accounts should use v2. Also, v1 supports queues but is not the recommended answer due to being legacy.

> **Note:** Premium storage accounts are type-specific: Premium Block Blobs (blobs only), Premium File Shares (files only), Premium Page Blobs (page blobs/disks only).

---

# Domain 3 — Deploy and Manage Azure Compute Resources

---

## Q39 ⭐ — VM Availability Options

**You need two VMs to host a web application with 99.95% SLA and protection against planned maintenance. Which availability option should you use?**

A. Deploy both VMs in the same Availability Zone  
B. Deploy both VMs in the same Availability Set  
C. Deploy both VMs in different Availability Zones  
D. Deploy both VMs in the same region with no availability configuration  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — An **Availability Set** places VMs across multiple **update domains** (up to 5, protecting against planned maintenance reboots) and **fault domains** (up to 3, protecting against hardware failures). Azure guarantees 99.95% SLA when 2+ VMs are in the same availability set. This is the classic HA configuration for VMs in a single datacenter.
- **A is wrong** — Deploying in the SAME Availability Zone keeps VMs in the same datacenter — no separation. This doesn't protect against hardware failure in that zone.
- **C is wrong** — Deploying in DIFFERENT Availability Zones provides 99.99% SLA (higher than 99.95%), but the question asks specifically about the 99.95% scenario, and zone-to-zone traffic may have latency/bandwidth costs.
- **D is wrong** — With no availability configuration, Azure provides no SLA guarantee. VMs could be on the same physical host and fail together during maintenance.

```
  Availability Set:
  VM1 → Fault Domain 0, Update Domain 0
  VM2 → Fault Domain 1, Update Domain 1

  During planned maintenance: VMs in different UDs don't reboot simultaneously
  During hardware failure: VMs in different FDs don't share power/network
```

---

## Q40 ⭐ — VM Scale Sets

**Your application experiences highly variable load — sometimes needing 2 VMs, sometimes needing 50. You want to automatically scale based on CPU usage without manual intervention. What should you use?**

A. Deploy 50 VMs and shut them down when not needed  
B. Azure Virtual Machine Scale Sets (VMSS) with autoscaling rules  
C. Azure App Service with manual scale-out  
D. Azure Container Instances with multiple containers  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **VM Scale Sets** is designed exactly for this scenario. It creates and manages a group of identical VMs. Autoscaling rules can automatically add VMs when CPU exceeds a threshold (scale out) and remove VMs when CPU drops below a threshold (scale in). The fleet can scale from 2 to 50 (or more) automatically.
- **A is wrong** — Pre-deploying 50 VMs and manually shutting them down is not autoscaling. Stopped (deallocated) VMs don't cost compute but still cost storage, and manual management defeats the purpose.
- **C is wrong** — App Service is a PaaS platform for web apps, not for VMs. The question specifies VM-level infrastructure.
- **D is wrong** — Azure Container Instances are for running containers, not traditional VM workloads. Also, ACI instances are designed for short-lived, isolated tasks — not a persistent autoscaling fleet.

---

## Q41 — VM Sizes

**A data scientist needs an Azure VM for training machine learning models that require significant GPU resources. Which VM series should you recommend?**

A. D-series (General Purpose)  
B. F-series (Compute Optimized)  
C. N-series (GPU)  
D. E-series (Memory Optimized)  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — The **N-series** (NC, ND, NV, NVv3, NCv3) VMs include NVIDIA GPUs. NC-series is for GPU compute (training ML models, CUDA workloads). NV-series is for GPU visualization. GPU-equipped VMs are explicitly required for GPU-accelerated ML training workloads.
- **A is wrong** — D-series are general-purpose VMs (balanced CPU/RAM). They have no GPU — unsuitable for GPU-accelerated ML.
- **B is wrong** — F-series are compute-optimized (high CPU-to-RAM ratio). Still no GPU — good for CPU-bound compute but not GPU ML training.
- **D is wrong** — E-series are memory-optimized (high RAM-to-CPU ratio). Good for in-memory databases (SAP HANA, large caching). No GPU.

---

## Q42 — VM Extensions

**After deploying an Azure VM, you need to automatically install and configure the IIS web server without connecting to the VM via RDP. What should you use?**

A. VM Boot diagnostics  
B. Custom Script Extension  
C. Azure Desired State Configuration (DSC) Extension  
D. Azure VM Insights  

**✅ Correct Answer: B (or C — both valid, but B is most direct)**

**✅ Also valid: C**

**Explanation:**
- **B is correct** — The **Custom Script Extension** allows you to run PowerShell scripts (or bash scripts on Linux) on a deployed VM automatically. You can specify a script that installs IIS (`Install-WindowsFeature -name Web-Server -IncludeManagementTools`). It runs the script via the Azure agent without requiring RDP access.
- **C is also valid** — **Azure DSC Extension** is a configuration management extension based on PowerShell DSC. It can declare the desired state ("IIS should be installed and running") and enforce it. Both B and C are legitimate answers; B is simpler, C is better for ongoing configuration drift prevention.
- **A is wrong** — Boot diagnostics captures serial console output and screenshot — useful for troubleshooting boot failures, not for installing software.
- **D is wrong** — Azure VM Insights monitors VM performance (CPU, memory, network, disk metrics) — it doesn't install or configure software.

---

## Q43 ⭐ — App Service Plans

**You have two web applications with minimal traffic. You want to minimize cost by sharing the underlying compute infrastructure between both apps. What should you do?**

A. Deploy each app to separate App Service Plans in different regions  
B. Deploy both apps to the same App Service Plan  
C. Deploy both apps as Azure Functions on Consumption plan  
D. Deploy both apps on separate Azure Container Instances  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — An **App Service Plan** defines the underlying compute (region, SKU, instance count). Multiple App Service apps can share a single App Service Plan — they all run on the same VMs, sharing resources. You pay for the Plan, not per app. This is the standard approach for cost optimization.
- **A is wrong** — Separate App Service Plans means separate compute — you pay for both plans. More expensive, not less.
- **C is wrong** — Azure Functions on Consumption plan could work for event-driven workloads but the question describes traditional web applications which may have always-on requirements. The Consumption plan also has cold start penalties. And this changes the architecture significantly.
- **D is wrong** — Separate Container Instances are separate compute units — you pay for each. Not cost-optimized for sharing compute.

> **App Service Plan limit:** A single App Service Plan can host up to ~100 apps (in Standard/Premium tiers). Apps in the same plan share the plan's CPU and RAM.

---

## Q44 — Azure Functions — Hosting Plans

**An Azure Function needs to run on a schedule every 5 minutes. The function runs for about 2 seconds each time. What hosting plan is MOST cost-effective?**

A. Dedicated (App Service) Plan  
B. Premium Plan  
C. Consumption Plan  
D. Kubernetes-based hosting  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — The **Consumption Plan** charges only for the actual execution time and number of executions. A function running for 2 seconds every 5 minutes = 720 executions per hour × 2 seconds = 1,440 seconds/hour of actual compute. The first 1 million executions and 400,000 GB-seconds per month are free. This is the most cost-effective for low-frequency, short-duration functions.
- **A is wrong** — The Dedicated plan charges for the App Service Plan continuously, even when the function isn't running. For a function running only 2 seconds every 5 minutes, you pay for 5 minutes of idle time for every 2 seconds of use — extremely wasteful.
- **B is wrong** — Premium Plan has pre-warmed instances and no cold start, but also charges continuously like the Dedicated plan. Justified for functions needing VNet integration, no cold start, or long running (>10 min). Overkill for this scenario.
- **D is wrong** — Kubernetes-based hosting adds significant operational complexity for a simple scheduled function. Not appropriate here.

---

## Q45 — Azure Kubernetes Service (AKS)

**You deploy an AKS cluster. The control plane (API server, etcd, scheduler) is managed by Azure. What do YOU pay for in AKS?**

A. The control plane VMs and the worker node VMs  
B. Only the worker node VMs (control plane is free)  
C. Only networking — compute is fully managed and free  
D. Per API call to the Kubernetes API server  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — AKS provides a **free managed control plane** — you don't pay for the API server, etcd, scheduler, or controller manager. You pay only for the **worker nodes** (the VMs in your node pools), their attached disks, networking, and any additional Azure services used (Load Balancer, Storage).
- **A is wrong** — You do not pay for the control plane VMs — Microsoft manages and pays for them. Only worker nodes are billable to you.
- **C is wrong** — Compute for worker nodes is absolutely a cost. Only control plane compute is free.
- **D is wrong** — AKS doesn't charge per API call. The billing model is based on worker node VM hours.

---

## Q46 — Container Registry

**Your development team builds Docker images in a CI/CD pipeline. You need a private container registry in Azure to store these images. What should you use?**

A. Docker Hub with private repositories  
B. Azure Container Registry (ACR)  
C. Azure Blob Storage with container images stored as blobs  
D. GitHub Container Registry  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Container Registry (ACR)** is Azure's managed private Docker registry. It integrates natively with Azure services (AKS, App Service, Azure Functions, Azure DevOps, GitHub Actions). It supports geo-replication, image scanning (Microsoft Defender), and private endpoints for secure access.
- **A is wrong** — Docker Hub is a valid option but is a third-party service. For Azure-native integration, private networking (VNet connectivity), and Azure AD authentication, ACR is the preferred choice.
- **C is wrong** — Blob Storage is for unstructured data storage. Container images are OCI-formatted layers — they need a registry that understands the Docker/OCI API. You cannot use a storage account as a Docker registry without additional software.
- **D is wrong** — GitHub Container Registry is valid for GitHub-centric workflows but is a GitHub service, not Azure-native. For enterprise Azure workloads, ACR is preferred.

---

## Q47 — VM Disk Types

**A production database server requires the highest possible disk IOPS and sub-millisecond latency. Cost is secondary. Which Azure disk type should you choose?**

A. Standard HDD  
B. Standard SSD  
C. Premium SSD  
D. Ultra Disk  

**✅ Correct Answer: D**

**Explanation:**
- **D is correct** — **Ultra Disk** provides the highest performance: up to 160,000 IOPS, up to 4 GB/s throughput, and sub-millisecond latency. You can configure IOPS and throughput independently. It is the top-tier option for latency-sensitive databases like SAP HANA or high-frequency transaction systems.
- **A is wrong** — Standard HDD is the lowest performance tier: ~2,000 IOPS, ~60 MB/s throughput, ~10ms latency. Only suitable for dev/test or infrequently accessed data.
- **B is wrong** — Standard SSD improves on HDD but still delivers only ~6,000 IOPS and ~400 MB/s. Not suitable for high-performance production databases.
- **C is wrong** — Premium SSD is excellent for most production databases: up to ~20,000 IOPS and ~900 MB/s. For maximum performance workloads, Ultra Disk exceeds Premium SSD significantly.

```
  Disk Type    | Max IOPS   | Max Throughput | Latency    | Cost
  ─────────────┼────────────┼────────────────┼────────────┼────────
  Standard HDD | ~2,000     | ~60 MB/s       | ~10ms      | $
  Standard SSD | ~6,000     | ~400 MB/s      | ~5ms       | $$
  Premium SSD  | ~20,000    | ~900 MB/s      | <1ms       | $$$
  Ultra Disk   | 160,000    | 4,000 MB/s     | <0.5ms     | $$$$
```

---

## Q48 — ARM Templates

**You want to deploy the same infrastructure (VNet, VM, storage account) to three different environments (dev, staging, prod) with slight differences in VM size per environment. What is the BEST approach?**

A. Create three separate ARM templates, one for each environment  
B. Use a single ARM template with parameters and deploy with different parameter files per environment  
C. Deploy manually via the Azure Portal for each environment  
D. Use Azure CLI scripts with hardcoded values for each environment  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — ARM templates support **parameters** — values that are passed in at deployment time. You create one template and three separate parameter files (`dev.parameters.json`, `staging.parameters.json`, `prod.parameters.json`). This is the standard IaC approach: single source of truth for infrastructure, variable configuration per environment.
- **A is wrong** — Three separate templates means three separate maintenance burdens. When you need to update the infrastructure (add a new resource), you must update all three templates. This leads to configuration drift.
- **C is wrong** — Manual portal deployment is not repeatable, not version-controlled, and error-prone. It doesn't scale to multiple environments.
- **D is wrong** — Hardcoded CLI scripts have the same problem as separate templates — three separate scripts to maintain, no reuse, configuration drift.

---

## Q49 — Azure Container Instances vs AKS

**A developer needs to run a containerized batch processing job that runs for 30 minutes once a day and then exits. Which service is MOST appropriate?**

A. Azure Kubernetes Service (AKS)  
B. Azure Container Instances (ACI)  
C. Azure Virtual Machines with Docker  
D. Azure App Service with Docker  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Container Instances (ACI)** is designed for on-demand, short-lived container execution. It starts a container in seconds, runs until completion, and you pay only for the duration it runs (per second billing). Perfect for batch jobs, scheduled tasks, or CI/CD pipeline steps.
- **A is wrong** — AKS is designed for persistent, complex multi-container applications requiring orchestration (service discovery, rolling updates, secrets management). Running a simple batch job on AKS requires setting up a Kubernetes cluster (overhead and cost) for a job that could run on ACI for a fraction of the cost.
- **C is wrong** — Running a VM 24/7 for a 30-minute daily batch job wastes 23.5 hours of VM cost per day. VM cost is continuous regardless of whether the container is running.
- **D is wrong** — App Service is for long-running web applications and APIs. While it can run containers, it's not optimized for batch jobs that start, run, and stop.

---

## Q50 ⭐ — VM Deallocate vs Stop

**A team uses the Azure Portal's "Stop" button to shut down a VM at the end of each day. They notice they are still being charged for the VM. What should they do instead?**

A. Delete the VM and recreate it each morning  
B. Use "Stop (Deallocate)" to fully deallocate the VM's compute resources  
C. Shut down the operating system from within the VM  
D. Remove the VM from its availability set  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — "**Stop (Deallocate)**" releases the VM's CPU and RAM back to Azure's pool. You stop being charged for compute. You still pay for the managed disk and public IP (if static). This is the correct way to avoid compute charges while keeping the VM's configuration.
- **A is wrong** — Deleting and recreating VMs daily is wasteful and risky (configuration loss, different IPs, different disks). Not practical for a daily workflow.
- **C is wrong** — Shutting down the OS from within the VM (via `shutdown /s` or `poweroff`) stops the OS but keeps the VM in the **Stopped (not deallocated)** state. Azure still holds the compute resources allocated to the VM and **continues billing for compute**. This is the common gotcha.
- **D is wrong** — Removing from an availability set doesn't stop or deallocate the VM — it's still running and billing.

> **⚠️ Critical Gotcha:** There are two "stopped" states:
> - `Stopped` (OS shutdown): still billed for compute ❌
> - `Stopped (Deallocated)`: compute released, no compute billing ✅
> Always use "Stop (Deallocate)" or `az vm deallocate` to avoid charges.

---

## Q51 — Azure Batch

**Your scientific computing workload involves running thousands of parallel simulation jobs. Each job takes 10 minutes and produces output files. No persistent service is needed between jobs. What Azure service is BEST suited?**

A. Azure Virtual Machine Scale Sets  
B. Azure Kubernetes Service  
C. Azure Batch  
D. Azure Functions Premium  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Azure Batch** is specifically designed for large-scale parallel and high-performance computing (HPC) workloads. It automatically provisions and manages pools of VMs, schedules jobs, retries failed tasks, and scales down when work is done. Thousands of parallel jobs is exactly the Azure Batch use case.
- **A is wrong** — VMSS autoscales a fleet of identical VMs but doesn't include job scheduling, task distribution, retry logic, or output collection. You'd have to build all that yourself.
- **B is wrong** — AKS can run batch workloads but requires significant Kubernetes knowledge and setup. Azure Batch is specifically designed for this job-queue pattern with less overhead.
- **D is wrong** — Azure Functions Premium is for event-driven serverless functions. It has a 10-minute execution limit (configurable to unlimited on Premium) but is not designed for massively parallel HPC batch job orchestration.

---

## Q52 — App Service Deployment Slots

**You want to deploy a new version of your web application to Azure App Service with zero downtime and the ability to instantly roll back if issues are found. What feature should you use?**

A. VNet Integration  
B. Deployment Slots with slot swap  
C. App Service Scale Out  
D. Azure CDN integration  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Deployment Slots** allow you to deploy new code to a staging slot while the production slot serves live traffic. After validation, you perform a **slot swap** which atomically switches staging → production. The swap is instant (no downtime). If issues arise, you swap back (rollback is instant). This is the standard zero-downtime deployment pattern.
- **A is wrong** — VNet Integration connects App Service to a virtual network for private resource access. It has nothing to do with deployment strategy.
- **C is wrong** — Scale Out adds more instances to handle load — it's a scaling feature, not a deployment strategy.
- **D is wrong** — Azure CDN caches static content at edge nodes for performance. Not a deployment strategy.

---

## Q53 — Azure App Service Plan SKUs

**You need to use Azure App Service with VNet Integration to access a private database. Which App Service Plan tier is required minimum?**

A. Free (F1)  
B. Shared (D1)  
C. Basic (B1)  
D. Standard (S1)  

**✅ Correct Answer: D**

**Explanation:**
- **D is correct** — **VNet Integration** (allowing outbound connections from App Service to a VNet) requires the **Standard** tier or higher. Basic tier does not support VNet Integration.
- **A is wrong** — Free tier: no custom domains, no TLS, no scaling. Completely unsuitable for production and no VNet Integration.
- **B is wrong** — Shared tier (D1): runs on shared infrastructure, no dedicated instances. No VNet Integration.
- **C is wrong** — Basic tier (B1): dedicated VMs, but no deployment slots and no VNet Integration.

```
  Feature Matrix (App Service Tiers):
  Feature              | Free | Shared | Basic | Standard | Premium
  ─────────────────────┼──────┼────────┼───────┼──────────┼────────
  Custom domain        | ❌   | ✅     | ✅    | ✅       | ✅
  TLS/SSL              | ❌   | ❌     | ✅    | ✅       | ✅
  Deployment slots     | ❌   | ❌     | ❌    | ✅ (5)   | ✅ (20)
  VNet Integration     | ❌   | ❌     | ❌    | ✅       | ✅
  Autoscale            | ❌   | ❌     | ❌    | ✅       | ✅
```

---

## Q54 — Azure Spot VMs

**Your batch processing workload can be interrupted and restarted without data loss. You want to minimize compute costs significantly. What should you use?**

A. Standard reserved VM instances  
B. Azure Spot VMs  
C. Azure Free tier VMs  
D. Azure Burstable VMs (B-series)  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Spot VMs** use Azure's unused capacity at up to **90% discount** compared to pay-as-you-go prices. The trade-off: Azure can evict Spot VMs with 30 seconds notice when capacity is needed. Workloads must be fault-tolerant and restartable. Batch processing that can be interrupted and restarted is the perfect Spot VM workload.
- **A is wrong** — Reserved instances give up to 72% discount but are for committed, stable workloads running continuously. They cannot be interrupted by Azure. Overkill for a batch workload.
- **C is wrong** — Azure Free tier is only for the first 12 months of an Azure account with limited VM sizes (B1s). Not applicable for production batch workloads.
- **D is wrong** — B-series (Burstable) VMs are cost-effective for workloads with variable CPU usage that occasionally burst. They're not designed for fault-tolerant batch computing and don't have the same cost discount level as Spot VMs.

---

## Q55 — Managed Identity in App Service

**An Azure App Service application needs to read secrets from Azure Key Vault. You enable a system-assigned managed identity on the App Service. What additional step is required?**

A. Assign the App Service a public IP address  
B. Grant the managed identity the appropriate Key Vault role (e.g., Key Vault Secrets User)  
C. Create a service principal and store its credentials in App Service settings  
D. Enable VNet Integration between App Service and Key Vault  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Enabling a managed identity creates the identity but doesn't grant it any permissions. You must separately create an **RBAC role assignment**: assign `Key Vault Secrets User` role to the App Service's managed identity on the Key Vault. Without this role assignment, the identity exists but has no access.
- **A is wrong** — Public IP has nothing to do with Key Vault access. Key Vault can be accessed via private endpoint or public endpoint — neither requires the App Service to have a public IP specifically assigned.
- **C is wrong** — Using a service principal with stored credentials defeats the entire purpose of using managed identities (which exist to eliminate credential management). Never do this when a managed identity is available.
- **D is wrong** — VNet Integration is needed if the Key Vault has a private endpoint and firewall restricting public access. But even then, the role assignment step (B) is still required regardless of networking configuration.

---

## Q56 — Azure Virtual Desktop

**Your organization has 500 remote workers who need access to a Windows 10 desktop environment from anywhere. They use lightweight devices. What is the appropriate Azure solution?**

A. Deploy 500 Azure VMs with Windows 10  
B. Azure Virtual Desktop (AVD) with multi-session Windows  
C. Azure App Service web applications  
D. Azure Container Apps with Windows containers  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Virtual Desktop** with **Windows 10/11 Enterprise Multi-session** allows multiple users to share a single VM session host — significantly reducing cost compared to one VM per user. The 500 users connect via a browser or RD client from any device. Licensing is included with Microsoft 365 E3/E5 subscriptions.
- **A is wrong** — 500 individual VMs for 500 users is the maximum cost approach. Each VM runs idle when not in use, and management overhead is enormous.
- **C is wrong** — App Service hosts web applications and APIs, not full Windows desktop environments. Workers need a full desktop experience.
- **D is wrong** — Container Apps with Windows containers don't provide a traditional desktop environment (Windows Explorer, Office applications, etc.).

---

## Q57 — Azure VM Serial Console

**A VM is unresponsive — you cannot RDP or SSH into it. The VM appears to be stuck in a boot loop. What Azure feature can help you diagnose and fix the boot issue without needing network access?**

A. Azure Monitor  
B. Azure Network Watcher  
C. Azure VM Serial Console  
D. Azure Resource Health  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — The **Azure VM Serial Console** provides text-based console access directly to the VM's serial port. Even if the network stack or SSH/RDP daemon is broken, you can access the VM console to view boot messages, log in to a recovery shell, and fix boot configuration. This is the equivalent of plugging in a physical keyboard and monitor to a server.
- **A is wrong** — Azure Monitor collects metrics and logs from running VMs but can't help you interact with a VM that isn't booting properly. You can't "fix" a boot loop through Monitor.
- **B is wrong** — Network Watcher diagnoses networking issues (NSG flow logs, connection troubleshooting, packet capture). It doesn't give console access to a non-responsive VM.
- **D is wrong** — Azure Resource Health reports the health state of the VM from Azure's platform perspective (e.g., "VM is unavailable due to host failure"). It's informational — it doesn't give you console access to fix the issue.

---

## Q58 — VM Disk Caching

**For an Azure VM running a database, which disk caching mode should you set on the data disk that receives many write operations?**

A. Read/Write caching  
B. Read-Only caching  
C. No caching (None)  
D. Write-Back caching  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — For **database data disks** (and any disk with heavy write operations or that uses its own caching layer), you should set disk caching to **None**. Write caching can lead to data corruption if the VM crashes before cached writes are flushed to disk. Database engines (SQL Server, PostgreSQL, MySQL) have their own caching mechanisms and don't need Azure disk caching — it adds risk with no benefit.
- **A is wrong** — Read/Write caching caches both reads and writes in the VM host's cache. While this speeds up I/O, if the VM crashes, unwritten cached data is lost — catastrophic for a database.
- **B is wrong** — Read-Only caching is appropriate for OS disks and data disks with mostly read operations (e.g., static reference data). For write-heavy database workloads, read caching doesn't help writes.
- **D is wrong** — "Write-Back" is not a distinct Azure disk caching mode name. The Azure options are: None, ReadOnly, ReadWrite.

> **Disk caching rules of thumb:**
> - OS disk: ReadWrite (default)
> - Read-heavy data disk: ReadOnly
> - Write-heavy or database data disk: None

---

## Q59 — Azure Spring Apps

**Your team is developing Java Spring Boot microservices. You want a fully managed platform that handles service discovery, configuration management, and autoscaling without managing Kubernetes. What should you use?**

A. AKS with Spring Boot Helm charts  
B. Azure Spring Apps  
C. Azure App Service for Java  
D. Azure Container Apps  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Spring Apps** is a fully managed service specifically for Java Spring Boot and Spring Cloud applications. It provides built-in Eureka service discovery, Spring Cloud Config Server, distributed tracing, and autoscaling — all fully managed. You deploy JAR files; the infrastructure is invisible.
- **A is wrong** — AKS requires managing Kubernetes manifests, networking, and adding Spring-specific operators. More powerful but much higher operational overhead.
- **C is wrong** — Azure App Service for Java runs Spring Boot applications but doesn't provide Spring Cloud features (Eureka, Config Server, Sleuth). You'd need to manage these components separately.
- **D is wrong** — Azure Container Apps is a container-based platform using Dapr and KEDA — good for microservices but not Spring-specific. You'd still need to manage Spring Cloud components.

---

## Q60 — Azure Compute Gallery

**You create a custom VM image with your application pre-installed and security hardened. You want to share this image across multiple subscriptions and Azure regions. What should you use?**

A. Azure Managed Disks snapshot  
B. Azure Compute Gallery (formerly Shared Image Gallery)  
C. Azure Blob Storage with VHD export  
D. Azure Image Builder only  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Compute Gallery** is designed for managing, sharing, and distributing custom VM images at scale. It supports: image versioning, replication across multiple regions, sharing across subscriptions and tenants, and specialized images. This is the enterprise standard for custom image distribution.
- **A is wrong** — A managed disk snapshot is a point-in-time copy of a single disk. It's not designed for cross-subscription or cross-region sharing and doesn't have image versioning or gallery management features.
- **C is wrong** — Exporting to Blob as a VHD works for single-VM image transfer but doesn't provide cross-region replication, versioning, access control across subscriptions, or the metadata/gallery management features.
- **D is wrong** — Azure Image Builder is used to BUILD customized images (installing software, running scripts). The output of Image Builder can be stored in Azure Compute Gallery — but Image Builder alone doesn't handle distribution.

---

# Domain 4 — Implement and Manage Virtual Networking

---

## Q61 ⭐ — Virtual Network CIDR Planning

**You are setting up an Azure Virtual Network for an AKS cluster using Azure CNI networking. The cluster will have 10 nodes with up to 50 pods per node. What minimum subnet size should you use for the node subnet?**

A. /29 (6 usable IPs)  
B. /27 (27 usable IPs)  
C. /24 (251 usable IPs)  
D. /21 (2043 usable IPs)  

**✅ Correct Answer: D**

**Explanation:**
- **D is correct** — With **Azure CNI**, every pod gets an IP address from the VNet subnet (not a separate overlay). 10 nodes × 50 pods = 500 pod IPs + 10 node IPs + 5 reserved Azure IPs + headroom for scaling = 515+ IPs minimum. /24 provides 251 usable IPs which is insufficient. /21 provides 2,046 usable IPs with room for future growth.
- **A is wrong** — /29 gives only 3 usable IPs (Azure reserves 5 from each subnet: .0, .1, .2, .3, .255). Completely inadequate.
- **B is wrong** — /27 gives only 27 usable IPs. Insufficient for even 1 node with multiple pods.
- **C is wrong** — /24 gives 251 usable IPs. With 10 nodes × 50 pods = 500 needed IPs, a /24 is insufficient even without growth headroom.

---

## Q62 ⭐ — NSG Rules

**An NSG is associated with a subnet. The NSG has these rules:**
- `Priority 100: Allow port 443 inbound from Internet`
- `Priority 200: Deny all inbound from Internet`

**A user from the internet tries to access port 80 on a VM in the subnet. What happens?**

A. The request is allowed because port 443 is allowed and HTTP redirects to HTTPS  
B. The request is denied because no rule explicitly allows port 80  
C. The request is allowed by Azure's default rules  
D. The request reaches the VM because the Deny rule doesn't include port 80 specifically  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — NSG rules are evaluated in **priority order** (lowest number first). The first matching rule wins. Port 80 doesn't match rule 100 (which only allows 443). It DOES match rule 200 (which denies ALL inbound from Internet). Therefore, the request is **denied**. The traffic never reaches the VM.
- **A is wrong** — NSGs operate at Layer 4 (TCP port). They don't understand HTTP redirects — they make allow/deny decisions based on the port of the connection, not application-layer behavior.
- **C is wrong** — Azure's default NSG rules allow only VNet-to-VNet, Azure Load Balancer health probes, and deny all other inbound Internet traffic. Port 80 would be denied by Azure defaults even without custom rules.
- **D is wrong** — Rule 200 explicitly states "Deny ALL inbound from Internet" — this covers all ports including 80. There doesn't need to be a port-specific deny rule when the rule says "all."

---

## Q63 — VNet Peering

**VNet-A is peered with VNet-B. VNet-B is peered with VNet-C. Can VMs in VNet-A communicate with VMs in VNet-C?**

A. Yes — peering is transitive, so VNet-A can reach VNet-C through VNet-B  
B. No — VNet peering is non-transitive; VNet-A must be directly peered with VNet-C  
C. Yes — but only if VNet-B has IP forwarding enabled  
D. Yes — but only if all three VNets are in the same region  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **VNet peering is non-transitive** by design. A→B peering and B→C peering does NOT create A→C connectivity. Traffic does not flow through intermediate VNets. To connect VNet-A to VNet-C, you must create a direct peering between A and C, or use Azure Virtual WAN / VPN Gateway with Gateway Transit enabled as a hub-spoke solution.
- **A is wrong** — This is one of the most common VNet peering misconceptions on the AZ-104 exam. Peering is explicitly non-transitive.
- **C is wrong** — IP forwarding on a NIC allows traffic forwarding through a VM (like a network virtual appliance/firewall) but doesn't make VNet peering transitive at the VNet level.
- **D is wrong** — VNet peering can be regional (same region) or global (different regions). The non-transitive limitation applies regardless of region.

---

## Q64 — Azure Load Balancer vs Application Gateway

**You need to distribute HTTPS traffic to multiple backend VMs based on the URL path (`/api/*` goes to API servers, `/images/*` goes to image servers). Which Azure service should you use?**

A. Azure Load Balancer (Standard SKU)  
B. Azure Application Gateway  
C. Azure Traffic Manager  
D. Azure NAT Gateway  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Application Gateway** is a Layer 7 (HTTP/HTTPS) load balancer that understands URL content. It supports **URL path-based routing** (sending `/api/*` to one backend pool and `/images/*` to another), SSL termination, cookie-based session affinity, and WAF (Web Application Firewall). Exactly the scenario described.
- **A is wrong** — Azure Load Balancer operates at Layer 4 (TCP/UDP). It distributes traffic based on IP, port, and protocol only — it cannot inspect URL paths or make routing decisions based on HTTP content.
- **C is wrong** — Azure Traffic Manager is a DNS-based global load balancer. It routes traffic between endpoints in different regions at the DNS level — it cannot do URL path-based routing for traffic arriving at a single endpoint.
- **D is wrong** — NAT Gateway provides outbound internet connectivity for resources in a subnet. It doesn't load balance inbound traffic at all.

---

## Q65 — Azure DNS Private Zones

**An Azure VM needs to resolve a private endpoint for a Key Vault using the hostname `myvault.vault.azure.net` to its private IP address. The Key Vault has a private endpoint configured. What must be in place for name resolution to work?**

A. A custom DNS server that has the mapping hardcoded  
B. A Private DNS zone `privatelink.vaultcore.azure.net` linked to the VM's VNet  
C. A public DNS record in Azure DNS pointing to the private IP  
D. An NSG rule allowing DNS traffic on port 53  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — When a private endpoint is created for Key Vault, Azure creates a DNS alias: `myvault.vault.azure.net` → `myvault.privatelink.vaultcore.azure.net`. For VMs inside the VNet to resolve `myvault.privatelink.vaultcore.azure.net` to the private IP, a **Private DNS Zone** named `privatelink.vaultcore.azure.net` must exist AND be **linked** to the VM's VNet. Without the link, the VM's DNS resolver can't query the private zone.
- **A is wrong** — While a custom DNS server is one approach, it requires additional management. The Private DNS Zone integrated approach is simpler, Azure-native, and the recommended method.
- **C is wrong** — You should never create public DNS records pointing to private IPs — they're unreachable from outside and create security confusion. Private endpoints use private DNS zones.
- **D is wrong** — NSG rules affect network traffic but DNS resolution between VMs and Azure's DNS service (168.63.129.16) is handled by Azure platform networking, not by NSG rules on port 53 that you manage.

---

## Q66 — Azure Bastion

**Your company's security policy prohibits all public IP addresses on VMs and requires all SSH access to go through an audited, browser-based mechanism. What should you deploy?**

A. A VPN Gateway with Point-to-Site (P2S) VPN  
B. A jump box VM with a public IP in a bastion subnet  
C. Azure Bastion  
D. Just-in-time (JIT) VM access via Microsoft Defender for Cloud  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Azure Bastion** provides browser-based SSH/RDP to VMs through the Azure Portal. VMs need NO public IP and no SSH/RDP ports (22/3389) open on NSGs. All sessions are logged in Azure Activity Log (audited). Bastion itself has a public IP but the VMs behind it are fully private. This exactly satisfies the requirements.
- **A is wrong** — P2S VPN connects your laptop to the Azure VNet but doesn't provide the audited browser-based access described. You'd still SSH directly from your machine, and the session isn't audited in Azure.
- **B is wrong** — A traditional jump box VM with a public IP explicitly violates the "no public IPs on VMs" policy. Also, jump boxes require maintenance and don't provide native Azure audit logging.
- **D is wrong** — JIT VM access (Microsoft Defender for Cloud feature) opens specific ports temporarily in NSG rules when requested — it does require network connectivity to reach the VM, and optionally a public IP. It doesn't provide browser-based access.

---

## Q67 — VPN Gateway SKUs

**You are setting up a Site-to-Site VPN between your on-premises network and Azure. The connection must support BGP routing and have a throughput of at least 1 Gbps. Which VPN Gateway SKU supports this?**

A. VpnGw1  
B. VpnGw2  
C. Basic  
D. VpnGw5  

**✅ Correct Answer: B (or higher)**

**Explanation:**
- **B is correct** — VpnGw2 supports up to **1.25 Gbps** throughput and supports **BGP**. It satisfies both requirements: BGP support (≥VpnGw1) and ≥1 Gbps throughput.
- **A (VpnGw1)** — supports BGP but only up to **650 Mbps** throughput. Less than the required 1 Gbps.
- **C (Basic)** — The Basic SKU does NOT support BGP and has very limited throughput (~100 Mbps). Entirely unsuitable.
- **D (VpnGw5)** — VpnGw5 has up to 10 Gbps — overkill but technically satisfies the requirement. VpnGw2 is the minimum that meets both requirements at lower cost.

---

## Q68 — Azure Firewall vs NSG

**What is the key architectural difference between Azure Firewall and Network Security Groups (NSGs)?**

A. NSGs can filter traffic based on FQDN (domain name); Azure Firewall cannot  
B. Azure Firewall is a centralized, managed firewall for the entire VNet; NSGs are distributed rules on subnets/NICs  
C. Azure Firewall is free; NSGs cost per rule  
D. NSGs can inspect Layer 7 (HTTP) traffic; Azure Firewall only handles Layer 4  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **NSGs** are distributed access control lists attached to subnets or NICs — they work at Layer 3/4 (IP address, port, protocol). Multiple NSGs exist independently per resource. **Azure Firewall** is a centralized, stateful managed firewall for the entire virtual network — it inspects all traffic flowing through it, supports FQDNs, threat intelligence, DNAT rules, and application rules (Layer 7 for HTTP/HTTPS FQDNs).
- **A is wrong** — This is exactly backwards. **Azure Firewall** supports FQDN-based rules (allow `*.github.com`). **NSGs** only support IP addresses, port ranges, and service tags — NOT domain names.
- **C is wrong** — Azure Firewall costs ~$900+/month (Standard SKU). NSGs are free — there's no charge for NSG rules. The cost comparison is the opposite of what's stated.
- **D is wrong** — This is also backwards. **Azure Firewall** (with Application rules) handles Layer 7 for HTTP/HTTPS. **NSGs** only work at Layer 3/4.

---

## Q69 — Private Link vs Service Endpoints

**What is the key difference between Azure Private Link/Private Endpoints and VNet Service Endpoints?**

A. Service Endpoints create a private IP for Azure services inside your VNet; Private Endpoints use public IPs with routing optimization  
B. Private Endpoints create a private IP in your VNet for Azure services; Service Endpoints optimize routing but keep the service on its public IP  
C. Service Endpoints are newer and always preferred over Private Endpoints  
D. Both provide identical security and connectivity — the only difference is price  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Private Endpoint** creates a **private IP address inside your VNet** for an Azure service (like Storage, Key Vault, SQL). Traffic to the service flows over the Azure backbone through private networking — the service's public IP is effectively bypassed for your VNet traffic. **Service Endpoints** keep the Azure service on its public IP but **optimize the network path** (traffic stays on Microsoft backbone, not internet), and allow you to restrict the service to only your VNet subnet — but the service's address is still public.
- **A is wrong** — This reverses the definitions. Private Endpoints = private IP in your VNet. Service Endpoints = optimized routing to the public IP.
- **C is wrong** — Service Endpoints are NOT newer or always preferred. Private Endpoints offer stronger isolation and are the recommended approach. Service Endpoints are simpler and cheaper but less secure.
- **D is wrong** — They are NOT identical. Private Endpoints provide true network isolation (only your VNet can reach the resource). Service Endpoints still leave the service on a public IP reachable from elsewhere.

```
  Private Endpoint:
  VM (10.0.1.4) → Private IP (10.0.2.5) → Key Vault
  (the Private IP is inside your VNet — fully private)

  Service Endpoint:
  VM → Microsoft backbone → Key Vault public IP
  (Key Vault still has a public IP, but traffic avoids internet)
```

---

## Q70 — Azure Front Door

**Your web application is deployed in East US and West Europe Azure regions. You want to automatically route users to the closest healthy region with a single global URL and DDoS protection. What should you use?**

A. Azure Traffic Manager + two Application Gateways  
B. Two Azure Load Balancers in each region  
C. Azure Front Door  
D. Azure CDN with origin groups  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Azure Front Door** is a global Layer 7 load balancer with built-in WAF, CDN, and anycast networking. It routes users to the closest healthy origin region automatically (using anycast routing and health probes). It provides a single global domain, built-in DDoS protection, and automatic failover. Exactly the scenario described.
- **A is wrong** — Traffic Manager + Application Gateways can achieve multi-region routing, but Traffic Manager uses DNS-based routing (higher latency than anycast), doesn't include DDoS or CDN, and requires managing two separate Application Gateways. More complex than Front Door.
- **B is wrong** — Azure Load Balancer is regional and Layer 4 only. Two regional load balancers don't provide global routing, health-based failover between regions, or DDoS protection.
- **D is wrong** — Azure CDN is for caching and delivering static content. It doesn't provide global load balancing with health-based origin failover for dynamic application content the same way Front Door does.

---

## Q71 — Network Watcher

**A VM cannot reach a specific external IP address on port 443. Which Azure Network Watcher feature should you use to troubleshoot the connectivity issue?**

A. Connection Monitor  
B. IP flow verify  
C. NSG flow logs  
D. Packet capture  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **IP flow verify** tests whether a specific packet (from source IP:port to destination IP:port with a specific protocol) is allowed or denied by the NSG rules applied to the VM's NIC and subnet. It immediately tells you which NSG rule is allowing or blocking the traffic. Perfect for the scenario: "why can't VM reach X on port 443?"
- **A is wrong** — Connection Monitor continuously monitors connectivity between endpoints over time (useful for tracking latency trends, detecting intermittent outages). It doesn't do instant one-time NSG rule analysis.
- **C is wrong** — NSG flow logs record actual traffic flows (log of what was allowed/denied). They require going through logs after the fact — they don't provide instant "is this packet blocked by NSG?" analysis.
- **D is wrong** — Packet capture records actual network packets for deep inspection. It's useful for complex troubleshooting but is more heavyweight than IP flow verify for a simple NSG rule check.

---

## Q72 — ExpressRoute vs VPN Gateway

**A financial services company needs to connect their on-premises datacenter to Azure with guaranteed bandwidth of 2 Gbps, the lowest possible latency, and a connection that does NOT traverse the public internet. What should they use?**

A. VPN Gateway with ExpressRoute backup  
B. Azure VPN Gateway (RouteBased)  
C. Azure ExpressRoute  
D. Azure VPN Gateway with IKEv2  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **ExpressRoute** is a private, dedicated connection between your datacenter and Azure that goes through a connectivity provider (Equinix, AT&T, etc.) — it does NOT traverse the public internet. It supports up to 100 Gbps circuits, guarantees bandwidth, and provides the lowest latency. Exactly what a financial services compliance requirement specifies.
- **A is wrong** — VPN Gateway with ExpressRoute backup suggests the primary connection is VPN — but VPN goes over the public internet. The requirement explicitly states "does NOT traverse the public internet."
- **B is wrong** — VPN Gateway creates an encrypted tunnel over the public internet (IPsec). Even though traffic is encrypted, it still travels over public internet infrastructure. Doesn't meet the non-internet requirement.
- **D is wrong** — IKEv2 is just the VPN protocol used by the VPN Gateway — it still goes over the public internet.

---

## Q73 — Peering Gateway Transit

**VNet-Hub has a VPN Gateway connecting to on-premises. VNet-Spoke is peered with VNet-Hub. You want VNet-Spoke to use VNet-Hub's VPN Gateway to reach on-premises without deploying a new gateway. What must be configured?**

A. Nothing — peering automatically shares the gateway  
B. Enable "Use Remote Gateway" on the VNet-Spoke peering and "Allow Gateway Transit" on VNet-Hub peering  
C. Deploy a second VPN Gateway in VNet-Spoke  
D. Set up VNet peering with BGP between Spoke and Hub  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — This is called **Gateway Transit** in VNet peering. Two settings are required:
  1. On the **Hub** side of the peering: enable **"Allow Gateway Transit"** (Hub shares its gateway)
  2. On the **Spoke** side of the peering: enable **"Use Remote Gateway"** (Spoke uses Hub's gateway)
  
  Together, these allow the Spoke VNet's traffic to route through the Hub's VPN Gateway to reach on-premises.
- **A is wrong** — Gateway transit is NOT automatic. Both peering configurations must be explicitly enabled. By default, peering does NOT share gateways.
- **C is wrong** — Deploying a second gateway defeats the purpose of hub-spoke architecture. The cost and complexity of maintaining separate gateways per spoke is exactly what gateway transit avoids.
- **D is wrong** — BGP is a routing protocol used within VPN Gateway connections. It doesn't replace the gateway transit peering configuration.

---

## Q74 — Azure NAT Gateway

**Multiple VMs in a subnet need to make outbound internet connections. Azure automatically assigns different outbound public IPs to different VMs, causing issues with IP allowlisting at a third-party service. What should you deploy?**

A. Assign a public IP to each VM  
B. Azure NAT Gateway in the subnet  
C. Azure Load Balancer with outbound rules  
D. Azure Firewall with SNAT rules  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure NAT Gateway** gives all VMs in a subnet a predictable, static set of public IP addresses for outbound internet traffic. The third-party service can allowlist the NAT Gateway's IP(s). NAT Gateway is specifically designed for this scenario: predictable outbound IP for many backend VMs.
- **A is wrong** — Assigning a public IP to each VM creates multiple different outbound IPs — one per VM. The third-party service would need to allowlist all VM IPs, and as VMs scale, more IPs must be managed. Defeats the purpose.
- **C is wrong** — Azure Load Balancer with outbound rules can provide SNAT, but NAT Gateway is simpler, more scalable (no SNAT port exhaustion at scale), and is the recommended replacement for Load Balancer outbound rules.
- **D is wrong** — Azure Firewall with SNAT also provides predictable outbound IPs but costs ~$900+/month and adds complexity with firewall rule management. Overkill when only outbound SNAT is needed.

---

## Q75 — Network Security Group Flow Logs

**You want to capture information about which traffic flows were allowed and denied by NSG rules in your virtual network for security auditing. What should you configure?**

A. Azure Monitor metrics for NSG  
B. NSG flow logs sent to a storage account  
C. Azure Network Watcher packet capture  
D. Azure Monitor diagnostic settings on each NIC  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **NSG flow logs** record every network flow evaluated by an NSG (source/destination IP, port, protocol, direction, action: allow/deny, bytes transferred). They are stored in Azure Blob Storage in JSON format. Azure Traffic Analytics can further analyze the flow logs for visualization and threat detection. This is the standard tool for network auditing.
- **A is wrong** — Azure Monitor NSG metrics give high-level aggregated counts (total allowed/denied packets) — they don't record individual flow details needed for security auditing.
- **C is wrong** — Packet capture records the actual packet payload for deep inspection. It's for troubleshooting specific issues, not continuous security auditing at scale. It captures full packet data (too much detail, high storage cost).
- **D is wrong** — Diagnostic settings on NICs route NIC-level metrics and logs to Monitor/Log Analytics, but NIC diagnostics don't include per-flow NSG decision records the way NSG flow logs do.

---

## Q76 — Azure Load Balancer SKUs

**You need a public Azure Load Balancer that works with Availability Zones and provides an SLA. Which SKU should you choose?**

A. Basic SKU  
B. Standard SKU  
C. Premium SKU  
D. Gateway SKU  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — The **Standard Load Balancer** supports Availability Zones, provides a 99.99% SLA, supports outbound rules, supports backend pools with VMs not in the same availability set, and is zone-redundant. This is the current recommended SKU for production.
- **A is wrong** — The **Basic SKU** does NOT support Availability Zones, does NOT have an SLA, doesn't support mixed backend pools, and has limited feature set. Microsoft recommends migrating from Basic to Standard. Basic will be retired.
- **C is wrong** — There is no "Premium" SKU for Azure Load Balancer. The tiers are Basic, Standard, and Gateway.
- **D is wrong** — The **Gateway SKU** is for integrating with third-party Network Virtual Appliances (NVAs) — it's a bump-in-the-wire deployment for inspection/filtering. Not for general web traffic load balancing.

---

## Q77 — Subnet Reserved IPs

**You create a subnet with the address range `10.0.0.0/28`. How many usable IP addresses are available for VMs?**

A. 16  
B. 14  
C. 11  
D. 8  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — A /28 subnet has 16 total IP addresses (2^(32-28) = 16). Azure **reserves 5 IPs from every subnet**:
  - `10.0.0.0` — Network address
  - `10.0.0.1` — Default gateway (Azure reserves)
  - `10.0.0.2` — Azure DNS mapping
  - `10.0.0.3` — Azure DNS mapping
  - `10.0.0.15` — Broadcast address
  
  16 - 5 = **11 usable IPs** for resources.
- **A is wrong** — 16 is the total IP count before Azure's reservation.
- **B is wrong** — 14 would be the case if only 2 IPs were reserved (standard networking reserves network + broadcast = 2). But Azure reserves 5.
- **D is wrong** — 8 would be from a /29 subnet calculation.

---

## Q78 — Application Security Groups

**You have 20 web VMs, 10 app VMs, and 5 database VMs. You want to allow web VMs to communicate with app VMs on port 8080, and app VMs to communicate with DB VMs on port 5432, without managing IP addresses in NSG rules. What should you use?**

A. Separate NSGs for each tier with hardcoded IP ranges  
B. Application Security Groups (ASGs) for each tier, referenced in NSG rules  
C. Azure Firewall with IP-based rules  
D. VNet peering between each tier  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Application Security Groups (ASGs)** allow you to group VMs by logical role (e.g., `asg-web`, `asg-app`, `asg-db`). NSG rules can reference ASGs as source/destination instead of IP addresses. When a VM's IP changes or new VMs are added, just add them to the ASG — no NSG rule changes needed. This makes rules readable (`from asg-web to asg-app on port 8080`) and maintainable.
- **A is wrong** — Hardcoded IP ranges in NSG rules become a maintenance nightmare as VMs scale, change IPs, or are replaced. You'd need to update NSG rules every time an IP changes.
- **C is wrong** — Azure Firewall is a premium centralized service with significant cost (~$900/month). For internal VNet traffic between application tiers, ASGs in NSGs are the appropriate lightweight solution.
- **D is wrong** — VNet peering connects separate VNets — it's not a tool for controlling traffic between tiers within the same VNet.

---

## Q79 — DNS Resolution in Azure VNet

**What DNS server does an Azure VM use by default when no custom DNS server is configured?**

A. `8.8.8.8` (Google DNS)  
B. `168.63.129.16` (Azure's internal DNS server)  
C. The VM's own localhost DNS resolver  
D. The VNet gateway's DNS service  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — By default, Azure VMs use **Azure-provided DNS** at the virtual IP `168.63.129.16`. This is Azure's internal recursive DNS resolver. It can resolve:
  - Internal Azure hostnames (within the VNet or auto-registered private DNS zones)
  - Public internet DNS (recursively)
  This IP is a virtual platform IP — not routed on the internet — accessible only from within Azure.
- **A is wrong** — Azure VMs don't default to Google's 8.8.8.8. You can configure this as a custom DNS server, but it's not the default.
- **C is wrong** — VMs don't run a local DNS server by default — they forward DNS queries to their configured DNS server (Azure's 168.63.129.16 by default).
- **D is wrong** — The VNet gateway is for VPN/ExpressRoute traffic — it doesn't serve as a DNS server.

---

## Q80 — Traffic Manager

**Users in Asia experience slow performance when accessing your web application hosted only in East US. The application doesn't require synchronized state between regions. What is the simplest solution?**

A. Add more VM instances to the East US deployment  
B. Deploy the application in Southeast Asia and use Azure Traffic Manager with a performance routing policy  
C. Enable Azure CDN on the East US deployment  
D. Increase the App Service Plan SKU size  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Traffic Manager** with **Performance routing** directs each user to the endpoint with the lowest latency from their location. Deploying the application in Southeast Asia and registering both endpoints in Traffic Manager means Asian users are automatically routed to the nearest region, dramatically reducing latency.
- **A is wrong** — Adding more VMs in East US doesn't reduce geographic latency — the physical distance between Asia and East US causes the round-trip delay regardless of how many servers are in East US.
- **C is wrong** — Azure CDN caches static content (images, scripts, CSS) at edge nodes near users. It helps with static content delivery but doesn't help with dynamic application responses that require hitting the origin server. This is a partial solution at best.
- **D is wrong** — Increasing SKU (CPU/RAM) doesn't reduce network latency — it improves server processing speed, not the time data takes to travel across the ocean.

---

## Q81 — Private Endpoint DNS

**What DNS zone name should you use for a Private Endpoint connected to an Azure Storage Blob service?**

A. `privatelink.blob.storage.azure.com`  
B. `privatelink.blob.core.windows.net`  
C. `blob.core.windows.net`  
D. `private.blob.azure.com`  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure's private endpoint DNS zone names follow a standardized pattern for each service. For Blob storage, the private DNS zone name is `privatelink.blob.core.windows.net`. When you create a private endpoint for a storage account `mystorageaccount`, Azure creates the DNS record: `mystorageaccount.blob.core.windows.net` → `mystorageaccount.privatelink.blob.core.windows.net` → private IP.
- **A is wrong** — This is an invented domain and doesn't match Azure's naming convention.
- **C is wrong** — `blob.core.windows.net` is the public DNS zone — not the private DNS zone for private endpoints.
- **D is wrong** — This domain doesn't exist in Azure's private endpoint naming scheme.

> **Common private DNS zone names to memorize:**
> - Key Vault: `privatelink.vaultcore.azure.net`
> - Blob Storage: `privatelink.blob.core.windows.net`
> - Azure SQL: `privatelink.database.windows.net`
> - ACR: `privatelink.azurecr.io`

---

## Q82 — Virtual WAN

**Your company has 20 branch offices and 3 Azure regions that all need to communicate with each other and with a central hub. Managing individual VPN connections and VNet peerings is becoming unmanageable. What Azure service simplifies this?**

A. Multiple VPN Gateways with BGP mesh  
B. Azure Virtual WAN (vWAN)  
C. ExpressRoute for each branch  
D. VNet peering between all VNets and branches  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Virtual WAN** provides a managed hub-and-spoke networking architecture at global scale. Branches connect to Virtual WAN hubs (S2S VPN or ExpressRoute), VNets peer to the hub, and Azure handles all routing automatically. 20 branches × 3 regions = 60 manual connections without vWAN; with vWAN, each branch connects to the nearest hub and gets full connectivity to everything automatically.
- **A is wrong** — Multiple VPN Gateways with BGP mesh scales poorly. Managing BGP peers, route tables, and individual connections for 20 branches + 3 regions manually is exactly the problem.
- **C is wrong** — ExpressRoute for each of 20 branch offices is prohibitively expensive (each circuit costs $200–10,000/month). Also doesn't solve the mesh routing problem.
- **D is wrong** — VNet peering is non-transitive — you'd need to peer each VNet with every other VNet (n*(n-1)/2 peerings) AND manage branch VPN connections separately. This doesn't scale.

---

# Domain 5 — Monitor and Maintain Azure Resources

---

## Q83 ⭐ — Azure Monitor

**You want to visualize CPU usage, memory, and disk I/O metrics for your Azure VMs on a single dashboard with custom charts. What Azure tool should you use?**

A. Azure Service Health  
B. Azure Advisor  
C. Azure Monitor Workbooks  
D. Azure Resource Health  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Azure Monitor Workbooks** (formerly Azure Workbooks) provides interactive, customizable reports and dashboards. You can combine metrics from multiple Azure resources (VMs, databases, networking) into a single visualization with charts, graphs, text, and parameter controls. This is the tool for custom metric dashboards.
- **A is wrong** — Azure Service Health reports on Azure platform incidents, planned maintenance, and service advisories across regions and services. Not for VM performance metrics.
- **B is wrong** — Azure Advisor provides cost, performance, security, reliability, and operational excellence recommendations. It's a recommendation engine, not a metrics dashboard.
- **D is wrong** — Azure Resource Health shows the health state of specific Azure resources (Is this VM running? Was there a host failure?). It's informational about resource availability, not a metric visualization tool.

---

## Q84 — Log Analytics Queries

**You want to query Azure VM log data to find all authentication failures in the last 24 hours. Where do you write and run this query?**

A. Azure Monitor Metrics Explorer  
B. Azure Log Analytics workspace using KQL (Kusto Query Language)  
C. Azure Resource Graph Explorer  
D. Azure Monitor Alerts  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Log Analytics** workspace collects log data from Azure resources (VM agents, diagnostic settings, Azure AD sign-in logs). You query this data using **KQL (Kusto Query Language)**. Example: `SecurityEvent | where EventID == 4625 | where TimeGenerated > ago(24h)` finds failed logon events (event 4625) in the last 24 hours.
- **A is wrong** — Azure Monitor Metrics Explorer visualizes numerical metrics (CPU%, disk IOPS, network bytes). Authentication log events are log data, not metrics — they go to Log Analytics, not Metrics.
- **C is wrong** — Azure Resource Graph Explorer queries Azure resource properties (resource types, tags, configurations) across subscriptions. It queries the Azure Resource Manager's inventory, not log data from within VMs.
- **D is wrong** — Azure Monitor Alerts USE queries (KQL) to detect conditions and trigger notifications. But you write and run queries in Log Analytics directly — Alerts is the alerting layer on top.

---

## Q85 — Azure Advisor

**Azure Advisor makes a recommendation that you have a VM running for 90 days with average CPU usage below 5%. What type of recommendation is this and what action should you take?**

A. Security recommendation — enable encryption on the VM  
B. Cost recommendation — rightsize or shut down the underutilized VM  
C. Performance recommendation — upgrade the VM to a higher tier  
D. Reliability recommendation — add a second VM to the availability set  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure Advisor analyzes telemetry and identifies underutilized resources. A VM running 90 days at <5% CPU is a **cost** waste. Advisor recommends rightsizing (moving to a smaller VM size) or shutting down the VM. Azure Advisor's 5 pillars are: Cost, Performance, Security, Reliability, Operational Excellence.
- **A is wrong** — Security recommendations address vulnerabilities: missing patches, open ports, weak passwords, missing encryption. Low CPU utilization is not a security issue.
- **C is wrong** — Performance recommendations suggest upgrades when resources are being throttled or experiencing degraded performance. A VM with 5% CPU is the opposite — it's over-provisioned, not under-provisioned.
- **D is wrong** — Reliability recommendations address risks to availability: single-instance VMs without availability sets, lack of backups, etc. Underutilization is not a reliability concern.

---

## Q86 — Azure Monitor Alerts

**You want to receive a Slack notification whenever a VM's CPU usage exceeds 80% for more than 5 minutes. What is the sequence of components needed?**

A. Azure Monitor → Action Group → Slack webhook  
B. Log Analytics → Alert Rule → Email  
C. Azure Service Health → Notification → Slack  
D. Azure Advisor → Recommendation → Slack  

**✅ Correct Answer: A**

**Explanation:**
- **A is correct** — The sequence is:
  1. **Azure Monitor** collects the CPU metric
  2. **Alert Rule** evaluates: CPU > 80% for 5 minutes
  3. When triggered, the alert fires on an **Action Group**
  4. The **Action Group** contains a webhook action pointing to Slack's incoming webhook URL
  
  Action Groups support: email, SMS, voice call, Azure mobile app, webhooks (for Slack, Teams, PagerDuty), Logic Apps, Automation Runbooks, and ITSM tools.
- **B is wrong** — The sequence includes Log Analytics (used for log-based alerts, not metric alerts), and email instead of Slack. But fundamentally, metric alerts use Azure Monitor, not Log Analytics directly.
- **C is wrong** — Azure Service Health alerts notify about Azure platform events (outages, maintenance). Not appropriate for VM metric threshold alerting.
- **D is wrong** — Azure Advisor doesn't support real-time alerting on metrics. It provides periodic (daily) recommendations, not threshold-based real-time alerts.

---

## Q87 — Azure Backup

**You need to protect an Azure VM from accidental deletion and enable point-in-time restore for up to 30 days. What should you configure?**

A. Azure VM snapshots  
B. Azure Backup with a Recovery Services vault and a 30-day retention policy  
C. Azure Site Recovery  
D. Azure managed disk replication  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Backup** with a **Recovery Services vault** provides scheduled, application-consistent VM backups with configurable retention (up to 30 days in standard policies). If a VM is accidentally deleted or corrupted, you can restore it to any recovery point within the retention period. This is the purpose-built backup solution for Azure VMs.
- **A is wrong** — VM snapshots (managed disk snapshots) are point-in-time copies of individual disks. They don't provide the scheduled backup management, centralized vault, application-consistent backup (VSS on Windows), or restore orchestration that Azure Backup provides. Manual snapshots are a supplementary tool, not a backup strategy.
- **C is wrong** — Azure Site Recovery is a **disaster recovery** service — it replicates VMs to another region for failover in case of regional outage. It provides continuous replication, not point-in-time restore of specific files or application data. DR ≠ Backup.
- **D is wrong** — Managed disk replication refers to disk-level redundancy (LRS/ZRS/GRS) for availability. It doesn't protect against accidental deletion or logical corruption — replicas mirror the production state, including any accidental deletion.

---

## Q88 — Azure Site Recovery

**Your company needs to ensure that if the entire East US Azure region becomes unavailable, your critical VMs can fail over to West US within 1 hour (RTO < 1 hour). What should you configure?**

A. Azure Backup with geo-redundant storage  
B. Azure Site Recovery (ASR) with continuous replication to West US  
C. Manual VM deployment scripts in West US  
D. ZRS (Zone-Redundant Storage) for VM disks  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Site Recovery** continuously replicates VMs from a primary region to a secondary region. In a disaster, you execute a **Failover** in ASR — VMs start in West US in minutes (or up to 1 hour for large workloads). ASR specifically addresses the RTO (Recovery Time Objective) requirement with pre-staged replicated VMs in the secondary region.
- **A is wrong** — Azure Backup with GRS stores backups in a secondary region, but restoring VMs from backup takes much longer than 1 hour (you're rebuilding the VM from scratch from backup data). GRS Backup doesn't guarantee RTO < 1 hour.
- **C is wrong** — Manual deployment scripts require someone to trigger them, wait for VM provisioning (10-20+ minutes), configure networking, restore data — this could take many hours, not < 1 hour.
- **D is wrong** — ZRS replicates disk data across zones WITHIN the same region. If the entire East US region fails, ZRS doesn't help — all zones are in East US. ZRS protects against datacenter failure, not regional failure.

---

## Q89 — Azure Monitor — Diagnostic Settings

**You want to send Azure Key Vault audit logs (who accessed which secrets) to a Log Analytics workspace for long-term retention and querying. What should you configure?**

A. Azure Security Center recommendations  
B. Diagnostic Settings on the Key Vault resource  
C. Key Vault access policies to allow Log Analytics  
D. Azure Monitor metrics collection on Key Vault  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Diagnostic Settings** on the Key Vault enables routing of Key Vault audit logs (resource logs) to a Log Analytics workspace, Storage Account, or Event Hub. The log category `AuditEvent` records every operation on the vault — who read a secret, who updated a key, etc. Once in Log Analytics, you can query with KQL: `AzureDiagnostics | where ResourceType == "VAULTS" | where OperationName == "SecretGet"`.
- **A is wrong** — Azure Security Center (Defender for Cloud) provides security recommendations and threat alerts — it doesn't send vault audit logs to Log Analytics for querying.
- **C is wrong** — Key Vault access policies control WHICH identities can perform WHICH operations on the vault. They don't configure log routing destinations.
- **D is wrong** — Azure Monitor metrics for Key Vault include numerical counts (API hits, availability percentage) — these are aggregated numbers, not individual audit trail records of who accessed what.

---

## Q90 — Azure Policy — Compliance Evaluation

**You assign a new Azure Policy to check that all VMs have disk encryption enabled. How can you see which existing VMs are not compliant?**

A. Azure Security Center — Recommendations blade  
B. Azure Policy — Compliance blade  
C. Azure Monitor — Alert History  
D. Azure Advisor — Security Recommendations  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — The **Azure Policy Compliance** blade shows the compliance state of all resources in scope: which are compliant, which are non-compliant, and the percentage overall. It evaluates existing resources and shows you exactly which VMs fail the disk encryption requirement.
- **A is wrong** — Security Center/Defender for Cloud also surfaces encryption recommendations, but the authoritative policy compliance view is the Azure Policy Compliance blade — this is what directly reflects your policy assignment's evaluation.
- **C is wrong** — Azure Monitor Alert History shows fired alerts (metric thresholds exceeded, log search matches). Policy compliance state is not an alert — it's a compliance evaluation.
- **D is wrong** — Azure Advisor Security recommendations can overlap with policy recommendations but are proactive suggestions, not a direct view of your specific assigned policy's compliance state.

---

## Q91 — Azure Cost Management

**You notice your Azure monthly bill has unexpectedly increased by 40%. Which tool should you use FIRST to identify the cause?**

A. Azure Advisor  
B. Azure Cost Analysis in Microsoft Cost Management  
C. Azure Monitor Metrics  
D. Azure Resource Health  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Cost Analysis** (in Microsoft Cost Management + Billing) lets you analyze spending by resource type, resource group, subscription, tags, and time period. You can compare current month to previous month, drill down into which resources have increased cost, and see exactly what changed. This is the primary tool for cost investigation.
- **A is wrong** — Azure Advisor provides optimization recommendations (including cost savings opportunities) but doesn't provide the granular cost breakdown needed to identify what specifically increased by 40%.
- **C is wrong** — Azure Monitor Metrics shows resource performance metrics (CPU, network, storage IOPS). It doesn't show billing or cost data.
- **D is wrong** — Azure Resource Health shows whether resources are healthy or impaired (platform issues). It has no cost information.

---

## Q92 — Azure Service Health

**Azure sends a notification that there will be a planned maintenance event in East US on Saturday that will affect your VMs. Where can you find more details and configure alerts for future events?**

A. Azure Monitor → VM metrics  
B. Azure Service Health → Health Advisories and Planned Maintenance  
C. Azure Advisor → Reliability Recommendations  
D. Microsoft Azure Status page at status.azure.com  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Service Health** provides personalized health information for your specific resources and subscriptions. It shows:
  - **Service Issues:** Active outages affecting Azure services
  - **Planned Maintenance:** Upcoming maintenance that may affect your resources
  - **Health Advisories:** Changes requiring action (deprecations, etc.)
  
  You can also configure Azure Service Health Alerts to be notified via Action Groups (email, SMS) about future events for specific services/regions.
- **A is wrong** — Azure Monitor metrics show resource performance data. Planned maintenance information comes from Azure's service health data, not VM metrics.
- **C is wrong** — Azure Advisor reliability recommendations suggest architecture improvements (add availability sets, configure backups). It doesn't show planned maintenance notifications.
- **D is wrong** — `status.azure.com` (the public Azure Status page) shows global Azure incidents visible to all customers. It doesn't show personalized maintenance notifications for YOUR resources or allow alert configuration. Azure Service Health is the personalized version.

---

## Q93 — Azure Resource Graph

**You manage 15 Azure subscriptions and need to find all virtual machines across ALL subscriptions that are running and have more than 4 vCPUs. How should you query this?**

A. Azure Monitor — run a Log Analytics query across all workspaces  
B. Azure Resource Graph Explorer using KQL  
C. Azure Policy Compliance view  
D. Run `az vm list` per subscription in a script  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Resource Graph** is specifically designed for querying resource properties across multiple subscriptions at scale. Using KQL in Resource Graph Explorer: `Resources | where type =~ 'microsoft.compute/virtualmachines' | where properties.hardwareProfile.vmSize has 'Standard' | where properties.extended.instanceView.powerState.code == 'PowerState/running'`. Resource Graph queries are fast (sub-second for millions of resources) because it maintains an index of all ARM resource properties.
- **A is wrong** — Log Analytics workspaces contain operational data (performance logs, event logs) sent from resource agents. Resource configuration data (VM size, running state) is in ARM / Resource Graph, not Log Analytics.
- **C is wrong** — Azure Policy Compliance shows compliance results for specific policy definitions. It doesn't support ad-hoc queries for resource properties like vCPU count across subscriptions.
- **D is wrong** — Running `az vm list` per subscription works but requires scripting a loop, handling authentication per subscription, and performance is poor for 15 subscriptions. Resource Graph handles all subscriptions in a single query.

---

## Q94 — Managed Disk Backup

**Which Azure Backup feature allows you to create an application-consistent backup of an Azure SQL Server installed on a VM?**

A. Azure VM snapshot (crash-consistent)  
B. Azure Backup for VMs with workload-aware (VSS) application-consistent backup  
C. Azure SQL Database automated backups  
D. Azure Managed Disk snapshots  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — Azure Backup for VMs (on Windows) uses the **Volume Shadow Copy Service (VSS)** to create **application-consistent** backups. VSS coordinates with SQL Server's VSS writer to flush all in-memory data to disk and pause writes during backup, ensuring the database is in a consistent state when captured. The result can be restored without any database recovery needed.
- **A is wrong** — Crash-consistent snapshots capture the disk state at a point in time without coordinating with SQL Server. SQL Server may have in-flight transactions in memory not yet written to disk. The restore may require crash recovery — like after a power failure. For SQL Server, this is usually fine for recovery but "crash-consistent" is not the same as "application-consistent."
- **C is wrong** — Azure SQL Database automated backups apply to the Azure SQL Database PaaS service (fully managed), not SQL Server installed on a VM. A VM-hosted SQL Server requires Azure Backup or SQL Server native backups.
- **D is wrong** — Managed Disk snapshots are crash-consistent (same issue as option A). They don't coordinate with SQL Server's VSS writer.

---

## Q95 — Azure Monitor Alerts — Types

**You want to create an alert that fires when more than 100 failed login attempts (Event ID 4625) are detected in your Log Analytics workspace within a 15-minute window. What type of alert rule should you create?**

A. Metric alert  
B. Log alert (log search alert)  
C. Activity log alert  
D. Smart detection alert  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — A **log alert** (or log search alert) runs a KQL query against a Log Analytics workspace on a schedule and fires if the query returns more than N results or meets a threshold. Example: `SecurityEvent | where EventID == 4625 | where TimeGenerated > ago(15m) | count` — if count > 100, alert fires. This is exactly the right alert type for log-based thresholds.
- **A is wrong** — Metric alerts monitor numerical time-series metrics (CPU%, network bytes, HTTP request rate). "Number of failed logins" is an event count from log data, not a numeric metric from Azure Monitor's metrics pipeline.
- **C is wrong** — Activity log alerts fire on specific operations recorded in the Azure Activity Log — like "VM deleted" or "RBAC role assigned." They're for Azure management plane events, not OS-level security event logs.
- **D is wrong** — Smart detection alerts are part of Application Insights and automatically detect anomalies in application performance (request failure rate changes, performance degradation). Not applicable to Windows security event logs.

---

## Q96 — Azure Backup MARS Agent

**You have an on-premises Windows server that you want to back up to Azure without deploying a backup server in Azure. The backup should protect individual files and folders. What should you use?**

A. Azure Site Recovery  
B. Azure Backup with MARS (Microsoft Azure Recovery Services) Agent  
C. Azure Backup Server (MABS)  
D. AzCopy to copy files to Azure Blob Storage  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — The **MARS Agent** is a lightweight agent you install directly on a Windows server (physical or VM). It backs up files, folders, and the Windows System State directly to an Azure Recovery Services vault. No additional infrastructure in Azure is needed. Simple, direct, cost-effective for file-level backup.
- **A is wrong** — Azure Site Recovery is for disaster recovery (VM replication for regional failover). It's not designed for file/folder backup and doesn't protect individual files — it's a whole-VM replication service.
- **C is wrong** — Azure Backup Server (MABS) is the heavy-duty on-premises backup server that protects workloads like Hyper-V VMs, SharePoint, Exchange, SQL at scale — and backs up to Azure. MABS requires a separate dedicated server. Overkill for simple file backup of one server.
- **D is wrong** — AzCopy copies files to Azure Blob Storage but provides no backup features: no scheduling, no versioning management, no centralized management, no recovery catalog, no encryption handling — it's just a file copy tool.

---

## Q97 — Azure Resource Tags for Cost Allocation

**Your finance team needs to see Azure costs split by project (Project-A and Project-B). What is the most effective way to enable this reporting?**

A. Create separate subscriptions for each project  
B. Create separate resource groups for each project  
C. Apply a `Project` tag to all resources and use Azure Cost Management tag filtering  
D. Use Azure Management Groups to separate projects  

**✅ Correct Answer: C**

**Explanation:**
- **C is correct** — **Resource tags** are the standard mechanism for cost allocation and chargeback in Azure. Tag every resource with `Project: Project-A` or `Project: Project-B`. In Azure Cost Management + Billing, you can filter and group costs by tag value — showing exactly how much each project costs. This works even if both projects share the same subscription and resource groups.
- **A is wrong** — Separate subscriptions is a heavy-handed approach with high management overhead (separate billing, RBAC management, networking configuration). It works for billing separation but is overkill when tagging achieves the same result with less complexity.
- **B is wrong** — Separate resource groups help organize resources but Cost Management can also filter by resource group already. However, resource groups don't force cost separation if both groups are in the same subscription — tags are the more flexible approach.
- **D is wrong** — Management Groups organize subscriptions into a hierarchy. They enable policy and RBAC inheritance across subscriptions but don't directly tag resources or enable project-level cost filtering within a subscription.

---

## Q98 — Action Groups

**An alert fires in Azure Monitor. The action group for this alert is configured to send an email AND trigger an Azure Logic App. The Logic App creates a Jira ticket. The email notification is received but the Logic App is NOT triggered. What should you check first?**

A. Whether the alert rule severity is set high enough  
B. Whether the Logic App has a public endpoint and the Action Group has permission to invoke it  
C. Whether Log Analytics is connected to the Logic App  
D. Whether the VM being monitored is running  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — For an Action Group to trigger a Logic App (via webhook), the Logic App must:
  1. Have an HTTP trigger with a publicly accessible endpoint
  2. The Action Group must be able to reach that endpoint (no firewall blocking)
  3. The endpoint URL must be correctly configured in the Action Group
  Since email works but Logic App doesn't, the alert firing is not the issue — the Logic App invocation itself is failing, which most commonly means a misconfigured endpoint URL or the Logic App endpoint is unreachable.
- **A is wrong** — Alert severity affects routing priority but not which actions execute. All configured actions in an Action Group execute regardless of severity level.
- **C is wrong** — Logic Apps and Log Analytics are separate services. Log Analytics provides data to alerts; Action Groups trigger Logic Apps. There's no direct "connection" requirement between them.
- **D is wrong** — The VM being monitored doesn't affect the Action Group's ability to trigger a Logic App. If the email action succeeded, the Action Group itself is working — the specific Logic App action is failing.

---

## Q99 — Azure Automanage

**You have 50 Azure VMs and want to automatically configure best practices: backup, monitoring, patch management, and antimalware — without manual configuration per VM. What should you enable?**

A. Azure Policy with a custom initiative  
B. Azure Automanage for VMs  
C. Azure Security Center recommendations  
D. ARM template with DSC extension  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Automanage** is a service that automatically applies and manages Azure best practices for VMs. When you enroll a VM, Automanage sets up: Azure Backup, Log Analytics agent, Azure Monitor, Update Management, Microsoft Antimalware, Change Tracking, and Azure Security Center — all following Microsoft's best practice configurations. No manual per-service configuration required.
- **A is wrong** — A custom Azure Policy initiative can enforce settings but doesn't automatically configure services. Policy can deny non-compliant resources but can't actively set up backup policies, monitoring agents, and antimalware settings.
- **C is wrong** — Defender for Cloud/Security Center provides recommendations (suggestions) but doesn't automatically implement them without your manual action per recommendation.
- **D is wrong** — ARM templates with DSC can configure VMs but require you to build and maintain all the configurations. Automanage is the managed service that handles all this without custom template development.

---

## Q100 ⭐ — Azure Update Management

**You need to centrally view and deploy OS security patches across 100 Azure VMs and 20 on-premises servers. What Azure solution provides this?**

A. Azure Backup  
B. Azure Update Manager (formerly Update Management in Azure Automation)  
C. Microsoft Endpoint Configuration Manager (MECM/SCCM) only  
D. Windows Server Update Services (WSUS) only  

**✅ Correct Answer: B**

**Explanation:**
- **B is correct** — **Azure Update Manager** provides centralized patch management for Azure VMs, Azure Arc-enabled servers (on-premises, other clouds), and Windows/Linux systems. It shows compliance state (which machines are missing which patches), schedules maintenance windows, and deploys patches at scale. It works both for Azure VMs AND on-premises servers (via Azure Arc).
- **A is wrong** — Azure Backup protects data from accidental deletion and disasters. It has no patch management capabilities.
- **C is wrong** — MECM (SCCM) is an on-premises Microsoft tool for device management including patching. It doesn't natively manage Azure VMs without additional configuration (co-management). Azure Update Manager is the cloud-native solution.
- **D is wrong** — WSUS is an on-premises Windows Server role for distributing Windows updates. It manages Windows updates for on-premises machines but doesn't extend to Azure VMs natively or provide the centralized cloud management view that Azure Update Manager offers.

---

# 📋 Quick Reference — Key Exam Facts to Memorize

```
  RBAC:
  ├── Owner = everything + assign roles
  ├── Contributor = create/manage, CANNOT assign roles
  ├── Reader = view only
  └── Role assignments inherit DOWNWARD in scope hierarchy

  STORAGE:
  ├── LRS = 3 copies in one datacenter
  ├── ZRS = 3 copies across 3 zones (same region)
  ├── GRS = LRS + async copy to secondary region
  ├── GZRS = ZRS + copy to secondary region (highest)
  ├── Storage account names: 3-24 chars, lowercase+digits, NO hyphens
  └── Azure reserves 5 IPs per subnet (.0, .1, .2, .3, .255)

  VMs:
  ├── Deallocated = no compute charge  ✅
  ├── Stopped (OS) = still charged  ❌
  ├── Availability Set = 99.95% SLA (same datacenter)
  ├── Availability Zones = 99.99% SLA (different datacenters)
  └── Ultra Disk = max IOPS (160,000), sub-ms latency

  NETWORKING:
  ├── VNet peering is NON-TRANSITIVE
  ├── NSG: lower priority number = processed FIRST
  ├── App Gateway = Layer 7 (URL routing, WAF, SSL offload)
  ├── Load Balancer = Layer 4 (TCP/UDP only)
  ├── Traffic Manager = DNS-based global routing
  ├── Front Door = anycast Layer 7 global routing + CDN + WAF
  ├── Private Endpoint = private IP IN your VNet for PaaS services
  └── Service Endpoint = optimized routing to public IP

  KEY VAULT DATA PLANE ROLES:
  ├── Key Vault Administrator = full CRUD on secrets/keys/certs
  ├── Key Vault Secrets Officer = CRUD secrets only
  ├── Key Vault Secrets User = READ secrets only (pipelines)
  └── Key Vault Reader = see vault metadata, NOT secret values

  MONITORING:
  ├── Metrics = numerical time-series (CPU%, bytes) → Metric alerts
  ├── Logs = events, audit, text → Log alerts (KQL)
  ├── Activity Log = Azure management operations (create/delete VM)
  ├── Azure Backup = point-in-time restore (up to 99 years)
  ├── Azure Site Recovery = regional DR failover
  └── Azure Automanage = auto-configure VM best practices
```

---

*Source: AZ-104 Exam Skills Measured (2024–2026) · [Azure Handbook](azure_handbook.md) · [Azure Services Handbook](../azure-services/azure_services_handbook.md)*
