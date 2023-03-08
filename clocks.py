import random
import select
import socket
import time
from queue import Queue
from threading import Event, Thread

from utils import EventType, gen_message, setup_logger

# Constants
PORTS = [4444, 4445, 4446]
HOST = '127.0.0.1'
MAX_SIZE = 4
TOTAL_RUN_TIME = 3  # In seconds


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
    exit : Event
        Event that is set when the process should exit.
    server : socket.socket
        Socket for the listener process.

    Methods
    -------
    run()
        Continuously runs listener process activity until is shutdown.
    poll_for_messages()
        Polls for messages from other virtual machines.
    shutdown()
        Initiates the shutdown of the listener process.

    """

    def __init__(self, port: int, queue: Queue):
        Thread.__init__(self)
        self.port = port
        self.queue = queue
        self.exit = Event()

        # Create a socket and bind it to the host and port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((HOST, self.port))
        self.server.listen(10)

        # Add the server socket to the list of inputs
        self.inputs = [self.server]

    def run(self):
        # Continuously poll for messages while exit event has not been set
        while not self.exit.is_set():
            self.poll_for_messages()

        # Close all socket connections
        for sock in self.inputs:
            sock.close()
            self.inputs.remove(sock)

        print('Exited')

    def poll_for_messages(self):
        # Use select.select to poll for messages
        read_sockets, _, _ = select.select(self.inputs, [], [], 0.1)

        for sock in read_sockets:
            # If the socket is the server socket, accept as a connection
            if sock == self.server:
                client, _ = sock.accept()
                self.inputs.append(client)
            # Otherwise, read the data from the socket
            else:
                data = sock.recv(1024)
                if data:
                    # Read in the data as a big-endian integer
                    self.queue.put(int.from_bytes(data, 'big'))
                # If there is no data, then the connection has been closed
                else:
                    sock.close()
                    self.inputs.remove(sock)

    def shutdown(self):
        print('Listener Shutdown Initiated')
        self.exit.set()


class Machine(Thread):
    """
    Virtual machine process that sends and ingests messages from other virtual machines.
    ...

    Attributes
    ----------
    global_time : time
        Global time at which the simulation started.
    machine_id : int
        Id of the machine process.
    logical_clock : int
        Logical clock time of the machine process.
    conns : dict
        Dictionary of socket connections to other virtual machines.
    queue : Queue
        Queue for all incoming messages.
    exit : Event
        Event that is set when the process should exit.

    Methods
    -------
    run()
        Represents the virtual machine process activity.
    operation()
        Performs an operation dependent on the state of queue.
    no_message_operation(diceRoll: int)
        Performs an operation dependent on the dice roll value.
    send_logical_clock(conn: socket.socket)
        Sends the logical clock time to another socket connection.
    shutdown()
        Initiates the shutdown of the virtual process.

    """

    def __init__(self, global_time: time, machine_id: int):
        Thread.__init__(self)
        self.global_time = global_time
        self.machine_id = machine_id
        self.logical_clock = 0
        self.conns = {}
        self.queue = Queue()
        self.exit = Event()

    def run(self):
        # Setup logger for this machine process
        log = setup_logger(f'{self.global_time}_machine_{self.machine_id}')

        # Set up clock rate
        rate = random.randint(1, 6)
        log.info(f'Clock rate: {rate}')

        # Start a parallel listener process for this machine process
        listener = Listener(PORTS[self.machine_id], self.queue)
        listener.start()

        # Set up connections to other machines
        for i in range(2):
            recip_id = (self.machine_id + i + 1) % 3
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((HOST, PORTS[recip_id]))
            self.conns[recip_id] = conn

        # Continuously run the machine process activity until shutdown
        while not self.exit.is_set():
            internal_start_time = time.time()
            self.logical_clock += 1

            log.info(self.operation())

            # Sleep for the remainder of the cycle
            time.sleep(1.0/rate - (time.time() - internal_start_time))

        # Close all connections
        for conn in self.conns.values():
            conn.close()

        # Shutdown listener process
        listener.shutdown()

    def operation(self):
        # Check if there is a message in the queue to ingest
        if not self.queue.empty():
            received_time = self.queue.get()
            queue_len = self.queue.qsize()
            self.logical_clock = max(self.logical_clock, received_time)
            return gen_message(EventType.RECEIVED, self.logical_clock, received_time=received_time, queue_len=queue_len)
        else:
            # Generate a random number to determine what to do
            dice_roll = random.randint(1, 10)
            return self.no_message_operation(dice_roll)

    def no_message_operation(self, dice_roll: int):
        # Send a message to one of the machines
        if dice_roll == 1 or dice_roll == 2:
            # Determine which machine to send to
            recip_id = (self.machine_id + dice_roll) % 3
            self.send_logical_clock(self.conns[recip_id])
            return gen_message(EventType.SENT_ONE, self.logical_clock, recip_id=recip_id)
        # Send a message to both machines
        elif dice_roll == 3:
            for conn in self.conns.values():
                self.send_logical_clock(conn)

            return gen_message(EventType.SENT_BOTH, self.logical_clock)
        # Treat as an internal event
        else:
            return gen_message(EventType.INTERNAL, self.logical_clock)

    def send_logical_clock(self, conn: socket.socket):
        data = self.logical_clock.to_bytes(MAX_SIZE, 'big')
        conn.send(data)

    def shutdown(self):
        print('Machine Shutdown Initiated')
        self.exit.set()


if __name__ == "__main__":
    # Setup state for the machine processes
    procs = []
    global_time = time.time()

    try:
        # Start machine processes
        for i in range(3):
            proc = Machine(global_time, i)
            proc.start()
            procs.append(proc)

        time.sleep(TOTAL_RUN_TIME)
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        # Shutdown machine processes
        for proc in procs:
            proc.shutdown()
        for proc in procs:
            proc.join()
