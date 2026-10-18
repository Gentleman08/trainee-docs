# 🤖 AI Coding Agents — Google Antigravity & Claude Code, Safely and Efficiently

> A beginner-first guide to working with **AI coding agents**: tools that read your code, edit
> files and run commands for you. It covers **Google Antigravity** (App/IDE GUI and the `agy`
> CLI) and **Anthropic Claude Code** (CLI and IDE/desktop GUI), with a focus on
> **customizations that make them safe and fast**. No AI or programming experience assumed.

[🏠 Back to Home](../README.md)

---

## 🧭 How to use this guide

1. **Read [Chapter 00 — Fundamentals & Safety](00-fundamentals.md) first.** It covers what agents
   are, the vocabulary, what can go wrong, the safety layers, Git basics, prompting, and your
   first safe session.
2. Then follow the track for your tool. Both tracks share the same structure, so concepts transfer.
3. Finish with **[Chapter 06](06-recipes-comparison.md)**: real scenarios solved in both tools, a
   translation table, troubleshooting and cheat sheets.

> 📝 **Freshness:** written in **October 2026** against the official docs
> (`antigravity.google/docs`, `code.claude.com/docs`). These tools change monthly, so verify
> exact menu labels and flags with `/help`, `agy --help`, `claude --help`.
>
> ⚠️ **Antigravity workflows** (`.agents/workflows/`) **stop working on 19 October 2026.** Use
> **skills** instead ([Chapter 03 §3.5](03-antigravity-customization.md#35-workflows-to-skills-migration)).

---

## 📚 Chapters

| # | Chapter | Covers |
|---|---------|--------|
| 00 | [Fundamentals & Safety](00-fundamentals.md) | Agents vs chatbots, vocabulary, the agent loop, GUI vs CLI, risks, defence in depth, 12 golden rules, Git undo, prompting, first safe session |
| **Antigravity** | | |
| 01 | [Antigravity App & IDE (GUI)](01-antigravity-gui.md) | Install, projects, Agent Manager, local vs worktree, artifacts & review, permission presets, Windows settings, allow/ask/deny rules, strict mode, sandbox, browser safety, recommended setups |
| 02 | [Antigravity CLI (`agy`)](02-antigravity-cli.md) | Install, modes, `settings.json`, `toolPermission`, permission rules, sandbox, slash commands, shortcuts, sessions, headless/CI, recommended configs |
| 03 | [Antigravity Customization](03-antigravity-customization.md) | `AGENTS.md`/rules & triggers, skills, workflows→skills migration, hooks (with blocking examples), MCP, subagents, plugins, repo starter kit |
| **Claude Code** | | |
| 04 | [Claude Code Basics](04-claude-code-basics.md) | Install, GUI options, trust dialog, permission prompts, permission modes, plan mode, commands, shortcuts, checkpoints/rewind, context, sessions, models/cost, Windows notes |
| 05 | [Claude Code Customization](05-claude-code-customization.md) | Settings precedence, permission rules, CLAUDE.md & rules, skills, subagents, hooks (with blocking examples), MCP, plugins, status line, sandbox, headless/CI, copy-paste configs |
| **Both** | | |
| 06 | [Scenarios, Recipes & Comparison](06-recipes-comparison.md) | Rosetta Stone table, 12 recipes (explore, bug fix, feature, review, docs, parallel agents, DevOps, secrets, automation, team rollout, WSL2, cost), red flags, troubleshooting, cheat sheets |

---

## 🔎 Quick lookup — "I want to…"

| I want to… | Antigravity | Claude Code |
|------------|-------------|-------------|
| Install it | [Ch 01 §1.2](01-antigravity-gui.md#12-install-and-sign-in), [Ch 02 §2.1](02-antigravity-cli.md#21-install-verify-sign-in) | [Ch 04 §4.1](04-claude-code-basics.md#41-install-verify-log-in) |
| Make it ask before doing anything risky | [Presets](01-antigravity-gui.md#16-permission-presets-app-macoslinux), [`toolPermission`](02-antigravity-cli.md#25-tool-permission-levels) | [Permission modes](04-claude-code-basics.md#45-permission-modes) |
| Stop it reading secrets | [Rules §1.8](01-antigravity-gui.md#18-writing-allow--ask--deny-rules) | [Rules §5.2](05-claude-code-customization.md#52-permission-rules) |
| Block dangerous commands for sure | [Hooks §3.6](03-antigravity-customization.md#36-hooks) | [Hooks §5.6](05-claude-code-customization.md#56-hooks) |
| Sandbox its commands | [§2.7](02-antigravity-cli.md#27-the-terminal-sandbox) | [§5.10](05-claude-code-customization.md#510-the-bash-sandbox) |
| Teach it my project's conventions | [Rules §3.3](03-antigravity-customization.md#33-rules) | [CLAUDE.md §5.3](05-claude-code-customization.md#53-claudemd-memory-and-rules) |
| Create my own `/command` | [Skills §3.4](03-antigravity-customization.md#34-skills) | [Skills §5.4](05-claude-code-customization.md#54-skills) |
| Connect GitHub/DB/other tools | [MCP §3.7](03-antigravity-customization.md#37-mcp) | [MCP §5.7](05-claude-code-customization.md#57-mcp-servers) |
| Undo the agent's mistake | [§2.10](02-antigravity-cli.md#210-sessions-resume-fork-rewind) | [§4.9](04-claude-code-basics.md#49-undo-checkpoints-rewind-git) |
| Use it in scripts / CI | [§2.11](02-antigravity-cli.md#211-headless-mode-and-automation) | [§5.11](05-claude-code-customization.md#511-headless-mode-scripting-and-ci) |
| Set it up safely on Windows | [§1.7](01-antigravity-gui.md#17-permission-settings-on-windows), [Recipe 11](06-recipes-comparison.md#recipe-11--safe-windows-setup-with-wsl2) | [§4.13](04-claude-code-basics.md#413-windows-specific-notes), [Recipe 11](06-recipes-comparison.md#recipe-11--safe-windows-setup-with-wsl2) |

---

## ✅ The 10 commandments of safe AI-agent use

1. **Commit before every task.** Git is your real undo button.
2. **Plan first.** Plan mode / implementation-plan review for anything non-trivial.
3. **Start cautious, loosen deliberately.** Request Review / Manual → sandboxed auto → never "skip all" on your real machine.
4. **Deny secrets and destructive commands** in permission rules.
5. **Enforce with hooks and sandboxes**, not just polite instructions.
6. **Isolate bigger work** in branches/worktrees, and one task per conversation.
7. **Read every diff and make the agent prove its work** with tests.
8. **Treat web pages, issues and tool output as untrusted** (prompt injection).
9. **Keep production credentials away** from agent sessions.
10. **Share reviewed config in the repo** (`AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`) so the whole team is safe by default.

---

## 🔗 Related notes in this repo

- [AI/ML Notes](../ai-ml-notes/index.md) cover how LLMs, agents and RAG work under the hood
- [CI/CD Pipeline Scenarios](../cicd-pipelines/README.md) cover running agents and security scans in pipelines
- [Git Handbook](../git/git_handbook.md) covers branches, worktrees and recovery

---

[🏠 Back to Home](../README.md)
