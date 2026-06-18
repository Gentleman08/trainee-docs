# Batch 4 — Endpoint & Cloud Security
> Securing devices and cloud infrastructure at scale.

## 1. Endpoint Detection and Response (EDR)
### Definition
EDR is a security solution that continuously monitors end-user devices (laptops, servers) to detect and respond to cyber threats like ransomware or malware. It acts like a flight data recorder for devices, logging activities to spot malicious behavior.

### Real-World Dev/IT Example
A developer's laptop runs a malicious script hidden in a downloaded PDF. EDR detects unusual PowerShell activity spawning from the PDF reader, instantly isolates the laptop from the company network, and alerts the security team.

### Gotchas & Dev Context
- EDR can be noisy and trigger false positives on legitimate developer tools (e.g., compilers, network scanners).
- It consumes system resources; heavy agent overhead can slow down CI/CD build servers if not tuned correctly.
- Requires a dedicated team (or Managed Service Provider) to interpret the logs and respond.

### Production FAQ
**Q: How is EDR different from traditional Antivirus?**
A: Antivirus relies on known signatures of malware to block threats. EDR monitors behavior (what a program does) to catch new, unknown threats (zero-days).

**Q: Can I run EDR in my Kubernetes clusters?**
A: Yes, but traditional endpoint EDR might not understand container dynamics well. You usually need cloud-workload specific agents for containers.

## 2. Extended Detection and Response (XDR)
### Definition
XDR is the evolution of EDR. Instead of just monitoring endpoints (devices), XDR collects and correlates data across emails, servers, cloud workloads, and networks to provide a unified view of complex cyber attacks.

### Real-World Dev/IT Example
An attacker phishes a developer via email, steals credentials, and logs into a cloud server to exfiltrate data. EDR would only see the server activity, but XDR connects the phishing email log with the strange cloud login and the data transfer, telling the whole story.

### ASCII Diagram
```text
Email Logs \
Network Logs —> [ XDR Brain (Correlation Engine) ] —> Unified Alert
Endpoint Logs /
```

### Gotchas & Dev Context
- Integration is tough; XDR works best when all your tools are from the same vendor (vendor lock-in) or through extensive API integrations.
- It requires mature log management and normalization across diverse systems.
- Alerts are fewer but more complex, requiring skilled analysts to investigate.

### Production FAQ
**Q: Does XDR replace SIEM?**
A: Not necessarily. SIEM is a broader log management and compliance tool, while XDR is strictly focused on threat detection and automated response.

**Q: Is XDR worth the cost for a small startup?**
A: Usually no. A strong EDR and MFA setup is better for small teams until infrastructure complexity demands XDR.

## 3. Antivirus vs Endpoint Protection Platform (EPP)
### Definition
Traditional Antivirus (AV) scans files against a database of known bad signatures. Endpoint Protection Platform (EPP) is a broader suite that includes next-gen AV, personal firewalls, device control (blocking USBs), and vulnerability scanning to prevent attacks before they run.

### Real-World Dev/IT Example
An employee plugs in a USB drive found in the parking lot. AV would try to scan the files on it. EPP flat-out blocks the USB port from mounting unauthorized drives based on company policy, preventing the attack entirely.

### Gotchas & Dev Context
- EPP focuses on *prevention* (stopping things before they happen), while EDR focuses on *detection and response* (when prevention fails).
- Often bundled together (EPP + EDR) by modern vendors like CrowdStrike or SentinelOne.
- EPP can accidentally block custom internal software if not properly whitelisted.

### Production FAQ
**Q: Do I still need AV if I have EDR?**
A: Yes. You want EPP/AV to filter out the 99% of known "dumb" malware so your EDR can focus on the 1% of complex, behavior-based attacks.

**Q: Does EPP work offline?**
A: Mostly yes. Signature and basic machine learning engines work offline, though advanced cloud-lookups require internet.

## 4. Mobile Device Management (MDM)
### Definition
MDM is software that allows IT administrators to control, secure, and enforce policies on smartphones, tablets, and laptops. It ensures that any device accessing company data meets security standards.

### Real-World Dev/IT Example
When a new dev joins, they install an MDM profile on their personal phone to access company email. If they lose the phone, IT can remotely wipe the company data without touching their personal photos.

### Gotchas & Dev Context
- Strict MDM policies (like forcing VPNs or blocking apps) can drain battery life and frustrate users.
- For BYOD (Bring Your Own Device), user privacy is a massive concern; MDMs separate personal and work profiles.
- Enrolling developer test devices into MDM can break custom mobile app builds due to restricted permissions.

### Production FAQ
**Q: Can MDM see my personal texts or browser history?**
A: In a proper BYOD setup with work profiles (like iOS User Enrollment or Android Work Profile), no. IT can only see and manage the corporate sandbox.

**Q: What happens if an MDM server goes down?**
A: Devices continue to operate with their last known policies, but new devices can't enroll, and remote wipe commands won't execute until the server is back.

## 5. Cloud Shared Responsibility Model
### Definition
The Shared Responsibility Model is a cloud security framework dictating that the cloud provider (AWS/GCP/Azure) is responsible for the security *of* the cloud (hardware, networking), while the customer is responsible for security *in* the cloud (data, applications, access).

### Real-World Dev/IT Example
AWS ensures that the physical server running your EC2 instance is locked in a secure data center and patched against hypervisor flaws. You are responsible for updating the Linux OS on that EC2 instance and ensuring your application doesn't have SQL injection vulnerabilities.

### ASCII Diagram
```text
[ YOU ] -> Data, Apps, IAM, OS Patching (Security IN the Cloud)
--------------------------------------------------------------
[ AWS ] -> Compute, Storage, Database, Physical Data Centers (Security OF the Cloud)
```

### Gotchas & Dev Context
- The line shifts based on the service type. In IaaS (EC2), you manage the OS. In SaaS/PaaS (S3, RDS), the provider manages the OS, and you only manage the data and access policies.
- Assuming the cloud provider backs up your data or secures your S3 bucket by default is the #1 cause of cloud breaches.

### Production FAQ
**Q: If AWS gets hacked, am I responsible?**
A: If the hypervisor or physical infrastructure is breached, AWS is responsible. If someone guesses your weak IAM password, you are responsible.

**Q: Who is responsible for encrypting data at rest?**
A: Usually, you. The provider gives you the encryption tools (like AWS KMS), but you have to turn the feature on.

## 6. IAM Roles & Policies (AWS/GCP/Azure)
### Definition
Identity and Access Management (IAM) controls who (identities) can do what (actions) on which resources. Policies are JSON/YAML documents defining permissions, and Roles are assumable identities that can be granted to users or services without sharing static passwords.

### Real-World Dev/IT Example
An EC2 instance needs to read photos from an S3 bucket. Instead of hardcoding AWS keys in the app, you assign an IAM Role to the EC2 instance. The attached IAM Policy explicitly allows `s3:GetObject` only for `arn:aws:s3:::my-photo-bucket`.

### Gotchas & Dev Context
- Never use wildcard permissions (`"Action": "*"`) in production. It leads to catastrophic privilege escalation.
- Hardcoded long-lived Access Keys leak easily via GitHub. Always prefer short-lived credentials via IAM Roles.
- IAM propagation isn't instant. Changes can take a few minutes to replicate across all cloud regions.

### Production FAQ
**Q: What is the Principle of Least Privilege?**
A: Giving an identity only the exact permissions it needs to do its job, and nothing more.

**Q: How do I debug why my app is getting "Access Denied"?**
A: Use cloud audit logs (like AWS CloudTrail) to see exactly which IAM action failed, then adjust the policy accordingly.

## 7. Web Application Firewall (WAF)
### Definition
A WAF sits in front of a web application and inspects incoming HTTP/HTTPS traffic. It filters, blocks, or rate-limits malicious traffic like SQL injections, cross-site scripting (XSS), and botnets before they hit your servers.

### Real-World Dev/IT Example
A hacker uses an automated script to attempt SQL injection (`' OR 1=1 --`) on your login page. The WAF detects the malicious payload in the HTTP POST request and drops the connection, returning a 403 Forbidden error to the attacker.

### Gotchas & Dev Context
- WAFs require constant tuning. Out-of-the-box rules will almost certainly block legitimate user traffic (false positives).
- They don't fix bad code. A WAF is a band-aid; you still need to patch the underlying SQLi vulnerability.
- Deploying a WAF in "blocking" mode on day one is risky. Always run in "monitoring" mode first to analyze traffic.

### Production FAQ
**Q: What's the difference between a WAF and a Network Firewall?**
A: A network firewall operates at Layer 3/4 (blocking IP addresses and ports). A WAF operates at Layer 7 (understanding HTTP headers, cookies, and JSON payloads).

**Q: Does a WAF protect against DDoS attacks?**
A: It protects against Application-Layer (Layer 7) DDoS attacks, like someone spamming your expensive search API.

## 8. Data Loss Prevention (DLP)
### Definition
DLP is a strategy and set of tools designed to ensure sensitive data (like credit card numbers, SSNs, or API keys) isn't accidentally or intentionally leaked outside the corporate network.

### Real-World Dev/IT Example
An employee tries to email a spreadsheet containing 5,000 customer credit card numbers to their personal Gmail. The DLP scanner running on the email server detects the 16-digit patterns, blocks the email from sending, and alerts the compliance team.

### Gotchas & Dev Context
- DLP relies heavily on regular expressions and pattern matching, which can be easily bypassed (e.g., zipping the file with a password).
- False positives are common (e.g., mistaking a 16-digit tracking number for a credit card).
- Implementing DLP requires knowing where all your sensitive data actually lives, which is often the hardest part.

### Production FAQ
**Q: Can DLP scan encrypted traffic?**
A: Only if you perform SSL/TLS decryption (man-in-the-middle) at the corporate firewall, which introduces privacy and performance concerns.

**Q: How do developers interact with DLP?**
A: Devs usually encounter DLP via pre-commit hooks that block them from pushing API keys or AWS credentials to public GitHub repos.

## 9. Container Security (Docker/K8s)
### Definition
Container Security involves protecting the container lifecycle—from scanning the base images for vulnerabilities during the build phase, to securing the runtime environment (like Kubernetes) against malicious activity.

### Real-World Dev/IT Example
A developer pulls a public Node.js Docker image that contains a known critical vulnerability (CVE). The CI/CD pipeline runs a container vulnerability scanner (like Trivy), detects the outdated package, and fails the build before it reaches production.

### Gotchas & Dev Context
- Running containers as `root` is a massive security risk. If an attacker breaches the app, they have root access to the container and potentially the host node.
- Containers are ephemeral; if a container is compromised and dies, the forensic evidence dies with it unless logs are shipped elsewhere.
- Kubernetes defaults are often insecure (e.g., pods can talk to any other pod by default). Use Network Policies.

### Production FAQ
**Q: How do I patch a running container?**
A: You don't. You patch the underlying Dockerfile, rebuild the image, and redeploy. Containers are immutable.

**Q: What is a sidecar proxy in security?**
A: A secondary container running alongside your main app container, often used to handle mTLS encryption and network policy enforcement (e.g., Istio).

## 10. Serverless Security
### Definition
Serverless Security focuses on protecting application code and configurations when the underlying infrastructure (servers) is managed entirely by the cloud provider (e.g., AWS Lambda). 

### Real-World Dev/IT Example
An attacker exploits a vulnerability in a vulnerable npm package used by an AWS Lambda function. Because the function's IAM role has excessive permissions (`AdministratorAccess`), the attacker steals all database records. Securing this requires restricting the Lambda's IAM role.

### Gotchas & Dev Context
- You can't install traditional security agents (EDR/WAF) on serverless functions. Security must be built into the code and API Gateway.
- Functions are prone to "Event Injection" attacks (like SQLi, but delivered via an S3 event trigger or CloudWatch log).
- Third-party dependencies are the biggest attack vector. Scan your `package.json` or `requirements.txt` relentlessly.

### Production FAQ
**Q: Is Serverless inherently more secure than VMs?**
A: Yes and no. The cloud provider handles OS patching (a huge win), but the attack surface shifts entirely to your code, IAM permissions, and third-party libraries.

**Q: How do you monitor attacks in Serverless?**
A: Rely heavily on application logs, cloud provider audit trails (CloudTrail), and specialized serverless security tools that analyze code execution context.
