#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

import serial
import re
import time

#class ReadLine:
#    def __init__(self, s):
#        self.buf = bytearray()
#        self.s = s
#    
#    def readline(self):
#        i = self.buf.find(b"\n")
#        if i >= 0:
#            r = self.buf[:i+1]
#            self.buf = self.buf[i+1:]
#            return r
#        while True:
#            i = max(1, min(2048, self.s.in_waiting))
#            data = self.s.read(i)
#            i = data.find(b"\n")
#            if i >= 0:
#                r = self.buf + data[:i+1]
#                self.buf[0:] = data[i+1:]
#                return r
#            else:
#                self.buf.extend(data)

ALLOWED_TAGS = ["2391729211"]
COL_GREEN = "\x1b[38;5;2m"
COL_RED = "\x1b[38;5;1m"
COL_RESET = "\033[0m"

def process_rfid(reader_line):
    #print(f"reader_line={reader_line}")
    match_process = re.match(string=reader_line, pattern=r"\. rfid_process\.sh (\d+)")
    match_write = re.match(string=reader_line, pattern=r"\. rfid_write\.sh (\d+)")
    if match_process:
        tag = match_process.group(1)
        #print(f"Tag to process: {tag}")
        validate(tag)
    elif match_write:
        tag = match_write.group(1)
        #print(f"Tag to allow: {tag}")
        allow_tag(tag)

def allow_tag(tag):
    ALLOWED_TAGS.append(tag)
    print(f"New allowed tag list: {ALLOWED_TAGS}")

def validate(tag):
    if tag in ALLOWED_TAGS:
        print(f"{COL_GREEN}ACCESS GRANTED!{COL_RESET}")
    else:
        print(f"{COL_RED}ACCESS DENIED!{COL_RESET}")

if __name__ == '__main__':
    
    tty_dev = "/dev/ttyUSB0"
    print('Running. Press CTRL-C to exit.')
    with serial.Serial(tty_dev, 9600, timeout=1) as arduino:
        #rl = ReadLine(arduino)
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print("{} connected!".format(arduino.port))
            try:
                while True:
                    #cmd=input("Enter command : ")
                    #arduino.write(cmd.encode())
                    #time.sleep(0.1) #wait for arduino to answer
                    while arduino.inWaiting()==0: pass
                    if  arduino.inWaiting()>0: 
                        answer=arduino.readline()
                        #answer=rl.readline()
                        print(answer)
                        arduino.flushInput() #remove data after reading
                        process_rfid(answer.decode("ascii"))
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")

