import logging
import random
import select
import socket
import time
from multiprocessing import Event, Manager, Process
from queue import Queue

from utils import EventType, gen_log_message, setup_logger


def send_message(port: int, logical_clock: int):
    '''
    This function should send a message to the host and port specified.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    # Send the logical clock time using big-endian encoding
    s.send(logical_clock.to_bytes(4, 'big'))
    s.close()


class Listener(Process):
    """
    Array with associated photographic information.

    ...

    Attributes
    ----------
    port : int
        Exposure in seconds.
    queue : Queue
        Exposure in seconds.
    host : str
        Exposure in seconds.

    Methods
    -------
    run()
        Represent the photo in the given colorspace.
    shutdown()
        Change the photo's gamma exposure.

    """
    def __init__(self, host, port, queue):
        Process.__init__(self)
        self.port = port
        self.queue = queue
        self.exit = Event()

    def run(self):
        # Create a socket and bind it to the host and port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', self.port))
        self.server.listen(5)

        # Continuously listen for messages and add them to the queue
        while not self.exit.is_set():
            # Use select to poll for messages
            inputs = [self.server]
            read_sockets, write_socket, error_socket = select.select(
                inputs, [], inputs, 0.1)
            for sock in read_sockets:
                client, _ = sock.accept()
                data = client.recv(1024)
                # Read in the data as a big-endian integer
                data = int.from_bytes(data, 'big')
                if data:
                    self.queue.put(data)
                client.close()

        self.socket.close()
        print("Exited")

    def shutdown(self):
        print("Shutdown initiated")
        self.exit.set()


def machine_process(global_time: time, machine_id: int, queue: Queue, ports: list[int], total_run_time: int):
    """
    Virtual machine process that sends and ingests messages from other virtual machines.

    Parameter
    ---------
    global_time : time
        Global time for which the process was started at.
    machine_id : int
        Id of the machine process.
    queue : Queue
        Queue of all messages sent to this machine process.
    ports : list[int]
        List of ports for all machine processes.
    total_run_time : int
        Global time for which the process was started at.
    """
    # Setup logger for this machine process
    log_name = f'{global_time}_machine_{machine_id}'
    setup_logger(log_name, f'./logs/{global_time}_machine_{machine_id}.log')
    log = logging.getLogger(log_name)

    # Set up clock rate and logical clock
    rate = random.randint(1, 6)
    logical_clock = 0

    for _ in range(total_run_time):
        for _ in range(rate):
            internal_start_time = time.time()
            logical_clock += 1

            # Check if there is a message in the queue to ingest
            if not queue.empty():
                received_time = queue.get()
                queue_len = queue.qsize()
                logical_clock = max(logical_clock, received_time)
                log.info(gen_log_message(
                    EventType.RECEIVED, logical_clock, received_time=received_time, queue_len=queue_len))
            else:
                # Generate a random number to determine what to do
                diceRoll = random.randint(1, 10)
                # Send a message to one machine
                if diceRoll == 1:
                    recip_id = (machine_id + 1) % 3
                    send_message(ports[recip_id], logical_clock)
                    log.info(gen_log_message(
                        EventType.SENT_ONE, logical_clock, recip_id=recip_id))
                # Send a message to the other machine
                elif diceRoll == 2:
                    recip_id = (machine_id + 2) % 3
                    send_message(ports[recip_id], logical_clock)
                    log.info(gen_log_message(
                        EventType.SENT_ONE, logical_clock, recip_id=recip_id))
                # Send a message to both machines
                elif diceRoll == 3:
                    for i in range(2):
                        recip_id = (machine_id + i) % 3
                        send_message(recip_id, logical_clock)
                        
                    log.info(gen_log_message(
                        EventType.SENT_BOTH, logical_clock))
                # Treat as an internal event
                else:
                    log.info(gen_log_message(
                        EventType.INTERNAL, logical_clock))

            # Sleep for the remainder of the cycle
            time.sleep(1.0/rate - (time.time() - internal_start_time))


if __name__ == "__main__":
    try:
        # initialize 3 sockets
        ports = [6666, 7777, 9999]

        # Setup state for the machine processes
        listeners = []
        queues = []
        m = Manager()
        global_time = time.time()

        total_run_time = 3

        for i in range(3):
            queues.append(m.Queue())
            listeners.append(Listener(ports[i], queues[i]))
            listeners[i].start()

        for i in range(3):
            Process(target=machine_process, args=(global_time, i, queues[i], ports, total_run_time)).start()

        time.sleep(total_run_time + 1)

        for i in range(3):
            listeners[i].shutdown()
    except KeyboardInterrupt:
        print('Interrupted')
        for i in range(3):
            listeners[i].shutdown()
