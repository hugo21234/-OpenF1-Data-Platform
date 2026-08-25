from bronze.validator.validator import Validator


class ValidatorCarData(Validator):
    REQUIRED_FIELDS = (
        "session_key",
        "meeting_key",
        "driver_number",
        "date",
        "brake",
        "drs",
        "n_gear",
        "rpm",
        "speed",
        "throttle",
    )
