from dotenv import load_dotenv
import requests
import os
import time


load_dotenv()



class validar_sessionkey:
    def __init__(self):
        self.prefix = os.getenv("prefix_databricks")
        self.access_token = os.getenv("access_token")
        self.path_volume = os.getenv("path_volume_databricks")
        self.databricks_host = os.getenv("databricks_host")
        if not all([self.prefix, self.access_token, self.path_volume, self.databricks_host]):
            raise ValueError("One or more required environment variables are missing.")

    def validar_sessionkey(self,session_key ) -> tuple[bool, object]:

        try:

            response = requests.head(url = (
            f"{self.databricks_host}"
            f"{self.prefix}"
            f"{self.path_volume}"
            f"/session_key={session_key}/"), 
            headers={'Authorization': f'Bearer {self.access_token}'},
            timeout=(60, 240))

            time.sleep(1)  # Sleep for 1 second to avoid overwhelming the API

            if response.status_code == 200:
                return True, response
            
            elif response.status_code == 404:
                return False,'not found'
            else:
                response.raise_for_status()

            
     
        
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ConnectionError):
            raise 

        except requests.exceptions.HTTPError as e:                            
            raise e
        