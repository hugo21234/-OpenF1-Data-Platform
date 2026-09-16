import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bronze.extractor.extractor import BronzePipeline
from bronze.extractor.practice import RequestPractice
from bronze.extractor.qualifying import RequestQualifying
from bronze.extractor.race import RequestRace


class SessionsClient:
    def __init__(self, sessions):
        self.sessions = sessions
        self.calls = []

    def get_data(self, endpoint, params):
        self.calls.append((endpoint, params))
        return self.sessions


def session(key, session_type="Race", **extra):
    return {
        "meeting_key": 10,
        "session_key": key,
        "session_type": session_type,
        "date_end": "2020-01-01T11:59:59Z",
        **extra,
    }


class ExtractSessionsTests(unittest.TestCase):
    @patch("bronze.extractor.base.time.sleep")
    @patch("bronze.extractor.base.datetime")
    def test_returns_only_completed_non_cancelled_races(self, mock_datetime, _sleep):
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat
        mock_datetime.now.return_value = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
        client = SessionsClient([
            session(1),
            session(2, "Practice"),
            session(3, "Qualifying"),
            session(4, session_name="Sprint Race"),
            session(5, is_cancelled=True),
            session(6, date_end="2020-01-01T12:00:00Z"),
            session(7, date_end="2020-01-01T12:00:01Z"),
            session(8, date_end="invalid"),
            session(9, date_end="2020-01-01T11:00:00"),
        ])
        pipeline = BronzePipeline(client, storage=None, table_loader=None)

        result = pipeline.extract_sessions()

        self.assertEqual([item["session_key"] for item in result], [1])
        self.assertEqual(client.calls[0][0], "/sessions")
        self.assertEqual(client.calls[0][1]["year"], __import__("time").localtime().tm_year)

    @patch("bronze.extractor.base.time.sleep")
    @patch("bronze.extractor.base.datetime")
    def test_each_request_selects_its_own_session_type(self, mock_datetime, _sleep):
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat
        mock_datetime.now.return_value = datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc)
        sessions = [session(1, "Practice"), session(2, "Qualifying"), session(3, "Race")]

        for extractor_type, expected_key in (
            (RequestPractice, 1), (RequestQualifying, 2), (RequestRace, 3),
        ):
            with self.subTest(extractor_type=extractor_type):
                extractor = extractor_type(SessionsClient(sessions), storage=None, table_loader=None)
                result = extractor.extract_sessions()
                self.assertEqual([item["session_key"] for item in result], [expected_key])
                self.assertEqual(extractor.client.calls[0][1]["session_type"],
                                 sessions[expected_key - 1]["session_type"])


if __name__ == "__main__":
    unittest.main()
