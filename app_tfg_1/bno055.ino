// Librerías necesarias
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <SoftwareSerial.h>

// Configuración del sensor BNO055
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

// Configuración del sensor láser
SoftwareSerial mySerial(2, 3); // TX = 3, RX = 2
char buff[4] = {0x80, 0x06, 0x03, 0x77};
unsigned char data[11] = {0};

// Configuración del botón
const int botonPin = 7;

void setup() {
  Serial.begin(115200);
  mySerial.begin(9600);

  pinMode(botonPin, INPUT_PULLUP);  // Configurar el botón con resistencia interna

  if (!bno.begin()) {
    Serial.println("No se encontró el BNO055, verifica las conexiones.");
    while (1);
  }
  bno.setExtCrystalUse(true); 
}

void loop() {
  if (digitalRead(botonPin) == LOW) {  // Si el botón es presionado
    float distancia = medirDistancia();
    float azimut, pitch, roll;
    medirOrientacion(&azimut, &pitch, &roll);

    // Enviar solo los datos medidos al puerto serial.
    Serial.print(distancia, 3);
    Serial.print(",");
    Serial.print(azimut, 2);
    Serial.print(",");
    Serial.print(pitch, 2);
    Serial.print(",");
    Serial.println(roll, 2);

    delay(500);  // Pausa para evitar lecturas múltiples rápidamente
  }
}

float medirDistancia() {
  mySerial.print(buff);
  delay(50);

  if (mySerial.available() > 0) {
    for (int i = 0; i < 11; i++) {
      data[i] = mySerial.read();
    }

    // Verificar que los datos son correctos
    unsigned char Check = 0;
    for (int i = 0; i < 10; i++) {
      Check = Check + data[i];
    }
    Check = ~Check + 1;

    if (data[10] == Check) {
      // Depuración: Imprimir datos recibidos en hexadecimal
      Serial.print("Datos recibidos: ");
      for (int i = 0; i < 11; i++) {
        Serial.print(data[i], HEX);
        Serial.print(" ");
      }
      Serial.println();

      if (data[3] == 'E' && data[4] == 'R' && data[5] == 'R') {
        Serial.println("Error: Distancia fuera de rango");
        return -1.0;
      } else {
        // Verificar si el número recibido es negativo
        bool esNegativo = (data[3] == '-');

        float distance = (data[3 + esNegativo] - '0') * 100 +
                         (data[4 + esNegativo] - '0') * 10 +
                         (data[5 + esNegativo] - '0') * 1 +
                         (data[7 + esNegativo] - '0') * 0.1 +
                         (data[8 + esNegativo] - '0') * 0.01 +
                         (data[9 + esNegativo] - '0') * 0.001;

        return esNegativo ? -distance : distance;
      }
    } else {
      Serial.println("Error: Datos inválidos");
      return -1.0;
    }
  }
  return -1.0;
}

void medirOrientacion(float* azimut, float* pitch, float* roll) {
  sensors_event_t event;
  bno.getEvent(&event);
  
  *azimut = event.orientation.x;
  *pitch = event.orientation.y;
  *roll = event.orientation.z;
}
