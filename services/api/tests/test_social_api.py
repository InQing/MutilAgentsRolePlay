from fastapi.testclient import TestClient


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
