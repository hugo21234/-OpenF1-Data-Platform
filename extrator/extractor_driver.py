from Request.OpenF1_Client import RequestFactory as rf
import extractor_car_data
endpointDrivers = "/drivers"
class ExtractorDriver:
    def __init__(self):
        self.client = rf(endpointDrivers)
    
    def extractDrivers(self):
        driver_number = []
        response = self.client.get_data(self.client.params, endpointDrivers)
        for i in response['driver_number']:
            number = i['driver_number']
            driver_number.append(number)
            getCarData = extractor_car_data.ExtractorCarData(number)
        return response

