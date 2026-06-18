# Phase 12: Security and Compliance

This phase covers the security posture of your DevOps platform. You will implement Least Privilege RBAC models, Azure Key Vault secrets integration, audit trail monitoring, and a comprehensive 50-item security hardening checklist.

---

## 1. Theory & Hardening Concepts

### 1.1 Access Control and RBAC
* **Azure DevOps RBAC**: Permissions are assigned to security groups (e.g. Project Administrators, Contributors, Readers) at the organization, project, repository, or pipeline level.
* **Least Privilege**: The principle of restricting users and automated service accounts to only the minimum permissions necessary to complete their tasks.
* **Workload Identity Federation (WIF)**: The recommended standard for service connections. WIF uses OpenID Connect (OIDC) trust relationships between Azure DevOps and Entra ID. It removes the need for client secrets, which are prone to leakage and require rotation.

### 1.2 Secrets Isolation
* **Azure Key Vault**: A secured cloud service for encrypting and managing keys, secrets, and certificates.
* **Managed Identity**: Eliminates credentials in code. Applications run under an identity recognized by Entra ID, allowing them to access Key Vault dynamically.
  * **System-assigned**: Bound to a single Azure resource (e.g. Web App). Deleted if the resource is deleted.
  * **User-assigned**: An independent Azure resource that can be shared across multiple resources.

---

## 2. Platform RBAC Configuration

Below is the authorization scheme for the DevOps platform:

| Scope | Security Group | Azure DevOps Role | Target Permissions |
| :--- | :--- | :--- | :--- |
| **Org Settings** | Platform Admins | Project Collection Admin | Administer all projects, billing, extensions. |
| **Project Settings** | DevOps Leads | Project Administrator | Create service connections, edit pools. |
| **Git Repositories** | Developers | Contributors | Read, Pull, Push to feature/* branches. |
| **Git Repositories** | Tech Leads | Project Administrators | Review PRs, merge release/* branches. |
| **Library / Vault** | Build Agents | Reader (Service Account) | Read variable values, download secure files. |
| **Service Connection** | Pipelines | User | Use OIDC token to deploy to resource groups. |

---

## 3. Azure Key Vault & YAML Integration

This configuration retrieves database credentials dynamically from Key Vault during build runtimes:

```yaml
trigger: none

pool:
  vmImage: 'ubuntu-latest'

variables:
- name: azureServiceConnection
  value: 'sc-azure-subscription-dev'
- name: keyVaultName
  value: 'kv-enterprise-banking'

stages:
- stage: RetrieveSecretsStage
  displayName: 'Fetch Safe Configurations'
  jobs:
  - job: FetchSecrets
    steps:
    # 1. Retrieve Secrets from Key Vault using OIDC connection
    - task: AzureKeyVault@2
      inputs:
        azureSubscription: '$(azureServiceConnection)'
        KeyVaultName: '$(keyVaultName)'
        SecretsFilter: 'DB-PASSWORD,JWT-SECRET' # Comma-separated secret names
        RunAsPreJob: false # Load during step execution, not pre-job initialization
      displayName: 'Download Secrets'

    # 2. Verify secrets are loaded (masked in logs)
    - script: |
        echo "Validating DB password extraction..."
        # If printed, this prints *** to protect the secret
        echo "DB Password is: $(DB-PASSWORD)"
      displayName: 'Verify Secret Masking'
```

---

## 4. Azure Portal UI Steps

### 4.1 Creating Azure Key Vault & Adding Secrets
1. Log in to the **Azure Portal**. Search for **Key vaults**. Click **Create**.
2. Resource Group: `rg-devops-platform`. Key vault name: `kv-enterprise-banking`. Region: `East US`.
3. Under **Access configuration**, select **Azure role-based access control** (recommended).
4. Click **Review + Create**, then **Create**.
5. Once created, open the vault, go to **Secrets**, and click **+ Generate/Import**.
6. Name: `DB-PASSWORD`. Value: `my-secure-password-123`. Click **Create**.

### 4.2 Granting Azure DevOps Access to Key Vault
1. Inside the Key Vault dashboard, select **Access control (IAM)**.
2. Click **+ Add** -> **Add role assignment**.
3. Role: **Key Vault Secrets User**.
4. Assign access to: **User, group, or service principal**.
5. Select the Service Principal identity associated with your Azure DevOps service connection (`sc-azure-subscription-dev`).
6. Click **Review + assign**.

---

## 5. Security Hardening Checklist (50 Items)

Perform these audits weekly to secure your Azure DevOps and cloud environments:

### 5.1 Identity and Organization Security (10 Items)
- [ ] Enable Multi-Factor Authentication (MFA) for all user accounts in Microsoft Entra ID.
- [ ] Enforce Entra ID conditional access policies to block logins from unauthorized IP ranges.
- [ ] Set organization security policy to restrict external guest invitations.
- [ ] Restrict creation of new Azure DevOps organizations to administrators only.
- [ ] Regularly audit users with the "Project Collection Administrator" role.
- [ ] Enforce automatic user de-provisioning when employees leave Entra ID.
- [ ] Limit the lifespan of Personal Access Tokens (PATs) to 30 days or less.
- [ ] Block the creation of PATs with "Full Access" scopes.
- [ ] Enable Audit Logging streaming to Azure Log Analytics.
- [ ] Regularly monitor organization usage logs for anomalous bulk repository downloads.

### 5.2 Repository Security (10 Items)
- [ ] Enable branch policies on `main`, `dev`, and `release/*` branches.
- [ ] Require at least two independent code reviewers on all production PRs.
- [ ] Prohibit Pull Request authors from approving their own code.
- [ ] Require all commits on production branches to be signed using GPG keys.
- [ ] Enable automated secret scanning (e.g. Gitleaks) in PR pipelines.
- [ ] Enforce work item linking on all merges to verify trace audits.
- [ ] Disable the "Bypass policies when pushing" permission for the Contributor role.
- [ ] Block force pushing (`git push -f`) on all branches.
- [ ] Remove stale, merged feature branches automatically after pull requests complete.
- [ ] Audit repository user access lists monthly to prune inactive accounts.

### 5.3 Pipeline and Task Security (10 Items)
- [ ] Restrict pipeline service connection access to specific authorized YAML file IDs.
- [ ] Transition all Service Connections to Workload Identity Federation (OIDC).
- [ ] Avoid using inline scripts to execute operations; use checked-in versioned scripts instead.
- [ ] Mandate the use of specific version tags for external marketplace tasks (e.g. `Task@1.2.3`).
- [ ] Enforce "Required Template" checks on environment deployment gates.
- [ ] Restrict variable group access to authorized release pipelines only.
- [ ] Ensure pipeline diagnostics logging does not print decrypted secrets to screen.
- [ ] Run untrusted builds in isolated, disposable container runners.
- [ ] Disable external PR builds from triggering pipelines automatically without manual verification.
- [ ] Force clean work folders on self-hosted agents after every pipeline execution.

### 5.4 Azure Cloud Infrastructure Hardening (10 Items)
- [ ] Limit service connections permission to Contributor on specific resource groups (no subscription Owner access).
- [ ] Set Key Vault configuration to use Azure RBAC instead of legacy access policies.
- [ ] Disable public network access to Azure Key Vault; use Private Endpoints instead.
- [ ] Enforce HTTPS traffic only on all App Services and Storage Accounts.
- [ ] Disable administrative access logins on Azure Container Registry (use Entra authentication).
- [ ] Apply resource locks (`ReadOnly` or `CanNotDelete`) on production resource groups.
- [ ] Configure Diagnostic Settings on all resources to stream logs to Log Analytics.
- [ ] Disable remote SSH/RDP ports on VM agents; use Azure Bastion or Session Manager instead.
- [ ] Scan container images using Trivy before deploying to App Services.
- [ ] Enable Microsoft Defender for DevOps on your Azure subscription.

### 5.5 Regulatory and Compliance Controls (10 Items)
- [ ] Map all pipeline approvals to ServiceNow or Jira Change Request tickets.
- [ ] Archive audit logs for at least one year to satisfy SOC2 / ISO27001 requirements.
- [ ] Run daily dependency vulnerability scans (SCA) to detect new CVEs.
- [ ] Enforce software licensing verification to prevent using GPL-licensed packages.
- [ ] Generate and publish Software Bill of Materials (SBOM) for all production builds.
- [ ] Limit deployment changes to scheduled business hours only.
- [ ] Ensure database backups are encrypted using customer-managed keys (CMK).
- [ ] Conduct tabletop DR drill exercises quarterly.
- [ ] Maintain an updated recovery runbook documenting active-passive swap commands.
- [ ] Schedule external penetration testing audits annually.

---

## 6. Validation Steps
1. Navigate to **Organization Settings** -> **Audit** in Azure DevOps. Verify that user addition, pipeline deletion, and service connection changes are logged.
2. In the Azure Portal, attempt to access your Key Vault from an unauthorized IP address. Verify that access is blocked.

---

## 7. Troubleshooting Steps
* **Secret shows up as plain text**: If you see secrets printed in cleartext in build console logs, check how they were declared. Secret variables must be referenced using `$(mySecretName)` notation. If you output them using env variables or raw print commands inside shell scripts, they can bypass masking mechanisms.
* **WIF Token Exchange Failures**: If Workload Identity Federation fails, ensure the Subject Identifier (issuer URL, org, project, and pipeline scope) matches the configuration created inside the Entra ID App Registration trust panel.

---

## 8. Interview Questions & Answers

1. **What is the Principle of Least Privilege?**
   * *Answer*: Restricting users, service accounts, and processes to only the minimal set of resources and permissions required to perform their jobs.
2. **What is Workload Identity Federation?**
   * *Answer*: An authentication method using OIDC trust relationships to authenticate pipelines with Azure without using client secrets.
3. **What is a System-assigned Managed Identity?**
   * *Answer*: An identity created in Entra ID that is tied directly to the lifecycle of a single Azure resource (e.g. App Service). It is deleted when the resource is deleted.
4. **How do you prevent secrets from leaking in pipeline logs?**
   * *Answer*: Define variables as Secrets in the UI or Key Vault. Azure DevOps masks these values with `***` in console outputs.
5. **How does Azure RBAC differ from legacy Key Vault Access Policies?**
   * *Answer*: Key Vault Access Policies are legacy configurations restricted to Key Vault settings. Azure RBAC uses standard role assignments (e.g. Secrets User, Reader) managed globally via IAM.
6. **What is Microsoft Defender for DevOps?**
   * *Answer*: A service in Defender for Cloud that provides security visibility across DevOps pipelines, container images, and IaC templates.
7. **What is the purpose of GPG signature verification in Git?**
   * *Answer*: It cryptographically signs commits to verify that they were authored by the trusted owner of the key, preventing commit spoofing.
8. **What does the AzureKeyVault task do?**
   * *Answer*: It downloads secrets from an Azure Key Vault and injects them as pipeline variables during execution.
9. **Explain how to audit Azure DevOps security changes.**
   * *Answer*: Navigate to Organization Settings -> Audit to view the audit log stream, or configure it to stream to Log Analytics.
10. **Why should you disable the ACR admin user account?**
    * *Answer*: The admin user account uses shared, static passwords. Disabling it forces pipelines to authenticate securely using dynamic Entra ID service principals.
11. **How do you secure self-hosted agents?**
    * *Answer*: Run them on dedicated, hardened VMs, restrict network permissions, and clean build workspaces after every run.
12. **What is SOC2 compliance in DevOps?**
    * *Answer*: An auditing procedure that ensures your organization manages data securely based on security, availability, processing integrity, confidentiality, and privacy.
13. **How do you restrict access to a Variable Group?**
    * *Answer*: Open the variable group in the Library settings, click Security, and assign permissions to specific users or pipelines.
14. **What is OIDC?**
    * *Answer*: OpenID Connect. An identity verification standard built on top of OAuth 2.0.
15. **What is conditional access?**
    * *Answer*: Entra ID policies that evaluate user sign-in signals (IP location, device compliance, MFA) before granting access to resources.
16. **Why should you limit PAT lifetimes?**
    * *Answer*: If a PAT is leaked, it grants access to your repositories. Shorter lifespans reduce the window of exposure.
17. **What is a Private Endpoint?**
    * *Answer*: A network configuration that assigns a private IP address from your Virtual Network to an Azure PaaS service (like Key Vault), blocking public access.
18. **What is the Key Vault Secrets User role?**
    * *Answer*: An Azure RBAC role that allows reading secret values from Key Vault but does not allow editing or deleting them.
19. **How do you enforce code reviews in Azure Repos?**
    * *Answer*: By configuring branch policies on target branches and checking "Require a minimum number of reviewers".
20. **Can you encrypt Azure DevOps repositories using your own keys?**
    * *Answer*: Azure DevOps repositories are encrypted at rest by default using Microsoft-managed keys. Customer-managed keys (CMK) are supported in Enterprise plans.

---

## 9. Real Industry Practices
- **No Secrets in Repositories**: Run Gitleaks in PR pipelines. If a secret is committed, rotate it immediately and delete the commit from the repository history.
- **Role Separation**: Separate the teams managing pipelines from those managing cloud resources.

---

## 10. Production Best Practices
- **Enforce Key Vault RBAC**: Use Azure RBAC for Key Vault access to centralize permission management.
- **Regular Audit Reviews**: Stream audit logs to a SIEM (like Microsoft Sentinel) to detect anomalous access patterns in real time.

---

## 11. Common Failure Scenarios
- **Secret Leaked in Logs**: Occurs when secrets are modified (e.g. Base64 encoded) in scripts, which prevents the masking engine from recognizing and hiding the raw secret values.
- **Expired OIDC Federation Trust**: Deployment fails because the trust relationship credentials inside Entra ID expired. Monitor federation credentials.
