from bronze.validator.validator import Validator


class ValidatorDriver(Validator):
    REQUIRED_FIELDS = ("session_key", "meeting_key", "driver_number")
