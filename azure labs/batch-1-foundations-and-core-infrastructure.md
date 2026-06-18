# 🔷 Batch 1: Foundations & Core Infrastructure

> **Level:** Beginner | **Estimated Total Time:** 10–15 days | **Scenarios:** 5
>
> This is where your Azure journey begins. These five scenarios build the foundational skills every cloud engineer needs — from organizing resources and understanding compute, to mastering networking, storage, and platform-as-a-service deployments. Complete them in order; each one builds on the previous.

---

## 📑 Table of Contents

- [Scenario 1: Subscription & Resource Group Strategy](#scenario-1-subscription--resource-group-strategy)
- [Scenario 2: Virtual Machine Deep Dive](#scenario-2-virtual-machine-deep-dive)
- [Scenario 3: Azure Networking Fundamentals](#scenario-3-azure-networking-fundamentals)
- [Scenario 4: Azure Storage Deep Dive](#scenario-4-azure-storage-deep-dive)
- [Scenario 5: Azure App Service Fundamentals](#scenario-5-azure-app-service-fundamentals)

---

## Scenario 1: Subscription & Resource Group Strategy

### 🎯 Objective

Learn how Azure organizes resources hierarchically — from Management Groups down to individual resources. Master RBAC, tagging, policies, locks, and cost management. This is the governance foundation everything else sits on.

### 📦 App Description

**A simple multi-page portfolio website (HTML/CSS/JS)** — a static site with 3–5 pages (Home, About, Projects, Contact). You'll deploy this trivial app in multiple ways across different resource groups to practice organizational patterns without worrying about app complexity.

### 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                   MANAGEMENT GROUP                       │
│                  "mg-training-root"                       │
│                                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐       │
│  │   SUBSCRIPTION      │  │   SUBSCRIPTION       │       │
│  │   "sub-dev"         │  │   "sub-prod"         │       │
│  │                     │  │                      │       │
│  │  ┌──────────────┐   │  │  ┌──────────────┐   │       │
│  │  │ RG: rg-dev-  │   │  │  │ RG: rg-prod- │   │       │
│  │  │ portfolio-   │   │  │  │ portfolio-   │   │       │
│  │  │ eastus       │   │  │  │ eastus       │   │       │
│  │  │              │   │  │  │              │   │       │
│  │  │ • App Svc    │   │  │  │ • App Svc    │   │       │
│  │  │ • Storage    │   │  │  │ • Storage    │   │       │
│  │  │   (static)   │   │  │  │   (static)   │   │       │
│  │  └──────────────┘   │  │  └──────────────┘   │       │
│  │                     │  │                      │       │
│  │  TAGS:              │  │  TAGS:               │       │
│  │   env=dev           │  │   env=prod            │       │
│  │   project=portfolio │  │   project=portfolio   │       │
│  │   cost-center=IT    │  │   cost-center=IT      │       │
│  └─────────────────────┘  └─────────────────────┘       │
│                                                          │
│  AZURE POLICY (inherited):                               │
│   • Require "env" tag on all RGs                         │
│   • Allowed locations: eastus, westus2                   │
│   • Deny public IP on VMs                                │
└──────────────────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Azure account with at least one subscription (free tier works)
- Azure CLI installed (`az --version`)
- VS Code with Azure extensions
- Basic understanding of cloud concepts

### ✅ Hands-on Tasks

#### Part A: Management Groups & Subscriptions

- [ ] Create a Management Group hierarchy: Root → Department (e.g., "IT-Training") → Environment (Dev, Prod)
- [ ] Move your subscription under the correct Management Group
- [ ] Verify inheritance by checking effective policies at subscription level

```bash
# Create management group
az account management-group create --name "mg-training-root" --display-name "Training Root"
az account management-group create --name "mg-training-dev" --display-name "Development" --parent "mg-training-root"

# Move subscription under management group
az account management-group subscription add --name "mg-training-dev" --subscription <sub-id>
```

> ⚠️ **DevOps Gotcha:** Management Group changes can take up to **15 minutes** to propagate. If you assign a policy at the MG level and immediately check compliance at the subscription level, it may show as "Not started." Don't panic — wait and re-check.

#### Part B: Resource Groups & Naming Conventions

- [ ] Design a naming convention: `<resource-type>-<workload>-<environment>-<region>-<instance>`
- [ ] Create resource groups following your convention:
  - `rg-portfolio-dev-eastus`
  - `rg-portfolio-prod-eastus`
  - `rg-shared-dev-eastus` (for shared resources like Key Vault)
- [ ] Document your naming convention in a markdown file

```bash
az group create --name "rg-portfolio-dev-eastus" --location "eastus" \
  --tags env=dev project=portfolio cost-center=IT owner=yourname
```

#### Part C: Tagging Strategy

- [ ] Define mandatory tags: `env`, `project`, `cost-center`, `owner`, `created-date`
- [ ] Apply tags to all resource groups
- [ ] Create a tag policy to enforce mandatory tags (Deny effect)
- [ ] Test the policy: try creating an RG without required tags — watch it get denied
- [ ] Query resources by tags using Azure Resource Graph

```bash
# Query all resources with a specific tag
az graph query -q "Resources | where tags.env == 'dev' | project name, type, resourceGroup"
```

> ⚠️ **DevOps Gotcha:** Tags are NOT inherited by child resources by default! If you tag a resource group, the resources inside it don't automatically get those tags. Use Azure Policy with the "Modify" effect to auto-inherit tags, or use `az tag` with `--operation merge`.

#### Part D: Resource Locks

- [ ] Apply a `CanNotDelete` lock on the production resource group
- [ ] Apply a `ReadOnly` lock on a storage account
- [ ] Try to delete the locked RG — observe the error
- [ ] Try to modify the read-only storage account — observe what fails
- [ ] Remove the lock and verify you can now delete

```bash
# Create a CanNotDelete lock
az lock create --name "prevent-delete" --resource-group "rg-portfolio-prod-eastus" --lock-type CanNotDelete

# Create a ReadOnly lock
az lock create --name "read-only" --resource-group "rg-portfolio-prod-eastus" --lock-type ReadOnly
```

> ⚠️ **DevOps Gotcha:** `ReadOnly` locks are surprisingly restrictive! They prevent ANY modification, including things like scaling an App Service Plan or rotating storage keys. Even **listing storage account keys** fails under ReadOnly because the `listKeys` operation is a POST, not a GET. This catches everyone off guard.

#### Part E: RBAC (Role-Based Access Control)

- [ ] Assign "Reader" role to a test user at the subscription scope
- [ ] Assign "Contributor" role at the resource group scope
- [ ] Create a custom RBAC role that allows only App Service management
- [ ] Verify role inheritance: a Reader at subscription level is also a Reader at RG level
- [ ] Check effective permissions using `az role assignment list`
- [ ] Understand the difference between Azure RBAC roles and Azure AD directory roles

```bash
# Assign a built-in role
az role assignment create --assignee user@domain.com --role "Reader" --scope /subscriptions/<sub-id>

# Create custom role
az role definition create --role-definition '{
  "Name": "App Service Operator",
  "Description": "Can manage App Services but nothing else",
  "Actions": [
    "Microsoft.Web/sites/*",
    "Microsoft.Web/serverFarms/*"
  ],
  "NotActions": [],
  "AssignableScopes": ["/subscriptions/<sub-id>"]
}'
```

#### Part F: Azure Policy

- [ ] Assign the built-in policy "Require a tag and its value on resources"
- [ ] Create a custom policy: "Allowed VM SKUs" — restrict to B-series only
- [ ] Assign a policy with "Audit" effect first, then change to "Deny"
- [ ] Create a policy initiative (policy set) combining multiple policies
- [ ] Check compliance dashboard
- [ ] Create a policy exemption for a specific resource
- [ ] Trigger a remediation task for non-compliant resources

> ⚠️ **DevOps Gotcha:** Policy evaluation is NOT instant. New policies can take up to **30 minutes** for initial evaluation. Compliance results may show "Not started" for a while. For CI/CD pipelines, never assume a just-assigned policy is immediately active — add a wait/retry loop or use `az policy state trigger-scan`.

#### Part G: Moving Resources

- [ ] Move a storage account from one RG to another
- [ ] Move a VM from one RG to another (note the restrictions!)
- [ ] Try moving a resource between subscriptions
- [ ] Document which resources CAN'T be moved (e.g., Azure Backup vaults with items, resources with resource locks)

> ⚠️ **DevOps Gotcha:** Moving resources between RGs is NOT a simple rename. Behind the scenes, Azure changes the resource ID (the RG is part of the path). If you have hardcoded resource IDs in your ARM templates, Terraform state, or application config, **they will break**. Always use resource names + lookups, never hardcoded IDs.

#### Part H: Cost Management

- [ ] Set up a budget of $50/month with email alerts at 50%, 80%, 100%
- [ ] Create a cost alert for anomaly detection
- [ ] Use Cost Analysis to view costs by resource group, tag, and service
- [ ] Review Azure Advisor cost recommendations
- [ ] Export cost data to a storage account

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Policy shows "Not started" compliance | Evaluation hasn't run yet | Wait 30 min or trigger `az policy state trigger-scan` |
| Can't delete resource group | Resource lock exists | Remove the lock first with `az lock delete` |
| Resource move fails | Resource type doesn't support move | Check [Move operation support](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/move-support-resources) |
| Tag policy doesn't catch existing resources | Policies are evaluated on create/update | Run a remediation task |
| Custom role assignment fails | Role definition scope mismatch | Ensure `AssignableScopes` includes the target scope |
| RBAC changes not taking effect | Token cache | User needs to sign out and sign back in; tokens are cached for ~1 hour |

### 💰 Cost Tips

- Management Groups, Resource Groups, Tags, Policies, RBAC: **All FREE** — no cost to practice
- Cost Management features: **FREE**
- Only costs come from actual resources you deploy
- Delete resources when done; RGs can be deleted with `az group delete --name <rg> --yes --no-wait`

### ✔️ Verification Checklist

- [ ] Management group hierarchy is visible in Portal under "Management Groups"
- [ ] All resource groups have mandatory tags
- [ ] Policy compliance dashboard shows >90% compliant
- [ ] Attempting to create a resource without tags is DENIED
- [ ] Resource lock prevents deletion of production RG
- [ ] Custom RBAC role is assignable and works correctly
- [ ] Budget alert is configured and visible in Cost Management

### 🔍 Behind the Scenes

- **Management Groups** are Azure AD-level constructs (not subscription-level). They exist in the tenant's directory.
- **RBAC** is evaluated on every API call to Azure Resource Manager (ARM). The ARM layer checks: Does this identity have a role assignment with the required `Actions` at this scope or any parent scope?
- **Azure Policy** works via the Azure Policy resource provider. It hooks into ARM's request pipeline — every PUT/PATCH operation is checked against assigned policies before ARM proceeds.
- **Resource locks** are implemented as a special resource type (`Microsoft.Authorization/locks`) that ARM checks before processing delete/modify operations.
- **Tags** are metadata stored in ARM alongside the resource definition. They are NOT passed to the underlying resource provider (e.g., the VM itself doesn't know about its tags).

---

## Scenario 2: Virtual Machine Deep Dive

### 🎯 Objective

Master Azure Virtual Machines end-to-end: provisioning, sizing, high availability, disk management, encryption, security access, backup, and troubleshooting. Understand what happens under the hood when you create a VM.

### 📦 App Description

**A Node.js REST API with a database backend that processes file uploads.** Think of a document management API: POST uploads, GET downloads, metadata stored in a database (PostgreSQL/MySQL on a separate VM or managed service). This forces you to deal with compute, storage, networking, and inter-VM communication.

### 🏗️ Architecture Diagram

```
                        ┌─────────────┐
                        │   INTERNET   │
                        └──────┬──────┘
                               │
                        ┌──────┴──────┐
                        │   BASTION   │
                        │  (Subnet)   │
                        └──────┬──────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                         VNet: 10.0.0.0/16                    │
│                                                              │
│  ┌────────────────────┐          ┌────────────────────┐      │
│  │ Subnet: web-tier   │          │ Subnet: data-tier  │      │
│  │ 10.0.1.0/24        │          │ 10.0.2.0/24        │      │
│  │                    │          │                    │      │
│  │  ┌──────────────┐  │          │  ┌──────────────┐  │      │
│  │  │ VM: web-vm   │  │  ──────► │  │ VM: db-vm    │  │      │
│  │  │ Ubuntu 22.04 │  │  Port    │  │ Ubuntu 22.04 │  │      │
│  │  │ Node.js API  │  │  5432    │  │ PostgreSQL   │  │      │
│  │  │              │  │          │  │              │  │      │
│  │  │ OS Disk(P10) │  │          │  │ OS Disk(P10) │  │      │
│  │  │ Data Disk    │  │          │  │ Data Disk    │  │      │
│  │  │ (P20, 256GB) │  │          │  │ (P30, 512GB) │  │      │
│  │  └──────────────┘  │          │  └──────────────┘  │      │
│  │                    │          │                    │      │
│  │  NSG: nsg-web      │          │  NSG: nsg-data     │      │
│  │  Allow: 443,22     │          │  Allow: 5432 from  │      │
│  │  from Bastion      │          │  web-tier only      │      │
│  └────────────────────┘          └────────────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────┐                    │
│  │ Recovery Services Vault              │                    │
│  │ Daily backup, 30-day retention       │                    │
│  └──────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Resource group created from Scenario 1
- SSH key pair generated (`ssh-keygen -t rsa -b 4096`)
- Azure CLI logged in
- Understanding of Linux basics

### ✅ Hands-on Tasks

#### Part A: Provision VMs

- [ ] Create a Linux VM (Ubuntu 22.04) with SSH key authentication
- [ ] Create a Windows VM (Server 2022) with password authentication
- [ ] Explore VM sizes: understand B-series (burstable), D-series (general purpose), E-series (memory optimized), F-series (compute optimized)
- [ ] Check VM pricing with `az vm list-skus --location eastus --size Standard_B --output table`
- [ ] Understand the resources created with a VM: NIC, OS Disk, Public IP (optional), NSG

```bash
# Create Linux VM
az vm create \
  --resource-group rg-portfolio-dev-eastus \
  --name vm-web-dev-01 \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --ssh-key-values ~/.ssh/id_rsa.pub \
  --vnet-name vnet-dev-eastus \
  --subnet snet-web \
  --nsg nsg-web \
  --public-ip-address "" \
  --storage-sku Premium_LRS \
  --tags env=dev role=webserver

# Create Windows VM
az vm create \
  --resource-group rg-portfolio-dev-eastus \
  --name vm-win-dev-01 \
  --image Win2022Datacenter \
  --size Standard_B2ms \
  --admin-username azureadmin \
  --admin-password 'P@$$w0rd1234!' \
  --public-ip-address ""
```

> ⚠️ **DevOps Gotcha:** When you create a VM via the Portal, Azure creates a PUBLIC IP by default! In production, this is a security risk. Always use `--public-ip-address ""` in CLI or uncheck the public IP option in the portal. Use Bastion or a VPN for access instead.

#### Part B: VM Sizes & Burstable Credits

- [ ] Deploy a B1s VM and monitor CPU credits via Metrics
- [ ] Observe credit accumulation when idle vs credit depletion under load
- [ ] Resize a running VM from B2s to D2s_v3 — understand which sizes require deallocation
- [ ] Check available sizes in your region: `az vm list-vm-resize-options`

> ⚠️ **DevOps Gotcha:** B-series VMs are CHEAP but have a catch — they "burst" using credits. If your app has sustained >20% CPU usage, you'll exhaust credits and performance will throttle to baseline. Many teams deploy B-series for "dev/test," then wonder why staging is slow. Use D-series or higher for anything beyond trivial workloads.

#### Part C: Availability Sets, Zones & Scale Sets

- [ ] Create an Availability Set with 3 fault domains and 5 update domains
- [ ] Deploy 2 VMs into the Availability Set
- [ ] Deploy a VM into Availability Zone 1 and another into Zone 2
- [ ] Create a VM Scale Set (VMSS) with 2-5 instances and auto-scale rules
- [ ] Understand the difference:

```
┌─────────────────────────────────────────────────────────────┐
│ AVAILABILITY SET vs ZONE vs SCALE SET                       │
│                                                             │
│ Availability Set:                                           │
│   Same datacenter, different racks (Fault Domains)          │
│   Protects against: hardware failures in a rack             │
│   SLA: 99.95%                                               │
│                                                             │
│ Availability Zone:                                          │
│   Different datacenters in the same region                  │
│   Protects against: entire datacenter outage                │
│   SLA: 99.99%                                               │
│                                                             │
│ VM Scale Set:                                               │
│   Auto-scaling group of identical VMs                       │
│   Can span zones, has auto-scale rules                      │
│   Best for: stateless apps needing elastic scale            │
└─────────────────────────────────────────────────────────────┘
```

#### Part D: Custom Script Extensions & cloud-init

- [ ] Use cloud-init to install Node.js and your app on VM creation
- [ ] Use Custom Script Extension to run a post-deployment script
- [ ] Compare the two approaches — when to use which

```bash
# cloud-init example (pass as --custom-data)
#cloud-config
package_update: true
packages:
  - nodejs
  - npm
  - nginx
runcmd:
  - git clone https://github.com/your/app.git /opt/app
  - cd /opt/app && npm install
  - npm start
```

```bash
# Custom Script Extension
az vm extension set \
  --resource-group rg-portfolio-dev-eastus \
  --vm-name vm-web-dev-01 \
  --name customScript \
  --publisher Microsoft.Azure.Extensions \
  --settings '{"fileUris":["https://raw.githubusercontent.com/your/repo/setup.sh"],"commandToExecute":"bash setup.sh"}'
```

> ⚠️ **DevOps Gotcha:** Custom Script Extension runs as root and has a **90-minute timeout**. If your script hangs (e.g., waiting for user input from `apt install` without `-y` flag), the extension will timeout and the VM will report as "failed." Always use `-y` or `DEBIAN_FRONTEND=noninteractive` in scripts.

#### Part E: Managed Disks

- [ ] Attach a Premium SSD data disk (P20 = 256GB) to the web VM
- [ ] Format and mount the disk in Linux (`fdisk`, `mkfs.ext4`, `mount`)
- [ ] Add the disk to `/etc/fstab` using UUID (NOT device path!)
- [ ] Take a snapshot of the OS disk
- [ ] Create a new VM from the snapshot
- [ ] Understand disk performance tiers:

```
┌─────────────────────────────────────────────────────────┐
│ MANAGED DISK TIERS                                       │
│                                                         │
│ Standard HDD  │ 500 IOPS  │ Cheapest, sequential I/O  │
│ Standard SSD  │ 500 IOPS  │ Better latency, dev/test   │
│ Premium SSD   │ 5000 IOPS │ Production workloads       │
│ Premium SSD v2│ 80K IOPS  │ Granular IOPS/throughput   │
│ Ultra Disk    │ 160K IOPS │ Mission-critical, SAP HANA │
└─────────────────────────────────────────────────────────┘
```

> ⚠️ **DevOps Gotcha:** NEVER mount disks in `/etc/fstab` using `/dev/sdX` paths! Device paths can change between reboots (especially after adding/removing disks). Always use the disk's UUID: `UUID=<uuid> /data ext4 defaults,nofail 0 2`. The `nofail` option is critical — without it, if the disk fails to mount on boot, the VM will hang and become inaccessible.

#### Part F: Disk Encryption

- [ ] Enable Azure Disk Encryption (ADE) using Key Vault — full disk encryption with BitLocker (Windows) or DM-Crypt (Linux)
- [ ] Compare with Server-Side Encryption (SSE) — default, at-rest encryption by Azure
- [ ] Understand Encryption at Host — encrypts temp disk and disk caches
- [ ] Verify encryption status: `az vm encryption show`

#### Part G: VM Access & Security

- [ ] Deploy Azure Bastion in a dedicated `AzureBastionSubnet`
- [ ] Connect to the Linux VM via Bastion (SSH through browser)
- [ ] Enable Just-in-Time VM access via Microsoft Defender for Cloud
- [ ] Configure auto-shutdown at 7 PM to save costs
- [ ] Use Run Command to execute an emergency script on the VM (useful when SSH is broken)

```bash
# Run command on VM without SSH
az vm run-command invoke \
  --resource-group rg-portfolio-dev-eastus \
  --name vm-web-dev-01 \
  --command-id RunShellScript \
  --scripts "systemctl status nginx"
```

> ⚠️ **DevOps Gotcha:** Azure Bastion has a dedicated subnet requirement: the subnet MUST be named exactly `AzureBastionSubnet` and must be at least /26. If you name it anything else, deployment will fail silently or with a cryptic error. Also, Bastion Standard SKU costs ~$330/month — use the Developer SKU or delete it when not in use!

#### Part H: Backup & Restore

- [ ] Create a Recovery Services Vault
- [ ] Configure daily backup for both VMs with 30-day retention
- [ ] Wait for the first backup to complete
- [ ] Perform a file-level restore (restore individual files, not the whole VM)
- [ ] Perform a full VM restore to a new VM
- [ ] Configure backup alerts

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| VM stuck in "Creating" | Quota limit reached | Check `az vm list-usage --location eastus`; request quota increase |
| VM stuck in "Deallocating" | Extension hung or backend issue | Wait 30 min; if persists, use `az vm delete --force-deletion` |
| VM Agent "Not Ready" | Agent not installed or blocked | Reinstall agent; check if NSG blocks outbound to `168.63.129.16` |
| Extension failed | Script error or timeout | Check `/var/log/azure/` on Linux or Event Viewer on Windows |
| Can't SSH after restart | Disk mounted without `nofail` | Use serial console or Run Command to fix fstab |
| VM performance throttled | B-series credits exhausted | Monitor CPU credits metric; resize to D-series |
| Disk shows wrong size | Partition not expanded | Run `growpart` and `resize2fs` after expanding disk in Azure |

### 💰 Cost Tips

- Use **B1s or B2s** VMs for practice ($5–15/month)
- **Auto-shutdown** at 7 PM saves ~60% cost (no charges when deallocated)
- **Spot VMs** for non-critical practice workloads (up to 90% cheaper)
- **Delete** VMs when done — OS disks still cost money even when VM is stopped!
- Use `az vm deallocate` (stops billing for compute but disk still charged) vs `az vm stop` (compute still allocated!)

> ⚠️ **DevOps Gotcha:** `az vm stop` ≠ `az vm deallocate`! `stop` keeps the VM allocated (you still pay for compute). `deallocate` releases the compute and stops billing. In the Portal, "Stop" actually deallocates, but in CLI, you must explicitly use `deallocate`. This mismatch confuses everyone.

### ✔️ Verification Checklist

- [ ] Both Linux and Windows VMs are running and accessible via Bastion
- [ ] Data disk is mounted and persists across reboots
- [ ] VM has boot diagnostics enabled and serial console works
- [ ] Backup shows "Healthy" with at least one recovery point
- [ ] Auto-shutdown is configured and fires on schedule
- [ ] VM encryption status shows "Encrypted"
- [ ] Custom Script Extension shows "Provisioning succeeded"

### 🔍 Behind the Scenes

- When you create a VM, Azure's Compute Resource Provider (CRP) orchestrates with multiple backend services: it creates the NIC (Network RP), OS Disk (Storage RP), allocates compute (Fabric Controller), and installs the VM Agent.
- The **VM Agent** is a critical component — it handles extensions, reports heartbeat, and enables features like Run Command. Without it, Azure "loses visibility" into the VM.
- **Bastion** works by creating a TLS-secured WebSocket connection from your browser to the Bastion host, which then SSH/RDPs into your VM over the private network. The VM never needs a public IP.
- **Managed Disks** are backed by Azure Storage blobs (page blobs), but you don't manage the storage account — Azure handles replication, availability, and performance tiers transparently.
- **Boot diagnostics** writes console output and screenshots to a storage account, giving you a "virtual KVM" into the VM's boot process — critical when the VM won't start.

---

## Scenario 3: Azure Networking Fundamentals

### 🎯 Objective

Design and implement a production-grade network topology with proper segmentation, security groups, peering, DNS, routing, and troubleshooting. Networking is the #1 area where Azure projects go wrong — master it now.

### 📦 App Description

**A three-tier web application (frontend, API, database)** — each tier runs in a separate subnet. The frontend serves static content + calls the API, the API handles business logic, and the database stores data. This forces you to practice network segmentation, NSG rules, and inter-tier communication.

### 🏗️ Architecture Diagram

```
                          INTERNET
                              │
                        ┌─────┴─────┐
                        │   Azure    │
                        │   Bastion  │
                        └─────┬─────┘
                              │
┌─────────────────────────────┴──────────────────────────────────┐
│                   VNet: vnet-hub-eastus                         │
│                   Address: 10.0.0.0/16                          │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ AzureBastionSubnet│ │ snet-shared      │  │ GatewaySubnet│  │
│  │ 10.0.0.0/26       │ │ 10.0.3.0/24      │  │ 10.0.255.0/27│ │
│  └──────────────────┘  │ (DNS, Jump Box)   │  └──────────────┘  │
│                        └──────────────────┘                    │
└────────────────────────────┬───────────────────────────────────┘
                             │ VNet Peering
┌────────────────────────────┴───────────────────────────────────┐
│                   VNet: vnet-spoke-eastus                       │
│                   Address: 10.1.0.0/16                          │
│                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐    │
│  │ snet-web       │  │ snet-app       │  │ snet-data      │    │
│  │ 10.1.1.0/24    │  │ 10.1.2.0/24    │  │ 10.1.3.0/24    │    │
│  │                │  │                │  │                │    │
│  │  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  │    │
│  │  │ Web VM   │──┼──┼──│ API VM   │──┼──┼──│ DB VM    │  │    │
│  │  │ Nginx    │  │  │  │ Node.js  │  │  │  │ Postgres │  │    │
│  │  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  │    │
│  │                │  │                │  │                │    │
│  │ NSG: Allow 80  │  │ NSG: Allow     │  │ NSG: Allow     │    │
│  │ 443 from       │  │ 3000 from      │  │ 5432 from      │    │
│  │ Internet       │  │ snet-web only  │  │ snet-app only  │    │
│  └────────────────┘  └────────────────┘  └────────────────┘    │
│                                                                │
│  UDR: Route all traffic through Hub (if using NVA/Firewall)   │
└────────────────────────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Resource groups from Scenario 1
- Understanding of IP addressing (CIDR notation)
- VMs from Scenario 2 or willingness to create new ones

### ✅ Hands-on Tasks

#### Part A: VNet & Subnet Design

- [ ] Create a hub VNet (`10.0.0.0/16`) with subnets: `AzureBastionSubnet`, `snet-shared`, `GatewaySubnet`
- [ ] Create a spoke VNet (`10.1.0.0/16`) with subnets: `snet-web`, `snet-app`, `snet-data`
- [ ] Understand why address spaces should NOT overlap
- [ ] Plan subnet sizes considering Azure reserves 5 IPs per subnet

```bash
# Create Hub VNet
az network vnet create \
  --resource-group rg-portfolio-dev-eastus \
  --name vnet-hub-eastus \
  --address-prefix 10.0.0.0/16 \
  --subnet-name AzureBastionSubnet \
  --subnet-prefix 10.0.0.0/26

# Create Spoke VNet
az network vnet create \
  --resource-group rg-portfolio-dev-eastus \
  --name vnet-spoke-eastus \
  --address-prefix 10.1.0.0/16

# Add subnets
az network vnet subnet create --resource-group rg-portfolio-dev-eastus \
  --vnet-name vnet-spoke-eastus --name snet-web --address-prefixes 10.1.1.0/24
az network vnet subnet create --resource-group rg-portfolio-dev-eastus \
  --vnet-name vnet-spoke-eastus --name snet-app --address-prefixes 10.1.2.0/24
az network vnet subnet create --resource-group rg-portfolio-dev-eastus \
  --vnet-name vnet-spoke-eastus --name snet-data --address-prefixes 10.1.3.0/24
```

> ⚠️ **DevOps Gotcha:** Azure reserves the first 4 and last 1 IP address in every subnet. So a `/24` (256 addresses) gives you 251 usable IPs, not 256. A `/29` (8 addresses) gives you only 3 usable IPs! This trips up people planning for AKS (which needs IPs per pod with Azure CNI) or large VMSS deployments.

#### Part B: Network Security Groups (NSGs)

- [ ] Create NSGs for each subnet tier
- [ ] Web NSG: Allow inbound 80/443 from Internet, allow 22 from Bastion subnet
- [ ] App NSG: Allow inbound 3000 from snet-web ONLY, deny all others
- [ ] Data NSG: Allow inbound 5432 from snet-app ONLY, deny all others
- [ ] Understand default NSG rules (AllowVNetInBound, AllowAzureLBInBound, DenyAllInBound)
- [ ] Understand priority ordering (lower number = higher priority)

```bash
# Create NSG and rules
az network nsg create --resource-group rg-portfolio-dev-eastus --name nsg-web

az network nsg rule create \
  --resource-group rg-portfolio-dev-eastus \
  --nsg-name nsg-web \
  --name AllowHTTPS \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 443 \
  --source-address-prefixes Internet

az network nsg rule create \
  --resource-group rg-portfolio-dev-eastus \
  --nsg-name nsg-data \
  --name AllowPostgresFromApp \
  --priority 100 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --destination-port-ranges 5432 \
  --source-address-prefixes 10.1.2.0/24
```

> ⚠️ **DevOps Gotcha:** NSGs can be applied at both the **subnet level** and the **NIC level**. Both are evaluated! Traffic must pass BOTH NSGs. Many teams apply NSGs at both levels and then can't figure out why traffic is blocked — they forgot the NIC-level NSG. Best practice: apply NSGs at the subnet level for simplicity, avoid NIC-level NSGs unless absolutely needed.

#### Part C: Application Security Groups (ASGs)

- [ ] Create ASGs: `asg-webservers`, `asg-appservers`, `asg-dbservers`
- [ ] Assign VMs to ASGs
- [ ] Rewrite NSG rules using ASGs instead of IP ranges
- [ ] Benefit: when you add a new VM, you just add it to the ASG — no NSG rule changes needed

#### Part D: VNet Peering

- [ ] Create peering from hub to spoke and spoke to hub (must be bidirectional!)
- [ ] Test connectivity: ping from hub VM to spoke VM
- [ ] Enable "Allow Gateway Transit" on hub and "Use Remote Gateways" on spoke
- [ ] Understand: peering is NOT transitive (Spoke A ↔ Hub ↔ Spoke B does NOT mean Spoke A can reach Spoke B directly — you need UDRs or NVA)

```bash
# Peer Hub to Spoke
az network vnet peering create \
  --resource-group rg-portfolio-dev-eastus \
  --name hub-to-spoke \
  --vnet-name vnet-hub-eastus \
  --remote-vnet vnet-spoke-eastus \
  --allow-vnet-access true \
  --allow-gateway-transit true

# Peer Spoke to Hub
az network vnet peering create \
  --resource-group rg-portfolio-dev-eastus \
  --name spoke-to-hub \
  --vnet-name vnet-spoke-eastus \
  --remote-vnet vnet-hub-eastus \
  --allow-vnet-access true \
  --use-remote-gateways false
```

> ⚠️ **DevOps Gotcha:** VNet peering is NON-TRANSITIVE. If Hub peers with Spoke-A and Hub peers with Spoke-B, Spoke-A and Spoke-B CANNOT communicate through the Hub by default. You need a Network Virtual Appliance (NVA) or Azure Firewall in the Hub plus User Defined Routes (UDRs) to enable spoke-to-spoke communication. This is the #1 networking surprise for Azure beginners.

#### Part E: Service Endpoints vs Private Endpoints

- [ ] Enable a Service Endpoint for Azure Storage on `snet-app`
- [ ] Configure the Storage Account firewall to allow access from `snet-app` only
- [ ] Create a Private Endpoint for Azure SQL in `snet-data`
- [ ] Compare the two approaches:

```
┌───────────────────────────────────────────────────────────────┐
│ SERVICE ENDPOINT vs PRIVATE ENDPOINT                          │
│                                                               │
│ Service Endpoint:                                             │
│   • Traffic stays on Azure backbone (not public internet)     │
│   • PaaS service still has public IP                          │
│   • Free                                                      │
│   • Source IP = subnet's private IP range                     │
│                                                               │
│ Private Endpoint:                                             │
│   • PaaS service gets a PRIVATE IP in YOUR VNet              │
│   • DNS resolution needed (Private DNS Zone)                  │
│   • Costs money (per endpoint per hour + data)                │
│   • Can completely disable public access                      │
│   • Works across VNet peering and VPN                         │
└───────────────────────────────────────────────────────────────┘
```

#### Part F: Azure DNS

- [ ] Create a Public DNS Zone (requires a domain or use for learning)
- [ ] Create a Private DNS Zone: `privatelink.database.windows.net`
- [ ] Link the Private DNS Zone to your VNet
- [ ] Enable auto-registration for VM DNS records
- [ ] Verify DNS resolution from within a VM using `nslookup`

> ⚠️ **DevOps Gotcha:** Private Endpoints break default DNS resolution. When you create a Private Endpoint for, say, `mydb.database.windows.net`, that FQDN still resolves to a public IP from outside the VNet. You need a Private DNS Zone (`privatelink.database.windows.net`) linked to the VNet to make the FQDN resolve to the private IP inside the VNet. If you forget this step, your VMs will try to reach the PaaS service via the public IP, which will be blocked by the firewall. This is the #1 Private Endpoint debugging issue.

#### Part G: UDR (User Defined Routes)

- [ ] Create a route table
- [ ] Add a route to force all internet-bound traffic through a hub NVA (or Azure Firewall)
- [ ] Associate the route table with a spoke subnet
- [ ] Test that traffic routing changed using Network Watcher > Next Hop

#### Part H: Network Watcher

- [ ] Use **IP Flow Verify** to check if traffic from web VM to db VM on port 5432 is allowed
- [ ] Use **Next Hop** to verify routing
- [ ] Use **Connection Troubleshoot** to test end-to-end connectivity
- [ ] Enable **NSG Flow Logs** and analyze with Traffic Analytics
- [ ] Take a **Packet Capture** on a VM

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| VMs in peered VNets can't communicate | Peering not configured bidirectionally | Create peering in BOTH directions |
| VM can't reach Azure PaaS service | NSG blocking outbound or missing Service Endpoint | Check outbound NSG rules; enable Service Endpoint |
| Private Endpoint DNS not resolving | Missing Private DNS Zone or VNet link | Create zone, link to VNet, verify with `nslookup` |
| Spoke-to-spoke traffic blocked | Peering is non-transitive | Add UDR through hub NVA/Firewall |
| NSG rule not taking effect | Higher priority rule overriding | Check rule priorities (lower number = higher priority) |
| Traffic asymmetric routing | UDR on one direction only | Apply UDR on all relevant subnets for symmetry |
| Overlapping address spaces | Bad planning | Must re-create VNets; can't peer overlapping ranges |

### 💰 Cost Tips

- VNets, Subnets, NSGs, UDRs, ASGs: **All FREE**
- VNet Peering: ~$0.01/GB for same-region, ~$0.035/GB cross-region
- Private Endpoints: ~$0.01/hour + $0.01/GB processed
- Network Watcher: Free for basic; NSG Flow Logs require a storage account
- Bastion: **Expensive** (~$140–330/month) — delete when not practicing

### ✔️ Verification Checklist

- [ ] Web VM can reach App VM on port 3000
- [ ] App VM can reach DB VM on port 5432
- [ ] DB VM CANNOT be reached directly from web tier or internet
- [ ] VNet peering shows "Connected" status on both sides
- [ ] Private Endpoint DNS resolves to private IP from within VNet
- [ ] NSG flow logs show allowed and denied traffic
- [ ] Network Watcher IP Flow Verify confirms expected allow/deny results

### 🔍 Behind the Scenes

- **VNets** are software-defined networks implemented in Azure's networking fabric (Azure SDN). There's no physical network device you can log into.
- **NSGs** are evaluated by the Azure SDN layer at the NIC level. Rules are compiled into flow tables that the hypervisor's virtual switch enforces. They are stateful — if you allow inbound traffic, the response is automatically allowed.
- **VNet Peering** creates a direct link between two VNets at the Azure backbone level. Traffic never leaves Microsoft's network. Peering is NOT a VPN tunnel — it's a fabric-level routing entry.
- **Service Endpoints** modify the route table to send traffic for specific Azure services via the Azure backbone instead of the internet. The PaaS service sees the traffic as coming from a VNet (not a public IP).
- **Private Endpoints** create a special NIC (network interface) in your VNet with a private IP address. Azure's Private Link service maps this NIC to the PaaS service, so traffic is entirely within your VNet.

---

## Scenario 4: Azure Storage Deep Dive

### 🎯 Objective

Master Azure Storage services: Blob, Files, Tables, and Queues. Understand redundancy options, access tiers, lifecycle management, security (SAS tokens, firewalls, encryption), and real-world edge cases around cost optimization and access control.

### 📦 App Description

**A file management application (React/Angular frontend) that uploads, downloads, and manages documents with thumbnail generation.** Users can upload PDFs, images, and office documents. The app stores files in Blob storage, generates thumbnails, manages versions, and allows sharing via time-limited SAS URLs.

### 🏗️ Architecture Diagram

```
                    ┌─────────────┐
                    │   Browser   │
                    │  (React App)│
                    └──────┬──────┘
                           │ Upload/Download
                           │ (SAS Token URL)
┌──────────────────────────┴──────────────────────────────┐
│                 STORAGE ACCOUNT                          │
│            "stfilemanagerdev001"                          │
│              Redundancy: GRS                             │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │              BLOB SERVICE                       │      │
│  │                                                 │      │
│  │  Container: "documents" (Hot)                   │      │
│  │    └── user1/report.pdf                         │      │
│  │    └── user2/photo.jpg                          │      │
│  │                                                 │      │
│  │  Container: "thumbnails" (Cool)                 │      │
│  │    └── user1/report_thumb.jpg                   │      │
│  │    └── user2/photo_thumb.jpg                    │      │
│  │                                                 │      │
│  │  Container: "archives" (Archive)                │      │
│  │    └── old_documents/...                        │      │
│  │                                                 │      │
│  │  LIFECYCLE POLICY:                              │      │
│  │    Hot → Cool after 30 days                     │      │
│  │    Cool → Archive after 90 days                 │      │
│  │    Delete after 365 days                        │      │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ┌─────────────────┐  ┌──────────────────┐               │
│  │   FILE SERVICE   │  │  STATIC WEBSITE  │               │
│  │  "fileshare01"   │  │  $web container  │               │
│  │   SMB 3.0        │  │  index.html      │               │
│  └─────────────────┘  └──────────────────┘               │
│                                                          │
│  SECURITY:                                               │
│  • VNet rules: Allow from snet-app only                  │
│  • Private Endpoint in snet-data                         │
│  • Soft delete: 14 days                                  │
│  • Versioning: Enabled                                   │
└──────────────────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Resource groups from Scenario 1
- VNet from Scenario 3
- Azure CLI and Azure Storage Explorer installed

### ✅ Hands-on Tasks

#### Part A: Storage Account Creation & Redundancy

- [ ] Create storage accounts with different redundancy:
  - LRS (Locally Redundant — 3 copies in one datacenter)
  - ZRS (Zone Redundant — 3 copies across availability zones)
  - GRS (Geo-Redundant — 6 copies across 2 regions)
  - RA-GRS (Read-Access Geo-Redundant — read from secondary)
  - GZRS (Geo-Zone-Redundant — best of both worlds)
- [ ] Understand the cost vs availability tradeoffs
- [ ] Check the secondary endpoint of a RA-GRS account

```bash
az storage account create \
  --name stfilemanagerdev001 \
  --resource-group rg-portfolio-dev-eastus \
  --location eastus \
  --sku Standard_GRS \
  --kind StorageV2 \
  --access-tier Hot \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false
```

> ⚠️ **DevOps Gotcha:** Storage account names must be globally unique, 3-24 characters, lowercase letters and numbers only. No hyphens, no underscores, no uppercase. This is the most restrictive naming convention in Azure and catches people constantly. Use a convention like `st<app><env><random3digits>`.

#### Part B: Blob Storage & Access Tiers

- [ ] Create containers: `documents` (Hot), `thumbnails` (Cool), `archives` (Archive)
- [ ] Upload files to each container
- [ ] Move a blob from Hot to Cool tier
- [ ] Move a blob to Archive tier — then try to read it (you can't — it needs to be rehydrated!)
- [ ] Rehydrate an archived blob (Standard priority: up to 15 hours; High priority: under 1 hour for <10GB)

```bash
# Upload a blob
az storage blob upload \
  --account-name stfilemanagerdev001 \
  --container-name documents \
  --name "reports/annual-2024.pdf" \
  --file ./annual-2024.pdf \
  --tier Hot

# Change tier
az storage blob set-tier \
  --account-name stfilemanagerdev001 \
  --container-name documents \
  --name "reports/annual-2024.pdf" \
  --tier Archive
```

> ⚠️ **DevOps Gotcha:** Archive tier blobs are **offline**. You CANNOT read them. Any attempt to download returns a 409 (Conflict) error. You must rehydrate them first, which can take up to 15 hours. If your app needs to serve archived files, implement a "request access" workflow where users request, you rehydrate, then notify when ready. Many teams learn this the hard way during an incident when they need archived logs urgently.

#### Part C: Lifecycle Management

- [ ] Create a lifecycle policy:
  - Move blobs to Cool tier after 30 days of no modification
  - Move to Archive after 90 days
  - Delete after 365 days
  - Delete old snapshots after 30 days
- [ ] Test the policy (note: policies run once per day, so changes aren't instant)

#### Part D: Versioning & Soft Delete

- [ ] Enable blob versioning
- [ ] Upload a file, then upload a modified version — verify both versions exist
- [ ] Enable soft delete (14-day retention)
- [ ] Delete a blob, then recover it from soft-deleted state
- [ ] Enable container soft delete

> ⚠️ **DevOps Gotcha:** Versioning + soft delete can cause storage costs to EXPLODE silently. Every modification creates a new version and the old version is retained. If you have a blob that's updated frequently (e.g., a log file), you'll end up with thousands of versions. Always pair versioning with a lifecycle policy that deletes old versions.

#### Part E: SAS Tokens

- [ ] Generate an Account-level SAS token
- [ ] Generate a Service-level SAS token (scoped to blob service only)
- [ ] Generate a User Delegation SAS (uses Azure AD, most secure)
- [ ] Create a Stored Access Policy and generate a SAS from it
- [ ] Revoke a SAS by deleting the Stored Access Policy
- [ ] Understand: you CANNOT revoke a standalone SAS — only by rotating the storage key

```bash
# Generate Service SAS
az storage blob generate-sas \
  --account-name stfilemanagerdev001 \
  --container-name documents \
  --name "reports/annual-2024.pdf" \
  --permissions r \
  --expiry 2025-12-31T00:00:00Z \
  --https-only
```

> ⚠️ **DevOps Gotcha:** If a SAS token is leaked, you can only invalidate it by rotating the storage account key it was signed with. This invalidates ALL SAS tokens signed with that key, which can cause widespread outages. Best practice: use User Delegation SAS (signed by Azure AD, can be revoked per-user) or Stored Access Policies (can be deleted to revoke). Never use account-level SAS with long expiry times.

#### Part F: Storage Security

- [ ] Configure Storage Firewall: allow access from specific VNet subnet only
- [ ] Create a Private Endpoint for the storage account
- [ ] Disable public access entirely (force Private Endpoint only)
- [ ] Enable infrastructure encryption (double encryption)
- [ ] Enable immutable storage (WORM — Write Once Read Many) on a container

#### Part G: Static Website Hosting

- [ ] Enable static website hosting on the storage account
- [ ] Upload your portfolio site from Scenario 1 to the `$web` container
- [ ] Access it via the static website endpoint
- [ ] Configure a custom domain and HTTPS using Azure CDN

#### Part H: Azure Files

- [ ] Create an Azure File Share (SMB protocol)
- [ ] Mount it on a Linux VM: `mount -t cifs`
- [ ] Mount it on a Windows VM: `net use`
- [ ] Understand SMB vs NFS (NFS requires Premium tier, Linux only)
- [ ] Configure Azure File Sync (sync on-prem file server with Azure Files)

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| 403 Forbidden when accessing blob | Firewall blocking, SAS expired, or wrong permissions | Check firewall rules, SAS expiry, and permission flags |
| 409 Conflict when reading archive blob | Blob is offline (Archive tier) | Rehydrate blob first with `set-tier` to Hot/Cool |
| Storage account name rejected | Already taken globally or invalid characters | Use a unique name with only lowercase + numbers |
| SAS URL stopped working | Storage key rotated or SAS expired | Regenerate SAS; use User Delegation SAS going forward |
| File share mount fails on Linux | Port 445 blocked by ISP/firewall | Check outbound 445; some ISPs block SMB — use VPN |
| CORS error from web app | CORS not configured on storage | Set CORS rules: `az storage cors add` |
| Throttling (503 errors) | Hit IOPS or throughput limits | Scale to Premium, split across accounts, implement retry |

### 💰 Cost Tips

- **Hot** tier: higher storage cost, lower access cost (frequent access)
- **Cool** tier: ~50% cheaper storage, higher access cost (infrequent)
- **Archive** tier: ~90% cheaper storage, expensive access + rehydration delay
- Use lifecycle policies aggressively — this is the #1 cost saver
- Monitor blob count and version count — versions pile up silently
- Use LRS for dev/test, GRS/GZRS for production only
- Static websites on Storage are extremely cheap (pennies/month)

### ✔️ Verification Checklist

- [ ] Blobs are accessible via SAS URL but NOT via direct public URL
- [ ] Lifecycle policy is configured and visible in portal
- [ ] Versioning shows multiple versions of a re-uploaded blob
- [ ] Soft-deleted blob can be recovered
- [ ] Private Endpoint resolves to private IP from VNet
- [ ] Static website serves your portfolio site
- [ ] Azure Files share is mounted and writable from VM
- [ ] CORS is configured for your web app domain

### 🔍 Behind the Scenes

- **Azure Storage** runs on a distributed storage system called **Azure Storage Stamp** — a cluster of storage nodes that replicate data according to your redundancy tier.
- **LRS** stores 3 copies across separate fault domains within ONE datacenter. **ZRS** stores 3 copies across 3 different availability zones (datacenters). **GRS** stores 3 copies locally + 3 copies in a paired region (6 total).
- **Access tiers** control WHERE data is stored physically. Hot = SSD/fast storage. Cool = slower, cheaper media. Archive = offline tape-like storage that requires rehydration.
- **SAS tokens** are cryptographic signatures — the token IS the authorization. There's no session or server-side state. That's why you can't revoke individual tokens without rotating the signing key.
- **Private Endpoints** work by creating a special NIC in your VNet subnet that maps to the storage account's internal IP. Azure's Private Link service handles the NAT from your VNet to the storage stamp.

---

## Scenario 5: Azure App Service Fundamentals

### 🎯 Objective

Deploy and manage web applications on Azure App Service (PaaS). Master deployment methods, deployment slots, scaling, custom domains, SSL, diagnostics, and troubleshooting. Understand why PaaS is preferred over VMs for most web workloads.

### 📦 App Description

**A full-stack e-commerce application (Node.js/Python backend + React frontend)** with user authentication, product catalog, shopping cart, and order processing. This is complex enough to test real deployment scenarios: environment variables, database connections, session management, and background processing.

### 🏗️ Architecture Diagram

```
                              INTERNET
                                  │
                           ┌──────┴──────┐
                           │  Custom     │
                           │  Domain +   │
                           │  SSL Cert   │
                           └──────┬──────┘
                                  │
┌─────────────────────────────────┴──────────────────────────────┐
│                     APP SERVICE PLAN                            │
│                   "asp-ecommerce-dev"                           │
│                   SKU: Standard S1                              │
│                   Instances: 1-3 (auto-scale)                  │
│                                                                │
│  ┌─────────────────────────────────────────┐                   │
│  │          WEB APP (Production Slot)       │                   │
│  │        "app-ecommerce-dev-eastus"        │                   │
│  │                                          │                   │
│  │  Runtime: Node.js 20 LTS                 │                   │
│  │  Always On: Enabled                      │                   │
│  │  Health Check: /api/health               │                   │
│  │                                          │                   │
│  │  App Settings:                           │                   │
│  │    DB_CONNECTION=@KV-reference           │                   │
│  │    NODE_ENV=production                   │                   │
│  │    REDIS_URL=@KV-reference               │                   │
│  │                                          │                   │
│  │  Deployment Slots:                       │                   │
│  │    [production] ◄──swap──► [staging]      │                   │
│  │                                          │                   │
│  └──────────────┬──────────────────────────┘                   │
│                 │                                               │
│    ┌────────────┴────────────┐                                  │
│    │ VNet Integration        │                                  │
│    │ (snet-app-integration)  │                                  │
│    └────────────┬────────────┘                                  │
│                 │                                               │
│    ┌────────────┴────────────┐                                  │
│    │ Private Endpoint for:   │                                  │
│    │  • Azure SQL Database   │                                  │
│    │  • Redis Cache          │                                  │
│    │  • Storage Account      │                                  │
│    └─────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 📋 Pre-requisites

- Resource groups from Scenario 1
- VNet from Scenario 3
- Storage account from Scenario 4
- A web application ready to deploy (pick from GitHub)

### ✅ Hands-on Tasks

#### Part A: App Service Plan & Web App Creation

- [ ] Create App Service Plans at different tiers and understand limitations:
  - Free (F1): 60 min/day compute, no custom domains, no SSL
  - Basic (B1): custom domains, SSL, manual scale
  - Standard (S1): auto-scale, deployment slots, VNet integration
  - Premium (P1v3): more power, zone redundancy
- [ ] Create a web app on the Standard tier
- [ ] Explore the Kudu console (SCM site): `https://<app>.scm.azurewebsites.net`

```bash
# Create App Service Plan
az appservice plan create \
  --name asp-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus \
  --sku S1 \
  --is-linux

# Create Web App
az webapp create \
  --name app-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus \
  --plan asp-ecommerce-dev-eastus \
  --runtime "NODE:20-lts"
```

> ⚠️ **DevOps Gotcha:** The Free (F1) and Shared (D1) tiers run on shared infrastructure and have a daily CPU quota. When your app exceeds the quota, it returns **403 errors** until the quota resets (every 24 hours). This confuses developers who think their app is broken when it's just throttled. Never use Free/Shared for anything beyond a quick test.

#### Part B: Deployment Methods

- [ ] Deploy via ZIP deployment: `az webapp deploy --src-path app.zip`
- [ ] Deploy via Git (Local Git deployment source)
- [ ] Deploy via GitHub Actions (configure in Deployment Center)
- [ ] Deploy via Docker container from ACR (if you have one)
- [ ] Compare deployment strategies and when to use each

```bash
# ZIP Deploy
az webapp deploy \
  --resource-group rg-portfolio-dev-eastus \
  --name app-ecommerce-dev-eastus \
  --src-path ./dist.zip \
  --type zip

# Local Git Deploy
az webapp deployment source config-local-git \
  --name app-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus
```

#### Part C: Deployment Slots

- [ ] Create a "staging" deployment slot
- [ ] Deploy a new version to the staging slot
- [ ] Test the staging slot URL: `https://app-ecommerce-dev-eastus-staging.azurewebsites.net`
- [ ] Swap staging ↔ production
- [ ] Verify zero-downtime deployment
- [ ] Configure auto-swap (deploy to staging → auto-swaps to production after warm-up)
- [ ] Understand slot-sticky settings (settings that DON'T swap, like database connections)

```bash
# Create staging slot
az webapp deployment slot create \
  --name app-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus \
  --slot staging

# Swap slots
az webapp deployment slot swap \
  --name app-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus \
  --slot staging \
  --target-slot production
```

> ⚠️ **DevOps Gotcha:** Slot swaps change the **hostname routing**, not the app itself. Both slots still exist with their original content. The swap just changes which slot serves the production URL. However, app settings marked as "slot setting" (sticky) do NOT swap — the production slot keeps its own database connection string. If you forget to mark a setting as sticky, your staging database connection might go to production. This is a classic data corruption risk!

#### Part D: App Settings & Connection Strings

- [ ] Configure app settings via CLI: `az webapp config appsettings set`
- [ ] Use Key Vault references for secrets: `@Microsoft.KeyVault(VaultName=...;SecretName=...)`
- [ ] Mark settings as "slot sticky" (stay with the slot, don't swap)
- [ ] Understand how App Service settings override `appsettings.json` in .NET or environment variables in Node.js
- [ ] Configure connection strings separately from app settings

```bash
# Set app settings
az webapp config appsettings set \
  --resource-group rg-portfolio-dev-eastus \
  --name app-ecommerce-dev-eastus \
  --settings NODE_ENV=production API_KEY="@Microsoft.KeyVault(VaultName=kv-dev-001;SecretName=api-key)"

# Mark as slot setting (sticky)
az webapp config appsettings set \
  --resource-group rg-portfolio-dev-eastus \
  --name app-ecommerce-dev-eastus \
  --slot-settings DB_CONNECTION="Server=prod-db..."
```

> ⚠️ **DevOps Gotcha:** App Settings in Azure App Service are exposed as **environment variables** to your app. On Linux, the variable name is exactly as you set it. On Windows, some special characters in names are replaced (e.g., `.` becomes `_`). Also, changing an app setting **restarts your app** — all of them, immediately. Don't update settings during peak traffic unless you're using deployment slots.

#### Part E: Custom Domains & SSL

- [ ] Add a custom domain (requires DNS CNAME or A record + TXT verification)
- [ ] Create a free App Service Managed Certificate (auto-renews!)
- [ ] Understand SNI SSL binding (modern, supports multiple domains per IP) vs IP-based SSL (legacy, requires dedicated IP)
- [ ] Force HTTPS redirect
- [ ] Set minimum TLS version to 1.2

#### Part F: Scaling

- [ ] Manually scale to 3 instances
- [ ] Configure auto-scale rules:
  - Scale out when CPU > 70% for 5 minutes
  - Scale in when CPU < 30% for 10 minutes
  - Min 1, Max 5 instances
- [ ] Load test the app and watch auto-scale in action
- [ ] Scale UP (change SKU from S1 to P1v3) vs Scale OUT (add instances)

> ⚠️ **DevOps Gotcha:** Auto-scale has a **cooldown period** (default 5 minutes). After scaling out, it won't scale out again for 5 minutes, even if load is still high. Also, scaling IN is more conservative than scaling OUT to avoid flapping. If your app has sudden traffic spikes, pre-scale (set min instances higher) rather than relying solely on auto-scale.

#### Part G: Diagnostics & Debugging

- [ ] Enable Application Logging (filesystem and blob storage)
- [ ] Enable Web Server Logging
- [ ] Enable Detailed Error Messages
- [ ] View live log stream: `az webapp log tail`
- [ ] Use the Kudu console to browse the filesystem, check process list, and download logs
- [ ] Enable Health Check endpoint (`/api/health`)
- [ ] Configure Application Insights integration

```bash
# Stream logs in real-time
az webapp log tail \
  --name app-ecommerce-dev-eastus \
  --resource-group rg-portfolio-dev-eastus
```

#### Part H: Access Restrictions & VNet Integration

- [ ] Configure IP restriction rules (allow only your office IP)
- [ ] Configure Service Endpoint restriction (allow from specific VNet/subnet)
- [ ] Enable VNet Integration (outbound — app can reach private resources)
- [ ] Create a Private Endpoint for the app (inbound — app has no public IP)
- [ ] Configure Hybrid Connections (access on-prem resources)

> ⚠️ **DevOps Gotcha:** VNet Integration and Private Endpoints do DIFFERENT things! **VNet Integration** gives your app an OUTBOUND path into your VNet (so it can reach private databases, etc.). **Private Endpoint** gives your app an INBOUND private IP (so it's not publicly accessible). Most production apps need BOTH: Private Endpoint for inbound + VNet Integration for outbound.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| 502 Bad Gateway | App crashed or taking too long to start | Check logs via Kudu; increase startup timeout |
| 503 Service Unavailable | App Service Plan at capacity or app pool crash | Scale up/out; check for memory leaks |
| Slot swap fails | Staging slot not warm, or app init fails | Enable health check; test staging before swap |
| App restarts randomly | Platform update or memory limit exceeded | Check platform logs; investigate memory usage |
| Cold start (slow first request) | App pool recycled after idle | Enable "Always On" (requires Basic tier+) |
| Key Vault reference not working | Managed Identity not configured or Access Policy missing | Enable system-assigned identity; add to KV access |
| Custom domain shows cert error | Certificate not bound or wrong binding type | Rebind certificate; check SSL binding type |
| CORS errors | CORS not configured in App Service | Configure allowed origins in App Service CORS settings |

### 💰 Cost Tips

- Free tier: truly free but severely limited
- Basic B1 (~$13/month): good for learning with custom domains
- Standard S1 (~$73/month): needed for slots and auto-scale
- Delete apps AND plans when done — empty plans still incur charges!
- Use the Dev/Test pricing option if available on your subscription
- Multiple apps can share one plan (density packing)

### ✔️ Verification Checklist

- [ ] Web app is accessible and returns 200 OK
- [ ] Staging slot deploys independently and is testable
- [ ] Slot swap completes without downtime
- [ ] Custom domain resolves and shows valid SSL certificate
- [ ] Auto-scale triggers under load (verify with Azure Monitor metrics)
- [ ] Health check endpoint is configured and reporting healthy
- [ ] Application Insights shows requests, dependencies, and exceptions
- [ ] Key Vault references resolve correctly (check app settings in Kudu > Environment)
- [ ] VNet Integration shows the app can reach private resources

### 🔍 Behind the Scenes

- **App Service** runs on a pool of Azure VMs managed by the App Service **"stamp"** (a unit of deployment). Your app runs as a process inside an IIS (Windows) or Nginx+Kestrel (Linux) setup on these shared VMs.
- **"Always On"** periodically pings your app to prevent IIS/the OS from recycling the worker process after idle timeout (default 20 minutes). Without it, the first request after idle has a "cold start."
- **Slot swaps** work by changing the routing rules at the load balancer level. Both slots are "warm" (running) before the swap. The swap operation first warms up the target slot by sending initialization requests, then switches the virtual IP mapping. This is why it's near-zero-downtime.
- **VNet Integration** works by injecting a virtual NIC into your app's worker process, connecting it to a delegated subnet in your VNet. Traffic from your app to resources in the VNet flows through this NIC and is subject to NSG rules and UDRs on that subnet.
- **Kudu** is the deployment/debugging sidecar. It runs alongside your app on the same VM, at `*.scm.azurewebsites.net`. It has a process explorer, file browser, environment viewer, and log streamer — invaluable for debugging.

---

## 🎯 What's Next?

After completing Batch 1, you should have solid foundations in:
- ✅ Azure resource organization and governance
- ✅ Virtual Machines and compute management
- ✅ Networking, segmentation, and security
- ✅ Storage services and data management
- ✅ Platform-as-a-Service web hosting

**Proceed to → Batch 2: Security, Identity & Advanced Networking** where you'll tackle Azure AD, Key Vault, Firewalls, Load Balancers, and VPN Gateways.
