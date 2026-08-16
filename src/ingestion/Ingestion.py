from os import read
import os
import requests
from dotenv import load_dotenv
load_dotenv()
import pandas as pd

class ingestion:
    def __init__(self, source,session_key: str, data: list[dict]) -> None:
        self.source = source
        self.session_key = session_key
        self.data = data
        self.dataframe = pd.DataFrame(self.data)
        self.prefix = os.getenv('prefix_databricks')
        self.databricks_access_token = os.getenv('access_token')
        self.databricks_host = os.getenv('databricks_host')
        self.path_volume = os.getenv('path_volume_databricks')

        self.url = f"{self.databricks_host}{self.prefix}{self.path_volume}/{self.source}_{self.session_key}.parquet"


    def process_data(self):
       to_parquet = self.dataframe.to_parquet(f"{self.source}_{self.session_key}.parquet", index=False)
       return to_parquet

    def save_data(self, destination):
        process_data = self.process_data()
        print(f"Data saved to {destination}/{self.source}_{self.session_key}.parquet")
        requests.put(self.url, data=process_data, headers={"Authorization": f"Bearer {self.databricks_access_token}"})
        return None