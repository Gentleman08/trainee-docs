# 🔷 Batch 4: Serverless, CI/CD & Infrastructure as Code

> **Level:** Intermediate–Advanced | **Estimated Total Time:** 15–20 days | **Scenarios:** 6 (numbered 17–22)
>
> This batch covers automation from every angle — serverless compute, workflow orchestration, CI/CD pipelines, and infrastructure as code. These are the skills that separate engineers who "use Azure" from those who "own Azure."

---

## 📑 Table of Contents

- [Scenario 17: Azure Functions Deep Dive](#scenario-17-azure-functions-deep-dive)
- [Scenario 18: Logic Apps & Integration Services](#scenario-18-azure-logic-apps--integration-services)
- [Scenario 19: Azure DevOps CI/CD](#scenario-19-azure-devops---cicd-pipelines)
- [Scenario 20: GitHub Actions for Azure](#scenario-20-github-actions-for-azure)
- [Scenario 21: Bicep IaC](#scenario-21-infrastructure-as-code---bicep)
- [Scenario 22: Terraform on Azure](#scenario-22-infrastructure-as-code---terraform-on-azure)

---

## Scenario 17: Azure Functions Deep Dive

### 🎯 Objective
Master serverless compute: triggers, bindings, Durable Functions patterns, cold starts, VNet integration, and monitoring. Understand when Functions are the right choice and when they're not.

### 📦 App Description
**An image processing pipeline**: upload images via HTTP trigger, process them (resize, watermark, thumbnail generation) with Blob triggers, store metadata in Cosmos DB via output bindings, and notify users via Queue trigger. Uses Durable Functions for multi-step orchestration.

### 🏗️ Architecture Diagram
```
  User uploads image
         │
  ┌──────▼──────┐                         ┌──────────────┐
  │ HTTP Trigger │────► Blob Storage ─────►│ Blob Trigger  │
  │ (upload API) │      "raw-images"       │ (processor)   │
  └──────────────┘                         └──────┬───────┘
                                                  │
                                           ┌──────▼───────┐
                                           │ Durable      │
                                           │ Orchestrator │
                                           │              │
                                           │ 1. Resize    │
                                           │ 2. Watermark │
                                           │ 3. Thumbnail │
                                           │ 4. Metadata  │
                                           └──┬───┬───┬───┘
                                              │   │   │
                              ┌───────────────┘   │   └───────────┐
                              ▼                   ▼               ▼
                       ┌────────────┐     ┌────────────┐  ┌────────────┐
                       │ Blob Store │     │ Cosmos DB  │  │ Queue      │
                       │ "processed"│     │ (metadata) │  │ "notify"   │
                       └────────────┘     └────────────┘  └─────┬──────┘
                                                                │
                                                          ┌─────▼──────┐
                                                          │Queue Trigger│
                                                          │(send email) │
                                                          └────────────┘

┌───────────────────────────────────────────────────────────┐
│ HOSTING PLANS:                                             │
│                                                           │
│ Consumption:    Pay per execution, auto-scale 0 → 200     │
│                 Cold start: 1-10 sec | Timeout: 5 min     │
│                 Best for: sporadic, unpredictable load     │
│                                                           │
│ Premium (EP1):  Always warm, VNet integration, larger     │
│                 Cold start: NONE | Timeout: unlimited      │
│                 Best for: latency-sensitive, VNet access   │
│                                                           │
│ Dedicated:      Runs on App Service Plan                  │
│                 Cold start: depends on Always On           │
│                 Best for: existing ASP, predictable load   │
└───────────────────────────────────────────────────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Core Triggers & Bindings
- [ ] Create an HTTP-triggered function (REST API endpoint)
- [ ] Create a Timer-triggered function (run every 5 minutes: `0 */5 * * * *`)
- [ ] Create a Blob-triggered function (fires when new blob uploaded)
- [ ] Create a Queue-triggered function (processes Service Bus/Queue messages)
- [ ] Use input bindings to read from Cosmos DB
- [ ] Use output bindings to write to Cosmos DB, Queue, and Blob Storage
- [ ] Configure local development with `func init` and `func start`

> ⚠️ **DevOps Gotcha:** Blob triggers use Storage Queue notifications internally, which means there can be up to a **10-minute delay** in trigger activation. If you need near-instant blob processing, use **Event Grid trigger** with a Storage blob created event instead — it fires within seconds.

#### Part B: Durable Functions
- [ ] Implement Function Chaining: Step1 → Step2 → Step3 in sequence
- [ ] Implement Fan-Out/Fan-In: process multiple images in parallel, then aggregate results
- [ ] Implement Human Interaction pattern: send approval email, wait for response, continue or reject
- [ ] Implement Eternal Orchestration: a monitoring loop that checks status every minute
- [ ] Understand the orchestrator replay model and deterministic constraints

> ⚠️ **DevOps Gotcha:** Durable Functions orchestrators must be **deterministic** — no `DateTime.Now`, no `Guid.NewGuid()`, no HTTP calls directly in the orchestrator. Use `context.CurrentUtcDateTime` and activity functions for non-deterministic work. Violating this causes replay bugs that are extremely hard to diagnose.

#### Part C: Cold Start & Performance
- [ ] Measure cold start time on Consumption plan (deploy and time first request)
- [ ] Mitigate cold start: use Premium plan with always-warm instances
- [ ] Implement singleton `HttpClient` (don't create a new one per invocation)
- [ ] Configure function timeout per plan (5 min consumption, unlimited premium)
- [ ] Use Application Insights to monitor execution time, failures, and invocation count

#### Part D: VNet Integration & Security
- [ ] Deploy function on Premium plan with VNet integration
- [ ] Access a Private Endpoint SQL database from the function
- [ ] Enable Managed Identity for accessing Key Vault and Storage
- [ ] Configure access restrictions (only allow Front Door or specific IPs)
- [ ] Set up deployment slots for zero-downtime deployments

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Cold start taking 10+ seconds | Large package, many dependencies | Reduce package size; use Premium plan |
| Function timeout (5 min on Consumption) | Processing takes too long | Use Durable Functions or switch to Premium plan |
| Connection exhaustion (`SocketException`) | Creating new `HttpClient` per call | Use static/singleton `HttpClient` |
| Blob trigger delay (10 min) | Storage polling mechanism | Use Event Grid trigger instead |
| Durable orchestration stuck | Non-deterministic code in orchestrator | Follow deterministic coding constraints |
| Poison queue messages | Message processing always fails | Configure max dequeue count; handle DLQ |
| Inconsistent local vs Azure behavior | Local settings vs Azure configuration | Use `local.settings.json` mirroring Azure App Settings |

### 💰 Cost Tips
- **Consumption Plan**: first 1 million executions/month FREE, then $0.20/million — incredibly cheap for sporadic workloads
- **Premium EP1**: ~$150/month minimum (one always-warm instance)
- Consumption is cheapest for <1M executions; Premium is cheaper for high-volume continuous workloads
- Durable Functions store state in Azure Storage — monitor storage costs for long-running orchestrations
- DELETE function apps when done — Consumption still charges for storage, Premium charges compute

---

## Scenario 18: Azure Logic Apps & Integration Services

### 🎯 Objective
Build no-code/low-code workflows for business process automation. Integrate with 400+ connectors. Understand API Management for securing and governing APIs.

### 📦 App Description
**A business process automation app — invoice processing workflow**: receives invoice emails, extracts data using AI (Form Recognizer), validates against database, routes for approval, stores in blob storage, and sends notification. Uses API Management to expose APIs securely.

### ✅ Hands-on Tasks

#### Part A: Logic Apps
- [ ] Create a Logic App (Consumption plan — pay per trigger)
- [ ] Build a workflow: When email arrives → Check attachment → Extract data → Store in DB → Send notification
- [ ] Configure retry policies and error handling with `runAfter` conditions
- [ ] Implement parallel branches and conditional logic
- [ ] Configure concurrency control (limit to 10 concurrent runs)
- [ ] Use Standard Logic Apps (stateful + stateless workflows on App Service)
- [ ] Compare Consumption vs Standard:

```
┌───────────────────────────────────────────────────────────┐
│ LOGIC APPS CONSUMPTION vs STANDARD                         │
│                                                           │
│ Consumption:                                              │
│   • Multi-tenant, pay per trigger/action                  │
│   • ~$0.000125 per action execution                       │
│   • Auto-scales, no infrastructure management             │
│   • Limited connectors (no VNet integration)              │
│                                                           │
│ Standard:                                                 │
│   • Single-tenant, runs on App Service plan               │
│   • VNet integration, Private Endpoints                   │
│   • Multiple workflows in one Logic App                   │
│   • Stateful + Stateless workflows                        │
│   • More expensive base cost but VNet access              │
└───────────────────────────────────────────────────────────┘
```

> ⚠️ **DevOps Gotcha:** Logic Apps have a **90-day run history retention** and an **action limit of 100,000 per run**. Long-running workflows that loop thousands of times can hit these limits. For high-volume processing, use Azure Functions instead. Logic Apps are best for orchestration and integration, not data crunching.

#### Part B: API Management (APIM)
- [ ] Create an APIM instance (Consumption tier for learning — cheaper)
- [ ] Import an API from OpenAPI specification
- [ ] Configure Products and Subscriptions (API keys)
- [ ] Apply policies:
  - **Rate limiting**: max 100 calls per minute per subscription
  - **Caching**: cache GET responses for 5 minutes
  - **JWT validation**: validate Azure AD tokens
  - **Transformation**: add/remove headers, modify response body
  - **CORS**: enable cross-origin requests
- [ ] Configure API versioning (URL path, header, query string)
- [ ] Customize the Developer Portal

```xml
<!-- Example APIM policy -->
<policies>
  <inbound>
    <rate-limit calls="100" renewal-period="60" />
    <validate-jwt header-name="Authorization" require-scheme="Bearer">
      <openid-config url="https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration" />
      <required-claims>
        <claim name="aud" match="all">
          <value>{your-api-app-id}</value>
        </claim>
      </required-claims>
    </validate-jwt>
    <cache-lookup vary-by-header="Accept" />
  </inbound>
  <outbound>
    <cache-store duration="300" />
  </outbound>
</policies>
```

> ⚠️ **DevOps Gotcha:** APIM policy evaluation order matters! Policies are processed: inbound → backend → outbound → on-error. Within each section, policies execute top-to-bottom. If you put `rate-limit` AFTER `validate-jwt`, unauthenticated requests still count against the rate limit. Put security policies (JWT validation) FIRST, then rate limiting.

### 💰 Cost Tips
- APIM Consumption: ~$3.50 per million calls (cheapest, but cold start per call)
- APIM Developer: ~$49/month (no SLA, good for learning)
- APIM Basic: ~$150/month (production-minimum)
- Logic Apps Consumption: ~$0.000125 per action (very cheap for low-volume)
- DELETE APIM instances when done — they charge 24/7

---

## Scenario 19: Azure DevOps - CI/CD Pipelines

### 🎯 Objective
Build end-to-end CI/CD pipelines: from code commit to production deployment with quality gates, approvals, and automated testing.

### 📦 App Description
**The e-commerce app from earlier batches** — now set up a complete CI/CD pipeline: commit → build → test → publish artifact → deploy to dev → approval gate → deploy to staging → smoke test → deploy to production.

### 🏗️ Architecture Diagram
```
  Developer
      │
      │ git push
      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  BUILD STAGE  │────►│  DEV STAGE   │────►│ STAGING STAGE│
│              │     │              │     │              │
│ • Restore    │     │ • Deploy     │     │ • Approval   │
│ • Build      │     │   to App Svc │     │   Gate       │
│ • Unit Tests │     │ • Smoke Test │     │ • Deploy     │
│ • Code Scan  │     │              │     │ • Integration│
│ • Publish    │     │ Environment: │     │   Tests      │
│   Artifact   │     │   "dev"      │     │              │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  │ Manual
                                                  │ Approval
                                                  ▼
                                           ┌──────────────┐
                                           │  PROD STAGE  │
                                           │              │
                                           │ • Blue-Green │
                                           │   Swap Slot  │
                                           │ • Health     │
                                           │   Check      │
                                           │ • Rollback   │
                                           │   if fails   │
                                           │              │
                                           │ Environment: │
                                           │   "production"│
                                           └──────────────┘
```

### ✅ Hands-on Tasks

#### Part A: Organization & Repos
- [ ] Create Azure DevOps organization and project
- [ ] Set up Azure Repos with Git
- [ ] Configure branch policies: required reviewers, build validation, linked work items
- [ ] Implement branching strategy (trunk-based or GitFlow)
- [ ] Set up pull request templates

#### Part B: YAML Pipelines
- [ ] Create a multi-stage YAML pipeline:
```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: 'app-settings-dev'

stages:
  - stage: Build
    jobs:
      - job: BuildAndTest
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: '20.x'
          - script: npm ci
          - script: npm run test -- --coverage
          - script: npm run build
          - publish: $(System.DefaultWorkingDirectory)/dist
            artifact: webapp

  - stage: DeployDev
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: DeployToDev
        environment: 'dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'azure-service-connection'
                    appName: 'app-ecommerce-dev-eastus'
                    package: '$(Pipeline.Workspace)/webapp'

  - stage: DeployProd
    dependsOn: DeployDev
    condition: succeeded()
    jobs:
      - deployment: DeployToProd
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: 'azure-service-connection'
                    appName: 'app-ecommerce-prod-eastus'
                    deployToSlotOrASE: true
                    slotName: 'staging'
                - task: AzureAppServiceManage@0
                  inputs:
                    azureSubscription: 'azure-service-connection'
                    Action: 'Swap Slots'
                    WebAppName: 'app-ecommerce-prod-eastus'
                    SourceSlot: 'staging'
```

- [ ] Configure variable groups linked to Key Vault
- [ ] Create reusable pipeline templates
- [ ] Set up pipeline caching for `node_modules`
- [ ] Configure deployment environments with approval gates

> ⚠️ **DevOps Gotcha:** YAML pipeline indentation is CRITICAL. A single wrong space can cause cryptic errors. Use the YAML pipeline editor's validation feature before committing. Also, secret variables are NOT available to forked pull request builds by default — this prevents PR authors from extracting secrets, but it means PR validation builds can't deploy.

#### Part C: Service Connections & Security
- [ ] Create an Azure Resource Manager service connection
- [ ] Use Workload Identity Federation (OIDC) instead of client secrets — more secure
- [ ] Restrict service connections to specific pipelines
- [ ] Configure environment approvals and gates (business hours only, approval timeout)

#### Part D: Azure Artifacts
- [ ] Create a feed for npm packages
- [ ] Publish a shared library as an npm package
- [ ] Configure upstream sources (proxy for npmjs.org)
- [ ] Use the feed in pipeline builds

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Pipeline YAML syntax error | Indentation or structure issue | Use pipeline editor validation; lint locally |
| Service connection permission denied | Connection not authorized for pipeline | Authorize via pipeline settings or pool admin |
| Agent pool at capacity | All agents busy, parallel job limit | Use Microsoft-hosted agents (auto-scale); increase parallel jobs |
| Secret not masked in logs | Secret used in output or complex expression | Use `issecret=true`; avoid echoing secrets |
| Template not found | Wrong path or repo reference | Use `template: path/to/template.yml@repo` with repo resource |
| Approval timeout | No one approved in time | Configure auto-approval after timeout; use Teams notifications |

### 💰 Cost Tips
- Azure DevOps: first 5 users FREE (Basic plan)
- Microsoft-hosted agents: 1 free parallel job (1800 min/month)
- Extra parallel jobs: ~$40/month each
- Self-hosted agents: FREE unlimited parallel jobs (you pay for the VM)
- Azure Artifacts: first 2GB FREE, then ~$2/GB/month

---

## Scenario 20: GitHub Actions for Azure

### 🎯 Objective
Build CI/CD workflows with GitHub Actions, using Azure best practices: OIDC authentication (no secrets), reusable workflows, and environment protection rules.

### 📦 App Description
**A Python/Node.js web application** with unit tests, integration tests, and deployment to three environments (dev, staging, production) using GitHub Actions.

### ✅ Hands-on Tasks

#### Part A: Workflow Setup
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure Azure Login using OIDC (Federated Credentials — no secrets stored in GitHub!)
- [ ] Deploy to App Service, AKS, and/or Azure Functions
- [ ] Set up GitHub Environments with protection rules (required reviewers, wait timer)

```yaml
name: Deploy to Azure
on:
  push:
    branches: [main]

permissions:
  id-token: write  # Required for OIDC
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: webapp
          path: dist/

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/download-artifact@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: 'app-ecommerce-staging'
          package: webapp/
```

> ⚠️ **DevOps Gotcha:** OIDC authentication (federated credentials) is MORE SECURE than client secrets because there's no secret to leak. But the setup is specific: you must create a federated credential in the Azure AD app registration that matches the GitHub repo, branch, and environment. If ANY of these don't match exactly, login fails with a cryptic "AADSTS700024" error.

#### Part B: Advanced Patterns
- [ ] Create reusable workflows (DRY principle)
- [ ] Configure matrix builds (test on Node 18, 20, 22 in parallel)
- [ ] Set up concurrency groups to prevent simultaneous deployments
- [ ] Implement rollback on failed deployment

#### Part C: Security
- [ ] Enable GitHub Advanced Security: CodeQL analysis, Dependabot, secret scanning
- [ ] Pin action versions to commit SHA (not tags — tags can be reassigned)
- [ ] Review GITHUB_TOKEN permissions (principle of least privilege)

### 💰 Cost Tips
- GitHub Actions: 2000 minutes/month FREE for public repos
- Private repos: 2000 minutes/month on Free plan
- Linux runners: 1x rate, macOS: 10x rate, Windows: 2x rate
- Self-hosted runners on Azure VMs: pay only for the VM

---

## Scenario 21: Infrastructure as Code - Bicep

### 🎯 Objective
Define Azure infrastructure declaratively using Bicep. Master modules, parameters, conditions, loops, and deployment scopes. Understand what-if deployments and deployment stacks.

### 📦 App Description
**Complete infrastructure for a production web app**: VNet, App Service, SQL Database, Key Vault, Storage Account, Redis Cache — all defined in Bicep modules, parameterized for dev/staging/prod environments.

### ✅ Hands-on Tasks

#### Part A: Bicep Fundamentals
- [ ] Install Bicep CLI and VS Code extension
- [ ] Create your first Bicep file (resource group, storage account)
- [ ] Use parameters, variables, and outputs
- [ ] Deploy: `az deployment group create --template-file main.bicep`
- [ ] Use what-if: `az deployment group what-if --template-file main.bicep`

```bicep
// main.bicep
param location string = resourceGroup().location
param environment string = 'dev'

var nameSuffix = '${environment}-eastus'

module vnet 'modules/vnet.bicep' = {
  name: 'vnet-deployment'
  params: {
    name: 'vnet-${nameSuffix}'
    location: location
    addressPrefix: '10.0.0.0/16'
  }
}

module appService 'modules/appservice.bicep' = {
  name: 'app-deployment'
  params: {
    name: 'app-ecom-${nameSuffix}'
    location: location
    subnetId: vnet.outputs.appSubnetId
  }
}

module sql 'modules/sql.bicep' = {
  name: 'sql-deployment'
  params: {
    name: 'sql-ecom-${nameSuffix}'
    location: location
    adminPassword: keyVault.getSecret('sql-admin-password')
  }
}
```

#### Part B: Modules & Composition
- [ ] Create reusable modules: VNet, App Service, SQL, Key Vault, Storage
- [ ] Use module outputs to wire resources together
- [ ] Implement conditional deployments (`if` on resources)
- [ ] Use loops (`for`) to create multiple resources from arrays
- [ ] Publish modules to a Bicep registry (ACR)

#### Part C: Environment Management
- [ ] Create parameter files for each environment: `dev.bicepparam`, `prod.bicepparam`
- [ ] Use deployment scopes: resource group, subscription, management group
- [ ] Implement deployment stacks for managed lifecycle
- [ ] Create template specs for versioned, shareable templates

> ⚠️ **DevOps Gotcha:** Bicep deployments are **incremental** by default — they ADD or UPDATE resources but DON'T DELETE removed resources. If you remove a resource from your Bicep file, it stays in Azure! Use `--mode Complete` for complete mode (deletes unmanaged resources) but be VERY careful — it will delete everything not in the template. Better: use Deployment Stacks which handle deletion safely.

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| Deployment stuck in "Failed" state | Previous deployment failed, blocking new ones | Cancel stuck deployment: `az deployment group cancel` |
| Circular dependency error | Resource A depends on B, B depends on A | Use `dependsOn` carefully; break cycles with intermediate resources |
| Resource name conflict | Name already exists globally (storage, web app) | Use unique naming: `uniqueString(resourceGroup().id)` |
| Parameter validation failed | Value doesn't match `@allowed` or `@minLength` | Check parameter constraints in the module |
| Module not found | Wrong path or registry reference | Verify relative path; check ACR login |

### 💰 Cost Tips
- Bicep itself is FREE — it compiles to ARM templates
- what-if deployments are FREE (no resources created)
- Deployment operations are tracked in the activity log (no extra cost)

---

## Scenario 22: Infrastructure as Code - Terraform on Azure

### 🎯 Objective
Define the same infrastructure as Scenario 21 using Terraform. Compare the experience with Bicep and understand trade-offs. Master state management, modules, and CI/CD integration.

### ✅ Hands-on Tasks

#### Part A: Terraform Fundamentals
- [ ] Configure AzureRM provider
- [ ] Set up remote state backend in Azure Storage with state locking
- [ ] Create resources: VNet, App Service, SQL, Key Vault
- [ ] Run `terraform plan`, `terraform apply`, `terraform destroy`

```hcl
# main.tf
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stterraformstate001"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}
```

#### Part B: State Management
- [ ] Set up Azure Storage backend with state locking (blob lease)
- [ ] Import existing resources into state: `terraform import`
- [ ] Handle state file conflicts with `terraform force-unlock`
- [ ] Use workspaces for multi-environment: `terraform workspace new staging`
- [ ] Understand state file sensitivity — it contains secrets in plaintext!

> ⚠️ **DevOps Gotcha:** Terraform state files contain ALL resource attributes, INCLUDING sensitive values like database passwords, storage keys, and connection strings — in PLAINTEXT. The state file is NOT encrypted by default. Store it in Azure Storage with encryption at rest and restrict access with RBAC. Never commit state files to Git!

#### Part C: Modules & Composition
- [ ] Create reusable modules with input variables and outputs
- [ ] Use the Terraform Registry for pre-built Azure modules
- [ ] Use `data` sources to reference existing resources
- [ ] Implement `count` and `for_each` for multiple resource instances

#### Part D: CI/CD Integration
- [ ] Integrate Terraform with Azure DevOps (plan in PR, apply on merge)
- [ ] Integrate with GitHub Actions
- [ ] Implement plan approval workflow
- [ ] Use Terragrunt for DRY Terraform across environments

```
┌───────────────────────────────────────────────────────────┐
│ BICEP vs TERRAFORM - WHEN TO USE WHICH                     │
│                                                           │
│ BICEP:                                                    │
│   ✅ Azure-native, first-party support                    │
│   ✅ No state file to manage                              │
│   ✅ Automatic dependency detection                       │
│   ✅ Full day-1 support for new Azure features            │
│   ❌ Azure-only (can't manage AWS/GCP)                    │
│   ❌ Limited ecosystem/community compared to Terraform    │
│                                                           │
│ TERRAFORM:                                                │
│   ✅ Multi-cloud (Azure + AWS + GCP + more)               │
│   ✅ Huge ecosystem, modules registry, community          │
│   ✅ State tracks actual vs desired (drift detection)     │
│   ✅ Mature tooling (Terragrunt, Spacelift, etc.)         │
│   ❌ State file management complexity                     │
│   ❌ New Azure features lag behind Bicep                   │
│   ❌ Provider version conflicts can break things           │
└───────────────────────────────────────────────────────────┘
```

### 🔧 Edge Cases

| Problem | Cause | Solution |
|---------|-------|----------|
| State file locked | Previous operation crashed without unlocking | `terraform force-unlock <lock-id>` |
| Provider version conflict | Breaking change in provider update | Pin provider version: `version = "~> 3.0"` |
| Resource recreation instead of update | Resource attribute forces replacement | Check plan output for `# forces replacement`; use `lifecycle { prevent_destroy = true }` |
| State drift | Someone changed resources outside Terraform | `terraform plan` shows drift; `terraform apply` reconciles |
| Import fails | Wrong resource ID format | Check Azure resource ID format in docs |

### 💰 Cost Tips
- Terraform CLI: FREE and open-source
- Terraform Cloud: free for up to 500 resources
- State storage in Azure: < $1/month
- CI/CD pipeline minutes: varies by platform

---

## 🎯 What's Next?

After completing Batch 4, you should have solid skills in:
- ✅ Serverless compute with Azure Functions and Durable Functions
- ✅ Business process automation with Logic Apps
- ✅ CI/CD pipelines with Azure DevOps and GitHub Actions
- ✅ Infrastructure as Code with both Bicep and Terraform

**Proceed to → Batch 5: Monitoring, Governance & Cost Management** where you'll tackle Azure Monitor, Application Insights, governance at scale, cost optimization, compliance, and disaster recovery.
