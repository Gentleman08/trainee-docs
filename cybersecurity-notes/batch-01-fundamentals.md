# Batch 1 — Cyber Security Fundamentals
> Core concepts every developer and IT professional must know.

## 1. CIA Triad (Confidentiality, Integrity, Availability)

### Definition
The foundational model of information security. Confidentiality keeps data secret, Integrity ensures data is accurate and untampered, and Availability ensures data is accessible when needed.

### Real-World Dev/IT Example
A banking app: 
- **C:** Only you can view your balance.
- **I:** Your transfer of $10 isn't maliciously changed to $100 in transit.
- **A:** The bank's API is online when you try to pay for dinner.

### ASCII Diagram
```text
      Confidentiality (Encryption)
           /      \
          /        \
         /          \
  Integrity ------ Availability
 (Hashing)         (Redundancy)
```

### Gotchas & Dev Context
- Optimizing one pillar often hurts another (e.g., heavy encryption hurts availability/speed).
- Focus on CIA during the system design phase, not as an afterthought.

### Production FAQ
**Q: How do we balance CIA in a microservices architecture?**
A: Use TLS for confidentiality, JWT signatures for integrity, and load balancers/auto-scaling for availability. 

**Q: Is CIA still relevant with modern cloud providers?**
A: Yes. AWS/Azure provide the tools, but you are still responsible for configuring them to maintain CIA (Shared Responsibility Model).

## 2. Authentication vs Authorization

### Definition
**Authentication (AuthN)** verifies *who* you are. **Authorization (AuthZ)** determines *what* you are allowed to do. 

### Real-World Dev/IT Example
Authentication is showing your boarding pass and ID at airport security. Authorization is trying to enter the First Class lounge—your economy ticket means you are known (AuthN), but denied entry (AuthZ).

### ASCII Diagram
```text
User --> [AuthN: "Are you Alice?"] --> Yes --> [AuthZ: "Can Alice DELETE?"] --> No!
```

### Gotchas & Dev Context
- Never conflate the two in code. A valid login token does not imply admin rights.
- Always check AuthZ on the backend, even if you hide UI buttons on the frontend.
- OAuth 2.0 is an Authorization framework, whereas OpenID Connect (OIDC) handles Authentication.

### Production FAQ
**Q: Where should authorization checks happen?**
A: At the API gateway or controller level before executing business logic, and at the database level using row-level security if possible.

**Q: Can a user be authorized but not authenticated?**
A: Usually no. AuthZ depends on the identity established by AuthN. Anonymous access is a special case of AuthZ granting public rights.

## 3. Identity and Access Management (IAM)

### Definition
A framework of policies and technologies ensuring that the right users (or machines) have the appropriate access to technology resources.

### Real-World Dev/IT Example
Using AWS IAM to create a specific "DatabaseBackupRole". An EC2 instance assumes this role, granting it permission to read the database and write to an S3 bucket, but nothing else.

### Gotchas & Dev Context
- IAM applies to humans *and* service accounts (machine-to-machine).
- Hardcoding credentials is an IAM failure. Use dynamic secrets or managed identities.
- Centralize IAM using an Identity Provider (IdP) like Okta or Active Directory.

### Production FAQ
**Q: Why use Roles instead of individual user credentials for services?**
A: Roles provide temporary, auto-rotating credentials. If leaked, they expire quickly, whereas static API keys remain active until manually revoked.

**Q: How do we handle offboarding?**
A: Centralized IAM allows 1-click revocation across all connected apps, preventing ex-employees from accessing corporate data.

## 4. Multi-Factor Authentication (MFA)

### Definition
A security mechanism requiring users to provide two or more different forms of evidence (factors) before granting access. Factors include: Something you know (password), Something you have (phone/token), Something you are (biometrics).

### Real-World Dev/IT Example
Logging into a production server requires your password (know) and a time-based 6-digit code from your authenticator app (have).

### Gotchas & Dev Context
- SMS is a weak factor due to SIM-swapping attacks. Prefer TOTP (Time-Based One-Time Password) apps or hardware keys (YubiKey).
- Implementing MFA from scratch is risky; rely on established IdP services (Auth0, Cognito).
- Always provide secure recovery codes for when users lose their devices.

### Production FAQ
**Q: Should APIs require MFA?**
A: APIs use machine-to-machine authentication (like mutual TLS or signed JWTs). MFA is for human interaction.

**Q: Does MFA stop all phishing?**
A: No. Advanced phishing can proxy MFA codes in real-time. FIDO2/WebAuthn hardware keys are the only truly phishing-resistant MFA.

## 5. Encryption vs Hashing vs Encoding

### Definition
**Encryption** is a two-way function to hide data (requires a key to decrypt). **Hashing** is a one-way mathematical function mapping data to a fixed-size string. **Encoding** changes data format for system compatibility, not for security.

### Real-World Dev/IT Example
- **Encryption:** Storing credit card numbers using AES-256. (Can be decrypted later).
- **Hashing:** Storing user passwords using bcrypt. (Cannot be reversed, only matched).
- **Encoding:** Converting a binary image to Base64 to send it via JSON. (Easily decoded by anyone).

### Gotchas & Dev Context
- Base64 is NOT security. Never use it to hide secrets.
- Hashes must use a random "salt" (extra unique data) to prevent pre-computed dictionary attacks (rainbow tables).
- Don't roll your own crypto. Use standard libraries like libsodium.

### Production FAQ
**Q: How do we reset a hashed password if we can't reverse it?**
A: You don't. You verify their email, let them set a new password, and overwrite the old hash with the new hash.

**Q: Which hashing algorithm should I use for passwords?**
A: Argon2, bcrypt, or scrypt. Never use MD5 or SHA-256 for passwords—they are too fast and easily brute-forced.

## 6. Malware (Virus, Worm, Trojan, Ransomware)

### Definition
Malicious software designed to disrupt, damage, or gain unauthorized access to a system. 
- **Virus:** Attaches to files, requires user action to spread.
- **Worm:** Spreads automatically across networks.
- **Trojan:** Disguises itself as legitimate software.
- **Ransomware:** Encrypts user data and demands payment for the decryption key.

### Real-World Dev/IT Example
A developer downloads a "free" PDF editor. It works, but it's a Trojan that quietly installs Ransomware, encrypting the company's shared drive and demanding Bitcoin.

### Gotchas & Dev Context
- Supply chain attacks are modern malware delivery: an npm or PyPI package gets compromised, injecting malicious code into your build pipeline.
- Antivirus is reactive (signature-based). EDR (Endpoint Detection and Response) is proactive (behavior-based).

### Production FAQ
**Q: How do we protect CI/CD pipelines from malware?**
A: Pin dependency versions, use Software Bill of Materials (SBOM), and scan containers/packages for known vulnerabilities before deployment.

**Q: Should we pay the ransom?**
A: Generally, no. There is no guarantee you will get your data back. Rely on immutable backups instead.

## 7. Social Engineering & Phishing

### Definition
Manipulating individuals into divulging confidential information or performing actions that compromise security. Phishing is a specific type using deceptive emails or messages.

### Real-World Dev/IT Example
An attacker emails an HR rep pretending to be the CEO, asking for an urgent wire transfer to a "new vendor." The email address is `ceo@compnay.com` instead of `ceo@company.com`.

### Gotchas & Dev Context
- The human is the weakest link in any cryptographic system.
- Spear-phishing targets specific high-value individuals; Whaling targets executives.
- Developers often fall for phishing via fake GitHub login pages or urgent "AWS quota exceeded" emails.

### Production FAQ
**Q: How can IT mitigate phishing risk?**
A: Implement DMARC/DKIM/SPF for email validation, use phishing-resistant MFA (hardware keys), and conduct regular employee awareness training.

**Q: Are technical controls enough?**
A: No. A culture where employees feel safe verifying requests ("Hey CEO, did you actually ask for this wire transfer?") prevents more breaches than spam filters.

## 8. Zero Trust Architecture

### Definition
A security model assuming threats exist both outside and inside the network. It requires strict identity verification for every person and device trying to access resources, regardless of their network location. "Never trust, always verify."

### Real-World Dev/IT Example
Instead of using a VPN that grants broad access to the corporate network, a developer authenticates via an identity proxy that checks their device posture, location, and MFA before granting access *only* to the specific Git server.

### ASCII Diagram
```text
[User/Device] --> [Policy Engine: Check AuthN, AuthZ, Device Health] --> [Resource]
```

### Gotchas & Dev Context
- IP addresses are no longer a source of trust.
- Requires continuous authorization, not just a one-time check at login.
- Implementation heavily relies on micro-segmentation and Identity-Aware Proxies.

### Production FAQ
**Q: Does Zero Trust mean getting rid of the VPN?**
A: Yes, eventually. VPNs provide a flat network after login. Zero Trust replaces this with per-application access tunnels.

**Q: How do microservices communicate in a Zero Trust environment?**
A: Through Service Meshes (like Istio) using mutual TLS (mTLS), ensuring every service authenticates and authorizes every other service.

## 9. Defense in Depth

### Definition
An approach using multiple layers of security controls so that if one layer fails, another layer is in place to thwart an attack. (Also known as the "Castle Approach").

### Real-World Dev/IT Example
Protecting a database:
1. Perimeter: Web Application Firewall (WAF) filters SQL injection.
2. Network: VPC private subnets block direct internet access.
3. App: Code uses parameterized queries.
4. Data: Database uses at-rest encryption.

### Gotchas & Dev Context
- Redundancy is key. Don't rely solely on the firewall to protect sloppy application code.
- Too many layers can cause alert fatigue and hinder developer productivity if not streamlined.

### Production FAQ
**Q: Does Defense in Depth conflict with Zero Trust?**
A: No, they complement each other. Zero Trust is a layer of Defense in Depth focused on identity and context, while DiD encompasses physical, network, and application layers.

**Q: Is it cost-effective to have overlapping controls?**
A: Yes. The cost of a breach far outweighs the operational cost of running a WAF alongside secure coding practices.

## 10. Principle of Least Privilege (PoLP)

### Definition
A user, program, or process should have only the bare minimum privileges necessary to perform its intended function.

### Real-World Dev/IT Example
A web application backend needs to read user data and insert new logs. It is given a database user with `SELECT` and `INSERT` grants. It is explicitly denied `DROP`, `DELETE`, and schema modification rights.

### Gotchas & Dev Context
- It's tempting to use `Administrator` or `root` during development "to make things work." Don't let this reach production.
- Scope cloud permissions down to specific resources (e.g., `s3:GetObject` on `arn:aws:s3:::my-bucket/*` instead of `s3:*` on `*`).

### Production FAQ
**Q: How do we enforce PoLP without slowing down developers?**
A: Use Infrastructure as Code (IaC) to request and review targeted permissions, and implement automated tools to alert on over-permissive IAM roles.

**Q: What is Just-In-Time (JIT) access?**
A: An evolution of PoLP. Instead of holding permanent admin rights, a developer requests elevated privileges for a specific task, which expire automatically after a few hours.

## 11. Insider Threat

### Definition
A security risk originating from within the targeted organization. This includes malicious employees stealing data, or negligent employees accidentally exposing systems.

### Real-World Dev/IT Example
A disgruntled database administrator downloads the customer database to a personal USB drive before quitting to sell to a competitor (Malicious). Or, a dev accidentally uploads AWS keys to a public GitHub repository (Negligent).

### Gotchas & Dev Context
- Most insider threats are accidents, not malice.
- High turnover or upcoming layoffs massively spike the risk of malicious insider activity.
- Logging and monitoring are your primary defenses against authorized users doing unauthorized things.

### Production FAQ
**Q: How do we catch data exfiltration?**
A: Use Data Loss Prevention (DLP) tools, monitor for unusual download volumes, and block access to personal cloud storage on corporate networks.

**Q: How do we prevent accidental leaks by developers?**
A: Implement pre-commit hooks (like `git-secrets` or `trufflehog`) to scan for API keys before they can be pushed to version control.

## 12. Vulnerability vs Risk vs Threat

### Definition
- **Vulnerability:** A weakness or flaw in a system (e.g., unpatched software).
- **Threat:** A potential danger that could exploit a vulnerability (e.g., a hacker, malware, or a flood).
- **Risk:** The probability and impact of a threat successfully exploiting a vulnerability. (Risk = Threat × Vulnerability × Impact).

### Real-World Dev/IT Example
Your app has an unpatched Log4j bug (**Vulnerability**). Ransomware gangs actively scan the internet for this bug (**Threat**). The **Risk** is critically high because successful exploitation means losing all customer data.

### ASCII Diagram
```text
[Threat Actor] 
      |
 (attempts to exploit)
      v
[Vulnerability] ----> [Asset] = (High Risk)
```

### Gotchas & Dev Context
- A vulnerability with no threat or impact has low risk. (e.g., An XSS bug in an internal admin panel accessible only via VPN is lower risk than on a public-facing page).
- We patch vulnerabilities, mitigate threats, and manage risks.

### Production FAQ
**Q: How do we prioritize which vulnerabilities to fix?**
A: Use CVSS (Common Vulnerability Scoring System) scores combined with environmental context. Prioritize internet-facing assets and systems holding sensitive data.

**Q: Can we eliminate risk entirely?**
A: No. You can only reduce, transfer (via insurance), or accept risk. Security is about risk management, not risk elimination.
