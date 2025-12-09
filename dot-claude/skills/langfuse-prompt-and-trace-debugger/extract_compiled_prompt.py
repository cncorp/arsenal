#!/usr/bin/env python3
"""
Extract compiled prompt from a Langfuse trace.

Usage:
    # By trace ID
    python extract_compiled_prompt.py --trace-id 9bc3029d-60b8-40cf-b0d7-417fc7f53604

    # Save to file
    python extract_compiled_prompt.py --trace-id TRACE_ID --output /path/to/file.md

    # Use production Langfuse (default is staging)
    python extract_compiled_prompt.py --trace-id TRACE_ID --production

This script extracts the compiled prompt from a Langfuse trace,
useful for debugging why a particular response was generated.

⚠️ LIMITATION: Langfuse API truncates large data (~10KB for outputs).
For full prompts with conversation history, use `reconstruct_compiled_prompt.py` instead.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse
from langfuse.api import NotFoundError


def extract_compiled_prompt(trace_id: str, langfuse: Langfuse) -> dict | None:
    """
    Extract the compiled prompt from a Langfuse trace.

    Returns dict with:
        - compiled_prompt: The full compiled prompt text
        - prompt_name: Name of the prompt used
        - timestamp: When the trace was created
        - input_variables: Variables passed to the prompt
        - llm_output: The LLM's response

    Returns None if trace is not found.
    """
    try:
        trace = langfuse.fetch_trace(trace_id)
        data = trace.data
    except NotFoundError:
        print(f"Trace not found: {trace_id}")
        return None

    result = {
        "trace_id": trace_id,
        "trace_name": data.name,
        "timestamp": str(data.timestamp),
        "compiled_prompt": None,
        "input_variables": None,
        "llm_output": None,
    }

    for obs in data.observations or []:
        # Find the main prompt compilation (not enricher)
        if obs.name == "prompt_compilation" and obs.type == "SPAN":
            if hasattr(obs, "output") and obs.output:
                output = obs.output
                # Skip the intervention conditions YAML
                if isinstance(output, str) and "condition_key:" not in output:
                    if result["compiled_prompt"] is None or len(output) > len(result["compiled_prompt"]):
                        result["compiled_prompt"] = output
                        if hasattr(obs, "input") and obs.input:
                            result["input_variables"] = obs.input

        # Get the LLM output
        if obs.type == "GENERATION" and obs.name == "llm_call":
            if hasattr(obs, "output") and obs.output:
                # Skip enricher outputs (they have 'affect' field)
                output = obs.output
                if isinstance(output, dict) and "affect" not in output:
                    result["llm_output"] = output

    return result


def format_as_markdown(data: dict) -> str:
    """Format the extracted data as a markdown document."""

    # Convert timestamp to US/Pacific (handles DST automatically)
    ts = data.get("timestamp", "")
    if ts:
        try:
            dt = datetime.fromisoformat(ts.replace("+00:00", "+00:00").replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("UTC"))
            dt_pacific = dt.astimezone(ZoneInfo("America/Los_Angeles"))
            tz_abbrev = dt_pacific.strftime("%Z")  # PST or PDT
            ts_formatted = f"{dt_pacific.strftime('%Y-%m-%d %H:%M:%S')} {tz_abbrev} ({ts})"
        except ValueError:
            ts_formatted = ts
    else:
        ts_formatted = "Unknown"

    md = f"""# Compiled Prompt Debug

## Trace Metadata
- **Trace ID**: {data.get('trace_id', 'Unknown')}
- **Trace Name**: {data.get('trace_name', 'Unknown')}
- **Timestamp**: {ts_formatted}
"""

    md += "\n---\n\n"

    # Add LLM output if available
    if data.get("llm_output"):
        md += "## LLM Output\n\n```json\n"
        md += json.dumps(data["llm_output"], indent=2)
        md += "\n```\n\n---\n\n"

    # Add compiled prompt
    md += "## Compiled Prompt\n\n"
    if data.get("compiled_prompt"):
        md += data["compiled_prompt"]
    else:
        md += "*No compiled prompt found in trace*"

    md += "\n\n---\n\n"

    # Add input variables summary
    if data.get("input_variables"):
        md += "## Input Variables\n\n"
        md += "| Variable | Value (truncated) |\n"
        md += "|----------|-------------------|\n"
        for key, value in sorted(data["input_variables"].items()):
            val_str = str(value)
            if len(val_str) > 100:
                val_str = val_str[:100] + "..."
            # Escape pipes for markdown table
            val_str = val_str.replace("|", "\\|").replace("\n", " ")
            md += f"| `{key}` | {val_str} |\n"

    return md


def main():
    parser = argparse.ArgumentParser(
        description="Extract compiled prompt from Langfuse trace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--trace-id", "-t",
        type=str,
        required=True,
        help="Langfuse trace ID"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: print to stdout)"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Use production Langfuse server (default: staging)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of markdown"
    )

    args = parser.parse_args()

    # Load environment
    if not load_superpowers_env():
        sys.exit(1)

    # Select environment
    env = "production" if args.production else "staging"
    select_langfuse_environment(env)

    # Initialize Langfuse
    langfuse = Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ["LANGFUSE_HOST"],
    )

    # Extract prompt
    print(f"Extracting compiled prompt from trace: {args.trace_id}")
    data = extract_compiled_prompt(args.trace_id, langfuse)

    if not data:
        print("ERROR: Could not extract prompt from trace")
        sys.exit(1)

    if not data.get("compiled_prompt"):
        print("WARNING: No compiled prompt found in trace")

    # Format output
    if args.json:
        output = json.dumps(data, indent=2)
    else:
        output = format_as_markdown(data)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(output)
        print(f"Saved to: {output_path}")
    else:
        print("\n" + "=" * 60)
        print(output)


if __name__ == "__main__":
    main()
