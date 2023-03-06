import multiprocessing
import os
import socket
import time
import unittest
from unittest.mock import patch

from clocks import Listener, machine_process, send_message


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
        listener = Listener(port, queue)
        listener.start()
        time.sleep(0.5)
        try:
            self.assertFalse(listener.exit.is_set())
        finally:
            listener.shutdown()
            listener.join()
        self.assertTrue(listener.exit.is_set())


class TestMachineProcess(unittest.TestCase):
    global_time = time.time()

    def test_machine_process(self):
        machine_id = 0
        queue = multiprocessing.Queue()
        ports = [5555, 5556, 5557]
        total_run_time = 10
        machine_process(self.global_time, machine_id,
                        queue, ports, total_run_time)
        self.assertEqual(queue.get(), 0)
        self.assertEqual(queue.get(), 1)
        self.assertEqual(queue.get(), 2)

    def delete_log_files_generated(self):
        os.remove(f"{self.global_time}_machine_0.log")


if __name__ == '__main__':
    TestMachineProcess.global_time = time.time()
    unittest.main()
