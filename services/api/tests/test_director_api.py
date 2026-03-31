from datetime import datetime

from fastapi.testclient import TestClient

from app.bootstrap import get_runtime_registry


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def test_director_control_api_can_pause_resume_and_change_speed(
    client: TestClient,
) -> None:
    initial_panel = client.get("/api/director/panel")
    assert initial_panel.status_code == 200
    initial_panel_payload = initial_panel.json()
    initial_speed = initial_panel_payload["speed_multiplier"]
    initial_time = _parse_iso_datetime(initial_panel_payload["current_time"])

    pause_response = client.post("/api/director/pause")
    assert pause_response.status_code == 200
    paused_panel = pause_response.json()
    assert paused_panel["paused"] is True
    assert any(
        "paused the world runtime" in item["summary"]
        for item in paused_panel["recent_logs"]
    )

    paused_advance = client.post("/api/world/advance", params={"seconds": 10})
    assert paused_advance.status_code == 200
    paused_state = paused_advance.json()
    assert _parse_iso_datetime(paused_state["clock"]["now"]) == initial_time
    assert paused_state["clock"]["paused"] is True

    speed_response = client.post(
        "/api/director/speed",
        json={"speed_multiplier": initial_speed * 2},
    )
    assert speed_response.status_code == 200
    accelerated_panel = speed_response.json()
    assert accelerated_panel["speed_multiplier"] == initial_speed * 2
    assert accelerated_panel["paused"] is True

    resume_response = client.post("/api/director/resume")
    assert resume_response.status_code == 200
    resumed_panel = resume_response.json()
    assert resumed_panel["paused"] is False
    assert resumed_panel["speed_multiplier"] == initial_speed * 2

    resumed_advance = client.post("/api/world/advance", params={"seconds": 10})
    assert resumed_advance.status_code == 200
    resumed_state = resumed_advance.json()
    resumed_time = _parse_iso_datetime(resumed_state["clock"]["now"])
    assert resumed_time > initial_time
    assert resumed_state["clock"]["speed_multiplier"] == initial_speed * 2

    refreshed_panel = client.get("/api/director/panel")
    assert refreshed_panel.status_code == 200
    recent_logs = refreshed_panel.json()["recent_logs"]
    assert any("paused the world runtime" in item["summary"] for item in recent_logs)
    assert any("resumed the world runtime" in item["summary"] for item in recent_logs)
    assert any("set world speed" in item["summary"] for item in recent_logs)


def test_director_panel_returns_moment_interactions_after_visibility_delay(
    client: TestClient,
) -> None:
    created_moment = client.post(
        "/api/social/moments",
        json={
            "sender_id": "char-001",
            "content": "导演面板互动聚合测试",
        },
    )
    assert created_moment.status_code == 200
    moment_payload = created_moment.json()

    comment = client.post(
        f"/api/social/moments/{moment_payload['id']}/comments",
        json={
            "sender_id": "char-002",
            "content": "这里先补一条评论",
        },
    )
    assert comment.status_code == 200

    like = client.post(
        f"/api/social/moments/{moment_payload['id']}/likes",
        json={"sender_id": "char-002"},
    )
    assert like.status_code == 200

    hidden_panel = client.get("/api/director/panel")
    assert hidden_panel.status_code == 200
    hidden_payload = hidden_panel.json()
    assert hidden_payload["moment_interactions"] == []
    assert all(
        item["kind"] != "moment_interaction_recorded"
        for item in hidden_payload["recent_logs"]
    )

    registry = get_runtime_registry()
    registry.world_runtime.clock.tick(301)

    visible_panel = client.get("/api/director/panel")
    assert visible_panel.status_code == 200
    visible_payload = visible_panel.json()
    moment_interactions = visible_payload["moment_interactions"]
    assert len(moment_interactions) == 2
    assert {item["interaction_type"] for item in moment_interactions} == {"comment", "like"}
    assert all(item["target_moment_id"] == moment_payload["id"] for item in moment_interactions)
    assert all(item["target_moment_preview"] for item in moment_interactions)
    assert any(item["content"] == "这里先补一条评论" for item in moment_interactions)
    assert any(item["actor_display_name"] == "许遥" for item in moment_interactions)
    assert any(
        item["kind"] == "moment_interaction_recorded"
        for item in visible_payload["recent_logs"]
    )


def test_director_inject_api_records_note_and_can_schedule_targeted_follow_up(
    client: TestClient,
) -> None:
    initial_panel = client.get("/api/director/panel")
    assert initial_panel.status_code == 200
    initial_payload = initial_panel.json()

    inject_response = client.post(
        "/api/director/inject",
        json={
            "summary": "请马上给我一个简短回复",
            "target_character_id": "char-001",
            "task_intent": "reply_to_direct_prompt",
        },
    )
    assert inject_response.status_code == 200
    injected_panel = inject_response.json()
    assert injected_panel["pending_task_count"] == initial_payload["pending_task_count"] + 1
    assert any(
        "Director injected a targeted note" in item["summary"]
        for item in injected_panel["recent_logs"]
    )

    advance_response = client.post("/api/world/advance", params={"seconds": 1})
    assert advance_response.status_code == 200

    conversations = client.get("/api/social/conversations")
    assert conversations.status_code == 200
    private_conversation = next(
        item
        for item in conversations.json()
        if item["conversation_type"] == "private"
    )

    messages = client.get(
        f"/api/social/conversations/{private_conversation['id']}/messages"
    )
    assert messages.status_code == 200
    message_payload = messages.json()
    assert len(message_payload) == 1
    assert message_payload[0]["sender_id"] == "char-001"
    assert message_payload[0]["target_id"] == "user-001"
