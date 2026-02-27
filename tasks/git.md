# Git – Advanced Hands-on & Concepts

---

## 1. Hands on for git force push

### Aim:
Hands on for git force push

Brief:
Practice `git push --force` and `--force-with-lease`, understand risks of overwriting remote history and when it is safe to use.

---

## 2. Hands on for pre-commit hook

### Aim:
Hands on for pre-commit hook

Brief:
Create a `.git/hooks/pre-commit` script to block commits based on custom conditions (lint errors, secret detection, formatting rules).

---

## 3. Hands on for branch protection rule

### Aim:
Hands on for branch protection rule

Brief:
Configure branch protection rules to prevent force pushes, enforce pull request reviews, and require status checks before merging.

---

## 4. Hands on for finding all commit id in which secret are exposed ( redact the secret from remote repository )

### Aim:
Hands on for finding all commit id in which secret are exposed ( redact the secret from remote repository )

Brief:
Identify commits containing sensitive data using `git log` and `git grep`, then rewrite history safely to remove secrets from the remote repository.

---

## 5. Hands on rearranging the commit history

### Aim:
Hands on rearranging the commit history

Brief:
Use interactive rebase (`git rebase -i`) to squash, reorder, edit, or remove commits.

---

## 6. What is signed commit ?

### Aim:
What is signed commit ?

Brief:
Learn how to sign commits using GPG and verify commit authenticity to ensure integrity and trusted authorship.

---

## 7. What is sparse checkout ?

### Aim:
What is sparse checkout ?

Brief:
Understand sparse checkout to clone or checkout only specific directories from a large repository.

---

## 8. How do you push tags to remote?

### Aim:
How do you push tags to remote?

Brief:
Create lightweight and annotated tags and push them using `git push origin <tag>` or `git push --tags`.

---

## 9. How to push large binary files into git repo ( without degrading performance )

### Aim:
How to push large binary files into git repo ( without degrading performance )

Brief:
Use Git LFS (Large File Storage) to manage large binaries efficiently without impacting repository performance.

---

## 10. How do you find which commit introduced a bug?

### Aim:
How do you find which commit introduced a bug?

Brief:
Use `git bisect` to perform a binary search in commit history to identify the commit that introduced the issue.

---

## 11. Repository migration with commit history

### Aim:
Repository migration with commit history

Brief:
Migrate repositories using mirror clone while preserving full commit history, branches, and tags.

---

## 12. Hands on accidental branch deletion and it’s recovery

### Aim:
Hands on accidental branch deletion and it’s recovery

Brief:
Recover deleted branches using `git reflog`, commit hashes, or remote references.

---

## 13. Create a cron which check repositories for changes if there are no changes - log timestamp and no change in log file and if there are changes it should pull automatically and log timestamp and changes which are done ( Make note of merge conflicts and how to tackle it )

### Aim:
Create a cron which check repositories for changes if there are no changes - log timestamp and no change in log file and if there are changes it should pull automatically and log timestamp and changes which are done ( Make note of merge conflicts and how to tackle it )

Brief:
Write a cron job script to:
- Check for remote updates
- Log timestamp
- Auto pull changes
- Log commit differences
- Detect and document merge conflicts
- Define conflict resolution workflow

---

## 14. Create a cron to automate cleanup of merged branches ( only clean branch which name start with temp/)

### Aim:
Create a cron to automate cleanup of merged branches ( only clean branch which name start with temp/)

Brief:
Automate deletion of merged branches that start with `temp/` using a scheduled cleanup script.

---

## 15. Create a cron to automate backup the repository with only 7 days retention period

### Aim:
Create a cron to automate backup the repository with only 7 days retention period

Brief:
Create a scheduled backup script that:
- Archives repository daily
- Maintains 7-day retention
- Automatically deletes older backups