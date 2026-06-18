# Phase 7: Environment Architecture

This phase details how to configure Azure DevOps Environments (QA, UAT, Stage, Prod, and DR) and secure them using role-based permissions, manual approvals, and deployment checks.

---

## 1. Theory & Environment Governance

### 1.1 Azure DevOps Environments
An **Environment** is a logical collection of resources (VMs, Kubernetes clusters, App Services, or generic targets) that can be targeted by deployments. 

Environments provide:
* **Traceability**: Audit log showing exactly which commit and pipeline run deployed to which environment at what time.
* **Security Boundaries**: Gatekeepers to prevent unauthorised code from deploying to high-value environments (like Production or UAT).

### 1.2 Deployment Checks & Gates
Unlike classic release gates, YAML pipelines configure checks directly on the Environment resource:
* **Manual Approvals**: Requires one or more specified users to sign off before the stage begins.
* **Exclusive Lock**: Prevents concurrent runs from executing on the environment simultaneously (avoids overlapping deployments).
* **Business Hours**: Restricts deployments to specified time windows.
* **Required Template**: Forces the pipeline to use a pre-approved YAML template to perform the deployment.
* **Query Azure Monitor Alerts**: Blocks deployment if active critical alerts exist on the target environment.

---

## 2. Environment Matrix Blueprints

### 2.1 Permissions Matrix
Different team roles require varying levels of access to environment configurations:

| Environment | Creator / Owner | Reader (Can view logs) | User (Can run deployments) |
| :--- | :--- | :--- | :--- |
| **QA** | DevOps Engineer | Developers | Build Service Account, Developers |
| **UAT** | DevOps Engineer | Business Stakeholders | Build Service Account, QA Leads |
| **Stage** | Lead Architect | QA Team | Build Service Account |
| **Prod** | Lead Architect | Security Auditors | Build Service Account |
| **DR** | Lead Architect | Security Auditors | Build Service Account |

### 2.2 Checks & Approvals Matrix
Each environment enforces a set of validation gates:

| Environment | Approver Roles | Multi-Approver Rules | Additional Checks |
| :--- | :--- | :--- | :--- |
| **QA** | None | Automated only | None |
| **UAT** | QA Lead, Product Owner | Any one approver | Exclusive Lock |
| **Stage** | Release Manager | All approvers required | Business Hours |
| **Prod** | CAB, DevOps Lead, PM | All approvers required | Exclusive Lock, Required Template, Alert Query |
| **DR** | Enterprise Release Manager | All approvers required | Exclusive Lock |

---

## 3. Azure DevOps UI Steps

### 3.1 Creating Environments
1. Navigate to **Pipelines** -> **Environments** in your Azure DevOps project.
2. Click **Create environment** (top right).
3. Name: `env-qa`. Resource: Select **None** (generic target). Click **Create**.
4. Repeat this process to create `env-uat`, `env-stage`, `env-prod`, and `env-dr`.

### 3.2 Configuring Approvals and Checks
1. Go to **Pipelines** -> **Environments** and select `env-prod`.
2. Click the **three vertical dots** in the top right corner of the environment dashboard, and select **Approvals and checks**.
3. Click the **+** (Add check) icon:
   * Select **Approvals**. Enter the emails of the approvers (e.g. Project Administrators group or specific user IDs). Under Control Options, set timeout to `7 Days`. Click **Create**.
   * Click **+** again. Select **Exclusive Lock**. Click **Create** (this prevents multiple build runs from deploying to Prod at once).
   * Click **+** again. Select **Business Hours**. Define standard working hours (e.g., Monday to Friday, 08:00 to 17:00). Click **Create**.

---

## 4. Configuration Examples (YAML)

To deployment jobs, reference your environments using the `environment` property:

```yaml
trigger: none # Run on manual or CD release trigger

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: DeployQA
  displayName: 'Deploy to QA'
  jobs:
  - deployment: DeployJobQA
    displayName: 'QA Deployment'
    environment: 'env-qa' # References QA environment check-free
    strategy:
      runOnce:
        deploy:
          steps:
          - script: |
              echo "Deploying application to QA App Service..."
            displayName: 'Execute Deploy Script'

- stage: DeployProd
  displayName: 'Deploy to Production'
  dependsOn: DeployQA
  jobs:
  - deployment: DeployJobProd
    displayName: 'Prod Deployment'
    environment: 'env-prod' # References Prod environment (triggers approvals, locks, business hours checks)
    strategy:
      runOnce:
        deploy:
          steps:
          - script: |
              echo "Deploying application to Production Slot..."
            displayName: 'Execute Deploy Script'
```

---

## 5. Azure Resources Required
No additional Azure cloud infrastructure is required to set up the environments configuration inside Azure DevOps itself.

---

## 6. Git Commands

Commit your deployment pipeline code:

```bash
# Create feature branch for environment testing
git checkout -b feature/env-pipelines
git add pipelines/cd-release.yml
git commit -m "ci: implement environment deployments pipeline structure"
git push origin feature/env-pipelines
```

---

## 7. Validation Steps
1. Run the pipeline.
2. Observe the pipeline execution flow. Once `DeployQA` finishes, the pipeline status changes to **Waiting (1 check passed / 2 pending)** on the `DeployProd` stage.
3. Verify that the configured approver receives an email notification.
4. Open the run summary page. Click the **Review** button to approve or reject the deployment.

---

## 8. Troubleshooting Steps
* **Exclusive Lock Blocking Runs**: If a pipeline run hangs on "Waiting for exclusive lock", check for other active or cancelled deployments running on the same environment. Cancel hung runs to free the lock.
* **Approvals Missing in YAML**: Ensure the environment name specified in the YAML (`environment: 'env-prod'`) matches the spelling of the environment created in the UI exactly. Environment names are case-sensitive.

---

## 9. Interview Questions & Answers

1. **What is an Environment in Azure DevOps?**
   * *Answer*: A target collection of resources that can receive deployments, allowing traceability and security gates.
2. **What is the difference between a job and a deployment job?**
   * *Answer*: A regular job runs scripts. A deployment job is specialized: it logs deployment history, references environments, and supports advanced deployment strategies (rolling, canary, runOnce).
3. **What is the purpose of the Exclusive Lock check?**
   * *Answer*: To prevent concurrent pipeline runs from deploying to the same resource group or app service at the same time, preventing config corruption.
4. **How do you restrict deployments to business hours?**
   * *Answer*: By configuring the "Business Hours" check on the environment.
5. **How long can a pipeline wait for an approval before timing out?**
   * *Answer*: The default maximum timeout is 30 days, but it is configurable in the check settings.
6. **Can a group of users be configured as approvers?**
   * *Answer*: Yes, you can add Azure DevOps groups (e.g. `[Project]\Contributors` or `[Project]\Release Managers`).
7. **What is the "Required Template" check?**
   * *Answer*: A check that forces pipelines to use a specific central template file, preventing developers from bypassing security steps in custom pipelines.
8. **What is deployment traceability?**
   * *Answer*: The ability to audit which commits, PRs, and work items are present in a specific environment version.
9. **Explain the difference between pre-deployment and post-deployment checks.**
   * *Answer*: Pre-deployment checks execute before the job starts. Post-deployment checks run after the deployment completes (e.g. health monitor checks).
10. **What is the "REST API" check?**
    * *Answer*: A check that invokes an external HTTP endpoint and waits for a successful response code before letting the pipeline proceed.
11. **How does Azure DevOps handle multi-approver logic?**
    * *Answer*: You can configure it so that either any one user from the list must approve, or all users on the list must sign off.
12. **Can you add physical virtual machines as resources inside an Environment?**
    * *Answer*: Yes, by registering the machines with the Azure Pipelines agent registration script under the environment resource tab.
13. **How does Kubernetes resource mapping work in Environments?**
    * *Answer*: By linking a Kubernetes Service Account and Namespace, allowing pipeline deployments to target specific namespaces.
14. **What happens if a check fails?**
    * *Answer*: The stage is marked as Failed, and no deployment tasks are executed.
15. **Why do we separate QA and Production environment checks?**
    * *Answer*: QA needs to be fast and frictionless for developers. Production needs strict governance, change approvals, and audit trails.
16. **How do you monitor environment deployment history?**
    * *Answer*: Go to Pipelines -> Environments -> select your environment. The history tab lists all runs.
17. **What is the "Invoke Azure Function" check?**
    * *Answer*: A check that runs an Azure Function (e.g., to query database state or external APIs) and evaluates the output.
18. **Can you modify environment checks programmatically?**
    * *Answer*: Yes, via the Azure DevOps REST API.
19. **What does the "Any one" approver option mean?**
    * *Answer*: Only one person from the specified approvers list needs to approve the deployment.
20. **Why are environment checks defined in the UI instead of YAML?**
    * *Answer*: If check configurations were defined in YAML, a developer could change the YAML in a feature branch to bypass the checks. UI-based checks cannot be modified by code.

---

## 10. Real Industry Practices
* **CAB Integration**: Tie production approvals to ServiceNow Change Request ticket state using the ITSM deployment check.
* **Separate Approver Groups**: Keep development leads, product managers, and security officers in separate approval groups to ensure segregation of duties.

---

## 11. Production Best Practices
* **Enforce Exclusive Locks**: Set locks on UAT, Stage, and Prod to guarantee linear deployments.
* **Alert Integration**: Enable the "Query Azure Monitor Alerts" check to block deployments if your app's error metrics spike.

---

## 12. Common Failure Scenarios
* **Timeout Failure**: Deployment fails because the approver did not respond before the approval timeout limit expired.
* **User Permission Drift**: Developers losing access to trigger pipelines due to group modifications.
