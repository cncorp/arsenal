# Superpowers

Reusable Claude Code agents, commands, skills, and patterns for your projects.

## Quick Start

```bash
# 1. Initialize submodule (if not already done)
git submodule update --init --recursive

# 2. Run install script (handles .env setup automatically)
./superpowers/install.sh

# 3. Start Docker services (optional - for semantic-code-search)
cd superpowers && docker-compose up -d
```

**The install script automatically:**
- Creates symlinks for `.claude`, `.pre-commit-scripts`, and `AGENTS.md` files
- Installs Node.js dependencies (playwright-tester, etc.)
- Sets up `superpowers/.env` and offers to copy OPENAI_API_KEY from `api/.env`

**Adding to a new repository:** `git submodule add git@github.com:cncorp/superpowers.git superpowers` then follow above.

## Structure

```
superpowers/
├── dot-claude/           # Claude Code configurations
│   ├── agents/          # Custom agents (mypy-error-fixer, pytest-test-reviewer, etc.)
│   ├── commands/        # Slash commands (/buildit, /planit, /review-code, etc.)
│   ├── skills/          # Skills (docker-log-debugger, langfuse-prompt-viewer, etc.)
│   └── settings.local.json
├── pre-commit-scripts/  # Pre-commit hooks and linting scripts
│   └── check_llm_nits.py # LLM anti-pattern detection
├── system-prompts/      # Project-specific patterns
│   ├── AGENTS.md       # Root-level agent guidance
│   └── testing/        # Testing-specific patterns
│       └── AGENTS.md
├── .env.example        # Environment template (copy to .env)
├── docker-compose.yml  # Centralized Docker orchestration
├── install.sh          # Installation script (idempotent)
├── uninstall.sh        # Uninstallation script
└── README.md           # This file
```

## What You Get

### 🤖 Specialized Agents (Auto-invoked)
Claude Code automatically uses these agents when appropriate:

- **`git-reader`** - Read-only git operations (status, diffs, history, logs) with tool-level enforcement
- **`pytest-test-reviewer`** - Reviews test code for quality, parametrization, and best practices
- **`test-fixture-reviewer`** - Refactors test fixtures to follow patterns
- **`mypy-error-fixer`** - Automatically fixes type errors
- **`task-complete-enforcer`** - Ensures tasks meet Definition of Done before marking complete

### 📋 Slash Commands
Invoke with `/command-name` in Claude Code:

**Planning & Implementation:**
- `/planit` - Create detailed implementation plans
- `/buildit` - Implement the next stage in your plan
- `/plan-tdd` - Create TDD-based implementation plans
- `/implement-tdd` - Implement using Test-Driven Development

**Code Quality:**
- `/review-code` - Review code changes for quality and patterns
- `/prreview` - Review pull requests comprehensively
- `/mypy` - Run and fix mypy type errors

**Research & Exploration:**
- `/research` - Research codebase features or topics
- `/wdyt` - "What do you think?" - get opinions on implementation approaches

**Quick Actions:**
- `/cyw` - "Code your way" - implement with minimal guidance
- `/yjd` - "You just do" - quick implementation without discussion
- `/prime` - Prime context for a task

**Project Management:**
- `/create-linear-ticket` - Create Linear tickets from tasks
- `/linear-agent` - Work with Linear issues

### 🎯 Skills (Specialized Tools)

**Semantic Code Search** - Find code by meaning, not text matching
```bash
# Start the skill
cd superpowers && docker-compose up -d

# Examples of what you can ask Claude:
"Find all authentication logic in the codebase"
"Where do we handle webhook messages?"
"Show me database query functions"
"Find code that sends emails"

# Direct CLI usage:
docker exec superpowers-semantic-search-cli python /app/src/cli.py find "authentication logic"
docker exec superpowers-semantic-search-cli python /app/src/cli.py find "send message to user"
```

**Langfuse Prompt Viewer** - Debug prompts and traces
```bash
# Examples of what you can ask Claude:
"Show me the voice_message_enricher prompt"
"What schema does the intervention_router prompt return?"
"View the trace for this error: trace_abc123"
"Why am I getting KeyError: 'therapist_response'?"

# It will run:
cd api && PYTHONPATH=src uv run python .claude/skills/langfuse-prompt-viewer/refresh_prompt_cache.py
```

**Playwright Tester** - Browser automation and testing
```bash
# Examples of what you can ask Claude:
"Test if the login page loads correctly"
"Find the submit button on the registration form"
"Check if error messages appear when form validation fails"
"Take a screenshot of the dashboard page"
"Verify the chat widget opens when clicked"

# It will use the playwright-tester skill to:
# - Launch browsers (Chrome, Firefox, Safari)
# - Find elements by text, CSS selector, or accessibility role
# - Interact with forms, buttons, links
# - Take screenshots and verify page state
```

**Docker Log Debugger** - Analyze container logs for errors
```bash
# Examples of what you can ask Claude:
"Find errors in the api container logs"
"Show me database connection failures"
"What's causing the worker to crash?"
"Search logs for 'KeyError' in the last 100 lines"

# It will run:
docker logs codel-api --tail 100 | grep -i error
docker logs codel-worker --since 10m
```

**Test Runner** - Run tests in parallel and background
```bash
# Examples of what you can ask Claude:
"Run all unit tests in the background"
"Run integration tests in parallel while I keep working"
"Show me test results for the messaging module"
"Run smoke tests and let me know when they finish"

# It will run:
cd api && just test-unit &
# Or monitor existing test runs
pytest --workers 4 tests/integration/
```

**Twilio Test Caller** - Test voice call functionality
```bash
# Examples of what you can ask Claude:
"Place a test call to +15555551234"
"Test the voice menu IVR flow"
"Verify call recording works"
"Send a test SMS to check delivery"

# It will use Twilio API to:
# - Initiate test calls
# - Verify call connection and audio
# - Test IVR menu responses
# - Check SMS delivery status
```

### 📚 System Prompts
Automatically loaded guidance for AI agents:
- **`AGENTS.md`** - Root-level coding patterns, anti-patterns, and quality standards
- **`api/tests/AGENTS.md`** - Testing patterns, fixture guidelines, and test types

### 🔍 Pre-commit Scripts
Automatic code quality checks:
- **`check_llm_nits.py`** - Detects LLM anti-patterns (broad exceptions, late imports, single-use functions)

## Updating

To pull latest changes from superpowers:

```bash
cd superpowers
git pull origin main
cd ..
git add superpowers
git commit -m "Update superpowers submodule"
```

After updating, re-run the install script if new skills were added:
```bash
./superpowers/install.sh
```

## Contributing

When updating patterns or configurations:

1. Make changes in `superpowers/` directory
2. Test in your project (changes reflect via symlinks)
3. Commit and push to superpowers repo
4. Update submodule reference in your project

## Skills with Node.js Dependencies

The following skills require Node.js and npm:
- **playwright-tester**: Browser automation skill using Playwright

These will be automatically set up during installation if npm is available.

## License

[Your License Here]
