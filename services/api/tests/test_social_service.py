import asyncio
from pathlib import Path

from app.infra.db.initializer import initialize_database
from app.infra.db.session import DatabaseManager
from app.social.service import SocialService


def test_social_service_creates_private_conversation_and_reuses_it(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'social-private.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        service = SocialService(database, world_id="local-prototype")
        await service.ensure_defaults()

        first = await service.post_private_message(
            sender_id="char-001",
            target_id="char-002",
            content="第一条私聊",
        )
        second = await service.post_private_message(
            sender_id="char-002",
            target_id="char-001",
            content="第二条私聊",
        )

        conversations = await service.list_conversations()
        private_conversations = [
            item for item in conversations if item.conversation_type == "private"
        ]
        assert len(private_conversations) == 1
        assert sorted(private_conversations[0].participant_ids) == ["char-001", "char-002"]
        assert first.conversation_id == second.conversation_id

        messages = await service.list_messages(conversation_id=first.conversation_id)
        assert len(messages) == 2

        await database.engine.dispose()

    asyncio.run(scenario())


def test_social_service_posts_moment_to_default_moment_conversation(
    tmp_path: Path,
) -> None:
    database = DatabaseManager(f"sqlite+aiosqlite:///{tmp_path / 'social-moment.db'}")

    async def scenario() -> None:
        await initialize_database(database)
        service = SocialService(database, world_id="local-prototype")
        await service.ensure_defaults()

        message = await service.post_moment(
            sender_id="char-001",
            content="今天的节奏很满，但我想先记录一下。",
        )

        assert message.conversation_id == "conv-moments"

        messages = await service.list_messages(conversation_id="conv-moments")
        assert len(messages) == 1
        assert messages[0].content == "今天的节奏很满，但我想先记录一下。"

        await database.engine.dispose()

    asyncio.run(scenario())
