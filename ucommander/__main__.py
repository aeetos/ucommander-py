"""ucommander/__main__.py

Provides a command line interface to a device on a serial port.

Copyright (C) 2019 Mark A Kendrick
code at ikend dot com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

from ucommander import uCommander
import argparse

parser = argparse.ArgumentParser(description='Send commands to a microprocessor.')
parser.add_argument('-b','--baudrate', default=115200, type=int,
                    help='Serial baud rate (defaults to 115200)')
parser.add_argument('-p','--serialport', default='?', 
                    help='Serial port of connected device, or "?" to list ports')
parser.add_argument('command', default='discover', 
                    help='Name of the command to run (try "listports" or "discover")')
parser.add_argument('parameter', nargs='*', default='',
                    help='Optional command parameters; use key=value pairs for named args')
args = parser.parse_args()
if(args.serialport=="?"):
    print('Attempting to enumerate serial ports...')
    from serial.tools import list_ports
    for port in list_ports.comports():
        print(port)
    exit(0)

uCmd = uCommander(args.serialport, args.baudrate)
uCmd.discover()
if(args.command=="discover"):
    print('Available commands:')
    for cmd in uCmd.commands.values():
        print(' '+str(cmd))
    exit(0)

try:
    command = uCmd.commands[args.command]
    posargs = []
    kwargs = {}
    for param in args.parameter:
        parts = param.split('=')
        if(len(parts)==2):
            kwargs[parts[0]] = float(parts[1]) if '.' in parts[1] else int(parts[1])
        else:
            posargs.append(float(parts[0]) if '.' in parts[0] else int(parts[0]))
    is_valid, error = command.validate(*posargs, **kwargs)
    if(not is_valid):
        print(error)
        exit(1)
    result = command.run(*posargs, **kwargs)
    exit(0)
except KeyError:
    print('ERROR: unknown command {}'.format(args.command))
    exit(1)