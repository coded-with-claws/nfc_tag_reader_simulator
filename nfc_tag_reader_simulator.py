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
ALARM_DENIED_THRESHOLD_ENABLED = True
ALARM_DENIED_THRESHOLD_VALUE = 5
#ALARM_DENIED_THRESHOLD_VALUE = 2 # DEBUG
ALARM_DENIED_THRESHOLD_DELAY = 60 * 5 # Unit: seconds. 5min.
#ALARM_DENIED_THRESHOLD_DELAY = 30 # DEBUG
### END CONFIGURATION ##############################

import logging
import os
import serial
import re
import time
import threading

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


logging.basicConfig(filename='nfc_tag_reader_simulator.log', encoding='utf-8', level=logging.DEBUG)

ALLOWED_TAGS = ["1179992064", "651317760", "2391729211"] # homer autocollants collés, homer autocollants non collés, robocop
POWEROFF_TAG = ["3055374848", "4007260474", "3601476352"] # pince coupante autocollant, puzzle bobble, ancienne carte poweroff autocollants non collés
COL_GREEN = "\x1b[38;5;2m"
COL_RED = "\x1b[38;5;1m"
COL_RESET = "\033[0m"

DENIED_COUNTER = 0

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
    os.system("sudo poweroff")
    exit()

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
        t_buzz = threading.Thread(target=masterkey_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = threading.Thread(target=screen_draw, args=("ENROLL TAG",))
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
        t_buzz = threading.Thread(target=masterkey_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = threading.Thread(target=screen_draw, args=(info_text,))
        t_screen.start()
    time.sleep(2)
    if BUZZER:
        t_buzz.join()
    if OLED_SCREEN:
        t_screen.join()
        screen_draw(None)

def validate(tag):
    if tag in POWEROFF_TAG:
        poweroff()
    if tag in ALLOWED_TAGS:
        handle_tag_granted()
    else:
        handle_tag_denied()

def handle_tag_granted():
    global DENIED_COUNTER
    logging.info(f"{COL_GREEN}ACCESS GRANTED!{COL_RESET}")
    DENIED_COUNTER = 0
    cancel_all_denied_threshold_timers()
    if TOUCHPHAT:
        access_granted_touchphat()
    if LEDs:
        t_led = threading.Thread(target=access_granted_leds)
        t_led.start()
    if BUZZER:
        t_buzz = threading.Thread(target=access_granted_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = threading.Thread(target=screen_draw, args=("GRANTED",))
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

def handle_tag_denied():
    global DENIED_COUNTER
    logging.info(f"{COL_RED}ACCESS DENIED!{COL_RESET}")
    DENIED_COUNTER += 1
    logging.info(f"{COL_RED}denied counter = {DENIED_COUNTER}{COL_RESET}")
    t = threading.Timer(ALARM_DENIED_THRESHOLD_DELAY, handle_alarm_denied_threshold_timer_end)
    t.start()
    if TOUCHPHAT:
        access_denied_touchphat()
    if LEDs:
        t_led = threading.Thread(target=access_denied_leds)
        t_led.start()
    if BUZZER:
        t_buzz = threading.Thread(target=access_denied_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = threading.Thread(target=screen_draw, args=("DENIED",))
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

def analyze_alarms():
    global DENIED_COUNTER
    if ALARM_DENIED_THRESHOLD_ENABLED:
        if DENIED_COUNTER >= ALARM_DENIED_THRESHOLD_VALUE:
            display_alarm_denied_threshold()
            DENIED_COUNTER = 0

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
    redled.blink(on_time=0.3, off_time=0.3, n=2, background=False)
    greenled.blink(on_time=0.3, off_time=0.3, n=2, background=False)

def access_granted_leds():
    greenled.blink(on_time=1.2, off_time=0, n=1, background=False)

def access_denied_leds():
    redled.blink(on_time=2.4, off_time=0, n=1, background=False)

def alarm_denied_threshold_leds():
    redled.blink(on_time=0.3, off_time=0.2, n=15, background=False)

### END LED Management -LEDs #################################

### BUZZER Management #################################
def buzz(pitch, duration):
    '''
    Cause the buzzer to produce a buzz according to a pitch in a note frequency number (Hz)
    for a duration in seconds.
    To produce a C4 note for half a second.
    >>> buzz(261.63, 0.5)
    Source: https://github.com/fongkahchun86/gpiozero_pwm_buzzer/blob/master/gpiozero_pwm_buzzer.py
    '''
    if pitch == 0:
        time.sleep(duration)
        return
    period = 1.0 / pitch #in physics, the period (sec/cyc) is the inverse of the frequency (cyc/sec)
    delay = period / 2 #calculate the time for half of the wave
    cycles = int(round(duration * pitch, 0)) #the number of waves to produce is the duration times the frequency
    for i in range(cycles):
        buzzer.on()
        time.sleep(delay)
        buzzer.off()
        time.sleep(delay)

def access_granted_buzzer():
    buzzer.blink(on_time=0.1, off_time=0.1, n=2, background=False)

def access_denied_buzzer():
    buzzer.blink(on_time=0.8, off_time=0.4, n=2, background=False)

def masterkey_buzzer():
    buzzer.blink(on_time=0.2, off_time=0, n=1, background=False)

def alarm_denied_threshold_buzzer():
    # https://en.wikipedia.org/wiki/Scientific_pitch_notation#Table_of_note_frequencies
    note_B4 = 493.88
    note_C5 = 523.25
    note_C4 = 261.63
    for i in range(3):
        #buzz(note_B4, 0.5)
        buzz(note_C5, 0.5)
        buzz(note_C4, 1)
        time.sleep(1)

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

### ALARMS Management #################################
def cancel_all_denied_threshold_timers():
    for t in threading.enumerate():
        if t.name != "MainThread":
            t.cancel()

def handle_alarm_denied_threshold_timer_end():
    global DENIED_COUNTER
    logging.info(f"{COL_GREEN}ALARM: one denied attempt expired (counter = {DENIED_COUNTER}){COL_RESET}")
    if DENIED_COUNTER > 0:
        DENIED_COUNTER -= 1
        logging.info(f"{COL_GREEN}ALARM: denied counter = {DENIED_COUNTER}{COL_RESET}")

def display_alarm_denied_threshold():
    logging.info(f"{COL_RED}ALARM: DENIED THRESHOLD REACHED!{COL_RESET}")
    if TOUCHPHAT:
        access_denied_touchphat()
    if LEDs:
        t_led = threading.Thread(target=alarm_denied_threshold_leds)
        t_led.start()
    if BUZZER:
        t_buzz = threading.Thread(target=alarm_denied_threshold_buzzer)
        t_buzz.start()
    if OLED_SCREEN:
        t_screen = threading.Thread(target=screen_draw, args=("ALARM",))
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

### END ALARMS Management  #################################

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
                        logging.info(f"arduino read: {answer}")
                        arduino.flushInput() #remove data after reading
                        process_rfid(answer.decode("ascii"))
                        analyze_alarms()
            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt has been caught.")
                cancel_all_denied_threshold_timers()
                if OLED_SCREEN:
                    screen_empty()

