import time
from collections import deque
from urllib.parse import quote

import requests

from bronze.contracts import DataClient


class OpenF1Client(DataClient):
    def __init__(self) -> None:
        self.base_url = 'https://api.openf1.org/v1'

        self.timeout = (60, 240)

        self.session = requests.Session()
        
        # Rate limiting: OpenF1 free tier allows 30 req/min and 3 req/sec
        # Using 30 req/min as the limiting factor (2 seconds between requests)
        self.min_request_interval = 2.1  # seconds between requests (with safety margin)
        self.last_request_time = 0.0
        
        # Track requests in the last minute for additional safety
        self.request_times = deque(maxlen=30)

    def _respect_rate_limit(self) -> None:
        """Ensure we respect OpenF1 rate limits: 30 req/min and 3 req/sec."""
        current_time = time.time()
        
        # Check per-second limit (3 req/sec)
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
            current_time = time.time()
        
        # Check per-minute limit (30 req/min)
        # Remove requests older than 60 seconds
        cutoff_time = current_time - 60
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()
        
        # If we've made 30 requests in the last minute, wait
        if len(self.request_times) >= 30:
            oldest_request = self.request_times[0]
            wait_time = 60 - (current_time - oldest_request)
            if wait_time > 0:
                print(f"Rate limit: aguardando {wait_time:.1f}s para respeitar limite de 30 req/min...")
                time.sleep(wait_time + 0.5)  # Add small buffer
                current_time = time.time()
        
        # Record this request
        self.last_request_time = current_time
        self.request_times.append(current_time)
    
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
            # Respect rate limits before making request
            self._respect_rate_limit()
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
                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < 2:
                        wait_time = 30 * (attempt + 1)  # 30s, then 60s
                        print(f"Rate limit atingido. Aguardando {wait_time}s antes de tentar novamente...")
                        time.sleep(wait_time)
                        continue
                # Handle server errors with retry
                if response.status_code in {500, 502, 503, 504} and attempt < 2:
                    time.sleep(3 ** (attempt + 1))
                    continue
                raise requests.exceptions.HTTPError(
                    f"{error}\nResposta OpenF1: {response.text[:2000]}",
                    response=response,
                    request=response.request,
                ) from error
