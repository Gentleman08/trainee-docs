# 05 — DevSecOps & Pipeline Security (Scenarios 45–52)

[⬅️ Back to Index](README.md) · [⬅️ Previous: IaC Pipelines](04-iac.md)

---

> **DevSecOps** = building security checks *into* the pipeline instead of a security review at
> the end. It also means **securing the pipeline itself**. A CI/CD system holds the keys to
> production, which makes it a top target for attackers.

### The security layers of a pipeline

```
 Code commit ─► SECRET SCAN ─► SAST ─► DEPENDENCY SCAN ─► IaC SCAN ─► build ─► IMAGE SCAN ─► deploy staging ─► DAST
     (leaked keys)  (code bugs) (vulnerable libs) (misconfig)      (CVEs in image)          (running app)
```

| Check | Finds | Example tools |
|-------|-------|---------------|
| **Secret scanning** | Passwords/keys committed to Git | gitleaks, GitHub secret scanning, trufflehog |
| **SAST** (Static Application Security Testing) | Insecure code patterns (SQL injection, XSS) | CodeQL, Semgrep, SonarQube |
| **SCA** (Software Composition Analysis) | Known-vulnerable dependencies | Dependabot, npm audit, Trivy fs, OWASP Dependency-Check |
| **IaC scanning** | Insecure cloud config (public buckets, open ports) | Checkov, tfsec/Trivy config, KICS |
| **Container scanning** | CVEs in OS packages in the image | Trivy, Grype, Defender, Inspector (Chapter 02) |
| **DAST** (Dynamic AST) | Vulnerabilities in the *running* app | OWASP ZAP, Burp |

---

## Table of Contents

| # | Scenario | Focus |
|---|----------|-------|
| 45 | [Set up OIDC / workload identity (no stored cloud secrets)](#scenario-45--set-up-oidc-and-workload-identity) | Auth |
| 46 | [Secret scanning](#scenario-46--secret-scanning) | gitleaks |
| 47 | [SAST — static code analysis](#scenario-47--sast) | CodeQL, Semgrep |
| 48 | [Dependency (SCA) scanning + automated update PRs](#scenario-48--dependency-scanning) | Dependabot, Trivy fs |
| 49 | [IaC security scanning](#scenario-49--iac-security-scanning) | Checkov |
| 50 | [DAST against staging](#scenario-50--dast-against-staging) | OWASP ZAP |
| 51 | [Reading runtime secrets from Key Vault / Secrets Manager](#scenario-51--reading-secrets-from-a-vault) | Vault integration |
| 52 | [Hardening the pipeline itself](#scenario-52--hardening-the-pipeline-itself) | Supply-chain & permissions |

---

## Scenario 45 — Set up OIDC and workload identity

**🎯 Goal:** One-time setup so pipelines can log in to Azure/AWS **without any stored secret**
(concept in [Chapter 00, §0.8](00-fundamentals.md#08-how-pipelines-log-in-to-clouds)).

### GitHub Actions → Azure (Azure CLI)

```bash
# 1. Create an app registration + service principal for the pipeline
APP_ID=$(az ad app create --display-name "gh-orders-api-prod" --query appId -o tsv)
az ad sp create --id "$APP_ID"

# 2. Trust GitHub tokens — ONLY for the "production" environment of acme/orders-api
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-orders-api-production",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:acme/orders-api:environment:production",
  "audiences": ["api://AzureADTokenExchange"]
}'

# 3. Grant least-privilege access (here: Contributor on ONE resource group)
az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-orders-prod"
```

Then store `AZURE_CLIENT_ID` (= `$APP_ID`), `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` as
**environment variables** on the GitHub `production` environment.

**Subject formats you'll need:**

| Workflow situation | `subject` |
|--------------------|-----------|
| Job with `environment: production` | `repo:acme/orders-api:environment:production` |
| Push to main (no environment) | `repo:acme/orders-api:ref:refs/heads/main` |
| Pull request | `repo:acme/orders-api:pull_request` |
| Tag | `repo:acme/orders-api:ref:refs/tags/v1.2.3` (wildcards not allowed in Entra; use flexible federated credentials or environments) |

### GitHub Actions → AWS

```bash
# 1. Register GitHub as an OIDC identity provider (once per AWS account)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
```

`trust-policy.json`, used when creating the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:acme/orders-api:environment:production" }
    }
  }]
}
```

```bash
aws iam create-role --role-name github-orders-api-prod --assume-role-policy-document file://trust-policy.json
aws iam attach-role-policy --role-name github-orders-api-prod --policy-arn arn:aws:iam::123456789012:policy/orders-api-deploy
```

### Azure DevOps → Azure

Project settings → Service connections → New → **Azure Resource Manager** → **Workload
Identity federation (automatic)**. Pick the subscription and resource group. Azure DevOps creates
the identity and the federated credential for you. Then:

- Untick **"Grant access permission to all pipelines"**, and authorise specific pipelines only.
- Add **Approvals and checks** on the service connection for production
  (e.g. *Required template*, *Branch control*).

### AWS CodeBuild → AWS

There's no federation step. Give the project's **service role** a narrowly scoped policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
      "Resource": "arn:aws:logs:eu-west-1:123456789012:log-group:/aws/codebuild/orders-api*" },
    { "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
    { "Effect": "Allow",
      "Action": ["ecr:BatchCheckLayerAvailability","ecr:InitiateLayerUpload","ecr:UploadLayerPart","ecr:CompleteLayerUpload","ecr:PutImage","ecr:BatchGetImage"],
      "Resource": "arn:aws:ecr:eu-west-1:123456789012:repository/orders-api" },
    { "Effect": "Allow", "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:eu-west-1:123456789012:secret:ci/orders-api/*" }
  ]
}
```

**⚠️ Gotchas:**

- **A trust condition with `repo:acme/*`** lets **any repo in the org** (including a new repo
  an attacker creates) assume the role. Always scope to the repo **and** environment/branch.
- **GitHub OIDC with AWS:** forgetting the `aud` condition, or using `StringLike` with `*` on
  `sub`, is a classic misconfiguration found in audits.
- **Entra ID:** the federated credential subject is **case-sensitive** and must match exactly.

---

## Scenario 46 — Secret scanning

**🎯 Goal:** Fail the pipeline if someone commits a password, API key or private key.

### GitHub Actions

```yaml
name: Secret scan
on: [push, pull_request]

permissions:
  contents: read
  security-events: write

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0                 # scan full history, not just the last commit
      - name: Run gitleaks
        run: |
          docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.21.2 \
            detect --source /repo --redact --verbose \
            --report-format sarif --report-path /repo/gitleaks.sarif
      - uses: github/codeql-action/upload-sarif@v3
        if: ${{ !cancelled() }}
        with:
          sarif_file: gitleaks.sarif
          category: gitleaks
```

> GitHub's own **secret scanning + push protection** (Settings → Code security) blocks known
> token formats **at `git push` time**, before they ever land. Enable it, and keep a CI scan
> for custom patterns.

### Azure DevOps

```yaml
steps:
  - checkout: self
    fetchDepth: 0
  - bash: |
      docker run --rm -v "$(Build.SourcesDirectory):/repo" ghcr.io/gitleaks/gitleaks:v8.21.2 \
        detect --source /repo --redact --verbose \
        --report-format junit --report-path /repo/gitleaks-junit.xml
    displayName: gitleaks
  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFiles: gitleaks-junit.xml
      testRunTitle: Secret scan
```

> With **GitHub Advanced Security for Azure DevOps** enabled, secret scanning push protection
> is built into Azure Repos too.

### AWS CodeBuild

```yaml
version: 0.2
phases:
  build:
    commands:
      # CodeBuild clones shallow by default; set "git clone depth: full" on the project to scan history
      - docker run --rm -v "$CODEBUILD_SRC_DIR:/repo" ghcr.io/gitleaks/gitleaks:v8.21.2 detect --source /repo --redact --verbose --report-format junit --report-path /repo/gitleaks-junit.xml
reports:
  secret-scan:
    files: [gitleaks-junit.xml]
    file-format: JUNITXML
```

**🔍 Explained:**

- **`--redact`** hides the secret values in the output. You don't want the scanner itself
  printing secrets into CI logs.
- **False positives** (test fixtures, example keys) go into a `.gitleaks.toml` allowlist or a
  `.gitleaksignore` file with fingerprints, reviewed in PRs.

**⚠️ Gotchas:**

- **A leaked secret must be ROTATED.** Removing it from the latest commit doesn't help: it's
  in the Git history, forks and clones. Revoke the key first, clean history second.
- **The `gitleaks-action` GitHub Action needs a (free) license key for organisation repos.**
  Running the CLI/container directly, as above, avoids that.

---

## Scenario 47 — SAST

**🎯 Goal:** Analyse source code for security bugs on every PR, and show the findings inline.

### GitHub Actions — CodeQL

```yaml
name: CodeQL
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 3 * * 0"              # weekly full scan catches new queries

permissions:
  contents: read
  security-events: write

jobs:
  analyze:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        language: [javascript-typescript, python]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended
      - uses: github/codeql-action/autobuild@v3     # compiled languages need a build; harmless for JS/Python
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

### Azure DevOps — GitHub Advanced Security for Azure DevOps (CodeQL)

```yaml
steps:
  - task: AdvancedSecurity-Codeql-Init@1
    inputs:
      languages: 'javascript,python'
      querysuite: security-extended
  - task: AdvancedSecurity-Codeql-Autobuild@1
  - task: AdvancedSecurity-Codeql-Analyze@1
```

> Without Advanced Security, use Semgrep (below) or SonarQube's security rules (Chapter 01,
> Scenario 13).

### AWS CodeBuild — Semgrep

```yaml
version: 0.2
phases:
  install:
    runtime-versions: { python: 3.12 }
    commands:
      - pip install semgrep==1.93.0
  build:
    commands:
      - semgrep scan --config p/owasp-top-ten --config p/secrets --junit-xml --output semgrep-junit.xml --error
reports:
  sast:
    files: [semgrep-junit.xml]
    file-format: JUNITXML
```

The same Semgrep command works on GitHub and Azure DevOps.

**🔍 Explained:**

- **CodeQL** builds a database of the code and runs queries for vulnerability patterns. Results
  appear under **Security → Code scanning** and as PR annotations.
- **`security-extended`** adds more queries than the default (more findings, a bit more noise).
- **Semgrep's `--error`** exits non-zero when findings exist, which gates the pipeline.

**⚠️ Gotchas:**

- **CodeQL autobuild fails on complex builds** (custom Maven settings, monorepos). Replace
  `autobuild` with your real build commands.
- **Start in "report only" mode,** fix the backlog, *then* make SAST blocking. Blocking on day
  one with 400 legacy findings gets the check disabled by Friday.

---

## Scenario 48 — Dependency scanning

**🎯 Goal:** Detect vulnerable libraries, and get **automatic PRs** that update them.

### GitHub — Dependabot config (`.github/dependabot.yml`)

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: "/"
    schedule: { interval: weekly, day: monday }
    open-pull-requests-limit: 10
    groups:
      minor-and-patch:                 # one PR for all minor/patch bumps instead of 30 PRs
        update-types: [minor, patch]
  - package-ecosystem: docker
    directory: "/"
    schedule: { interval: weekly }
  - package-ecosystem: github-actions  # keeps pinned action versions up to date too
    directory: "/"
    schedule: { interval: weekly }
```

CI gate (works the same on all platforms):

```yaml
# GitHub Actions
- name: Dependency review (PRs only — blocks NEW vulnerable deps)
  if: github.event_name == 'pull_request'
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high

- name: Trivy filesystem scan (lock files)
  uses: aquasecurity/trivy-action@0.28.0
  with:
    scan-type: fs
    scan-ref: .
    scanners: vuln
    severity: CRITICAL,HIGH
    ignore-unfixed: true
    exit-code: "1"
```

### Azure DevOps

```yaml
steps:
  # With GitHub Advanced Security for Azure DevOps:
  - task: AdvancedSecurity-Dependency-Scanning@1

  # Or with Trivy, anywhere:
  - bash: |
      docker run --rm -v "$(Build.SourcesDirectory):/src" aquasec/trivy:0.56.2 fs \
        --scanners vuln --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 /src
    displayName: Trivy dependency scan
```

> For automated update PRs in Azure Repos, use **Renovate** (runs as a scheduled pipeline) or
> the Dependabot support in Advanced Security.

### AWS CodeBuild

```yaml
version: 0.2
phases:
  build:
    commands:
      - npm ci
      - npm audit --omit=dev --audit-level=high      # language-native check
      - docker run --rm -v "$CODEBUILD_SRC_DIR:/src" aquasec/trivy:0.56.2 fs --scanners vuln --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 /src
```

**🔍 Explained:**

- **The dependency review action** compares the PR's dependency changes with the base branch,
  so it only blocks *newly introduced* risk. Legacy issues don't block every PR.
- **`groups`** batches Dependabot updates, which cuts down PR noise.
- **The `github-actions` ecosystem** keeps action versions (and SHA pins) updated automatically.

**⚠️ Gotchas:**

- **Auto-merging Dependabot PRs without good tests** means auto-merging breaking changes.
  Auto-merge **patch** updates only, and only when CI is green.
- **`npm audit` includes devDependencies by default.** `--omit=dev` focuses on what ships to production.

---

## Scenario 49 — IaC security scanning

**🎯 Goal:** Catch insecure infrastructure (public storage, unencrypted databases, `0.0.0.0/0`
security groups) **before** `terraform apply`.

### GitHub Actions — Checkov with SARIF

```yaml
jobs:
  checkov:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@v12
        with:
          directory: infra/
          framework: terraform
          output_format: cli,sarif
          output_file_path: console,checkov.sarif
          soft_fail: false
          skip_check: CKV_AZURE_35         # documented, reviewed exception (example)
      - uses: github/codeql-action/upload-sarif@v3
        if: ${{ !cancelled() }}
        with:
          sarif_file: checkov.sarif
```

### Azure DevOps

```yaml
steps:
  - bash: |
      docker run --rm -v "$(Build.SourcesDirectory):/src" bridgecrew/checkov:3 \
        -d /src/infra --framework terraform \
        -o cli -o junitxml --output-file-path console,/src/checkov-junit.xml
    displayName: Checkov
  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFiles: checkov-junit.xml
      testRunTitle: IaC security
```

### AWS CodeBuild

```yaml
version: 0.2
phases:
  install:
    runtime-versions: { python: 3.12 }
    commands: [pip install checkov]
  build:
    commands:
      - checkov -d infra --framework terraform,cloudformation -o cli -o junitxml --output-file-path console,checkov-junit.xml
reports:
  iac-security:
    files: [checkov-junit.xml]
    file-format: JUNITXML
```

**🔍 Explained:**

- **Checkov** has 1000+ built-in policies for Terraform, CloudFormation, Bicep/ARM, Kubernetes,
  Helm and Dockerfiles.
- **Inline suppression** with justification, right in the code:
  `# checkov:skip=CKV_AWS_20:Public bucket intentionally hosts the marketing site`.

**⚠️ Gotchas:**

- **Scanning `terraform plan` JSON** (`terraform show -json tfplan > plan.json`;
  `checkov -f plan.json`) catches issues in values only known at plan time (variables, module
  outputs) that static file scanning misses.
- **Also enforce at runtime** with cloud policies (Azure Policy, AWS SCPs/Config). Pipeline
  scans don't stop portal click-ops.

---

## Scenario 50 — DAST against staging

**🎯 Goal:** After deploying to **staging**, run an automated scan against the **running**
website (missing security headers, cookie flags, injection points).

### GitHub Actions — ZAP baseline

```yaml
  dast:
    needs: deploy-staging
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write                    # the action opens/updates an issue with findings
    steps:
      - uses: actions/checkout@v4      # for the rules file
      - uses: zaproxy/action-baseline@v0.14.0
        with:
          target: https://orders-staging.acme.com
          rules_file_name: .zap/rules.tsv     # tune: IGNORE / WARN / FAIL per rule ID
          cmd_options: "-a"
```

### Azure DevOps / AWS CodeBuild — ZAP container

```yaml
# Azure DevOps step
- bash: |
    mkdir -p zap && chmod 777 zap
    docker run --rm -v "$(pwd)/zap:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
      zap-baseline.py -t https://orders-staging.acme.com -r zap-report.html -J zap-report.json -I
  displayName: OWASP ZAP baseline
- publish: zap
  artifact: zap-report
```

```yaml
# AWS CodeBuild buildspec
version: 0.2
phases:
  build:
    commands:
      - mkdir -p zap && chmod 777 zap
      - docker run --rm -v "$(pwd)/zap:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t https://orders-staging.acme.com -r zap-report.html -I
artifacts:
  files: [zap/zap-report.html]
```

**🔍 Explained:**

- **The baseline scan** is *passive*: it spiders the site and inspects responses without
  attacking. It's safe to run on every deploy. **Full scans** actively attack, so run them
  against dedicated test environments only.
- **`-I`** means don't fail on warnings (report-only mode). Remove it once the rules are tuned.
- **`chmod 777 zap`** is needed because the ZAP container runs as a non-root user that must
  write reports into the mounted folder.

**⚠️ Gotchas:**

- **Never run active DAST against production** without explicit approval. It can create junk
  data, trigger alerts, or knock over fragile endpoints.
- **Authenticated areas need a login script/context.** Otherwise ZAP only scans the login page.

---

## Scenario 51 — Reading secrets from a vault

**🎯 Goal:** The pipeline needs a third-party API key during deploy. Store it in **Azure Key
Vault** / **AWS Secrets Manager**, not in CI settings, so there's one source of truth with
rotation and auditing.

### GitHub Actions → Azure Key Vault

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
- name: Read secret from Key Vault
  id: kv
  run: |
    VALUE=$(az keyvault secret show --vault-name kv-orders-prod --name payment-api-key --query value -o tsv)
    echo "::add-mask::$VALUE"                  # mask BEFORE it could ever be printed
    echo "PAYMENT_API_KEY=$VALUE" >> "$GITHUB_ENV"
- run: ./scripts/configure-payment-webhook.sh   # reads $PAYMENT_API_KEY
```

### GitHub Actions → AWS Secrets Manager

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/github-orders-api-prod
    aws-region: eu-west-1
- uses: aws-actions/aws-secretsmanager-get-secrets@v2
  with:
    secret-ids: |
      PAYMENT,prod/orders/payment          # exposes env vars like PAYMENT_API_KEY from the JSON keys
    parse-json-secrets: true
```

### Azure DevOps — Key Vault task or a linked variable group

```yaml
steps:
  - task: AzureKeyVault@2
    inputs:
      azureSubscription: arm-orders-prod
      KeyVaultName: kv-orders-prod
      SecretsFilter: 'payment-api-key,db-password'   # only what's needed — not '*'
      RunAsPreJob: false
  - bash: ./scripts/configure-payment-webhook.sh
    env:
      PAYMENT_API_KEY: $(payment-api-key)            # secrets must be mapped explicitly
```

Alternatively: Library → Variable group → **"Link secrets from an Azure key vault as
variables"**, then reference the group in `variables:`.

### AWS CodeBuild

```yaml
env:
  secrets-manager:
    PAYMENT_API_KEY: prod/orders/payment:api_key
    DB_PASSWORD: prod/orders/db:password
```

**🔍 Explained:**

- **`::add-mask::`** tells GitHub to mask that value in all later log output. Do it
  immediately after reading.
- **`SecretsFilter`** downloads only the named secrets. `*` pulls every secret in the vault
  into the job, which is over-exposure.
- **CodeBuild's `secrets-manager:`** resolves secrets at build start using the project role.
  They're masked in logs automatically.

**⚠️ Gotchas:**

- **Better still: don't give the pipeline the app's secrets at all.** Let the **app** read
  Key Vault/Secrets Manager at runtime with its own managed identity / IAM role. The pipeline
  then never sees them.
- **Key Vault firewalls block hosted agents** (their IPs aren't fixed). Use private agents,
  allow-list the agent IP for the job's duration, or have the app read secrets instead.

---

## Scenario 52 — Hardening the pipeline itself

**🎯 Goal:** Stop the pipeline from becoming the easiest way into production.

### GitHub Actions hardening

```yaml
name: Hardened workflow
on:
  pull_request:

# 1. Default to NO permissions at workflow level; grant per job
permissions: {}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    timeout-minutes: 20
    steps:
      # 2. Pin third-party actions to a full commit SHA (tags can be moved by attackers)
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683   # v4.2.2
        with:
          persist-credentials: false     # 3. don't leave the token in .git/config

      # 4. Never interpolate untrusted input directly into scripts
      - name: Safe use of PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title: $PR_TITLE"
```

| Control | Where |
|---------|-------|
| `permissions: {}` default + per-job grants | Workflow YAML |
| Org setting "Workflow permissions: **Read repository contents**" by default | Org/repo settings |
| Pin actions to SHAs + Dependabot for `github-actions` | YAML + dependabot.yml |
| Restrict allowed actions (GitHub-owned + verified + allow-list) | Org settings → Actions |
| **CODEOWNERS** on `.github/workflows/` (platform team must review) | `.github/CODEOWNERS` |
| Environments with required reviewers + branch restrictions for deploys | Repo settings |
| Require approval for workflows from first-time/outside contributors | Repo settings → Actions |
| Avoid `pull_request_target` + checkout of PR head | YAML review |
| Self-hosted runners: ephemeral, never on public repos | Runner setup |

`.github/CODEOWNERS`:

```text
/.github/workflows/  @acme/platform-team
/infra/              @acme/platform-team
```

### Azure DevOps hardening

| Control | Where |
|---------|-------|
| **Limit job authorization scope** to the current project (and for released pipelines) | Project settings → Pipelines → Settings |
| **Protect access to repositories in YAML pipelines** | Project settings → Pipelines → Settings |
| Service connections: no "all pipelines" access; approvals and **Required template** check | Service connection → Security / Approvals and checks |
| Environments: approvals, **branch control** (`refs/heads/main`), business hours | Environment → Approvals and checks |
| Pipelines must **`extends`** a central secure template | Required template check |
| Disable "Allow override of variables at queue time" for sensitive variables | Pipeline settings |
| Secrets in Key Vault-linked variable groups, scoped to specific pipelines | Library |

Enforcing a central template with `extends`:

```yaml
# app repo: azure-pipelines.yml
resources:
  repositories:
    - repository: templates
      type: git
      name: Platform/pipeline-templates
      ref: refs/tags/v3.2.0              # pin the template version

extends:
  template: secure-pipeline.yml@templates
  parameters:
    buildSteps:
      - script: npm ci && npm test && npm run build
```

```yaml
# Platform/pipeline-templates: secure-pipeline.yml
parameters:
  - name: buildSteps
    type: stepList
    default: []

stages:
  - stage: Build
    jobs:
      - job: Build
        pool: { vmImage: ubuntu-latest }
        steps:
          - template: steps/secret-scan.yml        # mandatory, can't be removed by app teams
          - ${{ each step in parameters.buildSteps }}:
            - ${{ if not(contains(step.script, 'curl')) }}:   # example guard-rail
              - ${{ step }}
          - template: steps/sca-scan.yml
```

### AWS CodeBuild / CodePipeline hardening

| Control | How |
|---------|-----|
| Least-privilege service role per project (separate prod deploy project) | IAM (Scenario 45) |
| **Restrict webhook builds to trusted actors** (fork PRs run with your role otherwise!) | Webhook filter `ACTOR_ACCOUNT_ID` |
| Don't put secrets in plaintext env vars on the project | Use `secrets-manager` / `parameter-store` |
| Run builds inside a VPC with controlled egress for sensitive projects | Project VPC config |
| Encrypt artifacts with a customer-managed KMS key; lock down the artifact bucket | CodePipeline artifact store |
| Separate accounts for build/tooling vs prod (cross-account deploy roles) | AWS Organizations |
| CloudTrail + alerts on pipeline/project changes | CloudTrail, EventBridge |

Webhook filter so only org members' PRs trigger privileged builds:

```yaml
FilterGroups:
  - - Type: EVENT
      Pattern: PULL_REQUEST_CREATED,PULL_REQUEST_UPDATED
    - Type: ACTOR_ACCOUNT_ID
      Pattern: ^(1234567|2345678|3456789)$      # GitHub user IDs of trusted maintainers
```

**🔍 Explained:**

- **Why pin by SHA:** in real incidents (e.g. the 2025 `tj-actions/changed-files` compromise),
  attackers re-pointed popular action **tags** to malicious code that dumped CI secrets.
  SHA-pinned workflows weren't affected.
- **`persist-credentials: false`** stops later steps (or a compromised dependency) from reading
  the Git token out of `.git/config`.
- **`extends` + the Required template check** means production service connections can only be
  used by pipelines built from the platform team's vetted template.

**⚠️ Gotchas:**

- **Logs are public on public repos.** Anything printed, including a debug `env` dump, is visible
  to the world.
- **Caches and artifacts can be poisoned.** A PR workflow that writes a cache later read by a
  `main` deploy workflow is an attack path. GitHub scopes caches by branch for this reason.
  Don't undo that with custom cache sharing.

---

**Next:** [06 — Advanced Pipeline Patterns ➡️](06-advanced-patterns.md)
