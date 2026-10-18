# 05 — Claude Code Customization: Settings, Permissions, Memory, Skills, Subagents, Hooks, MCP, Sandbox

[⬅️ Back to Index](README.md) · [⬅️ Previous: Claude Code Basics](04-claude-code-basics.md)

---

> Everything here is a **file** you can version, review and share. Learn which file does what,
> and you can make Claude Code safe *and* fast for you and your team.

> 📝 Based on code.claude.com/docs, October 2026. Run `claude doctor` / `/doctor` to see which
> settings are actually in effect and whether any are invalid.

---

## Table of Contents

- [5.1 Where configuration lives (and who wins)](#51-where-configuration-lives)
- [5.2 Permission rules](#52-permission-rules)
- [5.3 CLAUDE.md memory & `.claude/rules/`](#53-claudemd-memory-and-rules)
- [5.4 Skills (and old custom commands)](#54-skills)
- [5.5 Subagents](#55-subagents)
- [5.6 Hooks](#56-hooks)
- [5.7 MCP servers](#57-mcp-servers)
- [5.8 Plugins & marketplaces](#58-plugins-and-marketplaces)
- [5.9 Personalisation: status line, output style, keybindings, theme](#59-personalisation)
- [5.10 The Bash sandbox](#510-the-bash-sandbox)
- [5.11 Headless mode, scripting & CI](#511-headless-mode-scripting-and-ci)
- [5.12 Recommended configurations (copy-paste)](#512-recommended-configurations)
- [5.13 Gotchas](#513-gotchas)

---

## 5.1 Where configuration lives

```
~/.claude/                         ← YOU, every project
├── settings.json                  ← personal settings
├── CLAUDE.md                      ← personal instructions
├── rules/*.md                     ← personal modular rules
├── skills/<name>/SKILL.md         ← personal skills
├── agents/<name>.md               ← personal subagents
└── keybindings.json

your-repo/                         ← TEAM (commit these)
├── CLAUDE.md                      ← project instructions (or .claude/CLAUDE.md)
├── .mcp.json                      ← project MCP servers
└── .claude/
    ├── settings.json              ← shared project settings
    ├── settings.local.json        ← YOUR personal overrides for this repo (git-ignored)
    ├── rules/*.md                 ← modular/path-scoped rules
    ├── skills/<name>/SKILL.md     ← project skills
    ├── agents/<name>.md           ← project subagents
    └── hooks/                     ← (convention) hook scripts
CLAUDE.local.md                    ← YOUR private notes for this repo (add to .gitignore)
```

**Settings precedence (highest wins):**

| # | Level | File | Who |
|---|-------|------|-----|
| 1 | **Managed** | `managed-settings.json`, MDM, or claude.ai console | Your organisation (can't be overridden) |
| 2 | Command line | `claude --settings '…'` / flags | You, this session |
| 3 | Project local | `.claude/settings.local.json` | You, this repo |
| 4 | Shared project | `.claude/settings.json` | Everyone in the repo |
| 5 | User | `~/.claude/settings.json` | You, all repos |

> Permission rules **merge** across levels, and **deny beats allow** wherever it comes from. So a
> team can ship a deny list in `.claude/settings.json` that individuals can't loosen by accident.

**A typical `settings.json` shape:**

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "default",
    "allow": [],
    "ask": [],
    "deny": [],
    "additionalDirectories": []
  },
  "env": { "NODE_ENV": "development" },
  "hooks": {},
  "sandbox": { "enabled": false },
  "statusLine": { "type": "command", "command": "~/.claude/statusline.sh" }
}
```

> 💡 The `$schema` line gives you **autocomplete and validation** in VS Code, which catches typos
> before they silently do nothing.

---

## 5.2 Permission rules

### Syntax

`Tool` or `Tool(specifier)`:

| Rule | Matches |
|------|---------|
| `Bash` | All shell commands |
| `Bash(npm run build)` | Exactly `npm run build` |
| `Bash(npm run test *)` | `npm run test` followed by anything |
| `Bash(git log *)` | Any `git log …` (but not other git subcommands) |
| `Bash(git *)` | **Every** git command, including `push` and `reset`. Usually too broad |
| `Read(./.env)` | Reading `.env` in the project root |
| `Read(./secrets/**)` | Anything under `secrets/` |
| `Read(~/.ssh/**)` | Your SSH keys |
| `Edit(./src/**)` | Editing files under `src/` |
| `WebFetch(domain:docs.python.org)` | Fetching that domain |
| `mcp__github` | All tools of the `github` MCP server |
| `mcp__github__get_issue` | One MCP tool |
| `Agent(model:opus)` | Parameter match (deny/ask rules), e.g. subagents requesting Opus |

**Rules of thumb (from the docs):**

- Put the `*` **after the subcommand**: `Bash(git log *)`, not `Bash(git *)`. Claude Code warns
  about wildcards placed before the subcommand.
- **Precedence: deny > ask > allow.**
- A **deny** rule on a bare tool (`WebFetch`, or `Bash(*)`) removes that tool entirely.

### A safe project permission set (`.claude/settings.json`)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Bash(npm run build)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(npm install *)",
      "Bash(docker *)",
      "WebFetch"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(git push --force *)",
      "Bash(git reset --hard *)",
      "Bash(terraform apply *)",
      "Bash(kubectl delete *)",
      "Bash(curl * | sh)",
      "Bash(curl * | bash)"
    ]
  }
}
```

> ⚠️ **Deny rules on Bash are pattern-based, not a perfect wall.** Commands can be written many
> ways (`rm -r -f`, a script that deletes files, `find -delete`). For strong guarantees, combine
> deny rules with the **sandbox** (§5.10) and a **PreToolUse hook** (§5.6).

### Other useful permission settings

```json
{
  "permissions": {
    "defaultMode": "plan",
    "additionalDirectories": ["../shared-lib"],
    "disableBypassPermissionsMode": "disable"
  }
}
```

- `defaultMode`: the mode sessions start in (`default`, `acceptEdits`, `plan`, `auto`, …).
- `additionalDirectories`: extra folders Claude may access (same as `/add-dir`).
- `disableBypassPermissionsMode` / `disableAutoMode`: `"disable"` prevents those modes. Great
  in your **user** settings as a personal seatbelt, and standard in company **managed** settings.

Manage interactively with **`/permissions`**.

---

## 5.3 CLAUDE.md memory and rules

### The memory files

| Level | File | Shared? |
|-------|------|---------|
| Organisation (managed) | Windows `C:\Program Files\ClaudeCode\CLAUDE.md` · Linux/WSL `/etc/claude-code/CLAUDE.md` · macOS `/Library/Application Support/ClaudeCode/CLAUDE.md` | Everyone (IT-deployed) |
| You, all projects | `~/.claude/CLAUDE.md` | Only you |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` (Claude also reads `AGENTS.md`) | Team via Git |
| You, this project | `./CLAUDE.local.md` (add to `.gitignore`) | Only you |

- Files from the working directory **and every parent directory** load at start. Files in
  **subdirectories** load when Claude works with files there.
- They're **concatenated**, not overridden. Keep them consistent (contradictions confuse the model).
- **Imports:** `@path/to/file.md` inside CLAUDE.md pulls in another file.
- `/init` creates a starter CLAUDE.md. `/memory` opens your memory files for editing.

### Example project `CLAUDE.md`

```markdown
# Orders API — notes for Claude

## Stack & commands
- Node 22, TypeScript, Express, Prisma (Postgres), Vitest.
- Install `npm ci` · Test `npm test` · Lint `npm run lint` · Typecheck `npm run typecheck`.
- Before saying a task is done: run lint, typecheck and tests, and show the result.

## Layout
- `src/routes/` HTTP handlers · `src/services/` business logic · `tests/` mirrors `src/`.
- See @docs/architecture.md for the big picture.

## Rules
- Never read or modify `.env*` or `secrets/`.
- Never delete/skip/weaken tests to make them pass. Fix the code.
- Don't add dependencies without asking.
- Don't run database migrations or `git push`.
- Ask before changing public API response shapes.

## Communication
- I'm new to programming: explain changes in plain English, briefly.
```

### Personal `~/.claude/CLAUDE.md` example

```markdown
- I'm on Windows 11 with PowerShell; prefer cross-platform commands.
- Explain technical terms the first time you use them.
- Before large changes, show a plan and wait for my OK.
- Never commit or push unless I explicitly ask.
```

### Modular & path-scoped rules: `.claude/rules/`

Put topic files in `.claude/rules/` (discovered **recursively**, so subfolders are fine). Add
`paths:` frontmatter so a rule only loads when Claude works on matching files:

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API rules
- Validate every request body with zod schemas in src/api/schemas/.
- Return errors as { error: { code, message } }.
```

Personal rules for all projects go in `~/.claude/rules/`.

### Auto memory

Claude Code can also keep **its own notes** (learnings and corrections you gave it) per
repository, loaded each session (first ~200 lines / 25 KB). CLAUDE.md is for **instructions
you write**. Auto memory is for **things Claude picks up**. Review it occasionally.

> 🧠 **Memory ≠ enforcement.** The docs say these files are context, *not enforced
> configuration*: "To block an action regardless of what Claude decides, use a PreToolUse hook."

---

## 5.4 Skills

A **skill** is a folder with a `SKILL.md`. Claude loads it **automatically** when your request
matches its description, or you run it as **`/skill-name`**.

| Location | Path | Available |
|----------|------|-----------|
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This repo (commit it) |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | As `/plugin-name:skill-name` |

> **Custom commands were merged into skills.** An old `.claude/commands/deploy.md` and a new
> `.claude/skills/deploy/SKILL.md` both create `/deploy`, and old command files keep working.

### Frontmatter fields

| Field | Purpose |
|-------|---------|
| `name` | The `/name` (defaults to folder name) |
| `description` | **What + when**: Claude uses it to decide when to load the skill |
| `when_to_use` | Extra trigger phrases/examples |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `disable-model-invocation: true` | Only **you** can run it (manual `/name`). ✅ Use for anything with side effects |
| `user-invocable: false` | Only Claude can use it (hidden from `/` menu) |
| `allowed-tools` | Tools pre-approved **while this skill runs** (keep minimal!) |
| `model`, `effort` | Override model/effort for this skill |
| `context: fork` (+ `agent`) | Run in a separate subagent context |
| `paths` | Globs limiting when it auto-activates |

`$ARGUMENTS` is replaced with whatever you type after the command (`$1`, `$2`… for individual arguments).

### Example 1 — fix a GitHub issue (manual only)

`.claude/skills/fix-issue/SKILL.md`:

```markdown
---
name: fix-issue
description: Fix a GitHub issue by number following our standards
argument-hint: "[issue-number]"
disable-model-invocation: true
allowed-tools: Bash(gh issue view *) Read Grep
---

Fix GitHub issue $ARGUMENTS.

1. `gh issue view $ARGUMENTS` and summarise the problem in 2 lines.
2. Find the relevant code; propose a plan and WAIT for my approval.
3. Write a failing test that reproduces the issue.
4. Fix the code until the test passes; run the full test suite.
5. Show me `git diff`. Do not commit or push.
```

Run: `/fix-issue 123`

### Example 2 — commit message helper

`.claude/skills/commit-msg/SKILL.md`:

```markdown
---
name: commit-msg
description: Writes a Conventional Commits message for the staged changes. Use when the user asks for a commit message.
allowed-tools: Bash(git diff --cached *) Bash(git diff --cached)
---
Run `git diff --cached`. Write ONE commit message:
- first line `type(scope): summary` (≤ 72 chars; types: feat, fix, docs, refactor, test, chore, ci)
- blank line, then 1–3 bullet points on WHY.
Print the message only. Do not run git commit.
```

### Example 3 — beginner explainer (personal)

`~/.claude/skills/explain-simply/SKILL.md`: same idea as the Antigravity example in
[Chapter 03 §3.4](03-antigravity-customization.md#34-skills). The **Agent Skills format is shared**,
so the same `SKILL.md` folder works in both tools (only the folder location differs:
`.claude/skills/` vs `.agents/skills/`).

---

## 5.5 Subagents

Subagents are specialists with **their own context window, tools, model and instructions**.
Use them to keep your main conversation clean (e.g. "investigate these 40 files and report back")
or to enforce limits (a read-only reviewer).

| Location | Path |
|----------|------|
| Project | `.claude/agents/<name>.md` |
| Personal | `~/.claude/agents/<name>.md` |
| Plugin | `<plugin>/agents/` |

Create them interactively with **`/agents`** (recommended: it helps you pick tools), or write
the file:

`.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Reviews recent changes for bugs, security issues and readability. Use proactively after code changes, or when the user asks for a review.
tools: Read, Grep, Glob, Bash
model: inherit
---
You are a senior code reviewer.
1. Run `git diff` to see recent changes.
2. Report findings grouped as: Critical (must fix), Warnings, Suggestions, each with file:line.
3. Check: correctness, error handling, security (injection, secrets, auth), tests present.
Do NOT edit files. Be concise.
```

Use it: *"Use the code-reviewer subagent on my changes."* Claude may also delegate on its own
when the description matches.

> 🛡️ **Least privilege:** give subagents only the tools they need. A reviewer doesn't need
> `Edit` or `Write`. Leaving `tools` out entirely means the subagent inherits all tools.

---

## 5.6 Hooks

Hooks are **your scripts**, run automatically at lifecycle events. They're the way to
**enforce** policy and **automate** chores. They live under `"hooks"` in any settings file.

### The events you'll actually use first

| Event | Fires | Typical use |
|-------|-------|-------------|
| `PreToolUse` | Before a tool runs, **can block** | Block dangerous commands, protect files |
| `PostToolUse` | After a tool succeeds | Auto-format/lint edited files |
| `UserPromptSubmit` | When you send a prompt | Add context, block prompts containing secrets |
| `Notification` | When Claude needs your attention | Desktop notification / sound |
| `Stop` | When Claude finishes responding | Run tests, nudge Claude to continue |
| `SessionStart` | Session begins/resumes | Load context (current branch, open tickets) |

There are many more (`PermissionRequest`, `SubagentStop`, `PreCompact`, `SessionEnd`,
`ConfigChange`, `FileChanged`, …). See the hooks reference.

### How a command hook talks back

- Receives the event as **JSON on stdin** (e.g. `tool_name`, `tool_input.command`).
- **Exit 0** = OK (you may print JSON for structured decisions).
- **Exit 2** = **block**. Your stderr text is shown to Claude as the reason.
- Other exit codes = non-blocking error (the action continues).
- Structured `PreToolUse` decision (exit 0 + JSON):

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook"
  }
}
```

`permissionDecision` can be `allow`, `deny`, `ask` or `defer`.

### Example 1 — block destructive Bash commands

`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_dangerous.py\"" }
        ]
      }
    ]
  }
}
```

`.claude/hooks/block_dangerous.py`:

```python
#!/usr/bin/env python3
import json, re, sys

data = json.load(sys.stdin)
cmd = data.get("tool_input", {}).get("command", "")

BLOCK = [r"\brm\s+-[a-z]*r[a-z]*f?\s+(/|~|\*|\.\s*$)", r"git\s+push\s+.*(--force|-f\b)",
         r"git\s+reset\s+--hard", r"\bsudo\b", r"terraform\s+(apply|destroy)",
         r"kubectl\s+delete", r"(curl|wget)[^|]*\|\s*(ba|z)?sh", r"\.env\b"]

for pattern in BLOCK:
    if re.search(pattern, cmd):
        print(f"Blocked by project policy (pattern: {pattern}). Ask the user to run it manually if really needed.",
              file=sys.stderr)
        sys.exit(2)      # exit 2 = block, stderr goes to Claude
sys.exit(0)
```

### Example 2 — auto-format after edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "npx prettier --write \"$(jq -r '.tool_input.file_path')\" 2>/dev/null || true" }
        ]
      }
    ]
  }
}
```

### Example 3 — desktop notification when Claude needs you (Windows PowerShell)

```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          { "type": "command", "command": "powershell -NoProfile -Command \"[console]::beep(880,300)\"" }
        ]
      }
    ]
  }
}
```

### Example 4 — protect specific files from edits

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | grep -Eq '(package-lock\\.json|\\.github/workflows/|migrations/)' && { echo 'Protected file: ask the user' >&2; exit 2; } || exit 0"
          }
        ]
      }
    ]
  }
}
```

**Hook safety (from the docs):**

- *"Use the permission system rather than a hook to enforce a hard allow or deny"* where
  possible. Hooks are an extra layer. A timed-out hook doesn't block by default.
- Hooks run **with your full user permissions**. Read hooks in any repo before trusting it.
- Print **only** JSON on stdout when returning JSON (shell profile echoes break parsing).
- `${CLAUDE_PROJECT_DIR}` keeps script paths working from any subfolder.
- View active hooks with **`/hooks`**. Organisations can restrict hooks to managed ones
  (`allowManagedHooksOnly`).

---

## 5.7 MCP servers

MCP connects Claude Code to external tools (GitHub, Jira, databases, browsers, docs).

```bash
# Remote (HTTP) server
claude mcp add --transport http github https://api.githubcopilot.com/mcp/

# Local (stdio) server: everything after -- is the command to run
claude mcp add my-sqlite -- npx -y some-sqlite-mcp-server --db ./dev.db --read-only

# Share with the team: writes to .mcp.json in the repo
claude mcp add --scope project --transport http docs https://example.com/mcp

claude mcp list                 # what's configured
claude mcp remove my-sqlite
```

Inside a session: **`/mcp`** shows server status and handles OAuth logins.

| Scope | Stored | Visible to |
|-------|--------|-----------|
| `local` (default) | Your user config, this project | Only you |
| `project` | `.mcp.json` in the repo | Everyone (they approve it on first use) |
| `user` | Your user config | You, all projects |

**Permissions for MCP tools:** `mcp__<server>__<tool>`, e.g. allow
`mcp__github__get_issue`, ask for `mcp__github__create_pull_request`, deny `mcp__db__execute_sql`.

> ⚠️ **MCP safety:** install only trusted servers. Prefer **read-only** credentials and
> non-production data. Never commit tokens in `.mcp.json` (use environment variables). Treat
> tool output (issue text, web content) as **untrusted**, because it can carry prompt injection.

> The URLs/package names above are **illustrative**. Use each server's official instructions.

---

## 5.8 Plugins and marketplaces

Plugins bundle **skills, subagents, hooks and MCP servers** for one-step install and team sharing.

```text
/plugin                                   ← browse & manage
/plugin marketplace add <owner/repo>      ← add a marketplace (a Git repo listing plugins)
/plugin install <plugin>@<marketplace>
```

Teams can pre-enable plugins and marketplaces in `.claude/settings.json` so everyone gets the
same toolkit.

> Plugins run code (hooks, MCP servers) on your machine. Use your company's approved
> marketplace, read what a plugin includes, and keep the list short.

---

## 5.9 Personalisation

| What | How |
|------|-----|
| **Status line** (model, branch, context %, cost) | `/statusline` (Claude can generate a script), or `"statusLine": {"type": "command", "command": "~/.claude/statusline.sh"}` |
| **Output style** (e.g. more explanatory, teaching-oriented answers) | `/config` → output style, or the `outputStyle` setting. Great for learners |
| **Theme** | `/config` |
| **Keybindings** | `/keybindings` or `~/.claude/keybindings.json` |
| **Environment variables for every session** | `"env": { "KEY": "value" }` in settings (**no secrets** in shared files) |
| **Default model** | `"model"` in settings or `/model` |
| **Commit attribution** | `attribution` / co-author settings (see settings reference) |

Example status line script (`~/.claude/statusline.sh`, Git Bash/WSL):

```bash
#!/usr/bin/env bash
input=$(cat)                                   # JSON about the session arrives on stdin
model=$(echo "$input" | jq -r '.model.display_name')
dir=$(echo "$input" | jq -r '.workspace.current_dir' | xargs basename)
branch=$(git -C "$(echo "$input" | jq -r '.workspace.current_dir')" branch --show-current 2>/dev/null)
echo "🤖 $model | 📁 $dir | 🌿 ${branch:-no-git}"
```

---

## 5.10 The Bash sandbox

The sandbox is an **OS-enforced boundary** around shell commands Claude runs (macOS, Linux,
**WSL2**; *not* native Windows). Inside it, commands can be **auto-approved**, because the OS
limits the damage they can do.

| | Default inside the sandbox | Configure with |
|---|---|---|
| **Writes** | Working dir, temp dir, added dirs only; protected paths stay denied | `sandbox.filesystem.allowWrite` / `denyWrite` |
| **Reads** | Most of the machine, **including** `~/.ssh`, `~/.aws/credentials` unless you deny them | `sandbox.filesystem.denyRead` / `allowRead` |
| **Network** | No direct access; a proxy allows only listed domains (starts **empty**) | `sandbox.network.allowedDomains` / `deniedDomains` |

**Turn it on:** run **`/sandbox`** (it also shows missing dependencies; Linux/WSL2 needs
`bubblewrap` and `socat`), or in settings:

```json
{
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyRead": ["~/.ssh", "~/.aws", "~/.config/gcloud", "~/.azure"],
      "allowWrite": ["~/.npm"]
    },
    "network": {
      "allowedDomains": ["registry.npmjs.org", "pypi.org", "files.pythonhosted.org", "github.com"]
    }
  }
}
```

- **The unsandboxed-retry escape hatch:** if a command fails in the sandbox, Claude may retry
  it **outside** the sandbox (`dangerouslyDisableSandbox`), which normally needs your approval.
  `"allowUnsandboxedCommands": false` disables that ("strict sandbox mode").
- `excludedCommands` lists commands that always run outside the sandbox (e.g. `docker`). Prefer
  `allowWrite` for specific paths over excluding whole tools.
- **The sandbox covers shell commands only.** Claude's Read/Edit/WebFetch tools, MCP servers
  and hooks follow **permission rules**, not sandbox settings. Keep your `Read(...)` deny rules too.

**Quick self-test** (from the docs' idea): ask Claude to run `touch ~/sandbox-probe`. Inside the
sandbox it should fail (`Operation not permitted` / `Read-only file system`). If it succeeds,
the sandbox isn't active. Delete the file and check `/sandbox`.

> 🧭 Want everything (file tools, MCP, hooks) inside one boundary? Run Claude Code itself in a
> **dev container or VM**. That's also the only place `bypassPermissions` is reasonable.

---

## 5.11 Headless mode, scripting and CI

```bash
# One-shot question
claude -p "Explain what src/index.ts does in 5 bullet points"

# JSON output for scripts
claude -p "List the TODO comments in src/" --output-format json | jq -r '.result'

# Pipe input in
git diff --cached | claude -p "Write a conventional commit message for this diff"

# Limit what it may do in automation
claude -p "Run the linter and fix lint errors only" \
  --allowedTools "Read,Edit,Bash(npm run lint *)" \
  --permission-mode acceptEdits
```

| Flag | Purpose |
|------|---------|
| `-p` / `--print` | Non-interactive: run and exit |
| `--output-format text\|json\|stream-json` | Output style |
| `--allowedTools` / `--disallowedTools` | Pre-approve / forbid tools for this run |
| `--permission-mode` | `plan`, `acceptEdits`, `dontAsk`, … |
| `--max-turns N` | Cap agent loop iterations (cost/safety) |
| `-c` / `-r` | Continue / resume sessions |
| `--settings '<json>'` | Extra settings for this run |
| `--append-system-prompt "…"` | Add standing instructions for this run |

**CI (GitHub Actions)** with the official action, e.g. to review PRs when someone comments `@claude`:

```yaml
name: Claude
on:
  issue_comment:
    types: [created]
permissions:
  contents: read
  pull-requests: write
  issues: write
jobs:
  claude:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

> 🛡️ **Automation safety:** use `dontAsk` or tight `--allowedTools`, a `--max-turns` cap, a
> runner with **no production credentials**, least-privilege `permissions:` in the workflow,
> and remember that **PR/issue text is untrusted input** (prompt injection). See the
> [CI/CD Pipelines guide, Chapter 05](../cicd-pipelines/05-devsecops.md) for pipeline hardening.

---

## 5.12 Recommended configurations

### 🟢 Beginner: `~/.claude/settings.json` (personal seatbelt)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "plan",
    "disableBypassPermissionsMode": "disable",
    "deny": [
      "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.azure/**)", "Read(~/.config/gcloud/**)",
      "Read(./.env)", "Read(./.env.*)",
      "Bash(rm -rf *)", "Bash(sudo *)",
      "Bash(git push --force *)", "Bash(git reset --hard *)"
    ],
    "ask": ["Bash(git push *)", "Bash(npm install *)", "Bash(pip install *)"]
  }
}
```

### 🟡 Team project: `.claude/settings.json` (committed)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)", "Bash(npm run typecheck)", "Bash(npm run test *)",
      "Bash(git status)", "Bash(git diff *)", "Bash(git log *)"
    ],
    "ask": ["Bash(git push *)", "Bash(npm install *)", "WebFetch"],
    "deny": [
      "Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)",
      "Bash(terraform apply *)", "Bash(kubectl delete *)", "Bash(rm -rf *)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/block_dangerous.py\"" }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "npx prettier --write \"$(jq -r '.tool_input.file_path')\" 2>/dev/null || true" }] }
    ]
  }
}
```

Plus `CLAUDE.md`, `.claude/skills/` (fix-issue, commit-msg), `.claude/agents/code-reviewer.md`, and
`.gitignore` entries: `.claude/settings.local.json`, `CLAUDE.local.md`.

### 🟢🟡 Productive & sandboxed (WSL2/macOS/Linux): add to user settings

```json
{
  "permissions": { "defaultMode": "acceptEdits" },
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "filesystem": { "denyRead": ["~/.ssh", "~/.aws", "~/.azure", "~/.config/gcloud"] },
    "network": { "allowedDomains": ["registry.npmjs.org", "pypi.org", "files.pythonhosted.org", "github.com"] }
  }
}
```

### 🔴 Autopilot: only in a dev container / VM

`bypassPermissions` or `auto` mode, inside a container with a **copy** of the repo, **no**
cloud/prod credentials, and network limited. Review the final diff before merging.

---

## 5.13 Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| A setting "does nothing" | Typo in key name (ignored), wrong file, or overridden by higher level | Add `$schema` for validation; run `claude doctor` / `/doctor` |
| `Bash(git *)` allowed `git push --force` | Wildcard too broad | Allow specific subcommands: `Bash(git log *)`, `Bash(git diff *)` |
| Startup warning about a wildcard rule | `*` placed before the subcommand | Put `*` after the subcommand |
| Skill not triggering | Vague `description`, or `disable-model-invocation: true` | Improve description; run it with `/name` |
| Unknown frontmatter field silently ignored | Claude Code ignores unrecognized fields | Check exact names: `allowed-tools`, `disable-model-invocation` |
| Hook not firing | Wrong matcher (case-sensitive tool names like `Bash`, `Edit`), script not executable, extra stdout | Test the script: `echo '{"tool_input":{"command":"rm -rf /"}}' \| python3 block_dangerous.py; echo $?` |
| Sandbox can't be enabled | Native Windows, or missing `bubblewrap`/`socat` | Use WSL2; install deps; restart; `/sandbox` shows a Dependencies tab |
| `npm install` fails in sandbox | Domain not in `allowedDomains` | Add the registry domains |
| `.env` still readable by the Read tool with sandbox on | Sandbox only covers shell commands | Add `Read(./.env)` deny rules |
| Teammates get different behaviour | Personal `settings.local.json` / `~/.claude` differences | Put team policy in `.claude/settings.json` (committed) |

---

**Next:** [06 — Scenarios, Recipes & Side-by-Side Comparison ➡️](06-recipes-comparison.md)
