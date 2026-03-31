from fastapi.testclient import TestClient

from app.bootstrap import get_runtime_registry


def _build_character_payload(*, display_name: str, current_plan_summary: str) -> dict:
    return {
        "display_name": display_name,
        "profile": {
            "identity_and_background": f"{display_name} 的身份背景设定。",
            "personality": f"{display_name} 的性格设定。",
            "speaking_style": f"{display_name} 的说话风格设定。",
            "appearance_and_presence": f"{display_name} 的外在气质设定。",
            "additional_notes": f"{display_name} 的补充备注。"
        },
        "current_plan_summary": current_plan_summary,
        "emotion_state": "focused",
        "social_drive": 0.66,
        "interrupt_threshold": 0.41
    }


def test_character_api_lists_and_updates_existing_character(
    client: TestClient,
) -> None:
    listed = client.get("/api/characters")
    assert listed.status_code == 200
    listed_payload = listed.json()
    assert len(listed_payload) == 2
    assert "profile" in listed_payload[0]

    response = client.put(
        "/api/characters/char-001",
        json=_build_character_payload(
            display_name="林澈-角色页更新",
            current_plan_summary="整理角色管理系统的第一轮配置",
        ),
    )
    assert response.status_code == 200
    updated_payload = response.json()
    assert updated_payload["display_name"] == "林澈-角色页更新"
    assert updated_payload["profile"]["speaking_style"] == "林澈-角色页更新 的说话风格设定。"

    world_state = client.get("/api/world/state")
    assert world_state.status_code == 200
    active_characters = world_state.json()["active_characters"]
    assert any(item["display_name"] == "林澈-角色页更新" for item in active_characters)

    registry = get_runtime_registry()
    registry.world_runtime.clock.tick(301)
    panel = client.get("/api/director/panel")
    assert panel.status_code == 200
    panel_characters = panel.json()["characters"]
    updated_character = next(item for item in panel_characters if item["id"] == "char-001")
    assert updated_character["display_name"] == "林澈-角色页更新"
    assert updated_character["current_plan_summary"] == "整理角色管理系统的第一轮配置"

    missing = client.put(
        "/api/characters/not-found",
        json=_build_character_payload(
            display_name="不存在角色",
            current_plan_summary="不会成功",
        ),
    )
    assert missing.status_code == 404


def test_character_api_can_create_and_delete_character_without_breaking_world_runtime(
    client: TestClient,
) -> None:
    created = client.post(
        "/api/characters",
        json=_build_character_payload(
            display_name="苏见",
            current_plan_summary="先加入世界并熟悉当前节奏",
        ),
    )
    assert created.status_code == 200
    created_payload = created.json()
    created_id = created_payload["id"]

    world_state = client.get("/api/world/state")
    assert world_state.status_code == 200
    active_characters = world_state.json()["active_characters"]
    assert any(item["id"] == created_id for item in active_characters)

    create_message = client.post(
        "/api/social/conversations/conv-general/messages",
        json={
            "conversation_id": "conv-general",
            "conversation_type": "group",
            "sender_id": created_id,
            "content": "删除角色后这条历史消息仍应保留。"
        },
    )
    assert create_message.status_code == 200

    deleted = client.delete(f"/api/characters/{created_id}")
    assert deleted.status_code == 200
    assert deleted.json()["character_id"] == created_id

    refreshed_state = client.get("/api/world/state")
    assert refreshed_state.status_code == 200
    refreshed_characters = refreshed_state.json()["active_characters"]
    assert all(item["id"] != created_id for item in refreshed_characters)
    assert all(created_id not in task for task in refreshed_state.json()["pending_tasks"])

    listed_messages = client.get("/api/social/conversations/conv-general/messages")
    assert listed_messages.status_code == 200
    assert any(
        item["sender_id"] == created_id
        for item in listed_messages.json()
    )

    advance = client.post("/api/world/advance", params={"seconds": 60})
    assert advance.status_code == 200

    missing = client.delete(f"/api/characters/{created_id}")
    assert missing.status_code == 404
