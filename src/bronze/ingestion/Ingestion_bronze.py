from os import read
import os
import requests
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

class ingestion:
    def __init__(self, source, session_key: str) -> None:

        self.source = source
        self.session_key = session_key

        self.files_prefix = os.getenv('prefix_databricks_files')
        self.directories_prefix = os.getenv('prefix_databricks')
        self.databricks_access_token = os.getenv('access_token')
        self.databricks_host = os.getenv('databricks_host')
        self.path_volume = os.getenv('path_volume_databricks')

        if not all([
            self.files_prefix,
            self.directories_prefix,
            self.databricks_access_token,
            self.databricks_host,
            self.path_volume,
        ]):
            
            raise ValueError("One or more required environment variables are missing.")

        self.directory_path = f"{self.path_volume}/session_key={self.session_key}/"
        self.directory_url = f"{self.databricks_host}{self.directories_prefix}{self.directory_path}"
        self.url = f"{self.databricks_host}{self.files_prefix}{self.directory_path}{self.source}.parquet"

    def process_data(self, data: list[dict]) -> bytes | None:
        dataframe = pd.DataFrame(data)
        if dataframe.empty:
            print("No data to save.")
            return None
        return dataframe.to_parquet(index=False)

    def file_exists(self) -> bool:
        response = requests.head(
            self.url,
            headers={"Authorization": f"Bearer {self.databricks_access_token}"},
            timeout=(60, 240),
        )
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        response.raise_for_status()

    def save_data(self, parquet_data: bytes):
        headers = {"Authorization": f"Bearer {self.databricks_access_token}"}
        directory_response = requests.put(
            self.directory_url,
            headers=headers,
            timeout=(60, 240),
        )
        directory_response.raise_for_status()

        response = requests.put(
            self.url,
            params={"overwrite": "false"},
            data=parquet_data,
            headers={**headers, "Content-Type": "application/octet-stream"},
            timeout=(60, 240),
        )
        response.raise_for_status()
        print(f"Data saved to session_key={self.session_key}/{self.source}.parquet")
        return response
      
