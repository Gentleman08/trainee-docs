[🏠 Home](../README.md) · [Linux](README.md)

# 🔧 Linux CLI Power Tools — DevOps Handbook

> **Audience:** DevOps / Cloud Engineers | **Level:** Basic → Intermediate → Advanced
> Short explanations. Real scenarios. Command combinations that actually appear on the job.
> **Tools covered:** Regex · grep · sed · awk · curl · wget · journalctl

---

## Table of Contents

1. [Regex Foundations](#chapter-1-regex-foundations)
2. [grep — Search & Filter](#chapter-2-grep--search--filter)
3. [sed — Stream Editor](#chapter-3-sed--stream-editor)
4. [awk — Text Processing Language](#chapter-4-awk--text-processing-language)
5. [curl — HTTP Client](#chapter-5-curl--http-client)
6. [wget — Download Tool](#chapter-6-wget--download-tool)
7. [journalctl — Systemd Journal](#chapter-7-journalctl--systemd-journal)
8. [Combo Scenarios — Real-World Pipelines](#chapter-8-combo-scenarios--real-world-pipelines)

---

# Chapter 1: Regex Foundations

> **Why first?** grep, sed, and awk all use regex. Learn it once — apply it everywhere.

## 1.1 What is Regex?

Regex (Regular Expression) is a pattern language for matching text. Instead of saying "find the word ERROR", you describe the shape of what you want to find.

```
  Plain text search:  "error"      ← matches only the literal word "error"
  Regex search:       "err[oa]r"   ← matches "error" AND "errar"
  Regex search:       "\bERR\w+"   ← matches any word starting with ERR (ERROR, ERRAND...)
```

Think of regex as a mini-language that describes text shapes, not specific text.

---

## 1.2 Regex Flavors — Which Tools Use What

This is critical. A pattern that works in Python may not work in grep.

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  REGEX FLAVORS                                                        │
  │                                                                       │
  │  BRE (Basic Regular Expressions)                                     │
  │  ├── Used by: grep (default), sed (default)                          │
  │  ├── + ? { } | ( ) must be ESCAPED to be special: \+ \? \{ \| \(    │
  │  └── Examples: grep "a\+" file,  sed 's/\(foo\)/[\1]/'              │
  │                                                                       │
  │  ERE (Extended Regular Expressions)                                  │
  │  ├── Used by: grep -E / egrep, sed -E, awk (always ERE)             │
  │  ├── + ? { } | ( ) are special WITHOUT escaping                     │
  │  └── Examples: grep -E "a+" file,  awk '/a+/ {print}'               │
  │                                                                       │
  │  PCRE (Perl Compatible Regular Expressions)                          │
  │  ├── Used by: grep -P, Python re, JavaScript, PHP                   │
  │  ├── Adds: \d \w \s lookahead (?=...) lookbehind (?<=...) etc.      │
  │  └── Examples: grep -P "\d{4}-\d{2}-\d{2}" file                    │
  │                                                                       │
  │  Rule: Use -E always for grep and sed. It's cleaner.                 │
  └──────────────────────────────────────────────────────────────────────┘
```

---

## 1.3 Anchors

Anchors match a POSITION, not a character.

| Anchor | Matches | Example | Matches |
|--------|---------|---------|---------|
| `^` | Start of line | `^ERROR` | Lines that START with ERROR |
| `$` | End of line | `\.log$` | Lines that END with .log |
| `\b` | Word boundary | `\berror\b` | "error" but NOT "errors" or "terror" |
| `\B` | Non-word boundary | `\Berror\B` | "error" only when surrounded by word chars |

```bash
grep "^ERROR" app.log          # Lines starting with ERROR
grep "timeout$" app.log        # Lines ending with timeout
grep -E "\berror\b" app.log    # Word "error" only (not "errors")
grep "^$" file.txt             # Empty lines
grep -v "^$" file.txt          # Non-empty lines (remove blank lines)
grep -v "^#" config.conf       # Non-comment lines
grep -v "^[[:space:]]*#" conf  # Non-comment lines (allow leading spaces)
```

---

## 1.4 Character Classes

Match a SET of characters.

| Pattern | Matches |
|---------|---------|
| `.` | Any single character (except newline) |
| `[abc]` | a, b, or c |
| `[^abc]` | Any char EXCEPT a, b, c |
| `[a-z]` | Any lowercase letter |
| `[A-Z]` | Any uppercase letter |
| `[0-9]` | Any digit |
| `[a-zA-Z0-9]` | Any alphanumeric |
| `[a-zA-Z0-9_]` | Any word character |

### POSIX Classes (portable across tools)

| POSIX | Equivalent | Matches |
|-------|-----------|---------|
| `[:digit:]` | `[0-9]` | Digits |
| `[:alpha:]` | `[a-zA-Z]` | Letters |
| `[:alnum:]` | `[a-zA-Z0-9]` | Letters and digits |
| `[:space:]` | `[ \t\n\r]` | Whitespace |
| `[:upper:]` | `[A-Z]` | Uppercase letters |
| `[:lower:]` | `[a-z]` | Lowercase letters |
| `[:print:]` | printable chars | Printable (no control chars) |

```bash
# Use inside [] in grep:
grep "[[:digit:]]" file        # Lines containing a digit
grep "^[[:upper:]]" file       # Lines starting with capital letter
grep "[[:space:]]$" file       # Lines ending with whitespace (trailing spaces!)
```

### PCRE shorthand classes (grep -P only)

| Pattern | Matches |
|---------|---------|
| `\d` | Digit `[0-9]` |
| `\D` | Non-digit `[^0-9]` |
| `\w` | Word char `[a-zA-Z0-9_]` |
| `\W` | Non-word char |
| `\s` | Whitespace `[ \t\n\r\f]` |
| `\S` | Non-whitespace |

---

## 1.5 Quantifiers

How MANY times a pattern repeats.

| Quantifier | Meaning | Example | Matches |
|-----------|---------|---------|---------|
| `*` | 0 or more | `ab*c` | `ac`, `abc`, `abbc`, `abbbc` |
| `+` | 1 or more | `ab+c` | `abc`, `abbc` (NOT `ac`) |
| `?` | 0 or 1 | `colou?r` | `color`, `colour` |
| `{n}` | Exactly n | `\d{4}` | Exactly 4 digits |
| `{n,}` | n or more | `\d{2,}` | 2 or more digits |
| `{n,m}` | Between n and m | `\d{2,4}` | 2, 3, or 4 digits |

### Greedy vs Lazy (PCRE only)

```
  Input: <b>bold</b> and <i>italic</i>

  Greedy:  <.+>    → matches "<b>bold</b> and <i>italic</i>"  (too much!)
  Lazy:    <.+?>   → matches "<b>", "<i>"  (stops at first >)

  Add ? after a quantifier to make it lazy:  *? +? {n,m}?
```

---

## 1.6 Groups and Capturing

| Pattern | Meaning |
|---------|---------|
| `(abc)` | Capture group — matches "abc", stores it |
| `\1` | Backreference to group 1 (BRE: `\1`, PCRE: `\1`) |
| `(?:abc)` | Non-capturing group (PCRE) — groups without storing |
| `a\|b` | Alternation in BRE: a OR b |
| `a\|b` in ERE | `a|b` — no backslash needed |

```bash
# BRE backreference: find doubled words (the the)
grep -E "\b(\w+)\s+\1\b" file.txt

# ERE alternation: match error or warning
grep -E "error|warning|critical" app.log

# sed BRE: wrap first word in brackets
echo "hello world" | sed 's/\([^ ]*\)/[\1]/'
# Output: [hello] world

# sed ERE: same, cleaner
echo "hello world" | sed -E 's/([^ ]+)/[\1]/'
```

---

## 1.7 Common DevOps Regex Patterns

```bash
# IPv4 address (strict)
grep -E "^([0-9]{1,3}\.){3}[0-9]{1,3}$" file

# IPv4 address (in text)
grep -oE "[0-9]{1,3}(\.[0-9]{1,3}){3}" file

# Email address (simple)
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" file

# URL (http/https)
grep -oE "https?://[a-zA-Z0-9./_?&=-]+" file

# Semantic version (v1.2.3 or 1.2.3)
grep -E "^v?[0-9]+\.[0-9]+\.[0-9]+$" file

# ISO date (YYYY-MM-DD)
grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}" file

# Git commit SHA (40 hex chars)
grep -E "^[a-f0-9]{40}$" file

# Docker image tag
grep -E "^[a-z0-9._/-]+:[a-zA-Z0-9._-]+$" file

# AWS ARN
grep -E "^arn:aws:[a-z0-9-]+:[a-z0-9-]*:[0-9]{12}:" file

# Azure Resource ID
grep -E "^/subscriptions/[a-f0-9-]+/resourceGroups/" file

# Port number (1-65535)
grep -E "^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$" file

# Nginx access log line extraction (method + path + status)
grep -oP '"(GET|POST|PUT|DELETE|PATCH) \K[^"]+(?=" HTTP)' access.log

# Extract JWT token parts
grep -oP "ey[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+" file
```

---

## 1.8 Regex Gotchas ⚠️

### 1. `.` matches EVERYTHING (including slashes, dots)
```bash
# WRONG: looking for literal "1.2.3" — matches "1X2Y3" too
grep "1.2.3" versions.txt

# RIGHT: escape the dot
grep "1\.2\.3" versions.txt
grep -E "1\.2\.3" versions.txt
```

### 2. Greedy quantifiers eat too much
```bash
# Input: <div class="main">content</div>
# WRONG: matches entire string
echo '<div class="main">content</div>' | grep -oE "<div.*>"

# RIGHT: be specific about what can be inside
echo '<div class="main">content</div>' | grep -oE "<div[^>]*>"
```

### 3. BRE vs ERE confusion
```bash
# In BRE (grep default): + ? | { } ( ) must be escaped
grep "a\+" file       # matches "aa", "aaa" etc.
grep "a+" file        # matches literal "a+" (the + is not special!)

# In ERE (grep -E): + ? | { } ( ) are special without escaping
grep -E "a+" file     # matches "aa", "aaa" etc. ✅
```

### 4. `^` inside character class means NOT
```bash
[abc]   ← matches a, b, or c
[^abc]  ← matches anything EXCEPT a, b, c

# Easy to confuse when you also use ^ for start-of-line
^[abc]  ← line STARTING with a, b, or c
^[^abc] ← line starting with anything EXCEPT a, b, c
```

### 5. `\d` doesn't work in BRE/ERE — need `-P`
```bash
grep "\d+" file        # WRONG in standard grep (no \d in ERE)
grep -P "\d+" file     # RIGHT: PCRE mode ✅
grep -E "[0-9]+" file  # RIGHT: ERE with explicit character class ✅
```

---

# Chapter 2: grep — Search & Filter

> **Mental model:** grep is a filter. It reads lines in, and passes through only lines that match your pattern.

```
  Input file/stdin  →  [ grep pattern ]  →  Matching lines only
```

---

## 2.1 Basic Usage

```bash
grep "pattern" file.txt          # Search for pattern in file
grep "pattern" file1 file2       # Search in multiple files
grep "pattern" *.log             # Search in all .log files
cat file.txt | grep "pattern"    # From stdin (pipe)

# Multiple patterns: match lines containing either
grep -E "error|warning" file.txt
```

---

## 2.2 Essential Flags

| Flag | Long form | What it does |
|------|-----------|-------------|
| `-i` | `--ignore-case` | Case-insensitive match |
| `-n` | `--line-number` | Show line numbers |
| `-c` | `--count` | Count matching lines (not lines' content) |
| `-v` | `--invert-match` | Show NON-matching lines |
| `-l` | `--files-with-matches` | Show only filenames that match |
| `-L` | `--files-without-match` | Show only filenames that DON'T match |
| `-r` | `--recursive` | Recurse into directories |
| `-w` | `--word-regexp` | Match whole words only |
| `-x` | `--line-regexp` | Match whole lines only |
| `-q` | `--quiet` | No output; exit code only (0=match, 1=no match) |
| `-o` | `--only-matching` | Print only the matching part (not the whole line) |
| `-h` | `--no-filename` | Don't print filename prefix |
| `-H` | `--with-filename` | Always print filename prefix |
| `-E` | `--extended-regexp` | ERE mode (use `+`, `?`, `|` without escaping) |
| `-P` | `--perl-regexp` | PCRE mode (`\d`, `\w`, lookahead, etc.) |
| `-F` | `--fixed-strings` | Plain text (no regex), fastest |

---

## 2.3 Context Flags — See Surrounding Lines

```bash
grep -A 3 "ERROR" app.log     # 3 lines AFTER each match
grep -B 2 "ERROR" app.log     # 2 lines BEFORE each match
grep -C 5 "ERROR" app.log     # 5 lines before AND after (context)

# Practical: find a config block
grep -A 20 "server {" nginx.conf
grep -B 5 -A 5 "listen 443" nginx.conf
```

---

## 2.4 Recursive Search with Filters

```bash
# Search in all Python files under current directory
grep -r "def deploy" . --include="*.py"

# Search in all files EXCEPT test files
grep -r "SECRET_KEY" . --exclude="*.test.*" --exclude-dir=".git"

# Search and show filenames only (no content)
grep -rl "TODO" . --include="*.py"

# Count matches per file
grep -rc "import" . --include="*.py" | sort -t: -k2 -rn | head -20
```

---

## 2.5 Output Control

```bash
# Print only the matching PART (not the full line)
grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" access.log
# Output: just the IP addresses, one per line

# Print filename and line number
grep -rn "DB_PASSWORD" /opt/app --include="*.py" --include="*.env"

# Silent mode for scripts (check if pattern exists)
if grep -q "FAIL" test_results.txt; then
    echo "Tests failed!"
    exit 1
fi

# Count (for stats/reporting)
error_count=$(grep -c "ERROR" app.log)
echo "Found $error_count errors"
```

---

## 2.6 grep with xargs and find

```bash
# Find files modified today containing "ERROR"
find /var/log -mtime 0 -name "*.log" | xargs grep -l "ERROR"

# Search large number of files efficiently
find . -name "*.yaml" -print0 | xargs -0 grep -l "apiVersion"

# In-place replacement across files (grep to find, sed to fix)
grep -rl "old-registry.company.com" . --include="*.yaml" | \
    xargs sed -i 's|old-registry.company.com|new-registry.company.com|g'

# Count errors per log file, sort by count
find /var/log -name "*.log" | xargs -I{} sh -c 'echo -n "{}: "; grep -c "ERROR" "{}" 2>/dev/null || echo 0' | sort -t: -k2 -rn
```

---

## 2.7 Advanced grep Patterns

```bash
# AND logic: lines matching pattern1 AND pattern2
grep "ERROR" app.log | grep "database"
# Or using lookahead (PCRE):
grep -P "(?=.*ERROR)(?=.*database)" app.log

# OR logic: grep -E is cleaner
grep -E "ERROR|WARNING|CRITICAL" app.log

# NOT this AND that (grep v chaining)
grep "ERROR" app.log | grep -v "expected_error"

# Match lines where column 4 has specific value (combine with awk)
grep -E "^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" access.log | awk '$9 >= 500'

# Extract and count unique matches
grep -oP "(?<=user=)\w+" auth.log | sort | uniq -c | sort -rn

# Lines that match regex AND are at least 100 chars long
grep -E ".{100,}" file.txt
```

---

## 2.8 Real-World DevOps Scenarios

### Scenario 1: Find hardcoded secrets in a codebase
```bash
# Broad sweep for common secret patterns
grep -rn --include="*.py" --include="*.js" --include="*.yaml" \
    -E "(password|secret|api_key|token|passwd|pwd)\s*=\s*['\"][^'\"]{8,}" \
    /opt/app/ | grep -v "example\|sample\|test\|placeholder"
```

### Scenario 2: Monitor live logs for errors without buffering
```bash
# --line-buffered is critical when grepping a tail -f
tail -f /var/log/nginx/error.log | grep --line-buffered -E "error|crit|alert|emerg"
```

### Scenario 3: Find all IPs making requests to a specific endpoint
```bash
grep "POST /api/login" /var/log/nginx/access.log | \
    grep -oP "^\d{1,3}(\.\d{1,3}){3}" | \
    sort | uniq -c | sort -rn | head -20
# Output: count of requests per IP to /api/login
```

### Scenario 4: Find which services are using a specific port
```bash
grep -r "8080\|:8080" /etc/nginx/ /etc/apache2/ 2>/dev/null --include="*.conf"
```

### Scenario 5: Audit all files changed in the last deploy
```bash
git diff --name-only HEAD~1 HEAD | xargs grep -l "TODO\|FIXME\|HACK"
```

### Scenario 6: Check if a process is running (script-safe)
```bash
if grep -q "myapp" <(ps aux); then
    echo "myapp is running"
fi
# Better: use pgrep, but grep works too
```

---

## 2.9 grep Gotchas ⚠️

### 1. Binary files: grep refuses or gives garbage
```bash
grep "pattern" binaryfile    # Prints: Binary file matches (no content)
grep -a "pattern" binaryfile # Treat binary as text — force output
grep -I "pattern" files/*    # -I skips binary files entirely
```

### 2. Pipe buffering breaks tail -f | grep
```bash
# WRONG: output appears only in bursts (line buffering issue)
tail -f app.log | grep "ERROR"

# RIGHT: force line-by-line output
tail -f app.log | grep --line-buffered "ERROR"
# Or: stdbuf -oL grep "ERROR"
```

### 3. grep -c counts LINES not total occurrences
```bash
# Line with 3 "ERROR"s counts as 1
grep -c "ERROR" file.txt     # counts matching LINES
grep -o "ERROR" file.txt | wc -l  # counts total OCCURRENCES
```

### 4. Special characters in patterns need escaping
```bash
grep "192.168.1.1" file      # WRONG: . matches any char
grep "192\.168\.1\.1" file   # RIGHT: literal dot
grep -F "192.168.1.1" file   # RIGHT: -F = fixed string (no regex)
```

### 5. `grep -r` follows symlinks on some systems, not others
```bash
grep -rL "pattern" .         # May miss symlinked directories
grep -rL --follow "pattern" . # Explicitly follow symlinks (GNU grep)
```

---

# Chapter 3: sed — Stream Editor

> **Mental model:** sed reads a file line by line, applies operations to each line, and outputs the result. It never loads the whole file into memory.

```
  Input →  [ read line ]  →  [ apply script ]  →  [ output ]  →  next line
```

---

## 3.1 Basic Substitution

```bash
# Syntax: sed 's/FIND/REPLACE/FLAGS'
sed 's/old/new/' file          # Replace FIRST occurrence per line
sed 's/old/new/g' file         # Replace ALL occurrences per line (global)
sed 's/old/new/2' file         # Replace only 2nd occurrence per line
sed 's/old/new/gi' file        # Case-insensitive global replace
sed 's/old/new/gp' file        # Replace all + print matched lines twice
sed -n 's/old/new/p' file      # Print ONLY lines where replacement happened

# In-place edit (modifies the file!)
sed -i 's/old/new/g' file.txt
sed -i.bak 's/old/new/g' file.txt  # In-place with backup → file.txt.bak
```

### ⚠️ macOS vs Linux difference
```bash
# Linux (GNU sed): -i alone is fine
sed -i 's/old/new/g' file

# macOS (BSD sed): -i requires an extension argument
sed -i '' 's/old/new/g' file    # Use empty string for no backup
sed -i'.bak' 's/old/new/g' file # Or with backup
```

---

## 3.2 Delimiter Change

When your pattern contains `/`, use a different delimiter:

```bash
# WRONG: slashes in path break the syntax
sed 's//old/path//new/path/g' file   # Syntax error

# RIGHT: use | as delimiter
sed 's|/old/path|/new/path|g' file

# RIGHT: use # as delimiter  
sed 's#/old/path#/new/path#g' file

# Any character works as delimiter
sed 's@http@https@g' file
```

---

## 3.3 Address Ranges

Tell sed WHICH lines to operate on:

```bash
# Line number addresses
sed '5s/old/new/' file          # Only line 5
sed '5,10s/old/new/g' file      # Lines 5 through 10
sed '5,$s/old/new/g' file       # Line 5 to end of file
sed '1s/old/new/' file          # First line only
sed '$s/old/new/' file          # Last line only

# Pattern addresses
sed '/pattern/s/old/new/g' file # Only lines matching "pattern"
sed '/START/,/END/s/old/new/g' file  # Lines between START and END markers

# Negation: ! means NOT
sed '/pattern/!s/old/new/g' file     # Lines NOT matching "pattern"
sed '5!s/old/new/g' file             # All lines EXCEPT line 5
```

---

## 3.4 Delete, Print, and Other Commands

```bash
# Delete lines
sed '/pattern/d' file           # Delete lines matching pattern
sed '5d' file                   # Delete line 5
sed '5,10d' file                # Delete lines 5-10
sed '/^#/d' file                # Delete comment lines
sed '/^$/d' file                # Delete empty lines
sed '/^[[:space:]]*$/d' file    # Delete blank lines (spaces/tabs too)
sed '/^#/d;/^$/d' file          # Delete both comment and empty lines

# Print (use with -n to suppress auto-print)
sed -n '5p' file                # Print only line 5
sed -n '5,10p' file             # Print lines 5-10
sed -n '/START/,/END/p' file    # Print between markers
sed -n '/pattern/p' file        # Print matching lines (same as grep)

# Insert and append
sed '/pattern/i\New line above' file    # Insert before matching line
sed '/pattern/a\New line below' file    # Append after matching line
sed '3i\New line above line 3' file     # Insert before line 3
```

---

## 3.5 Multiple Operations

```bash
# Method 1: -e flag (multiple expressions)
sed -e 's/foo/bar/g' -e 's/baz/qux/g' -e '/^#/d' file

# Method 2: semicolons (same as -e)
sed 's/foo/bar/g; s/baz/qux/g; /^#/d' file

# Method 3: script file
cat > fix.sed << 'EOF'
s/foo/bar/g
s/baz/qux/g
/^#/d
/^$/d
EOF
sed -f fix.sed file
```

---

## 3.6 ERE Mode (-E)

```bash
# Without -E: must escape + ? | ( )
sed 's/\(foo\|bar\)/baz/g' file

# With -E: much cleaner
sed -E 's/(foo|bar)/baz/g' file
sed -E 's/[0-9]+/NUM/g' file
sed -E 's/(https?):\/\//\1:\/\/www./g' file
```

---

## 3.7 Advanced: Hold Space

sed has two buffers: **pattern space** (current line) and **hold space** (temporary storage):

```bash
# Commands:
# h  — copy pattern space to hold space (overwrite)
# H  — append pattern space to hold space (with newline)
# g  — get: copy hold space to pattern space (overwrite)
# G  — Get: append hold space to pattern space (with newline)
# x  — exchange pattern space and hold space

# Example: Reverse a file (tac equivalent)
sed -n '1!G;h;$p' file
# Explanation:
# 1!G  → Append hold to pattern (except on line 1)
# h    → Copy current combo to hold
# $p   → On last line, print

# Example: Double-space a file (add blank line after each line)
sed 'G' file

# Example: Print every other line
sed -n 'p;n' file      # Print 1st, skip 2nd, print 3rd, skip 4th...
sed -n 'n;p' file      # Skip 1st, print 2nd, skip 3rd, print 4th...
```

---

## 3.8 Real-World DevOps Scenarios

### Scenario 1: Update version in all files across a repo
```bash
OLD_VERSION="1.2.3"
NEW_VERSION="1.3.0"
find . -name "*.yaml" -o -name "*.json" | \
    xargs sed -i "s/${OLD_VERSION}/${NEW_VERSION}/g"
```

### Scenario 2: Configure app from environment variables (Docker entrypoint)
```bash
#!/bin/bash
# Replace template placeholders with env vars
sed -i \
    -e "s|{{DB_HOST}}|${DB_HOST}|g" \
    -e "s|{{DB_PORT}}|${DB_PORT}|g" \
    -e "s|{{APP_ENV}}|${APP_ENV}|g" \
    /etc/myapp/config.conf
exec "$@"
```

### Scenario 3: Strip comments and blank lines from config for parsing
```bash
sed -E '/^[[:space:]]*(#|;|$)/d' /etc/myapp/config.ini
```

### Scenario 4: Extract a block from a config file
```bash
# Extract nginx server block (from "server {" to matching "}")
sed -n '/^server {/,/^}/p' nginx.conf
```

### Scenario 5: Add a prefix to every line (for logging)
```bash
sed "s/^/[$(date '+%Y-%m-%d %H:%M:%S')] /" logfile.txt
```

### Scenario 6: Remove ANSI color codes from output
```bash
# Useful for processing colorized CLI output
some-command | sed -E 's/\x1B\[[0-9;]*[mK]//g'
```

### Scenario 7: Replace in-place across multiple files safely
```bash
# Always test with --dry-run equivalent first (no -i)
sed -E 's/old-hostname/new-hostname/g' /etc/hosts /etc/hostname

# Then apply in-place with backup
sed -i.bak -E 's/old-hostname/new-hostname/g' /etc/hosts
# Verify the change
diff /etc/hosts /etc/hosts.bak
```

---

## 3.9 sed Gotchas ⚠️

### 1. `-i` on macOS requires an argument
```bash
# macOS: sed -i 's/old/new/g' file → ERROR
# macOS: sed -i '' 's/old/new/g' file → OK
```

### 2. Newlines in replacement
```bash
# To insert a newline in replacement:
sed 's/,/\n/g' file     # Works on GNU sed
# On macOS BSD sed:
sed 's/,/\'$'\n''/g' file  # Different escaping required
```

### 3. `&` in replacement is the ENTIRE match
```bash
echo "hello" | sed 's/ell/[&]/'
# Output: h[ell]o   ← & = the matched text "ell"

# Useful for wrapping matches:
sed -E 's/[0-9]+/(&)/g' file  # Wrap all numbers in parentheses
```

### 4. sed processes empty pattern space by default
```bash
# ^ and $ match start/end of line in sed (not start/end of file)
# To process the whole file as one string, need GNU extensions or awk
```

---

# Chapter 4: awk — Text Processing Language

> **Mental model:** awk is a column-aware programming language. It splits each line into fields automatically and lets you filter, calculate, and format.

```
  Input line  →  [ split into $1 $2 $3... ]  →  [ pattern { action } ]  →  Output
```

---

## 4.1 Basic Structure

```
  awk 'PATTERN { ACTION }' file

  PATTERN = when to run the action (optional)
  ACTION  = what to do (optional)

  If PATTERN is omitted → action runs on EVERY line
  If ACTION is omitted  → matching lines are printed
```

```bash
awk '{print}' file           # Print every line (same as cat)
awk '/ERROR/' file           # Print lines matching ERROR (same as grep)
awk '/ERROR/ {print $0}' file # Same — $0 = entire line
```

---

## 4.2 Fields and Variables

```bash
# Fields: $1 = first word, $2 = second, $NF = last, $0 = whole line
echo "hello world foo" | awk '{print $2}'   # → world
echo "hello world foo" | awk '{print $NF}'  # → foo (last field)
echo "hello world foo" | awk '{print NF}'   # → 3 (number of fields)

# Field separator: default = whitespace (one or more)
awk -F: '{print $1, $3}' /etc/passwd        # Colon-separated
awk -F',' '{print $1, $2}' data.csv         # CSV
awk -F'\t' '{print $1}' data.tsv            # Tab-separated

# Built-in variables
awk '{print NR, $0}' file    # NR = line number (Number of Record)
awk 'NR==5' file             # Only line 5
awk 'NR==5,NR==10' file      # Lines 5-10
awk 'NR>1' file              # Skip header line

# Output field separator
awk -F: 'OFS="|" {print $1,$3,$6}' /etc/passwd
# → root|0|/root  (joined with |)
```

---

## 4.3 BEGIN and END Blocks

```bash
# BEGIN runs ONCE before any input is processed
# END runs ONCE after all input is processed
awk 'BEGIN { print "=== Report ===" }
     { print $0 }
     END { print "=== Done ===" }' file

# Practical: count lines with a header
awk 'BEGIN { count=0 }
     /ERROR/ { count++ }
     END { print "Total errors:", count }' app.log

# Sum a column
awk -F',' '{ total += $3 } END { printf "Total: %.2f\n", total }' sales.csv
```

---

## 4.4 Conditionals and Loops

```bash
# if/else
awk '{ if ($3 > 100) print "high:", $0; else print "low:", $0 }' file

# Ternary operator
awk '{ status = ($5 >= 400) ? "ERROR" : "OK"; print status, $7 }' access.log

# while loop
awk '{ i=1; while (i<=NF) { print i, $i; i++ } }' file

# for loop
awk '{ for (i=1; i<=NF; i++) printf "%s ", $i; print "" }' file

# Ranges (similar to sed address ranges)
awk '/START/,/END/ { print }' file   # Print between markers
```

---

## 4.5 String Functions

```bash
echo "Hello World" | awk '{print length($0)}'          # → 11
echo "Hello World" | awk '{print toupper($0)}'          # → HELLO WORLD
echo "Hello World" | awk '{print tolower($0)}'          # → hello world
echo "Hello World" | awk '{print substr($0, 1, 5)}'     # → Hello
echo "Hello World" | awk '{print index($0, "World")}'   # → 7

# split() — split a field into an array
echo "a:b:c:d" | awk '{n=split($0,arr,":"); for(i=1;i<=n;i++) print arr[i]}'

# gsub() — global substitution (like sed s///g)
echo "foo foo foo" | awk '{gsub("foo","bar"); print}'   # → bar bar bar

# sub() — first occurrence only (like sed s///)
echo "foo foo foo" | awk '{sub("foo","bar"); print}'    # → bar foo foo

# sprintf() — format a string
awk '{printf "%-15s %5.2f%%\n", $1, $2}' data.txt
```

---

## 4.6 Arrays (Associative)

awk arrays are associative (like dictionaries/hash maps):

```bash
# Count occurrences of each value
awk '{count[$1]++} END { for (k in count) print count[k], k }' file

# Frequency analysis: top error types
awk '/ERROR/ {errors[$5]++} END { for (e in errors) print errors[e], e }' \
    app.log | sort -rn | head -10

# Group by and sum
awk -F',' '{sum[$1]+=$3} END { for (k in sum) printf "%s: %.2f\n", k, sum[k]}' \
    sales.csv

# Check if key exists
awk '{if ($1 in seen) print "duplicate:", $1; else seen[$1]=1}' file

# Delete from array
awk '{delete arr[$1]}' file
```

---

## 4.7 User-Defined Functions

```bash
awk '
function abs(n) { return n < 0 ? -n : n }
function max(a, b) { return a > b ? a : b }
function human_bytes(bytes) {
    if (bytes >= 1073741824) return sprintf("%.1fG", bytes/1073741824)
    if (bytes >= 1048576)    return sprintf("%.1fM", bytes/1048576)
    if (bytes >= 1024)       return sprintf("%.1fK", bytes/1024)
    return bytes "B"
}
{ print human_bytes($1) }
' sizes.txt
```

---

## 4.8 Piping Inside awk

```bash
# awk can pipe output to external commands
awk '{ print | "sort -rn" }' file

# Or read from external commands with getline
awk 'BEGIN {
    while (("df -h" | getline line) > 0) {
        if (line ~ /[89][0-9]%|100%/) print "ALERT:", line
    }
}'
```

---

## 4.9 Real-World DevOps Scenarios

### Scenario 1: Parse nginx access.log — top IPs and status codes
```bash
# access.log format: IP - - [date] "METHOD path HTTP/1.1" STATUS size
# Top 10 IPs by request count:
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10

# Count requests by HTTP status:
awk '{status[$9]++} END {for (s in status) print s, status[s]}' \
    /var/log/nginx/access.log | sort -k1

# Average response size per status code:
awk '{sum[$9]+=$10; count[$9]++}
     END {for (s in sum) printf "HTTP %s: avg size %.0f bytes\n", s, sum[s]/count[s]}' \
    /var/log/nginx/access.log | sort
```

### Scenario 2: Disk usage alerting
```bash
df -h | awk 'NR>1 {
    # Extract the percentage number
    gsub(/%/, "", $5)
    if ($5+0 >= 80) {
        printf "ALERT: %s is %s%% full (mounted: %s)\n", $1, $5, $6
    }
}'
```

### Scenario 3: Process monitoring — find memory hogs
```bash
ps aux | awk 'NR==1 {print; next} {if ($4 > 5.0) print}' | \
    awk 'NR==1 {print} NR>1 {print | "sort -k4 -rn"}'
```

### Scenario 4: Generate CSV report from logs
```bash
awk -F' ' '
BEGIN { print "date,hour,requests,errors,avg_bytes" }
{
    split($4, dt, ":")
    hour = dt[2]
    date_hour = substr($4,2,11) ":" hour
    requests[date_hour]++
    if ($9 >= 500) errors[date_hour]++
    bytes[date_hour] += $10
}
END {
    for (dh in requests) {
        avg = (requests[dh] > 0) ? bytes[dh]/requests[dh] : 0
        printf "%s,%d,%d,%.0f\n", dh, requests[dh], errors[dh]+0, avg
    }
}' /var/log/nginx/access.log | sort
```

### Scenario 5: Parse /etc/passwd for audit
```bash
awk -F: '
BEGIN { print "=== User Account Audit ===" }
{
    uid  = $3
    gid  = $4
    home = $6
    shell = $7

    if (uid == 0 && $1 != "root") print "ALERT: Non-root UID 0:", $1
    if (uid >= 1000) {
        users++
        if (shell == "/bin/bash" || shell == "/bin/sh") bash_users++
        if (home !~ /^\/home\//) print "WARN: Unusual home dir:", $1, home
    }
}
END {
    print "Total regular users:", users
    print "Users with bash/sh:", bash_users
}' /etc/passwd
```

### Scenario 6: Kubernetes pod resource summary
```bash
kubectl top pods --all-namespaces | awk '
NR==1 { print; next }
{
    ns=$1; pod=$2; cpu=$3; mem=$4
    ns_cpu[ns] += substr(cpu, 1, length(cpu)-1)  # strip "m"
    ns_mem[ns] += substr(mem, 1, length(mem)-2)  # strip "Mi"
    ns_pods[ns]++
}
END {
    print "\n=== Resource Usage by Namespace ==="
    for (ns in ns_pods)
        printf "%-30s pods=%-4d cpu=%-8s mem=%sMi\n",
               ns, ns_pods[ns], ns_cpu[ns]"m", ns_mem[ns]
}' | sort
```

---

## 4.10 awk Gotchas ⚠️

### 1. awk uses `==` not `=` for comparison
```bash
awk '$3 = 100' file   # WRONG: assigns 100 to $3 (but works oddly — truthy assign)
awk '$3 == 100' file  # RIGHT: tests if $3 equals 100
```

### 2. String vs number comparison
```bash
awk '$3 > "9"' file   # String comparison: "10" < "9" (alphabetically!)
awk '$3 > 9' file     # Numeric comparison: 10 > 9 ✅
# awk auto-converts: if a string looks like a number, it's numeric in numeric context
```

### 3. Regex in awk uses ERE (not PCRE)
```bash
awk '/\d+/' file      # WRONG: \d not supported
awk '/[0-9]+/' file   # RIGHT: use character classes
```

### 4. Printing: print vs printf
```bash
awk '{print $1, $2}' file     # print: adds OFS between, newline at end
awk '{printf "%s\t%s\n",$1,$2}' file  # printf: you control ALL formatting
```

### 5. NR vs FNR when processing multiple files
```bash
awk 'NR==FNR { seen[$0]=1; next } $0 in seen' file1 file2
# NR = total lines across all files
# FNR = lines in CURRENT file
# NR==FNR is true only while reading the FIRST file
```

---

# Chapter 5: curl — HTTP Client

> **Mental model:** curl is a command-line browser. It makes HTTP requests and shows you the response. Invaluable for testing APIs, health checks, and automation.

---

## 5.1 Basic Requests

```bash
curl https://example.com                   # GET request, print body
curl -o output.html https://example.com    # Save body to file
curl -O https://example.com/file.zip       # Save with remote filename
curl -L https://example.com               # Follow redirects (-L = location)
curl -I https://example.com               # Headers only (HEAD request)
curl -i https://example.com               # Response headers + body
curl -s https://example.com               # Silent (no progress meter)
curl -f https://example.com               # Fail silently on HTTP errors (exit code != 0)
curl -sf https://example.com              # Silent + fail (good for scripts)
```

---

## 5.2 HTTP Methods and Data

```bash
# POST with form data (application/x-www-form-urlencoded)
curl -X POST -d "user=alice&pass=secret" https://api.example.com/login

# POST with JSON body
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"username": "alice", "password": "secret"}' \
    https://api.example.com/login

# POST JSON from a file
curl -X POST \
    -H "Content-Type: application/json" \
    -d @payload.json \
    https://api.example.com/endpoint

# PUT (update resource)
curl -X PUT \
    -H "Content-Type: application/json" \
    -d '{"name": "new-name"}' \
    https://api.example.com/resource/123

# DELETE
curl -X DELETE https://api.example.com/resource/123

# PATCH (partial update)
curl -X PATCH \
    -H "Content-Type: application/json" \
    -d '{"status": "inactive"}' \
    https://api.example.com/resource/123
```

---

## 5.3 Headers and Authentication

```bash
# Custom headers
curl -H "Accept: application/json" https://api.example.com
curl -H "X-Request-ID: abc123" -H "X-Client: myapp" https://api.example.com

# Bearer token (most common for REST APIs)
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiJ9..." https://api.example.com

# API key in header
curl -H "X-API-Key: your-api-key-here" https://api.example.com

# Basic auth
curl -u username:password https://api.example.com
curl -H "Authorization: Basic $(echo -n 'user:pass' | base64)" https://api.example.com

# Client certificate (mTLS)
curl --cert client.crt --key client.key https://api.example.com
curl --cert client.pem https://api.example.com  # Combined cert+key PEM

# CA certificate (custom CA)
curl --cacert /path/to/ca.crt https://internal-api.company.com

# Skip TLS verification (NEVER in production!)
curl -k https://self-signed-cert.example.com
```

---

## 5.4 Timeouts and Retries

```bash
# Connection timeout (seconds to establish connection)
curl --connect-timeout 5 https://api.example.com

# Max total time for the request
curl --max-time 30 https://api.example.com

# Retry logic
curl --retry 3 --retry-delay 2 --retry-max-time 30 https://api.example.com
curl --retry 5 --retry-all-errors https://api.example.com

# Combine: robust API call
curl --silent \
     --fail \
     --connect-timeout 5 \
     --max-time 30 \
     --retry 3 \
     --retry-delay 1 \
     https://api.example.com/health
```

---

## 5.5 Output Formatting with -w

`-w` (write-out) prints metrics after a request — invaluable for performance testing:

```bash
# Get HTTP status code only
curl -s -o /dev/null -w "%{http_code}" https://example.com

# Full timing breakdown
curl -s -o /dev/null -w "
  DNS lookup:       %{time_namelookup}s
  TCP connect:      %{time_connect}s
  TLS handshake:    %{time_appconnect}s
  TTFB:             %{time_starttransfer}s
  Total:            %{time_total}s
  Response size:    %{size_download} bytes
  HTTP status:      %{http_code}
" https://example.com

# Available variables:
# %{time_namelookup}  - DNS resolution time
# %{time_connect}     - TCP connection time
# %{time_appconnect}  - SSL/TLS handshake time
# %{time_pretransfer} - Time until data transfer started
# %{time_starttransfer} - TTFB (Time to First Byte)
# %{time_total}       - Total time
# %{size_download}    - Downloaded bytes
# %{speed_download}   - Download speed (bytes/sec)
# %{http_code}        - HTTP status code
# %{remote_ip}        - Server IP address used
# %{url_effective}    - Final URL after redirects
```

---

## 5.6 File Upload and Download

```bash
# Upload a file as form-data (multipart)
curl -X POST -F "file=@/path/to/file.zip" https://api.example.com/upload

# Upload with additional form fields
curl -X POST \
    -F "file=@report.pdf" \
    -F "description=Monthly report" \
    -F "version=1.0" \
    https://api.example.com/upload

# Resumable download (continue interrupted download)
curl -L -C - -O https://releases.example.com/large-file.tar.gz

# Download with progress bar
curl -# -O https://example.com/large-file.tar.gz

# Download and pipe to tar (extract on the fly)
curl -sL https://example.com/archive.tar.gz | tar xz -C /opt/myapp/
```

---

## 5.7 curl + jq for JSON APIs

```bash
# Parse JSON response
curl -s https://api.github.com/users/torvalds | jq '.name, .company, .location'

# Extract specific field for use in scripts
LATEST_TAG=$(curl -s https://api.github.com/repos/kubernetes/kubernetes/releases/latest | \
    jq -r '.tag_name')
echo "Latest k8s: $LATEST_TAG"

# POST and parse the response
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"username":"alice"}' \
    https://api.example.com/create-user)

USER_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Created user ID: $USER_ID"

# Handle API pagination
page=1
while true; do
    data=$(curl -s "https://api.example.com/items?page=$page&per_page=100")
    count=$(echo "$data" | jq '.items | length')
    echo "$data" | jq -r '.items[].name'
    [[ $count -lt 100 ]] && break
    ((page++))
done
```

---

## 5.8 Azure / Cloud API Calls

```bash
# Get Azure AD token
TOKEN=$(curl -s -X POST \
    "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&scope=https://management.azure.com/.default&grant_type=client_credentials" | \
    jq -r '.access_token')

# Call Azure Management API
curl -s \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "https://management.azure.com/subscriptions/${SUB_ID}/resourceGroups?api-version=2021-04-01" | \
    jq -r '.value[].name'

# AWS: assuming aws CLI isn't available — use curl directly
# (Usually you'd use the AWS CLI, but curl is the underlying mechanism)
```

---

## 5.9 Real-World DevOps Scenarios

### Scenario 1: Health check in CI/CD pipeline
```bash
health_check() {
    local url="$1"
    local max_attempts="${2:-10}"
    local wait_seconds="${3:-5}"

    for i in $(seq 1 "$max_attempts"); do
        http_code=$(curl -sf -o /dev/null -w "%{http_code}" \
            --connect-timeout 3 --max-time 10 "$url" 2>/dev/null || true)
        
        if [[ "$http_code" == "200" ]]; then
            echo "✅ Health check passed (attempt $i)"
            return 0
        fi
        echo "⏳ Waiting... (attempt $i/$max_attempts, got HTTP $http_code)"
        sleep "$wait_seconds"
    done
    echo "❌ Health check failed after $max_attempts attempts"
    return 1
}

health_check "https://myapp.example.com/health" 12 5
```

### Scenario 2: Trigger Slack webhook alert
```bash
send_slack_alert() {
    local message="$1"
    local channel="${2:-#alerts}"
    
    curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"channel\": \"$channel\", \"text\": \"$message\", \"username\": \"CI Bot\"}"
}

send_slack_alert "🔴 Deployment failed: v${VERSION} on ${ENV}"
```

### Scenario 3: Download + verify checksum
```bash
download_and_verify() {
    local url="$1"
    local expected_sha256="$2"
    local output="$3"

    echo "Downloading $url..."
    curl -sL --retry 3 --retry-delay 2 -o "$output" "$url"

    actual_sha256=$(sha256sum "$output" | awk '{print $1}')
    if [[ "$actual_sha256" != "$expected_sha256" ]]; then
        echo "❌ Checksum mismatch!"
        echo "  Expected: $expected_sha256"
        echo "  Got:      $actual_sha256"
        rm -f "$output"
        return 1
    fi
    echo "✅ Checksum verified"
}
```

### Scenario 4: SSL certificate expiry check
```bash
check_ssl_expiry() {
    local domain="$1"
    local warn_days="${2:-30}"

    expiry=$(curl -vI "https://$domain" 2>&1 | \
        grep -oP "expire date: \K.*" | \
        head -1)
    
    # Parse expiry date and calculate days remaining
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry" +%s)
    now_epoch=$(date +%s)
    days_remaining=$(( (expiry_epoch - now_epoch) / 86400 ))

    echo "Domain: $domain | Expires: $expiry | Days remaining: $days_remaining"
    
    if [[ $days_remaining -lt $warn_days ]]; then
        echo "⚠️  WARNING: Certificate expires in $days_remaining days!"
        return 1
    fi
}
```

### Scenario 5: Test API rate limiting
```bash
# Send N requests and track which ones were rate-limited (429)
for i in $(seq 1 20); do
    code=$(curl -s -o /dev/null -w "%{http_code}" https://api.example.com/endpoint)
    echo "Request $i: HTTP $code"
    [[ "$code" == "429" ]] && { echo "Rate limited at request $i"; break; }
    sleep 0.1
done
```

---

## 5.10 curl Gotchas ⚠️

### 1. `-f` fails silently — still get nothing on 404
```bash
curl -f https://example.com/missing   # Exit code 22, no output
# Check exit code:
if ! curl -sf https://example.com/health; then
    echo "Request failed (4xx or 5xx response)"
fi
```

### 2. Don't use `-k` in production
```bash
curl -k https://api.example.com  # Disables certificate validation — insecure!
# Use --cacert for custom CAs instead
```

### 3. `-d` encodes data but doesn't set Content-Type automatically for JSON
```bash
# WRONG: server may reject it as form data
curl -X POST -d '{"key":"val"}' https://api.example.com

# RIGHT: always set Content-Type for JSON
curl -X POST -H "Content-Type: application/json" -d '{"key":"val"}' https://api.example.com
```

### 4. Single quotes vs double quotes in -d
```bash
# Single quotes: no variable expansion (literal)
curl -d '{"user":"$USER"}' url     # Sends literal "$USER"

# Double quotes: variables expand
curl -d "{\"user\":\"$USER\"}" url  # Sends actual username — but need to escape "
# Better: use a file or heredoc for complex JSON
```

---

# Chapter 6: wget — Download Tool

> **Mental model:** wget is a download robot. Where curl is interactive (show me the response), wget is a downloader (save this to disk). It's better than curl for recursive, interrupted, or batch downloads.

---

## 6.1 Basic Usage

```bash
wget https://example.com/file.tar.gz          # Download to current directory
wget -O output.tar.gz https://example.com/file.tar.gz  # Custom output name
wget -q https://example.com/file.tar.gz       # Quiet (no output)
wget -P /opt/downloads/ https://example.com/file.tar.gz  # Save to directory
wget -nv https://example.com/file.tar.gz      # Not verbose (minimal output)
```

---

## 6.2 Resume and Retry

```bash
# Resume an interrupted download
wget -c https://example.com/large-file.tar.gz

# Retry on failure
wget --tries=5 --wait=3 https://example.com/file.tar.gz

# Retry with exponential backoff
wget --tries=5 --wait=3 --waitretry=10 https://example.com/file.tar.gz

# Limit download speed (be a good citizen)
wget --limit-rate=1M https://example.com/large-file.tar.gz
```

---

## 6.3 Authentication and Headers

```bash
# HTTP basic auth
wget --http-user=alice --http-password=secret https://private.example.com/file

# Custom headers
wget --header="Authorization: Bearer TOKEN" https://api.example.com/file
wget --header="Accept: application/json" https://api.example.com/data

# Custom user agent
wget --user-agent="MyBot/1.0" https://example.com

# Skip TLS verification (development only)
wget --no-check-certificate https://self-signed.example.com/file
```

---

## 6.4 Recursive Download / Mirroring

```bash
# Download a website for offline use
wget --mirror \
     --convert-links \         # Fix links for local navigation
     --adjust-extension \      # Add .html extension where needed
     --page-requisites \       # Download CSS, images, JS
     --no-parent \             # Don't go above the specified directory
     https://docs.example.com/

# Same as above, shorthand
wget -m -p -k -np https://docs.example.com/

# Download all files of a specific type from a page
wget -r -l1 --no-parent -A "*.pdf" https://docs.example.com/

# Download only up to 2 levels deep
wget -r -l2 https://docs.example.com/
```

---

## 6.5 Batch Download

```bash
# Download from a list of URLs
wget -i urls.txt           # One URL per line in urls.txt

# Download in background
wget -b https://example.com/large-file.tar.gz
# Logs to wget-log — check with:
tail -f wget-log

# Check if URL exists (spider mode — no download)
wget --spider https://example.com/file.tar.gz
# Exit code: 0=exists, 8=not found
```

---

## 6.6 wget vs curl — When to Use Which

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  USE wget WHEN:                    USE curl WHEN:                    │
  │                                                                      │
  │  ✅ Downloading files             ✅ API calls (POST, PUT, DELETE)  │
  │  ✅ Recursive/mirror downloads    ✅ Sending headers and data        │
  │  ✅ Resuming interrupted dl       ✅ Reading response body in script │
  │  ✅ Batch download from a list    ✅ Testing REST endpoints           │
  │  ✅ Background downloads          ✅ Uploading files                 │
  │  ✅ Mirroring entire websites     ✅ Timing measurements             │
  │                                   ✅ mTLS / custom certs             │
  │                                   ✅ Cookie handling                 │
  │                                   ✅ Streaming / piping             │
  │                                                                      │
  │  Both can: download files, set headers, basic auth, skip TLS        │
  └──────────────────────────────────────────────────────────────────────┘
```

---

## 6.7 Real-World Scenarios

### Scenario 1: Download daily database backup from a remote server
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
REMOTE="https://backups.internal.company.com/db"
LOCAL_DIR="/var/backups/db"

mkdir -p "$LOCAL_DIR"
wget -q \
    --header="Authorization: Bearer ${BACKUP_TOKEN}" \
    --timestamping \
    -P "$LOCAL_DIR" \
    "${REMOTE}/db_backup_${DATE}.sql.gz"

echo "Downloaded backup for $DATE"
```

### Scenario 2: Mirror documentation for offline access
```bash
wget --mirror --convert-links --adjust-extension --page-requisites \
    --no-parent --directory-prefix=/opt/docs \
    https://docs.kubernetes.io/docs/concepts/
```

### Scenario 3: Download all GitHub release assets
```bash
# Get release download URLs from API, then download
curl -s "https://api.github.com/repos/prometheus/prometheus/releases/latest" | \
    jq -r '.assets[].browser_download_url' | \
    grep "linux-amd64" | \
    wget -i -  # -i - = read URLs from stdin
```

---

## 6.8 wget Gotchas ⚠️

### 1. wget follows redirects by default (usually fine, but be aware)
```bash
# wget -nv shows the final URL after redirect
wget -nv https://bit.ly/some-short-link
```

### 2. `--no-parent` is essential for recursive downloads
```bash
# WITHOUT --no-parent: wget crawls UP the directory tree (downloads entire site!)
wget -r https://docs.example.com/api/v2/

# WITH --no-parent: stays within /api/v2/
wget -r --no-parent https://docs.example.com/api/v2/
```

### 3. wget by default creates `index.html?query=...` filenames
```bash
# Use --content-disposition to use the server's suggested filename
wget --content-disposition "https://api.example.com/download?id=123"
```

---

# Chapter 7: journalctl — Systemd Journal

> **Mental model:** journalctl is the query interface to systemd's journal — a structured, indexed binary log store. Unlike `/var/log/*.log` text files, the journal stores structured data (you can filter by field, time, unit, priority without grepping text).

---

## 7.1 Basic Usage

```bash
journalctl                     # All logs from current boot, oldest first
journalctl -f                  # Follow (tail -f equivalent) — live logs
journalctl -n 50               # Last 50 lines
journalctl -n 100 -f           # Last 100 lines then follow
journalctl --no-pager          # Output all at once (no less pager)
journalctl -r                  # Reverse: newest first
```

---

## 7.2 Filter by Unit (Service)

```bash
journalctl -u nginx.service            # All logs for nginx
journalctl -u nginx                    # .service is implied
journalctl -u nginx -f                 # Follow nginx logs
journalctl -u nginx -n 100             # Last 100 lines of nginx logs
journalctl -u nginx -u myapp           # Multiple units simultaneously
journalctl _SYSTEMD_UNIT=nginx.service # Alternative: field filter
```

---

## 7.3 Filter by Time

```bash
# Since and until
journalctl --since "2024-01-15 10:00:00" --until "2024-01-15 11:00:00"
journalctl --since "1 hour ago"
journalctl --since "2 days ago"
journalctl --since today
journalctl --since yesterday

# Current boot only
journalctl -b             # Current boot
journalctl -b 0           # Current boot (same)
journalctl -b -1          # Previous boot
journalctl -b -2          # Boot before that

# List available boots
journalctl --list-boots
```

---

## 7.4 Filter by Priority Level

```bash
# Priority levels (0=emerg → 7=debug):
# 0=emerg 1=alert 2=crit 3=err 4=warning 5=notice 6=info 7=debug

journalctl -p err                   # Error and above (err, crit, alert, emerg)
journalctl -p warning               # Warning and above
journalctl -p debug                 # All messages including debug
journalctl -p 3                     # Numeric: 3=err and above
journalctl -p err..warning          # Range: between err and warning

# Combine with unit
journalctl -u nginx -p err
journalctl -u nginx -p err --since "1 hour ago"
```

---

## 7.5 Output Formats

```bash
journalctl -o short            # Default: short human-readable
journalctl -o short-iso        # ISO timestamp (2024-01-15T10:23:45+05:30)
journalctl -o cat              # Message only (no timestamp, no hostname)
journalctl -o json             # JSON (one object per line)
journalctl -o json-pretty      # JSON, formatted for humans
journalctl -o verbose          # All fields, full detail
journalctl -o export           # Binary export format (for piping to journalctl --import)

# JSON output is powerful for parsing with jq
journalctl -u nginx -o json --no-pager | jq -r '.MESSAGE' | grep ERROR
journalctl -u myapp -o json -n 100 | jq -r '[.PRIORITY, .__REALTIME_TIMESTAMP, .MESSAGE] | @tsv'
```

---

## 7.6 Filter by Fields

The journal stores structured key=value data. You can filter on any field:

```bash
# Filter by executable/command name
journalctl _COMM=sshd              # Logs from the sshd binary
journalctl _COMM=nginx

# Filter by PID
journalctl _PID=1234

# Filter by user ID
journalctl _UID=1000               # Logs from user with UID 1000

# Filter by hostname (useful in centralized logging)
journalctl _HOSTNAME=web-server-01

# Filter by kernel messages
journalctl -k                      # Kernel messages only (like dmesg)
journalctl -k | grep -i "oom\|killed\|out of memory"

# Combine filters (AND logic)
journalctl _COMM=sshd _PRIORITY=3   # sshd AND error level

# List all available field names
journalctl -F _COMM                 # Show all unique values for _COMM field
journalctl -F _SYSTEMD_UNIT        # All units that have logged
```

---

## 7.7 Journal Disk Usage and Cleanup

```bash
# Check disk usage
journalctl --disk-usage
# Output: Archived and active journals take up 2.1G in the filesystem.

# Clean up: keep only last N days
journalctl --vacuum-time=7d

# Clean up: keep under specified size
journalctl --vacuum-size=500M

# Clean up: keep only N files
journalctl --vacuum-files=5

# Configure persistent journal size in /etc/systemd/journald.conf:
# SystemMaxUse=500M
# MaxRetentionSec=7day
# Then restart: systemctl restart systemd-journald
```

---

## 7.8 Persistent Journal Setup

By default on many systems, the journal is in RAM (`/run/log/journal/`) and lost on reboot:

```bash
# Check if journal is persistent
ls /var/log/journal/    # If this directory exists: persistent ✅
ls /run/log/journal/    # If only this: volatile (lost on reboot) ⚠️

# Enable persistent journal
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald

# Or set Storage=persistent in /etc/systemd/journald.conf
```

---

## 7.9 Real-World Scenarios

### Scenario 1: Debug a service that failed to start
```bash
# Check service status
systemctl status myapp.service

# Get ALL logs from the last boot for this service
journalctl -u myapp.service -b --no-pager

# Get only errors since yesterday
journalctl -u myapp.service -p err --since yesterday

# Watch live as you restart the service
journalctl -u myapp.service -f &
systemctl restart myapp.service
```

### Scenario 2: Find OOM-killed processes
```bash
# Kernel OOM killer logs
journalctl -k | grep -E "oom|killed|Out of memory" | tail -20

# Which processes were killed
journalctl -k | grep "Killed process" | awk '{print $NF, $(NF-1)}' | sort | uniq -c | sort -rn
```

### Scenario 3: Export logs for a support ticket
```bash
# Export last 24h of logs for myapp to a file
journalctl -u myapp.service --since "24 hours ago" \
    --no-pager -o short-iso > /tmp/myapp-logs-$(date +%Y%m%d).txt

# Compress and send
gzip /tmp/myapp-logs-$(date +%Y%m%d).txt
```

### Scenario 4: Monitor multiple services simultaneously
```bash
journalctl -u nginx -u myapp-api -u myapp-worker -f
```

### Scenario 5: Parse structured logs with jq
```bash
# Extract error messages as JSON for analysis
journalctl -u myapp -p err --since "1 hour ago" \
    -o json --no-pager | \
    jq -r '{time: (.__REALTIME_TIMESTAMP | tonumber / 1000000 | strftime("%Y-%m-%d %H:%M:%S")), msg: .MESSAGE}' | \
    jq -r '[.time, .msg] | @tsv'
```

### Scenario 6: Disk space recovery from huge journal
```bash
# Check how much space journals use
du -sh /var/log/journal/

# Vacuum to free space
journalctl --vacuum-size=200M
journalctl --vacuum-time=14d

# Verify
journalctl --disk-usage
```

---

## 7.10 journalctl vs Classic Log Files

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │              journalctl          vs       /var/log/ files            │
  │                                                                      │
  │  Format:    Structured binary            Plain text                  │
  │  Index:     Always indexed               No index (grep needed)      │
  │  Filtering: By any field natively        grep + awk required         │
  │  Space:     Compressed automatically     Manual rotation/gzip        │
  │  Corruption:Self-detecting checksums     Silent corruption possible  │
  │  Access:    journalctl command           Any text tool               │
  │  Boot logs: Per-boot separated          Mixed in same files         │
  │  Forwarding:rsyslog/syslog bridge        Direct                      │
  │                                                                      │
  │  Many services ALSO write to /var/log for compatibility.            │
  │  journalctl and /var/log coexist on most systems.                   │
  └──────────────────────────────────────────────────────────────────────┘
```

---

## 7.11 journalctl Gotchas ⚠️

### 1. Journal may not be persistent by default
```bash
# Check: if /var/log/journal/ doesn't exist, logs are lost on reboot
ls /var/log/journal/ || echo "Journal is NOT persistent"
```

### 2. `-f` and `--no-pager` can conflict
```bash
journalctl -f --no-pager   # Fine — follow mode never pages
journalctl --no-pager      # Required in scripts (otherwise blocks on 'q')
```

### 3. Priority levels are inclusive DOWN (lower number = higher priority)
```bash
journalctl -p err   # Shows: err (3), crit (2), alert (1), emerg (0)
# NOT just error messages — it's "err and worse"
```

### 4. Time filters use local timezone
```bash
# Be explicit when in doubt
journalctl --since "2024-01-15 10:00:00 UTC"
journalctl --since "2024-01-15 10:00:00" TZ=UTC  # May not work on all systems
```

---

# Chapter 8: Combo Scenarios — Real-World Pipelines

> **These are the 10 scenarios that appear on actual DevOps job tasks.** Each uses multiple tools together.

---

## Scenario 1: Nginx Log Analysis — Find the DDoS Source

```bash
#!/bin/bash
# Identify top attacking IPs, request patterns, and time distribution

LOG="/var/log/nginx/access.log"
THRESHOLD=1000  # requests per IP to flag as potential attack

echo "=== TOP 20 IPs BY REQUEST COUNT (last hour) ==="
grep "$(date '+%d/%b/%Y:%H')" "$LOG" | \
    awk '{print $1}' | \
    sort | uniq -c | sort -rn | \
    awk -v t="$THRESHOLD" '$1 >= t {print "🚨 POTENTIAL ATTACK:", $0} $1 < t {print $0}' | \
    head -20

echo ""
echo "=== TOP REQUESTED PATHS ==="
awk '{print $7}' "$LOG" | \
    sed 's/?.*$//' | \           # Strip query strings
    sort | uniq -c | sort -rn | \
    head -10

echo ""
echo "=== HTTP STATUS DISTRIBUTION ==="
awk '{print $9}' "$LOG" | \
    grep -E "^[0-9]{3}$" | \
    sort | uniq -c | sort -rn

echo ""
echo "=== REQUESTS PER HOUR (last 24h) ==="
grep "$(date --date='1 day ago' '+%d/%b/%Y')\|$(date '+%d/%b/%Y')" "$LOG" | \
    awk '{print substr($4, 2, 14)}' | \  # Extract YYYY:HH
    sort | uniq -c
```

---

## Scenario 2: SSL Certificate Expiry Checker

```bash
#!/bin/bash
# Check SSL expiry for a list of domains
# Uses: curl + awk + date

DOMAINS=(
    "myapp.example.com"
    "api.example.com"
    "admin.example.com"
)
WARN_DAYS=30

for domain in "${DOMAINS[@]}"; do
    # Get certificate expiry date using curl
    expiry=$(curl -vsI "https://$domain" 2>&1 | \
        grep -i "expire date" | \
        sed 's/.*expire date: //')

    if [[ -z "$expiry" ]]; then
        echo "❌ CANNOT CONNECT: $domain"
        continue
    fi

    # Calculate days remaining
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null)
    now_epoch=$(date +%s)
    days=$(( (expiry_epoch - now_epoch) / 86400 ))

    if [[ $days -lt 0 ]]; then
        echo "🔴 EXPIRED: $domain (expired $((days * -1)) days ago)"
    elif [[ $days -lt $WARN_DAYS ]]; then
        echo "🟡 EXPIRING SOON: $domain ($days days left — expires $expiry)"
    else
        echo "✅ OK: $domain ($days days left)"
    fi
done
```

---

## Scenario 3: Find Hardcoded Secrets in a Codebase

```bash
#!/bin/bash
# Security audit: find hardcoded credentials
# Uses: grep + awk + sed

SEARCH_DIR="${1:-.}"
REPORT="/tmp/secrets_audit_$(date +%Y%m%d_%H%M%S).txt"

echo "=== Security Audit: $SEARCH_DIR ===" | tee "$REPORT"
echo "Date: $(date)" | tee -a "$REPORT"
echo "" | tee -a "$REPORT"

# Patterns to search for
PATTERNS=(
    'password\s*=\s*["\x27][^"\x27]{4,}'
    'api_key\s*=\s*["\x27][^"\x27]{10,}'
    'secret\s*=\s*["\x27][^"\x27]{8,}'
    'AWS_ACCESS_KEY_ID\s*=\s*AK[A-Z0-9]{18}'
    'AKIA[A-Z0-9]{16}'                          # AWS Access Key
    'ghp_[a-zA-Z0-9]{36}'                       # GitHub token
    'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+' # JWT
)

EXCLUDE_DIRS=".git,node_modules,vendor,.venv,__pycache__"
EXCLUDE_PATTERNS="example\|sample\|placeholder\|dummy\|test\|fake"

for pattern in "${PATTERNS[@]}"; do
    matches=$(grep -rniE "$pattern" "$SEARCH_DIR" \
        --exclude-dir={"$EXCLUDE_DIRS"} \
        --include="*.py" --include="*.js" --include="*.ts" \
        --include="*.yaml" --include="*.yml" --include="*.env" \
        --include="*.conf" --include="*.config" \
        2>/dev/null | \
        grep -v "$EXCLUDE_PATTERNS" | \
        # Redact the actual value
        sed -E 's/(=\s*["\x27])[^"\x27]{4,}(["\x27])/\1***REDACTED***\2/g')

    if [[ -n "$matches" ]]; then
        echo "⚠️  PATTERN: $pattern" | tee -a "$REPORT"
        echo "$matches" | tee -a "$REPORT"
        echo "" | tee -a "$REPORT"
    fi
done

echo "Report saved to: $REPORT"
```

---

## Scenario 4: Automated API Health Monitor

```bash
#!/bin/bash
# Monitor a list of API endpoints and alert on failures
# Uses: curl + jq + grep + awk

ENDPOINTS=(
    "https://api.example.com/health|200|API Health"
    "https://api.example.com/v2/status|200|API Status"
    "https://admin.example.com/ping|200|Admin"
)
SLACK_URL="${SLACK_WEBHOOK_URL}"
FAILURES=0

check_endpoint() {
    local url="$1"
    local expected_code="$2"
    local name="$3"

    result=$(curl -s -o /dev/null \
        -w "%{http_code}|%{time_total}|%{remote_ip}" \
        --connect-timeout 5 --max-time 15 "$url" 2>/dev/null)

    http_code=$(echo "$result" | cut -d'|' -f1)
    time_total=$(echo "$result" | cut -d'|' -f2)
    remote_ip=$(echo "$result" | cut -d'|' -f3)

    # Convert time to ms
    time_ms=$(echo "$time_total * 1000" | awk '{printf "%.0f", $1}')

    if [[ "$http_code" == "$expected_code" ]]; then
        echo "✅ $name: HTTP $http_code | ${time_ms}ms | IP: $remote_ip"
    else
        echo "❌ $name: Expected HTTP $expected_code, got $http_code"
        FAILURES=$((FAILURES + 1))

        # Alert to Slack
        if [[ -n "$SLACK_URL" ]]; then
            curl -s -X POST "$SLACK_URL" \
                -H "Content-Type: application/json" \
                -d "{\"text\": \"🚨 ALERT: $name returned HTTP $http_code (expected $expected_code)\"}"
        fi
    fi
}

echo "=== API Health Check: $(date) ==="
for entry in "${ENDPOINTS[@]}"; do
    IFS='|' read -r url code name <<< "$entry"
    check_endpoint "$url" "$code" "$name"
done

echo ""
echo "Result: $FAILURES failures"
exit "$FAILURES"
```

---

## Scenario 5: Log Error Rate Monitor with journalctl

```bash
#!/bin/bash
# Calculate error rate per service from journal
# Uses: journalctl + awk + sed

SERVICES=("nginx" "myapp-api" "myapp-worker" "postgresql")
WINDOW_MINUTES=60
THRESHOLD_RATE=0.05  # 5% error rate threshold

for service in "${SERVICES[@]}"; do
    # Count total and error logs in the window
    total=$(journalctl -u "$service" \
        --since "$WINDOW_MINUTES minutes ago" \
        --no-pager -q 2>/dev/null | wc -l)

    errors=$(journalctl -u "$service" -p err \
        --since "$WINDOW_MINUTES minutes ago" \
        --no-pager -q 2>/dev/null | wc -l)

    if [[ $total -eq 0 ]]; then
        echo "⚪ $service: No logs in last ${WINDOW_MINUTES}m"
        continue
    fi

    # Calculate error rate
    rate=$(awk "BEGIN {printf \"%.4f\", $errors / $total}")
    pct=$(awk "BEGIN {printf \"%.1f\", $rate * 100}")

    # Flag if above threshold
    above_threshold=$(awk "BEGIN {print ($rate > $THRESHOLD_RATE) ? \"yes\" : \"no\"}")

    if [[ "$above_threshold" == "yes" ]]; then
        echo "🔴 $service: ${pct}% error rate ($errors/$total) — ABOVE THRESHOLD"
    else
        echo "✅ $service: ${pct}% error rate ($errors/$total)"
    fi
done
```

---

## Scenario 6: Config Drift Detector

```bash
#!/bin/bash
# Compare running server config against expected config
# Uses: curl + sed + diff + awk

EXPECTED_CONFIG="./expected-nginx.conf"
LIVE_SERVER="https://admin.example.com/api/config/nginx"
AUTH_TOKEN="${ADMIN_TOKEN}"
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Fetch current live config
curl -sf \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -o "$TMP_DIR/live.conf" \
    "$LIVE_SERVER"

# Normalize both configs before comparing
# Remove comments, blank lines, trailing whitespace
normalize() {
    sed -E '/^[[:space:]]*(#|$)/d' "$1" | \
        sed 's/[[:space:]]*$//' | \
        sed 's/^[[:space:]]*//' | \
        sort
}

normalize "$EXPECTED_CONFIG" > "$TMP_DIR/expected_normalized.conf"
normalize "$TMP_DIR/live.conf" > "$TMP_DIR/live_normalized.conf"

if diff -q "$TMP_DIR/expected_normalized.conf" "$TMP_DIR/live_normalized.conf" > /dev/null; then
    echo "✅ No config drift detected"
    exit 0
else
    echo "⚠️  Config drift detected!"
    echo ""
    diff --color=auto -u "$TMP_DIR/expected_normalized.conf" "$TMP_DIR/live_normalized.conf" | \
        awk 'NR<=3 {next} /^\-/ {print "  EXPECTED: " substr($0,2)} /^\+/ {print "  LIVE:     " substr($0,2)} /^ / {print "  SAME:     " substr($0,2)}'
    exit 1
fi
```

---

## Scenario 7: System Health Dashboard

```bash
#!/bin/bash
# One-script system health overview
# Uses: grep + awk + sed + curl + journalctl

DIVIDER="────────────────────────────────────────────"

header() { echo ""; echo "  $DIVIDER"; echo "  $1"; echo "  $DIVIDER"; }

header "SYSTEM OVERVIEW — $(hostname) — $(date)"

# CPU and Memory
header "CPU & MEMORY"
top -bn1 | grep -E "^(Cpu|%Cpu|MiB Mem)" | \
    sed 's/Cpu(s)://; s/MiB Mem :/Memory:/' | \
    awk '{printf "  %-12s %s\n", $1, $0}'

# Disk usage (alert on >80%)
header "DISK USAGE"
df -h | awk 'NR==1 {next} {
    gsub(/%/, "", $5)
    icon = ($5+0 >= 90) ? "🔴" : ($5+0 >= 80) ? "🟡" : "✅"
    printf "  %s %-30s %5s%% used (%s free)\n", icon, $6, $5, $4
}'

# Top 5 memory processes
header "TOP 5 MEMORY CONSUMERS"
ps aux --sort=-%mem | awk 'NR==1 {next} NR<=6 {
    printf "  %-10s %5s%% mem  %5s%% cpu  %s\n", $1, $4, $3, $11
}'

# Failed systemd services
header "FAILED SERVICES"
systemctl list-units --state=failed --no-legend 2>/dev/null | \
    awk '{printf "  🔴 %s\n", $1}' || echo "  ✅ No failed services"

# Recent errors in journal (last 10 minutes)
header "RECENT ERRORS (last 10 minutes)"
journalctl -p err --since "10 minutes ago" --no-pager -q 2>/dev/null | \
    tail -10 | \
    sed 's/^/  /' || echo "  ✅ No recent errors"

# Network connections summary
header "NETWORK CONNECTIONS"
ss -tuln 2>/dev/null | awk 'NR>1 {print $5}' | \
    grep -oE ":[0-9]+" | sort -t: -k2 -n | uniq -c | \
    awk '{printf "  Port %-6s %d listeners\n", $2, $1}' | head -10
```

---

## Scenario 8: Kubernetes Pod Log Parser

```bash
#!/bin/bash
# Parse K8s pod logs for errors and generate a summary
# Uses: kubectl + grep + awk + sort

NAMESPACE="${1:-default}"
SINCE="${2:-1h}"

echo "=== K8s Error Summary: namespace=$NAMESPACE, since=$SINCE ==="
echo ""

# Get all pods in namespace
pods=$(kubectl get pods -n "$NAMESPACE" \
    --field-selector=status.phase=Running \
    -o jsonpath='{.items[*].metadata.name}')

declare -A pod_errors

for pod in $pods; do
    # Get logs, filter errors, count by type
    error_count=$(kubectl logs -n "$NAMESPACE" "$pod" \
        --since="$SINCE" 2>/dev/null | \
        grep -ciE "error|exception|fatal|panic" || echo "0")

    pod_errors["$pod"]=$error_count

    if [[ $error_count -gt 0 ]]; then
        echo "🔴 $pod: $error_count errors"
        
        # Show top error patterns
        echo "   Top error messages:"
        kubectl logs -n "$NAMESPACE" "$pod" --since="$SINCE" 2>/dev/null | \
            grep -iE "error|exception|fatal" | \
            # Normalize timestamps and UUIDs for grouping
            sed -E 's/[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:Z.]+/TIMESTAMP/g' | \
            sed -E 's/[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}/UUID/g' | \
            sort | uniq -c | sort -rn | head -5 | \
            awk '{printf "   %5dx %s\n", $1, substr($0, index($0,$2))}'
        echo ""
    else
        echo "✅ $pod: No errors"
    fi
done
```

---

## Scenario 9: Automated Report Emailer

```bash
#!/bin/bash
# Generate a report and send to Slack
# Uses: awk + sed + journalctl + curl

REPORT_DATE=$(date '+%Y-%m-%d')
SLACK_URL="${SLACK_WEBHOOK_URL}"
SERVICES=("nginx" "myapp-api" "postgresql")

# Build the report as JSON for Slack
generate_report() {
    local blocks='[{"type":"header","text":{"type":"plain_text","text":"Daily Report - '"$REPORT_DATE"'"}}'

    for service in "${SERVICES[@]}"; do
        errors=$(journalctl -u "$service" \
            --since "24 hours ago" -p err \
            --no-pager -q 2>/dev/null | wc -l)

        restarts=$(journalctl -u "$service" \
            --since "24 hours ago" \
            --no-pager -q 2>/dev/null | \
            grep -c "Started\|started" || echo "0")

        status=$(systemctl is-active "$service" 2>/dev/null)
        icon=$([[ "$status" == "active" ]] && echo "✅" || echo "🔴")

        blocks+=',{"type":"section","text":{"type":"mrkdwn","text":"'"$icon *$service* | Status: $status | Errors: $errors | Restarts: $restarts"'"}}'
    done

    blocks+=']'
    echo "$blocks"
}

curl -s -X POST "$SLACK_URL" \
    -H "Content-Type: application/json" \
    -d "{\"blocks\": $(generate_report)}"
```

---

## Scenario 10: Multi-Tool Security Audit Pipeline

```bash
#!/bin/bash
# Full security audit combining all tools
# Uses: grep + awk + sed + curl + journalctl

echo "==============================="
echo "  SECURITY AUDIT — $(hostname)"
echo "  $(date)"
echo "==============================="

# 1. Failed SSH attempts (brute force detection)
echo ""
echo "[1] SSH BRUTE FORCE ATTEMPTS (last 24h)"
journalctl -u sshd --since "24 hours ago" --no-pager -q 2>/dev/null | \
    grep "Failed password" | \
    awk '{print $(NF-3)}' | \
    sort | uniq -c | sort -rn | \
    awk '$1 > 10 {printf "  🚨 %-20s %d attempts\n", $2, $1}
         $1 <= 10 {printf "  ⚠️  %-20s %d attempts\n", $2, $1}' | \
    head -20

# 2. Root login attempts
echo ""
echo "[2] ROOT LOGIN ATTEMPTS (last 24h)"
journalctl -u sshd --since "24 hours ago" --no-pager -q 2>/dev/null | \
    grep -i "root" | \
    awk '{print $(NF-3)}' | \
    sort | uniq -c | sort -rn | head -10 | \
    sed 's/^/  🔴 /'

# 3. Users with UID 0 (should only be root)
echo ""
echo "[3] USERS WITH UID 0 (should only be root)"
awk -F: '$3 == 0 {print $1}' /etc/passwd | \
    grep -v "^root$" | \
    while read -r u; do echo "  🚨 Non-root user with UID 0: $u"; done || \
    echo "  ✅ Only root has UID 0"

# 4. World-writable files (security risk)
echo ""
echo "[4] WORLD-WRITABLE FILES IN /etc"
find /etc -type f -perm -o+w 2>/dev/null | \
    head -10 | \
    sed 's/^/  🚨 /' || echo "  ✅ None found"

# 5. Open ports
echo ""
echo "[5] LISTENING PORTS"
ss -tlnp 2>/dev/null | awk 'NR>1 {print $4, $6}' | \
    sed 's/0\.0\.0\.0:\|:::/ANY:/' | \
    awk '{printf "  PORT %-25s  PROCESS: %s\n", $1, $2}' | \
    grep -v "^$" | sort

# 6. Check for suspicious curl/wget in cron
echo ""
echo "[6] CRON JOBS WITH NETWORK ACCESS"
cat /etc/crontab /etc/cron.d/* 2>/dev/null | \
    grep -v "^#\|^$" | \
    grep -iE "curl|wget|nc |ncat" | \
    sed 's/^/  ⚠️  /'

echo ""
echo "==============================="
echo "  Audit complete"
echo "==============================="
```

---

## Quick Reference Cheatsheet

```
  ┌──────────────────────────────────────────────────────────────────────┐
  │  GREP QUICK REFERENCE                                                │
  │  grep -i         case-insensitive                                    │
  │  grep -n         show line numbers                                   │
  │  grep -c         count matches                                       │
  │  grep -v         invert (non-matching)                               │
  │  grep -r         recursive                                           │
  │  grep -l         filenames only                                      │
  │  grep -o         matching part only                                  │
  │  grep -A/-B/-C   context lines (after/before/both)                  │
  │  grep -E         ERE (use +?|() without escaping)                   │
  │  grep -P         PCRE (\d \w \s lookahead)                          │
  ├──────────────────────────────────────────────────────────────────────┤
  │  SED QUICK REFERENCE                                                 │
  │  sed 's/old/new/'       replace first per line                      │
  │  sed 's/old/new/g'      replace all per line                        │
  │  sed -i 's/old/new/g'   in-place edit                               │
  │  sed '/pattern/d'       delete matching lines                        │
  │  sed -n '/pattern/p'    print matching lines only                   │
  │  sed '5,10d'            delete lines 5-10                           │
  │  sed -E                 ERE mode                                     │
  │  sed 's|/|\\|g'        use | as delimiter                           │
  ├──────────────────────────────────────────────────────────────────────┤
  │  AWK QUICK REFERENCE                                                 │
  │  awk '{print $1}'       first field                                  │
  │  awk -F: '{print $1}'   colon delimiter                              │
  │  awk 'NR==5'            only line 5                                  │
  │  awk '$3>100'           conditional filter                           │
  │  awk '{sum+=$3} END...' sum a column                                 │
  │  awk '{count[$1]++}...' count by key                                 │
  ├──────────────────────────────────────────────────────────────────────┤
  │  CURL QUICK REFERENCE                                                │
  │  curl -s              silent                                         │
  │  curl -f              fail on HTTP error (non-zero exit code)       │
  │  curl -L              follow redirects                               │
  │  curl -o file         save to file                                  │
  │  curl -X POST -d '{}'  POST with body                               │
  │  curl -H "Auth: ..."   set header                                   │
  │  curl -w "%{http_code}" print status code                           │
  ├──────────────────────────────────────────────────────────────────────┤
  │  JOURNALCTL QUICK REFERENCE                                          │
  │  journalctl -u svc     filter by service                            │
  │  journalctl -f         follow live                                   │
  │  journalctl -p err     error level and above                        │
  │  journalctl -b         current boot                                  │
  │  journalctl --since "1h ago"  time filter                           │
  │  journalctl -o json    structured JSON output                        │
  │  journalctl --vacuum-size=500M  free disk space                     │
  └──────────────────────────────────────────────────────────────────────┘
```

---

*Source: [Linux Admin Handbook §3](linux_admin_handbook.md) · [Scripting Handbook §5](../scripting/scripting_handbook.md)*
