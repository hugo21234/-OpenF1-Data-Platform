from abc import ABC, abstractmethod


class TableLoader(ABC):
    @abstractmethod
    def exists(self, source: str, session_key: int) -> bool:
        pass

    @abstractmethod
    def load(self, source: str, session_key: int) -> None:
        pass
