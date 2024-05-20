
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // Ancho de la pantalla OLED en píxeles
#define SCREEN_HEIGHT 64 // Altura de la pantalla OLED en píxeles

// Declaración para una pantalla SSD1306 conectada a I2C (pines SDA y SCL)
#define OLED_RESET -1 // Número de pin de reinicio (o -1 si se comparte el pin de reinicio de Arduino)
#define SCREEN_ADDRESS 0x3C // Dirección I2C de la pantalla OLED (0x3C o 0x3D)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
Serial.begin(9600);

// Inicializar la pantalla OLED con SSD1306_SWITCHCAPVCC
if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
Serial.println(F("Error al inicializar la pantalla OLED."));
while (true); // Bucle infinito si no se puede inicializar la pantalla
}

// Configurar la pantalla
display.clearDisplay(); // Limpiar la pantalla
display.setTextSize(1); // Escala normal de 1:1
display.setTextColor(SSD1306_WHITE); // Color blanco para el texto
display.cp437(true); // Habilitar conjunto de caracteres estándar

// Mostrar los cuatro mensajes simultáneamente en la pantalla
displayMensajes();
}

void loop() {
// En este caso, el loop está vacío ya que mostramos todos los mensajes en el setup()
}

// Función para mostrar los cuatro mensajes simultáneamente en la pantalla OLED
void displayMensajes() {
// Mostrar "Hola Mundo" en la primera línea (y=0)
display.setCursor(0, 0); // Colocar el cursor en la esquina superior izquierda
display.println("Hola Mundo");

// Actualizar la pantalla para mostrar todos los mensajes
display.display();
}
