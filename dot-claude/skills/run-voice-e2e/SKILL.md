---
name: run-voice-e2e
description: Complete E2E workflow for voice calls - database setup, user creation, infrastructure verification, and call testing. Use when setting up voice testing from scratch or debugging voice pipeline issues.
dependencies:
  - tailscale-manager
  - twilio-test-caller
---

# Voice E2E Testing Workflow

**Simple rule: Place a call, check if logs appear. If no logs → something's broken.**

## When to Use

- Setting up voice testing for the first time
- Debugging voice call failures
- Running voice baseline metrics collection
- Verifying complete voice pipeline works E2E

## Critical Architecture Requirement

**⚠️ EVERY voice user MUST have THREE conversation types:**

1. **GROUP** conversation - Contains 2 MEMBERS (the couple) + 1 THERAPIST (the AI coach)
2. **ONE_ON_ONE** conversation - Contains 1 MEMBER + 1 THERAPIST
3. **VOICE** conversation - Created automatically during calls

**Why all three are required:**
- The voice webhook looks up the caller's GROUP conversation to find their partner
- But VOICE uses a different therapist Person than text messaging
- The ONE_ON_ONE bridges this: `VOICE → ONE_ON_ONE → GROUP`
- Without ONE_ON_ONE, the lookup fails with: `ValueError: No ONE_ON_ONE conversation found for VOICE conversation`

See `api/src/data/models/conversation.py:220-236` for the implementation.

### 🚨 CRITICAL: Provider Requirements

**Each conversation type MUST use the correct provider:**

| Conversation Type | Required Provider | Why |
|------------------|-------------------|-----|
| GROUP | `'system'` | Group conversations are system-managed |
| ONE_ON_ONE | `'sendblue'` | **CRITICAL**: `get_conversation()` skips all `provider='twilio_voice'` conversations |
| VOICE | `'twilio_voice'` | Voice calls are handled by Twilio |

**⚠️ COMMON BUG - Wrong ONE_ON_ONE Provider:**

If ONE_ON_ONE uses `provider='twilio_voice'`, you will see:
```
ValueError: No conversation found with exactly these participants: self.id=X, other_ids=[Y]
```

**Root Cause**: The `get_conversation()` method in `api/src/data/helpers/models.py` (lines 185-186) explicitly skips conversations with `provider='twilio_voice'`:

```python
if conversation.provider == "twilio_voice":
    continue  # Skip voice conversations when looking up ONE_ON_ONE
```

**Fix**: ONE_ON_ONE conversations MUST use `provider='sendblue'`. This is already handled correctly in the setup script below (line 335).

**📚 For complete documentation, see:** `api/docs/VOICE_CONVERSATION_SETUP.md`

## Prerequisites

1. ✅ Docker running (`docker compose ps`)
2. ✅ Tailscale funnel active (use `tailscale-manager` skill)
3. ✅ Environment variables configured (`.env` file)
4. ✅ Database running and accessible

## Complete Pipeline Flow

**Understand the flow from script → logs to debug issues:**

**⚠️ DETECT YOUR ENVIRONMENT FIRST**:

Before running any commands, detect which ct directory you're in:

```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
echo "Current environment: ct${CT_DIR}"
```

**⚠️ PORT PATTERN - CRITICAL**: We use parallel dev environments (ct1, ct2, ct3, ct4). **THE LAST DIGIT IN EVERY PORT NUMBER MUST MATCH THE LAST DIGIT IN THE DIRECTORY NAME**:

| Directory | API Port | Postgres Port | Redis Port | Vite Port |
|-----------|----------|---------------|------------|-----------|
| ct1       | 8081     | 5431          | 6371       | 5171      |
| ct2       | 8082     | 5432          | 6372       | 5172      |
| ct3       | 8083     | 5433          | 6373       | 5173      |
| ct4       | 8084     | 5434          | 6374       | 5174      |

**Port calculation: ct${CT_DIR} → All ports end in ${CT_DIR}**

This pattern applies to:
- Tailscale funnel: `tailscale funnel --https=443 808${CT_DIR}`
- API health check: `http://localhost:808${CT_DIR}/health`
- Frontend URL: `http://100.93.144.78:517${CT_DIR}/`
- Database connection: `localhost:543${CT_DIR}`
- Redis connection: `localhost:637${CT_DIR}`

**🚨 COMMON MISTAKE - VITE DEFAULT PORT**: Vite defaults to port 5173. You MUST configure the port via environment variable in `frontend/.env.local`:

```bash
# Detect your environment and set the correct port
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
echo "VITE_WEB_PORT=517${CT_DIR}" > frontend/.env.local
echo "VITE_API_PORT=808${CT_DIR}" >> frontend/.env.local
```

The `vite.config.ts` reads these environment variables:
```typescript
const webPort = env.VITE_WEB_PORT || "5173";
const apiPort = env.VITE_API_PORT || "8000";
```

**Always verify the port matches your directory!**

| Step | Component | What Happens | Required Configuration | Expected Feedback/Logs | How to Verify |
|------|-----------|--------------|----------------------|----------------------|---------------|
| 1 | **Script Execution** | `twilio_place_call.py` sends API request to Twilio | `.env` has TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN | Terminal: `Started call CA... from +18643997362 to +16503977712` | Script runs without error |
| 2 | **Twilio Places Call** | Twilio initiates outbound call FROM +18643997362 TO +16503977712 | Phone number +16503977712 exists in Twilio account | Terminal: `status: in-progress` | Call connects (not busy/failed) |
| 3 | **Twilio Checks Webhook** | +16503977712 has webhook configured, Twilio POSTs to that URL | Twilio console: Voice URL = `https://wakeup.tail3b4b7f.ts.net/webhook/voice/twilio` | Twilio makes HTTP POST request | Check Twilio debugger console |
| 4 | **Tailscale Receives Request** | Public HTTPS request hits Tailscale funnel | `tailscale funnel status` shows `https://wakeup.tail3b4b7f.ts.net` → `http://127.0.0.1:808${CT_DIR}` | Funnel proxies request to localhost | `tailscale funnel status` |
| 5 | **Docker API Receives** | FastAPI container receives POST on port 808${CT_DIR} | `docker compose ps` shows ct${CT_DIR}-api-1 running, listening on port 808${CT_DIR} | **API LOG**: `Received Twilio voice webhook call_sid=CA...` | `docker logs ct${CT_DIR}-api-1 \| grep "Received Twilio"` |
| 6 | **Webhook Processes** | API looks up conversation, returns TwiML | Database has registered voice users with GROUP+ONE_ON_ONE+VOICE convos | **API LOG**: `Resolved existing voice caller`, `Using caller's voice contact` | `docker logs ct${CT_DIR}-api-1 \| grep "voice caller"` |
| 7 | **TwiML Response** | FastAPI returns XML: `<Response><Say>...</Say><Connect><Stream url="wss://..."/></Connect></Response>` | TwiML includes WebSocket URL: `wss://wakeup.tail3b4b7f.ts.net/webhook/voice/twilio/stream` | Twilio receives 200 OK with TwiML body | API logs show HTTP 200 response |
| 8 | **Twilio → WebSocket** | Twilio opens WebSocket connection to stream endpoint, starts streaming audio | WebSocket endpoint `/webhook/voice/twilio/stream` implemented, Tailscale funnel supports WebSocket upgrade | **API LOG**: `connection open`, `Twilio media stream started` | `docker logs ct${CT_DIR}-api-1 \| grep "media stream started"` |
| 9 | **Stream Processing** | StreamingTranscriptProcessor + RealtimeProcessor initialized, VAD starts | Silero VAD model cached, OpenAI API key configured, Langfuse configured | **API LOG**: `VAD model loaded`, `OpenAI Realtime WebSocket connected`, `Langfuse configuration loaded` | VAD and Realtime processor logs appear |
| 10 | **Audio Processing** | Twilio streams mulaw audio → decoded → VAD segments → queued for transcription | Worker container running, Redis available | **API LOG**: `Running VAD over audio chunk`, `Queueing streaming segment`, `Enqueued streaming segment` | Audio segments detected and queued |
| 11 | **Worker/Transcription** | RQ worker picks up transcription job, calls OpenAI Whisper API | ct${CT_DIR}-worker-1 running, OPENAI_API_KEY valid | **WORKER LOG**: transcription results | `docker logs ct${CT_DIR}-worker-1` shows job processing |
| 12 | **End Call** | Call duration expires or hangup, WebSocket closes, cleanup | - | **API LOG**: `Persisted Twilio media stream to WAV`, `Finalizing Realtime processor`, `OpenAI WebSocket closed` | Cleanup logs, WAV file saved to `/app/tmp/twilio_streams/` |

**Use this table to diagnose issues: If you don't see logs at step N, check the configuration for step N.**

## Step 1: Verify Infrastructure

### Detect Your Environment
First, determine which ct directory you're in:
```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
echo "Current environment: ct${CT_DIR}"
echo "API Port: 808${CT_DIR}"
echo "Worker container: ct${CT_DIR}-worker-1"
```

### Check Docker Services
```bash
# Navigate to your ct directory
cd ~/Hacking/codel/ct${CT_DIR}
docker compose ps
```

All services should show "Up". If not:
```bash
docker compose up -d
```

### Check Tailscale Funnel
Use the `tailscale-manager` skill to verify:
```bash
sudo tailscale funnel status
```

Expected output (port should match your ct directory):
```
https://wakeup.tail3b4b7f.ts.net (Funnel on)
|-- / proxy http://127.0.0.1:808${CT_DIR}
```

If funnel is not running, start it with the correct port:
```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
sudo tailscale funnel --https=443 808${CT_DIR}
```

### Verify API Health
```bash
curl https://wakeup.tail3b4b7f.ts.net/health
```

Expected: `{"status":"healthy"}`

## Step 2: Set Up Test Users

**CRITICAL:** Each voice user needs all three conversation types (GROUP, ONE_ON_ONE, VOICE).

### Check Existing Users
```bash
# Detect your environment
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api

set -a && source .env && set +a && PYTHONPATH=src uv run python -c "
from config.database import get_session
from data.helpers.models import PersonContacts

with get_session() as session:
    # Check if users exist
    jake = session.query(PersonContacts).filter_by(
        handle='+16504850071',
        provider='twilio_voice'
    ).first()

    mary = session.query(PersonContacts).filter_by(
        handle='+13607896822',
        provider='twilio_voice'
    ).first()

    if jake:
        print(f'✅ Jake exists: Person {jake.person_id}')
    else:
        print('❌ Jake does not exist')

    if mary:
        print(f'✅ Mary exists: Person {mary.person_id}')
    else:
        print('❌ Mary does not exist')
"
```

### Create Users If Needed

Run the setup script (already in the repo):
```bash
# Detect environment and run setup
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api
set -a && source .env && set +a && PYTHONPATH=src uv run python src/cli/setup_voice_e2e_users.py
```

### Verify User Setup

Check that all conversations exist:

```bash
# Detect environment
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api

set -a && source .env && set +a && PYTHONPATH=src uv run python -c "
from config.database import get_session
from data.models.conversation import Conversation, ConversationParticipant
from data.models.enums import ConversationType

with get_session() as session:
    # Get Jake's conversations
    jake_participants = session.query(ConversationParticipant).filter(
        ConversationParticipant.person_id == 12  # Jake's person_id - ADJUST AS NEEDED
    ).all()

    print('Jake conversations:')
    for cp in jake_participants:
        conv = session.query(Conversation).filter(Conversation.id == cp.conversation_id).first()
        participant_count = session.query(ConversationParticipant).filter(
            ConversationParticipant.conversation_id == conv.id
        ).count()
        print(f'  ✅ {conv.type.name}: ID {conv.id}, {participant_count} participants')
"
```

Expected output:
```
Jake conversations:
  ✅ GROUP: ID 16, 3 participants
  ✅ ONE_ON_ONE: ID 18, 2 participants
  ✅ VOICE: ID 17, 3 participants (if call already made)
```

## Step 3: Place Test Calls

**⚠️ DEPENDENCY: Use the `twilio-test-caller` skill to place calls**

**To place a test call, invoke the `twilio-test-caller` skill.**

The twilio-test-caller skill will:
1. Guide you to find your verified Twilio phone numbers
2. Explain how to configure the call parameters
3. Place an automated test call with audio
4. Monitor the call progress

**The call tests the complete flow:**
1. Twilio receives inbound call
2. Twilio webhook calls your API via Tailscale funnel
3. API finds Jake's GROUP conversation (via ONE_ON_ONE lookup)
4. API creates VOICE conversation
5. WebSocket streams audio
6. VAD detects speech segments
7. Transcription happens
8. Messages saved to database

**Always use the twilio-test-caller skill for programmatic testing - it handles phone number verification and provides step-by-step guidance.**

## Step 4: Monitor the Call

### Watch logs in real-time:
```bash
# Detect environment
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}

docker logs ct${CT_DIR}-api-1 -f --tail 50
```

### Look for these events:
1. ✅ `Received Twilio voice webhook` - Call received
2. ✅ `WebSocket /webhook/voice/twilio/stream` - WebSocket connected
3. ✅ `Twilio media stream started` - Audio streaming started
4. ✅ `Initialized streaming VAD` - Voice activity detection ready
5. ✅ `Speech segment detected` - Speech found in audio
6. ✅ `Transcription job queued` - Sent to worker for transcription
7. ✅ `Transcription completed` - Text extracted from audio

### Check for errors:
```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
docker logs ct${CT_DIR}-api-1 --since 2m 2>&1 | grep -i error
```

Common errors and fixes:
- `ValueError: This method is only valid for couple group conversations` → GROUP needs 3 participants (2 MEMBERS + 1 THERAPIST)
- `ValueError: No ONE_ON_ONE conversation found` → Create ONE_ON_ONE conversation for user
- `Unregistered caller` → User not in database
- `FATAL: Caller has no active GROUP conversation` → Create GROUP conversation

## Step 5: Verify Transcriptions

Check if messages were created:

```bash
# Detect environment
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api

set -a && source .env && set +a && PYTHONPATH=src uv run python -c "
from config.database import get_session
from data.models.message import Message
from data.models.conversation import Conversation
from data.models.enums import ConversationType

with get_session() as session:
    # Find recent VOICE conversation
    voice_conv = session.query(Conversation).filter(
        Conversation.type == ConversationType.VOICE
    ).order_by(Conversation.created_at.desc()).first()

    if voice_conv:
        print(f'Latest VOICE conversation: {voice_conv.id}')
        print(f'  Call SID: {voice_conv.provider_key}')

        # Get messages
        messages = session.query(Message).filter(
            Message.conversation_id == voice_conv.id
        ).order_by(Message.created_at).all()

        print(f'  Messages: {len(messages)}')
        for msg in messages:
            print(f'    - {msg.content[:100]}...')
    else:
        print('No VOICE conversations found')
"
```

## Step 6: Verify Interventions

After transcriptions are created, verify that interventions were generated by the AI coach.

### Start Frontend Server (if not running):

**BEFORE starting Vite, verify the port is configured correctly!**

```bash
# Detect environment and configure Vite ports
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
echo "VITE_WEB_PORT=517${CT_DIR}" > ~/Hacking/codel/ct${CT_DIR}/frontend/.env.local
echo "VITE_API_PORT=808${CT_DIR}" >> ~/Hacking/codel/ct${CT_DIR}/frontend/.env.local
```

Then start:
```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/frontend
npm run dev
```

Expected output **MUST show port 517${CT_DIR}**:
```
  ➜  Local:   http://localhost:517${CT_DIR}/
  ➜  Network: http://100.93.144.78:517${CT_DIR}/
```

**If you see the wrong port, re-run the port configuration command above!**

### View Interventions:
Visit the frontend at:
```
# Replace ${CT_DIR} with your environment number (1, 2, 3, or 4)
http://100.93.144.78:517${CT_DIR}/
```

This will show all interventions created during the call. If no interventions appear, check:
- Worker logs for enrichment errors
- OpenAI API key is valid
- Messages exist in database (Step 5)

**⚠️ PORT PATTERN REMINDER:** The last digit in the port MUST match the last digit in the directory name. This applies to ALL services.

## Step 7: Collect Metrics

### Copy metrics from container:
```bash
# Detect environment
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api

docker cp ct${CT_DIR}-api-1:/app/tmp/stream_metrics.log worker_stream_metrics.log
```

### Analyze metrics:
```bash
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
cd ~/Hacking/codel/ct${CT_DIR}/api
uv run python analyze_worker_metrics.py
```

Expected output:
```
Event                               Count    Avg (ms)    P95 (ms)
=================================================================
transcription_job                       5      1250.45     1450.23
voice_message_enrichment                5       850.12      950.45
vad_speech_detection                   10        45.23       55.67
=================================================================
Total events                           20
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Call rejected with "Unregistered caller" | User not in database | Run `setup_voice_e2e_users.py` |
| `ValueError: couple group conversations` | GROUP missing THERAPIST | Add coach as THERAPIST to GROUP |
| `ValueError: No ONE_ON_ONE conversation` | Missing ONE_ON_ONE | Create ONE_ON_ONE with user + coach |
| WebSocket crashes | Infrastructure issue | Check Tailscale funnel, Docker logs |
| No transcriptions | OpenAI API issue | Check OPENAI_API_KEY, worker logs |
| No metrics logged | Instrumentation off | Verify `instrument_operation` in code |

## Quick Reference Commands

```bash
# Detect your environment first
CT_DIR=$(pwd | grep -oP 'ct\K[0-9]+')
echo "Current environment: ct${CT_DIR}"

# Pre-flight check
cd ~/Hacking/codel/ct${CT_DIR}
docker compose ps
sudo tailscale funnel status
curl https://wakeup.tail3b4b7f.ts.net/health

# Setup users
cd api && set -a && source .env && set +a && PYTHONPATH=src uv run python src/cli/setup_voice_e2e_users.py

# Make call - USE THE twilio-test-caller SKILL
# The skill handles phone number verification and provides step-by-step guidance

# Monitor logs
docker logs ct${CT_DIR}-api-1 -f --tail 50

# Check errors
docker logs ct${CT_DIR}-api-1 --since 2m 2>&1 | grep -i error

# Collect metrics
docker cp ct${CT_DIR}-api-1:/app/tmp/stream_metrics.log worker_stream_metrics.log
uv run python analyze_worker_metrics.py
```

## Skill Dependencies

This skill orchestrates the full E2E workflow and delegates specific tasks to other skills:

- **tailscale-manager** - Infrastructure: Manage Tailscale funnel for webhook access
- **twilio-test-caller** - Testing: Place programmatic test calls with audio
- **docker-log-debugger** - Debugging: Analyze Docker container issues

## Workflow Summary

1. **Setup** (this skill):
   - Verify infrastructure (Docker, Tailscale, API health)
   - Create test users with all required conversation types
   - Verify database integrity

2. **Test** (delegate to `twilio-test-caller`):
   - Place calls programmatically
   - Monitor call progress

3. **Verify** (this skill):
   - Check transcriptions in database
   - Collect and analyze metrics
   - Debug issues if any
