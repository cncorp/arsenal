---
description: Answer product/data questions and create concise feature proposals (250 words max)
---

# Question to Feature Proposal Command

**Purpose:** Turn product questions into concise, actionable feature proposals (250 words or less).

## Output Format

Every proposal must answer exactly 4 questions in ≤250 words:

1. **User Insight:** What user behavior/feedback justifies this proposal?
2. **Infrastructure:** What key systems need to change?
3. **The Change:** What specifically will we build?
4. **User Outcome:** What will users experience differently?

## Workflow

### Step 1: Gather Data
Use sql-reader skill to query production database:
- Reactions: `message` table where `provider_data->>'reaction_id' IS NOT NULL`
- User messages: `message` + `conversation` + `persons` joins
- Run data model quickstart if needed

### Step 2: Create Analysis (Full Detail)
Save comprehensive analysis to: `docs/temp/analysis/analysis_{topic}_{YYYY-MM-DD}.md`
- Include all data, patterns, insights
- This is for reference, not the proposal

### Step 3: Create Proposal (≤250 Words)
Save concise proposal to: `docs/temp/proposals/{topic}-YYYY-MM-DD.md`

**Template:**
```markdown
# Proposal: {Title}

**Date:** {YYYY-MM-DD}
**Priority:** P0/P1/P2/P3
**Effort:** XS/S/M/L/XL

## 1. User Insight
{What user behavior/feedback justifies this? 2-3 sentences with specific data points.}

## 2. Infrastructure
{What key systems/components need to change? Bullet list.}

## 3. The Change
{What specifically will we build? 3-4 sentences describing the feature.}

## 4. User Outcome
{What will users experience differently? 2-3 sentences describing impact.}
```

**Total length:** 250 words maximum. Be specific. No fluff.

### Step 4: Output Summary

```
✅ Proposal created

📊 Question: {question}
📈 Data: {summary}

🎯 Proposal: {title}
- Priority: {P0/P1/P2/P3}
- Effort: {XS/S/M/L/XL}

📄 Analysis (full): docs/temp/analysis/analysis_{topic}_{YYYY-MM-DD}.md
📋 Proposal (concise): docs/temp/proposals/{topic}-YYYY-MM-DD.md
```

## Example

**Question:** "Has there been any user feedback in the last 24 hours?"

**Output:**
```markdown
# Proposal: Direct Suggestions Mode

**Date:** 2025-11-18
**Priority:** P0
**Effort:** M

## 1. User Insight
Marina Rich explicitly requested "just give me ideas already or options" instead of back-and-forth refinement. All 5 "Loved" reactions (100% of Loved feedback) went to concrete scripts with specific phrases. The only "Disliked" reaction went to a generic reflective question. Pattern is clear: users want immediate options, not exploration.

## 2. Infrastructure
- `message_processing/`: Add help request detector
- `prompt_handling/`: New Langfuse prompt `direct_suggestions_generator`
- `send_blue/main.py`: Multi-option response formatter

## 3. The Change
When users ask for help ("What should I say?", "Help me respond"), Codel immediately generates 2-3 labeled options (e.g., "Option A: Warm and validating", "Option B: Direct and clear"). Each option is personalized using user facts and recent context. User selects one, can request refinement. No clarifying questions first.

## 4. User Outcome
Users get actionable scripts in 1-2 messages instead of 3-5. Frustration with "if you want..." prompts eliminated. Time-to-value cut by 50%. Satisfaction increases as users feel heard and helped immediately.
```

**Word count:** 183 words ✅

## Cron Setup

```bash
# Daily feedback check
0 9 * * * claude -p "/question-to-feature-proposal 'User feedback in last 24h?'" >> /var/log/proposals.log 2>&1
```

## Notes

- Keep proposals under 250 words (strict limit)
- Full analysis can be as long as needed
- Proposal = executive summary for decision-making
- Analysis = detailed reference for implementation
