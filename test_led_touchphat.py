#!/usr/bin/env python

import time
import touchphat

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


access_granted()
time.sleep(1)
access_denied()

