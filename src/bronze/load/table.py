from bronze.load.contracts import TableLoader

import os

import pandas as pd
import requests
from dotenv import load_dotenv

from bronze.storage.contracts import VolumeStorage
from bronze.validator.validator_car_data import ValidatorCarData
from bronze.validator.validator_driver import ValidatorDriver
from bronze.validator.validator_laps import ValidatorLaps
from bronze.validator.validator_pit import ValidatorPit
from bronze.validator.validator_position import ValidatorPosition
from bronze.validator.validator_race_control import ValidatorRaceControl
from bronze.validator.validator_stints import ValidatorStints

class DatabricksTableLoader(TableLoader):
     
    def __init__(self) -> None:
            
            load_dotenv()
    
            self.files_prefix = os.getenv("prefix_databricks_files")
            self.directories_prefix = os.getenv("prefix_databricks")
            self.databricks_access_token = os.getenv("access_token")
            self.databricks_host = os.getenv("databricks_host")
            self.path_volume = os.getenv("path_volume_databricks")
            self.validators = {
                "drivers": ValidatorDriver(),
                "laps": ValidatorLaps(),
                "stints": ValidatorStints(),
                "pit": ValidatorPit(),
                "position": ValidatorPosition(),
                "race_control": ValidatorRaceControl(),
                "car_data": ValidatorCarData(),
            }
    
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

    def exist(self, source: str, session_key: str) -> bool:

        table_url = self._urls()

        statement = """
                SELECT * FROM {source}
                WHERE source = '{source}'
                AND session_key = '{session_key}'
                LIMIT 1
                """
        payload = {
                "warehouse_id": self.warehouse_id,
                "statement": statement,
                "parameters": [{
                    "name": "session_key",
                    "type": INTEGER,
                    "value": session_key
                            }]
                }
        
        response = requests.post(table_url,headers=self._authorization_headers(),json=payload,timeout=(60, 240),)

        if response.status_code == 200:
            
            return True
        if response.status_code == 404:
            print('File not found')
            raise ValueError("Unexpected status code from Databricks API.")

        
        return True






    def _urls(self) -> str:
        table_url = f"{self.databricks_host}/api/2.0/sql/statements"
        return  table_url
