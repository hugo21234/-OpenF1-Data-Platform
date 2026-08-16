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
                "race_control": "/race_control"
    }
        self.endpoint_car_data = {"car_data": "/car_data"}
        self.now = time.localtime()
        self.year = self.now.tm_year

        self.validar = validar_sessionkey()
    
    def extractSessions(self) -> list[dict]:
        return ExtractorSession(self.client).extractSessions(self.endpoints["sessions"], params={"year": self.year, "session_name": "Race", "is_cancelled": False})



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


                else:
                    data = self.client.get_data(endpoint, params)
                    print(f"Data for endpoint {endpoint}: {data}")
                    time.sleep(2)  # Sleep for 2 seconds between requests to avoid overwhelming the API

                #ingestion = self.client_ingestion.save_data(data, destination=f"data/{endpoint.strip('/')}_{session_key}.json")

            extractor.extractCarData(self, session_key, drivers_numbers)
            
    def extractCarData(self, session_key: int, drivers_numbers: list[int]):
                endpoint = self.endpoint_car_data["car_data"]
                for driver_number in drivers_numbers:
                            data = self.client.get_data(endpoint,params={"session_key": session_key, "driver_number": driver_number})
                            print(f"Car data | session={session_key} "f"| driver={driver_number} "f"| registros={len(data)}")
                            #ingestion = self.client_ingestion.save_data(data, destination=f"data/{endpoint.strip('/')}_{session_key}.json")
                            time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API
                            continue


run = extractor(RequestFactory())
print(run.run_extraction())
