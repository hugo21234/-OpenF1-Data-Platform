from abc import ABC, abstractmethod


class VolumeStorage(ABC):
    @abstractmethod
    def exists(self, source: str, session_key: int | None, meeting_key: int) -> bool:
        pass

    @abstractmethod
    def save(self,source: str, session_key: int | None, meeting_key: int,data: list[dict]) -> None:
        pass
