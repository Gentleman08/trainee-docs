# Case Study 1 — Unpacking and Analyzing a Ransomware Sample
> Safely dissecting packed malware to extract IoCs and understand encryption logic.

## 1. Project Overview
This project involves the deep technical analysis of a packed ransomware sample. The goal is to safely unpack the payload, extract crucial Indicators of Compromise (IoCs) such as Command and Control (C2) domains, and understand the core encryption loop. Security operations center (SOC) analysts, incident responders, and threat hunters use the outputs of this analysis to write detection rules (e.g., YARA, Snort) and remediate compromised systems.

## 2. Architecture Diagram

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|  Packed Malware   +------>+  Dynamic Unpacking    +------>+ Unpacked Payload  |
|  (Initial Sample) |       |  (Memory Dump via     |       | (Raw Executable)  |
|                   |       |  x64dbg / Scylla)     |       |                   |
+--------+----------+       +-----------------------+       +---------+---------+
         |                                                            |
         v                                                            v
+--------+----------+                                       +---------+---------+
|                   |                                       |                   |
|  Static Triage    |                                       | Reverse Eng.      |
|  (PE Bear, DiE)   |                                       | (Ghidra, IDA Pro) |
|                   |                                       |                   |
+-------------------+                                       +---------+---------+
                                                                      |
                                                                      v
                                                            +---------+---------+
                                                            |                   |
                                                            | IoC Extraction &  |
                                                            | Config Decryption |
                                                            | (Python Script)   |
                                                            |                   |
                                                            +-------------------+
```

## 3. Tech Stack Table

| Component | Tool / Technology | Purpose |
| --- | --- | --- |
| **Environment** | FlareVM (Windows) / REMnux (Linux) | Isolated malware analysis lab sandbox |
| **Static Triage** | PE Bear, Detect It Easy (DiE) | Identifying packing, analyzing PE headers |
| **Dynamic Analysis** | x64dbg, Scylla | Identifying OEP, dumping memory, rebuilding IAT |
| **Network Analysis**| Wireshark, INetSim | Capturing C2 traffic, simulating network services |
| **Disassembly** | Ghidra | Decompiling the unpacked payload, identifying encryption loops |
| **Scripting** | Python 3, `pefile`, `yara` | Automating configuration extraction and decryption |

## 4. Step-by-Step Build

### Phase 1: Set up an Isolated Malware Analysis Lab (Sandbox)
1. Provision a host-only network hypervisor environment.
2. Install FlareVM on a Windows guest for debugging and REMnux on a Linux guest for network simulation.
3. Configure INetSim and Wireshark on REMnux to capture all outbound DNS and HTTP/S traffic from the Windows machine.

### Phase 2: Perform Static Triage
1. Load the sample into Detect It Easy (DiE) to identify the packer (e.g., UPX, Custom).
2. Examine the PE headers using PE Bear. Anomalies such as a high entropy `.data` section and very few imported functions often indicate a packed executable.

### Phase 3: Dynamically Unpack the Payload from Memory
1. Load the malware into `x64dbg`.
2. Trace the execution to bypass the unpacking stub. Look for a `tail jump` or a transition from a memory allocation back to the executable's image base.
3. Once the Original Entry Point (OEP) is reached, use the Scylla plugin to dump the decrypted process memory to disk.
4. Use Scylla to fix and rebuild the Import Address Table (IAT) so the dumped executable can be analyzed statically.

### Phase 4: Decompile and Extract Configurations
1. Import the dumped, unpacked PE file into Ghidra.
2. Search for cryptographic API calls (e.g., `CryptEncrypt`) or custom XOR/AES loops.
3. Locate the configuration block containing encrypted C2 domains and ransom notes.

## 5. Code Snippets

### Assembly: Typical Unpacking Tail Jump (x86)
When tracing in `x64dbg`, look for the transition from the unpacking stub to the Original Entry Point (OEP).

```assembly
; Unpacking loop finishes here
0040A120  popad                     ; Restore general purpose registers
0040A121  popfd                     ; Restore EFLAGS
0040A122  push eax                  ; Push OEP onto the stack
0040A123  ret                       ; Jump to OEP (tail jump)
```

### Python: Extracting the Ransomware Configuration
A Python script utilizing the `pefile` library to extract and decrypt the C2 configuration from a known offset in the unpacked sample.

```python
import pefile
import struct

def rc4_decrypt(data, key):
    S = list(range(256))
    j = 0
    out = []
    
    # KSA
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
        
    # PRGA
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])
        
    return bytes(out)

def extract_config(file_path):
    # Load the unpacked executable
    pe = pefile.PE(file_path)
    
    # Assume config is in the .rdata section, hardcoded offset for this sample
    for section in pe.sections:
        if b".rdata" in section.Name:
            data = section.get_data()
            
            # Extract 16-byte RC4 key and 64-byte encrypted payload
            rc4_key = data[0x100:0x110]
            encrypted_c2 = data[0x110:0x150]
            
            decrypted = rc4_decrypt(encrypted_c2, rc4_key)
            print(f"[+] Decrypted C2 Domain: {decrypted.decode('utf-8', errors='ignore').strip(chr(0))}")

if __name__ == "__main__":
    extract_config("unpacked_ransomware.bin")
```

## 6. Deployment Steps
While manual analysis happens in a lab, at scale, you need an automated pipeline to handle thousands of samples daily.
1. **Automated Sandbox:** Deploy CAPEv2 Sandbox via Docker on bare-metal servers to process incoming samples automatically.
2. **Memory Dumping:** Configure CAPE to trigger memory dumps upon detecting process hollowing or injection.
3. **YARA Scanning:** Integrate a CI/CD pipeline (e.g., GitHub Actions) to automatically deploy updated YARA rules to the sandbox instances.
4. **Data Aggregation:** Push the extracted IoCs and behavioral logs to a central SIEM (e.g., Splunk or Elastic Security) via logstash.

## 7. Evaluation & Monitoring
- **Metrics:** Track the "Unpack Success Rate" (percentage of samples where OEP was successfully found automatically).
- **Tools:** Use Kibana to visualize the frequency of specific C2 IP addresses or Mutexes across different malware families over time.
- **Alerting:** Set up Slack/PagerDuty alerts when a new, unknown ransomware variant successfully bypasses the automated sandboxes.

## 8. Cost Analysis
- **On-Premises Infrastructure:** Running bare-metal servers for automated sandboxing (to prevent VM-detection) costs roughly $10,000 upfront for hardware + $200/month for electricity and networking.
- **Cloud Analytics:** Storing TBs of PCAP and memory dump data in AWS S3 Standard-IA costs approximately $12.50 per TB/month.
- **Software:** Using open-source tools (REMnux, CAPE, Ghidra) keeps software licensing costs to $0, substituting CAPEX with internal engineering time.

## 9. Production Gotchas
- **Sandbox Evasion causing the malware to sleep:** Malware checking `IsDebuggerPresent()` or looking for typical VM drivers (e.g., VMWare Tools) will simply exit or call `Sleep(999999)`. Use anti-anti-debugging plugins like ScyllaHide.
- **Anti-Dumping Tricks:** The malware may erase its PE header from memory (`SizeOfImage` manipulation) once loaded, breaking standard dumping tools. You must reconstruct the PE header manually.
- **Corrupted IATs:** Some packers destroy original API names and use API hashing or direct syscalls. Scylla might fail to rebuild the Import Address Table automatically, requiring manual resolution of imports.
- **Process Hollowing / Doppelgänging:** Instead of unpacking in its own memory space, the malware might start a legitimate process (like `svchost.exe`) suspended, hollow it out, and inject the malicious payload.

## 10. Lessons Learned
- **Static vs. Dynamic:** Relying purely on static analysis is incredibly time-consuming for packed samples. Mastering a debugger to let the malware unpack itself is a critical time-saver.
- **Automation is Key:** While manually unpacking is fun, an automated sandbox with reliable memory dumping is required for production threat intelligence.
- **Tool Familiarity:** Ghidra’s decompiler is powerful, but understanding the underlying assembly is still necessary when dealing with corrupted memory dumps or custom obfuscation loops.
