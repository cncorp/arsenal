# Prime CC
> Build understanding of arsenal structure and Claude Code configuration for this project.
>
> **When to use**: First Claude Code conversation in new worktree, after arsenal updates, configuration changes
> **When to skip**: Bug fixes, small features, test debugging when arsenal is unchanged
>
> **Token Impact**: ~3-5k tokens (~3% of context)

## Run
ls -la arsenal/                                    # Show arsenal top-level structure
ls arsenal/dot-claude/agents/ | wc -l             # Count available agents
ls arsenal/dot-claude/commands/ | wc -l           # Count available commands
ls arsenal/dot-claude/skills/ | wc -l             # Count available skills
git log --oneline arsenal/ | head -5              # Recent arsenal updates
git status | grep -E "(\.claude|arsenal)"         # Check symlink status

## Read
arsenal/README.md                                  # Arsenal overview and structure
arsenal/dot-claude/settings.local.json            # Claude Code configuration

## Understand Key Relationships
- **Source of truth**: `/arsenal/dot-claude/` → **Symlinked to**: `/.claude/`
- **System prompts**: `/arsenal/system-prompts/` → **Symlinked to**: `/AGENTS.md`
- **Pre-commit**: `/arsenal/pre-commit-scripts/` → **Symlinked to**: `/.pre-commit-scripts/`

## Available Resources Overview
Arsenal provides:
- **6 specialized agents** (git-reader, pytest-test-reviewer, mypy-error-fixer, etc.)
- **20+ slash commands** (/planit, /buildit, /prime, /review-code, etc.)
- **7+ skills** (test-runner, langfuse-debugger, semantic-search, etc.)
- **Mandatory workflows** enforced via session-start hook

## Critical Bootstrap Knowledge
1. **Skills are MANDATORY workflows** - not optional tools
2. **test-runner skill** - MUST be used after every code change (4-step process)
3. **Session start hook** - automatically loads getting-started skill every session
4. **Three Foundational Rules**:
   - Skills give you capabilities
   - Search for skills first (`ls .claude/skills/`)
   - If a skill exists, you MUST use it

## Quick Validation Commands
```bash
# Verify arsenal is properly linked
readlink .claude                    # Should point to arsenal/dot-claude
readlink AGENTS.md                  # Should point to arsenal/system-prompts/AGENTS.md

# Check if skills are loaded
ls .claude/skills/getting-started/  # Should contain SKILL.md

# Verify Docker services (optional)
cd arsenal && docker-compose ps     # Check semantic-search status
```

## Note
- **Arsenal submodule** already loaded - changes reflect immediately via symlinks
- **Session hooks active** - Superpowers bootstrap loaded automatically
- **Mandatory skills** enforced - test-runner, langfuse-debugger when applicable
- **Quality gates** in place - pre-commit scripts for anti-pattern detection

**Remember**: Arsenal is the centralized source - edit files in `/arsenal/` not `/.claude/`