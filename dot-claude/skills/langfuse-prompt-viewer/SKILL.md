---
name: langfuse-prompt-viewer
description: MANDATORY skill when KeyError or schema errors occur. Fetch actual prompt schemas instead of guessing. Use for debugging traces and understanding AI model behavior.
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Langfuse Prompt & Trace Viewer - MANDATORY FOR KEYERRORS

## 🔥 CRITICAL: Use This Skill Immediately When:

**MANDATORY triggers (you MUST use this skill):**
- ❗ Tests fail with `KeyError` (e.g., `KeyError: 'therapist_response'`)
- ❗ Schema validation errors
- ❗ Unexpected prompt response structure
- ❗ Need to understand what fields a prompt actually returns

**Common triggers:**
- User asks to view a specific prompt
- Code references a prompt but logic is unclear
- Investigating why AI behavior doesn't match expectations
- Debugging Langfuse traces
- Analyzing model output in production

## 🚨 VIOLATION: Guessing at Schemas

**WRONG:** "The prompt probably returns {field_name}, let me add that to the code"
**RIGHT:** *Uses this skill to fetch actual prompt, reads actual schema*

**DO NOT:**
- ❌ Assume field names without checking
- ❌ Guess at optional vs required fields
- ❌ Try multiple field names hoping one works
- ❌ Look at old code and assume it's current

**DO THIS:**
1. ✅ cd to `.claude/skills/langfuse-prompt-viewer`
2. ✅ Run `uv run python refresh_prompt_cache.py PROMPT_NAME`
3. ✅ Read `docs/cached_prompts/PROMPT_NAME_production.txt`
4. ✅ Read `docs/cached_prompts/PROMPT_NAME_production_config.json`
5. ✅ Use the ACTUAL schema you just read

## 🏢 Understanding Langfuse Servers vs Labels

**CRITICAL: We have TWO separate Langfuse servers:**

1. **Staging Langfuse Server** (`https://langfuse.staging.cncorp.io`)
   - Separate database/instance on staging ECS cluster
   - Used for development and testing
   - Has prompts tagged with "production" label - these are DEFAULT prompts for staging tests
   - ⚠️ "production" label here does NOT mean real user-facing prompts

2. **Production Langfuse Server** (`https://langfuse.prod.cncorp.io`)
   - Separate database/instance on production ECS cluster
   - Used for real user-facing application
   - Has prompts tagged with "production" label - these ARE the real prompts shown to users
   - ✅ "production" label here means actual live prompts

**Key Points:**
- The two servers are **completely independent** - no automatic sync between them
- Both servers use the same label system (`production`, `development`, `staging`, etc.)
- A prompt with "production" label on **staging server** ≠ prompt with "production" label on **prod server**
- Labels control which prompt version is served within each server
- Server selection is controlled by `LANGFUSE_HOST` environment variable

## Environment Setup

**Required environment variables:**
- `LANGFUSE_PUBLIC_KEY` - Langfuse API public key
- `LANGFUSE_SECRET_KEY` - Langfuse API secret key
- `LANGFUSE_HOST` - Langfuse server URL
  - Staging: `https://langfuse.staging.cncorp.io`
  - Production: `https://langfuse.prod.cncorp.io`

**Optional:**
- `ENVIRONMENT` - Label to fetch within the server (defaults to "production")
  - This is the LABEL/TAG within whichever server you're connected to
  - NOT the same as which Langfuse server you're querying

**Setup:**
```bash
# Add to arsenal/.env:
# For STAGING Langfuse server (default for development):
LANGFUSE_PUBLIC_KEY_STAGING=pk-lf-...  # pragma: allowlist-secret
LANGFUSE_SECRET_KEY_STAGING=sk-lf-...  # pragma: allowlist-secret
LANGFUSE_HOST_STAGING=https://langfuse.staging.cncorp.io

# For PRODUCTION Langfuse server (real user-facing prompts):
LANGFUSE_PUBLIC_KEY_PROD=pk-lf-...  # pragma: allowlist-secret
LANGFUSE_SECRET_KEY_PROD=sk-lf-...  # pragma: allowlist-secret
LANGFUSE_HOST_PROD=https://langfuse.prod.cncorp.io

# Select which server to use:
LANGFUSE_ENVIRONMENT=staging  # or 'production'
```

**No manual environment loading needed!** The scripts automatically find and load `arsenal/.env` from anywhere in the project.

## Available Scripts

### 1. refresh_prompt_cache.py - Download Prompts Locally

Downloads Langfuse prompts to `docs/cached_prompts/` for offline viewing.

**Usage:**
```bash
# Navigate to the skill directory
cd .claude/skills/langfuse-prompt-viewer

# Fetch specific prompt
uv run python refresh_prompt_cache.py PROMPT_NAME

# Fetch all prompts
uv run python refresh_prompt_cache.py

# Fetch multiple prompts
uv run python refresh_prompt_cache.py prompt1 prompt2 prompt3
```

**Cached Location:**
- `docs/cached_prompts/{prompt_name}_production.txt` - Prompt content + version
- `docs/cached_prompts/{prompt_name}_production_config.json` - Configuration

### 2. check_prompts.py - List Available Prompts

Lists all prompts available in Langfuse and checks their availability in the current environment.

**Usage:**
```bash
# Navigate to the skill directory
cd .claude/skills/langfuse-prompt-viewer

# Check all prompts
uv run python check_prompts.py
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
# Navigate to the skill directory
cd .claude/skills/langfuse-prompt-viewer

# Fetch specific trace by ID
uv run python fetch_trace.py db29520b-9acb-4af9-a7a0-1aa005eb7b24

# Fetch trace from Langfuse URL
uv run python fetch_trace.py "https://langfuse.example.com/project/.../traces?peek=db29520b..."

# List recent traces
uv run python fetch_trace.py --list --limit 5

# View help
uv run python fetch_trace.py --help
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
# Add LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST to arsenal/.env
# Make sure to add # pragma: allowlist-secret comments after secrets

# Navigate to skill directory
cd .claude/skills/langfuse-prompt-viewer

# List all available prompts
uv run python check_prompts.py

# Fetch specific prompt
uv run python refresh_prompt_cache.py PROMPT_NAME

# View cached prompt
cat ../../docs/cached_prompts/PROMPT_NAME_production.txt
cat ../../docs/cached_prompts/PROMPT_NAME_production_config.json

# List recent traces
uv run python fetch_trace.py --list --limit 5

# Fetch specific trace
uv run python fetch_trace.py TRACE_ID
```

## Important Notes

**READ-ONLY Operations:**
- These scripts are for viewing and debugging only
- DO NOT use to modify or delete prompts in Langfuse
- DO NOT push changes to Langfuse
- Always verify you're looking at the correct environment

**Portability:**
- Scripts are fully standalone with their own virtual environment via UV
- Automatically find and load `arsenal/.env` from anywhere in the project
- No manual environment loading needed
- Dependencies (langfuse==2.60.3, httpx==0.27.2) are pinned for compatibility
- Work from any directory - the scripts locate project root automatically
