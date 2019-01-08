uCommander - The Micro Commander
================================

This library simplifies interfacing with code written on
a microprocessor like an Arduino, Teensy, or similar devices
via serial communication.

The Python code is designed to work with the 
[uCommander Arduino library](https://github.com/aeetos/ucommander).

Basic CLI Usage
---------------
First, install the ucommander Python library with pip, ideally in a
virtual environment.
```
$ cd myproject
$ python -m venv venv
$ pip install ucommander
```
After you have the `ucommander` library installed in your Python environment,
ensure your microprocessor is attached to your host and determine what
serial port you will use to communicate with it. 

The `listports` command can help with this.
```
$ python -m ucommander listports
Attempting to enumerate serial ports...
/dev/cu.SOC - n/a
/dev/cu.usbmodem - USB Serial
```
Once you know the serial port, run the discover command to learn which
commands you can run and what arguments they require.
```
$ python -m ucommander -p /dev/cu.usbmodem discover
Available commands:
 ledIfPi        FLOAT(4)
```
Finally, run the commands, providing any required arguments after the command
name.
```
$ python -m ucommander -p /dev/cu.usbmodem ledIfPi 3.14
$ python -m ucommander -p /dev/cu.usbmodem ledIfPi 3.24
```




--------------------------------------------------------------
Copyright (C) 2019 Mark A Kendrick  
