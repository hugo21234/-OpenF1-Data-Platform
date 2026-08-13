from Request.OpenF1_Client import RequestFactory
from extrator.extractor_session import ExtractorSession
import time

endpoints = {
            "sessions": "/sessions",
            "drivers": "/drivers",
            "laps": "/laps",
            "stints": "/stints",
            "pit": "/pit",
            "position": "/position",
            "race_control": "/race_control",
            "car_data": "/car_data"
}

client = RequestFactory()
sessions = ExtractorSession(client).extractSessions(endpoints["sessions"], params={"year": 2025, "session_name": "Race"})


def rodar_main():
    for session in sessions:

        session_key = session["session_key"]
        params = {'session_key': session_key}

        for endpoint in list(endpoints.values())[1:]:

            if endpoint == '/drivers':
                data = client.get_data(endpoint, params)
                drivers_numbers = [driver['driver_number'] for driver in data]

            elif endpoint == '/car_data':

                for driver_number in drivers_numbers:

                    params_car = params.copy()
                    params_car['driver_number'] = driver_number
                    data = client.get_data(endpoint, params_car)

                    print(f"Car data for driver {params_car['driver_number']}: {data}")
                    time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API

            else:
                data = client.get_data(endpoint, params)
                print(f"Data for endpoint {endpoint}: {data}")
                time.sleep(3)  # Sleep for 3 seconds between requests to avoid overwhelming the API

            


print(rodar_main())