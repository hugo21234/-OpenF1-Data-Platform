from bronze.validator.validator import Validator


class ValidatorStints(Validator):
    def validate(self, data: list[dict], expected_session: str) -> bool:
        fields = ("session_key", "meeting_key", "driver_number", "stint_number", "lap_start")
        invalid = {field: {} for field in fields}

        for stint in data:
            for field in fields:
                value = stint.get(field)
                if value is None or str(value).strip() == "":
                    print(f"Invalid {field}: {value}")
                    invalid[field][field.title()] = expected_session
                    break

        result = tuple(invalid[field] for field in fields)
        if not data:
            print("No data to validate.")
            return (False, *result)
        if any(result):
            print("Validation failed. Invalid data found.")
            return (False, *result)
        return (True, *result)
