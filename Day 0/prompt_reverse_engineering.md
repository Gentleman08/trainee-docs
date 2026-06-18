# PROMPT — Reverse Engineering Notes

Write me new notes on Reverse Engineering & Malware Analysis in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world development/analysis example
- ASCII diagram if applicable
- Add gotchas and reverse-engineer-related context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with architecture, code/assembly snippets, analysis steps, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete Reverse Engineering Glossary

### Batch 1 — Reverse Engineering Fundamentals
Reverse Engineering (RE)
Goals of Reverse Engineering
Static Analysis vs Dynamic Analysis
Machine Code vs Assembly Code
Opcodes and Mnemonics
Endianness (Little-Endian vs Big-Endian)
Legal & Ethical Aspects of RE
Clean Room Design
Patching / Binary Modification

### Batch 2 — CPU Architectures & Assembly
x86 / x64 Architecture
Registers (General Purpose, Instruction Pointer, Flags)
Memory Segmentation
Stack vs Heap
Push / Pop Instructions
Call / Ret Instructions
Calling Conventions (cdecl, stdcall, fastcall)
ARM Architecture Basics
MIPS Architecture Basics

### Batch 3 — File Formats & OS Internals
PE (Portable Executable) Format (Windows)
ELF (Executable and Linkable Format) (Linux)
Mach-O Format (macOS)
File Headers & Magic Numbers
Sections (.text, .data, .rdata, .bss)
Import Address Table (IAT) & Export Address Table (EAT)
Windows API (WinAPI)
Linux Syscalls
Process Memory Layout
Dynamic Linking vs Static Linking (DLLs / SOs)

### Batch 4 — Disassembly & Decompilation Tools
Disassembler vs Decompiler
IDA Pro (Interactive Disassembler)
Ghidra
Radare2 / Cutter
Binary Ninja
Hex Editors (HxD, 010 Editor)
Strings Analysis
Dependency Walkers
Signatures (Flirt, YARA)

### Batch 5 — Dynamic Analysis & Debugging
Debuggers
x64dbg / x32dbg
GDB (GNU Debugger)
WinDbg
Breakpoints (Software, Hardware, Memory)
Stepping (Step Into, Step Over)
Process Attaching
Memory Editing & Patching in Memory
API Hooking
Frida (Dynamic Instrumentation)

### Batch 6 — Anti-Analysis & Obfuscation
Anti-Debugging Techniques (IsDebuggerPresent)
Anti-VM / Sandbox Evasion
Code Obfuscation
String Encryption
Packing vs Unpacking
UPX (Ultimate Packer for Executables)
Code Mutation / Metamorphism
Control Flow Flattening
Timing Attacks (for evasion)

### Batch 7 — Malware Analysis
Malware Triage
Behavioural Analysis
Process Monitor (ProcMon) / Process Explorer
Process Injection / Process Hollowing
Droppers & Downloaders
C2 (Command & Control) Communication
Ransomware Cryptography Mechanics
Rootkits / Bootkits
Living off the Land (LotL)

### Batch 8 — Exploit Development Basics
Buffer Overflow
Stack Layout (EBP, ESP, EIP)
Shellcode
NOP Sleds
Return Oriented Programming (ROP)
ASLR (Address Space Layout Randomization)
DEP / NX Bit (Data Execution Prevention)
Stack Canaries
Fuzzing

---

## PART 2 — Project Case Studies

### Case Study 1: Unpacking and Analyzing a Ransomware Sample

Safely analyze a packed ransomware executable to extract Indicators of Compromise (IoCs) and understand its encryption mechanism.
- Set up an isolated malware analysis lab (sandbox)
- Perform static triage (identifying packing)
- Dynamically unpack the payload from memory
- Decompile the unpacked payload to identify the encryption loop and C2 domains

**Cover in the case study:**
- Analysis flow diagram (ASCII)
- Tech stack: FlareVM / REMnux, Wireshark, x64dbg, Ghidra, PE Bear
- Snippets: Assembly snippet showing the unpacking routine, Python script to extract configurations
- Analysis steps: Identifying the Original Entry Point (OEP), dumping memory, rebuilding the IAT
- Gotchas: Sandbox detection causing the malware to sleep, anti-dumping tricks, corrupted PE headers
- Lessons learned

### Case Study 2: Finding and Exploiting a Buffer Overflow

Discover and write a working exploit for a classic stack-based buffer overflow in a legacy 32-bit Linux C application.
- Fuzz the application to find the crash point
- Control the Instruction Pointer (EIP)
- Find bad characters
- Generate shellcode
- Write a Python exploit script

**Cover in the case study:**
- Stack memory diagram (ASCII) showing the overflow overwriting EIP
- Tech stack: GDB with PEDA/GEF, Python (pwntools), vulnerable C code
- Snippets: The vulnerable C function (e.g., using `strcpy`), the exploit generation script
- Mitigation context: How ASLR and NX would prevent this, and why they were disabled for this exercise
- Gotchas: Off-by-one errors, bad characters breaking the payload, environment variable shifts affecting stack addresses
- Lessons learned
