import unittest as ut
from common.variables import RESPONSE, ERROR
from client import default_client as dc


class TestClientFunctions(ut.TestCase):
    def setUp(self):
        # Оставил на будущее
        pass

    def tearDown(self):
        # Оставил на будущее
        pass

    def test_response_ok(self):
        self.assertEqual(dc.process_ans({RESPONSE: 200}), '200 : SERVER OK', 'Все окей!')

    def test_response_not_ok(self):
        self.assertNotEqual(dc.process_ans({RESPONSE: 200}), '200 : OK', 'Проблема..')

    def test_value_error(self):
        self.assertRaises(ValueError, dc.process_ans, {ERROR: 'Bad Request'})

    # def test_nameless_user(self):
    #     self.assertDictEqual(dc.create_presence({USER: {ACCOUNT_NAME: ''}}), {USER: {ACCOUNT_NAME: 'Guest/Default'}})


if __name__ == '__main__':
    ut.main()
