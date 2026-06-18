# Batch 7 — Security Testing Tools & Methodologies
> The arsenal used to uncover application vulnerabilities.

## 1. Burp Suite (Proxy, Intruder, Repeater)
**Definition**
An all-in-one platform for web application security testing. It intercepts web traffic (Proxy), automates customized attacks (Intruder), and allows manual modification/re-sending of individual requests (Repeater).

**Real-World Dev/Testing Example**
You use the Proxy to capture a checkout request, send it to Repeater, change the item price parameter from `$50` to `$1`, and re-send it to see if the server validates the price on the backend.

**ASCII Diagram**
```text
Browser ---> [ Burp Proxy (Intercept & Modify) ] ---> Web Server
```

**Gotchas & Dev Context**
- Don't rely solely on client-side validation; Burp bypasses UI checks easily.
- Rate limit your Intruder attacks to avoid crashing the dev server.
- Intercepting HTTPS requires installing Burp’s CA certificate in your browser.

**Production FAQ**
- *How do we patch parameter tampering found via Burp?*
  Always validate and calculate sensitive values (like prices or discounts) server-side based on trusted session data, not client inputs.

---

## 2. OWASP ZAP
**Definition**
The Zed Attack Proxy (ZAP) is a free, open-source alternative to Burp Suite, maintained by OWASP, ideal for automated security scanning and CI/CD integration.

**Real-World Dev/Testing Example**
You configure a GitHub Actions workflow to run a ZAP Baseline Scan against your staging environment upon every pull request to catch common misconfigurations automatically.

**Gotchas & Dev Context**
- Highly scriptable via API, making it devops-friendly.
- The automated active scanner can be noisy and might generate false positives.
- Headless mode is perfect for Dockerized environments.

**Production FAQ**
- *How do we handle ZAP's active scan breaking our test database?*
  Use mock data or a dedicated sandbox environment for active scanning. Implement CSRF tokens and strong input validation to prevent automated injections.

---

## 3. Nmap
**Definition**
Network Mapper (Nmap) is an open-source tool used to discover hosts and services on a computer network by sending packets and analyzing the responses.

**Real-World Dev/Testing Example**
Running `nmap -p 1-65535 -sV target.com` to check if a developer accidentally exposed a Redis port (6379) or unauthenticated MongoDB instance to the public internet.

**Gotchas & Dev Context**
- Default scans only check the top 1,000 ports. Use `-p-` for all 65,535.
- Aggressive scans (`-A`) are noisy and will easily trigger IDS/IPS (Intrusion Detection Systems).
- NSE (Nmap Scripting Engine) scripts can automatically test for specific vulnerabilities.

**Production FAQ**
- *An Nmap scan shows port 3306 (MySQL) open to the internet. How to fix?*
  Bind the database service to `localhost` (127.0.0.1) or restrict access via firewall/Security Groups so only the application server IP can connect.

---

## 4. Nikto
**Definition**
A fast, command-line web server scanner that tests for thousands of potentially dangerous files, outdated server software, and missing security headers.

**Real-World Dev/Testing Example**
Running `nikto -h http://example.com` quickly reveals that the server is returning verbose error pages and is missing the `Strict-Transport-Security` header.

**Gotchas & Dev Context**
- Scans are extremely loud and easily blocked by Web Application Firewalls (WAF).
- It doesn't test for business logic flaws, only known server misconfigurations and files.
- Great for a quick "sanity check" on a newly provisioned Apache/Nginx server.

**Production FAQ**
- *Nikto flagged my server version in the HTTP headers. Is this bad?*
  Yes, it enables targeted attacks. Patch this by setting `ServerTokens Prod` in Apache or `server_tokens off` in Nginx to hide version details.

---

## 5. DirBuster / Gobuster
**Definition**
Tools used to brute-force directories and file names on web and application servers to find hidden or unlinked content.

**Real-World Dev/Testing Example**
Using Gobuster with a common wordlist to find a forgotten `http://site.com/admin_backup.zip` or a `/dev` directory containing debug logs.

**ASCII Diagram**
```text
Gobuster ---> HTTP GET /admin   (403 Forbidden)
Gobuster ---> HTTP GET /backup  (200 OK) -> BINGO!
```

**Gotchas & Dev Context**
- Gobuster (written in Go) is much faster than the older Java-based DirBuster.
- Rate limiting and WAFs will drop connections if you scan too fast.
- You must use high-quality wordlists (like SecLists) to find relevant files.

**Production FAQ**
- *How do we stop directory brute-forcing?*
  Implement rate limiting, deploy a WAF, and ensure no sensitive backups, `.git` folders, or `.env` files are deployed to the web root.

---

## 6. Fuzzing
**Definition**
An automated software testing technique that involves providing invalid, unexpected, or random data as inputs to a program to detect crashes or memory leaks.

**Real-World Dev/Testing Example**
Using a tool like `ffuf` to send thousands of weird characters and extremely long strings into a search API endpoint to see if it causes an Unhandled Exception or SQL error.

**Gotchas & Dev Context**
- Excellent for finding buffer overflows in C/C++ apps or unhandled JSON parsing errors in APIs.
- Fuzzing can easily exhaust server resources (CPU/RAM); monitor systems during testing.
- Requires robust error handling to prevent the app from crashing entirely.

**Production FAQ**
- *Fuzzing caused our API to return a 500 Internal Server Error with a stack trace. Fix?*
  Implement global exception handling. Catch all unhandled errors and return a generic `500` message without leaking code structures or database queries.

---

## 7. Automated DAST (Dynamic Application Security Testing)
**Definition**
Tools that interact with a running web application from the outside, exactly like an attacker would, to find vulnerabilities via simulated attacks.

**Real-World Dev/Testing Example**
Running a commercial DAST tool against a staging environment overnight to verify that newly deployed forms aren't vulnerable to Reflected XSS.

**Gotchas & Dev Context**
- Requires a deployed, running application.
- Struggles with complex multi-step workflows (like multi-page checkout forms) without manual training.
- Does not have access to source code, so it can't point out the exact line of failing code.

**Production FAQ**
- *Our DAST scanner keeps reporting false positives for XSS. What to do?*
  Tune the scanner rules. For genuine findings, implement Context-Aware Output Encoding (e.g., using React/Angular default protections or secure templating engines).

---

## 8. SAST (Static Application Security Testing)
**Definition**
"White-box" testing tools that analyze source code, bytecode, or binaries for security vulnerabilities *without* executing the program.

**Real-World Dev/Testing Example**
Integrating SonarQube or Semgrep into the CI pipeline. If a developer commits `exec(user_input)`, the SAST tool blocks the PR immediately.

**ASCII Diagram**
```text
Dev Code -> [ SAST Scanner (e.g., Semgrep) ] -> Reports "Hardcoded Secret" -> Block PR
```

**Gotchas & Dev Context**
- Finds vulnerabilities early in the SDLC (Shift-Left).
- Notorious for high false-positive rates; requires careful tuning by security teams.
- Cannot detect runtime environment issues or misconfigurations.

**Production FAQ**
- *SAST found SQL Injection in our legacy codebase. Best mitigation?*
  Refactor the affected queries to use Prepared Statements (Parameterized Queries) or an ORM, which inherently prevents SQL injection.

---

## 9. SCA (Software Composition Analysis)
**Definition**
Tools that inspect open-source components, frameworks, and libraries used in a project to identify known vulnerabilities (CVEs) and license compliance issues.

**Real-World Dev/Testing Example**
Running `npm audit` or using Snyk to discover that the `log4j` or `express` version defined in `package.json` has a known Remote Code Execution vulnerability.

**Gotchas & Dev Context**
- Over 70% of modern applications consist of third-party libraries; SCA is critical.
- Transitive dependencies (dependencies of your dependencies) are often where the worst bugs hide.
- Needs continuous monitoring, as a safe library today might get a CVE tomorrow.

**Production FAQ**
- *SCA flagged a vulnerable dependency, but upgrading breaks our app. What now?*
  If you can't upgrade, see if the vulnerable function is actually reachable in your code. If yes, apply a virtual patch (via WAF) or backport the security fix yourself until you can refactor.

---

## 10. Manual Source Code Review
**Definition**
A human-led, line-by-line examination of source code to identify complex business logic flaws, authorization bypasses, and subtle bugs that automated tools miss.

**Real-World Dev/Testing Example**
A senior engineer reviewing a PR notices that an API endpoint checks if a user is logged in, but fails to check if the user actually *owns* the resource they are trying to delete (IDOR).

**Gotchas & Dev Context**
- Extremely time-consuming and requires highly skilled reviewers.
- Focus should be on critical components: authentication, authorization, and payments.
- Best combined with SAST to filter out the easy "low-hanging fruit."

**Production FAQ**
- *Manual review found an Insecure Direct Object Reference (IDOR). How to patch?*
  Enforce authorization checks at the data access layer. Never rely solely on an ID parameter (like `?id=123`); always verify the currently authenticated user has permissions to access `id=123`.
