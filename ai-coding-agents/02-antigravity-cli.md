# 02 — Antigravity CLI (`agy`)

[⬅️ Back to Index](README.md) · [⬅️ Previous: Antigravity GUI](01-antigravity-gui.md)

---

> `agy` is Antigravity's **terminal agent**: same brain, same customization files, but
> keyboard-driven, scriptable and usable over SSH. It replaced the older **Gemini CLI**. If
> you're new to terminals, read [Chapter 00](00-fundamentals.md) first.

> 📝 Based on the official docs (antigravity.google/docs) as of October 2026. Run `agy --help`
> and `/help` to see what your installed version supports.

---

## Table of Contents

- [2.1 Install, verify, sign in](#21-install-verify-sign-in)
- [2.2 First run & the screen](#22-first-run)
- [2.3 Agent modes: default, accept-edits, plan](#23-agent-modes)
- [2.4 The settings file](#24-the-settings-file)
- [2.5 Tool permission levels (`toolPermission`)](#25-tool-permission-levels)
- [2.6 Permission rules in `settings.json`](#26-permission-rules)
- [2.7 The terminal sandbox](#27-the-terminal-sandbox)
- [2.8 Essential slash commands](#28-essential-slash-commands)
- [2.9 Keyboard shortcuts](#29-keyboard-shortcuts)
- [2.10 Sessions: resume, fork, rewind](#210-sessions-resume-fork-rewind)
- [2.11 Headless mode & automation](#211-headless-mode-and-automation)
- [2.12 Personalising the CLI](#212-personalising-the-cli)
- [2.13 Recommended configurations](#213-recommended-configurations)
- [2.14 Gotchas](#214-gotchas)

---

## 2.1 Install, verify, sign in

```powershell
# Windows (PowerShell)
irm https://antigravity.google/cli/install.ps1 | iex
# installs to C:\Users\<you>\AppData\Local\agy\bin
```

```cmd
:: Windows (Command Prompt)
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

```bash
# macOS / Linux / WSL2
curl -fsSL https://antigravity.google/cli/install.sh | bash
# installs to ~/.local/bin/agy
```

Optional installer flags: `--skip-aliases` (don't change shell aliases) and `--skip-path`
(don't edit `PATH` in your shell profile).

```bash
agy --version      # verify
```

> ⚠️ **About `curl … | bash` and `irm … | iex`:** these download a script and run it
> immediately. That's normal for official installers from the vendor's own domain. Never do
> it with URLs from random blog posts or chat messages.

**Sign in:**

| Situation | What happens |
|-----------|-------------|
| Local machine | Uses your OS keyring; if not signed in, opens the browser |
| Over SSH | Prints a URL → open it on your laptop → paste the code back |
| Gemini API key | Set `"modelProvider": "gemini"` in `~/.gemini/antigravity-cli/settings.json` **and** `export GEMINI_API_KEY=...` (the env var alone does nothing) |
| Log out | `/logout` |

---

## 2.2 First run

```bash
cd path/to/your/project      # ALWAYS start agy inside the project folder
agy
```

On first launch you pick a **color scheme**, a **rendering mode** (Alt-Screen or Inline), and
**confirm you trust the repository**. Only trust folders whose contents you know: a repo can
contain rules and hooks that instruct the agent.

Then type a prompt. When the agent proposes changes:

- `Ctrl+R` opens the **review panel**
- `y` approve · `n` reject · `f` full-screen diff · `Ctrl+G` edit in your editor
- Or **type an instruction** to reject and redirect ("no, keep the old function name")

---

## 2.3 Agent modes

| Mode | Behaviour | When to use |
|------|-----------|-------------|
| `default` | Pauses for **diff review before any file is created or changed** | ✅ Beginners, important code |
| `accept-edits` | Applies file edits **without asking** (subagents inherit it) | Trusted, well-scoped tasks, ideally in a worktree |
| `plan` | Investigates and **writes a plan first**, before code | Anything non-trivial; unfamiliar code |

- **Switch during a session:** `Shift+Tab` cycles `default → accept-edits → plan`. The status bar shows `[plan]` etc.
- **For one run:** `agy --mode=plan` or `agy --mode=accept-edits` (note: it's `--mode`, not `--permission-mode`).
- **Permanent default:** `"agentMode": "plan"` in settings.json.

> 💡 Modes control **file edits**. **Shell commands** are still governed by your permission
> rules / `toolPermission` (next sections), in every mode.

---

## 2.4 The settings file

```
~/.gemini/antigravity-cli/settings.json         ← CLI settings (permissions, UI, sandbox, hooks)
~/.gemini/antigravity-cli/keybindings.json      ← custom keyboard shortcuts
~/.gemini/antigravity-cli/rules/*.md            ← CLI-only global rules (Chapter 03)
~/.gemini/antigravity-cli/skills/<name>/        ← CLI global skills
~/.gemini/antigravity-cli/plugins/<name>/       ← installed plugins
```

On Windows, `~` is `C:\Users\<you>`. Edit settings with **`/config`** (alias `/settings`) inside
`agy`, or open the JSON in an editor. Command-line flags (like `--sandbox`) override the saved
values for that session only.

**Important keys:**

| Key | Values | Purpose |
|-----|--------|---------|
| `toolPermission` | `request-review` (default), `proceed-in-sandbox`, `strict`, `always-proceed` | Overall approval behaviour |
| `artifactReviewPolicy` | `asks-for-review` (default), `agent-decides`, `always-proceed` | Pause for plan/artifact review? |
| `enableTerminalSandbox` | `true` / `false` (default) | Run commands in the OS sandbox |
| `allowNonWorkspaceAccess` | `false` (default) / `true` | Files outside the project |
| `agentMode` | `default`, `accept-edits`, `plan` | Starting mode |
| `permissions` | `{ allow: [], ask: [], deny: [] }` | Fine-grained rules |
| `editor` / `editorMode` | `auto`, `vim`, … / `default`, `vim` | Editor used by `Ctrl+G`; vim keys |
| `colorScheme`, `altScreenMode`, `verbosity`, `notifications`, `showTips` | various | Look & feel |
| `enableTelemetry` | `true` / `false` | Usage data sharing |
| `useG1Credits` | `true` / `false` | Spend paid AI credits when standard quota runs out (cost control!) |

---

## 2.5 Tool permission levels

| `toolPermission` | Behaviour | Who it's for |
|------------------|-----------|-------------|
| `strict` | Prompts for **every non-read operation** | Sensitive repos, very cautious beginners |
| `request-review` *(default)* | Prompts before writes, shell commands, network calls | ✅ Beginners |
| `proceed-in-sandbox` | Runs terminal commands **inside the sandbox** automatically; prompts for risky/unsandboxed ones | ✅ Comfortable users on macOS/Linux/WSL2 |
| `always-proceed` | Doesn't ask | ⚠️ Disposable environments only |

And the nuclear option for one session: `--dangerously-skip-permissions` approves **every**
tool call (file writes **and** commands). The name is a warning. Use it only inside a throw-away
container/VM.

---

## 2.6 Permission rules

Same `action(target)` syntax as the App ([Chapter 01 §1.8](01-antigravity-gui.md#18-writing-allow--ask--deny-rules)),
stored in `settings.json`:

```json
{
  "toolPermission": "request-review",
  "permissions": {
    "allow": [
      "command(git status)",
      "command(git diff)",
      "command(git log)",
      "command(regex:npm run (build|lint|test))",
      "command(regex:pytest.*)",
      "write_file(src/)",
      "write_file(tests/)",
      "read_url(docs.python.org)"
    ],
    "ask": [
      "command(*)",
      "mcp(*)",
      "unsandboxed(*)"
    ],
    "deny": [
      "command(rm -rf)",
      "command(sudo)",
      "command(git push --force)",
      "command(git reset --hard)",
      "command(terraform apply)",
      "command(kubectl delete)",
      "read_file(.env)",
      "read_file(/home/me/.ssh)",
      "write_file(.git/)"
    ]
  }
}
```

**CLI defaults to know:**

- Reads/writes **inside the active project** are auto-allowed.
- `command`, `mcp`, `read_url`, `execute_url` and non-workspace files default to **Ask**.
- **Deny > Ask > Allow.**
- On Windows shells (PowerShell/CMD), commands that can't be split cleanly into words need an
  exact match. Use regex such as `command(regex:git .*)` to cover subcommands.
- Choosing "always allow" on a prompt for a command outside the sandbox records an
  `unsandboxed(...)` rule. Review your settings file now and then.

You can also manage rules interactively with **`/permissions`**.

> 💡 **Projects folder rules?** The docs describe CLI rules in the **user** settings file. For
> team-shared guidance per repo, use `AGENTS.md`/rules and `.agents/hooks.json` (Chapter 03),
> which live in the repo.

---

## 2.7 The terminal sandbox

The sandbox is an **OS-level box** (macOS Seatbelt, Linux namespaces) around commands the agent runs:

| | Inside the sandbox |
|---|---|
| Project folders | Read/write |
| Paths in `read_file` / `write_file` allow rules | Read-only / read-write |
| Everything else (incl. `~/.ssh`, `.env`) | **Blocked** |
| Network | **None by default**; domains in `read_url` allow rules are permitted |

**Turn it on:**

```json
{
  "enableTerminalSandbox": true,
  "toolPermission": "proceed-in-sandbox"
}
```

Or for one session: `agy --sandbox`.

**Escaping the sandbox:** some commands (Docker, `git push`, anything needing system services or
the network) can't run inside it. The agent then asks to run them **unsandboxed**, with full host
privileges. Approve case by case, or pre-approve specific ones with `"unsandboxed(git push)"` in `allow`.

> ⚠️ **Windows:** native-Windows sandboxing is described for the App (preview), not as a CLI
> feature. For the CLI sandbox on Windows, run `agy` inside **WSL2**.

---

## 2.8 Essential slash commands

Type `/` to open the menu. The most useful ones for beginners:

| Command | What it does |
|---------|-------------|
| `/help` | All commands & shortcuts |
| `/config` (`/settings`) | Settings editor |
| `/permissions` | Manage allow/ask/deny rules |
| `/model` | Choose the model (remembered) |
| `/effort [low…max]` | Reasoning effort |
| `/planning` · `/fast` | Plan-first mode · skip planning for quick tasks |
| `/diff` | Review changes, turns, commits |
| `/artifact` | Artifact review panel (`Ctrl+R`) |
| `/rewind` (`/undo`) | Roll the conversation back to an earlier message |
| `/fork` (`/branch`) | Copy the conversation into a new session (experiment safely) |
| `/resume` | Pick a previous conversation |
| `/clear` (`/new`) | Reset context: fresh start |
| `/context` | See how full the context window is |
| `/usage` (`/quota`) · `/credits` | Quota and credits |
| `/btw <question>` | Ask a side question without derailing the main task |
| `/add-dir <path>` | Give the agent access to another folder |
| `/skills` · `/hooks` · `/mcp` · `/plugin` | Inspect customizations (Chapter 03) |
| `/learn` | Turn this session's corrections into rules/skills (after your review) |
| `/goal <objective>` | Autonomous run until the goal is verified. ⚠️ Use with tight permissions |
| `/schedule <when> <task>` | One-off or recurring scheduled task |
| `/tasks` | Background shell logs |
| `/statusline` · `/title` · `/keybindings` | Personalise the UI |
| `/exit` | Quit |

---

## 2.9 Keyboard shortcuts

| Keys | Action |
|------|--------|
| `Esc` | **Stop the agent** / close panel / clear empty prompt |
| `Ctrl+C` | Exit (asks if agent is working) |
| `Shift+Tab` | Cycle modes (default / accept-edits / plan) |
| `Enter` / `Shift+Enter` (or `Ctrl+J`) | Send / new line |
| `@` | Insert a file path |
| `Ctrl+V` | Paste images/screenshots |
| `Ctrl+R` | Artifact review panel |
| `Ctrl+O` | Expand/collapse tool output |
| `Ctrl+G` | Write the prompt in your `$EDITOR` |
| `y` / `n` / `A` | Approve / reject / approve all artifacts |
| `Alt+J` / `Ctrl+K` | Jump to subagent awaiting approval / approve it |
| `F5` | Voice dictation |

Customise them in `~/.gemini/antigravity-cli/keybindings.json` or with `/keybindings`.

---

## 2.10 Sessions: resume, fork, rewind

```bash
agy -c                         # continue the most recent conversation
agy --conversation <id>        # resume a specific one
```

Inside a session:

- **`/rewind`** when the agent went down the wrong path. Roll back to a good message.
- **`/fork`** to try a risky idea in a copy, then `/resume` back to the main thread.
- **`/clear`** when switching to an unrelated task (keeps context small and cheap).

> ⚠️ Rewinding the **conversation** isn't the same as undoing **files on disk** in every case.
> Your real safety net is still **Git**: commit before, `git diff` after.

---

## 2.11 Headless mode and automation

Run one prompt without the UI. Output goes to stdout, so it's scriptable:

```bash
agy -p "Summarise what this repository does in 3 bullet points"

# Machine-readable output
agy -p "List TODO comments in src/" --output-format json | jq -r '.response'

# Force the answer into a JSON schema
agy -p "Extract major/minor/patch from v2.14.3" --output-format json \
  --json-schema '{"type":"object","properties":{"major":{"type":"integer"},"minor":{"type":"integer"},"patch":{"type":"integer"}},"required":["major","minor","patch"]}' \
  | jq '.structured_output'

# Draft a commit message from staged changes
git diff --cached | agy -p "Write a conventional commit message for this diff"
```

| Flag | Purpose |
|------|---------|
| `-p` / `--print` / `--prompt` | Run one prompt and exit |
| `--output-format text\|json\|stream-json` | Output style (JSON has `status`, `response`, `usage`, `conversation_id`) |
| `--json-schema` | Structured output |
| `-c` / `--continue`, `--conversation <id>` | Continue a conversation |
| `--model <slug>` (`agy models` lists them) | Pin a model |
| `--effort low\|medium\|high` | Reasoning effort |
| `--agent <name>` (`agy agents` lists them) | Use a custom agent |
| `--sandbox` | Force sandbox on |
| `--print-timeout 15m` | Default timeout is 5 minutes |
| `--dangerously-skip-permissions` | Approve everything. ⚠️ Avoid |

**Headless safety:** there's no one to click "approve", so actions needing approval are
**soft-denied**. The run continues and exits `0`, with a notice on stderr. So:

1. Pre-approve **only** what the job needs via `permissions.allow` (e.g. `command(git)`,
   `command(regex:npm run (lint|test))`).
2. **Check `status`** in JSON output (`SUCCESS`, `ERROR`, …), not just the exit code.
3. Run interactive `agy` once first so credentials are cached. In CI, an unauthenticated run fails
   with `authentication required` instead of hanging.

```bash
#!/usr/bin/env bash
set -euo pipefail
result=$(agy -p "Review the diff in review.patch for bugs" --output-format json --print-timeout 10m)
[ "$(echo "$result" | jq -r .status)" = "SUCCESS" ] || { echo "$result" | jq -r .error >&2; exit 1; }
echo "$result" | jq -r .response > review.md
```

---

## 2.12 Personalising the CLI

```json
{
  "colorScheme": "tokyo night",
  "editor": "code --wait",
  "editorMode": "vim",
  "verbosity": "low",
  "notifications": true,
  "showTips": false,
  "altScreenMode": "default"
}
```

- `/statusline`: choose what the status bar shows (model, mode, context %, etc.).
- `/title on`: terminal tab title follows the task, which helps with several sessions open.
- `notifications`: get notified when the agent needs approval while you're in another window.

---

## 2.13 Recommended configurations

### 🟢 Beginner — `~/.gemini/antigravity-cli/settings.json`

```json
{
  "toolPermission": "request-review",
  "artifactReviewPolicy": "asks-for-review",
  "agentMode": "plan",
  "allowNonWorkspaceAccess": false,
  "useG1Credits": false,
  "permissions": {
    "allow": ["command(git status)", "command(git diff)", "command(git log)"],
    "deny": [
      "command(rm -rf)", "command(sudo)", "command(git push --force)",
      "command(git reset --hard)", "read_file(.env)", "write_file(.git/)"
    ]
  }
}
```

### 🟡 Productive (macOS/Linux/WSL2)

```json
{
  "toolPermission": "proceed-in-sandbox",
  "enableTerminalSandbox": true,
  "artifactReviewPolicy": "asks-for-review",
  "agentMode": "default",
  "permissions": {
    "allow": [
      "command(git)", "command(regex:npm run (build|lint|test))",
      "read_url(registry.npmjs.org)", "read_url(pypi.org)"
    ],
    "ask": ["unsandboxed(*)", "mcp(*)", "command(git push)"],
    "deny": [
      "command(rm -rf)", "command(sudo)", "command(git push --force)",
      "command(git reset --hard)", "command(terraform apply)", "command(kubectl delete)",
      "read_file(.env)", "write_file(.git/)"
    ]
  }
}
```

### 🔴 CI / automation

Least privilege per job: a dedicated machine user, `-p` with `--output-format json`, an
allow-list of exactly the commands the job needs, `--sandbox`, no production credentials in the
environment, and status checking (§2.11).

---

## 2.14 Gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| `agy: command not found` | Install dir not on `PATH` (or `--skip-path` used) | Add `~/.local/bin` (or `%LOCALAPPDATA%\agy\bin`) to PATH; open a new terminal |
| API key "ignored" | Only `GEMINI_API_KEY` set | Also set `"modelProvider": "gemini"` in settings.json |
| Headless job "succeeds" but did nothing | Needed actions were soft-denied | Add precise `allow` rules; read stderr; check `status` |
| `--permission-mode` errors | Wrong flag name | Use `--mode=plan` / `--mode=accept-edits` |
| Allow rule ignored on Windows | Command not cleanly splittable | Use `command(regex:...)` |
| Command works for you but fails for agent | Sandbox blocks network/paths | Add `read_url(domain)` / `write_file(path)` allows, or approve unsandboxed once |
| Agent seems to "forget" project conventions | No rules file | Add `AGENTS.md` at the repo root (Chapter 03) |
| Quota surprise | Long `/goal` runs, Pro model for everything | `/usage`; Flash for small tasks; keep `useG1Credits` off unless intended |
| Old `/workflow` commands stopped working | Workflows stop working on **19 Oct 2026** | Run `/migrate-workflows` or convert to skills (Chapter 03) |

---

**Next:** [03 — Antigravity Customization: rules, skills, hooks, MCP, subagents ➡️](03-antigravity-customization.md)
