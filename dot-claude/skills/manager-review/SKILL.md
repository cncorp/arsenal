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

## 🚨 Common Mistakes (Check EVERY Response)

**These mistakes occur in >50% of responses. Check for them systematically:**

### Mistake #1: Wrote Code Without Running Tests

**Pattern:**
- User asks to implement feature
- Claude writes code
- Claude responds "Done! Here's the implementation..."
- **MISSING:** No test-runner execution

**What manager should check:**
```
Did I write/modify any code? → YES
Did I run test-runner skill after? → NO
→ ITERATE: Run test-runner skill now
```

**Correct action:**
```bash
# Must run after EVERY code change
cd api && just ruff     # Formatting
cd api && just lint     # Type checking
cd api && just test-all-mocked  # Quick tests
```

**Don't respond until tests actually run and output is verified.**

---

### Mistake #2: Claimed Tests Pass Without Verification

**Pattern:**
- Claude says "tests are passing" or "all tests pass"
- **MISSING:** No actual test output shown
- **OR:** Only ran one test suite, not all

**What manager should check:**
```
Did I claim tests pass? → YES
Did I show actual test output? → NO
→ ITERATE: Actually run tests and show output

Did I say "all tests pass"? → YES
Did I run parallel test suite? → NO
→ ITERATE: Use correct terminology ("quick tests pass") or run full suite
```

**Verification required:**
- Must show actual pytest output
- Must show line like: "===== X passed in Y.YYs ====="
- If said "all tests", must run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`

**Common false claims:**
- ❌ "Tests should pass" (didn't run them)
- ❌ "Tests are passing" (no evidence)
- ❌ "All tests pass" (only ran mocked tests)

---

### Mistake #3: Didn't Validate Data Model Assumptions

**Pattern:**
- User asks question about production data
- Claude makes assumptions about schema/data
- **MISSING:** No sql-reader or langfuse skill usage to verify

**Examples of unvalidated assumptions:**

**Example A: Database schema**
```
User: "How many interventions were sent yesterday?"
Claude: "Based on the schema, approximately 50..."
         ^^^^^^^^^^^^^^^^^ UNVALIDATED ASSUMPTION
```

**What manager should check:**
```
Did I make claims about production data? → YES
Did I use sql-reader to query actual data? → NO
→ ITERATE: Use sql-reader skill to get real numbers
```

**Example B: Langfuse prompt schema**
```
User: "What fields does the prompt return?"
Claude: "The prompt returns 'should_send' and 'message'..."
                                ^^^^^^^^^^^^^^^^^^^^^ GUESSED
```

**What manager should check:**
```
Did I describe Langfuse prompt fields? → YES
Did I use langfuse-prompt-and-trace-debugger to fetch actual prompt? → NO
→ ITERATE: Fetch actual prompt schema
```

**Example C: Data model relationships**
```
Claude: "Users are linked to conversations via the user_id field..."
                                                      ^^^^^^^ ASSUMED
```

**What manager should check:**
```
Did I describe database relationships? → YES
Did I read actual schema with sql-reader? → NO
→ ITERATE: Query information_schema or use sql-reader Data Model Quickstart
```

---

## 🔍 Manager Review Checklist (Expanded)

When reviewing your proposed response, verify:

### Code Changes
- [ ] Did I write/modify code?
- [ ] If YES: Did I run test-runner skill after?
- [ ] If YES: Did I show actual test output?
- [ ] If I claimed "tests pass": Do I have pytest output proving it?
- [ ] If I said "all tests": Did I run the parallel suite?

### Data Claims
- [ ] Did I make claims about production data?
- [ ] If YES: Did I use sql-reader to verify?
- [ ] Did I describe Langfuse prompt schemas?
- [ ] If YES: Did I use langfuse-prompt-and-trace-debugger to fetch actual schema?
- [ ] Did I make assumptions about table relationships/fields?
- [ ] If YES: Did I query information_schema or read actual code?

### Evidence Quality
- [ ] Did I show actual command output (not "should work")?
- [ ] Did I read actual files (not "based on the structure")?
- [ ] Did I verify current state (not rely on memory)?
- [ ] Can I prove every claim with evidence?

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

6. **Wrote code without running tests**
   - Severity: HIGH
   - Action: Run test-runner skill now, show output

7. **Made Langfuse schema assumptions**
   - Severity: HIGH
   - Action: Use langfuse-prompt-and-trace-debugger to fetch actual schema

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
