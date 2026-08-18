import os

import pandas as pd
import requests
from dotenv import load_dotenv

from bronze.contracts import BronzeStorage


class DatabricksBronzeStorage(BronzeStorage):
    def __init__(self) -> None:
        load_dotenv()

        self.files_prefix = os.getenv("prefix_databricks_files")
        self.directories_prefix = os.getenv("prefix_databricks")
        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.path_volume = os.getenv("path_volume_databricks")

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

    def save(
        self,
        source: str,
        session_key: str,
        data: list[dict],
    ) -> None:
        dataframe = pd.DataFrame(data)
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

    def _urls(self, source: str, session_key: str) -> tuple[str, str]:
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
