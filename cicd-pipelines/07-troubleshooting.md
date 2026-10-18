# 07 — Troubleshooting, Debugging & Gotchas Reference

[⬅️ Back to Index](README.md) · [⬅️ Previous: Advanced Patterns](06-advanced-patterns.md)

---

> Keep this page open when a pipeline goes red. Look for the error message in the tables below.
> If it's not there, follow the debugging playbook in §7.5.

## Table of Contents

- [7.1 Errors that happen on every platform](#71-errors-that-happen-on-every-platform)
- [7.2 GitHub Actions — errors & fixes](#72-github-actions--errors-and-fixes)
- [7.3 Azure DevOps — errors & fixes](#73-azure-devops--errors-and-fixes)
- [7.4 AWS CodeBuild / CodePipeline — errors & fixes](#74-aws-codebuild--codepipeline--errors-and-fixes)
- [7.5 The debugging playbook](#75-the-debugging-playbook)
- [7.6 Turning on debug logging](#76-turning-on-debug-logging)
- [7.7 Running pipelines locally](#77-running-pipelines-locally)
- [7.8 Cost optimisation](#78-cost-optimisation)
- [7.9 Choosing a platform](#79-choosing-a-platform)
- [7.10 Interview-style questions to test yourself](#710-interview-style-questions-to-test-yourself)

---

## 7.1 Errors that happen on every platform

| Symptom / message | Likely cause | Fix |
|-------------------|--------------|-----|
| `Permission denied` running `./script.sh` | Execute bit lost (often from Windows commits) | `git update-index --chmod=+x script.sh` or `bash script.sh` |
| `/bin/bash^M: bad interpreter` | CRLF line endings | `.gitattributes`: `*.sh text eol=lf`, then re-commit |
| Works locally, fails in CI | Different tool versions; missing env var; local cache hiding the problem | Pin versions (`.nvmrc`, `go.mod`, `global.json`); print `tool --version` in CI |
| `npm ci` fails: lock file out of sync | `package.json` changed without updating the lock file | Developer runs `npm install` and commits `package-lock.json` |
| Tests pass locally, fail randomly in CI | Flaky tests: timing, shared state, test order, timezones (CI is UTC!) | Fix the test; quarantine with a ticket; don't just add retries forever |
| Step "succeeded" but nothing happened | Script swallowed an error (no `set -e`), or a pipe hid a failure | `set -euo pipefail` at the top of scripts |
| `No space left on device` | Docker images/layers fill the runner disk (~14 GB free on hosted Linux runners) | `docker system prune -af`; remove unused preinstalled SDKs; bigger runner |
| `Killed` / exit code **137** | Out of memory (OOM) | Reduce parallelism (`--max-workers`, `-T1`), `NODE_OPTIONS=--max-old-space-size`, bigger runner |
| `toomanyrequests: You have reached your pull rate limit` | Anonymous Docker Hub pulls | Log in to Docker Hub, or use a mirror/pull-through cache |
| `x509: certificate signed by unknown authority` (self-hosted) | Corporate TLS-inspecting proxy | Install the corporate CA on the agent image (Dockerfile Handbook Ex 114) |
| Deploy succeeded but app is broken | No post-deploy verification | `rollout status` + smoke tests (Chapter 03, Scenario 35) |
| `exec format error` when running the image | Image built for the wrong CPU architecture | Build multi-arch / for the target platform (Chapter 02, Scenario 19) |
| Cache never hits | Cache key includes something that changes every run (timestamp, run ID) | Key on lock-file hashes + OS + tool version only |
| Secret is empty in a script | Not mapped to an env var / not available for this trigger (fork PR) | Map explicitly; check trigger type |
| YAML error on a line that looks fine | Tabs, wrong indentation, unquoted special characters | Validate with an editor schema / `yamllint`; see Chapter 00 §0.7 |

---

## 7.2 GitHub Actions — errors and fixes

| Message / symptom | Cause | Fix |
|-------------------|-------|-----|
| Workflow doesn't start at all | File not in `.github/workflows/`; YAML invalid; trigger branch/path filters don't match | Check the **Actions** tab for "workflow file invalid"; check `on:` filters |
| `Resource not accessible by integration` | `GITHUB_TOKEN` lacks a permission | Add the right `permissions:` (e.g. `pull-requests: write`, `packages: write`) |
| `Error: Unable to get ACTIONS_ID_TOKEN_REQUEST_URL env variable` | OIDC requested without `id-token: write` | Add `permissions: id-token: write` |
| `AADSTS70021: No matching federated identity record found` | OIDC subject mismatch (branch vs environment vs PR) | Make the federated credential subject match exactly (Chapter 05, Scenario 45) |
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | AWS trust policy `sub`/`aud` mismatch | Fix the trust policy conditions; check the role ARN |
| `The job was not started because recent account payments have failed` / spending limit | Billing | Check org billing / spending limits |
| Job queued forever on `self-hosted` | No online runner with **all** requested labels | Check runner labels/status; check runner group access to the repo |
| Secrets empty in PR from a fork | Secrets aren't passed to fork `pull_request` runs by design | Expected; don't use `pull_request_target` to "fix" it |
| `Invalid workflow file … matrix must define at least one vector` | Empty dynamic matrix | Guard the job with `if: … != '[]'` |
| Required status check "Expected — Waiting for status to be reported" | Workflow skipped (path filter) or job name changed | Use an always-running aggregator job (Chapter 01, Scenario 11) |
| `Unable to download artifact(s): Artifact not found` | Different run, wrong name, or expired retention | Pass `run-id` + `github-token` for cross-run downloads; check retention |
| `upload-artifact` fails: "artifact with this name already exists" | v4 artifacts are immutable per name | Unique names per matrix leg, or `overwrite: true` |
| `GITHUB_TOKEN` push doesn't trigger other workflows | Intentional loop prevention | Use a GitHub App / PAT token for that push |
| Scheduled workflow didn't run | Only runs from default branch; disabled after 60 days inactivity (public repos); delayed under load | Push activity / re-enable; don't rely on exact minute |
| `Node.js 16 actions are deprecated` warnings | Old action versions | Bump actions (Dependabot `github-actions` ecosystem) |

---

## 7.3 Azure DevOps — errors and fixes

| Message / symptom | Cause | Fix |
|-------------------|-------|-----|
| `No hosted parallelism has been purchased or granted` | New org without free-tier grant | Request the free grant (form), or buy parallel jobs; or use self-hosted agents |
| `There was a resource authorization issue: "The pipeline is not valid. Job X: Step Y references service connection Z which could not be found / is not authorized"` | First use of a service connection / environment / variable group / agent pool | Click **Permit** on the run, or authorise the pipeline on the resource |
| `##[error]Variable group was not found or is not authorized for use` | Same as above, for Library groups | Library → group → Pipeline permissions |
| Secret variable is empty in script | Secrets aren't auto-mapped to env vars | `env: MY_SECRET: $(MySecret)` |
| `${{ variables.x }}` empty | Compile-time syntax can't see runtime variables | Use `$(x)` or `$[ variables.x ]` |
| Output variable from another job is empty | Missing `isOutput=true`, missing step `name:`, or wrong path syntax | `dependencies.Job.outputs['step.var']` (same stage) / `stageDependencies.Stage.Job.outputs['step.var']` (other stage) |
| Deployment job can't find repo files | Deployment jobs don't check out automatically | Add `- checkout: self` |
| PR build doesn't run for Azure Repos | `pr:` keyword is ignored for Azure Repos Git | Configure **Build validation** branch policy |
| `The template expression … is not valid` / unexpected value | Template parameter types/indentation | Use **"Download full YAML"** from the run (⋮ menu) to see the expanded pipeline |
| Approval never requested | Approvals are on the **environment**, and the job isn't a `deployment` job (or uses another environment name) | Use `deployment:` jobs with the exact environment name |
| `Agent went offline` / job lost | Self-hosted agent crashed, OOM, or VM scaled in mid-job | Check agent diagnostics; agent pool scaling settings |
| `The job running on agent X ran longer than the maximum time of 60 minutes` | Default timeout for hosted agents (free tier/private project) | Set `timeoutInMinutes`, speed up, or buy parallel jobs (6 h max on paid hosted) |
| `Could not find a valid ICU package` (self-hosted Linux agent) | Missing `libicu` | Install the distro's `libicu` package |
| `TF400898: An Internal Error Occurred` on checkout of other repos | Build service lacks access to that repo | Grant **Read** to the project's Build Service identity; check "Protect access to repositories" setting |

---

## 7.4 AWS CodeBuild / CodePipeline — errors and fixes

| Message / symptom | Cause | Fix |
|-------------------|-------|-----|
| `YAML_FILE_ERROR: … buildspec` | Invalid buildspec (indentation, tabs, wrong keys) | Validate YAML; keys are case-sensitive (`pre_build`, not `prebuild`) |
| `Unknown runtime version named 'X' of nodejs` | Runtime not supported by the chosen image | Pick a version from the image's supported runtimes list, or a newer image |
| `Cannot connect to the Docker daemon at unix:///var/run/docker.sock` | **Privileged mode** disabled on the project | Enable privileged mode (needed for Docker builds) |
| `AccessDeniedException` / `not authorized to perform: X` | Service role missing permission | Add the specific action/resource to the role policy; read the full ARN in the message |
| `ACCESS_DENIED: … CLIENT_ERROR: error while downloading key` for secrets | Role can't read Secrets Manager / Parameter Store (or KMS key) | Grant `secretsmanager:GetSecretValue` / `ssm:GetParameters` + `kms:Decrypt` |
| `DOWNLOAD_SOURCE` failed | Connection/permissions to the source repo; CodeConnections not authorised | Re-authorise the GitHub connection (Developer Tools → Connections) |
| `CLIENT_ERROR: RequestError: send request failed … timeout` (VPC builds) | VPC subnet has no route to the internet/AWS APIs | NAT gateway or VPC endpoints (S3, ECR, logs, STS, Secrets Manager) |
| Build "succeeded" though tests failed | Failing command in `post_build` or `finally` doesn't fail the build as you expect; or `|| true` | Put checks in `build`; check `$CODEBUILD_BUILD_SUCCEEDING` |
| `post_build` pushed an image although build failed | `post_build` runs even after a failed `build` | Guard with `if [ "$CODEBUILD_BUILD_SUCCEEDING" != "1" ]; then exit 1; fi` |
| `no basic auth credentials` on `docker push` | ECR login missing, wrong region, or login to wrong registry host | `aws ecr get-login-password --region R \| docker login … <acct>.dkr.ecr.R.amazonaws.com` |
| `name unknown: The repository with name 'x' does not exist` | ECR repo not created | Create via IaC or repository creation templates |
| Artifacts upload empty / `no matching artifact paths found` | `artifacts.files` paths relative to wrong directory | Use `base-directory`; paths are relative to `$CODEBUILD_SRC_DIR` |
| CodePipeline ECS deploy: `Exception while trying to parse the image URI file` | `imagedefinitions.json` malformed or missing | Must be `[{"name":"<container>","imageUri":"<uri>"}]` and listed in artifacts |
| CodeDeploy blue/green: `The ECS service cannot be updated due to an unexpected error` / stuck | Mismatch between taskdef container name/port and appspec, target group issues | Align names/ports; check target group health checks |
| `git describe` fails / no tags | Source downloaded as zip (no `.git`) or shallow clone | Use full clone (`CODEBUILD_CLONE_REF`) / set git clone depth |
| Builds queue for a long time | Account concurrent build quota or project `ConcurrentBuildLimit` | Request quota increase; use reserved capacity fleets |

---

## 7.5 The debugging playbook

When a pipeline fails, work through these steps in order:

```
1. READ the first red error, not the last line.   → The real cause is usually earlier in the log.
2. WHICH step failed? Did it fail or time out?     → Exit code 137 = OOM, 143 = killed/cancelled, 1 = command error.
3. WHAT changed? Diff the last green run vs red:   → code? lock file? base image? runner image? action version? secret expiry?
4. REPRODUCE locally with the same versions        → same container image, same commands (Makefile helps).
5. ADD visibility                                  → print versions/env (not secrets), enable debug logging (§7.6).
6. NARROW down                                     → comment out steps, run a single job, use manual triggers.
7. FIX the root cause, then ADD a guard            → pin the version that drifted, add a validation step.
```

**"Nothing changed but it broke" usually means one of these:**

| Hidden change | How to spot it |
|---------------|----------------|
| Hosted runner image updated (new tool versions) | Runner image version is printed at the top of the job log ("Runner Image" / "Agent image") |
| Floating tag moved (`node:latest`, `@v4` action, `ubuntu-latest`) | Compare resolved versions/digests between runs |
| Dependency published a broken version (no lock file) | Lock file missing or `npm install` instead of `npm ci` |
| Secret / certificate / PAT expired | Auth errors starting on a specific date |
| Cloud quota or policy change | `QuotaExceeded`, `RequestDisallowedByPolicy` (Azure Policy), SCP denies (AWS) |
| Upstream outage (registry, package index) | Status pages: githubstatus.com, status.dev.azure.com, health.aws.amazon.com |

---

## 7.6 Turning on debug logging

| Platform | How |
|----------|-----|
| **GitHub Actions** | Re-run → "Enable debug logging", **or** set repository secrets/variables `ACTIONS_STEP_DEBUG=true` (step debug) and `ACTIONS_RUNNER_DEBUG=true` (runner diagnostics) |
| **Azure DevOps** | Run pipeline → **"Enable system diagnostics"**, or set variable `system.debug: true` |
| **AWS CodeBuild** | Add `set -x` to commands; use **CodeBuild Session Manager** debugging (add `codebuild-breakpoint` in buildspec and enable session connection when starting the build) to get a shell inside the running build |

Printing useful context safely:

```bash
# Versions and environment basics — NEVER dump full env (it may include secrets)
set -x
uname -a
node --version; npm --version
docker version --format '{{.Server.Version}}'
df -h; free -m
echo "Branch: $BRANCH  Commit: $COMMIT"
```

**GitHub expression debugging:**

```yaml
- name: Dump GitHub context (safe — no secrets in it)
  env:
    GITHUB_CONTEXT: ${{ toJSON(github) }}
  run: echo "$GITHUB_CONTEXT"
```

**Azure DevOps expanded YAML:** on any run → ⋮ → **Download full YAML** shows exactly what your
templates and parameters produced.

---

## 7.7 Running pipelines locally

| Platform | Tool | Notes |
|----------|------|-------|
| GitHub Actions | **`act`** (`nektos/act`) | Runs workflows in Docker locally. Not 100% identical (different images, no OIDC, limited service containers), but great for fast iteration |
| GitHub Actions | `actionlint` | Static checker for workflow files: catches expression typos, wrong keys, shell issues (via shellcheck) |
| Azure DevOps | No official local runner | Validate templates with the REST "preview" API (`POST …/pipelines/{id}/preview` with `previewRun: true`) or `az pipelines run` on a branch; keep logic in scripts |
| AWS CodeBuild | **CodeBuild local agent** (`codebuild_build.sh`) | Runs a buildspec locally in the official CodeBuild image |
| All | **Docker + Makefile** | Run `make test` inside the same image CI uses — the most reliable "local CI" |

```bash
# act: run the "test" job of the push event
act push -j test

# actionlint: lint all workflows
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:latest

# CodeBuild local agent
./codebuild_build.sh -i public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0 -a /tmp/artifacts -b buildspec.yml
```

---

## 7.8 Cost optimisation

| Tip | Why it saves money |
|-----|--------------------|
| Cancel outdated runs (`concurrency` / batching / SUPERSEDED mode) | Don't pay for runs of commits nobody will deploy |
| Path filters & affected-only builds | Docs changes don't run 40-minute builds |
| Cache dependencies and Docker layers | Minutes are money |
| Timeouts on every job | A hung job can burn hours (GitHub default: 6 h) |
| Linux over Windows/macOS where possible | Windows ≈ 2×, macOS ≈ 10× Linux per-minute price (GitHub-hosted, private repos) |
| Right-size runners | Bigger runners can be *cheaper* if they finish much faster; measure |
| Arm64 runners for compatible workloads | Usually cheaper per minute |
| Full matrix nightly, small matrix on PRs | Fewer jobs per push |
| Short artifact retention (3–7 days for CI artifacts) | Storage costs |
| Registry lifecycle policies (Chapter 06, Scenario 63) | Storage costs |
| Self-hosted/ephemeral runners for heavy, steady workloads | Can be cheaper at scale — but add ops cost |

---

## 7.9 Choosing a platform

| Factor | GitHub Actions | Azure DevOps Pipelines | AWS CodeBuild + CodePipeline |
|--------|---------------|------------------------|------------------------------|
| Best when | Code is on GitHub; open source; huge Marketplace | Enterprise on Azure; need Boards/Test Plans/Artifacts in one suite; complex approvals | Workloads on AWS; must run inside AWS accounts/VPCs |
| Pipeline definition | YAML in repo | YAML in repo (+ classic UI pipelines, legacy) | buildspec in repo; pipeline in console/IaC |
| Reuse | Actions, composite actions, reusable workflows | Templates (very powerful), `extends`, task extensions | Shared buildspecs/scripts, custom images |
| Approvals / gates | Environments (required reviewers, wait timers, custom protection rules) | Environments with rich checks (approvals, business hours, Azure Monitor, REST, exclusive lock, required template) | Manual approval actions; CodeDeploy alarms |
| Cloud auth | OIDC to any cloud | Workload identity (Azure), extensions for AWS/GCP | Native IAM role (no auth step at all) |
| Hosted runners | Linux/Windows/macOS, ARM, GPU, larger runners | Linux/Windows/macOS | Linux/Windows (+ macOS reserved), ARM, GPU, Lambda compute |
| Weak spots | Complex multi-stage release orchestration is DIY; approvals need paid plans for private repos | UI/permission model complexity; YAML syntax has three expression types | Pipeline-as-code split across services; less polished UX; fewer prebuilt integrations |

> It's very common to **combine** them: GitHub for code + Actions for CI, deploying to Azure via
> OIDC; or GitHub Actions jobs running **on** CodeBuild runners inside AWS.

---

## 7.10 Interview-style questions to test yourself

1. What's the difference between a **job** and a **stage**, and why don't files carry over between jobs?
2. Why is `npm ci` preferred over `npm install` in CI?
3. Explain OIDC federation for pipelines. What's the "subject" claim and why does it matter?
4. How do you make sure the image deployed to prod is the same one tested in staging?
5. A required GitHub status check is stuck on "Waiting for status to be reported". Why, and how do you fix it?
6. In Azure DevOps, what's the difference between `$(var)`, `${{ variables.var }}` and `$[ variables.var ]`?
7. Why does a CodeBuild `post_build` phase need to check `CODEBUILD_BUILD_SUCCEEDING`?
8. How would you prevent two deployments to production from running at the same time on each platform?
9. Why should Terraform apply a saved plan file rather than running a fresh `apply`?
10. What's the risk of `pull_request_target`, and of pinning actions by tag instead of SHA?
11. Describe blue/green vs canary. Which gives the fastest rollback?
12. How do you run database migrations safely with rolling or blue/green deployments?
13. What would you check first if a pipeline that worked yesterday fails today with no code changes?
14. How do you get secrets into a pipeline without storing them in the CI system?
15. Your monorepo CI takes 40 minutes. List five ways to make it faster.

<details>
<summary>💡 Short answers</summary>

1. A stage is a phase made of jobs. A job is a set of steps on **one machine**. Each job gets a
   fresh machine, so files must be passed as artifacts.
2. `npm ci` installs exactly what the lock file says, fails on mismatch, and is faster and reproducible.
3. The CI platform issues a signed token describing the run. The cloud trusts tokens with a
   specific issuer/audience/**subject** (repo + branch/environment) and swaps them for
   short-lived credentials. The subject restricts *which* pipelines can assume the identity.
4. Build once, tag immutably (SHA/digest), promote the same digest (copy/import), and deploy by digest.
5. The workflow/job didn't run (path filter, renamed job, condition). Use an always-running
   aggregator job as the required check.
6. Macro (runtime, before the task runs) vs template expression (compile time) vs runtime
   expression (used in conditions/variables at runtime).
7. `post_build` runs even if `build` failed, so pushes/deploys would happen after failures.
8. GitHub `concurrency` group (no cancel); ADO exclusive lock check / `lockBehavior`;
   CodePipeline `QUEUED` mode / CodeBuild concurrent build limit 1.
9. So that exactly what was reviewed and approved is applied; Terraform refuses a stale plan.
10. `pull_request_target` runs with secrets/write token in the base repo context, so running
    PR code there can leak secrets. Tags can be re-pointed to malicious code; SHAs can't.
11. Blue/green switches all traffic at once with an idle copy kept warm (instant rollback by
    switching back). Canary shifts traffic gradually while watching metrics (limits blast radius).
    Blue/green has the fastest rollback.
12. Run migrations once before deploying; keep them backward compatible (expand/contract);
    never drop/rename what the old version still uses.
13. Hidden changes: runner image updates, floating tags, expired secrets, upstream outages,
    quota/policy changes. Diff the green and red logs.
14. OIDC/workload identity for cloud auth; read secrets from Key Vault/Secrets Manager at
    runtime (or let the app read them itself).
15. Caching, Docker layer caching, affected-only builds/path filters, parallel jobs & test
    sharding, fail-fast ordering, cancel outdated runs, bigger runners.

</details>

---

[⬅️ Back to Index](README.md)
