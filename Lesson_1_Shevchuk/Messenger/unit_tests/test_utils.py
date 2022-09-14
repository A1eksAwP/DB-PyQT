import unittest as ut
from common.variables import *
from common.utils import get_message, send_message


class TestUtilsFunctions(ut.TestCase):

    _message_send = {
        ACTION: PRESENCE,
        TIME: 1.1,
        USER: {
            ACCOUNT_NAME: 'Test'
        }
    }
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

    def test_send_message(self):
        # Не стал пока с сокетом заморачиваться
        pass

    def test_get_message(self):
        # Не стал пока с сокетом заморачиваться
        pass


if __name__ == '__main__':
    ut.main()
