from abc import ABC, abstractmethod

class Validator(ABC):

    @abstractmethod
    def validate(self, data: list[dict], expected_session: str) -> bool:
        pass
