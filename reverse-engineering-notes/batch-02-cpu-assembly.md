# Batch 2 — CPU Architectures & Assembly
> Understanding the language of processors.

## 1. x86 / x64 Architecture

### Definition
The standard processor instruction set used in most PCs and servers. x86 refers to the 32-bit version, while x64 (AMD64) is the 64-bit extension.

### Real-World Analysis Example
Disassembling a suspicious `.exe` file to see if it calls Windows APIs to log keystrokes. 

### Gotchas & Context
- Uses a Complex Instruction Set Computing (CISC) design.
- Instructions have variable lengths (1 to 15 bytes), making disassembly tricky.
- Heavy backward compatibility means there are decades of legacy features still active.

### Production FAQ
**Q: Does an x64 processor run x86 code?**
Yes, modern OSs handle this seamlessly (e.g., WoW64 on Windows), allowing 32-bit apps to run on 64-bit hardware.

**Q: Why do reverse engineers prefer x64 analysis nowadays?**
Because most modern operating systems and compiled applications are 64-bit, giving them access to much larger memory spaces.

---

## 2. Registers (General Purpose, Instruction Pointer, Flags)

### Definition
Extremely fast, tiny storage locations built directly into the CPU. They hold data, track execution, and store operation results.

### Real-World Analysis Example
Monitoring the Instruction Pointer (`RIP`/`EIP`) in a debugger to pinpoint exactly which line of code executes before a program crashes.

### ASCII Diagram
```text
64-bit | RAX                         |
32-bit |          | EAX              |
16-bit |          |        | AX      |
 8-bit |          |        | AH | AL |
```

### Gotchas & Context
- **General Purpose**: `RAX`, `RBX`, `RCX`, `RDX`. (`RAX` usually holds function return values).
- **Instruction Pointer** (`RIP`/`EIP`): Points to the *next* instruction to run.
- **Flags** (`RFLAGS`): Stores boolean outcomes of operations (e.g., the Zero Flag indicates if a comparison resulted in a match).

### Production FAQ
**Q: Can I access memory directly without registers?**
Mostly no. CPUs load memory into registers, process it, and store it back.

---

## 3. Memory Segmentation

### Definition
An older technique for dividing memory into segments (Code, Data, Stack) for addressing and protection. 

### Real-World Analysis Example
Investigating a legacy 16-bit MS-DOS virus that modifies the Code Segment (`CS`) to inject malicious instructions.

### ASCII Diagram
```text
+------------------+
| Code Segment (CS)| <- Executable Instructions
+------------------+
| Data Segment (DS)| <- Global Variables
+------------------+
| Stack Segment(SS)| <- Local Vars & Call State
+------------------+
```

### Gotchas & Context
- Largely flattened out in modern 64-bit OSs; paging is preferred over segmentation for memory protection.
- Segment registers like `FS` and `GS` are still heavily used in Windows to store thread-local data like the Thread Environment Block (TEB).

### Production FAQ
**Q: Do I need to worry about segmentation in 64-bit reversing?**
Rarely, unless you are analyzing OS internals, anti-debugging tricks querying the TEB/PEB via `GS`/`FS`, or ancient legacy binaries.

---

## 4. Stack vs Heap

### Definition
The Stack is a fast, structured (LIFO) memory region for local variables and function execution. The Heap is a larger, disorganized region for dynamic, long-lived data.

### Real-World Analysis Example
Finding a dynamically allocated encryption key floating in the Heap, while finding the fixed-size loop counter for the encryption algorithm on the Stack.

### Gotchas & Context
- The stack grows *downwards* in memory (from higher addresses to lower addresses).
- Memory allocation on the heap (`malloc`, `new`) is slower and prone to fragmentation.
- The stack cleans up automatically when a function ends; the heap must be freed manually.

### Production FAQ
**Q: Why do attackers target the stack with buffer overflows?**
Because the stack stores the "return address" of functions. Overwriting it allows attackers to hijack control flow.

**Q: Can the heap be exploited?**
Yes, "heap spraying" and "use-after-free" bugs target heap management mechanisms to gain control.

---

## 5. Push / Pop Instructions

### Definition
Assembly commands that manage the stack. `push` adds data to the top of the stack, and `pop` removes data from the top.

### Real-World Analysis Example
Analyzing a function prologue where a register's value is saved via `push rbp` so it can be safely used and later restored via `pop rbp`.

### Gotchas & Context
- Every `push` should have a corresponding `pop`. Imbalanced stacks cause program crashes when returning.
- `push` decreases the stack pointer (`RSP`); `pop` increases it. 

### Production FAQ
**Q: Can I pop a value into a different register than I pushed it from?**
Absolutely. `push rax` followed by `pop rbx` is a valid way to move data, though `mov rbx, rax` is faster.

---

## 6. Call / Ret Instructions

### Definition
`call` transfers execution to a function while saving the return address. `ret` retrieves that saved address and jumps back to the caller.

### Real-World Analysis Example
During dynamic analysis, deciding to step *over* a `call MessageBoxA` to avoid getting lost in thousands of lines of internal OS UI code.

### Gotchas & Context
- `call` is essentially a `push next_instruction_address` followed by a `jmp target`.
- `ret` blindly trusts the top of the stack. If the stack is corrupted, `ret` jumps to garbage (or malicious code).

### Production FAQ
**Q: What is the difference between CALL and JMP?**
`call` intends to return (it saves the return address). `jmp` is a one-way trip (like a `goto`).

**Q: What is Return-Oriented Programming (ROP)?**
An exploit technique that chains multiple `ret` instructions together to execute existing snippets of code out of order.

---

## 7. Calling Conventions (cdecl, stdcall, fastcall)

### Definition
A standardized set of rules defining how functions receive arguments (via registers or stack) and who cleans up the stack afterward.

### Real-World Analysis Example
Reversing a 32-bit Windows API (`stdcall`), allowing you to infer that the last few `push` instructions before the `call` represent the function's arguments.

### Gotchas & Context
- **cdecl**: Arguments on stack, caller cleans up. Used by C programs.
- **stdcall**: Arguments on stack, callee cleans up. Used by 32-bit Windows APIs.
- **fastcall**: Passes first few arguments in registers (fast) rather than the stack.

### Production FAQ
**Q: How does x64 handle calling conventions?**
x64 largely unified this. Windows x64 uses a modified fastcall (`RCX`, `RDX`, `R8`, `R9`), and Linux uses System V AMD64 ABI (`RDI`, `RSI`, `RDX`, `RCX`, `R8`, `R9`).

---

## 8. ARM Architecture Basics

### Definition
A Reduced Instruction Set Computing (RISC) architecture known for power efficiency, commonly used in smartphones, IoT, and modern Macs (Apple Silicon).

### Real-World Analysis Example
Extracting and disassembling the firmware of an IoT smart doorbell to find hardcoded admin credentials.

### Gotchas & Context
- Uses a "Load/Store" architecture: data must be loaded into registers before processing; memory cannot be manipulated directly.
- Fixed instruction sizes (usually 4 bytes), making disassembly very clean and predictable.
- Uses Thumb mode (16-bit/32-bit instructions mixed) to save code space.

### Production FAQ
**Q: Is reversing ARM harder than x86?**
Generally, it's considered cleaner and more logical because of fixed instruction lengths and standardized behaviors, though learning the heavy register usage takes time.

---

## 9. MIPS Architecture Basics

### Definition
A classic, straightforward RISC architecture frequently found in embedded systems, routers, and legacy gaming consoles.

### Real-World Analysis Example
Analyzing a home router's firmware dump to uncover a backdoor vulnerability in its web administration interface.

### Gotchas & Context
- Highly register-dependent (32 general-purpose registers) to avoid slow memory accesses.
- **Branch Delay Slots**: The instruction immediately *following* a branch/jump is executed *before* the jump actually occurs. This is the biggest gotcha for beginners!

### Production FAQ
**Q: Why do branch delay slots exist?**
They are an artifact of early CPU pipelines. Executing the next instruction while the branch target was being calculated kept the CPU from wasting cycles.

**Q: Where will I realistically see MIPS today?**
Mostly in networking gear (routers, switches), IoT devices, and embedded controllers.
