# 02 — Container Image Pipelines (Scenarios 16–23)

[⬅️ Back to Index](README.md) · [⬅️ Previous: CI Build & Test](01-ci-build-test.md)

---

> How to build Docker images in CI, push them to registries (GHCR, ACR, ECR), and make them
> fast, multi-architecture, scanned, signed and promotable. For how to *write* the
> Dockerfiles themselves, see the
> [Dockerfile Handbook](../docker/dockerfile_handbook/README.md).

### Registry cheat sheet

| Registry | Full image name | CI login (the modern way) |
|----------|----------------|---------------------------|
| **GitHub Container Registry (GHCR)** | `ghcr.io/<owner>/<image>:<tag>` | `GITHUB_TOKEN` with `packages: write` |
| **Azure Container Registry (ACR)** | `<name>.azurecr.io/<image>:<tag>` | OIDC → `az acr login`, or an ADO Docker registry service connection |
| **Amazon ECR** | `<account>.dkr.ecr.<region>.amazonaws.com/<image>:<tag>` | IAM role → `aws ecr get-login-password` |
| **Docker Hub** | `docker.io/<user>/<image>:<tag>` | Access token stored as a secret |

### Tagging strategy (use several tags per image)

| Tag | Example | Purpose |
|-----|---------|---------|
| Git SHA | `orders-api:3f2c1ab` | **Immutable**, exact traceability. **Deploy using this** (or the digest) |
| Semantic version | `orders-api:1.4.2` | Human-friendly releases (from Git tags) |
| Branch | `orders-api:main` | "Latest build of main" for dev environments |
| `latest` | `orders-api:latest` | Convenience only. **Never deploy production from `latest`** |
| Digest | `orders-api@sha256:9b1e…` | Content address. Can't be changed, even by re-pushing a tag |

---

## Table of Contents

| # | Scenario | Key skills |
|---|----------|-----------|
| 16 | [Build & push to each platform's native registry](#scenario-16--build-and-push-to-the-native-registry) | GHCR, ACR, ECR basics |
| 17 | [GitHub Actions → ACR and ECR with OIDC](#scenario-17--github-actions-to-acr-and-ecr-with-oidc) | Cross-cloud, no secrets |
| 18 | [Fast builds: Docker layer caching in CI](#scenario-18--fast-builds-with-docker-layer-caching) | Registry/GHA cache |
| 19 | [Multi-architecture images (amd64 + arm64)](#scenario-19--multi-architecture-images) | buildx, QEMU, native runners |
| 20 | [Vulnerability scanning gate](#scenario-20--vulnerability-scanning-gate) | Trivy, SARIF |
| 21 | [SBOM + image signing and verification](#scenario-21--sbom-and-image-signing) | Syft, cosign |
| 22 | [Build once, promote the same image across environments](#scenario-22--build-once-promote-across-environments) | Retag/copy by digest |
| 23 | [PR image smoke test (build, run, curl — no push)](#scenario-23--pr-image-smoke-test) | Test the container itself |

---

## Scenario 16 — Build and push to the native registry

**🎯 Goal:** On every push to `main`, build the Dockerfile and push it to the platform's own
registry, tagged with the commit SHA and `main`.

### GitHub Actions → GHCR

```yaml
name: Image
on:
  push:
    branches: [main]

permissions:
  contents: read
  packages: write                   # allows GITHUB_TOKEN to push to GHCR

env:
  IMAGE: ghcr.io/${{ github.repository }}     # e.g. ghcr.io/acme/orders-api

jobs:
  image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.IMAGE }}:${{ github.sha }}
            ${{ env.IMAGE }}:main
```

### Azure DevOps → ACR

```yaml
trigger: [main]

pool:
  vmImage: ubuntu-latest

variables:
  dockerRegistryServiceConnection: acr-acme-prod   # "Docker Registry" service connection to ACR
  imageRepository: orders-api
  tag: $(Build.SourceVersion)

steps:
  - task: Docker@2
    displayName: Build and push
    inputs:
      command: buildAndPush
      containerRegistry: $(dockerRegistryServiceConnection)
      repository: $(imageRepository)
      dockerfile: Dockerfile
      buildContext: .
      tags: |
        $(tag)
        main
```

### AWS CodeBuild → ECR

> The CodeBuild project needs **privileged mode** enabled (to run Docker). Its IAM role needs
> ECR push permissions (`ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`,
> `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, `ecr:PutImage`).

```yaml
version: 0.2

env:
  variables:
    IMAGE_REPO_NAME: orders-api
  exported-variables:
    - IMAGE_URI

phases:
  pre_build:
    commands:
      - ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      - REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com"
      - aws ecr get-login-password --region "$AWS_DEFAULT_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
      - COMMIT=$(echo "$CODEBUILD_RESOLVED_SOURCE_VERSION" | cut -c1-7)
      - IMAGE_URI="${REGISTRY}/${IMAGE_REPO_NAME}:${COMMIT}"
  build:
    commands:
      - docker build -t "$IMAGE_URI" -t "${REGISTRY}/${IMAGE_REPO_NAME}:main" .
  post_build:
    commands:
      - |
        if [ "$CODEBUILD_BUILD_SUCCEEDING" != "1" ]; then
          echo "Build failed; not pushing"; exit 1
        fi
      - docker push "$IMAGE_URI"
      - docker push "${REGISTRY}/${IMAGE_REPO_NAME}:main"
      # File consumed by CodePipeline's ECS deploy action (Chapter 03)
      - printf '[{"name":"orders-api","imageUri":"%s"}]' "$IMAGE_URI" > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json
```

**🔍 Explained:**

- **GitHub:** `docker/setup-buildx-action` enables BuildKit features (cache export,
  multi-platform). `build-push-action` builds and pushes in one step.
- **Azure DevOps:** `Docker@2 buildAndPush` handles login, build and push. The service
  connection holds the registry credentials (or workload identity).
- **CodeBuild:** plain Docker CLI commands. `AWS_DEFAULT_REGION` is set automatically. The
  account ID comes from `sts get-caller-identity`.
- **`imagedefinitions.json`** tells CodePipeline's ECS deploy action which image to roll out
  for which container name.

**⚠️ Gotchas:**

- **ECR repositories must exist before pushing** (unlike GHCR/Docker Hub). Create them with
  IaC, or enable ECR's "create on push" repository creation templates.
- **ADO `Docker@2 buildAndPush` doesn't accept `arguments:`** (like `--build-arg`). For build
  args, use separate `build` (with `arguments`) and `push` commands.
- **GHCR packages start out private** and aren't linked to the repo. Add the OCI label
  `org.opencontainers.image.source` (the metadata action does this) to link them.
- **Docker Hub rate limits** apply to `FROM` pulls in your Dockerfile too. Log in to Docker
  Hub as well, or use a pull-through cache (ACR cache rules, ECR pull-through cache).

---

## Scenario 17 — GitHub Actions to ACR and ECR with OIDC

**🎯 Goal:** Code lives in GitHub, but images must go to **Azure ACR** and/or **AWS ECR**,
with **no stored passwords**. (One-time cloud setup is in [Chapter 05](05-devsecops.md).)

### GitHub Actions → Azure Container Registry

```yaml
name: Push to ACR
on:
  push:
    branches: [main]

permissions:
  id-token: write          # REQUIRED for OIDC — lets the job request an identity token
  contents: read

env:
  ACR_NAME: acmeprodacr
  IMAGE: acmeprodacr.azurecr.io/orders-api

jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Azure login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}           # not secrets — these IDs aren't sensitive
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: ACR login
        run: az acr login --name "$ACR_NAME"

      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ${{ env.IMAGE }}:${{ github.sha }}
```

### GitHub Actions → Amazon ECR

```yaml
name: Push to ECR
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-orders-api-ecr-push
          aws-region: eu-west-1

      - name: ECR login
        id: ecr
        uses: aws-actions/amazon-ecr-login@v2

      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ${{ steps.ecr.outputs.registry }}/orders-api:${{ github.sha }}
```

**🔍 Explained:**

- **`id-token: write`** without this permission, the job can't get an OIDC token and login
  fails with `Unable to get ACTIONS_ID_TOKEN_REQUEST_URL`.
- **`azure/login@v2`** exchanges the GitHub token for an Entra ID token, via the federated
  credential on the app registration / managed identity.
- **`configure-aws-credentials`** calls `sts:AssumeRoleWithWebIdentity` and sets temporary
  `AWS_*` env vars for later steps.
- **`amazon-ecr-login`** outputs the registry hostname (`<account>.dkr.ecr.<region>.amazonaws.com`).

**⚠️ Gotchas:**

- **The OIDC "subject" must match exactly.** An Azure federated credential for
  `repo:acme/orders-api:ref:refs/heads/main` **won't** work for a job that uses
  `environment: prod`. That job's subject is `repo:acme/orders-api:environment:prod`.
  Error: `AADSTS70021: No matching federated identity record found`.
- **The identity needs push rights:** `AcrPush` on the ACR, or the right ECR permissions in
  the IAM role policy.

---

## Scenario 18 — Fast builds with Docker layer caching

**🎯 Goal:** CI runners are fresh VMs, so Docker's local layer cache is empty on every run and
a 2-minute build takes 10 minutes. Store the cache **outside** the runner.

### GitHub Actions — GitHub Actions cache backend + metadata action

```yaml
- uses: docker/setup-buildx-action@v3

- name: Generate tags & labels
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=sha,format=long
      type=ref,event=branch
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}

- uses: docker/build-push-action@v6
  with:
    context: .
    push: ${{ github.event_name != 'pull_request' }}
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

### Azure DevOps — registry cache with buildx

```yaml
steps:
  - task: Docker@2
    displayName: Login to ACR
    inputs:
      command: login
      containerRegistry: acr-acme-prod

  - bash: |
      docker buildx create --use --name ci-builder
      docker buildx build \
        --cache-from type=registry,ref=acmeprodacr.azurecr.io/orders-api:buildcache \
        --cache-to   type=registry,ref=acmeprodacr.azurecr.io/orders-api:buildcache,mode=max \
        -t acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion) \
        --push .
    displayName: Build & push with registry cache
```

### AWS CodeBuild — registry cache in ECR (or CodeBuild local Docker layer cache)

```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      - REPO="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/orders-api"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "${REPO%%/*}"
      - docker buildx create --use --name ci-builder
  build:
    commands:
      - >
        docker buildx build
        --cache-from type=registry,ref=${REPO}:buildcache
        --cache-to type=registry,ref=${REPO}:buildcache,mode=max,image-manifest=true,oci-mediatypes=true
        -t ${REPO}:${CODEBUILD_RESOLVED_SOURCE_VERSION}
        --push .
```

**🔍 Explained:**

- **`docker/metadata-action`** generates a consistent set of tags and OCI labels from Git
  refs, so you don't have to write them by hand.
- **`mode=max`** caches layers from **all** stages (including the build stage of a
  multi-stage Dockerfile). The default `min` caches only the final image's layers.
- **`type=gha`** stores the cache in the GitHub Actions cache. `type=registry` stores it as a
  special image tag (`:buildcache`) in your registry.
- **`image-manifest=true,oci-mediatypes=true`** is required for ECR, which doesn't accept the
  default cache manifest format.
- **`${REPO%%/*}`** is bash: strip everything after the first `/`, leaving just the registry host.

**⚠️ Gotchas:**

- **The cache only helps if the Dockerfile is cache-friendly** (dependencies copied before
  source code; see Dockerfile Handbook 0.4). Bad layer ordering defeats any cache.
- **The `gha` cache counts toward GitHub's 10 GB repo cache limit,** and big images can evict
  your npm/pip caches.
- **CodeBuild's built-in "local Docker layer cache"** only helps when builds land on the same
  host in quick succession. It's not guaranteed, unlike a registry cache.

---

## Scenario 19 — Multi-architecture images

**🎯 Goal:** One image tag that runs on both **amd64** (most servers) and **arm64** (AWS
Graviton, Azure Cobalt, Apple Silicon). Graviton/ARM instances are often around 20% cheaper.

### GitHub Actions — QEMU emulation (simple) or native runners (fast)

```yaml
# Option A: one job, emulation (easy; slow for compiled languages)
- uses: docker/setup-qemu-action@v3
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v6
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
```

```yaml
# Option B: native runner per architecture, then merge into one manifest
jobs:
  build:
    strategy:
      matrix:
        include:
          - platform: linux/amd64
            runner: ubuntu-latest
          - platform: linux/arm64
            runner: ubuntu-24.04-arm         # GitHub-hosted ARM runner
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: build
        uses: docker/build-push-action@v6
        with:
          platforms: ${{ matrix.platform }}
          outputs: type=image,name=ghcr.io/${{ github.repository }},push-by-digest=true,name-canonical=true,push=true
      - name: Save digest
        run: |
          mkdir -p /tmp/digests
          digest="${{ steps.build.outputs.digest }}"
          touch "/tmp/digests/${digest#sha256:}"
      - uses: actions/upload-artifact@v4
        with:
          name: digest-${{ strategy.job-index }}
          path: /tmp/digests/*

  merge:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: /tmp/digests
          pattern: digest-*
          merge-multiple: true
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Create multi-arch manifest
        working-directory: /tmp/digests
        run: |
          docker buildx imagetools create \
            -t ghcr.io/${{ github.repository }}:${{ github.sha }} \
            $(printf 'ghcr.io/${{ github.repository }}@sha256:%s ' *)
```

### Azure DevOps

```yaml
steps:
  - task: Docker@2
    inputs:
      command: login
      containerRegistry: acr-acme-prod
  - bash: |
      docker run --privileged --rm tonistiigi/binfmt --install arm64   # enable QEMU emulation
      docker buildx create --use
      docker buildx build --platform linux/amd64,linux/arm64 \
        -t acmeprodacr.azurecr.io/orders-api:$(Build.SourceVersion) --push .
    displayName: Multi-arch build
```

### AWS CodeBuild — native ARM build + manifest merge

Create two CodeBuild projects (or a batch build): one on `LINUX_CONTAINER` with an x86 image,
one on `ARM_CONTAINER` with `aws/codebuild/amazonlinux2-aarch64-standard:3.0`. Each pushes
`orders-api:<sha>-amd64` / `orders-api:<sha>-arm64`. A final step merges them:

```yaml
version: 0.2
phases:
  build:
    commands:
      - ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
      - REPO="${ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/orders-api"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "${REPO%%/*}"
      - TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)
      - docker manifest create "${REPO}:${TAG}" "${REPO}:${TAG}-amd64" "${REPO}:${TAG}-arm64"
      - docker manifest push "${REPO}:${TAG}"
```

**🔍 Explained:**

- **A multi-arch image is a "manifest list"**: one tag pointing to several per-architecture
  images. `docker pull` automatically picks the right one.
- **QEMU** emulates ARM on x86. It's correct, but **5–20× slower** for compile-heavy builds.
  Native ARM runners avoid that.
- **`push-by-digest`** pushes each architecture's image without a tag. `imagetools create`
  then combines the digests under the final tag.

**⚠️ Gotchas:**

- **"exec format error" in production** means the image wasn't built for that node's
  architecture. Check with `docker buildx imagetools inspect <image>`.
- **If the Dockerfile downloads binaries**, it must use `TARGETARCH` (Dockerfile Handbook
  Ex 45, 83), or the arm64 image silently contains amd64 binaries.

---

## Scenario 20 — Vulnerability scanning gate

**🎯 Goal:** Scan every image for known vulnerabilities (CVEs). **Fail** the pipeline on
CRITICAL/HIGH issues that have a fix available, and show the findings in the platform's
security UI.

### GitHub Actions — Trivy + upload to Code Scanning

```yaml
permissions:
  contents: read
  security-events: write          # to upload SARIF results

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build (load locally, don't push yet)
        uses: docker/build-push-action@v6
        with:
          load: true
          tags: orders-api:scan

      - name: Trivy — report everything as SARIF
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: orders-api:scan
          format: sarif
          output: trivy.sarif
          ignore-unfixed: true

      - uses: github/codeql-action/upload-sarif@v3
        if: ${{ !cancelled() }}
        with:
          sarif_file: trivy.sarif

      - name: Trivy — gate on CRITICAL/HIGH
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: orders-api:scan
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"
```

### Azure DevOps — Trivy in a container, results as JUnit

```yaml
steps:
  - task: Docker@2
    inputs:
      command: build
      repository: orders-api
      tags: scan
      dockerfile: Dockerfile

  - bash: |
      docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        -v $(System.DefaultWorkingDirectory):/out aquasec/trivy:0.56.2 image \
        --format template --template "@contrib/junit.tpl" -o /out/trivy-junit.xml \
        --ignore-unfixed orders-api:scan
      docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.56.2 image \
        --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 orders-api:scan
    displayName: Trivy scan

  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: trivy-junit.xml
      testRunTitle: Container vulnerabilities
```

### AWS CodeBuild — Trivy CLI (plus ECR's own scanning)

```yaml
version: 0.2
phases:
  install:
    commands:
      - curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.56.2
  build:
    commands:
      - docker build -t orders-api:scan .
      - trivy image --format json -o trivy.json orders-api:scan
      - trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 orders-api:scan
artifacts:
  files: [trivy.json]
```

Also enable **ECR enhanced scanning (Amazon Inspector)** on the registry. It rescans images
continuously when new CVEs are published. In Azure, **Microsoft Defender for Containers** does
the same for ACR.

**🔍 Explained:**

- **Scan before push** (`load: true` loads the image into the local Docker daemon), so
  vulnerable images never reach the registry.
- **`--ignore-unfixed`** skips CVEs that have no fixed version yet. Failing on those blocks
  every build with nothing the team can do about it.
- **SARIF** is a standard format for security findings. GitHub shows them under
  **Security → Code scanning**.
- **Run two scans:** one that reports everything, and one that gates only on what matters.

**⚠️ Gotchas:**

- **Scanning once at build time isn't enough.** New CVEs are published daily, so an image
  that was clean last month may be critical today. Combine CI scanning with registry scanning
  and scheduled rescans.
- **You need an exception process.** Use a `.trivyignore` file with CVE IDs, a
  **justification and an expiry date**. Otherwise people disable the gate entirely.
- **Mounting `/var/run/docker.sock`** gives that container root-equivalent access to the host.
  That's acceptable on throw-away hosted agents, but think carefully on shared self-hosted agents.

---

## Scenario 21 — SBOM and image signing

**🎯 Goal:** Supply-chain security. For every image you publish:

- **SBOM** (Software Bill of Materials) — a list of every package inside it.
- **Signature** — cryptographic proof that *your pipeline* built it.

Then make the cluster refuse unsigned images.

### GitHub Actions — Syft SBOM + cosign keyless signing

```yaml
permissions:
  contents: read
  packages: write
  id-token: write                     # keyless signing uses the workflow's OIDC identity

jobs:
  release-image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: build
        uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          provenance: mode=max          # SLSA build provenance attestation
          sbom: true                    # BuildKit-generated SBOM attestation

      - name: Generate SPDX SBOM file (also kept as an artifact)
        uses: anchore/sbom-action@v0
        with:
          image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
          format: spdx-json
          output-file: sbom.spdx.json

      - uses: sigstore/cosign-installer@v3

      - name: Sign image (keyless) — always sign the DIGEST, not a tag
        run: cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}

      - name: Attach SBOM as a signed attestation
        run: |
          cosign attest --yes --type spdxjson --predicate sbom.spdx.json \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
```

**Verify** (in a deploy pipeline, or via a Kubernetes admission policy):

```bash
cosign verify ghcr.io/acme/orders-api@sha256:9b1e... \
  --certificate-identity-regexp '^https://github.com/acme/orders-api/.github/workflows/.+@refs/heads/main$' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

### Azure DevOps — cosign with a key stored in Azure Key Vault

```yaml
steps:
  - task: AzureCLI@2
    displayName: Sign image with Key Vault key
    inputs:
      azureSubscription: arm-acme-prod            # service connection (workload identity)
      scriptType: bash
      scriptLocation: inlineScript
      inlineScript: |
        curl -sSfL -o cosign https://github.com/sigstore/cosign/releases/download/v2.4.1/cosign-linux-amd64
        chmod +x cosign
        az acr login --name acmeprodacr
        DIGEST=$(az acr repository show --name acmeprodacr \
          --image orders-api:$(Build.SourceVersion) --query digest -o tsv)
        ./cosign sign --yes --key azurekms://acme-signing-kv.vault.azure.net/cosign-key \
          acmeprodacr.azurecr.io/orders-api@${DIGEST}
```

### AWS CodeBuild — cosign with an AWS KMS key

```yaml
version: 0.2
phases:
  post_build:
    commands:
      # REPO and TAG were set in pre_build exactly as in Scenario 16
      - curl -sSfL -o /usr/local/bin/cosign https://github.com/sigstore/cosign/releases/download/v2.4.1/cosign-linux-amd64
      - chmod +x /usr/local/bin/cosign
      - DIGEST=$(aws ecr describe-images --repository-name orders-api --image-ids imageTag=${TAG} --query 'imageDetails[0].imageDigest' --output text)
      - cosign sign --yes --key awskms:///alias/cosign-signing "${REPO}@${DIGEST}"
```

> AWS also offers **AWS Signer + Notation** for signing ECR images. Azure supports
> **Notation with Key Vault** for ACR. Pick one standard per organisation.

**🔍 Explained:**

- **Keyless signing (GitHub):** cosign gets a short-lived certificate from Sigstore that is
  bound to the workflow's identity. There's no key to manage. The verify command checks
  **which repo and branch** produced the image.
- **KMS-based signing (ADO/AWS):** the private key never leaves Key Vault/KMS. The pipeline
  identity only needs "sign" permission on that key.
- **Sign the digest:** tags can be moved to another image, digests can't.
- **Enforcement** happens at deploy time: Kyverno / Sigstore policy-controller / Ratify on
  Kubernetes reject images without a valid signature.

**⚠️ Gotchas:**

- **Signing without verification is theatre.** The security value only comes when something
  **refuses** unsigned images.
- **The certificate identity regex must match your workflow path and branch exactly.** A
  sloppy regex like `.*` accepts images signed by **any** GitHub workflow anywhere.

---

## Scenario 22 — Build once, promote across environments

**🎯 Goal:** The image tested in **dev** must be byte-for-byte the image that reaches **prod**.
Never rebuild for prod. Promote the exact digest, often into a **separate prod registry**.

```
 build ─► dev-registry/orders-api:3f2c1ab ──test──► copy SAME digest ─► prod-registry/orders-api:3f2c1ab
```

### GitHub Actions — copy between registries with `crane`

```yaml
jobs:
  promote:
    runs-on: ubuntu-latest
    environment: production           # requires approval (Chapter 03)
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: imjasonh/setup-crane@v0.4
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
      - run: |
          az acr login --name acmedevacr
          az acr login --name acmeprodacr
          # crane copies manifests + layers WITHOUT pulling/rebuilding; multi-arch preserved
          crane copy acmedevacr.azurecr.io/orders-api:${{ github.sha }} \
                     acmeprodacr.azurecr.io/orders-api:${{ github.sha }}
          crane digest acmeprodacr.azurecr.io/orders-api:${{ github.sha }}
```

### Azure DevOps — `az acr import` (server-side copy, no Docker needed)

```yaml
- stage: PromoteToProd
  dependsOn: TestInDev
  jobs:
    - deployment: Promote
      environment: production
      pool: { vmImage: ubuntu-latest }
      strategy:
        runOnce:
          deploy:
            steps:
              - task: AzureCLI@2
                inputs:
                  azureSubscription: arm-acme-prod
                  scriptType: bash
                  scriptLocation: inlineScript
                  inlineScript: |
                    az acr import \
                      --name acmeprodacr \
                      --source acmedevacr.azurecr.io/orders-api:$(Build.SourceVersion) \
                      --image orders-api:$(Build.SourceVersion)
```

### AWS — cross-account copy (or ECR replication rules)

```yaml
version: 0.2
phases:
  build:
    commands:
      - TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)
      - DEV="111111111111.dkr.ecr.eu-west-1.amazonaws.com/orders-api"
      - PROD="222222222222.dkr.ecr.eu-west-1.amazonaws.com/orders-api"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "${DEV%%/*}"
      - aws ecr get-login-password | docker login --username AWS --password-stdin "${PROD%%/*}"   # role must be allowed by the prod repo policy
      - docker buildx imagetools create -t "${PROD}:${TAG}" "${DEV}:${TAG}"   # copies manifest list + layers
```

Alternatively, an **ECR replication rule** in the dev account can automatically replicate
images to the prod account/region. Prod then deploys only from its own registry.

**🔍 Explained:**

- **Rebuilding for prod** (even from the same commit) can pull newer base images or
  dependencies, so you'd ship something you never tested.
- **`crane copy` / `az acr import` / `imagetools create`** copy images registry-to-registry,
  keeping the digest identical.
- **A separate prod registry** limits who can write to prod. Only the promotion identity can.

**⚠️ Gotchas:**

- **Promote by digest or immutable tag.** If someone re-pushes the dev tag between testing
  and promotion, you'd promote the wrong image. Turn on **tag immutability** in ECR/ACR for
  release repositories.
- **Cross-account ECR access** needs both an **IAM policy** on the caller and a **repository
  policy** on the target repo.

---

## Scenario 23 — PR image smoke test

**🎯 Goal:** On a PR, build the image **without pushing**, start the container and check
that it actually serves traffic. This catches "builds fine, crashes on start" problems:
a missing file, a wrong `CMD`, a bad port.

### GitHub Actions

```yaml
name: Image smoke test
on: pull_request

permissions:
  contents: read

jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          load: true
          tags: orders-api:pr-${{ github.event.number }}
          cache-from: type=gha
      - name: Run container and probe health endpoint
        run: |
          docker run -d --name app -p 8080:8080 \
            -e DATABASE_URL=sqlite:///tmp/test.db \
            orders-api:pr-${{ github.event.number }}
          for i in $(seq 1 30); do
            if curl -fsS http://localhost:8080/health; then echo "✅ healthy"; exit 0; fi
            sleep 2
          done
          echo "❌ container never became healthy"; docker logs app; exit 1
      - name: Image size report
        if: always()
        run: docker image ls orders-api --format '{{.Repository}}:{{.Tag}} {{.Size}}' >> "$GITHUB_STEP_SUMMARY"
```

### Azure DevOps

```yaml
pr:
  branches: { include: [main] }

pool:
  vmImage: ubuntu-latest

steps:
  - script: docker build -t orders-api:pr-$(System.PullRequest.PullRequestNumber) .
    displayName: Build
  - bash: |
      docker run -d --name app -p 8080:8080 orders-api:pr-$(System.PullRequest.PullRequestNumber)
      for i in $(seq 1 30); do
        curl -fsS http://localhost:8080/health && exit 0
        sleep 2
      done
      docker logs app; exit 1
    displayName: Smoke test
```

### AWS CodeBuild

```yaml
version: 0.2
phases:
  build:
    commands:
      - docker build -t orders-api:pr .
      - docker run -d --name app -p 8080:8080 orders-api:pr
      # Avoid "exit 0" inside buildspec commands; use a flag and only exit on failure
      - |
        healthy=0
        for i in $(seq 1 30); do
          if curl -fsS http://localhost:8080/health; then healthy=1; break; fi
          sleep 2
        done
        if [ "$healthy" != "1" ]; then docker logs app; exit 1; fi
```

**🔍 Explained:**

- **`load: true`** puts the built image into the runner's local Docker, so `docker run` can use it.
- **The retry loop** (30 × 2 s) gives slow-starting apps (Java!) up to a minute.
- **`docker logs app` on failure** puts the reason for the crash right in the CI log.
- **`$GITHUB_STEP_SUMMARY`** writes Markdown to the run's summary page. Good for sizes and reports.

**⚠️ Gotchas:**

- **The app must be able to start with test configuration** (e.g. SQLite or a stub instead
  of the production DB). Ask developers for a "smoke" config mode.
- **`exit 0` inside a multi-line `run:`** ends the step successfully. Make sure the failure
  path really ends with a non-zero exit.

---

**Next:** [03 — Deployment Scenarios ➡️](03-deployments.md)
