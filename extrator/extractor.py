from Request.OpenF1_Client import RequestFactory
from extrator.extractor_session import ExtractorSession

import time

#from Ingestion import ingestion


from validar.validar_sessionkey import validar_sessionkey

class extractor:
    def __init__(self, client: RequestFactory) -> None:
        self.client = client
        #self.client_ingestion = client_ingestion
        self.endpoints = {
                "sessions": "/sessions",
                "drivers": "/drivers",
                "laps": "/laps",
                "stints": "/stints",
                "pit": "/pit",
                "position": "/position",
                "race_control": "/race_control",
                "car_data": "/car_data"
    }
        self.now = time.localtime()
        self.year = self.now.tm_year

        self.validar = validar_sessionkey()
    
    def extractSessions(self) -> list[dict]:
        return ExtractorSession(self.client).extractSessions(self.endpoints["sessions"], params={"year": self.year, "session_name": "Race"})



    def run_extraction(self):
        for session in self.extractSessions():

            session_key = session["session_key"]
            params = {'session_key': session_key}
            is_exist, response = self.validar.validar_sessionkey(session_key)


            if  is_exist:
                print(f"Session key exist on volume: {session_key}")
                continue

            for endpoint in list(self.endpoints.values())[1:]:

                if endpoint == '/drivers':
                    data = self.client.get_data(endpoint, params)
                    drivers_numbers = [driver['driver_number'] for driver in data]

                elif endpoint == '/car_data':

                    for driver_number in drivers_numbers:

                        params_car = params.copy()
                        params_car['driver_number'] = driver_number
                        data = self.client.get_data(endpoint, params_car)
                        print(f"Car data for driver {params_car['driver_number']}: {data}")
                        #ingestion = self.client_ingestion.save_data(data, destination=f"data/{endpoint.strip('/')}_{session_key}.json")

                        print(f"Car data for driver {params_car['driver_number']}: {data}")
                        time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API
                    continue

                else:
                    data = self.client.get_data(endpoint, params)
                    print(f"Data for endpoint {endpoint}: {data}")
                    time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API

                #ingestion = self.client_ingestion.save_data(data, destination=f"data/{endpoint.strip('/')}_{session_key}.json")
            


run = extractor(RequestFactory())
print(run.run_extraction())
