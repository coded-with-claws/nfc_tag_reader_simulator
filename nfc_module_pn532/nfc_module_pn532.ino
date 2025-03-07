// Uses locally library from https://github.com/elechouse/PN532/tree/PN532_HSU : PN532 + PN532_I2C + NDEF
// Code inspired from https://how2electronics.com/interfacing-pn532-nfc-rfid-module-with-arduino/

#include <Wire.h>
#include "src/PN532/PN532.h"
#include "src/PN532_I2C/PN532_I2C.h"
#include "src/NDEF/NfcAdapter.h"

//#define WRITE_TAG 1982808832 //ancienne carte autocollants non colles
//#define WRITE_TAG 3054518528 // carte autocollant cles
#define WRITE_TAG 806781984 // badge rond bleu

PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);

int codeRead = 0;
uint32_t cardid = 0;
uint32_t lastCardRead = 0;
int waitForIt = 0;

void setup() {
  Serial.begin(9600);
  nfc.begin();
  //pinMode(8,OUTPUT);
  //pinMode(A0,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (nfc.tagPresent())
  {
    readRFID();
  }
  delay(50);
}

void cardLogic(String proc, uint32_t cardNum) {
  digitalWrite(LED_BUILTIN, HIGH);
  if (cardNum != WRITE_TAG) {
    Serial.print(proc);
    Serial.println(cardNum);
  } else {
    Serial.println(proc);
  }
  lastCardRead = cardNum;
  //delay(2000); // delay for reading next tag
  delay(1000); // delay for reading next tag
  digitalWrite(LED_BUILTIN, LOW);
}

void readRFID()
{
  const uint32_t wCard = WRITE_TAG; // Writing Card
  NfcTag tag;
  unsigned int tagLen;
  byte uidBytes[16];
  
  tag = nfc.read();
  if (tag.getUidLength() == 0) {
    // New card was not read
    return;
  }

  cardid = 0;
  tagLen = tag.getUidLength();
  tag.getUid(uidBytes, tagLen); // copy uid into uidBytes
  for (byte i = 0; i < tagLen; i++) {
    cardid |= uidBytes[i];
    if (i != tagLen - 1) {
      cardid <<= 8;
    }
  }

  if (lastCardRead != wCard && cardid == wCard) {
    cardLogic("m", cardid);
  }
  else if (lastCardRead == wCard && cardid != wCard) {
    cardLogic("w ", cardid);
  }
  else {
    cardLogic("r ", cardid);
  }


  // Halt PICC
  //rfid.PICC_HaltA();

  // Stop encryption on PCD
  //rfid.PCD_StopCrypto1();
}
