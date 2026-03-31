from fastapi.testclient import TestClient

from app.bootstrap import get_runtime_registry
from app.world.events import RuntimeTask, WorldEvent, WorldEventKind


def _schedule_direct_private_prompt(*, source_id: str, target_id: str) -> None:
    registry = get_runtime_registry()
    current_time = registry.world_runtime.clock.snapshot().now
    registry.world_runtime.record_event(
        WorldEvent(
            world_id=registry.world_runtime.world_id,
            kind=WorldEventKind.DIRECTOR_NOTE,
            summary=f"{source_id} left a direct prompt for {target_id}.",
            created_at=current_time,
            payload={
                "character_id": source_id,
                "target_character_id": target_id,
            },
        )
    )
    registry.world_runtime.scheduler.schedule(
        RuntimeTask(
            world_id=registry.world_runtime.world_id,
            task_type="character_plan_tick",
            run_at=current_time,
            payload={"character_id": target_id, "intent": "reply_to_direct_prompt"},
            priority=1,
        )
    )


def test_social_endpoints_list_default_conversations_and_create_messages(
    client: TestClient,
) -> None:
    conversations = client.get("/api/social/conversations")
    assert conversations.status_code == 200
    conversation_payload = conversations.json()
    ids = {item["id"] for item in conversation_payload}
    assert "conv-general" in ids
    assert "conv-moments" in ids

    response = client.post(
        "/api/social/conversations/conv-general/messages",
        json={
            "conversation_id": "conv-general",
            "conversation_type": "group",
            "sender_id": "user-001",
            "content": "测试一条用户消息"
        },
    )
    assert response.status_code == 200
    created_payload = response.json()
    assert created_payload["conversation_id"] == "conv-general"
    assert created_payload["sender_id"] == "user-001"

    listed = client.get("/api/social/conversations/conv-general/messages")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert len(listed_payload) == 1
    assert listed_payload[0]["content"] == "测试一条用户消息"


def test_social_private_message_api_creates_and_reuses_private_conversation(
    client: TestClient,
) -> None:
    first = client.post(
        "/api/social/private-messages",
        json={
            "sender_id": "user-001",
            "target_id": "char-001",
            "content": "这是一条私聊消息"
        },
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["conversation_type"] == "private"
    assert first_payload["target_id"] == "char-001"

    second = client.post(
        "/api/social/private-messages",
        json={
            "sender_id": "char-001",
            "target_id": "user-001",
            "content": "这是第二条私聊回复"
        },
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["conversation_id"] == first_payload["conversation_id"]

    conversations = client.get("/api/social/conversations")
    assert conversations.status_code == 200
    private_conversations = [
        item
        for item in conversations.json()
        if item["conversation_type"] == "private"
    ]
    assert len(private_conversations) == 1
    assert sorted(private_conversations[0]["participant_ids"]) == ["char-001", "user-001"]

    listed = client.get(f"/api/social/conversations/{first_payload['conversation_id']}/messages")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert len(listed_payload) == 2


def test_social_moment_api_writes_to_default_moment_conversation(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/social/moments",
        json={
            "sender_id": "char-001",
            "content": "今天先发一条朋友圈试试",
            "mentions": ["char-002"]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] == "conv-moments"
    assert payload["conversation_type"] == "moment"
    assert payload["mentions"] == ["char-002"]

    listed = client.get("/api/social/conversations/conv-moments/messages")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert len(listed_payload) == 1
    assert listed_payload[0]["content"] == "今天先发一条朋友圈试试"


def test_autonomous_group_and_moment_messages_are_visible_via_social_api(
    client: TestClient,
) -> None:
    first = client.post("/api/world/advance", params={"seconds": 700})
    assert first.status_code == 200

    general_messages = client.get("/api/social/conversations/conv-general/messages")
    assert general_messages.status_code == 200
    general_payload = general_messages.json()
    assert len(general_payload) == 1
    assert general_payload[0]["conversation_id"] == "conv-general"
    assert general_payload[0]["sender_id"] == "char-001"

    second = client.post("/api/world/advance", params={"seconds": 720})
    assert second.status_code == 200

    moment_messages = client.get("/api/social/conversations/conv-moments/messages")
    assert moment_messages.status_code == 200
    moment_payload = moment_messages.json()
    assert len(moment_payload) == 1
    assert moment_payload[0]["conversation_id"] == "conv-moments"
    assert moment_payload[0]["sender_id"] == "char-001"


def test_autonomous_private_messages_are_visible_and_reuse_the_same_conversation(
    client: TestClient,
) -> None:
    _schedule_direct_private_prompt(source_id="char-002", target_id="char-001")
    first = client.post("/api/world/advance", params={"seconds": 0})
    assert first.status_code == 200

    _schedule_direct_private_prompt(source_id="char-002", target_id="char-001")
    second = client.post("/api/world/advance", params={"seconds": 0})
    assert second.status_code == 200

    conversations = client.get("/api/social/conversations")
    assert conversations.status_code == 200
    private_conversations = [
        item
        for item in conversations.json()
        if item["conversation_type"] == "private"
    ]

    assert len(private_conversations) == 1
    private_conversation_id = private_conversations[0]["id"]
    assert sorted(private_conversations[0]["participant_ids"]) == ["char-001", "char-002"]

    listed = client.get(f"/api/social/conversations/{private_conversation_id}/messages")
    assert listed.status_code == 200
    listed_payload = listed.json()

    assert len(listed_payload) == 2
    assert all(item["conversation_id"] == private_conversation_id for item in listed_payload)
    assert all(item["sender_id"] == "char-001" for item in listed_payload)
    assert all(item["target_id"] == "char-002" for item in listed_payload)
    assert listed_payload[0]["created_at"] <= listed_payload[1]["created_at"]
