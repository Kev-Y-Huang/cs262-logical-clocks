import logging
import time
import socket
import random
import multiprocessing
from multiprocessing import Process
from utils import setup_logger, gen_log_message


def send_message(port, logical_clock):
    '''
    This function should send a message to the host and port specified.
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    s.send(logical_clock.to_bytes(4, 'big'))
    s.close()
    
            
class Listener():
    def __init__(self, host, port, queue):
        self.host = host
        self.port = port
        self.queue = queue

    def listen(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)

        while True:
            client, _ = self.socket.accept()
            data = client.recv(1024)
            data = int.from_bytes(data, 'big')
            if data:
                self.queue.put(data)
            client.close()
    
    def close(self):
        self.socket.close()
        

def machine_process(global_time: time, machine_id: int, listener: Listener, sending_port_1: int, sending_port_2: int, total_run_time: int):
    '''
    If there is a message in the message queue for the machine (remember, the
    queue is not running at the same cycle speed) the virtual machine should:
    1. take one message off the queue
    2. update the local logical clock
    3. write in the log that it received
        a. a message
        b. the global time (gotten from the system)
        c. the length of the message queue
        d. and the logical clock time.
    If there is no message in the queue, the virtual machine should generate a
    random number in the range of 1-10, and
    * if the value is 1, send to one of the other machines a message that is
      the local logical clock time, update it's own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is 2, send to the other virtual machine a message that is
      the local logical clock time, update it's own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is 3, send to both of the other virtual machines a message
      that is the logical clock time, update it's own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is other than 1-3, treat the cycle as an internal event;
      update the local logical clock, and log the internal event, the system
      time, and the logical clock value.
    '''
    log_name = f'{global_time}_machine_{machine_id}'
    setup_logger(log_name, f'./logs/{global_time}_machine_{machine_id}.log')
    process_log = logging.getLogger(log_name)

    rate = random.randint(1, 6)
    logical_clock = 0 
    internal_start_time = time.time()
    for _ in range(total_run_time):
      for _ in range(rate):
          internal_start_time = time.time()
          logical_clock += 1
          if not listener.queue.empty():
              logical_clock_value_received = listener.queue.get()
              process_log.info(gen_log_message(0, logical_clock, queue_len=listener.queue.qsize()))
              # print(f"Machine {listener.port} received message with clock value of {logical_clock_value_received} at time {logical_clock}")
              logical_clock = max(logical_clock, logical_clock_value_received) + 1

          diceRoll = random.randint(1, 10)
          if diceRoll == 1:
              # print(f"Machine {listener.port} sending message to machine 1 at time {logical_clock}")
              recip_id = (machine_id + 1) % 3
              process_log.info(gen_log_message(1, logical_clock, recip_id=recip_id))
              send_message(sending_port_1, logical_clock)
          elif diceRoll == 2:
              # print(f"Machine {listener.port} sending message to machine 2 at time {logical_clock}")
              recip_id = (machine_id + 2) % 3
              process_log.info(gen_log_message(1, logical_clock, recip_id=recip_id))
              send_message(sending_port_2, logical_clock)
          elif diceRoll == 3:
              # print(f"Machine {listener.port} sending message to both machines at time {logical_clock}")
              process_log.info(gen_log_message(3, logical_clock))
              send_message(sending_port_1, logical_clock)
              send_message(sending_port_2, logical_clock)
          else:
              # print(f"Machine {listener.port} internal event at time {logical_clock}")
              process_log.info(gen_log_message(4, logical_clock))

          time.sleep(1.0/rate - (time.time() - internal_start_time))


if __name__ == "__main__":
    try:
        # initialize 3 sockets
        ports = [6666, 7777, 9999]

        total_run_time = 10

        listeners = []
        global_time = time.time()

        m = multiprocessing.Manager()

        for i in range(3):
            listeners.append(Listener('127.0.0.1', ports[i], m.Queue()))
            Process(target = listeners[i].listen).start()

        for i in range(3):
            Process(target = machine_process, args = (global_time, i, listeners[i], ports[(i + 1) % 3], ports[(i + 2) % 3], total_run_time)).start()

        time.sleep(total_run_time + 1)

        for i in range(3):
            listeners[i].close()
    except KeyboardInterrupt:
        print('Interrupted')
        for i in range(3):
            listeners[i].close()