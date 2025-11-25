---
name: twilio-test-caller
description: Place test voice calls via Twilio. Use when testing voice features or debugging voice pipeline. Only works if twilio_place_call.py exists in branch.
dependencies:
  - tailscale-manager
---

# Twilio Test Caller

Place test voice calls to validate voice conversation features end-to-end.

## How It Works (Simple Version)

**Key concept: The script simulates a USER calling INTO our system.**

1. **Script calls Twilio API** → Twilio places call FROM +18643997362 (TestCaller) TO +19144449736 (webhook number)
2. **Twilio receives call on webhook number** → +19144449736 is configured with webhook URL in Twilio console
3. **Twilio hits our webhook** → Our API receives the call, looks up the CALLER (+18643997362)
4. **Caller must have GROUP conversation** → TestCaller (person 175) has GROUP conversation 251
5. **Tailscale forwards** → Public HTTPS request → localhost:8082
6. **Audio streams** → VAD + Whisper transcription + GPT enrichment run
7. **You see logs** → `docker logs ct1-api-1` shows "Received Twilio voice webhook call_sid=CA..."

**Important distinctions:**
- `--from` = WHO is calling (must be a Twilio-owned number with a person who has a GROUP conversation)
- `--to` = The Twilio number with webhooks configured (our "phone line")

**If you DON'T see logs in step 7 → something in the pipeline is broken.**

**For detailed pipeline flow with all 12 steps, see the `run-voice-e2e` skill which includes a complete diagnostic table.**

## When to Use

- User asks to place/test a call
- Testing voice pipeline (transcription, enrichment, interventions)
- Debugging voice call handling
- Verifying voice webhooks work

## Prerequisites

**⚠️ DEPENDENCY: This skill requires the tailscale-manager skill**

Before placing calls, verify:
1. ✅ `twilio_place_call.py` exists
2. ✅ Docker is running
3. ✅ **Tailscale funnel is active** (managed by tailscale-manager skill)
4. ✅ **Twilio number webhook points to Tailscale URL** (CRITICAL!)
5. ✅ Environment variables set
6. ✅ **Phone numbers are verified for your Twilio account** (see Phone Number Verification below)

## Setup Workflow

### 1. Check Script Exists
```bash
find . -maxdepth 4 -name "twilio_place_call.py" -type f 2>/dev/null
```
If not found, this branch doesn't have voice features.

### 2. Verify Docker Running
```bash
docker compose ps  # All services should be "Up"
docker compose up -d  # If any are down
```

### 3. Check Tailscale Funnel

**Use the tailscale-manager skill to verify and manage the funnel:**

```bash
sudo tailscale funnel status
```

Expected output when running:
```
https://wakeup.tail<hash>.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:8082
```

**If funnel is not running, use the tailscale-manager skill workflow:**
1. Check current status: `sudo tailscale funnel status`
2. Stop any existing funnel: `sudo tailscale funnel --https=443 off`
3. Start funnel for your ct project: `sudo tailscale funnel --https=443 8082`
4. Verify it started: `sudo tailscale funnel status`

See `.claude/skills/tailscale-manager/SKILL.md` for full funnel management workflow.

### 4. Phone Number Verification (CRITICAL!)

**⚠️ COMMON ERROR:** If you see this error when placing a call:
```
⚠  WARNING: +14155697366 is NOT verified for outbound calls
   This number can only RECEIVE calls, not place them.
   To verify for outbound calling, visit:
   https://console.twilio.com/us1/develop/phone-numbers/manage/verified
```

**This means the `--from` number is not verified for YOUR Twilio account.**

**Understanding Twilio Phone Number Types:**
- **Owned Numbers**: Numbers you purchased through Twilio (always work for outbound calls)
- **Verified Numbers**: Numbers you manually verified in Twilio console (can make outbound calls)
- **Unverified Numbers**: Numbers you don't own and haven't verified (RECEIVE only, cannot send)

**How to find YOUR verified numbers:**

The arsenal install script automatically installed and configured the Twilio CLI. Use it to list your available numbers:

```bash
# List all phone numbers in your Twilio account
twilio phone-numbers:list

# Example output:
# SID                                 Phone Number  Friendly Name
# PNd611e21fe212b13af84fad19f3dc7a83  +18643997362  (864) 399-7362
# PNea88101fbb3710daf9b18696439b585f  +16503977712  (650) 397-7712
```

**These are the numbers you can use with `--from` parameter.**

**If you need to use a number not in your account:**
1. Visit https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Click "Add a new number"
3. Verify via SMS or voice call
4. Wait for verification to complete
5. Use that number with `--from`

**Default numbers in documentation are examples only - substitute with YOUR verified numbers.**

### 5. Verify Twilio Webhook (CRITICAL!)

Check webhook configuration:
```bash
docker compose exec api bash -lc 'set -a && source /app/.env && set +a && python -c "
from twilio.rest import Client
import os
client = Client(os.environ[\"TWILIO_ACCOUNT_SID\"], os.environ[\"TWILIO_AUTH_TOKEN\"])
numbers = client.incoming_phone_numbers.list(phone_number=\"+16503977712\")
for number in numbers:
    print(f\"Voice URL: {number.voice_url}\")"'
```

Expected: `https://YOUR-MACHINE.tailXXXXXX.ts.net/webhook/voice/twilio`

If wrong, update webhook:
```bash
docker compose exec api bash -lc 'set -a && source /app/.env && set +a && python -c "
from twilio.rest import Client
import os
client = Client(os.environ[\"TWILIO_ACCOUNT_SID\"], os.environ[\"TWILIO_AUTH_TOKEN\"])
numbers = client.incoming_phone_numbers.list(phone_number=\"+16503977712\")
for number in numbers:
    number.update(voice_url=\"https://YOUR-MACHINE.tailXXXXXX.ts.net/webhook/voice/twilio\", voice_method=\"POST\")
    print(f\"Updated {number.phone_number}\")"'
```

## Place a Call (It's Simple)

**First, ensure your .env has these variables set:**
```bash
# In api/.env
TWILIO_VOICE_PHONE_NUMBER=+19144449736  # Your webhook number (the number to call INTO)
TWILIO_TEST_CALLER_NUMBER=+18643997362  # Test caller with GROUP conversation
```

**Then just run:**
```bash
cd api && set -a && source .env && set +a && \
PYTHONPATH=src uv run python src/scripts/twilio_place_call.py --duration-minutes 1
```

**That's it. If everything is configured correctly, you'll see logs in `docker logs ct1-api-1`.**

**Parameters (all have env var defaults):**
- `--from` - WHO is calling (env: `TWILIO_TEST_CALLER_NUMBER`). Must have GROUP conversation.
- `--to` - Webhook number to call INTO (env: `TWILIO_VOICE_PHONE_NUMBER`)
- `--duration-minutes` - How long to keep call active (default: 6 minutes, use 1 for quick tests)
- `--audio` - Test audio to play (see below)

**Test Audio Options (use ONLY these for consistency):**
- `--audio fight` (default) - Couple conflict audio, triggers interventions
- `--audio neutral` - Silero VAD test audio, no conflict, tests basic pipeline

```bash
# Test with conflict audio (triggers interventions)
PYTHONPATH=src uv run python src/scripts/twilio_place_call.py --audio fight --duration-minutes 1

# Test basic pipeline without conflict
PYTHONPATH=src uv run python src/scripts/twilio_place_call.py --audio neutral --duration-minutes 1
```

**Verify Interventions After Call:**
After placing a call, verify that interventions were created by visiting the frontend:
```
http://100.93.144.78:5174/
```

**⚠️ PORT PATTERN:** The frontend port MUST match your directory number:
- ct1 → http://100.93.144.78:5171/
- ct2 → http://100.93.144.78:5172/
- ct3 → http://100.93.144.78:5173/
- ct4 → http://100.93.144.78:5174/ ← YOU ARE HERE

This requires the vite dev server to be running. Start it with:
```bash
cd /home/odio/Hacking/codel/ct4/frontend && npm run dev
```
Vite will automatically use port 5174 (configured in vite.config.ts).

## Monitor Call

**Tail logs immediately:**
```bash
docker compose logs -f api worker
```

**Look for:**
- API receives webhook: `POST /webhook/voice-call`
- Worker processes: `Transcribing audio chunk`
- Enrichment: `voice_message_enricher prompt used`
- Interventions: `Sending intervention to...`

**Check for call activity:**
```bash
docker compose logs --since 5m | grep -iE -B 5 -A 5 "call|voice|twilio"
```

## Troubleshooting - Work Backwards

**Error: "WARNING: +XXXXX is NOT verified for outbound calls" → Phone number verification issue:**

1. **Find YOUR verified numbers:**
   ```bash
   twilio phone-numbers:list
   ```
   Use one of these numbers with `--from` parameter

2. **If you need a different number:**
   - Visit https://console.twilio.com/us1/develop/phone-numbers/manage/verified
   - Verify the number through Twilio console
   - Wait for verification to complete
   - Then use it with `--from`

**Call placed but NO LOGS in docker → Check in this order:**

1. **Is Docker running?**
   ```bash
   docker compose ps
   # All services should show "Up"
   ```
   Fix: `docker compose up -d`

2. **Is Tailscale funnel active?**
   ```bash
   tailscale funnel status
   # Should show: https://wakeup.tail... (Funnel on) |-- / proxy http://127.0.0.1:8084
   ```
   Fix: `tailscale funnel --https=443 8084`

3. **Is webhook configured in Twilio?**
   ```bash
   # Check what webhook URL is set
   set -a && source .env && set +a && python -c "
   from twilio.rest import Client; import os
   client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
   for n in client.incoming_phone_numbers.list(phone_number='+16503977712'):
       print(f'Voice URL: {n.voice_url}')
   "
   ```
   Expected: `https://wakeup.tail3b4b7f.ts.net/webhook/voice/twilio`

**Call logs appear but NO VAD/transcription → Check:**
- Audio URL is accessible: `curl -I <audio-url>` (should return 200 OK)
- Worker is running: `docker compose ps | grep worker`
- OpenAI API key set: `grep OPENAI_API_KEY .env`

## Quick Reference

```bash
# Pre-flight check
find . -maxdepth 4 -name "twilio_place_call.py" -type f 2>/dev/null
docker compose ps
sudo tailscale funnel status  # Use tailscale-manager skill commands

# Verify webhook on your TWILIO_VOICE_PHONE_NUMBER
docker compose exec api bash -lc 'set -a && source /app/.env && set +a && python -c "from twilio.rest import Client; import os; client = Client(os.environ[\"TWILIO_ACCOUNT_SID\"], os.environ[\"TWILIO_AUTH_TOKEN\"]); [print(f\"Voice URL: {n.voice_url}\") for n in client.incoming_phone_numbers.list(phone_number=os.environ.get(\"TWILIO_VOICE_PHONE_NUMBER\"))]"'

# Place 1-minute call (uses env vars: TWILIO_TEST_CALLER_NUMBER -> TWILIO_VOICE_PHONE_NUMBER)
cd api && set -a && source .env && set +a && \
PYTHONPATH=src uv run python src/scripts/twilio_place_call.py --duration-minutes 1

# Monitor
docker compose logs -f api worker
docker compose logs --since 5m | grep -iE "call|voice|twilio"
```

## Required Environment Variables

In `api/.env`:
```bash
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_VOICE_PHONE_NUMBER=+19144449736  # Webhook number to call INTO (each dev may have different)
TWILIO_TEST_CALLER_NUMBER=+18643997362  # Test caller phone (must have GROUP conversation)
OPENAI_API_KEY=sk-xxxxx
LANGFUSE_PUBLIC_KEY=pk-xxxxx
LANGFUSE_SECRET_KEY=sk-xxxxx
LANGFUSE_HOST=https://langfuse.prod.cncorp.io
```

**Notes:**
- Keep calls short (1 min) - costs money, uses Twilio slots
- Tailscale funnel must stay running during test
- Phone numbers need country code (+16503977712)
