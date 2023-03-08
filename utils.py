import logging
from enum import Enum


class EventType(Enum):
    """
    Enum for the different types of events that can occur.
    """
    RECEIVED = 0
    SENT_ONE = 1
    SENT_BOTH = 2
    INTERNAL = 3


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup the logger for the machine process.
    ...

    Parameters
    ----------
    name : str
        The name of the logger.
    level : int
        The level of logging to record.

    Returns
    -------
    logging.Logger
        The logger object.

    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')

    # Set up the file handler for writing to the log file
    log_file = f'./logs/{name}.log'
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)

    # Set up the stream handler for printing to the console
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    return logger


def gen_message(event: EventType, clock_time: int, received_time: int = 0, queue_len: int = 0, recip_id: int = 0) -> str:
    """
    Generate a message to write to the log based on the event type.
    ...

    Parameters
    ----------
    event : EventType
        The type of event that occurred.
    clock_time : int
        The current logical clock time.
    received_time : int
        The logical clock time in the received message.
    queue_len : int
        The length of the message queue during message ingestion.
    recip_id : int
        The ID of the recipient that is being sent the message.

    Returns
    -------
    str
        The message to write to the log.

    """
    # Get the system and logical clock time and format it
    time_message = f"(Logical Clock Time {clock_time})"

    # Generate the log message based on the event type
    if event == EventType.RECEIVED:
        return f"{time_message} Received a message with logical time {received_time}. Current queue length is {queue_len}."
    elif event == EventType.SENT_ONE:
        return f"{time_message} Sent a message to machine {recip_id}."
    elif event == EventType.SENT_BOTH:
        return f"{time_message} Sent a message to both other machines."
    else:
        return f"{time_message} Internal event occurred."
