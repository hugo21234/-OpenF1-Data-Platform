import time

from bronze.contracts import BronzeStorage, DataClient, Extractor


class BronzeExtractor(Extractor):
    ENDPOINTS = (
        "/drivers",
        "/laps",
        "/stints",
        "/pit",
        "/position",
        "/race_control",
    )
    SESSIONS_ENDPOINT = "/sessions"
    CAR_DATA_ENDPOINT = "/car_data"

    def __init__(self, client: DataClient, storage: BronzeStorage) -> None:
        self.client = client
        self.storage = storage

    def extract_sessions(self) -> list[dict]:
        return self.client.get_data(
            self.SESSIONS_ENDPOINT,
            params={
                "year": time.localtime().tm_year,
                "session_name": "Race",
                "is_cancelled": False,
            },
        )

    def run_extraction(self) -> None:
        for session in self.extract_sessions():
            session_key = session["session_key"]
            session_key_text = str(session_key)
            drivers_numbers: list[int] = []

            for endpoint in self.ENDPOINTS:
                source = endpoint.strip("/")

                if endpoint == "/drivers":
                    data = self.client.get_data(
                        endpoint,
                        {"session_key": session_key},
                    )
                    drivers_numbers = [
                        driver["driver_number"] for driver in data
                    ]
                    if self.storage.exists(source, session_key_text):
                        self._print_existing(source, session_key_text)
                        continue
                else:
                    if self.storage.exists(source, session_key_text):
                        self._print_existing(source, session_key_text)
                        continue

                    data = self.client.get_data(
                        endpoint,
                        {"session_key": session_key},
                    )
                    print(f"Data for endpoint {endpoint}: {data}")
                    time.sleep(2)

                self.storage.save(source, session_key, data)

            self.extract_car_data(session_key, drivers_numbers)

    def extract_car_data(
        self,
        session_key: int,
        drivers_numbers: list[int],
    ) -> None:
        session_key_text = str(session_key)

        for driver_number in drivers_numbers:
            source = f"car_data_driver={driver_number}"

            if self.storage.exists(source, session_key_text):
                print(
                    "Car data already exists: "
                    f"session={session_key} | driver={driver_number}"
                )
                continue

            data = self.client.get_data(
                self.CAR_DATA_ENDPOINT,
                {
                    "session_key": session_key,
                    "driver_number": driver_number,
                },
            )
            print(
                f"Car data | session={session_key} "
                f"| driver={driver_number} | registros={len(data)}"
            )
            self.storage.save(source, session_key, data)
            time.sleep(3)

    @staticmethod
    def _print_existing(source: str, session_key: str) -> None:
        print(
            f"Data already exists: session_key={session_key}/{source}.parquet"
        )
