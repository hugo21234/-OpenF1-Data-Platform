import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from clients.openf1 import OpenF1Client


def response(status, body):
    result = requests.Response()
    result.status_code = status
    result._content = body.encode()
    result.url = "https://api.openf1.org/v1/car_data"
    return result


class RetryTests(unittest.TestCase):
    def setUp(self):
        self.client = OpenF1Client()
        self.addCleanup(self.client.session.close)
        self.get = Mock()
        self.client.session.get = self.get
        self.params = {"session_key": 11465, "driver_number": 1}
        sleep = patch("clients.openf1.time.sleep")
        self.sleep = sleep.start()
        self.addCleanup(sleep.stop)

    def test_retry_same_request_then_success(self):
        self.get.side_effect = [response(500, "failure"), response(200, '[{"speed": 100}]')]
        self.assertEqual(self.client.get_data("/car_data", self.params), [{"speed": 100}])
        self.assertEqual(self.get.call_count, 2)
        self.assertEqual(self.get.call_args_list[0], self.get.call_args_list[1])
        self.sleep.assert_called_once_with(3)

    def test_persistent_failure_is_bounded_and_keeps_response(self):
        failed = response(500, "server detail")
        self.get.return_value = failed
        with self.assertRaisesRegex(requests.HTTPError, "server detail") as caught:
            self.client.get_data("/car_data", self.params)
        self.assertIs(caught.exception.response, failed)
        self.assertEqual(self.get.call_count, 3)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [3, 9])

    def test_422_is_not_retried(self):
        self.get.return_value = response(422, "too much data")
        with self.assertRaisesRegex(requests.HTTPError, "too much data"):
            self.client.get_data("/car_data", self.params)
        self.get.assert_called_once()
        self.sleep.assert_not_called()

    def test_comparison_query_has_no_extra_equals(self):
        self.get.return_value = response(200, "[]")
        self.client.get_data("/car_data", {
            "session_key": 11465, "driver_number": 1,
            "date>=": "2026-02-11T07:00:00+00:00",
            "date<": "2026-02-11T07:05:00+00:00",
        })
        query = self.get.call_args.kwargs["params"]
        prepared = requests.Request("GET", self.client.base_url + "/car_data", params=query).prepare()
        from urllib.parse import unquote
        self.assertEqual(unquote(prepared.url).split("?", 1)[1],
            "session_key=11465&driver_number=1"
            "&date>=2026-02-11T07:00:00+00:00"
            "&date<2026-02-11T07:05:00+00:00")

    def test_empty_telemetry_window_raises_404(self):
        self.get.return_value = response(404, '{"detail":"No results found."}')
        params = {**self.params, "date>=": "2026-02-11T11:05:00Z",
                  "date<": "2026-02-11T11:10:00Z"}
        with self.assertRaises(requests.HTTPError) as caught:
            self.client.get_data("/car_data", params)
        self.assertEqual(caught.exception.response.status_code, 404)
        self.get.assert_called_once()
        self.sleep.assert_not_called()

    def test_other_404_responses_remain_errors(self):
        window = {**self.params, "date>=": "2026-02-11T11:05:00Z",
                  "date<": "2026-02-11T11:10:00Z"}
        for endpoint, params, body in [
            ("/car_data", window, '{"detail":"Not Found"}'),
            ("/car_data", window, 'not json'),
            ("/car_data", window, '[]'),
            ("/car_data", self.params, '{"detail":"No results found."}'),
            ("/sessions", window, '{"detail":"No results found."}'),
        ]:
            with self.subTest(endpoint=endpoint, params=params, body=body):
                self.get.return_value = response(404, body)
                with self.assertRaises(requests.HTTPError):
                    self.client.get_data(endpoint, params)
