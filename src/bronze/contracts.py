from abc import ABC, abstractmethod


class BronzeFileStorage(ABC):
    @abstractmethod
    def exists(self, source: str, session_key: str) -> bool:
        pass

    @abstractmethod
    def save(
        self,
        source: str,
        session_key: int,
        data: list[dict],
    ) -> None:
        pass


class SaveTable(ABC):


    @abstractmethod
    def save(
        self,
        source: str,
        session_key: int,
        data: list[dict],
    ) -> None:
        pass
