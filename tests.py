import logging
import os
import time
import unittest
from queue import Queue
from unittest.mock import call, patch

from clocks import Listener, Machine
from utils import EventType, gen_message, setup_logger


class TestListener(unittest.TestCase):
    def test_run_and_exit(self):
        port = 6665
        queue = Queue()
        listener = Listener(port, queue)
        listener.start()
        time.sleep(0.5)
        try:
            self.assertFalse(listener.exit.is_set())
        finally:
            listener.shutdown()
            listener.join()
        self.assertTrue(listener.exit.is_set())
        self.assertTrue(len(listener.inputs) == 0)

    @patch('socket.socket')
    @patch('select.select')
    def test_poll_for_messages_incoming_connection(self, mock_select, mock_socket):
        port = 6665
        queue = Queue()
        listener = Listener(port, queue)

        mock_select.return_value = [mock_socket()], [None], [None]
        mock_socket().accept.return_value = (mock_socket(), None)

        listener.poll_for_messages()

        # Checks that a new connection has been made and has been added to the list of input sockets
        self.assertTrue(len(listener.inputs) > 1)

    @patch('socket.socket')
    @patch('select.select')
    def test_poll_for_messages_incoming_message(self, mock_select, mock_socket):
        port = 6665
        queue = Queue()
        listener = Listener(port, queue)
        listener.server = None
        listener.inputs = [None, mock_socket()]

        mock_select.return_value = [mock_socket()], [None], [None]
        mock_socket().recv.return_value = (1023).to_bytes(4, 'big')

        listener.poll_for_messages()

        # Checks that the message has been added to the queue
        self.assertTrue(listener.queue.qsize() == 1)
        self.assertTrue(listener.queue.get() == 1023)

    @patch('socket.socket')
    @patch('select.select')
    def test_poll_for_messages_close_connection(self, mock_select, mock_socket):
        port = 6665
        queue = Queue()
        listener = Listener(port, queue)
        listener.server = None
        listener.inputs = [None, mock_socket()]

        mock_select.return_value = [mock_socket()], [None], [None]
        mock_socket().recv.return_value = None

        listener.poll_for_messages()

        # Checks that the disconnected socket has been removed from the input list
        self.assertTrue(len(listener.inputs) == 1)


class TestMachine(unittest.TestCase):
    global_time = time.time()
    logging.disable(logging.CRITICAL)

    @patch('clocks.gen_message')
    @patch.object(Machine, 'send_logical_clock')
    def test_no_message_operation_die_1(self, mock_send_logical_clock, mock_gen_message):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.conns = {1: 1, 2: 2}

        mock_gen_message.return_value = 1

        assert machine.no_message_operation(1) == 1

        mock_send_logical_clock.assert_called_once_with(1,)
        mock_gen_message.assert_called_once_with(
            EventType.SENT_ONE, 0, recip_id=1)

    @patch('clocks.gen_message')
    @patch.object(Machine, 'send_logical_clock')
    def test_no_message_operation_die_2(self, mock_send_logical_clock, mock_gen_message):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.conns = {1: 1, 2: 2}

        machine.no_message_operation(2)

        mock_send_logical_clock.assert_called_once_with(2)
        mock_gen_message.assert_called_once_with(
            EventType.SENT_ONE, 0, recip_id=2)

    @patch('clocks.gen_message')
    @patch.object(Machine, 'send_logical_clock')
    def test_no_message_operation_die_3(self, mock_send_logical_clock, mock_gen_message):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.conns = {1: 1, 2: 2}

        machine.no_message_operation(3)

        calls = [call(1), call(2)]
        mock_send_logical_clock.assert_has_calls(calls)
        mock_gen_message.assert_called_once_with(EventType.SENT_BOTH, 0)

    @patch('clocks.gen_message')
    @patch.object(Machine, 'send_logical_clock')
    def test_no_message_operation_die_else(self, mock_send_logical_clock, mock_gen_message):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.conns = {1: 1, 2: 2}

        machine.no_message_operation(4)

        mock_send_logical_clock.assert_not_called()
        mock_gen_message.assert_called_once_with(EventType.INTERNAL, 0)

    @patch('socket.socket')
    def test_send_logical_clock(self, mock_socket):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.send_logical_clock(mock_socket())
        mock_socket().send.assert_called_once_with((0).to_bytes(4, 'big'))

    @patch('socket.socket')
    def test_send_logical_clock_with_improper_logical_clock(self, mock_socket):
        machine_id = 0
        machine = Machine(self.global_time, machine_id)
        machine.logical_clock = -1
        self.assertRaises(
            OverflowError, machine.send_logical_clock, mock_socket)


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
    logging.disable(logging.NOTSET)

    def test_setup_logger(self):
        logger_name = 'test_logger'
        log_file = './logs/test_logger.log'
        setup_logger(logger_name)

        # assert that test.log file was created in directory
        self.assertTrue(os.path.exists(log_file))

    def tearDown(self):
        logging.shutdown()
        os.remove("logs/test_logger.log")


if __name__ == '__main__':
    unittest.main()
