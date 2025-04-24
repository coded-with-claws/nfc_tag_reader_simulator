
# NFC Tag Reader Simulator

<img src="https://github.com/coded-with-claws/nfc_tag_reader_simulator/blob/main/Electronics/Fritzing/POC_tag_reader.gif" />

## Features
- grants or denies tags depending on UID
- can enroll dynamically a new tag (becoming granted)
- alarms after 3 fails in 5 minutes (configurable)

### Ideas of future features
- online verification (use wifi to call an HTTP API to get the decision for the UID read)
- host a Web GUI providing poweroff, adding/removing a tag

## Pre-requisite

### Pi Zero

Raspberry Pi OS Debian 11+.

As user `pi`:
```shell
sudo apt-get install python3 python3-venv
#sudo systemctl mask serial-getty@ttyAMA0.service   # it appears it was not needed
mkdir ~/nfc_tag_reader_simulator
cd ~/nfc_tag_reader_simulator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If not inside a venv:
```shell
sudo apt-get install python3-smbus
sudo pip install -r requirements.txt
```

Additional since Debian 12:
```shell
sudo apt install libopenjp2-7
```

### Arduino (Nano) + NFC module

#### MFRC522

Flash `nfc_module/nfc_module.ino` if you have an Arduino + MFRC522
(based on https://github.com/ElRojo/MiSTerRFID/blob/main/arduino/misterrfid.ino)

Change the value of `WRITE_TAG` if you want to have a master key to authorize additional tags.

Don't forget you can adjust the gain by editing the line:
```
    rfid.PCD_SetRegisterBitMask(rfid.RFCfgReg, (0x02<<4)); // RFID Gain
```
Note: for our RobotDyn MFRC522, we have set `0x02<<4` (otherwise, it had the tendency to read incorrect values sometimes).

How-to flash with arduino-cli from the raspberry pi (as user `pi`):
```
cd
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo ln -s ~/bin/arduino-cli /usr/local/bin/
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli core list
=> Check that "Arduino AVR" is listed
arduino-cli board list
=> Check that "/dev/ttyUSB0" is listed
arduino-cli lib install "Easy MFRC522"
arduino-cli compile -b arduino:avr:nano nfc_module/
arduino-cli upload -b arduino:avr:nano --port /dev/ttyUSB0 nfc_module/
=> Check that it displays "New upload port: /dev/ttyUSB0 (serial)"
```

#### PN532

Flash `nfc_module_pn532/nfc_module_pn532.ino` if you have an Arduino + PN532.
Note: the PN532 libraries used were committed into this project because they included messages printed on serial port, which would break our code reading the serial.

## Crontab
```shell
crontab -e
```

### With venv
```shell
@reboot while true; do ~/nfc_tag_reader_simulator/venv/bin/python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py; sleep 10; done
```

### Without venv
```shell
@reboot while true; do python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py; sleep 10; done
```

## Modules

### Touch pHat (optional)

Plugged on GPIO pins.

### LEDs (optional)

Plug LEDs:
- a red LED on GPIO17 (pin 11)
- a green LED on GPIO27 (pin 13).

### Buzzer (optional)

Plug the buzzer on GPIO22 (pin 15).

### OLED screen (optional)

Follow install instructions on https://github.com/mklements/OLED_Stats

Plug SSD1306:
- OLED VCC on 3V3 (pin 1 on Pi Zero)
- OLED SDA on SDA1 (pin 3)
- OLED SCL on SCL1 (pin 5)
- OLED GND on GND (pin 9)

## POC result

<img src="https://github.com/coded-with-claws/nfc_tag_reader_simulator/blob/main/Electronics/Fritzing/2.Tag_Reader_POC.jpg"/>

