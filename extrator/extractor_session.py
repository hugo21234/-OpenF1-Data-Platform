from Request.OpenF1_Client import RequestFactory


class ExtractorSession:
    def __init__(self, client: RequestFactory):
        self.client = client

    def extractSessions(self, endpoint: str, params: dict) -> list:
        response = self.client.get_data(endpoint, params)
        return response
