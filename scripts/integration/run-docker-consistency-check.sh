#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_DIR="$ROOT_DIR/.codex-tmp"
LOG_FILE="$TMP_DIR/docker-consistency.log"
API_BASE_URL="${MARP_CONSISTENCY_API_BASE_URL:-http://127.0.0.1:${API_PORT:-8000}/api}"
CURL_COMMON_ARGS=(--noproxy '*' -fsS)

mkdir -p "$TMP_DIR"
: > "$LOG_FILE"

log() {
  echo "$1" | tee -a "$LOG_FILE"
}

capture() {
  local output_file="$1"
  shift
  curl "${CURL_COMMON_ARGS[@]}" "$@" | tee "$output_file" >> "$LOG_FILE"
}

wait_for_api() {
  local max_attempts=30
  local attempt=1

  while [ "$attempt" -le "$max_attempts" ]; do
    if curl "${CURL_COMMON_ARGS[@]}" "$API_BASE_URL/health" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
    attempt=$((attempt + 1))
  done

  return 1
}

log "Starting postgres, redis, and api via Docker Compose..."
docker compose up -d postgres redis api | tee -a "$LOG_FILE"

log "Waiting for API health endpoint..."
if ! wait_for_api; then
  log "API did not become healthy in time."
  exit 1
fi

WORLD_STATE_BEFORE="$TMP_DIR/world-state-before.json"
WORLD_ADVANCE_AFTER="$TMP_DIR/world-advance-after.json"
CONVERSATIONS_AFTER="$TMP_DIR/conversations-after.json"
GROUP_MESSAGES_AFTER="$TMP_DIR/group-messages-after.json"
MOMENT_MESSAGES_AFTER="$TMP_DIR/moment-messages-after.json"
PRIVATE_CREATE="$TMP_DIR/private-create.json"
PRIVATE_MESSAGES_AFTER="$TMP_DIR/private-messages-after.json"
MOMENT_CREATE="$TMP_DIR/moment-create.json"

log "Fetching initial world state..."
capture "$WORLD_STATE_BEFORE" "$API_BASE_URL/world/state"

log "Advancing world by 700 seconds..."
capture "$WORLD_ADVANCE_AFTER" -X POST "$API_BASE_URL/world/advance?seconds=700"

log "Fetching social API snapshots..."
capture "$CONVERSATIONS_AFTER" "$API_BASE_URL/social/conversations"
capture "$GROUP_MESSAGES_AFTER" "$API_BASE_URL/social/conversations/conv-general/messages"
capture "$MOMENT_MESSAGES_AFTER" "$API_BASE_URL/social/conversations/conv-moments/messages"

log "Creating a private message through the API..."
capture \
  "$PRIVATE_CREATE" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"user-001","target_id":"char-001","content":"docker consistency ping"}' \
  "$API_BASE_URL/social/private-messages"

PRIVATE_CONVERSATION_ID="$(
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1], "r", encoding="utf-8"))["conversation_id"])' \
    "$PRIVATE_CREATE"
)"

capture \
  "$PRIVATE_MESSAGES_AFTER" \
  "$API_BASE_URL/social/conversations/$PRIVATE_CONVERSATION_ID/messages"

log "Creating a moment through the API..."
capture \
  "$MOMENT_CREATE" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"char-001","content":"docker consistency moment","mentions":["char-002"]}' \
  "$API_BASE_URL/social/moments"

python3 - "$WORLD_STATE_BEFORE" "$WORLD_ADVANCE_AFTER" "$CONVERSATIONS_AFTER" "$GROUP_MESSAGES_AFTER" "$MOMENT_MESSAGES_AFTER" "$PRIVATE_CREATE" "$PRIVATE_MESSAGES_AFTER" "$MOMENT_CREATE" <<'PY'
import json
import sys

(
    world_state_before_path,
    world_advance_after_path,
    conversations_after_path,
    group_messages_after_path,
    moment_messages_after_path,
    private_create_path,
    private_messages_after_path,
    moment_create_path,
) = sys.argv[1:]

world_state_before = json.load(open(world_state_before_path, "r", encoding="utf-8"))
world_advance_after = json.load(open(world_advance_after_path, "r", encoding="utf-8"))
conversations_after = json.load(open(conversations_after_path, "r", encoding="utf-8"))
group_messages_after = json.load(open(group_messages_after_path, "r", encoding="utf-8"))
moment_messages_after = json.load(open(moment_messages_after_path, "r", encoding="utf-8"))
private_create = json.load(open(private_create_path, "r", encoding="utf-8"))
private_messages_after = json.load(open(private_messages_after_path, "r", encoding="utf-8"))
moment_create = json.load(open(moment_create_path, "r", encoding="utf-8"))

conversation_ids = {item["id"] for item in conversations_after}
assert "conv-general" in conversation_ids, "Default group conversation is missing."
assert "conv-moments" in conversation_ids, "Default moment conversation is missing."
assert len(world_state_before["pending_tasks"]) >= 2, "Initial pending tasks are missing."
assert len(world_advance_after["pending_tasks"]) >= 2, "Follow-up tasks were not preserved after advance."
assert any(
    "action_executed" in item or "wrote a new message" in item
    for item in world_advance_after["recent_events"]
), "World advance did not record an autonomous message."
assert group_messages_after, "Autonomous group message is not visible through the conversation API."
assert private_create["conversation_type"] == "private", "Private message endpoint returned the wrong type."
assert len(private_messages_after) == 1, "Private conversation did not store the created message."
assert private_messages_after[0]["target_id"] == "char-001", "Private message target mismatch."
assert moment_create["conversation_id"] == "conv-moments", "Moment API did not use the default moment conversation."
assert any(
    item["sender_id"] == "char-001"
    for item in moment_messages_after
), "Moment conversation did not include the autonomous payload."
PY

log "Docker consistency check completed successfully."
log "Detailed artifacts are available in $TMP_DIR"
