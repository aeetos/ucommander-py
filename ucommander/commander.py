"""ucommander/commander.py

Provides core uCommander and uCommand objects.

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

import serial
from struct import pack
from collections import OrderedDict
from time import sleep
import re



class uCommander:
    CHAR    = 'c'
    SCHAR   = 'b'
    UCHAR   = 'B'
    SHORT   = 'h'
    USHORT  = 'H'
    INT     = 'i'
    UINT    = 'I'
    LONG    = 'l'
    ULONG   = 'L'
    FLOAT   = 'f'

    TYPEMETA = {
        CHAR:   ('CHAR',1),
        SCHAR:  ('SIGNED_CHAR',1),
        UCHAR:  ('UNSIGNED_CHAR',1),
        SHORT:  ('SIGNED_SHORT_INT',2),
        USHORT: ('UNSIGNED_SHORT_INT',2),
        INT:    ('SIGNED_INT',4),
        UINT:   ('UNSIGNED_INT',4),
        LONG:   ('SIGNED_LONG',4),
        ULONG:  ('UNSIGNED_LONG',4),
        FLOAT:  ('FLOAT',4),
    }

    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        self._meta = ''
        self._cmds = OrderedDict()

    def discover(self):
        if(self._meta==''):
            self.serial.open()
            self.serial.write([0xFF])
            sleep(0.05)
            self._meta = self.serial.read(self.serial.inWaiting())
            self.serial.close()
        pattern = re.compile(b'(\w*)\((\w*)(?:\|?)((\w,?)*)\)')
        for cmd in self._meta.split(b'\n'):
            result = pattern.search(cmd)
            if result:
                cmdname, argtypes, argnames = result.groups()[0:3]
                self.add_command(cmdname.decode("ascii"), argnames.decode("ascii"), argtypes.decode("ascii"))
        
    
    def add_command(self, cmdname, argnames='', argtypes=''):
        if cmdname in self._cmds:
            raise uCmdDuplicateCmd
        self._cmds[cmdname] = uCommand(self, len(self._cmds), cmdname, argnames, argtypes)
    
    def run_command(self, cmdname, *args, **kwargs):
        try:
            self._cmds[cmdname].run(*args, **kwargs)
        except KeyError:
            raise uCmdNotFound
    
    @property
    def commands(self):
        return self._cmds
    
    def __getattr__(self, name):
        return self._cmds[name]




class uCommand:
    def __init__(self, commander, id, name, argnames='', argtypes=None, response_timeout=0):
        self.commander = commander
        self._id = id
        self._name = name
        self._response_timeout = response_timeout
        self._response = bytearray()
        if not argnames or argnames=='':
            self._argnames = None
        else:
            self._argnames = argnames.split(',')            
        self._argtypes = argtypes
    
    def __str__(self):
        meta = self._name
        meta += '\t'
        if self._argtypes:
            typemeta = []
            for i in range(0,len(self._argtypes)):
                if self._argnames:
                    argname = self._argnames[i] + ':'
                else:
                    argname = ''
                typemeta.append('{0}{1}({2})'.format(argname, *uCommander.TYPEMETA[self._argtypes[i]]))
            meta += ', '.join(typemeta)
        return meta
    
    def document(self):
        self.__doc__ = 'Runs the {} command on the device at port {}'.format(self._name, self.commander.serial.port)
        self.__doc__ += '\n\n'
        if self._argtypes:
            self.__doc__ += 'Parameters\n----------\n'
            for i in range(0,len(self._argtypes)):
                self.__doc__ += ' : ' + self._argtypes[i] + '\n'
        self.__doc__ += '\n'

    def run(self, *args, **kwargs):
        packet = bytearray([self._id])
        arglist = self._build_arglist(*args, **kwargs)
        if(self._argtypes):
            packet.extend(pack('<'+self._argtypes, *arglist))
        self.commander.serial.open()
        self.commander.serial.write(packet)
        if(self._response_timeout):
            sleep(self._response_timeout)
            self.response = self.commander.serial.read(self.commander.serial.inWaiting())
        self.commander.serial.close()
        return self._response

    def _build_arglist(self, *args, **kwargs):
        """Build an array of argument values."""
        arglist = []
        if(self._argtypes):
            for i in range(0,len(self._argtypes)):
                try:
                    arglist.append(args[i])
                except IndexError:
                    arglist.append(0)
                if(kwargs):
                    try:
                        arglist[i] = kwargs[self._argnames[i]]
                    except KeyError:
                        pass
        return arglist

    def validate(self, *args, **kwargs):
        argcount = len(args)+len(kwargs)
        if(argcount != len(self._argtypes)):
            return (
                False,
                'Wrong argument count: expected {0} (got {1})'.format(len(self._argtypes),argcount)
            )
        if(len(kwargs) and len(self._argnames)):
            expected = set(self._argnames)
            received = set(kwargs.keys())
            if(expected != received):
                return (
                    False,
                    'Unknown argument name(s): {}}'.format(','.join(received-expected))
                )
        
        return (True,'')
    
    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)



class uCmdNotFound(Exception):
    pass

class uCmdDuplicateCmd(Exception):
    pass


