# 🔁 CI/CD Pipeline Scenarios — GitHub Actions · Azure DevOps · AWS CodeBuild

> A scenario-based guide to writing CI/CD pipelines on the three platforms you'll meet most
> often. Most scenarios show **the same job written three ways**, side by side, so you learn the
> concepts and can translate between platforms. Written for beginners: no development
> background assumed.

[🏠 Back to Home](../README.md)

---

## 🧭 How to use this guide

1. Start with **[Chapter 00 — Fundamentals](00-fundamentals.md)**. It covers what CI/CD is, the
   vocabulary, how each platform's YAML is structured, a **Rosetta Stone** table that translates
   between them, YAML traps, and how pipelines log in to clouds.
2. Then pick the chapter that matches your task.
3. Each scenario follows the same layout:

| Section | What you get |
|---------|--------------|
| 🎯 **Goal** | The real-world situation in one or two sentences |
| **GitHub Actions** | Complete workflow YAML |
| **Azure DevOps** | Complete pipeline YAML |
| **AWS CodeBuild / CodePipeline** | Complete `buildspec.yml` (+ CloudFormation for the pipeline where relevant) |
| 🔍 **Explained** | What the important lines do and why |
| ⚠️ **Gotchas** | Real-world traps, error messages, and fixes |

> 📝 Action/task/tool versions (e.g. `actions/checkout@v4`, `Docker@2`, `terraform 1.9.8`) were
> current when written. Check for newer versions, and pin them in your pipelines.

> 🔗 Related notes in this repo:
> - [Azure DevOps Enterprise CI/CD Guide](../azure-devops/index.md) goes deep on Azure DevOps alone
> - [Dockerfile Handbook](../docker/dockerfile_handbook/README.md) covers how to write the images these pipelines build

---

## 📚 Chapters

| # | Chapter | Scenarios | Covers |
|---|---------|-----------|--------|
| 00 | [Fundamentals & Platform Anatomy](00-fundamentals.md) | 1–3 | CI/CD concepts, vocabulary, anatomy of each platform, Rosetta Stone, YAML traps, OIDC, triggers, variables & secrets |
| 01 | [CI: Build & Test](01-ci-build-test.md) | 4–15 | Node, Python, Java, .NET, Go CI; matrices; service containers; monorepos; artifacts; SonarQube; PR validation; speed-ups |
| 02 | [Container Image Pipelines](02-containers.md) | 16–23 | GHCR/ACR/ECR, OIDC push, layer caching, multi-arch, Trivy gate, SBOM & cosign signing, promotion, smoke tests |
| 03 | [Deployments](03-deployments.md) | 24–36 | Multi-env approvals, App Service, Elastic Beanstalk, S3/CloudFront, AKS/EKS, Helm, ECS, Lambda/Functions, blue/green, canary, migrations, GitOps, rollback |
| 04 | [Infrastructure as Code](04-iac.md) | 37–44 | Terraform (all three platforms), Bicep, CloudFormation change sets, CDK, drift detection, multi-env layouts |
| 05 | [DevSecOps & Pipeline Security](05-devsecops.md) | 45–52 | OIDC setup, secret scanning, SAST, SCA, IaC scanning, DAST, vault secrets, pipeline hardening |
| 06 | [Advanced Patterns](06-advanced-patterns.md) | 53–64 | Reusable workflows/templates, composite actions, inputs, concurrency, dynamic matrices, releases, cross-pipeline triggers, self-hosted runners, notifications, hotfixes, housekeeping, portable pipelines |
| 07 | [Troubleshooting & Reference](07-troubleshooting.md) | — | Error → fix tables per platform, debugging playbook, debug logging, local runs, cost, platform choice, self-test questions |

---

## 🔎 Quick lookup — "I need a pipeline that…"

| I need to… | Go to |
|------------|-------|
| Understand pipeline YAML from zero | [Ch 00](00-fundamentals.md) |
| Translate a GitHub workflow to Azure DevOps (or back) | [Rosetta Stone](00-fundamentals.md#06-the-rosetta-stone) |
| Build & test a Node / Python / Java / .NET / Go app | [Scenarios 4–8](01-ci-build-test.md) |
| Run tests against a real database | [Scenario 10](01-ci-build-test.md#scenario-10--integration-tests-with-a-real-database) |
| Build only changed services in a monorepo | [Scenario 11](01-ci-build-test.md#scenario-11--monorepo-build-only-what-changed) |
| Build and push a Docker image | [Scenario 16](02-containers.md#scenario-16--build-and-push-to-the-native-registry) |
| Push from GitHub to Azure/AWS without secrets | [Scenario 17](02-containers.md#scenario-17--github-actions-to-acr-and-ecr-with-oidc), [Scenario 45](05-devsecops.md#scenario-45--set-up-oidc-and-workload-identity) |
| Add approvals before production | [Scenario 24](03-deployments.md#scenario-24--multi-environment-pipeline-with-approvals) |
| Deploy to Kubernetes | [Scenario 27](03-deployments.md#scenario-27--kubernetes-deploy-with-manifests), [Scenario 28](03-deployments.md#scenario-28--helm-deploy-with-atomic-rollback) |
| Deploy to ECS / Lambda | [Scenario 29](03-deployments.md#scenario-29--amazon-ecs-fargate-deploy), [Scenario 30](03-deployments.md#scenario-30--serverless-deploy) |
| Do blue/green or canary | [Scenario 31](03-deployments.md#scenario-31--bluegreen-deployments), [Scenario 32](03-deployments.md#scenario-32--canary-releases) |
| Roll back fast | [Scenario 35](03-deployments.md#scenario-35--post-deploy-smoke-tests-and-automatic-rollback), [Scenario 36](03-deployments.md#scenario-36--manual-rollback-to-a-previous-version) |
| Run Terraform safely in CI | [Scenarios 37–39](04-iac.md) |
| Add security scans | [Scenarios 46–50](05-devsecops.md) |
| Share one pipeline across many repos | [Scenario 53](06-advanced-patterns.md#scenario-53--reusable-pipelines) |
| Release on tag with changelog | [Scenario 58](06-advanced-patterns.md#scenario-58--release-automation) |
| Fix a red pipeline | [Ch 07](07-troubleshooting.md) |

---

## ✅ The 12 pipeline commandments

1. **Pipeline as code.** YAML in the repo, changed through PRs.
2. **Fail fast.** Lint and unit tests first; slow suites later.
3. **Build once, deploy many.** Promote the same artifact/digest through environments.
4. **Pin everything.** Actions/tasks (by SHA where possible), tools, base images, templates.
5. **Least privilege.** `permissions: {}` by default, scoped cloud roles, separate prod identity.
6. **No long-lived secrets.** OIDC / workload identity; vaults for the rest.
7. **Protect production.** Environments with approvals and branch restrictions.
8. **Never deploy two at once.** Concurrency groups / exclusive locks / queued execution.
9. **Verify every deploy.** Rollout status + smoke tests + automatic rollback.
10. **Shift security left.** Secrets, SAST, SCA, IaC and image scans in every pipeline.
11. **Cache and parallelise.** Fast pipelines get used; slow ones get bypassed.
12. **Keep logic in scripts.** Thin YAML, portable `make` targets, testable locally.

---

[🏠 Back to Home](../README.md)
