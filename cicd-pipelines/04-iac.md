# 04 — Infrastructure as Code (IaC) Pipelines (Scenarios 37–44)

[⬅️ Back to Index](README.md) · [⬅️ Previous: Deployments](03-deployments.md)

---

## 🧾 What is IaC, and why pipelines? (plain English)

**Infrastructure as Code** means describing cloud resources (networks, databases, Kubernetes
clusters) in text files instead of clicking around the portal.

| Tool | Cloud | Language | "Preview" command | "Apply" command |
|------|-------|----------|-------------------|-----------------|
| **Terraform / OpenTofu** | Any | HCL (`.tf`) | `terraform plan` | `terraform apply` |
| **Bicep** | Azure | `.bicep` | `az deployment group what-if` | `az deployment group create` |
| **CloudFormation** | AWS | YAML/JSON | change set | execute change set |
| **AWS CDK** | AWS | TypeScript/Python/… → CloudFormation | `cdk diff` | `cdk deploy` |

Why run IaC in pipelines instead of from laptops:

- Every change is **reviewed** (PR) and its **preview** (plan) is visible before anything changes.
- **One** controlled identity has write access to production, not every engineer's laptop.
- A full **audit trail**: who changed what, when, and why.

### The golden IaC pipeline pattern

```
 PR opened ──► fmt / validate / lint / security scan ──► PLAN ──► post plan as a PR comment
                                                                         │ (human review)
 PR merged ──► PLAN again (save plan file) ──► ⏸ APPROVAL ──► APPLY *that exact plan file*
```

> ⚠️ **Rule:** apply the **saved plan** that was approved, not a fresh `apply` that might
> include changes made since someone looked at it.

---

## Table of Contents

| # | Scenario | Tool / platform |
|---|----------|-----------------|
| 37 | [Terraform on GitHub Actions: plan on PR (comment), apply on merge](#scenario-37--terraform-on-github-actions) | Terraform → Azure |
| 38 | [Terraform on Azure DevOps: plan artifact → approval → apply](#scenario-38--terraform-on-azure-devops) | Terraform → Azure |
| 39 | [Terraform on AWS CodeBuild/CodePipeline: S3 state, approval](#scenario-39--terraform-on-aws-codebuild-and-codepipeline) | Terraform → AWS |
| 40 | [Bicep: what-if on PR, deploy on merge](#scenario-40--bicep-what-if-and-deploy) | Bicep (GitHub & ADO) |
| 41 | [CloudFormation change sets with approval](#scenario-41--cloudformation-change-sets) | CloudFormation |
| 42 | [AWS CDK pipeline](#scenario-42--aws-cdk-pipeline) | CDK |
| 43 | [Scheduled drift detection](#scenario-43--scheduled-drift-detection) | All three |
| 44 | [Multi-environment Terraform layout & promotion](#scenario-44--multi-environment-terraform) | Terraform patterns |

---

## Scenario 37 — Terraform on GitHub Actions

**🎯 Goal:**

- **On PR:** `fmt` check, `validate`, `plan`, and post the plan as a PR comment.
- **On merge to `main`:** plan again, wait for approval (the `production` environment), and
  apply exactly that plan.
- Auth to Azure via **OIDC**, with remote state in an **Azure Storage** account.

`backend.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "acmetfstate"
    container_name       = "tfstate"
    key                  = "orders/prod.tfstate"
    use_oidc             = true          # authenticate with the pipeline's OIDC token
    use_azuread_auth     = true          # use Entra ID RBAC instead of storage keys
  }
}
```

`.github/workflows/terraform.yml`:

```yaml
name: Terraform
on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

permissions:
  id-token: write
  contents: read
  pull-requests: write

env:
  ARM_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID }}
  ARM_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
  ARM_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
  ARM_USE_OIDC: "true"
  TF_IN_AUTOMATION: "true"
  TF_INPUT: "false"

defaults:
  run:
    working-directory: infra

concurrency:
  group: terraform-prod            # never run two plans/applies against the same state at once
  cancel-in-progress: false

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.8
          terraform_wrapper: false

      - name: Format check
        run: terraform fmt -check -recursive

      - name: Init
        run: terraform init

      - name: Validate
        run: terraform validate

      - name: Plan
        id: plan
        run: |
          terraform plan -out=tfplan -no-color | tee plan.txt
          # keep the comment readable: GitHub comments max out at ~65k chars
          tail -c 60000 plan.txt > plan-trimmed.txt

      - name: Comment plan on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('infra/plan-trimmed.txt', 'utf8');
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `### Terraform plan 📋\n<details><summary>Show plan</summary>\n\n\`\`\`terraform\n${plan}\n\`\`\`\n</details>`
            });

      - name: Save plan for the apply job
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: |
            infra/tfplan
            infra/.terraform.lock.hcl
          retention-days: 3

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production         # ⏸ required reviewers approve here
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.8
      - uses: actions/download-artifact@v4
        with: { name: tfplan, path: infra }
      - run: terraform init
      - name: Apply the reviewed plan
        run: terraform apply -auto-approve tfplan
```

**🔍 Explained:**

- **`ARM_*` env vars + `ARM_USE_OIDC=true`** tell the AzureRM provider *and* the backend to log
  in with the GitHub OIDC token. No client secret.
- **`terraform fmt -check`** fails if the files aren't formatted in the standard way. It's
  cheap, and it stops style arguments in PRs.
- **`-out=tfplan`** saves a binary plan. **`apply tfplan`** applies exactly that plan. If the
  state changed in the meantime, Terraform refuses ("Saved plan is stale"), which is safe.
- **`.terraform.lock.hcl`** pins provider versions, so the apply job uses the same providers as the plan.
- **`concurrency` without cancellation** queues runs. Cancelling a running `apply` midway can
  corrupt state or leave a stuck lock.
- **`terraform_wrapper: false`:** setup-terraform's wrapper captures stdout. Turning it off
  keeps `tee` and exit codes behaving normally.

**⚠️ Gotchas:**

- **Plan files contain secrets in plain text** (any sensitive values in resources). Keep
  artifact retention short and restrict who can download artifacts.
- **Fork PRs get no secrets or OIDC**, so plan fails for forks. That's expected. Run plans for
  internal branches only, or use a read-only plan identity.
- **Use separate identities:** the PR plan identity should be **Reader** (+ state read).
  Only the apply job (protected environment) gets **Contributor**. Separate federated
  credentials per environment make this possible.
- **State locking:** azurerm backends lock using blob leases. A killed run can leave a lease
  behind. `terraform force-unlock <ID>` fixes it, but only after confirming nothing else is running.

---

## Scenario 38 — Terraform on Azure DevOps

**🎯 Goal:** Same flow on Azure DevOps, using a **workload identity federation** service
connection, with an approval check on the `infra-prod` environment.

```yaml
trigger:
  branches: { include: [main] }
  paths: { include: [infra/*] }

pr:
  paths: { include: [infra/*] }

variables:
  tfVersion: 1.9.8
  workingDir: $(System.DefaultWorkingDirectory)/infra
  serviceConnection: arm-infra-prod

stages:
  - stage: Plan
    jobs:
      - job: Plan
        pool: { vmImage: ubuntu-latest }
        steps:
          - task: TerraformInstaller@1          # from the Microsoft DevLabs Terraform extension
            inputs:
              terraformVersion: $(tfVersion)

          - task: AzureCLI@2
            displayName: Terraform init/validate/plan
            inputs:
              azureSubscription: $(serviceConnection)
              scriptType: bash
              scriptLocation: inlineScript
              addSpnToEnvironment: true         # exposes $servicePrincipalId, $tenantId, $idToken
              workingDirectory: $(workingDir)
              inlineScript: |
                set -euo pipefail
                export ARM_CLIENT_ID=$servicePrincipalId
                export ARM_TENANT_ID=$tenantId
                export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
                export ARM_OIDC_TOKEN=$idToken
                export ARM_USE_OIDC=true
                terraform fmt -check -recursive
                terraform init -input=false
                terraform validate
                terraform plan -input=false -out=tfplan -no-color | tee plan.txt

          - task: PublishPipelineArtifact@1
            condition: and(succeeded(), ne(variables['Build.Reason'], 'PullRequest'))
            inputs:
              targetPath: $(workingDir)
              artifact: tfplan

  - stage: Apply
    dependsOn: Plan
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'), ne(variables['Build.Reason'], 'PullRequest'))
    jobs:
      - deployment: Apply
        pool: { vmImage: ubuntu-latest }
        environment: infra-prod                 # ⏸ approval configured on this environment
        strategy:
          runOnce:
            deploy:
              steps:
                - task: TerraformInstaller@1
                  inputs:
                    terraformVersion: $(tfVersion)
                - task: AzureCLI@2
                  displayName: Terraform apply (saved plan)
                  inputs:
                    azureSubscription: $(serviceConnection)
                    scriptType: bash
                    scriptLocation: inlineScript
                    addSpnToEnvironment: true
                    workingDirectory: $(Pipeline.Workspace)/tfplan
                    inlineScript: |
                      set -euo pipefail
                      export ARM_CLIENT_ID=$servicePrincipalId
                      export ARM_TENANT_ID=$tenantId
                      export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
                      export ARM_OIDC_TOKEN=$idToken
                      export ARM_USE_OIDC=true
                      terraform init -input=false
                      terraform apply -input=false -auto-approve tfplan
```

**🔍 Explained:**

- **`addSpnToEnvironment: true`** — with a workload identity federation connection, the task
  exposes the federated **ID token** as `$idToken`. Terraform uses it via `ARM_OIDC_TOKEN`.
- **The whole `infra` folder (including `.terraform/`) is published as the artifact,** so the
  apply stage has the plan, the lock file and the initialised modules.
- **The Apply stage condition** skips it for PR builds and non-main branches.

**⚠️ Gotchas:**

- **The ID token expires** (roughly an hour). Very long applies can fail with auth errors
  midway. Split huge stacks into smaller ones.
- **Publishing `.terraform/`** includes provider binaries (hundreds of MB). Some teams publish
  only `tfplan` + the lock file and re-run `init` in Apply (as in Scenario 37).
- **Marketplace Terraform tasks** (`TerraformTaskV4@4`) also exist. They're fine, but plain
  CLI commands are easier to debug and to port to other CI systems.

---

## Scenario 39 — Terraform on AWS CodeBuild and CodePipeline

**🎯 Goal:** Terraform for AWS with **S3 state + locking**, run by two CodeBuild projects (plan
and apply) and a **manual approval** in CodePipeline.

`backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket       = "acme-tfstate-prod"
    key          = "orders/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true      # S3-native locking (Terraform 1.10+). Older versions: dynamodb_table = "tf-locks"
  }
}
```

`buildspec-plan.yml`:

```yaml
version: 0.2

env:
  variables:
    TF_VERSION: 1.10.3
    TF_IN_AUTOMATION: "true"
    TF_INPUT: "false"

phases:
  install:
    commands:
      - curl -fsSLo tf.zip "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip"
      - unzip -o tf.zip -d /usr/local/bin && rm tf.zip
      - terraform version
  build:
    commands:
      - cd infra
      - terraform fmt -check -recursive
      - terraform init
      - terraform validate
      - terraform plan -out=tfplan -no-color | tee plan.txt

artifacts:
  base-directory: infra
  files:
    - "**/*"                 # code + .terraform.lock.hcl + tfplan for the apply stage
```

`buildspec-apply.yml`:

```yaml
version: 0.2
env:
  variables:
    TF_VERSION: 1.10.3
phases:
  install:
    commands:
      - curl -fsSLo tf.zip "https://releases.hashicorp.com/terraform/${TF_VERSION}/terraform_${TF_VERSION}_linux_amd64.zip"
      - unzip -o tf.zip -d /usr/local/bin && rm tf.zip
  build:
    commands:
      # the input artifact (the plan stage's output) is the working directory here
      - terraform init
      - terraform apply -auto-approve tfplan
```

CodePipeline stages (CloudFormation excerpt):

```yaml
- Name: Plan
  Actions:
    - Name: TerraformPlan
      ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
      Configuration: { ProjectName: !Ref TfPlanProject }         # uses buildspec-plan.yml, read-only role
      InputArtifacts: [{ Name: SourceOutput }]
      OutputArtifacts: [{ Name: PlanOutput }]
- Name: Approve
  Actions:
    - Name: ReviewPlan
      ActionTypeId: { Category: Approval, Owner: AWS, Provider: Manual, Version: "1" }
      Configuration:
        CustomData: "Review plan.txt in the TerraformPlan build logs before approving"
        ExternalEntityLink: !Sub "https://${AWS::Region}.console.aws.amazon.com/codesuite/codebuild/projects/${TfPlanProject}/history"
- Name: Apply
  Actions:
    - Name: TerraformApply
      ActionTypeId: { Category: Build, Owner: AWS, Provider: CodeBuild, Version: "1" }
      Configuration: { ProjectName: !Ref TfApplyProject }        # uses buildspec-apply.yml, admin-ish role
      InputArtifacts: [{ Name: PlanOutput }]
```

**🔍 Explained:**

- **`use_lockfile = true`** makes Terraform lock state with a `.tflock` object in S3 (newer
  versions). Older setups use a DynamoDB table. Either way, two runs can't modify state at once.
- **The plan project's IAM role is read-only** (plus state bucket access). The apply project's
  role has write permissions. That split is least privilege.
- **The plan stage's output artifact** (code + plan) becomes the apply stage's input, so the
  approved plan is exactly what gets applied.

**⚠️ Gotchas:**

- **CodePipeline artifacts are zipped into S3,** and file permissions/symlinks can get lost.
  Provider binaries inside `.terraform/` may lose their execute bit, so always run
  `terraform init` again in apply (as above).
- **Turn on versioning and encryption for the state bucket, and block public access.** State
  files contain secrets and are your only record of what Terraform manages.

---

## Scenario 40 — Bicep what-if and deploy

**🎯 Goal:** On PR, show **what would change** in Azure (`what-if`). On merge, deploy.

`infra/main.bicep` + `infra/main.prod.bicepparam` (parameter file).

### GitHub Actions

```yaml
name: Bicep
on:
  pull_request:
    paths: ["infra/**"]
  push:
    branches: [main]
    paths: ["infra/**"]

permissions:
  id-token: write
  contents: read
  pull-requests: write

jobs:
  validate-whatif:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - name: Lint (bicep build)
        run: az bicep build --file infra/main.bicep --stdout > /dev/null
      - name: What-if
        run: |
          az deployment group what-if \
            --resource-group rg-orders-prod \
            --template-file infra/main.bicep \
            --parameters infra/main.prod.bicepparam \
            --no-prompt | tee whatif.txt
          cat whatif.txt >> "$GITHUB_STEP_SUMMARY"     # show the result on the run summary page

  deploy:
    needs: validate-whatif
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - name: Deploy
        run: |
          az deployment group create \
            --name "orders-${{ github.run_number }}" \
            --resource-group rg-orders-prod \
            --template-file infra/main.bicep \
            --parameters infra/main.prod.bicepparam
```

### Azure DevOps

```yaml
stages:
  - stage: WhatIf
    jobs:
      - job: WhatIf
        pool: { vmImage: ubuntu-latest }
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: arm-orders-prod
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                az bicep build --file infra/main.bicep --stdout > /dev/null
                az deployment group what-if -g rg-orders-prod \
                  -f infra/main.bicep -p infra/main.prod.bicepparam --no-prompt

  - stage: Deploy
    dependsOn: WhatIf
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: Deploy
        pool: { vmImage: ubuntu-latest }
        environment: infra-prod
        strategy:
          runOnce:
            deploy:
              steps:
                - checkout: self
                - task: AzureResourceManagerTemplateDeployment@3
                  inputs:
                    deploymentScope: Resource Group
                    azureResourceManagerConnection: arm-orders-prod
                    subscriptionId: $(subscriptionId)
                    action: Create Or Update Resource Group
                    resourceGroupName: rg-orders-prod
                    location: westeurope
                    templateLocation: Linked artifact
                    csmFile: infra/main.bicep
                    csmParametersFile: infra/main.prod.bicepparam
                    deploymentMode: Incremental
                    deploymentName: orders-$(Build.BuildId)
```

**🔍 Explained:**

- **`what-if`** is Bicep's "plan": it lists resources to be created (+), modified (~) or deleted (−).
- **Bicep has no state file.** Azure itself is the state. Deployments are **incremental** by
  default: resources not in the template are left alone.
- **Unique `--name` per deployment** keeps deployment history readable (Resource group →
  Deployments).

**⚠️ Gotchas:**

- **`Complete` deployment mode deletes everything in the resource group that isn't in the
  template.** Never use it casually.
- **what-if produces "noise"** (properties shown as changing when they aren't). Teach
  reviewers to focus on creates and deletes.
- **Deployment stacks** (`az stack group create`) add delete protection and cleanup of removed
  resources. Consider them for new projects.

---

## Scenario 41 — CloudFormation change sets

**🎯 Goal:** Create a **change set** (CloudFormation's preview), let a human review it, then execute it.

### AWS CodePipeline — native CloudFormation actions

```yaml
- Name: Preview
  Actions:
    - Name: CreateChangeSet
      ActionTypeId: { Category: Deploy, Owner: AWS, Provider: CloudFormation, Version: "1" }
      Configuration:
        ActionMode: CHANGE_SET_REPLACE
        StackName: orders-network-prod
        ChangeSetName: pipeline-changeset
        TemplatePath: SourceOutput::cfn/network.yaml
        TemplateConfiguration: SourceOutput::cfn/network.prod.json   # parameters + tags
        Capabilities: CAPABILITY_IAM,CAPABILITY_NAMED_IAM
        RoleArn: !GetAtt CfnDeployRole.Arn                         # role CloudFormation itself assumes
      InputArtifacts: [{ Name: SourceOutput }]
- Name: Approve
  Actions:
    - Name: ReviewChangeSet
      ActionTypeId: { Category: Approval, Owner: AWS, Provider: Manual, Version: "1" }
      Configuration:
        CustomData: "Review change set 'pipeline-changeset' on stack orders-network-prod"
- Name: Execute
  Actions:
    - Name: ExecuteChangeSet
      ActionTypeId: { Category: Deploy, Owner: AWS, Provider: CloudFormation, Version: "1" }
      Configuration:
        ActionMode: CHANGE_SET_EXECUTE
        StackName: orders-network-prod
        ChangeSetName: pipeline-changeset
```

`cfn/network.prod.json`:

```json
{
  "Parameters": { "Environment": "prod", "VpcCidr": "10.20.0.0/16" },
  "Tags": { "owner": "platform", "cost-center": "1234" }
}
```

### GitHub Actions

```yaml
jobs:
  changeset:
    runs-on: ubuntu-latest
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-cfn
          aws-region: eu-west-1
      - name: Lint template
        run: pip install cfn-lint && cfn-lint cfn/network.yaml
      - name: Create change set (no execute) and show it
        run: |
          aws cloudformation deploy \
            --stack-name orders-network-prod \
            --template-file cfn/network.yaml \
            --parameter-overrides Environment=prod VpcCidr=10.20.0.0/16 \
            --capabilities CAPABILITY_NAMED_IAM \
            --no-execute-changeset
          CS=$(aws cloudformation list-change-sets --stack-name orders-network-prod \
            --query 'reverse(sort_by(Summaries,&CreationTime))[0].ChangeSetName' --output text)
          aws cloudformation describe-change-set --stack-name orders-network-prod --change-set-name "$CS" \
            --query 'Changes[].ResourceChange.{Action:Action,Resource:LogicalResourceId,Type:ResourceType,Replace:Replacement}' \
            --output table

  execute:
    needs: changeset
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    permissions: { id-token: write, contents: read }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-cfn
          aws-region: eu-west-1
      - name: Deploy
        run: |
          aws cloudformation deploy --stack-name orders-network-prod --template-file cfn/network.yaml \
            --parameter-overrides Environment=prod VpcCidr=10.20.0.0/16 \
            --capabilities CAPABILITY_NAMED_IAM --no-fail-on-empty-changeset
```

**🔍 Explained:**

- **`CHANGE_SET_REPLACE`** creates (or replaces) the change set. **`CHANGE_SET_EXECUTE`** applies it.
- **The `Replacement` column** in the change set is critical. `True` means CloudFormation
  will **delete and recreate** the resource. For a database, that means **data loss**.
- **`RoleArn`** is a service role CloudFormation assumes to make the changes. The pipeline
  itself only needs permission to call CloudFormation and pass this role.

**⚠️ Gotchas:**

- **Stack stuck in `UPDATE_ROLLBACK_FAILED`** blocks every future deploy until fixed with
  `continue-update-rollback` (sometimes skipping resources).
- **Enable termination protection and deletion policies** (`DeletionPolicy: Retain/Snapshot`)
  on stateful resources.

---

## Scenario 42 — AWS CDK pipeline

**🎯 Goal:** The infrastructure is written in TypeScript with **AWS CDK**. Run `cdk diff` on
PRs and `cdk deploy` on merge.

### GitHub Actions

```yaml
name: CDK
on:
  pull_request:
    paths: ["cdk/**"]
  push:
    branches: [main]
    paths: ["cdk/**"]

permissions:
  id-token: write
  contents: read

defaults:
  run:
    working-directory: cdk

jobs:
  diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm, cache-dependency-path: cdk/package-lock.json }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-cdk-readonly
          aws-region: eu-west-1
      - run: npm ci
      - run: npm test                      # CDK assertion/snapshot tests
      - run: npx cdk synth --quiet         # template must synthesise cleanly
      - run: npx cdk diff --all

  deploy:
    needs: diff
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm, cache-dependency-path: cdk/package-lock.json }
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-cdk-deploy
          aws-region: eu-west-1
      - run: npm ci
      - run: npx cdk deploy --all --require-approval never --concurrency 3
```

### AWS CodeBuild

```yaml
version: 0.2
phases:
  install:
    runtime-versions: { nodejs: 20 }
    commands:
      - cd cdk && npm ci
  build:
    commands:
      - npm test
      - npx cdk synth --quiet
      - npx cdk diff --all
      - |
        if [ "$TARGET" = "deploy" ]; then
          npx cdk deploy --all --require-approval never
        fi
```

**🔍 Explained:**

- **`cdk synth`** turns code into CloudFormation templates (`cdk.out/`). `cdk deploy` deploys
  them through CloudFormation.
- **`--require-approval never`** skips the interactive "Do you approve IAM changes?" prompt.
  In CI, the approval happens via the environment protection rule instead.
- **One-time `cdk bootstrap`** per account/region creates the S3 bucket, ECR repo and roles
  that CDK deploys through. Without it: `This stack uses assets, so the toolkit stack must be deployed`.

**⚠️ Gotchas:**

- **CDK Pipelines** (`aws-cdk-lib/pipelines`) is an alternative where CDK defines a
  **self-mutating CodePipeline**. It's powerful but opinionated. Pick one approach per team.
- **CDK deploys assume bootstrap roles** (`cdk-hnb659fds-deploy-role-...`). The CI role needs
  `sts:AssumeRole` on those roles, not broad permissions.

---

## Scenario 43 — Scheduled drift detection

**🎯 Goal:** Someone clicked a change in the portal and now the cloud doesn't match the code
("**drift**"). Detect it nightly and alert the team.

### GitHub Actions — Terraform `-detailed-exitcode` + open an issue

```yaml
name: Drift detection
on:
  schedule:
    - cron: "0 6 * * 1-5"         # weekdays 06:00 UTC
  workflow_dispatch:

permissions:
  id-token: write
  contents: read
  issues: write

jobs:
  drift:
    runs-on: ubuntu-latest
    env:
      ARM_CLIENT_ID: ${{ vars.AZURE_CLIENT_ID_READONLY }}
      ARM_TENANT_ID: ${{ vars.AZURE_TENANT_ID }}
      ARM_SUBSCRIPTION_ID: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      ARM_USE_OIDC: "true"
    defaults:
      run:
        working-directory: infra
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.9.8, terraform_wrapper: false }
      - run: terraform init -input=false
      - name: Plan with detailed exit code
        id: plan
        run: |
          set +e
          terraform plan -detailed-exitcode -no-color -input=false > plan.txt
          echo "exitcode=$?" >> "$GITHUB_OUTPUT"
      - name: Open issue if drift found
        if: steps.plan.outputs.exitcode == '2'
        uses: actions/github-script@v7
        with:
          script: |
            const plan = require('fs').readFileSync('infra/plan.txt','utf8').slice(-60000);
            await github.rest.issues.create({
              owner: context.repo.owner, repo: context.repo.repo,
              title: `⚠️ Infrastructure drift detected (${new Date().toISOString().slice(0,10)})`,
              labels: ['drift'],
              body: '```\n' + plan + '\n```'
            });
      - name: Fail on error
        if: steps.plan.outputs.exitcode == '1'
        run: exit 1
```

### Azure DevOps — scheduled pipeline

```yaml
trigger: none
schedules:
  - cron: "0 6 * * 1-5"
    branches: { include: [main] }
    always: true                       # run even if code hasn't changed (that's the point!)

pool: { vmImage: ubuntu-latest }

steps:
  - task: AzureCLI@2
    inputs:
      azureSubscription: arm-infra-readonly
      scriptType: bash
      scriptLocation: inlineScript
      addSpnToEnvironment: true
      workingDirectory: infra
      inlineScript: |
        export ARM_CLIENT_ID=$servicePrincipalId ARM_TENANT_ID=$tenantId ARM_OIDC_TOKEN=$idToken ARM_USE_OIDC=true
        export ARM_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
        terraform init -input=false
        set +e
        terraform plan -detailed-exitcode -no-color -input=false
        rc=$?
        if [ $rc -eq 2 ]; then echo "##vso[task.logissue type=warning]Drift detected"; echo "##vso[task.complete result=SucceededWithIssues;]"; fi
        if [ $rc -eq 1 ]; then exit 1; fi
```

### AWS — CloudFormation drift detection (CodeBuild on an EventBridge schedule)

```yaml
version: 0.2
phases:
  build:
    commands:
      - |
        for STACK in orders-network-prod orders-data-prod; do
          ID=$(aws cloudformation detect-stack-drift --stack-name "$STACK" --query StackDriftDetectionId --output text)
          while [ "$(aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $ID --query DetectionStatus --output text)" = "DETECTION_IN_PROGRESS" ]; do sleep 5; done
          STATUS=$(aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $ID --query StackDriftStatus --output text)
          echo "$STACK: $STATUS"
          if [ "$STATUS" = "DRIFTED" ]; then
            aws sns publish --topic-arn "$ALERT_TOPIC_ARN" --message "CloudFormation stack $STACK has DRIFTED"
          fi
        done
```

> **AWS Config** rules (e.g. `cloudformation-stack-drift-detection-check`) can do this
> continuously without a pipeline.

**🔍 Explained:**

- **`-detailed-exitcode`:** `0` = no changes, `1` = error, `2` = changes present (drift, or
  un-applied code).
- **`always: true`** (ADO schedules) runs even with no new commits. Drift happens outside Git.
- **Use a read-only identity** for drift checks. They must never change anything.

**⚠️ Gotchas:**

- **Exit code 2 also fires for merged-but-not-yet-applied code.** Make sure applies really
  happen on merge, or the drift alert becomes permanent noise.
- **Fix drift by deciding which side is right:** update the code to match (and `import` if
  needed), or re-apply the code to revert the manual change.

---

## Scenario 44 — Multi-environment Terraform

**🎯 Goal:** dev, staging and prod built from the **same modules**, with different sizes and
settings and **separate state files**. Changes are promoted dev → staging → prod.

### Recommended layout (directory per environment)

```
infra/
├── modules/
│   └── orders-stack/           # reusable module (vnet, aks, db, …)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── envs/
    ├── dev/
    │   ├── main.tf             # module "orders" { source = "../../modules/orders-stack"  sku = "small" }
    │   ├── backend.tf          # key = "orders/dev.tfstate"
    │   └── terraform.tfvars
    ├── staging/  (same shape)
    └── prod/     (same shape, key = "orders/prod.tfstate")
```

### GitHub Actions — matrix plan, sequential apply

```yaml
jobs:
  plan:
    strategy:
      fail-fast: false
      matrix:
        env: [dev, staging, prod]
    runs-on: ubuntu-latest
    environment: ${{ matrix.env }}-plan          # per-env READ-ONLY identity
    defaults:
      run:
        working-directory: infra/envs/${{ matrix.env }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with: { terraform_version: 1.9.8 }
      - run: terraform init -input=false && terraform plan -input=false -no-color

  apply-dev:
    needs: plan
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/_tf-apply.yml
    with: { env: dev }
    secrets: inherit
  apply-staging:
    needs: apply-dev
    uses: ./.github/workflows/_tf-apply.yml
    with: { env: staging }
    secrets: inherit
  apply-prod:
    needs: apply-staging
    uses: ./.github/workflows/_tf-apply.yml       # environment "prod" has required reviewers
    with: { env: prod }
    secrets: inherit
```

**🔍 Explained:**

- **Directory per environment** is explicit and easy to review. Each environment has its own
  backend key, so a broken dev apply can't touch prod state.
- **The module version** can be pinned per environment
  (`source = "git::https://.../modules.git//orders-stack?ref=v1.4.0"`) to promote module
  versions gradually.
- **Terraform workspaces** (`terraform workspace select prod`) are an alternative, but it's
  easy to apply to the wrong workspace. Many teams prefer directories.

**⚠️ Gotchas:**

- **Copy-paste drift between `envs/*`:** keep the env folders thin (just module calls and
  tfvars). All logic belongs in modules.
- **One giant state for everything** = slow plans, a big blast radius and lock contention.
  Split state by lifecycle (network, data, apps).

---

**Next:** [05 — DevSecOps & Pipeline Security ➡️](05-devsecops.md)
