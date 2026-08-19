from bronze.validator.validator import Validator

class ValidatorDriver(Validator):
    def validate(self, data: list[dict]) -> bool:
        session_key_none = {}
        meeting_key_none = {}
        driver_number_none = {}
        lap_number_none = {}

        session_key = get.('session_key')
        meeting_key = get.('meeting_key')
        driver_number = get.('driver_number')
        lap_number = get.('lap_number')

        if not data:
            print("No data to validate.")
            return False, session_key_none, meeting_key_none, driver_number_none, lap_number_none
        if 