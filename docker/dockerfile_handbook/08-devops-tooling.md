# 08 — DevOps Tooling, CI/CD Agents & Monitoring (Examples 83–94)

[⬅️ Back to Handbook Index](README.md) · [⬅️ Previous: Databases & Infra](07-databases-infra.md)

---

## 🧾 Why containerise DevOps tools?

As a DevOps engineer, *your* tools — Terraform, kubectl, Ansible, Azure CLI — are software
too. Putting them in images gives you:

- **The same tool versions** on every laptop and CI agent ("Terraform 1.9.8 everywhere").
- **No "install 15 tools" onboarding doc** — `docker run` and go.
- **Clean, disposable CI agents** that start fresh for every job.

### The "download a binary" pattern (used throughout this chapter)

Many tools are distributed as a single binary on a website/GitHub. The secure pattern:

```
1. Pin the VERSION in an ARG
2. Download the binary  +  its published SHA-256 checksum
3. Verify the checksum (fail the build if it doesn't match → tampered/corrupt download)
4. Install, clean up — all in ONE RUN
5. Use TARGETARCH so the same Dockerfile builds for amd64 and arm64
```

> ⚠️ **DevOps gotcha:** `curl https://get.something.sh | bash` in a Dockerfile = running an
> unverified script from the internet as root, with whatever version it fetches today.
> Prefer pinned versions + checksum verification.

> 💡 `curl -fsSL` flags: `-f` fail on HTTP errors (404 → non-zero exit instead of saving an
> HTML error page as your "binary"), `-s` silent, `-S` still show errors, `-L` follow redirects.

---

## Table of Contents

| # | Example | Key idea |
|---|---------|----------|
| 83 | [Terraform runner](#example-83--terraform-runner) | Checksum-verified binary |
| 84 | [Ansible control node](#example-84--ansible-control-node) | Python tool + collections |
| 85 | [Kubernetes toolbox (kubectl, helm, kustomize)](#example-85--kubernetes-toolbox) | Multi-binary, multi-arch |
| 86 | [Azure CLI + Bicep](#example-86--azure-cli--bicep) | Extend Microsoft's image |
| 87 | [AWS CLI v2](#example-87--aws-cli-v2) | Installer zip in a build stage |
| 88 | [Jenkins controller with plugins + JCasC](#example-88--jenkins-controller-with-plugins) | Jenkins as code |
| 89 | [Jenkins inbound agent with build tools](#example-89--jenkins-inbound-agent-with-build-tools) | Custom agent |
| 90 | [Azure DevOps self-hosted agent](#example-90--azure-devops-self-hosted-agent) | Containerised pipeline agent |
| 91 | [GitHub Actions self-hosted runner](#example-91--github-actions-self-hosted-runner) | Ephemeral runner |
| 92 | [Prometheus with baked config + rules](#example-92--prometheus-with-baked-config) | Validated monitoring config |
| 93 | [Grafana with provisioned datasources & dashboards](#example-93--grafana-with-provisioning) | Dashboards as code |
| 94 | [Database backup job (pg_dump → cloud storage)](#example-94--database-backup-job) | Scheduled ops job |

---

## Example 83 — Terraform runner

**🧾 What is this?** **Terraform** creates cloud infrastructure from code files (`.tf`).
This image pins the Terraform version and adds tools commonly used alongside it.

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.20

ARG TERRAFORM_VERSION=1.9.8
# Set automatically by buildx (amd64 / arm64)
ARG TARGETARCH

RUN apk add --no-cache bash git openssh-client curl jq ca-certificates \
 && cd /tmp \
 && curl -fsSLO "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_${TARGETARCH}.zip" \
 && curl -fsSLO "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_SHA256SUMS" \
 && grep "linux_${TARGETARCH}.zip" "terraform_${TERRAFORM_VERSION}_SHA256SUMS" | sha256sum -c - \
 && unzip "terraform_${TERRAFORM_VERSION}_linux_${TARGETARCH}.zip" -d /usr/local/bin \
 && rm -f /tmp/terraform_* \
 && terraform version

RUN adduser -D -u 1001 tf
USER 1001
WORKDIR /workspace

# Plugin cache: providers downloaded once are reused across runs (mount a volume here)
ENV TF_PLUGIN_CACHE_DIR=/home/tf/.terraform.d/plugin-cache \
    TF_IN_AUTOMATION=1
RUN mkdir -p "$TF_PLUGIN_CACHE_DIR"

ENTRYPOINT ["terraform"]
CMD ["--help"]
```

**▶️ Use:**

```bash
docker run --rm -v "$PWD":/workspace -e ARM_CLIENT_ID -e ARM_CLIENT_SECRET \
  -e ARM_TENANT_ID -e ARM_SUBSCRIPTION_ID tf-runner:1.9.8 plan
```

**🔍 Explained:**

- `grep ... | sha256sum -c -` — picks the line for our file from HashiCorp's checksum list and
  verifies it. Mismatch → non-zero exit → build fails.
- `terraform version` at the end — a smoke test that the binary actually runs on this OS/arch.
- `-v "$PWD":/workspace` — mounts your `.tf` files into the container.
- `-e ARM_CLIENT_ID` (no value) — passes the variable **from your shell** without typing the
  secret on the command line.
- `TF_IN_AUTOMATION=1` — tidier output for CI.

**⚠️ DevOps Gotchas:**

- Terraform is under the **BSL license** since 1.6. **OpenTofu** (`tofu`) is the open-source
  fork; same pattern applies. Know your company's policy.
- Without `ARG TARGETARCH` declared, it's **empty** → URL ends in `linux_.zip` → 404. With
  classic `docker build` (non-buildx), pass `--build-arg TARGETARCH=amd64`.
- **Never bake cloud credentials into the image.** Pass them at runtime, or better, use
  workload identity / OIDC federation in CI.

---

## Example 84 — Ansible control node

**🧾 What is this?** **Ansible** configures servers over SSH using YAML "playbooks". It's a
Python tool, plus "collections" (plugin packs for Azure, AWS, Kubernetes…).

`requirements.txt`:

```text
ansible-core==2.17.5
pywinrm==0.5.0
```

`requirements.yml` (Ansible collections):

```yaml
collections:
  - name: ansible.posix
    version: "1.6.2"
  - name: community.general
    version: "9.5.0"
```

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ANSIBLE_HOST_KEY_CHECKING=False \
    ANSIBLE_FORCE_COLOR=1 \
    ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-client sshpass git \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.yml /tmp/
RUN pip install -r /tmp/requirements.txt \
 && ansible-galaxy collection install -r /tmp/requirements.yml -p /usr/share/ansible/collections \
 && rm /tmp/requirements.*

RUN useradd --create-home --uid 1001 ansible
USER 1001
WORKDIR /work
ENTRYPOINT ["ansible-playbook"]
```

**▶️ Use:**

```bash
docker run --rm -v "$PWD":/work -v ~/.ssh/id_ed25519:/home/ansible/.ssh/id_ed25519:ro \
  ansible-runner -i inventory.ini site.yml
```

**🔍 Explained:**

- `ansible-core` + pinned collections = only what you need (the full `ansible` package
  bundles ~100 collections and is much larger).
- `ANSIBLE_COLLECTIONS_PATH` — where Ansible looks for installed collections.
- SSH key mounted **read-only** (`:ro`) at runtime — never `COPY` a private key into an image.

**⚠️ DevOps Gotchas:**

- `ANSIBLE_HOST_KEY_CHECKING=False` is convenient but disables protection against
  man-in-the-middle. In production, manage `known_hosts` properly.
- SSH refuses private keys with loose permissions ("UNPROTECTED PRIVATE KEY FILE").
  Mounted files keep host permissions; on Windows hosts they often appear as `0777`.
  Copy the key inside the container to `~/.ssh` with `chmod 600` in an entrypoint if needed.

---

## Example 85 — Kubernetes toolbox

**🧾 What is this?** One image with **kubectl** (talk to Kubernetes), **helm** (Kubernetes
package manager), and **kustomize** (YAML customisation) — for CI deploy stages.

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.20 AS download
ARG TARGETARCH
ARG KUBECTL_VERSION=v1.31.2
ARG HELM_VERSION=v3.16.2
ARG KUSTOMIZE_VERSION=v5.5.0
RUN apk add --no-cache curl tar
WORKDIR /dl

# kubectl — publishes a .sha256 file next to each binary
RUN curl -fsSLO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl" \
 && curl -fsSLO "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${TARGETARCH}/kubectl.sha256" \
 && echo "$(cat kubectl.sha256)  kubectl" | sha256sum -c - \
 && chmod +x kubectl

# helm — tarball + .sha256sum file
RUN curl -fsSLO "https://get.helm.sh/helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" \
 && curl -fsSLO "https://get.helm.sh/helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz.sha256sum" \
 && sha256sum -c "helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz.sha256sum" \
 && tar -xzf "helm-${HELM_VERSION}-linux-${TARGETARCH}.tar.gz" --strip-components=1 "linux-${TARGETARCH}/helm"

# kustomize — GitHub release with a checksums.txt
RUN curl -fsSLO "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_${TARGETARCH}.tar.gz" \
 && curl -fsSLO "https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/checksums.txt" \
 && grep "linux_${TARGETARCH}.tar.gz" checksums.txt | sha256sum -c - \
 && tar -xzf "kustomize_${KUSTOMIZE_VERSION}_linux_${TARGETARCH}.tar.gz"

FROM alpine:3.20
RUN apk add --no-cache bash git ca-certificates jq yq gettext \
 && adduser -D -u 1001 deployer
COPY --from=download /dl/kubectl /dl/helm /dl/kustomize /usr/local/bin/
USER 1001
WORKDIR /work
CMD ["bash"]
```

**🔍 Explained:**

- **Download stage** has `curl`/`tar`; the final image gets just three binaries + a few
  handy tools (`jq`/`yq` for JSON/YAML, `gettext` provides `envsubst` for templating).
- Each tool publishes checksums differently — read each project's release page.
- `--strip-components=1 "linux-amd64/helm"` — extract only the `helm` file, dropping the folder.

**⚠️ DevOps Gotchas:**

- **kubectl version skew:** kubectl is supported within **±1 minor version** of the
  cluster. kubectl 1.31 against a 1.28 cluster may misbehave. Keep the toolbox in step with
  your clusters.
- AKS with Entra ID auth needs **`kubelogin`** too; EKS needs the **AWS CLI** for tokens.

---

## Example 86 — Azure CLI + Bicep

**🧾 What is this?** The **Azure CLI** (`az`) manages Azure. **Bicep** is Azure's IaC language.
We extend Microsoft's official image.

```dockerfile
FROM mcr.microsoft.com/azure-cli:2.65.0

# Install Bicep to a fixed location and a couple of extensions, at a pinned version
ARG BICEP_VERSION=v0.30.23
RUN az bicep install --version ${BICEP_VERSION} \
 && az extension add --name resource-graph --yes \
 && az extension add --name containerapp --yes \
 && az version

ENV AZURE_CORE_COLLECT_TELEMETRY=false \
    AZURE_CORE_ONLY_SHOW_ERRORS=true

WORKDIR /work
CMD ["bash"]
```

**🔍 Explained:**

- `az bicep install --version` — pins Bicep (otherwise `az` downloads the latest on first use,
  at runtime, in every CI job).
- `az extension add ... --yes` — pre-installs extensions so pipelines don't download them each run.
- `AZURE_CORE_COLLECT_TELEMETRY=false` — no telemetry from CI.

**⚠️ DevOps Gotchas:**

- `az bicep install` puts Bicep in **the current user's** home (`~/.azure/bin`). If you
  later switch `USER`, that user won't find it. Install as the user who will run it, or set
  `AZURE_BICEP_USE_BINARY_FROM_PATH` and copy the binary to `/usr/local/bin`.
- In pipelines, log in with **workload identity federation** (OIDC) rather than client secrets.

---

## Example 87 — AWS CLI v2

**🧾 What is this?** AWS CLI v2 is distributed as an installer zip (not pip). We install it in
a build stage and copy the installed folder.

```dockerfile
# syntax=docker/dockerfile:1
FROM debian:bookworm-slim AS install
ARG AWSCLI_VERSION=2.18.13
ARG TARGETARCH
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl unzip ca-certificates \
 && rm -rf /var/lib/apt/lists/*
# AWS uses x86_64 / aarch64 naming; map from Docker's amd64 / arm64
RUN case "${TARGETARCH}" in \
      amd64) ARCH=x86_64 ;; \
      arm64) ARCH=aarch64 ;; \
      *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
 && curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}-${AWSCLI_VERSION}.zip" -o awscliv2.zip \
 && unzip -q awscliv2.zip \
 && ./aws/install --install-dir /opt/aws-cli --bin-dir /opt/aws-bin

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates groff-base less jq \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1001 aws
COPY --from=install /opt/aws-cli /opt/aws-cli
RUN ln -s /opt/aws-cli/v2/current/bin/aws /usr/local/bin/aws && aws --version
USER 1001
ENTRYPOINT ["aws"]
```

**🔍 Explained:**

- `case "${TARGETARCH}" in ... esac` — shell "switch" statement to translate architecture names.
  Different vendors name CPUs differently (amd64 = x86_64, arm64 = aarch64).
- `groff-base less` — needed for `aws help` pages.
- AWS CLI v2 bundles its own Python — glibc needed (doesn't run on Alpine without workarounds).

**⚠️ DevOps Gotchas:**

- AWS also signs the installer with **GPG**; for high-security environments verify the
  `.sig` file with AWS's public key in the build stage.
- `amazon/aws-cli` is an official ready-made image; build your own only when you need extra tools.

---

## Example 88 — Jenkins controller with plugins

**🧾 What is this?** **Jenkins** is a CI/CD server. Normally you click through a setup
wizard and install plugins manually (not reproducible). Here, plugins and configuration are
**code** — "JCasC" (Jenkins Configuration as Code).

`plugins.txt`:

```text
# Format: plugin-id:version. Pin the exact versions running in your tested Jenkins
# (Manage Jenkins → Plugins → Installed, or the Script Console) — the IDs below are real,
# replace "latest" with pinned versions before going to production.
configuration-as-code:latest
git:latest
workflow-aggregator:latest
kubernetes:latest
credentials-binding:latest
```

`casc.yaml`:

```yaml
jenkins:
  systemMessage: "Jenkins configured as code — changes via Git only"
  numExecutors: 0          # controller doesn't run builds; agents do
  securityRealm:
    local:
      allowsSignup: false
      users:
        - id: "admin"
          password: "${JENKINS_ADMIN_PASSWORD}"   # injected at runtime
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false
```

`Dockerfile`:

```dockerfile
FROM jenkins/jenkins:2.479.1-lts-jdk21

# Skip the interactive setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false" \
    CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml

COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

COPY --chown=jenkins:jenkins casc.yaml /usr/share/jenkins/ref/casc.yaml
```

**🔍 Explained:**

- `jenkins-plugin-cli` — official tool that downloads plugins and their dependencies at
  **build time** (pinned versions).
- `/usr/share/jenkins/ref/` — files here are copied into `JENKINS_HOME` on startup.
- `numExecutors: 0` — best practice: the controller only coordinates; builds run on agents.
- The base image already runs as the non-root `jenkins` user.

**⚠️ DevOps Gotchas:**

- **`JENKINS_HOME` (`/var/jenkins_home`) must be a persistent volume** — it holds job
  history and credentials.
- Plugin version conflicts are Jenkins' biggest pain. Upgrading the core image may require
  plugin bumps; test upgrades in a staging Jenkins first.
- Don't mount the Docker socket (`/var/run/docker.sock`) into Jenkins casually — it gives
  **root on the host** to anyone who can write a pipeline. Use Kubernetes agents or
  rootless builders (Kaniko/BuildKit) instead.

---

## Example 89 — Jenkins inbound agent with build tools

**🧾 What is this?** An **agent** connects to the controller and runs builds. The official
agent image has Java + the agent program; we add the tools our builds need.

```dockerfile
# Pin to a specific version tag from Docker Hub (jenkins/inbound-agent) in production
FROM jenkins/inbound-agent:latest-jdk21

# Switch to root only to install packages
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git make zip unzip jq python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Node.js from the official image (pinned major) — avoids distro-outdated versions
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
COPY --from=node:22-bookworm-slim /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && node --version && npm --version

# Back to the unprivileged agent user
USER jenkins
```

**🔍 Explained:**

- `USER root` → install → `USER jenkins`: the standard pattern for extending images that run
  as non-root.
- `COPY --from=node:22-bookworm-slim` — borrow a Node installation from the official Node
  image (same Debian release → compatible glibc).
- The base image's `ENTRYPOINT` (`jenkins-agent`) connects to the controller using env
  vars like `JENKINS_URL`, `JENKINS_SECRET`, `JENKINS_AGENT_NAME`.

**⚠️ DevOps Gotchas:**

- **"Fat" agent images** with every tool become huge and hard to patch. With the
  Kubernetes plugin, prefer **pod templates** with small tool-specific sidecar containers
  (one for Node, one for Maven…).

---

## Example 90 — Azure DevOps self-hosted agent

**🧾 What is this?** Microsoft-hosted agents are convenient, but you may need a
**self-hosted** agent (private network access, custom tools, bigger machines). This image
downloads the agent at startup, registers it with your Azure DevOps organisation, runs jobs,
and unregisters on shutdown.

`start.sh`:

```bash
#!/bin/bash
set -euo pipefail

: "${AZP_URL:?AZP_URL is required, e.g. https://dev.azure.com/myorg}"
: "${AZP_TOKEN:?AZP_TOKEN (PAT with Agent Pools read & manage) is required}"
AZP_POOL="${AZP_POOL:-Default}"
AZP_AGENT_NAME="${AZP_AGENT_NAME:-$(hostname)}"

cd /azp/agent

# Download the latest agent package for this architecture (once per container)
if [ ! -f ./config.sh ]; then
  PKG_URL=$(curl -fsSL -u "user:${AZP_TOKEN}" \
    "${AZP_URL}/_apis/distributedtask/packages/agent?platform=${AGENT_PLATFORM}&top=1" \
    | jq -r '.value[0].downloadUrl')
  curl -fsSL "$PKG_URL" | tar -xz
fi

cleanup() {
  echo "Removing agent registration..."
  ./config.sh remove --unattended --auth PAT --token "${AZP_TOKEN}" || true
}
trap 'cleanup; exit 0' EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM

./config.sh --unattended \
  --url "${AZP_URL}" --auth PAT --token "${AZP_TOKEN}" \
  --pool "${AZP_POOL}" --agent "${AZP_AGENT_NAME}" \
  --replace --acceptTeeEula

# Don't leak the token to pipeline jobs
unset AZP_TOKEN

# --once: take ONE job then exit (ephemeral agent — clean environment every job)
./run.sh --once & wait $!
```

`Dockerfile`:

```dockerfile
# syntax=docker/dockerfile:1
FROM ubuntu:22.04

ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git jq libicu70 unzip zip \
 && rm -rf /var/lib/apt/lists/*

# Map Docker arch names to Azure DevOps agent platform names
RUN case "${TARGETARCH}" in \
      amd64) echo "linux-x64"   > /etc/azp-platform ;; \
      arm64) echo "linux-arm64" > /etc/azp-platform ;; \
      *) exit 1 ;; \
    esac

RUN useradd --create-home --uid 1001 agent \
 && mkdir -p /azp/agent && chown -R agent:agent /azp
COPY --chmod=755 start.sh /azp/start.sh

USER 1001
WORKDIR /azp
ENTRYPOINT ["/bin/bash", "-c", "export AGENT_PLATFORM=$(cat /etc/azp-platform) && exec /azp/start.sh"]
```

**🔍 Explained:**

- `DEBIAN_FRONTEND=noninteractive` — stops `apt` from asking interactive questions (e.g.
  timezone) that would hang the build.
- `libicu70` — the agent is a .NET app and needs ICU (globalization library).
- `: "${AZP_URL:?message}"` — bash idiom: fail with that message if the variable is unset.
- `trap ... EXIT/INT/TERM` — when the container stops, unregister the agent so the pool
  doesn't fill with "offline" ghosts.
- `./run.sh --once` — **ephemeral** agent: one job, then exit. The orchestrator
  (Kubernetes/KEDA) starts a fresh one → no leftovers from previous jobs.

**⚠️ DevOps Gotchas:**

- The PAT is sensitive. Pass it via a **Kubernetes Secret / Key Vault**, scope it minimally
  (Agent Pools: Read & manage), and rotate it.
- `libicu70` is the Ubuntu 22.04 package name; Ubuntu 24.04 uses `libicu74`. Mismatch →
  "Couldn't find a valid ICU package".
- For auto-scaling agents on AKS, look at **KEDA's `azure-pipelines` scaler**; Azure also
  offers **Managed DevOps Pools** which may remove the need to run your own.

---

## Example 91 — GitHub Actions self-hosted runner

**🧾 What is this?** Same idea for GitHub Actions. GitHub publishes an official runner image
(used by Actions Runner Controller on Kubernetes); we extend it with tools.

```dockerfile
FROM ghcr.io/actions/actions-runner:2.320.0

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl jq unzip make \
 && rm -rf /var/lib/apt/lists/*

COPY --chmod=755 entrypoint.sh /home/runner/entrypoint.sh
USER runner
ENTRYPOINT ["/home/runner/entrypoint.sh"]
```

`entrypoint.sh` (standalone use, without Actions Runner Controller):

```bash
#!/bin/bash
set -euo pipefail
: "${GH_URL:?e.g. https://github.com/my-org}"
: "${RUNNER_TOKEN:?registration token from the GitHub API/UI}"

./config.sh --unattended --ephemeral \
  --url "$GH_URL" --token "$RUNNER_TOKEN" \
  --name "${RUNNER_NAME:-$(hostname)}" \
  --labels "${RUNNER_LABELS:-self-hosted,linux,docker}" \
  --replace
unset RUNNER_TOKEN
exec ./run.sh
```

**🔍 Explained:**

- `--ephemeral` — runner de-registers itself after **one** job (clean slate every time).
- `exec ./run.sh` — runner becomes PID 1 and receives shutdown signals.
- The **registration token** is short-lived (1 hour) — generate it via the GitHub API at
  container start, or let **Actions Runner Controller (ARC)** handle it on Kubernetes.

**⚠️ DevOps Gotchas:**

- **Never attach self-hosted runners to public repos** — anyone can open a PR that runs
  code on your infrastructure.
- Jobs needing `docker build` require Docker-in-Docker or a rootless builder; ARC supports
  a `dind` mode. Each has security trade-offs.

---

## Example 92 — Prometheus with baked config

**🧾 What is this?** **Prometheus** collects metrics (numbers over time: CPU, request
counts, error rates) by "scraping" HTTP endpoints. We bake its config and alert rules into
the image and **validate them at build time**.

`prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: api
    metrics_path: /metrics
    static_configs:
      - targets: ["api:8080"]
```

`rules/api.yml`:

```yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: critical }
        annotations:
          summary: "API 5xx error rate above 5% for 10 minutes"
```

`Dockerfile`:

```dockerfile
FROM prom/prometheus:v2.55.0
COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY rules/ /etc/prometheus/rules/
# promtool ships in the image — fail the build on invalid config or rules
RUN promtool check config /etc/prometheus/prometheus.yml
```

**🔍 Explained:**

- `promtool check config` — validates the main file **and** the rule files it references.
- The base image already runs as `nobody` and stores data in `/prometheus` (mount a volume).

**⚠️ DevOps Gotchas:**

- In Kubernetes, most teams use the **Prometheus Operator / kube-prometheus-stack** Helm
  chart (config via `ServiceMonitor` resources) rather than a custom image.
- Default retention is **15 days**; set `--storage.tsdb.retention.time` / size to avoid
  filling the disk.

---

## Example 93 — Grafana with provisioning

**🧾 What is this?** **Grafana** draws dashboards from Prometheus (and many other sources).
**Provisioning** = data sources and dashboards defined in files, so no one has to click them
together after every deploy.

`provisioning/datasources/prometheus.yaml`:

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
```

`provisioning/dashboards/provider.yaml`:

```yaml
apiVersion: 1
providers:
  - name: default
    folder: "Platform"
    type: file
    disableDeletion: true
    allowUiUpdates: false
    options:
      path: /var/lib/grafana/dashboards
```

`Dockerfile`:

```dockerfile
FROM grafana/grafana:11.3.0
COPY provisioning/ /etc/grafana/provisioning/
COPY dashboards/   /var/lib/grafana/dashboards/
ENV GF_AUTH_ANONYMOUS_ENABLED=false \
    GF_USERS_ALLOW_SIGN_UP=false \
    GF_ANALYTICS_REPORTING_ENABLED=false \
    GF_INSTALL_PLUGINS=""
```

**🔍 Explained:**

- `/etc/grafana/provisioning/` — Grafana reads data sources and dashboard providers from
  here on startup.
- `dashboards/*.json` — dashboards exported from the Grafana UI (Share → Export → JSON) and
  committed to Git.
- `GF_<SECTION>_<KEY>` env vars override any `grafana.ini` setting.
- `allowUiUpdates: false` — prevents edits in the UI that would be lost on redeploy.

**⚠️ DevOps Gotchas:**

- The admin password: `GF_SECURITY_ADMIN_PASSWORD` (or `__FILE` variant) at runtime — never
  leave the default `admin/admin`.
- If `/var/lib/grafana` is mounted as a volume, it **hides** the dashboards copied there in
  the image. Put dashboards in a different path (e.g. `/etc/grafana/dashboards`) and point
  the provider at it.

---

## Example 94 — Database backup job

**🧾 What is this?** A small image that dumps a PostgreSQL database, compresses it, and
uploads it to cloud storage. Run on a schedule as a **Kubernetes CronJob**.

`backup.sh`:

```bash
#!/bin/bash
set -euo pipefail

: "${PGHOST:?}"; : "${PGUSER:?}"; : "${PGPASSWORD:?}"; : "${PGDATABASE:?}"
: "${RCLONE_REMOTE:?e.g. azureblob:backups/postgres}"

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
FILE="/tmp/${PGDATABASE}-${STAMP}.dump"

echo "[$(date -u +%FT%TZ)] starting dump of ${PGDATABASE}"
# -Fc = custom compressed format (restorable with pg_restore, supports selective restore)
pg_dump --format=custom --no-owner --file "$FILE"

echo "uploading $(du -h "$FILE" | cut -f1) to ${RCLONE_REMOTE}"
rclone copy "$FILE" "${RCLONE_REMOTE}/" --no-traverse

rm -f "$FILE"
echo "[$(date -u +%FT%TZ)] backup complete"
```

`Dockerfile`:

```dockerfile
FROM alpine:3.20
# Client version must be >= the server's major version
RUN apk add --no-cache bash postgresql16-client rclone ca-certificates tzdata \
 && adduser -D -u 1001 backup
COPY --chmod=755 backup.sh /usr/local/bin/backup.sh
USER 1001
WORKDIR /tmp
ENTRYPOINT ["/usr/local/bin/backup.sh"]
```

**🔍 Explained:**

- `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` — standard env vars that `pg_dump` reads
  automatically.
- **rclone** — "rsync for cloud storage"; works with Azure Blob, S3, GCS. Configure it with
  env vars like `RCLONE_CONFIG_AZUREBLOB_TYPE=azureblob`, `RCLONE_CONFIG_AZUREBLOB_ACCOUNT=...`.
- `set -euo pipefail` — stop on errors, on unset variables, and on failures inside pipes.
  Without it, a failed `pg_dump` might still "succeed" and upload an empty file.

**⚠️ DevOps Gotchas:**

- **`pg_dump` client older than the server fails** ("server version mismatch"). Match or
  exceed the server's major version.
- **A backup you've never restored is not a backup.** Schedule a periodic restore test job.
- Large databases fill the container's ephemeral `/tmp` → stream directly instead:
  `pg_dump -Fc | rclone rcat remote:path/file.dump`.

---

**Next:** [09 — Data Science, ML & AI ➡️](09-data-ml-ai.md)
