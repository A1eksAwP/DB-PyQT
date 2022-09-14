import unittest as ut
from common.variables import *
from server import main_server as ms


class TestServerFunctions(ut.TestCase):
    _response_bad = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    _response_ok = {RESPONSE: 200}

    def setUp(self):
        # Оставил на будущее
        pass

    def tearDown(self):
        # Оставил на будущее
        pass

    def test_absence_user(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: PRESENCE,
             TIME: '1.1'}
        ), self._response_bad)

    def test_absence_action(self):
        self.assertEqual(ms.process_client_message(
            {USER: {ACCOUNT_NAME: 'Guest/Default'},
             TIME: '1.1'}
        ), self._response_bad)

    def test_absence_time(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: PRESENCE,
             USER: {ACCOUNT_NAME: 'Guest/Default'}}
        ), self._response_bad)

    def test_absence_user_action(self):
        self.assertEqual(ms.process_client_message(
            {TIME: '1.1'}
        ), self._response_bad)

    def test_absence_user_time(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: PRESENCE}
        ), self._response_bad)

    def test_absence_action_time(self):
        self.assertEqual(ms.process_client_message(
            {USER: {ACCOUNT_NAME: 'Guest/Default'}}
        ), self._response_bad)

    def test_absence_user_action_time(self):
        self.assertEqual(ms.process_client_message(''),
                         self._response_bad)

    def test_unknown_action(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: 'OTHER',
             USER: {ACCOUNT_NAME: 'Guest/Default'},
             TIME: '1.1'}
        ), self._response_bad)

    def test_unknown_user(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: PRESENCE,
             USER: {ACCOUNT_NAME: 'Elon Musk'},
             TIME: '1.1'}
        ), self._response_bad)

    def test_response_ok(self):
        self.assertEqual(ms.process_client_message(
            {ACTION: PRESENCE,
             USER: {ACCOUNT_NAME: 'Guest/Default'},
             TIME: '1.1'}
        ), self._response_ok)


if __name__ == '__main__':
    ut.main()
