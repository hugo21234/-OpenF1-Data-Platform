from bronze.validator.validator import Validator


class ValidatorRaceControl(Validator):
    REQUIRED_FIELDS = (
        "session_key",
        "meeting_key",
        "date",
        "category",
        "message",
    )
