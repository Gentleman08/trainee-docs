# Phase 3: PR Validation Pipeline

In this phase, you will implement the Pull Request Validation Pipeline. This pipeline automatically checks code quality, linting, software composition analysis (SCA), and secrets before any code is allowed to merge.

---

## 1. Theory & Conceptual Architecture

### 1.1 YAML Pipeline Anatomy
Azure DevOps pipelines are defined using YAML. An enterprise pipeline consists of these components:
* **Trigger**: Dictates when the pipeline runs. For PR validation, we use explicit `pr:` triggers.
* **Stage**: A logical collection of jobs (e.g., Build, Test, Deploy).
* **Job**: Runs on a single agent. Jobs can execute in parallel.
* **Step / Task**: Sequential execution units inside a job (e.g., executing a script, downloading an artifact).

### 1.2 Pipeline Templates
To avoid repeating tasks across multiple pipelines, we encapsulate jobs/steps in **Templates**. The main pipeline passes parameters to these templates, maintaining a DRY (Don't Repeat Yourself) design.

---

## 2. Architecture Diagram

Below is the workflow of the PR Validation Pipeline:

```mermaid
graph TD
    A[PR Opened/Updated] -->|Trigger| B[PR Validation Pipeline]
    subgraph Pipeline Stages
        B --> C[Stage: Format Check]
        B --> D[Stage: Lint Check]
        B --> E[Stage: SCA Scan]
        B --> F[Stage: Secret Scan]
    end
    C & D & E & F -->|All Pass| G[Quality Gate Passed]
    C | D | E | F -->|Any Fail| H[PR Merging Blocked]
```

---

## 3. Complete YAML Implementation

### 3.1 Template: Formatting & Linting (`pipelines/templates/format-lint.yml`)
Create this template to run formatting (using Prettier/eslint):
```yaml
parameters:
- name: nodeVersion
  type: string
  default: '18.x'

steps:
- task: NodeTool@0
  inputs:
    versionSpec: ${{ parameters.nodeVersion }}
  displayName: 'Install Node.js'

- script: |
    npm ci
  displayName: 'Install Dependencies'

- script: |
    npm run format:check
  displayName: 'Run Prettier Check'

- script: |
    npm run lint
  displayName: 'Run ESLint Check'
```

### 3.2 Template: Security Scans (`pipelines/templates/security-scans.yml`)
Create this template to run Gitleaks and SCA:
```yaml
steps:
- script: |
    # Install Gitleaks locally on the agent (using binary for cost-effectiveness)
    curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz | tar -xz
    ./gitleaks detect --source=$(System.DefaultWorkingDirectory) --verbose --redact
  displayName: 'Gitleaks Secret Scan'

- script: |
    # SCA check via npm audit (cost-effective OWASP alternative)
    npm audit --audit-level=high
  displayName: 'NPM Dependency Audit (SCA)'
```

### 3.3 Main PR Entrypoint Pipeline (`pipelines/pr-validation.yml`)
This main pipeline runs when a PR is targeted at `dev` or `main`:
```yaml
trigger: none # Disable CI trigger (only run on PR)

pr:
  branches:
    include:
    - main
    - dev
  paths:
    exclude:
    - README.md
    - docs/*

pool:
  vmImage: 'ubuntu-latest' # Microsoft Hosted Agent (or use 'Default' for self-hosted)

stages:
- stage: FormatAndLint
  displayName: 'Format and Lint Validation'
  jobs:
  - job: CodeQuality
    displayName: 'Code Quality Analysis'
    steps:
    - template: templates/format-lint.yml
      parameters:
        nodeVersion: '18.x'

- stage: SecurityCompliance
  displayName: 'Security Controls'
  dependsOn: FormatAndLint
  jobs:
  - job: SecurityScans
    displayName: 'Vulnerability and Secret Scans'
    steps:
    - template: templates/security-scans.yml
```

---

## 4. Azure DevOps UI Steps

### 4.1 Creating the YAML Pipeline
1. In the left menu, click **Pipelines** -> **Pipelines**.
2. Click **New pipeline** (top right).
3. Select **Azure Repos Git**. Select your repository (`repo-payment-gateway`).
4. Select **Existing Azure Pipelines YAML file**.
5. Path: `/pipelines/pr-validation.yml`. Click **Continue**.
6. Click **Save** (do not click Run yet).

### 4.2 Integrating Pipeline with Branch Protection
1. Navigate to **Repos** -> **Branches**.
2. Hover over the `dev` branch, select the **three dots**, and click **Branch policies**.
3. Scroll down to **Build validation**. Click **+ Add build validation**.
4. **Build pipeline**: Select the pipeline you just saved.
5. **Trigger**: Set to **Automatic**.
6. **Policy requirement**: Set to **Required**.
7. **Build expiration**: Set to **Immediately** (forces re-run if target branch changes).
8. Click **Save**.

---

## 5. Git Commands

Prepare your package scripts to support format/lint checks locally and in the pipeline:

```bash
# Add format and lint scripts to your package.json
cat <<EOT > package.json
{
  "name": "payment-gateway",
  "version": "1.0.0",
  "scripts": {
    "format:check": "npx prettier --check 'src/**/*.js'",
    "lint": "npx eslint 'src/**/*.js'"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
EOT

# Create feature branch to test the pipeline
git checkout -b feature/setup-pipelines
git add .
git commit -m "ci: add PR validation pipeline configurations"
git push origin feature/setup-pipelines
```

---

## 6. Validation Steps
1. Navigate to your Azure DevOps project and open a **Pull Request** from `feature/setup-pipelines` to `dev`.
2. Look at the bottom of the PR page. You should see the status message:
   `Required: Build Validation - [Pipeline Name] in progress...`
3. Click the status link to watch the steps execute. Ensure all formatting, linting, Gitleaks, and audit checks complete successfully.
4. If a check fails, verify that the **Merge** button is disabled.

---

## 7. Troubleshooting Steps
* **Pipeline not triggering**: Ensure the PR target branch matches the branch configured in your YAML `pr.branches.include` block.
* **Gitleaks fails on mock secrets**: Check your source code for test keys or mock passwords (e.g. `const api_key = "12345"`). Gitleaks detects patterns. Use local configs or configuration parameter switches to skip mock folders.
* **Build Validation Not Listed**: Ensure the pipeline has run at least once manually or was saved successfully before attempting to add it to branch policies.

---

## 8. Interview Questions & Answers

1. **How do you disable CI triggers and only run on PRs?**
   * *Answer*: Set `trigger: none` and specify target branches under the `pr:` section.
2. **What is the difference between `npm install` and `npm ci` in a pipeline?**
   * *Answer*: `npm install` can update package versions and modify package-lock.json. `npm ci` installs versions locked in package-lock.json strictly, runs faster, and deletes existing node_modules to guarantee a clean build.
3. **What is static code analysis?**
   * *Answer*: Analyzing application source code for styling, syntax, and vulnerability issues without executing the program.
4. **Explain SCA (Software Composition Analysis).**
   * *Answer*: Inspecting third-party libraries and open-source dependencies used by your application to locate known vulnerabilities (CVEs) and license compliance issues.
5. **How does GitLeaks perform secret scanning?**
   * *Answer*: It scans the Git history and commit differences using regular expressions and high-entropy calculations to search for keys, tokens, and certificates.
6. **What is a template parameter in Azure Pipelines?**
   * *Answer*: A typed variable defined in a template file whose value is supplied by the calling pipeline to control execution logic.
7. **How does Build Validation enforce branch quality?**
   * *Answer*: It forces the PR to compile and pass all tests successfully in an isolated merge commit before the Pull Request is allowed to merge.
8. **What does `dependsOn` do in a YAML pipeline?**
   * *Answer*: It defines dependencies between stages or jobs, controlling their order of execution.
9. **How do you run steps inside a pipeline conditionally?**
   * *Answer*: Using the `condition` attribute (e.g. `condition: succeeded()`).
10. **Why exclude README.md from PR triggers?**
    * *Answer*: Changing documentation does not impact app functionality. Skipping runs saves pipeline build minutes and reduces developer waiting times.
11. **What is the difference between a task and a script in YAML?**
    * *Answer*: A task is a packaged, versioned plugin provided by Microsoft or third parties. A script is a raw shell command (bash, powershell) executed on the runner.
12. **How do you store sensitive configuration variables in pipelines?**
    * *Answer*: By configuring them as secrets inside a Variable Group or loading them directly from Azure Key Vault.
13. **What are system variables in Azure Pipelines?**
    * *Answer*: Pre-populated variables provided by Azure DevOps during execution (e.g. `$(Build.SourceBranch)`, `$(System.DefaultWorkingDirectory)`).
14. **How do you configure path filters in YAML pipelines?**
    * *Answer*: Under `pr.paths` or `trigger.paths`, define `include` and `exclude` lists containing file/directory paths.
15. **What is Snyk?**
    * *Answer*: A popular developer-security platform used for SCA, container scanning, and IaC vulnerability detection.
16. **Why should you use fixed versions for tasks in YAML (e.g. NodeTool@0 instead of NodeTool)?**
    * *Answer*: To prevent breaking changes if a task author releases a new major version.
17. **Can you run a PR pipeline on a self-hosted agent?**
    * *Answer*: Yes, by setting the `pool.name` property to your self-hosted agent pool name.
18. **How does a pipeline handle multi-line script tasks?**
    * *Answer*: By using the pipe character `|` after the script definition.
19. **What is the purpose of Prettier?**
    * *Answer*: An opinionated code formatter that enforces consistent styling rules across the codebase.
20. **What is code entropy in secret scanning?**
    * *Answer*: A mathematical measure of randomness in a string. High entropy strings (like random keys/hashes) trigger secret detection rules.

---

## 9. Real Industry Practices
* **Linting Autocorrect**: Run formatting/linting scripts with `--fix` during local commit hooks (e.g., using `husky`) to prevent PR builds from failing on simple spacing mistakes.
* **Audit Enforcement**: Configure your SCA stage to fail the build if vulnerabilities with severity of `High` or `Critical` are detected.

---

## 10. Production Best Practices
* **Use Node / Tool Installers**: Always specify exact node/runtime versions in pipelines to prevent discrepancy failures.
* **Fail Fast**: Position fast tasks (linting, secret scan) in early stages or jobs to exit quickly if code is broken.

---

## 11. Common Failure Scenarios
* **Dependency Failures**: PR pipelines failing due to package registries being offline. Introduce local caching of node modules/packages to mitigate this.
* **Incorrect Node version**: Running linting tasks using incompatible Node.js runtimes.
