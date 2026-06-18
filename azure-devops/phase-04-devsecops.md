# Phase 4: DevSecOps Integration

In this phase, you will integrate advanced DevSecOps security scanners (SonarCloud, Gitleaks, Trivy, Checkov, and OWASP Dependency Check) directly into the CI/CD pipeline to enforce security quality gates.

---

## 1. Theory & Shift-Left Security

### 1.1 Shift-Left Security Concept
Shift-left security is the practice of moving security checks earlier in the software development lifecycle (SDLC). Instead of performing security audits right before production deployment (shift-right), scanning is done during PR validation and build phases. This makes vulnerabilities cheaper and faster to fix.

### 1.2 Security Concepts & SBOM
* **SAST (Static Application Security Testing)**: Scans source code for vulnerabilities (e.g., SQL injection, cross-site scripting) without executing it (SonarCloud/SonarQube).
* **SCA (Software Composition Analysis)**: Identifies vulnerabilities in third-party library dependencies (OWASP Dependency Check).
* **IaC Scanning**: Inspects infrastructure-as-code files (Terraform, Bicep, Kubernetes YAML) for security misconfigurations (Checkov).
* **Secret Scanning**: Searches commit history for leaked credentials (Gitleaks).
* **Container Scanning**: Analyzes base OS and packages inside container images (Trivy).
* **SBOM (Software Bill of Materials)**: A structured list of all software components, dependencies, and metadata used inside an application. Vital for tracking vulnerability exposure.

---

## 2. DevSecOps Maturity Model

Below is the roadmap for establishing DevSecOps in your organization:

| Maturity Level | Target Practices | Tools Used |
| :--- | :--- | :--- |
| **Level 1: Reactive** | basic code linting, credentials masking | ESLint, basic secrets patterns |
| **Level 2: Standard** | automated SAST, secret scanning on commits | SonarCloud, Gitleaks |
| **Level 3: Advanced** | IaC scans, SCA dependencies audit, block failures | Checkov, OWASP Dependency Check |
| **Level 4: Optimized** | container scans, runtime vulnerability matching, SBOM | Trivy, Azure Defender for DevOps |

---

## 3. Security Quality Gates Thresholds

To enforce compliance, pipelines will fail if the following scan results are detected:

| Scan Type | Tool | Critical Threshold (Fail Build) | High Threshold (Fail Build) | Medium Threshold (Warn Only) |
| :--- | :--- | :--- | :--- | :--- |
| **SAST** | SonarCloud | New Bugs > 0 | Quality Gate Failed | Coverage < 80% |
| **SCA** | OWASP Audit | Any Critical | Severity High count > 0 | Medium vulnerabilities > 5 |
| **IaC** | Checkov | Any Critical | Severity High count > 0 | Warnings allowed |
| **Secret Scan**| Gitleaks | Any leak found | Any leak found | N/A (Secrets are binary) |
| **Container** | Trivy | Any Critical | Severity High count > 0 | Allowed with warnings |

---

## 4. UI Steps

### 4.1 SonarCloud Setup in Azure DevOps
1. Go to `https://sonarcloud.io` and log in with your Azure DevOps credentials.
2. Create a new organization and project in SonarCloud.
3. Generate a **SonarCloud Access Token** under your account settings.
4. Open Azure DevOps. Navigate to **Project Settings** -> **Service connections**.
5. Click **New service connection**, select **SonarCloud**, enter the token you generated, and name the connection `sc-sonarcloud`.
6. Go to **Project Settings** -> **Pipelines** -> **Library** and add SonarCloud variables to a variable group (or reference them directly).

---

## 5. Complete Security Pipeline YAML

This unified security pipeline runs SAST, Secret Scanning, SCA, and IaC checks. It runs on Microsoft-hosted agents or local runners:

```yaml
trigger: none # Run on PRs and CI validations only

variables:
- group: vg-shared-config
- name: SonarCloudProjectKey
  value: 'payment-gateway-key'
- name: SonarCloudOrg
  value: 'my-sonarcloud-org'

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: SecurityScans
  displayName: 'DevSecOps Vulnerability Audits'
  jobs:
  - job: CodeScans
    displayName: 'Static & Dependency Code Analysis'
    steps:
    # 1. Gitleaks Secret Scanning
    - script: |
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz | tar -xz
        ./gitleaks detect --source=$(System.DefaultWorkingDirectory) --verbose --redact
      displayName: 'Gitleaks Credentials Scan'

    # 2. Checkov IaC Scanning
    - script: |
        pip install checkov
        checkov --directory $(System.DefaultWorkingDirectory) --framework terraform,bicep --soft-fail
      displayName: 'Checkov IaC Misconfiguration Scan'

    # 3. SonarCloud Analysis Setup
    - task: SonarCloudPrepare@1
      inputs:
        SonarCloud: 'sc-sonarcloud'
        organization: '$(SonarCloudOrg)'
        scannerMode: 'CLI'
        configMode: 'manual'
        cliProjectKey: '$(SonarCloudProjectKey)'
        cliProjectName: 'Payment Gateway App'
        extraProperties: |
          sonar.sources=src
          sonar.tests=src/tests
          sonar.javascript.lcov.reportPaths=coverage/lcov.info
      displayName: 'Prepare SonarCloud Analysis'

    # 4. Run SonarCloud Scanner
    - task: SonarCloudAnalyze@1
      displayName: 'Execute SonarCloud Code Analysis'

    # 5. Check SonarCloud Quality Gate
    - task: SonarCloudPublish@1
      inputs:
        pollingTimeoutSec: '300'
      displayName: 'Publish Quality Gate Results'

    # 6. OWASP Dependency Check (SCA)
    - script: |
        # Download and run OWASP Dependency-Check CLI
        wget https://github.com/jeremymicheli/dependency-check-sonar-plugin/releases/download/1.2.5/sonar-dependency-check-plugin-1.2.5.jar
        # Note: In real production, use the native Azure DevOps OWASP Dependency Check extension task
        echo "Running SCA checks..."
      displayName: 'OWASP Dependency Check'
```

---

## 6. Git Commands

How to configure and commit your local `.gitleaks.toml` configuration to ignore public mock testing keys:

```bash
# Create gitleaks configuration file
cat <<EOT > .gitleaks.toml
[allowlist]
description = "Ignore developer mock configurations"
paths = [
    '''src/tests/.*'''
]
EOT

# Commit and push config
git checkout -b feature/security-compliance
git add .gitleaks.toml
git commit -m "security: add custom Gitleaks configuration"
git push origin feature/security-compliance
```

---

## 7. Validation Steps
1. Create a Pull Request with a mock API token (e.g. `API_KEY = "xoxb-1234567890"`) inside a file. Verify that the **Gitleaks Credentials Scan** stage fails immediately and prints the leak details.
2. Log in to SonarCloud to inspect your dashboard. Verify that code complexity, security issues, and duplications are correctly calculated.

---

## 8. Troubleshooting Steps
* **Checkov pip command fails**: Ensure the runner VM has Python installed. If using hosted agents, Python is pre-installed. For self-hosted agents, run `sudo apt update && sudo apt install -y python3-pip`.
* **SonarCloud Quality Gate Timeout**: If the task hangs on "Publish Quality Gate", increase the `pollingTimeoutSec` parameter or verify that your service connection credentials are valid.
* **False Positives**: To skip false positives in SonarCloud, use the web portal to tag the issue as "Safe" or "False Positive". For Checkov, add a comment in your code: `# bridgecrew:skip=CKV_AZURE_33:Skip reason`.

---

## 9. Interview Questions & Answers

1. **What is Shift-Left Security?**
   * *Answer*: Performing security tests early in the development lifecycle (such as during code editing and commit phases) rather than waiting until QA or Production.
2. **What is the difference between SonarCloud and SonarQube?**
   * *Answer*: SonarCloud is a cloud-based SaaS platform maintained by SonarSource. SonarQube is self-hosted and requires maintaining server infrastructure and databases.
3. **What is an SBOM?**
   * *Answer*: Software Bill of Materials. It lists all dependency packages, licenses, and versions inside an application to track security exposure.
4. **How do you configure Checkov to not fail the pipeline on low-severity findings?**
   * *Answer*: Run Checkov with the `--soft-fail` flag, or specify `--skip-framework` to skip non-critical compliance checks.
5. **What is a False Positive in SAST scans?**
   * *Answer*: A security warning triggered by a tool that does not pose an actual threat in runtime (e.g., using a mock key inside a test suite).
6. **Why is dependency scanning (SCA) important?**
   * *Answer*: Most modern codebases consist of open-source libraries. SCA alerts developers when those dependencies contain known CVE (Common Vulnerabilities and Exposures) records.
7. **What happens if Gitleaks detects a secret inside a previous commit?**
   * *Answer*: Gitleaks scans the entire commit history. Even if the secret is removed in the latest commit, it will fail the build if the secret remains in the Git database history.
8. **How does Trivy scan container images?**
   * *Answer*: It inspects package databases and OS layers inside the container image, checking them against known vulnerability registries.
9. **Explain how to exclude code paths from SonarCloud analysis.**
   * *Answer*: Add `sonar.exclusions=path/to/files/**/*` in your `.sonarcloud.properties` file.
10. **What is the purpose of OWASP Dependency-Check?**
    * *Answer*: An open-source tool that analyzes project dependencies and reports known vulnerabilities.
11. **How does OIDC make DevSecOps pipelines more secure?**
    * *Answer*: It removes long-lived subscription secrets from the pipeline configuration, preventing potential credential leaks.
12. **What is SAST vs DAST?**
    * *Answer*: SAST scans static source code. DAST (Dynamic Application Security Testing) tests running applications externally (like penetration testing) to find live vulnerabilities.
13. **How do you ignore a rule in Gitleaks?**
    * *Answer*: Add the file path or specific hash to the `[allowlist]` section of `.gitleaks.toml`.
14. **Why do we run Checkov on Infrastructure as Code?**
    * *Answer*: To prevent deploying insecure infrastructure (e.g. storage accounts with public read access or open ports in firewalls).
15. **What is the SonarCloud Quality Gate?**
    * *Answer*: A set of boolean conditions a project must meet before it can be merged (e.g. 0 block issues, coverage > 80%).
16. **How does a pipeline secret differ from a regular variable?**
    * *Answer*: Secrets are masked in console output and stored encrypted by Azure DevOps, whereas regular variables are plain text.
17. **What is Checkov?**
    * *Answer*: A static code analysis tool for infrastructure-as-code (IaC) to detect security misconfigurations.
18. **Can you generate PDF reports from SonarCloud?**
    * *Answer*: Yes, enterprise plans support exporting compliance reports.
19. **How do you secure self-hosted runners?**
    * *Answer*: Run them inside isolated containers, limit network access, and clean the workspace folder after every run.
20. **What is Microsoft Defender for DevOps?**
    * *Answer*: An Azure security service that centralizes DevOps security state monitoring across GitHub, Azure DevOps, and GitLab.

---

## 10. Real Industry Practices
* **Developer Pre-commit Hooks**: Enforce Gitleaks checking locally prior to pushing using `husky` to avoid polluting repository history.
* **Auto-ticket Creation**: Configure your DevSecOps pipelines to auto-submit Jira/Azure Boards work items when dependency vulnerabilities are uncovered.

---

## 11. Production Best Practices
* **No Secrets in History**: If Gitleaks detects a secret, invalidate the credentials immediately. Do not just delete the line; rotate the secret since it is stored in the Git history.
* **Strict Quality Gates**: Block releases automatically if SonarCloud reports any new critical vulnerabilities.

---

## 12. Common Failure Scenarios
* **NPM Audit Registry Errors**: The pipeline fails because the package registry times out. Implement package mirroring or artifact caching.
* **Outdated Vulnerability DB**: SCA checks failing because the tool cannot update its CVE database due to network proxy issues. Configure local database mirrors.
