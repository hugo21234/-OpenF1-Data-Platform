from bronze.validator.validator import Validator


class ValidatorDriver(Validator):
    def validate(self, data: list[dict], expected_session: str) -> bool:
        session_key_none = {}
        meeting_key_none = {}
        driver_number_none = {}
        lap_number_none = {}

        for driver in data:
            session_key = driver.get("session_key")
            meeting_key = driver.get("meeting_key")
            driver_number = driver.get("driver_number")
            lap_number = driver.get("lap_number")

            if session_key is None or str(session_key).strip() == "":
                print(f"Invalid session_key: {session_key}")
                session_key_none["Session_Key"] = expected_session
                continue
            if meeting_key is None or str(meeting_key).strip() == "":
                print(f"Invalid meeting_key: {meeting_key}")
                meeting_key_none["Meeting_Key"] = expected_session
                continue
            if driver_number is None or str(driver_number).strip() == "":
                print(f"Invalid driver_number: {driver_number}")
                driver_number_none["Driver_Number"] = expected_session
                continue
            if lap_number is None or str(lap_number).strip() == "":
                print(f"Invalid lap_number: {lap_number}")
                lap_number_none["Lap_Number"] = expected_session
                continue

        if not data:
            print("No data to validate.")
            return False, session_key_none, meeting_key_none, driver_number_none, lap_number_none
        if session_key_none or meeting_key_none or driver_number_none or lap_number_none:
            print("Validation failed. Invalid data found.")
            return False, session_key_none, meeting_key_none, driver_number_none, lap_number_none
        return True, session_key_none, meeting_key_none, driver_number_none, lap_number_none
