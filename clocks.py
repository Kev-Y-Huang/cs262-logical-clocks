def machine_process():
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
      the local logical clock time, update it’s own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is 2, send to the other virtual machine a message that is
      the local logical clock time, update it’s own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is 3, send to both of the other virtual machines a message
      that is the logical clock time, update it’s own logical clock, and update
      the log with the send, the system time, and the logical clock time.
    * if the value is other than 1-3, treat the cycle as an internal event;
      update the local logical clock, and log the internal event, the system
      time, and the logical clock value.
    '''
