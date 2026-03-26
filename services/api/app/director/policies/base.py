from abc import ABC, abstractmethod

from app.director.models import PermissionView


class PermissionPolicy(ABC):
    @abstractmethod
    def describe_view(self) -> PermissionView:
        raise NotImplementedError

