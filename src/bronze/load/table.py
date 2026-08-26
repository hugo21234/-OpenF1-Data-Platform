import os
import time

import requests
from dotenv import load_dotenv

from bronze.load.contracts import TableLoader


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
    }

    def __init__(self) -> None:
        load_dotenv()

        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.path_volume = os.getenv("path_volume_databricks")
        self.warehouse_id = os.getenv("warehouse_id")

        if not all(
            [
                self.databricks_access_token,
                self.databricks_host,
                self.path_volume,
                self.warehouse_id,
            ]
        ):
            raise ValueError(
                "One or more required environment variables are missing."
            )

    def exists(self, source: str, session_key: int) -> bool:
        table_name, driver_number = self._source_data(source)
        filters = ["session_key = :session_key"]
        parameters = [
            {
                "name": "session_key",
                "type": "INT",
                "value": str(session_key),
            }
        ]

        if driver_number is not None:
            filters.append("driver_number = :driver_number")
            parameters.append(
                {
                    "name": "driver_number",
                    "type": "INT",
                    "value": str(driver_number),
                }
            )

        statement = f"""
            SELECT 1 FROM {table_name}
            WHERE {' AND '.join(filters)}
            LIMIT 1
        """
        result = self._execute_statement(statement, parameters)
        return bool(result.get("result", {}).get("data_array"))

    def load(self, source: str, session_key: int) -> None:
        table_name, _ = self._source_data(source)

        if self.exists(source, session_key):
            print(
                f"Data already loaded: table={table_name} "
                f"| session_key={session_key} | source={source}"
            )
            return

        file_path = (
            f"{self.path_volume.rstrip('/')}/"
            f"session_key={session_key}/{source}.parquet"
        )
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
        self._execute_statement(statement)

        print(
            f"Data loaded to table={table_name} "
            f"| session_key={session_key} | source={source}"
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

    def _execute_statement(
        self,
        statement: str,
        parameters: list[dict[str, str]] | None = None,
    ) -> dict:
        payload = {
            "warehouse_id": self.warehouse_id,
            "statement": statement,
            "wait_timeout": "50s",
            "on_wait_timeout": "CONTINUE",
        }

        if parameters:
            payload["parameters"] = parameters

        response = requests.post(
            self._url(),
            headers=self._authorization_headers(),
            json=payload,
            timeout=(60, 240),
        )
        response.raise_for_status()
        result = response.json()

        while result.get("status", {}).get("state") in {
            "PENDING",
            "RUNNING",
        }:
            
            time.sleep(2)
            statement_id = result["statement_id"]
            response = requests.get(
                f"{self._url()}/{statement_id}",
                headers=self._authorization_headers(),
                timeout=(60, 240),
            )
            response.raise_for_status()
            result = response.json()

        state = result.get("status", {}).get("state")
        if state != "SUCCEEDED":
            error = result.get("status", {}).get("error", {})
            message = error.get("message", "Databricks statement failed.")
            raise ValueError(message)

        return result

    def _url(self) -> str:
        return f"{self.databricks_host.rstrip('/')}/api/2.0/sql/statements"

    def _authorization_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.databricks_access_token}",
            "Content-Type": "application/json",
        }
