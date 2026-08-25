from bronze.validator.validator import Validator


class ValidatorLaps(Validator):
    REQUIRED_FIELDS = (
        "session_key",
        "meeting_key",
        "driver_number",
        "lap_number",
    )
