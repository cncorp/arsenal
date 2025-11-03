---
name: langfuse-prompt-viewer
description: Fetch and view Langfuse prompts. Use when debugging KeyError/schema errors, understanding prompt schemas, or when user requests to view a prompt.
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Langfuse Prompt Viewer

Fetch and view prompts from Langfuse to understand their content, schema, and configuration.

## When to Use

**Always use when:**
- Tests fail with `KeyError` or schema validation errors
- Need to understand what schema a prompt returns
- Code references a prompt and you need to see its logic
- User asks to view a specific prompt
- Investigating why prompt response doesn't match expectations

**Example:** `KeyError: 'therapist_response'` → Fetch `voice_message_enricher` to see actual schema

## Fetch Commands

```bash
# Fetch specific prompt (from api directory)
cd api && \
set -a; source .env; set +a; \
PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py PROMPT_NAME

# Fetch all prompts
cd api && \
set -a; source .env; set +a; \
PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py

# Fetch multiple prompts
cd api && \
set -a; source .env; set +a; \
PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py prompt1 prompt2 prompt3
```

## Cached Location

Prompts saved to: `docs/cached_prompts/`

Files created:
- `{prompt_name}_production.txt` - Prompt content + version
- `{prompt_name}_production_config.json` - Configuration

## Key Prompts

### Core Processing
- `message_enricher` - 🔥 Most critical - analyzes affect, conflict_state, intervention_needed
- `voice_message_enricher` - Voice enrichment with key_quote, segment_conflict_health
- `1on1` - One-on-one coaching conversations
- `fact_extractor` - Extracts facts for LTMM

### Intervention Logic
- `group_message_intervention_conditions_yaml` - SQL conditions triggering interventions
- `group_msg_intervention_needed_sender/recipient` - Intervention responses
- `group_msg_needs_soft_startup` - Soft startup intervention
- `group_msg_needs_timeout_sender/recipient` - Timeout suggestions
- `group_msg_positive_reinforcement_sender/recipient` - Positive reinforcement

### Onboarding
- `onboarding_v3_1on1` - V3 individual flow
- `onboarding_v3_group` - V3 group flow
- `onboarding_group_conversation` - Group onboarding

### Voice Features
- `voice_active_mediation` - Active mediation during calls
- `voice_conflict_intro` - Voice conflict intro
- `voice_guidance_delivery` - Voice guidance delivery

## Understanding Configs

### Prompt Text File
- Instructions: What AI should do
- Output format: JSON schema, required fields
- Variables: `{{sender_name}}`, `{{current_message}}`, etc.
- Allowed values: Enumerated options for fields
- Version: Header shows version

### Config JSON File
```json
{
  "model_config": {
    "model": "gpt-4.1",
    "temperature": 0.7,
    "response_format": {
      "type": "json_schema",  // or "json_object"
      "json_schema": { ... }
    }
  }
}
```

**response_format types:**
- `json_object` - Unstructured (model decides fields)
- `json_schema` - Strict validation (fields enforced)

## Debugging Workflows

### KeyError in Tests
1. Fetch the prompt
2. Check if field is optional/conditional in prompt text
3. Check config: `json_object` vs `json_schema`
4. Fix test to handle optional field OR update prompt

### Intervention Not Triggering
1. Fetch `message_enricher` to see `intervention_needed` values
2. Fetch `group_message_intervention_conditions_yaml` for SQL conditions
3. Verify enrichment result matches conditions

### Schema Validation Fails
1. Fetch the prompt
2. Read config's `json_schema` section
3. Check `required` array
4. Verify code provides all required parameters

## Quick Reference

```bash
# List cached prompts
ls -1 docs/cached_prompts/*_production.txt | xargs -n1 basename | sed 's/_production.txt$//'

# Fetch prompt
cd api && set -a; source .env; set +a; PYTHONPATH=src uv run python src/cli/refresh_prompt_cache.py PROMPT_NAME

# Read prompt
cat docs/cached_prompts/PROMPT_NAME_production.txt
cat docs/cached_prompts/PROMPT_NAME_production_config.json
```

**Note:** This is READ-ONLY. Never modify Langfuse prompts directly.
