import time

import requests

class RequestFactory:
    def __init__(self) -> None:
        self.base_url = 'https://api.openf1.org/v1'

        self.timeout = (60, 240)

        self.session = requests.Session()

    def get_data(self, endpoint: str, params: dict | None = None) -> list[dict]:
        for attempt in range(3):
            try:
                response = self.session.get(
                    self.base_url + endpoint,
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                
                return response.json()
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError,
            ):
                if attempt == 2:
                    raise

                time.sleep(2 ** attempt)
            except requests.exceptions.HTTPError as e:
                    raise e
