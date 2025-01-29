#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lsusb to check device name
#dmesg | grep "tty" to find port name

### CONFIGURATION ##################################
TOUCHPHAT = False
LEDs = True
GPIO_REDLED = 17
GPIO_GREENLED = 27
BUZZER = True
GPIO_BUZZER = 22
OLED_SCREEN = True
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
SCREEN_OFFSET = 4
### END CONFIGURATION ##############################

import logging
import os
import serial
import re
import time
from threading import Thread

if TOUCHPHAT:
    import touchphat

if LEDs:
    from gpiozero import LED
    redled = LED(GPIO_REDLED)
    greenled = LED(GPIO_GREENLED)

if BUZZER:
    from gpiozero import Buzzer
    buzzer = Buzzer(GPIO_BUZZER)

if OLED_SCREEN:
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306
    oled = None


### LOG ############################################
logging.basicConfig(filename='nfc_tag_reader_simulator.log', encoding='utf-8', level=logging.DEBUG)

ALLOWED_TAGS = ["1179992064", "651317760", "2391729211"] # homer autocollants collés, homer autocollants non collés, robocop
# POWEROFF_TAG = "4007260474" # puzzle bobble
# POWEROFF_TAG = "3601476352" # ancienne carte poweroff autocollants non collés
POWEROFF_TAG = "3055374848"
COL_GREEN = "\x1b[38;5;2m"
COL_RED = "\x1b[38;5;1m"
COL_RESET = "\033[0m"

### END LOG ######################################

### BOOT / POWEROFF ###########################################
def startup():
    if TOUCHPHAT:
        led_enter_on_off_touchphat()
        led_back_blink_touchphat()
    if LEDs:
        startup_leds()
    if OLED_SCREEN:
        startup_screen()
        screen_draw(None)
    if BUZZER:
        access_granted_buzzer()

def poweroff():
    if TOUCHPHAT:
        led_enter_on_off_touchphat()
        led_back_blink_touchphat()
    if LEDs:
        startup_leds()
    if OLED_SCREEN:
        poweroff_screen()
    if BUZZER:
        access_granted_buzzer()

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
    match_process = re.match(string=reader_line, pattern=r"r (\d+)")
    match_write = re.match(string=reader_line, pattern=r"w (\d+)")
    match_masterkey = re.match(string=reader_line, pattern=r"m")
    if match_process:
        tag = match_process.group(1)
        #logging.info(f"Tag to process: {tag}")
        validate(tag)
    elif match_write:
        tag = match_write.group(1)
        #logging.info(f"Tag to allow: {tag}")
        allow_tag(tag)
    elif match_masterkey:
        masterkey_detected()

def masterkey_detected():
    logging.info(f"Master key detected")
    if BUZZER:
        t_buzz = Thread(target=masterkey_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = Thread(target=screen_draw, args=("ENROLL TAG",))
        t_screen.start()
    time.sleep(2)
    if BUZZER:
        t_buzz.join()
    if OLED_SCREEN:
        t_screen.join()
        screen_draw(None)

def allow_tag(tag):
    info_text = "ALREADY ADDED"
    if tag not in ALLOWED_TAGS:
        ALLOWED_TAGS.append(tag)
        info_text = "ADDED TAG"
        logging.info(f"New allowed tag list: {ALLOWED_TAGS}")
    if BUZZER:
        t_buzz = Thread(target=masterkey_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = Thread(target=screen_draw, args=(info_text,))
        t_screen.start()
    time.sleep(2)
    if BUZZER:
        t_buzz.join()
    if OLED_SCREEN:
        t_screen.join()
        screen_draw(None)

def validate(tag):
    if tag == POWEROFF_TAG:
        poweroff()
        os.system("sudo poweroff")
        exit()
    if tag in ALLOWED_TAGS:
        logging.info(f"{COL_GREEN}ACCESS GRANTED!{COL_RESET}")
        if TOUCHPHAT:
            access_granted_touchphat()
        if LEDs:
            t_led = Thread(target=access_granted_leds)
            t_led.start()
        if BUZZER:
            t_buzz = Thread(target=access_granted_buzzer)
            t_buzz.start()
        if OLED_SCREEN:
            t_screen = Thread(target=screen_draw, args=("GRANTED",))
            t_screen.start()
        if LEDs:
            t_led.join()
        if BUZZER:
            t_buzz.join()
        if OLED_SCREEN:
            t_screen.join()
            # wait some time to read the screen in case there was no LED / Buzzer management
            if not LEDs and not BUZZER:
                time.sleep(3)
            screen_draw(None)
    else:
        logging.info(f"{COL_RED}ACCESS DENIED!{COL_RESET}")
        if TOUCHPHAT:
            access_denied_touchphat()
        if LEDs:
            t_led = Thread(target=access_denied_leds)
            t_led.start()
        if BUZZER:
            t_buzz = Thread(target=access_denied_buzzer)
            t_buzz.start()
        if OLED_SCREEN:
            t_screen = Thread(target=screen_draw, args=("DENIED",))
            t_screen.start()
        if LEDs:
            t_led.join()
        if BUZZER:
            t_buzz.join()
        if OLED_SCREEN:
            t_screen.join()
            # wait some time to read the screen in case there was no LED / Buzzer management
            if not LEDs and not BUZZER:
                time.sleep(3)
            screen_draw(None)

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

### LED Management -LEDs #################################
def startup_leds():
    redled.blink(on_time=1, off_time=0.5, n=3)
    greenled.blink(on_time=1, off_time=0.5, n=3)


def access_granted_leds():
    greenled.blink(on_time=0.8, off_time=0.2, n=1)


def access_denied_leds():
    redled.blink(on_time=0.8, off_time=0.4, n=3)

### END LED Management -LEDs #################################

### BUZZER Management #################################
def access_granted_buzzer():
    buzzer.blink(on_time=0.1, off_time=0.1, n=2)


def access_denied_buzzer():
    buzzer.blink(on_time=0.8, off_time=0.4, n=3)

### END BUZZER Management  #################################

### SCREEN Management #################################
def startup_screen():
    global oled
    oled_reset = digitalio.DigitalInOut(board.D4)
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=0x3C, reset=oled_reset)
    screen_empty()

def poweroff_screen():
    screen_draw("POWEROFF")

def screen_empty():
    global oled

    oled.fill(0)
    oled.show()

def screen_offset(text):
    return " " * SCREEN_OFFSET + str(text)

def screen_draw(access):
    global oled

    if access:
        status_msg = access
    else:
        status_msg = "WAITING"
    status_msg = screen_offset(status_msg)

    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    font = ImageFont.truetype('/home/pi/nfc_tag_reader_simulator/resources/PixelOperator.ttf', 16)

    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.text((0, 0), screen_offset("ACCESS CONTROL"), font=font, fill=255)
    #draw.text((0, 16), "", font=font, fill=255)
    draw.text((0, 32), status_msg, font=font, fill=255)
    #draw.text((0, 48), "", font=font, fill=255)

    oled.image(image)
    oled.show()

### END SCREEN Management  #################################

### MAIN ###############################################
if __name__ == '__main__':

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
            startup()
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
                if OLED_SCREEN:
                    screen_empty()

