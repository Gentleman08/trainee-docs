# Case Study 2 — Implementing a DevSecOps CI/CD Pipeline
> Automating security checks to shift left and prevent vulnerable deployments.

## 1. Project Overview
In modern software development, security cannot be an afterthought bolted on right before release. This project focuses on integrating security seamlessly into the development lifecycle ("shifting left") for a modern React frontend and Node.js backend application. 

The primary objective is to build an automated DevSecOps pipeline that acts as a security gatekeeper. The pipeline scans for vulnerable third-party dependencies (SCA), analyzes custom source code for common flaws like SQLi and XSS (SAST), and actively attacks the deployed staging environment (DAST). If any Critical or High vulnerabilities are detected, the pipeline automatically blocks the Pull Request (PR) and prevents the code from reaching production, thus protecting end-users and the business's data.

## 2. Architecture Diagram

The following ASCII diagram illustrates the ingestion of code changes and the automated query/inference pipelines for the security tooling.

```text
  [ Developer ]
       |
       | 1. Push code / Open PR
       v
  [ GitHub Pull Request ]
       |
       | 2. Trigger Workflow
       v
+-------------------------------------------------------------+
|                     GitHub Actions (CI)                     |
|                                                             |
|  +----------------+   +-----------------+   +------------+  |
|  | Build & Test   |-->| SCA (Snyk/npm)  |-->| SAST (Sem) |  |
|  | (Node & React) |   | Check 3rd party |   | Source Code|  |
|  +----------------+   +-----------------+   +------------+  |
|                               |                    |        |
+-------------------------------|--------------------|--------+
                                v                    v
                            [ Vulns Found? ] ---Yes--> ( Block PR / Notify )
                                |
                                No
                                |
                                v
                      [ Staging Environment ] <-- (Docker / ECS)
                                |
                                v
+-------------------------------------------------------------+
|                     GitHub Actions (CD)                     |
|                                                             |
|                       +----------------+                    |
|                       | DAST (ZAP)     |                    |
|                       | Dynamic Scan   |                    |
|                       +----------------+                    |
|                               |                             |
+-------------------------------|-----------------------------+
                                v
                            [ Vulns Found? ] ---Yes--> ( Block Deploy / Alert )
                                |
                                No
                                |
                                v
                     [ Production Deployment ]
```

## 3. Tech Stack Table

| Component | Tool / Technology | Purpose |
| :--- | :--- | :--- |
| **Source Control** | GitHub & GitHub Actions | Code repository, PR management, and CI/CD orchestration. |
| **SCA** | Dependabot & Snyk | Software Composition Analysis. Identifies CVEs in `package.json` dependencies. |
| **SAST** | Semgrep | Static Application Security Testing. Scans source code for hardcoded secrets, injection flaws, and bad practices. |
| **DAST** | OWASP ZAP (Zed Attack Proxy) | Dynamic Application Security Testing. Spiders and actively attacks the live staging URL. |
| **Deployment**| Docker & AWS ECS | Containerizes the Node/React apps and deploys to staging/production clusters. |

## 4. Step-by-Step Build

### Phase 1: Foundation and SCA Integration
1. Set up the GitHub repository with the React+Node.js codebase.
2. Enable GitHub Dependabot to automatically track and open PRs for vulnerable `npm` packages.
3. Integrate the Snyk Action in the CI pipeline to fail the build if High/Critical package vulnerabilities exist.

### Phase 2: Static Code Analysis (SAST)
1. Add Semgrep to the CI pipeline to run against the Node.js API and React frontend code.
2. Configure custom Semgrep rule-sets (e.g., `p/owasp-top-ten`, `p/javascript`).
3. Set the action to output SARIF results so vulnerabilities appear directly in the GitHub Security tab.

### Phase 3: Dynamic Application Security Testing (DAST)
1. Configure an automated deployment to an ephemeral Staging environment upon PR merge to `main`.
2. Add OWASP ZAP Full Scan to the deployment pipeline.
3. Target the Staging URL with ZAP to discover runtime issues (e.g., missing security headers, unauthenticated endpoints).

### Phase 4: Quality Gates and Blocking
1. Define GitHub Branch Protection Rules enforcing that all security checks must pass before a merge is allowed.
2. Configure failure thresholds for Snyk, Semgrep, and ZAP to fail the action only on High or Critical findings.

## 5. Code Snippets

### GitHub Actions Security Pipeline YAML
This snippet demonstrates the CI security gates (SCA + SAST) configured in `.github/workflows/security.yml`.

```yaml
name: DevSecOps CI Pipeline
on: [pull_request]

jobs:
  sast_and_sca:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      # 1. Software Composition Analysis (SCA)
      - name: Snyk Node.js Monitor
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --fail-on=all

      # 2. Static Application Security Testing (SAST)
      - name: Semgrep Code Scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: "p/default p/owasp-top-ten p/javascript"
          generateSarif: "1"
        # Semgrep action natively fails on high-severity findings

      # 3. Upload SARIF for GitHub Security Dashboard integration
      - name: Upload SARIF file
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
```

### Developer Patching Workflow
When a developer introduces a vulnerability (e.g., importing a vulnerable version of `lodash`), the PR build fails. The workflow looks like this:

```bash
# 1. Developer sees CI failure for SCA.
# CI Output: "✗ High severity vulnerability found in lodash < 4.17.21"

# 2. Developer updates the package locally:
npm update lodash
npm audit fix

# 3. Developer commits the security patch and pushes to PR
git add package.json package-lock.json
git commit -m "fix(security): update lodash to patch CVE-2021-23337"
git push origin feature/new-ui

# 4. CI automatically re-runs. 
# Snyk passes, branch protection goes green, PR is eligible for merge.
```

## 6. Deployment Steps

After the CI pipeline (SAST & SCA) passes and the PR is merged, the CD pipeline kicks off:
1. **Build & Push**: Docker images for Node.js API and React Frontend are built and pushed to Amazon ECR.
2. **Deploy to Staging**: An ECS task update is triggered, spinning up the new containers in the Staging VPC.
3. **Run DAST**: Once Staging is healthy, `zaproxy/action-full-scan` targets `https://staging.myapp.com`.
4. **Deploy to Prod**: If ZAP finds 0 Critical/High issues, manual approval is requested, followed by an ECS task update in the Production environment.

## 7. Evaluation & Monitoring

* **GitHub Security Advisory Dashboard**: Tracks overall repository health, showing a burndown chart of resolved vulnerabilities.
* **Pipeline Metrics**: We measure pipeline execution time. SAST and SCA typically complete in < 2 minutes. DAST is longer (15-20 minutes).
* **Mean Time to Remediate (MTTR)**: Tracked via Jira. Integration creates tickets automatically for findings that hit the `main` branch.

## 8. Cost Analysis

* **GitHub Actions**: ~2,000 CI/CD minutes/month. Free tier for public repos, otherwise ~$0.008/minute ($16/month).
* **Snyk**: Free tier (200 tests/month). Team tier is $25/developer/month.
* **Semgrep**: Free open-source community edition utilized.
* **OWASP ZAP**: Free and open-source.
* **AWS Staging Env**: ~$45/month for the ephemeral ECS cluster and application load balancers.
* **Total Estimated Cost**: ~$86/month (excluding developer seats for Snyk).

## 9. Production Gotchas

* **False Positives in SAST**: Semgrep initially flagged testing utility files as having insecure random number generation. *Fix: Exclude `__tests__` and `*.spec.js` directories from the scan.*
* **DAST Scanner Timeouts**: ZAP full scans were taking over 45 minutes and failing the CD pipeline due to timeout constraints. *Fix: Configured ZAP to use an API definition file (OpenAPI spec) to guide the spider, reducing scan time to 15 minutes.*
* **Managing Secrets Securely**: Early on, developers hardcoded `.env` files in PRs to make staging work. Semgrep flagged these. *Fix: Moved entirely to GitHub Actions Secrets and AWS Secrets Manager; the code now expects environment variables injected at runtime.*
* **State Mutation in Staging**: DAST scans were submitting random data to the staging database, polluting test data. *Fix: Created a dedicated DAST database and scheduled an automatic teardown/re-seed of the database after ZAP completes.*

## 10. Lessons Learned

* **Developer Friction is Real**: Initially, blocking PRs on "Medium" severity vulnerabilities ground development to a halt. We had to adjust thresholds to block *only* on "High/Critical" until the backlog was cleared.
* **Shift-Left Saves Time**: Catching a vulnerable `npm` package in the PR stage takes 2 minutes to fix. Catching it in production via a manual penetration test takes a week of meetings, ticket prioritization, and out-of-band hotfixes.
* **DAST is Best for APIs**: For SPAs (React), traditional spiders struggle. Supplying ZAP with an OpenAPI (Swagger) document of the backend yielded vastly better dynamic vulnerability discovery than trying to spider the React frontend.
* **Security is a Culture**: Tools don't fix vulnerabilities; developers do. Providing clear, actionable remediation advice inside the PR comments was crucial for adoption.
