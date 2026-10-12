# Automated Regression Isolation with git bisect

Comprehensive technical reference for authoring automated test predicates, handling unbuildable commits, and executing git bisect.

---

## 1. How git bisect Works

`git bisect` performs a binary search through Git commit history to find the exact commit that introduced a defect:
$$\text{Steps Required} \approx \lceil \log_2(N) \rceil$$
For a history of 1,000 commits, `git bisect` isolates the culprit commit in only $\approx 10$ steps.

---

## 2. Exit Code Invariants for `git bisect run`

When automating bisect via `git bisect run <script>`:

| Script Exit Code | Interpretation by `git bisect` | Action Taken |
|---|---|---|
| **`0`** | **GOOD** | The commit works correctly. Marks revision good; searches newer commits. |
| **`1` through `127` (except `125`)** | **BAD** | The regression is present. Marks revision bad; searches older commits. |
| **`125`** | **SKIP** | **The commit cannot be tested** (fails to compile, missing dependency, broken toolchain). `git bisect` skips this commit and tests an adjacent revision. |

> [!CRITICAL]
> **The Exit Code 125 Invariant**:
> If a commit fails to compile during bisect, your test script MUST return exit code **125**.
> If you return `1`, `git bisect` treats the compilation error as the regression itself and terminates early with a completely false culprit commit!

---

## 3. Template: Robust Automated Bisect Predicate

```bash
#!/usr/bin/env bash
# bisect_test.sh - Robust predicate script for git bisect run
set -uo pipefail

# 1. Clean workspace to avoid stale build artifacts
git clean -fdx -e bisect_test.sh >/dev/null 2>&1

# 2. Attempt compilation
if ! make -j"$(nproc)" >/dev/null 2>&1; then
    echo "[BISECT SKIP] Commit failed to compile; skipping."
    exit 125
fi

# 3. Execute the specific test case
if ./build/bin/my_app --test-feature; then
    echo "[BISECT GOOD] Feature passed."
    exit 0
else
    echo "[BISECT BAD] Feature failed (regression reproduced)."
    exit 1
fi
```

### Running the Bisect Session:
```bash
# Start bisect session
git bisect start

# Mark known boundaries
git bisect bad HEAD
git bisect good v1.4.0

# Hand over control to automated script
git bisect run ./bisect_test.sh

# When bisect finishes, git outputs:
# <SHA> is the first bad commit
# commit <SHA>
# Author: ...

# Reset repository back to original HEAD when finished
git bisect reset
```

---

## 4. Using Git Worktrees for Isolated Bisecting

Never run bisect directly in your active development directory if you have uncommitted changes or active editors open. Use `git worktree`:

```bash
# Create isolated worktree for bisect session
git worktree add /tmp/bisect-worktree master
cd /tmp/bisect-worktree
git bisect start HEAD v1.4.0
git bisect run /path/to/bisect_test.sh
cd -
git worktree remove /tmp/bisect-worktree
```
