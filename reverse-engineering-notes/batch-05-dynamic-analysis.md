# Batch 5 — Dynamic Analysis & Debugging
> Analyzing binaries while they are running.

## 1. Debuggers

### Definition
A debugger is a software tool used to run, pause, and inspect another program as it executes. It allows analysts to observe CPU registers, memory, and program flow in real-time.

### Real-World Analysis Example
When analyzing a ransomware sample, you use a debugger to pause execution right before it calls the encryption routine, allowing you to steal the generated encryption key from memory before files are locked.

### Gotchas & Context
- **Anti-Debugging:** Malware frequently checks if a debugger is attached (e.g., `IsDebuggerPresent` on Windows) and will crash or change behavior if detected.
- **Safety Risk:** Debugging inherently runs the code. Always use a thoroughly isolated virtual machine.

### Production FAQ
**Q: How is dynamic analysis different from static analysis?**
A: Static analysis (disassemblers) shows you the code without running it. Dynamic analysis (debuggers) lets you run the code step-by-step to see actual runtime values and decrypted strings.

**Q: Can I debug any executable?**
A: Mostly yes, but stripped binaries without symbols take more effort, and packed binaries must be unpacked in memory first.

## 2. x64dbg / x32dbg

### Definition
x64dbg (and its 32-bit counterpart, x32dbg) is an open-source, user-mode Windows debugger that has become the modern standard for reverse engineering and malware analysis.

### Real-World Analysis Example
You load a suspicious executable into x64dbg, use the "Search for String References" feature to find where "License Key Invalid" is printed, and jump straight to that function to analyze the license check logic.

### ASCII Diagram
```text
[ GUI ] -> [ TitanEngine ] -> [ Windows Debug API ] -> [ Target Process ]
```

### Gotchas & Context
- **Plugins:** x64dbg's superpower is its plugin ecosystem (like ScyllaHide for anti-anti-debugging).
- **Interface:** It combines disassembly, CPU registers, stack, and hex dumps in one busy but efficient window.

### Production FAQ
**Q: Why use x64dbg over OllyDbg?**
A: OllyDbg is outdated, unsupported, and lacks 64-bit support. x64dbg is actively maintained and handles modern 64-bit binaries flawlessly.

**Q: Does it support scripting?**
A: Yes, it supports its own scripting language and has plugins for Python integration, useful for automating repetitive unpacking steps.

## 3. GDB (GNU Debugger)

### Definition
GDB is the standard command-line debugger for Linux and Unix-like systems. It is highly versatile, supporting multiple architectures and languages.

### Real-World Analysis Example
You use GDB on a Linux server to attach to a crashing web server process, inspect the stack trace at the moment of the crash, and identify a buffer overflow vulnerability.

### Gotchas & Context
- **Steep Learning Curve:** The raw command-line interface can be daunting. Most reverse engineers use enhancements like GEF, Pwndbg, or PEDA.
- **Syntax:** By default, GDB uses AT&T assembly syntax. You usually want to switch it: `set disassembly-flavor intel`.

### Production FAQ
**Q: How do I make GDB usable for reverse engineering?**
A: Install a plugin like GEF (GDB Enhanced Features). It adds colorized context, memory layout views, and exploit-development tools automatically.

**Q: Can GDB debug Windows binaries?**
A: Not natively. GDB is for Linux/Unix ELF binaries, though it can debug remote targets via gdbserver.

## 4. WinDbg

### Definition
WinDbg is Microsoft's official, highly powerful debugger for Windows. It operates at both user-mode and kernel-mode, making it the ultimate tool for low-level Windows analysis.

### Real-World Analysis Example
A company's laptops keep blue-screening (BSOD). You load the resulting memory dump file (`MEMORY.DMP`) into WinDbg and run `!analyze -v` to pinpoint the exact driver causing the crash.

### Gotchas & Context
- **Symbols:** WinDbg relies heavily on PDB (Program Database) symbol files. You must configure the Microsoft Symbol Server path for it to make sense of Windows internals.
- **Commands:** It uses cryptic meta-commands (e.g., `!peb`, `.symfix`).

### Production FAQ
**Q: When should I use WinDbg instead of x64dbg?**
A: Use WinDbg for kernel-mode debugging (analyzing rootkits or drivers) and analyzing crash dumps. Use x64dbg for everyday user-mode malware unpacking.

**Q: Is WinDbg difficult to set up?**
A: The classic WinDbg is clunky, but Microsoft released "WinDbg Preview" (now just WinDbg in the Microsoft Store), which features a much friendlier, modern UI.

## 5. Breakpoints (Software, Hardware, Memory)

### Definition
A breakpoint is an intentional stopping place placed in a program, forcing the debugger to pause execution so the analyst can inspect the current state.

### Real-World Analysis Example
You set a breakpoint on the Windows API `CreateFileW`. When the malware tries to drop a file, the debugger pauses, and you can read the intended filename directly from the stack before the file is even created.

### ASCII Diagram
```text
Execution Flow:
Instr 1 -> Instr 2 -> [ INT 3 (Breakpoint) ] -> PAUSED -> (Debugger takes control)
```

### Gotchas & Context
- **Software (INT 3):** Replaces an instruction byte with `0xCC`. Easily detected by malware scanning its own code.
- **Hardware (DR Registers):** Uses CPU debug registers. Undetectable by memory scans but limited in number (usually 4 on x86/x64).
- **Memory:** Modifies page permissions. Slow, but useful to catch *any* read/write to a large data block.

### Production FAQ
**Q: Why did my program crash when I set a breakpoint?**
A: The malware likely ran an integrity check, noticed the `0xCC` byte replacing its instruction, and intentionally crashed to thwart your analysis.

**Q: When should I use a hardware breakpoint?**
A: When you want to find out what function accesses a specific memory address (like a decrypted string) without altering the program's code.

## 6. Stepping (Step Into, Step Over)

### Definition
Stepping is the process of executing a program one assembly instruction at a time. It allows you to trace the exact path the CPU takes through the code.

### Real-World Analysis Example
You reach a complicated mathematical function inside a keygen. Instead of running the whole program, you step through the function line-by-line, watching how the registers transform your input to understand the algorithm.

### Gotchas & Context
- **Step Into (F7):** Follows the execution *inside* a called function. Use this to analyze a custom routine.
- **Step Over (F8):** Executes a called function completely and pauses on the next instruction. Use this to skip boring, standard system calls (like `printf`).
- **Getting Lost:** Rapidly stepping into system libraries (like `ntdll.dll`) is a common beginner mistake.

### Production FAQ
**Q: I accidentally stepped into a massive system API. How do I get out?**
A: Most debuggers have a "Execute till Return" or "Step Out" feature (often Ctrl+F9), which runs the rest of the current function and pauses when it returns to your code.

**Q: Should I step through the whole program?**
A: Never. It takes too long. Use breakpoints to jump to the interesting parts, then step carefully from there.

## 7. Process Attaching

### Definition
Attaching is the act of connecting a debugger to a process that is already running on the operating system, rather than launching the program from within the debugger itself.

### Real-World Analysis Example
A game has severe anti-debugging that triggers if you launch it from x64dbg. Instead, you start the game normally, wait for it to reach the main menu, and then attach your debugger to the running process to bypass the initial checks.

### Gotchas & Context
- **Permissions:** You must have sufficient privileges (e.g., Administrator / `sudo`) to attach to another process.
- **State Loss:** You miss all the initialization code that ran before you attached.

### Production FAQ
**Q: Why can't I attach to a specific process?**
A: The process might be running under a different user (like `SYSTEM`), or it might have anti-attach protections, such as hooking `NtDebugActiveProcess`.

**Q: Is it safe to detach from a process?**
A: Usually, yes. If you detach properly, the program continues running normally. If you just close the debugger, it typically kills the target process.

## 8. Memory Editing & Patching in Memory

### Definition
Memory editing involves modifying the data or instructions of a running program directly in RAM. This allows you to alter behavior on the fly without modifying the executable file on disk.

### Real-World Analysis Example
A program checks a license status: `cmp eax, 0` followed by `je fail_routine`. While paused in the debugger, you edit the zero flag in the CPU register, tricking the program into thinking the license is valid for that session.

### Gotchas & Context
- **Volatility:** Changes made in memory are lost as soon as the process terminates.
- **Code Caves:** If you need to write more instructions than you are replacing, you must find empty space (a code cave) in memory, write your logic there, and jump to it.

### Production FAQ
**Q: Why patch in memory instead of patching the binary on disk?**
A: The binary on disk might be packed or cryptographically signed. Once it unpacks itself into RAM, you can modify the plain code directly.

**Q: Can I change variables as well as code?**
A: Yes. You can edit hex values in the memory dump window to change strings, bypass counters, or modify configuration data mid-execution.

## 9. API Hooking

### Definition
API hooking is a technique used to intercept calls between a program and the operating system (or other libraries). It allows an analyst to monitor, log, or modify the data being passed back and forth.

### Real-World Analysis Example
To figure out how malware communicates, you hook the `InternetConnect` and `HttpSendRequest` Windows APIs. Every time the malware tries to send data, your hook logs the target IP and payload before letting the call proceed.

### ASCII Diagram
```text
[ Malware Call ] -> [ Hook (Logs Data) ] -> [ Real OS API ] -> [ Network ]
```

### Gotchas & Context
- **Inline Hooking:** Overwrites the first few bytes of a target function with a `JMP` instruction to your custom code.
- **IAT Hooking:** Modifies the Import Address Table of the binary to point to your custom function instead of the real one.

### Production FAQ
**Q: Do I have to write hooks manually?**
A: No, tools like API Monitor, Cuckoo Sandbox, and Frida handle the complex hooking mechanics automatically, letting you focus on the data.

**Q: Can malware detect hooks?**
A: Yes. Advanced malware will read the first bytes of system APIs looking for unexpected `JMP` instructions to ensure they haven't been tampered with.

## 10. Frida (Dynamic Instrumentation)

### Definition
Frida is a dynamic instrumentation toolkit that allows you to inject JavaScript or Python snippets into native apps on Windows, macOS, Linux, iOS, and Android to hook functions and modify behavior in real-time.

### Real-World Analysis Example
You are analyzing a mobile app that uses SSL pinning to block network interception. You write a short Frida script to hook the app's SSL verification function and force it to always return "True," instantly bypassing the protection.

### Gotchas & Context
- **Cross-Platform:** Frida is uniquely powerful because it works almost identically across mobile and desktop environments.
- **No Pausing:** Unlike a traditional debugger, Frida doesn't usually pause execution. It runs your scripts asynchronously as the program continues.

### Production FAQ
**Q: How is Frida different from x64dbg?**
A: x64dbg is a visual interface for pausing and stepping through assembly. Frida is a scripting framework for hooking functions and manipulating data programmatically while the app runs.

**Q: Do I need the source code to use Frida?**
A: No. Frida operates entirely on compiled, black-box binaries. You just need to know the memory addresses or function names you want to hook.
