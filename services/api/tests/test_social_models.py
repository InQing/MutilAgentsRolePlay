from app.social.models import ConversationType, CreateMessageRequest


def test_create_message_request_trims_content() -> None:
    request = CreateMessageRequest(
        conversation_id="conv-general",
        conversation_type=ConversationType.GROUP,
        sender_id="user-001",
        content="  hello world  ",
    )

    assert request.content == "hello world"
