# 03 — Antigravity Customization: Rules, Skills, Hooks, MCP, Subagents, Plugins

[⬅️ Back to Index](README.md) · [⬅️ Previous: Antigravity CLI](02-antigravity-cli.md)

---

> Customizations are **plain files** that change how the agent behaves. They work across the
> Antigravity App, IDE, extensions and CLI. Most live in your repo (shared with the team via
> Git) or in your home folder (personal, all projects).

> 📝 Based on antigravity.google/docs, October 2026. Note the date warning about workflows in §3.5.

---

## Table of Contents

- [3.1 The big picture: which customization for which job?](#31-the-big-picture)
- [3.2 Folder layout cheat sheet](#32-folder-layout-cheat-sheet)
- [3.3 Rules: `AGENTS.md`, `GEMINI.md`, `.agents/rules/`](#33-rules)
- [3.4 Skills: reusable `/commands` and know-how](#34-skills)
- [3.5 ⚠️ Workflows → skills migration (deadline 19 Oct 2026)](#35-workflows-to-skills-migration)
- [3.6 Hooks: automatic checks and guard-rails](#36-hooks)
- [3.7 MCP: connecting external tools](#37-mcp)
- [3.8 Custom subagents](#38-custom-subagents)
- [3.9 Plugins: packaging it all](#39-plugins)
- [3.10 A complete starter kit for a repo](#310-a-complete-starter-kit)
- [3.11 Gotchas](#311-gotchas)

---

## 3.1 The big picture

| I want the agent to… | Use | Analogy |
|----------------------|-----|---------|
| Always know our conventions ("use pnpm", "tests live in `tests/`") | **Rules** (`AGENTS.md`) | Employee handbook |
| Follow a specific procedure when asked ("how we write release notes") | **Skill** (`/release-notes`) | Standard operating procedure (SOP) |
| **Never** do something, enforced by code, not by politeness | **Hook** (+ deny permission rules) | Security guard at the door |
| Talk to GitHub, a database, Jira, Figma… | **MCP server** | A phone line to another department |
| Hand a sub-task to a specialist with limited tools | **Subagent** | Calling in a consultant |
| Share all of the above across many repos/people | **Plugin** | A starter kit in a box |

> 🧠 **Key insight:** rules and skills are **requests**. The model *usually* follows them,
> but can slip. **Permissions and hooks are enforcement.** For anything safety-critical, use
> enforcement, not just a sentence in `AGENTS.md`.

---

## 3.2 Folder layout cheat sheet

```
your-repo/                              ← commit these (team-shared)
├── AGENTS.md                           ← always-on project rules (or GEMINI.md)
├── .agents/
│   ├── rules/                          ← modular rules (frontmatter required, top level only)
│   │   ├── testing.md
│   │   └── api-style.md
│   ├── rules.json                      ← optional: include nested/external rule files
│   ├── skills/
│   │   └── release-notes/
│   │       └── SKILL.md                ← becomes /release-notes
│   ├── agents/
│   │   └── code-auditor.md             ← custom subagent
│   ├── hooks.json                      ← workspace hooks
│   └── mcp_config.json                 ← workspace MCP servers (NO secrets inside!)
└── src/payments/AGENTS.md              ← directory-specific rules (apply when working here)

~/.gemini/                              ← personal (all projects)
├── AGENTS.md  or  GEMINI.md            ← global always-on rules
└── config/
    ├── rules/*.md                      ← global modular rules (frontmatter required)
    ├── skills/<name>/SKILL.md          ← global skills (App/IDE)
    ├── agents/<name>.md                ← global subagents
    ├── hooks.json                      ← global hooks
    └── mcp_config.json                 ← global MCP servers
~/.gemini/antigravity-cli/              ← CLI-specific
    ├── settings.json, keybindings.json
    ├── rules/*.md, skills/<name>/, plugins/<name>/
```

> Older docs/blogs show `.agent/` (singular). Antigravity still reads it for backward
> compatibility, but **`.agents/`** (plural) is current.

---

## 3.3 Rules

### Where rules come from

| Location | Scope | Frontmatter? |
|----------|-------|-------------|
| `<dir>/AGENTS.md` or `<dir>/GEMINI.md` (also inside `<dir>/.agents/`) | That directory and below (repo root = whole project) | No: always active |
| `<dir>/.agents/rules/*.md` | That directory and below | **Yes, required** |
| `~/.gemini/AGENTS.md` / `~/.gemini/GEMINI.md` | All your projects | No |
| `~/.gemini/config/rules/*.md` | All your projects | **Yes** |
| `~/.gemini/antigravity-cli/rules/*.md` | CLI only | **Yes** |

Antigravity walks **up** from the file being worked on to the workspace root, loading rules at
each level. When rules conflict, **the more specific (deeper) directory wins**.

### Example root `AGENTS.md` (good for beginners and teams)

```markdown
# Project: Orders API

## What this is
A Node.js 22 + TypeScript REST API. Postgres via Prisma. Tests with Vitest.

## Commands
- Install: `npm ci`
- Test: `npm test`   (always run before saying a task is done)
- Lint: `npm run lint`
- Never run `npm install <pkg>` without asking me first.

## Conventions
- Code lives in `src/`, tests in `tests/` mirroring the src path.
- Use named exports. No default exports.
- Errors: throw `AppError` from `src/errors.ts`, never plain `Error`.

## Safety
- Never read, print or modify `.env` files or anything in `secrets/`.
- Never delete or weaken existing tests to make them pass.
- Never run git push, git reset --hard, or database migrations.
- If a task is ambiguous or risky, stop and ask.

## Explaining
- I'm a beginner: after each change, explain what you did in plain English.
```

### Modular rules with triggers (`.agents/rules/*.md`)

Every file **must** start with frontmatter containing a valid `trigger`. Files without it are
**silently ignored**.

| `trigger` | Loads when | Required fields | Use for |
|-----------|-----------|-----------------|---------|
| `always_on` | Every turn | — | Short, critical rules |
| `model_decision` | Agent decides it's relevant (sees only the description up front) | `description` | Longer domain guides |
| `glob` | Agent works on matching files | `globs` | Language/folder-specific style |
| `manual` | Only when you `@`-mention it | — | Checklists, audit rubrics |

```markdown
---
trigger: glob
globs: "*.sql, migrations/**"
description: "Database migration rules"
---
- Migrations must be backward compatible (add columns; never drop/rename in the same release).
- Every migration needs a matching down/rollback step.
- Never edit an already-applied migration file; create a new one.
```

```markdown
---
trigger: manual
description: "Pre-merge review checklist"
---
Before approving, check: tests added? docs updated? no secrets? no TODOs left? error handling?
```

> Values are **snake_case and case-sensitive**: `always_on`, not `alwaysOn`.

### Including other files

```markdown
Follow our API standards:
@[API Design Standards](../docs/api-standards.md)     ← INLINES the file's content
When changing models, look at @src/db/schema.ts first. ← just a precise path reference
```

### Limits that matter

- **24 KB per rule file** (after inlining). Bigger files are truncated.
- **~20,000-token budget** shared by global + `always_on` rules. Over budget, the biggest files
  become short pointers the agent reads on demand.
- Only **top-level** files in `.agents/rules/` are scanned. For subfolders, register them in
  `.agents/rules.json`.

**Writing good rules:** short, specific, testable sentences. "Use 2-space indentation in
TypeScript" works. "Write clean code" does nothing.

---

## 3.4 Skills

A **skill** is a folder with a `SKILL.md` (plus optional `scripts/`, `examples/`,
`resources/`) that teaches the agent a procedure. Skills follow the open **Agent Skills**
standard: the same format works in Claude Code (Chapter 05).

### Where

| Scope | App / IDE | CLI |
|-------|-----------|-----|
| Workspace (team) | `.agents/skills/<name>/` | `.agents/skills/<name>/` |
| Global (you) | `~/.gemini/config/skills/<name>/` | `~/.gemini/antigravity-cli/skills/<name>/` |
| Plugin | — | `~/.gemini/antigravity-cli/plugins/<plugin>/skills/` |

### How they're used

- **Automatically:** the agent sees every skill's `name` + `description`, and loads the full
  `SKILL.md` when relevant. **The description is what triggers it**, so make it precise.
- **Manually:** type `/<skill-name>` (App prompt box and CLI). In the IDE, see the
  **Customizations** menu in the agent side panel. CLI: `/skills` lists them.

### Example 1 — release notes (procedure skill)

`.agents/skills/release-notes/SKILL.md`:

```markdown
---
name: release-notes
description: Drafts release notes from git history since the last tag. Use when the user asks for release notes, a changelog entry, or "what changed since the last release".
---

# Release notes

1. Find the latest tag: `git describe --tags --abbrev=0`.
2. List commits since then: `git log <tag>..HEAD --oneline`.
3. Group into **Features**, **Fixes**, **Other** using the Conventional Commit prefix (feat/fix/…).
4. Write for non-technical readers: one line per change, no commit hashes.
5. Save to `RELEASE_NOTES.md` and show me the result. Do NOT create tags or push anything.
```

### Example 2 — safe dependency upgrade (with a script)

```
.agents/skills/upgrade-dependency/
├── SKILL.md
└── scripts/
    └── check-outdated.sh
```

```markdown
---
name: upgrade-dependency
description: Safely upgrades ONE npm dependency with tests. Use when asked to update, bump or upgrade a package.
---

1. Run `bash .agents/skills/upgrade-dependency/scripts/check-outdated.sh` and show the table.
2. Ask the user which ONE package to upgrade if not specified.
3. Read the package's changelog for breaking changes between versions; summarise them.
4. Upgrade with `npm install <pkg>@<version>`, then run `npm test` and `npm run lint`.
5. If anything fails, revert with `git restore package.json package-lock.json` and report.
6. Never upgrade more than one package per run.
```

### Example 3 — explain-like-I'm-new (personal, global)

`~/.gemini/config/skills/explain-simply/SKILL.md`:

```markdown
---
name: explain-simply
description: Explains code, errors, or diffs in beginner-friendly language with analogies. Use when the user asks "what does this mean", "explain", or seems confused.
---
Explain in plain English for someone with no programming background:
1. One-sentence summary.
2. An everyday analogy.
3. Line-by-line walkthrough of the important parts only.
4. "What could go wrong" in 2–3 bullets.
Avoid jargon; define any technical word you must use.
```

**Skill writing tips:**

- **Description = trigger.** Say *what* it does and *when* to use it, including the phrases a user would type.
- Use numbered steps, exact commands, and explicit "never do X" lines.
- Put long reference material in `resources/`, and tell the skill to read it only if needed (keeps context small).
- Skill names: lowercase-with-hyphens.

---

## 3.5 Workflows to skills migration

> ⚠️ **Deadline:** per the docs, legacy **workflows** (`.agents/workflows/<name>.md`,
> `~/.gemini/config/workflows/<name>.md`) **stop working on October 19, 2026**. After that,
> they're no longer indexed or runnable as slash commands. Many older tutorials still teach
> workflows. Use **skills** instead.

**Automatic migration:** run **`/migrate-workflows`**. It converts each workflow into a skill
folder and renames the original to `*.bak`.

**Manual migration:**

```
.agents/workflows/lint-check.md      ──►   .agents/skills/lint-check/SKILL.md
```

1. Create `.agents/skills/lint-check/`.
2. Move the workflow file in and rename it `SKILL.md`.
3. Add frontmatter with `name` and a good `description`.
4. Move long scripts/reference text into `scripts/` or `references/`.
5. Test with `/lint-check`.

If a skill and a workflow share a name, **the skill wins**.

---

## 3.6 Hooks

Hooks run **your scripts** automatically at points in the agent loop. They're how you
**enforce** policies (block, ask, rewrite) and automate chores (format, lint, log).

### Where

| Scope | File |
|-------|------|
| Workspace | `.agents/hooks.json` |
| Global | `~/.gemini/config/hooks.json` (CLI also reads hooks from its `settings.json`) |
| Plugin | the plugin's `hooks.json` (CLI) |

List loaded hooks in the CLI with **`/hooks`**.

### Events

| Event | Fires | Can it change behaviour? |
|-------|-------|--------------------------|
| `SessionStart` | Once, before the first model call | Setup / context |
| `PreInvocation` | Before each model call | — |
| `PreToolUse` | **Before a tool runs** (matcher filters tools) | ✅ allow / ask / deny / rewrite args |
| `PostToolUse` | After a tool finishes (matcher filters tools) | React (lint, log) |
| `PostInvocation` | After each model call | — |
| `Stop` | When the agent wants to stop | ✅ `"continue"` forces it to keep going |

### Format

```json
{
  "<hook-name>": {
    "enabled": true,
    "<EventName>": [
      {
        "matcher": "<regex on tool name>",
        "hooks": [
          { "type": "command", "command": "<shell command>", "timeout": 30 }
        ]
      }
    ]
  }
}
```

- `matcher` (PreToolUse/PostToolUse only): regex on the **tool name**. Examples: `"run_command"`,
  `"write_to_file|replace_file_content"`, `"browser_.*"`, `"*"` (all).
- Hooks get **JSON on stdin** and reply with **JSON on stdout**.
- `PreToolUse` input includes `toolCall.name` and `toolCall.args`. For `run_command`, the
  args include `CommandLine` and `Cwd`.
- `PreToolUse` output: `{"decision": "...", "reason": "..."}`, where `decision` is one of `allow`,
  `auto_approve`, `deny`, `ask`, `force_ask`, `deny_unless_prior_grant`. Optional `overwrite`
  merges new args into the tool call.

### Example 1 — block dangerous commands (enforcement)

`.agents/hooks.json`:

```json
{
  "safety-gate": {
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [{ "command": "python3 .agents/hooks/safety_gate.py", "timeout": 10 }]
      }
    ]
  }
}
```

`.agents/hooks/safety_gate.py`:

```python
#!/usr/bin/env python3
"""Deny obviously destructive commands; force a human prompt for risky ones."""
import json, re, sys

event = json.load(sys.stdin)
cmd = event.get("toolCall", {}).get("args", {}).get("CommandLine", "")

DENY = [r"\brm\s+-rf\s+(/|~|\*)", r"git\s+push\s+.*--force", r"git\s+reset\s+--hard",
        r"\bsudo\b", r"terraform\s+(apply|destroy)", r"kubectl\s+delete", r"curl[^|]*\|\s*(ba)?sh"]
ASK  = [r"\bnpm\s+install\b", r"\bpip\s+install\b", r"\bgit\s+push\b", r"\bdocker\b"]

def reply(decision, reason):
    print(json.dumps({"decision": decision, "reason": reason}))
    sys.exit(0)

for pattern in DENY:
    if re.search(pattern, cmd):
        reply("deny", f"Blocked by safety hook: matches '{pattern}'")
for pattern in ASK:
    if re.search(pattern, cmd):
        reply("force_ask", "Installs/pushes/docker need explicit human approval")

print("{}")   # no opinion: normal permission rules apply
```

### Example 2 — auto-format after the agent writes files

```json
{
  "format-after-write": {
    "PostToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [{ "command": "npx prettier --write . --log-level warn", "timeout": 60 }]
      }
    ]
  }
}
```

### Example 3 — don't let the agent stop until tests pass

```json
{
  "tests-must-pass": {
    "Stop": [
      { "hooks": [{ "command": "bash .agents/hooks/require_tests.sh", "timeout": 300 }] }
    ]
  }
}
```

```bash
#!/usr/bin/env bash
# .agents/hooks/require_tests.sh
cat > /dev/null            # consume stdin
if npm test --silent > /tmp/agent-tests.log 2>&1; then
  echo '{}'
else
  echo '{"decision":"continue","reason":"Tests are failing. Read /tmp/agent-tests.log and fix the code (do not modify tests)."}'
fi
```

> ⚠️ Use Stop hooks carefully: a test suite that can never pass makes the agent loop until
> quotas or limits stop it. Add a counter or check `executionNum` in the input.

**Hook safety notes:**

- Hooks run **with your permissions**, outside the agent's control. Review hooks in repos you
  clone **before** trusting the folder.
- Keep hooks **fast** (default timeout 30 s), and make them print **only** JSON on stdout.
- Toggle a hook off with `"enabled": false` instead of deleting it.

---

## 3.7 MCP

**MCP servers** give the agent new tools (GitHub issues, a database, docs search, Figma…).

### Where

| Scope | File |
|-------|------|
| Global | `~/.gemini/config/mcp_config.json` |
| Workspace | `.agents/mcp_config.json` |
| App UI | **Settings → Customizations → Installed MCP Servers → Add MCP** (MCP Store) |
| CLI UI | `/mcp` |

### Format

```json
{
  "mcpServers": {
    "github": {
      "serverUrl": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "local-sqlite": {
      "command": "npx",
      "args": ["-y", "some-sqlite-mcp-server", "--db", "./dev.db", "--read-only"],
      "disabledTools": ["execute_write_query"]
    }
  }
}
```

- `command` + `args` → a **local** (stdio) server. `serverUrl` → a **remote** server (legacy `url`/`httpUrl` aren't supported).
- `disabled: true` turns a server off. `disabledTools` hides specific tools from the model.
- OAuth tokens are stored by Antigravity in `~/.gemini/antigravity/mcp_oauth_tokens.json`.

> The server name/URL above are **illustrative**. Use the exact install instructions from the
> MCP server's own documentation or the MCP Store. Check whether your version expands
> `${VAR}` in config. If not, keep tokens in your **global** config, never in the repo.

### MCP safety

- **Every MCP server is code with access to your data.** Install only from sources you trust (official vendors, MCP Store).
- Keep MCP tools on **Ask** (the default), and allow only read-only tools:
  `mcp(github/get_issue)`, `mcp(docs/*)`. Keep mutations on ask: `mcp(sql/execute_mutation)`.
- Prefer **read-only** credentials and **non-production** databases.
- **Never commit tokens** in `.agents/mcp_config.json`. Plain-text secrets in a repo leak.
- Content returned by MCP tools (issue text, web pages) can contain **prompt injection**.

---

## 3.8 Custom subagents

A subagent is a specialist the main agent can delegate to, with **its own instructions,
tools and model**, and **without** the main conversation's history (fresh, focused context).

### Where

- Workspace: `.agents/agents/<name>.md` (or `.agents/agents/<name>/agent.md`)
- Global: `~/.gemini/config/agents/<name>.md`
- Plugins: `plugins/<plugin>/agents/`

### Example — read-only security auditor

`.agents/agents/code-auditor.md`:

```markdown
---
name: code-auditor
description: Reviews code for security vulnerabilities (injection, auth flaws, secrets, unsafe deserialization). Use after implementing features that touch auth, input handling, or data access.
tools: [view_file, grep_search]
model: pro
subagent: true
mainAgent: false
commandExecutionPolicy: off
---
You are a security reviewer. Analyse the code you are pointed to and report findings as a table:
| Severity | File:line | Issue | Suggested fix |
You must NOT modify any files. If nothing is found, say so explicitly.
```

| Field | Meaning |
|-------|---------|
| `name`, `description` | Required. The description tells the main agent **when** to delegate |
| `tools` | What it may use. **Fewer tools = safer.** A misspelled tool name can make it hang |
| `model` | `inherit` (default), `flash`, or `pro` |
| `subagent` / `mainAgent` | Can be delegated to / can be picked as the main chat agent |
| `commandExecutionPolicy` | `off`, `auto`, `eager`, `sandbox` (default) |
| `mcpServers`, `skills`, `plugins` | Extra capabilities for this agent only |

Use it: "Implement the password-reset endpoint, then have **code-auditor** review it." In the
CLI, `/agents` shows custom agents and running subagents, and `Alt+J` jumps to one awaiting approval.

---

## 3.9 Plugins

Plugins bundle **skills, rules, agents, hooks and MCP servers** so a team can install a whole
setup in one go (CLI: `/plugin` or `agy plugin`).

```bash
agy plugin install ./acme-agent-kit      # from a local folder (or a marketplace source)
agy plugin list
agy plugin disable acme-agent-kit
```

Typical plugin layout:

```
acme-agent-kit/
├── skills/<name>/SKILL.md
├── rules/*.md
├── agents/*.md
└── hooks.json
```

> Treat plugins like any software dependency: install from trusted sources only, read the
> hooks before installing (they run scripts on your machine), and pin versions for teams.

---

## 3.10 A complete starter kit

Copy this into a repo to get a safe, productive Antigravity setup:

```
AGENTS.md                                 ← §3.3 example (commands, conventions, safety)
.agents/
├── rules/
│   └── migrations.md                     ← glob rule for *.sql
├── skills/
│   ├── release-notes/SKILL.md            ← §3.4 example 1
│   └── upgrade-dependency/               ← §3.4 example 2
├── agents/
│   └── code-auditor.md                   ← §3.8
├── hooks.json                            ← safety-gate + format-after-write (§3.6)
└── hooks/
    └── safety_gate.py
```

Plus, per person (not in the repo):

- `~/.gemini/AGENTS.md`: your personal preferences ("explain changes simply", "I use Windows + PowerShell").
- CLI `settings.json`: the beginner or productive profile from [Chapter 02 §2.13](02-antigravity-cli.md#213-recommended-configurations).
- App: preset **Request Review** or **Default**, strict mode for sensitive repos.

Add to `.gitignore`:

```gitignore
.env
.env.*
*.pem
# keep personal/secret MCP configs out of the repo if you create any locally
.agents/mcp_config.local.json
```

---

## 3.11 Gotchas

| Problem | Cause | Fix |
|---------|-------|-----|
| A rule in `.agents/rules/` is ignored | Missing/invalid frontmatter (`trigger`), or camelCase value | Add `trigger: always_on` (snake_case) |
| Nested rule files ignored | Only top-level `.agents/rules/*.md` are scanned | Move them up, or register them in `.agents/rules.json` |
| Huge rules file only partly followed | Truncated at 24 KB / budget exceeded | Split into `model_decision`/`glob` rules; keep `always_on` short |
| Skill never triggers automatically | Vague `description` | Describe *what* and *when*, using the words users type |
| `/my-workflow` stopped working | Workflows end **19 Oct 2026** | `/migrate-workflows` |
| Hook seems to do nothing | Script prints extra text, wrong matcher, not executable, timeout | Print only JSON; check the tool name; `chmod +x`; test it by piping sample JSON |
| Subagent hangs | Misspelled tool name in `tools` | Fix the tool name |
| MCP server fails to connect | Using `url` instead of `serverUrl`; missing token | Use `serverUrl`; set the token in your global config |
| Teammate's agent behaves differently | Personal `~/.gemini` rules/settings differ | Put team rules in the repo (`AGENTS.md`, `.agents/`) |

---

**Next:** [04 — Claude Code: Basics, Modes & Safe Usage ➡️](04-claude-code-basics.md)
