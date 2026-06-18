# Batch 5 — Threat Intel & Incident Response
> Understanding the attacker's mindset and responding to breaches.

## 1. Cyber Kill Chain
**Definition**
A framework developed by Lockheed Martin that outlines the stages of a cyberattack, from early reconnaissance to data exfiltration. It helps defenders identify and stop attacks at various phases.

**Real-World Dev/IT Example**
An attacker scans your public IP for open ports (Reconnaissance), creates a malicious PDF (Weaponization), emails it to an employee (Delivery), the employee opens it running a script (Exploitation), the script downloads malware (Installation), the malware contacts a C2 server (Command & Control), and finally encrypts the database (Actions on Objectives).

**ASCII Diagram**
```text
Recon -> Weaponize -> Deliver -> Exploit -> Install -> C2 -> Actions
```

**Gotchas & Dev Context**
- The further down the chain an attacker gets, the more costly the incident.
- Breaking the chain at *any* step stops the attack.
- It's somewhat traditional; modern cloud and insider threats don't always follow this linear path.

**Production FAQ**
- **Q: Does the Kill Chain apply to cloud environments?**
  A: Yes, but it requires adaptation. E.g., "Delivery" might be exploiting a misconfigured S3 bucket rather than sending an email.
- **Q: How do we use this practically?**
  A: Map your security controls to each stage. If you have no controls for "Command & Control", you have a blind spot.

## 2. MITRE ATT&CK Framework
**Definition**
A comprehensive, globally accessible knowledge base of adversary tactics and techniques based on real-world observations. It's like a detailed dictionary of how hackers operate.

**Real-World Dev/IT Example**
Instead of just saying "we were hacked," you use ATT&CK to specify the attacker used "T1566: Phishing" for Initial Access and "T1003: OS Credential Dumping" for Credential Access.

**ASCII Diagram**
```text
[ Tactic: Why ] -> [ Technique: How ] -> [ Procedure: Exact implementation ]
Example:
Initial Access -> Phishing -> Spearphishing with malicious link
```

**Gotchas & Dev Context**
- ATT&CK is matrix-based (Tactics are columns, Techniques are rows).
- It is much more granular than the Cyber Kill Chain.
- Security tooling (like SIEMs and EDRs) often maps alerts directly to MITRE ATT&CK IDs (e.g., T1059).

**Production FAQ**
- **Q: How is this different from the Cyber Kill Chain?**
  A: The Kill Chain is high-level and linear. MITRE ATT&CK is highly detailed, non-linear, and maps specific technical behaviors.
- **Q: How should a dev team use this?**
  A: Use it to test your logging. If an attacker uses "T1078: Valid Accounts", do your logs capture anomalous logins?

## 3. Indicators of Compromise (IoC)
**Definition**
Pieces of forensic data that suggest a system or network has already been breached. They are the "fingerprints" left behind by an attacker.

**Real-World Dev/IT Example**
You find a suspicious IP address communicating with your database server, or an antivirus alert flags a file with a known malicious MD5 hash. Both the IP and the hash are IoCs.

**Gotchas & Dev Context**
- IoCs are reactive; they tell you you've *already* been hit.
- They have a short shelf-life. Attackers easily change file hashes or IP addresses.
- Common IoCs: IP addresses, domain names, file hashes (MD5, SHA-256), and weird registry keys.

**Production FAQ**
- **Q: Where do we get IoCs?**
  A: Threat intelligence feeds, ISACs (Information Sharing and Analysis Centers), or post-incident analysis of your own logs.
- **Q: Are IoCs enough to stop attacks?**
  A: No. Relying solely on IoCs is like playing Whac-A-Mole. Attackers change them constantly (known as the "Pyramid of Pain").

## 4. Indicators of Attack (IoA)
**Definition**
Observable behaviors or events that suggest an attack is currently in progress, focusing on the *intent* and *action* rather than the specific tool used.

**Real-World Dev/IT Example**
A service account executing PowerShell commands to dump memory, or a user account suddenly trying to access 50 different internal servers it has never talked to before.

**Gotchas & Dev Context**
- IoAs are proactive and behavioral.
- They are harder for attackers to change than IoCs because changing tactics requires learning new skills.
- Detecting IoAs requires good behavioral analytics and baseline profiling (knowing what "normal" looks like).

**Production FAQ**
- **Q: What's the main difference between IoC and IoA?**
  A: An IoC is a static artifact (a specific bad IP). An IoA is a dynamic behavior (scanning the network).
- **Q: Are false positives common with IoAs?**
  A: Yes. A developer legitimately running a heavy network scan might trigger an IoA alert. Fine-tuning is required.

## 5. Incident Response Lifecycle
**Definition**
A structured methodology for handling a security breach or cyberattack, ensuring the threat is contained, eradicated, and learned from.

**Real-World Dev/IT Example**
A ransomware attack hits. The team follows the plan: isolating the infected server (Containment), deleting the malware and patching the vulnerability (Eradication), restoring from backups (Recovery), and holding a meeting to prevent recurrence (Post-Incident Activity).

**ASCII Diagram**
```text
Preparation <-> Detection & Analysis -> Containment, Eradication & Recovery -> Post-Incident
```

**Gotchas & Dev Context**
- Preparation is 80% of the work. If you don't have backups or logs during peace time, response will fail.
- Never reboot a compromised machine unless told to—you will lose volatile memory (RAM) needed for forensics.
- Communication (knowing who to call, including legal/PR) is as critical as technical steps.

**Production FAQ**
- **Q: Who should be on the IR team?**
  A: IT, Security, Legal, HR, and PR. It is not just a technical problem.
- **Q: What is the most ignored phase?**
  A: Post-Incident Activity (Lessons Learned). Teams are often too exhausted, but skipping this means the same breach will happen again.

## 6. Digital Forensics Basics
**Definition**
The scientific process of identifying, preserving, extracting, and documenting computer evidence so it can be used to understand an attack or present in a court of law.

**Real-World Dev/IT Example**
An employee is suspected of stealing code. A forensic analyst makes a bit-for-bit, read-only copy of their hard drive (imaging) and calculates a cryptographic hash to prove the evidence hasn't been tampered with before analyzing it.

**Gotchas & Dev Context**
- **Order of Volatility:** Always collect data that disappears fastest first (e.g., RAM > Network Connections > Hard Drive).
- **Chain of Custody:** A paper trail documenting who handled the evidence and when. Without it, evidence is legally void.
- Timestamps can be spoofed (timestomping). Cross-reference multiple logs.

**Production FAQ**
- **Q: Can we just look around a compromised server to figure out what happened?**
  A: No! Opening files or running commands changes timestamps and overwrites memory. Isolate it and let forensics experts handle it.
- **Q: What tools are common?**
  A: EnCase, FTK, Autopsy, and command-line tools like `dd` for imaging.

## 7. YARA Rules
**Definition**
A pattern-matching tool used by malware researchers to identify and classify malware based on textual or binary patterns. It is essentially "grep for malware."

**Real-World Dev/IT Example**
You write a YARA rule that scans all uploaded attachments for a specific hex string (`{ 4D 5A }` for Windows executables) combined with the string "cmd.exe" to block hidden malicious payloads.

**Gotchas & Dev Context**
- YARA rules use boolean logic (e.g., "Match if String A AND String B are found").
- They are widely supported in EDRs, email gateways, and threat intel platforms.
- Poorly written YARA rules can cause massive performance hits if they are too generic.

**Production FAQ**
- **Q: Can YARA detect unknown malware?**
  A: Yes, if the new malware reuses code or strings from known families that your YARA rule targets.
- **Q: Where do I run YARA?**
  A: You can run it on static files, in memory, or integrate it into your CI/CD pipeline to scan dependencies.

## 8. Threat Hunting
**Definition**
A proactive security search through networks, endpoints, and datasets to hunt down malicious activity that has evaded existing automated security controls.

**Real-World Dev/IT Example**
Instead of waiting for an antivirus alert, a security analyst assumes the network is already breached and actively queries logs for powershell scripts making outbound connections at 3 AM.

**Gotchas & Dev Context**
- Threat hunting is hypothesis-driven (e.g., "I hypothesize attackers are hiding persistence in registry run keys").
- It requires rich log data (SIEM, EDR) to be effective.
- It is NOT automated alerting; it requires a human analyst thinking like an attacker.

**Production FAQ**
- **Q: When should a company start threat hunting?**
  A: Only after the basics (firewalls, EDR, patching, automated alerting) are mature. Hunting is an advanced capability.
- **Q: How do you measure hunting success?**
  A: By new detections created. If a hunt finds no attackers, the logic used should be turned into an automated alert for the future.

## 9. Red Team vs Blue Team vs Purple Team
**Definition**
Security roles based on wargaming terminology: Red attacks the systems, Blue defends them, and Purple acts as a feedback loop bridging the two to improve overall security.

**Real-World Dev/IT Example**
The Red Team launches a simulated phishing attack and tries to steal admin credentials. The Blue Team monitors the SIEM to detect and block them. The Purple Team reviews the exercise afterward to ensure Blue learns how Red bypassed their filters.

**Gotchas & Dev Context**
- **Red Teams** simulate real-world adversaries. They are stealthy and objective-focused (not just generic vulnerability scanners).
- **Blue Teams** handle defensive operations (SOC analysts, incident responders, engineers).
- **Purple Teams** are often a collaborative process rather than a standalone department, focusing on knowledge sharing.

**Production FAQ**
- **Q: Is penetration testing the same as Red Teaming?**
  A: No. Pen testing finds as many vulnerabilities as possible. Red teaming tests the organization's detection and response capabilities against a targeted objective.
- **Q: Who wins?**
  A: There are no winners. If the Blue Team doesn't improve their defenses based on the Red Team's findings, the exercise failed.

## 10. Sandboxing
**Definition**
An isolated, tightly controlled testing environment where suspicious software or code can be executed safely without affecting the host system or network.

**Real-World Dev/IT Example**
When an employee receives a suspicious email attachment, the email gateway automatically opens the file inside a virtual machine (sandbox) to see if it tries to download malware. If it behaves badly, the email is blocked.

**Gotchas & Dev Context**
- Advanced malware is "sandbox-aware" and will simply sleep or behave normally if it detects it is running inside a virtual machine or debugger.
- Sandboxing consumes significant compute resources and introduces latency (e.g., email delivery delays).
- Developers also use sandboxes to test untested code or APIs safely.

**Production FAQ**
- **Q: How does malware know it's in a sandbox?**
  A: It checks for VM drivers (like VMware tools), low RAM/CPU counts, lack of user interaction (mouse movement), or specific registry keys.
- **Q: Is a sandbox 100% safe?**
  A: Mostly, but "VM escape" vulnerabilities exist where malware breaks out of the hypervisor and infects the host.
