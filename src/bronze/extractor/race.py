from bronze.extractor.base import BaseSessionExtractor


class RequestRace(BaseSessionExtractor):
    @property
    def session_type(self) -> str:
        return "Race"
