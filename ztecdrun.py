#!/usr/bin/env python

"""ZTE MF636 CD Run enable / disable

EnhancedSerial class from : http://pyserial.sourceforge.net/
part of pyserial (http://pyserial.sf.net)  (C)2002 cliechti@gmx.net
"""

OPTIONS=('enable', 'disable')
TRANSLATE=dict(enable=9, disable=8)
COMMANDS=(('ATZ\r', 'OK'), ('AT+ZOPRT=5\r', 'OK'), ('AT+ZCDRUN={val1}\r', '):1'))

import sys
from serial import Serial

class EnhancedSerial(Serial):
    def __init__(self, *args, **kwargs):
        #ensure that a reasonable timeout is set
        timeout = kwargs.get('timeout',0.1)
        if timeout < 0.01: timeout = 0.1
        kwargs['timeout'] = timeout
        Serial.__init__(self, *args, **kwargs)
        self.buf = ''
        
    def readline(self, maxsize=None, timeout=1):
        """maxsize is ignored, timeout in seconds is the max time that is way for a complete line"""
        tries = 0
        while 1:
            self.buf += self.read(512)
            pos = self.buf.find('\n')
            if pos >= 0:
                line, self.buf = self.buf[:pos+1], self.buf[pos+1:]
                return line
            tries += 1
            if tries * self.timeout > timeout:
                break
        line, self.buf = self.buf, ''
        return line

    def readlines(self, sizehint=None, timeout=1):
        """read all lines that are available. abort after timout
        when no more data arrives."""
        lines = []
        while 1:
            line = self.readline(timeout=timeout)
            if line:
                lines.append(line)
            if not line or line[-1:] != '\n':
                break
        return lines

    def write_read(self, cmd):
        self.write(cmd)
        return [i.strip() for i in s.readlines()]

if __name__=='__main__':
    if len(sys.argv) < 3 or sys.argv[2] not in OPTIONS:
        print 'Usage: {0} [port] [{1}]'.format(sys.argv[0], '/'.join(OPTIONS))
        print 'Example to reenable CDRUN: {0} /dev/ttyUSB1 enable'.format(sys.argv[0])
        exit(1)
    s = EnhancedSerial(sys.argv[1], timeout=0.2)

    for cmd in COMMANDS:
        mycmd = cmd[0].format(val1=TRANSLATE[sys.argv[2]])
        output = s.write_read(mycmd)
        if output[0] != mycmd.strip():
            print 'Write failed\n Sent: {0}\n Received: {1}'.format(mycmd, output[0])
            exit(1)
        if output[1].find(cmd[1]) == -1:
            print 'Read failed\n Sent: {0}\n Expected: {1}\n Received: {2}'.format(mycmd, cmd[1], output[1])
            exit(1)
        print '{0}: {1}'.format(mycmd.strip(), output[1])
    print 'SUCCESS'
    exit(0)
