from fastapi.testclient import TestClient


def test_world_restart_preserves_messages_and_pending_tasks(client_factory) -> None:
    with client_factory(reset_db=True) as first_client:
        first_advance = first_client.post("/api/world/advance", params={"seconds": 700})
        assert first_advance.status_code == 200
        first_state = first_advance.json()

        first_messages = first_client.get("/api/social/conversations/conv-general/messages")
        assert first_messages.status_code == 200
        first_messages_payload = first_messages.json()
        assert first_messages_payload

        pending_before_restart = first_state["pending_tasks"]
        recent_before_restart = first_state["recent_events"]

    with client_factory(reset_db=False) as second_client:
        restored_state_response = second_client.get("/api/world/state")
        assert restored_state_response.status_code == 200
        restored_state = restored_state_response.json()

        restored_messages = second_client.get("/api/social/conversations/conv-general/messages")
        assert restored_messages.status_code == 200
        restored_messages_payload = restored_messages.json()

        assert restored_messages_payload == first_messages_payload
        assert restored_state["pending_tasks"] == pending_before_restart
        assert restored_state["recent_events"] == recent_before_restart


def test_multiple_advances_keep_autonomous_loop_stable(client: TestClient) -> None:
    first = client.post("/api/world/advance", params={"seconds": 700})
    assert first.status_code == 200

    second = client.post("/api/world/advance", params={"seconds": 800})
    assert second.status_code == 200

    third = client.post("/api/world/advance", params={"seconds": 900})
    assert third.status_code == 200
    final_state = third.json()

    general_messages = client.get("/api/social/conversations/conv-general/messages")
    assert general_messages.status_code == 200
    general_payload = general_messages.json()

    moment_messages = client.get("/api/social/conversations/conv-moments/messages")
    assert moment_messages.status_code == 200
    moment_payload = moment_messages.json()

    assert len(general_payload) >= 1
    assert len(moment_payload) >= 1
    assert len(final_state["pending_tasks"]) >= 1
    assert any("action_executed" in item or "wrote a new message" in item for item in final_state["recent_events"])
    assert any("action_skipped" in item or "skipped acting" in item for item in final_state["recent_events"])
