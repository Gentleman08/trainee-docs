# 06 — Scenarios, Recipes & Side-by-Side Comparison

[⬅️ Back to Index](README.md) · [⬅️ Previous: Claude Code Customization](05-claude-code-customization.md)

---

> Real situations, each solved **safely and efficiently** in both Antigravity and Claude Code.
> Every recipe is a prompt you can adapt, plus the settings and habits that make it safe.

---

## Table of Contents

- [6.1 Rosetta Stone: Antigravity ↔ Claude Code](#61-rosetta-stone)
- [6.2 Recipe 1 — Understand an unfamiliar repo (read-only)](#recipe-1--understand-an-unfamiliar-repo)
- [6.3 Recipe 2 — Fix a bug with a test first](#recipe-2--fix-a-bug-with-a-test-first)
- [6.4 Recipe 3 — Build a feature: plan → isolate → implement → review](#recipe-3--build-a-feature-safely)
- [6.5 Recipe 4 — Code review before you merge](#recipe-4--code-review-before-you-merge)
- [6.6 Recipe 5 — Write or update documentation](#recipe-5--write-or-update-documentation)
- [6.7 Recipe 6 — Several agents in parallel](#recipe-6--several-agents-in-parallel)
- [6.8 Recipe 7 — Infrastructure / DevOps tasks without touching prod](#recipe-7--devops-and-infrastructure-tasks)
- [6.9 Recipe 8 — Protect secrets end-to-end](#recipe-8--protect-secrets-end-to-end)
- [6.10 Recipe 9 — Automation: commit messages & PR reviews in scripts/CI](#recipe-9--automation)
- [6.11 Recipe 10 — Team rollout: shared config in the repo](#recipe-10--team-rollout)
- [6.12 Recipe 11 — Safe Windows setup with WSL2](#recipe-11--safe-windows-setup-with-wsl2)
- [6.13 Recipe 12 — Keeping costs and quota under control](#recipe-12--keeping-costs-under-control)
- [6.14 Red flags: when to stop the agent](#614-red-flags-when-to-stop-the-agent)
- [6.15 Troubleshooting both tools](#615-troubleshooting-both-tools)
- [6.16 One-page cheat sheets](#616-one-page-cheat-sheets)

---

## 6.1 Rosetta Stone

| Concept | Antigravity | Claude Code |
|---------|-------------|-------------|
| Start in terminal | `agy` | `claude` |
| GUI | Antigravity App / IDE / editor extensions | VS Code & JetBrains extensions, desktop app, web |
| One-shot / headless | `agy -p "…" --output-format json` | `claude -p "…" --output-format json` |
| Continue last session | `agy -c` | `claude -c` |
| Plan first | `--mode=plan`, `/planning`, Shift+Tab | `--permission-mode plan`, Shift+Tab |
| Auto-accept edits | `--mode=accept-edits` | `acceptEdits` mode |
| "Approve everything" (danger) | Turbo preset · `toolPermission: always-proceed` · `--dangerously-skip-permissions` | `bypassPermissions` mode · `--dangerously-skip-permissions` |
| Interrupt | `Esc` | `Esc` |
| Undo conversation/changes | `/rewind` (`/undo`), `/fork` | `Esc Esc` / `/rewind`, checkpoints |
| Fresh context | `/clear` | `/clear` (+ `/compact`) |
| Personal settings | `~/.gemini/antigravity-cli/settings.json` (CLI), App Settings | `~/.claude/settings.json` |
| Project settings | App project settings; repo files in `.agents/` | `.claude/settings.json` (+ `.local.json`) |
| Always-on instructions | `AGENTS.md` / `GEMINI.md` | `CLAUDE.md` (reads `AGENTS.md` too) |
| Modular rules | `.agents/rules/*.md` (`trigger:` frontmatter) | `.claude/rules/*.md` (`paths:` frontmatter) |
| Skills | `.agents/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` |
| Subagents | `.agents/agents/<name>.md` | `.claude/agents/<name>.md` |
| Hooks | `.agents/hooks.json` | `"hooks"` in `.claude/settings.json` |
| Block via hook | stdout `{"decision":"deny"}` | exit code `2`, or `permissionDecision: "deny"` |
| MCP config | `.agents/mcp_config.json`, `~/.gemini/config/mcp_config.json` | `.mcp.json`, `claude mcp add` |
| Permission rule: command | `command(npm test)` | `Bash(npm test)` |
| Permission rule: read file | `read_file(.env)` | `Read(./.env)` |
| Permission rule: write file | `write_file(src/)` | `Edit(./src/**)` |
| Permission rule: website | `read_url(github.com)` | `WebFetch(domain:github.com)` |
| Permission rule: MCP | `mcp(github/get_issue)` | `mcp__github__get_issue` |
| Precedence | Deny > Ask > Allow | Deny > Ask > Allow |
| Sandbox | Default preset / `enableTerminalSandbox` (macOS, Linux; Windows App preview) | `/sandbox`, `sandbox.enabled` (macOS, Linux, WSL2) |
| Plugins | `agy plugin …`, `/plugin` | `/plugin`, marketplaces |
| Check quota | `/usage`, `/credits` | `/usage`, `/cost` |

> 💡 **Portable setup:** write shared instructions in **`AGENTS.md`** and skills in the shared
> **Agent Skills** format. Then both tools can use the same content. (Claude Code reads
> `AGENTS.md`. For skills, keep one copy and symlink or copy it into `.claude/skills/` and
> `.agents/skills/`.)

---

## Recipe 1 — Understand an unfamiliar repo

**Goal:** learn how a codebase works **without any risk of changes**.

**Setup:** Antigravity → **plan** mode / Request Review / strict mode. Claude Code → **plan** mode.

**Prompts (one at a time):**

```
1. "Give me a 10-line overview of this repository: purpose, main language/framework, how to run it."
2. "Draw an ASCII diagram of the main components and how a request flows through them."
3. "Which files would I touch to change <the login behaviour>? Don't edit anything."
4. "List the commands to install, test, lint and run this project, based on the repo's files."
5. "What looks risky, outdated or confusing here? Explain like I'm a beginner."
```

**Make it reusable:** ask the agent to *"turn findings into a draft AGENTS.md / CLAUDE.md"*
(Claude Code: `/init`). Review it, then commit.

---

## Recipe 2 — Fix a bug with a test first

**Goal:** fix a reported bug and prove it's fixed.

```
GOAL:   Prices show as "NaN" on the cart page when quantity is empty.
CONTEXT: Cart logic is in src/cart/. Steps: add item, clear the quantity box.
RULES:  Don't modify existing tests. Don't change the public API.
STEPS:  1) Write a failing test that reproduces this. Run it and show it failing.
        2) Fix the code. 3) Run the full test suite and show the output.
        4) Explain the root cause in 2 sentences.
```

**Why test-first:** the failing test proves the agent understood the bug, and stops it from
"fixing" things by deleting assertions.

**Safety:** allow `npm run test *` / `command(regex:npm run (test|lint))` so the loop is fast.
Keep `git push`, installs and deletes on ask/deny.

---

## Recipe 3 — Build a feature safely

```
 1. Clean Git state → new branch or WORKTREE
      Antigravity App: "New worktree mode"   |   Claude Code: git worktree add … && claude
 2. PLAN mode → prompt with Goal / Context / Constraints / Verify
 3. Review the plan (Antigravity: implementation-plan artifact with inline comments)
 4. Implement in default (review every diff) or accept-edits (review at end)
 5. Verify: tests + lint + typecheck output shown in the chat
 6. Review: run a reviewer subagent (code-auditor / code-reviewer) + read git diff yourself
 7. Commit with a good message (commit-msg skill), open a PR, normal human review
```

**Prompt template:**

```
Feature: add "Export to CSV" to the Reports page.
- Use the existing table data; no new backend endpoint.
- Put logic in src/reports/export.ts with unit tests.
- Follow the patterns in src/reports/print.ts.
Plan only first. List files to create/change and any new dependencies (prefer none).
```

---

## Recipe 4 — Code review before you merge

**Antigravity:** *"Have the **code-auditor** subagent review the changes on this branch
compared to main."* (Chapter 03 §3.8)

**Claude Code:** *"Use the **code-reviewer** subagent on `git diff main...HEAD`."* (Chapter 05 §5.5)

**Generic review prompt (works anywhere):**

```
Review `git diff main...HEAD` as a strict senior engineer.
Report as a table: Severity | File:line | Problem | Suggested fix.
Check correctness, edge cases, error handling, security (injection, secrets, authz),
performance, missing tests, and readability. Don't edit files.
```

> An AI review **complements** a human review. It doesn't replace one. Treat its findings as
> leads to verify, not truths.

---

## Recipe 5 — Write or update documentation

```
Update README.md so a new developer can run the project locally on Windows and macOS.
- Verify every command by reading package.json / Makefile; do not invent commands.
- Add a "Troubleshooting" section with the 3 most likely setup errors.
- Keep the existing style. Show me the diff.
```

**Tip:** documentation tasks are low-risk, so they're a good place to try `acceptEdits` /
accept-edits mode or the "Always proceed" artifact policy while you build trust.

---

## Recipe 6 — Several agents in parallel

**When:** independent tasks (a bug fix + a docs update + a test-coverage task).

| | Antigravity | Claude Code |
|---|---|---|
| Isolation | App: one conversation per task in **New worktree mode**; supervise in the **Agent Manager** (`Ctrl+E`) | One `git worktree` + terminal per task (or built-in worktree subagents) |
| Within one task | Main agent spawns **parallel subagents** (`/agents` to monitor, `Alt+J` to approve) | Ask Claude to "use subagents in parallel to investigate X, Y, Z" |
| Multi-agent teams | `/teamwork-preview` (paid plans) | Agent teams / subagents (see docs) |

**Rules for parallel agents:**

- **Never** let two agents edit the same folder at once. Separate worktrees prevent overwrites.
- Give each a **narrow scope** ("only touch `docs/`").
- Merge one branch at a time and re-run tests after each merge.

---

## Recipe 7 — DevOps and infrastructure tasks

**Goal:** write Terraform/Kubernetes/pipeline code with AI help **without** an agent ever
changing real infrastructure.

**Setup:**

- **Log out of production** or use a separate terminal profile with **no** cloud credentials
  loaded (`az logout`, unset `AWS_PROFILE`, a separate kubeconfig).
- Deny rules:
  - Antigravity: `command(terraform apply)`, `command(terraform destroy)`, `command(kubectl delete)`,
    `command(kubectl apply)`, `command(az)`, `command(aws)`
  - Claude Code: `Bash(terraform apply *)`, `Bash(terraform destroy *)`, `Bash(kubectl apply *)`,
    `Bash(kubectl delete *)`, `Bash(az *)`, `Bash(aws *)`
- Allow the safe, read-only checks: `terraform fmt`, `terraform validate`, `helm lint`,
  `kubectl kustomize`, `hadolint`, `checkov`.

**Prompt:**

```
Write a Terraform module for an Azure Storage account with private endpoint, following the
conventions in infra/modules/. Run `terraform fmt` and `terraform validate` only.
Never run plan/apply. Explain each resource for a beginner.
```

Then run `terraform plan` **yourself**, in your normal pipeline (see the
[CI/CD guide, Chapter 04](../cicd-pipelines/04-iac.md)).

---

## Recipe 8 — Protect secrets end-to-end

| Layer | Antigravity | Claude Code |
|-------|-------------|-------------|
| Don't read secret files | `deny: read_file(.env)`, `read_file(~/.ssh)`; strict mode respects `.gitignore` | `deny: Read(./.env)`, `Read(./.env.*)`, `Read(~/.ssh/**)` |
| Sandbox the shell | Sandbox blocks `~/.ssh`, `.env` by default; network off | `sandbox.filesystem.denyRead`, `network.allowedDomains` |
| Block exfiltration patterns | PreToolUse hook denying `curl … \| sh`, uploads | PreToolUse hook (exit 2) |
| Keep them out of Git | `.gitignore` `.env*`, `*.pem`; secret scanning in CI | Same |
| Keep them out of config | No tokens in `.agents/mcp_config.json` | No tokens in `.mcp.json`; use env vars |
| Instruct | `AGENTS.md`: "never read/print secrets" | `CLAUDE.md`: same |

**If a secret is ever pasted into a chat or committed: rotate it.** Deleting the message or
commit isn't enough.

---

## Recipe 9 — Automation

**Commit message from staged changes (local Git alias or script):**

```bash
# Antigravity
git diff --cached | agy -p "Write a Conventional Commits message for this diff. Output only the message."

# Claude Code
git diff --cached | claude -p "Write a Conventional Commits message for this diff. Output only the message."
```

**Review a patch in CI with strict limits:**

```bash
# Antigravity: settings.json allows only what's needed; check JSON status
agy -p "Review the diff in pr.patch for bugs and security issues. Output Markdown." \
  --output-format json --print-timeout 10m | jq -r 'if .status=="SUCCESS" then .response else error(.error) end' > review.md

# Claude Code: read-only tools, capped turns
claude -p "Review the diff in pr.patch for bugs and security issues. Output Markdown." \
  --allowedTools "Read,Grep,Glob" --permission-mode dontAsk --max-turns 15 \
  --output-format json | jq -r '.result' > review.md
```

**Automation safety checklist:**

- [ ] Read-only or minimal tool allow-list
- [ ] No production credentials in the CI environment
- [ ] Turn/time limits (`--max-turns`, `--print-timeout`)
- [ ] Check success status in the JSON output
- [ ] Treat PR titles/bodies/issue text as **untrusted** (prompt injection)
- [ ] Never `--dangerously-skip-permissions` on shared runners

---

## Recipe 10 — Team rollout

Commit a shared, reviewed setup so every teammate's agent behaves the same:

```
repo/
├── AGENTS.md                         ← shared instructions (both tools read it)
├── CLAUDE.md                         ← can be just:  @AGENTS.md  + Claude-specific notes
├── .agents/                          ← Antigravity: rules/, skills/, agents/, hooks.json
├── .claude/                          ← Claude Code: settings.json (perms + hooks), skills/, agents/, rules/
├── .github/CODEOWNERS                ← platform team must review changes to agent config:
│                                        /.claude/  /.agents/  /AGENTS.md  /CLAUDE.md
└── .gitignore                        ← .claude/settings.local.json, CLAUDE.local.md, .env*
```

**Team policy checklist:**

- [ ] Agent config changes go through PR review (CODEOWNERS), because hooks run code on everyone's machine
- [ ] Deny lists for secrets and destructive commands committed in the repo
- [ ] Organisation-level guard-rails where available (Claude Code **managed settings** with
      `disableBypassPermissionsMode`; Antigravity enterprise/business settings)
- [ ] Approved list of MCP servers/plugins
- [ ] Short onboarding: Chapter 00 of this guide + "your first safe session"

---

## Recipe 11 — Safe Windows setup with WSL2

Both tools have their **strongest sandboxing on Linux**. On Windows:

```powershell
# 1. Install WSL2 with Ubuntu (admin PowerShell), then reboot
wsl --install -d Ubuntu
```

```bash
# 2. Inside Ubuntu (WSL)
sudo apt update && sudo apt install -y git bubblewrap socat jq
mkdir -p ~/code && cd ~/code && git clone <your-repo>      # keep repos in the Linux filesystem

# 3. Install the agents inside WSL
curl -fsSL https://claude.ai/install.sh | bash
curl -fsSL https://antigravity.google/cli/install.sh | bash

# 4. Turn on sandboxes
#    Claude Code: run `claude`, then /sandbox
#    Antigravity CLI: ~/.gemini/antigravity-cli/settings.json → "enableTerminalSandbox": true, "toolPermission": "proceed-in-sandbox"
```

5. GUI: VS Code → "WSL" remote extension → open the folder from WSL, then use the Claude Code
   extension there. For the Antigravity App on Windows, use **Request Review** + **Always Ask**
   for outside-folder access, and try **Sandbox Mode (Preview)**.

---

## Recipe 12 — Keeping costs under control

| Habit | Why |
|-------|-----|
| `/clear` between unrelated tasks | Smaller context = cheaper and smarter |
| `@`-mention files instead of "find the code that…" | Less searching |
| Use fast/smaller models for simple work | Big models cost more per token |
| Put stable facts in `AGENTS.md`/`CLAUDE.md` | No re-explaining each session |
| Use subagents for big investigations | Only the summary enters your main context |
| Check `/usage` (both), `/credits` (Antigravity), `/cost` (Claude Code API) | Know where you stand |
| Antigravity: keep `useG1Credits` off unless intended | Avoid spending paid credits automatically |
| Avoid open-ended autonomy (`/goal`, long auto runs) without limits | Runaway loops |

---

## 6.14 Red flags: when to stop the agent

Press **Esc** immediately if you see the agent:

- 🚩 Reading `.env`, keys, or files outside the project you didn't mention
- 🚩 Deleting or "simplifying" tests to make them pass
- 🚩 Running `rm`, `git reset --hard`, `git push --force`, `sudo`, or cloud CLI commands you didn't ask for
- 🚩 Installing packages you didn't ask for (possible hallucinated or typo-squatted names)
- 🚩 Disabling linters, type checks or security settings ("// eslint-disable", "--no-verify")
- 🚩 Following instructions it found in a web page, issue or file ("the README says to run…")
- 🚩 Looping on the same failing fix 3+ times
- 🚩 Making a huge diff for a small request

Then: explain the problem, `/rewind`, or `/clear` and restart with a sharper prompt.

---

## 6.15 Troubleshooting both tools

| Problem | Antigravity | Claude Code |
|---------|-------------|-------------|
| Too many prompts | Add `allow` rules; use Default preset (sandbox) | Add `allow` rules; `acceptEdits`; sandbox auto-allow |
| Agent ignores my conventions | Put them in `AGENTS.md`; check rule frontmatter (`trigger`) | Put them in `CLAUDE.md`; keep it short and specific |
| A safety rule must never be broken | Deny rule + PreToolUse hook + sandbox | Deny rule + PreToolUse hook + sandbox |
| Command fails only for the agent | Sandbox blocks network/paths → `read_url`/`write_file` allows | Sandbox → `allowedDomains` / `allowWrite` |
| Skill/command not found | `.agents/skills/<name>/SKILL.md`, workflows retired 19 Oct 2026 | `.claude/skills/<name>/SKILL.md` |
| Hook not running | `/hooks`; JSON-only stdout; matcher = tool name regex | `/hooks`; exit codes; matcher case-sensitive (`Bash`, `Edit`) |
| Settings not applied | `/config`; check file path `~/.gemini/antigravity-cli/settings.json` | `claude doctor`; `$schema` validation; precedence |
| Context full / agent confused | `/context`, `/clear`, `/fork` | `/context`, `/compact`, `/clear` |
| Install/PATH issues | `agy --version`; add install dir to PATH | `claude --version`; `claude doctor` |

---

## 6.16 One-page cheat sheets

### Antigravity

```
INSTALL   Win: irm https://antigravity.google/cli/install.ps1 | iex
          mac/Linux/WSL: curl -fsSL https://antigravity.google/cli/install.sh | bash
RUN       agy · agy -c · agy --mode=plan · agy --sandbox · agy -p "…" --output-format json
KEYS      Esc stop · Shift+Tab modes · @ file · Ctrl+R review · y/n approve · Ctrl+V paste image
CMDS      /help /config /permissions /model /effort /planning /fast /diff /rewind /fork
          /resume /clear /context /usage /skills /hooks /mcp /plugin /agents /learn
FILES     AGENTS.md · .agents/{rules,skills,agents}/ · .agents/hooks.json · .agents/mcp_config.json
          ~/.gemini/AGENTS.md · ~/.gemini/config/{rules,skills,agents,hooks.json,mcp_config.json}
          ~/.gemini/antigravity-cli/settings.json
RULES     command(x) read_file(x) write_file(x) read_url(x) execute_url(x) mcp(s/t) unsandboxed(x)
          Deny > Ask > Allow
SAFE      App: Request Review / Default preset, Strict mode, worktree mode, artifact review ON
          CLI: toolPermission request-review | proceed-in-sandbox + enableTerminalSandbox
```

### Claude Code

```
INSTALL   Win: irm https://claude.ai/install.ps1 | iex
          mac/Linux/WSL: curl -fsSL https://claude.ai/install.sh | bash
RUN       claude · claude -c · claude -r · claude --permission-mode plan · claude -p "…" --output-format json
KEYS      Esc stop · Esc Esc rewind · Shift+Tab modes · @ file · ! shell · / commands
CMDS      /help /init /memory /permissions /config /model /effort /clear /compact /context
          /rewind /resume /agents /mcp /hooks /sandbox /plugin /statusline /doctor /usage
FILES     CLAUDE.md · CLAUDE.local.md · .claude/{settings.json,settings.local.json,rules,skills,agents}/
          .mcp.json · ~/.claude/{settings.json,CLAUDE.md,rules,skills,agents}
RULES     Bash(cmd *) Read(./path) Edit(./src/**) WebFetch(domain:x) mcp__server__tool
          Deny > Ask > Allow
MODES     default(Manual) · acceptEdits · plan · auto · dontAsk · bypassPermissions(containers only)
SAFE      plan mode first · deny secrets & destructive cmds · /sandbox (WSL2/mac/Linux)
          disableBypassPermissionsMode · hooks for must-never rules · Git before every task
```

---

[⬅️ Back to Index](README.md)
