#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

### CONFIGURATION ##################################
TOUCHPHAT = True
### END CONFIGURATION ##############################

import logging
import os
import serial
import re
import time

if TOUCHPHAT:
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

logging.basicConfig(filename='nfc_tag_reader_simulator.log', encoding='utf-8', level=logging.DEBUG)

ALLOWED_TAGS = ["2391729211"]
COL_GREEN = "\x1b[38;5;2m"
COL_RED = "\x1b[38;5;1m"
COL_RESET = "\033[0m"

### BOOT ###########################################
def startup():
    led_enter_on_off_touchphat()
    led_back_blink_touchphat()

### END BOOT ######################################

### Serial Management ##############################
def find_serial_dev():
    #dev = ["/dev/ttyAMA0", "/dev/ttyUSB0"]
    dev = ["/dev/ttyUSB0"]
    for d in dev:
        if os.path.exists(d):
            return d
    return None

### END Serial Management ##############################

### Tag Management #################################
def process_rfid(reader_line):
    #logging.info(f"reader_line={reader_line}")
    match_process = re.match(string=reader_line, pattern=r"\. rfid_process\.sh (\d+)")
    match_write = re.match(string=reader_line, pattern=r"\. rfid_write\.sh (\d+)")
    if match_process:
        tag = match_process.group(1)
        #logging.info(f"Tag to process: {tag}")
        validate(tag)
    elif match_write:
        tag = match_write.group(1)
        #logging.info(f"Tag to allow: {tag}")
        allow_tag(tag)

def allow_tag(tag):
    ALLOWED_TAGS.append(tag)
    logging.info(f"New allowed tag list: {ALLOWED_TAGS}")

def validate(tag):
    if tag in ALLOWED_TAGS:
        logging.info(f"{COL_GREEN}ACCESS GRANTED!{COL_RESET}")
        if TOUCHPHAT:
            access_granted_touchphat()
    else:
        logging.info(f"{COL_RED}ACCESS DENIED!{COL_RESET}")
        if TOUCHPHAT:
            access_denied_touchphat()

### END Tag Management #################################

### LED Management - Touch pHat #################################

def access_granted_touchphat():
    led_enter_on_off_touchphat()

def access_denied_touchphat():
    led_back_blink_touchphat()

def led_enter_on_off_touchphat():
    touchphat.set_led('Enter', True)
    time.sleep(1)
    touchphat.set_led('Enter', False)

def led_back_blink_touchphat():
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

### END LED Management - Touch pHat #################################

### MAIN ###############################################
if __name__ == '__main__':
    
    startup()
    tty_dev = find_serial_dev()
    if tty_dev is None:
        logging.info("No serial device found")
        exit(-1)

    os.system(f"sudo chmod 666 {tty_dev}")
    logging.info('Running. Press CTRL-C to exit.')
    with serial.Serial(tty_dev, 9600, timeout=1) as arduino:
        logging.info(f"Opening serial device {tty_dev}")
        #rl = ReadLine(arduino)
        time.sleep(0.1) #wait for serial to open
        if arduino.isOpen():
            logging.info(f"{arduino.port} connected!")
            try:
                while True:
                    #cmd=input("Enter command : ")
                    #arduino.write(cmd.encode())
                    #time.sleep(0.1) #wait for arduino to answer
                    while arduino.inWaiting()==0: pass
                    if  arduino.inWaiting()>0: 
                        answer=arduino.readline()
                        #answer=rl.readline()
                        logging.info(answer)
                        arduino.flushInput() #remove data after reading
                        process_rfid(answer.decode("ascii"))
            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt has been caught.")

