# ☁️ Azure Services — Complete Reference Handbook

> **Audience:** DevOps / Cloud Engineers & Trainees
> **Format:** Each service → plain English explanation → key terms → input/output → use cases → az CLI example → ASCII diagram → gotcha
> **Tip:** Use the Table of Contents below to jump to any service.

---

## Table of Contents

### Chapter 1 — Azure Compute Services
- [1.1 Azure Virtual Machines (VMs)](#11-azure-virtual-machines-vms)
- [1.2 VM Scale Sets (VMSS)](#12-vm-scale-sets-vmss)
- [1.3 Azure App Service](#13-azure-app-service)
- [1.4 Azure Functions](#14-azure-functions)
- [1.5 Azure Container Instances (ACI)](#15-azure-container-instances-aci)
- [1.6 Azure Kubernetes Service (AKS)](#16-azure-kubernetes-service-aks)
- [1.7 Azure Container Apps](#17-azure-container-apps)
- [1.8 Azure Batch](#18-azure-batch)
- [1.9 Azure Virtual Desktop (AVD)](#19-azure-virtual-desktop-avd)
- [1.10 Azure Spring Apps](#110-azure-spring-apps)
- [1.11 Azure Service Fabric](#111-azure-service-fabric)
- [1.12 Compute Decision Guide](#112-compute-decision-guide)

### Chapter 2 — Azure Networking Services
- [2.1 Virtual Network (VNet)](#21-virtual-network-vnet)
- [2.2 Subnets](#22-subnets)
- [2.3 Network Security Groups (NSG)](#23-network-security-groups-nsg)
- [2.4 Network Interface Card (NIC)](#24-network-interface-card-nic)
- [2.5 Public IP Addresses](#25-public-ip-addresses)
- [2.6 Azure Load Balancer](#26-azure-load-balancer)
- [2.7 Application Gateway](#27-application-gateway)
- [2.8 Azure Front Door](#28-azure-front-door)
- [2.9 Azure DNS](#29-azure-dns)
- [2.10 VNet Peering](#210-vnet-peering)
- [2.11 VPN Gateway](#211-vpn-gateway)
- [2.12 ExpressRoute](#212-expressroute)
- [2.13 Azure Bastion](#213-azure-bastion)
- [2.14 Azure Firewall](#214-azure-firewall)
- [2.15 Private Link & Private Endpoints](#215-private-link--private-endpoints)
- [2.16 Azure Traffic Manager](#216-azure-traffic-manager)
- [2.17 NAT Gateway](#217-nat-gateway)
- [2.18 Azure CDN](#218-azure-cdn)
- [2.19 Service Endpoints](#219-service-endpoints)
- [2.20 Network Watcher](#220-network-watcher)

### Chapter 3 — Azure Identity & Access Management
- [3.1 Microsoft Entra ID (Azure AD)](#31-microsoft-entra-id-azure-ad)
- [3.2 Azure RBAC](#32-azure-rbac)
- [3.3 Managed Identities](#33-managed-identities)
- [3.4 Service Principals](#34-service-principals)
- [3.5 Conditional Access](#35-conditional-access)
- [3.6 Privileged Identity Management (PIM)](#36-privileged-identity-management-pim)

### Chapter 4 — Azure Governance & Compliance
- [4.1 Management Groups](#41-management-groups)
- [4.2 Azure Policy](#42-azure-policy)
- [4.3 Azure Blueprints](#43-azure-blueprints)
- [4.4 Resource Locks](#44-resource-locks)
- [4.5 Tags](#45-tags)
- [4.6 Azure Cost Management](#46-azure-cost-management)

### Chapter 5 — Azure Storage Services
- [5.1 Storage Accounts](#51-storage-accounts)
- [5.2 Blob Storage](#52-blob-storage)
- [5.3 Azure Files](#53-azure-files)
- [5.4 Table Storage](#54-table-storage)
- [5.5 Queue Storage](#55-queue-storage)
- [5.6 Managed Disks](#56-managed-disks)
- [5.7 Storage Access & Security](#57-storage-access--security)

### Chapter 6 — Azure Security Services
- [6.1 Azure Key Vault](#61-azure-key-vault)
- [6.2 Microsoft Defender for Cloud](#62-microsoft-defender-for-cloud)
- [6.3 Azure DDoS Protection](#63-azure-ddos-protection)
- [6.4 Microsoft Sentinel](#64-microsoft-sentinel)

### Chapter 7 — Azure Backup & Disaster Recovery
- [7.1 Azure Backup](#71-azure-backup)
- [7.2 Recovery Services Vault](#72-recovery-services-vault)
- [7.3 Azure Site Recovery (ASR)](#73-azure-site-recovery-asr)
- [7.4 Geo-Replication & Paired Regions](#74-geo-replication--paired-regions)

### Chapter 8 — Azure Monitoring & Observability
- [8.1 Azure Monitor](#81-azure-monitor)
- [8.2 Log Analytics Workspace](#82-log-analytics-workspace)
- [8.3 Application Insights](#83-application-insights)
- [8.4 Alerts & Action Groups](#84-alerts--action-groups)

### Chapter 9 — Azure Container & Registry Services
- [9.1 Azure Container Registry (ACR)](#91-azure-container-registry-acr)
- [9.2 ACI Deep Dive](#92-aci-deep-dive)
- [9.3 AKS Deep Dive](#93-aks-deep-dive)

### Chapter 10 — Azure Resource Manager & IaC
- [10.1 Azure Resource Manager (ARM)](#101-azure-resource-manager-arm)
- [10.2 ARM Templates (JSON)](#102-arm-templates-json)
- [10.3 Bicep Language](#103-bicep-language)
- [10.4 Terraform on Azure](#104-terraform-on-azure)

### Chapter 11 — Azure Database Services
- [11.1 Azure SQL Database](#111-azure-sql-database)
- [11.2 Azure Cosmos DB](#112-azure-cosmos-db)
- [11.3 Azure Database for MySQL/PostgreSQL](#113-azure-database-for-mysqlpostgresql)
- [11.4 Azure Cache for Redis](#114-azure-cache-for-redis)

### Chapter 12 — Azure Messaging & Integration
- [12.1 Azure Service Bus](#121-azure-service-bus)
- [12.2 Azure Event Grid](#122-azure-event-grid)
- [12.3 Azure Event Hubs](#123-azure-event-hubs)
- [12.4 Azure Logic Apps](#124-azure-logic-apps)
- [12.5 Azure API Management](#125-azure-api-management)

### Chapter 13 — Azure DevOps Services
- [13.1 Azure DevOps Overview](#131-azure-devops-overview)
- [13.2 Azure Pipelines (YAML)](#132-azure-pipelines-yaml)

### Chapter 14 — Azure Serverless & App Platform
- [14.1 Azure Functions Deep Dive](#141-azure-functions-deep-dive)
- [14.2 Azure Static Web Apps](#142-azure-static-web-apps)

### Chapter 15 — Hands-on Tasks
- [Task Set 1: Compute](#task-set-1-compute)
- [Task Set 2: Networking](#task-set-2-networking)
- [Task Set 3: Identity & Governance](#task-set-3-identity--governance)
- [Task Set 4: Storage & Security](#task-set-4-storage--security)
- [Task Set 5: IaC](#task-set-5-iac)

### Chapter 16 — Interview Questions
- [Compute Interview Questions](#compute-interview-questions)
- [Networking Interview Questions](#networking-interview-questions)
- [Identity & Security Interview Questions](#identity--security-interview-questions)
- [Storage & IaC Interview Questions](#storage--iac-interview-questions)
- [General Azure Interview Questions](#general-azure-interview-questions)

---

# Chapter 1 — Azure Compute Services

> **Compute** = anything that runs your code. Azure gives you 11+ ways to run code — from raw VMs to fully serverless.

```
  AZURE COMPUTE SPECTRUM
  ──────────────────────────────────────────────────────────────
  MORE CONTROL                                    LESS CONTROL
  (you manage more)                         (Azure manages more)

  VMs ──► VMSS ──► AKS ──► Container Apps ──► App Service ──► Functions
  IaaS                                                          Serverless

  Rule: Move RIGHT unless you have a reason to stay LEFT.
```

---

## 1.1 Azure Virtual Machines (VMs)

**What is it?** A virtual computer in the cloud. You pick the OS, size, and software — Azure gives you a server running in minutes. It's like renting a laptop in a data center.

**Key terms:**

| Term | Meaning |
|------|---------|
| **VM Size** | How much CPU, RAM, and disk the VM gets (e.g., Standard_D2s_v5 = 2 vCPU, 8 GB RAM) |
| **Image** | Pre-built OS template (Ubuntu 22.04, Windows Server 2022, etc.) |
| **Availability Zone** | A separate datacenter within a region (for high availability) |
| **Managed Disk** | Azure-managed virtual hard drive attached to a VM |
| **NIC** | Network Interface Card — connects VM to a virtual network |
| **NSG** | Network Security Group — firewall rules for the VM |

**Input → Output:**

```
  You give it:  OS image + VM size + network config + SSH key
  It gives you: A running server with a public/private IP you can SSH/RDP into
```

**Use cases:**
1. Run legacy apps that need a full OS
2. Host databases (SQL Server, MongoDB)
3. Build/test servers for CI/CD
4. Run software that needs GPU (ML training)

**Other ways to use it:**
- As a self-hosted CI/CD agent (Azure DevOps, GitHub Actions)
- As a bastion/jump server to access private networks
- As a VPN appliance (e.g., WireGuard, OpenVPN)

**Example:**

```bash
# Create a resource group
az group create --name rg-demo --location eastus

# Create a Linux VM
az vm create \
    --resource-group rg-demo \
    --name vm-web01 \
    --image Ubuntu2204 \
    --size Standard_D2s_v5 \
    --admin-username azureuser \
    --generate-ssh-keys \
    --zone 1

# Open port 80
az vm open-port --resource-group rg-demo --name vm-web01 --port 80

# SSH into the VM
ssh azureuser@<public-ip>

# List all VMs
az vm list -d --output table

# Stop VM (still billed for disk)
az vm deallocate --resource-group rg-demo --name vm-web01

# Delete VM
az vm delete --resource-group rg-demo --name vm-web01 --yes
```

**Diagram:**

```
  ┌─────────────────────────────────────────────┐
  │  Azure Region (East US)                     │
  │                                             │
  │  ┌─────────────────────────────────────┐   │
  │  │  VNet: 10.0.0.0/16                 │   │
  │  │                                     │   │
  │  │  ┌───────────────────────────────┐ │   │
  │  │  │ Subnet: 10.0.1.0/24          │ │   │
  │  │  │                               │ │   │
  │  │  │  ┌─────────┐   ┌─────────┐  │ │   │
  │  │  │  │  NIC     │──►│  NSG    │  │ │   │
  │  │  │  └────┬────┘   └─────────┘  │ │   │
  │  │  │       │                      │ │   │
  │  │  │  ┌────▼────┐                │ │   │
  │  │  │  │  VM      │                │ │   │
  │  │  │  │ Ubuntu   │                │ │   │
  │  │  │  │ 2 vCPU   │                │ │   │
  │  │  │  │ 8GB RAM  │                │ │   │
  │  │  │  │ [Disk]   │                │ │   │
  │  │  │  └─────────┘                │ │   │
  │  │  └───────────────────────────────┘ │   │
  │  └─────────────────────────────────────┘   │
  │                                             │
  │  Public IP: 20.50.x.x ──► NIC ──► VM      │
  └─────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Stopping a VM via OS (`sudo shutdown`) keeps the VM allocated — you still pay. Use `az vm deallocate` to stop billing for compute (you still pay for disk).

---

## 1.2 VM Scale Sets (VMSS)

**What is it?** A group of identical VMs that automatically grows or shrinks based on demand. Think of it as "auto-pilot for VMs" — if traffic increases, Azure adds more VMs. If it drops, VMs are removed.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Instance** | One VM inside the scale set |
| **Scaling rule** | "If CPU > 70% for 5 min, add 2 VMs" |
| **Scale-in / Scale-out** | Removing / adding instances |
| **Orchestration mode** | Uniform (identical VMs) or Flexible (mix of VM sizes) |
| **Upgrade policy** | How OS/app updates roll out: Manual, Rolling, or Automatic |

**Input → Output:**

```
  You give it:  VM image + size + min/max count + scaling rules
  It gives you: A fleet of identical VMs that auto-scales with demand
```

**Use cases:**
1. Web server fleet behind a load balancer
2. Batch processing workers (video encoding, data pipelines)
3. Self-hosted CI/CD agent pools
4. Stateless microservices at scale

**Example:**

```bash
# Create a VMSS with autoscale (2-10 instances)
az vmss create \
    --resource-group rg-demo \
    --name vmss-web \
    --image Ubuntu2204 \
    --instance-count 2 \
    --vm-sku Standard_D2s_v5 \
    --admin-username azureuser \
    --generate-ssh-keys \
    --upgrade-policy-mode Rolling \
    --load-balancer lb-web

# Add autoscale rule
az monitor autoscale create \
    --resource-group rg-demo \
    --resource vmss-web \
    --resource-type Microsoft.Compute/virtualMachineScaleSets \
    --min-count 2 --max-count 10 --count 2

az monitor autoscale rule create \
    --resource-group rg-demo \
    --autoscale-name vmss-web \
    --condition "Percentage CPU > 70 avg 5m" \
    --scale out 2

# List instances
az vmss list-instances -g rg-demo -n vmss-web -o table
```

**Diagram:**

```
                    Internet
                       │
                 ┌─────▼─────┐
                 │   Load     │
                 │  Balancer  │
                 └──┬──┬──┬──┘
                    │  │  │
          ┌─────────┘  │  └─────────┐
          ▼            ▼            ▼
     ┌────────┐  ┌────────┐  ┌────────┐
     │ VM #1  │  │ VM #2  │  │ VM #3  │   ← All identical
     │ Ubuntu │  │ Ubuntu │  │ Ubuntu │   ← Auto-created
     │ Nginx  │  │ Nginx  │  │ Nginx  │   ← Auto-scaling
     └────────┘  └────────┘  └────────┘

     CPU > 70%? → Azure adds VM #4, #5...
     CPU < 30%? → Azure removes extra VMs
```

> ⚠️ **Gotcha:** Scale-in can kill active requests. Use `terminateNotificationProfile` to give VMs a grace period (e.g., 5 minutes) to drain connections before deletion.

---

## 1.3 Azure App Service

**What is it?** A fully managed platform to host web apps, REST APIs, and backends. You push your code — Azure handles servers, OS patches, scaling, and SSL. Like a hotel: you bring your luggage (code), they handle everything else.

**Key terms:**

| Term | Meaning |
|------|---------|
| **App Service Plan** | The "server" your app runs on — defines CPU, RAM, pricing tier |
| **Deployment Slot** | A copy of your app (e.g., "staging") you can swap into production with zero downtime |
| **Always On** | Keeps app loaded in memory (prevents cold starts). Only in Standard+ tiers |
| **Managed Identity** | Lets your app authenticate to Azure services (Key Vault, SQL) without passwords |
| **Custom Domain** | Use your own domain (myapp.com) instead of myapp.azurewebsites.net |

**Input → Output:**

```
  You give it:  Your code (Python/Node/Java/.NET) + runtime version
  It gives you: A running web app at https://myapp.azurewebsites.net with auto-SSL
```

**Use cases:**
1. Company website or web application
2. REST API backend for mobile apps
3. Staging environments for testing
4. WordPress / CMS hosting

**Other ways to use it:**
- Run Docker containers (Web App for Containers)
- Host WebJobs for background processing
- Use as a reverse proxy to internal services

**Example:**

```bash
# Create App Service Plan (Linux, B1 tier)
az appservice plan create \
    --name asp-demo --resource-group rg-demo \
    --sku B1 --is-linux

# Create a Python web app
az webapp create \
    --name myapp-demo-2024 --resource-group rg-demo \
    --plan asp-demo --runtime "PYTHON:3.12"

# Deploy from GitHub
az webapp deployment source config \
    --name myapp-demo-2024 --resource-group rg-demo \
    --repo-url https://github.com/user/repo --branch main

# Create a staging slot
az webapp deployment slot create \
    --name myapp-demo-2024 --resource-group rg-demo \
    --slot staging

# Swap staging → production (zero downtime)
az webapp deployment slot swap \
    --name myapp-demo-2024 --resource-group rg-demo \
    --slot staging --target-slot production

# View logs
az webapp log tail --name myapp-demo-2024 --resource-group rg-demo
```

**Diagram:**

```
  Developer                    Azure App Service
  ─────────                    ──────────────────
  git push ──────────────────► ┌──────────────────────────┐
                               │  App Service Plan (B1)   │
                               │  ┌────────────────────┐  │
  Browser ◄── HTTPS ──────────►│  │   myapp (prod)     │  │
                               │  │   Python 3.12      │  │
                               │  └────────────────────┘  │
                               │  ┌────────────────────┐  │
  Tester ◄── HTTPS ───────────►│  │   myapp (staging)  │  │
                               │  │   Python 3.12      │  │
                               │  └────────────────────┘  │
                               │          ↕ SWAP          │
                               └──────────────────────────┘
```

> ⚠️ **Gotcha:** Free/Shared tiers have no SLA, no custom domains with SSL, and no deployment slots. Use **B1** minimum for real apps, **S1+** for production (deployment slots, auto-scale).

---

## 1.4 Azure Functions

**What is it?** Run small pieces of code without managing any server. You write a function, tell Azure what triggers it (HTTP request, timer, file upload), and Azure runs it on demand. You pay only when it executes — literally per-second billing.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Trigger** | What starts the function (HTTP, Timer, Blob upload, Queue message) |
| **Binding** | Automatic connection to input/output data (read from DB, write to Queue) |
| **Consumption Plan** | Pay-per-execution, auto-scales 0→200 instances, has cold starts |
| **Premium Plan** | Always-warm instances, no cold start, VNet support |
| **Cold Start** | Delay (1-10 sec) when function hasn't run recently on Consumption plan |

**Input → Output:**

```
  You give it:  Function code + trigger type + binding config
  It gives you: An endpoint/scheduler that runs your code on demand, scales automatically
```

**Use cases:**
1. Webhook receiver (GitHub, Stripe, Slack events)
2. Scheduled cleanup jobs (cron: "delete old records every night")
3. File processing (resize image when uploaded to Blob)
4. API backend (lightweight REST endpoints)

**Example:**

```bash
# Create a Function App
az functionapp create \
    --name func-demo-2024 --resource-group rg-demo \
    --storage-account stdemo2024 \
    --consumption-plan-location eastus \
    --runtime python --runtime-version 3.12 \
    --functions-version 4 --os-type Linux

# Deploy function code
func azure functionapp publish func-demo-2024

# List functions
az functionapp function list \
    --name func-demo-2024 --resource-group rg-demo -o table
```

```python
# Example: HTTP trigger function (Python)
import azure.functions as func
import json

app = func.FunctionApp()

@app.route(route="hello", methods=["GET"])
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name", "World")
    return func.HttpResponse(json.dumps({"message": f"Hello, {name}!"}))

# Trigger: GET /api/hello?name=Azure
# Output:  {"message": "Hello, Azure!"}
```

**Diagram:**

```
  Triggers:                    Azure Functions              Outputs:
  ─────────                    ───────────────              ────────
  HTTP Request ──────┐                              ┌────► Blob Storage
  Timer (cron)  ─────┤   ┌───────────────────┐     ├────► Queue Message
  Blob Upload ───────┼──►│  Your Function     │─────┼────► Database
  Queue Message ─────┤   │  (runs on demand)  │     ├────► Email (SendGrid)
  Event Grid ────────┘   └───────────────────┘     └────► Slack Webhook
```

> ⚠️ **Gotcha:** Consumption plan has a **5-minute default timeout** (max 10 min). For long-running tasks, use Premium plan (no timeout) or Durable Functions (chaining).

---

## 1.5 Azure Container Instances (ACI)

**What is it?** Run a Docker container instantly without managing any server or cluster. Just give Azure a container image — it runs it in seconds. Perfect for quick one-off jobs. Think of it as "serverless containers."

**Key terms:**

| Term | Meaning |
|------|---------|
| **Container Group** | One or more containers that share network and storage (like a K8s Pod) |
| **Restart Policy** | Always (keep running), OnFailure (retry crashes), Never (run once and stop) |
| **Sidecar** | A helper container that runs alongside your main container in the same group |

**Input → Output:**

```
  You give it:  Container image + CPU/RAM + environment variables
  It gives you: A running container with an IP address in seconds, per-second billing
```

**Use cases:**
1. Database migrations (run once, throw away)
2. CI/CD build agents
3. Batch data processing jobs
4. Quick testing of container images

**Example:**

```bash
# Run a container (Nginx)
az container create \
    --resource-group rg-demo \
    --name ci-nginx-test \
    --image nginx:alpine \
    --cpu 1 --memory 1 \
    --ports 80 \
    --ip-address Public \
    --restart-policy Never

# Check logs
az container logs --resource-group rg-demo --name ci-nginx-test

# See status
az container show --resource-group rg-demo --name ci-nginx-test \
    --query "{Status:provisioningState, IP:ipAddress.ip}" -o table

# Delete when done
az container delete --resource-group rg-demo --name ci-nginx-test --yes
```

**Diagram:**

```
  ┌──────────────────────────────────┐
  │  Container Group (ACI)           │
  │  IP: 20.50.x.x                  │
  │                                  │
  │  ┌─────────┐    ┌─────────┐    │
  │  │  Main    │    │ Sidecar │    │
  │  │  App     │◄──►│ (logs)  │    │    ← Share network (localhost)
  │  │  :80     │    │         │    │    ← Share volumes
  │  └─────────┘    └─────────┘    │
  │                                  │
  │  No VM to manage. Starts in ~5s │
  │  Billed per-second of runtime.  │
  └──────────────────────────────────┘
```

> ⚠️ **Gotcha:** ACI has no auto-scaling. It's designed for single-instance or small fixed workloads. For auto-scaling containers, use **Container Apps** or **AKS**.

---

## 1.6 Azure Kubernetes Service (AKS)

**What is it?** Azure's managed Kubernetes. You get a full K8s cluster where Azure manages the control plane (API server, etcd, scheduler) for free — you only pay for the worker nodes (VMs) that run your containers.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Control Plane** | The "brain" of K8s (API server, scheduler). Azure manages this for free |
| **Node Pool** | A group of VMs (nodes) that run your containers |
| **System Pool** | Nodes running K8s system components (CoreDNS, etc.) — at least 1 required |
| **User Pool** | Nodes for your application workloads |
| **Workload Identity** | Secure way for pods to access Azure services (replaces service principal secrets) |
| **Cluster Autoscaler** | Automatically adds/removes nodes based on pod scheduling needs |

**Input → Output:**

```
  You give it:  Node count + VM size + K8s version + network config
  It gives you: A fully working K8s cluster with kubectl access
```

**Use cases:**
1. Microservices architecture (10+ services)
2. Complex workloads needing service mesh, RBAC, network policies
3. Multi-team platform with namespace isolation
4. ML/AI workloads with GPU node pools

**Example:**

```bash
# Create an AKS cluster
az aks create \
    --resource-group rg-demo \
    --name aks-demo \
    --node-count 2 \
    --node-vm-size Standard_D2s_v5 \
    --enable-managed-identity \
    --generate-ssh-keys

# Get kubectl credentials
az aks get-credentials --resource-group rg-demo --name aks-demo

# Verify
kubectl get nodes

# Add a user node pool
az aks nodepool add \
    --resource-group rg-demo --cluster-name aks-demo \
    --name apppool --node-count 3 \
    --node-vm-size Standard_D4s_v5 --mode User

# Scale nodes
az aks scale --resource-group rg-demo --name aks-demo --node-count 5

# Attach ACR (so AKS can pull images)
az aks update --resource-group rg-demo --name aks-demo \
    --attach-acr myacr
```

**Diagram:**

```
  ┌──────────────────────────────────────────────────┐
  │  AKS Cluster                                     │
  │                                                  │
  │  ┌──────────────────────┐  ← Azure manages this │
  │  │  Control Plane (FREE)│     (no VM access)     │
  │  │  API Server + etcd   │                        │
  │  └──────────┬───────────┘                        │
  │             │                                    │
  │  ┌──────────▼───────────┐  ← You pay for these  │
  │  │  System Node Pool    │                        │
  │  │  node01, node02      │  (K8s system pods)     │
  │  └──────────────────────┘                        │
  │  ┌──────────────────────┐                        │
  │  │  App Node Pool       │                        │
  │  │  node03, node04, 05  │  (your app pods)       │
  │  └──────────────────────┘                        │
  │  ┌──────────────────────┐                        │
  │  │  GPU Pool (optional) │                        │
  │  │  node06 (NC6s_v3)    │  (ML workloads)        │
  │  └──────────────────────┘                        │
  └──────────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** AKS supports N-2 Kubernetes versions only. If you fall behind on upgrades, you'll have to upgrade through every version sequentially. Upgrade staging first — breaking K8s API changes can kill your deployments.

---

## 1.7 Azure Container Apps

**What is it?** A fully managed platform to run containerized apps with auto-scaling, built on Kubernetes under the hood — but you never touch K8s directly. Think of it as "the simplicity of App Service, but for containers."

**Key terms:**

| Term | Meaning |
|------|---------|
| **Environment** | A shared boundary for Container Apps (like a lightweight K8s cluster) |
| **Revision** | An immutable snapshot of your app. New deployment = new revision |
| **Ingress** | Built-in HTTP/HTTPS endpoint for your app |
| **KEDA scaler** | Auto-scales based on events (queue length, HTTP traffic, cron) |
| **Dapr** | Built-in microservice framework for service-to-service calls, state, pub/sub |

**Input → Output:**

```
  You give it:  Container image + scaling rules + ingress config
  It gives you: A running app with HTTPS URL, auto-scaling 0→N, per-second billing
```

**Use cases:**
1. Microservices without K8s complexity
2. Event-driven apps that scale to zero
3. Background queue processors
4. APIs that need auto-scaling

**Example:**

```bash
# Create a Container Apps environment
az containerapp env create \
    --name cae-demo --resource-group rg-demo \
    --location eastus

# Deploy a container app
az containerapp create \
    --name myapi --resource-group rg-demo \
    --environment cae-demo \
    --image nginx:alpine \
    --target-port 80 --ingress external \
    --min-replicas 0 --max-replicas 10

# Update with new image
az containerapp update \
    --name myapi --resource-group rg-demo \
    --image myacr.azurecr.io/myapi:v2
```

**Diagram:**

```
  ┌──────────────────────────────────────────────┐
  │  Container Apps Environment                  │
  │  (managed K8s underneath — you don't see it) │
  │                                              │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
  │  │ myapi    │  │ worker   │  │ frontend │ │
  │  │ (3 repl.)│  │ (0-10)   │  │ (2 repl.)│ │
  │  │ HTTPS ✓  │  │ Queue ✓  │  │ HTTPS ✓  │ │
  │  └──────────┘  └──────────┘  └──────────┘ │
  │                                              │
  │  Scale to ZERO when idle (no cost)          │
  │  Scale OUT on HTTP load or queue depth      │
  └──────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Container Apps doesn't give you `kubectl` access. If you need network policies, custom CRDs, or Helm charts — use AKS instead.

---

## 1.8 Azure Batch

**What is it?** Run large-scale parallel and high-performance computing (HPC) jobs. Azure creates a pool of VMs, distributes your tasks across them, and cleans up when done. Think of it as "rent 1000 VMs for 2 hours, process everything, then stop paying."

**Key terms:**

| Term | Meaning |
|------|---------|
| **Pool** | A set of VMs (nodes) that run your tasks |
| **Job** | A collection of tasks to run on the pool |
| **Task** | A single command or script to execute on one node |
| **Low-priority VMs** | Cheaper VMs that can be evicted (up to 80% discount) |

**Input → Output:**

```
  You give it:  A pool config + job definition + list of tasks
  It gives you: All tasks executed in parallel across many VMs, results in Blob Storage
```

**Use cases:**
1. Video rendering (each frame = one task)
2. Financial risk modeling (Monte Carlo simulations)
3. Genomics / scientific computing
4. Large-scale data transformation (ETL)

**Example:**

```bash
# Create a Batch account
az batch account create \
    --name batchdemo --resource-group rg-demo \
    --location eastus --storage-account stdemo2024

# Create a pool of 10 VMs
az batch pool create \
    --account-name batchdemo \
    --id render-pool --vm-size Standard_D4s_v5 \
    --target-dedicated-nodes 10 \
    --image "canonical:0001-com-ubuntu-server-jammy:22_04-lts"
```

> ⚠️ **Gotcha:** Batch pools keep running (and billing) until explicitly deleted. Always set auto-scale formulas or delete pools after jobs complete.

---

## 1.9 Azure Virtual Desktop (AVD)

**What is it?** A cloud-hosted Windows desktop you can access from any device. Companies use it to give employees a secure Windows environment without shipping physical laptops. Like "Remote Desktop, but managed by Azure."

**Key terms:**

| Term | Meaning |
|------|---------|
| **Host Pool** | A collection of session host VMs that users connect to |
| **Session Host** | A VM running Windows that serves user desktops |
| **Workspace** | The portal where users see their available desktops/apps |
| **FSLogix** | Profile management — stores user profiles in Azure Files for fast login |

**Input → Output:**

```
  You give it:  Host pool config + user assignments + VM image
  It gives you: A Windows desktop accessible via browser or RD client from anywhere
```

**Use cases:**
1. Remote work (employees access corporate desktop from home)
2. Contractor access (give temporary access without shipping laptops)
3. Call centers (shared desktops for shift workers)
4. Secure environments (data never leaves the cloud)

> ⚠️ **Gotcha:** AVD requires Microsoft 365 or Windows per-user licensing on top of VM costs. Factor this into budgeting.

---

## 1.10 Azure Spring Apps

**What is it?** A fully managed platform specifically for Java Spring Boot applications. You deploy your `.jar` file — Azure handles infrastructure, scaling, monitoring, and Spring-specific tooling.

**Input → Output:**

```
  You give it:  Spring Boot JAR + config
  It gives you: A running Spring app with built-in Eureka, Config Server, and monitoring
```

**Use cases:**
1. Enterprise Java microservices
2. Spring Boot APIs with service discovery
3. Java apps needing managed middleware (config server, gateway)

> ⚠️ **Gotcha:** Only supports Java/Spring. If you're not using Spring Boot, use App Service or Container Apps instead.

---

## 1.11 Azure Service Fabric

**What is it?** Microsoft's microservices platform (predates AKS). Used internally by Azure itself to run services like Cosmos DB, SQL Database, and Cortana. It manages stateful and stateless services on a cluster of VMs.

**Input → Output:**

```
  You give it:  Application package + cluster config
  It gives you: A managed cluster running your microservices with built-in state management
```

**Use cases:**
1. Stateful microservices (service maintains its own data)
2. Actor-based programming model
3. Legacy Microsoft workloads already on Service Fabric

> ⚠️ **Gotcha:** Service Fabric is losing mindshare to AKS and Container Apps. For new projects, prefer AKS (Kubernetes) or Container Apps unless you specifically need Service Fabric's stateful programming model.

---

## 1.12 Compute Decision Guide

**Which compute service should I pick?**

```
  START HERE
     │
     ▼
  Do you need full OS control? ─── YES ──► Azure VM / VMSS
     │ NO
     ▼
  Is it a container? ─── YES ──┐
     │ NO                       │
     ▼                          ▼
  Is it a web app ─── YES     Need K8s features? ─── YES ──► AKS
  or API?              │       │ NO
     │ NO              │       ▼
     ▼                 │     Need simple auto-scale? ──► Container Apps
  Is it event- ──YES──►│       │ NO
  driven / cron?       │       ▼
     │                 │     One-off job? ──► ACI
     ▼                 │
  Azure Functions      ▼
                    App Service
```

**Quick comparison table:**

```
  ┌──────────────┬────────┬────────┬──────────┬──────────┬─────────┐
  │              │   VM   │  VMSS  │ App Svc  │  AKS     │Functions│
  ├──────────────┼────────┼────────┼──────────┼──────────┼─────────┤
  │ You manage   │ Everything│ Less │ Code only│ Manifests│Code only│
  │ Auto-scale   │   No   │  Yes   │   Yes    │   Yes    │  Yes    │
  │ Scale to 0   │   No   │  No    │   No     │   No     │  Yes    │
  │ Container    │   No   │  No    │  Yes*    │   Yes    │  Yes    │
  │ Min cost/mo  │  ~$15  │  ~$30  │   $13    │  ~$70    │  Free** │
  │ Best for     │ Legacy │ Fleets │ Web apps │ Micro-svc│ Events  │
  └──────────────┴────────┴────────┴──────────┴──────────┴─────────┘

  * App Service supports Docker containers
  ** Consumption plan: 1M free executions/month

  ┌──────────────┬────────────┬──────────────┬──────────────┐
  │              │ Cont. Apps │   ACI        │   Batch      │
  ├──────────────┼────────────┼──────────────┼──────────────┤
  │ You manage   │ Image only │ Image only   │ Pool config  │
  │ Auto-scale   │ Yes (KEDA) │ No           │ Yes          │
  │ Scale to 0   │ Yes        │ N/A          │ Yes          │
  │ Best for     │ Simple µsvc│ One-off jobs │ HPC / batch  │
  └──────────────┴────────────┴──────────────┴──────────────┘
```

> **Rule of thumb:** Start with the MOST managed option (rightmost in the spectrum). Move left only when you hit a limitation.

---

# Chapter 2 — Azure Networking Services

> **Networking** = how your resources talk to each other, to the internet, and to on-prem. Azure networking is the backbone of every architecture.

```
  AZURE NETWORKING — BIG PICTURE
  ─────────────────────────────────────────────────────────────────
  Internet ──► Front Door / CDN ──► App Gateway / LB ──► VNet
                                                           │
                  ┌────────────────────────────────────────┤
                  │                                        │
              Subnet A                                 Subnet B
              (Web VMs)                                (DB VMs)
              NSG: allow 80,443                        NSG: allow 1433
                  │                                        │
                  └────────── VNet Peering ─────────────────┘
                                    │
                              VPN Gateway ──► On-Prem Datacenter
```

---

## 2.1 Virtual Network (VNet)

**What is it?** Your own private network in Azure. It's like having your own building with rooms (subnets) — resources inside can talk to each other, but the outside world can't get in unless you open doors.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Address space** | The IP range for the whole VNet (e.g., 10.0.0.0/16 = 65,536 IPs) |
| **CIDR notation** | Shorthand for IP ranges. /16 = large, /24 = 256 IPs, /28 = 16 IPs |
| **Region-bound** | A VNet lives in ONE Azure region. Cross-region needs peering |
| **Isolation** | VNets are isolated by default — two VNets can't talk without peering |

**Input → Output:**

```
  You give it:  Address space (e.g., 10.0.0.0/16) + region
  It gives you: A private network where Azure resources get private IPs
```

**Use cases:**
1. Isolate production from dev environments
2. Host VMs, AKS, databases on private IPs
3. Connect to on-prem via VPN or ExpressRoute
4. Create DMZ architectures

**Example:**

```bash
# Create a VNet with two subnets
az network vnet create \
    --resource-group rg-demo --name vnet-main \
    --address-prefix 10.0.0.0/16 \
    --subnet-name snet-web --subnet-prefix 10.0.1.0/24 \
    --location eastus

# Add another subnet
az network vnet subnet create \
    --resource-group rg-demo --vnet-name vnet-main \
    --name snet-db --address-prefix 10.0.2.0/24

# List VNets
az network vnet list -g rg-demo -o table
```

**Diagram:**

```
  ┌─────────────────────────────────────────┐
  │  VNet: vnet-main (10.0.0.0/16)         │
  │                                         │
  │  ┌─────────────────┐  ┌──────────────┐ │
  │  │ snet-web         │  │ snet-db      │ │
  │  │ 10.0.1.0/24      │  │ 10.0.2.0/24  │ │
  │  │                   │  │              │ │
  │  │ [VM: 10.0.1.4]   │  │ [DB: 10.0.2.4]│ │
  │  │ [VM: 10.0.1.5]   │  │              │ │
  │  └─────────────────┘  └──────────────┘ │
  │                                         │
  │  VMs in snet-web CAN talk to snet-db   │
  │  (same VNet = automatic routing)        │
  └─────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** VNet address spaces can't overlap if you want to peer them. Plan your IP ranges upfront. Use 10.x.0.0/16 blocks and assign each VNet a unique second octet (10.1.0.0/16, 10.2.0.0/16, etc.).

---

## 2.2 Subnets

**What is it?** A subdivision of a VNet. Like rooms inside a building — each subnet gets a slice of the VNet's IP range, and you can apply different security rules to each.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Subnet delegation** | Reserves a subnet for a specific Azure service (e.g., App Service, ACI) |
| **Reserved IPs** | Azure reserves 5 IPs per subnet (.0 network, .1 gateway, .2-.3 DNS, .255 broadcast) |
| **NSG association** | You attach an NSG to a subnet to filter traffic for all resources in it |

**Input → Output:**

```
  You give it:  A CIDR range within the VNet + optional NSG + optional delegation
  It gives you: An isolated network segment where you place resources
```

**Use cases:**
1. Separate web tier, app tier, database tier
2. Dedicate subnets for AKS, App Service, Bastion
3. Apply different firewall rules per subnet
4. Isolate sensitive workloads (PCI, HIPAA)

**Example:**

```bash
# Create a subnet with NSG
az network vnet subnet create \
    --resource-group rg-demo --vnet-name vnet-main \
    --name snet-app --address-prefix 10.0.3.0/24 \
    --network-security-group nsg-app

# Delegate subnet to App Service
az network vnet subnet update \
    --resource-group rg-demo --vnet-name vnet-main \
    --name snet-appservice \
    --delegations Microsoft.Web/serverFarms
```

> ⚠️ **Gotcha:** A /24 subnet gives 251 usable IPs (256 - 5 reserved). For AKS with Azure CNI, plan bigger (/20 or /21) because every pod gets a VNet IP.

---

## 2.3 Network Security Groups (NSG)

**What is it?** A firewall for your subnets and NICs. It contains a list of rules that say "allow" or "deny" traffic based on source, destination, port, and protocol. Think of it as a bouncer at the door.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Inbound rule** | Controls traffic coming IN to the resource |
| **Outbound rule** | Controls traffic going OUT from the resource |
| **Priority** | Lower number = processed first (100-4096). First match wins |
| **Service tag** | Named group of IPs (e.g., `Internet`, `AzureLoadBalancer`, `Storage`) |
| **ASG** | Application Security Group — tag VMs by role instead of IP |

**Input → Output:**

```
  You give it:  Allow/Deny + Source + Destination + Port + Protocol + Priority
  It gives you: Traffic filtering at the subnet or NIC level
```

**Use cases:**
1. Allow only port 443 (HTTPS) from internet to web VMs
2. Block all internet access from database subnet
3. Allow SSH only from your office IP
4. Restrict inter-subnet traffic

**Example:**

```bash
# Create an NSG
az network nsg create --resource-group rg-demo --name nsg-web

# Allow HTTPS inbound from internet
az network nsg rule create \
    --resource-group rg-demo --nsg-name nsg-web \
    --name AllowHTTPS --priority 100 \
    --direction Inbound --access Allow \
    --protocol Tcp --destination-port-ranges 443 \
    --source-address-prefixes Internet

# Deny all other inbound
az network nsg rule create \
    --resource-group rg-demo --nsg-name nsg-web \
    --name DenyAllInbound --priority 4000 \
    --direction Inbound --access Deny \
    --protocol '*' --destination-port-ranges '*' \
    --source-address-prefixes '*'

# Attach NSG to subnet
az network vnet subnet update \
    --resource-group rg-demo --vnet-name vnet-main \
    --name snet-web --network-security-group nsg-web

# List rules
az network nsg rule list -g rg-demo --nsg-name nsg-web -o table
```

**Diagram:**

```
  Internet ──────────────────────────────────────────────────┐
       │                                                     │
       ▼                                                     ▼
  ┌──────────┐    ┌────────────────────────────┐     ┌──────────┐
  │ NSG      │    │   Rules (processed in      │     │ NSG      │
  │ (snet-web)│    │   order of priority):      │     │ (snet-db)│
  │          │    │                            │     │          │
  │ Allow 443│◄──│ 100: Allow HTTPS (443)     │     │ Deny ALL │
  │ Allow 80 │    │ 200: Allow HTTP (80)       │     │ from     │
  │ Deny rest│    │ 4000: Deny everything else │     │ internet │
  └──────────┘    └────────────────────────────┘     └──────────┘
```

> ⚠️ **Gotcha:** NSG rules are stateful — if you allow inbound traffic, the response is automatically allowed out. But you still need to allow outbound for NEW connections (e.g., apt update needs outbound 80/443).

---

## 2.4 Network Interface Card (NIC)

**What is it?** The virtual network adapter that connects a VM to a VNet. Every VM has at least one NIC. The NIC holds the VM's private IP, optional public IP, and NSG association.

**Input → Output:**

```
  You give it:  Subnet + IP configuration + optional public IP + optional NSG
  It gives you: A network connection for your VM with private and/or public IP
```

**Use cases:**
1. Assign multiple NICs to a VM (e.g., one for app traffic, one for management)
2. Move a NIC between VMs (keep the same IP)
3. Attach an NSG at NIC level for per-VM rules

**Example:**

```bash
# Create a NIC
az network nic create \
    --resource-group rg-demo --name nic-vm01 \
    --vnet-name vnet-main --subnet snet-web \
    --network-security-group nsg-web

# List NICs
az network nic list -g rg-demo -o table

# Show IP config
az network nic ip-config list --resource-group rg-demo --nic-name nic-vm01 -o table
```

> ⚠️ **Gotcha:** Deleting a VM does NOT auto-delete its NIC, public IP, or disk. These become "orphaned resources" that still cost money.

---

## 2.5 Public IP Addresses

**What is it?** An IP address reachable from the internet. You attach it to a VM, Load Balancer, or other resource to make it internet-accessible.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Static** | IP never changes (even if resource is stopped). Costs ~$4/month |
| **Dynamic** | IP may change if resource is deallocated. Free when attached |
| **SKU: Basic** | Legacy, no availability zone support |
| **SKU: Standard** | Zone-redundant, required for Standard LB. Always static |

**Input → Output:**

```
  You give it:  SKU (Basic/Standard) + static/dynamic + region
  It gives you: A public IP you can attach to VMs, LBs, App Gateways, Bastion
```

**Example:**

```bash
# Create a static Standard public IP
az network public-ip create \
    --resource-group rg-demo --name pip-web01 \
    --sku Standard --allocation-method Static

# List public IPs
az network public-ip list -g rg-demo -o table
```

> ⚠️ **Gotcha:** Unattached public IPs cost money (~$4/month). Delete them if not in use. Standard SKU IPs are zone-redundant — always prefer Standard over Basic.

---

## 2.6 Azure Load Balancer

**What is it?** Distributes incoming traffic across multiple VMs. It works at Layer 4 (TCP/UDP) — it doesn't understand HTTP, just forwards packets. Like a traffic cop directing cars to different lanes.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Frontend IP** | The IP that clients connect to |
| **Backend pool** | The group of VMs that receive traffic |
| **Health probe** | Checks if VMs are alive (e.g., TCP ping on port 80 every 15 sec) |
| **Load balancing rule** | Maps frontend port → backend port (e.g., :80 → :80) |
| **Internal LB** | Private IP only (for internal services). External LB = public IP |

**Input → Output:**

```
  You give it:  Frontend IP + backend VMs + health probe + routing rule
  It gives you: Traffic evenly distributed across healthy VMs
```

**Use cases:**
1. Distribute web traffic across VM Scale Set
2. Internal load balancer for database read replicas
3. HA for any TCP/UDP service (RDP, SSH, custom protocols)

**Example:**

```bash
# Create a public load balancer
az network lb create \
    --resource-group rg-demo --name lb-web \
    --sku Standard --frontend-ip-name fe-web \
    --backend-pool-name pool-web \
    --public-ip-address pip-lb-web

# Add health probe
az network lb probe create \
    --resource-group rg-demo --lb-name lb-web \
    --name hp-http --protocol Http \
    --port 80 --path /health

# Add LB rule (port 80 → port 80)
az network lb rule create \
    --resource-group rg-demo --lb-name lb-web \
    --name rule-http --protocol Tcp \
    --frontend-port 80 --backend-port 80 \
    --frontend-ip-name fe-web \
    --backend-pool-name pool-web \
    --probe-name hp-http
```

**Diagram:**

```
        Internet
           │
     ┌─────▼─────┐
     │ Public IP  │  20.50.x.x:80
     │  (LB)     │
     └─────┬─────┘
           │ Health probe: /health every 15s
     ┌─────▼─────────────────────────┐
     │ Backend Pool                  │
     │                               │
     │  ┌──────┐ ┌──────┐ ┌──────┐ │
     │  │ VM-1 │ │ VM-2 │ │ VM-3 │ │   ← Traffic split 33/33/33
     │  │ :80  │ │ :80  │ │ :80  │ │
     │  │  ✓   │ │  ✓   │ │  ✗   │ │   ← VM-3 unhealthy, skipped
     │  └──────┘ └──────┘ └──────┘ │
     └───────────────────────────────┘
```

> ⚠️ **Gotcha:** Azure LB is Layer 4 only — no URL routing, no SSL termination, no WAF. For HTTP/HTTPS features, use **Application Gateway** (L7).

---

## 2.7 Application Gateway

**What is it?** A Layer 7 (HTTP/HTTPS) load balancer. Unlike the basic Load Balancer, it understands URLs, can route `/api/*` to one backend and `/images/*` to another, and includes a Web Application Firewall (WAF).

**Key terms:**

| Term | Meaning |
|------|---------|
| **URL-based routing** | Route requests by URL path (e.g., /api → backend A, /web → backend B) |
| **SSL termination** | App Gateway handles HTTPS, backends receive plain HTTP |
| **WAF** | Web Application Firewall — blocks SQL injection, XSS, OWASP Top 10 |
| **Listener** | Listens on a port+protocol (e.g., HTTPS:443) |
| **Backend pool** | VMs, VMSS, App Service, or IPs that receive routed traffic |

**Input → Output:**

```
  You give it:  HTTPS listener + URL routing rules + backend pools + optional WAF
  It gives you: Smart HTTP routing with SSL offloading and attack protection
```

**Use cases:**
1. Multi-site hosting (host1.com → pool A, host2.com → pool B)
2. Path-based routing (/api → API servers, /static → CDN)
3. WAF protection for web applications
4. SSL termination (offload HTTPS to gateway)

**Example:**

```bash
# Create an Application Gateway (simplified)
az network application-gateway create \
    --resource-group rg-demo --name ag-web \
    --sku WAF_v2 --capacity 2 \
    --vnet-name vnet-main --subnet snet-agw \
    --public-ip-address pip-agw \
    --http-settings-port 80 --http-settings-protocol Http \
    --frontend-port 443 --routing-rule-type Basic
```

**Diagram:**

```
  Client (HTTPS) ─────────────────────────────────────┐
         │                                             │
   ┌─────▼────────────────────────────────────────┐   │
   │  Application Gateway (Layer 7)               │   │
   │                                              │   │
   │  SSL Cert ──► Terminate HTTPS               │   │
   │  WAF ──► Block SQL injection, XSS           │   │
   │                                              │   │
   │  URL Routing:                                │   │
   │  /api/*    ──► Backend Pool: API Servers     │   │
   │  /images/* ──► Backend Pool: CDN / Storage   │   │
   │  /*        ──► Backend Pool: Web Servers     │   │
   └──────────────────────────────────────────────┘   │
```

> ⚠️ **Gotcha:** App Gateway requires its own **dedicated subnet** (can't share with VMs). Use at least /24. Also, App Gateway v2 takes 5-10 minutes to provision.

---

## 2.8 Azure Front Door

**What is it?** A global Layer 7 load balancer + CDN + WAF. Unlike App Gateway (regional), Front Door works across the entire planet — it routes users to the closest healthy backend anywhere in the world.

**Key terms:**

| Term | Meaning |
|------|---------|
| **POP** | Point of Presence — edge servers worldwide (200+ locations) |
| **Origin group** | A group of backends (App Service, VM, storage) in different regions |
| **Health probe** | Checks if each origin is healthy (auto-failover if not) |
| **Caching** | Caches static content at edge POPs for fast delivery |

**Input → Output:**

```
  You give it:  Custom domain + origin groups (backends in multiple regions) + WAF policy
  It gives you: Global load balancing with auto-failover, CDN caching, DDoS + WAF
```

**Use cases:**
1. Multi-region web apps (East US + West Europe)
2. Global CDN for static assets
3. Instant failover when a region goes down
4. Global WAF protection

**Diagram:**

```
  Users worldwide
  ┌──────┐  ┌──────┐  ┌──────┐
  │ Asia │  │ Europe│  │ US   │
  └──┬───┘  └──┬───┘  └──┬───┘
     │         │         │
     ▼         ▼         ▼
  ┌─────────────────────────────┐
  │     Azure Front Door        │  ← Global edge network
  │  (CDN + WAF + LB)          │
  └──┬──────────┬───────────┬──┘
     │          │           │
     ▼          ▼           ▼
  Origin 1   Origin 2   Origin 3
  (East US)  (W Europe) (SE Asia)
```

> ⚠️ **Gotcha:** Front Door is for HTTP/HTTPS only. For TCP/UDP global load balancing, use **Traffic Manager** + **Load Balancer**.

---

## 2.9 Azure DNS

**What is it?** Host your DNS zones in Azure. It translates domain names (myapp.com) into IP addresses. You manage DNS records (A, CNAME, MX, TXT) via Azure Portal or CLI.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Public DNS zone** | Resolves names from the internet (myapp.com → 20.50.1.1) |
| **Private DNS zone** | Resolves names only inside your VNet (db.internal → 10.0.2.4) |
| **A record** | Maps name → IPv4 address |
| **CNAME record** | Maps name → another name (alias) |
| **TTL** | Time To Live — how long DNS resolvers cache the answer |

**Input → Output:**

```
  You give it:  Domain name + DNS records (A, CNAME, MX, etc.)
  It gives you: Name resolution — your domain resolves to your Azure resources
```

**Example:**

```bash
# Create a public DNS zone
az network dns zone create \
    --resource-group rg-demo --name myapp.com

# Add an A record
az network dns record-set a add-record \
    --resource-group rg-demo --zone-name myapp.com \
    --record-set-name www --ipv4-address 20.50.1.1

# Create a private DNS zone
az network private-dns zone create \
    --resource-group rg-demo --name internal.myapp.com

# Link private DNS zone to VNet
az network private-dns link vnet create \
    --resource-group rg-demo --zone-name internal.myapp.com \
    --name link-vnet-main --virtual-network vnet-main \
    --registration-enabled true
```

> ⚠️ **Gotcha:** Private DNS zones need to be **linked to a VNet** to work. Forgetting this link is the #1 reason Private Endpoints fail to resolve.

---

## 2.10 VNet Peering

**What is it?** Connects two VNets so resources in both can communicate using private IPs. Traffic flows through Microsoft's backbone (not the internet). Like building a hallway between two buildings.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Regional peering** | Both VNets in the same region (free) |
| **Global peering** | VNets in different regions (small cost per GB) |
| **Non-transitive** | VNet A↔B and B↔C does NOT mean A↔C. You must peer A↔C separately |
| **Gateway transit** | One VNet's VPN gateway can be shared with the peered VNet |

**Input → Output:**

```
  You give it:  Two VNet IDs + peering settings
  It gives you: Private, low-latency connectivity between the VNets
```

**Example:**

```bash
# Peer VNet-A with VNet-B (must create both directions)
az network vnet peering create \
    --resource-group rg-demo --name peer-A-to-B \
    --vnet-name vnet-A --remote-vnet vnet-B \
    --allow-vnet-access true

az network vnet peering create \
    --resource-group rg-demo --name peer-B-to-A \
    --vnet-name vnet-B --remote-vnet vnet-A \
    --allow-vnet-access true

# Verify
az network vnet peering list -g rg-demo --vnet-name vnet-A -o table
```

**Diagram:**

```
  ┌──────────────────┐         ┌──────────────────┐
  │ VNet-A (East US) │         │ VNet-B (East US) │
  │ 10.1.0.0/16      │◄──────►│ 10.2.0.0/16      │
  │                  │ Peering │                  │
  │ [VM: 10.1.1.4]  │         │ [VM: 10.2.1.4]  │
  └──────────────────┘         └──────────────────┘

  10.1.1.4 can ping 10.2.1.4 via private backbone
  No internet. No VPN. Just fast, direct connectivity.

  ⚠️ NON-TRANSITIVE:
  VNet-A ↔ VNet-B ✓
  VNet-B ↔ VNet-C ✓
  VNet-A ↔ VNet-C ✗  (need separate peering!)
```

> ⚠️ **Gotcha:** VNet address spaces MUST NOT overlap for peering. You can't peer 10.0.0.0/16 with 10.0.0.0/16. Plan your IP ranges from day one.

---

## 2.11 VPN Gateway

**What is it?** Connects your Azure VNet to your on-premises network over an encrypted IPsec tunnel through the public internet. Like a secure tunnel between your office and the cloud.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Site-to-Site (S2S)** | Permanent tunnel: on-prem datacenter ↔ Azure VNet |
| **Point-to-Site (P2S)** | Individual laptop ↔ Azure VNet (remote worker VPN) |
| **Gateway subnet** | A dedicated subnet (named `GatewaySubnet`) for the VPN gateway |
| **Local network gateway** | Represents your on-prem network in Azure (IP + address ranges) |
| **IKEv2/IPsec** | The encryption protocols used for the tunnel |

**Input → Output:**

```
  You give it:  Gateway subnet + on-prem public IP + shared key
  It gives you: Encrypted tunnel — on-prem machines can reach Azure private IPs
```

**Use cases:**
1. Connect office network to Azure VNet
2. Remote workers access Azure resources securely
3. Hybrid cloud — some services on-prem, some in Azure

**Example:**

```bash
# Create the gateway subnet (MUST be named GatewaySubnet)
az network vnet subnet create \
    --resource-group rg-demo --vnet-name vnet-main \
    --name GatewaySubnet --address-prefix 10.0.255.0/27

# Create VPN gateway (takes 30-45 minutes!)
az network vnet-gateway create \
    --resource-group rg-demo --name vpngw-main \
    --vnet vnet-main --gateway-type Vpn \
    --vpn-type RouteBased --sku VpnGw1 \
    --public-ip-address pip-vpngw

# Create local network gateway (your on-prem)
az network local-gateway create \
    --resource-group rg-demo --name lgw-office \
    --gateway-ip-address 203.0.113.1 \
    --local-address-prefixes 192.168.0.0/16

# Create the S2S connection
az network vpn-connection create \
    --resource-group rg-demo --name conn-office \
    --vnet-gateway1 vpngw-main \
    --local-gateway2 lgw-office \
    --shared-key "MySecretKey123!"
```

**Diagram:**

```
  On-Premises                                    Azure
  ──────────                                    ─────
  ┌──────────────┐                        ┌──────────────┐
  │ Office       │    IPsec Tunnel        │ VNet         │
  │ 192.168.0.0  │◄═════════════════════►│ 10.0.0.0/16  │
  │              │    (encrypted,         │              │
  │ Firewall     │     over internet)     │ VPN Gateway  │
  │ 203.0.113.1  │                        │ 20.50.x.x   │
  └──────────────┘                        └──────────────┘
```

> ⚠️ **Gotcha:** VPN Gateway takes **30-45 minutes** to provision. The `GatewaySubnet` must be at least /27. For production, use VpnGw2 or higher (VpnGw1 maxes out at 650 Mbps).

---

## 2.12 ExpressRoute

**What is it?** A private, dedicated connection between your datacenter and Azure that does NOT go over the internet. It's faster, more reliable, and more secure than VPN — but costs significantly more ($200-10,000+/month).

**Input → Output:**

```
  You give it:  A circuit order with a connectivity provider (e.g., Equinix, AT&T)
  It gives you: A private 50Mbps-10Gbps link to Azure with <10ms latency
```

**Use cases:**
1. Financial services (low latency, high security)
2. Large data transfers (terabytes daily)
3. Compliance requirements (data can't traverse internet)
4. Hybrid apps needing consistent performance

**Diagram:**

```
  On-Premises          Provider Edge          Azure
  ──────────          ──────────────          ─────
  ┌──────────┐      ┌──────────────┐      ┌──────────┐
  │ Your DC  │──────│ Equinix/AT&T │──────│ Azure    │
  │          │ MPLS │ Meet-me      │ MSFT │ Edge     │
  │          │      │ location     │      │ Router   │
  └──────────┘      └──────────────┘      └──────────┘

  ✓ No internet involved
  ✓ 99.95% SLA
  ✓ Up to 100 Gbps
  ✗ Expensive ($$$)
  ✗ Weeks to provision
```

> ⚠️ **Gotcha:** ExpressRoute is NOT encrypted by default (it's a private circuit, not a VPN). For encryption, add VPN over ExpressRoute or use MACsec.

---

## 2.13 Azure Bastion

**What is it?** A managed jump server that lets you RDP/SSH into VMs through the Azure Portal browser — no public IP needed on VMs. It's the secure way to access VMs without exposing them to the internet.

**Input → Output:**

```
  You give it:  Bastion host in a VNet + VM in the same/peered VNet
  It gives you: Browser-based RDP/SSH to VMs via Azure Portal — no public IP required
```

**Use cases:**
1. Secure VM access without public IPs
2. Eliminate RDP/SSH exposure to internet (no port 3389/22 open)
3. Audit all VM access sessions
4. Access VMs from locked-down corporate networks

**Example:**

```bash
# Create Bastion subnet (MUST be named AzureBastionSubnet, /26 minimum)
az network vnet subnet create \
    --resource-group rg-demo --vnet-name vnet-main \
    --name AzureBastionSubnet --address-prefix 10.0.254.0/26

# Create Bastion host
az network bastion create \
    --resource-group rg-demo --name bast-main \
    --vnet-name vnet-main --public-ip-address pip-bastion \
    --sku Standard
```

**Diagram:**

```
  Admin (browser)
       │
       ▼  HTTPS (443)
  ┌──────────────┐
  │ Azure Bastion│  ← Managed by Azure
  │ (Public IP)  │  ← Only port 443 exposed
  └──────┬───────┘
         │  RDP/SSH (private network)
         ▼
  ┌──────────────┐
  │ VM (NO       │  ← No public IP!
  │  public IP)  │  ← No port 22/3389 open!
  └──────────────┘
```

> ⚠️ **Gotcha:** Bastion costs ~$140/month (Standard SKU). For dev/test, you might prefer a temporary public IP + NSG instead. For production, Bastion is the security best practice.

---

## 2.14 Azure Firewall

**What is it?** A managed, cloud-native network firewall. Unlike NSGs (which work at subnet/NIC level), Azure Firewall is a centralized firewall that controls traffic for the entire VNet, with URL filtering, threat intelligence, and FQDN rules.

**Key terms:**

| Term | Meaning |
|------|---------|
| **DNAT rule** | Destination NAT — forward incoming traffic to internal IPs |
| **Network rule** | Allow/deny by IP, port, protocol |
| **Application rule** | Allow/deny by FQDN (e.g., allow *.github.com) |
| **Threat intelligence** | Auto-block traffic from known malicious IPs |
| **Hub-spoke** | Architecture where firewall sits in a "hub" VNet, all traffic routes through it |

**Input → Output:**

```
  You give it:  Rules (DNAT + network + application) + VNet route tables
  It gives you: Centralized traffic inspection, filtering, and logging
```

**Diagram:**

```
  ┌──────────────────────────────────────────────────┐
  │  Hub VNet (10.0.0.0/16)                          │
  │                                                  │
  │  ┌────────────────────────┐                     │
  │  │  Azure Firewall        │                     │
  │  │  ├─ App rules (FQDN)  │                     │
  │  │  ├─ Network rules (IP) │                     │
  │  │  └─ DNAT rules        │                     │
  │  └───────────┬────────────┘                     │
  │              │                                   │
  └──────────────┼───────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
  Spoke VNet 1  Spoke VNet 2  Internet
  (Web apps)   (Databases)    (filtered)
```

> ⚠️ **Gotcha:** Azure Firewall costs ~$912/month minimum (Standard SKU). It's a premium service — use it for production environments that need centralized security. For simpler setups, NSGs are sufficient and free.

---

## 2.15 Private Link & Private Endpoints

**What is it?** Access Azure PaaS services (Storage, SQL, Key Vault) over a private IP inside your VNet instead of over the public internet. The traffic never leaves Microsoft's network.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Private Endpoint** | A NIC with a private IP in your VNet that represents an Azure service |
| **Private Link** | The underlying technology. Also lets you expose YOUR services privately |
| **Private DNS zone** | Resolves mydb.database.windows.net → private IP instead of public IP |

**Input → Output:**

```
  You give it:  Azure service (e.g., SQL DB) + subnet for the private endpoint
  It gives you: A private IP (10.0.x.x) that connects to the service — no internet
```

**Example:**

```bash
# Create private endpoint for Azure SQL
az network private-endpoint create \
    --resource-group rg-demo --name pe-sql \
    --vnet-name vnet-main --subnet snet-pe \
    --private-connection-resource-id $SQL_SERVER_ID \
    --group-ids sqlServer \
    --connection-name conn-sql

# Create private DNS zone and link
az network private-dns zone create \
    --resource-group rg-demo --name privatelink.database.windows.net

az network private-dns link vnet create \
    --resource-group rg-demo \
    --zone-name privatelink.database.windows.net \
    --name link-vnet-main --virtual-network vnet-main

# Disable public access on the SQL server
az sql server update --resource-group rg-demo --name sql-demo \
    --public-network-access Disabled
```

**Diagram:**

```
  WITHOUT Private Endpoint:           WITH Private Endpoint:
  ─────────────────────────           ──────────────────────

  App (VNet) ──► Internet ──► SQL    App (VNet) ──► PE (10.0.5.4) ──► SQL
                 (public IP)                        (private IP)
                 ⚠️ Exposed                         ✓ Never leaves VNet
```

> ⚠️ **Gotcha:** After creating a private endpoint, you MUST set up a Private DNS zone + link it to your VNet. Otherwise your app still resolves the public IP and can't connect.

---

## 2.16 Azure Traffic Manager

**What is it?** A DNS-based global load balancer. It routes users to the closest or healthiest endpoint by returning different IP addresses in DNS responses. Works at the DNS level (not packet level).

**Input → Output:**

```
  You give it:  Multiple endpoints (different regions) + routing method
  It gives you: DNS that resolves to the best endpoint (closest, healthiest, weighted)
```

**Routing methods:**

```
  Priority:     Always use Endpoint A. If A is down → use B
  Weighted:     70% of traffic → A, 30% → B (for gradual rollouts)
  Performance:  Route to nearest endpoint by latency
  Geographic:   Users in Europe → Europe endpoint, US → US endpoint
```

> ⚠️ **Gotcha:** Traffic Manager is DNS-only — the actual traffic flows directly from client to endpoint (not through Traffic Manager). DNS TTL means failover isn't instant (30-60 sec).

---

## 2.17 NAT Gateway

**What is it?** Provides outbound internet access for resources in a subnet through a single static public IP. Useful when VMs need to call external APIs but you want a predictable, fixed source IP.

**Input → Output:**

```
  You give it:  A public IP + association to a subnet
  It gives you: All outbound traffic from that subnet uses the NAT Gateway's IP
```

**Use cases:**
1. VMs need outbound internet but no inbound
2. External API requires IP whitelisting (fixed source IP)
3. Replace default Azure outbound connectivity

**Example:**

```bash
az network nat gateway create \
    --resource-group rg-demo --name natgw-main \
    --public-ip-addresses pip-natgw --idle-timeout 10

az network vnet subnet update \
    --resource-group rg-demo --vnet-name vnet-main \
    --name snet-app --nat-gateway natgw-main
```

> ⚠️ **Gotcha:** Azure is retiring default outbound access for VMs. New VMs created after Sept 2025 MUST have NAT Gateway, LB outbound rule, or Public IP for internet access.

---

## 2.18 Azure CDN

**What is it?** Content Delivery Network — caches your static content (images, CSS, JS) at edge servers worldwide so users get fast load times regardless of their location.

**Input → Output:**

```
  You give it:  Origin (Blob Storage, App Service, custom URL) + CDN profile
  It gives you: Content cached at 200+ edge locations, served from nearest POP
```

**Use cases:**
1. Static website hosting (images, CSS, JS)
2. Video/media streaming
3. Software download distribution
4. API response caching

> ⚠️ **Gotcha:** Azure CDN is being merged into Front Door. For new projects, use **Azure Front Door** (Standard/Premium) which includes CDN + WAF + global LB.

---

## 2.19 Service Endpoints

**What is it?** Extends your VNet identity to Azure PaaS services. Traffic still goes to the service's public IP, but the service sees it coming from your VNet and can allow/deny based on that. Simpler (and cheaper) than Private Endpoints.

**Input → Output:**

```
  You give it:  Subnet + service type (Microsoft.Storage, Microsoft.Sql, etc.)
  It gives you: PaaS service can restrict access to "only from this VNet/subnet"
```

**Service Endpoints vs Private Endpoints:**

```
  ┌────────────────────────┬────────────────────┬──────────────────────┐
  │                        │ Service Endpoints  │ Private Endpoints    │
  ├────────────────────────┼────────────────────┼──────────────────────┤
  │ Traffic path           │ Optimized route    │ Private IP in VNet   │
  │ DNS resolution         │ Still public IP    │ Private IP           │
  │ Cross-region           │ No                 │ Yes                  │
  │ On-prem access         │ No                 │ Yes (via VPN/ER)     │
  │ Cost                   │ Free               │ ~$7/month + data     │
  │ Setup complexity       │ Simple             │ More complex (DNS)   │
  └────────────────────────┴────────────────────┴──────────────────────┘

  Use Service Endpoints for: Simple VNet-to-PaaS restriction within same region
  Use Private Endpoints for: Full private access, cross-region, on-prem access
```

---

## 2.20 Network Watcher

**What is it?** Azure's network diagnostic and monitoring toolkit. It helps you troubleshoot connectivity issues, capture packets, view NSG flow logs, and verify routes.

**Input → Output:**

```
  You give it:  A source and destination (VM to VM, VM to internet)
  It gives you: Connectivity test results, route info, packet captures, flow logs
```

**Key tools:**

```bash
# Test if VM can reach a destination
az network watcher test-connectivity \
    --source-resource vm-web01 \
    --dest-address 10.0.2.4 --dest-port 1433

# Check effective NSG rules on a NIC
az network watcher show-security-group-view \
    --resource-group rg-demo --vm vm-web01

# Capture packets (like tcpdump in Azure)
az network watcher packet-capture create \
    --resource-group rg-demo --vm vm-web01 \
    --name capture01 --storage-account stdemo2024

# Check effective routes
az network nic show-effective-route-table \
    --resource-group rg-demo --name nic-vm01
```

> ⚠️ **Gotcha:** Network Watcher is auto-enabled per region but some features (NSG flow logs) need a storage account and can generate significant data costs. Set retention policies.

---

# Chapter 3 — Azure Identity & Access Management

> **Identity** = WHO are you? **Access** = WHAT can you do? Azure uses Microsoft Entra ID (formerly Azure AD) as the identity backbone for everything.

```
  IDENTITY & ACCESS — BIG PICTURE
  ────────────────────────────────────────────────────────
  WHO?                    HOW?                  WHAT?
  ────                    ────                  ─────
  Users              ──► Entra ID          ──► RBAC Role
  Groups             ──► (authenticates)   ──► (authorizes)
  Service Principals ──►                   ──► at a Scope
  Managed Identities ──►                   ──► (sub/rg/resource)
```

---

## 3.1 Microsoft Entra ID (Azure AD)

**What is it?** Azure's cloud-based identity service. It's the "gatekeeper" — every user, app, and service that wants to access Azure must prove their identity through Entra ID. It's NOT the same as on-prem Active Directory.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Tenant** | Your organization's dedicated Entra ID instance (one per company) |
| **Directory** | The database of users, groups, and apps inside a tenant |
| **User** | A person's identity (email + password + MFA) |
| **Group** | A collection of users (assign permissions to group, not individual users) |
| **Guest user (B2B)** | External person invited to your tenant (contractor, partner) |
| **App Registration** | An identity for an application (like a user account but for code) |

**Input → Output:**

```
  You give it:  Username + password + MFA
  It gives you: An authentication token (JWT) that proves who you are
```

**Use cases:**
1. User login to Azure Portal
2. Single Sign-On (SSO) for SaaS apps (Office 365, Salesforce)
3. App authentication (APIs calling Azure services)
4. B2B collaboration (invite external partners)

**Example:**

```bash
# List users in your tenant
az ad user list --query "[].{Name:displayName, UPN:userPrincipalName}" -o table

# Create a new user
az ad user create \
    --display-name "Jane Doe" \
    --user-principal-name jane@mycompany.onmicrosoft.com \
    --password "TempP@ss123!" --force-change-password-next-sign-in true

# Create a security group
az ad group create --display-name "DevOps-Team" --mail-nickname "devops-team"

# Add user to group
az ad group member add --group "DevOps-Team" --member-id <user-object-id>

# List groups
az ad group list --query "[].displayName" -o table
```

**Diagram:**

```
  ┌──────────────────────────────────────────────┐
  │  Entra ID Tenant (mycompany.onmicrosoft.com) │
  │                                              │
  │  Users:          Groups:        Apps:         │
  │  ├── alice@      ├── DevOps     ├── myapi    │
  │  ├── bob@        ├── Developers ├── portal   │
  │  └── jane@       └── Admins     └── cicd-sp  │
  │                                              │
  │  Guest Users (B2B):                          │
  │  └── contractor@external.com                 │
  └──────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Entra ID ≠ Windows Active Directory. Entra ID is cloud-native, uses OAuth2/OIDC protocols. On-prem AD uses Kerberos/LDAP. They can sync via Azure AD Connect, but they're different systems.

---

## 3.2 Azure RBAC

**What is it?** Role-Based Access Control — controls WHO can do WHAT on WHICH resources. You assign a **role** to a **principal** (user/group/SP) at a **scope** (subscription/resource group/resource).

**Key terms:**

| Term | Meaning |
|------|---------|
| **Role** | A set of permissions (e.g., "Reader" can view, "Contributor" can create/delete) |
| **Principal** | Who gets the role (user, group, service principal, managed identity) |
| **Scope** | Where the role applies (management group → subscription → resource group → resource) |
| **Assignment** | The combination: "Jane (principal) is Contributor (role) on rg-prod (scope)" |

**Built-in roles (most common):**

```
  ┌────────────────────┬──────────────────────────────────────────┐
  │ Role               │ What it can do                          │
  ├────────────────────┼──────────────────────────────────────────┤
  │ Owner              │ Everything + assign roles to others     │
  │ Contributor        │ Create/delete resources, can't assign   │
  │                    │ roles                                   │
  │ Reader             │ View only, no changes                   │
  │ User Access Admin  │ Only manage role assignments            │
  ├────────────────────┼──────────────────────────────────────────┤
  │ VM Contributor     │ Manage VMs only                         │
  │ Network Contrib.   │ Manage networking only                  │
  │ Storage Blob Reader│ Read blobs only                         │
  │ Key Vault Admin    │ Manage Key Vault secrets/keys/certs     │
  │ AKS Cluster Admin  │ Full admin on AKS clusters              │
  └────────────────────┴──────────────────────────────────────────┘
```

**Input → Output:**

```
  You give it:  Principal + Role + Scope
  It gives you: That principal can perform the role's actions at that scope
```

**Example:**

```bash
# Assign Contributor role to a user on a resource group
az role assignment create \
    --assignee jane@mycompany.com \
    --role "Contributor" \
    --resource-group rg-prod

# Assign Reader at subscription level
az role assignment create \
    --assignee "DevOps-Team" \
    --role "Reader" \
    --scope "/subscriptions/${SUB_ID}"

# List role assignments for a resource group
az role assignment list --resource-group rg-prod -o table

# Create a custom role
az role definition create --role-definition '{
    "Name": "VM Restarter",
    "Description": "Can restart VMs only",
    "Actions": ["Microsoft.Compute/virtualMachines/restart/action"],
    "AssignableScopes": ["/subscriptions/'${SUB_ID}'"]
}'
```

**Diagram:**

```
  SCOPE HIERARCHY (permissions inherit downward):

  Management Group
       │
       ├── Subscription (Production)
       │       │
       │       ├── rg-web ──── VM, App Service, LB
       │       │                  ↑
       │       │            Jane = Contributor HERE
       │       │            (can manage VM, App Svc, LB in rg-web)
       │       │
       │       └── rg-db ──── SQL DB, Redis
       │                      ↑
       │                Jane = NO access here
       │
       └── Subscription (Dev)
               └── rg-dev ──── everything
```

> ⚠️ **Gotcha:** Always use the **principle of least privilege** — give the narrowest role at the narrowest scope. Never assign Owner at subscription level unless absolutely necessary.

---

## 3.3 Managed Identities

**What is it?** An identity for your Azure resource (VM, App Service, Function) that lets it authenticate to other Azure services WITHOUT storing passwords or secrets. Azure creates and rotates the credentials automatically.

**Key terms:**

| Term | Meaning |
|------|---------|
| **System-assigned** | Tied to ONE resource. Deleted when resource is deleted. 1:1 relationship |
| **User-assigned** | Independent identity. Can be assigned to MULTIPLE resources. You manage lifecycle |

**Input → Output:**

```
  You give it:  Enable managed identity on a resource
  It gives you: The resource can call Azure APIs (Key Vault, Storage, SQL) with zero secrets
```

**Use cases:**
1. App Service reads secrets from Key Vault (no connection string needed)
2. VM pulls images from ACR
3. Azure Function writes to Blob Storage
4. AKS pods access Azure SQL

**Example:**

```bash
# Enable system-assigned identity on App Service
az webapp identity assign --name myapp --resource-group rg-prod

# Create a user-assigned identity
az identity create --name id-myapp --resource-group rg-prod

# Assign it to a VM
az vm identity assign \
    --name vm-web01 --resource-group rg-prod \
    --identities id-myapp

# Grant the identity access to Key Vault
az keyvault set-policy \
    --name kv-prod --resource-group rg-prod \
    --object-id $(az identity show -n id-myapp -g rg-prod --query principalId -o tsv) \
    --secret-permissions get list
```

**Diagram:**

```
  WITHOUT Managed Identity:          WITH Managed Identity:
  ──────────────────────────          ─────────────────────

  App Service                        App Service
      │                                  │
      │ Connection string:               │ "I am id-myapp"
      │ "AccountKey=abc123..."           │ (token from Entra ID)
      │ ⚠️ Secret stored in code!        │ ✓ No secrets anywhere!
      ▼                                  ▼
  Storage Account                    Storage Account
                                     (RBAC: id-myapp = Blob Reader)
```

> ⚠️ **Gotcha:** Always prefer **managed identities** over service principals with secrets. Managed identities = zero secret management, automatic rotation. Service principal secrets expire and can leak.

---

## 3.4 Service Principals

**What is it?** An identity for an external application (GitHub Actions, Jenkins, Terraform) to access Azure resources. It's like a "robot user account" for automation that lives outside Azure.

**Key terms:**

| Term | Meaning |
|------|---------|
| **App Registration** | Creates the identity in Entra ID |
| **Client ID** | The "username" of the service principal |
| **Client Secret** | The "password" (expires! Must be rotated) |
| **Federated Credential** | Passwordless authentication using OIDC (preferred over secrets) |

**Input → Output:**

```
  You give it:  App registration + client secret or federated credential
  It gives you: An identity that external tools can use to manage Azure resources
```

**Example:**

```bash
# Create a service principal with Contributor role
az ad sp create-for-rbac \
    --name sp-github-actions \
    --role Contributor \
    --scopes /subscriptions/${SUB_ID}/resourceGroups/rg-prod

# Output: appId, password, tenant (save these!)

# List service principals
az ad sp list --display-name sp-github-actions -o table

# Check when secret expires
az ad sp credential list --id <app-id> --query "[].endDateTime" -o table

# Add federated credential (passwordless, for GitHub Actions)
az ad app federated-credential create --id <app-id> --parameters '{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
}'
```

> ⚠️ **Gotcha:** Service principal secrets **expire** (default 1 year). Set calendar reminders. Better yet, switch to **federated credentials** (OIDC) — zero secrets to expire or leak.

---

## 3.5 Conditional Access

**What is it?** "If-then" policies for sign-in. Example: "IF user is signing in from outside the office, THEN require MFA." It adds security layers based on context (location, device, risk level).

**Input → Output:**

```
  You give it:  Conditions (who, where, what device) + controls (MFA, block, comply)
  It gives you: Dynamic security that adapts to sign-in risk
```

**Common policies:**

```
  Policy 1: Require MFA for all users
  Policy 2: Block sign-in from banned countries
  Policy 3: Require compliant device for accessing production
  Policy 4: Force password reset if sign-in risk is "High"
  Policy 5: Require MFA for admin roles (Owner, Contributor)
```

> ⚠️ **Gotcha:** Conditional Access requires **Entra ID P1 or P2** license (not free tier). Test policies in "Report-only" mode before enforcing — a misconfigured policy can lock out everyone, including admins.

---

## 3.6 Privileged Identity Management (PIM)

**What is it?** Just-in-time (JIT) access for privileged roles. Instead of being a permanent Owner, you "activate" the role when needed (for 1-8 hours) with approval. Like checking out a master key instead of keeping it permanently.

**Input → Output:**

```
  You give it:  User + eligible role + max duration + approval workflow
  It gives you: User can activate the role temporarily when needed, with full audit trail
```

**Example flow:**

```
  1. Jane is ELIGIBLE for "Contributor" on rg-prod
  2. Jane needs to deploy → requests activation in Portal
  3. Manager approves → Jane gets Contributor for 4 hours
  4. After 4 hours → role auto-deactivates
  5. Full audit log of who activated what, when, and why
```

> ⚠️ **Gotcha:** PIM requires **Entra ID P2** license. But it's essential for production — reduces the blast radius of compromised accounts.

---

# Chapter 4 — Azure Governance & Compliance

> **Governance** = rules that ensure your Azure environment stays organized, secure, and cost-controlled. Without governance, Azure becomes the Wild West.

---

## 4.1 Management Groups

**What is it?** A container ABOVE subscriptions for organizing and applying policies across multiple subscriptions. Like folders for your subscriptions.

**Input → Output:**

```
  You give it:  A hierarchy of management groups + policy assignments
  It gives you: Policies and RBAC that automatically apply to all subscriptions underneath
```

**Diagram:**

```
  Root Management Group
       │
       ├── mg-production
       │       ├── sub-prod-eastus
       │       └── sub-prod-westeu
       │       Policy: "Deny public IPs" → applies to BOTH subs
       │
       ├── mg-development
       │       ├── sub-dev
       │       └── sub-sandbox
       │       Policy: "Allow all regions" → applies to BOTH subs
       │
       └── mg-shared-services
               └── sub-shared (DNS, monitoring, networking)
```

**Example:**

```bash
# Create a management group
az account management-group create --name mg-production --display-name "Production"

# Move a subscription under it
az account management-group subscription add \
    --name mg-production --subscription $SUB_ID
```

---

## 4.2 Azure Policy

**What is it?** Automated rules that enforce standards on your Azure resources. "All VMs must use managed disks" or "No resources allowed in Brazil South region." Policies evaluate resources at creation and on an ongoing basis.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Policy definition** | The rule itself (JSON document) |
| **Policy assignment** | Applying the rule to a scope (subscription, RG) |
| **Effect** | What happens when rule is violated: Deny, Audit, DeployIfNotExists, Modify |
| **Initiative** | A group of related policies bundled together |
| **Compliance** | % of resources that pass the policy check |

**Input → Output:**

```
  You give it:  Policy definition + scope + effect
  It gives you: Automatic enforcement — non-compliant resources are blocked or flagged
```

**Example:**

```bash
# Assign built-in policy: "Allowed locations"
az policy assignment create \
    --name "restrict-locations" \
    --policy "e56962a6-4747-49cd-b67b-bf8b01975c4c" \
    --params '{"listOfAllowedLocations": {"value": ["eastus", "westus", "westeurope"]}}' \
    --scope "/subscriptions/${SUB_ID}"

# Assign built-in policy: "Require tag on resource groups"
az policy assignment create \
    --name "require-env-tag" \
    --policy "96670d01-0a4d-4649-9c89-2d3abc0a5025" \
    --params '{"tagName": {"value": "environment"}}' \
    --resource-group rg-prod

# Check compliance
az policy state summarize --resource-group rg-prod -o table
```

**Common policies:**

```
  ┌──────────────────────────────────────┬──────────────────────────┐
  │ Policy                               │ Effect                   │
  ├──────────────────────────────────────┼──────────────────────────┤
  │ Allowed locations                    │ Deny                     │
  │ Require tag on resource groups       │ Deny                     │
  │ VMs must use managed disks           │ Deny                     │
  │ Storage must use HTTPS               │ Deny                     │
  │ SQL must have TDE enabled            │ DeployIfNotExists         │
  │ Audit VMs without backup             │ Audit                    │
  │ Inherit tag from resource group      │ Modify                   │
  └──────────────────────────────────────┴──────────────────────────┘
```

> ⚠️ **Gotcha:** "Deny" policies block resource creation instantly. Test with "Audit" effect first to see what WOULD be blocked before switching to "Deny."

---

## 4.3 Azure Blueprints

**What is it?** A package of ARM templates + policies + RBAC + resource groups that you can deploy as a single unit to set up a new subscription consistently. Like a "starter kit" for new projects.

**Input → Output:**

```
  You give it:  Blueprint definition (templates + policies + roles)
  It gives you: A repeatable, auditable environment setup
```

> ⚠️ **Gotcha:** Azure Blueprints is being **deprecated** in favor of **Deployment Stacks** + **Template Specs**. For new projects, use Bicep with deployment stacks instead.

---

## 4.4 Resource Locks

**What is it?** A safety mechanism that prevents accidental deletion or modification of critical resources. Like a padlock on a door.

**Key terms:**

| Term | Meaning |
|------|---------|
| **CanNotDelete** | Can modify but NOT delete (most common for production) |
| **ReadOnly** | Can't modify OR delete (use for critical infra like VNet, DNS) |

**Example:**

```bash
# Add a delete lock on production resource group
az lock create --name lock-prod --lock-type CanNotDelete \
    --resource-group rg-prod --notes "Production - do not delete"

# Add read-only lock on VNet
az lock create --name lock-vnet --lock-type ReadOnly \
    --resource-group rg-prod --resource vnet-main \
    --resource-type Microsoft.Network/virtualNetworks

# List locks
az lock list --resource-group rg-prod -o table

# Delete a lock (only Owner can do this)
az lock delete --name lock-prod --resource-group rg-prod
```

> ⚠️ **Gotcha:** Locks are inherited. A lock on a resource group applies to ALL resources inside it. ReadOnly locks can break things unexpectedly (e.g., listing storage keys fails with ReadOnly lock).

---

## 4.5 Tags

**What is it?** Key-value labels you attach to resources for organization, cost tracking, and automation. Like sticky notes on your resources.

**Input → Output:**

```
  You give it:  Key=value pairs (e.g., environment=production, team=devops)
  It gives you: Ability to filter, group, and report on resources by tag
```

**Example:**

```bash
# Tag a resource group
az group update --name rg-prod \
    --tags environment=production team=devops cost-center=CC-1234

# Tag a specific resource
az resource tag --tags environment=production \
    --ids /subscriptions/.../resourceGroups/rg-prod/providers/.../vm-web01

# Find all resources with a specific tag
az resource list --tag environment=production -o table

# Enforce tags via Azure Policy (see 4.2)
```

**Recommended tags:**

```
  ┌──────────────┬───────────────────┬──────────────────────────────┐
  │ Tag Key      │ Example Value     │ Purpose                      │
  ├──────────────┼───────────────────┼──────────────────────────────┤
  │ environment  │ prod / staging    │ Identify environment         │
  │ team         │ devops / backend  │ Ownership                    │
  │ cost-center  │ CC-1234           │ Cost allocation / chargeback │
  │ project      │ myapp             │ Project association          │
  │ created-by   │ terraform / manual│ Track how resource was made  │
  │ expiry-date  │ 2025-06-30        │ Auto-cleanup scheduling      │
  └──────────────┴───────────────────┴──────────────────────────────┘
```

> ⚠️ **Gotcha:** Tags do NOT inherit from resource groups to resources. You must tag each resource individually. Use Azure Policy with "Modify" effect to auto-inherit tags.

---

## 4.6 Azure Cost Management

**What is it?** Azure's built-in tool for tracking, analyzing, and optimizing cloud spending. Set budgets, get alerts, and find waste.

**Input → Output:**

```
  You give it:  Budget limits + alert thresholds
  It gives you: Spending visibility, alerts when approaching budget, optimization tips
```

**Example:**

```bash
# View current costs
az consumption usage list \
    --start-date 2024-01-01 --end-date 2024-01-31 \
    --query "[].{Resource:instanceName, Cost:pretaxCost}" -o table

# Create a budget with email alert
az consumption budget create \
    --budget-name "monthly-prod" --amount 5000 \
    --category Cost --time-grain Monthly \
    --start-date 2024-01-01 --end-date 2025-12-31

# Get Azure Advisor cost recommendations
az advisor recommendation list --category Cost -o table
```

**Quick cost-saving checklist:**

```
  ✓ Auto-shutdown dev VMs at night
  ✓ Delete orphaned disks and public IPs
  ✓ Right-size over-provisioned VMs (check Azure Advisor)
  ✓ Use Reserved Instances for stable workloads (30-60% savings)
  ✓ Use Spot VMs for batch/CI workloads (up to 90% savings)
  ✓ Move cold storage to Cool/Archive tier
  ✓ Tag everything for cost visibility
```

> ⚠️ **Gotcha:** Cost data has a 24-48 hour delay. Don't panic if you don't see charges immediately. Set budget alerts at 50%, 80%, and 100% thresholds.

---

# Chapter 5 — Azure Storage Services

> **Storage** = where your data lives. Azure offers multiple storage types optimized for different data patterns — blobs, files, tables, queues, and disks.

```
  AZURE STORAGE — DATA TYPES
  ─────────────────────────────────────────────────────
  Unstructured data (files, images, videos) ──► Blob Storage
  File shares (SMB/NFS)                     ──► Azure Files
  Key-value data (simple NoSQL)             ──► Table Storage
  Message queuing                           ──► Queue Storage
  VM hard drives                            ──► Managed Disks
```

---

## 5.1 Storage Accounts

**What is it?** A container that holds all your Azure storage data (blobs, files, tables, queues). Every storage service lives inside a storage account. Think of it as a "parking garage" — blobs, files, and queues are different floors.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Account kind** | StorageV2 (general purpose v2) — always use this one |
| **Replication** | How many copies of your data Azure keeps (see table below) |
| **Access tier** | Hot (frequent access, higher storage cost) / Cool (infrequent, cheaper) / Archive (rare, cheapest) |
| **Performance** | Standard (HDD) or Premium (SSD) |

**Replication options:**

```
  ┌─────┬──────────────────────────────────────────────────┬──────────┐
  │ Type│ What it does                                     │ Cost     │
  ├─────┼──────────────────────────────────────────────────┼──────────┤
  │ LRS │ 3 copies in ONE datacenter                      │ Cheapest │
  │ ZRS │ 3 copies across 3 availability zones (same region)│ Medium  │
  │ GRS │ 6 copies: 3 local + 3 in paired region          │ Higher   │
  │ GZRS│ 6 copies: 3 across zones + 3 in paired region   │ Highest  │
  └─────┴──────────────────────────────────────────────────┴──────────┘

  LRS  = Dev/test. GRS = Production data you can't lose.
```

**Example:**

```bash
# Create a storage account (StorageV2, LRS, Hot tier)
az storage account create \
    --name stdemo2024 --resource-group rg-demo \
    --location eastus --sku Standard_LRS \
    --kind StorageV2 --access-tier Hot

# List storage accounts
az storage account list -g rg-demo -o table

# Show connection string
az storage account show-connection-string --name stdemo2024 -o tsv

# Show keys
az storage account keys list --account-name stdemo2024 -o table
```

> ⚠️ **Gotcha:** Storage account names must be globally unique, 3-24 chars, lowercase letters and numbers only. No dashes, no uppercase.

---

## 5.2 Blob Storage

**What is it?** Object storage for unstructured data — files, images, videos, backups, logs. Blobs are organized in **containers** (like folders). Azure's equivalent of AWS S3.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Container** | A folder-like grouping for blobs (e.g., "images", "backups") |
| **Block blob** | Most common — for files up to 190 TB (images, docs, videos) |
| **Page blob** | For random read/write (VM disks use this internally) |
| **Append blob** | Optimized for append operations (log files) |
| **Lifecycle policy** | Auto-move blobs between tiers (Hot→Cool→Archive→Delete) |

**Access tiers:**

```
  ┌──────────┬───────────┬────────────┬────────────────────────┐
  │ Tier     │ Storage $ │ Access $   │ Best for               │
  ├──────────┼───────────┼────────────┼────────────────────────┤
  │ Hot      │ Highest   │ Lowest     │ Frequently accessed    │
  │ Cool     │ Lower     │ Higher     │ 30+ days infrequent    │
  │ Cold     │ Lower     │ Higher     │ 90+ days rare access   │
  │ Archive  │ Cheapest  │ Expensive  │ 180+ days, hours to    │
  │          │           │            │ retrieve (rehydrate)   │
  └──────────┴───────────┴────────────┴────────────────────────┘
```

**Example:**

```bash
# Create a container
az storage container create --name images --account-name stdemo2024

# Upload a file
az storage blob upload \
    --account-name stdemo2024 --container-name images \
    --name photo.jpg --file ./photo.jpg

# List blobs
az storage blob list --account-name stdemo2024 --container-name images -o table

# Download a blob
az storage blob download \
    --account-name stdemo2024 --container-name images \
    --name photo.jpg --file ./downloaded.jpg

# Set lifecycle policy (move to Cool after 30 days, Archive after 90)
az storage account management-policy create \
    --account-name stdemo2024 --resource-group rg-demo \
    --policy @lifecycle-policy.json
```

**Diagram:**

```
  Storage Account: stdemo2024
       │
       ├── Container: images/
       │       ├── photo1.jpg     (Hot tier)
       │       ├── photo2.png     (Cool tier, >30 days old)
       │       └── old-photo.jpg  (Archive tier, >90 days old)
       │
       ├── Container: backups/
       │       ├── db-2024-01.bak
       │       └── db-2024-02.bak
       │
       └── Container: logs/
               └── app-2024-01.log  (Append blob)
```

> ⚠️ **Gotcha:** Archive tier blobs take **1-15 hours** to rehydrate before you can read them. Don't use Archive for data you need quickly.

---

## 5.3 Azure Files

**What is it?** Fully managed file shares in the cloud, accessible via SMB (Windows) or NFS (Linux) protocols. Like a shared network drive (\\server\share) but hosted in Azure.

**Input → Output:**

```
  You give it:  Storage account + share name + quota (size)
  It gives you: A network file share mountable from VMs, on-prem, or containers
```

**Use cases:**
1. Shared config files across multiple VMs
2. Replace on-prem file servers
3. Mount into Docker containers or AKS pods
4. Azure File Sync — sync on-prem file server with cloud

**Example:**

```bash
# Create a file share
az storage share create --name config-share --account-name stdemo2024 --quota 100

# Upload a file
az storage file upload --share-name config-share \
    --account-name stdemo2024 --source ./config.yaml

# Mount on Linux VM
sudo mount -t cifs //stdemo2024.file.core.windows.net/config-share /mnt/share \
    -o vers=3.0,username=stdemo2024,password=<storage-key>,dir_mode=0777
```

> ⚠️ **Gotcha:** SMB shares require port 445 open. Many ISPs block this port — Azure Files may not work from home networks. Use VPN or Azure File Sync instead.

---

## 5.4 Table Storage

**What is it?** A simple NoSQL key-value store. Good for storing structured data that doesn't need complex queries or relationships. Cheap and fast for large datasets with simple access patterns.

**Input → Output:**

```
  You give it:  PartitionKey + RowKey + properties (columns)
  It gives you: Fast key-based lookups on billions of rows at low cost
```

**Use cases:**
1. IoT telemetry data (device ID + timestamp → sensor reading)
2. User session data
3. Simple lookup tables

> ⚠️ **Gotcha:** For complex queries, indexing, or global distribution, use **Cosmos DB** instead. Table Storage is for simple key-value patterns only.

---

## 5.5 Queue Storage

**What is it?** A simple message queue for decoupling application components. Producer puts a message in the queue, consumer picks it up and processes it. Messages are guaranteed to be delivered at least once.

**Input → Output:**

```
  You give it:  Messages (up to 64 KB each)
  It gives you: Reliable asynchronous communication between app components
```

**Example:**

```bash
# Create a queue
az storage queue create --name task-queue --account-name stdemo2024

# Add a message
az storage message put --queue-name task-queue \
    --account-name stdemo2024 --content "Process order #1234"

# Peek at messages (don't remove)
az storage message peek --queue-name task-queue --account-name stdemo2024
```

> ⚠️ **Gotcha:** For advanced features (dead-letter queues, sessions, topics/subscriptions), use **Azure Service Bus** instead. Queue Storage is for simple scenarios.

---

## 5.6 Managed Disks

**What is it?** Virtual hard drives for Azure VMs. Azure manages the underlying storage infrastructure — you just pick the size and performance tier.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Ultra Disk** | Extreme IOPS (up to 160,000). For SAP HANA, top-tier databases |
| **Premium SSD v2** | Flexible IOPS/throughput tuning. Best price-performance |
| **Premium SSD** | High performance for production workloads |
| **Standard SSD** | Dev/test, light production |
| **Standard HDD** | Cheapest. Backups, infrequent access |

**Example:**

```bash
# Create a premium SSD disk (128 GB)
az disk create --resource-group rg-demo --name disk-data01 \
    --size-gb 128 --sku Premium_LRS

# Attach to VM
az vm disk attach --resource-group rg-demo --vm-name vm-web01 \
    --name disk-data01

# List disks
az disk list -g rg-demo -o table

# Find orphaned (unattached) disks
az disk list --query "[?managedBy==null].{Name:name, Size:diskSizeGb}" -o table
```

> ⚠️ **Gotcha:** Orphaned disks (not attached to any VM) still cost money. Run the "find orphaned" query above monthly and delete unused disks.

---

## 5.7 Storage Access & Security

**How do you control who can access storage?**

```
  ┌──────────────────────────┬──────────────────────────────────────┐
  │ Method                   │ When to use                          │
  ├──────────────────────────┼──────────────────────────────────────┤
  │ Storage Account Keys     │ Full access (like root password).    │
  │                          │ Avoid in production!                 │
  │ SAS Tokens               │ Temporary, scoped access (read blob │
  │                          │ X for 1 hour). Good for external     │
  │ Entra ID + RBAC          │ Best practice. Assign roles like     │
  │                          │ "Storage Blob Reader" to identities  │
  │ Managed Identity         │ Apps access storage without secrets  │
  │ Private Endpoint         │ Access only from your VNet           │
  │ Firewall rules           │ Allow only specific IPs/VNets        │
  └──────────────────────────┴──────────────────────────────────────┘
```

**Example — SAS token:**

```bash
# Generate a SAS token (read-only, expires in 1 hour)
az storage blob generate-sas \
    --account-name stdemo2024 --container-name images \
    --name photo.jpg --permissions r \
    --expiry $(date -u -d "+1 hour" +%Y-%m-%dT%H:%MZ) -o tsv

# Result: https://stdemo2024.blob.core.windows.net/images/photo.jpg?sv=...&sig=...
```

> ⚠️ **Gotcha:** Storage account keys give FULL access to everything. Never commit them to code. Use managed identities or SAS tokens instead. Rotate keys regularly: `az storage account keys renew`.

---

# Chapter 6 — Azure Security Services

> **Security** = protect your data, apps, and infrastructure. Azure gives you tools for secrets management, threat detection, and attack prevention.

---

## 6.1 Azure Key Vault

**What is it?** A secure vault for storing secrets (passwords, API keys), encryption keys, and SSL certificates. Apps retrieve secrets at runtime — nothing is hardcoded.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Secret** | A string value (DB password, API key, connection string) |
| **Key** | A cryptographic key for encryption/decryption (RSA, EC) |
| **Certificate** | An SSL/TLS certificate (auto-renew supported) |
| **Access policy** | Who can read/write secrets (legacy method) |
| **RBAC** | Recommended method — use roles like "Key Vault Secrets User" |
| **Soft delete** | Deleted secrets are recoverable for 7-90 days |

**Input → Output:**

```
  You give it:  Secret name + secret value + access policy/RBAC
  It gives you: Secure, centralized secret storage with audit logging
```

**Example:**

```bash
# Create a Key Vault
az keyvault create \
    --name kv-demo-2024 --resource-group rg-demo \
    --location eastus --enable-rbac-authorization true

# Store a secret
az keyvault secret set \
    --vault-name kv-demo-2024 --name db-password \
    --value "SuperSecret123!"

# Retrieve a secret
az keyvault secret show \
    --vault-name kv-demo-2024 --name db-password \
    --query value -o tsv

# List secrets
az keyvault secret list --vault-name kv-demo-2024 -o table

# Grant App Service access (via managed identity + RBAC)
az role assignment create \
    --assignee <managed-identity-id> \
    --role "Key Vault Secrets User" \
    --scope /subscriptions/.../resourceGroups/rg-demo/providers/Microsoft.KeyVault/vaults/kv-demo-2024

# Delete a secret (soft-deleted, recoverable)
az keyvault secret delete --vault-name kv-demo-2024 --name db-password

# Purge a secret (permanent delete)
az keyvault secret purge --vault-name kv-demo-2024 --name db-password
```

**Diagram:**

```
  App Service ──► "Give me db-password" ──► Key Vault ──► "SuperSecret123!"
       │                                        │
       │  (Managed Identity token)              │  Audit log:
       │  (No password in code!)                │  "App read db-password at 14:30"
       │                                        │
  AKS Pod ──► "Give me api-key" ──────────────►│
  Function ──► "Give me cert" ──────────────────│
```

> ⚠️ **Gotcha:** Key Vault names are globally unique. Soft delete is enabled by default — purging is a separate operation. Enable **purge protection** for production to prevent accidental permanent deletion.

---

## 6.2 Microsoft Defender for Cloud

**What is it?** Azure's security posture management and threat protection service. It scans your resources, gives you a **Secure Score** (0-100%), and recommends fixes. Like a security audit that runs continuously.

**Key terms:**

| Term | Meaning |
|------|---------|
| **CSPM** | Cloud Security Posture Management — finds misconfigurations |
| **CWPP** | Cloud Workload Protection Platform — threat detection for VMs, containers, SQL |
| **Secure Score** | 0-100% rating of your security posture |
| **Recommendations** | Specific fixes to improve security (e.g., "Enable MFA for owners") |

**Input → Output:**

```
  You give it:  Enabled on your subscription (free tier or paid plans)
  It gives you: Security score + recommendations + threat alerts
```

**Common recommendations:**

```
  ✗ Storage accounts should restrict network access     → Add firewall rules
  ✗ VMs should have encryption at host enabled          → Enable disk encryption
  ✗ MFA should be enabled for accounts with owner role  → Enable Conditional Access
  ✗ SQL databases should have TDE enabled               → Enable Transparent Data Encryption
  ✗ Key vaults should have soft delete enabled          → Enable soft delete
```

> ⚠️ **Gotcha:** Free tier gives CSPM (recommendations) only. For threat detection (CWPP), you need paid plans (~$15/server/month for VMs).

---

## 6.3 Azure DDoS Protection

**What is it?** Protection against Distributed Denial of Service attacks. Azure's basic DDoS protection is free and always-on. The paid tier (DDoS Protection Plan) adds advanced mitigation, alerting, and cost protection.

**Input → Output:**

```
  You give it:  DDoS Protection Plan associated with your VNet
  It gives you: Automatic DDoS detection + mitigation + attack analytics + cost guarantee
```

```
  ┌──────────────────┬──────────────────────────────────────────┐
  │ Tier             │ What you get                             │
  ├──────────────────┼──────────────────────────────────────────┤
  │ Basic (free)     │ Always-on, automatic L3/L4 protection   │
  │ Standard ($2,944 │ Adaptive tuning, metrics, alerts,       │
  │  /month)         │ cost protection (Azure credits if       │
  │                  │ DDoS causes scale-out costs)            │
  └──────────────────┴──────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** DDoS Standard costs ~$2,944/month. Only needed for internet-facing production apps. Basic (free) is sufficient for most workloads.

---

## 6.4 Microsoft Sentinel

**What is it?** Azure's cloud-native SIEM (Security Information and Event Management) and SOAR (Security Orchestration, Automation, and Response). It collects security data from all sources, detects threats using AI, and automates responses.

**Input → Output:**

```
  You give it:  Log sources (Azure logs, firewalls, servers, M365) + detection rules
  It gives you: Correlated security incidents + automated investigation + response playbooks
```

**Use cases:**
1. Detect brute-force attacks on VMs
2. Alert on suspicious sign-ins (impossible travel)
3. Correlate events across multiple services
4. Automate incident response (block IP, disable user)

> ⚠️ **Gotcha:** Sentinel pricing is based on data ingestion volume (per GB). It can get expensive quickly with high-volume log sources. Set data retention and filtering carefully.

---

# Chapter 7 — Azure Backup & Disaster Recovery

> **Backup** = copies of your data for recovery. **DR** = keeping your apps running even when an entire region fails.

---

## 7.1 Azure Backup

**What is it?** A managed backup service that creates and manages backups for VMs, SQL databases, file shares, and more. Backups are stored in a Recovery Services Vault.

**What can you back up?**

```
  ┌───────────────────────┬──────────────────────────────────────┐
  │ Resource              │ Backup method                        │
  ├───────────────────────┼──────────────────────────────────────┤
  │ Azure VMs             │ Snapshot → stored in vault           │
  │ Azure SQL Database    │ Automatic (built-in, configurable)   │
  │ Azure Files           │ Share snapshots → vault              │
  │ Azure Blob Storage    │ Operational + vaulted backups         │
  │ On-prem servers       │ MARS agent → vault                   │
  │ Azure Managed Disks   │ Disk snapshots → vault               │
  │ AKS                   │ AKS backup extension → vault         │
  └───────────────────────┴──────────────────────────────────────┘
```

**Example:**

```bash
# Create a Recovery Services Vault
az backup vault create \
    --name rsv-prod --resource-group rg-demo \
    --location eastus

# Enable backup for a VM (default policy: daily at 10 PM, 30-day retention)
az backup protection enable-for-vm \
    --resource-group rg-demo --vault-name rsv-prod \
    --vm vm-web01 --policy-name DefaultPolicy

# Trigger an on-demand backup
az backup protection backup-now \
    --resource-group rg-demo --vault-name rsv-prod \
    --container-name vm-web01 --item-name vm-web01 \
    --backup-management-type AzureIaasVM

# List recovery points
az backup recoverypoint list \
    --resource-group rg-demo --vault-name rsv-prod \
    --container-name vm-web01 --item-name vm-web01 \
    --backup-management-type AzureIaasVM -o table
```

> ⚠️ **Gotcha:** Azure Backup uses UTC time for scheduling. If you set backup at "10:00 PM," that's 10 PM UTC, not your local time.

---

## 7.2 Recovery Services Vault

**What is it?** The storage container for all your backups and replication data. Think of it as a "safe" that holds all your backup copies and DR replication data.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Backup policy** | Schedule + retention rules (how often, how long to keep) |
| **Recovery point** | A specific backup snapshot you can restore from |
| **GRS vault** | Vault data replicated to paired region (for DR) |
| **LRS vault** | Vault data in same region only (cheaper) |
| **Soft delete** | Deleted backups retained for 14 days (protection against ransomware) |

**Diagram:**

```
  ┌──────────────────────────────────────────────┐
  │  Recovery Services Vault (rsv-prod)          │
  │                                              │
  │  Backup Items:                               │
  │  ├── vm-web01 ──► 30 daily recovery points  │
  │  ├── vm-db01  ──► 30 daily + 12 monthly     │
  │  └── share01  ──► 7 daily snapshots          │
  │                                              │
  │  Replication (ASR):                          │
  │  └── vm-web01 ──► replicating to West US    │
  │                                              │
  │  Storage: GRS (replicated to paired region)  │
  └──────────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Choose GRS for production vaults (data survives region failure). The vault MUST be in the same region as the resources it backs up.

---

## 7.3 Azure Site Recovery (ASR)

**What is it?** Replicates your VMs to another Azure region in real-time. If the primary region goes down, you "failover" to the secondary region and your apps keep running. Like a standby generator that kicks in during a power outage.

**Key terms:**

| Term | Meaning |
|------|---------|
| **RPO** | Recovery Point Objective — max data loss you can tolerate (ASR: ~30 seconds) |
| **RTO** | Recovery Time Objective — time to recover (ASR: minutes) |
| **Failover** | Switch from primary region to secondary |
| **Failback** | Switch back to primary after it recovers |
| **Test failover** | Practice DR in an isolated network (no impact on production) |

**Diagram:**

```
  Primary (East US)              Secondary (West US)
  ─────────────────              ──────────────────
  ┌──────────┐                   ┌──────────┐
  │ VM-web01 │ ═══replication═══►│ VM-web01 │  (standby)
  │ VM-db01  │ ═══════════════►  │ VM-db01  │  (standby)
  └──────────┘                   └──────────┘

  Normal:   Traffic → East US (primary)
  Failover: Traffic → West US (secondary, becomes active)
  Failback: Traffic → East US (after recovery)

  RPO: ~30 seconds (max 30 sec of data loss)
  RTO: ~2 minutes (failover takes ~2 min)
```

> ⚠️ **Gotcha:** Test failover monthly. A DR plan that's never tested is just a document. ASR charges per protected instance (~$25/VM/month).

---

## 7.4 Geo-Replication & Paired Regions

**What is it?** Azure automatically pairs regions (East US ↔ West US, North Europe ↔ West Europe). During major outages, Azure prioritizes recovery of one region in each pair. Some services (Storage, SQL) can replicate data to paired regions automatically.

**Azure paired regions:**

```
  ┌─────────────────┬─────────────────┐
  │ Primary Region  │ Paired Region   │
  ├─────────────────┼─────────────────┤
  │ East US         │ West US         │
  │ East US 2       │ Central US      │
  │ North Europe    │ West Europe     │
  │ Southeast Asia  │ East Asia       │
  │ UK South        │ UK West         │
  │ Central India   │ South India     │
  └─────────────────┴─────────────────┘
```

> ⚠️ **Gotcha:** Not all services auto-replicate to paired regions. You must configure GRS for storage, failover groups for SQL, and ASR for VMs explicitly.

---

# Chapter 8 — Azure Monitoring & Observability

> **Monitoring** = knowing what's happening inside your apps and infra. Azure Monitor is the backbone — everything feeds into it.

```
  MONITORING DATA FLOW
  ────────────────────────────────────────────────────
  Sources                    Pipeline              Action
  ───────                    ────────              ──────
  VMs (metrics/logs)    ──┐
  App Service (logs)    ──┤                   ┌─► Alerts (email/SMS)
  AKS (container logs)  ──┼──► Azure Monitor ──┼─► Dashboards
  Functions (traces)    ──┤    (central hub)   ├─► Workbooks
  Custom apps (SDK)     ──┤                   ├─► Autoscale triggers
  Network (flow logs)   ──┘                   └─► Log Analytics (KQL)
```

---

## 8.1 Azure Monitor

**What is it?** The central monitoring platform for everything in Azure. It collects **metrics** (numbers like CPU%) and **logs** (text events) from all Azure resources and custom apps.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Metrics** | Numeric time-series data (CPU %, memory, request count). Auto-collected |
| **Logs** | Text/structured events stored in Log Analytics. Query with KQL |
| **Diagnostic settings** | Turn on log/metric collection for a resource → send to Log Analytics |

**Input → Output:**

```
  You give it:  Resources with diagnostic settings enabled
  It gives you: Real-time metrics, searchable logs, alerts, dashboards
```

**Example:**

```bash
# Enable diagnostic settings on a VM (send to Log Analytics)
az monitor diagnostic-settings create \
    --resource /subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm-web01 \
    --name diag-vm-web01 \
    --workspace $LOG_ANALYTICS_ID \
    --metrics '[{"category":"AllMetrics","enabled":true}]'

# View VM CPU metric (last 1 hour)
az monitor metrics list \
    --resource /subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm-web01 \
    --metric "Percentage CPU" --interval PT1H -o table
```

---

## 8.2 Log Analytics Workspace

**What is it?** A centralized database for all your log data. Everything in Azure Monitor flows here. You query it using KQL (Kusto Query Language) — like SQL but for logs.

**Key terms:**

| Term | Meaning |
|------|---------|
| **KQL** | Kusto Query Language — the query language for Log Analytics |
| **Retention** | How long logs are kept (default 30 days, max 730 days) |
| **Table** | Logs are organized in tables (Heartbeat, Perf, AzureActivity, etc.) |

**Input → Output:**

```
  You give it:  Log sources (VMs, apps, network) + retention period
  It gives you: Searchable log database you can query with KQL
```

**Example:**

```bash
# Create a Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group rg-demo --workspace-name law-demo \
    --location eastus --retention-time 90
```

**Common KQL queries:**

```kusto
// Find top 10 errors in the last 24 hours
AppExceptions
| where TimeGenerated > ago(24h)
| summarize count() by ProblemId
| top 10 by count_

// VM CPU usage over time
Perf
| where ObjectName == "Processor" and CounterName == "% Processor Time"
| summarize avg(CounterValue) by bin(TimeGenerated, 5m), Computer
| render timechart

// Failed sign-ins
SigninLogs
| where ResultType != 0
| summarize count() by UserPrincipalName, ResultDescription
| order by count_ desc
```

> ⚠️ **Gotcha:** Log Analytics charges per GB ingested (~$2.76/GB). High-volume sources (NSG flow logs, container logs) can get expensive. Use data collection rules to filter what you ingest.

---

## 8.3 Application Insights

**What is it?** Application Performance Monitoring (APM) for your code. It tracks requests, failures, dependencies, and performance of your web apps. Like having X-ray vision into your application.

**Input → Output:**

```
  You give it:  SDK in your app code or auto-instrumentation
  It gives you: Request rates, response times, failure rates, dependency maps, distributed tracing
```

**What it tracks:**

```
  ┌─────────────────────────────────────────────────────────────┐
  │  Application Insights Dashboard                            │
  │                                                            │
  │  Requests:    1,234/sec   (avg 45ms)                      │
  │  Failures:    0.3%        (12 in last hour)                │
  │  Dependencies: SQL: 15ms avg, Redis: 2ms, External: 200ms │
  │  Exceptions:  NullReferenceException × 5                   │
  │                                                            │
  │  Live Metrics: ████████░░ CPU: 42%  Memory: 67%           │
  │  Application Map:  Frontend → API → SQL DB → Redis        │
  └─────────────────────────────────────────────────────────────┘
```

**Example:**

```bash
# Create Application Insights (workspace-based)
az monitor app-insights component create \
    --app appi-myapp --location eastus \
    --resource-group rg-demo \
    --workspace $LOG_ANALYTICS_ID

# Get the instrumentation key
az monitor app-insights component show \
    --app appi-myapp --resource-group rg-demo \
    --query instrumentationKey -o tsv
```

> ⚠️ **Gotcha:** Enable **sampling** for high-traffic apps. Without it, App Insights can ingest millions of telemetry events and cost a fortune. Default sampling keeps 1/5 of events.

---

## 8.4 Alerts & Action Groups

**What is it?** Automated notifications when something goes wrong. "If CPU > 90% for 5 minutes → send email + SMS." Alerts watch metrics or logs and trigger Action Groups.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Metric alert** | Fires when a metric crosses a threshold (CPU > 90%) |
| **Log alert** | Fires when a KQL query returns results (error count > 10) |
| **Action Group** | WHO to notify and HOW (email, SMS, webhook, Azure Function) |
| **Severity** | 0 (Critical) → 4 (Verbose) |

**Example:**

```bash
# Create an Action Group (email + SMS)
az monitor action-group create \
    --resource-group rg-demo --name ag-devops \
    --short-name DevOps \
    --action email devops-email devops@company.com \
    --action sms devops-sms 1 5551234567

# Create a metric alert (CPU > 90%)
az monitor metrics alert create \
    --resource-group rg-demo --name alert-cpu-high \
    --scopes /subscriptions/.../providers/Microsoft.Compute/virtualMachines/vm-web01 \
    --condition "avg Percentage CPU > 90" \
    --window-size 5m --evaluation-frequency 1m \
    --action ag-devops --severity 2 \
    --description "VM CPU is above 90%"
```

> ⚠️ **Gotcha:** Alert storms — if a flapping metric triggers repeatedly, you'll get flooded with notifications. Use `--auto-mitigate true` to auto-resolve and set appropriate evaluation windows.

---

# Chapter 9 — Azure Container & Registry Services

> Container-specific services. Note: ACI and AKS basics are covered in Chapter 1. This chapter covers **ACR** and advanced container patterns.

---

## 9.1 Azure Container Registry (ACR)

**What is it?** A private Docker registry hosted in Azure. You build, store, and manage container images here. Like Docker Hub but private and inside your Azure environment.

**Key terms:**

| Term | Meaning |
|------|---------|
| **SKU: Basic** | 10 GB storage, limited throughput. Dev/test |
| **SKU: Standard** | 100 GB, more throughput. Small teams |
| **SKU: Premium** | 500 GB, geo-replication, private endpoints, content trust |
| **Repository** | A collection of related image tags (e.g., myapi:v1, myapi:v2) |
| **ACR Tasks** | Build images in the cloud (no local Docker needed) |

**Input → Output:**

```
  You give it:  Dockerfile + source code (or pre-built image)
  It gives you: A private, scannable container image registry with RBAC
```

**Example:**

```bash
# Create an ACR
az acr create --name myacr2024 --resource-group rg-demo \
    --sku Standard --admin-enabled false

# Login to ACR
az acr login --name myacr2024

# Build image in cloud (ACR Tasks — no local Docker needed)
az acr build --registry myacr2024 \
    --image myapi:v1 --file Dockerfile .

# Push a local image
docker tag myapi:v1 myacr2024.azurecr.io/myapi:v1
docker push myacr2024.azurecr.io/myapi:v1

# List repositories
az acr repository list --name myacr2024 -o table

# List tags for a repository
az acr repository show-tags --name myacr2024 --repository myapi -o table

# Attach ACR to AKS (so AKS can pull images)
az aks update --resource-group rg-demo --name aks-demo \
    --attach-acr myacr2024

# Delete old images (keep last 5 tags)
az acr run --cmd "acr purge --filter 'myapi:.*' --ago 30d --keep 5" \
    --registry myacr2024 /dev/null
```

**Diagram:**

```
  Developer                    ACR                         AKS / App Service
  ─────────                    ───                         ─────────────────
  Dockerfile ──► az acr build ──► myacr.azurecr.io/myapi:v1 ──► Pod pulls image
                                      │
                                      ├── Vulnerability scan
                                      ├── Geo-replication (Premium)
                                      └── Private endpoint access
```

> ⚠️ **Gotcha:** Disable admin access (`--admin-enabled false`). Use managed identities or `az aks update --attach-acr` for AKS. Admin passwords are a security risk.

---

## 9.2 ACI Deep Dive

**What is it?** Advanced ACI patterns beyond the basics covered in Chapter 1.

**Multi-container groups (sidecar pattern):**

```yaml
# deploy-aci.yaml — Container group with sidecar
apiVersion: 2021-10-01
type: Microsoft.ContainerInstance/containerGroups
properties:
  containers:
    - name: app
      properties:
        image: myacr.azurecr.io/myapi:v1
        ports: [{ port: 80 }]
        resources:
          requests: { cpu: 1, memoryInGB: 1.5 }
    - name: log-shipper
      properties:
        image: fluent/fluentd
        resources:
          requests: { cpu: 0.5, memoryInGB: 0.5 }
  osType: Linux
  ipAddress:
    type: Public
    ports: [{ port: 80, protocol: TCP }]
```

```bash
# Deploy container group from YAML
az container create --resource-group rg-demo \
    --file deploy-aci.yaml
```

---

## 9.3 AKS Deep Dive

**What is it?** Advanced AKS patterns beyond the basics covered in Chapter 1.

**Key production patterns:**

```bash
# Enable workload identity (pods access Azure services securely)
az aks update --resource-group rg-demo --name aks-demo \
    --enable-oidc-issuer --enable-workload-identity

# Enable Application Gateway Ingress Controller (AGIC)
az aks enable-addons --resource-group rg-demo --name aks-demo \
    --addons ingress-appgw --appgw-subnet-cidr "10.0.10.0/24"

# Enable Azure Monitor for containers
az aks enable-addons --resource-group rg-demo --name aks-demo \
    --addons monitoring --workspace-resource-id $LOG_ANALYTICS_ID

# Upgrade AKS cluster
az aks get-upgrades --resource-group rg-demo --name aks-demo -o table
az aks upgrade --resource-group rg-demo --name aks-demo \
    --kubernetes-version 1.29.0

# Enable cluster autoscaler
az aks update --resource-group rg-demo --name aks-demo \
    --enable-cluster-autoscaler --min-count 2 --max-count 10
```

> ⚠️ **Gotcha:** AKS + Azure CNI: every pod gets a VNet IP. With a /24 subnet (251 IPs), you'll run out fast with 50+ pods. Use /20 or larger, or switch to Azure CNI Overlay.

---

# Chapter 10 — Azure Resource Manager & Infrastructure as Code

> **IaC** = manage infrastructure with code files instead of clicking in the portal. Repeatable, version-controlled, auditable.

```
  IaC OPTIONS ON AZURE
  ────────────────────────────────────────────────────
  ┌──────────────┬──────────────────────────────────────┐
  │ Tool         │ Language / Format                     │
  ├──────────────┼──────────────────────────────────────┤
  │ ARM Templates│ JSON (verbose, Azure-native)          │
  │ Bicep        │ DSL (clean, compiles to ARM JSON)     │
  │ Terraform    │ HCL (multi-cloud, state management)   │
  │ Pulumi       │ Python/JS/Go (general purpose langs)  │
  └──────────────┴──────────────────────────────────────┘

  Recommendation: Bicep for Azure-only, Terraform for multi-cloud.
```

---

## 10.1 Azure Resource Manager (ARM)

**What is it?** The control plane for ALL Azure resource operations. Every action in Azure — portal click, CLI command, REST API call — goes through ARM. It authenticates, authorizes, and executes resource operations.

**Diagram:**

```
  az vm create ──────┐
  Portal click  ─────┤
  REST API call ─────┼──► ARM (Resource Manager) ──► Resource Provider
  Terraform apply ───┤        │                        │
  Bicep deploy  ─────┘        │                  Microsoft.Compute
                           Authenticate            Microsoft.Network
                           Authorize (RBAC)        Microsoft.Storage
                           Execute
```

---

## 10.2 ARM Templates (JSON)

**What is it?** Azure's native IaC format. JSON files that declare what resources to create. Declarative — you describe the desired state, ARM figures out how to get there.

**Template anatomy:**

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "vmName": { "type": "string", "defaultValue": "vm-web01" }
  },
  "variables": {
    "nicName": "[concat(parameters('vmName'), '-nic')]"
  },
  "resources": [
    {
      "type": "Microsoft.Compute/virtualMachines",
      "apiVersion": "2023-09-01",
      "name": "[parameters('vmName')]",
      "location": "[resourceGroup().location]",
      "properties": { ... }
    }
  ],
  "outputs": {
    "vmId": { "type": "string", "value": "[resourceId('Microsoft.Compute/virtualMachines', parameters('vmName'))]" }
  }
}
```

**Example:**

```bash
# Deploy an ARM template
az deployment group create \
    --resource-group rg-demo \
    --template-file main.json \
    --parameters vmName=vm-web01

# Validate (dry-run)
az deployment group validate \
    --resource-group rg-demo --template-file main.json

# What-if (preview changes)
az deployment group what-if \
    --resource-group rg-demo --template-file main.json
```

> ⚠️ **Gotcha:** ARM JSON is verbose and hard to read. Microsoft created **Bicep** as a cleaner alternative. Use Bicep for new projects — it compiles down to ARM JSON anyway.

---

## 10.3 Bicep Language

**What is it?** A domain-specific language (DSL) that makes Azure IaC readable. It compiles to ARM JSON but is dramatically simpler. Think of Bicep as "TypeScript for ARM templates."

**Example — Create a Storage Account:**

```bicep
// main.bicep
param location string = resourceGroup().location
param storageName string = 'st${uniqueString(resourceGroup().id)}'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
}

output storageId string = storageAccount.id
output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob
```

**Example — Create a VNet + Subnet + NSG (modules):**

```bicep
// modules/network.bicep
param vnetName string
param location string = resourceGroup().location

resource nsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: '${vnetName}-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTPS'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          destinationPortRange: '443'
          sourceAddressPrefix: 'Internet'
          destinationAddressPrefix: '*'
          sourcePortRange: '*'
        }
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: { addressPrefixes: ['10.0.0.0/16'] }
    subnets: [
      {
        name: 'snet-web'
        properties: {
          addressPrefix: '10.0.1.0/24'
          networkSecurityGroup: { id: nsg.id }
        }
      }
    ]
  }
}
```

**Deployment:**

```bash
# Deploy Bicep
az deployment group create \
    --resource-group rg-demo \
    --template-file main.bicep \
    --parameters storageName=stdemo2024

# What-if (preview)
az deployment group what-if \
    --resource-group rg-demo --template-file main.bicep

# Decompile ARM JSON → Bicep
az bicep decompile --file main.json

# Build Bicep → ARM JSON
az bicep build --file main.bicep
```

**ARM JSON vs Bicep comparison:**

```
  ARM JSON (40 lines):              Bicep (10 lines):
  ──────────────────                ─────────────────
  {                                 resource sa 'Microsoft.Storage/
    "$schema": "...",                 storageAccounts@2023-01-01' = {
    "contentVersion": "1.0",          name: storageName
    "resources": [{                   location: location
      "type": "Microsoft...",         sku: { name: 'Standard_LRS' }
      "apiVersion": "2023...",        kind: 'StorageV2'
      "name": "[parameters(..)]",   }
      "location": "[resource..)]",
      "properties": {
        "sku": { "name": "..." },
        ...
      }
    }]
  }

  Winner: Bicep. Same result, 75% less code.
```

> ⚠️ **Gotcha:** Bicep is Azure-only. If you need multi-cloud (AWS + Azure + GCP), use Terraform instead.

---

## 10.4 Terraform on Azure

**What is it?** HashiCorp's multi-cloud IaC tool. Uses HCL (HashiCorp Configuration Language). Works on Azure, AWS, GCP, and 3000+ providers. State is tracked in a file (local or remote).

**Example:**

```hcl
# main.tf — Create a Resource Group + Storage Account
terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.0" }
  }
  backend "azurerm" {
    resource_group_name  = "rg-terraform"
    storage_account_name = "sttfstate2024"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" { features {} }

resource "azurerm_resource_group" "demo" {
  name     = "rg-demo"
  location = "eastus"
}

resource "azurerm_storage_account" "demo" {
  name                     = "stdemo2024"
  resource_group_name      = azurerm_resource_group.demo.name
  location                 = azurerm_resource_group.demo.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

```bash
# Initialize
terraform init

# Preview changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

**IaC Decision Guide:**

```
  ┌──────────────┬──────────┬──────────┬──────────────┐
  │              │ Bicep    │ Terraform│ ARM JSON     │
  ├──────────────┼──────────┼──────────┼──────────────┤
  │ Language     │ DSL      │ HCL      │ JSON         │
  │ Multi-cloud  │ No       │ Yes      │ No           │
  │ State mgmt   │ Azure    │ You      │ Azure        │
  │ Learning     │ Easy     │ Medium   │ Hard         │
  │ Community    │ Growing  │ Massive  │ Legacy       │
  │ Best for     │ Azure-   │ Multi-   │ Avoid for    │
  │              │ only     │ cloud    │ new projects │
  └──────────────┴──────────┴──────────┴──────────────┘
```

> ⚠️ **Gotcha:** Terraform state contains secrets (passwords, keys). Always use remote backend (Azure Blob Storage) with encryption + state locking. Never commit `.tfstate` to Git.

---

# Chapter 11 — Azure Database Services

> **Databases** = managed data storage with built-in HA, backups, and scaling. Azure manages the engine — you manage the data.

---

## 11.1 Azure SQL Database

**What is it?** A fully managed relational database running Microsoft SQL Server engine. Azure handles patching, backups, HA, and scaling. You just design your schema and write queries.

**Key terms:**

| Term | Meaning |
|------|---------|
| **DTU model** | Bundled compute (CPU + IO + memory). Simple pricing: Basic/Standard/Premium |
| **vCore model** | Pick CPU cores + memory separately. More control, reserved instance discounts |
| **Elastic Pool** | Share resources across multiple databases (cost-effective for many small DBs) |
| **Failover Group** | Automatic geo-replication + failover to another region |
| **TDE** | Transparent Data Encryption — encrypts data at rest (enabled by default) |
| **Serverless** | Auto-pause when idle (no charge for compute). Great for dev/test |

**Input → Output:**

```
  You give it:  SQL schema + queries + performance tier
  It gives you: A managed SQL database with 99.99% SLA, auto-backups, geo-replication
```

**Example:**

```bash
# Create a SQL server
az sql server create \
    --name sql-demo-2024 --resource-group rg-demo \
    --location eastus --admin-user sqladmin \
    --admin-password "P@ssw0rd123!"

# Create a database (serverless, auto-pause after 1 hour)
az sql db create \
    --resource-group rg-demo --server sql-demo-2024 \
    --name db-myapp --edition GeneralPurpose \
    --compute-model Serverless --auto-pause-delay 60 \
    --min-capacity 0.5 --capacity 2

# Set firewall rule (allow your IP)
az sql server firewall-rule create \
    --resource-group rg-demo --server sql-demo-2024 \
    --name AllowMyIP --start-ip-address 203.0.113.1 \
    --end-ip-address 203.0.113.1

# List databases
az sql db list --resource-group rg-demo --server sql-demo-2024 -o table
```

> ⚠️ **Gotcha:** Serverless tier auto-pauses after idle period, causing a **cold start delay** (~1 min) on the next query. Don't use for production APIs with strict latency requirements.

---

## 11.2 Azure Cosmos DB

**What is it?** A globally distributed, multi-model NoSQL database. It replicates data to any Azure region with single-digit millisecond latency. Supports multiple APIs: NoSQL (document), MongoDB, Cassandra, Gremlin (graph), Table.

**Key terms:**

| Term | Meaning |
|------|---------|
| **RU/s** | Request Units per second — the "currency" of Cosmos DB throughput |
| **Partition key** | How data is distributed. Choosing wrong key = hot partitions = throttling |
| **Global distribution** | Write in East US, read from Europe — automatic replication |
| **Consistency levels** | Strong → Bounded Staleness → Session → Consistent Prefix → Eventual |

**Input → Output:**

```
  You give it:  Data model + partition key + RU/s budget + regions
  It gives you: <10ms reads/writes globally with 99.999% availability (multi-region)
```

**Example:**

```bash
# Create Cosmos DB account (NoSQL API)
az cosmosdb create \
    --name cosmos-demo-2024 --resource-group rg-demo \
    --locations regionName=eastus failoverPriority=0 \
    --locations regionName=westeurope failoverPriority=1 \
    --default-consistency-level Session

# Create a database and container
az cosmosdb sql database create \
    --account-name cosmos-demo-2024 --resource-group rg-demo \
    --name mydb

az cosmosdb sql container create \
    --account-name cosmos-demo-2024 --resource-group rg-demo \
    --database-name mydb --name users \
    --partition-key-path "/userId" --throughput 400
```

> ⚠️ **Gotcha:** Cosmos DB can get expensive fast. 400 RU/s minimum = ~$24/month per container. Use autoscale (100-1000 RU/s) for variable workloads, and always pick the right partition key.

---

## 11.3 Azure Database for MySQL/PostgreSQL

**What is it?** Fully managed open-source databases. Azure handles backups, patching, HA, and scaling. Use **Flexible Server** (recommended) — it replaces the older Single Server.

**Input → Output:**

```
  You give it:  MySQL/PostgreSQL version + compute tier + storage size
  It gives you: A managed database with auto-backups, HA, and VNet integration
```

**Example:**

```bash
# Create a PostgreSQL Flexible Server
az postgres flexible-server create \
    --resource-group rg-demo --name pg-demo-2024 \
    --location eastus --admin-user pgadmin \
    --admin-password "P@ssw0rd123!" \
    --sku-name Standard_B1ms --tier Burstable \
    --storage-size 32 --version 16

# Create a database
az postgres flexible-server db create \
    --resource-group rg-demo --server-name pg-demo-2024 \
    --database-name myappdb

# Connect
psql "host=pg-demo-2024.postgres.database.azure.com user=pgadmin dbname=myappdb"
```

> ⚠️ **Gotcha:** Flexible Server "Burstable" tier is cheapest (~$13/month) but has CPU limits. Use "General Purpose" for production workloads.

---

## 11.4 Azure Cache for Redis

**What is it?** A managed in-memory cache based on Redis. Stores frequently accessed data in RAM for sub-millisecond responses. Used for session state, caching, and real-time leaderboards.

**Input → Output:**

```
  You give it:  Cache size tier + optional clustering
  It gives you: Sub-millisecond key-value store for caching and session management
```

**Use cases:**
1. Cache database query results (reduce DB load by 90%)
2. Session state storage for web apps
3. Real-time leaderboards and counters
4. Pub/sub messaging

**Example:**

```bash
# Create Redis cache (C0 = Basic, 250MB)
az redis create --name redis-demo-2024 --resource-group rg-demo \
    --location eastus --sku Basic --vm-size c0

# Get connection string
az redis list-keys --name redis-demo-2024 --resource-group rg-demo
```

> ⚠️ **Gotcha:** Basic tier has no SLA and no replication. Use **Standard** (replicated) for production, **Premium** for clustering and VNet support.

---

# Chapter 12 — Azure Messaging & Integration

> **Messaging** = decouple your application components. Instead of direct calls, apps communicate via messages/events.

```
  MESSAGING DECISION GUIDE
  ──────────────────────────────────────────────
  Need point-to-point queuing?     ──► Service Bus Queue
  Need pub/sub (topics)?           ──► Service Bus Topics
  Need event routing (react)?      ──► Event Grid
  Need high-throughput streaming?  ──► Event Hubs (Kafka)
  Need workflow orchestration?     ──► Logic Apps
  Need API gateway?                ──► API Management
```

---

## 12.1 Azure Service Bus

**What is it?** Enterprise-grade message broker. Supports queues (point-to-point) and topics (pub/sub). Guarantees ordered, exactly-once delivery with dead-letter handling.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Queue** | One sender → one receiver. Messages processed in order |
| **Topic** | One sender → many receivers (subscriptions). Pub/sub pattern |
| **Dead-letter queue** | Where unprocessable messages go (after max retries) |
| **Session** | Group related messages for ordered processing |

**Input → Output:**

```
  You give it:  Messages from producers
  It gives you: Reliable, ordered delivery to consumers with retry and dead-letter
```

**Example:**

```bash
# Create a Service Bus namespace
az servicebus namespace create \
    --resource-group rg-demo --name sb-demo-2024 \
    --location eastus --sku Standard

# Create a queue
az servicebus queue create \
    --resource-group rg-demo --namespace-name sb-demo-2024 \
    --name order-queue --max-size 1024

# Create a topic + subscription
az servicebus topic create \
    --resource-group rg-demo --namespace-name sb-demo-2024 \
    --name notifications

az servicebus topic subscription create \
    --resource-group rg-demo --namespace-name sb-demo-2024 \
    --topic-name notifications --name email-sub
```

**Diagram:**

```
  QUEUE (point-to-point):           TOPIC (pub/sub):
  ───────────────────────           ────────────────

  Producer → [Queue] → Consumer    Publisher → [Topic] → Sub A → Email
                                                       → Sub B → SMS
                                                       → Sub C → Webhook
```

> ⚠️ **Gotcha:** Service Bus Standard supports topics. Basic tier only has queues. For production pub/sub, use Standard or Premium.

---

## 12.2 Azure Event Grid

**What is it?** A serverless event routing service. Azure services emit events (e.g., "blob uploaded", "VM created"), and Event Grid delivers them to handlers (Functions, Logic Apps, webhooks). Reactive, event-driven architecture.

**Input → Output:**

```
  You give it:  Event source + event subscription + handler
  It gives you: Automatic event routing — "when X happens, trigger Y"
```

**Common event sources:**

```
  Blob Storage → "blob created" → resize image (Function)
  Resource Group → "resource deleted" → alert (email)
  Container Registry → "image pushed" → deploy (Pipeline)
  Key Vault → "secret expiring" → rotate (Function)
  Custom app → "order placed" → process (Service Bus)
```

> ⚠️ **Gotcha:** Event Grid delivers events but doesn't guarantee ordering. For ordered processing, use Service Bus.

---

## 12.3 Azure Event Hubs

**What is it?** A big-data streaming platform. Ingests millions of events per second. Think of it as "managed Apache Kafka." Used for telemetry, clickstreams, and real-time analytics.

**Key terms:**

| Term | Meaning |
|------|---------|
| **Partition** | Parallel processing lanes (more partitions = more throughput) |
| **Consumer group** | Independent reader of the stream (each gets all events) |
| **Capture** | Auto-save events to Blob Storage or Data Lake |
| **Kafka compatible** | Use Kafka clients/APIs directly — no code changes |

**Input → Output:**

```
  You give it:  High-volume event stream (millions/sec)
  It gives you: Buffered, partitioned event stream for real-time processing
```

> ⚠️ **Gotcha:** Event Hubs is for high-throughput streaming, not point-to-point messaging. For reliable delivery to a single consumer, use Service Bus.

---

## 12.4 Azure Logic Apps

**What is it?** A low-code/no-code workflow engine. Connect 400+ services with drag-and-drop. "When a new email arrives in Outlook, save attachment to Blob Storage and notify Slack."

**Input → Output:**

```
  You give it:  Trigger + actions + connectors (drag-and-drop in designer)
  It gives you: Automated workflows without writing code
```

**Use cases:**
1. Approval workflows (manager approves expense → update SharePoint)
2. Data integration (sync Salesforce → SQL → Power BI)
3. Alert escalation (Defender alert → Teams → create Jira ticket)
4. File processing (email attachment → OCR → save to DB)

> ⚠️ **Gotcha:** Logic Apps Standard runs on App Service Plan (predictable cost). Consumption plan charges per action execution — can get expensive with high-frequency workflows.

---

## 12.5 Azure API Management

**What is it?** A managed API gateway that sits in front of your APIs. It handles authentication, rate limiting, caching, monitoring, and developer portal — so your API code stays clean.

**Input → Output:**

```
  You give it:  Backend API URLs + policies (rate limit, auth, transform)
  It gives you: A unified API gateway with developer portal, analytics, and security
```

**Diagram:**

```
  Mobile App ──┐                              ┌── Backend API 1
  Web App   ───┼──► API Management Gateway ───┼── Backend API 2
  Partner   ───┘    │                          └── Backend API 3
                    ├── Auth (JWT, API key)
                    ├── Rate limiting (100 req/min)
                    ├── Response caching
                    └── Request/response transform
```

> ⚠️ **Gotcha:** APIM Developer tier is for testing only (no SLA). Use Standard or Premium for production. Premium required for VNet integration.

---

# Chapter 13 — Azure DevOps Services

> **Azure DevOps** = a suite of development tools for planning, coding, building, testing, and deploying.

---

## 13.1 Azure DevOps Overview

**What is it?** A set of 5 integrated services for the software development lifecycle:

```
  ┌─────────────────────────────────────────────────────────┐
  │  Azure DevOps                                          │
  │                                                        │
  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │
  │  │ Boards   │  │ Repos    │  │ Pipelines            │ │
  │  │ (plan)   │  │ (code)   │  │ (build + deploy)     │ │
  │  └──────────┘  └──────────┘  └──────────────────────┘ │
  │  ┌──────────┐  ┌──────────┐                           │
  │  │ Test Plans│  │ Artifacts│                           │
  │  │ (test)   │  │ (packages)│                           │
  │  └──────────┘  └──────────┘                           │
  └─────────────────────────────────────────────────────────┘
```

| Service | What it does |
|---------|-------------|
| **Boards** | Work items, sprints, Kanban boards (like Jira) |
| **Repos** | Git repositories (like GitHub) |
| **Pipelines** | CI/CD pipelines in YAML (like GitHub Actions) |
| **Test Plans** | Manual/exploratory/automated testing |
| **Artifacts** | Package feeds (npm, NuGet, Maven, pip) |

---

## 13.2 Azure Pipelines (YAML)

**What is it?** CI/CD pipelines defined in YAML. Build, test, and deploy your code to any platform. Similar to GitHub Actions but with deeper Azure integration.

**Example — Multi-stage pipeline:**

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include: [main]

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: Build
    jobs:
      - job: BuildApp
        steps:
          - task: UsePythonVersion@0
            inputs: { versionSpec: '3.12' }
          - script: |
              pip install -r requirements.txt
              python -m pytest tests/ --junitxml=results.xml
            displayName: 'Test'
          - task: Docker@2
            inputs:
              containerRegistry: 'myacr-connection'
              repository: 'myapi'
              command: 'buildAndPush'
              Dockerfile: 'Dockerfile'
              tags: '$(Build.BuildId)'

  - stage: Deploy
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: DeployProd
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebAppContainer@1
                  inputs:
                    azureSubscription: 'my-sub'
                    appName: 'myapp-prod'
                    imageName: 'myacr.azurecr.io/myapi:$(Build.BuildId)'
```

> ⚠️ **Gotcha:** Azure Pipelines gives 1 free parallel job (1800 min/month) for public projects, and 1 free job for private. Request more free parallelism or purchase additional parallel jobs for teams.

---

# Chapter 14 — Azure Serverless & App Platform

> Additional serverless and app hosting services beyond Functions (covered in Ch 1).

---

## 14.1 Azure Functions Deep Dive

**Advanced patterns beyond Ch 1 basics:**

**Durable Functions** — orchestrate multi-step workflows:

```python
# Orchestrator function — chains multiple activities
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    result1 = yield context.call_activity("Step1_Validate", input_data)
    result2 = yield context.call_activity("Step2_Process", result1)
    result3 = yield context.call_activity("Step3_Notify", result2)
    return result3
```

**Fan-out / Fan-in pattern:**

```
  Orchestrator
       │
       ├──► Activity A ──┐
       ├──► Activity B ──┤──► Aggregate results
       └──► Activity C ──┘
```

---

## 14.2 Azure Static Web Apps

**What is it?** Host static websites (React, Angular, Vue, Hugo) with built-in CI/CD from GitHub, automatic SSL, global CDN, and optional serverless API backend.

**Input → Output:**

```
  You give it:  GitHub repo with static site + optional /api folder (Azure Functions)
  It gives you: Globally distributed website with HTTPS, CI/CD on every push, free tier
```

**Example:**

```bash
# Create a Static Web App (connected to GitHub)
az staticwebapp create \
    --name swa-demo --resource-group rg-demo \
    --source https://github.com/user/mysite \
    --branch main --location eastus \
    --app-location "/" --api-location "api" \
    --output-location "build"
```

**Diagram:**

```
  GitHub Repo
       │
       │ git push (triggers CI/CD)
       ▼
  ┌──────────────────────────────────────────┐
  │  Azure Static Web Apps                   │
  │                                          │
  │  /              → React SPA (global CDN) │
  │  /api/users     → Azure Function (API)   │
  │  /api/orders    → Azure Function (API)   │
  │                                          │
  │  HTTPS ✓  Custom domain ✓  Free tier ✓  │
  └──────────────────────────────────────────┘
```

> ⚠️ **Gotcha:** Free tier is limited to 2 custom domains and 0.5 GB bandwidth/day. Standard tier ($9/month) removes limits. Great for portfolios, docs sites, and SPAs.

---

# Chapter 15 — Hands-On Practice Tasks

> Complete these tasks to build real Azure skills. They're structured from beginner to advanced, covering all chapters.

---

## 15.1 Compute Tasks

**Task 1 — Deploy a Linux VM and serve a web page**
```
  1. Create a resource group "rg-lab-compute"
  2. Create an Ubuntu 22.04 VM with Standard_B1s size
  3. Open port 80 via NSG
  4. SSH into the VM and install Nginx
  5. Create a custom index.html with your name
  6. Access the page from your browser using the VM's public IP
  7. Deallocate the VM when done (save costs)
```
**Skills tested:** VM creation, NSG rules, SSH, web server setup, cost management

---

**Task 2 — Deploy an App Service with CI/CD**
```
  1. Create an App Service Plan (Linux, B1 tier)
  2. Create a Web App (Node.js or Python runtime)
  3. Deploy a sample app from a GitHub repo using deployment center
  4. Configure a custom startup command
  5. Enable Application Insights for monitoring
  6. View live logs using "az webapp log tail"
  7. Scale up to S1, then scale out to 2 instances
```
**Skills tested:** App Service, deployment, scaling, monitoring

---

**Task 3 — Serverless image processing pipeline**
```
  1. Create a Storage Account with a "raw-images" container
  2. Create an Azure Function (Blob trigger)
  3. When an image is uploaded to "raw-images":
     - Function triggers automatically
     - Logs the image name and size
     - Copies the blob to a "processed" container
  4. Test by uploading an image via CLI
  5. Verify the processed container has the copy
```
**Skills tested:** Functions, Blob trigger, Storage SDK, event-driven architecture

---

## 15.2 Networking Tasks

**Task 4 — Build a multi-tier network**
```
  1. Create VNet (10.0.0.0/16) with 3 subnets:
     - snet-web (10.0.1.0/24) — public-facing
     - snet-api (10.0.2.0/24) — internal
     - snet-db  (10.0.3.0/24) — restricted
  2. Create NSG for each subnet:
     - snet-web: allow HTTP(80), HTTPS(443) from Internet
     - snet-api: allow 8080 from snet-web ONLY
     - snet-db:  allow 5432 from snet-api ONLY
  3. Deploy a VM in snet-web, verify it can reach snet-api
  4. Verify snet-web CANNOT directly reach snet-db
```
**Skills tested:** VNet, subnets, NSGs, network security design

---

**Task 5 — Set up VNet peering and Bastion**
```
  1. Create two VNets: vnet-hub (10.0.0.0/16) and vnet-spoke (10.1.0.0/16)
  2. Peer vnet-hub ↔ vnet-spoke (bidirectional)
  3. Deploy a VM in each VNet (no public IPs)
  4. Deploy Azure Bastion in vnet-hub
  5. RDP/SSH into hub VM via Bastion (browser)
  6. From hub VM, ping spoke VM (verify peering works)
  7. Delete Bastion when done ($$$)
```
**Skills tested:** VNet peering, Bastion, hub-spoke topology, private connectivity

---

**Task 6 — Load balancer with health probes**
```
  1. Create 2 VMs running Nginx in an availability set
  2. Create a Standard Load Balancer with:
     - Frontend public IP
     - Backend pool with both VMs
     - Health probe on port 80
     - Load balancing rule (port 80 → port 80)
  3. Access the LB public IP — verify traffic alternates between VMs
  4. Stop one VM — verify LB detects failure and routes to healthy VM
```
**Skills tested:** Load Balancer, health probes, high availability

---

## 15.3 Identity & Governance Tasks

**Task 7 — RBAC and least privilege**
```
  1. Create two resource groups: rg-dev and rg-prod
  2. Create a user "dev-user" in Entra ID
  3. Assign "Contributor" role on rg-dev only
  4. Assign "Reader" role on rg-prod only
  5. Sign in as dev-user and verify:
     - CAN create resources in rg-dev ✓
     - CANNOT create resources in rg-prod ✗
     - CAN view resources in rg-prod ✓
  6. Create a custom role "VM Restarter" (restart VMs only)
```
**Skills tested:** RBAC, custom roles, principle of least privilege

---

**Task 8 — Managed Identity + Key Vault**
```
  1. Create a Key Vault with RBAC authorization
  2. Store a secret: "db-password" = "MySecret123"
  3. Create an App Service with system-assigned managed identity
  4. Grant the managed identity "Key Vault Secrets User" role
  5. In the app code, read the secret using DefaultAzureCredential
  6. Verify NO connection string or password is stored in app config
  7. Disable public access to Key Vault (VNet/PE only)
```
**Skills tested:** Managed Identity, Key Vault, zero-secret architecture

---

**Task 9 — Azure Policy enforcement**
```
  1. Assign policy: "Allowed locations" (eastus and westus only)
  2. Try creating a VM in "southeastasia" — verify it's DENIED
  3. Assign policy: "Require environment tag" on a resource group
  4. Try creating a storage account without the tag — verify DENIED
  5. Create a policy initiative with both policies
  6. Check compliance dashboard
```
**Skills tested:** Azure Policy, deny effect, initiatives, compliance

---

## 15.4 Storage & Security Tasks

**Task 10 — Blob storage lifecycle**
```
  1. Create a Storage Account (StorageV2, LRS)
  2. Create containers: "active", "archive"
  3. Upload 5 files to "active" container
  4. Generate a SAS token (read-only, 1 hour expiry)
  5. Access a blob using the SAS URL from Incognito browser
  6. Create a lifecycle policy:
     - Move to Cool tier after 30 days
     - Move to Archive after 90 days
     - Delete after 365 days
  7. Restrict storage to VNet access only (firewall)
```
**Skills tested:** Blob storage, SAS tokens, lifecycle management, network security

---

**Task 11 — Backup and restore a VM**
```
  1. Create a VM and install a web app on it
  2. Create a Recovery Services Vault
  3. Enable backup (daily, 30-day retention)
  4. Take an on-demand backup
  5. Make changes to the VM (modify files, break the app)
  6. Restore the VM from the backup
  7. Verify the app is back to its original state
```
**Skills tested:** Azure Backup, Recovery Services Vault, restore operations

---

## 15.5 Monitoring & IaC Tasks

**Task 12 — Full monitoring setup**
```
  1. Create a Log Analytics Workspace
  2. Create an App Service and enable diagnostic settings
  3. Create Application Insights (workspace-based)
  4. Generate some traffic to the app
  5. Write KQL queries to find:
     - Request count by URL in the last hour
     - Average response time
     - Failed requests (status >= 500)
  6. Create an alert: "If error rate > 5%, email devops team"
  7. Create a dashboard with key metrics
```
**Skills tested:** Azure Monitor, Log Analytics, KQL, App Insights, Alerts

---

**Task 13 — Deploy infrastructure with Bicep**
```
  1. Write a Bicep file that creates:
     - Resource Group (use subscription-level deployment)
     - VNet with 2 subnets
     - NSG with HTTPS rule
     - Storage Account
     - App Service Plan + Web App
  2. Use parameters for environment (dev/prod)
  3. Use modules (separate network.bicep, storage.bicep)
  4. Run "what-if" to preview changes
  5. Deploy to Azure
  6. Make a change (add subnet) and redeploy
  7. Verify incremental deployment (only new subnet created)
```
**Skills tested:** Bicep, modules, parameters, what-if, declarative IaC

---

## 15.6 Database & Messaging Tasks

**Task 14 — Full-stack with Azure SQL + App Service**
```
  1. Create Azure SQL Server + Database (serverless tier)
  2. Create App Service with Node.js/Python
  3. Connect app to SQL using managed identity (no password!)
  4. Deploy a simple CRUD API (create/read/update/delete users)
  5. Enable private endpoint for SQL (disable public access)
  6. Test from App Service (should work via VNet integration)
  7. Enable SQL auditing and review logs
```
**Skills tested:** Azure SQL, App Service, managed identity, private endpoints

---

**Task 15 — Event-driven architecture with Service Bus**
```
  1. Create Service Bus namespace (Standard tier)
  2. Create a "orders" topic with 2 subscriptions:
     - "fulfillment" (processes orders)
     - "notifications" (sends email confirmations)
  3. Create an Azure Function for each subscription
  4. Publish a test message to the topic
  5. Verify both Functions process the message independently
  6. Send a malformed message — verify it goes to dead-letter queue
  7. Read and inspect the dead-letter message
```
**Skills tested:** Service Bus topics, pub/sub, Functions triggers, dead-letter

---

## 15.7 End-to-End Capstone Tasks

**Task 16 — Production-ready 3-tier application**
```
  Deploy a complete 3-tier app with production best practices:

  ┌─────────────────────────────────────────────────────────┐
  │  ARCHITECTURE                                          │
  │                                                        │
  │  Internet                                              │
  │      │                                                 │
  │      ▼                                                 │
  │  App Gateway (WAF, SSL)                                │
  │      │                                                 │
  │      ▼                                                 │
  │  App Service (VNet integrated, managed identity)       │
  │      │                                                 │
  │      ▼                                                 │
  │  Azure SQL (private endpoint, no public access)        │
  │      │                                                 │
  │  Key Vault (secrets via managed identity)              │
  │  Azure Monitor (App Insights + Log Analytics)          │
  │  Backup (Recovery Services Vault, daily)               │
  └─────────────────────────────────────────────────────────┘

  Checklist:
  □ VNet with proper subnet segmentation
  □ NSGs with least-privilege rules
  □ No public IP on SQL or Key Vault
  □ All secrets in Key Vault (zero in code/config)
  □ Managed identity for all service-to-service auth
  □ Monitoring with alerts (CPU, errors, latency)
  □ Backup policy for database and app
  □ Tags on all resources (environment, team, cost-center)
  □ Resource locks on production resources
  □ Budget alert at 80% threshold
```
**Skills tested:** Everything from Chapters 1-14. This is the "final exam."

---

# Chapter 16 — Interview Questions & Answers

> Questions organized by topic area. Answers are concise — expand in interviews with real-world examples.

---

## 16.1 Compute Interview Questions

**Q1: What is the difference between Azure App Service and Azure VMs?**
> App Service is PaaS — Azure manages the OS, patching, scaling, and load balancing. VMs are IaaS — you manage everything from OS level up. Use App Service for web apps, VMs for custom software or OS-level control.

**Q2: When would you use Azure Functions vs Container Apps?**
> Functions for short-lived, event-driven code (process a queue message, respond to webhook). Container Apps for long-running microservices that need persistent connections, sidecars, or Dapr integration. Functions scale to zero; Container Apps can too but support more complex architectures.

**Q3: How does VMSS provide high availability?**
> VMSS spreads instances across fault domains and update domains within an availability set or across availability zones. It auto-scales based on metrics (CPU, memory, custom). Combined with a load balancer, unhealthy instances are replaced automatically.

**Q4: What is the difference between scaling up and scaling out?**
> Scale UP = bigger machine (more CPU/RAM on same instance). Scale OUT = more machines (add instances behind a load balancer). Scale out is preferred for availability — a single big machine is still a single point of failure.

**Q5: Explain Azure Container Instances vs AKS.**
> ACI = simple, single-container or small groups, no orchestration, fast startup (~30 seconds). AKS = full Kubernetes, orchestrates hundreds of containers, auto-scaling, self-healing, service mesh. ACI for quick jobs/testing, AKS for production microservices.

---

## 16.2 Networking Interview Questions

**Q6: What is the difference between NSG and Azure Firewall?**
> NSG = free, stateful packet filter at subnet/NIC level (L3/L4). Azure Firewall = managed centralized firewall with FQDN filtering, threat intelligence, DNAT, and application rules (L3-L7). NSG for basic filtering, Firewall for enterprise hub-spoke security.

**Q7: Explain VNet peering. Is it transitive?**
> VNet peering connects two VNets for private IP communication via Azure backbone (no internet). It is NOT transitive — if VNet A peers with B, and B peers with C, A cannot reach C unless explicitly peered. Use hub-spoke with gateway transit for transitive routing.

**Q8: What is the difference between Application Gateway and Azure Load Balancer?**
> Load Balancer = L4 (TCP/UDP), distributes by IP:port, no URL awareness, regional. Application Gateway = L7 (HTTP/HTTPS), understands URLs/headers, path-based routing, SSL termination, WAF, cookie affinity. Use LB for non-HTTP, App GW for web apps.

**Q9: How do Private Endpoints work?**
> A private endpoint creates a NIC with a private IP in your VNet that maps to a PaaS service (Storage, SQL, Key Vault). DNS is configured to resolve the service FQDN to this private IP instead of the public IP. Traffic never leaves the Azure backbone.

**Q10: When would you use ExpressRoute over VPN Gateway?**
> ExpressRoute: private dedicated circuit, 50 Mbps-100 Gbps, <10ms latency, 99.95% SLA, no internet involvement. VPN: encrypted tunnel over internet, up to ~1.25 Gbps, variable latency. Use ExpressRoute for financial services, large data transfers, or compliance-sensitive workloads.

---

## 16.3 Identity & Security Interview Questions

**Q11: What is the difference between authentication and authorization?**
> Authentication = proving WHO you are (Entra ID verifies your identity with password + MFA). Authorization = deciding WHAT you can do (RBAC checks if you have permission to perform an action on a resource at a scope).

**Q12: Explain Azure RBAC with an example.**
> RBAC = Principal + Role + Scope. Example: "Jane (principal) is Contributor (role) on rg-prod (scope)." This means Jane can create, modify, and delete resources in rg-prod but cannot assign roles to others. Permissions inherit downward (management group → subscription → resource group → resource).

**Q13: What are Managed Identities and why are they important?**
> Managed identities are Azure-managed credentials for resources (VMs, App Services, Functions). The app uses a token from Entra ID instead of storing passwords. System-assigned = tied to one resource. User-assigned = independent, multi-resource. Important because: zero secrets to manage, no rotation needed, no risk of leaked credentials.

**Q14: What is Conditional Access?**
> If-then policies for sign-in: "IF signing in from unknown device AND accessing production, THEN require MFA AND compliant device." It evaluates conditions (user, location, device, risk) and applies controls (grant, block, MFA). Requires Entra ID P1/P2.

**Q15: How would you secure a Key Vault in production?**
> 1) Enable RBAC authorization (not access policies). 2) Use managed identities for access. 3) Enable private endpoint (disable public access). 4) Enable soft delete + purge protection. 5) Enable diagnostic logging. 6) Use "Key Vault Secrets User" role (least privilege). 7) Rotate secrets regularly.

---

## 16.4 Storage & Database Interview Questions

**Q16: Explain Azure Storage redundancy options.**
> LRS = 3 copies in 1 datacenter (cheapest, no region protection). ZRS = 3 copies across 3 availability zones (single-region HA). GRS = 3 local + 3 in paired region (region failure protection, read from secondary with RA-GRS). GZRS = ZRS + GRS combined (highest durability).

**Q17: What is the difference between Blob access tiers?**
> Hot = frequent access, highest storage cost, lowest access cost. Cool = 30+ days infrequent, lower storage, higher access. Cold = 90+ days. Archive = 180+ days, cheapest storage but 1-15 hours to rehydrate. Use lifecycle policies to auto-tier based on age.

**Q18: When would you use Cosmos DB vs Azure SQL?**
> Cosmos DB: NoSQL, globally distributed, multi-model (document/graph/key-value), <10ms latency worldwide, auto-scale. Azure SQL: relational, ACID transactions, complex joins, stored procedures, T-SQL. Use Cosmos for global apps with simple data models; SQL for transactional apps with complex relationships.

**Q19: How do you secure an Azure SQL Database?**
> 1) Private endpoint (no public access). 2) Entra ID authentication (not SQL auth). 3) TDE enabled (default). 4) Auditing enabled. 5) Firewall rules (allow only VNet/specific IPs). 6) Managed identity from app (no passwords). 7) Advanced Threat Protection enabled.

---

## 16.5 Governance & Monitoring Interview Questions

**Q20: What is Azure Policy and how is it different from RBAC?**
> RBAC controls WHO can do WHAT (user permissions). Policy controls WHAT can be created/configured (resource rules). Example: RBAC says "Jane can create VMs." Policy says "All VMs must use managed disks." They work together — RBAC grants the ability, Policy enforces the standards.

**Q21: Explain Azure Monitor architecture.**
> Azure Monitor is the central hub. Sources (VMs, apps, network) send metrics (numeric) and logs (text) to Monitor. Metrics go to the metrics database (auto-collected, 93 days retention). Logs go to Log Analytics workspace (KQL queries). Alerts watch both and trigger Action Groups (email, SMS, webhook, Function).

**Q22: What is the difference between Azure Backup and Azure Site Recovery?**
> Backup = point-in-time snapshots for data recovery (restore files, databases, VMs from backup). RPO: hours/daily. ASR = real-time replication for business continuity (failover entire VMs to another region). RPO: ~30 seconds. Backup for "I deleted a file." ASR for "The entire region is down."

**Q23: How do you control costs in Azure?**
> 1) Tags for cost allocation. 2) Budgets with alerts (50%, 80%, 100%). 3) Azure Advisor recommendations. 4) Reserved instances for stable workloads (30-60% savings). 5) Auto-shutdown dev VMs. 6) Right-size over-provisioned resources. 7) Delete orphaned resources (disks, PIPs). 8) Lifecycle policies for storage (hot → cool → archive).

---

## 16.6 IaC & DevOps Interview Questions

**Q24: What is Infrastructure as Code and why is it important?**
> IaC = managing infrastructure through code files instead of manual portal clicks. Benefits: repeatable (deploy same infra to dev/staging/prod), version-controlled (Git), auditable (who changed what), reviewable (PR reviews for infra changes), self-documenting. On Azure, use Bicep (Azure-only) or Terraform (multi-cloud).

**Q25: Explain the difference between Bicep and Terraform.**
> Bicep: Azure-native DSL, compiles to ARM JSON, state managed by Azure, easy to learn, no state file management. Terraform: multi-cloud (Azure + AWS + GCP), HCL language, requires state management (remote backend), larger community, 3000+ providers. Use Bicep for Azure-only shops, Terraform for multi-cloud.

**Q26: What is a Terraform state file and why is it important?**
> The state file maps Terraform resources to real Azure resources. It tracks what exists so Terraform knows what to create, update, or destroy. Store remotely in Azure Blob Storage with state locking (prevents concurrent modifications). Never commit to Git (contains secrets). Losing state = Terraform loses track of your infrastructure.

**Q27: Describe a CI/CD pipeline for deploying to Azure.**
> Trigger: push to main branch. Stage 1 (Build): install deps, run tests, build Docker image, push to ACR. Stage 2 (Deploy to staging): deploy container to staging App Service, run integration tests. Stage 3 (Deploy to production): approval gate, deploy to production App Service, smoke tests. Rollback: if health check fails, revert to previous image tag.

---

## 16.7 Scenario-Based Interview Questions

**Q28: Design a highly available web application on Azure.**
```
  Answer structure:
  ┌───────────────────────────────────────────────────┐
  │  Azure Front Door (global LB + WAF + CDN)        │
  │       │                                           │
  │       ├── Region 1 (East US)                      │
  │       │   ├── App Service (S1, 2+ instances)     │
  │       │   ├── Azure SQL (failover group, primary) │
  │       │   ├── Redis Cache (Standard)              │
  │       │   └── Key Vault (private endpoint)        │
  │       │                                           │
  │       └── Region 2 (West US)                      │
  │           ├── App Service (S1, 2+ instances)     │
  │           ├── Azure SQL (failover, secondary)    │
  │           ├── Redis Cache (Standard)              │
  │           └── Key Vault (private endpoint)        │
  │                                                   │
  │  Monitoring: App Insights + Log Analytics         │
  │  Backup: Daily backups with GRS vault             │
  │  Identity: Managed identities for all auth        │
  └───────────────────────────────────────────────────┘
```

**Q29: Your team accidentally deleted a production database. How do you recover?**
> 1) Check Azure SQL's built-in PITR (Point-in-Time Restore) — available up to 35 days. 2) If within retention period: restore to a new database at the point before deletion. 3) If Recovery Services Vault was configured: restore from backup. 4) If failover group exists: check secondary replica. 5) Prevention: enable resource locks (CanNotDelete) on production resources, enable soft delete, regular backup testing.

**Q30: How would you migrate an on-premises app to Azure?**
> Assessment: Use Azure Migrate to discover and assess on-prem servers. Strategy: choose approach — Rehost (lift & shift VMs to Azure VMs), Replatform (move to App Service/containers with minimal changes), Rearchitect (redesign for cloud-native using Functions/AKS). Data: use Azure Database Migration Service for databases. Network: set up VPN Gateway or ExpressRoute for hybrid connectivity during migration. Phased approach: migrate dev first, validate, then staging, then production.

---

# 📚 Handbook Complete!

```
  ╔══════════════════════════════════════════════════════╗
  ║  Azure Services Handbook — Summary                  ║
  ╠══════════════════════════════════════════════════════╣
  ║                                                      ║
  ║  16 Chapters  │  70+ Azure Services                 ║
  ║  15 Tasks     │  30 Interview Questions              ║
  ║  50+ CLI      │  25+ ASCII Diagrams                 ║
  ║  Examples     │  20+ Decision Guide Tables           ║
  ║                                                      ║
  ║  Chapters covered:                                   ║
  ║  ├── 1.  Compute Services                           ║
  ║  ├── 2.  Networking Services                        ║
  ║  ├── 3.  Identity & Access Management               ║
  ║  ├── 4.  Governance & Compliance                    ║
  ║  ├── 5.  Storage Services                           ║
  ║  ├── 6.  Security Services                          ║
  ║  ├── 7.  Backup & Disaster Recovery                 ║
  ║  ├── 8.  Monitoring & Observability                 ║
  ║  ├── 9.  Container & Registry Services              ║
  ║  ├── 10. Resource Manager & IaC                     ║
  ║  ├── 11. Database Services                          ║
  ║  ├── 12. Messaging & Integration                    ║
  ║  ├── 13. DevOps Services                            ║
  ║  ├── 14. Serverless & App Platform                  ║
  ║  ├── 15. Hands-On Practice Tasks                    ║
  ║  └── 16. Interview Questions & Answers              ║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
```

> **Next steps:** Work through the tasks in Chapter 15 sequentially. Each builds on skills from previous tasks. The capstone task (Task 16) tests everything together.
