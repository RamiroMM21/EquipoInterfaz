#include <Arduino.h>

const int ledPin = 25; // Pin GPIO donde está conectado el LED

void setup() {
    pinMode(ledPin, OUTPUT); // Configurar el pin del LED como salida
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Hola, Raspberry Pi Pico W!");
}

void loop() {
    digitalWrite(ledPin, HIGH); // Encender el LED
    Serial.println("LED encendido");
    delay(1000); // Esperar 1 segundo
    digitalWrite(ledPin, LOW); // Apagar el LED
    Serial.println("LED apagado");
    delay(1000); // Esperar 1 segundo
}
