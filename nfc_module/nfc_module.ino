// Codebase from https://github.com/ElRojo/MiSTerRFID/blob/main/arduino/misterrfid.ino
#include <MFRC522.h>
#include <SPI.h>

#define WRITE_TAG 1234567890
#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

int codeRead = 0;
uint32_t cardid = 0;
uint32_t lastCardRead = 0;
int waitForIt = 0;
String uidString;
void setup() {
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
  rfid.PCD_SetRegisterBitMask(rfid.RFCfgReg, (0x02<<4)); // RFID Gain
  pinMode(8,OUTPUT);
  pinMode(A0,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (rfid.PICC_IsNewCardPresent())
  {
    readRFID();
  }
  delay(50); // delay for CPU charge
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
  if (! rfid.PICC_ReadCardSerial()) {
    // New card was not read
    return;
  }
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
      piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
      piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    //tag is a MIFARE Classic."
    return;
  }

  cardid = 0;
  for (byte i = 0; i < rfid.uid.size; i++) {
    cardid |= rfid.uid.uidByte[i];
    if (i != rfid.uid.size - 1) {
      cardid <<= 8;
    }
  }

  if (lastCardRead == wCard && cardid != wCard) {
    cardLogic("w ", cardid);
  }
  else {
    cardLogic("r ", cardid);
  }


  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  //rfid.PCD_StopCrypto1();
}
