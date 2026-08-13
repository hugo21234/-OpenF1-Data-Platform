from Request.OpenF1_Client import RequestFactory
endpoints = {
            "drivers": "/drivers",
            "sessions": "/sessions",
            "laps": "/laps",
            "stints": "/stints",
            "pit": "/pit",
            "position": "/position",
            "race_control": "/race_control",
            "car_data": "/car_data"
            }

client = RequestFactory(endpoints)

for i in endpoints:
    print(client.get_data(client.params, endpoints[i]))
