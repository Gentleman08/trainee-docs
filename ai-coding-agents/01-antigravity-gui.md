# 01 — Google Antigravity: App & IDE (GUI)

[⬅️ Back to Index](README.md) · [⬅️ Previous: Fundamentals](00-fundamentals.md)

---

> **Antigravity** is Google's "agent-first" development platform. This chapter covers the
> **graphical** parts: the desktop **Antigravity App** (where you manage agents, projects and
> conversations) and the **Antigravity IDE** (a full code editor with an agent side panel).
> The terminal version (`agy`) is in [Chapter 02](02-antigravity-cli.md). Rules, skills, hooks
> and MCP are in [Chapter 03](03-antigravity-customization.md).

> 📝 **Versions:** written against the official docs at antigravity.google/docs as of
> October 2026. Antigravity changes fast, so menu labels may differ slightly in your version.
> When in doubt, check the in-app Settings and the docs.

---

## Table of Contents

- [1.1 The Antigravity family at a glance](#11-the-antigravity-family-at-a-glance)
- [1.2 Install & sign in](#12-install-and-sign-in)
- [1.3 Tour of the App: projects, Agent Manager, editor](#13-tour-of-the-app)
- [1.4 Local mode vs worktree mode](#14-local-mode-vs-worktree-mode)
- [1.5 Artifacts: plans, walkthroughs, screenshots](#15-artifacts)
- [1.6 Permission presets (App, macOS/Linux)](#16-permission-presets-app-macoslinux)
- [1.7 Permission settings on Windows](#17-permission-settings-on-windows)
- [1.8 Writing allow / ask / deny rules](#18-writing-allow--ask--deny-rules)
- [1.9 IDE settings: auto-execution, strict mode, sandbox](#19-ide-settings)
- [1.10 The built-in browser safely](#110-the-built-in-browser-safely)
- [1.11 Models, effort and quota](#111-models-effort-and-quota)
- [1.12 Recommended setups (beginner → advanced)](#112-recommended-setups)
- [1.13 Efficient daily workflow in the GUI](#113-efficient-daily-workflow)
- [1.14 Gotchas](#114-gotchas)

---

## 1.1 The Antigravity family at a glance

| Surface | What it is | Use it for |
|---------|-----------|-----------|
| **Antigravity App** | Desktop "mission control" for agents: projects, conversations, Agent Manager, artifacts, browser | Running and supervising one or many agents |
| **Antigravity IDE** | A code editor (VS Code-style) with an agent side panel, tab completion and review-changes editor | Working on code yourself *with* an agent beside you |
| **IDE extensions** | Antigravity agent inside VS Code, Visual Studio, JetBrains, Zed, Xcode | Keeping your existing editor |
| **Antigravity CLI (`agy`)** | Terminal agent | Speed, SSH, automation (Chapter 02) |
| **Antigravity SDK** | Build your own agents on the same harness | Advanced/developers |

All surfaces share the same customization files (`AGENTS.md`, `.agents/skills/`, `.agents/hooks.json`,
MCP config), so what you set up once works everywhere.

---

## 1.2 Install and sign in

**App:** download from `antigravity.google/download`.

| OS | Install |
|----|---------|
| Windows 10 (64-bit) / 11 | Run the `.exe` installer (x64 or ARM64) |
| macOS 12+ | Open `Antigravity.dmg`, drag **Antigravity** into **Applications** |
| Linux (x64/ARM64) | `tar -xzf Antigravity.tar.gz` then `./Antigravity` |

**Sign in:**

- **Personal Google account** — click **Sign in** and finish in the browser (Free, Pro or Ultra plans).
- **Work account** — choose **Business account** → **Continue with Google Cloud** (or advanced
  Workforce Identity Federation), then pick your license/project.

> ⚠️ **Privacy check on day one:** Settings → Account has an **Enable Telemetry** toggle
> (sharing interaction logs). For company code, follow your employer's policy, and use a
> business/enterprise account if your company provides one.

---

## 1.3 Tour of the App

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Top bar:  [Agent Manager]   project / workspace switcher   [Open Editor]│
├──────────────┬──────────────────────────────────────────────────────────┤
│ Sidebar      │  Conversation with the agent                            │
│  + New       │   ├── your prompt                                       │
│    Project   │   ├── agent's thinking / plan                           │
│  Projects    │   ├── tool calls (files read, commands run) ← approvals │
│   └ convos   │   └── artifacts (plan, walkthrough, screenshots)        │
│  Settings    │  ┌──────────────────────────────────────────────┐       │
│              │  │ Prompt box  (type @ for files, / for commands)│       │
└──────────────┴──┴──────────────────────────────────────────────┴───────┘
```

**Key concepts:**

- **Project** — a set of folders (one repo, or e.g. frontend + backend) that defines **what the
  agent can see** and **its permissions**. Create one with the *New Project* icon (folder with
  a plus) → **Add Folder** → **Create**.
- **Conversation** — one task/chat with an agent inside a project. Keep one task per conversation.
- **Standalone conversation** — a chat outside any project, with its own terminal, file-access
  and permission settings.
- **Agent Manager** — overview of all running agents and workspaces. Toggle it with
  **Cmd+E / Ctrl+E**. Use it to supervise several agents working in parallel.
- **Editor** — open a workspace in the full editor from the Agent Manager ("Focus Editor" / "Open Editor").

**Handy shortcuts (from the docs):** `Ctrl+K` switch conversations, `Ctrl+P` search files,
`Tab` inspect diffs/tool details, `Esc` close review panel, `Ctrl+C` stop the agent.

---

## 1.4 Local mode vs worktree mode

When you start a conversation, you choose how the agent touches your folders:

| Mode | What happens | Use when |
|------|-------------|----------|
| **Local mode** | Agent edits your folders **directly** | Small, quick, interactive changes you're watching |
| **New worktree mode** | Agent works in a **separate Git worktree** (its own copy and branch); your folder stays untouched | Bigger or riskier changes, experiments, or **several agents at once** |

> 🛡️ **Safety tip:** for anything bigger than a one-line fix, use **worktree mode**. If the
> result is bad, you delete the worktree and nothing in your main folder changed. If it's
> good, you merge the branch.

> Worktree mode only applies to **Git** folders. Non-Git folders in a project are always used directly.

---

## 1.5 Artifacts

Instead of a wall of chat text, Antigravity agents produce **artifacts**: structured documents
you can review and comment on.

| Artifact | What it is | Why it matters to you |
|----------|-----------|----------------------|
| **Implementation plan** | Which files will change and how, before code is written | **Your best checkpoint.** Catch misunderstandings before any code changes |
| **Task groups** | How the agent organised the work | Track progress |
| **Walkthrough** | Summary of what was done and how it was verified | Faster review |
| **Screenshots / browser recordings** | Visual proof of UI changes, recorded by the browser agent | Check UI work without running it yourself |

**Artifact review policy** (App: Settings → **Agent** tab):

| Option | Behaviour | Recommendation |
|--------|-----------|----------------|
| **Request review** | Agent **halts** after producing a plan/diff and waits for your approval. You can add **inline comments** | ✅ **Beginners: always use this** |
| **Always proceed** | Agent never pauses for review | Only for trusted, low-risk work |

**How to review a plan well:**

1. Does it touch **only** the files you expected?
2. Does it delete or change **tests**? (Red flag unless you asked for that.)
3. Does it add **new dependencies/packages**? Ask why.
4. Leave inline comments ("Don't change the DB schema; use the existing column"), then approve.

---

## 1.6 Permission presets (App, macOS/Linux)

Antigravity checks every sensitive action (running a command, writing a file, opening a URL,
calling an MCP tool) against your **preset** plus your **rules**.

Configure globally under **Settings → General → Permission Settings**, and per project under
**Settings → Projects** (new projects use **Inherit General**).

| Preset | Sandbox | Terminal commands | File access | MCP & web |
|--------|---------|-------------------|-------------|-----------|
| **Default** | ✅ On | Run freely **inside the sandbox**; ask if they need to run outside it | Workspace + temp dirs | Ask |
| **Request Review** | ❌ Off | **Always ask** | Workspace only | Ask |
| **Turbo** | ❌ Off | Run **without asking** (unrestricted) | **Full filesystem** | Allowed |

**Which preset should you use?**

```
 Total beginner, real projects ─────────► Request Review  (see and approve everything)
 Comfortable, want fewer prompts ───────► Default         (sandbox does the protecting)
 Disposable VM/container, demo repo ────► Turbo           (NEVER on your main machine)
```

> ⚠️ **Turbo gives the agent full filesystem access with no prompts.** One misunderstood
> instruction or one prompt injection from a web page can delete or leak anything your user
> account can touch.

---

## 1.7 Permission settings on Windows

> 💡 You're on Windows. Per the docs, the **new permission system (presets + full rule
> engine) is macOS/Linux first**, and Windows still uses the earlier system (to be updated).
> On Windows the App offers:

| Setting (project or General → Agent Settings) | Options | Recommended |
|------------------------------------------------|---------|-------------|
| **Terminal execution policy / Terminal Command Auto Execution** | e.g. Request Review / Proceed in Sandbox / Always Proceed (labels may vary) | **Request Review** (or Proceed in Sandbox once the sandbox works for you) |
| **Outside of folder file access policy** | **Always Allow**, **Always Ask**, **Always Deny** | **Always Ask** or **Always Deny** |
| **Sandbox mode** / **Enable Sandbox Mode (Preview)** | On / Off | Try **On** (preview). Enabling it switches the preset to *Custom* |

On Windows, commands default to **Ask**, and allow rules for commands that should run outside
the sandbox use the `unsandboxed(...)` form, e.g. `unsandboxed(git push)`. Windows paths are
normalised (drive letter stripped, `\` → `/`) before rules are checked.

> 🧭 **Strong recommendation for Windows users who want maximum safety:** run agents inside
> **WSL2** (Linux on Windows) or a dev container. Linux gets the full sandbox and rule engine
> for both Antigravity and Claude Code.

---

## 1.8 Writing allow / ask / deny rules

Every action is a **permission resource** written as `action(target)`:

| Action | Examples | Meaning |
|--------|----------|---------|
| `command` | `command(git)`, `command(npm test)`, `command(regex:npm run (build\|lint\|test))`, `command(*)` | Terminal commands (matched by word prefix) |
| `read_file` | `read_file(/var/log/app)`, `read_file(docs/)` | Read a file or folder (recursive) |
| `write_file` | `write_file(src/)`, `write_file(*)` | Write (also implies read) |
| `read_url` | `read_url(github.com)` | Fetch a website (covers subdomains) |
| `execute_url` | `execute_url(localhost)` | Click/type on a website in the browser |
| `mcp` | `mcp(github/*)`, `mcp(sql/execute_mutation)` | Call MCP tools |
| `unsandboxed` | `unsandboxed(git push)` | Run a command **outside** the sandbox (CLI & Windows) |

**Precedence:** **Deny > Ask > Allow**. If `command(*)` is in *Ask*, it beats `command(git)`
in *Allow*, so everything asks.

**A safe starter rule set** (enter these in Settings → Permission Settings / project permissions):

```text
ALLOW
command(git status)
command(git diff)
command(git log)
command(regex:npm run (build|lint|test))
command(ls)
write_file(src/)
write_file(tests/)

ASK
command(*)
mcp(*)
read_url(*)

DENY
command(rm -rf)
command(sudo)
command(git push --force)
command(git reset --hard)
command(terraform apply)
command(kubectl delete)
write_file(.git/)
read_file(.env)
read_file(~/.ssh)
read_file(~/.aws)
```

**Shell tricks disable prefix matching.** If a command contains `$(...)`, backticks, brace
expansion or redirections (`>`), a prefix rule like `command(git)` **won't** auto-allow it. It
then needs an exact match, or it prompts. Pipes `|` and `&&` chains still match by prefix.
Example: with `command(git)` allowed, `git status && git log` runs, but `git log $(whoami)` prompts.

**Implicit rules:** allowing `write_file(x)` also allows reading `x`; denying `read_file(x)` also denies writing it.

**When a prompt appears** for a file/URL/MCP action, you can **widen the scope** before
allowing (e.g. `/project/file.txt` → `/project`) for the rest of that turn. Do this
deliberately, not by reflex.

---

## 1.9 IDE settings

The standalone **Antigravity IDE** exposes similar controls in its settings:

| Setting | Options | Beginner choice |
|---------|---------|-----------------|
| **Terminal command auto execution** | **Request Review** (asks except allowlisted commands) / **Always Proceed** (runs except denylisted commands) | **Request Review** + a small allowlist (`git status`, `npm test`) |
| **Agent non-workspace file access** | Off (default) / On | **Off**. The agent can then only reach project folders and `~/.gemini/antigravity-ide/` |
| **Strict mode** | On / Off | **On** for sensitive repos |
| **Enable Terminal Sandboxing** | Off (default) / On (macOS Seatbelt, Linux nsjail) | **On** where available |
| **Sandbox Allow Network** | On / Off | **Off** unless a task needs downloads |

**What Strict mode does (all at once):**

- Terminal auto-execution → **Request Review**, and the **terminal allowlist is ignored**.
- Browser JavaScript execution → **Request Review**.
- Artifact review → **Request Review**.
- Agent **respects `.gitignore`** (ignored files like `.env` are off-limits).
- **Workspace isolation**: no access to files outside the workspace.
- Browser URL allow/deny lists govern external images and the Read URL tool.
- The terminal sandbox is turned on **with network denied**.

> 🧭 **Strict mode is the "seatbelt" switch.** Turn it on for client code, repos with secrets,
> or whenever you're unsure.

---

## 1.10 The built-in browser safely

Antigravity agents can drive a real browser (via Chrome) to test web apps, take screenshots
and record videos. This is powerful, and it's also the biggest **prompt-injection** surface.

| Control | What it does |
|---------|-------------|
| **Denylist** (server-side, Google-maintained) | Blocks known-dangerous URLs. If the check service is unreachable, access is **denied** by default |
| **Allowlist** (local file) | Starts with only `localhost`. Visiting another URL prompts **Always allow**, which adds it |
| Precedence | Denylist always wins |
| **Browser JavaScript execution policy** | Set to **Request Review** (strict mode does this) |
| **Separate Chrome profile** | Run the agent's browser in a profile **not logged in** to your email, bank or cloud consoles |

> ⚠️ **Never** let the agent browse while logged in to production consoles or your personal
> accounts. A malicious page could instruct the agent to act with your session.

---

## 1.11 Models, effort and quota

- Pick the model per conversation. Antigravity offers Gemini models (Pro = strongest; Flash =
  fast/cheap) and some partner/open models; the docs list Claude and GPT-OSS options too.
- **Fast vs planning:** for tiny edits use fast mode; for multi-file work, use planning (it
  produces the implementation plan artifact).
- **Effort level** (low → max) trades thinking time for quality.
- Check usage with **`/usage`** (also in the CLI). Heavy autonomous runs burn quota quickly.

| Task | Model / mode suggestion |
|------|------------------------|
| Explain code, small fix, rename | Flash / fast mode |
| Feature across several files | Pro / planning mode, Request review on |
| Big refactor, unfamiliar codebase | Pro, high effort, worktree mode, plan first |

---

## 1.12 Recommended setups

### 🟢 Level 1 — "Training wheels" (first weeks)

- Preset: **Request Review** (Windows: terminal policy *Request Review*, outside-folder access *Always Ask*)
- **Strict mode: On**
- Artifact review: **Request review**
- Conversation mode: **Local** for tiny things, **worktree** for everything else
- Rules: the safe starter set from §1.8 (deny secrets and destructive commands)

### 🟡 Level 2 — "Productive & safe" (comfortable users, macOS/Linux/WSL)

- Preset: **Default** (sandbox on, commands auto-run inside the sandbox)
- Allow rules for your project's routine commands (`npm run test`, `pytest`, `go test ./...`)
- Deny list kept from Level 1
- Artifact review: Request review for features; you may relax it for docs-only work
- Hooks for linting after edits (Chapter 03)

### 🔴 Level 3 — "Autopilot" (only in disposable environments)

- Preset: **Turbo**, inside a **VM, cloud workstation or dev container** with **no
  production credentials** and only a copy of the code
- Use worktrees and let multiple agents run in parallel
- Still review the final diff before merging

---

## 1.13 Efficient daily workflow

```
 1. git pull && git status (clean)          → start from a known state
 2. New conversation, WORKTREE mode         → isolate the work
 3. Prompt: Goal / Context / Constraints / Verify   (see Chapter 00 §0.10)
 4. Read the IMPLEMENTATION PLAN, comment, approve
 5. Watch tool calls; approve/deny prompts thoughtfully
 6. Read the WALKTHROUGH + review-changes diff
 7. Run tests yourself (or ask the agent to show output)
 8. Commit / merge the worktree branch; archive the conversation
```

**Efficiency tips:**

- **One task = one conversation.** Long conversations drift and cost more.
- Put repeated instructions in **`AGENTS.md`** (Chapter 03) instead of retyping them.
- Turn repeated multi-step procedures into **skills** (`/release-notes`, `/add-endpoint`).
- Use **`@file`** mentions so the agent doesn't have to search.
- Paste **screenshots** for UI bugs (`Ctrl+V` in the prompt box).
- Run **parallel agents** in separate worktrees for independent tasks, and supervise them in the Agent Manager.

---

## 1.14 Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| Agent keeps asking for every command | Request Review preset / strict mode (by design) | Add specific **allow** rules for safe routine commands |
| Allow rule doesn't work for a command | Command contains `$()`, backticks, `>` or brace expansion, so prefix matching is disabled | Simplify the command, add an exact rule, or approve manually |
| Allowlisted command still prompts | **Strict mode ignores the terminal allowlist** | Expected; turn strict mode off for that project if appropriate |
| `npm install` fails inside the sandbox | Sandbox blocks network by default | Allow the domain (`read_url(registry.npmjs.org)`), or approve that one command outside the sandbox |
| Docker commands fail | Docker can't run inside the sandbox | Needs an `unsandboxed`/`command` allow rule; approve deliberately |
| Agent can't see a file you mentioned | File is outside the project, or in `.gitignore` under strict mode | Add the folder to the project; or move the info into a non-ignored file |
| Changes appeared in your main folder unexpectedly | Conversation was started in **Local mode** | Use **New worktree mode** for non-trivial tasks |
| Windows: sandbox/rules behave differently from the docs | Windows uses the older permission system | Use WSL2, or follow the Windows settings in §1.7 |

---

**Next:** [02 — Antigravity CLI (`agy`) ➡️](02-antigravity-cli.md)
