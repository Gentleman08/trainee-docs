# 🔷 Batch 3: Containers, Databases & Messaging

> **Level:** Intermediate | **Estimated Total Time:** 15–20 days | **Scenarios:** 6 (numbered 11–16)
>
> This batch takes you into the world of containers, orchestration, databases, and event-driven architecture — the backbone of modern cloud-native applications.

---

## 📑 Table of Contents

- [Scenario 11: ACR & ACI](#scenario-11-azure-container-registry-acr--container-instances-aci)
- [Scenario 12: AKS Fundamentals](#scenario-12-azure-kubernetes-service-aks---fundamentals)
- [Scenario 13: AKS Advanced](#scenario-13-aks-advanced---production-grade)
- [Scenario 14: Azure SQL & Cosmos DB](#scenario-14-azure-sql--cosmos-db)
- [Scenario 15: Messaging & Event-Driven](#scenario-15-messaging--event-driven-architecture)
- [Scenario 16: Redis Cache & CDN](#scenario-16-azure-cache-for-redis--cdn)

---

## Scenario 11: Azure Container Registry (ACR) & Container Instances (ACI)

### 🎯 Objective
Master container image lifecycle: build, store, scan, and deploy container images. Use ACR for private image hosting and ACI for quick container deployments without orchestration overhead.

### 📦 App Description
**A microservices application with 3-4 services** (user service, product service, notification service, API gateway) — each as a separate container image. Build, push, scan, and deploy them independently.

### 🏗️ Architecture Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                 AZURE CONTAINER REGISTRY                      │
│               "acrprodeastus001" (Premium)                     │
│                                                              │
│  Repositories:                                               │
│  ├── myapp/api-gateway:v1.2.3                                │
│  ├── myapp/user-service:v1.1.0                               │
│  ├── myapp/product-service:v2.0.1                            │
│  └── myapp/notification-service:v1.0.5                       │
│                                                              │
│  Features:                                                   │
│  • Geo-replication (Premium): eastus + westeurope            │
│  • Vulnerability scanning (Defender for Containers)          │
│  • ACR Tasks: auto-build on git commit                       │
│  • Content trust: signed images                              │
│  • Webhooks → trigger deployments                            │
└────────────────────────┬─────────────────────────────────────┘
                         │ Pull images
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
  ┌──────────────┐ ┌──────────┐ ┌──────────────┐
  │     ACI      │ │   AKS    │ │ App Service  │
  │ (quick test) │ │ (prod)   │ │ (container)  │
  └──────────────┘ └──────────┘ └──────────────┘
```

### ✅ Hands-on Tasks

#### Part A: ACR Setup
- [ ] Create ACR at each tier — understand the differences:
  - Basic: 10GB, no geo-replication, no content trust
  - Standard: 100GB, no geo-replication
  - Premium: 500GB, geo-replication, Private Endpoint, content trust
- [ ] Build an image locally and push to ACR
- [ ] Use ACR Tasks for server-side builds (no local Docker needed!):
```bash
# Quick build in the cloud
az acr build --registry acrprodeastus001 --image myapp/api-gateway:v1.0 .

# Auto-build on git commit
az acr task create --registry acrprodeastus001 --name build-api \
  --image myapp/api-gateway:{{.Run.ID}} \
  --context https://github.com/yourrepo.git \
  --file Dockerfile --git-access-token <token>
```

- [ ] Enable vulnerability scanning with Microsoft Defender for Containers
- [ ] Configure ACR purge to auto-delete images older than 30 days
- [ ] Set up geo-replication (Premium tier) to a second region

> ⚠️ **DevOps Gotcha:** ACR names must be globally unique, 5-50 chars, alphanumeric ONLY (no hyphens!). Also, ACR Basic tier has aggressive throttling limits — only 1000 read operations per minute. In CI/CD pipelines pulling many images in parallel, you'll hit `429 Too Many Requests`. Use Standard or Premium for anything beyond basic testing.

#### Part B: ACI Deployment
- [ ] Deploy a single container to ACI from your ACR image
- [ ] Deploy a multi-container group (API + sidecar logger) using YAML
- [ ] Attach Azure Files volume for persistent storage
- [ ] Enable VNet integration (deploy ACI into a VNet subnet)
- [ ] Configure restart policy: Always, OnFailure, Never
- [ ] View container logs: `az container logs`

```bash
# Simple ACI deployment
az container create \
  --resource-group rg-portfolio-dev-eastus \
  --name aci-api-gateway \
  --image acrprodeastus001.azurecr.io/myapp/api-gateway:v1.0 \
  --registry-login-server acrprodeastus001.azurecr.io \
  --registry-username <acr-user> \
  --registry-password <acr-password> \
  --cpu 1 --memory 1.5 \
  --ports 80 443 \
  --ip-address Public
```

> ⚠️ **DevOps Gotcha:** ACI with VNet integration requires a **delegated subnet** (subnet delegated to `Microsoft.ContainerInstance/containerGroups`). You can't use a regular subnet. Also, VNet-integrated ACI containers get NO public IP — they're only accessible from within the VNet. Many people deploy ACI into a VNet expecting public access and wonder why it's unreachable.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `ImagePullBackOff` / `401 Unauthorized` | ACR credentials wrong or expired | Use `az acr credential show`; or use Managed Identity/service principal |
| ACR build fails | Dockerfile syntax error or missing context files | Test build locally first; check build logs |
| ACI container restart loop | App crashing on startup | Check logs: `az container logs`; fix startup config |
| ACI VNet container unreachable | No public IP with VNet integration | Access from within VNet; or remove VNet integration for public IP |
| ACR throttling (429) | Basic tier rate limits | Upgrade to Standard/Premium tier |
| Geo-replicated image not available in second region | Replication delay | Wait a few minutes; check replication status |

### 💰 Cost Tips
- ACR Basic: ~$5/month, Standard: ~$20/month, Premium: ~$50/month
- ACI: ~$0.0025/second per vCPU + $0.0000025/second per GB RAM (pay only while running)
- ACI is billed per-second — great for short-lived tasks
- DELETE ACI containers when done — they keep running (and billing)

### ✔️ Verification Checklist
- [ ] Images pushed to ACR and visible in repositories
- [ ] ACR Tasks auto-build on git push (if configured)
- [ ] Vulnerability scan results visible in Defender for Cloud
- [ ] ACI container running and accessible
- [ ] Multi-container group with sidecar pattern works
- [ ] ACI with VNet integration can reach private resources

### 🔍 Behind the Scenes
- **ACR** is backed by Azure Storage (blob storage). Images are stored as layers (blobs) with manifests. Geo-replication copies all layers to secondary regions.
- **ACR Tasks** spin up a temporary build VM, clone your repo, run `docker build`, push the image, then destroy the VM. You never see or manage this VM.
- **ACI** provisions a Hyper-V isolated container on Azure's container infrastructure. Each container group gets its own Hyper-V sandbox — your containers are isolated at the hypervisor level, not just namespace level.

---

## Scenario 12: Azure Kubernetes Service (AKS) - Fundamentals

### 🎯 Objective
Deploy and manage a Kubernetes cluster on Azure. Master workload deployment, networking, storage, monitoring, and the most common troubleshooting scenarios.

### 📦 App Description
**A full microservices e-commerce platform (5+ services)** with API gateway, auth service, product catalog, cart, and order processing. Deploy on AKS with proper namespaces, resource limits, and health checks.

### 🏗️ Architecture Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                      AKS CLUSTER                              │
│                  "aks-ecom-prod-eastus"                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ System Node Pool (Standard_D2s_v3 × 3)               │    │
│  │  • CoreDNS, kube-proxy, metrics-server                │    │
│  │  • Taints: CriticalAddonsOnly=true:NoSchedule         │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ User Node Pool "apppool" (Standard_D4s_v3 × 2-10)    │    │
│  │  • Auto-scaler: min=2, max=10                         │    │
│  │                                                       │    │
│  │  ┌─────────────────────────────────────────────┐      │    │
│  │  │ Namespace: ecommerce                         │      │    │
│  │  │                                              │      │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌──────────┐      │      │    │
│  │  │  │ api-gw  │ │ auth-   │ │ product- │      │      │    │
│  │  │  │ (nginx  │ │ service │ │ catalog  │      │      │    │
│  │  │  │ ingress)│ │ (3 pods)│ │ (3 pods) │      │      │    │
│  │  │  └─────────┘ └─────────┘ └──────────┘      │      │    │
│  │  │                                              │      │    │
│  │  │  ┌──────────┐ ┌──────────┐                  │      │    │
│  │  │  │ cart-svc │ │ order-   │                  │      │    │
│  │  │  │ (2 pods) │ │ processor│                  │      │    │
│  │  │  │          │ │ (2 pods) │                  │      │    │
│  │  │  └──────────┘ └──────────┘                  │      │    │
│  │  │                                              │      │    │
│  │  │  Resource Quotas: 8 CPU, 16Gi RAM max        │      │    │
│  │  └─────────────────────────────────────────────┘      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Networking: Azure CNI | Network Policy: Calico              │
│  Ingress: NGINX Ingress Controller                           │
│  Storage: Azure Disk (ReadWriteOnce), Azure Files (ReadMany) │
│  Monitoring: Container Insights + Prometheus                  │
└──────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Cluster Creation
- [ ] Create an AKS cluster with system and user node pools
- [ ] Understand networking options:
  - **kubenet**: simple, pod IPs from a separate range, uses NAT — limited to 400 nodes
  - **Azure CNI**: pods get VNet IPs directly — uses more IPs, enables Network Policies
  - **Azure CNI Overlay**: pods get overlay IPs but VNet integration for services
- [ ] Enable Container Insights for monitoring
- [ ] Connect with `az aks get-credentials` and verify with `kubectl get nodes`

```bash
az aks create \
  --resource-group rg-portfolio-dev-eastus \
  --name aks-ecom-dev-eastus \
  --node-count 2 \
  --node-vm-size Standard_D2s_v3 \
  --network-plugin azure \
  --network-policy calico \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --nodepool-name systempool \
  --enable-cluster-autoscaler \
  --min-count 2 --max-count 5

# Add user node pool
az aks nodepool add \
  --resource-group rg-portfolio-dev-eastus \
  --cluster-name aks-ecom-dev-eastus \
  --name apppool \
  --node-count 2 \
  --node-vm-size Standard_D4s_v3 \
  --enable-cluster-autoscaler \
  --min-count 2 --max-count 10
```

> ⚠️ **DevOps Gotcha:** Azure CNI assigns a VNet IP to EVERY pod. With 30 pods per node and 10 nodes, that's 300 IPs from your subnet. A /24 subnet (251 usable IPs) would be exhausted! Plan subnet sizes carefully: `/22` or larger for AKS with Azure CNI. Use Azure CNI Overlay if IP exhaustion is a concern.

#### Part B: Deploy Workloads
- [ ] Create namespaces for environments: `dev`, `staging`, `production`
- [ ] Set up resource quotas and limit ranges per namespace
- [ ] Deploy microservices with Deployments (replicas, resource limits, health checks)
- [ ] Expose services: ClusterIP (internal), LoadBalancer (external), NodePort
- [ ] Set up NGINX Ingress Controller with path-based routing
- [ ] Configure ConfigMaps for non-sensitive configuration
- [ ] Configure Secrets for sensitive data (or use Key Vault CSI driver)

```yaml
# Example Deployment with best practices
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-catalog
  namespace: ecommerce
spec:
  replicas: 3
  selector:
    matchLabels:
      app: product-catalog
  template:
    metadata:
      labels:
        app: product-catalog
    spec:
      containers:
      - name: product-catalog
        image: acrprodeastus001.azurecr.io/myapp/product-service:v2.0.1
        ports:
        - containerPort: 3000
        resources:
          requests:
            cpu: 250m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
        env:
        - name: DB_CONNECTION
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: connection-string
```

> ⚠️ **DevOps Gotcha:** ALWAYS set resource `requests` AND `limits`. Without requests, the scheduler can't make intelligent placement decisions. Without limits, a misbehaving pod can consume all node resources and cause other pods to get OOMKilled. The request determines scheduling; the limit determines the ceiling.

#### Part C: Persistent Storage
- [ ] Create a PersistentVolumeClaim with Azure Disk (ReadWriteOnce)
- [ ] Create a PVC with Azure Files (ReadWriteMany — shared across pods)
- [ ] Understand storage classes: `managed-premium`, `azurefile-csi`, `azurefile-csi-premium`
- [ ] Test: kill a pod with a PV attached, verify data persists on the new pod

#### Part D: Networking & Network Policies
- [ ] Configure Network Policies (Calico) to restrict pod-to-pod communication
- [ ] Policy: Only API gateway can reach auth service, only order-processor can reach cart service
- [ ] Default deny all ingress for the namespace, then whitelist specific flows
- [ ] Verify network policies with `kubectl exec` and `curl` between pods

#### Part E: Monitoring & Debugging
- [ ] Enable Container Insights and view in Azure Monitor
- [ ] Use `kubectl top nodes` and `kubectl top pods` for resource usage
- [ ] Debug common issues:
  - `CrashLoopBackOff`: `kubectl logs <pod> --previous`
  - `ImagePullBackOff`: check image name and registry credentials
  - `Pending` pods: `kubectl describe pod <pod>` — check events
  - `OOMKilled`: increase memory limits
  - `Node NotReady`: `kubectl describe node` — check conditions
- [ ] Set up alerts for pod restarts and node issues

> ⚠️ **DevOps Gotcha:** `kubectl logs` only shows logs from the CURRENT container. If a pod crashed and restarted, the current logs are from the NEW instance. Use `kubectl logs <pod> --previous` to see logs from the CRASHED instance — that's where the error is. Many developers miss this and see "clean" logs from the restarted container.

### 🔧 Edge Cases & Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pod stuck in `Pending` | Insufficient resources or no matching node | Check `kubectl describe pod`; scale node pool |
| `CrashLoopBackOff` | App crashing on startup | `kubectl logs <pod> --previous`; fix startup errors |
| `ImagePullBackOff` | Wrong image name, no registry auth, or image doesn't exist | Verify image tag; check `imagePullSecrets` |
| `OOMKilled` | Container exceeded memory limit | Increase memory limit; fix memory leaks |
| Node `NotReady` | Node VM issue, kubelet crash, or disk pressure | `kubectl describe node`; if persistent, cordon + drain + delete |
| DNS resolution fails inside pods | CoreDNS pods unhealthy | Check CoreDNS pods in `kube-system` namespace |
| Ingress returns 404 | Ingress path mismatch or backend service not found | Verify ingress rules and service names/ports |

### 💰 Cost Tips
- **AKS control plane: FREE** — you only pay for worker node VMs
- Use **B-series VMs** for dev/test node pools (~$30/month per node)
- **AKS stop/start**: `az aks stop --name <cluster>` stops all nodes (no compute charges)
- Use **cluster autoscaler** with conservative min counts
- Use **spot node pools** for non-critical workloads (up to 90% cheaper)
- A 3-node dev cluster with B2s nodes: ~$90/month

### ✔️ Verification Checklist
- [ ] AKS cluster running with system + user node pools
- [ ] All microservice pods running in correct namespaces
- [ ] Ingress routes traffic correctly to each service
- [ ] Network Policies restrict unauthorized pod communication
- [ ] Persistent Volumes survive pod restarts
- [ ] Container Insights shows metrics and logs
- [ ] Cluster autoscaler scales nodes under load

### 🔍 Behind the Scenes
- **AKS control plane** (API server, etcd, scheduler, controller-manager) runs on Microsoft-managed VMs — you never see or manage them. Microsoft handles upgrades, HA, and scaling.
- **Node pools** are VM Scale Sets (VMSS) managed by AKS. Each node runs kubelet, kube-proxy, and the container runtime (containerd).
- **Azure CNI** injects a virtual NIC for each pod into the Azure VNet. The Azure IPAM allocates IPs from the subnet. This is why pods get real VNet IPs and are directly routable.
- **CoreDNS** handles all DNS within the cluster. Service names resolve to ClusterIP addresses. If CoreDNS pods are unhealthy, ALL service discovery breaks.

---

## Scenario 13: AKS Advanced - Production-Grade

### 🎯 Objective
Harden AKS for production: Azure AD integration, workload identity, auto-scaling, policy enforcement, private clusters, service mesh, GitOps, and zero-downtime deployments.

### 📦 App Description
**Same e-commerce platform from Scenario 12**, now production-hardened with zero-downtime deployments, auto-scaling, security policies, and full observability.

### ✅ Hands-on Tasks

#### Part A: Azure AD & RBAC
- [ ] Enable Azure AD integration on AKS
- [ ] Configure Kubernetes RBAC using Azure AD groups
- [ ] Create ClusterRole + ClusterRoleBinding for admin group
- [ ] Create Role + RoleBinding for dev group (namespace-scoped)
- [ ] Test: a dev user can deploy to `dev` namespace but NOT `production`

#### Part B: Workload Identity
- [ ] Enable Workload Identity on the AKS cluster
- [ ] Create a User-Assigned Managed Identity
- [ ] Federate the MI with a Kubernetes service account
- [ ] Configure a pod to use the service account to access Key Vault — no secrets in cluster!

```bash
# Enable workload identity
az aks update --resource-group myrg --name myaks --enable-oidc-issuer --enable-workload-identity

# Create federated credential
az identity federated-credential create \
  --name fed-cred-ecom \
  --identity-name mi-ecom-prod \
  --resource-group myrg \
  --issuer <aks-oidc-issuer-url> \
  --subject system:serviceaccount:ecommerce:product-catalog-sa
```

> ⚠️ **DevOps Gotcha:** Workload Identity replaces the deprecated AAD Pod Identity. If you're following old tutorials that mention `aadpodidbinding` labels, those are DEPRECATED. Use Workload Identity with federated credentials — it's simpler and more secure.

#### Part C: Auto-Scaling (HPA, VPA, KEDA)
- [ ] Configure Horizontal Pod Autoscaler (HPA) based on CPU/memory
- [ ] Install KEDA for event-driven scaling (scale based on Service Bus queue depth)
- [ ] Understand Vertical Pod Autoscaler (VPA) — auto-adjusts resource requests
- [ ] Test: generate load and watch pods + nodes scale out

#### Part D: Private AKS Cluster
- [ ] Create a private AKS cluster (API server has NO public IP)
- [ ] Access the API server via VNet (Bastion → Jump Box → kubectl)
- [ ] Configure Private DNS Zone for the private API server
- [ ] Understand the trade-offs: more secure but more complex CI/CD (agents need VNet access)

> ⚠️ **DevOps Gotcha:** Private AKS clusters break standard CI/CD pipelines. Your GitHub Actions runners or Azure DevOps agents can't reach the private API server. Solutions: (1) Self-hosted agents in the VNet, (2) Azure DevOps with VNet-connected agent pools, (3) AKS command invoke (`az aks command invoke`). Plan this BEFORE making your cluster private.

#### Part E: Blue-Green & Canary Deployments
- [ ] Implement Blue-Green using two Deployments + Service label switching
- [ ] Implement Canary using NGINX Ingress annotations (traffic splitting)
- [ ] Implement progressive delivery with Flagger or Argo Rollouts
- [ ] Test: deploy a buggy version to canary, verify it doesn't affect production traffic

#### Part F: GitOps with Flux v2
- [ ] Install Flux v2 on the AKS cluster
- [ ] Connect Flux to a Git repository containing Kubernetes manifests
- [ ] Push a change to Git → watch Flux automatically apply it to the cluster
- [ ] Configure multi-environment GitOps (dev branch → dev cluster, main → prod)

#### Part G: Azure Policy for AKS
- [ ] Enable Azure Policy add-on for AKS
- [ ] Assign built-in policies:
  - No privileged containers
  - No containers as root
  - Enforce resource limits on every container
  - Only pull images from approved registries
- [ ] Test: try deploying a privileged container — watch it get rejected

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Workload Identity token errors | Federated credential subject mismatch | Verify service account name matches exactly |
| HPA not scaling | Metrics server not running or metrics not available | Check `kubectl top pods`; verify metrics-server pod |
| Private cluster kubectl timeout | Can't reach private API server | Use Bastion + jump box, or `az aks command invoke` |
| Flux sync stuck | Git auth failure or YAML syntax error | Check Flux logs; validate manifests with `kubectl apply --dry-run` |
| Policy blocking legitimate deployments | Policy too restrictive | Create policy exemption or adjust policy parameters |

### 💰 Cost Tips
- Production AKS is expensive — 3 D4s_v3 nodes: ~$420/month
- Use **spot node pools** for batch/dev workloads
- **AKS stop/start** for non-production clusters saves ~60%
- Right-size resource requests based on actual usage (VPA helps)

---

## Scenario 14: Azure SQL & Cosmos DB

### 🎯 Objective
Master relational and NoSQL databases on Azure. Understand purchasing models, scaling, replication, security, and the critical art of Cosmos DB partition key selection.

### 📦 App Description
**A social media application** with user profiles (Azure SQL — relational data), posts/feeds (Cosmos DB NoSQL — high-scale document data), and graph relationships (Cosmos DB Gremlin — friend connections). This forces you to use multiple database engines and understand their trade-offs.

### 🏗️ Architecture Diagram
```
┌──────────────────────────────────────────────────────────────┐
│                    DATA TIER                                   │
│                                                              │
│  ┌─────────────────────────┐  ┌──────────────────────────┐   │
│  │     AZURE SQL            │  │      COSMOS DB            │   │
│  │  "sql-social-prod"       │  │  "cosmos-social-prod"     │   │
│  │                          │  │                           │   │
│  │  Model: Serverless       │  │  API: NoSQL (core)        │   │
│  │  (auto-pause after 1hr)  │  │  Consistency: Session     │   │
│  │                          │  │  Partition: /userId       │   │
│  │  Tables:                 │  │                           │   │
│  │  • Users (profiles)      │  │  Containers:              │   │
│  │  • Settings              │  │  • posts (partition: /userId)│ │
│  │  • Subscriptions         │  │  • feeds (partition: /userId)│ │
│  │                          │  │  • likes (partition: /postId)│ │
│  │  Security:               │  │                           │   │
│  │  • TDE: Enabled          │  │  ┌─────────────────────┐  │   │
│  │  • Always Encrypted:     │  │  │ Gremlin API         │  │   │
│  │    SSN, email             │  │  │ Graph: friendships  │  │   │
│  │  • Dynamic Data Masking: │  │  │ Vertices: users     │  │   │
│  │    email, phone           │  │  │ Edges: follows      │  │   │
│  │  • Auditing: Enabled     │  │  └─────────────────────┘  │   │
│  │                          │  │                           │   │
│  │  Failover Group:         │  │  Multi-region:            │   │
│  │  Primary: eastus         │  │  Write: eastus            │   │
│  │  Secondary: westeurope   │  │  Read: westeurope, seasia │   │
│  │  Auto-failover: Enabled  │  │  Change Feed: Enabled     │   │
│  └─────────────────────────┘  └──────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Azure SQL
- [ ] Create Azure SQL Server + Database (Single Database)
- [ ] Compare **DTU** vs **vCore** purchasing models:
```
┌─────────────────────────────────────────────────────────┐
│ DTU vs vCORE                                            │
│                                                         │
│ DTU (Database Transaction Unit):                        │
│   • Bundled: CPU + Memory + IO in one metric            │
│   • Simple pricing: S0 = 10 DTU, S1 = 20 DTU, etc.    │
│   • Good for: predictable workloads, simplicity         │
│   • Can't independently scale CPU vs memory             │
│                                                         │
│ vCore:                                                  │
│   • Choose CPU cores and memory independently           │
│   • Azure Hybrid Benefit eligible (save 55%)            │
│   • Serverless tier (auto-scale + auto-pause)           │
│   • Good for: flexible scaling, cost optimization       │
└─────────────────────────────────────────────────────────┘
```
- [ ] Try Serverless tier: configure auto-pause (pauses after 1 hour idle — no charges!)
- [ ] Create an Elastic Pool for multiple databases sharing resources
- [ ] Set up geo-replication and failover groups with automatic failover
- [ ] Enable auditing and Advanced Threat Detection
- [ ] Configure TDE (transparent, on by default), Always Encrypted, Dynamic Data Masking
- [ ] Set up Private Endpoint for SQL

> ⚠️ **DevOps Gotcha:** Serverless auto-pause is great for saving money, but the FIRST connection after auto-pause has a cold start of **~1 minute**. Your app will get a connection timeout if the default timeout is too short. Set `Connection Timeout=120` in your connection string. Also, auto-pause is triggered by zero activity — even a single health check query prevents pausing, negating the cost savings.

#### Part B: Cosmos DB
- [ ] Create a Cosmos DB account with NoSQL API
- [ ] Create a database and containers with appropriate partition keys
- [ ] **THE CRITICAL SKILL — Partition Key Selection:**

```
┌─────────────────────────────────────────────────────────┐
│ PARTITION KEY SELECTION - THE #1 COSMOS DB SKILL        │
│                                                         │
│ GOOD partition key has:                                  │
│   ✅ High cardinality (many distinct values)            │
│   ✅ Evenly distributed data                            │
│   ✅ Used in most queries as a filter                   │
│                                                         │
│ BAD partition key causes:                                │
│   ❌ Hot partitions (one partition gets all traffic)     │
│   ❌ Cross-partition queries (slow and expensive)        │
│   ❌ 429 throttling on hot partitions                    │
│                                                         │
│ Examples:                                                │
│   Posts container → /userId (each user's posts together)│
│   Orders container → /customerId                        │
│   IoT data → /deviceId                                  │
│   DON'T use: /date, /status, /country (low cardinality)│
└─────────────────────────────────────────────────────────┘
```

- [ ] Understand consistency levels (from strongest to weakest):
  1. **Strong**: read latest write globally — highest latency
  2. **Bounded Staleness**: reads lag by K versions or T time
  3. **Session**: strong within a session, eventual for others (DEFAULT — best for most apps)
  4. **Consistent Prefix**: reads never see out-of-order writes
  5. **Eventual**: no ordering guarantee — lowest latency
- [ ] Estimate RU (Request Unit) consumption for your queries
- [ ] Configure auto-scale (100–4000 RU/s range)
- [ ] Enable Change Feed and process changes with Azure Functions
- [ ] Set up multi-region reads (add West Europe and Southeast Asia)

> ⚠️ **DevOps Gotcha:** Cosmos DB `429 Too Many Requests` is the #1 production issue. It means you've exceeded the provisioned RU/s for a partition. The fix isn't always "add more RU/s" — it might be a **hot partition** problem. If one partition key value (e.g., one userId) gets 80% of traffic, only that partition throttles. Use partition key statistics in the portal to identify hot partitions. The fix is often redesigning the partition key.

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| SQL DTU at 100% | Database under-provisioned | Scale up DTU tier or switch to vCore |
| SQL failover group slow DNS switch | DNS TTL propagation | Use `<server-name>.database.windows.net` (auto-switches) not specific server name |
| Cosmos DB 429 throttling | Exceeded RU/s or hot partition | Enable auto-scale; check partition distribution |
| Cross-partition query slow | Query doesn't filter on partition key | Redesign query or add partition key filter |
| Connection pool exhaustion | Too many connections, not reusing clients | Use singleton CosmosClient; pool SQL connections |
| Always Encrypted breaks queries | Can't query on encrypted columns | Only equality queries on deterministic encryption; no range queries |

### 💰 Cost Tips
- SQL Serverless: auto-pause saves ~60-80% for dev/test databases
- SQL DTU Basic (5 DTU): ~$5/month — cheapest option for learning
- Cosmos DB Serverless: pay per request, no minimum — great for learning
- Cosmos DB Free Tier: 1000 RU/s + 25GB FREE forever (one per account)
- Use provisioned auto-scale instead of manual RU — prevents over-provisioning
- Delete databases you're not actively using

---

## Scenario 15: Messaging & Event-Driven Architecture

### 🎯 Objective
Build event-driven systems using Azure messaging services. Understand when to use queues vs topics, when to use Service Bus vs Event Hubs vs Event Grid, and how to handle poison messages, dead letters, and exactly-once processing.

### 📦 App Description
**An order processing system** — orders come in via API, get queued in Service Bus, processed asynchronously by worker services, emit events via Event Grid for inventory, notification, and analytics services. High-volume telemetry goes to Event Hubs.

### 🏗️ Architecture Diagram
```
                    ┌─────────────┐
                    │  Order API  │
                    └──────┬──────┘
                           │ Send message
                    ┌──────▼──────┐
                    │ SERVICE BUS │
                    │   Queue:    │
                    │ "orders"    │
                    │             │
                    │ Dead-letter │
                    │ queue (DLQ) │
                    └──────┬──────┘
                           │ Receive & Process
                    ┌──────▼──────┐
                    │   Order     │
                    │  Processor  │
                    └──────┬──────┘
                           │ Publish event
                    ┌──────▼──────┐
                    │ EVENT GRID  │
                    │ Topic:      │
                    │ "order-     │
                    │  events"    │
                    └──┬────┬──┬──┘
                       │    │  │ Subscribe
           ┌───────────┘    │  └───────────┐
           ▼                ▼              ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Inventory  │  │ Notification│ │ Analytics  │
    │ Service    │  │ Service    │  │ Service    │
    │(Func/Logic)│  │(Logic App) │  │(Event Hubs)│
    └────────────┘  └────────────┘  └────────────┘

┌───────────────────────────────────────────────────────────┐
│ WHEN TO USE WHAT:                                          │
│                                                           │
│ Service Bus Queue:                                        │
│   Point-to-point, guaranteed delivery, ordering           │
│   Use for: Commands, work items, transactions             │
│                                                           │
│ Service Bus Topic/Subscription:                           │
│   Pub-sub with filtering, multiple subscribers            │
│   Use for: Events with filtered subscribers               │
│                                                           │
│ Event Grid:                                               │
│   Reactive events, push model, serverless-friendly        │
│   Use for: Resource events, webhooks, lightweight events  │
│                                                           │
│ Event Hubs:                                               │
│   High-throughput streaming, millions/sec                  │
│   Use for: Telemetry, logs, IoT data, analytics           │
│                                                           │
│ Queue Storage:                                            │
│   Simple queues, large backlog, cheap                     │
│   Use for: Simple async tasks, massive queues (>80GB)     │
└───────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Service Bus
- [ ] Create a Service Bus namespace (Standard or Premium)
- [ ] Create a Queue with dead-letter queue enabled
- [ ] Send and receive messages using the SDK
- [ ] Configure duplicate detection and message sessions
- [ ] Implement dead-letter queue processing (handle poison messages)
- [ ] Create a Topic with two Subscriptions using SQL filters
- [ ] Configure scheduled messages (deliver at a future time)

> ⚠️ **DevOps Gotcha:** Service Bus has a **lock duration** (default 30 seconds). If your consumer takes longer than 30 seconds to process a message, the lock expires and the message becomes visible to other consumers — resulting in duplicate processing. Either: increase lock duration (max 5 min), renew the lock periodically, or process messages faster.

#### Part B: Event Hubs
- [ ] Create Event Hub namespace with multiple Event Hubs
- [ ] Send events at high throughput using partitions
- [ ] Consume events with consumer groups and checkpointing
- [ ] Enable Event Hubs Capture (auto-save to Storage/Data Lake)
- [ ] Use Kafka protocol compatibility to test with Kafka clients

#### Part C: Event Grid
- [ ] Create a custom Event Grid topic
- [ ] Create subscriptions with webhook, Service Bus, and Azure Function destinations
- [ ] Configure subject and event type filters
- [ ] Set up dead-letter destination for failed deliveries
- [ ] Subscribe to Azure system events (e.g., blob created, resource group modified)

#### Part D: Patterns
- [ ] Implement competing consumers (multiple workers processing one queue)
- [ ] Implement pub-sub (order event → inventory + notification + analytics)
- [ ] Handle idempotency (processing the same message twice should have no side effects)
- [ ] Implement retry with exponential backoff for transient failures

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Messages going to dead-letter queue | Max delivery count exceeded (default 10) | Fix consumer errors; process DLQ separately |
| Duplicate message processing | Lock expired, message redelivered | Increase lock duration; implement idempotency |
| Event Grid delivery failures | Subscriber endpoint returning non-2xx | Fix endpoint; check dead-letter for failed events |
| Event Hub consumer lag | Consumer too slow for the event rate | Scale out consumers; increase throughput units |
| Message ordering violated | Multiple partitions/sessions | Use message sessions for ordered processing |
| Queue depth growing unbounded | Consumer offline or too slow | Scale consumers; set TTL on messages |

### 💰 Cost Tips
- Service Bus Basic: ~$0.05/million operations (no topics, no sessions)
- Service Bus Standard: ~$10/month + operations
- Event Hubs Basic: ~$11/month per throughput unit
- Event Grid: first 100K operations/month FREE, then $0.60/million
- Queue Storage: cheapest at $0.00036/10K operations

---

## Scenario 16: Azure Cache for Redis & CDN

### 🎯 Objective
Implement caching strategies to dramatically improve application performance. Understand Redis patterns (cache-aside, session store, pub-sub, distributed locks) and CDN for static content delivery.

### 📦 App Description
**A high-traffic news/blog platform** that needs caching for articles (frequently read, rarely updated), user sessions (must persist across requests), and static assets (CSS, JS, images). Test performance with and without cache to see the impact.

### ✅ Hands-on Tasks

#### Part A: Redis Cache
- [ ] Create Azure Cache for Redis (Standard C1 tier for learning)
- [ ] Implement **cache-aside pattern**: check cache → if miss, query DB → store in cache
- [ ] Implement **session store**: store user sessions in Redis (stateless web tier)
- [ ] Implement **distributed lock**: prevent concurrent updates with `SETNX`
- [ ] Configure TTL (time-to-live) for cached items
- [ ] Understand eviction policies: `volatile-lru`, `allkeys-lru`, `noeviction`
- [ ] Monitor cache hit ratio, memory usage, connected clients

```
┌───────────────────────────────────────────────────────────┐
│ CACHE-ASIDE PATTERN                                        │
│                                                           │
│  1. App checks Redis for data                             │
│     ├── HIT: Return cached data (fast! <1ms)             │
│     └── MISS: Continue to step 2                          │
│                                                           │
│  2. App queries database (slow: 50-200ms)                 │
│                                                           │
│  3. App writes result to Redis with TTL                   │
│                                                           │
│  4. App returns data to user                              │
│                                                           │
│  Cache Invalidation:                                      │
│    • On data update: delete cache key (lazy invalidation) │
│    • TTL expiry: automatic (simpler but slightly stale)   │
│    • Cache stampede risk: many concurrent cache misses    │
│      → use lock or probabilistic early refresh            │
└───────────────────────────────────────────────────────────┘
```

> ⚠️ **DevOps Gotcha:** The #1 Redis production issue: **connection storms**. If your app creates a new Redis connection per request instead of using a connection pool/singleton, you'll exhaust the connection limit fast (Standard C1 = 256 connections). In .NET, use a singleton `ConnectionMultiplexer`. In Node.js, reuse the client. Check `connected_clients` metric — if it's growing, you have a connection leak.

#### Part B: Azure CDN
- [ ] Create an Azure CDN profile (Microsoft Standard tier)
- [ ] Create an endpoint pointing to your Storage Account static website
- [ ] Configure caching rules (override cache headers for specific paths)
- [ ] Configure custom domain with HTTPS
- [ ] Purge cached content after updates
- [ ] Preload popular content to CDN edge nodes
- [ ] Configure compression for text-based content

> ⚠️ **DevOps Gotcha:** CDN cache invalidation is NOT instant. Purge operations can take 2-10 minutes to propagate across all edge nodes globally. If you deploy a new version of your app and purge immediately, users might still see cached old content. Use **versioned file names** (e.g., `app.v2.js`) instead of relying on purge for cache busting.

### 💰 Cost Tips
- Redis Basic C0 (250MB): ~$16/month — cheapest for learning
- Redis Standard C1 (1GB): ~$80/month — minimum for production patterns
- CDN Standard: ~$0.081/GB for first 10TB (very cheap)
- DELETE Redis when not actively testing — it charges 24/7

---

## 🎯 What's Next?

After completing Batch 3, you should have solid skills in:
- ✅ Container image lifecycle (build, push, scan, deploy)
- ✅ Kubernetes orchestration (AKS fundamentals + production hardening)
- ✅ Relational and NoSQL database design and management
- ✅ Event-driven architecture with Azure messaging services
- ✅ Caching strategies for high-performance applications

**Proceed to → Batch 4: Serverless, CI/CD & Infrastructure as Code** where you'll tackle Azure Functions, Logic Apps, Azure DevOps, GitHub Actions, Bicep, and Terraform.
