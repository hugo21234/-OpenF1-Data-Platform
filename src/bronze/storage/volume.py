import os
import requests
import pandas as pd
from dotenv import load_dotenv

from bronze.validator.validator_driver import ValidatorDriver
from bronze.validator.validator_laps import ValidatorLaps
from bronze.validator.validator_stints import ValidatorStints
from bronze.validator.validator_pit import ValidatorPit
from bronze.validator.validator_position import ValidatorPosition
from bronze.validator.validator_race_control import ValidatorRaceControl
from bronze.validator.validator_car_data import ValidatorCarData
from bronze.contracts import SaveTable

class DatabricksVolumeStorage(SaveTable):
    def __init__(self) -> None:
        load_dotenv()
        self.files_prefix = os.getenv("prefix_databricks_files")
        self.directories_prefix = os.getenv("prefix_databricks")
        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.path_volume = os.getenv("path_volume_databricks")

        self.validator_driver = ValidatorDriver()
        self.validators = {
            "stints": ValidatorStints(),
            "pit": ValidatorPit(),
            "position": ValidatorPosition(),
            "race_control": ValidatorRaceControl(),
            "car_data": ValidatorCarData(),
        }
        self.validator_laps = ValidatorLaps()
        
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

    def save(self,source: str,session_key: int, data: list[dict]) -> None:
        
        validator_source = (
            "car_data" if source.startswith("car_data_driver=") else source
        )

        if validator_source == "drivers":
            validation_result = self.validator_driver.validate(
                data,
                session_key,
            )
        elif validator_source == "laps":
            validation_result = self.validator_laps.validate(
                data,
                session_key,
            )
        else:
            validator = self.validators.get(validator_source)
            if validator is None:
                print(f"No validator configured for source: {source}")
                return
            validation_result = validator.validate(data, session_key)

        if not validation_result[0]:
            print("Validation failed. Invalid data found.")
            print(f"Validation context: {validation_result[1]}")
            return

        dataframe = pd.DataFrame(data)

        if dataframe.empty: 
            print("No data to save.")
            return
        
        parquet_data = dataframe.to_parquet(index=False)
        directory_url, file_url = self._urls(source, session_key)
        headers = self._authorization_headers()
        
        directory_response = requests.put(directory_url,headers=headers,timeout=(60, 240))
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
        
    def _urls(self, source: str, session_key: int) -> tuple[str, str]:
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

    


    
