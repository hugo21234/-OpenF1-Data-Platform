from Request.OpenF1_Client import RequestFactory as rf
import extractor_car_data

endpointDrivers = "/drivers"
get_data_car_data = extractor_car_data.ExtractorCarData()
class ExtractorDriver:
    def __init__(self):
        self.client = rf(endpointDrivers)
    
    def extractDrivers(self) -> list:
        driver_number = []
        response = self.client.get_data(self.client.params, endpointDrivers)
        for i in response:
            number = i['driver_number']
            driver_number.append(number)
            getCarData = get_data_car_data.extractCarData(int(number))
        return response

    
print(ExtractorDriver().extractDrivers())
