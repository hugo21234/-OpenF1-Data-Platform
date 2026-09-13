import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from bronze.extractor.extractor import BronzePipeline
from bronze.load.table import DatabricksTableLoader
from bronze.storage.volume import DatabricksVolumeStorage
from bronze.validator.validator import Validator
from bronze.verification.loadVerifier import LoadVerifier


def session(key, kind='Race', **extra):
    return dict(meeting_key=10, session_key=key, session_type=kind,
                date_end='2020-01-01T12:00:00Z', **extra)


class Boundary:
    def __init__(self, events, label):
        self.events, self.label, self.saved = events, label, set()

    def exists(self, source, meeting_key, session_key):
        return (source, meeting_key, session_key) in self.saved

    def save(self, source, meeting_key, session_key, data):
        self.saved.add((source, meeting_key, session_key))
        self.events.append(('save', source, session_key))

    def load(self, source, meeting_key, session_key):
        self.saved.add((source, meeting_key, session_key))
        self.events.append(('load', source, session_key))


class Client:
    def __init__(self, sessions):
        self.sessions, self.calls = sessions, []
        self.fail_car = False

    def get_data(self, endpoint, params):
        self.calls.append((endpoint, params))
        if endpoint == '/sessions':
            return self.sessions
        if endpoint == '/meetings':
            return [{'meeting_key': 10}]
        if endpoint == '/pit':
            return []
        if endpoint == '/car_data' and self.fail_car:
            raise RuntimeError('transport failure')
        return [{'meeting_key': 10, 'session_key': params['session_key'], 'driver_number': 44}]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.client = Client([session(1, 'Practice'), session(2, 'Qualifying'), session(3)])
        self.storage = Boundary(self.events, 'storage')
        self.loader = Boundary(self.events, 'loader')
        self.pipeline = BronzePipeline(self.client, self.storage, self.loader, year=2020)
        sleep = patch('bronze.extractor.extractor.time.sleep')
        sleep.start()
        self.addCleanup(sleep.stop)

    def test_order_and_rerun(self):
        self.pipeline.run_extraction()
        self.assertEqual([p for e, p in self.client.calls if e == '/meetings'], [{'meeting_key': 10}])
        for key in (1, 2, 3):
            events = [e[:2] for e in self.events if e[2] == key]
            self.assertEqual(events[0], ('save', 'sessions'))
            self.assertEqual(events[-2:], [('load', 'car_data_driver=44'), ('load', 'sessions')])
            self.assertNotIn(('load', 'pit'), events)
        before = list(self.events)
        self.pipeline.run_extraction()
        self.assertEqual(self.events, before)
        self.assertEqual(sum(e == '/drivers' for e, _ in self.client.calls), 6)

    def test_filters(self):
        self.client.sessions += [session(4, 'Testing'), session(5, is_cancelled=True)]
        self.client.sessions += [{**session(6), 'date_end': '2999-01-01T00:00:00Z'},
                                 {**session(7), 'date_end': None}]
        self.assertEqual([s['session_key'] for s in self.pipeline.extract_sessions()], [1, 2, 3])
        self.assertEqual(self.client.calls[0], ('/sessions', {'year': 2020}))

    def test_reuse_meeting_file(self):
        self.storage.saved.add(('meetings', 10, None))
        self.pipeline.run_extraction()
        self.assertFalse(any(e == '/meetings' for e, _ in self.client.calls))
        self.assertEqual(self.events[0], ('load', 'meetings', None))

    def test_session_table_not_loaded_after_failure(self):
        self.client.fail_car = True
        with self.assertRaises(RuntimeError):
            self.pipeline.run_extraction()
        self.assertIn(('save', 'sessions', 1), self.events)
        self.assertNotIn(('load', 'sessions', 1), self.events)

    def test_validation(self):
        validator = Validator()
        self.assertTrue(validator.validate([{'meeting_key': 10}], None, 'meetings', 10)[0])
        self.assertTrue(validator.validate([session(1)], 1, 'sessions', 10)[0])
        self.assertFalse(validator.validate([session(1)], 2, 'sessions', 10)[0])

    def test_paths_and_sql_filters(self):
        storage = object.__new__(DatabricksVolumeStorage)
        storage.path_volume = '/Volumes/test/raw/'
        storage.databricks_host = 'https://example.test'
        storage.files_prefix = '/files'
        storage.directories_prefix = '/directories'
        loader = object.__new__(DatabricksTableLoader)
        loader.path_volume = storage.path_volume
        verifier = object.__new__(LoadVerifier)
        statements = []
        def execute(statement, parameters=None):
            statements.append((statement, parameters))
            return {}
        verifier.execute_statement = execute
        loader.verifier = verifier
        for source, key in [('meetings', None), ('sessions', 1), ('car_data_driver=44', 1)]:
            loader.load(source, 10, key)
            url = storage._urls(source, key, 10)[1]
            self.assertIn(url.removeprefix('https://example.test/files'), statements[-1][0])
        parameters = statements[-2][1]
        self.assertEqual({p['name']: p['value'] for p in parameters},
                         {'meeting_key': '10', 'session_key': '1', 'driver_number': '44'})


if __name__ == '__main__':
    unittest.main()
