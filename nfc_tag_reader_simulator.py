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

if BUZZER:
    from gpiozero import Buzzer

if OLED_SCREEN:
    import board
    import digitalio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306

    oled = None

### LOG ############################################
logging.basicConfig(filename='nfc_tag_reader_simulator.log', encoding='utf-8', level=logging.DEBUG)

ALLOWED_TAGS = ["2391729211"]  # robocop
POWEROFF_TAG = "4007260474"  # puzzle bobble

TAG_1 = "2391729211"  # robocop
TAG_2 = "1773311577"  # blank card
TAG_3 = "3457133370"  # bomberman2
TAG_4 = TAG_2  # blank card
TAG_5 = TAG_1  # robocop
TAG_List = [TAG_1, TAG_2, TAG_3, TAG_4, TAG_5]
TAG_SUPERVISOR = TAG_3  # bomberman2

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
    match_process = re.match(string=reader_line, pattern=r"\. rfid_process\.sh (\d+)")
    match_write = re.match(string=reader_line, pattern=r"\. rfid_write\.sh (\d+)")
    if match_process:
        tag = match_process.group(1)
        # logging.info(f"Tag to process: {tag}")
        validate(tag)
    elif match_write:
        tag = match_write.group(1)
        # logging.info(f"Tag to allow: {tag}")
        allow_tag(tag)


def allow_tag(tag):
    ALLOWED_TAGS.append(tag)
    logging.info(f"New allowed tag list: {ALLOWED_TAGS}")


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


def get_tag_id(reader_line, n_l, status_seq):
    # logging.info(f"reader_line={reader_line}")
    match_process = re.match(string=reader_line, pattern=r"\. rfid_process\.sh (\d+)")
    match_write = re.match(string=reader_line, pattern=r"\. rfid_write\.sh (\d+)")
    if match_process:
        tag = match_process.group(1)
        if tag == POWEROFF_TAG:
            poweroff()
            os.system("sudo poweroff")
            exit()
        if LEDs:
            t_led = Thread(target=access_granted_leds)
            t_led.start()
        if BUZZER:
            t_buzz = Thread(target=access_granted_buzzer)
            t_buzz.start()
        if OLED_SCREEN:
            if tag == TAG_SUPERVISOR and status_seq:
                t_screen = Thread(target=screen_draw, args=("Congratulations employee",))
            else:
                if n_l == 1:
                    t_screen = Thread(target=screen_draw, args=("[X----]",))
                elif n_l == 2:
                    t_screen = Thread(target=screen_draw, args=("[XX---]",))
                elif n_l == 3:
                    t_screen = Thread(target=screen_draw, args=("[XXX--]",))
                elif n_l == 4:
                    t_screen = Thread(target=screen_draw, args=("[XXXX-]",))
                elif n_l == 5:
                    t_screen = Thread(target=screen_draw, args=("[XXXXX]",))
                else:
                    t_screen = Thread(target=screen_draw, args=("[-----]",))
            t_screen.start()
        if LEDs:
            t_led.join()
        if BUZZER:
            t_buzz.join()
        if OLED_SCREEN:
            t_screen.join()

        return tag
    elif match_write:
        tag = match_write.group(1)
        allow_tag(tag)


def try_sequence(tag_list):
    if tag_list == TAG_List:
        logging.info(f"{COL_GREEN}ACCESS GRANTED! Correct Sequence{COL_RESET}")
        if TOUCHPHAT:
            access_granted_touchphat()
        if LEDs:
            t_led = Thread(target=sequence_success_leds)
            t_led.start()
        if BUZZER:
            t_buzz = Thread(target=access_granted_buzzer)
            t_buzz.start()
        if OLED_SCREEN:
            t_screen = Thread(target=screen_draw, args=("Correct sequence",))
            t_screen.start()
        if LEDs:
            t_led.join()
        if BUZZER:
            t_buzz.join()
        if OLED_SCREEN:
            t_screen.join()
            # wait some time to read the screen in case there was no LED / Buzzer management
            if not LEDs and not BUZZER:
                time.sleep(5)
                ## TODO: change the success message to be permanent until reset ?3
        return True
    else:
        logging.info(f"{COL_RED}ACCESS DENIED! Wrong sequence{COL_RESET}")
        if TOUCHPHAT:
            access_denied_touchphat()
        if LEDs:
            t_led = Thread(target=access_denied_leds)
            t_led.start()
        if BUZZER:
            t_buzz = Thread(target=access_denied_buzzer)
            t_buzz.start()
        if OLED_SCREEN:
            t_screen = Thread(target=screen_draw, args=("Invalid Sequence",))
            t_screen.start()
        if LEDs:
            t_led.join()
        if BUZZER:
            t_buzz.join()
        if OLED_SCREEN:
            t_screen.join()
            # wait some time to read the screen in case there was no LED / Buzzer management
            if not LEDs and not BUZZER:
                time.sleep(5)
            screen_draw(None)
    return False


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
    led_enter_on_off('red', 1)
    led_enter_on_off('green', 1)
    led_enter_on_off('both', 1)


def led_enter_on_off(leds, duration):
    redled = LED(GPIO_REDLED)
    greenled = LED(GPIO_GREENLED)
    if leds in ('red', 'both'):
        redled.on()
    if leds in ('green', 'both'):
        greenled.on()
    time.sleep(duration)
    if leds in ('red', 'both'):
        redled.off()
    if leds in ('green', 'both'):
        greenled.off()


def access_granted_leds():
    led_enter_on_off('green', 1)


def access_denied_leds():
    #    for i in range(10):
    #        led_enter_on_off('red', 0.2)
    #        time.sleep(0.2)
    for i in range(3):
        led_enter_on_off('red', 0.8)
        time.sleep(0.4)


def sequence_success_leds():
    for i in range(5):
        # led_enter_on_off('red', 1)
        led_enter_on_off('green', 1)
        led_enter_on_off('both', 1)


### END LED Management -LEDs #################################

### BUZZER Management #################################
def buzzer_on_off(duration):
    buzzer = Buzzer(GPIO_BUZZER)
    buzzer.on()
    time.sleep(duration)
    buzzer.off()


def access_granted_buzzer():
    buzzer_on_off(0.1)
    time.sleep(0.1)
    buzzer_on_off(0.1)


def access_denied_buzzer():
    for i in range(3):
        buzzer_on_off(0.8)
        time.sleep(0.4)


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
    # draw.text((0, 16), "", font=font, fill=255)
    draw.text((0, 32), status_msg, font=font, fill=255)
    # draw.text((0, 48), "", font=font, fill=255)

    oled.image(image)
    oled.show()


###  END SCREEN Management  #################################

###  MAIN ###############################################
if __name__ == '__main__':

    startup()
    tty_dev = find_serial_dev()
    if tty_dev is None:
        logging.info("No serial device found")
        exit(-1)
    input_sequence = []
    n_loop = 1
    status_sequence = False
    os.system(f"sudo chmod 666 {tty_dev}")
    logging.info('Running. Press CTRL-C to exit.')
    with serial.Serial(tty_dev, 9600, timeout=1) as arduino:
        logging.info(f"Opening serial device {tty_dev}")
        # rl = ReadLine(arduino)
        time.sleep(0.1)  # wait for serial to open
        if arduino.isOpen():
            logging.info(f"{arduino.port} connected!")
            try:
                while True:
                    # cmd=input("Enter command : ")
                    # arduino.write(cmd.encode())
                    # time.sleep(0.1) #wait for arduino to answer
                    while arduino.inWaiting() == 0: pass
                    if arduino.inWaiting() > 0:
                        answer = arduino.readline()
                        # answer=rl.readline()
                        logging.info(answer)
                        arduino.flushInput()  # remove data after reading
                        # process_rfid(answer.decode("ascii"))
                        tag_id = get_tag_id(answer.decode("ascii"), n_loop, status_sequence)
                        input_sequence.append(tag_id)
                        if n_loop == 5:
                            status_sequence = try_sequence(input_sequence)
                            input_sequence = []
                            n_loop = 1
                        else:
                            n_loop += 1
            except KeyboardInterrupt:
                logging.info("KeyboardInterrupt has been caught.")
                if OLED_SCREEN:
                    screen_empty()
