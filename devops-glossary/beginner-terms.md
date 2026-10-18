# 🌱 Beginner DevOps Terms — Explained Simply

> **~110 foundational terms**, each with a plain-English definition, an **everyday analogy**,
> and a short DevOps example. No prior IT knowledge needed.
>
> Next steps: [Intermediate Terms](intermediate-terms.md) → [Advanced Terms](advanced-terms.md).

[⬅️ Back to Glossary Index](README.md)

---

## 📑 Table of Contents

1. [What DevOps Is](#1--what-devops-is)
2. [Software Development Basics](#2--software-development-basics)
3. [Version Control & Git](#3--version-control--git)
4. [Computers, Operating Systems & the Terminal](#4--computers-operating-systems--the-terminal)
5. [Networking Basics](#5--networking-basics)
6. [Cloud Basics](#6--cloud-basics)
7. [Containers & Orchestration (Intro)](#7--containers--orchestration-intro)
8. [CI/CD & Automation Basics](#8--cicd--automation-basics)
9. [Data & Storage Basics](#9--data--storage-basics)
10. [Monitoring & Operations Basics](#10--monitoring--operations-basics)
11. [Security Basics](#11--security-basics)
12. [File Formats & Everyday Tools](#12--file-formats--everyday-tools)

---

# 1 — What DevOps Is

### DevOps
**What:** A culture and set of practices where **Dev**elopment (people who write software) and **Op**eration**s** (people who run it) work together, automate as much as possible, and deliver changes quickly and reliably.
**Analogy:** Instead of chefs throwing dishes over a wall to waiters, they work as one kitchen team.
**Example:** Code changes go from a developer's laptop to production through an automated pipeline in minutes instead of weeks.

### DevOps Engineer
**What:** Someone who builds and maintains the tools, automation and infrastructure that help teams ship and run software.
**Analogy:** The person who designs and maintains the kitchen's conveyor belts and ovens.
**Example:** Writes CI/CD pipelines, Terraform, Dockerfiles and monitoring dashboards.

### CALMS
**What:** A summary of DevOps pillars: **C**ulture, **A**utomation, **L**ean, **M**easurement, **S**haring.
**Example:** Teams automate repetitive tasks (Automation) and share postmortems openly (Sharing).

### Agile
**What:** A way of building software in small increments with frequent feedback, instead of one big plan up front.
**Analogy:** Cooking a meal course by course and tasting as you go, instead of cooking everything at once.
**Example:** Two-week sprints, each delivering working features.

### Scrum
**What:** A popular Agile framework with fixed-length **sprints**, roles (Product Owner, Scrum Master, team) and ceremonies (planning, daily stand-up, review, retrospective).
**Example:** Daily 15-minute stand-up: what I did, what I'll do, what's blocking me.

### Kanban
**What:** A visual way to manage work as cards moving across columns (To Do → In Progress → Done), limiting work in progress.
**Analogy:** Sticky notes on a whiteboard.
**Example:** Ops teams often use Kanban boards in Jira or Azure Boards for tickets.

### SDLC (Software Development Life Cycle)
**What:** The stages software goes through: plan → design → build → test → release → operate → monitor → (feedback) plan again.
**Example:** DevOps automates and connects these stages into a continuous loop (the "infinity loop").

```
   plan → code → build → test
     ▲                     ▼
  monitor ← operate ← deploy ← release
```

### Automation
**What:** Letting computers do repetitive tasks instead of humans.
**Analogy:** A dishwasher instead of washing by hand.
**Example:** A script that creates 10 servers in 5 minutes instead of a person clicking for 2 hours.

---

# 2 — Software Development Basics

### Source Code
**What:** The human-readable instructions programmers write.
**Analogy:** A recipe.
**Example:** Files like `app.py`, `index.js`, `Main.java`.

### Programming Language
**What:** A language for writing source code.
**Example:** Python, JavaScript, Java, C#, Go. DevOps engineers often use Python, Bash and PowerShell for automation.

### Compile / Build
**What:** Turning source code into something that can run (a program, package or image).
**Analogy:** Baking dough into bread.
**Example:** `mvn package` produces a `.jar`; `docker build` produces an image.

### Dependency / Library / Package
**What:** Code written by others that your project reuses.
**Analogy:** Buying ready-made pasta instead of making it from flour.
**Example:** Listed in `package.json` (Node), `requirements.txt` (Python).

### Package Manager
**What:** A tool that downloads and manages dependencies or software.
**Example:** `npm`, `pip`, `apt` (Ubuntu), `winget`/`choco` (Windows), `brew` (macOS).

### Application / App
**What:** A software program that does something for users.
**Example:** A website, a mobile app, an internal API.

### Frontend vs Backend
**What:** **Frontend** = what users see and click (in the browser/app). **Backend** = the server side that processes requests and stores data.
**Analogy:** Frontend is the restaurant dining room; backend is the kitchen.
**Example:** React website (frontend) calls a Node.js API (backend) that reads a database.

### API (Application Programming Interface)
**What:** A defined way for programs to talk to each other.
**Analogy:** A restaurant menu: you order from it without knowing how the kitchen works.
**Example:** Weather app calls `GET https://api.weather.com/today?city=Pune`.

### REST API
**What:** A common style of web API using HTTP methods (`GET` read, `POST` create, `PUT/PATCH` update, `DELETE` remove) on URLs.
**Example:** `GET /orders/42` returns order 42 as JSON.

### Bug
**What:** A mistake in software that makes it behave incorrectly.
**Example:** The checkout button charges twice.

### Feature
**What:** A piece of functionality users can use.
**Example:** "Dark mode", "Export to PDF".

### Environment (Dev / Test / Staging / Production)
**What:** Separate copies of a system for different purposes. **Dev** for building, **test/QA** for testing, **staging** for a final production-like check, **production (prod)** for real users.
**Analogy:** Rehearsal stage vs the real concert.
**Example:** A change is tested in staging before going to prod.

### Production (Prod)
**What:** The live environment real users depend on.
**Example:** "Prod is down" = customers are affected. Treat prod changes carefully.

### Localhost
**What:** Your own computer, as seen by itself (`127.0.0.1`).
**Example:** A developer runs the app at `http://localhost:3000` while coding.

---

# 3 — Version Control & Git

### Version Control
**What:** A system that tracks every change to files, who made it, and lets you go back in time.
**Analogy:** "Track changes" plus unlimited undo for a whole project.
**Example:** Git is the most widely used version control system.

### Git
**What:** A distributed version control tool. Every developer has the full history locally.
**Example:** `git commit`, `git push`, `git pull`. See [Git Handbook](../git/git_handbook.md).

### Repository (Repo)
**What:** A project folder tracked by Git, including its full history.
**Example:** `github.com/acme/orders-api`.

### Commit
**What:** A saved snapshot of changes with a message.
**Analogy:** A save point in a video game.
**Example:** `git commit -m "Fix login timeout"`.

### Branch
**What:** An independent line of development.
**Analogy:** A copy of the document where you try edits without touching the original.
**Example:** `feature/dark-mode` branch off `main`.

### Main Branch (main / master)
**What:** The primary branch, usually representing the official, deployable code.
**Example:** Merging to `main` may trigger a deployment.

### Merge
**What:** Combining changes from one branch into another.
**Example:** Merge `feature/dark-mode` into `main` after review.

### Merge Conflict
**What:** When two changes edit the same lines and Git can't decide which to keep, so a human must choose.
**Example:** Two people both changed line 12 of `config.yaml`.

### Pull Request (PR)
**What:** A request to merge your branch, where others review the changes and automated checks run.
**Example:** "Please review my PR #128: add password reset."

### Code Review
**What:** Teammates reading your changes before they're merged, to catch mistakes and share knowledge.
**Example:** Reviewer comments: "This query needs an index."

### Clone / Fork
**What:** **Clone** = download a copy of a repo to your computer. **Fork** = create your own copy of someone else's repo on the server.
**Example:** `git clone https://github.com/acme/app.git`.

### Push / Pull
**What:** **Push** = upload your commits to the shared server. **Pull** = download others' commits.
**Example:** `git push origin feature/login`, `git pull`.

### GitHub / GitLab / Azure Repos / Bitbucket
**What:** Websites that host Git repositories, plus collaboration features (PRs, issues, CI/CD).
**Example:** GitHub Actions runs pipelines; GitLab has built-in CI/CD.

### .gitignore
**What:** A file listing files Git should **not** track.
**Example:** `node_modules/`, `.env` (secrets!), build outputs.

---

# 4 — Computers, Operating Systems & the Terminal

### Server
**What:** A computer that provides services to other computers (clients) over a network.
**Analogy:** A waiter serving many tables.
**Example:** A web server sends web pages to browsers.

### Client
**What:** A device/program that requests services from a server.
**Example:** Your browser is a client of a website's server.

### Operating System (OS)
**What:** The core software managing hardware and running programs.
**Example:** Windows, Linux (Ubuntu, RHEL), macOS. Most servers and containers run Linux.

### Linux
**What:** A free, open-source operating system family powering most of the world's servers, cloud and containers.
**Example:** Ubuntu, Debian, Red Hat Enterprise Linux, Amazon Linux. See [Linux handbook](../linux/linux_admin_handbook.md).

### Distribution (Distro)
**What:** A packaged version of Linux with its own tools and defaults.
**Example:** Ubuntu (apt), RHEL/Fedora (dnf), Alpine (apk).

### Terminal / Shell / Command Line (CLI)
**What:** A text interface where you type commands. The **shell** interprets them (Bash, Zsh, PowerShell).
**Analogy:** Texting instructions to the computer instead of clicking.
**Example:** `ls` (list files), `cd` (change folder), `cat` (show file).

### GUI (Graphical User Interface)
**What:** Windows, buttons and menus you click.
**Example:** Azure Portal, AWS Console. Automation prefers CLI/APIs over GUIs.

### Script
**What:** A file containing commands run in sequence.
**Example:** `backup.sh` (Bash) or `deploy.ps1` (PowerShell). See [Scripting handbook](../scripting/scripting_handbook.md).

### Bash / PowerShell
**What:** **Bash**: the common Linux shell and scripting language. **PowerShell**: Microsoft's shell, object-based, cross-platform.
**Example:** `for f in *.log; do gzip "$f"; done` (Bash).

### SSH (Secure Shell)
**What:** An encrypted way to log in to and run commands on remote computers.
**Example:** `ssh azureuser@10.0.1.4` using an SSH key.

### SSH Key (Public / Private)
**What:** A key pair for passwordless login. The **public** key goes on the server; the **private** key stays secret with you.
**Analogy:** A padlock (public) you give out, and the only key (private) you keep.
**Example:** `ssh-keygen -t ed25519`. Never share or commit the private key.

### Process / Service (Daemon)
**What:** A **process** is a running program. A **service/daemon** is a background process that keeps running.
**Example:** `nginx` service serving websites; `systemctl status nginx`.

### Root / Administrator / sudo
**What:** The all-powerful account (root on Linux, Administrator on Windows). `sudo` runs one command with admin rights.
**Example:** `sudo apt install nginx`.
**⚠️** Use admin rights only when needed. Mistakes as root can break the whole system.

### File Permissions
**What:** Rules for who can read, write or execute a file.
**Example:** Linux `chmod 600 key.pem` = only the owner can read/write.

### Environment Variable
**What:** A named value available to programs, often used for configuration.
**Example:** `PORT=8080`, `NODE_ENV=production`; read by the app at startup.

### Cron / Scheduled Task
**What:** A way to run tasks automatically on a schedule.
**Example:** `0 2 * * * /opt/backup.sh` = every day at 2 a.m. (Linux cron). Windows has Task Scheduler.

---

# 5 — Networking Basics

> Deeper dive: [Networking Handbook](../networking/networking_handbook.md).

### Network
**What:** Connected computers that can exchange data.
**Example:** Office LAN, the internet, a cloud virtual network.

### IP Address
**What:** A numeric address identifying a device on a network.
**Analogy:** A house address for computers.
**Example:** IPv4 `192.168.1.10`, IPv6 `2001:db8::1`.

### Public vs Private IP
**What:** **Public** IPs are reachable on the internet. **Private** IPs (`10.x`, `172.16–31.x`, `192.168.x`) are used inside networks.
**Example:** Your laptop has a private IP; your home router has a public one.

### Port
**What:** A numbered "door" on a computer for a specific service.
**Analogy:** Apartment numbers in a building (the IP is the building).
**Example:** 22 SSH, 80 HTTP, 443 HTTPS, 3306 MySQL, 5432 PostgreSQL.

### Protocol
**What:** Agreed rules for communication.
**Example:** HTTP (web), TCP (reliable delivery), UDP (fast, no guarantee), SSH, DNS.

### HTTP / HTTPS
**What:** The protocol for web traffic. **HTTPS** is HTTP encrypted with TLS (the padlock in the browser).
**Example:** Always use HTTPS for anything with logins or personal data.

### DNS (Domain Name System)
**What:** The internet's phone book. It turns names (`google.com`) into IP addresses.
**Example:** You type `acme.com`, DNS answers `20.50.1.2`.

### Domain Name
**What:** A human-friendly address for a website.
**Example:** `acme.com`, with subdomains like `api.acme.com`.

### URL
**What:** A full web address: protocol + domain + path (+ query).
**Example:** `https://shop.acme.com/products/42?color=red`.

### Router / Switch
**What:** A **router** connects different networks (and routes traffic between them). A **switch** connects devices within one network.
**Example:** Your home router connects your Wi-Fi network to the internet.

### Firewall
**What:** A security barrier that allows or blocks network traffic based on rules.
**Analogy:** A security guard checking who may enter.
**Example:** Allow port 443 from anywhere, port 22 only from the office IP.

### Load Balancer
**What:** Spreads incoming traffic across several servers.
**Analogy:** A host seating guests at different tables so no waiter is overloaded.
**Example:** 3 web servers behind one load balancer; if one dies, traffic goes to the other two.

### Bandwidth / Latency / Throughput
**What:** **Bandwidth** = maximum data per second a link can carry. **Latency** = delay for data to travel (ms). **Throughput** = actual data transferred per second.
**Analogy:** Bandwidth = width of the highway; latency = travel time; throughput = cars actually arriving per hour.
**Example:** A cross-continent call might have 150 ms latency.

### Ping
**What:** A simple tool to check if a host is reachable and measure latency.
**Example:** `ping google.com`. Note that many cloud firewalls block ping.

### VPN (Virtual Private Network)
**What:** An encrypted tunnel connecting you or an office to a private network over the internet.
**Example:** Employees connect via VPN to reach internal systems.

---

# 6 — Cloud Basics

> Deeper dive: [Cloud Handbook](../cloud/cloud_handbook.md).

### Cloud Computing
**What:** Renting computing resources (servers, storage, databases) over the internet, paying for what you use.
**Analogy:** Using electricity from the grid instead of owning a power plant.
**Example:** Microsoft Azure, Amazon Web Services (AWS), Google Cloud (GCP).

### On-Premises (On-Prem)
**What:** Servers in your own building or data centre, managed by your organisation.
**Example:** A company's server room vs cloud hosting.

### IaaS / PaaS / SaaS
**What:** Cloud service models:
- **IaaS** (Infrastructure as a Service): you rent VMs/networks and manage the OS upwards.
- **PaaS** (Platform as a Service): you deploy code and the provider runs the platform.
- **SaaS** (Software as a Service): you just use the finished software.

**Analogy (pizza):** IaaS = rent a kitchen; PaaS = take-and-bake pizza; SaaS = pizza delivered.
**Example:** Azure VMs (IaaS), Azure App Service (PaaS), Microsoft 365 (SaaS).

### Public / Private / Hybrid / Multi-Cloud
**What:** **Public** cloud = shared provider infrastructure. **Private** = dedicated to one organisation. **Hybrid** = cloud + on-prem together. **Multi-cloud** = several cloud providers.
**Example:** Company keeps a mainframe on-prem and runs web apps in Azure (hybrid).

### Region / Availability Zone
**What:** A **region** is a geographic area with data centres (e.g. Central India, West Europe). An **availability zone** is a separate data centre within a region.
**Example:** Spread servers across 3 zones so one building's power failure doesn't take you down.

### Virtual Machine (VM)
**What:** A software-based computer running on a physical server, with its own OS.
**Analogy:** Several apartments inside one building.
**Example:** An Ubuntu VM in Azure running a web server.

### Resource / Resource Group
**What:** A **resource** is anything you create in the cloud (VM, database, network). A **resource group** (Azure) groups related resources for management.
**Example:** `rg-orders-prod` contains the app, database and storage for the orders system.

### Subscription / Account
**What:** The billing and management boundary in a cloud (Azure subscription, AWS account).
**Example:** Separate subscriptions for dev and prod.

### Elasticity / Scalability
**What:** **Scalability** = ability to handle more load by adding resources. **Elasticity** = adding/removing resources automatically as demand changes.
**Example:** A shopping site adds servers during a sale and removes them afterwards.

### Pay-as-you-go
**What:** Paying only for resources while you use them.
**Example:** A VM billed per second/hour. Forgetting to stop test VMs means paying for nothing.

### Serverless (intro)
**What:** Running code without managing servers. It runs on demand and you pay per execution.
**Example:** An Azure Function resizes images whenever a file is uploaded.

---

# 7 — Containers & Orchestration (Intro)

### Container
**What:** A lightweight package containing an app and everything it needs to run, so it runs the same everywhere.
**Analogy:** A shipping container: standard box, any ship or truck can carry it.
**Example:** "It works on my machine" problems disappear because the container *is* the machine setup.

### Docker
**What:** The most popular tool for building and running containers.
**Example:** `docker run nginx` starts a web server container. See [Docker notes](../docker/README.md).

### Image
**What:** A read-only template used to create containers.
**Analogy:** A recipe card (image) vs the cooked dish (container).
**Example:** `python:3.12-slim`, `nginx:1.27`.

### Dockerfile
**What:** A text file with instructions to build an image.
**Example:** `FROM python:3.12-slim`, `COPY . .`, `CMD ["python","app.py"]`. See [Dockerfile Handbook](../docker/dockerfile_handbook/README.md).

### Registry
**What:** A place to store and share images.
**Example:** Docker Hub, GitHub Container Registry, Azure Container Registry.

### Kubernetes (K8s)
**What:** A system that runs and manages many containers across many machines: starting, restarting, scaling and connecting them.
**Analogy:** An orchestra conductor making sure every musician (container) plays at the right time.
**Example:** "Keep 3 copies of my app running; if one crashes, start another."

### Orchestration
**What:** Automated management of many containers or services (placement, scaling, healing, networking).
**Example:** Kubernetes, Docker Swarm, Amazon ECS.

### Microservice (intro)
**What:** An application built as many small services that each do one job.
**Example:** Separate services for users, orders and payments.

---

# 8 — CI/CD & Automation Basics

### CI (Continuous Integration)
**What:** Automatically building and testing code every time someone pushes a change.
**Analogy:** A spell-checker that runs every time you save a document.
**Example:** A push to GitHub triggers tests; a red ❌ means something broke.

### CD (Continuous Delivery / Continuous Deployment)
**What:** **Continuous Delivery**: every good build is *ready* to deploy with one click. **Continuous Deployment**: every good build is deployed *automatically*.
**Example:** After tests pass, the app deploys to staging automatically; production needs approval (delivery).

### Pipeline
**What:** An automated sequence of steps (build → test → deploy).
**Analogy:** A factory assembly line.
**Example:** GitHub Actions workflow, Azure Pipeline, Jenkins job. See [CI/CD guide](../cicd-pipelines/README.md).

### Build Artifact
**What:** The output of a build that gets deployed.
**Example:** A `.zip`, `.jar`, or container image.

### Deployment
**What:** Putting a new version of software onto servers/environments.
**Example:** Deploying version 2.3 to production.

### Release
**What:** Making a version available to users, often with a version number and release notes.
**Example:** "Release 2.3: adds dark mode, fixes login bug."

### Rollback
**What:** Going back to the previous working version after a bad deployment.
**Analogy:** The undo button for a deployment.
**Example:** "Version 2.3 broke checkout, so roll back to 2.2."

### Hotfix
**What:** An urgent fix deployed quickly to production.
**Example:** Patch for a security hole released the same day.

### Infrastructure as Code (intro)
**What:** Creating servers and networks from code files instead of manual clicking.
**Example:** A Terraform file describes a VM; running it creates the VM the same way every time.

### Jenkins / GitHub Actions / Azure DevOps / GitLab CI
**What:** Popular CI/CD tools.
**Example:** Jenkins (self-hosted, plugin-based), GitHub Actions (built into GitHub), Azure DevOps Pipelines (Microsoft), GitLab CI (built into GitLab).

### Trigger
**What:** An event that starts a pipeline.
**Example:** A push, a pull request, a schedule (nightly), or a manual button.

---

# 9 — Data & Storage Basics

### Database
**What:** An organised system for storing and retrieving data.
**Example:** PostgreSQL, MySQL, SQL Server, MongoDB.

### SQL / Relational Database
**What:** Stores data in **tables** with rows and columns, queried with **SQL**.
**Example:** `SELECT * FROM orders WHERE status = 'paid';`.

### NoSQL Database
**What:** Non-table databases (documents, key-value, graphs) designed for flexibility or scale.
**Example:** MongoDB (documents), Redis (key-value), Cosmos DB, DynamoDB.

### Storage (Block / File / Object)
**What:** **Block** = raw disks for VMs. **File** = shared folders. **Object** = files with metadata accessed over HTTP, at massive scale.
**Example:** Azure Disk (block), Azure Files (file), Azure Blob / Amazon S3 (object).

### Backup
**What:** A copy of data kept to recover from loss or damage.
**Example:** Nightly database backup stored in another region.

### Restore
**What:** Recovering data from a backup.
**Example:** Restore yesterday's database after accidental deletion.
**⚠️** Practise restores. Backups you've never restored might not work.

### Replication
**What:** Keeping copies of data on multiple machines or locations automatically.
**Example:** Database replica in another zone takes over if the primary fails.

### Cache (intro)
**What:** A fast, temporary store of frequently used data.
**Analogy:** Keeping your most-used tools on the desk instead of in the shed.
**Example:** Redis stores product details so the database isn't queried every time.

---

# 10 — Monitoring & Operations Basics

### Monitoring
**What:** Continuously checking systems' health and performance.
**Example:** Dashboards showing CPU, memory, error rates; Azure Monitor, Prometheus, Datadog.

### Log
**What:** A timestamped record of events written by software.
**Example:** `2026-10-18T10:00:01Z ERROR payment failed order=A12`.

### Metric
**What:** A number measured over time.
**Example:** Requests per second, CPU %, response time.

### Dashboard
**What:** A screen of charts summarising system health.
**Example:** Grafana dashboard for the web app.

### Alert
**What:** An automatic notification when something needs attention.
**Example:** "Website down" alert sent to the on-call engineer's phone.

### Uptime / Downtime / Availability
**What:** **Uptime** = time the system works. **Downtime** = time it doesn't. **Availability** = uptime as a percentage.
**Example:** 99.9% availability ≈ 43 minutes downtime per month allowed.

### Latency / Response Time
**What:** How long a request takes to get a response.
**Example:** The page loads in 300 ms.

### Incident
**What:** An unplanned event that disrupts or degrades a service.
**Example:** Login failing for all users.

### On-Call
**What:** Being responsible for responding to alerts outside normal hours, in rotation.
**Example:** This week Priya is on-call for the payments system.

### Ticket
**What:** A recorded request or issue in a tracking system.
**Example:** Jira, ServiceNow or Azure Boards ticket: "Increase disk on VM web-01".

### SLA (intro)
**What:** A promise (often contractual) about service level, like availability.
**Example:** "99.9% monthly uptime or customers get credits." See [Advanced: SLI/SLO/SLA](advanced-terms.md#sla-service-level-agreement).

### Postmortem (intro)
**What:** A write-up after an incident: what happened, why, and how to prevent it, without blaming people.
**Example:** "Expired certificate caused outage; we added automatic renewal and expiry alerts."

### Runbook (intro)
**What:** Step-by-step instructions for handling a known task or problem.
**Example:** "How to restart the payment service safely."

### Documentation
**What:** Written information about how systems work and how to operate them.
**Example:** READMEs, architecture diagrams, runbooks, this repo!

---

# 11 — Security Basics

### Authentication (AuthN)
**What:** Proving who you are.
**Example:** Username + password + phone code.

### Authorization (AuthZ)
**What:** Deciding what you're allowed to do after you're authenticated.
**Example:** You can read reports but not delete them.

### MFA (Multi-Factor Authentication)
**What:** Logging in with two or more proofs: something you know (password), have (phone/key), or are (fingerprint).
**Example:** Password + Microsoft Authenticator approval. It blocks the vast majority of account-takeover attacks.

### SSO (Single Sign-On)
**What:** One login gives access to many applications.
**Example:** Log in once with your company Microsoft account to access Jira, GitHub and Azure.

### Password Manager
**What:** An app that generates and stores strong, unique passwords.
**Example:** Bitwarden, 1Password, KeePass.

### Secret
**What:** Sensitive information used to access systems: passwords, API keys, tokens, certificates.
**Example:** A database password. Never put secrets in code or Git.

### Encryption
**What:** Scrambling data so only those with the key can read it.
**Analogy:** A locked box.
**Example:** HTTPS encrypts web traffic; disks are encrypted at rest.

### Certificate (intro)
**What:** A digital ID card that proves a website's identity and enables HTTPS.
**Example:** The padlock icon in your browser means the certificate is valid.

### Least Privilege (intro)
**What:** Give people and systems only the access they need, nothing more.
**Example:** A reporting tool gets read-only database access.

### Vulnerability (intro)
**What:** A weakness that attackers could exploit.
**Example:** An outdated library with a known security flaw.

### Patch / Update
**What:** A software update fixing bugs or security vulnerabilities.
**Example:** Monthly OS security patches on servers.

### Phishing
**What:** Fake emails/messages tricking people into revealing credentials or running malware.
**Example:** "Your password expires today, click here," leading to a fake login page.

### Open Source
**What:** Software whose source code is publicly available to use, modify and share (under a license).
**Example:** Linux, Kubernetes, Git, Terraform's fork OpenTofu.
**⚠️** "Free to use" still comes with license terms. Check them for company use.

---

# 12 — File Formats & Everyday Tools

### YAML
**What:** A human-readable configuration format using indentation.
**Example:** Kubernetes manifests, CI/CD pipelines, Ansible playbooks.

```yaml
app:
  name: orders
  replicas: 3
```
**⚠️** Indentation matters, and tabs aren't allowed.

### JSON
**What:** A data format with `{ }` objects and `[ ]` lists, common in APIs and configs.
**Example:** `{"name": "orders", "replicas": 3}`.

### Markdown
**What:** A simple text format for documents (`#` headings, `**bold**`, lists). Renders nicely on GitHub.
**Example:** README.md files, and every page in this repo.

### Configuration File
**What:** A file holding settings for an application or tool.
**Example:** `nginx.conf`, `appsettings.json`, `.env`.

### IDE / Code Editor
**What:** An application for writing code, with helpers like autocomplete and debugging.
**Example:** Visual Studio Code, IntelliJ IDEA, Visual Studio.

### Jira / Azure Boards / Confluence
**What:** **Jira/Azure Boards**: track work items and tickets. **Confluence**: team documentation wiki.
**Example:** Sprint board in Jira; runbooks in Confluence.

### Slack / Microsoft Teams
**What:** Team chat tools, often connected to alerts and pipelines ("ChatOps").
**Example:** Pipeline posts "✅ Deployed v2.3 to prod" in the #deployments channel.

### ChatOps
**What:** Running operational tasks and getting notifications through chat.
**Example:** Typing `/deploy orders staging` in Slack triggers a deployment bot.

### AI Coding Assistant / Agent
**What:** AI tools that help write, explain or change code, and some can run commands.
**Example:** Claude Code, Google Antigravity, GitHub Copilot. See the [AI Coding Agents guide](../ai-coding-agents/README.md).
**⚠️** Always review what they change, and don't give them production access.

---

**Next:** [Intermediate Terms ➡️](intermediate-terms.md) · [Advanced Terms](advanced-terms.md)

[⬅️ Back to Glossary Index](README.md)
