# Batch 1 — Reverse Engineering Fundamentals
> Core concepts every reverse engineer must know.

## 1. Reverse Engineering (RE)
**Definition:** The process of deconstructing a compiled software application to understand its architecture, uncover its internal logic, or extract its algorithms without having access to the original source code.

**Real-World Analysis Example:** A malware analyst unpacks a new ransomware variant to determine which encryption algorithm it uses and whether a decryption key can be recovered.

**Gotchas & Context:**
* Source code is almost never 100% recoverable due to compilation loss.
* Compiler optimizations and code obfuscation make the resulting binaries highly complex.
* It requires deep knowledge of CPU architecture and operating system internals.

### Production FAQ
* **Do I need the original source code to reverse engineer?** No, you work entirely with the compiled executable (binary) and analyze its low-level instructions.
* **Is RE only used by hackers?** Not at all. It's heavily used by security vendors for malware analysis, developers for debugging, and engineers ensuring software interoperability.

## 2. Goals of Reverse Engineering
**Definition:** The underlying motives for tearing apart software, which typically include finding security vulnerabilities, building interoperable systems, recovering lost source code, or analyzing malicious behavior.

**Real-World Analysis Example:** Developing an open-source Linux driver for a proprietary graphics card by analyzing how the official Windows driver communicates with the hardware.

**Gotchas & Context:**
* You must clearly define your goal before starting, or you will get lost in millions of lines of assembly.
* Finding bugs requires a different approach (fuzzing, tracing) than algorithm extraction (deep static analysis).

### Production FAQ
* **Can RE recover lost source code completely?** It can recover the logic, but original variable names, comments, and exact structuring are permanently lost during compilation.
* **How do companies defend against this?** They use anti-debugging techniques, packers, and code obfuscators to make the reverser's goal mathematically or practically exhausting.

## 3. Static Analysis vs Dynamic Analysis
**Definition:** Static analysis examines the code without executing it (like reading a blueprint), while dynamic analysis observes the code while it is running (like test-driving a car).

**Real-World Analysis Example:** Using Ghidra to read a binary's strings and imports (Static), then running it in x64dbg to see what registry keys it modifies upon execution (Dynamic).

**ASCII Diagram:**
```text
[Binary File]
     |
     +--> Static Analysis  (Disassemblers) --> Focus: Code structure, logic
     |
     +--> Dynamic Analysis (Debuggers)     --> Focus: State, behavior, memory
```

**Gotchas & Context:**
* Static analysis is safe but can be thwarted by packed or encrypted code.
* Dynamic analysis reveals actual behavior but risks executing dangerous malware.
* Advanced malware detects dynamic analysis environments (VMs, debuggers) and hides its true behavior.

### Production FAQ
* **Which method should I start with?** Always start with basic static analysis to gauge what you're dealing with, then move to dynamic analysis for behavioral context.
* **What is symbolic execution?** It's an advanced hybrid technique that treats inputs as symbolic variables to map out all possible execution paths statically.

## 4. Machine Code vs Assembly Code
**Definition:** Machine code is the raw sequence of 1s and 0s (binary) executed directly by the CPU. Assembly code is the human-readable text representation of that exact machine code.

**Real-World Analysis Example:** The CPU executes the raw hex bytes `B8 01 00 00 00`. A reverse engineer uses a disassembler to read this as the assembly instruction `MOV EAX, 1`.

**Gotchas & Context:**
* There is a 1-to-1 mapping between machine code instructions and assembly instructions.
* Assembly language is architecture-specific. ARM assembly looks completely different from x86-64 assembly.
* Decompilers attempt to translate assembly back into high-level C/C++ pseudo-code, but it is an approximation.

### Production FAQ
* **Do I need to memorize machine code bytes?** No, disassemblers do the translation for you. However, recognizing common bytes (like `EB` for jump or `90` for NOP) speeds up patching.
* **Why not just read the binary in a hex editor?** Without a disassembler mapping the bytes to mnemonics, the structural logic of the program is impossible for humans to parse at scale.

## 5. Opcodes and Mnemonics
**Definition:** An opcode (operation code) is the specific machine code byte or byte sequence that tells the CPU what action to perform. A mnemonic is the human-friendly keyword used in assembly to represent that opcode.

**Real-World Analysis Example:** In the instruction `JMP 0x1000`, `JMP` is the mnemonic meaning "Jump", and its underlying opcode byte might be `E9`.

**ASCII Diagram:**
```text
Byte Data:    [ E9 ] [ 00 10 00 00 ]
                |            |
Translation:  Opcode       Operand
                |            |
Assembly:      JMP       0x1000
            (Mnemonic)
```

**Gotchas & Context:**
* An instruction usually consists of an opcode followed by operands (the data or addresses to act upon).
* Different CPU architectures define entirely different opcodes for the exact same conceptual operation.

### Production FAQ
* **Can multiple mnemonics share the same opcode?** Sometimes disassemblers use alias mnemonics for the same opcode if the context changes, but generally, opcodes map strictly to specific hardware operations.
* **What is a NOP?** `NOP` (No Operation) is a mnemonic for an opcode (like `0x90` in x86) that tells the CPU to do nothing and move to the next instruction. It's heavily used in binary patching.

## 6. Endianness (Little-Endian vs Big-Endian)
**Definition:** Endianness describes the byte order in which multi-byte data types are stored in computer memory. Little-endian stores the least significant byte first, while big-endian stores the most significant byte first.

**Real-World Analysis Example:** Storing the 32-bit hex value `0x11223344` in memory. In Little-Endian it is stored as `44 33 22 11`. In Big-Endian it is stored as `11 22 33 44`.

**ASCII Diagram:**
```text
Value: 0x11223344
Memory Addr:  0x00  0x01  0x02  0x03
Little-Endian: 44    33    22    11
Big-Endian:    11    22    33    44
```

**Gotchas & Context:**
* Intel x86/x64 processors are strictly Little-Endian.
* Network protocols (like IP addresses) generally use Big-Endian (Network Byte Order).
* Reading raw memory dumps requires constantly translating Little-Endian backwards in your head.

### Production FAQ
* **Why does Little-Endian exist?** It historically made it easier for early 8-bit CPUs to perform addition on multi-byte numbers, starting with the least significant byte.
* **How does this affect reversing?** If you see `78 56 34 12` in a hex editor on a Windows machine, you must remember the actual value the program sees is `0x12345678`.

## 7. Legal & Ethical Aspects of RE
**Definition:** The legal frameworks and ethical boundaries governing when reverse engineering is permitted, usually balancing intellectual property rights against the need for security research and interoperability.

**Real-World Analysis Example:** Reverse engineering a proprietary messaging protocol to build a compatible open-source chat client, which is generally protected under interoperability laws in many jurisdictions.

**Gotchas & Context:**
* Bypassing Digital Rights Management (DRM) or software licensing is often illegal under laws like the DMCA.
* Using RE to steal trade secrets or duplicate a competitor's proprietary code is illegal.
* End User License Agreements (EULAs) frequently forbid RE, though courts sometimes overrule EULAs for security research.

### Production FAQ
* **Is malware analysis legal?** Yes, analyzing malicious code to protect systems is widely legally protected and encouraged.
* **Can I publish my RE findings?** It depends. Publishing vulnerabilities responsibly is standard practice, but publishing DRM-bypassing keys or proprietary algorithms can invite lawsuits.

## 8. Clean Room Design
**Definition:** A legally defensible method of reverse engineering where one team analyzes a product to write technical specifications, and a completely separate team uses only those specifications to build a new, non-infringing product.

**Real-World Analysis Example:** Phoenix Technologies creating the first legal clone of the IBM PC BIOS. Team A reverse-engineered IBM's hardware to write a manual. Team B, having never seen IBM's code, wrote the new BIOS using only Team A's manual.

**ASCII Diagram:**
```text
Original -> [Team A] -> Spec Document -> [Team B] -> Legal Clone
Product     (Reversers)   (No Code!)   (Developers)
```

**Gotchas & Context:**
* It requires strict legal oversight, documentation, and physical/digital separation of teams.
* If Team B developers are found to have even glanced at the original proprietary code, the entire project can be legally compromised.

### Production FAQ
* **Why go through this massive effort?** It's the safest way to achieve software interoperability while proving in court that zero copyright infringement occurred.
* **Is this still used today?** Yes, heavily in emulator development (like video game console emulators) and proprietary protocol implementations.

## 9. Patching / Binary Modification
**Definition:** The process of altering a compiled binary file by directly modifying its underlying machine code bytes to change the software's execution flow or behavior.

**Real-World Analysis Example:** Modifying an offline video game binary by replacing a `JZ` (Jump if Zero) instruction with `JNZ` (Jump if Not Zero) to permanently bypass a CD-ROM validation check.

**Gotchas & Context:**
* Adding new code is difficult because it shifts file offsets. Reversers usually overwrite existing instructions.
* If the new instruction is smaller than the old one, the remaining bytes must be padded with `NOP` (No Operation) instructions to align the code.
* Modern binaries use digital signatures and anti-tamper mechanisms that crash the program if modifications are detected.

### Production FAQ
* **How do I actually change the bytes?** You use a hex editor or the patching features built into debuggers like x64dbg/Ghidra to export a modified executable.
* **Why pad with NOPs?** If an old instruction is 5 bytes and your new instruction is 2 bytes, leaving the 3 old leftover bytes will cause the CPU to interpret garbage and crash. You replace them with `0x90` (NOPs).
