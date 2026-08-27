import os

import pandas as pd
import requests
from dotenv import load_dotenv

from bronze.storage.contracts import VolumeStorage
from bronze.validator.validator import REQUIRED_FIELDS, Validator


class DatabricksVolumeStorage(VolumeStorage):
    COLUMN_TYPES = {
        "car_data": {
            "brake": "INT",
            "date": "STRING",
            "driver_number": "INT",
            "drs": "INT",
            "meeting_key": "INT",
            "session_key": "INT",
            "n_gear": "INT",
            "rpm": "INT",
            "speed": "INT",
            "throttle": "INT",
        },
        "drivers": {
            "broadcast_name": "STRING",
            "country_code": "INT",
            "driver_number": "BIGINT",
            "first_name": "STRING",
            "last_name": "STRING",
            "headshot_url": "STRING",
            "full_name": "STRING",
            "meeting_key": "INT",
            "session_key": "INT",
            "name_acronym": "STRING",
            "team_colour": "STRING",
            "team_name": "STRING",
        },
        "laps": {
            "date_start": "STRING",
            "driver_number": "BIGINT",
            "duration_sector_1": "DOUBLE",
            "duration_sector_2": "DOUBLE",
            "duration_sector_3": "DOUBLE",
            "i1_speed": "DOUBLE",
            "i2_speed": "DOUBLE",
            "is_pit_out_lap": "BOOLEAN",
            "lap_duration": "DOUBLE",
            "lap_number": "BIGINT",
            "meeting_key": "INT",
            "segments_sector_1": "ARRAY<BIGINT>",
            "segments_sector_2": "ARRAY<BIGINT>",
            "segments_sector_3": "ARRAY<BIGINT>",
            "session_key": "INT",
            "st_speed": "DOUBLE",
        },
        "stints": {
            "compound": "STRING",
            "driver_number": "BIGINT",
            "lap_end": "BIGINT",
            "lap_start": "BIGINT",
            "meeting_key": "INT",
            "session_key": "INT",
            "stint_number": "BIGINT",
            "tyre_age_at_start": "BIGINT",
        },
        "pit": {
            "date": "STRING",
            "driver_number": "BIGINT",
            "lane_duration": "DOUBLE",
            "lap_number": "BIGINT",
            "meeting_key": "INT",
            "session_key": "INT",
            "pit_duration": "DOUBLE",
            "stop_duration": "DOUBLE",
        },
        "position": {
            "date": "STRING",
            "driver_number": "BIGINT",
            "meeting_key": "INT",
            "position": "BIGINT",
            "session_key": "INT",
        },
        "race_control": {
            "category": "STRING",
            "date": "STRING",
            "driver_number": "DOUBLE",
            "lap_number": "BIGINT",
            "flag": "STRING",
            "meeting_key": "INT",
            "message": "STRING",
            "session_key": "INT",
            "qualifying_phase": "INT",
            "scope": "STRING",
            "sector": "DOUBLE",
        },
    }

    def __init__(self) -> None:
        load_dotenv()

        self.files_prefix = os.getenv("prefix_databricks_files")
        self.directories_prefix = os.getenv("prefix_databricks")
        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.path_volume = os.getenv("path_volume_databricks")
        

        self.validator = Validator()

        if not all(
            [
                self.files_prefix,
                self.directories_prefix,
                self.databricks_access_token,
                self.databricks_host,
                self.path_volume,
            ]
        ):
            raise ValueError(
                "One or more required environment variables are missing."
            )

    def exists(self, source: str, session_key: str) -> bool:
        _, file_url = self._urls(source, session_key)
        response = requests.head(
            file_url,
            headers=self._authorization_headers(),
            timeout=(60, 240),
        )

        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False

        response.raise_for_status()
        return False

    def save(self,source: str,session_key: int,data: list[dict] ) -> None:
        validator_source = (
            "car_data" if source.startswith("car_data_driver=") else source
        )
        if validator_source not in REQUIRED_FIELDS:
            print(f"No validator configured for source: {source}")
            return

        validation_passed, invalid_records = self.validator.validate(
            data,
            session_key,
            validator_source,
        )

        if not validation_passed:
            print("Validation failed. Invalid data found.")
            print(f"Validation context: {invalid_records}")
            raise ValueError("Data validation failed.")

        dataframe = self._apply_sql_types(
            validator_source,
            pd.DataFrame(data),
        )

        if dataframe.empty:
            print("No data to save.")
            return

        parquet_data = dataframe.to_parquet(index=False)
        directory_url, file_url = self._urls(source, session_key)
        headers = self._authorization_headers()

        directory_response = requests.put(
            directory_url,
            headers=headers,
            timeout=(60, 240),
        )
        directory_response.raise_for_status()

        response = requests.put(
            file_url,
            params={"overwrite": "false"},
            data=parquet_data,
            headers={**headers, "Content-Type": "application/octet-stream"},
            timeout=(60, 240),
        )
        response.raise_for_status()

        print(f"Data saved to session_key={session_key}/{source}.parquet")

        return  dataframe

    @classmethod
    def _apply_sql_types(
        cls,
        source: str,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """Converte os dados da API nos tipos definidos pelos DDLs Bronze."""
        for column, sql_type in cls.COLUMN_TYPES.get(source, {}).items():
            if column not in dataframe:
                continue

            if sql_type == "INT":
                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="raise",
                ).astype("Int32")
            elif sql_type == "BIGINT":
                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="raise",
                ).astype("Int64")
            elif sql_type == "DOUBLE":
                dataframe[column] = pd.to_numeric(
                    dataframe[column],
                    errors="raise",
                ).astype("Float64")
            elif sql_type == "BOOLEAN":
                dataframe[column] = dataframe[column].astype("boolean")
            elif sql_type == "STRING":
                dataframe[column] = dataframe[column].astype("string")
            elif sql_type == "ARRAY<BIGINT>":
                dataframe[column] = dataframe[column].map(
                    cls._to_bigint_array,
                )

        return dataframe

    @staticmethod
    def _to_bigint_array(value: object) -> object:
        if not isinstance(value, list):
            return value

        return list(pd.array(value, dtype="Int64"))

    def _urls(self, source: str, session_key: int | str) -> tuple[str, str]:
        directory_path = f"{self.path_volume}/session_key={session_key}/"
        directory_url = (
            f"{self.databricks_host}{self.directories_prefix}{directory_path}"
        )
        file_url = (
            f"{self.databricks_host}{self.files_prefix}"
            f"{directory_path}{source}.parquet"
        )
        return directory_url, file_url

    def _authorization_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.databricks_access_token}",
        }
