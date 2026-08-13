from Request.OpenF1_Client import RequestFactory as rf

endpoint_car_data = "/car_data"

class ExtractorCarData:
    def __init__(self):
        self.client = rf(endpoint_car_data)
        
    
    def extractCarData(self, driver_number: int) -> list:
        params = self.client.params.copy()
        params['driver_number'] = driver_number   
        response = self.client.get_data(params, endpoint_car_data)
        print(response)
        return response