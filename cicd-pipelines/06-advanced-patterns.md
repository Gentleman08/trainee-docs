# 06 — Advanced Pipeline Patterns (Scenarios 53–64)

[⬅️ Back to Index](README.md) · [⬅️ Previous: DevSecOps](05-devsecops.md)

---

> Once you have 5, then 50, then 500 pipelines, copy-paste stops scaling. This chapter covers
> reuse, control flow, releases, cross-pipeline orchestration, runners, notifications and
> housekeeping.

## Table of Contents

| # | Scenario | Key idea |
|---|----------|----------|
| 53 | [Reusable pipelines: reusable workflows / templates / shared buildspecs](#scenario-53--reusable-pipelines) | DRY at pipeline level |
| 54 | [Reusable steps: composite actions / step templates / shared scripts](#scenario-54--reusable-steps) | DRY at step level |
| 55 | [Manual runs with inputs](#scenario-55--manual-runs-with-inputs) | Parameters & dropdowns |
| 56 | [Concurrency: cancel outdated runs, serialise deploys](#scenario-56--concurrency-control) | No overlapping deploys |
| 57 | [Dynamic matrix & conditional logic](#scenario-57--dynamic-matrix-and-conditional-logic) | Generate jobs at runtime |
| 58 | [Release automation: tags, versions, changelogs](#scenario-58--release-automation) | Semantic versioning |
| 59 | [Cross-repo & cross-pipeline triggers](#scenario-59--cross-repo-and-cross-pipeline-triggers) | Pipeline chaining |
| 60 | [Self-hosted runners & agents](#scenario-60--self-hosted-runners-and-agents) | Private networks, custom tools |
| 61 | [Notifications to Slack / Teams](#scenario-61--notifications) | Alert on failure |
| 62 | [Hotfix flow](#scenario-62--hotfix-flow) | Fast, safe emergency fixes |
| 63 | [Scheduled housekeeping: clean old images & artifacts](#scenario-63--scheduled-housekeeping) | Cost control |
| 64 | [Write once, run anywhere: portable pipelines with a Makefile](#scenario-64--portable-pipelines-with-a-makefile) | Easy CI migration |

---

## Scenario 53 — Reusable pipelines

**🎯 Goal:** 40 microservices all need the same "build → test → scan → push image" pipeline.
Define it **once** in a central repo, and let every service call it with a few parameters.

### GitHub Actions — reusable workflow (`workflow_call`)

Central repo `acme/ci-templates`, file `.github/workflows/docker-service.yml`:

```yaml
name: Docker service CI (reusable)
on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string
      node-version:
        required: false
        type: string
        default: "22"
      run-e2e:
        required: false
        type: boolean
        default: false
    secrets:
      SONAR_TOKEN:
        required: false
    outputs:
      image-digest:
        description: Digest of the pushed image
        value: ${{ jobs.image.outputs.digest }}

permissions:
  contents: read
  packages: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci && npm run lint && npm test
      - if: ${{ inputs.run-e2e }}
        run: npm run test:e2e

  image:
    needs: test
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: push
        uses: docker/build-push-action@v6
        with:
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository_owner }}/${{ inputs.image-name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

Each service's workflow becomes ~15 lines:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    uses: acme/ci-templates/.github/workflows/docker-service.yml@v2   # pin a tag (or SHA)
    with:
      image-name: orders-api
      run-e2e: true
    secrets: inherit
    permissions:
      contents: read
      packages: write

  after:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - run: echo "Pushed digest ${{ needs.ci.outputs.image-digest }}"
```

### Azure DevOps — templates (step / job / stage) with typed parameters

Central repo `Platform/pipeline-templates`, file `stages/docker-service.yml`:

```yaml
parameters:
  - name: imageName
    type: string
  - name: nodeVersion
    type: string
    default: '22.x'
  - name: runE2E
    type: boolean
    default: false
  - name: acrConnection
    type: string
    default: acr-acme-prod

stages:
  - stage: Test
    jobs:
      - job: Test
        pool: { vmImage: ubuntu-latest }
        steps:
          - task: UseNode@1
            inputs: { version: '${{ parameters.nodeVersion }}' }
          - script: npm ci && npm run lint && npm test
          - ${{ if eq(parameters.runE2E, true) }}:      # compile-time conditional insertion
            - script: npm run test:e2e

  - stage: Image
    dependsOn: Test
    jobs:
      - job: Image
        pool: { vmImage: ubuntu-latest }
        steps:
          - task: Docker@2
            inputs:
              command: buildAndPush
              containerRegistry: ${{ parameters.acrConnection }}
              repository: ${{ parameters.imageName }}
              tags: $(Build.SourceVersion)
```

Service pipeline:

```yaml
trigger: [main]

resources:
  repositories:
    - repository: templates
      type: git
      name: Platform/pipeline-templates
      ref: refs/tags/v2.1.0

stages:
  - template: stages/docker-service.yml@templates
    parameters:
      imageName: orders-api
      runE2E: true
```

### AWS CodeBuild — shared buildspec + shared scripts as a secondary source

The CodeBuild project references a buildspec **from a central repo**: a secondary source named
`templates`, with the buildspec path set in the project:

```yaml
# CloudFormation for each service's project — only parameters differ
OrdersApiBuild:
  Type: AWS::CodeBuild::Project
  Properties:
    Name: orders-api-ci
    Source:
      Type: GITHUB
      Location: https://github.com/acme/orders-api.git
      BuildSpec: templates/buildspecs/docker-service.yml     # path inside the secondary source
    SecondarySources:
      - Type: GITHUB
        Location: https://github.com/acme/ci-templates.git
        SourceIdentifier: templates
    SecondarySourceVersions:
      - SourceIdentifier: templates
        SourceVersion: refs/tags/v2.1.0
    Environment:
      Type: LINUX_CONTAINER
      ComputeType: BUILD_GENERAL1_MEDIUM
      Image: aws/codebuild/standard:7.0
      PrivilegedMode: true
      EnvironmentVariables:
        - { Name: IMAGE_NAME, Value: orders-api }
        - { Name: RUN_E2E, Value: "true" }
    # ServiceRole, Artifacts, Triggers ...
```

`ci-templates/buildspecs/docker-service.yml`:

```yaml
version: 0.2
phases:
  install:
    runtime-versions: { nodejs: 20 }
  build:
    commands:
      - cd "$CODEBUILD_SRC_DIR"                         # primary source = the service repo
      - npm ci && npm run lint && npm test
      - if [ "$RUN_E2E" = "true" ]; then npm run test:e2e; fi
      - bash "$CODEBUILD_SRC_DIR_templates/scripts/docker-build-push.sh" "$IMAGE_NAME"
```

**🔍 Explained:**

- **GitHub reusable workflows** are whole workflows with `on: workflow_call`, typed `inputs`,
  `secrets` and `outputs`. The caller uses them at **job** level (`uses:` instead of `runs-on:`).
- **ADO templates** come in step, job, stage and variable flavours, plus `extends` templates.
  Parameters are typed (`string`, `boolean`, `number`, `object`, `stepList`, …) and expanded at
  **compile time**.
- **CodeBuild:** each secondary source is available at `$CODEBUILD_SRC_DIR_<identifier>`.

**⚠️ Gotchas:**

- **Pin template versions** (`@v2`, `ref: refs/tags/v2.1.0`). Otherwise a change to the central
  template breaks 40 pipelines at once, or silently changes production deploys.
- **GitHub limits:** there's a cap on how deeply reusable workflows can nest and how many one
  workflow can call. Check the current numbers in GitHub's docs before designing deep
  hierarchies. Also, `env:` set in the caller is **not** passed into the called workflow. Use
  `inputs`.
- **Private reusable workflows** must be shared explicitly: repo Settings → Actions → Access →
  "Accessible from repositories in the organization".

---

## Scenario 54 — Reusable steps

**🎯 Goal:** Five steps ("install tools, log in, set up cache") repeat in every job. Package
them as one reusable step.

### GitHub Actions — composite action

`.github/actions/setup-node-project/action.yml` (in the same repo, or a shared one):

```yaml
name: Setup Node project
description: Checkout-independent Node setup with cache and install
inputs:
  node-version:
    description: Node.js version
    default: "22"
  working-directory:
    description: Folder containing package.json
    default: "."
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
        cache-dependency-path: ${{ inputs.working-directory }}/package-lock.json
    - name: Install
      shell: bash                         # REQUIRED for run steps in composite actions
      working-directory: ${{ inputs.working-directory }}
      run: npm ci
```

Use it:

```yaml
steps:
  - uses: actions/checkout@v4
  - uses: ./.github/actions/setup-node-project
    with:
      working-directory: services/api
  - run: npm test
    working-directory: services/api
```

### Azure DevOps — step template

`steps/setup-node-project.yml`:

```yaml
parameters:
  - name: nodeVersion
    default: '22.x'
  - name: workingDirectory
    default: '$(System.DefaultWorkingDirectory)'

steps:
  - task: UseNode@1
    inputs: { version: '${{ parameters.nodeVersion }}' }
  - task: Cache@2
    inputs:
      key: 'npm | "$(Agent.OS)" | ${{ parameters.workingDirectory }}/package-lock.json'
      path: $(Pipeline.Workspace)/.npm
  - script: npm ci --cache $(Pipeline.Workspace)/.npm
    workingDirectory: ${{ parameters.workingDirectory }}
    displayName: npm ci
```

Use it:

```yaml
steps:
  - template: steps/setup-node-project.yml
    parameters:
      workingDirectory: services/api
  - script: npm test
    workingDirectory: services/api
```

### AWS CodeBuild — shared shell scripts

CodeBuild has no step-level reuse construct. Put reusable logic in **scripts** (versioned in a
shared repo or baked into a **custom build image**) and call them:

```yaml
phases:
  install:
    commands:
      - bash "$CODEBUILD_SRC_DIR_templates/scripts/setup-node-project.sh" services/api
```

**⚠️ Gotchas:**

- **Composite actions don't support `if:` on the action as a whole,** or `secrets` (pass them as
  inputs), and every `run` step needs an explicit `shell:`.
- **Custom CodeBuild images** speed builds up (tools preinstalled), but **you** must patch them.
  Rebuild them on a schedule.

---

## Scenario 55 — Manual runs with inputs

**🎯 Goal:** Give on-call engineers a "Run" button that asks which environment, which version,
and whether to run migrations.

### GitHub Actions — `workflow_dispatch` inputs

```yaml
name: Manual deploy
on:
  workflow_dispatch:
    inputs:
      environment:
        description: Target environment
        type: choice
        options: [dev, staging, production]
        required: true
      version:
        description: Image tag (git SHA)
        type: string
        required: true
      run_migrations:
        description: Run DB migrations first?
        type: boolean
        default: false
      log_level:
        type: choice
        options: [info, debug]
        default: info

run-name: Deploy ${{ inputs.version }} to ${{ inputs.environment }} by @${{ github.actor }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - if: ${{ inputs.run_migrations }}
        run: ./scripts/migrate.sh "${{ inputs.environment }}"
      - name: Deploy
        env:
          VERSION: ${{ inputs.version }}
          TARGET: ${{ inputs.environment }}
        run: ./scripts/deploy.sh "$TARGET" "$VERSION"
```

Trigger from the CLI too:

```bash
gh workflow run "Manual deploy" -f environment=staging -f version=3f2c1ab -f run_migrations=true
```

### Azure DevOps — runtime parameters

```yaml
parameters:
  - name: environment
    displayName: Target environment
    type: string
    default: dev
    values: [dev, staging, prod]
  - name: version
    displayName: Image tag
    type: string
  - name: runMigrations
    displayName: Run DB migrations first?
    type: boolean
    default: false

trigger: none

name: Deploy ${{ parameters.version }} to ${{ parameters.environment }}   # run name

stages:
  - stage: Deploy
    jobs:
      - deployment: Deploy
        environment: orders-${{ parameters.environment }}
        pool: { vmImage: ubuntu-latest }
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self
                - ${{ if parameters.runMigrations }}:
                  - script: ./scripts/migrate.sh ${{ parameters.environment }}
                - script: ./scripts/deploy.sh ${{ parameters.environment }} ${{ parameters.version }}
```

### AWS — start a build with overrides, or a CodePipeline V2 with variables

```bash
# CodeBuild: override environment variables for one run
aws codebuild start-build --project-name orders-deploy \
  --environment-variables-override \
    name=TARGET_ENV,value=staging,type=PLAINTEXT \
    name=VERSION,value=3f2c1ab,type=PLAINTEXT \
    name=RUN_MIGRATIONS,value=true,type=PLAINTEXT

# CodePipeline V2: pipeline-level variables
aws codepipeline start-pipeline-execution --name orders-deploy \
  --variables name=TargetEnv,value=staging name=Version,value=3f2c1ab
```

In a V2 pipeline definition, declare the variables and reference them as
`#{variables.TargetEnv}` in action configuration.

**🔍 Explained:**

- **`run-name` / `name`** gives each run a descriptive title, which makes the history readable
  at a glance.
- **`type: choice` / `values:`** gives a dropdown. Users can't type `prdo` by mistake.
- **ADO `${{ if parameters.x }}`** inserts or removes steps at compile time, so skipped steps
  don't even appear in the run.

**⚠️ Gotchas:**

- **GitHub `workflow_dispatch` only appears once the workflow file is on the default branch.**
- **Inputs are untrusted text.** Pass them via `env:` (as above) to avoid script injection,
  even for internal users.

---

## Scenario 56 — Concurrency control

**🎯 Goal:**

1. When a developer pushes 3 commits quickly to a PR, cancel the 2 outdated CI runs.
2. **Never** run two deploys to the same environment at the same time.

### GitHub Actions — `concurrency`

```yaml
name: CI
on: [push, pull_request]

# 1. One run per branch/PR; a newer push cancels the older run
concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo testing

  deploy:
    if: github.ref == 'refs/heads/main'
    needs: test
    runs-on: ubuntu-latest
    # 2. Deploys queue up; NEVER cancel a deploy halfway
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    steps:
      - run: echo deploying
```

### Azure DevOps — batching + exclusive lock

```yaml
trigger:
  batch: true                          # pushes during a run are batched into ONE next run
  branches: { include: [main] }

lockBehavior: sequential              # or runLatest: skip queued older runs, deploy only the newest

stages:
  - stage: Deploy
    jobs:
      - deployment: Deploy
        environment: orders-prod       # add an "Exclusive lock" check on this environment
        strategy:
          runOnce:
            deploy:
              steps:
                - script: ./scripts/deploy.sh
```

> Environment → Approvals and checks → **Exclusive lock**: only one run at a time can hold the
> environment. `lockBehavior: runLatest` makes waiting runs give way to the newest one.

### AWS

- **CodePipeline V2 execution mode:**
  - `SUPERSEDED` (default): a newer execution replaces an older one waiting at a stage.
  - `QUEUED`: one at a time, in order.
  - `PARALLEL`: independent executions.

```yaml
OrdersPipeline:
  Type: AWS::CodePipeline::Pipeline
  Properties:
    PipelineType: V2
    ExecutionMode: QUEUED
```

- **CodeBuild:** set the project's **concurrent build limit** (e.g. `ConcurrentBuildLimit: 1`
  for a deploy project) so extra builds wait or fail instead of overlapping.

**⚠️ Gotchas:**

- **`cancel-in-progress: true` on a deploy job** can kill Terraform/Helm halfway, leaving locks
  and half-applied changes. Cancel CI, queue deploys.
- **GitHub concurrency groups keep at most one *pending* run per group.** A third run replaces
  the pending second one. That's usually what you want for deploys (newest wins).

---

## Scenario 57 — Dynamic matrix and conditional logic

**🎯 Goal:** Discover at runtime which services exist (or changed), then fan out one job per service.

### GitHub Actions — matrix from a previous job's JSON output

```yaml
jobs:
  discover:
    runs-on: ubuntu-latest
    outputs:
      services: ${{ steps.find.outputs.services }}
    steps:
      - uses: actions/checkout@v4
      - id: find
        run: |
          # every folder under services/ that contains a Dockerfile
          SERVICES=$(find services -maxdepth 2 -name Dockerfile -printf '%h\n' | xargs -n1 basename | jq -R . | jq -sc .)
          echo "services=$SERVICES" >> "$GITHUB_OUTPUT"     # e.g. ["api","web","worker"]

  build:
    needs: discover
    if: needs.discover.outputs.services != '[]'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: ${{ fromJSON(needs.discover.outputs.services) }}
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ${{ matrix.service }} services/${{ matrix.service }}
```

**Common conditional expressions:**

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
if: startsWith(github.ref, 'refs/tags/v')
if: contains(github.event.pull_request.labels.*.name, 'run-e2e')     # opt-in via PR label
if: failure()                                                         # only when an earlier step failed
if: always()                                                          # run no matter what
if: ${{ !cancelled() }}                                               # run unless the run was cancelled
```

### Azure DevOps — compile-time loop and runtime matrix

```yaml
# Compile-time loop over a parameter list
parameters:
  - name: services
    type: object
    default: [api, web, worker]

jobs:
  - ${{ each svc in parameters.services }}:
    - job: build_${{ svc }}
      pool: { vmImage: ubuntu-latest }
      steps:
        - script: docker build -t ${{ svc }} services/${{ svc }}
```

```yaml
# Runtime matrix generated by a previous job
jobs:
  - job: Discover
    pool: { vmImage: ubuntu-latest }
    steps:
      - bash: |
          MATRIX=$(find services -maxdepth 2 -name Dockerfile -printf '%h\n' | xargs -n1 basename \
            | jq -R '{(.): {service: .}}' | jq -sc add)
          echo "##vso[task.setvariable variable=matrix;isOutput=true]$MATRIX"
        name: set
  - job: Build
    dependsOn: Discover
    pool: { vmImage: ubuntu-latest }
    strategy:
      matrix: $[ dependencies.Discover.outputs['set.matrix'] ]
    steps:
      - script: docker build -t $(service) services/$(service)
```

**Common conditions:**

```yaml
condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
condition: startsWith(variables['Build.SourceBranch'], 'refs/tags/v')
condition: eq(variables['Build.Reason'], 'PullRequest')
condition: failed()
condition: always()
```

### AWS CodeBuild — batch `build-list`

```yaml
version: 0.2
batch:
  build-list:
    - identifier: api
      env:
        variables: { SERVICE: api }
    - identifier: web
      env:
        variables: { SERVICE: web }
    - identifier: worker
      env:
        variables: { SERVICE: worker }
      ignore-failure: true            # worker failing doesn't fail the batch
phases:
  build:
    commands:
      - docker build -t "$SERVICE" "services/$SERVICE"
```

**⚠️ Gotchas:**

- **An empty matrix (`[]`) fails the GitHub job** with "matrix must define at least one
  vector". Guard it with the `if:` shown above.
- **ADO:** the runtime matrix JSON must be an **object of objects**
  (`{"api":{"service":"api"}}`), not a list.
- **GitHub matrix limit:** 256 jobs per workflow run.

---

## Scenario 58 — Release automation

**🎯 Goal:** Pushing a tag `v1.4.2` builds release artifacts, publishes a versioned image, and
creates a release with auto-generated notes.

### Semantic Versioning (SemVer) refresher

```
v MAJOR . MINOR . PATCH
  1     . 4     . 2
  │       │       └── bug fixes, backward compatible
  │       └────────── new features, backward compatible
  └────────────────── breaking changes
```

With **Conventional Commits** (`feat:`, `fix:`, `feat!:`), tools compute the next version and
the changelog automatically.

### GitHub Actions — release on tag push

```yaml
name: Release
on:
  push:
    tags: ["v*.*.*"]

permissions:
  contents: write                     # create releases
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Derive version from tag
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> "$GITHUB_ENV"     # v1.4.2 → 1.4.2

      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          build-args: APP_VERSION=${{ env.VERSION }}
          tags: |
            ghcr.io/${{ github.repository }}:${{ env.VERSION }}
            ghcr.io/${{ github.repository }}:latest

      - name: Build CLI binaries
        run: make dist VERSION=${VERSION}                 # produces dist/*.tar.gz

      - name: Create GitHub Release with generated notes
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh release create "$GITHUB_REF_NAME" dist/*.tar.gz --generate-notes --verify-tag
```

**Fully automated versioning with release-please** (opens a "Release PR" that bumps the version
and changelog; merging it creates the tag and release):

```yaml
name: release-please
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node          # bumps package.json + CHANGELOG.md
```

### Azure DevOps — tag-triggered release pipeline

```yaml
trigger:
  tags:
    include: ['v*']
  branches:
    exclude: ['*']                    # ONLY tags trigger this pipeline

pool: { vmImage: ubuntu-latest }

variables:
  version: $[ replace(variables['Build.SourceBranchName'], 'v', '') ]   # refs/tags/v1.4.2 → 1.4.2

name: release-$(Build.SourceBranchName)

steps:
  - task: Docker@2
    inputs:
      command: buildAndPush
      containerRegistry: acr-acme-prod
      repository: orders-api
      tags: |
        $(version)
        latest
  - script: make dist VERSION=$(version)
  - task: GitHubRelease@1             # for GitHub-hosted repos; Azure Repos: publish to Azure Artifacts instead
    inputs:
      gitHubConnection: github-acme
      repositoryName: acme/orders-api
      action: create
      tagSource: gitTag
      assets: dist/*.tar.gz
      changeLogCompareToRelease: lastFullRelease
      changeLogType: commitBased
```

### AWS — CodePipeline V2 triggered by tags

```yaml
OrdersReleasePipeline:
  Type: AWS::CodePipeline::Pipeline
  Properties:
    PipelineType: V2
    Triggers:
      - ProviderType: CodeStarSourceConnection
        GitConfiguration:
          SourceActionName: Source
          Push:
            - Tags:
                Includes: ["v*"]
    # Stages: Source → Build (buildspec-release.yml) → Approve → Deploy
```

`buildspec-release.yml` reads the tag from the source revision:

```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - VERSION=$(git describe --tags --exact-match 2>/dev/null | sed 's/^v//')
      - test -n "$VERSION" || { echo "Not a tagged commit"; exit 1; }
  build:
    commands:
      - docker build --build-arg APP_VERSION="$VERSION" -t "$REPO:$VERSION" .
      - docker push "$REPO:$VERSION"
```

**⚠️ Gotchas:**

- **Protect release tags** (GitHub tag rulesets / ADO tag permissions), so not everyone can
  create `v*` tags and trigger production releases.
- **The `GITHUB_TOKEN` can't trigger other workflows.** A release created with it won't fire
  `on: release` workflows. That's intentional, to prevent loops. Use a GitHub App token if you
  need chaining.
- **CodePipeline / CodeBuild may clone without tags.** Set the source action's output to
  **full clone** (`OutputArtifactFormat: CODEBUILD_CLONE_REF`) so `git describe` works.

---

## Scenario 59 — Cross-repo and cross-pipeline triggers

**🎯 Goal:** When the **shared library** repo publishes a new version, automatically run the
dependent **app** pipeline. Or: when CI finishes, start the deploy pipeline.

### GitHub Actions — `workflow_run` (same repo) and `repository_dispatch` (another repo)

```yaml
# Same repo: deploy.yml runs when "CI" completes on main
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: app
          run-id: ${{ github.event.workflow_run.id }}       # artifacts from the triggering run
          github-token: ${{ secrets.GITHUB_TOKEN }}
      - run: ./deploy.sh
```

```yaml
# Library repo: notify the app repo
- name: Trigger app pipeline
  env:
    GH_TOKEN: ${{ steps.app-token.outputs.token }}      # GitHub App token with access to acme/orders-api
  run: |
    gh api repos/acme/orders-api/dispatches \
      -f event_type=shared-lib-released \
      -F client_payload[version]="${GITHUB_REF_NAME}"
```

```yaml
# App repo: listen for it
on:
  repository_dispatch:
    types: [shared-lib-released]
jobs:
  bump:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Shared lib ${{ github.event.client_payload.version }} released — testing compatibility"
```

### Azure DevOps — pipeline resource triggers

```yaml
# orders-api-deploy pipeline: runs whenever orders-api-ci succeeds on main
resources:
  pipelines:
    - pipeline: ci                      # local alias
      source: orders-api-ci             # name of the other pipeline
      trigger:
        branches:
          include: [main]

trigger: none

stages:
  - stage: Deploy
    jobs:
      - deployment: Deploy
        environment: orders-prod
        strategy:
          runOnce:
            deploy:
              steps:
                - download: ci            # artifacts from the triggering CI run
                  artifact: app
                - script: echo "Deploying CI run $(resources.pipeline.ci.runName)"
```

Cross-repo: `resources: repositories:` with a `trigger:` makes a pipeline run when **another
repo** changes (Azure Repos).

### AWS — EventBridge rule on CodeBuild/CodePipeline state change

```yaml
LibReleasedRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source: ["aws.codebuild"]
      detail-type: ["CodeBuild Build State Change"]
      detail:
        project-name: ["shared-lib-release"]
        build-status: ["SUCCEEDED"]
    Targets:
      - Arn: !Sub "arn:aws:codepipeline:${AWS::Region}:${AWS::AccountId}:orders-api-pipeline"
        Id: start-app-pipeline
        RoleArn: !GetAtt EventsStartPipelineRole.Arn
```

**⚠️ Gotchas:**

- **`workflow_run` runs with the default branch's workflow file and has secrets,** even when the
  triggering run came from a fork PR. Never execute artifacts or code from an untrusted triggering
  run in a privileged context.
- **Trigger chains are hard to follow.** Document them, and show the upstream run ID in run names.

---

## Scenario 60 — Self-hosted runners and agents

**🎯 Goal:** Jobs need to reach **private resources** (a database in a VNet, an internal
registry), need **special hardware** (GPU, lots of RAM), or must stay inside your network for
compliance.

### GitHub Actions — self-hosted runner labels + Actions Runner Controller (ARC)

```yaml
jobs:
  integration:
    runs-on: [self-hosted, linux, x64, vnet-prod]    # all labels must match a runner
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/integration-tests.sh          # can reach private endpoints
```

On Kubernetes, **ARC** autoscales ephemeral runner pods. The `runs-on` value is the **runner
scale set name**:

```yaml
runs-on: arc-runner-set-prod
```

### GitHub Actions jobs on AWS CodeBuild (managed runners in your AWS account/VPC)

Create a CodeBuild project with a GitHub source and the webhook event `WORKFLOW_JOB_QUEUED`,
then:

```yaml
jobs:
  build:
    runs-on: codebuild-orders-runner-${{ github.run_id }}-${{ github.run_attempt }}
    steps:
      - uses: actions/checkout@v4
      - run: aws sts get-caller-identity        # runs with the CodeBuild project's IAM role
```

### Azure DevOps — agent pools and demands

```yaml
pool:
  name: vnet-prod-agents          # self-hosted pool (VMSS agents or Managed DevOps Pools)
  demands:
    - docker                      # agent must advertise this capability
    - Agent.OS -equals Linux

steps:
  - script: ./scripts/integration-tests.sh
```

> **Managed DevOps Pools** and **VM Scale Set agent pools** give autoscaled, ephemeral agents
> inside your VNet without managing individual VMs.

### AWS CodeBuild — VPC configuration

Attach the project to private subnets + a security group, and it can reach RDS, internal APIs
and so on:

```yaml
VpcConfig:
  VpcId: vpc-0abc123
  Subnets: [subnet-0aaa, subnet-0bbb]       # private subnets with a NAT gateway for internet access
  SecurityGroupIds: [sg-0ccc]
```

**⚠️ Gotchas:**

- **Persistent self-hosted runners keep state between jobs** (files, Docker images, credentials).
  One job can poison the next. Prefer **ephemeral** runners: one job, then destroyed.
- **Never attach self-hosted runners to public repos.** Anyone can open a PR that runs code on
  your network.
- **CodeBuild in a VPC needs a NAT gateway or VPC endpoints** to reach the internet / AWS APIs.
  Otherwise even `npm ci` and the S3 artifact upload time out.

---

## Scenario 61 — Notifications

**🎯 Goal:** Post to Slack/Teams when a `main` build fails or a production deploy completes.

### GitHub Actions — incoming webhook

```yaml
  notify:
    needs: [build, deploy]
    if: failure() && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Slack alert
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          curl -sS -X POST -H 'Content-Type: application/json' "$SLACK_WEBHOOK_URL" -d @- <<EOF
          {"text":"❌ *${GITHUB_REPOSITORY}* main pipeline failed (commit ${GITHUB_SHA::7} by ${GITHUB_ACTOR}). <${RUN_URL}|Open run>"}
          EOF
```

### Azure DevOps

```yaml
- job: Notify
  dependsOn: [Build, Deploy]
  condition: failed()
  pool: { vmImage: ubuntu-latest }
  steps:
    - checkout: none
    - bash: |
        curl -sS -X POST -H 'Content-Type: application/json' "$TEAMS_WEBHOOK_URL" -d @- <<EOF
        {"text":"❌ $(Build.DefinitionName) failed on $(Build.SourceBranchName). $(System.CollectionUri)$(System.TeamProject)/_build/results?buildId=$(Build.BuildId)"}
        EOF
      env:
        TEAMS_WEBHOOK_URL: $(TeamsWebhookUrl)    # secret variable
```

> Azure DevOps also has built-in **notification subscriptions** (Project settings →
> Notifications), plus Slack/Teams apps that post build and release events without any YAML.

### AWS — EventBridge → SNS → chat (AWS Chatbot / Amazon Q Developer in chat applications)

```yaml
BuildFailedRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source: ["aws.codepipeline"]
      detail-type: ["CodePipeline Pipeline Execution State Change"]
      detail:
        state: ["FAILED"]
        pipeline: ["orders-api-pipeline"]
    Targets:
      - Arn: !Ref AlertsTopic               # SNS topic subscribed by the chat integration
        Id: notify-chat
```

**⚠️ Gotchas:**

- **Webhook URLs are secrets.** Anyone holding one can post to your channel. Store them as secrets.
- **Notify on failure and on recovery, not on every success.** Noisy channels get muted, and then
  nobody sees the real alerts.
- **Microsoft retired Office 365 connectors for Teams** in favour of **Workflows** webhooks.
  Old `outlook.office.com/webhook` URLs stop working; recreate them as Workflows.

---

## Scenario 62 — Hotfix flow

**🎯 Goal:** Production (v1.4.2) has a critical bug, but `main` already contains unreleased
features. Ship **only the fix**, quickly but safely.

```
main      ──●──●──●(new features, not released)──●(fix merged back)
              \
release/1.4    ●(v1.4.2)──●(fix cherry-picked) → tag v1.4.3 → prod
```

### Process

1. Create the fix on a branch from the release tag/branch:
   `git switch -c hotfix/1.4.3 v1.4.2` (or from `release/1.4`).
2. Open a PR **into `release/1.4`**. The same CI runs (tests and security are never skipped).
3. Merge and tag `v1.4.3`. The release pipeline (Scenario 58) builds and deploys it.
4. **Merge or cherry-pick the fix back into `main`**, or the bug returns in the next release.

### Pipeline support

```yaml
# GitHub: run CI + release for release branches too
on:
  push:
    branches: [main, "release/**"]
    tags: ["v*.*.*"]
  pull_request:
    branches: [main, "release/**"]
```

```yaml
# Azure DevOps: allow production deploys from main OR release branches
condition: |
  and(succeeded(),
      or(eq(variables['Build.SourceBranch'], 'refs/heads/main'),
         startsWith(variables['Build.SourceBranch'], 'refs/heads/release/'),
         startsWith(variables['Build.SourceBranch'], 'refs/tags/v')))
```

The environment's **branch control** check must also allow `refs/heads/release/*` and
`refs/tags/v*`, or the hotfix deploy is blocked at 3 a.m.

```yaml
# AWS: a second webhook filter group / pipeline trigger for release branches
- - Type: EVENT
    Pattern: PUSH
  - Type: HEAD_REF
    Pattern: ^refs/heads/release/.*$
```

**⚠️ Gotchas:**

- **"Just this once, skip the tests"** is how hotfixes cause second outages. Make the pipeline
  fast enough that skipping is never tempting.
- **Forgetting to port the fix back to `main`** brings the bug back in the next release. Automate
  a reminder: a bot opens a PR to `main` when a `release/*` branch gets a fix.

---

## Scenario 63 — Scheduled housekeeping

**🎯 Goal:** Container registries and artifact stores grow forever and cost money. Clean them on
a schedule, while **keeping** what production might need for rollback.

### GitHub Actions — delete old GHCR versions

```yaml
name: Cleanup
on:
  schedule:
    - cron: "0 2 * * 0"           # Sundays 02:00 UTC
  workflow_dispatch:

permissions:
  packages: write

jobs:
  ghcr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/delete-package-versions@v5
        with:
          package-name: orders-api
          package-type: container
          min-versions-to-keep: 30
          delete-only-untagged-versions: "true"
```

### Azure DevOps — ACR purge

```yaml
schedules:
  - cron: "0 2 * * 0"
    branches: { include: [main] }
    always: true
trigger: none

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: arm-acr-maintenance
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        # Delete tags older than 30 days but always keep the 20 most recent; remove untagged manifests
        az acr run --registry acmeprodacr \
          --cmd "acr purge --filter 'orders-api:.*' --ago 30d --keep 20 --untagged" /dev/null
```

> Azure Pipelines **retention policies** (Project settings → Pipelines → Settings) control how
> long runs, logs and artifacts are kept. Runs deployed to environments are retained
> automatically.

### AWS — ECR lifecycle policy (no pipeline needed)

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Remove untagged images after 7 days",
      "selection": { "tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7 },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Keep only the last 50 images",
      "selection": { "tagStatus": "any", "countType": "imageCountMoreThan", "countNumber": 50 },
      "action": { "type": "expire" }
    }
  ]
}
```

```bash
aws ecr put-lifecycle-policy --repository-name orders-api --lifecycle-policy-text file://ecr-lifecycle.json
```

Plus an **S3 lifecycle rule** on the CodePipeline artifact bucket (expire objects after N days).

**⚠️ Gotchas:**

- **Don't delete what's running.** Purge rules based only on age can delete the image currently
  deployed in production (an old but stable service), and the next node scale-up fails with
  `ImagePullBackOff`. Keep generous counts, protect release tags (`v*`) with a separate rule, or
  check what's deployed before deleting.

---

## Scenario 64 — Portable pipelines with a Makefile

**🎯 Goal:** The company is migrating from Azure DevOps to GitHub Actions (or running on both
during a transition). Keep **all real logic** in versioned scripts, so each CI system only needs
a thin wrapper.

`Makefile` (the single source of truth for *how* to build):

```makefile
IMAGE   ?= orders-api
VERSION ?= $(shell git rev-parse --short HEAD)
REGISTRY ?= ghcr.io/acme

.PHONY: install lint test build image push scan

install:
	npm ci

lint: install
	npm run lint

test: install
	npm test -- --ci --reporters=default --reporters=jest-junit

build: install
	npm run build

image:
	docker build -t $(REGISTRY)/$(IMAGE):$(VERSION) .

scan: image
	trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 $(REGISTRY)/$(IMAGE):$(VERSION)

push: scan
	docker push $(REGISTRY)/$(IMAGE):$(VERSION)
```

Thin wrappers. Each platform only handles triggers, auth and reporting:

```yaml
# GitHub Actions
jobs:
  ci:
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: make lint test build
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - run: make push VERSION=${{ github.sha }}
```

```yaml
# Azure DevOps
steps:
  - task: UseNode@1
    inputs: { version: '22.x' }
  - script: make lint test build
  - task: Docker@2
    inputs: { command: login, containerRegistry: acr-acme-prod }
  - script: make push VERSION=$(Build.SourceVersion) REGISTRY=acmeprodacr.azurecr.io
  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs: { testResultsFiles: junit.xml }
```

```yaml
# AWS CodeBuild
version: 0.2
phases:
  install:
    runtime-versions: { nodejs: 20 }
  pre_build:
    commands:
      - REGISTRY="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "$REGISTRY"
  build:
    commands:
      - make lint test build
      - make push VERSION="$CODEBUILD_RESOLVED_SOURCE_VERSION" REGISTRY="$REGISTRY"
reports:
  tests:
    files: [junit.xml]
    file-format: JUNITXML
```

**🔍 Explained:**

- **Developers run the same `make test` locally,** so "works in CI but not locally" mostly
  disappears.
- **A migration only touches the thin YAML layer:** triggers, authentication, caching and
  reporting, which really are platform-specific.
- **Alternatives to Make:** `Taskfile` (go-task), `just`, npm scripts, or the **Dagger**
  framework (pipelines written as code that run identically on any CI).

**⚠️ Gotchas:**

- **Makefiles need TAB indentation** for recipe lines. Spaces give `missing separator`.
- **Don't push platform logic (approvals, environments) into scripts.** Those protections belong
  in the CI platform, where admins control them.

---

**Next:** [07 — Troubleshooting & Gotchas Reference ➡️](07-troubleshooting.md)
