# Batch 6 — Security Compliance & Governance
> The rules, frameworks, and audits that keep organizations accountable.

## 1. ISO 27001
**Definition:** An international standard detailing the requirements for an Information Security Management System (ISMS), proving a company has systematic approaches to managing sensitive data.
**Real-World Dev/IT Example:** Your SaaS startup wants European enterprise clients. To prove you take security seriously, you hire an auditor to certify your ISMS meets ISO 27001 standards, confirming your access controls and incident response plans are formally documented.
**Gotchas & Dev Context:**
*   It focuses heavily on *process*, not just technology.
*   You can have the best firewalls in the world and still fail if your HR onboarding process doesn't include mandatory security training.
**Production FAQ:**
*   **Q: Do developers need to read the ISO 27001 spec?** A: No, just follow the internal policies (e.g., locking laptops, encrypting DBs) your compliance team derived from it.
*   **Q: How long does certification take?** A: Usually 6-12 months of preparation for a mid-sized startup.

## 2. SOC 2 Type I & Type II
**Definition:** An auditing standard for service organizations that securely manage data. Type I assesses security design at a specific point in time; Type II assesses operating effectiveness continuously over a period (usually 6-12 months).
**Real-World Dev/IT Example:** You are building a B2B cloud storage app. To land big contracts, you complete a SOC 2 Type II audit to prove your "encrypt at rest" policy actually worked consistently over the last year, rather than just being written on paper.
**Gotchas & Dev Context:**
*   SOC 2 is an auditor's *report*, not a true "certificate".
*   It focuses on 5 Trust Services Criteria: Security, Availability, Processing Integrity, Confidentiality, and Privacy.
**Production FAQ:**
*   **Q: What's the practical difference between Type I and Type II for devs?** A: Type I says "We have a backup script." Type II says "Here are 6 months of logs proving the script ran successfully every day."

## 3. NIST Cybersecurity Framework (CSF)
**Definition:** A voluntary set of guidelines developed by the US government to help organizations manage and reduce cybersecurity risks using a common, practical language.
**Real-World Dev/IT Example:** Your DevOps team maps your infrastructure to NIST's 5 core functions to ensure you aren't just over-investing in firewalls ("Protect") while ignoring alerting and logging ("Detect").
**ASCII Diagram:**
```text
Identify -> Protect -> Detect -> Respond -> Recover
(Know)      (Lock)     (Watch)   (Act)      (Restore)
```
**Gotchas & Dev Context:**
*   It’s not a test you "pass" or "fail". It’s a blueprint used to build a well-rounded security program.
*   Great for explaining security posture to non-technical executives.
**Production FAQ:**
*   **Q: Is NIST only for US government contractors?** A: No, it is widely adopted by private tech companies globally because it is highly practical, comprehensive, and free.

## 4. GDPR (Privacy by Design)
**Definition:** A European Union regulation mandating strict data protection and giving citizens control over their personal info. "Privacy by Design" means integrating data protection into software architecture from the very beginning.
**Real-World Dev/IT Example:** When designing a user registration flow, you only ask for an email (data minimization), hash the password immediately, and include an automated "Delete My Account" button (right to be forgotten) on day one.
**Gotchas & Dev Context:**
*   Applies to ANY company holding EU citizen data, regardless of where your servers or headquarters are located.
*   Violations carry massive fines (up to 4% of global revenue).
**Production FAQ:**
*   **Q: Do IP addresses count as personal data?** A: Yes. If your logging system saves raw IP addresses, you must handle them under strict GDPR rules.
*   **Q: What if our backups contain data a user wanted deleted?** A: Backups usually fall under exceptions, provided the data is isolated and will be overwritten/deleted in the standard backup rotation.

## 5. HIPAA
**Definition:** The Health Insurance Portability and Accountability Act is a US law mandating the protection and confidential handling of Protected Health Information (PHI).
**Real-World Dev/IT Example:** Your telemedicine app stores patient diagnosis records. You must encrypt this data, enforce strict Role-Based Access Control (RBAC), and sign legal Business Associate Agreements (BAAs) with third-party vendors like AWS.
**Gotchas & Dev Context:**
*   HIPAA violations carry immense financial penalties and even criminal charges for negligence.
*   "De-identified" data is exempt from HIPAA, but correctly stripping data so it can never be re-identified is highly complex.
**Production FAQ:**
*   **Q: Can I log patient IDs to our centralized logging server for debugging?** A: Absolutely not, unless that server is explicitly covered by a BAA and access is strictly audited. Use generic trace IDs instead.

## 6. Risk Assessment Matrix
**Definition:** A visual tool used during risk assessments to define the level of a risk by mapping the probability (likelihood) of an event against the severity of its impact.
**Real-World Dev/IT Example:** You find a vulnerability where an attacker could theoretically spoof a user, but it requires physical access to the bare-metal server. You map it on the matrix: High Impact, but Low Likelihood = Medium Risk overall.
**ASCII Diagram:**
```text
Impact ->   Low       Med       High
Likelihood
  High    | Med     | High    | Critical|
  Med     | Low     | Med     | High    |
  Low     | Info    | Low     | Med     |
```
**Gotchas & Dev Context:**
*   Risk rating is highly subjective. One engineer's "Medium" likelihood is another's "Low". It requires consensus and threat modeling.
**Production FAQ:**
*   **Q: Do we have to fix every risk on the matrix?** A: No. Teams fix Critical/High, and often formally "accept" Low risks because the engineering cost to fix them is higher than the potential financial loss.

## 7. Vulnerability Management Lifecycle
**Definition:** The continuous, operational process of identifying, prioritizing, remediating, and reporting on security vulnerabilities in systems and software.
**Real-World Dev/IT Example:** A scanner flags an outdated Log4j library in your Java backend (Identify). You rate it critical (Prioritize), update the version in `pom.xml` (Remediate), and verify the scanner runs clean (Report).
**ASCII Diagram:**
```text
[Discover] -> [Assess/Prioritize] -> [Remediate] -> [Verify]
     ^------------------------------------------------|
```
**Gotchas & Dev Context:**
*   Discovery is easy; prioritization is hard. If tools generate 10,000 alerts, developers will ignore them.
*   Context matters: a vulnerable library on an internal, air-gapped server is lower priority than on a public-facing API.
**Production FAQ:**
*   **Q: Can we just batch our security patching once a quarter?** A: No, attackers weaponize critical CVEs within days or hours. The lifecycle must be a continuous pipeline.

## 8. Penetration Testing (Black Box, White Box, Grey Box)
**Definition:** An authorized simulated cyberattack on a system to evaluate its security. Black Box gives testers zero inside info; White Box gives full source code access; Grey Box gives partial info (e.g., standard user credentials).
**Real-World Dev/IT Example:** You hire a security firm for a Grey Box pen test of your web app. You provide them with standard user logins, and they attempt to exploit authorization flaws to access other tenants' private data.
**Gotchas & Dev Context:**
*   Pen tests are point-in-time assessments. A clean pen test today doesn't mean you're secure tomorrow after deploying 5 new features.
*   Usually mandated annually by compliance frameworks like SOC 2 or ISO 27001.
**Production FAQ:**
*   **Q: Which type is best for software companies?** A: White/Grey box is usually more cost-effective. Black box often wastes expensive tester time mapping out routes that the dev team could have simply handed over.

## 9. Bug Bounty Programs
**Definition:** A crowdsourced security initiative where organizations pay freelance security researchers (ethical hackers) financial rewards (bounties) for finding and reporting valid vulnerabilities.
**Real-World Dev/IT Example:** Your company launches a HackerOne program. A researcher finds a Stored XSS vulnerability in your forum module. You pay them $500, fix the bug, and prevent a potential public data breach.
**Gotchas & Dev Context:**
*   Only launch a bug bounty AFTER you have strong internal security testing. Otherwise, you'll go broke paying thousands of dollars for obvious, low-hanging fruit.
*   Requires dedicated engineering time to triage reports, many of which are false positives or duplicates.
**Production FAQ:**
*   **Q: Will bug bounties replace formal pen testing?** A: No. Audits and enterprise clients require formal pen testing methodology and reports. Bug bounties are an excellent supplementary layer.

## 10. Security Audits
**Definition:** A systematic, formal evaluation of an organization's information system by measuring how well it conforms to established criteria, policies, or external frameworks.
**Real-World Dev/IT Example:** Once a year, an external auditor interviews your engineering managers, asks to see the pull request approval logs, and verifies that production database access is revoked within 24 hours of an employee's termination.
**Gotchas & Dev Context:**
*   Audits check *compliance*, not necessarily *absolute security*. Being compliant means you followed the rules; it doesn't magically prevent sophisticated hacks.
*   Audits are inherently stressful for the engineering org if evidence isn't centralized.
**Production FAQ:**
*   **Q: How can developers make audits less painful?** A: Automate evidence collection. If you have to manually screenshot PR approvals for an auditor, the audit will be a nightmare. Enforce rules via CI/CD and infrastructure-as-code.
