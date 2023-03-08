import multiprocessing
import os
import socket
import time
import unittest
from unittest.mock import patch
import logging

from clocks import Listener, send_message
from utils import EventType, gen_message, setup_logger

class TestSendMessage(unittest.TestCase):
    @patch('clocks.socket.socket')
    def test_send_message(self, mock_socket):
        port = 6664
        logical_clock = 42
        send_message(port, logical_clock)
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket().connect.assert_called_once_with(('127.0.0.1', port))
        mock_socket().send.assert_called_once_with(logical_clock.to_bytes(4, 'big'))

    @patch('clocks.socket.socket')
    def test_send_message_with_different_port(self, mock_socket):
        port = 6663
        logical_clock = 42
        send_message(port, logical_clock)
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket().connect.assert_called_once_with(('127.0.0.1', port))
        mock_socket().send.assert_called_once_with(logical_clock.to_bytes(4, 'big'))

    @patch('clocks.socket.socket')
    def test_send_message_with_improper_logical_clock(self, mock_socket):
        port = 6664
        logical_clock = -1
        self.assertRaises(OverflowError, send_message, port, logical_clock)

    @patch('clocks.socket.socket')
    def test_send_message_with_improper_port_and_logical_clock(self, mock_socket):
        port = -1
        logical_clock = -1
        self.assertRaises(OverflowError, send_message, port, logical_clock)


class TestListener(unittest.TestCase):
    def test_run_and_exit(self):
        port = 6665
        queue = multiprocessing.Queue()
        listener = Listener(port, queue, 'machine_0.log')
        listener.start()
        time.sleep(0.5)
        try:
            self.assertFalse(listener.exit.is_set())
        finally:
            listener.shutdown()
            listener.join()
        self.assertTrue(listener.exit.is_set())

    def delete_log_files_generated(self):
        os.remove(f"machine_0.log")

class TestGenMessage(unittest.TestCase):
    def test_gen_message_received(self):
        message = gen_message(EventType.RECEIVED, 5, 3, 10, 2)
        expected_message = "(Logical Clock Time 5) Received a message with logical time 3. Current queue length is 10."
        self.assertEqual(message, expected_message)

    def test_gen_message_sent_one(self):
        message = gen_message(EventType.SENT_ONE, 8, recip_id=3)
        expected_message = "(Logical Clock Time 8) Sent a message to machine 3."
        self.assertEqual(message, expected_message)

    def test_gen_message_sent_both(self):
        message = gen_message(EventType.SENT_BOTH, 10)
        expected_message = "(Logical Clock Time 10) Sent a message to both other machines."
        self.assertEqual(message, expected_message)

    def test_gen_message_internal(self):
        message = gen_message(EventType.INTERNAL, 15)
        expected_message = "(Logical Clock Time 15) Internal event occurred."
        self.assertEqual(message, expected_message)

class TestSetupLogger(unittest.TestCase):
    def test_setup_logger(self):
        logger_name = 'test_logger'
        log_file = 'logs/test.log'
        setup_logger(logger_name, log_file)
        logger = logging.getLogger(logger_name)
        # assert that test.log file was created in directory
        self.assertTrue(os.path.exists(log_file))

    def tearDown(self):
        os.remove("logs/test.log")

if __name__ == '__main__':
    unittest.main()