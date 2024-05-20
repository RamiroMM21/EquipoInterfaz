void setup() {
  // Iniciar Serial1 en UART0 (TX on GPIO 0, RX on GPIO 1)
  Serial1.begin(9600); 
  // Iniciar Serial para el monitor serial
  Serial.begin(9600);
}

void loop() {
  // Enviar datos por Bluetooth
  Serial1.println("Hello from Pico via Bluetooth");
  // Esperar 2 segundos
  delay(2000);
}
