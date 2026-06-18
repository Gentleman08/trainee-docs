# Batch 2 — VAPT Fundamentals
> The processes and standards used to discover and evaluate vulnerabilities.

## 1. Vulnerability Assessment vs Penetration Testing

**Definition**
Vulnerability Assessment (VA) is the automated process of identifying and logging potential security flaws. Penetration Testing (PT) is a manual, simulated cyberattack to verify if those flaws can actually be exploited to compromise the system.

**Real-World Dev/Testing Example**
Running an automated tool like Nessus to find unpatched servers is a VA. A security engineer manually extracting a database via an exposed API flaw found during that scan is a PT.

**ASCII Diagram**
```text
[Automated Scan] --finds--> [Open Door] == (VA)
[Manual Tester] --enters--> [Steals Data] == (PT)
```

**Gotchas & Dev Context**
- VA produces many false positives; PT is deeper but takes more time and money.
- VA is usually breadth-first (compliance-driven); PT is depth-first (risk-driven).

**Production FAQ**
- **Q: Do we need both?**
  **A:** Yes. Run VAs continuously in your CI/CD pipeline for broad coverage. Schedule PTs annually or before major releases to validate real-world risk.

## 2. OWASP Top 10 Overview

**Definition**
The Open Worldwide Application Security Project (OWASP) Top 10 is a globally recognized awareness document representing the top ten most critical security risks to web applications.

**Real-World Dev/Testing Example**
Using the OWASP list to prioritize fixing a "Broken Access Control" vulnerability (currently #1) before spending sprint points on obscure, low-risk edge cases.

**Gotchas & Dev Context**
- It is an awareness document, not a comprehensive testing checklist.
- The list evolves based on industry data (e.g., Injection dropped in rank recently, while Access Control rose).

**Production FAQ**
- **Q: Is our app secure if we mitigate the OWASP Top 10?**
  **A:** No, it’s just the bare minimum baseline. You must still threat-model your specific business logic and architecture.

## 3. Common Vulnerability Scoring System (CVSS)

**Definition**
CVSS is a standardized numerical framework (0.0 to 10.0) used to rate the severity of software vulnerabilities based on exploitability, impact, and complexity.

**Real-World Dev/Testing Example**
Prioritizing an emergency hotfix for a CVSS 9.8 (Critical) remote code execution bug over a CVSS 3.5 (Low) self-XSS bug.

**Gotchas & Dev Context**
- CVSS measures *severity*, not necessarily *environmental risk*.
- A Critical 9.8 on a purely internal, isolated server might pose less actual business risk than a High 7.5 on your public-facing payment gateway.

**Production FAQ**
- **Q: How do we handle High/Critical CVSS scores in production?**
  **A:** Enforce SLA patching windows (e.g., Critical within 48h). Use Web Application Firewall (WAF) rules as temporary virtual patches while developers fix the code.

## 4. CVE (Common Vulnerabilities and Exposures)

**Definition**
A CVE is a standardized dictionary of publicly disclosed cybersecurity vulnerabilities, assigning each a unique identifier for easy tracking across tools and databases.

**Real-World Dev/Testing Example**
Searching the National Vulnerability Database (NVD) for `CVE-2021-44228` to see if your Java application's version of Log4j is vulnerable to remote exploitation.

**Gotchas & Dev Context**
- A CVE requires public disclosure. Many zero-days or custom app bugs don't have CVEs.
- Vulnerability scanners rely heavily on CVE databases to flag outdated software.

**Production FAQ**
- **Q: What if a library we use gets a CVE, but we don't invoke the vulnerable function?**
  **A:** You should still patch it. It ensures you pass security audits and prevents future developers from accidentally invoking the vulnerable function later.

## 5. CWE (Common Weakness Enumeration)

**Definition**
CWE is a community-developed list of common software and hardware weakness types (the root causes of vulnerabilities) rather than specific vulnerability instances.

**Real-World Dev/Testing Example**
Identifying that your application has a "CWE-89: SQL Injection" problem, indicating you need to train your developers on using parameterized queries.

**Gotchas & Dev Context**
- **CWE** describes the *type* of bug (the "how").
- **CVE** describes the *specific incident* (the "where").

**Production FAQ**
- **Q: How do we use CWEs in development?**
  **A:** Map your SAST/DAST scanner findings to CWE categories. Build targeted developer training around the top 3 most common CWEs found in your codebase to stop bugs at the source.

## 6. Bug Bounty Basics

**Definition**
A bug bounty is a crowdsourced security initiative where organizations pay ethical hackers (researchers) financial rewards for discovering and responsibly reporting vulnerabilities.

**Real-World Dev/Testing Example**
A company launches a HackerOne program paying $5,000 for critical bugs, successfully catching an authorization bypass that internal testing missed.

**Gotchas & Dev Context**
- It is not a substitute for internal security or formal pentesting.
- Triage can be overwhelming due to "beg bounties" (low-quality or duplicate reports like missing HTTP headers).

**Production FAQ**
- **Q: When should we start a bug bounty program?**
  **A:** Only after you have mature internal testing, a solid patching/remediation pipeline, and dedicated budget/staff to triage reports quickly.

## 7. Reconnaissance (Active vs Passive)

**Definition**
Reconnaissance is the information-gathering phase of an attack. Passive recon collects data without touching the target's infrastructure directly, while active recon directly interacts with the target to map open ports and services.

**Real-World Dev/Testing Example**
Looking up a company's DNS records and employee emails via LinkedIn (Passive) versus running an Nmap port scan directly against their web server (Active).

**Gotchas & Dev Context**
- Active recon often triggers Intrusion Detection Systems (IDS) and firewalls.
- Passive recon relies on OSINT (Open Source Intelligence) and is nearly impossible to detect.

**Production FAQ**
- **Q: How do we mitigate reconnaissance?**
  **A:** You cannot stop passive recon. Mitigate active recon by reducing your public attack surface—close unused ports, remove debug endpoints, and sit behind a WAF/CDN.

## 8. Vulnerability Scanning

**Definition**
Vulnerability scanning is the automated inspection of networks, systems, or applications to identify known security weaknesses, misconfigurations, or missing patches.

**Real-World Dev/Testing Example**
Running an automated pipeline with Dependabot (for library vulnerabilities) and OWASP ZAP (for web endpoints) to flag outdated dependencies on every PR.

**Gotchas & Dev Context**
- Scanners lack business logic context. They won't know if an endpoint allowing a user to change an ID in a URL violates your specific privacy rules (IDOR).
- They generate noisy reports if not tuned properly.

**Production FAQ**
- **Q: Scanners give us thousands of alerts. How do we remediate?**
  **A:** Filter by exploitability (e.g., prioritize CISA's Known Exploited Vulnerabilities list), focus on internet-facing assets first, and update base Docker images to bulk-patch issues.

## 9. Exploitation vs Post-Exploitation

**Definition**
Exploitation is the act of using a vulnerability to gain unauthorized access. Post-Exploitation covers everything an attacker does *after* gaining access, like stealing data, escalating privileges, or pivoting to other machines.

**Real-World Dev/Testing Example**
Sending a malicious payload to bypass a login screen (Exploitation), then dumping the user database and installing a persistent backdoor shell (Post-Exploitation).

**ASCII Diagram**
```text
[Perimeter] --Exploit--> [Server Access] --Post-Exploit--> [DB / Internal Network]
```

**Gotchas & Dev Context**
- Traditional defenses focus too heavily on preventing exploitation.
- Modern security assumes breach and actively limits post-exploitation movement.

**Production FAQ**
- **Q: How do we limit post-exploitation damage?**
  **A:** Implement Zero Trust principles. Use network segmentation, enforce least-privilege IAM roles, and monitor internal lateral movement.

## 10. Reporting & Remediation

**Definition**
Reporting is documenting the findings of a security test with evidence and risk ratings. Remediation is the process of fixing those findings via patches, code changes, or configuration updates.

**Real-World Dev/Testing Example**
A pentester delivers a report detailing an XSS flaw with replication steps; the dev team remediates it by implementing a strict Content Security Policy (CSP) and HTML escaping.

**Gotchas & Dev Context**
- Reports must be actionable—developers need exact URLs, parameters, and HTTP requests to reproduce the bug.
- Remediation must be re-tested (a "fix validation" test) to ensure the patch actually worked.

**Production FAQ**
- **Q: What if we can't patch a vulnerability immediately due to breaking changes?**
  **A:** Apply a mitigating control (e.g., block the malicious input pattern at the WAF or temporarily disable the vulnerable feature) and document a formal risk acceptance with a hard deadline for the true fix.
