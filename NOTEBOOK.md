# Engineering Notebook

## Analysis of results

[Presentation slides](https://docs.google.com/presentation/d/1wH0nhtxOqBf24_KemDlondbWPpwuR5HtyjgaH2j-0X0/edit?usp=sharing)

We see a few trends from our experimental results:

- When clock rates are the same, the system behaves as expected. The experimental values for the logical clock were very close to the expected values.
- *Queue size*: When clock rates differ, the slowest clock rate typically gets the largest queue size, and the fastest clock rate typically gets the smallest queue size. The queue size grows continuously for the slower clock and never seems to clear. This makes sense because the slowest clock rate will process things slower as it ticks slower, and the fastest clock rate will have the smallest logical clock differences because of out fast it is going. 
- *Logical clock jumps*: When the clock rates differ, there are more jumps in the clock ticks for slower clocks rates. This makes sense because the slower clock rates will receive more messages from faster moving clocks and thus have larger logical clock differences between machine operations, therefore leading to larger jumps in the clock ticks.
- *Drift*: Slower clocks experience more drift compared when they are in a system with machines with faster clocks. The experimental clock rates for slower clocks in systems with faster clocks were a lot farther away from their expected clock rate compared to the faster clock rates.
- When clock rates were different but close together, the numbers were closer to expected. Larger discrepancies were found when the range between the min and max clock rate of the machines was larger.
- The fastest machine almost never needs to update its logical clock, it always grows in increments of 1 per tick. 

Delving into each of the five experiments in more detail:

In Experiment 1, the machines have different actual clock rates, resulting in different logical clock differences.

Machine 0 has the slowest clock rate of 1.000, while Machine 2 has the fastest clock rate of 6.000, and Machine 1 had a clock rate of 3.000. We see that Machine 0's experimental clock rate (0.002) drifted very far from the expected clock rate (1.000), while Machine 2's experimental clock rate (0.170) was very close to its true value (0.167) and Machine 1's (0.268 experimental, 0.333 true) was in between the two in terms of accuracy. 

We also see that Machine 0 had to update is logical clock in much larger increments, with an average logical clock difference of 3.869 between machine operations. Not surprisingly, Machine 1 had an average of 1.953, which was inbetween Machine 0 and Machine 2's average logical clock update of 1.000.


In Experiment 2, the machines have different actual clock rates, resulting in different logical clock differences. However, this time, the clock rates were closer to their true expected values compared to Experiment 1.

Within this experiment, Machine 0's experimental clock rate (0.392) drifted farthest from its expected clock rate (0.500), while Machine 2's experimental clock rate (0.254) was very close to its true value (0.250) and again Machine 1's (0.303 experimental, 0.333 true) was in between the two in terms of accuracy. 

Similar to Experiment 1, Machine 0 had to update is logical clock in much larger increments, with an average logical clock difference of 1.980 between machine operations. Machine 1 had an average increase in logical clock per tick of 1.314, and again Machine 2 had an average of 1.000. Notice again Machine 2 had a tick of 1, and also how these increments are smaller than Experiment 1, which makes sense because the clock rates are closer together.

In Experiment 3, all machines have the same actual clock rate, resulting in the same logical clock differences. In this experiment, we saw behavior from our machines that was expected. The experimental clock rates were all 0.337, which were very close to their expected clock rates of 0.333, and we saw no large jumps in the logical clock values for any machine. We also saw how all of the logical clocks increased on average by 1.000 per tick, which was expected since all of the machines had the same clock rate.

In Experiment 4, two of the machines (Machine 0 and Machine 2) have the same clock rates while a third (Machine 1) had a much slower clock rate. This resulted in different logical clock differences between the faster two and the slower third machine, but not between the two faster machines themselves.

Within this experiment, Machine 1's experimental clock rate (0.002) drifted farthest from its expected clock rate (1.000), while Machine 0's and 2's experimental clock rate were the same and (0.204) were very close to their true value (0.200). We also saw that the two faster machines' logical clocks increased on average by 1 per tick, while the slower machine's logical clock increased on average by 2.758 per tick. 

Finally, in Experiment 5, the randomly generated numbers gave us two of the machines (Machine 1 and Machine 2) have the same clock rates while a third (Machine 0) had a faster clock rate. However, this time the numbers were closer together (clock rates of 2, 1, and 1). Within this experiment, Machine 1 and 2's experimental clock rates (0.003) drifted farther from its expected clock rate (1.000), while Machine 0's experimental clock rate was the same and (0.504) was very close to its true value (0.500). Similar to experiment 4, we saw that the machines with the same clock rate saw the same average increase in their logical clocks per tick. Here, the slower machines increased on average by 1.980 per tick, while the faster machine's logical clock increased on average by 1.000 per tick. 


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
