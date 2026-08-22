# OpenAI Codex Adapter & Integration Guide

## 1. Overview
This directory contains configuration templates and manifests enabling compatibility with **OpenAI Codex** and ChatGPT plugins.

## 2. Key Integration Components
1. **Repository Instructions (`AGENTS.md`)**:
   Codex automatically indexes `AGENTS.md` at the repository root. It serves as persistent, durable guidance detailing the research-first methodology, safety tiers, and available skill workflows.
2. **Skill Definitions (`agents/openai.yaml`)**:
   Declares the skill entry points and their relative paths within the repository.
3. **Packaging (`scripts/package-skills.py --target codex`)**:
   Compiles canonical skills into a standalone Codex-compatible skill directory while verifying path integrity.

## 3. Usage with Codex
In an interactive Codex terminal session, skills can be invoked via:
```text
$linux-engineer How do I harden an unprivileged systemd service?
$linux-research Investigate kernel commit history for epoll_wait
$linux-environment Detect active toolchains and kernel version
```
