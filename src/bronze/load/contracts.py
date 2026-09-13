from abc import ABC, abstractmethod


class TableLoader(ABC):
    @abstractmethod
    def exists(self, source: str, meeting_key: int | None, session_key: int | None) -> bool:
        pass

    @abstractmethod
    def load(self, source: str, meeting_key: int | None, session_key: int | None) -> None:
        pass
