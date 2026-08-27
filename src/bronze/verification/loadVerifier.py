import os
import time

import requests
from dotenv import load_dotenv


class LoadVerifier:
    def __init__(self) -> None:
        load_dotenv()

        self.databricks_access_token = os.getenv("access_token")
        self.databricks_host = os.getenv("databricks_host")
        self.warehouse_id = os.getenv("warehouse_id")

        if not all(
            [
                self.databricks_access_token,
                self.databricks_host,
                self.warehouse_id,
            ]
        ):
            raise ValueError(
                "One or more required environment variables are missing."
            )

    def exists(
        self,
        table_name: str,
        driver_number: int | None,
        session_key: int,
    ) -> bool:
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
            SELECT 1
            FROM {table_name}
            WHERE {' AND '.join(filters)}
            LIMIT 1
        """
        result = self.execute_statement(statement, parameters)
        return bool(result.get("result", {}).get("data_array"))

    def execute_statement(
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

        while result.get("status", {}).get("state") in {"PENDING", "RUNNING"}:
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
