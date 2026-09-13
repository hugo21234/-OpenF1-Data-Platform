REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "meetings": ("meeting_key",),
    "sessions": ("meeting_key", "session_key"),
    "drivers": (
        "session_key",
        "meeting_key",
        "driver_number",
    ),
    "laps": (
        "session_key",
        "meeting_key",
        "driver_number",
        "lap_number",
    ),
    "stints": (
        "session_key",
        "meeting_key",
        "driver_number",
        "stint_number",
        "lap_start",
        "lap_end",
    ),
    "pit": (
        "session_key",
        "meeting_key",
        "driver_number",
        "lap_number",
        "date",
    ),
    "position": (
        "session_key",
        "meeting_key",
        "driver_number",
        "position",
        "date",
    ),
    "race_control": (
        "session_key",
        "meeting_key",
        "date",
        "category",
    ),
    "car_data": (
        "session_key",
        "meeting_key",
        "driver_number",
        "date",
    ),
}


class Validator:
    """Valida os identificadores mínimos necessários para dados Bronze."""

    def validate(
        self,
        data: list[dict],
        expected_session: int | str | None,
        source: str,
        expected_meeting: int | str | None = None,
    ) -> tuple[bool, list[dict[str, object]]]:
        required_fields = REQUIRED_FIELDS[source]
        invalid_records: list[dict[str, object]] = []

        if not data:
            return False, [
                {
                    "source": source,
                    "expected_session": expected_session,
                    "reason": "no_data",
                }
            ]

        for record_index, record in enumerate(data):
            for field in required_fields:
                if field not in record:
                    invalid_records.append(
                        {
                            "source": source,
                            "record_index": record_index,
                            "field": field,
                            "value": None,
                            "reason": "missing",
                            "expected_session": expected_session,
                        }
                    )
                    continue

                value = record[field]
                if value is None or (
                    isinstance(value, str) and not value.strip()
                ):
                    invalid_records.append(
                        {
                            "source": source,
                            "record_index": record_index,
                            "field": field,
                            "value": value,
                            "reason": "empty",
                            "expected_session": expected_session,
                        }
                    )

            for field, expected in (("session_key", expected_session),
                                    ("meeting_key", expected_meeting)):
                if expected is not None and str(record.get(field)) != str(expected):
                    invalid_records.append({"source": source, "record_index": record_index,
                                            "field": field, "reason": "mismatch",
                                            "expected": expected, "value": record.get(field)})

        return not invalid_records, invalid_records
