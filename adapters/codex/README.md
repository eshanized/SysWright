# OpenAI Codex Integration

SysWright uses the portable Agent Skills format. Codex discovers skills from these locations:

- Repository scope: `.agents/skills/<skill-name>/SKILL.md`
- User scope: `~/.agents/skills/<skill-name>/SKILL.md`
- Administrator scope: `/etc/codex/skills/<skill-name>/SKILL.md`

The canonical source remains `skills/` in this repository. Do not maintain a second copy of skill instructions in this adapter.

## Build a Codex bundle

From the repository root:

```bash
python3 scripts/package-skills.py --target codex --output dist/
```

The resulting bundle has this structure:

```text
dist/codex-package/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── linux-engineer/
│       │   └── SKILL.md
│       └── ...
└── references/
```

## Install for the current user

Review the generated bundle, then copy its skills into the Codex user-level directory:

```bash
mkdir -p "$HOME/.agents"
cp -a dist/codex-package/.agents/skills "$HOME/.agents/"
```

For repository-scoped use, copy `dist/codex-package/.agents/skills` into the target repository's `.agents/` directory instead.

The included `AGENTS.md` is repository-level guidance. Do not copy it into a user's home directory as a global instruction file; place it only in a repository where those instructions are intended to apply.

## Updates and removal

Rebuild the bundle from the desired SysWright revision. Review differences before replacing an existing installation; the packager intentionally refuses to overwrite existing output directories.

Remove only the SysWright skill directories from the chosen scope. Do not delete the entire `.agents/skills` directory if it contains skills from other projects.

Codex may need a restart or skill refresh after installation.

## Optional Codex UI metadata

Codex supports optional `agents/openai.yaml` metadata **inside an individual skill directory**. It is not a repository-wide catalog manifest. SysWright does not currently generate per-skill UI metadata; the portable `SKILL.md` files remain usable without it.

## References

- [Build skills — OpenAI documentation](https://learn.chatgpt.com/docs/build-skills)
- [Agent Skills specification](https://agentskills.io/specification)
