from abc import ABC, abstractmethod



class SaveTable(ABC):


    @abstractmethod
    def save(self,source: str,session_key: str, data: list[dict],) -> dict:
        pass



