#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <SoftwareSerial.h>

// =========================
// CONFIGURACIÓN DE SENSORES
// =========================

// Sensor BNO055
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

// Sensor láser
// SoftwareSerial(RX, TX)
// Arduino pin 2 RX <- TX del sensor láser
// Arduino pin 3 TX -> RX del sensor láser
SoftwareSerial mySerial(2, 3);

byte buff[4] = {0x80, 0x06, 0x03, 0x77};
unsigned char data[11] = {0};

// Botón
const int botonPin = 7;

// Control de pulsación
bool botonAnterior = HIGH;

void setup() {
  Serial.begin(115200);
  mySerial.begin(9600);

  pinMode(botonPin, INPUT_PULLUP);

  if (!bno.begin()) {
    Serial.println("ERROR_BNO055");
    while (1);
  }

  delay(1000);
  bno.setExtCrystalUse(true);

  Serial.println("READY");
}

void loop() {
  bool botonActual = digitalRead(botonPin);

  // Detecta pulsación: HIGH -> LOW
  if (botonAnterior == HIGH && botonActual == LOW) {
    delay(50); // Antirrebote básico

    if (digitalRead(botonPin) == LOW) {
      float distancia = medirDistancia();

      if (distancia < 0) {
        Serial.println("ERROR_LASER");
      } else {
        float azimut, pitch, roll;
        medirOrientacion(&azimut, &pitch, &roll);

        // Formato limpio para Python:
        // distancia,azimut,pitch,roll
        Serial.print(distancia, 3);
        Serial.print(",");
        Serial.print(azimut, 2);
        Serial.print(",");
        Serial.print(pitch, 2);
        Serial.print(",");
        Serial.println(roll, 2);
      }

      // Esperar a que se suelte el botón
      while (digitalRead(botonPin) == LOW) {
        delay(10);
      }
    }
  }

  botonAnterior = botonActual;
  delay(20);
}

float medirDistancia() {
  // Limpiar buffer anterior
  while (mySerial.available()) {
    mySerial.read();
  }

  // Enviar comando binario al sensor láser
  mySerial.write(buff, 4);

  // Esperar respuesta con timeout
  unsigned long inicio = millis();

  while (mySerial.available() < 11 && millis() - inicio < 500) {
    delay(5);
  }

  if (mySerial.available() < 11) {
    return -1.0;
  }

  for (int i = 0; i < 11; i++) {
    data[i] = mySerial.read();
  }

  // Checksum
  unsigned char check = 0;

  for (int i = 0; i < 10; i++) {
    check += data[i];
  }

  check = ~check + 1;

  if (data[10] != check) {
    return -1.0;
  }

  // Fuera de rango
  if (data[3] == 'E' && data[4] == 'R' && data[5] == 'R') {
    return -1.0;
  }

  // Conversión a metros
  bool esNegativo = (data[3] == '-');

  int offset = esNegativo ? 1 : 0;

  float distance =
      (data[3 + offset] - '0') * 100 +
      (data[4 + offset] - '0') * 10 +
      (data[5 + offset] - '0') * 1 +
      (data[7 + offset] - '0') * 0.1 +
      (data[8 + offset] - '0') * 0.01 +
      (data[9 + offset] - '0') * 0.001;

  if (esNegativo) {
    distance = -distance;
  }

  return distance;
}

void medirOrientacion(float* azimut, float* pitch, float* roll) {
  sensors_event_t event;
  bno.getEvent(&event);

  // BNO055:
  // orientation.x = heading / azimut
  // orientation.y = roll
  // orientation.z = pitch
  *azimut = event.orientation.x;
  *roll = event.orientation.y;
  *pitch = event.orientation.z;
}