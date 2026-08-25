from bronze.validator.validator import Validator


class ValidatorPosition(Validator):
    REQUIRED_FIELDS = (
        "session_key",
        "meeting_key",
        "driver_number",
        "position",
        "date",
    )
