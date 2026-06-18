# Batch 3 — File Formats & OS Internals
> How operating systems load and execute binaries.

## PE (Portable Executable) Format (Windows)
### Definition
The standard file format for Windows executables, object code, and DLLs that tells the OS how to map the file into memory.

### Real-World Analysis Example
When analyzing Windows malware, a reverse engineer checks the PE headers using tools like PEStudio to find suspicious compilation timestamps or unexpected imports before running the code.

### ASCII Diagram
```text
+---------------------+
| DOS Header (MZ)     |
+---------------------+
| DOS Stub            |
+---------------------+
| PE Header (NT)      |
+---------------------+
| Section Headers     |
+---------------------+
| Sections (.text...) |
+---------------------+
```

### Gotchas & Dev Context
*   **"Portable" is historical:** It originally meant portable across different 32-bit Windows architectures (x86, MIPS, Alpha).
*   **Header modification:** Malware often obfuscates or wipes PE headers to break analysis tools that rely on standard offsets.

### Production FAQ
**Q: How do I view PE headers in Windows?**
A: Use tools like `dumpbin.exe /headers file.exe`, CFF Explorer, or PE-bear.

**Q: Can a PE file contain other PE files?**
A: Yes, "droppers" or installers often embed fully intact PE files in their resource sections (`.rsrc`).

## ELF (Executable and Linkable Format) (Linux)
### Definition
The standard binary format for executables, shared libraries, and core dumps on Linux and Unix-like operating systems.

### Real-World Analysis Example
When debugging a crashing Linux daemon, a developer analyzes the ELF core dump to inspect the exact memory state at the moment of the crash.

### ASCII Diagram
```text
+---------------------+
| ELF Header (0x7fELF)|
+---------------------+
| Program Header Table|
+---------------------+
| Sections (.text...) |
+---------------------+
| Section Header Table|
+---------------------+
```

### Gotchas & Dev Context
*   **Two views:** ELF has a "Linking View" (uses sections, needed for compilers) and an "Execution View" (uses segments, needed for the OS loader).
*   **Stripped binaries:** Release builds strip the symbol table, removing function names and making reverse engineering harder.

### Production FAQ
**Q: How do I inspect an ELF file?**
A: The standard Linux utility `readelf -a binary` or `objdump -d binary`.

**Q: Why does my binary run on Ubuntu but not Alpine?**
A: Alpine uses `musl` libc instead of `glibc`. The ELF file's interpreter (loader) points to a different missing library.

## Mach-O Format (macOS)
### Definition
The native executable format for macOS and iOS systems, used for programs, libraries, and object code.

### Real-World Analysis Example
A security researcher analyzing an iOS jailbreak exploit looks at the Mach-O load commands to understand how memory protections are configured for the target app.

### Gotchas & Dev Context
*   **Fat Binaries:** Mach-O supports "Universal Binaries," packing multiple architectures (e.g., Intel x86_64 and Apple Silicon ARM64) into a single file.
*   **Load Commands:** Unlike PE or ELF, Mach-O heavily relies on "Load Commands" immediately following the header to tell the kernel exactly what to do.

### Production FAQ
**Q: How do I examine Mach-O files natively on Mac?**
A: Use `otool -l binary` to view load commands or `MachOView` for a GUI.

**Q: What is a Universal Binary?**
A: An archive (fat header) containing multiple complete Mach-O files for different CPU architectures. The OS picks the right one at runtime.

## File Headers & Magic Numbers
### Definition
A short sequence of bytes at the very beginning of a file used by the OS and tools to instantly identify the file type, regardless of its extension.

### Real-World Analysis Example
An analyst is given a file named `invoice.pdf`. Running the Linux `file` command reveals the magic number is `MZ`, indicating it's actually a disguised Windows executable.

### Gotchas & Dev Context
*   **Extensions lie:** The OS loader ignores file extensions (like `.exe` or `.txt`) and strictly trusts the magic numbers and headers.
*   **Endianness matters:** Reading magic bytes programmatically requires understanding the byte order of the target architecture.

### Production FAQ
**Q: What are the common magic numbers?**
A: PE: `MZ` (`0x4D 0x5A`), ELF: `0x7f ELF` (`0x7F 0x45 0x4C 0x46`), Mach-O: `0xFEEDFACE` (32-bit) or `0xFEEDFACF` (64-bit).

**Q: How does the Linux `file` command work?**
A: It compares the first few bytes of the file against a database of known magic numbers stored in `/etc/magic` or `/usr/share/misc/magic`.

## Sections (.text, .data, .rdata, .bss)
### Definition
Distinct regions inside an executable file that separate different types of content like code, initialized variables, and read-only constants.

### Real-World Analysis Example
When unpacking malware, a reverse engineer watches for writes to the `.text` section, which normally shouldn't happen, indicating self-modifying code.

### ASCII Diagram
```text
+-----------------------+ Memory Permissions
| .text (Executable)    | Read + Execute
+-----------------------+
| .rdata (Constants)    | Read Only
+-----------------------+
| .data (Init Vars)     | Read + Write
+-----------------------+
| .bss (Uninit Vars)    | Read + Write (Zeroed)
+-----------------------+
```

### Gotchas & Dev Context
*   **`.bss` takes no space on disk:** It only defines the size needed in RAM for uninitialized variables. The OS zeros it out at load time.
*   **Permissions:** Security features like DEP/NX ensure only `.text` is executable, and data sections are non-executable.

### Production FAQ
**Q: Can section names be changed?**
A: Yes, compilers and packers often create custom names (e.g., UPX creates `.UPX0`, `.UPX1`). The OS loader doesn't care about the name, only the permissions.

**Q: Where do strings go?**
A: Hardcoded strings (like `"Hello World"`) are typically stored in the read-only `.rdata` (Windows) or `.rodata` (Linux) section.

## Import Address Table (IAT) & Export Address Table (EAT)
### Definition
Tables in a Windows PE file that list the external functions a program needs to import from DLLs (IAT) and the functions it provides for others to use (EAT).

### Real-World Analysis Example
By analyzing an executable's IAT, an analyst spots `InternetOpenUrlA` and `WriteFile`, immediately suggesting the program downloads a file from the internet and saves it to disk.

### Gotchas & Dev Context
*   **API Hooking:** Antivirus and game anti-cheats overwrite IAT entries to redirect function calls to their own monitoring code.
*   **Dynamic Loading:** Malware often leaves the IAT empty to hide intent, manually resolving functions at runtime using `GetProcAddress`.

### Production FAQ
**Q: What is the difference between IAT and EAT?**
A: EXEs usually have an IAT (they consume functions). DLLs usually have both an IAT (consuming) and an EAT (providing functions to others).

**Q: How do packers affect the IAT?**
A: Packers compress the original program and its IAT. The packed file has a tiny stub IAT (just enough to unpack itself), rebuilding the real IAT in memory later.

## Windows API (WinAPI)
### Definition
The core set of functions provided by the Windows operating system that allows applications to interact with the hardware, UI, and file system.

### Real-World Analysis Example
A reverse engineer sets a debugger breakpoint on the WinAPI function `CreateProcessInternalW` to intercept malware right before it launches a malicious child process.

### Gotchas & Dev Context
*   **A vs. W suffixes:** WinAPI functions often end in 'A' (ANSI/ASCII, 8-bit) or 'W' (Wide/Unicode, 16-bit). Modern Windows uses 'W' internally.
*   **User-mode vs. Kernel-mode:** `kernel32.dll` provides user-mode APIs, which eventually transition into `ntdll.dll` to make the actual jump to the kernel.

### Production FAQ
**Q: Where is WinAPI documented?**
A: The Microsoft Developer Network (MSDN) is the definitive source for WinAPI function signatures and behaviors.

**Q: Why do malwares avoid WinAPI?**
A: To evade detection, advanced malware bypasses standard WinAPI DLLs and calls kernel functions directly (Direct Syscalls).

## Linux Syscalls
### Definition
The fundamental interface between user-space applications and the Linux kernel, used to request privileged operations like reading files or sending network packets.

### Real-World Analysis Example
Using the `strace` command, a sysadmin tracks every syscall a failing web server makes to discover it's crashing because of a missing configuration file (`openat` returning `ENOENT`).

### Gotchas & Dev Context
*   **Calling convention:** Syscalls aren't called like normal functions. Programs load a syscall number into a specific CPU register (e.g., `rax` on x64) and execute a special `syscall` instruction.
*   **Stability:** The Linux kernel guarantees ABI stability for syscalls, meaning a binary compiled 20 years ago will still execute correct syscalls today.

### Production FAQ
**Q: How do C programs use syscalls?**
A: Usually indirectly. The C Standard Library (glibc) provides wrapper functions (like `printf()`) that internally format data and execute the `write()` syscall.

**Q: How do I monitor syscalls?**
A: Use `strace ./binary` on Linux. It intercepts and logs all system calls the process makes.

## Process Memory Layout
### Definition
The structured way an operating system organizes a running program in RAM, dividing it into segments for code, data, heap, and stack.

### Real-World Analysis Example
When exploiting a buffer overflow, an attacker targets a local variable on the Stack, overwriting the return address to point their execution into a payload stored on the Heap.

### ASCII Diagram
```text
High Addresses
+------------------+
| Stack (Grows V)  | <- Local vars, return addresses
+------------------+
|      ...         |
+------------------+
| Heap (Grows ^)   | <- Dynamic allocation (malloc)
+------------------+
| .bss / .data     | <- Global variables
+------------------+
| .text (Code)     | <- Executable instructions
+------------------+
Low Addresses
```

### Gotchas & Dev Context
*   **Virtual Memory:** Every process believes it has its own contiguous, private memory space starting at zero, thanks to the CPU's MMU and OS page tables.
*   **ASLR (Address Space Layout Randomization):** Modern OSes randomize where the stack, heap, and libraries are loaded to make memory-corruption exploits difficult.

### Production FAQ
**Q: What is the difference between Stack and Heap?**
A: The stack is fast, auto-managed, and used for temporary local variables. The heap is larger, manually managed (`malloc`/`free`), and used for dynamic data.

**Q: How do I view a process's memory layout?**
A: On Linux, `cat /proc/<pid>/maps`. On Windows, use tools like VMMap or Process Hacker.

## Dynamic Linking vs Static Linking (DLLs / SOs)
### Definition
Static linking bakes all required library code directly into the executable file, whereas dynamic linking loads shared libraries (DLLs/SOs) into memory only when the program runs.

### Real-World Analysis Example
An analyst easily decompiles a 50KB dynamically linked malware sample, but struggles with a 15MB statically linked Go binary because it contains thousands of bundled library functions they must manually filter out.

### Gotchas & Dev Context
*   **Size vs. Portability:** Statically linked binaries are huge but run anywhere without dependencies. Dynamically linked binaries are small but break if a required DLL/SO is missing ("DLL Hell").
*   **Updates:** Security patches to a dynamic library (like OpenSSL) instantly fix all programs using it. Statically linked programs must be recompiled individually.

### Production FAQ
**Q: What are the file extensions for dynamic libraries?**
A: `.dll` (Dynamic Link Library) on Windows, `.so` (Shared Object) on Linux, and `.dylib` on macOS.

**Q: How can I tell if a binary is statically or dynamically linked?**
A: On Linux, use `file binary` or `ldd binary`. `ldd` will list dynamic dependencies or say "not a dynamic executable."
