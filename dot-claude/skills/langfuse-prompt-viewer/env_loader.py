#!/usr/bin/env python3
"""
Automatic environment loader for langfuse-prompt-viewer skill.
Finds and loads superpowers/.env automatically.
"""

import os
from pathlib import Path


def find_superpowers_dir() -> Path | None:
    """
    Find the superpowers directory by searching up from current directory.

    Returns:
        Path to superpowers directory, or None if not found
    """
    current = Path.cwd()

    # First check if we're already in superpowers or its subdirectories
    if current.name == "superpowers":
        return current

    # Check if superpowers is a sibling or parent
    for parent in [current, *current.parents]:
        superpowers = parent / "superpowers"
        if superpowers.is_dir() and (superpowers / ".env").exists():
            return superpowers

    return None


def load_superpowers_env() -> bool:
    """
    Automatically find and load superpowers/.env file, or use existing environment variables.

    Returns:
        True if environment is available (either loaded or already set), False otherwise
    """
    # Check if required variables are already set in environment
    required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    already_set = all(os.environ.get(var) for var in required_vars)

    if already_set:
        print("✓ Using existing environment variables")
        return True

    # Try to find and load superpowers/.env
    superpowers = find_superpowers_dir()

    if not superpowers:
        print("⚠ Could not find superpowers/.env")
        print(f"\nSearched from: {Path.cwd()}")
        print("\nTo use this skill, either:")
        print("  1. Create superpowers/.env with Langfuse credentials:")
        print("     LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("     LANGFUSE_SECRET_KEY=sk-lf-...")
        print("     LANGFUSE_HOST=https://your-instance.com")
        print("\n  2. Or set environment variables manually:")
        print("     export LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("     export LANGFUSE_SECRET_KEY=sk-lf-...")
        print("     export LANGFUSE_HOST=https://your-instance.com")
        return False

    env_file = superpowers / ".env"

    if not env_file.exists():
        print(f"⚠ {env_file} not found")
        print("\nCreate it with:")
        print(f"  cp {superpowers}/.env.example {env_file}")
        print("  # Then edit with your Langfuse credentials")
        print("\nOr set environment variables manually (see above)")
        return False

    # Load environment variables from file
    try:
        loaded_count = 0
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Parse key=value
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove inline comments (anything after #)
                    if "#" in value:
                        value = value.split("#")[0].strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not empty
                    if value:
                        os.environ[key] = value
                        loaded_count += 1

        print(f"✓ Loaded {loaded_count} variables from: {env_file}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to load {env_file}: {e}")
        return False


def find_project_root() -> Path:
    """
    Find the project root directory (parent of superpowers).

    Returns:
        Path to project root
    """
    superpowers = find_superpowers_dir()
    if superpowers:
        return superpowers.parent
    return Path.cwd()
