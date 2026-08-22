# Multi-Agent Compatibility Guide

## 1. Supported Agent Environments

Linux Engineering is designed around the open standard **Agent Skills specification** (`agentskills.io`). Because the canonical skills in `skills/` avoid proprietary formatting, they work natively across multiple agent platforms.

### 1.1 Google Antigravity CLI / Gemini Code Assist
- **Native Support**: Antigravity natively loads skills from `.agents/skills/` or declared workspaces.
- **Workflow**: The central `linux-engineer` orchestrates tasks and delegates research to `linux-research` using native subagents.

### 1.2 Cursor & Windsurf
- **Rules Integration**: Developers using Cursor or Windsurf can include references to `references/engineering-principles.md` and `references/safety-policy.md` inside `.cursorrules` or `.windsurfrules`.
- **Skill Usage**: The Markdown instructions in `skills/*/SKILL.md` can be read directly by the agent upon task assignment.

### 1.3 Roo Code / Cline
- **Custom Prompts & Modes**: The foundation skills map directly to custom modes (e.g., `linux-research` as an architecture/research mode, and `linux-engineer` as an orchestrator mode).
