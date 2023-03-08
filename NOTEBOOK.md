# Engineering Notebook

## Key Decisions/Justifications and Issues

### Using a server to spin up three separate processes:

We decided to initiate a single server to start three separate virtual machine processes that send messages to each other. 

The central server will not handle of any the message sending/receiving -- this was directly handled by the virtual machines themselves. This approach isn't scalable, as in real life we would likely want separate servers to host each of the machines for reliability and load, but it will work for our purposes in this assignment. This should still simulate the same conditions as if we had separate servers for each of the machines, since we are spinning up three separate processes.

### OS Issues:

Over the course of this project, we ran into multiple issues with running our code on Windows and MacOS. Our initial code worked fine on Windows, but when we tried to run it on MacOS, we ran into `ConnectionRefusedError: [Errno 61] Connection refused` errors. These issues were resolved by moving code in/out of the `init` functions for our classes, which was interesting to see. The code should work properly on both Windows and MacOS.

## Working Log

### March 7th

We ran the experiment for 3 different set conditions for our clock rates on each machine to ensure that we simulated different conditions. We also ran two experiments with a randomly generated clock rates.

#### Experiment 1 Rates:

* Machine 0: 1 tick/second
* Machine 1: 3 tick/second
* Machine 2: 6 tick/second

#### Experiment 2 Rates:

* Machine 0: 2 tick/second
* Machine 1: 3 tick/second
* Machine 2: 4 tick/second

#### Experiment 3 Rates:

* Machine 0: 3 tick/second
* Machine 1: 3 tick/second
* Machine 2: 3 tick/second

#### Experiment 4 Rates (randomly generated):

* Machine 0: 5 tick/second
* Machine 1: 1 tick/second
* Machine 2: 5 tick/second

#### Experiment 5 Rates (randomly generated):

* Machine 0: 1 tick/second
* Machine 1: 2 tick/second
* Machine 2: 1 tick/second

### March 6th

We've decided to switch to the `threading` module because of issues with the `multiprocessing` module, since we weren't able to quit out of the program using `Ctrl+C` to stop it if needed. This will be very similar to what we we had before - since we are still spinning up three separate processes for our virtual machines. 

Each of the machines will function as a server and a client, and will be able to send messages to each other. The server will be listening for messages from the client, and the client will be sending messages to the server.

### March 5th

We've decided to initiate a server to start three separate virtual machine processes that send messages to each other. The central server will not handle of any the message sending/receiving, as this will directly be handled by the virtual machines themselves. This isn't scalable, as in real life we would want separate servers to host each of the machines, but it will work for our purposes. However, this should simulate the same conditions as if we had separate servers for each of the machines, since we are spinning up three separate processes.

To send messages between the machines, we will be encoding the messages using big-endian, and then sending them as bytes.

We will likely be using the `multiprocessing` module to create the processes, and using the `socket` module to create the server and the sockets for the virtual machines to communicate with each other.

### March 1st

Started the code today. We've decided to run the code for a specific amount of time so we can test it under specific conditions, and then also use threading so we can run multiple processes at once. 

For each of the (virtual) machines, we will need to have:
* Logical clock, running at clock rate randomly generated between 1 and 6 for the number of clock ticks per second
* Connect to each of the other virtual machines
    * Probably using sockets
* Open a file for logging
* Have a queue to hold incoming messages
* Should listen to socket for messages
