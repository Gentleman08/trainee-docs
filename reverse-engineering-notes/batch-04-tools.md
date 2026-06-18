# Batch 4 — Disassembly & Decompilation Tools
> The essential toolkit for ripping binaries apart.

## Disassembler vs Decompiler
**Definition**
A disassembler converts machine code (1s and 0s) into human-readable assembly language (like `MOV`, `JMP`), while a decompiler attempts to translate that assembly back into higher-level code (like C/C++) to make the logic easier to follow. 

**Real-World Analysis Example**
When reversing malware, you'd use a disassembler to see exactly how registers are manipulated for a tricky anti-debugging check, but you'd rely on a decompiler to quickly understand the overall flow of its network communication loop.

**ASCII Diagram**
```text
Binary File (.exe)
       |
  [Disassembler]
       v
Assembly (MOV EAX, 1)
       |
   [Decompiler]
       v
C Pseudocode (return 1;)
```

**Gotchas & Context**
- Decompiled code is rarely 100% accurate; it's a "best guess" representation (often called pseudocode).
- Disassembly is closer to the truth but takes much longer to read and interpret.
- Optimization by the compiler can severely mangle the output, confusing decompilers.

**Production FAQ**
- *Q: Should I trust the decompiler output blindly?*
  A: No. Always verify weird-looking C code by checking the underlying assembly graph.
- *Q: Can a decompiler get me the exact original source code?*
  A: Never. Variable names, comments, and project structure are lost during compilation.

## IDA Pro (Interactive Disassembler)
**Definition**
IDA Pro is the industry-standard, commercial reverse engineering platform that analyzes binaries, generates control flow graphs, and supports a massive range of processor architectures. 

**Real-World Analysis Example**
A vulnerability researcher uses IDA Pro's graph view to trace user input from a vulnerable network parsing function down to a buffer overflow, visually tracking the execution paths.

**Gotchas & Context**
- It is notoriously expensive, though a free version exists with limited architectures.
- "Interactive" means you are expected to rename variables, fix types, and add comments as you analyze.
- The standard decompiler (Hex-Rays) is sold separately per architecture.

**Production FAQ**
- *Q: Why do professionals still use IDA when free alternatives exist?*
  A: Unmatched architecture support, a massive ecosystem of plugins (like IDAPython), and decades of reliability.
- *Q: What is IDAPython?*
  A: A scripting engine inside IDA that lets you automate repetitive tasks like renaming functions or extracting decryptor keys.

## Ghidra
**Definition**
Ghidra is a free, open-source software reverse engineering (SRE) framework created by the NSA, famous for including a powerful, built-in decompiler for all supported architectures out-of-the-box.

**Real-World Analysis Example**
A student analyzing an old MIPS router firmware loads it into Ghidra to quickly read the C-like pseudocode of the authentication bypass vulnerability without needing to buy a pricey MIPS decompiler.

**Gotchas & Context**
- Written in Java, so it can feel a bit sluggish or memory-heavy compared to C++ native tools.
- Collaborative by design; multiple users can work on the same binary via a shared project server.
- The default UI is cluttered but highly customizable.

**Production FAQ**
- *Q: Is Ghidra's decompiler as good as IDA's Hex-Rays?*
  A: It is highly competitive and often better for obscure architectures, though Hex-Rays is sometimes considered cleaner for standard x86/x64.
- *Q: Is it safe to run NSA software on my machine?*
  A: Yes. It is fully open-source and heavily audited by the security community since its release.

## Radare2 / Cutter
**Definition**
Radare2 (r2) is a blazing-fast, command-line framework for reverse engineering and binary analysis, while Cutter is its official graphical user interface (GUI) that makes it friendlier for visual users.

**Real-World Analysis Example**
An incident responder writes a quick bash script using `rabin2` (part of the r2 suite) to extract imports and sections from 500 suspicious binaries in seconds, without ever opening a GUI.

**Gotchas & Context**
- The r2 command line has a notoriously steep learning curve (commands look like `pdf`, `s main`, `afl`).
- Exceptionally fast at analyzing massive binaries that would choke other tools.
- Cutter integrates the r2 engine with modern decompilers like Ghidra's (via r2ghidra).

**Production FAQ**
- *Q: Why use command-line r2 instead of a GUI?*
  A: Speed, scriptability, and the ability to run it headless over SSH on a remote compromised server.
- *Q: I hate the command line. Should I use Cutter?*
  A: Absolutely. Cutter provides the speed of r2 with a modern interface, graphs, and decompilation.

## Binary Ninja
**Definition**
Binary Ninja (Binja) is a commercial reverse engineering platform known for its clean UI and Intermediate Languages (ILs) that make writing analysis scripts incredibly easy.

**Real-World Analysis Example**
A vulnerability researcher writes a Python script using Binary Ninja's Medium Level IL (MLIL) to automatically find all instances where a variable controlled by the user is passed directly to `system()`.

**ASCII Diagram**
```text
Assembly -> Low Level IL -> Medium Level IL -> High Level IL (Decompiled)
(Raw)       (Cleaned up)    (Variables mapped) (C-like Code)
```

**Gotchas & Context**
- Cheaper than IDA Pro but lacks some of the hyper-obscure processor support.
- Its Intermediate Languages (BNIL) abstract away CPU-specific quirks, so an analysis script written for x86 often works on ARM without changes.
- Highly praised for its responsive development team and modern Python API.

**Production FAQ**
- *Q: What makes BNIL so special?*
  A: It translates messy assembly into a standardized tree structure, making automated vulnerability discovery much simpler.
- *Q: Is there a free version?*
  A: Yes, "Binary Ninja Free" supports basic analysis but has limitations on saving and headless scripting.

## Hex Editors (HxD, 010 Editor)
**Definition**
Hex editors are tools that allow you to view and modify the raw byte-level data of a file, essential for patching binaries or analyzing unknown file formats.

**Real-World Analysis Example**
A malware analyst opens a malicious document in 010 Editor and uses a template to parse the file structure, quickly spotting an embedded PE executable hidden within the macro data.

**Gotchas & Context**
- Editing a binary directly can break its execution if you misalign instructions or corrupt headers.
- 010 Editor is famous for "Binary Templates" which automatically parse complex formats (like ZIP or PE headers) into readable structures.
- HxD is the go-to lightweight, free tool for simple byte patching on Windows.

**Production FAQ**
- *Q: How is this different from a disassembler?*
  A: Disassemblers interpret bytes as CPU instructions. Hex editors just show you the raw bytes and let you edit them directly.
- *Q: Why would I patch a binary?*
  A: To force a branch (like changing a `JNZ` to `JZ` to bypass a license check) or neuter a malicious function.

## Strings Analysis
**Definition**
Strings analysis involves extracting printable text sequences from a binary file to quickly gather clues about its functionality, such as IP addresses, registry keys, or error messages.

**Real-World Analysis Example**
Running the `strings` command on a suspicious executable reveals the text `http://evil.com/drop.exe`, instantly providing an Indicator of Compromise (IoC) to block on the firewall.

**Gotchas & Context**
- Malware authors often obfuscate or encrypt strings to hide them from simple analysis.
- Wide strings (UTF-16) require specific flags to extract (e.g., `strings -el` or `strings -a`).
- Finding a string doesn't mean the code actually uses it; it could be left over from a library or inserted as a decoy.

**Production FAQ**
- *Q: Should I run strings on every binary?*
  A: Yes. It is the cheapest, fastest triage step in reverse engineering.
- *Q: What if strings output is just garbage characters?*
  A: The binary is likely packed or encrypted. You will need to unpack it in memory before running strings analysis again.

## Dependency Walkers
**Definition**
Dependency Walkers are tools that list all the external libraries (DLLs/Shared Objects) and specific functions (Imports) an executable requires to run.

**Real-World Analysis Example**
By loading an unknown `.exe` into a dependency walker, you see it imports `CryptDecrypt` and `InternetOpenA`, strongly suggesting it is ransomware with network capabilities.

**Gotchas & Context**
- Modern binaries often load dependencies dynamically at runtime (using `LoadLibrary`/`GetProcAddress`), which hides them from static dependency walkers.
- Missing dependencies are the #1 reason a piece of malware won't run in your sandbox.
- The original `depends.exe` is severely outdated; modern alternatives include Dependencies (GitHub) or CFF Explorer.

**Production FAQ**
- *Q: How do I find dynamically loaded imports?*
  A: You have to run the binary in a debugger or sandbox and watch the API calls happen in real time.
- *Q: Why does my malware crash with a "DLL not found" error?*
  A: The author compiled it with custom libraries. You must simulate or provide those libraries for it to execute properly.

## Signatures (Flirt, YARA)
**Definition**
Signatures are unique patterns of bytes or strings used to identify specific compiler libraries, known malware families, or specific code behaviors across different files.

**Real-World Analysis Example**
A threat intel team writes a YARA rule searching for a specific combination of encryption keys and strings to scan their corporate network and detect all variants of a new ransomware strain.

**Gotchas & Context**
- FLIRT (Fast Library Identification and Recognition Technology) is used by IDA to automatically rename standard library functions (like `printf`), saving you from reverse-engineering boring boilerplate code.
- YARA is the "pattern matching swiss army knife" used globally for malware classification.
- Attackers frequently recompile code or use simple packers to break basic byte signatures.

**Production FAQ**
- *Q: How does FLIRT save me time?*
  A: Without FLIRT, statically linked standard functions look like custom code. FLIRT flags them so you can ignore them and focus on the author's actual logic.
- *Q: Can YARA match on more than just raw bytes?*
  A: Yes. YARA rules can include strings, regex, file size conditions, and even check specific PE header attributes.
