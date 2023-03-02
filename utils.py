import datetime
import logging


def setup_logger(name: str, log_file: str, level: int = logging.INFO):
    '''
    Set up a logger to write to a file and to the console.
    '''
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')

    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


def gen_log_message(event_type: int, clock_time: int, recip_id: int = 0, queue_len: int = 0) -> str:
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
    system_time = datetime.datetime.now()
    time_message = f"(System Time {system_time} - Logical Clock Time {clock_time})"

    if event_type == 0:
        return f"{time_message} Received a message. Current queue length is {queue_len}."
    elif event_type == 1 or event_type == 2:
        return f"{time_message} Sent a message to {recip_id}."
    elif event_type == 3:
        return f"{time_message} Sent a message to both other machines."
    else:
        return f"{time_message} Internal event occurred."
