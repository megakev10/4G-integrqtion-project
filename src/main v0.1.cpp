/*#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  Serial.println("Lancement de la plateforme");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("plateforme fonctionnelle");
  Serial.println("AT");
  delay(1500);
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    Serial.print("ESP32 received: ");
    Serial.println(command);
  }
}*/
