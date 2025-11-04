---
name: langfuse-prompt-viewer
description: Fetch and view Langfuse prompts and traces. Use when debugging KeyError/schema errors, understanding prompt schemas, viewing traces, or when user requests to view a prompt.
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Langfuse Prompt & Trace Viewer

Comprehensive skill for working with Langfuse prompts and traces. Portable scripts that work with any project using Langfuse.

## When to Use

**Always use when:**
- Tests fail with `KeyError` or schema validation errors
- Need to understand what schema a prompt returns
- Code references a prompt and you need to see its logic
- User asks to view a specific prompt
- Investigating why prompt response doesn't match expectations
- Debugging Langfuse traces
- Analyzing AI model behavior in production

**Example:** `KeyError: 'therapist_response'` → Fetch the prompt to see actual schema

## Environment Setup

**Required environment variables:**
- `LANGFUSE_PUBLIC_KEY` - Langfuse API public key
- `LANGFUSE_SECRET_KEY` - Langfuse API secret key
- `LANGFUSE_HOST` - Langfuse instance URL (optional, defaults to https://cloud.langfuse.com)

**Optional:**
- `ENVIRONMENT` - Environment label (defaults to "production") - used by `check_prompts.py` to check prompt availability

**Setup:**
```bash
# Add to superpowers/.env:
LANGFUSE_PUBLIC_KEY=pk-lf-...  # pragma: allowlist-secret
LANGFUSE_SECRET_KEY=sk-lf-...  # pragma: allowlist-secret
LANGFUSE_HOST=https://your-langfuse-instance.com
ENVIRONMENT=production
```

**Load environment:**
```bash
set -a; source superpowers/.env; set +a
```

## Available Scripts

### 1. refresh_prompt_cache.py - Download Prompts Locally

Downloads Langfuse prompts to `docs/cached_prompts/` for offline viewing.

**Usage:**
```bash
# Load environment first
set -a; source superpowers/.env; set +a

# Fetch specific prompt
python superpowers/dot-claude/skills/langfuse-prompt-viewer/refresh_prompt_cache.py PROMPT_NAME

# Fetch all prompts
python superpowers/dot-claude/skills/langfuse-prompt-viewer/refresh_prompt_cache.py

# Fetch multiple prompts
python superpowers/dot-claude/skills/langfuse-prompt-viewer/refresh_prompt_cache.py prompt1 prompt2 prompt3
```

**Cached Location:**
- `docs/cached_prompts/{prompt_name}_production.txt` - Prompt content + version
- `docs/cached_prompts/{prompt_name}_production_config.json` - Configuration

### 2. check_prompts.py - List Available Prompts

Lists all prompts available in Langfuse and checks their availability in the current environment.

**Usage:**
```bash
# Load environment first
set -a; source superpowers/.env; set +a

# Check all prompts
python superpowers/dot-claude/skills/langfuse-prompt-viewer/check_prompts.py
```

**Output:**
- Lists all prompt names in Langfuse
- Shows which prompts are available in the specified environment (from `ENVIRONMENT` variable)
- Color-coded indicators (✓ green for available, ✗ red for missing)
- Summary statistics

### 3. fetch_trace.py - View Langfuse Traces

Fetch and display Langfuse traces for debugging AI model behavior.

**Usage:**
```bash
# Load environment first
set -a; source superpowers/.env; set +a

# Fetch specific trace by ID
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py db29520b-9acb-4af9-a7a0-1aa005eb7b24

# Fetch trace from Langfuse URL
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py "https://langfuse.example.com/project/.../traces?peek=db29520b..."

# List recent traces
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py --list --limit 5

# View help
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py --help
```

**What it shows:**
- Trace ID and metadata
- All observations (LLM calls, tool uses, etc.)
- Input/output for each step
- Timing information
- Hierarchical display of nested observations
- Useful for debugging AI workflows

## Understanding Prompt Configs

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
1. Fetch the prompt using `refresh_prompt_cache.py`
2. Check if field is optional/conditional in prompt text
3. Check config: `json_object` vs `json_schema`
4. Fix test to handle optional field OR update prompt

### Schema Validation Fails
1. Fetch the prompt using `refresh_prompt_cache.py`
2. Read config's `json_schema` section
3. Check `required` array
4. Verify code provides all required parameters

### Understanding AI Behavior
1. Get trace ID from logs or Langfuse UI
2. Use `fetch_trace.py` to view full trace
3. Examine inputs, outputs, and intermediate steps
4. Check for unexpected model responses

## Quick Reference

```bash
# Setup (one-time)
# Add LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST to superpowers/.env

# Load environment (required before each use)
set -a; source superpowers/.env; set +a

# List all available prompts
python superpowers/dot-claude/skills/langfuse-prompt-viewer/check_prompts.py

# Fetch specific prompt
python superpowers/dot-claude/skills/langfuse-prompt-viewer/refresh_prompt_cache.py PROMPT_NAME

# View cached prompt
cat docs/cached_prompts/PROMPT_NAME_production.txt
cat docs/cached_prompts/PROMPT_NAME_production_config.json

# List recent traces
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py --list --limit 5

# Fetch specific trace
python superpowers/dot-claude/skills/langfuse-prompt-viewer/fetch_trace.py TRACE_ID
```

## Important Notes

**READ-ONLY Operations:**
- These scripts are for viewing and debugging only
- DO NOT use to modify or delete prompts in Langfuse
- DO NOT push changes to Langfuse
- Always verify you're looking at the correct environment

**Portability:**
- Scripts are self-contained and work from any directory
- No project-specific dependencies required
- Only requires `langfuse` Python package
- Works with superpowers/.env for configuration
