# CS 262 Logical Clocks

## Description

This is an implementations of a model of a small, asynchronous distributed
system with independent logical clocks for Design Exercise 2 for Harvard's
CS 262: Introduction to Distributed Computing.

## How to Run

### Installation

1. Clone the repository
2. Run the following command in the root directory of the project
```bash
python clocks.py
```
## Testing

1. Run the following command in the root directory of the project
```bash
python3 -m unittest tests.py
```

## Project Directory Structure
```
cs262-base-implementation
├───logs                # directory storing log files from different runs
├───.gitignore          # gitignore file
├───clocks.py           # Actual implementation
├───tests.py            # Unit tests
├───LICENSE             
├───NOTEBOOK.md         # Engineering Notebook
└───README.md           # README for cs262-base-implementation
```
