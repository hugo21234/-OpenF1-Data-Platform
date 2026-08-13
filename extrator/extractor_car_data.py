from Request.OpenF1_Client import RequestFactory as rf

endpoint_car_data = "/car_data"

class ExtractorCarData():
    def __init__(self, ):
        self.client = rf(endpoint_car_data)
       
    
    def extractCarData(self, driver_number):
        response = self.client.get_data(self.client.params+driver_number, endpoint_car_data)
        print(response)
        return response