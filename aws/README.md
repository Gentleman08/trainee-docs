[🏠 Home](../README.md)

# ☁️ Amazon Web Services (AWS) — Terms, Services & When to Use Each

> A beginner-to-advanced guide to AWS: the **vocabulary**, **what every major service does and
> when to pick it**, and **20 real-world scenarios** with architectures and decision guides. It
> also maps each Azure service to its AWS equivalent, for readers coming from this repo's Azure notes.

| # | Chapter | What's inside |
|---|---------|---------------|
| 01 | [📖 AWS Terms & Concepts](01-aws-terms.md) | ~170 terms: global infrastructure, accounts & Organizations, IAM, VPC networking, EC2, storage, databases, serverless & containers, security/encryption, monitoring & IaC, reliability/DR, pricing |
| 02 | [🧰 AWS Services: What & When](02-aws-services.md) | ~170 services in 17 categories with "use it when" / "think twice", plus a list of retired services to avoid |
| 03 | [🏗️ Scenarios & Decision Guides](03-aws-scenarios.md) | 8 decision guides (compute, DB, storage, messaging, networking, load balancing, access, IaC), 20 scenario architectures, Azure ↔ AWS mapping, top 20 beginner mistakes, certification path |
| 04 | [⌨️ AWS CLI Commands](04-aws-cli-commands.md) | CLI v2 install, SSO/profiles, `--query`/filters/waiters, commands for IAM, EC2, VPC, SSM, S3, Lambda, ECR/ECS/EKS, RDS/DynamoDB, CloudFormation, CloudWatch, secrets/KMS, ELB/ASG, Route 53/ACM/CloudFront, messaging, security, cost, Bedrock, plus recipes, PowerShell notes and error fixes |

---

## 🧭 How to use this

- **New to AWS?** Read Chapter 01 sections 1–6 → skim Chapter 02 → do Scenarios 1–3 in a sandbox account.
- **"Which service should I use?"** → [Decision guides](03-aws-scenarios.md#part-a--decision-guides).
- **Coming from Azure?** → [Azure ↔ AWS mapping](03-aws-scenarios.md#c1-azure--aws-service-mapping).
- **Designing something real?** → find the closest of the [20 scenarios](03-aws-scenarios.md#part-b--20-real-world-scenarios).
- **Need the command?** → [AWS CLI Commands](04-aws-cli-commands.md) (start with [authentication & SSO](04-aws-cli-commands.md#2--authentication-profiles--sso)).

## ✅ Day-one checklist for any AWS account

1. MFA on the root user; no root access keys.
2. **AWS Budgets** alert (and Cost Anomaly Detection).
3. Humans log in via **IAM Identity Center**, not IAM users.
4. **CloudTrail**, **GuardDuty**, **Security Hub**, **Config** enabled (all regions).
5. **S3 Block Public Access** at account level; default EBS encryption on.
6. Workloads use **IAM roles**; CI/CD uses **OIDC**, never stored keys.
7. Everything created with **IaC** (Terraform/CloudFormation/CDK) and tagged.

---

## 🔗 Related notes in this repo

- [Cloud Handbook](../cloud/cloud_handbook.md) covers cloud concepts across AWS/Azure/GCP
- [Cloud practice lab: production web app on AWS](../labs/cloud_practice_lab.md)
- [CI/CD Pipelines: AWS CodeBuild/CodePipeline examples](../cicd-pipelines/README.md)
- [Dockerfile Handbook](../docker/dockerfile_handbook/README.md) · [DevOps Glossary](../devops-glossary/README.md) · [Azure notes](../azure/README.md)

---

[🏠 Back to Home](../README.md)
