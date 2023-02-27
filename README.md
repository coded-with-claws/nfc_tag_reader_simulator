
# Pre-requisite

## Pi Zero

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
@reboot ~/nfc_tag_reader_simulator/venv/bin/python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py
```

## Without venv
```shell
@reboot python ~/nfc_tag_reader_simulator/nfc_tag_reader_simulator.py
```

