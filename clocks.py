import logging
import random
import select
import socket
import time
from multiprocessing import Event, Manager, Process

from utils import EventType, gen_message, setup_logger


PORTS = [6666, 7777, 9999]


def send_message(port: int, logical_clock: int):
    """
    This function should send a message to the host and port specified.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    # Send the logical clock time using big-endian encoding
    s.send(logical_clock.to_bytes(4, 'big'))
    s.close()


class Listener(Process):
    """
    Listener process that listens for messages from other virtual machines.
    ...

    Attributes
    ----------
    port : int
        Port for the listener process.
    queue : Queue
        Queue for all incoming messages.
    exit : Event
        Exposure in seconds.

    Methods
    -------
    run()
        Represents the listener process activity.
    shutdown()
        Initiates the shutdown of the listener process.

    """

    def __init__(self, port, queue):
        Process.__init__(self)
        self.port = port
        self.queue = queue
        self.exit = Event()

    def run(self):
        # Create a socket and bind it to the host and port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', self.port))
        self.server.listen(10)

        inputs = [self.server]

        # Continuously listen for messages and add them to the queue
        while not self.exit.is_set():
            # Use select to poll for messages
            read_sockets, _, _ = select.select(
                inputs, [], inputs, 0.1)
            for sock in read_sockets:
                if sock == self.server:
                    client, _ = sock.accept()
                    inputs.append(client)
                else:
                    data = sock.recv(1024)
                    if data:
                        # Read in the data as a big-endian integer
                        data = int.from_bytes(data, 'big')
                        if data:
                            self.queue.put(data)

        for sock in inputs:
            sock.close()

        print("Exited")

    def shutdown(self):
        print("Shutdown initiated")
        self.exit.set()


def machine_process(global_time: time, machine_id: int, total_run_time: int):
    """
    Virtual machine process that sends and ingests messages from other virtual machines.

    Parameters
    ----------
    global_time : time
        Global time for which the process was started at.
    machine_id : int
        Id of the machine process.
    total_run_time : int
        Amount of seconds the process should run for.

    """
    # Start listener process for this machine process
    queue = Manager().Queue()
    listener = Listener(PORTS[machine_id], queue)
    listener.start()

    # Setup logger for this machine process
    log_name = f'{global_time}_machine_{machine_id}'
    setup_logger(log_name, f'./logs/{global_time}_machine_{machine_id}.log')
    log = logging.getLogger(log_name)

    # Set up clock rate and logical clock
    logical_clock = 0
    rate = random.randint(1, 6)
    log.info(f'Clock rate: {rate}')

    # Set up connections to other machines
    conns = {}
    for i in range(2):
        recip_id = (machine_id + i + 1) % 3
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(('127.0.0.1', PORTS[recip_id]))
        conns[recip_id] = conn

    for _ in range(total_run_time):
        for _ in range(rate):
            internal_start_time = time.time()
            logical_clock += 1

            # Check if there is a message in the queue to ingest
            if not queue.empty():
                received_time = queue.get()
                queue_len = queue.qsize()
                logical_clock = max(logical_clock, received_time)
                log.info(gen_message(
                    EventType.RECEIVED, logical_clock, received_time=received_time, queue_len=queue_len))
            else:
                # Generate a random number to determine what to do
                diceRoll = random.randint(1, 10)
                # Send a message to one machine
                if diceRoll == 1:
                    recip_id = (machine_id + 1) % 3
                    conns[recip_id].send(
                        logical_clock.to_bytes(4, 'big'))
                    log.info(gen_message(
                        EventType.SENT_ONE, logical_clock, recip_id=recip_id))
                # Send a message to the other machine
                elif diceRoll == 2:
                    recip_id = (machine_id + 2) % 3
                    conns[recip_id].send(
                        logical_clock.to_bytes(4, 'big'))
                    log.info(gen_message(
                        EventType.SENT_ONE, logical_clock, recip_id=recip_id))
                # Send a message to both machines
                elif diceRoll == 3:
                    for conn in conns.values():
                        conn.send(logical_clock.to_bytes(4, 'big'))

                    log.info(gen_message(
                        EventType.SENT_BOTH, logical_clock))
                # Treat as an internal event
                else:
                    log.info(gen_message(
                        EventType.INTERNAL, logical_clock))

            # Sleep for the remainder of the cycle
            time.sleep(1.0/rate - (time.time() - internal_start_time))

    # Close all connections
    for conn in conns.values():
        conn.close()

    # Shutdown listener process
    listener.shutdown()


if __name__ == "__main__":
    # Setup state for the machine processes
    procs = []
    global_time = time.time()
    total_run_time = 3

    try:
        # Start machine processes
        for i in range(3):
            proc = Process(target=machine_process, args=(global_time, i, total_run_time))
            proc.start()
            procs.append(proc)

    except KeyboardInterrupt:
        print('Interrupted')
        for proc in procs:
            proc.shutdown()
