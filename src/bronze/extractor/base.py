import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from requests.exceptions import HTTPError

from bronze.contracts import DataClient, Extractor
from bronze.load.contracts import TableLoader
from bronze.storage.contracts import VolumeStorage


class BaseSessionExtractor(Extractor, ABC):
    MEETINGS_ENDPOINT = "/meetings"
    SESSIONS_ENDPOINT = "/sessions"
    SESSION_ENDPOINTS = (
        "/drivers", "/laps", "/stints", "/pit", "/position", "/race_control",
    )
    CAR_DATA_ENDPOINT = "/car_data"

    def __init__(self, client: DataClient, storage: VolumeStorage,
                 table_loader: TableLoader,
                 endpoints: tuple[str, ...] = SESSION_ENDPOINTS) -> None:
        self.client = client
        self.storage = storage
        self.table_loader = table_loader
        self.endpoint = endpoints

    @property
    @abstractmethod
    def session_type(self) -> str:
        pass

    def extract_sessions(self) -> list[dict]:
        sessions = self.client.get_data(
            self.SESSIONS_ENDPOINT,
            params={"year": time.localtime().tm_year, "session_type": self.session_type},
        )

        now = datetime.now(timezone.utc)
        completed_sessions = []
        for session in sessions:
            if session.get("session_type") != self.session_type:
                continue
            if "sprint" in session.get("session_name", "").lower():
                continue
            if session.get("is_cancelled"):
                continue
            try:
                date_end = datetime.fromisoformat(session["date_end"])
            except (KeyError, TypeError, ValueError):
                continue
            if date_end.tzinfo is None or date_end >= now:
                continue
            completed_sessions.append(session)
        return completed_sessions

    def run_extraction(self) -> None:
        processed_meetings: set[int] = set()

        for session in self.extract_sessions():
            meeting_key = session["meeting_key"]
            session_key = session["session_key"]
            if meeting_key not in processed_meetings:
                meetings = self.client.get_data(
                    self.MEETINGS_ENDPOINT, {"meeting_key": meeting_key}
                )
                if not meetings:
                    raise ValueError(f"Meeting {meeting_key} was not returned by OpenF1.")
                self._save_and_load("meetings", meeting_key, None, meetings)
                processed_meetings.add(meeting_key)

            self._save_and_load("sessions", meeting_key, session_key, [session])
            drivers_numbers: list[int] = []
            for endpoint in self.endpoint:
                data = self.client.get_data(endpoint, {"session_key": session_key})
                if endpoint == "/drivers":
                    drivers_numbers = [driver["driver_number"] for driver in data]
                self._save_and_load(endpoint.strip("/"), meeting_key, session_key, data)

            self.extract_car_data(meeting_key, session_key, drivers_numbers,
                                  session["date_start"], session["date_end"])

    def _save_and_load(self, source: str, meeting_key: int,
                       session_key: int | None, data: list[dict]) -> None:
        if self.storage.exists(source=source, meeting_key=meeting_key,
                               session_key=session_key):
            self._print_existing(source, meeting_key, session_key)
        elif data:
            self.storage.save(source=source, meeting_key=meeting_key,
                              session_key=session_key, data=data)
        else:
            return
        self.table_loader.load(source=source, meeting_key=meeting_key,
                               session_key=session_key)

    def extract_car_data(self, meeting_key: int, session_key: int,
                         drivers_numbers: list[int], date_start: str,
                         date_end: str) -> None:
        session_start = datetime.fromisoformat(date_start)
        session_end = datetime.fromisoformat(date_end)
        if (session_start.tzinfo is None or session_end.tzinfo is None
                or session_start >= session_end):
            raise ValueError("Car data requires a valid timezone-aware session interval.")

        for driver_number in drivers_numbers:
            source = f"car_data_driver={driver_number}"
            if self.storage.exists(source=source, meeting_key=meeting_key,
                                   session_key=session_key):
                self._print_existing(source, meeting_key, session_key)
                self.table_loader.load(source=source, meeting_key=meeting_key,
                                       session_key=session_key)
                continue

            data: list[dict] = []
            inicio = session_start
            while inicio < session_end:
                fim = min(inicio + timedelta(minutes=5), session_end)
                params = {"session_key": session_key, "driver_number": driver_number,
                          "date>=": inicio.isoformat(), "date<": fim.isoformat()}
                try:
                    dados = self.client.get_data(self.CAR_DATA_ENDPOINT, params)
                except HTTPError as error:
                    if error.response is not None and error.response.status_code == 404:
                        inicio = fim
                        continue
                    raise
                data.extend(dados)
                inicio = fim
            self._save_and_load(source, meeting_key, session_key, data)

    @staticmethod
    def _print_existing(source: str, meeting_key: int,
                        session_key: int | None) -> None:
        directory = f"meeting_key={meeting_key}"
        if session_key is not None:
            directory += f"/session_key={session_key}"
        print(f"Data already exists: {directory}/{source}.parquet")
