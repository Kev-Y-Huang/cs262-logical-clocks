import logging
import random
import select
import socket
import time
from queue import Queue
from threading import Event, Thread

from utils import EventType, gen_message, setup_logger

PORTS = [4444, 4445, 4446]


def send_message(port: int, logical_clock: int):
    """
    This function should send a message to the host and port specified.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    # Send the logical clock time using big-endian encoding
    s.send(logical_clock.to_bytes(4, 'big'))
    s.close()


class Listener(Thread):
    """
    Listener process that listens for messages from other virtual machines.
    ...

    Attributes
    ----------
    port : int
        Port for the listener process.
    queue : Queue
        Queue for all incoming messages.
    log : logging.Logger
        Logger for the virtual machine process.
    exit : Event
        Event that is set when the process should exit.
    server : socket.socket
        Socket for the listener process.

    Methods
    -------
    run()
        Represents the listener process activity.
    shutdown()
        Initiates the shutdown of the listener process.

    """

    def __init__(self, port: int, queue: Queue, log: logging.Logger):
        Thread.__init__(self)
        self.port = port
        self.queue = queue
        self.log = log
        self.exit = Event()

        # Create a socket and bind it to the host and port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', self.port))
        self.server.listen(10)

        # Add the server socket to the list of inputs
        self.inputs = [self.server]

    def run(self):
        # Continuously listen for messages and add them to the queue
        while not self.exit.is_set():
            # Use select to poll for messages
            read_sockets, _, _ = select.select(self.inputs, [], [], 0.1)
            for sock in read_sockets:
                if sock == self.server:
                    client, _ = sock.accept()
                    self.inputs.append(client)
                else:
                    data = sock.recv(1024)
                    if data:
                        # Read in the data as a big-endian integer
                        self.queue.put(int.from_bytes(data, 'big'))

        # Close all socket connections
        for sock in self.inputs:
            sock.close()

        print('Exited')

    def shutdown(self):
        print('Listener Shutdown Initiated')
        self.exit.set()


class Machine(Thread):
    """
    Virtual machine process that sends and ingests messages from other virtual machines.
    ...

    Attributes
    ----------
    machine_id : int
        Id of the machine process.
    total_run_time : int
        Amount of seconds the process should run for.
    logical_clock : int
        Logical clock time of the machine process.
    exit : Event
        Event that is set when the process should exit.
    log : logging.Logger
        Logger for the virtual machine process.
    rate : int
        Number of virtual machine cycles per second.

    Methods
    -------
    run()
        Represents the virtual machine process activity.
    shutdown()
        Initiates the shutdown of the virtual process.

    """
    
    def __init__(self, global_time: time, machine_id: int, total_run_time: int):
        Thread.__init__(self)
        self.machine_id = machine_id
        self.total_run_time = total_run_time
        self.logical_clock = 0
        self.exit = Event()

        # Setup logger for this machine process
        log_name = f'{global_time}_machine_{self.machine_id}'
        setup_logger(
            log_name, f'./logs/{global_time}_machine_{self.machine_id}.log')
        self.log = logging.getLogger(log_name)

        # Set up clock rate
        self.rate = random.randint(1, 6)
        self.log.info(f'Clock rate: {self.rate}')

    def run(self):
        # Start listener process for this machine process
        queue = Queue()
        listener = Listener(PORTS[self.machine_id], queue, self.log)
        listener.start()

        # Set up connections to other machines
        conns = {}
        for i in range(2):
            recip_id = (self.machine_id + i + 1) % 3
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(('127.0.0.1', PORTS[recip_id]))
            conns[recip_id] = conn

        for _ in range(self.total_run_time * self.rate):
            # Exit if the exit event flag is set
            if self.exit.is_set():
                break

            internal_start_time = time.time()
            self.logical_clock += 1

            # Check if there is a message in the queue to ingest
            if not queue.empty():
                received_time = queue.get()
                queue_len = queue.qsize()
                self.logical_clock = max(
                    self.logical_clock, received_time)
                self.log.info(gen_message(
                    EventType.RECEIVED, self.logical_clock, received_time=received_time, queue_len=queue_len))
            else:
                # Generate a random number to determine what to do
                diceRoll = random.randint(1, 10)
                # Send a message to one machine
                if diceRoll == 1:
                    recip_id = (self.machine_id + 1) % 3
                    conns[recip_id].send(
                        self.logical_clock.to_bytes(4, 'big'))
                    self.log.info(gen_message(
                        EventType.SENT_ONE, self.logical_clock, recip_id=recip_id))
                # Send a message to the other machine
                elif diceRoll == 2:
                    recip_id = (self.machine_id + 2) % 3
                    conns[recip_id].send(
                        self.logical_clock.to_bytes(4, 'big'))
                    self.log.info(gen_message(
                        EventType.SENT_ONE, self.logical_clock, recip_id=recip_id))
                # Send a message to both machines
                elif diceRoll == 3:
                    for conn in conns.values():
                        conn.send(
                            self.logical_clock.to_bytes(4, 'big'))

                    self.log.info(gen_message(
                        EventType.SENT_BOTH, self.logical_clock))
                # Treat as an internal event
                else:
                    self.log.info(gen_message(
                        EventType.INTERNAL, self.logical_clock))

            # Sleep for the remainder of the cycle
            time.sleep(1.0/self.rate -
                       (time.time() - internal_start_time))

        # Close all connections
        for conn in conns.values():
            conn.close()

        # Shutdown listener process
        listener.shutdown()

    def shutdown(self):
        print('Machine Shutdown Initiated')
        self.exit.set()


if __name__ == "__main__":
    # Setup state for the machine processes
    procs = []
    global_time = time.time()
    total_run_time = 10

    try:
        # Start machine processes
        for i in range(3):
            # proc = Process(target=machine_process, args=(
            #     global_time, i, total_run_time))
            proc = Machine(global_time, i, total_run_time)
            proc.start()
            procs.append(proc)

        time.sleep(total_run_time)

    except KeyboardInterrupt:
        print('Interrupted')
        for proc in procs:
            proc.shutdown()
