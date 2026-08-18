from abc import ABC, abstractmethod


class DataClient(ABC):
    @abstractmethod
    def get_data(
        self, endpoint: str, params: dict | None = None
    ) -> list[dict]:
        """Return records obtained from a data source."""


class Extractor(ABC):
    @abstractmethod
    def run_extraction(self) -> None:
        """Run the extraction workflow."""


class BronzeStorage(ABC):
    @abstractmethod
    def exists(self, source: str, session_key: str) -> bool:
        """Return whether data has already been stored."""

    @abstractmethod
    def save(
        self, source: str, session_key: str, data: list[dict]
    ) -> None:
        """Persist source records in the Bronze layer."""
