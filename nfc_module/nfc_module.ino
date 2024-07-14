// Codebase from https://github.com/ElRojo/MiSTerRFID/blob/main/arduino/misterrfid.ino
#include <MFRC522.h>
#include <SPI.h>

//#define WRITE_TAG 1982808832 //ancienne carte autocollants non colles
#define WRITE_TAG 3054518528
#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

MFRC522::MIFARE_Key key;

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
  Serial.println("loaded"); 
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  if (  rfid.PICC_IsNewCardPresent())
  {
    readRFID();
  }
  delay(100);
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
  delay(2000); // delay for reading next tag
  digitalWrite(LED_BUILTIN, LOW);
}

void readRFID()
{
  const uint32_t wCard = WRITE_TAG; // Writing Card
  rfid.PICC_ReadCardSerial();
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
      piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
      piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    //tag is a MIFARE Classic."
    return;
  }

  cardid = rfid.uid.uidByte[0];
  cardid <<= 8;
  cardid |= rfid.uid.uidByte[1];
  cardid <<= 8;
  cardid |= rfid.uid.uidByte[2];
  cardid <<= 8;
  cardid |= rfid.uid.uidByte[3];

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
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}
