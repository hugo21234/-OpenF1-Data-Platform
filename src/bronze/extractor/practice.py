from bronze.extractor.base import BaseSessionExtractor


class RequestPractice(BaseSessionExtractor):
    @property
    def session_type(self) -> str:
        return "Practice"
