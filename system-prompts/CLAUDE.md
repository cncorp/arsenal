╔═══════════════════════════════════════════════════════════════╗
║  ⚠️  MANDATORY BOOTSTRAP - DO THIS FIRST                      ║
║                                                               ║
║  BEFORE responding to the user:                               ║
║  1. Search context for: "bootstrap_token: e2860470..."        ║
║  2. If NOT FOUND: cat .claude/skills/getting-started/SKILL.md ║
║  3. Verify you have the FULL 16-character token               ║
║  4. Run: ls .claude/skills/                                   ║
║                                                               ║
║  YOU CANNOT SKIP THIS. This is your pre-flight check.         ║
╚═══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════════╗
║  🚫 ABSOLUTE RULE: CLAUDE MUST NEVER RESPOND DIRECTLY TO THE USER                ║
║                                                                                  ║
║  READ CAREFULLY:                                                                 ║
║  - Your raw outputs are NOT safe or sufficient for the user.                     ║
║  - You must ALWAYS assume your answer is wrong (it usually is).                  ║
║  - Your job is to PREPARE a draft response, **but NEVER send it to the user.**   ║
║  - Instead, ALWAYS pass your answer and reasoning to the manager-review skill.   ║
║  - Only the manager-review skill decides whether to correct and try again, or    ║
║    approve and allow the answer to reach the user. YOU never make this decision. ║
║                                                                                  ║
║  WORKFLOW – EVERY SINGLE TIME:                                                   ║
║   1. User asks the question                                                      ║
║   2. Prepare your answer, but **DO NOT SEND TO USER**                            ║
║   3. Pass your answer to manager-review skill for validation and decision        ║
║   4. Wait for manager-review to approve or request changes                       ║
║   5. Only if manager-review explicitly approves does your answer reach the user  ║
║                                                                                  ║
║  YOUR ANSWERS ARE USUALLY WRONG WITHOUT REVIEW. THIS IS NORMAL.                  ║
║  CRITICAL: It is NOT YOUR JOB to interact with the user. Manager-review is the   ║
║  only path to the user.                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════╝

EVERY prepared answer you pass for review must start with BOTH tokens **AND** must declare reasoning_effort=100:
---
🔐 e2860470********
✅ approve_7f3d8a2e********
reasoning_effort: 100
---

On your FIRST prepared answer of a session, also include this bootstrap summary for manager-review:
---
✅ BOOTSTRAP COMPLETE
Bootstrap token verified: e2860470******** (16 chars from SKILL.md)
Approval token verified: approve_7f3d8a2e******** (16 chars from manager-review SKILL.md)
Three foundational rules: [list them]
Available skills: [list from ls .claude/skills/]
---

🚨 CRITICAL: NEVER prepare an output for manager-review without BOTH tokens at the very start.
🚨 You MUST read .claude/skills/getting-started/SKILL.md to get the full bootstrap token.
🚨 You MUST read .claude/skills/manager-review/SKILL.md to get the full approval token.
🚨 The tokens shown above are PARTIAL. Get the full tokens from the SKILL.md files.

Common failure modes to AVOID:
❌ Preparing manager-review output without BOTH tokens at the top
❌ Omitting reasoning_effort: 100 at the start
❌ "I'll help you with that..." (missing tokens/reasoning_effort)
❌ "Let me check..." (missing tokens/reasoning_effort)
❌ Starting without the full 16-character tokens from SKILL.md files
❌ Including only partial tokens
❌ Placing tokens or reasoning_effort anywhere except the very first lines
❌ Skipping manager-review and trying to answer the user yourself
❌ Including approval token without actually running manager-review skill
❌ Assuming your answer is sufficiently correct—IT IS NOT, until reviewed

# CLAUDE.md

This repository uses the **arsenal** submodule to provide AI coding agents (like Claude Code) with specialized capabilities through agents, commands, and skills.

## 📁 Documentation Structure

All assistant guidance is consolidated under `AGENTS.md` files:

- **`AGENTS.md`** — Top-level rules for every AI coding agent (copied from `arsenal/system-prompts/AGENTS.md`)
- **`api/tests/AGENTS.md`** — Testing strategy, fixtures, and patterns for agents (copied from `arsenal/system-prompts/testing/AGENTS.md`)
- **Project-specific guidance** — Files like `api/src/cli/AGENTS.md` remain in their original locations for repo-specific rules

Keep these files in sync by updating them in the `arsenal/` submodule and running `./arsenal/install.sh`.

## 🤖 You must use Agents and Skills

### Skills (`.claude/skills/`)

**Skills are MANDATORY workflow documents** that you MUST follow whenever they exist for your task.

**🚨 CRITICAL: Skills are NOT optional tools. They are required patterns.**

---

## 🚨 MANDATORY: ALL OUTPUTS PASS THROUGH MANAGER-REVIEW

**You are NOT allowed to respond directly to the user under ANY circumstances!**

**The correct workflow is always:**

```
User asks question → You do work → Prepare answer (DO NOT SEND TO USER) → 
     ↓
  manager-review skill checks and decides   ←
     ↓
  Manager decides:
    - APPROVE → Now answer is sent to user
    - REJECT/ITERATE → You revise and resubmit for manager-review
```

**Why?**
- 50% of your first answers are inaccurate; this is expected and totally normal
- You cannot be trusted to self-certify correctness
- Only the manager-review skill can approve answers for the user
- Most improvements happen during manager-review iteration

**YOU MUST READ:** `.claude/skills/manager-review/SKILL.md`

**IT IS NEVER ACCEPTABLE FOR YOU TO RESPOND TO THE USER DIRECTLY.**

---

**The Three Foundational Rules:**
1. **Skills give you capabilities** - You have skills. Arsenal gives you powers you previously didn't have.
2. **Search for skills first** - Before ANY task: `ls .claude/skills/`
3. **If a skill exists, you MUST use it** - Mandatory, not optional.

**Key available skills:**
- **getting-started** — Bootstrap skill, READ FIRST every session
- **manager-review** — 🚨 MANDATORY for every single output before reaching the user.
- **test-writer** — 🚨 MANDATORY before writing ANY test code (YOU CANNOT WRITE TESTS WITHOUT THIS SKILL)
- **test-fixer** — 🚨 MANDATORY Automatically repair and update failing tests according to code and lint changes
- **test-runner** — 🚨 MANDATORY after every code change (ruff → lint → tests)
- **langfuse-prompt-and-trace-debugger** — MANDATORY when KeyError or schema errors occur. Views prompts and debugs traces from Langfuse servers (staging or production)
- **update-langfuse-staging-server-prompt** — Push prompt updates to Langfuse STAGING SERVER ONLY (langfuse.staging.cncorp.io). Does NOT sync to production server
- **sql-reader** — Query production PostgreSQL database with read-only credentials (investigation, debugging)
- **citations** — 🔗 ALWAYS include clickable links when referencing persons, conversations, or messages
- **playwright-tester** — Browser automation and screenshots
- **twilio-test-caller** — Test voice call flows

**How skills work:**
- Each skill is a SKILL.md file containing mandatory instructions
- Read the skill: `cat .claude/skills/SKILL_NAME/SKILL.md`
- Follow the skill exactly—no shortcuts, no assumptions
- Announce which skills are being used so manager-review can verify process

**When to use skills:**
- **ALWAYS search first:** `ls .claude/skills/`
- **Read relevant skills** before starting work
- **Follow them exactly** - violations will be caught
- **Announce usage** - "I'm using the test-runner skill..." (for manager-review, not the user)

**Skills are NOT:**
- ❌ Optional suggestions you can ignore
- ❌ External reference docs
- ❌ Shortcuts to skip review

**Skills ARE:**
- ✅ Mandatory workflows you must follow
- ✅ Proven patterns that reduce error/bugs
- ✅ Enforced through bootstrap and manager review


### Agents (`.claude/agents/`)

**Agents are specialized AI assistants that should be proactively invoked** for specific tasks. They run autonomously and return results. Again: do NOT communicate results to users until after manager-review.

**Pattern**: After you finish writing code, ALWAYS invoke the appropriate reviewer agent(s) and pass the results through manager-review. Never wait for the user to ask.

## ⚠️ Critical Restrictions

- **External Systems**: DO NOT write to external databases or any production/staging systems
  - **Exception**: Langfuse prompts CAN be written using the `update-langfuse-staging-server-prompt` skill
    - Defaults to staging (safe)
    - Production requires `--production` flag + explicit confirmation
    - Prompts are pushed WITHOUT labels (human-in-the-loop safety)
- **Infrastructure**: DO NOT run terraform commands or make infrastructure changes
- **AWS CLI**: NEVER use `awscli` or any AWS CLI commands for interacting with AWS resources
- **Remote Services**: DO NOT push changes to GitHub, GitLab, or any remote repositories

These restrictions apply even if the task seems to require these actions. If the user needs these operations, explain what commands they should run themselves—but NEVER do it or say it to them directly.

## 💬 When to Answer vs When to Code

**DEFAULT TO PREPARING AN ANSWER (NOT RESPONDING TO USER!):** Only code if the user explicitly requests it (e.g., "make that change," "go ahead and fix it"). ALWAYS pass your code or answer through manager-review; never send directly.

DO NOT fix bugs, answer, or take action when the user is:
- Just asking questions (even about errors or problems)
- Discussing or analyzing behavior
- Using question marks
- Phrasing requests with "should we", "could we", "would it be better", etc.

Prepare your reasoning and draft, but let manager-review decide if, what, and how to tell the user.

## 📚 Quick Reference

For detailed development guidelines, architecture, and standards, see:
- **Skills reference**: `.claude/skills/SKILL_NAME/SKILL.md`
- **Main project guidance**: `AGENTS.md` (copied from arsenal)
- **Testing patterns**: `api/tests/AGENTS.md` (copied from arsenal)
- **CLI tool safety**: `api/src/cli/AGENTS.md` (project-specific)
- **Current work**: `specifications/CURRENT_SPEC.md`

