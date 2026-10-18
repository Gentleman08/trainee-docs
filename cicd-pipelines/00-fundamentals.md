# 00 — CI/CD Fundamentals & Platform Anatomy (Scenarios 1–3)

> **Who this is for:** You've never written a pipeline, and you don't write application code.
> This chapter explains what a pipeline *is*. It walks through how GitHub Actions, Azure DevOps
> and AWS CodeBuild each describe one, and gives you a translation table between the three.

[⬅️ Back to Index](README.md)

---

## Table of Contents

- [0.1 What is CI/CD? (plain English)](#01-what-is-cicd)
- [0.2 The vocabulary you need](#02-the-vocabulary-you-need)
- [0.3 Anatomy: GitHub Actions](#03-anatomy-github-actions)
- [0.4 Anatomy: Azure DevOps Pipelines](#04-anatomy-azure-devops-pipelines)
- [0.5 Anatomy: AWS CodeBuild (buildspec) + CodePipeline](#05-anatomy-aws-codebuild-buildspec--codepipeline)
- [0.6 The Rosetta Stone — same concept, three syntaxes](#06-the-rosetta-stone)
- [0.7 YAML crash course (and its traps)](#07-yaml-crash-course)
- [0.8 How pipelines log in to clouds — secrets vs OIDC](#08-how-pipelines-log-in-to-clouds)
- [0.9 Scenario 1 — "Hello pipeline" on all three platforms](#scenario-1--hello-pipeline)
- [0.10 Scenario 2 — Triggers: when should a pipeline run?](#scenario-2--triggers)
- [0.11 Scenario 3 — Variables, secrets and passing data between steps](#scenario-3--variables-secrets-and-passing-data)
- [0.12 Universal pipeline best practices](#012-universal-pipeline-best-practices)

---

## 0.1 What is CI/CD?

Imagine a bakery:

- **Developers** write recipes (code) and keep them in a shared recipe book (**Git repository**).
- Every time someone changes a recipe, you want to **automatically** bake a test cake, taste
  it, and if it's good, deliver it to the shop.

That automation is **CI/CD**:

```
 Developer pushes code
        │
        ▼
 ┌──────────────── CI — Continuous Integration ────────────────┐
 │  1. Get the code (checkout)                                  │
 │  2. Install dependencies                                     │
 │  3. Build / compile                                          │
 │  4. Run tests, linting, security scans                       │
 │  5. Package an ARTIFACT (zip, jar, Docker image)             │
 └───────────────────────────┬──────────────────────────────────┘
                             ▼
 ┌──────────────── CD — Continuous Delivery / Deployment ──────┐
 │  6. Deploy artifact to DEV  → automated tests                │
 │  7. Deploy to STAGING       → more tests                     │
 │  8. (Approval)              → human clicks "Approve"         │
 │  9. Deploy to PRODUCTION                                     │
 └──────────────────────────────────────────────────────────────┘
```

- **Continuous Integration** — every change is built and tested automatically, so breakages
  are caught within minutes, not weeks.
- **Continuous Delivery** — every good build *can* be deployed to production with one click.
- **Continuous Deployment** — every good build *is* deployed to production automatically,
  with no human click.

A **pipeline** is the written-down list of those steps, stored as a **YAML file** in the
same Git repo as the code. That idea is called **"pipeline as code"**.

---

## 0.2 The vocabulary you need

| Term | Meaning | Analogy |
|------|---------|---------|
| **Pipeline / Workflow** | The whole automated process, defined in YAML | The full recipe card |
| **Trigger** | What starts the pipeline (push, pull request, schedule, manual click) | The doorbell |
| **Stage** | A big phase (Build, Deploy-Dev, Deploy-Prod) | A course in a meal |
| **Job** | A group of steps that run **on one machine** | One cook at one station |
| **Step / Task / Action** | A single command or pre-built action | One instruction: "whisk eggs" |
| **Runner / Agent / Build environment** | The machine (VM or container) that executes a job | The kitchen |
| **Hosted vs self-hosted** | Platform-provided throw-away VMs vs machines you manage | Rented kitchen vs your own |
| **Artifact** | The output file(s) of a build, passed to later jobs/stages | The packed cake box |
| **Environment** | A deployment target (dev/staging/prod) with optional approvals | The shop branch |
| **Secret** | A password/token stored encrypted, masked in logs | Safe-deposit key |
| **Service connection / credentials** | How the pipeline logs in to Azure/AWS/Kubernetes | A delivery van key |
| **Pull Request (PR)** | A request to merge a code change; pipelines validate it before merging | Asking the head chef to review your recipe change |
| **Main branch** | The "official" version of the code | The master recipe book |

### Key fact: each job starts on a fresh machine

```
Job A (VM #1)           Job B (VM #2)
├─ checkout             ├─ checkout          ← must checkout AGAIN
├─ npm install          ├─ ??? node_modules  ← NOT there! different machine
└─ build → dist/        └─ ??? dist/         ← NOT there! use artifacts
```

> ⚠️ **Gotcha #1 for beginners:** Files created in one job are **not** visible in another
> job. Pass them as **artifacts**, or put the steps in the same job.

---

## 0.3 Anatomy: GitHub Actions

- Files live in **`.github/workflows/*.yml`** (any name, any number of files).
- Structure: **workflow → jobs → steps**. Jobs run **in parallel** unless you use `needs:`.
- Steps either `run:` a shell command or `uses:` a pre-built **action** from the Marketplace
  (e.g. `actions/checkout@v4`).
- Runners: `ubuntu-latest`, `windows-latest`, `macos-latest` (GitHub-hosted), or self-hosted.

```yaml
name: CI                          # display name

on:                               # TRIGGERS
  push:
    branches: [main]
  pull_request:

permissions:                      # what the automatic GITHUB_TOKEN may do (least privilege)
  contents: read

env:                              # workflow-wide environment variables
  NODE_VERSION: "22"

jobs:
  build:                          # job ID (your choice)
    runs-on: ubuntu-latest        # which runner
    steps:
      - uses: actions/checkout@v4             # an ACTION
      - name: Say hello                       # a SHELL step
        run: echo "Building commit ${{ github.sha }}"

  deploy:
    needs: build                  # runs after "build" succeeds
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production       # approvals/secrets attached to this environment
    steps:
      - run: echo "Deploying..."
```

**Key syntax:**

| Syntax | Meaning |
|--------|---------|
| `${{ ... }}` | Expression, evaluated by GitHub **before** the step runs |
| `${{ github.sha }}` | Commit ID that triggered the run (`github` context) |
| `${{ secrets.MY_SECRET }}` | Encrypted secret (repo / org / environment level) |
| `${{ vars.MY_VAR }}` | Non-secret configuration variable |
| `${{ steps.<id>.outputs.<name> }}` | Output from an earlier step |
| `${{ needs.<job>.outputs.<name> }}` | Output from an earlier job |

---

## 0.4 Anatomy: Azure DevOps Pipelines

- A YAML file anywhere in the repo (convention: `azure-pipelines.yml` or `pipelines/*.yml`).
  You then **register** it in Azure DevOps → Pipelines → New pipeline.
- Structure: **pipeline → stages → jobs → steps**. Stages run **sequentially** by default.
  Jobs inside a stage run **in parallel** by default.
- Steps are `script:` / `bash:` / `pwsh:` commands or **tasks** (`task: DotNetCoreCLI@2`). The
  `@2` is the task's major version.
- Agents: Microsoft-hosted (`vmImage: ubuntu-latest`) or self-hosted **agent pools**.
- **Deployment jobs** target an **Environment**. Approvals and checks are configured on the
  Environment **in the web UI**, not in YAML.

```yaml
trigger:                          # CI trigger (push)
  branches:
    include: [main]

pr:                               # PR trigger (GitHub/Bitbucket repos; Azure Repos use branch policies)
  branches:
    include: [main]

pool:
  vmImage: ubuntu-latest          # Microsoft-hosted agent

variables:
  nodeVersion: '22.x'

stages:
  - stage: Build
    jobs:
      - job: BuildJob
        steps:
          - checkout: self                    # automatic in regular jobs; shown for clarity
          - script: echo "Building $(Build.SourceVersion)"
            displayName: Say hello

  - stage: Deploy
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProd                # a DEPLOYMENT job
        environment: production               # approvals configured on this environment
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo "Deploying..."
```

**Key syntax — three kinds of variable syntax (confusing at first!):**

| Syntax | When evaluated | Use for |
|--------|---------------|---------|
| `$(myVar)` | **Runtime**, just before the task runs (macro) | Most task inputs and scripts |
| `${{ variables.myVar }}` / `${{ parameters.x }}` | **Compile time**, when YAML is processed | Templates, conditions on structure, loops |
| `$[ variables.myVar ]` | **Runtime** expression | Conditions, `dependencies.*` outputs |

| Predefined variable | Meaning |
|---------------------|---------|
| `$(Build.SourceVersion)` | Commit ID |
| `$(Build.SourceBranch)` | e.g. `refs/heads/main` |
| `$(Build.BuildId)` | Unique run number |
| `$(Build.ArtifactStagingDirectory)` | Folder to stage files for publishing |
| `$(Pipeline.Workspace)` | Where downloaded artifacts land |
| `$(System.DefaultWorkingDirectory)` | Where the repo is checked out |

> ⚠️ **Gotcha:** In a `deployment` job, the repo is **not** checked out automatically.
> Pipeline artifacts **are** downloaded automatically. Add `- checkout: self` if you need
> repo files there.

---

## 0.5 Anatomy: AWS CodeBuild (buildspec) + CodePipeline

AWS splits CI/CD across services:

```
 ┌──────────────┐    ┌────────────────────┐    ┌───────────────────┐
 │ Source       │──► │ CodeBuild          │──► │ Deploy            │
 │ GitHub /     │    │ runs buildspec.yml │    │ CodeDeploy / ECS /│
 │ CodeCommit / │    │ (build + test)     │    │ CloudFormation /  │
 │ S3 / Bitbucket│   └────────────────────┘    │ another CodeBuild │
 └──────────────┘                              └───────────────────┘
 └──────────────────── orchestrated by CodePipeline ─────────────────┘
```

- **CodeBuild** — runs one build in a container, following **`buildspec.yml`** (by default at
  the repo root). One buildspec = roughly one **job**.
- **CodePipeline** — chains stages (Source → Build → Approve → Deploy). It's usually defined
  in the console, CloudFormation/CDK or Terraform, **not** in the repo YAML.
- The CodeBuild **project** (created once, in console/IaC) defines the build image, compute
  size, IAM role, VPC, **privileged mode** (needed for Docker builds) and the webhook triggers.

```yaml
version: 0.2                      # buildspec format version (always 0.2)

env:
  variables:                      # plain variables
    NODE_ENV: test
  parameter-store:                # pulled from SSM Parameter Store at build start
    API_URL: /myapp/dev/api_url
  secrets-manager:                # pulled from Secrets Manager (secret-id:json-key)
    NPM_TOKEN: prod/npm:token
  exported-variables:             # made available to later CodePipeline actions
    - IMAGE_TAG

phases:
  install:
    runtime-versions:             # choose language versions available on the build image
      nodejs: 20
    commands:
      - npm ci
  pre_build:
    commands:
      - echo "Commit $CODEBUILD_RESOLVED_SOURCE_VERSION"
  build:
    commands:
      - npm run build
      - npm test
  post_build:
    commands:
      - export IMAGE_TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)

reports:                          # test reports shown in the CodeBuild console
  unit-tests:
    files: ["junit.xml"]
    file-format: JUNITXML

artifacts:                        # output handed to the next pipeline stage / S3
  files:
    - "dist/**/*"

cache:
  paths:
    - "/root/.npm/**/*"
```

**Key facts:**

| Concept | How CodeBuild does it |
|---------|----------------------|
| Phases | `install` → `pre_build` → `build` → `post_build`. Each has `commands`, optional `finally`, optional `on-failure: ABORT \| CONTINUE` |
| Failure | Any command exiting non-zero fails that phase. If `build` fails, `post_build` **still runs** (check `$CODEBUILD_BUILD_SUCCEEDING`) |
| Shell | Each command runs in the same shell session (variables persist between commands, since buildspec 0.2) |
| Commit ID | `$CODEBUILD_RESOLVED_SOURCE_VERSION` |
| Build number | `$CODEBUILD_BUILD_NUMBER` |
| Source folder | `$CODEBUILD_SRC_DIR` |
| Webhook info | `$CODEBUILD_WEBHOOK_TRIGGER` (e.g. `branch/main`, `pr/42`), `$CODEBUILD_WEBHOOK_HEAD_REF` |
| Permissions | The project's **IAM service role** — no stored keys needed |

> ⚠️ **Gotcha:** `post_build` runs even after `build` fails. Guard deploy commands:
> `- if [ "$CODEBUILD_BUILD_SUCCEEDING" != "1" ]; then echo "build failed, skipping"; exit 1; fi`

> 💡 **Hybrid option:** CodeBuild can act as a **runner for GitHub Actions**
> (`runs-on: codebuild-<project>-${{ github.run_id }}-${{ github.run_attempt }}`). You write
> GitHub Actions YAML, but the jobs run inside your AWS account and VPC. See Chapter 06.

---

## 0.6 The Rosetta Stone

| Concept | GitHub Actions | Azure DevOps | AWS CodeBuild / CodePipeline |
|---------|---------------|--------------|------------------------------|
| File location | `.github/workflows/*.yml` | any `.yml`, registered in UI | `buildspec.yml` (+ pipeline in IaC/console) |
| Top-level unit | workflow | pipeline | pipeline (CodePipeline) |
| Phase | job (with `needs`) | stage | stage (CodePipeline) |
| Machine-level unit | job | job | build project run |
| Command | `run:` | `script:` / `bash:` / `pwsh:` | `commands:` list in a phase |
| Reusable unit | action / reusable workflow | task / template | shared buildspec file / CodeBuild project |
| Push trigger | `on: push` | `trigger:` | webhook filter group `PUSH` / CodePipeline source |
| PR trigger | `on: pull_request` | `pr:` or branch policy | webhook `PULL_REQUEST_CREATED/UPDATED` |
| Schedule | `on: schedule: - cron:` | `schedules: - cron:` | EventBridge rule |
| Manual run | `on: workflow_dispatch` | "Run pipeline" button + `parameters:` | "Start build" / "Release change" |
| Runner | `runs-on: ubuntu-latest` | `pool: vmImage: ubuntu-latest` | project environment image (`aws/codebuild/standard:7.0`) |
| Variable | `env:` / `vars.X` | `variables:` / variable groups | `env: variables:` |
| Secret | `secrets.X` | secret variables / Key Vault-linked group | `secrets-manager:` / `parameter-store:` |
| Commit ID | `${{ github.sha }}` | `$(Build.SourceVersion)` | `$CODEBUILD_RESOLVED_SOURCE_VERSION` |
| Branch | `${{ github.ref_name }}` | `$(Build.SourceBranchName)` | `$CODEBUILD_WEBHOOK_HEAD_REF` |
| Run number | `${{ github.run_number }}` | `$(Build.BuildId)` | `$CODEBUILD_BUILD_NUMBER` |
| Condition | `if:` | `condition:` | shell `if` / pipeline structure |
| Dependencies | `needs:` | `dependsOn:` | stage order / `build-graph` |
| Matrix | `strategy: matrix:` | `strategy: matrix:` | `batch: build-matrix:` |
| Artifacts | `upload-artifact` / `download-artifact` | `publish:` / `download:` | `artifacts:` section (S3) |
| Cache | `actions/cache` or setup-* `cache:` | `Cache@2` task | `cache: paths:` (S3 or local) |
| Test reports | third-party action / job summary | `PublishTestResults@2` | `reports:` section |
| Approvals | Environment protection rules | Environment approvals & checks | Manual approval action |
| Cloud auth | OIDC → `azure/login`, `configure-aws-credentials` | Service connection (workload identity) | IAM service role |

---

## 0.7 YAML crash course

YAML is the language all three use. It's **indentation-sensitive** (like Python).

```yaml
# A comment
name: my-app            # key: value (string)
replicas: 3             # number
enabled: true           # boolean
tags:                   # list (each item starts with "- ")
  - web
  - api
database:               # nested map
  host: db.internal
  port: 5432
script: |               # multi-line string, newlines KEPT
  echo "line 1"
  echo "line 2"
description: >          # multi-line string, newlines folded into spaces
  this becomes
  one line
```

### YAML traps that break pipelines

| Trap | Example | Problem | Fix |
|------|---------|---------|-----|
| Tabs | `<TAB>steps:` | YAML forbids tabs for indentation | Spaces only (configure your editor) |
| Wrong indent | step indented under the wrong key | "Unexpected value" / step silently ignored | Use an editor with YAML schema validation (VS Code + extensions) |
| The "Norway problem" | `country: NO` | Older YAML parsers read `NO`/`yes`/`on` as booleans | Quote: `"NO"` |
| Versions as numbers | `node-version: 22.10` → fine, but `python-version: 3.10` → **3.1** | Trailing zero dropped | Quote versions: `"3.10"` |
| Colons in strings | `run: echo key: value` | Parsed as a map | Quote or use `|` block |
| `on:` in GitHub | — | Some generic YAML linters treat `on` as `true` | Harmless in GitHub; ignore the linter warning |
| `*` and `&` at start | `files: *.zip` | YAML alias/anchor syntax | Quote: `"*.zip"` |

---

## 0.8 How pipelines log in to clouds

To deploy to Azure or AWS, the pipeline must authenticate. There are two generations of doing this.

### ❌ Old way: long-lived secrets

Create an Azure **client secret** or AWS **access key**, paste it into the pipeline's secrets.
Problems: it can leak, it expires (and breaks deploys at 2 a.m.), and it needs manual rotation.

### ✅ Modern way: OIDC / workload identity federation (no stored secret)

```
 ┌─────────────┐  1. "I am repo acme/api, branch main"  ┌──────────────────┐
 │  Pipeline   │ ─────── signed token (JWT) ──────────►  │ Azure Entra ID / │
 │  run        │                                         │ AWS IAM          │
 │             │ ◄────── 2. short-lived cloud token ──── │ (trusts GitHub/  │
 └─────────────┘         (valid ~1 hour)                 │  ADO as issuer)  │
                                                         └──────────────────┘
```

- The CI platform issues a **signed identity token** for each run.
- The cloud is configured once to **trust** tokens from that platform **for a specific
  repo/branch/environment**, and swaps them for short-lived credentials.
- **Nothing to leak, nothing to rotate.**

| Platform | How |
|----------|-----|
| GitHub Actions → Azure | Entra app + **federated credential** (subject `repo:org/repo:environment:prod`); `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id`; job needs `permissions: id-token: write` |
| GitHub Actions → AWS | IAM **OIDC identity provider** `token.actions.githubusercontent.com` + IAM role with trust policy; `aws-actions/configure-aws-credentials@v4` with `role-to-assume` |
| Azure DevOps → Azure | Azure Resource Manager **service connection** using **Workload identity federation** (the default for new connections) |
| Azure DevOps → AWS | AWS Toolkit service connection (supports OIDC role assumption) |
| AWS CodeBuild → AWS | Nothing to do — the build runs **as its IAM service role** |

Full setup walkthroughs are in [Chapter 05 — DevSecOps](05-devsecops.md).

---

## Scenario 1 — "Hello pipeline"

**🎯 Goal:** The smallest working pipeline on each platform. It checks out the code, prints
some information and runs a script from the repo.

Repo contents:

```
my-repo/
├── scripts/hello.sh        ← #!/bin/bash  echo "Hello from $1"
└── (pipeline file)
```

### GitHub Actions — `.github/workflows/hello.yml`

```yaml
name: Hello
on:
  push:
  workflow_dispatch:        # adds a "Run workflow" button in the Actions tab

jobs:
  hello:
    runs-on: ubuntu-latest
    steps:
      - name: Get the code
        uses: actions/checkout@v4

      - name: Show context
        run: |
          echo "Repo:   ${{ github.repository }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "Commit: ${{ github.sha }}"
          echo "Actor:  ${{ github.actor }}"

      - name: Run repo script
        run: |
          chmod +x scripts/hello.sh
          ./scripts/hello.sh "GitHub Actions"
```

### Azure DevOps — `azure-pipelines.yml`

```yaml
trigger:
  - '*'                     # any branch

pool:
  vmImage: ubuntu-latest

steps:
  - checkout: self

  - script: |
      echo "Repo:   $(Build.Repository.Name)"
      echo "Branch: $(Build.SourceBranchName)"
      echo "Commit: $(Build.SourceVersion)"
      echo "Who:    $(Build.RequestedFor)"
    displayName: Show context

  - bash: |
      chmod +x scripts/hello.sh
      ./scripts/hello.sh "Azure DevOps"
    displayName: Run repo script
```

### AWS CodeBuild — `buildspec.yml`

```yaml
version: 0.2

phases:
  build:
    commands:
      - echo "Source dir  $CODEBUILD_SRC_DIR"
      - echo "Commit      $CODEBUILD_RESOLVED_SOURCE_VERSION"
      - echo "Trigger     $CODEBUILD_WEBHOOK_TRIGGER"
      - echo "Build no.   $CODEBUILD_BUILD_NUMBER"
      - chmod +x scripts/hello.sh
      - ./scripts/hello.sh "AWS CodeBuild"
```

**🔍 Explained:**

- **GitHub:** `actions/checkout@v4` is required. Without it, the runner's folder is empty.
- **Azure DevOps:** the checkout happens automatically in normal jobs. A single-job pipeline can
  skip `stages:`/`jobs:` and put `steps:` directly at the top level.
- **CodeBuild:** the source is already downloaded into `$CODEBUILD_SRC_DIR` before the
  buildspec runs. There's no checkout step.

**⚠️ Gotchas:**

- `Permission denied` running `./scripts/hello.sh` happens when the execute bit was lost
  (common when committing from Windows). Either `chmod +x` in the pipeline, or fix it in Git
  with `git update-index --chmod=+x scripts/hello.sh`.
- CRLF line endings in scripts cause `/bin/bash^M: bad interpreter`. Add
  `*.sh text eol=lf` to `.gitattributes`.

---

## Scenario 2 — Triggers

**🎯 Goal:** Control **when** pipelines run:

- on pushes to `main` and `release/*`,
- on PRs into `main`,
- but **not** when only docs change,
- plus a nightly run and a manual button.

### GitHub Actions

```yaml
on:
  push:
    branches: [main, "release/**"]
    tags: ["v*"]                    # also run for version tags like v1.2.3
    paths-ignore:
      - "docs/**"
      - "**/*.md"
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
    paths-ignore:
      - "docs/**"
      - "**/*.md"
  schedule:
    - cron: "30 1 * * 1-5"          # 01:30 UTC, Monday–Friday
  workflow_dispatch:                # manual
```

### Azure DevOps

```yaml
trigger:
  batch: true                       # if many pushes arrive while running, queue ONE run for all of them
  branches:
    include: [main, release/*]
  tags:
    include: [v*]
  paths:
    exclude: [docs/*, '*.md']

pr:                                 # GitHub/Bitbucket-hosted repos only
  branches:
    include: [main]
  paths:
    exclude: [docs/*]

schedules:
  - cron: "30 1 * * 1-5"            # UTC
    displayName: Nightly
    branches:
      include: [main]
    always: false                   # skip if nothing changed since the last scheduled run
```

> For **Azure Repos Git**, PR builds are configured with a **branch policy** (Repos →
> Branches → main → Branch policies → Build validation), not with `pr:`.

### AWS CodeBuild

Triggers are **not** in the buildspec. They're set on the CodeBuild project's webhook
(console or IaC). Here they are in CloudFormation:

```yaml
MyBuildProject:
  Type: AWS::CodeBuild::Project
  Properties:
    # ... source, environment, service role ...
    Triggers:
      Webhook: true
      FilterGroups:
        - - Type: EVENT
            Pattern: PUSH
          - Type: HEAD_REF
            Pattern: ^refs/heads/(main|release/.*)$
          - Type: FILE_PATH
            Pattern: ^docs/.*
            ExcludeMatchedPattern: true
        - - Type: EVENT
            Pattern: PULL_REQUEST_CREATED,PULL_REQUEST_UPDATED,PULL_REQUEST_REOPENED
          - Type: BASE_REF
            Pattern: ^refs/heads/main$
```

The nightly schedule uses an **EventBridge** rule that starts the build:

```yaml
NightlyRule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: "cron(30 1 ? * MON-FRI *)"   # AWS cron has 6 fields and uses '?'
    Targets:
      - Arn: !GetAtt MyBuildProject.Arn
        Id: nightly-build
        RoleArn: !GetAtt EventsInvokeCodeBuildRole.Arn
```

**🔍 Explained:**

- Each **filter group** is a list of conditions that are **AND**-ed together. Separate groups
  are **OR**-ed.
- `cron` uses 5 fields on GitHub and ADO (`minute hour day month weekday`). AWS uses 6 fields
  and requires `?` in day-of-month or day-of-week.

**⚠️ Gotchas:**

- **All schedules are UTC.** "Run at 9 a.m." in India (UTC+5:30) means `30 3 * * *`.
- **GitHub schedules only run on the default branch.** They can be delayed under load, and
  they're **disabled automatically after 60 days** of no repo activity in public repos.
- **Path filters and required checks don't mix well.** If a required status check is skipped
  because of `paths-ignore`, the PR waits **forever** for that check. Either don't make
  path-filtered workflows required, or use a job-level filter (Chapter 01, Scenario 11).
- **PRs from forks:** GitHub doesn't give secrets to `pull_request` runs from forks. That's
  intentional, for security.

---

## Scenario 3 — Variables, secrets and passing data

**🎯 Goal:** Use plain config variables and secrets. Then **compute a value in one step**
(an image tag) and use it in a later step **and** a later job.

### GitHub Actions

```yaml
name: Vars demo
on: workflow_dispatch

env:
  APP_NAME: orders-api                    # workflow-level, plain

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.tag.outputs.image_tag }}   # expose step output as JOB output
    steps:
      - uses: actions/checkout@v4
      - id: tag
        name: Compute tag
        run: echo "image_tag=$(date -u +%Y%m%d)-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"

      - name: Use it in the same job
        run: echo "Tag is ${{ steps.tag.outputs.image_tag }}"

      - name: Use a secret (masked in logs)
        env:
          API_KEY: ${{ secrets.THIRD_PARTY_API_KEY }}   # map secret → env var for this step only
        run: ./scripts/call-api.sh                       # script reads $API_KEY

  build:
    needs: prepare
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building ${APP_NAME}:${{ needs.prepare.outputs.image_tag }}"
```

### Azure DevOps

```yaml
trigger: none

variables:
  - name: appName
    value: orders-api
  - group: orders-api-secrets            # Library → Variable group (can be linked to Key Vault)

stages:
  - stage: Prepare
    jobs:
      - job: Tag
        pool: { vmImage: ubuntu-latest }
        steps:
          - bash: |
              TAG="$(date -u +%Y%m%d)-$(echo $(Build.SourceVersion) | cut -c1-7)"
              echo "##vso[task.setvariable variable=imageTag;isOutput=true]$TAG"
            name: setTag                 # 'name' (not displayName) is needed to reference outputs

          - bash: echo "Tag is $(setTag.imageTag)"

          - bash: ./scripts/call-api.sh
            env:
              API_KEY: $(ThirdPartyApiKey)   # secrets are NOT auto-exposed as env vars; map explicitly

  - stage: Build
    dependsOn: Prepare
    variables:
      # Cross-STAGE output syntax: stageDependencies.<stage>.<job>.outputs['<step>.<var>']
      imageTag: $[ stageDependencies.Prepare.Tag.outputs['setTag.imageTag'] ]
    jobs:
      - job: Build
        pool: { vmImage: ubuntu-latest }
        steps:
          - bash: echo "Building $(appName):$(imageTag)"
```

### AWS CodeBuild

```yaml
version: 0.2

env:
  variables:
    APP_NAME: orders-api
  secrets-manager:
    API_KEY: orders-api/third-party:api_key     # <secret-name>:<json-key>
  parameter-store:
    LOG_LEVEL: /orders-api/dev/log_level
  exported-variables:
    - IMAGE_TAG                                  # visible to later CodePipeline actions

phases:
  pre_build:
    commands:
      - IMAGE_TAG="$(date -u +%Y%m%d)-$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)"
      - export IMAGE_TAG
  build:
    commands:
      - echo "Building ${APP_NAME}:${IMAGE_TAG}"    # variables persist across phases
      - ./scripts/call-api.sh                       # $API_KEY already in the environment
```

In **CodePipeline**, a later action reads the exported variable through the action's
**namespace**, e.g. `#{BuildVariables.IMAGE_TAG}`. The Build action must have
`Namespace: BuildVariables` set.

**🔍 Explained:**

- **GitHub:** a step writes `name=value` to the file `$GITHUB_OUTPUT`. A step `id` makes it
  addressable, and job `outputs:` pass it on to other jobs.
- **Azure DevOps:** the `##vso[task.setvariable ...]` "logging command" printed to the log
  sets a variable. `isOutput=true` plus the step `name:` make it readable from other jobs
  (`dependencies.Job.outputs['step.var']`) or stages (`stageDependencies...`).
- **CodeBuild:** env vars persist across phases in the same build. `exported-variables`
  hands values to CodePipeline.
- `${GITHUB_SHA::7}` is bash substring syntax: the first 7 characters.

**⚠️ Gotchas:**

- **Secrets are masked in logs, but only as exact strings.** If a script base64-encodes or
  splits a secret, the transformed value is **printed in clear text**. Never `echo` secrets.
- **Azure DevOps secret variables aren't automatically env vars.** You must map them with
  `env:`. Forgetting this is the #1 "my script sees an empty password" issue.
- **GitHub masks job outputs that contain secrets,** so the output arrives empty in the next
  job. Pass a reference (e.g. a secret name) instead of the secret itself.
- **Expression timing in ADO:** `${{ }}` is evaluated at compile time, so it **can't see**
  variables set by earlier steps. Use `$( )` or `$[ ]` for those.

---

## 0.12 Universal pipeline best practices

| # | Practice | Why |
|---|----------|-----|
| 1 | **Pipeline as code** — the YAML lives in the repo and changes go through PRs | Reviewable, versioned, reproducible |
| 2 | **Fail fast** — lint and unit tests first, slow things later | Developers get feedback in minutes |
| 3 | **Build once, deploy many** — the *same* artifact goes to dev → staging → prod | What you tested is what you ship |
| 4 | **Pin versions** of actions/tasks/tools/images | Upstream changes can't break or compromise you |
| 5 | **Least privilege** — minimal token permissions, scoped cloud roles | Limits the damage from a compromised pipeline |
| 6 | **No long-lived secrets** — OIDC / workload identity | Nothing to leak or rotate |
| 7 | **Cache dependencies** | Faster and cheaper runs |
| 8 | **Protect production** — environments with approvals, branch restrictions | Nobody deploys to prod from a random branch |
| 9 | **Make pipelines idempotent** — re-running is safe | Retries don't break things |
| 10 | **Fast rollback path** — keep previous artifacts, documented redeploy | Incidents get resolved in minutes |
| 11 | **Observable** — test reports, job summaries, notifications | People know what broke and why |
| 12 | **Keep logic in scripts/Makefiles, not giant YAML** | Testable locally, portable between CI platforms |

> 💡 Practice #12 is what makes migrating between GitHub, Azure DevOps and AWS easy. If the
> YAML just calls `make test` and `make build`, only the thin wrapper changes.

---

**Next:** [01 — CI: Build & Test Scenarios ➡️](01-ci-build-test.md)
