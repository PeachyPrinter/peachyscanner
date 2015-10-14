import sys
import unittest
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.status import Status


class StatusTest(unittest.TestCase):
    def setUp(self):
        self.last_call = None
        self.last_call2 = None

    def fake_handler(self, last_call):
        self.last_call = last_call

    def fake_handler2(self, last_call):
        self.last_call2 = last_call

    def test_init_has_correct_defaults(self):
        status = Status()
        self.assertEqual("Startup", status.operation)
        self.assertEqual(1.0, status.progress)

    def test_register_handler_calls_back_handlers_with_data_change(self):
        status = Status()
        status.register_handler(self.fake_handler)
        status.progress = 0.5
        self.assertEqual(0.5, self.last_call.progress)

    def test_register_handler_calls_back_multiple_handlers_with_data_change(self):
        status = Status()
        status.register_handler(self.fake_handler)
        status.register_handler(self.fake_handler2)
        status.progress = 0.5
        self.assertEqual(0.5, self.last_call.progress)
        self.assertEqual(0.5, self.last_call2.progress)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
