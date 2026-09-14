import time
from urllib.parse import quote

import requests

from bronze.contracts import DataClient


class OpenF1Client(DataClient):
    def __init__(self) -> None:
        self.base_url = 'https://api.openf1.org/v1'

        self.timeout = (60, 240)

        self.session = requests.Session()

    def get_data(self, endpoint: str, params: dict | None = None) -> list[dict]:
        # OpenF1 parses comparison operators directly from the query string.
        # A normal params dict adds an extra '=' (date>==... or date<=...).
        query = None
        if params is not None:
            parts = []
            for key, value in params.items():
                if value is None:
                    continue
                operator = "="
                for candidate in (">=", "<=", ">", "<"):
                    if key.endswith(candidate):
                        key, operator = key[:-len(candidate)], candidate
                        break
                parts.append(
                    f"{quote(key, safe='')}{operator}{quote(str(value), safe='')}"
                )
            query = "&".join(parts)
        for attempt in range(3):
            try:
                response = self.session.get(
                    self.base_url + endpoint,
                    params=query,
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

                time.sleep(3 ** attempt)
            except requests.exceptions.HTTPError as error:
                if response.status_code in {500, 502, 503, 504} and attempt < 2:
                    time.sleep(3 ** (attempt + 1))
                    continue
                raise requests.exceptions.HTTPError(
                    f"{error}\nResposta OpenF1: {response.text[:2000]}",
                    response=response,
                    request=response.request,
                ) from error
