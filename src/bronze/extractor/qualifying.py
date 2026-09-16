from bronze.extractor.base import BaseSessionExtractor


class RequestQualifying(BaseSessionExtractor):
    @property
    def session_type(self) -> str:
        return "Qualifying"
