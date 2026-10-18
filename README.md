# 📚 DevOps & Cloud Engineering — Trainee Notes

> A curated knowledge base for DevOps & Cloud Engineers: handbooks, cheatsheets, glossaries,
> hands-on tasks, labs, edge cases and interview prep, from first Linux command to production SRE.
> **Every folder has an index page.** Start below, or jump to the [full document list](#-all-documents).

---

## 📑 Contents

- [🚀 Start Here](#-start-here)
- [🧭 Learning Path](#-learning-path)
- [📂 Browse by Domain](#-browse-by-domain)
  - [1. Foundations](#1-foundations) · [2. Cloud, AWS & Azure](#2-cloud-aws--azure) · [3. Containers & Kubernetes](#3-containers--kubernetes) · [4. CI/CD & Automation](#4-cicd--automation)
  - [5. Security](#5-security) · [6. AI & Development](#6-ai--development) · [7. Reference & Glossaries](#7-reference--glossaries) · [8. Practice & Interview Prep](#8-practice--interview-prep)
- [📄 All Documents](#-all-documents)
- [🧱 Repo Structure](#-repo-structure)
- [🤝 Adding New Notes](#-adding-new-notes)

---

## 🚀 Start Here

| If you are… | Open first |
|-------------|-----------|
| A brand-new trainee | [DevOps Glossary: Beginner Terms](devops-glossary/beginner-terms.md) → [Linux Handbook](linux/linux_admin_handbook.md) → [Git Handbook](git/git_handbook.md) |
| Looking for a quick answer | [⚡ Quick Reference](quick-reference/README.md) · [📖 DevOps Glossary](devops-glossary/README.md) · [🧰 IT Tools & Websites](it-tools-and-websites/README.md) |
| Preparing for an interview | [📝 1st Review Handbook](first_review/README.md) · [Linux Q&A](linux_qa.md) · [⚠️ Edge Cases](edge_cases/README.md) |
| Preparing for Azure certs | [AZ-104](azure/az104_exam_handbook.md) · [AZ-305](azure/az305_exam_handbook.md) · [SC-300](azure/sc300_cheatsheet.md) |
| Wanting hands-on practice | [🎯 Tasks](tasks/README.md) · [🧪 Labs](labs/README.md) · [🧪 Azure Labs](azure%20labs/README.md) |
| Using AI tools at work | [🤖 AI Coding Agents](ai-coding-agents/README.md) (Antigravity & Claude Code, safely) |

---

## 🧭 Learning Path

A suggested order for a DevOps/Cloud trainee. Each step: **read the handbook → do the tasks → do the lab → review edge cases**.

| # | Stage | Read | Practise |
|---|-------|------|----------|
| 1 | Vocabulary | [Beginner Terms](devops-glossary/beginner-terms.md) | — |
| 2 | Linux & shell | [Linux Admin](linux/linux_admin_handbook.md), [CLI Power Tools](linux/cli_power_tools_handbook.md) | [Linux tasks](tasks/README.md) · [Linux DR lab](labs/linux_etc_disaster_recovery.md) · [Edge cases](edge_cases/linux_edge_cases.md) |
| 3 | Git | [Git Handbook](git/git_handbook.md), [Git Scenarios](git/git_scenarios.md) | [Git tasks](tasks/README.md) · [Edge cases](edge_cases/git_edge_cases.md) |
| 4 | Networking | [Networking Handbook](networking/networking_handbook.md), [DNS notes](quick-reference/dns_notes.md) | [Networking tasks](tasks/README.md) · [Networking lab](labs/networking_practice_lab.md) |
| 5 | Web servers | [Nginx](servers/nginx.md), [Apache](servers/apache.md), [IIS](servers/iis.md) | [Server tasks](tasks/README.md) · [Server labs](labs/README.md) |
| 6 | Windows Server | [Windows Server 2022](windows/windows_server_2022_cheatsheet.md) | [Windows Server tasks](tasks/windows_server/level_1.md) · [IIS lab](labs/iis_practice_lab.md) |
| 7 | Scripting | [Scripting Handbook](scripting/scripting_handbook.md) | Automate tasks from earlier stages |
| 8 | Cloud concepts | [Cloud Handbook](cloud/cloud_handbook.md), [Intermediate Terms](devops-glossary/intermediate-terms.md) | [Cloud tasks](tasks/README.md) · [Cloud lab](labs/cloud_practice_lab.md) |
| 9 | Azure and/or AWS | [Azure Handbook](azure/azure_handbook.md), [Azure Services](azure-services/README.md) · [AWS Terms](aws/01-aws-terms.md), [AWS Services](aws/02-aws-services.md) | [Azure Labs 1–6](azure%20labs/README.md) · [AWS Scenarios](aws/03-aws-scenarios.md) |
| 10 | Containers | [VM vs Containers & Docker](docker/devops_vm_containers_docker.md), [Dockerfile Handbook](docker/dockerfile_handbook/README.md) | Containerise a sample app |
| 11 | Kubernetes | [Kubernetes Handbook](kubernetes/kubernetes_handbook.md) | [Azure Labs batch 3 (AKS)](azure%20labs/batch-3-containers-databases-and-messaging.md) |
| 12 | CI/CD & IaC | [CI/CD Pipeline Scenarios](cicd-pipelines/README.md), [Azure DevOps Guide](azure-devops/index.md), [Terraform Architecture](terraform-arch/README.md) | [Azure Labs batch 4](azure%20labs/batch-4-serverless-cicd-and-iac.md) |
| 13 | Security | [Cybersecurity](cybersecurity-notes/index.md), [Web VAPT](web-vapt-notes/index.md), [CI/CD DevSecOps](cicd-pipelines/05-devsecops.md) | — |
| 14 | Production & SRE | [Advanced Terms](devops-glossary/advanced-terms.md), [Best Practices](best-practices-devops-cloud.md), [Project Best Practices](quick-reference/project_best_practices.md) | [Azure Labs 5–6](azure%20labs/README.md) |

---

## 📂 Browse by Domain

### 1. Foundations

| Folder | What's inside |
|--------|---------------|
| [🐧 Linux](linux/README.md) | Linux administration handbook; CLI power tools (grep, awk, sed, curl, wget, journalctl, regex) |
| [🪟 Windows](windows/README.md) | Windows Server 2022: AD DS, DNS, DHCP, GPO, storage, permissions, PowerShell |
| [🌐 Networking](networking/README.md) | OSI/TCP-IP, subnetting, DNS, HTTP/TLS, firewalls, load balancers, VPNs, container networking |
| [🔀 Git](git/README.md) | Git internals, branching, workflows, recovery; scenario-based command reference |
| [📜 Scripting](scripting/README.md) | Bash & Python for DevOps: automation, CI/CD, Kubernetes, monitoring |
| [🌐 Servers](servers/README.md) | Nginx, Apache, IIS: reverse proxy, SSL, hosting, production Q&A |

### 2. Cloud, AWS & Azure

| Folder | What's inside |
|--------|---------------|
| [☁️ Cloud](cloud/README.md) | Data centres, virtualisation, IaaS/PaaS/SaaS, AWS/Azure/GCP, HA/DR, FinOps |
| [🟧 AWS](aws/README.md) | ~170 AWS terms, ~170 services with when to use each, 20 scenario architectures, decision guides, Azure ↔ AWS mapping, AWS CLI command reference |
| [☁️ Azure](azure/README.md) | DevOps-on-Azure handbook, AZ-104 & AZ-305 exam Q&A, SC-300 cheatsheet, networking presentation |
| [🧰 Azure Services](azure-services/README.md) | Service-by-service reference handbook + configuration deep dives |
| [📖 Azure Glossary](azure-glossary/README.md) | 500+ Azure & Active Directory terms |
| [🧪 Azure Labs](azure%20labs/README.md) | 34 hands-on scenarios in 6 batches, beginner → advanced |
| [🔁 Azure DevOps](azure-devops/index.md) | Enterprise Azure DevOps CI/CD platform guide in 12 phases (GitFlow → DR & compliance) |
| [🏗️ Terraform Architecture](terraform-arch/README.md) | Reference 3-tier application on Azure with Terraform |

### 3. Containers & Kubernetes

| Folder | What's inside |
|--------|---------------|
| [🐳 Docker](docker/README.md) | VMs vs containers & Docker internals; **Dockerfile Handbook** with 115 examples across tech stacks |
| [☸️ Kubernetes](kubernetes/README.md) | Architecture, workloads, networking, Helm, security, observability, GitOps |

### 4. CI/CD & Automation

| Folder | What's inside |
|--------|---------------|
| [🔁 CI/CD Pipelines](cicd-pipelines/README.md) | 64 scenarios side by side in GitHub Actions, Azure DevOps and AWS CodeBuild/CodePipeline |
| [🔁 Azure DevOps](azure-devops/index.md) | Deep, single-platform enterprise guide (also listed under Azure) |

### 5. Security

| Folder | What's inside |
|--------|---------------|
| [🛡️ Cybersecurity Notes](cybersecurity-notes/index.md) | Fundamentals, network security, cryptography, endpoint/cloud, threat intel, compliance + 2 case studies |
| [🕸️ Web VAPT Notes](web-vapt-notes/index.md) | Web vulnerability assessment & pentesting: injection, XSS, auth, misconfigs, tools, DevSecOps + case studies |
| [🔬 Reverse Engineering Notes](reverse-engineering-notes/index.md) | Assembly, OS internals, tools, dynamic analysis, malware analysis, exploit dev + case studies |

### 6. AI & Development

| Folder | What's inside |
|--------|---------------|
| [🤖 AI Coding Agents](ai-coding-agents/README.md) | Google Antigravity (App/IDE/CLI) & Claude Code: safe setup, permissions, sandbox, rules, skills, hooks, MCP |
| [🧠 AI/ML Notes](ai-ml-notes/index.md) | AI fundamentals → LLMs, fine-tuning, RAG, agents, MLOps, AI safety + 2 case studies |
| [💻 Web Dev Notes](webdev-notes/index.md) | Internet fundamentals, CSS, TypeScript, React ecosystem, testing, security |
| [⛓️ Web3 & Blockchain Notes](web3-blockchain-notes/index.md) | Blockchain, consensus, Ethereum, Solidity, DeFi, L2s, dApps, security + case studies |

### 7. Reference & Glossaries

| Resource | What's inside |
|----------|---------------|
| [📖 DevOps Glossary](devops-glossary/README.md) | ~360 vendor-neutral terms in Beginner / Intermediate / Advanced levels |
| [📖 Azure Glossary](azure-glossary/README.md) | 500+ Azure & AD terms |
| [🧰 IT Tools & Websites](it-tools-and-websites/README.md) | ~200 tools/sites (Firebase, Supabase, Vercel, Postman…): what they're for and when to use each |
| [⚡ Quick Reference](quick-reference/README.md) | DNS, Azure RBAC, KT checklist, project best practices |
| [✅ Best Practices: Cloud & DevOps](best-practices-devops-cloud.md) | Best practices with reasoning for Azure, AWS, GCP, Git, GitHub, Docker, Terraform and more |
| [🛠️ DevOps Toolkit](devops_toolkit.md) | Software & tools list for the training environment |

### 8. Practice & Interview Prep

| Resource | What's inside |
|----------|---------------|
| [🎯 Tasks](tasks/README.md) | Level 1/2/3 task sheets: Linux, Git, Networking, Nginx, Apache, Windows Server, Cloud |
| [🧪 Labs](labs/README.md) | Disaster-recovery labs and server/networking/cloud practice labs |
| [🧪 Azure Labs](azure%20labs/README.md) | 34 Azure scenarios |
| [⚠️ Edge Cases](edge_cases/README.md) | 110 production edge cases each for Linux, Git, Networking, Nginx, Apache, Cloud |
| [📝 1st Review Handbook](first_review/README.md) | Interview-prep deep dive: Linux internals, shell, processes, networking, Nginx, Windows Server |
| [❓ Linux & DevOps Q&A](linux_qa.md) | Interview questions with concise answers |
| [🎓 Azure exam prep](azure/README.md) | AZ-104 & AZ-305 Q&A, SC-300 cheatsheet |
| [🧾 Day 0 Prompt Library](Day%200/README.md) | The prompts used to generate note sets, reusable as templates |

---

## 📄 All Documents

<details>
<summary><b>Click to expand the complete list (main documents; batch trackers omitted)</b></summary>

| Document | Folder |
|----------|--------|
| [Linux Admin Handbook](linux/linux_admin_handbook.md) | Linux |
| [Linux CLI Power Tools Handbook](linux/cli_power_tools_handbook.md) | Linux |
| [Windows Server 2022 Cheatsheet](windows/windows_server_2022_cheatsheet.md) | Windows |
| [Computer Networking Handbook](networking/networking_handbook.md) | Networking |
| [Git Handbook](git/git_handbook.md) | Git |
| [Git Scenarios — Command Reference](git/git_scenarios.md) | Git |
| [Scripting for DevOps Handbook](scripting/scripting_handbook.md) | Scripting |
| [Nginx](servers/nginx.md) · [Apache](servers/apache.md) · [IIS](servers/iis.md) | Servers |
| [Data Centers & Cloud Computing Handbook](cloud/cloud_handbook.md) | Cloud |
| [AWS Terms](aws/01-aws-terms.md) · [AWS Services](aws/02-aws-services.md) · [AWS Scenarios & Decision Guides](aws/03-aws-scenarios.md) · [AWS CLI Commands](aws/04-aws-cli-commands.md) | AWS |
| [DevOps on Azure Handbook](azure/azure_handbook.md) | Azure |
| [AZ-104 Exam Handbook](azure/az104_exam_handbook.md) · [AZ-305 Exam Handbook](azure/az305_exam_handbook.md) · [SC-300 Cheatsheet](azure/sc300_cheatsheet.md) | Azure |
| [Azure Services Handbook](azure-services/azure_services_handbook.md) · [Azure Deep Dive Notes](azure-services/azure_deepdive_notes.md) | Azure Services |
| [Azure Glossary](azure-glossary/azure_glossary.md) | Azure Glossary |
| [Azure Labs batches 1–6](azure%20labs/README.md) | Azure Labs |
| [Azure DevOps Guide — Index](azure-devops/index.md) + phases 1–12 | Azure DevOps |
| [Terraform 3-Tier Architecture](terraform-arch/ARCHITECTURE.md) | Terraform |
| [VM vs Containers & Docker](docker/devops_vm_containers_docker.md) | Docker |
| [Dockerfile Handbook — 115 Examples](docker/dockerfile_handbook/README.md) (11 chapters) | Docker |
| [Kubernetes Handbook](kubernetes/kubernetes_handbook.md) | Kubernetes |
| [CI/CD Pipeline Scenarios](cicd-pipelines/README.md) (8 chapters) | CI/CD |
| [Cybersecurity Notes](cybersecurity-notes/index.md) (6 batches + 2 case studies) | Security |
| [Web VAPT Notes](web-vapt-notes/index.md) (8 batches + 2 case studies) | Security |
| [Reverse Engineering Notes](reverse-engineering-notes/index.md) (8 batches + 2 case studies) | Security |
| [AI Coding Agents](ai-coding-agents/README.md) (7 chapters) | AI |
| [AI/ML Notes](ai-ml-notes/index.md) (13 batches + 2 case studies) | AI |
| [Web Dev Notes](webdev-notes/index.md) | Development |
| [Web3 & Blockchain Notes](web3-blockchain-notes/index.md) (15 batches + 2 case studies) | Development |
| [DevOps Glossary — Beginner](devops-glossary/beginner-terms.md) · [Intermediate](devops-glossary/intermediate-terms.md) · [Advanced](devops-glossary/advanced-terms.md) | Glossary |
| [IT Tools & Websites](it-tools-and-websites/README.md) | Reference |
| [DNS Notes](quick-reference/dns_notes.md) · [Azure RBAC Notes](quick-reference/azure_rbac_notes.md) · [KT Checklist](quick-reference/kt_checklist.md) · [Project Best Practices](quick-reference/project_best_practices.md) | Quick Reference |
| [Best Practices — Cloud & DevOps](best-practices-devops-cloud.md) | Reference |
| [DevOps Toolkit](devops_toolkit.md) | Reference |
| [Tasks — Linux, Git, Networking, Nginx, Apache, Windows Server, Cloud (L1–L3)](tasks/README.md) | Practice |
| [Labs — DR, servers, networking, cloud](labs/README.md) | Practice |
| [Edge Cases — Linux, Git, Networking, Nginx, Apache, Cloud](edge_cases/README.md) | Practice |
| [1st Review Handbook](first_review/review_handbook.md) | Interview Prep |
| [Linux & DevOps Q&A](linux_qa.md) | Interview Prep |
| [Day 0 Prompt Library](Day%200/README.md) | Meta |

</details>

---

## 🧱 Repo Structure

```
trainee-docs/
├── README.md                    ← You are here
│
├── ── Foundations ──────────────────────────────────────────────
├── linux/                       ← Linux admin + CLI power tools
├── windows/                     ← Windows Server 2022
├── networking/                  ← Networking handbook
├── git/                         ← Git handbook + scenarios
├── scripting/                   ← Bash & Python for DevOps
├── servers/                     ← Nginx, Apache, IIS
│
├── ── Cloud, AWS & Azure ───────────────────────────────────────────
├── cloud/                       ← Data centres & cloud computing
├── aws/                         ← AWS terms, services, scenarios, decision guides & CLI commands
├── azure/                       ← Azure handbook, AZ-104/305, SC-300, presentation/
├── azure-services/              ← Service reference + deep dives
├── azure-glossary/              ← 500+ Azure/AD terms
├── azure labs/                  ← 6 batches, 34 scenarios
├── azure-devops/                ← Enterprise Azure DevOps guide (index.md + 12 phases)
├── terraform-arch/              ← Terraform 3-tier architecture on Azure
│
├── ── Containers, Kubernetes, CI/CD ────────────────────────────
├── docker/                      ← Docker notes + dockerfile_handbook/ (11 chapters)
├── kubernetes/                  ← Kubernetes handbook
├── cicd-pipelines/              ← 64 pipeline scenarios (GitHub/ADO/AWS)
│
├── ── Security ─────────────────────────────────────────────────
├── cybersecurity-notes/         ← index.md + batches + case studies
├── web-vapt-notes/              ← index.md + batches + case studies
├── reverse-engineering-notes/   ← index.md + batches + case studies
│
├── ── AI & Development ─────────────────────────────────────────
├── ai-coding-agents/            ← Antigravity & Claude Code (7 chapters)
├── ai-ml-notes/                 ← index.md + batches + case studies
├── webdev-notes/                ← index.md + batches
├── web3-blockchain-notes/       ← index.md + batches + case studies
│
├── ── Reference ────────────────────────────────────────────────
├── devops-glossary/             ← Beginner / Intermediate / Advanced terms
├── it-tools-and-websites/       ← Tools & websites guide
├── quick-reference/             ← DNS, RBAC, KT checklist, project best practices
├── best-practices-devops-cloud.md
├── devops_toolkit.md
│
├── ── Practice & Interview Prep ────────────────────────────────
├── tasks/                       ← Level 1/2/3 per topic (7 topics)
├── labs/                        ← DR + practice labs
├── edge_cases/                  ← 110 edge cases per topic (6 topics)
├── first_review/                ← 1st review interview handbook
├── linux_qa.md                  ← Linux & DevOps Q&A
│
└── Day 0/                       ← Prompt library used to generate notes
```

> **About `*batch_state*.md` / `batch-tracker.md` files:** these are progress trackers used while
> long notes were generated in batches. They're not study material, but they show what's complete.

---

## 🤝 Adding New Notes

1. **Pick the domain** above and the matching folder, or create a new `kebab-case` folder.
2. **Every folder has an index**: `README.md` (or `index.md` in the batch-style note folders).
   Add your file to that index with a one-line description.
3. **Add it to this README**: the domain table, the [All Documents](#-all-documents) list, and
   the [Repo Structure](#-repo-structure) tree.
4. **Navigation:** start pages with `[🏠 Home](../README.md)` and end with a "Back to Home" link.
5. **Links:** use relative Markdown links `[Text](folder/file.md)`. Folder names with spaces
   need `%20` (e.g. `azure%20labs/README.md`).
6. **Style used across the repo:** beginner-friendly explanation → real example → ASCII diagram
   where useful → ⚠️ gotchas → production FAQ.

---

> **Maintained by:** Vishvam Moliya
