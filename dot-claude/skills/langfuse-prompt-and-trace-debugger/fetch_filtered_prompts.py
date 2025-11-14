#!/usr/bin/env python3
"""Fetch production prompts matching criteria: onboarding, yaml, or >1000 observations"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env

# Load environment and switch to production
load_superpowers_env()

# Override with production credentials
os.environ["LANGFUSE_PUBLIC_KEY"] = os.environ.get("LANGFUSE_PUBLIC_KEY_PROD", "")
os.environ["LANGFUSE_SECRET_KEY"] = os.environ.get("LANGFUSE_SECRET_KEY_PROD", "")
os.environ["LANGFUSE_HOST"] = os.environ.get("LANGFUSE_HOST_PROD", "")

from langfuse import Langfuse

# Use production credentials
public_key = os.environ["LANGFUSE_PUBLIC_KEY"]
secret_key = os.environ["LANGFUSE_SECRET_KEY"]
host = os.environ["LANGFUSE_HOST"]

if not all([public_key, secret_key, host]):
    print("ERROR: Missing production Langfuse credentials")
    sys.exit(1)

print(f"Connecting to production Langfuse: {host}\n")

client = Langfuse(
    public_key=public_key,
    secret_key=secret_key,
    host=host
)

# Fetch all prompts
print("Fetching all prompts from production...")
all_prompts = []
page = 1

while True:
    response = client.api.prompts.list(page=page, limit=100)
    page_prompts = response.data
    all_prompts.extend(page_prompts)
    
    if len(page_prompts) < 100:
        break
    page += 1

print(f"Found {len(all_prompts)} total prompts\n")

matching_prompts = []

for prompt_meta in all_prompts:
    name = prompt_meta.name
    
    # Check criteria based on name
    has_onboarding = 'onboarding' in name.lower()
    has_yaml = 'yaml' in name.lower()
    
    if has_onboarding or has_yaml:
        matching_prompts.append({
            'name': name,
            'reason': (
                'onboarding' if has_onboarding else 'yaml'
            )
        })

# Add known high-observation prompts from the screenshot
high_obs_prompts = [
    ('group_msg_needs_affirmation', 1039),
    ('group_msg_intervention_needed_sender', 1682),
    ('group_msg_intervention_needed_recipient', 1202),
    ('onboarding_1on1_no_group_thread_responses', 1237),
    ('1on1', 3078),
    ('fact_extractor_1on1', 1107),
    ('oh-by-the-way', 2756),
    ('fact_extractor', 1572),
    ('message_enricher', 36130),
    ('fact_reconciler', 2227)
]

for prompt_name, obs_count in high_obs_prompts:
    if not any(p['name'] == prompt_name for p in matching_prompts):
        matching_prompts.append({
            'name': prompt_name,
            'reason': f'{obs_count:,} observations'
        })

# Sort by name
matching_prompts.sort(key=lambda x: x['name'])

print(f"Matching prompts ({len(matching_prompts)} total):\n")
for p in matching_prompts:
    print(f"  • {p['name']:<50} ({p['reason']})")

# Print list for refresh_prompt_cache.py
print(f"\n\nTo fetch all {len(matching_prompts)} prompts, run:\n")
prompt_names = ' '.join([p['name'] for p in matching_prompts])
print(f"uv run python refresh_prompt_cache.py {prompt_names}")
