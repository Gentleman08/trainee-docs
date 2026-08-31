[🏠 Home](../README.md) · [Git](README.md)

# 🎭 Git Scenarios — Command Reference

> **Format:** Real situation → exact commands to run → why this works
> **Audience:** DevOps Engineers, Developers hitting real problems
> **Note:** For deep theory, see [git_handbook.md](git_handbook.md)

---

## Table of Contents

1. [Starting Work](#1-starting-work)
2. [Committing](#2-committing)
3. [Branching](#3-branching)
4. [Merging & Rebasing](#4-merging--rebasing)
5. [Undoing Things](#5-undoing-things)
6. [Remote & Collaboration](#6-remote--collaboration)
7. [Stashing](#7-stashing)
8. [Viewing History & Diff](#8-viewing-history--diff)
9. [Tags & Releases](#9-tags--releases)
10. [Disaster Recovery](#10-disaster-recovery)
11. [Conflict Resolution](#11-conflict-resolution)
12. [Searching & Debugging](#12-searching--debugging)
13. [Rewriting History](#13-rewriting-history)
14. [Submodules](#14-submodules)
15. [CI/CD & Automation Scenarios](#15-cicd--automation-scenarios)
16. [Large File & Repo Scenarios](#16-large-file--repo-scenarios)

---

# 1. Starting Work

---

## Scenario 1.1: Clone a repo and immediately set up your identity

**Situation:** You just joined a team. Clone the repo and make sure commits show your work email, not your personal one.

```bash
git clone https://github.com/company/project.git
cd project

# Set identity LOCAL to this repo only (doesn't affect other repos)
git config user.name "Your Name"
git config user.email "you@company.com"

# Verify
git config --list --local
```

**Why:** `--local` sets config only in `.git/config` of this repo. Without it, you might commit with your personal email (from global config) — messy in team history and company audit logs.

---

## Scenario 1.2: Initialize a new repo and push to GitHub

**Situation:** You have a new project folder locally. Set it up as a Git repo and push to a new GitHub repository.

```bash
cd /path/to/project

git init
git add .
git commit -m "Initial commit"

# Connect to remote (create the repo on GitHub first — empty, no README)
git remote add origin https://github.com/yourname/project.git

# Push and set upstream tracking
git push -u origin main
```

**Why:** `git init` creates the `.git` directory (makes it a repo). `-u origin main` sets the upstream so future `git push` / `git pull` don't need arguments — saves typing every time.

---

## Scenario 1.3: Shallow clone for CI/CD (speed up pipelines)

**Situation:** Your CI pipeline is slow because cloning a repo with years of history takes 2 minutes.

```bash
# Clone only the last 1 commit (no history at all)
git clone --depth=1 https://github.com/company/project.git

# Clone only last 10 commits (small history)
git clone --depth=10 https://github.com/company/project.git
```

**Why:** `--depth=1` fetches only the latest snapshot, not the entire history. CI usually only needs to build the latest code — not browse 5 years of commits. Reduces clone time from minutes to seconds for large repos.

> **Gotcha:** Shallow clones break `git describe`, `git log` spanning old commits, and some changelog tools. Don't use for local development — only CI.

---

## Scenario 1.4: Fork a repo, keep fork in sync with upstream

**Situation:** You forked a repo on GitHub. Original repo gets updates. You need to pull those updates into your fork.

```bash
# After cloning YOUR fork:
git remote add upstream https://github.com/original-owner/project.git

# Fetch all upstream changes (without merging)
git fetch upstream

# Merge upstream main into your local main
git checkout main
git merge upstream/main

# Push updated main to your fork on GitHub
git push origin main
```

**Why:** `origin` = your fork. `upstream` = the original repo. Fetching upstream pulls changes into your local tracking branches without affecting your working tree. Then you merge to bring your fork up to date. Essential for long-running forks to avoid huge divergence.

---

# 2. Committing

---

## Scenario 2.1: Stage specific parts of a file (not the whole file)

**Situation:** You modified `app.py` — one change is a feature (should be committed), another is a debug print statement (shouldn't be committed yet).

```bash
git add -p app.py
# Or: git add --patch app.py
```

This opens an interactive prompt for each "hunk" (block of changes):
- `y` — stage this hunk
- `n` — skip this hunk  
- `s` — split into smaller hunks
- `e` — manually edit the hunk
- `q` — quit

**Why:** Clean commits tell a story. Mixing a feature with debug code in one commit makes history noisy, breaks bisect, and makes PRs harder to review. `-p` lets you craft surgical commits.

---

## Scenario 2.2: Amend the last commit (message or content)

**Situation:** You just committed and realized you misspelled the commit message, or forgot to include a file.

```bash
# Fix commit message only
git commit --amend -m "Fixed: correct spelling in commit message"

# Add a forgotten file to the last commit
git add forgotten-file.txt
git commit --amend --no-edit   # --no-edit keeps the existing message
```

**Why:** `--amend` replaces the last commit with a new one (new SHA). The old commit disappears locally. **Only safe if you haven't pushed yet.** If you already pushed, amending creates history divergence — you'd need to force push (dangerous on shared branches).

> **Rule:** Amend freely before pushing. Never amend commits others have already pulled.

---

## Scenario 2.3: Write a good commit message (multi-line)

**Situation:** You need to write a detailed commit message explaining a complex change.

```bash
git commit
# Opens your $EDITOR (usually vim/nano)
```

Format:
```
feat: add Redis caching for user sessions

Previously, every API call re-queried the database for session validation.
This adds a Redis cache layer with 15-minute TTL, reducing DB load by ~60%.

Fixes #234
Co-authored-by: Alice <alice@company.com>
```

**Why:** First line = title (50 chars max, imperative tense). Blank line. Body = why, not what (code shows what; commit explains why). Trailers (`Fixes #234`) auto-close GitHub issues. Good messages make `git log`, `git bisect`, and code archaeology dramatically easier.

---

## Scenario 2.4: Commit with a specific date/time

**Situation:** You did work yesterday but forgot to commit. You want the commit timestamp to reflect when you actually did the work.

```bash
git commit --date="2024-01-15T14:30:00" -m "feat: add payment processing"

# Or relative
git commit --date="yesterday" -m "feat: add payment processing"
```

**Why:** `--date` sets the author date. Git has two timestamps: author date (when the change was made) and committer date (when committed). `--date` sets the author date. Useful for accuracy in project tracking. Note: it doesn't change the actual commit time in the blockchain-like chain — just the metadata.

---

## Scenario 2.5: Sign commits with GPG (for verified commits on GitHub)

**Situation:** Your team/company requires signed commits for security/compliance.

```bash
# One-time setup: tell git which GPG key to use
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true   # Sign all commits automatically

# Or sign a single commit
git commit -S -m "feat: add audit logging"
```

**Why:** Signed commits prove the commit actually came from you — not someone who stole your credentials. GitHub shows a green "Verified" badge. Required by many security-conscious organizations and open source projects.

---

# 3. Branching

---

## Scenario 3.1: Create a branch and start working immediately

**Situation:** You need to start a new feature without affecting main.

```bash
# Method 1: Create and switch (modern)
git switch -c feature/user-auth

# Method 2: Classic equivalent
git checkout -b feature/user-auth

# Method 3: Create from a specific branch/commit
git switch -c hotfix/login-bug origin/main
```

**Why:** Always branch off `main` (or the appropriate base). `-c` = create. `git switch` is the modern command (Git 2.23+) — cleaner than `checkout` which does too many things.

---

## Scenario 3.2: Rename a branch

**Situation:** You named your branch wrong and want to fix it.

```bash
# Rename current branch
git branch -m new-name

# Rename a different branch
git branch -m old-name new-name

# If already pushed: rename local, push new name, delete old remote branch
git branch -m old-name new-name
git push origin -u new-name
git push origin --delete old-name
```

**Why:** `-m` = move/rename. The remote doesn't automatically rename — you must push the new name and delete the old remote branch. Team members who had the old branch checked out will need to update their remote tracking reference.

---

## Scenario 3.3: Delete a branch (local and remote)

**Situation:** Feature is merged, branch is no longer needed.

```bash
# Delete local branch (safe — refuses if not merged)
git branch -d feature/user-auth

# Force delete local branch (merged or not)
git branch -D feature/user-auth

# Delete remote branch
git push origin --delete feature/user-auth

# Or shorter syntax
git push origin :feature/user-auth
```

**Why:** `-d` (lowercase) = safe delete — Git checks if the branch has been merged and refuses if it hasn't. `-D` (uppercase) = force delete regardless. Good habit: always use `-d` first, only use `-D` if you're certain the branch is truly done.

---

## Scenario 3.4: List all branches (local and remote)

**Situation:** You need to see all branches that exist.

```bash
# Local branches only
git branch

# Remote branches only
git branch -r

# Both local and remote
git branch -a

# With last commit info
git branch -av

# Branches already merged into current branch (safe to delete)
git branch --merged main

# Branches NOT yet merged into main
git branch --no-merged main
```

**Why:** `--merged` and `--no-merged` are essential for branch hygiene. Run `git branch --merged main | grep -v main` to find all local branches safe to clean up.

---

## Scenario 3.5: Check out a remote branch that doesn't exist locally

**Situation:** A colleague pushed a branch. You need to work on it locally.

```bash
# Git 2.23+: automatically creates local branch tracking the remote
git switch feature/colleague-work

# Classic way (explicit)
git checkout -b feature/colleague-work origin/feature/colleague-work

# Or using --track
git checkout --track origin/feature/colleague-work
```

**Why:** When you run `git switch feature/colleague-work`, Git sees it doesn't exist locally but finds `origin/feature/colleague-work` and automatically sets up the local tracking branch. The local branch name matches remote by convention.

---

# 4. Merging & Rebasing

---

## Scenario 4.1: Merge a feature branch into main (with a merge commit)

**Situation:** Feature is done, PR is approved, you want to merge preserving the branch history.

```bash
git switch main
git pull origin main          # Make sure main is up to date first!
git merge feature/user-auth

# If no conflicts:
git push origin main

# Force a merge commit even when fast-forward is possible
git merge --no-ff feature/user-auth -m "Merge: add user authentication feature"
```

**Why:** `--no-ff` (no fast-forward) always creates a merge commit, preserving the fact that a feature branch existed. Fast-forward makes history linear (feature commits appear directly on main) — cleaner but loses the branch context. Team preference varies; `--no-ff` is common for explicit merge tracking.

---

## Scenario 4.2: Rebase feature branch onto latest main (before PR)

**Situation:** You started a feature branch a week ago. Main has moved on. You want your feature to sit on top of current main before creating a PR.

```bash
git switch feature/my-feature
git fetch origin
git rebase origin/main

# If conflicts arise during rebase:
# Fix the conflict in the files, then:
git add conflicted-file.py
git rebase --continue

# To abort the rebase and go back to before you started:
git rebase --abort
```

**Why:** Rebase replays your commits on top of the new main. Result: linear history. Your PR diff shows only YOUR changes, not the noise from main diverging. Makes code review easier. Preferred in many teams over merging main into your branch (which creates a confusing "merge main into feature" commit).

> **Gotcha:** Rebase rewrites your commit SHAs. If you've already pushed the branch, you'll need to force push: `git push --force-with-lease origin feature/my-feature`. Never rebase shared/main branches.

---

## Scenario 4.3: Squash merge — combine all feature commits into one

**Situation:** Your feature branch has 20 messy "WIP", "fix typo", "another fix" commits. You want one clean commit on main.

```bash
# Squash all feature branch commits into one commit on main
git switch main
git merge --squash feature/user-auth
git commit -m "feat: add complete user authentication (#PR-123)"
```

**Why:** `--squash` takes all the changes from the feature branch and stages them as a single uncommitted change on main. Then you commit once with a clean message. The feature branch's individual commits disappear from main's history. Clean main history = easier reading, easier bisect.

---

## Scenario 4.4: Cherry-pick a specific commit from another branch

**Situation:** A bug fix was committed to `feature/new-ui`. You need that exact fix on `main` NOW without merging the entire feature branch.

```bash
# Find the commit hash
git log feature/new-ui --oneline

# Cherry-pick it onto your current branch
git cherry-pick abc1234

# Cherry-pick multiple commits
git cherry-pick abc1234 def5678

# Cherry-pick a range
git cherry-pick abc1234..def5678

# Cherry-pick without committing (stage only)
git cherry-pick --no-commit abc1234
```

**Why:** Cherry-pick applies the diff of a specific commit to your current branch as a NEW commit (new SHA). Useful for backporting fixes to release branches or grabbing a single commit without pulling in unfinished work. The original commit remains on its branch — this is a copy.

> **Gotcha:** Cherry-picking the same commit twice creates duplicate changes and messy conflicts during later merges. Track what you've cherry-picked.

---

## Scenario 4.5: Merge only specific files from another branch

**Situation:** Branch `feature/redesign` has updates to `styles.css` and `logo.png` that you want on main, but NOT the JS changes.

```bash
git switch main
git checkout feature/redesign -- styles.css logo.png
# This stages the files at their state in feature/redesign

git commit -m "chore: update styles and logo from redesign branch"
```

**Why:** `git checkout <branch> -- <files>` copies specific files from another branch into your working tree and stages them. It doesn't create a merge relationship — just copies the file state. Useful but use carefully; you lose merge tracking for those files.

---

# 5. Undoing Things

---

## Scenario 5.1: Undo the last commit (keep changes staged)

**Situation:** You committed too soon. You want the commit undone but your changes still ready to recommit.

```bash
git reset --soft HEAD~1
```

**Why:** `--soft` moves HEAD back one commit but leaves the staging area (index) and working tree unchanged. Your files are still staged exactly as they were in the commit. Perfect for "oops, wrong commit message" or "forgot to include a file."

---

## Scenario 5.2: Undo the last commit (keep changes but unstage them)

**Situation:** You committed something you want to rethink. Keep the files changed but start fresh on what to stage.

```bash
git reset HEAD~1
# Or explicitly:
git reset --mixed HEAD~1
```

**Why:** `--mixed` (the default) moves HEAD back and resets the staging area, but leaves your working directory files modified. You'll see the files as unstaged changes. Good when you want to re-examine what you did before committing again.

---

## Scenario 5.3: Completely undo the last commit (discard changes)

**Situation:** You made a commit with test data or something you never want to see again. Nuke it entirely.

```bash
git reset --hard HEAD~1
```

**Why:** `--hard` resets HEAD, staging area, AND working directory to the target commit. Files are gone. No trace in working tree. Dangerous but sometimes exactly what's needed. 

> **Safety net:** The commit still exists in `git reflog` for ~30 days. You can recover it with `git reset --hard <old-sha>` if you regret this.

---

## Scenario 5.4: Undo a pushed commit (public history — use revert)

**Situation:** You pushed a bad commit to main and others have already pulled it. You can't rewrite history.

```bash
# Create a NEW commit that undoes the bad commit
git revert abc1234

# Revert multiple commits
git revert abc1234..def5678

# Revert but don't auto-commit (review first)
git revert --no-commit abc1234
git revert --continue   # after reviewing
```

**Why:** `revert` adds a new commit that applies the inverse diff of the target commit. The bad commit remains in history, but its effect is undone. Safe for shared/public branches because it doesn't rewrite history — everyone's clones remain compatible.

> **Rule:** `reset` = rewrite history (private only). `revert` = undo via new commit (safe for public).

---

## Scenario 5.5: Discard all changes in working directory (start fresh)

**Situation:** You made a mess of changes and want to go back to the last committed state.

```bash
# Discard changes in a specific file
git restore app.py
# Old way: git checkout -- app.py

# Discard ALL unstaged changes
git restore .

# Discard EVERYTHING including staged changes (nuclear option)
git reset --hard HEAD
```

**Why:** `git restore` (Git 2.23+) is the clean, purpose-built command for this. It restores files from the index or a tree. Much clearer than the old `git checkout -- .` which was confusing (checkout does too many things).

---

## Scenario 5.6: Unstage a file (you added it but don't want to commit it yet)

**Situation:** You ran `git add .` and accidentally staged `debug.log` or a config file.

```bash
# Unstage specific file (keeps the file changes intact)
git restore --staged debug.log
# Old way: git reset HEAD debug.log

# Unstage everything
git restore --staged .
```

**Why:** `--staged` tells `restore` to restore from HEAD into the staging area (not the working tree). The file remains modified in your working directory — you just removed it from "to be committed." The old `git reset HEAD <file>` did the same thing but was less intuitive.

---

## Scenario 5.7: Recover a deleted file that was committed

**Situation:** A file was deleted and the deletion was committed 5 commits ago. You need it back.

```bash
# Find when the file was deleted
git log --all --full-history -- path/to/deleted-file.txt

# Get the file from the commit BEFORE the deletion (the parent commit)
git checkout abc1234~1 -- path/to/deleted-file.txt

# Now it's staged; commit to restore it
git commit -m "restore: bring back deleted-file.txt"
```

**Why:** `~1` means "parent of this commit." Since `abc1234` IS the deletion commit, its parent still has the file. `git checkout <tree-ish> -- <file>` copies the file from that point in history into your working tree and stages it.

---

# 6. Remote & Collaboration

---

## Scenario 6.1: Fetch vs Pull — knowing the difference

**Situation:** You want to see what's changed on the remote before bringing it into your branch.

```bash
# FETCH: download remote changes WITHOUT merging into local branches
git fetch origin
# Now you can inspect: git log origin/main
# Compare: git diff main origin/main

# PULL: fetch + merge (or fetch + rebase if configured)
git pull origin main

# Pull with rebase instead of merge (recommended)
git pull --rebase origin main
```

**Why:** `fetch` is safe — it downloads to tracking branches (like `origin/main`) but never touches your local branches. `pull` = `fetch` + `merge` (or rebase). Many engineers prefer always fetching first, reviewing, then deciding how to integrate. This avoids surprise merge commits.

> **Tip:** Set pull to rebase by default: `git config --global pull.rebase true`

---

## Scenario 6.2: Push to remote (first time and subsequent)

**Situation:** Push your branch to the remote for the first time.

```bash
# First push: set upstream tracking
git push -u origin feature/my-feature

# Subsequent pushes (upstream already set):
git push

# Push all branches
git push --all origin

# Push tags
git push --tags
```

**Why:** `-u` (or `--set-upstream`) links your local branch to the remote branch. After this, plain `git push` and `git pull` know where to push/pull without specifying. Saves typing.

---

## Scenario 6.3: Force push safely (after rebase)

**Situation:** You rebased your feature branch and need to push. Normal push is rejected because history was rewritten.

```bash
# SAFE force push (fails if someone else pushed since you last fetched)
git push --force-with-lease origin feature/my-feature

# UNSAFE force push (NEVER use on shared branches)
git push --force origin feature/my-feature
```

**Why:** `--force-with-lease` checks that your remote tracking branch is still at the same commit you last fetched. If someone else pushed while you were rebasing, it FAILS — protecting their work. `--force` overwrites whatever is there, potentially destroying a teammate's commits. Always use `--force-with-lease`.

---

## Scenario 6.4: Update your local list of remote branches

**Situation:** A colleague deleted a remote branch but it still shows in your `git branch -r`.

```bash
# Prune remote-tracking branches that no longer exist on the remote
git fetch --prune
# Or: git remote prune origin

# Auto-prune on every fetch (recommended setting)
git config --global fetch.prune true
```

**Why:** Your local remote-tracking branches (like `origin/feature/old-branch`) are just references. When the remote branch is deleted, your local reference becomes stale. `--prune` removes these stale references. Without this, `git branch -r` becomes cluttered with dead branches.

---

## Scenario 6.5: Work with multiple remotes

**Situation:** You need to push to both GitHub (origin) and an internal GitLab server.

```bash
# Add a second remote
git remote add gitlab https://gitlab.company.com/team/project.git

# List all remotes
git remote -v

# Push to specific remote
git push gitlab main
git push origin main

# Push to all remotes at once (add a push URL to origin)
git remote set-url --add --push origin https://gitlab.company.com/team/project.git
git push origin main  # now pushes to BOTH GitHub and GitLab
```

**Why:** Multiple remotes are common in organizations that mirror repos, maintain backups, or use different services for different purposes (GitHub for open source, GitLab for internal). `set-url --add --push` lets you push to multiple places with one command.

---

## Scenario 6.6: Pull a PR / Merge Request branch to test locally

**Situation:** A colleague's PR is under review. You want to test it locally without merging.

```bash
# GitHub: Pull the PR branch by PR number
git fetch origin pull/123/head:pr-123
git switch pr-123

# GitLab: Pull MR branch
git fetch origin merge-requests/456/head:mr-456
git switch mr-456

# If you know the branch name:
git fetch origin feature/their-branch:feature/their-branch
git switch feature/their-branch
```

**Why:** GitHub/GitLab keep PR/MR branches in special refs (`pull/*/head`). Fetching them creates a local branch you can test without affecting your own work. You never need to ask the author to share the branch name this way.

---

# 7. Stashing

---

## Scenario 7.1: Save work in progress without committing

**Situation:** You're mid-feature and someone needs you to fix an urgent bug on main RIGHT NOW.

```bash
# Stash everything (tracked files only)
git stash

# Stash with a descriptive name (recommended)
git stash push -m "WIP: user auth validation logic"

# Stash including untracked files
git stash push -u -m "WIP: user auth"

# Stash including untracked AND ignored files
git stash push -a -m "WIP: user auth"

# After fixing the bug, restore your stash:
git stash pop       # apply and remove from stash list
# Or:
git stash apply     # apply but KEEP in stash list (safe)
```

**Why:** Stash is a temporary save slot. `pop` = apply + delete. `apply` = apply only (the stash remains so you can apply it multiple times or to other branches). Use named stashes — without names, `git stash list` becomes meaningless after a few entries.

---

## Scenario 7.2: Manage multiple stashes

**Situation:** You have several things stashed and need to apply a specific one.

```bash
# List all stashes
git stash list
# Output:
# stash@{0}: On main: WIP: user auth validation logic
# stash@{1}: On feature/ui: WIP: new button styles
# stash@{2}: On main: WIP: db migration script

# Apply a specific stash by index
git stash apply stash@{1}

# Drop a specific stash
git stash drop stash@{2}

# Apply the most recent and drop it
git stash pop

# Clear all stashes (destructive!)
git stash clear
```

**Why:** Stash is a stack, but you can access any item by index. `stash@{0}` is always the most recent. Descriptive names (from `-m`) are critical here — without them, `stash@{1}` tells you nothing.

---

## Scenario 7.3: Stash only specific files

**Situation:** You have changes to 5 files. You want to stash only 2 of them.

```bash
git stash push -m "WIP: config changes" config.yaml settings.py
```

**Why:** `git stash push` accepts file paths at the end. Only those files are stashed; the rest remain in your working tree. Useful when you want to quickly test without certain changes but don't want to lose them.

---

## Scenario 7.4: Create a branch from a stash

**Situation:** You stashed some work. Now you realize it should be its own branch, not continuation of current work.

```bash
# Create a new branch from the stash point and apply the stash
git stash branch feature/new-idea stash@{0}
```

**Why:** This creates a new branch at the commit where you originally stashed, applies the stash to it, and drops the stash. Avoids the common problem of stash conflicts when your branch has moved on since you stashed.

---

# 8. Viewing History & Diff

---

## Scenario 8.1: Pretty-print the git log

**Situation:** The default `git log` output is too verbose. You want a clean view.

```bash
# One line per commit
git log --oneline

# With branch graph
git log --oneline --graph --all --decorate

# Last 10 commits
git log -10 --oneline

# Commits by a specific author
git log --author="Alice" --oneline

# Commits in a date range
git log --since="2024-01-01" --until="2024-01-31" --oneline

# Commits that touched a specific file
git log --oneline -- path/to/file.py

# Commits with the actual diff (patch)
git log -p --oneline

# Useful alias to set up:
git config --global alias.lg "log --oneline --graph --all --decorate --color"
# Usage: git lg
```

**Why:** `--graph` draws ASCII art of the branch/merge topology. `--all` shows all branches (not just current). `--decorate` shows branch names and tags next to commits. This one-liner is arguably the most useful git command you can put in your muscle memory.

---

## Scenario 8.2: See what changed in a specific commit

**Situation:** You want to see exactly what files and lines changed in commit `abc1234`.

```bash
# Show the full diff of a commit
git show abc1234

# Show only the files changed (not the diff)
git show --stat abc1234
git show --name-only abc1234

# Show a specific file's change in that commit
git show abc1234:path/to/file.py     # file AS it was in that commit
git show abc1234 -- path/to/file.py  # diff of that file in that commit
```

**Why:** `git show` is the go-to for inspecting a specific commit. `--stat` gives a quick summary. Combining `git log` to find the commit + `git show` to inspect it is the standard debugging workflow.

---

## Scenario 8.3: Compare two branches

**Situation:** You want to see what commits are on `feature/my-feature` that aren't on `main`.

```bash
# Commits on feature/my-feature NOT in main
git log main..feature/my-feature --oneline

# Commits in EITHER but not BOTH (symmetric difference)
git log main...feature/my-feature --oneline

# Actual file diff between branches
git diff main..feature/my-feature

# Files changed (summary only)
git diff --stat main..feature/my-feature

# Specific file diff between branches
git diff main..feature/my-feature -- app.py
```

**Why:** `..` (two dots) = commits reachable from right but NOT from left. `...` (three dots) = commits in either but not the common ancestor. For branch comparison, `..` is what you usually want: "what does this branch add?"

---

## Scenario 8.4: Find who changed a specific line (blame)

**Situation:** A bug is on line 42 of `auth.py`. Who wrote it and when?

```bash
# Show line-by-line authorship
git blame auth.py

# Blame a specific line range
git blame -L 35,55 auth.py

# Ignore whitespace changes
git blame -w auth.py

# Show the email instead of name
git blame --show-email auth.py

# Follow lines through file renames and moves
git blame -C auth.py
```

**Why:** `git blame` annotates every line with the commit SHA, author, and date that last modified it. Essential for understanding "who decided this?" or "when was this added?" The SHA it shows lets you `git show <sha>` for full context. `-C` detects copied code — useful when code was moved from another file.

---

## Scenario 8.5: See what files changed between two commits/branches/tags

```bash
# Files changed between two commits
git diff --name-only HEAD~5 HEAD

# Files changed between two branches
git diff --name-only main feature/my-feature

# With change type (A=added, M=modified, D=deleted)
git diff --name-status main feature/my-feature

# Between two tags
git diff --name-only v1.0 v1.1
```

**Why:** `--name-only` is gold for automation scripts. In CI/CD you often need to know WHAT changed to decide which tests to run or which deployments to trigger. `--name-status` adds the type prefix (A/M/D) which is even more useful for conditional logic.

---

# 9. Tags & Releases

---

## Scenario 9.1: Create a release tag

**Situation:** You're releasing v2.1.0. Tag the commit and push it.

```bash
# Lightweight tag (just a pointer, no metadata)
git tag v2.1.0

# Annotated tag (recommended — has metadata, message, GPG-signable)
git tag -a v2.1.0 -m "Release v2.1.0: add payment processing"

# Tag a specific commit (not HEAD)
git tag -a v2.0.1 abc1234 -m "Hotfix: fix auth bypass vulnerability"

# Push tags to remote (they're NOT pushed by default!)
git push origin v2.1.0      # push specific tag
git push origin --tags       # push all tags
```

**Why:** Annotated tags (`-a`) store the tagger name, email, date, and message — unlike lightweight tags which are just pointers. GitHub uses annotated tags for release notes. `git describe` works better with annotated tags. **Always push tags explicitly** — `git push` doesn't push tags by default, which trips up many people.

---

## Scenario 9.2: List and delete tags

```bash
# List all tags
git tag

# List tags matching a pattern
git tag -l "v2.*"

# Show tag details
git show v2.1.0

# Delete local tag
git tag -d v2.1.0-beta

# Delete remote tag
git push origin --delete v2.1.0-beta
# Or:
git push origin :refs/tags/v2.1.0-beta
```

**Why:** Deleting a tag locally doesn't remove it from the remote. You must explicitly push the deletion. The `:refs/tags/...` syntax means "push nothing to this ref" = delete.

---

## Scenario 9.3: Checkout code at a specific tag (read-only)

**Situation:** You need to reproduce a bug that existed in v1.5.2.

```bash
# Detached HEAD — you're now AT that tag, read-only
git checkout v1.5.2

# Better: create a branch if you want to make changes
git switch -c hotfix/v1.5.2-fix v1.5.2
```

**Why:** Checking out a tag puts you in "detached HEAD" state — you're not on any branch. Any commits you make here are orphaned (not on a branch). If you need to fix something, always create a branch first. Detached HEAD is fine for just looking/testing.

---

# 10. Disaster Recovery

---

## Scenario 10.1: Recover a deleted branch

**Situation:** You accidentally deleted a branch that hadn't been merged yet.

```bash
# Find the lost commit SHA using reflog
git reflog
# Look for: "abc1234 HEAD@{3}: checkout: moving from deleted-branch to main"

# Recreate the branch at that SHA
git branch recovered-branch abc1234

# Or switch to it immediately
git switch -c recovered-branch abc1234
```

**Why:** `reflog` is Git's safety net — it records every movement of HEAD for ~90 days. When you delete a branch, the commits still exist (as orphaned objects) until garbage collection runs. `reflog` shows you the SHAs you need to rescue them. **This is the most important Git recovery command.**

---

## Scenario 10.2: Recover from a bad `git reset --hard`

**Situation:** You ran `git reset --hard HEAD~5` and lost 5 commits you actually needed.

```bash
# Find the SHA of where you were BEFORE the reset
git reflog
# Look for: "abc1234 HEAD@{1}: commit: feat: add the thing I need"

# Reset back to where you were
git reset --hard abc1234
```

**Why:** `reset --hard` moves HEAD and clears the working tree, but doesn't delete commits immediately. Reflog records the old HEAD position. The commits are still accessible via their SHA for ~90 days. This is why reflog is often called "git's undo history."

---

## Scenario 10.3: Find a commit that broke something (git bisect)

**Situation:** The app worked 3 weeks ago. Something broke it. There are 150 commits between then and now. Which commit broke it?

```bash
# Start bisect
git bisect start

# Mark current state as bad
git bisect bad

# Mark a known good commit (3 weeks ago)
git bisect good v2.0.0
# Or: git bisect good abc1234

# Git will checkout a commit halfway between — test it
# If bug is present:
git bisect bad
# If bug is NOT present:
git bisect good

# Git keeps narrowing down (binary search: ~7 steps for 150 commits)
# When done, Git shows the first bad commit
git bisect reset  # return to original branch

# Automate with a test script
git bisect start
git bisect bad HEAD
git bisect good v2.0.0
git bisect run ./run_test.sh   # script exits 0 = good, non-0 = bad
```

**Why:** Binary search finds the bad commit in O(log n) steps. 150 commits = 7–8 steps. Without bisect, manual hunting would take hours. With `bisect run`, it's fully automated — Git checks out each commit and runs your test script automatically. **This is the correct professional approach to regression hunting.**

---

## Scenario 10.4: Undo a merge commit

**Situation:** You merged a feature branch into main and it broke production. You need to undo the merge.

```bash
# Find the merge commit SHA and its parent number
git log --oneline
# abc1234 Merge branch 'feature/broken' into main  ← this is the merge commit

# Revert the merge commit (specify parent 1 = main side of the merge)
git revert -m 1 abc1234
# -m 1 means: revert to the first parent (main before the merge)
git push origin main
```

**Why:** A merge commit has two parents. `-m 1` says "restore to the state of parent 1" (the branch you merged INTO, i.e., main before the merge). `-m 2` would restore to the feature branch tip. This creates a revert commit — safe for shared/public branches. 

> **Gotcha after revert:** If you later try to re-merge the feature branch (after fixing it), Git thinks all those changes are already incorporated (they're in history). You'd need to `git revert` the revert commit first.

---

## Scenario 10.5: Rescue uncommitted changes after a crash/force reset

**Situation:** You had uncommitted work in progress. The terminal crashed (or someone ran `git reset --hard`). Can you get it back?

```bash
# Git's object store keeps dangling blobs for a while
# Find recently referenced blobs
git fsck --lost-found
# Creates files in .git/lost-found/

# Or search reflog for any recent activity
git reflog --all

# List dangling commits (may contain your work)
git fsck --dangling | grep "dangling commit" | awk '{print $3}' | \
    xargs -I{} git show {}
```

**Why:** Git only garbage-collects (`gc`) periodically. Unreachable objects (dangling blobs, commits) persist temporarily. `fsck --lost-found` dumps them to `.git/lost-found/` for inspection. This is a last resort — uncommitted work that was never staged has much lower chance of recovery, but staged work (even if reset) often can be recovered this way.

---

# 11. Conflict Resolution

---

## Scenario 11.1: Understand a conflict and resolve it

**Situation:** Git stopped mid-merge with a conflict.

```bash
# See which files have conflicts
git status
# Both modified:  src/auth.py

# Open the conflicted file — look for conflict markers:
# <<<<<<< HEAD
# (your version)
# =======
# (their version)
# >>>>>>> feature/their-branch
```

Resolution steps:
```bash
# Option 1: Use a merge tool
git mergetool           # Opens configured merge tool (vimdiff, VS Code, etc.)

# Option 2: Manually edit the file to resolve, then:
git add src/auth.py
git commit              # Completes the merge

# Option 3: Accept one side entirely
git checkout --ours src/auth.py    # Keep YOUR version
git checkout --theirs src/auth.py  # Keep THEIR version
git add src/auth.py
git commit
```

**Why:** Conflict markers show both versions — you must choose what the final version should be (could be either, or a combination). `--ours`/`--theirs` are shortcuts when you know one side is completely correct. After resolving, `git add` marks the conflict resolved; then `git commit` (or `git rebase --continue` if rebasing) finishes.

---

## Scenario 11.2: Abort a merge or rebase mid-conflict

**Situation:** The conflict is too complex. You want to go back to before the merge/rebase started.

```bash
# Abort a merge
git merge --abort

# Abort a rebase
git rebase --abort

# Abort a cherry-pick
git cherry-pick --abort
```

**Why:** These commands restore your repo to the state it was in BEFORE the operation started. Clean slate. All your tracked files go back to pre-operation state. Use this when the conflict resolution would take too long and you need to discuss strategy with the team first.

---

## Scenario 11.3: Configure a merge tool (VS Code)

**Situation:** You want VS Code to open for conflict resolution instead of the terminal.

```bash
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# For diff tool:
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
```

**Why:** Visual merge tools are much easier than manually editing conflict markers in a terminal editor. VS Code, IntelliJ, and vimdiff are popular choices. `--wait` tells code to block until you close the file — needed so Git knows when you've finished resolving.

---

# 12. Searching & Debugging

---

## Scenario 12.1: Search for a string in all commits (ever)

**Situation:** "When did we remove the `legacy_auth` function? It was there at some point."

```bash
# Search all commit history for when a string was added or removed
git log -S "legacy_auth" --oneline

# Regex search
git log -G "legacy_auth.*function" --oneline

# Show the actual diff where the string appeared/disappeared
git log -S "legacy_auth" -p --oneline
```

**Why:** `-S` (pickaxe) finds commits where the number of occurrences of the string changed — i.e., where it was added or deleted. `-G` uses regex and finds commits where any line in the diff matches. Invaluable for "when was this added?", "when did this function disappear?", or finding deleted code.

---

## Scenario 12.2: Search for a string in current code across the repo

**Situation:** You need to find every file that uses `AWS_SECRET_KEY`.

```bash
# Search current working tree
git grep "AWS_SECRET_KEY"

# Case-insensitive
git grep -i "aws_secret"

# Show line numbers
git grep -n "AWS_SECRET_KEY"

# Search all branches (not just current checkout)
git grep "AWS_SECRET_KEY" $(git rev-list --all)

# Only show filenames
git grep -l "AWS_SECRET_KEY"
```

**Why:** `git grep` is faster than `grep -r` on large repos because it only searches tracked files (skipping `.git/`, build artifacts, etc.) and uses Git's optimized object store. `git rev-list --all` searches across all commits — useful for finding secrets that may have been removed from current code but exist in history.

---

## Scenario 12.3: Find which commit introduced a file

**Situation:** "When was `Dockerfile` first added to this repo?"

```bash
# Find the commit that ADDED the file
git log --diff-filter=A --oneline -- Dockerfile

# Find the commit that DELETED a file
git log --diff-filter=D --oneline -- old-script.sh

# Find commits that RENAMED a file
git log --diff-filter=R --oneline --summary

# Filter codes: A=Added, M=Modified, D=Deleted, R=Renamed, C=Copied
```

**Why:** `--diff-filter` limits `git log` to commits where the file changed in a specific way. Much faster than reading through all logs manually.

---

# 13. Rewriting History

---

## Scenario 13.1: Interactive rebase — clean up commits before a PR

**Situation:** Your feature branch has 8 commits: some "WIP", some "fix typo", some "oops". You want to combine them into 3 clean commits before opening a PR.

```bash
# Rebase the last 8 commits interactively
git rebase -i HEAD~8

# Or rebase against the branch you'll merge into
git rebase -i origin/main
```

In the editor that opens:
```
pick abc1234 feat: scaffold user auth
squash def5678 WIP: working on auth
squash ghi9012 fix typo in auth
pick jkl3456 feat: add JWT token generation
squash mno7890 oops forgot import
pick pqr1234 test: add auth unit tests
```

Commands:
- `pick` — keep commit as-is
- `squash` / `s` — combine with the previous commit (prompts for new message)
- `fixup` / `f` — combine with previous, discard this commit's message
- `reword` / `r` — keep commit but edit its message
- `drop` / `d` — delete this commit entirely
- `edit` / `e` — pause here to amend the commit

**Why:** Interactive rebase lets you craft a clean, logical commit history before it becomes permanent (merged into main). PR reviewers see clean commits = faster reviews. Also useful for splitting one giant commit into multiple focused ones.

---

## Scenario 13.2: Remove a secret from ALL git history (emergency)

**Situation:** Someone accidentally committed an API key or password. It's been pushed. You need to scrub it from all history.

```bash
# OPTION 1: git-filter-repo (recommended modern tool)
pip install git-filter-repo

git filter-repo --path secrets.env --invert-paths  # Remove entire file from history
# Or replace the secret value:
git filter-repo --replace-text <(echo 'API_KEY=sk-1234abcd==>API_KEY=REDACTED')

# OPTION 2: BFG Repo Cleaner (Java, easier for simple cases)
# Download bfg.jar from https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files secrets.env
java -jar bfg.jar --replace-text passwords.txt  # file with "secret==>REDACTED"

# After either tool: force push ALL branches
git push origin --force --all
git push origin --force --tags
```

**Why:** Once a secret is in git history, it's accessible to anyone with clone access — even if the file is later deleted. The secret must be scrubbed from ALL commits in ALL branches. After cleaning, you must ALSO rotate the secret (assume it was compromised). GitHub has "secret scanning" that will alert you if known secret formats appear in pushes.

> **Critical:** Force-pushing rewrites history. All collaborators must delete their local clones and re-clone. Coordinate with the team.

---

## Scenario 13.3: Split a large commit into smaller ones

**Situation:** You have one giant commit with 5 unrelated changes. You want to split it into 5 separate commits.

```bash
# Start interactive rebase at that commit
git rebase -i HEAD~1   # (if it's the last commit)

# Mark the commit as 'edit':
# edit abc1234 feat: big commit with everything

# Git pauses at that commit
# Reset to the previous commit's state (unstages everything from this commit)
git reset HEAD~1

# Now stage and commit piece by piece:
git add auth.py
git commit -m "feat: add authentication"

git add -p api.py   # stage only specific parts
git commit -m "feat: add API endpoints"

# Continue rebase when done splitting
git rebase --continue
```

**Why:** `edit` in interactive rebase pauses at that commit. `reset HEAD~1` keeps all the file changes but uncommits them, letting you re-commit them in smaller pieces. Then `--continue` finishes the rebase with your new split commits.

---

# 14. Submodules

---

## Scenario 14.1: Add a submodule to a project

**Situation:** You want to include a shared library from another git repo inside your project.

```bash
git submodule add https://github.com/company/shared-lib.git libs/shared-lib
git commit -m "chore: add shared-lib submodule"
```

This creates:
- `libs/shared-lib/` — the library code
- `.gitmodules` — configuration file tracking submodule URLs

**Why:** Submodules let you embed one Git repo inside another. The parent repo stores only the submodule URL and the pinned commit SHA — not the actual code. Other developers clone the parent repo and get a reference to the submodule but must explicitly initialize it.

---

## Scenario 14.2: Clone a repo that has submodules

**Situation:** You cloned a repo and the submodule folders are empty.

```bash
# Clone with submodules in one command
git clone --recurse-submodules https://github.com/company/project.git

# If you already cloned without --recurse-submodules:
git submodule init
git submodule update
# Or in one step:
git submodule update --init --recursive
```

**Why:** `git clone` by default does NOT download submodule content — only the reference. The submodule directory is created but empty. `--recurse-submodules` (or the two-step `init` + `update`) fetches the submodule's code at the pinned commit.

---

## Scenario 14.3: Update a submodule to its latest version

**Situation:** The shared library released a new version. You want to update your submodule to use it.

```bash
# Go into the submodule and pull
cd libs/shared-lib
git pull origin main

# Go back to parent repo and commit the updated reference
cd ../..
git add libs/shared-lib
git commit -m "chore: update shared-lib to latest main"
```

**Why:** The parent repo stores the pinned SHA of the submodule. Changing that SHA (by pulling inside the submodule dir) is what "updating" means. You must then commit in the parent repo to save the new pinned SHA. Other developers run `git submodule update` to move to the new pinned commit.

---

# 15. CI/CD & Automation Scenarios

---

## Scenario 15.1: Get information about the current state in CI

**Situation:** In your CI pipeline script, you need the current branch name, commit SHA, and tag (if any).

```bash
# Current commit SHA (full)
git rev-parse HEAD

# Short SHA (7 chars — common for Docker image tags)
git rev-parse --short HEAD

# Current branch name
git branch --show-current
# Or:
git rev-parse --abbrev-ref HEAD

# Tag for this commit (if any)
git describe --exact-match --tags HEAD 2>/dev/null || echo "no tag"

# All tags pointing to this commit
git tag --points-at HEAD

# Describe: nearest tag + commits since + short SHA
git describe --tags --always

# Example: use in Docker build
IMAGE_TAG=$(git rev-parse --short HEAD)
docker build -t myapp:${IMAGE_TAG} .
```

**Why:** CI/CD pipelines need Git metadata to tag images, name artifacts, and track what version is deployed. `rev-parse --short HEAD` is the universal way to get a reproducible, unique version identifier.

---

## Scenario 15.2: Conditionally run steps based on what changed

**Situation:** In CI, only run backend tests if backend files changed; only build frontend if frontend files changed.

```bash
# Files changed in the last commit
git diff --name-only HEAD~1 HEAD

# Files changed between current commit and a specific branch
git diff --name-only origin/main...HEAD

# Check if specific paths changed (exit code 1 if no changes, 0 if yes)
git diff --name-only HEAD~1 HEAD | grep -q "^backend/"
if [ $? -eq 0 ]; then
    echo "Backend changed — running backend tests"
    cd backend && npm test
fi

# In a more robust form:
CHANGED_FILES=$(git diff --name-only origin/main...HEAD)
if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
    npm run build:frontend
fi
```

**Why:** Selective CI is massive for pipeline speed in monorepos. Instead of running everything for every commit, you only build/test what changed. `origin/main...HEAD` (three dots) gives all commits in the PR that aren't in main.

---

## Scenario 15.3: Create a changelog from git log

**Situation:** You want to auto-generate a changelog from commit messages for a release.

```bash
# All commits between two tags
git log v1.0.0..v1.1.0 --oneline

# Formatted for a changelog
git log v1.0.0..v1.1.0 \
    --pretty=format:"- %s (%h, %an)" \
    --no-merges

# Group by type (assuming conventional commits: feat:, fix:, chore:)
echo "## Features"
git log v1.0.0..v1.1.0 --oneline --no-merges | grep "^feat:"

echo "## Bug Fixes"
git log v1.0.0..v1.1.0 --oneline --no-merges | grep "^fix:"

# Tools that automate this:
# - conventional-changelog-cli
# - git-cliff
# - semantic-release
```

**Why:** Commit messages following Conventional Commits format (`feat:`, `fix:`, `chore:`, `break:`) enable automated changelogs and semantic versioning. `git log` between tags gives all changes in that release.

---

## Scenario 15.4: Ensure the branch is clean before deploying

**Situation:** In your deploy script, you want to abort if there are uncommitted changes.

```bash
#!/bin/bash
# Check for uncommitted changes
if ! git diff --quiet; then
    echo "ERROR: Uncommitted changes detected. Commit or stash before deploying."
    exit 1
fi

# Check for untracked files
if [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "WARNING: Untracked files detected."
fi

# Check if we're on the expected branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "ERROR: Deployments must be from main. Current branch: $CURRENT_BRANCH"
    exit 1
fi

echo "✅ Repository is clean. Proceeding with deployment."
```

**Why:** `git diff --quiet` exits with 0 if no changes, 1 if there are changes — perfect for scripting. Deploying from a dirty working tree is a footgun: you might deploy code that isn't committed, making the deployment unreproducible and unauditable.

---

# 16. Large File & Repo Scenarios

---

## Scenario 16.1: Stop tracking a file that's already committed (e.g., add to .gitignore)

**Situation:** You committed `node_modules/` or `*.log` files. You added them to `.gitignore` but Git still tracks them.

```bash
# Remove from tracking (but keep the file locally)
git rm --cached node_modules/ -r
git rm --cached "*.log" -r
# Or remove everything and re-add:
git rm --cached . -r
git add .

# Now commit the .gitignore and the removal
git commit -m "chore: stop tracking node_modules and logs"

# Push
git push
```

**Why:** `.gitignore` only prevents FUTURE tracking of untracked files. It has no effect on files already being tracked by Git. `git rm --cached` removes files from Git's index (stops tracking) without deleting them from disk. After committing, Git will ignore changes to those files.

---

## Scenario 16.2: Use Git LFS for large binary files

**Situation:** Your repo has PSD files, videos, or trained ML models that make the repo huge.

```bash
# Install Git LFS
git lfs install

# Track large file types
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "models/*.bin"

# This creates/updates .gitattributes
git add .gitattributes
git commit -m "chore: configure LFS for large files"

# Now add large files normally — LFS handles them transparently
git add model.bin
git commit -m "add trained model v2"
git push
```

**Why:** LFS (Large File Storage) stores large binary files on an LFS server (separate from the Git object store) and replaces them in the repo with small text pointers. The repo stays fast to clone (small), and LFS downloads large files only when needed. Supported by GitHub, GitLab, Bitbucket.

---

## Scenario 16.3: Check what's making your repo large

**Situation:** Your repo is 2 GB. You want to find what's taking so much space.

```bash
# See total pack size
git count-objects -vH

# Find the largest objects in git history
git rev-list --objects --all \
    | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
    | awk '/^blob/ {print substr($0,6)}' \
    | sort -k2 -rn \
    | head -20

# More user-friendly with git-sizer (install separately)
git-sizer --verbose
```

**Why:** Large repos are often caused by accidentally committed binary files, old database dumps, or build artifacts that were removed from the latest code but still live in history (Git never deletes committed data automatically). This analysis finds them so you can use `git filter-repo` to remove them.

---

## Quick Reference Card

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  GIT SCENARIO QUICK REFERENCE                                         │
  │                                                                       │
  │  UNDO CHEATSHEET:                                                     │
  │  Unstage file:        git restore --staged <file>                    │
  │  Discard changes:     git restore <file>                             │
  │  Undo last commit     git reset --soft HEAD~1  (keep staged)        │
  │  (not pushed):        git reset HEAD~1          (keep unstaged)      │
  │                       git reset --hard HEAD~1   (nuke it)           │
  │  Undo pushed commit:  git revert <sha>           (safe)              │
  │                                                                       │
  │  RECOVERY:                                                            │
  │  Lost branch:         git reflog → git branch name <sha>            │
  │  Lost commit:         git reflog → git reset --hard <sha>           │
  │  Find bug commit:     git bisect start/bad/good/run                  │
  │                                                                       │
  │  HISTORY INSPECTION:                                                  │
  │  Visual log:          git log --oneline --graph --all                │
  │  File history:        git log --follow -p -- <file>                  │
  │  Who changed line:    git blame <file>                               │
  │  Search history:      git log -S "string"                            │
  │  Commit diff:         git show <sha>                                 │
  │                                                                       │
  │  BRANCH HYGIENE:                                                      │
  │  Merged branches:     git branch --merged main                       │
  │  Delete local:        git branch -d <branch>                        │
  │  Delete remote:       git push origin --delete <branch>             │
  │  Prune stale remote:  git fetch --prune                              │
  │                                                                       │
  │  FORCE PUSH SAFELY:   git push --force-with-lease (not --force)     │
  │  MERGE VS REBASE:     merge = preserve history; rebase = linear      │
  │  REVERT VS RESET:     revert = safe (new commit); reset = rewrite    │
  └──────────────────────────────────────────────────────────────────────┘
```

---

*Cross-reference: [git_handbook.md](git_handbook.md) for deep internals and theory*
