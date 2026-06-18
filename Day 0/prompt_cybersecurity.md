# PROMPT — Cyber Security Notes

Write me new notes on Cyber Security in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world development/IT example
- ASCII diagram if applicable
- Add gotchas and security-related context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with architecture, code/config snippets, deployment steps, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete Cyber Security Glossary

### Batch 1 — Cyber Security Fundamentals
CIA Triad (Confidentiality, Integrity, Availability)
Authentication vs Authorization
Identity and Access Management (IAM)
Multi-Factor Authentication (MFA)
Encryption vs Hashing vs Encoding
Malware (Virus, Worm, Trojan, Ransomware)
Social Engineering & Phishing
Zero Trust Architecture
Defense in Depth
Principle of Least Privilege (PoLP)
Insider Threat
Vulnerability vs Risk vs Threat

### Batch 2 — Network Security
Firewall (Stateful vs Stateless)
Intrusion Detection System (IDS) vs Intrusion Prevention System (IPS)
Virtual Private Network (VPN)
SIEM (Security Information and Event Management)
SOC (Security Operations Center)
Subnetting & VLANs
OSI Model (Security perspective)
TCP/IP Handshake
Port Scanning
Man-in-the-Middle (MITM) Attack
DDoS Attack
Honeypot

### Batch 3 — Cryptography & Data Security
Symmetric vs Asymmetric Encryption
RSA Algorithm
AES (Advanced Encryption Standard)
Public Key Infrastructure (PKI)
Digital Signatures
SSL / TLS Handshake
Digital Certificates (X.509)
Salting & Peppering
Key Management (KMS)
Steganography
Homomorphic Encryption

### Batch 4 — Endpoint & Cloud Security
Endpoint Detection and Response (EDR)
Extended Detection and Response (XDR)
Antivirus vs Endpoint Protection Platform (EPP)
Mobile Device Management (MDM)
Cloud Shared Responsibility Model
IAM Roles & Policies (AWS/GCP/Azure)
Web Application Firewall (WAF)
Data Loss Prevention (DLP)
Container Security (Docker/K8s)
Serverless Security

### Batch 5 — Threat Intel & Incident Response
Cyber Kill Chain
MITRE ATT&CK Framework
Indicators of Compromise (IoC)
Indicators of Attack (IoA)
Incident Response Lifecycle
Digital Forensics Basics
YARA Rules
Threat Hunting
Red Team vs Blue Team vs Purple Team
Sandboxing

### Batch 6 — Security Compliance & Governance
ISO 27001
SOC 2 Type I & Type II
NIST Cybersecurity Framework (CSF)
GDPR (Privacy by Design)
HIPAA
Risk Assessment Matrix
Vulnerability Management Lifecycle
Penetration Testing (Black Box, White Box, Grey Box)
Bug Bounty Programs
Security Audits

---

## PART 2 — Project Case Studies

### Case Study 1: Building a Minimalist SIEM Pipeline (LogStream)

Build a log ingestion and alerting pipeline that:
- Collects system and network logs from multiple servers
- Parses and normalizes logs using Logstash/Fluentd
- Stores logs securely in Elasticsearch/OpenSearch
- Triggers real-time alerts based on specific IoCs (e.g., multiple failed SSH logins, unexpected port usage)
- Provides a dashboard for SOC analysts

**Cover in the case study:**
- Architecture diagram (ASCII): Endpoints → Forwarders → Parser → Datastore → Dashboard/Alerting
- Tech stack: Filebeat, Logstash, Elasticsearch, Kibana (ELK), ElastAlert/Wazuh
- Config snippets: Logstash grok filters, ElastAlert rule for SSH brute-force
- Deployment steps: Docker-compose for the ELK stack
- Production gotchas: Log retention costs, indexing bottlenecks, alert fatigue
- Lessons learned

### Case Study 2: Implementing Zero Trust Network Access (ZTNA)

Deploy a Zero Trust architecture for a remote development team that:
- Replaces legacy VPNs
- Authenticates identity and verifies device health before granting access to internal Git repositories and CI/CD pipelines
- Micro-segments network access per user role
- Continuously monitors active sessions

**Cover in the case study:**
- Architecture diagram (ASCII): User → Identity Provider → Device Posture Check → Access Gateway → Internal App
- Tech stack: Cloudflare Access / Tailscale / Teleport, Okta/Azure AD, Docker
- Config snippets: Access policy rules, device posture requirements
- Deployment steps: Setting up the IdP integration, installing the gateway agent on internal servers
- Production gotchas: Break-glass procedures, latency overhead, user friction during onboarding
- Lessons learned
