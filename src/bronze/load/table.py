import os

from dotenv import load_dotenv

from bronze.load.contracts import TableLoader
from bronze.verification.loadVerifier import LoadVerifier


class DatabricksTableLoader(TableLoader):
    TABLE_SCHEMA = "f1_plataform_data.bronze"
    FILE_TO_TABLE_MAP = {"pit": "pits"}
    SOURCES = {
        "drivers",
        "laps",
        "stints",
        "pit",
        "position",
        "race_control",
        "car_data",
        "meetings",
        "sessions"
    }

    def __init__(self) -> None:
        load_dotenv()

        self.path_volume = os.getenv("path_volume_databricks")
        self.verifier = LoadVerifier()

        if not self.path_volume:
            raise ValueError(
                "One or more required environment variables are missing."
            )


    def exists(self, source: str, meeting_key: int | None,
               session_key: int | None) -> bool:
        table_name, driver_number = self._source_data(source)
        if meeting_key is None:
            raise ValueError("meeting_key cannot be None.")
        if source != "meetings" and session_key is None:
            raise ValueError("session_key is required for session data.")
        return self.verifier.exists(table_name, driver_number, meeting_key, session_key)

    def load(self, source: str, meeting_key: int | None,
             session_key: int | None) -> None:
        table_name, _ = self._source_data(source)
        if self.exists(source, meeting_key, session_key):
            return
        directory = f"{self.path_volume.rstrip('/')}/meeting_key={meeting_key}"
        if session_key is not None:
            directory += f"/session_key={session_key}"
        file_path = f"{directory}/{source}.parquet"

        if source == "laps":
            statement = f"""
                COPY INTO {table_name}
                FROM (
                    SELECT
                        meeting_key,
                        session_key,
                        driver_number,
                        lap_number,
                        date_start,
                        duration_sector_1,
                        duration_sector_2,
                        duration_sector_3,
                        CAST(i1_speed AS DOUBLE) AS i1_speed,
                        CAST(i2_speed AS DOUBLE) AS i2_speed,
                        is_pit_out_lap,
                        lap_duration,
                        segments_sector_1,
                        segments_sector_2,
                        segments_sector_3,
                        CAST(st_speed AS DOUBLE) AS st_speed
                    FROM '{file_path}'
                )
                FILEFORMAT = PARQUET
            """
        else:
            statement = f"""
                COPY INTO {table_name}
                FROM '{file_path}'
                FILEFORMAT = PARQUET
            """
        self.verifier.execute_statement(statement)

        print(
            f"Data loaded to table={table_name} "
            f"| meeting_key={meeting_key} | session_key={session_key} | source={source}"
        )

    def _source_data(self, source: str) -> tuple[str, int | None]:
        if source.startswith("car_data_driver="):
            driver_number_text = source.removeprefix("car_data_driver=")

            if not driver_number_text.isdigit():
                raise ValueError(f"Invalid car data source: {source}")

            return f"{self.TABLE_SCHEMA}.car_data", int(driver_number_text)

        if source not in self.SOURCES:
            raise ValueError(f"Invalid source: {source}")

        table_name = self.FILE_TO_TABLE_MAP.get(source, source)
        return f"{self.TABLE_SCHEMA}.{table_name}", None
