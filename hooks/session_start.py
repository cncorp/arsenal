#!/usr/bin/env python3
"""
SessionStart hook that injects the getting-started skill into every session.

This ensures agents have the skill content in their context from the start,
making compliance mechanical rather than relying on LLM choice.
"""
import os
import sys

def main():
    skill_path = "./.claude/skills/getting-started/SKILL.md"

    if os.path.exists(skill_path):
        with open(skill_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line_count = len(lines)
            content = "".join(lines)

            print("╔══════════════════════════════════════════════════════════╗")
            print("║   📋 SESSION BOOTSTRAP: getting-started skill loaded     ║")
            print(f"║   File size: {line_count} lines                                   ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print()
            print(content)
            print()
            print(f"--- End of getting-started skill ({line_count} lines) ---")
            print()
    else:
        print("⚠️  WARNING: getting-started skill not found at:", skill_path)
        print("Expected location: ./.claude/skills/getting-started/SKILL.md")
        print("The agent will not have skill context loaded.")
        sys.exit(1)

if __name__ == "__main__":
    main()
