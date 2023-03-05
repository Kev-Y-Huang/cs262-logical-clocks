import datetime
import logging
from enum import Enum


class EventType(Enum):
    RECEIVED = 0
    SENT_ONE = 1
    SENT_BOTH = 2
    INTERNAL = 3


def setup_logger(name: str, log_file: str, level: int = logging.INFO):
    '''
    Set up a logger to write to a file and to the console.
    '''
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')

    # Set up the file handler for writing to the log file
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)

    # Set up the stream handler for printing to the console
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


def gen_message(event_type: EventType, clock_time: int, received_time: int = 0, queue_len: int = 0, recip_id: int = 0) -> str:
    '''
    Write in the log that it received
        1. a message
        2. the system time
        3. the length of the message queue
        4. and the logical clock time.
    If the value is 1, update the log with the send, the system time, and the
        logical clock time.
    If the value is 2, update the log with the send, the system time, and the
        logical clock time.
    If the value is 3, update the log with the send, the system time, and the
        logical clock time.
    If the value is other than 1-3, update the log with the internal event,
        the system time, and the logical clock value.
    '''
    # Get the system and logical clock time and format it
    system_time = datetime.datetime.now()
    time_message = f"(System Time {system_time} - Logical Clock Time {clock_time})"

    # Generate the log message based on the event type
    if event_type == EventType.RECEIVED:
        return f"{time_message} Received a message with logical time {received_time}. Current queue length is {queue_len}."
    elif event_type == EventType.SENT_ONE:
        return f"{time_message} Sent a message to machine {recip_id}."
    elif event_type == EventType.SENT_BOTH:
        return f"{time_message} Sent a message to both other machines."
    else:
        return f"{time_message} Internal event occurred."
