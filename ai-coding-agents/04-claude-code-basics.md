# 04 — Claude Code: Basics, Modes & Safe Everyday Use

[⬅️ Back to Index](README.md) · [⬅️ Previous: Antigravity Customization](03-antigravity-customization.md)

---

> **Claude Code** is Anthropic's AI coding agent. It runs in your **terminal** (`claude`), inside
> **VS Code / JetBrains** (extension), as a **desktop app**, and on the **web**. This chapter
> covers installing it, the permission modes, and the commands and habits you'll use every day.
> Customization (settings, CLAUDE.md, skills, hooks, MCP…) is in [Chapter 05](05-claude-code-customization.md).

> 📝 Based on the official docs at code.claude.com/docs as of October 2026. Type `/` inside
> Claude Code to see the commands your version actually has, and `/help` for help.

---

## Table of Contents

- [4.1 Install, verify, log in](#41-install-verify-log-in)
- [4.2 GUI options: VS Code, JetBrains, desktop, web](#42-gui-options)
- [4.3 First run: the trust dialog and your first prompt](#43-first-run)
- [4.4 Understanding permission prompts](#44-understanding-permission-prompts)
- [4.5 Permission modes](#45-permission-modes)
- [4.6 Plan mode: think before touching anything](#46-plan-mode)
- [4.7 Essential slash commands](#47-essential-slash-commands)
- [4.8 Keyboard shortcuts & input tricks](#48-keyboard-shortcuts-and-input-tricks)
- [4.9 Undo: checkpoints, rewind, Git](#49-undo-checkpoints-rewind-git)
- [4.10 Managing context (why long chats get worse)](#410-managing-context)
- [4.11 Sessions: continue, resume, parallel work](#411-sessions)
- [4.12 Models, effort and cost](#412-models-effort-and-cost)
- [4.13 Windows-specific notes](#413-windows-specific-notes)
- [4.14 Gotchas](#414-gotchas)

---

## 4.1 Install, verify, log in

```powershell
# Windows (PowerShell) — native installer
irm https://claude.ai/install.ps1 | iex
```

```bash
# macOS / Linux / WSL2 — native installer
curl -fsSL https://claude.ai/install.sh | bash
```

```bash
claude --version     # verify
claude doctor        # health check: install, settings, permissions problems
```

> The official docs also list other options (package managers, npm). The native installer is
> the recommended path and **auto-updates**.

**Log in:** run `claude` and follow the browser prompt. You can use a **Claude subscription**
(Pro/Max/Team/Enterprise) or an **Anthropic Console (API) account**. Companies may configure
Amazon Bedrock / Google Vertex AI / Microsoft Foundry instead. Ask your platform team.

> ⚠️ **Work code + personal account?** Check your company's AI policy first. Many companies
> require their Team/Enterprise plan, which has centrally managed settings (§5.1, "managed").

---

## 4.2 GUI options

| Surface | How | Good for |
|---------|-----|---------|
| **VS Code extension** | Extensions → search "Claude Code" (Anthropic) → install | Visual diffs, clicking through changes, beginners |
| **JetBrains plugin** | IntelliJ/PyCharm/WebStorm plugin marketplace | JetBrains users |
| **Desktop app** | Download from claude.ai | Working without an editor; multiple sessions |
| **Web (claude.ai/code)** | Browser, runs in Anthropic's cloud sandbox on your GitHub repos | Tasks while away from your machine; isolated by design |
| **CLI** | `claude` in any terminal | Speed, automation, SSH, full feature set |

All of them use the **same configuration files** (`CLAUDE.md`, `.claude/settings.json`,
skills, hooks…), so you can switch freely.

> 🧭 **Beginner path:** install the **VS Code extension** first. It shows proposed edits as
> side-by-side diffs that you accept or reject. Move to the CLI once you're comfortable.

---

## 4.3 First run

```bash
cd path/to/your/project      # always start inside the project folder
claude
```

1. **Trust dialog:** Claude Code asks whether you trust this folder. Repos can contain
   `CLAUDE.md` instructions, hooks and settings that influence the agent, so **only trust
   folders whose contents you know**.
2. **Create a project memory file:** run **`/init`**. Claude scans the repo and writes a starter
   `CLAUDE.md` (project overview, commands, conventions). Review and edit it (Chapter 05).
3. **First safe prompt:** *"Explain what this project does and how it's structured. Don't change anything."*

---

## 4.4 Understanding permission prompts

By default, Claude Code **asks before acting** on anything risky:

| Tool type | Example | Asks by default? | "Yes, and don't ask again" lasts |
|-----------|---------|------------------|-----------------------------------|
| Read-only | Read files, search (Grep) | **No**, within the working directory | — |
| Bash commands | `npm test`, `git commit` | **Yes**, except a built-in set of read-only commands | **Permanently** for that repo + command |
| File edits | Edit/Write | **Yes** | Until the session ends |
| Web fetch | Download a URL | Yes (except preapproved documentation sites) | Permanently for that repo + domain |
| Web search | Search the web | Yes | Permanently for that repo |

A Bash prompt looks roughly like:

```
Bash command
  npm test
  Run the test suite
This command requires approval
Do you want to proceed?
❯ 1. Yes
  2. Yes, and don't ask again for: npm test *
  3. No (Esc)  — and tell Claude what to do differently
```

**How to answer like a pro:**

- **Read the actual command**, not just the description.
- Use **"don't ask again"** only for harmless, repetitive commands (`npm test`, `git status`).
  Each "don't ask again" becomes a saved **allow rule**. Review them with `/permissions`.
- Choose **No** and type the correction ("use pnpm, not npm"). The agent adapts.
- `Tab` lets you **amend** the proposed command in some prompts.

---

## 4.5 Permission modes

Cycle modes with **`Shift+Tab`** (the current mode shows near the prompt), start with
`claude --permission-mode <mode>`, or set a default with `defaultMode` in settings.

| Mode | What it does | Use it when |
|------|-------------|-------------|
| **`default`** (shown as **Manual**) | Asks the first time each tool is used | ✅ Learning; unfamiliar repos |
| **`acceptEdits`** | Auto-accepts file edits and simple filesystem commands (`mkdir`, `touch`, `mv`, `cp`) inside your working dirs; still asks for other commands | You trust the task and will review the diff at the end |
| **`plan`** | Reads and explores; **doesn't edit your source files** | ✅ Start of every non-trivial task |
| **`auto`** | No routine prompts; a background **classifier** checks risky actions (commands, network) against your request | Experienced users wanting flow, where available on your plan |
| **`dontAsk`** | Auto-**denies** anything that would prompt; only pre-approved tools run | Locked-down automation |
| **`bypassPermissions`** | Skips prompts (except a few protected actions) | ⚠️ **Only in containers/VMs**: never on your real machine |

```
 Safety  ◄──────────────────────────────────────────────────────────►  Speed
 dontAsk   plan   default(Manual)   acceptEdits   auto   bypassPermissions
```

> ⚠️ The docs warn: in `bypassPermissions`, Claude Code even writes to protected paths like
> `.git` and `.claude` without asking. *"Only use this mode in isolated environments like
> containers or VMs."* Organisations can disable it (and auto mode) with
> `permissions.disableBypassPermissionsMode` / `permissions.disableAutoMode` set to `"disable"`.

> 💡 **About auto mode:** it reduces prompt fatigue, but a classifier isn't you. Pair it with
> **deny rules** for things that must never happen, plus the **sandbox** (§5.10).

---

## 4.6 Plan mode

Plan mode is the single best habit for beginners.

```
 Shift+Tab until "plan" is shown
 You:    "Add rate limiting to the login endpoint. Plan only."
 Claude: reads files, maybe runs read-only commands, then presents a PLAN:
           1. Add express-rate-limit middleware in src/middleware/rateLimit.ts
           2. Apply to POST /login in src/routes/auth.ts
           3. Add tests in tests/auth.rateLimit.test.ts
           4. Document in README
 You:    review → "Use our existing Redis client instead of an in-memory store" → approve
 Claude: switches out of plan mode and implements (with normal permission prompts)
```

Why it works: misunderstandings get caught **before** any file changes. It's the same idea as
Antigravity's implementation-plan artifact.

---

## 4.7 Essential slash commands

| Command | What it does |
|---------|-------------|
| `/help` | Help and command list |
| `/init` | Generate a starter `CLAUDE.md` for this repo |
| `/memory` | Open/edit memory files (CLAUDE.md) |
| `/permissions` | View/edit allow, ask and deny rules |
| `/config` | Settings UI (theme, defaults, etc.) |
| `/model` | Switch model |
| `/effort` | Reasoning effort level |
| `/clear` | Start a fresh conversation (new context) |
| `/compact [instructions]` | Summarise the conversation to free context |
| `/context` | Show what's using the context window |
| `/rewind` | Go back to an earlier point (conversation and/or code) |
| `/resume` | Pick a previous session |
| `/add-dir <path>` | Give access to another folder |
| `/agents` | Manage subagents |
| `/mcp` | Manage MCP servers |
| `/hooks` | View hooks |
| `/sandbox` | Configure the Bash sandbox |
| `/plugin` | Browse/install plugins |
| `/statusline` | Set up a status line |
| `/doctor` | Diagnose problems (also `claude doctor`) |
| `/usage` · `/cost` | Usage / cost information (depends on plan) |
| `/<your-skill>` | Run one of your skills (Chapter 05) |

---

## 4.8 Keyboard shortcuts and input tricks

| Keys / syntax | Action |
|---------------|--------|
| `Esc` | **Interrupt** Claude immediately (it keeps context; tell it what to change) |
| `Esc` `Esc` (twice) | Open **rewind** to jump back to an earlier message/checkpoint |
| `Shift+Tab` | Cycle permission modes (Manual → accept edits → plan → …) |
| `@path/to/file` | Reference a file or folder in your prompt |
| `!command` | Run a shell command yourself; output goes into the conversation (e.g. `! git status`) |
| `/` | Command & skill menu |
| `Ctrl+C` | Cancel input / exit |
| `↑` | Previous prompts |
| Paste an image | Screenshots of UI bugs or error dialogs (supported terminals/IDE) |
| `\` + `Enter` or `Shift+Enter` (if configured) | New line in the prompt |

Customise keys with `/keybindings` or `~/.claude/keybindings.json`.

---

## 4.9 Undo: checkpoints, rewind, Git

Claude Code automatically saves **checkpoints** of files it edits during a session.

- **`Esc Esc`** or **`/rewind`** lets you pick an earlier point and restore the **conversation**,
  the **code**, or both.
- Checkpoints cover edits made through Claude's **file tools**. Changes made by **shell
  commands** (e.g. a script that deletes files, `git` operations) or by you outside Claude
  **may not be restorable** this way.

> 🛡️ **So Git is still the real safety net:** commit before a task, work on a branch or
> worktree, and check `git diff` before accepting the result.

---

## 4.10 Managing context

The **context window** holds everything Claude has seen in this session. As it fills up:

- older details get **summarised** (compacted) and nuance is lost,
- responses get slower and cost more,
- the agent is more likely to get confused.

| Situation | Do this |
|-----------|---------|
| Starting an unrelated task | **`/clear`** (fresh context) |
| Same task, conversation getting long | **`/compact Focus on the payment bug; drop the CSS discussion`** |
| Don't know what's eating context | **`/context`** |
| Big investigation (read 50 files) | Ask Claude to use a **subagent** for it. Only the summary comes back to your main context |
| Instructions repeated every session | Move them into **`CLAUDE.md`** (Chapter 05) |

---

## 4.11 Sessions

```bash
claude -c                     # continue the most recent session in this folder
claude -r                     # pick a session to resume (also /resume inside)
claude -p "question"          # one-shot, non-interactive (Chapter 05 §5.11)
```

**Parallel work safely: git worktrees**

```bash
git worktree add ../app-feature-a -b feature/a
git worktree add ../app-bugfix-b  -b fix/b
# terminal 1:  cd ../app-feature-a && claude
# terminal 2:  cd ../app-bugfix-b  && claude
```

Each Claude session gets its own folder and branch, so they can't overwrite each other.
(Claude Code also has built-in worktree support for subagents. See the docs' "worktrees" page.)

---

## 4.12 Models, effort and cost

- **`/model`** switches models. Bigger models (the Opus family) handle complex reasoning
  better. Smaller ones (Sonnet, Haiku families) are faster and cheaper. Defaults depend on your plan.
- **`/effort`** trades thinking time for quality.
- Check usage with **`/usage`** (subscription limits) or **`/cost`** (API spend), depending on how you log in.

| Task | Suggestion |
|------|-----------|
| Explain code, rename, small fix | Default/smaller model, low effort |
| Multi-file feature | Default model, plan mode first |
| Gnarly bug, architecture decision | Strongest model, higher effort |

**Cost-savers:** `/clear` between tasks, `@`-mention the exact files, put stable info in
`CLAUDE.md`, and don't let a confused conversation drag on. Restart with a better prompt.

---

## 4.13 Windows-specific notes

You're on Windows, so these matter:

| Topic | Note |
|-------|------|
| Shell | Claude Code runs natively on Windows. It uses **Git Bash** (from Git for Windows) or **PowerShell** for commands. Install Git for Windows first |
| **Sandbox** | The Bash sandbox runs on **macOS, Linux and WSL2 only**. *"On native Windows, Claude Code runs commands unsandboxed."* For sandboxing, run Claude Code inside **WSL2** |
| Paths | Permission rules use forward-slash style paths. Test your rules with `/permissions` |
| Line endings | Scripts the agent writes may get CRLF line endings. Use `.gitattributes` (`*.sh text eol=lf`) |
| Home folder | `~/.claude/` = `C:\Users\<you>\.claude\` |

> 🧭 **Recommended Windows setup for safety:** install WSL2 (Ubuntu), clone repos **inside**
> the Linux filesystem (`~/code/...`, not `/mnt/c/...`, which is much faster too), and run
> `claude` (and `agy`) there with the sandbox on. Use VS Code's "WSL" remote mode for the GUI.

---

## 4.14 Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| Asked to approve the same command repeatedly | No allow rule; or the command differs slightly each time | Add a scoped allow rule, e.g. `Bash(npm run test *)` (Chapter 05) |
| Claude "forgot" what we agreed an hour ago | Context was compacted | Put durable decisions in `CLAUDE.md`; `/clear` + summary for new phases |
| Rewind didn't restore a deleted file | It was deleted by a shell command, not the edit tool | Restore from Git; work in branches |
| Claude edited files in plan mode? | Plan mode allows reading/exploring; edits happen after you approve the plan | Read what you're approving; stay in plan mode until happy |
| `claude: command not found` | PATH not updated | Open a new terminal; run the installer again; `claude doctor` |
| Sandbox options missing on Windows | Native Windows has no sandbox | Use WSL2 |
| Instructions in CLAUDE.md ignored | Too long / vague / contradictory | Shorter, specific rules; use hooks for must-never rules (Chapter 05) |

---

**Next:** [05 — Claude Code Customization ➡️](05-claude-code-customization.md)
