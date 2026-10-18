# 03 — Deployment Scenarios (Scenarios 24–36)

[⬅️ Back to Index](README.md) · [⬅️ Previous: Container Pipelines](02-containers.md)

---

> **CD (Continuous Delivery/Deployment)** takes the artifact that CI built and puts it on real
> infrastructure: web apps, Kubernetes, serverless, static sites. It does this safely, with
> approvals, progressive rollouts and rollbacks.

### Deployment strategies in one picture

```
 RECREATE      stop v1 ──────► start v2            (downtime; simplest)
 ROLLING       v1 v1 v1 → v2 v1 v1 → v2 v2 v1 → v2 v2 v2   (gradual replace; default in K8s/ECS)
 BLUE/GREEN    [blue=v1 live] [green=v2 idle] → test green → SWITCH traffic → keep blue for instant rollback
 CANARY        v2 gets 5% → 25% → 50% → 100%, watching metrics; abort = route back to v1
```

| Strategy | Downtime | Rollback speed | Extra cost | Typical tooling |
|----------|----------|----------------|-----------|-----------------|
| Recreate | Yes | Slow (redeploy) | None | Dev environments |
| Rolling | No | Medium | Minimal | K8s Deployment, ECS rolling |
| Blue/Green | No | **Instant** (switch back) | 2× capacity during deploy | App Service slots, ECS + CodeDeploy |
| Canary | No | Fast | Small | Argo Rollouts, ADO canary, Lambda aliases, Container Apps revisions |

---

## Table of Contents

| # | Scenario | Platforms / targets |
|---|----------|---------------------|
| 24 | [Multi-environment pipeline: dev → staging → prod with approvals](#scenario-24--multi-environment-pipeline-with-approvals) | All three |
| 25 | [Deploy a web app to PaaS (App Service / Elastic Beanstalk)](#scenario-25--deploy-a-web-app-to-paas) | Azure App Service, AWS Elastic Beanstalk |
| 26 | [Static website to object storage + CDN](#scenario-26--static-website-to-object-storage-and-cdn) | S3 + CloudFront, Azure Storage + Front Door |
| 27 | [Kubernetes deploy with manifests (AKS / EKS)](#scenario-27--kubernetes-deploy-with-manifests) | kubectl / kustomize |
| 28 | [Helm deploy with atomic rollback](#scenario-28--helm-deploy-with-atomic-rollback) | Helm on AKS / EKS |
| 29 | [Amazon ECS Fargate deploy](#scenario-29--amazon-ecs-fargate-deploy) | ECS, CodePipeline |
| 30 | [Serverless deploy (AWS Lambda SAM / Azure Functions)](#scenario-30--serverless-deploy) | SAM, Functions |
| 31 | [Blue/green deployments](#scenario-31--bluegreen-deployments) | App Service slots, ECS + CodeDeploy |
| 32 | [Canary releases](#scenario-32--canary-releases) | ADO canary on AKS, Lambda traffic shifting, Container Apps |
| 33 | [Database migrations in the pipeline](#scenario-33--database-migrations-in-the-pipeline) | Flyway job before deploy |
| 34 | [GitOps: pipeline updates a config repo, Argo CD deploys](#scenario-34--gitops-with-argo-cd-or-flux) | Argo CD / Flux |
| 35 | [Post-deploy smoke tests with automatic rollback](#scenario-35--post-deploy-smoke-tests-and-automatic-rollback) | All three |
| 36 | [Manual rollback to a previous version](#scenario-36--manual-rollback-to-a-previous-version) | All three |

---

## Scenario 24 — Multi-environment pipeline with approvals

**🎯 Goal:** Build once. Deploy automatically to **dev**, then **staging**, and to
**production** only after a human approves, and only from `main`. Each environment has its
own settings (URL, resource names) and secrets.

```
 build ──► dev (auto) ──► staging (auto) ──► ⏸ approval ──► prod
```

### GitHub Actions — Environments with protection rules

**One-time setup** (repo Settings → Environments):

| Environment | Protection rules | Variables / secrets |
|-------------|------------------|---------------------|
| `dev` | none | `APP_NAME=orders-dev`, `RESOURCE_GROUP=rg-orders-dev` |
| `staging` | deployment branches: `main` | `APP_NAME=orders-stg` … |
| `production` | **required reviewers** (team `platform-approvers`), **wait timer** 10 min, branches: `main` only | `APP_NAME=orders-prod` … |

`.github/workflows/deploy.yml`:

```yaml
name: Build & Deploy
on:
  push:
    branches: [main]

permissions:
  contents: read
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm test && npm run build
      - uses: actions/upload-artifact@v4
        with: { name: app, path: dist/ }

  deploy-dev:
    needs: build
    uses: ./.github/workflows/_deploy.yml      # reusable workflow (Chapter 06)
    with:
      environment: dev
    secrets: inherit

  deploy-staging:
    needs: deploy-dev
    uses: ./.github/workflows/_deploy.yml
    with:
      environment: staging
    secrets: inherit

  deploy-prod:
    needs: deploy-staging
    uses: ./.github/workflows/_deploy.yml
    with:
      environment: production
    secrets: inherit
```

`.github/workflows/_deploy.yml` (the reusable deploy job):

```yaml
name: _deploy
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: ${{ inputs.environment }}          # pauses here until approved (if rules exist)
      url: https://${{ vars.APP_NAME }}.azurewebsites.net
    concurrency: deploy-${{ inputs.environment }}   # never two deploys to the same env at once
    steps:
      - uses: actions/download-artifact@v4
        with: { name: app, path: dist/ }
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}        # per-environment value
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ vars.APP_NAME }}
          package: dist/
```

### Azure DevOps — stages + Environments (approvals set in the UI)

**One-time setup** (Pipelines → Environments): create `orders-dev`, `orders-staging`,
`orders-prod`. On `orders-prod` → **Approvals and checks** → add *Approvals*
(group `Platform Approvers`), *Branch control* (`refs/heads/main`) and optionally
*Business hours*.

```yaml
trigger: [main]

variables:
  - name: vmImage
    value: ubuntu-latest

stages:
  - stage: Build
    jobs:
      - job: Build
        pool: { vmImage: $(vmImage) }
        steps:
          - script: npm ci && npm test && npm run build
          - publish: dist
            artifact: app

  - template: templates/deploy-stage.yml
    parameters:
      envName: dev
      dependsOn: Build
      serviceConnection: arm-orders-dev
      appName: orders-dev

  - template: templates/deploy-stage.yml
    parameters:
      envName: staging
      dependsOn: Deploy_dev
      serviceConnection: arm-orders-staging
      appName: orders-stg

  - template: templates/deploy-stage.yml
    parameters:
      envName: prod
      dependsOn: Deploy_staging
      serviceConnection: arm-orders-prod
      appName: orders-prod
```

`templates/deploy-stage.yml`:

```yaml
parameters:
  - name: envName
    type: string
  - name: dependsOn
    type: string
  - name: serviceConnection
    type: string
  - name: appName
    type: string

stages:
  - stage: Deploy_${{ parameters.envName }}
    dependsOn: ${{ parameters.dependsOn }}
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    variables:
      - group: orders-${{ parameters.envName }}      # per-environment variable group
    jobs:
      - deployment: Deploy
        pool: { vmImage: ubuntu-latest }
        environment: orders-${{ parameters.envName }}   # approvals/checks enforced here
        strategy:
          runOnce:
            deploy:
              steps:
                # artifact "app" is downloaded automatically to $(Pipeline.Workspace)/app
                - task: AzureWebApp@1
                  inputs:
                    azureSubscription: ${{ parameters.serviceConnection }}
                    appType: webAppLinux
                    appName: ${{ parameters.appName }}
                    package: $(Pipeline.Workspace)/app
```

### AWS CodePipeline — stages with a Manual Approval action (CloudFormation)

```yaml
OrdersPipeline:
  Type: AWS::CodePipeline::Pipeline
  Properties:
    PipelineType: V2
    RoleArn: !GetAtt PipelineRole.Arn
    ArtifactStore:
      Type: S3
      Location: !Ref ArtifactBucket
    Stages:
      - Name: Source
        Actions:
          - Name: GitHub
            ActionTypeId: { Category: Source, Owner: AWS, Provider: CodeStarSourceConnection, Version: "1" }
            Configuration:
              ConnectionArn: !Ref GitHubConnectionArn
              FullRepositoryId: acme/orders-api
              BranchName: main
            OutputArtifacts: [{ Name: SourceOutput }]

      - Name: Build
        Actions:
          - Name: Build
            ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
            Configuration: { ProjectName: !Ref BuildProject }
            InputArtifacts: [{ Name: SourceOutput }]
            OutputArtifacts: [{ Name: BuildOutput }]

      - Name: DeployDev
        Actions:
          - Name: Deploy
            ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
            Configuration:
              ProjectName: !Ref DeployProject              # runs a deploy buildspec
              EnvironmentVariables: '[{"name":"TARGET_ENV","value":"dev","type":"PLAINTEXT"}]'
            InputArtifacts: [{ Name: BuildOutput }]

      - Name: ApproveProd
        Actions:
          - Name: ManualApproval
            ActionTypeId: { Category: Approval, Owner: AWS, Provider: Manual, Version: "1" }
            Configuration:
              NotificationArn: !Ref ApprovalTopic          # SNS → email/Slack
              CustomData: "Approve deploying orders-api to PRODUCTION"

      - Name: DeployProd
        Actions:
          - Name: Deploy
            ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
            Configuration:
              ProjectName: !Ref DeployProjectProd          # separate project + IAM role for prod
              EnvironmentVariables: '[{"name":"TARGET_ENV","value":"prod","type":"PLAINTEXT"}]'
            InputArtifacts: [{ Name: BuildOutput }]
```

**🔍 Explained:**

- **Approvals live outside the YAML.** GitHub environment protection rules, ADO environment
  checks and CodePipeline Manual Approval actions are all controlled by admins. A developer
  can't remove the approval by editing the pipeline file.
- **Per-environment config:**
  - GitHub environment variables/secrets
  - ADO variable groups (one per environment)
  - CodeBuild environment variables or Parameter Store paths like `/orders/${TARGET_ENV}/...`
- **A separate cloud identity per environment** (`arm-orders-prod`, a prod deploy project with
  its own IAM role) means a compromised dev pipeline can't touch production.

**⚠️ Gotchas:**

- **GitHub: required reviewers on environments in private repos** need a paid plan
  (GitHub Team/Enterprise). On the free plan the rule silently doesn't apply.
- **ADO: an environment's approvals apply to every pipeline that uses that environment.**
  Use distinct environment names per app if teams need different approvers.
- **Approval timeouts:** ADO approvals time out (default 30 days, configurable). CodePipeline
  approvals expire after 7 days. Stale runs should be rejected, not approved weeks later.

---

## Scenario 25 — Deploy a web app to PaaS

**🎯 Goal:** Deploy a Node.js app as a zip package to a managed web hosting service.

### GitHub Actions → Azure App Service

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: |
          npm ci
          npm run build
          npm prune --omit=dev                 # ship only production dependencies
          zip -r app.zip dist node_modules package.json
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: orders-prod
          package: app.zip
      - name: Set app settings (configuration, not code)
        run: |
          az webapp config appsettings set -g rg-orders-prod -n orders-prod \
            --settings NODE_ENV=production LOG_LEVEL=info
```

### Azure DevOps → Azure App Service

```yaml
steps:
  - script: |
      npm ci && npm run build && npm prune --omit=dev
    displayName: Build
  - task: ArchiveFiles@2
    inputs:
      rootFolderOrFile: $(System.DefaultWorkingDirectory)
      includeRootFolder: false
      archiveType: zip
      archiveFile: $(Build.ArtifactStagingDirectory)/app.zip
  - task: AzureWebApp@1
    inputs:
      azureSubscription: arm-orders-prod
      appType: webAppLinux
      appName: orders-prod
      package: $(Build.ArtifactStagingDirectory)/app.zip
      runtimeStack: 'NODE|22-lts'
      startUpCommand: 'node dist/server.js'
      appSettings: '-NODE_ENV production -LOG_LEVEL info'
```

### AWS CodeBuild → Elastic Beanstalk

```yaml
version: 0.2
env:
  variables:
    EB_APP: orders
    EB_ENV: orders-prod
    BUCKET: acme-eb-artifacts
phases:
  install:
    runtime-versions: { nodejs: 20 }
  build:
    commands:
      - npm ci && npm run build && npm prune --omit=dev
      - VERSION="v-$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)-$CODEBUILD_BUILD_NUMBER"
      - zip -r app.zip dist node_modules package.json Procfile
  post_build:
    commands:
      - aws s3 cp app.zip "s3://${BUCKET}/${EB_APP}/${VERSION}.zip"
      - aws elasticbeanstalk create-application-version --application-name "$EB_APP" --version-label "$VERSION" --source-bundle S3Bucket="$BUCKET",S3Key="${EB_APP}/${VERSION}.zip"
      - aws elasticbeanstalk update-environment --environment-name "$EB_ENV" --version-label "$VERSION"
      - aws elasticbeanstalk wait environment-updated --environment-names "$EB_ENV"
```

**🔍 Explained:**

- **PaaS ("Platform as a Service")** means you hand over the code and the platform runs it.
  No servers or containers to manage.
- **`npm prune --omit=dev`** before zipping keeps test and build tools out of the package.
- **App settings** become environment variables inside the app. Config lives in the platform,
  not in the zip, so the same package works in every environment.
- **`aws elasticbeanstalk wait environment-updated`** blocks until the rollout finishes, so the
  pipeline result matches reality.

**⚠️ Gotchas:**

- **App Service: the Node/Python build can run twice.** If `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
  is set (common with zip deploy), App Service runs `npm install` *again* on the server.
  That's slow and can produce different results. Either build in CI and disable it, or let
  the platform build. Don't do both.
- **Zip deploy replaces files while the app runs.** For zero downtime, use slots (Scenario 31).
- **Elastic Beanstalk keeps old application versions** until you hit a quota. Configure a
  version lifecycle policy.

---

## Scenario 26 — Static website to object storage and CDN

**🎯 Goal:** Upload a built SPA (React/Vue) to storage, set correct caching, and purge the CDN
so users get the new version.

### GitHub Actions → S3 + CloudFront

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-web-deploy
          aws-region: eu-west-1
      - name: Upload hashed assets (cache 1 year)
        run: aws s3 sync dist/assets s3://acme-web-prod/assets --cache-control "public,max-age=31536000,immutable"
      - name: Upload everything else (no cache) and delete removed files
        run: aws s3 sync dist s3://acme-web-prod --delete --exclude "assets/*" --cache-control "no-cache"
      - name: Invalidate CloudFront
        run: aws cloudfront create-invalidation --distribution-id ${{ vars.CF_DISTRIBUTION_ID }} --paths "/index.html" "/"
```

### Azure DevOps → Azure Storage static website + Front Door

```yaml
steps:
  - script: npm ci && npm run build
    displayName: Build
  - task: AzureCLI@2
    displayName: Upload & purge
    inputs:
      azureSubscription: arm-web-prod
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        az storage blob upload-batch --account-name acmewebprod --auth-mode login \
          -d '$web' -s dist --overwrite \
          --content-cache-control "no-cache" --pattern "*.html"
        az storage blob upload-batch --account-name acmewebprod --auth-mode login \
          -d '$web' -s dist --overwrite \
          --content-cache-control "public,max-age=31536000,immutable" --pattern "assets/*"
        az afd endpoint purge -g rg-web-prod --profile-name afd-acme \
          --endpoint-name web-prod --content-paths "/index.html" "/"
```

### AWS CodeBuild → S3 + CloudFront

```yaml
version: 0.2
env:
  variables:
    BUCKET: acme-web-prod
  parameter-store:
    CF_DISTRIBUTION_ID: /web/prod/cloudfront_id
phases:
  install:
    runtime-versions: { nodejs: 20 }
    commands: [npm ci]
  build:
    commands: [npm run build]
  post_build:
    commands:
      - aws s3 sync dist/assets "s3://${BUCKET}/assets" --cache-control "public,max-age=31536000,immutable"
      - aws s3 sync dist "s3://${BUCKET}" --delete --exclude "assets/*" --cache-control "no-cache"
      - aws cloudfront create-invalidation --distribution-id "$CF_DISTRIBUTION_ID" --paths "/index.html" "/"
```

**🔍 Explained:**

- **Two cache policies:**
  - Fingerprinted files (`assets/app.3f2c1a.js`) never change, so cache them for a year.
  - `index.html` must always be fresh, because it points to the newest asset names.
- **`--delete`** removes files from the bucket that no longer exist locally. We exclude
  `assets/` so that users still holding an old `index.html` can download the old assets.
- **CDN invalidation** tells CloudFront/Front Door to drop its cached copy of `index.html`.
- **`--auth-mode login`** uses the pipeline's Entra identity (it needs the *Storage Blob Data
  Contributor* role) instead of storage account keys.

**⚠️ Gotchas:**

- **Invalidating `/*` on every deploy** is slow, and CloudFront charges for invalidations
  beyond the free monthly quota. Invalidate only the non-hashed files.
- **SPA deep links (`/orders/42`) return 404 from S3** unless CloudFront maps 403/404 errors to
  `/index.html` (custom error responses), or a CloudFront Function rewrites the path.
- **Build-time environment variables** (`VITE_API_URL`) are baked into the files. See the
  Dockerfile Handbook, Example 67/69.

---

## Scenario 27 — Kubernetes deploy with manifests

**🎯 Goal:** Deploy a new image tag to a Kubernetes cluster using plain YAML manifests (with
**kustomize** to set the image), and wait until the rollout succeeds.

Repo layout:

```
k8s/
├── base/
│   ├── deployment.yaml     # image: orders-api (tag set by kustomize)
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── dev/kustomization.yaml
    └── prod/kustomization.yaml   # replicas, resources, namespace for prod
```

### GitHub Actions → AKS

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/setup-kubectl@v4
      - uses: azure/use-kubelogin@v1          # needed for Entra ID-enabled AKS clusters
        with: { kubelogin-version: v0.1.4 }
      - uses: azure/aks-set-context@v4
        with:
          resource-group: rg-aks-prod
          cluster-name: aks-prod
          admin: "false"
          use-kubelogin: "true"
      - name: Set image tag and apply
        working-directory: k8s/overlays/prod
        run: |
          kustomize edit set image orders-api=acmeprodacr.azurecr.io/orders-api:${{ github.sha }}
          kubectl apply -k .
          kubectl -n orders rollout status deployment/orders-api --timeout=5m
```

### Azure DevOps → AKS (KubernetesManifest task)

```yaml
- stage: DeployProd
  jobs:
    - deployment: Deploy
      pool: { vmImage: ubuntu-latest }
      environment: orders-prod
      strategy:
        runOnce:
          deploy:
            steps:
              - checkout: self                       # manifests live in the repo
              - task: KubernetesManifest@1
                displayName: Bake kustomize overlay
                name: bake
                inputs:
                  action: bake
                  renderType: kustomize
                  kustomizationPath: k8s/overlays/prod
              - task: KubernetesManifest@1
                displayName: Deploy
                inputs:
                  action: deploy
                  connectionType: azureResourceManager
                  azureSubscriptionConnection: arm-orders-prod
                  azureResourceGroup: rg-aks-prod
                  kubernetesCluster: aks-prod
                  namespace: orders
                  manifests: $(bake.manifestsBundle)
                  containers: acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion)
```

### AWS CodeBuild → EKS

```yaml
version: 0.2
env:
  variables:
    CLUSTER: eks-prod
    NAMESPACE: orders
phases:
  install:
    commands:
      - curl -fsSLo /usr/local/bin/kubectl "https://dl.k8s.io/release/v1.31.2/bin/linux/amd64/kubectl" && chmod +x /usr/local/bin/kubectl
      - curl -fsSL "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv5.5.0/kustomize_v5.5.0_linux_amd64.tar.gz" | tar -xz -C /usr/local/bin
  pre_build:
    commands:
      - aws eks update-kubeconfig --name "$CLUSTER" --region "$AWS_DEFAULT_REGION"
      - ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      - IMAGE="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/orders-api:$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)"
  build:
    commands:
      - cd k8s/overlays/prod
      - kustomize edit set image orders-api="$IMAGE"
      - kubectl apply -k .
      - kubectl -n "$NAMESPACE" rollout status deployment/orders-api --timeout=5m
```

**🔍 Explained:**

- **`kustomize edit set image`** rewrites the image tag in `kustomization.yaml` without
  touching the base manifests.
- **`kubectl rollout status --timeout`** waits until all new pods are ready. If they crash or
  fail readiness probes, the step fails, so the pipeline result reflects the real deployment.
- **The ADO `KubernetesManifest` task** substitutes the `containers:` image into the manifests,
  annotates resources with pipeline metadata, and checks rollout status for you.

**⚠️ Gotchas:**

- **EKS: the CodeBuild IAM role must be granted cluster access** with an **EKS access entry**
  (or the legacy `aws-auth` ConfigMap). Without it you get
  `error: You must be logged in to the server (Unauthorized)`.
- **AKS with Entra ID auth needs `kubelogin`.** Without it, kubectl tries to open an
  interactive browser login and hangs.
- **Don't use `admin: true` credentials** in pipelines. Bind the pipeline identity to a
  namespace-scoped Kubernetes Role instead.
- **`kubectl apply` succeeding ≠ the app working.** Always follow it with `rollout status`.

---

## Scenario 28 — Helm deploy with atomic rollback

**🎯 Goal:** Deploy with **Helm** (Kubernetes' package manager). If the new release doesn't
become healthy within the timeout, **automatically roll back** to the previous release.

The core command is the same everywhere:

```bash
helm upgrade --install orders-api ./charts/orders-api \
  --namespace orders --create-namespace \
  -f charts/orders-api/values-prod.yaml \
  --set image.tag="$TAG" \
  --atomic --timeout 5m --wait \
  --history-max 10
```

| Flag | Meaning |
|------|---------|
| `upgrade --install` | Install if missing, upgrade if present (idempotent) |
| `-f values-prod.yaml` | Environment-specific settings |
| `--set image.tag=` | Override a single value |
| `--wait` | Wait until pods/services are ready |
| `--atomic` | If the release fails (or times out), **roll back automatically** |
| `--history-max 10` | Keep only 10 old releases (otherwise Secrets pile up in the namespace) |

### GitHub Actions → EKS

```yaml
jobs:
  helm-deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-eks-deploy
          aws-region: eu-west-1
      - uses: azure/setup-helm@v4          # works for any cluster, not just Azure
        with: { version: v3.16.2 }
      - run: aws eks update-kubeconfig --name eks-prod
      - name: Lint & render first (fail early on template errors)
        run: |
          helm lint charts/orders-api -f charts/orders-api/values-prod.yaml
          helm template orders-api charts/orders-api -f charts/orders-api/values-prod.yaml > /dev/null
      - name: Deploy
        run: |
          helm upgrade --install orders-api charts/orders-api -n orders --create-namespace \
            -f charts/orders-api/values-prod.yaml --set image.tag=${{ github.sha }} \
            --atomic --timeout 5m --wait --history-max 10
```

### Azure DevOps → AKS

```yaml
steps:
  - task: HelmInstaller@1
    inputs:
      helmVersionToInstall: 3.16.2
  - task: AzureCLI@2
    displayName: Helm upgrade
    inputs:
      azureSubscription: arm-orders-prod
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        az aks get-credentials -g rg-aks-prod -n aks-prod --overwrite-existing
        kubelogin convert-kubeconfig -l azurecli      # use the pipeline's Azure CLI identity
        helm upgrade --install orders-api charts/orders-api -n orders --create-namespace \
          -f charts/orders-api/values-prod.yaml --set image.tag=$(Build.SourceVersion) \
          --atomic --timeout 5m --wait --history-max 10
```

### AWS CodeBuild → EKS

```yaml
version: 0.2
phases:
  install:
    commands:
      - curl -fsSL https://get.helm.sh/helm-v3.16.2-linux-amd64.tar.gz | tar -xz --strip-components=1 -C /usr/local/bin linux-amd64/helm
  pre_build:
    commands:
      - aws eks update-kubeconfig --name eks-prod
      - TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)
  build:
    commands:
      - helm lint charts/orders-api -f charts/orders-api/values-prod.yaml
      - >
        helm upgrade --install orders-api charts/orders-api -n orders --create-namespace
        -f charts/orders-api/values-prod.yaml --set image.tag=$TAG
        --atomic --timeout 5m --wait --history-max 10
```

**⚠️ Gotchas:**

- **"another operation (install/upgrade/rollback) is in progress"** means a previous run was
  killed mid-deploy and the release is stuck in a `pending-*` state. Check
  `helm history orders-api -n orders`, then `helm rollback` to the last good revision.
  Prevent it by never running two deploys at once (`concurrency`, Chapter 06).
- **`--atomic` hides the reason for failure,** because it rolls back immediately. Print
  diagnostics on failure: `kubectl get events -n orders --sort-by=.lastTimestamp | tail -30`.
- **Helm doesn't change CRDs on upgrade** (`crds/` folder). CRD changes need a separate step.

---

## Scenario 29 — Amazon ECS Fargate deploy

**🎯 Goal:** Roll out a new image to an **ECS service** on Fargate (serverless containers),
and wait until it's stable.

### GitHub Actions

`ecs/task-definition.json` is committed to the repo (exported once with
`aws ecs describe-task-definition`).

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-ecs-deploy
          aws-region: eu-west-1
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build & push
        env:
          IMAGE: ${{ steps.ecr.outputs.registry }}/orders-api:${{ github.sha }}
        run: |
          docker build -t "$IMAGE" .
          docker push "$IMAGE"
          echo "IMAGE=$IMAGE" >> "$GITHUB_ENV"

      - name: Render task definition with the new image
        id: render
        uses: aws-actions/amazon-ecs-render-task-definition@v1
        with:
          task-definition: ecs/task-definition.json
          container-name: orders-api
          image: ${{ env.IMAGE }}

      - name: Deploy to ECS
        uses: aws-actions/amazon-ecs-deploy-task-definition@v2
        with:
          task-definition: ${{ steps.render.outputs.task-definition }}
          cluster: prod-cluster
          service: orders-api
          wait-for-service-stability: true
```

### AWS CodePipeline — Build (Scenario 16 buildspec) + ECS deploy action

The buildspec from **Scenario 16** writes `imagedefinitions.json`. Add a Deploy stage:

```yaml
- Name: Deploy
  Actions:
    - Name: DeployToECS
      ActionTypeId: { Category: Deploy, Owner: AWS, Provider: ECS, Version: "1" }
      Configuration:
        ClusterName: prod-cluster
        ServiceName: orders-api
        FileName: imagedefinitions.json
        DeploymentTimeout: "15"            # minutes
      InputArtifacts: [{ Name: BuildOutput }]
```

### Azure DevOps → ECS (AWS CLI with an OIDC-assumed role)

```yaml
steps:
  - task: AWSShellScript@1                # from the "AWS Toolkit for Azure DevOps" extension
    inputs:
      awsCredentials: aws-prod-oidc        # AWS service connection
      regionName: eu-west-1
      scriptType: inline
      inlineScript: |
        set -euo pipefail
        IMAGE="123456789012.dkr.ecr.eu-west-1.amazonaws.com/orders-api:$(Build.SourceVersion)"
        # Take the current task definition, swap the image, register a new revision
        aws ecs describe-task-definition --task-definition orders-api --query taskDefinition > td.json
        jq --arg IMG "$IMAGE" '.containerDefinitions[0].image=$IMG
          | del(.taskDefinitionArn,.revision,.status,.requiresAttributes,.compatibilities,.registeredAt,.registeredBy)' td.json > td-new.json
        NEW_ARN=$(aws ecs register-task-definition --cli-input-json file://td-new.json --query taskDefinition.taskDefinitionArn --output text)
        aws ecs update-service --cluster prod-cluster --service orders-api --task-definition "$NEW_ARN"
        aws ecs wait services-stable --cluster prod-cluster --services orders-api
```

**🔍 Explained:**

- **A task definition** is ECS's "pod spec": image, CPU/memory, env vars, IAM role. Every
  change creates a new **revision**. The **service** is updated to point at the new revision,
  and ECS does a rolling replacement.
- **`wait-for-service-stability` / `aws ecs wait services-stable`** waits until the new tasks
  are healthy and the old ones have drained.
- **The `jq ... del(...)`** strips read-only fields that `register-task-definition` rejects.

**⚠️ Gotchas:**

- **Enable the ECS deployment circuit breaker** (`deploymentCircuitBreaker: enable, rollback`)
  on the service. Without it, a crash-looping image keeps ECS trying for hours.
- **The deploy role needs `iam:PassRole`** for the task execution role and task role.
  Otherwise: `AccessDenied ... iam:PassRole`.
- **Task definitions edited in the console drift** from the JSON in the repo. Treat the repo
  (or IaC) as the source of truth.

---

## Scenario 30 — Serverless deploy

### GitHub Actions → AWS Lambda with SAM

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: aws-actions/setup-sam@v2
        with: { use-installer: true }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-sam-deploy
          aws-region: eu-west-1
      - run: sam build --use-container=false
      - run: >
          sam deploy
          --stack-name orders-functions-prod
          --resolve-s3
          --capabilities CAPABILITY_IAM
          --no-confirm-changeset
          --no-fail-on-empty-changeset
          --parameter-overrides Stage=prod
```

### AWS CodeBuild → Lambda with SAM

```yaml
version: 0.2
phases:
  install:
    runtime-versions: { python: 3.12 }
  build:
    commands:
      - sam build
      - >
        sam deploy --stack-name orders-functions-prod --resolve-s3 --capabilities CAPABILITY_IAM
        --no-confirm-changeset --no-fail-on-empty-changeset --parameter-overrides Stage=prod
```

### Azure DevOps → Azure Functions

```yaml
steps:
  - task: UsePythonVersion@0
    inputs: { versionSpec: '3.11' }
  - bash: |
      pip install --target=".python_packages/lib/site-packages" -r requirements.txt
    displayName: Install dependencies into the package folder
  - task: ArchiveFiles@2
    inputs:
      rootFolderOrFile: $(System.DefaultWorkingDirectory)
      includeRootFolder: false
      archiveFile: $(Build.ArtifactStagingDirectory)/functions.zip
  - task: AzureFunctionApp@2
    inputs:
      connectedServiceNameARM: arm-orders-prod
      appType: functionAppLinux
      appName: func-orders-prod
      package: $(Build.ArtifactStagingDirectory)/functions.zip
      deploymentMethod: auto
```

**🔍 Explained:**

- **SAM** (Serverless Application Model) is a CloudFormation extension. `sam build` packages
  the code and dependencies, and `sam deploy` creates/updates the CloudFormation stack.
- **`--resolve-s3`** lets SAM create and manage the upload bucket for you.
- **`--no-fail-on-empty-changeset`** means re-running with no changes doesn't fail
  (idempotent pipelines).
- **Azure Functions (Python)** expects dependencies inside `.python_packages/` in the zip,
  unless remote build is enabled.

**⚠️ Gotchas:**

- **Native dependencies** (e.g. `numpy`, `cryptography`) built on the CI machine must match
  Lambda's Linux and architecture. Use `sam build --use-container` or Lambda-compatible wheels.
- **`CAPABILITY_IAM` / `CAPABILITY_NAMED_IAM`** must be passed when the template creates IAM
  roles, or the deploy fails with `Requires capabilities`.

---

## Scenario 31 — Blue/green deployments

### Azure App Service deployment slots (GitHub Actions)

```
 staging slot (green) ◄── deploy v2, warm up, smoke test
 production slot (blue) = v1 live
            └──── SWAP (instant, no downtime) ────┘
```

```yaml
jobs:
  blue-green:
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/download-artifact@v4
        with: { name: app, path: app }
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy to the staging slot
        uses: azure/webapps-deploy@v3
        with:
          app-name: orders-prod
          slot-name: staging
          package: app
      - name: Smoke test the staging slot
        run: |
          for i in $(seq 1 20); do
            curl -fsS https://orders-prod-staging.azurewebsites.net/health && break
            sleep 5
          done
          curl -fsS https://orders-prod-staging.azurewebsites.net/health
      - name: Swap staging → production
        run: az webapp deployment slot swap -g rg-orders-prod -n orders-prod --slot staging --target-slot production
```

Azure DevOps equivalent: `AzureWebApp@1` with `deployToSlotOrASE: true`, `slotName: staging`,
then:

```yaml
- task: AzureAppServiceManage@0
  inputs:
    azureSubscription: arm-orders-prod
    Action: Swap Slots
    WebAppName: orders-prod
    ResourceGroupName: rg-orders-prod
    SourceSlot: staging
```

**Rollback = swap again.** The previous version is still sitting in the staging slot.

### ECS blue/green with CodeDeploy (CodeBuild + CodePipeline)

The buildspec must output three files: `imageDetail.json`, `taskdef.json`, `appspec.yaml`.

```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      - REPO="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/orders-api"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "${REPO%%/*}"
      - TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)
  build:
    commands:
      - docker build -t "${REPO}:${TAG}" .
      - docker push "${REPO}:${TAG}"
  post_build:
    commands:
      - printf '{"ImageURI":"%s"}' "${REPO}:${TAG}" > imageDetail.json
artifacts:
  files:
    - imageDetail.json
    - ecs/taskdef.json      # contains  "image": "<IMAGE1_NAME>"  placeholder
    - ecs/appspec.yaml
  discard-paths: yes
```

`ecs/appspec.yaml`:

```yaml
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>       # filled in by CodePipeline
        LoadBalancerInfo:
          ContainerName: orders-api
          ContainerPort: 8080
Hooks:
  - AfterAllowTestTraffic: arn:aws:lambda:eu-west-1:123456789012:function:orders-smoke-test
```

CodePipeline deploy action:

```yaml
- Name: BlueGreen
  ActionTypeId: { Category: Deploy, Owner: AWS, Provider: CodeDeployToECS, Version: "1" }
  Configuration:
    ApplicationName: orders-api
    DeploymentGroupName: orders-api-prod
    TaskDefinitionTemplateArtifact: BuildOutput
    TaskDefinitionTemplatePath: taskdef.json
    AppSpecTemplateArtifact: BuildOutput
    AppSpecTemplatePath: appspec.yaml
    Image1ArtifactName: BuildOutput
    Image1ContainerName: IMAGE1_NAME
  InputArtifacts: [{ Name: BuildOutput }]
```

**🔍 Explained:**

- **CodeDeploy** starts a **green** task set behind a **test listener**, runs the
  `AfterAllowTestTraffic` hook (a Lambda smoke test), then shifts production traffic. It keeps
  the blue task set for a configurable time, ready for instant rollback.
- **`<IMAGE1_NAME>` in `taskdef.json`** is replaced with the URI from `imageDetail.json`.

**⚠️ Gotchas:**

- **Slot settings marked as "deployment slot setting"** stay with the slot during a swap.
  Others move with the code. Getting this wrong swaps your **staging database connection
  string into production**.
- **Database schema changes must work for both blue and green** while both are live. See
  Scenario 33's expand/contract pattern.

---

## Scenario 32 — Canary releases

### Azure DevOps — built-in `canary` strategy on AKS

```yaml
- stage: CanaryProd
  jobs:
    - deployment: Canary
      pool: { vmImage: ubuntu-latest }
      environment: orders-prod.orders           # environment + Kubernetes namespace resource
      strategy:
        canary:
          increments: [10, 50]                  # 10% → 50% → (promote) 100%
          deploy:
            steps:
              - checkout: self
              - task: KubernetesManifest@1
                inputs:
                  action: deploy
                  strategy: canary
                  percentage: $(strategy.increment)
                  manifests: k8s/deployment.yaml
                  containers: acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion)
          postRouteTraffic:
            pool: server
            steps:
              - task: Delay@1                   # let real traffic hit the canary
                inputs: { delayForMinutes: '10' }
          on:
            failure:
              steps:
                - task: KubernetesManifest@1
                  inputs:
                    action: reject              # delete canary pods
                    strategy: canary
                    manifests: k8s/deployment.yaml
            success:
              steps:
                - task: KubernetesManifest@1
                  inputs:
                    action: promote             # roll the new version out to 100%
                    strategy: canary
                    manifests: k8s/deployment.yaml
                    containers: acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion)
```

### AWS — Lambda traffic shifting with SAM `DeploymentPreference`

In `template.yaml`. The pipeline just runs `sam deploy` (Scenario 30), and CodeDeploy handles
the canary:

```yaml
OrdersFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: app.handler
    Runtime: python3.12
    AutoPublishAlias: live                  # every deploy publishes a version behind alias "live"
    DeploymentPreference:
      Type: Canary10Percent5Minutes         # 10% for 5 minutes, then 100%
      Alarms:
        - !Ref OrdersErrorsAlarm            # if this alarm fires → automatic rollback
      Hooks:
        PreTraffic: !Ref PreTrafficCheckFunction
```

### GitHub Actions — Azure Container Apps revision traffic split

```yaml
- name: Deploy new revision with 0% traffic
  run: |
    az containerapp update -g rg-orders-prod -n orders-api \
      --image acmeprodacr.azurecr.io/orders-api:${{ github.sha }} \
      --revision-suffix g${GITHUB_SHA::7}
- name: Send 10% to the new revision
  run: |
    STABLE=$(az containerapp ingress traffic show -g rg-orders-prod -n orders-api \
      --query "[?weight==\`100\`].revisionName | [0]" -o tsv)
    az containerapp ingress traffic set -g rg-orders-prod -n orders-api \
      --revision-weight "$STABLE=90" "orders-api--g${GITHUB_SHA::7}=10"
- name: Watch error rate for 10 minutes
  run: ./scripts/check-error-rate.sh orders-api 10m    # exits non-zero if errors spike
- name: Promote to 100%
  run: |
    az containerapp ingress traffic set -g rg-orders-prod -n orders-api \
      --revision-weight "orders-api--g${GITHUB_SHA::7}=100"
```

**🔍 Explained:**

- **A canary** exposes a small percentage of real users to the new version. If metrics stay
  healthy, increase the share. If not, abort and only that small percentage was affected.
- **ADO's `canary` strategy** creates a separate `-canary` deployment and adjusts replica
  counts. `postRouteTraffic` is where you wait and check metrics. `on.failure`/`on.success`
  reject or promote.
- **Lambda aliases** split invocations between two versions by weight. CodeDeploy shifts them
  automatically and rolls back on CloudWatch alarms.
- **Container Apps** needs **multiple revision mode** so several revisions can receive traffic.

**⚠️ Gotchas:**

- **ADO canary with plain Kubernetes** splits traffic by **replica count**, which is
  approximate. Precise percentages need a service mesh (SMI/Istio/Linkerd) or **Argo Rollouts**.
- **A canary without automated metric checks** is just a slow rolling deploy. Define the
  success criteria (error rate, p95 latency) up front.

---

## Scenario 33 — Database migrations in the pipeline

**🎯 Goal:** Apply schema changes **once**, **before** the new app version starts, and stop
the deploy if the migration fails.

```
 build ─► migrate DB (one job) ─► deploy app ─► smoke test
```

### The expand → contract rule (zero-downtime schema changes)

| Release | DB change | App change |
|---------|-----------|-----------|
| N | **Expand:** add new column `phone_e164` (nullable) | Writes both old & new columns |
| N+1 | Backfill data | Reads new column |
| N+2 | **Contract:** drop old column `phone` | Old column no longer used |

Never rename or drop a column in the same release that stops using it. During rolling,
blue/green or canary deploys, **old and new app versions run at the same time**.

### GitHub Actions

```yaml
  migrate:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Run Flyway migrations
        env:
          FLYWAY_URL: ${{ secrets.DB_JDBC_URL }}
          FLYWAY_USER: ${{ secrets.DB_MIGRATOR_USER }}
          FLYWAY_PASSWORD: ${{ secrets.DB_MIGRATOR_PASSWORD }}
        run: |
          docker run --rm -v "$PWD/db/migrations:/flyway/sql" \
            -e FLYWAY_URL -e FLYWAY_USER -e FLYWAY_PASSWORD \
            flyway/flyway:10 -connectRetries=10 migrate
  deploy:
    needs: migrate
    # ... deploy job as in previous scenarios
```

### Azure DevOps

```yaml
- stage: Migrate
  dependsOn: Build
  variables:
    - group: orders-prod-db          # linked to Key Vault: DbJdbcUrl, DbMigratorUser, DbMigratorPassword
  jobs:
    - deployment: Migrate
      environment: orders-prod
      pool: { vmImage: ubuntu-latest }
      strategy:
        runOnce:
          deploy:
            steps:
              - checkout: self
              - bash: |
                  docker run --rm -v "$(System.DefaultWorkingDirectory)/db/migrations:/flyway/sql" \
                    -e FLYWAY_URL -e FLYWAY_USER -e FLYWAY_PASSWORD \
                    flyway/flyway:10 -connectRetries=10 migrate
                env:
                  FLYWAY_URL: $(DbJdbcUrl)
                  FLYWAY_USER: $(DbMigratorUser)
                  FLYWAY_PASSWORD: $(DbMigratorPassword)
- stage: DeployApp
  dependsOn: Migrate
  # ...
```

### AWS CodeBuild (project inside the VPC so it can reach RDS)

```yaml
version: 0.2
env:
  secrets-manager:
    DB_USER: prod/orders/db-migrator:username
    DB_PASSWORD: prod/orders/db-migrator:password
    DB_HOST: prod/orders/db-migrator:host
phases:
  build:
    commands:
      - >
        docker run --rm -v "$CODEBUILD_SRC_DIR/db/migrations:/flyway/sql"
        -e FLYWAY_URL="jdbc:postgresql://${DB_HOST}:5432/orders"
        -e FLYWAY_USER="$DB_USER" -e FLYWAY_PASSWORD="$DB_PASSWORD"
        flyway/flyway:10 -connectRetries=10 migrate
```

**⚠️ Gotchas:**

- **Private databases aren't reachable from hosted runners.** Use self-hosted agents in the
  VNet, a CodeBuild project with **VPC configuration**, or run the migration as a Kubernetes
  Job inside the cluster.
- **Use a dedicated migrator account** with DDL rights. The app's runtime account should only
  have read/write (DML) rights.
- **Take a backup or snapshot before destructive migrations,** and test migrations against a
  copy of production data in staging. Lock-heavy migrations on big tables cause outages.

---

## Scenario 34 — GitOps with Argo CD or Flux

**🎯 Goal:** The pipeline **doesn't** touch the cluster at all. It builds the image and
**commits the new tag to a config repo**. **Argo CD** (or Flux), running *inside* the cluster,
sees the commit and syncs the cluster to match Git.

```
 app repo ──CI──► build image ──► commit "orders-api: 3f2c1ab" to config repo
                                                    │
                       Argo CD (in cluster) ◄──watches──┘ ──► applies to cluster
```

**Why:** the cluster's desired state is in Git (auditable, revertible with `git revert`). CI
needs **no cluster credentials**, and drift is auto-corrected.

### GitHub Actions — bump the tag in the config repo (GitHub App token)

```yaml
  update-gitops:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Get a short-lived token for the config repo
        id: app-token
        uses: actions/create-github-app-token@v1
        with:
          app-id: ${{ vars.GITOPS_APP_ID }}
          private-key: ${{ secrets.GITOPS_APP_PRIVATE_KEY }}
          repositories: platform-config
      - uses: actions/checkout@v4
        with:
          repository: acme/platform-config
          token: ${{ steps.app-token.outputs.token }}
      - name: Bump image tag (dev overlay)
        run: |
          cd apps/orders-api/overlays/dev
          kustomize edit set image orders-api=acmeprodacr.azurecr.io/orders-api:${{ github.sha }}
          git config user.name "gitops-bot"
          git config user.email "gitops-bot@users.noreply.github.com"
          git commit -am "orders-api(dev): deploy ${{ github.sha }}"
          git push
```

### Azure DevOps — second repo as a resource

```yaml
resources:
  repositories:
    - repository: config
      type: git
      name: Platform/platform-config

steps:
  - checkout: config
    persistCredentials: true           # keep the token so we can push
  - bash: |
      cd apps/orders-api/overlays/dev
      kustomize edit set image orders-api=acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion)
      git config user.email "pipeline@acme.com" && git config user.name "Azure Pipelines"
      git commit -am "orders-api(dev): deploy $(Build.SourceVersion)"
      git push origin HEAD:main
    workingDirectory: $(Build.SourcesDirectory)
```

> The project's **Build Service** identity needs **Contribute** permission on `platform-config`.

### AWS CodeBuild — token from Secrets Manager

```yaml
version: 0.2
env:
  secrets-manager:
    GITOPS_TOKEN: ci/gitops:token
phases:
  build:
    commands:
      - TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)
      - git clone "https://x-access-token:${GITOPS_TOKEN}@github.com/acme/platform-config.git"
      - cd platform-config/apps/orders-api/overlays/dev
      - kustomize edit set image "orders-api=123456789012.dkr.ecr.eu-west-1.amazonaws.com/orders-api:${TAG}"
      - git config user.email "codebuild@acme.com" && git config user.name "CodeBuild"
      - git commit -am "orders-api(dev): deploy ${TAG}"
      - git push
```

**⚠️ Gotchas:**

- **Promotion to prod** is usually a **PR** to the prod overlay (reviewed and approved), not a
  direct push. The PR approval *is* the change approval.
- **Two pipelines pushing to the config repo at once** gives `rejected — fetch first`. Add a
  `git pull --rebase` retry loop, or serialise runs with concurrency.
- **Use Argo CD Image Updater / Flux image automation** if you'd rather the cluster tooling
  detect new tags itself.

---

## Scenario 35 — Post-deploy smoke tests and automatic rollback

**🎯 Goal:** After deploying, hit the key endpoints. If they fail, **roll back automatically**
and fail the pipeline loudly.

### GitHub Actions (Kubernetes)

```yaml
      - name: Deploy
        run: |
          kubectl -n orders set image deployment/orders-api orders-api=acmeprodacr.azurecr.io/orders-api:${{ github.sha }}
          kubectl -n orders rollout status deployment/orders-api --timeout=5m

      - name: Smoke tests
        id: smoke
        run: |
          set -e
          curl -fsS --retry 5 --retry-delay 5 https://orders.acme.com/health
          curl -fsS https://orders.acme.com/api/v1/orders?limit=1 -H "Authorization: Bearer ${{ secrets.SMOKE_TOKEN }}" > /dev/null

      - name: Roll back on failure
        if: failure()
        run: |
          echo "::error::Smoke tests failed — rolling back"
          kubectl -n orders rollout undo deployment/orders-api
          kubectl -n orders rollout status deployment/orders-api --timeout=5m
```

### Azure DevOps (`on: failure` hook of a deployment job)

```yaml
- deployment: DeployProd
  environment: orders-prod
  pool: { vmImage: ubuntu-latest }
  strategy:
    runOnce:
      deploy:
        steps:
          - script: ./scripts/deploy.sh $(Build.SourceVersion)
      postRouteTraffic:
        steps:
          - script: ./scripts/smoke-test.sh https://orders.acme.com
      on:
        failure:
          steps:
            - script: ./scripts/rollback.sh
              displayName: Automatic rollback
```

### AWS (ECS/CodeDeploy alarm-based rollback)

Configure the CodeDeploy **deployment group** (or the ECS circuit breaker) to roll back
automatically:

```yaml
DeploymentGroup:
  Type: AWS::CodeDeploy::DeploymentGroup
  Properties:
    # ...
    AutoRollbackConfiguration:
      Enabled: true
      Events: [DEPLOYMENT_FAILURE, DEPLOYMENT_STOP_ON_ALARM]
    AlarmConfiguration:
      Enabled: true
      Alarms:
        - Name: orders-api-5xx-high
        - Name: orders-api-p95-latency-high
```

And for an explicit smoke test in a CodeBuild "verify" stage:

```yaml
version: 0.2
phases:
  build:
    commands:
      - curl -fsS --retry 5 --retry-delay 5 https://orders.acme.com/health
      - ./scripts/smoke-test.sh https://orders.acme.com
```

**⚠️ Gotchas:**

- **Automatic rollback of the app does NOT roll back database migrations.** That's another
  reason for backward-compatible (expand/contract) schema changes.
- **Smoke tests must be safe to run against production**: read-only, or using clearly marked
  test data.

---

## Scenario 36 — Manual rollback to a previous version

**🎯 Goal:** At 3 a.m. the new version misbehaves. On-call needs to redeploy the previous
known-good version in **under 5 minutes**, without rebuilding anything.

### GitHub Actions — manual workflow with a version input

```yaml
name: Rollback
on:
  workflow_dispatch:
    inputs:
      version:
        description: "Image tag (git SHA) to roll back to"
        required: true
        type: string
      environment:
        description: "Target environment"
        required: true
        type: choice
        options: [staging, production]

permissions:
  id-token: write
  contents: read

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - name: Verify the image exists before doing anything
        env:
          VERSION: ${{ inputs.version }}
        run: az acr repository show --name acmeprodacr --image "orders-api:${VERSION}"
      - uses: azure/aks-set-context@v4
        with: { resource-group: rg-aks-prod, cluster-name: aks-prod }
      - name: Roll back
        env:
          VERSION: ${{ inputs.version }}
        run: |
          helm upgrade orders-api charts/orders-api -n orders --reuse-values \
            --set image.tag="${VERSION}" --atomic --wait --timeout 5m
```

### Azure DevOps

- **Option 1 (built in):** open a **previous successful run** → the Deploy stage →
  **"Rerun stage"**. It redeploys that run's artifacts. Environment history shows which run is
  in each environment.
- **Option 2:** a rollback pipeline with a runtime parameter:

```yaml
parameters:
  - name: version
    displayName: Image tag to roll back to
    type: string

trigger: none

stages:
  - stage: Rollback
    jobs:
      - deployment: Rollback
        environment: orders-prod
        pool: { vmImage: ubuntu-latest }
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self
                - task: AzureCLI@2
                  inputs:
                    azureSubscription: arm-orders-prod
                    scriptType: bash
                    scriptLocation: inlineScript
                    inlineScript: |
                      az aks get-credentials -g rg-aks-prod -n aks-prod
                      kubelogin convert-kubeconfig -l azurecli
                      helm upgrade orders-api charts/orders-api -n orders --reuse-values \
                        --set image.tag='${{ parameters.version }}' --atomic --wait
```

### AWS

- **CodePipeline:** pick an earlier execution → **"Rollback"** on the stage (V2 pipelines
  support stage rollback to a previous successful execution's artifacts).
- **ECS:** point the service back at the previous task definition revision:

```bash
aws ecs update-service --cluster prod-cluster --service orders-api --task-definition orders-api:41
aws ecs wait services-stable --cluster prod-cluster --services orders-api
```

- **Helm:** `helm rollback orders-api 0 -n orders` (`0` = the previous revision).
- **Kubernetes:** `kubectl rollout undo deployment/orders-api -n orders`.

**⚠️ Gotchas:**

- **Rollback only works if old artifacts still exist.** Registry retention/cleanup policies
  must keep at least the last N production images.
- **`kubectl rollout undo` / console changes cause drift.** If GitOps or the pipeline
  redeploys afterwards, the bad version comes back. Revert in Git too.
- **Practise rollbacks** in a game day. The middle of an incident is a bad time to discover the
  rollback workflow has a typo.

---

**Next:** [04 — Infrastructure as Code Pipelines ➡️](04-iac.md)
