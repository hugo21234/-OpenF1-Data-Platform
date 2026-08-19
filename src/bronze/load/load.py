import os
import requests
import pandas as pd
from dotenv import load_dotenv

from bronze.validator.validator_driver import ValidatorDriver
from bronze.contracts import SaveTable

class BronzeStorage(SaveTable):
    def __init__(self) -> None:
        load_dotenv()
        self.files_prefix = os.getenv("prefix_databricks_files")
        self.directories_prefix = os.getenv("prefix_databricks")
        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.path_volume = os.getenv("path_volume_databricks")

        self.validator_driver = ValidatorDriver()
        
        if not all(
            [
                self.files_prefix,
                self.directories_prefix,
                self.databricks_access_token,
                self.databricks_host,
                self.path_volume,
            ]
        ):
            raise ValueError("One or more required environment variables are missing.")

    def save(self, source, session_key, data):

        dataframe = pd.DataFrame(data)

        if dataframe.empty: 
            print("No data to save.")
            return
        
        parquet_data = dataframe.to_parquet(index=False)
        directory_url, file_url = self._urls(source, session_key)
        headers = self._authorization_headers()
        
        directory_response = requests.put(directory_url,headers=headers,timeout=(60, 240))
        directory_response.raise_for_status()

        driver_validation, Session_Key_none, drivers_name_none = self.validator_driver.validate(data)
        if not driver_validation :
            print("Validation failed. Invalid data found.")
            print(f"Session_Key_none: {Session_Key_none}")
            print(f"drivers_name_none: {drivers_name_none}")
            return

        response = requests.put(
                    file_url,
                    params={"overwrite": "false"},
                    data=parquet_data,
                    headers={**headers, "Content-Type": "application/octet-stream"},
                    timeout=(60, 240),
                )
        response.raise_for_status()
        print(f"Data saved to session_key={session_key}/{source}.parquet")
        
        return {(source, session_key, data)}

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
        return {"Authorization": f"Bearer {self.databricks_access_token}"}    

    


    
