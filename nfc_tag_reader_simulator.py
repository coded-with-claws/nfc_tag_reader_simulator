#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

### CONFIGURATION ##################################
RELEASE_MODE = False
### END CONFIGURATION ##############################

import os
import serial
import re
import time

if RELEASE_MODE:
    import touchphat

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

### Serial Management ##############################
def find_serial_dev():
    dev = ["/dev/ttyAMA0", "/dev/ttyUSB0"]
    for d in dev:
        if os.path.exists(d):
            return d
    return None

### END Serial Management ##############################

### Tag Management #################################
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
        if RELEASE_MODE:
            access_granted()
    else:
        print(f"{COL_RED}ACCESS DENIED!{COL_RESET}")
        if RELEASE_MODE:
            access_denied()

### END Tag Management #################################

### LED Management #################################

def access_granted():
    led_enter_on_off()

def access_denied():
    led_back_blink()

def led_enter_on_off():
    touchphat.set_led('Enter', True)
    time.sleep(1)
    touchphat.set_led('Enter', False)

def led_back_blink():
    touchphat.set_led('Back', True)
    time.sleep(0.1)
    touchphat.set_led('Back', False)
    time.sleep(0.1)
    touchphat.set_led('Back', True)
    time.sleep(0.1)
    touchphat.set_led('Back', False)
    time.sleep(0.1)
    touchphat.set_led('Back', True)
    time.sleep(0.1)
    touchphat.set_led('Back', False)

### END LED Management #################################

### MAIN ###############################################
if __name__ == '__main__':
    
    tty_dev = find_serial_dev()
    if tty_dev is None:
        print("No serial device found")
        exit(-1)

    print('Running. Press CTRL-C to exit.')
    with serial.Serial(tty_dev, 9600, timeout=1) as arduino:
        print(f"Opening serial device {tty_dev}")
        #rl = ReadLine(arduino)
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            print(f"{arduino.port} connected!")
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

