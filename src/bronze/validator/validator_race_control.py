from bronze.validator.validator import Validator


class ValidatorRaceControl(Validator):
    def validate(self, data: list[dict], expected_session: str) -> bool:
        fields = ("session_key", "meeting_key", "date", "category", "message")
        invalid = {field: {} for field in fields}

        for event in data:
            for field in fields:
                value = event.get(field)
                if value is None or str(value).strip() == "":
                    print(f"Invalid {field}: {value}")
                    invalid[field][field.title()] = expected_session
                    raise

        result = tuple(invalid[field] for field in fields)
        if not data:
            print("No data to validate.")
            return (False, *result)
        
        if any(result):
            print("Validation failed. Invalid data found.")
            return (False, *result)
        
        return (True, *result)
