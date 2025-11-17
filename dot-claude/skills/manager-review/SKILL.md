---
name: manager-review
description: Quality gate before responding to user. Reviews proposed response against original query, checks skill usage, iterates 50% of the time for accuracy.
---

# Manager Review Skill

**MANDATORY quality gate before EVERY user response.**

---

## 🎯 Purpose

This skill acts as a critical quality review before you respond to the user. You are a senior engineer who must review your own work with the skepticism that **50% of responses are inaccurate and can be improved** through better use of arsenal skills.

**Use this skill:**
- **BEFORE responding to the user** (EVERY time)
- After you've completed your work
- When you think you have a final answer

**YOU CANNOT respond to the user without running this skill first.**

---

## 🚨 CRITICAL: Response Workflow

```
User asks question
    ↓
You do research/work
    ↓
You prepare a response
    ↓
⚠️ STOP - DO NOT RESPOND YET ⚠️
    ↓
Run manager-review skill
    ↓
Manager reviews and decides:
  - APPROVE → Respond to user
  - ITERATE → Improve response and review again
```

**NEVER skip the manager-review step.**

---

## 📋 Manager Review Checklist

When reviewing your proposed response, ask yourself:

### 1. Original Query Alignment
- [ ] Does the response **directly answer** what the user asked?
- [ ] Did I answer the RIGHT question, or a related but different question?
- [ ] Did I over-deliver or under-deliver on the scope?

### 2. Arsenal Skills Usage
- [ ] Did I search for relevant skills first? (`ls .claude/skills/`)
- [ ] Did I use the **correct skills** for this task?
- [ ] Are there skills I should have used but didn't?
- [ ] Did I follow the skills exactly, or cut corners?

**Common missed opportunities:**
- Used direct bash instead of sql-reader skill
- Searched manually instead of using semantic-code-search
- Wrote tests without test-writer skill
- Modified arsenal without skill-writer skill
- Queried production data without product-data-analyst skill
- Analyzed logs without docker-log-debugger or aws-logs-query skills

### 3. Accuracy & Completeness
- [ ] Is my response factually accurate?
- [ ] Did I verify claims with actual data/code?
- [ ] Did I make assumptions that should be checked?
- [ ] Are there edge cases I missed?

### 4. Evidence Quality
- [ ] Did I show actual output from commands?
- [ ] Did I read the actual files, or assume their contents?
- [ ] Did I verify the current state, or rely on memory?
- [ ] Did I use grep/glob/read to confirm, not guess?

### 5. Restrictions & Rules
- [ ] Did I follow all CLAUDE.md restrictions?
- [ ] Did I avoid banned operations (git commit, destructive commands)?
- [ ] Did I stay within my allowed operations?
- [ ] Did I properly use git-reader/git-writer instead of direct git?

---

## 🔄 Decision: Approve or Iterate

### APPROVE (Rare - ~20% of cases)

**Approve ONLY when ALL of these are true:**
- ✅ Response directly answers the user's question
- ✅ All relevant skills were used correctly
- ✅ Evidence is strong (actual command output, file reads)
- ✅ No assumptions or guesses
- ✅ All restrictions followed
- ✅ Accurate and complete

**If approved, respond to user with your prepared answer.**

---

### ITERATE (Common - ~80% of cases)

**Iterate when ANY of these are true:**
- ❌ Didn't use a relevant skill
- ❌ Made assumptions without verification
- ❌ Answered a different question than asked
- ❌ Missing evidence or verification
- ❌ Skipped a mandatory workflow step
- ❌ Could be more accurate with better skill usage

**When iterating:**
1. Identify what's missing or wrong
2. Identify which skills would improve accuracy
3. Run those skills
4. Improve your response
5. Run manager-review again

---

## 📊 Self-Assessment: Accuracy Rate

**Assume you start at 50% accuracy.** Your goal is to reach 95%+ through iteration.

**Common accuracy problems:**
1. **Skill blindness** - Didn't know a skill existed for this task
   - Solution: Always `ls .claude/skills/` first
2. **Assumption creep** - Guessed instead of verified
   - Solution: Use grep/read/bash to verify claims
3. **Scope drift** - Answered related but different question
   - Solution: Re-read original query before responding
4. **Evidence gaps** - Claimed something without proof
   - Solution: Show actual command output
5. **Shortcut temptation** - Skipped skills to save time
   - Solution: Skills save time by preventing rework

---

## 🎯 Examples

### Example 1: User asks "How many interventions were sent yesterday?"

**Your proposed response:**
"Based on the database schema, there were approximately 50 interventions sent yesterday."

**Manager review:**
- ❌ ITERATE - Used "approximately" without actual data
- ❌ ITERATE - Didn't use sql-reader skill to query production DB
- ❌ ITERATE - "Based on schema" means you guessed

**Improved approach:**
1. Use sql-reader skill
2. Run actual query: `SELECT COUNT(*) FROM interventions WHERE sent_at >= CURRENT_DATE - INTERVAL '1 day'`
3. Return exact number with evidence

---

### Example 2: User asks "Write tests for the auth function"

**Your proposed response:**
```python
def test_auth():
    assert auth("user", "pass") == True
```

**Manager review:**
- ❌ ITERATE - Didn't use test-writer skill (MANDATORY for test writing)
- ❌ ITERATE - Violated critical rule: "YOU CANNOT WRITE TESTS WITHOUT test-writer SKILL"
- ❌ ITERATE - Missing contract analysis, dependency check, etc.

**Improved approach:**
1. STOP before writing any test code
2. Use test-writer skill
3. Follow 12-step analysis workflow
4. Present analysis to user first
5. Then write tests following patterns

---

### Example 3: User asks "What changed in the last commit?"

**Your proposed response:**
"Let me check the git log..."
```bash
git log -1
```

**Manager review:**
- ❌ ITERATE - Didn't use git-reader agent (mandatory for git queries)
- ❌ ITERATE - Running git commands directly violates workflow

**Improved approach:**
1. Use Task tool with git-reader agent
2. Let agent run git commands safely
3. Return agent's findings to user

---

### Example 4: User asks "Are users engaging with the new feature?"

**Your proposed response:**
"Based on the code, users should be engaging well since the feature is prominent in the UI."

**Manager review:**
- ❌ ITERATE - Answered with code analysis instead of actual usage data
- ❌ ITERATE - Didn't use product-data-analyst skill (mandatory for product questions)
- ❌ ITERATE - Made assumption ("should be") without evidence

**Improved approach:**
1. Use product-data-analyst skill
2. Query actual usage metrics from production
3. Show real engagement numbers
4. Provide data-driven answer

---

## 🔁 Iteration Template

When you need to iterate, use this format in your internal reasoning:

```
MANAGER REVIEW RESULT: ITERATE

Issues found:
1. [Specific issue]
2. [Specific issue]

Skills I should use:
1. [skill-name] - because [reason]
2. [skill-name] - because [reason]

Improved approach:
1. [Step using skill]
2. [Step using skill]
3. [Verify and review again]

Now executing improved approach...
```

---

## ⚠️ Critical Violations (Immediate ITERATE)

These automatically require iteration:

1. **Wrote test code without test-writer skill**
   - Severity: CRITICAL
   - Action: Delete test code, use test-writer skill, start over

2. **Modified arsenal without skill-writer skill**
   - Severity: CRITICAL
   - Action: Revert changes, use skill-writer skill

3. **Ran git commit/push/reset**
   - Severity: CRITICAL
   - Action: Explain to user you cannot do this

4. **Guessed at data without querying**
   - Severity: HIGH
   - Action: Use sql-reader or product-data-analyst to get real data

5. **Said "tests pass" without running test-runner**
   - Severity: HIGH
   - Action: Run actual tests with test-runner skill

---

## 📈 Success Criteria

You've successfully used manager-review when:

- [ ] Checked response against original query
- [ ] Verified all relevant skills were used
- [ ] Confirmed accuracy with evidence
- [ ] Iterated at least once (most responses need iteration)
- [ ] Only approved when genuinely high quality
- [ ] Responded to user with confident, verified answer

---

## 🚀 Quick Decision Tree

```
Am I about to respond to the user?
    ↓
YES → STOP
    ↓
Run manager-review checklist
    ↓
Did I use all relevant skills? → NO → ITERATE
Did I verify my claims? → NO → ITERATE
Is my evidence strong? → NO → ITERATE
Am I answering the right question? → NO → ITERATE
    ↓
ALL YES → APPROVE → Respond to user
```

---

## Remember

**50% of your initial responses are inaccurate.** This isn't a failure—it's expected. The manager-review skill exists to catch those issues and guide you to the 95%+ accuracy tier through proper skill usage and verification.

**Trust the process. Iterate when in doubt.**
