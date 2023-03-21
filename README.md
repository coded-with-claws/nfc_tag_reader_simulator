
# Pre-requisite

## Pi Zero

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

## Arduino

https://github.com/ElRojo/MiSTerRFID/blob/main/arduino/misterrfid.ino

# Crontab
```shell
crontab -e
```

## With venv
```shell
@reboot while true; do ~/nfc_tag_reader_simulator/venv/bin/python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py; sleep 10; done
```

## Without venv
```shell
@reboot while true; do python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py; sleep 10; done
```

## Touch pHat (optional)

Plugged on GPIO pins.

## LEDs (optional)

Plug LEDs:
- a red LED on GPIO17 (pin 11)
- a green LED on GPIO27 (pin 13).

## Buzzer (optional)

Plug the buzzer on GPIO22 (pin 15).

## OLED screen (optional)

Follow install instructions on https://github.com/mklements/OLED_Stats

Plug SSD1306:
- OLED VCC on 3V3 (pin 1 on Pi Zero)
- OLED SDA on SDA1 (pin 3)
- OLED SCL on SCL1 (pin 5)
- OLED GND on GND (pin 9)

