#include <Arduino.h>

HardwareSerial& modemSerial = Serial;

bool sendATCommand(const char* command, unsigned long timeout = 2000) {

    // Clear old data
    while (modemSerial.available()) {
        modemSerial.read();
    }

    // Send command
    modemSerial.println(command);

    Serial.print("Command sent: ");
    Serial.println(command);

    String response = "";

    unsigned long startTime = millis();

    while (millis() - startTime < timeout) {

        if (modemSerial.available()) {

            String line = modemSerial.readStringUntil('\n');
            line.trim(); // enlever des vides autour de "line"

            if (line.length() == 0) { // filtrer les lines vides
                continue;
            }

            // Store the complete response
            response += line + "\n";

            Serial.print("Modem: ");
            Serial.println(line);

            // Final response
            if (line == "OK") {
                return true;
            }

            if (line == "ERROR") {
                return false;
            }
        }
    }

    Serial.println("Modem: TIMEOUT");

    return false;
}

void setup(){
    modemSerial.begin(115200);
    modemSerial.println("plateforme lancee");
}

void loop(){
    sendATCommand("AT");
    delay(1500);
    sendATCommand("AT+CPIN?");
    delay(1500);
    sendATCommand("AT+CSQ");
    delay(1500);
    sendATCommand("AT+CEREG?");
    delay(1500);
    sendATCommand("AT+COPS?");    
    delay(1500);
}