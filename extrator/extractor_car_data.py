from Request.OpenF1_Client import RequestFactory

class ExtractorCarData:
    def __init__(self, client: RequestFactory):
        self.client = client
        
    
    def extractCarData(self, endpoint: str, driver_number: int, params: dict | None = None) -> list:
        request_params = params.copy() if params else {}

        request_params["driver_number"] = driver_number

        response = self.client.get_data(endpoint, request_params)

        return response
