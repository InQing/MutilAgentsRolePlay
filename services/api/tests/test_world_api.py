from fastapi.testclient import TestClient


def test_world_advance_triggers_autonomous_message_and_follow_up_task(
    client: TestClient,
) -> None:
    initial_state = client.get("/api/world/state")
    assert initial_state.status_code == 200
    initial_payload = initial_state.json()
    assert len(initial_payload["pending_tasks"]) == 2

    advanced = client.post("/api/world/advance", params={"seconds": 700})
    assert advanced.status_code == 200
    advanced_payload = advanced.json()

    assert len(advanced_payload["recent_events"]) >= 3
    assert any("action_executed" in item or "wrote a new message" in item for item in advanced_payload["recent_events"])
    assert len(advanced_payload["pending_tasks"]) >= 2

    messages = client.get("/api/social/conversations/conv-general/messages")
    assert messages.status_code == 200
    payload = messages.json()
    assert payload
    assert payload[0]["conversation_id"] == "conv-general"
    assert payload[0]["sender_id"] == "char-001"

