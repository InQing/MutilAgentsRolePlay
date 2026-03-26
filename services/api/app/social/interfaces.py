from abc import ABC, abstractmethod

from app.social.models import MessageRecord


class AutonomousSocialGateway(ABC):
    @abstractmethod
    async def post_group_message(self, *, sender_id: str, content: str) -> MessageRecord:
        raise NotImplementedError

    @abstractmethod
    async def post_private_message(
        self,
        *,
        sender_id: str,
        target_id: str,
        content: str,
    ) -> MessageRecord:
        raise NotImplementedError

    @abstractmethod
    async def post_moment(self, *, sender_id: str, content: str) -> MessageRecord:
        raise NotImplementedError
