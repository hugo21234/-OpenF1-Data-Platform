from Request.OpenF1_Client import RequestFactory
from bronze.extrator.extractor_session import ExtractorSession

import time

from bronze.ingestion.Ingestion_bronze import ingestion


class extractor:
    def __init__(self, client: RequestFactory) -> None:
        self.client = client
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


    def extractSessions(self) -> list[dict]:
        return ExtractorSession(self.client).extractSessions(self.endpoints["sessions"], params={"year": self.year, "session_name": "Race", "is_cancelled": False})



    def run_extraction(self):
        for session in self.extractSessions():

            session_key = session["session_key"]
            params = {'session_key': session_key}

            for endpoint in list(self.endpoints.values())[1:]:

                client_ingestion = ingestion(
                    source=endpoint.strip('/'),
                    session_key=str(session_key),
                )

                data_exists = client_ingestion.file_exists()

                if endpoint == '/drivers':

                    data = self.client.get_data(endpoint, params)
                    drivers_numbers = [driver['driver_number'] for driver in data]

                    if data_exists:
                        print(f"Data already exists: session_key={session_key}/{endpoint.strip('/')}.parquet")
                        continue
                    

                else:

                    if data_exists:
                        print(f"Data already exists: session_key={session_key}/{endpoint.strip('/')}.parquet")
                        continue

                    data = self.client.get_data(endpoint, params)
                    print(f"Data for endpoint {endpoint}: {data}")

                    time.sleep(2)  # Sleep for 2 seconds between requests to avoid overwhelming the API

                parquet_data = client_ingestion.process_data(data)

                if parquet_data is not None:
                    client_ingestion.save_data(parquet_data)

            self.extractCarData(session_key, drivers_numbers)
            
    def extractCarData(self, session_key: int, drivers_numbers: list[int]):
                endpoint = self.endpoint_car_data["car_data"]
                for driver_number in drivers_numbers:
                            client_ingestion = ingestion(
                                source=f"car_data_driver={driver_number}",
                                session_key=str(session_key),
                            )
                            if client_ingestion.file_exists():
                                print(f"Car data already exists: session={session_key} | driver={driver_number}")
                                continue
                            data = self.client.get_data(endpoint,params={"session_key": session_key, "driver_number": driver_number})
                            print(f"Car data | session={session_key} "f"| driver={driver_number} "f"| registros={len(data)}")
                            parquet_data = client_ingestion.process_data(data)
                            if parquet_data is not None:
                                client_ingestion.save_data(parquet_data)
                            time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API
                            continue



if __name__ == "__main__":
    run = extractor(RequestFactory())
    print(run.run_extraction())
