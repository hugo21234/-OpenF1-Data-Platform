from bronze.validator.validator import Validator


class ValidatorStints(Validator):
    REQUIRED_FIELDS = (
        "session_key",
        "meeting_key",
        "driver_number",
        "stint_number",
        "lap_start",
    )
