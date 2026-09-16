import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from requests import Response
from requests.exceptions import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bronze.extractor.race import RequestRace


class CarDataWindowTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.storage = Mock()
        self.storage.exists.return_value = False
        self.loader = Mock()
        self.pipeline = RequestRace(self.client, self.storage, self.loader)
        sleep = patch("bronze.extractor.base.time.sleep")
        sleep.start()
        self.addCleanup(sleep.stop)

    def extract(self):
        self.pipeline.extract_car_data(
            1304, 11465, [1],
            "2026-01-01T10:00:00+00:00", "2026-01-01T10:12:00+00:00",
        )

    def test_contiguous_windows_and_single_save(self):
        self.client.get_data.side_effect = [[{"sample": 1}], [], [{"sample": 2}]]
        self.extract()
        calls = self.client.get_data.call_args_list
        self.assertEqual(len(calls), 3)
        for call, start, end in zip(calls, ("00", "05", "10"), ("05", "10", "12")):
            self.assertEqual(call.args, ("/car_data", {
                "session_key": 11465, "driver_number": 1,
                "date>=": f"2026-01-01T10:{start}:00+00:00",
                "date<": f"2026-01-01T10:{end}:00+00:00",
            }))
        self.storage.save.assert_called_once_with(
            source="car_data_driver=1", meeting_key=1304, session_key=11465,
            data=[{"sample": 1}, {"sample": 2}],
        )
        self.loader.load.assert_called_once()

    def test_failed_window_does_not_save_partial_data(self):
        self.client.get_data.side_effect = [[{"sample": 1}], RuntimeError("API failed")]
        with self.assertRaisesRegex(RuntimeError, "API failed"):
            self.extract()
        self.storage.save.assert_not_called()
        self.loader.load.assert_not_called()

    def test_existing_file_is_reused(self):
        self.storage.exists.return_value = True
        self.extract()
        self.client.get_data.assert_not_called()
        self.storage.save.assert_not_called()
        self.loader.load.assert_called_once()

    def test_404_advances_to_next_window_and_preserves_data(self):
        response = Response()
        response.status_code = 404
        self.client.get_data.side_effect = [
            [{"sample": 1}], HTTPError(response=response), [{"sample": 2}],
        ]
        self.extract()
        self.assertEqual(self.client.get_data.call_count, 3)
        self.assertEqual(self.client.get_data.call_args.args[1]["date>="],
                         "2026-01-01T10:10:00+00:00")
        self.assertEqual(self.storage.save.call_args.kwargs["data"],
                         [{"sample": 1}, {"sample": 2}])

    def test_other_http_errors_propagate_without_partial_save(self):
        for status in (500, 422, None):
            with self.subTest(status=status):
                response = Response() if status is not None else None
                if response is not None:
                    response.status_code = status
                self.client.get_data.side_effect = HTTPError(response=response)
                with self.assertRaises(HTTPError):
                    self.extract()
                self.storage.save.assert_not_called()
                self.loader.load.assert_not_called()
