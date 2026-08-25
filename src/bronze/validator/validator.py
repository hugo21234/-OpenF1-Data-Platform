class Validator:
    REQUIRED_FIELDS: tuple[str, ...] = ()

    def validate(
        self,
        data: list[dict],
        expected_session: int | str,
    ) -> tuple[bool, dict[str, object]]:
        if not data:
            return False, {"error": "No data to validate."}

        invalid_records = []
        for index, record in enumerate(data):
            missing_fields = [
                field
                for field in self.REQUIRED_FIELDS
                if self._is_empty(record.get(field))
            ]
            session_key = record.get("session_key")
            has_expected_session = str(session_key) == str(expected_session)

            if missing_fields or not has_expected_session:
                invalid_records.append(
                    {
                        "index": index,
                        "missing_fields": missing_fields,
                        "session_key": session_key,
                    }
                )

        if invalid_records:
            return False, {
                "expected_session": expected_session,
                "invalid_records": invalid_records,
            }

        return True, {}

    @staticmethod
    def _is_empty(value: object) -> bool:
        return value is None or (
            isinstance(value, str) and not value.strip()
        )
