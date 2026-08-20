from abc import ABC, abstractmethod


class DataClient(ABC):
    @abstractmethod
    def get_data(
        self,
        endpoint: str,
        params: dict | None = None,
    ) -> list[dict]:
        pass


class Extractor(ABC):
    @abstractmethod
    def run_extraction(self) -> None:
        pass
